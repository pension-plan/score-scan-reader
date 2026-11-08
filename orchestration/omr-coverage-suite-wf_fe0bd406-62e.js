export const meta = {
  name: 'omr-coverage-suite',
  description: 'Generate a synthetic coverage suite with every notation symbol and layout (exact truth + scan damage), add per-symbol accuracy and speed/memory benchmarking to the harness, baseline the app',
  phases: [
    { title: 'Generate', detail: '8 parallel generators, one per symbol/layout family' },
    { title: 'Harness', detail: 'per-symbol scoring + speed/memory benchmark (runs in parallel with generation)' },
    { title: 'Baseline', detail: 'validate, merge, score, publish COVERAGE.md' },
  ],
}

const ROOT = '/Users/d.sloane/music'
const COV = `${ROOT}/corpus/coverage`
const OPTS = { model: 'opus', effort: 'xhigh' }
const CTX = `
GOAL: A systematic SYNTHETIC COVERAGE SUITE for a browser OMR app that converts SCANNED sheet music (image-only PDFs) into MusicXML 4.0 (repo ${ROOT}; app code in ${ROOT}/mvp/src — do NOT edit mvp/src, other agents are changing it). The suite must contain EVERY common notation symbol and EVERY common score layout, each with EXACT ground truth, so we can say per symbol / per layout whether the app supports it and how accurately, and measure speed and memory.
Machine: Linux aarch64, 192 cores, node 24, python venv ${ROOT}/.venv (music21), lilypond 2.24, poppler-utils, ghostscript. Never run filesystem-wide searches (find /); search only under ${ROOT}. Put timeouts on long commands.
REUSE tooling (copy, don't modify): ${ROOT}/corpus/challenge/*/_tools/ (LilyPond writers, truth-vs-MIDI/event-log checks, damage simulator with seeded params), ${ROOT}/corpus/challenge/_validate/validate.py, ${ROOT}/corpus/synthetic/_tools/.
OUTPUT per item: ${COV}/<family>/<id>/ with engraving.ly, truth.musicxml (MusicXML 4.0, passes XSD ${ROOT}/mvp/work/schema/musicxml.xsd via xmllint, parses in music21), clean.pdf, scan.pdf (typical 200-300 dpi scan: slight skew, noise, JPEG), scan-severe.pdf (heavy damage), meta.json {id, family, title, symbols:[canonical symbol tags present, see TAXONOMY], layout:<layout tag>, expected:{parts:[names], must_not_split:bool}, counts:{<symbol tag>: number of occurrences in truth}, degradations:{per file: params+seed}, dpi, pages, license:'CC0'}, ATTRIBUTION.txt. Truth must match the engraving exactly (verify with LilyPond MIDI / event log as the challenge tools do). If a symbol can't be represented in MusicXML truth exactly, say so in meta.notes. All music your own CC0 composition or public domain. Write ${COV}/<family>/manifest.json.
TAXONOMY (use these exact tags in meta.symbols and meta.counts; add new ones only if needed, prefixed x-):
 notes: note-breve, note-whole, note-half, note-quarter, note-8th, note-16th, note-32nd, note-64th, dot, double-dot, chord, beam, flag, stem-up, stem-down, ledger-above, ledger-below, grace, grace-slash, cue-note, tremolo
 rests: rest-breve, rest-whole, rest-half, rest-quarter, rest-8th, rest-16th, rest-32nd, rest-64th, rest-dotted, rest-whole-bar, rest-multibar
 pitch: clef-treble, clef-bass, clef-alto, clef-tenor, clef-soprano, clef-treble-8vb, clef-treble-8va, clef-bass-8vb, clef-change, key-0..key-7 sharps as key-s1..key-s7, flats key-f1..key-f7, key-change, acc-sharp, acc-flat, acc-natural, acc-double-sharp, acc-double-flat, acc-courtesy, ottava-8va, ottava-8vb, ottava-15ma
 time: time-2-4, time-3-4, time-4-4, time-2-2, time-3-2, time-6-8, time-9-8, time-12-8, time-5-4, time-5-8, time-7-8, time-common, time-cut, time-change, pickup, tuplet-3, tuplet-2, tuplet-5, tuplet-6, tuplet-7, tuplet-nested, tie, tie-across-system
 marks: slur, staccato, staccatissimo, accent, tenuto, marcato, fermata, trill, mordent, turn, arpeggio, breath, dyn-pp, dyn-p, dyn-mp, dyn-mf, dyn-f, dyn-ff, dyn-sfz, hairpin-cresc, hairpin-dim, pedal, fingering, text-expression, tempo-mark, metronome, rehearsal-mark, chord-symbol
 structure: barline-double, barline-final, repeat-start, repeat-end, volta-1, volta-2, segno, coda, dc, ds, fine, system-break, page-break, multi-page
 lyrics: lyrics, lyrics-multi-verse, lyrics-melisma, lyrics-extender, lyrics-hyphen, lyrics-elision, lyrics-non-ascii, stanza-text
 layouts (meta.layout): melody, melody-lyrics, piano, voice-piano, choir-closed-satb, choir-open-satb, choir-sab, choir-ttbb, choir-ssaa, choir-piano, organ, string-quartet, orchestral, lead-sheet, hymnal-stanzas, divisi, cross-staff, two-voices-one-staff-instrument, percussion-none
Keep pieces SHORT (4–16 bars) so each symbol is isolated and countable, but put many occurrences of the target symbols in each piece. Engrave cleanly at standard size first; damage only in scan.pdf / scan-severe.pdf.
`
const SECTION = { type: 'object', properties: { summary: { type: 'string' }, count: { type: 'number' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'count', 'files'] }

const FAMILIES = [
  { key: 'notes', brief: 'Every note value breve..64th, dots and double dots, chords (2-6 notes), beams (all common groupings, beams across rests, beamed 16th/32nd), flags, both stem directions, ledger lines up to 5 above/below, grace notes (slashed/unslashed), cue notes, tremolos. 6–10 items, single staff and piano.' },
  { key: 'rests', brief: 'Every rest value breve..64th, dotted rests, whole-bar rests in several meters (3/4, 6/8, 2/2), multi-bar rests (H-bar with number, old-style symbols), rests in two-voice staves raised/lowered, rests inside tuplets and beams, rests in piano left hand. 6–10 items.' },
  { key: 'pitch', brief: 'All clefs (treble, bass, alto, tenor, soprano, treble-8vb, treble-8va, bass-8vb) and clef changes; all 15 key signatures major and minor (one short piece each or a key tour), key changes with cancellations; all accidentals incl. double sharp/flat and courtesy; ottava 8va/8vb/15ma. 8–12 items.' },
  { key: 'time', brief: 'Every listed time signature incl. common and cut, time changes, pickups, tuplets 2/3/5/6/7 and nested tuplets, ties incl. across system and page breaks. 6–10 items.' },
  { key: 'marks', brief: 'Articulations (staccato, staccatissimo, accent, tenuto, marcato), fermatas, ornaments (trill, mordent, turn), arpeggio, breath, all dynamics and hairpins, pedal marks, fingering, text expressions, tempo and metronome marks, rehearsal marks, chord symbols (lead sheet). These mostly test that the app is NOT confused by them (no false notes) and whether it transcribes them. 6–10 items.' },
  { key: 'structure', brief: 'Double and final barlines, repeats, 1st/2nd endings, segno, coda, D.C., D.S., Fine, explicit system and page breaks, multi-page pieces (2, 5, 12 pages). 6–8 items.' },
  { key: 'layouts', brief: 'One clean exemplar per layout tag: melody, melody-lyrics, piano, voice-piano, choir-closed-satb, choir-open-satb, choir-sab, choir-ttbb, choir-ssaa, choir-piano, organ (3 staves), string-quartet (bracketed 4 staves, must_not_split per staff), orchestral excerpt (8+ staves with brackets/braces), lead-sheet, hymnal-stanzas, divisi, cross-staff piano, two-voices-one-staff-instrument (piano RH two voices; must stay one part). 16–20 items.' },
  { key: 'perf', brief: 'PERFORMANCE set: the same 1-page SATB hymn and a dense piano page rendered at 100, 150, 200, 300, 400 and 600 dpi; A4, Letter and A3 page sizes; and multi-page documents of 1, 5, 10, 20 and 40 pages (repeat CC0 pages with varied content). meta.json adds perf:{dpi, pageSize, pages, megapixels}. Truth required as for every item. 15–25 files.' },
]

phase('Generate')
const genP = parallel(FAMILIES.map(f => () => agent(`${CTX}
YOUR FAMILY: ${f.key} → write only under ${COV}/${f.key}/.
${f.brief}
Return a summary listing items with their symbol tags and counts, layouts, damage, and truth limitations.`, { ...OPTS, label: `gen:${f.key}`, phase: 'Generate', schema: SECTION })))

phase('Harness')
const harnessP = agent(`${CTX}
TASK (harness, in parallel with the generators): extend the evaluation so the coverage suite produces a per-symbol support matrix and performance numbers.
1. ${ROOT}/mvp/tools/eval.mjs: add --set coverage (items = ${COV}/*/*/ with scan*.pdf/clean.pdf + truth.musicxml, id = <family>/<id>/<variant>), keeping the DEFAULT set exactly unchanged (other agents run it right now: write to a temp file and rename atomically; verify the default 20-item results are unchanged afterwards). Record per item wall time, per-page time and peak RSS of the child process.
2. New ${ROOT}/tools/coverage.mjs: reads an eval output for --set coverage plus each item's meta.json and truth.musicxml, and for EVERY taxonomy tag computes: occurrences in truth; whether the app's MusicXML contains the corresponding element at all (e.g. rests <rest>, dots <dot/>, tuplets <time-modification>/<tuplet>, clefs <clef> sign/line/octave, keys <fifths>, time <time>, accidentals <accidental> incl double-sharp/flat-flat, ties <tie>, slurs <slur>, articulations <articulations>, dynamics <dynamics>, fermata <fermata>, ornaments <ornaments>, repeats <repeat>, endings <ending>, lyrics features <lyric>/<extend>/<elision>, grace <grace/>, multi-bar rests <multiple-rest>, ottava <octave-shift>, chord symbols <harmony>, etc.) and an accuracy where alignment allows (matched-note recall for note-level tags, exact-match rate for header tags); for each layout tag: parts count/name match and aggregate. Status per tag: supported (accuracy >= 0.8), partial (0.2–0.8), unsupported (< 0.2 or never emitted), plus "not confused" for marks the app is not expected to output (no false notes added vs clean truth). Also a performance table: ms per page and peak MB by dpi, page size and page count (from the perf family), and a linear fit (ms per megapixel).
3. Output ${ROOT}/docs/COVERAGE.md (tables: symbols by family with status/accuracy/occurrences, layouts, performance) and ${ROOT}/docs/coverage.json. Test on whatever items exist so far (generators are still writing; skip incomplete folders without meta.json/truth).
Return a summary of the new options/files and a sample of the matrix.`, { ...OPTS, label: 'harness:coverage', phase: 'Harness', schema: SECTION })

const [gens, harness] = await Promise.all([genP, harnessP])

phase('Baseline')
const base = await agent(`${CTX}
Generators finished:\n${gens.map((g, i) => `${FAMILIES[i].key}: ${g ? g.summary : 'FAILED'}`).join('\n\n')}
Harness: ${harness ? harness.summary : 'FAILED'}
TASK: 1) Validate every item under ${COV} (adapt ${ROOT}/corpus/challenge/_validate/validate.py: XSD, music21 parse, image-only PDFs, meta completeness incl. symbols/counts/layout, LilyPond re-render MIDI/event check). Fix or drop broken items with reasons. 2) Merge manifests into ${COV}/manifest.json and write ${COV}/README.md (families, items, symbol and layout coverage table: every taxonomy tag must have >= 1 item; list any tag still missing and why). 3) Run node ${ROOT}/mvp/tools/eval.mjs --set coverage --jobs 48 --out ${ROOT}/mvp/work/eval-coverage-baseline.json (with OCR) and node ${ROOT}/tools/coverage.mjs to write ${ROOT}/docs/COVERAGE.md + docs/coverage.json. 4) Report the support matrix headline: counts of supported / partial / unsupported tags, the 15 most important unsupported or partial symbols (by how common they are in real hymnals and scores), per-layout results, and performance (ms/page and MB by dpi/pages).`, { ...OPTS, label: 'validate+baseline', phase: 'Baseline', schema: { type: 'object', properties: {
  summary: { type: 'string' }, items: { type: 'number' }, supported: { type: 'number' }, partial: { type: 'number' }, unsupported: { type: 'number' },
  top_gaps: { type: 'string' }, layouts: { type: 'string' }, performance: { type: 'string' }, missing_tags: { type: 'string' } },
  required: ['summary', 'items', 'supported', 'partial', 'unsupported', 'top_gaps', 'layouts', 'performance', 'missing_tags'] } })
return { gens: gens.map((g, i) => ({ fam: FAMILIES[i].key, count: g?.count, summary: g?.summary })), harness: harness?.summary, base }
