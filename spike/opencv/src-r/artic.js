'use strict';
// Articulations (L22): staccato, staccatissimo, tenuto, accent and marcato over or under a note.
//
// readArticulations(fr, asm) runs once per page at the start of buildScore (score.js). Engravers
// put these marks on the side of the note away from its stem (marcato above a stemless or up-stem
// note too), centred on the head, a little beyond the outermost head of the chord. Each component
// of the staff-removed page found there is classified by its size and shape:
//   staccato       a round dot, a third to a half space across
//   staccatissimo  a thin upright wedge
//   tenuto         a short flat dash about a head wide
//   accent         '>' wider than tall: two strokes meeting at the right
//   marcato        '^' over the note, 'v' under it: two strokes meeting at the top / bottom
// Up to two marks stack (accent or tenuto with a staccato). The heads of the chord get
// h.artic = ['staccato', ...]; toMusicXML writes <articulations> from it.

// share of rows (cols) of the box b holding ink in [a, z) of its width (height)
function inkRuns(R, b, row) {
  const W = R.width, n = row ? b.y1 - b.y0 + 1 : b.x1 - b.x0 + 1, m = row ? b.x1 - b.x0 + 1 : b.y1 - b.y0 + 1;
  const runs = [];
  for (let i = 0; i < n; i++) {
    const rs = [];
    let on = false;
    for (let j = 0; j < m; j++) {
      const x = row ? b.x0 + j : b.x0 + i, y = row ? b.y0 + i : b.y0 + j;
      const v = R.data[y * W + x];
      if (v && b.ids && b.lab && !b.ids.has(b.lab[y * W + x])) continue;
      if (v && !on) rs.push([j, j]);
      if (v) rs[rs.length - 1][1] = j;
      on = !!v;
    }
    runs.push(rs);
  }
  return runs;
}

// the kind of mark component c is, or null
function markKind(R, c, sp, above) {
  const w = (c.x1 - c.x0 + 1) / sp, h = (c.y1 - c.y0 + 1) / sp, fill = c.area / ((c.x1 - c.x0 + 1) * (c.y1 - c.y0 + 1));
  if (w >= 0.2 && w <= 0.65 && h >= 0.2 && h <= 0.65 && w / h >= 0.6 && w / h <= 1.6 && fill >= 0.5) return 'staccato';
  if (w >= 0.12 && w <= 0.5 && h >= 0.45 && h <= 1.1 && h / w >= 1.6 && fill >= 0.4) return 'staccatissimo';
  if (w >= 0.7 && w <= 1.5 && h >= 0.06 && h <= 0.36 && fill >= 0.6) return 'tenuto';
  if (w >= 0.75 && w <= 1.6 && h >= 0.4 && h <= 1.0 && w / h >= 1.2) {
    // '>': the left columns hold ink at the top and bottom only, the right ones in the middle
    const cols = inkRuns(R, c, false), n = cols.length, k = Math.max(1, Math.round(0.15 * n));
    const left = cols.slice(0, k), right = cols.slice(n - k);
    const hh = c.y1 - c.y0 + 1;
    const two = left.filter(rs => rs.length >= 2 || (rs.length === 1 && rs[0][1] - rs[0][0] > 0.6 * hh)).length;
    const mid = right.filter(rs => rs.length === 1 && Math.abs((rs[0][0] + rs[0][1]) / 2 - hh / 2) < 0.3 * hh).length;
    if (two >= 0.5 * k && mid >= 0.5 * k) return 'accent';
  }
  if (w >= 0.5 && w <= 1.25 && h >= 0.5 && h <= 1.25) {
    // '^' / 'v': one run in the rows at the point, two runs in the rows at the open end
    const rows = inkRuns(R, c, true), n = rows.length, k = Math.max(1, Math.round(0.25 * n));
    const tip = above ? rows.slice(0, k) : rows.slice(n - k), open = above ? rows.slice(n - k) : rows.slice(0, k);
    const ww = c.x1 - c.x0 + 1;
    const one = tip.filter(rs => rs.length === 1 && Math.abs((rs[0][0] + rs[0][1]) / 2 - ww / 2) < 0.25 * ww).length;
    const two = open.filter(rs => rs.length >= 2).length;
    if (one >= 0.5 * k && two >= 0.5 * k) return 'marcato';
  }
  return null;
}

function readArticulations(fr, asm, stats = {}) {
  const R = fr && fr.R;
  if (!R || !asm) return stats;
  const comps = asm.comps || [];
  // components by column bands, for the windows below
  const G = Math.max(8, Math.round(2 * fr.ss)), grid = new Map();
  comps.forEach(c => { for (let g = Math.floor(c.x0 / G); g <= Math.floor(c.x1 / G); g++) { if (!grid.has(g)) grid.set(g, []); grid.get(g).push(c); } });
  const near = (x0, x1) => { const s = new Set(); for (let g = Math.floor(x0 / G); g <= Math.floor(x1 / G); g++) for (const c of grid.get(g) || []) s.add(c); return [...s]; };
  for (const sy of asm.systems) for (const s of sy.staves) {
    const sp = s.st.space || fr.ss;
    for (const ch of s.chords) {
      const hs = ch.heads;
      if (!hs.length) continue;
      const hx = hs.reduce((a, h) => a + h.x, 0) / hs.length;
      const top = Math.min(...hs.map(h => h.y)), bot = Math.max(...hs.map(h => h.y));
      const up = hs.some(h => h.stemDir === 1 || h.stemDir === 2), down = hs.some(h => h.stemDir === -1 || h.stemDir === 2);
      // the side away from the stem (both sides of a stemless note)
      // (a head read with stems both ways may have a marcato taken for its second stem)
      const sides = up && !down ? [false] : down && !up ? [true] : [true, false];
      const found = [];
      for (const above of sides) {
        const y0 = above ? top - 3.6 * sp : bot + 0.55 * sp, y1 = above ? top - 0.55 * sp : bot + 3.6 * sp;
        const cand = near(hx - 1.2 * sp, hx + 1.2 * sp).filter(c => {
          const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
          return Math.abs(cx - hx) <= 0.45 * sp && cy >= y0 && cy <= y1 && c.x1 - c.x0 < 1.7 * sp && c.y1 - c.y0 < 1.3 * sp &&
            // nothing that reaches into the chord's heads (a stem, a beam, a slur end)
            !(c.y0 <= bot + 0.4 * sp && c.y1 >= top - 0.4 * sp);
        }).sort((a, b) => (above ? b.y1 - a.y1 : a.y0 - b.y0));
        let last = above ? top : bot;
        // a mark cut in pieces by staff-line removal: pieces within a fifth of a space joined
        const used = new Set();
        const glyphs = [];
        for (const c of cand) {
          if (used.has(c)) continue;
          const g = { x0: c.x0, y0: c.y0, x1: c.x1, y1: c.y1, area: c.area };
          used.add(c);
          for (const o of cand) if (!used.has(o) && o.x0 <= g.x1 + 0.2 * sp && o.x1 >= g.x0 - 0.2 * sp && o.y0 <= g.y1 + 0.2 * sp && o.y1 >= g.y0 - 0.2 * sp &&
            !markKind(R, c, sp, above) && !markKind(R, o, sp, above)) {
            used.add(o); g.x0 = Math.min(g.x0, o.x0); g.y0 = Math.min(g.y0, o.y0); g.x1 = Math.max(g.x1, o.x1); g.y1 = Math.max(g.y1, o.y1); g.area += o.area;
          }
          glyphs.push(g);
        }
        for (const c of glyphs) {
          const gap = above ? (last - c.y1) / sp : (c.y0 - last) / sp;
          if (gap > (found.length ? 1.2 : 2.6)) break;
          const k = markKind(R, c, sp, above);
          if (!k) break;
          if (!found.includes(k)) found.push(k);
          last = above ? c.y0 : c.y1;
          if (found.length >= 2) break;
        }
        if (found.length) break;
      }
      if (found.length) {
        for (const h of hs) h.artic = found;
        stats.marks = (stats.marks || 0) + found.length;
      }
    }
  }
  return stats;
}

// Double dots (L14): a head read with one augmentation dot (assemble.js headDuration) whose dot has
// a second one just right of it at the same height: 1.75 times the plain value, not 1.5.
function readDoubleDots(fr, asm, stats = {}) {
  if (!fr || !asm) return stats;
  const comps = asm.comps || [];
  const dotLike = (c, sp) => {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
    return w >= 0.2 * sp && w <= 0.8 * sp && h >= 0.2 * sp && h <= 0.8 * sp && c.area >= 0.45 * w * h && Math.max(w, h) <= 1.8 * Math.min(w, h);
  };
  for (const sy of asm.systems) for (const s of sy.staves) {
    const sp0 = s.st.space || fr.ss;
    const ds = comps.filter(c => dotLike(c, sp0) && c.y1 > s.st.yAt(0, c.x0) - 6 * sp0 && c.y0 < s.st.yAt(4, c.x0) + 6 * sp0);
    for (const ch of s.chords) for (const h of ch.heads) {
      if (!h.dur || h.dur.dots !== 1) continue;
      const sp = h.sp || sp0;
      const first = ds.filter(c => c.x0 >= h.x + 0.5 * sp && c.x0 <= h.x + 2.0 * sp && Math.abs((c.y0 + c.y1) / 2 - h.y) <= 0.85 * sp).sort((a, b) => a.x0 - b.x0)[0];
      if (!first) continue;
      const cy = (first.y0 + first.y1) / 2;
      const second = ds.find(c => c !== first && c.x0 > first.x1 && c.x0 <= first.x1 + 0.9 * sp && Math.abs((c.y0 + c.y1) / 2 - cy) <= 0.2 * sp);
      // (not the first dot of the next note's head: no head right after it)
      if (!second || s.chords.some(o => o !== ch && o.heads.some(g => Math.abs(g.y - cy) < 0.7 * sp && g.x - 0.6 * sp <= second.x1 && g.x + 0.6 * sp >= second.x0))) continue;
      const k = 1.75 / 1.5;
      h.dur = Object.assign({}, h.dur, { q: h.dur.q * k, dots: 2 });
      if (h.dur.down) h.dur.down = Object.assign({}, h.dur.down, { q: h.dur.down.q * k, dots: 2 });
      stats.doubleDots = (stats.doubleDots || 0) + 1;
    }
  }
  return stats;
}

module.exports = { readArticulations, readDoubleDots, _markKind: markKind };
