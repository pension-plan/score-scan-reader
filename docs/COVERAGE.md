# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 09:13 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage-text.json` (eval 2026-11-08 09:11, app source hash `984f2a856a04`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 81 items, 243 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

**Scope of this matrix:** the symbol and layout tables use every coverage family except `perf` (`mvp/work/eval-coverage-text.json` = the coverage eval of the text/dynamics round without the 21 perf items, which repeat one hymn page, one piano page and one piano book at several resolutions and would count the same notes up to 8 times). The performance tables come from the native-dpi perf run (`mvp/work/eval-coverage-baseline-perf.json`). The previous matrix (22 supported, 40 partial, 92 unsupported) was measured on the source at commit e94a0a1; this one is the source of the text/dynamics round (dynamics, hairpins, tempo and expression text now written).

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

**Totals:** 35 supported, 46 partial, 73 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | 75% | **unsupported** | not confused (+0.03) | duration of the aligned note (sem) |
| `note-whole` | 163 | 37 | 132 | 54% (102/188) | 46% (86/188) | 26% (49/188) | 61% | partial | not confused (-0.03) | duration of the aligned note (sem) |
| `note-half` | 1351 | 75 | 1354 | 83% (1228/1471) | 79% (1158/1471) | 36% (525/1471) | 91% | partial | not confused (-0.05) | duration of the aligned note (sem) |
| `note-quarter` | 4025 | 80 | 4492 | 91% (4023/4426) | 91% (4010/4426) | 68% (3022/4426) | 94% | supported | not confused (-0.12) | duration of the aligned note (sem) |
| `note-8th` | 1526 | 61 | 1650 | 79% (1269/1608) | 77% (1238/1608) | 64% (1035/1608) | 84% | partial | not confused (-0.01) | duration of the aligned note (sem) |
| `note-16th` | 651 | 22 | 744 | 79% (516/651) | 80% (521/651) | 69% (452/651) | 89% | supported | not confused (+0.00) | duration of the aligned note (sem) |
| `note-32nd` | 113 | 10 | 11 | 11% (12/113) | 13% (15/113) | 4% (4/113) | 81% | **unsupported** | not confused (-0.01) | duration of the aligned note (sem) |
| `note-64th` | 71 | 5 | 0 | 0% (0/71) | 0% (0/71) | 0% (0/71) | 76% | **unsupported** | not confused (+0.04) | duration of the aligned note (sem) |
| `dot` | 295 | 49 | 323 | 68% (203/299) | 70% (208/299) | 52% (154/299) | 88% | partial | **confused** (+0.08) | <dot/> count + duration |
| `double-dot` | 15 | 4 | 6 | 27% (4/15) | 27% (4/15) | 7% (1/15) | 87% | partial | **confused** (+0.17) | <dot/> count + duration |
| `chord` | 608 | 29 | 1634 | 89% (1480/1666) | 88% (1459/1666) | 68% (1125/1666) | 90% | supported | not confused (-0.01) | element on the aligned note |
| `beam` | 703 | 56 | 0 | 0% (0/2064) | 0% (0/2064) | 0% (0/2064) | 86% | **unsupported** — element never emitted | not confused (-0.00) | element on the aligned note |
| `flag` | 308 | 31 | 1548 | 61% (187/308) | 62% (190/308) | 49% (150/308) | 77% | partial | not confused (+0.01) | duration of the flagged note (sem) |
| `stem-up` | 2653 | 67 | 2673 | 90% (2387/2653) | 88% (2347/2653) | 68% (1811/2653) | 89% | supported | not confused (-0.13) | element on the aligned note |
| `stem-down` | 4155 | 72 | 3915 | 91% (3783/4155) | 90% (3732/4155) | 73% (3051/4155) | 91% | supported | not confused (-0.29) | element on the aligned note |
| `ledger-above` | 601 | 58 | 568 | 90% (543/601) | 87% (521/601) | 76% (457/601) | 87% | supported | not confused (-0.03) | pitch (sem) |
| `ledger-below` | 374 | 45 | 350 | 89% (333/374) | 89% (331/374) | 66% (247/374) | 89% | supported | not confused (-0.02) | pitch (sem) |
| `grace` | 58 | 2 | 0 | 0% (0/58) | 0% (0/58) | 0% (0/58) | 0% | **unsupported** — element never emitted | not confused (-0.08) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 16 | 2 | 0 | 0% (0/16) | 0% (0/16) | 0% (0/16) | 0% | **unsupported** — element never emitted | not confused (-0.07) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.40) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 35 | 1 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 31% | **unsupported** — element never emitted | not confused (-0.84) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | 100% | **unsupported** — low n (2) | – | aligned rest with the same duration (sem) |
| `rest-whole` | 3 | 1 | 2 | 100% (3/3) | 100% (3/3) | 0% (0/3) | 100% | supported | not confused (-0.63) | aligned rest with the same duration (sem) |
| `rest-half` | 36 | 15 | 32 | 75% (27/36) | 67% (24/36) | 67% (24/36) | 75% | partial | not confused (+0.03) | aligned rest with the same duration (sem) |
| `rest-quarter` | 183 | 33 | 137 | 76% (139/183) | 70% (129/183) | 42% (77/183) | 75% | partial | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-8th` | 124 | 16 | 114 | 77% (96/124) | 81% (100/124) | 66% (82/124) | 92% | supported | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-16th` | 60 | 7 | 59 | 65% (39/60) | 67% (40/60) | 38% (23/60) | 92% | partial | not confused (+0.02) | aligned rest with the same duration (sem) |
| `rest-32nd` | 22 | 4 | 15 | 86% (19/22) | 64% (14/22) | 14% (3/22) | 73% | partial | **confused** (+0.25) | aligned rest with the same duration (sem) |
| `rest-64th` | 10 | 1 | 1 | 60% (6/10) | 10% (1/10) | 0% (0/10) | 30% | **unsupported** | **confused** (+0.47) | aligned rest with the same duration (sem) |
| `rest-dotted` | 30 | 6 | 27 | 80% (24/30) | 87% (26/30) | 47% (14/30) | 93% | supported | **confused** (+0.18) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 202 | 14 | 190 | 79% (159/202) | 62% (126/202) | 39% (78/202) | 81% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 0 | 67% (6/9) | 44% (4/9) | 0% (0/9) | – | partial — <multiple-rest> never emitted | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 105 | 71 | 106 | 98% (103/105) | 99% (104/105) | 88% (92/105) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 63 | 45 | 62 | 95% (60/63) | 97% (61/63) | 76% (48/63) | – | supported | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 14 | 13 | 13 | 93% (13/14) | 93% (13/14) | 93% (13/14) | – | supported | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 5 | 3 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.67) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 6 | 5 | 5 | 83% (5/6) | 83% (5/6) | 67% (4/6) | – | supported | not confused (-0.01) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | unclear (+0.38) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | **confused** (+0.91) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 27 | 4 | 17 | 48% (13/27) | 56% (15/27) | 7% (2/27) | – | partial | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 40 | 37 | 50 | 97% (36/37) | 97% (36/37) | 92% (34/37) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 18 | 15 | 31 | 87% (13/15) | 87% (13/15) | 80% (12/15) | – | supported | **confused** (+0.14) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 12 | 9 | 25 | 100% (9/9) | 89% (8/9) | 89% (8/9) | – | supported | not confused (-0.07) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 6 | 5 | 8 | 83% (5/6) | 83% (5/6) | 83% (5/6) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 4 | 4 | 3 | 75% (3/4) | 75% (3/4) | 25% (1/4) | – | partial | not confused (+0.00) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 3 | 3 | 2 | 67% (2/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 2 | 2 | 0 | 50% (1/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — low n (2) | not confused (-0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 16 | 13 | 19 | 100% (13/13) | 100% (13/13) | 77% (10/13) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 7 | 7 | 10 | 100% (7/7) | 100% (7/7) | 86% (6/7) | – | supported | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 9 | 8 | 11 | 100% (8/8) | 100% (8/8) | 50% (4/8) | – | supported | **confused** (+0.16) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 3 | 3 | 2 | 100% (3/3) | 67% (2/3) | 33% (1/3) | – | partial | not confused (-0.05) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 50% (1/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 0% (0/2) | – | partial — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 0% (0/2) | – | supported — low n (2) | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 34 | 6 | 23 | 79% (27/34) | 68% (23/34) | 35% (12/34) | – | partial | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 78 | 22 | 68 | 59% (46/78) | 71% (55/78) | 45% (35/78) | 71% | partial | not confused (+0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 28 | 6 | 23 | 75% (21/28) | 75% (21/28) | 93% (26/28) | 75% | partial | not confused (-0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 53 | 10 | 46 | 81% (43/53) | 81% (43/53) | 58% (31/53) | 81% | supported | not confused (+0.00) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 7 | 3 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 29% | **unsupported** — <accidental> never emitted | not confused (+0.05) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 5 | 2 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | 0% | **unsupported** — <accidental> never emitted | not confused (+0.08) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 9 | 2 | 0 | 22% (2/9) | 22% (2/9) | 56% (5/9) | 22% | partial — <accidental> never emitted | not confused (-0.02) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 4 | 2 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.43) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 4 | 2 | 0 | 0% (0/22) | 0% (0/22) | 0% (0/22) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.40) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 2 | 2 | 0 | 0% (0/12) | 0% (0/12) | 0% (0/12) | 0% | **unsupported** — <octave-shift> never emitted | **confused** (+0.32) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 0% (0/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | not confused (+0.03) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (+0.12) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 14 | 9 | 4 | 27% (3/11) | 36% (4/11) | 45% (5/11) | – | partial | **confused** (+0.18) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 38 | 25 | 30 | 55% (16/29) | 55% (16/29) | 52% (15/29) | – | partial | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 69 | 54 | 92 | 69% (43/62) | 69% (43/62) | 53% (33/62) | – | partial | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.16) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 21 | 15 | 0 | 0% (0/18) | 0% (0/18) | 0% (0/18) | – | **unsupported** — element never emitted | **confused** (+0.16) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.47) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 5 | 4 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | not confused (-0.43) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 3 | 2 | 0 | 0% (0/3) | 0% (0/3) | 0% (0/3) | – | **unsupported** — element never emitted | not confused (-0.49) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 7 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.52) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 11 | 6 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.00) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 10 | 5 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | – | **unsupported** — element never emitted | not confused (-0.31) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 110 | 20 | 0 | 0% (0/89) | 0% (0/89) | 0% (0/89) | – | **unsupported** — element never emitted | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 9 | 9 | 7 | 56% (5/9) | 44% (4/9) | 67% (6/9) | – | partial | not confused (+0.12) | first measure has the pickup length (sem) |
| `tuplet-3` | 76 | 8 | 168 | 67% (133/200) | 67% (133/200) | 40% (80/200) | 93% | partial | not confused (-0.00) | duration + <time-modification> ratio |
| `tuplet-2` | 15 | 6 | 0 | 0% (0/27) | 0% (0/27) | 0% (0/27) | 85% | **unsupported** — element never emitted | not confused (+0.01) | duration + <time-modification> ratio |
| `tuplet-5` | 10 | 4 | 29 | 45% (20/44) | 45% (20/44) | 34% (15/44) | 95% | partial | not confused (-0.13) | duration + <time-modification> ratio |
| `tuplet-6` | 6 | 2 | 24 | 67% (24/36) | 67% (24/36) | 44% (16/36) | 89% | partial | not confused (-0.07) | duration + <time-modification> ratio |
| `tuplet-7` | 5 | 2 | 21 | 40% (14/35) | 40% (14/35) | 40% (14/35) | 100% | partial | not confused (-0.07) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 100% | **unsupported** — element never emitted | not confused (-1.00) | duration + <time-modification> |
| `tie` | 79 | 14 | 4 | 0% (0/79) | 0% (0/79) | 0% (0/79) | 95% | **unsupported** | **confused** (+0.06) | element on the aligned note |
| `tie-across-system` | 46 | 11 | 0 | 0% (0/46) | 0% (0/46) | 0% (0/46) | 93% | **unsupported** — element never emitted | not confused (+0.03) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-0.92) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 4 | 3 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.12) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (-1.17) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.18) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 100 | 20 | 0 | 0% (0/100) | 0% (0/100) | 0% (0/100) | 79% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `staccato` | 78 | 7 | 0 | 0% (0/78) | 0% (0/78) | 0% (0/78) | 95% | **unsupported** — element never emitted | not confused (-0.08) | element on the aligned note |
| `staccatissimo` | 9 | 2 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 89% | **unsupported** — element never emitted | not confused (-0.01) | element on the aligned note |
| `accent` | 43 | 8 | 0 | 0% (0/43) | 0% (0/43) | 0% (0/43) | 79% | **unsupported** — element never emitted | **confused** (+0.13) | element on the aligned note |
| `tenuto` | 37 | 6 | 0 | 0% (0/37) | 0% (0/37) | 0% (0/37) | 97% | **unsupported** — element never emitted | not confused (-0.07) | element on the aligned note |
| `marcato` | 23 | 3 | 0 | 0% (0/23) | 0% (0/23) | 0% (0/23) | 87% | **unsupported** — element never emitted | not confused (+0.04) | element on the aligned note |
| `fermata` | 130 | 32 | 0 | 0% (0/130) | 0% (0/130) | 0% (0/130) | 86% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `trill` | 9 | 3 | 0 | 0% (0/9) | 0% (0/9) | 0% (0/9) | 100% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `mordent` | 5 | 2 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | 100% | **unsupported** — element never emitted | not confused (+0.05) | element on the aligned note |
| `turn` | 5 | 2 | 0 | 0% (0/7) | 0% (0/7) | 0% (0/7) | 100% | **unsupported** — element never emitted | not confused (+0.06) | element on the aligned note |
| `arpeggio` | 24 | 3 | 0 | 0% (0/68) | 0% (0/68) | 0% (0/68) | 88% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `breath` | 8 | 4 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.02) | element on the aligned note |
| `dyn-pp` | 8 | 5 | 8 | 75% (6/8) | 75% (6/8) | 50% (4/8) | – | partial | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 43 | 19 | 33 | 58% (25/43) | 77% (33/43) | 42% (18/43) | – | partial | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 13 | 9 | 15 | 85% (11/13) | 100% (13/13) | 23% (3/13) | – | supported | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 54 | 25 | 29 | 87% (47/54) | 43% (23/54) | 28% (15/54) | – | partial | not confused (-0.00) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 56 | 18 | 43 | 77% (43/56) | 77% (43/56) | 61% (34/56) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 16 | 5 | 14 | 75% (12/16) | 88% (14/16) | 81% (13/16) | – | supported | **confused** (+0.10) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 6 | 3 | 3 | 67% (4/6) | 50% (3/6) | 17% (1/6) | – | partial | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 43 | 18 | 37 | 86% (37/43) | 86% (37/43) | 26% (11/43) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 31 | 15 | 28 | 84% (26/31) | 84% (26/31) | 19% (6/31) | – | supported | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `pedal` | 28 | 5 | 0 | 0% (0/28) | 0% (0/28) | 0% (0/28) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `fingering` | 112 | 3 | 0 | 0% (0/112) | 0% (0/112) | 0% (0/112) | 89% | **unsupported** — element never emitted | not confused (-0.04) | element on the aligned note |
| `text-expression` | 45 | 11 | 7 | 14% (5/35) | 20% (7/35) | 17% (6/35) | – | partial | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 59 | 53 | 39 | 53% (36/68) | 54% (37/68) | 32% (22/68) | – | partial | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `metronome` | 36 | 33 | 0 | 0% (0/36) | 0% (0/36) | 0% (0/36) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
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
| `barline-final` | 94 | 80 | 143 | 96% (78/81) | 94% (76/81) | 86% (70/81) | – | supported | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 25 | 6 | 0 | 0% (0/25) | 0% (0/25) | 0% (0/25) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 32 | 8 | 0 | 0% (0/32) | 0% (0/32) | 0% (0/32) | – | **unsupported** — element never emitted | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `volta-1` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `volta-2` | 8 | 5 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | – | **unsupported** — element never emitted | not confused (-0.02) | same element/value at the aligned measure (+-1) |
| `segno` | 2 | 2 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `coda` | 4 | 2 | 0 | 0% (0/4) | 0% (0/4) | 0% (0/4) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `dc` | 2 | 2 | 1 | 50% (1/2) | 50% (1/2) | 100% (2/2) | – | partial — low n (2) | **confused** (+0.20) | same element/value at the aligned measure (+-1) |
| `ds` | 2 | 2 | 2 | 100% (2/2) | 100% (2/2) | 100% (2/2) | – | supported — low n (2) | not confused (+0.09) | same element/value at the aligned measure (+-1) |
| `fine` | 2 | 2 | 1 | 100% (2/2) | 50% (1/2) | 100% (2/2) | – | partial — low n (2) | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `system-break` | 226 | 80 | 0 | 0% (0/226) | 0% (0/226) | 0% (0/226) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `page-break` | 19 | 6 | 0 | 0% (0/19) | 0% (0/19) | 0% (0/19) | – | **unsupported** — element never emitted | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `multi-page` | 22 | 6 | 0 | 96% (1837/1908) | 94% (1800/1908) | 80% (1518/1908) | – | supported | not confused (+0.02) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 0 | 0% (0/1) | 0% (0/1) | 0% (0/1) | – | **unsupported** — element never emitted; low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 895 | 15 | 606 | 86% (536/624) | 88% (550/624) | 52% (327/624) | 98% | supported | not confused (-0.30) | lyric on the aligned note |
| `lyrics-multi-verse` | 288 | 5 | 109 | 68% (96/142) | 73% (103/142) | 46% (66/142) | 100% | partial | not confused (-0.03) | lyric on the aligned note |
| `lyrics-melisma` | 39 | 10 | 39 | 70% (23/33) | 67% (22/33) | 55% (18/33) | 97% | partial | not confused (-0.01) | lyric on the aligned note |
| `lyrics-extender` | 27 | 8 | 17 | 53% (10/19) | 58% (11/19) | 42% (8/19) | 100% | partial | not confused (-0.00) | lyric on the aligned note |
| `lyrics-hyphen` | 203 | 15 | 145 | 69% (110/160) | 78% (124/160) | 57% (91/160) | 98% | partial | not confused (-0.02) | lyric on the aligned note |
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
| `melody` | 32 | 97% | 96% | 86% | 100% | 88% | 100% | 0 | 0.861 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.931 | supported |
| `piano` | 16 | 100% | 100% | 88% | 100% | 100% | 100% | 0 | 0.930 | supported |
| `voice-piano` | 3 | 100% | 100% | 48% | 100% | 100% | 100% | 0 | 0.953 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 99% | 0 | 0.925 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 6% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.985 | supported |
| `choir-piano` | 1 | 100% | 100% | 24% | 100% | 100% | 100% | 0 | 0.997 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.960 | supported |
| `string-quartet` | 6 | 86% | 95% | 57% | 100% | 88% | 98% | 0 | 0.951 | supported |
| `orchestral` | 2 | 92% | 93% | 57% | 100% | 82% | 98% | 0 | 0.966 | supported |
| `lead-sheet` | 2 | 83% | 83% | 83% | 100% | 50% | 100% | 0 | 0.940 | supported |
| `hymnal-stanzas` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.999 | supported |
| `divisi` | 2 | 100% | 96% | 99% | 100% | 88% | 100% | 0 | 0.969 | supported |
| `cross-staff` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.874 | supported |
| `two-voices-one-staff-instrument` | 3 | 89% | 89% | 89% | 100% | 67% | 100% | 0 | 0.920 | supported |
| `percussion-none` | 1 | 44% | 44% | 44% | 0% | 33% | 100% | 0 | 0.628 | partial |

## Performance

Source: `mvp/work/eval-coverage-baseline-perf.json` (perf family; 63 PDFs; raster native, OCR on, 8 parallel jobs on 192 CPUs, load average 166.9 at the start). Times are the converter (`convert()`) in a Node child process, per page; peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. Pages are rasterised at the resolution of the scan image, so pixel count follows the source dpi.

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
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 2417 | 243 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.925 | 0.879 | 4 → 4 | 2948 | 255 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 0.999 | 0.997 | 0.530 | 5 → 5 | 4153 | 321 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 3001 | 234 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.990 | 0.985 | 0.982 | 4 → 4 | 2374 | 257 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.352 | 4 → 4 | 2794 | 223 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.874 | 0.874 | 0.799 | 1 → 1 | 1963 | 231 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 4543 | 295 |
| `layouts/divisi-strings-lament` | divisi | 0.971 | 0.950 | 0.938 | 4 → 4 | 2169 | 257 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 3294 | 244 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 2949 | 240 |
| `layouts/melody-cello-elegy-2page` | melody | 0.876 | 0.843 | 0.713 | 1 → 1 | 1408 | 294 |
| `layouts/melody-flute-air` | melody | 0.959 | 0.968 | 0.961 | 1 → 1 | 1655 | 247 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 2424 | 237 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.972 | 0.957 | 0.873 | 9 → 9 | 3811 | 496 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.985 | 0.946 | 0.763 | 1 → 1 | 2441 | 234 |
| `layouts/piano-grand-staff-prelude` | piano | 0.896 | 0.942 | 0.928 | 1 → 1 | 1683 | 227 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.984 | 0.774 | 4 → 4 | 4095 | 298 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1898 | 232 |
| `layouts/voice-piano-night-song` | voice-piano | 0.972 | 0.922 | 0.459 | 2 → 2 | 2869 | 243 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.919 | 0.976 | 0.888 | 1 → 1 | 3367 | 231 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.825 | 0.832 | 0.815 | 1 → 1 | 3429 | 241 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 2048 | 230 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1809 | 231 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.978 | 0.967 | 0.799 | 1 → 1 | 2055 | 249 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.938 | 0.921 | 0.841 | 1 → 1 | 2695 | 225 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.752 | 0.940 | 0.723 | 1 → 1 | 2530 | 235 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.970 | 0.960 | 0.850 | 1 → 1 | 2643 | 237 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.980 | 1.000 | 0.904 | 2 → 2 | 2499 | 233 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.973 | 0.907 | 4 → 4 | 2631 | 239 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.920 | 0.888 | 1 → 1 | 2710 | 237 |
| `notes/nt01-note-values` | melody | 0.822 | 0.827 | 0.660 | 1 → 1 | 1907 | 248 |
| `notes/nt02-dots` | melody | 0.845 | 0.830 | 0.797 | 1 → 1 | 2360 | 240 |
| `notes/nt03-chords` | piano | 0.864 | 0.856 | 0.894 | 1 → 1 | 1785 | 237 |
| `notes/nt04-beams` | melody | 0.923 | 0.918 | 0.916 | 1 → 1 | 1873 | 255 |
| `notes/nt05-flags-stems` | melody | 0.834 | 0.847 | 0.762 | 1 → 1 | 1779 | 251 |
| `notes/nt06-ledger-lines` | piano | 0.946 | 0.946 | 0.946 | 1 → 1 | 2365 | 238 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.755 | 0.684 | 1 → 1 | 1904 | 229 |
| `notes/nt08-cue-notes` | melody | 0.936 | 0.946 | 0.947 | 1 → 1 | 1923 | 247 |
| `notes/nt09-tremolos` | piano | 0.709 | 0.709 | 0.695 | 1 → 1 | 1945 | 242 |
| `notes/nt10-piano-etude` | piano | 0.951 | 0.941 | 0.914 | 1 → 1 | 2026 | 235 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.634 | 3 → 2 | 2521 | 250 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.944 | 0.938 | 0.856 | 1 → 1 | 1792 | 238 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.853 | 0.902 | 0.836 | 1 → 1 | 1760 | 250 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1599 | 215 |
| `pitch/pitch-cov-clefs-all` | melody | 0.736 | 0.730 | 0.676 | 1 → 1 | 1704 | 232 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.769 | 0.955 | 0.756 | 4 → 4 | 1833 | 240 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.978 | 0.974 | 0.811 | 1 → 1 | 1958 | 270 |
| `pitch/pitch-cov-keys-major-flats` | piano | 0.997 | 0.997 | 0.577 | 1 → 1 | 1672 | 242 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.992 | 0.911 | 0.872 | 1 → 1 | 1683 | 215 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.967 | 0.971 | 0.885 | 1 → 1 | 1929 | 234 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.604 | 0.541 | 0.557 | 1 → 1 | 2266 | 244 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 0.838 | 0.838 | 0.787 | 1 → 1 | 1814 | 238 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.809 | 0.795 | 0.803 | 1 → 1 | 2035 | 224 |
| `rests/rst01-rest-values` | melody | 0.823 | 0.757 | 0.685 | 1 → 1 | 1670 | 230 |
| `rests/rst02-dotted-rests` | melody | 0.858 | 0.887 | 0.746 | 1 → 1 | 1895 | 238 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.768 | 0.777 | 0.577 | 1 → 1 | 1649 | 242 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.721 | 0.728 | 0.817 | 1 → 1 | 1699 | 235 |
| `rests/rst05-multibar-rests` | melody | 0.849 | 0.728 | 0.620 | 1 → 1 | 1833 | 242 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.858 | 0.840 | 1 → 1 | 1785 | 235 |
| `rests/rst07-piano-rests` | piano | 0.927 | 0.910 | 0.886 | 1 → 1 | 1803 | 240 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.835 | 0.827 | 0.367 | 1 → 1 | 2148 | 248 |
| `rests/rst09-quartet-rests` | string-quartet | 0.990 | 0.961 | 0.923 | 4 → 4 | 3125 | 325 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.953 | 1 → 1 | 1525 | 253 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.754 | 1 → 1 | 1711 | 246 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.466 | 4 → 4 | 3198 | 358 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 1931 | 214 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.877 | 1 → 1 | 1898 | 246 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.972 | 0.938 | 0.201 | 2 → 2 | 3568 | 466 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.975 | 0.664 | 7 → 7 | 2853 | 577 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.983 | 0.973 | 0.961 | 1 → 1 | 1464 | 639 |
| `time/t01-simple-meters` | melody | 0.875 | 0.875 | 0.851 | 1 → 1 | 1646 | 237 |
| `time/t02-compound-irregular` | melody | 0.897 | 0.894 | 0.909 | 1 → 1 | 1830 | 228 |
| `time/t03-common-cut-piano` | piano | 0.959 | 0.974 | 0.928 | 1 → 1 | 1618 | 230 |
| `time/t04-pickup-song` | melody-lyrics | 0.916 | 0.917 | 0.936 | 1 → 1 | 2069 | 263 |
| `time/t05-triplets-duplets` | melody | 0.817 | 0.839 | 0.803 | 1 → 1 | 1683 | 224 |
| `time/t06-quint-sext-sept` | melody | 0.971 | 0.968 | 0.914 | 1 → 1 | 1554 | 219 |
| `time/t07-nested-tuplets` | melody | 0.808 | 0.802 | 0.831 | 1 → 1 | 1538 | 220 |
| `time/t08-ties-systems-pages` | piano | 0.978 | 0.990 | 0.404 | 1 → 1 | 1480 | 269 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.906 | 0.906 | 0.765 | 1 → 1 | 1703 | 227 |
| `time/t10-quartet-meters` | string-quartet | 0.868 | 0.854 | 0.620 | 4 → 4 | 1949 | 243 |
