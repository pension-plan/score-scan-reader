'use strict';
// Blob-based notehead detection on the staff-removed binary.
//   1. fill small enclosed holes of B (hollow heads become solid)
//   2. horizontal opening (kills stems, barlines, thin vertical strokes)
//   3. vertical opening (kills staff-line remnants, ledgers, thin horizontals)
//   4. connected components -> head-sized blobs; tall blobs are stacked chords,
//      wide blobs are beams (returned separately) or seconds (split L/R).
// Kind (filled / hollow) comes from the core density of R at the head centre.
const { makeBinary } = require('./image');
const { labelComponents, integral } = require('./cc');

function fillHoles(B, R, ss) {
  // background components of B that are small and enclosed -> ink in a copy of R
  const { width: w, height: h } = B;
  const inv = makeBinary(w, h);
  for (let i = 0; i < w * h; i++) inv.data[i] = B.data[i] ? 0 : 1;
  const { labels, comps } = labelComponents(inv, { four: true });
  const maxW = 1.5 * ss, maxH = 1.0 * ss, maxA = 0.6 * ss * ss;
  const fill = new Uint8Array(comps.length + 1);
  for (const c of comps) {
    if (c.x0 === 0 || c.y0 === 0 || c.x1 === w - 1 || c.y1 === h - 1) continue;
    if (c.x1 - c.x0 + 1 <= maxW && c.y1 - c.y0 + 1 <= maxH && c.area <= maxA && c.area >= 2) fill[c.id] = 1;
  }
  const out = { width: w, height: h, data: new Uint8Array(R.data) };
  for (let i = 0; i < w * h; i++) if (labels[i] && fill[labels[i]]) out.data[i] = 1;
  return out;
}

function openRuns(bin, minLen, horizontal) {
  const { width: w, height: h, data } = bin;
  const out = new Uint8Array(w * h);
  if (horizontal) {
    for (let y = 0; y < h; y++) {
      const r = y * w;
      for (let x = 0; x < w;) {
        if (!data[r + x]) { x++; continue; }
        let x1 = x; while (x1 < w && data[r + x1]) x1++;
        if (x1 - x >= minLen) out.fill(1, r + x, r + x1);
        x = x1;
      }
    }
  } else {
    for (let x = 0; x < w; x++) {
      for (let y = 0; y < h;) {
        if (!data[y * w + x]) { y++; continue; }
        let y1 = y; while (y1 < h && data[y1 * w + x]) y1++;
        if (y1 - y >= minLen) for (let k = y; k < y1; k++) out[k * w + x] = 1;
        y = y1;
      }
    }
  }
  return { width: w, height: h, data: out };
}

// staff lookup: nearest staff and staff position for a point
function staffPos(staves, x, y) {
  let best = null, bd = 1e9;
  for (const st of staves) {
    if (x < st.left - 3 * st.space || x > st.right + st.space) continue;
    const ym = st.yAt(2, x), sp = st.spaceAt(x);
    const d = Math.abs(y - ym) / sp;
    if (d < bd) { bd = d; best = { st, p: (ym - y) / (sp / 2), sp }; }
  }
  return best;
}

function detectHeads(B, R, staves, ss, lt) {
  const F = fillHoles(B, R, ss);
  const O1 = openRuns(F, Math.max(3, Math.round(0.55 * ss)), true);
  const O = openRuns(O1, Math.max(3, Math.round(0.42 * ss)), false);
  const { comps } = labelComponents(O);
  const IR = integral(R), IB = integral(B);
  const heads = [], beams = [];
  for (const c of comps) {
    const bw = c.x1 - c.x0 + 1, bh = c.y1 - c.y0 + 1;
    if (bw < 0.8 * ss || bh < 0.5 * ss) continue;
    const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
    const sp0 = staffPos(staves, cx, cy);
    if (!sp0 || Math.abs(sp0.p) > 12) continue;
    const sp = sp0.sp;
    const fillRatio = c.area / (bw * bh);
    if (bw > 2.4 * sp) {
      if (bh < 1.6 * sp) beams.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1, staff: sp0.st.index });
      continue;
    }
    if (fillRatio < 0.45 || bh > 5.5 * sp) continue;
    // columns: a second (two heads offset sideways) makes the blob ~2 heads wide
    const cols = bw > 1.75 * sp ? [[c.x0, c.x0 + bw / 2], [c.x0 + bw / 2, c.x1 + 1]] : [[c.x0, c.x1 + 1]];
    for (const [xa, xb] of cols) {
      // vertical extent of ink in this column range
      let ya = -1, yb = -1;
      const xm = Math.round((xa + xb) / 2);
      for (let y = c.y0; y <= c.y1; y++) {
        let n = 0; for (let x = Math.round(xa); x < xb; x++) n += O.data[y * O.width + x];
        if (n > 0.3 * (xb - xa)) { if (ya < 0) ya = y; yb = y; }
      }
      if (ya < 0) continue;
      const hh = yb - ya + 1;
      const k = Math.max(1, Math.round(hh / (0.95 * sp)));
      if (k > 4) continue;
      const step = hh / k;
      for (let i = 0; i < k; i++) {
        const y = ya + step * (i + 0.5);
        const ps = staffPos(staves, xm, y);
        if (!ps) continue;
        const p = Math.round(ps.p);
        const ycen = ps.st.yAt(2, xm) - (p * ps.sp) / 2;
        const core = IR.frac(xm - 0.18 * sp, ycen - 0.12 * sp, xm + 0.18 * sp, ycen + 0.12 * sp);
        const coreB = IB.frac(xm - 0.3 * sp, ycen - 0.2 * sp, xm + 0.3 * sp, ycen + 0.2 * sp);
        const hollow = core < 0.5 && coreB < 0.75;
        const wid = xb - xa;
        if (wid < 0.9 * sp) continue;
        heads.push({ x: xm, y: ycen, staff: ps.st.index, p, sp, kind: hollow ? 'hollow' : 'filled', score: 1, w: wid,
          x0: Math.round(xa), x1: Math.round(xb) });
      }
    }
  }
  // dedupe
  heads.sort((a, b) => a.x - b.x);
  const out = [];
  for (const h of heads) if (!out.some(o => o.staff === h.staff && o.p === h.p && Math.abs(o.x - h.x) < 0.6 * h.sp)) out.push(h);
  return { heads: out, beams, opened: O };
}

// Ledger-line evidence.  A head more than half a space outside its staff
// (|p| >= 6) always sits on / next to ledger lines: thin horizontal strokes at
// p = +-6, +-8, ... crossing the head's column.  Lyrics, titles, tuplet
// numbers and dynamics that blob-detect as heads have none.
//   ledgers between staff and head: a thin line >= 0.8 sp around the head x
//   the ledger touching the head: merged with it, so only the short ends that
//   reach past the head count
function ledgerOK(bin, staves, hd, lt) {
  const ap = Math.abs(hd.p);
  if (ap < 6) return true;
  const { width: w, height: h, data } = bin;
  const sp = hd.sp, sgn = hd.p > 0 ? 1 : -1;
  const st = staves[hd.staff];
  const xm = Math.round(hd.x);
  const maxThick = Math.max(2, Math.round(1.6 * lt + 1));
  const band = Math.max(1, Math.round(lt / 2 + 1));
  const ymid = st.yAt(2, xm);
  const thinAt = (x, yq) => {
    if (x < 0 || x >= w) return false;
    for (let y = Math.round(yq - band); y <= Math.round(yq + band); y++) {
      if (y < 0 || y >= h || !data[y * w + x]) continue;
      let a = y, b = y;
      while (a > 0 && data[(a - 1) * w + x] && y - a <= maxThick) a--;
      while (b < h - 1 && data[(b + 1) * w + x] && b - y <= maxThick) b++;
      if (b - a + 1 <= maxThick) return true;
    }
    return false;
  };
  for (let q = 6; q <= ap; q += 2) {
    const yq = ymid - sgn * (q * sp) / 2;
    if (ap - q >= 2) {
      const reach = Math.round(1.1 * sp), side = 0.25 * sp;
      let n = 0, left = 0, right = 0;
      for (let x = xm - reach; x <= xm + reach; x++) {
        if (!thinAt(x, yq)) continue;
        n++; if (x < xm - side) left++; else if (x > xm + side) right++;
      }
      if (n < 0.8 * sp || left < 2 || right < 2) return false;
    } else {
      const reach = Math.round(1.25 * sp), inner = Math.round(0.45 * sp);
      let left = 0, right = 0;
      for (let x = xm - reach; x <= xm + reach; x++) {
        if (Math.abs(x - xm) <= inner || !thinAt(x, yq)) continue;
        if (x < xm) left++; else right++;
      }
      if (left + right < Math.max(3, 0.25 * sp) || Math.max(left, right) < 2) return false;
    }
  }
  return true;
}

module.exports = { detectHeads, staffPos, fillHoles, openRuns, ledgerOK };

// Chord-level stem detection.  Heads of one staff whose x differ by < 0.6 sp
// form a chord; we look for the longest thin vertical run leaving the chord
// upward (from the top head) and downward (from the bottom head) on L (a
// lenient, staff-removed binary: faint thin stems survive there).
function chordStems(L, heads, opts = {}) {
  const minLen = opts.minLen ?? 1.5;
  const { width: w, height: h, data } = L;
  const byStaff = {};
  for (const hd of heads) (byStaff[hd.staff] ||= []).push(hd);
  const chords = [];
  for (const k in byStaff) {
    const hs = byStaff[k].sort((a, b) => a.x - b.x);
    let cur = null;
    for (const hd of hs) {
      if (cur && hd.x - cur.xs[cur.xs.length - 1] < 0.7 * hd.sp) { cur.heads.push(hd); cur.xs.push(hd.x); }
      else { cur = { heads: [hd], xs: [hd.x], staff: +k }; chords.push(cur); }
    }
  }
  const ink = (x, y) => x >= 0 && y >= 0 && x < w && y < h && data[y * w + x];
  for (const c of chords) {
    c.heads.sort((a, b) => a.y - b.y);
    const sp = c.heads[0].sp;
    const top = c.heads[0], bot = c.heads[c.heads.length - 1];
    const xa = Math.round(Math.min(...c.xs) - 0.85 * sp), xb = Math.round(Math.max(...c.xs) + 0.85 * sp);
    const maxGap = Math.max(2, Math.round(0.4 * sp));
    let up = 0, upX = -1, down = 0, downX = -1;
    for (let x = xa; x <= xb; x++) {
      // upward run starting inside the top head band
      let y0 = -1;
      for (let y = Math.round(top.y + 0.3 * sp); y >= Math.round(top.y - 0.5 * sp); y--) if (ink(x, y)) { y0 = y; }
      if (y0 >= 0) {
        let yt = y0, gap = 0;
        for (let y = y0 - 1; y >= 0; y--) { if (ink(x, y)) { yt = y; gap = 0; } else if (++gap > maxGap) break; }
        // thin: the run's upper part must not be wide (not a beam/flag-free blob check, cheap)
        const len = (top.y - yt) / sp;
        if (len > up) { up = len; upX = x; c.upEnd = yt; }
      }
      y0 = -1;
      for (let y = Math.round(bot.y - 0.3 * sp); y <= Math.round(bot.y + 0.5 * sp); y++) if (ink(x, y)) { y0 = y; }
      if (y0 >= 0) {
        let yb = y0, gap = 0;
        for (let y = y0 + 1; y < h; y++) { if (ink(x, y)) { yb = y; gap = 0; } else if (++gap > maxGap) break; }
        const len = (yb - bot.y) / sp;
        if (len > down) { down = len; downX = x; c.downEnd = yb; }
      }
    }
    c.up = up >= minLen ? up : 0; c.down = down >= minLen ? down : 0;
    c.upX = upX; c.downX = downX;
    c.x = c.xs.reduce((a, b) => a + b, 0) / c.xs.length;
    for (const hd of c.heads) hd.chord = c;
    if (c.up && c.down) {
      // two voices: the head(s) nearest the up stem go up; split at the largest gap
      // simple rule: top head(s) up, bottom head down
      const n = c.heads.length;
      c.heads.forEach((hd, i) => { hd.stemDir = i < Math.ceil(n / 2) ? 1 : -1; });
      if (n === 1) c.heads[0].stemDir = 2;
    } else if (c.up) c.heads.forEach(hd => { hd.stemDir = 1; });
    else if (c.down) c.heads.forEach(hd => { hd.stemDir = -1; });
    else c.heads.forEach(hd => { hd.stemDir = 0; });
    for (const hd of c.heads) hd.stem = { dir: hd.stemDir, upX, downX, up: c.up, down: c.down };
  }
  return chords;
}

module.exports.chordStems = chordStems;
