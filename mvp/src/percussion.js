'use strict';
// Percussion staves: the percussion clef (two upright bars across the middle of the staff) and
// the drum kit a drum-set staff's positions stand for. A staff with that clef is read like a
// treble staff for its positions (display step and octave); score.js writes its notes as
// <unpitched> with the kit instrument of each position.

// The percussion clef at the start of staff s (assemble.js system staff: s.st, s.hdr): two
// upright bars side by side, each about two spaces tall and centred on the middle line, thin
// (less than half a space), a gap of under a space between them, and no other glyph there
// (a G, F or C clef). Components of the staff-removed image (asm.comps) are used: the staff
// lines do not join the bars to anything.
function percussionClef(fr, asm, s) {
  const st = s.st, sp = st.space || fr.ss, comps = asm.comps || [];
  const x0 = st.left - 0.3 * sp, x1 = st.left + 4 * sp;
  const mid = (x) => st.yAt(2, x);
  const near = comps.filter((c) => c.x1 >= x0 && c.x0 <= x1 && c.y1 >= st.yAt(0, c.x0) - 2 * sp && c.y0 <= st.yAt(4, c.x0) + 2 * sp);
  const bar = (c) => {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1, cy = (c.y0 + c.y1) / 2;
    return h >= 1.5 * sp && h <= 2.6 * sp && w <= 0.55 * sp && w >= 1 && Math.abs(cy - mid((c.x0 + c.x1) / 2)) <= 0.35 * sp && c.area >= 0.7 * w * h;
  };
  const bars = near.filter(bar).sort((a, b) => a.x0 - b.x0);
  for (let i = 0; i + 1 < bars.length; i++) {
    const a = bars[i], b = bars[i + 1], gap = b.x0 - a.x1 - 1;
    if (gap < 0.1 * sp || gap > 0.9 * sp) continue;
    if (Math.abs(a.y0 - b.y0) > 0.3 * sp || Math.abs(a.y1 - b.y1) > 0.3 * sp) continue;
    // nothing tall before them at the staff start (a clef glyph the bars would be part of)
    const other = near.some((c) => c !== a && c !== b && c.x1 < a.x0 && c.y1 - c.y0 > 2.5 * sp);
    if (other) continue;
    return { x0: a.x0, x1: b.x1 };
  }
  return null;
}

// An x-shaped head (a cymbal or hi-hat) on a percussion staff: the head finder takes it for a
// filled head that is not solid, or for a hollow one half a space off (the hole between its arms
// and a staff line). Ink share inside the head's ellipse on the staff-removed image: a filled head
// is nearly solid, an open (half) note keeps its ring, an x is two thin strokes.
function inkShare(R, h, sp) {
  const rx = 0.5 * sp, ry = 0.38 * sp;
  let n = 0, k = 0;
  for (let y = Math.round(h.y - ry); y <= h.y + ry; y++) for (let x = Math.round(h.x - rx); x <= h.x + rx; x++) {
    const dx = (x - h.x) / rx, dy = (y - h.y) / ry;
    if (dx * dx + dy * dy > 1 || x < 0 || y < 0 || x >= R.width || y >= R.height) continue;
    n++; if (R.data[y * R.width + x]) k++;
  }
  return n ? k / n : 1;
}
// the centre of an x: the ink centroid around the head, without the stem (columns inked from
// top to bottom of the window)
function xCentre(R, h, sp) {
  const x0 = Math.round(h.x - 0.6 * sp), x1 = Math.round(h.x + 0.6 * sp), y0 = Math.round(h.y - 0.8 * sp), y1 = Math.round(h.y + 0.8 * sp);
  let sx = 0, sy = 0, n = 0;
  for (let x = Math.max(0, x0); x <= Math.min(R.width - 1, x1); x++) {
    let c = 0;
    for (let y = Math.max(0, y0); y <= Math.min(R.height - 1, y1); y++) if (R.data[y * R.width + x]) c++;
    if (c >= 0.85 * (y1 - y0 + 1)) continue;
    for (let y = Math.max(0, y0); y <= Math.min(R.height - 1, y1); y++) if (R.data[y * R.width + x]) { sx += x; sy += y; n++; }
  }
  return n ? { x: sx / n, y: sy / n } : null;
}

// Mark the staves with a percussion clef: hdr.clef 'perc' (read, not guessed), and the x heads on
// them (h.xHead, its position set from the x's centre). Returns the number of staves.
function markPercussion(fr, asm) {
  let n = 0;
  if (!fr || !asm || !asm.comps) return 0;
  const perc = new Set();
  for (const sy of asm.systems || []) for (const s of sy.staves) {
    if (!s.hdr || (s.hdr.clef && !s.hdr.clefGuessed && s.hdr.clef !== 'perc')) continue;
    // (the front end has already seen the clef on the page: st.perc)
    const c = s.st.perc || percussionClef(fr, asm, s);
    if (!c) continue;
    s.hdr.clef = 'perc';
    s.hdr.clefGuessed = false;
    perc.add(fr.staves.indexOf(s.st));
    n++;
  }
  const R = fr.R;
  if (n && R && R.data) for (const h of fr.heads || []) {
    if (!perc.has(h.staff) || h.xHead) continue;
    const sp = h.sp || fr.ss, f = inkShare(R, h, sp);
    if (!((h.kind === 'filled' && f < 0.8) || (h.kind === 'hollow' && f < 0.36))) continue;
    const c = xCentre(R, h, sp), st = fr.staves[h.staff];
    if (!c || !st) continue;
    const s2 = st.spaceAt ? st.spaceAt(h.x) : sp, ym = st.yAt(2, h.x);
    h.p = Math.round((ym - c.y) / (s2 / 2));
    h.y = ym - (h.p * s2) / 2;
    h.xHead = true;
  }
  return n;
}

// Drum-set positions (display step + octave on a treble-like staff) and their instruments,
// General MIDI percussion keys (0-based; MusicXML <midi-unpitched> is this + 1). An x head on a
// position is the cymbal there.
const KIT = [
  { id: 'bd', name: 'Bass Drum', key: 36, at: ['F4', 'E4'] },
  { id: 'ft', name: 'Floor Tom', key: 41, at: ['A4', 'G4'] },
  { id: 'sn', name: 'Snare Drum', key: 38, at: ['C5', 'B4'] },
  { id: 'tm', name: 'Mid Tom', key: 47, at: ['D5'] },
  { id: 'th', name: 'High Tom', key: 50, at: ['E5'] },
  { id: 'hp', name: 'Pedal Hi-Hat', key: 44, at: ['D4'], x: true },
  { id: 'hh', name: 'Hi-Hat', key: 42, at: ['E5', 'G5'], x: true },
  { id: 'rd', name: 'Ride Cymbal', key: 51, at: ['F5'], x: true },
  { id: 'cr', name: 'Crash Cymbal', key: 49, at: ['A5', 'B5'], x: true },
];
// the kit instrument at a position (step + octave), x: an x-shaped head
function kitAt(step, octave, x) {
  const pos = step + octave;
  return KIT.find((k) => !!k.x === !!x && k.at.includes(pos)) || KIT.find((k) => k.at.includes(pos)) || KIT[2];
}

// ---------------------------------------------------------------- front-end passes
// (front.js: before the heads are found, so they are read like any staff's)

// The percussion clef on the binary page (staff lines still in): at the staff start, two runs of
// columns inked all the way from a space above the middle line to a space below it, and empty
// half a space beyond that (a C clef's bars and a barline run over the whole staff, a G clef
// further still), each under 0.55 space wide, 0.1-0.9 space apart.
function percClefOnPage(B, left, right, yMid, ss) {
  const { width: W, height: H, data } = B;
  const ink = (x, y) => x >= 0 && y >= 0 && x < W && y < H && data[y * W + x];
  const ya = Math.round(yMid - 0.9 * ss), yb = Math.round(yMid + 0.9 * ss);
  const yo = [Math.round(yMid - 1.5 * ss), Math.round(yMid + 1.5 * ss)];
  const isBar = (x) => { for (let y = ya; y <= yb; y++) if (!ink(x, y)) return false; return !ink(x, yo[0]) && !ink(x, yo[1]); };
  const runs = [];
  for (let x = Math.round(left - 0.3 * ss), r = null; x <= Math.min(right, left + 4 * ss); x++) {
    if (isBar(x)) { if (r && r.x1 === x - 1) r.x1 = x; else runs.push(r = { x0: x, x1: x }); }
  }
  for (let i = 0; i + 1 < runs.length; i++) {
    const a = runs[i], b = runs[i + 1], gap = b.x0 - a.x1 - 1;
    if (a.x1 - a.x0 + 1 > 0.55 * ss || b.x1 - b.x0 + 1 > 0.55 * ss) continue;
    if (gap >= 0.1 * ss && gap <= 0.9 * ss) return { x0: a.x0, x1: b.x1 };
  }
  return null;
}

// a staff object with straight lines k = 0..4 at y0 + (k - 2) * ss over [left, right] (a one-line
// staff: its line is line 2); yAt/spaceAt as module functions, as staves.js makes them
function lineAt(k, x) { const d = this.dense[k]; return d[Math.max(0, Math.min(d.length - 1, Math.round(x)))]; }
function spaceOf(x) { return (this.yAt(4, x) - this.yAt(0, x)) / 4; }
function oneLineStaff(W, left, right, a, b, ss) {
  // y of the line at x: a + b * x (fitted on its run)
  const dense = [0, 1, 2, 3, 4].map((k) => { const d = new Float32Array(W); for (let x = 0; x < W; x++) d[x] = a + b * x + (k - 2) * ss; return d; });
  const xs = [left, right], ys = [0, 1, 2, 3, 4].map((k) => xs.map((x) => a + b * x + (k - 2) * ss));
  return { xs, ys, dense, yAt: lineAt, spaceAt: spaceOf, left, right, space: ss, oneLine: true };
}

// One-line percussion staves (a snare or other single drum): a lone thin horizontal line, clear
// of every five-line staff, running most of the width the page's staves run, with the percussion
// clef at its start. Returns the new staves (none on almost every page).
function findOneLineStaves(B, staves, ss, lt) {
  if (!staves.length || !(ss > 0)) return [];
  const { width: W, height: H, data } = B;
  const left = Math.min(...staves.map((s) => s.left)), right = Math.max(...staves.map((s) => s.right));
  const span = right - left;
  if (span < 20 * ss) return [];
  const inStaff = (y) => staves.some((s) => { const xm = (s.left + s.right) / 2; return y > s.yAt(0, xm) - 1.2 * ss && y < s.yAt(4, xm) + 1.2 * ss; });
  const maxT = Math.max(2, Math.round(2 * lt + 1));
  // ink along each row over the staves' width (a scanned line is broken in places)
  const x0s = Math.max(0, Math.round(left)), x1s = Math.min(W - 1, Math.round(right));
  const cov = new Int32Array(H);
  for (let y = 0; y < H; y++) { let n = 0; const o = y * W; for (let x = x0s; x <= x1s; x++) if (data[o + x]) n++; cov[y] = n; }
  const out = [];
  for (let y = 0; y < H;) {
    if (cov[y] < 0.75 * span || inStaff(y)) { y++; continue; }
    let y1 = y;
    while (y1 + 1 < H && cov[y1 + 1] >= 0.75 * span) y1++;
    const ya = y, yb = y1;
    y = y1 + 1;
    if (yb - ya + 1 > maxT) continue; // a thick bar, not a staff line
    // a thin line: the rows just beyond it hold much less ink, and no other line within a space
    const top = Math.max(...Array.from({ length: yb - ya + 1 }, (_, i) => cov[ya + i]));
    if (ya - 2 < 0 || yb + 2 >= H || cov[ya - 2] > 0.6 * top || cov[yb + 2] > 0.6 * top) continue;
    let alone = true;
    for (let d = maxT + 2; d < 1.5 * ss && alone; d++) if ((ya - d >= 0 && cov[ya - d] >= 0.75 * span) || (yb + d < H && cov[yb + d] >= 0.75 * span)) alone = false;
    if (!alone) continue;
    const yl = (ya + yb) / 2;
    // its extent: that of the nearest staff (one system's staves start and end together)
    const nb = staves.slice().sort((u, v) => Math.abs(u.yAt(2, (u.left + u.right) / 2) - yl) - Math.abs(v.yAt(2, (v.left + v.right) / 2) - yl))[0];
    if (!percClefOnPage(B, nb.left, nb.right, yl, ss)) continue;
    out.push(oneLineStaff(W, nb.left, nb.right, yl, 0, ss));
  }
  return out;
}

// x heads (hi-hat, cymbals) on the percussion staves of a page (staff indices `perc`), on the
// staff-removed image: at a staff position, both diagonals of a head-sized square inked (the arms
// of the x; a staff line may cut them) and the middles of its sides mostly empty (not a solid
// head). One per position and place, the best; head objects shaped as heads.js makes them,
// filled with xHead set.
function findXHeads(R, staves, perc, ss) {
  const { width: W, height: H, data } = R;
  const ink = (x, y) => { for (let d = -1; d <= 1; d++) { const yy = y + d; if (x >= 0 && yy >= 0 && x < W && yy < H && data[yy * W + x]) return true; } return false; };
  const out = [];
  for (const k of perc) {
    const st = staves[k];
    if (!st) continue;
    const s2 = st.space || ss, a = Math.max(3, Math.round(0.42 * s2));
    const cands = [];
    for (let p = -6; p <= 10; p++) for (let x = Math.round(st.left + 3 * s2); x <= st.right - a; x++) {
      const y = Math.round(st.yAt(2, x) - (p * s2) / 2);
      let d1 = 0, d2 = 0, n = 0;
      for (let t = -a; t <= a; t++) { n++; if (ink(x + t, y + t)) d1++; if (ink(x + t, y - t)) d2++; }
      if (d1 < 0.75 * n || d2 < 0.75 * n) continue;
      const sides = [ink(x - a, y), ink(x + a, y), ink(x, y - a), ink(x, y + a)].filter(Boolean).length;
      if (sides > 1) continue;
      cands.push({ x, y, p, score: (d1 + d2) / (2 * n) });
    }
    // the best within half a head width and a position of each other
    cands.sort((u, v) => v.score - u.score || u.x - v.x);
    const kept = [];
    for (const c of cands) if (!kept.some((o) => Math.abs(o.x - c.x) < 0.8 * s2 && Math.abs(o.p - c.p) <= 1)) kept.push(c);
    for (const c of kept) {
      const s = st.spaceAt ? st.spaceAt(c.x) : s2;
      out.push({ x: c.x, y: st.yAt(2, c.x) - (c.p * s) / 2, staff: k, p: c.p, sp: s, kind: 'filled', score: +c.score.toFixed(3), w: 2 * a + 1, blob: -1 - out.length, x0: c.x - a, x1: c.x + a, xHead: true });
    }
  }
  return out;
}

module.exports = { percussionClef, markPercussion, KIT, kitAt, percClefOnPage, findOneLineStaves, findXHeads };
