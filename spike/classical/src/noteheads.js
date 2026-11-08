'use strict';
// Notehead detection constrained to staff positions.
//   For every staff, every staff position p (0 = middle line, units of half a
//   staff space) and every column x, cheap box-sum features are evaluated on
//   the original binary (B, staff lines kept) and the staff-removed binary (R):
//   filled heads  : solid core, wide enough, closed top/bottom edges, not a beam
//   hollow heads  : white core, ink walls left/right belonging to one
//                   connected outline, closed top/bottom, no accidental strokes
//   |p| >= 6      : the required ledger lines must be present
// then non-maximum suppression across x, p and staves.  Stem verification is
// done in stems.js (filled heads and half notes need one).
const { integral } = require('./cc');

const DEFAULTS = {
  filledMin: 0.78,       // core fill (B) for filled heads
  sideMin: 0.45,         // filled: ink at +-0.4..0.55 sp on the centre row (B)
  edgeMin: 0.45,         // top/bottom edge band fill (R)
  beamSide: 0.65,        // both sides this full (R) -> beam, reject
  hollowCoreMax: 0.3,
  hollowCoreMaxOnLine: 0.45, // line rows excluded, but only ~1-2 px hole rows remain at 150-200 dpi
  hollowWallMin: 0.4,
  hollowEdgeMin: 0.18,
  strokeMin: 0.12,       // accidental stroke detector (thin vertical ink above/below walls)
  strokeMax: 0.62,
  wholeOuterMin: 0.45,
  ledgerMin: 0.55,
  pRange: 13,
  clefZone: 3.0,         // staff spaces after staff start where no note can be
  sameRowNMS: 1.1,
  tiltMin: 0.25,
  minInk: 0.28,          // fast reject threshold (ink fraction of the 1.2 x 0.9 sp head box)
  wallsConnected: false, // require both walls in one component of R (breaks when staff removal cuts the outline)       // sp: two heads at the same staff position closer than this -> keep best
};

function headerExclusions(st, comps, ss, o) {
  // returns [x0] start column for the search plus a list of excluded x-ranges
  let x0 = Math.round(st.left + o.clefZone * ss);
  const ranges = [];
  if (!comps) return { x0, ranges };
  const yTop = st.yAt(0, st.left), yBot = st.yAt(4, st.left), yMid = st.yAt(2, st.left);
  for (const c of comps) {
    const hgt = c.y1 - c.y0 + 1, wid = c.x1 - c.x0 + 1;
    if (c.y1 < yTop - 2 * ss || c.y0 > yBot + 2 * ss) continue;
    // clef / brace: tall component starting near the staff start
    if (c.x0 < st.left + 2.0 * ss && c.x1 < st.left + 7 * ss && c.x1 > st.left && hgt >= 2.5 * ss) {
      x0 = Math.max(x0, Math.round(c.x1 + 0.4 * ss));
      continue;
    }
    // time signature (C or digits): ~2 ss tall, 1-2.2 ss wide, centred on the
    // middle line or in the upper / lower half of the staff, early in the staff
    if (c.x0 < st.left + 25 * ss && hgt >= 1.6 * ss && hgt <= 2.5 * ss && wid >= 0.9 * ss && wid <= 2.4 * ss) {
      const cy = (c.y0 + c.y1) / 2;
      const atMid = Math.abs(cy - yMid) < 0.35 * ss;
      const upper = Math.abs(cy - (yTop + yMid) / 2) < 0.35 * ss;
      const lower = Math.abs(cy - (yMid + yBot) / 2) < 0.35 * ss;
      if (atMid || upper || lower) {
        // digits come in stacked pairs; C is alone at the middle
        const partner = upper || lower ? comps.some(d => d !== c && Math.abs(d.x0 - c.x0) < 0.6 * ss &&
          Math.abs((d.y0 + d.y1) / 2 - (upper ? (yMid + yBot) / 2 : (yTop + yMid) / 2)) < 0.4 * ss) : true;
        if (partner) ranges.push([c.x0 - 0.2 * ss, c.x1 + 0.2 * ss]);
      }
    }
  }
  return { x0, ranges };
}

function detectNoteheads(B, R, staves, ss, opts = {}, cc = null) {
  const o = { ...DEFAULTS, ...opts };
  const IB = integral(B), IR = integral(R);
  const comps = cc ? cc.comps : null, labels = cc ? cc.labels : null;
  const W = B.width;
  const cands = [];
  for (const st of staves) {
    const { x0, ranges } = headerExclusions(st, comps, ss, o);
    const x1 = st.right;
    for (let p = -o.pRange; p <= o.pRange; p++) {
      const row = [];
      for (let x = x0; x <= x1; x++) {
        if (ranges.length && ranges.some(r => x >= r[0] && x <= r[1])) { row.push(null); continue; }
        const sp = (st.dense[4][x] - st.dense[0][x]) / 4;
        const yc = st.dense[2][x] - (p * sp) / 2;
        row.push(classify(IB, IR, R, labels, W, x, yc, sp, p, o, st.dense[0][x], st.dense[4][x]));
      }
      // 1-D NMS along x: plateau of same kind -> best (centre on ties)
      for (let i = 0; i < row.length; i++) {
        const c = row[i];
        if (!c) continue;
        let j = i;
        while (j + 1 < row.length && row[j + 1] && row[j + 1].kind === c.kind) j++;
        let best = i;
        for (let k = i; k <= j; k++) if (row[k].score > row[best].score + 1e-9) best = k;
        const mid = (i + j) >> 1;
        const pick = Math.abs(row[mid].score - row[best].score) < 0.02 ? row[mid] : row[best];
        if (Math.abs(p) >= 6 && !ledgersOK(IB, st, p, pick.x, ss, o)) { i = j; continue; }
        cands.push({ ...pick, staff: st.index, p, runLen: j - i + 1 });
        i = j;
      }
    }
  }
  // global NMS: overlapping heads keep best; prefer nearer staff for duplicates
  cands.sort((a, b) => (b.score - a.score) || (Math.abs(a.p) - Math.abs(b.p)));
  const kept = [];
  for (const c of cands) {
    const clash = kept.some(k => {
      const dx = Math.abs(k.x - c.x), dy = Math.abs(k.yc - c.yc);
      if (dx < 0.75 * c.sp && dy < 0.75 * c.sp) return true;
      // same row (dot after a head, head+dot gap, etc.)
      return dy < 0.3 * c.sp && dx < o.sameRowNMS * c.sp && (c.kind === 'hollow' || k.kind === c.kind);
    });
    if (!clash) kept.push(c);
  }
  return kept.map(c => ({ x: c.x, y: c.yc, kind: c.kind, score: c.score, staff: c.staff, p: c.p, sp: c.sp, wholeLike: c.wholeLike, f: c.f }));
}

function classify(IB, IR, R, labels, W, x, yc, sp, p, o, yTop = -1, yBot = -1) {
  // fast reject: not enough ink in the head box for any notehead (most positions)
  if (!o.explain && IB.frac(x - 0.6 * sp, yc - 0.45 * sp, x + 0.6 * sp, yc + 0.45 * sp) < o.minInk) return null;
  const f = {
    core: IB.frac(x - 0.38 * sp, yc - 0.28 * sp, x + 0.38 * sp, yc + 0.28 * sp),
    sideL: IR.frac(x - 0.55 * sp, yc - 0.1 * sp, x - 0.4 * sp, yc + 0.1 * sp),
    sideR: IR.frac(x + 0.4 * sp, yc - 0.1 * sp, x + 0.55 * sp, yc + 0.1 * sp),
    // vertical bar test: solid ink 1.6-2.2 sp above AND below (barline, not a head)
    vbar: Math.min(IR.frac(x - 0.15 * sp, yc - 2.2 * sp, x + 0.15 * sp, yc - 1.6 * sp), IR.frac(x - 0.15 * sp, yc + 1.6 * sp, x + 0.15 * sp, yc + 2.2 * sp)),
    top: IR.frac(x - 0.25 * sp, yc - 0.40 * sp, x + 0.25 * sp, yc - 0.22 * sp),
    bot: IR.frac(x - 0.25 * sp, yc + 0.22 * sp, x + 0.25 * sp, yc + 0.40 * sp),
    left: IR.frac(x - 1.05 * sp, yc - 0.12 * sp, x - 0.75 * sp, yc + 0.12 * sp),
    right: IR.frac(x + 0.75 * sp, yc - 0.12 * sp, x + 1.05 * sp, yc + 0.12 * sp),
  };
  const rej = (why) => (o.explain ? { kind: null, why, f } : null);
  if (f.vbar >= 0.85) return rej('vbar');
  // ink columns spanning the whole staff (top to bottom line) = barline
  const spanFrac = (xa, xb) => (yTop >= 0 ? IR.frac(xa, yTop, xb, yBot + 1) : 0);
  f.span = Math.max(spanFrac(x - 0.62 * sp, x - 0.32 * sp), spanFrac(x - 0.15 * sp, x + 0.15 * sp), spanFrac(x + 0.32 * sp, x + 0.62 * sp));
  if (f.span >= 0.75) return rej('barline');
  if (f.core >= o.filledMin && f.sideL >= o.sideMin && f.sideR >= o.sideMin && f.top >= o.edgeMin && f.bot >= o.edgeMin &&
      !(f.left >= o.beamSide && f.right >= o.beamSide)) {
    return { kind: 'filled', score: f.core, x, yc, sp, f };
  }
  // hollow: core avoiding the centre row when the head sits on a (ledger) line
  const onLine = (p & 1) === 0;
  const lt = Math.max(1, 0.1 * sp);
  f.hcore = onLine
    ? (IR.frac(x - 0.15 * sp, yc - 0.2 * sp, x + 0.15 * sp, yc - lt - 0.5) + IR.frac(x - 0.15 * sp, yc + lt + 0.5, x + 0.15 * sp, yc + 0.2 * sp)) / 2
    : IR.frac(x - 0.15 * sp, yc - 0.1 * sp, x + 0.15 * sp, yc + 0.1 * sp);
  if (f.hcore > (onLine ? o.hollowCoreMaxOnLine : o.hollowCoreMax)) return rej('hcore');
  f.wallL = IR.frac(x - 0.62 * sp, yc - 0.12 * sp, x - 0.32 * sp, yc + 0.12 * sp);
  f.wallR = IR.frac(x + 0.32 * sp, yc - 0.12 * sp, x + 0.62 * sp, yc + 0.12 * sp);
  if (f.wallL < o.hollowWallMin || f.wallR < o.hollowWallMin) return rej('walls');
  f.htop = IB.frac(x - 0.22 * sp, yc - 0.62 * sp, x + 0.22 * sp, yc - 0.3 * sp);
  f.hbot = IB.frac(x - 0.22 * sp, yc + 0.3 * sp, x + 0.22 * sp, yc + 0.62 * sp);
  if (f.htop < o.hollowEdgeMin || f.hbot < o.hollowEdgeMin) return rej('edges');
  // accidental strokes: thin vertical ink continuing above/below the walls.
  // A half note may only have right-up or left-down (its stem).
  // stroke = 1..0.3 sp wide set of columns that are (almost) fully inked over the
  // box height; the curved edge of a neighbouring head does not qualify
  const stroke = (x0, x1, y0, y1) => {
    const ya = Math.round(y0), yb = Math.round(y1), hgt = yb - ya;
    if (hgt <= 0) return false;
    let full = 0;
    for (let xx = Math.round(x0); xx < Math.round(x1); xx++) if (IR.sum(xx, ya, xx + 1, yb) >= 0.85 * hgt) full++;
    return full >= 1 && full <= Math.max(2, 0.3 * sp);
  };
  f.lu = stroke(x - 0.66 * sp, x - 0.3 * sp, yc - 1.25 * sp, yc - 0.75 * sp);
  f.ld = stroke(x - 0.66 * sp, x - 0.3 * sp, yc + 0.75 * sp, yc + 1.25 * sp);
  f.ru = stroke(x + 0.3 * sp, x + 0.66 * sp, yc - 1.25 * sp, yc - 0.75 * sp);
  f.rd = stroke(x + 0.3 * sp, x + 0.66 * sp, yc + 0.75 * sp, yc + 1.25 * sp);
  // allowed stroke sets: {}, {ru} (stem up), {ld} (stem down), {ru,ld} (unison head of two voices)
  if (f.lu || f.rd) return rej('strokes');
  // a wall that is part of a long vertical bar (barline) -> not a head
  const vb = (xa, xb) => Math.min(IR.frac(xa, yc - 2.2 * sp, xb, yc - 1.6 * sp), IR.frac(xa, yc + 1.6 * sp, xb, yc + 2.2 * sp));
  f.vbw = Math.max(vb(x - 0.62 * sp, x - 0.32 * sp), vb(x + 0.32 * sp, x + 0.62 * sp));
  if (f.vbw >= 0.3) return rej('wallbar');
  // the hole of a half note is tilted '/', so the outline is thick in its
  // upper-left and lower-right (rejects head+dot gaps, sharps, letters)
  f.ul = IR.frac(x - 0.6 * sp, yc - 0.4 * sp, x - 0.3 * sp, yc - 0.15 * sp);
  f.lr = IR.frac(x + 0.3 * sp, yc + 0.15 * sp, x + 0.6 * sp, yc + 0.4 * sp);
  if (f.ul < o.tiltMin || f.lr < o.tiltMin) return rej('tilt');
  // walls must belong to one connected outline (rejects head+dot gaps, letter pairs)
  if (labels && o.wallsConnected) {
    const la = inkLabel(R, labels, W, x - 0.62 * sp, x - 0.32 * sp, yc, sp);
    const lb = inkLabel(R, labels, W, x + 0.32 * sp, x + 0.62 * sp, yc, sp);
    if (!la || !lb || la !== lb) return rej('connected');
  }
  // whole notes are wider: ink at +-0.65..0.85 sp on the centre row
  const oL = IR.frac(x - 0.88 * sp, yc - 0.1 * sp, x - 0.66 * sp, yc + 0.1 * sp);
  const oR = IR.frac(x + 0.66 * sp, yc - 0.1 * sp, x + 0.88 * sp, yc + 0.1 * sp);
  const wholeLike = oL >= o.wholeOuterMin && oR >= o.wholeOuterMin;
  const score = Math.min(f.wallL, f.wallR, 2 * f.htop, 2 * f.hbot) - f.hcore;
  return { kind: 'hollow', score, x, yc, sp, f, wholeLike };
}

function inkLabel(R, labels, W, x0, x1, yc, sp) {
  const y0 = Math.round(yc - 0.12 * sp), y1 = Math.round(yc + 0.12 * sp);
  for (let y = y0; y <= y1; y++) for (let x = Math.round(x0); x <= Math.round(x1); x++) {
    const i = y * W + x;
    if (i >= 0 && i < labels.length && R.data[i]) return labels[i];
  }
  return 0;
}

// For a head at staff position p (|p| >= 6) every ledger line between the staff
// and the head (and through the head if p is even) must show ink to the left
// and right of the head centre.
function ledgersOK(IB, st, p, x, ss, o) {
  const sgn = Math.sign(p);
  const sp = st.spaceAt(x);
  const lt = Math.max(1, 0.12 * sp);
  for (let q = 6; q <= Math.abs(p); q += 2) {
    const y = st.yAt(2, x) - (sgn * q * sp) / 2;
    const l = IB.frac(x - 0.85 * sp, y - lt - 1, x - 0.62 * sp, y + lt + 1);
    const r = IB.frac(x + 0.62 * sp, y - lt - 1, x + 0.85 * sp, y + lt + 1);
    if (Math.max(l, r) < o.ledgerMin * 0.5 || Math.min(l, r) < 0.15) return false;
  }
  return true;
}

module.exports = { detectNoteheads, classify, DEFAULTS };
