'use strict';
// copista-2m symbol detector: the page-level pipeline (resample, dense CNN,
// peak picking, relational verifier, decode) and the browser worker that runs
// it with onnxruntime-web.  Environment agnostic: node (onnxruntime-node,
// see ml.js) and the browser worker use the same copistaCore() code.
//
// Model: copista-2m by KobiMusic, Apache-2.0
//   https://huggingface.co/kobimusic/copista-2m (sha c37d89e1e52edc95c1a73bda0aea5f2f71a9c763)
//   converted to ONNX (two graphs, int8 weight storage); see assets-src/ml/PROVENANCE.md
//   and the LICENSE / NOTICE files shipped next to the model in assets/.
// Runtime: onnxruntime-web 1.30.0 (MIT), ESM bundle from a pinned CDN URL,
// imported dynamically inside a blob: module worker (a static import fails
// there), single thread, wasm bytes fetched by the page from assets/ and
// handed over as env.wasm.wasmBinary (no same-origin .mjs import needed).

const ORT_VERSION = '1.30.0';
const ORT_URLS = [
  `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/ort.wasm.bundle.min.mjs`,
  `https://cdnjs.cloudflare.com/ajax/libs/onnxruntime-web/${ORT_VERSION}/ort.wasm.bundle.min.mjs`,
];
const MODEL_FILES = { dense: 'copista2m-dense.int8w.onnx', rel: 'copista2m-rel.int8w.onnx', meta: 'copista2m-classes.json', wasm: 'ort-wasm-simd-threaded.wasm' };

// Self-contained (its source text is the worker's core): no outer references.
function copistaCore() {
  const TARGET_SP = 10.6;

  // vertical run-length staff space: most common ink run (line) + gap run
  function staffSpace(img) {
    const { width: w, height: h, data } = img;
    const step = Math.max(1, Math.floor(w / 400));
    const bl = new Int32Array(64), wh = new Int32Array(256);
    for (let x = 0; x < w; x += step) {
      let run = 0, inInk = false, lastEnd = -1;
      for (let y = 0; y <= h; y++) {
        const ink = y < h && data[y * w + x] < 128;
        if (ink) {
          if (!inInk) { if (lastEnd >= 0) wh[Math.min(255, y - lastEnd)]++; inInk = true; run = 0; }
          run++;
        } else if (inInk) { inInk = false; bl[Math.min(63, run)]++; lastEnd = y; }
      }
    }
    let line = 1, gap = 2;
    for (let i = 1; i < 64; i++) if (bl[i] > bl[line]) line = i;
    for (let i = 2; i < 256; i++) if (wh[i] > wh[gap]) gap = i;
    return { sp: line + gap, line, gap };
  }

  function imgszFor(sp, longSide) {
    return Math.trunc(Math.min(4096, Math.max(640, Math.round(longSide * TARGET_SP / sp / 32) * 32)));
  }

  // area-average resample to the model scale, padded to /32 with white (1.0)
  function prepare(img, imgsz) {
    const { width: W0, height: H0, data } = img;
    const s = imgsz / Math.max(W0, H0);
    const w2 = Math.max(32, Math.round(W0 * s)), h2 = Math.max(32, Math.round(H0 * s));
    const H = Math.ceil(h2 / 32) * 32, W = Math.ceil(w2 / 32) * 32;
    const out = new Float32Array(H * W).fill(1);
    const fx = W0 / w2, fy = H0 / h2;
    const tmp = new Float32Array(H0 * w2);
    for (let x = 0; x < w2; x++) {
      const a = x * fx, b = a + fx, i0 = Math.floor(a), i1 = Math.min(W0, Math.ceil(b));
      for (let y = 0; y < H0; y++) {
        let acc = 0;
        const row = y * W0;
        for (let i = i0; i < i1; i++) acc += (Math.min(b, i + 1) - Math.max(a, i)) * data[row + i];
        tmp[y * w2 + x] = acc / fx;
      }
    }
    for (let y = 0; y < h2; y++) {
      const a = y * fy, b = a + fy, j0 = Math.floor(a), j1 = Math.min(H0, Math.ceil(b));
      for (let x = 0; x < w2; x++) {
        let acc = 0;
        for (let j = j0; j < j1; j++) acc += (Math.min(b, j + 1) - Math.max(a, j)) * tmp[j * w2 + x];
        out[y * W + x] = acc / fy / 255;
      }
    }
    return { x: out, H, W, s, w2, h2 };
  }

  // 3x3 local maxima of sigmoid(obj) above thresh, top K by score
  function peaks(obj, h, w, K, thresh) {
    const n = h * w, p = new Float32Array(n);
    for (let i = 0; i < n; i++) p[i] = 1 / (1 + Math.exp(-obj[i]));
    const cand = [];
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const v = p[y * w + x];
      if (v <= thresh) continue;
      let isMax = true;
      for (let dy = -1; dy <= 1 && isMax; dy++) for (let dx = -1; dx <= 1; dx++) {
        const yy = y + dy, xx = x + dx;
        if (yy < 0 || yy >= h || xx < 0 || xx >= w) continue;
        if (p[yy * w + xx] > v) { isMax = false; break; }
      }
      if (isMax) cand.push([v, y, x]);
    }
    cand.sort((a, b) => b[0] - a[0]);
    return cand.slice(0, K);
  }

  function nmsPerClass(boxes, scores, cls, iou) {
    const order = scores.map((s, i) => i).sort((a, b) => scores[b] - scores[a]);
    const keep = [], dead = new Uint8Array(scores.length);
    for (let oi = 0; oi < order.length; oi++) {
      const i = order[oi];
      if (dead[i]) continue;
      keep.push(i);
      const [ax0, ay0, ax1, ay1] = boxes[i], aa = (ax1 - ax0) * (ay1 - ay0);
      for (let oj = oi + 1; oj < order.length; oj++) {
        const j = order[oj];
        if (dead[j] || cls[j] !== cls[i]) continue;
        const [bx0, by0, bx1, by1] = boxes[j];
        const iw = Math.min(ax1, bx1) - Math.max(ax0, bx0), ih = Math.min(ay1, by1) - Math.max(ay0, by0);
        if (iw <= 0 || ih <= 0) continue;
        const inter = iw * ih, o = inter / (aa + (bx1 - bx0) * (by1 - by0) - inter + 1e-9);
        if (o > iou) dead[j] = 1;
      }
    }
    return keep;
  }

  // one page -> {dets: [{cls, conf, xyxy (page px), attrs?}], timing}
  // sessions {dense, rel}: InferenceSession; meta: copista2m-classes.json
  async function detect(ort, sessions, meta, img, opts) {
    opts = opts || {};
    const conf = opts.conf != null ? opts.conf : 0.05;
    const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
    const t = {};
    let t0 = now();
    const sp = opts.sp || staffSpace(img).sp;
    const imgsz = imgszFor(sp, Math.max(img.width, img.height));
    const P = prepare(img, imgsz);
    t.prep_ms = now() - t0;
    t0 = now();
    const o = await sessions.dense.run({ x: new ort.Tensor('float32', P.x, [1, 1, P.H, P.W]) });
    t.dense_ms = now() - t0;
    const h = o.obj.dims[2], w = o.obj.dims[3];
    const pk = peaks(o.obj.data, h, w, meta.k_infer, conf * 0.5);
    const n = pk.length;
    if (!n) return { dets: [], timing: Object.assign(t, { imgsz, sp, n_cand: 0 }) };
    const cy = new BigInt64Array(n), cx = new BigInt64Array(n);
    pk.forEach((q, i) => { cy[i] = BigInt(q[1]); cx[i] = BigInt(q[2]); });
    t0 = now();
    const r = await sessions.rel.run({ f: o.f, reg: o.reg, cy: new ort.Tensor('int64', cy, [1, n]), cx: new ort.Tensor('int64', cx, [1, n]) });
    t.rel_ms = now() - t0;
    t0 = now();
    const C = meta.classes.length + 1, NA = r.attr.dims[2];
    const cl = r.cls.data, ref = r.ref.data, at = r.attr.data, rr = r.r.data;
    const boxes = [], scores = [], cls = [], idx = [];
    for (let i = 0; i < n; i++) {
      let mx = -Infinity;
      for (let c = 0; c < C; c++) mx = Math.max(mx, cl[i * C + c]);
      let sum = 0, best = 0, bc = 0;
      for (let c = 0; c < C; c++) {
        const e = Math.exp(cl[i * C + c] - mx); sum += e;
        if (c < C - 1 && e > best) { best = e; bc = c; }
      }
      const score = pk[i][0] * (best / sum);
      if (score <= conf) continue;
      const r0 = rr[i * 4] + ref[i * 4 + 2], r1 = rr[i * 4 + 1] + ref[i * 4 + 3];
      const r2 = rr[i * 4 + 2] + ref[i * 4], r3 = rr[i * 4 + 3] + ref[i * 4 + 1];
      const bw = Math.exp(r0) * meta.stride, bh = Math.exp(r1) * meta.stride;
      const xc = (pk[i][2] + r2) * meta.stride, yc = (pk[i][1] + r3) * meta.stride;
      boxes.push([xc - bw / 2, yc - bh / 2, xc + bw / 2, yc + bh / 2]);
      scores.push(score); cls.push(bc); idx.push(i);
    }
    const keep = nmsPerClass(boxes, scores, cls, 0.7);
    const prefixes = new Set(meta.attr_class_prefixes);
    const dets = keep.map((k) => {
      const name = meta.classes[cls[k]];
      const rec = { cls: name, conf: Math.round(scores[k] * 1000) / 1000, xyxy: boxes[k].map((v) => Math.round((v / P.s) * 10) / 10) };
      if (prefixes.has(name.split('_')[0])) {
        rec.attrs = {};
        const i = idx[k];
        for (const a of Object.keys(meta.attr_vocab)) {
          const off = meta.attr_offsets[a], sz = meta.attr_sizes[a];
          let bi = 0;
          for (let j = 1; j < sz; j++) if (at[i * NA + off + j] > at[i * NA + off + bi]) bi = j;
          rec.attrs[a] = meta.attr_vocab[a][bi];
        }
      }
      return rec;
    });
    t.post_ms = now() - t0;
    for (const k of Object.keys(t)) t[k] = Math.round(t[k] * 10) / 10;
    return { dets, timing: Object.assign(t, { imgsz, sp, n_cand: n, input: [1, 1, P.H, P.W] }) };
  }

  return { TARGET_SP, staffSpace, imgszFor, prepare, peaks, detect };
}

// Body of the browser worker (its source text runs in a blob: module worker).
// In:  {t:'init', wasm: ArrayBuffer, dense: ArrayBuffer, rel: ArrayBuffer, meta}
//      {t:'detect', id, img: {width, height, data}}
// Out: {t:'ready', ms} | {t:'dets', id, dets, timing} | {t:'error', id?, msg}
function mlWorkerMain(scope, core, ortP) {
  let ready = null;
  const post = (m) => scope.postMessage(m);
  scope.onmessage = async (ev) => {
    const m = ev.data || {};
    if (m.t === 'init') {
      ready = (async () => {
        const t0 = performance.now();
        const ort = await ortP;
        ort.env.wasm.numThreads = 1;
        ort.env.wasm.wasmBinary = m.wasm;
        const opt = { executionProviders: ['wasm'] };
        const sessions = { dense: await ort.InferenceSession.create(new Uint8Array(m.dense), opt), rel: await ort.InferenceSession.create(new Uint8Array(m.rel), opt) };
        return { ort, sessions, meta: m.meta, ms: Math.round(performance.now() - t0) };
      })();
      try { const r = await ready; post({ t: 'ready', ms: r.ms }); } catch (e) { post({ t: 'error', msg: String((e && e.message) || e) }); }
    } else if (m.t === 'detect') {
      try {
        if (!ready) throw new Error('detector not initialised');
        const r = await ready;
        const out = await core.detect(r.ort, r.sessions, r.meta, m.img, m.opts || {});
        post({ t: 'dets', id: m.id, dets: out.dets, timing: out.timing });
      } catch (e) { post({ t: 'error', id: m.id, msg: String((e && e.message) || e) }); }
    }
  };
}

// Source text of the module worker.  The ORT bundle is imported dynamically
// (a static import from a CDN fails inside a blob: module worker); the first
// URL that loads wins.
function workerSource(urls) {
  urls = urls || ORT_URLS;
  return `const core = (${copistaCore.toString()})();\n` +
    `const ortP = (async () => { let err; for (const u of ${JSON.stringify(urls)}) { try { return await import(u); } catch (e) { err = e; } } throw err || new Error('onnxruntime-web did not load'); })();\n` +
    `ortP.catch(() => {});\n` +
    `(${mlWorkerMain.toString()})(self, core, ortP);\n`;
}

module.exports = { copistaCore, mlWorkerMain, workerSource, ORT_VERSION, ORT_URLS, MODEL_FILES };
