// Browser check of "Mark for repair" on the default sample: drawing with mouse
// (1280 px) and touch (400 px, mobile), light and dark; pen, Shift line, box and
// circle tools; notes; undo (keys and button); persistence across a reload and
// re-conversion; Copy repair notes (JSON shape); Escape; no page scroll while
// drawing on touch, normal scrolling when off. Screenshots go to <outdir>.
//   node tools/pw/repair-shots.js <outdir>
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, '../../work/repair'));
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
  const port = srv.address().port, url = `http://localhost:${port}/`;
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const out = { errors: [], failures: [], runs: {} };
  const fail = (t) => out.failures.push(t);
  for (const scheme of ['light', 'dark']) for (const width of [1280, 400]) {
    const tag = width + (scheme === 'dark' ? '-dark' : '');
    const touch = width === 400;
    const ctx = await browser.newContext({ viewport: { width, height: 800 }, colorScheme: scheme, hasTouch: touch, isMobile: touch, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error') out.errors.push(tag + ': ' + m.text()); });
    page.on('pageerror', e => out.errors.push(tag + ' pageerror: ' + e.message));
    const r = out.runs[tag] = {};
    try {
      await page.goto(url);
      await page.evaluate(() => { try { Object.keys(localStorage).filter(k => k.startsWith('ssr.repair') || k === 'ssr.zoom').forEach(k => localStorage.removeItem(k)); } catch (e) {} });
      await page.reload();
      await page.waitForFunction(() => window.__omrResult, null, { timeout: 240000 });
      await page.waitForTimeout(300);
      // reachable by Tab
      let reached = false;
      for (let k = 0; k < 80 && !reached; k++) { await page.keyboard.press('Tab'); reached = await page.evaluate(() => document.activeElement && document.activeElement.id === 'repairToggle'); }
      r.tabReach = reached; if (!reached) fail(tag + ': Mark for repair not reachable by Tab');
      await page.keyboard.press('Enter');
      r.on = await page.evaluate(() => document.getElementById('repairToggle').getAttribute('aria-pressed') === 'true' && document.getElementById('pages').classList.contains('drawing'));
      if (!r.on) fail(tag + ': drawing mode did not turn on');
      const frameBox = async () => page.evaluate(() => { const f = document.querySelector('#pages .pageframe').getBoundingClientRect(); return { x: f.x, y: f.y, w: f.width, h: f.height }; });
      await page.evaluate(() => document.querySelector('#pages .pageframe').scrollIntoView({ block: 'start', behavior: 'instant' }));
      await page.waitForTimeout(600);
      let fb = await frameBox();
      const count = () => page.evaluate(() => document.querySelectorAll('#pages svg.rp .rp-mark').length);
      const cdp = touch ? await ctx.newCDPSession(page) : null;
      const drag = async (pts, shift) => {
        await page.evaluate(() => document.querySelector('#pages .pageframe').scrollIntoView({ block: 'start', behavior: 'instant' }));
        await page.waitForTimeout(150);
        fb = await frameBox();
        const P = pts.map(([fx, fy]) => [fb.x + fx * fb.w, fb.y + fy * fb.h]);
        if (touch && !shift) {
          await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: P[0][0], y: P[0][1] }] });
          for (const q of P.slice(1)) await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: q[0], y: q[1] }] });
          await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
        } else {
          if (shift) await page.keyboard.down('Shift');
          await page.mouse.move(P[0][0], P[0][1]); await page.mouse.down();
          for (const q of P.slice(1)) await page.mouse.move(q[0], q[1], { steps: 3 });
          await page.mouse.up();
          if (shift) await page.keyboard.up('Shift');
        }
        await page.waitForTimeout(60);
      };
      // (the mark list growing above the page shifts scrollY by scroll anchoring;
      // what matters is that the page under the finger did not move)
      await drag([[0.30, 0.12], [0.34, 0.14], [0.38, 0.12], [0.42, 0.15], [0.46, 0.12]]);   // pen squiggle
      const top0 = fb.y;
      r.scrollWhileDrawing = Math.round((await frameBox()).y - top0);
      if (Math.abs(r.scrollWhileDrawing) > 1) fail(tag + ': page scrolled while drawing (' + r.scrollWhileDrawing + ')');
      await drag([[0.50, 0.20], [0.60, 0.22], [0.70, 0.20]], true);                           // Shift: straight line
      await page.check('input[name="rpTool"][value="box"]', { force: true });
      fb = await frameBox();
      await drag([[0.15, 0.25], [0.25, 0.30]]);                                                // box
      await page.check('input[name="rpTool"][value="ellipse"]', { force: true });
      fb = await frameBox();
      await drag([[0.55, 0.38], [0.68, 0.45]]);                                                // circle
      r.marks = await count();
      r.tools = await page.evaluate(() => [...document.querySelectorAll('#rpList li span:nth-child(2)')].map(s => s.textContent));
      if (r.marks !== 4) fail(tag + ': expected 4 marks, got ' + r.marks + ' ' + JSON.stringify(r.tools));
      if (JSON.stringify(r.tools) !== JSON.stringify(['Pen', 'Line', 'Box', 'Circle'])) fail(tag + ': tools ' + JSON.stringify(r.tools));
      await page.fill('#rpList li:nth-child(1) input', 'missed chord note');
      await page.screenshot({ path: path.join(OUT, `drawn-${tag}.png`) });
      // undo: keys, then button
      await page.click('#pages', { position: { x: 2, y: 2 }, force: true }).catch(() => {});
      await page.evaluate(() => document.activeElement && document.activeElement.blur());
      await page.keyboard.press(process.platform === 'darwin' ? 'Meta+z' : 'Control+z');
      const afterKey = await count();
      await page.click('#rpUndo');
      const afterBtn = await count();
      r.undo = [afterKey, afterBtn];
      if (afterKey !== 3 || afterBtn !== 2) fail(tag + ': undo gave ' + afterKey + ', ' + afterBtn);
      // marks stay aligned when zoomed (same viewBox as the overlay)
      r.sameFrame = await page.evaluate(() => document.querySelector('#pages svg.rp').getAttribute('viewBox') === document.querySelector('#pages svg.ov').getAttribute('viewBox'));
      if (!r.sameFrame) fail(tag + ': repair layer frame differs from the overlay');
      // copy repair notes
      await page.click('#rpCopy');
      await page.waitForTimeout(200);
      const txt = await page.evaluate(() => navigator.clipboard.readText().catch(() => document.getElementById('rpOut').value));
      let j = null; try { j = JSON.parse(txt); } catch (e) { /* */ }
      r.json = j ? { format: j.format, pages: j.pages.length, marks: j.pages[0] && j.pages[0].marks.length, note: j.pages[0] && j.pages[0].marks[0].note,
        first: j.pages[0] && { bbox: j.pages[0].marks[0].bbox, measures: j.pages[0].marks[0].found.measures, heads: j.pages[0].marks[0].found.heads.length, sample: j.pages[0].marks[0].found.heads.slice(0, 2) } } : null;
      if (!j || j.format !== 'score-scan-reader/repair-notes' || j.pages[0].marks.length !== 2 || j.pages[0].marks[0].note !== 'missed chord note') fail(tag + ': copied notes wrong: ' + String(txt).slice(0, 200));
      else if (!Array.isArray(j.pages[0].marks[0].found.measures)) fail(tag + ': no measure numbers in notes');
      // Escape leaves draw mode; then touch scrolling works
      await page.keyboard.press('Escape');
      r.escOff = await page.evaluate(() => !document.getElementById('pages').classList.contains('drawing') && document.getElementById('repairBar').hidden);
      if (!r.escOff) fail(tag + ': Escape did not leave draw mode');
      if (touch) {
        fb = await frameBox();
        const ys = await page.evaluate(() => window.scrollY);
        const x = fb.x + fb.w * 0.5, ya = Math.min(700, fb.y + fb.h * 0.6);
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: ya }] });
        for (let k = 1; k <= 8; k++) await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: ya - 30 * k }] });
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
        await page.waitForTimeout(400);
        r.scrollWhenOff = (await page.evaluate(() => window.scrollY)) - ys;
        if (r.scrollWhenOff < 20) fail(tag + ': touch did not scroll with drawing off (' + r.scrollWhenOff + ')');
        if (await count() !== 2) fail(tag + ': a touch with drawing off made a mark');
      }
      // persistence across a reload (the sample converts again)
      await page.reload();
      await page.waitForFunction(() => window.__omrResult, null, { timeout: 240000 });
      await page.waitForTimeout(300);
      r.afterReload = await count();
      if (r.afterReload !== 2) fail(tag + ': marks after reload: ' + r.afterReload);
      r.noteAfterReload = await page.evaluate(() => { document.getElementById('repairToggle').click(); const i = document.querySelector('#rpList li input'); return i && i.value; });
      if (r.noteAfterReload !== 'missed chord note') fail(tag + ': note not kept: ' + r.noteAfterReload);
      await page.evaluate(() => document.querySelector('#pages .pageframe').scrollIntoView({ block: 'start', behavior: 'instant' }));
      await page.screenshot({ path: path.join(OUT, `reloaded-${tag}.png`) });
      const plate = await page.$('section.plate');
      await plate.screenshot({ path: path.join(OUT, `plate-${tag}.png`) });
      await page.click('#rpClear');
      r.cleared = await count();
      if (r.cleared !== 0) fail(tag + ': clear page left ' + r.cleared);
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
