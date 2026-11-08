'use strict';
// Notehead detection constrained to staff positions.
//   For every staff, every staff position p (0 = middle line, units of half a
//   staff space) and every column x, cheap box-sum features are evaluated on
//   the original binary (B, staff lines kept) and the staff-removed binary (R):
//   filled heads  : solid core, closed top/bottom edges, not part of a beam
//   hollow heads  : white core, ink walls left/right, closed top/bottom
//   |p| >= 6      : the required ledger lines must be present
// then non-maximum suppression across x, p and staves.  Stem verification is
// done in stems.js (filled heads and half notes need one).
const { integral } = require('./cc');

const DEFAULTS = {
  filledMin: 0.78,       // core fill (B) for filled heads
  edgeMin: 0.45,         // top/bottom edge band fill (R)
  beamSide: 0.65,        // both sides this full (R) -> beam, reject
  hollowCoreMax: 0.3,
  hollowWallMin: 0.4,
  hollowEdgeMin: 0.18,
  ledgerMin: 0.55,
  pRange: 13,
  clefZone: 3.0,         // staff spaces after staff start where no note can be
};

function detectNoteheads(B, R, staves, ss, opts = {}, comps = null) {
  const o = { ...DEFAULTS, ...opts };
  const IB = integral(B), IR = integral(R);
  const w = B.width;
  const cands = [];
  for (const st of staves) {
    let x0 = Math.round(st.left + o.clefZone * ss);
    const x1 = st.right;
    if (comps) {
      // clef (and brace) exclusion: tall components starting near the staff start
      const yt = st.yAt(0, st.left) - 2 * ss, yb = st.yAt(4, st.left) + 2 * ss;
      for (const c of comps) {
        if (c.x0 < st.left + 2.0 * ss && c.x1 < st.left + 7 * ss && c.x1 > st.left && c.y1 > yt && c.y0 < yb && (c.y1 - c.y0) >= 2.5 * ss) {
          x0 = Math.max(x0, Math.round(c.x1 + 0.4 * ss));
        }
      }
    }
    for (let p = -o.pRange; p <= o.pRange; p++) {
      const row = [];
      for (let x = x0; x <= x1; x++) {
        const sp = (st.dense[4][x] - st.dense[0][x]) / 4;
        const yc = st.dense[2][x] - (p * sp) / 2;
        const f = featuresAt(IB, IR, x, yc, sp);
        let kind = null, score = 0;
        if (f.core >= o.filledMin && f.top >= o.edgeMin && f.bot >= o.edgeMin && !(f.left >= o.beamSide && f.right >= o.beamSide)) {
          kind = 'filled'; score = f.core;
        } else if (f.hcore <= o.hollowCoreMax && f.wallL >= o.hollowWallMin && f.wallR >= o.hollowWallMin &&
                   f.htop >= o.hollowEdgeMin && f.hbot >= o.hollowEdgeMin) {
          kind = 'hollow'; score = Math.min(f.wallL, f.wallR, 2 * f.htop, 2 * f.hbot) - f.hcore;
        }
        row.push(kind ? { kind, score, x, yc, sp, f } : null);
      }
      // 1-D NMS along x: keep local maxima runs (centre of plateau)
      for (let i = 0; i < row.length; i++) {
        const c = row[i];
        if (!c) continue;
        let j = i;
        while (j + 1 < row.length && row[j + 1] && row[j + 1].kind === c.kind) j++;
        // pick best score in run, tie -> centre
        let best = i;
        for (let k = i; k <= j; k++) if (row[k].score > row[best].score + 1e-9) best = k;
        const mid = (i + j) >> 1;
        const pick = Math.abs(row[mid].score - row[best].score) < 0.02 ? row[mid] : row[best];
        const runLen = j - i + 1;
        if (runLen >= Math.max(1, 0.08 * ss)) {
          if (Math.abs(p) >= 6 && !ledgersOK(IB, st, p, pick.x, ss, o)) { i = j; continue; }
          cands.push({ ...pick, staff: st.index, p, runLen });
        }
        i = j;
      }
    }
  }
  // global NMS: overlapping heads (|dx| < 0.75 ss and |dy| < 0.75 ss) keep best;
  // prefer smaller |p| (nearest staff) for duplicates between staves
  cands.sort((a, b) => (b.score - a.score) || (Math.abs(a.p) - Math.abs(b.p)));
  const kept = [];
  for (const c of cands) {
    const clash = kept.some(k => Math.abs(k.x - c.x) < 0.75 * c.sp && Math.abs(k.yc - c.yc) < 0.75 * c.sp);
    if (!clash) kept.push(c);
  }
  return kept.map(c => ({ x: c.x, y: c.yc, kind: c.kind, score: c.score, staff: c.staff, p: c.p, sp: c.sp, f: c.f }));
}

function featuresAt(IB, IR, x, yc, sp) {
  return {
    core: IB.frac(x - 0.38 * sp, yc - 0.28 * sp, x + 0.38 * sp, yc + 0.28 * sp),
    top: IR.frac(x - 0.25 * sp, yc - 0.45 * sp, x + 0.25 * sp, yc - 0.33 * sp),
    bot: IR.frac(x - 0.25 * sp, yc + 0.33 * sp, x + 0.25 * sp, yc + 0.45 * sp),
    left: IR.frac(x - 1.05 * sp, yc - 0.12 * sp, x - 0.75 * sp, yc + 0.12 * sp),
    right: IR.frac(x + 0.75 * sp, yc - 0.12 * sp, x + 1.05 * sp, yc + 0.12 * sp),
    hcore: IR.frac(x - 0.15 * sp, yc - 0.1 * sp, x + 0.15 * sp, yc + 0.1 * sp),
    wallL: IR.frac(x - 0.62 * sp, yc - 0.12 * sp, x - 0.32 * sp, yc + 0.12 * sp),
    wallR: IR.frac(x + 0.32 * sp, yc - 0.12 * sp, x + 0.62 * sp, yc + 0.12 * sp),
    htop: IB.frac(x - 0.22 * sp, yc - 0.62 * sp, x + 0.22 * sp, yc - 0.3 * sp),
    hbot: IB.frac(x - 0.22 * sp, yc + 0.3 * sp, x + 0.22 * sp, yc + 0.62 * sp),
  };
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
    // ledger extends ~0.35 sp beyond the head on both sides: test the outer parts
    const l = IB.frac(x - 0.85 * sp, y - lt - 1, x - 0.62 * sp, y + lt + 1);
    const r = IB.frac(x + 0.62 * sp, y - lt - 1, x + 0.85 * sp, y + lt + 1);
    if (Math.max(l, r) < o.ledgerMin * 0.5 || Math.min(l, r) < 0.15) return false;
  }
  return true;
}

module.exports = { detectNoteheads, featuresAt, DEFAULTS };
