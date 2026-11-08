'use strict';
// Notation assembly: per system and staff -> clef, key, measures, durations,
// voices; then the part layout (closed-score split vs grand staff) for the page.
const { labelComponents } = require('./cc');

// divisions per quarter: 840 = 8 * 3 * 5 * 7 keeps 32nds and 3-, 5-, 6- and
// 7-tuplets whole numbers
const DIV = 840;
const SHARP_ORDER = ['F', 'C', 'G', 'D', 'A', 'E', 'B'];
const FLAT_ORDER = ['B', 'E', 'A', 'D', 'G', 'C', 'F'];

// ---------------------------------------------------------------- symbols ---
function compIndex(R) {
  const { comps } = labelComponents(R);
  return comps.filter(c => c.area >= 4);
}

function strokes(R, c, minRun, strict) {
  // columns with a vertical run >= 0.55 * height (or minRun) -> clustered into strokes
  const { width: w, data } = R;
  const hgt = c.y1 - c.y0 + 1;
  const need = minRun || 0.55 * hgt;
  const cols = [];
  // a stroke may be cut where a staff line was removed: runs are joined over
  // short gaps as long as the gaps stay a small share of the stroke
  const maxGap = strict ? 0 : Math.max(2, 0.22 * hgt);
  for (let x = c.x0; x <= c.x1; x++) {
    let best = 0, bestTop = -1, bestBot = -1, segTop = -1, segBot = -1, gaps = 0, y = c.y0;
    while (y <= c.y1) {
      if (!data[y * w + x]) { y++; continue; }
      let y2 = y; while (y2 + 1 <= c.y1 && data[(y2 + 1) * w + x]) y2++;
      const gap = segBot >= 0 ? y - segBot - 1 : 0;
      if (segBot >= 0 && gap <= maxGap && (gaps + gap) <= 0.2 * (y2 - segTop + 1)) { gaps += gap; segBot = y2; }
      else { segTop = y; segBot = y2; gaps = 0; }
      if (segBot - segTop + 1 > best) { best = segBot - segTop + 1; bestTop = segTop; bestBot = segBot; }
      y = y2 + 1;
    }
    cols.push(best >= need ? { x, top: bestTop, bot: bestBot } : null);
  }
  const out = [];
  for (const c2 of cols) {
    if (!c2) continue;
    const last = out[out.length - 1];
    if (last && c2.x - last.x1 <= 1) { last.x1 = c2.x; last.top = Math.min(last.top, c2.top); last.bot = Math.max(last.bot, c2.bot); }
    else out.push({ x0: c2.x, x1: c2.x, top: c2.top, bot: c2.bot });
  }
  // heavy ink: bars joined across the sign look like one wide stroke; strokes
  // are thin, so fall back to unbroken runs only
  if (!strict && out.some(t => t.x1 - t.x0 + 1 > 0.25 * hgt)) return strokes(R, c, minRun, true);
  return out;
}

// runs of rows (lengths) in box [b] whose ink crosses column cx (+-1 px)
function crossBands(R, b, cx, minRun) {
  const { width: w, data } = R;
  const out = [];
  let run = 0;
  for (let y = b.y0; y <= b.y1 + 1; y++) {
    let on = false;
    if (y <= b.y1) for (let x = cx - 1; x <= cx + 1; x++) if (x >= b.x0 && x <= b.x1 && data[y * w + x]) on = true;
    if (on) run++;
    else { if (run >= minRun) out.push(run); run = 0; }
  }
  return out;
}

// The glyph alone, cropped to its box: only its own components (g.parts, or g
// itself), so a neighbour reaching into the box cannot disturb shape tests.
function glyphImage(R, g) {
  const bw = g.x1 - g.x0 + 1, bh = g.y1 - g.y0 + 1;
  const img = { width: bw, height: bh, data: new Uint8Array(bw * bh) };
  for (let y = 0; y < bh; y++) {
    const o = (y + g.y0) * R.width + g.x0;
    for (let x = 0; x < bw; x++) img.data[y * bw + x] = R.data[o + x];
  }
  const parts = g.parts || [g];
  const { labels, comps } = labelComponents(img);
  const keep = new Uint8Array(comps.length + 2);
  for (const c of comps) {
    if (parts.some(p => p.area === c.area && p.x0 === c.x0 + g.x0 && p.y0 === c.y0 + g.y0 && p.x1 === c.x1 + g.x0 && p.y1 === c.y1 + g.y0)) keep[c.id] = 1;
  }
  for (let i = 0; i < bw * bh; i++) img.data[i] = labels[i] && keep[labels[i]] ? 1 : 0;
  return img;
}

// g: one component or a merged glyph group {x0,y0,x1,y1[,parts]} on R
function classifyAccidental(R, g, sp) {
  const hgt = g.y1 - g.y0 + 1, wid = g.x1 - g.x0 + 1;
  if (hgt < 1.3 * sp || hgt > 3.8 * sp || wid < 0.3 * sp || wid > 1.5 * sp) return null;
  const img = glyphImage(R, g);
  const b = { x0: 0, y0: 0, x1: wid - 1, y1: hgt - 1 };
  const st = strokes(img, b);
  if (st.length >= 2) {
    const a = st[0], c = st[st.length - 1];
    if (c.x0 - a.x1 < Math.max(2, 0.1 * sp)) return null;
    // sharps and naturals have bars joining the two strokes (two, or one
    // long blob when heavy ink merges them); letters ("ll", "H" ...) and
    // neighbouring stems do not
    const bars = crossBands(img, b, Math.round((a.x1 + c.x0) / 2), Math.max(1, 0.1 * sp));
    if (!(bars.length >= 2 || (bars.length === 1 && bars[0] >= 1.1 * sp))) return null;
    if (a.top < c.top - 0.4 * sp && c.bot > a.bot + 0.4 * sp) return 'natural';
    return 'sharp';
  }
  if (st.length === 1 && st[0].x0 < 0.35 * wid && hgt > 1.5 * sp && hgt < 3.4 * sp && wid < 1.25 * sp) {
    // flat: stroke on the left, bowl only in the lower part to its right
    // (a stem-down note has its head at the top instead)
    let n = 0, sy = 0, top = hgt;
    const xs = st[0].x1 + Math.max(2, Math.round(0.2 * sp)); // clear of the stem's ragged edge
    for (let y = 0; y < hgt; y++) for (let x = xs; x < wid; x++) if (img.data[y * wid + x]) { n++; sy += y; if (y < top) top = y; }
    if (n >= 0.08 * sp * sp && top > 0.25 * hgt && sy / n > 0.55 * hgt) return 'flat';
  }
  return null;
}

// Sharps run together by heavy ink (one component holding several signs):
// split at the stroke pairs.  Returns [{kind, x0, y0, x1, y1}] or null.
function splitSharps(R, g, sp) {
  const wid = g.x1 - g.x0 + 1, hgt = g.y1 - g.y0 + 1;
  if (wid < 1.5 * sp || wid > 6 * sp || hgt > 7 * sp) return null;
  const img = glyphImage(R, g);
  const all = { x0: 0, y0: 0, x1: wid - 1, y1: hgt - 1 };
  const st = strokes(img, all, 2.0 * sp, true);
  if (st.length < 4 || st.length % 2) return null;
  const out = [];
  for (let i = 0; i < st.length; i += 2) {
    const a = st[i], b = st[i + 1];
    if (b.x0 - a.x1 < Math.max(2, 0.1 * sp) || b.x0 - a.x1 > 0.9 * sp || a.bot - a.top > 3.8 * sp || b.bot - b.top > 3.8 * sp) return null;
    const bars = crossBands(img, all, Math.round((a.x1 + b.x0) / 2), Math.max(1, 0.1 * sp));
    if (!(bars.length >= 2 || (bars.length === 1 && bars[0] >= 1.1 * sp))) return null;
    out.push({ kind: 'sharp', x0: g.x0 + a.x0, x1: g.x0 + b.x1, y0: g.y0 + Math.min(a.top, b.top), y1: g.y0 + Math.max(a.bot, b.bot) });
  }
  return out;
}

const boxOf = (cs) => cs.reduce((b, c) => ({ x0: Math.min(b.x0, c.x0), y0: Math.min(b.y0, c.y0), x1: Math.max(b.x1, c.x1), y1: Math.max(b.y1, c.y1) }),
  { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity });

// Group components (sorted by x0) into glyphs: horizontally overlapping parts,
// plus a flat's bowl cut off its stem by staff-line removal.
function groupGlyphs(cs, sp) {
  const out = [];
  for (const c of cs) {
    const g = out[out.length - 1];
    if (g) {
      const gw = g.x1 - g.x0 + 1, gh = g.y1 - g.y0 + 1;
      const ov = Math.min(c.x1, g.x1) - Math.max(c.x0, g.x0);
      const vnear = c.y0 <= g.y1 + 0.5 * sp && c.y1 >= g.y0 - 0.5 * sp; // not a sign stacked above / below
      const overlap = vnear && (ov >= 0.15 * sp || ov >= 0.6 * (c.x1 - c.x0));
      const bowl = gw < 0.45 * sp && gh > 1.4 * sp && c.x0 - g.x1 < 0.5 * sp && (c.x1 - c.x0) < 0.9 * sp &&
        (c.y1 - c.y0) < 1.5 * sp && c.y0 > g.y0 + 0.35 * gh && c.y1 < g.y1 + 0.5 * sp;
      if (overlap || bowl) { g.parts.push(c); Object.assign(g, boxOf(g.parts)); continue; }
    }
    out.push({ parts: [c], x0: c.x0, y0: c.y0, x1: c.x1, y1: c.y1 });
  }
  return out;
}

// diatonic index (7 * octave + step) of the middle line: D3 (bass), B3
// (treble 8vb), B4 (treble); C clefs 'C1'..'C5' put C4 on line 1..5
function clefBase(clef) {
  if (clef === 'F') return 22;
  if (clef === 'G8') return 27;
  if (/^C[1-5]$/.test(clef || '')) return 28 - 2 * (+clef[1] - 3);
  return 34;
}

// staff steps above the middle line where key-signature accidentals sit
const KEY_POS = { G: { sharp: [4, 1, 5, 2, -1, 3, 0], flat: [0, 3, -1, 2, -2, 1, -3] } };
KEY_POS.F = { sharp: KEY_POS.G.sharp.map(p => p - 2), flat: KEY_POS.G.flat.map(p => p - 2) };
// C clefs: the treble pattern moved to the clef, each sign kept nearest its
// treble place; tenor clef writes its first sharp low (F3)
KEY_POS.C3 = { sharp: [3, 0, 4, 1, -2, 2, -1], flat: [-1, 2, -2, 1, -3, 0, -4] };
KEY_POS.C4 = { sharp: [-2, 2, -1, 3, 0, 4, 1], flat: [1, 4, 0, 3, -1, 2, -2] };
for (const k of ['C1', 'C2', 'C5']) {
  const shift = 34 - clefBase(k);
  const move = (t) => [t + shift - 14, t + shift - 7, t + shift, t + shift + 7].reduce((a, b) => (Math.abs(b - t) < Math.abs(a - t) ? b : a));
  KEY_POS[k] = { sharp: KEY_POS.G.sharp.map(move), flat: KEY_POS.G.flat.map(move) };
}
const keyPosFor = (clef) => KEY_POS[clef] || KEY_POS[clef === 'F' ? 'F' : 'G'];

// accidental's staff position: sharps/naturals are centred on it, a flat's
// bowl sits at the bottom of the glyph
function accPos(st, g, kind, sp) {
  const x = (g.x0 + g.x1) / 2;
  const yc = kind === 'flat' ? g.y1 - 0.55 * sp : (g.y0 + g.y1) / 2;
  return (st.yAt(2, x) - yc) / (sp / 2);
}

// share of rows in [ya, yb] whose ink spans >= minW (rows outside count empty)
function wideRows(img, ya, yb, minW) {
  const { width: w, height: h, data } = img;
  let n = 0, tot = 0;
  for (let y = Math.round(ya); y <= Math.round(yb); y++) {
    tot++;
    if (y < 0 || y >= h) continue;
    let l = -1, r = -1;
    for (let x = 0; x < w; x++) if (data[y * w + x]) { if (l < 0) l = x; r = x; }
    if (l >= 0 && r - l + 1 >= minW) n++;
  }
  return tot ? n / tot : 0;
}

// time signature: two stacked digits filling the staff height (or C / cut C)
function isTimeSig(R, st, g, sp) {
  const x = (g.x0 + g.x1) / 2, y0 = st.yAt(0, x) - g.y0, y2 = st.yAt(2, x) - g.y0, y4 = st.yAt(4, x) - g.y0;
  const wid = (g.x1 - g.x0 + 1) / sp, hgt = (g.y1 - g.y0 + 1) / sp;
  if (wid < 0.7 || wid > 3.2 || hgt > 5.2) return false;
  const img = glyphImage(R, g);
  if (Math.abs(y0) < 0.55 * sp && Math.abs(g.y1 - g.y0 - y4) < 0.55 * sp) {
    return wideRows(img, y0 + 0.2 * sp, y2 - 0.2 * sp, 0.4 * sp) >= 0.6 && wideRows(img, y2 + 0.2 * sp, y4 - 0.2 * sp, 0.4 * sp) >= 0.6;
  }
  // common time: a 'C' about two spaces high centred on the middle line;
  // cut time adds a vertical stroke through it
  const cy = (g.y1 - g.y0) / 2;
  if (Math.abs(cy - y2) < 0.5 * sp && wid >= 0.9 && wid <= 2.0 && hgt >= 1.6) {
    return wideRows(img, y2 - 0.7 * sp, y2 + 0.7 * sp, 0.25 * sp) >= 0.9 && wideRows(img, y2 - 0.8 * sp, y2 - 0.6 * sp, 0.8 * sp) > 0;
  }
  return false;
}

// back of a common-time C (a thick crescent from the second to the fourth
// line); with a stroke through the whole staff it is cut time
function commonTime(st, g, sp) {
  const x = (g.x0 + g.x1) / 2, y1 = st.yAt(1, x), y3 = st.yAt(3, x);
  const wid = (g.x1 - g.x0 + 1) / sp, hgt = (g.y1 - g.y0 + 1) / sp;
  const fill = g.parts ? g.parts.reduce((a, c) => a + c.area, 0) / ((g.x1 - g.x0 + 1) * (g.y1 - g.y0 + 1)) : 0;
  if (wid >= 0.35 && wid <= 1.0 && hgt >= 1.7 && hgt <= 2.7 && fill > 0.45 &&
      Math.abs(g.y0 - y1) < 0.4 * sp && Math.abs(g.y1 - y3) < 0.4 * sp) return 'common';
  return null;
}

// Header of a staff: clef, key signature, time signature, read left to right
// from the staff start.  The parse stops at the first glyph that is none of
// these, so noteheads never count; header.end marks where the music starts
// (heads detected left of it are header glyphs misread as notes).
// Clef at the start of a staff from the components near it.
// Returns {clef, clefOct, clefEnd} (clef null when none is recognised).
function readClef(R, near, left, lineY, sp, yTop, yBot) {
  // tall glyphs at the staff start, centred on this staff (not the clef of
  // the staff above / below reaching into the search band)
  const tall = near.filter(c => c.x0 < left + 2.5 * sp && c.x0 >= left - 0.5 * sp && (c.y1 - c.y0) > 2.4 * sp && (c.x1 - c.x0) > 0.6 * sp && (c.y1 - c.y0) < 9 * sp &&
    (c.y0 + c.y1) / 2 > lineY(0) - 1.5 * sp && (c.y0 + c.y1) / 2 < lineY(4) + 1.5 * sp).sort((a, b) => (b.y1 - b.y0) - (a.y1 - a.y0));
  let first = null;
  for (const c0 of tall) {
    const r = clefFrom(R, near, c0, left, lineY, sp, yTop, yBot);
    if (r.clef) return r;
    if (!first) first = r;
  }
  return first || { clef: null, clefOct: 0, clefEnd: left };
}

function clefFrom(R, near, c0, left, lineY, sp, yTop, yBot) {
  let clef = null, clefOct = 0, clefEnd = left;
  // pieces of the clef cut apart by staff-line removal: overlapping it in x
  // and touching it vertically (not text or slurs further away)
  const parts = [c0];
  let cb = boxOf(parts), grew = true;
  while (grew) {
    grew = false;
    for (const c of near) {
      if (parts.includes(c) || c.x0 > cb.x1 - 0.1 * sp || c.x1 < cb.x0 + 0.1 * sp || (c.x1 - c.x0) > 3.5 * sp) continue;
      if (c.y0 < yTop || c.y1 > yBot) continue; // brace, system barline, text lines
      if (c.y0 > cb.y1 + 0.6 * sp || c.y1 < cb.y0 - 0.6 * sp) continue;
      parts.push(c); cb = boxOf(parts); grew = true;
    }
  }
  const top = (cb.y0 - lineY(0)) / sp, bot = (cb.y1 - lineY(4)) / sp, hgt = (cb.y1 - cb.y0) / sp;
  // G: from well above the staff to below it; F: from the top line down
  // to about the fourth line (its dots follow); C: two full-height bars on
  // the left, centred on the line it names
  if (hgt > 5.2 && hgt < 9.5 && top < -0.6 && bot > 0.4) clef = 'G';
  else if (hgt > 3.3 && hgt < 5.4 && top > -2.6 && top < 0.6 && bot > -2.6 && bot < 2.6 && cClefBars(R, cb, parts, sp)) {
    const p = Math.round((lineY(2) - (cb.y0 + cb.y1) / 2) / sp); // lines from the middle
    // an F clef's two dots to its right in the spaces around the fourth line
    const dots = near.filter(c => c.x0 > cb.x1 - 0.2 * sp && c.x0 < cb.x1 + 0.8 * sp && (c.x1 - c.x0) < 0.7 * sp && (c.y1 - c.y0) < 0.7 * sp &&
      c.y0 > lineY(0) - 0.3 * sp && c.y1 < lineY(2) + 0.3 * sp).length;
    if (Math.abs(p) <= 2 && dots < 2) clef = 'C' + (3 + p);
  }
  else if (hgt > 2.4 && hgt < 4.6 && top > -0.8 && top < 1.3 && bot > -2.0 && bot < 1.1) clef = 'F';
  clefEnd = cb.x1;
  if (clef === 'G') {
    // small "8" hanging under the clef: octave-transposing (tenor) treble clef
    const eight = near.find(c => c.y0 > cb.y1 - 0.2 * sp && c.y0 < cb.y1 + 0.8 * sp && c.x0 >= cb.x0 - 0.2 * sp && c.x1 <= cb.x1 + 0.2 * sp &&
      (c.y1 - c.y0) > 0.5 * sp && (c.y1 - c.y0) < 1.4 * sp && (c.x1 - c.x0) > 0.3 * sp && (c.x1 - c.x0) < 1.0 * sp);
    if ((eight && c0.y1 < lineY(4) + 2.2 * sp) || cb.y1 > lineY(4) + 2.05 * sp) clefOct = -1;
  }
  if (clef === 'F') {
    // the two dots right of the bass clef
    for (const c of near) {
      if (c.x0 > clefEnd - 0.2 * sp && c.x0 < clefEnd + 0.8 * sp && (c.x1 - c.x0) < 0.7 * sp && (c.y1 - c.y0) < 0.7 * sp &&
          c.y0 > lineY(0) - 0.3 * sp && c.y1 < lineY(2) + 0.3 * sp) clefEnd = Math.max(clefEnd, c.x1);
    }
  }
  return { clef, clefOct, clefEnd };
}

// C clef: its left part holds vertical bars running nearly its full height
// (an F clef's curve and a G clef's spine do not reach that far down), and
// it is symmetric about its centre line (an F clef is heavy at the top)
function cClefBars(R, cb, parts, sp) {
  const g = { ...cb, parts };
  const img = glyphImage(R, g);
  const w = img.width, h = img.height;
  const st = strokes(img, { x0: 0, y0: 0, x1: Math.max(0, Math.round(w * 0.4)), y1: h - 1 }, 0.85 * h);
  if (!st.length || st[0].x0 >= 0.3 * w) return false;
  let top = 0, bot = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (img.data[y * w + x]) { if (y < h / 2) top++; else bot++; }
  return bot > 0 && top / bot > 0.75 && top / bot < 1.33;
}

// The page's components near a staff start with the system's barline (or a
// bracket / brace touching the clef) cut away: a clef drawn against the
// barline is one component with it otherwise.
function detachedNear(R, st, left, lineY, sp, limitX) {
  const x0 = Math.max(0, Math.round(left - 1.2 * sp)), x1 = Math.min(R.width - 1, Math.round(Math.min(limitX, left + 6 * sp)));
  const y0 = Math.max(0, Math.round(lineY(0) - 3.5 * sp)), y1 = Math.min(R.height - 1, Math.round(lineY(4) + 3.5 * sp));
  const w = x1 - x0 + 1, h = y1 - y0 + 1;
  if (w < 4 || h < 4) return [];
  const img = { width: w, height: h, data: new Uint8Array(w * h) };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) img.data[y * w + x] = R.data[(y + y0) * R.width + x + x0];
  // barline columns: ink through (nearly) the whole staff, near its start
  // (staff-line removal may have nicked it)
  const ya = Math.max(0, Math.round(lineY(0) - y0 - 0.3 * sp)), yb = Math.min(h - 1, Math.round(lineY(4) - y0 + 0.3 * sp));
  const xe = Math.min(w - 1, Math.round(left + 0.6 * sp - x0));
  let cut = 0;
  for (let x = 0; x <= xe; x++) {
    let n = 0;
    for (let y = ya; y <= yb; y++) if (img.data[y * w + x]) n++;
    if (n >= 0.85 * (yb - ya + 1)) {
      for (let y = 0; y < h; y++) img.data[y * w + x] = 0;
      if (x + 1 < w) for (let y = 0; y < h; y++) img.data[y * w + x + 1] = 0;
      cut++;
    }
  }
  if (!cut) return [];
  const { comps } = labelComponents(img);
  // pieces cut by the crop's own border are partial: flagged
  return comps.filter(c => c.area >= 4).map(c => ({ ...c, x0: c.x0 + x0, x1: c.x1 + x0, y0: c.y0 + y0, y1: c.y1 + y0, edge: c.x1 === w - 1 || c.y0 === 0 || c.y1 === h - 1 }));
}

// Header of a staff: clef, key signature, time signature, read left to right
// from the staff start.  The parse stops at the first glyph that is none of
// these, so noteheads never count; header.end marks where the music starts
// (heads detected left of it are header glyphs misread as notes).
function analyseHeader(R, comps, st, limitX, trace) {
  const sp = st.spaceAt(st.left), left = st.left;
  const lineY = (k) => st.yAt(k, left + 4 * sp);
  const yTop = lineY(0) - 3 * sp, yBot = lineY(4) + 3 * sp;
  let near = comps.filter(c => c.x1 >= left - 0.5 * sp && c.x0 < limitX && c.y1 > yTop && c.y0 < yBot);
  let { clef, clefOct, clefEnd } = readClef(R, near, left, lineY, sp, yTop, yBot);
  if (!clef) {
    // a clef touching the system barline / brace: read it with those cut away
    // (pieces of that one component only: whole components are in near)
    const same = (a, b) => a.x0 === b.x0 && a.y0 === b.y0 && a.x1 === b.x1 && a.y1 === b.y1;
    const det = detachedNear(R, st, left, lineY, sp, limitX).filter(c => !c.edge && !near.some(o => same(o, c)));
    if (det.length) {
      const r = readClef(R, near.concat(det), left, lineY, sp, yTop, yBot);
      if (r.clef) { ({ clef, clefOct, clefEnd } = r); near = near.concat(det); }
    }
  }
  // glyphs after the clef, ignoring text well above / below the staff
  const cand = near.filter(c => c.x0 > clefEnd + 0.05 * sp && c.area >= 0.04 * sp * sp &&
    (c.y0 + c.y1) / 2 > lineY(0) - 1.6 * sp && (c.y0 + c.y1) / 2 < lineY(4) + 1.6 * sp).sort((a, b) => a.x0 - b.x0);
  const glyphs = groupGlyphs(cand, sp);
  // expected accidental positions; both clefs stay possible when unread
  let kcs = clef ? [keyPosFor(clef)] : [KEY_POS.G, KEY_POS.F];
  let kind = null, n = 0, end = clefEnd, time = null;
  for (let gi = 0; gi < glyphs.length; gi++) {
    let g = glyphs[gi];
    if ((g.x1 - g.x0) < 0.25 * sp && (g.y1 - g.y0) < 0.4 * sp) continue; // specks
    if (g.x0 - end > 2.2 * sp) break;
    let k = g.kind || classifyAccidental(R, g, sp);
    if (!k && kind !== 'flat') {
      const pieces = splitSharps(R, g, sp);
      if (pieces) { glyphs.splice(gi, 1, ...pieces); g = glyphs[gi]; k = g.kind; }
    }
    if (trace) trace.push({ x: +((g.x0 - left) / sp).toFixed(2), x1: +((g.x1 - left) / sp).toFixed(2), y: +((g.y0 - lineY(0)) / sp).toFixed(2), y1: +((g.y1 - lineY(0)) / sp).toFixed(2), parts: g.parts ? g.parts.length : 0, k, p: k ? +accPos(st, g, k, sp).toFixed(2) : null, t: isTimeSig(R, st, g, sp) });
    if ((k === 'sharp' || k === 'flat') && (kind === null || kind === k) && n < 7) {
      const p = accPos(st, g, k, sp);
      const ok = kcs.filter(kc => Math.abs(p - kc[k][n]) <= 1.2);
      if (ok.length) { kcs = ok; kind = k; n++; end = g.x1; continue; }
      break;
    }
    if (isTimeSig(R, st, g, sp)) { time = { x0: g.x0, x1: g.x1 }; end = g.x1; break; }
    const cs = commonTime(st, g, sp);
    if (cs) {
      // the C's arcs lie on staff lines and were removed with them: what is
      // left is its back and the two terminals, within ~1.6 spaces
      let x1 = g.x1;
      for (const o of glyphs.slice(gi + 1)) if (o.x0 < g.x0 + 1.7 * sp && (o.y1 - o.y0) < 2.6 * sp && o.y0 > lineY(0) - 0.3 * sp && o.y1 < lineY(4) + 0.3 * sp) x1 = Math.max(x1, o.x1);
      time = { x0: g.x0, x1, beats: cs === 'cut' ? 2 : 4, type: cs === 'cut' ? 2 : 4, symbol: cs };
      end = x1;
    }
    break;
  }
  return { clef: clef === 'G' && clefOct === -1 ? 'G8' : clef, clefOct, fifths: kind === 'flat' ? -n : n, end: end + 0.2 * sp, keyN: n, time, mid: lineY(2) };
}

// --------------------------------------------------------------- duration ---
function countBeams(R, x, tip, dir, sp) {
  // count horizontal bars crossing columns beside the stem tip
  const { width: w, height: h, data } = R;
  let best = 0;
  for (const off of [-0.7, -0.45, 0.45, 0.7]) {
    const cx = Math.round(x + off * sp);
    if (cx < 0 || cx >= w) continue;
    let n = 0, run = 0, linked = false;
    const span = Math.round(1.6 * sp);
    // the bar must touch the stem (text near a stem tip does not)
    const nx = Math.round(x + Math.sign(off) * 0.15 * sp);
    for (let i = -2; i <= span; i++) {
      const y = Math.round(tip + dir * i);
      const on = y >= 0 && y < h && data[y * w + cx];
      if (on) { run++; if (data[y * w + nx] || data[y * w + nx + Math.sign(off)]) linked = true; }
      else { if (run >= 0.22 * sp && run <= 0.9 * sp && linked) n++; run = 0; linked = false; }
    }
    if (run >= 0.22 * sp && run <= 0.9 * sp && linked) n++;
    best = Math.max(best, n);
  }
  return Math.min(3, best);
}

function hasDot(R, hd) {
  const { width: w, height: h, data } = R;
  const sp = hd.sp;
  // the dot sits in a space: on a line head -> look half a space above
  // (lower voice, stem down: in the space below)
  const ys = hd.p % 2 !== 0 ? [hd.y] : hd.stemDir === -1 ? [hd.y - 0.5 * sp, hd.y + 0.5 * sp] : [hd.y - 0.5 * sp];
  for (const yc of ys) {
    for (let x = Math.round(hd.x + 0.85 * sp); x < hd.x + 1.9 * sp; x++) {
      let n = 0, tot = 0;
      for (let dy = -0.2 * sp; dy <= 0.2 * sp; dy++) for (let dx = 0; dx < 0.3 * sp; dx++) {
        const yy = Math.round(yc + dy), xx = Math.round(x + dx);
        tot++; if (yy >= 0 && yy < h && xx < w && data[yy * w + xx]) n++;
      }
      if (n > 0.6 * tot) {
        // isolated: nothing directly above/below (not a stem / head)
        const above = data[Math.round(yc - 0.55 * sp) * w + Math.round(x + 0.15 * sp)];
        const below = data[Math.round(yc + 0.55 * sp) * w + Math.round(x + 0.15 * sp)];
        if (!above && !below) return true;
      }
    }
  }
  return false;
}

function headDuration(R, hd, chord) {
  const sp = hd.sp;
  let q;
  const dir = hd.stemDir;
  if (hd.kind === 'hollow') q = dir === 0 ? 4 : 2;
  else {
    q = 1;
    const useUp = dir === 1 || (dir === 2) || (dir !== -1 && chord.up);
    const x = useUp ? chord.upX : chord.downX;
    const tip = useUp ? chord.upEnd : chord.downEnd;
    if (x >= 0 && tip != null) {
      const nb = countBeams(R, x, tip, useUp ? 1 : -1, sp);
      q = q / Math.pow(2, nb);
    }
  }
  const dot = hasDot(R, hd);
  return { q: dot ? q * 1.5 : q, dots: dot ? 1 : 0 };
}

// ---------------------------------------------------------------- tuplets ---
// A tuplet is read from its number: a small isolated digit printed beyond the
// beam of a beamed group, or in the gap of a bracket.  The notes it covers
// (its bracket's span, else the part of the beam nearest to it) give the
// ratio from their notated length in units of the shortest note:
// 3 -> 3:2, 5 -> 5:4, 6 -> 6:4, 7 -> 7:4.
const TUPLET = { 3: 2, 5: 4, 6: 4, 7: 4 };

function digitLike(c, sp) {
  const w = (c.x1 - c.x0 + 1) / sp, h = (c.y1 - c.y0 + 1) / sp;
  if (h < 0.7 || h > 2.0 || w < 0.35 || w > 1.5 || h / w < 0.9) return false;
  const fill = c.area / ((c.x1 - c.x0 + 1) * (c.y1 - c.y0 + 1));
  return fill > 0.2 && fill < 0.92;
}

// thin horizontal piece: half of a tuplet bracket (with its end hook)
function bracketLike(c, sp) {
  const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
  return w >= 0.7 * sp && w <= 10 * sp && h <= 1.3 * sp && h < 0.8 * w && c.area <= 0.55 * w * h;
}

// no glyph close beside it at its height: a lyric syllable or a word is a
// row of letters, a tuplet number stands alone (bracket halves aside)
function isolated(n, comps, sp) {
  const h = n.y1 - n.y0 + 1;
  return !comps.some(c => c !== n && c.area >= 0.04 * sp * sp && (c.x1 - c.x0) < 3 * sp && !bracketLike(c, sp) &&
    c.y1 > n.y0 + 0.25 * h && c.y0 < n.y1 - 0.25 * h && c.x1 >= n.x0 - 0.45 * sp && c.x0 <= n.x1 + 0.45 * sp);
}

// the stem a head's duration was read from: 1 up, -1 down
const durDir = (h) => (h.stemDir === -1 ? -1 : 1);

// Stems hanging from a beam between xa and xb: columns whose ink runs on from
// the beam well past the beams' own depth (dir 1: beam above the heads).
function stemsUnder(R, beamY, dir, xa, xb, sp) {
  const { width: w, height: h, data } = R;
  const gapMax = Math.max(2, Math.round(0.3 * sp));
  const reach = [];
  for (let x = Math.max(0, Math.round(xa)); x <= Math.min(w - 1, Math.round(xb)); x++) {
    const y0 = Math.round(beamY(x) - dir * 0.15 * sp);
    let r = 0, gap = 0;
    for (let k = 0; k < 6 * sp; k++) {
      const yy = y0 + dir * k;
      if (yy < 0 || yy >= h) break;
      if (data[yy * w + x]) { r = k; gap = 0; } else if (++gap > gapMax) break;
    }
    reach.push([x, r]);
  }
  if (!reach.length) return 0;
  const need = Math.max(2.2 * sp, median(reach.map(v => v[1])) + 1.0 * sp);
  let n = 0, last = -1e9;
  for (const [x, r] of reach) if (r >= need) { if (x - last > 0.4 * sp) n++; last = x; }
  return n;
}

// Beamed groups of a staff: stems whose tips touch one component (the beam).
// A stem inside a group's span that ends at its beam but read no beam (cut
// stem, faint beam) is a beamed note too: its value is read again at the beam.
function beamGroups(R, labels, s, sp) {
  const W = R.width;
  const items = [];
  for (const c of s.chords) {
    for (const dir of [1, -1]) {
      const heads = c.heads.filter(h => h.dur && durDir(h) === dir && h.stemDir !== 0);
      if (!heads.length) continue;
      const x = dir === 1 ? c.upX : c.downX, tip = dir === 1 ? c.upEnd : c.downEnd;
      if (!(x >= 0) || tip == null || !(dir === 1 ? c.up : c.down)) continue;
      // the component at the stem tip (beam, flag or the stem itself)
      let lab = 0;
      for (let r = 0; r <= 3 && !lab; r++) for (let dy = -r; dy <= r && !lab; dy++) for (let dx = -r; dx <= r && !lab; dx++) {
        const xx = Math.round(x + dx), yy = Math.round(tip + dy);
        if (xx >= 0 && yy >= 0 && xx < W && yy < R.height && R.data[yy * W + xx]) lab = labels[yy * W + xx];
      }
      items.push({ dir, x, tipY: tip, q: heads[0].dur.q, heads, lab });
    }
  }
  const byLab = new Map();
  for (const it of items) if (it.lab && it.q <= 0.5 + 1e-6) {
    const k = it.lab + ':' + it.dir;
    if (!byLab.has(k)) byLab.set(k, []);
    byLab.get(k).push(it);
  }
  const groups = [];
  const inGroup = new Set();
  for (const g of byLab.values()) {
    if (g.length < 2) continue;
    g.sort((a, b) => a.x - b.x);
    g.forEach(it => inGroup.add(it));
    groups.push(g);
  }
  for (const g of groups) {
    // the beam's edge through the stem tips (extended along the end slopes)
    g.beamY = (x) => {
      for (let i = 1; i < g.length; i++) if (x <= g[i].x || i === g.length - 1) {
        const t = (x - g[i - 1].x) / Math.max(1, g[i].x - g[i - 1].x);
        return g[i - 1].tipY + t * (g[i].tipY - g[i - 1].tipY);
      }
      return g[0].tipY;
    };
    const dir = g[0].dir, gx0 = g[0].x, gx1 = g[g.length - 1].x;
    for (const it of items) {
      if (inGroup.has(it) || it.dir !== dir || it.x <= gx0 + 0.3 * sp || it.x >= gx1 - 0.3 * sp || it.q < 1 - 1e-6) continue;
      if (it.heads.some(h => h.kind === 'hollow')) continue;
      const by = g.beamY(it.x);
      // the stem stops short of the beam or runs into it
      if (Math.abs(it.tipY - by) > 2.5 * sp) continue;
      const nb = countBeams(R, it.x, by, dir, sp);
      if (!nb) continue;
      const q = 1 / Math.pow(2, nb);
      for (const h of it.heads) h.dur = { q: h.dur.dots ? q * 1.5 : q, dots: h.dur.dots };
      it.q = it.heads[0].dur.q; it.tipY = by;
      inGroup.add(it); g.push(it);
    }
    g.sort((a, b) => a.x - b.x);
    // where the beam itself ends (a missed note at either end still has its
    // stem under it)
    const ink = (x) => {
      const by = g.beamY(x);
      for (let k = -0.2 * sp; k <= 0.6 * sp; k++) {
        const yy = Math.round(by + dir * k);
        if (x >= 0 && x < W && yy >= 0 && yy < R.height && R.data[yy * W + x]) return true;
      }
      return false;
    };
    const walk = (x, step) => {
      let gap = 0, last = x;
      for (let xx = Math.round(x); Math.abs(xx - x) < 12 * sp; xx += step) {
        if (ink(xx)) { last = xx; gap = 0; } else if (++gap > 0.3 * sp) break;
      }
      return last;
    };
    g.x0 = walk(g[0].x, -1); g.x1 = walk(g[g.length - 1].x, 1);
  }
  return { items, groups };
}

// Mark tuplets on one staff: rescales the covered heads' dur and drops
// stemless 'heads' found on a tuplet number.
function markTuplets(R, comps, s, sp, items, groups) {
  const st = s.st;
  if (items.length < 2) return;
  const allHeads = s.chords.flatMap(c => c.heads);
  const xm = (st.left + st.right) / 2, y0 = st.yAt(0, xm), y4 = st.yAt(4, xm);
  // candidate numbers near this staff, not on a real notehead (a stemless
  // 'hollow head' found on a number is the number)
  const nums = comps.filter(c => c.x0 > s.hdr.end && c.y1 > y0 - 7 * sp && c.y0 < y4 + 7 * sp && digitLike(c, sp) &&
    !allHeads.some(h => h.stemDir !== 0 && Math.abs(h.x - (c.x0 + c.x1) / 2) < 0.6 * sp && Math.abs(h.y - (c.y0 + c.y1) / 2) < 0.6 * sp) &&
    isolated(c, comps, sp));
  if (!nums.length) return;
  for (const n of nums) {
    const cy = (n.y0 + n.y1) / 2;
    const side = comps.filter(c => c !== n && bracketLike(c, sp) && c.y0 < cy + 0.3 * sp && c.y1 > cy - 0.9 * sp && c.y1 < n.y1 + 0.9 * sp && c.y0 > n.y0 - 0.9 * sp);
    const L = side.find(c => c.x1 <= n.x0 + 0.3 * sp && c.x1 >= n.x0 - 1.2 * sp);
    const Rt = side.find(c => c.x0 >= n.x1 - 0.3 * sp && c.x0 <= n.x1 + 1.2 * sp);
    n.br = L && Rt ? { x0: L.x0, x1: Rt.x1 } : null;
  }
  const used = new Set(), claimed = new Set();
  // its: the notes found under the number; total: notes counted there
  // (stems under the beam: a missed notehead still has its stem)
  const tryTuplet = (its, n, total) => {
    its = its.filter(it => !claimed.has(it));
    if (!its.length) return;
    const minq = Math.min(...its.map(it => it.q));
    const u = its.reduce((a, it) => a + it.q, 0) / minq;
    if (Math.abs(u - Math.round(u)) > 0.01) return;
    const U = Math.round(u) + Math.max(0, (total || 0) - its.length);
    if (U < 2 || (U === 2 && its.length < 2)) return;
    const equal = its.every(it => Math.abs(it.q - minq) < 1e-6);
    const actual = U === 3 ? 3 : equal && TUPLET[U] ? U : 0;
    if (!actual) return;
    const normal = TUPLET[actual];
    for (const it of its) {
      claimed.add(it);
      for (const h of it.heads) if (!h.dur.tuplet) h.dur = { q: h.dur.q * normal / actual, dots: h.dur.dots, tuplet: { actual, normal } };
    }
    used.add(n);
  };
  for (const g of groups) {
    const dir = g[0].dir, gx0 = g[0].x, gx1 = g[g.length - 1].x;
    const mine = nums.filter(n => {
      if (used.has(n)) return false;
      const cx = (n.x0 + n.x1) / 2;
      if (cx < g.x0 - 0.6 * sp || cx > g.x1 + 0.6 * sp) return false;
      const by = g.beamY(cx), reach = (n.br ? 3.6 : 2.8) * sp;
      return dir === 1 ? n.y1 <= by + 0.3 * sp && n.y0 >= by - reach : n.y0 >= by - 0.3 * sp && n.y1 <= by + reach;
    }).sort((a, b) => a.x0 - b.x0);
    if (!mine.length) continue;
    // notes under a bracket go to its number, the rest to the nearest number
    const parts = mine.map(n => ({ n, its: [] }));
    const free = parts.filter(p => !p.n.br);
    for (const it of g) {
      let p = parts.find(p => p.n.br && it.x >= p.n.br.x0 - 0.5 * sp && it.x <= p.n.br.x1 + 0.5 * sp);
      if (!p && free.length) p = free.reduce((a, b) => (Math.abs((b.n.x0 + b.n.x1) / 2 - it.x) < Math.abs((a.n.x0 + a.n.x1) / 2 - it.x) ? b : a));
      if (p) p.its.push(it);
    }
    for (const p of parts) {
      if (!p.its.length) continue;
      // the span to count stems in: the bracket, the whole beam for a lone
      // number, else the notes assigned
      const xa = p.n.br ? Math.max(g.x0, p.n.br.x0) : parts.length === 1 ? g.x0 : Math.min(...p.its.map(it => it.x));
      const xb = p.n.br ? Math.min(g.x1, p.n.br.x1) : parts.length === 1 ? g.x1 : Math.max(...p.its.map(it => it.x));
      // an unbracketed number is centred on its notes (a lyric letter under
      // a beam is not)
      if (!p.n.br && Math.abs((p.n.x0 + p.n.x1) / 2 - (xa + xb) / 2) > 0.25 * (xb - xa) + 0.4 * sp) continue;
      tryTuplet(p.its, p.n, stemsUnder(R, g.beamY, dir, xa - 0.3 * sp, xb + 0.3 * sp, sp));
    }
  }
  // bracketed numbers over unbeamed notes
  for (const n of nums) {
    if (used.has(n) || !n.br) continue;
    const cy = (n.y0 + n.y1) / 2;
    const its = items.filter(it => it.x >= n.br.x0 - 0.5 * sp && it.x <= n.br.x1 + 0.5 * sp && Math.min(...it.heads.map(h => Math.abs(h.y - cy))) < 8 * sp);
    if (its.length >= 2 && new Set(its.map(it => it.dir)).size === 1) tryTuplet(its, n, 0);
  }
  // numbers read as stemless noteheads are not notes
  if (used.size) {
    const onNum = (h) => h.stemDir === 0 && [...used].some(n => h.x >= n.x0 - 0.2 * sp && h.x <= n.x1 + 0.2 * sp && h.y >= n.y0 - 0.2 * sp && h.y <= n.y1 + 0.2 * sp);
    s.chords = s.chords.map(c => (c.heads.some(onNum) ? { ...c, heads: c.heads.filter(h => !onNum(h)) } : c)).filter(c => c.heads.length);
  }
}

// ---------------------------------------------------------------- systems ---
function systemBarlines(fr, sys) {
  const xs = fr.barlines.filter(b => sys.includes(b.staff)).map(b => b.x).sort((a, b) => a - b);
  const cl = [];
  for (const x of xs) {
    const last = cl[cl.length - 1];
    if (last && x - last.x[last.x.length - 1] < 1.2 * fr.ss) last.x.push(x); else cl.push({ x: [x] });
  }
  return cl.map(c => c.x.reduce((a, b) => a + b, 0) / c.x.length);
}

function pitchOf(clef, p, keyAlter, measAcc) {
  const d = clefBase(clef) + p;
  const step = 'CDEFGAB'[((d % 7) + 7) % 7];
  const octave = Math.floor(d / 7);
  const k = step + octave;
  const alter = measAcc[k] != null ? measAcc[k] : (keyAlter[step] || 0);
  return { step, octave, alter, d };
}

function keyAlters(fifths) {
  const a = {};
  if (fifths > 0) SHARP_ORDER.slice(0, fifths).forEach(s => { a[s] = 1; });
  if (fifths < 0) FLAT_ORDER.slice(0, -fifths).forEach(s => { a[s] = -1; });
  return a;
}

// Find an accidental left of a head; returns 'sharp'|'flat'|'natural'|null
function headAccidental(R, comps, hd, minX = -Infinity, reach = 1.9) {
  const sp = hd.sp;
  // candidate glyphs left of the head (pieces cut by staff-line removal
  // grouped); a chord's accidentals stagger further left
  const near = comps.filter(c => c.x1 <= hd.x - 0.5 * sp && c.x1 >= hd.x - reach * sp && c.x0 > minX &&
    c.y0 < hd.y + 1.6 * sp && c.y1 > hd.y - 2.6 * sp && (c.x1 - c.x0) < 1.6 * sp && (c.y1 - c.y0) < 4 * sp).sort((a, b) => a.x0 - b.x0);
  let best = null, bd = Infinity;
  // single components first; merged groups only add flats cut in two
  const cands = near.concat(groupGlyphs(near, sp).filter(g => g.parts.length > 1));
  for (const g of cands) {
    const k = classifyAccidental(R, g, sp);
    if (!k) continue;
    // the sign's own height: a flat's bowl, the middle of a sharp / natural
    const yc = k === 'flat' ? g.y1 - 0.55 * sp : (g.y0 + g.y1) / 2;
    const dy = Math.abs(yc - hd.y);
    if (dy > 0.55 * sp) continue;
    const d = (hd.x - g.x1) / sp + 2 * dy / sp;
    if (d < bd) { bd = d; best = k; }
  }
  return best;
}

function median(a) { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : 0; }

function assemblePage(fr, pageIndex = 0) {
  const R = fr.R;
  const { labels, comps: allComps } = labelComponents(R);
  const comps = allComps.filter(c => c.area >= 4);
  const warnings = [];
  const systems = [];
  for (const sys of fr.systems) {
    const barX = systemBarlines(fr, sys);
    const staves = sys.map(si => {
      const st = fr.staves[si];
      const chords = fr.chords.filter(c => c.staff === si && c.heads.some(h => fr.heads.includes(h)))
        .map(c => ({ ...c, heads: c.heads.filter(h => fr.heads.includes(h)) })).sort((a, b) => a.x - b.x);
      const hdr = analyseHeader(R, comps, st, st.left + 18 * st.space);
      // heads found on clef / key / time-signature glyphs are not notes
      const music = chords.filter(c => c.x > hdr.end);
      const s = { st, si, chords: music, hdr };
      // durations read once here: tuplets rescale whole groups
      for (const c of music) for (const h of c.heads) if (!h.dur) h.dur = headDuration(R, h, c);
      try {
        const sp = st.space || fr.ss;
        const { items, groups } = beamGroups(R, labels, s, sp);
        markTuplets(R, comps, s, sp, items, groups);
      } catch (e) { warnings.push(`Beam / tuplet reading failed on a staff (${e.message}).`); }
      return s;
    });
    // bass over treble in a two-staff system is a misreading: guess both
    if (staves.length === 2 && staves[0].hdr.clef === 'F' && /^G/.test(staves[1].hdr.clef || '')) {
      staves[0].hdr.clef = null; staves[1].hdr.clef = null;
    }
    staves.forEach((s, i) => {
      if (!s.hdr.clef) {
        s.hdr.clef = staves.length === 2 ? (i === 0 ? 'G' : 'F') : 'G';
        s.hdr.clefGuessed = true;
      }
    });
    // measure boundaries
    const left = Math.min(...staves.map(s => s.st.left)), right = Math.max(...staves.map(s => s.st.right));
    const bounds = [left, ...barX.filter(x => x > left + 2 * fr.ss && x < right - 0.8 * fr.ss), right + 1];
    const measures = [];
    for (let m = 0; m + 1 < bounds.length; m++) {
      const xa = bounds[m], xb = bounds[m + 1];
      const has = staves.some(s => s.chords.some(c => c.x > xa && c.x < xb));
      if (has) measures.push([xa, xb]);
    }
    systems.push({ staves, measures, index: systems.length, page: pageIndex });
  }
  return { systems, warnings, comps };
}

// Build voice streams for a staff in a measure: returns {v1:[ev], v2:[ev], chordal:[ev]}
function staffMeasureEvents(fr, R, comps, s, xa, xb) {
  const chords = s.chords.filter(c => c.x > xa && c.x < xb);
  const v = { 1: [], 2: [], chordal: [] };
  const cur = { 1: 0, 2: 0 };
  for (const c of chords) {
    const hs = c.heads.slice().sort((a, b) => a.y - b.y);
    hs.forEach(h => { if (!h.dur) h.dur = headDuration(R, h, c); h.acc = headAccidental(R, comps, h, s.hdr ? s.hdr.end : -Infinity, hs.length > 1 ? 3.2 : 1.9); });
    const ev = (heads) => ({ x: c.x, heads, q: heads[0].dur.q, dots: heads[0].dur.dots });
    v.chordal.push({ ...ev(hs), q: Math.min(...hs.map(h => h.dur.q)) });
    let a1 = [], a2 = [];
    const ups = hs.filter(h => h.stemDir === 1), downs = hs.filter(h => h.stemDir === -1), both = hs.filter(h => h.stemDir === 2);
    if (both.length) { a1 = both; a2 = both; }
    if (ups.length && downs.length) { a1 = a1.concat(ups); a2 = a2.concat(downs); }
    else if (hs.length >= 2) { a1 = [hs[0]]; a2 = [hs[hs.length - 1]]; }
    else if (hs.length === 1 && !both.length) {
      // single head: unison unless one voice is still sounding
      const h = hs[0];
      if (Math.abs(cur[1] - cur[2]) < 1e-6) { a1 = [h]; a2 = [h]; }
      else if (cur[1] < cur[2]) a1 = [h]; else a2 = [h];
    }
    if (a1.length) { v[1].push(ev([a1[0]])); cur[1] += a1[0].dur.q; }
    if (a2.length) { v[2].push(ev([a2[a2.length - 1]])); cur[2] += a2[a2.length - 1].dur.q; }
  }
  return v;
}

module.exports = { assemblePage, staffMeasureEvents, pitchOf, keyAlters, DIV, median, headDuration, _analyseHeader: analyseHeader, _compIndex: compIndex, _strokes: strokes, _classifyAccidental: classifyAccidental, _crossBands: crossBands, _glyphImage: glyphImage, _splitSharps: splitSharps, _detachedNear: detachedNear, _readClef: readClef };
