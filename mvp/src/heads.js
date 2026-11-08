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

function fillHoles(B, R, ss, lt = 2, opts = {}) {
  // background components of B that are small and enclosed -> ink in a copy of R.
  // Worn hollow heads (older engravings, light scans) have 1-2 px breaks in
  // their outline: a second pass looks for holes after a 1-px dilation of B,
  // restricted to the shape of a head's inside (flat, at most ~2/3 space high).
  // Above / below every filled inside, the outline (and a staff line crossing
  // it) is put back over the inside's columns: staff-line removal eats those
  // thin horizontal pieces and would cut the head in two.
  const { width: w, height: h } = B;
  const src = B.data;
  const out = { width: w, height: h, data: new Uint8Array(R.data) };
  const o = out.data;
  const inner = (c) => !(c.x0 === 0 || c.y0 === 0 || c.x1 === w - 1 || c.y1 === h - 1);
  const r = Math.max(2, Math.round(lt + 1));
  const restore = (labels, c) => {
    for (let x = c.x0; x <= c.x1; x++) {
      let top = -1, bot = -1;
      for (let y = c.y0; y <= c.y1; y++) if (labels[y * w + x] === c.id) { if (top < 0) top = y; bot = y; }
      if (top < 0) continue;
      for (let y = top - 1, k = 0; y >= 0 && k < r && src[y * w + x]; y--, k++) o[y * w + x] = 1;
      for (let y = bot + 1, k = 0; y < h && k < r && src[y * w + x]; y++, k++) o[y * w + x] = 1;
    }
  };
  const inv = makeBinary(w, h);
  // a head's inside sits in a head-tall stack of ink (outline + inside >= 3/4
  // space); the lens between a slur / tie and a staff line or beam is flat
  const headTall = (labels, c) => {
    const isIn = (i) => !inv.data[i] || labels[i] === c.id;  // ink (of the image searched) or the hole
    let best = 0;
    const xm = Math.round((c.x0 + c.x1) / 2);
    for (let x = Math.max(c.x0, xm - 2); x <= Math.min(c.x1, xm + 2); x++) {
      let y0 = -1;
      for (let y = c.y0; y <= c.y1; y++) if (labels[y * w + x] === c.id) { y0 = y; break; }
      if (y0 < 0) continue;
      let a = y0, b = y0;
      while (a > 0 && isIn((a - 1) * w + x)) a--;
      while (b < h - 1 && isIn((b + 1) * w + x)) b++;
      best = Math.max(best, b - a + 1);
    }
    return best >= 0.75 * ss;
  };
  for (let i = 0; i < w * h; i++) inv.data[i] = src[i] ? 0 : 1;
  // the inside of a hollow head is ringed by a thin outline on all four
  // sides; the gap between a flag and its stem or a beam is not (a head or
  // the beam is thick), and neither is a gap in a heavy glyph
  const thinRing = (labels, c) => {
    if (!(c.x1 - c.x0 + 1 >= 0.45 * ss && c.x1 - c.x0 + 1 <= 1.5 * ss && c.y1 - c.y0 + 1 <= 0.75 * ss && c.y1 - c.y0 + 1 >= 0.2 * ss)) return false;
    const xm = Math.round((c.x0 + c.x1) / 2), ym = Math.round((c.y0 + c.y1) / 2);
    const lim = 0.58 * ss;
    const cap = 1.2 * ss;
    const run = (x, y, dx, dy) => { let n = 0; while (x >= 0 && y >= 0 && x < w && y < h && src[y * w + x] && n <= cap) { n++; x += dx; y += dy; } return n; };
    let top = -1, bot = -1;
    for (let y = c.y0; y <= c.y1; y++) if (labels[y * w + xm] === c.id) { if (top < 0) top = y; bot = y; }
    if (top < 0) return false;
    let lft = -1, rgt = -1;
    for (let x = c.x0; x <= c.x1; x++) if (labels[ym * w + x] === c.id) { if (lft < 0) lft = x; rgt = x; }
    if (lft < 0) return false;
    const up = run(xm, top - 1, 0, -1), dn = run(xm, bot + 1, 0, 1), l = run(lft - 1, ym, -1, 0), r = run(rgt + 1, ym, 1, 0);
    return up >= 1 && dn >= 1 && l >= 1 && r >= 1 && up <= lim && dn <= lim && l <= 1.1 * ss && r <= 1.1 * ss;
  };
  {
    const { labels, comps } = labelComponents(inv, { four: true });
    const maxW = 1.5 * ss, maxH = 1.0 * ss, maxA = 0.6 * ss * ss;
    const fill = new Uint8Array(comps.length + 1);
    for (const c of comps) {
      if (!inner(c)) continue;
      const cw = c.x1 - c.x0 + 1, ch = c.y1 - c.y0 + 1;
      if (opts.thinRing && !thinRing(labels, c)) continue;
      // wide, flat insides: hollow heads of older engravings run up to ~1.9
      // spaces wide (taller regions that wide are gaps between lines and stems)
      if (!(ch <= maxH && c.area <= maxA && c.area >= 2)) continue;
      // a narrow, upright gap is the paper between two glyphs closed by staff
      // lines (an accidental and its head), not a head's inside (flat or tilted)
      if (cw < 0.5 * ss && ch > 1.4 * cw && ch >= 0.5 * ss) continue;
      const flat = cw >= 0.4 * ss && cw >= ch && ch <= 0.65 * ss;
      if (cw <= maxW) {
        fill[c.id] = 1;
        if (opts.walls !== false && flat && headTall(labels, c)) restore(labels, c);
      } else if (cw <= 1.9 * ss && ch <= 0.6 * ss && headTall(labels, c)) {
        fill[c.id] = 1;
        if (opts.walls !== false) restore(labels, c);
      }
    }
    for (let i = 0; i < w * h; i++) if (labels[i] && fill[labels[i]]) o[i] = 1;
  }
  if (opts.close === false) return out;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    inv.data[i] = (src[i] || (x > 0 && src[i - 1]) || (x < w - 1 && src[i + 1]) || (y > 0 && src[i - w]) || (y < h - 1 && src[i + w])) ? 0 : 1;
  }
  const { labels, comps } = labelComponents(inv, { four: true });
  const maxW = 1.9 * ss, maxH = 0.65 * ss, maxA = 0.5 * ss * ss, minA = 0.03 * ss * ss;
  for (const c of comps) {
    const cw = c.x1 - c.x0 + 1, ch = c.y1 - c.y0 + 1;
    if (!(inner(c) && cw <= maxW && ch <= maxH && cw >= (opts.aspect ?? 3) * ch && cw >= 0.5 * ss && c.area <= maxA && c.area >= minA)) continue;
    if (!headTall(labels, c)) continue;
    // the hole and its 1-px rim (the dilation shrank it)
    for (let y = Math.max(1, c.y0 - 1); y <= Math.min(h - 2, c.y1 + 1); y++) for (let x = Math.max(1, c.x0 - 1); x <= Math.min(w - 2, c.x1 + 1); x++) {
      const i = y * w + x;
      if (labels[i] === c.id || labels[i - 1] === c.id || labels[i + 1] === c.id || labels[i - w] === c.id || labels[i + w] === c.id) o[i] = 1;
    }
    if (opts.walls !== false) restore(labels, { ...c, x0: c.x0, x1: c.x1 });
  }
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

// Head-wide column windows of a wide blob (component c of the opened image):
// the densest window (column ink counts) is a head; a second, nearly as dense
// window beside it is the other head of a second.  Returns the windows, the
// mean column height of the best one and of the columns outside it.
function headWindows(c, labels, w, sp, R, B) {
  const n = c.x1 - c.x0 + 1;
  const ext = new Float64Array(n), ysum = new Float64Array(n);
  for (let y = c.y0; y <= c.y1; y++) for (let x = c.x0; x <= c.x1; x++) if (labels[y * w + x] === c.id) { ext[x - c.x0]++; ysum[x - c.x0] += y; }
  const cyOf = (a, b) => { let s = 0, k = 0; for (let i = a; i < b; i++) { s += ysum[i]; k += ext[i]; } return k ? s / k : 0; };
  // an accidental fused with its head through the paper between them, closed above and below
  // by staff lines and filled with the holes: columns with (almost) no ink of their own there.
  // The head is the part right of such a gap (accidentals stand left of their heads) when that
  // part is head-wide, the part left of it holds an accidental's stroke (taller than a time-signature
  // digit, shorter than a stem or barline) and the gap is wider than the one between two digits
  // (1 and 2 of 12/8); the part left of it is left out
  let cut = 0;
  if (R) {
    const own = new Float64Array(n);
    for (let i = 0; i < n; i++) for (let y = c.y0; y <= c.y1; y++) if (labels[y * w + c.x0 + i] === c.id && R.data[y * w + c.x0 + i]) own[i]++;
    for (let i = n - 1; i > 0; i--) {
      if (own[i] > 0.1 * sp) continue;
      let j = i; while (j > 0 && own[j - 1] <= 0.1 * sp) j--;
      if (j > 0 && n - 1 - i >= 0.8 * sp) {
        const tall = wallRun(B, c.x0 - 0.6 * sp, c.x0 + j - 1, (c.y0 + c.y1) / 2, sp).len;
        if (tall < 2.2 * sp || tall > 3.3 * sp || i - j + 1 < 0.2 * sp) break;
        for (let k = 0; k <= i; k++) { ext[k] = 0; ysum[k] = 0; }
        cut = i + 1;
        break;
      }
      i = j;
    }
  }
  // a sharp / natural fused with its head: a narrow run of columns much taller
  // than a head next to head-high columns -> leave those columns out
  let headCols = 0;
  for (let i = 0; i < n; i++) if (ext[i] >= 0.6 * sp && ext[i] <= 1.3 * sp) headCols++;
  if (headCols >= 0.8 * sp) {
    for (let i = 0; i < n;) {
      if (ext[i] < 1.35 * sp) { i++; continue; }
      let j = i; while (j < n && ext[j] >= 1.35 * sp) j++;
      if (j - i <= 0.8 * sp) for (let k = i; k < j; k++) { ext[k] = 0; ysum[k] = 0; }
      i = j;
    }
  }
  const hw = Math.max(3, Math.round(1.15 * sp));
  const best = (a, b) => {
    const ww = Math.min(hw, b - a);
    let s = 0;
    for (let i = a; i < a + ww; i++) s += ext[i];
    let bs = s, ba = a;
    for (let i = a + 1; i + ww <= b; i++) { s += ext[i + ww - 1] - ext[i - 1]; if (s > bs) { bs = s; ba = i; } }
    return { a: ba, b: ba + ww, mean: bs / ww };
  };
  const m = best(0, n);
  if (m.mean < 0.6 * sp) return { cols: [], peak: m.mean, rest: 0, cut };
  const cols = [[m.a, m.b]];
  let rs = 0;
  for (let i = cut; i < n; i++) if (i < m.a || i >= m.b) rs += ext[i];
  const rest = n - cut > m.b - m.a ? rs / (n - cut - (m.b - m.a)) : 0;
  for (const [a, b] of [[cut, m.a], [m.b, n]]) {
    if (b - a < 0.9 * sp) continue;
    // the two heads of a second sit a staff position apart; an accidental
    // fused with its head sits level with it
    const t = best(a, b);
    if (t.mean >= 0.75 * m.mean && t.b - t.a >= 0.9 * sp && Math.abs(cyOf(t.a, t.b) - cyOf(m.a, m.b)) >= 0.25 * sp) cols.push([t.a, t.b]);
  }
  return { cols: cols.map(([a, b]) => [c.x0 + a, c.x0 + b]).sort((p, q) => p[0] - q[0]), peak: m.mean, rest, cut };
}

// Longest vertical ink run through row y (+-0.3 sp) in columns [xa, xb]:
// { len, up, down } in px (up / down = reach above / below y).
function wallRun(R, xa, xb, y, sp) {
  const { width: w, height: h, data } = R;
  const yc = Math.round(y);
  let best = { len: 0, up: 0, down: 0 };
  for (let x = Math.max(0, Math.round(xa)); x <= Math.min(w - 1, Math.round(xb)); x++) {
    let y0 = -1;
    for (let d = 0; d <= Math.round(0.3 * sp) && y0 < 0; d++) {
      if (yc - d >= 0 && data[(yc - d) * w + x]) y0 = yc - d; else if (yc + d < h && data[(yc + d) * w + x]) y0 = yc + d;
    }
    if (y0 < 0) continue;
    let a = y0, b = y0;
    while (a > 0 && data[(a - 1) * w + x]) a--;
    while (b < h - 1 && data[(b + 1) * w + x]) b++;
    if (b - a + 1 > best.len) best = { len: b - a + 1, up: y - a, down: b - y };
  }
  return best;
}

// A hole walled by two long verticals (barline + stem, two stems) and closed
// by staff lines is not a head.  The one exception is a unison of two voices:
// one head with the up stem on its right and the down stem on its left.
function twoTallWalls(R, xa, xb, y, sp) {
  const wid = xb - xa, lim = 1.8 * sp;
  const L = wallRun(R, xa, xa + 0.3 * wid, y, sp), Rt = wallRun(R, xb - 0.3 * wid, xb, y, sp);
  if (L.len <= lim || Rt.len <= lim) return false;
  const unison = Rt.up > 1.5 * sp && Rt.down < 0.9 * sp && L.down > 1.5 * sp && L.up < 0.9 * sp;
  return !unison;
}

// A head's inside is empty when its core is mostly paper; a ledger line (left in R) can run
// straight through the middle of a hollow head, so thin windows just above and below count too.
function hollowCore(IR, IB, xm, yc, sp) {
  const at = IR.frac(xm - 0.18 * sp, yc - 0.12 * sp, xm + 0.18 * sp, yc + 0.12 * sp) < 0.5;
  if (at && IB.frac(xm - 0.3 * sp, yc - 0.2 * sp, xm + 0.3 * sp, yc + 0.2 * sp) < 0.75) return true;
  const thin = (dy) => IR.frac(xm - 0.18 * sp, yc + dy - 0.06 * sp, xm + 0.18 * sp, yc + dy + 0.06 * sp) < 0.35;
  return thin(-0.22 * sp) && thin(0.22 * sp);
}

// A head on a ledger line (|p| >= 6, even): the ledger, left in R, runs through its middle and
// fills the core test. Ink over the head's box with the ledger's rows left out: about 0.9 for a
// filled head, 0.5-0.65 for a hollow one on clean pages (coverage notes family); on a degraded
// page the values run together, so detectHeads only calls a head hollow when it is clearly lighter
// than the page's filled ledger heads.
function ledgerInkOf(R, xm, yc, sp, lt) {
  const { width: w, height: h, data } = R, skip = Math.ceil(lt / 2) + 1;
  let ink = 0, n = 0;
  for (let dy = -Math.round(0.35 * sp); dy <= Math.round(0.35 * sp); dy++) {
    if (Math.abs(dy) <= skip) continue;
    const y = Math.round(yc + dy); if (y < 0 || y >= h) continue;
    for (let dx = -Math.round(0.4 * sp); dx <= Math.round(0.4 * sp); dx++) { const x = Math.round(xm + dx); if (x < 0 || x >= w) continue; n++; ink += data[y * w + x]; }
  }
  return n ? ink / n : null;
}

function detectHeads(B, R, staves, ss, lt, opts = {}) {
  let F = fillHoles(B, R, ss, lt);
  // thin-walled hollow heads of old prints break open in B; their outline
  // stays closed on a lenient threshold: fill those insides too
  if (opts.lenient) F = fillHoles(opts.lenient, F, ss, lt, { close: false, thinRing: true });
  const O1 = openRuns(F, Math.max(3, Math.round(0.55 * ss)), true);
  const O = openRuns(O1, Math.max(3, Math.round(0.42 * ss)), false);
  const { labels, comps } = labelComponents(O);
  const IR = integral(R), IB = integral(B);
  const heads = [], beams = [], stacked = [];
  // the page's typical head height (blobs a head wide, up to a head and a half tall), in spaces
  const hts = [];
  for (const c of comps) {
    const bw = c.x1 - c.x0 + 1, bh = c.y1 - c.y0 + 1;
    if (bw >= 0.9 * ss && bw <= 1.6 * ss && bh >= 0.7 * ss && bh <= 1.6 * ss && c.area >= 0.6 * bw * bh) hts.push(bh / ss);
  }
  hts.sort((a, b) => a - b);
  const headH = hts.length >= 8 ? hts[hts.length >> 1] : 1, thick = headH > 1.15;
  for (const c of comps) {
    const bw = c.x1 - c.x0 + 1, bh = c.y1 - c.y0 + 1;
    // cue-size heads (about 0.7 of a head: a cue part over rests, small grace notes) are smaller
    // than the opening leaves of a full head; kept when solid, and marked small
    const small = bw < 0.8 * ss && bw >= 0.55 * ss && bh >= 0.45 * ss && bh <= 0.75 * ss && c.area >= 0.85 * bw * bh;
    if (!small && (bw < 0.8 * ss || bh < 0.5 * ss)) continue;
    const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
    const sp0 = staffPos(staves, cx, cy);
    if (!sp0 || Math.abs(sp0.p) > 16) continue;
    const sp = sp0.sp;
    const fillRatio = c.area / (bw * bh);
    // wide blobs: a head fused with its accidental (filled flat / natural bowl)
    // or a second (two heads side by side): take the head-wide column windows
    // with the most ink; a flat band with no head-shaped bump is a beam
    let cols = null;
    if (bw > 1.75 * sp && bh >= 0.6 * sp && bh <= 5.5 * sp) {
      const win = headWindows(c, labels, O.width, sp, R, B);
      // (an accidental cut off at its gap no longer counts towards the width)
      const bw1 = bw - win.cut;
      if (win.cols.length && (bw1 <= 2.4 * sp || (bw1 <= 3.6 * sp && win.peak >= 1.25 * win.rest))) cols = win.cols;
    }
    if (!cols) {
      if (bw > 2.4 * sp) {
        if (bh < 1.6 * sp) beams.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1, staff: sp0.st.index });
        continue;
      }
      if (fillRatio < 0.45 || bh > 5.5 * sp) continue;
      // columns: a second (two heads offset sideways) makes the blob ~2 heads wide
      cols = bw > 1.75 * sp ? [[c.x0, c.x0 + bw / 2], [c.x0 + bw / 2, c.x1 + 1]] : [[c.x0, c.x1 + 1]];
    }
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
      // heads stacked a third apart; on a page whose heads come out thick (heavy scans, the page's
      // typical head over 1.15 spaces tall) a single head reaches 1.5 spaces and is still one
      const k = Math.max(1, thick ? Math.round((hh - (headH - 1) * sp) / (0.95 * sp)) : Math.round(hh / (0.95 * sp)));
      if (k > 4) continue;
      const step = hh / k;
      // a stack of hollow heads (whole- / half-note chord): equal steps put centres on the
      // outlines between the heads and only the top head survives. The heads sit where the inside
      // is empty and closed on both sides: those positions are returned separately (stacked), for
      // assemble.js to add to a chord found there, right of the staff's header
      const wcol = (xb - xa) / sp;
      if (k >= 2 && wcol >= 1.1 && wcol <= 1.9) {
        const pa = staffPos(staves, xm, ya + 0.4 * sp), pb = staffPos(staves, xm, yb - 0.4 * sp);
        const ring = (yc) => IR.frac(xa, yc - 0.15 * sp, xa + 0.22 * sp, yc + 0.15 * sp) > 0.25 && IR.frac(xb - 0.22 * sp, yc - 0.15 * sp, xb, yc + 0.15 * sp) > 0.25;
        if (pa && pb && pa.st === pb.st) {
          const hits = [];
          for (let p = Math.round(pa.p); p >= Math.round(pb.p); p--) {
            const yc = pa.st.yAt(2, xm) - (p * pa.sp) / 2;
            if (hollowCore(IR, IB, xm, yc, sp) && ring(yc) && !hits.some(q => Math.abs(q.y - yc) < 0.9 * sp)) hits.push({ y: yc, p });
          }
          if (hits.length >= 2) for (const q of hits) stacked.push({ x: xm, y: q.y, staff: pa.st.index, p: q.p, sp: pa.sp, kind: 'hollow', score: 1, w: xb - xa, blob: c.id, x0: Math.round(xa), x1: Math.round(xb), stacked: true });
        }
      }
      for (let i = 0; i < k; i++) {
        const y = ya + step * (i + 0.5);
        const ps = staffPos(staves, xm, y);
        if (!ps) continue;
        const p = Math.round(ps.p);
        const ycen = ps.st.yAt(2, xm) - (p * ps.sp) / 2;
        const core = IR.frac(xm - 0.18 * sp, ycen - 0.12 * sp, xm + 0.18 * sp, ycen + 0.12 * sp);
        const coreB = IB.frac(xm - 0.3 * sp, ycen - 0.2 * sp, xm + 0.3 * sp, ycen + 0.2 * sp);
        // a hollow head on a ledger line (|p| >= 6, even) has the ledger (left in R) through its
        // middle: its inside is then read just above and below the line
        const hollow = core < 0.5 && coreB < 0.75;
        // on a ledger line the core test cannot see the inside: decided for the page below
        const ledgerInk = !hollow && !small && Math.abs(p) >= 6 && p % 2 === 0 ? ledgerInkOf(R, xm, ycen, sp, lt) : null;
        const wid = xb - xa;
        if (wid < 0.75 * sp && !small) continue;
        // a hole walled by two long verticals (barline + stem, two stems) and
        // closed by staff lines is not a head: a head has at most one stem
        if (hollow && twoTallWalls(R, xa, xb, ycen, sp)) continue;
        heads.push({ x: xm, y: ycen, staff: ps.st.index, p, sp, kind: hollow ? 'hollow' : 'filled', ledgerInk, score: 1, w: wid, blob: c.id,
          x0: Math.round(xa), x1: Math.round(xb), ...(small ? { small: true } : {}) });
      }
    }
  }
  // hollow heads on ledger lines: under 0.7, and 0.1 under the lightest clearly filled one (0.75 or
  // more; a scan's hollow ledger heads read 0.61-0.68, its filled ones 0.79-0.94, so a cut-off below
  // 0.66 took the hollow ones for the page's filled ones). A degraded page whose values run
  // together keeps them filled
  const darkL = heads.filter(h => h.ledgerInk != null && h.ledgerInk >= 0.75).map(h => h.ledgerInk);
  const lim = Math.min(0.7, darkL.length ? Math.min(...darkL) - 0.1 : 0.66);
  for (const h of heads) { if (h.ledgerInk != null && h.ledgerInk < lim) h.kind = 'hollow'; delete h.ledgerInk; }
  // self-calibrated width floor: engravings differ in head proportions
  // (LilyPond ~1.3 spaces, some 1900s hymnals ~1.0), so the floor follows the
  // page's median head width, within [0.78, 0.9] spaces
  const rel = heads.filter(h => !h.small).map(h => h.w / h.sp).sort((a, b) => a - b);
  const headW = rel.length >= 8 ? rel[rel.length >> 1] : 1.3;
  const minW = Math.min(0.9, Math.max(0.78, 0.8 * headW));
  // dedupe
  heads.sort((a, b) => a.x - b.x);
  const out = [];
  for (const h of heads) {
    if (h.small || h.w < minW * h.sp) continue;
    if (!out.some(o => o.staff === h.staff && o.p === h.p && Math.abs(o.x - h.x) < 0.6 * h.sp)) out.push(h);
  }
  // cue-size heads after the full-size ones, clear of them (a small blob beside a head is a piece of
  // an accidental, a dot or a flag)
  // only on pages whose full heads are clearly wider (modern engravings, about 1.2
  // spaces and up): on narrow-headed old prints a worn full head reads as small
  if (headW >= 1.12) for (const h of heads) {
    if (h.small && !out.some(o => o.staff === h.staff && Math.abs(o.p - h.p) <= 8 && Math.abs(o.x - h.x) < 1.2 * h.sp)) out.push(h);
  }
  out.sort((a, b) => a.x - b.x);
  return { heads: out, beams, opened: O, headW, stacked };
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
  // (a scan's ledgers come out thicker than its staff lines measure, and thicker still where
  // they run into the head: up to about a quarter space)
  const maxThick = Math.max(2, Math.round(1.6 * lt + 1), Math.round(0.28 * sp));
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
  // the ends of a ledger reaching past a head on it (the head hides the middle)
  const ends = (yq) => {
    const reach = Math.round(1.25 * sp), inner = Math.round(0.45 * sp);
    let left = 0, right = 0;
    for (let x = xm - reach; x <= xm + reach; x++) {
      if (Math.abs(x - xm) <= inner || !thinAt(x, yq)) continue;
      if (x < xm) left++; else right++;
    }
    return { left, right };
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
      if (n >= 0.8 * sp && left >= 2 && right >= 2) continue;
      // a lower head of the same chord sits on this ledger: only its two
      // ends show, on both sides
      const e = ends(yq);
      if (e.left < 2 || e.right < 2 || e.left + e.right < Math.max(4, 0.4 * sp)) return false;
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
      // same column, or the other head of a second (same blob, a position apart)
      const join = cur && (hd.x - cur.xs[cur.xs.length - 1] < 0.7 * hd.sp ||
        (opts.sides && cur.heads.some(o => o.blob === hd.blob && Math.abs(o.p - hd.p) === 1 && hd.x - o.x <= 1.6 * hd.sp)));
      if (join) { cur.heads.push(hd); cur.xs.push(hd.x); }
      else { cur = { heads: [hd], xs: [hd.x], staff: +k }; chords.push(cur); }
    }
  }
  const ink = (x, y) => x >= 0 && y >= 0 && x < w && y < h && data[y * w + x];
  const stems = (c) => {
    c.heads.sort((a, b) => a.y - b.y);
    const sp = c.heads[0].sp;
    const top = c.heads[0], bot = c.heads[c.heads.length - 1];
    const xa = Math.round(Math.min(...c.xs) - 0.85 * sp), xb = Math.round(Math.max(...c.xs) + 0.85 * sp);
    const maxGap = Math.max(2, Math.round((opts.stemGap ?? 0.4) * sp));
    // stems sit right of the heads going up and left going down; a stroke on
    // the other side is an accidental's (flat: up on the left, natural: up on
    // the left and down on the right)
    const xl = Math.min(...c.xs) + 0.1 * sp, xr = Math.max(...c.xs) - 0.1 * sp;
    let up = 0, upX = -1, down = 0, downX = -1, upIll = 0, downIll = 0;
    for (let x = xa; x <= xb; x++) {
      // upward run starting inside the top head band
      let y0 = -1;
      for (let y = Math.round(top.y + 0.3 * sp); y >= Math.round(top.y - 0.5 * sp); y--) if (ink(x, y)) { y0 = y; }
      if (y0 >= 0) {
        let yt = y0, gap = 0;
        for (let y = y0 - 1; y >= 0; y--) { if (ink(x, y)) { yt = y; gap = 0; } else if (++gap > maxGap) break; }
        const len = (top.y - yt) / sp;
        if (opts.sides && x < xl) { if (len > upIll) upIll = len; }
        else if (len > up) { up = len; upX = x; c.upEnd = yt; }
      }
      y0 = -1;
      for (let y = Math.round(bot.y - 0.3 * sp); y <= Math.round(bot.y + 0.5 * sp); y++) if (ink(x, y)) { y0 = y; }
      if (y0 >= 0) {
        let yb = y0, gap = 0;
        for (let y = y0 + 1; y < h; y++) { if (ink(x, y)) { yb = y; gap = 0; } else if (++gap > maxGap) break; }
        const len = (yb - bot.y) / sp;
        if (opts.sides && x > xr) { if (len > downIll) downIll = len; }
        else if (len > down) { down = len; downX = x; c.downEnd = yb; }
      }
    }
    c.up = up >= minLen ? up : 0; c.down = down >= minLen ? down : 0;
    c.accidental = false;
    if (opts.sides) {
      // only wrong-side strokes, or two short strokes both ways (a sharp):
      // an accidental, not a note
      const ill = !c.up && !c.down && Math.max(upIll, downIll) >= minLen;
      const sharp = c.heads.length === 1 && c.up && c.down && Math.max(c.up, c.down) < (opts.sharpLen ?? 2.2);
      if (ill || sharp) { c.accidental = true; c.up = 0; c.down = 0; }
    }
    c.upX = upX; c.downX = downX;
    c.x = c.xs.reduce((a, b) => a + b, 0) / c.xs.length;
  };
  // heads of one column far apart with nothing between them (a rest's flag
  // blob over a low note, a lyric glyph under a head) are not one chord: when
  // the column has a stem one way only, each such group is read on its own
  // (two voices sharing a column, stems up and down, stay one chord)
  // (a faint stem may break where it crosses a staff line: mostly ink, no
  // long gap, is enough)
  const linked = (a, b, xa, xb, sp) => {
    const ya = Math.round(a.y + 0.3 * sp), yb = Math.round(b.y - 0.3 * sp), gapMax = Math.max(2, Math.round(0.6 * sp));
    for (let x = Math.round(xa); x <= Math.round(xb); x++) {
      let gap = 0, n = 0, ok = true;
      for (let y = ya; y <= yb && ok; y++) { if (ink(x, y)) { gap = 0; n++; } else if (++gap > gapMax) ok = false; }
      if (ok && n >= 0.7 * (yb - ya + 1)) return true;
    }
    return false;
  };
  for (let i = 0; i < chords.length; i++) {
    const c = chords[i];
    stems(c);
    if (c.heads.length < 2 || (c.up && c.down)) continue;
    const hs = c.heads, sp = hs[0].sp;
    const xa = Math.min(...c.xs) - 0.85 * sp, xb = Math.max(...c.xs) + 0.85 * sp;
    const parts = [[hs[0]]];
    for (let k = 1; k < hs.length; k++) {
      if (hs[k].y - hs[k - 1].y > 2.0 * sp && !linked(hs[k - 1], hs[k], xa, xb, sp)) parts.push([hs[k]]);
      else parts[parts.length - 1].push(hs[k]);
    }
    if (parts.length < 2) continue;
    // a detached hollow head stays (a stemless half note of a second voice
    // drawn on the chord's stem); black heads need a stem of their own
    for (let k = parts.length - 1; k > 0; k--) {
      if (parts[k].every(hd => hd.kind === 'hollow') || parts[k - 1].every(hd => hd.kind === 'hollow')) parts.splice(k - 1, 2, parts[k - 1].concat(parts[k]));
    }
    if (parts.length < 2) continue;
    const sub = parts.map(p => ({ heads: p, xs: p.map(hd => hd.x), staff: c.staff }));
    sub.forEach(stems);
    // a group with no stem of its own and no glyph strokes is a head whose
    // stem was lost (blur, faint print): it stays on the column's stem
    if (sub.some(p => !p.up && !p.down && !p.accidental)) { stems(c); continue; }
    chords.splice(i, 1, ...sub);
    i += sub.length - 1;
  }
  for (const c of chords) {
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
    for (const hd of c.heads) hd.stem = { dir: hd.stemDir, upX: c.upX, downX: c.downX, up: c.up, down: c.down };
  }
  return chords;
}

module.exports.chordStems = chordStems;
