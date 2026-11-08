#!/usr/bin/env node
'use strict';
// Run the classical pipeline on any page image (no truth needed).
// usage: node tools/omr.js <image.png|jpg|pgm> [--overlay out.png] [--json out.json]
// JPEG input is converted to PGM via ImageMagick (node-only convenience).
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { readGray } = require('../src/image');
const { runOMR } = require('../src/pipeline');
const { drawOverlay } = require('./eval');
const args = process.argv.slice(2);
let img = args[0];
if (/\.jpe?g$/i.test(img)) {
  const tmp = path.join(require('os').tmpdir(), path.basename(img) + '.pgm');
  execFileSync('convert', [img, '-colorspace', 'Gray', tmp]);
  img = tmp;
}
const gray = readGray(img);
const det = runOMR(gray);
const oi = args.indexOf('--overlay'), ji = args.indexOf('--json');
if (oi >= 0) drawOverlay(args[oi + 1], gray, det, null);
if (ji >= 0) fs.writeFileSync(args[ji + 1], JSON.stringify(det));
const kinds = {}; const stems = {};
for (const h of det.heads) { kinds[h.kind] = (kinds[h.kind] || 0) + 1; stems[h.stem] = (stems[h.stem] || 0) + 1; }
console.log(JSON.stringify({ image: path.basename(args[0]), size: `${gray.width}x${gray.height}`, staffSpace: det.staffSpace, lineThickness: det.lineThickness,
  skew: det.skew.angle, staves: det.staves.length, systems: det.systems.map(s => s.length), heads: det.heads.length, kinds, stems, barlines: det.barlines.length, timings: det.timings }));
