'use strict';
// Staves whose lines are washed out or partly missing (faded copies, severe scans): the line
// finders (staves.js) return no staff, or a staff only where its lines survive. What remains of
// the music places the rest:
//   - a partial staff is extended along its own slope over the glyphs that continue it in its
//     band (clef, notes, rests: gaps under six spaces), towards the system's margins;
//   - a treble clef standing where no staff was found gives a staff of its own: Bravura's G clef
//     is 7.25 spaces tall and reaches 1.78 spaces above the top line, so its box gives both the
//     space and the lines; the staff runs right over the glyphs in its band.
// front.js runs this only when the finders came back empty or with a staff clearly shorter than
// the page's longest one, or with a clef outside every staff.
const { labelComponents } = require('./cc');
const { clefBoxScores } = require('./cv');

const G_TALL = 7.25, G_ABOVE = 1.78;

function staffYAt(k, x) { const d = this.dense[k]; return d[Math.max(0, Math.min(d.length - 1, Math.round(x)))]; }
function staffSpaceAt(x) { return (this.yAt(4, x) - this.yAt(0, x)) / 4; }

function lineStaff(w, y0, sp, slope, left, right) {
  const xs = [left, right];
  const ys = [0, 1, 2, 3, 4].map(k => [y0 + k * sp, y0 + k * sp + slope * (right - left)]);
  const dense = [0, 1, 2, 3, 4].map(k => { const d = new Float32Array(w); for (let x = 0; x < w; x++) d[x] = ys[k][0] + slope * (x - left); return d; });
  return { xs, ys, dense, yAt: staffYAt, spaceAt: staffSpaceAt, left, right, space: sp, inferred: true };
}

// glyphs in a staff's band (centre between a space above the top line and a space below the
// bottom one), chained outwards from [a, b] while the gaps stay under maxGap
function chain(comps, st, a, b, sp, w, maxGap) {
  const inBand = comps.filter(c => {
    const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
    return cx >= 0 && cx < w && cy > st.yAt(0, cx) - 1.0 * sp && cy < st.yAt(4, cx) + 1.0 * sp && c.y1 - c.y0 < 9 * sp;
  });
  let lo = a, hi = b;
  for (const c of inBand.filter(c => c.x1 < a).sort((p, q) => q.x1 - p.x1)) { if (lo - c.x1 > maxGap) break; lo = Math.min(lo, c.x0); }
  for (const c of inBand.filter(c => c.x0 > b).sort((p, q) => p.x0 - q.x0)) { if (c.x0 - hi > maxGap) break; hi = Math.max(hi, c.x1); }
  return { lo, hi };
}

// treble clefs on the left of the page: pieces of a faded clef (hook, body, tail dot) are joined
// when they overlap in x and lie close above one another; a group counts when the G clef template
// matches it clearly better than the F and C clefs
function trebleClefs(B, comps, ss) {
  const w = B.width;
  const left = comps.filter(c => c.x0 < 0.35 * w && c.y1 - c.y0 >= 8);
  const groups = [];
  for (const c of left.slice().sort((a, b) => a.y0 - b.y0)) {
    const g = groups.find(g => Math.min(g.x1, c.x1) - Math.max(g.x0, c.x0) >= 0.4 * Math.min(g.x1 - g.x0, c.x1 - c.x0) + 1 && c.y0 - g.y1 <= 0.3 * (g.y1 - g.y0 + c.y1 - c.y0));
    if (g) Object.assign(g, { x0: Math.min(g.x0, c.x0), x1: Math.max(g.x1, c.x1), y0: Math.min(g.y0, c.y0), y1: Math.max(g.y1, c.y1) });
    else groups.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1 });
  }
  const clefs = [];
  for (const c of groups) {
    const cw = c.x1 - c.x0 + 1, ch = c.y1 - c.y0 + 1;
    if (ch < 40 || ch / cw < 2.4 || ch / cw > 3.6) continue;
    const sp = ch / G_TALL;
    if (ss && (sp < 0.85 * ss || sp > 1.15 * ss)) continue;
    const sc = clefBoxScores(B, c, sp);
    if (!sc || sc['clef-G'] < 0.38 || sc['clef-G'] < Math.max(sc['clef-F'], sc['clef-C']) + 0.2) continue;
    clefs.push({ ...c, sp });
  }
  return clefs;
}

function inferStaves(B, staves, opts = {}) {
  const { width: w } = B;
  const out = staves.slice();
  const sp0 = out.map(s => s.space).sort((a, b) => a - b);
  const ss0 = sp0.length ? sp0[sp0.length >> 1] : null;
  // (a two-up spread, staves in two columns, is left alone: its half-width staves are not short)
  if (out.some(s => s.left > 0.5 * w) && out.some(s => s.right < 0.5 * w)) return null;
  const { comps: all } = labelComponents(B);
  const comps = all.filter(c => c.area >= 6);
  const clefs = trebleClefs(B, comps, ss0);
  const bandOf = (c, set) => set.find(st => { const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2; return cy > st.yAt(0, cx) - 2 * st.space && cy < st.yAt(4, cx) + 2 * st.space; });
  // run only where the lines are missing: no staff at all, or a treble clef standing left of the
  // staff it belongs to, or outside every staff
  const stray = clefs.filter(c => { const o = bandOf(c, out); return !o || c.x0 < o.left - 2 * o.space; });
  // or a staff under 60 % of the page's longest
  const width0 = Math.max(0, ...out.map(s => s.right - s.left));
  const short = out.filter(s => s.right - s.left < 0.6 * width0);
  if (out.length && !stray.length && !short.length) return null;
  let added = 0, extended = 0;
  const touched = new Set();
  // 1. the dashed-line finder (staves.js), where the lines survive in pieces: its staves extend
  //    the ones found here, or stand where none was when a stray clef confirms them
  // (a dashed staff where the page's system spacing leaves room for one: below the last staff or
  // in a gap twice the usual, as long as the page's other staves)
  const ys = out.map(st => st.yAt(0, w / 2)).sort((a, b) => a - b);
  const steps = ys.slice(1).map((y, i) => y - ys[i]).sort((a, b) => a - b), step = steps.length ? steps[steps.length >> 1] : 0;
  const gapFits = (ds) => {
    if (out.length < 3 || ds.right - ds.left < 0.6 * width0) return false;
    const y = ds.yAt(0, w / 2), above = ys.filter(v => v < y).pop(), below = ys.find(v => v > y);
    const near = (d) => Math.abs(d - step) < 0.25 * step;
    return (above != null && near(y - above)) && (below == null || near(below - y));
  };
  if (opts.dashed) {
    const d = opts.dashed(B);
    for (const ds of d.staves) {
      const mid = (ds.left + ds.right) / 2;
      const o = out.find(st => Math.abs(st.yAt(0, mid) - ds.yAt(0, mid)) < 2 * ds.space);
      if (o) {
        if (!(short.includes(o) || stray.some(c => bandOf(c, [o]))) || Math.abs(o.space - ds.space) > 0.15 * o.space) continue;
        if (ds.left < o.left - 2 * o.space) { o.left = ds.left; extended++; touched.add(o); }
        if (ds.right > o.right + 2 * o.space) { o.right = ds.right; extended++; touched.add(o); }
      } else if ((stray.some(c => bandOf(c, [ds])) || gapFits(ds)) && (!ss0 || Math.abs(ds.space - ss0) <= 0.15 * ss0)) { ds.inferred = true; out.push(ds); added++; touched.add(ds); }
    }
  }
  const sps = out.map(s => s.space).sort((a, b) => a - b);
  const ss = sps.length ? sps[sps.length >> 1] : null;
  const slopes = out.map(s => (s.yAt(2, s.right) - s.yAt(2, s.left)) / Math.max(1, s.right - s.left)).sort((a, b) => a - b);
  const slope = slopes.length ? slopes[slopes.length >> 1] : 0;
  // 2. the stray clefs: a partial staff starts at its clef; with no staff there, the clef's box
  //    gives the lines
  for (const c of stray) {
    const o = bandOf(c, out);
    if (o) {
      if (c.x0 < o.left - 2 * o.space) { o.left = Math.max(0, Math.round(c.x0 - 0.5 * o.space)); extended++; touched.add(o); }
      continue;
    }
    const s = ss || c.sp;
    const st = lineStaff(w, c.y0 + G_ABOVE * s, s, slope, Math.max(0, Math.round(c.x0 - 0.5 * s)), Math.min(w - 1, c.x1));
    const { hi } = chain(comps, st, st.left, st.right, s, w, 6 * s);
    // music after the clef: a staff, not a stray clef-shaped blot
    if (hi - st.left < 12 * s) continue;
    st.right = hi;
    out.push(st); added++; touched.add(st);
  }
  // 3. right ends of the staves changed here: over the glyphs that continue them, up to the page's
  //    right margin (faded music leaves gaps: three glyphs in the band before the margin also
  //    carry a staff there)
  const rights = out.map(s => s.right).sort((a, b) => a - b), margin = rights[rights.length >> 1];
  for (const st of touched) {
    if (out.length < 3 || st.right >= margin - 2 * st.space) continue;
    const { hi } = chain(comps, st, st.left, st.right, st.space, w, 6 * st.space);
    const more = comps.filter(c => { const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2; return cx > st.right && cx < margin && cy > st.yAt(0, cx) - st.space && cy < st.yAt(4, cx) + st.space && c.y1 - c.y0 < 9 * st.space; }).length;
    const r = more >= 3 ? margin : Math.min(margin + st.space, hi);
    if (r > st.right + 2 * st.space) { st.right = Math.round(r); extended++; }
  }
  if (!added && !extended) return null;
  out.sort((a, b) => a.yAt(0, w / 2) - b.yAt(0, w / 2));
  out.forEach((st, i) => { st.index = i; });
  const sp2 = out.map(s => s.space).sort((a, b) => a - b);
  return { staves: out, added, extended, ss: sp2[sp2.length >> 1] };
}

// One-line staves (a percussion staff with a single line: a snare, a cymbal part): a lone thin
// line (about the staff-line thickness) on a page that has five-line staves, inked along at least
// 70% of the nearest staff's width (a scanned line breaks in places), next to the system's staves
// (a five-line staff within 8 spaces) but none within 2 spaces, no other line within 1.5 spaces,
// and confirmed by opts.confirm(B, left, right, y, ss) (the caller's clef test). Each becomes a
// lineStaff with the line as its middle line, marked oneLine (not inferred: its heads keep the
// stem rule). opts: {ss, lt, confirm}.
function oneLineStaves(B, staves, opts = {}) {
  const ss = opts.ss, lt = opts.lt || 1;
  if (!staves.length || !(ss > 0) || typeof opts.confirm !== 'function') return [];
  const { width: W, height: H, data } = B;
  const left = Math.min(...staves.map(s => s.left)), right = Math.max(...staves.map(s => s.right));
  if (right - left < 20 * ss) return [];
  const mid = (s) => (s.left + s.right) / 2;
  // gap from y to the nearest five-line staff (0 inside one)
  const gapTo = (y) => Math.min(...staves.map(s => { const t = s.yAt(0, mid(s)), b = s.yAt(4, mid(s)); return y < t ? t - y : y > b ? y - b : 0; }));
  const maxT = Math.max(2, Math.round(2 * lt + 1));
  const x0s = Math.max(0, Math.round(left)), x1s = Math.min(W - 1, Math.round(right));
  const cov = new Int32Array(H);
  for (let y = 0; y < H; y++) { let n = 0; const o = y * W; for (let x = x0s; x <= x1s; x++) if (data[o + x]) n++; cov[y] = n; }
  const out = [];
  for (let y = 0; y < H;) {
    const g0 = gapTo(y);
    // (a cheap first test on the whole width; the line's own staff width is checked below)
    if (g0 < 2 * ss || g0 > 8 * ss || cov[y] < 0.49 * (right - left)) { y++; continue; }
    let y1 = y;
    while (y1 + 1 < H && cov[y1 + 1] >= 0.49 * (right - left)) y1++;
    const ya = y, yb = y1;
    y = y1 + 1;
    if (yb - ya + 1 > maxT) continue; // a thick bar (a beam), not a staff line
    const yl = (ya + yb) / 2;
    if (gapTo(yl) < 2 * ss) continue;
    const nb = staves.slice().sort((u, v) => Math.abs(u.yAt(2, mid(u)) - yl) - Math.abs(v.yAt(2, mid(v)) - yl))[0];
    const width = nb.right - nb.left;
    let n = 0;
    for (let x = Math.max(0, Math.round(nb.left)); x <= Math.min(W - 1, Math.round(nb.right)); x++) {
      for (let r = ya; r <= yb; r++) if (data[r * W + x]) { n++; break; }
    }
    if (n < 0.7 * width) continue;
    // thin: the rows just beyond it hold much less ink; alone: no other line within 1.5 spaces
    const top = Math.max(...Array.from({ length: yb - ya + 1 }, (_, i) => cov[ya + i]));
    if (ya - 2 < 0 || yb + 2 >= H || cov[ya - 2] > 0.6 * top || cov[yb + 2] > 0.6 * top) continue;
    let alone = true;
    for (let d = maxT + 2; d < 1.5 * ss && alone; d++) if ((ya - d >= 0 && cov[ya - d] >= 0.75 * top) || (yb + d < H && cov[yb + d] >= 0.75 * top)) alone = false;
    if (!alone) continue;
    if (!opts.confirm(B, nb.left, nb.right, yl, ss)) continue;
    const st = lineStaff(W, yl - 2 * ss, ss, 0, nb.left, nb.right);
    st.inferred = false;
    st.oneLine = true;
    out.push(st);
  }
  return out;
}

module.exports = { inferStaves, oneLineStaves };
