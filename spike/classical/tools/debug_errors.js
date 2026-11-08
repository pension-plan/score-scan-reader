#!/usr/bin/env node
'use strict';
// Show notehead / barline errors for one image: prints FP/FN lists and writes a
// contact sheet of crops (FP heads red frame, FN heads blue frame, FP barlines orange).
// usage: node tools/debug_errors.js <image> <truth.json> <sheet.png> [--opts json]
const fs = require('fs');
const { readGray, writePNGrgb } = require('../src/image');
const { runOMR } = require('../src/pipeline');

const [img, tr, sheet] = process.argv.slice(2);
const opi = process.argv.indexOf('--opts');
const opts = opi >= 0 ? JSON.parse(process.argv[opi + 1]) : {};
const gray = readGray(img);
const truth = JSON.parse(fs.readFileSync(tr, 'utf8'));
const det = runOMR(gray, { ...opts, debug: true });
const ss = truth.meta.staffSpace;
const raw = det._debug.headsRaw;
const fps = [], fns = [];
const tUsed = new Set();
det.heads.forEach((h, i) => {
  let best = -1, bd = 1e9;
  truth.heads.forEach((t, j) => { if (tUsed.has(j)) return; const d = Math.hypot(h.x - t.c[0], h.y - t.c[1]); if (d < bd) { bd = d; best = j; } });
  if (bd < 0.5 * ss) tUsed.add(best); else fps.push({ ...h, f: raw[i] && raw[i].f });
});
truth.heads.forEach((t, j) => { if (!tUsed.has(j)) fns.push(t); });
const r2 = (o) => Object.fromEntries(Object.entries(o || {}).map(([k, v]) => [k, typeof v === 'number' ? +v.toFixed(2) : v]));
console.log(`heads det=${det.heads.length} truth=${truth.heads.length} FP=${fps.length} FN=${fns.length}`);
fps.forEach((h, k) => console.log(`FP#${k} x=${h.x} y=${h.y} kind=${h.kind} staff=${h.staff} p=${h.p} score=${h.score} stem=${h.stem}/${h.stemLen}`, JSON.stringify(r2(h.f))));
fns.forEach((t, k) => console.log(`FN#${k} x=${t.c[0].toFixed(0)} y=${t.c[1].toFixed(0)} kind=${t.kind} staff=${t.staff} pos=${t.staffPos} voices=${t.voices}`));
// barline errors
const tb = truth.barlines.map(b => ({ x: (b.bb[0] + b.bb[2]) / 2, y: (b.bb[1] + b.bb[3]) / 2 }));
const bUsed = new Set(); const bfp = [];
det.barlines.forEach(b => {
  let best = -1, bd = 1e9;
  tb.forEach((t, k) => { if (bUsed.has(k)) return; const d = Math.abs(t.x - b.x) + Math.abs(t.y - (b.y0 + b.y1) / 2) * 0.2; if (d < bd) { bd = d; best = k; } });
  if (bd < ss) bUsed.add(best); else bfp.push(b);
});
const bfn = tb.filter((t, k) => !bUsed.has(k));
console.log(`barlines det=${det.barlines.length} truth=${tb.length} FP=${bfp.length} FN=${bfn.length}`);
bfp.forEach(b => console.log('barFP', JSON.stringify(b)));
bfn.forEach(b => console.log('barFN', JSON.stringify(b)));
// contact sheet
const items = [...fps.map(h => ({ x: h.x, y: h.y, c: [230, 0, 0] })), ...fns.map(t => ({ x: t.c[0], y: t.c[1], c: [0, 0, 230] })),
  ...bfp.map(b => ({ x: b.x, y: (b.y0 + b.y1) / 2, c: [255, 140, 0] })), ...bfn.map(b => ({ x: b.x, y: b.y, c: [0, 160, 0] }))];
if (sheet && items.length) {
  const cs = Math.round(6 * ss), cols = 8, rows = Math.ceil(items.length / cols);
  const W = cols * (cs + 4), H = rows * (cs + 4);
  const rgb = new Uint8Array(W * H * 3).fill(255);
  items.forEach((it, k) => {
    const ox = (k % cols) * (cs + 4), oy = Math.floor(k / cols) * (cs + 4);
    for (let y = 0; y < cs; y++) for (let x = 0; x < cs; x++) {
      const sx = Math.round(it.x - cs / 2 + x), sy = Math.round(it.y - cs / 2 + y);
      const v = sx >= 0 && sy >= 0 && sx < gray.width && sy < gray.height ? gray.data[sy * gray.width + sx] : 255;
      const i = ((oy + y) * W + ox + x) * 3;
      const border = x < 2 || y < 2 || x >= cs - 2 || y >= cs - 2;
      const centre = Math.abs(x - cs / 2) + Math.abs(y - cs / 2) < 2;
      if (border || centre) { rgb[i] = it.c[0]; rgb[i + 1] = it.c[1]; rgb[i + 2] = it.c[2]; } else rgb[i] = rgb[i + 1] = rgb[i + 2] = v;
    }
  });
  writePNGrgb(sheet, W, H, rgb);
}
