# Spike: OpenCV.js as a fallback symbol identifier

Date: 2026-11-08 (pre-clean update the same day). Scope: should OpenCV.js be added to the browser OMR app as a fallback for identifying music symbols where the classical reading (`mvp/src/*.js`) and the copista-2m ML pass are missing or weak? Everything below was measured on this machine (Linux, 192 cores, shared and heavily loaded: load average 115–170 during the runs) with the corpus as it stands on disk. Experiment code, data and logs are in `spike/opencv/`. The compact results are in `spike/opencv/results/`, and every number can be regenerated (see "Reproduce").

## Update: plain-JS header reader (shipped, default on)

`mvp/src/cv.js` `readHeaders(fr, asm)` now runs on every page, called from `omr.js` `analyse()` right after
`assemblePage` (after the orientation clef count, so orientation still judges the plain reading). It is the
section 4 template reader in plain JS (Bravura templates, normalised correlation), with the OpenCV symbol paths,
the rest fallback and `wrapConverter` removed. Changes since the spike:
- matching stays inside the header: a few glyphs per staff, and the template only shifts ±0.35 staff space
  around the glyph's centre: **≈15–100 ms per page** (was 283 ms with a full search).
- the two numbers are cut at the middle line (they often touch once the line is removed), and the search for a
  missed time signature may start on the tail of the key signature (the first three ink groups are tried).
- when a missed time signature is found the header ends after it, so its digits are no longer taken for notes
  or accidentals, and the overlay's time-signature layer (`symbols.js` reads `hdr.time`) shows it. Maple Leaf Rag
  (benchmark page, 200 dpi): time signatures 1 → 2 (both 2/4 read), the false head on the treble digits dropped,
  no accidental boxed on the digits.

A/B (same src, pre-clean on in both arms; `spike/opencv/results/header-*.txt`):

| set | aggregate | first time signature right | items changed |
|---|---|---|---|
| challenge (no OCR, 365) | 0.8212 → **0.8227** (pitch +0.0031, duration +0.0029) | 342 → **352** | 63; one drop −0.023 (`andantino-piano-photocopy-thin` severe, meter became right) |
| benchmark with OCR (20) | 0.9496 → **0.9499**, real scans 0.9295 = | 19 = | 2, both up (`joplin-maple-leaf-piano` +0.001, `schumann-dichterliebe2` +0.005) |

## Update: OpenCV pre-clean for degraded scans (shipped)

Scope extension: OpenCV now runs as a **pre-clean stage before binarisation**, only on pages a cheap
quality check calls degraded. This supersedes the "do not add OpenCV.js" verdict below for this use; the
symbol-reader findings in sections 1–7 still hold.

**How it works** (`mvp/src/cv.js`, hook `mvp/src/front.js` `frontSteps`):
- `pageQuality(gray)` in plain JS (30–70 ms per page) measures: share of mid-grey pixels (`mid`), mid-grey share of inked
  pixels (`midShare`), lightest-1 % level (`p1`), paper darkness and unevenness from 32 px cells (`bgLow`,
  `bgUneven`), paper texture (`bgStd`), isolated specks per Mpx (`speck`), staff-line thickness / staff space (`ltss`).
- `precleanPlan(q)` picks repairs; an empty plan returns **the same gray object**, so clean pages are read exactly as
  before and OpenCV is never loaded for them (verified: the clean class and every unaffected item are unchanged).
- Otherwise OpenCV.js (patched 4.10.0, self-hosted `dist/assets/opencv-4.10.0-noeval.js`) is loaded **synchronously**
  (front() is synchronous): node reads the file; the recognition Web Worker uses a synchronous XHR + `blob:`
  `importScripts`, and the embedded wasm is compiled with `new WebAssembly.Module` through `instantiateWasm`
  (the patch makes the UMD wrapper read `globalThis.__opencvModuleArgs`). On a page's main thread (worker
  unavailable) the pre-clean is skipped. `OMR_PRECLEAN=off` disables it (node).

| repair | when (plan rule) | OpenCV ops |
|---|---|---|
| `thin` | binary page (`bgStd` < 0.5, `mid` < 0.03), `ltss` > 0.16 (thick photocopy) | `dilate` 3×3 (paper grows) × n, n = round((lt − 0.11·ss)/2) clamped 1–3 |
| `close` | binary page, 300 < `speck` < 2000 (thin photocopy broken into dots) | `erode` 2×2 (ink grows 1 px) |
| `descreen` | `speck` > 25000 and `bgStd` > 4 (halftone screen) | `GaussianBlur` σ = ss/14 |
| `flatten` | `mid` > 0.15 and (`bgUneven` < 0.4, `bgLow` > 0.12, `midShare` > 0.8 — yellowed/stained) or `bgStd` > 6.8 (combined damage) | 4× `resize`, `morphologyEx` CLOSE (ellipse 0.8·ss), `GaussianBlur`, `resize` back, gain capped at 2.5×, `divide` |
| `sharpen` | `midShare` > 0.94 and `p1` > 100 (heavy blur) | unsharp mask: `GaussianBlur` σ = ss/5, `addWeighted` 3, −2 |

**Per class, challenge degradation set** (aggregate, `eval.mjs --set challenge --no-ocr --jobs 8`, same src snapshot,
`OMR_PRECLEAN=off` vs on; `spike/opencv/results/preclean-perclass.txt`):

| class | ops used | all | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| photocopy-thick | thin | 0.681 → **0.816** | 0.756 → 0.868 | 0.831 → 0.888 | 0.456 → **0.691** |
| blur | sharpen (severe only) | 0.754 → **0.839** | = | = | 0.542 → **0.796** |
| combo | flatten (severe) | 0.804 → **0.855** | = | = | 0.669 → **0.823** |
| halftone | descreen | 0.813 → **0.855** | 0.842 → 0.873 | 0.786 → 0.854 | 0.811 → 0.839 |
| yellowed | flatten (severe) | 0.859 → 0.868 | = | = | 0.809 → 0.838 |
| photocopy-thin | close (severe) | 0.806 → 0.815 | = | = | 0.668 → 0.695 |
| clean, bleed, book, crop, highdpi, holes-staple, jpeg, lowdpi, noise, phone, rot90/180, scale, skew, spread, stain-pencil | none | unchanged | | | |

Whole challenge set: **0.8091 → 0.8212** (+0.0121; pitch +0.023, duration +0.023, rests +0.013); degradation
0.8493 → 0.8651, pitch category +0.007, lyrics +0.0045, rhythm +0.0043, layout and voices unchanged; scan-severe
0.7354 → 0.7623. Largest item drop −0.009 (`agrace-satb-photocopy-thick/scan-severe`), 46 items up.
Benchmark **with OCR**: **0.9480 → 0.9496**, real scans 0.9256 → **0.9295**, synthetic 0.9519 → 0.9531, no item down
(`golden1923-america` +0.012 flatten, `bach-bwv3-6` +0.011 flatten, `bach-bwv166-6` +0.010 thin).

Named limits: the severe photocopies improve (`andantino` thick severe 0.616 → 0.854, `wind-melody` thick severe
0.351 → 0.711, `agrace` thin severe 0.595 → 0.657; `agrace` thick severe stays at 0.25). **Not helped**: L11
`hymn-descant-cue-notes-amen-small` severe (0.113; its staff lines are broken into dashes — a 1×ss horizontal
closing was tried and did not help), L19 `satb-closed-lyrics-both-staves-de` severe (0.545) and phone shots
(`andantino-piano-phone` severe 0.576): flattening phone shots measured worse (class 0.824 → 0.771 even with the
gain cap), so phone pages are left alone; dewarping was not attempted.

What was tried and rejected (`results/preclean-trials.txt`, 12 items per class): 3×3 / 5×5 **median** destroys 1–2 px
staff lines (halftone 0.813 → 0.643, noise 0.869 → 0.473); **despeckle** (drop tiny components) erases the dotted staff
lines of thin photocopies (0.806 → 0.690); a second thinning pass ruins mild thick photocopies (mild 0.888 → 0.254),
hence the thickness-driven pass count; descreen on random noise is slightly worse (0.869 → 0.865); flatten without the
gain cap turns a photographed page's dark surround into texture (phone severe 0.708 → 0.448).

**Cost.** Asset: `opencv-4.10.0-noeval.js` 10,376,412 B (≈3.4 MB gzip), plus licence and notice (dist/assets total
49.9 MB of 64 MB). Node: quality check 30–70 ms per page; OpenCV load ≈170 ms once; repairs 40–240 ms per degraded page
(`results/preclean-timing.txt`). Headless Chromium, CSP blob worker (`spike/opencv/probe/browser-preclean.js`): the
first degraded page costs ≈1.1 s extra (sync fetch of 10 MB, wasm compile, then the repair); clean pages cost only the
quality check; results match node exactly (same plans, staves and heads).

## Recommendation (TL;DR)

1. **Do not add OpenCV.js as a dependency now.** The one approach that wins is **template matching against SMuFL glyphs** (approach a), and a plain-JS implementation of the same matcher produces **byte-identical output** on 671 eval items (challenge + coverage: 0 items changed). It needs no 10.4 MB asset, no CSP patch, and no wasm load. OpenCV.js only makes the matching faster: 38 ms per page against 283 ms in JS. In the browser it costs about 0.85 s to load, so it breaks even after 3–4 pages.
2. **Adopt template matching (approach a) for time-signature numbers and unread clefs.** The classical header finds numbered time signatures but **never reads their digits** (0 of 182 read on the coverage patches). Bravura digit templates read **99.8 %** of digits on scans and **90.9 %** on severe scans. End to end, with the fallback on, the first time signature is right in **+23 coverage items (246 → 269 of 306)** and **+8 challenge items (333 → 341 of 365)**, with no item moving away from the truth. Aggregate scores change by +0.0003 (coverage), +0.0004 (challenge) and 0 (benchmark). The eval metric does not score time signatures directly; the gain shows up in duration, rests and the coverage time tags (`time-6-8` 0 → 3 of 31 on scans, `time-4-4` severe 33 → 41 of 79). Reading unread clefs fixed one piano spread outright (+0.147 aggregate).
3. **Do not adopt approaches b (contour features + kNN) or c (HOG + linear SVM)** as fallbacks. On isolated glyphs they are no better than the classical readers where those exist (rests, accidentals, clefs). They cannot recognise classes missing from their training items (32nd and 64th rests: 0 % recall under an item-level split). They would also ship training vectors. For digits, HOG-kNN beats templates on severe scans (95.9 % against 90.9 %), but it is trained on this corpus's engraving font.
4. **Do not enable the rest fallback.** Template matching as a second opinion on glyphs `rests.js` leaves unclassified raised rests F1 on the benchmark (+0.030) and challenge (+0.006) but lowered it on coverage (−0.010; false rests on piano scores with pedal marks and fingering). The code is in `cv.js` behind `opts.rests`, and the hook is in `spike/opencv/hooks/rests-hook.patch`, not applied.
5. Prototype delivered: **`mvp/src/cv.js`**, default **off**, used like `ml.js` (`wrapConverter`). It has two interchangeable matchers: `createJsCv()` (recommended, no asset) and `createNodeCv()` / `createBrowserCv()` (OpenCV.js). `node mvp/tools/build.js` and `node mvp/tools/pw/test.js` both pass with it in the bundle. The eval harness switch is a ready patch: `spike/opencv/hooks/eval-cv.patch` adds `--cv js|opencv` to `mvp/tools/eval.mjs`. It applies cleanly and was tested on a temporary copy, but is not applied, because that file belongs to the harness owner.

## 1. Runtime feasibility

### 1.1 Builds, sizes, licence

| package (npm, jsDelivr) | published | `opencv.js` | gzip | wasm | licence |
|---|---|---:|---:|---|---|
| `@techstark/opencv-js@4.10.0-release.1` (pinned) | 2024-08-25 | 10,378,215 B | 3,389,608 B | inlined as base64 (`SINGLE_FILE=1`) | Apache-2.0 |
| `@techstark/opencv-js@4.11.0-release.1` | 2025-06-04 | 11,386,540 B | 3,870,043 B | inlined | Apache-2.0 |
| `@techstark/opencv-js@4.12.0-release.1` | 2025-11-08 | 10,872,779 B | – | inlined | Apache-2.0 |
| `@techstark/opencv-js@5.0.0-release.1` | 2026-06-24 | 13,298,869 B | – | inlined | Apache-2.0 |

A single file, under the 15 MB asset limit. cdnjs has no OpenCV.js package. The official build at docs.opencv.org is the same emscripten/embind build.

Modules compiled in (4.10.0 `getBuildInformation()`): `calib3d core dnn features2d flann imgproc js objdetect photo video`. **Disabled: `ml`** (so no `cv.ml_KNearest`, no `cv.ml_SVM`), `imgcodecs`, `highgui`. Also missing from the JS bindings: **`cv.HuMoments`** (I computed it from `cv.moments` nu values) and **`HOGDescriptor.compute`** (only `detectMultiScale` / `setSVMDetector` are bound; I computed HOG from `cv.Sobel` + `cv.cartToPolar`, with JS binning). `matchTemplate`, `moments`, `findContours`, `convexHull`, `connectedComponentsWithStats`, `resize`, `threshold`, `morphologyEx` and `distanceTransform` are present.

### 1.2 The artifact CSP blocks every published build

Loaded from the pinned jsDelivr URL under the app's CSP (`script-src` has `'wasm-unsafe-eval'` and `blob:`, but no `'unsafe-eval'` and no `'self'`), **all four builds fail to initialise**: *"Evaluating a string as JavaScript violates the following Content Security Policy directive … 'unsafe-eval'"*. Embind builds every binding invoker with `new Function(...)` (`craftInvokerFunction`, `createNamedFunction`, `makeDynCaller`, `__emval_get_method_caller`). 4.11+ removed `createNamedFunction`'s eval but still crafts invokers with `newFunc(Function, …)`.

Fix: `spike/opencv/tools/patch-noeval.js` rewrites those four generators as equivalent closures. This is the logic emscripten itself emits with `-s DYNAMIC_EXECUTION=0`. The patch makes exact-string replacements and fails loudly on any other build. The patched 4.10.0 file (10,376,402 B) cannot come from a CDN `<script>`. It must be **self-hosted and run from a `blob:` URL** (fetch from `'self'` via `connect-src`, then `<script src=blob:>` or `importScripts(blob:)` in the recognition worker). Inside a `blob:` worker, the asset base must be an absolute URL. On GitHub Pages (no CSP) the patched file loads directly.

Speed is unchanged by the patch (100 calls each, node): `moments` 5.9 ms vs 5.8 ms stock, `findContours` 6.0 vs 5.3, `matchTemplate` + `minMaxLoc` 14.3 vs 12.2.

### 1.3 Load time and memory

| where | load | memory | probe |
|---|---|---|---|
| node 24, stock package `require` | 235–274 ms | RSS +71–80 MB (+128 MB `external`) | `probe/load.js` |
| node 24, patched file | 140–182 ms | RSS +79–84 MB | `probe/micro.js`, `probe/timing.js` |
| headless Chromium 1208, page, patched via `blob:` script | 852–865 ms | JS heap 168.5 MB | `probe/browser.js` |
| headless Chromium, `blob:` Web Worker, `importScripts(blob:)` | 853–854 ms | (not observable in a worker) | `probe/browser.js` |
| headless Chromium, stock build from jsDelivr | **fails** (CSP eval) | | `probe/browser.js` |

One `matchTemplate` (TM_CCOEFF_NORMED) of a 40×40 template over a 2000×2800 page takes 211–224 ms in Chromium.

## 2. Ground truth for symbol-level measurement

The coverage corpus (`corpus/coverage`) is LilyPond-engraved, so exact glyph positions are available:

1. `spike/opencv/tools/svgtag.ly` is an include-settings file with a Scheme engraver. It sets `output-attributes` (a callback, read at output time) on every Rest, MultiMeasureRest, Accidental, Clef, TimeSignature, Script, DynamicText, Flag, Dots and NoteHead grob, so LilyPond's SVG backend wraps each one in `<g class=…>` with `data-*` detail (duration log, glyph name, fraction). `tools/svgboxes.py` turns the SVG paths into pixel boxes at 300 dpi. They align with `clean.pdf` (checked by ink inside and outside each box).
2. `tools/patches.js` runs the pipeline's own front end (`front()`, src snapshot) on `clean`, `scan` and `scan-severe`. Each truth box is carried onto the scan by its staff (staff index, fraction along the staff, offset from the middle line in staff spaces), which follows skew, scaling and mild warps. The patch is the union of the staff-removed page's (`fr.R`) components whose centres fall inside the box. This is exactly what a fallback sees at run time.
3. 70 items (rests, pitch, time, marks, notes and layouts families), 15,247 patches. Used after dropping flags, which are attached to stems and so are not glyph patches: 14,150 samples. Of these, 4,000 are other-component negatives, 3,500 noteheads and 529 other scripts. Rests: 1,195 (incl. 14 H-bars, 176 whole/bar rests). Accidentals: 467 (incl. 15 double flats and 18 double sharps). Clefs: 1,289 (incl. 119 C clefs). Time-signature digits: 1,548, plus 110 C / cut glyphs. Also 332 fermatas, 451 dynamics and 705 dots.
4. Evaluation uses a 2-fold, **item-level** split, so items never straddle train and test. Training uses all three variants of the train items; testing is per variant.

## 3. Isolated-glyph results (patch level)

### 3.1 The three approaches, family micro precision / recall (%), test folds

`a-template`: best normalised correlation against Bravura 1.392 templates (SIL OFL 1.1) scaled by the measured staff space (×0.85/1/1.15) with small shifts, `neg` below a threshold tuned on the train fold. `b-shape-knn`: Hu moments, aspect, size and staff position, fill, solidity, holes, components and 4×4 zoning; standardised 3-NN in JS. `c-hog-svm` / `c-hog-knn`: HOG (32×32, 8 px cells, 9 bins, L2-Hys) plus size and position; one-vs-rest linear SVM (Pegasos) or 3-NN in JS. `ac`: HOG plus the template scores as features.

**scan** (typical 200–300 dpi scan)

| approach | rests | accidentals | clefs | time digits + C | fermata | dynamics | dots | negatives |
|---|---|---|---|---|---|---|---|---|
| a-template | 33/83 | 99/83 | 100/96 | 97/99 | 100/99 | 91/69 | 0/0 | 89/67 |
| b-shape-knn | 82/81 | 94/88 | 97/100 | 97/99 | 100/99 | 93/96 | 80/85 | 94/92 |
| c-hog-svm | 95/73 | 99/71 | 100/98 | 98/90 | 99/96 | 99/94 | 80/84 | 82/94 |
| c-hog-knn | 84/83 | 93/88 | 100/100 | 97/99 | 100/99 | 98/95 | 84/86 | 94/94 |
| ac-hog+tpl-svm | 96/76 | 98/70 | 100/98 | 100/90 | 99/96 | 99/95 | 85/84 | 83/97 |

**scan-severe** (photocopies, phone photos, 100–150 dpi)

| approach | rests | accidentals | clefs | time digits + C | fermata | dynamics | dots | negatives |
|---|---|---|---|---|---|---|---|---|
| a-template | 31/86 | 94/72 | 100/71 | 91/87 | 98/77 | 76/53 | 0/0 | 83/74 |
| b-shape-knn | 66/77 | 68/80 | 94/95 | 87/88 | 94/95 | 93/92 | 63/71 | 94/87 |
| c-hog-svm | 95/51 | 86/64 | 99/89 | 98/66 | 99/88 | 98/81 | 64/52 | 75/96 |
| c-hog-knn | 81/81 | 76/79 | 97/95 | 94/90 | 100/95 | 94/95 | 68/71 | 92/93 |
| ac-hog+tpl-svm | 96/54 | 87/68 | 99/89 | 99/67 | 98/89 | 98/81 | 72/54 | 76/97 |

Cost per patch (features + prediction, node, OpenCV.js): template 10.3 ms (31 classes × 3 scales), shape-kNN 0.42 ms, HOG-SVM 0.41 ms, HOG-kNN 2.5 ms.

Per-class findings (`results/patch-classifiers.json`):
- **Templates are font-independent and precise.** The corpus is engraved in Emmentaler and the templates are Bravura, yet on scans: quarter to 64th rests 100 % precision (recall 91–100 %), sharps / flats / naturals 98–100 / 84–87, G / F / C clefs 100 / 92–100, digits 100 / 95–100, fermata 100 / 99. They fail where shape alone is ambiguous: whole and half rests are the same glyph (rest-whole precision 59 %, half recall 0), and the dot template loses to block-rest and notehead templates (dot recall 0). That is the low "rests" and "dots" precision in the tables.
- **Trained models cannot see unseen classes.** All 32nd and 64th rests sit in one fold, so b and c score 0 % on them, while the templates score 100 %.
- **Double accidentals:** HOG-kNN double flat 100/100 (n = 5), double sharp 100/71 (n = 7). The classical classifier never outputs them, but the counts are too small to act on.

### 3.2 Time-signature digits, given the time-signature box

| reader | clean | scan | scan-severe |
|---|---|---|---|
| templates only (no training) | 100.0 % (532) | **99.8 %** (532) | 90.9 % (484) |
| HOG-kNN (other fold) | 99.6 % | 99.4 % | **95.9 %** |
| combined (template unless kNN confident) | 100.0 % | 99.6 % | 93.4 % |

### 3.3 The classical readers on the same truth glyphs (`tools/classical.js`, `results/patch-classical.json`)

| family, P / R % | clean | scan | scan-severe |
|---|---|---|---|
| rests (`detectRests` over each staff, after `assemblePage`) | 93/94 | 96/90 | 80/67 |
| accidentals (`classifyAccidental` on every 1–4-space glyph; precision is low because non-accidentals are tried too, which the pipeline does not do) | 27/90 | 48/89 | 39/79 |
| clefs (staff header / clef change) | 100/98 | 100/98 (C clef 77 %) | 100/93 (C clef 68 %) |
| numbered time signatures: found / numbers read | 169 / 0 of 308 | 160 / 0 of 308 | 142 / 0 of 284 |

So on isolated glyphs the classical rest, accidental and clef readers are already as good as b and c (coverage's accidental recall of about 50 % end to end comes from association and detection, not classification). The **only family the pipeline cannot read at all is time-signature numbers**. Unread C clefs and the severe-scan rest recall are the next gaps.

## 4. Prototype: `mvp/src/cv.js`

- **When it runs:** after `createConverter().addPage` (the same pattern as `ml.wrapConverter`), only where the classical reading is missing:
  1. A numbered time signature the header found (`hdr.time` with no `beats`) on the **first system of a page**: each row (lines 1–3 and 3–5) is read as one digit, or as two digits split at a gap, whichever matches better. Accepted only if every digit scores ≥ 0.45 and beats every rest, accidental and notehead template; beats 2–16, beat type 1–32.
  2. No time signature found: two stacked digits right after the clef / key (score ≥ 0.55). The signature is set and "heads" found on it are dropped.
  3. `hdr.clefGuessed`: the tall glyph at the staff start is matched against G / F / C (≥ 0.45, margin 0.05); a C clef takes its line from its centre. A bass clef over a treble clef in a two-staff system is rejected, as in `assemblePage`.
  4. `opts.rests` (off; needs the `rests.js` hook): quarter to 64th rest templates for glyphs `detectRests` left unclassified.
- **Why only the first system:** later systems carry meter changes, which `score.js` does not model (one meter per piece). An early version read every staff and made pieces starting in 3/4 come out in 6/8 (`time/t04-pickup-song`).
- **Matchers:** `createJsCv()` (plain JS: area resize, threshold, TM_CCOEFF_NORMED by direct correlation with integral-image window sums). `createNodeCv()` (`OPENCV_JS=path`, else `mvp/assets-src/opencv/…` or `spike/opencv/vendor/…`). `createBrowserCv({ base })` (fetch the patched file, then `blob:`, then `importScripts` / `<script>`). Templates: 27 Bravura glyphs at 24 px per staff space, 1 bit per pixel, 12 KB inline. Scores agree to a mean of 0.0001 (max 0.012) and the argmax agrees on 565 of 566 sampled patches (`probe/parity.js`).
- **Browser check** (`probe/browser-cv.js`, src bundled like `build.js`, blob worker, artifact CSP): both matchers read 6/8 on `time/t02-compound-irregular` scan, the same as node. Matching time: 51 ms (OpenCV) vs 272 ms (JS); total with the first-page load: 2.1 s vs 1.6 s.
- **Not done:** no UI toggle (that is the UI owner's file). Today the option is reached by calling `wrapConverter` in node, the worker or tests. The patched OpenCV file is not copied into `dist/assets` (10.4 MB for an option that is off, and the recommended matcher does not need it).

## 5. End-to-end A/B (same src snapshot, fallback off vs on)

The snapshot of `mvp/src` (md5 of the concatenated files: `7385b7ac…`) was copied to `spike/opencv/src-ab`. The only addition is `cv.js` plus an env switch in the copy's `omr.js`. The eval is `mvp/tools/eval.mjs --no-ocr --jobs 16 --src …` (OCR off in both arms: the fallback does not touch lyrics). Full output: `results/ab-eval.txt`.

| set (n) | aggregate | pitch | duration | rests | first time signature right | items changed | runtime per item |
|---|---|---|---|---|---|---|---|
| benchmark (20) | 0.8042 → 0.8042 | = | = | = | 19 → 19 | 0 | +235 ms |
| challenge (365) | 0.8091 → **0.8095** | +0.0009 | +0.0007 | = | **333 → 341** | 9 | +256 ms |
| coverage (306) | 0.7766 → **0.7769** | +0.0003 | +0.0012 | **+0.0103** | **246 → 269** | 23 | +467 ms |

- Every time-signature change moved to the truth: 6/8 ×14, 4/4 ×13, 3/2 ×2, 2/4 ×1, 3/8 ×1. A few items lose a little aggregate even though the meter became right (`rests/rst04` severe −0.042 at 3/8, `notes/nt04-beams` clean −0.023 at 2/4); rhythm repair in `score.js` fits the bars differently under the true meter.
- Largest gains: `challenge degradation/twinkle-piano2p-spread/scan-severe` +0.147 (clefs read on staves the header had guessed), `coverage notes/nt03-chords/clean` +0.048, `perf/perf-pages-05` +0.013 to +0.022.
- Coverage matrix (`tools/coverage.mjs` on both reports; `results/coverage-matrix-{off,on}.json`): `time-6-8` 0 → 2 / 3 / 1 of 31 (clean / scan / severe), `time-4-4` 43 → 45 clean and 33 → 41 severe, `time-3-2` 0 → 1, `time-2-4` 3 → 4 clean, `x-time-3-8` 0 → 1. Note values gain slightly from the right bar length (`note-8th` +41 to +45 hits per variant).
- The runtime increase in node is mostly loading OpenCV.js in each eval child process (about 0.18 s). Measured directly over 30 pages: the fallback's matching takes **38 ms per page with OpenCV and 283 ms with the JS matcher**, against a 1.2 s conversion. The JS matcher's end-to-end eval output is **identical** to the OpenCV one (challenge 0/365, coverage 0/306 items changed).

Rest fallback (`src-ab2`, fallback on, rests hook off vs on):

| set | aggregate | rests F1 |
|---|---|---|
| benchmark | 0.8042 → 0.8044 | 0.8015 → 0.8311 |
| challenge | 0.8095 → 0.8097 | 0.7587 → 0.7645 |
| coverage | 0.7769 → 0.7764 | 0.6249 → 0.6147 |

The rest fallback loses on coverage: piano pages (`perf-piano-*`, `marks/mk04` pedal and fingering) gain false rests. Not recommended without position and context checks.

## 6. What OpenCV.js would and would not buy

- **Would:** about 7× faster template matching (38 vs 283 ms per page here). That matters only for full-page or multi-scale detection, such as searching whole staves for missed rests or fermatas; per-glyph second opinions do not need it.
- **Would not:** any accuracy. The OpenCV build ships no `ml` module and no HOG `compute`, and its contour and moment functions are a few lines of JS each. The recommendation in `docs/research-omr.md` §7.2 (plain typed-array JS) still holds. The new information is that the CDN builds do not run under the artifact CSP at all without the no-eval patch.
- **Costs:** 10.4 MB self-hosted asset (3.4 MB gzip), about 0.85 s load and about 170 MB heap in the browser, a patched third-party file to maintain, and `Mat.delete()` memory management.

## 7. Next steps (owners)

1. Harness owner: apply `spike/opencv/hooks/eval-cv.patch` (`--cv js|opencv`), so `mvp/src/cv.js` can be measured without the spike copy.
2. UI / session owner: an opt-in "Read time signatures from templates" setting calling `cv.wrapConverter(conv, cv.createJsCv())` in the recognition worker. With +0.3 s per page and no regressions in the first-time-signature check, it is a candidate to turn on by default after review.
3. Score owner: meter changes (`time-change`, 110 occurrences) are now the limit. `cv.js` can read every staff's numbers once `score.js` models more than one meter per piece.
4. Rests owner: if the rest fallback is wanted, it needs context rules (no fingering or pedal zones, voice position) before `spike/opencv/hooks/rests-hook.patch` is applied.

## Files

- `mvp/src/cv.js`: the prototype (default off; not called by any existing code path).
- `spike/opencv/tools/`: `patch-noeval.js` (CSP patch), `svgtag.ly` + `svgboxes.py` + `mkboxes.sh` (LilyPond truth boxes), `templates.js` (Bravura templates via Chromium), `patches.js` (glyph patches), `samples.js`, `features.js`, `classifiers.js`, `exp.js`, `digits-exp.js` (patch experiments), `classical.js` + `classical-report.js` (classical baseline), `ab.sh`, `ab-rests.sh`, `abcmp.js` (end-to-end A/B), `cvload.js`.
- `spike/opencv/probe/`: `load.js`, `hog.js`, `micro.js`, `browser.js` (CSP / load probes), `browser-cv.js` (prototype in a CSP blob worker), `parity.js` (OpenCV vs JS matcher), `timing.js`, `one.js`, `smoke-mvp.js`, debug probes.
- `spike/opencv/hooks/`: `eval-cv.patch`, `rests-hook.patch` (not applied).
- `spike/opencv/results/`: `ab-eval.txt`, `patch-classifiers.json`, `patch-classical.json`, `coverage-matrix-off.json`, `coverage-matrix-on.json`.
- `spike/opencv/fonts/LICENSE.txt`: Bravura's OFL 1.1 licence (the font files themselves are ignored).

## Licences

- OpenCV.js 4.10.0 (`@techstark/opencv-js` 4.10.0-release.1): **Apache-2.0**. The no-eval patch is a modification and must be stated in a NOTICE if the file is ever shipped.
- Bravura 1.392 (Steinberg Media Technologies): **SIL OFL 1.1**. `cv.js` embeds bitmaps rendered from 27 of its glyphs, credited in the file header.
- LilyPond 2.24 (GPL) is used offline only, to make truth boxes; nothing from it ships.

## Reproduce

```
cd spike/opencv
npm install                                                    # @techstark/opencv-js 4.10.0-release.1
node tools/patch-noeval.js node_modules/@techstark/opencv-js/dist/opencv.js vendor/opencv-4.10.0-noeval.js
for f in redist/woff/Bravura.woff2 LICENSE.txt; do curl -sfL -o fonts/$(basename $f) https://cdn.jsdelivr.net/gh/steinbergmedia/bravura@bravura-1.392/$f; done
node tools/templates.js 24                                     # data/templates.json
tools/mkboxes.sh                                               # data/boxes (LilyPond SVG truth)
ls data/boxes | sed 's/.json$//' | xargs -P 6 -I{} node tools/patches.js {}
node tools/exp.js --feat && node tools/digits-exp.js           # section 3
ls data/patches/*.jsonl | xargs -n1 basename | sed 's/.jsonl$//' | xargs -P 5 -I{} node tools/classical.js {}; node tools/classical-report.js
cp -r ../../mvp/src src-ab && cp ../../mvp/src/cv.js src-ab/   # then the OMR_CV_FALLBACK switch in src-ab/omr.js convert()
tools/ab.sh; node tools/abcmp.js data/eval/ab-coverage-cv0.json data/eval/ab-coverage-cv1.json
```
