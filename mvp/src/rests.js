'use strict';
// Rest glyphs on a staff, read from the staff-removed page R and its
// connected components (the note detector does not report rests).
//
// Positions are in staff spaces below the top line (lines at 0..4). Shapes:
//   whole    filled block hanging from a line (centre ~0.25 below it)
//   half     filled block sitting on a line (centre ~0.25 above it)
//   breve    filled block one space tall (two bars as a church rest)
//   long     filled block two spaces tall (four bars)
//   quarter  zigzag about three spaces tall
//   8th..64th  a stem slanting down to the left with one hook per flag on
//            its left, about 1 + n spaces tall for n flags; the stem below
//            the last hook is a thin tail (a quarter rest ends in a hook)
//   H-bar    thick bar on the middle line with end strokes: a multi-bar
//            rest, its bar count printed above the staff
// A dot or two right of the glyph lengthen it.

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

// thin tail at the bottom (spaces), how far it slants left going down, and
// how far the right edge comes back right below the top fifth (a quarter
// rest zigzags; a flag rest's stem only moves left)
function strokeShape(rows, sp) {
  let n = 0;
  for (let i = rows.length - 1; i >= 0; i--) {
    const r = rows[i];
    if (r.a < 0) continue;
    if (r.b - r.a + 1 > 0.42 * sp || r.runs > 1) break;
    n++;
  }
  const t0 = rows[rows.length - 1], t1 = rows[Math.max(0, rows.length - n)];
  const slant = n ? ((t1.a + t1.b) - (t0.a + t0.b)) / 2 / sp : 0;
  let rise = 0, lo = Infinity;
  for (let i = Math.floor(0.2 * rows.length); i < rows.length; i++) {
    const b = rows[i].b;
    if (b < 0) continue;
    if (b < lo) lo = b;
    rise = Math.max(rise, (b - lo) / sp);
  }
  return { tail: n / sp, slant, rise };
}

// wide stretches of the row profile, top to bottom: one per hook of a flag rest
function hookCount(rows, sp) {
  let n = 0, run = 0;
  const minRun = Math.max(2, 0.18 * sp);
  for (let i = 0; i <= rows.length; i++) {
    const wide = i < rows.length && rows[i].a >= 0 && rows[i].b - rows[i].a + 1 >= 0.55 * sp;
    if (wide) run++;
    else { if (run >= minRun) n++; run = 0; }
  }
  return n;
}

// ---- digits (the bar count over a multi-bar rest) ----
// holes: background regions of the glyph box not reaching its border
function holes(R, c) {
  const w = c.x1 - c.x0 + 3, h = c.y1 - c.y0 + 3, seen = new Uint8Array(w * h);
  const ink = (x, y) => x >= 1 && y >= 1 && x < w - 1 && y < h - 1 && R.data[(c.y0 + y - 1) * R.width + c.x0 + x - 1];
  const out = [];
  for (let sy = 0; sy < h; sy++) for (let sx = 0; sx < w; sx++) {
    if (seen[sy * w + sx] || ink(sx, sy)) continue;
    const st = [[sx, sy]]; seen[sy * w + sx] = 1;
    let n = 0, border = false, ys = 0;
    while (st.length) {
      const [x, y] = st.pop(); n++; ys += y;
      if (x === 0 || y === 0 || x === w - 1 || y === h - 1) border = true;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= w || ny >= h || seen[ny * w + nx] || ink(nx, ny)) continue;
        seen[ny * w + nx] = 1; st.push([nx, ny]);
      }
    }
    if (!border && n >= 3) out.push({ n, cy: (ys / n - 1) / (h - 2) });
  }
  return out;
}

// one engraved digit from its topology and ink distribution
function readDigit(R, c) {
  const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
  if (w < 0.42 * h) return 1;
  const hs = holes(R, c);
  if (hs.length >= 2) return 8;
  if (hs.length === 1) {
    const y = hs[0].cy;
    if (y > 0.55) return 6;
    if (y < 0.42) return w > 0.8 * h ? 4 : 9;
    return 0;
  }
  const rows = rowProfile(R, c);
  const span = (f0, f1) => {
    let s = 0, k = 0;
    for (let i = Math.floor(f0 * h); i < Math.max(Math.floor(f0 * h) + 1, Math.floor(f1 * h)); i++) if (rows[i] && rows[i].a >= 0) { s += (rows[i].b - rows[i].a + 1) / w; k++; }
    return k ? s / k : 0;
  };
  const left = (f0, f1) => {
    let s = 0, k = 0;
    for (let i = Math.floor(f0 * h); i < Math.max(Math.floor(f0 * h) + 1, Math.floor(f1 * h)); i++) if (rows[i] && rows[i].a >= 0) { s += (rows[i].a - c.x0) / w; k++; }
    return k ? s / k : 1;
  };
  const topW = span(0, 0.15), botW = span(0.85, 1);
  if (topW > 0.8 && botW < 0.5) return 7;
  if (botW > 0.8) return 2;
  if (topW > 0.75 && left(0.1, 0.4) < 0.3) return 5;
  if (left(0.35, 0.65) > 0.3) return 3;
  return 5;
}

// the number printed above a multi-bar rest: digit components over its
// middle, left to right (touching digits are cut at their thinnest column)
function readNumber(R, comps, st, sp, x0, x1) {
  const ds = comps.filter(c => {
    const xc = (c.x0 + c.x1) / 2, y0 = st.yAt(0, xc);
    const h = (c.y1 - c.y0 + 1) / sp;
    return xc > x0 && xc < x1 && c.y1 < y0 - 0.2 * sp && c.y0 > y0 - 5 * sp && h >= 1.2 && h <= 2.8;
  }).sort((a, b) => a.x0 - b.x0);
  if (!ds.length) return 0;
  const glyphs = [];
  for (const c of ds) {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
    if (w <= 0.95 * h) { glyphs.push(c); continue; }
    // two digits touching: cut at the column with least ink in the middle
    let best = -1, bv = Infinity;
    for (let x = c.x0 + Math.floor(0.3 * w); x <= c.x0 + Math.ceil(0.7 * w); x++) {
      let n = 0;
      for (let y = c.y0; y <= c.y1; y++) n += R.data[y * R.width + x];
      if (n < bv) { bv = n; best = x; }
    }
    const shrink = (b) => {
      let { x0, x1 } = b, y0 = c.y1, y1 = c.y0;
      for (let y = c.y0; y <= c.y1; y++) for (let x = x0; x <= x1; x++) if (R.data[y * R.width + x]) { if (y < y0) y0 = y; if (y > y1) y1 = y; }
      return { x0, x1, y0, y1 };
    };
    glyphs.push(shrink({ x0: c.x0, x1: best - 1 }), shrink({ x0: best + 1, x1: c.x1 }));
  }
  let n = 0;
  for (const g of glyphs.slice(0, 3)) n = 10 * n + readDigit(R, g);
  return n;
}

// The rests printed on staff s between xa and xb:
// [{x, pos (centre), q, dots, kind, box, bars (bars it stands for, block
// rests), multi (bar count of a multi-bar rest)}] sorted by x.
function detectRests({ R, comps, s, xa, xb, debug }) {
  const st = s.st, sp = st.space;
  const xMin = Math.max(xa, (s.hdr && s.hdr.end) || -1e9) + 0.3 * sp;
  const heads = [];
  for (const c of s.chords) if (c.x > xa - 3 * sp && c.x < xb + 3 * sp) for (const h of c.heads) heads.push(h);
  const near = comps.filter(c => c.x1 > xMin - 2 * sp && c.x0 < xb + 2 * sp && c.area >= 0.03 * sp * sp);
  const out = [];
  for (const c of near) {
    if (c.x0 < xMin || c.x1 > xb - 0.2 * sp || c.area < 0.1 * sp * sp) continue;
    const f = features(R, c, st, sp);
    if (f.h < 0.3 || f.w < 0.3 || f.w > 14 || f.h > 5.6) continue;
    // must sit on the staff
    if (Math.min(f.bot, 4) - Math.max(f.top, 0) < 0.3) continue;
    // part of a note (head, stem, flag)
    if (heads.some(hd => hd.x + 0.6 * sp >= c.x0 && hd.x - 0.6 * sp <= c.x1 && hd.y + 0.5 * sp >= c.y0 && hd.y - 0.5 * sp <= c.y1)) continue;
    let kind = null, q = 0, bars = 0, multi = 0;
    const fr = f.cy - Math.floor(f.cy);
    if (f.fill >= 0.65 && f.h >= 0.3 && f.h <= 0.85 && f.w >= 0.8 && f.w <= 1.8 && f.top >= -0.2 && f.bot <= 4.2) {
      // block hanging from a line (whole) or sitting on one (half)
      if (fr > 0.05 && fr < 0.5) { kind = 'whole'; q = 4; bars = 1; } else { kind = 'half'; q = 2; }
    } else if (f.fill >= 0.65 && f.h >= 0.8 && f.h <= 1.3 && f.w >= 0.3 && f.w <= 0.8) { kind = 'breve'; q = 8; bars = 2; }
    else if (f.fill >= 0.65 && f.h >= 1.7 && f.h <= 2.3 && f.w >= 0.3 && f.w <= 0.8) { kind = 'long'; q = 16; bars = 4; }
    else if (f.w >= 2.5 && f.h <= 2.8 && f.cy > 1.2 && f.cy < 2.8) {
      // H-bar: rows spanning nearly the whole width around the middle line
      const rows = rowProfile(R, c);
      let run = 0, best = 0, mid = 0;
      rows.forEach((r, i) => {
        if (r.a >= 0 && r.b - r.a + 1 >= 0.85 * (c.x1 - c.x0 + 1) && r.runs <= 2) { run++; if (run > best) { best = run; mid = i - run / 2; } } else run = 0;
      });
      const pos = (c.y0 + mid - st.yAt(0, f.xc)) / sp;
      if (best >= 0.3 * sp && best <= 1.1 * sp && Math.abs(pos - 2) < 0.6) {
        kind = 'multi'; q = 4; bars = 1;
        multi = readNumber(R, comps, st, sp, c.x0 - 0.5 * sp, c.x1 + 0.5 * sp) || 0;
      }
    } else if (f.h >= 1.3 && f.h <= 5.4 && f.w >= 0.6 && f.w <= 1.9 && f.fill >= 0.15 && f.fill <= 0.65) {
      const rows = rowProfile(R, c);
      const sh = strokeShape(rows, sp), nh = hookCount(rows, sp);
      if (debug) debug('  shape', Math.round(f.xc), 'tail', sh.tail.toFixed(2), 'slant', sh.slant.toFixed(2), 'rise', sh.rise.toFixed(2), 'hooks', nh);
      if (f.h >= 2.2 && f.h <= 3.4 && f.w <= 1.5 && sh.tail < 0.75 && sh.rise >= 0.25 && f.fill >= 0.25) { kind = 'quarter'; q = 1; }
      else if (sh.tail >= 0.55 && sh.slant >= 0.1 && nh >= 1) {
        const byH = Math.max(1, Math.min(4, Math.round(f.h - 0.9)));
        const n = Math.abs(byH - nh) <= 1 ? byH : Math.min(nh, 4);
        kind = 'flag' + n; q = 0.5 / Math.pow(2, n - 1);
      }
    }
    if (debug) debug('cand', Math.round(f.xc), Math.round(c.y0), 'w', f.w.toFixed(2), 'h', f.h.toFixed(2), 'top', f.top.toFixed(2), 'fill', f.fill.toFixed(2), '->', kind);
    if (!kind) continue;
    // a glyph directly left of a notehead at its height is an accidental
    if (q <= 1 && heads.some(hd => hd.x - c.x1 >= -0.2 * sp && hd.x - c.x1 <= 1.5 * sp && hd.y >= c.y0 - 0.3 * sp && hd.y <= c.y1 + 0.3 * sp)) continue;
    // a time signature: two glyphs stacked on the staff
    if (kind !== 'multi' && near.some(o => o !== c && Math.abs((o.x0 + o.x1) / 2 - f.xc) < 0.4 * sp && (o.y1 - o.y0) >= 1.2 * sp &&
      (o.y0 > c.y1 ? o.y0 - c.y1 : c.y0 - o.y1) >= -1 && (o.y0 > c.y1 ? o.y0 - c.y1 : c.y0 - o.y1) < 0.5 * sp)) continue;
    // augmentation dots: small round blobs just right of the glyph
    let dots = 0, dx = c.x1;
    const yLo = c.y0 - 0.3 * sp, yHi = c.y1 + 0.3 * sp;
    for (let k = 0; k < 2 && !bars; k++) {
      const d = near.find(o => {
        const w = (o.x1 - o.x0 + 1) / sp, h = (o.y1 - o.y0 + 1) / sp, oy = (o.y0 + o.y1) / 2;
        return o !== c && w >= 0.2 && w <= 0.7 && h >= 0.2 && h <= 0.7 && o.x0 > dx && o.x0 - dx <= (k ? 0.9 : 1.2) * sp && oy >= yLo && oy <= yHi &&
          o.area >= 0.5 * (o.x1 - o.x0 + 1) * (o.y1 - o.y0 + 1);
      });
      if (!d) break;
      dots++; dx = d.x1;
    }
    if (dots) q *= dots === 1 ? 1.5 : 1.75;
    out.push({ x: f.xc, pos: f.cy, q, dots, kind, box: c, bars, multi });
  }
  return out.sort((a, b) => a.x - b.x);
}

module.exports = { detectRests, readNumber, _features: features, _rowProfile: rowProfile };
