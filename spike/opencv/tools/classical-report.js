// Summarise data/classical/*.jsonl: per family and variant, micro precision / recall of the classical reading.
'use strict';
const fs = require('fs'), path = require('path');
const D = process.env.CDIR || path.join(__dirname, '../data/classical');
const rows = [];
for (const f of fs.readdirSync(D)) for (const l of fs.readFileSync(path.join(D, f), 'utf8').split('\n')) if (l) rows.push({ ...JSON.parse(l), key: f });
const res = {};
for (const variant of ['clean', 'scan', 'scan-severe']) {
  const V = rows.filter(r => r.variant === variant);
  const out = res[variant] = {};
  // rests: positives = truth rests; FP = detections of the wrong kind or matching no truth rest
  const R = V.filter(r => r.fam === 'rests');
  let tp = 0, fp = 0, fn = 0; const per = {};
  for (const r of R) {
    const c = (per[r.lab] ||= { tp: 0, fn: 0, fp: 0 });
    if (r.lab === 'none') { fp++; (per[r.pred] ||= { tp: 0, fn: 0, fp: 0 }).fp++; continue; }
    if (r.pred === r.lab) { tp++; c.tp++; } else { fn++; c.fn++; if (r.pred !== 'none') { fp++; (per[r.pred] ||= { tp: 0, fn: 0, fp: 0 }).fp++; } }
  }
  out.rests = { tp, fp, fn, per };
  const A = V.filter(r => r.fam === 'accidentals'); tp = fp = fn = 0; const pa = {};
  for (const r of A) {
    if (r.lab !== 'neg') { const c = (pa[r.lab] ||= { tp: 0, fn: 0, fp: 0 }); if (r.pred === r.lab) { tp++; c.tp++; } else { fn++; c.fn++; if (r.pred !== 'neg') { fp++; (pa[r.pred] ||= { tp: 0, fn: 0, fp: 0 }).fp++; } } }
    else if (r.pred !== 'neg') { fp++; (pa[r.pred] ||= { tp: 0, fn: 0, fp: 0 }).fp++; }
  }
  out.accidentals = { tp, fp, fn, per: pa };
  const C = V.filter(r => r.fam === 'clefs'); tp = fp = fn = 0; const pc = {};
  for (const r of C) { const c = (pc[r.lab] ||= { tp: 0, fn: 0, fp: 0 }); if (r.pred === r.lab) { tp++; c.tp++; } else { fn++; c.fn++; if (r.pred !== 'none') { fp++; (pc[r.pred] ||= { tp: 0, fn: 0, fp: 0 }).fp++; } } }
  out.clefs = { tp, fp, fn, per: pc };
  const T = V.filter(r => r.fam === 'time');
  out.time = { n: T.length, found: T.filter(r => r.found).length, read_right: T.filter(r => r.pred === r.lab || (r.pred === '4/4' && r.lab === '4/4' ) ).length,
    numbered: T.filter(r => r.style === 'numbered').length, numbered_read: T.filter(r => r.style === 'numbered' && r.pred === r.lab).length };
}
fs.writeFileSync(path.join(__dirname, '../data/classical-summary.json'), JSON.stringify(res, null, 1));
const pr = (o) => `${o.tp + o.fp ? (100 * o.tp / (o.tp + o.fp)).toFixed(0) : '-'}/${o.tp + o.fn ? (100 * o.tp / (o.tp + o.fn)).toFixed(0) : '-'}`;
for (const [v, o] of Object.entries(res)) {
  console.log(`== ${v}: rests ${pr(o.rests)}  accidentals ${pr(o.accidentals)}  clefs ${pr(o.clefs)}  time found ${o.time.found}/${o.time.n}, numbers read ${o.time.numbered_read}/${o.time.numbered}`);
  for (const fam of ['rests', 'accidentals', 'clefs']) console.log('   ' + fam + ': ' + Object.entries(o[fam].per).sort().map(([k, c]) => `${k} ${pr(c)}`).join(', '));
}
