// dewarp gate measures (spread, bend, lean) for cached pages matching the arguments
const fs = require('fs'), path = require('path');
const src = process.env.SRC || '/Users/d.sloane/music/spike/opencv/src-dw/';
const { readGray } = require(src + 'image.js'), { frontSteps } = require(src + 'front.js'), cvm = require(src + 'cv.js');
const C = '/Users/d.sloane/music/mvp/work/cache';
const pats = process.argv.slice(2);
for (const d of fs.readdirSync(C).filter(d => d.endsWith('__r200') && pats.some(p => d.includes(p))).sort()) {
  const it = frontSteps(readGray(path.join(C, d, 'p-1.pgm')), {}); let r = it.next(); while (!r.done) r = it.next();
  const msgs = []; const orig = console.error; console.error = (...a) => msgs.push(a.join(' '));
  process.env.DW_DEBUG = '1'; const g = cvm.dewarpPage(r.value, {}); console.error = orig;
  console.log(d.replace(/__r200$/, '').replace(/^challenge__/, '').padEnd(64), msgs.join(' ').replace('dewarp ', ''), g ? 'WARP' : '-');
}
