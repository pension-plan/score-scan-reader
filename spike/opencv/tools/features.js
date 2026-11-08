// Patch features for the three OpenCV.js fallback approaches.
//   shapeFeatures  (b) Hu moments (from cv.moments; cv.HuMoments is not bound in opencv.js), aspect, size in
//                  staff spaces, staff position, fill, solidity (cv.findContours + cv.convexHull), holes
//                  (RETR_CCOMP inner contours), component count, 4x4 zoning
//   hogFeatures    (c) HOG on a 32x32 normalised patch: gradients by cv.Sobel + cv.cartToPolar, 9-bin cells
//                  and L2-Hys blocks in JS (cv.HOGDescriptor.compute is not bound in opencv.js 4.10)
//   templateScores (a) best TM_CCOEFF_NORMED of each Bravura template, scaled to the patch's staff space
'use strict';

function toMat(cv, img, pad = 0, val = 255) {
  // ink -> 255 (white on black) for contour work
  const m = new cv.Mat(img.h + 2 * pad, img.w + 2 * pad, cv.CV_8U, new cv.Scalar(0));
  const d = m.data, W = img.w + 2 * pad;
  for (let y = 0; y < img.h; y++) for (let x = 0; x < img.w; x++) if (img.data[y * img.w + x]) d[(y + pad) * W + x + pad] = val;
  return m;
}

function shapeFeatures(cv, s) {
  const { img, sp } = s;
  const m = toMat(cv, img, 1);
  const mo = cv.moments(m, true);
  const nu = [mo.nu20, mo.nu11, mo.nu02, mo.nu30, mo.nu21, mo.nu12, mo.nu03];
  const [n20, n11, n02, n30, n21, n12, n03] = nu;
  const hu = [
    n20 + n02,
    (n20 - n02) ** 2 + 4 * n11 ** 2,
    (n30 - 3 * n12) ** 2 + (3 * n21 - n03) ** 2,
    (n30 + n12) ** 2 + (n21 + n03) ** 2,
    (n30 - 3 * n12) * (n30 + n12) * ((n30 + n12) ** 2 - 3 * (n21 + n03) ** 2) + (3 * n21 - n03) * (n21 + n03) * (3 * (n30 + n12) ** 2 - (n21 + n03) ** 2),
    (n20 - n02) * ((n30 + n12) ** 2 - (n21 + n03) ** 2) + 4 * n11 * (n30 + n12) * (n21 + n03),
    (3 * n21 - n03) * (n30 + n12) * ((n30 + n12) ** 2 - 3 * (n21 + n03) ** 2) - (n30 - 3 * n12) * (n21 + n03) * (3 * (n30 + n12) ** 2 - (n21 + n03) ** 2),
  ].map(v => -Math.sign(v) * Math.log10(Math.abs(v) + 1e-30) / 10);
  const contours = new cv.MatVector(), hier = new cv.Mat();
  cv.findContours(m, contours, hier, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE);
  let outer = 0, holes = 0, area = 0, hullA = 0;
  for (let i = 0; i < contours.size(); i++) {
    const c = contours.get(i);
    const parent = hier.data32S[i * 4 + 3];
    if (parent < 0) {
      outer++; area += cv.contourArea(c);
      const h = new cv.Mat(); cv.convexHull(c, h, false, true); hullA += cv.contourArea(h); h.delete();
    } else if (cv.contourArea(c) >= 0.02 * sp * sp) holes++;
    c.delete();
  }
  contours.delete(); hier.delete(); m.delete();
  let ink = 0; for (let i = 0; i < img.data.length; i++) ink += img.data[i];
  const Z = 4, zone = new Array(Z * Z).fill(0), zc = new Array(Z * Z).fill(0);
  for (let y = 0; y < img.h; y++) for (let x = 0; x < img.w; x++) { const k = Math.min(Z - 1, (y * Z / img.h) | 0) * Z + Math.min(Z - 1, (x * Z / img.w) | 0); zone[k] += img.data[y * img.w + x]; zc[k]++; }
  return [img.w / sp, img.h / sp, Math.log(img.w / img.h), s.vtop / 4, s.vbot / 4, ink / (img.w * img.h),
    hullA > 0 ? area / hullA : 1, Math.min(holes, 4) / 2, Math.min(outer, 6) / 3, ...hu, ...zone.map((v, k) => zc[k] ? v / zc[k] : 0)];
}

// aspect-preserving resize into an N x N float image (ink = 1), centred
function normPatch(cv, img, N) {
  const sc = (N - 2) / Math.max(img.w, img.h);
  const w = Math.max(1, Math.round(img.w * sc)), h = Math.max(1, Math.round(img.h * sc));
  const src = toMat(cv, img, 0), dst = new cv.Mat();
  cv.resize(src, dst, new cv.Size(w, h), 0, 0, cv.INTER_AREA);
  const out = new cv.Mat(N, N, cv.CV_32F, new cv.Scalar(0));
  const ox = (N - w) >> 1, oy = (N - h) >> 1;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) out.data32F[(y + oy) * N + x + ox] = dst.data[y * w + x] / 255;
  src.delete(); dst.delete();
  return out;
}

function hogFeatures(cv, s, N = 32, cell = 8, bins = 9) {
  const m = normPatch(cv, s.img, N);
  const gx = new cv.Mat(), gy = new cv.Mat(), mag = new cv.Mat(), ang = new cv.Mat();
  cv.Sobel(m, gx, cv.CV_32F, 1, 0, 1); cv.Sobel(m, gy, cv.CV_32F, 0, 1, 1);
  cv.cartToPolar(gx, gy, mag, ang, false);
  const C = N / cell, H = new Float32Array(C * C * bins);
  const M = mag.data32F, A = ang.data32F;
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    let a = A[y * N + x] % Math.PI; const b = a / Math.PI * bins, b0 = Math.floor(b) % bins, b1 = (b0 + 1) % bins, t = b - Math.floor(b);
    const k = (((y / cell) | 0) * C + ((x / cell) | 0)) * bins;
    H[k + b0] += M[y * N + x] * (1 - t); H[k + b1] += M[y * N + x] * t;
  }
  const f = [];
  for (let by = 0; by + 1 < C; by++) for (let bx = 0; bx + 1 < C; bx++) {
    const blk = [];
    for (const [dy, dx] of [[0, 0], [0, 1], [1, 0], [1, 1]]) for (let i = 0; i < bins; i++) blk.push(H[((by + dy) * C + bx + dx) * bins + i]);
    let n = Math.sqrt(blk.reduce((a, v) => a + v * v, 0) + 1e-6); let v = blk.map(x => Math.min(0.2, x / n));
    n = Math.sqrt(v.reduce((a, x) => a + x * x, 0) + 1e-6); v = v.map(x => x / n);
    f.push(...v);
  }
  [m, gx, gy, mag, ang].forEach(x => x.delete());
  const { img, sp } = s;
  return [...f, img.w / sp, img.h / sp, s.vtop / 4, s.vbot / 4];
}

// ---- (a) templates
const TPL_CLASS = {
  'rest-breve': ['rest-breve'], 'rest-whole': ['rest-whole'], 'rest-half': ['rest-half'], 'rest-quarter': ['rest-quarter'], 'rest-8th': ['rest-8th'],
  'rest-16th': ['rest-16th'], 'rest-32nd': ['rest-32nd'], 'rest-64th': ['rest-64th'],
  'acc-sharp': ['acc-sharp'], 'acc-flat': ['acc-flat'], 'acc-natural': ['acc-natural'], 'acc-double-sharp': ['acc-double-sharp'], 'acc-double-flat': ['acc-double-flat'],
  'clef-G': ['clef-G'], 'clef-F': ['clef-F'], 'clef-C': ['clef-C'],
  'digit-0': ['digit-0'], 'digit-1': ['digit-1'], 'digit-2': ['digit-2'], 'digit-3': ['digit-3'], 'digit-4': ['digit-4'], 'digit-5': ['digit-5'], 'digit-6': ['digit-6'], 'digit-7': ['digit-7'], 'digit-8': ['digit-8'], 'digit-9': ['digit-9'],
  'time-C': ['time-C'], 'time-cut': ['time-cut'], fermata: ['fermata-up', 'fermata-down'], dyn: ['dyn-p', 'dyn-m', 'dyn-f', 'dyn-s', 'dyn-z'], dot: ['dot'],
  'neg-head': ['head-filled', 'head-half', 'head-whole'],
};

function loadTemplates(cv, json) {
  const T = {};
  for (const [name, g] of Object.entries(json.glyphs)) {
    const b = Buffer.from(g.data, 'base64');
    const m = new cv.Mat(g.h, g.w, cv.CV_8U);
    for (let i = 0; i < b.length; i++) m.data[i] = b[i] >= 128 ? 255 : 0;
    T[name] = { m, w: g.w, h: g.h };
  }
  return { T, sp: json.sp, cache: new Map() };
}

function scaledTpl(cv, bank, name, k) {
  const key = name + '@' + k.toFixed(2);
  let t = bank.cache.get(key);
  if (!t) {
    const g = bank.T[name], w = Math.max(3, Math.round(g.w * k)), h = Math.max(3, Math.round(g.h * k));
    t = new cv.Mat(); cv.resize(g.m, t, new cv.Size(w, h), 0, 0, cv.INTER_AREA);
    cv.threshold(t, t, 127, 255, cv.THRESH_BINARY);
    bank.cache.set(key, t);
  }
  return t;
}

// best NCC per class for a patch, scales k * {0.85, 1, 1.15}; the patch is padded so the template may shift
function templateScores(cv, bank, s, scales = [0.85, 1, 1.15]) {
  const { img, sp } = s;
  const out = {};
  const k0 = sp / bank.sp;
  let maxT = 0;
  for (const names of Object.values(TPL_CLASS)) for (const n of names) maxT = Math.max(maxT, bank.T[n].w, bank.T[n].h);
  const res = new cv.Mat();
  const padded = new Map();
  for (const [cls, names] of Object.entries(TPL_CLASS)) {
    let best = -1;
    for (const n of names) for (const f of scales) {
      const t = scaledTpl(cv, bank, n, k0 * f);
      // template far larger / smaller than the glyph cannot be it
      if (t.cols > 2.2 * img.w + 4 || t.rows > 2.2 * img.h + 4 || t.cols * 3 < img.w || t.rows * 3 < img.h) continue;
      const pad = Math.max(t.cols, t.rows) >> 1;
      let pm = padded.get(pad); if (!pm) { pm = toMat(cv, img, pad); padded.set(pad, pm); }
      if (t.cols > pm.cols || t.rows > pm.rows) continue;
      cv.matchTemplate(pm, t, res, cv.TM_CCOEFF_NORMED);
      const mm = cv.minMaxLoc(res);
      // penalise ink of the patch the template leaves uncovered: NCC over the template window alone
      // would let a small template match inside a big glyph
      const cover = Math.min(1, (t.cols * t.rows) / (img.w * img.h));
      const sc = mm.maxVal * Math.sqrt(cover);
      if (sc > best) best = sc;
    }
    out[cls] = best;
  }
  res.delete(); for (const m of padded.values()) m.delete();
  return out;
}

module.exports = { shapeFeatures, hogFeatures, templateScores, loadTemplates, TPL_CLASS, normPatch, toMat };
