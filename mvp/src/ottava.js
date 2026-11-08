'use strict';
// Octave lines (L15): 8va / 8vb / 15ma brackets.
//
// readOttavas(fr, asm) runs once per page at the start of buildScore (score.js). An octave line is
// a number (8 or 15, often italic, "8va" / "8vb" letters after it allowed) followed by a dashed
// or dotted line along the staff, above it (play higher) or below it (play lower), ending in a
// short hook. The dashes are small flat pieces of ink in a row at one height and an even
// spacing; the number is read by its shape (lineNumber). A line that
// runs on from the system before starts at the staff start with no number. The heads under the
// line get h.ott = +1 / -1 (8va / 8vb) or +2 / -2 (15ma / 15mb); toMusicXML writes the sounding
// pitch and <octave-shift> at the line's ends.
const { labelComponents } = require('./cc');

// dashed rows of ink in comps: [{x0, x1, y, n}]
function dashRows(comps, sp) {
  const ds = comps.filter(c => { const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1; return w >= 0.12 * sp && w <= 0.75 * sp && h <= 0.3 * sp; }).sort((a, b) => a.x0 - b.x0);
  const rows = [], used = new Set();
  for (const d of ds) {
    if (used.has(d)) continue;
    const cy = (d.y0 + d.y1) / 2, run = [d];
    used.add(d);
    let last = d;
    for (const e of ds) {
      if (used.has(e) || e.x0 <= last.x1) continue;
      if (e.x0 - last.x1 > 1.6 * sp) break;
      if (Math.abs((e.y0 + e.y1) / 2 - cy) > 0.15 * sp) continue;
      run.push(e); used.add(e); last = e;
    }
    if (run.length < 4) continue;
    // an even spacing (not a row of staccato dots or a slur's pieces)
    const gaps = run.slice(1).map((e, i) => e.x0 - run[i].x0), g = gaps.slice().sort((a, b) => a - b)[gaps.length >> 1];
    if (gaps.filter(x => Math.abs(x - g) <= 0.35 * sp).length < 0.75 * gaps.length) continue;
    rows.push({ x0: run[0].x0, x1: last.x1, y: cy, n: run.length });
  }
  return rows;
}

// enclosed holes of the ink in box c (an 8 has two, a 1 or a 5 none)
function holes(R, c) {
  const w = c.x1 - c.x0 + 3, h = c.y1 - c.y0 + 3, img = { width: w, height: h, data: new Uint8Array(w * h) };
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) img.data[y * w + x] = R.data[(c.y0 + y - 1) * R.width + c.x0 + x - 1] ? 1 : 0;
  const { comps } = labelComponents(img, { value: 0 });
  return comps.filter(b => b.x0 > 0 && b.y0 > 0 && b.x1 < w - 1 && b.y1 < h - 1 && b.area >= 2).length;
}

// the number at the start of a dashed row: 8 or 15 (null when not read). Engravers set it in an
// italic the time-signature digit templates do not match, so it is read by its shape: an 8 is one
// glyph with two holes; 15 is a narrow 1 and a 5, neither with two holes
function lineNumber(R, comps, row, sp) {
  // the word left of the line ("8", "8va", "15ma"): glyphs run together leftwards from its start
  const near = comps.filter(c => c.x1 <= row.x0 + 0.3 * sp && c.x0 >= row.x0 - 8 * sp && c.y0 <= row.y + 0.8 * sp && c.y1 >= row.y - 1.2 * sp &&
    c.y1 - c.y0 >= 0.35 * sp && c.y1 - c.y0 <= 2.2 * sp && c.x1 - c.x0 <= 2.2 * sp).sort((a, b) => b.x1 - a.x1);
  const word = [];
  let edge = row.x0;
  for (const c of near) {
    if (edge - c.x1 > 0.7 * sp) break;
    word.unshift(c);
    edge = Math.min(edge, c.x0);
  }
  const tall = (c) => c.y1 - c.y0 >= 0.8 * sp;
  if (!word.length || !tall(word[0])) return null;
  const a = word[0], b = word[1] && tall(word[1]) ? word[1] : null;
  const ha = holes(R, a);
  if (ha === 2 && a.x1 - a.x0 >= 0.6 * sp) return { k: 1, x0: a.x0 };
  if (b && ha === 0 && holes(R, b) <= 1 && (a.x1 - a.x0) <= 0.9 * (b.x1 - b.x0) && (a.x1 - a.x0 + 1) <= 0.75 * (a.y1 - a.y0 + 1)) return { k: 2, x0: a.x0 };
  return null;
}

function readOttavas(fr, asm, stats = {}) {
  const R = fr && fr.R;
  if (!R || !asm) return stats;
  const comps = asm.comps || [];
  let open = new Map(); // staff index in system -> {k} still running at the system's end
  for (const sy of asm.systems) {
    const next = new Map();
    sy.staves.forEach((s, si) => {
      const st = s.st, sp = st.space || fr.ss, xm = (st.left + st.right) / 2;
      const top = st.yAt(0, xm), bot = st.yAt(4, xm);
      const prevBot = si > 0 ? sy.staves[si - 1].st.yAt(4, xm) : -Infinity, nextTop = si + 1 < sy.staves.length ? sy.staves[si + 1].st.yAt(0, xm) : Infinity;
      const near = comps.filter(c => c.x0 >= st.left - sp && c.x1 <= st.right + sp && ((c.y1 < top - 0.3 * sp && c.y0 > top - 10 * sp) || (c.y0 > bot + 0.3 * sp && c.y1 < bot + 10 * sp)));
      for (const row of dashRows(near, sp)) {
        const above = row.y < top;
        // a row between two staves belongs to the nearer one
        if (above && row.y - prevBot < top - row.y) continue;
        if (!above && nextTop - row.y < row.y - bot) continue;
        let num = lineNumber(R, near, row, sp);
        const atStart = row.x0 < (s.hdr && s.hdr.end != null ? s.hdr.end : st.left) + 3 * sp;
        if (!num && atStart && open.has(si) && open.get(si).above === above) num = { k: open.get(si).k, x0: row.x0, cont: true };
        if (!num) continue;
        const k = above ? num.k : -num.k;
        // a hook down (up) at the end: the line stops there; otherwise it runs on
        const hook = near.some(c => c.x0 >= row.x1 - 0.3 * sp && c.x0 <= row.x1 + 0.8 * sp && c.x1 - c.x0 <= 0.6 * sp && c.y1 - c.y0 >= 0.4 * sp &&
          (above ? c.y0 >= row.y - 0.3 * sp && c.y0 <= row.y + 0.3 * sp : c.y1 >= row.y - 0.3 * sp && c.y1 <= row.y + 0.3 * sp));
        const x0 = num.x0 - 0.3 * sp, x1 = row.x1 + 0.8 * sp;
        let n = 0;
        for (const ch of s.chords) if (ch.x >= x0 && ch.x <= x1) for (const h of ch.heads) { h.ott = k; n++; }
        if (!hook && st.right - row.x1 < 3 * sp) next.set(si, { k: num.k, above, dy: row.y - top });
        if (num.cont) open.delete(si);
        (s.ottavas ||= []).push({ x0, x1, k });
        stats.lines = (stats.lines || 0) + 1;
        stats.heads = (stats.heads || 0) + n;
      }
      // a line run on from the system before that is too short for dashes here: its number again
      // ("15ma") and the hook at the height the line had; the notes up to the hook are under it
      const o = open.get(si);
      if (o && !(s.ottavas || []).some(v => v.x0 < (s.hdr && s.hdr.end != null ? s.hdr.end : st.left) + 4 * sp)) {
        // (the line's height follows the notes, so the hook is looked for on the number's side of
        // the staff, right after the number: tall glyphs within a space of each other)
        const hk = near.filter(c => c.x0 > st.left && c.x0 < st.left + 16 * sp && c.x1 - c.x0 <= 0.6 * sp && c.y1 - c.y0 >= 0.4 * sp && c.y1 - c.y0 <= 1.4 * sp &&
          (o.above ? c.y1 < top : c.y0 > bot) &&
          near.some(d => d !== c && d.x1 <= c.x0 && c.x0 - d.x1 <= 1.0 * sp && d.y1 - d.y0 >= 0.5 * sp && (o.above ? Math.abs(d.y0 - c.y0) <= 1.0 * sp : Math.abs(d.y1 - c.y1) <= 1.0 * sp)) &&
          near.some(d => d.x1 <= c.x0 && c.x0 - d.x0 <= 6 * sp && d.y1 - d.y0 >= 0.8 * sp && holes(R, d) !== 1))
          .sort((a, b) => a.x0 - b.x0)[0];
        if (hk) {
          const k = o.above ? o.k : -o.k;
          for (const ch of s.chords) if (ch.x <= hk.x1 + 0.3 * sp) for (const h of ch.heads) h.ott = k;
          (s.ottavas ||= []).push({ x0: st.left, x1: hk.x1, k });
          stats.lines = (stats.lines || 0) + 1;
        }
      }
    });
    open = next;
  }
  return stats;
}

module.exports = { readOttavas, holes, _dashRows: dashRows };
