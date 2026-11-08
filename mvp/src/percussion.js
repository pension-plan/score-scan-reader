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
    const c = percussionClef(fr, asm, s);
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

module.exports = { percussionClef, markPercussion, KIT, kitAt };
