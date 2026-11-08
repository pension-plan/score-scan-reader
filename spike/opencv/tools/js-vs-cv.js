// pre-clean ops: plain JS vs OpenCV on sample degraded pages: time and pixel difference
const path = require('path');
process.env.OPENCV_JS = '/Users/d.sloane/music/mvp/dist/assets/opencv-4.10.0-noeval.js';
const cvm = require('../src-js/cv.js'), { readGray } = require('../src-js/image.js');
const C = '/Users/d.sloane/music/mvp/work/cache/challenge__degradation__';
let t = performance.now(); const cv = cvm.loadCvSync(); console.log('opencv load ms', Math.round(performance.now() - t));
for (const n of ['andantino-piano-photocopy-thick__scan', 'agrace-satb-photocopy-thin__scan-severe', 'andantino-piano-blur__scan-severe', 'andantino-piano-halftone__scan', 'andantino-piano-combo__scan-severe', 'andantino-piano-yellowed__scan-severe']) {
  const g = readGray(C + n + '__r200/p-1.pgm'), q = cvm.pageQuality(g), ops = cvm.precleanPlan(q);
  t = performance.now(); const a = cvm.applyOps(cv, g, ops, q); const ta = performance.now() - t;
  t = performance.now(); const b = cvm.applyOpsJs(g, ops, q); const tb = performance.now() - t;
  let diff = 0, mx = 0; for (let i = 0; i < a.data.length; i++) { const dd = Math.abs(a.data[i] - b.data[i]); diff += dd; if (dd > mx) mx = dd; }
  console.log(n.padEnd(42), ops.join(','), 'opencv', Math.round(ta), 'ms  js', Math.round(tb), 'ms  mean|diff|', (diff / a.data.length).toFixed(3), 'max', mx);
}
