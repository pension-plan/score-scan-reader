'use strict';
// Minimal environment-agnostic grayscale bitmap helpers ({width,height,data:Uint8ClampedArray}).
// Node-only I/O (readGray/toPNG) is lazily required so the rest also runs in a browser.

function readGray(path) {
  const { PNG } = require('pngjs');
  const fs = require('fs');
  const png = PNG.sync.read(fs.readFileSync(path));
  const { width, height, data } = png;
  const g = new Uint8ClampedArray(width * height);
  for (let i = 0, j = 0; i < g.length; i++, j += 4) g[i] = (data[j] * 299 + data[j + 1] * 587 + data[j + 2] * 114) / 1000;
  return { width, height, data: g };
}
function toPNG(img) {
  const { PNG } = require('pngjs');
  const png = new PNG({ width: img.width, height: img.height, colorType: 0, inputColorType: 0, inputHasAlpha: false });
  png.data = Buffer.from(img.data.buffer, img.data.byteOffset, img.data.length);
  return PNG.sync.write(png, { colorType: 0, inputColorType: 0, inputHasAlpha: false });
}
function crop(img, x0, y0, x1, y1) {
  x0 = Math.max(0, Math.floor(x0)); y0 = Math.max(0, Math.floor(y0));
  x1 = Math.min(img.width, Math.ceil(x1)); y1 = Math.min(img.height, Math.ceil(y1));
  const w = Math.max(1, x1 - x0), h = Math.max(1, y1 - y0);
  const out = new Uint8ClampedArray(w * h);
  for (let y = 0; y < h; y++) out.set(img.data.subarray((y0 + y) * img.width + x0, (y0 + y) * img.width + x0 + w), y * w);
  return { width: w, height: h, data: out, x0, y0 };
}
function resize(img, s) {
  // area-average for downscale, bilinear for upscale
  const W = Math.max(1, Math.round(img.width * s)), H = Math.max(1, Math.round(img.height * s));
  const out = new Uint8ClampedArray(W * H);
  const src = img.data, w = img.width, h = img.height;
  if (s >= 1) {
    for (let y = 0; y < H; y++) {
      const fy = Math.min(h - 1, Math.max(0, (y + 0.5) / s - 0.5)); const y0 = Math.floor(fy), y1 = Math.min(h - 1, y0 + 1), dy = fy - y0;
      for (let x = 0; x < W; x++) {
        const fx = Math.min(w - 1, Math.max(0, (x + 0.5) / s - 0.5)); const x0 = Math.floor(fx), x1 = Math.min(w - 1, x0 + 1), dx = fx - x0;
        const a = src[y0 * w + x0], b = src[y0 * w + x1], c = src[y1 * w + x0], d = src[y1 * w + x1];
        out[y * W + x] = (a * (1 - dx) + b * dx) * (1 - dy) + (c * (1 - dx) + d * dx) * dy;
      }
    }
  } else {
    const inv = 1 / s;
    for (let y = 0; y < H; y++) {
      const sy0 = y * inv, sy1 = Math.min(h, (y + 1) * inv);
      for (let x = 0; x < W; x++) {
        const sx0 = x * inv, sx1 = Math.min(w, (x + 1) * inv);
        let acc = 0, wt = 0;
        for (let yy = Math.floor(sy0); yy < Math.ceil(sy1); yy++) {
          const wy = Math.min(yy + 1, sy1) - Math.max(yy, sy0);
          for (let xx = Math.floor(sx0); xx < Math.ceil(sx1); xx++) {
            const wx = Math.min(xx + 1, sx1) - Math.max(xx, sx0);
            acc += src[yy * w + xx] * wx * wy; wt += wx * wy;
          }
        }
        out[y * W + x] = acc / wt;
      }
    }
  }
  return { width: W, height: H, data: out };
}
function otsu(img) {
  const hist = new Float64Array(256);
  for (let i = 0; i < img.data.length; i++) hist[img.data[i]]++;
  const total = img.data.length; let sum = 0;
  for (let i = 0; i < 256; i++) sum += i * hist[i];
  let sumB = 0, wB = 0, best = 0, thr = 128;
  for (let t = 0; t < 256; t++) {
    wB += hist[t]; if (!wB) continue; const wF = total - wB; if (!wF) break;
    sumB += t * hist[t]; const mB = sumB / wB, mF = (sum - sumB) / wF;
    const v = wB * wF * (mB - mF) * (mB - mF);
    if (v > best) { best = v; thr = t; }
  }
  return thr;
}
/** Adaptive (local mean) binarisation; returns Uint8Array 1=ink. Window ~ 2*r+1. */
function binarize(img, r = 25, k = 0.12) {
  const { width: w, height: h, data } = img;
  const ii = new Float64Array((w + 1) * (h + 1));
  for (let y = 0; y < h; y++) { let row = 0; for (let x = 0; x < w; x++) { row += data[y * w + x]; ii[(y + 1) * (w + 1) + x + 1] = ii[y * (w + 1) + x + 1] + row; } }
  const g = otsu(img);
  const out = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    const ya = Math.max(0, y - r), yb = Math.min(h, y + r + 1);
    for (let x = 0; x < w; x++) {
      const xa = Math.max(0, x - r), xb = Math.min(w, x + r + 1);
      const s = ii[yb * (w + 1) + xb] - ii[ya * (w + 1) + xb] - ii[yb * (w + 1) + xa] + ii[ya * (w + 1) + xa];
      const mean = s / ((yb - ya) * (xb - xa));
      const v = data[y * w + x];
      out[y * w + x] = (v < mean * (1 - k) && v < g + 40) ? 1 : 0;
    }
  }
  return out;
}
/** 8-connected components on a binary mask. Returns {labels:Int32Array, comps:[{x0,y0,x1,y1,area}]} (x1,y1 exclusive). */
function components(bin, w, h) {
  const labels = new Int32Array(w * h).fill(0);
  const comps = [null]; const stack = new Int32Array(w * h);
  let n = 0;
  for (let i = 0; i < w * h; i++) {
    if (!bin[i] || labels[i]) continue;
    n++; let sp = 0; stack[sp++] = i; labels[i] = n;
    let x0 = w, y0 = h, x1 = -1, y1 = -1, area = 0;
    while (sp) {
      const p = stack[--sp]; const x = p % w, y = (p - x) / w; area++;
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
      for (let dy = -1; dy <= 1; dy++) {
        const yy = y + dy; if (yy < 0 || yy >= h) continue;
        for (let dx = -1; dx <= 1; dx++) {
          const xx = x + dx; if (xx < 0 || xx >= w) continue;
          const q = yy * w + xx; if (bin[q] && !labels[q]) { labels[q] = n; stack[sp++] = q; }
        }
      }
    }
    comps.push({ id: n, x0, y0, x1: x1 + 1, y1: y1 + 1, area });
  }
  return { labels, comps };
}
module.exports = { readGray, toPNG, crop, resize, otsu, binarize, components };
