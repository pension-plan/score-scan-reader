// Playback model (src/playback.js): MusicXML -> timed note events, GM
// instruments, the Standard MIDI File writer (round trip through readSMF), and
// a sweep over every corpus truth file and produced output (they parse, timing
// is finite and ordered, ties merge to the expected count, every structure item
// plays in the order its meta.json describes).
//   node ui/test/playback.js
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const MVP = path.join(__dirname, '../..'), ROOT = path.join(MVP, '..');
const P = require(path.join(MVP, 'src/playback.js'));
const fails = [];
let checks = 0;
const ok = (c, t) => { checks++; if (!c) fails.push(t); };
const near = (a, b, e = 1e-6) => Math.abs(a - b) <= e;

// a one-part score from measure bodies (divisions 4)
const score = (measures, { name = 'Piano', parts } = {}) => {
  const ps = parts || [{ id: 'P1', name, measures }];
  return `<?xml version="1.0" encoding="UTF-8"?>\n<score-partwise version="4.0"><work><work-title>T</work-title></work><part-list>${ps.map((p) => `<score-part id="${p.id}"><part-name>${p.name}</part-name></score-part>`).join('')}</part-list>\n` +
    ps.map((p) => `<part id="${p.id}">\n${p.measures.map((m, i) => `<measure number="${i + 1}">${i === 0 ? '<attributes><divisions>4</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>' : ''}${m}</measure>`).join('\n')}\n</part>`).join('\n') + '\n</score-partwise>\n';
};
const n = (step, oct, dur, extra = '') => `<note>${extra.includes('<chord/>') ? '<chord/>' : ''}${extra.includes('<grace') ? extra.match(/<grace[^>]*\/>/)[0] : ''}<pitch><step>${step}</step><octave>${oct}</octave></pitch>${extra.includes('<grace') ? '' : `<duration>${dur}</duration>`}${extra.replace(/<chord\/>|<grace[^>]*\/>/g, '')}</note>`;
const r = (dur) => `<note><rest/><duration>${dur}</duration></note>`;
const notes = (m) => m.parts.flatMap((p) => p.notes);

// ---- basics: default tempo 100, quarters, a rest, chord
{
  const m = P.events(score([n('C', 4, 4) + r(4) + n('E', 4, 8) + n('G', 4, 8, '<chord/>')]));
  const ns = notes(m);
  ok(near(m.startBpm, 100), 'default tempo 100 qpm');
  ok(ns.length === 3, 'three notes (rest skipped)');
  ok(ns[0].midi === 60 && near(ns[0].t, 0) && near(ns[0].q, 0), 'C4 = 60 at 0');
  ok(near(ns[1].t, 1.2) && ns[1].midi === 64 && ns[2].midi === 67 && near(ns[2].t, 1.2), 'chord after a quarter rest at 2 beats = 1.2 s');
  ok(near(m.duration, 2.4), 'bar of 4/4 at 100 = 2.4 s');
  ok(ns[1].d < 1.2 && ns[1].d > 1.0, 'half note sounds slightly detached');
}
// ---- voices with backup / forward, dots and tuplets via duration, alter, transpose
{
  const m = P.events(score([n('C', 5, 6, '<voice>1</voice><dot/>') + n('D', 5, 2, '<voice>1</voice>') + n('E', 5, 8, '<voice>1</voice>') +
    '<backup><duration>16</duration></backup><forward><duration>4</duration></forward>' + n('F', 3, 4, '<voice>2</voice>') +
    `<note><pitch><step>F</step><alter>1</alter><octave>3</octave></pitch><duration>8</duration><voice>2</voice></note>`]));
  const ns = notes(m).sort((a, b) => a.q - b.q || a.midi - b.midi);
  ok(near(ns.find((x) => x.midi === 74).q, 1.5), 'dotted quarter then eighth (D5 at 1.5)');
  ok(ns.some((x) => x.midi === 53 && near(x.q, 1)), 'voice 2 after <forward> at beat 1');
  ok(ns.some((x) => x.midi === 54 && near(x.q, 2)), 'F#3 from <alter>');
  const t = P.events(score([`<note><pitch><step>C</step><octave>4</octave></pitch><duration>2</duration><time-modification><actual-notes>3</actual-notes><normal-notes>2</normal-notes></time-modification></note>`.repeat(1).replace('<duration>2</duration>', '<duration>4</duration>')]));
  ok(near(notes(t)[0].dq, 1), 'tuplets: the duration carries the time');
  const tr = P.events(score(['<attributes><transpose><diatonic>-1</diatonic><chromatic>-2</chromatic></transpose></attributes>' + n('D', 4, 16)], { name: 'Clarinet in B♭' }));
  ok(notes(tr)[0].midi === 60, 'transposing part sounds a tone lower');
  ok(tr.parts[0].program === 71, 'clarinet -> GM 72 (program 71)');
}
// ---- ties merge, also across a barline; grace notes
{
  const m = P.events(score([n('G', 4, 8) + n('A', 4, 8, '<tie type="start"/><notations><tied type="start"/></notations>'), n('A', 4, 8, '<tie type="stop"/><notations><tied type="stop"/></notations>') + n('B', 4, 8)]));
  const ns = notes(m);
  ok(ns.length === 3, `tie merged (3 notes, got ${ns.length})`);
  const a = ns.find((x) => x.midi === 69);
  ok(near(a.dq, 4) && a.lines.length === 2, 'tied A lasts 4 quarters and keeps both lines');
  const g = P.events(score([n('D', 5, 0, '<grace slash="yes"/>') + n('C', 5, 16)]));
  const gs = notes(g);
  ok(gs.length === 2 && gs.find((x) => x.grace) && gs.find((x) => x.grace).dq <= 0.125, 'grace note is short');
  const on = P.events(score([n('D', 5, 0, '<grace/>') + n('C', 5, 16)]));
  const pr = notes(on).find((x) => !x.grace);
  ok(pr.q > 0 && near(pr.q + pr.dq, 4), 'appoggiatura takes its time from the principal');
}
// ---- tempo: <sound tempo>, metronome, words ("Not fast", Allegro), rit. / a tempo, fermata
{
  const dir = (inner, extra = '') => `<direction placement="above"><direction-type>${inner}</direction-type>${extra}</direction>`;
  const s1 = P.events(score([dir('<words>Allegro</words>', '<sound tempo="66"/>') + n('C', 4, 16)]));
  ok(near(s1.startBpm, 66), '<sound tempo> beats the words');
  const s2 = P.events(score([dir('<metronome><beat-unit>half</beat-unit><per-minute>60</per-minute></metronome>') + n('C', 4, 16)]));
  ok(near(s2.startBpm, 120), 'half = 60 -> 120 qpm');
  const s3 = P.events(score([dir('<metronome><beat-unit>quarter</beat-unit><beat-unit-dot/><per-minute>60</per-minute></metronome>') + n('C', 4, 16)]));
  ok(near(s3.startBpm, 90), 'dotted quarter = 60 -> 90 qpm');
  const s4 = P.events(score([dir('<words>Not fast</words>') + n('C', 4, 16)]));
  ok(s4.startBpm >= 76 && s4.startBpm <= 84, `"Not fast" (the rag) -> ${s4.startBpm}`);
  ok(P.tempoFromWords('Allegro moderato') === 120 && P.tempoFromWords('Andante') === 80 && P.tempoFromWords('Tempo di marcia') === 112 && P.tempoFromWords('Var. 3  Presto') === 176, 'tempo words table');
  const s5 = P.events(score([dir('<words>Andante</words>') + n('C', 4, 16), dir('<words>rit.</words>') + n('C', 4, 16), dir('<words>a tempo</words>') + n('C', 4, 16)]));
  ok(s5.tempos.length === 3 && s5.tempos[1].bpm < 80 && near(s5.tempos[2].bpm, 80), 'rit. slows, a tempo restores');
  const f = P.events(score([n('C', 4, 4) + n('D', 4, 4, '<notations><fermata/></notations>') + n('E', 4, 8)]));
  const e = notes(f).find((x) => x.midi === 64);
  ok(near(e.t, 0.6 + 0.9), 'fermata holds its note 1.5x (later notes shift)');
}
// ---- dynamics and wedges -> velocity; accents
{
  const dir = (inner) => `<direction><direction-type>${inner}</direction-type></direction>`;
  const m = P.events(score([dir('<dynamics><p/></dynamics>') + n('C', 4, 4) + dir('<wedge type="crescendo"/>') + n('C', 4, 4) + n('C', 4, 4) + dir('<wedge type="stop"/>') + n('C', 4, 4), dir('<dynamics><f/></dynamics>') + n('C', 4, 4, '<notations><articulations><accent/></articulations></notations>') + n('C', 4, 4, '<notations><articulations><staccato/></articulations></notations>') + r(8)]));
  const v = notes(m).map((x) => x.vel);
  ok(v[0] === P.DYN_VEL.p, 'p -> velocity');
  ok(v[1] <= v[2] && v[2] < v[3] && v[3] <= P.DYN_VEL.f, `crescendo rises towards f (${v.slice(0, 5)})`);
  ok(v[4] === P.DYN_VEL.f + 12, 'accent adds to f');
  const st = notes(m)[5];
  ok(st.d < 0.35, 'staccato shortens');
}
// ---- repeats, voltas, D.C. al Fine, D.S. al Coda
{
  const L = (inner) => `<barline location="left">${inner}</barline>`, R = (inner) => `<barline location="right">${inner}</barline>`;
  const q = (s) => n(s, 4, 16);
  const m = P.events(score([q('C'), L('<ending number="1" type="start"/>') + q('D') + R('<ending number="1" type="stop"/><repeat direction="backward"/>'), L('<ending number="2" type="start"/>') + q('E') + R('<ending number="2" type="discontinue"/>'), q('F')]));
  ok(m.order.join(',') === '0,1,0,2,3', `voltas: ${m.order}`);
  ok(notes(m).length === 5 && near(m.duration, 12), 'repeat expanded in time');
  const dc = P.events(score([q('C'), q('D') + '<direction><direction-type><words>Fine</words></direction-type></direction>', q('E') + '<direction><direction-type><words>D.C. al Fine</words></direction-type></direction>']));
  ok(dc.order.join(',') === '0,1,2,0,1', `D.C. al Fine: ${dc.order}`);
  const ds = P.events(score([q('C'), '<direction><direction-type><segno/></direction-type><sound segno="s"/></direction>' + q('D'), q('E') + '<direction><direction-type><words>To Coda</words></direction-type><sound tocoda="c"/></direction>', q('F') + '<direction><direction-type><words>D.S. al Coda</words></direction-type><sound dalsegno="s"/></direction>', '<direction><direction-type><coda/></direction-type><sound coda="c"/></direction>' + q('G')]));
  ok(ds.order.join(',') === '0,1,2,3,1,2,4', `D.S. al Coda: ${ds.order}`);
  const nr = P.events(score([q('C') + R('<repeat direction="backward"/>')]), { noRepeats: true });
  ok(nr.order.join(',') === '0', 'noRepeats keeps the written order');
}
// ---- GM instruments from part names, instrument XML
{
  const t = [['Piano', 0], ['Organ', 19], ['Violin I', 40], ['Viola', 41], ['Violoncello', 42], ['Contrabass', 43], ['Flute', 73], ['Clarinet', 71], ['Trumpet in C', 56], ['Tuba', 58], ['Guitar', 24], ['Oboe', 68], ['Bassoon', 70], ['Horn in F', 60], ['Snare Drum', -1]];
  for (const [nm, p] of t) ok(P.gmFor(nm, { vocalParts: 0 }).program === p, `${nm} -> ${p} (got ${P.gmFor(nm).program})`);
  for (const nm of ['Soprano', 'Alto', 'Tenor', 'Bass', 'Chorus']) ok(P.gmFor(nm, { vocalParts: 4 }).program === 52, `${nm} in a choir -> Choir Aahs`);
  ok(P.gmFor('Voice', { vocalParts: 1 }).program === 53 && P.gmFor('Solo Voice', { vocalParts: 5 }).program === 53, 'solo voice -> Voice Oohs');
  const x = P.instrumentXML({ id: 'P2', name: 'Alto' }, 1, 4, { vocalParts: 4 });
  ok(/<score-instrument id="P2-I1"><instrument-name>Choir Aahs<\/instrument-name><\/score-instrument><midi-instrument id="P2-I1"><midi-channel>2<\/midi-channel><midi-program>53<\/midi-program><volume>80<\/volume><pan>-13<\/pan><\/midi-instrument>/.test(x), 'instrument XML ' + x);
  ok(P.channelFor(8) === 9 && P.channelFor(9) === 11, 'channel 10 left for drums');
  // the written instrument is what plays back
  const s = score([n('C', 4, 16)]).replace('<part-name>Piano</part-name>', '<part-name>Piano</part-name>' + P.instrumentXML({ id: 'P1', name: 'Flute' }, 0, 1));
  ok(P.events(s).parts[0].program === 73, 'midi-program read back');
}
// ---- SMF: write and read back
{
  const dir = (inner, extra = '') => `<direction><direction-type>${inner}</direction-type>${extra}</direction>`;
  const xml = score(null, { parts: [
    { id: 'P1', name: 'Soprano', measures: [dir('<words>Andante</words>') + n('E', 5, 8) + n('D', 5, 8), n('C', 5, 8, '<notations><fermata/></notations>') + r(8)] },
    { id: 'P2', name: 'Alto', measures: [n('C', 5, 16), n('G', 4, 8) + r(8)] }] });
  const m = P.events(xml);
  const smf = P.readSMF(P.writeSMF(m));
  ok(smf.format === 1 && smf.ppq === P.PPQ && smf.tracks.length === 3, 'type 1, tempo track + one per part');
  const tempos = smf.tracks[0].filter((e) => e.type === 'meta' && e.meta === 0x51).map((e) => ({ tick: e.tick, bpm: 60000000 / ((e.data[0] << 16) | (e.data[1] << 8) | e.data[2]) }));
  ok(tempos.length === m.tempos.length && near(tempos[0].bpm, 80, 0.01), `tempo map ${JSON.stringify(tempos)}`);
  ok(tempos.some((t) => near(t.bpm, 80 * 2 / 3, 0.01) && t.tick === 4 * P.PPQ), 'fermata written as a tempo dip at bar 2');
  ok(smf.tracks[0].some((e) => e.meta === 0x58 && e.data[0] === 4 && e.data[1] === 2), 'time signature 4/4');
  for (let k = 1; k <= 2; k++) {
    const tr = smf.tracks[k];
    const ons = tr.filter((e) => e.type === 'on'), offs = tr.filter((e) => e.type === 'off');
    const prog = tr.find((e) => e.type === 'program');
    ok(prog && prog.a === 52, `track ${k} program Choir Aahs`);
    ok(ons.length === m.parts[k - 1].notes.length && offs.length === ons.length, `track ${k}: note on/off pairs`);
    m.parts[k - 1].notes.forEach((nn, j) => ok(ons[j].a === nn.midi && ons[j].tick === Math.round(nn.q * P.PPQ) && ons[j].b === nn.vel, `track ${k} note ${j} pitch/tick/velocity`));
    ok(tr.some((e) => e.type === 'cc' && e.a === 7) && tr.some((e) => e.type === 'cc' && e.a === 10), `track ${k} volume and pan`);
    ok(new Set(tr.filter((e) => e.ch != null).map((e) => e.ch)).size === 1, `track ${k} one channel`);
  }
  const muted = P.readSMF(P.writeSMF(m, { parts: [{ mute: true }, { program: 40 }] }));
  ok(muted.tracks.length === 2 && muted.tracks[1].find((e) => e.type === 'program').a === 40, 'mixer overrides: mute drops a track, instrument changes the program');
}
// ---- corpus sweep: truths and produced outputs
{
  const find = (dir, re, out = []) => { if (!fs.existsSync(dir)) return out; for (const f of fs.readdirSync(dir, { withFileTypes: true })) { const p = path.join(dir, f.name); if (f.isDirectory()) find(p, re, out); else if (re.test(f.name)) out.push(p); } return out; };
  const truths = find(path.join(ROOT, 'corpus'), /^truth\.musicxml$/);
  const outs = find(path.join(MVP, 'work'), /\.musicxml$/).filter((f) => /regress-head-(default-ocr|challenge)\.out/.test(f));
  let nTruth = 0, nOut = 0, tieChecked = 0, structChecked = 0;
  for (const f of truths.concat(outs)) {
    const x = fs.readFileSync(f, 'utf8');
    let m;
    try { m = P.events(x); } catch (e) { ok(false, `${path.relative(ROOT, f)}: ${e.message}`); continue; }
    if (truths.includes(f)) nTruth++; else nOut++;
    const ns = notes(m);
    ok(Number.isFinite(m.duration) && m.duration > 0, `${path.relative(ROOT, f)}: duration ${m.duration}`);
    ok(ns.every((e) => Number.isFinite(e.t) && e.d > 0 && e.midi >= 0 && e.midi <= 127 && e.vel >= 1 && e.vel <= 127), `${path.relative(ROOT, f)}: bad event`);
    ok(m.measures.every((mm, i) => i === 0 || mm.t0 >= m.measures[i - 1].t0), `${path.relative(ROOT, f)}: measure times ordered`);
    // without repeats, sounding notes = pitched non-cue notes minus tie continuations
    if (m.order.every((v, i) => v === i) && !/<grace/.test(x)) {
      const nn = x.match(/<note\b[\s\S]*?<\/note>/g) || [];
      const want = nn.filter((s) => /<pitch>|<unpitched>/.test(s) && !/<cue\/>/.test(s) && !/<tie type="stop"\/>/.test(s)).length;
      // (produced outputs can hold a tie stop with no matching start: it sounds as a note)
      const stops = truths.includes(f) ? 0 : nn.filter((s) => /<tie type="stop"\/>/.test(s)).length;
      if (ns.length < want || ns.length > want + stops) ok(false, `${path.relative(ROOT, f)}: ${ns.length} events, ${want} expected`);
      tieChecked++;
    }
    // structure items: the played form in meta.json
    const meta = path.join(path.dirname(f), 'meta.json');
    if (truths.includes(f) && fs.existsSync(meta)) {
      const s = ((JSON.parse(fs.readFileSync(meta, 'utf8')).expected || {}).structure || '');
      const pf = s.match(/Played form:\s*([\d\s,\-–]+)/);
      if (pf && /\d/.test(pf[1])) {
        const want = pf[1].split(',').map((t) => t.trim()).filter(Boolean).flatMap((t) => { const [a, b] = t.split(/[-–]/).map(Number); return b ? Array.from({ length: b - a + 1 }, (_, k) => a + k) : [a]; });
        const got = m.order.map((i) => i + 1);
        ok(got.join(' ') === want.join(' '), `${path.relative(ROOT, path.dirname(f))}: played ${got.join(' ')}, expected ${want.join(' ')}`);
        structChecked++;
      }
    }
  }
  ok(nTruth > 100, `corpus truths parsed: ${nTruth}`);
  console.log(`corpus: ${nTruth} truth files, ${nOut} produced outputs, ${tieChecked} note-count checks, ${structChecked} played-form checks`);
}
// ---- the produced XML with instruments stays schema-valid
{
  const xsd = [path.join(ROOT, 'test/schema/musicxml.xsd'), path.join(MVP, 'work/schema/musicxml.xsd')].find((f) => fs.existsSync(f));
  const f = path.join(MVP, 'work/regress-head-default-ocr.out/real__methodist1905-st-anselm.musicxml');
  if (xsd && fs.existsSync(f)) {
    let i = 0;
    const x = fs.readFileSync(f, 'utf8').replace(/<score-instrument[\s\S]*?<\/midi-instrument>/g, '').replace(/(<score-part id="([^"]+)"><part-name>([^<]*)<\/part-name>(?:<part-abbreviation>[^<]*<\/part-abbreviation>)?)/g, (mm, a, id, name) => a + P.instrumentXML({ id, name }, i++, 4, { vocalParts: 4 }));
    const tmp = path.join(require('os').tmpdir(), `pb-${process.pid}.musicxml`);
    fs.writeFileSync(tmp, x);
    let valid = true;
    try { execFileSync('xmllint', ['--noout', '--nonet', '--schema', xsd, tmp], { stdio: 'pipe' }); } catch (e) { valid = false; }
    fs.unlinkSync(tmp);
    ok(valid, 'score-instrument / midi-instrument validate against the MusicXML 4.0 XSD');
  }
}
console.log(`${checks} checks, ${fails.length} failed`);
if (fails.length) { console.log('  ' + fails.slice(0, 40).join('\n  ')); process.exit(1); }
