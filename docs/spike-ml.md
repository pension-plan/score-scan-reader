# Spike: pretrained ML OMR models in the browser

Date: 2026-11-08. Scope: can a pretrained, permissively licensed optical-music-recognition model run client-side
(onnxruntime-web, self-hosted wasm, artifact CSP, files of 15 MB or less, 64 MB in total) and help with the two hard
requirements: scanned closed-score SATB with voice separation, and lyrics?
Everything here was measured on this machine (Linux aarch64, 192 cores) unless a number is quoted from a model card.
Code, data and raw logs are in `spike/ml/`, and every table can be regenerated (see "Reproduce").

## Recommendation (TL;DR)

1. **Use the copista-2m symbol detector** (KobiMusic, **Apache-2.0** weights and code,
   https://huggingface.co/kobimusic/copista-2m, HF sha `c37d89e1e52edc95c1a73bda0aea5f2f71a9c763`).
   I exported it to ONNX as two graphs and stored the weights as int8 (`int8w`): **1.77 MB + 0.29 MB = 2.06 MB**
   (`spike/ml/assets/`). The page-level JS pipeline is `spike/ml/src/copista_core.mjs`: plain array code with no
   dependencies, and it runs unchanged in node and in the browser.
   - On the 36 test scans (3 pieces × 200/300 dpi × 6 degradations), run through **onnxruntime-web wasm**:
     notehead **P 1.000 / R 0.991 / F1 0.996**, staff-position accuracy **1.000** on everything except a harsh
     photocopy (0.65), stem direction 0.984, and **voice-slot accuracy 0.991 on the closed-score SATB**. The model
     itself says "voice 1 (stem up) / voice 2 (stem down)" for every notehead, which gives S/A and T/B part
     separation almost for free.
   - Speed, one wasm thread (the realistic artifact case, since there is no cross-origin isolation): **≈4.2–5.1 s per
     A4 page** in headless Chromium, end to end (resample, dense CNN ≈4.0–4.7 s, verifier ≈0.1 s, decode).
   - Quantization costs nothing. fp32, fp16-weight and int8-weight variants give identical scores. **Do not** use ORT
     dynamic int8 (`int8d`): it is 2× faster in native ORT but **3× slower in wasm** (12.2 s vs 4.1 s).
2. **Runtime: onnxruntime-web 1.30.0** (MIT). Load `ort.wasm.bundle.min.mjs` from jsdelivr or cdnjs with a
   **dynamic `import()` inside a blob: module worker**, and set `ort.env.wasm.wasmPaths = { wasm: <absolute URL of
   self-hosted ort-wasm-simd-threaded.wasm> }` (14,239,897 bytes, which fits under 15 MB) and `numThreads = 1`. This passes an
   artifact-like strict CSP (no `'self'` in script-src). Fallback: **onnxruntime-web 1.18.0 UMD**
   (`ort.wasm.min.js` via `<script src>` or `importScripts` in a blob worker, `wasmPaths = 'assets/'`, self-host
   `ort-wasm-simd.wasm`, 10.6 MB). Its warm speed is the same within noise (4.2–4.4 s vs 4.1–4.3 s), it uses the
   simplest loading path, but it lacks some kernels (for example ConvInteger).
   Things that **fail** under that CSP (measured): the ORT UMD builds of 1.20.1, 1.22.0 and 1.30.0, and an ESM bundle
   given a *string* `wasmPaths`. Both try to `import()` `ort-wasm-simd-threaded.mjs` from the same origin. A *static*
   `import … from <CDN>` inside a blob module worker also fails.
3. **Do not use** homr (AGPL-3.0; at least 75 MB of weights even after quantization; minutes per page in wasm; no
   voice separation, since closed score comes out as chords: voice accuracy 0.46). Do not use oemer (MIT but 109 MB
   fp32, which needs splitting; about 33 min/page of wasm compute; measure-pitch F1 0.20–0.44 on our scans; breaks
   with OpenCV 5). Do not use a YOLO/DeepScoresV2 detector: none with a permissive licence exists. The
   Ultralytics-trained ones carry AGPL-3.0, others have no licence, and DeepScoresV2 itself is CC BY 4.0.
   satb-line-omr (MIT, 6.4 MB, built for the browser) is excellent on *clean open-score* prints (100 % pitch), but by
   design it reads one voice per staff (closed score: 17 % notes), and its staff finder found **0 staves on every
   rotated/scanned/photocopied page**. At most it is an optional extra.
4. **What ML does not give us**:
   - **Lyrics.** copista has no text classes. Lyrics still need the Tesseract path; the detector's notehead and
     system boxes give the text bands.
   - **Rhythm and measure assembly into MusicXML.** This must be written in JS from the detections (noteheads with
     duration class, dots, voice_slot, stem_dir and staff_position; plus barlines, measure boxes, clefs, key/meter
     signatures, rests, beams, ties/slurs). An alternative is to port copisteria's Apache-2.0 reader (about 4,000
     lines of Python plus a 2.03 M-param evidence transformer). On these hymn scans the detector's raw readings are
     already more accurate (F1 0.996) than copisteria's full reader output (measure-pitch F1 0.93 with the 2m
     detector), so a simple JS assembler is the right first step.
5. **Pitch from geometry, not only from the model.** On broken-staff photocopies, copista's `staff_position` drops
   to 0.65 (2m) / 0.87 (28m), while notehead *detection* stays at F1 0.996. Compute pitch from the notehead's y
   relative to our own staff-line fit, and use the model's `staff_position` only as a cross-check.
6. Optional **"accurate" mode: copista-28m** (Apache-2.0). Its int8 weights are 26.8 MB, so they must be split into
   two external-data files (13.7 + 13.0 MB; this loads in ort-web). It costs **≈47 s/page** in wasm, and on our
   scans it only helps on the photocopy (staff-position 0.87 vs 0.65). Not worth shipping by default.

Budget for the recommended path: wasm 14.2 MB + models 2.1 MB + classes JSON 5 KB. That leaves about 47 MB of the
64 MB for Tesseract core, traineddata, pdf.js and the sample.

## Test material (`spike/ml/scans/`)

- Generator: `spike/ml/src/make_scans.py`, with pieces defined in `src/pieces.py`. All music is public domain.
  - `melody_lyrics`: *Amazing Grace* (NEW BRITAIN, text Newton 1779). G major, 3/4 with pickup, 2 verses,
    4 melismas with extenders.
  - `satb_closed`: *Old Hundredth* (Genevan 1551) in a 4-part setting written for the spike. Closed score: S+A on the
    treble staff (`\voiceOne`/`\voiceTwo`), T+B on the bass staff, 2 verses between the staves. 128 notes, 12 bars.
  - `satb_open`: the same setting on 4 staves.
- Pipeline:
  1. LilyPond 2.24 → PDF (A4, one page).
  2. `pdftoppm -r 200|300 -gray`.
  3. Six variants per page: `clean`; `rot` (1.3°); `noiseblur` (σ 1.1 px at 300 dpi + noise σ 14); `jpeg` (q30);
     `scan` (−0.8° plus a shift, uneven lighting, blur, noise, JPEG q55); `photocopy` (0.5°, blur + noise σ 25,
     hard threshold, speckle, median: broken and thickened lines).
  - Result: 36 images.
- Ground truth:
  - `scans/gt/<piece>.musicxml`: MusicXML 4.0 partwise, one `<part>` per voice, lyrics with syllabic and extend.
  - `scans/gt/<piece>.json`: note lists.
  - `scans/<image>.boxes.json`: one box per notehead, labelled with voice and note index. LilyPond **point-and-click
    link annotations** in the PDF (`\pointAndClickTypes #'note-event`) are mapped through the textedit line:col back
    to the generated source, then pushed through the same affine transform as the degradation. 288/288 noteheads
    mapped, checked visually.
- One **real scan**: `scans/real/be_thou_1919.jpg`, from Wikimedia Commons (public domain). *Church Hymnal with
  Accompanying Tunes* (1919), "Slane" in closed-score SATB, with show-through from the reverse page. No ground
  truth; used for a qualitative check only.

## Candidates and licences

| Candidate | Licence (code / weights) | What it is | Params | fp32 size | Smallest working size | Verdict |
|---|---|---|---:|---:|---:|---|
| **copista-2m** (kobimusic/copisteria 1.3.4, HF `kobimusic/copista-2m`) | Apache-2.0 / **Apache-2.0** (keep NOTICE, credit KobiMusic) | custom CenterNet-style detector, 270 classes + note attributes (staff pos, stem, dots, grace, **voice slot**), stride-4 trunk + transformer verifier | 1.92 M | 7.7 MB (2 graphs) | **2.06 MB** int8w | **recommended** |
| copista-28m (HF `kobimusic/copista-28m`, sha `44464d11…`) | Apache-2.0 / Apache-2.0 | same design, wider | 28.7 M | 114.8 MB | 29.0 MB int8w (2 × ≤14 MB external data + 2.25 MB) | optional, slow |
| copisteria evidence model (`evidence-2m.pt`) | Apache-2.0 | 6-layer transformer that re-reads detections in context (part of the Python reader) | 2.03 M | 8.1 MB (.pt) | ~2 MB expected | not exported; needs the reader's tokenizer ported |
| oemer 0.1.8 (BreezeWhite/oemer, release `checkpoints`) | MIT / MIT | 2 tf2onnx U-Nets (opset 9, uint8 NHWC windows) + sklearn SVMs + heuristics | 17.6 M + 9.6 M | 70.8 + 38.4 MB | 18.1 + 10.0 MB int8w (unet still > 15 MB) | rejected: slow, inaccurate here |
| homr 0.7.0 (liebharc/homr; segnet_308, TrOMR enc/dec 396; main uses 509) | **AGPL-3.0** / AGPL-3.0 (same repo releases) | U-Net segnet + per-staff transformer (encoder + autoregressive decoder with KV cache, contrib ops) | 14.3 + 13.2 + 46.9 M | 57.3 + 52.9 + 47.3 MB | 14.4 + 13.5 + **47.2** MB (the decoder is already int8) | **rejected: AGPL**, size, speed |
| homr `best.onnx` (release `checkpoints`) | AGPL-3.0 | Ultralytics-style YOLO, 2 classes | 1.76 M | 7.1 MB | – | AGPL; not a music-symbol detector we can use |
| satb-line-omr (alexanderalber, `model-public-domain/`) | MIT / **MIT** (PDMX-only training); sibling `model-cc-by-nc-sa/` is **CC BY-NC-SA** (Bach chorales) and must not be used | CRNN+CTC, one staff line → kern tokens | 3.2 M | 12.8 MB | 6.4 MB fp16 / 3.25 MB int8 | optional; clean open score only |
| v-dvorak/omr-layout-analysis (nota / notax notehead, OLA layout) | MIT repo, but **Ultralytics YOLOv8**-trained (Ultralytics asserts AGPL-3.0 on trained models); training data includes MUSCIMA++ (CC BY-NC-SA) | YOLOv8 detectors | – | 5.5 / 114 / 40 MB `.pt` | – | flagged: AGPL/NC risk; not evaluated |
| fusiongodo/yolo-score (DeepScoresV2 YOLO) | **no licence** | ResNet-18 YOLO | – | – | – | unusable (all rights reserved) |
| Luckolite/Sheet-Music-Recognition v0.1.5 | Apache-2.0 / Apache-2.0 (own synthetic data) | 6-class U-Net segmentation (1.95 M), TFLite fp16 3.9 MB + PyTorch `best.pt` | 1.95 M | – | 3.9 MB (tflite) | not evaluated: TFLite only (tflite2onnx fails on ARG_MAX); needs a full classical decoder anyway |
| Flova/omr_transformer, rokot-omr-2b | Apache-2.0 / CC BY-NC | seq2seq transformers | 140 M+ / 2 B | 574 MB / – | – | far too big; NC |

There is no permissively licensed DeepScoresV2-trained YOLO. Every YOLO I found was trained with Ultralytics
(AGPL-3.0 claim), has no licence, or is part of AGPL homr. DeepScoresV2 itself is CC BY 4.0 (Zenodo 4012193), so
training our own detector on it would be allowed. PDMX (the copista training scores) is CC BY 4.0 (Zenodo 15571083).
The copista detector's own corpus is described only as "87K pages" in its card; the weights are released under
Apache-2.0 by the authors.

## Accuracy

### End-to-end, using each project's own Python pipeline (upper bound for what a port could do)

Metrics:
- **Measure-pitch F1**: per-measure multiset of MIDI pitches, ignoring part and voice.
- **+duration F1**: the same, with (pitch, duration) pairs.
- **Voice-assignment accuracy**: predicted (part, staff, voice) streams are assigned one-to-one to the ground-truth
  voices (S/A/T/B or the melody), scoring LCS matches of (pitch, duration). A stream that holds chords can serve
  only one voice, so an unseparated closed score scores about 0.5.

The scorer is `spike/ml/src/eval_xml.py`. The ground-truth file scores 1.000 on every metric.

| system | piece | images | measure-pitch F1 | +duration F1 | voice-assignment acc | parts out | wall s/page (8 cores, shared box) | failures |
|---|---|---:|---:|---:|---:|---|---:|---:|
| copisteria + copista-28m | melody_lyrics | 12 | 0.953 | 0.945 | 0.945 | 1 | 72 | 0 |
| copisteria + copista-28m | satb_closed | 12 | **0.969** | 0.969 | **0.956** | **2 (2 voices each)** | 67 | 0 |
| copisteria + copista-28m | satb_open | 12 | 0.949 | 0.949 | 0.935 | 4 | 63 | 0 |
| copisteria + copista-2m | melody_lyrics | 12 | 0.875 | 0.844 | 0.844 | 1 | 27 | 0 |
| copisteria + copista-2m | satb_closed | 12 | 0.932 | 0.919 | 0.908 | 2 (2 voices each) | 27 | 0 |
| copisteria + copista-2m | satb_open | 12 | 0.911 | 0.907 | 0.898 | 4 | 27 | 0 |
| homr 0.7.0 | melody_lyrics | 12 | **1.000** | 1.000 | 1.000 | 1 | 284 | 0 |
| homr 0.7.0 | satb_closed | 12 | 0.913 | 0.913 | **0.458** (chords, no separation) | 1 | 214 | 1 |
| homr 0.7.0 | satb_open | 12 | 0.708 | 0.708 | 0.693 | 1 or 4 | 259 | 0 |
| oemer 0.1.8 | melody_lyrics | 1 | 0.438 | 0.281 | 0.281 | 1 | 697 | 0 |
| oemer 0.1.8 | satb_closed | 2 | 0.350 | 0.318 | 0.156 | 1 | 579 | 0 |
| oemer 0.1.8 | satb_open | 1 | 0.198 | 0.198 | 0.125 | 1 | 685 | 0 |

The same results by degradation (all three pieces, 200 and 300 dpi; cells are measure-pitch F1 / voice-assignment
accuracy):

| system | clean | rot 1.3° | noise+blur | JPEG q30 | "scan" | "photocopy" |
|---|---|---|---|---|---|---|
| copisteria + 28m | 0.997 / 0.994 | 0.994 / 0.988 | 0.997 / 0.994 | 0.995 / 0.991 | 0.992 / 0.984 | 0.769 / 0.723 |
| copisteria + 2m | 0.994 / 0.990 | 0.995 / 0.990 | 0.995 / 0.990 | 0.994 / 0.988 | 0.996 / 0.992 | 0.463 / 0.352 |
| homr | 0.915 / 0.750 | 0.915 / 0.750 | 0.915 / 0.750 | 0.915 / 0.750 | 0.915 / 0.750 | 0.665 / 0.553 (1 crash: "No staffs found") |
| oemer | 0.330 / 0.190 (4 pages only, 8–11 min each) | – | – | – | – | – |

Notes:
- The piece averages above include the photocopy column. On every other degradation copisteria scores at least
  0.99 measure-pitch F1 and 0.98 voice-assignment accuracy.
- Raw results: `spike/ml/out/e2e/results.jsonl`. Outputs: `spike/ml/out/e2e/<system>/<image>/`.
- oemer needed `opencv-python-headless<5` (it crashes in `find_lines` with OpenCV 5), and ORT pinned to 8 threads.
  Unpinned, one page took 35 min and 4.5 CPU-hours.

### Detector-level: copista through the browser-portable pipeline (`src/copista_core.mjs`)

Predicted `note_*` boxes are matched one-to-one to ground-truth noteheads (centre within 0.6 notehead widths).
Attribute accuracies are computed on matched notes:
- staff position: half-spaces from the middle line, against ground-truth pitch and clef.
- stem: closed score only, whole notes excluded.
- voice slot: closed score only; S/T should be 1, A/B should be 2.

Scorer: `src/eval_notes.py` and `src/score_dets.py`. "web" means onnxruntime-web 1.30.0 wasm (run in node; Chromium
gives identical detections, see below). "torch" means the authors' PyTorch detector inside copisteria. CPU ms is
process CPU time per page, which is robust to the machine being shared (load average was often above 1000).

| run (runtime-model-weights-threads) | images | notehead P | R | F1 | staff-pos acc | stem acc | voice-slot acc | median CPU ms/page |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| torch-2m-fp32 (reference) | 36 | 1.000 | 0.992 | 0.996 | 0.944 | 0.984 | 0.991 | – |
| node-2m-fp32-t1 | 36 | 1.000 | 0.992 | 0.996 | 0.943 | 0.984 | 0.991 | 2042 |
| node-2m-int8d-t1 | 36 | 1.000 | 0.992 | 0.996 | 0.939 | 0.984 | 0.991 | **982** |
| web-2m-fp32-t1 | 36 | 1.000 | 0.992 | 0.996 | 0.943 | 0.984 | 0.991 | 4162 |
| web-2m-fp16w-t1 | 36 | 1.000 | 0.992 | 0.996 | 0.943 | 0.984 | 0.991 | 4179 |
| **web-2m-int8w-t1** | 36 | 1.000 | 0.991 | **0.996** | 0.941 | 0.984 | **0.991** | **4178** |
| web-2m-int8d-t1 | 36 | 1.000 | 0.993 | 0.996 | 0.938 | 0.984 | 0.991 | 12336 |
| torch-28m-fp32 (reference) | 36 | 1.000 | 0.992 | 0.996 | 0.967 | 0.987 | 0.991 | – |
| node-28m-fp32-t1 | 24 | 1.000 | 0.990 | 0.995 | 0.970 | 0.984 | 0.991 | 18892 |
| node-28m-int8w-t1 | 24 | 1.000 | 0.989 | 0.995 | 0.968 | 0.984 | 0.991 | 18966 |
| node-28m-int8d-t1 | 24 | 1.000 | 0.990 | 0.995 | 0.958 | 0.984 | 0.991 | 6813 |
| web-28m-int8w-t1 | 3 | 1.000 | 0.997 | 0.999 | 0.831 | 0.991 | 0.991 | 48421 |

Staff-position accuracy is **1.000 on clean, rot, noise+blur, JPEG and scan** for every 2m and 28m variant. On the
photocopy it drops to 0.63–0.66 (2m) and 0.83–0.88 (28m). Detection itself stays at F1 0.995–0.997 there, which is
why pitch should come from staff-line geometry.

Notes:
- My ONNX export plus JS decode reproduces the PyTorch reference (identical P/R/F1, staff-position 0.943 vs 0.944).
- The JS box-filter resample is used instead of PIL Lanczos and makes no measurable difference.
- Where the remaining voice-slot errors (0.9 %) come from:
  - **Stemless whole notes** in the bass voice (two per page), where the model guesses voice 1. The assembler should
    resolve these from vertical order and rhythm: the lower whole note on a two-voice staff is voice 2.
  - **One tight S/A second**, read as `stem_dir=both`.
  - In addition, 1–3 noteheads per page are missed (for example the soprano B4 in bar 4).

### satb-line-omr (MIT CRNN+CTC), using its own reference staff finder and decoder (`src/eval_satbline.py`)

| piece | clean: notes / pitch | JPEG q30 * | noise+blur * | rot / scan / photocopy |
|---|---|---|---|---|
| satb_open (300 / 200 dpi) | **1.000 / 1.000**, 0.992 / 1.000 | 1.000, 0.992 | 0.922, 0.734 (pitch 1.0 / 0.97) | 0 staves found → 0.0 |
| melody_lyrics | 0.938 / 1.000, 0.844 / 1.000 | 0.938, 0.844 | 0.813, 0.563 | 0 staves found → 0.0 |
| satb_closed | 0.18 / 0.43 (reads one voice per staff, by design) | 0.17 | 0.16 | 0.0 |

\* scored with the staff boxes found on the clean page; its own staff finder finds nothing on these.

Timings are about 0.11 s per 1200-px line in native ORT and 0.26 s in wasm (fp32).

The authors' "browser default" full-fp16 file is **2× slower in wasm** (0.54 s) than fp32. My weight-only `fp16w`
runs at fp32 speed (0.26 s) at the same 6.4 MB.

### Real 1919 hymnal scan (qualitative)

copista-2m int8w ran in the wasm runtime on the left page (1600×2373, show-through, old-style clefs):
- 2.86 s CPU.
- 197 noteheads. Voice slots are consistently up=1/down=2 on both staves.
- Clefs (G2, F4), key (1♭) and meter (3/2) are all found.
- A handful of hollow notes are missed (visual inspection: `spike/ml/out/real/be_thou_1919_copista2m_overlay.png`).

copisteria + 28m produces 2 parts × 2 voices with 196 notes. homr produces 1 part with 200 notes, as chords in a
single voice.

## Size and quantization (`src/quantize.py`)

Four variants were built for every model:
- **fp16w**: initializers stored as fp16 with a Cast to fp32; compute stays fp32.
- **int8w**: per-output-channel symmetric int8 initializers plus DequantizeLinear; compute stays fp32.
- **fp16**: full fp16 graph via onnxconverter-common 1.16 with `keep_io_types`.
- **int8d**: `onnxruntime.quantization.quantize_dynamic`, QInt8, per-channel.

| model | fp32 | fp16w | int8w | fp16 (full) | int8d | ≤ 15 MB per file? |
|---|---:|---:|---:|---:|---:|---|
| copista2m dense / rel | 6.71 / 1.01 MB | 3.39 / 0.52 | **1.77 / 0.29** | 3.38 / converter error | 1.78 / 0.30 | yes (all variants) |
| copista28m dense / rel | 106.1 / 8.7 MB | 53.1 / 4.4 | 26.8 / 2.25 | 53.1 / error | 26.8 / 2.27 | only int8w split into 2 × ≤ 14 MB external data |
| oemer unet / seg | 70.8 / 38.4 MB | 35.7 / 19.5 | 18.1 / 10.0 | fails to load (Cast type error) | 20.1 / 13.1 | no (unet ≥ 18 MB) |
| homr segnet308 | 57.3 MB | 28.7 | 14.4 | 28.7 (loads; ORT falls back) | 14.4 | yes |
| homr encoder 396 / 509 | 52.9 MB | 26.5 | 13.5 | 26.5 | 15.6 | int8w only |
| homr decoder 396 / 509 | 47.3 MB (already int8, contrib ops) | 47.2 | 47.2 | error | 47.3 | no; would need 4-bit plus splitting, and total ≥ 75 MB > 64 MB |
| satb-line MIT | 12.8 MB | 6.4 | 3.2 | 6.4 (authors' file) | 3.3 | yes |

Findings:
- Weight-only storage (fp16w/int8w) is the right tool for wasm. It gives a ¼ size download at fp32 speed with no
  accuracy loss (copista: identical scores).
- ORT dynamic int8 is 2× faster in native ORT but 2.5–3× slower in wasm: copista2m 12.2 s vs 4.1 s, 28m 133 s vs
  47 s, oemer-seg 14.8 s vs 5.9 s, homr segnet 2.2 s vs 0.75 s.
- Full fp16 graphs are slower or broken on CPU/wasm.
- When opset-9 tf2onnx models (oemer) get weight-only transforms, they must first be upgraded with
  `onnx.version_converter` to opset 13; Slice changed from attributes to inputs.

## Speed (`src/microbench.mjs`, one thread, process CPU ms; representative input)

| model | input | ort-node 1.30.0 | ort-web 1.30.0 wasm | per-page estimate in wasm |
|---|---|---:|---:|---|
| copista-2m dense (fp32/fp16w/int8w) | 1×1×1760×1248 (300 dpi A4 at 10.6 px staff space) | 1.82–1.86 s | **4.09–4.10 s** | **≈4.3 s** (+0.1 s verifier, 0.1–0.3 s prep) |
| copista-28m dense | same | 21.0 s | 47.0 s | ≈48 s (Chromium, split int8w: 46.6 s) |
| oemer unet / seg | one 256² / 288² u8 window; **234 windows each** per page | 1.09 / 2.42 s | 2.44 / 5.93 s | ≈ 234 × 8.4 s ≈ **33 min** |
| homr segnet | one 320² patch | 0.32 s | 0.79 s | tens of patches/page → 30–60 s |
| homr encoder | one staff 256×1280 | 1.15 s | 2.52 s | 8 staves → 20 s |
| homr decoder | one token step | 0.063 s | 0.45 s | ~100 tokens × 8 staves → **≈6 min** |
| satb-line (fp32 / fp16w) | one 1200-px line | 0.11 s | 0.26 s | 8–16 lines → 2–4 s (clean open score only) |

On this aarch64 server, wasm runs at about 0.45× native. Headless Chromium matches the node-wasm numbers within
about 10 %. A desktop x86 browser is probably faster: the satb-line authors report 176 ms/line on a Ryzen
5800X3D, against our 260 ms.

## onnxruntime-web in a browser under an artifact-like CSP (`src/web_bench.mjs`)

Setup:
- Browser: headless Chromium (Playwright chromium_headless_shell-1248, arm64).
- Page: copista-2m on `satb_closed_300_scan.png`, decoded via `createImageBitmap` → OffscreenCanvas → gray.
- Hosting: ORT JS comes from the public CDN. The `.wasm`, models and image are served same-origin.
- CSP, as an HTTP header (`strict`):
  ```
  default-src 'none'; script-src https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com
  'unsafe-inline' 'wasm-unsafe-eval'; connect-src 'self' blob: data:; worker-src 'self' blob:;
  img-src 'self' blob: data:; style-src 'unsafe-inline'
  ```
- Raw rows: `spike/ml/out/web/results.jsonl`; logs: `out/web/matrix{1,2,3}.log`.

| ort-web | how it is loaded | strict CSP result | page time (warm) |
|---|---|---|---|
| 1.18.0 | `<script src=…/ort.wasm.min.js>` (UMD, jsdelivr or cdnjs), `wasmPaths='assets/'` prefix | **OK**, main thread | 4.45–5.4 s |
| 1.18.0 | blob: classic worker + `importScripts(CDN ort.wasm.min.js)` | **OK**, in worker | 5.36 s |
| 1.20.1 / 1.22.0 / 1.30.0 | UMD `ort.wasm.min.js` (main thread or `importScripts` worker) | **FAIL**: dynamic `import()` of same-origin `ort-wasm-simd-threaded.mjs` is blocked by script-src (works when CSP has `'self'`: 1.30.0 4.5 s) | – |
| 1.22.0 / 1.30.0 | ESM `ort.wasm.bundle.min.mjs` from CDN, `wasmPaths` **string** | **FAIL** (same `.mjs` import) | – |
| 1.20.1 | ESM `ort.bundle.min.mjs`, string `wasmPaths` | OK (2 non-fatal "script-src eval" reports) | 5.1 s |
| 1.22.0 / **1.30.0** | ESM bundle from jsdelivr/cdnjs, `wasmPaths = { wasm: '<abs url>/ort-wasm-simd-threaded.wasm' }` | **OK**, no CSP reports | 4.47–5.1 s |
| 1.20.1 / 1.22.0 / **1.30.0** | **blob: module worker + dynamic `import(CDN bundle)`** + `{ wasm }` | **OK** (jsdelivr and cdnjs) | best of 2: 4.2–4.7 s (single runs 4.2–11 s on the loaded box) |
| any | blob: module worker with *static* `import … from CDN` | FAIL (worker error, no message) | – |

Weights variants, multi-threading and external data on the working paths (strict CSP):
- Chromium int8w detections are **identical** (191 of 191 boxes) to the node onnxruntime-web int8w run used in the
  accuracy table, on ORT 1.18.0 and 1.30.0. Every weight variant finds the same 124 noteheads on this page
  (int8d: 125).
- Warm page times (1.30.0 ESM and 1.18.0 UMD): fp32 / fp16w / int8w are all 4.1–4.4 s; int8d is 11.6 s on 1.30.0.
- **int8d does not load at all on 1.18.0**: "Could not find an implementation for ConvInteger(10)".
- **Always set `ort.env.wasm.numThreads = 1`.** With `numThreads=4`, the 1.30.0 bundle fetches
  `ort-wasm-simd-threaded.mjs` *from the CDN* to start its thread workers, and connect-src blocks that ("no available
  backend"). This happened even with COOP/COEP headers sent; in this harness `crossOriginIsolated` stayed false, so
  the multi-thread upside was not measured. The artifact host cannot be assumed to send those headers anyway.
  With 1.18.0 and `numThreads=4` the page **hangs** with no error: its thread workers `importScripts` a `blob:` URL,
  script-src blocks that, and the workers die silently.
- copista-28m int8w split into two external-data files loads via `externalData: [{path, data: url}]` and runs
  in 46.6 s for the page (127 of 128 noteheads).
- Other pages with 1.30.0 int8w: `satb_open_300_clean` 4.3 s, 128 note boxes for 128 noteheads;
  `melody_lyrics_200_photocopy` 4.3 s, 32 for 32.
- Full numbers are in the matrix logs; see the appendix table generated by `src/summarize.py` (`out/tables.md`).

### Loader that worked (ORT 1.30.0, strict CSP, off the main thread)

```js
const BASE = new URL('.', location.href).href;            // blob: workers can't resolve relative URLs
const SRC = `
const ortP = import('https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/ort.wasm.bundle.min.mjs');
self.onmessage = async ({ data }) => {
  const ort = await ortP;
  ort.env.wasm.numThreads = 1;
  ort.env.wasm.wasmPaths = { wasm: data.base + 'assets/ort-wasm-simd-threaded.wasm' };  // object form!
  const get = async (f) => new Uint8Array(await (await fetch(data.base + 'assets/' + f)).arrayBuffer());
  const dense = await ort.InferenceSession.create(await get('copista2m-dense.int8w.onnx'), { executionProviders: ['wasm'] });
  const rel   = await ort.InferenceSession.create(await get('copista2m-rel.int8w.onnx'),   { executionProviders: ['wasm'] });
  // ... copista_core.detect(ort, {dense, rel}, meta, data.gray) -> postMessage(dets)
};`;
const worker = new Worker(URL.createObjectURL(new Blob([SRC], { type: 'text/javascript' })), { type: 'module' });
worker.postMessage({ base: BASE, gray /* {width,height,data} */ }, [gray.data.buffer]);
```

Fallback with ORT 1.18.0:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/onnxruntime-web/1.18.0/ort.wasm.min.js"></script>
```
then `ort.env.wasm.wasmPaths = 'assets/'` and self-host `ort-wasm-simd.wasm`. For a worker, use
`importScripts(<same URL>)` in a blob: classic worker with an absolute `wasmPaths`.

## How the detector maps onto the product requirements

- **Closed-score SATB → separate parts.** For each staff, notes with `voice_slot=1` (stems up) become S (treble) or
  T (bass), and `voice_slot=2` become A or B. `stem_dir=both` on a shared head goes into both voices.
  The brace/bracket class (`grpSym_*`) is **not** enough to tell a choir system from a piano one: the 1919 hymnal
  braces its closed-score SATB. Decide "split vs piano" from voice structure instead: two consistent stem-direction
  voices per staff, mostly homorhythmic, with a lyric band between or under the staves → split. Keyboard texture
  (chords on one stem, cross-staff beams, no lyrics) → keep as one part.
- **Rhythm.** Duration comes from the note class (`note_whole … note_16th`) plus the `dots` attribute, rests from
  the `rest_*` classes, and bar boundaries from `barLine_*` and `measure` boxes (one per staff per bar). Clefs,
  `keySig_*` and `meterSig_N_D` (82 meter classes) are all detected.
- **Pitch.** Use our own staff-line fit with notehead y. Cross-check against `staff_position` and use it when the
  staff fit is unsure. Get the clef from the `clef_*` class.
- **Lyrics.** Not covered. Run OCR on the band between the notehead boxes of adjacent staves, or below the system.
  Attach syllables by x to the voice that carries them: in a hymn the between-staves verses belong to S, and to A,
  T and B too when they are homorhythmic.

## Files (all under `spike/ml/`)

- **Assets**
  - `assets/`: copista-2m ONNX (int8w recommended; fp16w and fp32 too), `copista2m-classes.json`, LICENSE and NOTICE
    files, `PROVENANCE.md` (sources, sha256, conversion commands), `SHA256SUMS`.
  - `assets/copista28m/`: optional 28m int8w, split into ≤14 MB external data.
- **Source code (`src/`)**
  - Browser/node pipeline: `copista_core.mjs`, with its Python reference in `omr_copista.py`.
  - Model conversion: `export_copista.py`, `quantize.py`, `split_external.py`.
  - Scans and evaluation: `make_scans.py`, `pieces.py`, `eval_xml.py` (MusicXML scorer), `eval_notes.py` and
    `score_dets.py` (notehead scorer), `run_e2e.py` and `oemer_wrap.py` (reference pipelines), `eval_satbline.py`.
  - Harnesses: `node_copista.mjs` (node harness), `microbench.mjs`, `web_bench.mjs` (Chromium + CSP harness).
  - Tables: `summarize.py`.
- **Data**
  - `scans/`: 36 test images plus `.boxes.json` notehead ground truth; `scans/gt/` holds MusicXML and JSON ground
    truth; `scans/ly/` holds the LilyPond sources and PDFs; `scans/real/` holds the 1919 scan.
- **Results (`out/`)**
  - `e2e/results.jsonl`, `nodedets/`, `dets_scores.json`, `micro/`, `satbline/results.jsonl`, `web/results.jsonl`.
  - `tables.md` holds every table, regenerated from the raw files.
  - Overlays: `real/be_thou_1919_copista2m_overlay.png`, `gt_overlay_check.png`.

## Reproduce

All commands run from `spike/ml/`. The venvs were created by the spike.

```
.venv/bin/python src/make_scans.py                                  # scans + ground truth (≈25 s)
.venv-cop/bin/python src/export_copista.py                          # ONNX export + parity check
.venv/bin/python src/quantize.py out/onnx/copista2m-dense.onnx out/onnx/copista2m-dense fp16w int8w int8d
.venv/bin/python src/split_external.py out/onnx/copista28m-dense.int8w.onnx out/onnx/copista28m-dense.int8w.split.onnx 14
node src/node_copista.mjs web 2m int8w 1 scans/*_*_*.png           # browser-equivalent run -> out/nodedets/
.venv/bin/python src/score_dets.py                                  # notehead P/R/attrs
.venv/bin/python src/run_e2e.py homr cop2m cop28m                   # reference pipelines (+ oemer: see run_e2e.py)
.venv/bin/python src/eval_satbline.py
node src/microbench.mjs web 1 out/onnx/*.onnx
node src/web_bench.mjs out/web/matrix2.json                        # Chromium, strict CSP
.venv/bin/python src/summarize.py > out/tables.md
```

Exact versions:
- Runtimes: onnxruntime-node 1.30.0, onnxruntime-web 1.30.0 / 1.22.0 / 1.20.1 / 1.18.0 (npm tarballs in
  `spike/ml/ortweb/`); Python onnxruntime 1.31.1.
- Tooling: onnx 1.23.x, onnxconverter-common 1.16.0, torch 2.15.0+cpu, torchvision 0.29.2, playwright-core 1.48.2,
  Chromium build 1248.
- Projects: copisteria commit `c685f280914d91a694494588d9f6a376d7917eba`, homr 0.7.0 (PyPI), oemer 0.1.8 (PyPI) with
  checkpoints from `https://github.com/BreezeWhite/oemer/releases/download/checkpoints/{1st,2nd}_model.onnx`,
  satb-line-omr commit `c60823117a5c92b0c29f921dbca023e94026d279`.
- Engraving and rendering: LilyPond 2.24, poppler `pdftoppm`.

## Caveats

- **Machine.** The box was shared and heavily loaded (load average 500–1400 on 192 cores) while I measured. Wall
  times are noisy, which is why CPU ms is reported. Chromium numbers are single runs on aarch64.
- **Test data.** The scans are synthetic, from LilyPond engraving, and the pieces are simple, homophonic hymn
  textures. copista was trained on varied engravings with scan effects, so the near-perfect detector numbers here
  are likely optimistic for 19th-century prints. The one real 1919 scan looked good, with a few misses, but it has no
  ground truth.
- **Python baselines.** copisteria e2e numbers include its own Python reader. Our browser path would replace that
  with a JS assembler, so its accuracy is still to be built and measured.
- **Out of scope.** Lyrics and OCR were not evaluated in this spike.
