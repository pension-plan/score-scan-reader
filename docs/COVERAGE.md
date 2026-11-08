# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 13:37 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 13:37, app source hash `092a734b6900`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 81 items, 243 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

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

**Totals:** 62 supported, 42 partial, 50 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 50% | **unsupported** | not confused (-0.15) | duration of the aligned note (sem) |
| `note-whole` | 163 | 37 | 179 | 81% (152/188) | 78% (146/188) | 43% (81/188) | 84% | partial | not confused (+0.00) | duration of the aligned note (sem) |
| `note-half` | 1351 | 75 | 1379 | 92% (1354/1471) | 85% (1253/1471) | 43% (627/1471) | 93% | supported | not confused (-0.02) | duration of the aligned note (sem) |
| `note-quarter` | 4025 | 80 | 4431 | 93% (4094/4426) | 93% (4094/4426) | 75% (3302/4426) | 95% | supported | not confused (-0.07) | duration of the aligned note (sem) |
| `note-8th` | 1526 | 61 | 1588 | 81% (1301/1608) | 79% (1267/1608) | 66% (1065/1608) | 86% | partial | not confused (+0.00) | duration of the aligned note (sem) |
| `note-16th` | 651 | 22 | 626 | 81% (529/651) | 81% (529/651) | 69% (450/651) | 90% | supported | not confused (+0.00) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 103 | 80% (90/113) | 82% (93/113) | 43% (49/113) | 91% | supported | not confused (-0.02) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 30 | 32% (23/71) | 39% (28/71) | 6% (4/71) | 79% | partial | not confused (-0.00) | duration of the aligned note (sem) |
| `dot` | 295 | 49 | 329 | 91% (271/299) | 92% (275/299) | 61% (181/299) | 96% | supported | not confused (+0.00) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 6 | 27% (4/15) | 27% (4/15) | 7% (1/15) | 93% | partial | **confused** (+0.13) | <dot/> count + duration |
| `chord` | 608 | 29 | 1681 | 94% (1560/1666) | 93% (1555/1666) | 71% (1189/1666) | 94% | supported | not confused (-0.01) | element on the aligned note |
| `beam` | 703 | 56 | 0 | 0% (0/2064) | 0% (0/2064) | 0% (0/2064) | 88% | **unsupported** — element never emitted | not confused (+0.00) | element on the aligned note |
| `flag` | 308 | 31 | 1526 | 62% (191/308) | 63% (193/308) | 47% (146/308) | 81% | partial | not confused (+0.03) | duration of the flagged note (sem) |
| `stem-up` | 2653 | 67 | 2623 | 90% (2398/2653) | 89% (2359/2653) | 76% (2018/2653) | 89% | supported | not confused (-0.09) | element on the aligned note |
| `stem-down` | 4155 | 72 | 3950 | 92% (3836/4155) | 91% (3800/4155) | 78% (3224/4155) | 93% | supported | not confused (-0.20) | element on the aligned note |
| `ledger-above` | 601 | 58 | 589 | 93% (561/601) | 91% (544/601) | 80% (478/601) | 91% | supported | not confused (-0.03) | pitch (sem) |
| `ledger-below` | 374 | 45 | 374 | 95% (356/374) | 95% (357/374) | 78% (293/374) | 95% | supported | not confused (-0.01) | pitch (sem) |
| `grace` | 58 | 2 | 8 | 45% (26/58) | 10% (6/58) | 3% (2/58) | 10% | **unsupported** | not confused (-0.04) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 19% | **unsupported** | not confused (-0.03) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.20) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 46% | **unsupported** — element never emitted | not confused (-0.83) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 100% (2/2) | 100% (2/2) | 100% (2/2) | 100% | supported — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 3 | 100% (3/3) | 100% (3/3) | 0% (0/3) | 100% | supported | not confused (-0.47) | aligned rest with the same duration (sem) |
| `rest-half` | 36 | 15 | 30 | 78% (28/36) | 72% (26/36) | 56% (20/36) | 75% | partial | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-quarter` | 183 | 33 | 136 | 77% (140/183) | 71% (130/183) | 44% (80/183) | 76% | partial | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-8th` | 124 | 16 | 114 | 77% (96/124) | 82% (102/124) | 66% (82/124) | 92% | supported | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 59 | 65% (39/60) | 67% (40/60) | 42% (25/60) | 90% | partial | not confused (+0.02) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 15 | 91% (20/22) | 64% (14/22) | 14% (3/22) | 68% | partial | **confused** (+0.11) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 1 | 60% (6/10) | 10% (1/10) | 0% (0/10) | 20% | **unsupported** | not confused (+0.11) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 28 | 83% (25/30) | 93% (28/30) | 53% (16/30) | 93% | supported | not confused (+0.05) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 202 | 14 | 209 | 90% (181/202) | 83% (168/202) | 48% (97/202) | 90% | supported | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 0 | 67% (6/9) | 67% (6/9) | 0% (0/9) | – | partial — <multiple-rest> never emitted | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 105 | 71 | 106 | 99% (104/105) | 99% (104/105) | 87% (91/105) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 63 | 45 | 62 | 95% (60/63) | 97% (61/63) | 81% (51/63) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 14 | 13 | 13 | 93% (13/14) | 93% (13/14) | 93% (13/14) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.64) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 6 | 5 | 5 | 83% (5/6) | 83% (5/6) | 67% (4/6) | – | supported | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.14) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.93) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 17 | 48% (13/27) | 56% (15/27) | 7% (2/27) | – | partial | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 40 | 37 | 50 | 100% (37/37) | 97% (36/37) | 92% (34/37) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 18 | 15 | 31 | 87% (13/15) | 87% (13/15) | 73% (11/15) | – | supported | **confused** (+0.14) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 12 | 9 | 25 | 100% (9/9) | 89% (8/9) | 89% (8/9) | – | supported | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 6 | 5 | 8 | 83% (5/6) | 83% (5/6) | 83% (5/6) | – | supported | not confused (+0.00) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 4 | 4 | 3 | 75% (3/4) | 75% (3/4) | 25% (1/4) | – | partial | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 2 | 67% (2/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 0 | 50% (1/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 16 | 13 | 19 | 100% (13/13) | 100% (13/13) | 92% (12/13) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 7 | 7 | 10 | 100% (7/7) | 100% (7/7) | 100% (7/7) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 9 | 8 | 11 | 100% (8/8) | 100% (8/8) | 75% (6/8) | – | supported | **confused** (+0.17) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 0% (0/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 34 | 6 | 23 | 79% (27/34) | 68% (23/34) | 41% (14/34) | – | partial | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 78 | 22 | 68 | 60% (47/78) | 72% (56/78) | 41% (32/78) | 72% | partial | not confused (+0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 25 | 75% (21/28) | 82% (23/28) | 93% (26/28) | 82% | supported | not confused (-0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 53 | 10 | 46 | 81% (43/53) | 83% (44/53) | 62% (33/53) | 83% | supported | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 2 | 43% (3/7) | 29% (2/7) | 0% (0/7) | 57% | partial | not confused (-0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 4 | 40% (2/5) | 80% (4/5) | 40% (2/5) | 80% | supported | not confused (-0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 0 | 22% (2/9) | 33% (3/9) | 56% (5/9) | 33% | partial — <accidental> never emitted | not confused (+0.04) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.43) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 0 | 0% (0/22) | 0% (0/22) | 0% (0/22) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.40) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 0 | 0% (0/12) | 0% (0/12) | 0% (0/12) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.32) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | unclear (+0.07) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (+0.04) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 14 | 9 | 11 | 91% (10/11) | 73% (8/11) | 64% (7/11) | – | partial | **confused** (+0.10) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 38 | 25 | 44 | 93% (27/29) | 100% (29/29) | 66% (19/29) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 69 | 54 | 104 | 95% (59/62) | 92% (57/62) | 82% (51/62) | – | supported | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 4 | 100% (4/4) | 100% (4/4) | 50% (2/4) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 4 | 100% (4/4) | 100% (4/4) | 25% (1/4) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 23 | 89% (16/18) | 94% (17/18) | 44% (8/18) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 60% (3/5) | – | supported | not confused (-0.11) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 5 | 80% (4/5) | 100% (5/5) | 20% (1/5) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 3 | 100% (3/3) | 100% (3/3) | 33% (1/3) | – | supported | not confused (-0.12) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 7 | 100% (4/4) | 100% (4/4) | 75% (3/4) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 7 | 100% (4/4) | 100% (4/4) | 100% (4/4) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 11 | 6 | 12 | 88% (7/8) | 88% (7/8) | 75% (6/8) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 10 | 86% (6/7) | 86% (6/7) | 43% (3/7) | – | supported | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 110 | 93% (83/89) | 96% (85/89) | 53% (47/89) | – | supported | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 9 | 9 | 7 | 67% (6/9) | 67% (6/9) | 56% (5/9) | – | partial | not confused (+0.06) | first measure has the pickup length (sem) |
| `tuplet-3` | 76 | 8 | 166 | 68% (135/200) | 68% (135/200) | 42% (83/200) | 93% | partial | not confused (+0.02) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 100% | **unsupported** — element never emitted | not confused (-0.04) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 29 | 45% (20/44) | 45% (20/44) | 34% (15/44) | 93% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 89% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 21 | 60% (21/35) | 60% (21/35) | 40% (14/35) | 100% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 100% | **unsupported** — element never emitted | not confused (+0.00) | duration + <time-modification> |
| `tie` | 79 | 14 | 26 | 29% (23/79) | 27% (21/79) | 10% (8/79) | 100% | partial | not confused (-0.03) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 2% (1/46) | 2% (1/46) | 100% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | unclear (+0.08) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 4 | 100% (4/4) | 100% (4/4) | 25% (1/4) | – | supported | not confused (-0.20) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | not confused (-0.28) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.05) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 100 | 20 | 27 | 18% (18/100) | 15% (15/100) | 11% (11/100) | 81% | **unsupported** | not confused (+0.04) | element on the aligned note |
| `staccato` | 78 | 7 | 0 | 0% (0/78) | 0% (0/78) | 0% (0/78) | 99% | **unsupported** — element never emitted | not confused (-0.08) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 89% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `accent` | 43 | 8 | 0 | 0% (0/43) | 0% (0/43) | 0% (0/43) | 79% | **unsupported** — element never emitted | **confused** (+0.13) | element on the aligned note |
| `tenuto` | 37 | 6 | 0 | 0% (0/37) | 0% (0/37) | 0% (0/37) | 97% | **unsupported** — element never emitted | not confused (-0.07) | element on the aligned note |
| `marcato` | 23 | 3 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (+0.04) | element on the aligned note |
| `fermata` | 130 | 32 | 91 | 72% (94/130) | 60% (78/130) | 14% (18/130) | 95% | partial | not confused (-0.01) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 93% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `dyn-pp` | 8 | 5 | 8 | 75% (6/8) | 75% (6/8) | 50% (4/8) | – | partial | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 43 | 19 | 33 | 58% (25/43) | 77% (33/43) | 42% (18/43) | – | partial | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 13 | 9 | 15 | 85% (11/13) | 100% (13/13) | 23% (3/13) | – | supported | **confused** (+0.15) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 54 | 25 | 29 | 87% (47/54) | 43% (23/54) | 31% (17/54) | – | partial | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 56 | 18 | 43 | 77% (43/56) | 77% (43/56) | 63% (35/56) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 16 | 5 | 14 | 75% (12/16) | 88% (14/16) | 81% (13/16) | – | supported | **confused** (+0.12) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 3 | 67% (4/6) | 50% (3/6) | 17% (1/6) | – | partial | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 43 | 18 | 37 | 86% (37/43) | 86% (37/43) | 26% (11/43) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 31 | 15 | 28 | 84% (26/31) | 84% (26/31) | 19% (6/31) | – | supported | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `pedal` | 28 | 5 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 0 | 0% (0/112) | 0% (0/112) | 0% (0/112) | 92% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `text-expression` | 45 | 11 | 7 | 14% (5/35) | 20% (7/35) | 14% (5/35) | – | partial | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 59 | 53 | 55 | 66% (45/68) | 68% (46/68) | 44% (30/68) | – | partial | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `metronome` | 36 | 33 | 38 | 86% (31/36) | 89% (32/36) | 61% (22/36) | – | supported | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 16 | 6 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 0 | 0% (0/61) | 0% (0/61) | 0% (0/61) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `x-artic-detached-legato` | 4 | 1 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 100% | **unsupported** — element never emitted | not confused (+0.00) | element on the aligned note |
| `x-dyn-fff` | 1 | 1 | 0 | 100% (1/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-fp` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 0% (0/1) | – | supported — low n (1) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `x-dyn-fz` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 0% (0/1) | – | supported — low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-ppp` | 1 | 1 | 0 | 100% (1/1) | 0% (0/1) | 100% (1/1) | – | **unsupported** — low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `x-dyn-sf` | 3 | 2 | 3 | 100% (3/3) | 100% (3/3) | 33% (1/3) | – | supported | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `x-dyn-sfp` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.02) | same element/value at the aligned measure (+-1) |

## Symbols: structure

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `barline-double` | 42 | 14 | 0 | 0% (0/42) | 0% (0/42) | 0% (0/42) | – | **unsupported** — element never emitted | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `barline-final` | 94 | 80 | 143 | 96% (78/81) | 94% (76/81) | 89% (72/81) | – | supported | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 25 | 6 | 0 | 0% (0/25) | 0% (0/25) | 0% (0/25) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 32 | 8 | 0 | 0% (0/32) | 0% (0/32) | 0% (0/32) | – | **unsupported** — element never emitted | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `volta-1` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `volta-2` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `segno` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `coda` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `dc` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `ds` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (+0.09) | same element/value at the aligned measure (+-1) |
| `fine` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `system-break` | 226 | 80 | 0 | 0% (0/226) | 0% (0/226) | 0% (0/226) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `page-break` | 19 | 6 | 0 | 0% (0/19) | 0% (0/19) | 0% (0/19) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `multi-page` | 22 | 6 | 0 | 97% (1859/1908) | 95% (1819/1908) | 89% (1699/1908) | – | supported | not confused (+0.01) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 895 | 15 | 615 | 89% (555/624) | 90% (561/624) | 61% (383/624) | 98% | supported | not confused (-0.28) | lyric on the aligned note |
| `lyrics-multi-verse` | 288 | 5 | 125 | 82% (117/142) | 81% (115/142) | 70% (99/142) | 99% | supported | not confused (-0.03) | lyric on the aligned note |
| `lyrics-melisma` | 39 | 10 | 36 | 79% (26/33) | 73% (24/33) | 55% (18/33) | 97% | partial | not confused (-0.01) | lyric on the aligned note |
| `lyrics-extender` | 27 | 8 | 16 | 63% (12/19) | 63% (12/19) | 47% (9/19) | 100% | partial | not confused (-0.02) | lyric on the aligned note |
| `lyrics-hyphen` | 203 | 15 | 157 | 79% (127/160) | 84% (134/160) | 72% (115/160) | 98% | supported | not confused (-0.03) | lyric on the aligned note |
| `lyrics-elision` | 11 | 1 | 9 | 63% (5/8) | 50% (4/8) | 63% (5/8) | 100% | partial | not confused (+0.00) | lyric on the aligned note |
| `lyrics-non-ascii` | 30 | 2 | 3 | 0% (0/19) | 0% (0/19) | 0% (0/19) | 100% | **unsupported** | not confused (+0.00) | lyric on the aligned note |
| `stanza-text` | 7 | 2 | – | 82% (150/183) | 80% (148/185) | 79% (135/171) | – | supported | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

## Generator-specific extra tags (not measured)

Tags outside the taxonomy that the generators record in `meta.json` (detail counts with no MusicXML element of their own, e.g. rest positions or minor-key flags). They are listed for completeness; the symbols they refine are scored above.

| Tag | Occurrences | Items |
|---|---:|---|
| `x-acc-courtesy-paren` | 6 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `x-cross-staff-note` | 29 | `layouts/cross-staff-piano-arpeggio-study` |
| `x-group-bracket` | 12 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/orchestral-festive-march-9-staves`, `layouts/string-quartet-minuet` |
| `x-group-square` | 1 | `layouts/orchestral-festive-march-9-staves` |
| `x-inverted-mordent` | 5 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola` |
| `x-inverted-turn` | 2 | `marks/mk02-ornaments-fermatas-flute` |
| `x-key-cancel` | 5 | `pitch/pitch-cov-key-changes-organ` |
| `x-key-minor` | 16 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-minor-flats`, `pitch/pitch-cov-keys-minor-sharps` |
| `x-measures` | 237 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/cross-staff-piano-arpeggio-study`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages`, `percussion/perc01-parade-flute-snare-drumset` |
| `x-multi-staff-part` | 6 | `layouts/choir-piano-song-of-rejoicing`, `layouts/cross-staff-piano-arpeggio-study`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song` |
| `x-notehead-x` | 58 | `percussion/perc01-parade-flute-snare-drumset` |
| `x-noteheads` | 2249 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/cross-staff-piano-arpeggio-study`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages`, `percussion/perc01-parade-flute-snare-drumset` |
| `x-parts` | 64 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/cross-staff-piano-arpeggio-study`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages`, `percussion/perc01-parade-flute-snare-drumset` |
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
| `x-staff-1-line` | 1 | `percussion/perc01-parade-flute-snare-drumset` |
| `x-staves` | 71 | `layouts/choir-closed-satb-light-of-morning`, `layouts/choir-open-satb-gloria`, `layouts/choir-piano-song-of-rejoicing`, `layouts/choir-sab-summer-song`, `layouts/choir-ssaa-winter-night`, `layouts/choir-ttbb-evening-bells`, `layouts/cross-staff-piano-arpeggio-study`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/hymnal-stanzas-light-of-ages`, `layouts/lead-sheet-long-road`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/orchestral-festive-march-9-staves`, `layouts/organ-three-staves-chorale-prelude`, `layouts/piano-grand-staff-prelude`, `layouts/string-quartet-minuet`, `layouts/two-voices-piano-song-without-words`, `layouts/voice-piano-night-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages`, `percussion/perc01-parade-flute-snare-drumset` |
| `x-tie-across-page` | 3 | `time/t08-ties-systems-pages` |
| `x-time-courtesy` | 24 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano`, `time/t04-pickup-song`, `time/t05-triplets-duplets`, `time/t07-nested-tuplets`, `time/t08-ties-systems-pages`, `time/t10-quartet-meters` |
| `x-to-coda` | 2 | `structure/str04-segno-coda-ds`, `structure/str08-variations-twelve-pages-piano` |
| `x-two-voice-staff-measure` | 30 | `layouts/cross-staff-piano-arpeggio-study`, `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament`, `layouts/organ-three-staves-chorale-prelude`, `layouts/two-voices-piano-song-without-words` |
| `x-unpitched` | 139 | `percussion/perc01-parade-flute-snare-drumset` |

## Layouts

Layout score = mean of part-count match (exact), part-name score and the share of recognised notes that landed in the right part (from eval.mjs). Status from the `scan` input with the same thresholds.

| Layout | Items | Layout score clean | Layout score scan | Layout score scan-severe | Part count ok | Names | Right part | Split violations | Aggregate | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `melody` | 32 | 97% | 96% | 88% | 100% | 88% | 100% | 0 | 0.896 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.980 | supported |
| `piano` | 16 | 100% | 100% | 88% | 100% | 100% | 100% | 0 | 0.954 | supported |
| `voice-piano` | 3 | 100% | 100% | 77% | 100% | 100% | 100% | 0 | 0.957 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 99% | 0 | 0.925 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 5% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.992 | supported |
| `choir-piano` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.961 | supported |
| `string-quartet` | 6 | 87% | 95% | 57% | 100% | 88% | 98% | 0 | 0.970 | supported |
| `orchestral` | 2 | 92% | 93% | 89% | 100% | 82% | 98% | 0 | 0.966 | supported |
| `lead-sheet` | 2 | 83% | 83% | 67% | 100% | 50% | 100% | 0 | 0.940 | supported |
| `hymnal-stanzas` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.999 | supported |
| `divisi` | 2 | 100% | 96% | 99% | 100% | 88% | 100% | 0 | 0.970 | supported |
| `cross-staff` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.889 | supported |
| `two-voices-one-staff-instrument` | 3 | 89% | 89% | 89% | 100% | 67% | 100% | 0 | 0.931 | supported |
| `percussion-none` | 1 | 44% | 44% | 44% | 0% | 33% | 100% | 0 | 0.628 | partial |

## Performance

Source: `mvp/work/eval-coverage.json` (all coverage items, no perf family yet; 243 PDFs; raster 200 dpi, OCR on, 8 parallel jobs on 192 CPUs, load average 42.6 at the start). Times are the converter (`convert()`) in a Node child process, per page; peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. With a fixed raster dpi the source scan dpi changes image quality, not pixel count; use `--dpi native` (raster at the scan resolution) or `--dpi app` (browser app: 2300 px wide) to measure the dpi effect.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 4 | 4.582 | 2028 | 4632 | 276.8 | 318.2 |
| 110 | 2 | 4.555 | 2556 | 2556 | 249 | 249 |
| 120 | 8 | 3.869 | 2220 | 5050 | 259.6 | 504.3 |
| 150 | 40 | 4.31 | 2309 | 18589 | 270.2 | 619.3 |
| 200 | 43 | 4.002 | 2062 | 4426 | 258.8 | 655.5 |
| 240 | 3 | 3.873 | 2674 | 2924 | 240.6 | 257.2 |
| 250 | 17 | 3.87 | 2141 | 4879 | 251.1 | 493.1 |
| 300 | 126 | 3.869 | 1921 | 4565 | 239.3 | 598 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| ~A3 landscape | 1 | 9.314 | 3249 | 3249 | 380 | 380 |
| ~A4 | 37 | 4.277 | 2043 | 18589 | 259.6 | 619.3 |
| ~B4 | 19 | 4.697 | 2309 | 7121 | 288 | 492.4 |
| A3 landscape | 1 | 7.742 | 12204 | 12204 | 561.7 | 561.7 |
| A4 | 184 | 3.869 | 1966 | 5050 | 240.8 | 655.5 |
| A4 landscape | 1 | 3.871 | 2288 | 2288 | 260.8 | 260.8 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 227 | 3.869 | 2028 | 18589 | 242.1 | 619.3 |
| 2 | 10 | 3.869 | 3158 | 5050 | 470.4 | 512.5 |
| 5 | 3 | 3.869 | 3504 | 4153 | 598 | 655.5 |
| 12 | 3 | 3.869 | 1655 | 1667 | 536.3 | 557.1 |

**Linear fits.** ms per page = -1519.1 + **975.28 ms per megapixel** × MP per page (n=243, R²=0.098). Peak MB = 227.2 + 9.12 MB per megapixel × total MP (n=243, R²=0.349). Overall: 596 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 2135 | 239 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.925 | 0.879 | 4 → 4 | 2813 | 262 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 1.000 | 1.000 | 0.972 | 5 → 5 | 3973 | 322 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 2674 | 233 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.996 | 0.992 | 0.982 | 4 → 4 | 2141 | 240 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.348 | 4 → 4 | 2146 | 234 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.884 | 0.889 | 0.794 | 1 → 1 | 1718 | 242 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 4879 | 313 |
| `layouts/divisi-strings-lament` | divisi | 0.974 | 0.953 | 0.938 | 4 → 4 | 2271 | 257 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 3282 | 267 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 2924 | 241 |
| `layouts/melody-cello-elegy-2page` | melody | 0.886 | 0.843 | 0.713 | 1 → 1 | 1475 | 257 |
| `layouts/melody-flute-air` | melody | 0.959 | 0.977 | 0.961 | 1 → 1 | 1658 | 236 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 2171 | 247 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.973 | 0.957 | 0.896 | 9 → 9 | 3958 | 493 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.987 | 0.948 | 0.770 | 1 → 1 | 2292 | 232 |
| `layouts/piano-grand-staff-prelude` | piano | 0.899 | 0.954 | 0.941 | 1 → 1 | 1866 | 227 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.986 | 0.774 | 4 → 4 | 4107 | 324 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1684 | 223 |
| `layouts/voice-piano-night-song` | voice-piano | 0.979 | 0.931 | 0.459 | 2 → 2 | 2294 | 257 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.982 | 0.977 | 0.890 | 1 → 1 | 2507 | 236 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.975 | 0.975 | 0.943 | 1 → 1 | 3048 | 259 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 1647 | 218 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1578 | 256 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.984 | 0.968 | 0.775 | 1 → 1 | 1816 | 231 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.944 | 0.949 | 0.842 | 1 → 1 | 2366 | 242 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.982 | 0.956 | 0.723 | 1 → 1 | 2099 | 236 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.970 | 0.960 | 0.836 | 1 → 1 | 2158 | 262 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.980 | 0.993 | 0.904 | 2 → 2 | 2228 | 231 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.977 | 0.911 | 4 → 4 | 2285 | 260 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.920 | 0.895 | 1 → 1 | 2013 | 243 |
| `notes/nt01-note-values` | melody | 0.895 | 0.919 | 0.672 | 1 → 1 | 1939 | 251 |
| `notes/nt02-dots` | melody | 0.940 | 0.922 | 0.875 | 1 → 1 | 1975 | 231 |
| `notes/nt03-chords` | piano | 0.974 | 0.970 | 0.900 | 1 → 1 | 1921 | 233 |
| `notes/nt04-beams` | melody | 0.985 | 0.971 | 0.975 | 1 → 1 | 2062 | 261 |
| `notes/nt05-flags-stems` | melody | 0.845 | 0.849 | 0.755 | 1 → 1 | 1869 | 231 |
| `notes/nt06-ledger-lines` | piano | 1.000 | 0.953 | 0.953 | 1 → 1 | 1780 | 240 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.771 | 0.730 | 1 → 1 | 1913 | 248 |
| `notes/nt08-cue-notes` | melody | 0.960 | 0.946 | 0.947 | 1 → 1 | 1700 | 239 |
| `notes/nt09-tremolos` | piano | 0.719 | 0.751 | 0.635 | 1 → 1 | 1827 | 219 |
| `notes/nt10-piano-etude` | piano | 0.992 | 0.985 | 0.954 | 1 → 1 | 1831 | 229 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.636 | 3 → 2 | 2131 | 230 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.976 | 0.977 | 0.869 | 1 → 1 | 1860 | 239 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.857 | 0.927 | 0.843 | 1 → 1 | 1822 | 254 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1713 | 249 |
| `pitch/pitch-cov-clefs-all` | melody | 0.741 | 0.727 | 0.733 | 1 → 1 | 1766 | 260 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.769 | 0.955 | 0.756 | 4 → 4 | 2030 | 234 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.989 | 0.974 | 0.806 | 1 → 1 | 1956 | 265 |
| `pitch/pitch-cov-keys-major-flats` | piano | 1.000 | 1.000 | 0.676 | 1 → 1 | 1784 | 241 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.992 | 0.911 | 0.941 | 1 → 1 | 1795 | 217 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.967 | 0.971 | 0.885 | 1 → 1 | 1809 | 225 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.604 | 0.541 | 0.557 | 1 → 1 | 2323 | 260 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 0.838 | 0.838 | 0.838 | 1 → 1 | 1753 | 242 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.845 | 0.807 | 0.803 | 1 → 1 | 1860 | 258 |
| `rests/rst01-rest-values` | melody | 0.857 | 0.799 | 0.684 | 1 → 1 | 1855 | 260 |
| `rests/rst02-dotted-rests` | melody | 0.934 | 0.948 | 0.786 | 1 → 1 | 2056 | 231 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.904 | 0.904 | 0.701 | 1 → 1 | 1977 | 254 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.935 | 1.000 | 0.903 | 1 → 1 | 1970 | 214 |
| `rests/rst05-multibar-rests` | melody | 0.881 | 0.807 | 0.626 | 1 → 1 | 2080 | 226 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.863 | 0.840 | 1 → 1 | 1867 | 244 |
| `rests/rst07-piano-rests` | piano | 0.954 | 0.959 | 0.932 | 1 → 1 | 2019 | 220 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.863 | 0.840 | 0.367 | 1 → 1 | 2358 | 257 |
| `rests/rst09-quartet-rests` | string-quartet | 0.990 | 0.976 | 0.921 | 4 → 4 | 3607 | 327 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 1692 | 220 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.980 | 1 → 1 | 1854 | 258 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.466 | 4 → 4 | 4302 | 389 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 2064 | 213 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.481 | 1 → 1 | 2143 | 254 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.976 | 0.946 | 0.842 | 2 → 2 | 3416 | 505 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.975 | 0.957 | 7 → 7 | 3504 | 517 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.996 | 0.983 | 0.962 | 1 → 1 | 1667 | 557 |
| `time/t01-simple-meters` | melody | 0.962 | 0.961 | 0.855 | 1 → 1 | 2059 | 238 |
| `time/t02-compound-irregular` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 2143 | 238 |
| `time/t03-common-cut-piano` | piano | 0.991 | 1.000 | 0.931 | 1 → 1 | 2188 | 241 |
| `time/t04-pickup-song` | melody-lyrics | 0.953 | 0.966 | 0.955 | 1 → 1 | 2265 | 230 |
| `time/t05-triplets-duplets` | melody | 0.848 | 0.875 | 0.824 | 1 → 1 | 2043 | 241 |
| `time/t06-quint-sext-sept` | melody | 0.971 | 0.968 | 0.917 | 1 → 1 | 1679 | 233 |
| `time/t07-nested-tuplets` | melody | 0.819 | 0.812 | 0.833 | 1 → 1 | 1746 | 234 |
| `time/t08-ties-systems-pages` | piano | 0.984 | 0.992 | 0.408 | 1 → 1 | 1592 | 309 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.933 | 0.933 | 0.765 | 1 → 1 | 1732 | 254 |
| `time/t10-quartet-meters` | string-quartet | 0.987 | 0.948 | 0.649 | 4 → 4 | 2562 | 251 |
