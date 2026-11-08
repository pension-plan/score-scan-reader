'use strict';
// OCR engine adapters with a common interface: recognize(img) -> {text, conf, tokens:[{t,x0,x1}] (img px)}
const path = require('path'), fs = require('fs');
const IMG = require('./img');
const MODELS = path.join(__dirname, '..', 'models');

async function tess(cfg, langs) {
  const { createWorker } = require('tesseract.js');
  const w = await createWorker(langs, 1, { langPath: path.join(MODELS, 'tessdata', cfg.model), gzip: cfg.model === 'best_int', cacheMethod: 'none' });
  await w.setParameters({ tessedit_pageseg_mode: String(cfg.psm || 7), user_defined_dpi: '300' });
  return {
    async recognize(img) {
      const { data } = await w.recognize(IMG.toPNG(img), {}, { text: true, blocks: true });
      const tokens = [];
      for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const wd of l.words) tokens.push({ t: wd.text, x0: wd.bbox.x0, x1: wd.bbox.x1, c: wd.confidence });
      return { text: data.text.replace(/\n+/g, ' ').trim(), conf: data.confidence, tokens };
    },
    terminate: () => w.terminate(),
  };
}

async function paddle(cfg) {
  const ort = require('onnxruntime-node');
  const MD = path.join(MODELS, 'paddle', cfg.model);
  const dict = JSON.parse(fs.readFileSync(path.join(MD, 'dict.json'), 'utf8'));
  const chars = ['<blank>', ...dict, ' '];
  const sess = await ort.InferenceSession.create(path.join(MD, 'inference.onnx'), { intraOpNumThreads: cfg.threads || 1, interOpNumThreads: 1, logSeverityLevel: 3, graphOptimizationLevel: 'all' });
  const H = cfg.height || 48;
  return {
    async recognize(img) {
      const s = H / img.height; const r = IMG.resize(img, s);
      const W = Math.max(16, Math.ceil(r.width / 8) * 8);
      const x = new Float32Array(3 * H * W).fill(1.0);
      for (let y = 0; y < H; y++) for (let xx = 0; xx < r.width; xx++) { const v = (r.data[y * r.width + xx] / 255 - 0.5) / 0.5; x[y * W + xx] = v; x[H * W + y * W + xx] = v; x[2 * H * W + y * W + xx] = v; }
      const o = await sess.run({ x: new ort.Tensor('float32', x, [1, 3, H, W]) });
      const out = o[sess.outputNames[0]]; const [, T, C] = out.dims; const P = out.data;
      let prev = -1; const seq = []; let csum = 0;
      for (let t = 0; t < T; t++) { let best = 0, bv = -1; const off = t * C; for (let c = 0; c < C; c++) if (P[off + c] > bv) { bv = P[off + c]; best = c; } if (best !== prev && best !== 0) { seq.push({ ch: chars[best], x: (t + 0.5) * (W / T) / s }); csum += bv; } prev = best; }
      const text = seq.map(q => q.ch).join('').replace(/\s+/g, ' ').trim();
      const tokens = []; let cur = null; const half = 0.25 * img.height;
      for (const q of seq) { if (q.ch === ' ') { if (cur) tokens.push(cur); cur = null; continue; } if (!cur) cur = { t: '', x0: q.x - half, x1: q.x + half }; cur.t += q.ch; cur.x1 = q.x + half; }
      if (cur) tokens.push(cur);
      return { text, conf: seq.length ? 100 * csum / seq.length : 0, tokens };
    },
    terminate: async () => {},
  };
}
async function none() { return { recognize: async () => ({ text: '', conf: 0, tokens: [] }), terminate: async () => {} }; }
module.exports = { tess, paddle, none };
