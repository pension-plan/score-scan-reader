// Inference worker: loads onnxruntime-web 1.30.0 from jsDelivr and the two copista-2m graphs,
// then runs copista_core.detect() on grayscale pages posted from the page.
import * as ort from 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/ort.wasm.bundle.min.mjs';
import { detect } from './copista_core.mjs';

const ORT_WASM = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/ort-wasm-simd-threaded.wasm';
const MODELS = new URL('../models/', import.meta.url);

ort.env.wasm.numThreads = 1;
ort.env.wasm.wasmPaths = { wasm: ORT_WASM };

let ready = null;
function load() {
  ready ??= (async () => {
    const t0 = performance.now();
    const get = async (name) => {
      const r = await fetch(new URL(name, MODELS));
      if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
      return name.endsWith('.json') ? r.json() : new Uint8Array(await r.arrayBuffer());
    };
    const [dense, rel, meta] = await Promise.all([
      get('copista2m-dense.int8w.onnx'), get('copista2m-rel.int8w.onnx'), get('copista2m-classes.json')]);
    const opt = { executionProviders: ['wasm'] };
    const sessions = { dense: await ort.InferenceSession.create(dense, opt), rel: await ort.InferenceSession.create(rel, opt) };
    return { sessions, meta, load_ms: Math.round(performance.now() - t0) };
  })();
  return ready;
}

self.onmessage = async (e) => {
  const { id, img } = e.data;
  try {
    self.postMessage({ id, progress: 'Loading the model (2.1 MB)' });
    const m = await load();
    self.postMessage({ id, progress: 'Detecting symbols' });
    const t0 = performance.now();
    const r = await detect(ort, m.sessions, m.meta, img);
    const total_ms = Math.round(performance.now() - t0);
    self.postMessage({ id, result: { dets: r.dets, timing: { ...r.timing, total_ms, load_ms: m.load_ms } } });
  } catch (err) {
    self.postMessage({ id, error: String((err && (err.message || err)) || 'unknown error') });
  }
};
