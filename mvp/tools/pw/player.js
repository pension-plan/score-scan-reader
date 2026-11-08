// Score playback in the page (ui/player.js) on the Maple Leaf Rag sample and
// the St. Anselm hymn (SATB -> four choir parts), at 1280 and 400 px, light
// and dark: Play starts a running AudioContext, the OSMD cursor and the scan's
// sounding-head rings advance, Space pauses, a click on a note head and on a
// preview measure plays from there, an OfflineAudioContext render of the first
// seconds is not silent, and the .mid export is a valid file. Screenshots go to
// <outdir>.   node tools/pw/player.js <outdir>
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, '../../work/player'));
fs.mkdirSync(OUT, { recursive: true });
const PB = require(path.join(__dirname, '../../src/playback.js'));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.pdf': 'application/pdf', '.gz': 'application/gzip', '.wasm': 'application/wasm' };
const only = (process.env.PW_ONLY || '').split(',').filter(Boolean);
const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(path.join(DIST, 'index.html'), 'utf8') + '</body></html>'); }
  const f = path.join(DIST, p);
  if (!f.startsWith(DIST) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0, async () => {
  const port = srv.address().port;
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch({ ...(fs.existsSync(cached) ? { executablePath: cached } : {}), args: ['--autoplay-policy=no-user-gesture-required'] });
  const out = { errors: [], failures: [], runs: {} };
  const fail = (m) => { out.failures.push(m); console.log('FAIL', m); };
  for (const scheme of ['light', 'dark']) for (const width of [1280, 400]) {
    const tag = width + (scheme === 'dark' ? '-dark' : '');
    if (only.length && !only.includes(tag)) continue;
    const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme, acceptDownloads: true });
    page.on('console', (m) => { if (m.type() === 'error') out.errors.push(tag + ': ' + m.text()); });
    page.on('pageerror', (e) => out.errors.push(tag + ' pageerror: ' + e.message));
    try {
      await page.goto(`http://localhost:${port}/`);
      for (const sample of ['rag', 'hymn']) {
        const key = `${tag}-${sample}`;
        if (sample === 'hymn') {
          await page.evaluate(() => { window.__omrResult = null; });
          // the hymn sample: a button in older layouts, an option of the examples picker now
          const sel = await page.evaluate(() => (document.getElementById('sampleHymn') ? '#sampleHymn' : '#sampleAll'));
          await page.waitForFunction((q) => !document.querySelector(q).disabled, sel, { timeout: 120000 });
          await page.evaluate(() => window.scrollTo(0, 0));
          if (sel === '#sampleHymn') await page.click(sel, { timeout: 10000 });
          else await page.selectOption(sel, 'hymn', { timeout: 10000 });
        }
        await page.waitForFunction(() => window.__omrResult && window.__player && window.__player.model, null, { timeout: 300000 });
        await page.waitForTimeout(400);
        const info = await page.evaluate(() => {
          const s = window.__player;
          return { parts: s.parts.map((p) => [p.name, p.program]), notes: s.all.length, dur: s.model.duration, bpm: s.model.startBpm, heads: s.lineHeads.size,
            measures: s.model.measures.length, mixer: document.querySelectorAll('#pbParts .pb-part').length, hscroll: document.documentElement.scrollWidth > window.innerWidth };
        });
        const run = { info };
        out.runs[key] = run;
        if (!info.notes) fail(`${key}: nothing to play`);
        if (info.mixer !== info.parts.length) fail(`${key}: mixer rows ${info.mixer} != parts ${info.parts.length}`);
        if (sample === 'hymn' && !(info.parts.length === 4 && info.parts.every((p) => p[1] === 52))) fail(`${key}: expected four Choir Aahs parts, got ${JSON.stringify(info.parts)}`);
        if (sample === 'rag' && !(info.parts.length === 1 && info.parts[0][1] === 0)) fail(`${key}: expected one piano part, got ${JSON.stringify(info.parts)}`);
        if (info.hscroll) fail(`${key}: horizontal page scroll`);
        if (!info.heads) fail(`${key}: no note heads linked to MusicXML lines`);
        // play: the context runs, the position, cursor and head rings move
        await page.locator('#pb').scrollIntoViewIfNeeded();
        await page.click('#pbPlay');
        const samples = [];
        for (let k = 0; k < 14; k++) {
          await page.waitForTimeout(250);
          samples.push(await page.evaluate(() => { const s = window.__player; const hl = document.querySelector('#pages svg.pb-hl'); return { state: s.ctx && s.ctx.state, playing: s.playing, pos: s.pos, stop: s.stopIdx, hl: hl ? +hl.dataset.count || 0 : -1, key: s.hlKey, sets: [...s.loaded.keys()] }; }));
        }
        run.play = samples;
        const last = samples[samples.length - 1];
        if (last.state !== 'running') fail(`${key}: AudioContext is ${last.state}`);
        if (!last.playing || !(last.pos > 0.8)) fail(`${key}: position did not advance (${last.pos})`);
        const stops = new Set(samples.map((x) => x.stop));
        if (stops.size < 3) fail(`${key}: OSMD cursor did not advance (${[...stops]})`);
        const keys = new Set(samples.filter((x) => x.hl > 0).map((x) => x.key));
        if (keys.size < 2) fail(`${key}: scan highlight did not advance (${keys.size} states)`);
        if (!last.sets.length) fail(`${key}: no sample set loaded`);
        await page.screenshot({ path: path.join(OUT, `${key}-playing.png`) });
        const sheet = await page.$('#previewPanel');
        if (sheet) await sheet.screenshot({ path: path.join(OUT, `${key}-preview.png`) });
        const plate = await page.$('#pages');
        if (plate) await plate.screenshot({ path: path.join(OUT, `${key}-scan.png`) });
        // Space pauses (focus on the page body)
        await page.evaluate(() => document.activeElement && document.activeElement.blur());
        await page.keyboard.press('Space');
        await page.waitForTimeout(150);
        const paused = await page.evaluate(() => !window.__player.playing);
        if (!paused) fail(`${key}: Space did not pause`);
        run.spacePaused = paused;
        // a click on a note head on the scan plays from that note
        const target = await page.evaluate(() => {
          const s = window.__player, b = s.book, pg = b.pages[b.sel], notes = b.headNotes.get(b.sel) || [];
          const ks = pg.view.heads.map((h, k) => k).filter((k) => notes[k] && notes[k][7] >= 0);
          const k = ks[Math.floor(ks.length * 0.6)];
          const h = pg.view.heads[k];
          const img = document.querySelector('#pages .pageframe img');
          img.scrollIntoView({ block: 'center' });
          const r = img.getBoundingClientRect();
          const n = s.all.find((x) => x.lines.includes(notes[k][7]));
          return { x: r.left + (h[0] / pg.view.width) * r.width, y: r.top + (h[1] / pg.view.height) * r.height, t: n ? n.t : null };
        });
        await page.mouse.click(target.x, target.y);
        await page.waitForTimeout(600);
        const fromHead = await page.evaluate(() => ({ playing: window.__player.playing, pos: window.__player.pos }));
        run.headClick = { target, fromHead };
        if (!fromHead.playing || target.t == null || Math.abs(fromHead.pos - target.t) > 2) fail(`${key}: head click did not play from the note (${JSON.stringify({ target, fromHead })})`);
        await page.screenshot({ path: path.join(OUT, `${key}-from-head.png`) });
        await page.click('#pbStop');
        // a click on the third measure of the preview
        const m3 = await page.evaluate(() => {
          const s = window.__player, o = s.osmd, gm = o.GraphicSheet.MeasureList[2] && o.GraphicSheet.MeasureList[2][0];
          const svg = document.querySelector('#osmd svg');
          if (!gm || !svg) return null;
          const ps = gm.PositionAndShape, ap = ps.AbsolutePosition, z = o.zoom || 1;
          const at = () => {
            const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
            const sx = vb && vb.width ? r.width / vb.width : 1, sy = vb && vb.height ? r.height / vb.height : 1;
            return { x: r.left + (ap.x + (ps.BorderLeft + ps.BorderRight) / 2) * 10 * z * sx, y: r.top + (ap.y + 2) * 10 * z * sy };
          };
          window.scrollBy(0, at().y - window.innerHeight / 2);
          return { ...at(), t: s.model.measures.find((m) => m.src === 2).t0 };
        });
        if (m3) {
          await page.mouse.click(m3.x, m3.y);
          await page.waitForTimeout(500);
          const fromBar = await page.evaluate(() => ({ playing: window.__player.playing, pos: window.__player.pos }));
          run.barClick = { m3, fromBar };
          if (!fromBar.playing || Math.abs(fromBar.pos - m3.t) > 1.5) fail(`${key}: preview measure click did not play from bar 3 (${JSON.stringify(run.barClick)})`);
          await page.click('#pbStop');
        } else fail(`${key}: no third measure in the preview`);
        // offline render of the first 4 seconds
        const off = await page.evaluate(() => window.ScorePlayer.renderOffline(4));
        run.offline = off;
        if (!(off.rms > 0.003)) fail(`${key}: offline render is silent (${JSON.stringify(off)})`);
        // tempo control and mixer: 150 %, mute the first part
        await page.$eval('#pbTempo', (el) => { el.value = '150'; el.dispatchEvent(new Event('input', { bubbles: true })); });
        const tempoTxt = await page.textContent('#pbTempoOut');
        if (!/150%/.test(tempoTxt)) fail(`${key}: tempo label ${tempoTxt}`);
        await page.$eval('#pbTempo', (el) => { el.value = '100'; el.dispatchEvent(new Event('input', { bubbles: true })); });
        await page.click('#pbMix summary');
        await page.click('#pbParts button[data-act="mute"]');
        const pressed = await page.getAttribute('#pbParts button[data-act="mute"]', 'aria-pressed');
        if (pressed !== 'true') fail(`${key}: mute aria-pressed ${pressed}`);
        await page.click('#pbParts button[data-act="mute"]');
        await (await page.$('#pb')).screenshot({ path: path.join(OUT, `${key}-transport.png`) });
        await page.click('#pbMix summary');
        // .mid export (not framed here, so a real download)
        const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 10000 }), page.click('#pbMidi')]);
        const file = path.join(OUT, `${key}.mid`);
        await dl.saveAs(file);
        const smf = PB.readSMF(fs.readFileSync(file));
        const ons = smf.tracks.flat().filter((e) => e.type === 'on').length;
        run.midi = { name: dl.suggestedFilename(), tracks: smf.tracks.length, ons, programs: smf.tracks.flat().filter((e) => e.type === 'program').map((e) => e.a) };
        if (smf.tracks.length !== info.parts.length + 1 || ons !== info.notes) fail(`${key}: MIDI file ${JSON.stringify(run.midi)} vs ${info.notes} notes`);
        console.log(key, JSON.stringify({ parts: info.parts, notes: info.notes, bpm: info.bpm, dur: +info.dur.toFixed(1), last, offline: off, midi: run.midi }));
      }
    } catch (e) { fail(`${tag}: ${e.message.split('\n')[0]}`); }
    await page.close();
  }
  await browser.close();
  srv.close();
  fs.writeFileSync(path.join(OUT, 'player-report.json'), JSON.stringify(out, null, 1));
  console.log(`errors: ${out.errors.length}${out.errors.length ? '\n  ' + out.errors.slice(0, 10).join('\n  ') : ''}`);
  console.log(`failures: ${out.failures.length}`);
  process.exit(out.failures.length || out.errors.length ? 1 : 0);
});
