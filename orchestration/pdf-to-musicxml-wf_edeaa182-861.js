export const meta = {
  name: 'pdf-to-musicxml',
  description: 'Research, design, build, measure and review a standalone browser PDF→MusicXML converter (lyrics + multi-voice part splitting)',
  phases: [
    { title: 'Research', detail: 'web research on OMR + voice separation, pdf.js glyph probe, open-source corpus with ground truth' },
    { title: 'Design', detail: 'architecture + module contracts' },
    { title: 'Build', detail: 'parallel module builders' },
    { title: 'Integrate', detail: 'assemble, test against corpus, improve until metrics plateau' },
    { title: 'Review', detail: 'adversarial lenses' },
    { title: 'Fix', detail: 'apply confirmed findings, final measurement' },
  ],
}

const ROOT = '/Users/d.sloane/music'
const OPTS = { model: 'opus', effort: 'xhigh' }
const CONTEXT = `
PROJECT: A standalone, client-side JavaScript web app that converts sheet-music PDFs into MusicXML (3.1/4.0 partwise), RETAINING LYRICS, and that DETECTS WHEN ONE STAFF CARRIES MULTIPLE VOICES/PARTS (e.g. SATB closed score: soprano stems-up + alto stems-down on treble staff; tenor+bass on bass staff; or "a2"/divisi) and SEPARATES THEM INTO DIFFERENT <part>s where relevant (with lyrics attached to the correct voice).
Project root: ${ROOT} (not a git repo). Machine: Linux aarch64, sudo available, node v24, python3, lilypond 2.24 + musicxml2ly installed, poppler-utils, ghostscript, network access.
DELIVERY TARGET: one self-contained HTML file dist/pdf2musicxml.html that will be published as a claude.ai Artifact. Artifact constraints (CSP-enforced):
 - No <!doctype>/<html>/<head>/<body> tags; start with <title> (2-4 word name), <meta name="claude:viewport-fit-sides" content="cover">, <style>.
 - External scripts ONLY from cdnjs.cloudflare.com (preferred)/cdn.jsdelivr.net/npm/unpkg.com, exact pinned versions (e.g. pdf.js 3.11.174 UMD: https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js). fetch/XHR to CDNs is BLOCKED, and cross-origin Worker URLs fail. So load https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js as a plain <script> tag too (it defines globalThis.pdfjsWorker, letting pdf.js run its "fake worker" on the main thread) or build a blob: worker. Verify whichever approach actually works.
 - Fonts only from Google Fonts. Downloads via <a download> / script saves are inert in the viewer: provide the MusicXML as a selectable textarea + "Copy" button (navigator.clipboard.writeText inside click handler, catch and fall back to select()). Also OK to try a download button, but copy must be the primary path. No alert/confirm/prompt, no window.print.
 - Theme-aware color tokens: light on :root, dark under @media (prefers-color-scheme: dark){:root:not([data-theme="light"]){...;color-scheme:dark}} and again :root[data-theme="dark"]{...}; body background from token. Works at 400px width, side gutter padding-left:max(16px, env(safe-area-inset-left,0px)) (and right). Avoid generic AI looks (cream+terracotta, Inter, purple gradients, emoji). Visible focus states, prefers-reduced-motion.
 - Must open in a realistic working state: embed a small open-source sample PDF (base64, public domain/CC0, with lyrics and closed-score multi-voice) that is converted on load; user can drop/upload their own PDF. Show a rendered preview of the result (e.g. OpenSheetMusicDisplay UMD from jsdelivr pinned version, or a simple self-drawn notation/table view) plus per-part summary, detected warnings/confidence.
 - Total file < 16MB.
Core conversion logic must be environment-agnostic ES code that ALSO runs in node (via npm pdfjs-dist@3.11.174 legacy build) so a test harness can measure accuracy against ground truth.
`

const SECTION = { type: 'object', properties: { summary: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'files'] }

// ───────── Research ─────────
phase('Research')
const [omr, voices, probe, corpus] = await parallel([
  () => agent(`${CONTEXT}
TASK: Search the internet (WebSearch/WebFetch — load via ToolSearch) for CURRENT (2023-2026) approaches to converting PDF sheet music into MusicXML, and write ${ROOT}/docs/research-omr.md.
Cover: (1) vector/born-digital PDF extraction (reading engraver fonts: LilyPond Emmentaler glyph names, SMuFL codepoints in Bravura/Leland/Petaluma used by MuseScore/Dorico, Finale Maestro/Sibelius Opus legacy font char maps; vector staff lines/stems/beams/barlines from path ops; pdf.js getOperatorList/getTextContent capabilities and pitfalls), (2) raster OMR: Audiveris, oemer, homr, Polyphonic-TrOMR, SMT/Sheet Music Transformer, legato, end-to-end transformer models, ONNX-in-browser feasibility, classical pipelines (staff detection via horizontal projection, staff removal, connected components, template matching), (3) lyric extraction and syllable/hyphen/melisma handling (MusicXML <lyric> syllabic begin/middle/end/single, <extend>, verse numbers), (4) evaluation metrics used in the literature (e.g. OMR-NED, TEDn, symbol error rate, MV2H).
End with concrete recommendations for a pure-browser JS app with a high-accuracy vector path and a best-effort raster fallback. Cite URLs. Return a concise summary + file paths.`, { ...OPTS, label: 'research:omr', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Search the internet for current approaches to VOICE / PART SEPARATION in OMR and symbolic music, and write ${ROOT}/docs/research-voices.md.
Cover: identifying multiple voices on one staff (stem direction, shared vs separate noteheads, rests offset vertically, voice-numbered layers in LilyPond \\voiceOne/\\voiceTwo, "a 2"/unison notation, chords vs two voices), closed-score SATB conventions, divisi, piano grand staff vs vocal parts, part naming from instrument labels at system start (e.g. "S A", "T B", "Soprano Alto"), lyrics placement (lyrics between staves belong to which voice; multiple verses; lyrics only under the upper voice in hymns applying to all voices), and how MusicXML represents this (<voice>, <backup>, <staff>, separate <part>s, <part-group>). Include algorithms from literature (e.g. voice separation by contig mapping, stream segregation, Audiveris voice/slot model, music21 voicesToParts/explode). Give a recommended decision procedure for WHEN to split a staff's voices into separate parts (relevant) vs keep as one part with multiple <voice>s (e.g. piano). Cite URLs. Return summary + file paths.`, { ...OPTS, label: 'research:voices', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Empirically probe what pdf.js 3.11.174 exposes for engraved PDFs. In ${ROOT}: npm init -y if needed, npm i pdfjs-dist@3.11.174. Write small LilyPond test files in ${ROOT}/probe/ (a melody with lyrics incl. hyphenated and melisma syllables; closed-score SATB with \\voiceOne/\\voiceTwo on two staves with lyrics; accidentals, key/time sigs, dotted notes, rests, beams, ties, tuplets), compile to PDF with lilypond. Then write ${ROOT}/probe/dump.mjs that uses pdfjs-dist legacy build in node to dump: getTextContent items (str, transform, fontName), getOperatorList ops (showText glyph objects: fontChar, unicode, width, font name; constructPath ops with coordinates; transforms/CTM), and figure out reliably HOW to identify music glyphs (Emmentaler glyph names? unicode? font's charProcOperatorList? commonObjs font data with glyph names / toUnicode / differences encoding). Also inspect with pdffonts/pdftotext -bbox. Document precise findings (with snippets and real numbers: staff line thickness, staff space, how stems/beams/barlines/ledger lines/slurs appear as paths, notehead glyph identifiers for each duration, rest glyphs, accidental glyphs, clef/time/key glyphs, flags, dots, lyric text items and hyphen glyphs) in ${ROOT}/docs/pdfjs-probe.md. Also check the same for at least one non-LilyPond PDF (e.g. a MuseScore-exported or Finale/Sibelius PDF from CPDL https://www.cpdl.org or IMSLP/musescore openscore) to see SMuFL/legacy font behaviour. Return summary + file paths.`, { ...OPTS, label: 'research:pdfjs-probe', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Build an OPEN-SOURCE test corpus with ground truth in ${ROOT}/corpus/. Each item: a folder with source.pdf, truth.musicxml (ground truth, ideally the source the PDF was engraved from), LICENSE/attribution note, and an entry in ${ROOT}/corpus/manifest.json: {id, title, source_url, license, engraver ('lilypond'|'musescore'|'finale'|'sibelius'|'scan'|...), has_ground_truth, features:[lyrics, multi_voice_staff, satb_closed, multi_verse, piano, ...], expected_parts:[names]}.
Aim for >= 12 items covering: single melody + lyrics (folk songs, hymns), multi-verse hymns, SATB closed score (2 staves, 2 voices each, lyrics) — these are the key multi-part-per-line cases — SATB open score (4 staves), piano solo (grand staff, should NOT be split into parts), voice+piano lieder.
Sources (public domain / CC0 / CC-BY only): music21 corpus (pip install music21 in a venv at ${ROOT}/.venv; Bach chorales with lyrics in MusicXML — make closed-score versions by writing LilyPond with \\voiceOne/\\voiceTwo and \\addlyrics/\\lyricsto from the parsed data, so ground truth parts are S/A/T/B), OpenScore Lieder (github.com/OpenScore/Lieder, CC0, MuseScore files — fetch MusicXML if available), Mutopia Project (mutopiaproject.org: PDFs + .ly sources; can convert .ly → ground truth only if feasible, otherwise use as no-ground-truth smoke tests), CPDL PDFs (smoke tests from other engravers, check license per score). Generate PDFs from MusicXML via musicxml2ly + lilypond where ground truth is MusicXML. Also include 1-2 scanned/raster PDFs (e.g. rasterize a generated PDF with ghostscript at 300dpi and re-wrap as image PDF, plus a real IMSLP-style public-domain scan) for raster fallback testing.
Also produce ${ROOT}/corpus/sample-embed.pdf: a SMALL (<200KB) public-domain hymn/chorale in closed-score SATB with lyrics, for embedding in the app as the default sample. Record its attribution.
Verify every PDF opens (pdfinfo). Return summary + manifest stats + file paths.`, { ...OPTS, label: 'research:corpus', schema: SECTION }),
])
log(`Research done: ${[omr, voices, probe, corpus].filter(Boolean).length}/4 agents returned`)

// ───────── Design ─────────
phase('Design')
const design = await agent(`${CONTEXT}
Read ${ROOT}/docs/research-omr.md, ${ROOT}/docs/research-voices.md, ${ROOT}/docs/pdfjs-probe.md, ${ROOT}/corpus/manifest.json (and look at probe/ and corpus/ files).
Research summaries: OMR: ${omr?.summary}\nVOICES: ${voices?.summary}\nPROBE: ${probe?.summary}\nCORPUS: ${corpus?.summary}
TASK: Write ${ROOT}/docs/DESIGN.md — the architecture and EXACT module contracts that 4 builders will implement IN PARALLEL without talking to each other. Fixed file layout:
 - src/extract.js — PDF → per-page primitives: glyphs {page,x,y,w,h,font,id(normalized symbol name e.g. 'noteheadBlack','restQuarter','gClef','accidentalSharp'...),raw}, text items {str,x,y,size,font}, line/rect/path segments. Engraver font maps (Emmentaler names, SMuFL codepoints, plus heuristics for unknown fonts). Raster detection (no glyphs/vectors → mark page as raster) + best-effort raster pipeline OR clear diagnostic (designer decides scope; document it).
 - src/recognize.js — primitives → score model: systems, staves (5-line groups, staff space), clefs, key/time sigs, barlines/measures, noteheads+stems+beams+flags+dots → durations, accessorized pitches (key + accidentals carried through measure), rests, ties, tuplets, chords, voices-per-staff (stem direction / layer analysis), part/staff identity across systems (brace/bracket, instrument labels).
 - src/lyrics.js — attach lyric text to notes: line/verse detection under staves, syllable→note x-alignment, hyphens ⇒ syllabic, extender lines ⇒ <extend>, multiple verses ⇒ lyric number, which voice the lyric belongs to.
 - src/parts.js — the voice→part split decision (when multiple voices on one staff should become separate parts: SATB closed score, labels like "S A"; when not: piano/keyboard). Produce final parts list with names.
 - src/musicxml.js — score model → MusicXML 4.0 partwise string (divisions, attributes, notes, chords, rests, voices, backup, ties, tuplets, beams, lyrics, part-list with names/part-groups) + must be well-formed and valid against the MusicXML XSD.
 - src/index.js — convert(pdfData: Uint8Array|ArrayBuffer, {pdfjsLib, onProgress}) → {musicxml, score, warnings, stats}; pdfjsLib injected so node and browser both work.
 - ui/ (template.html, ui.js, styles) and build.mjs → dist/pdf2musicxml.html (inline all src as one script — no ES module imports at runtime; e.g. concatenate or a tiny bundler like esbuild via npm), embedding corpus/sample-embed.pdf as base64.
 - test/run.mjs — runs convert() over corpus/manifest.json, compares to truth.musicxml, prints per-item + aggregate metrics JSON to test/results.json: part count/name match, measure count, note pitch accuracy, duration accuracy, rest accuracy, lyric syllable accuracy (text+syllabic), voice/part assignment accuracy (alignment by part order + measure + onset), XSD validity (download MusicXML 4.0 XSD into test/schema and use xmllint), plus crash/runtime. Define an aggregate score in [0,1].
Specify the shared score-model data structures (JSON shapes) with field-level precision, coordinate conventions (pdf.js y-up vs flipped), units, and error/warning conventions. Explicitly assign each concern to exactly one module. Return summary + paths.`, { ...OPTS, label: 'design', schema: SECTION })

// ───────── Build ─────────
phase('Build')
const BUILDERS = [
  { key: 'extract+recognize', files: 'src/extract.js, src/recognize.js', extra: 'This is the hardest module: get the vector path (LilyPond + SMuFL fonts) highly accurate. Write unit checks against probe/ PDFs.' },
  { key: 'lyrics+parts+musicxml', files: 'src/lyrics.js, src/parts.js, src/musicxml.js', extra: 'Build against hand-written score-model fixtures matching DESIGN.md shapes (put them in test/fixtures/). Validate musicxml output with xmllint against the XSD.' },
  { key: 'harness+build', files: 'src/index.js, build.mjs, test/run.mjs, test/schema/, package.json scripts (npm run build, npm test)', extra: 'The metric harness must be robust: alignment by measure+onset, tolerant to missing modules (stub fallbacks if other modules not yet present). Use stub modules only in-memory for your own testing; do not overwrite other builders\' files.' },
  { key: 'ui', files: 'ui/template.html, ui/ui.js, ui/styles.css', extra: 'Design a distinctive, sheet-music-world UI (engraving/score vernacular: staff-line motifs, measure numbers, part names, real terms of art). Drop zone + file input, embedded sample auto-converts on load, progress, results: rendered preview (OSMD UMD from cdn.jsdelivr.net/npm/opensheetmusicdisplay@<pinned>/build/opensheetmusicdisplay.min.js is fine), per-part list showing which parts were split from shared staves, lyrics preview, warnings, MusicXML textarea + Copy. Use a mock convert() result for development.' },
]
const built = await parallel(BUILDERS.map(b => () => agent(`${CONTEXT}
Read ${ROOT}/docs/DESIGN.md (authoritative contracts) and the docs/ research files. You are the builder for: ${b.files}. Write ONLY these files (other builders are writing the others concurrently). ${b.extra}
Test your work as far as possible in isolation. Return summary + files written + any contract deviations (there should be none; if unavoidable, document them at the top of your file AND in your summary).`, { ...OPTS, label: `build:${b.key}`, phase: 'Build', schema: SECTION })))
const buildNotes = built.map((r, i) => `${BUILDERS[i].key}: ${r ? r.summary : 'FAILED'}`).join('\n')

// ───────── Integrate + improve loop ─────────
phase('Integrate')
const METRICS = { type: 'object', properties: {
  aggregate: { type: 'number' }, pitch: { type: 'number' }, duration: { type: 'number' }, lyrics: { type: 'number' },
  parts: { type: 'number' }, xsd_valid_ratio: { type: 'number' }, crashes: { type: 'number' },
  worst_items: { type: 'array', items: { type: 'string' } }, changes: { type: 'string' } },
  required: ['aggregate', 'pitch', 'duration', 'lyrics', 'parts', 'xsd_valid_ratio', 'crashes', 'worst_items', 'changes'] }

let m = await agent(`${CONTEXT}
Builders finished:\n${buildNotes}
TASK (integrator): In ${ROOT}, make everything work together per docs/DESIGN.md: resolve contract mismatches, npm run build produces dist/pdf2musicxml.html, npm test runs test/run.mjs over the whole corpus with no crashes. Then verify the built HTML in a real browser (Playwright tools via ToolSearch, or npx playwright with chromium): open dist file served locally, confirm the embedded sample converts, OSMD/preview renders, no console errors, and that pdf.js works WITHOUT any fetch to CDNs except script tags (simulate the artifact CSP: script-src cdnjs/jsdelivr/unpkg + 'unsafe-inline', connect-src 'self' blob: data:, worker-src blob:). Report metrics from test/results.json.`, { ...OPTS, label: 'integrate', schema: METRICS })
log(`Initial aggregate ${m?.aggregate}`)

let best = m?.aggregate ?? 0, stale = 0
for (let round = 1; round <= 6 && stale < 2 && best < 0.97; round++) {
  m = await agent(`${CONTEXT}
Improvement round ${round}. Current metrics: ${JSON.stringify(m)}.
TASK: In ${ROOT}, run npm test, study test/results.json and the worst items (diff produced vs truth MusicXML, render PDFs to PNG with pdftoppm to look at them). Fix the highest-impact root causes in src/ (generalizable fixes only — no per-file hacks or hard-coding corpus content). Prioritise: crashes > XSD validity > part/voice separation for multi-voice staves > pitch > duration > lyrics (syllabic/extend/verses) > rest/ties/tuplets. Re-run npm test + npm run build after changes and make sure nothing regressed. Report updated metrics and what changed.`, { ...OPTS, label: `improve:r${round}`, phase: 'Integrate', schema: METRICS })
  if (!m) break
  log(`Round ${round}: aggregate ${m.aggregate} (pitch ${m.pitch}, dur ${m.duration}, lyrics ${m.lyrics}, parts ${m.parts})`)
  if (m.aggregate > best + 0.005) { best = m.aggregate; stale = 0 } else stale++
}

// ───────── Review ─────────
phase('Review')
const FINDINGS = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, file: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
  evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['title', 'file', 'severity', 'evidence', 'fix'] } } }, required: ['findings'] }
const LENSES = [
  'MusicXML correctness: validity, divisions/durations summing to measure length per voice, backup/forward, chords, ties, tuplets, key/clef changes mid-piece, pickups/anacrusis, part-list. Load output into music21 (in .venv) and check it parses with no warnings.',
  'Lyrics retention: every lyric syllable in the PDF appears, correct note, syllabic, hyphen/extender, multiple verses, punctuation, non-ASCII (é, ü), lyrics in multi-voice staves assigned to correct voice/part.',
  'Multi-voice / multi-part separation: closed-score SATB split into 4 named parts correctly; piano grand staff NOT split; single-voice staves untouched; voices crossing/unison/shared noteheads; rests for one voice only; mid-piece divisi.',
  'Robustness on unseen real-world PDFs: download 3 fresh open-license PDFs not in corpus (CPDL, Mutopia, MuseScore-exported) and run them; also raster/scanned PDFs, multi-page, landscape, empty/corrupt/encrypted PDFs — check graceful behaviour and helpful messages.',
  'Artifact/browser compliance + UX: dist/pdf2musicxml.html meets every artifact constraint in the context (no doctype/html tags, pinned CDN script hosts only, no fetch to CDNs, theme tokens light/dark, 400px width no horizontal scroll, copy fallback, no alert/print, focus states, size). Test it in Playwright at 1280 and 400 widths, light and dark, with CSP simulation. Check sample auto-converts.',
]
const reviews = await parallel(LENSES.map((lens, i) => () => agent(`${CONTEXT}
You are an ADVERSARIAL reviewer of the app in ${ROOT} (src/, ui/, dist/pdf2musicxml.html, test/). Lens: ${lens}
Actively try to break it. Only report findings you have REPRODUCED with concrete evidence (command + output). Do not fix anything. Return findings.`, { ...OPTS, label: `review:${i + 1}`, phase: 'Review', schema: FINDINGS })))
const allFindings = reviews.filter(Boolean).flatMap(r => r.findings)
log(`${allFindings.length} findings (${allFindings.filter(f => f.severity === 'critical').length} critical)`)

// ───────── Fix ─────────
phase('Fix')
const final = await agent(`${CONTEXT}
Reviewers reproduced these findings in ${ROOT}:\n${JSON.stringify(allFindings, null, 1)}
TASK: Re-verify each, fix all critical and major ones and any cheap minor ones (generalizable fixes). Then npm test (no regressions vs aggregate ${best}), npm run build, and re-verify dist/pdf2musicxml.html in Playwright with CSP simulation (sample converts, no console errors, light/dark, 400px). Write ${ROOT}/README.md (what it does, approach, supported inputs, limitations, corpus attributions/licenses, how to run tests). Report final metrics; in 'changes' list which findings were fixed vs deferred and why.`, { ...OPTS, label: 'fix:final', schema: METRICS })

return { research: { omr: omr?.summary, voices: voices?.summary, probe: probe?.summary, corpus: corpus?.summary }, design: design?.summary, best, final, findings: allFindings.map(f => `${f.severity}: ${f.title}`) }
