# Spike: lyric OCR for scanned sheet music

Status: done (2026-11-08). Code, data generators and raw results are in `spike/ocr/`. Every number below can be reproduced with the commands in [Reproduce](#reproduce).

## TL;DR

* **Lyric OCR in the browser works well enough to ship.** On detected and cleaned lyric strips from 280 synthetic scanned pages (5 degradations, English/German/Latin, 1–3 verses, 17 typefaces incl. italic verses), the best engines reach **1.3–1.5 % character error rate (CER)**. Syllable error rate is 10–12 %, and about 6 points of that come from hyphens the engraver did not print (see below). Hyphen detection reaches **P 99.7–99.8 % and R 97–99 %**.
* **Lyric strip isolation is solved with classical image processing** (`spike/ocr/src/strips.js`, pure JS, about 300 lines, no ML). It finds **100 % of the 1,920 ground-truth lyric lines with 99.2 % precision** on all five degradations. Each line comes back with baseline, x-height, font size (median error 9 %), and geometric hyphens (**P 96.6 % / R 97.8 %**) and extenders (P 63 % / R 81 %) with x positions. It runs in 0.08–0.46 s per page in Node.
* **Recommendation:**
  1. If the app ships **onnxruntime-web** anyway (for the OMR symbol models), use **PaddleOCR PP-OCRv5 `latin_PP-OCRv5_mobile_rec` (ONNX, 8.0 MB, Apache-2.0)**. It is the most accurate (e2e CER 1.3 %, oracle-crop CER 1.9 %, or 1.3 % with cleaning), has the best hyphen recall (99.3 %), covers eng/deu/lat with a single model, and needs no language choice. Cost: 142 ms per strip on 1 thread in Node (45 ms on 4 threads), 229–263 ms in headless Chromium.
  2. Otherwise use **tesseract.js 7.0.0 with the `best_int` models** (`eng`/`deu`/`lat` .traineddata.gz, 6.0 MB total) and the simd-lstm core (3.9 MB). Apply the **gap-compression** preprocessing described here (it cuts WER from 19.5 % to 11.5 %) with PSM 7. e2e CER is 1.5 %. If the language is unknown, `eng+deu+lat` gives the best syllable and word scores (SylER 10.2–10.7 %) at about 1.8× the time.
  3. In both cases, run OCR **per detected strip**, never on the whole page. Feed the engine the *masked* strip (only the text components kept). Use the geometric hyphen and extender detector to place syllables against notes and to find melismas.
* **Gotchas found:**
  * tessdata_best *float* models crash tesseract.js 7 (`missing function DotProductSSE`), so use `best_int`.
  * Disabling Tesseract dictionaries has no effect.
  * PSM 6 is catastrophic on lyric strips (CER 15.9 %).
  * PaddleOCR must **not** get gap-compressed strips: it needs at least 1 CTC frame per character, and CER rises to 11 %.
  * `ort.env.wasm.wasmPaths` must be an **absolute** URL.
  * ORT 1.31.1's `ort-wasm-simd-threaded.wasm` is 14,848,852 B, just under the 15 MB per-file limit.

## 1. Test data

`spike/ocr/gen/` (Python 3.12 venv: pdfplumber 0.11.4, numpy, opencv-python-headless 5.0, pyyaml; LilyPond 2.24.3; poppler `pdftoppm`):

* `texts.py`: 14 public-domain texts, pre-syllabified, 2–3 verses each.
  * **English (5):** Abide with Me, O God Our Help, Holy Holy Holy, Amazing Grace, Angels We Have Heard on High (with the Latin "Gloria" refrain).
  * **German (4):** Nun danket alle Gott, Ein feste Burg, Wer nur den lieben Gott, Lobe den Herren. These include ä/ö/ü/ß.
  * **Latin (5):** Pange lingua, Veni Creator, Stabat Mater, Adeste fideles, Ave verum.
* `make_ly.py`: 56 LilyPond scores built from random melodies with **melismas**: slurred groups with `__` extenders, plus ties from `Completion_heads_engraver`.
  * Layouts:
    * closed-score SATB with lyrics between the staves (132 lines)
    * melody plus 2–3 verses (84)
    * open score with lyrics under all 4 staves (122)
    * voice + piano (46)
  * Formatting: stanza numbers ("1.") on 70 % of pieces, italic even verses on 30 %, staff size 16–20, lyric size −1…+1 steps.
  * 12 font families, which give 17 faces: TeX Gyre Schola/Termes/Bonum/Pagella/Heros, C059, P052, Liberation Serif, DejaVu Serif/Sans, Latin Modern, Charter. Pango falls back to DejaVu Sans for some.
* `gt.py`: renders each page at 300 dpi and extracts ground truth from the PDF with pdfplumber:
  * lyric chars by baseline and size, with ligatures (`ﬁ`/`ﬂ`) and `(cid:N)` Latin-1 glyphs handled;
  * an alignment to the logical syllables from the generator;
  * a **printed** hyphen/extender flag per syllable gap, measured on the clean raster. LilyPond drops a hyphen when the gap is too small, and **8.6 % of logical hyphens are not printed**.

  Coverage check: every syllable of every verse was matched (0 mismatches).
* `degrade.py`: produces 5 variants per page, transforming the GT boxes and syllable x positions accordingly:

  | variant | simulates | details |
  |---|---|---|
  | `clean300` | born-digital rasterised | 300 dpi gray |
  | `scan300` | flatbed gray scan | tilt ±0.35°, blur σ 0.5–0.9, paper tone 228–245, illumination ±8 %, noise σ 6, JPEG q70–85 |
  | `bilevel300` | IMSLP-style 1-bit | blur + noise + threshold 105–165 (thin or fat strokes, **faint staff lines drop out**), salt/pepper |
  | `copy200` | photocopy | 200 dpi, eroded/darker strokes, gutter shadow, toner specks, noise σ 9 |
  | `phone150` | phone / low-res scan | 150 dpi, blur σ 1, strong illumination gradient (25 %), low contrast, JPEG q55 |

Totals: **56 docs → 280 page images, 1,920 lyric-line strips** (eng 158 / deu 103 / lat 123 lines per variant). Each variant has 6,885 syllables, 2,645 logical hyphens (2,418 printed), 876 melisma syllables and 170 printed extenders. Lyric font size is 35–51 px at 300 dpi.

Limitations of the data: it is synthetic. It has no real paper texture, bleed-through or page curl, no Fraktur, no handwritten annotations, and only modern engraving fonts. Real IMSLP/CPDL scans should be added to the harness (see [Follow-ups](#9-risks-and-follow-ups)).

## 2. Metrics

`spike/ocr/src/metrics.js`. OCR text first goes through the filter the app would use: drop `|[]{}<>/\*#@=+` and similar, map ’→', all dashes to `-`, `_` to space.

* **CER**: Levenshtein distance on the text with whitespace and hyphens removed (letters + punctuation), divided by GT length.
* **SylER**: edit distance over syllable tokens (split on space and hyphen, punctuation stripped). This is what becomes one `<lyric><text>` per note. **Floor: a perfect OCR of the *printed* page still scores 6.1 % SylER (eng 3.2 / deu 4.4 / lat 10.0)**, because hyphens the engraver omitted ("Morgen" instead of "Mor-gen") can only be recovered by note alignment or hyphenation patterns.
* **WER**: words after joining hyphenated syllables, punctuation stripped.
* **Hyphen P/R**: computed per GT syllable gap after character alignment of OCR to GT. Only gaps where a hyphen was printed count as positives.

## 3. Lyric strip isolation (`src/strips.js`)

The input is a grayscale page `{width,height,data}`, so the same code runs in Node and in the browser. Steps:

1. **Adaptive binarisation**: local mean over a window of about W/45, k = 0.15, capped at Otsu + 40.
2. **Staff-line thickness `lt` and spacing `ss`** from vertical run-length histograms: the most frequent black run, and the most frequent white run above 2·lt.
3. **Skew** from the projection-profile variance over ±1° in 0.05° steps, using 32-px column chunks. The image is then sheared, not rotated. Estimates matched the applied tilt to within the step size.
4. **Staff lines** from a row projection that counts only horizontal runs longer than 2·ss, smoothed over the line thickness, with a threshold of 0.25 × robust max. Candidates closer than 0.4·ss are merged.
5. **Staves** are grouped as 5 lines at spacing ss+lt (±30 %). The grouping **tolerates one missing line** (inner gap 2d, or an outer line inferred from the side with more long-run ink). Without this, the bilevel variant lost 3.4 % of lines.
6. For every band between consecutive staves (and up to 14 staff spaces below the last staff), find connected components that **do not touch the band edges**. Touching components are attached to the staff: notes, stems, beams. Also drop components taller than 4·ss or wider than 30·ss.
7. **Baselines**: build a histogram of component bottoms for letter-sized components (0.45–3.2 ss high), smooth it, and take peaks at least 1.4·ss apart. Each peak needs at least 4 core letters, and the median core height must be at least 0.6·ss so that rows of toner specks are rejected. A line's members are all components inside [baseline − 1.9·cap, baseline + 0.6·cap].
8. **Per line output**:
   * bbox and baseline, mapped back through the shear;
   * x-height, cap height and font size ≈ cap/0.70;
   * **hyphens**: flat components (h ≤ 0.4·xh, w ≥ 1.6·h) centred between 0.15 and 0.95 xh above the baseline;
   * **extenders**: flat components at the baseline that are at least 1.2·xh wide;
   * a **masked strip** containing only member pixels from the deskewed gray image, which removes stems and noteheads that poke into the text band.

Results (`results/summary_det.json`, every page of every variant):

| | value |
|---|---|
| lyric-line recall | **100.0 %** (1920/1920) |
| precision | **99.2 %** (15 false lines, mostly toner-speck rows in `copy200`; trivially filtered by "OCR text has < 2 letters") |
| font-size estimate | median rel. error 9.1 %, p90 26.5 % |
| geometric hyphens (per variant set) | P 96.6 %, R 97.8 % (tp 11958 / fp 418 / fn 267 over the 5 variants) |
| geometric extenders | P 63.5 %, R 81.3 % (usable as a melisma *hint*, combined with slurs/ties from the OMR) |
| time (Node 24, 1 thread) | 461 ms/page at 300 dpi (2480×3508), 163 ms at 200 dpi, 79 ms at 150 dpi |

An example overlay is in `spike/ocr/results/samples/detect_*.png`: staves in blue, lyric lines in red, hyphens in green, extenders in orange.

Things that would break it, and are not in the test set:

* Lyrics touching notes or stems: very tight hymnals, or slurs crossing the text.
* Text above the staff: chord symbols, or lyrics placed above.
* Strongly curved page lines: phone photos of bound books need dewarping first.
* Dynamics or "cresc." in the lyric band. They usually fail the "≥ 4 letters spread over ≥ 20 % of the staff width" test, but can merge into a lyric line.

The OMR pipeline should reuse steps 1–5 (skew, staves) and step 6 (components) instead of re-running them.

## 4. Engines evaluated

All engines run in Node through the same harness. Tesseract runs as tesseract.js (WASM), not native.

| engine | version / source | files & sizes (bytes) | licence |
|---|---|---|---|
| tesseract.js | `tesseract.js@7.0.0` (2025-12-15) — `dist/tesseract.min.js` 62,961, `dist/worker.min.js` 111,307 | | Apache-2.0 |
| tesseract.js-core | `tesseract.js-core@7.0.0` — LSTM-only builds `tesseract-core-simd-lstm.wasm.js` 3,899,472 (1.46 MB gz), `-relaxedsimd-lstm.wasm.js` 3,905,767, `-lstm.wasm.js` (no SIMD) 3,896,484 | | Apache-2.0 |
| traineddata `best_int` (tesseract.js default) | `https://cdn.jsdelivr.net/npm/@tesseract.js-data/{eng,deu,lat}/4.0.0_best_int/{lang}.traineddata.gz` | eng 2,952,873 · deu 1,333,102 · lat 1,739,234 (gz) | Apache-2.0 |
| traineddata `fast` | `https://github.com/tesseract-ocr/tessdata_fast/raw/main/{lang}.traineddata` | eng 4,113,088 (gz 1,976,309) · deu 1,525,436 (gz 853,431) · lat 3,187,463 (gz 1,739,991) | Apache-2.0 |
| traineddata `best` (float) | `https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata` | eng 15,400,601 · deu 8,628,461 · lat 9,705,145 | Apache-2.0 — **does not run in tesseract.js 7** (abort: `missing function _ZN9tesseract13DotProductSSEEPKfS1_i`, in both the LSTM and full cores). `best_int` is the int8 conversion of the same nets. |
| PaddleOCR PP-OCRv5 latin mobile rec | `https://huggingface.co/PaddlePaddle/latin_PP-OCRv5_mobile_rec_onnx` (`inference.onnx` + `inference.yml` with the 836-char dict; official PaddlePaddle export, modified 2026-05-26) | 8,042,023 | Apache-2.0 |
| PaddleOCR PP-OCRv5 en mobile rec | `https://huggingface.co/PaddlePaddle/en_PP-OCRv5_mobile_rec_onnx` | 7,848,423 (436-char dict, **no ß/œ**) | Apache-2.0 |
| onnxruntime | `onnxruntime-node@1.31.1` (harness); `onnxruntime-web@1.31.1`: `dist/ort.wasm.min.js` 53,796 + `ort-wasm-simd-threaded.mjs` 24,738 + `ort-wasm-simd-threaded.wasm` **14,848,852** (just under the 15 MB/file limit; the `.jsep`/`.asyncify` variants are 28–30 MB and do not fit) | | MIT |

Alternatives that were looked at but not run (and why):

| candidate | size | licence | verdict |
|---|---|---|---|
| PP-OCRv5 multilingual mobile rec (`PaddlePaddle/PP-OCRv5_mobile_rec_onnx`) | 16,534,782 | Apache-2.0 | Over the 15 MB per-file limit, and its CJK vocabulary is useless here. |
| PP-OCRv5 server rec | 84,503,027 | Apache-2.0 | Too big. |
| docTR / OnnxTR `crnn_mobilenet_v3_small` (8-bit 5,657,454; fp32 8,331,378), `parseq` (8-bit 34.5 MB), `vitstr_small` (22 MB) | | Apache-2.0 | Fixed 32×128 input, so long lyric lines would need chunking. PP-OCRv5 latin is already near the ceiling here. |
| ocrs (robertknight/ocrs, Rust + WASM, rten models) | ~10 MB | Apache-2.0/MIT | Model bucket returned 403 at test time. English/Latin alphabet only. |
| Tesseract Fraktur: `tessdata_best/deu_latf` 12,938,047; `tessdata_fast/deu_latf` 6,423,052; `tessdata_fast/script/Fraktur` 10,915,632 | | Apache-2.0 | Relevant for old German hymnals; untested (no Fraktur test data). |
| Calamari OCR | | **GPL-3.0** | Do not ship. |
| Kraken | | Apache-2.0 code, models vary | Python only. |
| TrOCR / Donut-class models | | | Far too big for the 64 MB budget. |

Licence flags:
* Nothing in the recommended runtime stack is GPL/AGPL.
* **LilyPond (GPL-3.0)** and **pdfplumber/pdfminer.six (MIT)** are used only offline, to generate test data. They are not shipped.
* PyMuPDF (AGPL) was deliberately avoided.

## 5. Results

### 5a. End-to-end: detected and masked strips (`results/table_e2e.md`, `results/summary_e2e.json`)

"fused" = OCR tokens with hyphens from OCR **or** geometry. It did not beat OCR-only hyphens, so CER/SylER/WER are effectively the OCR-only numbers.

| config | CER % | SylER % | WER % | hyphen P/R % | clean300 | scan300 | bilevel300 | copy200 | phone150 (CER %) |
|---|---|---|---|---|---|---|---|---|---|
| **Paddle latin_v5**, font 40 px → height 48 | **1.3** | 12.0 | 11.7 | **99.8 / 99.3** | 1.1 | 1.3 | 1.1 | 1.9 | 1.2 |
| tess best_int **matched lang**, PSM 7, **gap-compress** | 1.5 | 11.5 | 11.5 | 99.7 / 96.9 | 1.3 | 1.2 | 2.0 | 1.4 | 1.8 |
| tess best_int matched, PSM 13 (raw line), compress | 1.4 | 12.7 | 11.6 | 99.3 / 96.7 | 1.2 | 1.2 | 2.0 | 1.2 | 1.6 |
| tess fast matched, PSM 7, compress | 1.5 | 12.2 | 12.6 | 99.3 / 97.2 | 1.2 | 1.2 | 2.1 | 1.4 | 1.7 |
| tess best_int **eng only** (all languages), compress | 1.5 | 12.5 | 13.4 | 99.8 / 97.2 | 1.4 | 1.2 | 1.9 | 1.4 | 1.6 |
| tess fast **eng+deu+lat**, compress | 1.7 | **10.2** | **10.2** | 99.4 / 98.7 | 1.5 | 1.6 | 2.4 | 1.5 | 1.7 |
| tess best_int eng+deu+lat, compress | 2.3 | 10.7 | 10.6 | 99.3 / 97.9 | 2.0 | 2.1 | 2.7 | 2.2 | 2.3 |
| tess best_int matched, PSM 7, *no* compress | 1.7 | 16.2 | 19.5 | 99.3 / 96.4 | 1.4 | 1.3 | 2.3 | 1.5 | 1.9 |
| Paddle en_v5 | 1.8 | 11.9 | 12.1 | 99.3 / 99.0 | 1.4 | 1.8 | 1.3 | 2.4 | 2.2 |

Per language (CER / SylER / WER %; remember the SylER floors of 3.2 / 4.4 / 10.0):

| config | eng | deu | lat |
|---|---|---|---|
| Paddle latin_v5 | 1.0 / 11.0 / 10.4 | 2.3 / 12.7 / 12.1 | **0.8** / 12.4 / **7.9** |
| tess best_int matched, compress | 1.1 / 8.5 / 7.2 | **1.1 / 7.8 / 6.3** | 2.4 / 16.9 / 13.1 |
| tess fast eng+deu+lat, compress | 2.2 / 8.4 / 7.2 | 1.9 / 8.9 / 6.8 | 1.0 / 12.8 / 6.2 |
| tess best_int eng only, compress | 1.1 / 8.5 / 7.2 | 2.5 / 12.1 / 12.6 | 1.1 / 16.6 / 12.7 |

Observations:
* The Tesseract **`lat` model is the weak spot**: on Latin text it does worse than `eng` (oracle CER 5.3 % vs 3.4 %), and it turns short syllables like "ti" into "ü".
* The German `deu` model is best on German, because of the umlauts.
* Paddle latin is uniformly good and needs no language decision. Its weakest case is German (ß/umlauts, 2.3 %).

### 5b. Oracle crops: GT box + padding, no masking (`results/table_oracle.md`)

These isolate the recogniser from the detector. Stems and notes are still in the crop, so CER is higher than end-to-end. Each row covers 1,920 strips.

| config | CER % | SylER % | WER % | hyphen P/R % | clean / scan / bilevel / copy / phone CER % |
|---|---|---|---|---|---|
| Paddle latin_v5, crop masked to GT bbox ("clean") | **1.3** | 14.1 | 12.7 | 99.8 / 99.4 | 0.6 / 1.2 / 1.2 / 2.5 / 0.9 |
| Paddle latin_v5, crop rescaled to 40 px font | 1.9 | 13.1 | 10.4 | 99.7 / 98.8 | 0.6 / 1.8 / 1.5 / 3.4 / 2.0 |
| tess fast matched, compress | 2.1 | 13.4 | 13.2 | 98.6 / 94.7 | 1.3 / 2.3 / 2.8 / 2.2 / 2.1 |
| tess best_int matched, compress | 2.2 | 12.5 | 11.6 | 99.1 / 94.5 | 1.2 / 2.4 / 2.7 / 2.3 / 2.2 |
| tess best_int matched, PSM 7, rescaled to 40 px font (no compress) | 3.2 | 16.6 | 18.3 | 98.4 / 92.9 | 1.6 / 4.0 / 3.1 / 4.0 / 3.3 |
| … same, raw resolution (no rescale) | 3.1 | 17.0 | 18.4 | 98.4 / 92.9 | |
| … same, rescaled to 30 px / 56 px font | 3.0 / 3.6 | 16.5 / 16.6 | | | |
| … same, dictionaries disabled (`load_system_dawg=0`, `load_freq_dawg=0` at init) | 3.2 | 16.6 | 18.3 | identical output | |
| tess fast matched, rescaled to 40 px font (no compress) | 3.2 | 18.2 | 21.1 | 97.6 / 93.1 | |
| tess best_int, **PSM 6** (block) | **15.9** | 33.6 | 42.7 | | 3.3 / 22.0 / 10.1 / 20.3 / 23.8 |
| Paddle latin_v5 **on gap-compressed strips** | 11.0 | 28.2 | 27.9 | | 1.1 / 14.8 / 4.3 / 17.3 / 17.7 |

What matters:

* **Gap compression (Tesseract only).**
  * What it does: inside the text band, every all-white column run wider than 0.5 × font size is shrunk to 0.5 × font size, which turns "Glo    -    ri    -    a" back into normally spaced text. An x-map is kept so that word boxes can be mapped back to page x.
  * Effect: CER 3.2 → 2.2 % on oracle crops, and **WER 19.5 → 11.5 %, SylER 16.2 → 11.5 %** end-to-end. Without it, Tesseract's word segmentation and LSTM context suffer from widely spread syllables.
  * Do not use it for Paddle: its CTC head emits one frame per 8 input px, so dense text gets fewer than 1.5 frames per glyph and characters are dropped.
* **Masking** (keeping only the text components) is the biggest single win for both engines. Strips from the detector beat oracle crops: Paddle 1.3 % vs 1.9 %, Tesseract 1.5 % vs 2.2 %.
* **Rescaling**: normalising to a font size of about 40 px (cap height about 28 px) is right for Tesseract. Pure upscaling of 150 dpi input made little difference, because Tesseract rescales internally.
* Typeface sensitivity (oracle CER for Paddle latin, norm): 0.2–1.6 % for most faces. Outliers are **C059 (6.6 %) and Liberation Serif (8.0 %)**, both fixed by masking (4.7 % / 2.6 %). Tesseract with compress: 0.8–3.4 % across faces.

### 5c. Hyphens, extenders, melismas, verses

* **Hyphens**:
  * Both engines read printed lyric hyphens reliably. Paddle gets P 99.8 / R 99.3. Tesseract with compress gets P 99.7 / R 96.9; it sometimes glues a tight hyphen into a word ("dark-ness", which is still correct) or reads it as "—" or "-.".
  * The geometric detector (P 96.6 / R 97.8) adds **x positions** for each hyphen. It did not improve OCR hyphen recall when fused naively, but it gives an independent check and handles hyphens at line start and line end. LilyPond repeats the hyphen at the start of the next system: 18 cases.
* **Unprinted hyphens** (8.6 % of logical hyphens, about 3 % of all syllable boundaries) are invisible to any OCR. They cause the SylER floor of 6.1 % (Latin 10 %).
  * Recovering them needs note alignment: a lyric token spanning two noteheads that have no slur, tie or extender between them must be split.
  * Hyphenation patterns (Liang/TeX patterns for en/de/la) then choose the split point. This belongs in the OMR lyric-attachment stage, not in OCR.
* **Extenders / melismas**:
  * OCR output for extenders is inconsistent: Paddle sometimes emits `_`, Tesseract `—` or `___`. The post-filter maps them to spaces.
  * Use the geometric extender list instead (R 81 %, P 63 %) together with OMR slurs and ties to mark melismas, i.e. `<extend/>` on the syllable.
  * Many melismas have no extender at all (word-internal melismas only show as a hyphen spanning several notes).
* **Verses**: each verse is its own strip, ordered top to bottom inside a band, so verse number = line index in the band. LilyPond-style stanza labels ("1.", bold) come out as a leading `1.` token (Tesseract occasionally reads "L"). Strip `^\d+\.` and use it to confirm the verse index.
* **Language**: unknown at input. Options:
  * Paddle latin needs none.
  * With Tesseract, either load `eng+deu+lat` (best SylER/WER, about 1.8× the time), or OCR the first strips with `eng` and switch to `deu` or `lat` from a cheap detector. Signals: ä/ö/ü/ß plus German function words; -us/-um/-ae/-is endings plus Latin function words (et, in, de, cum).

## 6. Speed

Node 24.11.1 on a Neoverse-V2 (aarch64) host, **shared and heavily loaded (load average 280–550 on 192 cores)**, so absolute numbers are pessimistic. Single-threaded, sequential, 40 strips (`results/bench_node.json`):

| engine | init (load model) | ms / strip | ms / 1000 px of strip width | RSS |
|---|---|---|---|---|
| tess fast eng | 327 ms | **79** | 48 | 351 MB |
| tess best_int eng | 291 ms | 122 | 74 | 442 MB |
| tess fast eng+deu+lat | 394 ms | 144 | 88 | 544 MB |
| tess best_int eng+deu+lat | 666 ms | 223 | 135 | 528 MB |
| Paddle latin_v5, ORT 1 thread | 112 ms | 142 | 70 | 510 MB |
| Paddle latin_v5, ORT 4 threads | 72 ms | **45** | 22 | 500 MB |
| strip detection (`strips.js`) | — | 461 ms/page (300 dpi) · 79 ms/page (150 dpi) | | |

A page has about 7 lyric lines on average, so lyric OCR costs **about 0.6–1.6 s per page on one thread**. Detection adds 0.1–0.5 s. Both can run in a Web Worker.

**Browser check** (`spike/ocr/browser/index.html`): everything was self-hosted and loaded by relative URL, to mirror the artifact CSP. It ran with Playwright 1.56.1 headless on the same loaded host, over 40 strips.

* **Chromium 141** (3 runs):
  * tesseract.js best_int `eng`: init 0.3–0.8 s, **119–175 ms/strip**.
  * `eng+deu+lat`: init 0.6–2.1 s, 194–231 ms/strip.
  * Paddle latin_v5 on onnxruntime-web (wasm EP, 1 thread, `crossOriginIsolated=false`): init 0.7–1.3 s, **229–263 ms/strip**.
  * Accuracy on this 40-strip sample: tesseract `eng` 1.4 % CER, `eng+deu+lat` 1.9 %. Paddle scored 3.8 %, but only because the test strips are gap-compressed, which Paddle must not get (see 5b); the outputs are the same as in Node.
  * An earlier run exposed an Otsu bug in gap compression on all-0/255 (bilevel) images. It was fixed in `jobs.js`, and all compress results in this document come from the fixed code.
* **Firefox 142** (headless, Linux aarch64): it works, but tesseract ran at 1.4–3.5 s/strip and Paddle at 3.9 s/strip, 8–17× slower than Chromium on the same machine. This looks like a WASM-SIMD performance problem specific to this aarch64 build. **Re-measure on desktop x86 Firefox and Safari before deciding**: Safari has no relaxed-SIMD, so tesseract.js picks the simd-lstm core there.
* WebKit could not be launched here (missing system libraries).

## 7. Integration notes for the artifact

**tesseract.js (works under the artifact CSP model; verified in Chromium):**

```js
// <script src="assets/tesseract/tesseract.min.js"> (self-hosted; or cdnjs/jsdelivr tag for this file only)
const worker = await Tesseract.createWorker('eng+deu+lat', 1 /* OEM.LSTM_ONLY */, {
  workerPath: 'assets/tesseract/worker.min.js',      // own origin; resolved against window.location.href
  corePath:   'assets/tesseract/tesseract-core-simd-lstm.wasm.js', // pin ONE core file (3.9 MB; a path ending in .js is used as-is per getCore.js - the browser test used the directory form) - every
                                                     // browser with WASM SIMD (Chrome 91+, FF 89+, Safari 16.4+)
  langPath:   'assets/tessdata',                     // {lang}.traineddata.gz (best_int)
  workerBlobURL: false, cacheMethod: 'none', gzip: true,
});
await worker.setParameters({ tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
const { data } = await worker.recognize(canvasOrImageData, {}, { text: true, blocks: true }); // word bboxes
```

* If `corePath` is a directory, tesseract.js picks between `relaxedsimd-lstm`, `simd-lstm` and `lstm`. Ship all three (11.7 MB) only if pre-SIMD browsers matter.
* `cacheMethod:'none'` avoids IndexedDB, which may be unavailable or throw in the sandbox.
* tesseract.js resolves relative paths with `new URL(p, window.location.href)`. If the page is ever served from `about:srcdoc`, pass absolute URLs built from `document.baseURI`.

**onnxruntime-web + Paddle (verified in Chromium):**

```js
// <script src="https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.1/dist/ort.wasm.min.js"> or self-host (53,796 B)
ort.env.wasm.wasmPaths = new URL('assets/ort/', document.baseURI).href; // MUST be absolute: the .mjs is loaded by
ort.env.wasm.numThreads = 1;               // dynamic import(); a bare 'assets/ort/' fails ("Failed to resolve module
                                           // specifier"). Threads need crossOriginIsolated, which is not available.
const sess = await ort.InferenceSession.create('assets/paddle/latin_v5.onnx', { executionProviders: ['wasm'] });
// input: float32 [1,3,48,W] (W = ceil(48*w/h / 8)*8, right-pad white), (v/255-0.5)/0.5, gray replicated to 3 ch
// output [1, W/8, 838]: greedy CTC, index 0 = blank, 1..836 = inference.yml character_dict, 837 = space
```

Self-host `ort-wasm-simd-threaded.wasm` (14,848,852 B) and `.mjs` (24,738 B) in `assets/ort/`. Ship the dictionary as a small JSON file extracted from `inference.yml`; see `models/paddle/latin_v5/dict.json`. CTC frame index × 8 / scale gives each character's x, which is enough to place syllables under notes.

**Budget:**

| option | files | total |
|---|---|---|
| A (tesseract) | core 3.90 MB + js 0.17 MB + `best_int` eng/deu/lat 6.03 MB | **≈ 10.1 MB** (with `fast` traineddata: 4.57 MB → ≈ 8.6 MB) |
| B (Paddle) | ORT wasm 14.85 MB + .mjs/.js 0.08 MB + model 8.04 MB | **≈ 23 MB**, of which only **8 MB is incremental** if ORT is already shipped for the OMR models |

Both fit under the 64 MB total and the per-file limits.

**Pipeline per page:**
1. Grayscale page (pdf.js render or decode).
2. `detectLyricLines(page)`.
3. For each line: masked strip → scale to font ≈ 40 px. For Tesseract, apply `compressGaps` and keep `xmap`. Then OCR.
4. Tokens with x positions → split into syllables on spaces and hyphens. Hyphen flags come from OCR and are confirmed by geometry; extender spans come from geometry.
5. Hand over to the OMR lyric-attachment stage: nearest notehead x per syllable, verse = line order in the band, staff above = voice candidates; split tokens that span several notes (unprinted hyphens).

## 8. Answers to the spike questions

| question | answer |
|---|---|
| Character / word accuracy | e2e CER **1.3 %** (Paddle) / **1.5 %** (tess best_int + compress). WER 10–12 %, SylER 10–12 % (floor 6.1 % from unprinted hyphens). Clean 300 dpi: 1.1–1.3 % CER; worst variant: bilevel for Tesseract (2.0 %), photocopy for Paddle (1.9 %). |
| Hyphen detection | OCR: P 99.7–99.8 % / R 96.9–99.3 %. Geometry: P 96.6 % / R 97.8 % with x positions. Extenders via geometry only: R 81 %. |
| Speed | 79–223 ms per strip (Tesseract, depending on model and languages); 142 ms on 1 thread / 45 ms on 4 threads (Paddle) in Node; 120–260 ms per strip in Chromium. About 1 s per page of lyrics. |
| fast vs best sizes | `fast` ≈ `best_int` on CER (1.5 vs 1.5 % e2e; 2.1 vs 2.2 % oracle), slightly worse WER (12.6 vs 11.5 %), 35 % faster. `fast` is also smaller once gzipped: eng 1.98 vs 2.95 MB, deu 0.85 vs 1.33 MB, lat 1.74 vs 1.74 MB. Float `best` (eng 15.4 MB) does not run in tesseract.js 7. |
| Isolating lyric strips | Staff detection plus inter-staff bands, with connected components that do not touch the staff, baseline clustering and a speck filter: 100 % recall / 99.2 % precision across all degradations (section 3). |
| Recommendation | Paddle latin_v5 on ORT-web if ORT is in the bundle; otherwise tesseract.js 7 best_int with gap compression. Run OCR on masked per-line strips from `strips.js` in both cases. |

## 9. Risks and follow-ups

1. **Real scans.** Add 10–20 real IMSLP/CPDL hymnal pages with hand-typed lyric ground truth to the harness. Expect a higher CER than on this synthetic data: old typefaces, broken glyphs, bleed-through.
2. **Fraktur** (pre-1940 German hymnals): evaluate `deu_latf` (fast 6.4 MB) against Paddle latin, which has no Fraktur training.
3. **Firefox and Safari performance** must be re-measured on real desktop and iOS hardware (section 6).
4. **Unprinted hyphens**: implement note-aligned token splitting with hyphenation patterns. Check that the pattern licences are compatible with distribution; TeX hyph-utf8 patterns are mostly LPPL/MIT-style.
5. **Lyrics touching music, chord symbols and dynamics in the lyric band**: extend the component classifier, for example with a tiny CNN text/non-text classifier if needed.
6. Detection runs at 0.46 s/page at 300 dpi in Node. Binarisation and the skew search dominate, and both can share work with the OMR staff detection.

## Reproduce

```bash
cd spike/ocr
npm ci                                   # tesseract.js 7.0.0, tesseract.js-core 7.0.0, onnxruntime-node/web 1.31.1, pngjs 7.0.0
python3 -m venv .venv && .venv/bin/pip install pdfplumber==0.11.4 numpy pillow opencv-python-headless pyyaml
# models: see URLs in section 4 -> models/tessdata/{fast,best_int,best}/, models/paddle/{latin_v5,en_v5}/ (+ dict.json from inference.yml)
.venv/bin/python gen/make_ly.py data/ly 56 && ./gen/render_all.sh          # LilyPond -> 300 dpi PNG + GT -> 4 degradations
node src/grid.js tess1 176 16                                              # oracle-crop Tesseract grid
node src/grid.js results/raw/ora2.json 120 16                              # oracle-crop compress / Paddle grid
node src/grid.js results/raw/e2e3.json 150 16                              # end-to-end (strips.js + OCR)
node src/score.js > results/summary_oracle.json && node src/table.js results/summary_oracle.json
node src/score_e2e.js e2e_ > results/summary_e2e.json && node src/table_e2e.js results/summary_e2e.json
node src/bench.js 8 > results/bench_node.json                              # timing
(cd browser && python3 -m http.server 8765)   # then open http://127.0.0.1:8765/?n=40&tests=eng,combined,paddle
```

## Files

* `spike/ocr/src/strips.js`: lyric strip isolation (environment-agnostic; candidate for the real core).
* `spike/ocr/src/img.js`: gray bitmap helpers (crop, resize, Otsu, adaptive binarise, connected components).
* `spike/ocr/src/jobs.js`: oracle crops, `compressGaps` (gap compression with x-map).
* `spike/ocr/src/engines.js`: tesseract.js and Paddle-ONNX adapters (CTC decode with x positions).
* `spike/ocr/src/metrics.js`, `score.js`, `score_e2e.js`, `table*.js`: metrics and reports.
* `spike/ocr/src/tess_eval.js`, `paddle_eval.js`, `e2e_eval.js`, `grid.js`, `bench.js`: runners.
* `spike/ocr/gen/*`: test-data generation (LilyPond → PDF → GT → degradations).
* `spike/ocr/browser/index.html` + `assets/`: self-hosted browser check.
* `spike/ocr/results/`: `summary_oracle.json`, `summary_e2e.json`, `summary_det.json`, `table_oracle.md`, `table_e2e.md`, `bench_node.json`, `browser_chromium141.json`, `browser_firefox142_subset.json`, `samples/*.png`.
