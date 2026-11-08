'use strict';
// Staff-line thickness and staff-space estimation from vertical run lengths
// (Fujinaga 1988 / Audiveris "combo" histogram).  Works before staff detection.
//   lt = line thickness (px), ss = line-to-line distance (px, centre to centre)

function estimateStaffSpace(bin, opts = {}) {
  const { width: w, height: h, data } = bin;
  const maxR = Math.min(200, h);
  const blackH = new Float64Array(maxR + 1);
  const whiteH = new Float64Array(maxR + 1);
  const comboH = new Float64Array(2 * maxR + 2); // black + following white
  const colStep = opts.colStep || 2;
  for (let x = 0; x < w; x += colStep) {
    let y = 0;
    let prevBlack = -1;
    while (y < h) {
      const v = data[y * w + x];
      let y1 = y;
      while (y1 < h && data[y1 * w + x] === v) y1++;
      const len = y1 - y;
      if (len <= maxR) {
        if (v) { blackH[len]++; prevBlack = len; }
        else {
          whiteH[len]++;
          if (prevBlack > 0 && y > 0 && y1 < h) comboH[prevBlack + len]++;
          prevBlack = -1;
        }
      } else if (v) prevBlack = -1; else prevBlack = -1;
      y = y1;
    }
  }
  const argmax = (H, lo, hi) => { let b = lo; for (let i = lo; i <= hi; i++) if (H[i] > H[b]) b = i; return b; };
  // staff space: combo mode in a plausible range (4..120 px)
  const sp = argmax(comboH, 4, Math.min(comboH.length - 1, 120));
  const refine = (H, m) => {
    let s = 0, n = 0;
    for (let i = Math.max(1, m - 1); i <= Math.min(H.length - 1, m + 1); i++) { s += i * H[i]; n += H[i]; }
    return n ? s / n : m;
  };
  const ss = refine(comboH, sp);
  // thickness: black-run mode restricted to runs < ss/2
  const lt0 = argmax(blackH, 1, Math.max(1, Math.floor(ss / 2)));
  const lt = refine(blackH, lt0);
  // confidence: how peaked the combo histogram is
  let tot = 0; for (let i = 4; i < comboH.length; i++) tot += comboH[i];
  const peakMass = (comboH[sp - 1] || 0) + comboH[sp] + (comboH[sp + 1] || 0);
  return { ss, lt, confidence: tot ? peakMass / tot : 0, hist: opts.keepHist ? { blackH, whiteH, comboH } : undefined };
}

// Staff space from the autocorrelation of strip-wise horizontal projections.
// Integrates along x, so it survives broken / dotted lines and heavy blur where
// run-length statistics break down.
function staffSpaceAC(bin, minSS = 4, maxSS = 80) {
  const { width: w, height: h, data } = bin;
  const nStrips = 8, sw = Math.floor(w / nStrips);
  const ac = new Float64Array(maxSS + 2);
  const proj = new Float64Array(h);
  for (let s = 0; s < nStrips; s++) {
    proj.fill(0);
    for (let y = 0; y < h; y++) { let c = 0; const r = y * w + s * sw; for (let x = 0; x < sw; x += 2) c += data[r + x]; proj[y] = c; }
    let m = 0; for (let y = 0; y < h; y++) m += proj[y]; m /= h;
    for (let y = 0; y < h; y++) proj[y] -= m;
    let a0 = 0; for (let y = 0; y < h; y++) a0 += proj[y] * proj[y];
    if (a0 <= 0) continue;
    for (let lag = minSS - 1; lag <= maxSS + 1; lag++) {
      let a = 0; for (let y = 0; y + lag < h; y++) a += proj[y] * proj[y + lag];
      ac[lag] += a / a0;
    }
  }
  // best local maximum with prominence over the preceding minimum (the AC of
  // a page without staff periodicity just decays -> no valid peak)
  let best = -1, bestProm = 0.03;
  let runMin = ac[minSS - 1];
  for (let lag = minSS; lag <= maxSS; lag++) {
    if (ac[lag] < runMin) runMin = ac[lag];
    if (ac[lag] > ac[lag - 1] && ac[lag] >= ac[lag + 1]) {
      const prom = ac[lag] - runMin;
      if (prom > bestProm && (best < 0 || ac[lag] > ac[best])) { best = lag; bestProm = Math.max(0.03, prom * 0.5); }
    }
  }
  if (best < 0) return { ss: NaN, peak: 0 };
  const a = ac[best - 1], b = ac[best], c = ac[best + 1];
  const den = a - 2 * b + c;
  const off = den < 0 ? 0.5 * (a - c) / den : 0;
  return { ss: best + Math.max(-0.5, Math.min(0.5, off)), peak: b / nStrips };
}

// Combined estimate: run-length combo (precise) cross-checked by autocorrelation (robust).
function estimateStaffSpaceRobust(bin, opts = {}) {
  const rl = estimateStaffSpace(bin, opts);
  const ac = staffSpaceAC(bin);
  rl.ssRunLength = rl.ss; rl.ssAC = Number.isFinite(ac.ss) ? ac.ss : 0;
  if (Number.isFinite(ac.ss) && Math.abs(rl.ss - ac.ss) / ac.ss > 0.12) {
    rl.ss = ac.ss; rl.source = 'autocorr';
    // recompute thickness from black runs below ss/2
    const { width: w, height: h, data } = bin;
    const H = new Float64Array(Math.ceil(ac.ss / 2) + 2);
    for (let x = 0; x < w; x += 2) {
      let y = 0;
      while (y < h) { if (!data[y * w + x]) { y++; continue; } let y1 = y; while (y1 < h && data[y1 * w + x]) y1++; const L = y1 - y; if (L < H.length) H[L]++; y = y1; }
    }
    let m = 1; for (let i = 1; i < H.length; i++) if (H[i] > H[m]) m = i;
    rl.lt = m;
  } else rl.source = 'runlength';
  return rl;
}

module.exports = { estimateStaffSpace, staffSpaceAC, estimateStaffSpaceRobust };
