// Per degradation class (and variant) aggregate from one or two challenge eval reports.
//   node perclass.js base.json [new.json]
'use strict';
const fs = require('fs');
const [A, B] = process.argv.slice(2).map(f => JSON.parse(fs.readFileSync(f, 'utf8')));
const cls = (id) => { const m = /^degradation\/[a-z0-9]+-[a-z0-9]+-(.+)\/(scan[^/]*)$/.exec(id); return m ? [m[1], m[2]] : null; };
const agg = (R) => { const t = {}; for (const i of R.items) { const c = cls(i.id); if (!c) continue; for (const k of [c[0], c[0] + ' ' + c[1]]) { (t[k] ||= []).push(i.aggregate || 0); } } return t; };
const ta = agg(A), tb = B ? agg(B) : null;
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const rows = Object.keys(ta).filter(k => !k.includes(' ')).sort();
console.log('class'.padEnd(16) + ['all', 'scan', 'scan-mild', 'scan-severe'].map(v => v.padStart(22)).join(''));
for (const c of rows) {
  const cell = (k) => { if (!ta[k]) return ''.padStart(22); const a = mean(ta[k]); if (!tb) return a.toFixed(3).padStart(22); const b = mean(tb[k]); return `${a.toFixed(3)}→${b.toFixed(3)} (${b - a >= 0 ? '+' : ''}${(b - a).toFixed(3)})`.padStart(22); };
  console.log(c.padEnd(16) + [c, c + ' scan', c + ' scan-mild', c + ' scan-severe'].map(cell).join(''));
}
if (B) console.log('challenge aggregate', A.summary.all.aggregate, '->', B.summary.all.aggregate, ' degradation', A.summary.by_category.degradation.aggregate, '->', B.summary.by_category.degradation.aggregate);
