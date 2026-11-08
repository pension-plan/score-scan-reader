export const meta = {
  name: 'omr-challenge-corpus',
  description: 'Parallel generation of an edge-case challenge corpus (synthetic sheet music + exact MusicXML truth + scan degradations), then validate, merge and baseline-score it',
  phases: [
    { title: 'Generate', detail: '6 parallel edge-case generators' },
    { title: 'Validate', detail: 'merge manifests, verify truth, add to eval, baseline score' },
  ],
}

const ROOT = '/Users/d.sloane/music'
const CH = `${ROOT}/corpus/challenge`
const OPTS = { model: 'opus', effort: 'xhigh' }
const CTX = `
GOAL: Create SYNTHETIC SHEET MUSIC that stress-tests a browser OMR app which converts SCANNED (image-only) sheet-music PDFs into MusicXML 4.0, keeping lyrics, splitting two voices on one staff (closed-score SATB etc.) into separate parts, and NEVER splitting piano grand staves. Each item needs EXACT ground truth so the app can be scored.
Machine: Linux aarch64, 192 cores, sudo, node 24, python3 (venv ${ROOT}/.venv with music21), lilypond 2.24, musicxml2ly, poppler-utils, ghostscript, ImageMagick if installed (else Pillow/numpy in the venv). Never run filesystem-wide searches (find /, locate); search only under ${ROOT}. Put timeouts on long commands.
REUSE existing tooling — read first: ${ROOT}/corpus/synthetic/_tools/ (run_all.py, catalog.py, items.py, custom LilyPond writer, truth-vs-render checks, degradation code), ${ROOT}/spike/classical/tools/degrade.py (degradations incl. page curl, phone photo, photocopy), ${ROOT}/corpus/manifest*.json for the item schema. Do NOT modify anything outside your own output folders; copy code you need.
OUTPUT for each item: ${CH}/<category>/<id>/ with: engraving.ly (or source), truth.musicxml (MusicXML 4.0, must pass the XSD at ${ROOT}/mvp/work/schema/musicxml.xsd via xmllint), clean.pdf (undamaged render), scan.pdf (image-only PDF, damaged), and for at least half the items also scan-mild.pdf and scan-severe.pdf (same page, lighter / heavier damage), meta.json {id, category, title, edge_cases:[tags], expected:{parts:[names], must_not_split:bool, shared_staves:[[...]], notes:"what a correct conversion must do"}, degradations:{per file: list with parameters + seed}, dpi, license}, ATTRIBUTION.txt. Truth must match the engraving exactly (verify notes/onsets/pitches/lyric syllables against what LilyPond rendered, as the synthetic corpus tools do); if a feature can't be represented exactly in truth, say so in meta.notes.
Licensing: public-domain tunes/texts or your own CC0 compositions only. No copyrighted music.
Write your category manifest to ${CH}/<category>/manifest.json (array of meta objects). Verify each scan PDF is image-only (pdffonts shows no fonts).
SCAN DAMAGE palette (mix per item, vary strengths, record params+seed): skew/rotation (0.5°–10°, plus a 90° and a 180° rotated page somewhere), perspective/keystone (phone photo), page curl and book-gutter shadow, uneven lighting/vignette, yellowed or coloured paper (RGB scan), paper texture, bleed-through of the reverse page, coffee stain / foxing spots, pencil annotations and circled notes, punch holes / staples, cropped edges cutting staff ends, moiré/halftone, blur (focus + motion), gaussian + salt-and-pepper noise, JPEG quality 15–60, binarized photocopy (thick and thin), low dpi (100–150) and high dpi (400–600), double-page spread (2-up), slight scale mismatch between pages.
`
const SECTION = { type: 'object', properties: { summary: { type: 'string' }, count: { type: 'number' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'count', 'files'] }

const CATS = [
  { key: 'voices', brief: 'VOICES AND PARTS on shared staves: closed SATB with voice crossing, frequent unisons (one head two stems, and one head one stem), one voice resting while the other sings, divisi appearing mid-piece, SAB (3 parts on 2 staves), TTBB with treble-8vb clef (octave!), SSAA, chords on one stem (must stay chords, not split), "a2" passages, a voice moving to the other staff briefly, a hymn with lyrics only under the treble staff vs one with lyrics under each staff. Part labels printed at system starts (S A / T B, Soprano Alto, Sopran Alt, Tenor Bass) in some items, absent in others. 6–8 items.' },
  { key: 'rhythm', brief: 'RHYTHM: triplets and other tuplets (quarter and eighth triplets, duplets in 6/8, quintuplets), ties across barlines and across system breaks, dotted and double-dotted values, anacrusis/pickup and incomplete final bar, time-signature changes mid-piece, compound meters (6/8, 9/8, 12/8), common/cut time symbols, 16th and 32nd beamed groups, beams across rests, every rest type including whole-bar rests and multi-measure rests, fermatas, grace notes and appoggiaturas, cross-voice rhythm differences in closed score. 6–8 items.' },
  { key: 'pitch', brief: 'PITCH AND NOTATION: key signature changes mid-piece (incl. to/from 7 sharps / 7 flats and naturals cancelling), clef changes mid-staff (treble↔bass, alto and tenor clefs, treble-8vb), heavy accidentals incl. double sharps/flats and courtesy accidentals, accidentals carrying through a bar and cancelled by barline, extreme ledger lines high and low, 8va/8vb brackets, chromatic passages, enharmonic spellings. 6–8 items, mix of melody and closed-score SATB.' },
  { key: 'lyrics', brief: 'LYRICS: long melismas with extender lines, 4–6 verses stacked, hyphenated long words, elisions (two syllables on one note with ‿), lyrics in German (ä ö ü ß), French (é è ç œ), Latin, Welsh/Scandinavian characters, verse numbers (1. 2. 3.), refrain/chorus text sharing one line, italic translation line under the original, lyrics under different staves in SATB, additional stanzas printed as text blocks BELOW the last system (hymnal style), apostrophes and punctuation. 6–8 items.' },
  { key: 'layout', brief: 'LAYOUT AND STRUCTURE: multi-page pieces (one 10+ pages, one 3–4 pages), repeats with 1st/2nd endings (volta), D.C./D.S./Coda markings, title, composer, tempo and dynamics text on the page (must not be read as lyrics or notes), page numbers and headers, small cue notes and an "Amen" ending at smaller staff size, mixed staff sizes on a page, organ score on 3 staves (pedal), piano with cross-staff beams and pedal marks (must_not_split), SATB choir + piano accompaniment (choir splits, piano does not), system with a brace vs a bracket, landscape page, a page with only one system, systems with different numbers of staves (hidden empty staves). 6–8 items.' },
  { key: 'degradation', brief: 'SCAN DEGRADATION EXTREMES: take 4–6 SIMPLE pieces (a closed-score SATB hymn, a melody with lyrics, a short piano piece) and produce MANY damaged variants each (at least 8 variants per piece covering the whole SCAN DAMAGE palette, especially: 5–10° skew, 90° and 180° rotated pages, phone perspective, book gutter shadow + curl, coloured yellowed paper RGB scan, bleed-through, coffee stain + pencil marks, punch holes, cropped staff ends, halftone/moiré, JPEG 15, thin photocopy, 100 dpi and 600 dpi, 2-up spread). Each variant is its own item id sharing the piece truth, so scores per degradation type can be compared. Include clean controls.' },
]

phase('Generate')
const gens = await parallel(CATS.map(c => () => agent(`${CTX}
YOUR CATEGORY: ${c.key} → write only under ${CH}/${c.key}/.
${c.brief}
Make every item deliberately hard for an OMR system in the stated way, but musically valid and engraved cleanly by LilyPond before damage. Return a summary listing items, their edge-case tags, damage applied, and any truth limitations.`, { ...OPTS, label: `gen:${c.key}`, phase: 'Generate', schema: SECTION })))

phase('Validate')
const v = await agent(`${CTX}
Generators finished:\n${gens.map((g, i) => `${CATS[i].key}: ${g ? g.summary : 'FAILED'}`).join('\n\n')}
TASK (validator, do not change other folders except as stated):
1. Check every item under ${CH}/*/*/: truth.musicxml passes the XSD; scan PDFs open and are image-only; meta.json complete; clean.pdf render matches truth (re-run the generator's check or spot-check with music21 vs LilyPond event export). Fix or drop broken items, recording why.
2. Merge all category manifests into ${CH}/manifest.json and write ${CH}/README.md (categories, item list with edge-case tags and damage, how to rebuild, licences).
3. Add challenge support to the evaluation harness ${ROOT}/mvp/tools/eval.mjs with a minimal, backward-compatible change: a new --set challenge option (and challenge items matched by scan*.pdf, scoring each scan variant separately, id = <category>/<id>/<variant>). The DEFAULT run must stay exactly the same 19-item benchmark (synthetic + real) so ongoing fix-forward rounds stay comparable. Another agent may be running eval.mjs right now: write the new version to a temp file and atomically rename it in place; run its default mode once afterwards to confirm the 19-item results are unchanged.
4. Baseline: run node ${ROOT}/mvp/tools/eval.mjs --set challenge --jobs 48 --no-ocr --out ${ROOT}/mvp/work/eval-challenge-baseline.json (then with OCR on the lyrics category). Report aggregate per category and per damage type, the worst 10 items, crashes, and which edge cases fail completely.`, { ...OPTS, label: 'validate+baseline', phase: 'Validate', schema: { type: 'object', properties: {
  summary: { type: 'string' }, items: { type: 'number' }, scans: { type: 'number' }, dropped: { type: 'string' },
  per_category: { type: 'string' }, per_damage: { type: 'string' }, worst: { type: 'string' }, crashes: { type: 'number' }, failing_edge_cases: { type: 'string' } },
  required: ['summary', 'items', 'scans', 'dropped', 'per_category', 'per_damage', 'worst', 'crashes', 'failing_edge_cases'] } })
return { gens: gens.map((g, i) => ({ cat: CATS[i].key, summary: g?.summary, count: g?.count })), validate: v }
