'use strict';
// Front end: gray page -> staves, systems, heads (+stems), beams, barlines.
// Works in the deskewed frame; everything downstream uses that frame.
const { binarize } = require('./binarize');
const { estimateSkew } = require('./skew');
const { estimateStaffSpace } = require('./staffspace');
const { detectStaves, groupSystems, mergeStaffSets } = require('./staves');
const { removeStaffLines } = require('./staffremoval');
const { detectHeads, chordStems, ledgerOK } = require('./heads');
const { threshold } = require('./binarize');
const { detectStems } = require('./stems');
const { detectBarlines } = require('./barlines');
const { rotateGray, makeGray } = require('./image');

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

function front(gray, opts = {}) {
  const warnings = [];
  let bz = binarize(gray);
  let sp = estimateStaffSpace(bz.binary);
  let scale = 1;
  // normalise staff space to ~18 px (speed for big scans, detail for small ones)
  if (sp.ss > 26 || (sp.ss < 13 && sp.ss >= 5)) {
    scale = 18 / sp.ss;
    gray = resample(gray, scale);
    bz = binarize(gray);
  }
  const skew = estimateSkew(bz.binary);
  if (Math.abs(skew.angle) >= 0.05) {
    gray = rotateGray(gray, (-skew.angle * Math.PI) / 180);
    bz = binarize(gray);
  }
  const B = bz.binary;
  sp = estimateStaffSpace(B);
  // staves on the main binary and on a lenient one (faint / thin-ruled scans
  // lose staff lines in B); keep the better-supported staff where they clash
  const L0 = threshold(bz.gray, Math.min(235, (bz.info.threshold || 180) + 35));
  const spL = estimateStaffSpace(L0);
  const sB = detectStaves(B, sp.ss, sp.lt), sL = detectStaves(L0, spL.ss, spL.lt);
  let staves = mergeStaffSets([sB, sL], L0, Math.max(sp.lt, spL.lt), sp.ss);
  let ltL = sp.lt;
  if (staves.filter(st => sL.includes(st)).length > staves.length / 2 && sB.length < staves.length) {
    sp = { ...sp, ss: spL.ss }; ltL = Math.max(sp.lt, spL.lt);
  }
  if (!staves.length) {
    warnings.push('No staves found on this page.');
    return { gray, B, R: B, scale, skew, ss: sp.ss, lt: sp.lt, staves: [], systems: [], heads: [], beams: [], barlines: [], warnings };
  }
  const systems = groupSystems(B, staves, sp.ss, L0);
  const { binary: R } = removeStaffLines(B, staves, sp.lt);
  const { heads, beams } = detectHeads(B, R, staves, sp.ss, sp.lt);
  const { binary: L } = removeStaffLines(L0, staves, ltL);
  let hs = heads.filter(h => h.x > staves[h.staff].left + 3.0 * sp.ss && ledgerOK(L, staves, h, ltL));
  const chords = chordStems(L, hs, { minLen: 1.5 });
  hs = hs.filter(h => h.stemDir !== 0 || h.kind === 'hollow');
  const barlines = detectBarlines(R, staves, hs, sp.ss);
  return { gray, B, R, L, scale, skew, ss: sp.ss, lt: sp.lt, staves, systems, heads: hs, chords, beams, barlines, warnings };
}

module.exports = { front, resample };
