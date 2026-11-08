// Browser test of the ML detector under the artifact CSP (Playwright, headless Chromium).
//   node assets-src/ml/browser-test.js [page.pgm] [--nested]
// Serves dist/assets/ and a test page that bundles src/ml-worker.js + src/ml.js the way
// tools/build.js does; runs createBrowserDetector().detect() on the page (main thread,
// or with --nested from inside a blob: worker, as the app's recognition worker would),
// and compares the detections with onnxruntime-node on the same image.
const http = require('http'), fs = require('fs'), path = require('path');
const MVP = path.join(__dirname, '../..');
const { chromium } = require(path.join(MVP, 'tools/pw/node_modules/playwright'));
const CSP = "default-src 'self'; script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'";
const args = process.argv.slice(2);
const nested = args.includes('--nested');
const pgm = args.find(a => !a.startsWith('--')) || path.join(MVP, 'work/cache/synthetic__joplin-maple-leaf-piano__r200/p-1.pgm');
const { readGray } = require(path.join(MVP, 'src/image'));
const gray = readGray(pgm);
let bundle = 'const defs={},cache={};function req(n){n=n.replace(/^\\.\\//,"").replace(/\\.js$/,"");if(cache[n])return cache[n].exports;if(!defs[n])return {};const m={exports:{}};cache[n]=m;defs[n](req,m,m.exports);return m.exports;}\n';
for (const m of ['ml-worker', 'ml']) bundle += `defs[${JSON.stringify(m)}]=function(require,module,exports){\n${fs.readFileSync(path.join(MVP, 'src', m + '.js'), 'utf8')}\n};\n`;
const page = `<!doctype html><meta charset="utf-8"><title>ML test</title><script>
${bundle}
window.mlReq = req;
window.mlBundle = ${JSON.stringify(bundle)};
</script>`;
const srv = http.createServer((q, res) => {
  const p = decodeURIComponent(q.url.split('?')[0]);
  if (p === '/') { res.writeHead(200, { 'Content-Type': 'text/html', 'Content-Security-Policy': CSP }); return res.end(page); }
  if (p === '/gray.bin') { res.writeHead(200, { 'Content-Type': 'application/octet-stream' }); return res.end(Buffer.from(gray.data.buffer, gray.data.byteOffset, gray.data.byteLength)); }
  const f = path.join(MVP, 'dist', p);
  if (!f.startsWith(path.join(MVP, 'dist')) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': /\.wasm$/.test(f) ? 'application/wasm' : 'application/octet-stream', 'Content-Security-Policy': CSP });
  fs.createReadStream(f).pipe(res);
}).listen(0, async () => {
  const port = srv.address().port;
  const out = { pgm, nested, errors: [], csp: [] };
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  try {
    const pg = await browser.newPage();
    pg.on('console', m => { if (m.type() === 'error') out.errors.push(m.text()); if (/Content Security Policy/i.test(m.text())) out.csp.push(m.text()); });
    pg.on('pageerror', e => out.errors.push('pageerror: ' + e.message));
    await pg.goto(`http://localhost:${port}/`);
    const r = await pg.evaluate(async ({ w, h, nested }) => {
      const data = new Uint8ClampedArray(await (await fetch('gray.bin')).arrayBuffer());
      const t0 = performance.now();
      if (!nested) {
        const det = window.mlReq('./ml').createBrowserDetector();
        const a = await det.detect({ width: w, height: h, data });
        const t1 = performance.now();
        const b = await det.detect({ width: w, height: h, data });
        det.terminate();
        return { dets: a.dets, timing: a.timing, firstMs: Math.round(t1 - t0), warmMs: Math.round(performance.now() - t1) };
      }
      // from inside a blob: classic worker (the app's recognition worker): absolute base
      const base = new URL('assets/', location.href).href;
      const src = window.mlBundle + `\nself.onmessage = async (e) => { try { const det = req('./ml').createBrowserDetector({ base: ${JSON.stringify(base)} });
        const t0 = performance.now(); const a = await det.detect(e.data); self.postMessage({ dets: a.dets, timing: a.timing, firstMs: Math.round(performance.now() - t0) }); }
        catch (err) { self.postMessage({ error: String(err && err.message || err) }); } };`;
      const wk = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' })));
      return await new Promise((res) => { wk.onmessage = (e) => res(e.data); wk.onerror = (e) => res({ error: 'worker error ' + e.message }); wk.postMessage({ width: w, height: h, data }); });
    }, { w: gray.width, h: gray.height, nested });
    if (r.error) throw new Error(r.error);
    out.browser = { n: r.dets.length, notes: r.dets.filter(d => d.cls.startsWith('note_')).length, firstMs: r.firstMs, warmMs: r.warmMs, timing: r.timing };
    // the same image through onnxruntime-node
    const ml = require(path.join(MVP, 'src/ml'));
    const det = await ml.createNodeDetector();
    const n = await det.detect(gray);
    // same class, centre within 2 px
    const c = d => [(d.xyxy[0] + d.xyxy[2]) / 2, (d.xyxy[1] + d.xyxy[3]) / 2];
    const same = r.dets.filter(d => { const [x, y] = c(d); return n.dets.some(e => e.cls === d.cls && Math.hypot(c(e)[0] - x, c(e)[1] - y) <= 2); }).length;
    out.node = { n: n.dets.length, notes: n.dets.filter(d => d.cls.startsWith('note_')).length };
    out.agreement = +(same / Math.max(n.dets.length, r.dets.length)).toFixed(3);
    out.ok = out.errors.length === 0 && out.agreement >= 0.95;
  } catch (e) { out.errors.push(e.message); out.ok = false; }
  console.log(JSON.stringify(out, null, 1));
  await browser.close(); srv.close();
  process.exit(out.ok ? 0 : 1);
});
