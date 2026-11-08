export const meta = {
  name: 'scan-pdf-to-musicxml-fast',
  description: 'Max-parallel ultracode build of a standalone browser OMR app: scanned (image) sheet-music PDFs → MusicXML with lyrics + multi-voice part splitting',
  phases: [
    { title: 'Research', detail: '7 parallel agents: OMR + voice web research, ML/classical/OCR spikes, synthetic + real scan corpora' },
    { title: 'Design', detail: 'single fast design decision' },
    { title: 'Build', detail: '9 parallel module builders' },
    { title: 'Integrate', detail: 'assemble, then parallel module-owner improvement rounds until metrics plateau' },
    { title: 'Review', detail: '6 adversarial lenses' },
    { title: 'Fix', detail: 'parallel module-owner fixers → final integration' },
  ],
}

const ROOT = '/Users/d.sloane/music'
const OPTS = { model: 'opus', effort: 'xhigh' }
const CONTEXT = `
PROJECT: A standalone, client-side JavaScript web app (Optical Music Recognition) that converts SCANNED sheet-music PDFs — i.e. PDFs whose pages are IMAGES (photocopies/scans, e.g. IMSLP/CPDL-style scans, phone scans), NOT born-digital vector PDFs — into MusicXML 4.0 partwise. Requirements:
 1. RETAIN LYRICS (OCR the text under staves, split into syllables with correct syllabic begin/middle/end/single, extenders, multiple verses).
 2. DETECT WHEN ONE STAFF CARRIES MULTIPLE VOICES/PARTS (e.g. hymn/chorale closed score SATB: soprano stems-up + alto stems-down on treble staff, tenor + bass on bass staff; divisi) and SEPARATE THEM INTO DIFFERENT <part>s where relevant (with lyrics attached to the right voices), while NOT splitting e.g. piano grand staves.
 3. Born-digital vector PDFs are a secondary nice-to-have (rasterize every page and use the same OMR path).
Project root: ${ROOT} (not a git repo; files from an aborted earlier run may exist — overwrite freely). Machine: Linux aarch64, 192 cores, sudo available, node v24, python3, lilypond 2.24 + musicxml2ly, poppler-utils (pdftoppm, pdfimages), ghostscript, network access. Many agents work concurrently in this directory: write ONLY the files you are assigned.

DELIVERY TARGET: a claude.ai Artifact = dist/index.html plus supporting files in dist/assets/ (e.g. *.onnx, *.wasm, *.traineddata, worker .js, sample pdf) loaded by RELATIVE URL (fetch('assets/x') works for files published alongside the page). Limits: each binary supporting file <= 15MB, text file <= 16MB, total <= 64MB. Artifact constraints (CSP-enforced):
 - dist/index.html has NO <!doctype>/<html>/<head>/<body> tags; it starts with <title> (2-4 word name), <meta name="claude:viewport-fit-sides" content="cover">, <style>.
 - External scripts ONLY from cdnjs.cloudflare.com (preferred) / cdn.jsdelivr.net/npm / unpkg.com, exact pinned versions, as <script src> tags (UMD globals). fetch/XHR/WASM/worker loads from CDNs are BLOCKED; cross-origin Worker URLs fail. So: pdf.js 3.11.174 UMD from cdnjs (https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js) with its worker as a plain <script> tag (pdf.worker.min.js defines globalThis.pdfjsWorker → main-thread fake worker) or a blob: worker; any WASM (onnxruntime-web, tesseract core, opencv.js) and model weights / traineddata MUST be self-hosted relative files (e.g. ort.env.wasm.wasmPaths='assets/'; Tesseract workerPath/corePath/langPath relative, workerBlobURL as needed). Workers from own files or blob: URLs work.
 - Fonts only from Google Fonts. <a download>/script saves are inert: give MusicXML in a selectable textarea + "Copy" button (navigator.clipboard.writeText in click handler, catch → select()). No alert/confirm/prompt, no window.print.
 - Theme-aware color tokens: light on :root, dark under @media (prefers-color-scheme: dark){:root:not([data-theme="light"]){...;color-scheme:dark}} and again :root[data-theme="dark"]{...}; body background from token. Works at 400px width (no horizontal page scroll), side gutter padding-left:max(16px, env(safe-area-inset-left,0px)) (and right). Avoid generic AI looks (cream+terracotta, Inter, purple gradients, emoji). Visible focus states, prefers-reduced-motion.
 - Opens in a realistic working state: ships a small public-domain SCANNED sample (closed-score SATB hymn/chorale with lyrics) converted on load; user can drop/upload their own PDF (also PNG/JPG). Shows the scanned page with toggleable detection overlay, a notation preview of the result (e.g. OpenSheetMusicDisplay UMD from jsdelivr pinned), per-part summary (incl. which parts were split from shared staves), lyrics preview, warnings/confidence, MusicXML textarea + Copy, progress per stage.
CORE LOGIC is environment-agnostic: the OMR core operates on grayscale page bitmaps ({width,height,data:Uint8ClampedArray}) and runs in node too, so a harness measures accuracy vs ground truth (node rasterizes with pdftoppm/pdfimages + pngjs; uses onnxruntime-node / tesseract.js in node if ML/OCR is used).
LICENSING: everything shipped must be open source compatible with public distribution; prefer MIT/Apache/BSD; flag any AGPL/GPL model or code clearly.
`
const SECTION = { type: 'object', properties: { summary: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'files'] }

// ───────── Research (7 parallel) ─────────
phase('Research')
const RESEARCH = [
  { key: 'web:omr', prompt: `Search the internet (load WebSearch/WebFetch via ToolSearch) for CURRENT (2023-2026) approaches to OMR of SCANNED sheet music → MusicXML; write ${ROOT}/docs/research-omr.md. Cover classical pipelines (binarization Otsu/Sauvola, deskew, staff detection via projections/run-lengths/stable paths, staff removal, connected components, symbol classification, rhythm reconstruction, measure-timing repair); SOTA systems + weights + licences (Audiveris AGPL, oemer MIT ONNX, homr, Polyphonic-TrOMR, SMT Sheet Music Transformer, legato, YOLO detectors on DeepScoresV2/MUSCIMA++; datasets PrIMuS/Camera-PrIMuS/OLiMPiC/GrandStaff); in-browser execution (onnxruntime-web wasm/webgpu, quantization, opencv.js); lyric OCR under staves; evaluation metrics (OMR-NED, TEDn, SER, MV2H). End with a recommended pure-browser architecture. Cite URLs.` },
  { key: 'web:voices', prompt: `Search the internet for current approaches to VOICE / PART SEPARATION in OMR and symbolic music; write ${ROOT}/docs/research-voices.md. Cover: multiple voices on one staff from images (stem direction, shared noteheads/unisons, displaced rests, chords vs two voices, per-voice beams), closed-score SATB, divisi, piano grand staff vs vocal parts, part naming from system-start labels ("S A", "T B"), brace vs bracket, lyric placement & which voices lyrics apply to, MusicXML representation (<voice>, <backup>, <staff>, separate <part>s, <part-group>), algorithms (Audiveris voice/slot model, music21 voicesToParts/explode, contig mapping, stream segregation). Give a decision procedure for WHEN to split voices into separate parts vs keep one part, and handling of uncertain cases. Cite URLs.` },
  { key: 'spike:ml', prompt: `Feasibility spike for PRETRAINED ML OMR models in the browser, in ${ROOT}/spike/ml/. Make test scans (LilyPond melody+lyrics and closed-score SATB with \\voiceOne/\\voiceTwo → pdf → pdftoppm 200/300dpi → degrade with rotation/noise/blur/JPEG). Evaluate oemer ONNX models, homr models, any permissively licensed YOLO music-object detector (DeepScoresV2): licence, sizes, int8/fp16 quantization to <=15MB files, onnxruntime-node accuracy + speed on the scans, and whether onnxruntime-web (pin a known version) runs them with self-hosted wasm. Keep assets in ${ROOT}/spike/ml/assets with provenance. Write numbers + exact versions/URLs + recommendation to ${ROOT}/docs/spike-ml.md.` },
  { key: 'spike:classical', prompt: `Feasibility spike for a CLASSICAL pure-JS OMR pipeline in ${ROOT}/spike/classical/. Make test scans (LilyPond melody+lyrics and closed-score SATB → pdf → pdftoppm 150/200/300dpi → degrade with rotation/noise/blur/JPEG/lighting). Prototype in plain JS (node, pngjs): binarization, deskew, staff-space/line-thickness estimation, staff detection, staff removal, connected components, filled/hollow notehead detection, stem direction, barlines. Measure robustness (precision/recall vs known truth). Write findings with numbers to ${ROOT}/docs/spike-classical.md, keep code reusable.` },
  { key: 'spike:ocr', prompt: `Feasibility spike for LYRIC OCR in ${ROOT}/spike/ocr/. Make test scans with lyrics (English, German, Latin; hyphenated syllables, melismas, 2-3 verses) via LilyPond → pdftoppm → degrade. Evaluate tesseract.js (pin version; self-hosted worker/core/traineddata; eng/deu/lat fast vs best sizes) on cropped lyric strips: character/word accuracy, hyphen detection, speed; alternatives (PaddleOCR ONNX small rec model, etc.) with licences/sizes. Also how to isolate lyric strips from music (staff-free horizontal bands, component heights). Write numbers, exact versions/URLs, recommendation to ${ROOT}/docs/spike-ocr.md.` },
  { key: 'corpus:synthetic', prompt: `Build the SYNTHETIC-SCAN part of the test corpus in ${ROOT}/corpus/synthetic/<id>/ with scan.pdf (image-only), truth.musicxml, attribution; manifest at ${ROOT}/corpus/manifest-synthetic.json: [{id,title,source_url,license,origin:'synthetic-scan',dpi,degradations:[],has_ground_truth:true,features:[lyrics,multi_voice_staff,satb_closed,multi_verse,piano,...],expected_parts:[...]}]. >= 14 items from public-domain/CC0 MusicXML (music21 corpus in venv ${ROOT}/.venv — Bach chorales with lyrics; OpenScore Lieder CC0; folk songs/hymns). Engrave via musicxml2ly+lilypond; for CLOSED-SCORE SATB (several items — key case) write LilyPond with \\voiceOne/\\voiceTwo on two staves + \\lyricsto so truth parts are S/A/T/B. Rasterize (150/200/300 dpi grayscale), degrade at varied strengths (rotation, noise, blur, salt-pepper, JPEG, lighting gradient, slight curvature), wrap as image-only PDFs. Cover single melody+lyrics, multi-verse hymns, SATB closed, SATB open (4 staves), piano solo (must NOT be split), voice+piano. Also make ${ROOT}/corpus/sample-embed.pdf: small (<400KB) scanned-looking closed-score SATB hymn/chorale page with lyrics for the app's default sample, + ${ROOT}/corpus/sample-embed.ATTRIBUTION.txt. Verify image-only (pdffonts empty).` },
  { key: 'corpus:real', prompt: `Build the REAL-SCAN part of the test corpus in ${ROOT}/corpus/real/<id>/ with scan.pdf, optional truth.musicxml, attribution; manifest ${ROOT}/corpus/manifest-real.json (same shape: origin:'real-scan'). Find 5-8 genuinely scanned public-domain pages (IMSLP, CPDL, archive.org, HathiTrust public-domain hymnals/chorale books/song books) — prioritise hymns in closed-score SATB with lyrics, plus a folk song with lyrics and a piano piece. For at least 3 short ones hand-transcribe ground truth MusicXML carefully (verify by engraving your transcription with lilypond and comparing images against the scan). Record licences/provenance precisely.` },
]
const research = await parallel(RESEARCH.map(r => () => agent(`${CONTEXT}\nTASK: ${r.prompt}\nReturn a concise summary (with key numbers) + file paths.`, { ...OPTS, label: r.key, phase: 'Research', schema: SECTION })))
const researchNotes = research.map((r, i) => `[${RESEARCH[i].key}] ${r ? r.summary : 'FAILED'}`).join('\n\n')
log(`Research: ${research.filter(Boolean).length}/${RESEARCH.length} returned`)

// ───────── Design: 3 competing architectures → judge synthesis ─────────
phase('Design')
const design = await agent(`${CONTEXT}
Research results:\n${researchNotes}
TIME IS CRITICAL — the user wants delivery ASAP; decide quickly and favour the lowest-risk approach the spikes proved works. A fast-track v1 exists in ${ROOT}/mvp/ (classical JS + tesseract.js) — read it and reuse what works.
TASK: Choose the architecture from the spike evidence. First merge ${ROOT}/corpus/manifest-synthetic.json and manifest-real.json into ${ROOT}/corpus/manifest.json. Then write ${ROOT}/docs/DESIGN.md with EXACT module contracts for 9 builders working IN PARALLEL without talking. Fixed layout (one owner per file):
 - src/raster.js — input (PDF bytes or image) → page bitmaps via injected env adapters; grayscale, binarization, deskew, noise cleanup, scale normalization.
 - src/staff.js — staff lines (staff space, thickness), systems (brace/bracket), staff removal / staff-relative coords, barlines, measures.
 - src/symbols.js — symbol detection & classification (noteheads, stems, beams, flags, dots, rests, accidentals, clefs, key/time sigs, ties/slurs, ledger lines, tuplets) + model loading via env.
 - src/recognize.js — symbols → score model: pitch (clef+key+accidentals), duration, chords, voices-per-staff, per-measure rhythm repair, cross-system part continuity.
 - src/lyrics.js — lyric strip location, OCR via env, syllables/hyphens/extenders, verses, alignment to notes, voice assignment.
 - src/parts.js — voice→part split decision, part naming (OCR'd labels or inferred), lyric duplication policy.
 - src/musicxml.js — score model → XSD-valid MusicXML 4.0 partwise.
 - src/index.js + build.mjs + test/run.mjs + test/schema + package.json — convert(input,{env,onProgress}) → {musicxml, score, pages:[overlay data], warnings, stats}; build → dist/index.html (all app JS inlined) + dist/assets (size-checked); harness over corpus/manifest.json writing per-item + aggregate metrics (part count/names, measures, pitch, duration, rests, lyric CER + syllabic, voice/part assignment via alignment, XSD validity via xmllint, runtime; split synthetic vs real), aggregate score in [0,1]. Harness CLI MUST support: --out <file> (so concurrent agents don't collide), --only <id,...>, --filter <feature>, and --debug <dir> (overlay PNGs).
 - src/env-node.js + src/env-browser.js — adapters (rasterize, image decode, ONNX session factory, OCR engine factory) [owned by the harness builder (node) and UI builder (browser)].
 - ui/template.html, ui/ui.js, ui/styles.css — the page.
Specify shared JSON data structures at field level (bitmap, staff, system, symbol, note, rest, chord, voice, measure, part, lyric syllable, score, overlay), coordinate conventions, units (staff spaces), confidence fields, warnings, env adapter interface, and asset paths/versions. Write the decision rationale at the top. Return summary + paths.`, { ...OPTS, label: 'design', schema: SECTION })

// ───────── Build (9 parallel) ─────────
phase('Build')
const MODULES = [
  { key: 'raster', files: 'src/raster.js', extra: 'Robust to skew, noise, lighting, DPI. Self-test on corpus scans with debug PNGs in test/debug/raster/.' },
  { key: 'staff', files: 'src/staff.js', extra: 'Build on raster contract (use your own minimal binarization inside test scaffolding if raster.js not ready). Debug PNG overlays in test/debug/staff/; measure staff/system/barline detection vs truth (staff counts from manifest/truth).' },
  { key: 'symbols', files: 'src/symbols.js and assets-src/ (model conversion/quantization scripts + models with provenance)', extra: 'Hardest module. Measure symbol precision/recall on synthetic scans (truth derivable from LilyPond sources / truth.musicxml).' },
  { key: 'recognize', files: 'src/recognize.js', extra: 'Build against symbol/staff fixtures you generate (test/fixtures/recognize/). Rhythm repair and voice detection (stem direction, layers) are key.' },
  { key: 'lyrics', files: 'src/lyrics.js', extra: 'Test OCR on lyric strips cropped from corpus scans; fixtures in test/fixtures/lyrics/.' },
  { key: 'parts', files: 'src/parts.js', extra: 'Fixtures in test/fixtures/parts/ covering closed SATB, open SATB, piano, voice+piano, single melody, ambiguous cases.' },
  { key: 'musicxml', files: 'src/musicxml.js', extra: 'Fixtures in test/fixtures/musicxml/; validate every output with xmllint against the MusicXML 4.0 XSD (download to test/schema if missing — coordinate: harness builder also does this; if present, reuse).' },
  { key: 'harness+build', files: 'src/index.js, src/env-node.js, build.mjs, test/run.mjs, test/schema/, package.json', extra: 'Harness tolerant of missing/failing modules (in-memory stubs only; never write other owners\' files). build.mjs copies assets into dist/assets and enforces size limits.' },
  { key: 'ui', files: 'ui/template.html, ui/ui.js, ui/styles.css, src/env-browser.js', extra: 'Follow the wireframe in docs/ui-refs/ui-mock.excalidraw-elements.json (Excalidraw elements: drop zone, 7-step conversion stepper, page view with overlay, parts/lyrics/warnings column, MusicXML code block, notation preview) and port the 21st.dev patterns in docs/ui-refs/21st-dev.md to plain JS (drag depth counter, accessible stepper with aria-current and sr-only state text, code block with line numbers and copy). Start from the working v1 UI in mvp/ui and mvp/dist/index.html. Distinctive UI from the world of engraving/score scanning (staff-line motifs, measure numbers, terms like "closed score", "divisi", "staff space"). Drop zone + file input (PDF/PNG/JPG), sample auto-loads, per-stage progress, page view with toggleable overlay (staves, systems, barlines, noteheads coloured by voice/part), OSMD preview, per-part list noting parts split from shared staves, lyrics preview, warnings, MusicXML textarea + Copy. Develop against a mock convert() result.' },
]
const built = await parallel(MODULES.map(b => () => agent(`${CONTEXT}
Read ${ROOT}/docs/DESIGN.md (authoritative contracts) and relevant docs/ research + spike code. You own: ${b.files}. Write ONLY these (8 other builders write the rest concurrently). ${b.extra}
Test in isolation as far as possible. Return summary + files + any contract deviations (avoid; if unavoidable, document at top of your file AND in summary).`, { ...OPTS, label: `build:${b.key}`, phase: 'Build', schema: SECTION })))
const buildNotes = built.map((r, i) => `${MODULES[i].key}: ${r ? r.summary : 'FAILED'}`).join('\n')

// ───────── Integrate + parallel improvement rounds ─────────
phase('Integrate')
const METRICS = { type: 'object', properties: {
  aggregate: { type: 'number' }, pitch: { type: 'number' }, duration: { type: 'number' }, lyrics: { type: 'number' },
  parts: { type: 'number' }, xsd_valid_ratio: { type: 'number' }, crashes: { type: 'number' }, real_scan_aggregate: { type: 'number' },
  worst_items: { type: 'array', items: { type: 'string' } }, per_module_issues: { type: 'string' }, changes: { type: 'string' } },
  required: ['aggregate', 'pitch', 'duration', 'lyrics', 'parts', 'xsd_valid_ratio', 'crashes', 'real_scan_aggregate', 'worst_items', 'per_module_issues', 'changes'] }
const BROWSER_CHECK = `verify the built app in a real browser (Playwright via ToolSearch, or npx playwright + chromium): serve dist/ locally with a CSP header simulating the artifact (script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:), confirm the sample converts, overlay + preview render, lyrics appear, no console errors or blocked loads.`

let m = await agent(`${CONTEXT}
Builders finished:\n${buildNotes}
TASK (integrator): In ${ROOT}, make everything work together per docs/DESIGN.md (resolve contract mismatches minimally, in whichever file is wrong), npm run build → dist/index.html + dist/assets, npm test over the whole corpus with no crashes. Then ${BROWSER_CHECK} Report metrics from test/results.json and, in per_module_issues, the main weaknesses attributable to each module (raster/staff, symbols, recognize, lyrics, parts/musicxml).`, { ...OPTS, label: 'integrate', schema: METRICS })
log(`Initial aggregate ${m?.aggregate} (real ${m?.real_scan_aggregate})`)

const OWNERS = [
  { key: 'raster+staff', files: 'src/raster.js, src/staff.js', focus: 'page preprocessing, staff/system/barline/measure detection' },
  { key: 'symbols', files: 'src/symbols.js, assets-src/', focus: 'symbol detection/classification precision & recall' },
  { key: 'recognize', files: 'src/recognize.js', focus: 'pitch, duration, chords, voices-per-staff, rhythm repair' },
  { key: 'lyrics', files: 'src/lyrics.js', focus: 'lyric OCR, syllabic, extenders, verses, alignment, voice assignment' },
  { key: 'parts+musicxml', files: 'src/parts.js, src/musicxml.js', focus: 'voice→part splitting, part naming, MusicXML validity and fidelity' },
]
let best = m?.aggregate ?? 0, stale = 0
for (let round = 1; round <= 2 && stale < 2 && best < 0.95; round++) {
  const imp = await parallel(OWNERS.map(o => () => agent(`${CONTEXT}
Improvement round ${round}. You own ONLY ${o.files} (focus: ${o.focus}); 4 other owners are editing other modules concurrently — never edit their files (if you need a contract change, note it in your summary instead).
Current metrics: ${JSON.stringify(m)}
TASK: Run the harness with node test/run.mjs --out test/results-${o.key}-r${round}.json (plus --only/--debug as useful), study failures relevant to your module (diff vs truth, view scans/overlays as images), fix the highest-impact root causes in your files with generalizable changes (never hard-code corpus content). Re-run to confirm improvement for your area and no crash. Return summary of changes + measured before/after for your area.`, { ...OPTS, label: `improve:r${round}:${o.key}`, phase: 'Integrate', schema: SECTION })))
  m = await agent(`${CONTEXT}
Round ${round}: module owners made concurrent changes:\n${imp.map((r, i) => `${OWNERS[i].key}: ${r ? r.summary : 'FAILED'}`).join('\n')}
TASK (round integrator): In ${ROOT}, run full npm test and npm run build; resolve any cross-module breakage or requested contract changes; if a change regressed the aggregate vs ${best}, fix or revert that part. Report metrics + per_module_issues for the next round.`, { ...OPTS, label: `measure:r${round}`, phase: 'Integrate', schema: METRICS })
  if (!m) break
  log(`Round ${round}: aggregate ${m.aggregate} (pitch ${m.pitch}, dur ${m.duration}, lyrics ${m.lyrics}, parts ${m.parts}, real ${m.real_scan_aggregate})`)
  if (m.aggregate > best + 0.005) { best = m.aggregate; stale = 0 } else stale++
}

// ───────── Review (6 parallel lenses) ─────────
phase('Review')
const FINDINGS = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, file: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
  evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['title', 'file', 'severity', 'evidence', 'fix'] } } }, required: ['findings'] }
const LENSES = [
  'MusicXML correctness: XSD validity, per-voice durations summing to measure length, backup/forward, chords, ties, tuplets, key/clef changes, pickups, part-list. Load outputs into music21 (.venv) and check they parse cleanly.',
  'Lyrics retention: every syllable on the scan appears on the right note with correct syllabic/hyphen/extender; multiple verses; punctuation; non-ASCII (é, ü, æ); lyrics in multi-voice staves on correct voices/parts; OCR robustness on noisy scans.',
  'Multi-voice / multi-part separation: closed SATB → 4 named parts; piano grand staff NOT split; single-voice staves untouched; voice crossing, unisons/shared noteheads, one-voice rests, mid-piece divisi; part continuity across systems/pages.',
  'Robustness on unseen real scans: download 3-4 fresh public-domain scans not in the corpus (IMSLP/CPDL/archive.org hymnals, a phone-photo-like page, a multi-page piece, a 2-up/landscape page) and run them; also corrupt/encrypted/empty/huge PDFs and plain images — graceful behaviour, partial output, time + memory, helpful messages.',
  'Artifact/browser compliance: dist/index.html + dist/assets meet every artifact constraint in the context (no doctype/html tags, pinned CDN script hosts only, wasm/models/traineddata relative, no CDN fetches, size limits, theme tokens, 400px no horizontal scroll, copy fallback, no alert/print, focus states) — test in Playwright with CSP simulation.',
  'UX + visual design: in Playwright at 1280 and 400 widths, light and dark, screenshot and critique hierarchy, legibility, overlay usefulness, progress feedback, error states, upload flow, empty/edge states; check the sample conversion demonstrates the multi-part split and lyrics clearly.',
]
const reviews = await parallel(LENSES.map((lens, i) => () => agent(`${CONTEXT}
You are an ADVERSARIAL reviewer of the app in ${ROOT} (src/, ui/, dist/, test/). Lens: ${lens}
Actively try to break it. Report only findings you REPRODUCED with concrete evidence (command + output / screenshot path). Do not fix anything. Use --out test/results-review-${i + 1}.json if you run the harness.`, { ...OPTS, label: `review:${i + 1}`, phase: 'Review', schema: FINDINGS })))
const allFindings = reviews.filter(Boolean).flatMap(r => r.findings)
log(`${allFindings.length} findings (${allFindings.filter(f => f.severity === 'critical').length} critical)`)

// ───────── Fix: parallel per-owner, then final integration ─────────
phase('Fix')
const FIX_OWNERS = [...OWNERS,
  { key: 'ui', files: 'ui/, src/env-browser.js', focus: 'page UX, design, browser/artifact compliance' },
  { key: 'harness+build', files: 'src/index.js, src/env-node.js, build.mjs, test/', focus: 'pipeline orchestration, build, assets, harness' },
]
const fixes = await parallel(FIX_OWNERS.map(o => () => agent(`${CONTEXT}
Reviewers reproduced these findings:\n${JSON.stringify(allFindings, null, 1)}
You own ONLY ${o.files} (focus: ${o.focus}); other owners fix their files concurrently. Re-verify the findings that fall in your files, fix all critical/major and cheap minor ones with generalizable changes, and confirm (harness with --out test/results-fix-${o.key}.json). Return which findings you fixed vs deferred and why, and any cross-module issue you could not fix.`, { ...OPTS, label: `fix:${o.key}`, phase: 'Fix', schema: SECTION })))

const final = await agent(`${CONTEXT}
Parallel fixers reported:\n${fixes.map((r, i) => `${FIX_OWNERS[i].key}: ${r ? r.summary : 'FAILED'}`).join('\n')}
TASK (final integrator): In ${ROOT}, resolve any remaining cross-module issues, run full npm test (no regression vs aggregate ${best}), npm run build, and ${BROWSER_CHECK} Also check at 400px and in dark mode. Write ${ROOT}/README.md (what it does, approach + research basis, supported inputs, accuracy table from test/results.json split synthetic vs real, limitations, licences + corpus/model attributions, how to run tests). Report final metrics; in 'changes' list fixed vs deferred findings.`, { ...OPTS, label: 'fix:final-integrate', schema: METRICS })

return { research: researchNotes, design: design?.summary, best, final, findings: allFindings.map(f => `${f.severity}: ${f.title}`) }
