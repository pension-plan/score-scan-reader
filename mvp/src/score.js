'use strict';
// Page assemblies -> parts (closed-score split / grand staff / single), time
// signature inference, per-measure rhythm repair, lyrics alignment, MusicXML.
const { staffMeasureEvents, pitchOf, keyAlters, DIV } = require('./assemble');
const { detectRests, mergeRests, restBars } = require('./rests');
const { readMeters, plausibleMeter } = require('./meter');
const { readStructure } = require('./structure');
const { readArticulations, readDoubleDots } = require('./artic');
const { readOttavas } = require('./ottava');
const { pageMarks } = require('./symbols');
const { instrumentXML, soundDynamics, tempoFromWords } = require('./playback');

const COLORS = ['#d1495b', '#edae49', '#00798c', '#30638e', '#7b5ea7', '#3a7d44'];

// most common value; ties go to the larger value
function mode(a) {
  const c = new Map();
  for (const v of a) c.set(v, (c.get(v) || 0) + 1);
  let best = null, bn = -1;
  for (const [v, n] of c) if (n > bn || (n === bn && v > best)) { best = v; bn = n; }
  return best;
}

// ------------------------------------------------------------ layout evidence
function staffStats(systems, idx) {
  let n = 0, n2 = 0, n3 = 0, mix = 0;
  for (const sy of systems) {
    const s = sy.staves[idx]; if (!s) continue;
    for (const c of s.chords) {
      n++;
      const dirs = new Set(c.heads.map(h => h.stemDir));
      if (c.heads.length >= 3) n3++;
      else if (c.heads.length === 2 || dirs.has(2)) n2++;
      if (dirs.has(1) && dirs.has(-1)) { n2 += 0.5; mix++; }
    }
  }
  return { n, f2: n ? n2 / n : 0, f3: n ? n3 / n : 0, mix: n ? mix / n : 0 };
}

// Share of the barlines of staff k that run on into staff k+1. Engraving
// convention: barlines are drawn through a keyboard grand staff (one player)
// but stop at each staff of a choir or a voice (so they never cross the text).
function pairConnectivity(systems, k) {
  let n = 0, c = 0;
  for (const sy of systems) {
    const a = sy.staves[k], b = sy.staves[k + 1];
    if (!a || !b || !sy.fr || !sy.fr.barlines) continue;
    const ss = sy.fr.ss || a.st.space;
    for (const bl of sy.fr.barlines) {
      if (bl.staff !== a.st.index) continue;
      n++;
      if (bl.bot >= b.st.yAt(0, bl.x) - 0.5 * ss) c++;
    }
  }
  return { n, frac: n ? c / n : null };
}

// fraction of systems whose OCR found an underlay line (>= 3 syllables) below staff k
function lyricPresence(systems, lyricsBySystem, nSt) {
  const pres = new Array(nSt).fill(0);
  let ns = 0;
  for (const sy of systems) {
    ns++;
    const lyr = lyricsBySystem[sy.page + ':' + sy.index] || [];
    const bands = new Set(lyr.filter(v => v.syllables && v.syllables.length >= 3).map(v => v.band));
    for (const b of bands) if (b >= 0 && b < nSt) pres[b]++;
  }
  return pres.map(x => (ns ? x / ns : 0));
}

function staffClef(systems, k) {
  const read = systems.map(sy => sy.staves[k]).filter(s => s && !s.hdr.clefGuessed).map(s => s.hdr.clef);
  if (read.length) return mode(read);
  const any = systems.map(sy => sy.staves[k]).filter(Boolean).map(s => s.hdr.clef);
  return any.length ? mode(any) : 'G';
}

// Names for the vocal parts, from the staff / voice pattern and the clefs
// (research-voices.md §6 fallback when no labels are read).
function vocalNames(vs) {
  // vs: [{ staff, split, clef }] top to bottom
  const nV = vs.reduce((a, v) => a + (v.split ? 2 : 1), 0);
  const isLow = c => c === 'F';
  const sig = vs.map(v => (v.split ? '2' : '1') + (v.clef === 'G8' ? 't' : isLow(v.clef) ? 'b' : 'g')).join('');
  const table = {
    '2g2b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '2t2b': ['Tenor I', 'Tenor II', 'Baritone', 'Bass'],
    '2g2g': ['Soprano I', 'Soprano II', 'Alto I', 'Alto II'],
    '2t2t': ['Tenor I', 'Tenor II', 'Bass I', 'Bass II'],
    '2b2b': ['Tenor I', 'Tenor II', 'Bass I', 'Bass II'],
    '2g1b': ['Soprano', 'Alto', 'Baritone'],
    '1g1g1g1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1g1t1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1g1b1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1t1b': ['Soprano', 'Tenor', 'Bass'],
    '2g': ['Soprano', 'Alto'],
    '2t': ['Tenor', 'Bass'],
    '2b': ['Tenor', 'Bass'],
  };
  if (table[sig]) return table[sig];
  // a solo line (or several) above a four-part choir in open score
  if (vs.length > 4 && vs.every(v => !v.split)) {
    const tail = vs.slice(-4).map(v => (v.clef === 'G8' ? 't' : isLow(v.clef) ? 'b' : 'g')).join('');
    if (/^gg[gtb]b$/.test(tail)) {
      const head = vs.slice(0, -4).map((_, i, a) => (a.length === 1 ? 'Voice' : `Voice ${i + 1}`));
      return head.concat(['Soprano', 'Alto', 'Tenor', 'Bass']);
    }
  }
  if (nV === 1) return ['Voice'];
  const out = [];
  let i = 0;
  for (const v of vs) {
    i++;
    const base = vs.length === 1 ? 'Voice' : `Voice ${i}`;
    if (v.split) out.push(`${base} upper`, `${base} lower`); else out.push(base);
  }
  return out;
}

// ------------------------------------------------------------ part labels
// Names printed left of the first system (lyrics.js readPartLabels ->
// fr.partLabels: [{staves, text, conf, y}]). research-voices.md section 6:
// normalise, look the words up in a small multilingual lexicon, keep the
// printed spelling for full names ("Sopran", "Tenor II", "Canto") and expand
// abbreviations ("S." -> Soprano). Collective names give two voices.
const LEX = [
  [/^(s|sop|sopr|soprano|soprani|sopranos|sopran|soprane|treble|trebles|cantus|superius|discantus|descant)$/, 'Soprano', 'vocal'],
  [/^(a|alt|alto|alti|altos|contralto|altus)$/, 'Alto', 'vocal'],
  [/^(t|ten|tenor|tenore|tenori|tenors|ténor|ténors)$/, 'Tenor', 'vocal'],
  [/^(bar|bari|baritone|baritono|bariton|baryton)$/, 'Baritone', 'vocal'],
  [/^(b|bs|bass|basso|bassi|basse|basses|bassus)$/, 'Bass', 'vocal'],
  [/^(mezzo|mezzosoprano)$/, 'Mezzo-soprano', 'vocal'],
  [/^(voice|voce|voix|singstimme|gesang|stimme|canto|chant|melody|melodie|mélodie|cantor)$/, 'Voice', 'vocal'],
  [/^(piano|pianoforte|pf|pfte|pno|klavier|clavier|accompaniment|acc|accomp|keyboard|organ|orgel|organo|orgue|harmonium|manual|manuals)$/, 'Piano', 'keyboard'],
  [/^(violin|violino|violine|violon|viola|violoncello|cello|vc|vln|vla|flute|flauto|flöte|oboe|clarinet|clarinetto|bassoon|fagotto|horn|corno|trumpet|tromba|trombone|tuba|harp|guitar|contrabass|kontrabass)$/, null, 'instrument'],
];
const COLLECTIVE = [[/^(women|ladies|frauen|femmes|donne|sa)$/, ['Soprano', 'Alto']], [/^(men|männer|maenner|hommes|uomini|tb)$/, ['Tenor', 'Bass']]];
const MOD = /^(i{1,3}|iv|[1-4]|[1-4](st|nd|rd|th)|primo|secondo|solo|div|divisi|1mo|2do)$/;

function parseLabel(text) {
  const out = [];
  const clean = String(text || '').normalize('NFC').replace(/[^\p{L}\p{N}.&/,+\s'’-]/gu, ' ');
  // a part label is a name or two, not prose (text of a facing page, a
  // preface): most of its words must be names, numerals or joiners
  const all = clean.split(/[\s&/,+]+/).map(w => w.toLowerCase().replace(/[.'’]/g, '')).filter(Boolean);
  const known = all.filter(w => LEX.some(([re]) => re.test(w)) || COLLECTIVE.some(([re]) => re.test(w)) || MOD.test(w) || /^(and|und|et)$/.test(w)).length;
  if (all.length > 4 || (all.length > 1 && known < 0.6 * all.length)) return out;
  for (const chunk of clean.split(/\s*(?:[&/,+]|\band\b|\bund\b|\bet\b)\s*/i)) {
    const words = chunk.split(/\s+/).filter(Boolean);
    let cur = null;
    for (const w0 of words) {
      const w = w0.toLowerCase().replace(/[.'’]/g, '');
      if (!w) continue;
      const col = COLLECTIVE.find(([re]) => re.test(w));
      if (col) { col[1].forEach(n => out.push({ name: n, kind: 'vocal', abbrev: false })); cur = null; continue; }
      const hit = LEX.find(([re]) => re.test(w));
      if (hit && !(cur && MOD.test(w) && w === 'solo')) {
        const abbrev = w.length <= 3 && hit[1] !== null && w !== 'alt' && w !== 'pf';
        const shown = abbrev ? hit[1] : w0.replace(/[.,]+$/, '');
        cur = { name: shown.charAt(0).toUpperCase() + shown.slice(1), kind: hit[2], abbrev, canon: hit[1], letter: w.length === 1 };
        out.push(cur);
        continue;
      }
      if (MOD.test(w)) {
        if (cur) cur.name += ' ' + w0.replace(/[.,]+$/, '').replace(/^i{1,3}$/i, m => m.toUpperCase());
        else out.push(cur = { name: w0, kind: 'modifier', pending: true });
        continue;
      }
      // a lone unknown word: keep as a name only when the whole label is that word
      if (words.length === 1 && w.length >= 3) out.push(cur = { name: w0.charAt(0).toUpperCase() + w0.slice(1), kind: 'unknown', abbrev: false });
    }
  }
  // "Solo Voice": a modifier printed before its name
  for (let i = 0; i + 1 < out.length; i++) if (out[i].pending && out[i + 1].kind !== 'modifier') { out[i + 1].name = out[i].name + ' ' + out[i + 1].name; out.splice(i, 1); }
  for (const n of out) if (n.pending && /^solo$/i.test(n.name)) { n.name = 'Solo'; n.kind = 'vocal'; n.canon = 'Voice'; }
  return out.filter(n => n.kind !== 'modifier' && n.kind !== 'unknown');
}

// Labels of the first system that has the piece's staff count, per staff
// (system-relative): [{names, off (label centre - staff centre, in spaces), span}]
function readLabels(systems, nSt) {
  const per = Array.from({ length: nSt }, () => []);
  const seen = new Set();
  for (const sy of systems) {
    const fr = sy.fr;
    if (!fr || !fr.partLabels || !fr.partLabels.length || seen.has(fr) || sy.index !== 0) continue;
    seen.add(fr);
    if (sy.staves.length !== nSt) continue;
    const ids = sy.staves.map(s => s.si);
    for (const l of fr.partLabels) {
      const rel = (l.staves || [l.staff]).map(s => ids.indexOf(s)).filter(k => k >= 0);
      if (!rel.length || (l.conf != null && l.conf < 45)) continue;
      const names = parseLabel(l.text);
      if (!names.length) continue;
      const st = sy.staves[rel[0]].st, sp = st.space;
      const off = rel.length === 1 && l.y != null ? (l.y - st.yAt(2, st.left)) / sp : 0;
      per[rel[0]].push({ names, off, span: rel.length > 1 ? rel : null, y: l.y || 0 });
    }
    break;
  }
  per.forEach(a => a.sort((x, y) => x.y - y.y));
  return per;
}

// Braces and system lines (text.js marks) joining staves k and k+1 of the
// systems: {braces, lines} counted over systems
function braceEvidence(sel, k) {
  let braces = 0, lines = 0;
  for (const sy of sel) {
    const m = sy.fr && sy.fr._marks && sy.fr._marks.marks;
    if (!m || !sy.staves[k + 1]) continue;
    const a = sy.staves[k].si, b = sy.staves[k + 1].si;
    const on = m.braces.filter(x => x.span && x.span.includes(a) && x.span.includes(b));
    if (on.some(x => x.kind === 'brace')) braces++;
    else if (on.length) lines++;
  }
  return { braces, lines };
}

// Decide the part layout for the whole piece (never per measure):
//  - adjacent staves joined by barlines with no underlay between them are a
//    keyboard grand staff: one part, never split (voices kept inside it);
//  - every other staff is a vocal / melody staff; one that carries two voices
//    (stems up and down, at most two heads per stem) is split by stem direction
//    into two parts (closed score SATB, SSAA, TTBB, divisi).
function chooseLayout(systems, lyricsBySystem = {}, opts = {}) {
  const nSt = mode(systems.map(s => s.staves.length)) || 1;
  const sel = systems.filter(s => s.staves.length === nSt);
  const stats = [], clefs = [];
  for (let i = 0; i < nSt; i++) { stats.push(staffStats(sel, i)); clefs.push(staffClef(sel, i)); }
  const lyr = lyricPresence(sel, lyricsBySystem, nSt);
  const anyLyrics = lyr.some(x => x > 0);
  const ocr = opts.ocr !== false;
  const notes = [];
  // printed part names (first system with the full staff count), per staff
  const labels = readLabels(systems, nSt);
  const ownNames = (k, kinds) => labels[k].filter(l => !l.span).flatMap(l => l.names.filter(n => kinds.includes(n.kind)));
  // staff size against the largest staff of its system (median over the
  // systems): small staves printed over a full-size score are the solo or
  // cue staves of a piano score (an instrument each), never one half of a
  // grand staff, whose two staves have one size (L18)
  const small = Array.from({ length: nSt }, (_, k) => {
    const r = sel.map(sy => (sy.staves[k] ? sy.staves[k].st.space / Math.max(...sy.staves.map(s => s.st.space)) : 1)).sort((a, b) => a - b);
    return r.length > 0 && r[r.length >> 1] <= 0.85;
  });
  // keyboard links between adjacent staves (evid: the evidence per pair, for debugging)
  const link = [], evid = [];
  for (let k = 0; k + 1 < nSt; k++) {
    const c = pairConnectivity(sel, k);
    const underlay = lyr[k] >= 0.3;
    let kb;
    // accompaniment cue (research-voices.md section 5): the bottom pair of
    // staves carries chords but no text while a staff above it carries the
    // underlay -> voice(s) over a piano whose barlines were not seen joined
    const chordy = Math.max(stats[k].f2 + stats[k].f3, stats[k + 1].f2 + stats[k + 1].f3) >= 0.2;
    const accomp = ocr && k + 1 === nSt - 1 && lyr.slice(0, k).some(x => x >= 0.3) && lyr[k] < 0.15 && lyr[k + 1] < 0.15 && chordy;
    if (c.n >= 2) kb = (c.frac >= 0.5 && !underlay) || accomp;
    else {
      // no barline evidence: two chordal staves with no text at all read as piano
      const chordal = (stats[k].f3 + stats[k + 1].f3) / 2 >= 0.2 || (stats[k].f2 + stats[k + 1].f2) / 2 <= 0.3;
      kb = nSt === 2 && !underlay && (chordal || (ocr && !anyLyrics));
    }
    if (small[k] || small[k + 1]) kb = false;
    // a lone one-letter voice name ("a": OCR of a brace, a clef fragment or a
    // misread instrument name) on a pair already read as keyboard, with chords
    // on one of its staves and no text under any staff, is noise, not a
    // singer: it does not split the grand staff (L6). Two single-line staves
    // may be two instruments (L18), so there the name still counts.
    const own = ownNames(k, ['vocal', 'instrument']).concat(ownNames(k + 1, ['vocal', 'instrument']));
    const texture = Math.max(stats[k].f2 + stats[k].f3, stats[k + 1].f2 + stats[k + 1].f3) >= 0.1;
    const noise = kb && texture && !anyLyrics && own.length === 1 && own[0].letter;
    // printed names overrule: one keyboard name across the pair joins it; a
    // staff with its own voice or instrument name is not half of a grand staff
    if (labels[k].some(l => l.span && l.span.includes(k + 1) && l.names.some(n => n.kind === 'keyboard'))) kb = true;
    else if (own.length && !noise) kb = false;
    // a grand staff is braced: where the systems' left edges were read (a
    // system line joins the pair) and no system shows a brace over the pair,
    // the two staves are two instruments (L18). Off unless opts.braceCheck: on
    // the challenge set it fixed the two-instrument items but split pianos
    // whose brace was not found (degraded copies)
    if (kb && opts.braceCheck) {
      const ev = braceEvidence(sel, k);
      if (ev.lines >= 2 && !ev.braces) { kb = false; notes.push(`Staves ${k + 1}+${k + 2}: joined by a system line but no brace on any system: read as two parts, not a keyboard grand staff.`); }
    }
    evid.push({ pair: k, bars: c.n, joined: c.frac == null ? null : +c.frac.toFixed(2), lyr: [+lyr[k].toFixed(2), +lyr[k + 1].toFixed(2)], accomp, small: [small[k], small[k + 1]], brace: braceEvidence(sel, k), kb });
    link.push(kb);
  }
  // organ: a pedal staff (bass clef, no text, no name of its own) under a
  // keyboard pair belongs to it; its barlines are often not drawn through
  if (nSt === 3 && link[0] && !link[1] && clefs[2] === 'F' && lyr[2] < 0.15 && !ownNames(2, ['vocal', 'instrument']).length) {
    link[1] = true;
    notes.push('Staff 3: read as the pedal staff of the keyboard above it (no text, bass clef), kept in the same part.');
  }
  // groups: runs of linked staves (max 3: organ) are one keyboard part
  const groups = [];
  for (let i = 0; i < nSt;) {
    let j = i;
    while (j + 1 < nSt && link[j] && j - i < 2) j++;
    groups.push({ staves: Array.from({ length: j - i + 1 }, (_, t) => i + t), keyboard: j > i });
    i = j + 1;
  }
  // vocal staves: split when two voices share the staff for the whole piece
  const vocal = groups.filter(g => !g.keyboard).map(g => g.staves[0]);
  // a piece on one staff splits only where stems up and down are seen
  // together (research-voices.md section 11): two heads on one stem there
  // are chords, double stops or blurred heads, not two singers
  const vs = vocal.map(k => ({ staff: k, clef: clefs[k], small: small[k], split: !small[k] && stats[k].f2 > 0.35 && stats[k].f3 < 0.2 && (nSt > 1 || stats[k].mix >= 0.25) }));
  // a two-staff closed score decides once for both staves
  if (vs.length === 2 && nSt === 2 && !small[0] && !small[1]) {
    const both = (stats[0].f2 + stats[1].f2) / 2 > 0.3 && (stats[0].f3 + stats[1].f3) / 2 < 0.2;
    vs.forEach(v => { v.split = both; });
  }
  // printed names decide the voice count of a staff: two names (stacked
  // "Soprano / Alto", "S. A.", "Women") split it, one name centred on the
  // staff keeps it whole (SAB: "Baritone" alone under "Soprano / Alto"); a
  // single name off-centre had its partner missed and names one voice only
  for (const v of vs) {
    const ls = labels[v.staff].filter(l => !l.span && l.names.some(n => n.kind === 'vocal' || n.kind === 'instrument'));
    const names = ls.flatMap(l => l.names.filter(n => n.kind === 'vocal' || n.kind === 'instrument'));
    if (names.length >= 2 && (stats[v.staff].f2 > 0.1 || stats[v.staff].mix > 0)) { v.split = true; v.names = [names[0], names[1]]; }
    else if (names.length === 1 && Math.abs(ls[0].off) < 0.8) { v.split = false; v.names = [names[0]]; }
    else if (names.length === 1) { v.names = ls[0].off < 0 ? [names[0], null] : [null, names[0]]; }
    else if (names.length >= 2) v.names = [names[0]];
  }
  // inferred names: voices from the vocal staves' pattern, small staves
  // (instruments, their names not read) numbered
  {
    const vv = vs.filter(v => !v.small), vn = vocalNames(vv), sm = vs.filter(v => v.small);
    let q = 0;
    vv.forEach(v => { const n = v.split ? 2 : 1; v.inf = vn.slice(q, q + n); q += n; });
    sm.forEach((v, i) => { v.inf = [sm.length > 1 ? `Instrument ${i + 1}` : 'Instrument']; });
  }
  const read = [];
  const parts = [];
  let vi = 0;
  const nKb = groups.filter(g => g.keyboard).length;
  let kbi = 0;
  for (const g of groups) {
    if (g.keyboard) {
      kbi++;
      const kbName = g.staves.flatMap(k => labels[k]).flatMap(l => l.names).find(n => n.kind === 'keyboard');
      // three linked staves are manuals and pedal: an organ
      const kbDefault = g.staves.length === 3 ? 'Organ' : 'Piano';
      parts.push({ name: kbName ? kbName.name : nKb > 1 ? `${kbDefault} ${kbi}` : kbDefault, nameRead: !!kbName, kind: 'keyboard', src: g.staves.map(s => ({ staff: s, voice: 'chordal' })),
        layout: `Staves ${g.staves[0] + 1}\u2013${g.staves[g.staves.length - 1] + 1}: keyboard grand staff, one part` });
      notes.push(`Staves ${g.staves.map(s => s + 1).join('+')}: read as a keyboard grand staff (barlines joined or chords without lyrics under a sung line), kept together as one part and never split.`);
      continue;
    }
    const v = vs.find(x => x.staff === g.staves[0]);
    const nm = (k) => { const n = v.names && v.names[k]; const inf = v.inf[k] || `Voice ${++vi}`; return n ? { name: n.name, nameRead: true } : { name: inf, nameRead: false }; };
    if (v.split) {
      parts.push({ ...nm(0), kind: 'vocal', src: [{ staff: v.staff, voice: 1 }], layout: `Staff ${v.staff + 1}, stems up (split from a shared staff)` });
      parts.push({ ...nm(1), kind: 'vocal', src: [{ staff: v.staff, voice: 2 }], layout: `Staff ${v.staff + 1}, stems down (split from a shared staff)` });
      notes.push(`Staff ${v.staff + 1}: two voices on one staff, split by stem direction into ${parts[parts.length - 2].name} and ${parts[parts.length - 1].name}.`);
    } else if (v.small) {
      parts.push({ ...nm(0), kind: 'instrument', src: [{ staff: v.staff, voice: 'chordal' }], layout: `Staff ${v.staff + 1} (small staff: a separate instrument)` });
      notes.push(`Staff ${v.staff + 1}: printed smaller than the staves below it, read as a separate instrument part (not part of the piano's grand staff).`);
    } else parts.push({ ...nm(0), kind: 'vocal', src: [{ staff: v.staff, voice: 'chordal' }], layout: `Staff ${v.staff + 1}` });
  }
  parts.forEach(p => { if (p.nameRead) read.push(p.name); });
  if (read.length) notes.push(`Part names read from the page: ${read.join(', ')}.`);
  parts.forEach((p, i) => { p.id = 'P' + (i + 1); p.color = COLORS[i % COLORS.length]; });
  return { parts, nSt, notes, clefs, stats, link, evid };
}

// Key signature: every staff carries the same key. A staff whose accidentals
// were missed reads as 0 (or as fewer accidentals than printed), while extra
// accidentals are rare, so the largest key that several staves agree on wins.
function chooseKey(systems) {
  const all = [];
  systems.forEach(sy => sy.staves.forEach(s => all.push(s.hdr.fifths | 0)));
  if (!all.length) return 0;
  const nz = all.filter(v => v !== 0);
  if (!nz.length || (nz.length < 2 && nz.length < 0.2 * all.length)) return 0;
  const pos = nz.filter(v => v > 0).length, neg = nz.length - pos;
  const sgn = pos >= neg ? 1 : -1;
  const same = nz.filter(v => Math.sign(v) === sgn).map(Math.abs);
  const cnt = {};
  same.forEach(v => { cnt[v] = (cnt[v] || 0) + 1; });
  const vals = Object.keys(cnt).map(Number).sort((a, b) => b - a);
  for (const v of vals) if (cnt[v] >= 2 || cnt[v] >= 0.25 * same.length) return sgn * v;
  return sgn * vals[vals.length - 1];
}

const qsum = (evs) => evs.reduce((a, e) => a + e.q, 0);
const EPS = 1e-6;

// onsets of the stream that disagree with an onset another voice has at the
// same x (simultaneous notes are printed vertically aligned)
function anchorMisses(evs, anchors, sp) {
  if (!anchors.length) return 0;
  let t = 0, miss = 0;
  for (const e of evs) {
    if (!e.rest && e.x != null) {
      const near = anchors.filter(a => Math.abs(a.x - e.x) <= 0.8 * sp);
      if (near.length && !near.some(a => Math.abs(a.t - t) < EPS)) miss++;
    }
    t += e.q;
  }
  return miss;
}

// Cheapest set of duration edits that makes a voice fill the measure exactly:
// a missed / extra augmentation dot, a missed / extra flag or beam (halve /
// double) or, in an over-full measure, a false notehead dropped. A dynamic
// programme over the events and the time reached so far; an edit that puts a
// note's onset out of step with a voice printed at the same x (simultaneous
// notes are vertically aligned) costs extra. Returns {events, ok}.
function searchRepair(evs, target, anchors, sp, over) {
  const U = DIV, T = Math.round(target * U);
  const near = evs.map(e => (e.rest || e.x == null) ? null : anchors.filter(a => Math.abs(a.x - e.x) <= 0.8 * sp).map(a => Math.round(a.t * U)));
  const opts = evs.map((e, i) => {
    const q = e.q, d = e.dots || 0, o = [[q, 0]];
    if (!e.rest) {
      if (!d) o.push([q * 1.5, 1.0]);
      if (d === 1) o.push([q / 1.5, 1.2]);
      o.push([q / 2, 1.5]);
      if (q * 2 <= 4 + EPS) o.push([q * 2, 1.6]);
      // a note that took a syllable is printed for sure: dropping it costs more
      // ties go to the earliest event: header leftovers and barline debris
      // come first in a bar
      if (over) o.push([0, (e.lyrics ? 3.5 : 1.8) + 0.001 * i]);
    }
    // the value as read is always an option (a tuplet note has no plain type)
    return o.filter(([nq, c]) => c === 0 || nq === 0 || valueOk(e, nq)).map(([nq, c]) => [Math.round(nq * U), nq, c]);
  });
  const layers = [new Map([[0, { c: 0, from: 0, q: null }]])];
  for (let i = 0; i < evs.length; i++) {
    const cur = layers[i], nxt = new Map();
    for (const [t, st] of cur) {
      const nr = near[i];
      for (const [du, nq, c] of opts[i]) {
        const t2 = t + du;
        if (t2 > T) continue;
        const cost = st.c + c + (du > 0 && nr && nr.length && !nr.includes(t) ? 2 : 0);
        const p = nxt.get(t2);
        if (!p || cost < p.c - 1e-9) nxt.set(t2, { c: cost, from: t, q: nq });
      }
    }
    layers.push(nxt);
  }
  const end = layers[evs.length].get(T);
  if (!end) return null;
  const qs = new Array(evs.length);
  for (let i = evs.length, t = T; i > 0; i--) { const st = layers[i].get(t); qs[i - 1] = st.q; t = st.from; }
  return { cost: end.c, qs };
}

function repairStream(evs, target, anchors, sp) {
  const sum = qsum(evs), diff = target - sum;
  const base = anchorMisses(evs, anchors, sp);
  const best = searchRepair(evs, target, anchors, sp, diff < -EPS);
  // leaving a gap costs about as much as two edits; an over-full bar must be
  // fixed, so a little more is spent there before squeezing it
  const gapCost = 2.6 + 2 * base;
  if (best && best.cost < gapCost + (diff < -EPS ? 1.2 : 0)) {
    const out = [];
    evs.forEach((e, i) => {
      const nq = best.qs[i];
      if (nq === 0) return;
      if (Math.abs(nq - e.q) > EPS) { e.q = nq; e.dots = (qToType(nq) || { dots: 0 }).dots; }
      out.push(e);
    });
    return { events: out, ok: true };
  }
  if (diff > EPS) return { events: evs.concat([{ forward: true, q: diff }]), ok: false };
  // still over-full: shorten the longest values (drop a dot, else halve) until
  // the voice fits, so every note read is kept; pad any small gap left over
  {
    const tr = evs.map(e => ({ ...e }));
    let sum = qsum(tr);
    while (sum > target + EPS) {
      let k = -1;
      tr.forEach((e, i) => { if (e.q > 0.25 + EPS && (k < 0 || e.q > tr[k].q + EPS || (e.rest && !tr[k].rest && Math.abs(e.q - tr[k].q) < EPS))) k = i; });
      if (k < 0) break;
      const e = tr[k], nq = e.dots ? e.q / 1.5 : e.q / 2;
      if (!qToType(nq)) break;
      sum -= e.q - nq; e.q = nq; e.dots = qToType(nq).dots;
    }
    if (sum <= target + EPS) {
      evs.forEach((e, i) => { e.q = tr[i].q; e.dots = tr[i].dots; });
      const out = evs.slice();
      if (target - sum > EPS) out.push({ forward: true, q: target - sum });
      return { events: out, ok: false };
    }
  }
  // cannot be shortened enough: keep what fits and cut the note that crosses
  // the barline so the measure stays importable (notation programs reject
  // over-full bars)
  const out = [];
  let t = 0;
  for (const e of evs) {
    if (t >= target - EPS) break;
    if (t + e.q > target + EPS) {
      const rest = target - t, tt = qToType(rest);
      if (tt) { e.q = rest; e.dots = tt.dots; out.push(e); }
      else for (const q of restsFor(rest)) out.push({ forward: true, q });
      t = target; break;
    }
    out.push(e); t += e.q;
  }
  return { events: out, ok: false };
}

// Two voices sharing a staff (closed score): stem up -> upper voice, stem
// down -> lower voice, a head with both stems -> both (unison). Heads printed
// side by side for a second between the voices are one onset. A lone head goes
// to its stem's voice and is copied to the other voice as a unison only when
// that voice is not still holding a note (a missed head there would otherwise
// leave a hole in its rhythm). With reliable stems, a voice that reaches a
// shared onset early has its previous note lengthened (a missed dot or flag),
// or gets a rest there when no note value fits.
function splitTwoVoices(chordal, sp, trust) {
  const slots = [];
  const only = (dirs, d) => !!dirs && dirs.size === 1 && dirs.has(d);
  for (const ev of chordal) {
    const dirs = new Set(ev.heads.map(h => h.stemDir));
    const last = slots[slots.length - 1];
    const near = last && ev.x - last.x1 < 1.5 * sp;
    // opposite stems side by side, or two lone heads a step apart (a second
    // between the voices is printed with the heads beside each other)
    const opposite = (only(last && last.dirs, 1) && only(dirs, -1)) || (only(last && last.dirs, -1) && only(dirs, 1));
    const second = last && last.heads.length === 1 && ev.heads.length === 1 && Math.abs(last.heads[0].p - ev.heads[0].p) === 1;
    if (near && (opposite || second)) {
      last.heads.push(...ev.heads); last.x1 = ev.x; dirs.forEach(d => last.dirs.add(d)); last.pair = true;
      continue;
    }
    slots.push({ x: ev.x, x1: ev.x, heads: ev.heads.slice(), dirs });
  }
  const out = { 1: [], 2: [] }, cur = { 1: 0, 2: 0 };
  for (const sl of slots) {
    const hs = sl.heads.slice().sort((a, b) => a.y - b.y);
    const v1 = hs.filter(h => h.stemDir === 1 || h.stemDir === 2), v2 = hs.filter(h => h.stemDir === -1 || h.stemDir === 2);
    let a1 = null, a2 = null;
    if (sl.pair && hs.length === 2 && !(hs[0].stemDir === -1 && hs[1].stemDir === 1)) { a1 = hs[0]; a2 = hs[1]; }
    else if (v1.length && v2.length) { a1 = v1[0]; a2 = v2[v2.length - 1]; }
    else if (v1.length || v2.length) {
      const c = v1.length ? v1 : v2;
      if (c.length >= 2) { a1 = c[0]; a2 = c[c.length - 1]; } // two voices on one stem
      else {
        const h = c[0], mine = v1.length ? 1 : 2, other = 3 - mine;
        const free = cur[other] <= cur[mine] + 1e-6;
        if (mine === 1) { a1 = h; if (free) a2 = h; } else { a2 = h; if (free) a1 = h; }
      }
    } else if (hs.length) { a1 = hs[0]; a2 = hs[hs.length - 1]; } // stemless (whole notes)
    const vs = [[1, a1], [2, a2]].filter(([, h]) => h);
    const t = Math.max(...vs.map(([v]) => cur[v]));
    for (const [v, h] of vs) {
      const gap = t - cur[v];
      if (trust && gap > 1e-6) {
        // a hole before an onset the other voice shares: most often a missed
        // dot or flag on the previous note, rarely a printed rest
        const prev = out[v][out[v].length - 1];
        if (prev && !prev.rest && qToType(prev.q + gap)) { prev.q += gap; prev.dots = qToType(prev.q).dots; }
        else for (const q of restsFor(gap)) out[v].push({ rest: true, q, dots: 0, x: sl.x });
      }
      cur[v] = t;
      // a head with both stems: the lower voice's value is read on its own
      // stem (assemble.js h.dur.down)
      const d = (v === 2 && h.stemDir === 2 && h.dur.down) || h.dur;
      out[v].push({ x: sl.x, heads: [h], q: d.q, dots: d.dots });
      cur[v] += d.q;
    }
  }
  return out;
}

// Two voices inside one staff of a keyboard part (L17): a melody with stems
// up over an accompaniment with stems down (or the reverse), printed in
// the same columns but with their own note values. The chordal reading gives
// every head of a column the shortest value there and loses a head shared by
// both voices (one notehead, two stems). Split only on direct evidence that
// two rhythms run at once: a head with both stems, or a column whose
// up-stem and down-stem heads have different values. Voice 1 takes the
// up-stem (and stemless) heads as chords, voice 2 the down-stem heads (a
// shared head with the value read on its down stem). Voice 2's onsets are
// taken from voice 1 where both have a column at the same x (simultaneous
// notes are printed aligned); a hole before such an onset is a rest. Returns
// {1, 2} or null (no evidence, or the voices do not line up: keep chordal).
function keyboardVoices(chordal, rests, sp) {
  let evidence = 0;
  const up = [], dn = [];
  for (const ev of chordal) {
    const hs = ev.heads;
    const u = hs.filter(h => h.stemDir !== -1), d = hs.filter(h => h.stemDir === -1 || h.stemDir === 2);
    const qd = (h) => ((h.stemDir === 2 && h.dur.down) || h.dur);
    // a shared head whose two stems carry different values
    if (hs.some(h => h.stemDir === 2 && Math.abs(qd(h).q - h.dur.q) > EPS)) evidence++;
    if (u.some(h => h.stemDir === 1) && d.some(h => h.stemDir === -1)) {
      const a = Math.min(...u.map(h => h.dur.q)), b = Math.min(...d.map(h => qd(h).q));
      if (Math.abs(a - b) > EPS) evidence++;
    }
    if (u.length) {
      const q = Math.min(...u.map(h => h.dur.q)), h0 = u.find(h => Math.abs(h.dur.q - q) < EPS) || u[0];
      up.push({ x: ev.x, heads: u, q, dots: h0.dur.dots });
    }
    if (d.length) {
      const q = Math.min(...d.map(h => qd(h).q)), h0 = d.find(h => Math.abs(qd(h).q - q) < EPS) || d[0];
      dn.push({ x: ev.x, heads: d, q, dots: qd(h0).dots, low: true });
    }
  }
  // one sign and one lone lower note is as likely a stray stem or flag
  if (!evidence || !up.length || !dn.length || (evidence < 2 && dn.length < 2)) return null;
  const v1 = mergeRests(up, rests, 1, sp);
  const anchors = [];
  let t = 0;
  for (const e of v1) { if (e.x != null) anchors.push({ x: e.x, t }); t += e.q; }
  const total = t, v2 = [];
  // a hole in voice 2 shows as a rest only where a low rest is printed in
  // it; keyboard engraving often leaves a resting inner voice unmarked, and
  // an unprinted rest stays a hidden <forward>
  const low = (rests || []).filter(r => r.pos > 2.4);
  const fill = (q, xa, xb) => (low.some(r => r.x > xa && r.x < xb)
    ? restsFor(q).map(v => ({ rest: true, glyph: true, q: v, dots: qToType(v) ? qToType(v).dots : 0, x: Number.isFinite(xb) ? xb - 0.5 * sp : undefined }))
    : [{ forward: true, hidden: true, q }]);
  let cur = 0, px = -Infinity;
  for (const e of dn) {
    const a = anchors.filter(z => Math.abs(z.x - e.x) <= 0.8 * sp).sort((p, q) => Math.abs(p.x - e.x) - Math.abs(q.x - e.x))[0];
    if (a) {
      if (a.t < cur - EPS) return null; // voice 2 would overlap itself
      if (a.t > cur + EPS) v2.push(...fill(a.t - cur, px, e.x));
      cur = a.t;
    }
    v2.push(e);
    cur += e.q;
    px = e.x;
  }
  if (cur > total + EPS) return null;
  if (total - cur > EPS) v2.push(...fill(total - cur, px, Infinity));
  return { 1: v1, 2: v2 };
}

// printed value of a note inside a tuplet (assemble.js h.dur.tuplet {actual,
// normal}): q * actual / normal is the plain value it is drawn as
const tupletOf = (e) => (!e.rest && e.heads && e.heads[0] && e.heads[0].dur && e.heads[0].dur.tuplet) || null;
const valueOk = (e, q) => !!(qToType(q) || (tupletOf(e) && qToType(q * tupletOf(e).actual / tupletOf(e).normal)));

function qToType(q) {
  const table = [[4, 'whole', 0], [3, 'half', 1], [2, 'half', 0], [1.5, 'quarter', 1], [1, 'quarter', 0], [0.75, 'eighth', 1],
    [0.5, 'eighth', 0], [0.375, '16th', 1], [0.25, '16th', 0], [0.125, '32nd', 0], [6, 'whole', 1],
    [0.1875, '32nd', 1], [0.0625, '64th', 0], [3.5, 'half', 2], [1.75, 'quarter', 2], [0.875, 'eighth', 2], [0.4375, '16th', 2]];
  for (const [v, t, d] of table) if (Math.abs(v - q) < 1e-6) return { type: t, dots: d };
  return null;
}

function restsFor(q) {
  // split a gap into standard rest values
  const out = [];
  let left = Math.round(q * DIV) / DIV;
  for (const v of [4, 3, 2, 1.5, 1, 0.75, 0.5, 0.25, 0.125]) while (left >= v - 1e-6) { out.push(v); left -= v; }
  return out;
}

function buildScore(pages, lyricsBySystem = {}, opts = {}) {
  const warnings = [];
  // time signatures on every system, after barlines and at system ends (meter.js; once per page)
  // and barline kinds, repeats and volta brackets (structure.js)
  for (const p of pages) if (p.asm && !p.asm.metersRead) {
    try { readMeters(p.fr, p.asm); } catch (e) { /* the piece's one meter */ }
    try { readStructure(p.fr, p.asm); } catch (e) { /* plain barlines */ }
    try { readArticulations(p.fr, p.asm); } catch (e) { /* no articulations */ }
    try { readDoubleDots(p.fr, p.asm); } catch (e) { /* single dots */ }
    try { readOttavas(p.fr, p.asm); } catch (e) { /* no octave lines */ }
    p.asm.metersRead = true;
  }
  const systems = pages.flatMap(p => p.asm.systems.map(s => ({ ...s, fr: p.fr, comps: p.asm.comps })));
  if (!systems.length) return { parts: [], measures: 0, warnings: ['No music systems found.'], xml: emptyXML() };
  // marks first (text.js via symbols.js): braces inform the layout
  for (const p of pages) { try { pageMarks(p.fr, p.asm); } catch (e) { /* layout reads without them */ } }
  const layout = chooseLayout(systems, lyricsBySystem, opts);
  const { parts } = layout;
  const fifths = chooseKey(systems);
  const kAlt = keyAlters(fifths);
  // clefs per staff index (majority of the clefs read across systems)
  const clefs = layout.clefs;
  if (systems.some(sy => sy.staves.some(s => s.hdr.clefGuessed))) warnings.push('Clef not recognised on some staves; assumed treble on top / bass below.');

  // collect events per raw measure segment, per part
  const segs = [];
  for (const sy of systems) for (const [xa, xb] of sy.measures) segs.push({ sy, xa, xb });
  // stems are trusted on a staff when up and down stems are seen together on it
  const trust = layout.stats.map(st => st.mix >= 0.25);
  // rests printed on each staff (rests.js) go into every voice at their x
  // position, so rhythm repair counts them
  // streams written per part: one per source staff; a keyboard part also has
  // an optional second voice on each staff (L17), empty unless that staff
  // shows two rhythms at once in a bar. p.src stays the staff list.
  parts.forEach(p => {
    const multi = p.src.length > 1;
    p.streams = p.src.map((s, k) => ({ ...s, staffNo: k + 1, vno: multi ? 1 + 4 * k : 1 }));
    if (p.kind === 'keyboard') p.src.forEach((s, k) => p.streams.push({ staff: s.staff, voice: 'kb2', staffNo: k + 1, vno: 2 + 4 * k, optional: true }));
  });
  let kbSplit = 0;
  const segEv = segs.map(m => {
    const cache = {}, restCache = {};
    return parts.map(p => p.streams.map(src => {
      const s = m.sy.staves[src.staff];
      if (!s) return [];
      const c = (cache[src.staff] ||= staffMeasureEvents(m.sy.fr, m.sy.fr.R, m.sy.comps, s, m.xa, m.xb));
      const rs = (restCache[src.staff] ||= m.sy.fr.R ? detectRests({ R: m.sy.fr.R, comps: m.sy.comps || [], s, xa: m.xa, xb: m.xb }) : []);
      if (p.kind === 'keyboard') {
        if (c.kb === undefined) { c.kb = keyboardVoices(c.chordal, rs, s.st.space); if (c.kb) kbSplit++; }
        if (src.voice === 'kb2') return c.kb ? c.kb[2] : [];
        if (c.kb) return c.kb[1];
      }
      if (src.voice === 'kb2') return [];
      if (src.voice === 1 || src.voice === 2) {
        c.split ||= splitTwoVoices(c.chordal, s.st.space, !!trust[src.staff]);
        return mergeRests(c.split[src.voice], rs, src.voice, s.st.space);
      }
      return mergeRests(c[src.voice] || [], rs, src.voice, s.st.space);
    }));
  });
  // grace notes the head finder took as notes: filled heads clearly narrower
  // than the page's heads (upper quartile; about 0.9 staff space against 1.2-1.3), short
  // values, leave the bar's count and go before the next note (e.graces)
  // On unless opts.graceHeads === false (it passes regress.mjs: benchmark 0.950 ->
  // 0.951, challenge 0.829 -> 0.831; a few items dip, e.g. rst01 rests)
  if (opts.graceHeads !== false) {
    const ratio = new Map();
    const pageRatio = (fr) => {
      if (!ratio.has(fr)) {
        const r = (fr.heads || []).filter(h => h.kind === 'filled' && h.w).map(h => h.w / (h.sp || fr.ss)).sort((a, b) => a - b);
        ratio.set(fr, r.length >= 8 ? r[Math.floor(0.75 * r.length)] : 0);
      }
      return ratio.get(fr);
    };
    segEv.forEach((e, si) => {
      const fr = segs[si].sy.fr, med = pageRatio(fr);
      if (med < 1.12) return;
      const small = (h) => h.kind === 'filled' && h.w && h.w / (h.sp || fr.ss) <= Math.min(1.0, 0.8 * med);
      e.forEach((streams, pi) => streams.forEach((evs, k) => {
        if (!evs.some(x => !x.rest && x.heads && x.heads.length && x.heads.every(small))) return;
        const out = [];
        let pend = [];
        const isGrace = (i) => { const x = evs[i]; return !x.rest && !x.forward && x.heads && x.heads.length && x.heads.every(small) && x.q <= 0.5; };
        for (let i = 0; i < evs.length; i++) {
          const x = evs[i];
          if (isGrace(i)) {
            pend.push(...x.heads.map(h => ({ p: Math.round(h.p), slash: false, n: 2 })));
            continue;
          }
          if (pend.length && !x.rest && x.heads) { if (pend.length === 1) pend[0].n = 1; x.graces = pend; pend = []; }
          out.push(x);
        }
        streams[k] = out;
      }));
    });
  }
  // length of each segment: the most common stream total (a stream that lost
  // a note or a rest comes out short, so one stream alone is not trusted)
  const segSum = segEv.map(e => {
    const sums = [];
    e.forEach(streams => streams.forEach(evs => {
      const s = evs.reduce((a, x) => a + x.q, 0);
      if (s > 0) sums.push(Math.round(s * 4) / 4);
    }));
    return sums.length ? mode(sums) : 0;
  });
  // time signature: most common full-measure length, also counting pairs of
  // short segments (phrase barlines / measures split across systems)
  const votes = {};
  const vote = (v, wgt) => { const r = Math.round(v * 2) / 2; if (r > 0) votes[r] = (votes[r] || 0) + wgt; };
  // prior: common metres need less evidence than rare ones (measure length
  // in quarters: 4 = 4/4, 3 = 3/4 or 6/8, 2 = 2/4, 6 = 6/4 or 3/2, ...)
  const PRIOR = { 4: 1, 3: 0.9, 2: 0.75, 6: 0.45, 1.5: 0.4, 5: 0.25, 3.5: 0.15 };
  segSum.forEach(v => vote(v, 1));
  // a pair of neighbours votes for their sum unless both are already full
  // bars of the best single-segment metre: two short halves of one bar
  // (a phrase barline, a bar split at a system break) are evidence, but two
  // whole 2/4 bars side by side are not a 4/4 bar
  const rnd = (v) => Math.round(v * 2) / 2;
  const single = +((Object.entries(votes).filter(([k]) => +k >= 1.5 && PRIOR[+k]).map(([k, v]) => [k, v * PRIOR[+k]]).sort((a, b) => b[1] - a[1])[0] || [0])[0]);
  segSum.forEach((v, i) => {
    if (i + 1 >= segSum.length) return;
    if (single && rnd(v) === single && rnd(segSum[i + 1]) === single) return;
    vote(v + segSum[i + 1], 0.6);
  });
  let mq = +(Object.entries(votes).filter(([k]) => +k >= 1.5 && PRIOR[+k]).map(([k, v]) => [k, v * PRIOR[+k]]).sort((a, b) => b[1] - a[1])[0] || [4])[0];
  let time = { beats: 4, type: 4 };
  if (Number.isInteger(mq) && mq >= 2 && mq <= 6) time = { beats: mq, type: 4 };
  else if (mq === 1.5) time = { beats: 3, type: 8 };
  else if (mq === 3.5) time = { beats: 7, type: 8 };
  else { mq = 4; warnings.push('Could not infer a time signature; using 4/4.'); }
  // a time signature read from the staff headers (C, cut C, or digits when
  // the header reader gives them) is shown as printed when its bar length
  // agrees with the contents, and wins outright when the contents give it
  // fair support
  let timeRead = false;
  {
    const hs = systems.flatMap(sy => sy.staves.map(s => s.hdr && s.hdr.time)).filter(t => t && plausibleMeter(t));
    if (hs.length >= Math.max(1, 0.3 * systems.filter(sy => sy.index === 0).reduce((a, sy) => a + sy.staves.length, 0))) {
      const key = mode(hs.map(t => `${t.beats}/${t.type}/${t.symbol || ''}`)), [b, ty] = key.split('/').map(Number), sym = key.split('/')[2], hq = (b * 4) / ty;
      const qNow = (time.beats * 4) / time.type;
      if (Math.abs(hq - qNow) < 1e-6 || (votes[hq] || 0) >= 0.5 * (votes[qNow] || 0)) { time = { beats: b, type: ty, symbol: sym || '' }; timeRead = true; }
    }
  }
  // the meter in force at each segment (meter.js: sy.meters, read on every system header, after
  // barlines and at system ends). Used when the page shows a change of meter; a piece read
  // with one meter throughout keeps the meter chosen above.
  const segTime = segs.map(() => time);
  {
    const ms = systems.flatMap(sy => (sy.meters || []).filter(m => !m.courtesy));
    const vals = new Set(ms.map(m => `${m.beats}/${m.type}/${m.symbol || ''}`));
    if (vals.size >= 2) {
      let cur = time;
      segs.forEach((sg, i) => {
        const sp = (sg.sy.staves[0] && sg.sy.staves[0].st.space) || 16;
        // a courtesy signature at the end of the system before stands for this system's header
        // when that was not read
        const prev = i > 0 && segs[i - 1].sy !== sg.sy ? (segs[i - 1].sy.meters || []).find(m => m.courtesy) : null;
        if (prev && !(sg.sy.meters || []).some(m => m.header)) cur = { beats: prev.beats, type: prev.type, symbol: prev.symbol || '' };
        const here = (sg.sy.meters || []).filter(m => !m.courtesy && m.x <= sg.xa + 0.5 * sp);
        if (here.length && (i === 0 || segs[i - 1].sy !== sg.sy || here[here.length - 1].x > segs[i - 1].xa + 0.5 * sp)) {
          const m = here[here.length - 1];
          cur = { beats: m.beats, type: m.type, symbol: m.symbol || '' };
        }
        segTime[i] = cur;
      });
      const nCh = segTime.filter((t, i) => i > 0 && (t.beats !== segTime[i - 1].beats || t.type !== segTime[i - 1].type || t.symbol !== segTime[i - 1].symbol)).length;
      if (nCh) warnings.push(`${nCh} change${nCh > 1 ? 's' : ''} of time signature read from the page.`);
    }
  }
  const lenOf = (i) => (segTime[i].beats * 4) / segTime[i].type;
  const mLen = (time.beats * 4) / time.type;
  warnings.push(timeRead ? `Time signature read from the page: ${time.beats}/${time.type}.` : `Time signature inferred from measure contents: ${time.beats}/${time.type}.`);
  // Barline reconciliation. Barline detection both misses barlines and finds
  // false ones (stems, brackets, text). Within each system the raw segments
  // are grouped into measures by a small dynamic programme: a group costs how
  // far its content is from a full bar plus a charge for every barline it
  // drops (cheap when one side is a sliver no wider than a few staff spaces,
  // which is how a stem misread as a barline shows up). An opening pickup and
  // a closing short bar cost nothing. Over-full groups are cut later.
  const nStreams = segEv.length ? segEv[0].reduce((a, ps) => a + ps.length, 0) : 0;
  const segStreamSums = segEv.map(e => e.flatMap(ps => ps.map(evs => qsum(evs))));
  const groupDev = (a, b, edge) => {
    const mLen = lenOf(a);
    // dropping a barline must never make a bar over-full (its notes would be cut)
    const sums = [];
    for (let k = 0; k < nStreams; k++) {
      let s = 0;
      for (let i = a; i <= b; i++) s += segStreamSums[i][k] || 0;
      if (s > 1e-6) sums.push(Math.round(s * 4) / 4);
    }
    if (!sums.length) return 0; // nothing but rests: a bar of rests
    const S = mode(sums);
    if (b > a && Math.max(...sums) > mLen + 1e-6) return Infinity;
    if (Math.abs(S - mLen) < 1e-6 || (edge && S < mLen)) return 0;
    return 0.1 + Math.min(1, Math.abs(S - mLen) / mLen);
  };
  const measures = []; // [{segs:[...]}]
  for (let i0 = 0; i0 < segs.length;) {
    let i1 = i0;
    while (i1 + 1 < segs.length && segs[i1 + 1].sy === segs[i0].sy) i1++;
    const n = i1 - i0 + 1;
    // the printed bar numbers may fix this system's bar count (checkBarNumbers,
    // second pass): T bars, counting a group whose contents fill k bars as k
    const sk = segs[i0].sy.page + ':' + segs[i0].sy.index;
    const T = opts.barTargets && opts.barTargets[sk] ? opts.barTargets[sk] : 0;
    const cost = (i, j) => {
      const a = i0 + i, b = i0 + j - 1;
      const edge = a === 0 || b === segs.length - 1;
      let c = 2 * groupDev(a, b, edge);
      for (let t = a; t < b; t++) {
        const sp = (segs[t].sy.staves[0] && segs[t].sy.staves[0].st.space) || 16;
        const w = Math.min(segs[t].xb - segs[t].xa, segs[t + 1].xb - segs[t + 1].xa) / sp;
        c += w < 4 ? 0.15 : 0.45;
      }
      return c;
    };
    // bars a group holds: one, or k when its contents fill k bars (a missed barline)
    const barsIn = (i, j) => {
      let S = 0;
      for (let t = i0 + i; t < i0 + j; t++) S += segSum[t];
      const mLen = lenOf(i0 + i);
      const k = Math.round(S / mLen);
      return k >= 2 && Math.abs(S - k * mLen) < 1e-6 ? k : 1;
    };
    const groups = [], gBars = [];
    if (T) {
      // best[j][g]: first j segments holding g bars; the system holds exactly T
      const best = Array.from({ length: n + 1 }, () => new Array(T + 1).fill(Infinity)), from = Array.from({ length: n + 1 }, () => new Array(T + 1).fill(-1));
      best[0][0] = 0;
      for (let j = 1; j <= n; j++) for (let i = Math.max(0, j - 5); i < j; i++) {
        // only clean fixes: no over-full merge, and a group counts k bars only
        // when its contents fill exactly k
        const k = barsIn(i, j), c = cost(i, j);
        if (c === Infinity) continue;
        for (let g = k; g <= T; g++) {
          if (best[i][g - k] === Infinity) continue;
          if (best[i][g - k] + c < best[j][g] - 1e-9) { best[j][g] = best[i][g - k] + c; from[j][g] = i; }
        }
      }
      if (best[n][T] < Infinity) for (let j = n, g = T; j > 0;) { const i = from[j][g], k = barsIn(i, j); groups.unshift(Array.from({ length: j - i }, (_, t) => i0 + i + t)); gBars.unshift(k); g -= k; j = i; }
    }
    if (!groups.length) {
      const best = new Array(n + 1).fill(Infinity), from = new Array(n + 1).fill(-1);
      best[0] = 0;
      for (let j = 1; j <= n; j++) {
        for (let i = Math.max(0, j - 5); i < j; i++) {
          if (best[i] === Infinity) continue;
          const c = cost(i, j);
          if (best[i] + c < best[j] - 1e-9) { best[j] = best[i] + c; from[j] = i; }
        }
      }
      for (let j = n; j > 0; j = from[j]) groups.unshift(Array.from({ length: j - from[j] }, (_, t) => i0 + from[j] + t));
    }
    // with the bar count fixed, a group is cut into its bars by contents
    // exactly when it holds several (forceSplit), never otherwise (noSplit)
    groups.forEach((g, k) => measures.push(gBars.length ? { segs: g, forceSplit: gBars[k] > 1, noSplit: gBars[k] === 1 } : { segs: g }));
    i0 = i1 + 1;
  }
  // a bar split across a system break: two short halves that make one bar
  for (let k = 1; k + 1 < measures.length; k++) {
    const a = measures[k], b = measures[k + 1];
    if (segs[a.segs[0]].sy === segs[b.segs[0]].sy || a.segs.length > 1 || b.segs.length > 1) continue;
    const sa = segSum[a.segs[0]], sb = segSum[b.segs[0]], mLen = lenOf(a.segs[0]);
    if (sa < mLen - 1e-6 && sb > 1e-6 && Math.abs(sa + sb - mLen) < 1e-6) { a.segs.push(...b.segs); measures.splice(k + 1, 1); }
  }
  if (opts.debug) segs.forEach((sg, i) => opts.debug.push(`seg ${i} sys ${sg.sy.page}:${sg.sy.index} x ${Math.round(sg.xa)}-${Math.round(sg.xb)} sum ${segSum[i]} streams ${segEv[i].map(ps => ps.map(evs => evs.map(e => (e.rest ? 'r' : '') + e.q).join(',')).join('/')).join(' | ')}`));
  // an optional voice found in only some segments of a bar keeps its time
  // through the others (the length of that staff's main voice there)
  const perPart = parts.map((p, pi) => measures.map(m => p.streams.map((src, k) => {
    if (src.optional && m.segs.length > 1 && m.segs.some(si => segEv[si][pi][k].length)) {
      const main = p.streams.findIndex(s => !s.optional && s.staffNo === src.staffNo);
      return { staff: src.staff, events: m.segs.flatMap(si => (segEv[si][pi][k].length ? segEv[si][pi][k] : qsum(segEv[si][pi][main]) > EPS ? [{ forward: true, q: qsum(segEv[si][pi][main]) }] : [])) };
    }
    return { staff: src.staff, events: m.segs.flatMap(si => segEv[si][pi][k]) };
  })));
  if (kbSplit) warnings.push(`Keyboard: two voices on one staff (stems up and down with their own note values) in ${kbSplit} staff-bars, written as voices 1 and 2.`);
  measures.forEach(m => { m.sy = segs[m.segs[0]].sy; m.sys = m.segs.map(si => segs[si].sy); });
  // remember which parts each head ended up in (overlay colouring)
  perPart.forEach((pm, pi) => pm.forEach(streams => streams.forEach(st => st.events.forEach(e => (e.heads || []).forEach(h => {
    (h.parts ||= []); if (!h.parts.includes(pi)) h.parts.push(pi);
  })))));

  // lyrics: each underlay line belongs to the staff above it. On a staff split
  // into two voices the line goes to ONE voice, chosen once per text band for
  // the whole piece from how well the syllables sit under each voice's onsets
  // (summed over every system and verse). With no clear winner a line between
  // staves goes to the upper voice (the melody); a line under the lowest split
  // staff whose two voices share every onset goes to both (research-voices.md
  // section 7.2). A line whose local fit is clearly better in the other voice
  // (each voice with its own words) follows that voice.
  // opts.copyLyrics copies every line to all fitting voices of its staff
  // (research-voices.md section 7.2). Keyboard staves never take underlay.
  const lyrNotes = new Set();
  const vocalStaves = parts.filter(p => p.kind !== 'keyboard').map(p => p.src[0].staff);
  const topVocal = vocalStaves.length ? Math.min(...vocalStaves) : -1;
  const splitStaves = parts.filter(p => p.kind !== 'keyboard' && p.src[0].voice === 2).map(p => p.src[0].staff);
  const lowestSplit = splitStaves.length ? Math.max(...splitStaves) : -1;
  const lines = [];
  for (const sy of systems) {
    const lyr = lyricsBySystem[sy.page + ':' + sy.index];
    if (!lyr || !lyr.length) continue;
    const sp = sy.staves[0] ? sy.staves[0].st.space : 16;
    const evCache = {};
    // sung notes of a part in this system (rests never take a syllable)
    const evOf = (pi) => (evCache[pi] ||= segs.flatMap((sg, si) => (sg.sy === sy ? segEv[si][pi][0] : [])).filter(e => !e.rest && !e.forward && e.heads && e.heads.length));
    const fitOf = (v) => parts.map((p, pi) => ({ p, pi })).filter(({ p }) => p.kind !== 'keyboard' && p.src[0].staff === v.band)
      .map(c => { const evs = evOf(c.pi); return { ...c, evs, fit: lyricFit(v.syllables, evs, sp), soft: softFit(v.syllables, evs, sp) }; });
    const sysLines = lyr.filter(v => v.syllables && v.syllables.length && !v.stanza).map(v => ({ sy, v, sp, cands: fitOf(v) })).filter(L => L.cands.length);
    // verses stack under the same staff: once one line of a band clearly
    // follows the notes, its sibling lines (same band, same system) are
    // underlay too and need only a looser fit (unhyphenated multi-note words
    // and OCR-merged words pull a line's syllables off the onsets)
    const bandOK = new Set(sysLines.filter(L => wordy(L.v.syllables) && L.cands.some(c => c.fit >= 0.5)).map(L => L.v.band));
    sysLines.forEach(L => { L.minFit = bandOK.has(L.v.band) ? 0.3 : 0.5; });
    lines.push(...sysLines);
  }
  // piece-wide evidence per text band: summed soft fit of each candidate part
  const bandEv = {};
  for (const L of lines) {
    if (L.cands.length < 2 || !wordy(L.v.syllables)) continue;
    const b = (bandEv[L.v.band] ||= {});
    for (const c of L.cands) b[c.pi] = (b[c.pi] || 0) + c.soft;
  }
  const bandVoice = {};
  for (const band in bandEv) {
    const e = bandEv[band], pis = Object.keys(e).map(Number).sort((a, b) => a - b);
    const lowest = +band === lowestSplit && +band !== topVocal;
    const prior = lowest ? pis[pis.length - 1] : pis[0];
    // a syllable under an onset that only one voice has adds about 1 to that
    // voice's total; voices that share every onset tie. A voice whose onsets
    // include the other's (eighths against quarters) can only gain, so a line
    // between staves leaves the melody (upper voice) only on strong evidence.
    let best = prior;
    for (const pi of pis) if (e[pi] > (lowest ? e[best] + 0.6 : 1.25 * e[best] + 2)) best = pi;
    bandVoice[band] = best;
    // under the lowest split staff with nothing to tell the voices apart (the
    // same onsets throughout): the text serves both voices of that staff
    const tie = lowest && best === prior && pis.every(pi => Math.abs(e[pi] - e[prior]) < 0.6);
    if (tie) bandVoice[band] = 'all';
    if (pis.length > 1) lyrNotes.add(`Lyrics under staff ${+band + 1} attached to ${tie ? pis.map(pi => parts[pi].name).join(' and ') + ' (same rhythm, text sung by both)' : parts[best].name + (best === prior ? ' (upper voice)' : ' (its rhythm fits the syllables best)')}.`);
  }
  for (const L of lines) {
    const { v, cands, sp } = L;
    let best = cands.find(c => c.pi === bandVoice[v.band]) || cands[0];
    // a clearly better local fit wins (a passage where the other voice sings the text)
    // (each voice with its own words and rhythm: the line sits under nearly
    // every onset of one voice and misses several of the other's)
    const nSyl = v.syllables.length, margin = Math.max(1.5, 0.15 * nSyl);
    for (const c of cands) {
      if (c === best || c.soft < best.soft + margin) continue;
      if ((best.fit < 0.6 && c.fit >= 0.8) || (c.soft >= 0.88 * nSyl && best.soft < 0.8 * nSyl)) best = c;
    }
    if (best.fit < L.minFit || !wordy(v.syllables)) { lyrNotes.add(`A text line under staff ${v.band + 1} does not follow the notes; not used as lyrics.`); continue; }
    const take = opts.copyLyrics || bandVoice[v.band] === 'all' ? cands.filter(c => c.fit >= L.minFit) : [best];
    if (opts.debug) opts.debug.push({ sys: L.sy.page + ':' + L.sy.index, band: v.band, n: v.number, nsyl: v.syllables.length, fits: cands.map(c => [c.p.name, +c.fit.toFixed(2), c.evs.length, +c.soft.toFixed(2)]), take: take.map(c => c.p.name) });
    for (const c of take) alignSyllables(v, c.evs, sp, L.sy && L.sy.comps);
    v.used = take.map(c => c.p.name).join(', ');
  }
  lyrNotes.forEach(n => warnings.push(n));

  // rhythm repair: every voice must fill its measure. Measure length is the
  // time signature, or for an opening pickup / closing short bar the length
  // most voices agree on. Voices that do not fit are repaired by the cheapest
  // duration edits that make them fit and keep their onsets in step with the
  // voices that already fit; failing that the gap is left as <forward>.
  let mismatch = 0, repaired = 0, restsFound = 0, splitBars = 0;
  // a missed barline leaves two (or more) bars in one segment: when the voices
  // agree on about k bar lengths, cut every voice at the bar boundaries (notes
  // crossing a boundary are split and tied)
  const units = [];
  measures.forEach((m, mi) => {
    const mLen = lenOf(m.segs[0]), uTime = segTime[m.segs[0]];
    const byPart = perPart.map(pm => pm[mi]);
    const sums = [];
    byPart.forEach(sts => sts.forEach(st => { const q = qsum(st.events); if (q > 1e-6) sums.push(Math.round(q * 4) / 4); }));
    const S = sums.length ? mode(sums) : 0;
    const k = Math.round(S / mLen);
    const agree = sums.filter(x => Math.abs(x - S) <= 0.25 * mLen).length;
    // a missed barline lengthens every voice of the system alike: where as
    // many voices fill exactly one bar as run long, the long ones have false
    // notes in them (a tie end read as a half note), not a second bar
    const one = sums.filter(x => Math.abs(x - mLen) <= 0.25 * mLen).length;
    if (k >= 2 && Math.abs(S - k * mLen) <= 0.25 * mLen && ((agree >= Math.max(1, 0.5 * sums.length) && agree > one) || (m.forceSplit && agree >= 1)) && !m.noSplit) {
      splitBars += k - 1;
      const chunks = Array.from({ length: k }, () => byPart.map(sts => sts.map(st => ({ staff: st.staff, events: [] }))));
      byPart.forEach((sts, pi) => sts.forEach((st, si) => {
        let t = 0;
        for (const e of st.events) {
          let left = e.q, cur = e, first = true;
          while (left > 1e-6) {
            const c = Math.min(k - 1, Math.floor((t + 1e-6) / mLen));
            const room = (c + 1) * mLen - t;
            const take = c === k - 1 ? left : Math.min(left, room);
            const piece = take === e.q ? e : { ...cur, q: take, dots: qToType(take) ? qToType(take).dots : 0 };
            if (piece !== e) {
              if (!first) { piece.tieStop = true; piece.lyrics = undefined; }
              if (left - take > 1e-6 && !e.rest) piece.tieStart = true;
            }
            chunks[c][pi][si].events.push(piece);
            t += take; left -= take; first = false;
          }
        }
      }));
      chunks.forEach(ch => units.push({ m, streams: ch, split: true, time: uTime }));
      return;
    }
    units.push({ m, streams: byPart, split: false, time: uTime });
    // a multi-bar rest (or church rests) in a bar with no notes: one bar each
    const barRests = byPart.flatMap(sts => sts.flatMap(st => st.events));
    if (barRests.length && barRests.every(e => e.bar)) {
      const n = Math.max(...barRests.map(e => restBars(e, mLen)));
      // written as one multi-bar rest (<multiple-rest>) over the n bars
      if (n > 1) units[units.length - 1].multi = n;
      for (let k = 1; k < n; k++) units.push({ m, streams: byPart.map(sts => sts.map(st => ({ staff: st.staff, events: [] }))), split: false, time: uTime });
    }
  });
  const partMeasures = parts.map(() => []);
  units.forEach((u, mi) => {
    const m = u.m;
    const streams = [];
    parts.forEach((p, pi) => u.streams[pi].forEach((st, k) => streams.push({ pi, k, staff: st.staff, events: st.events.slice() })));
    const sums = streams.map(st => qsum(st.events));
    const nz = sums.filter(x => x > 1e-6).map(x => Math.round(x * DIV) / DIV);
    const mLen = (u.time.beats * 4) / u.time.type;
    let target = mLen;
    const ms = nz.length ? mode(nz) : 0;
    const agree = nz.filter(x => Math.abs(x - ms) < 1e-6).length;
    const edge = mi === 0 || mi === units.length - 1;
    if (edge && ms > 1e-6 && ms < mLen - 1e-6 && agree >= Math.max(2, 0.5 * nz.length)) target = ms;
    else if (edge && ms > 1e-6 && ms < mLen - 1e-6 && nz.length === 1) target = ms;
    // the printed bar numbers count the first bar as a pickup
    else if (mi === 0 && opts.pickup && nz.length && Math.max(...nz) < mLen - 1e-6) target = Math.max(...nz);
    const implicit = mi === 0 && target < mLen - 1e-6;
    const sp = (m.sy.staves[0] && m.sy.staves[0].st.space) || 16;
    const anchors = [];
    streams.forEach((st, i) => {
      if (Math.abs(sums[i] - target) > 1e-6) return;
      let t = 0;
      for (const e of st.events) { if (!e.rest && e.x != null) anchors.push({ x: e.x, t, i }); t += e.q; }
    });
    streams.forEach((st, i) => {
      let evs = st.events;
      if (sums[i] <= 1e-6 && parts[st.pi].streams[st.k].optional) evs = [];
      else if (sums[i] <= 1e-6) evs = [{ rest: true, q: target, dots: 0, whole: true }];
      else if (Math.abs(sums[i] - target) > 1e-6) {
        const r = repairStream(evs, target, anchors.filter(a => a.i !== i), sp);
        evs = r.events;
        if (r.ok) repaired++; else mismatch++;
      }
      if (evs.some(e => e.glyph && !e.bar)) restsFound++;
      (partMeasures[st.pi][mi] ||= [])[st.k] = { staff: st.staff, events: evs, implicit };
    });
  });
  if (splitBars) warnings.push(`${splitBars} barlines were missing on the page; bars were split by their contents.`);
  if (restsFound) warnings.push(`Rests read from the page in ${restsFound} voice-measures.`);
  if (repaired) warnings.push(`${repaired} voice-measures repaired to fit ${time.beats}/${time.type} (likely misread dots, flags or beams).`);
  if (mismatch) warnings.push(`${mismatch} voice-measures still did not add up to ${time.beats}/${time.type}; gaps left empty, notes past the barline cut.`);
  // stanzas printed after the music (lyrics.js readStanzas -> fr.stanzas) are
  // not set under notes: kept as lyric credits, as engraved scores carry them
  const credits = [];
  const seenFr = new Set();
  for (const pg of pages) {
    if (!pg.fr || seenFr.has(pg.fr)) continue;
    seenFr.add(pg.fr);
    for (const st of pg.fr.stanzas || []) {
      const lines = (st.lines || []).map(l => String(l).trim()).filter(Boolean);
      if (lines.length) credits.push({ page: Math.floor(pg.index || 0) + 1, label: st.label || (st.number ? st.number + '.' : ''), text: lines.join('\n') });
    }
  }
  if (credits.length) warnings.push(`${credits.length} stanza${credits.length > 1 ? 's' : ''} printed below the music kept as text in the file (not set under notes).`);
  const unitSys = units.map(u => u.m.sy);
  // text and marks read on the page (symbols.js pageMarks -> text.js): title
  // and credits, part abbreviations, dynamics, hairpins, tempo and expression text
  let read = { dirs: parts.map(() => units.map(() => [])), head: {}, nDyn: 0, nWedge: 0, nWords: 0 };
  try { read = readMarks(pages, segs, units, parts, partMeasures); } catch (e) { warnings.push(`Text and dynamics not placed (${e.message}).`); }
  if (read.nDyn || read.nWedge || read.nWords || read.nTie || read.nSlur || read.nGrace || read.nFermata) warnings.push(`Read from the page: ${[read.nDyn && `${read.nDyn} dynamic${read.nDyn > 1 ? 's' : ''}`, read.nWedge && `${read.nWedge} hairpin${read.nWedge > 1 ? 's' : ''}`, read.nWords && `${read.nWords} tempo / expression text${read.nWords > 1 ? 's' : ''}`, read.nTie && `${read.nTie} tie${read.nTie > 1 ? 's' : ''}`, read.nSlur && `${read.nSlur} slur${read.nSlur > 1 ? 's' : ''}`, read.nGrace && `${read.nGrace} grace note${read.nGrace > 1 ? 's' : ''}`, read.nFermata && `${read.nFermata} fermata${read.nFermata > 1 ? 's' : ''}`].filter(Boolean).join(', ')}.`);
  const unitTime = units.map(u => u.time), unitMulti = units.map(u => u.multi || 0);
  // barlines, repeats and voltas read on the page (structure.js: sy.bars, sy.voltas) at the ends of
  // each bar: {left, right} with {style, repeat, ending: {n, type}}
  const unitBars = units.map(() => ({}));
  try {
    const spOf = (sy) => (sy.staves[0] && sy.staves[0].st.space) || 16;
    const barAt = (sy, x, tol) => (sy.bars || []).filter(b => Math.abs(b.x - x) <= tol).sort((a, b) => Math.abs(a.x - x) - Math.abs(b.x - x))[0];
    const sysEnd = (si) => si + 1 >= segs.length || segs[si + 1].sy !== segs[si].sy;
    const firstOf = (i) => i === 0 || units[i - 1].m !== units[i].m, lastOf = (i) => i === units.length - 1 || units[i + 1].m !== units[i].m;
    units.forEach((u, i) => {
      if (firstOf(i)) {
        const sg = segs[u.m.segs[0]], b = barAt(sg.sy, sg.xa, spOf(sg.sy));
        if (b && (b.kind === 'repeat-start' || b.kind === 'repeat-both')) unitBars[i].left = { style: 'heavy-light', repeat: 'forward' };
      }
      if (lastOf(i)) {
        const li = u.m.segs[u.m.segs.length - 1], sg = segs[li], b = barAt(sg.sy, sg.xb, (sysEnd(li) ? 1.5 : 1) * spOf(sg.sy));
        if (b && (b.kind === 'repeat-end' || b.kind === 'repeat-both')) unitBars[i].right = { style: 'light-heavy', repeat: 'backward' };
        else if (b && b.kind === 'final') unitBars[i].right = { style: 'light-heavy' };
        else if (b && b.kind === 'double') unitBars[i].right = { style: 'light-light' };
      }
    });
    // voltas: the bars under each bracket; a bracket left open at a system end runs on in the
    // next system's bracket that starts without a hook. Numbered 1, 2, 3 ... along a run of
    // brackets that follow on from each other
    const sysOrder = [...new Set(segs.map(sg => sg.sy))];
    const vs = [];
    sysOrder.forEach((sy, k) => (sy.voltas || []).forEach(v => {
      const sp = spOf(sy);
      const idx = units.map((u, i) => i).filter(i => units[i].m.segs.some(si => segs[si].sy === sy && segs[si].xa >= v.x0 - 1.5 * sp && segs[si].xb <= v.x1 + 1.5 * sp));
      if (!idx.length) return;
      const prev = vs[vs.length - 1];
      if (v.cont && prev && prev.open && prev.k === k - 1) { prev.b = idx[idx.length - 1]; prev.open = v.open; prev.k = k; return; }
      if (v.cont) return;
      vs.push({ a: idx[0], b: idx[idx.length - 1], open: v.open, k, nums: v.nums });
    }));
    // the numbers printed under the bracket (structure.js), else 1, 2, 3 ... along the run
    let n = 0;
    vs.forEach((v, j) => {
      n = j > 0 && vs[j - 1].b === v.a - 1 ? n + 1 : 1;
      if (v.nums && v.nums.length) n = v.nums[v.nums.length - 1];
      const num = v.nums && v.nums.length ? v.nums.join(', ') : String(n);
      (unitBars[v.a].left ||= {}).ending = { n: num, type: 'start' };
      (unitBars[v.b].right ||= {}).ending = { n: num, type: v.open ? 'discontinue' : 'stop' };
    });
    // segno and coda signs: a direction at the start of the bar they stand over (the first part)
    if (read.dirs && read.dirs[0]) sysOrder.forEach(sy => (sy.signs || []).forEach(g => {
      // (a sign over a barline belongs to the bar after it)
      const sp = spOf(sy), si = segs.findIndex(sg => sg.sy === sy && g.x >= sg.xa - 1.5 * sp && g.x < sg.xb - 1.5 * sp);
      const sj = si >= 0 ? si : segs.map((sg, i) => (sg.sy === sy ? i : -1)).filter(i => i >= 0).pop();
      const ui = sj == null ? -1 : units.findIndex(u => u.m.segs.includes(sj));
      if (ui < 0 || !read.dirs[0][ui]) return;
      read.dirs[0][ui].unshift({ t: 0, staffNo: 0, xml: `<direction placement="above"><direction-type><${g.kind}/></direction-type>`, tail: `<sound ${g.kind}="${g.kind}"/>` });
    }));
  } catch (e) { warnings.push(`Repeats and voltas not placed (${e.message}).`); }
  {
    const nRep = unitBars.filter(b => b.right && b.right.repeat).length, nVol = unitBars.filter(b => b.left && b.left.ending).length;
    if (nRep || nVol) warnings.push(`Read from the page: ${[nRep && `${nRep} repeat sign${nRep > 1 ? 's' : ''}`, nVol && `${nVol} volta bracket${nVol > 1 ? 's' : ''}`].filter(Boolean).join(', ')}.`);
  }
  const xml = toMusicXML({ parts, partMeasures, fifths, kAlt, time, unitTime, unitBars, unitMulti, clefs, measures, credits, unitSys, title: read.head.title, head: read.head, dirs: read.dirs });
  const nNotes = partMeasures.map(pm => pm.reduce((a, m) => a + m.reduce((b, s) => b + s.events.filter(e => !e.rest && !e.forward).length, 0), 0));
  const ranges = partMeasures.map(pm => {
    let lo = null, hi = null;
    pm.forEach(m => m.forEach(st => st.events.forEach(e => (e.heads || []).forEach(h => {
      if (!h.pitch) return;
      if (!lo || h.pitch.d < lo.d) lo = h.pitch;
      if (!hi || h.pitch.d > hi.d) hi = h.pitch;
    }))));
    return lo ? `${lo.step}${lo.octave}\u2013${hi.step}${hi.octave}` : '-';
  });
  // where each written measure stands on its page (overlay and repair notes):
  // {n: measure number as written, page, sys, xa, xb, y0, y1} per segment, in the
  // page frame of that page entry (a spread's half: page i + 0.5)
  const first0 = partMeasures[0] && partMeasures[0][0] && partMeasures[0][0].every(s => s.implicit);
  const measureMap = [];
  units.forEach((u, mi) => {
    const n = mi === 0 && first0 ? 0 : mi + (first0 ? 0 : 1);
    let ex = null;
    if (u.split) {
      const xs = u.streams.flat().flatMap(st => st.events).filter(e => e.x != null).map(e => e.x);
      if (xs.length) ex = [Math.min(...xs), Math.max(...xs)];
    }
    for (const si of u.m.segs) {
      const sg = segs[si], sts = sg.sy.staves;
      if (!sts.length) continue;
      const xa = ex ? Math.max(sg.xa, ex[0] - 0.8 * sts[0].st.space) : sg.xa, xb = ex ? Math.min(sg.xb, ex[1] + 0.8 * sts[0].st.space) : sg.xb;
      measureMap.push({ n, page: sg.sy.page, sys: sg.sy.index, xa: Math.round(xa), xb: Math.round(xb),
        y0: Math.round(sts[0].st.yAt(0, sg.xa)), y1: Math.round(sts[sts.length - 1].st.yAt(4, sg.xa)) });
    }
  });
  let barCheck = null;
  try { barCheck = checkBarNumbers(pages, measureMap); } catch (e) { barCheck = null; }
  // the printed bar numbers disagree with the bars read: read again with the
  // bar counts they give (barTargets) and keep that reading when it agrees
  // with more of them
  // Off unless opts.barFix: on the benchmark it set the bar count right on 9 more
  // systems but rhythm repair then did worse (duration -0.01 to -0.06 on 6 items)
  if (opts.barFix && barCheck && barCheck.notes.length && !opts.barTargets) {
    const hint = barHints(pages, measureMap, barCheck, partMeasures);
    if (hint) {
      let again = null;
      try { again = buildScore(pages, lyricsBySystem, { ...opts, barTargets: hint.targets, pickup: hint.pickup }); } catch (e) { again = null; }
      // and the bars it makes fill as well as before (no more voice-measures
      // that needed repair or still do not add up)
      if (again && again.barCheck && again.barCheck.agree > barCheck.agree && again.rhythm.repaired + again.rhythm.mismatch <= repaired + mismatch) {
        again.warnings.unshift(`Bar count corrected from the printed bar numbers (${barCheck.agree} of ${barCheck.printed} agreed, now ${again.barCheck.agree}).`);
        return again;
      }
    }
  }
  if (barCheck) barCheck.notes.forEach(n => warnings.push(n));
  // UI compares clefs with 'F'; 'G8' stays a treble clef there
  return { parts, layout, fifths, time, timeRead, clefs, ranges, measures: units.length, nNotes, credits, title: read.head.title || null, composer: read.head.composer || null, warnings: warnings.concat(layout.notes), xml, measureMap, barCheck, rhythm: { repaired, mismatch } };
}

// Horizontal extent of a syllable: lyrics.js may report x0/x1; otherwise it is
// estimated from the letter count (about 1.1 staff spaces per letter).
function sylBox(s, sp) {
  if (s.x0 != null && s.x1 != null && s.x1 > s.x0) return [s.x0, s.x1];
  const w = Math.max(1, String(s.text || '').length) * 1.1 * sp;
  return [s.x - w / 2, s.x + w / 2];
}

// Distance from a syllable to a notehead centre at x. A syllable is printed
// centred under its note, except one that starts a melisma (a word held over
// several notes, drawn with an extender line), which is left-aligned with the
// notehead; so a long syllable may also sit with its left edge at the head.
// Long tokens (7+ letters) are more often two syllables OCR read as one word
// ("cherchons") and keep the centred reading only.
function sylDist(s, x, sp) {
  const c = Math.abs(x - s.x);
  if (String(s.text || '').replace(/[^\p{L}]/gu, '').length > 6) return c;
  const x0 = sylBox(s, sp)[0];
  // an extender line printed after it: certainly a melisma start
  return Math.min(c, Math.abs(x - (x0 + 0.55 * sp)) + (s.extend || s.ext ? 0 : 0.15 * sp));
}

// share of syllables that sit under an onset of the stream
function lyricFit(syl, evs, sp) {
  if (!syl.length || !evs.length) return 0;
  let hit = 0;
  for (const s of syl) {
    let d = 1e9;
    for (const e of evs) { const t = sylDist(s, e.x, sp); if (t < d) d = t; }
    if (d <= 1.2 * sp) hit++;
  }
  return hit / syl.length;
}

// graded version of lyricFit: 1 for a syllable right under an onset, falling
// to 0 at `tol` staff spaces away (separates two voices of one staff that
// share most onsets)
function softFit(syl, evs, sp, tol = 0.8) {
  let s = 0;
  for (const y of syl) {
    let d = 1e9;
    for (const e of evs) if (!e.rest && e.x != null) d = Math.min(d, sylDist(y, e.x, sp));
    s += Math.max(0, 1 - d / (tol * sp));
  }
  return s;
}

// OCR junk (dynamics, stray marks read as letters) rather than words
function wordy(syl) {
  if (syl.length < 3) return false;
  const good = syl.filter(s => /[a-zà-ɏ]{2}/.test(s.text) || /^[A-ZÀ-Þ][a-zà-ɏ]/.test(s.text)).length;
  return good >= 0.4 * syl.length;
}

// Monotonic alignment of the syllables of one verse line to the onsets of one
// voice (both left to right): each syllable takes one onset, onsets without a
// syllable are melisma continuations, syllables far from any onset are dropped.
// Tied continuation notes never take a syllable. A word-final syllable held
// over the following notes of its voice gets an extender (<extend/> start on
// its note, stop on the last note of the melisma); hyphenated syllables do not
// (their hyphen spans the melisma).
// An elision slur under a syllable ("a‿in": two syllables sung on one note):
// a small thin arc in the lower part of the text row, inside the syllable's
// box. OCR reads such a syllable as one word ("ain"); it is cut at the arc.
// [left, right] or null
function elisionOf(s, verse, comps, sp) {
  // joined in lyrics.js (an arc across the gap between two words)
  if (s.text && /.‿./.test(s.text)) { const k = s.text.indexOf('‿'); return [s.text.slice(0, k), s.text.slice(k + 1)]; }
  if (!comps || s.x0 == null || s.x1 == null || verse.y == null || verse.y1 == null || !s.text || s.text.length < 2) return null;
  const w = s.x1 - s.x0, rowH = verse.y1 - verse.y;
  const arc = comps.find(c => {
    const cw = c.x1 - c.x0 + 1, ch = c.y1 - c.y0 + 1, cx = (c.x0 + c.x1) / 2;
    // under the baseline, wider than tall but not a flat hyphen
    return cw >= 0.6 * sp && cw <= 3 * sp && ch <= 0.6 * sp && ch >= 0.2 * sp && cw >= 2.5 * ch && cx > s.x0 + 0.12 * w && cx < s.x1 - 0.12 * w &&
      c.y0 >= verse.y + 0.75 * rowH && c.y1 <= verse.y1 + 1.0 * sp;
  });
  if (!arc) return null;
  const t = s.text.replace(/[‿_]/g, ''), cx = (arc.x0 + arc.x1) / 2;
  const k = Math.max(1, Math.min(t.length - 1, Math.round(t.length * (cx - s.x0) / Math.max(1, w))));
  return [t.slice(0, k), t.slice(k)];
}

function alignSyllables(verse, evs, sp, comps) {
  const syl = verse.syllables, n = syl.length, m = evs.length;
  if (!n || !m) return;
  const SKIP_EV = 0.15, DROP_SYL = 2.2;
  const cost = (i, j) => (evs[j].tieStop ? Infinity : Math.min(3, sylDist(syl[i], evs[j].x, sp) / sp));
  // D[i][j]: best cost using syllables < i and onsets < j
  const W = m + 1;
  const D = new Float64Array((n + 1) * W).fill(Infinity), T = new Uint8Array((n + 1) * W);
  D[0] = 0;
  for (let i = 0; i <= n; i++) for (let j = 0; j <= m; j++) {
    const here = D[i * W + j];
    if (here === Infinity) continue;
    if (i < n && j < m) { const v = here + cost(i, j); if (v < D[(i + 1) * W + j + 1]) { D[(i + 1) * W + j + 1] = v; T[(i + 1) * W + j + 1] = 1; } }
    if (j < m) { const v = here + SKIP_EV; if (v < D[i * W + j + 1]) { D[i * W + j + 1] = v; T[i * W + j + 1] = 2; } }
    if (i < n) { const v = here + DROP_SYL; if (v < D[(i + 1) * W + j]) { D[(i + 1) * W + j] = v; T[(i + 1) * W + j] = 3; } }
  }
  let i = n, j = m;
  const pairs = [];
  while (i > 0 || j > 0) {
    const t = T[i * W + j];
    if (t === 1) { pairs.push([i - 1, j - 1]); i--; j--; }
    else if (t === 2) j--;
    else i--;
  }
  pairs.reverse();
  const num = verse.number;
  const placed = [];
  for (const [a, b] of pairs) {
    const ev = evs[b], s = syl[a];
    ev.lyrics ||= {};
    if (ev.lyrics[num]) continue;
    ev.lyrics[num] = { text: s.text, syllabic: s.syllabic };
    const el = elisionOf(s, verse, comps, sp);
    if (el) ev.lyrics[num].elision = el;
    placed.push([a, b]);
  }
  // melismas between placed syllables
  placed.forEach(([a, b], k) => {
    const s = syl[a];
    if (s.syllabic !== 'single' && s.syllabic !== 'end') return;
    const next = k + 1 < placed.length ? placed[k + 1][1] : null;
    const ext = s.ext || s.extend;
    // after the last syllable of the line only with an extender seen in print;
    // a printed extender also says where the melisma ends
    let last = next != null ? next - 1 : (ext ? m - 1 : b);
    if (ext && s.extendTo != null) while (last > b && evs[last].x > s.extendTo + 1.0 * sp) last--;
    if (last <= b || (last - b > 6 && !ext)) return;
    for (let t = b + 1; t <= last; t++) if (evs[t].lyrics && evs[t].lyrics[num]) return;
    evs[b].lyrics[num].extend = true;
    (evs[last].lyrExt ||= {})[num] = true;
  });
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// no staves found: still a schema-valid score (the schema asks for at least
// one part with one measure), so the file opens and the warnings explain it
function emptyXML() {
  return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n' +
    '<score-partwise version="4.0">\n  <work><work-title>Scanned score (no staves found)</work-title></work>\n' +
    '  <part-list><score-part id="P1"><part-name>Music</part-name></score-part></part-list>\n' +
    '  <part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes></measure></part>\n</score-partwise>\n';
}

function clefXML(c, n) {
  const num = n ? ` number="${n}"` : '';
  if (c === 'F') return `<clef${num}><sign>F</sign><line>4</line></clef>`;
  if (c === 'G8') return `<clef${num}><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>`;
  if (c === 'G8va') return `<clef${num}><sign>G</sign><line>2</line><clef-octave-change>1</clef-octave-change></clef>`;
  if (/^C[1-5]$/.test(c)) return `<clef${num}><sign>C</sign><line>${c[1]}</line></clef>`;
  return `<clef${num}><sign>G</sign><line>2</line></clef>`;
}

// Printed bar numbers (text.js role 'measure', read from their digit shapes
// or by OCR) against the measures read: the written number of each system's
// first measure (measureMap). A misread digit disagrees on one system only; a
// missed or extra barline shifts every later system by the same amount, so a
// change of the offset that the next system keeps is reported.
// {systems: [{page, sys, printed, read}], printed, agree, notes}
function checkBarNumbers(pages, measureMap) {
  const out = { systems: [], printed: 0, agree: 0, notes: [] };
  const seenFr = new Set();
  for (const pg of pages) {
    if (!pg.fr || !pg.asm || seenFr.has(pg.fr)) continue;
    seenFr.add(pg.fr);
    const m = pg.fr._marks && pg.fr._marks.asm === pg.asm ? pg.fr._marks.marks : pageMarks(pg.fr, pg.asm);
    if (!m) continue;
    for (const t of m.text) {
      if (t.role !== 'measure' || !/^\d{1,4}$/.test(t.text) || t.sys < 0) continue;
      const sy = pg.asm.systems[t.sys];
      if (!sy) continue;
      const ns = measureMap.filter(e => e.page === sy.page && e.sys === sy.index).map(e => e.n);
      if (!ns.length) continue;
      out.systems.push({ page: sy.page, sys: sy.index, printed: +t.text, read: Math.min(...ns) });
    }
  }
  out.systems.sort((a, b) => a.page - b.page || a.sys - b.sys);
  out.printed = out.systems.length;
  out.agree = out.systems.filter(s => s.printed === s.read).length;
  let prev = 0;
  out.systems.forEach((s, i) => {
    const d = s.printed - s.read, next = out.systems[i + 1];
    // a spike between two systems that agree with each other is a misread digit
    if (d !== prev && !(next && next.printed - next.read === prev)) {
      const at = `system ${s.sys + 1}${pages.length > 1 ? ` of page ${Math.floor(s.page) + 1}` : ''}`;
      out.notes.push(`Bar numbers say ${at} starts at bar ${s.printed}; the reading has it start at bar ${s.read} (${Math.abs(d - prev)} barline${Math.abs(d - prev) > 1 ? 's' : ''} ${d > prev ? 'missed' : 'too many'} before it).`);
      prev = d;
    }
  });
  return out;
}

// Bar counts per system from the printed bar numbers, where they change the
// offset (checkBarNumbers) and the system to blame is known: the numbered
// system before the change, when no unnumbered system lies between. A change
// at the first numbered system with one bar too many read, and a first bar
// not read as a pickup, makes the first bar a pickup.
// {targets: {'page:sys': bars}, pickup} or null
function barHints(pages, measureMap, bc, partMeasures) {
  const order = [];
  const seenFr = new Set();
  for (const pg of pages) {
    if (!pg.asm || seenFr.has(pg.fr)) continue;
    seenFr.add(pg.fr);
    for (const sy of pg.asm.systems) order.push(sy.page + ':' + sy.index);
  }
  const pos = (s) => order.indexOf(s.page + ':' + s.sys);
  const count = (key) => new Set(measureMap.filter(e => e.page + ':' + e.sys === key).map(e => e.n)).size;
  const targets = {};
  let pickup = false, prev = 0, any = false;
  bc.systems.forEach((s, i) => {
    const d = s.printed - s.read, next = bc.systems[i + 1];
    if (d === prev || (next && next.printed - next.read === prev)) return;
    const a = bc.systems[i - 1];
    if (!a) {
      // the first numbered system: the bars before it are the first system's
      const firstImplicit = partMeasures[0] && partMeasures[0][0] && partMeasures[0][0].every(st => st.implicit);
      if (d === -1 && !firstImplicit) { pickup = true; any = true; }
      else if (pos(s) === 1 && Math.abs(d) === 1) { targets[order[0]] = count(order[0]) + d; if (targets[order[0]] >= 1) any = true; else delete targets[order[0]]; }
    } else if (pos(s) - pos(a) === 1 && Math.abs(d - prev) === 1) {
      const key = order[pos(a)];
      targets[key] = count(key) + (d - prev);
      if (targets[key] >= 1) any = true; else delete targets[key];
    }
    prev = d;
  });
  return any ? { targets, pickup } : null;
}

// ------------------------------------------------------------ text and marks
const DYN_XML = new Set(['p', 'pp', 'ppp', 'pppp', 'f', 'ff', 'fff', 'ffff', 'mp', 'mf', 'sf', 'sfp', 'sfpp', 'fp', 'rf', 'rfz', 'sfz', 'sffz', 'fz', 'n', 'pf', 'sfzp']);
// Marks read on each page (symbols.js pageMarks) placed in the score:
//  head: title, subtitle, composer, lyricist, arranger, rights (first page);
//  part abbreviations (p.abbrev) from the names left of later systems;
//  dirs[pi][mi]: [{t, staffNo, placement, xml}] per part and written measure,
//  t the onset in quarters of the note the mark stands at (nearest by x).
// a part abbreviation as read ("Pno.", "S.", "Vc."): short, letters, and
// starting as the part's name does; else null
function abbrevOf(text, name) {
  const ab = String(text || '').replace(/[^\p{L}\p{N}. ]/gu, '').replace(/\s+/g, ' ').trim();
  if (!ab || ab.length > 10 || !/^\p{L}/u.test(ab) || /\d/.test(ab)) return null;
  // its letters in order within the name ("Pno." in Piano, "Vc." in Violoncello)
  const a = ab.toLowerCase().replace(/[^\p{L}]/gu, ''), n = String(name || '').toLowerCase();
  if (!a || a[0] !== n[0]) return null;
  let i = 0;
  for (const ch of n) if (ch === a[i]) i++;
  return i === a.length ? ab : null;
}
// tempo / expression text worth writing: known terms, or confident words
const TERMS = /^(tempo|a tempo|allegr|andant|adagi|larg|lent|prest|vivac|modera|grave|maestos|marcia|rubato|cresc|decresc|dim|rit|rall|accel|poco|più|piu|meno|molto|sempre|subito|dolce|espr|legato|leggiero|stacc|sost|smorz|morendo|cantabile|con |senza|simile|pizz|arco|fine|d\.\s?c|d\.\s?s|da capo|dal segno|to coda|not |slow|fast|lively|moderately|brightly|gently|with |langsam|schnell|mässig|ruhig|bewegt|lebhaft|sehr |nicht |innig|zart)/i;
// the <sound> of a jump word: D.C. / D.S. (al Fine / al Coda), Fine, To Coda
function jumpSound(text) {
  const w = String(text || '').trim();
  if (/^d\.?\s*c\.?(\s|$|al)/i.test(w) || /da capo/i.test(w)) return '<sound dacapo="yes"/>';
  if (/^d\.?\s*s\.?(\s|$|al)/i.test(w) || /dal segno/i.test(w)) return '<sound dalsegno="segno"/>';
  if (/^fine\.?$/i.test(w)) return '<sound fine="yes"/>';
  if (/^to\s+coda/i.test(w)) return '<sound tocoda="coda"/>';
  return '';
}

function wordsOk(t) {
  const s = t.text.trim();
  if (TERMS.test(s)) return true;
  const ws = s.split(/\s+/);
  return (t.conf || 0) >= 80 && ws.length >= 2 && ws.every(w => /^\p{L}{2,}[.,]?$/u.test(w));
}

function readMarks(pages, segs, units, parts, partMeasures) {
  const dirs = parts.map(() => units.map(() => []));
  const head = {};
  let nDyn = 0, nWedge = 0, nWords = 0;
  const unitsOfSeg = new Map();
  units.forEach((u, mi) => u.m.segs.forEach(si => { if (!unitsOfSeg.has(si)) unitsOfSeg.set(si, []); unitsOfSeg.get(si).push(mi); }));
  // parts reading staff k of a system, with the staff number inside the part
  const partsOn = (k) => parts.map((p, pi) => ({ pi, n: p.src.findIndex(s => s.staff === k) })).filter(a => a.n >= 0).map(a => ({ pi: a.pi, staffNo: a.n + 1, multi: parts[a.pi].src.length > 1 }));
  // (unit, onset) of the note nearest x on staff k of a page system
  const locate = (fr, sysIndex, k, x, pi) => {
    const ss = segs.map((sg, si) => ({ sg, si })).filter(({ sg }) => sg.sy.fr === fr && sg.sy.index === sysIndex);
    if (!ss.length) return null;
    let cand = ss.filter(({ sg }) => x >= sg.xa && x < sg.xb);
    if (!cand.length) cand = [ss.reduce((a, b) => (Math.min(Math.abs(x - a.sg.xa), Math.abs(x - a.sg.xb)) <= Math.min(Math.abs(x - b.sg.xa), Math.abs(x - b.sg.xb)) ? a : b))];
    let best = null;
    for (const { si } of cand) for (const mi of unitsOfSeg.get(si) || []) {
      const streams = (partMeasures[pi] && partMeasures[pi][mi]) || [];
      for (const st of streams) {
        if (!st || st.staff !== k) continue;
        let t = 0;
        for (const e of st.events) {
          if (e.x != null && !e.forward) { const d = Math.abs(e.x - x); if (!best || d < best.d) best = { mi, t, d }; }
          t += e.q;
        }
      }
      if (!best) best = { mi, t: 0, d: Infinity };
    }
    return best;
  };
  const seenFr = new Set();
  for (const pg of pages) {
    const fr = pg.fr;
    if (!fr || seenFr.has(fr) || !pg.asm) continue;
    seenFr.add(fr);
    const marks = pageMarks(fr, pg.asm);
    if (!marks) continue;
    const sysIdx = (k) => (pg.asm.systems[k] ? pg.asm.systems[k].index : -1);
    const place = (m, x, entry, tail) => {
      if (m.sys < 0 || m.k < 0) return;
      const st = pg.asm.systems[m.sys] && pg.asm.systems[m.sys].staves[m.k];
      const placement = st && (m.box[1] + m.box[3]) / 2 < st.st.yAt(0, x) ? 'above' : 'below';
      for (const { pi, staffNo, multi } of partsOn(m.k)) {
        const at = locate(fr, sysIdx(m.sys), m.k, x, pi);
        if (!at) continue;
        const list = dirs[pi][at.mi];
        const xml = entry(placement);
        if (list.some(d => d.xml === xml && Math.abs(d.t - at.t) < 1e-6)) continue;
        list.push({ t: at.t, staffNo: multi ? staffNo : 0, xml, tail: tail || '' });
      }
      return true;
    };
    for (const d of marks.dyns) {
      const tag = DYN_XML.has(d.value) ? `<${d.value}/>` : `<other-dynamics>${esc(d.value)}</other-dynamics>`;
      // explicit loudness for other players: <sound dynamics> (% of forte, MuseScore's convention, velocity x 100 / 90; OMR_NO_MIDI=1: left out)
      const sd = process.env.OMR_NO_MIDI ? null : soundDynamics(d.value);
      if (place(d, d.x, (pl) => `<direction placement="${pl}"><direction-type><dynamics>${tag}</dynamics></direction-type>`, sd != null ? `<sound dynamics="${sd}"/>` : '')) nDyn++;
    }
    for (const w of marks.wedges) {
      const ok = place(w, w.box[0] + 0.1 * (w.box[2] - w.box[0]), (pl) => `<direction placement="${pl}"><direction-type><wedge type="${w.type}" number="1"/></direction-type>`);
      if (ok) { place(w, w.box[2], (pl) => `<direction placement="${pl}"><direction-type><wedge type="stop" number="1"/></direction-type>`); nWedge++; }
    }
    for (const t of marks.text) {
      if (!t.text && !t.metro) continue;
      if (t.role === 'tempo' && t.metro && t.sys >= 0) {
        // a metronome mark, with its tempo word: words, metronome and the
        // tempo in quarter notes per minute (<sound tempo>) for players
        const mt = t.metro, bq = { quarter: 1, half: 2, eighth: 0.5, '16th': 0.25 }[mt.unit] || 1;
        const word = t.text && (t.text.match(/\p{L}/gu) || []).length >= 3 ? `<direction-type><words font-weight="bold">${esc(t.text)}</words></direction-type>` : '';
        const metro = mt.bpm ? `<direction-type><metronome><beat-unit>${mt.unit}</beat-unit>${mt.dotted ? '<beat-unit-dot/>' : ''}<per-minute>${mt.bpm}</per-minute></metronome></direction-type>` : '';
        const q = mt.bpm ? mt.bpm * bq * (mt.dotted ? 1.5 : 1) : tempoFromWords(t.text || '');
        if (!word && !metro) continue;
        if (place(t, t.box[0], () => `<direction placement="above">${word}${metro}`, q ? `<sound tempo="${Math.round(q * 100) / 100}"/>` : '')) nWords++;
        continue;
      }
      if ((t.role === 'tempo' || t.role === 'expression') && t.sys >= 0) {
        if (!wordsOk(t)) continue;
        const bold = t.role === 'tempo' ? ' font-weight="bold"' : '';
        // a tempo word alone: its usual tempo for players (playback.js table)
        const q = t.role === 'tempo' ? tempoFromWords(t.text) : 0;
        // jumps (D.C., D.S., Fine, To Coda) also as <sound> for players
        const jump = jumpSound(t.text);
        if (place(t, t.box[0], (pl) => `<direction placement="${pl}"><direction-type><words${bold}>${esc(t.text)}</words></direction-type>`, q ? `<sound tempo="${q}"/>` : jump)) nWords++;
      } else if ((pg.index || 0) < 1 && ['title', 'subtitle', 'composer', 'lyricist', 'arranger', 'copyright'].includes(t.role)) {
        // a credit is words: OCR of a smudge or a stray glyph is not
        const key = t.role === 'copyright' ? 'rights' : t.role;
        if (!head[key] && (t.text.match(/\p{L}/gu) || []).length >= 3 && (t.conf || 0) >= 50) head[key] = t.text;
      } else if (t.role === 'abbrev' && t.sys > 0 && t.k >= 0) {
        // the abbreviation of the part(s) whose first staff it faces
        for (const { pi, staffNo } of partsOn(t.k)) if (staffNo === 1 && !parts[pi].abbrev) parts[pi].abbrev = abbrevOf(t.text, parts[pi].name);
      }
    }
  }
  // slurs and ties (text.js curves) whose two ends sit at note heads: a curve
  // joining two heads of one pitch on one staff is a tie, else a slur. Marked
  // on the heads (h.tieOn / h.tieOff, h.slurOn / h.slurOff counts) for toMusicXML.
  let nTie = 0, nSlur = 0;
  {
    const written = new Set();
    for (const pm of partMeasures) for (const m of pm) for (const st of m || []) if (st) for (const e of st.events) for (const h of e.heads || []) written.add(h);
    const seen = new Set();
    for (const pg of pages) {
      const fr = pg.fr, m = fr && fr._marks && fr._marks.marks;
      if (!m || seen.has(fr)) continue;
      seen.add(fr);
      const heads = (fr.heads || []).filter(h => written.has(h));
      const near = (x, y, side) => {
        let best = null, bd = Infinity;
        for (const h of heads) {
          const sp = h.sp || fr.ss, dx = side < 0 ? x - h.x : h.x - x;
          if (dx < -0.6 * sp || dx > 1.8 * sp || Math.abs(h.y - y) > 1.6 * sp) continue;
          const d = Math.abs(dx - 0.5 * sp) + Math.abs(h.y - y);
          if (d < bd) { bd = d; best = h; }
        }
        return best;
      };
      for (const c of m.slurs) {
        if (!c.ends) continue;
        const a = near(c.ends[0][0], c.ends[0][1], -1), b = near(c.ends[1][0], c.ends[1][1], 1);
        // half a tie or slur at a system break: one end at a head, the other
        // at the end of the staff (or its start, after clef and key)
        if ((!a) !== (!b)) {
          const h = a || b, st = fr.staves[h.staff];
          if (!st) continue;
          const sp = h.sp || fr.ss, x = a ? c.ends[1][0] : c.ends[0][0];
          const atEdge = a ? x >= st.right - 1.5 * sp : !heads.some(o => o.staff === h.staff && o.x < h.x - 0.5 * sp) && x < h.x - 0.5 * sp;
          if (!atEdge) continue;
          const tieish = c.box[2] - c.box[0] <= 4 * sp && Math.abs(c.ends[0][1] - c.ends[1][1]) <= 0.6 * sp;
          if (tieish) { if (a) a.tieOn = true; else b.tieOff = true; nTie++; }
          else { if (a) a.slurOn = (a.slurOn || 0) + 1; else b.slurOff = (b.slurOff || 0) + 1; nSlur++; }
          continue;
        }
        if (!a || !b || a === b || b.x <= a.x) continue;
        if (a.staff === b.staff && a.p === b.p) { a.tieOn = true; b.tieOff = true; nTie++; }
        else { a.slurOn = (a.slurOn || 0) + 1; b.slurOff = (b.slurOff || 0) + 1; nSlur++; }
      }
    }
  }
  // ties the curve finder missed (a tie broken by staff-line removal, or
  // joined to its heads): two neighbouring heads of one pitch on one staff
  // with a thin arc of ink between them, above or below
  {
    const written = new Set();
    for (const pm of partMeasures) for (const m of pm) for (const st of m || []) if (st) for (const e of st.events) for (const h of e.heads || []) written.add(h);
    const seen = new Set();
    for (const pg of pages) {
      const fr = pg.fr, R = fr && fr.R;
      if (!R || seen.has(fr)) continue;
      seen.add(fr);
      const W = R.width, H = R.height;
      const byStaff = new Map();
      for (const h of fr.heads || []) { if (!byStaff.has(h.staff)) byStaff.set(h.staff, []); byStaff.get(h.staff).push(h); }
      const arc = (a, b, side) => {
        const sp = a.sp || fr.ss, x0 = Math.round(a.x + 0.7 * sp), x1 = Math.round(b.x - 0.7 * sp);
        if (x1 - x0 < 3) return false;
        const ys = [];
        let hit = 0;
        for (let x = x0; x <= x1; x++) {
          let best = null;
          const ya = Math.round(side < 0 ? a.y - 1.8 * sp : a.y + 0.3 * sp), yb = Math.round(side < 0 ? a.y - 0.3 * sp : a.y + 1.8 * sp);
          for (let y = Math.max(0, ya); y <= Math.min(H - 1, yb);) {
            if (!R.data[y * W + x]) { y++; continue; }
            let e = y; while (e <= yb && e < H && R.data[e * W + x]) e++;
            const run = e - y, mid = (y + e - 1) / 2;
            if (run <= 0.45 * sp && (!best || Math.abs(mid - a.y) < Math.abs(best - a.y))) best = mid;
            y = e;
          }
          if (best != null) { hit++; ys.push([x, best]); }
        }
        if (hit < 0.6 * (x1 - x0 + 1) || ys.length < 3) return false;
        for (let i = 1; i < ys.length; i++) if (ys[i][0] - ys[i - 1][0] <= 2 && Math.abs(ys[i][1] - ys[i - 1][1]) > 0.35 * sp) return false;
        // it bows away from the heads: the middle farther from them than the ends
        const dist = (p) => Math.abs(p[1] - a.y);
        const m = ys[ys.length >> 1];
        return dist(m) >= Math.max(dist(ys[0]), dist(ys[ys.length - 1])) - 0.05 * sp;
      };
      for (const hs of byStaff.values()) {
        const w = hs.filter(h => written.has(h)).sort((p, q) => p.x - q.x);
        for (let i = 0; i < w.length; i++) {
          const a = w[i];
          if (a.tieOn) continue;
          const sp = a.sp || fr.ss;
          // the next head on this staff to the right (other heads of the same chord skipped)
          const nextX = w.find(h => h.x > a.x + 0.8 * sp);
          if (!nextX) continue;
          const b = w.find(h => h.x >= nextX.x - 0.3 * sp && h.x <= nextX.x + 0.3 * sp && h.p === a.p);
          if (!b || b.tieOff || b.x - a.x > 40 * sp) continue;
          if (arc(a, b, -1) || arc(a, b, 1)) { a.tieOn = true; b.tieOff = true; nTie++; }
        }
      }
    }
  }
  // grace notes (text.js): each small head goes before the first note after
  // it on its staff, in each part reading that staff (e.graces)
  let nGrace = 0;
  {
    const seen = new Set();
    for (const pg of pages) {
      const fr = pg.fr, m = fr && fr._marks && fr._marks.marks;
      if (!m || seen.has(fr) || !m.grace) continue;
      seen.add(fr);
      for (const g of m.grace) {
        const sy = pg.asm.systems[g.sys], s = sy && sy.staves[g.k];
        if (!s) continue;
        const st = s.st, sp = st.space || fr.ss;
        for (const { pi } of partsOn(g.k)) {
          const at = locate(fr, sy.index, g.k, Math.max(...g.heads.map(h => h.x)) + 2.5 * sp, pi);
          if (!at) continue;
          // the first written note right of the grace notes on that staff
          let target = null;
          for (const sm of partMeasures[pi][at.mi] || []) if (sm && sm.staff === g.k) for (const e of sm.events) {
            if (e.rest || e.forward || e.x == null || e.x <= g.box[2] - 0.2 * sp || e.x > g.box[2] + 5 * sp) continue;
            if (!target || e.x < target.x) target = e;
          }
          if (!target) continue;
          const heads = g.heads.slice().sort((a, b) => a.x - b.x);
          target.graces = (target.graces || []).concat(heads.map(h => ({ p: Math.round((st.yAt(2, h.x) - h.y) / (sp / 2)), slash: g.slash && heads.length === 1, n: heads.length })));
          nGrace += heads.length;
        }
      }
    }
  }
  // fermatas (text.js): on the note or rest under (or, inverted, over) them,
  // nearest by x on the staff they stand by (e.fermata)
  let nFermata = 0;
  {
    const seen = new Set();
    for (const pg of pages) {
      const fr = pg.fr, m = fr && fr._marks && fr._marks.marks;
      if (!m || seen.has(fr) || !m.fermatas) continue;
      seen.add(fr);
      for (const f of m.fermatas) {
        if (f.sys == null || f.sys < 0) continue;
        const sy = pg.asm.systems[f.sys], s = sy && sy.staves[f.k];
        if (!s) continue;
        const cx = (f.box[0] + f.box[2]) / 2, sp = s.st.space || fr.ss;
        const inverted = (f.box[1] + f.box[3]) / 2 > s.st.yAt(4, cx);
        for (const { pi } of partsOn(f.k)) {
          const at = locate(fr, sy.index, f.k, cx, pi);
          if (!at) continue;
          let target = null, bd = Infinity;
          for (const sm of partMeasures[pi][at.mi] || []) if (sm && sm.staff === f.k) for (const e of sm.events) {
            if (e.forward || e.x == null) continue;
            const d = Math.abs(e.x - cx);
            if (d < bd && d <= 1.5 * sp) { bd = d; target = e; }
          }
          if (target && !target.fermata) { target.fermata = inverted ? 'inverted' : 'upright'; nFermata++; }
        }
      }
    }
  }
  // a keyboard part's name is printed between its staves: the abbreviation
  // stands on the staff nearest to it, which may be the lower one
  for (const p of parts) if (!p.abbrev && p.src.length > 1) {
    for (const pg of pages) {
      const m = pg.fr && pg.fr._marks && pg.fr._marks.marks;
      const t = m && m.text.find(t => t.role === 'abbrev' && t.text && p.src.some(s => s.staff === t.k));
      if (t && abbrevOf(t.text, p.name)) { p.abbrev = abbrevOf(t.text, p.name); break; }
    }
  }
  for (const pm of dirs) for (const l of pm) l.sort((a, b) => a.t - b.t);
  return { dirs, head, nDyn, nWedge, nWords, nTie, nSlur, nGrace, nFermata };
}

// a <barline> at one end of a bar (buildScore: unitBars)
function barlineXML(loc, b) {
  if (!b || (!b.style && !b.repeat && !b.ending)) return '';
  return `      <barline location="${loc}">${b.style ? `<bar-style>${b.style}</bar-style>` : ''}${b.ending ? `<ending number="${b.ending.n}" type="${b.ending.type}"/>` : ''}${b.repeat ? `<repeat direction="${b.repeat}"/>` : ''}</barline>`;
}

function toMusicXML({ parts, partMeasures, fifths, kAlt, time, unitTime, unitBars, unitMulti, clefs, title, credits, unitSys, head, dirs }) {
  // each system's own clef where it was read (a staff can change clef from
  // one system to the next), else the clef most systems show. A clef read on
  // one system only is more often a misread (or a header clef cancelled at
  // once by a change the reader does not see) than a real change, so a
  // system's clef counts only when that staff shows it on two systems or more.
  const seenClef = {};
  for (const sy of new Set(unitSys || [])) if (sy) sy.staves.forEach((st, k) => {
    if (!st.hdr.clefGuessed && st.hdr.clef) { const key = k + ':' + st.hdr.clef; seenClef[key] = (seenClef[key] || 0) + 1; }
  });
  // the same for keys: a system whose staves all read one key signature
  // uses it (a key change at a system break) when that key is read so on two
  // systems or more; otherwise the piece's key. Faded or broken signatures
  // lose accidentals, so a key with fewer accidentals than the piece's (same
  // side, or none) counts only on a clear majority of the systems
  const sysKeyOf = new Map(), seenKey = {};
  const allSys = new Set((unitSys || []).filter(Boolean));
  for (const sy of allSys) if (sy.staves.length) {
    const ks = sy.staves.map(st => st.hdr.fifths | 0);
    if (ks.every(k => k === ks[0])) { sysKeyOf.set(sy, ks[0]); seenKey[ks[0]] = (seenKey[ks[0]] || 0) + 1; }
  }
  const dropout = (k) => (k === 0 || Math.sign(k) === Math.sign(fifths)) && Math.abs(k) < Math.abs(fifths);
  const keyOk = (k) => seenKey[k] >= 2 && (!dropout(k) || (seenKey[k] >= 3 && seenKey[k] > 0.5 * allSys.size));
  // Key changes at system breaks: walk the systems in order with the key in
  // force (the previous system's, or a change read inside it). A system whose
  // staves all read another key takes it unless that is a dropout of the key
  // in force (same side or none, fewer accidentals: a faded signature loses
  // accidentals, it does not gain them in the right places), which still
  // needs the majority rule above. A gain of a single accidental on a lone
  // staff (a note's accidental just after the signature) must be confirmed
  // by another staff, the next system or an earlier reading.
  const seqKey = new Map();
  {
    const order = [...allSys], lastFifths = (sy) => {
      let best = null;
      for (const s of sy.staves) for (const ch of s.chords) for (const h of ch.heads) if (!best || h.x > best.x) best = h;
      return best && best.fifths != null ? best.fifths : null;
    };
    const drop = (r, c) => (r === 0 || Math.sign(r) === Math.sign(c)) && Math.abs(r) < Math.abs(c);
    const multi = [...sysKeyOf.values()].some(r => r !== fifths && !drop(r, fifths));
    let cur = null;
    order.forEach((sy, i) => {
      const r = sysKeyOf.get(sy), next = order[i + 1] ? sysKeyOf.get(order[i + 1]) : undefined;
      let k;
      // the first system: in a piece whose readings are all the piece's key
      // or dropouts of it, the piece's key; in a piece that reads other keys
      // too, its own reading unless that is a dropout of a piece key read on
      // two systems or more
      if (cur == null) k = r != null && (keyOk(r) || (multi && (!drop(r, fifths) || (seenKey[fifths] || 0) < 2))) ? r : fifths;
      else if (r == null || r === cur) k = cur;
      else if (drop(r, cur)) k = seenKey[r] >= 3 && seenKey[r] > 0.5 * allSys.size ? r : cur;
      else if (keyOk(r) || sy.staves.length >= 2 || next === r || Math.sign(r) !== Math.sign(cur) || Math.abs(r) >= Math.abs(cur) + 2) k = r;
      else k = cur;
      seqKey.set(sy, k);
      const e = lastFifths(sy);
      cur = e != null ? e : k;
    });
  }
  const keyAt = (mi) => {
    const sy = unitSys && unitSys[mi], k = sy != null ? sysKeyOf.get(sy) : undefined;
    if (sy != null && seqKey.has(sy)) return seqKey.get(sy);
    return k != null && keyOk(k) ? k : fifths;
  };
  const altsOf = new Map();
  const altsFor = (f) => { if (!altsOf.has(f)) altsOf.set(f, keyAlters(f)); return altsOf.get(f); };
  // A clef read on one system only is also kept when it carries on a clef
  // change read inside that staff on the system before (the new clef is
  // printed again at the head of the next system)
  const carried = new Set();
  {
    const order = [...allSys];
    for (let i = 1; i < order.length; i++) order[i].staves.forEach((st, k) => {
      const prev = order[i - 1].staves[k];
      if (!prev || st.hdr.clefGuessed || !st.hdr.clef) return;
      let last = null;
      for (const ch of prev.chords) for (const h of ch.heads) if (!last || h.x > last.x) last = h;
      if (last && last.clef && last.clef === st.hdr.clef) carried.add(order[i].staves[k]);
    });
  }
  const clefAt = (mi, staff) => {
    const sy = unitSys && unitSys[mi], st = sy && sy.staves[staff];
    if (st && !st.hdr.clefGuessed && st.hdr.clef && ((seenClef[staff + ':' + st.hdr.clef] || 0) >= 2 || carried.has(st))) return st.hdr.clef;
    return clefs[staff] || 'G';
  };
  // Accidentals on a shared staff bind every voice on it for the rest of the
  // bar (a split Alto keeps the natural the Soprano printed): per measure and
  // staff, the accidentals of all parts by onset time.
  const accLine = new Map();
  partMeasures.forEach(pm => pm.forEach((streams, mi) => streams.forEach(st => {
    const key = mi + ':' + st.staff;
    if (!accLine.has(key)) accLine.set(key, []);
    const clef = clefAt(mi, st.staff);
    let t = 0;
    for (const e of st.events) {
      if (!e.rest && !e.forward && e.heads) for (const h of e.heads) {
        if (!h.acc || e.tieStop) continue;
        // a clef or key change read inside the staff (assemble.js marks the
        // heads after it with h.clef / h.fifths) overrides the staff's own
        const pk = pitchOf(h.clef || clef, h.p, altsFor(h.fifths != null ? h.fifths : keyAt(mi)), {});
        accLine.get(key).push({ t, k: pk.step + pk.octave, a: h.acc === 'sharp' ? 1 : h.acc === 'flat' ? -1 : h.acc === 'double-sharp' ? 2 : h.acc === 'flat-flat' ? -2 : 0 });
      }
      t += e.q;
    }
  })));
  accLine.forEach(a => a.sort((x, y) => x.t - y.t));
  const L = [];
  const noteAt = [], noted = new Set(); // (user corrections: the XML line of each head's first written note)
  L.push('<?xml version="1.0" encoding="UTF-8" standalone="no"?>');
  L.push('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">');
  L.push('<score-partwise version="4.0">');
  head = head || {};
  L.push(`  <work><work-title>${esc(title || 'Scanned score')}</work-title></work>`);
  const creators = ['composer', 'lyricist', 'arranger'].filter(k => head[k]).map(k => `<creator type="${k}">${esc(head[k])}</creator>`).join('');
  L.push(`  <identification>${creators}${head.rights ? `<rights>${esc(head.rights)}</rights>` : ''}<encoding><software>Score Scan Reader (classical OMR, browser)</software></encoding></identification>`);
  // title and credits as printed on the first page
  for (const k of ['title', 'subtitle', 'composer', 'lyricist', 'arranger', 'rights']) {
    if (head[k]) L.push(`  <credit page="1"><credit-type>${k}</credit-type><credit-words>${esc(head[k])}</credit-words></credit>`);
  }
  for (const c of credits || []) {
    L.push(`  <credit page="${c.page}"><credit-type>lyrics</credit-type>${c.label ? `<credit-words>${esc(c.label)} </credit-words>` : ''}<credit-words>${esc(c.text)}</credit-words></credit>`);
  }
  L.push('  <part-list>');
  // vocal parts split from shared staves are bracketed as one choir group
  const vocalIdx = parts.map((p, i) => (p.kind === 'vocal' ? i : -1)).filter(i => i >= 0);
  const groupChoir = vocalIdx.length >= 2 && vocalIdx.every((v, k) => k === 0 || v === vocalIdx[k - 1] + 1) &&
    parts.some(p => p.kind === 'vocal' && (p.src[0].voice === 1 || p.src[0].voice === 2));
  parts.forEach((p, i) => {
    if (groupChoir && i === vocalIdx[0]) L.push('    <part-group type="start" number="1"><group-name>Choir</group-name><group-symbol>bracket</group-symbol><group-barline>no</group-barline></part-group>');
    // General MIDI sound per part (playback.js), so exports and players carry it (OMR_NO_MIDI=1: left out)
    const midi = process.env.OMR_NO_MIDI ? '' : instrumentXML(p, i, parts.length, { vocalParts: parts.filter(q => q.kind === 'vocal').length });
    L.push(`    <score-part id="${p.id}"><part-name>${esc(p.name)}</part-name>${p.abbrev ? `<part-abbreviation>${esc(p.abbrev)}</part-abbreviation>` : ''}${midi}</score-part>`);
    if (groupChoir && i === vocalIdx[vocalIdx.length - 1]) L.push('    <part-group type="stop" number="1"/>');
  });
  L.push('  </part-list>');
  parts.forEach((p, pi) => {
    L.push(`  <part id="${p.id}">`);
    const nStaves = p.src.length;
    const multi = nStaves > 1;
    const curClef = [];
    // octave line in force per staff of the part (ottava.js), written by the first voice on it
    const ottCur = [];
    const ottXML = (k, si, stop) => `      <direction placement="${k > 0 ? 'above' : 'below'}"><direction-type><octave-shift type="${stop ? 'stop' : k > 0 ? 'down' : 'up'}" size="${Math.abs(k) === 2 ? 15 : 8}" number="1"/></direction-type>${multi ? `<staff>${si + 1}</staff>` : ''}</direction>`;
    let curKey = fifths, curTime = null;
    // clef / key in force at a stream's first note: a change read inside a
    // staff (h.clef / h.fifths from assemble.js) carries on into later bars
    const firstHead = (st) => { for (const e of st.events) if (!e.rest && !e.forward && e.heads && e.heads.length) return e.heads[0]; return null; };
    partMeasures[pi].forEach((streams, mi) => {
      const implicit = streams.every(s => s.implicit);
      L.push(`    <measure number="${implicit ? 0 : mi + (partMeasures[pi][0].every(s => s.implicit) ? 0 : 1)}"${implicit ? ' implicit="yes"' : ''}>`);
      // the meter of each bar (buildScore: read changes of time signature), written where it changes
      const tm = (unitTime && unitTime[mi]) || time;
      const timeXML = `<time${tm.symbol ? ` symbol="${tm.symbol}"` : ''}><beats>${tm.beats}</beats><beat-type>${tm.type}</beat-type></time>`;
      // a multi-bar rest starting here (its bars follow as bars of rest)
      const mrest = unitMulti && unitMulti[mi] > 1 ? `<measure-style><multiple-rest>${unitMulti[mi]}</multiple-rest></measure-style>` : '';
      if (mi === 0) {
        const fh0 = streams.map(firstHead).find(Boolean);
        curKey = fh0 && fh0.fifths != null ? fh0.fifths : keyAt(0);
        curTime = timeXML;
        L.push(`      <attributes><divisions>${DIV}</divisions><key><fifths>${curKey}</fifths></key>${timeXML}` +
          (multi ? `<staves>${nStaves}</staves>${p.src.map((s, k) => clefXML(clefAt(0, s.staff), k + 1)).join('')}` : clefXML(clefAt(0, p.src[0].staff))) + mrest + '</attributes>');
        p.src.forEach((s, k) => { curClef[k] = clefAt(0, s.staff); });
      } else {
        const ch = [];
        const fh = streams.map(firstHead).find(Boolean);
        const key = fh && fh.fifths != null ? fh.fifths : keyAt(mi);
        if (key !== curKey) { ch.push(`<key><fifths>${key}</fifths></key>`); curKey = key; }
        if (timeXML !== curTime) { ch.push(timeXML); curTime = timeXML; }
        p.src.forEach((s, k) => {
          const h0 = streams[k] ? firstHead(streams[k]) : null;
          const c = (h0 && h0.clef) || clefAt(mi, s.staff);
          if (c !== curClef[k]) { ch.push(clefXML(c, multi ? k + 1 : 0)); curClef[k] = c; }
        });
        if (mrest) ch.push(mrest);
        if (ch.length) L.push(`      <attributes>${ch.join('')}</attributes>`);
      }
      const ub = (unitBars && unitBars[mi]) || {};
      if (ub.left) L.push(barlineXML('left', ub.left));
      // streams in staff then voice order; an empty optional voice is left
      // out; <backup> returns to the bar start after each written voice
      const ps = p.streams || p.src.map((s, k) => ({ ...s, staffNo: k + 1, vno: multi ? 1 + 4 * k : 1 }));
      const order = streams.map((_, k) => k).filter(k => streams[k] && !(ps[k] && ps[k].optional && !streams[k].events.length))
        .sort((a, b) => (ps[a].staffNo - ps[b].staffNo) || (ps[a].vno - ps[b].vno));
      let pos = 0;
      // directions (dynamics, hairpins, words) go with the first voice written,
      // before the note they stand at (an offset when they fall inside it)
      const pend = ((dirs && dirs[pi] && dirs[pi][mi]) || []).slice();
      const dirXML = (d, off) => `      ${d.xml}${off ? `<offset>${off}</offset>` : ''}${d.staffNo ? `<staff>${d.staffNo}</staff>` : ''}${d.tail || ''}</direction>`;
      const ottSeen = new Set();
      order.forEach((k, oi) => {
        const s = streams[k], si = ps[k].staffNo - 1;
        const ottFirst = !ottSeen.has(si);
        ottSeen.add(si);
        if (pos > 0) L.push(`      <backup><duration>${pos}</duration></backup>`);
        pos = s.events.reduce((a, e) => a + Math.max(1, Math.round(e.q * DIV)), 0);
        let dt = 0;
        const flush = oi === 0 ? (e) => {
          while (pend.length && pend[0].t < dt + e.q - 1e-6) { const d = pend.shift(); L.push(dirXML(d, Math.max(0, Math.round((d.t - dt) * DIV)))); }
          dt += e.q;
        } : null;
        const clef = clefAt(mi, s.staff);
        const line = accLine.get(mi + ':' + s.staff) || [];
        let et = 0;
        const voice = ps[k].vno;
        const staffTag = multi ? `<staff>${si + 1}</staff>` : '';
        // beams read on the page (assemble.js: h.beam, one id per beam group): begin / continue /
        // end along the notes of this voice that share a group
        const bid = s.events.map(e => (!e.rest && !e.forward && e.heads && e.heads[0].beam && e.q < 1 - 1e-6 ? e.heads[0].beam : 0));
        const beamOf = bid.map((b, i) => {
          if (!b) return '';
          const p = i > 0 && bid[i - 1] === b, n = i + 1 < bid.length && bid[i + 1] === b;
          return p && n ? 'continue' : n ? 'begin' : p ? 'end' : '';
        });
        let ei = -1;
        for (const e of s.events) {
          ei++;
          if (flush) flush(e);
          if (ottFirst && !e.rest && !e.forward && e.heads && e.heads.length) {
            const ko = e.heads[0].ott || 0;
            if (ko !== (ottCur[si] || 0)) {
              if (ottCur[si]) L.push(ottXML(ottCur[si], si, true));
              if (ko) L.push(ottXML(ko, si, false));
              ottCur[si] = ko;
            }
          }
          const t0 = et;
          et += e.q;
          const dur = Math.max(1, Math.round(e.q * DIV));
          let tt = qToType(e.q), tmod = '';
          const tu = tupletOf(e);
          if (!tt && tu) {
            // a tuplet note: drawn as its plain value, scaled by the ratio
            tt = qToType(e.q * tu.actual / tu.normal);
            if (tt) tmod = `<time-modification><actual-notes>${tu.actual}</actual-notes><normal-notes>${tu.normal}</normal-notes></time-modification>`;
          }
          const typeXML = tt ? `<type>${tt.type}</type>${'<dot/>'.repeat(tt.dots)}` : '';
          if (e.forward) {
            L.push(`      <forward><duration>${dur}</duration><voice>${voice}</voice>${staffTag}</forward>`);
            continue;
          }
          if (e.rest) {
            const rf = e.fermata ? `<notations><fermata type="${e.fermata}"/></notations>` : '';
            if (e.whole) L.push(`      <note><rest measure="yes"/><duration>${dur}</duration><voice>${voice}</voice>${staffTag}${rf}</note>`);
            else L.push(`      <note><rest/><duration>${dur}</duration><voice>${voice}</voice>${typeXML}${staffTag}${rf}</note>`);
            continue;
          }
          const hc = e.heads[0].clef || clef;
          if (curClef[si] !== undefined && hc !== curClef[si]) { L.push(`      <attributes>${clefXML(hc, multi ? si + 1 : 0)}</attributes>`); curClef[si] = hc; }
          // grace notes read before this note (no duration; a slash for an acciaccatura)
          for (const gn of e.graces || []) {
            const pt = pitchOf(hc, gn.p, altsFor(e.heads[0].fifths != null ? e.heads[0].fifths : keyAt(mi)), {});
            L.push(`      <note><grace${gn.slash ? ' slash="yes"' : ''}/><pitch><step>${pt.step}</step>${pt.alter ? `<alter>${pt.alter}</alter>` : ''}<octave>${pt.octave}</octave></pitch><voice>${voice}</voice><type>${gn.n > 1 ? '16th' : 'eighth'}</type><stem>up</stem>${staffTag}</note>`);
          }
          e.heads.forEach((h, hi) => {
            const pos = h.p;
            const hClef = h.clef || clef, hAlt = altsFor(h.fifths != null ? h.fifths : keyAt(mi));
            const pk = pitchOf(hClef, pos, hAlt, {}), kk = pk.step + pk.octave;
            let alt = null;
            for (const a of line) { if (a.t > t0 + 1e-6) break; if (a.k === kk) alt = a.a; }
            const pw = pitchOf(hClef, pos, hAlt, alt == null ? {} : { [kk]: alt });
            // under an octave line (ottava.js: h.ott) the note sounds 1 or 2 octaves away
            const pt = h.ott && pw.octave + h.ott >= 0 && pw.octave + h.ott <= 9 ? { ...pw, octave: pw.octave + h.ott, d: pw.d + 7 * h.ott } : pw;
            h.pitch = pt;
            // (overlay only: the value written for this head, first part that writes it)
            h.shown ||= { q: e.q, type: tt ? tt.type : null, dots: tt ? tt.dots : 0, tuplet: tmod ? tu.actual : 0 };
            if (!noted.has(h)) { noted.add(h); noteAt.push([h, L.length]); }
            const acc = h.acc && !e.tieStop ? `<accidental>${h.acc}</accidental>` : '';
            // ties: a note cut at a barline (e.tieStart / e.tieStop) or a tie read on the page (h.tieOn / h.tieOff);
            // slurs read on the page (h.slurOn / h.slurOff)
            const tStop = e.tieStop || h.tieOff, tStart = e.tieStart || h.tieOn;
            const tie = (tStop ? '<tie type="stop"/>' : '') + (tStart ? '<tie type="start"/>' : '');
            const slurs = hi === 0 ? (e.heads.some(x => x.slurOff) ? '<slur type="stop" number="1"/>' : '') + (e.heads.some(x => x.slurOn) ? '<slur type="start" number="1"/>' : '') : '';
            const ferm = hi === 0 && e.fermata ? `<fermata type="${e.fermata}"/>` : '';
            // articulations read over / under the chord (artic.js: h.artic), on the first note of a
            // chord and not again on the continuation of a note tied over a barline
            const ar = hi === 0 && !e.tieStop ? (e.heads.find(x => x.artic) || {}).artic : null;
            const artic = ar && ar.length ? `<articulations>${ar.map(k => (k === 'marcato' ? '<strong-accent type="up"/>' : `<${k}/>`)).join('')}</articulations>` : '';
            const tied = tStop || tStart || slurs || ferm || artic ? `<notations>${tStop ? '<tied type="stop"/>' : ''}${tStart ? '<tied type="start"/>' : ''}${slurs}${artic}${ferm}</notations>` : '';
            // a head with both stems: up in the upper voice, down in the lower
            const sd = h.stemDir === 2 ? (e.low ? -1 : 1) : h.stemDir;
            const stem = sd === 1 ? '<stem>up</stem>' : sd === -1 ? '<stem>down</stem>' : '';
            let lyr = '';
            if (hi === 0 && (e.lyrics || e.lyrExt)) {
              const nums = new Set([...Object.keys(e.lyrics || {}), ...Object.keys(e.lyrExt || {})]);
              for (const n of [...nums].sort((a, b) => a - b)) {
                const l = e.lyrics && e.lyrics[n];
                // an elision: the two syllables joined by ‿ on one note
                const body = l && l.elision ? `<syllabic>${l.syllabic}</syllabic><text>${esc(l.elision[0])}</text><elision>‿</elision><syllabic>single</syllabic><text>${esc(l.elision[1])}</text>` : l ? `<syllabic>${l.syllabic}</syllabic><text>${esc(l.text)}</text>` : '';
                if (l) lyr += `<lyric number="${n}">${body}${l.extend ? '<extend type="start"/>' : ''}</lyric>`;
                else lyr += `<lyric number="${n}"><extend type="stop"/></lyric>`;
              }
            }
            L.push(`      <note>${hi > 0 ? '<chord/>' : ''}<pitch><step>${pt.step}</step>${pt.alter ? `<alter>${pt.alter}</alter>` : ''}<octave>${pt.octave}</octave></pitch>` +
              `<duration>${dur}</duration>${tie}<voice>${voice}</voice>${typeXML}${acc}${tmod}${stem}${staffTag}${beamOf[ei] ? `<beam number="1">${beamOf[ei]}</beam>` : ''}${tied}${lyr}</note>`);
          });
        }
      });
      // marks past the first voice's last note (or a bar with no voice written)
      if (pend.length) {
        const cur = order.length ? pos / DIV : 0;
        for (const d of pend) L.push(dirXML(d, Math.round((d.t - cur) * DIV)));
      }
      if (mi === partMeasures[pi].length - 1) ottCur.forEach((k, si) => { if (k) L.push(ottXML(k, si, true)); });
      if (mi === partMeasures[pi].length - 1) L.push(barlineXML('right', { ...ub.right, style: 'light-heavy' }));
      else if (ub.right) L.push(barlineXML('right', ub.right));
      L.push('    </measure>');
    });
    L.push('  </part>');
  });
  L.push('</score-partwise>');
  // entries may hold line breaks: count them for the line numbers
  if (noteAt.length) {
    const off = new Array(L.length + 1).fill(0);
    for (let i = 0; i < L.length; i++) off[i + 1] = off[i] + (L[i].split('\n').length - 1);
    for (const [h, i] of noteAt) h.xmlLine = i + off[i];
  }
  return L.join('\n') + '\n';
}

module.exports = { buildScore, chooseLayout, chooseKey, COLORS };
