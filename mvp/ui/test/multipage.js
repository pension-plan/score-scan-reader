// Multi-page check of dist/index.html (L5a): long PDFs are read page by page.
//   node ui/test/multipage.js [--html path] [--pages 24] [--width 1280] [--out file.json] [--shots prefix] [--no-stop]
// Builds an N-page PDF from corpus scans (pdfunite, cached in work/ui-fixtures),
// serves the page under the simulated artifact CSP, waits for the sample, then
// drops the long PDF and records: pages read and their states, the cap warning,
// parts and measures, main-thread long tasks during the conversion (Long Tasks
// API), JS heap, time, page navigation, and then Stop after two pages.
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const MVP = path.join(__dirname, '../..');
const CORPUS = path.join(MVP, '../corpus');
const { chromium } = require(path.join(MVP, 'tools/pw/node_modules/playwright'));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const HTML = path.resolve(arg('--html', path.join(MVP, 'dist/index.html')));
const N = +arg('--pages', 24);
const WIDTH = +arg('--width', 1280);
const OUT = arg('--out', null);
const SHOTS = arg('--shots', null);
const DIST = path.join(MVP, 'dist');
const FIX = path.join(MVP, 'work/ui-fixtures');
const CSP = "default-src 'self'; script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com";

// a long "book": real and synthetic scans in a fixed order, repeated to N pages
function fixture(n) {
  fs.mkdirSync(FIX, { recursive: true });
  const out = path.join(FIX, `book-${n}.pdf`);
  if (fs.existsSync(out)) return out;
  const ids = ['real/methodist1905-st-anselm', 'synthetic/bach-bwv244-62-closed-en-3v', 'real/golden1923-america', 'synthetic/hymn-joyful-closed-3v',
    'real/methodist1905-tappan-dennis', 'synthetic/beach-prayer-ssaa-piano', 'synthetic/foster-jeanie-melody', 'real/haupt1867-aus-meines-herzens-grunde'];
  const srcs = [];
  let pages = 0;
  for (let k = 0; pages < n; k++) {
    const f = path.join(CORPUS, ids[k % ids.length], 'scan.pdf');
    const np = +String(execFileSync('pdfinfo', [f])).match(/Pages:\s+(\d+)/)[1];
    srcs.push(f); pages += np;
  }
  const tmp = out + '.tmp.pdf';
  execFileSync('pdfunite', [...srcs, tmp]);
  // trim to exactly n pages
  const trimmed = out + '.trim.pdf';
  const all = +String(execFileSync('pdfinfo', [tmp])).match(/Pages:\s+(\d+)/)[1];
  if (all > n) {
    const parts = [];
    for (let i = 1; i <= n; i++) { const p = `${out}.p${i}.pdf`; execFileSync('pdfseparate', ['-f', String(i), '-l', String(i), tmp, p]); parts.push(p); }
    execFileSync('pdfunite', [...parts, trimmed]);
    parts.forEach((p) => fs.unlinkSync(p));
    fs.renameSync(trimmed, out);
    fs.unlinkSync(tmp);
  } else fs.renameSync(tmp, out);
  return out;
}

const fixPath = fixture(N);
const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html', 'Content-Security-Policy': CSP });
    return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>[hidden]{display:none!important}</style></head><body>' + fs.readFileSync(HTML, 'utf8') + '</body></html>');
  }
  if (p === '/__fixture/book.pdf') { res.writeHead(200, { 'Content-Type': 'application/pdf' }); return fs.createReadStream(fixPath).pipe(res); }
  const f = path.join(DIST, p);
  if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Security-Policy': CSP });
  fs.createReadStream(f).pipe(res);
});

const LT = `(() => { window.__lt = []; try { new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__lt.push([Math.round(e.startTime), Math.round(e.duration)]); }).observe({ type: 'longtask', buffered: true }); } catch (e) {} })();`;
const dropBook = `(async () => {
  const buf = await (await fetch('/__fixture/book.pdf')).arrayBuffer();
  const dt = new DataTransfer(); dt.items.add(new File([buf], 'book.pdf', { type: 'application/pdf' }));
  const zone = document.getElementById('drop');
  window.__omrResult = null; window.__t0 = performance.now(); window.__lt = [];
  zone.dispatchEvent(new DragEvent('dragenter', { bubbles: true, cancelable: true, dataTransfer: dt }));
  zone.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
})()`;

srv.listen(0, async () => {
  const url = `http://localhost:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell', args: ['--enable-precise-memory-info'] });
  const ctx = await browser.newContext({ viewport: { width: WIDTH, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.addInitScript(LT);
  await page.goto(url);
  await page.waitForFunction(() => window.__omrResult, null, { timeout: 180000 });
  const sample = await page.evaluate(() => ({ secs: window.__omrResult.secs, engine: window.__omrResult.engine, lt: window.__lt.slice() }));
  const out = { html: path.relative(MVP, HTML), pages: N, width: WIDTH, sample: { secs: sample.secs, engine: sample.engine, longTasks: sample.lt.length, maxLongTaskMs: Math.max(0, ...sample.lt.map((x) => x[1])) } };

  // ---- the long document
  const samples = [];
  await page.evaluate(dropBook);
  const t0 = Date.now();
  let shot = false;
  while (Date.now() - t0 < 1500000) {
    const s = await page.evaluate(() => ({ done: !!window.__omrResult, chips: [...document.querySelectorAll('#pageChips .chip')].map((c) => c.dataset.state).join(''), heap: performance.memory ? performance.memory.usedJSHeapSize : 0 }));
    samples.push([Math.round((Date.now() - t0) / 1000), s.chips.replace(/done/g, 'D').replace(/queued/g, '.').replace(/work/g, 'W').replace(/render/g, 'R').replace(/empty/g, 'E').replace(/failed/g, 'F'), Math.round(s.heap / 1048576)]);
    if (SHOTS && !shot && /D.*D.*D/.test(samples[samples.length - 1][1]) && !s.done) {
      shot = true;
      await page.screenshot({ path: `${SHOTS}-during.png`, fullPage: false });
    }
    if (s.done) break;
    await page.waitForTimeout(2000);
  }
  const r = await page.evaluate(() => ({ res: window.__omrResult, secs: (performance.now() - window.__t0) / 1000, lt: window.__lt.slice(),
    hscroll: document.documentElement.scrollWidth > window.innerWidth, osmd: document.querySelectorAll('#osmd svg').length, osmdNote: document.getElementById('osmdNote').textContent,
    heap: performance.memory ? performance.memory.usedJSHeapSize : 0 }));
  const lt = r.lt.map((x) => x[1]).sort((a, b) => b - a);
  out.book = {
    secs: +r.secs.toFixed(1), engine: r.res && r.res.engine, error: r.res && r.res.error,
    pagesInfo: r.res && r.res.pages, parts: r.res && r.res.parts, measures: r.res && r.res.measures,
    capWarning: !!(r.res && (r.res.warnings || []).some((w) => /Only the first/.test(w))),
    longTasks: lt.length, longTaskMsTotal: lt.reduce((a, b) => a + b, 0), maxLongTaskMs: lt[0] || 0, top5: lt.slice(0, 5),
    heapMB: Math.round(r.heap / 1048576), peakHeapMB: Math.max(0, ...samples.map((s) => s[2])),
    hscroll: r.hscroll, osmd: r.osmd + ' svg; ' + r.osmdNote, timeline: samples.filter((_, i) => i % 3 === 0).map((s) => s.join(' ')),
  };
  // navigation: chip 5, then previous
  const nav = await page.evaluate(async () => {
    const chips = [...document.querySelectorAll('#pageChips .chip')];
    if (chips.length < 5) return { ok: false, n: chips.length };
    chips[4].click();
    await new Promise((r) => setTimeout(r, 50));
    const a = { label: document.getElementById('pgLabel').textContent, current: chips[4].getAttribute('aria-current'), img: !!document.querySelector('#pages img'), svg: !!document.querySelector('#pages svg.ov path') };
    document.getElementById('pgPrev').click();
    await new Promise((r) => setTimeout(r, 50));
    const b = { label: document.getElementById('pgLabel').textContent, current: chips[3].getAttribute('aria-current') };
    return { ok: true, a, b };
  });
  out.nav = nav;
  if (SHOTS) await page.screenshot({ path: `${SHOTS}-done.png`, fullPage: false });

  // ---- stop after two pages
  if (!process.argv.includes('--no-stop')) {
    await page.evaluate(dropBook);
    await page.waitForFunction(() => [...document.querySelectorAll('#pageChips .chip')].filter((c) => c.dataset.state === 'done').length >= 2, null, { timeout: 300000 });
    await page.click('#stop');
    await page.waitForFunction(() => window.__omrResult, null, { timeout: 300000 });
    out.stop = await page.evaluate(() => ({ read: window.__omrResult.pages && window.__omrResult.pages.read, states: window.__omrResult.pages && window.__omrResult.pages.states.join(','), warn: (window.__omrResult.warnings || []).find((w) => /Stopped/.test(w)) || null,
      parts: window.__omrResult.parts, title: document.getElementById('dropTitle').textContent, secs: (performance.now() - window.__t0) / 1000 }));
  }
  out.errors = errors.slice(0, 8);
  const b = out.book;
  out.checks = {
    allPagesRead: !!(b.pagesInfo && b.pagesInfo.read === N && b.pagesInfo.states.every((s) => s === 'done' || s === 'empty')),
    noCapWarning: !b.capWarning,
    hasParts: !!(b.parts && b.parts.length),
    navigation: !!(nav.ok && /Page 5 of/.test(nav.a.label) && nav.a.current === 'page' && nav.a.img && nav.a.svg && /Page 4 of/.test(nav.b.label)),
    stop: process.argv.includes('--no-stop') || !!(out.stop && out.stop.read >= 2 && out.stop.read < N && out.stop.warn),
    noErrors: errors.length === 0,
    noHScroll: !b.hscroll,
  };
  out.ok = Object.values(out.checks).every(Boolean);
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
  srv.close();
  process.exit(out.ok ? 0 : 1);
});
