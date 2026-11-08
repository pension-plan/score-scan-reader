# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 06:47 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 06:47, app source hash `26833f6ccdb3`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 62 items, 186 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

Regenerate:

```
node mvp/tools/eval.mjs --set coverage --out mvp/work/eval-coverage.json
node mvp/tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 --out mvp/work/eval-coverage-perf.json   # optional, for timing
node tools/coverage.mjs --eval mvp/work/eval-coverage.json [--perf mvp/work/eval-coverage-perf.json]
```

## How to read the tables

- **Occurrences**: how often the symbol occurs in the truth files, summed over items (`meta.json` counts; this tool's own count from `truth.musicxml` where meta has none). **Items**: items containing it.
- **Accuracy** per input (clean / scan / scan-severe): recall over the truth instances. Note-level tags: truth notes with the tag that are aligned to an app note with the right pitch *and* the tag's feature (an element such as `<dot/>`, `<beam>`, `<slur>`, `<staccato/>`, or, for semantic tags marked *sem*, its meaning: duration for note values, spelled pitch for accidentals, sounding pitch under an ottava). Clef, key and time tags: exact match of the same clef/key/time change at the aligned measure (±1). Directions and structure: the same element and value at the aligned measure (±1). Notes and rests are aligned with all parts merged, so part splitting does not affect these numbers (it is scored under layouts).
- **Emitted**: how many times the app's MusicXML contains the corresponding element, on the typical scan (0 = never written).
- **Read**: share of truth notes carrying the tag that the app read with the right pitch, whether or not it kept the mark.
- **Status** (from the `scan` input, the typical 200–300 dpi scan): supported ≥ 0.8, partial 0.2–0.8, unsupported < 0.2 or the element is never emitted. Semantic tags whose MusicXML element exists but is never written (e.g. `<octave-shift>`, `<multiple-rest>`) are capped at partial.
- **Confusion** (on `clean.pdf`): false notes (app notes that match no truth note) per truth note in the measures holding the symbol, minus the same rate in the other measures (all items' rate when the symbol is in every measure). *confused* = excess > 0.05 and at least 3 surplus false notes; *unclear* = excess > 0.05 on fewer than 10 truth notes; otherwise *not confused*: the app may drop the mark, but it does not turn it into extra notes. It matters most for marks the app does not output.

**Totals:** 15 supported, 41 partial, 94 unsupported, 23 not measurable, 3 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 75% | **unsupported** | not confused (+0.02) | duration of the aligned note (sem) |
| `note-whole` | 124 | 29 | 102 | 51% (72/140) | 41% (57/140) | 21% (29/140) | 59% | partial | not confused (-0.09) | duration of the aligned note (sem) |
| `note-half` | 924 | 57 | 908 | 72% (710/993) | 68% (672/993) | 29% (284/993) | 85% | partial | not confused (-0.05) | duration of the aligned note (sem) |
| `note-quarter` | 2019 | 61 | 2210 | 82% (1801/2188) | 80% (1758/2188) | 53% (1165/2188) | 88% | supported | not confused (-0.17) | duration of the aligned note (sem) |
| `note-8th` | 931 | 49 | 1131 | 74% (693/931) | 75% (695/931) | 61% (568/931) | 84% | partial | not confused (-0.10) | duration of the aligned note (sem) |
| `note-16th` | 347 | 19 | 417 | 64% (222/347) | 58% (202/347) | 50% (174/347) | 84% | partial | not confused (-0.10) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 8 | 2% (2/113) | 3% (3/113) | 1% (1/113) | 82% | **unsupported** | not confused (-0.03) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 0 | 0% (0/71) | 0% (0/71) | 0% (0/71) | 75% | **unsupported** | not confused (-0.01) | duration of the aligned note (sem) |
| `dot` | 234 | 40 | 301 | 71% (168/236) | 73% (173/236) | 48% (114/236) | 94% | partial | not confused (+0.04) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 6 | 27% (4/15) | 27% (4/15) | 7% (1/15) | 87% | partial | **confused** (+0.21) | <dot/> count + duration |
| `chord` | 382 | 20 | 983 | 85% (911/1066) | 82% (873/1066) | 52% (556/1066) | 84% | supported | not confused (-0.12) | element on the aligned note |
| `beam` | 397 | 45 | 0 | 0% (0/1208) | 0% (0/1208) | 0% (0/1208) | 86% | **unsupported** — element never emitted | not confused (-0.09) | element on the aligned note |
| `flag` | 251 | 26 | 883 | 44% (110/251) | 43% (108/251) | 38% (95/251) | 71% | partial | not confused (-0.03) | duration of the flagged note (sem) |
| `stem-up` | 1260 | 49 | 1369 | 85% (1074/1260) | 86% (1078/1260) | 62% (776/1260) | 87% | supported | not confused (-0.22) | element on the aligned note |
| `stem-down` | 2216 | 53 | 2069 | 84% (1859/2216) | 82% (1816/2216) | 64% (1423/2216) | 84% | supported | not confused (-0.48) | element on the aligned note |
| `ledger-above` | 380 | 49 | 346 | 85% (323/380) | 78% (298/380) | 66% (251/380) | 78% | partial | not confused (-0.10) | pitch (sem) |
| `ledger-below` | 212 | 32 | 199 | 79% (167/212) | 76% (161/212) | 57% (120/212) | 76% | partial | not confused (-0.07) | pitch (sem) |
| `grace` | 58 | 2 | 0 | 0% (0/58) | 0% (0/58) | 0% (0/58) | 0% | **unsupported** — element never emitted | not confused (-0.05) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 0% | **unsupported** — element never emitted | not confused (-0.02) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.40) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 37% | **unsupported** — element never emitted | **confused** (+0.19) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | 100% | **unsupported** — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 2 | 100% (3/3) | 67% (2/3) | 0% (0/3) | 100% | partial | not confused (-0.70) | aligned rest with the same duration (sem) |
| `rest-half` | 24 | 12 | 18 | 63% (15/24) | 54% (13/24) | 33% (8/24) | 71% | partial | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-quarter` | 125 | 25 | 112 | 86% (108/125) | 82% (102/125) | 54% (68/125) | 86% | supported | **confused** (+0.05) | aligned rest with the same duration (sem) |
| `rest-8th` | 92 | 15 | 79 | 68% (63/92) | 73% (67/92) | 54% (50/92) | 86% | partial | not confused (-0.05) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 58 | 63% (38/60) | 65% (39/60) | 33% (20/60) | 90% | partial | not confused (-0.07) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 17 | 86% (19/22) | 55% (12/22) | 14% (3/22) | 64% | partial | **confused** (+0.20) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 1 | 60% (6/10) | 10% (1/10) | 0% (0/10) | 30% | **unsupported** | **confused** (+0.38) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 27 | 90% (27/30) | 87% (26/30) | 50% (15/30) | 93% | supported | **confused** (+0.12) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 134 | 10 | 61 | 27% (36/134) | 24% (32/134) | 13% (17/134) | 42% | partial | **confused** (+0.20) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 0 | 11% (1/9) | 0% (0/9) | 0% (0/9) | – | **unsupported** — <multiple-rest> never emitted | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 69 | 53 | 70 | 93% (64/69) | 97% (67/69) | 81% (56/69) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 41 | 31 | 39 | 90% (37/41) | 93% (38/41) | 71% (29/41) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 10 | 9 | 9 | 90% (9/10) | 90% (9/10) | 90% (9/10) | – | supported | not confused (-0.12) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.66) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | unclear (+0.34) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.39) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.92) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 15 | 41% (11/27) | 48% (13/27) | 7% (2/27) | – | partial | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 35 | 32 | 34 | 88% (28/32) | 91% (29/32) | 81% (26/32) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 12 | 9 | 10 | 78% (7/9) | 78% (7/9) | 56% (5/9) | – | partial | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 11 | 8 | 14 | 63% (5/8) | 63% (5/8) | 63% (5/8) | – | partial | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 3 | 3 | 2 | 67% (2/3) | 67% (2/3) | 67% (2/3) | – | partial | not confused (-0.46) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 3 | 3 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 5 | 67% (2/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.32) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 3 | 50% (1/2) | 50% (1/2) | 50% (1/2) | – | partial — low n (2) | not confused (-0.49) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 0 | 50% (1/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — low n (2) | not confused (-0.34) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 14 | 11 | 12 | 82% (9/11) | 82% (9/11) | 73% (8/11) | – | supported | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 5 | 5 | 5 | 80% (4/5) | 100% (5/5) | 60% (3/5) | – | supported | not confused (+0.06) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 8 | 7 | 8 | 71% (5/7) | 71% (5/7) | 43% (3/7) | – | partial | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.27) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.17) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 6 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.28) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 32 | 5 | 18 | 50% (16/32) | 38% (12/32) | 25% (8/32) | – | partial | not confused (-0.15) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 53 | 17 | 42 | 47% (25/53) | 49% (26/53) | 28% (15/53) | 53% | partial | not confused (-0.07) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 20 | 68% (19/28) | 68% (19/28) | 64% (18/28) | 68% | partial | not confused (+0.00) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 47 | 9 | 35 | 60% (28/47) | 60% (28/47) | 40% (19/47) | 60% | partial | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 14% | **unsupported** — <accidental> never emitted | not confused (-0.05) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | 0% | **unsupported** — <accidental> never emitted | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 0 | 33% (3/9) | 11% (1/9) | 33% (3/9) | 11% | **unsupported** — <accidental> never emitted | not confused (-0.01) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.43) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 0 | 0% (0/22) | 0% (0/22) | 0% (0/22) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.40) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 0 | 0% (0/12) | 0% (0/12) | 0% (0/12) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.32) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | **unsupported** — element never emitted; low n (1) | unclear (+0.26) | element on the aligned note |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 50% (1/2) | 50% (1/2) | 50% | **unsupported** — element never emitted; low n (2) | not confused (-0.00) | element on the aligned note |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 13 | 8 | 3 | 30% (3/10) | 30% (3/10) | 40% (4/10) | – | partial | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 34 | 21 | 20 | 48% (12/25) | 48% (12/25) | 36% (9/25) | – | partial | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 57 | 42 | 53 | 64% (32/50) | 64% (32/50) | 46% (23/50) | – | partial | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.20) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 0 | 0% (0/18) | 0% (0/18) | 0% (0/18) | – | **unsupported** — element never emitted | **confused** (+0.22) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.62) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.57) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.56) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.11) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.62) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 9 | 4 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (-0.23) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | – | **unsupported** — element never emitted | not confused (-0.35) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 0 | 0% (0/89) | 0% (0/89) | 0% (0/89) | – | **unsupported** — element never emitted | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 7 | 7 | 6 | 29% (2/7) | 29% (2/7) | 57% (4/7) | – | partial | not confused (+0.04) | first measure has the pickup length (sem) |
| `tuplet-3` | 46 | 7 | 68 | 32% (35/110) | 30% (33/110) | 16% (18/110) | 76% | partial | not confused (-0.07) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 85% | **unsupported** — element never emitted | not confused (+0.02) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 17 | 43% (19/44) | 27% (12/44) | 0% (0/44) | 93% | partial | not confused (-0.10) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 100% | partial | not confused (-0.09) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 6 | 37% (13/35) | 14% (5/35) | 17% (6/35) | 86% | **unsupported** | not confused (-0.08) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 88% | **unsupported** — element never emitted | not confused (-2.46) | duration + <time-modification> |
| `tie` | 79 | 14 | 6 | 3% (2/79) | 0% (0/79) | 0% (0/79) | 95% | **unsupported** | **confused** (+0.07) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 0% (0/46) | 0% (0/46) | 91% | **unsupported** — element never emitted | not confused (+0.00) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-1.17) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.14) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-1.39) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.19) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 62 | 13 | 0 | 0% (0/62) | 0% (0/62) | 0% (0/62) | 68% | **unsupported** — element never emitted | not confused (+0.02) | element on the aligned note |
| `staccato` | 66 | 6 | 0 | 0% (0/66) | 0% (0/66) | 0% (0/66) | 94% | **unsupported** — element never emitted | not confused (-0.12) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `accent` | 23 | 6 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `tenuto` | 37 | 6 | 0 | 0% (0/37) | 0% (0/37) | 0% (0/37) | 95% | **unsupported** — element never emitted | not confused (-0.06) | element on the aligned note |
| `marcato` | 23 | 3 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (+0.04) | element on the aligned note |
| `fermata` | 49 | 18 | 0 | 0% (0/49) | 0% (0/49) | 0% (0/49) | 90% | **unsupported** — element never emitted | not confused (-0.05) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 87% | **unsupported** — element never emitted | not confused (-0.10) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.00) | element on the aligned note |
| `dyn-pp` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 26 | 12 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | – | **unsupported** — element never emitted | **confused** (+0.10) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 13 | 11 | 0 | 0% (0/13) | 0% (0/13) | 0% (0/13) | – | **unsupported** — element never emitted | not confused (-0.08) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 11 | 7 | 0 | 0% (0/11) | 0% (0/11) | 0% (0/11) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 6 | 3 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (+0.09) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 21 | 10 | 0 | 0% (0/21) | 0% (0/21) | 0% (0/21) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 20 | 10 | 0 | 0% (0/20) | 0% (0/20) | 0% (0/20) | – | **unsupported** — element never emitted | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `pedal` | 26 | 4 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 0 | 0% (0/112) | 0% (0/112) | 0% (0/112) | 90% | **unsupported** — element never emitted | not confused (-0.23) | element on the aligned note |
| `text-expression` | 20 | 6 | 0 | 0% (0/19) | 0% (0/19) | 0% (0/19) | – | **unsupported** — element never emitted | **confused** (+0.09) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 37 | 34 | 0 | 0% (0/38) | 0% (0/38) | 0% (0/38) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `metronome` | 16 | 14 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | – | **unsupported** — element never emitted | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 11 | 4 | 0 | 0% (0/11) | 0% (0/11) | 0% (0/11) | – | **unsupported** — element never emitted | **confused** (+0.09) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 30 | 1 | 0 | 0% (0/30) | 0% (0/30) | 0% (0/30) | – | **unsupported** — element never emitted | not confused (-0.11) | same element/value at the aligned measure (+-1) |
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
| `barline-double` | 36 | 11 | 0 | 0% (0/36) | 0% (0/36) | 0% (0/36) | – | **unsupported** — element never emitted | not confused (+0.05) | same element/value at the aligned measure (+-1) |
| `barline-final` | 69 | 55 | 73 | 96% (54/56) | 93% (52/56) | 82% (46/56) | – | supported | not confused (-0.11) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 9 | 4 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 13 | 4 | 0 | 0% (0/13) | 0% (0/13) | 0% (0/13) | – | **unsupported** — element never emitted | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `volta-1` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `volta-2` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `segno` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.25) | same element/value at the aligned measure (+-1) |
| `coda` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.25) | same element/value at the aligned measure (+-1) |
| `dc` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `ds` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.80) | same element/value at the aligned measure (+-1) |
| `fine` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `system-break` | 177 | 62 | 0 | 0% (0/177) | 0% (0/177) | 0% (0/177) | – | **unsupported** — element never emitted | not confused (-0.10) | same element/value at the aligned measure (+-1) |
| `page-break` | 3 | 3 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `multi-page` | 4 | 3 | 0 | 85% (106/124) | 84% (104/124) | 35% (44/124) | – | supported | not confused (-0.01) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 172 | 5 | 153 | 82% (127/155) | 78% (121/155) | 41% (63/155) | 97% | partial | not confused (-0.21) | lyric on the aligned note |
| `lyrics-multi-verse` | 33 | 1 | 15 | 94% (31/33) | 94% (31/33) | 0% (0/33) | 100% | supported | not confused (+0.00) | lyric on the aligned note |
| `lyrics-melisma` | 11 | 5 | 18 | 47% (7/15) | 40% (6/15) | 27% (4/15) | 100% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-extender` | 15 | 5 | 11 | 36% (5/14) | 29% (4/14) | 21% (3/14) | 100% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-hyphen` | 37 | 5 | 32 | 79% (27/34) | 76% (26/34) | 38% (13/34) | 97% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-elision` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric on the aligned note |
| `lyrics-non-ascii` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric on the aligned note |
| `stanza-text` | 0 | 0 | – | – | – | – | – | no items yet | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

## Generator-specific extra tags (not measured)

Tags outside the taxonomy that the generators record in `meta.json` (detail counts with no MusicXML element of their own, e.g. rest positions or minor-key flags). They are listed for completeness; the symbols they refine are scored above.

| Tag | Occurrences | Items |
|---|---:|---|
| `x-acc-courtesy-paren` | 6 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `x-group-bracket` | 1 | `layouts/choir-closed-satb-light-of-morning` |
| `x-inverted-mordent` | 5 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola` |
| `x-inverted-turn` | 2 | `marks/mk02-ornaments-fermatas-flute` |
| `x-key-cancel` | 5 | `pitch/pitch-cov-key-changes-organ` |
| `x-key-minor` | 16 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-minor-flats`, `pitch/pitch-cov-keys-minor-sharps` |
| `x-measures` | 80 | `layouts/choir-closed-satb-light-of-morning`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/piano-grand-staff-prelude`, `layouts/voice-piano-night-song` |
| `x-multi-staff-part` | 2 | `layouts/piano-grand-staff-prelude`, `layouts/voice-piano-night-song` |
| `x-parts` | 10 | `layouts/choir-closed-satb-light-of-morning`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/piano-grand-staff-prelude`, `layouts/voice-piano-night-song` |
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
| `x-staves` | 12 | `layouts/choir-closed-satb-light-of-morning`, `layouts/melody-cello-elegy-2page`, `layouts/melody-flute-air`, `layouts/melody-lyrics-morning-song`, `layouts/piano-grand-staff-prelude`, `layouts/voice-piano-night-song` |
| `x-tie-across-page` | 3 | `time/t08-ties-systems-pages` |
| `x-time-courtesy` | 24 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano`, `time/t04-pickup-song`, `time/t05-triplets-duplets`, `time/t07-nested-tuplets`, `time/t08-ties-systems-pages`, `time/t10-quartet-meters` |
| `x-to-coda` | 1 | `structure/str04-segno-coda-ds` |

## Layouts

Layout score = mean of part-count match (exact), part-name score and the share of recognised notes that landed in the right part (from eval.mjs). Status from the `scan` input with the same thresholds.

| Layout | Items | Layout score clean | Layout score scan | Layout score scan-severe | Part count ok | Names | Right part | Split violations | Aggregate | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `melody` | 32 | 97% | 96% | 86% | 100% | 88% | 100% | 0 | 0.839 | supported |
| `melody-lyrics` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.899 | supported |
| `piano` | 15 | 100% | 100% | 83% | 100% | 100% | 100% | 0 | 0.904 | supported |
| `voice-piano` | 3 | 100% | 100% | 47% | 100% | 100% | 100% | 0 | 0.952 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-open-satb` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `choir-sab` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `choir-ttbb` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `choir-ssaa` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `choir-piano` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `organ` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.834 | supported |
| `string-quartet` | 5 | 86% | 94% | 60% | 100% | 85% | 98% | 0 | 0.939 | supported |
| `orchestral` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `lead-sheet` | 1 | 100% | 100% | 33% | 100% | 100% | 100% | 0 | 0.961 | supported |
| `hymnal-stanzas` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `divisi` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `cross-staff` | 0 | – | – | – | – | – | – | – | – | no items yet |
| `two-voices-one-staff-instrument` | 2 | 58% | 58% | 58% | 50% | 50% | 75% | 1 | 0.747 | partial |
| `percussion-none` | 0 | – | – | – | – | – | – | – | – | no items yet |

## Performance

Source: `mvp/work/eval-coverage.json` (all coverage items (no perf family yet); 186 PDFs; raster 200 dpi, OCR on, 64 parallel jobs on 192 CPUs, load average 402.7 at the start). Times are the converter (`convert()`) in a Node child process, per page; peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. With a fixed raster dpi the source scan dpi changes image quality, not pixel count; use `--dpi native` (raster at the scan resolution) or `--dpi app` (browser app: 2300 px wide) to measure the dpi effect.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 4 | 4.582 | 12679 | 14775 | 252.6 | 353.3 |
| 110 | 2 | 4.555 | 13058 | 13058 | 255.5 | 255.5 |
| 120 | 5 | 4.546 | 2603 | 4179 | 238.3 | 254.3 |
| 150 | 28 | 4.379 | 3914 | 19537 | 264.8 | 544.2 |
| 200 | 34 | 4.06 | 4524 | 15836 | 243.4 | 384.2 |
| 240 | 1 | 3.873 | 1706 | 1706 | 257.4 | 257.4 |
| 250 | 14 | 3.972 | 3277 | 11473 | 248.2 | 274.4 |
| 300 | 98 | 3.869 | 3966 | 16223 | 235.1 | 445 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 10.0x12.9in | 1 | 5.153 | 2550 | 2550 | 238.3 | 238.3 |
| 13.0x17.9in landscape | 1 | 9.314 | 3469 | 3469 | 406.8 | 406.8 |
| 8.8x12.0in | 4 | 4.23 | 4524 | 4836 | 239.9 | 245.1 |
| 8.8x12.1in | 2 | 4.277 | 19537 | 19537 | 544.2 | 544.2 |
| 8.9x12.1in | 7 | 4.31 | 4066 | 14775 | 274.4 | 300.3 |
| 8.9x12.3in | 1 | 4.411 | 2745 | 2745 | 279.9 | 279.9 |
| 8.9x12.4in | 1 | 4.413 | 11490 | 11490 | 266.3 | 266.3 |
| 9.0x12.2in | 2 | 4.39 | 4961 | 4961 | 267.4 | 267.4 |
| 9.1x12.2in | 5 | 4.442 | 5442 | 16223 | 246 | 273.1 |
| 9.1x12.3in | 1 | 4.449 | 3521 | 3521 | 260.8 | 260.8 |
| 9.1x12.5in | 6 | 4.55 | 3023 | 12916 | 260.9 | 363.2 |
| 9.3x12.4in | 3 | 4.584 | 6720 | 8627 | 252.6 | 266.1 |
| 9.3x12.7in | 3 | 4.697 | 5634 | 5930 | 296.4 | 389.5 |
| 9.4x12.5in | 1 | 4.727 | 3607 | 3607 | 262.8 | 262.8 |
| 9.5x12.5in | 1 | 4.734 | 10739 | 10739 | 264.8 | 264.8 |
| 9.6x12.6in | 2 | 4.864 | 4179 | 4179 | 254.3 | 254.3 |
| A3 landscape | 1 | 7.742 | 5643 | 5643 | 489.3 | 489.3 |
| A4 | 143 | 3.869 | 3922 | 15836 | 238 | 445 |
| A4 landscape | 1 | 3.871 | 2808 | 2808 | 258.8 | 258.8 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 179 | 3.871 | 4061 | 19537 | 239.1 | 544.2 |
| 2 | 7 | 3.869 | 1989 | 4279 | 268.9 | 445 |

**Linear fits.** ms per page = 3859.2 + **287.69 ms per megapixel** × MP per page (n=186, R²=0.002). Peak MB = 143.9 + 25.75 MB per megapixel × total MP (n=186, R²=0.229). Overall: 1211 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 1.000 | 1.000 | 0.986 | 4 → 4 | 4470 | 246 |
| `layouts/melody-cello-elegy-2page` | melody | 0.824 | 0.855 | 0.691 | 1 → 1 | 1706 | 257 |
| `layouts/melody-flute-air` | melody | 0.941 | 0.957 | 0.961 | 1 → 1 | 3404 | 241 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 0.887 | 0.887 | 0.841 | 1 → 1 | 2327 | 239 |
| `layouts/piano-grand-staff-prelude` | piano | 0.876 | 0.920 | 0.910 | 1 → 1 | 2021 | 235 |
| `layouts/voice-piano-night-song` | voice-piano | 0.971 | 0.923 | 0.424 | 2 → 2 | 2539 | 253 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.971 | 1 → 1 | 5171 | 248 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 11473 | 248 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.978 | 0.944 | 0.789 | 1 → 1 | 4860 | 249 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.933 | 0.910 | 0.810 | 1 → 1 | 2732 | 231 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.750 | 0.736 | 0.893 | 1 → 1 | 9074 | 253 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.957 | 0.961 | 0.367 | 1 → 1 | 11564 | 246 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.984 | 0.997 | 0.858 | 2 → 2 | 11412 | 248 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.963 | 0.923 | 4 → 4 | 9759 | 270 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.935 | 0.905 | 1 → 1 | 6547 | 242 |
| `notes/nt01-note-values` | melody | 0.814 | 0.827 | 0.681 | 1 → 1 | 7505 | 261 |
| `notes/nt02-dots` | melody | 0.841 | 0.824 | 0.797 | 1 → 1 | 2486 | 231 |
| `notes/nt03-chords` | piano | 0.894 | 0.840 | 0.859 | 1 → 1 | 13385 | 249 |
| `notes/nt04-beams` | melody | 0.909 | 0.915 | 0.901 | 1 → 1 | 6855 | 242 |
| `notes/nt05-flags-stems` | melody | 0.812 | 0.806 | 0.759 | 1 → 1 | 8846 | 243 |
| `notes/nt06-ledger-lines` | piano | 0.946 | 0.913 | 0.913 | 1 → 1 | 5521 | 265 |
| `notes/nt07-grace-notes` | melody | 0.924 | 0.806 | 0.730 | 1 → 1 | 1810 | 240 |
| `notes/nt08-cue-notes` | melody | 0.906 | 0.944 | 0.903 | 1 → 1 | 6995 | 240 |
| `notes/nt09-tremolos` | piano | 0.720 | 0.722 | 0.680 | 1 → 1 | 4228 | 243 |
| `notes/nt10-piano-etude` | piano | 0.939 | 0.930 | 0.914 | 1 → 1 | 11520 | 258 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.851 | 0.832 | 0.813 | 1 → 1 | 7014 | 231 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.819 | 0.822 | 0.749 | 1 → 1 | 3204 | 214 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.907 | 0.982 | 0.367 | 1 → 1 | 4767 | 247 |
| `pitch/pitch-cov-clefs-all` | melody | 0.737 | 0.726 | 0.676 | 1 → 1 | 4291 | 241 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.759 | 0.959 | 0.756 | 4 → 4 | 4214 | 242 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.850 | 0.834 | 0.730 | 1 → 1 | 2684 | 260 |
| `pitch/pitch-cov-keys-major-flats` | piano | 0.881 | 0.883 | 0.578 | 1 → 1 | 4674 | 247 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.890 | 0.810 | 0.785 | 1 → 1 | 3901 | 228 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.851 | 0.827 | 0.779 | 1 → 1 | 2606 | 227 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.589 | 0.564 | 0.612 | 1 → 1 | 2854 | 248 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 0.838 | 0.838 | 0.787 | 1 → 1 | 1948 | 231 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.809 | 0.795 | 0.803 | 1 → 1 | 1802 | 235 |
| `rests/rst01-rest-values` | melody | 0.809 | 0.735 | 0.676 | 1 → 1 | 1864 | 244 |
| `rests/rst02-dotted-rests` | melody | 0.832 | 0.848 | 0.744 | 1 → 1 | 5623 | 239 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.768 | 0.777 | 0.579 | 1 → 1 | 3544 | 253 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.714 | 0.786 | 0.811 | 1 → 1 | 2171 | 239 |
| `rests/rst05-multibar-rests` | melody | 0.722 | 0.706 | 0.622 | 1 → 1 | 3421 | 245 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.610 | 0.623 | 0.620 | 1 → 2 | 2408 | 238 |
| `rests/rst07-piano-rests` | piano | 0.905 | 0.906 | 0.836 | 1 → 1 | 2878 | 213 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.838 | 0.804 | 0.367 | 1 → 1 | 4793 | 238 |
| `rests/rst09-quartet-rests` | string-quartet | 0.995 | 0.961 | 0.953 | 4 → 4 | 4206 | 299 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 1864 | 235 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.754 | 1 → 1 | 1919 | 239 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.448 | 4 → 4 | 5382 | 350 |
| `structure/str04-segno-coda-ds` | melody | 0.878 | 0.883 | 0.909 | 1 → 1 | 4805 | 224 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.367 | 1 → 1 | 3966 | 243 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.972 | 0.935 | 0.201 | 2 → 2 | 4279 | 432 |
| `time/t01-simple-meters` | melody | 0.858 | 0.866 | 0.847 | 1 → 1 | 2399 | 243 |
| `time/t02-compound-irregular` | melody | 0.875 | 0.875 | 0.897 | 1 → 1 | 3277 | 253 |
| `time/t03-common-cut-piano` | piano | 0.961 | 0.974 | 0.940 | 1 → 1 | 3294 | 238 |
| `time/t04-pickup-song` | melody-lyrics | 0.911 | 0.911 | 0.926 | 1 → 1 | 3112 | 239 |
| `time/t05-triplets-duplets` | melody | 0.794 | 0.824 | 0.805 | 1 → 1 | 4507 | 248 |
| `time/t06-quint-sext-sept` | melody | 0.938 | 0.912 | 0.834 | 1 → 1 | 2589 | 264 |
| `time/t07-nested-tuplets` | melody | 0.807 | 0.772 | 0.810 | 1 → 1 | 2188 | 244 |
| `time/t08-ties-systems-pages` | piano | 0.948 | 0.970 | 0.404 | 1 → 1 | 2000 | 276 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.871 | 0.871 | 0.744 | 1 → 1 | 2036 | 209 |
| `time/t10-quartet-meters` | string-quartet | 0.857 | 0.830 | 0.617 | 4 → 4 | 2060 | 242 |
