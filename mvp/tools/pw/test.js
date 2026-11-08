const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const DIST = path.join(__dirname, '../../dist');
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
}).listen(18931, async () => {
  const browser = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell' });
  const out = { errors: [] };
  for (const width of [1280, 400]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    page.on('console', m => { if (m.type() === 'error') out.errors.push(width + ': ' + m.text()); });
    page.on('pageerror', e => out.errors.push(width + ' pageerror: ' + e.message));
    const t0 = Date.now();
    await page.goto('http://localhost:18931/');
    await page.waitForFunction(() => window.__omrResult, null, { timeout: 180000 });
    out['result' + width] = await page.evaluate(() => window.__omrResult);
    out['secs' + width] = (Date.now() - t0) / 1000;
    out['status' + width] = await page.textContent('#status');
    out['hscroll' + width] = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    out['osmd' + width] = await page.evaluate(() => document.querySelectorAll('#osmd svg').length + ' svg; ' + document.getElementById('osmdNote').textContent);
    await page.screenshot({ path: path.join(__dirname, `../../work/shot${width}.png`), fullPage: width === 1280 });
    await page.close();
  }
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
});
