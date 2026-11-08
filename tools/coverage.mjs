#!/usr/bin/env node
// Coverage matrix: per-symbol / per-layout support of the OMR app, plus speed and memory.
//
//   node mvp/tools/eval.mjs --set coverage --out mvp/work/eval-coverage.json            (accuracy run)
//   node mvp/tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 \
//        --out mvp/work/eval-coverage-perf.json                                        (optional perf run)
//   node tools/coverage.mjs --eval mvp/work/eval-coverage.json [--perf mvp/work/eval-coverage-perf.json]
//        [--coverage-dir corpus/coverage] [--md docs/COVERAGE.md] [--json docs/coverage.json]
//
// Reads an eval.mjs report for --set coverage, each item's meta.json + truth.musicxml and the
// MusicXML the app produced, and for every taxonomy tag computes:
//   occurrences  meta.counts summed over items (the generators' count rules), falling back to
//                this tool's own count from truth.musicxml
//   emitted      how often the app's MusicXML contains the corresponding element (the same tagger
//                run on the app output: <rest>, <dot/>, <time-modification>, <clef>, <fifths>,
//                <accidental>, <tie>, <slur>, <articulations>, <dynamics>, <octave-shift>, ...)
//   accuracy     recall on the truth instances, per scan variant (clean / scan / scan-severe):
//                note-level tags: truth notes carrying the tag that are aligned to an app note with
//                the right pitch AND the tag's feature (element tags: the same element, e.g. <dot/>,
//                <beam>, <slur>, <staccato/>; semantic tags: the meaning, e.g. duration for note
//                values, spelled pitch for accidentals, sounding pitch under an ottava);
//                header tags (clef/key/time): exact-match rate of the change at the aligned measure
//                (+-1); direction/structure tags: same element and value at the aligned measure (+-1)
//   read         share of truth notes carrying the tag that the app read with the right pitch
//                (whether or not it kept the mark)
//   status       supported (accuracy >= 0.8), partial (0.2-0.8), unsupported (< 0.2 or the element
//                is never emitted), from the 'scan' variant (fallback clean). Semantic tags whose
//                MusicXML element is never emitted are capped at partial.
//   confusion    on clean.pdf: false notes (app notes not matching truth) per truth note in the
//                measures holding the tag, vs. the other measures. "not confused" when the excess
//                is <= 0.05 per note: the app may ignore the mark but it does not invent notes.
// Layouts (meta.layout): part count match, part-name score, right-part share, aggregate.
// Performance: ms per page and peak RSS by source dpi, page size and page count (perf family, or
// every item when the perf family is absent) and least-squares fits ms/page ~ megapixels/page.
// Notes and rests are aligned with all parts merged (Needleman-Wunsch, as in eval.mjs), so symbol
// accuracy does not depend on part splitting; part splitting is scored under layouts.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
if (argv.includes('-h') || argv.includes('--help')) {
  const L = fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n'); let e = 1; while (e < L.length && L[e].startsWith('//')) e++;
  console.log(L.slice(1, e).join('\n')); process.exit(0);
}
const EVAL = path.resolve(opt('--eval', path.join(ROOT, 'mvp/work/eval-coverage.json')));
const PERF = opt('--perf', null) ? path.resolve(opt('--perf')) : null;
const MD = path.resolve(opt('--md', path.join(ROOT, 'docs/COVERAGE.md')));
const JSON_OUT = path.resolve(opt('--json', path.join(ROOT, 'docs/coverage.json')));
const COV_DIR_ARG = opt('--coverage-dir', null);
const T_SUP = 0.8, T_PART = 0.2, CONF_EXCESS = 0.05, CONF_MIN_SURPLUS = 3, CONF_MIN_NOTES = 10;

// ---------------------------------------------------------------- taxonomy
const TAXONOMY = {
  notes: ['note-breve', 'note-whole', 'note-half', 'note-quarter', 'note-8th', 'note-16th', 'note-32nd', 'note-64th', 'dot', 'double-dot', 'chord', 'beam', 'flag', 'stem-up', 'stem-down', 'ledger-above', 'ledger-below', 'grace', 'grace-slash', 'cue-note', 'tremolo'],
  rests: ['rest-breve', 'rest-whole', 'rest-half', 'rest-quarter', 'rest-8th', 'rest-16th', 'rest-32nd', 'rest-64th', 'rest-dotted', 'rest-whole-bar', 'rest-multibar'],
  pitch: ['clef-treble', 'clef-bass', 'clef-alto', 'clef-tenor', 'clef-soprano', 'clef-treble-8vb', 'clef-treble-8va', 'clef-bass-8vb', 'clef-change', 'key-0',
    ...[1, 2, 3, 4, 5, 6, 7].map(n => 'key-s' + n), ...[1, 2, 3, 4, 5, 6, 7].map(n => 'key-f' + n), 'key-change',
    'acc-sharp', 'acc-flat', 'acc-natural', 'acc-double-sharp', 'acc-double-flat', 'acc-courtesy', 'ottava-8va', 'ottava-8vb', 'ottava-15ma'],
  time: ['time-2-4', 'time-3-4', 'time-4-4', 'time-2-2', 'time-3-2', 'time-6-8', 'time-9-8', 'time-12-8', 'time-5-4', 'time-5-8', 'time-7-8', 'time-common', 'time-cut', 'time-change', 'pickup',
    'tuplet-3', 'tuplet-2', 'tuplet-5', 'tuplet-6', 'tuplet-7', 'tuplet-nested', 'tie', 'tie-across-system'],
  marks: ['slur', 'staccato', 'staccatissimo', 'accent', 'tenuto', 'marcato', 'fermata', 'trill', 'mordent', 'turn', 'arpeggio', 'breath', 'dyn-pp', 'dyn-p', 'dyn-mp', 'dyn-mf', 'dyn-f', 'dyn-ff', 'dyn-sfz',
    'hairpin-cresc', 'hairpin-dim', 'pedal', 'fingering', 'text-expression', 'tempo-mark', 'metronome', 'rehearsal-mark', 'chord-symbol'],
  structure: ['barline-double', 'barline-final', 'repeat-start', 'repeat-end', 'volta-1', 'volta-2', 'segno', 'coda', 'dc', 'ds', 'fine', 'system-break', 'page-break', 'multi-page'],
  lyrics: ['lyrics', 'lyrics-multi-verse', 'lyrics-melisma', 'lyrics-extender', 'lyrics-hyphen', 'lyrics-elision', 'lyrics-non-ascii', 'stanza-text'],
};
const LAYOUTS = ['melody', 'melody-lyrics', 'piano', 'voice-piano', 'choir-closed-satb', 'choir-open-satb', 'choir-sab', 'choir-ttbb', 'choir-ssaa', 'choir-piano', 'organ', 'string-quartet', 'orchestral',
  'lead-sheet', 'hymnal-stanzas', 'divisi', 'cross-staff', 'two-voices-one-staff-instrument', 'percussion-none'];
const TAG_FAMILY = {};
for (const [f, ts] of Object.entries(TAXONOMY)) for (const t of ts) TAG_FAMILY[t] = f;
const familyOf = t => TAG_FAMILY[t] || (/^x-(note|grace|cue|stem|beam)/.test(t) ? 'notes' : /^x-rest/.test(t) ? 'rests' : /^x-(clef|key|acc|ottava)/.test(t) ? 'pitch' : /^x-(time|tuplet)/.test(t) ? 'time'
  : /^x-(dyn|artic|orn|text|words)/.test(t) ? 'marks' : /^x-(bar|repeat|volta)/.test(t) ? 'structure' : /^x-lyr/.test(t) ? 'lyrics' : 'other');

// How each tag is scored. kind: 'note' (truth notes carrying the tag, aligned), 'rest', 'grace', 'cue',
// 'event' (header/direction/structure element at the aligned measure), 'pickup', 'multirest',
// 'multipage', 'lyrprec' (lyric precision), 'meta' (only declared in meta.json, cannot be measured).
// sem: semantic check (no element needed); elem: the MusicXML element the semantic tag maps to (cap).
const NOTE_VALUE = { 'note-breve': 'breve', 'note-whole': 'whole', 'note-half': 'half', 'note-quarter': 'quarter', 'note-8th': 'eighth', 'note-16th': '16th', 'note-32nd': '32nd', 'note-64th': '64th' };
const REST_VALUE = { 'rest-breve': 'breve', 'rest-whole': 'whole', 'rest-half': 'half', 'rest-quarter': 'quarter', 'rest-8th': 'eighth', 'rest-16th': '16th', 'rest-32nd': '32nd', 'rest-64th': '64th' };
function tagSpec(tag) {
  if (NOTE_VALUE[tag]) return { kind: 'note', sem: true, what: 'duration of the aligned note' };
  if (REST_VALUE[tag] || tag === 'rest-dotted' || tag === 'rest-whole-bar' || /^x-rest-/.test(tag)) return { kind: 'rest', sem: true, what: 'aligned rest with the same duration' };
  if (/^x-note-/.test(tag)) return { kind: 'note', sem: true, what: 'duration' };
  switch (tag) {
    case 'flag': return { kind: 'note', sem: true, what: 'duration of the flagged note' };
    case 'ledger-above': case 'ledger-below': return { kind: 'note', sem: true, what: 'pitch' };
    case 'acc-sharp': case 'acc-flat': case 'acc-natural': case 'acc-double-sharp': case 'acc-double-flat': case 'acc-courtesy':
      return { kind: 'note', sem: true, elem: '<accidental>', what: 'spelled pitch (step, alter, octave)' };
  }
  if (/^x-acc-/.test(tag)) return { kind: 'note', sem: true, elem: '<accidental>', what: 'spelled pitch (step, alter, octave)' };
  switch (tag) {
    case 'ottava-8va': case 'ottava-8vb': case 'ottava-15ma': return { kind: 'note', sem: true, elem: '<octave-shift>', what: 'sounding pitch of the notes under the line' };
    case 'grace': case 'grace-slash': return { kind: 'grace', what: tag === 'grace' ? '<grace/> note, same pitch, aligned measure' : '<grace slash="yes"/>' };
    case 'cue-note': return { kind: 'cue', what: '<cue/> note, same pitch, aligned measure' };
    case 'pickup': return { kind: 'pickup', sem: true, what: 'first measure has the pickup length' };
    case 'rest-multibar': return { kind: 'multirest', sem: true, elem: '<multiple-rest>', what: 'every bar of the block read as a full-bar rest' };
    case 'multi-page': return { kind: 'multipage', sem: true, what: 'pitch recall of the notes on pages 2+' };
    case 'stanza-text': return { kind: 'lyrprec', sem: true, what: 'lyric precision (stanza text blocks not underlaid as lyrics)' };
    case 'tuplet-nested': return { kind: 'note', what: 'duration + <time-modification>' };
  }
  if (/^(clef-|key-|time-|x-clef|x-key|x-time)/.test(tag)) return { kind: 'event', what: 'same clef/key/time at the aligned measure (+-1)' };
  if (/^(dyn-|x-dyn|hairpin|pedal|text-expression|tempo-mark|metronome|rehearsal-mark|chord-symbol|barline-|repeat-|volta-|segno|coda|dc|ds|fine|system-break|page-break|x-bar|x-volta)/.test(tag) || ['segno', 'coda', 'dc', 'ds', 'fine'].includes(tag))
    return { kind: 'event', what: 'same element/value at the aligned measure (+-1)' };
  if (/^tuplet-|^x-tuplet/.test(tag)) return { kind: 'note', what: 'duration + <time-modification> ratio' };
  if (/^(lyrics|x-lyr)/.test(tag)) return { kind: 'note', what: 'lyric on the aligned note' };
  if (tag === 'dot' || tag === 'double-dot') return { kind: 'note', what: '<dot/> count + duration' };
  return { kind: 'note', what: 'element on the aligned note' };
}

// ---------------------------------------------------------------- XML parser (as in eval.mjs)
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };
const decode = s => s.replace(/&(#x[0-9a-f]+|#\d+|\w+);/gi, (m, e) => e[0] === '#' ? String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : +e.slice(1)) : (ENT[e] ?? m));
function parseXML(s) {
  const root = { name: '#root', attrs: {}, children: [], text: '' };
  const stack = [root];
  const re = /<!--[\s\S]*?-->|<!\[CDATA\[([\s\S]*?)\]\]>|<\?[\s\S]*?\?>|<!DOCTYPE(?:[^>\[]|\[[\s\S]*?\])*>|<\/([^\s>]+)\s*>|<([^\s>\/!?]+)((?:\s+[^\s=\/>]+\s*=\s*(?:"[^"]*"|'[^']*'))*)\s*(\/?)>|([^<]+)/g;
  let m;
  while ((m = re.exec(s))) {
    const top = stack[stack.length - 1];
    if (m[1] !== undefined) top.text += m[1];
    else if (m[2]) { if (stack.length > 1) stack.pop(); }
    else if (m[3]) {
      const attrs = {};
      m[4].replace(/([^\s=]+)\s*=\s*("([^"]*)"|'([^']*)')/g, (_, k, __, a, b) => { attrs[k] = decode(a ?? b); });
      const el = { name: m[3], attrs, children: [], text: '' };
      top.children.push(el);
      if (!m[5]) stack.push(el);
    } else if (m[6]) top.text += decode(m[6]);
  }
  return root;
}
const kids = (el, name) => el ? el.children.filter(c => c.name === name) : [];
const kid = (el, name) => el ? el.children.find(c => c.name === name) : undefined;
const txt = (el, name) => { const k = kid(el, name); return k ? k.text.trim() : undefined; };
function find(el, name) { if (!el) return; if (el.name === name) return el; for (const c of el.children) { const r = find(c, name); if (r) return r; } }

// ---------------------------------------------------------------- MusicXML -> tagged notes + events
const STEPI = { C: 0, D: 1, E: 2, F: 3, G: 4, A: 5, B: 6 };
const STEP = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const TYPEQ = { maxima: 32, long: 16, breve: 8, whole: 4, half: 2, quarter: 1, eighth: 0.5, '16th': 0.25, '32nd': 0.125, '64th': 0.0625, '128th': 0.03125 };
const TYPE_TAG = { breve: 'note-breve', whole: 'note-whole', half: 'note-half', quarter: 'note-quarter', eighth: 'note-8th', '16th': 'note-16th', '32nd': 'note-32nd', '64th': 'note-64th' };
const REST_TAG = { breve: 'rest-breve', whole: 'rest-whole', half: 'rest-half', quarter: 'rest-quarter', eighth: 'rest-8th', '16th': 'rest-16th', '32nd': 'rest-32nd', '64th': 'rest-64th' };
const CLEF_TAG = { 'G2/0': 'clef-treble', 'F4/0': 'clef-bass', 'C3/0': 'clef-alto', 'C4/0': 'clef-tenor', 'C1/0': 'clef-soprano', 'G2/-1': 'clef-treble-8vb', 'G2/1': 'clef-treble-8va', 'F4/-1': 'clef-bass-8vb' };
const ACC_TAG = { sharp: 'acc-sharp', flat: 'acc-flat', natural: 'acc-natural', 'double-sharp': 'acc-double-sharp', 'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat' };
const ARTIC_TAG = { staccato: 'staccato', staccatissimo: 'staccatissimo', accent: 'accent', tenuto: 'tenuto', 'strong-accent': 'marcato', 'breath-mark': 'breath' };
const ORN_TAG = { 'trill-mark': 'trill', mordent: 'mordent', 'inverted-mordent': 'mordent', turn: 'turn', 'inverted-turn': 'turn', 'delayed-turn': 'turn', 'delayed-inverted-turn': 'turn' };
const DYN_TAG = { pp: 'dyn-pp', p: 'dyn-p', mp: 'dyn-mp', mf: 'dyn-mf', f: 'dyn-f', ff: 'dyn-ff', sfz: 'dyn-sfz' };
const normText = s => (s || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const r4 = x => Math.round(x * 1e4) / 1e4;

function clefBottom(c) {
  // diatonic number (octave*7 + step) of the bottom staff line
  const ref = c.sign === 'G' ? 32 : c.sign === 'F' ? 24 : c.sign === 'C' ? 28 : null; // G4, F3, C4
  if (ref == null) return null;
  return ref - 2 * ((+c.line || (c.sign === 'G' ? 2 : c.sign === 'F' ? 4 : 3)) - 1) + 7 * (c.oct || 0);
}

function extract(xml) {
  const doc = parseXML(xml);
  const sp = find(doc, 'score-partwise');
  if (!sp) throw new Error('no score-partwise root');
  const names = {};
  for (const s of kids(kid(sp, 'part-list'), 'score-part')) names[s.attrs.id] = txt(s, 'part-name') || '';
  const S = { parts: [], notes: [], graces: [], cues: [], events: [], measures: 0, sysBreaks: new Set(), pageBreaks: new Set(), mlen: [], tsig: [] };
  kids(sp, 'part').forEach((p, pi) => {
    let div = 1;
    const clef = {}, ott = {}, tupOpen = {};
    let key = null, time = null, firstAttrs = true;
    const measures = kids(p, 'measure');
    S.measures = Math.max(S.measures, measures.length);
    const pnotes = [];
    const mlen = [], tsig = [];
    const ev = (o) => { o.pi = pi; S.events.push(o); };
    measures.forEach((m, mi) => {
      let t = 0, last = 0, maxT = 0;
      for (const c of m.children) {
        if (c.name === 'print') {
          if (c.attrs['new-system'] === 'yes' && mi > 0) S.sysBreaks.add(mi);
          if (c.attrs['new-page'] === 'yes' && mi > 0) S.pageBreaks.add(mi);
        } else if (c.name === 'attributes') {
          const d = +txt(c, 'divisions'); if (d > 0) div = d;
          for (const k of kids(c, 'key')) {
            const f = txt(k, 'fifths'); if (f === undefined) continue;
            const v = +f;
            if (key !== v) {
              const tags = [v === 0 ? 'key-0' : v > 0 ? `key-s${v}` : `key-f${-v}`];
              if (key !== null || !firstAttrs) tags.push('key-change');
              ev({ type: 'key', m: mi, tags, value: v });
              key = v;
            }
          }
          for (const tm of kids(c, 'time')) {
            const b = txt(tm, 'beats'), bt = txt(tm, 'beat-type'), sym = tm.attrs.symbol || '';
            const v = `${b}/${bt}/${sym === 'common' || sym === 'cut' ? sym : ''}`;
            if (time !== v) {
              const tags = [sym === 'common' ? 'time-common' : sym === 'cut' ? 'time-cut' : `time-${b}-${bt}`];
              if (!TAG_FAMILY[tags[0]]) tags[0] = 'x-' + tags[0];
              if (time !== null || !firstAttrs) tags.push('time-change');
              ev({ type: 'time', m: mi, tags, value: v });
              time = v;
            }
          }
          for (const cl of kids(c, 'clef')) {
            const st = cl.attrs.number || '1';
            const cv = { sign: txt(cl, 'sign'), line: txt(cl, 'line') || '', oct: +(txt(cl, 'clef-octave-change') || 0) };
            const v = `${cv.sign}${cv.line}/${cv.oct}`;
            const prev = clef[st];
            if (!prev || prev.v !== v) {
              const tags = [CLEF_TAG[v] || `x-clef-${cv.sign === 'percussion' ? 'percussion' : (cv.sign + cv.line + (cv.oct ? (cv.oct > 0 ? '+' : '') + cv.oct : '')).toLowerCase()}`];
              if (prev || !firstAttrs) tags.push('clef-change');
              ev({ type: 'clef', m: mi, tags, value: v, staff: st });
            }
            clef[st] = { ...cv, v };
          }
          for (const ms of kids(c, 'measure-style')) {
            const mr = kid(ms, 'multiple-rest');
            if (mr) ev({ type: 'multirest', m: mi, tags: ['rest-multibar'], n: +mr.text.trim() || 1 });
          }
          firstAttrs = false;
        } else if (c.name === 'backup') t -= (+txt(c, 'duration') || 0) / div;
        else if (c.name === 'forward') { t += (+txt(c, 'duration') || 0) / div; maxT = Math.max(maxT, t); }
        else if (c.name === 'direction') {
          const st = txt(c, 'staff') || '1';
          const snd = kid(c, 'sound');
          const tags = new Set(); let words = '';
          for (const dt of kids(c, 'direction-type')) for (const x of dt.children) {
            const n = x.name;
            if (n === 'words') {
              const w = x.text.trim(); if (!w) continue;
              words += (words ? ' ' : '') + w;
              if (/^d\.?\s*c\.?(\s|$|al)/i.test(w) || /da capo/i.test(w)) tags.add('dc');
              else if (/^d\.?\s*s\.?(\s|$|al)/i.test(w) || /dal segno/i.test(w)) tags.add('ds');
              else if (/^fine\.?$/i.test(w)) tags.add('fine');
              else if (/^(to )?coda$/i.test(w)) { /* text twin of the coda sign */ }
              // generators' rule: bold words or a <sound tempo> are tempo marks, other words are expressions
              else if ((snd && snd.attrs.tempo) || x.attrs['font-weight'] === 'bold') tags.add('tempo-mark');
              else tags.add('text-expression');
            } else if (n === 'rehearsal') tags.add('rehearsal-mark');
            else if (n === 'dynamics') for (const d of x.children) tags.add(DYN_TAG[d.name] || 'x-dyn-' + d.name);
            else if (n === 'wedge') { if (x.attrs.type === 'crescendo') tags.add('hairpin-cresc'); else if (x.attrs.type === 'diminuendo') tags.add('hairpin-dim'); }
            else if (n === 'pedal') { if (x.attrs.type === 'start') tags.add('pedal'); }
            else if (n === 'metronome') tags.add('metronome');
            else if (n === 'segno') tags.add('segno');
            else if (n === 'coda') tags.add('coda');
            else if (n === 'octave-shift') {
              const ty = x.attrs.type, size = +(x.attrs.size || 8);
              if (ty === 'up' || ty === 'down') {
                const tag = size === 15 ? (ty === 'down' ? 'ottava-15ma' : 'x-ottava-15mb') : (ty === 'down' ? 'ottava-8va' : 'ottava-8vb');
                ott[st] = { ty, k: size === 15 ? 2 : 1, tag };
                tags.add(tag);
              } else if (ty === 'stop') ott[st] = null;
            }
          }
          if (snd) {
            if (snd.attrs.dacapo === 'yes') tags.add('dc');
            if (snd.attrs.dalsegno) tags.add('ds');
            if (snd.attrs.fine) tags.add('fine');
          }
          for (const tg of tags) ev({ type: 'dir', m: mi, tags: [tg], value: tg === 'text-expression' || tg === 'tempo-mark' ? normText(words) : '' });
        } else if (c.name === 'harmony') {
          const root = kid(c, 'root');
          ev({ type: 'harmony', m: mi, tags: ['chord-symbol'], value: `${txt(root, 'root-step') || ''}${txt(root, 'root-alter') || ''}:${txt(c, 'kind') || ''}` });
        } else if (c.name === 'barline') {
          const style = txt(c, 'bar-style') || '';
          const rep = kid(c, 'repeat');
          const tags = [];
          if (rep) tags.push(rep.attrs.direction === 'forward' ? 'repeat-start' : 'repeat-end');
          else if (style === 'light-heavy') tags.push('barline-final');
          else if (style === 'light-light') tags.push('barline-double');
          else if (style && style !== 'regular') tags.push('x-bar-' + style);
          const end = kid(c, 'ending');
          if (end && end.attrs.type === 'start') for (const num of (end.attrs.number || '').replace(/\s/g, '').split(',')) if (num) tags.push(num === '1' || num === '2' ? `volta-${num}` : `x-volta-${num}`);
          for (const tg of tags) ev({ type: 'bar', m: mi, tags: [tg], value: '' });
        } else if (c.name === 'note') {
          const gr = kid(c, 'grace');
          const cue = !!kid(c, 'cue') || (kid(c, 'type') && kid(c, 'type').attrs.size === 'cue');
          const chord = !!kid(c, 'chord');
          const type = txt(c, 'type');
          const dots = kids(c, 'dot').length;
          let dur = gr ? 0 : (+txt(c, 'duration') || 0) / div;
          if (!dur && !gr) dur = (TYPEQ[type] || 0) * (2 - Math.pow(0.5, dots));
          const on = chord ? last : t;
          if (!chord && !gr) { last = t; t += dur; maxT = Math.max(maxT, t); }
          const pt = kid(c, 'pitch'), up = kid(c, 'unpitched'), restEl = kid(c, 'rest');
          const n = { pi, m: mi, on: r4(on), dur: r4(dur), type, dots, chord, rest: !!restEl || (!pt && !up), staff: txt(c, 'staff') || '1', voice: txt(c, 'voice') || '1', tags: new Set(), lyrics: [] };
          if (pt) { n.step = txt(pt, 'step'); n.alter = Math.round(+txt(pt, 'alter') || 0); n.oct = +txt(pt, 'octave'); }
          else if (up) { n.step = txt(up, 'display-step'); n.alter = 0; n.oct = +txt(up, 'display-octave'); n.unpitched = true; }
          n.midi = n.rest ? null : (n.oct + 1) * 12 + STEP[n.step] + n.alter;
          n.spell = n.rest ? null : `${n.step}${n.alter}${n.oct}`;
          n.stem = txt(c, 'stem');
          n.beam = kids(c, 'beam').length > 0;
          const acc = kid(c, 'accidental');
          if (acc) { n.acc = acc.text.trim(); if (ACC_TAG[n.acc]) n.tags.add(ACC_TAG[n.acc]); else n.tags.add('x-acc-' + n.acc); if (['yes'].includes(acc.attrs.cautionary) || acc.attrs.parentheses === 'yes' || acc.attrs.bracket === 'yes') n.tags.add('acc-courtesy'); }
          const tmEl = kid(c, 'time-modification');
          if (tmEl) n.tm = `${txt(tmEl, 'actual-notes')}:${txt(tmEl, 'normal-notes')}`;
          for (const tie of kids(c, 'tie')) if (tie.attrs.type === 'start') n.tieStart = true;
          const vk = `${n.staff}:${n.voice}`;
          const open = tupOpen[vk] ||= new Set();
          const stops = [];
          let twoNoteTrem = false;
          for (const nt of kids(c, 'notations')) for (const x of nt.children) {
            if (x.name === 'tied' && x.attrs.type === 'start') n.tieStart = true;
            else if (x.name === 'slur' && x.attrs.type === 'start') n.tags.add('slur');
            else if (x.name === 'tuplet') { const num = x.attrs.number || '1'; if (x.attrs.type === 'start') open.add(num); else if (x.attrs.type === 'stop') stops.push(num); }
            else if (x.name === 'fermata') n.tags.add('fermata');
            else if (x.name === 'arpeggiate') n.tags.add('arpeggio');
            else if (x.name === 'articulations') for (const a of x.children) n.tags.add(ARTIC_TAG[a.name] || 'x-artic-' + a.name);
            else if (x.name === 'ornaments') for (const o of x.children) {
              if (o.name === 'tremolo') { const ty = o.attrs.type || 'single'; if (ty === 'single' || ty === 'start') n.tags.add('tremolo'); if (ty !== 'single') twoNoteTrem = true; }
              else if (ORN_TAG[o.name]) n.tags.add(ORN_TAG[o.name]);
              else if (o.name !== 'accidental-mark') n.tags.add('x-orn-' + o.name);
            } else if (x.name === 'technical') { for (const f of kids(x, 'fingering')) n.tags.add('fingering'); }
            else if (x.name === 'dynamics') for (const d of x.children) ev({ type: 'dir', m: mi, tags: [DYN_TAG[d.name] || 'x-dyn-' + d.name], value: '' });
          }
          if (n.tm && !twoNoteTrem) { // two-note tremolos carry a <time-modification> but are not tuplets
            const depth = Math.max(1, open.size);
            n.tupDepth = depth;
            if (depth >= 2) n.tags.add('tuplet-nested');
            else { const a = n.tm.split(':')[0]; const tg = `tuplet-${a}`; n.tags.add(TAG_FAMILY[tg] ? tg : 'x-' + tg); }
          }
          for (const s of stops) open.delete(s);
          if (n.tieStart) n.tags.add('tie');
          kids(c, 'lyric').forEach((l, k) => {
            const raw = kids(l, 'text').map(x => x.text).join(kids(l, 'elision').length ? '_' : '');
            const ly = { num: l.attrs.number || String(k + 1), text: normText(raw), raw, syl: txt(l, 'syllabic') || 'single', extend: !!kid(l, 'extend') && (kid(l, 'extend').attrs.type || 'start') !== 'stop', elision: !!kid(l, 'elision') };
            if (ly.text) n.lyrics.push(ly);
          });
          if (n.lyrics.length) {
            n.tags.add('lyrics');
            if (n.lyrics.some(l => +l.num >= 2)) n.tags.add('lyrics-multi-verse');
            if (n.lyrics.some(l => l.extend)) n.tags.add('lyrics-extender');
            if (n.lyrics.some(l => l.syl === 'begin' || l.syl === 'middle')) n.tags.add('lyrics-hyphen');
            if (n.lyrics.some(l => l.elision)) n.tags.add('lyrics-elision');
            if (n.lyrics.some(l => /[^\x00-\x7f]/.test(l.raw))) n.tags.add('lyrics-non-ascii');
          }
          if (n.rest) {
            if (restEl && restEl.attrs.measure === 'yes') n.tags.add('rest-whole-bar');
            else { n.tags.add(REST_TAG[type] || (type ? 'x-rest-' + type : 'rest-whole-bar')); if (dots) n.tags.add('rest-dotted'); }
            if (dots === 1) n.tags.add('dot'); else if (dots === 2) n.tags.add('double-dot');
            n.measureRest = n.tags.has('rest-whole-bar');
          } else if (gr) {
            n.grace = true; n.slash = gr.attrs.slash === 'yes';
            n.tags.add('grace'); if (n.slash) n.tags.add('grace-slash');
          } else if (cue) {
            n.cue = true; n.tags.add('cue-note');
          } else {
            n.tags.add(TYPE_TAG[type] || (type ? 'x-note-' + type : 'x-note-untyped'));
            if (dots === 1) n.tags.add('dot'); else if (dots === 2) n.tags.add('double-dot');
            if (!n.unpitched) {
              const cl = clef[n.staff] || { sign: 'G', line: '2', oct: 0 };
              const bottom = clefBottom(cl);
              const o = ott[n.staff];
              if (o) n.tags.add(o.tag);
              if (bottom != null) {
                const disp = n.oct * 7 + STEPI[n.step] + (o ? (o.ty === 'down' ? -7 : 7) * o.k : 0);
                const pos = disp - bottom;
                if (pos >= 10) n.tags.add('ledger-above'); else if (pos <= -2) n.tags.add('ledger-below');
              }
            }
            if (!chord) {
              if (n.stem === 'up') n.tags.add('stem-up'); else if (n.stem === 'down') n.tags.add('stem-down');
              if (['eighth', '16th', '32nd', '64th', '128th'].includes(type) && !n.beam && !twoNoteTrem) n.tags.add('flag');
            }
            if (n.beam) n.tags.add('beam');
          }
          if (chord && pnotes.length) {
            n.tags.add('chord');
            // the chord's first head (the note without <chord/>) is part of the chord too
            for (let k = pnotes.length - 1; k >= 0; k--) { const q = pnotes[k]; if (q.m === mi && !q.rest && !q.grace && q.on === n.on && q.staff === n.staff) { q.tags.add('chord'); q.inChord = true; if (!q.chord) break; } else break; }
            n.inChord = true;
          }
          pnotes.push(n);
        }
      }
      mlen[mi] = r4(maxT);
      const ts = time ? time.split('/') : null;
      tsig[mi] = ts ? (+ts[0]) * 4 / (+ts[1]) : null;
    });
    // ties across a system/page break
    for (const n of pnotes) if (n.tieStart && (S.sysBreaks.has(n.m + 1) || S.pageBreaks.has(n.m + 1)) && n.on + n.dur >= (mlen[n.m] || 0) - 1e-6) n.tags.add('tie-across-system');
    // melisma syllables: the next sung note of that verse is not the following note
    const main = pnotes.filter(n => !n.rest && !n.grace && !n.cue && !n.chord);
    const byVoice = {};
    for (const n of main) (byVoice[`${n.staff}:${n.voice}`] ||= []).push(n);
    for (const seq of Object.values(byVoice)) {
      seq.sort((a, b) => a.m - b.m || a.on - b.on);
      for (let i = 0; i < seq.length; i++) {
        const n = seq[i];
        for (const l of n.lyrics) {
          const nx = seq[i + 1];
          if (l.extend || (nx && !n.tieStart && !nx.lyrics.some(x => x.num === l.num) && seq.slice(i + 1).some(x => x.lyrics.some(y => y.num === l.num)))) { l.melisma = true; n.tags.add('lyrics-melisma'); }
        }
      }
    }
    for (const n of pnotes) { if (n.grace) S.graces.push(n); else if (n.cue) S.cues.push(n); else S.notes.push(n); }
    S.mlen[pi] = mlen; S.tsig[pi] = tsig;
    S.parts.push({ id: p.attrs.id, name: names[p.attrs.id] ?? p.attrs.id, measures: measures.length });
  });
  // pickup: measure 1 shorter than its time signature (or implicit)
  const firstLen = Math.max(0, ...S.mlen.map(a => a[0] || 0));
  const firstSig = S.tsig.map(a => a[0]).find(x => x);
  const implicit0 = kids(sp, 'part').some(p => { const m0 = kids(p, 'measure')[0]; return m0 && m0.attrs.implicit === 'yes'; });
  if ((firstSig && firstLen > 0 && firstLen < firstSig - 1e-3) || (implicit0 && firstLen > 0 && (!firstSig || firstLen < firstSig - 1e-3))) S.events.push({ type: 'pickup', m: 0, tags: ['pickup'], value: firstLen, pi: 0 });
  S.firstLen = firstLen;
  // system / page breaks: one event per break (not per part)
  for (const mi of S.sysBreaks) S.events.push({ type: 'print', m: mi, tags: ['system-break'], value: '', pi: -1 });
  for (const mi of S.pageBreaks) S.events.push({ type: 'print', m: mi, tags: ['page-break'], value: '', pi: -1 });
  return S;
}

// ---------------------------------------------------------------- alignment (Needleman-Wunsch, as eval.mjs + duration bonus)
function pairScore(a, b) {
  let s;
  if (a.rest && b.rest) s = 2 + (Math.abs(a.dur - b.dur) < 1e-3 ? 0.5 : 0);
  else if (a.rest || b.rest) return -2;
  else if (a.midi === b.midi) s = 3;
  else if (Math.abs(a.midi - b.midi) <= 2) s = 0.5;
  else s = -0.5;
  if (a.m === b.m) s += Math.abs(a.on - b.on) < 1e-3 ? 1 : 0.3;
  return s;
}
const GAP = -1;
const SCORE_WIDE = /^(barline-|repeat-|volta-|x-bar|x-volta|time-|x-time|key-|x-key|segno$|coda$|dc$|ds$|fine$|rehearsal-mark$|tempo-mark$|metronome$|system-break$|page-break$)/;
function align(T, P) {
  const n = T.length, m = P.length, W = m + 1;
  const tb = new Uint8Array((n + 1) * W);
  let prev = new Float64Array(W), cur = new Float64Array(W);
  for (let j = 1; j <= m; j++) { prev[j] = j * GAP; tb[j] = 3; }
  for (let i = 1; i <= n; i++) {
    cur[0] = i * GAP; tb[i * W] = 2;
    for (let j = 1; j <= m; j++) {
      const d = prev[j - 1] + pairScore(T[i - 1], P[j - 1]);
      const u = prev[j] + GAP, l = cur[j - 1] + GAP;
      if (d >= u && d >= l) { cur[j] = d; tb[i * W + j] = 1; }
      else if (u >= l) { cur[j] = u; tb[i * W + j] = 2; }
      else { cur[j] = l; tb[i * W + j] = 3; }
    }
    [prev, cur] = [cur, prev];
  }
  const pairs = [];
  let i = n, j = m;
  while (i > 0 || j > 0) {
    const t = tb[i * W + j];
    if (t === 1) { pairs.push([i - 1, j - 1]); i--; j--; }
    else if (t === 2) i--;
    else j--;
  }
  return pairs.reverse();
}
const order = (a, b) => a.m - b.m || a.on - b.on || (a.rest - b.rest) || (b.midi ?? -1) - (a.midi ?? -1) || (b.dur - a.dur) || a.pi - b.pi;

// ---------------------------------------------------------------- per item-variant evaluation
function lyricFor(p, l, k, sortedT) {
  if (!p || !p.lyrics.length) return null;
  return p.lyrics.find(z => z.num === l.num) || [...p.lyrics].sort((u, v) => +u.num - +v.num)[sortedT.indexOf(l)] || null;
}

function evaluateVariant(T, P, opts = {}) {
  // P may be null (crash / no output): every recall is 0, nothing emitted
  const Pn = P ? P.notes.slice().sort(order) : [];
  const Tn = T.notes.slice().sort(order);
  const pairs = align(Tn, Pn);
  const mate = new Map();
  for (const [a, b] of pairs) mate.set(Tn[a], Pn[b]);
  const matchedP = new Set();
  for (const [a, b] of pairs) if (!Tn[a].rest && !Pn[b].rest && Tn[a].midi === Pn[b].midi) matchedP.add(Pn[b]);
  // measure map truth -> produced by majority vote of pitch-correct pairs
  const votes = {};
  for (const [a, b] of pairs) { const x = Tn[a], y = Pn[b]; if (x.rest || y.rest || x.midi !== y.midi) continue; ((votes[x.m] ||= {})[y.m] = (votes[x.m][y.m] || 0) + 1); }
  const mmap = new Array(T.measures).fill(null);
  for (const [tm, v] of Object.entries(votes)) mmap[+tm] = +Object.entries(v).sort((a, b) => b[1] - a[1] || a[0] - b[0])[0][0];
  // measures without a vote take the offset of the nearest voted measure before them (after them for the
  // leading ones; identity when nothing matched)
  const firstVoted = mmap.findIndex(x => x != null);
  let off = firstVoted >= 0 ? mmap[firstVoted] - firstVoted : 0;
  for (let i = 0; i < mmap.length; i++) { if (mmap[i] != null) off = mmap[i] - i; else mmap[i] = i + off; }
  const pm = tm => (tm >= 0 && tm < mmap.length) ? mmap[tm] : tm;

  // produced next-note lyric info per voice for melisma checks
  if (P) {
    const byVoice = {};
    for (const n of P.notes) if (!n.rest && !n.chord) (byVoice[`${n.pi}:${n.staff}:${n.voice}`] ||= []).push(n);
    for (const seq of Object.values(byVoice)) { seq.sort((a, b) => a.m - b.m || a.on - b.on); seq.forEach((n, i) => { n.pNext = seq[i + 1] || null; }); }
  }

  const R = {}; // tag -> {n, hit, read, emitted, measures:Set(truth measures)}
  const rec = tag => (R[tag] ||= { n: 0, hit: 0, read: 0, readN: 0, emitted: 0, measures: new Set() });
  const durOk = (x, y) => y && Math.abs(x.dur - y.dur) < 1e-3;
  const pitchOk = (x, y) => y && !y.rest && !x.rest && x.midi === y.midi;
  // ---- notes and rests
  for (const t of Tn) {
    const p = mate.get(t);
    for (const tag of t.tags) {
      const spec = tagSpec(tag);
      const r = rec(tag); r.n++; r.measures.add(t.m);
      if (t.rest) {
        r.readN++; if (p && p.rest) r.read++;
        if (spec.kind === 'rest' ? (p && p.rest && durOk(t, p)) : (p && p.rest && durOk(t, p) && p.tags.has(tag))) r.hit++;
        continue;
      }
      r.readN++; const pok = pitchOk(t, p); if (pok) r.read++;
      if (!pok) continue;
      let ok;
      if (NOTE_VALUE[tag] || /^x-note-/.test(tag) || tag === 'flag') ok = durOk(t, p);
      else if (tag === 'dot' || tag === 'double-dot') ok = durOk(t, p) && p.dots === t.dots;
      else if (tag === 'chord') ok = !!p.inChord;
      else if (tag === 'beam') ok = p.beam;
      else if (tag === 'stem-up' || tag === 'stem-down') ok = p.stem === t.stem;
      else if (tag === 'ledger-above' || tag === 'ledger-below') ok = true;
      else if (/^acc-|^x-acc-/.test(tag)) ok = p.spell === t.spell;
      else if (/ottava/.test(tag)) ok = true;
      else if (tag === 'tie' || tag === 'tie-across-system') ok = !!p.tieStart;
      else if (tag === 'tuplet-nested') ok = durOk(t, p) && !!p.tm;
      else if (/^(x-)?tuplet-/.test(tag)) ok = durOk(t, p) && p.tm === t.tm;
      else if (/^lyrics/.test(tag)) {
        const sortedT = [...t.lyrics].sort((u, v) => +u.num - +v.num);
        const want = tag === 'lyrics' ? t.lyrics : tag === 'lyrics-multi-verse' ? t.lyrics.filter(l => +l.num >= 2) : tag === 'lyrics-extender' ? t.lyrics.filter(l => l.extend)
          : tag === 'lyrics-hyphen' ? t.lyrics.filter(l => l.syl === 'begin' || l.syl === 'middle') : tag === 'lyrics-elision' ? t.lyrics.filter(l => l.elision)
          : tag === 'lyrics-non-ascii' ? t.lyrics.filter(l => /[^\x00-\x7f]/.test(l.raw)) : tag === 'lyrics-melisma' ? t.lyrics.filter(l => l.melisma) : t.lyrics;
        ok = want.length > 0 && want.every(l => {
          const c = lyricFor(p, l, 0, sortedT); if (!c || c.text !== l.text) return false;
          if (tag === 'lyrics-extender') return c.extend;
          if (tag === 'lyrics-hyphen') return c.syl === l.syl;
          if (tag === 'lyrics-elision') return c.elision;
          if (tag === 'lyrics-melisma') return !(p.pNext && p.pNext.lyrics.some(z => z.num === c.num));
          return true;
        });
      } else ok = p.tags.has(tag);
      if (ok) r.hit++;
    }
  }
  // ---- grace and cue notes: same pitch in the aligned measure (any part)
  for (const [list, plist] of [[T.graces, P ? P.graces : []], [T.cues, P ? P.cues : []]]) {
    const used = new Set();
    for (const t of list) {
      const target = pm(t.m);
      const p = plist.find(q => !used.has(q) && q.midi === t.midi && Math.abs(q.m - target) <= 1 && !q.rest);
      if (p) used.add(p);
      for (const tag of t.tags) {
        if (!['grace', 'grace-slash', 'cue-note'].includes(tag) && !/^acc-/.test(tag) && !['slur', 'tie'].includes(tag)) continue;
        const r = rec(tag); r.n++; r.measures.add(t.m); r.readN++; if (p) r.read++;
        if (p && (tag === 'grace-slash' ? p.slash : /^acc-/.test(tag) ? p.spell === t.spell : tag === 'slur' || tag === 'tie' ? p.tags.has(tag) : true)) r.hit++;
      }
    }
  }
  // ---- events (clef/key/time/directions/barlines/prints)
  // one instance per (event, tag); score-wide marks (barlines, repeats, voltas, key/time, segno, ...) once per
  // measure for the whole score, so a quartet's four copies of a repeat sign count once on both sides
  const instances = (events) => {
    const out = [], seen = new Set();
    for (const e of events) {
      if (e.type === 'pickup' || e.type === 'multirest') continue;
      for (const tag of e.tags) {
        if (SCORE_WIDE.test(tag)) { const k = `${tag}|${e.m}|${e.value}`; if (seen.has(k)) continue; seen.add(k); }
        out.push({ ...e, tags: [tag] });
      }
    }
    return out;
  };
  const pev = P ? instances(P.events) : [];
  const usedE = new Map(); // tag -> produced events already matched for that tag
  const evs = instances(T.events);
  const hitE = new Map();  // truth event -> Set(tags matched)
  const sameValue = (e, q) => {
    if (e.type === 'clef' || e.type === 'key' || e.type === 'time') return q.type === e.type && q.value === e.value;
    if (e.type === 'dir' && e.value) return !!q.value && (q.value === e.value || q.value.includes(e.value) || e.value.includes(q.value));
    return true;
  };
  // exact (aligned) measure first, then +-1
  for (const pass of [0, 1]) for (const e of evs) for (const tag of e.tags) {
    const got = hitE.get(e) || new Set();
    if (got.has(tag)) continue;
    const used = usedE.get(tag) || new Set();
    const target = pm(e.m);
    const p = pev.find(q => !used.has(q) && q.tags.includes(tag) && Math.abs(q.m - target) <= pass && sameValue(e, q));
    if (p) { used.add(p); usedE.set(tag, used); got.add(tag); hitE.set(e, got); }
  }
  for (const e of evs) for (const tag of e.tags) { const r = rec(tag); r.n++; r.measures.add(e.m); if (e.type === 'print') r.measures.add(Math.max(0, e.m - 1)); if ((hitE.get(e) || new Set()).has(tag)) r.hit++; }
  // ---- pickup
  for (const e of T.events.filter(e => e.type === 'pickup')) { const r = rec('pickup'); r.n++; r.measures.add(0); if (P && Math.abs((P.firstLen || 0) - e.value) < 1e-3) r.hit++; }
  // ---- multi-bar rests: every bar of the block aligned to a produced rest of the same length
  for (const e of T.events.filter(e => e.type === 'multirest')) {
    const r = rec('rest-multibar'); r.n++;
    let ok = true;
    for (let k = 0; k < e.n; k++) {
      r.measures.add(e.m + k);
      const rs = Tn.filter(t => t.rest && t.m === e.m + k && t.pi === e.pi);
      if (!rs.length || !rs.every(t => { const p = mate.get(t); return p && p.rest && durOk(t, p); })) ok = false;
    }
    if (ok) r.hit++;
  }
  // ---- multi-page: pitch recall of the notes on page 2+
  if (T.pageBreaks.size || (opts.pages || 1) > 1) {
    const first = T.pageBreaks.size ? Math.min(...T.pageBreaks) : 0;
    const r = rec('multi-page');
    for (const t of Tn) if (!t.rest && t.m >= first) { r.n++; r.measures.add(t.m); if (pitchOk(t, mate.get(t))) r.hit++; }
    r.occ = 1;
  }
  // ---- lyric precision (stanza text must not become lyrics)
  {
    const r = rec('stanza-text');
    let pl = 0, good = 0;
    const back = new Map(); for (const [t, q] of mate) back.set(q, t);
    if (P) for (const p of P.notes) for (const l of p.lyrics) {
      pl++;
      const t = back.get(p);
      if (t && t.lyrics.some(x => x.text === l.text)) good++;
    }
    r.prec = { produced: pl, matched: good };
  }
  // ---- emitted counts: same tagger on the app output
  const emitted = {};
  if (P) {
    for (const n of [...P.notes, ...P.graces, ...P.cues]) for (const tg of n.tags) emitted[tg] = (emitted[tg] || 0) + 1;
    for (const e of P.events) for (const tg of e.tags) emitted[tg] = (emitted[tg] || 0) + 1;
    if (P.pageBreaks.size) emitted['multi-page'] = 1;
  }
  // ---- confusion: false notes in the measures that hold each tag vs elsewhere
  const truthPerM = {}, falsePerPM = {};
  for (const t of Tn) if (!t.rest) truthPerM[t.m] = (truthPerM[t.m] || 0) + 1;
  for (const p of Pn) if (!p.rest && !matchedP.has(p)) falsePerPM[p.m] = (falsePerPM[p.m] || 0) + 1;
  const conf = (ms) => {
    const pset = new Set([...ms].map(pm));
    let tin = 0, fin = 0, tout = 0, fout = 0;
    for (let m = 0; m < T.measures; m++) { if (ms.has(m)) tin += truthPerM[m] || 0; else tout += truthPerM[m] || 0; }
    for (const [m, f] of Object.entries(falsePerPM)) { if (pset.has(+m)) fin += f; else fout += f; }
    return { tin, fin, tout, fout };
  };
  for (const [tag, r] of Object.entries(R)) if (r.measures.size) r.conf = conf(r.measures);
  const allConf = conf(new Set());
  return { R, emitted, allConf, nTruth: Tn.filter(t => !t.rest).length, nFalse: Pn.filter(p => !p.rest && !matchedP.has(p)).length };
}

// ---------------------------------------------------------------- main
function main() {
// ---------------------------------------------------------------- load inputs
const readJSON = f => JSON.parse(fs.readFileSync(f, 'utf8'));
if (!fs.existsSync(EVAL)) { console.error(`eval report not found: ${EVAL}\nrun: node mvp/tools/eval.mjs --set coverage --out ${path.relative(ROOT, EVAL)}`); process.exit(2); }
const report = readJSON(EVAL);
const perfReport = PERF && fs.existsSync(PERF) ? readJSON(PERF) : null;
const covItems = report.items.filter(r => r.set === 'coverage');
if (!covItems.length) { console.error('no coverage items in ' + EVAL + ' (run eval.mjs with --set coverage)'); process.exit(2); }
const COV = path.resolve(COV_DIR_ARG || report.config.coverage_dir || path.join(ROOT, 'corpus/coverage'));
const OUTDIR = report.config.outputs;

const itemCache = new Map();
function loadItem(family, id) {
  const k = `${family}/${id}`;
  if (itemCache.has(k)) return itemCache.get(k);
  const d = path.join(COV, family, id);
  let o = null;
  try {
    const meta = readJSON(path.join(d, 'meta.json'));
    const truthXml = fs.readFileSync(path.join(d, 'truth.musicxml'), 'utf8');
    o = { family, id, dir: d, meta, truthXml, T: extract(truthXml) };
  } catch (e) { o = { family, id, dir: d, error: String(e.message || e) }; }
  itemCache.set(k, o);
  return o;
}

const variants = [];
const skipped = [...(report.skipped || [])];
const evalStart = Date.parse(report.when) - (report.wall_s || 0) * 1000;
const mtime = f => { try { return fs.statSync(f).mtimeMs; } catch { return Infinity; } };
for (const r of covItems) {
  const it = loadItem(r.family, r.item);
  if (it.error) { skipped.push({ id: r.id, why: it.error }); continue; }
  // generators may rewrite an item after the eval read it: its output no longer matches the files
  const changed = [path.join(it.dir, 'truth.musicxml'), path.join(it.dir, r.variant + '.pdf')].filter(f => mtime(f) > evalStart);
  if (changed.length) { skipped.push({ id: r.id, why: `${changed.map(f => path.basename(f)).join(', ')} changed after the eval run started (re-run eval)` }); continue; }
  const prodFile = path.join(OUTDIR, (r.key || `coverage__${r.family}__${r.item}__${r.variant}`) + '.musicxml');
  let P = null, perr = null;
  if (!r.crash && fs.existsSync(prodFile)) {
    const x = fs.readFileSync(prodFile, 'utf8');
    if (x.trim()) { try { P = extract(x); } catch (e) { perr = String(e.message || e); } }
  }
  const ev = evaluateVariant(it.T, P, { pages: +it.meta.pages || 1 });
  variants.push({ r, it, P, perr, ev });
}
if (!variants.length) { console.error('no evaluable coverage items (missing meta.json / truth?)', skipped); process.exit(2); }

// ---------------------------------------------------------------- aggregate per tag
const VAR_ORDER = ['clean', 'scan', 'scan-mild', 'scan-severe'];
const vrank = v => (VAR_ORDER.indexOf(v) + 1) || 99;
const variantNames = [...new Set(variants.map(v => v.r.variant))].sort((a, b) => vrank(a) - vrank(b) || a.localeCompare(b));
// global false-note rate per input (baseline for tags present in every measure)
const globalFalse = {};
for (const v of variants) { const g = globalFalse[v.r.variant] ||= { t: 0, f: 0 }; g.t += v.ev.allConf.tout; g.f += v.ev.allConf.fout; }
const items = [...new Map(variants.map(v => [`${v.it.family}/${v.it.id}`, v.it])).values()];
const allTags = new Set(Object.values(TAXONOMY).flat());
for (const it of items) { for (const t of it.meta.symbols || []) allTags.add(t); for (const t of Object.keys(it.meta.counts || {})) allTags.add(t); }
for (const v of variants) for (const t of Object.keys(v.ev.R)) if (v.ev.R[t].n) allTags.add(t);

const tagRows = {};
for (const tag of allTags) {
  const spec = tagSpec(tag);
  const row = { tag, family: familyOf(tag), kind: spec.kind, check: spec.what, semantic: !!spec.sem, element: spec.elem || null, occurrences: 0, occurrences_extracted: 0, items: [], by_variant: {}, notes: [] };
  for (const it of items) {
    const declared = (it.meta.counts || {})[tag];
    const inSymbols = (it.meta.symbols || []).includes(tag);
    const vFirst = variants.find(v => v.it === it);
    const ex = vFirst.ev.R[tag];
    const exN = tag === 'multi-page' ? (it.T.pageBreaks.size ? 1 : 0) : ex ? ex.n : 0;
    if (declared || inSymbols || exN) {
      row.items.push(`${it.family}/${it.id}`);
      row.occurrences += declared != null ? +declared : (tag === 'multi-page' ? 1 : exN);
      row.occurrences_extracted += exN;
    }
  }
  for (const vn of variantNames) {
    const vs = variants.filter(v => v.r.variant === vn && row.items.includes(`${v.it.family}/${v.it.id}`));
    if (!vs.length) continue;
    const agg = { variants: vs.length, n: 0, hit: 0, read: 0, readN: 0, emitted: 0, emitted_any_item: 0, crashes: vs.filter(v => v.r.crash).length };
    let prodLyr = 0, goodLyr = 0;
    const cf = { tin: 0, fin: 0, tout: 0, fout: 0 };
    for (const v of vs) {
      const x = v.ev.R[tag];
      if (x) {
        agg.n += x.n; agg.hit += x.hit; agg.read += x.read; agg.readN += x.readN;
        if (x.prec) { prodLyr += x.prec.produced; goodLyr += x.prec.matched; }
        if (x.conf) for (const k in cf) cf[k] += x.conf[k];
      }
      const e = v.ev.emitted[tag] || 0;
      agg.emitted += e; if (e) agg.emitted_any_item++;
    }
    if (spec.kind === 'lyrprec') { agg.n = prodLyr; agg.hit = goodLyr; agg.accuracy = prodLyr ? goodLyr / prodLyr : 1; agg.emitted = null; }
    else agg.accuracy = agg.n ? agg.hit / agg.n : null;
    agg.read = agg.readN ? +(agg.read / agg.readN).toFixed(4) : null;
    delete agg.readN;
    if (agg.accuracy != null) agg.accuracy = +agg.accuracy.toFixed(4);
    if (cf.tin) {
      const g = globalFalse[vn];
      const rin = cf.fin / cf.tin, rout = cf.tout ? cf.fout / cf.tout : (g && g.t ? g.f / g.t : 0);
      agg.false_notes_per_note_in = +rin.toFixed(4);
      agg.false_notes_per_note_out = +rout.toFixed(4);
      agg.false_baseline = cf.tout ? 'other measures' : 'all items';
      agg.false_counts = { truth_notes_in: cf.tin, false_in: cf.fin, truth_notes_out: cf.tout, false_out: cf.fout };
    }
    row.by_variant[vn] = agg;
  }
  // status from the typical scan (fallback: clean, then any)
  const sv = row.by_variant.scan ? 'scan' : row.by_variant.clean ? 'clean' : Object.keys(row.by_variant)[0];
  row.status_variant = sv || null;
  const S = sv ? row.by_variant[sv] : null;
  const emittedAnywhere = Object.values(row.by_variant).some(a => a.emitted);
  row.emitted_anywhere = spec.kind === 'lyrprec' ? null : emittedAnywhere;
  if (!row.items.length) row.status = 'no-items';
  else if (!S || S.accuracy == null) { row.status = 'not-measured'; row.notes.push(spec.kind === 'lyrprec' ? 'no lyric output to check' : 'declared in meta.json but not found in truth.musicxml by this tool'); }
  else {
    const a = S.accuracy;
    row.accuracy = a;
    row.status = a >= T_SUP ? 'supported' : a >= T_PART ? 'partial' : 'unsupported';
    if (!spec.sem && spec.kind !== 'lyrprec' && !emittedAnywhere) { row.status = 'unsupported'; row.notes.push('element never emitted'); }
    if (spec.sem && spec.elem && !emittedAnywhere) { if (row.status === 'supported') row.status = 'partial'; row.notes.push(`${spec.elem} never emitted`); }
    if (S.n < 3) row.notes.push(`low n (${S.n})`);
  }
  // confusion on clean (fallback: status variant)
  const cv = row.by_variant.clean || S;
  if (cv && cv.false_notes_per_note_in != null) {
    const excess = cv.false_notes_per_note_in - (cv.false_notes_per_note_out ?? 0);
    const fc = cv.false_counts, surplus = fc.false_in - (cv.false_notes_per_note_out ?? 0) * fc.truth_notes_in;
    // confused only with evidence: excess rate above the threshold AND at least CONF_MIN_SURPLUS extra false notes
    const verdict = excess > CONF_EXCESS && surplus >= CONF_MIN_SURPLUS ? 'confused' : fc.truth_notes_in < CONF_MIN_NOTES && excess > CONF_EXCESS ? 'unclear' : 'not confused';
    row.confusion = { variant: row.by_variant.clean ? 'clean' : sv, false_per_note_in: cv.false_notes_per_note_in, false_per_note_out: cv.false_notes_per_note_out, baseline: cv.false_baseline,
      excess: +excess.toFixed(4), surplus_false_notes: +surplus.toFixed(1), truth_notes_in: fc.truth_notes_in, verdict, not_confused: verdict === 'not confused' };
  }
  tagRows[tag] = row;
}

// ---------------------------------------------------------------- layouts
const normName = s => (s || '').toLowerCase().replace(/\bii\b/g, '2').replace(/\bi\b/g, '1').replace(/[^a-z0-9]/g, '');
const layoutRows = {};
const itemRows = [];
for (const v of variants) {
  const { r, it, P } = v;
  const expParts = (it.meta.expected && it.meta.expected.parts) || it.T.parts.map(p => p.name);
  const prodParts = P ? P.parts.map(p => p.name) : [];
  const countOk = prodParts.length === expParts.length ? 1 : 0;
  const pd = r.parts_detail || {};
  const mustNotSplit = !!(it.meta.expected && it.meta.expected.must_not_split);
  const row = {
    id: r.id, family: it.family, item: it.id, variant: r.variant, layout: it.meta.layout || 'unknown', title: it.meta.title || '',
    expected_parts: expParts, produced_parts: prodParts, part_count_ok: countOk, part_names: +(pd.names ?? 0).toFixed(4), right_part_share: +(pd.right_part_share ?? 0).toFixed(4),
    split_violation: mustNotSplit && prodParts.length > expParts.length ? 1 : 0,
    aggregate: +(r.aggregate || 0).toFixed(4), pitch: +(r.pitch || 0).toFixed(4), duration: +(r.duration || 0).toFixed(4), rests: +(r.rests || 0).toFixed(4), lyrics: +(r.lyrics || 0).toFixed(4), xml_valid: r.xml_valid,
    crash: r.crash, false_notes: v.ev.nFalse, truth_notes: v.ev.nTruth,
    ms_per_page: r.ms_per_page ?? null, peak_rss_mb: r.peak_rss_mb ?? null, pages: r.pagesN ?? null,
  };
  row.layout_score = +((countOk + row.part_names + row.right_part_share) / 3).toFixed(4);
  itemRows.push(row);
}
for (const lay of new Set([...LAYOUTS, ...itemRows.map(r => r.layout)])) {
  const rows = itemRows.filter(r => r.layout === lay);
  const L = { layout: lay, items: [...new Set(rows.map(r => `${r.family}/${r.item}`))], by_variant: {} };
  for (const vn of variantNames) {
    const rs = rows.filter(r => r.variant === vn);
    if (!rs.length) continue;
    const mean = k => +(rs.reduce((s, r) => s + (r[k] || 0), 0) / rs.length).toFixed(4);
    L.by_variant[vn] = { n: rs.length, part_count_ok: mean('part_count_ok'), part_names: mean('part_names'), right_part_share: mean('right_part_share'), split_violations: rs.reduce((s, r) => s + r.split_violation, 0), layout_score: mean('layout_score'), aggregate: mean('aggregate'), pitch: mean('pitch'), lyrics: mean('lyrics'), crashes: rs.reduce((s, r) => s + (r.crash ? 1 : 0), 0) };
  }
  const sv = L.by_variant.scan ? 'scan' : L.by_variant.clean ? 'clean' : Object.keys(L.by_variant)[0];
  L.status_variant = sv || null;
  if (!rows.length) L.status = 'no-items';
  else { const a = L.by_variant[sv].layout_score; L.accuracy = a; L.status = a >= T_SUP ? 'supported' : a >= T_PART ? 'partial' : 'unsupported'; }
  layoutRows[lay] = L;
}

// ---------------------------------------------------------------- performance
function paperName(pts) {
  if (!pts) return 'unknown';
  const [w, h] = pts, land = w > h, a = Math.min(w, h), b = Math.max(w, h);
  const std = [['A5', 420, 595], ['A4', 595, 842], ['Letter', 612, 792], ['Legal', 612, 1008], ['A3', 842, 1191], ['B4', 709, 1001], ['Tabloid', 792, 1224], ['Executive', 522, 756]];
  // scans carry borders and scale changes: name the nearest standard sheet ("~" when more than 3% off)
  let best = null;
  for (const [n, x, y] of std) { const e = Math.max(Math.abs(a / x - 1), Math.abs(b / y - 1)); if (e < 0.15 && (!best || e < best.e)) best = { n, e }; }
  return (best ? (best.e > 0.03 ? '~' : '') + best.n : `${(a / 72).toFixed(1)}x${(b / 72).toFixed(1)}in`) + (land ? ' landscape' : '');
}
function fit(xs, ys) {
  const n = xs.length; if (n < 2) return null;
  const mx = xs.reduce((s, x) => s + x, 0) / n, my = ys.reduce((s, y) => s + y, 0) / n;
  let sxx = 0, sxy = 0, syy = 0;
  for (let i = 0; i < n; i++) { sxx += (xs[i] - mx) ** 2; sxy += (xs[i] - mx) * (ys[i] - my); syy += (ys[i] - my) ** 2; }
  if (!sxx) return null;
  const b = sxy / sxx, a = my - b * mx;
  return { n, slope: +b.toFixed(2), intercept: +a.toFixed(1), r2: syy ? +((sxy * sxy) / (sxx * syy)).toFixed(3) : 1 };
}
const perfSrc = perfReport ? perfReport.items.filter(r => r.set === 'coverage') : covItems;
const perfFam = perfSrc.filter(r => r.family === 'perf');
const perfBase = (perfFam.length ? perfFam : perfSrc).filter(r => !r.crash && r.ms_per_page != null);
const perfRows = perfBase.map(r => {
  const pages = r.pagesN || 1;
  const eff = r.px && r.px[0] && r.page_pts ? Math.round(r.px[0][0] / (r.page_pts[0] / 72)) : null;
  return { id: r.id, variant: r.variant, src_dpi: r.src_ppi ?? null, raster_dpi: eff ?? r.raster_dpi ?? (perfReport || report).config.dpi, paper: paperName(r.page_pts), page_pts: r.page_pts || null, pages,
    mp_per_page: r.megapixels != null ? +(r.megapixels / pages).toFixed(3) : null, ms_per_page: r.ms_per_page, page_ms: r.page_ms || null, assemble_ms: r.assemble_ms ?? null,
    runtime_ms: r.runtime_ms, wall_ms: r.wall_ms, peak_rss_mb: r.peak_rss_mb ?? null };
});
function groupPerf(key) {
  const g = {};
  for (const r of perfRows) (g[r[key] ?? 'unknown'] ||= []).push(r);
  const med = a => { const b = a.filter(x => x != null).sort((x, y) => x - y); return b.length ? b[b.length >> 1] : null; };
  return Object.entries(g).sort((a, b) => (+a[0] || 0) - (+b[0] || 0) || String(a[0]).localeCompare(String(b[0]))).map(([k, rs]) => ({
    [key]: k, n: rs.length, mp_per_page: med(rs.map(r => r.mp_per_page)), ms_per_page_median: med(rs.map(r => r.ms_per_page)), ms_per_page_max: Math.max(...rs.map(r => r.ms_per_page)),
    peak_rss_mb_median: med(rs.map(r => r.peak_rss_mb)), peak_rss_mb_max: Math.max(0, ...rs.map(r => r.peak_rss_mb || 0)),
  }));
}
const fitRows = perfRows.filter(r => r.mp_per_page != null);
const perf = {
  source: perfReport ? path.relative(ROOT, PERF) : path.relative(ROOT, EVAL), scope: perfFam.length ? 'perf family' : 'all coverage items, no perf family yet',
  config: (perfReport || report).config ? { dpi: (perfReport || report).config.dpi, jobs: (perfReport || report).config.jobs, ocr: (perfReport || report).config.ocr, loadavg: (perfReport || report).config.loadavg || null, cpus: (perfReport || report).config.cpus || null } : null,
  n: perfRows.length,
  by_src_dpi: groupPerf('src_dpi'), by_raster_dpi: groupPerf('raster_dpi'), by_paper: groupPerf('paper'), by_pages: groupPerf('pages'),
  fit_ms_per_page_vs_mp: fit(fitRows.map(r => r.mp_per_page), fitRows.map(r => r.ms_per_page)),
  fit_peak_mb_vs_total_mp: fit(fitRows.filter(r => r.peak_rss_mb).map(r => r.mp_per_page * r.pages), fitRows.filter(r => r.peak_rss_mb).map(r => r.peak_rss_mb)),
  ms_per_megapixel_overall: (() => { const mp = fitRows.reduce((s, r) => s + r.mp_per_page * r.pages, 0); return mp ? Math.round(fitRows.reduce((s, r) => s + r.runtime_ms, 0) / mp) : null; })(),
  rows: perfRows,
};

// ---------------------------------------------------------------- outputs
const statusCount = st => Object.values(tagRows).filter(r => r.status === st).length;
const out = {
  generated: new Date().toISOString(),
  inputs: { eval: path.relative(ROOT, EVAL), eval_when: report.when, perf: PERF ? path.relative(ROOT, PERF) : null, coverage_dir: path.relative(ROOT, COV), src_hash: report.config.src_hash, ocr: report.config.ocr, dpi: report.config.dpi },
  thresholds: { supported: T_SUP, partial: T_PART, confusion_excess: CONF_EXCESS, confusion_min_surplus: CONF_MIN_SURPLUS, confusion_min_notes: CONF_MIN_NOTES },
  totals: { items: items.length, variants: variants.length, variant_names: variantNames, skipped, tags_supported: statusCount('supported'), tags_partial: statusCount('partial'), tags_unsupported: statusCount('unsupported'), tags_not_measured: statusCount('not-measured'), tags_without_items: statusCount('no-items') },
  tags: tagRows, layouts: layoutRows, items: itemRows, perf,
};
fs.mkdirSync(path.dirname(JSON_OUT), { recursive: true });
const atomic = (f, s) => { const tmp = `${f}.tmp-${process.pid}`; fs.writeFileSync(tmp, s); fs.renameSync(tmp, f); };
atomic(JSON_OUT, JSON.stringify(out, null, 1) + '\n');

// markdown
const pct = x => x == null ? '–' : (x * 100).toFixed(0) + '%';
const num = x => x == null ? '–' : String(x);
const vcols = variantNames;
const L = [];
L.push('# Coverage matrix: symbols, layouts, performance');
L.push('');
L.push(`Generated ${out.generated.slice(0, 16).replace('T', ' ')} UTC by \`tools/coverage.mjs\` from \`${out.inputs.eval}\` (eval ${String(report.when).slice(0, 16).replace('T', ' ')}, app source hash \`${report.config.src_hash}\`, OCR ${report.config.ocr ? 'on' : 'off'}, raster ${report.config.dpi}${typeof report.config.dpi === 'number' ? ' dpi' : ''}).`);
L.push(`Corpus: \`${out.inputs.coverage_dir}\` — ${items.length} items, ${variants.length} scored PDFs (${vcols.join(', ')})${skipped.length ? `, ${skipped.length} skipped` : ''}. Every item is a short LilyPond engraving with exact MusicXML truth and a \`meta.json\` listing its symbols, layout and per-symbol counts.`);
L.push('');
L.push('Regenerate:');
L.push('');
L.push('```');
L.push('node mvp/tools/eval.mjs --set coverage --out mvp/work/eval-coverage.json');
L.push('node mvp/tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 --out mvp/work/eval-coverage-perf.json   # optional, for timing');
L.push('node tools/coverage.mjs --eval mvp/work/eval-coverage.json [--perf mvp/work/eval-coverage-perf.json]');
L.push('```');
L.push('');
L.push('## How to read the tables');
L.push('');
L.push(`- **Occurrences**: how often the symbol occurs in the truth files, summed over items (\`meta.json\` counts; this tool's own count from \`truth.musicxml\` where meta has none). **Items**: items containing it.`);
L.push(`- **Accuracy** per input (${vcols.join(' / ')}): recall over the truth instances. Note-level tags: truth notes with the tag that are aligned to an app note with the right pitch *and* the tag's feature (an element such as \`<dot/>\`, \`<beam>\`, \`<slur>\`, \`<staccato/>\`, or, for semantic tags marked *sem*, its meaning: duration for note values, spelled pitch for accidentals, sounding pitch under an ottava). Clef, key and time tags: exact match of the same clef/key/time change at the aligned measure (±1). Directions and structure: the same element and value at the aligned measure (±1). Notes and rests are aligned with all parts merged, so part splitting does not affect these numbers (it is scored under layouts).`);
L.push('- **Emitted**: how many times the app\'s MusicXML contains the corresponding element, on the typical scan (0 = never written). Emitted and the accuracy denominators (hit/n) count notes for note-level tags, so a chord, beam group, tuplet, arpeggio or ottava line counts once per note it covers, while **Occurrences** follow the generators\' count rules in `meta.json` (`count_rules`: chords, beam groups, tuplet brackets and ottava lines once each).');
L.push('- **Read**: share of truth notes carrying the tag that the app read with the right pitch, whether or not it kept the mark.');
L.push(`- **Status** (from the \`scan\` input, the typical 200–300 dpi scan): supported ≥ ${T_SUP}, partial ${T_PART}–${T_SUP}, unsupported < ${T_PART} or the element is never emitted. Semantic tags whose MusicXML element exists but is never written (e.g. \`<octave-shift>\`, \`<multiple-rest>\`) are capped at partial.`);
L.push(`- **Confusion** (on \`clean.pdf\`): false notes (app notes that match no truth note) per truth note in the measures holding the symbol, minus the same rate in the other measures (all items' rate when the symbol is in every measure). *confused* = excess > ${CONF_EXCESS} and at least ${CONF_MIN_SURPLUS} surplus false notes; *unclear* = excess > ${CONF_EXCESS} on fewer than ${CONF_MIN_NOTES} truth notes; otherwise *not confused*: the app may drop the mark, but it does not turn it into extra notes. It matters most for marks the app does not output.`);
L.push('');
L.push(`**Totals:** ${out.totals.tags_supported} supported, ${out.totals.tags_partial} partial, ${out.totals.tags_unsupported} unsupported, ${out.totals.tags_not_measured} not measurable, ${out.totals.tags_without_items} taxonomy tags without items yet.`);
L.push('');
const famOrder = [...Object.keys(TAXONOMY), 'other'];
const esc = s => String(s).replace(/\|/g, '\\|');
for (const fam of famOrder) {
  const rows = Object.values(tagRows).filter(r => r.family === fam && !(r.tag.startsWith('x-') && r.status === 'not-measured')).sort((a, b) => {
    const ia = (TAXONOMY[fam] || []).indexOf(a.tag), ib = (TAXONOMY[fam] || []).indexOf(b.tag);
    return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib) || a.tag.localeCompare(b.tag);
  });
  if (!rows.length) continue;
  L.push(`## Symbols: ${fam}`);
  L.push('');
  L.push(`| Tag | Occurrences | Items | Emitted | ${vcols.map(v => `Accuracy ${v}`).join(' | ')} | Read | Status | Confusion | Check |`);
  L.push(`|---|---:|---:|---:|${vcols.map(() => '---:').join('|')}|---:|---|---|---|`);
  for (const r of rows) {
    if (!r.items.length) { L.push(`| \`${r.tag}\` | 0 | 0 | – | ${vcols.map(() => '–').join(' | ')} | – | no items yet | – | ${esc(r.check)}${r.semantic ? ' (sem)' : ''} |`); continue; }
    const S = r.by_variant[r.status_variant] || {};
    const conf = r.confusion ? `${r.confusion.verdict === 'confused' ? '**confused**' : r.confusion.verdict} (${r.confusion.excess >= 0 ? '+' : ''}${r.confusion.excess.toFixed(2)})` : '–';
    const st = r.status === 'supported' ? 'supported' : r.status === 'partial' ? 'partial' : r.status === 'unsupported' ? '**unsupported**' : r.status;
    L.push(`| \`${r.tag}\` | ${r.occurrences} | ${r.items.length} | ${S.emitted == null ? '–' : S.emitted} | ${vcols.map(v => r.by_variant[v] ? `${pct(r.by_variant[v].accuracy)}${r.by_variant[v].n != null ? ` (${r.by_variant[v].hit}/${r.by_variant[v].n})` : ''}` : '–').join(' | ')} | ${pct(S.read)} | ${st}${r.notes.length ? ` — ${esc(r.notes.join('; '))}` : ''} | ${conf} | ${esc(r.check)}${r.semantic ? ' (sem)' : ''} |`);
  }
  L.push('');
}
const extra = Object.values(tagRows).filter(r => r.tag.startsWith('x-') && r.status === 'not-measured').sort((a, b) => a.tag.localeCompare(b.tag));
if (extra.length) {
  L.push('## Generator-specific extra tags (not measured)');
  L.push('');
  L.push('Tags outside the taxonomy that the generators record in `meta.json` (detail counts with no MusicXML element of their own, e.g. rest positions or minor-key flags). They are listed for completeness; the symbols they refine are scored above.');
  L.push('');
  L.push('| Tag | Occurrences | Items |');
  L.push('|---|---:|---|');
  for (const r of extra) L.push(`| \`${r.tag}\` | ${r.occurrences} | ${r.items.map(i => `\`${i}\``).join(', ')} |`);
  L.push('');
}
L.push('## Layouts');
L.push('');
L.push(`Layout score = mean of part-count match (exact), part-name score and the share of recognised notes that landed in the right part (from eval.mjs). Status from the \`scan\` input with the same thresholds.`);
L.push('');
L.push(`| Layout | Items | ${vcols.map(v => `Layout score ${v}`).join(' | ')} | Part count ok | Names | Right part | Split violations | Aggregate | Status |`);
L.push(`|---|---:|${vcols.map(() => '---:').join('|')}|---:|---:|---:|---:|---:|---|`);
for (const l of Object.values(layoutRows).sort((a, b) => { const ia = LAYOUTS.indexOf(a.layout), ib = LAYOUTS.indexOf(b.layout); return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib); })) {
  if (!l.items.length) { L.push(`| \`${l.layout}\` | 0 | ${vcols.map(() => '–').join(' | ')} | – | – | – | – | – | no items yet |`); continue; }
  const S = l.by_variant[l.status_variant];
  L.push(`| \`${l.layout}\` | ${l.items.length} | ${vcols.map(v => l.by_variant[v] ? pct(l.by_variant[v].layout_score) : '–').join(' | ')} | ${pct(S.part_count_ok)} | ${pct(S.part_names)} | ${pct(S.right_part_share)} | ${S.split_violations} | ${S.aggregate.toFixed(3)} | ${l.status === 'unsupported' ? '**unsupported**' : l.status} |`);
}
L.push('');
L.push('## Performance');
L.push('');
const pc = perf.config || {};
L.push(`Source: \`${perf.source}\` (${perf.scope}; ${perf.n} PDFs; raster ${pc.dpi}${typeof pc.dpi === 'number' ? ' dpi' : ''}, OCR ${pc.ocr ? 'on' : 'off'}, ${pc.jobs} parallel jobs${pc.cpus ? ` on ${pc.cpus} CPUs` : ''}${pc.loadavg ? `, load average ${pc.loadavg[0]} at the start` : ''}). Times are the converter in a Node child process, per page, run as the browser worker runs it (\`createConverter()\`: each page read from disk when its turn comes, \`addPage\`, then \`releasePage\` frees its image buffers and keeps the staff-removed binary bit-packed, then \`finish\`); peak memory is the child's peak RSS (\`maxRSS\`), including Node itself (~50 MB) and the OCR engine when OCR is on. ${typeof pc.dpi === 'number' ? 'With a fixed raster dpi the source scan dpi changes image quality, not pixel count; use `--dpi native` (raster at the scan resolution) or `--dpi app` (browser app: 2300 px wide) to measure the dpi effect.' : pc.dpi === 'native' ? 'Pages are rasterised at the resolution of the scan image, so pixel count follows the source dpi.' : 'Pages are rasterised like the browser app (2300 px wide).'}`);
L.push('');
const perfTable = (title, rows, key, label) => {
  if (!rows.length) return;
  L.push(`**${title}**`);
  L.push('');
  L.push(`| ${label} | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |`);
  L.push('|---|---:|---:|---:|---:|---:|---:|');
  for (const g of rows) L.push(`| ${g[key]} | ${g.n} | ${g.mp_per_page ?? '–'} | ${g.ms_per_page_median ?? '–'} | ${g.ms_per_page_max ?? '–'} | ${g.peak_rss_mb_median ?? '–'} | ${g.peak_rss_mb_max || '–'} |`);
  L.push('');
};
perfTable('By source scan dpi', perf.by_src_dpi, 'src_dpi', 'Scan dpi');
if (pc.dpi === 'app') perfTable('By raster dpi (app-sized pages, 2300 px wide)', perf.by_raster_dpi, 'raster_dpi', 'Raster dpi');
perfTable('By page size', perf.by_paper, 'paper', 'Page size');
perfTable('By page count', perf.by_pages, 'pages', 'Pages');
const f1 = perf.fit_ms_per_page_vs_mp, f2 = perf.fit_peak_mb_vs_total_mp;
L.push(`**Linear fits.** ${f1 ? `ms per page = ${f1.intercept} + **${f1.slope} ms per megapixel** × MP per page (n=${f1.n}, R²=${f1.r2}).` : 'ms per page vs megapixels: not enough data.'} ${f2 ? `Peak MB = ${f2.intercept} + ${f2.slope} MB per megapixel × total MP (n=${f2.n}, R²=${f2.r2}).` : ''} Overall: ${perf.ms_per_megapixel_overall ?? '–'} ms of conversion per megapixel.`);
L.push('');
L.push('## Items');
L.push('');
L.push(`| Item | Layout | ${vcols.map(v => `Aggregate ${v}`).join(' | ')} | Parts (expected → ${vcols.includes('scan') ? 'scan' : vcols[0]}) | ms/page | peak MB |`);
L.push(`|---|---|${vcols.map(() => '---:').join('|')}|---|---:|---:|`);
for (const it of items) {
  const rs = itemRows.filter(r => r.family === it.family && r.item === it.id);
  const s = rs.find(r => r.variant === 'scan') || rs[0];
  L.push(`| \`${it.family}/${it.id}\` | ${s.layout} | ${vcols.map(v => { const r = rs.find(x => x.variant === v); return r ? (r.crash ? 'crash' : r.aggregate.toFixed(3)) : '–'; }).join(' | ')} | ${s.expected_parts.length} → ${s.produced_parts.length} | ${s.ms_per_page ?? '–'} | ${s.peak_rss_mb != null ? Math.round(s.peak_rss_mb) : '–'} |`);
}
if (skipped.length) { L.push(''); L.push('Skipped: ' + skipped.map(s => `\`${s.id}\` (${esc(s.why)})`).join(', ')); }
L.push('');
fs.mkdirSync(path.dirname(MD), { recursive: true });
atomic(MD, L.join('\n'));

// console summary
const pad = (s, n) => String(s).padEnd(n).slice(0, n);
console.log(`coverage: ${items.length} items, ${variants.length} PDFs; tags supported=${out.totals.tags_supported} partial=${out.totals.tags_partial} unsupported=${out.totals.tags_unsupported} not-measured=${out.totals.tags_not_measured} no-items=${out.totals.tags_without_items}`);
for (const r of Object.values(tagRows).filter(r => r.items.length).sort((a, b) => famOrder.indexOf(a.family) - famOrder.indexOf(b.family) || a.tag.localeCompare(b.tag))) {
  const S = r.by_variant[r.status_variant] || {};
  console.log(`  ${pad(r.family, 9)} ${pad(r.tag, 20)} occ=${pad(r.occurrences, 5)} ${vcols.map(v => `${v}=${r.by_variant[v] ? pct(r.by_variant[v].accuracy) : '–'}`).join(' ').padEnd(40)} emitted=${pad(S.emitted ?? '–', 5)} ${pad(r.status, 12)} ${r.confusion ? r.confusion.verdict.toUpperCase() === 'CONFUSED' ? 'CONFUSED' : r.confusion.verdict : ''}`);
}
console.log(`-> ${path.relative(ROOT, MD)}, ${path.relative(ROOT, JSON_OUT)}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();

export { extract, evaluateVariant, tagSpec, TAXONOMY, LAYOUTS };
