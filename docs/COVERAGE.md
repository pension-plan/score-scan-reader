# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 12:52 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 12:52, app source hash `201470bddc41`, OCR on, raster 200 dpi).
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

**Totals:** 38 supported, 52 partial, 64 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 75% | **unsupported** | unclear (+0.06) | duration of the aligned note (sem) |
| `note-whole` | 163 | 37 | 154 | 59% (110/188) | 55% (104/188) | 37% (70/188) | 68% | partial | not confused (-0.03) | duration of the aligned note (sem) |
| `note-half` | 1351 | 75 | 1356 | 84% (1241/1471) | 80% (1172/1471) | 42% (614/1471) | 91% | partial | not confused (-0.04) | duration of the aligned note (sem) |
| `note-quarter` | 4025 | 80 | 4489 | 91% (4042/4426) | 92% (4054/4426) | 74% (3273/4426) | 95% | supported | not confused (-0.13) | duration of the aligned note (sem) |
| `note-8th` | 1526 | 61 | 1634 | 79% (1265/1608) | 77% (1242/1608) | 65% (1053/1608) | 84% | partial | not confused (-0.01) | duration of the aligned note (sem) |
| `note-16th` | 651 | 22 | 635 | 80% (519/651) | 80% (521/651) | 69% (451/651) | 88% | supported | not confused (+0.01) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 97 | 77% (87/113) | 79% (89/113) | 43% (49/113) | 88% | partial | not confused (-0.03) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 32 | 32% (23/71) | 39% (28/71) | 6% (4/71) | 76% | partial | **confused** (+0.08) | duration of the aligned note (sem) |
| `dot` | 295 | 49 | 342 | 74% (222/299) | 77% (230/299) | 55% (163/299) | 89% | partial | **confused** (+0.09) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 5 | 27% (4/15) | 27% (4/15) | 7% (1/15) | 93% | partial | **confused** (+0.19) | <dot/> count + duration |
| `chord` | 608 | 29 | 1660 | 90% (1505/1666) | 90% (1505/1666) | 71% (1177/1666) | 92% | supported | not confused (-0.01) | element on the aligned note |
| `beam` | 703 | 56 | 0 | 0% (0/2064) | 0% (0/2064) | 0% (0/2064) | 86% | **unsupported** — element never emitted | not confused (-0.00) | element on the aligned note |
| `flag` | 308 | 31 | 1548 | 60% (186/308) | 62% (192/308) | 48% (148/308) | 80% | partial | not confused (+0.01) | duration of the flagged note (sem) |
| `stem-up` | 2653 | 67 | 2667 | 90% (2391/2653) | 89% (2353/2653) | 76% (2003/2653) | 89% | supported | not confused (-0.13) | element on the aligned note |
| `stem-down` | 4155 | 72 | 3923 | 91% (3798/4155) | 90% (3753/4155) | 77% (3213/4155) | 92% | supported | not confused (-0.26) | element on the aligned note |
| `ledger-above` | 601 | 58 | 573 | 91% (547/601) | 88% (528/601) | 79% (476/601) | 88% | supported | not confused (-0.03) | pitch (sem) |
| `ledger-below` | 374 | 45 | 351 | 89% (334/374) | 89% (333/374) | 77% (287/374) | 89% | supported | not confused (-0.02) | pitch (sem) |
| `grace` | 58 | 2 | 8 | 45% (26/58) | 10% (6/58) | 3% (2/58) | 10% | **unsupported** | not confused (-0.04) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 19% | **unsupported** | not confused (-0.03) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.40) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 34% | **unsupported** — element never emitted | not confused (-0.84) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | 100% | **unsupported** — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 2 | 100% (3/3) | 100% (3/3) | 100% (3/3) | 100% | supported | not confused (-0.63) | aligned rest with the same duration (sem) |
| `rest-half` | 36 | 15 | 30 | 75% (27/36) | 67% (24/36) | 56% (20/36) | 75% | partial | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-quarter` | 183 | 33 | 137 | 75% (138/183) | 70% (129/183) | 43% (79/183) | 76% | partial | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-8th` | 124 | 16 | 114 | 77% (96/124) | 81% (100/124) | 65% (81/124) | 92% | supported | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 60 | 65% (39/60) | 67% (40/60) | 42% (25/60) | 92% | partial | not confused (-0.01) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 15 | 86% (19/22) | 64% (14/22) | 14% (3/22) | 73% | partial | **confused** (+0.31) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 1 | 60% (6/10) | 10% (1/10) | 0% (0/10) | 30% | **unsupported** | **confused** (+0.47) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 27 | 80% (24/30) | 87% (26/30) | 50% (15/30) | 93% | supported | **confused** (+0.18) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 202 | 14 | 192 | 79% (160/202) | 64% (129/202) | 46% (93/202) | 81% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 0 | 67% (6/9) | 44% (4/9) | 0% (0/9) | – | partial — <multiple-rest> never emitted | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 105 | 71 | 106 | 98% (103/105) | 99% (104/105) | 87% (91/105) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 63 | 45 | 62 | 95% (60/63) | 97% (61/63) | 81% (51/63) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 14 | 13 | 13 | 93% (13/14) | 93% (13/14) | 93% (13/14) | – | supported | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.67) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 6 | 5 | 5 | 83% (5/6) | 83% (5/6) | 67% (4/6) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.38) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.91) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 17 | 48% (13/27) | 56% (15/27) | 7% (2/27) | – | partial | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 40 | 37 | 50 | 97% (36/37) | 97% (36/37) | 92% (34/37) | – | supported | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 18 | 15 | 31 | 87% (13/15) | 87% (13/15) | 73% (11/15) | – | supported | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 12 | 9 | 25 | 100% (9/9) | 89% (8/9) | 89% (8/9) | – | supported | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 6 | 5 | 8 | 83% (5/6) | 83% (5/6) | 83% (5/6) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 4 | 4 | 3 | 75% (3/4) | 75% (3/4) | 25% (1/4) | – | partial | not confused (+0.00) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 2 | 67% (2/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 0 | 50% (1/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 16 | 13 | 19 | 100% (13/13) | 100% (13/13) | 92% (12/13) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 7 | 7 | 10 | 100% (7/7) | 100% (7/7) | 100% (7/7) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 9 | 8 | 11 | 100% (8/8) | 100% (8/8) | 75% (6/8) | – | supported | **confused** (+0.16) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 0% (0/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 34 | 6 | 23 | 79% (27/34) | 68% (23/34) | 41% (14/34) | – | partial | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 78 | 22 | 68 | 59% (46/78) | 71% (55/78) | 41% (32/78) | 71% | partial | not confused (+0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 23 | 71% (20/28) | 75% (21/28) | 93% (26/28) | 75% | partial | not confused (-0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 53 | 10 | 46 | 81% (43/53) | 83% (44/53) | 60% (32/53) | 83% | supported | not confused (+0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 2 | 43% (3/7) | 29% (2/7) | 0% (0/7) | 57% | partial | not confused (-0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 4 | 40% (2/5) | 80% (4/5) | 40% (2/5) | 80% | supported | not confused (+0.05) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 0 | 22% (2/9) | 22% (2/9) | 56% (5/9) | 22% | partial — <accidental> never emitted | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.43) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 0 | 0% (0/22) | 0% (0/22) | 0% (0/22) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.40) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 0 | 0% (0/12) | 0% (0/12) | 0% (0/12) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.32) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | unclear (+0.07) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 14 | 9 | 4 | 45% (5/11) | 36% (4/11) | 36% (4/11) | – | partial | **confused** (+0.11) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 38 | 25 | 29 | 55% (16/29) | 55% (16/29) | 55% (16/29) | – | partial | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 69 | 54 | 92 | 73% (45/62) | 71% (44/62) | 66% (41/62) | – | partial | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 1 | 25% (1/4) | 25% (1/4) | 0% (0/4) | – | partial | not confused (-0.30) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 3 | 11% (2/18) | 17% (3/18) | 6% (1/18) | – | **unsupported** | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.46) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.27) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.43) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.52) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 11 | 6 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | – | **unsupported** — element never emitted | not confused (-0.32) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 0 | 0% (0/89) | 0% (0/89) | 0% (0/89) | – | **unsupported** — element never emitted | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 9 | 9 | 7 | 67% (6/9) | 67% (6/9) | 67% (6/9) | – | partial | not confused (-0.03) | first measure has the pickup length (sem) |
| `tuplet-3` | 76 | 8 | 168 | 67% (133/200) | 67% (133/200) | 40% (80/200) | 93% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 85% | **unsupported** — element never emitted | not confused (+0.05) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 29 | 45% (20/44) | 45% (20/44) | 34% (15/44) | 95% | partial | not confused (-0.13) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 89% | partial | not confused (-0.06) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 21 | 60% (21/35) | 60% (21/35) | 40% (14/35) | 100% | partial | not confused (-0.05) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 100% | **unsupported** — element never emitted | not confused (-1.00) | duration + <time-modification> |
| `tie` | 79 | 14 | 27 | 28% (22/79) | 24% (19/79) | 9% (7/79) | 96% | partial | not confused (+0.05) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 2% (1/46) | 2% (1/46) | 98% | **unsupported** — element never emitted | not confused (+0.01) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 0% (0/1) | – | supported — low n (1) | not confused (-0.79) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — low n (1) | not confused (-1.06) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.16) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 100 | 20 | 27 | 18% (18/100) | 15% (15/100) | 11% (11/100) | 81% | **unsupported** | not confused (+0.05) | element on the aligned note |
| `staccato` | 78 | 7 | 0 | 0% (0/78) | 0% (0/78) | 0% (0/78) | 99% | **unsupported** — element never emitted | not confused (-0.08) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 89% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `accent` | 43 | 8 | 0 | 0% (0/43) | 0% (0/43) | 0% (0/43) | 79% | **unsupported** — element never emitted | **confused** (+0.13) | element on the aligned note |
| `tenuto` | 37 | 6 | 0 | 0% (0/37) | 0% (0/37) | 0% (0/37) | 97% | **unsupported** — element never emitted | not confused (-0.07) | element on the aligned note |
| `marcato` | 23 | 3 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (+0.04) | element on the aligned note |
| `fermata` | 130 | 32 | 90 | 72% (94/130) | 59% (77/130) | 14% (18/130) | 90% | partial | not confused (-0.04) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 93% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `dyn-pp` | 8 | 5 | 8 | 75% (6/8) | 75% (6/8) | 50% (4/8) | – | partial | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 43 | 19 | 33 | 58% (25/43) | 77% (33/43) | 42% (18/43) | – | partial | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 13 | 9 | 15 | 85% (11/13) | 100% (13/13) | 23% (3/13) | – | supported | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 54 | 25 | 29 | 87% (47/54) | 43% (23/54) | 31% (17/54) | – | partial | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 56 | 18 | 43 | 77% (43/56) | 77% (43/56) | 63% (35/56) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 16 | 5 | 14 | 75% (12/16) | 88% (14/16) | 81% (13/16) | – | supported | **confused** (+0.10) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 3 | 67% (4/6) | 50% (3/6) | 17% (1/6) | – | partial | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 43 | 18 | 37 | 86% (37/43) | 86% (37/43) | 26% (11/43) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 31 | 15 | 28 | 84% (26/31) | 84% (26/31) | 19% (6/31) | – | supported | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `pedal` | 28 | 5 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 0 | 0% (0/112) | 0% (0/112) | 0% (0/112) | 92% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `text-expression` | 45 | 11 | 7 | 14% (5/35) | 20% (7/35) | 14% (5/35) | – | partial | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 59 | 53 | 55 | 66% (45/68) | 68% (46/68) | 44% (30/68) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `metronome` | 36 | 33 | 38 | 83% (30/36) | 89% (32/36) | 61% (22/36) | – | supported | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 16 | 6 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 0 | 0% (0/61) | 0% (0/61) | 0% (0/61) | – | **unsupported** — element never emitted | not confused (-0.05) | same element/value at the aligned measure (+-1) |
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
| `barline-double` | 42 | 14 | 0 | 0% (0/42) | 0% (0/42) | 0% (0/42) | – | **unsupported** — element never emitted | not confused (+0.05) | same element/value at the aligned measure (+-1) |
| `barline-final` | 94 | 80 | 143 | 95% (77/81) | 94% (76/81) | 88% (71/81) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 25 | 6 | 0 | 0% (0/25) | 0% (0/25) | 0% (0/25) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 32 | 8 | 0 | 0% (0/32) | 0% (0/32) | 0% (0/32) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `volta-1` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `volta-2` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `segno` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `coda` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `dc` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | **confused** (+0.20) | same element/value at the aligned measure (+-1) |
| `ds` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (+0.09) | same element/value at the aligned measure (+-1) |
| `fine` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `system-break` | 226 | 80 | 0 | 0% (0/226) | 0% (0/226) | 0% (0/226) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `page-break` | 19 | 6 | 0 | 0% (0/19) | 0% (0/19) | 0% (0/19) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `multi-page` | 22 | 6 | 0 | 96% (1838/1908) | 94% (1802/1908) | 89% (1700/1908) | – | supported | not confused (+0.02) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 895 | 15 | 606 | 86% (536/624) | 88% (550/624) | 60% (376/624) | 98% | supported | not confused (-0.30) | lyric on the aligned note |
| `lyrics-multi-verse` | 288 | 5 | 109 | 68% (96/142) | 73% (103/142) | 64% (91/142) | 100% | partial | not confused (-0.03) | lyric on the aligned note |
| `lyrics-melisma` | 39 | 10 | 38 | 70% (23/33) | 67% (22/33) | 55% (18/33) | 97% | partial | not confused (-0.01) | lyric on the aligned note |
| `lyrics-extender` | 27 | 8 | 17 | 53% (10/19) | 58% (11/19) | 47% (9/19) | 100% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-hyphen` | 203 | 15 | 145 | 69% (110/160) | 78% (124/160) | 66% (106/160) | 98% | partial | not confused (-0.02) | lyric on the aligned note |
| `lyrics-elision` | 11 | 1 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (+0.00) | lyric on the aligned note |
| `lyrics-non-ascii` | 30 | 2 | 1 | 0% (0/19) | 0% (0/19) | 0% (0/19) | 100% | **unsupported** | not confused (+0.00) | lyric on the aligned note |
| `stanza-text` | 7 | 2 | – | 84% (76/91) | 79% (92/117) | 81% (82/101) | – | partial | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

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
| `melody` | 32 | 97% | 96% | 88% | 100% | 88% | 100% | 0 | 0.867 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.933 | supported |
| `piano` | 16 | 100% | 100% | 88% | 100% | 100% | 100% | 0 | 0.939 | supported |
| `voice-piano` | 3 | 100% | 100% | 77% | 100% | 100% | 100% | 0 | 0.955 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 99% | 0 | 0.925 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 5% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.985 | supported |
| `choir-piano` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.999 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.960 | supported |
| `string-quartet` | 6 | 86% | 95% | 57% | 100% | 88% | 98% | 0 | 0.953 | supported |
| `orchestral` | 2 | 92% | 93% | 89% | 100% | 82% | 98% | 0 | 0.966 | supported |
| `lead-sheet` | 2 | 83% | 83% | 67% | 100% | 50% | 100% | 0 | 0.940 | supported |
| `hymnal-stanzas` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.999 | supported |
| `divisi` | 2 | 100% | 96% | 99% | 100% | 88% | 100% | 0 | 0.969 | supported |
| `cross-staff` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.877 | supported |
| `two-voices-one-staff-instrument` | 3 | 89% | 89% | 89% | 100% | 67% | 100% | 0 | 0.920 | supported |
| `percussion-none` | 1 | 44% | 44% | 44% | 0% | 33% | 100% | 0 | 0.628 | partial |

## Performance

Source: `mvp/work/eval-coverage.json` (all coverage items, no perf family yet; 243 PDFs; raster 200 dpi, OCR on, 8 parallel jobs on 192 CPUs, load average 31.8 at the start). Times are the converter (`convert()`) in a Node child process, per page; peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. With a fixed raster dpi the source scan dpi changes image quality, not pixel count; use `--dpi native` (raster at the scan resolution) or `--dpi app` (browser app: 2300 px wide) to measure the dpi effect.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 4 | 4.582 | 1743 | 3916 | 282 | 306.8 |
| 110 | 2 | 4.555 | 2057 | 2057 | 248.2 | 248.2 |
| 120 | 8 | 3.869 | 2010 | 3686 | 250.3 | 538.7 |
| 150 | 40 | 4.31 | 2217 | 16963 | 276.5 | 632.2 |
| 200 | 43 | 4.002 | 1931 | 4234 | 255.8 | 727.1 |
| 240 | 3 | 3.873 | 2627 | 2778 | 241.5 | 283.6 |
| 250 | 17 | 3.87 | 1919 | 4399 | 254.1 | 491.9 |
| 300 | 126 | 3.869 | 1715 | 4266 | 241.8 | 678.9 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| ~A3 landscape | 1 | 9.314 | 3102 | 3102 | 412.1 | 412.1 |
| ~A4 | 37 | 4.277 | 1875 | 16963 | 254.2 | 562.2 |
| ~B4 | 19 | 4.697 | 2057 | 7276 | 282 | 505.9 |
| A3 landscape | 1 | 7.742 | 11355 | 11355 | 597.9 | 597.9 |
| A4 | 184 | 3.869 | 1760 | 4399 | 242.5 | 727.1 |
| A4 landscape | 1 | 3.871 | 2308 | 2308 | 267.7 | 267.7 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 227 | 3.869 | 1853 | 16963 | 243.7 | 597.9 |
| 2 | 10 | 3.869 | 2941 | 3686 | 452.8 | 562.5 |
| 5 | 3 | 3.869 | 3020 | 3524 | 678.9 | 727.1 |
| 12 | 3 | 3.869 | 1442 | 1449 | 632.2 | 658.3 |

**Linear fits.** ms per page = -1477.1 + **912.09 ms per megapixel** × MP per page (n=243, R²=0.102). Peak MB = 219.1 + 11.58 MB per megapixel × total MP (n=243, R²=0.438). Overall: 539 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 2057 | 242 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.925 | 0.879 | 4 → 4 | 2758 | 245 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 0.999 | 0.999 | 0.971 | 5 → 5 | 3723 | 351 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 2627 | 242 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.990 | 0.985 | 0.982 | 4 → 4 | 2078 | 256 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.348 | 4 → 4 | 2127 | 235 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.877 | 0.877 | 0.799 | 1 → 1 | 1599 | 229 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 4399 | 313 |
| `layouts/divisi-strings-lament` | divisi | 0.971 | 0.950 | 0.938 | 4 → 4 | 2011 | 233 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 3184 | 261 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 2778 | 241 |
| `layouts/melody-cello-elegy-2page` | melody | 0.886 | 0.843 | 0.713 | 1 → 1 | 1475 | 284 |
| `layouts/melody-flute-air` | melody | 0.959 | 0.968 | 0.961 | 1 → 1 | 1538 | 225 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 2086 | 255 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.972 | 0.957 | 0.896 | 9 → 9 | 3528 | 492 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.985 | 0.946 | 0.770 | 1 → 1 | 2110 | 249 |
| `layouts/piano-grand-staff-prelude` | piano | 0.892 | 0.948 | 0.932 | 1 → 1 | 1595 | 246 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.986 | 0.774 | 4 → 4 | 3574 | 337 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1576 | 243 |
| `layouts/voice-piano-night-song` | voice-piano | 0.977 | 0.924 | 0.459 | 2 → 2 | 2139 | 255 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.919 | 0.976 | 0.888 | 1 → 1 | 2561 | 229 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.825 | 0.832 | 0.815 | 1 → 1 | 3000 | 234 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 1591 | 248 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1585 | 244 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.978 | 0.967 | 0.775 | 1 → 1 | 1785 | 252 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.941 | 0.924 | 0.842 | 1 → 1 | 2249 | 249 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.752 | 0.940 | 0.723 | 1 → 1 | 2071 | 226 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.970 | 0.960 | 0.836 | 1 → 1 | 2101 | 258 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.980 | 1.000 | 0.904 | 2 → 2 | 2139 | 258 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.977 | 0.907 | 4 → 4 | 2201 | 254 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.920 | 0.895 | 1 → 1 | 2077 | 250 |
| `notes/nt01-note-values` | melody | 0.881 | 0.906 | 0.660 | 1 → 1 | 1703 | 252 |
| `notes/nt02-dots` | melody | 0.894 | 0.878 | 0.846 | 1 → 1 | 1710 | 242 |
| `notes/nt03-chords` | piano | 0.916 | 0.912 | 0.896 | 1 → 1 | 1678 | 248 |
| `notes/nt04-beams` | melody | 0.935 | 0.938 | 0.941 | 1 → 1 | 1801 | 260 |
| `notes/nt05-flags-stems` | melody | 0.831 | 0.845 | 0.762 | 1 → 1 | 1695 | 227 |
| `notes/nt06-ledger-lines` | piano | 0.946 | 0.946 | 0.946 | 1 → 1 | 1742 | 236 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.755 | 0.730 | 1 → 1 | 1853 | 228 |
| `notes/nt08-cue-notes` | melody | 0.936 | 0.946 | 0.947 | 1 → 1 | 1604 | 251 |
| `notes/nt09-tremolos` | piano | 0.709 | 0.717 | 0.635 | 1 → 1 | 1682 | 230 |
| `notes/nt10-piano-etude` | piano | 0.986 | 0.981 | 0.951 | 1 → 1 | 1725 | 240 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.634 | 3 → 2 | 1871 | 225 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.955 | 0.945 | 0.860 | 1 → 1 | 1683 | 228 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.857 | 0.927 | 0.843 | 1 → 1 | 1672 | 242 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1654 | 231 |
| `pitch/pitch-cov-clefs-all` | melody | 0.736 | 0.730 | 0.733 | 1 → 1 | 1655 | 261 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.769 | 0.955 | 0.756 | 4 → 4 | 1939 | 239 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.978 | 0.974 | 0.806 | 1 → 1 | 1753 | 259 |
| `pitch/pitch-cov-keys-major-flats` | piano | 0.997 | 1.000 | 0.676 | 1 → 1 | 1674 | 226 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.992 | 0.911 | 0.941 | 1 → 1 | 1657 | 241 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.967 | 0.971 | 0.885 | 1 → 1 | 1800 | 228 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.604 | 0.541 | 0.557 | 1 → 1 | 2399 | 268 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 0.838 | 0.838 | 0.838 | 1 → 1 | 1706 | 220 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.809 | 0.795 | 0.803 | 1 → 1 | 1912 | 248 |
| `rests/rst01-rest-values` | melody | 0.823 | 0.757 | 0.684 | 1 → 1 | 1677 | 253 |
| `rests/rst02-dotted-rests` | melody | 0.858 | 0.883 | 0.747 | 1 → 1 | 1762 | 232 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.768 | 0.777 | 0.701 | 1 → 1 | 1734 | 232 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.753 | 0.746 | 0.853 | 1 → 1 | 1719 | 245 |
| `rests/rst05-multibar-rests` | melody | 0.849 | 0.723 | 0.620 | 1 → 1 | 1849 | 227 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.858 | 0.840 | 1 → 1 | 1811 | 235 |
| `rests/rst07-piano-rests` | piano | 0.927 | 0.921 | 0.897 | 1 → 1 | 1744 | 250 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.852 | 0.837 | 0.367 | 1 → 1 | 2208 | 253 |
| `rests/rst09-quartet-rests` | string-quartet | 0.990 | 0.976 | 0.921 | 4 → 4 | 3305 | 339 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 1571 | 228 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.980 | 1 → 1 | 1592 | 260 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.466 | 4 → 4 | 3196 | 380 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 1909 | 228 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.481 | 1 → 1 | 1941 | 252 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.972 | 0.942 | 0.838 | 2 → 2 | 3244 | 563 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.975 | 0.957 | 7 → 7 | 2869 | 668 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.983 | 0.974 | 0.962 | 1 → 1 | 1442 | 658 |
| `time/t01-simple-meters` | melody | 0.833 | 0.881 | 0.851 | 1 → 1 | 1600 | 245 |
| `time/t02-compound-irregular` | melody | 0.897 | 0.895 | 0.891 | 1 → 1 | 1766 | 227 |
| `time/t03-common-cut-piano` | piano | 0.959 | 0.974 | 0.928 | 1 → 1 | 1627 | 234 |
| `time/t04-pickup-song` | melody-lyrics | 0.916 | 0.923 | 0.936 | 1 → 1 | 2133 | 231 |
| `time/t05-triplets-duplets` | melody | 0.817 | 0.839 | 0.787 | 1 → 1 | 1761 | 235 |
| `time/t06-quint-sext-sept` | melody | 0.971 | 0.968 | 0.917 | 1 → 1 | 1570 | 222 |
| `time/t07-nested-tuplets` | melody | 0.808 | 0.802 | 0.823 | 1 → 1 | 1598 | 241 |
| `time/t08-ties-systems-pages` | piano | 0.978 | 0.990 | 0.404 | 1 → 1 | 1485 | 315 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.906 | 0.906 | 0.765 | 1 → 1 | 1570 | 247 |
| `time/t10-quartet-meters` | string-quartet | 0.863 | 0.845 | 0.620 | 4 → 4 | 1919 | 258 |
