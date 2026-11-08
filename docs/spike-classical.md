# Spike: a classical (non-ML) OMR front end in plain JS

**Question.** Can rule-based image processing in plain JavaScript find the staves, noteheads, stems and barlines on *scanned* hymn and chorale pages well enough to sit at the core of the client-side OMR app? Specifically: binarization, deskew, staff-space estimation, staff detection, staff removal, connected components, filled and hollow noteheads, stem direction and barlines.

**Answer: yes for the staff/geometry layer, and yes for filled noteheads and stem-based SATB voice splitting. Hollow notes, chords and symbol recognition are where hand rules run out.** On 180 synthetic scans under realistic degradations (37 k noteheads in total, 31 k of them under realistic conditions):

| stage | result (15 realistic conditions, 150/200/300 dpi) |
|---|---|
| staff detection | recall 99.9 %, precision 100 %, mean line-position error 0.01–0.1 px |
| staff-space estimate | 0.24 % mean error |
| deskew (rotations up to 4°) | ≤ 0.01° error; 0.22° on the phone/perspective case |
| noteheads (all kinds) | P 99.7 / R 97.3 / **F1 98.5** |
| filled / half / whole heads | F1 99.2 / 88.8 / 69.2 |
| pitch (staff position) of matched heads | 99.8 % |
| stem direction | 98.5 % |
| **SATB voice assignment from stem direction alone** | **97.0 %** (clean 98.6 %, flatbed "scan" 95.7 %, "phone" 83.0 %) |
| unison heads shared by two voices (two stems) | 197/200 found as "both voices" |
| barlines | P 100 / R 99.9 |
| system grouping (which staves form a system) | 99.0 % |
| runtime | 0.43 s/page at 150–200 dpi, 0.70 s at 300 dpi (1.0 s with deskew), single thread, node 24 |

On two real 1906 hymnal scans the geometry layer worked first time (all main staves, systems and barlines found). Notehead recall was only **about 65–70 %**, judged by eye on one system per page with a different engraving font. The rules were tuned on LilyPond's Emmentaler glyphs, and that is the main risk (see *Real scan*).

**Recommendation.**
- Adopt this pipeline as the deterministic front end. The parts to keep are binarization, deskew, staff-space estimation, staff tracking and removal, and system grouping. Also keep staff-position-constrained candidate generation, stem search and barlines.
- Make the notehead/symbol **classifier** swappable. That means a small learned patch classifier (ONNX) over the candidates this pipeline proposes, or at least self-calibrating templates.
- Voice separation for closed score can be decided by stem direction plus staff role in the system. That rule scored 97 % here.

---

## 1. What was built

All code is in `spike/classical/`. The core in `src/` is environment-agnostic: it works on `{width, height, data: Uint8ClampedArray}` gray pages and returns plain objects. Only `image.js` file I/O touches node APIs. Entry point: `runOMR(gray, opts)` in `src/pipeline.js`.

| stage | method | file |
|---|---|---|
| binarization | Background normalisation: per-block 90th percentile, smoothed and bilinear-interpolated, then divided out. Then global Otsu. An *absolute contrast guard* (ink must be ≥ max(12, 2.5·σ_noise) grey levels below the local paper level) stops vignetted corners turning black. A lenient companion threshold is used only to recover faint hairline stems. Isolated-pixel removal, plus area-scaled despeckle when the page is noisy. | `binarize.js` |
| deskew | Projection-profile sharpness (Σ bin²) of `y + x·tanθ` over ±8°: 0.25° coarse, then 0.02° fine. Rotate the grey image back and re-binarize. | `skew.js` |
| staff space / line thickness | Vertical run-length "combo" histogram (black run + following white run; Fujinaga / Audiveris). Cross-checked by the autocorrelation of strip-wise row projections, which survives broken lines and blur. | `staffspace.js` |
| staff detection | Thin-horizontal mask (vertical run ≤ 2·lt+1.5, horizontal run ≥ 0.8·ss, ±1-row jitter). Row projections in strips 6·ss wide, then a 5-equally-spaced-peaks search, then a 4-of-5 search with one inner line missing. Candidates are tracked across strips, so each line is a polyline, which tolerates curvature. Relaxed passes (gap-bridging, lower peak threshold) run only on rows not already explained. Extents are walked out while ≥ 4 lines have ink; barline-like columns are skipped. | `staves.js` |
| systems | Staves are linked when a thin, near-vertical ink column (a bracket or system start bar) joins one staff's bottom line to the next staff's top line, with paper on one side so a dark blob doesn't count. | `staves.js` |
| staff removal | Line tracking plus a vertical run-length test: erase the run through the line when it is ≤ 1.8·lt+1. | `staffremoval.js` |
| connected components | Two-pass union-find, 8-connectivity; integral images. | `cc.js` |
| noteheads | For every staff, every staff position p (−13…13) and every column: O(1) box-sum features on the original binary (B) and the staff-removed binary (R). *Filled*: solid core, wide enough, closed top/bottom, not inside a beam, not part of a staff-spanning bar. *Hollow*: white core (line rows excluded for heads on lines), ink walls left and right, closed top/bottom, no accidental-like strokes (column test), not a barline, and the tilted-hole check (ink upper-left and lower-right). Heads beyond the staff need their ledger lines. Clef, time-signature and header exclusion zones are found from components. NMS runs across x, p and staves, plus same-row NMS so dots don't count. | `noteheads.js` |
| stems | For each head, scan columns on both sides for the longest vertical ink run through the head row (small gaps bridged); a stem must extend ≥ 2.2 ss. Direction is up, down, or both (two different columns: right-up plus left-down = a unison of two voices). Stem rule: filled and half notes need a stem; stemless hollow heads must be whole-note wide. Lenient-binary fallback for heads with no stem. | `stems.js` |
| barlines | Thin columns covering ≥ 90 % of the staff height on R. The full vertical extent must end at the staff edges or continue to the neighbouring staff of the same system (span bar). Stems, the staff start and the header zone are rejected; thin+thick pairs are merged (final and double bars). | `barlines.js` |

---

## 2. Test data with pixel-exact ground truth

**Scores** (`spike/classical/scores/`, all public domain or CC0):

| piece | content | staff size → staff space at 150/200/300 dpi |
|---|---|---|
| `satb20` | Closed-score SATB hymn (Wesley, *Love divine*, 4 verses; my tune, CC0), ChoirStaff, voiceOne/voiceTwo, 242 heads incl. 2 unisons | 20 pt → 10.4 / 13.9 / 20.8 px |
| `satb16` | Same music at hymnal size | 15 pt → **7.8** / 10.4 / 15.5 px |
| `melody` | Melody + 2 verses (Jonson, *To Celia*): slurs, ties, dots, accidentals, ledger lines, rests | 20 pt |
| `piano` | Grand staff: chords, seconds, beams, 2 voices, whole-note chords, ledger lines | 18 pt |

**Truth method** (`scores/omrtruth.ily`, `tools/truth.js`). Each score is rendered twice by LilyPond 2.24. The truth render paints every relevant grob in a unique colour: R = class (notehead filled/half/whole, stem up/down, barline, staff symbol, ledger, beam, accidental, clef, lyric text, …), (G,B) = a 16-bit object id. It is rasterized without anti-aliasing. A Scheme colour callback logs, for every id, the pitch, duration, staff position, stem direction and voice name, plus lyric text. Colour does not change layout: the clean and truth renders have pixel IoU 0.992 against each other. So every pixel of every notehead, stem, barline and staff line is known exactly at any DPI. Unisons where one head hides another are re-attached to the visible head, so it carries both voices. The truth JSON also contains lyric syllable boxes with their text, which the lyrics/OCR work can reuse.

**Degradations** (`tools/degrade.py`). All geometric warps are defined as inverse maps, and truth points are pushed forward by numerical inversion, so the truth stays exact after rotation and warping. Photometric parameters are in physical units.

| condition | definition |
|---|---|
| clean | pdftoppm anti-aliased grey |
| rot+0.6 / rot-2 / rot+4 | rotation (deg) |
| blur1 / blur2 | Gaussian σ = 1 / 2 px at 300 dpi (scaled with dpi) |
| noise20 / noise45 | Gaussian noise σ = 20 / 45 grey levels |
| jpeg25 / jpeg8 | JPEG quality 25 / 8 |
| light | strong lamp vignette + gradient, paper 0.85, contrast 0.7 |
| speckle | 0.4 % salt & pepper + dust blobs |
| bin_thick / bin_faded / bin_thin | 1-bit photocopy: blur + noise + threshold 205 / 95 / 60 (bin_thin deletes 1–2 px lines entirely) |
| warp | page curl (0.4 % H bow) + keystone 0.03 + 0.8° |
| scan | flatbed: 0.9° + blur 0.7 + mild light + noise 8 + JPEG 60 |
| phone | curl 0.6 % + keystone 0.04 − 1.4° + strong light + blur 1.2 + noise 10 + JPEG 45 |

That is 4 pieces × 3 DPIs × 18 conditions = **216 page images, 37 422 truth noteheads**. The rendered and degraded set (`data/set/*.png` + truth `*.json`) is reusable by the other workstreams.

---

## 3. Results

Matching rules: a head matches if its centre is within 0.5 ss. A barline matches on the same staff within 1 ss in x. A staff matches if its middle line is within 0.6 ss. "Pitch" = the detected staff position equals the truth staff position. "SATB voice" = the voice set from (upper/lower staff of the system) × (stem up/down/both) equals the truth voices. Full tables are in `spike/classical/results/by_*.md`; raw per-image records are in `results/final.jsonl`.

### 3.1 By condition (all pieces, all DPIs; percentages)

| condition | staves R | ss err | skew err | head P | head R | head F1 | half F1 | pitch | stem dir | SATB voice | bar P | bar R | systems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 100.0 | 0.2% | 0.00° | 100.0 | 98.2 | **99.1** | 93.6 | 99.9 | 98.9 | 98.6 | 100.0 | 100.0 | 100.0 |
| rot+0.6 | 100.0 | 0.2% | 0.01° | 99.7 | 97.2 | **98.4** | 89.4 | 99.9 | 98.8 | 97.8 | 100.0 | 100.0 | 100.0 |
| rot-2 | 100.0 | 0.2% | 0.00° | 99.6 | 97.4 | **98.5** | 90.0 | 99.7 | 99.2 | 98.5 | 100.0 | 100.0 | 100.0 |
| rot+4 | 100.0 | 0.2% | 0.01° | 99.9 | 97.2 | **98.5** | 89.3 | 99.9 | 99.2 | 98.5 | 100.0 | 100.0 | 100.0 |
| blur1 | 100.0 | 0.2% | 0.00° | 99.8 | 97.0 | **98.4** | 88.5 | 99.9 | 98.8 | 97.8 | 99.7 | 100.0 | 100.0 |
| blur2 | 93.1 | 8.8% | 0.00° | 94.7 | 86.5 | **90.4** | 42.3 | 98.6 | 90.4 | 83.3 | 97.6 | 91.5 | 92.9 |
| noise20 | 100.0 | 0.2% | 0.00° | 100.0 | 97.9 | **98.9** | 92.0 | 99.9 | 98.9 | 98.5 | 100.0 | 100.0 | 100.0 |
| noise45 | 100.0 | 0.2% | 0.00° | 99.9 | 98.3 | **99.1** | 92.6 | 100.0 | 98.9 | 98.5 | 100.0 | 100.0 | 100.0 |
| jpeg25 | 100.0 | 0.2% | 0.00° | 100.0 | 97.7 | **98.8** | 92.3 | 99.9 | 99.1 | 98.6 | 100.0 | 100.0 | 100.0 |
| jpeg8 | 100.0 | 0.2% | 0.00° | 99.8 | 97.7 | **98.8** | 91.5 | 99.9 | 99.0 | 98.5 | 100.0 | 100.0 | 100.0 |
| light | 100.0 | 0.2% | 0.00° | 100.0 | 98.2 | **99.1** | 93.6 | 99.9 | 98.9 | 98.6 | 100.0 | 100.0 | 100.0 |
| speckle | 100.0 | 0.2% | 0.00° | 100.0 | 98.1 | **99.0** | 92.8 | 99.9 | 98.9 | 98.6 | 100.0 | 100.0 | 100.0 |
| bin_thick | 98.6 | 0.6% | 0.00° | 98.5 | 96.2 | **97.3** | 73.8 | 97.0 | 95.6 | 91.6 | 97.5 | 98.1 | 97.6 |
| bin_faded | 98.6 | 0.2% | 0.00° | 100.0 | 94.5 | **97.2** | 84.6 | 99.9 | 99.0 | 98.6 | 100.0 | 98.9 | 97.6 |
| bin_thin | 33.3 | 78.2% | 0.00° | 100.0 | 12.3 | **21.9** | 0.9 | 99.4 | 97.0 | 76.8 | 100.0 | 17.4 | 23.8 |
| warp | 100.0 | 0.3% | 0.02° | 99.7 | 97.1 | **98.4** | 87.1 | 99.8 | 97.5 | 95.5 | 100.0 | 100.0 | 100.0 |
| scan | 100.0 | 0.3% | 0.01° | 99.4 | 96.8 | **98.1** | 83.0 | 99.7 | 97.7 | 95.7 | 100.0 | 100.0 | 100.0 |
| phone | 100.0 | 0.8% | 0.22° | 97.5 | 95.7 | **96.6** | 68.2 | 99.3 | 94.2 | 83.0 | 99.7 | 99.4 | 88.1 |
| **realistic (15 conds)** | 99.9 | 0.2% | 0.02° | 99.7 | 97.3 | **98.5** | 88.8 | 99.8 | 98.5 | 97.0 | 100.0 | 99.9 | 99.0 |
| **stress (blur2, bin_thick, bin_thin)** | 75.0 | 29.2% | 0.00° | 96.8 | 65.0 | **77.8** | 45.2 | 98.0 | 93.7 | 86.8 | 97.8 | 69.0 | 71.4 |
| **all 216 pages** | 95.8 | 5.1% | 0.01° | 99.3 | 91.9 | **95.5** | 83.3 | 99.6 | 97.8 | 95.8 | 99.7 | 94.7 | 94.4 |

### 3.2 By resolution (realistic conditions)

| DPI | staves R | head P | head R | head F1 | half F1 | stem dir | SATB voice | bar R |
|---|---|---|---|---|---|---|---|---|
| 150 | 100.0 | 99.6 | 95.9 | 97.7 | 82.6 | 97.6 | 94.8 | 100.0 |
| 200 | 100.0 | 99.5 | 97.9 | 98.7 | 89.9 | 98.6 | 97.5 | 100.0 |
| 300 | 99.7 | 99.9 | 98.0 | 98.9 | 93.4 | 99.1 | 98.7 | 99.7 |

### 3.3 By piece (realistic conditions)

| piece | staff space px (150/200/300) | head F1 | filled F1 | half F1 | whole F1 | stem dir | SATB voice |
|---|---|---|---|---|---|---|---|
| satb20 | 10.4 / 13.9 / 20.8 | 99.8 | 100.0 | 96.4 | – | 99.3 | 98.8 |
| satb16 (hymnal size) | 7.8 / 10.4 / 15.5 | 98.9 | 99.3 | 88.4 | – | 95.5 | 95.3 |
| melody | 10.4 / 13.9 / 20.8 | 98.5 | 99.5 | 94.8 | – | 100.0 | – |
| piano | 9.3 / 12.5 / 18.7 | 95.1 | 97.4 | 75.3 | 69.6 | 99.1 | – |

The hardest realistic case for hymnals is satb16 at 150 dpi (staff space 7.8 px, 1-px lines). It still reaches head F1 98.0, but half-note F1 falls to 74.3, stem direction to 91.9 % and SATB voice to 91.2 %. **Ask for (or upsample to) ≥ 200 dpi equivalent**: a staff space of at least ~10 px.

---

## 4. Findings per stage

**Binarization.**
- Background normalisation + Otsu beat Sauvola overall (window = page/60, k = 0.25, same pipeline otherwise): all-page head F1 95.5 vs 94.3, staff recall 95.8 vs 93.4. Sauvola lost a staff on clean pages (95.8 % staff recall, systems 92.9 %) and fell apart on the phone case (head recall 68 %, staff-space error 9 %). Raw per-image records are in `results/sauvola.jsonl`.
- The contrast guard was required for phone-style vignetting. Without it, the dark corner binarized to texture: staves extended into it and systems merged. With it, phone staff recall went from 94.4 to 100 %.
- **Do not median-filter**: a 3×3 median erases 1-px staff lines at 150 dpi. That alone caused noise45 staff recall to drop to 28 % in an early run. Despeckling the binary by component area (scaled by ss²) is safe and fixed noise45 completely (F1 99.1).

**Deskew.**
- The projection-profile estimate is essentially exact for rigid rotation: error ≤ 0.01° up to 4°. The residual is 0.22° when keystone and curl are present.
- Staff lines are tracked as polylines per strip (6 ss wide), so 0.6 % page curl costs nothing. Line-position error stayed ≤ 0.11 px mean and ≤ 0.12 ss max.

**Staff space.**
- The run-length combo estimate is accurate to 0.2 % whenever lines survive binarization.
- It fails by a factor of 2–3 when lines are broken or very blurred. The autocorrelation cross-check fixed some of these cases. It returns "no periodicity" instead of a wrong value when lines are genuinely gone (bin_thin at 200/300 dpi: threshold 60 deletes the 1–2 px lines outright, which no staff-based method can recover).

**Staff detection.**
- The strict pass (25 % of strip width) handles everything except faded copies.
- The cascade adds relaxed passes with gap bridging, applied only to rows not yet explained by a staff. Running relaxed passes everywhere produced phantom staves from lyric lines.
- A 4-of-5 pattern with a missing inner line rescued single staff lines lost to subpixel alignment in faded copies (satb16_300_bin_faded went from 4 to 7 of 8 staves). It must run only after complete staves have claimed their peaks, and only in the strict pass. Otherwise it locks onto text lines.
- **Assumes one staff size per page.** The small "Amen" staves on the real scan were half-missed. Per-region staff space is needed for cue/ossia/Amen staves.

**Staff removal.** The simple run-length rule is good enough for detection, but it cuts hollow-note outlines that are tangent to a line. So hollow-head features read the *original* binary for the top/bottom closure and R for the walls. Requiring the two walls of a hollow head to be in the same R component broke half notes in spaces, and was dropped.

**Noteheads.**
- Constraining the search to staff positions is very effective: pitch accuracy of matched heads is 99.8 % and essentially free.
- Filled heads are near-solved: F1 99.2 realistic, 99.7 clean.
- Every false-positive family seen had to be removed with a dedicated rule:
  - thick final barline (as filled or hollow)
  - head+dot gap (as hollow)
  - sharp/natural/flat interiors (as hollow)
  - bass-clef dots and treble-clef loops
  - time-signature "C" and digits
  - beams
  - duplicate detections between staves
- Hollow heads remain the weak point: half F1 88.8 realistic, 68 phone, 42 under blur2, because blur and JPEG fill the hole. Whole notes reach 69 %, mostly from whole-note chords in the piano piece. Stacked heads in chords (thirds and seconds) also cause misses in the piano piece (half F1 75). Hymns in closed score rarely have three-note chords per stem, so satb20 half F1 is 96.4.
- These rules are tied to the glyph proportions they were tuned on (see Real scan).

**Stems and voice separation (requirement 2).**
- Stem direction is 98.5 % correct (realistic). Closed-score voice assignment by rule reaches 97.0 % realistic and 98.6 % clean: upper staff up = S, down = A; lower staff up = T, down = B; two stems = both voices.
- Unisons, drawn by LilyPond as one head with two stems, are found as "both voices" in 197/200 cases.
- This is strong evidence that the "split shared staves into parts" requirement is decidable from stem geometry for hymn-style closed score, without ML. Grand staves don't need this: the same data shows piano chords with one stem per chord, i.e. a single voice.
- The faint hairline stems of old prints are lost by the main threshold. A lenient-threshold fallback, used only for heads without a stem, recovered them: +33 % detected heads on the real page, with no change on the synthetic set.

**Barlines.** P 100 / R 99.9 realistic, once stems, the staff start, the header zone, staff-spanning test columns and thin+thick merging were handled. Span bars (piano) are recognised as system-spanning.

**Systems.** 99.0 % realistic. The remaining phone errors come from the tolerant vertical-link test (bracket under keystone and shadow). Explicit bracket/brace component recognition would fix it.

---

## 5. Real scan check (no ground truth)

Two pages of *The English Hymnal* (1906, University of Toronto scan via archive.org, public domain), 1502×2233 px ≈ 190 dpi, yellowed paper with show-through. They are in `spike/classical/data/realscan/` (`*_overlay.jpg` = detections).

| page | staves | systems | barlines | heads detected (stems up / down / both / none) |
|---|---|---|---|---|
| p171 (keyboard-style SATB, chords) | 10/10 | 5/5 correct | all, visually | 148 (50 / 76 / 9 / 13) |
| p269 (closed SATB + 2 small "Amen" systems + one 4-line chant staff) | 8 of 10 five-line staves (main 6/6, small Amen 2/4) | 4 | all main, visually | 94 |

- Staff space came out as 18.2 px (consistent), skew −0.1°, and staff lines overlay exactly.
- Notehead recall, judged by eye on one system per page, is about **65–70 %**, with few false positives. The misses:
  - half notes in the period font: rounder, thicker outline, different hole tilt
  - stacked chord heads
  - heads on ledger lines
  - breve-shaped whole notes
- Before the lenient-stem fallback, many correct filled heads were dropped by the stem rule because the stems are hairlines.
- **Conclusion: the geometry layer transfers to real scans unchanged. The hand-tuned head classifier does not transfer fully.**

---

## 6. Runtime

`tools/bench.js`, minimum of 5 runs, single thread, node 24, aarch64. The machine was heavily shared during the measurement (load average 400–1100), so treat these as upper bounds.

| page | total | biggest stages |
|---|---|---|
| 1241×1754 (150 dpi) | 0.43 s | heads 0.11, staves 0.09, binarize 0.07 |
| 1654×2339 (200 dpi) | 0.43 s | heads 0.09, staves 0.08, binarize 0.08 |
| 2481×3508 (300 dpi) | 0.70 s | binarize 0.17, staves 0.16, CC 0.11, heads 0.10 |
| 2481×3508 phone (with deskew) | 1.0 s | + deskew rotation 0.27 |

That is fine for a browser worker. The obvious speedups are a downsampled skew search, a typed-array CC/despeckle, and computing the thin mask once per image. That is already done for the staff passes.

---

## 7. Limits of the classical approach

1. **Font and engraving dependence of the head rules.** The box thresholds encode Emmentaler proportions: hole tilt, outline thickness, head width 1.18–1.4 ss. Fix: keep candidate generation (staff position × x) and the cheap rejections. Then classify candidates with either (a) templates learned on the fly from high-confidence heads of the same page, or (b) a tiny CNN on 2 ss × 2 ss patches. Option (b) is the better bet for IMSLP-style variety, and the candidate stream from this spike is the right input for it.
2. **Symbol recognition is not done.** That covers clefs, key and time signatures, accidentals, rests, flags/beams (durations), dots, ties/slurs and fermatas. The header-zone heuristics used here only suppress false positives. These need a component classifier: classical moments/templates are feasible for clefs, accidentals and rests; ML is more robust.
3. **Hollow heads under blur/JPEG** (blur2 half F1 42) and **bin_thin**-level line loss are effectively unrecoverable with rules.
4. **One staff size per page**: the small Amen/cue staves were partly missed. Only 5-line staves are handled (no 4-line chant).
5. **Chords and seconds**: 3+ stacked heads and displaced seconds lose recall. This matters for piano/keyboard-style hymnals (p171), less for closed-score SATB.
6. **Lyrics are not handled here.** They are cleanly separated, though: no phantom staves on 4-verse pages, and the truth JSON carries lyric boxes with text for the OCR work.

---

## 8. Reuse notes for the product pipeline

- `runOMR(gray)` returns everything in input-image coordinates (deskew undone):
  - `staves[]`: 5 line polylines, left/right, system, space
  - `systems[]`
  - `heads[]`: x, y, kind (filled/half/whole), staff, p (staff position), stem (+1 / −1 / 2 / 0), score
  - `barlines[]`
  - `skew`, `staffSpace`, `lineThickness`, `timings`
- The modules are CommonJS without node dependencies (except `image.js` readers). For the artifact, bundle them with esbuild into an IIFE/worker; no WASM is needed.
- Suggested product flow: this front end → candidate patches → small ONNX symbol classifier (heads, rests, accidentals, clefs) → rhythm/measure assembly → voice split by stem direction + staff role → MusicXML.
- The truth generator (`omrtruth.ily` + `truth.js` + `degrade.py`) can produce unlimited labelled training patches for that classifier, from any LilyPond or MusicXML score converted with musicxml2ly.

## 9. Licensing

- All spike code is original and MIT-licensable. The only runtime dependency is `pngjs` (MIT), used for node I/O only.
- LilyPond (GPL), poppler and ghostscript are used only offline to *generate* test data and are not shipped.
- Test scores: tunes CC0 (written for this spike), texts public domain (Wesley 1747, Jonson 1616).
- The real-scan pages are a 1906 public-domain edition.

## 10. Files

- `spike/classical/src/*.js`: pipeline (see §1)
- `spike/classical/scores/`: `omrtruth.ily`, `satb_music.ily`, `satb20.ly`, `satb16.ly`, `melody.ly`, `piano.ly`
- `spike/classical/tools/`: `make_scores.sh`, `truth.js`, `degrade.py`, `make_dataset.sh`, `eval.js`, `run_all.js`, `report.js`, `omr.js`, `bench.js`, `debug_errors.js`, `probe.js`
- `spike/classical/data/set/`: 216 degraded pages + truth JSON. `data/truth/`: undistorted truth. `data/pdf/`: clean and truth PDFs + grob logs. `data/realscan/`: 1906 hymnal pages + overlays.
- `spike/classical/results/final.jsonl` (per-image metrics), `by_cond.md`, `by_dpi.md`, `by_piece.md`, `by_cond_dpi.md`
