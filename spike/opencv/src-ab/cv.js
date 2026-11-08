'use strict';
// Optional OpenCV.js fallback symbol reader (default off). Runs after the classical page
// assembly and only where that reading is missing:
//   - numbered time signatures: the header finds the glyph but never reads its numbers; each
//     digit is matched against Bravura templates (cv.matchTemplate, TM_CCOEFF_NORMED) scaled to
//     the staff space. A time signature the header missed altogether (two stacked digits right
//     after the clef / key) is read the same way, and "heads" found on it are dropped.
//   - clefs the header could not read (clef guessed): the glyph at the staff start is matched
//     against the G / F / C clef templates; a C clef takes its line from its centre.
// Measured in docs/spike-opencv.md (templates beat the shape/HOG classifiers on these glyphs and
// need no training data). Usage, like ml.js:
//   node:    conv = wrapConverter(omr.createConverter(opts), createNodeCv())
//   browser: conv = wrapConverter(omr.createConverter(opts), createBrowserCv({ base: 'assets/' }))
// OpenCV.js: @techstark/opencv-js 4.10.0-release.1 (Apache-2.0), patched so embind never calls
// new Function (the artifact CSP has no unsafe-eval): spike/opencv/tools/patch-noeval.js.
// Templates: glyphs of the Bravura font (SIL OFL 1.1, Steinberg Media Technologies), rendered at
// 24 px per staff space, 1 bit per pixel.
const { labelComponents } = require('./cc');

const BANK_SP = 24;
const DIGITS = ['digit-0', 'digit-1', 'digit-2', 'digit-3', 'digit-4', 'digit-5', 'digit-6', 'digit-7', 'digit-8', 'digit-9'];
const NOT_DIGITS = ['rest-quarter', 'rest-8th', 'rest-16th', 'acc-sharp', 'acc-flat', 'acc-natural', 'head-filled', 'head-half', 'time-C'];
const CLEFS = ['clef-G', 'clef-F', 'clef-C'];
const SCALES = [0.85, 1, 1.15];

// ---------------------------------------------------------------- loading
// the emscripten Module is a thenable: resolving a promise with it loops, so it is wrapped
function moduleReady(m) {
  return new Promise((resolve) => {
    const done = () => { if (typeof m.then === 'function') delete m.then; resolve({ cv: m }); };
    if (m.Mat) done(); else m.onRuntimeInitialized = done;
  }).then(w => w.cv);
}

function createNodeCv(opts = {}) {
  const path = require('path');
  const tries = [opts.path, process.env.OPENCV_JS, path.join(__dirname, '../assets-src/opencv/opencv-4.10.0-noeval.js'),
    path.join(__dirname, '../../spike/opencv/vendor/opencv-4.10.0-noeval.js')].filter(Boolean);
  let p = null;
  return () => (p ||= (async () => {
    let err;
    for (const f of tries) { try { return makeApi(await moduleReady(require(f))); } catch (e) { err = e; } }
    throw new Error('opencv.js not found (' + (err && err.message) + ')');
  })());
}

// page or worker: the patched build is fetched from the page's own assets and run from a blob:
// URL (the artifact CSP allows blob: scripts, not 'self' ones)
function createBrowserCv(opts = {}) {
  const url = (opts.base || 'assets/') + (opts.file || 'opencv-4.10.0-noeval.js');
  let p = null;
  return () => (p ||= (async () => {
    const g = typeof self !== 'undefined' ? self : window;
    if (!g.cv || !g.cv.Mat) {
      const r = await fetch(url);
      if (!r.ok) throw new Error('opencv.js: HTTP ' + r.status);
      const blobUrl = URL.createObjectURL(new Blob([await r.blob()], { type: 'text/javascript' }));
      if (typeof importScripts === 'function') importScripts(blobUrl);
      else await new Promise((ok, no) => { const s = document.createElement('script'); s.src = blobUrl; s.onload = ok; s.onerror = () => no(new Error('opencv.js failed to load')); document.head.appendChild(s); });
    }
    return makeApi(await moduleReady(g.cv));
  })());
}

// ---------------------------------------------------------------- matching
function makeApi(cv) {
  const tpl = {};
  for (const [name, [w, h, b64]] of Object.entries(BANK)) {
    const bits = typeof atob === 'function' ? Uint8Array.from(atob(b64), c => c.charCodeAt(0)) : new Uint8Array(Buffer.from(b64, 'base64'));
    const m = new cv.Mat(h, w, cv.CV_8U);
    for (let i = 0; i < w * h; i++) m.data[i] = (bits[i >> 3] >> (i & 7)) & 1 ? 255 : 0;
    tpl[name] = m;
  }
  const cache = new Map();
  const scaled = (name, k) => {
    const key = name + '@' + k.toFixed(3);
    let t = cache.get(key);
    if (!t) {
      const g = tpl[name];
      t = new cv.Mat();
      cv.resize(g, t, new cv.Size(Math.max(3, Math.round(g.cols * k)), Math.max(3, Math.round(g.rows * k))), 0, 0, cv.INTER_AREA);
      cv.threshold(t, t, 127, 255, cv.THRESH_BINARY);
      if (cache.size > 400) { for (const v of cache.values()) v.delete(); cache.clear(); }
      cache.set(key, t);
    }
    return t;
  };
  // glyph image {w, h, data (0/1)} -> {name: best score}; the score is the best normalised
  // correlation over small shifts and three scales, damped when the template covers much less
  // than the glyph (a small template must not win inside a big glyph)
  function scores(img, sp, names) {
    const out = {};
    const k0 = sp / BANK_SP, res = new cv.Mat(), padded = new Map();
    try {
      for (const name of names) {
        let best = -1;
        for (const f of SCALES) {
          const t = scaled(name, k0 * f);
          if (t.cols > 2.2 * img.w + 4 || t.rows > 2.2 * img.h + 4 || t.cols * 3 < img.w || t.rows * 3 < img.h) continue;
          const pad = Math.max(t.cols, t.rows) >> 1;
          let pm = padded.get(pad);
          if (!pm) {
            pm = new cv.Mat(img.h + 2 * pad, img.w + 2 * pad, cv.CV_8U, new cv.Scalar(0));
            const W = img.w + 2 * pad;
            for (let y = 0; y < img.h; y++) for (let x = 0; x < img.w; x++) if (img.data[y * img.w + x]) pm.data[(y + pad) * W + x + pad] = 255;
            padded.set(pad, pm);
          }
          cv.matchTemplate(pm, t, res, cv.TM_CCOEFF_NORMED);
          const sc = cv.minMaxLoc(res).maxVal * Math.sqrt(Math.min(1, (t.cols * t.rows) / (img.w * img.h)));
          if (sc > best) best = sc;
        }
        out[name] = best;
      }
    } finally { res.delete(); for (const m of padded.values()) m.delete(); }
    return out;
  }
  const best = (sc, names) => names.reduce((a, n) => (sc[n] > sc[a] ? n : a), names[0]);
  return { cv, scores, best };
}

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
function numberGroups(g, sp) {
  const groups = [];
  for (const c of g.comps.slice().sort((p, q) => p.x0 - q.x0)) {
    const last = groups[groups.length - 1];
    if (last && c.x0 <= last.x1) { last.x1 = Math.max(last.x1, c.x1); last.y0 = Math.min(last.y0, c.y0); last.y1 = Math.max(last.y1, c.y1); }
    else groups.push({ x0: c.x0, x1: c.x1, y0: c.y0, y1: c.y1 });
  }
  const run = [];
  for (const d of groups) {
    if (run.length && (d.x0 - run[run.length - 1].x1 > 0.6 * sp || d.x1 - run[0].x0 > 3.6 * sp)) break;
    run.push(d);
  }
  return run;
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
  const run = numberGroups(g, sp);
  if (!run.length) return null;
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
  const top = readNumber(api, R, { x0, x1, y0: l0 - 0.7 * sp, y1: l2 + 0.2 * sp, inner: inRow(l0 - 0.6 * sp, l2) }, sp, minScore);
  if (!top) return null;
  const bot = readNumber(api, R, { x0, x1, y0: l2 - 0.2 * sp, y1: l4 + 0.7 * sp, inner: inRow(l2, l4 + 0.6 * sp) }, sp, minScore);
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

// ---------------------------------------------------------------- page refinement
// entry: {fr, asm} from omr createConverter.addPage. Changes asm in place; returns counts.
function refineEntry(entry, api, opts = {}, stats = {}) {
  const R = entry.fr && entry.fr.R;
  if (!R || !entry.asm) return stats;
  const minScore = opts.minScore ?? 0.45;
  for (const sy of entry.asm.systems) {
    // time signatures only at the top of a page: later systems carry meter changes, which the
    // score does not model (one meter per piece), and a change read as the piece's meter is worse
    // than the meter inferred from the bars
    const timeOk = sy === entry.asm.systems[0];
    for (const s of sy.staves) {
      const st = s.st, sp = st.space || entry.fr.ss, h = s.hdr;
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

// wraps an omr converter (createConverter) like ml.wrapConverter: every page entry is refined
// after the classical reading; getCv is a function returning a promise of the matcher
function wrapConverter(conv, getCv, opts = {}) {
  const stats = { pages: 0, ms: 0 };
  const warnings = [];
  let off = false;
  return Object.assign({}, conv, {
    async addPage(gray, i, n) {
      const entry = await conv.addPage(gray, i, n);
      if (!entry || off) return entry;
      const t0 = Date.now();
      try {
        const api = await getCv();
        for (const e of entry.spread && entry.spread.length ? entry.spread : [entry]) refineEntry(e, api, opts, stats);
        stats.pages++;
      } catch (err) {
        off = true;
        warnings.push(`The OpenCV symbol fallback could not start (${(err && err.message) || err}); the classical reading is kept.`);
      }
      stats.ms += Date.now() - t0;
      return entry;
    },
    finish() {
      const r = conv.finish();
      if (warnings.length) r.warnings = warnings.concat(r.warnings || []);
      r.cv = Object.assign({}, stats);
      return r;
    },
    cvStats: stats,
  });
}

const BANK = {"digit-0":[43,48,"AAD8AwAAAPx/AAAA+P8PAADwH/8BAMB/8D8AAP8B/wMA/g/wPwDwP4D/AcD/AfwfAP8HwP8B/D8A/h/g/wHw/4D/BwD/D/w/APh/4P8BwP+D/w8A/j/8fwDw/+H/A4D/D/8fAPz//H8AwP/n/wMA/j//HwDw//n/AID/z/8HAPx//j8A4P/z/wEA/5//DwD4//x/AMD/5/8HAP4//z8A+P/x/wHA/4f/DwD+P/x/APD/wf8DgP8H/h8A/D/g/wHw/wH/D4D/B/B/APw/gP8H8P8A+D+A/wOA/wP+DwD8H/B/AID/wf8BAPi//wcAgP//DwAA+P8/AAAA/j8AAACAfwAA"],"digit-1":[29,48,"APh/AID/HwD4/wMA/38A4P8PAP7/AcD/PwD8/weA//8A+P8fAP//A/D/fwD+/w/A//8B/P8/gO//B/j8/wCf/x/w8f8DPv5/4MP/Dzz4/4EH/z944P8HD/z/AID/HwDw/wMA/n8AwP8PAPj/AQD/PwDg/wcA/P8AgP8fAPD/AwD+fwDA/w8A+P8BAP8/AOD/BwD8/wCA/x8A8P8DAP9/APD/P8D//x/8//8D//9/"],"digit-2":[40,50,"AAAAAAAA8P8PAAD+/38AgB/A/wHABwD/A+ADAP8P8AMA/h/4BwD+H/wPAPw//D8A/H/+fwD8f/7/APx//v8A/P/+/wD8//7/APz//v8A/P/+/wD+//z/AP7//P8A/v/4fwD/f/B/AP9/4D+A/z+AD4D/HwAAwP8PAADg/wcAAPD/AQAA+H8AAAD8DwAAAP4BAACAfwAAAMAfAAAA8AcAAAD4AQAAAPwAAGAA/x4AYID//wNwwP//H3DA////fOD///9/8P///z/w////P/j///8/+P///x/8////H/zH//8P/gD//wd+APz/Az4A+P8BHADAfwAIAAAAAA=="],"digit-3":[38,48,"AMA/AAAA/v8AAPD//wAA//D/AOAP4P8A/AHwf4B/APg/4H8A/g/8fwD/B/8fwP/B/w/wf/D/A/w//P8A/w//P8D/gf8P8H/g/wH+H/B/gP8H+A/w/wBwAPwfAADA/wMAAPw/AADg/wEAgP8/AADw/z8AAPj/fwAAAP9/AAAA/z8AAAD/HwAAwP8P8AHg/wP/AfD/4f8A/H/8fwD/H/8fwP/v/wfw//v/Afx//v8A/5//H8D/5/8H8P/5/wD+P/w/gP8P/w/w/4H/Af4/4P/A/wfw////APD//w8A8P9/AADg/wMA"],"digit-4":[42,49,"AAAAAAAAAP//AAAA/v8DAAD4/wcAAOD/HwAAgP8/AAAA/n8AAAD4/wEAAPD/AwAAwP8HAAAA/x8cAAD8P3gAAPh/8AEA4P/gBwCA/4MfAAD/B38AAPwP/gEA+B/8BwDgf/gfAMD/8H8AAP/B/wEA/oP/BwD4B/8fAPAf/H8AwD/w/wGAf8D/BwD+AP8fAPwB/H8A+APw/wHgB8D/B8APAP8fgB8A/H8A///////9//////f/////n/////8/AADw/wEAAMD/BwAAAP8fAAAA/H8AAADw/wEAAMD/BwAAAP8fAAAA/n8AAAD8/wMAAP7/fwAA/P//AwDw//8PAMD//x8A"],"digit-5":[37,48,"AAAAAAD+//8f4P///wP8//9/gP///w/w////AP7//x/A////Afj//x8A////AeD//w8APPgHAIAHAAAA8AAAAAAeAAAAwAEAAAA4AAAAAAf+fwDg+P8/APz//w+AP/D/B/gD+P8BHwD8P+ABAP8PGADg/wMAAPh/AAAA/x8AAMD/A/4A+H/wfwD/H/4f4P/j/wP8f/7/gP/P/x/w//n/A/4//3/A/+f/D/j//P+B/4//H/D/8f8B/h/8H+D/g/8B/D/gH+D/A/wH/j8A////A4D//z8A4P//AADA/wMA"],"digit-6":[39,48,"AAD4AwAAwP8fAAD4wz8AAP/APwDAP+A/APgP+D8A/gP+HwD/Af8fwP/A/w/wP+D/B/gf8P8B/g/4/wD/B/h/wP8D/B/g/wD8B/h/APgA/D8AAAD+HwAAAP8PAADA/wf4AOD/g/8B8P/x/wP4//3/B/z///8H/v/H/wf//8D/h/9/wP/H/x/g/+P/D+D/8/8D8P/x/wH4//j/APx//H8A/H/+PwD+P/4fAP8P/w+A/4f/B8D/g/8D4P+B/wH4f8D/APw/wP8A/g/Af4D/B+B/wP8BwD/wfwDAP/wfAMD//wMAgP9/AAAA/wMA"],"digit-7":[39,48,"APADAAAA/g8AXMD/HwBu8P8fgHf8/x/A+///H/D9//8f+P7//z9+/////7//////3//////nn/////MD////+QD+/388AP7/Px4A/P8fBwD854cDAPDxwwEAAPxgAAAAfiAAAIA/AAAA4A8AAAD4BwAAAP4BAACA/wAAAOA/AAAA+B8AAAD+DwAAgP8DAADg/wEAAPj/AAAA/j8AAID/HwAAwP8PAADw/wMAAPz/AQAA/v8AAID/fwAAwP8/AADw/x8AAPj/BwAA/v8DAAD//wEAgP//AADA/38AAOD/PwAA8P8fAAB4gAcA"],"digit-8":[39,50,"AAA/AAAA+P8HAID//w8A8D/wHwD8A8A/AH8AgB/AHwCAH/APAIAf/AMAwA/+AQDAB/8BAOCH/wAA8MN/AAD48X8AAPzw/wAAPvj/AIAf/P8D4A/+/wf4A///H/4A////f4D///8PgP///wOA////B4D///8HgP///wcA////B4D///8H4P///wf8+f//Az/w///BD+D///EDwP///ACA/39+AAD/vx8AAP/fDwAA/+8DAID/8wEAgP/5AQDA//wAAOB/fgAA8B9+AAD4Dz8AAP4DPwAA/wB/AMB/AP8A+A8A/4f/AwD+/38AAPz/DwAA4H8AAA=="],"digit-9":[39,48,"AMA/AAAA/v8BAMD//wcA+D/8BwD+D/wHgP8H/AfA/wH+B/D/AP4H/D8A/wP+H4D/A/8PwP/B/wfg/+H/A+D/8P8B8P/4/wD4f/x/AP4//j8A/z//H4D/H/8PwP+P/w/g/8f/B/j/w/8H/v/B/wf//8D/5/9/4P///z/A/3//H8D/j/8PgP/B/wcAAOD/AwAA8P8BAAD4/wAAAPw/AD8A/h/AfwD/D/A/gP8D/D/A/wH/H/B/gP8P+D/A/wf8D+D/A/4D8P+B/wH4f8B/APgf8B8A/A/4BwD8A/4AAPzDPwAA+P8DAADgPwAA"],"time-C":[41,50,"AAAAAAAAAP4HAAAA/38AAID/gAcAwH8AHADAfwBwAMA/AOABwH8AwAfAfwDAD8B/APA/gP8A8H+A/wHw/4H/AfD/A/8D4P8H/gfA/w/+B4D/H/wPAP8//B8A/n/4PwD8f/B/APD/4P8A4P/g/wGA/8D/AwB8gP8HAAAA/w8AAAD+HwAAAPw/AAAA+H8AAADw/wAAAOD/AQAAnP8DAAA4/wcAAHD+HwAA4Pw/AADA8X8AAIDj/wAAAMP/AwAAB/8HAAAO/g8AAA74PwAAHOB/AAAcwP8BADwA/wcAPAD8HwA8APB/AD4AwP8DPwAA/v8fAAD4/w8AAID/AwAAAAAAAAA="],"time-cut":[41,70,"AAAOAAAAABwAAAAAOAAAAABwAAAAAOAAAAAAwAEAAACAAwAAAAAHAAAAAA4AAAAAHAAAAAB4AAAAAPg/AAAA/v8DAAD/Bx4AAP8HcACA/wfAA4D/D4APgP8fAB8A/zkAfwD/ccD/AP/j4P8D/sPB/wf+h8P/D/wPh/8f/B8O/z/4Hxz+f/A/OPz/8H9w+P/h/+Dw/8H/wcH/g/+DA/+D/wcH/AP/Dw7AAP4fHAAA/D84AAD4f3AAAPD/4AAA4P/BAQDA/4MDAID/BwcAcP4PDgDg/B8cAMD5fzgAgPP/cAAAx//hAACG/8MBAA7+jwMAHPwfBwAY8D8OADjg/xwAMID/OQBwAP5/AHAA+P8AeADg/wH8AID/B34AAP7/fwAA8P8/AACA/w8AAAB8AAAAAHAAAAAA4AAAAADAAQAAAIADAAAAAAcAAAAADgAAAAAcAAAAADgAAAAAcAAAAADgAAAAAAAAAAA="],"clef-G":[66,170,"AAAAAAAAAAAAAAAAAPAAAAAAAAAA4AcAAAAAAADAPwAAAAAAAID/AQAAAAAAAP8PAAAAAAAA/j8AAAAAAAD8/wEAAAAAAPD/BwAAAAAA4P8/AAAAAACA//8AAAAAAAD//wcAAAAAAP7/HwAAAAAA+P//AAAAAADg//8DAAAAAMD//w8AAAAAAP8HfgAAAAAA/AfwAQAAAAD4D4AHAAAAAOAfAB4AAAAAgH8AcAAAAAAA/gDAAwAAAAD8AQAPAAAAAPAHADwAAAAAwA8A8AAAAAAAPwDAAwAAAAB8AAAPAAAAAPgBAD4AAAAA4AcA+AAAAACAHwDgAwAAAAA+AIAPAAAAAPgAAD8AAAAA4AMA/AAAAACADwD4AwAAAAA+AOAHAAAAAPgAwB8AAAAA4AOAfwAAAACABwD+AQAAAAAeAPwHAAAAAHgA+A8AAAAA4AHwPwAAAACAB+D/AAAAAAAewP8BAAAAAHiA/wcAAAAA4AH/DwAAAAAAD/4/AAAAAAA8/P8AAAAAAPD4/wEAAAAAwPP/BwAAAAAA//8PAAAAAAD8/x8AAAAAAPD/fwAAAAAAwP//AAAAAACA//8BAAAAAAD//wcAAAAAAP7/DwAAAAAA/v8fAAAAAAD8/z8AAAAAAPj//wAAAAAA8P//AQAAAADg//8DAAAAAMD//wcAAAAAgP//DwAAAAAA//8fAAAAAAD+/z8AAAAAAPz/fwAAAAAA+P//AQAAAADw//8HAAAAAOD//zwAAAAAgP//8QAAAAAA///BAwAAAAD+/wMPAAAAAPz/BzwAAAAA+P8P8AEAAADg/x+ABwAAAMD/PwAeAAAAgP9/AHgAAAAA/v8A4AEAAAD8/wGABwAAAPD/AwA+AAAA4P8HAPAAAACA/w8AwAMAAAD/HwCA/w8AAPw/AAD//wMA+H8AgP//PwDg/wEA////AYD/AwD///8fAP8HAP7///8A/B8A/P///wfwPwD4////P8B/APD/////gP8B4P////8H/geA/////z/4DwD//////+A/APz/////h/8A+P/z4P8f/gHg/8MD/v/4B4D/Aw/w/+MfAP4HPAD/j38A/A/gAfg//gHwH4AHwP/5B8A/AB4A/+cfAP8AeAD4nz8A/AHgAcB//gHwB4AHAP/xB4AfADwA/McfAH4A8ADgH38A+AHAA4B/+AHgBwAPAP7hBwAfADwA+Ic/AHwA8ADgD/wA4AOAB4A/8AOADwAeAP6AHwB8AHgA+AN+AOAD4AHgB/ADAB+AB8AfgA8A+AEeAD8AfgCAD/AA/gDwAwB4wAP4AYAfAAAAD/ADAPwAAAA84AcA4AcAAPDADwAAfwAAwIMfAAD4BwAAnj8AAIB/AAD4fwAAAPgPAOB/AAAAwP8f8P8AAAAA/P//fwAAAACA////AAAAAADA/+8DAAAAAAAAAA8AAAAAAAAAPAAAAAAAAADwAAAAAAAAAMADAAAAAAAAAB8AAAAAAAAAeAAAAAAAAADgAQAAAAAAAIAHAAAAAAAAAB4AAAAAAAAAeAAAAAAAAADgAQAAAAAAAIAPAAAAAAAAADwAAAAA/gMA8AAAAAD8PwDAAwAAAPj/AQAPAAAA8P8HADwAAADg/z8A8AAAAID//wDAAwAAAP//BwAPAAAA/P8fADwAAADw/38A8AAAAMD//wHAAwAAAP//BwAPAAAA/P8fADwAAADw/38A+AAAAMD//wDgAQAAAP//A4AHAAAA/P8HAB8AAADg/w8APAAAAID/DwD4AAAAAPwPAPABAAAA8A8A4AcAAACAPwDADwAAAAD8AeAfAAAAAOA/8D8AAAAAAP7/PwAAAAAA8P8/AAAAAAAA/B8AAAAAAAAAAAAAAAA="],"clef-F":[67,87,"AAAAAAAAAAAAAID/BwAAAAAAwP//AwAAAADA//9/AAAAAID/4P8PAAAAAP4A8P8BAAAA+AAA/h8AAADgAwDg/wEAAIAHAAD+HwAAAB4AAPD/AcAH+AAAAP8fgH/gAwAA8P8B/AcPAACA/w/wP3wAAAD4/4D/4QMAAMD/B/yPHwAAAP5/4H/8AAAA4P8D/uP/HwAA/z/wj///AQD4/wE+/P8/AMD/DwDg//8BAP5/AAD//x8A4P8HAPj//wAA/z8AwP//DwD4/wEA/v9/AMD/DwDw//8DAP5/AAD//x8A8P8DAPj//wCA/x8AwP//BwD8/wAA/P8/AOD/BwDg//8AAP8/AAD+/wcA+P8BAPD/HwDA/w8AAP9/AAD+f8AH8P8BAPD/A38A/gcAgP8f/AcAAAAA/P/wPwAAAADg/4P/AQAAAID/H/wPAAAAAPz/4H8AAAAA4P8H/gMAAAAA/x/gDwAAAAD4/wA+AAAAAMD/BwAAAAAAAP8/AAAAAAAA+P8AAAAAAADA/wcAAAAAAAD+HwAAAAAAAPj/AAAAAAAAwP8DAAAAAAAA/h8AAAAAAAD4fwAAAAAAAMD/AwAAAAAAAP8PAAAAAAAA+H8AAAAAAADg/wEAAAAAAAD/BwAAAAAAAPw/AAAAAAAA4P8AAAAAAACA/wMAAAAAAAD+DwAAAAAAAPA/AAAAAAAAwP8AAAAAAAAA/wcAAAAAAAD8HwAAAAAAAOA/AAAAAAAAgP8AAAAAAAAA/gMAAAAAAAD4DwAAAAAAAOA/AAAAAAAAgP8AAAAAAAAA/gEAAAAAAAD4BwAAAAAAAOAfAAAAAAAAwD8AAAAAAAAA/wAAAAAAAAD8AwAAAAAAAPgHAAAAAAAA4A8AAAAAAACAPwAAAAAAAAB/AAAAAAAAAP4AAAAAAAAA+AMAAAAAAADwBwAAAAAAAOAPAAAAAAAAAB8AAAAAAAAAGAAAAAAAAAAA"],"clef-C":[67,98,"AAAAAAAAAADwf8AAAP4/AMD/Aw8A/v8PAP4feAD4//8B8P/AA/AH+D+A/wcewAcA/wf8P/AAPwDwf+D/gQf4AwD/B/8PPOB/APA/+H/gAf8HgP/D/wMP/H8A/D/+H3jg/wPA//H/wAP/PwD+n/8HHvj/AfD//D/wwP8PgP/v/4EH/n8A/H//Dzzg/wHg//t/4AH/DwD///8DD/A/APj//x94AP8AwP///8ADwAEA/v//Bx4AAADw//8/8AAAAID///+BBwAAAPz//w88AAAA4P//f+ABAAAA////Aw8AAAD4//8feAAAAMD/9//AAwAAAP6//wcegAEA8P/9P/AAHACA/+//gQfwAAD8P/8PPIAPAOD/+X/gAXwAAP/H/wMP4AMA/D/+H3iAPwDg//D/wAP8AwD/h/8HHuAfAPwf/D/wgP8B8H/g/4EH/D/A/wH/Dzzw////A/h/4IH///8PwP8DD/7//x8A/h94+H/wDwDw/8Dj/wEAAID/B/7/DwAAAPw/8P8/AAAA4P+B//8BAAAA/w/8/wcAAAD4f+D/PwAAAMD/A///AwAAAP4f+P8fAAAA8P/A//8BAACA/wce/w8AAAD8P/Dw/8AfAOD/gQf///8PAP8PPPD///8B+H/gAf///z/A/wMP+H+A/wP+H3jA/wD4P/D/wAP8A4D/g/8HHuAfAPg//D/wAH8AwP/h/4EH8AEA/h//DzyADwDg//l/4AF8AAD/z/8DD+ABAPh//h94AA4AwP/3/8ADMAAA/r//Bx4AAADw//0/8AAAAID/7/+BBwAAAPz//w88AAAA4P//f+ABAAAA////Aw8AAAD4//8feAAAAMD////AAwAAAP7//wceAA4A8P//P/AA/gGA////gQf4HwD8//8PPOD/AeD//3/gAf8PAP/f/wMP/P8A+P/+H3jg/wfA//f/wAP/PwD+n/8HHvj/AfD//D/wwP8HwP/j/4EH/j8A/h//Dzzg/wDwf/h/4AH/A8D/wf8DD/AHAP4P/h94gB8A+D/w/8AD+ADgf4D/Bx6AP8D/Afw/8ADw//8D4P+BBwD//wcA/g8YAMD/BwAAAAAAAAAAAAA="],"rest-quarter":[26,72,"EAAA4AEAgA8AAH4AAPABAMAPAAB+AADwAwDAHwAA/gAA+AcAwD8AAP8AAPwHAOA/AID/AQD+DwD4fwDg/wGA/w8A/38A/P8B8P8D4P8PgP8fAP8/AP7/APz/Afj/B+D/D8D/PwD/fwD8/wHg/weA/w8A/D8A4P8AAP8DAPgPAOA/AAD/AAD4AwDAHwAAfwAA+AEAwA8AAH8A8PwB8P8P4P9/wP//A///D/7/f/j///P//9///3//P4D/fwDg/wCA/wEA/gcA8B8AgH8AAP4BAPAHAIA/AAD8AADgBwAAPwAA+AEAwAcAABwA"],"rest-8th":[24,41,"8AEA+ANg/Afw/g94/w98/x9+/x9///8///8//v8//P8f+D8f8AcfAAAfAIAPAIAPAIAPAMAPAMAHAMAHAOAHAOADAOADAPADAPADAPgBAPgBAPgBAPwAAPwAAPwAAP4AAH4AAH4AAH8AAD8AAD8AAD8AgD8AgB8AAA8A"],"rest-16th":[31,65,"APgAAAD/ATjA/wEO4P+AB/j/4AP8f/gB/j9/AP//P4D//x+A//8PgP//A4D/8QEAP/gAAAB8AAAAHwAAgA8AAMAHAADwAQAA+AAAAHwAAAAeAACADwAAwAcAAOAD8AH4AP4DfID/Az/A/4EP8P/BB/j/8AP8f/wA/v9/AP7/PwD//w8A//8HAP/3AwB++AEAAHwAAAA/AACAHwAAwAcAAPADAAD4AQAAfAAAAD8AAIAfAADADwAA8AMAAPgBAAD8AAAAPwAAgB8AAMAPAADwAwAA+AEAAPwAAAA/AACAHwAAwA8AAPAHAAD4AQAA/AAAAH8AAIAfAACABwAA"],"acc-sharp":[25,68,"AAAAAAAOAAAcAAA4AABwABzgADjAAXCAA+AAB8ABDoADHAAHOAAOcAAc4AA4wD9wgH/ggP/Agf+B4/8D//8H/v8P//+f//+f//8P//8P/v8P/H8c+D848B9w4B/gwD3AAXCAA+AABsABDoADHAAHOAAOcAwc4B84wD9wwH/gwP/A4f+B//+D///H///P///H//+D//8D//8H/h8O/A8c+Ac48A9wYBzgADjAAXCAA+AAB8ABDoADHAAHOAAOcAAc4AA4wAFwAADgAADAAQCAAwAAAAAA"],"acc-flat":[23,60,"AAAADgCABwDAAwDgAQDwAAB4AAA8AAAeAAAPAIAHAMADAOABAPAAAHgAADwAAB4AAA8AgAcAwAMA4AEA8AAAeAAAPAAAHgAADwCABwDAAwDggQ/w8B94/D/8/z/+/x//4Z8/4M8P8OcD8PcA+HsA/DwAfh4APw+AnwfgxwPw4wH88AB+eIAfPOAHHvgBD36Ahx/A9wfg/wDgPwDwDwD4AQB8AAAeAAADAAAAAAA="],"acc-natural":[16,66,"BgAPAA8ADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA8AD8AP+I/////////////////////////wH/AP8A/wD/AP8A/wD/AP8A/wD/AP+A/+j/////////////////////////9/8A/wA/AA8ADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA4AAA"],"head-filled":[30,24,"AAB/AAD8fwDA/38A/P8/gP//D/D//wf+///B//9/8P//H/7//8f////x//8//P//j////+P//3/4//8P/v//g///f+D//wfw//8A/P8fAP7/AQD+HwAAfgAA"],"head-half":[29,25,"AMA/AAD/PwD4/w/A//8D/D/4wP8AHvwHgMN/AHD8AwCOHwDA+QEAPB8AwOcBAHweAMDPAwD8OADgHwcA/uEA8D8cgP8DB/w/4PP/A/j/HwD+/wAA/wEAAAAAAA=="]};

module.exports = { createNodeCv, createBrowserCv, wrapConverter, refineEntry, readTime, readClefAt, makeApi, moduleReady };
