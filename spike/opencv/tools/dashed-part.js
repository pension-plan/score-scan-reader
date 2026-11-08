// Fallback for pages whose staff lines survive only as dashes (thin photocopies of halftoned or
// low-resolution pages): no strip ever shows five clean peaks, and the staff space estimate is
// wrong. Here the staff space comes from the autocorrelation of the thin-line profile, and a staff
// is found where five profile peaks at that spacing line up (four of five suffice), strip by strip
// on wide strips; the strips are tracked across the page and the lines fitted through them. Used by
// front.js only when the normal finder found no staff. Returns { staves, ss }.
function detectDashedStaves(bin, lt, opts = {}) {
  const { width: w, height: h } = bin;
  const line = thinLineMask(bin, Math.max(2, Math.round(lt * 2 + 1.5)), 3);
  const nS = opts.strips || 10, sw = Math.ceil(w / nS);
  const prof = [];
  for (let s = 0; s < nS; s++) {
    const x0 = s * sw, x1 = Math.min(w, x0 + sw), p = new Float64Array(h);
    for (let y = 0; y < h; y++) { let c = 0; const r = y * w; for (let x = x0; x < x1; x++) c += line[r + x]; p[y] = c; }
    prof.push({ x0, x1, xc: (x0 + x1 - 1) / 2, p });
  }
  // staff space: the lag (5..40 px) where the strips' profiles best match themselves shifted, with
  // twice the lag also matching (a staff has four equal gaps; text rows do not repeat that way)
  const ac = (lag) => { let a = 0; for (const { p } of prof) for (let y = 0; y + lag < h; y++) a += p[y] * p[y + lag]; return a; };
  let best = 0, ss = 0;
  const A = []; for (let lag = 0; lag <= 82; lag++) A.push(lag < 4 ? 0 : ac(lag));
  for (let lag = 5; lag <= 40; lag++) { const sc = A[lag] + A[2 * lag]; if (A[lag] >= A[lag - 1] && A[lag] >= A[lag + 1] && sc > best) { best = sc; ss = lag; } }
  if (!ss) return { staves: [], ss: 0 };
  // sub-pixel: parabola through the peak
  const d = A[ss - 1] - 2 * A[ss] + A[ss + 1]; if (d < 0) ss += 0.5 * (A[ss - 1] - A[ss + 1]) / d;
  // per strip: rows where four of five lines at that spacing carry line ink
  const pk = (p, y) => { let m = 0; for (let dy = -1; dy <= 1; dy++) { const yy = Math.round(y + dy); if (yy >= 0 && yy < h && p[yy] > m) m = p[yy]; } return m; };
  const cands = prof.map(({ p, x0, x1 }) => {
    const thr = (opts.minCover ?? 0.06) * (x1 - x0), out = [], sc = new Float64Array(h);
    for (let y = 0; y + 4 * ss < h; y++) {
      const v = [0, 1, 2, 3, 4].map(k => pk(p, y + k * ss)).sort((a, b) => a - b);
      // between-line rows must be lighter than the lines (a block of text or a beam is dense throughout)
      let mid = 0; for (let k = 0; k < 4; k++) mid += p[Math.round(y + (k + 0.5) * ss)];
      sc[y] = v[1] >= thr ? v[1] + v[2] + v[3] + v[4] - 1.5 * mid / 4 * 4 : 0;
    }
    for (let y = 1; y + 4 * ss < h - 1; y++) {
      if (sc[y] <= 0 || sc[y] < sc[y - 1] || sc[y] < sc[y + 1]) continue;
      let peak = true; for (let dy = -Math.round(0.6 * ss); dy <= Math.round(0.6 * ss); dy++) if (sc[y + dy] > sc[y]) { peak = false; break; }
      if (peak && !out.some(o => Math.abs(o.y - y) < 2 * ss)) out.push({ y, sc: sc[y] });
    }
    return out;
  });
  // track the candidate tops across strips
  const tracks = [];
  for (let s = 0; s < nS; s++) for (const c of cands[s]) {
    let bt = null, bd = 0.6 * ss;
    for (const t of tracks) { const l = t[t.length - 1]; if (s - l.s > 3 || s === l.s) continue; const dd = Math.abs(l.y - c.y); if (dd < bd) { bd = dd; bt = t; } }
    if (bt) bt.push({ s, y: c.y }); else tracks.push([{ s, y: c.y }]);
  }
  const staves = [];
  for (const t of tracks.filter(t => t.length >= Math.max(3, Math.round(0.3 * nS)))) {
    const xs = t.map(it => prof[it.s].xc);
    // each line refined to the centroid of its line ink in the strip (+-2 px)
    const ys = [0, 1, 2, 3, 4].map(k => t.map(it => {
      const { p } = prof[it.s], y0 = it.y + k * ss; let sw0 = 0, swy = 0;
      for (let y = Math.round(y0 - 2); y <= Math.round(y0 + 2); y++) if (y >= 0 && y < h) { sw0 += p[y]; swy += p[y] * y; }
      return sw0 > 0 ? swy / sw0 : y0;
    }));
    // equal spacing per strip (least squares through the five)
    for (let j = 0; j < t.length; j++) { let my = 0; for (let k = 0; k < 5; k++) my += ys[k][j]; my /= 5; let num = 0; for (let k = 0; k < 5; k++) num += (k - 2) * (ys[k][j] - my); const g = num / 10; for (let k = 0; k < 5; k++) ys[k][j] = my + (k - 2) * g; }
    const dense = [0, 1, 2, 3, 4].map(k => densify(xs, ys[k], w));
    const staff = { xs, ys, dense, yAt(k, x) { const xi = Math.max(0, Math.min(w - 1, Math.round(x))); return this.dense[k][xi]; }, spaceAt(x) { return (this.yAt(4, x) - this.yAt(0, x)) / 4; } };
    // extents: from the first to the last tracked strip, trimmed to where a window of one space
    // still has ink on three of the five lines
    const inked = (x) => { let n = 0; for (let k = 0; k < 5; k++) { let any = 0; for (let xx = x; xx < Math.min(w, x + Math.round(ss)); xx++) { const y = Math.round(staff.yAt(k, xx)); if (y >= 0 && y < h && line[y * w + xx]) { any = 1; break; } } n += any; } return n >= 3; };
    let left = prof[t[0].s].x0, right = prof[t[t.length - 1].s].x1 - 1;
    while (left < right && !inked(left)) left += 2;
    while (right > left && !inked(Math.max(0, right - Math.round(ss)))) right -= 2;
    // and outwards past the tracked strips, along the staff's own slope, while the dashes go on
    // (gaps of up to three spaces are bridged)
    const slope = xs.length > 1 ? (ys[2][xs.length - 1] - ys[2][0]) / (xs[xs.length - 1] - xs[0]) : 0;
    const ext = (x0, dir) => {
      let x = x0, end = x0, gap = 0; const step = Math.max(2, Math.round(ss));
      const at = (k, xx) => staff.yAt(k, x0) + slope * (xx - x0);
      const ink = (xx) => { let n = 0; for (let k = 0; k < 5; k++) { let any = 0; for (let q = 0; q < step; q++) { const xq = xx + q, y = Math.round(at(k, xq)); if (xq >= 0 && xq < w && y >= 0 && y < h && line[y * w + xq]) { any = 1; break; } } n += any; } return n >= 3; };
      for (x = x0 + dir * step; x >= 0 && x + step < w; x += dir * step) { if (ink(x)) { end = dir < 0 ? x : x + step - 1; gap = 0; } else if (++gap > 3) break; }
      return { end, at };
    };
    const L = ext(left, -1), Rr = ext(right, 1);
    if (L.end < left || Rr.end > right) {
      const nx = [], ny = [[], [], [], [], []];
      if (L.end < left) { nx.push(L.end); for (let k = 0; k < 5; k++) ny[k].push(L.at(k, L.end)); }
      xs.forEach((x, j) => { nx.push(x); for (let k = 0; k < 5; k++) ny[k].push(ys[k][j]); });
      if (Rr.end > right) { nx.push(Rr.end); for (let k = 0; k < 5; k++) ny[k].push(Rr.at(k, Rr.end)); }
      staff.xs = nx; staff.ys = ny; staff.dense = [0, 1, 2, 3, 4].map(k => densify(nx, ny[k], w));
      left = Math.min(left, L.end); right = Math.max(right, Rr.end);
    }
    if (right - left < 8 * ss) continue;
    Object.assign(staff, { left, right, space: (staff.yAt(4, (left + right) / 2) - staff.yAt(0, (left + right) / 2)) / 4, dashed: true });
    staves.push(staff);
  }
  staves.sort((a, b) => a.yAt(2, w / 2) - b.yAt(2, w / 2));
  // staves share the page's margins: a staff that stops short of the outermost end is extended to it
  // when at least a third of the one-space windows on the way still show its dashes
  if (staves.length > 1) {
    const R = Math.max(...staves.map(s => s.right)), Lm = Math.min(...staves.map(s => s.left)), step = Math.max(2, Math.round(ss));
    for (const st of staves) {
      const sl = (st.yAt(2, st.right) - st.yAt(2, st.left)) / Math.max(1, st.right - st.left);
      const share = (xa, xb, x0) => { let n = 0, m = 0; for (let x = xa; x + step <= xb; x += step) { m++; let lines = 0; for (let k = 0; k < 5; k++) { let any = 0; for (let q = 0; q < step; q++) { const y = Math.round(st.yAt(k, x0) + sl * (x + q - x0)); if (y >= 0 && y < h && line[y * w + x + q]) { any = 1; break; } } lines += any; } if (lines >= 3) n++; } return m ? n / m : 0; };
      const nx = st.xs.slice(), ny = st.ys.map(a => a.slice());
      let changed = false;
      if (R - st.right > 2 * ss && share(st.right, R, st.right) >= 0.33) { nx.push(R); for (let k = 0; k < 5; k++) ny[k].push(st.yAt(k, st.right) + sl * (R - st.right)); st.right = R; changed = true; }
      if (st.left - Lm > 2 * ss && share(Lm, st.left, st.left) >= 0.33) { nx.unshift(Lm); for (let k = 0; k < 5; k++) ny[k].unshift(st.yAt(k, st.left) - sl * (st.left - Lm)); st.left = Lm; changed = true; }
      if (changed) { st.xs = nx; st.ys = ny; st.dense = [0, 1, 2, 3, 4].map(k => densify(nx, ny[k], w)); }
    }
  }
  // two staves never overlap
  const out = [];
  for (const st of staves) { const p = out[out.length - 1]; if (p && st.yAt(0, w / 2) - p.yAt(4, w / 2) < 0.5 * ss) { if (st.right - st.left > p.right - p.left) out[out.length - 1] = st; } else out.push(st); }
  out.forEach((s, i) => { s.index = i; });
  return { staves: out, ss };
}

