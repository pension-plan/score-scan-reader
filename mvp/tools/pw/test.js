// Browser smoke test of dist/index.html under the artifact CSP.
//   node tools/pw/test.js            (port from $PW_PORT, else a free port)
// Loads the page at 1280 and 400 px, in light and dark colour schemes; the sample
// converts on load. Fails (exit 1) on console errors, page errors, no result,
// horizontal scroll, or no rendered notation. Screenshots go to work/shot<w>[-dark].png.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
const WORK = path.join(__dirname, '../../work');
const CSP = "default-src 'self'; script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com";
const types = { '.html': 'text/html', '.js': 'text/javascript', '.pdf': 'application/pdf', '.gz': 'application/gzip' };
const srv = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') { res.writeHead(200, { 'Content-Type': 'text/html', 'Content-Security-Policy': CSP });
    return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(path.join(DIST, 'index.html'), 'utf8') + '</body></html>'); }
  const f = path.join(DIST, p);
  if (!f.startsWith(DIST) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream', 'Content-Security-Policy': CSP });
  fs.createReadStream(f).pipe(res);
}).listen(+process.env.PW_PORT || 0, async () => {
  const port = srv.address().port;
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const out = { port, errors: [], failures: [] };
  for (const scheme of ['light', 'dark']) {
    for (const width of [1280, 400]) {
      const tag = width + (scheme === 'dark' ? 'd' : '');
      const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
      page.on('console', m => { if (m.type() === 'error') out.errors.push(tag + ': ' + m.text()); });
      page.on('pageerror', e => out.errors.push(tag + ' pageerror: ' + e.message));
      const t0 = Date.now();
      try {
        await page.goto(`http://localhost:${port}/`);
        await page.waitForFunction(() => window.__omrResult, null, { timeout: 180000 });
        // the notation preview renders after the result is published
        await page.waitForFunction(() => document.querySelectorAll('#osmd svg').length > 0, null, { timeout: 60000 }).catch(() => {});
        out['result' + tag] = await page.evaluate(() => window.__omrResult);
        out['secs' + tag] = (Date.now() - t0) / 1000;
        out['status' + tag] = await page.textContent('#status');
        out['hscroll' + tag] = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
        out['osmd' + tag] = await page.evaluate(() => document.querySelectorAll('#osmd svg').length + ' svg; ' + document.getElementById('osmdNote').textContent);
        out['bg' + tag] = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
        const r = out['result' + tag];
        if (!r || !(r.parts && r.parts.length)) out.failures.push(tag + ': sample produced no parts');
        if (out['hscroll' + tag]) out.failures.push(tag + ': horizontal scroll');
        if (!/^[1-9]/.test(out['osmd' + tag])) out.failures.push(tag + ': notation preview did not render');
        await page.screenshot({ path: path.join(WORK, `shot${width}${scheme === 'dark' ? '-dark' : ''}.png`), fullPage: width === 1280 });
      } catch (e) {
        out.failures.push(tag + ': ' + e.message.split('\n')[0]);
      }
      await page.close();
    }
  }
  if (out.bg1280 && out.bg1280 === out.bg1280d) out.failures.push('dark scheme did not change the page background');
  if (out.errors.length) out.failures.push(out.errors.length + ' console/page errors');
  out.ok = out.failures.length === 0;
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
  process.exit(out.ok ? 0 : 1);
});
