// Offline A/B of the three OpenCV.js fallback approaches on labelled glyph patches.
//   node exp.js [--feat]   (--feat recomputes data/feat.json)
// 2-fold cross-validation by item (items never straddle folds); train on all variants of the train
// items, test on each variant of the test items. Negatives (noteheads, other scripts, other
// components) score as one class 'neg'. Output: data/exp.json + a table on stdout.
'use strict';
const fs = require('fs'), path = require('path');
const loadCv = require('./cvload');
const { load } = require('./samples');
const { shapeFeatures, hogFeatures, templateScores, loadTemplates, TPL_CLASS } = require('./features');
const { trainKnn, trainSvm } = require('./classifiers');
const FEAT = path.join(__dirname, '../data/feat.json');

(async () => {
  const cv = await loadCv();
  const S = load();
  let F;
  if (process.argv.includes('--feat') || !fs.existsSync(FEAT)) {
    const bank = loadTemplates(cv, JSON.parse(fs.readFileSync(path.join(__dirname, '../data/templates.json'), 'utf8')));
    const ms = { shape: 0, hog: 0, tpl: 0 };
    F = S.map((s, i) => {
      let t = performance.now(); const sh = shapeFeatures(cv, s); ms.shape += performance.now() - t;
      t = performance.now(); const hg = hogFeatures(cv, s); ms.hog += performance.now() - t;
      t = performance.now(); const tp = templateScores(cv, bank, s); ms.tpl += performance.now() - t;
      if (i % 2000 === 0) console.error('feat', i, '/', S.length);
      return { sh, hg, tp };
    });
    const per = Object.fromEntries(Object.entries(ms).map(([k, v]) => [k, +(v / S.length).toFixed(3)]));
    fs.writeFileSync(FEAT, JSON.stringify({ n: S.length, ms_per_patch: per, F }));
    console.error('ms per patch', per);
  } else F = JSON.parse(fs.readFileSync(FEAT, 'utf8')).F;
  const msPer = JSON.parse(fs.readFileSync(FEAT, 'utf8')).ms_per_patch;

  const score = (lab) => (lab.startsWith('neg') ? 'neg' : lab);
  const results = {}; // approach -> variant -> {tp, fp, fn per class}
  const add = (ap, variant, truth, pred) => {
    const R = (results[ap] ||= {}), V = (R[variant] ||= {});
    const t = score(truth), p = score(pred);
    (V[t] ||= { tp: 0, fp: 0, fn: 0 }); (V[p] ||= { tp: 0, fp: 0, fn: 0 });
    if (t === p) V[t].tp++; else { V[t].fn++; V[p].fp++; }
  };
  const tplClasses = Object.keys(TPL_CLASS);
  const predMs = {};
  for (const testFold of [0, 1]) {
    const tr = S.map((s, i) => i).filter(i => S[i].fold !== testFold && !S[i].lab.startsWith('digits-'));
    const te = S.map((s, i) => i).filter(i => S[i].fold === testFold && !S[i].lab.startsWith('digits-'));
    const y = tr.map(i => S[i].lab);
    let t0 = performance.now();
    const knnS = trainKnn(tr.map(i => F[i].sh), y, 3);
    const svmH = trainSvm(tr.map(i => F[i].hg), y);
    const knnH = trainKnn(tr.map(i => F[i].hg), y, 3);
    // (a) templates: argmax over classes, 'neg' below a threshold tuned on the train fold
    const tplPred = (f, tau) => { let lab = 'neg', b = -1; for (const c of tplClasses) if (f.tp[c] > b) { b = f.tp[c]; lab = c; } return b >= tau ? lab : 'neg'; };
    let bestTau = 0.3, bestAcc = -1;
    for (let tau = 0.2; tau <= 0.8; tau += 0.025) { let ok = 0; for (const i of tr) ok += score(tplPred(F[i], tau)) === score(S[i].lab); if (ok > bestAcc) { bestAcc = ok; bestTau = tau; } }
    // (a+c) template scores appended to HOG: does Bravura shape knowledge add to a trained model?
    const svmHT = trainSvm(tr.map(i => [...F[i].hg, ...tplClasses.map(c => F[i].tp[c])]), y);
    console.error('fold', testFold, 'train', tr.length, 'test', te.length, 'tau', bestTau.toFixed(3), 'train s', ((performance.now() - t0) / 1000).toFixed(1));
    const time = (k, fn) => { const t = performance.now(); const r = fn(); predMs[k] = (predMs[k] || 0) + performance.now() - t; return r; };
    for (const i of te) {
      const s = S[i];
      add('a-template', s.variant, s.lab, time('a-template', () => tplPred(F[i], bestTau)));
      add('b-shape-knn', s.variant, s.lab, time('b-shape-knn', () => knnS.predict(F[i].sh).lab));
      add('c-hog-svm', s.variant, s.lab, time('c-hog-svm', () => svmH.predict(F[i].hg).lab));
      add('c-hog-knn', s.variant, s.lab, time('c-hog-knn', () => knnH.predict(F[i].hg).lab));
      add('ac-hog+tpl-svm', s.variant, s.lab, time('ac-hog+tpl-svm', () => svmHT.predict([...F[i].hg, ...tplClasses.map(c => F[i].tp[c])]).lab));
    }
  }
  const nTest = S.filter(s => !s.lab.startsWith('digits-')).length;
  const featMs = { 'a-template': msPer.tpl, 'b-shape-knn': msPer.shape, 'c-hog-svm': msPer.hog, 'c-hog-knn': msPer.hog, 'ac-hog+tpl-svm': msPer.hog + msPer.tpl };
  const out = { n: S.length, ms_per_patch: {}, results };
  for (const ap of Object.keys(results)) out.ms_per_patch[ap] = +(featMs[ap] + predMs[ap] / nTest).toFixed(3);
  fs.writeFileSync(path.join(__dirname, '../data/exp.json'), JSON.stringify(out, null, 1));
  // table: per class P/R on scan, and family macro F1 per variant
  const fam = (c) => c.startsWith('rest') ? 'rests' : c.startsWith('acc') ? 'accidentals' : c.startsWith('clef') ? 'clefs' : (c.startsWith('digit') || c.startsWith('time')) ? 'time' : c;
  const pr = (v) => ({ p: v.tp + v.fp ? v.tp / (v.tp + v.fp) : NaN, r: v.tp + v.fn ? v.tp / (v.tp + v.fn) : NaN });
  const f1 = (v) => { const { p, r } = pr(v); return p + r ? 2 * p * r / (p + r) : 0; };
  console.log('ms per patch (features + predict):', JSON.stringify(out.ms_per_patch));
  for (const variant of ['clean', 'scan', 'scan-severe']) {
    console.log(`\n== ${variant}: family micro P / R (pooled over the family's classes)`);
    const fams = ['rests', 'accidentals', 'clefs', 'time', 'fermata', 'dyn', 'dot', 'neg'];
    console.log('approach'.padEnd(16) + fams.map(f => f.padStart(13)).join(''));
    for (const ap of Object.keys(results)) {
      const V = results[ap][variant] || {};
      const cells = fams.map(f => { const a = { tp: 0, fp: 0, fn: 0 }; for (const [c, v] of Object.entries(V)) if (fam(c) === f) { a.tp += v.tp; a.fp += v.fp; a.fn += v.fn; } const { p, r } = pr(a); return `${(p * 100).toFixed(0)}/${(r * 100).toFixed(0)}`.padStart(13); });
      console.log(ap.padEnd(16) + cells.join(''));
    }
  }
})();
