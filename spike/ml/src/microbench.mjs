// Op-support + speed microbench for every candidate ONNX model/variant.
// usage: node src/microbench.mjs <runtime node|web> <threads> <model.onnx>...   (one JSON line per model)
// Feeds a representative input (shape per model family) of mid-gray noise, runs warm-up + 3 timed runs,
// reports load_ms, median run ms and CPU ms (process.cpuUsage, robust to a busy shared box).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [runtime, threadsS, ...models] = process.argv.slice(2);
const threads = Number(threadsS);
const ort = runtime === 'web' ? await import('onnxruntime-web') : await import('onnxruntime-node');
if (runtime === 'web') {
  ort.env.wasm.numThreads = threads;
  ort.env.wasm.wasmPaths = path.join(ROOT, 'node_modules/onnxruntime-web/dist/');
}

function rnd(n, base = 0.8, amp = 0.2) {
  const a = new Float32Array(n);
  let s = 12345;
  for (let i = 0; i < n; i++) { s = (s * 1103515245 + 12345) & 0x7fffffff; a[i] = base + amp * (s / 0x7fffffff - 0.5); }
  return a;
}

function feeds(name, sess) {
  const f = {};
  const T = (t, d, data) => new ort.Tensor(t, data, d);
  const u8 = (n) => Uint8Array.from(rnd(n, 200, 100), (v) => Math.max(0, Math.min(255, v)));
  if (name.startsWith('oemer-unet')) f.input = T('uint8', [1, 256, 256, 3], u8(256 * 256 * 3)); // tf2onnx: uint8 NHWC
  else if (name.startsWith('oemer-seg')) f.input = T('uint8', [1, 288, 288, 3], u8(288 * 288 * 3));
  else if (name.startsWith('homr-segnet')) f.input = T('float32', [1, 3, 320, 320], rnd(3 * 320 * 320, 200, 100));
  else if (name.startsWith('homr-enc')) f.input = T('float32', [1, 1, 256, 1280], rnd(256 * 1280));
  else if (name.startsWith('satbline')) f.input = T('float32', [1, 1, 128, 1200], rnd(128 * 1200, 0.1, 0.2));
  else if (name.startsWith('copista2m-dense') || name.startsWith('copista28m-dense'))
    f.x = T('float32', [1, 1, 1760, 1248], rnd(1760 * 1248));
  else if (name.startsWith('homr-dec')) {
    for (const k of sess.inputNames) {
      if (['rhythms', 'pitchs', 'lifts', 'articulations', 'slurs'].includes(k)) f[k] = T('int64', [1, 1], new BigInt64Array([1n]));
      else if (k === 'context') f[k] = T('float32', [1, 1280, 512], rnd(1280 * 512, 0, 1));
      else if (k === 'cache_len') f[k] = T('int64', [1], new BigInt64Array([0n]));
      else if (k.startsWith('cache_in')) f[k] = T('float32', [1, 8, 0, 64], new Float32Array(0));
    }
  } else return null;
  return f;
}

for (const m of models) {
  const name = path.basename(m).replace(/\.onnx$/, '');
  const rec = { runtime, threads, model: name, bytes: fs.statSync(m).size };
  try {
    const opts = runtime === 'web' ? { executionProviders: ['wasm'] }
      : { executionProviders: ['cpu'], intraOpNumThreads: threads, interOpNumThreads: 1 };
    let t0 = Date.now();
    const sess = await ort.InferenceSession.create(runtime === 'web' ? fs.readFileSync(m) : m, opts);
    rec.load_ms = Date.now() - t0;
    const f = feeds(name, sess);
    if (!f) { rec.note = 'loaded only (no feed defined)'; console.log(JSON.stringify(rec)); continue; }
    const out = await sess.run(f); // warm-up
    rec.out = Object.fromEntries(Object.entries(out).slice(0, 3).map(([k, v]) => [k, v.dims]));
    const times = [], cpus = [];
    for (let i = 0; i < 3; i++) {
      const c0 = process.cpuUsage(); t0 = performance.now();
      await sess.run(f);
      times.push(performance.now() - t0);
      const c = process.cpuUsage(c0); cpus.push((c.user + c.system) / 1000);
    }
    times.sort((a, b) => a - b); cpus.sort((a, b) => a - b);
    rec.run_ms = Math.round(times[1]); rec.cpu_ms = Math.round(cpus[1]);
  } catch (e) {
    rec.error = String(e.message || e).slice(0, 400);
  }
  console.log(JSON.stringify(rec));
}
