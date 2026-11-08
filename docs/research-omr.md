# OMR of scanned sheet music → MusicXML: research notes (Nov 2026)

Scope: what current (2023–2026) work says about turning **scanned/image** sheet-music PDFs into MusicXML 4.0,
with particular attention to (a) lyrics, (b) splitting multi-voice staves (closed-score SATB) into separate parts,
and (c) running everything **client-side in a claude.ai Artifact** (CSP: no CDN fetch/WASM/worker loads; each
binary asset ≤ 15 MB, total ≤ 64 MB). Every number below is sourced; numbers the source reports about itself
(not independently reproduced) are marked *self-reported*. Sizes and versions were checked directly against
npm / GitHub / Hugging Face APIs on 2026-11-08.

---

## 0. TL;DR

* **No off-the-shelf system does what we need.** None of the open systems outputs lyrics *and* voice-separated
  parts. Audiveris reads lyrics but is AGPL Java. homr is AGPL. copisteria (Apache-2.0, Oct 2026) explicitly says
  "Lyrics are not written". LEGATO swaps all text for a `<|text|>` token. SMT/SMT++ and Zeus/OLiMPiC were trained on
  piano and quartet music and output `**kern`/LMX with no lyrics. **Lyrics and SATB part-splitting have to be built
  by us.**
* **Recommended core: a deterministic classical pipeline in plain JS**, with optional small ONNX models where they
  help: Sauvola binarisation using integral images → run-length staff metrics → staff detection from projections
  per strip with line tracking → run-length staff removal → connected components → notehead template/classifier →
  stem, beam, flag and dot assembly → time-slot rhythm solver with measure repair → voice and part separation →
  lyric OCR (tesseract.js) and syllable alignment → MusicXML writer. The same code runs in node, so the accuracy
  harness can use it.
* **Best ML candidate for later (licence-clean and small):** `kobimusic/copista-2m`. Its symbol detector has 1.94M
  params (7.8 MB fp32 .pt) and its "evidence" transformer has 2.03M params (8.15 MB). Both code and weights are
  Apache-2.0 and the training data is PDMX (CC BY 4.0). The detector predicts **stem direction (`up/down/both`)
  and a `voice_slot` for each notehead**, which is exactly the signal SATB splitting needs. The project is new
  (Oct 2026, ~18 stars) and its benchmark numbers are *self-reported*: on scans it claims OMR-NED of 11.2 % on
  string quartets and 17.8 % on Lieder, against homr 42.3 % and Legato 58.2 %. It ships as PyTorch, so an ONNX
  export spike is needed.
* **Licence flags.** The following are AGPL-3.0 or GPL: **Audiveris, homr (code and weights), and the Ultralytics
  YOLOv8/YOLO11 code and weights.** YOLOv7 and YOLOv9 are GPL-3.0. **LEGATO** code and weights are MIT, but it runs
  on a frozen **Llama-3.2-11B-Vision** encoder (Llama Community Licence, not OSI). **homr transformer weights were
  trained partly on Camera-PrIMuS** (its HF mirror says CC BY-NC). **MUSCIMA++ is CC BY-NC-SA.** **Verovio is
  LGPL-3.0**, so we prefer OSMD (BSD-3).
* **Browser runtime facts:**
  * onnxruntime-web 1.30.0 (on cdnjs) ships `ort-wasm-simd-threaded.wasm` at **14.24 MB**, just under the 15 MB
    cap. The WebGPU/JSEP binary is **28.3 MB**, so it cannot be one file. That makes **WASM CPU, single-threaded**
    the realistic EP, because threads need `crossOriginIsolated`.
  * gzip cuts ORT wasm to about 26 % (11.2 MB → 2.87 MB gz, 1.80 MB brotli, measured on 1.22). The bytes can be
    passed in with `ort.env.wasm.wasmBinary` after `DecompressionStream`.
  * tesseract.js 7.0.0 (Apache-2.0, on cdnjs) needs core `*-lstm.wasm.js` files of about 3.9 MB each.
    `tessdata_fast` traineddata sizes: eng 4.11 MB, lat 3.19 MB, deu 1.53 MB. `tessdata_best` eng is 15.4 MB, which
    is over the cap.
* **Metrics:**
  * **OMR-NED** = (I+D)/(N_pred+N_ref) over visual symbols (musicdiff-based; ISMIR 2025). This is now the common
    cross-system metric.
  * **TEDn** is tree edit distance on MusicXML (Hajič 2016; Mayer 2024).
  * **SER/CER/LER** are edit rates on tokens.
  * **MV2H** scores multi-pitch, voice, meter, value and harmony (McLeod 2018). Its *voice* sub-score directly
    measures our part-splitting.

---

## 1. Problem framing for this project

* The input is page **images** (scans and photocopies at 150–600 dpi, from IMSLP/CPDL/Internet Archive or phone
  scans). Born-digital PDFs are only rasterised. The core takes `{width,height,data:Uint8ClampedArray}` grayscale.
* The target repertoire is **hymn/chorale closed score**: two staves per system with a brace, S+A on the treble
  staff and T+B on the bass staff. Lyrics sit between the staves, often 2–6 numbered verses. Notation is mostly
  homorhythmic and simple: quarters, halves, dotted values, eighth pairs, fermatas, and pickup measures.
  Secondary: open-score SATB (one voice per staff, lyrics under each staff), melody plus piano, and piano.
* Output: MusicXML 4.0 `score-partwise`.
  * A closed-score staff with two consistent stem-direction voices becomes **two `<part>`s** (S/A, T/B).
  * A piano grand staff stays **one part with two staves** (`<staves>2</staves>`), with voices kept as `<voice>` and
    `<backup>`.
  * Lyrics are copied to every vocal part that sings them.

---

## 2. Classical (rule-based) pipeline: stage by stage

Classical OMR is still the backbone of Audiveris (5.11.0, Jul 2026) and of the front ends of oemer, homr and
copisteria. Even copisteria, the strongest recent open system, decides **staves, systems and bars with
hand-written geometry rules over the ink** and uses ML only for symbols and musical context
([copisteria ARCHITECTURE.md](https://github.com/kobimusic/copisteria)).

### 2.1 Ingest and resolution normalisation
* **Node:** `pdfimages -list` / `pdfimages -png` extract the embedded scan at native resolution (no resampling).
  `pdftoppm -r 300 -gray` rasterises born-digital pages.
* **Browser:** pdf.js 3.11.174 `page.render()` to a canvas. Scale so the page is about 300 dpi, or better, scale by
  measured staff space (below). For scanned PDFs the image XObject's native size is the right render scale.
* **Normalise by staff space, not dpi.** Measure the staff-space height `s` (distance between line centres), then
  rescale so `s` is fixed. Learned detectors need this. copisteria rescales the page so the staff space is
  **10.6 px**, cross-checked against a first pass at 2048 px. Classical rules then work in staff-space units.
  Rule-based steps do better around `s` = 16–24 px, which is typical of 300 dpi hymnals.

### 2.2 Grayscale and binarisation
* **Otsu** (global, histogram-based) is fine for clean photocopies. It fails on uneven lighting, phone shadows and
  yellowed paper.
* **Sauvola**: `T(x,y) = m·(1 + k·(σ/R − 1))` with R = 128 and k ≈ 0.2–0.4. Window ≈ 2–4 staff spaces (about 31–61
  px at 300 dpi). Compute it in O(1) per pixel with integral images of I and I²
  (Shafait, Keysers & Breuel 2008, "Efficient implementation of local adaptive thresholding techniques using
  integral images"). Use it as the default for scans. A cheap safeguard: run Otsu as well and keep the result with
  the more plausible staff-line run-length histogram.
* **Shading normalisation first** (divide by a large-kernel blur or a morphological closing of the background).
  copisteria runs its line finder on the original and on a "paper's shading divided out" copy, then keeps whichever
  the detector confirms.
* **Learned binarisation:** selectional auto-encoders (Calvo-Zaragoza & Gallego, *Pattern Recognition* 86, 2019;
  Castellanos et al., ISMIR 2018 for music documents) beat Sauvola on degraded manuscripts. They are not needed for
  printed hymnals.
* Keep **both** the gray and the binary image. Learned models and template matching work better on gray. Run-length
  analysis needs binary.

### 2.3 Deskew and dewarp
* **Global skew:** maximise the variance (sharpness) of the horizontal projection profile over angles in ±5°.
  Search coarsely, then refine to 0.05°. Alternatively, run a Hough transform on long horizontal black runs. Staff
  lines dominate the profile, which makes this very reliable for music.
* **Local curvature** (book gutter, phone photos): handle per staff by tracking lines in vertical strips (2.5) and
  fitting a polyline or spline per line. Do not warp the image; map coordinates through the per-staff line model.
  oemer and homr dewarp the whole image before recognition, and the oemer README notes that deskewing itself
  causes errors and offers `--without-deskew`.

### 2.4 Staff metrics (line thickness `t`, space `s`)
* Classic Fujinaga method: the **most frequent vertical black run** gives line thickness `t` (typically 2–4 px at
  300 dpi). The **most frequent white run** gives the space between lines.
* More robust (Cardoso & Rebelo, ICPR 2010, "Robust staffline thickness and distance estimation in binary and
  gray-level music scores"): take the **most common sum of a black run and the next white run**. That gives
  `t+s` reliably; then split it with a 2D histogram.
* Every later threshold is expressed in `s` and `t`. Examples: notehead height ≈ 1 s; stem length ≈ 3.5 s; a beam is
  about 0.5 s thick; staff removal deletes vertical runs ≤ ~1.5–2 t.

### 2.5 Staff and system detection
* **Projection per strip:** split the page into about 8–16 vertical strips. In each strip, find peaks of the
  horizontal black projection. Group peaks into **5 equally spaced lines** (spacing ≈ t+s, tolerance ±20 %). Link
  the groups across strips into staves, which tolerates skew and curvature.
* **Line tracking / stable paths:** Cardoso et al. (*IEEE TPAMI* 31(6), 2009, open access, CC BY) model staff lines
  as stable shortest paths across the page, which copes with curvature, breaks and slant. Capela et al. (SIGMAP
  2008) add removal on top of the same paths. This is a good fallback for warped scans.
* **Systems:** two adjacent staves belong to one system if a brace, a bracket or a vertical ink run joins them at
  the left edge, or if their **barlines continue through the gap**. copisteria uses both cues, plus a small
  logistic model. Hymnals put a brace on S/A + T/B. The gap between staves is large because it holds the lyrics.
* Output per staff: five line polylines, `s`, `t`, x-extent, and a system id.

### 2.6 Staff removal
* **Run-length filter:** along each detected line, delete black pixels whose vertical run is ≤ ~1.5–2 t and
  centred on the line. Keep pixels where a longer run passes through, because those belong to symbols. This is
  the "line track height" family in Dalitz, Droettboom, Pranzas & Fujinaga, "A Comparative Study of Staff Removal
  Algorithms", *IEEE TPAMI* 30(5), 2008. That paper also compares skeleton-based and vector-field methods.
  Audiveris 5.11 added "smarter staff line removal in case of crossing curves".
* **Keep the un-removed image** for notehead matching. Removal fragments hollow heads and whole notes, so template
  matching on the original gray image is more reliable for heads.
* Removal is less important if a learned detector is used. copisteria and homr segment symbols directly.

### 2.7 Connected components and segmentation
* Use two-pass union-find, 8-connectivity, on the staff-removed binary image. Compute bbox, area, centroid,
  black-pixel density, and moments in staff-space units.
* Use an **inverted** CC pass to find enclosed white holes (hollow heads, whole notes, flats, natural/sharp
  bodies).
* Treat oversized CCs (beamed groups, chords with a shared stem, and barlines touching heads) as "compound". Split
  them by removing stems (vertical runs ≥ 2.5 s with width ≤ ~0.3 s) and beams (thick near-horizontal runs ≥ 0.4 s
  tall), then re-labelling.
* **Text CCs** (lyrics, titles, verse numbers) are found as rows of small CCs with x-height ~0.6–1.2 s on a common
  baseline, **outside** the staff band (between staves / below staff). Mask them out of music recognition and send
  them to OCR (§6).

### 2.8 Symbol classification
Options, from cheapest to most capable:
1. **Template matching** with normalised cross-correlation on gray at the normalised `s`.
   * Use it for filled, hollow and whole noteheads, clefs (G, F, C), accidentals (♯ ♭ ♮), rests and digits. Render
     templates from an open SMuFL font: **Bravura** and **Leland** are SIL OFL-1.1, so templates or synthetic data
     derived from them can be shipped.
   * Restrict head search to staff positions: y = line or space, which gives 1/2-s quantisation.
   * Hymnals are engraved in a small number of house styles, so templates do well there. Keep 2–3 template variants
     per class.
2. **Hand-crafted features + kNN/SVM.** oemer classifies clefs, accidentals and rests with **three SVMs** trained
   on DeepScores-extended. Audiveris uses its own glyph classifier, and 5.11 added L2 regularisation to it.
   * Features: 16×16 or 20×20 zoned density, aspect ratio, area/s², hole count, and Hu moments.
   * Easy to do in pure JS; small enough to inline as JSON weights.
3. **Small CNN classifier on CC crops** (e.g., 32×32, 50–200k params, int8 ONNX ≈ 0.1 MB). Train it on crops
   rendered by LilyPond/Verovio from synthetic hymns with scan degradation, plus DeepScoresV2 crops (CC BY 4.0).
4. **Full-page detector** (YOLO/DETR family) on DeepScoresV2 or synthetic pages. Copisteria's detectors predict 270
   classes, with staff-position, stem-direction, dots, grace and voice attributes on every note and rest.
   * DeepScoresV2 notes: orthogonal boxes suit long, thin, possibly rotated objects badly (Tuggener et al., ICPR
     2020). Most papers use its **dense subset (1,714 images)**.
   * **Licence trap:** Ultralytics YOLOv8/YOLO11 code and trained weights are AGPL-3.0. Use Apache-2.0
     detectors: YOLOX, RT-DETR/RT-DETRv2, D-FINE, or RF-DETR base sizes (RF-DETR XL/2XL use a non-OSI licence).

### 2.9 Notation assembly
* **Stems:** vertical runs ≥ ~2.5 s, attached to a head at its right edge (stem up) or left edge (stem down). A head
  with stems on **both** sides, or one head carrying an up stem and a down stem, is a **unison of two voices**.
  copisteria's detector has an explicit `stem_dir = both` value: "one head, a stem each way (two voices)".
* **Beams:** thick slanted bands between stem ends. The number of beam lines crossing a stem gives the beam level:
  1 = eighth, 2 = sixteenth. **Flags** are separate CCs attached to the stem end.
* **Augmentation dots:** a small round CC about 0.5–1 s to the right of the head, in a **space** (a dot is lifted
  into the space above when the head is on a line). Distinguish them from staccato dots, which sit above or below
  the head on the stem-free side.
* **Accidentals:** left of a head at the same y (a flat is anchored at its bowl). They hold until the barline at
  that step and octave. **Key signature:** accidentals right after the clef at the start of each staff.
* **Ties vs slurs:** a curve between two heads of the same pitch is a tie. homr's changelog: "Ties are recovered
  from slurs between notes of the same pitch."
* Formal model: the **Music Notation Graph (MuNG)** from MUSCIMA++ has primitives as nodes and syntactic relations
  as edges. Yang et al. 2024 ("Toward a More Complete OMR Solution", arXiv 2409.00316) train notation assembly
  on detector output (YOLOv8 on MUSCIMA++ v2.0) instead of perfect detections.

### 2.10 Rhythm reconstruction and measure-timing repair
This is where classical OMR usually breaks: one missed dot or beam desynchronises every voice after it.
Current practice:
* **Time-slot (onset column) model.** Notes in different voices and staves of a system that share an x-position
  share an onset. Audiveris builds time slots per measure. In homorhythmic hymns this constraint is very strong:
  one wrong duration in a voice contradicts the onsets of the other three.
* **Joint decoding per voice and measure.** Keep a short list of duration hypotheses per note: head type ×
  stem/beam/flag count × dot present? × tuplet. Pick the combination that (a) matches the measure length from the
  time signature, (b) places each note's onset at its x-column, and (c) maximises detector confidence.
  * copisteria does this as a **Viterbi search over 48ths of a quarter note**, with penalties for gaps, overlaps,
    two notes at one onset, and running past the barline. "One misread duration does not shift the rest of the
    bar."
  * For hymns, an exhaustive search over a few hypotheses per note is cheap (≤ ~16 notes per voice per measure).
* **Missed barlines:** if a voice holds ≥ 1.75 bars of duration, look for a full-height vertical stroke at the
  point where the running sum crosses a whole bar, insert a barline, and decode again (copisteria `revise.py`).
* **Missing time signature:** pick the bar length that most measures fit. Hymnals usually print it, but some
  chorales omit it. **Pickup and final measures:** allow the first measure to be short (`implicit="yes"`). In
  hymns, pickup + final measure ≈ one full measure.
* **Fallback when repair fails:** pad with invisible rests (`print-object="no"`) or a `<forward>` so every voice
  sums to the measure length, and **flag the measure** in the confidence report. Both oemer ("beat adjustment only
  adds beats") and copisteria do this.
* The classic triplet failure: unmarked triplets (marked once, pages earlier) get read as plain notes.
  copisteria writes 65 % of tuplet notes as tuplets when every mark is removed, against 96 % with marks.

### 2.11 Pitch
* Pitch = (clef, staff position of head relative to the line model) + key signature + accidentals in the measure,
  with ties carrying accidentals across barlines. Clef changes mid-staff apply from their x onward.
* Octave-treble ("tenor") clef G2-8vb is common for tenor parts in open score. Write it as
  `<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>`.

---

## 3. State-of-the-art systems (2023–2026)

### 3.1 Comparison table

| System (latest) | Approach | Code / weights licence | Weights (size) | Lyrics? | Voices→parts? | Browser feasibility |
|---|---|---|---|---|---|---|
| **Audiveris 5.11.0** (2026-07-11) | Classical + glyph classifier, Java | **AGPL-3.0** | n/a (bundled) | **Yes**: Tesseract; lyric lines; verse numbers filtered since 5.10 | Voices per staff, not split into parts | No (Java). Use only as an offline baseline in the harness |
| **oemer 0.1.8** (2024-11; last push 2025-04) | 2 UNets (staff/symbols; heads/clefs/stems) + SVMs + rules | **MIT** | `1st_model.onnx` **70.8 MB**, `2nd_model.onnx` **38.4 MB** (fp32) | No | Groups chords by stem direction; no part split | Possible only after int8/fp16 quantisation and chunking to ≤ 15 MB per file; single-thread WASM UNet on a full page is slow |
| **homr** (0.7 + unreleased; push 2026-11) | oemer-style segnet + Polyphonic-TrOMR-style transformer per staff | **AGPL-3.0 code *and* weights**; transformer data includes Camera-PrIMuS (HF mirror says CC BY-NC) | ONNX: segnet 53 MB (fp16 26.5), encoder 48 MB (fp16 24), decoder 37–47 MB | No (title OCR via RapidOCR) | "Multiple voices per staff" (unreleased) | Licence-blocked for permissive shipping |
| **copisteria 1.3.4 / copista** (Oct 2026) | Detector (270 classes + per-head attributes: staff pos, **stem dir incl. both**, dots, grace, **voice slot**) → geometric front end → 2.03M evidence transformer → Viterbi rhythm writer | **Apache-2.0 code and weights** (NOTICE file must be kept); trained on PDMX renders | copista-2m detector **7.8 MB** (.pt fp32) + evidence **8.15 MB**; copista-28m detector 115 MB | **No** ("Lyrics are not written"; text needs external OCR boxes) | Voice slots per note; parts = staves/braced pairs | **Most promising ML option** (about 4M params in total). Needs ONNX export of PyTorch; front end and writer would need porting to JS |
| **Polyphonic-TrOMR** (NetEase; push 2023-01) | Patch-embedding transformer, single staff | Apache-2.0 | `img2score_epoch47.pth` 86.3 MB | No | Polyphonic tokens | Stale; training code never released |
| **SMT** / **SMT++** (Ríos-Vila et al.; IJCV 2025) | CNN/ConvNeXt encoder + 8-layer transformer decoder → `**bekern`, full page | MIT code; MIT weights on HF | `PRAIG/smt-fp-grandstaff` 43.7 MB; `antoniorv6/smt-grandstaff` 85.5 MB | No | Piano spines | Autoregressive; piano-only training; weak on real scans (see LEGATO table) |
| **Zeus / OLiMPiC** (Mayer et al., ICDAR 2024) | ResNet-ish CNN + 2×BiLSTM + attention LSTM decoder → Linearised MusicXML (LMX), per system | MIT code; data CC BY-SA | not checked | No | Piano voices (LMX encodes voice/staff changes) | Small RNN; per-system; piano-only |
| **LEGATO** (ICLR 2026) | Frozen **Llama-3.2-11B-Vision encoder (836M)** + 101M decoder → ABC, multi-page | MIT code and weights, but the **encoder is under the Llama 3.2 Community Licence** | legato decoder 429.5 MB; legato-small 43.7 MB (plus encoder) | **Text replaced by `<|text|>`** | ABC voices | Not feasible in a browser |
| **LEGATO 2** (arXiv 2607.05769, Jul 2026) | System-level segmentation + autoregressive VLM; embeds text (titles, annotations) | not released | not released | Embedded text claimed | n/a | n/a |
| **Transcoda** (arXiv 2605.10835, May 2026) | 59M-param model; synthetic data + normalised `**kern` + grammar-constrained decoding | release promised "upon publication" | n/a | No | kern spines | n/a |
| **Bottleneck-ResNet + BiGRU + CTC** (arXiv 2604.16446, Apr 2026) | Monophonic CRNN-CTC | no code | n/a | No | Monophonic | Illustrates small CTC models for monophonic staves |

### 3.2 Reported accuracy (all lower = better)

**LEGATO, Table 1 (TEDn / OMR-NED, %)**. Source: [arXiv 2506.19065](https://arxiv.org/abs/2506.19065).

| Test set | GPT-5 | SMT++ | Legato | Legato-small |
|---|---|---|---|---|
| Camera OpenScore String Quartets (252 pp.) | 90.5 / 97.6 | 98.6 / 94.7 | **60.4 / 58.2** | 84.1 / 93.5 |
| Camera OpenScore Lieder (64 pp.) | 91.6 / 97.6 | 98.4 / 84.1 | **36.4 / 44.9** | 82.6 / 83.5 |
| IMSLP piano scans (32 pp.) | 96.7 / 98.7 | 97.7 / 91.9 | **29.7 / 44.3** | 76.9 / 86.7 |

The takeaways: frontier VLMs (GPT-5) are useless as OMR today (~97 % OMR-NED), and SMT++ collapses on real scans.

**copisteria README / model card (OMR-NED via efficient-musicdiff, %, *self-reported*, scans)**:

| | Quartet scans (252) | Lieder scans (55) | Polish piano scans (112) |
|---|---|---|---|
| copista-28m | 8.6–8.7 | 16.9–17.7 | 31.5–34.4 |
| copista-2m | 11.1–11.2 | 17.0–17.8 | 34.3–38.7 |
| Legato 2 (paper) | 31.6 | n/a | n/a |
| Legato | 58.2 | n/a | n/a |
| homr 0.7 | piano only | 42.3 | 48.3 |
| Audiveris 5.11 | 66.9 (no output on 54/252) | 51.8 | 62.6 |
| Transcoda | piano only | 48.4 | 55.1 |

The ranges are the README vs model-card numbers. Both are from the same authors.

**Other reference points**
* **SMT++ (FP-GrandStaff, bekern):** CER 5.6, SER 6.9, LER 12.9 (ConvNeXt encoder). Synthetic full pages only.
* **Zeus:**
  * GrandStaff SER 2.77 / Camera-GrandStaff 3.03.
  * OLiMPiC **scanned**: TEDn 44.41 without augmentation, **18.40 with augmentation**. Augmentation is what makes
    real scans work.
* **Transcoda:** OMR-NED 63.97 % on 112 historical Polish scans, against SMT++ 80.16 % and Legato 86.73 %. On its
  synthetic benchmark it scores 18.46 %.
* **Sheet Music Benchmark (SMB, ISMIR 2025):** an SMT baseline at region level reaches OMR-NED 57.4 % on pianoform
  and 94.1 % on monophony. The scanned KernScores pages are hard.
* **Camera-PrIMuS** (monophonic incipits): the 2026 CRNN-CTC reports symbol error 0.45 % and sequence error
  7.52 %. Monophonic incipits are close to solved.

### 3.3 What to take from each system
* **Audiveris:** the lyric model.
  * A lyric line is a *sentence* with role `Lyrics`, made of syllables, each linked to a chord above or below.
  * The handbook warns that it is "not always clear which voice is concerned (if there is more than one voice per
    staff)".
  * Lyrics are assumed below the staff, with an option for above.
  * Since 5.10, verse numbers ("1.", "2.") are detected and filtered, and isolated punctuation is merged into the
    previous syllable.
  * Single-character syllables (vowels) are hard for Tesseract.
* **oemer:** the rule set for staff peaks, `unit_size`, chord grouping by stem direction, beam/flag counting in a
  region near each note group, and dot finding by subtraction. Watch out: its `unet_big` ONNX has **negative
  ConvTranspose pads that newer onnxruntime versions reject**, and the omr-mcp package rewrites them.
* **homr:**
  * Its benchmark design (Benchmark.md) tokenises kern and MusicXML into one vocabulary and reports NED for each
    field (rhythm, pitch, lift, articulation, slur), with alignments stored in SQLite. That is a good template for
    our harness.
  * Its changelog lists practical fixes: grand-staff pairing errors, staves joined across a book gutter, staves
    that hold only rests, and unnumbered triplets.
* **copisteria:**
  * A geometry-only front end, with **all musical decisions left to a model** that adds log-probability
    "evidence" to the detector's outputs.
  * Joint rhythm decoding for each voice.
  * Part planning on the fullest system (a braced pair is one part).
  * We would **override** that last rule: a braced pair *with lyrics between and two-voice stems* becomes **four
    parts**.

---

## 4. Datasets

| Dataset | Content | Size | Licence | Use for us |
|---|---|---|---|---|
| **DeepScoresV2** (Tuggener et al., ICPR 2020) | Rendered pages with boxes (oriented and orthogonal) and segmentation | 255,385 images, 151M instances, 135 classes; dense subset 1,714 | CC BY 4.0 (Zenodo 4012193) | Symbol detector / classifier training |
| **MUSCIMA++ v2** | Handwritten pages, MuNG graph | 140 pages, ~91k symbols (v0.9) | **CC BY-NC-SA 4.0** | Avoid for shipped weights |
| **PrIMuS / Camera-PrIMuS** (Calvo-Zaragoza & Rizo 2018) | Monophonic RISM incipits (Verovio renders, plus camera distortions) | 87,678 | Not stated at source; HF mirror CC BY-NC | Avoid for shipped weights |
| **GrandStaff** (Ríos-Vila et al., IJDAR 2023) | Single-system piano renders, `**kern` | 53,882 | MIT (HF copy) | Piano only |
| **FP-GrandStaff** | Full-page piano | 688 pages | (SMT++ repo, MIT) | Piano only |
| **OLiMPiC** (Mayer et al. 2024) | Lieder systems (voice + piano), synthetic train; **IMSLP scans** for dev/test | 17,945 systems; dev 1,438 / test 1,493 scanned | CC BY-SA | Real-scan evaluation including vocal staves |
| **OpenScore Lieder** | MusicXML of 19th-c. songs | ~1,356 scores | **CC0** | Ground-truth MusicXML for synthetic rendering |
| **PDMX** | MuseScore public-domain scores → MusicXML | ~250k | CC BY 4.0 (`no_license_conflict` subset) | copisteria and homr training data; synthetic pages |
| **Sheet Music Benchmark (SMB)** | KernScores scans, region + page, `**kern` | 685 pages, 4,039 regions | Gated HF (`PRAIG/SMB`) | External evaluation |
| **polish-scores** (`btrkeks/polish-scores`) | Historical Polish scans, kern + MusicXML | 112 pages | eval-only | External evaluation |
| **MusiCorpus** (arXiv 2605.18436, 2026) | Hand-annotated historical/handwritten pages, MusicXML at page and system level | 1,309 pages | CC BY-NC-SA (arXiv) | Manuscripts; not our target |
| **AMNLT** (Martinez-Sevilla et al., ICDAR 2023; arXiv 2412.04217) | **Aligned music + lyrics** (Gregorian chant) | 4 datasets | academic | Only lyric+music aligned benchmark family |
| **Smashcima** (OMR-Research) | Synthetic handwritten music generator | tool | Apache-2.0 | Not needed (we target print) |

**No public dataset covers closed-score SATB hymns with lyrics.** We should **synthesise one**:
1. Take public-domain hymns and chorales, from OpenScore (CC0), PDMX's PD subset, or our own LilyPond
   transcriptions of PD hymn tunes.
2. Render them with LilyPond 2.24. LilyPond is GPL as a tool, but its output is not encumbered. Engrave in closed
   and open score with 1–4 verses.
3. Degrade the renders: rotate ±2°, add page curl, Gaussian blur, salt-and-pepper noise, JPEG compression, and
   threshold artefacts at 150–300 dpi.
4. Add a few real PD hymnal scans (IMSLP / Internet Archive) that we transcribe ourselves.

---

## 5. Detecting multiple voices on one staff and splitting them into parts

### 5.1 What the literature and tools offer
* **OMR systems keep voices inside a staff.** Audiveris assigns voices per staff, oemer groups by stem direction
  ("opposing stem directions can indicate separate melodic lines"), and homr added "multiple voices per staff".
  copisteria predicts a `voice_slot` (1–8) for each head plus `stem_dir ∈ {up, down, both}`, and then makes
  **parts = staves or braced pairs**. **None of them promotes voices to separate `<part>`s.**
* **Symbolic voice separation:**
  * Foscarin, Karystinaios, Nakamura & Widmer, "Cluster and Separate: a GNN approach to voice and staff
    prediction for score engraving" (ISMIR 2024). It treats voice assignment as edge prediction and handles chords
    and cross-staff voices. Code and models are MIT (`CPJKU/piano_svsep`), but it is piano-oriented.
  * MV2H's voice dimension measures exactly this.
* **Notation tools:** splitting a closed SATB score is a manual "voices → parts" or "explode" step in MuseScore
  (MuseScore forum threads; MuseScore 3 "Explode", MuseScore 4 part-voice visibility). music21 can do the same
  offline for testing.

### 5.2 Recommended rule-based voice/part logic (hymn-specific, deterministic)
For each staff and measure, after rhythm decoding:
1. **Stem-direction voices.** Up stems → voice 1 (upper), down stems → voice 2 (lower).
   * A head with both stems, or with `both`, is a **unison** shared by both voices: copy it into both.
   * **Stemless whole notes:** two heads at one onset go upper → v1, lower → v2. A single whole note is shared.
     Heads a second apart are offset horizontally.
   * **Shared-stem chords:** older hymnals often print S and A on one stem when the rhythms match. Split a 2-note
     chord by pitch (top → v1, bottom → v2). A 3+-note chord means divisi or piano; flag it.
   * **Rests:** vertical position (above the middle line → v1, below → v2). One centred rest is shared by both.
2. **Rhythmic independence check.** Each voice must sum to the measure length on its own (§2.10). If the split
   voices don't balance and the unsplit chordal reading does, treat the staff as chordal (single voice).
3. **Staff classification: "closed-score vocal" vs "keyboard".** Score each braced pair; split only if the score
   is high:
   * **+** Lyrics text rows between the two staves, or under both.
   * **+** In ≥ 60–70 % of onsets, every staff has ≤ 2 heads per onset, with opposite stems when there are 2.
   * **+** Part labels found by OCR: `S`, `A`, `T`, `B`, `Soprano`, `Alto`, `Tenor`, `Bass`, `S.A.`, `T.B.`, `Choir`,
     `SATB`.
   * **+** Ranges: v1 above v2 on each staff. Treble-staff voices fit S (C4–A5) and A (G3–D5); bass-staff voices fit
     T (C3–G4) and B (E2–D4).
   * **−** Chords of 3+ heads, cross-staff beams, arpeggios, pedal marks, or `Piano`/`Organ`/`Pno.` labels.
   * **−** A second staff carrying a different, independent rhythm with no lyrics (accompaniment).
   * A choir + piano system (vocal staves + braced piano pair) gets these rules on the vocal staves only. The piano
     braced pair stays one part with 2 staves.
4. **Emit parts.**
   * Closed SATB → P1 Soprano (treble clef), P2 Alto (treble), P3 Tenor (bass clef as printed, or optionally
     treble-8vb), P4 Bass (bass).
   * A two-voice single staff → two parts (e.g., "Soprano I/II" for divisi).
   * Record provenance for the UI: `splitFrom: {system staff index, stem: 'up'|'down'}`.
   * When splitting is ambiguous (low score), keep **one part with `<voice>1/2` + `<backup>`** and warn.
5. **Consistency across systems.** Decide the part layout once per page or movement, on the fullest system (as
   copisteria does). Then map every system's staves onto it, so a system where the alto drops out still yields 4
   parts. The missing voice gets rests.

---

## 6. Lyrics OCR under and between staves

### 6.1 State of the art
* The research community rarely addresses lyrics.
  * **AMNLT** (Martinez-Sevilla, Ríos-Vila, Castellanos & Calvo-Zaragoza, ICDAR 2023; Fuentes-Martínez et al.,
    arXiv 2412.04217) transcribes music and text in one pass with an implicitly aligned encoding, but only for
    chant.
  * **OMMR4all / Hartelt, Eipert & Puppe** (*Applied Sciences* 14(16):7355, 2024) handle text recognition,
    **syllabification by grammar rules + dictionary**, and syllable-to-neume assignment. They report syllable
    alignment needing **≈2.3 % interventions**, for about **9×** efficiency over manual transcription.
  * LEGATO 2 claims embedded text output but is unreleased.
  * The SMB OMR-NED symbol categories *include* `lyric`, so lyrics count toward the error when present.
* **Practical engines:**
  * **Audiveris** uses Tesseract with lyric-specific word-gap handling (a separate `lyric` OCR button, "because
    lyric word gaps can be much wider").
  * **copisteria** leaves text to external OCR boxes and says a vision-language OCR such as PaddleOCR-VL beats
    Tesseract on small print.
  * **homr** uses RapidOCR for titles.

### 6.2 Engines usable in the artifact
| Engine | Licence | Files (self-hosted) | Notes |
|---|---|---|---|
| **tesseract.js 7.0.0** (Dec 2025; on cdnjs) | Apache-2.0 | `worker.min.js` 0.11 MB; core `tesseract-core-{relaxedsimd-,simd-,}lstm.wasm.js` ≈ 3.9 MB each (the `.wasm` alone is 2.86 MB); `tessdata_fast` eng **4.11 MB**, lat 3.19, deu 1.53, fra 1.13, ita 2.70 | v7 is 15–35 % faster than v6 (relaxed-SIMD build). Since **v6 only `text` output is on by default**, so request `{blocks:true}` to get word/line boxes. `corePath` must be a *directory* holding the variants. `langPath` + `gzip:false` serves raw `.traineddata`. Set `workerBlobURL:false` to load `workerPath` from our own origin. `tessdata_best` eng 15.4 MB is over the cap |
| **PP-OCRv5 mobile via onnxruntime-web** | Apache-2.0 | det 4.8 MB, Latin rec 8.0 MB (fp32 ONNX, `nakamura196/ppocrv5-mobile-web-onnx`) | More robust on degraded scans. Needs DB post-processing + CTC decode in JS, and shares the ORT runtime. Use it as an upgrade path |

### 6.3 Recommended lyric pipeline
1. **Find lyric bands.** After staff detection and music-symbol masking, look in each inter-staff gap and below the
   last staff. Find text rows by horizontal projection of the leftover small CCs: x-height ≈ 0.6–1.2 s, with a
   common baseline. Several stacked rows in one gap are **verses 1..n**, numbered top-down.
   * A leading `1.`, `2.` etc. at the row start gives the verse number. Strip it, as Audiveris does since 5.10.
   * Text far below the last system (verses 4–6 printed as stanzas) is **not underlay**. Report it as unattached
     extra text and a warning.
2. **OCR each row.** Crop with a margin of ~0.3 s, upscale so the x-height is ≥ 20 px, and binarise. Run
   tesseract.js with `tessedit_pageseg_mode = 7` (single line) and request `blocks` for word boxes and confidence.
   Restrict the character set to letters, punctuation, hyphen, apostrophe and digits.
3. **Tokenise into syllables using the print.**
   * Engravers separate syllables with **centred hyphens** ("glo - ry"), which OCR returns as `-` tokens or as
     `glo-ry`. Words are separated by wider gaps.
   * **Extenders** are thin horizontal lines at baseline height after a word's last syllable. They often vanish in
     OCR, so detect them **geometrically** in the band: a long thin horizontal CC with height ≤ t·1.5 and length
     ≥ 1 s.
   * If OCR merged a hyphenated word, split it at the hyphen. Use Liang/TeX hyphenation patterns only as a last
     resort, because the score already shows the splits.
4. **Assign `syllabic`** from position in the word: no hyphens → `single`; first → `begin`; inner → `middle`;
   last → `end`. MusicXML 4.0 `<lyric number="v">` per verse holds `<syllabic>`, `<text>`, optional `<elision>`,
   and `<extend type="start|stop|continue"/>`.
5. **Align syllables to notes.** Run a monotonic DP (DTW-like) over the note onsets of the target voice in that
   system.
   * Cost = |syllable centre − notehead centre| in staff spaces. Allow skipping a note (melisma); a syllable may
     not be skipped without a penalty.
   * Lyrics are usually centred under the head. The first syllable of a word may be left-aligned.
   * **Melisma cues:** a slur or tie across notes, an extender after the syllable, or beamed notes with one
     syllable. Notes inside a melisma get no `<text>`. The syllable that starts the melisma gets
     `<extend type="start"/>` and its last note `<extend type="stop"/>` (MusicXML allows a standalone `<extend>`).
6. **Which voices get which lyric rows.**
   * **Closed SATB hymn** (rows between the staves): attach to **all four voices**, aligning separately for each
     voice so rhythmic differences (e.g., an alto passing tone) become melismas or skips.
   * **Open score**: rows below a staff belong to that staff's part(s).
   * **Rows above a staff**: attach to the staff below, or above, by proximity. Audiveris treats "lyrics above
     staff" as a separate option.
   * Report per-part, per-verse coverage (syllables attached / syllables OCR'd) as a confidence signal.
7. **Hymn specifics:** "A-men" codas; elisions (`‿` ligature between two syllables on one note → `<elision>`);
   apostrophes ("pray'r"); italic refrains; small-caps or all-caps first words of a verse.

---

## 7. In-browser execution

### 7.1 onnxruntime-web (MIT)
* **Versions:** npm latest is **1.31.1** (2026-11-05). cdnjs carries **1.30.0**.
* **Loading under the artifact CSP:**
  * Load the JS from cdnjs with a `<script>` tag, e.g. `ort.wasm.min.js` (0.05 MB) or `ort.min.js` (0.37 MB).
    Self-host the wasm from **the exact same version** under `assets/`, and set `ort.env.wasm.wasmPaths =
    'assets/'`. The docs warn that mixing versions makes initialisation fail.
  * Alternatively, ship a compressed `.wasm.gz` and decompress it with `DecompressionStream('gzip')`. Pass the bytes
    in via **`ort.env.wasm.wasmBinary`** (typed in onnxruntime-common: "a custom buffer which contains the
    WebAssembly binary").
* **Binary sizes per version (simd-threaded wasm / JSEP-WebGPU wasm):**

  | Version | simd-threaded wasm | JSEP (WebGPU) wasm |
  |---|---|---|
  | 1.17.3 | 10.65 MB | 19.5 MB |
  | 1.20.1 | 11.25 MB | 21.7 MB |
  | 1.22.0 | 11.21 MB | 21.9 MB |
  | 1.24.1 | 12.3 MB | 24.9 MB |
  | **1.30.0** | **14.24 MB** | **28.3 MB** |
  | 1.31.1 | 14.85 MB | 29.5 MB |

  Measured on 1.22.0: gzip −9 gives **2.87 MB**, brotli −q11 **1.80 MB**.
* **Execution provider:**
  * Every JSEP/WebGPU binary is > 15 MB, so WebGPU would need chunked or compressed shipping, plus a capable GPU.
    Default to **`executionProviders: ['wasm']`**.
  * WebGPU on ORT-web gave large speed-ups (SAM encoder 19×, decoder 3.8× vs WASM; Microsoft, Feb 2024), but
    frequent CPU↔GPU transfers can slow it down.
* **Threads:** multithreading needs WebAssembly threads **and `crossOriginIsolated`**. An artifact iframe almost
  certainly isn't cross-origin isolated, so plan for **`numThreads = 1`**. Parallelism comes from running pages or
  stages in our own Web Workers instead.
* **Proxy worker:** `env.wasm.proxy = true` creates the worker from a Blob and is documented as not working under
  CSP. Run our **own** worker file (`assets/omr-worker.js`) that imports ORT and the core.
* **Model size cap:** a model file must be ≤ 15 MB, or split into chunks (`model.onnx.part0..n`) concatenated into
  one `Uint8Array` before `InferenceSession.create(bytes)`. Total assets must stay ≤ 64 MB.
* **Quantisation:**
  * fp16 halves size. Dynamic int8 (`onnxruntime.quantization.quantize_dynamic`) gives ~¼ size for
    MatMul/Gemm-heavy transformers. Static QDQ int8 is best for CNNs; calibrate on our synthetic hymn pages.
  * int8 on the WASM EP is fast with SIMD. Accuracy drift is model-specific: measure TEDn/NED before and after.
  * `freeDimensionOverrides` with fixed input sizes helps performance.
* **Node parity:** `onnxruntime-node@1.31.1` (MIT) runs the same `.onnx` in the harness.

### 7.2 Classical image processing: opencv.js vs plain JS
* **opencv.js** (Apache-2.0 for OpenCV ≥ 4.5) has no package on cdnjs. `@techstark/opencv-js` 4.10 ships a single
  **10.4 MB** `opencv.js` with the wasm inlined as base64. That is heavy, and it brings its own memory management
  (`Mat.delete()`).
* **Recommendation: write the ~10 needed primitives in plain typed-array JS:** integral image, Sauvola/Otsu,
  projection profiles, run-length encoding, union-find CC labelling, morphology with line structuring elements,
  distance transform, NCC template matching, and bilinear resampling. Each is O(N), runs in ~10–200 ms on an
  8 Mpx page in V8, works identically in node, and costs ~0 KB of assets.

### 7.3 PDF and rendering libraries
* **pdf.js 3.11.174** (Apache-2.0) is already in `package.json` as `pdfjs-dist ^3.11.174`, and is the version
  pinned for the artifact. Load `pdf.min.js` and `pdf.worker.min.js` from cdnjs as plain scripts; this makes pdf.js
  use a fake worker on the main thread. Render each page to `OffscreenCanvas`/canvas → `getImageData` → grayscale.
* **Notation preview:** **OpenSheetMusicDisplay 2.3.0** (BSD-3-Clause; UMD on jsdelivr). Verovio 6.4.1 is
  **LGPL-3.0** and a 28 MB package, so avoid it.

### 7.4 Rough per-page budget (single-thread WASM, mid-range laptop; estimates to verify in the harness)
* Pure-JS classical stages: ≈ 0.3–1.5 s per 300-dpi page.
* Tesseract, fast model: ≈ 0.1–0.3 s per lyric row. A hymn page with 4 systems × 3–4 verses is ≈ 2–5 s.
* Tiny classifier CNN on a few hundred crops: < 0.5 s.
* A 2M-param detector at a 1536-px long side: ~1–3 s. copisteria quotes ~5 s per page on CPU in PyTorch, including
  the evidence model and start-up.

---

## 8. Evaluation metrics and harness

| Metric | Definition | Where | Notes for us |
|---|---|---|---|
| **SER / CER / LER** | Edit distance ÷ reference length on symbols, characters, or lines of a sequence encoding | PrIMuS, SMT, Zeus | Depends on encoding (kern vs bekern vs LMX); not comparable across systems |
| **TEDn** | Zhang–Shasha tree edit distance on MusicXML with note-level costs, normalised by the gold tree; correlates with editor effort | Hajič jr. et al., ISMIR 2016 (human preference corpus of 1,230 judgments); Mayer et al. 2024; LEGATO | O(m²n²); LEGATO truncates trees to < 6,000 nodes |
| **OMR-NED** | (I + D) / (N_pred + N_ref) over **visual** symbols. A substitution counts as delete + insert. Broken down by category (heads, pitch, accidentals, beams, dots, … **lyric**) | Martinez-Sevilla et al., "Sheet Music Benchmark", ISMIR 2025, built on **musicdiff** (MIT, v6.0) | The de-facto cross-system metric in 2025–26: LEGATO, Transcoda, copisteria (`efficient-musicdiff`), homr (own token version) |
| **MV2H** | Joint multi-pitch / **voice separation** / meter / note value / harmony, with disjoint penalties; non-aligned variant via DTW | McLeod & Steedman, ISMIR 2018; `apmcleod/MV2H` (Java reference, MIT); pyMV2H | The voice score directly measures SATB splitting quality |

**Project harness (node) recommendation**
1. **Ground truth** is MusicXML from our synthetic hymn set (§4) plus a handful of real scans.
2. **Our own JS metrics** (fast, no Python):
   * **Note F1 per part:** match on (onset, pitch, duration) after part alignment.
   * **Part-assignment accuracy:** the fraction of GT notes landing in the right S/A/T/B part. This is the key
     metric for requirement 2.
   * **Lyrics:** syllable CER, `syllabic` accuracy, **syllable→note attachment accuracy** per verse, and verse-count
     correctness.
   * **Measure validity:** the share of measures whose voices sum to the time signature.
   * **Token NED** per staff, in homr style.
3. **Optional reference scores** run offline with the Python and Java tools on the machine: musicdiff OMR-NED (MIT)
   and MV2H (MIT). Audiveris (AGPL, run as a separate process, never shipped) can serve as a lyric-capable baseline.

---

## 9. Recommended pure-browser architecture

### 9.1 Principles
* **Deterministic classical core first.** It is fast, tiny, and licence-clean, and it is debuggable through the
  overlay. Printed hymnals are the easy end of OMR, and a classical pipeline tuned to them plus strong musical
  constraints (homorhythm, time slots, measure sums) should beat generic ML that was never trained on SATB with
  lyrics.
* **ML only where it pays,** behind interfaces that the classical code also implements: a symbol classifier, an
  optional detector, and an optional OCR upgrade.
* **One codebase for browser and node:** ES modules with no DOM access in the core. The browser shell handles
  PDF/canvas/UI. Node handles pdftoppm/pdfimages + pngjs. ML backends are injected: `onnxruntime-web` or
  `onnxruntime-node`, and `tesseract.js` in both.

### 9.2 Pipeline (core, environment-agnostic)
```
Page {w,h,data:Uint8ClampedArray gray}
 └─ preprocess: shading-normalise → Sauvola(int. images) [+Otsu check] → deskew (projection variance)
 └─ staffMetrics: run-length (t, s, t+s)
 └─ staves: per-strip projection peaks → 5-line groups → line tracking (polylines) → systems (brace/bracket/barline continuity)
 └─ scale-normalise to s≈20px (coordinates mapped back for overlay)
 └─ staffRemoval: run-length ≤ ~1.75t on tracked lines (keep original for matching)
 └─ components: union-find CC + hole CCs; text-row detection → lyric bands (masked from music)
 └─ symbols:
     heads (NCC templates from Bravura/Leland + optional tiny CNN), stems, beams (count), flags, dots,
     accidentals, clefs, key/time sigs (digits), rests, barlines (staff-/system-height), ties/slurs, fermatas
 └─ assembly: head↔stem↔beam graph, accidental/dot attachment, chords
 └─ rhythm: per voice/measure hypothesis search + time-slot alignment across voices; pickup/final; repair + flags
 └─ voices: stem-direction split, unisons, shared-stem chords, rests
 └─ parts: staff classifier (closed-score vocal vs keyboard vs single voice) → part plan per page/movement
 └─ lyrics: band→rows→tesseract(blocks)→syllables(hyphen/extender geometry)→verse numbers→DP alignment per voice
 └─ musicxml: score-partwise 4.0 writer (parts, staves, voices/backup, lyrics with syllabic/extend, implicit pickup)
 └─ report: per-stage timings, per-part summary (split provenance), per-measure confidence, warnings, overlay geometry
```

### 9.3 Browser shell and assets (all relative, ≤ 15 MB per file)
| Asset | Size | Licence |
|---|---|---|
| `assets/omr-worker.js` (core bundle, module worker or classic) | < 0.5 MB | ours |
| tesseract.js `worker.min.js` | 0.11 MB | Apache-2.0 |
| tesseract core `tesseract-core-simd-lstm.wasm.js` + `tesseract-core-lstm.wasm.js` (+ relaxedsimd optional) | 2 × 3.9 MB (+3.9) | Apache-2.0 |
| `eng.traineddata` (tessdata_fast) (+ `lat` 3.19, `deu` 1.53 optional) | 4.11 MB | Apache-2.0 |
| sample scanned SATB hymn PDF (PD) | 0.3–2 MB | PD |
| *(phase 2)* ORT `ort-wasm-simd-threaded.wasm` 1.30.0 (or `.gz` + `wasmBinary`) | 14.24 MB (≈3.5 MB gz) | MIT |
| *(phase 2)* tiny symbol CNN (int8) / copista-2m detector (fp16 ONNX ≈ 4 MB) | 0.1–8 MB | ours / Apache-2.0 (+NOTICE) |
| CDN `<script>`s: pdf.js 3.11.174 + worker (cdnjs), tesseract.js 7.0.0 (cdnjs), OSMD 2.3.0 (jsdelivr), ORT 1.30.0 JS (cdnjs, phase 2) | n/a | Apache/BSD/MIT |

Phase 1 total ≈ 13–20 MB; phase 2 ≈ 30–40 MB. Both are well under 64 MB.

### 9.4 Phased plan
1. **Phase 1 (ship):**
   * Classical core, tesseract lyrics, SATB splitting rules, MusicXML writer, and the harness on synthetic hymn
     scans.
   * Targets on clean synthetic closed-score hymns: note F1 ≥ 95 %, part assignment ≥ 97 %, lyric attachment
     ≥ 90 %.
2. **Phase 2 (ML assist):**
   * **(a) Tiny CNN** for head/rest/accidental/clef crops, trained on LilyPond/Verovio-rendered synthetic crops +
     DeepScoresV2 (CC BY 4.0), exported to int8 ONNX.
   * **(b) Spike: copista-2m** (Apache-2.0):
     1. Export the 1.94M detector to ONNX in Python on this machine.
     2. Confirm that the detector source has no Ultralytics/AGPL code; `export.py` mentions ultralytics-format
        datasets and "custom loops".
     3. Use its `stem_dir`/`voice_slot`/`staff_position` attributes as an additional vote in our assembly.
     4. Port its Viterbi rhythm idea, not its Python code.
     5. Keep its NOTICE file (Apache-2.0 §4(d)).
   * **(c) Optional** PP-OCRv5 Latin recogniser for lyrics on degraded scans.
3. **Not recommended:**
   * End-to-end image→sequence models (SMT/SMT++, Zeus, LEGATO, TrOMR, homr transformer) in the browser. Their
     weights are 40–430 MB plus a gated Llama encoder for LEGATO. Autoregressive decoding is slow on single-thread
     WASM. They are trained on piano/quartet/Lieder with no SATB part semantics, and they drop lyrics.
   * homr and Audiveris for licence reasons (AGPL).

### 9.5 Key risks and mitigations
* **Shared-stem S/A chords and unisons:** explicit handling (§5.2), plus a confidence flag when chord size > 2.
* **Lyric rows touching low notes or ledger lines:** run text-row detection *after* masking assembled music
  symbols, and use x-height and baseline consistency checks.
* **Hymnals printing verses 3+ as stanzas below the music:** detect them and report them as unattached text, with
  no hallucinated underlay.
* **Low-dpi scans (s < 10 px):** upscale 2× before recognition. Audiveris refuses small staff spacing, and
  copisteria's figures note that pages had to be upscaled for it.
* **Warped phone scans:** per-strip line tracking plus stable-paths fallback, and coordinate mapping instead of
  image warping.
* **Licence hygiene:** keep a `THIRD_PARTY.md` listing pdf.js (Apache-2.0), tesseract.js + core + tessdata_fast
  (Apache-2.0), OSMD (BSD-3), ORT (MIT), Bravura/Leland templates (OFL-1.1), and copista (Apache-2.0 + NOTICE) if
  used. Ship nothing AGPL, GPL or NC.

---

## 10. References (URLs)

**Systems / code / weights**
- Audiveris (AGPL-3.0), releases 5.10–5.11: https://github.com/Audiveris/audiveris · handbook text/lyrics: https://audiveris.github.io/audiveris/_pages/guides/ui/ui_tools/text · updates: https://audiveris.github.io/audiveris/_pages/updates
- oemer (MIT): https://github.com/BreezeWhite/oemer · ONNX checkpoints: https://github.com/BreezeWhite/oemer/releases/tag/checkpoints · omr-mcp note on ConvTranspose pads: https://pypi.org/project/omr-mcp/0.2.0/
- homr (AGPL-3.0): https://github.com/liebharc/homr · Benchmark.md, LICENSE_FAQ.md, Changelog.md in repo · ONNX: https://github.com/liebharc/homr/releases/tag/onnx_checkpoints
- copisteria (Apache-2.0): https://github.com/kobimusic/copisteria · weights: https://huggingface.co/kobimusic/copista-2m , https://huggingface.co/kobimusic/copista-28m
- Polyphonic-TrOMR (Apache-2.0): https://github.com/NetEase/Polyphonic-TrOMR · paper https://arxiv.org/abs/2308.09370
- SMT: https://arxiv.org/abs/2402.07596 · https://github.com/antoniorv6/SMT · SMT++: https://arxiv.org/abs/2405.12105 · https://github.com/antoniorv6/SMT-plusplus · IJCV: https://link.springer.com/article/10.1007/s11263-025-02654-6 · weights https://huggingface.co/PRAIG/smt-fp-grandstaff , https://huggingface.co/antoniorv6/smt-grandstaff
- Zeus / OLiMPiC / LMX: https://arxiv.org/abs/2403.13763 · https://github.com/ufal/olimpic-icdar24 · data http://hdl.handle.net/11234/1-5419
- LEGATO: https://arxiv.org/abs/2506.19065 · https://github.com/guang-yng/legato · https://huggingface.co/guangyangmusic/legato · LEGATO 2: https://arxiv.org/abs/2607.05769
- Transcoda: https://arxiv.org/abs/2605.10835 · polish-scores: https://huggingface.co/datasets/btrkeks/polish-scores
- CRNN-CTC (2026): https://arxiv.org/abs/2604.16446
- Real-world manuscripts + Smashcima (ICDAR 2026): https://arxiv.org/abs/2606.09479 · https://github.com/OMR-Research/Smashcima
- Toward a More Complete OMR Solution (YOLOv8 + assembly, MUSCIMA++): https://arxiv.org/abs/2409.00316
- Cluster and Separate (GNN voice/staff, MIT): https://arxiv.org/abs/2407.21030 · https://github.com/CPJKU/piano_svsep
- Detector licences overview (Ultralytics AGPL vs Apache alternatives): https://lightly.ai/blog/best-ultralytics-alternatives-in-2026 · https://blog.roboflow.com/rf-detr-vs-alternatives/

**Datasets**
- DeepScoresV2: https://zenodo.org/records/4012193 · paper https://srv-clst-301-data66.zhaw.ch/bitstream/11475/20647/3/2020_Tuggener-etal_DeepScoresV2-dataset-and-benchmark_ICPR.pdf
- MUSCIMA++: https://ufal.mff.cuni.cz/muscima · https://arxiv.org/abs/1703.04824
- PrIMuS / Camera-PrIMuS: https://grfia.dlsi.ua.es/primus/
- GrandStaff (IJDAR 2023): https://doi.org/10.1007/s10032-023-00432-z · https://github.com/multiscore/e2e-pianoform
- Sheet Music Benchmark + OMR-NED: https://arxiv.org/abs/2506.10488 · https://huggingface.co/datasets/PRAIG/SMB
- OpenScore Lieder (CC0): https://github.com/OpenScore/Lieder · PDMX: https://zenodo.org/records/15571083
- MusiCorpus: https://arxiv.org/abs/2605.18436
- AMNLT: https://arxiv.org/abs/2412.04217 · ICDAR 2023 paper: https://observatorio-cientifico.ua.es/documentos/6522c912ec1a10197ffdc19c
- Hartelt, Eipert, Puppe 2024 (chant pipeline incl. syllables): https://doi.org/10.3390/app14167355 · OMMR4all revisited: https://arxiv.org/abs/2411.15741

**Classical methods**
- Stable paths (TPAMI 2009): https://repositorio.upt.pt/entities/publication/090ea399-f415-42c2-b3fb-e980faf83c3f · staff removal w/ stable paths: https://www.scitepress.org/Papers/2008/19378/
- Dalitz et al. 2008, comparative study of staff removal: https://www.pubmed.gov/18369247/
- Cardoso & Rebelo, staffline thickness/distance estimation: https://repositorio.inesctec.pt/handle/123456789/1876
- Selectional auto-encoders for binarisation / music document analysis: https://grfia.dlsi.ua.es/repositori/grfia/pubs/395/1706.10241.pdf · https://ismir2018.ismir.net/doc/pdfs/93_Paper.pdf
- Shafait, Keysers, Breuel 2008 (integral-image Sauvola): DOI 10.1117/12.767755

**Metrics**
- musicdiff (MIT): https://github.com/gregchapman-dev/musicdiff · efficient-musicdiff: https://github.com/guang-yng/efficient-musicdiff
- MV2H (MIT): https://github.com/apmcleod/MV2H · ISMIR 2018 paper https://ismir2018.ismir.net/doc/pdfs/148_Paper.pdf
- TEDn origin (Hajič et al., ISMIR 2016): https://bpb-us-e1.wpmucdn.com/wp.nyu.edu/dist/2/2294/files/2016/07/289_Paper.pdf

**Browser runtime**
- onnxruntime-web env flags: https://onnxruntime.ai/docs/tutorials/web/env-flags-and-session-options.html · WebGPU blog: https://opensource.microsoft.com/blog/2024/02/29/onnx-runtime-web-unleashes-generative-ai-in-the-browser-using-webgpu/ · WebGPU EP issue: https://github.com/microsoft/onnxruntime/issues/15796
- tesseract.js (Apache-2.0): https://github.com/naptha/tesseract.js · local installation: https://github.com/naptha/tesseract.js/blob/master/docs/local-installation.md · tessdata_fast: https://github.com/tesseract-ocr/tessdata_fast
- PP-OCRv5 for the browser: https://huggingface.co/nakamura196/ppocrv5-mobile-web-onnx · https://www.paddleocr.ai/latest/en/version3.x/deployment/browser.html
- OpenSheetMusicDisplay (BSD-3): https://github.com/opensheetmusicdisplay/opensheetmusicdisplay
- pdf.js 3.11.174 on cdnjs: https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js
- MusicXML 4.0 `<lyric>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/lyric/
- SMuFL fonts (OFL-1.1): https://github.com/steinbergmedia/bravura · https://github.com/MuseScoreFonts/Leland
- MuseScore closed-SATB → parts discussion: https://musescore.org/en/node/292464
