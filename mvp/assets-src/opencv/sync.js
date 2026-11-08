// Copies the OpenCV.js pre-clean files (patched opencv.js, licence, notice) from
// assets-src/opencv/ into dist/assets/, checking each against SHA256SUMS.
//   node assets-src/opencv/sync.js [--check]
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const SRC = __dirname, DST = path.join(__dirname, '../../dist/assets');
const SHIP = ['opencv-4.10.0-noeval.js', 'LICENSE.opencv-js-Apache-2.0.txt', 'NOTICE.opencv.txt'];
const sums = Object.fromEntries(fs.readFileSync(path.join(SRC, 'SHA256SUMS'), 'utf8').trim().split('\n').map(l => l.trim().split(/\s+/)).map(([h, f]) => [f.replace(/^\.\//, ''), h]));
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
let bad = 0;
for (const f of SHIP) {
  const s = path.join(SRC, f);
  if (sums[f] && sha(s) !== sums[f]) { console.error('checksum mismatch:', f); bad++; continue; }
  if (process.argv.includes('--check')) {
    const d = path.join(DST, f);
    if (!fs.existsSync(d) || sha(d) !== sha(s)) { console.error('dist differs:', f); bad++; }
    continue;
  }
  fs.mkdirSync(DST, { recursive: true });
  const tmp = path.join(DST, `.${f}.${process.pid}.tmp`);
  fs.copyFileSync(s, tmp);
  fs.renameSync(tmp, path.join(DST, f));
}
if (bad) process.exit(1);
console.log(process.argv.includes('--check') ? 'dist/assets OpenCV files match' : `copied ${SHIP.length} OpenCV files to dist/assets`);
