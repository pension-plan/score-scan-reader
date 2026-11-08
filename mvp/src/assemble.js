'use strict';
// Notation assembly: per system and staff -> clef, key, measures, durations,
// voices; then the part layout (closed-score split vs grand staff) for the page.
const { labelComponents } = require('./cc');

const DIV = 8; // divisions per quarter
const SHARP_ORDER = ['F', 'C', 'G', 'D', 'A', 'E', 'B'];
const FLAT_ORDER = ['B', 'E', 'A', 'D', 'G', 'C', 'F'];

// ---------------------------------------------------------------- symbols ---
function compIndex(R) {
  const { comps } = labelComponents(R);
  return comps.filter(c => c.area >= 4);
}

function strokes(R, c, minRun) {
  // columns with a vertical run >= 0.55 * height (or minRun) -> clustered into strokes
  const { width: w, data } = R;
  const hgt = c.y1 - c.y0 + 1;
  const need = minRun || 0.55 * hgt;
  const cols = [];
  for (let x = c.x0; x <= c.x1; x++) {
    let best = 0, run = 0, top = -1, bestTop = -1, bestBot = -1;
    for (let y = c.y0; y <= c.y1; y++) {
      if (data[y * w + x]) { if (!run) top = y; run++; if (run > best) { best = run; bestTop = top; bestBot = y; } }
      else run = 0;
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
    if (n >= 0.08 * sp * sp && top > 0.4 * hgt && sy / n > 0.6 * hgt) return 'flat';
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
  const st = strokes(img, all, 2.0 * sp);
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

// staff steps above the middle line where key-signature accidentals sit
const KEY_POS = { G: { sharp: [4, 1, 5, 2, -1, 3, 0], flat: [0, 3, -1, 2, -2, 1, -3] } };
KEY_POS.F = { sharp: KEY_POS.G.sharp.map(p => p - 2), flat: KEY_POS.G.flat.map(p => p - 2) };

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
function analyseHeader(R, comps, st, limitX, trace) {
  const sp = st.spaceAt(st.left), left = st.left;
  const lineY = (k) => st.yAt(k, left + 4 * sp);
  const yTop = lineY(0) - 3 * sp, yBot = lineY(4) + 3 * sp;
  const near = comps.filter(c => c.x1 >= left - 0.5 * sp && c.x0 < limitX && c.y1 > yTop && c.y0 < yBot);
  let clef = null, clefOct = 0, clefEnd = left;
  const tall = near.filter(c => c.x0 < left + 2.5 * sp && c.x0 >= left - 0.5 * sp && (c.y1 - c.y0) > 2.4 * sp && (c.x1 - c.x0) > 0.6 * sp && (c.y1 - c.y0) < 9 * sp);
  if (tall.length) {
    const c0 = tall.reduce((a, b) => ((b.y1 - b.y0) > (a.y1 - a.y0) ? b : a));
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
    // to about the fourth line (its dots follow)
    if (hgt > 5.2 && hgt < 9.5 && top < -0.6 && bot > 0.4) clef = 'G';
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
  }
  // glyphs after the clef, ignoring text well above / below the staff
  const cand = near.filter(c => c.x0 > clefEnd + 0.05 * sp && c.area >= 0.04 * sp * sp &&
    (c.y0 + c.y1) / 2 > lineY(0) - 1.6 * sp && (c.y0 + c.y1) / 2 < lineY(4) + 1.6 * sp).sort((a, b) => a.x0 - b.x0);
  const glyphs = groupGlyphs(cand, sp);
  // expected accidental positions; both clefs stay possible when unread
  let kcs = clef ? [KEY_POS[clef === 'F' ? 'F' : 'G']] : [KEY_POS.G, KEY_POS.F];
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
  // diatonic index of the middle line: D3 (bass), B3 (treble 8vb), B4 (treble)
  const base = clef === 'F' ? 22 : clef === 'G8' ? 27 : 34;
  const d = base + p;
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
  const comps = compIndex(R);
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
      return { st, si, chords: music, hdr };
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

module.exports = { assemblePage, staffMeasureEvents, pitchOf, keyAlters, DIV, median, headDuration, _analyseHeader: analyseHeader, _compIndex: compIndex, _strokes: strokes, _classifyAccidental: classifyAccidental, _crossBands: crossBands, _glyphImage: glyphImage, _splitSharps: splitSharps };
