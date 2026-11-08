'use strict';
// PaddleOCR PP-OCRv5 mobile rec (ONNX, CTC) evaluation on oracle lyric strips.
//   node src/paddle_eval.js '<json config>' SHARD NSHARDS OUT.jsonl
// config: {model: latin_v5|en_v5, prep: raw|norm|clean, target: 40, height: 48, threads: 1}
const fs = require('fs'), path = require('path');
const ort = require('onnxruntime-node');
const { listJobs, oracleCrop, loadPage } = require('./jobs');
const IMG = require('./img');
const cfg = JSON.parse(process.argv[2]);
const shard = +process.argv[3], nshard = +process.argv[4], out = process.argv[5];
const MD = path.join(__dirname, '..', 'models', 'paddle', cfg.model);

function ctcDecode(probs, T, C, chars) {
  // greedy; returns text and per-char frame index
  let prev = -1; const res = []; const confs = [];
  for (let t = 0; t < T; t++) {
    let best = 0, bv = -1;
    const o = t * C;
    for (let c = 0; c < C; c++) { const v = probs[o + c]; if (v > bv) { bv = v; best = c; } }
    if (best !== prev && best !== 0) { res.push({ ch: chars[best], t }); confs.push(bv); }
    prev = best;
  }
  return { text: res.map(r => r.ch).join(''), pos: res, conf: confs.length ? confs.reduce((a, b) => a + b, 0) / confs.length : 0 };
}

(async () => {
  const dict = JSON.parse(fs.readFileSync(path.join(MD, 'dict.json'), 'utf8'));
  const chars = ['<blank>', ...dict, ' '];
  const sess = await ort.InferenceSession.create(path.join(MD, 'inference.onnx'), { intraOpNumThreads: cfg.threads || 1, interOpNumThreads: 1, logSeverityLevel: 3, graphOptimizationLevel: 'all' });
  const H = cfg.height || 48;
  const jobs = listJobs(cfg.variants).filter((_, i) => i % nshard === shard);
  const fd = fs.openSync(out, 'w');
  for (const j of jobs) {
    const page = loadPage(j.png);
    const c = oracleCrop(page, j.line, cfg.prep || 'norm', cfg.target || 40);
    // resize to fixed height, keep aspect
    const s = H / c.height;
    const r = IMG.resize(c, s);
    const W = Math.max(16, Math.ceil(r.width / 8) * 8);
    const x = new Float32Array(3 * H * W).fill(1.0);   // pad right with white (normalised +1)
    for (let y = 0; y < H; y++) for (let xx = 0; xx < r.width; xx++) {
      const v = (r.data[y * r.width + xx] / 255 - 0.5) / 0.5;
      x[y * W + xx] = v; x[H * W + y * W + xx] = v; x[2 * H * W + y * W + xx] = v;
    }
    const t0 = process.hrtime.bigint();
    const o = await sess.run({ x: new ort.Tensor('float32', x, [1, 3, H, W]) });
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    const out0 = o[sess.outputNames[0]]; const [, T, C] = out0.dims;
    const d = ctcDecode(out0.data, T, C, chars);
    const fx = (W / T) / s / c.scale;   // frame -> original crop px
    fs.writeSync(fd, JSON.stringify({ key: j.key, lang: j.lang, ocr: d.text.trim(), conf: Math.round(d.conf * 100), ms: Math.round(ms), w: W, h: H,
      pos: d.pos.map(p => [p.ch, Math.round(p.t * fx)]) }) + '\n');
  }
  fs.closeSync(fd);
})().catch(e => { console.error(e); process.exit(1); });
