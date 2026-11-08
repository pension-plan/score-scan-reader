// Browser check of unrecognised marks on the default sample at 1280 px (mouse,
// keyboard) and 400 px (touch), light and dark: the "Unrecognised only"
// default and the one-time migration of an older layer choice, highlight size,
// N / P navigation with zoom, the "what is this mark?" popover (keyboard and
// touch tap), saving a label (MusicXML corrected, count updated), persistence
// over a reload, Escape, repair notes and labelled examples on the clipboard.
//   node tools/pw/ident-shots.js <outdir>
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, '../../work/ident'));
fs.mkdirSync(OUT, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.pdf': 'application/pdf', '.gz': 'application/gzip', '.wasm': 'application/wasm', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(path.join(DIST, 'index.html'), 'utf8') + '</body></html>'); }
  const f = path.join(DIST, p);
  if (!f.startsWith(DIST) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0, async () => {
  const url = `http://localhost:${srv.address().port}/`;
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const out = { errors: [], failures: [], runs: {} };
  const fail = (t) => out.failures.push(t);
  for (const scheme of ['light', 'dark']) for (const width of [1280, 400]) {
    const tag = width + (scheme === 'dark' ? '-dark' : ''), touch = width === 400;
    const ctx = await browser.newContext({ viewport: { width, height: 800 }, colorScheme: scheme, hasTouch: touch, isMobile: touch, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error') out.errors.push(tag + ': ' + m.text()); });
    page.on('pageerror', e => out.errors.push(tag + ' pageerror: ' + e.message));
    const r = out.runs[tag] = {};
    const ready = async () => { await page.waitForFunction(() => window.__omrResult, null, { timeout: 240000 }); await page.waitForTimeout(400); };
    try {
      await page.goto(url);
      // a returning visitor from before presets, with a custom layer choice
      await page.evaluate(() => { Object.keys(localStorage).filter(k => /^ssr\.(view|ident|repair|zoom)/.test(k)).forEach(k => localStorage.removeItem(k)); localStorage.setItem('ssr.layers', '["rests"]'); });
      await page.reload(); await ready();
      r.mode = await page.evaluate(() => document.querySelector('.preset[aria-pressed="true"]').dataset.mode);
      if (r.mode !== 'unknown') fail(tag + ': default view is ' + r.mode);
      r.onlyUnknown = await page.evaluate(() => ['notes', 'rests', 'bars', 'labels'].every(k => document.getElementById('pages').classList.contains('hide-' + k)));
      if (!r.onlyUnknown) fail(tag + ': other layers shown in Unrecognised only');
      await page.screenshot({ path: path.join(OUT, `default-${tag}.png`), fullPage: false });
      await page.$('section.plate').then(el => el.screenshot({ path: path.join(OUT, `plate-${tag}.png`) }));
      const info = () => page.evaluate(() => ({
        n: document.querySelectorAll('#pages .unk:not(.done)').length, done: document.querySelectorAll('#pages .unk.done').length,
        count: document.getElementById('unkCount').textContent, ident: document.getElementById('identCount').hidden ? '' : document.getElementById('identCount').textContent,
        sizes: [...document.querySelectorAll('#pages .unk')].map(b => { const q = b.getBoundingClientRect(); return [Math.round(q.width), Math.round(q.height), getComputedStyle(b).borderTopWidth]; }),
        labels: [...document.querySelectorAll('#pages .unk')].map(b => b.getAttribute('aria-label')),
      }));
      const i0 = r.start = await info();
      if (!i0.n) fail(tag + ': no unrecognised highlights');
      if (i0.sizes.some(([w, h, bw]) => w < 10 || h < 10 || parseFloat(bw) < 3)) fail(tag + ': a highlight is too small at Fit ' + JSON.stringify(i0.sizes));
      // keyboard: N goes to the first mark, zooms in, focuses it
      await page.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
      await page.keyboard.press('n');
      await page.waitForTimeout(400);
      // on to the flat in bar 8 when there is one (the rag's flat the reading misses)
      r.firstLabel = await page.evaluate(() => document.activeElement.getAttribute('aria-label'));
      for (let k = 0; k < 5 && !/bar 8\b/.test(await page.evaluate(() => document.activeElement.getAttribute('aria-label') || '')); k++) { await page.keyboard.press('n'); await page.waitForTimeout(300); }
      const isFlat = /bar 8\b/.test(await page.evaluate(() => document.activeElement.getAttribute('aria-label') || ''));
      r.afterN = await page.evaluate(() => ({ focus: document.activeElement && document.activeElement.className, label: document.activeElement && document.activeElement.getAttribute('aria-label'), zoom: document.getElementById('zoomLabel').textContent,
        inView: (() => { const q = document.activeElement.getBoundingClientRect(); return q.top >= 0 && q.bottom <= innerHeight && q.left >= 0 && q.right <= innerWidth; })() }));
      if (!/unk/.test(r.afterN.focus || '') || !/^Unrecognised mark 1 of/.test(r.firstLabel || '')) fail(tag + ': N did not focus the first mark ' + JSON.stringify(r.afterN));
      if (!r.afterN.inView) fail(tag + ': the selected mark is not in view');
      const xml0 = await page.evaluate(() => document.getElementById('xml').value);
      // open: Enter (keyboard) at 1280, a tap at 400
      if (touch) { const b = await page.$('#pages .unk.sel'); const q = await b.boundingBox(); await page.touchscreen.tap(q.x + q.width / 2, q.y + q.height / 2); }
      else await page.keyboard.press('Enter');
      await page.waitForTimeout(200);
      r.pop = await page.evaluate(() => ({ open: !document.getElementById('idPop').hidden, focus: document.activeElement && document.activeElement.id, where: document.getElementById('idWhere').textContent }));
      if (!r.pop.open || r.pop.focus !== 'idType') fail(tag + ': popover did not open with focus on the type ' + JSON.stringify(r.pop));
      await page.selectOption('#idType', isFlat ? 'acc:flat' : 'acc:natural');
      r.effect = await page.textContent('#idEffect');
      await page.screenshot({ path: path.join(OUT, `popover-${tag}.png`) });
      // Escape closes and returns focus; open again and save
      await page.keyboard.press('Escape');
      r.esc = await page.evaluate(() => document.getElementById('idPop').hidden && /unk/.test(document.activeElement.className));
      if (!r.esc) fail(tag + ': Escape did not close the popover back to the mark');
      if (touch) { const b = await page.$('#pages .unk.sel'); const q = await b.boundingBox(); await page.touchscreen.tap(q.x + q.width / 2, q.y + q.height / 2); }
      else await page.keyboard.press('Enter');
      await page.selectOption('#idType', isFlat ? 'acc:flat' : 'acc:natural');
      if (touch) await page.tap('#idSave'); else await page.click('#idSave');
      await page.waitForTimeout(600);
      const i1 = r.saved = await info();
      r.corrNote = await page.evaluate(() => document.getElementById('corrNote').hidden ? null : document.getElementById('corrNote').textContent);
      const xml1 = await page.evaluate(() => document.getElementById('xml').value);
      const accRe = isFlat ? /<accidental>flat<\/accidental>/g : /<accidental>natural<\/accidental>/g;
      r.naturals = [(xml0.match(accRe) || []).length, (xml1.match(accRe) || []).length];
      if (i1.done !== 1 || i1.n !== i0.n - 1) fail(tag + ': after saving ' + JSON.stringify([i0.n, i1.n, i1.done]));
      if (!/Identified by you: 1/.test(i1.ident)) fail(tag + ': identified count ' + i1.ident);
      if (!(r.effect || '').trim()) fail(tag + ': no effect text');
      if (isFlat && !/^Makes/.test(r.effect)) fail(tag + ': the flat in bar 8 found no note: ' + r.effect);
      if (/Makes/.test(r.effect) && !(r.naturals[1] > r.naturals[0])) fail(tag + ': the natural was not applied to the MusicXML ' + JSON.stringify(r.naturals));
      await page.screenshot({ path: path.join(OUT, `saved-${tag}.png`) });
      // labelled examples
      await page.click('#identCopy');
      await page.waitForTimeout(500);
      const ex = await page.evaluate(() => navigator.clipboard.readText().catch(() => ''));
      try { const j = JSON.parse(ex); r.examples = { n: j.examples.length, type: j.examples[0].type, sub: j.examples[0].sub, png: j.examples[0].png.slice(0, 22) }; } catch (e) { r.examples = null; }
      if (!r.examples || r.examples.n !== 1 || !/^data:image\/png/.test(r.examples.png)) fail(tag + ': labelled examples ' + String(ex).slice(0, 120));
      // reload: label kept, correction applied again
      await page.reload(); await ready();
      const i2 = r.reloaded = await info();
      r.corrAfter = await page.evaluate(() => window.__omrResult.corrections);
      if (i2.done !== 1) fail(tag + ': label not kept over a reload');
      if (/Makes/.test(r.effect) && r.corrAfter !== 1) fail(tag + ': correction not re-applied after reload (' + r.corrAfter + ')');
      // repair notes carry the label
      await page.click('#repairToggle');
      await page.click('#rpCopy');
      await page.waitForTimeout(300);
      const rn = await page.evaluate(() => navigator.clipboard.readText().catch(() => ''));
      try { const j = JSON.parse(rn); r.repairIdent = j.pages[0].identified[0]; } catch (e) { r.repairIdent = null; }
      if (!r.repairIdent || r.repairIdent.type !== 'acc' || r.repairIdent.sub !== (isFlat ? 'flat' : 'natural') || !Array.isArray(r.repairIdent.nearestHeads)) fail(tag + ': repair notes lack the label');
      await page.keyboard.press('Escape');
      // the older custom choice became the custom set
      await page.click('.preset[data-mode="custom"]');
      r.customRests = await page.evaluate(() => document.querySelector('#layers button[data-layer="rests"]').getAttribute('aria-pressed'));
      if (r.customRests !== 'false') fail(tag + ': older layer choice not kept as the custom set');
      await page.click('.preset[data-mode="unknown"]');
      r.hscroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      if (r.hscroll) fail(tag + ': horizontal scroll');
    } catch (e) { fail(tag + ': ' + e.message.split('\n')[0]); }
    await ctx.close();
  }
  if (out.errors.length) fail(out.errors.length + ' console/page errors');
  out.ok = out.failures.length === 0;
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
  process.exit(out.ok ? 0 : 1);
});
