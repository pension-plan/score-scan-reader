'use strict';
// Page assemblies -> parts (closed-score split / grand staff / single), time
// signature inference, per-measure rhythm repair, lyrics alignment, MusicXML.
const { staffMeasureEvents, pitchOf, keyAlters, DIV } = require('./assemble');
const { detectRests, mergeRests, restBars } = require('./rests');

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
        cur = { name: shown.charAt(0).toUpperCase() + shown.slice(1), kind: hit[2], abbrev, canon: hit[1] };
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
  // keyboard links between adjacent staves
  const link = [];
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
    // printed names overrule: one keyboard name across the pair joins it; a
    // staff with its own voice or instrument name is not half of a grand staff
    if (labels[k].some(l => l.span && l.span.includes(k + 1) && l.names.some(n => n.kind === 'keyboard'))) kb = true;
    else if (ownNames(k, ['vocal', 'instrument']).length || ownNames(k + 1, ['vocal', 'instrument']).length) kb = false;
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
  const vs = vocal.map(k => ({ staff: k, clef: clefs[k], split: stats[k].f2 > 0.35 && stats[k].f3 < 0.2 }));
  // a two-staff closed score decides once for both staves
  if (vs.length === 2 && nSt === 2) {
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
  const vnames = vocalNames(vs);
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
    const nm = (k) => { const n = v.names && v.names[k]; const inf = vnames[vi++]; return n ? { name: n.name, nameRead: true } : { name: inf, nameRead: false }; };
    if (v.split) {
      parts.push({ ...nm(0), kind: 'vocal', src: [{ staff: v.staff, voice: 1 }], layout: `Staff ${v.staff + 1}, stems up (split from a shared staff)` });
      parts.push({ ...nm(1), kind: 'vocal', src: [{ staff: v.staff, voice: 2 }], layout: `Staff ${v.staff + 1}, stems down (split from a shared staff)` });
      notes.push(`Staff ${v.staff + 1}: two voices on one staff, split by stem direction into ${parts[parts.length - 2].name} and ${parts[parts.length - 1].name}.`);
    } else parts.push({ ...nm(0), kind: 'vocal', src: [{ staff: v.staff, voice: 'chordal' }], layout: `Staff ${v.staff + 1}` });
  }
  parts.forEach(p => { if (p.nameRead) read.push(p.name); });
  if (read.length) notes.push(`Part names read from the page: ${read.join(', ')}.`);
  parts.forEach((p, i) => { p.id = 'P' + (i + 1); p.color = COLORS[i % COLORS.length]; });
  return { parts, nSt, notes, clefs, stats, link };
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
  if (process.env.KBDEBUG && evidence && up.length && dn.length) console.error('KB', evidence, 'v2notes', dn.length, 'both', chordal.filter(e => e.heads.some(h => h.stemDir === 2)).map(e => e.heads.filter(h => h.stemDir === 2).map(h => h.dur.q + '/' + (h.dur.down ? h.dur.down.q : '-')).join(',')).join(' '), 'mixed', chordal.filter(e => e.heads.some(h => h.stemDir === 1) && e.heads.some(h => h.stemDir === -1)).length);
  // one sign and one lone lower note is as likely a stray stem or flag
  if (!evidence || !up.length || !dn.length || (evidence < 2 && dn.length < 2 && !process.env.KBWEAK)) return null;
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
  const systems = pages.flatMap(p => p.asm.systems.map(s => ({ ...s, fr: p.fr, comps: p.asm.comps })));
  if (!systems.length) return { parts: [], measures: 0, warnings: ['No music systems found.'], xml: emptyXML() };
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
      if (p.kind === 'keyboard' && !process.env.NOKB2) {
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
    if (!process.env.OLDPAIRS && single && rnd(v) === single && rnd(segSum[i + 1]) === single) return;
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
    const hs = systems.flatMap(sy => sy.staves.map(s => s.hdr && s.hdr.time)).filter(t => t && t.beats > 0 && t.type > 0);
    if (hs.length >= Math.max(1, 0.3 * systems.filter(sy => sy.index === 0).reduce((a, sy) => a + sy.staves.length, 0))) {
      const key = mode(hs.map(t => `${t.beats}/${t.type}`)), [b, ty] = key.split('/').map(Number), hq = (b * 4) / ty;
      const qNow = (time.beats * 4) / time.type;
      if (Math.abs(hq - qNow) < 1e-6 || (votes[hq] || 0) >= 0.5 * (votes[qNow] || 0)) { time = { beats: b, type: ty }; timeRead = true; }
    }
  }
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
    const n = i1 - i0 + 1, best = new Array(n + 1).fill(Infinity), from = new Array(n + 1).fill(-1);
    best[0] = 0;
    for (let j = 1; j <= n; j++) {
      for (let i = Math.max(0, j - 5); i < j; i++) {
        if (best[i] === Infinity) continue;
        const a = i0 + i, b = i0 + j - 1;
        const edge = a === 0 || b === segs.length - 1;
        let c = 2 * groupDev(a, b, edge);
        for (let t = a; t < b; t++) {
          const sp = (segs[t].sy.staves[0] && segs[t].sy.staves[0].st.space) || 16;
          const w = Math.min(segs[t].xb - segs[t].xa, segs[t + 1].xb - segs[t + 1].xa) / sp;
          c += w < 4 ? 0.15 : 0.45;
        }
        if (best[i] + c < best[j] - 1e-9) { best[j] = best[i] + c; from[j] = i; }
      }
    }
    const groups = [];
    for (let j = n; j > 0; j = from[j]) groups.unshift(Array.from({ length: j - from[j] }, (_, t) => i0 + from[j] + t));
    groups.forEach(g => measures.push({ segs: g }));
    i0 = i1 + 1;
  }
  // a bar split across a system break: two short halves that make one bar
  for (let k = 1; k + 1 < measures.length; k++) {
    const a = measures[k], b = measures[k + 1];
    if (segs[a.segs[0]].sy === segs[b.segs[0]].sy || a.segs.length > 1 || b.segs.length > 1) continue;
    const sa = segSum[a.segs[0]], sb = segSum[b.segs[0]];
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
    for (const c of take) alignSyllables(v, c.evs, sp);
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
    const byPart = perPart.map(pm => pm[mi]);
    const sums = [];
    byPart.forEach(sts => sts.forEach(st => { const q = qsum(st.events); if (q > 1e-6) sums.push(Math.round(q * 4) / 4); }));
    const S = sums.length ? mode(sums) : 0;
    const k = Math.round(S / mLen);
    const agree = sums.filter(x => Math.abs(x - S) <= 0.25 * mLen).length;
    if (k >= 2 && Math.abs(S - k * mLen) <= 0.25 * mLen && agree >= Math.max(1, 0.5 * sums.length)) {
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
      chunks.forEach(ch => units.push({ m, streams: ch, split: true }));
      return;
    }
    units.push({ m, streams: byPart, split: false });
    // a multi-bar rest (or church rests) in a bar with no notes: one bar each
    const barRests = byPart.flatMap(sts => sts.flatMap(st => st.events));
    if (barRests.length && barRests.every(e => e.bar)) {
      const n = Math.max(...barRests.map(e => restBars(e, mLen)));
      for (let k = 1; k < n; k++) units.push({ m, streams: byPart.map(sts => sts.map(st => ({ staff: st.staff, events: [] }))), split: false });
    }
  });
  const partMeasures = parts.map(() => []);
  units.forEach((u, mi) => {
    const m = u.m;
    const streams = [];
    parts.forEach((p, pi) => u.streams[pi].forEach((st, k) => streams.push({ pi, k, staff: st.staff, events: st.events.slice() })));
    const sums = streams.map(st => qsum(st.events));
    const nz = sums.filter(x => x > 1e-6).map(x => Math.round(x * DIV) / DIV);
    let target = mLen;
    const ms = nz.length ? mode(nz) : 0;
    const agree = nz.filter(x => Math.abs(x - ms) < 1e-6).length;
    const edge = mi === 0 || mi === units.length - 1;
    if (edge && ms > 1e-6 && ms < mLen - 1e-6 && agree >= Math.max(2, 0.5 * nz.length)) target = ms;
    else if (edge && ms > 1e-6 && ms < mLen - 1e-6 && nz.length === 1) target = ms;
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
  const xml = toMusicXML({ parts, partMeasures, fifths, kAlt, time, clefs, measures, credits, unitSys });
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
  // UI compares clefs with 'F'; 'G8' stays a treble clef there
  return { parts, layout, fifths, time, timeRead, clefs, ranges, measures: units.length, nNotes, credits, warnings: warnings.concat(layout.notes), xml };
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
function alignSyllables(verse, evs, sp) {
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

function toMusicXML({ parts, partMeasures, fifths, kAlt, time, clefs, title, credits, unitSys }) {
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
  const keyAt = (mi) => {
    const sy = unitSys && unitSys[mi], k = sy != null ? sysKeyOf.get(sy) : undefined;
    return k != null && keyOk(k) ? k : fifths;
  };
  const altsOf = new Map();
  const altsFor = (f) => { if (!altsOf.has(f)) altsOf.set(f, keyAlters(f)); return altsOf.get(f); };
  const clefAt = (mi, staff) => {
    const sy = unitSys && unitSys[mi], st = sy && sy.staves[staff];
    if (st && !st.hdr.clefGuessed && st.hdr.clef && (seenClef[staff + ':' + st.hdr.clef] || 0) >= 2) return st.hdr.clef;
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
  L.push('<?xml version="1.0" encoding="UTF-8" standalone="no"?>');
  L.push('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">');
  L.push('<score-partwise version="4.0">');
  L.push(`  <work><work-title>${esc(title || 'Scanned score')}</work-title></work>`);
  L.push('  <identification><encoding><software>Score Scan Reader (classical OMR, browser)</software></encoding></identification>');
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
    L.push(`    <score-part id="${p.id}"><part-name>${esc(p.name)}</part-name></score-part>`);
    if (groupChoir && i === vocalIdx[vocalIdx.length - 1]) L.push('    <part-group type="stop" number="1"/>');
  });
  L.push('  </part-list>');
  parts.forEach((p, pi) => {
    L.push(`  <part id="${p.id}">`);
    const nStaves = p.src.length;
    const multi = nStaves > 1;
    const curClef = [];
    let curKey = fifths;
    // clef / key in force at a stream's first note: a change read inside a
    // staff (h.clef / h.fifths from assemble.js) carries on into later bars
    const firstHead = (st) => { for (const e of st.events) if (!e.rest && !e.forward && e.heads && e.heads.length) return e.heads[0]; return null; };
    partMeasures[pi].forEach((streams, mi) => {
      const implicit = streams.every(s => s.implicit);
      L.push(`    <measure number="${implicit ? 0 : mi + (partMeasures[pi][0].every(s => s.implicit) ? 0 : 1)}"${implicit ? ' implicit="yes"' : ''}>`);
      if (mi === 0) {
        const fh0 = streams.map(firstHead).find(Boolean);
        curKey = fh0 && fh0.fifths != null ? fh0.fifths : keyAt(0);
        L.push(`      <attributes><divisions>${DIV}</divisions><key><fifths>${curKey}</fifths></key><time><beats>${time.beats}</beats><beat-type>${time.type}</beat-type></time>` +
          (multi ? `<staves>${nStaves}</staves>${p.src.map((s, k) => clefXML(clefAt(0, s.staff), k + 1)).join('')}` : clefXML(clefAt(0, p.src[0].staff))) + '</attributes>');
        p.src.forEach((s, k) => { curClef[k] = clefAt(0, s.staff); });
      } else {
        const ch = [];
        const fh = streams.map(firstHead).find(Boolean);
        const key = fh && fh.fifths != null ? fh.fifths : keyAt(mi);
        if (key !== curKey) { ch.push(`<key><fifths>${key}</fifths></key>`); curKey = key; }
        p.src.forEach((s, k) => {
          const h0 = streams[k] ? firstHead(streams[k]) : null;
          const c = (h0 && h0.clef) || clefAt(mi, s.staff);
          if (c !== curClef[k]) { ch.push(clefXML(c, multi ? k + 1 : 0)); curClef[k] = c; }
        });
        if (ch.length) L.push(`      <attributes>${ch.join('')}</attributes>`);
      }
      // streams in staff then voice order; an empty optional voice is left
      // out; <backup> returns to the bar start after each written voice
      const ps = p.streams || p.src.map((s, k) => ({ ...s, staffNo: k + 1, vno: multi ? 1 + 4 * k : 1 }));
      const order = streams.map((_, k) => k).filter(k => streams[k] && !(ps[k] && ps[k].optional && !streams[k].events.length))
        .sort((a, b) => (ps[a].staffNo - ps[b].staffNo) || (ps[a].vno - ps[b].vno));
      let pos = 0;
      order.forEach((k) => {
        const s = streams[k], si = ps[k].staffNo - 1;
        if (pos > 0) L.push(`      <backup><duration>${pos}</duration></backup>`);
        pos = s.events.reduce((a, e) => a + Math.max(1, Math.round(e.q * DIV)), 0);
        const clef = clefAt(mi, s.staff);
        const line = accLine.get(mi + ':' + s.staff) || [];
        let et = 0;
        const voice = ps[k].vno;
        const staffTag = multi ? `<staff>${si + 1}</staff>` : '';
        for (const e of s.events) {
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
            if (e.whole) L.push(`      <note><rest measure="yes"/><duration>${dur}</duration><voice>${voice}</voice>${staffTag}</note>`);
            else L.push(`      <note><rest/><duration>${dur}</duration><voice>${voice}</voice>${typeXML}${staffTag}</note>`);
            continue;
          }
          const hc = e.heads[0].clef || clef;
          if (curClef[si] !== undefined && hc !== curClef[si]) { L.push(`      <attributes>${clefXML(hc, multi ? si + 1 : 0)}</attributes>`); curClef[si] = hc; }
          e.heads.forEach((h, hi) => {
            const pos = h.p;
            const hClef = h.clef || clef, hAlt = altsFor(h.fifths != null ? h.fifths : keyAt(mi));
            const pk = pitchOf(hClef, pos, hAlt, {}), kk = pk.step + pk.octave;
            let alt = null;
            for (const a of line) { if (a.t > t0 + 1e-6) break; if (a.k === kk) alt = a.a; }
            const pt = pitchOf(hClef, pos, hAlt, alt == null ? {} : { [kk]: alt });
            h.pitch = pt;
            const acc = h.acc && !e.tieStop ? `<accidental>${h.acc}</accidental>` : '';
            const tie = (e.tieStop ? '<tie type="stop"/>' : '') + (e.tieStart ? '<tie type="start"/>' : '');
            const tied = e.tieStop || e.tieStart ? `<notations>${e.tieStop ? '<tied type="stop"/>' : ''}${e.tieStart ? '<tied type="start"/>' : ''}</notations>` : '';
            // a head with both stems: up in the upper voice, down in the lower
            const sd = h.stemDir === 2 ? (e.low ? -1 : 1) : h.stemDir;
            const stem = sd === 1 ? '<stem>up</stem>' : sd === -1 ? '<stem>down</stem>' : '';
            let lyr = '';
            if (hi === 0 && (e.lyrics || e.lyrExt)) {
              const nums = new Set([...Object.keys(e.lyrics || {}), ...Object.keys(e.lyrExt || {})]);
              for (const n of [...nums].sort((a, b) => a - b)) {
                const l = e.lyrics && e.lyrics[n];
                if (l) lyr += `<lyric number="${n}"><syllabic>${l.syllabic}</syllabic><text>${esc(l.text)}</text>${l.extend ? '<extend type="start"/>' : ''}</lyric>`;
                else lyr += `<lyric number="${n}"><extend type="stop"/></lyric>`;
              }
            }
            L.push(`      <note>${hi > 0 ? '<chord/>' : ''}<pitch><step>${pt.step}</step>${pt.alter ? `<alter>${pt.alter}</alter>` : ''}<octave>${pt.octave}</octave></pitch>` +
              `<duration>${dur}</duration>${tie}<voice>${voice}</voice>${typeXML}${acc}${tmod}${stem}${staffTag}${tied}${lyr}</note>`);
          });
        }
      });
      if (mi === partMeasures[pi].length - 1) L.push('      <barline location="right"><bar-style>light-heavy</bar-style></barline>');
      L.push('    </measure>');
    });
    L.push('  </part>');
  });
  L.push('</score-partwise>');
  return L.join('\n') + '\n';
}

module.exports = { buildScore, chooseLayout, chooseKey, COLORS };
