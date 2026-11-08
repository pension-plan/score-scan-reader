'use strict';
// Staff detection by strip-wise projection + 5-line pattern search + tracking
// across strips.  Tolerates residual skew and page curvature (each line is a
// polyline sampled at strip centres).  Also groups staves into systems.

function verticalThinMask(bin, maxThick) {
  const { width: w, height: h, data } = bin;
  const thin = new Uint8Array(w * h);
  for (let x = 0; x < w; x++) {
    let y = 0;
    while (y < h) {
      if (!data[y * w + x]) { y++; continue; }
      let y1 = y; while (y1 < h && data[y1 * w + x]) y1++;
      if (y1 - y <= maxThick) for (let k = y; k < y1; k++) thin[k * w + x] = 1;
      y = y1;
    }
  }
  return thin;
}

function thinLineMask(bin, maxThick, minRun, maxGapRun = 0, thinPre = null, skipRow = null) {
  const { width: w, height: h } = bin;
  const thin = thinPre || verticalThinMask(bin, maxThick);
  if (minRun > 1) {
    // keep only pixels in horizontal runs >= minRun; +-1 row jitter allowed and
    // gaps up to maxGapRun bridged (broken / dotted lines of faded copies)
    const keep = new Uint8Array(w * h);
    const band = new Uint8Array(w);
    for (let y = 0; y < h; y++) {
      if (skipRow && skipRow[y]) continue;
      const r0 = y * w;
      for (let x = 0; x < w; x++) band[x] = thin[r0 + x] | (y > 0 ? thin[r0 - w + x] : 0) | (y < h - 1 ? thin[r0 + w + x] : 0);
      let x = 0;
      while (x < w) {
        if (!thin[r0 + x]) { x++; continue; }
        let x1 = x, last = x, gap = 0;
        while (x1 < w) { if (band[x1]) { last = x1; gap = 0; } else if (++gap > maxGapRun) break; x1++; }
        if (last - x + 1 >= minRun) for (let k = x; k <= last; k++) if (thin[r0 + k]) keep[r0 + k] = 1;
        x = last + 1;
      }
    }
    return keep;
  }
  return thin;
}

function findPeaks(proj, thr, maxWidth) {
  const peaks = [];
  const n = proj.length;
  for (let y = 0; y < n; y++) {
    if (proj[y] < thr) continue;
    let y1 = y, s = 0, sy = 0, mx = 0;
    while (y1 < n && proj[y1] >= thr) { s += proj[y1]; sy += proj[y1] * y1; if (proj[y1] > mx) mx = proj[y1]; y1++; }
    if (y1 - y <= maxWidth) peaks.push({ y: sy / s, strength: mx, width: y1 - y });
    y = y1;
  }
  return peaks;
}

function fivePatterns(peaks, ss, allow4 = true) {
  const out = [];
  const used = new Uint8Array(peaks.length);
  for (let i = 0; i < peaks.length; i++) {
    if (used[i]) continue;
    const seq = [i];
    let last = i, gap = ss;
    for (let k = 1; k < 5; k++) {
      let best = -1, bd = 1e9;
      for (let j = last + 1; j < peaks.length; j++) {
        const d = peaks[j].y - peaks[last].y;
        if (d > 1.4 * ss) break;
        if (d < 0.7 * ss) continue;
        const err = Math.abs(d - gap);
        if (err < bd) { bd = err; best = j; }
      }
      if (best < 0 || bd > 0.25 * ss) break;
      if (k === 1) gap = peaks[best].y - peaks[last].y;
      seq.push(best); last = best;
    }
    if (seq.length === 5) {
      const ys = seq.map(j => peaks[j].y);
      const gaps = ys.slice(1).map((y, k) => y - ys[k]);
      const mg = (ys[4] - ys[0]) / 4;
      if (Math.max(...gaps) - Math.min(...gaps) <= 0.3 * mg) {
        out.push({ ys, space: mg });
        seq.forEach(j => { used[j] = 1; });
        continue;
      }
    }
  }
  // phase 2, on peaks not explained by complete staves: 4-of-5 with one inner
  // line missing (faded copies lose single lines; inner -> unambiguous)
  for (let i = 0; allow4 && i < peaks.length; i++) {
    if (used[i]) continue;
    const m4 = fourOfFive(peaks, i, ss, used);
    if (m4) { out.push(m4.cand); m4.idx.forEach(j => { used[j] = 1; }); }
  }
  out.sort((a, b) => a.ys[0] - b.ys[0]);
  return out;
}

function fourOfFive(peaks, i, ss, used) {
  const y0 = peaks[i].y;
  for (const g of [ss, 0.95 * ss, 1.05 * ss, 0.9 * ss, 1.1 * ss]) {
    const idx = [i], ys = [y0];
    let missing = -1;
    for (let k = 1; k <= 4; k++) {
      const target = y0 + k * g;
      let best = -1, bd = 0.18 * ss;
      for (let j = i + 1; j < peaks.length; j++) {
        if (used[j]) continue;
        const d = Math.abs(peaks[j].y - target);
        if (d < bd) { bd = d; best = j; }
        if (peaks[j].y > target + ss) break;
      }
      if (best >= 0) { idx.push(best); ys.push(peaks[best].y); }
      else if (missing < 0 && k < 4) { missing = k; ys.push(NaN); }
      else { missing = -2; break; }
    }
    if (missing > 0 && idx.length === 4) {
      ys[missing] = (ys[missing - 1] + ys[missing + 1]) / 2;
      return { cand: { ys, space: (ys[4] - ys[0]) / 4, inferred: missing }, idx };
    }
  }
  return null;
}

// Cascade: strict parameters first; if that finds nothing, relax (broken lines,
// thin faded copies, heavy noise).
function detectStaves(bin, ss, lt, opts = {}) {
  const passes = opts.passes || [
    { gap: 0, peak: 0.25 },
    { gap: Math.max(1, Math.round(0.4 * ss)), peak: 0.15 },
    { gap: Math.max(2, Math.round(0.8 * ss)), peak: 0.10 },
  ];
  // strict pass first; relaxed passes only add staves that do not overlap
  let res = [];
  const w = bin.width, h = bin.height;
  const maxThick = Math.max(2, Math.round(lt * 2 + 1.5));
  const thin = verticalThinMask(bin, maxThick);
  const skipRow = new Uint8Array(h);
  passes.forEach((ps, k) => {
    // rows already explained by found staves are skipped in relaxed passes
    for (const r of res) {
      const y0 = Math.max(0, Math.floor(Math.min(r.yAt(0, 0), r.yAt(0, w - 1)) - 1.5 * ss));
      const y1 = Math.min(h - 1, Math.ceil(Math.max(r.yAt(4, 0), r.yAt(4, w - 1)) + 1.5 * ss));
      for (let y = y0; y <= y1; y++) skipRow[y] = 1;
    }
    const found = detectStavesPass(bin, ss, lt, { ...opts, ...ps, thin, skipRow: k ? skipRow : null });
    for (const st of found) {
      const y = st.yAt(2, w / 2);
      if (!res.some(r => Math.abs(r.yAt(2, w / 2) - y) < 3 * ss)) { st.pass = k; res.push(st); }
    }
  });
  res.sort((a, b) => a.yAt(2, w / 2) - b.yAt(2, w / 2));
  res.forEach((s, i) => { s.index = i; });
  return res;
}

function detectStavesPass(bin, ss, lt, opts = {}) {
  const { width: w, height: h, data } = bin;
  const maxThick = Math.max(2, Math.round(lt * 2 + 1.5));
  const line = thinLineMask(bin, maxThick, Math.max(3, Math.round(ss * 0.8)), opts.gap || 0, opts.thin, opts.skipRow);
  const stripW = Math.max(16, Math.round(opts.stripFactor ? opts.stripFactor * ss : 6 * ss));
  const nStrips = Math.ceil(w / stripW);
  const strips = [];
  const proj = new Float64Array(h);
  for (let s = 0; s < nStrips; s++) {
    const x0 = s * stripW, x1 = Math.min(w, x0 + stripW);
    proj.fill(0);
    for (let y = 0; y < h; y++) { let c = 0; const r = y * w; for (let x = x0; x < x1; x++) c += line[r + x]; proj[y] = c; }
    const peaks = findPeaks(proj, (opts.peak ?? 0.25) * (x1 - x0), Math.max(3, Math.round(3 * lt + 2)));
    strips.push({ x0, x1, xc: (x0 + x1 - 1) / 2, cands: fivePatterns(peaks, ss, !opts.gap) });
  }
  // tracking
  const tracks = [];
  for (let s = 0; s < nStrips; s++) {
    for (const c of strips[s].cands) {
      let best = null, bd = 1e9;
      for (const t of tracks) {
        const last = t.items[t.items.length - 1];
        const ds = s - last.s;
        if (ds <= 0 || ds > 4) continue;
        const pred = last.c.ys[0] + t.slope * ds;
        const d = Math.abs(pred - c.ys[0]) + Math.abs((last.c.ys[4] + t.slope * ds) - c.ys[4]);
        if (d < 1.2 * ss && d < bd) { bd = d; best = t; }
      }
      if (best) {
        const last = best.items[best.items.length - 1];
        const sl = (c.ys[0] - last.c.ys[0]) / (s - last.s);
        best.slope = best.items.length > 1 ? 0.7 * best.slope + 0.3 * sl : sl;
        best.items.push({ s, c });
      } else tracks.push({ items: [{ s, c }], slope: 0 });
    }
  }
  const minStrips = Math.max(3, Math.round(0.12 * nStrips));
  let good = tracks.filter(t => t.items.length >= minStrips);
  // merge tracks that are the same staff split by a gap
  good.sort((a, b) => a.items[0].s - b.items[0].s);
  const merged = [];
  for (const t of good) {
    const m = merged.find(o => {
      const a = o.items[o.items.length - 1], b = t.items[0];
      return b.s > a.s && Math.abs(a.c.ys[2] - b.c.ys[2]) < 1.5 * ss + Math.abs(o.slope) * (b.s - a.s);
    });
    if (m) m.items.push(...t.items); else merged.push(t);
  }
  const staves = merged.map(t => buildStaff(t, strips, line, bin, w, h, ss, lt)).filter(Boolean);
  staves.sort((a, b) => a.yAt(2, w / 2) - b.yAt(2, w / 2));
  // drop overlapping duplicates
  const out = [];
  for (const st of staves) {
    const prev = out[out.length - 1];
    if (prev && Math.abs(prev.yAt(2, w / 2) - st.yAt(2, w / 2)) < 2 * ss) {
      if (st.right - st.left > prev.right - prev.left) out[out.length - 1] = st;
    } else out.push(st);
  }
  out.forEach((s, i) => { s.index = i; });
  return out;
}

function buildStaff(t, strips, line, bin, w, h, ss, lt) {
  const items = t.items.slice().sort((a, b) => a.s - b.s);
  const xs = items.map(it => strips[it.s].xc);
  const ys = [0, 1, 2, 3, 4].map(k => items.map(it => it.c.ys[k]));
  // refine each line y per strip: centroid of line-mask pixels near prediction
  const rad = Math.max(1.5, lt + 1);
  for (let k = 0; k < 5; k++) {
    for (let j = 0; j < items.length; j++) {
      const st = strips[items[j].s];
      const y0 = Math.max(0, Math.floor(ys[k][j] - rad)), y1 = Math.min(h - 1, Math.ceil(ys[k][j] + rad));
      let s = 0, sy = 0;
      for (let y = y0; y <= y1; y++) { let c = 0; for (let x = st.x0; x < st.x1; x++) c += line[y * w + x]; s += c; sy += c * y; }
      if (s > 0.2 * (st.x1 - st.x0)) ys[k][j] = sy / s;
    }
  }
  const dense = [0, 1, 2, 3, 4].map(k => densify(xs, ys[k], w));
  const staff = {
    xs, ys, dense,
    yAt(k, x) { const xi = Math.max(0, Math.min(w - 1, Math.round(x))); return this.dense[k][xi]; },
    spaceAt(x) { return (this.yAt(4, x) - this.yAt(0, x)) / 4; },
  };
  // extents: walk left/right from the tracked range while >= 4 lines have ink
  // 1 = staff lines present, 0 = absent, 2 = vertical structure (barline /
  // bracket / stem: ink between the lines too) -> neither extends nor stops
  const present = (x) => {
    let n = 0;
    for (let k = 0; k < 5; k++) {
      const y = staff.yAt(k, x);
      const ya = Math.max(0, Math.floor(y - lt / 2 - 1)), yb = Math.min(h - 1, Math.ceil(y + lt / 2 + 1));
      for (let yy = ya; yy <= yb; yy++) if (bin.data[yy * w + x]) { n++; break; }
    }
    if (n < 4) return 0;
    let m = 0;
    for (let k = 0; k < 4; k++) {
      const y = Math.round((staff.yAt(k, x) + staff.yAt(k + 1, x)) / 2);
      if (y >= 0 && y < h && bin.data[y * w + x]) m++;
    }
    return m >= 3 ? 2 : 1;
  };
  const maxGap = Math.max(3, Math.round(1.0 * ss));
  // the first/last tracked strip centre may lie just outside the staff
  // (strip only partly covered) -> snap inwards to the first column with lines
  let left = Math.round(xs[0]), gap = 0, x;
  while (left < Math.round(xs[xs.length - 1]) && present(left) !== 1) left++;
  x = left;
  for (; x >= 0; x--) { const v = present(x); if (v === 1) { left = x; gap = 0; } else if (v === 0 && ++gap > maxGap) break; }
  let right = Math.round(xs[xs.length - 1]); gap = 0;
  while (right > left && present(right) !== 1) right--;
  for (x = right; x < w; x++) { const v = present(x); if (v === 1) { right = x; gap = 0; } else if (v === 0 && ++gap > maxGap) break; }
  // a terminating barline at the right end belongs to the staff
  for (x = right + 1; x < Math.min(w, right + Math.round(1.2 * ss)); x++) if (present(x) === 2) right = x;
  staff.left = left; staff.right = right;
  staff.space = (staff.yAt(4, (left + right) / 2) - staff.yAt(0, (left + right) / 2)) / 4;
  if (right - left < 8 * ss) return null;
  return staff;
}

function densify(xs, ys, w) {
  const out = new Float32Array(w);
  let j = 0;
  for (let x = 0; x < w; x++) {
    if (xs.length === 1 || x <= xs[0]) {
      // extrapolate with first segment slope (clamped)
      const sl = xs.length > 1 ? (ys[1] - ys[0]) / (xs[1] - xs[0]) : 0;
      out[x] = ys[0] + sl * (x - xs[0]);
      continue;
    }
    if (x >= xs[xs.length - 1]) {
      const n = xs.length;
      const sl = (ys[n - 1] - ys[n - 2]) / (xs[n - 1] - xs[n - 2]);
      out[x] = ys[n - 1] + sl * (x - xs[n - 1]);
      continue;
    }
    while (xs[j + 1] < x) j++;
    const t = (x - xs[j]) / (xs[j + 1] - xs[j]);
    out[x] = ys[j] * (1 - t) + ys[j + 1] * t;
  }
  return out;
}

// Group consecutive staves into systems: connected when a vertical ink column
// near the left edge joins the bottom line of one staff to the top of the next.
function groupSystems(bin, staves, ss) {
  const { width: w, data } = bin;
  const sys = [];
  let cur = staves.length ? [0] : [];
  for (let k = 1; k < staves.length; k++) {
    const A = staves[k - 1], B = staves[k];
    const L = Math.min(A.left, B.left), L2 = Math.max(A.left, B.left);
    let linked = false;
    for (let x = Math.max(0, Math.round(L - 2.5 * ss)); x <= Math.min(w - 1, Math.round(L2 + 1.0 * ss)) && !linked; x++) {
      const y0 = Math.round(A.yAt(4, x)), y1 = Math.round(B.yAt(0, x));
      if (y1 - y0 > 30 * ss) break;
      // tolerant column: ink within +-r px on each row (perspective / residual tilt)
      const r = Math.max(1, Math.round(0.15 * ss));
      let n = 0;
      for (let y = y0; y <= y1; y++) {
        for (let xx = Math.max(0, x - r); xx <= Math.min(w - 1, x + r); xx++) if (data[y * w + xx]) { n++; break; }
      }
      if (n >= 0.92 * (y1 - y0 + 1)) {
        // must be a thin line (bracket / system barline), not a dark blob:
        // paper within 1.5 ss on at least one side at mid-gap height
        const ym = Math.round((y0 + y1) / 2), r = Math.round(1.5 * ss);
        let white = 0;
        for (let xx = Math.max(0, x - r); xx <= Math.min(w - 1, x + r); xx++) if (!data[ym * w + xx]) white++;
        if (white >= r) linked = true;
      }
    }
    if (linked) cur.push(k); else { sys.push(cur); cur = [k]; }
  }
  if (cur.length) sys.push(cur);
  sys.forEach((g, i) => g.forEach(k => { staves[k].system = i; }));
  return sys;
}

module.exports = { detectStaves, groupSystems, thinLineMask };
