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

module.exports = { estimateStaffSpace };
