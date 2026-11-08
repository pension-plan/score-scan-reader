'use strict';
// Classical OMR front-end: gray page -> staves, noteheads (+kind, staff
// position, stem direction), barlines, systems.  Environment agnostic.
const { binarize, despeckle, removeIsolated } = require('./binarize');
const { estimateSkew } = require('./skew');
const { estimateStaffSpaceRobust: estimateStaffSpace } = require('./staffspace');
const { detectStaves, groupSystems } = require('./staves');
const { removeStaffLines } = require('./staffremoval');
const { detectNoteheads } = require('./noteheads');
const { detectStems, applyStemRule } = require('./stems');
const { detectBarlines } = require('./barlines');
const { rotateGray, rotatePoint } = require('./image');
const { labelComponents } = require('./cc');

const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());

function runOMR(gray, opts = {}) {
  const T = {};
  let t = now();
  const lap = (k) => { const n = now(); T[k] = +(n - t).toFixed(1); t = n; };

  let bz = binarize(gray, opts.binarize);
  lap('binarize');
  const skew = opts.deskew === false ? { angle: 0, confidence: 0 } : estimateSkew(bz.binary);
  lap('skew');
  let work = gray;
  const rotRad = (skew.angle * Math.PI) / 180;
  if (Math.abs(skew.angle) >= (opts.minDeskew ?? 0.05)) {
    work = rotateGray(gray, -rotRad); // undo the rotation
    bz = binarize(work, opts.binarize);
    lap('deskew');
  }
  const B = bz.binary;
  // despeckle: isolated dots first (scale unknown), then relative to staff space
  const iso = removeIsolated(B);
  bz.info.despeckled = iso;
  let sp = estimateStaffSpace(B);
  // full despeckle only when the page is noisy (many isolated pixels)
  if (opts.despeckle !== false && (opts.despeckle === true || iso > 2e-4 * B.data.length)) {
    const a = Math.max(2, Math.round((opts.despeckleFactor ?? 0.025) * sp.ss * sp.ss));
    bz.info.despeckled += despeckle(B, a);
    sp = estimateStaffSpace(B);
  }
  lap('staffspace');
  const staves = detectStaves(B, sp.ss, sp.lt, opts.staves);
  const systems = groupSystems(B, staves, sp.ss);
  lap('staves');
  const { binary: R } = removeStaffLines(B, staves, sp.lt, opts.removal);
  lap('removal');
  const cc = labelComponents(R);
  lap('cc');
  let heads = detectNoteheads(B, R, staves, sp.ss, opts.heads, cc);
  lap('heads');
  detectStems(R, heads, opts.stems);
  // fallback for heads without a stem: search again on a lenient binary
  // (faint hairline stems of old prints are lost by the main threshold)
  const noStem = heads.filter(h => h.stem.dir === 0);
  if (bz.lenient && noStem.length && opts.lenientStems !== false) {
    removeIsolated(bz.lenient);
    const RS = removeStaffLines(bz.lenient, staves, sp.lt, opts.removal).binary;
    detectStems(RS, noStem, opts.stems);
  }
  if (opts.stemRule !== false) heads = applyStemRule(heads, { staves, ss: sp.ss, ...(opts.stemRule || {}) });
  lap('stems');
  const barlines = detectBarlines(R, staves, heads, sp.ss, opts.barlines);
  lap('barlines');

  // map results back to input-image coordinates
  const W = gray.width, H = gray.height;
  const back = (x, y) => (rotRad ? rotatePoint(x, y, W, H, rotRad) : [x, y]);
  const out = {
    width: W, height: H,
    binarize: bz.info,
    skew: { angle: skew.angle, confidence: +skew.confidence.toFixed(2) },
    staffSpace: +sp.ss.toFixed(3), lineThickness: +sp.lt.toFixed(3), staffSpaceConfidence: +sp.confidence.toFixed(3), staffSpaceSource: sp.source, ssRunLength: +sp.ssRunLength.toFixed(2), ssAC: +sp.ssAC.toFixed(2),
    staves: staves.map(st => ({
      index: st.index, system: st.system, left: st.left, right: st.right, space: +st.space.toFixed(3),
      lines: [0, 1, 2, 3, 4].map(k => {
        const pts = [];
        const step = Math.max(8, Math.round((st.right - st.left) / 40));
        for (let x = st.left; x <= st.right; x += step) pts.push(back(x, st.yAt(k, x)).map(v => +v.toFixed(2)));
        return pts;
      }),
    })),
    systems,
    heads: heads.map(hd => {
      const [x, y] = back(hd.x, hd.y);
      return { x: +x.toFixed(1), y: +y.toFixed(1), kind: hd.kind, staff: hd.staff, p: hd.p, score: +hd.score.toFixed(3),
        stem: hd.stem ? hd.stem.dir : 0, stemLen: hd.stem ? Math.max(hd.stem.up, hd.stem.down) : 0 };
    }),
    barlines: barlines.map(b => {
      const [x, y0] = back(b.x, b.top); const [, y1] = back(b.x, b.bot);
      return { staff: b.staff, x: +x.toFixed(1), y0: +y0.toFixed(1), y1: +y1.toFixed(1), double: !!b.double, spansSystem: b.spansSystem };
    }),
    timings: T,
  };
  if (opts.debug) out._debug = { B, R, work, staves, headsRaw: heads, barlinesRaw: barlines, rotRad };
  return out;
}

module.exports = { runOMR };
