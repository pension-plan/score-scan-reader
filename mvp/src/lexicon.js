'use strict';
// Lyric OCR post-correction against word-frequency lists (L36).
//
// The lists (assets/lex-<lang>.txt.gz: the 100,000 most frequent words of
// wordfreq 3.1.1, CC BY-SA 4.0, see NOTICE.lexicon.txt) are fetched only when
// a page has lyrics, one language at a time.  A word the list does not know
// (or knows only as a rarity) is replaced by a list word that a few typical
// OCR confusions turn it into ("Iler-zens" -> "Her-zens", "dureh" -> "durch",
// "nenı" -> "nem") when that word is far more frequent; at most one edit
// outside the confusion table is allowed.  The syllable boundaries of the
// word are kept where they were (mapped through the edits), so each syllable
// stays under its note.

const LANGS = ['en', 'de', 'fr', 'es', 'it', 'cs'];

// observed -> intended, cost (a generic substitution, insertion or deletion costs 1)
const CONFUSIONS = [
  ['Il', 'H', 0.3], ['Iı', 'H', 0.3], ['Ii', 'H', 0.4], ['Ili', 'H', 0.5], ['Cs', 'G', 0.4], ['Ci', 'G', 0.3], ['C', 'G', 0.6], ['Gi', 'G', 0.4],
  ['T', 'L', 0.5], ['J', 'H', 0.7], ['I', 'l', 0.3], ['l', 'I', 0.5], ['1', 'l', 0.3], ['ı', 'i', 0.1], ['|', 'l', 0.3],
  ['rn', 'm', 0.3], ['m', 'rn', 0.4], ['nı', 'm', 0.3], ['ni', 'm', 0.5], ['in', 'm', 0.5], ['iu', 'm', 0.5], ['ri', 'n', 0.5], ['n', 'ri', 0.6],
  ['n', 'u', 0.4], ['u', 'n', 0.4], ['a', 'u', 0.6], ['ii', 'ü', 0.3], ['di', 'ü', 0.5], ['u', 'ü', 0.3], ['a', 'ä', 0.3], ['o', 'ö', 0.3],
  ['e', 'c', 0.5], ['c', 'e', 0.5], ['eh', 'ch', 0.4], ['h', 'b', 0.5], ['b', 'h', 0.5], ['li', 'h', 0.5], ['f', 's', 0.4], ['ſ', 's', 0.1],
  ['l', 'i', 0.5], ['i', 'l', 0.5], ['cl', 'd', 0.4], ['vv', 'w', 0.3], ['e', 'o', 0.6], ['o', 'e', 0.6], ['c', 'o', 0.6], ['o', 'c', 0.6],
  ['t', 'f', 0.6], ['f', 't', 0.6], ['tl', 'd', 0.5], ['h', 'k', 0.6], ['k', 'h', 0.6], ['y', 'v', 0.6], ['v', 'y', 0.6],
];
// accent-blind letters of the second-pass languages
for (const [b, acc] of [['a', 'àáâä'], ['e', 'èéêë'], ['i', 'ìíîï'], ['o', 'òóôö'], ['u', 'ùúûü'], ['c', 'čç'], ['n', 'ñň'], ['s', 'š'], ['z', 'ž'], ['r', 'ř'], ['y', 'ý']]) {
  for (const a of acc) CONFUSIONS.push([b, a, 0.3]);   // (an accent read is kept: the row may be another language)
}
const LETTERS = 'abcdefghijklmnopqrstuvwxyzäöüßéèàùâêîôûçëïñáíóúčšžřýěů';

// ------------------------------------------------------------------ lists
const cache = new Map();
function parseList(text) {
  const m = new Map();
  for (const line of text.split('\n')) {
    if (!line || line[0] === '#') continue;
    const sp = line.indexOf(' ');
    const cb = +line.slice(0, sp);
    for (const w of line.slice(sp + 1).split(' ')) if (w && !m.has(w)) m.set(w, cb);
  }
  return m;
}
async function fetchList(lang) {
  const file = `lex-${lang}.txt.gz`;
  if (typeof process !== 'undefined' && process.versions && process.versions.node && typeof require === 'function') {
    const fs = require('fs'), path = require('path'), zlib = require('zlib');
    const dirs = [process.env.OMR_ASSETS, path.join(__dirname, '../dist/assets'), path.join(process.cwd(), 'mvp/dist/assets'), path.join(process.cwd(), 'dist/assets')].filter(Boolean);
    const d = dirs.find(x => fs.existsSync(path.join(x, file)));
    if (!d) return null;
    return parseList(zlib.gunzipSync(fs.readFileSync(path.join(d, file))).toString('utf8'));
  }
  if (typeof fetch !== 'function' || typeof DecompressionStream !== 'function') return null;
  const base = (typeof self !== 'undefined' && self.OMR_ASSET_BASE) || 'assets/';
  const r = await fetch(base + file);
  if (!r.ok) return null;
  const text = await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).text();
  return parseList(text);
}
// a language's list, or null when it cannot be loaded (kept: one try per session)
function loadLexicon(lang) {
  if (!LANGS.includes(lang)) return Promise.resolve(null);
  if (!cache.has(lang)) cache.set(lang, fetchList(lang).catch(() => null));
  return cache.get(lang);
}

// ------------------------------------------------------------ candidates
const lf = (lex, w) => { const c = lex.get(w); return c == null ? -9 : -c / 100; };   // log10 frequency
const norm = (s) => s.toLowerCase().replace(/[’]/g, "'");

// Every string a few confusions (and at most one generic edit) make of s,
// with its cost and where each character of s starts in it.
function variants(s, maxCost, generic0) {
  const out = [];
  const n = s.length;
  const rec = (i, acc, map, cost, generic) => {
    if (cost > maxCost) return;
    if (i === n) { map.push(acc.length); out.push({ t: acc, cost, map: map.slice() }); map.pop(); return; }
    // keep
    map.push(acc.length);
    rec(i + 1, acc + s[i], map, cost, generic);
    map.pop();
    for (const [a, b, c] of CONFUSIONS) {
      if (s.startsWith(a, i)) {
        for (let k = 0; k < a.length; k++) map.push(acc.length);
        rec(i + a.length, acc + b, map, cost + c, generic);
        for (let k = 0; k < a.length; k++) map.pop();
      }
    }
    // (no generic edit in a word's last two letters: an inflection there is not a misread,
    // "templed" is not "temple")
    if (!generic && i < n - 2) {
      map.push(acc.length);
      for (const L of LETTERS) if (L !== s[i].toLowerCase()) rec(i + 1, acc + L, map, cost + 1, true);   // substitute
      map.pop();
      // insert before (the new letter ends the previous syllable: "me-nes" -> "mei-nes")
      map.push(acc.length + 1);
      for (const L of LETTERS) rec(i + 1, acc + L + s[i], map, cost + 1, true);
      map.pop();
      map.push(acc.length);
      rec(i + 1, acc, map, cost + 1, true);                                          // delete
      map.pop();
    }
  };
  rec(0, '', [], 0, !!generic0);
  return out;
}

// minLen: shorter tokens are often a syllable whose hyphen was lost ("Suf" of Suf-fer), not a word;
// generic edits only on words of genericLen..maxGenericLen letters
const OPTS = { maxCost: 1.6, perCost: 2, minGain: 2, minFreq: -6.3, knownAt: -5.6, minLen: 4, mergeCost: 0.3, genericLen: 6, maxGenericLen: 10, commonAt: -4 };

// Best correction of one word (letters only, case kept) or null.  f0: the
// log frequency to beat (default: the word's own).
function correctWord(word, lex, o = OPTS, f0) {
  // letters only; elisions (o'er, heav'n) are left as printed
  if (word.length < o.minLen || !/^\p{L}+$/u.test(word)) return null;
  if (f0 == null) f0 = lf(lex, norm(word));
  if (f0 >= o.knownAt) return null;
  let best = null;
  const seen = new Map();
  for (const v of variants(word, o.maxCost, word.length > o.maxGenericLen || word.length < o.genericLen)) {
    const t = norm(v.t);
    if (t.length < 2) continue;
    const f = lf(lex, t);
    if (f < o.minFreq) continue;
    const gain = f - f0 - o.perCost * v.cost;
    const prev = seen.get(t);
    if (prev && prev.gain >= gain) continue;
    seen.set(t, { gain });
    if (gain >= o.minGain && (!best || gain > best.gain)) best = { text: v.t, gain, cost: v.cost, map: v.map, freq: f };
  }
  if (!best) return null;
  // case as printed: a capital first letter stays capital
  const up = /\p{Lu}/u.test(word[0]) || /\p{Lu}/u.test(best.text[0]);
  best.text = (up ? best.text[0].toUpperCase() : best.text[0].toLowerCase()) + best.text.slice(1).toLowerCase();
  if (/^\p{Lu}+$/u.test(word)) best.text = best.text.toUpperCase();
  return best;
}

// ------------------------------------------------------------- syllables
// words of a row: runs of syllables joined by hyphens (begin .. end)
function wordsOf(syl) {
  const ws = [];
  let cur = null;
  syl.forEach((s, i) => {
    if (!cur || s.syllabic === 'single' || s.syllabic === 'begin') { cur = [i]; ws.push(cur); } else cur.push(i);
    if (s.syllabic === 'single' || s.syllabic === 'end') cur = null;
  });
  return ws;
}
const strip = (t) => {
  const m = t.match(/^([^\p{L}]*)([\p{L}'’]*)([^\p{L}]*)$/u);
  return m ? { pre: m[1], core: m[2], post: m[3] } : null;
};
// the corrected word cut at the old syllable starts (mapped); an empty piece
// joins its neighbour
function resplit(syl, idx, fix, starts) {
  const pieces = [];
  for (let k = 0; k < idx.length; k++) {
    const a = fix.map[starts[k]], b = k + 1 < idx.length ? fix.map[starts[k + 1]] : fix.text.length;
    pieces.push({ s: syl[idx[k]], text: fix.text.slice(a, b) });
  }
  const kept = [];
  for (const p of pieces) {
    if (p.text) { kept.push(p); continue; }
    const q = kept[kept.length - 1];
    if (q) { q.s = Object.assign({}, q.s, { x1: p.s.x1 }); } else p.empty = true;
  }
  // a leading empty piece hands its left edge to the first kept one
  if (pieces[0].empty && kept.length) kept[0].s = Object.assign({}, kept[0].s, { x0: pieces[0].s.x0 });
  return kept;
}

// Corrects the syllables of one row in place; returns [{from, to}] changes.
// others: the other loaded lists (a word one of them knows is left alone: rows mix languages)
function correctRow(syl, lex, o = OPTS, others = []) {
  const known = (t) => others.some(x => lf(x, norm(t)) >= o.knownAt);
  const changes = [];
  const words = wordsOf(syl);
  const out = syl.slice();
  const replace = new Map();   // first index -> {idx, kept}
  for (let w = 0; w < words.length; w++) {
    let idx = words[w];
    const parts = idx.map(i => strip(syl[i].text));
    if (parts.some(p => !p) || parts.slice(0, -1).some(p => p.post) || parts.slice(1).some(p => p.pre)) continue;
    let core = parts.map(p => p.core).join('');
    let starts = [];
    { let k = 0; for (const p of parts) { starts.push(k); k += p.core.length; } }
    let fix = known(core) ? null : correctWord(core, lex, o);
    // two words OCR set apart ("I ler-zens" for Her-zens, "dei nenı" for dei-nem): read
    // as one when one of them is unknown and together they make a known word
    if (w + 1 < words.length && !parts[parts.length - 1].post) {
      const idx2 = words[w + 1], parts2 = idx2.map(i => strip(syl[i].text));
      if (parts2.every(p => p && !p.pre) && parts2.slice(0, -1).every(p => !p.post)) {
        const core2 = parts2.map(p => p.core).join('');
        const fa = lf(lex, norm(core)), fb = lf(lex, norm(core2));
        // (a common word of any loaded language is never glued to its neighbour: "to", "es")
        const common = (t) => t.length >= 2 && [lex, ...others].some(x => lf(x, norm(t)) >= o.commonAt);
        if (Math.min(fa, fb) < o.minFreq && core2 && !(known(core) && known(core2)) && !common(core) && !common(core2)) {
          const f2 = correctWord(core + core2, lex, o, Math.min(fa, fb) + o.perCost * o.mergeCost);
          if (f2 && (!fix || f2.gain > fix.gain)) {
            fix = f2; idx = idx.concat(idx2);
            starts.push(core.length); { let k = core.length; for (const p of parts2.slice(1)) { k += parts2[parts2.indexOf(p) - 1].core.length; starts.push(k); } }
            core = core + core2; parts.push(...parts2); w++;
          }
        }
      }
    }
    if (!fix) continue;
    const kept = resplit(syl, idx, fix, starts);
    if (!kept.length) continue;
    // syllabic marks of the new pieces: one word
    kept.forEach((p, k) => {
      const syllabic = kept.length === 1 ? 'single' : k === 0 ? 'begin' : k === kept.length - 1 ? 'end' : 'middle';
      const pre = k === 0 ? parts[0].pre : '', post = k === kept.length - 1 ? parts[parts.length - 1].post : '';
      p.s = Object.assign({}, p.s, { text: pre + p.text + post, syllabic, lex: true });
    });
    // a word continued from or to another system keeps its outer marks
    const first = syl[idx[0]], last = syl[idx[idx.length - 1]];
    if (first.syllabic === 'middle' || first.syllabic === 'end') kept[0].s.syllabic = kept.length === 1 ? (last.syllabic === 'middle' ? 'middle' : 'end') : 'middle';
    if (last.syllabic === 'begin' || last.syllabic === 'middle') { const L = kept[kept.length - 1].s; L.syllabic = L.syllabic === 'single' ? 'begin' : L.syllabic === 'end' ? 'middle' : L.syllabic; }
    replace.set(idx[0], { idx, kept: kept.map(p => p.s) });
    changes.push({ from: idx.map(i => syl[i].text).join(' '), to: kept.map(p => p.s.text).join('-') });
  }
  if (!replace.size) return changes;
  const drop = new Set();
  for (const r of replace.values()) r.idx.forEach(i => drop.add(i));
  const res = [];
  syl.forEach((s, i) => { if (replace.has(i)) res.push(...replace.get(i).kept); else if (!drop.has(i)) res.push(s); });
  syl.length = 0; syl.push(...res);
  return changes;
}

// how well a list fits a row: the share of its longer words the list knows
// (as more than a rarity), and their mean log frequency (which tells a
// German row from English: web English knows "und" and "ich", rarely)
function fit(syl, lex) {
  let n = 0, k = 0, sum = 0;
  for (const idx of wordsOf(syl)) {
    const t = norm(idx.map(i => syl[i].text).join('').replace(/[^\p{L}'’]/gu, ''));
    if (t.length < 3) continue;
    n++;
    const f = lf(lex, t);
    sum += f;
    if (f >= -6) k++;
  }
  return n ? { hit: k / n, mean: sum / n } : { hit: 0, mean: -9 };
}

// Corrects the rows (arrays of syllables) of a page: each row against the
// list of its language (the loaded list it matches best; lists of the
// second-pass languages are loaded only when English and German both fit
// badly).  Returns the changes made.
async function correctRows(rows, opts = {}) {
  const o = Object.assign({}, OPTS, opts);
  const first = ['en', 'de'];
  if (o.lang && !first.includes(o.lang)) first.unshift(o.lang);
  const lists = new Map();
  for (const l of first) { const x = await loadLexicon(l); if (x) lists.set(l, x); }
  if (!lists.size) return [];
  const pick = (syl) => { let best = null, bf = null; for (const [l, x] of lists) { const f = fit(syl, x); if (!bf || f.mean > bf.mean) { bf = f; best = l; } } return [best, bf ? bf.hit : 0]; };
  let loadedMore = false;
  const changes = [];
  for (const syl of rows) {
    let [l, r] = pick(syl);
    if (r < 0.6 && !loadedMore && o.more !== false) {
      loadedMore = true;
      for (const m of LANGS) if (!lists.has(m)) { const x = await loadLexicon(m); if (x) lists.set(m, x); }
      [l, r] = pick(syl);
    }
    // a row the lists hardly know (Latin, another language, noise) is left alone
    if (r < (o.minHit != null ? o.minHit : 0.5)) continue;
    for (const c of correctRow(syl, lists.get(l), o, [...lists].filter(([k]) => k !== l).map(([, x]) => x))) changes.push(Object.assign(c, { lang: l }));
  }
  return changes;
}

// Lines of plain text (stanzas printed below the music): each read as a row
// of syllables (hyphenated words in pieces), corrected, and written back.
function toSyl(line) {
  const syl = [];
  for (const tok of line.split(/\s+/).filter(Boolean)) {
    const ps = tok.split(/(?<=\p{L})-(?=\p{L})/u);
    ps.forEach((p, k) => syl.push({ text: p, syllabic: ps.length === 1 ? 'single' : k === 0 ? 'begin' : k === ps.length - 1 ? 'end' : 'middle', x0: 0, x1: 0 }));
  }
  return syl;
}
const fromSyl = (syl) => syl.map((x, i) => x.text + (i + 1 < syl.length ? (x.syllabic === 'begin' || x.syllabic === 'middle' ? '-' : ' ') : '')).join('');
async function correctLines(lines, opts = {}) {
  const rows = lines.map(toSyl);
  const changes = await correctRows(rows, opts);
  return { lines: rows.map((r, i) => (r.some(x => x.lex) ? fromSyl(r) : lines[i])), changes };
}

module.exports = { correctLines,  loadLexicon, correctWord, correctRow, correctRows, variants, CONFUSIONS, _wordsOf: wordsOf, _fit: fit };
