'use strict';
// Connected-component labelling (8-connectivity, two-pass union-find) and
// integral images.

function labelComponents(bin, opts = {}) {
  const { width: w, height: h, data } = bin;
  const target = opts.value ?? 1;
  const labels = new Int32Array(w * h);
  const parent = [0];
  const find = (a) => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; } return a; };
  const union = (a, b) => { a = find(a); b = find(b); if (a !== b) { if (a < b) parent[b] = a; else parent[a] = b; } };
  let next = 1;
  const eight = opts.four !== true;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      if (data[i] !== target) continue;
      // labelled neighbours (left, up, up-left, up-right; 0 = none): the smallest labels the
      // pixel and the others are joined to it (no per-pixel array: this runs on every pixel)
      const a = x > 0 ? labels[i - 1] : 0, b = y > 0 ? labels[i - w] : 0;
      const c = eight && y > 0 && x > 0 ? labels[i - w - 1] : 0, d = eight && y > 0 && x < w - 1 ? labels[i - w + 1] : 0;
      if (!a && !b && !c && !d) { labels[i] = next; parent.push(next); next++; continue; }
      let m = 0x7fffffff;
      if (a && a < m) m = a; if (b && b < m) m = b; if (c && c < m) m = c; if (d && d < m) m = d;
      labels[i] = m;
      if (a && a !== m) union(m, a); if (b && b !== m) union(m, b); if (c && c !== m) union(m, c); if (d && d !== m) union(m, d);
    }
  }
  // compact
  const remap = new Int32Array(next);
  let count = 0;
  for (let l = 1; l < next; l++) { const r = find(l); if (!remap[r]) remap[r] = ++count; remap[l] = remap[r]; }
  const comps = [];
  for (let c = 0; c <= count; c++) comps.push({ id: c, area: 0, x0: w, y0: h, x1: -1, y1: -1, sx: 0, sy: 0 });
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    if (!labels[i]) continue;
    const l = remap[labels[i]]; labels[i] = l;
    const c = comps[l];
    c.area++; c.sx += x; c.sy += y;
    if (x < c.x0) c.x0 = x; if (x > c.x1) c.x1 = x; if (y < c.y0) c.y0 = y; if (y > c.y1) c.y1 = y;
  }
  comps.shift();
  return { labels, comps };
}

function integral(bin) {
  const { width: w, height: h, data } = bin;
  const W1 = w + 1;
  const I = new Int32Array(W1 * (h + 1));
  for (let y = 0; y < h; y++) {
    let rs = 0;
    for (let x = 0; x < w; x++) { rs += data[y * w + x]; I[(y + 1) * W1 + x + 1] = I[y * W1 + x + 1] + rs; }
  }
  return {
    w, h, I,
    // sum over [x0,x1) x [y0,y1) (clamped, floats rounded)
    sum(x0, y0, x1, y1) {
      x0 = Math.max(0, Math.min(w, Math.round(x0))); x1 = Math.max(0, Math.min(w, Math.round(x1)));
      y0 = Math.max(0, Math.min(h, Math.round(y0))); y1 = Math.max(0, Math.min(h, Math.round(y1)));
      if (x1 <= x0 || y1 <= y0) return 0;
      return I[y1 * W1 + x1] - I[y0 * W1 + x1] - I[y1 * W1 + x0] + I[y0 * W1 + x0];
    },
    frac(x0, y0, x1, y1) {
      x0 = Math.max(0, Math.min(w, Math.round(x0))); x1 = Math.max(0, Math.min(w, Math.round(x1)));
      y0 = Math.max(0, Math.min(h, Math.round(y0))); y1 = Math.max(0, Math.min(h, Math.round(y1)));
      const a = (x1 - x0) * (y1 - y0);
      if (a <= 0) return 0;
      return (I[y1 * W1 + x1] - I[y0 * W1 + x1] - I[y1 * W1 + x0] + I[y0 * W1 + x0]) / a;
    },
  };
}

module.exports = { labelComponents, integral };
