// ---- the repairs in plain JS (separable filters on typed arrays; OpenCV border rules: reflect-101
// for blurs, replicate-like max/min for morphology)
function gaussKernel(sigma) {
  const r = Math.max(1, Math.round(sigma * 3)), k = new Float32Array(2 * r + 1);
  let s = 0; for (let i = -r; i <= r; i++) { k[i + r] = Math.exp(-(i * i) / (2 * sigma * sigma)); s += k[i + r]; }
  for (let i = 0; i < k.length; i++) k[i] /= s;
  return { k, r };
}
const reflect = (i, n) => { if (n === 1) return 0; while (i < 0 || i >= n) i = i < 0 ? -i : 2 * n - 2 - i; return i; };
// separable Gaussian of an 8-bit image; returns Float32Array
function gaussBlur(src, w, h, sigma) {
  const { k, r } = gaussKernel(sigma), tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) {
    const o = y * w;
    for (let x = 0; x < w; x++) {
      let v = 0;
      if (x >= r && x < w - r) for (let i = -r; i <= r; i++) v += src[o + x + i] * k[i + r];
      else for (let i = -r; i <= r; i++) v += src[o + reflect(x + i, w)] * k[i + r];
      tmp[o + x] = v;
    }
  }
  for (let y = 0; y < h; y++) {
    const inside = y >= r && y < h - r;
    for (let x = 0; x < w; x++) {
      let v = 0;
      if (inside) for (let i = -r; i <= r; i++) v += tmp[(y + i) * w + x] * k[i + r];
      else for (let i = -r; i <= r; i++) v += tmp[reflect(y + i, h) * w + x] * k[i + r];
      out[y * w + x] = v;
    }
  }
  return out;
}
const clamp8 = (v) => (v < 0 ? 0 : v > 255 ? 255 : Math.round(v));
// running max (grow = true) or min over a 1-D window [i - a, i + b] along rows or columns
function morph1(src, w, h, a, b, horiz, grow) {
  const out = new Uint8Array(w * h);
  const n = horiz ? w : h, lines = horiz ? h : w;
  for (let l = 0; l < lines; l++) {
    for (let i = 0; i < n; i++) {
      let v = grow ? 0 : 255;
      for (let j = Math.max(0, i - a); j <= Math.min(n - 1, i + b); j++) {
        const p = horiz ? src[l * w + j] : src[j * w + l];
        if (grow ? p > v : p < v) v = p;
      }
      out[horiz ? l * w + i : i * w + l] = v;
    }
  }
  return out;
}
// grey closing with an elliptical element of size k (OpenCV MORPH_ELLIPSE): max, then min
function ellipseClose(src, w, h, k) {
  const r = k >> 1, half = [];
  // OpenCV's ellipse rows: half-width of row dy
  for (let dy = -r; dy <= r; dy++) half.push(r ? Math.round(r * Math.sqrt((r * r - dy * dy) / (r * r))) : 0);
  const pass = (img, grow) => {
    const out = new Uint8Array(w * h);
    // per row offset: max/min over horizontal windows of each half-width, cached
    const rowCache = new Map();
    const rowOp = (hw) => { if (!rowCache.has(hw)) rowCache.set(hw, morph1(img, w, h, hw, hw, true, grow)); return rowCache.get(hw); };
    out.fill(grow ? 0 : 255);
    for (let dy = -r; dy <= r; dy++) {
      const R = rowOp(half[dy + r]);
      for (let y = 0; y < h; y++) {
        const sy = y + dy, o = y * w, so = sy * w;
        if (sy < 0 || sy >= h) continue; // outside the image does not count (OpenCV's default border)
        if (grow) { for (let x = 0; x < w; x++) if (R[so + x] > out[o + x]) out[o + x] = R[so + x]; }
        else { for (let x = 0; x < w; x++) if (R[so + x] < out[o + x]) out[o + x] = R[so + x]; }
      }
    }
    return out;
  };
  return pass(pass(src, true), false);
}
function bilinearUp(src, W, H, w, h) {
  const out = new Float32Array(w * h), fx = W / w, fy = H / h;
  for (let y = 0; y < h; y++) {
    const sy = Math.min(H - 1, Math.max(0, (y + 0.5) * fy - 0.5)), y0 = Math.floor(sy), y1 = Math.min(H - 1, y0 + 1), ty = sy - y0;
    for (let x = 0; x < w; x++) {
      const sx = Math.min(W - 1, Math.max(0, (x + 0.5) * fx - 0.5)), x0 = Math.floor(sx), x1 = Math.min(W - 1, x0 + 1), tx = sx - x0;
      out[y * w + x] = (src[y0 * W + x0] * (1 - tx) + src[y0 * W + x1] * tx) * (1 - ty) + (src[y1 * W + x0] * (1 - tx) + src[y1 * W + x1] * tx) * ty;
    }
  }
  return out;
}

function applyOpsJs(gray, ops, q) {
  const { width: w, height: h } = gray;
  let d = gray.data;
  const ss = q.ss > 4 ? q.ss : 16;
  for (const op of ops) {
    if (op === 'flatten') {
      // 4x smaller (area weights as OpenCV INTER_AREA, also when the size is not a multiple of 4)
      const W4 = Math.max(1, w >> 2), H4 = Math.max(1, h >> 2), smf = areaResize(d, w, h, W4, H4);
      const sm = { data: Uint8Array.from(smf, v => clamp8(v)), W: W4, H: H4 };
      const k = Math.max(3, Math.round(ss * 0.8) | 1);
      const bgc = ellipseClose(sm.data, sm.W, sm.H, k);
      const bgf = gaussBlur(bgc, sm.W, sm.H, k / 2);
      const bg8 = new Uint8Array(bgf.length); for (let i = 0; i < bgf.length; i++) bg8[i] = clamp8(bgf[i]);
      const up = bilinearUp(bg8, sm.W, sm.H, w, h);
      const bv = Array.from(bg8).sort((x, y) => x - y), floor = 0.4 * bv[Math.floor(0.95 * (bv.length - 1))];
      const o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) { const u = Math.max(floor, Math.round(up[i])); o[i] = u > 0 ? clamp8(d[i] * 255 / u) : 0; }
      d = o;
    } else if (op === 'descreen') {
      const b = gaussBlur(d, w, h, Math.max(1, ss / 14)), o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) o[i] = clamp8(b[i]);
      d = o;
    } else if (op === 'thin') {
      const n = Math.max(1, Math.min(3, Math.round((q.lt - 0.11 * ss) / 2)));
      for (let i = 0; i < n; i++) d = morph1(morph1(d, w, h, 1, 1, true, true), w, h, 1, 1, false, true);
    } else if (op === 'sharpen') {
      const b = gaussBlur(d, w, h, Math.max(1, ss / 5)), o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) o[i] = clamp8(3 * d[i] - 2 * b[i]);
      d = o;
    } else if (op === 'close') {
      // OpenCV 2x2 erode, anchor (1,1): min over the pixel and its left / upper neighbours
      d = morph1(morph1(d, w, h, 1, 0, true, false), w, h, 1, 0, false, false);
    }
  }
  return { width: w, height: h, data: d === gray.data ? new Uint8Array(d) : d };
}
