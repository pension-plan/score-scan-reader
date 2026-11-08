'use strict';
// Staff detection by strip-wise projection + 5-line pattern search + tracking
// across strips.  Tolerates residual skew and page curvature (each line is a
// polyline sampled at strip centres).  Also groups staves into systems.

function thinLineMask(bin, maxThick, minRun) {
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
  if (minRun > 1) {
    // keep only pixels in horizontal runs (allowing +-1 row jitter via OR of neighbours) >= minRun
    const keep = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) {
      let x = 0;
      const r0 = y * w;
      while (x < w) {
        const on = (xx) => thin[r0 + xx] || (y > 0 && thin[r0 - w + xx]) || (y < h - 1 && thin[r0 + w + xx]);
        if (!thin[r0 + x]) { x++; continue; }
        let x1 = x; while (x1 < w && on(x1)) x1++;
        if (x1 - x >= minRun) for (let k = x; k < x1; k++) if (thin[r0 + k]) keep[r0 + k] = 1;
        x = x1 + 1;
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

function fivePatterns(peaks, ss) {
  const out = [];
  const used = new Uint8Array(peaks.length);
  for (let i = 0; i < peaks.length; i++) {
    if (used[i]) continue;
    let seq = [i];
    let last = i, gap = ss;
    // follow the chain past five lines: ledger lines above / below a staff
    // continue its spacing, and the five strongest consecutive peaks (full
    // staff lines, not the short ledgers) are the staff
    for (let k = 1; k < 9; k++) {
      let best = -1, bd = 1e9;
      for (let j = last + 1; j < peaks.length; j++) {
        const d = peaks[j].y - peaks[last].y;
        if (d > 1.4 * ss) break;
        if (d < 0.7 * ss) continue;
        const err = Math.abs(d - gap);
        if (err < bd) { bd = err; best = j; }
      }
      if (best < 0 || bd > 0.35 * ss) break;
      if (k === 1) gap = peaks[best].y - peaks[last].y;
      seq.push(best); last = best;
    }
    if (seq.length > 5) {
      // the window whose weakest line is clearly the strongest (a ledger is
      // the weakest "line" of a window that includes it)
      const minOf = (a) => Math.min(...seq.slice(a, a + 5).map(j => peaks[j].strength));
      let ba = 0, bm = minOf(0);
      for (let a = 1; a + 5 <= seq.length; a++) { const m = minOf(a); if (m > 1.25 * bm) { bm = m; ba = a; } }
      seq = seq.slice(ba, ba + 5);
    }
    if (seq.length === 5) {
      const ys = seq.map(j => peaks[j].y);
      const gaps = ys.slice(1).map((y, k) => y - ys[k]);
      const mg = (ys[4] - ys[0]) / 4;
      // two chains can settle on the same five lines: keep one
      if (Math.max(...gaps) - Math.min(...gaps) <= 0.4 * mg && !out.some(o => Math.abs(o.ys[0] - ys[0]) < 0.3 * ss && Math.abs(o.ys[4] - ys[4]) < 0.3 * ss)) {
        out.push({ ys, space: mg });
        seq.forEach(j => { used[j] = 1; });
      }
    }
  }
  return out;
}

function detectStaves(bin, ss, lt, opts = {}) {
  const { width: w, height: h, data } = bin;
  const maxThick = Math.max(2, Math.round(lt * 2 + 1.5));
  const line = thinLineMask(bin, maxThick, Math.max(3, Math.round(ss * 0.8)));
  const stripW = Math.max(16, Math.round(opts.stripFactor ? opts.stripFactor * ss : 6 * ss));
  const nStrips = Math.ceil(w / stripW);
  const strips = [];
  const proj = new Float64Array(h);
  for (let s = 0; s < nStrips; s++) {
    const x0 = s * stripW, x1 = Math.min(w, x0 + stripW);
    proj.fill(0);
    for (let y = 0; y < h; y++) { let c = 0; const r = y * w; for (let x = x0; x < x1; x++) c += line[r + x]; proj[y] = c; }
    const peaks = findPeaks(proj, 0.25 * (x1 - x0), Math.max(3, Math.round(3 * lt + 2)));
    strips.push({ x0, x1, xc: (x0 + x1 - 1) / 2, cands: fivePatterns(peaks, ss) });
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
      return b.s > a.s && Math.abs(a.c.ys[2] - b.c.ys[2]) < 0.6 * ss + Math.abs(o.slope) * (b.s - a.s);
    });
    if (m) m.items.push(...t.items); else merged.push(t);
  }
  const staves = merged.map(t => buildStaff(t, strips, line, bin, w, h, ss, lt)).filter(Boolean);
  staves.sort((a, b) => a.yAt(2, w / 2) - b.yAt(2, w / 2));
  // drop overlapping / conflicting staves: two real staves never overlap
  // vertically, but ledger lines + some staff lines can form a 5-line pattern
  // a couple of spaces off a real staff.  Keep the better-supported one.
  const support = (st) => st.xs.length * 1e6 + (st.right - st.left);
  const out = [];
  for (const st of staves) {
    const prev = out[out.length - 1];
    let clash = false;
    if (prev) {
      const xa = Math.max(prev.left, st.left), xb = Math.min(prev.right, st.right);
      const xm = xb > xa ? (xa + xb) / 2 : w / 2;
      clash = st.yAt(0, xm) - prev.yAt(4, xm) < 0.5 * ss && Math.abs(prev.yAt(2, xm) - st.yAt(2, xm)) < 4.5 * ss;
    }
    if (clash) {
      if (support(st) > support(prev)) out[out.length - 1] = st;
    } else out.push(st);
  }
  out.forEach((s, i) => { s.index = i; });
  return out;
}

// Drop track items whose 5-line pattern is shifted by a line (ledger lines or
// a beam taken for a staff line): robust (Theil-Sen) fit of the middle-line y
// over x, items more than 0.4 space off the fit go.
function consistentItems(items, strips, ss) {
  if (items.length < 3) return items;
  const xs = items.map(it => strips[it.s].xc), ys = items.map(it => it.c.ys[2]);
  const sl = [];
  for (let i = 0; i < xs.length; i++) for (let j = i + 1; j < xs.length; j++) sl.push((ys[j] - ys[i]) / (xs[j] - xs[i]));
  sl.sort((a, b) => a - b);
  const m = sl[sl.length >> 1];
  const ic = ys.map((y, i) => y - m * xs[i]).sort((a, b) => a - b);
  const c = ic[ic.length >> 1];
  const keep = items.filter((it, i) => Math.abs(ys[i] - (m * xs[i] + c)) <= 0.4 * ss);
  return keep.length >= Math.max(2, items.length / 2) ? keep : items;
}

function buildStaff(t, strips, line, bin, w, h, ss, lt) {
  const items = consistentItems(t.items.slice().sort((a, b) => a.s - b.s), strips, ss);
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
  // staff lines are equally spaced: fit y_k = c + (k - 2) * g per strip, the
  // worst line left out when it is off (a beam / ledger pulled its centroid)
  for (let j = 0; j < items.length; j++) {
    const fit = (ks) => {
      const n = ks.length, mk = ks.reduce((a, k) => a + k, 0) / n, my = ks.reduce((a, k) => a + ys[k][j], 0) / n;
      let sxy = 0, sxx = 0;
      for (const k of ks) { sxy += (k - mk) * (ys[k][j] - my); sxx += (k - mk) * (k - mk); }
      const g = sxy / sxx;
      return { g, c: my + (2 - mk) * g };
    };
    let f = fit([0, 1, 2, 3, 4]);
    const res = [0, 1, 2, 3, 4].map(k => Math.abs(ys[k][j] - (f.c + (k - 2) * f.g)));
    const worst = res.indexOf(Math.max(...res));
    if (res[worst] > 0.12 * ss) f = fit([0, 1, 2, 3, 4].filter(k => k !== worst));
    for (let k = 0; k < 5; k++) ys[k][j] = f.c + (k - 2) * f.g;
  }
  const dense = [0, 1, 2, 3, 4].map(k => densify(xs, ys[k], w));
  const staff = {
    xs, ys, dense,
    yAt: staffYAt, spaceAt: staffSpaceAt,
  };
  // extents: walk left/right from the tracked range while >= 4 lines have ink.
  // The walk follows the staff with a vertical offset that is re-fitted every
  // half space (page curvature / residual skew make the linear extrapolation
  // of the end segments drift off the lines), and the followed positions are
  // added to the polyline.
  // present: 1 = staff lines present, 0 = absent, 2 = vertical structure
  // (barline / bracket / stem: ink between the lines too) -> neither extends nor stops
  const band = lt / 2 + 1;
  const hit = (x, y) => {
    const ya = Math.max(0, Math.floor(y - band)), yb = Math.min(h - 1, Math.ceil(y + band));
    for (let yy = ya; yy <= yb; yy++) if (bin.data[yy * w + x]) return 1;
    return 0;
  };
  const present = (x, off = 0) => {
    let n = 0;
    for (let k = 0; k < 5; k++) n += hit(x, staff.yAt(k, x) + off);
    if (n < 4) return 0;
    let m = 0;
    for (let k = 0; k < 4; k++) {
      const y = Math.round((staff.yAt(k, x) + staff.yAt(k + 1, x)) / 2 + off);
      if (y >= 0 && y < h && bin.data[y * w + x]) m++;
    }
    return m >= 3 ? 2 : 1;
  };
  const maxGap = Math.max(3, Math.round(1.0 * ss));
  const bs = Math.max(3, Math.round(0.5 * ss));
  const minRun = Math.max(3, Math.round(0.3 * ss));
  const walk = (x0, dir) => {
    let off = 0, gap = 0, end = x0, lastPt = x0, run = 0;
    const pts = [];
    for (let x = x0; x >= 0 && x < w; x += dir) {
      if ((x - x0) % bs === 0) {
        // re-fit the offset on the next block (ties keep the current offset)
        let bestD = off, bestS = -1;
        for (const d of [off, off - 1, off + 1]) {
          let sc = 0;
          for (let j = 0; j < bs; j++) {
            const xx = x + dir * j;
            if (xx < 0 || xx >= w) break;
            let n = 0;
            for (let k = 0; k < 5; k++) n += hit(xx, staff.yAt(k, xx) + d);
            if (n >= 4) sc += n;
          }
          if (sc > bestS) { bestS = sc; bestD = d; }
        }
        off = bestD;
      }
      // lines must run on for a few columns (letters of a staff label or a
      // dark margin can put ink on four line positions in isolated columns)
      const v = present(x, off);
      if (v === 1) {
        if (++run >= minRun) {
          end = x; gap = 0;
          if (Math.abs(x - lastPt) >= 2 * ss) { pts.push({ x, off }); lastPt = x; }
        }
      } else if (v === 0) { run = 0; if (++gap > maxGap) break; }
    }
    if (Math.abs(end - lastPt) >= 0.5 * ss) pts.push({ x: end, off });
    return { end, pts };
  };
  const wl = walk(Math.round(xs[0]), -1), wr = walk(Math.round(xs[xs.length - 1]), 1);
  let left = wl.end, right = wr.end;
  if (wl.pts.length || wr.pts.length) {
    const L = wl.pts.slice().reverse(), Rp = wr.pts;
    const nxs = [...L.map(p => p.x), ...xs, ...Rp.map(p => p.x)];
    const nys = [0, 1, 2, 3, 4].map(k => [...L.map(p => staff.yAt(k, p.x) + p.off), ...ys[k], ...Rp.map(p => staff.yAt(k, p.x) + p.off)]);
    staff.xs = nxs; staff.ys = nys;
    staff.dense = [0, 1, 2, 3, 4].map(k => densify(nxs, nys[k], w));
  }
  let x;
  // a terminating barline at the right end belongs to the staff
  for (x = right + 1; x < Math.min(w, right + Math.round(1.2 * ss)); x++) if (present(x) === 2) right = x;
  staff.left = left; staff.right = right;
  if (right - left < 8 * ss) return null;
  // re-anchor: a pattern shifted by one line (ledger lines / a beam + four
  // staff lines) passes every 4-of-5 test; the true staff has five continuous lines
  const c0 = Math.min(...lineCoverage(staff, bin, lt, 0));
  for (const sh of [-1, 1]) {
    if (Math.min(...lineCoverage(staff, bin, lt, sh)) > c0 + 0.15) { shiftStaff(staff, sh, w); break; }
  }
  staff.space = (staff.yAt(4, (left + right) / 2) - staff.yAt(0, (left + right) / 2)) / 4;
  return staff;
}

function extendStaff(o, st, w) {
  const x0 = o.xs[0], x1 = o.xs[o.xs.length - 1];
  const dl = [0, 1, 2, 3, 4].map(k => o.yAt(k, x0) - st.yAt(k, x0));
  const dr = [0, 1, 2, 3, 4].map(k => o.yAt(k, x1) - st.yAt(k, x1));
  const li = [], ri = [];
  st.xs.forEach((x, j) => { if (x < x0 - 1 && x >= st.left - 1) li.push(j); else if (x > x1 + 1 && x <= st.right + 1) ri.push(j); });
  if (st.left < o.left && st.left < x0 && !li.length) li.push(-1);
  if (st.right > o.right && st.right > x1 && !ri.length) ri.push(-2);
  if (!li.length && !ri.length) return;
  const px = (j) => j === -1 ? st.left : j === -2 ? st.right : st.xs[j];
  const py = (j, k, d) => st.yAt(k, px(j)) + d[k];
  o.xs = [...li.map(px), ...o.xs, ...ri.map(px)];
  o.ys = [0, 1, 2, 3, 4].map(k => [...li.map(j => py(j, k, dl)), ...o.ys[k], ...ri.map(j => py(j, k, dr))]);
  o.dense = [0, 1, 2, 3, 4].map(k => densify(o.xs, o.ys[k], w));
  o.left = Math.min(o.left, st.left); o.right = Math.max(o.right, st.right);
}

function shiftStaff(staff, sh, w) {
  staff.ys = staff.ys.map((_, k) => staff.ys[k].map((y, j) => y + sh * (staff.ys[4][j] - staff.ys[0][j]) / 4));
  staff.dense = [0, 1, 2, 3, 4].map(k => densify(staff.xs, staff.ys[k], w));
}

// Per-line ink coverage of a staff on `bin`: fraction of sampled columns in
// [left, right] where line k has ink within +-(lt/2+1) px; `shift` moves the
// whole staff by that many spaces.
function lineCoverage(staff, bin, lt, shift = 0) {
  const { width: w, height: h, data } = bin;
  const band = lt / 2 + 1;
  const cov = [0, 0, 0, 0, 0];
  let n = 0;
  for (let x = Math.max(0, staff.left); x <= Math.min(w - 1, staff.right); x += 2) {
    n++;
    const sp = shift ? staff.spaceAt(x) : 0;
    for (let k = 0; k < 5; k++) {
      const y = staff.yAt(k, x) + shift * sp;
      const ya = Math.max(0, Math.floor(y - band)), yb = Math.min(h - 1, Math.ceil(y + band));
      for (let yy = ya; yy <= yb; yy++) if (data[yy * w + x]) { cov[k]++; break; }
    }
  }
  return cov.map(c => c / Math.max(1, n));
}

// Union of staff sets found on different binaries (e.g. the main and a lenient
// threshold): best-supported first (extent x line coverage on `bin`), a staff
// is dropped when it overlaps an accepted one.
function mergeStaffSets(sets, bin, lt, ss) {
  const all = [];
  sets.forEach((set, si) => set.forEach(st => {
    const c = lineCoverage(st, bin, lt);
    // later sets (lenient binaries) must be clearly better to replace a staff
    st.quality = (st.right - st.left) * (Math.min(...c) + c.reduce((a, b) => a + b, 0) / 5) / 2 / (1 + 0.1 * si);
    all.push(st);
  }));
  all.sort((a, b) => b.quality - a.quality);
  const w = bin.width;
  const keep = [];
  for (const st of all) {
    let clash = null;
    for (const o of keep) {
      const xa = Math.max(o.left, st.left), xb = Math.min(o.right, st.right);
      if (xb - xa < 2 * ss) continue;
      const xm = (xa + xb) / 2;
      if (Math.abs(o.yAt(2, xm) - st.yAt(2, xm)) < 4.5 * ss) { clash = { o, xm }; break; }
    }
    if (!clash) { keep.push(st); continue; }
    // the same staff found on both binaries: the kept one inherits the
    // other's reach where it extends further (faint line ends)
    const { o, xm } = clash;
    if (Math.abs(o.yAt(0, xm) - st.yAt(0, xm)) < 0.35 * ss && Math.abs(o.yAt(4, xm) - st.yAt(4, xm)) < 0.35 * ss) extendStaff(o, st, w);
  }
  keep.sort((a, b) => a.yAt(2, (a.left + a.right) / 2) - b.yAt(2, (b.left + b.right) / 2));
  keep.forEach((s, i) => { s.index = i; });
  return keep;
}

// a staff's line k at column x (dense rows are one value per page column). Shared
// module functions, not closures: a closure would keep the finder's whole scope,
// page binaries included, alive for as long as the staff is.
function staffYAt(k, x) { const d = this.dense[k]; return d[Math.max(0, Math.min(d.length - 1, Math.round(x)))]; }
function staffSpaceAt(x) { return (this.yAt(4, x) - this.yAt(0, x)) / 4; }

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
// near the left edge joins the bottom line of one staff to the top of the next
// (+-1 px of slant tolerated).  `lenient` (optional, a lighter threshold) is
// also searched, but only right at the staff starts where the system's opening
// barline runs: faint scans break that thin line in the main binary.
function groupSystems(bin, staves, ss, lenient) {
  const { width: w } = bin;
  const linkedIn = (b, xa, xb, A, B) => {
    const d = b.data;
    for (let x = Math.max(1, Math.round(xa)); x <= Math.min(w - 2, Math.round(xb)); x++) {
      const y0 = Math.round(A.yAt(4, x)), y1 = Math.round(B.yAt(0, x));
      if (y1 - y0 > 30 * ss) return false;
      let n = 0;
      for (let y = y0; y <= y1; y++) { const i = y * w + x; if (d[i] || d[i - 1] || d[i + 1]) n++; }
      if (n >= 0.92 * (y1 - y0 + 1)) return true;
    }
    return false;
  };
  const sys = [];
  let cur = staves.length ? [0] : [];
  for (let k = 1; k < staves.length; k++) {
    const A = staves[k - 1], B = staves[k];
    const L = Math.min(A.left, B.left);
    const linked = linkedIn(bin, L - 2.5 * ss, L + 1.0 * ss, A, B) ||
      (!!lenient && linkedIn(lenient, L - 0.6 * ss, Math.max(A.left, B.left) + 0.6 * ss, A, B));
    if (linked) cur.push(k); else { sys.push(cur); cur = [k]; }
  }
  if (cur.length) sys.push(cur);
  sys.forEach((g, i) => g.forEach(k => { staves[k].system = i; }));
  return sys;
}

// Staff lines of thin photocopies survive only as rows of loose dots: no
// horizontal run is long enough for the thin-line mask.  Bridging each row's
// gaps of up to r px (a pixel is set when ink lies within r on both sides in
// its own row) joins the dots into lines; letters and heads stay thick, so
// the line search still ignores them.  Used for staff finding only.
function bridgeRows(b, r) {
  const { width: w, height: h, data } = b;
  const out = { width: w, height: h, data: new Uint8Array(w * h) };
  const left = new Int32Array(w);
  for (let y = 0; y < h; y++) {
    const row = y * w;
    let last = -1e9;
    for (let x = 0; x < w; x++) { if (data[row + x]) last = x; left[x] = last; }
    let next = 1e9;
    for (let x = w - 1; x >= 0; x--) {
      if (data[row + x]) next = x;
      if (x - left[x] <= r && next - x <= r) out.data[row + x] = 1;
    }
  }
  return out;
}

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
    // re-anchor: four of five lines also match a pattern one line off (an empty line where there
    // is none, the real outer line left out); keep the five consecutive positions with the most ink
    {
      const cover = (sh) => { let n = 0; for (let j = 0; j < t.length; j++) { const { p } = prof[t[j].s]; const g = (ys[4][j] - ys[0][j]) / 4; n += Math.min(...[0, 1, 2, 3, 4].map(k => pk(p, ys[k][j] + sh * g))); } return n; };
      let bestSh = 0, bestC = cover(0);
      for (const sh of [-1, 1]) { const cv = cover(sh); if (cv > bestC * 1.2) { bestC = cv; bestSh = sh; } }
      if (bestSh) for (let j = 0; j < t.length; j++) { const g = (ys[4][j] - ys[0][j]) / 4; for (let k = 0; k < 5; k++) ys[k][j] += bestSh * g; }
    }
    const dense = [0, 1, 2, 3, 4].map(k => densify(xs, ys[k], w));
    const staff = { xs, ys, dense, yAt: staffYAt, spaceAt: staffSpaceAt };
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

module.exports = { detectDashedStaves, detectStaves, groupSystems, thinLineMask, mergeStaffSets, lineCoverage, bridgeRows };
