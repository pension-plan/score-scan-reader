'use strict';
// Global skew estimation by projection-profile sharpness (sum of squared bin
// counts of y + x*tan(theta)).  Staff lines dominate, so this is very sharp on
// music pages.  Returns degrees, positive = content rotated counter-clockwise
// (visually, y down), i.e. lines rise to the right.

function collectPoints(bin, step) {
  const { width: w, height: h, data } = bin;
  const xs = [], ys = [];
  for (let y = 0; y < h; y += step) {
    const row = y * w;
    for (let x = 0; x < w; x += step) if (data[row + x]) { xs.push(x); ys.push(y); }
  }
  return { xs: Float64Array.from(xs), ys: Float64Array.from(ys) };
}

function score(pts, w, h, deg, binW = 1) {
  const t = Math.tan((deg * Math.PI) / 180);
  const off = Math.abs(t) * w + 2;
  const nb = Math.ceil((h + 2 * off) / binW) + 2;
  const bins = new Float64Array(nb);
  const { xs, ys } = pts;
  for (let i = 0; i < xs.length; i++) {
    const b = ((ys[i] + xs[i] * t + off) / binW) | 0;
    bins[b]++;
  }
  let s = 0;
  for (let i = 0; i < nb; i++) s += bins[i] * bins[i];
  return s;
}

function estimateSkew(bin, opts = {}) {
  const maxDeg = opts.maxDeg ?? 8;
  const { width: w, height: h } = bin;
  const step = w > 1800 ? 2 : 1;
  const pts = collectPoints(bin, step);
  if (pts.xs.length < 100) return { angle: 0, confidence: 0 };
  // coarse
  let best = 0, bestS = -1;
  const coarse = [];
  for (let d = -maxDeg; d <= maxDeg + 1e-9; d += 0.25) {
    const s = score(pts, w, h, d, step);
    coarse.push(s);
    if (s > bestS) { bestS = s; best = d; }
  }
  // fine
  let fBest = best, fS = bestS;
  for (let d = best - 0.3; d <= best + 0.3 + 1e-9; d += 0.02) {
    const s = score(pts, w, h, d, step);
    if (s > fS) { fS = s; fBest = d; }
  }
  // finest (sub-bin) around fBest using 1px bins on full points
  const median = coarse.slice().sort((a, b) => a - b)[coarse.length >> 1];
  return { angle: Math.round(fBest * 1000) / 1000, confidence: fS / Math.max(1, median) };
}

module.exports = { estimateSkew };
