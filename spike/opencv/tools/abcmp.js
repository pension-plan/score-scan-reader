// Compare two eval reports (fallback off vs on): summary deltas, items that changed, and the first
// time signature of each output against the truth's.
//   node abcmp.js off.json on.json
'use strict';
const fs = require('fs'), path = require('path');
const [A, B] = process.argv.slice(2).map(f => JSON.parse(fs.readFileSync(f, 'utf8')));
const keys = ['aggregate', 'pitch', 'duration', 'rests', 'parts', 'lyrics', 'xml_valid', 'crashes', 'runtime_ms_mean'];
const sa = A.summary.all, sb = B.summary.all;
console.log('n', sa.n, keys.map(k => `${k} ${sa[k]} -> ${sb[k]} (${(sb[k] - sa[k] >= 0 ? '+' : '') + (sb[k] - sa[k]).toFixed(k === 'runtime_ms_mean' ? 0 : 4)})`).join(' | '));
for (const grp of ['by_family', 'by_variant', 'by_category']) if (A.summary[grp]) {
  for (const [g, va] of Object.entries(A.summary[grp])) { const vb = B.summary[grp][g]; if (!vb) continue; const d = (vb.aggregate - va.aggregate); console.log(`  ${grp} ${g.padEnd(14)} n=${va.n} agg ${va.aggregate} -> ${vb.aggregate} (${d >= 0 ? '+' : ''}${d.toFixed(4)})  dur ${va.duration}->${vb.duration} pitch ${va.pitch}->${vb.pitch} rests ${va.rests}->${vb.rests}`); }
}
const firstTime = (xml) => { const m = /<time[^>]*>\s*<beats>(\d+)<\/beats>\s*<beat-type>(\d+)<\/beat-type>/.exec(xml || ''); return m ? `${m[1]}/${m[2]}` : null; };
const CORPUS = path.join(__dirname, '../../../corpus');
const truthOf = (i) => { const p = i.id.split('/'); return i.set === 'challenge' || i.set === 'coverage' ? path.join(CORPUS, i.set, p[0], p[1], 'truth.musicxml') : path.join(CORPUS, i.set, i.id, 'truth.musicxml'); };
const ib = new Map(B.items.map(i => [i.id, i]));
let changed = 0, tA = 0, tB = 0, nT = 0;
const rows = [];
for (const ia of A.items) {
  const i2 = ib.get(ia.id); if (!i2) continue;
  const d = (i2.aggregate ?? 0) - (ia.aggregate ?? 0);
  const outA = path.join(A.config.outputs, `${ia.set}__${ia.id.replace(/\//g, '__')}.musicxml`), outB = path.join(B.config.outputs, `${ia.set}__${ia.id.replace(/\//g, '__')}.musicxml`);
  let ta = null, tb = null, tt = null;
  try { ta = firstTime(fs.readFileSync(outA, 'utf8')); tb = firstTime(fs.readFileSync(outB, 'utf8')); tt = firstTime(fs.readFileSync(truthOf(ia), 'utf8')); } catch (e) { /* missing */ }
  if (tt) { nT++; if (ta === tt) tA++; if (tb === tt) tB++; }
  if (Math.abs(d) > 1e-9 || ta !== tb) { changed++; rows.push({ id: ia.id, d, a: ia.aggregate, b: i2.aggregate, dur: `${ia.duration}->${i2.duration}`, time: `${ta}->${tb} (truth ${tt})` }); }
}
console.log(`items changed: ${changed}/${A.items.length}; first time signature right: off ${tA}/${nT}, on ${tB}/${nT}`);
rows.sort((p, q) => p.d - q.d);
for (const r of rows) console.log(`  ${r.d >= 0 ? '+' : ''}${r.d.toFixed(4)} ${r.id}  agg ${r.a}->${r.b} dur ${r.dur} time ${r.time}`);
