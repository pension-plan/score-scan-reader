# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 06:50 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 06:50, app source hash `237ccb49cd6b`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 76 items, 228 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

Regenerate:

```
node mvp/tools/eval.mjs --set coverage --out mvp/work/eval-coverage.json
node mvp/tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 --out mvp/work/eval-coverage-perf.json   # optional, for timing
node tools/coverage.mjs --eval mvp/work/eval-coverage.json [--perf mvp/work/eval-coverage-perf.json]
```

## How to read the tables

- **Occurrences**: how often the symbol occurs in the truth files, summed over items (`meta.json` counts; this tool's own count from `truth.musicxml` where meta has none). **Items**: items containing it.
- **Accuracy** per input (clean / scan / scan-severe): recall over the truth instances. Note-level tags: truth notes with the tag that are aligned to an app note with the right pitch *and* the tag's feature (an element such as `<dot/>`, `<beam>`, `<slur>`, `<staccato/>`, or, for semantic tags marked *sem*, its meaning: duration for note values, spelled pitch for accidentals, sounding pitch under an ottava). Clef, key and time tags: exact match of the same clef/key/time change at the aligned measure (±1). Directions and structure: the same element and value at the aligned measure (±1). Notes and rests are aligned with all parts merged, so part splitting does not affect these numbers (it is scored under layouts).
- **Emitted**: how many times the app's MusicXML contains the corresponding element, on the typical scan (0 = never written). Emitted and the accuracy denominators (hit/n) count notes for note-level tags, so a chord, beam group, tuplet, arpeggio or ottava line counts once per note it covers, while **Occurrences** follow the generators' count rules in `meta.json` (`count_rules`: chords, beam groups, tuplet brackets and ottava lines once each).
- **Read**: share of truth notes carrying the tag that the app read with the right pitch, whether or not it kept the mark.
- **Status** (from the `scan` input, the typical 200–300 dpi scan): supported ≥ 0.8, partial 0.2–0.8, unsupported < 0.2 or the element is never emitted. Semantic tags whose MusicXML element exists but is never written (e.g. `<octave-shift>`, `<multiple-rest>`) are capped at partial.
- **Confusion** (on `clean.pdf`): false notes (app notes that match no truth note) per truth note in the measures holding the symbol, minus the same rate in the other measures (all items' rate when the symbol is in every measure). *confused* = excess > 0.05 and at least 3 surplus false notes; *unclear* = excess > 0.05 on fewer than 10 truth notes; otherwise *not confused*: the app may drop the mark, but it does not turn it into extra notes. It matters most for marks the app does not output.

**Totals:** 20 supported, 40 partial, 90 unsupported, 25 not measurable, 3 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 75% | **unsupported** | not confused (+0.02) | duration of the aligned note (sem) |
| `note-whole` | 161 | 36 | 142 | 56% (103/183) | 46% (84/183) | 24% (44/183) | 60% | partial | not confused (-0.04) | duration of the aligned note (sem) |
| `note-half` | 1290 | 70 | 1255 | 79% (1097/1394) | 72% (1002/1394) | 34% (471/1394) | 86% | partial | not confused (-0.06) | duration of the aligned note (sem) |
| `note-quarter` | 3662 | 75 | 3918 | 89% (3448/3878) | 88% (3410/3878) | 59% (2302/3878) | 92% | supported | not confused (-0.20) | duration of the aligned note (sem) |
| `note-8th` | 1078 | 57 | 1282 | 77% (831/1078) | 77% (828/1078) | 59% (637/1078) | 85% | partial | not confused (-0.04) | duration of the aligned note (sem) |
| `note-16th` | 355 | 20 | 425 | 65% (230/355) | 59% (210/355) | 50% (176/355) | 85% | partial | not confused (-0.08) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 8 | 2% (2/113) | 3% (3/113) | 1% (1/113) | 82% | **unsupported** | not confused (-0.03) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 0 | 0% (0/71) | 0% (0/71) | 0% (0/71) | 75% | **unsupported** | not confused (-0.01) | duration of the aligned note (sem) |
| `dot` | 265 | 46 | 337 | 74% (199/269) | 74% (198/269) | 49% (133/269) | 93% | partial | **confused** (+0.06) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 6 | 27% (4/15) | 27% (4/15) | 7% (1/15) | 87% | partial | **confused** (+0.21) | <dot/> count + duration |
| `chord` | 447 | 26 | 1180 | 86% (1053/1219) | 83% (1010/1219) | 49% (600/1219) | 85% | supported | not confused (-0.05) | element on the aligned note |
| `beam` | 460 | 52 | 0 | 0% (0/1338) | 0% (0/1338) | 0% (0/1338) | 87% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `flag` | 276 | 30 | 1001 | 46% (127/276) | 45% (125/276) | 42% (116/276) | 72% | partial | not confused (-0.00) | duration of the flagged note (sem) |
| `stem-up` | 2163 | 62 | 2274 | 91% (1969/2163) | 90% (1943/2163) | 65% (1397/2163) | 90% | supported | not confused (-0.23) | element on the aligned note |
| `stem-down` | 3477 | 67 | 3248 | 88% (3068/3477) | 87% (3019/3477) | 66% (2295/3477) | 89% | supported | not confused (-0.45) | element on the aligned note |
| `ledger-above` | 486 | 57 | 455 | 86% (420/486) | 83% (402/486) | 67% (326/486) | 83% | supported | not confused (-0.07) | pitch (sem) |
| `ledger-below` | 332 | 42 | 318 | 82% (273/332) | 80% (264/332) | 55% (184/332) | 80% | partial | not confused (-0.05) | pitch (sem) |
| `grace` | 58 | 2 | 0 | 0% (0/58) | 0% (0/58) | 0% (0/58) | 0% | **unsupported** — element never emitted | not confused (-0.05) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 0% | **unsupported** — element never emitted | not confused (-0.02) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.40) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 37% | **unsupported** — element never emitted | **confused** (+0.19) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | 100% | **unsupported** — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 2 | 100% (3/3) | 67% (2/3) | 0% (0/3) | 100% | partial | not confused (-0.70) | aligned rest with the same duration (sem) |
| `rest-half` | 35 | 14 | 27 | 74% (26/35) | 63% (22/35) | 51% (18/35) | 74% | partial | **confused** (+0.05) | aligned rest with the same duration (sem) |
| `rest-quarter` | 148 | 31 | 130 | 88% (130/148) | 81% (120/148) | 51% (75/148) | 85% | supported | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-8th` | 92 | 15 | 79 | 68% (63/92) | 73% (67/92) | 54% (50/92) | 86% | partial | not confused (-0.05) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 58 | 63% (38/60) | 65% (39/60) | 33% (20/60) | 90% | partial | not confused (-0.07) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 17 | 86% (19/22) | 55% (12/22) | 14% (3/22) | 64% | partial | **confused** (+0.20) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 1 | 60% (6/10) | 10% (1/10) | 0% (0/10) | 30% | **unsupported** | **confused** (+0.38) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 27 | 90% (27/30) | 87% (26/30) | 50% (15/30) | 93% | supported | **confused** (+0.12) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 202 | 14 | 133 | 50% (100/202) | 46% (92/202) | 37% (74/202) | 55% | partial | not confused (-0.02) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 0 | 33% (3/9) | 22% (2/9) | 0% (0/9) | – | partial — <multiple-rest> never emitted | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 100 | 66 | 101 | 95% (95/100) | 98% (98/100) | 85% (85/100) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 61 | 43 | 59 | 93% (57/61) | 95% (58/61) | 72% (44/61) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 14 | 13 | 13 | 93% (13/14) | 93% (13/14) | 93% (13/14) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.66) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 6 | 5 | 5 | 83% (5/6) | 83% (5/6) | 67% (4/6) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.39) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.92) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 15 | 41% (11/27) | 48% (13/27) | 7% (2/27) | – | partial | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 39 | 36 | 48 | 89% (32/36) | 92% (33/36) | 83% (30/36) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 16 | 13 | 28 | 85% (11/13) | 85% (11/13) | 69% (9/13) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 12 | 9 | 23 | 67% (6/9) | 67% (6/9) | 56% (5/9) | – | partial | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 4 | 4 | 6 | 75% (3/4) | 75% (3/4) | 75% (3/4) | – | partial | not confused (-0.33) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 4 | 4 | 1 | 25% (1/4) | 25% (1/4) | 0% (0/4) | – | partial | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 5 | 67% (2/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.32) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 3 | 50% (1/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.49) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 0 | 50% (1/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — low n (2) | not confused (-0.34) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 15 | 12 | 16 | 83% (10/12) | 83% (10/12) | 75% (9/12) | – | supported | **confused** (+0.09) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 7 | 7 | 10 | 86% (6/7) | 100% (7/7) | 71% (5/7) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 8 | 7 | 8 | 71% (5/7) | 71% (5/7) | 43% (3/7) | – | partial | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.27) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.17) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 6 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.28) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 32 | 5 | 18 | 50% (16/32) | 38% (12/32) | 25% (8/32) | – | partial | not confused (-0.15) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 73 | 21 | 53 | 48% (35/73) | 49% (36/73) | 27% (20/73) | 52% | partial | not confused (+0.00) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 20 | 68% (19/28) | 68% (19/28) | 64% (18/28) | 68% | partial | not confused (+0.00) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 47 | 9 | 35 | 60% (28/47) | 60% (28/47) | 40% (19/47) | 60% | partial | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 14% | **unsupported** — <accidental> never emitted | not confused (-0.05) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | 0% | **unsupported** — <accidental> never emitted | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 0 | 33% (3/9) | 11% (1/9) | 33% (3/9) | 11% | **unsupported** — <accidental> never emitted | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.43) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 0 | 0% (0/22) | 0% (0/22) | 0% (0/22) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.40) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 0 | 0% (0/12) | 0% (0/12) | 0% (0/12) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.32) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | unclear (+0.26) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 50% (1/2) | 50% (1/2) | 50% | partial — <accidental> never emitted; low n (2) | not confused (-0.00) | spelled pitch (step, alter, octave) (sem) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 13 | 8 | 3 | 30% (3/10) | 30% (3/10) | 40% (4/10) | – | partial | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 37 | 24 | 28 | 54% (15/28) | 54% (15/28) | 43% (12/28) | – | partial | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 66 | 51 | 90 | 69% (41/59) | 69% (41/59) | 51% (30/59) | – | partial | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.20) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 0 | 0% (0/18) | 0% (0/18) | 0% (0/18) | – | **unsupported** — element never emitted | **confused** (+0.24) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.57) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.52) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.56) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.57) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 11 | 6 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | – | **unsupported** — element never emitted | not confused (-0.35) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 0 | 0% (0/89) | 0% (0/89) | 0% (0/89) | – | **unsupported** — element never emitted | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 8 | 8 | 7 | 38% (3/8) | 38% (3/8) | 50% (4/8) | – | partial | not confused (+0.02) | first measure has the pickup length (sem) |
| `tuplet-3` | 46 | 7 | 68 | 32% (35/110) | 30% (33/110) | 16% (18/110) | 76% | partial | not confused (-0.07) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 85% | **unsupported** — element never emitted | not confused (+0.02) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 17 | 43% (19/44) | 27% (12/44) | 0% (0/44) | 93% | partial | not confused (-0.10) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 100% | partial | not confused (-0.09) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 6 | 37% (13/35) | 14% (5/35) | 17% (6/35) | 86% | **unsupported** | not confused (-0.08) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 88% | **unsupported** — element never emitted | not confused (-2.46) | duration + <time-modification> |
| `tie` | 79 | 14 | 6 | 3% (2/79) | 0% (0/79) | 0% (0/79) | 95% | **unsupported** | **confused** (+0.07) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 0% (0/46) | 0% (0/46) | 91% | **unsupported** — element never emitted | not confused (+0.00) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.06) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.14) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-1.00) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.19) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 92 | 17 | 0 | 0% (0/92) | 0% (0/92) | 0% (0/92) | 78% | **unsupported** — element never emitted | not confused (+0.01) | element on the aligned note |
| `staccato` | 78 | 7 | 0 | 0% (0/78) | 0% (0/78) | 0% (0/78) | 95% | **unsupported** — element never emitted | not confused (-0.10) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `accent` | 35 | 7 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 91% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `tenuto` | 37 | 6 | 0 | 0% (0/37) | 0% (0/37) | 0% (0/37) | 95% | **unsupported** — element never emitted | not confused (-0.06) | element on the aligned note |
| `marcato` | 23 | 3 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (+0.04) | element on the aligned note |
| `fermata` | 128 | 31 | 0 | 0% (0/128) | 0% (0/128) | 0% (0/128) | 85% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 87% | **unsupported** — element never emitted | not confused (-0.10) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.00) | element on the aligned note |
| `dyn-pp` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 40 | 17 | 0 | 0% (0/40) | 0% (0/40) | 0% (0/40) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 10 | 6 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | – | **unsupported** — element never emitted | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 49 | 21 | 0 | 0% (0/49) | 0% (0/49) | 0% (0/49) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 51 | 16 | 0 | 0% (0/51) | 0% (0/51) | 0% (0/51) | – | **unsupported** — element never emitted | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 15 | 4 | 0 | 0% (0/15) | 0% (0/15) | 0% (0/15) | – | **unsupported** — element never emitted | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 39 | 14 | 0 | 0% (0/39) | 0% (0/39) | 0% (0/39) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 29 | 13 | 0 | 0% (0/29) | 0% (0/29) | 0% (0/29) | – | **unsupported** — element never emitted | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `pedal` | 26 | 4 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 0 | 0% (0/112) | 0% (0/112) | 0% (0/112) | 90% | **unsupported** — element never emitted | not confused (-0.23) | element on the aligned note |
| `text-expression` | 36 | 10 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 51 | 48 | 0 | 0% (0/52) | 0% (0/52) | 0% (0/52) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `metronome` | 30 | 28 | 0 | 0% (0/30) | 0% (0/30) | 0% (0/30) | – | **unsupported** — element never emitted | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 16 | 6 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 0 | 0% (0/61) | 0% (0/61) | 0% (0/61) | – | **unsupported** — element never emitted | not confused (-0.07) | same element/value at the aligned measure (+-1) |
| `x-artic-detached-legato` | 4 | 1 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 100% | **unsupported** — element never emitted | not confused (+0.00) | element on the aligned note |
| `x-dyn-fff` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-fp` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `x-dyn-fz` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-ppp` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-sf` | 3 | 2 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `x-dyn-sfp` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |

## Symbols: structure

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `barline-double` | 39 | 13 | 0 | 0% (0/39) | 0% (0/39) | 0% (0/39) | – | **unsupported** — element never emitted | **confused** (+0.09) | same element/value at the aligned measure (+-1) |
| `barline-final` | 70 | 56 | 80 | 95% (54/57) | 91% (52/57) | 81% (46/57) | – | supported | not confused (-0.09) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 11 | 5 | 0 | 0% (0/11) | 0% (0/11) | 0% (0/11) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 17 | 7 | 0 | 0% (0/17) | 0% (0/17) | 0% (0/17) | – | **unsupported** — element never emitted | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `volta-1` | 6 | 4 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `volta-2` | 6 | 4 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `segno` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `coda` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.25) | same element/value at the aligned measure (+-1) |
| `dc` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `ds` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.15) | same element/value at the aligned measure (+-1) |
| `fine` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `system-break` | 196 | 74 | 0 | 0% (0/196) | 0% (0/196) | 0% (0/196) | – | **unsupported** — element never emitted | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `page-break` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `multi-page` | 10 | 5 | 0 | 96% (794/827) | 95% (783/827) | 62% (516/827) | – | supported | not confused (-0.01) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 709 | 13 | 567 | 90% (514/572) | 89% (511/572) | 51% (290/572) | 98% | supported | not confused (-0.29) | lyric on the aligned note |
| `lyrics-multi-verse` | 154 | 3 | 72 | 93% (84/90) | 97% (87/90) | 60% (54/90) | 100% | supported | not confused (-0.03) | lyric on the aligned note |
| `lyrics-melisma` | 25 | 8 | 34 | 72% (21/29) | 69% (20/29) | 48% (14/29) | 100% | partial | not confused (+0.02) | lyric on the aligned note |
| `lyrics-extender` | 16 | 6 | 12 | 40% (6/15) | 33% (5/15) | 27% (4/15) | 100% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-hyphen` | 131 | 13 | 117 | 87% (108/124) | 81% (101/124) | 57% (71/124) | 98% | supported | not confused (-0.01) | lyric on the aligned note |
| `lyrics-elision` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric on the aligned note |
| `lyrics-non-ascii` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric on the aligned note |
| `stanza-text` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

## Generator-specific extra tags (not measured)

Tags outside the taxonomy that the generators record in `meta.json` (detail counts with no MusicXML element of their own, e.g. rest positions or minor-key flags). They are listed for completeness; the symbols they refine are scored above.

| Tag | Occurrences | Items |
|---|---:|---|
| `x-acc-courtesy-paren` | 6 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `x-group-bracket` | 12 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/orchestral-festive-march-9-staves`, `layouts/string-quartet-minuet` |
| `x-group-square` | 1 | `layouts/orchestral-festive-march-9-staves` |
| `x-inverted-mordent` | 5 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola` |
| `x-inverted-turn` | 2 | `marks/mk02-ornaments-fermatas-flute` |
| `x-key-cancel` | 5 | `pitch/pitch-cov-key-changes-organ` |
| `x-key-minor` | 16 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-minor-flats`, `pitch/pitch-cov-keys-minor-sharps` |
| `x-measures` | 202 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song` |
| `x-multi-staff-part` | 5 | `layouts/choir-piano-song-of-rejoicing`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song` |
| `x-parts` | 58 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song` |
| `x-pedal-release` | 23 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `x-portato` | 4 | `marks/mk01-articulations-violin` |
| `x-rest-fermata` | 8 | `rests/rst03-whole-bar-rests-simple`, `rests/rst04-whole-bar-rests-compound`, `rests/rst07-piano-rests`, `rests/rst09-quartet-rests` |
| `x-rest-in-beam` | 36 | `rests/rst08-tuplet-beam-rests` |
| `x-rest-in-tuplet` | 28 | `rests/rst08-tuplet-beam-rests` |
| `x-rest-lowered` | 21 | `rests/rst06-two-voice-rests`, `rests/rst07-piano-rests` |
| `x-rest-multibar-hbar` | 4 | `rests/rst05-multibar-rests` |
| `x-rest-multibar-symbols` | 5 | `rests/rst05-multibar-rests` |
| `x-rest-raised` | 51 | `rests/rst06-two-voice-rests`, `rests/rst07-piano-rests`, `rests/rst08-tuplet-beam-rests` |
| `x-rest-whole-bar-shared-staff` | 4 | `rests/rst06-two-voice-rests` |
| `x-staves` | 64 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song` |
| `x-tie-across-page` | 3 | `time/t08-ties-systems-pages` |
| `x-time-courtesy` | 24 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano`, `time/t04-pickup-song`, `time/t05-triplets-duplets`, `time/t07-nested-tuplets`, `time/t08-ties-systems-pages`, `time/t10-quartet-meters` |
| `x-to-coda` | 1 | `structure/str04-segno-coda-ds` |
| `x-two-voice-staff-measure` | 22 | `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/organ-three-staves-chorale-prelude`, `layouts/two-voices-piano-song-without-words` |

## Layouts

Layout score = mean of part-count match (exact), part-name score and the share of recognised notes that landed in the right part (from eval.mjs). Status from the `scan` input with the same thresholds.

| Layout | Items | Layout score clean | Layout score scan | Layout score scan-severe | Part count ok | Names | Right part | Split violations | Aggregate | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `melody` | 32 | 97% | 96% | 86% | 100% | 88% | 100% | 0 | 0.840 | supported |
| `melody-lyrics` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.899 | supported |
| `piano` | 15 | 100% | 100% | 83% | 100% | 100% | 100% | 0 | 0.904 | supported |
| `voice-piano` | 3 | 100% | 100% | 47% | 100% | 100% | 100% | 0 | 0.952 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-open-satb` | 1 | 100% | 99% | 99% | 100% | 100% | 97% | 0 | 0.915 | supported |
| `choir-sab` | 1 | 100% | 100% | 32% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 9% | 100% | 100% | 100% | 0 | 0.993 | supported |
| `choir-ssaa` | 1 | 98% | 95% | 93% | 100% | 94% | 91% | 0 | 0.949 | supported |
| `choir-piano` | 1 | 100% | 100% | 24% | 100% | 100% | 99% | 0 | 0.978 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.888 | supported |
| `string-quartet` | 6 | 86% | 95% | 57% | 100% | 88% | 98% | 0 | 0.910 | supported |
| `orchestral` | 2 | 92% | 93% | 56% | 100% | 82% | 98% | 0 | 0.965 | supported |
| `lead-sheet` | 2 | 83% | 83% | 50% | 100% | 50% | 100% | 0 | 0.941 | supported |
| `hymnal-stanzas` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `divisi` | 2 | 100% | 99% | 99% | 100% | 97% | 100% | 0 | 0.973 | supported |
| `cross-staff` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `two-voices-one-staff-instrument` | 3 | 72% | 72% | 72% | 67% | 67% | 83% | 1 | 0.830 | partial |
| `percussion-none` | 0 | – | – | – | – | – | – | – | – | no items yet |

## Performance

Source: `mvp/work/eval-coverage-perf.json` (all coverage items, no perf family yet; 168 PDFs; raster native, OCR on, 16 parallel jobs on 192 CPUs, load average 455.1 at the start). Times are the converter (`convert()`) in a Node child process, per page; peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. Pages are rasterised at the resolution of the scan image, so pixel count follows the source dpi.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 4 | 1.145 | 3490 | 10285 | 295.9 | 398 |
| 110 | 2 | 1.379 | 4795 | 4795 | 344.9 | 344.9 |
| 120 | 3 | 1.75 | 2738 | 2779 | 327.9 | 344.9 |
| 150 | 25 | 2.462 | 3012 | 16138 | 294.3 | 570.3 |
| 200 | 32 | 4.083 | 2170 | 9655 | 249.7 | 363.9 |
| 250 | 13 | 6.204 | 2691 | 7814 | 273.5 | 345.7 |
| 300 | 89 | 8.703 | 3111 | 14203 | 306.3 | 456.3 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| ~A3 landscape | 1 | 5.237 | 5507 | 5507 | 525.2 | 525.2 |
| ~A4 | 37 | 4.06 | 3020 | 16138 | 277.5 | 570.3 |
| ~B4 | 15 | 2.642 | 3331 | 6095 | 321.2 | 363.9 |
| A3 landscape | 1 | 4.353 | 4963 | 4963 | 520.5 | 520.5 |
| A4 | 113 | 8.703 | 2939 | 10285 | 300.5 | 456.3 |
| A4 landscape | 1 | 2.178 | 3012 | 3012 | 309.8 | 309.8 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 164 | 8.703 | 2992 | 16138 | 299.9 | 570.3 |
| 2 | 4 | 8.704 | 3007 | 3304 | 414.4 | 456.3 |

**Linear fits.** ms per page = 3214.3 + **81.6 ms per megapixel** × MP per page (n=168, R²=0.01). Peak MB = 276.1 + 4.07 MB per megapixel × total MP (n=168, R²=0.066). Overall: 578 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 1.000 | 1.000 | 0.986 | 4 → 4 | 2641 | 234 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.926 | 0.915 | 0.868 | 4 → 4 | 2598 | 228 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 0.981 | 0.978 | 0.509 | 5 → 5 | 5469 | 289 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.989 | 0.359 | 3 → 3 | 3630 | 247 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.964 | 0.949 | 0.934 | 4 → 4 | 2639 | 245 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 0.993 | 0.993 | 0.298 | 4 → 4 | 2687 | 231 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.940 | 4 → 4 | 4849 | 307 |
| `layouts/divisi-strings-lament` | divisi | 0.967 | 0.959 | 0.934 | 4 → 4 | 2789 | 263 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 0.995 | 0.996 | 0.988 | 4 → 4 | 4668 | 249 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.879 | 1 → 1 | 4205 | 241 |
| `layouts/melody-cello-elegy-2page` | melody | 0.824 | 0.855 | 0.691 | 1 → 1 | 1829 | 266 |
| `layouts/melody-flute-air` | melody | 0.941 | 0.957 | 0.961 | 1 → 1 | 1766 | 233 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 0.887 | 0.887 | 0.841 | 1 → 1 | 3174 | 242 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.972 | 0.957 | 0.796 | 9 → 9 | 3755 | 513 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.965 | 0.942 | 0.774 | 1 → 1 | 3113 | 248 |
| `layouts/piano-grand-staff-prelude` | piano | 0.876 | 0.920 | 0.910 | 1 → 1 | 1877 | 255 |
| `layouts/string-quartet-minuet` | string-quartet | 0.774 | 0.768 | 0.770 | 4 → 4 | 3958 | 318 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.715 | 1 → 1 | 1861 | 219 |
| `layouts/voice-piano-night-song` | voice-piano | 0.971 | 0.923 | 0.424 | 2 → 2 | 3044 | 233 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.971 | 1 → 1 | 1879 | 235 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 2628 | 215 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.978 | 0.944 | 0.789 | 1 → 1 | 2609 | 239 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.933 | 0.910 | 0.839 | 1 → 1 | 2090 | 239 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.750 | 0.736 | 0.893 | 1 → 1 | 2191 | 243 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.957 | 0.961 | 0.367 | 1 → 1 | 4359 | 244 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.984 | 0.997 | 0.858 | 2 → 2 | 1960 | 246 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.963 | 0.923 | 4 → 4 | 2401 | 229 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.935 | 0.905 | 1 → 1 | 1825 | 240 |
| `notes/nt01-note-values` | melody | 0.814 | 0.827 | 0.681 | 1 → 1 | 1984 | 238 |
| `notes/nt02-dots` | melody | 0.841 | 0.824 | 0.797 | 1 → 1 | 1911 | 248 |
| `notes/nt03-chords` | piano | 0.894 | 0.840 | 0.859 | 1 → 1 | 1894 | 246 |
| `notes/nt04-beams` | melody | 0.909 | 0.915 | 0.901 | 1 → 1 | 2138 | 250 |
| `notes/nt05-flags-stems` | melody | 0.812 | 0.806 | 0.759 | 1 → 1 | 2954 | 241 |
| `notes/nt06-ledger-lines` | piano | 0.946 | 0.913 | 0.913 | 1 → 1 | 1842 | 248 |
| `notes/nt07-grace-notes` | melody | 0.924 | 0.806 | 0.730 | 1 → 1 | 1686 | 254 |
| `notes/nt08-cue-notes` | melody | 0.906 | 0.944 | 0.903 | 1 → 1 | 1466 | 235 |
| `notes/nt09-tremolos` | piano | 0.720 | 0.722 | 0.680 | 1 → 1 | 1729 | 246 |
| `notes/nt10-piano-etude` | piano | 0.939 | 0.930 | 0.914 | 1 → 1 | 1957 | 252 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.851 | 0.832 | 0.813 | 1 → 1 | 1659 | 238 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.819 | 0.822 | 0.749 | 1 → 1 | 2063 | 246 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.907 | 0.982 | 0.367 | 1 → 1 | 1789 | 234 |
| `pitch/pitch-cov-clefs-all` | melody | 0.737 | 0.726 | 0.676 | 1 → 1 | 2842 | 227 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.759 | 0.959 | 0.756 | 4 → 4 | 2886 | 252 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.850 | 0.834 | 0.730 | 1 → 1 | 2038 | 255 |
| `pitch/pitch-cov-keys-major-flats` | piano | 0.881 | 0.883 | 0.578 | 1 → 1 | 3991 | 242 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.890 | 0.810 | 0.785 | 1 → 1 | 1655 | 221 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.851 | 0.827 | 0.779 | 1 → 1 | 2249 | 235 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.589 | 0.564 | 0.612 | 1 → 1 | 2961 | 256 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 0.838 | 0.838 | 0.787 | 1 → 1 | 1579 | 234 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.809 | 0.795 | 0.803 | 1 → 1 | 1781 | 258 |
| `rests/rst01-rest-values` | melody | 0.809 | 0.735 | 0.676 | 1 → 1 | 3170 | 246 |
| `rests/rst02-dotted-rests` | melody | 0.832 | 0.848 | 0.744 | 1 → 1 | 2206 | 230 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.768 | 0.777 | 0.579 | 1 → 1 | 1811 | 238 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.776 | 0.786 | 0.811 | 1 → 1 | 2578 | 236 |
| `rests/rst05-multibar-rests` | melody | 0.761 | 0.737 | 0.622 | 1 → 1 | 1920 | 239 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.610 | 0.623 | 0.620 | 1 → 2 | 1672 | 232 |
| `rests/rst07-piano-rests` | piano | 0.905 | 0.906 | 0.836 | 1 → 1 | 2048 | 247 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.838 | 0.804 | 0.367 | 1 → 1 | 1960 | 235 |
| `rests/rst09-quartet-rests` | string-quartet | 0.995 | 0.961 | 0.953 | 4 → 4 | 3628 | 314 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 1676 | 231 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.754 | 1 → 1 | 2068 | 235 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.448 | 4 → 4 | 3688 | 336 |
| `structure/str04-segno-coda-ds` | melody | 0.878 | 0.883 | 0.909 | 1 → 1 | 1678 | 236 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.367 | 1 → 1 | 1561 | 242 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.972 | 0.935 | 0.201 | 2 → 2 | 7383 | 400 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.973 | 0.664 | 7 → 7 | 5711 | 546 |
| `time/t01-simple-meters` | melody | 0.858 | 0.866 | 0.847 | 1 → 1 | 1987 | 248 |
| `time/t02-compound-irregular` | melody | 0.875 | 0.875 | 0.897 | 1 → 1 | 2790 | 251 |
| `time/t03-common-cut-piano` | piano | 0.961 | 0.974 | 0.940 | 1 → 1 | 1701 | 240 |
| `time/t04-pickup-song` | melody-lyrics | 0.911 | 0.911 | 0.926 | 1 → 1 | 4574 | 224 |
| `time/t05-triplets-duplets` | melody | 0.794 | 0.824 | 0.805 | 1 → 1 | 2184 | 246 |
| `time/t06-quint-sext-sept` | melody | 0.938 | 0.912 | 0.834 | 1 → 1 | 3618 | 230 |
| `time/t07-nested-tuplets` | melody | 0.807 | 0.772 | 0.810 | 1 → 1 | 3569 | 237 |
| `time/t08-ties-systems-pages` | piano | 0.948 | 0.970 | 0.404 | 1 → 1 | 2411 | 269 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.871 | 0.871 | 0.744 | 1 → 1 | 2771 | 213 |
| `time/t10-quartet-meters` | string-quartet | 0.857 | 0.830 | 0.617 | 4 → 4 | 2226 | 253 |
