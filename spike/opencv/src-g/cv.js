'use strict';
// Header reader and pre-clean of degraded scans, plain JS.
//
// readHeaders(fr, asm) runs after assemblePage (omr.js) and reads what the header parse left
// unread, by matching Bravura glyph templates (SIL OFL 1.1, Steinberg Media Technologies; 24 px
// per staff space, 1 bit per pixel, BANK at the end; spike/opencv/tools/templates.js) scaled to
// the staff space:
//   - numbered time signatures on the first system of a page: the header finds the glyph but did
//     not read its numbers. A time signature the header missed altogether (two stacked digits
//     right after the clef / key) is read the same way; the header then ends after it, so its
//     digits are no longer taken for notes or accidentals.
//   - clefs the header could not read (clef guessed): G / F / C at the staff start.
// Matching stays inside the header region (a few glyphs per staff). docs/spike-opencv.md.
//
// precleanPage(gray) (front.js) repairs degraded scans before binarisation; dewarpReading (omr.js)
// rereads photographed / curled pages straightened from their staves; see their sections.
const { labelComponents } = require('./cc');

const BANK_SP = 24;
const DIGITS = ['digit-0', 'digit-1', 'digit-2', 'digit-3', 'digit-4', 'digit-5', 'digit-6', 'digit-7', 'digit-8', 'digit-9'];
const NOT_DIGITS = ['rest-quarter', 'rest-8th', 'rest-16th', 'acc-sharp', 'acc-flat', 'acc-natural', 'head-filled', 'head-half', 'time-C'];
const CLEFS = ['clef-G', 'clef-F', 'clef-C'];
const SCALES = [0.85, 1, 1.15];

// ---------------------------------------------------------------- matching
// Template matcher in plain JS: area-weighted resize, threshold, and normalised correlation
// (OpenCV's TM_CCOEFF_NORMED) by direct correlation with integral-image window statistics.
function areaResize(src, sw, sh, dw, dh) {
  // separable area weights (OpenCV INTER_AREA for shrinking)
  const weights = (sn, dn) => {
    const k = sn / dn, out = [];
    for (let d = 0; d < dn; d++) {
      const a = d * k, b = (d + 1) * k, w = [];
      for (let s0 = Math.floor(a); s0 < Math.min(sn, Math.ceil(b)); s0++) { const f = Math.min(b, s0 + 1) - Math.max(a, s0); if (f > 1e-9) w.push([s0, f / k]); }
      out.push(w);
    }
    return out;
  };
  const wx = weights(sw, dw), wy = weights(sh, dh), tmp = new Float32Array(sh * dw), out = new Float32Array(dw * dh);
  for (let y = 0; y < sh; y++) for (let x = 0; x < dw; x++) { let v = 0; for (const [s0, f] of wx[x]) v += src[y * sw + s0] * f; tmp[y * dw + x] = v; }
  for (let y = 0; y < dh; y++) for (let x = 0; x < dw; x++) { let v = 0; for (const [s0, f] of wy[y]) v += tmp[s0 * dw + x] * f; out[y * dw + x] = v; }
  return out;
}

function makeJsApi() {
  const tpl = {};
  for (const [name, [w, h, b64]] of Object.entries(BANK)) {
    const bits = typeof atob === 'function' ? Uint8Array.from(atob(b64), c => c.charCodeAt(0)) : new Uint8Array(Buffer.from(b64, 'base64'));
    const d = new Float32Array(w * h);
    for (let i = 0; i < w * h; i++) d[i] = (bits[i >> 3] >> (i & 7)) & 1 ? 255 : 0;
    tpl[name] = { w, h, d };
  }
  const cache = new Map();
  const scaled = (name, k) => {
    const key = name + '@' + k.toFixed(3);
    let t = cache.get(key);
    if (!t) {
      const g = tpl[name], w = Math.max(3, Math.round(g.w * k)), h = Math.max(3, Math.round(g.h * k));
      const r = areaResize(g.d, g.w, g.h, w, h), d = new Float32Array(w * h);
      let sum = 0;
      for (let i = 0; i < d.length; i++) { d[i] = Math.round(r[i]) > 127 ? 1 : 0; sum += d[i]; }
      const mean = sum / d.length; let ss = 0;
      const z = new Float32Array(d.length); for (let i = 0; i < d.length; i++) { z[i] = d[i] - mean; ss += z[i] * z[i]; }
      t = { w, h, z, ss };
      if (cache.size > 400) cache.clear();
      cache.set(key, t);
    }
    return t;
  };
  function scores(img, sp, names) {
    const out = {}, k0 = sp / BANK_SP, padded = new Map();
    for (const name of names) {
      let best = -1;
      for (const f of SCALES) {
        const t = scaled(name, k0 * f);
        if (t.w > 2.2 * img.w + 4 || t.h > 2.2 * img.h + 4 || t.w * 3 < img.w || t.h * 3 < img.h) continue;
        const pad = Math.max(t.w, t.h) >> 1;
        let P = padded.get(pad);
        if (!P) {
          const W = img.w + 2 * pad, H = img.h + 2 * pad, d = new Uint8Array(W * H), S = new Float64Array((W + 1) * (H + 1));
          for (let y = 0; y < img.h; y++) for (let x = 0; x < img.w; x++) if (img.data[y * img.w + x]) d[(y + pad) * W + x + pad] = 1;
          for (let y = 0; y < H; y++) { let row = 0; for (let x = 0; x < W; x++) { row += d[y * W + x]; S[(y + 1) * (W + 1) + x + 1] = S[y * (W + 1) + x + 1] + row; } }
          P = { W, H, d, S }; padded.set(pad, P);
        }
        if (t.w > P.W || t.h > P.H) continue;
        const n = t.w * t.h, W1 = P.W + 1;
        // only small shifts: the template's centre within r of the glyph's (the glyph is already cut out)
        const r = Math.max(2, Math.round(0.35 * sp));
        const cx = pad + img.w / 2 - t.w / 2, cy = pad + img.h / 2 - t.h / 2;
        const xa = Math.max(0, Math.floor(cx - r)), xb = Math.min(P.W - t.w, Math.ceil(cx + r));
        const ya = Math.max(0, Math.floor(cy - r)), yb = Math.min(P.H - t.h, Math.ceil(cy + r));
        let mx = -1;
        for (let y = ya; y <= yb; y++) for (let x = xa; x <= xb; x++) {
          // binary image: sum == sum of squares
          const s = P.S[(y + t.h) * W1 + x + t.w] - P.S[y * W1 + x + t.w] - P.S[(y + t.h) * W1 + x] + P.S[y * W1 + x];
          const vI = s - s * s / n;
          if (vI <= 1e-6 || t.ss <= 1e-6) continue;
          let num = 0;
          for (let v = 0; v < t.h; v++) { const o = (y + v) * P.W + x, to = v * t.w; for (let u = 0; u < t.w; u++) if (P.d[o + u]) num += t.z[to + u]; }
          const r = num / Math.sqrt(t.ss * vI);
          if (r > mx) mx = r;
        }
        const sc = mx * Math.sqrt(Math.min(1, n / (img.w * img.h)));
        if (sc > best) best = sc;
      }
      out[name] = best;
    }
    return out;
  }
  const best = (sc, names) => names.reduce((a, n) => (sc[n] > sc[a] ? n : a), names[0]);
  return { scores, best };
}

let api0 = null;
const matcher = () => (api0 ||= makeJsApi());

// ---------------------------------------------------------------- glyphs from the page
// components of R inside box b (by centre), as one trimmed glyph image; parts are components
// at least minArea px. Returns {img, x0, y0, x1, y1, comps} or null.
function glyphIn(R, b, minArea) {
  const x0 = Math.max(0, Math.floor(b.x0)), y0 = Math.max(0, Math.floor(b.y0));
  const x1 = Math.min(R.width - 1, Math.ceil(b.x1)), y1 = Math.min(R.height - 1, Math.ceil(b.y1));
  if (x1 <= x0 || y1 <= y0) return null;
  const w = x1 - x0 + 1, h = y1 - y0 + 1, crop = { width: w, height: h, data: new Uint8Array(w * h) };
  for (let y = 0; y < h; y++) crop.data.set(R.data.subarray((y + y0) * R.width + x0, (y + y0) * R.width + x0 + w), y * w);
  const { labels, comps } = labelComponents(crop);
  // a component cut by the box edge is kept only when its centre is inside (b.cx* limits)
  const keep = comps.filter(c => c.area >= minArea && (b.inner ? b.inner(c.x0 + x0, c.y0 + y0, c.x1 + x0, c.y1 + y0) : true));
  if (!keep.length) return null;
  const ids = new Set(keep.map(c => c.id));
  let gx0 = w, gy0 = h, gx1 = -1, gy1 = -1;
  for (const c of keep) { gx0 = Math.min(gx0, c.x0); gy0 = Math.min(gy0, c.y0); gx1 = Math.max(gx1, c.x1); gy1 = Math.max(gy1, c.y1); }
  const gw = gx1 - gx0 + 1, gh = gy1 - gy0 + 1, data = new Uint8Array(gw * gh);
  for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) if (ids.has(labels[(y + gy0) * w + x + gx0])) data[y * gw + x] = 1;
  return { img: { w: gw, h: gh, data }, x0: gx0 + x0, y0: gy0 + y0, x1: gx1 + x0, y1: gy1 + y0, comps: keep.map(c => ({ x0: c.x0 + x0, x1: c.x1 + x0, y0: c.y0 + y0, y1: c.y1 + y0 })) };
}

// the pieces of a number, left to right: components overlapping in x form one group;
// the run of groups from the first one, while gaps stay small (a digit cut apart by staff-line
// removal, or the two digits of 12)
function numberGroups(g, sp, start = 0) {
  const groups = [];
  for (const c of g.comps.slice().sort((p, q) => p.x0 - q.x0)) {
    const last = groups[groups.length - 1];
    if (last && c.x0 <= last.x1) { last.x1 = Math.max(last.x1, c.x1); last.y0 = Math.min(last.y0, c.y0); last.y1 = Math.max(last.y1, c.y1); }
    else groups.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1 });
  }
  const run = [];
  for (const d of groups.slice(start)) {
    if (run.length && (d.x0 - run[run.length - 1].x1 > 0.6 * sp || d.x1 - run[0].x0 > 3.6 * sp)) break;
    run.push(d);
  }
  return { run, n: groups.length };
}

// staff-line removal leaves short vertical gaps in a glyph: fill them where ink is above and below
function heal(img, n) {
  const { w, h, data } = img;
  for (let x = 0; x < w; x++) {
    let last = -1;
    for (let y = 0; y < h; y++) {
      if (!data[y * w + x]) continue;
      if (last >= 0 && y - last > 1 && y - last - 1 <= n) for (let k = last + 1; k < y; k++) data[k * w + x] = 1;
      last = y;
    }
  }
  return img;
}

const TYPES = new Set([1, 2, 4, 8, 16, 32]);

// the number printed in box b (one row of a time signature): read as one digit, or as two
// digits split at a gap between groups, whichever matches better. {n, score, x0, x1} or null
function readNumber(api, R, b, sp, minScore) {
  const minA = Math.max(3, 0.03 * sp * sp);
  const g = glyphIn(R, b, minA);
  if (!g) return null;
  // the search window may begin on the tail of a key signature: try the first few groups as the start
  for (let start = 0; start < 3; start++) {
    const { run, n } = numberGroups(g, sp, start);
    if (!run.length) return null;
    const r = readRun(api, R, b, sp, minScore, run, minA);
    if (r) return r;
    if (start + 1 >= n) return null;
  }
  return null;
}

function readRun(api, R, b, sp, minScore, run, minA) {
  const box = (gs) => ({ x0: gs[0].x0, x1: gs[gs.length - 1].x1, y0: Math.min(...gs.map(d => d.y0)), y1: Math.max(...gs.map(d => d.y1)) });
  const digit = (gs) => {
    const bb = box(gs), w = bb.x1 - bb.x0 + 1, h = bb.y1 - bb.y0 + 1;
    if (h < 1.0 * sp || h > 2.8 * sp || w < 0.3 * sp || w > 2.3 * sp) return null;
    const d = glyphIn(R, { ...bb, inner: b.inner }, minA);
    if (!d) return null;
    const sc = api.scores(heal(d.img, Math.max(2, Math.round(0.18 * sp))), sp, DIGITS.concat(NOT_DIGITS));
    const dg = api.best(sc, DIGITS), nd = api.best(sc, NOT_DIGITS);
    if (sc[dg] < minScore || sc[nd] > sc[dg] - 0.02) return null;
    return { v: DIGITS.indexOf(dg), score: sc[dg] };
  };
  let best = null;
  const one = digit(run);
  if (one) best = { n: one.v, score: one.score };
  for (let k = 1; k < run.length; k++) {
    const a = digit(run.slice(0, k)); if (!a || a.v === 0) continue;
    const c = digit(run.slice(k)); if (!c) continue;
    const sc = Math.min(a.score, c.score);
    // two digits must beat one clearly (pieces of one digit also read as digits)
    if (!best || sc > best.score + 0.05) best = { n: 10 * a.v + c.v, score: sc };
  }
  if (!best) return null;
  const bb = box(run);
  return { n: best.n, score: best.score, x0: bb.x0, x1: bb.x1 };
}

function readTime(api, R, st, x0, x1, sp, minScore) {
  const xm = (x0 + x1) / 2, l0 = st.yAt(0, xm), l2 = st.yAt(2, xm), l4 = st.yAt(4, xm);
  const inRow = (ya, yb) => (cx0, cy0, cx1, cy1) => { const cy = (cy0 + cy1) / 2; return cy > ya && cy < yb; };
  // the rows are cut at the middle line: the two numbers often touch there once it is removed
  const top = readNumber(api, R, { x0, x1, y0: l0 - 0.7 * sp, y1: l2, inner: inRow(l0 - 0.7 * sp, l2 + 1) }, sp, minScore);
  if (!top) return null;
  const bot = readNumber(api, R, { x0, x1, y0: l2 + 1, y1: l4 + 0.7 * sp, inner: inRow(l2, l4 + 0.7 * sp) }, sp, minScore);
  if (!bot || top.n < 2 || top.n > 16 || !TYPES.has(bot.n)) return null;
  // the two numbers stand one above the other
  if (Math.min(top.x1, bot.x1) - Math.max(top.x0, bot.x0) < 0.3 * sp) return null;
  return { beats: top.n, type: bot.n, x0: Math.min(top.x0, bot.x0), x1: Math.max(top.x1, bot.x1), score: Math.min(top.score, bot.score) };
}

function readClefAt(api, R, st, sp) {
  const left = st.left, ya = st.yAt(0, left) - 3.5 * sp, yb = st.yAt(4, left) + 3.5 * sp;
  const g = glyphIn(R, { x0: left - 0.6 * sp, x1: left + 4 * sp, y0: ya, y1: yb, inner: (cx0, cy0, cx1, cy1) => cx0 < left + 2.5 * sp && cx1 - cx0 < 3.5 * sp }, Math.max(3, 0.03 * sp * sp));
  if (!g) return null;
  // the tallest part and what overlaps it in x (pieces cut by staff-line removal)
  const tall = g.comps.slice().sort((a, b) => (b.y1 - b.y0) - (a.y1 - a.y0))[0];
  if (!tall || tall.y1 - tall.y0 < 2.4 * sp) return null;
  const parts = g.comps.filter(c => c.x1 > tall.x0 + 0.1 * sp && c.x0 < tall.x1 - 0.1 * sp);
  const b = { x0: Math.min(...parts.map(c => c.x0)), x1: Math.max(...parts.map(c => c.x1)), y0: Math.min(...parts.map(c => c.y0)), y1: Math.max(...parts.map(c => c.y1)) };
  const gl = glyphIn(R, { ...b, inner: (cx0, cy0, cx1, cy1) => cx1 > tall.x0 + 0.1 * sp && cx0 < tall.x1 - 0.1 * sp }, Math.max(3, 0.03 * sp * sp));
  if (!gl) return null;
  const sc = api.scores(heal(gl.img, Math.max(2, Math.round(0.18 * sp))), sp, CLEFS), k = api.best(sc, CLEFS);
  const second = Math.max(...CLEFS.filter(c => c !== k).map(c => sc[c]));
  if (sc[k] < 0.45 || sc[k] - second < 0.05) return null;
  if (k === 'clef-C') {
    const p = Math.round((st.yAt(2, left) - (gl.y0 + gl.y1) / 2) / sp);
    return Math.abs(p) <= 2 ? { clef: 'C' + (3 + p), score: sc[k], x1: gl.x1 } : null;
  }
  return { clef: k === 'clef-G' ? 'G' : 'F', score: sc[k], x1: gl.x1 };
}

// ---------------------------------------------------------------- header reading
function readHeaders(fr, asm, opts = {}, stats = {}) {
  const R = fr && fr.R;
  if (!R || !asm) return stats;
  const api = matcher();
  const minScore = opts.minScore ?? 0.45;
  for (const sy of asm.systems) {
    // time signatures only at the top of a page: later systems carry meter changes, which the
    // score does not model (one meter per piece), and a change read as the piece's meter is worse
    // than the meter inferred from the bars
    const timeOk = sy === asm.systems[0];
    for (const s of sy.staves) {
      const st = s.st, sp = st.space || fr.ss, h = s.hdr;
      if (!h) continue;
      try {
        if (timeOk && h.time && !h.time.beats) {
          // numbered time signature found by the header: read its numbers
          const t = readTime(api, R, st, h.time.x0 - 0.3 * sp, h.time.x1 + 0.3 * sp, sp, minScore);
          if (t) { h.time.beats = t.beats; h.time.type = t.type; h.time.cv = true; stats.timeRead = (stats.timeRead || 0) + 1; }
        } else if (timeOk && !h.time) {
          // none found: two stacked digits right after the clef / key signature
          const x0 = h.end - 0.4 * sp;
          const t = readTime(api, R, st, x0, x0 + 3.2 * sp, sp, Math.max(minScore, 0.55));
          if (t && t.x0 < h.end + 1.5 * sp) {
            h.time = { x0: t.x0, x1: t.x1, beats: t.beats, type: t.type, cv: true };
            h.end = Math.max(h.end, t.x1 + 0.2 * sp);
            const n = s.chords.length;
            s.chords = s.chords.filter(c => c.x > h.end);
            stats.timeFound = (stats.timeFound || 0) + 1;
            stats.headsDropped = (stats.headsDropped || 0) + n - s.chords.length;
          }
        }
        if (h.clefGuessed && opts.clefs !== false) {
          const c = readClefAt(api, R, st, sp);
          if (c) { h.clef = c.clef; h.clefGuessed = false; h.cvClef = true; stats.clefRead = (stats.clefRead || 0) + 1; }
        }
      } catch (e) { stats.errors = (stats.errors || 0) + 1; }
    }
    // a bass clef over a treble clef in a two-staff system is a misreading (as in assemblePage)
    const ss = sy.staves;
    if (ss.length === 2 && ss[0].hdr.cvClef && ss[0].hdr.clef === 'F' && /^G/.test(ss[1].hdr.clef || '')) {
      ss[0].hdr.clef = 'G'; ss[0].hdr.clefGuessed = true; ss[0].hdr.cvClef = false; stats.clefRead--;
    }
  }
  return stats;
}

// ---------------------------------------------------------------- pre-clean of degraded scans
// front() calls precleanPage(gray) before binarisation. A cheap page-quality check (30-70 ms)
// decides which repairs the page needs; a page that looks clean is returned as the same object,
// so clean pages go through the pipeline exactly as before. Repairs (plain JS; they were first
// built with OpenCV.js, and this port gives the same pixels to within 2-5 grey levels and the same
// scores, without a 10 MB asset or a ~1 s load: docs/spike-opencv.md):
//   flatten    stained, yellowed or heavily damaged paper: divide by a background estimated with
//              a large grey closing (gain capped, so a dark surround is not turned into texture)
//   descreen   halftone screens: Gaussian low-pass before thresholding
//   thin       thick photocopies (strokes fattened, heads filled in): grow the paper by 1-3 px,
//              until the staff lines are about a tenth of a space thick
//   close      thin photocopies whose strokes fell apart into loose dots: grow the ink by 1 px
//   sharpen    heavy blur: unsharp mask
// Severe phone shots get flatten only (milder ones read better as they are); noise and JPEG are left
// alone: every repair tried on them measured worse. If a repaired page shows no staves, front()
// reads the page as it was.
const { estimateStaffSpace } = require('./staffspace');

function pageQuality(g) {
  const { width: w, height: h, data } = g, n = w * h;
  const hist = new Float64Array(256);
  for (let i = 0; i < n; i++) hist[data[i]]++;
  let sum = 0; for (let v = 0; v < 256; v++) sum += v * hist[v];
  let wB = 0, sB = 0, best = 0, thr = 128;
  for (let v = 0; v < 256; v++) {
    wB += hist[v]; if (!wB || wB === n) continue; sB += v * hist[v];
    const b = wB * (n - wB) * (sB / wB - (sum - sB) / (n - wB)) ** 2;
    if (b > best) { best = b; thr = v; }
  }
  let mid = 0, dark = 0, acc1 = 0, p1 = 0;
  for (let v = 61; v < 200; v++) mid += hist[v];
  for (let v = 0; v <= 60; v++) dark += hist[v];
  for (let v = 0; v < 256; v++) { acc1 += hist[v]; if (acc1 >= 0.01 * n) { p1 = v; break; } }
  // paper per 32 px cell: its 90th percentile, and the spread of the pixels near it
  const CS = 32, bg = [], sd = [], cellH = new Uint32Array(256);
  for (let cy = 0; cy < h; cy += CS) for (let cx = 0; cx < w; cx += CS) {
    cellH.fill(0); let cnt = 0;
    for (let y = cy; y < Math.min(h, cy + CS); y += 2) for (let x = cx; x < Math.min(w, cx + CS); x += 2) { cellH[data[y * w + x]]++; cnt++; }
    let acc = 0, p90 = 255; for (let v = 0; v < 256; v++) { acc += cellH[v]; if (acc >= 0.9 * cnt) { p90 = v; break; } }
    bg.push(p90);
    let s1 = 0, s2 = 0, m = 0; for (let v = Math.max(0, p90 - 70); v < 256; v++) { s1 += v * cellH[v]; s2 += v * v * cellH[v]; m += cellH[v]; }
    sd.push(m ? Math.sqrt(Math.max(0, s2 / m - (s1 / m) ** 2)) : 0);
  }
  const pct = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
  // isolated dark pixels (all 8 neighbours light), per megapixel
  let speck = 0;
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x; if (data[i] > thr) continue;
    if (data[i - 1] > thr && data[i + 1] > thr && data[i - w] > thr && data[i + w] > thr && data[i - w - 1] > thr && data[i - w + 1] > thr && data[i + w - 1] > thr && data[i + w + 1] > thr) speck++;
  }
  const bin = { width: w, height: h, data: new Uint8Array(n) };
  for (let i = 0; i < n; i++) bin.data[i] = data[i] <= thr ? 1 : 0;
  const sp = estimateStaffSpace(bin);
  // blur: inked pixels that are only mid-grey, and how light the darkest 1 % of the page is
  return { thr, mid: mid / n, midShare: mid / Math.max(1, mid + dark), p1, bgLow: (255 - pct(bg, 0.5)) / 255, bgUneven: (pct(bg, 0.95) - pct(bg, 0.05)) / 255, bgStd: pct(sd, 0.5),
    speck: speck / (n / 1e6), ss: sp.ss, lt: sp.lt, ltss: sp.ss > 0 ? sp.lt / sp.ss : 0 };
}

// which repairs a page needs, from its quality (empty: leave the page alone)
function precleanPlan(q, force) {
  if (force) return force.split(',').filter(Boolean);
  const ops = [];
  const binary = q.bgStd < 0.5 && q.mid < 0.03;
  if (binary) {
    // photocopies: fattened strokes are thinned; thin ones broken into loose dots are rejoined
    // (a binary page with thousands of specks is noise, which rejoining would only grow)
    if (q.ltss > 0.16) ops.push('thin');
    else if (q.speck > 300 && q.speck < 2000) ops.push('close');
    return ops;
  }
  if (q.speck > 25000 && q.bgStd > 4) return ['descreen'];
  // stained / yellowed paper, heavy combined damage (not phone shots: the binariser handles their
  // shading better, and flattening their dark surround adds texture)
  // (severe phone shots too: dark, uneven, grainy paper; milder ones read better as they are)
  if (q.mid > 0.15 && ((q.bgUneven < 0.4 && q.bgLow > 0.12 && q.midShare > 0.8) || q.bgStd > 6.8 || (q.mid > 0.5 && q.bgLow > 0.33 && q.bgStd > 4.5 && q.speck < 200))) ops.push('flatten');
  // heavy blur: nearly no ink pixel is dark any more
  if (!ops.length && q.midShare > 0.94 && q.p1 > 100) ops.push('sharpen');
  return ops;
}

// ---- the repairs (separable filters on typed arrays, OpenCV's border rules: reflect-101 for
// blurs; outside pixels ignored by max / min)
function gaussKernel(sigma) {
  const r = Math.max(1, Math.round(sigma * 3)), k = new Float32Array(2 * r + 1);
  let s = 0; for (let i = -r; i <= r; i++) { k[i + r] = Math.exp(-(i * i) / (2 * sigma * sigma)); s += k[i + r]; }
  for (let i = 0; i < k.length; i++) k[i] /= s;
  return { k, r };
}
const reflect = (i, n) => { if (n === 1) return 0; while (i < 0 || i >= n) i = i < 0 ? -i : 2 * n - 2 - i; return i; };
// separable Gaussian of an 8-bit image; returns Float32Array
function gaussBlur(src, w, h, sigma) {
  const { k, r } = gaussKernel(sigma), tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) {
    const o = y * w;
    for (let x = 0; x < w; x++) {
      let v = 0;
      if (x >= r && x < w - r) for (let i = -r; i <= r; i++) v += src[o + x + i] * k[i + r];
      else for (let i = -r; i <= r; i++) v += src[o + reflect(x + i, w)] * k[i + r];
      tmp[o + x] = v;
    }
  }
  for (let y = 0; y < h; y++) {
    const inside = y >= r && y < h - r;
    for (let x = 0; x < w; x++) {
      let v = 0;
      if (inside) for (let i = -r; i <= r; i++) v += tmp[(y + i) * w + x] * k[i + r];
      else for (let i = -r; i <= r; i++) v += tmp[reflect(y + i, h) * w + x] * k[i + r];
      out[y * w + x] = v;
    }
  }
  return out;
}
const clamp8 = (v) => (v < 0 ? 0 : v > 255 ? 255 : Math.round(v));
// running max (grow = true) or min over a 1-D window [i - a, i + b] along rows or columns
function morph1(src, w, h, a, b, horiz, grow) {
  const out = new Uint8Array(w * h);
  const n = horiz ? w : h, lines = horiz ? h : w;
  for (let l = 0; l < lines; l++) {
    for (let i = 0; i < n; i++) {
      let v = grow ? 0 : 255;
      for (let j = Math.max(0, i - a); j <= Math.min(n - 1, i + b); j++) {
        const p = horiz ? src[l * w + j] : src[j * w + l];
        if (grow ? p > v : p < v) v = p;
      }
      out[horiz ? l * w + i : i * w + l] = v;
    }
  }
  return out;
}
// grey closing with an elliptical element of size k (OpenCV MORPH_ELLIPSE): max, then min
function ellipseClose(src, w, h, k) {
  const r = k >> 1, half = [];
  // OpenCV's ellipse rows: half-width of row dy
  for (let dy = -r; dy <= r; dy++) half.push(r ? Math.round(r * Math.sqrt((r * r - dy * dy) / (r * r))) : 0);
  const pass = (img, grow) => {
    const out = new Uint8Array(w * h);
    // per row offset: max/min over horizontal windows of each half-width, cached
    const rowCache = new Map();
    const rowOp = (hw) => { if (!rowCache.has(hw)) rowCache.set(hw, morph1(img, w, h, hw, hw, true, grow)); return rowCache.get(hw); };
    out.fill(grow ? 0 : 255);
    for (let dy = -r; dy <= r; dy++) {
      const R = rowOp(half[dy + r]);
      for (let y = 0; y < h; y++) {
        const sy = y + dy, o = y * w, so = sy * w;
        if (sy < 0 || sy >= h) continue; // outside the image does not count (OpenCV's default border)
        if (grow) { for (let x = 0; x < w; x++) if (R[so + x] > out[o + x]) out[o + x] = R[so + x]; }
        else { for (let x = 0; x < w; x++) if (R[so + x] < out[o + x]) out[o + x] = R[so + x]; }
      }
    }
    return out;
  };
  return pass(pass(src, true), false);
}
function bilinearUp(src, W, H, w, h) {
  const out = new Float32Array(w * h), fx = W / w, fy = H / h;
  for (let y = 0; y < h; y++) {
    const sy = Math.min(H - 1, Math.max(0, (y + 0.5) * fy - 0.5)), y0 = Math.floor(sy), y1 = Math.min(H - 1, y0 + 1), ty = sy - y0;
    for (let x = 0; x < w; x++) {
      const sx = Math.min(W - 1, Math.max(0, (x + 0.5) * fx - 0.5)), x0 = Math.floor(sx), x1 = Math.min(W - 1, x0 + 1), tx = sx - x0;
      out[y * w + x] = (src[y0 * W + x0] * (1 - tx) + src[y0 * W + x1] * tx) * (1 - ty) + (src[y1 * W + x0] * (1 - tx) + src[y1 * W + x1] * tx) * ty;
    }
  }
  return out;
}

function applyOpsJs(gray, ops, q) {
  const { width: w, height: h } = gray;
  let d = gray.data;
  const ss = q.ss > 4 ? q.ss : 16;
  for (const op of ops) {
    if (op === 'flatten') {
      // 4x smaller (area weights as OpenCV INTER_AREA, also when the size is not a multiple of 4)
      const W4 = Math.max(1, w >> 2), H4 = Math.max(1, h >> 2), smf = areaResize(d, w, h, W4, H4);
      const sm = { data: Uint8Array.from(smf, v => clamp8(v)), W: W4, H: H4 };
      const k = Math.max(3, Math.round(ss * 0.8) | 1);
      const bgc = ellipseClose(sm.data, sm.W, sm.H, k);
      const bgf = gaussBlur(bgc, sm.W, sm.H, k / 2);
      const bg8 = new Uint8Array(bgf.length); for (let i = 0; i < bgf.length; i++) bg8[i] = clamp8(bgf[i]);
      const up = bilinearUp(bg8, sm.W, sm.H, w, h);
      const bv = Array.from(bg8).sort((x, y) => x - y), floor = 0.4 * bv[Math.floor(0.95 * (bv.length - 1))];
      const o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) { const u = Math.max(floor, Math.round(up[i])); o[i] = u > 0 ? clamp8(d[i] * 255 / u) : 0; }
      d = o;
    } else if (op === 'descreen') {
      const b = gaussBlur(d, w, h, Math.max(1, ss / 14)), o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) o[i] = clamp8(b[i]);
      d = o;
    } else if (op === 'thin') {
      const n = Math.max(1, Math.min(3, Math.round((q.lt - 0.11 * ss) / 2)));
      for (let i = 0; i < n; i++) d = morph1(morph1(d, w, h, 1, 1, true, true), w, h, 1, 1, false, true);
    } else if (op === 'sharpen') {
      const b = gaussBlur(d, w, h, Math.max(1, ss / 5)), o = new Uint8Array(w * h);
      for (let i = 0; i < o.length; i++) o[i] = clamp8(3 * d[i] - 2 * b[i]);
      d = o;
    } else if (op === 'gamma' || op === 'gamma3') {
      // darken mid-greys (faint lines, stems) relative to the paper
      const gm = op === 'gamma' ? 2 : 3, o = new Uint8Array(w * h), lut = new Uint8Array(256);
      for (let v = 0; v < 256; v++) lut[v] = Math.round(255 * Math.pow(v / 255, gm));
      for (let i = 0; i < o.length; i++) o[i] = lut[d[i]];
      d = o;
    } else if (op === 'close') {
      // OpenCV 2x2 erode, anchor (1,1): min over the pixel and its left / upper neighbours
      d = morph1(morph1(d, w, h, 1, 0, true, false), w, h, 1, 0, false, false);
    }
  }
  return { width: w, height: h, data: d === gray.data ? new Uint8Array(d) : d };
}

const precleanStats = { pages: 0, cleaned: 0, ms: 0, ops: {} };
// gray page -> the same page (it looks clean) or a repaired copy
function precleanPage(gray, opts = {}) {
  const env = typeof process !== 'undefined' && process.env ? process.env : {};
  if (opts.preclean === false || env.OMR_PRECLEAN === 'off') return gray;
  if (!gray || !gray.data || gray.width < 64 || gray.height < 64) return gray;
  const t0 = Date.now();
  precleanStats.pages++;
  const q = pageQuality(gray);
  const ops = precleanPlan(q, env.OMR_PRECLEAN_OPS);
  if (!ops.length) return gray;
  let out = gray;
  try { out = applyOpsJs(gray, ops, q); } catch (e) { return gray; }
  precleanStats.cleaned++; precleanStats.ms += Date.now() - t0;
  for (const o of ops) precleanStats.ops[o] = (precleanStats.ops[o] || 0) + 1;
  out.preclean = ops;
  return out;
}

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

// A page reading that looks broken (systems of unequal size, or about one measure per system) on
// a page whose staves disagree in slope, bend or lean is read again from the dewarped page; the
// second reading is kept only if it is clearly more coherent. reread(gray) -> {fr, asm}.
function readingQuality(asm) {
  if (!asm || !asm.systems.length) return -1e9;
  // staff-measure cells (a system split into single staves does not gain any), less a penalty
  // per system smaller than the page's largest
  const sizes = asm.systems.map(s => s.staves.length), top = Math.max(...sizes);
  const cells = asm.systems.reduce((a, s) => a + s.measures.length * s.staves.length, 0);
  return cells - 3 * sizes.filter(n => n < top).length;
}
function dewarpReading(fr, asm, reread, stats = {}) {
  if (!asm || (typeof process !== 'undefined' && process.env && process.env.OMR_DEWARP === 'off')) return null;
  // landscape sheets (two-up spreads with a page missed, landscape layouts) are left alone
  if (!fr.gray || fr.gray.width > 1.1 * fr.gray.height) return null;
  const sizes = asm.systems.map(s => s.staves.length), top = Math.max(...sizes);
  const perSystem = asm.systems.reduce((a, s) => a + s.measures.length, 0) / asm.systems.length;
  if (!(sizes.some(n => n < top) || perSystem < 2)) return null;
  const g = dewarpPage(fr);
  if (!g) return null;
  const alt = reread(g);
  if (!alt || !alt.asm || alt.fr.staves.length < fr.staves.length) return null;
  const q0 = readingQuality(asm), q1 = readingQuality(alt.asm);
  if (q1 < q0 + 2) return null;
  stats.dewarped = (stats.dewarped || 0) + 1;
  alt.fr.dewarped = true;
  return alt;
}

const BANK = {"digit-0":[43,48,"AAD8AwAAAPx/AAAA+P8PAADwH/8BAMB/8D8AAP8B/wMA/g/wPwDwP4D/AcD/AfwfAP8HwP8B/D8A/h/g/wHw/4D/BwD/D/w/APh/4P8BwP+D/w8A/j/8fwDw/+H/A4D/D/8fAPz//H8AwP/n/wMA/j//HwDw//n/AID/z/8HAPx//j8A4P/z/wEA/5//DwD4//x/AMD/5/8HAP4//z8A+P/x/wHA/4f/DwD+P/x/APD/wf8DgP8H/h8A/D/g/wHw/wH/D4D/B/B/APw/gP8H8P8A+D+A/wOA/wP+DwD8H/B/AID/wf8BAPi//wcAgP//DwAA+P8/AAAA/j8AAACAfwAA"],"digit-1":[29,48,"APh/AID/HwD4/wMA/38A4P8PAP7/AcD/PwD8/weA//8A+P8fAP//A/D/fwD+/w/A//8B/P8/gO//B/j8/wCf/x/w8f8DPv5/4MP/Dzz4/4EH/z944P8HD/z/AID/HwDw/wMA/n8AwP8PAPj/AQD/PwDg/wcA/P8AgP8fAPD/AwD+fwDA/w8A+P8BAP8/AOD/BwD8/wCA/x8A8P8DAP9/APD/P8D//x/8//8D//9/"],"digit-2":[40,50,"AAAAAAAA8P8PAAD+/38AgB/A/wHABwD/A+ADAP8P8AMA/h/4BwD+H/wPAPw//D8A/H/+fwD8f/7/APx//v8A/P/+/wD8//7/APz//v8A/P/+/wD+//z/AP7//P8A/v/4fwD/f/B/AP9/4D+A/z+AD4D/HwAAwP8PAADg/wcAAPD/AQAA+H8AAAD8DwAAAP4BAACAfwAAAMAfAAAA8AcAAAD4AQAAAPwAAGAA/x4AYID//wNwwP//H3DA////fOD///9/8P///z/w////P/j///8/+P///x/8////H/zH//8P/gD//wd+APz/Az4A+P8BHADAfwAIAAAAAA=="],"digit-3":[38,48,"AMA/AAAA/v8AAPD//wAA//D/AOAP4P8A/AHwf4B/APg/4H8A/g/8fwD/B/8fwP/B/w/wf/D/A/w//P8A/w//P8D/gf8P8H/g/wH+H/B/gP8H+A/w/wBwAPwfAADA/wMAAPw/AADg/wEAgP8/AADw/z8AAPj/fwAAAP9/AAAA/z8AAAD/HwAAwP8P8AHg/wP/AfD/4f8A/H/8fwD/H/8fwP/v/wfw//v/Afx//v8A/5//H8D/5/8H8P/5/wD+P/w/gP8P/w/w/4H/Af4/4P/A/wfw////APD//w8A8P9/AADg/wMA"],"digit-4":[42,49,"AAAAAAAAAP//AAAA/v8DAAD4/wcAAOD/HwAAgP8/AAAA/n8AAAD4/wEAAPD/AwAAwP8HAAAA/x8cAAD8P3gAAPh/8AEA4P/gBwCA/4MfAAD/B38AAPwP/gEA+B/8BwDgf/gfAMD/8H8AAP/B/wEA/oP/BwD4B/8fAPAf/H8AwD/w/wGAf8D/BwD+AP8fAPwB/H8A+APw/wHgB8D/B8APAP8fgB8A/H8A///////9//////f/////n/////8/AADw/wEAAMD/BwAAAP8fAAAA/H8AAADw/wEAAMD/BwAAAP8fAAAA/n8AAAD8/wMAAP7/fwAA/P//AwDw//8PAMD//x8A"],"digit-5":[37,48,"AAAAAAD+//8f4P///wP8//9/gP///w/w////AP7//x/A////Afj//x8A////AeD//w8APPgHAIAHAAAA8AAAAAAeAAAAwAEAAAA4AAAAAAf+fwDg+P8/APz//w+AP/D/B/gD+P8BHwD8P+ABAP8PGADg/wMAAPh/AAAA/x8AAMD/A/4A+H/wfwD/H/4f4P/j/wP8f/7/gP/P/x/w//n/A/4//3/A/+f/D/j//P+B/4//H/D/8f8B/h/8H+D/g/8B/D/gH+D/A/wH/j8A////A4D//z8A4P//AADA/wMA"],"digit-6":[39,48,"AAD4AwAAwP8fAAD4wz8AAP/APwDAP+A/APgP+D8A/gP+HwD/Af8fwP/A/w/wP+D/B/gf8P8B/g/4/wD/B/h/wP8D/B/g/wD8B/h/APgA/D8AAAD+HwAAAP8PAADA/wf4AOD/g/8B8P/x/wP4//3/B/z///8H/v/H/wf//8D/h/9/wP/H/x/g/+P/D+D/8/8D8P/x/wH4//j/APx//H8A/H/+PwD+P/4fAP8P/w+A/4f/B8D/g/8D4P+B/wH4f8D/APw/wP8A/g/Af4D/B+B/wP8BwD/wfwDAP/wfAMD//wMAgP9/AAAA/wMA"],"digit-7":[39,48,"APADAAAA/g8AXMD/HwBu8P8fgHf8/x/A+///H/D9//8f+P7//z9+/////7//////3//////nn/////MD////+QD+/388AP7/Px4A/P8fBwD854cDAPDxwwEAAPxgAAAAfiAAAIA/AAAA4A8AAAD4BwAAAP4BAACA/wAAAOA/AAAA+B8AAAD+DwAAgP8DAADg/wEAAPj/AAAA/j8AAID/HwAAwP8PAADw/wMAAPz/AQAA/v8AAID/fwAAwP8/AADw/x8AAPj/BwAA/v8DAAD//wEAgP//AADA/38AAOD/PwAA8P8fAAB4gAcA"],"digit-8":[39,50,"AAA/AAAA+P8HAID//w8A8D/wHwD8A8A/AH8AgB/AHwCAH/APAIAf/AMAwA/+AQDAB/8BAOCH/wAA8MN/AAD48X8AAPzw/wAAPvj/AIAf/P8D4A/+/wf4A///H/4A////f4D///8PgP///wOA////B4D///8HgP///wcA////B4D///8H4P///wf8+f//Az/w///BD+D///EDwP///ACA/39+AAD/vx8AAP/fDwAA/+8DAID/8wEAgP/5AQDA//wAAOB/fgAA8B9+AAD4Dz8AAP4DPwAA/wB/AMB/AP8A+A8A/4f/AwD+/38AAPz/DwAA4H8AAA=="],"digit-9":[39,48,"AMA/AAAA/v8BAMD//wcA+D/8BwD+D/wHgP8H/AfA/wH+B/D/AP4H/D8A/wP+H4D/A/8PwP/B/wfg/+H/A+D/8P8B8P/4/wD4f/x/AP4//j8A/z//H4D/H/8PwP+P/w/g/8f/B/j/w/8H/v/B/wf//8D/5/9/4P///z/A/3//H8D/j/8PgP/B/wcAAOD/AwAA8P8BAAD4/wAAAPw/AD8A/h/AfwD/D/A/gP8D/D/A/wH/H/B/gP8P+D/A/wf8D+D/A/4D8P+B/wH4f8B/APgf8B8A/A/4BwD8A/4AAPzDPwAA+P8DAADgPwAA"],"time-C":[41,50,"AAAAAAAAAP4HAAAA/38AAID/gAcAwH8AHADAfwBwAMA/AOABwH8AwAfAfwDAD8B/APA/gP8A8H+A/wHw/4H/AfD/A/8D4P8H/gfA/w/+B4D/H/wPAP8//B8A/n/4PwD8f/B/APD/4P8A4P/g/wGA/8D/AwB8gP8HAAAA/w8AAAD+HwAAAPw/AAAA+H8AAADw/wAAAOD/AQAAnP8DAAA4/wcAAHD+HwAA4Pw/AADA8X8AAIDj/wAAAMP/AwAAB/8HAAAO/g8AAA74PwAAHOB/AAAcwP8BADwA/wcAPAD8HwA8APB/AD4AwP8DPwAA/v8fAAD4/w8AAID/AwAAAAAAAAA="],"time-cut":[41,70,"AAAOAAAAABwAAAAAOAAAAABwAAAAAOAAAAAAwAEAAACAAwAAAAAHAAAAAA4AAAAAHAAAAAB4AAAAAPg/AAAA/v8DAAD/Bx4AAP8HcACA/wfAA4D/D4APgP8fAB8A/zkAfwD/ccD/AP/j4P8D/sPB/wf+h8P/D/wPh/8f/B8O/z/4Hxz+f/A/OPz/8H9w+P/h/+Dw/8H/wcH/g/+DA/+D/wcH/AP/Dw7AAP4fHAAA/D84AAD4f3AAAPD/4AAA4P/BAQDA/4MDAID/BwcAcP4PDgDg/B8cAMD5fzgAgPP/cAAAx//hAACG/8MBAA7+jwMAHPwfBwAY8D8OADjg/xwAMID/OQBwAP5/AHAA+P8AeADg/wH8AID/B34AAP7/fwAA8P8/AACA/w8AAAB8AAAAAHAAAAAA4AAAAADAAQAAAIADAAAAAAcAAAAADgAAAAAcAAAAADgAAAAAcAAAAADgAAAAAAAAAAA="],"clef-G":[66,170,"AAAAAAAAAAAAAAAAAPAAAAAAAAAA4AcAAAAAAADAPwAAAAAAAID/AQAAAAAAAP8PAAAAAAAA/j8AAAAAAAD8/wEAAAAAAPD/BwAAAAAA4P8/AAAAAACA//8AAAAAAAD//wcAAAAAAP7/HwAAAAAA+P//AAAAAADg//8DAAAAAMD//w8AAAAAAP8HfgAAAAAA/AfwAQAAAAD4D4AHAAAAAOAfAB4AAAAAgH8AcAAAAAAA/gDAAwAAAAD8AQAPAAAAAPAHADwAAAAAwA8A8AAAAAAAPwDAAwAAAAB8AAAPAAAAAPgBAD4AAAAA4AcA+AAAAACAHwDgAwAAAAA+AIAPAAAAAPgAAD8AAAAA4AMA/AAAAACADwD4AwAAAAA+AOAHAAAAAPgAwB8AAAAA4AOAfwAAAACABwD+AQAAAAAeAPwHAAAAAHgA+A8AAAAA4AHwPwAAAACAB+D/AAAAAAAewP8BAAAAAHiA/wcAAAAA4AH/DwAAAAAAD/4/AAAAAAA8/P8AAAAAAPD4/wEAAAAAwPP/BwAAAAAA//8PAAAAAAD8/x8AAAAAAPD/fwAAAAAAwP//AAAAAACA//8BAAAAAAD//wcAAAAAAP7/DwAAAAAA/v8fAAAAAAD8/z8AAAAAAPj//wAAAAAA8P//AQAAAADg//8DAAAAAMD//wcAAAAAgP//DwAAAAAA//8fAAAAAAD+/z8AAAAAAPz/fwAAAAAA+P//AQAAAADw//8HAAAAAOD//zwAAAAAgP//8QAAAAAA///BAwAAAAD+/wMPAAAAAPz/BzwAAAAA+P8P8AEAAADg/x+ABwAAAMD/PwAeAAAAgP9/AHgAAAAA/v8A4AEAAAD8/wGABwAAAPD/AwA+AAAA4P8HAPAAAACA/w8AwAMAAAD/HwCA/w8AAPw/AAD//wMA+H8AgP//PwDg/wEA////AYD/AwD///8fAP8HAP7///8A/B8A/P///wfwPwD4////P8B/APD/////gP8B4P////8H/geA/////z/4DwD//////+A/APz/////h/8A+P/z4P8f/gHg/8MD/v/4B4D/Aw/w/+MfAP4HPAD/j38A/A/gAfg//gHwH4AHwP/5B8A/AB4A/+cfAP8AeAD4nz8A/AHgAcB//gHwB4AHAP/xB4AfADwA/McfAH4A8ADgH38A+AHAA4B/+AHgBwAPAP7hBwAfADwA+Ic/AHwA8ADgD/wA4AOAB4A/8AOADwAeAP6AHwB8AHgA+AN+AOAD4AHgB/ADAB+AB8AfgA8A+AEeAD8AfgCAD/AA/gDwAwB4wAP4AYAfAAAAD/ADAPwAAAA84AcA4AcAAPDADwAAfwAAwIMfAAD4BwAAnj8AAIB/AAD4fwAAAPgPAOB/AAAAwP8f8P8AAAAA/P//fwAAAACA////AAAAAADA/+8DAAAAAAAAAA8AAAAAAAAAPAAAAAAAAADwAAAAAAAAAMADAAAAAAAAAB8AAAAAAAAAeAAAAAAAAADgAQAAAAAAAIAHAAAAAAAAAB4AAAAAAAAAeAAAAAAAAADgAQAAAAAAAIAPAAAAAAAAADwAAAAA/gMA8AAAAAD8PwDAAwAAAPj/AQAPAAAA8P8HADwAAADg/z8A8AAAAID//wDAAwAAAP//BwAPAAAA/P8fADwAAADw/38A8AAAAMD//wHAAwAAAP//BwAPAAAA/P8fADwAAADw/38A+AAAAMD//wDgAQAAAP//A4AHAAAA/P8HAB8AAADg/w8APAAAAID/DwD4AAAAAPwPAPABAAAA8A8A4AcAAACAPwDADwAAAAD8AeAfAAAAAOA/8D8AAAAAAP7/PwAAAAAA8P8/AAAAAAAA/B8AAAAAAAAAAAAAAAA="],"clef-F":[67,87,"AAAAAAAAAAAAAID/BwAAAAAAwP//AwAAAADA//9/AAAAAID/4P8PAAAAAP4A8P8BAAAA+AAA/h8AAADgAwDg/wEAAIAHAAD+HwAAAB4AAPD/AcAH+AAAAP8fgH/gAwAA8P8B/AcPAACA/w/wP3wAAAD4/4D/4QMAAMD/B/yPHwAAAP5/4H/8AAAA4P8D/uP/HwAA/z/wj///AQD4/wE+/P8/AMD/DwDg//8BAP5/AAD//x8A4P8HAPj//wAA/z8AwP//DwD4/wEA/v9/AMD/DwDw//8DAP5/AAD//x8A8P8DAPj//wCA/x8AwP//BwD8/wAA/P8/AOD/BwDg//8AAP8/AAD+/wcA+P8BAPD/HwDA/w8AAP9/AAD+f8AH8P8BAPD/A38A/gcAgP8f/AcAAAAA/P/wPwAAAADg/4P/AQAAAID/H/wPAAAAAPz/4H8AAAAA4P8H/gMAAAAA/x/gDwAAAAD4/wA+AAAAAMD/BwAAAAAAAP8/AAAAAAAA+P8AAAAAAADA/wcAAAAAAAD+HwAAAAAAAPj/AAAAAAAAwP8DAAAAAAAA/h8AAAAAAAD4fwAAAAAAAMD/AwAAAAAAAP8PAAAAAAAA+H8AAAAAAADg/wEAAAAAAAD/BwAAAAAAAPw/AAAAAAAA4P8AAAAAAACA/wMAAAAAAAD+DwAAAAAAAPA/AAAAAAAAwP8AAAAAAAAA/wcAAAAAAAD8HwAAAAAAAOA/AAAAAAAAgP8AAAAAAAAA/gMAAAAAAAD4DwAAAAAAAOA/AAAAAAAAgP8AAAAAAAAA/gEAAAAAAAD4BwAAAAAAAOAfAAAAAAAAwD8AAAAAAAAA/wAAAAAAAAD8AwAAAAAAAPgHAAAAAAAA4A8AAAAAAACAPwAAAAAAAAB/AAAAAAAAAP4AAAAAAAAA+AMAAAAAAADwBwAAAAAAAOAPAAAAAAAAAB8AAAAAAAAAGAAAAAAAAAAA"],"clef-C":[67,98,"AAAAAAAAAADwf8AAAP4/AMD/Aw8A/v8PAP4feAD4//8B8P/AA/AH+D+A/wcewAcA/wf8P/AAPwDwf+D/gQf4AwD/B/8PPOB/APA/+H/gAf8HgP/D/wMP/H8A/D/+H3jg/wPA//H/wAP/PwD+n/8HHvj/AfD//D/wwP8PgP/v/4EH/n8A/H//Dzzg/wHg//t/4AH/DwD///8DD/A/APj//x94AP8AwP///8ADwAEA/v//Bx4AAADw//8/8AAAAID///+BBwAAAPz//w88AAAA4P//f+ABAAAA////Aw8AAAD4//8feAAAAMD/9//AAwAAAP6//wcegAEA8P/9P/AAHACA/+//gQfwAAD8P/8PPIAPAOD/+X/gAXwAAP/H/wMP4AMA/D/+H3iAPwDg//D/wAP8AwD/h/8HHuAfAPwf/D/wgP8B8H/g/4EH/D/A/wH/Dzzw////A/h/4IH///8PwP8DD/7//x8A/h94+H/wDwDw/8Dj/wEAAID/B/7/DwAAAPw/8P8/AAAA4P+B//8BAAAA/w/8/wcAAAD4f+D/PwAAAMD/A///AwAAAP4f+P8fAAAA8P/A//8BAACA/wce/w8AAAD8P/Dw/8AfAOD/gQf///8PAP8PPPD///8B+H/gAf///z/A/wMP+H+A/wP+H3jA/wD4P/D/wAP8A4D/g/8HHuAfAPg//D/wAH8AwP/h/4EH8AEA/h//DzyADwDg//l/4AF8AAD/z/8DD+ABAPh//h94AA4AwP/3/8ADMAAA/r//Bx4AAADw//0/8AAAAID/7/+BBwAAAPz//w88AAAA4P//f+ABAAAA////Aw8AAAD4//8feAAAAMD////AAwAAAP7//wceAA4A8P//P/AA/gGA////gQf4HwD8//8PPOD/AeD//3/gAf8PAP/f/wMP/P8A+P/+H3jg/wfA//f/wAP/PwD+n/8HHvj/AfD//D/wwP8HwP/j/4EH/j8A/h//Dzzg/wDwf/h/4AH/A8D/wf8DD/AHAP4P/h94gB8A+D/w/8AD+ADgf4D/Bx6AP8D/Afw/8ADw//8D4P+BBwD//wcA/g8YAMD/BwAAAAAAAAAAAAA="],"rest-quarter":[26,72,"EAAA4AEAgA8AAH4AAPABAMAPAAB+AADwAwDAHwAA/gAA+AcAwD8AAP8AAPwHAOA/AID/AQD+DwD4fwDg/wGA/w8A/38A/P8B8P8D4P8PgP8fAP8/AP7/APz/Afj/B+D/D8D/PwD/fwD8/wHg/weA/w8A/D8A4P8AAP8DAPgPAOA/AAD/AAD4AwDAHwAAfwAA+AEAwA8AAH8A8PwB8P8P4P9/wP//A///D/7/f/j///P//9///3//P4D/fwDg/wCA/wEA/gcA8B8AgH8AAP4BAPAHAIA/AAD8AADgBwAAPwAA+AEAwAcAABwA"],"rest-8th":[24,41,"8AEA+ANg/Afw/g94/w98/x9+/x9///8///8//v8//P8f+D8f8AcfAAAfAIAPAIAPAIAPAMAPAMAHAMAHAOAHAOADAOADAPADAPADAPgBAPgBAPgBAPwAAPwAAPwAAP4AAH4AAH4AAH8AAD8AAD8AAD8AgD8AgB8AAA8A"],"rest-16th":[31,65,"APgAAAD/ATjA/wEO4P+AB/j/4AP8f/gB/j9/AP//P4D//x+A//8PgP//A4D/8QEAP/gAAAB8AAAAHwAAgA8AAMAHAADwAQAA+AAAAHwAAAAeAACADwAAwAcAAOAD8AH4AP4DfID/Az/A/4EP8P/BB/j/8AP8f/wA/v9/AP7/PwD//w8A//8HAP/3AwB++AEAAHwAAAA/AACAHwAAwAcAAPADAAD4AQAAfAAAAD8AAIAfAADADwAA8AMAAPgBAAD8AAAAPwAAgB8AAMAPAADwAwAA+AEAAPwAAAA/AACAHwAAwA8AAPAHAAD4AQAA/AAAAH8AAIAfAACABwAA"],"acc-sharp":[25,68,"AAAAAAAOAAAcAAA4AABwABzgADjAAXCAA+AAB8ABDoADHAAHOAAOcAAc4AA4wD9wgH/ggP/Agf+B4/8D//8H/v8P//+f//+f//8P//8P/v8P/H8c+D848B9w4B/gwD3AAXCAA+AABsABDoADHAAHOAAOcAwc4B84wD9wwH/gwP/A4f+B//+D///H///P///H//+D//8D//8H/h8O/A8c+Ac48A9wYBzgADjAAXCAA+AAB8ABDoADHAAHOAAOcAAc4AA4wAFwAADgAADAAQCAAwAAAAAA"],"acc-flat":[23,60,"AAAADgCABwDAAwDgAQDwAAB4AAA8AAAeAAAPAIAHAMADAOABAPAAAHgAADwAAB4AAA8AgAcAwAMA4AEA8AAAeAAAPAAAHgAADwCABwDAAwDggQ/w8B94/D/8/z/+/x//4Z8/4M8P8OcD8PcA+HsA/DwAfh4APw+AnwfgxwPw4wH88AB+eIAfPOAHHvgBD36Ahx/A9wfg/wDgPwDwDwD4AQB8AAAeAAADAAAAAAA="],"acc-natural":[16,66,"BgAPAA8ADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA8AD8AP+I/////////////////////////wH/AP8A/wD/AP8A/wD/AP8A/wD/AP+A/+j/////////////////////////9/8A/wA/AA8ADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA4AAA"],"head-filled":[30,24,"AAB/AAD8fwDA/38A/P8/gP//D/D//wf+///B//9/8P//H/7//8f////x//8//P//j////+P//3/4//8P/v//g///f+D//wfw//8A/P8fAP7/AQD+HwAAfgAA"],"head-half":[29,25,"AMA/AAD/PwD4/w/A//8D/D/4wP8AHvwHgMN/AHD8AwCOHwDA+QEAPB8AwOcBAHweAMDPAwD8OADgHwcA/uEA8D8cgP8DB/w/4PP/A/j/HwD+/wAA/wEAAAAAAA=="]};

module.exports = { dewarpPage, dewarpReading, applyOpsJs, readHeaders, precleanPage, pageQuality, precleanPlan, precleanStats, readTime, readClefAt, makeJsApi };
