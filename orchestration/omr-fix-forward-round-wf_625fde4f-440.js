export const meta = {
  name: 'omr-fix-forward-round',
  description: 'One fix-forward round on the live v1 OMR app: (round 1: fast eval harness) → parallel module fixers → integrate, measure, revert regressions, rebuild, browser-check',
  phases: [
    { title: 'Harness', detail: 'fast corpus eval for mvp/ (round 1 only)' },
    { title: 'Fix', detail: 'parallel owners, one set of files each' },
    { title: 'Integrate', detail: 'measure, revert regressions, rebuild, browser check' },
  ],
}

const ROOT = '/Users/d.sloane/music'
const MVP = `${ROOT}/mvp`
const OPTS = { model: 'opus', effort: 'xhigh' }
const R = args.round
const CTX = `
You are improving a LIVE browser app that converts SCANNED sheet-music PDFs (images) into MusicXML 4.0, keeping lyrics and splitting closed-score SATB (two voices per staff, stems up/down) into separate parts, but never splitting piano grand staves. Never run filesystem-wide searches (find / ..., locate) — this machine hosts many large projects; search only under ${ROOT}. Put a timeout on any long command (timeout 600 ...). Strategy: FAIL FAST, FIX FORWARD — small, measured, generalizable improvements; ship every round; never leave the app broken.
Code: ${MVP}/src/*.js (pure-JS pipeline: image, binarize, skew, staffspace, staves, staffremoval, cc, stems, barlines, heads, front, assemble, lyrics, score, omr), UI ${MVP}/ui/, build: node ${MVP}/tools/build.js → ${MVP}/dist/index.html (+ dist/assets: tesseract worker/core/eng.traineddata.gz, sample-st-anselm.pdf). Node runner: node ${MVP}/tools/run.js page.pgm out.musicxml [--no-ocr]. Browser test: node ${MVP}/tools/pw/test.js (Playwright, CSP-simulated). Existing scorers: ${MVP}/tools/headeval.js, ${MVP}/tools/score_cmp.py.
Test data: ${ROOT}/corpus/synthetic/<id>/ (scan.pdf + truth.musicxml, LilyPond-engraved then degraded) and ${ROOT}/corpus/real/<id>/ (real 1867–1923 public-domain scans; some have truth.musicxml). Other agents may still be writing corpus/ and spike/ — read only; also ${ROOT}/docs/research-*.md, ${ROOT}/docs/spike-*.md if present, ${ROOT}/docs/SDD.md.
Artifact constraints for dist/index.html (do not break): no doctype/html/head/body tags; scripts only pinned from cdnjs/jsdelivr/unpkg; all wasm/worker/traineddata loaded by RELATIVE path from assets/ (fetched as text → blob: URLs); no alert/confirm/prompt/print/downloads; theme tokens light+dark; works at 400px without horizontal scroll; each asset <= 15MB.
Eval harness: ${MVP}/tools/eval.mjs — run with: node ${MVP}/tools/eval.mjs --out <file> [--only id,...] [--no-ocr]. CHALLENGE SET: if ${ROOT}/corpus/challenge/manifest.json exists, also run eval with --set challenge (edge cases: voices, rhythm, pitch, lyrics, layout, scan damage extremes; see corpus/challenge/README.md) and use its failures to prioritise; the default 19-item benchmark remains the regression gate. Write your eval output ONLY to ${MVP}/work/eval-r${R}-<yourkey>.json (other agents run it concurrently).
`
const LIMITS = [
  { id: 'L1', text: 'Hollow noteheads sometimes missed (main source of rhythm errors)', owner: 'heads' },
  { id: 'L2', text: 'Key signatures unreliable on old engraving', owner: 'symbols' },
  { id: 'L3a', text: 'Rests not detected', owner: 'symbols' },
  { id: 'L3b', text: 'Ties and slurs not detected (stray slur near a stem tip makes a false 16th)', owner: 'symbols' },
  { id: 'L3c', text: 'Triplets / tuplets not detected', owner: 'symbols' },
  { id: 'L3d', text: 'Mid-piece clef and key changes not detected', owner: 'symbols' },
  { id: 'L3e', text: 'Part names not read (OCR the system-start labels, e.g. S A / T B, Soprano, Piano; fall back to inferred names)', owner: 'lyrics (OCR) + score (apply)' },
  { id: 'L4a', text: 'Lyric alignment drifts when the note count is off (align by x-position/onset, not order)', owner: 'score + lyrics' },
  { id: 'L4b', text: 'No melisma / extender handling (<extend/>, syllable held over several notes, slur-aware)', owner: 'lyrics + score' },
  { id: 'L5a', text: 'At most 8 PDF pages processed (raise the cap, process pages incrementally with per-page progress, stay responsive)', owner: 'ui' },
  { id: 'L6', text: 'Piano wrongly split: grand staves become S/A/T/B and voice+piano gets 4 parts instead of 2 (HARD rule: never split piano; items tagged must_not_split)', owner: 'score' },
  { id: 'L7', text: 'Lyrics attached to every part in closed score (3-4x too many syllables): attach to the voice(s) the text is printed under, copy to other voices only per the research-voices policy', owner: 'score + lyrics' },
  { id: 'L8', text: 'Lyric text or other glyphs read as noteheads on single-melody pages (Jeanie 262 notes vs 95)', owner: 'heads' },
  { id: 'L9', text: 'Part names generic or wrong (open score shows Staff N; TTBB named SATB with an octave error from treble-8vb clef)', owner: 'score + symbols' },
  { id: 'L10', text: 'Pages rotated 90 deg produce nothing; 180 deg pages read badly: detect page orientation (0/90/180/270) and rotate before staff detection', owner: 'heads' },
  { id: 'L11', text: 'Halftone screens and heavy noise blank the page (35 of 365 challenge files produce no notes): descreen / denoise adaptively', owner: 'heads' },
  { id: 'L12', text: 'Two-page spreads read as one wide system (8-13 parts): detect a gutter and split the page into two before staff detection', owner: 'heads' },
  { id: 'L13', text: 'Tuplets impossible with 8 divisions per quarter: move to divisions >= 24 (e.g. 48), detect tuplet numbers/brackets and emit <time-modification>/<tuplet>', owner: 'symbols + score' },
  { id: 'L14', text: 'Double dots, multi-bar rests (H-bar / old-style) and whole-bar rests', owner: 'symbols + score' },
  { id: 'L15', text: 'Double sharps/flats and 8va/8vb brackets', owner: 'symbols' },
  { id: 'L16', text: 'Mid-piece key and time-signature changes not written; C clefs (alto/tenor) not read', owner: 'symbols + score' },
  { id: 'L17', text: 'Two voices inside one part (piano right hand, divisi on one staff of an open score) merged into chords: emit separate <voice>s within the part', owner: 'score' },
  { id: 'L18', text: 'A bracketed instrument pair (violin + cello) read as a piano grand staff; organ pedal staff becomes a separate part: use brace vs bracket and part labels', owner: 'score' },
  { id: 'L5b', text: 'Stanza text printed below the last system is dropped for SATB (OCR it; attach as extra verses when syllable counts fit the melody, else keep as <credit>/words text)', owner: 'lyrics + score' },
]
const LIMIT_TEXT = LIMITS.map(l => `${l.id} [${l.owner}]: ${l.text}`).join('\n')
const SECTION = { type: 'object', properties: { summary: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'files'] }
const METRICS = { type: 'object', properties: {
  aggregate: { type: 'number' }, pitch: { type: 'number' }, duration: { type: 'number' }, lyrics: { type: 'number' }, parts: { type: 'number' },
  xml_valid_ratio: { type: 'number' }, crashes: { type: 'number' }, real_scan_aggregate: { type: 'number' },
  per_owner_issues: { type: 'string' }, changes: { type: 'string' }, reverted: { type: 'string' }, browser_ok: { type: 'boolean' },
  limits: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, status: { type: 'string', enum: ['resolved', 'partial', 'open'] }, evidence: { type: 'string' } }, required: ['id', 'status', 'evidence'] } } },
  required: ['aggregate', 'pitch', 'duration', 'lyrics', 'parts', 'xml_valid_ratio', 'crashes', 'real_scan_aggregate', 'per_owner_issues', 'changes', 'reverted', 'browser_ok', 'limits'] }

let baseline = args.metrics || null
if (R === 1) {
  phase('Harness')
  baseline = await agent(`${CTX}
TASK (harness, be quick — target 15 minutes): Write ${MVP}/tools/eval.mjs if it doesn't exist: for every corpus item with truth.musicxml (synthetic + real), rasterize scan.pdf (pdftoppm -gray -r 200, cache PGMs under ${MVP}/work/cache/), run the v1 pipeline in node (reuse tools/run.js logic; OCR optional via --no-ocr, default ON using spike/ocr node_modules tesseract), compare with truth: per part (match produced parts to truth parts by order/name), per measure+onset alignment with sequence alignment tolerant to insertions/deletions; metrics in [0,1]: pitch, duration, rests, lyrics (syllable text + syllabic accuracy on aligned notes), parts (part count/name match and share of notes in the right part), xml_valid (xmllint --noout well-formedness; XSD if a schema is available in ${ROOT}/test/schema or download MusicXML 4.0 XSD to ${MVP}/work/schema), crashes, runtime; aggregate = 0.3 pitch + 0.2 duration + 0.2 parts + 0.2 lyrics + 0.1 xml_valid; split synthetic vs real (real_scan_aggregate). Support --out, --only, --no-ocr, --jobs N (parallel child processes; machine has 192 cores). Print a compact table and write JSON. Also snapshot the current src as ${MVP}/work/src-r0/ (baseline for reverts). Run it once over everything and report the metrics.`, { ...OPTS, label: 'harness', phase: 'Harness', schema: METRICS })
  log(`Baseline aggregate ${baseline?.aggregate} (real ${baseline?.real_scan_aggregate})`)
}

phase('Fix')
const OPEN = (args.limits || []).filter(l => l.status !== 'resolved').map(l => l.id)
const limitNote = `KNOWN LIMITS CHECKLIST (each round must resolve as many as possible; ${OPEN.length ? 'still open: ' + OPEN.join(', ') : 'all listed'}):\n${LIMIT_TEXT}\nResolve the limits assigned to you. A limit is resolved only with evidence (eval delta, or a corpus item / test case that now passes).`
const OWNERS = [
  { key: 'heads', files: 'src/heads.js, src/stems.js, src/front.js, src/staves.js, src/staffremoval.js, src/binarize.js', focus: 'adopt docs/spike-classical.md fixes: font-independent head rules, lenient second pass for hairline stems (+33% heads on a real page), more than one staff size per page (Amen staves), minimum-contrast check for dark corners, no 3x3 median at low dpi, projection-based staff-space fallback; notehead recall/precision (hollow heads next to accidentals, thick-walled engraving), stems, staff detection failures (e.g. thin-line scans returning "no staves"), skew/curvature robustness' },
  { key: 'symbols', files: 'src/assemble.js', focus: 'triplets/tuplets (L3c), mid-piece clef and key changes (L3d), key signature reading on old engraving (America read 0 sharps, Tappan-Dennis 0), clef classification, accidentals, rests detection (currently none), dots, beams/flags vs stray slurs causing false 16ths, ties' },
  { key: 'score', files: 'src/score.js, src/omr.js', focus: 'apply OCR part names (L3e), align lyrics by x/onset not order (L4a), emit <extend/> and melismas (L4b), attach stanza verses from below the music when they fit (L5b), voice assignment and closed-score S/A/T/B split (decision procedure in docs/research-voices.md §11: vocal score >=3 split, <=-1 keep), unisons/shared noteheads, rhythm repair per measure (search instead of padding rests), time signature, pickup measures, MusicXML validity (durations sum per voice, backup), lyric copy to voices by onset' },
  { key: 'lyrics', files: 'src/lyrics.js', focus: 'adopt the OCR spike results (docs/spike-ocr.md): port spike/ocr/src/strips.js lyric-line detector (100% line recall, hyphen/extender positions), switch to tesseract.js 7.0.0 best_int eng+deu+lat models self-hosted (NOT tessdata_best float, it crashes), PSM 7, close up wide syllable gaps before OCR, split unhyphenated syllables by note matching; OCR of part-name labels at system starts (L3e: expose them for score.js), melisma/extender detection (L4b), stanza text below the last system (L5b: OCR and hand over as extra verses), lyric line detection between staves, OCR quality (tesseract params, crop scaling), syllable splitting and hyphen/extender detection, verse numbers stripped, multiple verses, alignment inputs (syllable x positions) — coordinate with score owner only via your summary' },
  { key: 'ui', files: 'ui/ (all), tools/build.js', focus: 'raise the 8-page cap with incremental per-page processing and progress (L5a); implement the wireframe docs/ui-refs/ui-mock.excalidraw-elements.json and port the 21st.dev patterns in docs/ui-refs/21st-dev.md to plain JS: drag-depth counter dropzone, accessible 7-step conversion stepper wired to real progress, MusicXML code block with line numbers + Copy (keep clipboard fallback), overlay toggle, per-part list stating which staff each part was split from; distinctive engraving-world design (not generic), light+dark, 400px; keep the sample auto-converting on load' },
]
if (R >= 3) OWNERS.push({ key: 'ml', files: 'src/ml.js (new), src/ml-worker.js (new), dist/assets/ (model, wasm, LICENSE/NOTICE files only), assets-src/ml/, and the asset list in tools/build.js (the ui owner leaves build.js alone this round)', focus: 'integrate the copista-2m ONNX detector found by the ML trial (docs/spike-ml.md, spike/ml/: copista_core.mjs, ONNX export, PROVENANCE.md, the CSP-tested onnxruntime-web 1.30.0 loading recipe: dynamic import of ort.wasm.bundle.min.mjs from a pinned CDN inside a blob module worker, wasmPaths {wasm: absolute URL} to a self-hosted wasm, numThreads 1). Expose it as an alternative source of noteheads, stems, dots, rests, accidentals and voice slots for front.js/assemble.js behind an option (env/browser + node via onnxruntime-node), keeping our staff-line fit for pitch. Measure A/B on the benchmark AND the challenge set (with and without the model); report both. Only make it the default if it is better on both and the page stays within artifact limits (each asset <= 15 MB). Ship LICENSE/NOTICE crediting KobiMusic.' })
const fixes = await parallel(OWNERS.map(o => () => agent(`${CTX}
Round ${R}. Current metrics: ${JSON.stringify(baseline)}
You own ONLY ${o.files} (paths under ${MVP}); four other owners edit other files concurrently — never edit theirs. Focus: ${o.focus}.\n${limitNote}
TASK: Find the highest-impact failures in your area (run eval with --out ${MVP}/work/eval-r${R}-${o.key}.json, --only for speed, view scans/overlays as images), make generalizable fixes (never hard-code corpus content), re-run to prove your area improved and nothing crashes. Keep changes shippable. Return summary with measured before/after and any request for another owner.`, { ...OPTS, label: `fix:r${R}:${o.key}`, phase: 'Fix', schema: SECTION })))

phase('Integrate')
const m = await agent(`${CTX}
Round ${R} owners reported:\n${fixes.map((r, i) => `${OWNERS[i].key}: ${r ? r.summary : 'FAILED'}`).join('\n')}
Baseline metrics: ${JSON.stringify(baseline)}
TASK (integrator): run full eval (--out ${MVP}/work/eval-r${R}-final.json), fix cross-module breakage; if any owner's change regressed aggregate or real_scan_aggregate, fix or revert just that part (snapshots: ${MVP}/work/src-r${R - 1}/). Then snapshot src to ${MVP}/work/src-r${R}/, run node ${MVP}/tools/build.js, and node ${MVP}/tools/pw/test.js at 1280 and 400 px in light and dark (sample converts, no console errors, no horizontal scroll). Also run the challenge set if present (--set challenge --out ${MVP}/work/eval-r${R}-challenge.json) and include its aggregate and worst categories in per_owner_issues. Report metrics, what changed, what was reverted, browser_ok, per_owner_issues for next round, and in the limits field the status of EVERY limit in the checklist (resolved / partial / open) with concrete evidence.\n${limitNote}`, { ...OPTS, label: `integrate:r${R}`, phase: 'Integrate', schema: METRICS })
return { round: R, limits: m?.limits, baseline, fixes: fixes.map((r, i) => ({ owner: OWNERS[i].key, summary: r?.summary })), metrics: m }
