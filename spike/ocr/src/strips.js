'use strict';
/**
 * Lyric-strip isolation for scanned sheet music (environment-agnostic, pure JS).
 * Input: grayscale page {width,height,data:Uint8ClampedArray}.
 * Steps: adaptive binarise -> staff line thickness/space from vertical run lengths -> skew by projection
 * variance (shear) -> staff lines from row projection -> 5-line staves -> for each inter-staff / below-staff
 * band: connected components NOT touching the staff region, text-sized, clustered by baseline into lines
 * spanning a good part of the staff width -> per line: bbox, baseline, x-height, font size, hyphen and
 * extender candidates (small horizontal bars), and a cleaned strip (only member components kept).
 */
const IMG = require('./img');

function runLengths(bin, w, h) {
  const black = new Float64Array(200), white = new Float64Array(400);
  const step = Math.max(1, Math.floor(w / 300));
  for (let x = 0; x < w; x += step) {
    let cur = bin[x], len = 0;
    for (let y = 0; y < h; y++) {
      const v = bin[y * w + x];
      if (v === cur) len++; else { if (cur) { if (len < 200) black[len]++; } else if (len < 400) white[len]++; cur = v; len = 1; }
    }
  }
  let lt = 1, ss = 10;
  for (let i = 1; i < 200; i++) if (black[i] > black[lt]) lt = i;
  // staff space: most frequent white run greater than 2*lt
  let best = 0; for (let i = Math.max(3, 2 * lt); i < 400; i++) if (white[i] > best) { best = white[i]; ss = i; }
  return { lt, ss };
}

function estimateSkew(bin, w, h, maxDeg = 1.0, stepDeg = 0.05) {
  const CH = 32; const nch = Math.ceil(w / CH);
  // per chunk row sums
  const rs = new Array(nch);
  for (let c = 0; c < nch; c++) {
    const a = new Float64Array(h); const x0 = c * CH, x1 = Math.min(w, x0 + CH);
    for (let y = 0; y < h; y++) { let s = 0; const o = y * w; for (let x = x0; x < x1; x++) s += bin[o + x]; a[y] = s; }
    rs[c] = a;
  }
  let bestA = 0, bestV = -1;
  for (let d = -maxDeg; d <= maxDeg + 1e-9; d += stepDeg) {
    const t = Math.tan(d * Math.PI / 180); const proj = new Float64Array(h);
    for (let c = 0; c < nch; c++) { const off = Math.round((c * CH + CH / 2) * t); const a = rs[c]; for (let y = 0; y < h; y++) { const yy = y - off; if (yy >= 0 && yy < h) proj[yy] += a[y]; } }
    let v = 0; for (let y = 0; y < h; y++) v += proj[y] * proj[y];
    if (v > bestV) { bestV = v; bestA = d; }
  }
  return bestA;
}

/** shear so that a line at angle deg becomes horizontal: out(x, y) = in(x, y + x*tan) */
function shear(src, w, h, deg, fill) {
  const t = Math.tan(deg * Math.PI / 180);
  const out = new (src.constructor)(w * h).fill(fill);
  for (let x = 0; x < w; x++) {
    const off = Math.round(x * t);
    for (let y = 0; y < h; y++) { const yy = y + off; if (yy >= 0 && yy < h) out[y * w + x] = src[yy * w + x]; }
  }
  return out;
}

function findStaves(bin, w, h, lt, ss) {
  const raw = new Float64Array(h);
  // count only pixels in long horizontal runs (> 2*ss) to suppress text/notes
  for (let y = 0; y < h; y++) {
    let run = 0, s = 0; const o = y * w;
    for (let x = 0; x <= w; x++) { if (x < w && bin[o + x]) run++; else { if (run > 2 * ss) s += run; run = 0; } }
    raw[y] = s;
  }
  // smooth over ~line thickness so thin/broken or slightly tilted lines are not split into several rows
  const R = Math.max(1, Math.round(lt / 2 + 1)), proj = new Float64Array(h);
  for (let y = 0; y < h; y++) { let a = 0; for (let d = -R; d <= R; d++) { const yy = y + d; if (yy >= 0 && yy < h) a += raw[yy]; } proj[y] = a; }
  const sorted = [...proj].sort((a, b) => b - a);
  const ref = sorted[Math.min(sorted.length - 1, Math.floor(h * 0.004))];   // robust max (ignores a few extreme rows)
  const thr = 0.25 * ref;
  let lines = [];
  for (let y = 0; y < h; y++) {
    if (proj[y] >= thr) { let y1 = y; let acc = 0, wsum = 0; while (y1 < h && proj[y1] >= thr) { acc += y1 * proj[y1]; wsum += proj[y1]; y1++; } lines.push({ y: acc / wsum, y0: y, y1, s: wsum }); y = y1; }
  }
  // merge candidates closer than 0.4*ss
  const merged = [];
  for (const l of lines) { const m = merged[merged.length - 1]; if (m && l.y - m.y < 0.4 * ss) { m.y = (m.y * m.s + l.y * l.s) / (m.s + l.s); m.y1 = l.y1; m.s += l.s; } else merged.push({ ...l }); }
  lines = merged;
  if (typeof process !== "undefined" && process.env && process.env.DBG_STAFF) console.log("cand", lines.map(l => Math.round(l.y) + ":" + Math.round(l.s)).join(" "), "thr", Math.round(thr));
  // group into 5-line staves; tolerate ONE missing line (faint/dropped staff lines are common in bilevel scans)
  const d = ss + lt, staves = []; const used = new Set();
  const projAt = (y) => { y = Math.round(y); let m = 0; for (let k = -R; k <= R; k++) if (y + k >= 0 && y + k < h) m = Math.max(m, proj[y + k]); return m; };
  for (let i = 0; i < lines.length; i++) {
    if (used.has(i)) continue;
    const grp = [i]; let last = i, missing = 0;
    for (let j = i + 1; j < lines.length; j++) {
      const g = lines[j].y - lines[last].y, span = lines[j].y - lines[i].y;
      if (span > 4.3 * d) break;
      if (Math.abs(g - d) <= 0.3 * d) { grp.push(j); last = j; }
      else if (!missing && Math.abs(g - 2 * d) <= 0.35 * d) { grp.push(j); last = j; missing = 1; }
      else if (g > 2.4 * d) break;
    }
    let ys = grp.map(k => lines[k].y);
    const span = ys[ys.length - 1] - ys[0];
    if (ys.length + missing < 4) continue;
    if (Math.abs(span - 4 * d) <= 0.4 * d && ys.length >= 4) { /* complete (maybe one interior line missing) */ }
    else if (ys.length === 4 && !missing && Math.abs(span - 3 * d) <= 0.4 * d) {
      // one outer line missing: add on the side with more long-run evidence
      const up = projAt(ys[0] - d), dn = projAt(ys[3] + d);
      ys = up >= dn ? [ys[0] - d, ...ys] : [...ys, ys[3] + d];
    } else continue;
    grp.forEach(k => used.add(k));
    const top = Math.round(ys[0] - lt), bottom = Math.round(ys[ys.length - 1] + lt + 1);
    const ym = Math.round(ys[0] + 2 * d); let x0 = w, x1 = 0;
    // horizontal extent: columns with ink on >= 3 of the 5 expected line rows
    const rowsY = [0, 1, 2, 3, 4].map(k => Math.round(ys[0] + k * d));
    for (let x = 0; x < w; x++) {
      let hits = 0;
      for (const yr of rowsY) { for (let dy = -lt - 1; dy <= lt + 1; dy++) { const yy = yr + dy; if (yy >= 0 && yy < h && bin[yy * w + x]) { hits++; break; } } }
      if (hits >= 3) { if (x < x0) x0 = x; x1 = x; }
    }
    staves.push({ top, bottom, lines: rowsY, x0, x1, inferred: ys.length - grp.length });
  }
  return staves;
}

function detectLyricLines(page, opts = {}) {
  const { width: w, height: h } = page;
  const r = opts.binRadius || Math.max(8, Math.round(w / 90));
  let bin = IMG.binarize(page, r, 0.15);
  const { lt, ss: ss0 } = runLengths(bin, w, h);
  const skew = estimateSkew(bin, w, h);
  bin = shear(bin, w, h, skew, 0);
  const gray = shear(page.data, w, h, skew, 255);
  const staves = findStaves(bin, w, h, lt, ss0);
  const ss = staves.length ? median(staves.map(s => (s.lines[4] - s.lines[0]) / 4)) - lt : ss0;
  const out = [];
  for (let si = 0; si < staves.length; si++) {
    const st = staves[si], nx = staves[si + 1];
    const y0 = Math.ceil(st.bottom + lt), y1 = Math.floor(nx ? nx.top - lt : Math.min(h, st.bottom + 14 * (ss + lt)));
    if (y1 - y0 < 1.5 * ss) continue;
    const x0 = Math.round(Math.max(0, Math.min(st.x0, nx ? nx.x0 : st.x0) - 4 * ss)), x1 = Math.round(Math.min(w, Math.max(st.x1, nx ? nx.x1 : st.x1) + 2 * ss));
    // components in band
    const bw = x1 - x0, bh = y1 - y0;
    const band = new Uint8Array(bw * bh);
    for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) band[y * bw + x] = bin[(y0 + y) * w + x0 + x];
    const { labels, comps } = IMG.components(band, bw, bh);
    const cand = [];
    for (let k = 1; k < comps.length; k++) {
      const c = comps[k]; const ch = c.y1 - c.y0, cw = c.x1 - c.x0;
      c.touch = c.y0 === 0 || c.y1 === bh;     // attached to staff/stems above or below
      if (c.touch) continue;
      if (ch > 4.0 * ss || cw > 30 * ss) continue;    // stems, beams, slurs, long lines
      if (c.area < 3) continue;
      cand.push(c);
    }
    // letter-like comps for baseline voting
    const letters = cand.filter(c => (c.y1 - c.y0) >= 0.45 * ss && (c.y1 - c.y0) <= 3.2 * ss && (c.x1 - c.x0) <= 4 * ss && (c.x1 - c.x0) >= 0.12 * ss);
    if (letters.length < 4) continue;
    const hist = new Float64Array(bh + 1);
    for (const c of letters) hist[c.y1] += 1;
    // smooth
    const sm = new Float64Array(bh + 1); const R = Math.max(1, Math.round(0.15 * ss));
    for (let y = 0; y <= bh; y++) { let s = 0; for (let d = -R; d <= R; d++) { const yy = y + d; if (yy >= 0 && yy <= bh) s += hist[yy]; } sm[y] = s; }
    // peaks
    const peaks = [];
    const order = [...sm.keys()].sort((a, b) => sm[b] - sm[a]);
    for (const y of order) {
      if (sm[y] < 4) break;
      if (peaks.some(p => Math.abs(p - y) < 1.4 * ss)) continue;
      peaks.push(y);
    }
    peaks.sort((a, b) => a - b);
    for (const bl of peaks) {
      // members: letters whose bottom near baseline (or descenders), then other comps within band
      const core = letters.filter(c => Math.abs(c.y1 - bl) <= 0.25 * ss + 1);
      if (core.length < 4) continue;
      const xh = median(core.map(c => c.y1 - c.y0).sort((a, b) => a - b).slice(0, Math.max(1, Math.floor(core.length * 0.5))));
      const tall = median(core.map(c => c.y1 - c.y0).sort((a, b) => a - b).slice(Math.floor(core.length * 0.5)));
      const top = bl - 1.9 * tall, bot = bl + 0.6 * tall;
      const mem = cand.filter(c => c.y0 >= top && c.y1 <= bot && (c.y1 - c.y0) <= 2.2 * tall);
      if (tall < 0.6 * ss || median(core.map(c => c.area)) < 0.15 * ss * ss) continue;   // rows of specks / dots
      const lx0 = Math.min(...mem.map(c => c.x0)), lx1 = Math.max(...mem.map(c => c.x1));
      if (lx1 - lx0 < 0.2 * (st.x1 - st.x0) && core.length < 8) continue;
      // reject music rows: noteheads below staff etc. look like round blobs with bottom alignment; require text-like height variety
      const aspectMed = median(core.map(c => (c.x1 - c.x0) / (c.y1 - c.y0)));
      const hyph = [], ext = [];
      for (const c of mem) {
        const ch = c.y1 - c.y0, cw = c.x1 - c.x0, cy = (c.y0 + c.y1) / 2;
        if (ch <= Math.max(2, 0.4 * xh) && cw >= 1.6 * ch) {
          if (cy < bl - 0.15 * xh && cy > bl - 0.95 * xh && cw <= 3.5 * xh) hyph.push({ x0: c.x0 + x0, x1: c.x1 + x0 });
          else if (Math.abs(cy - bl) <= 0.3 * xh + 1 && cw >= 1.2 * xh) ext.push({ x0: c.x0 + x0, x1: c.x1 + x0 });
        }
      }
      // strip: keep member pixels only (from sheared gray)
      const sx0 = Math.max(0, lx0 - Math.round(0.5 * xh)), sx1 = Math.min(bw, lx1 + Math.round(0.5 * xh));
      const sy0 = Math.max(0, Math.round(top)), sy1 = Math.min(bh, Math.round(bot));
      const keep = new Set(mem.map(c => c.id));
      const dropHy = opts.dropHyphens ? new Set(mem.filter(c => hyph.some(hh => hh.x0 === c.x0 + x0) || ext.some(e => e.x0 === c.x0 + x0)).map(c => c.id)) : new Set();
      const SW = sx1 - sx0, SH = sy1 - sy0, data = new Uint8ClampedArray(SW * SH).fill(255);
      for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
        const lab = labels[(sy0 + y) * bw + sx0 + x];
        if (lab && keep.has(lab) && !dropHy.has(lab)) data[y * SW + x] = opts.binaryStrip ? 0 : gray[(y0 + sy0 + y) * w + x0 + sx0 + x];
      }
      out.push({
        staff: si, baseline: y0 + bl, xHeight: xh, capHeight: tall, sizePx: tall / 0.70, ss, lt, skewDeg: skew, aspectMed,
        bbox: [x0 + lx0, y0 + Math.min(...mem.map(c => c.y0)), x0 + lx1, y0 + Math.max(...mem.map(c => c.y1))],
        nComps: mem.length, hyphens: hyph, extenders: ext,
        strip: { width: SW, height: SH, data, x0: x0 + sx0, y0: y0 + sy0 },
      });
    }
  }
  return { skewDeg: skew, lt, ss, staves, lines: out };
}
function median(a) { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; }
/** map a point from deskewed (sheared) coordinates back to page coordinates */
function unshearY(x, y, deg) { return y + x * Math.tan(deg * Math.PI / 180); }
module.exports = { detectLyricLines, unshearY, runLengths, estimateSkew, findStaves };
