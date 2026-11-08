// Screenshots of the detection overlay (every symbol layer, labels, ink not
// recognised) on the default sample at 1280 and 400 px, light and dark.
//   node tools/pw/overlay-shots.js <outdir>
// Fails (exit 1) on console / page errors, a missing layer, labels drawn
// while too small to read, or horizontal page scroll.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, '../../work/overlay'));
fs.mkdirSync(OUT, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.pdf': 'application/pdf', '.gz': 'application/gzip', '.wasm': 'application/wasm' };
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
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const out = { errors: [], failures: [], runs: {} };
  for (const scheme of ['light', 'dark']) for (const width of [1280, 400]) {
    const tag = width + (scheme === 'dark' ? '-dark' : '');
    const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
    page.on('console', m => { if (m.type() === 'error') out.errors.push(tag + ': ' + m.text()); });
    page.on('pageerror', e => out.errors.push(tag + ' pageerror: ' + e.message));
    try {
      await page.goto(`http://localhost:${port}/`);
      await page.evaluate(() => { try { localStorage.removeItem('ssr.layers'); localStorage.removeItem('ssr.zoom'); } catch (e) {} });
      await page.waitForFunction(() => window.__omrResult, null, { timeout: 240000 });
      await page.waitForTimeout(300);
      const info = () => page.evaluate(() => {
        const q = (s) => document.querySelectorAll('#pages ' + s).length;
        return {
          rests: q('.ov-rests rect'), clefs: q('.ov-clefs path, .ov-clefs rect'), keys: q('.ov-keys rect'), times: q('.ov-times rect'),
          marks: q('.ov-marks > *'), unknown: q('.ov-unknown rect'), labels: q('.ov-labels text'), stems: q('.ov-stem'),
          labelsShown: !document.getElementById('pages').classList.contains('lbl-small'),
          layers: [...document.querySelectorAll('#layers .layer')].map(b => b.textContent.trim()),
          hscroll: document.documentElement.scrollWidth > window.innerWidth,
          sample: [...document.querySelectorAll('#pages .ov-labels text')].slice(0, 12).map(t => t.textContent),
        };
      });
      const fit = await info();
      out.runs[tag] = { fit };
      for (const k of ['rests', 'clefs', 'keys', 'marks', 'unknown', 'labels']) if (!fit[k]) out.failures.push(`${tag}: no ${k} drawn`);
      if (fit.hscroll) out.failures.push(tag + ': horizontal scroll at fit');
      const plate = await page.$('section.plate');
      await plate.screenshot({ path: path.join(OUT, `fit-${tag}.png`) });
      // zoom in until labels show, then a close-up of the first system
      for (let k = 0; k < 4; k++) { if (await page.evaluate(() => !document.getElementById('pages').classList.contains('lbl-small'))) break; await page.click('#zoomIn'); await page.waitForTimeout(150); }
      const z = await info();
      out.runs[tag].zoom = { labelsShown: z.labelsShown, zoom: await page.textContent('#zoomLabel'), hscroll: z.hscroll, sample: z.sample };
      if (!z.labelsShown) out.failures.push(tag + ': labels never shown after zooming in');
      if (z.hscroll) out.failures.push(tag + ': horizontal page scroll when zoomed');
      const shot = async (name, fx, fy) => {
        const r = await page.evaluate(([fx, fy]) => {
          const el = document.getElementById('pages'), fr = el.querySelector('.pageframe');
          el.scrollLeft = (el.scrollWidth - el.clientWidth) * fx;
          const f = fr.getBoundingClientRect();
          window.scrollTo(0, window.scrollY + f.top + f.height * fy - 40);
          const b = el.getBoundingClientRect();
          return { x: b.x, y: 40, w: b.width, h: Math.min(window.innerHeight - 40, 640) };
        }, [fx, fy]);
        await page.waitForTimeout(100);
        await page.screenshot({ path: path.join(OUT, name), clip: { x: r.x, y: r.y, width: r.w, height: r.h } });
      };
      await shot(`zoom-${tag}.png`, 0, 0.02);
      await shot(`zoom-mid-${tag}.png`, 0.45, 0.3);
      out.runs[tag].wide = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1 && !e.closest('#pages')).slice(0, 5).map(e => e.tagName + '#' + e.id + '.' + e.className));
      // layer toggle: switch off unrecognised and labels, check they hide and persist
      await page.click('#layers button[data-layer="unknown"]');
      const hid = await page.evaluate(() => getComputedStyle(document.querySelector('#pages .ov-unknown')).display === 'none' && localStorage.getItem('ssr.layers'));
      if (!hid) out.failures.push(tag + ': unrecognised layer toggle did not hide / persist');
      await page.click('#layers button[data-layer="unknown"]');
    } catch (e) { out.failures.push(tag + ': ' + e.message.split('\n')[0]); }
    await page.close();
  }
  if (out.errors.length) out.failures.push(out.errors.length + ' console/page errors');
  out.ok = out.failures.length === 0;
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
  process.exit(out.ok ? 0 : 1);
});
