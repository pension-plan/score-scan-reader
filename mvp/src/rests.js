'use strict';
// Rest glyphs on a staff, read from the staff-removed page R and its
// connected components (the note detector does not report rests).

// row profile of a component's box: per row the ink span [a, b] (-1 when
// empty) and the number of separate runs
function rowProfile(R, c) {
  const W = R.width, rows = [];
  for (let y = c.y0; y <= c.y1; y++) {
    let a = -1, b = -1, runs = 0, prev = 0;
    for (let x = c.x0; x <= c.x1; x++) {
      const v = R.data[y * W + x];
      if (v) { if (a < 0) a = x; b = x; if (!prev) runs++; }
      prev = v;
    }
    rows.push({ a, b, runs });
  }
  return rows;
}

function features(R, c, st, sp) {
  const xc = (c.x0 + c.x1) / 2, y0 = st.yAt(0, xc);
  const w = (c.x1 - c.x0 + 1) / sp, h = (c.y1 - c.y0 + 1) / sp;
  const top = (c.y0 - y0) / sp, bot = (c.y1 + 1 - y0) / sp;
  const fill = c.area / ((c.x1 - c.x0 + 1) * (c.y1 - c.y0 + 1));
  return { xc, w, h, top, bot, cy: (top + bot) / 2, fill };
}

// wide stretches of the row profile, top to bottom: a flag rest has one per
// hook (its blob and the hook out to the stem); the stem below is thin
function hooks(rows, sp) {
  const wide = rows.map(r => r.a >= 0 && r.b - r.a + 1 >= 0.55 * sp);
  let n = 0, run = 0;
  const minRun = Math.max(2, 0.18 * sp);
  for (let i = 0; i <= wide.length; i++) {
    if (i < wide.length && wide[i]) run++;
    else { if (run >= minRun) n++; run = 0; }
  }
  return n;
}

// The rests printed on staff s between xa and xb:
// [{x, pos (centre, staff spaces below the top line), q, dots, kind, box,
//   bar (whole-bar rest), multi (bars of a multi-bar rest)}] sorted by x.
function detectRests({ R, comps, s, xa, xb, debug }) {
  const st = s.st, sp = st.space;
  const xMin = Math.max(xa, (s.hdr && s.hdr.end) || -1e9) + 0.3 * sp;
  const heads = [];
  for (const c of s.chords) if (c.x > xa - 3 * sp && c.x < xb + 3 * sp) for (const h of c.heads) heads.push(h);
  const out = [];
  const band = comps.filter(c => c.x1 > xMin && c.x0 < xb && c.area >= 0.05 * sp * sp);
  for (const c of band) {
    if (c.x0 < xMin || c.x1 > xb - 0.2 * sp) continue;
    const f = features(R, c, st, sp);
    if (f.top < -2.5 || f.bot > 6.5) continue;
    if (f.h < 0.3 || f.w < 0.3 || f.w > 12 || f.h > 5.5) continue;
    // part of a note (head, stem, flag)
    if (heads.some(hd => hd.x + 0.6 * sp >= c.x0 && hd.x - 0.6 * sp <= c.x1 && hd.y + 0.5 * sp >= c.y0 && hd.y - 0.5 * sp <= c.y1)) continue;
    const rows = rowProfile(R, c);
    const nh = hooks(rows, sp);
    let kind = null, q = 0;
    if (f.fill >= 0.65 && f.h >= 0.3 && f.h <= 0.85 && f.w >= 0.8 && f.w <= 1.7) {
      // block hanging from a line (whole) or sitting on one (half)
      const fr = f.cy - Math.floor(f.cy);
      if (fr > 0.05 && fr < 0.5) { kind = 'whole'; q = 4; } else { kind = 'half'; q = 2; }
    } else if (f.fill >= 0.65 && f.h >= 0.8 && f.h <= 1.25 && f.w >= 0.35 && f.w <= 0.75) { kind = 'breve'; q = 8; }
    else if (f.fill >= 0.6 && f.h >= 0.35 && f.h <= 1.0 && f.w >= 2.2) { kind = 'multi'; q = 4; }
    else if (f.h >= 2.2 && f.h <= 3.5 && f.w >= 0.6 && f.w <= 1.5 && f.fill >= 0.2 && f.fill <= 0.65) { kind = 'quarter?'; q = 1; }
    else if (f.h >= 1.3 && f.h < 2.2 && f.w >= 0.6 && f.w <= 1.4 && f.fill >= 0.15 && f.fill <= 0.6) { kind = 'eighth'; q = 0.5; }
    else if (f.h >= 3.5 && f.h < 5.5 && f.w >= 0.8 && f.w <= 1.8 && f.fill >= 0.15 && f.fill <= 0.55) { kind = 'flag'; q = 0.125; }
    if (debug) debug('cand', Math.round(f.xc), Math.round(c.y0), 'w', f.w.toFixed(2), 'h', f.h.toFixed(2), 'top', f.top.toFixed(2), 'fill', f.fill.toFixed(2), 'hooks', nh, '->', kind);
    if (!kind) continue;
    out.push({ x: f.xc, pos: f.cy, q, kind, box: c, hooks: nh });
  }
  return out.sort((a, b) => a.x - b.x);
}

module.exports = { detectRests, _features: features, _rowProfile: rowProfile };
