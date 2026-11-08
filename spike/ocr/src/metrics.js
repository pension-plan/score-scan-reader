'use strict';
// Text normalisation + accuracy metrics for lyric OCR (CER, WER, syllable error, hyphen boundary P/R).

const DASHES = /[‐‑‒–—―−­~]/g;

function postFilter(s) {
  // what the app would do to raw OCR of a lyric strip: drop glyphs that never occur in lyrics (stems -> | etc.)
  return s.normalize('NFKC')
    .replace(/[|\[\]{}<>^*#@=+\\/§®©°¢£€$%&]/g, ' ')
    .replace(/[‘’‛`´ʼ]/g, "'").replace(/[“”„«»]/g, '"')
    .replace(DASHES, '-')
    .replace(/_+/g, ' ')
    .replace(/\s+/g, ' ').trim();
}
function normGT(s) { return postFilter(s); }
function tightHyphens(s) { return s.replace(/\s*-\s*/g, '-').replace(/-+/g, '-').trim(); }
function lettersOnly(s) { return s.replace(/[\s\-]/g, ''); }

function lev(a, b) {
  // a, b: arrays or strings
  const n = a.length, m = b.length;
  if (!n) return m; if (!m) return n;
  let prev = new Array(m + 1), cur = new Array(m + 1);
  for (let j = 0; j <= m; j++) prev[j] = j;
  for (let i = 1; i <= n; i++) {
    cur[0] = i;
    const ai = a[i - 1];
    for (let j = 1; j <= m; j++) {
      const c = ai === b[j - 1] ? 0 : 1;
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + c);
    }
    [prev, cur] = [cur, prev];
  }
  return prev[m];
}

function align(a, b) {
  // returns map from index in a -> index in b (or -1), via full DP backtrace (strings of moderate length)
  const n = a.length, m = b.length;
  const D = new Array(n + 1);
  for (let i = 0; i <= n; i++) { D[i] = new Int32Array(m + 1); D[i][0] = i; }
  for (let j = 0; j <= m; j++) D[0][j] = j;
  for (let i = 1; i <= n; i++) for (let j = 1; j <= m; j++) {
    const c = a[i - 1] === b[j - 1] ? 0 : (a[i - 1].toLowerCase() === b[j - 1].toLowerCase() ? 0.5 : 1);
    D[i][j] = Math.min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + (c ? 1 : 0));
  }
  const map = new Int32Array(n).fill(-1);
  let i = n, j = m;
  while (i > 0 && j > 0) {
    const c = a[i - 1] === b[j - 1] ? 0 : 1;
    if (D[i][j] === D[i - 1][j - 1] + c) { map[i - 1] = j - 1; i--; j--; }
    else if (D[i][j] === D[i - 1][j] + 1) i--;
    else j--;
  }
  return map;
}

function stripPunct(w) { return w.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ''); }
function words(s) { return tightHyphens(s).split(' ').map(t => stripPunct(t.replace(/-/g, ''))).filter(Boolean); }
function syllables(s) { return tightHyphens(s).split(/[ \-]/).map(stripPunct).filter(Boolean); }

/** Score one line. gtLine: GT json line; ocr: raw OCR string. */
function scoreLine(gtLine, ocrRaw) {
  const gt = normGT(gtLine.text), oc = postFilter(ocrRaw || '');
  const gL = lettersOnly(gt), oL = lettersOnly(oc);
  const r = {
    nChars: gL.length, eChars: lev(gL, oL),
    nCharsFull: tightHyphens(gt).length, eCharsFull: lev(tightHyphens(gt), tightHyphens(oc)),
  };
  const gw = words(gt), ow = words(oc);
  r.nWords = gw.length; r.eWords = lev(gw, ow);
  const gs = syllables(gt), os = syllables(oc);
  r.nSyl = gs.length; r.eSyl = lev(gs, os);
  r.exactLine = tightHyphens(gt) === tightHyphens(oc) ? 1 : 0;
  // hyphen boundaries: GT syllable sequence with boundary types
  const sy = gtLine.syllables;
  let gstr = '', ends = [];
  for (const s of sy) { gstr += s.t.normalize('NFKC').replace(/[‘’]/g, "'").replace(/\s/g, ''); ends.push(gstr.length - 1); }
  const ostr = oc;               // keep spaces/hyphens in OCR, align on non-space/hyphen chars
  const oIdx = [], oChars = [];
  for (let k = 0; k < ostr.length; k++) if (!/[\s\-]/.test(ostr[k])) { oIdx.push(k); oChars.push(ostr[k]); }
  const map = align(gstr.split(''), oChars);
  const h = { tp: 0, fn: 0, fp: 0, tn: 0, joinedHy: 0, joinedSp: 0 };
  for (let k = 0; k < sy.length - 1; k++) {
    const isH = sy[k].hyph, printed = sy[k].hyph_printed;
    if (isH && !printed) continue;
    const a = map[ends[k]], b = map[ends[k] + 1];
    let pred = 'unk';
    if (a >= 0 && b >= 0 && b > a) {
      const between = ostr.slice(oIdx[a] + 1, oIdx[b]);
      pred = between.includes('-') ? 'h' : (/\s/.test(between) ? 's' : 'j');
    }
    if (pred === 'unk') continue;
    if (isH) { if (pred === 'h') h.tp++; else { h.fn++; if (pred === 'j') h.joinedHy++; } }
    else { if (pred === 'h') h.fp++; else { h.tn++; if (pred === 'j') h.joinedSp++; } }
  }
  r.hy = h;
  return r;
}

function aggregate(rs) {
  const A = { lines: rs.length, nChars: 0, eChars: 0, nCharsFull: 0, eCharsFull: 0, nWords: 0, eWords: 0, nSyl: 0, eSyl: 0, exact: 0, tp: 0, fn: 0, fp: 0, tn: 0, joinedHy: 0, joinedSp: 0, ms: 0 };
  for (const r of rs) {
    for (const k of ['nChars', 'eChars', 'nCharsFull', 'eCharsFull', 'nWords', 'eWords', 'nSyl', 'eSyl']) A[k] += r[k];
    A.exact += r.exactLine; A.ms += r.ms || 0;
    for (const k of ['tp', 'fn', 'fp', 'tn', 'joinedHy', 'joinedSp']) A[k] += r.hy[k];
  }
  return {
    lines: A.lines,
    CER: A.eChars / A.nChars, CERfull: A.eCharsFull / A.nCharsFull, WER: A.eWords / A.nWords, SylER: A.eSyl / A.nSyl,
    lineExact: A.exact / A.lines,
    hyP: A.tp / Math.max(1, A.tp + A.fp), hyR: A.tp / Math.max(1, A.tp + A.fn),
    hyF1: 2 * A.tp / Math.max(1, 2 * A.tp + A.fp + A.fn),
    joinRate: (A.joinedHy + A.joinedSp) / Math.max(1, A.tp + A.fn + A.fp + A.tn),
    msPerLine: A.ms / A.lines,
  };
}

module.exports = { postFilter, normGT, tightHyphens, lev, align, words, syllables, scoreLine, aggregate };
