'use strict';
// Lyric text rows: find them under each staff of a system (between staves and
// below the last one), crop, OCR (injected engine), split into syllables.
// Rows are screened twice: by their ink (stems, ties, fermatas are not text)
// and by what OCR reads (lyric rows are mostly confident lower-case words).
// Verses are numbered top-down per staff; a stack under the bottom staff that
// starts with a printed "2." is stanza text set after the music and dropped.
const { makeGray } = require('./image');

const DEFAULTS = {
  widen: true,        // stretch word gaps before OCR (stops "workswith" merges)
  gapSp: 0.3,         // min blank run (staff spaces) that counts as a word gap
  addSp: 0.8,         // blank columns inserted into each word gap (staff spaces)
  hyGaps: true,       // also open up the gaps either side of a tight hyphen ("Her-ze-leid")
  rules: true,        // erase vertical rules (barlines, brackets, stems) crossing the text row
  targetH: 56,        // OCR crop height in px (incl. padding)
  norm: true,         // contrast-stretch the crop (paper -> white, ink -> black)
  minWordConf: 20,    // words below this confidence are dropped ...
  relaxLow: true,     // ... unless they look like clean words on a confident row
  minLineConf: 50,
  geomCheck: true,    // reject rows whose ink does not look like a text line (stems, fermatas, ties)
  goodFrac: 0.4,      // share of tokens that must be confident word-like tokens ...
  goodAbs: 6,         // ... or at least this many of them
  lastStaffSp: 14,    // how far below the last staff of a system verse rows may reach ...
  maxRowGapSp: 1.5,   // ... provided each row follows the previous one within this gap
};

// Returns [{band, sys, y0, y1, x0, x1}] text-line boxes in deskewed page coords.
function findTextLines(fr, sysIdx, nextTop, opts) {
  const o = { ...DEFAULTS, ...(opts || {}) };
  const { B, staves } = fr;
  const sys = fr.systems[sysIdx];
  const w = B.width;
  const out = [];
  sys.forEach((si, k) => {
    const st = staves[si];
    const sp = st.space;
    const xL = st.left, xR = st.right;
    const yA = Math.round(Math.max(...[xL, (xL + xR) / 2, xR].map(x => st.yAt(4, x))) + 1.2 * sp);
    let yB, ySoft = Infinity;
    if (k + 1 < sys.length) yB = Math.round(Math.min(...[xL, (xL + xR) / 2, xR].map(x => staves[sys[k + 1]].yAt(0, x))) - 2.0 * sp);
    else {
      // below the last staff: rows must start within 6 sp, but a stack of
      // verses may run further down as long as the rows stay contiguous
      yB = Math.round(Math.min(nextTop - 2.5 * sp, yA + o.lastStaffSp * sp, B.height - 1));
      ySoft = yA + 6 * sp;
    }
    if (yB - yA < 0.8 * sp) return;
    const first = out.length;
    // row profile of small-ink content (text) within the staff's x range
    const prof = [];
    for (let y = yA; y <= yB; y++) { let n = 0; for (let x = xL; x <= xR; x++) n += B.data[y * w + x]; prof.push(n); }
    const thr = Math.max(3, 0.004 * (xR - xL));
    let y = 0;
    while (y < prof.length) {
      if (prof[y] < thr) { y++; continue; }
      let y1 = y; while (y1 < prof.length && prof[y1] >= thr * 0.5) y1++;
      const hgt = y1 - y;
      if (hgt >= 0.6 * sp && hgt <= 2.6 * sp) out.push({ band: k, sys: sysIdx, last: k === sys.length - 1, y0: yA + y, y1: yA + y1, x0: xL, x1: xR, sp });
      else if (hgt > 2.6 * sp) {
        // tightly stacked verses: split the block at the profile valleys
        let mx = 0; for (let i = y; i < y1; i++) mx = Math.max(mx, prof[i]);
        const t2 = 0.18 * mx;
        for (let i = y; i < y1;) {
          if (prof[i] < t2) { i++; continue; }
          let j = i; while (j < y1 && prof[j] >= t2) j++;
          if (j - i >= 0.5 * sp && j - i <= 2.6 * sp) {
            const a = Math.max(y, i - Math.round(0.25 * sp)), b = Math.min(y1, j + Math.round(0.25 * sp));
            out.push({ band: k, sys: sysIdx, last: k === sys.length - 1, y0: yA + a, y1: yA + b, x0: xL, x1: xR, sp });
          }
          i = j;
        }
      }
      y = y1;
    }
    if (ySoft < Infinity) {
      let keep = first, prevEnd = -Infinity;
      for (let i = first; i < out.length; i++) {
        const r = out[i];
        if (r.y0 > ySoft && r.y0 - prevEnd > o.maxRowGapSp * sp) break;
        prevEnd = r.y1; keep = i + 1;
      }
      out.length = keep;
    }
  });
  return out;
}

// Column analysis of a text row on the binary page: vertical rules that cross
// the whole (padded) row, blank runs between glyph clusters, and simple shape
// statistics used to reject rows that are stems / ties / fermatas, not text.
function analyseRow(B, ln, pad) {
  const w = B.width;
  const ya = Math.max(0, ln.y0 - pad), yb = Math.min(B.height - 1, ln.y1 + pad);
  const xa = ln.x0, xb = ln.x1;
  const H = yb - ya + 1;
  const n = xb - xa + 1;
  const ink = new Int32Array(n), rule = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const x = xa + i;
    let c = 0, run = 0, best = 0;
    for (let y = ya; y <= yb; y++) {
      if (B.data[y * w + x]) { c++; run++; if (run > best) best = run; } else run = 0;
    }
    ink[i] = c;
    if (best >= 0.85 * H) rule[i] = 1;
  }
  // a rule is thin: drop marks on columns that belong to wide solid blobs
  for (let i = 0; i < n;) {
    if (!rule[i]) { i++; continue; }
    let j = i; while (j < n && rule[j]) j++;
    if (j - i > Math.max(3, 0.35 * ln.sp)) for (let k = i; k < j; k++) rule[k] = 0;
    i = j;
  }
  // clusters of inked columns (rules count as blank)
  const clusters = [];
  for (let i = 0; i < n;) {
    if (ink[i] < 1 || rule[i]) { i++; continue; }
    let j = i; while (j < n && ink[j] >= 1 && !rule[j]) j++;
    clusters.push([i, j]);
    i = j;
  }
  let cov = 0; for (const [a, b] of clusters) cov += b - a;
  // hyphen-like clusters: a short thin dash in the middle band of the row
  const hy = clusters.map(([a, b]) => {
    const wdt = b - a;
    if (wdt < 0.25 * ln.sp || wdt > 1.3 * ln.sp) return false;
    let top = Infinity, bot = -1;
    for (let x = xa + a; x < xa + b; x++) for (let y = ya; y <= yb; y++) if (B.data[y * w + x]) { if (y < top) top = y; if (y > bot) bot = y; }
    if (bot < 0) return false;
    const mid = (top + bot) / 2, rel = (mid - ln.y0) / Math.max(1, ln.y1 - ln.y0);
    return bot - top + 1 <= Math.max(3, 0.22 * ln.sp) && rel > 0.3 && rel < 0.85;
  });
  return { xa, ya, yb, n, ink, rule, clusters, hy, cov: cov / n };
}

// Build the OCR crop: blank vertical rules, stretch word gaps (tesseract
// otherwise glues tightly set underlay words together), contrast-stretch,
// scale. Returns {img, toPage(xCrop) -> page x}.
function buildCrop(g, row, ln, o) {
  const gapMin = Math.max(3, o.gapSp * ln.sp);
  const add = o.widen ? Math.round(o.addSp * ln.sp) : 0;
  // segments of source columns, with inserted blank columns before each
  const segs = []; // {sx, len, before}
  const { clusters, n } = row;
  if (!o.widen || !clusters.length) segs.push({ sx: 0, len: n, before: 0 });
  else {
    let start = 0;
    for (let c = 1; c < clusters.length; c++) {
      const gap = clusters[c][0] - clusters[c - 1][1];
      if (gap >= gapMin || (o.hyGaps && (row.hy[c] || row.hy[c - 1]))) {
        const cut = clusters[c - 1][1] + Math.floor(gap / 2);
        segs.push({ sx: start, len: cut - start, before: segs.length ? add : 0 });
        start = cut;
      }
    }
    segs.push({ sx: start, len: n - start, before: segs.length ? add : 0 });
  }
  const srcW = segs.reduce((a, s) => a + s.len + s.before, 0);
  const srcH = row.yb - row.ya + 1;
  const scale = Math.min(3, Math.max(0.5, o.targetH / srcH));
  // source column for each virtual column (-1 = inserted blank)
  const vcol = new Int32Array(srcW);
  let v = 0;
  for (const s of segs) {
    for (let k = 0; k < s.before; k++) vcol[v++] = -1;
    for (let k = 0; k < s.len; k++) vcol[v++] = s.sx + k;
  }
  // background level: bright percentile of the row
  const hist = new Int32Array(256);
  for (let y = row.ya; y <= row.yb; y++) for (let i = 0; i < n; i += 2) hist[g.data[y * g.width + row.xa + i]]++;
  let tot = 0; for (let i = 0; i < 256; i++) tot += hist[i];
  let acc = 0, bg = 255; for (let i = 255; i >= 0; i--) { acc += hist[i]; if (acc >= 0.3 * tot) { bg = i; break; } }
  // dark level: ink percentile, for an optional contrast stretch
  acc = 0; let dk = 0; for (let i = 0; i < 256; i++) { acc += hist[i]; if (acc >= 0.02 * tot) { dk = i; break; } }
  const stretch = o.norm && bg - dk > 40;
  const lut = new Uint8ClampedArray(256);
  for (let i = 0; i < 256; i++) lut[i] = stretch ? Math.round(255 * (i - dk) / (bg - dk)) : i;
  const W = Math.max(1, Math.round(srcW * scale)), Hh = Math.max(1, Math.round(srcH * scale));
  const img = makeGray(W, Hh, stretch ? 255 : bg);
  const real = (v) => vcol[v] >= 0 && !(o.rules && row.rule[vcol[v]]);
  for (let x = 0; x < W; x++) {
    const vi = Math.min(srcW - 1, Math.floor(x / scale));
    if (!real(vi)) continue;
    const sx = row.xa + vcol[vi];
    for (let y = 0; y < Hh; y++) {
      const sy = Math.min(g.height - 1, row.ya + Math.floor(y / scale));
      img.data[y * W + x] = lut[g.data[sy * g.width + sx]];
    }
  }
  const toPage = (xc) => {
    const vi = Math.max(0, Math.min(srcW - 1, Math.floor(xc / scale)));
    // nearest real column
    for (let d = 0; d < srcW; d++) {
      if (vi + d < srcW && vcol[vi + d] >= 0) return row.xa + vcol[vi + d];
      if (vi - d >= 0 && vcol[vi - d] >= 0) return row.xa + vcol[vi - d];
    }
    return row.xa;
  };
  return { img, toPage, scale };
}

function cropGray(g, x0, y0, x1, y1, scale) {
  const w = Math.round((x1 - x0) * scale), h = Math.round((y1 - y0) * scale);
  const out = makeGray(w, h, 255);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const sx = Math.min(g.width - 1, Math.round(x0 + x / scale)), sy = Math.min(g.height - 1, Math.round(y0 + y / scale));
    out.data[y * w + x] = g.data[sy * g.width + sx];
  }
  return out;
}

const HY = /[-‐‑‒–—―~]/;
const LETTER = /[A-Za-zÀ-ɏ]/;

// Does an OCR token look like part of a lyric (word, syllable, hyphen, verse number)?
function plausible(t) {
  if (/_/.test(t)) return t.split(/_+/).filter(Boolean).every(plausible);
  const s = t.replace(/^[|_.,;:!?'"“”‘’()]+|[|_.,;:!?'"“”‘’()]+$/g, '');
  if (!s) return false;
  if (/^[-‐‑‒–—―~]+$/.test(s)) return true;
  if (/^\d{1,2}$/.test(s)) return true;
  // letters with optional leading/internal/trailing hyphens and apostrophes; no digits or odd symbols
  return /^[-‐‑‒–—―~]*[\p{L}'’]+(?:[-‐‑‒–—―~]+[\p{L}'’]+)*[-‐‑‒–—―~]*$/u.test(s);
}

// Split OCR words that glue two words together: "thee,Sweet", "song.Let",
// "GodtoThee", "we_on" -> pieces with proportional x extents.
function splitMerged(words) {
  const out = [];
  for (const wd of words) {
    const t = wd.text.replace(/_+/g, ' ').replace(/([,.;:!?])(?=\p{L})/gu, '$1 ').replace(/(\p{Ll})(?=\p{Lu})/gu, '$1 ');
    const parts = t.split(/\s+/).filter(Boolean);
    if (parts.length <= 1) { out.push({ ...wd, text: parts[0] || '' }); continue; }
    const tot = parts.reduce((a, p) => a + p.length, 0);
    let x = wd.x0;
    for (const p of parts) {
      const ww = (wd.x1 - wd.x0) * p.length / tot;
      out.push({ ...wd, text: p, x0: x, x1: x + ww });
      x += ww;
    }
  }
  return out.filter(w => w.text);
}

// confident word-like token: lower case and a vowel (or the words A / I / O)
function goodWord(w, minLen = 1) {
  const letters = w.text.replace(/[^\p{L}]/gu, '');
  if (!w.ok || w.conf < 50 || letters.length < minLen) return false;
  if (/^[AIO]$/.test(letters)) return true;
  return /\p{Ll}/u.test(letters) && /[aeiouyäöüàâæçéèêëîïôœùûÿáíóúñ]/i.test(letters);
}

// words: [{text, conf, x0, x1}] in page coordinates
function toSyllables(words) {
  const toks = [];
  for (const wd of words) {
    let t = wd.text.replace(/[|*^{}\[\]<>«»]/g, '').replace(/_+/g, ' ').trim();
    if (!t) continue;
    // an OCR word can still hold spaces (after "_" removal): split proportionally
    const sub = t.split(/\s+/).filter(Boolean);
    const totalLen = sub.reduce((a, s) => a + s.length, 0) || 1;
    let wx = wd.x0;
    for (const s0 of sub) {
      const sw = (wd.x1 - wd.x0) * s0.length / totalLen;
      // split on hyphens, keeping hyphen markers
      const parts = s0.split(/([-‐‑‒–—―~]+)/).filter(Boolean);
      const letters = parts.reduce((a, p) => a + (HY.test(p[0]) ? 0 : p.length), 0) || 1;
      let cx = wx;
      for (const p of parts) {
        if (HY.test(p[0])) { toks.push({ hy: true }); continue; }
        const ww = sw * p.length / letters;
        toks.push({ text: p, x: cx + ww / 2, conf: wd.conf });
        cx += ww;
      }
      wx += sw;
    }
  }

  // drop leading verse number like "1." / "2" / "3.O" (number glued to the first word)
  // (scan noise such as a bracket read as "Wi" may precede it: drop that too)
  let number = null;
  for (let i = 0; i < Math.min(3, toks.length); i++) {
    if (toks[i].hy) continue;
    const m = toks[i].text.match(/^([0-9]{1,2})[.,:]\s*(.*)$/) || toks[i].text.match(/^([0-9]{1,2})$/);
    const roman = /^[IVX]{1,3}[.,]$/.test(toks[i].text);
    if (!m && !roman) continue;
    if (i > 0 && !(m && /[.,:]/.test(toks[i].text)) && !roman) continue; // bare digit later in the row: not a verse number
    if (m) number = parseInt(m[1], 10);
    const rest = m && m[2] && LETTER.test(m[2]) ? { ...toks[i], text: m[2] } : null;
    toks.splice(0, i + 1);
    if (rest) toks.unshift(rest);
    break;
  }
  const syl = [];
  for (let i = 0; i < toks.length; i++) {
    const t = toks[i];
    if (t.hy) continue;
    if (!LETTER.test(t.text)) continue;
    const hyBefore = i > 0 && toks[i - 1].hy && syl.length;
    const hyAfter = i + 1 < toks.length && toks[i + 1].hy;
    const syllabic = hyBefore ? (hyAfter ? 'middle' : 'end') : (hyAfter ? 'begin' : 'single');
    syl.push({ text: t.text.replace(/^[^\p{L}'’]+|[^\p{L}'’!?,.;:]+$/gu, ''), x: t.x, syllabic, conf: t.conf });
  }
  return { number, syllables: syl.filter(s => s.text) };
}

// ocr(grayImage) -> Promise<[{text, conf, x0, x1}]> in the given image's pixels
async function readLyrics(fr, ocr, onProgress, opts) {
  const o = { ...DEFAULTS, ...(opts || {}) };
  const out = {};
  const sysTops = fr.systems.map(sys => fr.staves[sys[0]].yAt(0, fr.staves[sys[0]].left));
  let done = 0;
  const all = [];
  fr.systems.forEach((sys, si) => all.push(...findTextLines(fr, si, sysTops[si + 1] ?? fr.gray.height, o)));
  for (const ln of all) {
    const step = () => { done++; if (onProgress) onProgress(done, all.length); };
    const pad = Math.round(0.3 * ln.sp);
    const row = analyseRow(fr.B, ln, pad);
    // opts.debug (an array) collects per-row decisions for tuning tools
    const dbg = o.debug ? { sys: ln.sys, band: ln.band, y: ln.y0, h: ln.y1 - ln.y0, sp: +ln.sp.toFixed(1), cov: +row.cov.toFixed(3), ncl: row.clusters.length } : null;
    if (dbg) o.debug.push(dbg);
    // text rows have many glyph clusters and a fair share of inked columns;
    // rows of stems, ties or fermatas have few, thin ones
    if (o.geomCheck && (row.cov < 0.08 || row.clusters.length < 4)) { if (dbg) dbg.reject = 'geom'; step(); continue; }
    const { img, toPage } = buildCrop(fr.gray, row, ln, o);
    let words = [];
    try { words = await ocr(img); } catch (e) { words = []; }
    const mapped = splitMerged(words.map(w => ({ ...w, x0: toPage(w.x0), x1: toPage(Math.max(w.x0, w.x1 - 1)) + 1 }))).map(w => ({ ...w, ok: plausible(w.text) }));
    // line-level sanity: lyric rows are mostly clean words
    const nOk = mapped.filter(w => w.ok).length;
    const meanConf = mapped.reduce((a, w) => a + w.conf, 0) / Math.max(1, mapped.length);
    const kept = mapped.filter(w => w.conf >= o.minWordConf || (o.relaxLow && w.ok && meanConf >= o.minLineConf));
    if (dbg) { dbg.raw = mapped.map(w => w.text + '(' + Math.round(w.conf) + ')').join(' '); dbg.meanConf = Math.round(meanConf); dbg.okFrac = +(nOk / Math.max(1, mapped.length)).toFixed(2); }
    // a lyric row has several confident, word-like tokens (lower case, a vowel, 2+ letters);
    // rows of stems, dynamics or ties read as capitals, symbols and single letters
    const nGood = mapped.filter(w => goodWord(w)).length, nGood2 = mapped.filter(w => goodWord(w, 2)).length;
    const nTok = mapped.filter(w => !/^[-‐‑‒–—―~_|.,;:'"]+$/.test(w.text)).length;
    if (dbg) dbg.good = nGood + '/' + nTok;
    if (!mapped.length || meanConf < o.minLineConf * 0.8 || nOk < 0.6 * mapped.length || nGood2 < 2 || (nGood < o.goodFrac * nTok && nGood < o.goodAbs)) { if (dbg) dbg.reject = 'ocr'; step(); continue; }
    const { number, syllables } = toSyllables(kept.filter(w => w.ok || w.conf >= 60));
    (out[ln.sys] ||= []).push({ band: ln.band, last: ln.last, y: ln.y0, printed: number, number, syllables, raw: mapped.map(w => w.text).join(' '), conf: meanConf });
    step();
  }
  // verse numbers: per system and band, rows top-down are verses 1..n
  for (const k in out) {
    out[k] = out[k].filter(v => v.syllables.length >= 2);
    const byBand = {};
    out[k].forEach(v => (byBand[v.band] ||= []).push(v));
    for (const b in byBand) {
      const rows = byBand[b].sort((a, c) => a.y - c.y);
      // below the bottom staff, a stack whose top row is printed "2." (or
      // later) is the remaining stanzas set as a poem after the music
      if (rows[0].last && rows[0].printed >= 2) { rows.forEach(v => { v.stanza = true; }); continue; }
      rows.forEach((v, i) => { v.number = i + 1; });
    }
    out[k] = out[k].filter(v => !v.stanza);
  }
  // a word hyphenated across a system break: the first syllable of the next
  // system's matching verse continues it ("o-" | "cean" -> end, not single)
  const keys = Object.keys(out).map(Number).sort((a, b) => a - b);
  for (let i = 1; i < keys.length; i++) {
    if (keys[i] !== keys[i - 1] + 1) continue;
    for (const v of out[keys[i]]) {
      const prev = out[keys[i - 1]].find(u => u.band === v.band && u.number === v.number);
      const last = prev && prev.syllables[prev.syllables.length - 1];
      if (!last || !(last.syllabic === 'begin' || last.syllabic === 'middle') || !v.syllables.length) continue;
      const f = v.syllables[0];
      if (f.syllabic === 'single') f.syllabic = 'end';
      else if (f.syllabic === 'begin') f.syllabic = 'middle';
    }
  }
  return out;
}

module.exports = { readLyrics, findTextLines, toSyllables, cropGray, DEFAULTS, _analyseRow: analyseRow };
