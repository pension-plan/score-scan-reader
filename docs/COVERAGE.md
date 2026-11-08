# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 15:56 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage-text.json` (eval 2026-11-08 15:56, app source hash `bd1a6df06b7f`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 83 items, 249 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

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

**Totals:** 86 supported, 42 partial, 26 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 50% | **unsupported** | not confused (-0.14) | duration of the aligned note (sem) |
| `note-whole` | 174 | 39 | 185 | 80% (160/199) | 77% (153/199) | 43% (85/199) | 82% | partial | not confused (+0.00) | duration of the aligned note (sem) |
| `note-half` | 1390 | 77 | 1419 | 94% (1426/1510) | 87% (1311/1510) | 43% (650/1510) | 94% | supported | not confused (-0.01) | duration of the aligned note (sem) |
| `note-quarter` | 4101 | 82 | 4497 | 95% (4257/4502) | 94% (4244/4502) | 77% (3482/4502) | 97% | supported | not confused (-0.05) | duration of the aligned note (sem) |
| `note-8th` | 1538 | 62 | 1584 | 83% (1352/1620) | 81% (1319/1620) | 69% (1117/1620) | 88% | supported | not confused (+0.01) | duration of the aligned note (sem) |
| `note-16th` | 651 | 22 | 611 | 82% (531/651) | 81% (530/651) | 70% (453/651) | 90% | supported | not confused (+0.01) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 103 | 79% (89/113) | 81% (92/113) | 43% (49/113) | 90% | supported | not confused (-0.02) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 30 | 32% (23/71) | 39% (28/71) | 6% (4/71) | 79% | partial | not confused (-0.02) | duration of the aligned note (sem) |
| `dot` | 295 | 49 | 316 | 92% (275/299) | 92% (275/299) | 68% (204/299) | 96% | supported | not confused (-0.00) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 16 | 93% (14/15) | 93% (14/15) | 40% (6/15) | 93% | supported | **confused** (+0.15) | <dot/> count + duration |
| `chord` | 624 | 30 | 1726 | 95% (1614/1708) | 94% (1604/1708) | 73% (1246/1708) | 95% | supported | not confused (-0.01) | element on the aligned note |
| `beam` | 709 | 57 | 1664 | 84% (1737/2076) | 78% (1616/2076) | 64% (1331/2076) | 89% | partial | not confused (+0.01) | element on the aligned note |
| `flag` | 308 | 31 | 459 | 63% (193/308) | 63% (195/308) | 49% (151/308) | 81% | partial | not confused (+0.02) | duration of the flagged note (sem) |
| `stem-up` | 2696 | 69 | 2612 | 92% (2483/2696) | 91% (2440/2696) | 78% (2090/2696) | 91% | supported | not confused (-0.06) | element on the aligned note |
| `stem-down` | 4218 | 74 | 4014 | 94% (3971/4218) | 93% (3934/4218) | 79% (3342/4218) | 95% | supported | not confused (-0.14) | element on the aligned note |
| `ledger-above` | 608 | 60 | 599 | 96% (585/608) | 93% (567/608) | 82% (499/608) | 93% | supported | not confused (-0.03) | pitch (sem) |
| `ledger-below` | 382 | 46 | 382 | 97% (372/382) | 97% (372/382) | 81% (310/382) | 97% | supported | not confused (-0.01) | pitch (sem) |
| `grace` | 58 | 2 | 37 | 38% (22/58) | 59% (34/58) | 74% (43/58) | 59% | partial | not confused (-0.04) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 56% | **unsupported** | not confused (-0.03) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.20) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 46% | **unsupported** — element never emitted | not confused (-0.83) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 100% (2/2) | 100% (2/2) | 100% (2/2) | 100% | supported — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 3 | 100% (3/3) | 100% (3/3) | 0% (0/3) | 100% | supported | not confused (-0.40) | aligned rest with the same duration (sem) |
| `rest-half` | 37 | 16 | 31 | 78% (29/37) | 73% (27/37) | 57% (21/37) | 76% | partial | not confused (+0.04) | aligned rest with the same duration (sem) |
| `rest-quarter` | 183 | 33 | 140 | 78% (142/183) | 73% (133/183) | 50% (91/183) | 77% | partial | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-8th` | 124 | 16 | 110 | 76% (94/124) | 81% (100/124) | 66% (82/124) | 94% | supported | not confused (+0.02) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 63 | 68% (41/60) | 68% (41/60) | 52% (31/60) | 92% | partial | not confused (+0.00) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 18 | 100% (22/22) | 77% (17/22) | 32% (7/22) | 77% | partial | not confused (+0.04) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 5 | 100% (10/10) | 50% (5/10) | 30% (3/10) | 50% | partial | not confused (-0.09) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 28 | 83% (25/30) | 93% (28/30) | 60% (18/30) | 93% | supported | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 202 | 14 | 204 | 90% (182/202) | 83% (168/202) | 49% (98/202) | 90% | supported | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 7 | 67% (6/9) | 67% (6/9) | 0% (0/9) | – | partial | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 107 | 73 | 108 | 99% (106/107) | 99% (106/107) | 87% (93/107) | – | supported | **confused** (+0.05) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 64 | 46 | 63 | 95% (61/64) | 97% (62/64) | 83% (53/64) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 14 | 13 | 13 | 93% (13/14) | 93% (13/14) | 93% (13/14) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.64) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 6 | 5 | 5 | 83% (5/6) | 83% (5/6) | 83% (5/6) | – | supported | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.14) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.93) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 17 | 48% (13/27) | 56% (15/27) | 7% (2/27) | – | partial | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 41 | 38 | 51 | 100% (38/38) | 97% (37/38) | 89% (34/38) | – | supported | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 19 | 16 | 33 | 100% (16/16) | 94% (15/16) | 88% (14/16) | – | supported | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 12 | 9 | 26 | 100% (9/9) | 100% (9/9) | 89% (8/9) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 6 | 5 | 9 | 100% (6/6) | 100% (6/6) | 83% (5/6) | – | supported | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 4 | 4 | 4 | 100% (4/4) | 100% (4/4) | 25% (1/4) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 3 | 100% (3/3) | 100% (3/3) | 33% (1/3) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 0% (0/2) | – | supported — low n (2) | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 16 | 13 | 19 | 100% (13/13) | 100% (13/13) | 92% (12/13) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 7 | 7 | 10 | 100% (7/7) | 100% (7/7) | 100% (7/7) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 9 | 8 | 11 | 100% (8/8) | 100% (8/8) | 75% (6/8) | – | supported | **confused** (+0.17) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 34 | 6 | 30 | 100% (34/34) | 88% (30/34) | 47% (16/34) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 82 | 23 | 78 | 94% (77/82) | 91% (75/82) | 62% (51/82) | 91% | supported | not confused (-0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 28 | 96% (27/28) | 96% (27/28) | 82% (23/28) | 96% | supported | not confused (-0.05) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 53 | 10 | 49 | 92% (49/53) | 92% (49/53) | 75% (40/53) | 92% | supported | not confused (+0.01) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 4 | 71% (5/7) | 57% (4/7) | 0% (0/7) | 57% | partial | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 4 | 80% (4/5) | 80% (4/5) | 40% (2/5) | 80% | supported | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 9 | 100% (9/9) | 100% (9/9) | 89% (8/9) | 100% | supported | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 27 | 100% (28/28) | 96% (27/28) | 71% (20/28) | 96% | supported | not confused (+0.00) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 22 | 100% (22/22) | 100% (22/22) | 100% (22/22) | 100% | supported | not confused (+0.00) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 12 | 100% (12/12) | 100% (12/12) | 100% (12/12) | 100% | supported | not confused (+0.00) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | not confused (-0.02) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 100% (2/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 14 | 9 | 11 | 91% (10/11) | 73% (8/11) | 64% (7/11) | – | partial | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 38 | 25 | 44 | 93% (27/29) | 100% (29/29) | 72% (21/29) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 71 | 56 | 107 | 97% (62/64) | 94% (60/64) | 81% (52/64) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 4 | 100% (4/4) | 100% (4/4) | 50% (2/4) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 4 | 100% (4/4) | 100% (4/4) | 25% (1/4) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 23 | 89% (16/18) | 94% (17/18) | 56% (10/18) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 100% (5/5) | – | supported | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 80% (4/5) | – | supported | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 3 | 100% (3/3) | 100% (3/3) | 33% (1/3) | – | supported | not confused (-0.12) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 7 | 100% (4/4) | 100% (4/4) | 75% (3/4) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 7 | 100% (4/4) | 100% (4/4) | 100% (4/4) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 11 | 6 | 12 | 88% (7/8) | 88% (7/8) | 75% (6/8) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 10 | 86% (6/7) | 86% (6/7) | 43% (3/7) | – | supported | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 110 | 94% (84/89) | 96% (85/89) | 61% (54/89) | – | supported | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 9 | 9 | 7 | 67% (6/9) | 67% (6/9) | 56% (5/9) | – | partial | not confused (+0.06) | first measure has the pickup length (sem) |
| `tuplet-3` | 76 | 8 | 166 | 68% (135/200) | 68% (135/200) | 43% (85/200) | 94% | partial | not confused (+0.02) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 100% | **unsupported** — element never emitted | not confused (-0.04) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 29 | 45% (20/44) | 45% (20/44) | 34% (15/44) | 93% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 89% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 21 | 60% (21/35) | 60% (21/35) | 40% (14/35) | 100% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 100% | **unsupported** — element never emitted | not confused (+0.00) | duration + <time-modification> |
| `tie` | 79 | 14 | 26 | 29% (23/79) | 27% (21/79) | 16% (13/79) | 100% | partial | not confused (-0.03) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 2% (1/46) | 2% (1/46) | 100% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | unclear (+0.33) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 4 | 100% (4/4) | 100% (4/4) | 25% (1/4) | – | supported | not confused (-0.18) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.05) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 100 | 20 | 18 | 18% (18/100) | 15% (15/100) | 11% (11/100) | 88% | **unsupported** | not confused (+0.05) | element on the aligned note |
| `staccato` | 78 | 7 | 82 | 97% (76/78) | 96% (75/78) | 83% (65/78) | 99% | supported | not confused (-0.08) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 9 | 100% (9/9) | 100% (9/9) | 89% (8/9) | 100% | supported | not confused (-0.01) | element on the aligned note |
| `accent` | 43 | 8 | 36 | 72% (31/43) | 72% (31/43) | 63% (27/43) | 79% | partial | **confused** (+0.14) | element on the aligned note |
| `tenuto` | 37 | 6 | 38 | 97% (36/37) | 95% (35/37) | 76% (28/37) | 97% | supported | not confused (-0.06) | element on the aligned note |
| `marcato` | 23 | 3 | 22 | 83% (19/23) | 74% (17/23) | 52% (12/23) | 87% | partial | not confused (+0.04) | element on the aligned note |
| `fermata` | 130 | 32 | 90 | 72% (94/130) | 60% (78/130) | 14% (18/130) | 93% | partial | not confused (-0.01) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 96% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `dyn-pp` | 9 | 6 | 9 | 67% (6/9) | 78% (7/9) | 56% (5/9) | – | partial | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 45 | 20 | 34 | 58% (26/45) | 76% (34/45) | 40% (18/45) | – | partial | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 13 | 9 | 15 | 85% (11/13) | 100% (13/13) | 23% (3/13) | – | supported | **confused** (+0.15) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 55 | 26 | 31 | 89% (49/55) | 45% (25/55) | 31% (17/55) | – | partial | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 56 | 18 | 43 | 77% (43/56) | 77% (43/56) | 63% (35/56) | – | partial | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 16 | 5 | 14 | 75% (12/16) | 88% (14/16) | 81% (13/16) | – | supported | **confused** (+0.12) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 3 | 67% (4/6) | 50% (3/6) | 17% (1/6) | – | partial | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 43 | 18 | 37 | 86% (37/43) | 86% (37/43) | 23% (10/43) | – | supported | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 31 | 15 | 28 | 84% (26/31) | 84% (26/31) | 19% (6/31) | – | supported | not confused (-0.06) | same element/value at the aligned measure (+-1) |
| `pedal` | 44 | 6 | 23 | 90% (26/29) | 79% (23/29) | 21% (6/29) | – | partial | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 76 | 79% (88/112) | 67% (75/112) | 43% (48/112) | 95% | partial | not confused (-0.03) | element on the aligned note |
| `text-expression` | 45 | 11 | 13 | 37% (13/35) | 31% (11/35) | 31% (11/35) | – | partial | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 61 | 55 | 58 | 67% (47/70) | 70% (49/70) | 46% (32/70) | – | partial | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `metronome` | 36 | 33 | 38 | 86% (31/36) | 89% (32/36) | 61% (22/36) | – | supported | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 22 | 7 | 17 | 82% (18/22) | 64% (14/22) | 50% (11/22) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 52 | 84% (51/61) | 85% (52/61) | 66% (40/61) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
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
| `barline-double` | 42 | 14 | 54 | 95% (40/42) | 95% (40/42) | 69% (29/42) | – | supported | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `barline-final` | 96 | 82 | 153 | 100% (83/83) | 99% (82/83) | 92% (76/83) | – | supported | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 25 | 6 | 44 | 100% (25/25) | 96% (24/25) | 68% (17/25) | – | supported | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 32 | 8 | 60 | 100% (32/32) | 100% (32/32) | 75% (24/32) | – | supported | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `volta-1` | 8 | 5 | 24 | 100% (8/8) | 100% (8/8) | 75% (6/8) | – | supported | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `volta-2` | 8 | 5 | 24 | 100% (8/8) | 100% (8/8) | 63% (5/8) | – | supported | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `segno` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 0% (0/2) | – | supported — low n (2) | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `coda` | 4 | 2 | 4 | 100% (4/4) | 100% (4/4) | 100% (4/4) | – | supported | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `dc` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `ds` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (+0.10) | same element/value at the aligned measure (+-1) |
| `fine` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `system-break` | 230 | 82 | 0 | 0% (0/230) | 0% (0/230) | 0% (0/230) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `page-break` | 19 | 6 | 0 | 0% (0/19) | 0% (0/19) | 0% (0/19) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `multi-page` | 22 | 6 | 0 | 98% (1863/1908) | 95% (1822/1908) | 91% (1734/1908) | – | supported | not confused (+0.01) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 4 | 100% (1/1) | 100% (1/1) | 0% (0/1) | – | supported — low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 895 | 15 | 615 | 89% (557/624) | 90% (561/624) | 62% (385/624) | 98% | supported | not confused (-0.28) | lyric on the aligned note |
| `lyrics-multi-verse` | 288 | 5 | 125 | 83% (118/142) | 81% (115/142) | 70% (99/142) | 99% | supported | not confused (-0.03) | lyric on the aligned note |
| `lyrics-melisma` | 39 | 10 | 34 | 79% (26/33) | 73% (24/33) | 55% (18/33) | 97% | partial | not confused (-0.01) | lyric on the aligned note |
| `lyrics-extender` | 27 | 8 | 14 | 63% (12/19) | 63% (12/19) | 47% (9/19) | 100% | partial | not confused (-0.02) | lyric on the aligned note |
| `lyrics-hyphen` | 203 | 15 | 157 | 79% (127/160) | 83% (133/160) | 72% (115/160) | 97% | supported | not confused (-0.03) | lyric on the aligned note |
| `lyrics-elision` | 11 | 1 | 7 | 88% (7/8) | 50% (4/8) | 63% (5/8) | 100% | partial | not confused (+0.00) | lyric on the aligned note |
| `lyrics-non-ascii` | 30 | 2 | 3 | 0% (0/19) | 0% (0/19) | 0% (0/19) | 100% | **unsupported** | not confused (+0.00) | lyric on the aligned note |
| `stanza-text` | 7 | 2 | – | 83% (152/183) | 81% (149/185) | 79% (135/171) | – | supported | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

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
| `x-pedal-release` | 39 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano`, `marks/mk10-piano-pedal-brackets` |
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
| `melody` | 33 | 98% | 97% | 90% | 100% | 91% | 100% | 0 | 0.927 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.980 | supported |
| `piano` | 17 | 100% | 100% | 94% | 100% | 100% | 100% | 0 | 0.967 | supported |
| `voice-piano` | 3 | 100% | 100% | 97% | 100% | 100% | 100% | 0 | 0.963 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.938 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 98% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.992 | supported |
| `choir-piano` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.975 | supported |
| `string-quartet` | 6 | 98% | 100% | 80% | 100% | 100% | 99% | 0 | 0.981 | supported |
| `orchestral` | 2 | 92% | 93% | 91% | 100% | 82% | 99% | 0 | 0.969 | supported |
| `lead-sheet` | 2 | 83% | 83% | 67% | 100% | 50% | 100% | 0 | 0.960 | supported |
| `hymnal-stanzas` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.999 | supported |
| `divisi` | 2 | 100% | 100% | 99% | 100% | 100% | 100% | 0 | 0.988 | supported |
| `cross-staff` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.889 | supported |
| `two-voices-one-staff-instrument` | 3 | 89% | 89% | 89% | 100% | 67% | 100% | 0 | 0.931 | supported |
| `percussion-none` | 1 | 44% | 44% | 44% | 0% | 33% | 100% | 0 | 0.628 | partial |

## Performance

Source: `mvp/work/eval-coverage-baseline-perf.json` (perf family; 63 PDFs; raster native, OCR on, 8 parallel jobs on 192 CPUs, load average 166.9 at the start). Times are the converter in a Node child process, per page, run as the browser worker runs it (`createConverter()`: each page read from disk when its turn comes, `addPage`, then `releasePage` frees its image buffers and keeps the staff-removed binary bit-packed, then `finish`); peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. Pages are rasterised at the resolution of the scan image, so pixel count follows the source dpi.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 6 | 0.968 | 3227 | 4464 | 309.4 | 374.5 |
| 150 | 6 | 2.178 | 3332 | 4900 | 318.2 | 376.2 |
| 200 | 6 | 3.869 | 3110 | 4225 | 252.2 | 337.6 |
| 300 | 33 | 8.703 | 3185 | 5352 | 375.3 | 2184.3 |
| 400 | 6 | 15.475 | 5593 | 7527 | 446 | 557.8 |
| 600 | 6 | 34.806 | 4819 | 5363 | 418 | 445.6 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| ~A3 | 1 | 20.49 | 5259 | 5259 | 417.9 | 417.9 |
| ~B4 | 6 | 10.25 | 5352 | 7527 | 419.1 | 557.8 |
| ~Letter | 1 | 9.965 | 4833 | 4833 | 453.1 | 453.1 |
| A3 | 5 | 17.403 | 3617 | 4266 | 345.9 | 411.7 |
| A4 | 45 | 8.703 | 2993 | 6659 | 345.4 | 2184.3 |
| Letter | 5 | 8.415 | 3717 | 4452 | 336.6 | 369.5 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 51 | 8.703 | 3782 | 7527 | 336.6 | 557.8 |
| 5 | 3 | 8.703 | 2740 | 2993 | 572.1 | 666.1 |
| 10 | 3 | 8.703 | 2614 | 2864 | 891.3 | 908.4 |
| 20 | 3 | 8.703 | 2602 | 2727 | 1301.1 | 1302.1 |
| 40 | 3 | 8.703 | 2429 | 2632 | 2180.8 | 2184.3 |

**Linear fits.** ms per page = 3056.2 + **51.49 ms per megapixel** × MP per page (n=63, R²=0.2). Peak MB = 296.9 + 5.2 MB per megapixel × total MP (n=63, R²=0.968). Overall: 301 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 1675 | 281 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.938 | 0.879 | 4 → 4 | 2223 | 299 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 1.000 | 1.000 | 0.972 | 5 → 5 | 3285 | 364 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 2026 | 285 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.996 | 0.992 | 0.982 | 4 → 4 | 1602 | 285 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.767 | 4 → 4 | 1722 | 285 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.884 | 0.889 | 0.794 | 1 → 1 | 1373 | 286 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 3834 | 339 |
| `layouts/divisi-strings-lament` | divisi | 0.993 | 0.988 | 0.956 | 4 → 4 | 1821 | 294 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 2249 | 295 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 2033 | 271 |
| `layouts/melody-cello-elegy-2page` | melody | 0.902 | 0.855 | 0.732 | 1 → 1 | 1199 | 332 |
| `layouts/melody-flute-air` | melody | 0.967 | 0.977 | 0.972 | 1 → 1 | 1341 | 274 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 1611 | 289 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.973 | 0.958 | 0.905 | 9 → 9 | 3721 | 517 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.998 | 0.973 | 0.768 | 1 → 1 | 1731 | 286 |
| `layouts/piano-grand-staff-prelude` | piano | 0.902 | 0.954 | 0.952 | 1 → 1 | 1573 | 276 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.988 | 0.775 | 4 → 4 | 3663 | 376 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1420 | 288 |
| `layouts/voice-piano-night-song` | voice-piano | 0.979 | 0.949 | 0.542 | 2 → 2 | 1801 | 281 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.985 | 0.979 | 0.890 | 1 → 1 | 1780 | 294 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.975 | 0.975 | 0.943 | 1 → 1 | 2046 | 277 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 1350 | 287 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1374 | 294 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.994 | 0.968 | 0.780 | 1 → 1 | 1530 | 277 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.955 | 0.951 | 0.829 | 1 → 1 | 1785 | 278 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.982 | 0.956 | 0.723 | 1 → 1 | 1673 | 283 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 1.000 | 1.000 | 0.836 | 1 → 1 | 1646 | 292 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.988 | 0.993 | 0.904 | 2 → 2 | 1781 | 300 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.983 | 0.977 | 0.928 | 4 → 4 | 2053 | 325 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.947 | 0.902 | 1 → 1 | 1638 | 295 |
| `marks/mk10-piano-pedal-brackets` | piano | 0.977 | 0.979 | 0.902 | 1 → 1 | 1515 | 287 |
| `marks/mk11-violin-circled-rehearsal-numbers` | melody | 0.933 | 0.956 | 0.985 | 1 → 1 | 1364 | 288 |
| `notes/nt01-note-values` | melody | 0.895 | 0.924 | 0.673 | 1 → 1 | 1528 | 303 |
| `notes/nt02-dots` | melody | 0.963 | 0.936 | 0.879 | 1 → 1 | 1486 | 303 |
| `notes/nt03-chords` | piano | 0.975 | 0.972 | 0.900 | 1 → 1 | 1446 | 285 |
| `notes/nt04-beams` | melody | 0.985 | 0.971 | 0.978 | 1 → 1 | 1560 | 285 |
| `notes/nt05-flags-stems` | melody | 0.847 | 0.850 | 0.759 | 1 → 1 | 1562 | 289 |
| `notes/nt06-ledger-lines` | piano | 1.000 | 0.953 | 0.953 | 1 → 1 | 1494 | 295 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.927 | 0.946 | 1 → 1 | 1504 | 282 |
| `notes/nt08-cue-notes` | melody | 0.960 | 0.946 | 0.947 | 1 → 1 | 1412 | 285 |
| `notes/nt09-tremolos` | piano | 0.719 | 0.751 | 0.635 | 1 → 1 | 1438 | 288 |
| `notes/nt10-piano-etude` | piano | 0.989 | 0.988 | 0.959 | 1 → 1 | 1470 | 292 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.639 | 3 → 2 | 1746 | 297 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 1.000 | 0.997 | 0.879 | 1 → 1 | 1462 | 296 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.985 | 0.985 | 0.892 | 1 → 1 | 1568 | 275 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1524 | 284 |
| `pitch/pitch-cov-clefs-all` | melody | 0.741 | 0.727 | 0.733 | 1 → 1 | 1519 | 282 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.964 | 0.955 | 0.948 | 4 → 4 | 1790 | 281 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.989 | 0.978 | 0.813 | 1 → 1 | 1764 | 305 |
| `pitch/pitch-cov-keys-major-flats` | piano | 1.000 | 1.000 | 0.683 | 1 → 1 | 1637 | 301 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 1.000 | 0.911 | 0.952 | 1 → 1 | 1556 | 283 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.981 | 0.994 | 0.972 | 1 → 1 | 1517 | 279 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.994 | 0.994 | 0.589 | 1 → 1 | 1575 | 284 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 1.000 | 1.000 | 1.000 | 1 → 1 | 1369 | 289 |
| `pitch/pitch-cov-ottava-piano` | piano | 1.000 | 0.958 | 0.925 | 1 → 1 | 1533 | 288 |
| `rests/rst01-rest-values` | melody | 0.867 | 0.841 | 0.725 | 1 → 1 | 1594 | 295 |
| `rests/rst02-dotted-rests` | melody | 0.934 | 0.948 | 0.798 | 1 → 1 | 1598 | 280 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.904 | 0.904 | 0.768 | 1 → 1 | 1515 | 314 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.989 | 1.000 | 0.940 | 1 → 1 | 1461 | 298 |
| `rests/rst05-multibar-rests` | melody | 0.881 | 0.807 | 0.626 | 1 → 1 | 1708 | 287 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.863 | 0.840 | 1 → 1 | 1454 | 282 |
| `rests/rst07-piano-rests` | piano | 0.954 | 0.959 | 0.943 | 1 → 1 | 1596 | 297 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.863 | 0.846 | 0.367 | 1 → 1 | 1840 | 296 |
| `rests/rst09-quartet-rests` | string-quartet | 0.995 | 0.992 | 0.938 | 4 → 4 | 3036 | 357 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.944 | 1 → 1 | 1439 | 306 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.980 | 1 → 1 | 1570 | 296 |
| `structure/str03-voltas-string-quartet` | string-quartet | 1.000 | 0.996 | 0.761 | 4 → 4 | 4286 | 387 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 1635 | 288 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.487 | 1 → 1 | 1779 | 298 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.976 | 0.948 | 0.844 | 2 → 2 | 2856 | 497 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.985 | 0.980 | 0.960 | 7 → 7 | 3557 | 565 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.997 | 0.984 | 0.967 | 1 → 1 | 1383 | 471 |
| `time/t01-simple-meters` | melody | 0.962 | 0.961 | 0.869 | 1 → 1 | 1586 | 280 |
| `time/t02-compound-irregular` | melody | 1.000 | 1.000 | 0.971 | 1 → 1 | 1624 | 292 |
| `time/t03-common-cut-piano` | piano | 0.991 | 1.000 | 0.931 | 1 → 1 | 1628 | 290 |
| `time/t04-pickup-song` | melody-lyrics | 0.953 | 0.966 | 0.955 | 1 → 1 | 1593 | 285 |
| `time/t05-triplets-duplets` | melody | 0.848 | 0.875 | 0.841 | 1 → 1 | 1569 | 286 |
| `time/t06-quint-sext-sept` | melody | 0.973 | 0.971 | 0.920 | 1 → 1 | 1310 | 295 |
| `time/t07-nested-tuplets` | melody | 0.819 | 0.812 | 0.827 | 1 → 1 | 1390 | 282 |
| `time/t08-ties-systems-pages` | piano | 1.000 | 0.997 | 0.972 | 1 → 1 | 1287 | 314 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.933 | 0.933 | 0.790 | 1 → 1 | 1300 | 296 |
| `time/t10-quartet-meters` | string-quartet | 0.987 | 0.978 | 0.884 | 4 → 4 | 1990 | 306 |
