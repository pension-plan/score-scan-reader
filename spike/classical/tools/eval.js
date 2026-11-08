#!/usr/bin/env node
'use strict';
// Run the classical pipeline on one image and score it against truth.
// usage: node tools/eval.js <image.png|pgm> <truth.json> [--overlay out.png] [--opts '{json}']
const fs = require('fs');
const path = require('path');
const { readGray } = require('../src/image');
const { runOMR } = require('../src/pipeline');

function interpY(pts, x) {
  if (x <= pts[0][0]) return pts[0][1] + (pts.length > 1 ? (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0] || 1) * (x - pts[0][0]) : 0);
  for (let i = 1; i < pts.length; i++) {
    if (pts[i][0] >= x) { const t = (x - pts[i - 1][0]) / ((pts[i][0] - pts[i - 1][0]) || 1); return pts[i - 1][1] * (1 - t) + pts[i][1] * t; }
  }
  const n = pts.length;
  return pts[n - 1][1] + (n > 1 ? (pts[n - 1][1] - pts[n - 2][1]) / ((pts[n - 1][0] - pts[n - 2][0]) || 1) * (x - pts[n - 1][0]) : 0);
}

function prf(tp, fp, fn) {
  const p = tp + fp ? tp / (tp + fp) : (fn ? 0 : 1);
  const r = tp + fn ? tp / (tp + fn) : 1;
  return { tp, fp, fn, precision: +p.toFixed(4), recall: +r.toFixed(4), f1: +(p + r ? 2 * p * r / (p + r) : 0).toFixed(4) };
}

function evaluate(det, truth) {
  const ss = truth.meta.staffSpace;
  const M = {};
  M.staffSpaceRelErr = +(Math.abs(det.staffSpace - ss) / ss).toFixed(4);
  M.lineThicknessErr = +(det.lineThickness - truth.meta.lineThickness).toFixed(3);
  const trueRot = truth.meta.transform ? truth.meta.transform.rotDeg || 0 : 0;
  M.skewErrDeg = +Math.abs(det.skew.angle - trueRot).toFixed(3);

  // ---- staves: match by middle line at the staff's horizontal centre
  const tStaves = truth.staves.map((s, i) => {
    const xs = s.lines[2].pts.map(p => p[0]);
    const xc = (Math.min(...xs) + Math.max(...xs)) / 2;
    return { i, xc, y: interpY(s.lines[2].pts, xc), s };
  });
  const map = new Map(); // det staff -> truth staff
  const usedT = new Set();
  let lineErrSum = 0, lineErrN = 0, lineErrMax = 0;
  for (const ds of det.staves) {
    let best = -1, bd = 1e9;
    for (const ts of tStaves) {
      if (usedT.has(ts.i)) continue;
      const d = Math.abs(interpY(ds.lines[2], ts.xc) - ts.y);
      if (d < bd) { bd = d; best = ts.i; }
    }
    if (best >= 0 && bd < 0.6 * ss) {
      map.set(ds.index, best); usedT.add(best);
      const ts = tStaves[best].s;
      for (let k = 0; k < 5; k++) {
        for (const [x, y] of ds.lines[k]) {
          const tx = ts.lines[k].pts.map(p => p[0]);
          if (x < Math.min(...tx) || x > Math.max(...tx)) continue;
          const e = Math.abs(y - interpY(ts.lines[k].pts, x));
          lineErrSum += e; lineErrN++; if (e > lineErrMax) lineErrMax = e;
        }
      }
    }
  }
  M.staves = prf(map.size, det.staves.length - map.size, truth.staves.length - map.size);
  M.staffLineErrPx = lineErrN ? +(lineErrSum / lineErrN).toFixed(3) : null;
  M.staffLineErrMaxSS = lineErrN ? +(lineErrMax / ss).toFixed(3) : null;
  // systems: compare partitions (as sets of truth staff indices)
  const tSys = new Map(); truth.staves.forEach((s, i) => { (tSys.get(s.system) || tSys.set(s.system, []).get(s.system)).push(i); });
  const tSysKeys = new Set([...tSys.values()].map(a => a.join(',')));
  const dSysKeys = det.systems.map(g => g.map(k => map.get(k)).filter(v => v !== undefined).join(','));
  M.systems = { truth: tSys.size, detected: det.systems.length, correct: dSysKeys.filter(k => tSysKeys.has(k)).length };

  // ---- noteheads
  const tHeads = truth.heads.map(h => ({ ...h, kindN: h.kind === 'filled' ? 'filled' : (h.kind === 'half' ? 'half' : 'whole') }));
  const pairs = [];
  for (let i = 0; i < det.heads.length; i++) {
    for (let j = 0; j < tHeads.length; j++) {
      const dx = det.heads[i].x - tHeads[j].c[0], dy = det.heads[i].y - tHeads[j].c[1];
      const d = Math.hypot(dx, dy);
      if (d < 0.5 * ss) pairs.push([d, i, j]);
    }
  }
  pairs.sort((a, b) => a[0] - b[0]);
  const dm = new Int32Array(det.heads.length).fill(-1), tm = new Int32Array(tHeads.length).fill(-1);
  for (const [, i, j] of pairs) if (dm[i] < 0 && tm[j] < 0) { dm[i] = j; tm[j] = i; }
  const tp = [...dm].filter(v => v >= 0).length;
  M.heads = prf(tp, det.heads.length - tp, tHeads.length - tp);
  const byKind = {};
  for (const k of ['filled', 'half', 'whole']) {
    const tk = tHeads.map((h, j) => j).filter(j => tHeads[j].kindN === k);
    const dk = det.heads.map((h, i) => i).filter(i => det.heads[i].kind === k);
    const tpk = dk.filter(i => dm[i] >= 0 && tHeads[dm[i]].kindN === k).length;
    byKind[k] = prf(tpk, dk.length - tpk, tk.length - tpk);
  }
  M.headsByKind = byKind;
  let kindOK = 0, pitchOK = 0, pitchN = 0, stemOK = 0, stemN = 0, matched = 0, posErr = 0;
  const confusion = {};
  for (let i = 0; i < det.heads.length; i++) {
    const j = dm[i]; if (j < 0) continue;
    matched++;
    const d = det.heads[i], t = tHeads[j];
    posErr += Math.hypot(d.x - t.c[0], d.y - t.c[1]);
    if (d.kind === t.kindN) kindOK++;
    const key = t.kindN + '->' + d.kind; confusion[key] = (confusion[key] || 0) + 1;
    if (map.get(d.staff) === t.staff && t.staffPos !== undefined) { pitchN++; if (d.p === t.staffPos) pitchOK++; }
    else pitchN++;
    if (t.kindN !== 'whole') {
      const dirs = new Set(t.stemDirs.filter(v => v));
      const tdir = dirs.size === 2 ? 2 : (dirs.has(1) ? 1 : (dirs.has(-1) ? -1 : 0));
      if (tdir) { stemN++; if (d.stem === tdir) stemOK++; }
    }
  }
  M.headKindAcc = matched ? +(kindOK / matched).toFixed(4) : null;
  M.headPitchAcc = pitchN ? +(pitchOK / pitchN).toFixed(4) : null;
  M.headStemDirAcc = stemN ? +(stemOK / stemN).toFixed(4) : null;
  M.headPosErrSS = matched ? +(posErr / matched / ss).toFixed(3) : null;
  M.headKindConfusion = confusion;

  // ---- closed-score voice assignment from stem direction (SATB pieces only):
  // upper staff of a system: stem up = S, down = A; lower staff: up = T, down = B
  const isSATB = tHeads.some(h => h.voices && h.voices.includes('S'));
  if (isSATB) {
    const sysFirst = new Map();
    for (const st of det.staves) if (!sysFirst.has(st.system)) sysFirst.set(st.system, st.index);
    let ok = 0, n = 0, sharedN = 0, sharedOK = 0;
    for (let i = 0; i < det.heads.length; i++) {
      const j = dm[i]; if (j < 0) continue;
      const d = det.heads[i], t = tHeads[j];
      const st = det.staves[d.staff];
      const role = st ? d.staff - sysFirst.get(st.system) : 0;
      const [up, down] = role === 0 ? ['S', 'A'] : ['T', 'B'];
      const pred = d.stem === 1 ? [up] : d.stem === -1 ? [down] : d.stem === 2 ? [up, down] : [];
      const tv = [...new Set(t.voices)].sort().join(''), pv = pred.sort().join('');
      n++; if (tv === pv) ok++;
      if (new Set(t.voices).size === 2) { sharedN++; if (tv === pv) sharedOK++; }
    }
    M.voiceAcc = n ? +(ok / n).toFixed(4) : null;
    M.voiceN = n; M.voiceOK = ok; M.sharedHeads = sharedN; M.sharedHeadsOK = sharedOK;
  }

  // ---- barlines (per staff, x within 1 ss)
  const tBars = truth.barlines.map(b => ({ x: (b.bb[0] + b.bb[2]) / 2, staff: b.staff, y: (b.p0[1] + b.p1[1]) / 2 }));
  const used = new Set();
  let btp = 0;
  for (const b of det.barlines) {
    const ts = map.get(b.staff);
    let best = -1, bd = 1e9;
    tBars.forEach((t, k) => {
      if (used.has(k) || t.staff !== ts) return;
      const d = Math.abs(t.x - b.x);
      if (d < bd) { bd = d; best = k; }
    });
    if (best >= 0 && bd < 1.0 * ss) { used.add(best); btp++; }
  }
  M.barlines = prf(btp, det.barlines.length - btp, tBars.length - btp);
  return M;
}

function drawOverlay(file, gray, det, truth) {
  const { writePNGrgb } = require('../src/image');
  const W = gray.width, H = gray.height;
  const rgb = new Uint8Array(W * H * 3);
  for (let i = 0; i < W * H; i++) { const v = 128 + (gray.data[i] >> 1); rgb[i * 3] = rgb[i * 3 + 1] = rgb[i * 3 + 2] = v; }
  const put = (x, y, c) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 3; rgb[i] = c[0]; rgb[i + 1] = c[1]; rgb[i + 2] = c[2]; };
  const circle = (x, y, r, c) => { for (let a = 0; a < 64; a++) put(x + r * Math.cos(a / 64 * 2 * Math.PI), y + r * Math.sin(a / 64 * 2 * Math.PI), c); };
  const line = (x0, y0, x1, y1, c) => { const n = Math.ceil(Math.hypot(x1 - x0, y1 - y0)); for (let k = 0; k <= n; k++) put(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, c); };
  const ss = det.staffSpace;
  for (const st of det.staves) for (const l of st.lines) for (let k = 1; k < l.length; k++) line(l[k - 1][0], l[k - 1][1], l[k][0], l[k][1], [0, 170, 0]);
  if (truth) for (const h of truth.heads) circle(h.c[0], h.c[1], 0.15 * ss, [0, 0, 255]);
  for (const h of det.heads) {
    const c = h.kind === 'filled' ? [230, 0, 0] : (h.kind === 'half' ? [230, 120, 0] : [200, 0, 200]);
    circle(h.x, h.y, 0.55 * ss, c); circle(h.x, h.y, 0.58 * ss, c);
    if (h.stem === 1 || h.stem === 2) line(h.x + 0.6 * ss, h.y, h.x + 0.6 * ss, h.y - 2.5 * ss, [255, 0, 255]);
    if (h.stem === -1 || h.stem === 2) line(h.x - 0.6 * ss, h.y, h.x - 0.6 * ss, h.y + 2.5 * ss, [0, 160, 255]);
  }
  for (const b of det.barlines) { line(b.x - 2, b.y0, b.x - 2, b.y1, [0, 120, 255]); line(b.x + 2, b.y0, b.x + 2, b.y1, [0, 120, 255]); }
  writePNGrgb(file, W, H, rgb);
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const img = args[0], tr = args[1];
  const oi = args.indexOf('--overlay');
  const opi = args.indexOf('--opts');
  const opts = opi >= 0 ? JSON.parse(args[opi + 1]) : {};
  const gray = readGray(img);
  const truth = JSON.parse(fs.readFileSync(tr, 'utf8'));
  const t0 = Date.now();
  const det = runOMR(gray, opts);
  const ms = Date.now() - t0;
  const M = evaluate(det, truth);
  const name = path.basename(img).replace(/\.(png|pgm)$/, '');
  const [piece, dpi, ...cond] = name.split('_');
  const rec = { name, piece, dpi: +dpi, cond: cond.join('_') || 'clean', ms, timings: det.timings, ss: det.staffSpace, lt: det.lineThickness, skew: det.skew.angle, binarize: det.binarize, ...M };
  if (oi >= 0) drawOverlay(args[oi + 1], gray, det, truth);
  if (args.includes('--det')) rec.det = det;
  console.log(JSON.stringify(rec));
}

module.exports = { evaluate, drawOverlay };
