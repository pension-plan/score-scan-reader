'use strict';
// Form on the page (L22): barline kinds, repeats and volta brackets.
//
// readStructure(fr, asm) runs once per page at the start of buildScore (score.js), after
// meter.js, and gives each system
//   sy.bars:   [{x, x0, x1, kind}] for every barline of the system, the one closing it included,
//              kind single | double | final | heavy-light | repeat-start | repeat-end | repeat-both
//              (from the stroke widths through the staves and the repeat dots beside them);
//   sy.voltas: [{x0, x1, open, cont}] volta brackets over the top staff (a long thin line two to
//              five spaces above it with a hook down at its start; open: no hook down at its end,
//              cont: carried over from the system before, so no hook at its start either);
//   sy.signs:  [{x, kind}] segno and coda signs over the top staff: a coda is an oval crossed by a
//              cross (four enclosed holes); a segno a tall slashed S standing alone (no holes, its
//              middle column crossing ink three times or more; its two dots are too small to rely on).
// buildScore writes them as <barline> (bar-style, <repeat>, <ending>), which playback.js follows.

const { holes } = require('./ottava');
const { matcher, crop, heal } = require('./meter');

const lineY = (st, k, x) => st.yAt(0, x) + k * (st.yAt(4, x) - st.yAt(0, x)) / 4;

// ink columns through the staff in [xa, xb]: runs of columns covered over most of the height
function strokes(R, st, xa, xb) {
  const W = R.width, out = [];
  let run = null;
  for (let x = Math.max(0, Math.floor(xa)); x <= Math.min(W - 1, Math.ceil(xb)); x++) {
    const y0 = Math.round(lineY(st, 0, x)), y1 = Math.round(lineY(st, 4, x));
    let n = 0;
    for (let y = y0; y <= y1; y++) n += R.data[y * W + x] ? 1 : 0;
    const on = n >= 0.8 * (y1 - y0 + 1);
    if (on && run) run.x1 = x;
    else if (on) { run = { x0: x, x1: x }; out.push(run); }
    else run = null;
  }
  return out.map(r => ({ ...r, w: r.x1 - r.x0 + 1 }));
}

// repeat dots on one side of a barline: two dots in the second and third spaces
function repeatDots(comps, st, x0, x1, sp, side) {
  const xm = side < 0 ? x0 : x1;
  const isDot = (c, k) => {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
    return w >= 0.2 * sp && w <= 0.75 * sp && h >= 0.2 * sp && h <= 0.75 * sp && c.area >= 0.4 * w * h &&
      Math.abs((c.y0 + c.y1) / 2 - lineY(st, k, xm)) <= 0.3 * sp;
  };
  const inWin = (c) => (side < 0 ? c.x1 < x0 && c.x1 >= x0 - 1.2 * sp : c.x0 > x1 && c.x0 <= x1 + 1.2 * sp);
  const near = comps.filter(inWin);
  const a = near.find(c => isDot(c, 1.5)), z = near.find(c => isDot(c, 2.5));
  return !!(a && z && Math.abs((a.x0 + a.x1) - (z.x0 + z.x1)) / 2 <= 0.4 * sp);
}

// the kind of the barline standing in [x0, x1] on staff st
function barKind(R, comps, st, x0, x1, sp) {
  const ss = strokes(R, st, x0 - 0.3 * sp, x1 + 0.3 * sp);
  let kind = 'single';
  if (ss.length >= 2) {
    const a = ss[0], b = ss[ss.length - 1];
    if (b.w >= 1.7 * a.w && b.w >= 0.3 * sp) kind = 'final';
    else if (a.w >= 1.7 * b.w && a.w >= 0.3 * sp) kind = 'heavy-light';
    else kind = 'double';
  }
  const lx = ss.length ? ss[0].x0 : x0, rx = ss.length ? ss[ss.length - 1].x1 : x1;
  const L = repeatDots(comps, st, lx, rx, sp, -1), Rr = repeatDots(comps, st, lx, rx, sp, 1);
  if (L && Rr) kind = 'repeat-both';
  else if (L) kind = 'repeat-end';
  else if (Rr) kind = 'repeat-start';
  return { kind, x0: lx, x1: rx };
}

function readBars(fr, asm, sy) {
  const sis = new Set(sy.staves.map(s => s.si));
  const bs = fr.barlines.filter(b => sis.has(b.staff)).sort((a, b) => a.x - b.x);
  const cl = [];
  for (const b of bs) {
    const last = cl[cl.length - 1];
    if (last && b.x - last[last.length - 1].x < 1.2 * fr.ss) last.push(b); else cl.push([b]);
  }
  const out = [];
  for (const c of cl) {
    const x0 = Math.min(...c.map(b => (b.x0 != null ? b.x0 : b.x))), x1 = Math.max(...c.map(b => (b.x1 != null ? b.x1 : b.x)));
    // each staff's reading; the kind most staves show (a repeat sign on any of them counts)
    const ks = sy.staves.map(s => barKind(fr.R, asm.comps, s.st, x0, x1, s.st.space || fr.ss));
    const cnt = {};
    for (const k of ks) cnt[k.kind] = (cnt[k.kind] || 0) + 1;
    let kind = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0][0];
    const rep = ks.filter(k => /^repeat/.test(k.kind));
    if (rep.length >= Math.max(1, 0.5 * ks.length)) {
      const rc = {};
      for (const k of rep) rc[k.kind] = (rc[k.kind] || 0) + 1;
      kind = Object.entries(rc).sort((a, b) => b[1] - a[1])[0][0];
    }
    out.push({ x: (x0 + x1) / 2, x0, x1, kind });
  }
  return out;
}

// the numbers printed under a volta bracket's start ("1.", "2.", "1.-3.", "1, 2."): digits read
// against the digit templates scaled to their own height (half the template's two spaces); a dash
// between two digits is a range. null when nothing reads
const DIGITS = ['digit-0', 'digit-1', 'digit-2', 'digit-3', 'digit-4', 'digit-5', 'digit-6', 'digit-7', 'digit-8', 'digit-9'];
function voltaNumbers(fr, comps, line, sp) {
  const R = fr.R, api = matcher();
  const near = comps.filter(o => o.x0 >= line.x0 + 0.2 * sp && o.x0 <= line.x0 + 5 * sp && o.y0 >= line.y0 + 0.15 * sp && o.y1 <= line.y0 + 2.6 * sp && o !== line)
    .sort((a, b) => a.x0 - b.x0);
  const digits = [], marks = [];
  for (const o of near) {
    const w = o.x1 - o.x0 + 1, h = o.y1 - o.y0 + 1;
    if (h >= 0.6 * sp && h <= 1.9 * sp && w <= 1.4 * sp) {
      const g = crop(R, { x0: o.x0, y0: o.y0, x1: o.x1, y1: o.y1, inner: (a, b, c2, d) => a >= o.x0 && c2 <= o.x1 && b >= o.y0 && d <= o.y1 }, 2);
      if (!g) continue;
      const sc = api.scores(heal(g.img, 1), h / 2, DIGITS);
      const d = DIGITS.reduce((p, n) => (sc[n] > sc[p] ? n : p), DIGITS[1]);
      if (sc[d] >= 0.45 && d !== 'digit-0') digits.push({ x: o.x0, v: DIGITS.indexOf(d) });
    } else if (w >= 0.3 * sp && w <= 1.2 * sp && h <= 0.3 * sp) marks.push({ x: o.x0, dash: true });
    if (digits.length && o.x0 - digits[digits.length - 1].x > 3 * sp) break;
  }
  if (!digits.length || digits.length > 4) return null;
  const nums = [digits[0].v];
  for (let i = 1; i < digits.length; i++) {
    const range = marks.some(m => m.x > digits[i - 1].x && m.x < digits[i].x);
    if (range && digits[i].v > nums[nums.length - 1]) for (let k = nums[nums.length - 1] + 1; k <= digits[i].v; k++) nums.push(k);
    else if (digits[i].v > nums[nums.length - 1]) nums.push(digits[i].v);
  }
  return nums;
}

// volta brackets over the top staff
function readVoltas(fr, asm, sy) {
  const s = sy.staves[0];
  if (!s) return [];
  const st = s.st, sp = st.space || fr.ss, comps = asm.comps;
  const out = [];
  for (const c of comps) {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
    if (w < 3 * sp) continue;
    const top = lineY(st, 0, c.x0);
    if (c.y0 < top - 6 * sp || c.y0 > top - 1.2 * sp) continue;
    // the line: a thin row of ink along the top of the box
    const W = fr.R.width, R = fr.R.data;
    const yl = c.y0;
    let row = 0;
    for (let x = c.x0; x <= c.x1; x++) {
      let on = false;
      for (let y = yl; y <= yl + Math.max(2, Math.round(0.25 * sp)); y++) if (R[y * W + x]) { on = true; break; }
      if (on) row++;
    }
    if (row < 0.9 * w) continue;
    // a slur or a beam is not flat: the line's thickness stays small
    let thick = 0;
    const xm = Math.round((c.x0 + c.x1) / 2);
    for (let y = c.y0; y <= c.y1 && R[y * W + xm]; y++) thick++;
    if (thick > 0.35 * sp) continue;
    // hooks down at the ends: a vertical run from the line at the end column
    const hook = (x) => {
      let n = 0;
      for (let dx = -1; dx <= 1; dx++) {
        let k = 0;
        for (let y = c.y0; y <= c.y1 && y < c.y0 + 3 * sp; y++) if (R[y * W + x + dx]) k = y - c.y0; else if (y - c.y0 > k + 2) break;
        n = Math.max(n, k);
      }
      return n >= 1.0 * sp;
    };
    const hl = hook(c.x0 + 1), hr = hook(c.x1 - 1);
    if (h > 3 * sp) continue;
    // not a hairpin or text: nothing tall below the line inside the bracket but the hooks
    out.push({ x0: c.x0, x1: c.x1, y: c.y0, open: !hr, cont: !hl, nums: hl ? voltaNumbers(fr, comps, c, sp) : null });
  }
  // a bracket carried over from the system before has no hook at its start: keep it only when it
  // starts at the staff start
  return out.filter(v => !v.cont || v.x0 < st.left + 12 * sp).sort((a, b) => a.x0 - b.x0);
}

function crossings(R, c, x) {
  let n = 0, on = false;
  for (let y = c.y0; y <= c.y1; y++) { const v = !!R.data[y * R.width + x]; if (v && !on) n++; on = v; }
  return n;
}

function readSigns(fr, asm, sy) {
  const s = sy.staves[0];
  if (!s) return [];
  const st = s.st, sp = st.space || fr.ss, R = fr.R, out = [];
  for (const c of asm.comps) {
    const top = lineY(st, 0, c.x0), w = (c.x1 - c.x0 + 1) / sp, h = (c.y1 - c.y0 + 1) / sp;
    if (c.y1 > top - 0.2 * sp || c.y0 < top - 7 * sp || h < 1.5 || h > 3.2 || w < 0.9 || w > 2.6) continue;
    const fill = c.area / ((c.x1 - c.x0 + 1) * (c.y1 - c.y0 + 1));
    const nh = holes(R, c);
    if (nh >= 4 && fill >= 0.2 && fill <= 0.6) { out.push({ x: (c.x0 + c.x1) / 2, kind: 'coda' }); continue; }
    if (nh === 0 && h >= 1.8 && h <= 2.8 && w >= 1.1 && w <= 1.9 && fill >= 0.25 && fill <= 0.6) {
      const xm = Math.round((c.x0 + c.x1) / 2);
      if (Math.max(crossings(R, c, xm), crossings(R, c, xm - 1), crossings(R, c, xm + 1)) < 3) continue;
      // standing alone: not a letter of a word ("D.S."): no letter within a space and a half,
      // no full stop at its foot
      const word = asm.comps.some(o => o !== c && o.y0 < c.y1 && o.y1 > c.y0 && o.x0 < c.x1 + 1.5 * sp && o.x1 > c.x0 - 1.5 * sp &&
        (o.y1 - o.y0 >= 0.5 * sp || (o.x0 > c.x1 - 0.2 * sp && o.y1 > c.y1 - 0.5 * sp && o.area >= 0.06 * sp * sp)));
      if (!word) out.push({ x: (c.x0 + c.x1) / 2, kind: 'segno' });
    }
  }
  return out.sort((a, b) => a.x - b.x);
}

function readStructure(fr, asm, stats = {}) {
  if (!fr || !fr.R || !asm) return stats;
  for (const sy of asm.systems) {
    try { sy.bars = readBars(fr, asm, sy); } catch (e) { sy.bars = []; stats.errors = (stats.errors || 0) + 1; }
    try { sy.voltas = readVoltas(fr, asm, sy); } catch (e) { sy.voltas = []; stats.errors = (stats.errors || 0) + 1; }
    try { sy.signs = readSigns(fr, asm, sy); } catch (e) { sy.signs = []; stats.errors = (stats.errors || 0) + 1; }
  }
  return stats;
}

module.exports = { readStructure, _barKind: barKind, _strokes: strokes };
