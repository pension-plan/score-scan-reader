'use strict';
// Barline detection: thin vertical ink spanning a staff from top to bottom line
// (on the staff-removed binary), whose full vertical extent ends at the staff
// edges or continues to a neighbouring staff of the same system (span bars),
// and that is not a stem of a detected notehead.

function detectBarlines(R, staves, heads, ss, opts = {}) {
  const { width: w, height: h, data } = R;
  const out = [];
  const minCover = opts.minCover ?? 0.9;
  const maxGap = Math.max(1, Math.round(0.1 * ss));
  for (const st of staves) {
    const cols = [];
    for (let x = Math.max(0, st.left); x <= Math.min(w - 1, st.right); x++) {
      const y0 = Math.round(st.yAt(0, x)), y1 = Math.round(st.yAt(4, x));
      let n = 0;
      for (let y = y0; y <= y1; y++) n += data[y * w + x];
      cols.push(n >= minCover * (y1 - y0 + 1));
    }
    // group into segments
    const segs = [];
    for (let i = 0; i < cols.length; i++) {
      if (!cols[i]) continue;
      let j = i; while (j + 1 < cols.length && cols[j + 1]) j++;
      segs.push({ x0: st.left + i, x1: st.left + j });
      i = j;
    }
    for (const s of segs) {
      const width = s.x1 - s.x0 + 1;
      if (width > 0.9 * ss) continue; // too thick: clef/brace/beam cluster
      const xc = Math.round((s.x0 + s.x1) / 2);
      if (xc < st.left + 2.5 * ss) continue; // system start line / bracket (clef always precedes the first barline)
      // vertical extent of the run at xc
      const yt = st.yAt(0, xc), yb = st.yAt(4, xc);
      let top = Math.round(yt), bot = Math.round(yb), gap = 0;
      for (let y = top - 1; y >= 0; y--) { if (data[y * w + xc] || (xc > 0 && data[y * w + xc - 1]) || data[y * w + xc + 1]) { top = y; gap = 0; } else if (++gap > maxGap) break; }
      gap = 0;
      for (let y = bot + 1; y < h; y++) { if (data[y * w + xc] || (xc > 0 && data[y * w + xc - 1]) || data[y * w + xc + 1]) { bot = y; gap = 0; } else if (++gap > maxGap) break; }
      const upOver = (yt - top) / ss, downOver = (bot - yb) / ss;
      const prev = staves[st.index - 1], next = staves[st.index + 1];
      const reachesPrev = prev && prev.system === st.system && top <= prev.yAt(4, xc) + 0.5 * ss;
      const reachesNext = next && next.system === st.system && bot >= next.yAt(0, xc) - 0.5 * ss;
      const okTop = upOver <= 0.6 || reachesPrev;
      const okBot = downOver <= 0.6 || reachesNext;
      if (!okTop || !okBot) continue;
      // reject stems: a notehead touching the segment within the staff band
      const isStem = heads.some(hd => hd.staff === st.index && hd.stem && hd.stem.dir !== 0 &&
        (Math.abs(hd.stem.upX - xc) <= 2 || Math.abs(hd.stem.downX - xc) <= 2) && Math.abs(hd.x - xc) < 1.2 * ss);
      if (isStem) continue;
      // reject if a notehead sits right on the line (stem through a chord etc.)
      const nearHead = heads.some(hd => hd.staff === st.index && Math.abs(hd.x - xc) < 0.55 * ss);
      if (nearHead) continue;
      // header zone: no barline before the first notehead of the staff (clef/key/time strokes)
      const firstHead = heads.reduce((m, hd) => (hd.staff === st.index && hd.x < m ? hd.x : m), 1e9);
      if (xc < firstHead && xc < st.left + 15 * ss) continue;
      out.push({ staff: st.index, x: xc, x0: s.x0, x1: s.x1, top, bot, width, spansSystem: !!(reachesPrev || reachesNext) });
    }
  }
  // merge thin+thick pairs (final / double barlines) within 1.2 ss
  out.sort((a, b) => (a.staff - b.staff) || (a.x - b.x));
  const merged = [];
  for (const b of out) {
    const m = merged[merged.length - 1];
    if (m && m.staff === b.staff && b.x0 - m.x1 <= 1.2 * ss) { m.x1 = b.x1; m.x = Math.round((m.x0 + m.x1) / 2); m.double = true; }
    else merged.push({ ...b });
  }
  return merged;
}

module.exports = { detectBarlines };
