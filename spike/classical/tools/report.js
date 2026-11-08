#!/usr/bin/env node
'use strict';
// Aggregate results JSONL into markdown tables.
// usage: node tools/report.js results/run.jsonl [--by cond|dpi|piece|cond,dpi] [--md]
const fs = require('fs');
const args = process.argv.slice(2);
const rows = fs.readFileSync(args[0], 'utf8').trim().split('\n').map(l => JSON.parse(l));
const bi = args.indexOf('--by');
const by = bi >= 0 ? args[bi + 1].split(',') : ['cond'];
const CONDS = ['clean', 'rot+0.6', 'rot-2', 'rot+4', 'blur1', 'blur2', 'noise20', 'noise45', 'jpeg25', 'jpeg8', 'light', 'speckle', 'bin_thick', 'bin_faded', 'bin_thin', 'warp', 'scan', 'phone'];

function sumPRF(list, key) {
  let tp = 0, fp = 0, fn = 0;
  for (const r of list) { const m = key.split('.').reduce((o, k) => o && o[k], r); if (!m) continue; tp += m.tp; fp += m.fp; fn += m.fn; }
  const p = tp + fp ? tp / (tp + fp) : 1, rc = tp + fn ? tp / (tp + fn) : 1;
  return { p, r: rc, f1: p + rc ? 2 * p * rc / (p + rc) : 0, tp, fp, fn };
}
const mean = (list, f) => { const v = list.map(f).filter(x => x !== null && x !== undefined && !Number.isNaN(x)); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : NaN; };
const pct = v => Number.isNaN(v) ? '–' : (100 * v).toFixed(1);

const groups = new Map();
for (const r of rows) {
  const k = by.map(b => r[b]).join(' / ');
  if (!groups.has(k)) groups.set(k, []);
  groups.get(k).push(r);
}
const order = [...groups.keys()].sort((a, b) => {
  const ka = a.split(' / '), kb = b.split(' / ');
  for (let i = 0; i < by.length; i++) {
    if (by[i] === 'cond') { const d = CONDS.indexOf(ka[i]) - CONDS.indexOf(kb[i]); if (d) return d; }
    else if (by[i] === 'dpi') { const d = +ka[i] - +kb[i]; if (d) return d; }
    else { const d = ka[i].localeCompare(kb[i]); if (d) return d; }
  }
  return 0;
});
const hdr = ['group', 'n', 'staff R', 'line err px', 'skew err°', 'ss err %', 'head P', 'head R', 'head F1', 'filled F1', 'half F1', 'kind acc', 'pitch acc', 'stem acc', 'SATB voice acc', 'bar P', 'bar R', 'sys ok', 'ms'];
console.log('| ' + hdr.join(' | ') + ' |');
console.log('|' + hdr.map(() => '---').join('|') + '|');
const all = [];
for (const k of order) {
  const L = groups.get(k);
  const st = sumPRF(L, 'staves'), hd = sumPRF(L, 'heads'), fl = sumPRF(L, 'headsByKind.filled'), hf = sumPRF(L, 'headsByKind.half'), bl = sumPRF(L, 'barlines');
  const sysOk = L.reduce((a, r) => a + r.systems.correct, 0) / Math.max(1, L.reduce((a, r) => a + r.systems.truth, 0));
  const row = [k, L.length, pct(st.r), mean(L, r => r.staffLineErrPx).toFixed(2), mean(L, r => r.skewErrDeg).toFixed(2), pct(mean(L, r => r.staffSpaceRelErr)),
    pct(hd.p), pct(hd.r), pct(hd.f1), pct(fl.f1), pct(hf.f1), pct(mean(L, r => r.headKindAcc)), pct(mean(L, r => r.headPitchAcc)), pct(mean(L, r => r.headStemDirAcc)),
    pct(L.reduce((a, r) => a + (r.voiceOK || 0), 0) / Math.max(1, L.reduce((a, r) => a + (r.voiceN || 0), 0))),
    pct(bl.p), pct(bl.r), pct(sysOk), Math.round(mean(L, r => r.ms))];
  console.log('| ' + row.join(' | ') + ' |');
  all.push(...L);
}
if (args.includes('--total')) {
  const hd = sumPRF(all, 'heads'), bl = sumPRF(all, 'barlines'), st = sumPRF(all, 'staves');
  console.log(`\nTOTAL n=${all.length} staffR=${pct(st.r)} headP=${pct(hd.p)} headR=${pct(hd.r)} headF1=${pct(hd.f1)} barP=${pct(bl.p)} barR=${pct(bl.r)} kind=${pct(mean(all, r => r.headKindAcc))} pitch=${pct(mean(all, r => r.headPitchAcc))} stem=${pct(mean(all, r => r.headStemDirAcc))}`);
}
