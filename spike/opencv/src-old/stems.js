'use strict';
// Stem search next to each notehead on the staff-removed binary.  For both
// sides of the head, find the column whose vertical ink run (through the head
// row, small gaps bridged) extends furthest up / down.  A stem is a run that
// extends >= minLen staff spaces beyond the head centre.
//   dir: +1 up, -1 down, 2 both (shared head of two voices / chord), 0 none

function runExtent(R, x, yc, sp, maxGap) {
  const { width: w, height: h, data } = R;
  if (x < 0 || x >= w) return { up: 0, down: 0 };
  // start: nearest ink pixel to yc within +-0.4 sp
  let y0 = -1;
  const lim = Math.round(0.45 * sp);
  for (let d = 0; d <= lim && y0 < 0; d++) {
    const a = Math.round(yc - d), b = Math.round(yc + d);
    if (a >= 0 && data[a * w + x]) y0 = a; else if (b < h && data[b * w + x]) y0 = b;
  }
  if (y0 < 0) return { up: 0, down: 0 };
  let top = y0, gap = 0;
  for (let y = y0 - 1; y >= 0; y--) { if (data[y * w + x]) { top = y; gap = 0; } else if (++gap > maxGap) break; }
  let bot = y0; gap = 0;
  for (let y = y0 + 1; y < h; y++) { if (data[y * w + x]) { bot = y; gap = 0; } else if (++gap > maxGap) break; }
  return { up: yc - top, down: bot - yc, top, bot };
}

function detectStems(R, heads, opts = {}) {
  const minLen = opts.minLen ?? 2.2;
  for (const hd of heads) {
    const sp = hd.sp;
    const maxGap = Math.max(1, Math.round(0.12 * sp));
    let best = { up: 0, down: 0, upX: -1, downX: -1, upSide: 0, downSide: 0 };
    const scan = (xa, xb, side) => {
      for (let x = Math.round(xa); x <= Math.round(xb); x++) {
        const e = runExtent(R, x, hd.y, sp, maxGap);
        if (e.up > best.up) { best.up = e.up; best.upX = x; best.upSide = side; best.upEnd = e.top; }
        if (e.down > best.down) { best.down = e.down; best.downX = x; best.downSide = side; best.downEnd = e.bot; }
      }
    };
    const half = hd.kind === 'hollow' ? 0.95 : 0.8;
    scan(hd.x + 0.2 * sp, hd.x + half * sp, 1);
    scan(hd.x - half * sp, hd.x - 0.2 * sp, -1);
    const up = best.up / sp, down = best.down / sp;
    const hasUp = up >= minLen, hasDown = down >= minLen;
    let dir = 0;
    if (hasUp && hasDown) {
      // genuine double stem (unison of two voices): up stem on the right, down stem on the left, different columns
      if (best.upSide === 1 && best.downSide === -1 && Math.abs(best.upX - best.downX) > 0.5 * sp) dir = 2;
      else dir = up >= down ? 1 : -1; // chord middle note: one stem passing by
    } else if (hasUp) dir = 1; else if (hasDown) dir = -1;
    hd.stem = { dir, up: +up.toFixed(2), down: +down.toFixed(2), upX: best.upX, downX: best.downX, upEnd: best.upEnd, downEnd: best.downEnd };
  }
  return heads;
}

// Filter heads with the stem rule: filled heads and half notes have stems,
// whole notes do not (and are wider).  Returns kept heads; sets hd.kind to
// 'filled' | 'half' | 'whole'.
function applyStemRule(heads, opts = {}) {
  const out = [];
  for (const hd of heads) {
    const has = hd.stem && hd.stem.dir !== 0;
    if (hd.kind === 'filled') {
      if (has || (opts.keepStemless && hd.score >= 0.97)) out.push(hd);
    } else if (hd.kind === 'hollow') {
      if (has) { hd.kind = 'half'; out.push(hd); }
      else { hd.kind = 'whole'; out.push(hd); }
    } else out.push(hd);
  }
  return out;
}

module.exports = { detectStems, applyStemRule, runExtent };
