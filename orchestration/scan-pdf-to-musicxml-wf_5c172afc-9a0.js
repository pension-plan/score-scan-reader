export const meta = {
  name: 'scan-pdf-to-musicxml',
  description: 'Research, design, build, measure and review a standalone browser OMR app: scanned (image) sheet-music PDFs → MusicXML with lyrics + multi-voice part splitting',
  phases: [
    { title: 'Research', detail: 'web research on raster OMR + voice separation, in-browser ML/OCR feasibility spike, open-source scanned corpus with ground truth' },
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
PROJECT: A standalone, client-side JavaScript web app (Optical Music Recognition) that converts SCANNED sheet-music PDFs — i.e. PDFs whose pages are IMAGES (photocopies/scans, e.g. IMSLP/CPDL-style scans, phone scans), NOT born-digital vector PDFs — into MusicXML 4.0 partwise. Requirements:
 1. RETAIN LYRICS (OCR the text under staves, split into syllables with correct syllabic begin/middle/end/single, extenders, multiple verses).
 2. DETECT WHEN ONE STAFF CARRIES MULTIPLE VOICES/PARTS (e.g. hymn/chorale closed score SATB: soprano stems-up + alto stems-down on treble staff, tenor + bass on bass staff; divisi) and SEPARATE THEM INTO DIFFERENT <part>s where relevant (with lyrics attached to the right voices), while NOT splitting e.g. piano grand staves.
 3. Born-digital vector PDFs are a secondary nice-to-have (can be handled by simply rasterizing every page and using the same OMR path).
Project root: ${ROOT} (not a git repo). Machine: Linux aarch64, 192 cores, sudo available, node v24, python3, lilypond 2.24 + musicxml2ly, poppler-utils (pdftoppm, pdfimages), ghostscript, network access.

DELIVERY TARGET: a claude.ai Artifact = dist/index.html plus optional supporting files in dist/ (e.g. dist/assets/*.onnx, *.wasm, *.traineddata, worker .js) that the page loads by RELATIVE URL (fetch('assets/x') works for files published alongside the page). Limits: each binary supporting file <= 15MB, text file <= 16MB, total publish <= 64MB. Artifact constraints (CSP-enforced):
 - dist/index.html has NO <!doctype>/<html>/<head>/<body> tags; it starts with <title> (2-4 word name), <meta name="claude:viewport-fit-sides" content="cover">, <style>.
 - External scripts ONLY from cdnjs.cloudflare.com (preferred) / cdn.jsdelivr.net/npm / unpkg.com, exact pinned versions, loaded as <script src> tags (UMD globals). fetch/XHR/WASM/worker loads from CDNs are BLOCKED, and cross-origin Worker URLs fail. Therefore: pdf.js 3.11.174 UMD from cdnjs (https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js) with its worker either as a plain <script> tag (pdf.worker.min.js defines globalThis.pdfjsWorker → main-thread fake worker) or a blob: worker; any WASM (onnxruntime-web, tesseract core, opencv.js) and model weights / traineddata MUST be self-hosted as relative supporting files (e.g. ort.env.wasm.wasmPaths='assets/'; Tesseract workerPath/corePath/langPath pointing at relative assets, workerBlobURL as needed). Web Workers from own files or blob: URLs work.
 - Fonts only from Google Fonts. Downloads via <a download>/script saves are inert in the viewer: give the MusicXML in a selectable textarea + "Copy" button (navigator.clipboard.writeText inside click handler, catch → select()). No alert/confirm/prompt, no window.print.
 - Theme-aware color tokens: light on :root, dark under @media (prefers-color-scheme: dark){:root:not([data-theme="light"]){...;color-scheme:dark}} and again :root[data-theme="dark"]{...}; body background from token. Works at 400px width (no horizontal page scroll), side gutter padding-left:max(16px, env(safe-area-inset-left,0px)) (and right). Avoid generic AI looks (cream+terracotta, Inter, purple gradients, emoji). Visible focus states, prefers-reduced-motion.
 - Must open in a realistic working state: ships a small public-domain SCANNED sample (closed-score SATB hymn/chorale with lyrics) that is converted on load (or one click with results pre-shown); user can drop/upload their own PDF (also accept PNG/JPG images). Show the scanned page with detected staves/symbols overlaid (debug overlay toggle), a rendered notation preview of the result (e.g. OpenSheetMusicDisplay UMD from jsdelivr pinned), per-part summary (incl. which parts were split from shared staves), lyrics preview, warnings/confidence, MusicXML textarea + Copy, plus progress for slow steps.
CORE LOGIC must be environment-agnostic: the OMR core operates on grayscale page bitmaps ({width,height,data:Uint8ClampedArray}) and must run in node too, so a test harness can measure accuracy vs ground truth (node can rasterize with pdftoppm/pdfimages + pngjs, and use onnxruntime-node / tesseract.js-node equivalents if ML/OCR is used).
LICENSING: everything shipped must be open source compatible with public distribution; prefer MIT/Apache/BSD; flag any AGPL/GPL model or code clearly.
`

const SECTION = { type: 'object', properties: { summary: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'files'] }

// ───────── Research ─────────
phase('Research')
const [omr, voices, spike, corpus] = await parallel([
  () => agent(`${CONTEXT}
TASK: Search the internet (WebSearch/WebFetch — load via ToolSearch) for CURRENT (2023-2026) approaches to optical music recognition of SCANNED sheet music → MusicXML, and write ${ROOT}/docs/research-omr.md.
Cover: (1) classical pipelines: binarization (Otsu/Sauvola), deskew, staff-line detection (horizontal projection, run-length staff-space/line-thickness estimation, Fujinaga/Cardoso stable paths), staff removal, connected components, symbol segmentation & classification (template matching, kNN/HOG, small CNNs), stems/beams/ledger lines, rhythm reconstruction, measure timing consistency repair; (2) state of the art systems and their available models/weights + licences: Audiveris (Java, AGPL), oemer (MIT, ONNX UNets), homr (TrOMR-based, check licence), Polyphonic-TrOMR, SMT / Sheet Music Transformer (end-to-end page-level), legato, Zeus/others, YOLO-based music object detectors trained on DeepScoresV2 / MUSCIMA++, CVC-MUSCIMA, PrIMuS/Camera-PrIMuS, OLiMPiC, GrandStaff datasets; (3) running these in the browser: onnxruntime-web (wasm/webgpu), model sizes & quantization, opencv.js, speed on CPU; (4) lyric OCR under staves: tesseract.js self-hosting, isolating lyric lines from the music, hyphen/extender detection, multiple verses; (5) evaluation metrics (OMR-NED, TEDn, SER, MV2H).
End with a concrete recommended architecture for a pure-browser JS app (what to use, what to build ourselves, expected accuracy, sizes) given the artifact constraints. Cite URLs. Return a concise summary + file paths.`, { ...OPTS, label: 'research:omr', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Search the internet for current approaches to VOICE / PART SEPARATION in OMR and symbolic music, and write ${ROOT}/docs/research-voices.md.
Cover: identifying multiple voices on one staff from an image (stem direction, shared noteheads/unisons, rests displaced vertically, chords vs two voices, beam groups per voice), closed-score SATB conventions, divisi, piano grand staff vs vocal parts, part naming from instrument labels at system start (e.g. "S A", "T B", "Soprano/Alto"), brace vs bracket semantics, lyrics placement (lyrics between staves; hymn lyrics under the treble staff applying to S and A — and often T/B too), and how MusicXML represents this (<voice>, <backup>, <staff>, separate <part>s, <part-group>). Include algorithms from literature (Audiveris voice/slot model, music21 voicesToParts/explode, contig mapping, stream segregation, OMR voice assignment heuristics). Give a recommended decision procedure for WHEN to split a staff's voices into separate parts vs keep one part with multiple <voice>s, plus how to handle uncertain cases. Cite URLs. Return summary + file paths.`, { ...OPTS, label: 'research:voices', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Feasibility spike for in-browser raster OMR + lyric OCR. Work in ${ROOT}/spike/. Make a few test scans yourself: write small LilyPond pieces (melody with hyphenated/melisma lyrics; closed-score SATB with \\voiceOne/\\voiceTwo and lyrics), compile to PDF, rasterize with pdftoppm at 200 and 300 dpi, degrade (slight rotation 0.5-2°, gaussian noise, blur, JPEG artifacts, uneven lighting) and wrap back into image-only PDFs. Also download 1-2 real public-domain scans (IMSLP/CPDL/archive.org hymnals).
Then evaluate candidate approaches empirically, in node where possible:
 (a) Pretrained models: try oemer's ONNX models (pip/github; check sizes, licence, onnxruntime-node inference on our scans: staff/symbol segmentation quality, speed), homr (check licence + model formats/sizes), any small YOLO music-object detector with permissive weights (DeepScoresV2-trained). Can each be served as <=15MB files (quantize to int8/fp16 with onnxruntime tools if needed)? Does onnxruntime-web (pin a version, e.g. 1.17-1.20 era from jsdelivr) run them with self-hosted wasm?
 (b) Classical JS pipeline: quickly prototype staff detection + staff removal + connected components + notehead detection on our scans in plain JS; measure how robust it is.
 (c) Lyric OCR: tesseract.js self-hosted (pin version; worker/core/traineddata as local files; check sizes of eng/lat 'fast' vs 'best' traineddata) on cropped lyric strips; measure word accuracy; check languages (Latin, German, English hymn lyrics).
Write precise findings with numbers (accuracy, timing, file sizes, licences, exact package versions + file URLs that worked) and a recommendation in ${ROOT}/docs/spike.md. Keep downloaded models/assets under ${ROOT}/spike/assets/ (note provenance). Return summary + file paths.`, { ...OPTS, label: 'research:spike', schema: SECTION }),

  () => agent(`${CONTEXT}
TASK: Build an OPEN-SOURCE SCANNED test corpus with ground truth in ${ROOT}/corpus/. Each item: a folder with scan.pdf (image-only PDF), truth.musicxml (ground truth), attribution/licence note, and an entry in ${ROOT}/corpus/manifest.json: {id, title, source_url, license, origin ('synthetic-scan' | 'real-scan'), dpi, degradations:[...], has_ground_truth, features:[lyrics, multi_voice_staff, satb_closed, multi_verse, piano, ...], expected_parts:[names]}.
Aim for >= 16 items:
 - SYNTHETIC SCANS with exact ground truth: take public-domain/CC0 MusicXML (music21 corpus in a venv at ${ROOT}/.venv — Bach chorales with lyrics; OpenScore Lieder github.com/OpenScore/Lieder CC0; folk songs/hymns), engrave via musicxml2ly+lilypond (for CLOSED-SCORE SATB, write LilyPond yourself with \\voiceOne/\\voiceTwo on two staves + \\lyricsto so truth parts are S/A/T/B), rasterize (pdftoppm 150/200/300 dpi, grayscale), apply realistic scan degradations at varied strengths (rotation, noise, blur, salt-pepper, JPEG, lighting gradient, slight page curvature for a couple), wrap as image-only PDFs (img2pdf or gs). Cover: single melody + lyrics, multi-verse hymns, SATB closed score (the key multi-part-per-staff case, several items), SATB open score (4 staves), piano solo (grand staff — must NOT be split), voice + piano.
 - REAL SCANS: 3-5 genuinely scanned public-domain pages (IMSLP / CPDL / archive.org / Hathi public-domain hymnals) — for at least 2 short ones (e.g. a single hymn), hand-transcribe ground truth MusicXML carefully (verify by engraving your transcription with lilypond and comparing visually to the scan with pdftoppm images); others as smoke tests without truth.
Also produce ${ROOT}/corpus/sample-embed.pdf: a SMALL (<400KB) public-domain scanned-looking closed-score SATB hymn/chorale page with lyrics, for shipping as the app's default sample (+ attribution).
Verify every PDF is image-only (pdffonts empty, pdfimages lists images). Return summary + manifest stats + file paths.`, { ...OPTS, label: 'research:corpus', schema: SECTION }),
])
log(`Research done: ${[omr, voices, spike, corpus].filter(Boolean).length}/4 agents returned`)

// ───────── Design ─────────
phase('Design')
const design = await agent(`${CONTEXT}
Read ${ROOT}/docs/research-omr.md, ${ROOT}/docs/research-voices.md, ${ROOT}/docs/spike.md, ${ROOT}/corpus/manifest.json (and look at spike/ and corpus/).
Research summaries: OMR: ${omr?.summary}\nVOICES: ${voices?.summary}\nSPIKE: ${spike?.summary}\nCORPUS: ${corpus?.summary}
TASK: Choose the architecture (use the spike's evidence: pretrained ONNX models vs classical JS vs hybrid; OCR approach) and write ${ROOT}/docs/DESIGN.md with EXACT module contracts that 5 builders implement IN PARALLEL without talking to each other. Fixed layout:
 - src/raster.js — input (PDF bytes or image) → page bitmaps; environment adapters injected (browser: pdf.js render to canvas / decode images; node: provided by harness). Preprocessing: grayscale, binarization, deskew, noise cleanup, DPI/scale normalization.
 - src/staff.js — staff-line detection (staff space, line thickness), staff grouping into systems (brace/bracket detection), staff removal / staff-relative coordinates, barline detection, measure segmentation.
 - src/symbols.js — symbol detection & classification (noteheads filled/hollow/whole, stems, beams, flags, dots, rests, accidentals, clefs, key/time signatures, ties/slurs, ledger lines, tuplet numbers) — via ML models (onnxruntime-web/node, models in assets/) and/or classical methods per the design decision.
 - src/recognize.js — symbols → score model: pitches (clef + key + measure-scoped accidentals), durations (with beam/flag/dot), chords, voices-per-staff (stem-direction/layer analysis), rhythmic consistency repair per measure (fill/trim to time signature, flag low confidence), part/staff identity across systems.
 - src/lyrics.js — locate lyric strips between/under staves, OCR (e.g. self-hosted tesseract.js), syllable segmentation by hyphens/gaps, align syllables to note x-positions, extenders, verse numbering, which voice(s) each lyric line belongs to.
 - src/parts.js — voice→part split decision (closed-score SATB → separate parts; piano → not), part names (from OCR'd labels if present, else inferred S/A/T/B etc.), lyric duplication policy.
 - src/musicxml.js — score model → MusicXML 4.0 partwise string valid against the XSD (divisions, attributes, notes, chords, rests, voices, backup, ties, tuplets, beams, lyrics, part-list, part-groups).
 - src/index.js — convert(input, {env, onProgress}) → {musicxml, score, pages:[{overlay data}], warnings, stats}.
 - ui/ (template.html, ui.js, styles.css) + build.mjs → dist/index.html (all app JS inlined; no runtime ES module imports) + dist/assets/* (models, wasm, traineddata, sample). Sizes within artifact limits.
 - test/run.mjs — node harness: runs convert() over corpus/manifest.json, compares to truth.musicxml, writes test/results.json with per-item + aggregate: part count/name match, measure count, note pitch accuracy, duration accuracy, rest accuracy, lyric syllable accuracy (text CER + syllabic), voice/part assignment accuracy (alignment per part by measure+onset, sequence alignment tolerant to insertions/deletions), XSD validity (download MusicXML 4.0 XSD to test/schema, use xmllint), runtime. Define an aggregate score in [0,1] and per-feature breakdown (synthetic vs real scans, degradation levels).
Specify shared score-model and symbol data structures (JSON shapes) at field-level precision, coordinate conventions, units (staff spaces), confidence fields, warning conventions, and the env-adapter interface (how browser vs node supply rasterization, ONNX session creation, OCR). Assign each concern to exactly one module. Return summary + paths.`, { ...OPTS, label: 'design', schema: SECTION })

// ───────── Build ─────────
phase('Build')
const BUILDERS = [
  { key: 'raster+staff', files: 'src/raster.js, src/staff.js', extra: 'Must be robust to skew, noise, uneven lighting and varied DPI. Verify on corpus scans and write a debug renderer (PNG overlays in test/debug/) to eyeball staff/system/barline detection.' },
  { key: 'symbols+recognize', files: 'src/symbols.js, src/recognize.js, and any model/asset prep under assets-src/ (conversion/quantization scripts, models copied with provenance)', extra: 'Hardest module. Implement per DESIGN.md; you may assume staff.js output shapes and build against fixtures you generate (e.g. run your own quick staff detection only inside test scaffolding). Measure symbol-level precision/recall on synthetic scans (ground truth available from the LilyPond/MusicXML sources).' },
  { key: 'lyrics+parts+musicxml', files: 'src/lyrics.js, src/parts.js, src/musicxml.js', extra: 'Build against hand-written score-model fixtures matching DESIGN.md (test/fixtures/). Validate musicxml output with xmllint against the XSD. Test lyric OCR on cropped strips from corpus scans.' },
  { key: 'harness+build', files: 'src/index.js, build.mjs, test/run.mjs, test/schema/, package.json (deps + scripts: npm run build, npm test)', extra: 'Harness must be robust and tolerant of missing/failing modules (in-memory stubs only for your own testing — never overwrite other builders\' files). build.mjs copies assets into dist/assets and enforces size limits.' },
  { key: 'ui', files: 'ui/template.html, ui/ui.js, ui/styles.css', extra: 'Design a distinctive UI from the world of engraving/score scanning (staff-line motifs, measure numbers, part names, real terms of art like "closed score", "divisi", "staff space"). Drop zone + file input (PDF/PNG/JPG), sample auto-loads, progress per stage, page view with toggleable detection overlay (staves, systems, barlines, noteheads coloured by voice/part), notation preview (OSMD), per-part list noting which parts were split from shared staves, lyrics preview, warnings, MusicXML textarea + Copy. Develop against a mock convert() result.' },
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
  real_scan_aggregate: { type: 'number' },
  worst_items: { type: 'array', items: { type: 'string' } }, changes: { type: 'string' } },
  required: ['aggregate', 'pitch', 'duration', 'lyrics', 'parts', 'xsd_valid_ratio', 'crashes', 'real_scan_aggregate', 'worst_items', 'changes'] }

let m = await agent(`${CONTEXT}
Builders finished:\n${buildNotes}
TASK (integrator): In ${ROOT}, make everything work together per docs/DESIGN.md: resolve contract mismatches, npm run build produces dist/index.html + dist/assets, npm test runs test/run.mjs over the whole corpus with no crashes. Then verify the built app in a real browser (Playwright tools via ToolSearch, or npx playwright + chromium): serve dist/ locally with a CSP header simulating the artifact (script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:), confirm the sample converts, overlay + preview render, lyrics appear, no console errors, no blocked loads. Report metrics from test/results.json.`, { ...OPTS, label: 'integrate', schema: METRICS })
log(`Initial aggregate ${m?.aggregate} (real scans ${m?.real_scan_aggregate})`)

let best = m?.aggregate ?? 0, stale = 0
for (let round = 1; round <= 7 && stale < 2 && best < 0.95; round++) {
  m = await agent(`${CONTEXT}
Improvement round ${round}. Current metrics: ${JSON.stringify(m)}.
TASK: In ${ROOT}, run npm test, study test/results.json and the worst items (diff produced vs truth MusicXML; look at the scans and debug overlays as images). Fix the highest-impact root causes in src/ (generalizable fixes only — never hard-code corpus content or tune to one file). Prioritise: crashes > XSD validity > staff/system detection > part/voice separation for multi-voice staves > pitch > duration/rhythm consistency > lyrics (OCR, syllabic, extenders, verses) > rests/ties/tuplets. Watch real-scan performance as well as synthetic. Re-run npm test + npm run build; make sure nothing regressed. Report updated metrics and what changed.`, { ...OPTS, label: `improve:r${round}`, phase: 'Integrate', schema: METRICS })
  if (!m) break
  log(`Round ${round}: aggregate ${m.aggregate} (pitch ${m.pitch}, dur ${m.duration}, lyrics ${m.lyrics}, parts ${m.parts}, real ${m.real_scan_aggregate})`)
  if (m.aggregate > best + 0.005) { best = m.aggregate; stale = 0 } else stale++
}

// ───────── Review ─────────
phase('Review')
const FINDINGS = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, file: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
  evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['title', 'file', 'severity', 'evidence', 'fix'] } } }, required: ['findings'] }
const LENSES = [
  'MusicXML correctness: XSD validity, divisions/durations summing to measure length per voice, backup/forward, chords, ties, tuplets, key/clef changes, pickup measures, part-list. Load outputs into music21 (.venv) and check they parse cleanly.',
  'Lyrics retention: every lyric syllable on the scan appears, on the right note, correct syllabic/hyphen/extender, multiple verses, punctuation, non-ASCII (é, ü, æ), lyrics in multi-voice staves assigned to correct voices/parts; OCR robustness on noisy scans.',
  'Multi-voice / multi-part separation: closed-score SATB split into 4 named parts correctly; piano grand staff NOT split; single-voice staves untouched; voice crossing, unisons/shared noteheads, rests for one voice only, mid-piece divisi; system-to-system part continuity.',
  'Robustness on unseen real scans: download 3-4 fresh public-domain scans not in the corpus (IMSLP/CPDL/archive.org hymnals, a phone-photo-like page you degrade yourself, a multi-page piece, landscape/2-up page) and run them; also corrupt/encrypted/empty/huge PDFs and plain images — check graceful behaviour, sensible partial output, performance (time + memory), helpful messages.',
  'Artifact/browser compliance + UX: dist/index.html + dist/assets meet every artifact constraint in the context (no doctype/html tags, pinned CDN script hosts only, all wasm/models/traineddata relative, no CDN fetches, per-file and total size limits, theme tokens light/dark, 400px no horizontal scroll, copy fallback, no alert/print, focus states). Test in Playwright at 1280 and 400 widths, light and dark, with CSP simulation; check sample conversion, overlay toggle, upload flow.',
]
const reviews = await parallel(LENSES.map((lens, i) => () => agent(`${CONTEXT}
You are an ADVERSARIAL reviewer of the app in ${ROOT} (src/, ui/, dist/, test/). Lens: ${lens}
Actively try to break it. Only report findings you have REPRODUCED with concrete evidence (command + output). Do not fix anything. Return findings.`, { ...OPTS, label: `review:${i + 1}`, phase: 'Review', schema: FINDINGS })))
const allFindings = reviews.filter(Boolean).flatMap(r => r.findings)
log(`${allFindings.length} findings (${allFindings.filter(f => f.severity === 'critical').length} critical)`)

// ───────── Fix ─────────
phase('Fix')
const final = await agent(`${CONTEXT}
Reviewers reproduced these findings in ${ROOT}:\n${JSON.stringify(allFindings, null, 1)}
TASK: Re-verify each, fix all critical and major ones and any cheap minor ones (generalizable fixes). Then npm test (no regressions vs aggregate ${best}), npm run build, and re-verify dist/ in Playwright with CSP simulation (sample converts, no console errors, light/dark, 400px). Write ${ROOT}/README.md (what it does, approach, research basis, supported inputs, accuracy table from test/results.json, limitations, licences + corpus/model attributions, how to run tests). Report final metrics; in 'changes' list which findings were fixed vs deferred and why.`, { ...OPTS, label: 'fix:final', schema: METRICS })

return { research: { omr: omr?.summary, voices: voices?.summary, spike: spike?.summary, corpus: corpus?.summary }, design: design?.summary, best, final, findings: allFindings.map(f => `${f.severity}: ${f.title}`) }
