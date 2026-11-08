// Playback model: the app's MusicXML -> timed note events, General MIDI
// instruments per part, and a Standard MIDI File writer (and reader, for the
// tests). Pure functions, no DOM: the page's player (ui/player.js) and the
// Node tests use the same code.
//
//   events(xml, opts) -> { title, parts: [{ id, name, program, channel, volume, pan, notes: [...] }],
//                          measures: [{ src, number, q0, q1, t0, t1 }], tempos, beats, duration, quarters }
//     note: { part, staff, voice, midi, q, dq, t, d, vel, line, m (play-order measure), grace }
//       q / dq in quarters along the played timeline (repeats expanded), t / d in seconds,
//       line = 0-based line of the <note> in the MusicXML text (the overlay's head -> note link)
//   gmFor(name, ctx) -> { program (0-based), family }       part name -> GM program
//   instrumentXML(part, index, nParts, ctx) -> '<score-instrument>..<midi-instrument>..'
//   writeSMF(model) -> Uint8Array (type 1, 480 PPQ, tempo map, one track per part)
//   readSMF(bytes) -> { format, ppq, tracks: [[{ tick, type, ... }]] }
//
// Coverage: chords, voices (backup / forward), ties merged, dots and tuplets
// through <duration>, grace notes (short, stolen from the principal or the
// note before), rests, cue notes skipped, <transpose>; tempo from <sound
// tempo>, metronome marks, tempo words (Allegro, Not fast, ...), else 100 qpm;
// rit. / a tempo / Tempo I; fermatas hold 1.5x; dynamics, <sound dynamics>,
// wedges, cresc. / dim. words, accents and staccato -> velocity and length;
// repeats with voltas, D.C. / D.S. al Fine / al Coda (from <sound> or words).

// ------------------------------------------------------------- XML parse ---
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };
const decode = (s) => s.replace(/&(#x[0-9a-f]+|#\d+|\w+);/gi, (m, e) => (e[0] === '#' ? String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : +e.slice(1)) : ENT[e] != null ? ENT[e] : m));
// elements {name, attrs, children, text, line (0-based line of the start tag)}
function parseXML(s) {
  const root = { name: '#root', attrs: {}, children: [], text: '', line: 0 };
  const stack = [root];
  const re = /<!--[\s\S]*?-->|<!\[CDATA\[([\s\S]*?)\]\]>|<\?[\s\S]*?\?>|<!DOCTYPE(?:[^>[]|\[[\s\S]*?\])*>|<\/([^\s>]+)\s*>|<([^\s>/!?]+)((?:\s+[^\s=/>]+\s*=\s*(?:"[^"]*"|'[^']*'))*)\s*(\/?)>|([^<]+)/g;
  let m, line = 0, last = 0;
  while ((m = re.exec(s))) {
    for (let i = last; i < m.index; i++) if (s.charCodeAt(i) === 10) line++;
    last = m.index;
    const top = stack[stack.length - 1];
    if (m[1] !== undefined) top.text += m[1];
    else if (m[2]) { if (stack.length > 1) stack.pop(); }
    else if (m[3]) {
      const attrs = {};
      m[4].replace(/([^\s=]+)\s*=\s*("([^"]*)"|'([^']*)')/g, (_, k, __, a, b) => { attrs[k] = decode(a != null ? a : b); });
      const el = { name: m[3], attrs, children: [], text: '', line };
      top.children.push(el);
      if (!m[5]) stack.push(el);
    } else if (m[6] !== undefined) top.text += decode(m[6]);
  }
  return root;
}
const kid = (el, n) => (el ? el.children.find((c) => c.name === n) : undefined);
const kids = (el, n) => (el ? el.children.filter((c) => c.name === n) : []);
const txt = (el, n) => { const k = kid(el, n); return k ? k.text.trim() : ''; };
function findAll(el, n, out = []) { for (const c of el.children) { if (c.name === n) out.push(c); findAll(c, n, out); } return out; }
const findOne = (el, n) => findAll(el, n)[0];

// ------------------------------------------------------- GM instruments ---
const GM = ['Acoustic Grand Piano', 'Bright Acoustic Piano', 'Electric Grand Piano', 'Honky-tonk Piano', 'Electric Piano 1', 'Electric Piano 2', 'Harpsichord', 'Clavinet',
  'Celesta', 'Glockenspiel', 'Music Box', 'Vibraphone', 'Marimba', 'Xylophone', 'Tubular Bells', 'Dulcimer',
  'Drawbar Organ', 'Percussive Organ', 'Rock Organ', 'Church Organ', 'Reed Organ', 'Accordion', 'Harmonica', 'Tango Accordion',
  'Acoustic Guitar (nylon)', 'Acoustic Guitar (steel)', 'Electric Guitar (jazz)', 'Electric Guitar (clean)', 'Electric Guitar (muted)', 'Overdriven Guitar', 'Distortion Guitar', 'Guitar Harmonics',
  'Acoustic Bass', 'Electric Bass (finger)', 'Electric Bass (pick)', 'Fretless Bass', 'Slap Bass 1', 'Slap Bass 2', 'Synth Bass 1', 'Synth Bass 2',
  'Violin', 'Viola', 'Cello', 'Contrabass', 'Tremolo Strings', 'Pizzicato Strings', 'Orchestral Harp', 'Timpani',
  'String Ensemble 1', 'String Ensemble 2', 'Synth Strings 1', 'Synth Strings 2', 'Choir Aahs', 'Voice Oohs', 'Synth Voice', 'Orchestra Hit',
  'Trumpet', 'Trombone', 'Tuba', 'Muted Trumpet', 'French Horn', 'Brass Section', 'Synth Brass 1', 'Synth Brass 2',
  'Soprano Sax', 'Alto Sax', 'Tenor Sax', 'Baritone Sax', 'Oboe', 'English Horn', 'Bassoon', 'Clarinet',
  'Piccolo', 'Flute', 'Recorder', 'Pan Flute', 'Blown Bottle', 'Shakuhachi', 'Whistle', 'Ocarina',
  'Lead 1 (square)', 'Lead 2 (sawtooth)', 'Lead 3 (calliope)', 'Lead 4 (chiff)', 'Lead 5 (charang)', 'Lead 6 (voice)', 'Lead 7 (fifths)', 'Lead 8 (bass + lead)',
  'Pad 1 (new age)', 'Pad 2 (warm)', 'Pad 3 (polysynth)', 'Pad 4 (choir)', 'Pad 5 (bowed)', 'Pad 6 (metallic)', 'Pad 7 (halo)', 'Pad 8 (sweep)',
  'FX 1 (rain)', 'FX 2 (soundtrack)', 'FX 3 (crystal)', 'FX 4 (atmosphere)', 'FX 5 (brightness)', 'FX 6 (goblins)', 'FX 7 (echoes)', 'FX 8 (sci-fi)',
  'Sitar', 'Banjo', 'Shamisen', 'Koto', 'Kalimba', 'Bagpipe', 'Fiddle', 'Shanai',
  'Tinkle Bell', 'Agogo', 'Steel Drums', 'Woodblock', 'Taiko Drum', 'Melodic Tom', 'Synth Drum', 'Reverse Cymbal',
  'Guitar Fret Noise', 'Breath Noise', 'Seashore', 'Bird Tweet', 'Telephone Ring', 'Helicopter', 'Applause', 'Gunshot'];
// part name patterns, first match wins (English, German, Italian, French names and abbreviations)
const NAME_GM = [
  [/organ|orgel|organo|orgue|pedal|ped\./i, 19], [/harmonium/i, 20], [/harpsichord|cembalo|clavecin/i, 6], [/celest/i, 8],
  [/accordion|akkordeon/i, 21], [/harmonica/i, 22], [/marimba/i, 12], [/xylophon/i, 13], [/vibraphon/i, 11], [/glocken/i, 9], [/timpan|pauken/i, 47],
  [/harp\b|harfe|arpa|harpe/i, 46],
  [/violoncell|cello|vc\.?$|vlc/i, 42], [/viola|bratsche|vla\.?$|alto viol/i, 41], [/contrabass|double bass|kontrabass|string bass|cb\.?$/i, 43],
  [/violin|geige|violino|violon\b|vln?\.?\s*\d*$|fiddle/i, 40], [/strings|streicher|archi/i, 48],
  [/piccolo|ottavino/i, 72], [/flute|flöte|flauto|fl\.?\s*\d*$/i, 73], [/recorder|blockflöte/i, 74], [/oboe|hautbois|ob\.?\s*\d*$/i, 68], [/english horn|cor anglais|englischhorn/i, 69],
  [/clarinet|klarinette|clarinetto|cl\.?\s*\d*$/i, 71], [/bassoon|fagott|fagotto|basson|bsn/i, 70],
  [/soprano sax/i, 64], [/alto sax|altsax/i, 65], [/tenor sax/i, 66], [/baritone sax|bari sax/i, 67], [/sax/i, 65],
  [/trumpet|trompete|tromba|cornet|kornett|tpt|trp/i, 56], [/trombone|posaune|tbn/i, 57], [/tuba|euphonium/i, 58], [/horn|corno|cor\b|hn\.?\s*\d*$/i, 60], [/brass|bläser/i, 61],
  [/bass guitar|electric bass/i, 33], [/guitar|gitarre|chitarra|guitare|gtr/i, 24], [/banjo/i, 105], [/ukulele/i, 24], [/mandolin/i, 25],
  [/drum|percussion|schlagzeug|snare|cymbal/i, -1],
  [/piano|klavier|pianoforte|pno|pf\.?$|keyboard|accomp/i, 0],
];
const VOICE_RE = /soprano|sopran|alto\b|^alt\b|tenor|bass\b|^bass|baritone|bariton|mezzo|contralto|treble|cantus|voice|vocal|stimme|singst|choir|chorus|chor\b|coro|satb|s\.?\s*a\.?\s*t\.?\s*b|melody|melodie|descant|canto|cantor|solo|^[satb]\.?\s*\d*$|^[satb]\s*[12]?$|^(s|a|t|b)\s*&\s*(s|a|t|b)$/i;
// family of a GM program, for the player's sample sets
function gmFamily(p) {
  if (p < 0) return 'drums';
  if (p <= 15) return 'piano';
  if (p <= 23) return 'organ';
  if (p <= 31) return 'guitar';
  if (p <= 39) return 'bass';
  if (p <= 51 || p === 55) return 'strings';
  if (p <= 54) return 'voice';
  if (p <= 63) return 'brass';
  if (p <= 71) return 'reed';
  if (p <= 79) return 'pipe';
  return 'synth';
}
// ctx: { vocalParts: number of vocal parts in the score, kind: the part's kind from the pipeline }
function gmFor(name, ctx = {}) {
  const n = String(name || '').trim();
  // an instrument name wins; then a voice name, or a part the pipeline read as vocal
  if (!(VOICE_RE.test(n) && !NAME_GM.some(([re]) => re.test(n)))) for (const [re, p] of NAME_GM) if (re.test(n)) return { program: p, family: gmFamily(p) };
  if (VOICE_RE.test(n) || ctx.kind === 'vocal') return { program: (ctx.vocalParts || 1) <= 1 || /solo/i.test(n) ? 53 : 52, family: 'voice' };
  return { program: 0, family: 'piano' };
}
const escX = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// MIDI channel (1-based, 10 kept for drums) and pan of part i of n
function channelFor(i, drums) { if (drums) return 10; const c = (i % 15) + 1; return c >= 10 ? c + 1 : c; }
function panFor(i, n, family) { if (n <= 1 || family === 'piano' || family === 'organ') return 0; return Math.round(-40 + (80 * i) / (n - 1)); }
// <score-instrument> + <midi-instrument> for a <score-part> (after part-name / part-abbreviation, as the schema orders them)
// ctx.kit: a drum kit ([{id, name, key}], percussion.js): one instrument per drum on channel 10,
// its General MIDI key as <midi-unpitched> (1-based)
function instrumentXML(part, i, n, ctx = {}) {
  if (ctx.kit) {
    return ctx.kit.map((k) => `<score-instrument id="${part.id}-${k.id}"><instrument-name>${escX(k.name)}</instrument-name></score-instrument>`).join('') +
      ctx.kit.map((k) => `<midi-instrument id="${part.id}-${k.id}"><midi-channel>10</midi-channel><midi-unpitched>${k.key + 1}</midi-unpitched><volume>80</volume><pan>${panFor(i, n, 'drums')}</pan></midi-instrument>`).join('');
  }
  const g = gmFor(part.name, { vocalParts: ctx.vocalParts, kind: part.kind });
  const id = `${part.id}-I1`;
  const drums = g.program < 0;
  const name = drums ? 'Percussion' : GM[g.program];
  const midi = drums ? `<midi-channel>10</midi-channel>` : `<midi-channel>${channelFor(i, false)}</midi-channel><midi-program>${g.program + 1}</midi-program>`;
  return `<score-instrument id="${id}"><instrument-name>${escX(name)}</instrument-name></score-instrument>` +
    `<midi-instrument id="${id}">${midi}<volume>80</volume><pan>${panFor(i, n, g.family)}</pan></midi-instrument>`;
}

// ------------------------------------------------------------ tempo text ---
// qpm for tempo words (longest / most specific first); "Not fast" is the rag's marking
const TEMPO_WORDS = [
  [/prestissimo/i, 200], [/presto/i, 176], [/vivacissimo/i, 172], [/vivace|vivo\b/i, 156], [/allegro\s+(ma\s+non\s+troppo|moderato)/i, 120], [/allegro\s+(assai|molto)|molto\s+allegro/i, 152],
  [/allegretto/i, 112], [/allegro/i, 132], [/tempo di (valse|valzer)|valse|waltz/i, 150], [/tempo di marcia|marcia|march|alla marcia/i, 112],
  [/moderato|moderately|moderate/i, 104], [/maestoso/i, 84], [/andantino/i, 88], [/andante/i, 80], [/adagietto/i, 72], [/adagio/i, 66],
  [/larghetto/i, 60], [/lento|slowly|slow\b/i, 56], [/largo|grave/i, 46],
  [/not (too )?fast|non troppo|tempo di rag|ragtime/i, 80], [/quickly|fast|lively|briskly|bright/i, 140], [/gently|tenderly|expressively|with feeling/i, 76],
];
const tempoFromWords = (s) => { for (const [re, q] of TEMPO_WORDS) if (re.test(s)) return q; return 0; };
const BEATQ = { maxima: 32, long: 16, breve: 8, whole: 4, half: 2, quarter: 1, eighth: 0.5, '16th': 0.25, '32nd': 0.125, '64th': 0.0625 };
// dynamics -> velocity
const DYN_VEL = { pppppp: 8, ppppp: 12, pppp: 18, ppp: 26, pp: 38, p: 52, mp: 66, mf: 80, f: 96, ff: 110, fff: 120, ffff: 124, fffff: 126, ffffff: 127 };
const ACCENT_DYN = { sf: 18, sfz: 20, sffz: 24, fz: 18, rfz: 14, rf: 12, sfp: 18, sfpp: 18, fp: 14, sfzp: 20 };
// before the first marking: between mp and mf, so a first mf is still heard as a change
const DEFAULT_VEL = 72;
// <sound dynamics> for a marking: % of the default forte (MusicXML; MuseScore reads velocity = dynamics x 90 / 100)
const soundDynamics = (v) => { const x = DYN_VEL[String(v || '').toLowerCase()]; return x == null ? null : Math.round((x * 10000) / 90) / 100; };

// --------------------------------------------------------------- events ---
const STEP = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const EPS = 1e-6;

// One source measure of one part: notes and marks with offsets in quarters.
function readMeasure(meas, st) {
  const notes = [], marks = [];
  let cur = 0, maxPos = 0, lastOnset = 0, lastDur = 0;
  const graceQ = [];
  for (const el of meas.children) {
    if (el.name === 'attributes') {
      const d = txt(el, 'divisions'); if (d) st.div = +d || st.div;
      const t = kid(el, 'time'); if (t && txt(t, 'beats')) { st.beats = +txt(t, 'beats').split('+').reduce((a, b) => a + +b, 0) || st.beats; st.beatType = +txt(t, 'beat-type') || st.beatType; }
      const tr = kid(el, 'transpose'); if (tr) st.transpose = (+txt(tr, 'chromatic') || 0) + 12 * (+txt(tr, 'octave-change') || 0);
      const stv = txt(el, 'staves'); if (stv) st.staves = +stv;
    } else if (el.name === 'backup') { cur -= (+txt(el, 'duration') || 0) / st.div; if (cur < 0) cur = 0; }
    else if (el.name === 'forward') { cur += (+txt(el, 'duration') || 0) / st.div; maxPos = Math.max(maxPos, cur); }
    else if (el.name === 'direction') {
      const off = cur + (+txt(el, 'offset') || 0) / st.div;
      const staff = +txt(el, 'staff') || 0;
      for (const dt of kids(el, 'direction-type')) {
        for (const c of dt.children) {
          if (c.name === 'dynamics') for (const d of c.children) marks.push({ kind: 'dyn', q: off, staff, v: d.name === 'other-dynamics' ? d.text.trim() : d.name });
          else if (c.name === 'wedge') marks.push({ kind: 'wedge', q: off, staff, v: c.attrs.type, num: c.attrs.number || '1' });
          else if (c.name === 'metronome') {
            const units = kids(c, 'beat-unit').map((u) => BEATQ[u.text.trim()] || 1);
            const dots = kids(c, 'beat-unit-dot').length;
            const pm = parseFloat(txt(c, 'per-minute'));
            if (units.length === 1 && pm > 0) marks.push({ kind: 'tempo', q: off, v: pm * units[0] * (dots ? 1.5 : 1), src: 'metronome' });
          } else if (c.name === 'words') marks.push({ kind: 'words', q: off, staff, v: c.text.trim() });
          else if (c.name === 'segno') marks.push({ kind: 'segno', q: off });
          else if (c.name === 'coda') marks.push({ kind: 'coda', q: off });
        }
      }
      const snd = kid(el, 'sound'); if (snd) marks.push({ kind: 'sound', q: off, staff, a: snd.attrs });
    } else if (el.name === 'sound') marks.push({ kind: 'sound', q: cur, a: el.attrs });
    else if (el.name === 'barline') {
      const loc = el.attrs.location || 'right';
      const rep = kid(el, 'repeat');
      if (rep) marks.push({ kind: 'repeat', loc, dir: rep.attrs.direction, times: +rep.attrs.times || 0 });
      const end = kid(el, 'ending');
      if (end) marks.push({ kind: 'ending', loc, type: end.attrs.type, nums: String(end.attrs.number || '1').split(/[\s,]+/).filter(Boolean).map(Number) });
      if (kid(el, 'fermata')) marks.push({ kind: 'fermata-bar', loc });
      if (kid(el, 'segno')) marks.push({ kind: 'segno', q: 0 });
      if (kid(el, 'coda')) marks.push({ kind: 'coda', q: 0 });
      const snd = kid(el, 'sound'); if (snd) marks.push({ kind: 'sound', q: loc === 'left' ? 0 : Infinity, a: snd.attrs });
    } else if (el.name === 'note') {
      const chord = !!kid(el, 'chord'), grace = kid(el, 'grace'), rest = kid(el, 'rest'), cue = !!kid(el, 'cue');
      const dq = (+txt(el, 'duration') || 0) / st.div;
      const onset = chord ? lastOnset : cur;
      const voice = txt(el, 'voice') || '1', staff = +txt(el, 'staff') || 1;
      const nots = kid(el, 'notations');
      const fermata = !!(nots && kid(nots, 'fermata'));
      if (fermata) marks.push({ kind: 'fermata', q: onset, dq: dq || 1 });
      if (!rest && !cue) {
        const p = kid(el, 'pitch'), un = kid(el, 'unpitched');
        let midi = null, drum = false;
        if (p) midi = 12 * ((+txt(p, 'octave')) + 1) + (STEP[txt(p, 'step')] || 0) + Math.round(+txt(p, 'alter') || 0) + (st.transpose || 0);
        else if (un) {
          // the note's drum: its <instrument> (a kit's midi-unpitched), else the part's, else a snare
          const ins = kid(el, 'instrument'), k = ins && st.drumKeys ? st.drumKeys[ins.attrs.id] : null;
          drum = true; midi = k != null ? k : st.drumNote != null ? st.drumNote : 38;
        }
        if (midi != null && midi >= 0 && midi <= 127) {
          const ties = kids(el, 'tie').map((t) => t.attrs.type).concat(nots ? kids(nots, 'tied').map((t) => t.attrs.type) : []);
          const art = nots ? kid(nots, 'articulations') : null;
          const n = { midi, q: onset, dq, staff, voice, line: el.line, drum, tieStart: ties.includes('start'), tieStop: ties.includes('stop'), fermata,
            stacc: !!(art && (kid(art, 'staccato') || kid(art, 'spiccato'))), staccatissimo: !!(art && kid(art, 'staccatissimo')),
            accent: art ? (kid(art, 'strong-accent') ? 18 : kid(art, 'accent') ? 12 : 0) : 0, tenuto: !!(art && kid(art, 'tenuto')),
            dyn: el.attrs.dynamics != null ? +el.attrs.dynamics : null };
          if (grace) { n.grace = grace.attrs.slash === 'yes' ? 'before' : 'on'; n.dq = 0; graceQ.push(n); }
          else {
            n.graces = chord ? [] : graceQ.splice(0);
            notes.push(n);
          }
        }
      }
      if (!grace) {
        if (!chord) { lastOnset = cur; lastDur = dq; cur += dq; } else if (dq > lastDur) { /* longer chord tone: cursor follows the first */ }
        maxPos = Math.max(maxPos, cur, onset + dq);
      }
    }
  }
  return { notes, marks, len: maxPos };
}

// Play order of source measures: repeats (with voltas) and D.C. / D.S. jumps.
function playOrder(info) {
  const M = info.length;
  const out = [];
  let i = 0, start = 0, pass = 1, jumped = false, back = false;
  const lastEndingOf = (j) => { // is the volta starting at j the last one of its group?
    let k = j; while (k < M && !info[k].endingStop) k++;
    return !(k + 1 < M && info[k + 1].endingStart);
  };
  let guard = 0;
  while (i < M && guard++ < 20000) {
    const m = info[i];
    if (m.forward && !back) { start = i; pass = 1; }
    back = false;
    if (m.endingStart) {
      const play = jumped ? lastEndingOf(i) : m.endingNums.includes(pass) || (pass > Math.max(...m.endingNums) && lastEndingOf(i) && !m.endingNums.some((x) => x > pass));
      if (!play) { // skip to after this volta's end
        let k = i; while (k < M - 1 && !info[k].endingStop) k++;
        i = k + 1; continue;
      }
    }
    out.push(i);
    if (jumped && m.fine) break;
    if (jumped && m.tocoda) {
      let k = i + 1; while (k < M && !info[k].codaSign) k++;
      if (k < M) { i = k; continue; }
    }
    if (m.backward && !jumped) {
      const times = m.times || Math.max(2, ...(m.endingStop ? m.endingNums.map((x) => x + 1) : [2]));
      if (pass < times) { pass++; i = start; back = true; continue; }
      pass = 1; start = i + 1;
    } else if (m.backward && jumped && !info.noRepeatAfterJump) { /* repeats are not taken again after a jump */ }
    if (m.dacapo && !info.dcDone) { info.dcDone = true; jumped = true; i = 0; start = 0; pass = 1; continue; }
    if (m.dalsegno && !info.dsDone) {
      info.dsDone = true; jumped = true;
      let k = i; while (k >= 0 && !info[k].segno) k--;
      i = Math.max(0, k); start = i; pass = 1; continue;
    }
    i++;
  }
  return out;
}

function events(xml, opts = {}) {
  const doc = parseXML(xml);
  const sp = findOne(doc, 'score-partwise');
  if (!sp) throw new Error('no score-partwise root');
  const title = txt(kid(sp, 'work'), 'work-title') || txt(sp, 'movement-title') || '';
  const pl = kid(sp, 'part-list');
  const spEls = pl ? kids(pl, 'score-part') : [];
  const partEls = kids(sp, 'part');
  const nameOf = {}; const midiOf = {}; const drumKeysOf = {};
  for (const s of spEls) {
    nameOf[s.attrs.id] = txt(s, 'part-name');
    const mi = kid(s, 'midi-instrument'), un = mi && kid(mi, 'midi-unpitched');
    // every drum of a kit (one midi-instrument per score-instrument)
    for (const m of kids(s, 'midi-instrument')) { const u = kid(m, 'midi-unpitched'); if (u) (drumKeysOf[s.attrs.id] ||= {})[m.attrs.id] = +u.text - 1; }
    if (mi) midiOf[s.attrs.id] = { channel: +txt(mi, 'midi-channel') || 0, program: txt(mi, 'midi-program') ? +txt(mi, 'midi-program') - 1 : null, volume: txt(mi, 'volume') ? +txt(mi, 'volume') : null, pan: txt(mi, 'pan') ? +txt(mi, 'pan') : null, unpitched: un ? +un.text - 1 : null };
  }
  const vocalParts = partEls.filter((p) => { const n = nameOf[p.attrs.id] || ''; return !NAME_GM.some(([re]) => re.test(n)) && VOICE_RE.test(n); }).length;

  // read every part's measures
  const parts = partEls.map((p, pi) => {
    const id = p.attrs.id;
    const st = { div: 1, beats: 4, beatType: 4, transpose: 0, staves: 1, drumNote: midiOf[id] && midiOf[id].unpitched != null ? midiOf[id].unpitched : null, drumKeys: drumKeysOf[id] || null };
    const meas = kids(p, 'measure').map((m) => { const r = readMeasure(m, st); r.number = m.attrs.number || ''; r.timeQ = (st.beats * 4) / st.beatType; r.beats = st.beats; r.beatType = st.beatType; return r; });
    const g = gmFor(nameOf[id], { vocalParts });
    const mo = midiOf[id] || {};
    const program = mo.program != null ? mo.program : g.program;
    const drums = program < 0 || mo.channel === 10 || meas.some((m) => m.notes.some((n) => n.drum));
    return { id, name: nameOf[id] || `Part ${pi + 1}`, program: drums ? -1 : program, family: drums ? 'drums' : gmFamily(program), channel: (mo.channel || channelFor(pi, drums)) - 1,
      volume: mo.volume != null ? mo.volume : 80, pan: mo.pan != null ? mo.pan : panFor(pi, partEls.length, gmFamily(program)), meas };
  });
  const M = Math.max(0, ...parts.map((p) => p.meas.length));
  // measure lengths and structure (from all parts)
  const info = [];
  for (let mi = 0; mi < M; mi++) {
    const ms = parts.map((p) => p.meas[mi]).filter(Boolean);
    const len = Math.max(0, ...ms.map((m) => m.len));
    const timeQ = ms.length ? ms[0].timeQ : 4;
    const r = { len: len > EPS ? len : timeQ, number: ms.length ? ms[0].number : String(mi + 1), beats: ms.length ? ms[0].beats : 4, beatType: ms.length ? ms[0].beatType : 4, marks: [] };
    for (const m of ms) for (const k of m.marks) {
      r.marks.push(k);
      if (k.kind === 'repeat' && k.dir === 'forward') r.forward = true;
      if (k.kind === 'repeat' && k.dir === 'backward') { r.backward = true; r.times = Math.max(r.times || 0, k.times); }
      if (k.kind === 'ending' && k.type === 'start') { r.endingStart = true; r.endingNums = k.nums; }
      if (k.kind === 'ending' && (k.type === 'stop' || k.type === 'discontinue')) { r.endingStop = true; r.endingNums = r.endingNums || k.nums; }
      if (k.kind === 'segno') r.segno = true;
      if (k.kind === 'coda') r.codaSign = true;
      if (k.kind === 'sound') {
        const a = k.a;
        if (a.segno) r.segno = true;
        if (a.coda) r.codaSign = true;
        if (a.tocoda) r.tocoda = true;
        if (a.fine != null) r.fine = true;
        if (a.dacapo === 'yes') r.dacapo = true;
        if (a.dalsegno) r.dalsegno = true;
      }
      if (k.kind === 'words') {
        const w = k.v;
        if (/^\s*fine\.?\s*$/i.test(w)) r.fine = true;
        else if (/to\s+coda|al\s+coda\s*$/i.test(w) && !/d\.?\s*[cs]\.?/i.test(w)) r.tocoda = true;
        else if (/\bd\.?\s?c\.?(\s|$)|da\s+capo/i.test(w)) r.dacapo = true;
        else if (/\bd\.?\s?s\.?(\s|$)|dal\s+segno/i.test(w)) r.dalsegno = true;
        else if (/^\s*coda\s*$/i.test(w)) r.codaSign = true;
      }
    }
    // a "To Coda" sign measure whose <coda/> sign is the jump, not the target
    if (r.tocoda) r.codaSign = false;
    info.push(r);
  }
  const order = opts.noRepeats ? info.map((_, i) => i) : playOrder(info);

  // timeline in quarters
  const measures = [];
  let Q = 0;
  for (const src of order) { measures.push({ src, number: info[src].number, q0: Q, q1: Q + info[src].len }); Q += info[src].len; }
  const totalQ = Q;

  // tempo points (step changes) and fermata holds, in played quarters
  const defaultBpm = opts.defaultBpm || 100;
  const tp = []; // {q, bpm, kind}
  let firstBpm = 0, lastSteady = 0;
  const fermatas = [];
  measures.forEach((pm) => {
    const r = info[pm.src];
    for (const k of r.marks) {
      const q = pm.q0 + Math.min(k.q || 0, r.len);
      if (k.kind === 'sound' && k.a.tempo && +k.a.tempo > 0) tp.push({ q, bpm: +k.a.tempo, kind: 'set' });
      else if (k.kind === 'tempo') tp.push({ q, bpm: k.v, kind: 'set', weak: true });
      else if (k.kind === 'words') {
        const w = k.v;
        if (/\b(rit|ritard|rall|rallent|riten|allarg)/i.test(w)) tp.push({ q, kind: 'rit' });
        else if (/a\s+tempo/i.test(w)) tp.push({ q, kind: 'atempo' });
        else if (/tempo\s+(i|1|primo)\b/i.test(w)) tp.push({ q, kind: 'tempo1' });
        else { const b = tempoFromWords(w); if (b) tp.push({ q, bpm: b, kind: 'set', weak: true, words: true }); }
      } else if (k.kind === 'fermata') fermatas.push([q, q + Math.max(0.25, k.dq)]);
      else if (k.kind === 'fermata-bar') { const qq = k.loc === 'left' ? pm.q0 : pm.q1; fermatas.push([qq - 0.5, qq]); }
    }
  });
  // one tempo per position: <sound tempo> beats a metronome mark beats words
  tp.sort((a, b) => a.q - b.q || (a.weak ? 1 : 0) - (b.weak ? 1 : 0) || (a.words ? 1 : 0) - (b.words ? 1 : 0));
  const steps = []; // {q, bpm}
  let cur = 0;
  for (const t of tp) {
    if (steps.length && Math.abs(steps[steps.length - 1].q - t.q) < EPS && t.kind === 'set' && steps[steps.length - 1].kind === 'set') continue;
    if (t.kind === 'set') { cur = t.bpm; if (!firstBpm) firstBpm = cur; lastSteady = cur; steps.push({ q: t.q, bpm: cur, kind: 'set' }); }
    else if (t.kind === 'rit') { const b = (cur || defaultBpm) * 0.82; steps.push({ q: t.q, bpm: b, kind: 'rit' }); cur = b; }
    else if (t.kind === 'atempo') { cur = lastSteady || firstBpm || defaultBpm; steps.push({ q: t.q, bpm: cur, kind: 'set' }); }
    else if (t.kind === 'tempo1') { cur = firstBpm || defaultBpm; lastSteady = cur; steps.push({ q: t.q, bpm: cur, kind: 'set' }); }
  }
  const startBpm = steps.length && steps[0].q < EPS ? steps[0].bpm : (opts.fallbackFirst !== false && firstBpm ? firstBpm : defaultBpm);
  if (!steps.length || steps[0].q > EPS) steps.unshift({ q: 0, bpm: startBpm, kind: 'set' });
  // segments with fermata holds folded in (2/3 speed: a held note lasts 1.5x)
  const cuts = new Set([0, totalQ]);
  steps.forEach((s) => cuts.add(s.q));
  const ferm = mergeSpans(fermatas.filter(([a, b]) => b > a));
  ferm.forEach(([a, b]) => { cuts.add(a); cuts.add(b); });
  const qs = [...cuts].filter((q) => q >= 0 && q <= totalQ + EPS).sort((a, b) => a - b);
  const tempos = []; // {q, bpm, t}
  let t = 0, si = 0;
  for (let k = 0; k < qs.length; k++) {
    const q = qs[k];
    while (si + 1 < steps.length && steps[si + 1].q <= q + EPS) si++;
    const held = ferm.some(([a, b]) => q >= a - EPS && q < b - EPS);
    const bpm = steps[si].bpm * (held ? 2 / 3 : 1);
    if (!tempos.length || Math.abs(tempos[tempos.length - 1].bpm - bpm) > 1e-9) tempos.push({ q, bpm, t });
    if (k + 1 < qs.length) t += ((qs[k + 1] - q) * 60) / bpm;
  }
  const secAt = (q) => {
    let lo = 0, hi = tempos.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (tempos[mid].q <= q + EPS) lo = mid; else hi = mid - 1; }
    const s = tempos[lo];
    return s.t + ((q - s.q) * 60) / s.bpm;
  };
  measures.forEach((m) => { m.t0 = secAt(m.q0); m.t1 = secAt(m.q1); });

  // notes per part, with dynamics, wedges, ties and grace timing
  const shown = []; // dynamic markings as written, for the player's display: {q, part, staff, v}
  const outParts = parts.map((p, pi) => {
    const notes = [];
    const dynPts = []; // {q, vel} step changes
    const wedges = []; // {q0, q1, dir}
    const accents = []; // {q, add}
    let openW = null, openWords = null;
    measures.forEach((pm, idx) => {
      const ms = p.meas[pm.src];
      if (!ms) return;
      for (const k of ms.marks) {
        const q = pm.q0 + Math.min(k.q || 0, info[pm.src].len);
        if (k.kind === 'dyn') {
          const v = k.v.toLowerCase();
          const staff = k.staff || 0;
          if (DYN_VEL[v] != null || ACCENT_DYN[v] != null) shown.push({ q, part: pi, staff, v });
          if (DYN_VEL[v] != null) dynPts.push({ q, vel: DYN_VEL[v], staff });
          else if (ACCENT_DYN[v] != null) { accents.push({ q, add: ACCENT_DYN[v], staff }); if (v === 'fp' || v === 'sfp' || v === 'sfzp') dynPts.push({ q: q + 0.25, vel: DYN_VEL.p, staff }); if (v === 'sfpp') dynPts.push({ q: q + 0.25, vel: DYN_VEL.pp, staff }); }
        } else if (k.kind === 'sound' && k.a.dynamics != null && +k.a.dynamics >= 0) dynPts.push({ q, vel: Math.max(1, Math.min(127, Math.round((+k.a.dynamics * 90) / 100))), weak: true, staff: k.staff || 0 });
        else if (k.kind === 'wedge') {
          if (k.v === 'crescendo' || k.v === 'diminuendo') openW = { q0: q, dir: k.v === 'crescendo' ? 1 : -1, staff: k.staff || 0 };
          else if (k.v === 'stop' && openW) { wedges.push({ q0: openW.q0, q1: Math.max(q, openW.q0 + 0.25), dir: openW.dir, staff: openW.staff }); openW = null; }
        } else if (k.kind === 'words') {
          if (/^\s*(cresc|crescendo|poco a poco cresc)/i.test(k.v)) openWords = { q0: q, dir: 1 };
          else if (/^\s*(dim|decresc|diminuendo|morendo|smorz)/i.test(k.v)) openWords = { q0: q, dir: -1 };
          if (openWords && openWords.q0 === q) wedges.push({ q0: q, q1: Math.min(totalQ, q + 2 * info[pm.src].len), dir: openWords.dir, words: true, staff: k.staff || 0 });
        }
      }
      for (const n of ms.notes) notes.push({ ...n, q: pm.q0 + n.q, m: idx });
    });
    if (openW) wedges.push({ q0: openW.q0, q1: Math.min(totalQ, openW.q0 + 4), dir: openW.dir, staff: openW.staff });
    dynPts.sort((a, b) => a.q - b.q);
    // Staff scope in a multi-staff part (piano): a mark with no <staff>, or marks on one
    // staff only, apply to the whole part (a mark under the left hand means both hands);
    // when two or more staves carry their own marks, each staff follows its own.
    const marked = new Set(dynPts.concat(wedges, accents).map((d) => d.staff).filter((x) => x > 0));
    const perStaff = marked.size >= 2;
    const on = (d, staff) => !perStaff || !d.staff || d.staff === staff;
    const baseVel = (q, staff) => { let v = DEFAULT_VEL; for (const d of dynPts) { if (d.q > q + EPS) break; if (on(d, staff)) v = d.vel; } return v; };
    const nextDyn = (q, within, staff) => dynPts.find((d) => d.q > q - EPS && d.q <= within + EPS && on(d, staff));
    const velAt = (q, staff) => {
      let v = baseVel(q, staff);
      for (const w of wedges) {
        if (!on(w, staff) || q < w.q0 - EPS || q > w.q1 + 4) continue;
        const from = baseVel(w.q0, staff);
        const nd = nextDyn(w.q1, w.q1 + 2.5, staff);
        const to = nd && Math.sign(nd.vel - from) === w.dir ? nd.vel : Math.max(20, Math.min(124, from + 18 * w.dir));
        if (q <= w.q1 + EPS) { if (!nd || nd.q > q + EPS) v = from + (to - from) * ((q - w.q0) / Math.max(EPS, w.q1 - w.q0)); }
        else if (!nd || nd.q > q + EPS) { if (baseVel(q, staff) === from) v = to; }
      }
      return v;
    };
    // ties: extend the open note of the same pitch (and staff) that ends where this one starts
    notes.sort((a, b) => a.q - b.q || a.midi - b.midi);
    const open = new Map(), kept = []; // pitch:staff -> notes whose tie is open
    for (const n of notes) {
      const key = n.midi + ':' + n.staff;
      const cands = (open.get(key) || []).filter((o) => Math.abs(o.q + o.dq - n.q) < 0.02);
      const o = n.tieStop && (cands.find((c) => c.voice === n.voice) || cands[0]);
      if (o) {
        o.dq = n.q + n.dq - o.q; o.lines.push(n.line); o.fermata = o.fermata || n.fermata;
        if (!n.tieStart) open.set(key, open.get(key).filter((c) => c !== o));
        continue;
      }
      n.lines = [n.line];
      kept.push(n);
      if (n.tieStart) open.set(key, (open.get(key) || []).filter((c) => c.q + c.dq > n.q - 0.02).concat([n]));
    }
    // grace notes: a short value stolen from the principal (on the beat) or the time before it (slashed)
    const res = [];
    for (const n of kept) {
      const gs = n.graces || [];
      if (gs.length) {
        const g = Math.min(0.125, n.dq / (gs.length + 1) / 2);
        gs.forEach((gn, j) => {
          const q = gn.grace === 'before' ? n.q - g * (gs.length - j) : n.q + g * j;
          res.push({ ...gn, q: Math.max(0, q), dq: g, m: n.m, lines: [gn.line], graceOf: true });
        });
        if (gs[0].grace === 'on') { n.q += g * gs.length; n.dq -= g * gs.length; }
      }
      res.push(n);
    }
    const out = res.map((n) => {
      const t0 = secAt(n.q);
      let dq = n.dq;
      if (n.stacc) dq *= 0.5; else if (n.staccatissimo) dq *= 0.3; else if (!n.tenuto && !n.graceOf && p.family !== 'organ') dq = Math.max(dq - Math.min(0.06, dq * 0.1), dq * 0.9);
      const t1 = secAt(n.q + dq);
      let vel = velAt(n.q, n.staff) + (n.accent || 0);
      for (const a of accents) if (Math.abs(a.q - n.q) < 0.05 && on(a, n.staff)) vel += a.add;
      if (n.dyn != null) vel = (n.dyn * 90) / 100;
      if (n.graceOf) vel *= 0.85;
      return { part: pi, staff: n.staff, voice: n.voice, midi: n.midi, q: n.q, dq: n.dq, t: t0, d: Math.max(0.02, t1 - t0), vel: Math.max(1, Math.min(127, Math.round(vel))),
        line: n.line, lines: n.lines || [n.line], m: n.m, grace: !!n.graceOf };
    });
    out.sort((a, b) => a.t - b.t || a.midi - b.midi);
    return { id: p.id, name: p.name, program: p.program, family: p.family, channel: p.channel, volume: p.volume, pan: p.pan, perStaffDynamics: perStaff, notes: out };
  });

  // metronome beats (compound meters beat in dotted quarters)
  const beats = [];
  measures.forEach((pm, idx) => {
    const r = info[pm.src];
    const compound = r.beatType >= 8 && r.beats % 3 === 0 && r.beats > 3;
    const bq = compound ? (12 / r.beatType) : 4 / r.beatType;
    for (let q = 0, k = 0; q < r.len - EPS; q += bq, k++) beats.push({ q: pm.q0 + q, t: secAt(pm.q0 + q), down: k === 0, m: idx });
  });
  const timeSigs = [];
  measures.forEach((pm) => { const r = info[pm.src], l = timeSigs[timeSigs.length - 1]; if (!l || l.beats !== r.beats || l.beatType !== r.beatType) timeSigs.push({ q: pm.q0, beats: r.beats, beatType: r.beatType }); });
  const dynamics = shown.sort((a, b) => a.q - b.q).map((d) => ({ ...d, t: secAt(d.q) }));
  return { title, parts: outParts, measures, tempos, beats, timeSigs, dynamics, quarters: totalQ, duration: secAt(totalQ), secAt, order, startBpm: tempos.length ? tempos[0].bpm : defaultBpm };
}
function mergeSpans(sp) {
  const s = sp.slice().sort((a, b) => a[0] - b[0]), out = [];
  for (const x of s) { const l = out[out.length - 1]; if (l && x[0] <= l[1] + EPS) l[1] = Math.max(l[1], x[1]); else out.push([x[0], x[1]]); }
  return out;
}

// Bpm of the first tempo mark, words or metronome, for the UI's "written tempo"
const firstTempo = (model) => model.startBpm;

// ------------------------------------------------------------------ SMF ---
const PPQ = 480;
function vlq(n) { const b = [n & 0x7f]; while ((n >>= 7)) b.unshift((n & 0x7f) | 0x80); return b; }
function trackChunk(evs) {
  // evs: [{tick, data: [bytes], order}] -> MTrk bytes
  evs.sort((a, b) => a.tick - b.tick || a.order - b.order);
  const body = [];
  let last = 0;
  for (const e of evs) { body.push(...vlq(Math.max(0, e.tick - last)), ...e.data); last = Math.max(last, e.tick); }
  body.push(0, 0xff, 0x2f, 0);
  return [0x4d, 0x54, 0x72, 0x6b, (body.length >>> 24) & 255, (body.length >>> 16) & 255, (body.length >>> 8) & 255, body.length & 255, ...body];
}
const textBytes = (s) => { const out = []; for (const ch of String(s)) { const c = ch.codePointAt(0); out.push(c < 128 ? c : 63); } return out; };
// model: events() result; opts.parts: per-part overrides [{program, volume (0-127), pan (-64..63), mute}]
function writeSMF(model, opts = {}) {
  const ov = opts.parts || [];
  const tick = (q) => Math.round(q * PPQ);
  const t0 = [];
  if (model.title) { const tb = textBytes(model.title); t0.push({ tick: 0, order: 0, data: [0xff, 0x03, ...vlq(tb.length), ...tb] }); }
  // time signature at each played measure whose meter changes
  for (const ts of model.timeSigs || []) t0.push({ tick: tick(ts.q), order: 1, data: [0xff, 0x58, 4, ts.beats & 255, Math.round(Math.log2(ts.beatType)), 24, 8] });
  for (const tp of model.tempos) {
    const us = Math.round(60000000 / tp.bpm);
    t0.push({ tick: tick(tp.q), order: 2, data: [0xff, 0x51, 3, (us >> 16) & 255, (us >> 8) & 255, us & 255] });
  }
  const tracks = [trackChunk(t0)];
  model.parts.forEach((p, i) => {
    const o = ov[i] || {};
    if (o.mute) return;
    const ch = p.program < 0 ? 9 : p.channel & 15;
    const prog = o.program != null ? o.program : p.program;
    const evs = [];
    const nb = textBytes(p.name);
    evs.push({ tick: 0, order: 0, data: [0xff, 0x03, ...vlq(nb.length), ...nb] });
    if (prog >= 0 && ch !== 9) evs.push({ tick: 0, order: 1, data: [0xc0 | ch, prog & 127] });
    const vol = o.volume != null ? o.volume : Math.round(((p.volume != null ? p.volume : 80) * 127) / 100);
    evs.push({ tick: 0, order: 2, data: [0xb0 | ch, 7, Math.max(0, Math.min(127, vol))] });
    const pan = Math.max(0, Math.min(127, 64 + Math.round(((o.pan != null ? o.pan : p.pan || 0) * 63) / 90)));
    evs.push({ tick: 0, order: 3, data: [0xb0 | ch, 10, pan] });
    for (const n of p.notes) {
      const a = tick(n.q), b = Math.max(a + 1, tick(n.q + Math.max(n.dq, 0.0625) * (n.grace ? 1 : 0.98)));
      evs.push({ tick: a, order: 5, data: [0x90 | ch, n.midi, n.vel] });
      evs.push({ tick: b, order: 4, data: [0x80 | ch, n.midi, 0] });
    }
    tracks.push(trackChunk(evs));
  });
  const head = [0x4d, 0x54, 0x68, 0x64, 0, 0, 0, 6, 0, 1, (tracks.length >> 8) & 255, tracks.length & 255, (PPQ >> 8) & 255, PPQ & 255];
  const all = head.concat(...tracks);
  return Uint8Array.from(all);
}
function readSMF(bytes) {
  const b = bytes instanceof Uint8Array ? bytes : Uint8Array.from(bytes);
  let i = 0;
  const u32 = () => { const v = (b[i] << 24) | (b[i + 1] << 16) | (b[i + 2] << 8) | b[i + 3]; i += 4; return v >>> 0; };
  const u16 = () => { const v = (b[i] << 8) | b[i + 1]; i += 2; return v; };
  const str = (n) => { let s = ''; for (let k = 0; k < n; k++) s += String.fromCharCode(b[i + k]); i += n; return s; };
  const rv = () => { let v = 0, c; do { c = b[i++]; v = (v << 7) | (c & 0x7f); } while (c & 0x80); return v; };
  if (str(4) !== 'MThd') throw new Error('not a MIDI file');
  const hl = u32(); const format = u16(), ntr = u16(), ppq = u16(); i += hl - 6;
  const tracks = [];
  for (let k = 0; k < ntr; k++) {
    if (str(4) !== 'MTrk') throw new Error('bad track chunk');
    const len = u32(), end = i + len;
    const evs = []; let tick = 0, run = 0;
    while (i < end) {
      tick += rv();
      let st = b[i];
      if (st & 0x80) i++; else st = run;
      if (st === 0xff) { const type = b[i++]; const l = rv(); const data = b.slice(i, i + l); i += l; evs.push({ tick, type: 'meta', meta: type, data: Array.from(data) }); if (type === 0x2f) break; }
      else if (st === 0xf0 || st === 0xf7) { const l = rv(); i += l; }
      else {
        run = st; const hi = st & 0xf0, ch = st & 15;
        const d1 = b[i++], d2 = hi === 0xc0 || hi === 0xd0 ? 0 : b[i++];
        const type = hi === 0x90 && d2 > 0 ? 'on' : hi === 0x80 || hi === 0x90 ? 'off' : hi === 0xc0 ? 'program' : hi === 0xb0 ? 'cc' : 'other';
        evs.push({ tick, type, ch, a: d1, b: d2 });
      }
    }
    i = end;
    tracks.push(evs);
  }
  return { format, ppq, tracks };
}

module.exports = { parseXML, events, soundDynamics, DEFAULT_VEL, gmFor, gmFamily, instrumentXML, channelFor, panFor, writeSMF, readSMF, tempoFromWords, firstTempo, GM, DYN_VEL, PPQ };
