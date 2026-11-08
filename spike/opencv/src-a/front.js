'use strict';
// Front end: gray page -> staves, systems, heads (+stems), beams, barlines.
// Works in the deskewed frame; everything downstream uses that frame.
const { binarize, boxBlur, despeckle, clearEdgeBands } = require('./binarize');
const { estimateSkew } = require('./skew');
const { estimateStaffSpace } = require('./staffspace');
const { detectStaves, groupSystems, mergeStaffSets, lineCoverage, bridgeRows } = require('./staves');
const { removeStaffLines } = require('./staffremoval');
const { detectHeads, chordStems, ledgerOK } = require('./heads');
const { threshold } = require('./binarize');
const { detectStems } = require('./stems');
const { detectBarlines } = require('./barlines');
const { rotateGray, makeGray } = require('./image');
const { precleanPage } = require('./cv');

function resample(g, f) {
  const w = Math.max(1, Math.round(g.width * f)), h = Math.max(1, Math.round(g.height * f));
  const out = makeGray(w, h, 255);
  for (let y = 0; y < h; y++) {
    const sy = Math.min(g.height - 1.001, (y + 0.5) / f - 0.5), y0 = Math.max(0, Math.floor(sy)), ty = Math.max(0, sy - y0);
    for (let x = 0; x < w; x++) {
      const sx = Math.min(g.width - 1.001, (x + 0.5) / f - 0.5), x0 = Math.max(0, Math.floor(sx)), tx = Math.max(0, sx - x0);
      const i = y0 * g.width + x0;
      out.data[y * w + x] = (g.data[i] * (1 - tx) + g.data[i + 1] * tx) * (1 - ty) + (g.data[i + g.width] * (1 - tx) + g.data[i + g.width + 1] * tx) * ty;
    }
  }
  return out;
}

// A hollow "head" on the stem of a filled head, towards the stem's far end,
// is the hole a flag (or a beam meeting its stem) closes: flags curl out to
// the right of the stem.  The stem is a thin ink column (on the lenient
// binary L) joining both rows.
function atStemTip(h, heads, L) {
  if (h.kind !== 'hollow') return false;
  const { width: w, height: H, data } = L;
  const sp = h.sp, maxGap = Math.max(1, Math.round(0.12 * sp));
  for (const f of heads) {
    if (f === h || f.kind !== 'filled' || f.staff !== h.staff) continue;
    const dy = Math.abs(h.y - f.y);
    if (dy < 1.2 * sp || dy > 4.5 * sp || Math.abs(h.x - f.x) > 1.6 * sp) continue;
    const ya = Math.max(0, Math.round(Math.min(f.y, h.y))), yb = Math.min(H - 1, Math.round(Math.max(f.y, h.y)));
    const ym = Math.round((ya + yb) / 2);
    for (let x = Math.max(1, Math.round(f.x - 0.9 * sp)); x <= Math.min(w - 2, Math.round(f.x + 0.9 * sp)); x++) {
      const off = (h.x - x) / sp;
      if (off < -0.3 || off > 1.2) continue;
      let gap = 0, ok = true;
      for (let y = ya; y <= yb && ok; y++) { if (data[y * w + x]) gap = 0; else if (++gap > maxGap) ok = false; }
      if (!ok) continue;
      // thin at mid-height: a stem, not the body of a glyph
      let a = x, b = x;
      while (a > 0 && data[ym * w + a - 1] && x - a < sp) a--;
      while (b < w - 1 && data[ym * w + b + 1] && b - x < sp) b++;
      if (b - a + 1 <= Math.max(3, 0.3 * sp)) return true;
    }
  }
  return false;
}

// The line that opens a system (and a bracket's spine) runs down the staff's
// left edge.  A clef printed against it fuses with it into one tall component
// that no longer reads as a clef, so it is erased from R (barlines and heads
// ignore the staff start anyway).  Only columns whose ink spans the whole
// staff height right at the left edge go; the clef's own columns do not.
function eraseStartLines(R, staves, ss) {
  const { width: w, height: h, data } = R;
  for (const st of staves) {
    const sp = st.space || ss;
    const xa = Math.max(0, Math.round(st.left - 1.0 * sp)), xb = Math.min(w - 1, Math.round(st.left + 0.5 * sp));
    const cols = [];
    for (let x = xa; x <= xb; x++) {
      const y0 = Math.round(st.yAt(0, x) - 0.2 * sp), y1 = Math.round(st.yAt(4, x) + 0.2 * sp);
      if (y0 < 0 || y1 >= h) continue;
      let n = 0;
      for (let y = y0; y <= y1; y++) n += data[y * w + x];
      if (n >= 0.97 * (y1 - y0 + 1)) cols.push(x);
    }
    if (!cols.length || cols[cols.length - 1] - cols[0] + 1 > 0.9 * sp) continue;
    // only where a glyph actually touches the line from the right
    const xr = cols[cols.length - 1] + 1;
    if (xr >= w) continue;
    let touch = 0;
    for (let y = Math.max(0, Math.round(st.yAt(0, xr) - 0.5 * sp)); y <= Math.min(h - 1, Math.round(st.yAt(4, xr) + 0.5 * sp)); y++) touch += data[y * w + xr];
    if (touch < 2) continue;
    for (const x of cols) {
      const y0 = Math.round(st.yAt(0, x) - 0.5 * sp), y1 = Math.round(st.yAt(4, x) + 0.5 * sp);
      for (let y = Math.max(0, y0); y <= Math.min(h - 1, y1); y++) data[y * w + x] = 0;
    }
  }
}

// Binarization modes, tried in order when a page yields no staves:
//   default  background-normalised Otsu (median filter on noisy pages)
//   raw      no median: a 3x3 median erases 1-px staff lines on noisy scans
//   blur1/2  box blur first: descreens halftone dots, rejoins broken lines of
//            heavy photocopies
//   bridge   thin photocopies: staff lines are rows of loose dots and thin
//            strokes break up; a lenient threshold, staves found with each
//            row's gaps bridged
const MODES = [
  { name: 'default' },
  { name: 'raw', denoise: false, despeckle: true },
  { name: 'blur1', denoise: false, blur: 1 },
  { name: 'blur2', denoise: false, blur: 2 },
  { name: 'bridge', denoise: false, bridge: true },
];

// bridge mode reads a lenient threshold (thin strokes keep their ink, broken
// hollow-head outlines close); staves are found on it with each row's gaps
// bridged, the gap limit following the page width (about a staff space)
const BRIDGE_T = 230;
const staffBinary = (bz, mode) => mode.bridge ? bridgeRows(threshold(bz.gray, BRIDGE_T), Math.max(6, Math.round(bz.gray.width / 110))) : bz.binary;

// Exact quarter / half turns of a gray page (clockwise).
function turn(g, quarter) {
  const q = ((quarter % 4) + 4) % 4;
  if (!q) return g;
  const { width: w, height: h, data } = g;
  const W = q === 2 ? w : h, Hh = q === 2 ? h : w;
  const out = makeGray(W, Hh, 255);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = data[y * w + x];
    if (q === 1) out.data[x * W + (h - 1 - y)] = v;
    else if (q === 2) out.data[(h - 1 - y) * W + (w - 1 - x)] = v;
    else out.data[(w - 1 - x) * W + y] = v;
  }
  return out;
}

// Gray page -> binary, staff space and deskew for one mode.
function clean(gray, mode) {
  const bin = (g) => binarize(mode.blur ? boxBlur(g, mode.blur) : g, mode.denoise === false ? { denoise: false } : {});
  let bz = bin(gray);
  let sp = estimateStaffSpace(staffBinary(bz, mode));
  let scale = 1;
  // normalise staff space to ~18 px (speed for big scans, detail for small
  // ones), when the estimate is trustworthy (a blank, text-only or sideways
  // page has no clear line spacing)
  if ((sp.ss > 26 || (sp.ss < 13 && sp.ss >= 5)) && sp.confidence >= 0.2) {
    scale = 18 / sp.ss;
    gray = resample(gray, scale);
    bz = bin(gray);
  }
  const skew = estimateSkew(bz.binary);
  if (Math.abs(skew.angle) >= 0.05) {
    gray = rotateGray(gray, (-skew.angle * Math.PI) / 180);
    bz = bin(gray);
  }
  const eb = clearEdgeBands(mode.bridge ? threshold(bz.gray, BRIDGE_T) : bz.binary);
  let B = eb.binary;
  const SB = mode.bridge ? staffBinary(bz, mode) : null;
  sp = estimateStaffSpace(SB || B);
  if (mode.despeckle && bz.info.noise > 12) { B = despeckle(B, Math.max(2, Math.round(0.02 * sp.ss * sp.ss))); sp = estimateStaffSpace(B); }
  return { gray, bz, B, SB, sp, scale, skew, mode: mode.name, bands: eb.bands };
}

// Staves on the main binary and on a lenient one (faint / thin-ruled scans
// lose staff lines in B); the better-supported staff is kept where they clash.
function findStaves(c) {
  const { bz, B, SB } = c;
  let { sp } = c;
  const L0 = clearEdgeBands(threshold(bz.gray, Math.min(235, (bz.info.threshold || 180) + 35)), c.bands && c.bands.length ? { bands: c.bands } : {}).binary;
  if (SB) {
    c.staves = mergeStaffSets([detectStaves(SB, sp.ss, sp.lt)], SB, sp.lt, sp.ss);
    return Object.assign(c, { L0, ltL: sp.lt });
  }
  const spL = estimateStaffSpace(L0);
  const sB = detectStaves(B, sp.ss, sp.lt), sL = detectStaves(L0, spL.ss, spL.lt);
  const staves = mergeStaffSets([sB, sL], L0, Math.max(sp.lt, spL.lt), sp.ss);
  let ltL = sp.lt;
  if (staves.filter(st => sL.includes(st)).length > staves.length / 2 && sB.length < staves.length) {
    sp = { ...sp, ss: spL.ss }; ltL = Math.max(sp.lt, spL.lt);
  }
  return Object.assign(c, { L0, sp, ltL, staves });
}

const prepare = (gray, mode) => findStaves(clean(gray, mode));

function transpose(b) {
  const { width: w, height: h, data } = b;
  const o = { width: h, height: w, data: new Uint8Array(w * h) };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) o.data[x * h + y] = data[y * w + x];
  return o;
}

// Staves found by a fallback binarization must look like staves.  Blurred
// text rows make regularly spaced bands too, but they are thick for their
// spacing AND broken at every word gap; real staff lines are thin or run on.
function plausible(c) {
  if (c.sp.lt <= 0.35 * c.sp.ss) return c.staves.length > 0;
  c.staves = c.staves.filter(st => { const cv = lineCoverage(st, c.B, c.sp.lt); return cv.reduce((a, b) => a + b, 0) / 5 >= 0.8; });
  c.staves.forEach((st, i) => { st.index = i; });
  return c.staves.length > 0;
}

// Upside-down pages: a staff opens with clef / key / time signature (dense
// ink in its first spaces) and closes with a thin barline.  Returns the share
// of staves whose far end is clearly denser than their start.
function invertedShare(R, staves) {
  const { width: w, height: h, data } = R;
  let n = 0, inv = 0;
  for (const st of staves) {
    const sp = st.space;
    if (st.right - st.left < 16 * sp) continue;
    const dens = (xa, xb) => {
      let ink = 0, tot = 0;
      for (let x = Math.max(0, Math.round(xa)); x <= Math.min(w - 1, Math.round(xb)); x++) {
        const y0 = Math.max(0, Math.round(st.yAt(0, x) - 0.5 * sp)), y1 = Math.min(h - 1, Math.round(st.yAt(4, x) + 0.5 * sp));
        for (let y = y0; y <= y1; y++) { ink += data[y * w + x]; tot++; }
      }
      return tot ? ink / tot : 0;
    };
    const a = dens(st.left + 0.6 * sp, st.left + 4.6 * sp), b = dens(st.right - 4.6 * sp, st.right - 0.6 * sp);
    n++;
    if (b > 1.6 * a + 0.02) inv++;
  }
  return n ? inv / n : 0;
}

// Staged front end.  Yields the stage about to run ('cleanup', 'staves',
// 'notes') so a caller can report progress and let the page repaint between
// stages; returns the result.  front() below runs it in one go, reporting
// each stage to opts.onStage(stage) and opts.onProgress(message, { stage }).
function* frontSteps(gray0, opts = {}) {
  const warnings = [];
  // degraded scans are repaired first (src/cv.js, OpenCV); a page that looks clean comes back
  // unchanged (the same object), so clean pages are read exactly as before
  gray0 = precleanPage(gray0, opts);
  const precleaned = !!gray0.preclean;
  yield 'cleanup';
  let ctx = clean(gray0, (opts.mode && MODES.find(m => m.name === opts.mode)) || MODES[0]);
  yield 'staves';
  findStaves(ctx);
  let quarter = 0;
  if (!ctx.staves.length && !opts.mode) {
    // fail over: other binarizations, then the page turned a quarter.  Only
    // pages with straight-line structure are worth it (projection sharpness
    // along rows, or along columns for a page lying on its side); a blank or
    // text-only page stops here.
    const rowConf = estimateSkew(ctx.B).confidence, colConf = estimateSkew(transpose(ctx.B)).confidence;
    const tries = [];
    if (rowConf >= 1.5) for (const m of MODES.slice(1)) tries.push([0, m]);
    if (colConf >= 1.5) for (const q of [1, 3]) for (const m of [MODES[0], MODES[2]]) tries.push([q, m]);
    for (let i = 0; i < tries.length; i++) {
      const [q, m] = tries[i];
      // bridging is the last resort: it also joins a halftone screen's dots
      // into tight phantom "staves" (a 3-5 px spacing nothing can be read at)
      if (!(m.bridge && ctx.staves.length)) {
        const c = prepare(turn(gray0, q), m);
        if (!(m.bridge && c.sp.ss < 6) && plausible(c) && c.staves.length > ctx.staves.length) { ctx = c; quarter = q; }
      }
      // upright readings first; a turned page only when none of them works
      if (ctx.staves.length && (q !== 0 || !tries[i + 1] || tries[i + 1][0] !== 0)) break;
    }
  }
  let { gray, B, L0, sp, ltL, scale, skew, staves } = ctx;
  if (!staves.length) {
    warnings.push('No staves found on this page.');
    // orientation left unset: nothing settled it, a caller may still try turns
    return { gray, B, R: B, scale, skew, ss: sp.ss, lt: sp.lt, staves: [], systems: [], heads: [], beams: [], barlines: [], warnings, mode: ctx.mode, precleaned };
  }
  let R = removeStaffLines(B, staves, sp.lt).binary;
  if (opts.orient !== false && invertedShare(R, staves) >= 0.6) {
    const c = prepare(turn(gray0, quarter + 2), MODES.find(m => m.name === ctx.mode));
    if (c.staves.length >= staves.length) {
      const R2 = removeStaffLines(c.B, c.staves, c.sp.lt).binary;
      if (invertedShare(R2, c.staves) < 0.4) {
        ctx = c; quarter += 2; R = R2;
        ({ gray, B, L0, sp, ltL, scale, skew, staves } = ctx);
      }
    }
  }
  if (quarter % 4) warnings.push(`Page was turned ${((quarter % 4) * 90)}\u00b0 to read it.`);
  const systems = groupSystems(B, staves, sp.ss, L0);
  eraseStartLines(R, staves, sp.ss);
  yield 'notes';
  // thin, faint prints: hollow-head outlines break open in B but stay closed
  // on the lenient binary (heavy prints close unrelated gaps there instead)
  const { heads, beams } = detectHeads(B, R, staves, sp.ss, sp.lt, sp.lt < 0.16 * sp.ss ? { lenient: L0 } : {});
  const { binary: L } = removeStaffLines(L0, staves, ltL);
  // ledger evidence on the lenient binary, or on the main one: lenient
  // thresholds thicken a ledger fused with its head past the thin-stroke limit
  const ledgered = (h) => ledgerOK(L, staves, h, ltL) || ledgerOK(R, staves, h, sp.lt);
  // a head between two staves goes to the staff its ledger lines lead to,
  // which is not always the nearer one (high notes over a wide gap)
  const other = (h) => {
    const st0 = staves[h.staff], k = h.y < st0.yAt(2, h.x) ? h.staff - 1 : h.staff + 1, st = staves[k];
    if (!st || h.x < st.left - st.space || h.x > st.right + st.space) return null;
    const s2 = st.spaceAt(h.x), ym = st.yAt(2, h.x), p = Math.round((ym - h.y) / (s2 / 2));
    if (Math.abs(p) < 6 || Math.abs(p) > 16) return null;
    const c = { ...h, staff: k, p, y: ym - (p * s2) / 2, sp: s2 };
    return ledgered(c) ? c : null;
  };
  let hs = [];
  for (const h of heads) {
    if (h.x <= staves[h.staff].left + 3.0 * sp.ss) continue;
    if (ledgered(h)) { hs.push(h); continue; }
    const c = other(h);
    if (c && !heads.some(o => o.staff === c.staff && o.p === c.p && Math.abs(o.x - c.x) < 0.6 * c.sp)) hs.push(c);
  }
  const chords = chordStems(L, hs, { minLen: 1.5, sides: true });
  hs = hs.filter(h => (h.stemDir !== 0 || h.kind === 'hollow') && !(h.chord && h.chord.accidental));
  hs = hs.filter(h => !atStemTip(h, hs, L));
  const barlines = detectBarlines(R, staves, hs, sp.ss);
  return { gray, B, R, L, scale, skew, ss: sp.ss, lt: sp.lt, staves, systems, heads: hs, chords, beams, barlines, warnings,
    orientation: (quarter % 4) * 90, mode: ctx.mode };
}

const STAGE_TEXT = { cleanup: 'cleaning up the scan', staves: 'finding staves', notes: 'finding notes' };

function front(gray, opts = {}) {
  const it = frontSteps(gray, opts);
  let r = it.next();
  while (!r.done) {
    if (opts.onStage) opts.onStage(r.value);
    if (opts.onProgress) opts.onProgress(STAGE_TEXT[r.value] || r.value, { stage: r.value });
    r = it.next();
  }
  // a repair that left no staves to find (noise amplified into texture): read the page as it was
  if (r.value.precleaned && !r.value.staves.length) return front(gray, Object.assign({}, opts, { preclean: false }));
  return r.value;
}

module.exports = { front, frontSteps, resample, turn, prepare };
