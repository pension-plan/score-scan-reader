// ---------------------------------------------------------------- dewarp (phone shots, book curl)
// After the global deskew a photographed or curled page still has staves at different slopes or
// bent, barlines and stems leaning, staff ends drifting sideways: systems split and barlines go
// unfound. dewarpPage(fr) straightens the page with a mesh built from the staves themselves: every
// staff line becomes horizontal (its own detected curve, so curl is followed exactly), every staff
// gets the same space (gaps between staves rescaled by the local space), and the staff ends are
// brought to one left and one right margin (indented first systems excluded from the left one).
// The map is computed on a coarse grid and interpolated. Gated: only when the staves' slopes
// differ, the staves bend, or the staff ends lean, beyond what a flat scan shows; else null.
// y = c0 + c1 t + c2 t^2 through (x, y), t = x scaled to [-1, 1]; returns the fitted function
function quadFit(X, Y) {
  const n = X.length, x0 = X[0], x1 = X[n - 1], sc = (x) => (x1 > x0 ? (2 * (x - x0)) / (x1 - x0) - 1 : 0);
  const M = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], r = [0, 0, 0];
  for (let i = 0; i < n; i++) { const t = sc(X[i]), v = [1, t, t * t]; for (let a = 0; a < 3; a++) { r[a] += v[a] * Y[i]; for (let b = 0; b < 3; b++) M[a][b] += v[a] * v[b]; } }
  for (let c = 0; c < 3; c++) { let p = c; for (let q = c + 1; q < 3; q++) if (Math.abs(M[q][c]) > Math.abs(M[p][c])) p = q; [M[c], M[p]] = [M[p], M[c]]; [r[c], r[p]] = [r[p], r[c]];
    if (Math.abs(M[c][c]) < 1e-9) { const m = Y.reduce((a, b) => a + b, 0) / n; return () => m; }
    for (let q = 0; q < 3; q++) if (q !== c) { const f = M[q][c] / M[c][c]; for (let k = c; k < 3; k++) M[q][k] -= f * M[c][k]; r[q] -= f * r[c]; } }
  const c = r.map((v, i) => v / M[i][i]);
  return (x) => { const t = sc(x); return c[0] + c[1] * t + c[2] * t * t; };
}
const lineFit = (P) => { // x = a + b y, least squares
  const n = P.length, my = P.reduce((s, p) => s + p[1], 0) / n, mx = P.reduce((s, p) => s + p[0], 0) / n;
  let sxy = 0, syy = 0; for (const [x, y] of P) { sxy += (x - mx) * (y - my); syy += (y - my) ** 2; }
  const b = syy ? sxy / syy : 0; return { a: mx - b * my, b, at: (y) => mx - b * my + b * y };
};
function dewarpPage(fr, opts = {}) {
  const st = (fr.staves || []).filter(s => s.right - s.left > 10 * s.space);
  if (st.length < 2 || !fr.gray || !fr.gray.data) return null;
  const { width: w, height: h, data } = fr.gray;
  const STEP = 8, NX = Math.ceil(w / STEP) + 1;
  const S = st.map(s => {
    // middle line and space sampled every STEP px (extended flat beyond the staff's ends)
    // a smooth (quadratic) fit of the staff's middle line and space: curl and perspective are
    // smooth, a locally misread line end is not and must not bend the page
    const xs = [], ym = [], ys = [];
    for (let x = s.left; x <= s.right; x += STEP) { xs.push(x); ym.push(s.yAt(2, x)); ys.push((s.yAt(4, x) - s.yAt(0, x)) / 4); }
    const qm = quadFit(xs, ym), qs = quadFit(xs, ys);
    const mid = new Float64Array(NX), sp = new Float64Array(NX);
    for (let i = 0; i < NX; i++) { const x = Math.min(s.right, Math.max(s.left, i * STEP)); mid[i] = qm(x); sp[i] = qs(x); }
    const xm = (s.left + s.right) / 2, ia = Math.round(s.left / STEP), ib = Math.round(s.right / STEP), im = Math.round(xm / STEP);
    // bend: the middle line's largest departure from its chord, in spaces
    let bend = 0; for (let i = ia; i <= ib; i++) bend = Math.max(bend, Math.abs(mid[i] - (mid[ia] + (mid[ib] - mid[ia]) * (i - ia) / Math.max(1, ib - ia))));
    return { s, mid, sp, xa: s.left, xb: s.right, ym: mid[im], spm: sp[im], slope: (mid[ib] - mid[ia]) / Math.max(1, (ib - ia) * STEP), bend: bend / sp[im] };
  }).sort((a, b) => a.ym - b.ym);
  const sp0 = S.reduce((a, o) => a + o.spm, 0) / S.length;
  const slopes = S.map(o => o.slope), spread = Math.max(...slopes) - Math.min(...slopes), bend = Math.max(...S.map(o => o.bend));
  // margins: lines through the staff ends, leaving out ends far inside the others (indented first
  // systems on the left, a short last system on the right)
  const margin = (key, inside) => {
    let f = lineFit(S.map(o => [o[key], o.ym]));
    for (let it = 0; it < 2; it++) { const keep = S.filter(o => inside(o[key] - f.at(o.ym)) < 2 * sp0); if (keep.length >= 2) f = lineFit(keep.map(o => [o[key], o.ym])); }
    f.n = S.filter(o => inside(o[key] - f.at(o.ym)) < 2 * sp0).length;
    return f;
  };
  const left = margin('xa', d => d), right = margin('xb', d => -d);
  // the right margin is the reliable one (justified); lean counts only with three staves on it
  const lean = right.n >= 3 ? Math.abs(right.b) : 0;
  if (process.env.DW_DEBUG) console.error('dewarp spread', spread.toFixed(4), 'bend', bend.toFixed(2), 'lean', lean.toFixed(4));
  if (spread < (opts.minSpread ?? 0.006) && bend < (opts.minBend ?? 0.5) && lean < (opts.minLean ?? 0.015)) return null;
  // targets
  const Yt = [S[0].ym];
  for (let i = 1; i < S.length; i++) Yt.push(Yt[i - 1] + (S[i].ym - S[i - 1].ym) * sp0 / ((S[i].spm + S[i - 1].spm) / 2));
  const yRef = S[S.length >> 1].ym, XR = right.at(yRef), XL = left.at(yRef);
  // the left margin is used only when its staves sit on one line (no brace or name offsets) and it
  // leans differently from the right one
  const keptL = S.filter(o => o.xa - left.at(o.ym) < 2 * sp0);
  const keystone = left.n >= 3 && keptL.every(o => Math.abs(o.xa - left.at(o.ym)) < 0.5 * sp0) && Math.abs(left.b - right.b) > 0.01;
  const sample = (arr, x) => { const f = Math.min(NX - 1.001, Math.max(0, x / STEP)), i = Math.floor(f), t = f - i; return arr[i] * (1 - t) + arr[i + 1] * t; };
  // source y on staff i's frame for target height v at source column x
  const onStaff = (i, v, x) => sample(S[i].mid, x) + (v - Yt[i]) * sample(S[i].sp, x) / sp0;
  const map = (u, v) => {
    let k = 0; while (k < S.length - 1 && Yt[k + 1] < v) k++;
    let x = u, y = v;
    for (let it = 0; it < 2; it++) {
      // horizontal: the target's place between the margins, at the source row
      // the right margin upright; the left one too when it is clean (keystone), else a plain shear
      const R = right.at(y);
      if (keystone) { const L = left.at(y); x = L + (u - XL) * (R - L) / (XR - XL); } else x = R - (XR - u);
      if (v <= Yt[0]) y = onStaff(0, v, x);
      else if (v >= Yt[S.length - 1]) y = onStaff(S.length - 1, v, x);
      else { const t0 = (v - Yt[k]) / (Yt[k + 1] - Yt[k]), t = t0 * t0 * (3 - 2 * t0); y = (1 - t) * onStaff(k, v, x) + t * onStaff(k + 1, v, x); }
    }
    return [x, y];
  };
  const GX = Math.ceil(w / STEP) + 1, GY = Math.ceil(h / STEP) + 1, MX = new Float32Array(GX * GY), MY = new Float32Array(GX * GY);
  for (let gy = 0; gy < GY; gy++) for (let gx = 0; gx < GX; gx++) { const [x, y] = map(gx * STEP, gy * STEP); MX[gy * GX + gx] = x; MY[gy * GX + gx] = y; }
  const out = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    const fy = y / STEP, gy = Math.min(GY - 2, Math.floor(fy)), ty = fy - gy;
    for (let x = 0; x < w; x++) {
      const fx = x / STEP, gx = Math.min(GX - 2, Math.floor(fx)), tx = fx - gx, i = gy * GX + gx;
      const xs = (MX[i] * (1 - tx) + MX[i + 1] * tx) * (1 - ty) + (MX[i + GX] * (1 - tx) + MX[i + GX + 1] * tx) * ty;
      const ys = (MY[i] * (1 - tx) + MY[i + 1] * tx) * (1 - ty) + (MY[i + GX] * (1 - tx) + MY[i + GX + 1] * tx) * ty;
      const x0 = Math.floor(xs), y0 = Math.floor(ys);
      if (x0 < 0 || y0 < 0 || x0 >= w - 1 || y0 >= h - 1) { out[y * w + x] = 255; continue; }
      const ax = xs - x0, ay = ys - y0, j = y0 * w + x0;
      out[y * w + x] = Math.round((data[j] * (1 - ax) + data[j + 1] * ax) * (1 - ay) + (data[j + w] * (1 - ax) + data[j + w + 1] * ax) * ay);
    }
  }
  return { width: w, height: h, data: out, dewarped: true };
}

