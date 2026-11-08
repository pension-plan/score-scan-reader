// Browser feasibility bench: onnxruntime-web from a public CDN (script tag / ESM / blob worker),
// self-hosted .wasm + models served same-origin under an artifact-like CSP, run in headless Chromium.
// usage: node src/web_bench.mjs [configs.json]   -> out/web/results.jsonl
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CORE = fs.readFileSync(path.join(ROOT, 'src/copista_core.mjs'), 'utf8').replace(/^export /gm, '');
const ORTDIR = (v) => (v === '1.30.0' ? path.join(ROOT, 'node_modules/onnxruntime-web/dist')
  : path.join(ROOT, 'ortweb', v, 'package/dist'));
const CSP = {
  // what the artifact host is described to allow: CDN scripts, same-origin fetch/worker, blob workers
  strict: "default-src 'none'; script-src https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com " +
    "'unsafe-inline' 'wasm-unsafe-eval'; connect-src 'self' blob: data:; worker-src 'self' blob:; " +
    "img-src 'self' blob: data:; style-src 'unsafe-inline'",
  self: "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline' " +
    "'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' blob: data:",
  none: null,
};
const TYPES = { '.wasm': 'application/wasm', '.mjs': 'text/javascript', '.js': 'text/javascript',
  '.json': 'application/json', '.png': 'image/png', '.onnx': 'application/octet-stream', '.html': 'text/html' };

function cdnUrl(cdn, ver, file) {
  if (cdn === 'cdnjs') return `https://cdnjs.cloudflare.com/ajax/libs/onnxruntime-web/${ver}/${file}`;
  if (cdn === 'local') return `/assets/ort/${ver}/${file}`;
  return `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ver}/dist/${file}`;
}

// page logic shared by main thread and worker (runs after `ort` exists)
const RUN = `
async function runBench(ort, P, img) {
  const out = { ortVersion: ort.env && ort.env.versions ? ort.env.versions : null };
  ort.env.wasm.numThreads = P.threads;
  // string prefix: ORT >= 1.21 also loads the .mjs glue from there (dynamic import -> needs script-src 'self');
  // object form {wasm} keeps the glue embedded in *.bundle.min.mjs and only fetches the .wasm (connect-src)
  ort.env.wasm.wasmPaths = P.wasmObj ? { wasm: P.wasmBase + 'ort-wasm-simd-threaded.wasm' } : P.wasmBase;
  if (P.simd === false) ort.env.wasm.simd = false;
  const t0 = performance.now();
  const opt = { executionProviders: ['wasm'] };
  const get = async (u) => new Uint8Array(await (await fetch(u)).arrayBuffer());
  const mk = async (name) => {
    const o = { ...opt };
    if (P.external && P.external[name]) o.externalData = P.external[name].map((f) => ({ path: f, data: P.modelBase + f }));
    return ort.InferenceSession.create(await get(P.modelBase + name), o);
  };
  const sessions = { dense: await mk(P.dense), rel: await mk(P.rel) };
  out.load_ms = Math.round(performance.now() - t0);
  const meta = await (await fetch(P.modelBase + P.meta)).json();
  const runs = [];
  for (let k = 0; k < P.reps; k++) {
    const t1 = performance.now();
    const r = await detect(ort, sessions, meta, img);
    runs.push({ total_ms: Math.round(performance.now() - t1), ...r.timing, n: r.dets.length,
      notes: r.dets.filter((d) => d.cls.startsWith('note_')).length });
    out.dets = r.dets;
  }
  out.runs = runs;
  return out;
}`;

function page(q) {
  const ver = q.get('ver'), mode = q.get('mode'), cdn = q.get('cdn') || 'jsdelivr';
  const umdFile = 'ort.wasm.min.js';
  const esmFile = ver === '1.20.1' ? 'ort.bundle.min.mjs' : 'ort.wasm.bundle.min.mjs';
  const P = {
    threads: Number(q.get('threads') || 1), reps: Number(q.get('reps') || 2),
    dense: q.get('dense'), rel: q.get('rel'), meta: q.get('meta'), img: q.get('img'),
    external: q.get('external') ? JSON.parse(q.get('external')) : null,
    wasmObj: q.get('wasmobj') === '1',
  };
  const head = `<meta charset="utf-8"><title>ort bench</title>`;
  const common = `
<script>${CORE}</script>
<script>${RUN}
const Q = new URLSearchParams(location.search);
const P = ${JSON.stringify(P)};
P.wasmBase = new URL('/assets/ort/${ver}/', location.href).href;
P.modelBase = new URL('/assets/models/', location.href).href;
window.__errors = [];
window.addEventListener('error', (e) => window.__errors.push(String(e.message || e)));
window.addEventListener('unhandledrejection', (e) => window.__errors.push(String(e.reason && (e.reason.stack || e.reason))));
document.addEventListener('securitypolicyviolation', (e) => window.__errors.push('CSP ' + e.violatedDirective + ' ' + e.blockedURI));
async function loadGray(u) {
  const bmp = await createImageBitmap(await (await fetch(u)).blob());
  const c = new OffscreenCanvas(bmp.width, bmp.height); const g = c.getContext('2d');
  g.drawImage(bmp, 0, 0); const d = g.getImageData(0, 0, bmp.width, bmp.height).data;
  const a = new Uint8ClampedArray(bmp.width * bmp.height);
  for (let i = 0; i < a.length; i++) a[i] = d[i * 4];
  return { width: bmp.width, height: bmp.height, data: a };
}
async function go(getOrt) {
  try {
    const img = await loadGray('/assets/scans/' + P.img);
    let res;
    if (${JSON.stringify(mode)}.startsWith('worker')) {
      const src = ${JSON.stringify(mode)} === 'worker-esm'
        // static "import ... from <CDN>" fails in a blob: module worker (measured); dynamic import() works
        ? document.getElementById('wcore').textContent + '\\nconst ortP = import(' + JSON.stringify(${JSON.stringify(cdnUrl(cdn, ver, esmFile))}) + ');' +
          '\\nself.onmessage = async (e) => { try { const ort = await ortP; self.postMessage({ ok: await runBench(ort, e.data.P, e.data.img) }); } catch (err) { self.postMessage({ err: String(err && (err.stack || err)) }); } };'
        : 'importScripts(' + JSON.stringify(${JSON.stringify(cdnUrl(cdn, ver, umdFile))}) + ');\\n' + document.getElementById('wcore').textContent +
          '\\nself.onmessage = async (e) => { try { self.postMessage({ ok: await runBench(self.ort, e.data.P, e.data.img) }); } catch (err) { self.postMessage({ err: String(err && (err.stack || err)) }); } };';
      const url = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
      const w = new Worker(url, ${JSON.stringify(mode)} === 'worker-esm' ? { type: 'module' } : undefined);
      w.onerror = (e) => window.__errors.push('worker error ' + (e.message || e));
      res = await new Promise((ok, bad) => { w.onmessage = (e) => (e.data.err ? bad(new Error(e.data.err)) : ok(e.data.ok)); w.postMessage({ P, img }, [img.data.buffer]); });
      res.where = 'worker';
    } else {
      res = await runBench(await getOrt(), P, img);
      res.where = 'main';
    }
    res.crossOriginIsolated = self.crossOriginIsolated;
    window.__result = res;
  } catch (e) { window.__result = { error: String(e && (e.stack || e)), errors: window.__errors }; }
}
</script>
<script type="text/plain" id="wcore">${CORE}\n${RUN}</script>`;
  let loader;
  if (mode === 'umd' || mode.startsWith('worker')) {
    loader = `${mode === 'umd' ? `<script src="${cdnUrl(cdn, ver, umdFile)}" crossorigin="anonymous"></script>` : ''}
<script>go(async () => window.ort);</script>`;
  } else { // esm bundle from CDN
    loader = `<script type="module">import * as ort from ${JSON.stringify(cdnUrl(cdn, ver, esmFile))}; go(async () => ort);</script>`;
  }
  return `${head}${common}${loader}`;
}

function serve() {
  const srv = http.createServer((req, res) => {
    const u = new URL(req.url, 'http://x');
    let file = null;
    if (u.pathname === '/bench.html') {
      const csp = CSP[u.searchParams.get('csp') || 'strict'];
      const h = { 'content-type': 'text/html; charset=utf-8' };
      if (csp) h['content-security-policy'] = csp;
      if (u.searchParams.get('coi') === '1') {
        h['cross-origin-opener-policy'] = 'same-origin'; h['cross-origin-embedder-policy'] = 'credentialless';
      }
      res.writeHead(200, h);
      return res.end(page(u.searchParams));
    }
    let m;
    if ((m = u.pathname.match(/^\/assets\/ort\/([\d.]+)\/(.+)$/))) file = path.join(ORTDIR(m[1]), m[2]);
    else if ((m = u.pathname.match(/^\/assets\/models\/(.+)$/))) file = path.join(ROOT, 'out/onnx', m[1]);
    else if ((m = u.pathname.match(/^\/assets\/scans\/(.+)$/))) file = path.join(ROOT, 'scans', m[1]);
    if (!file || !fs.existsSync(file)) { res.writeHead(404); return res.end('nf'); }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream',
      'cross-origin-resource-policy': 'same-origin' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((ok) => srv.listen(0, '127.0.0.1', () => ok(srv)));
}

const DEFAULT = [];
for (const ver of ['1.18.0', '1.20.1', '1.22.0', '1.30.0']) {
  for (const mode of ['umd', 'esm', 'worker-umd', 'worker-esm']) {
    if (ver === '1.18.0' && mode.endsWith('esm')) continue;
    DEFAULT.push({ ver, mode, csp: 'strict', dense: 'copista2m-dense.int8w.onnx', rel: 'copista2m-rel.int8w.onnx', reps: 1 });
  }
}

const configs = process.argv[2] ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) : DEFAULT;
const srv = await serve();
const port = srv.address().port;
const exe = path.join(process.env.HOME, '.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux-arm64/chrome-headless-shell');
const browser = await chromium.launch({ executablePath: exe, args: ['--enable-features=SharedArrayBuffer'] });
fs.mkdirSync(path.join(ROOT, 'out/web'), { recursive: true });
for (const c of configs) {
  const q = new URLSearchParams({ ver: c.ver, mode: c.mode, csp: c.csp || 'strict', cdn: c.cdn || 'jsdelivr',
    threads: String(c.threads || 1), reps: String(c.reps || 2), dense: c.dense, rel: c.rel,
    meta: c.meta || 'copista2m-classes.json', img: c.img || 'satb_closed_300_scan.png', coi: c.coi ? '1' : '0',
    wasmobj: c.wasmobj ? '1' : '0' });
  if (c.external) q.set('external', JSON.stringify(c.external));
  const pg = await browser.newPage();
  const consoleErr = [];
  pg.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') consoleErr.push(m.text().slice(0, 300)); });
  const t0 = Date.now();
  let res;
  try {
    await pg.goto(`http://127.0.0.1:${port}/bench.html?${q}`);
    // poll with evaluate (CDP callFunctionOn is not subject to page CSP; waitForFunction uses eval)
    const deadline = Date.now() + (c.timeout || 900000);
    while (!(await pg.evaluate(() => !!window.__result))) {
      if (Date.now() > deadline) throw new Error('timeout');
      await new Promise((r) => setTimeout(r, 500));
    }
    res = await pg.evaluate(() => ({ ...window.__result, pageErrors: window.__errors }));
  } catch (e) { res = { error: String(e).slice(0, 500) }; }
  const dets = res.dets; delete res.dets;
  const rec = { ...c, wall_s: (Date.now() - t0) / 1000, ok: !res.error, ...res, console: consoleErr.slice(0, 6) };
  if (dets && c.saveDets) fs.writeFileSync(path.join(ROOT, 'out/web', `${c.saveDets}.json`), JSON.stringify({ dets }));
  fs.appendFileSync(path.join(ROOT, 'out/web/results.jsonl'), JSON.stringify(rec) + '\n');
  console.log(JSON.stringify({ ver: c.ver, mode: c.mode, csp: c.csp, cdn: c.cdn, dense: c.dense, ok: rec.ok,
    where: res.where, runs: res.runs, load_ms: res.load_ms, error: res.error && res.error.slice(0, 300),
    pageErrors: (res.pageErrors || []).slice(0, 3) }));
  await pg.close();
}
await browser.close();
srv.close();
