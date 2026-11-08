// Tiny JS classifiers (cv.ml is disabled in the opencv.js build): standardised kNN and one-vs-rest
// linear SVM (Pegasos SGD, hinge loss).
'use strict';
function standardiser(X) {
  const d = X[0].length, mu = new Float64Array(d), sd = new Float64Array(d);
  for (const x of X) for (let j = 0; j < d; j++) mu[j] += x[j] / X.length;
  for (const x of X) for (let j = 0; j < d; j++) sd[j] += (x[j] - mu[j]) ** 2 / X.length;
  for (let j = 0; j < d; j++) sd[j] = Math.sqrt(sd[j]) || 1;
  return { mu: Array.from(mu), sd: Array.from(sd), f: (x) => x.map((v, j) => (v - mu[j]) / sd[j]) };
}

function trainKnn(X, y, k = 3) {
  const st = standardiser(X), Z = X.map(st.f);
  return {
    k, st, Z, y,
    predict(x) {
      const z = st.f(x), best = [];
      for (let i = 0; i < Z.length; i++) {
        let d = 0; const zi = Z[i]; for (let j = 0; j < z.length; j++) { const t = z[j] - zi[j]; d += t * t; }
        if (best.length < k) { best.push([d, i]); best.sort((a, b) => a[0] - b[0]); }
        else if (d < best[k - 1][0]) { best[k - 1] = [d, i]; best.sort((a, b) => a[0] - b[0]); }
      }
      const votes = {}; for (const [d, i] of best) votes[y[i]] = (votes[y[i]] || 0) + 1 / (1e-6 + Math.sqrt(d));
      let lab = null, v = -1, tot = 0; for (const [l, s] of Object.entries(votes)) { tot += s; if (s > v) { v = s; lab = l; } }
      return { lab, conf: v / tot, dist: Math.sqrt(best[0][0]) };
    },
  };
}

function trainSvm(X, y, { lambda = 1e-4, epochs = 25, seed = 1 } = {}) {
  const st = standardiser(X), Z = X.map(st.f), classes = [...new Set(y)].sort(), d = Z[0].length + 1;
  let r = seed; const rnd = () => ((r = Math.imul(r ^ (r >>> 15), 2246822519) + 1 >>> 0) / 4294967296);
  const W = {};
  // class weights: rare classes count more (balanced hinge)
  const cnt = {}; for (const l of y) cnt[l] = (cnt[l] || 0) + 1;
  for (const c of classes) {
    const w = new Float64Array(d); let t = 0;
    const pw = Math.min(20, (y.length - cnt[c]) / cnt[c]);
    for (let e = 0; e < epochs; e++) for (let n = 0; n < Z.length; n++) {
      const i = (rnd() * Z.length) | 0, yi = y[i] === c ? 1 : -1, z = Z[i];
      t++; const eta = 1 / (lambda * (t + 100));
      let s = w[d - 1]; for (let j = 0; j < d - 1; j++) s += w[j] * z[j];
      for (let j = 0; j < d - 1; j++) w[j] *= (1 - eta * lambda);
      if (yi * s < 1) { const g = eta * yi * (yi > 0 ? Math.sqrt(pw) : 1); for (let j = 0; j < d - 1; j++) w[j] += g * z[j]; w[d - 1] += g; }
    }
    W[c] = Array.from(w);
  }
  return {
    st, W, classes,
    predict(x) {
      const z = st.f(x); let lab = null, best = -Infinity, second = -Infinity;
      for (const c of classes) { const w = W[c]; let s = w[w.length - 1]; for (let j = 0; j < z.length; j++) s += w[j] * z[j]; if (s > best) { second = best; best = s; lab = c; } else if (s > second) second = s; }
      return { lab, conf: best - second, score: best };
    },
  };
}
module.exports = { trainKnn, trainSvm, standardiser };
