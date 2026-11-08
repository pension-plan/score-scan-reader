'use strict';
// Binarization: background normalisation + Otsu (default), Sauvola (alternative),
// with automatic noise estimation and light pre-smoothing for noisy scans.
const { makeGray, makeBinary } = require('./image');

function otsuFromHist(hist, total) {
  let sum = 0;
  for (let i = 0; i < 256; i++) sum += i * hist[i];
  let sumB = 0, wB = 0, best = 0, thr = 127;
  for (let t = 0; t < 256; t++) {
    wB += hist[t];
    if (!wB) continue;
    const wF = total - wB;
    if (!wF) break;
    sumB += t * hist[t];
    const mB = sumB / wB, mF = (sum - sumB) / wF;
    const between = wB * wF * (mB - mF) * (mB - mF);
    if (between > best) { best = between; thr = t; }
  }
  return thr;
}

function histogram(gray) {
  const h = new Float64Array(256);
  for (let i = 0; i < gray.data.length; i++) h[gray.data[i]]++;
  return h;
}

function threshold(gray, t) {
  const b = makeBinary(gray.width, gray.height);
  for (let i = 0; i < gray.data.length; i++) b.data[i] = gray.data[i] <= t ? 1 : 0;
  return b;
}

// Estimate the paper level per block (high percentile), smooth, interpolate,
// and divide it out.  Removes vignetting / lamp gradients / yellowed paper.
function backgroundNormalize(gray, block) {
  const { width: w, height: h, data } = gray;
  block = block || Math.max(16, Math.round(Math.min(w, h) / 48));
  const bw = Math.ceil(w / block), bh = Math.ceil(h / block);
  const bg = new Float64Array(bw * bh);
  const hist = new Uint32Array(256);
  for (let by = 0; by < bh; by++) {
    for (let bx = 0; bx < bw; bx++) {
      hist.fill(0);
      let n = 0;
      const y1 = Math.min(h, (by + 1) * block), x1 = Math.min(w, (bx + 1) * block);
      for (let y = by * block; y < y1; y += 2) for (let x = bx * block; x < x1; x += 2) { hist[data[y * w + x]]++; n++; }
      // 90th percentile = paper (ink rarely covers > 10% of a block... handled below)
      let acc = 0, p = 255; const target = n * 0.9;
      for (let v = 0; v < 256; v++) { acc += hist[v]; if (acc >= target) { p = v; break; } }
      bg[by * bw + bx] = p;
    }
  }
  // robustify: replace blocks much darker than their neighbourhood max (ink-heavy blocks)
  const bg2 = new Float64Array(bw * bh);
  for (let by = 0; by < bh; by++) for (let bx = 0; bx < bw; bx++) {
    let mx = 0, s = 0, n = 0;
    for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) {
      const yy = by + dy, xx = bx + dx;
      if (yy < 0 || xx < 0 || yy >= bh || xx >= bw) continue;
      const v = bg[yy * bw + xx]; if (v > mx) mx = v;
    }
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const yy = by + dy, xx = bx + dx;
      if (yy < 0 || xx < 0 || yy >= bh || xx >= bw) continue;
      const v = Math.max(bg[yy * bw + xx], mx * 0.85); s += v; n++;
    }
    bg2[by * bw + bx] = s / n;
  }
  const out = makeGray(w, h, 0);
  for (let y = 0; y < h; y++) {
    const fy = Math.min(bh - 1, Math.max(0, (y + 0.5) / block - 0.5));
    const y0 = Math.floor(fy), y1 = Math.min(bh - 1, y0 + 1), ty = fy - y0;
    for (let x = 0; x < w; x++) {
      const fx = Math.min(bw - 1, Math.max(0, (x + 0.5) / block - 0.5));
      const x0 = Math.floor(fx), x1 = Math.min(bw - 1, x0 + 1), tx = fx - x0;
      const b = (bg2[y0 * bw + x0] * (1 - tx) + bg2[y0 * bw + x1] * tx) * (1 - ty) +
                (bg2[y1 * bw + x0] * (1 - tx) + bg2[y1 * bw + x1] * tx) * ty;
      out.data[y * w + x] = Math.min(255, (255 * data[y * w + x]) / Math.max(1, b));
    }
  }
  return out;
}

// Noise sigma estimated from the paper: MAD of horizontal pixel differences in bright areas.
function estimateNoise(gray) {
  const { width: w, height: h, data } = gray;
  const diffs = [];
  for (let y = 1; y < h; y += 7) {
    for (let x = 1; x < w; x += 3) {
      const i = y * w + x;
      if (data[i] > 150 && data[i - 1] > 150) diffs.push(Math.abs(data[i] - data[i - 1]));
    }
  }
  if (!diffs.length) return 0;
  diffs.sort((a, b) => a - b);
  return (diffs[diffs.length >> 1] * 1.4826) / Math.SQRT2;
}

function boxBlur(gray, r) {
  const { width: w, height: h, data } = gray;
  const tmp = new Float32Array(w * h);
  const out = makeGray(w, h, 0);
  const n = 2 * r + 1;
  for (let y = 0; y < h; y++) {
    let s = 0;
    for (let x = -r; x <= r; x++) s += data[y * w + Math.min(w - 1, Math.max(0, x))];
    for (let x = 0; x < w; x++) {
      tmp[y * w + x] = s / n;
      s += data[y * w + Math.min(w - 1, x + r + 1)] - data[y * w + Math.max(0, x - r)];
    }
  }
  for (let x = 0; x < w; x++) {
    let s = 0;
    for (let y = -r; y <= r; y++) s += tmp[Math.min(h - 1, Math.max(0, y)) * w + x];
    for (let y = 0; y < h; y++) {
      out.data[y * w + x] = s / n;
      s += tmp[Math.min(h - 1, y + r + 1) * w + x] - tmp[Math.max(0, y - r) * w + x];
    }
  }
  return out;
}

// 3x3 median (salt & pepper)
function median3(gray) {
  const { width: w, height: h, data } = gray;
  const out = makeGray(w, h, 255);
  const v = new Uint8Array(9);
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    let k = 0;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) v[k++] = data[(y + dy) * w + x + dx];
    v.sort();
    out.data[y * w + x] = v[4];
  }
  return out;
}

function sauvola(gray, win, k = 0.25, R = 128) {
  const { width: w, height: h, data } = gray;
  const W1 = w + 1;
  const S = new Float64Array(W1 * (h + 1)), S2 = new Float64Array(W1 * (h + 1));
  for (let y = 0; y < h; y++) {
    let rs = 0, rs2 = 0;
    for (let x = 0; x < w; x++) {
      const v = data[y * w + x]; rs += v; rs2 += v * v;
      S[(y + 1) * W1 + x + 1] = S[y * W1 + x + 1] + rs;
      S2[(y + 1) * W1 + x + 1] = S2[y * W1 + x + 1] + rs2;
    }
  }
  const r = win >> 1;
  const b = makeBinary(w, h);
  for (let y = 0; y < h; y++) {
    const y0 = Math.max(0, y - r), y1 = Math.min(h, y + r + 1);
    for (let x = 0; x < w; x++) {
      const x0 = Math.max(0, x - r), x1 = Math.min(w, x + r + 1);
      const n = (y1 - y0) * (x1 - x0);
      const s = S[y1 * W1 + x1] - S[y0 * W1 + x1] - S[y1 * W1 + x0] + S[y0 * W1 + x0];
      const s2 = S2[y1 * W1 + x1] - S2[y0 * W1 + x1] - S2[y1 * W1 + x0] + S2[y0 * W1 + x0];
      const m = s / n, sd = Math.sqrt(Math.max(0, s2 / n - m * m));
      const t = m * (1 + k * (sd / R - 1));
      b.data[y * w + x] = data[y * w + x] <= t ? 1 : 0;
    }
  }
  return b;
}

// Main entry.  Returns { binary, gray (normalised, possibly smoothed), info }.
function binarize(gray, opts = {}) {
  const method = opts.method || 'bgotsu';
  const info = { method };
  let g = gray;
  const noise = estimateNoise(g);
  info.noise = noise;
  if (opts.denoise !== false) {
    if (noise > 30) { g = median3(g); g = boxBlur(g, 1); info.denoise = 'median3+box1'; }
    else if (noise > 12) { g = median3(g); info.denoise = 'median3'; }
  }
  if (method === 'otsu') {
    const t = otsuFromHist(histogram(g), g.data.length);
    info.threshold = t;
    return { binary: threshold(g, t), gray: g, info };
  }
  if (method === 'sauvola') {
    const win = opts.window || Math.max(15, Math.round(Math.min(g.width, g.height) / 60) | 1);
    info.window = win;
    return { binary: sauvola(g, win, opts.k ?? 0.25), gray: g, info };
  }
  // bgotsu
  const n = backgroundNormalize(g, opts.block);
  const t = otsuFromHist(histogram(n), n.data.length);
  // Otsu on a page that is >90% paper sits a bit high; bias slightly towards paper
  info.threshold = t;
  return { binary: threshold(n, t), gray: n, info };
}

module.exports = { binarize, backgroundNormalize, otsuFromHist, histogram, threshold, sauvola, estimateNoise, boxBlur, median3 };
