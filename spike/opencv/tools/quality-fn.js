// page-quality measures on a gray page (draft; becomes part of src/cv.js)
'use strict';
function measure(g, estimateStaffSpace) {
  const { width: w, height: h, data } = g, n = w * h;
  // histogram and Otsu threshold
  const hist = new Float64Array(256); for (let i = 0; i < n; i++) hist[data[i]]++;
  let sum = 0; for (let v = 0; v < 256; v++) sum += v * hist[v];
  let wB = 0, sB = 0, best = 0, thr = 128;
  for (let v = 0; v < 256; v++) { wB += hist[v]; if (!wB || wB === n) continue; sB += v * hist[v]; const mB = sB / wB, mF = (sum - sB) / (n - wB); const b = wB * (n - wB) * (mB - mF) ** 2; if (b > best) { best = b; thr = v; } }
  let mid = 0, dark = 0; for (let v = 0; v < 256; v++) { if (v > 60 && v < 200) mid += hist[v]; if (v <= thr) dark += hist[v]; }
  // background per 32 px cell: 90th percentile; and spread of the light pixels inside each cell
  const CS = 32, cw = Math.ceil(w / CS), ch = Math.ceil(h / CS), bg = [], sd = [];
  const cellH = new Uint32Array(256);
  for (let cy = 0; cy < ch; cy++) for (let cx = 0; cx < cw; cx++) {
    cellH.fill(0); let cnt = 0;
    for (let y = cy * CS; y < Math.min(h, cy * CS + CS); y += 2) for (let x = cx * CS; x < Math.min(w, cx * CS + CS); x += 2) { cellH[data[y * w + x]]++; cnt++; }
    let acc = 0, p90 = 255; for (let v = 0; v < 256; v++) { acc += cellH[v]; if (acc >= 0.9 * cnt) { p90 = v; break; } }
    bg.push(p90);
    // std of pixels within 70 of the cell background (paper texture, halftone dots, noise)
    let s1 = 0, s2 = 0, m = 0; for (let v = Math.max(0, p90 - 70); v <= 255; v++) { s1 += v * cellH[v]; s2 += v * v * cellH[v]; m += cellH[v]; }
    sd.push(m ? Math.sqrt(Math.max(0, s2 / m - (s1 / m) ** 2)) : 0);
  }
  const sorted = bg.slice().sort((a, b) => a - b), pct = (a, p) => a[Math.min(a.length - 1, Math.floor(p * a.length))];
  const sds = sd.slice().sort((a, b) => a - b);
  // isolated dark specks (all 8 neighbours light) per megapixel
  let speck = 0;
  for (let y = 1; y < h - 1; y += 1) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x; if (data[i] > thr) continue;
    if (data[i - 1] > thr && data[i + 1] > thr && data[i - w] > thr && data[i + w] > thr && data[i - w - 1] > thr && data[i - w + 1] > thr && data[i + w - 1] > thr && data[i + w + 1] > thr) speck++;
  }
  const bin = { width: w, height: h, data: new Uint8Array(n) }; for (let i = 0; i < n; i++) bin.data[i] = data[i] <= thr ? 1 : 0;
  const sp = estimateStaffSpace(bin);
  return { thr, mid: mid / n, dark: dark / n, bgLow: (255 - pct(sorted, 0.5)) / 255, bgUneven: (pct(sorted, 0.95) - pct(sorted, 0.05)) / 255, bgStd: pct(sds, 0.5), speck: speck / (n / 1e6), lt: sp.lt, ss: sp.ss, ltss: sp.ss ? sp.lt / sp.ss : 0 };
}
module.exports = { measure };
