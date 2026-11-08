// Load OpenCV.js in node: the no-eval patched 4.10.0 build (vendor/), the same file the browser would use.
// The emscripten Module is a thenable: never resolve a promise with it directly (that loops forever).
'use strict';
const path = require('path');
let p = null;
module.exports = function loadCv(file = path.join(__dirname, '../vendor/opencv-4.10.0-noeval.js')) {
  if (!p) p = new Promise((resolve) => {
    const cv = require(file);
    const done = () => { const c = cv; if (typeof c.then === 'function') delete c.then; resolve({ cv: c }); };
    if (cv.Mat) done(); else cv.onRuntimeInitialized = done;
  }).then(w => w.cv);
  return p;
};
