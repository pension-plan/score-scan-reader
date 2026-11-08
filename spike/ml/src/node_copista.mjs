// Node harness: run the copista detector (src/copista_core.mjs) on spike scans with
// onnxruntime-node (native CPU EP) or onnxruntime-web (wasm, same kernels as the browser).
// usage: node src/node_copista.mjs <runtime node|web> <size 2m|28m> <variant fp32|fp16w|int8w|int8d> <threads> <img.png...>
// writes out/nodedets/<runtime>-<size>-<variant>-t<threads>/<stem>.json  {timing, cpu_ms, dets}
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { detect } from './copista_core.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [runtime, size, variant, threadsS, ...imgs] = process.argv.slice(2);
const threads = Number(threadsS);
const ort = runtime === 'web' ? await import('onnxruntime-web') : await import('onnxruntime-node');
if (runtime === 'web') {
  ort.env.wasm.numThreads = threads;
  ort.env.wasm.wasmPaths = path.join(ROOT, 'node_modules/onnxruntime-web/dist/');
}
const suf = variant === 'fp32' ? '' : `.${variant}`;
const mdir = path.join(ROOT, 'out/onnx');
const opts = runtime === 'web'
  ? { executionProviders: ['wasm'] }
  : { executionProviders: ['cpu'], intraOpNumThreads: threads, interOpNumThreads: 1 };
const load = async (p) => ort.InferenceSession.create(runtime === 'web' ? fs.readFileSync(p) : p, opts);
let t0 = Date.now();
const sessions = {
  dense: await load(path.join(mdir, `copista${size}-dense${suf}.onnx`)),
  rel: await load(path.join(mdir, `copista${size}-rel${suf}.onnx`)),
};
const loadMs = Date.now() - t0;
const meta = JSON.parse(fs.readFileSync(path.join(mdir, `copista${size}-classes.json`), 'utf8'));
const outDir = path.join(ROOT, 'out/nodedets', `${runtime}-${size}-${variant}-t${threads}`);
fs.mkdirSync(outDir, { recursive: true });
for (const f of imgs) {
  const png = PNG.sync.read(fs.readFileSync(f));
  const g = new Uint8ClampedArray(png.width * png.height);
  for (let i = 0; i < g.length; i++) g[i] = png.data[i * 4];
  const c0 = process.cpuUsage();
  t0 = Date.now();
  const { dets, timing } = await detect(ort, sessions, meta, { width: png.width, height: png.height, data: g });
  const wall = Date.now() - t0;
  const c = process.cpuUsage(c0);
  const stem = path.basename(f, '.png');
  fs.writeFileSync(path.join(outDir, `${stem}.json`), JSON.stringify({ timing, wall_ms: wall,
    cpu_ms: Math.round((c.user + c.system) / 1000), load_ms: loadMs, dets }));
  console.log(JSON.stringify({ runtime, size, variant, threads, stem, wall_ms: wall,
    cpu_ms: Math.round((c.user + c.system) / 1000), ...timing, n: dets.length }));
}
