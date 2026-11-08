// Browser test of the shipped pre-clean: mvp/src bundled like build.js, run in a blob: worker under
// the artifact CSP with OMR_ASSET_BASE set as app.js does; front() pre-cleans a thick photocopy
// (OpenCV loaded synchronously: sync XHR, blob: importScripts, new WebAssembly.Module) and leaves a
// clean page alone. Prints ops, timings and staff counts.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require(path.join(__dirname, '../../../mvp/tools/pw/node_modules/playwright'));
const SRC = path.join(__dirname, '../../../mvp/src'), DIST = path.join(__dirname, '../../../mvp/dist');
const CSP = "default-src 'self'; script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'";
let bundle = 'const process={env:{}};const defs={},cache={};function req(n){n=n.replace(/^\\.\\//,"").replace(/\\.js$/,"");if(cache[n])return cache[n].exports;if(!defs[n])return {};const m={exports:{}};cache[n]=m;defs[n](req,m,m.exports);return m.exports;}\n';
for (const f of fs.readdirSync(SRC).filter(f => f.endsWith('.js'))) bundle += `defs[${JSON.stringify(f.slice(0, -3))}]=function(require,module,exports){\n${fs.readFileSync(path.join(SRC, f), 'utf8')}\n};\n`;
const worker = bundle + `
self.onmessage = (e) => {
  const out = [];
  for (const g of e.data.pages) {
    const t0 = performance.now();
    const fr = req('front').front({ width: g.width, height: g.height, data: new Uint8Array(g.data) });
    out.push({ name: g.name, ms: Math.round(performance.now() - t0), ops: fr.gray.preclean || null, staves: fr.staves.length, heads: fr.heads.length });
  }
  postMessage({ out, stats: req('cv').precleanStats });
};`;
const html = `<!doctype html><meta charset=utf-8><script>
window.run = async (pages) => { const src = 'self.OMR_ASSET_BASE=' + JSON.stringify(new URL('assets/', location.href).href) + ';\\n' + await (await fetch('/worker.js')).text();
  const w = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' })));
  return await new Promise((ok) => { w.onmessage = e => ok(e.data); w.onerror = e => ok({ err: e.message }); w.postMessage({ pages }); }); };
</script>`;
const { readGray } = require(path.join(SRC, 'image.js'));
const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  if (u === '/') { res.writeHead(200, { 'Content-Type': 'text/html', 'Content-Security-Policy': CSP }); return res.end(html); }
  if (u === '/worker.js') { res.writeHead(200, { 'Content-Type': 'text/javascript' }); return res.end(worker); }
  const f = path.join(DIST, u);
  if (f.startsWith(DIST) && fs.existsSync(f)) { res.writeHead(200, { 'Content-Type': 'text/javascript' }); return fs.createReadStream(f).pipe(res); }
  res.writeHead(404); res.end();
}).listen(0, async () => {
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const p = await browser.newPage(); const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
  await p.goto(`http://localhost:${srv.address().port}/`);
  const C = path.join(__dirname, '../../../mvp/work/cache');
  const pages = ['challenge__degradation__andantino-piano-clean__scan', 'challenge__degradation__andantino-piano-photocopy-thick__scan', 'challenge__degradation__andantino-piano-combo__scan-severe'].map(n => { const g = readGray(path.join(C, n + '__r200/p-1.pgm')); return { name: n.split('__').slice(2).join('/'), width: g.width, height: g.height, data: Array.from(g.data) }; });
  const r = await p.evaluate(async (pages) => window.run(pages), pages);
  console.log(JSON.stringify(r, null, 1), errs.length ? errs : '');
  await browser.close(); srv.close();
});
