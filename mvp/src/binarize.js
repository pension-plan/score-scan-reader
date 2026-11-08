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
function backgroundNormalize(gray, block, bgOut) {
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
      if (bgOut) bgOut[y * w + x] = b;
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
    // a 3x3 median erases 1-px staff lines (and halftone screens read as
    // noise turn into texture under it); a box blur keeps thin lines
    // connected
    if (noise > 30) { g = boxBlur(g, 2); info.denoise = 'box2'; }
    else if (noise > 12) { g = boxBlur(g, 1); info.denoise = 'box1'; }
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
  const bgMap = new Uint8Array(g.data.length);
  const n = backgroundNormalize(g, opts.block, bgMap);
  const t = otsuFromHist(histogram(n), n.data.length);
  info.threshold = t;
  // absolute contrast guard: ink lies at least max(12, 2.5 sigma) grey levels
  // below its local paper level.  Otsu splits even a blank or noise-only page
  // in two, and dividing out a dark corner (vignetting, book gutter) blows its
  // noise up to ink-like values; neither passes this test.
  const sig = info.denoise === 'box2' ? noise / 5 : info.denoise === 'box1' ? noise / 3 : noise;
  const minC = opts.minContrast ?? Math.max(12, 2.5 * sig);
  info.minContrast = minC;
  const b = makeBinary(g.width, g.height), nd = n.data, bd = b.data;
  for (let i = 0; i < nd.length; i++) bd[i] = nd[i] <= t && bgMap[i] * (255 - nd[i]) >= 255 * minC ? 1 : 0;
  return { binary: b, gray: n, info };
}

// Remove 8-connected ink components of at most maxArea pixels (speckle).
function despeckle(bin, maxArea) {
  const { labelComponents } = require('./cc');
  const { labels, comps } = labelComponents(bin);
  const kill = new Uint8Array(comps.length + 1);
  for (const c of comps) if (c.id && c.area <= maxArea) kill[c.id] = 1;
  const out = makeBinary(bin.width, bin.height);
  for (let i = 0; i < bin.data.length; i++) out.data[i] = bin.data[i] && !kill[labels[i]] ? 1 : 0;
  return out;
}

// Dark scanner borders, paper edges and edge shadows binarize to bands of
// ink along the page edges; staves walk on into them and they join every
// staff to the next.  In the outer 12% of the width, a group of adjacent
// columns holding vertical ink runs of a third of the page height or more
// (gaps of a few px bridged), at least 6 px wide, with no staff lines running
// off its inner side (a system's opening line and bracket have them) is
// cleared, with the columns next to it that still hold runs of a tenth.
function clearEdgeBands(bin, opts = {}) {
  const { width: w, height: h, data } = bin;
  const zone = Math.round(0.12 * w);
  // vertical ink runs of column x at least min long (gaps of <= 3 px bridged)
  const longest = (x, min) => {
    const runs = [];
    for (let y = 0; y < h;) {
      if (!data[y * w + x]) { y++; continue; }
      let y1 = y + 1, last = y;
      while (y1 < h && y1 - last <= 4) { if (data[y1 * w + x]) last = y1; y1++; }
      if (last + 1 - y >= min) runs.push([y, last + 1]);
      y = last + 1;
    }
    return runs;
  };
  const isLong = new Uint8Array(w);
  for (let x = 0; x < w; x++) if ((x < zone || x >= w - zone) && longest(x, Math.round(h / 3)).length) isLong[x] = 1;
  const groups = [];
  for (let x = 0; x < w; x++) {
    if (!isLong[x]) continue;
    let x1 = x; while (x1 + 1 < w && isLong[x1 + 1]) x1++;
    groups.push([x, x1]); x = x1;
  }
  let out = null, cleared = 0;
  const bands = [];
  const clear = (x) => {
    for (const [a, b] of longest(x, Math.round(h / 10))) { for (let y = a; y < b; y++) out.data[y * w + x] = 0; cleared += b - a; }
  };
  if (opts.bands) {
    // bands found on another binary of the page (a lenient threshold widens
    // them into the staff ends): long vertical runs there go, lines stay
    for (const [x0, x1] of opts.bands) {
      if (!out) out = { width: w, height: h, data: new Uint8Array(data) };
      for (let x = Math.max(0, x0 - 30); x <= Math.min(w - 1, x1 + 30); x++) clear(x);
    }
    return { binary: out || bin, cleared, bands: opts.bands };
  }
  for (const [x0, x1] of groups) {
    if (x1 - x0 + 1 < 6) continue;
    // staff lines leaving the inner side: long horizontal runs from the edge
    const dir = x0 < w / 2 ? 1 : -1, xe = dir === 1 ? x1 + 1 : x0 - 1;
    // (thin ones: a dark border along the top or bottom edge is thick)
    let attached = 0;
    const xt = xe + dir * 15;
    for (let y = 5; y < h - 5 && attached < 10; y++) {
      if (xt < 0 || xt >= w || data[(y - 5) * w + xt] || data[(y + 5) * w + xt]) continue;
      let n = 0;
      for (let x = xe; x >= 0 && x < w && Math.abs(x - xe) < 40 && data[y * w + x]; x += dir) n++;
      if (n >= 30) attached++;
    }
    if (attached >= 10) continue;
    if (!out) out = { width: w, height: h, data: new Uint8Array(data) };
    bands.push([x0, x1]);
    for (let x = x0; x <= x1; x++) clear(x);
    for (const [xs, d] of [[x0 - 1, -1], [x1 + 1, 1]]) {
      for (let k = 0, xx = xs; k < 8 && xx >= 0 && xx < w; k++, xx += d) {
        if (!longest(xx, Math.round(h / 10)).length) break;
        clear(xx);
      }
    }
  }
  return { binary: out || bin, cleared, bands };
}

module.exports = { clearEdgeBands, despeckle, binarize, backgroundNormalize, otsuFromHist, histogram, threshold, sauvola, estimateNoise, boxBlur, median3 };
