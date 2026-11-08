// Time-signature digit reading, given the time-signature box (the classical header finds it):
// template-only (Bravura, no training), HOG-kNN (trained on the other fold), and the two combined.
'use strict';
const fs = require('fs'), path = require('path');
const { load } = require('./samples');
const { trainKnn } = require('./classifiers');
const S = load(); const F = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/feat.json'), 'utf8')).F;
const D = ['digit-1', 'digit-2', 'digit-3', 'digit-4', 'digit-5', 'digit-6', 'digit-7', 'digit-8', 'digit-9', 'digit-0'];
const isD = (l) => /^digit-/.test(l);
const res = {};
for (const tf of [0, 1]) {
  const tr = S.map((s, i) => i).filter(i => S[i].fold !== tf && isD(S[i].lab));
  const te = S.map((s, i) => i).filter(i => S[i].fold === tf && isD(S[i].lab));
  const knn = trainKnn(tr.map(i => F[i].hg), tr.map(i => S[i].lab), 3);
  for (const i of te) {
    const s = S[i], tp = F[i].tp;
    const tBest = D.reduce((a, d) => (tp[d] > tp[a] ? d : a), D[0]);
    const k = knn.predict(F[i].hg);
    // combined: template unless the kNN is confident and disagrees with a weak template match
    const comb = (tp[tBest] >= 0.55 || k.conf < 0.67) ? tBest : k.lab;
    for (const [ap, p] of [['template', tBest], ['hog-knn', k.lab], ['combined', comb]]) {
      const r = ((res[ap] ||= {})[s.variant] ||= { ok: 0, n: 0 }); r.n++; if (p === s.lab) r.ok++;
    }
  }
}
for (const [ap, v] of Object.entries(res)) console.log(ap.padEnd(10), Object.entries(v).map(([k, r]) => `${k} ${(100 * r.ok / r.n).toFixed(1)}% (${r.ok}/${r.n})`).join('  '));
