'use strict';
// Optional ML symbol source: the copista-2m detector (KobiMusic, Apache-2.0,
// https://huggingface.co/kobimusic/copista-2m) read alongside the classical
// front end.  Off unless a caller wraps its converter:
//
//   node:    const det = await createNodeDetector();           // onnxruntime-node
//   browser: const det = createBrowserDetector();             // page: assets/ relative
//            const det = createBrowserDetector({ base });     // inside a worker: absolute assets URL
//   either:  conv = wrapConverter(omr.createConverter(opts), det.detect, { onProgress })
//            ... conv.addPage(gray, i, n) / conv.finish() as before; finish().ml = stats
//
// After the classical reading of a page (front + assemblePage), the detector
// reads the same deskewed page (fr.gray) and refines it in place:
//   - note values: notehead class (8th/16th/quarter/half...) and its dots
//     (dots_N boxes) replace ours where they disagree, one value per stem;
//     a quarter against a beam/flag the detector sees at our stem tip (or a
//     shorter value with none) is vetoed; heads shared by two voices are kept
//   - false heads: our head with no detector notehead but a rest, clef, time
//     or key signature, accidental, dynamic... box over it is dropped
//   - missed heads: a confident detector notehead we lack is added at the
//     staff position of OUR staff-line fit, into the chord at its x or as a
//     new chord with its stem read from the page
// Pitch comes from our staff fit (the model's staff_position drops to 0.65
// on broken-staff photocopies; it only confirms ledger positions here), and
// voices from the stem-based logic: on a real 1905 hymnal scan the model put
// 208 of 213 heads in voice slot 1, so voice_slot / stem_dir are not used.
// A detector that fails (offline CDN, no wasm) leaves the classical reading
// and one warning.
const { copistaCore, workerSource, MODEL_FILES } = require('./ml-worker');
const { staffPos, chordStems, ledgerOK } = require('./heads');

const core = copistaCore();

// ------------------------------------------------------------------ node
function loadOrtNode(hint) {
  const path = require('path');
  const tries = [hint, 'onnxruntime-node', path.join(__dirname, '../node_modules/onnxruntime-node'),
    path.join(__dirname, '../../node_modules/onnxruntime-node'), path.join(__dirname, '../../spike/ml/node_modules/onnxruntime-node')].filter(Boolean);
  let err;
  for (const t of tries) { try { return require(t); } catch (e) { err = e; } }
  throw new Error('onnxruntime-node not found (' + (err && err.message) + ')');
}

async function createNodeDetector(opts = {}) {
  const fs = require('fs'), path = require('path');
  const ort = opts.ort || loadOrtNode(opts.ortPath);
  const dirs = [opts.assets, path.join(__dirname, '../assets-src/ml'), path.join(__dirname, '../dist/assets')].filter(Boolean);
  const dir = dirs.find(d => fs.existsSync(path.join(d, MODEL_FILES.dense)));
  if (!dir) throw new Error('copista-2m model files not found');
  const so = { executionProviders: ['cpu'], intraOpNumThreads: opts.threads || 1, interOpNumThreads: 1, graphOptimizationLevel: 'all' };
  const sessions = {
    dense: await ort.InferenceSession.create(path.join(dir, MODEL_FILES.dense), so),
    rel: await ort.InferenceSession.create(path.join(dir, MODEL_FILES.rel), so),
  };
  const meta = JSON.parse(fs.readFileSync(path.join(dir, MODEL_FILES.meta), 'utf8'));
  return {
    detect: (gray, o) => core.detect(ort, sessions, meta, gray, o),
    async release() { try { await sessions.dense.release(); await sessions.rel.release(); } catch (e) { /* ignore */ } },
  };
}

// --------------------------------------------------------------- browser
// The detector runs in its own blob: module worker (onnxruntime-web from a
// pinned CDN, single thread).  Model and wasm bytes are fetched from the
// assets folder by relative path (or from opts.base, which must be absolute
// when this runs inside a worker) and handed to the worker.
function createBrowserDetector(opts = {}) {
  const base = opts.base || 'assets/';
  const timeoutMs = opts.timeoutMs || 180000;
  let wP = null, seq = 0;
  const pending = new Map();
  const fail = (err) => { for (const p of pending.values()) p.reject(err); pending.clear(); };
  function start() {
    if (wP) return wP;
    wP = (async () => {
      const get = async (f, json) => {
        const r = await fetch(base + f);
        if (!r.ok) throw new Error(`${f}: HTTP ${r.status}`);
        return json ? r.json() : r.arrayBuffer();
      };
      const [wasm, dense, rel, meta] = await Promise.all([get(MODEL_FILES.wasm), get(MODEL_FILES.dense), get(MODEL_FILES.rel), get(MODEL_FILES.meta, true)]);
      const url = URL.createObjectURL(new Blob([workerSource(opts.ortUrls)], { type: 'text/javascript' }));
      const w = new Worker(url, { type: 'module' });
      await new Promise((resolve, reject) => {
        const t = setTimeout(() => reject(new Error('the ML detector did not start in time')), timeoutMs);
        w.onmessage = (ev) => {
          const m = ev.data || {};
          if (m.t === 'ready') { clearTimeout(t); resolve(); } else if (m.t === 'error') { clearTimeout(t); reject(new Error(m.msg)); }
        };
        w.onerror = (e) => { clearTimeout(t); reject(new Error('the ML worker failed to start' + (e && e.message ? ': ' + e.message : ''))); };
        w.postMessage({ t: 'init', wasm, dense, rel, meta }, [wasm, dense, rel]);
      }).catch((e) => { w.terminate(); URL.revokeObjectURL(url); throw e; });
      URL.revokeObjectURL(url);
      w.onmessage = (ev) => {
        const m = ev.data || {};
        const p = pending.get(m.id);
        if (!p) return;
        pending.delete(m.id);
        clearTimeout(p.timer);
        if (m.t === 'dets') p.resolve({ dets: m.dets, timing: m.timing }); else p.reject(new Error(m.msg || 'detection failed'));
      };
      w.onerror = (e) => fail(new Error('the ML worker stopped' + (e && e.message ? ': ' + e.message : '')));
      return w;
    })();
    wP.catch(() => {});
    return wP;
  }
  return {
    warm: () => start().then(() => true, () => false),
    async detect(gray) {
      const w = await start();
      const id = ++seq;
      const data = new Uint8ClampedArray(gray.data); // own copy: the page keeps its buffer
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => { pending.delete(id); reject(new Error('the ML detector timed out')); }, timeoutMs);
        pending.set(id, { resolve, reject, timer });
        w.postMessage({ t: 'detect', id, img: { width: gray.width, height: gray.height, data } }, [data.buffer]);
      });
    },
    terminate() {
      if (wP) wP.then((w) => w.terminate(), () => {});
      fail(new Error('the ML detector was stopped'));
      wP = null;
    },
  };
}

// ------------------------------------------------------------- refinement
// Duration of each notehead class in quarters.
const NOTE_Q = { note_breve: 8, note_whole: 4, note_half: 2, note_quarter: 1, note_eighth: 0.5, note_16th: 0.25, note_32nd: 0.125, note_64th: 0.0625 };
const EPS = 1e-6;

function noteDets(dets, minConf) {
  const out = [];
  for (const d of dets || []) {
    const q0 = NOTE_Q[d.cls];
    if (!q0 || d.conf < minConf) continue;
    const [x0, y0, x1, y1] = d.xyxy;
    const nd = d.attrs && /^[1-4]$/.test(d.attrs.dots) ? +d.attrs.dots : 0;
    const grace = !!(d.attrs && d.attrs.grace && d.attrs.grace !== '<na>');
    const spos = d.attrs && /^-?\d+$/.test(d.attrs.staff_position) ? +d.attrs.staff_position : null;
    out.push({ x: (x0 + x1) / 2, y: (y0 + y1) / 2, w: x1 - x0, h: y1 - y0, q0, dots: nd, q: q0 * (2 - Math.pow(0.5, nd)), conf: d.conf, cls: d.cls, grace, spos });
  }
  return out;
}

// one-to-one matching of model noteheads to our heads: nearest centres, the
// vertical offset well under half a space (same staff position)
function matchHeads(heads, notes, ss) {
  const pairs = [];
  heads.forEach((h, i) => {
    const sp = h.sp || ss;
    notes.forEach((n, j) => {
      const dx = Math.abs(n.x - h.x), dy = Math.abs(n.y - h.y);
      if (dx < 0.6 * sp && dy < 0.4 * sp) pairs.push([dx / sp + 2 * dy / sp, i, j]);
    });
  });
  pairs.sort((a, b) => a[0] - b[0]);
  const hm = new Map(), nm = new Set();
  for (const [, i, j] of pairs) if (!hm.has(i) && !nm.has(j)) { hm.set(i, j); nm.add(j); }
  return hm;
}

// augmentation dots the detector reports as their own boxes (dots_N), right
// of a head and within a space of its height
function dotCount(h, dotBoxes, sp) {
  let best = 0;
  for (const d of dotBoxes) {
    if (d.x < h.x + 0.45 * sp || d.x > h.x + 2.6 * sp || Math.abs(d.y - h.y) > 0.8 * sp) continue;
    best = Math.max(best, d.n);
  }
  return best;
}

// what the detector found at the tip of a head's stem: 'beam', 'flag',
// 'none', or null when the head has no stem we know of
function tipMark(h, marks, sp) {
  const c = h.chord;
  if (!c || (h.stemDir !== 1 && h.stemDir !== -1)) return null;
  const up = h.stemDir === 1, x = up ? c.upX : c.downX, y = up ? c.upEnd : c.downEnd;
  if (!(x >= 0) || y == null) return null;
  for (const b of marks) {
    const dx = b.cls === 'beam' ? [0.4, 0.4] : [0.6, 0.3];
    if (x >= b.x0 - dx[0] * sp && x <= b.x1 + dx[1] * sp && y >= b.y0 - 0.8 * sp && y <= b.y1 + 0.8 * sp) return b.cls;
  }
  return 'none';
}

// Depth of the beam stack at a head's stem tip, in staff spaces, read on
// the staff-removed page R beside the stem (where the beams run on and the
// stem does not): one beam ~0.5, two ~1.25, three ~2.  null when the tip is
// unknown or carries no beam (nothing runs on sideways for 1.4 spaces).
function beamDepth(h, R, sp) {
  const c = h.chord;
  if (!R || !R.data || !c || (h.stemDir !== 1 && h.stemDir !== -1)) return null;
  const up = h.stemDir === 1, x = Math.round(up ? c.upX : c.downX), tip = up ? c.upEnd : c.downEnd;
  if (!(x >= 0) || tip == null) return null;
  const { width: w, height: H, data } = R;
  const ink = (xx, yy) => xx >= 0 && yy >= 0 && xx < w && yy < H && !!data[yy * w + xx];
  const inward = up ? 1 : -1;
  // the beam: the first row near the tip (a slur touching the stem can carry
  // the tip past it) where ink runs sideways for well over a head's width,
  // gaps of a screen or a broken print bridged
  const maxGap = Math.max(2, Math.round(0.15 * sp));
  const run = (yb, step) => {
    let n = 0, gap = 0, xx = x;
    while (Math.abs(xx - x) < 3 * sp) { xx += step; if (ink(xx, yb)) { n = Math.abs(xx - x); gap = 0; } else if (++gap > maxGap) break; }
    return n;
  };
  let row = null, side = 1;
  for (let k = -Math.round(0.2 * sp); k <= Math.round(1.2 * sp) && row == null; k++) {
    const yb = Math.round(tip + inward * k), l = run(yb, -1), r = run(yb, 1);
    if (Math.max(l, r) >= 1.4 * sp) { row = yb; side = r >= l ? 1 : -1; }
  }
  if (row == null) return null;
  const depths = [];
  for (const off of [0.45, 0.65, 0.85]) {
    const xx = Math.round(x + side * off * sp);
    let y0 = -1;
    for (let k = -Math.round(0.25 * sp); k <= Math.round(0.25 * sp) && y0 < 0; k++) if (ink(xx, row + inward * k)) y0 = row + inward * k;
    if (y0 < 0) continue;
    while (ink(xx, y0 - inward) && Math.abs(y0 - row) < 0.5 * sp) y0 -= inward;
    let y1 = y0, gap = 0;
    for (let yy = y0 + inward; Math.abs(yy - y0) < 3 * sp; yy += inward) { if (ink(xx, yy)) { y1 = yy; gap = 0; } else if (++gap > 0.35 * sp) break; }
    depths.push((Math.abs(y1 - y0) + 1) / sp);
  }
  if (!depths.length) return null;
  depths.sort((p, q) => p - q);
  return depths[depths.length >> 1];
}

// kind of a disagreement between two printed values (in quarters, undotted)
// Ink share of a head's centre (the middle of its oval, half a space wide and
// a third of a space high) on the page without staff lines: about 1 for a
// black head, well under for an open one.  null when the page is gone.
function centreInk(h, R, sp) {
  if (!R || !R.data) return null;
  const { width: w, height: H, data } = R;
  const x0 = Math.round(h.x - 0.25 * sp), x1 = Math.round(h.x + 0.25 * sp), y0 = Math.round(h.y - 0.17 * sp), y1 = Math.round(h.y + 0.17 * sp);
  let n = 0, k = 0;
  for (let y = Math.max(0, y0); y <= Math.min(H - 1, y1); y++) for (let x = Math.max(0, x0); x <= Math.min(w - 1, x1); x++) { n++; if (data[y * w + x]) k++; }
  return n ? k / n : null;
}

function changeKind(a, b) {
  const lo = Math.min(a, b), hi = Math.max(a, b);
  if (hi <= 0.5 + EPS) return 'flags';      // 8th / 16th / 32nd: beam or flag count
  if (lo >= 2 - EPS) return 'whole';        // half / whole / breve
  if (lo >= 1 - EPS) return 'hollow';       // quarter vs half or longer
  if (hi <= 1 + EPS) return 'stem';         // quarter vs 8th or shorter
  return 'far';
}

// Note values from the detector's notehead classes replace the classical
// reading where they differ (by the kinds of change allowed).  Heads on one
// stem take one value (the most confident vote).  A head shared by two voices
// (stems both ways) keeps the classical reading: the class names one value.
// Dots: the detector's dot boxes (dots_N) and its per-head dot attribute; a
// dot we read ourselves is kept unless opts.dots === 'ml'.
function refinePage(entry, dets, opts, stats) {
  const fr = entry.fr;
  const minConf = opts.minConf != null ? opts.minConf : 0.3;
  const overConf = opts.overrideConf != null ? opts.overrideConf : 0.5;
  const kinds = new Set(opts.kinds || ['flags', 'hollow', 'stem', 'whole', 'far']);
  const notes = noteDets(dets, minConf);
  const dotBoxes = (dets || []).filter(d => /^dots_[1-4]$/.test(d.cls) && d.conf >= minConf)
    .map(d => ({ x: (d.xyxy[0] + d.xyxy[2]) / 2, y: (d.xyxy[1] + d.xyxy[3]) / 2, n: +d.cls.slice(5) }));
  const marks = (dets || []).filter(d => (d.cls === 'beam' || d.cls === 'flag') && d.conf >= minConf)
    .map(d => ({ cls: d.cls, x0: d.xyxy[0], y0: d.xyxy[1], x1: d.xyxy[2], y1: d.xyxy[3] }));
  const heads = fr.heads || [];
  const hm = matchHeads(heads, notes, fr.ss);
  stats.heads += heads.length; stats.notes += notes.length; stats.matched += hm.size;
  // the two readings must mostly agree on where the heads are before either
  // corrects the other: on a page where they do not (a heavy photocopy, a
  // page the model cannot read) one of them is lost, and which one is unknown
  const agree = hm.size / Math.max(1, Math.min(heads.length, notes.length));
  if (heads.length >= 8 && agree < (opts.minAgree != null ? opts.minAgree : 0.6)) { stats.skipped = (stats.skipped || 0) + 1; return; }
  const edit = agree >= (opts.minAgreeEdit != null ? opts.minAgreeEdit : 0.75);
  // vote per (chord, stem direction)
  const groups = new Map();
  // cue-sized heads (see addMissedHeads) keep our value: the detector reads them as
  // full notes of another kind as often as not
  const minW = opts.minHeadW != null ? opts.minHeadW : 1.1;
  heads.forEach((h, i) => {
    if (!hm.has(i) || !h.dur || h.stemDir === 2) return;
    if (notes[hm.get(i)].w < minW * (h.sp || fr.ss)) return;
    const key = h.chord || h;
    const k = groups.get(key) || new Map();
    groups.set(key, k);
    (k.get(h.stemDir) || k.set(h.stemDir, []).get(h.stemDir)).push([h, notes[hm.get(i)]]);
  });
  for (const byDir of groups.values()) for (const list of byDir.values()) {
    const votes = new Map();
    for (const [, n] of list) votes.set(n.q0, (votes.get(n.q0) || 0) + n.conf);
    let q0 = null, best = -1;
    for (const [v, s] of votes) if (s > best) { best = s; q0 = v; }
    const conf = best / list.length;
    for (const [h, n] of list) {
      const our = h.dur, tup = our.tuplet;
      const sp = h.sp || fr.ss;
      const printed = tup ? our.q * tup.actual / tup.normal : our.q;
      const ourDots = our.dots || 0;
      const ourBase = printed / (2 - Math.pow(0.5, ourDots));
      const mlDots = Math.max(n.dots, dotCount(h, dotBoxes, sp));
      const dots = opts.dots === 'ml' ? mlDots : Math.max(mlDots, ourDots);
      let base = ourBase;
      const kind = changeKind(q0, ourBase);
      if (Math.abs(q0 - ourBase) > EPS && conf >= overConf && kinds.has(kind)) {
        // vetoes: a quarter (or longer) against a beam or flag the detector
        // itself found at the stem tip, or a shorter value with nothing
        // there; and between beamed values the beam stack we measure at our
        // stem tip has the final say on how many beams there are (blur
        // thickens one beam into the look of two for the model; a sliver of
        // a second beam gets lost for us)
        const tip = kind === 'stem' && opts.tipCheck !== false ? tipMark(h, marks, sp) : null;
        let veto = !!(tip && (q0 >= 1 - EPS ? tip !== 'none' : tip === 'none'));
        // black to open: the page must show the open centre too (a speckled or
        // blurred scan makes a black head look open to the detector)
        if (!veto && kind === 'hollow' && q0 > ourBase && opts.fillCheck !== false) {
          const ink = centreInk(h, fr.R, sp);
          if (ink != null && ink >= (opts.fillMax != null ? opts.fillMax : 0.9)) veto = true;
        }
        if (!veto && kind === 'flags' && opts.depthCheck !== false) {
          const d = beamDepth(h, fr.R, sp);
          if (d != null) veto = Math.round(Math.log2(0.5 / q0)) + 1 !== (d < 0.95 ? 1 : d < 1.75 ? 2 : d < 2.6 ? 3 : 4);
        }
        if (!veto) base = q0;
        else stats.vetoed = (stats.vetoed || 0) + 1;
      }
      const q = base * (2 - Math.pow(0.5, dots));
      if (Math.abs(printed - q) < EPS) continue;
      h.dur = { q: tup ? q * tup.normal / tup.actual : q, dots };
      if (tup) h.dur.tuplet = tup;
      h.mlDur = { from: printed, to: q, conf: +conf.toFixed(3), kind };
      stats.durations++;
    }
  }
  annotateAccidentals(heads, hm, dets, fr.ss, minConf);
  // rests, clefs and signatures stay on the page for other readers
  if (opts.keepDets !== false) fr.mlDets = (dets || []).filter(d => /^(rest_|mRest|multiRest|clef_|keySig_|meterSig_)/.test(d.cls) && d.conf >= minConf);
  if (entry.asm && edit && opts.remove !== false) removeFalseHeads(entry, dets, hm, opts, stats);
  if (entry.asm && edit && opts.add !== false) addMissedHeads(entry, notes, hm, opts, stats, heads, dets);
}

// The accidental the detector prints left of each head it also saw, as
// h.mlAcc ('sharp' | 'flat' | 'natural' | 'double-sharp' | 'flat-flat', or
// null for none): a reading assemble.js may prefer to its own glyph test.
const ACC = { accid_sharp: 'sharp', accid_flat: 'flat', accid_natural: 'natural', accid_dsharp: 'double-sharp', accid_dflat: 'flat-flat' };
function annotateAccidentals(heads, hm, dets, ss, minConf) {
  const acc = (dets || []).filter(d => ACC[d.cls] && d.conf >= minConf);
  heads.forEach((h, i) => {
    if (!hm.has(i)) return;
    const sp = h.sp || ss;
    let best = null, bd = Infinity;
    for (const d of acc) {
      const [x0, y0, x1, y1] = d.xyxy;
      if (x1 > h.x - 0.3 * sp || x1 < h.x - 3.2 * sp) continue;
      // a flat's bowl sits on the note; a sharp's / natural's middle does
      const yc = d.cls === 'accid_flat' || d.cls === 'accid_dflat' ? y1 - 0.55 * sp : (y0 + y1) / 2;
      const dy = Math.abs(yc - h.y);
      if (dy > 0.6 * sp) continue;
      const dd = (h.x - x1) / sp + 2 * dy / sp;
      if (dd < bd) { bd = dd; best = ACC[d.cls]; }
    }
    h.mlAcc = best;
  });
}

// Blobs we read as heads where the detector sees no notehead but another
// symbol (a rest, clef, time or key signature, accidental, dynamic, tuplet
// number...) covering the head's centre are that symbol: they leave the page.
const NON_NOTE = /^(rest_|mRest|multiRest|clef_|meterSig_|keySig_|accid_|dynam|tuplet|fermata|artic_|ending_|repeatMark|octave_|trill|mordent|pedal|breath|caesura)/;
function removeFalseHeads(entry, dets, hm, opts, stats) {
  const fr = entry.fr;
  const minC = opts.removeConf != null ? opts.removeConf : 0.5;
  const boxes = (dets || []).filter(d => NON_NOTE.test(d.cls) && d.conf >= minC);
  const drop = new Set();
  (fr.heads || []).forEach((h, i) => {
    if (hm.has(i)) return;
    const m = 0.15 * (h.sp || fr.ss);
    for (const b of boxes) {
      const [x0, y0, x1, y1] = b.xyxy;
      if (h.x >= x0 - m && h.x <= x1 + m && h.y >= y0 - m && h.y <= y1 + m) { drop.add(h); h.mlDrop = b.cls; break; }
    }
  });
  if (!drop.size) return;
  fr.heads = fr.heads.filter(h => !drop.has(h));
  for (const sy of entry.asm.systems) for (const s of sy.staves) {
    s.chords = s.chords.map(c => (c.heads.some(h => drop.has(h)) ? Object.assign({}, c, { heads: c.heads.filter(h => !drop.has(h)) }) : c)).filter(c => c.heads.length);
  }
  stats.removed = (stats.removed || 0) + drop.size;
}

// Confident noteheads of the detector that we missed join the page: on the
// staff position our own staff-line fit gives (not the model's), in the chord
// at their x (taking its stem and value) or as a new chord whose stem is read
// from the page.  Grace notes, heads in the clef / key area and heads outside
// every measure are left out.
function addMissedHeads(entry, notes, hm, opts, stats, heads0, dets) {
  const fr = entry.fr, asm = entry.asm;
  // staves with a percussion clef: the detector reads their heads well, but
  // their 'pitch' is an instrument and the classical reading leaves them out
  const perc = (dets || []).filter(d => d.cls === 'clef_perc' && d.conf >= 0.5).map(d => (d.xyxy[1] + d.xyxy[3]) / 2);
  const minW = opts.minHeadW != null ? opts.minHeadW : 1.1;
  const used = new Set(hm.values());
  const matched = new Set([...hm.keys()].map(i => heads0[i]));
  const minC = opts.addConf != null ? opts.addConf : 0.9;
  const L = fr.L || fr.R;
  for (let j = 0; j < notes.length; j++) {
    const n = notes[j];
    if (used.has(j) || n.conf < minC || n.grace) continue;
    const ps = staffPos(fr.staves, n.x, n.y);
    if (!ps) continue;
    // the staff its ledger lines lead to: the nearest one, else the next
    // staff on the head's side (high notes over a wide gap), as front.js
    // does; a position the model's own staff_position agrees with needs no
    // ledger evidence (ledgers fused into octave chords read badly)
    let st = null, p = 0, sp = 0, y = 0;
    for (const cand of [ps.st, fr.staves[ps.st.index + (ps.p > 0 ? -1 : 1)]]) {
      if (!cand || n.x < cand.left - cand.space || n.x > cand.right + cand.space) continue;
      const s2 = cand.spaceAt(n.x), ym = cand.yAt(2, n.x), pp = Math.round((ym - n.y) / (s2 / 2));
      if (Math.abs(pp) > 14) continue;
      const hd = { x: n.x, y: ym - (pp * s2) / 2, staff: cand.index, p: pp, sp: s2 };
      if (Math.abs(hd.y - n.y) > 0.35 * s2) continue;
      if (Math.abs(pp) >= 6 && n.spos !== pp && !(ledgerOK(L, fr.staves, hd, fr.lt) || ledgerOK(fr.R, fr.staves, hd, fr.lt))) continue;
      st = cand; p = pp; sp = s2; y = hd.y;
      break;
    }
    if (!st) continue;
    // cue and grace heads (narrower than a space and a tenth; a full head is
    // about 1.3) are not added: the detector has no cue class and its grace
    // flag misses most of them
    if (n.w < minW * sp) continue;
    if (perc.some(y0 => Math.abs(y0 - st.yAt(2, st.left)) < 2.5 * sp)) continue;
    // one of ours there already, or one of ours unmatched close by (the same
    // head, read at another height by one of the two)
    if (fr.heads.some(h => Math.abs(h.x - n.x) < 0.6 * sp && (Math.abs(h.y - y) < 0.45 * sp || (!matched.has(h) && Math.abs(h.y - y) < 1.2 * sp)))) continue;
    let sy = null, s = null;
    for (const a of asm.systems) for (const b of a.staves) if (b.si === st.index) { sy = a; s = b; }
    if (!s || n.x <= s.hdr.end + 0.3 * sp || !sy.measures.some(([a, b]) => n.x > a && n.x < b)) continue;
    const h = { x: n.x, y, staff: st.index, p, sp, kind: n.q0 >= 2 ? 'hollow' : 'filled', score: n.conf, w: n.w,
      x0: Math.round(n.x - n.w / 2), x1: Math.round(n.x + n.w / 2), ml: true };
    const k = s.chords.findIndex(c => Math.abs(c.x - n.x) < 0.7 * sp);
    if (k >= 0) {
      const c = s.chords[k];
      // the stem of the nearest head of the chord (above the top head of a
      // two-voice chord: up; below its bottom head: down)
      const near = c.heads.slice().sort((a, b) => Math.abs(a.y - y) - Math.abs(b.y - y))[0];
      let dir = near.stemDir;
      if (dir === 2 || (c.heads.some(o => o.stemDir === 1) && c.heads.some(o => o.stemDir === -1))) dir = y < near.y ? 1 : -1;
      const mate = c.heads.find(o => o.stemDir === dir && o.dur) || null;
      h.stemDir = dir;
      h.stem = Object.assign({}, near.stem || {}, { dir });
      h.chord = near.chord || c;
      h.dur = mate ? Object.assign({}, mate.dur) : { q: n.q, dots: n.dots };
      s.chords[k] = Object.assign({}, c, { heads: c.heads.concat([h]) });
    } else {
      const cs = chordStems(L, [h], { minLen: 1.5, sides: true });
      const c = cs[0];
      if (!c || c.accidental) continue;
      if (h.stemDir === 0 && n.q0 < 2) continue; // a black head needs a stem
      h.dur = { q: n.q, dots: n.dots };
      let at = s.chords.findIndex(o => o.x > c.x);
      if (at < 0) at = s.chords.length;
      s.chords.splice(at, 0, c);
    }
    fr.heads.push(h);
    stats.added = (stats.added || 0) + 1;
  }
}

// Wraps a converter (omr.createConverter) so each page's symbols are also
// read by the detector; detect(gray) -> Promise<{dets}>.  Pages are read as
// before, then refined in place (the page entry's heads), so a detector that
// fails or is slow costs nothing but a warning.
function wrapConverter(conv, detect, opts = {}) {
  const progress = opts.onProgress || (() => {});
  const stats = { pages: 0, failed: 0, ms: 0, heads: 0, notes: 0, matched: 0, durations: 0 };
  const warnings = [];
  let off = false;
  return Object.assign({}, conv, {
    async addPage(gray, i, n) {
      const entry = await conv.addPage(gray, i, n);
      if (!entry || off) return entry;
      const parts = entry.spread && entry.spread.length ? entry.spread : [entry];
      for (const e of parts) {
        if (off || !e.fr || !e.fr.gray || !e.fr.gray.data || !e.asm) continue;
        progress(`Page ${i + 1}${n ? '/' + n : ''}: checking note values with the ML detector`, { stage: 'notes', page: i, pages: n });
        const t0 = Date.now();
        try {
          const r = await detect(e.fr.gray);
          refinePage(e, (r && r.dets) || [], opts, stats);
          stats.pages++;
        } catch (err) {
          stats.failed++;
          // a detector that cannot start (offline CDN, no wasm) is not retried
          if (!stats.pages) off = true;
          warnings.push(`Page ${i + 1}: the ML symbol detector failed (${(err && err.message) || err}); the classical reading is kept${off ? ' for every page' : ''}.`);
        }
        stats.ms += Date.now() - t0;
      }
      return entry;
    },
    finish(...a) {
      const r = conv.finish(...a);
      if (warnings.length) r.warnings = warnings.concat(r.warnings || []);
      r.ml = Object.assign({}, stats);
      return r;
    },
    mlStats: stats,
  });
}

module.exports = { createNodeDetector, createBrowserDetector, wrapConverter, refinePage, matchHeads, noteDets, NOTE_Q, core };
