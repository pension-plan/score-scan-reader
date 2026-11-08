// ---------------------------------------------------------------- pre-clean of degraded scans
// front() calls precleanPage(gray) before binarisation. A cheap page-quality check (plain JS,
// about 25 ms) decides which repairs the page needs; a page that looks clean is returned as the
// same object, so clean pages go through the pipeline exactly as before and OpenCV is never
// loaded for them. Repairs (OpenCV.js, loaded synchronously on first need: front() is
// synchronous):
//   flatten    uneven or dark paper (phone shots, yellowing, stains, book gutters): divide by a
//              background estimated with a large grey closing
//   descreen   halftone screens: Gaussian low-pass before thresholding
//   denoise    grain and salt-and-pepper noise: 3x3 median
//   despeckle  binary pages with loose specks (thin photocopies): drop tiny ink components
//   thin       thick photocopies (strokes fattened, heads filled in): grow the paper by 1 px
//   sharpen    blur and low resolution: unsharp mask
// docs/spike-opencv.md has the per-class measurements behind the thresholds.
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
  let mid = 0; for (let v = 61; v < 200; v++) mid += hist[v];
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
  return { thr, mid: mid / n, bgLow: (255 - pct(bg, 0.5)) / 255, bgUneven: (pct(bg, 0.95) - pct(bg, 0.05)) / 255, bgStd: pct(sd, 0.5),
    speck: speck / (n / 1e6), ss: sp.ss, lt: sp.lt, ltss: sp.ss > 0 ? sp.lt / sp.ss : 0 };
}

// which repairs a page needs, from its quality (empty: leave the page alone)
function precleanPlan(q, force) {
  if (force) return force.split(',').filter(Boolean);
  const ops = [];
  const binary = q.bgStd < 0.5 && q.mid < 0.03;
  if (q.speck > 20000 && q.bgStd > 4) ops.push('descreen');
  else if (q.speck > 800 && q.bgStd > 5) ops.push('denoise');
  if (q.mid > 0.15 && (q.bgUneven > 0.25 || q.bgLow > 0.12)) ops.unshift('flatten');
  if (binary && q.speck > 300) ops.push('despeckle');
  if (binary && q.ltss > 0.16) ops.push('thin');
  if (!binary && !ops.length && q.mid > 0.035 && q.bgStd < 3 && q.speck < 5 && q.ltss > 0.14) ops.push('sharpen');
  return ops;
}

// ---- OpenCV, loaded synchronously: node reads the file; a Web Worker fetches it with a
// synchronous XHR and runs it from a blob: URL (the artifact CSP allows blob: scripts). The
// embedded wasm is compiled with new WebAssembly.Module (synchronous; allowed in workers and
// node, not on a page's main thread, where the pre-clean is skipped). The patched build reads
// its module arguments from globalThis.__opencvModuleArgs.
let cvSync, cvTried = false;
const CV_FILE = 'opencv-4.10.0-noeval.js';
function wasmArgs(text) {
  const m = /data:application\/octet-stream;base64,([A-Za-z0-9+/=]+)/.exec(text);
  if (!m) throw new Error('no embedded wasm');
  const bytes = typeof Buffer !== 'undefined' ? Buffer.from(m[1], 'base64') : Uint8Array.from(atob(m[1]), c => c.charCodeAt(0));
  return { instantiateWasm(imports, ok) { const mod = new WebAssembly.Module(bytes); const inst = new WebAssembly.Instance(mod, imports); ok(inst, mod); return inst.exports; } };
}
function loadCvSync() {
  if (cvTried) return cvSync;
  cvTried = true;
  try {
    const g = typeof globalThis !== 'undefined' ? globalThis : self;
    if (typeof window === 'undefined' && typeof importScripts !== 'function' && typeof require === 'function' && typeof process !== 'undefined' && process.versions && process.versions.node) {
      const fs = require('fs'), path = require('path');
      const tries = [process.env.OPENCV_JS, path.join(__dirname, '../dist/assets', CV_FILE), path.join(__dirname, '../assets-src/opencv', CV_FILE)].filter(Boolean);
      const f = tries.find(p => fs.existsSync(p));
      if (!f) return (cvSync = null);
      g.__opencvModuleArgs = wasmArgs(fs.readFileSync(f, 'utf8'));
      cvSync = require(f);
    } else if (typeof importScripts === 'function' && typeof XMLHttpRequest !== 'undefined') {
      const base = g.OMR_ASSET_BASE || 'assets/';
      const x = new XMLHttpRequest();
      x.open('GET', base + CV_FILE, false); x.send();
      if (x.status !== 200 && x.status !== 0) return (cvSync = null);
      g.__opencvModuleArgs = wasmArgs(x.responseText);
      importScripts(URL.createObjectURL(new Blob([x.responseText], { type: 'text/javascript' })));
      cvSync = g.cv;
    } else return (cvSync = null);
    if (cvSync && typeof cvSync.then === 'function') delete cvSync.then;
    if (!cvSync || !cvSync.Mat) cvSync = null;
  } catch (e) { cvSync = null; }
  return cvSync;
}

function applyOps(cv, gray, ops, q) {
  const { width: w, height: h } = gray;
  let m = new cv.Mat(h, w, cv.CV_8U); m.data.set(gray.data);
  const swap = (o) => { m.delete(); m = o; };
  const ss = q.ss > 4 ? q.ss : 16;
  for (const op of ops) {
    if (op === 'flatten') {
      // paper estimate: grey closing (ink is darker than the paper around it) on a 4x smaller
      // copy, smoothed, back to full size; the page is divided by it
      const sm = new cv.Mat(), bg = new cv.Mat(), up = new cv.Mat(), o = new cv.Mat();
      cv.resize(m, sm, new cv.Size(Math.max(1, w >> 2), Math.max(1, h >> 2)), 0, 0, cv.INTER_AREA);
      const k = Math.max(3, Math.round(ss * 0.8) | 1);
      const se = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(k, k));
      cv.morphologyEx(sm, bg, cv.MORPH_CLOSE, se);
      cv.GaussianBlur(bg, bg, new cv.Size(0, 0), k / 2);
      cv.resize(bg, up, new cv.Size(w, h), 0, 0, cv.INTER_LINEAR);
      cv.divide(m, up, o, 255);
      se.delete(); sm.delete(); bg.delete(); up.delete(); swap(o);
    } else if (op === 'descreen') {
      const o = new cv.Mat(); cv.GaussianBlur(m, o, new cv.Size(0, 0), Math.max(1, ss / 14)); swap(o);
    } else if (op === 'denoise') {
      const o = new cv.Mat(); cv.medianBlur(m, o, 3); swap(o);
    } else if (op === 'median5') {
      const o = new cv.Mat(); cv.medianBlur(m, o, 5); swap(o);
    } else if (op === 'despeckle') {
      // ink components of at most a few pixels become paper
      const inv = new cv.Mat(), lab = new cv.Mat(), st = new cv.Mat(), cen = new cv.Mat();
      cv.threshold(m, inv, q.thr, 255, cv.THRESH_BINARY_INV);
      const nl = cv.connectedComponentsWithStats(inv, lab, st, cen, 8, cv.CV_32S);
      const maxA = Math.max(2, Math.round(0.012 * ss * ss)), small = new Uint8Array(nl);
      for (let i = 1; i < nl; i++) if (st.intAt(i, cv.CC_STAT_AREA) <= maxA) small[i] = 1;
      const L = lab.data32S, d = m.data;
      for (let i = 0; i < L.length; i++) if (small[L[i]]) d[i] = 255;
      inv.delete(); lab.delete(); st.delete(); cen.delete();
    } else if (op === 'thin') {
      // thicken the paper by one pixel: strokes thin, filled-in heads open up again
      const o = new cv.Mat(), se = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(3, 3));
      cv.dilate(m, o, se); se.delete(); swap(o);
    } else if (op === 'thin2') {
      const o = new cv.Mat(), se = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(2, 2));
      cv.dilate(m, o, se); se.delete(); swap(o);
    } else if (op === 'sharpen') {
      const bl = new cv.Mat(), o = new cv.Mat();
      cv.GaussianBlur(m, bl, new cv.Size(0, 0), Math.max(1, ss / 8));
      cv.addWeighted(m, 2.0, bl, -1.0, 0, o);
      bl.delete(); swap(o);
    } else if (op === 'close') {
      // thin photocopies: rejoin broken strokes
      const o = new cv.Mat(), se = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(2, 2));
      cv.erode(m, o, se); se.delete(); swap(o);
    }
  }
  const out = { width: w, height: h, data: new Uint8Array(m.data) };
  m.delete();
  return out;
}

const precleanStats = { pages: 0, cleaned: 0, ms: 0, ops: {} };
// gray page -> the same page (clean, or OpenCV unavailable) or a repaired copy
function precleanPage(gray, opts = {}) {
  const env = typeof process !== 'undefined' && process.env ? process.env : {};
  if (opts.preclean === false || env.OMR_PRECLEAN === 'off') return gray;
  if (!gray || !gray.data || gray.width < 64 || gray.height < 64) return gray;
  const t0 = Date.now();
  precleanStats.pages++;
  const q = pageQuality(gray);
  const ops = precleanPlan(q, env.OMR_PRECLEAN_OPS);
  if (!ops.length) return gray;
  const cv = loadCvSync();
  if (!cv) return gray;
  let out = gray;
  try { out = applyOps(cv, gray, ops, q); } catch (e) { return gray; }
  precleanStats.cleaned++; precleanStats.ms += Date.now() - t0;
  for (const o of ops) precleanStats.ops[o] = (precleanStats.ops[o] || 0) + 1;
  out.preclean = ops;
  return out;
}

