'use strict';
// Staff-line removal by line-tracking + vertical run-length test (Dalitz et al.
// 2008 "linetracking runlength" family): at each column of each detected line,
// the vertical ink run touching the line is erased when it is not much taller
// than a staff line (i.e. nothing crosses the line there).
const { cloneBinary } = require('./image');

function removeStaffLines(bin, staves, lt, opts = {}) {
  const out = cloneBinary(bin);
  const { width: w, height: h } = bin;
  const src = bin.data, dst = out.data;
  const maxRun = opts.maxRun || Math.max(2, Math.round(lt * 1.8 + 1));
  const search = Math.max(1, Math.round(lt / 2 + 1));
  let removed = 0;
  for (const st of staves) {
    const x0 = Math.max(0, st.left - 2), x1 = Math.min(w - 1, st.right + 2);
    for (let k = 0; k < 5; k++) {
      for (let x = x0; x <= x1; x++) {
        const yc = st.yAt(k, x);
        // find ink pixel nearest to yc within +-search
        let yi = -1;
        for (let d = 0; d <= search && yi < 0; d++) {
          const ya = Math.round(yc - d), yb = Math.round(yc + d);
          if (ya >= 0 && src[ya * w + x]) yi = ya; else if (yb < h && src[yb * w + x]) yi = yb;
        }
        if (yi < 0) continue;
        let a = yi, b = yi;
        while (a > 0 && src[(a - 1) * w + x]) a--;
        while (b < h - 1 && src[(b + 1) * w + x]) b++;
        if (b - a + 1 <= maxRun) {
          for (let y = a; y <= b; y++) dst[y * w + x] = 0;
          removed += b - a + 1;
        }
      }
    }
  }
  return { binary: out, removed, maxRun };
}

module.exports = { removeStaffLines };
