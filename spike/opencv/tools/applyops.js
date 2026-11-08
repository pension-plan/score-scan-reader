// apply pre-clean ops to a cached page and save a downscaled PNG: node applyops.js page.pgm ops out.png [scale]
const path = require('path'), fs = require('fs');
process.env.OPENCV_JS = process.env.OPENCV_JS || path.join(__dirname, '../vendor/opencv-4.10.0-noeval.js');
const cvm = require('../../../mvp/src/cv.js');
const { readGray } = require('../../../mvp/src/image.js');
const { PNG } = require('../../../node_modules/pngjs');
const [f, ops, out, s = 3] = process.argv.slice(2);
const g = readGray(f);
const q = cvm.pageQuality(g); console.log(JSON.stringify(q), 'auto plan', cvm.precleanPlan(q));
if (ops !== 'none') process.env.OMR_PRECLEAN_OPS = ops === 'auto' ? '' : ops;
const r = ops === 'none' ? g : cvm.precleanPage(g);
const S = +s, p = new PNG({ width: Math.floor(r.width / S), height: Math.floor(r.height / S) });
for (let j = 0; j < p.height; j++) for (let i = 0; i < p.width; i++) { const v = r.data[j * S * r.width + i * S]; const k = (j * p.width + i) * 4; p.data[k] = p.data[k + 1] = p.data[k + 2] = v; p.data[k + 3] = 255; }
fs.writeFileSync(out, PNG.sync.write(p));
