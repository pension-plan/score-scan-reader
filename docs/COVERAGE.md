# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 14:40 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 14:40, app source hash `cba75110a3ff`, OCR on, raster 200 dpi).
Corpus: `corpus/coverage` — 102 items, 306 scored PDFs (clean, scan, scan-severe). Every item is a short LilyPond engraving with exact MusicXML truth and a `meta.json` listing its symbols, layout and per-symbol counts.

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

**Totals:** 71 supported, 58 partial, 25 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 29 | 3 | 0 | 0% (0/29) | 0% (0/29) | 0% (0/29) | 34% | **unsupported** | **confused** (+0.10) | duration of the aligned note (sem) |
| `note-whole` | 512 | 50 | 485 | 48% (257/537) | 40% (217/537) | 24% (129/537) | 56% | partial | not confused (-0.01) | duration of the aligned note (sem) |
| `note-half` | 4857 | 96 | 4276 | 83% (4109/4977) | 71% (3530/4977) | 40% (1978/4977) | 87% | partial | not confused (+0.01) | duration of the aligned note (sem) |
| `note-quarter` | 11462 | 101 | 11949 | 86% (10174/11863) | 85% (10074/11863) | 74% (8808/11863) | 89% | supported | not confused (-0.00) | duration of the aligned note (sem) |
| `note-8th` | 9382 | 81 | 9330 | 84% (7914/9464) | 83% (7896/9464) | 75% (7083/9464) | 88% | supported | not confused (-0.02) | duration of the aligned note (sem) |
| `note-16th` | 2464 | 34 | 2642 | 75% (1842/2464) | 74% (1830/2464) | 70% (1716/2464) | 87% | partial | not confused (-0.06) | duration of the aligned note (sem) |
| `note-32nd` | 709 | 21 | 432 | 57% (407/709) | 53% (376/709) | 47% (334/709) | 64% | partial | not confused (-0.08) | duration of the aligned note (sem) |
| `note-64th` | 123 | 16 | 83 | 57% (70/123) | 54% (66/123) | 26% (32/123) | 79% | partial | not confused (-0.01) | duration of the aligned note (sem) |
| `dot` | 1513 | 69 | 2258 | 89% (1994/2233) | 84% (1876/2233) | 74% (1657/2233) | 91% | supported | not confused (-0.02) | <dot/> count + duration |
| `double-dot` | 23 | 12 | 22 | 91% (21/23) | 87% (20/23) | 39% (9/23) | 87% | supported | not confused (+0.04) | <dot/> count + duration |
| `chord` | 4333 | 42 | 10737 | 84% (8859/10585) | 84% (8899/10585) | 76% (8058/10585) | 84% | supported | not confused (+0.01) | element on the aligned note |
| `beam` | 3452 | 68 | 9886 | 77% (8557/11082) | 74% (8159/11082) | 62% (6888/11082) | 86% | partial | not confused (-0.06) | element on the aligned note |
| `flag` | 649 | 51 | 2127 | 69% (382/551) | 65% (357/551) | 48% (264/551) | 75% | partial | not confused (-0.02) | duration of the flagged note (sem) |
| `stem-up` | 6550 | 88 | 6390 | 88% (5576/6356) | 87% (5504/6356) | 76% (4807/6356) | 88% | supported | not confused (+0.01) | element on the aligned note |
| `stem-down` | 16719 | 93 | 15611 | 86% (14391/16719) | 86% (14397/16719) | 77% (12834/16719) | 87% | supported | not confused (-0.19) | element on the aligned note |
| `ledger-above` | 5241 | 79 | 4980 | 85% (4322/5076) | 87% (4433/5076) | 81% (4093/5076) | 87% | supported | not confused (+0.00) | pitch (sem) |
| `ledger-below` | 1128 | 66 | 1100 | 87% (983/1128) | 89% (1002/1128) | 80% (905/1128) | 89% | supported | not confused (+0.02) | pitch (sem) |
| `grace` | 252 | 14 | 327 | 22% (55/252) | 32% (81/252) | 46% (117/252) | 32% | partial | not confused (+0.03) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 114 | 14 | 15 | 8% (9/114) | 0% (0/114) | 0% (0/114) | 29% | **unsupported** | not confused (+0.04) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.20) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 163 | 11 | 0 | 0% (0/163) | 0% (0/163) | 0% (0/163) | 58% | **unsupported** — element never emitted | not confused (-0.07) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 7 | 2 | 0 | 86% (6/7) | 71% (5/7) | 29% (2/7) | 100% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-whole` | 11 | 4 | 3 | 100% (11/11) | 100% (11/11) | 73% (8/11) | 100% | supported | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-half` | 59 | 25 | 52 | 86% (51/59) | 81% (48/59) | 61% (36/59) | 83% | supported | not confused (-0.05) | aligned rest with the same duration (sem) |
| `rest-quarter` | 224 | 45 | 180 | 81% (181/224) | 75% (168/224) | 43% (97/224) | 79% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-8th` | 148 | 24 | 133 | 75% (111/148) | 78% (115/148) | 66% (97/148) | 89% | partial | not confused (+0.04) | aligned rest with the same duration (sem) |
| `rest-16th` | 68 | 15 | 72 | 72% (49/68) | 72% (49/68) | 54% (37/68) | 93% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-32nd` | 102 | 7 | 82 | 100% (102/102) | 78% (80/102) | 56% (57/102) | 81% | partial | not confused (-0.08) | aligned rest with the same duration (sem) |
| `rest-64th` | 30 | 4 | 16 | 80% (24/30) | 37% (11/30) | 13% (4/30) | 37% | partial | not confused (-0.00) | aligned rest with the same duration (sem) |
| `rest-dotted` | 38 | 14 | 34 | 87% (33/38) | 87% (33/38) | 55% (21/38) | 92% | supported | **confused** (+0.05) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 210 | 22 | 216 | 90% (190/210) | 83% (175/210) | 48% (101/210) | 90% | supported | not confused (-0.04) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 7 | 67% (6/9) | 67% (6/9) | 0% (0/9) | – | partial | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 157 | 92 | 151 | 95% (149/157) | 95% (149/157) | 86% (135/157) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 115 | 66 | 107 | 90% (104/115) | 90% (104/115) | 78% (90/115) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 19 | 14 | 13 | 68% (13/19) | 68% (13/19) | 68% (13/19) | – | partial | **confused** (+0.08) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 10 | 4 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | – | **unsupported** — element never emitted | **confused** (+0.33) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 6 | 2 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | **confused** (+0.43) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 10 | 6 | 5 | 50% (5/10) | 50% (5/10) | 40% (4/10) | – | partial | **confused** (+0.29) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 6 | 2 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | **confused** (+0.62) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 5 | 2 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | **confused** (+0.67) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 101 | 14 | 49 | 44% (44/101) | 45% (45/101) | 27% (27/101) | – | partial | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 47 | 42 | 59 | 86% (38/44) | 84% (37/44) | 80% (35/44) | – | supported | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 32 | 26 | 46 | 86% (25/29) | 79% (23/29) | 76% (22/29) | – | partial | **confused** (+0.09) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 18 | 12 | 32 | 100% (15/15) | 100% (15/15) | 93% (14/15) | – | supported | not confused (-0.11) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 15 | 9 | 19 | 67% (10/15) | 73% (11/15) | 60% (9/15) | – | partial | **confused** (+0.26) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 15 | 14 | 15 | 93% (14/15) | 93% (14/15) | 33% (5/15) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 5 | 4 | 5 | 100% (5/5) | 80% (4/5) | 60% (3/5) | – | supported | **confused** (+0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 8 | 6 | 13 | 100% (8/8) | 100% (8/8) | 75% (6/8) | – | supported | **confused** (+0.65) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 8 | 5 | 10 | 100% (8/8) | 88% (7/8) | 75% (6/8) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 19 | 15 | 22 | 100% (16/16) | 100% (16/16) | 94% (15/16) | – | supported | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 11 | 9 | 14 | 100% (11/11) | 100% (11/11) | 100% (11/11) | – | supported | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 27 | 25 | 55 | 92% (24/26) | 92% (24/26) | 65% (17/26) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 17 | 15 | 15 | 94% (16/17) | 76% (13/17) | 29% (5/17) | – | partial | **confused** (+0.23) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 6 | 4 | 7 | 67% (4/6) | 67% (4/6) | 50% (3/6) | – | partial | **confused** (+0.11) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 7 | 5 | 6 | 100% (7/7) | 86% (6/7) | 0% (0/7) | – | supported | **confused** (+0.08) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 9 | 6 | 9 | 100% (9/9) | 100% (9/9) | 11% (1/9) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 129 | 18 | 146 | 87% (112/129) | 82% (106/129) | 48% (62/129) | – | supported | **confused** (+0.16) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 411 | 35 | 332 | 70% (286/411) | 72% (296/411) | 61% (251/411) | 72% | partial | not confused (+0.01) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 51 | 26 | 49 | 76% (39/51) | 80% (41/51) | 84% (43/51) | 80% | supported | not confused (-0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 356 | 30 | 299 | 85% (302/356) | 82% (293/356) | 78% (276/356) | 82% | supported | not confused (-0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 124 | 15 | 57 | 55% (68/124) | 46% (57/124) | 9% (11/124) | 46% | partial | not confused (+0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 13 | 10 | 11 | 69% (9/13) | 85% (11/13) | 77% (10/13) | 85% | supported | not confused (-0.08) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 39 | 14 | 0 | 44% (17/39) | 49% (19/39) | 51% (20/39) | 49% | partial — <accidental> never emitted | **confused** (+0.07) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 21 | 13 | 215 | 60% (132/221) | 71% (158/221) | 59% (131/221) | 69% | partial | not confused (-0.03) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 20 | 13 | 307 | 67% (207/310) | 65% (203/310) | 65% (201/310) | 63% | partial | **confused** (+0.18) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 5 | 3 | 63 | 84% (53/63) | 81% (51/63) | 81% (51/63) | 79% | supported | not confused (-0.06) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | unclear (+0.14) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (-0.07) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 21 | 13 | 18 | 94% (17/18) | 83% (15/18) | 72% (13/18) | – | supported | **confused** (+0.53) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 60 | 45 | 90 | 88% (45/51) | 92% (47/51) | 73% (37/51) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 86 | 58 | 122 | 96% (76/79) | 94% (74/79) | 85% (67/79) | – | supported | **confused** (+0.06) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 5 | 3 | 5 | 100% (5/5) | 100% (5/5) | 60% (3/5) | – | supported | **confused** (+0.26) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 8 | 6 | 8 | 63% (5/8) | 100% (8/8) | 50% (4/8) | – | supported | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 34 | 27 | 35 | 94% (29/31) | 94% (29/31) | 55% (17/31) | – | supported | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 8 | 6 | 8 | 100% (8/8) | 100% (8/8) | 100% (8/8) | – | supported | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 8 | 6 | 7 | 100% (8/8) | 88% (7/8) | 75% (6/8) | – | supported | **confused** (+0.38) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 60% (3/5) | – | supported | **confused** (+0.47) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 8 | 4 | 8 | 100% (5/5) | 100% (5/5) | 80% (4/5) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 10 | 5 | 10 | 100% (7/7) | 86% (6/7) | 86% (6/7) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 25 | 19 | 29 | 95% (21/22) | 95% (21/22) | 91% (20/22) | – | supported | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 20 | 15 | 19 | 94% (16/17) | 88% (15/17) | 53% (9/17) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 190 | 32 | 190 | 93% (157/169) | 92% (156/169) | 67% (114/169) | – | supported | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 17 | 17 | 14 | 82% (14/17) | 76% (13/17) | 71% (12/17) | – | partial | not confused (+0.00) | first measure has the pickup length (sem) |
| `tuplet-3` | 412 | 19 | 892 | 68% (816/1208) | 68% (822/1208) | 56% (679/1208) | 90% | partial | not confused (-0.04) | duration + <time-modification> ratio |
| `tuplet-2` | 40 | 10 | 0 | 0% (0/77) | 0% (0/77) | 0% (0/77) | 68% | **unsupported** — element never emitted | not confused (+0.03) | duration + <time-modification> ratio |
| `tuplet-5` | 58 | 14 | 204 | 82% (232/284) | 68% (193/284) | 54% (152/284) | 98% | partial | not confused (-0.09) | duration + <time-modification> ratio |
| `tuplet-6` | 62 | 12 | 416 | 46% (170/372) | 57% (212/372) | 45% (168/372) | 78% | partial | not confused (-0.05) | duration + <time-modification> ratio |
| `tuplet-7` | 37 | 4 | 89 | 29% (75/259) | 29% (75/259) | 28% (72/259) | 75% | partial | not confused (-0.01) | duration + <time-modification> ratio |
| `tuplet-nested` | 8 | 1 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 100% | **unsupported** — element never emitted | not confused (+0.00) | duration + <time-modification> |
| `tie` | 87 | 22 | 46 | 34% (30/87) | 32% (28/87) | 15% (13/87) | 100% | partial | not confused (-0.06) | element on the aligned note |
| `tie-across-system` | 54 | 19 | 0 | 13% (7/54) | 15% (8/54) | 11% (6/54) | 100% | **unsupported** — element never emitted | not confused (-0.06) | element on the aligned note |
| `x-time-3-8` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | unclear (+0.33) | same clef/key/time at the aligned measure (+-1) |
| `x-time-4-2` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 40% (2/5) | – | supported | not confused (-0.13) | same clef/key/time at the aligned measure (+-1) |
| `x-time-6-4` | 1 | 1 | 1 | 100% (1/1) | 100% (1/1) | 100% (1/1) | – | supported — low n (1) | not confused (-0.06) | same clef/key/time at the aligned measure (+-1) |
| `x-tuplet-4` | 2 | 2 | 0 | 0% (0/8) | 0% (0/8) | 0% (0/8) | 100% | **unsupported** — element never emitted | not confused (-0.05) | duration + <time-modification> ratio |

## Symbols: marks

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `slur` | 628 | 40 | 271 | 45% (280/628) | 41% (259/628) | 36% (223/628) | 94% | partial | not confused (-0.02) | element on the aligned note |
| `staccato` | 1267 | 19 | 1279 | 38% (478/1267) | 39% (489/1267) | 34% (436/1267) | 87% | partial | not confused (-0.03) | element on the aligned note |
| `staccatissimo` | 17 | 10 | 18 | 100% (17/17) | 76% (13/17) | 53% (9/17) | 76% | partial | not confused (+0.01) | element on the aligned note |
| `accent` | 246 | 20 | 221 | 53% (131/246) | 52% (129/246) | 50% (123/246) | 91% | partial | not confused (+0.00) | element on the aligned note |
| `tenuto` | 173 | 19 | 173 | 48% (83/173) | 50% (86/173) | 42% (73/173) | 77% | partial | **confused** (+0.19) | element on the aligned note |
| `marcato` | 119 | 14 | 119 | 27% (32/119) | 24% (29/119) | 16% (19/119) | 87% | partial | not confused (+0.04) | element on the aligned note |
| `fermata` | 398 | 53 | 190 | 63% (249/398) | 38% (152/398) | 27% (107/398) | 81% | partial | not confused (-0.03) | element on the aligned note |
| `trill` | 42 | 15 | 0 | 0% (0/42) | 0% (0/42) | 0% (0/42) | 93% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `mordent` | 53 | 13 | 0 | 0% (0/58) | 0% (0/58) | 0% (0/58) | 90% | **unsupported** — element never emitted | not confused (-0.05) | element on the aligned note |
| `turn` | 33 | 13 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 97% | **unsupported** — element never emitted | not confused (-0.08) | element on the aligned note |
| `arpeggio` | 92 | 12 | 0 | 0% (0/312) | 0% (0/312) | 0% (0/312) | 70% | **unsupported** — element never emitted | not confused (+0.01) | element on the aligned note |
| `breath` | 26 | 13 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 88% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `dyn-pp` | 29 | 17 | 28 | 86% (25/29) | 86% (25/29) | 79% (23/29) | – | supported | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 77 | 38 | 45 | 52% (40/77) | 58% (45/77) | 42% (32/77) | – | partial | not confused (+0.03) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 34 | 21 | 35 | 94% (32/34) | 97% (33/34) | 59% (20/34) | – | supported | **confused** (+0.18) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 93 | 46 | 53 | 91% (85/93) | 46% (43/93) | 31% (29/93) | – | partial | not confused (+0.05) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 94 | 38 | 64 | 68% (64/94) | 68% (64/94) | 60% (56/94) | – | partial | **confused** (+0.13) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 35 | 17 | 32 | 77% (27/35) | 91% (32/35) | 77% (27/35) | – | supported | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 14 | 11 | 6 | 43% (6/14) | 43% (6/14) | 7% (1/14) | – | partial | not confused (-0.08) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 104 | 30 | 43 | 45% (47/104) | 41% (43/104) | 11% (11/104) | – | partial | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 92 | 35 | 38 | 39% (36/92) | 38% (35/92) | 13% (12/92) | – | partial | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `pedal` | 268 | 17 | 225 | 74% (199/268) | 81% (217/268) | 51% (137/268) | – | supported | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `fingering` | 292 | 12 | 180 | 63% (185/292) | 48% (140/292) | 20% (58/292) | 77% | partial | not confused (+0.02) | element on the aligned note |
| `text-expression` | 65 | 23 | 26 | 53% (27/51) | 49% (25/51) | 39% (20/51) | – | partial | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 175 | 74 | 174 | 51% (93/184) | 48% (88/184) | 38% (70/184) | – | partial | **confused** (+0.16) | same element/value at the aligned measure (+-1) |
| `metronome` | 144 | 54 | 141 | 88% (127/144) | 88% (127/144) | 78% (112/144) | – | supported | **confused** (+0.18) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 124 | 19 | 109 | 91% (113/124) | 87% (108/124) | 64% (79/124) | – | supported | **confused** (+0.17) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 32 | 56% (34/61) | 52% (32/61) | 46% (28/61) | – | partial | not confused (-0.06) | same element/value at the aligned measure (+-1) |
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
| `barline-double` | 133 | 26 | 136 | 96% (128/133) | 92% (122/133) | 82% (109/133) | – | supported | not confused (-0.06) | same element/value at the aligned measure (+-1) |
| `barline-final` | 123 | 101 | 206 | 100% (110/110) | 99% (109/110) | 91% (100/110) | – | supported | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 33 | 14 | 51 | 97% (32/33) | 94% (31/33) | 70% (23/33) | – | supported | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 40 | 16 | 67 | 98% (39/40) | 98% (39/40) | 78% (31/40) | – | supported | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `volta-1` | 16 | 13 | 30 | 88% (14/16) | 88% (14/16) | 50% (8/16) | – | supported | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `volta-2` | 16 | 13 | 23 | 44% (7/16) | 44% (7/16) | 25% (4/16) | – | partial | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `segno` | 6 | 6 | 8 | 100% (6/6) | 100% (6/6) | 67% (4/6) | – | supported | **confused** (+0.62) | same element/value at the aligned measure (+-1) |
| `coda` | 8 | 6 | 8 | 100% (8/8) | 100% (8/8) | 100% (8/8) | – | supported | not confused (-0.11) | same element/value at the aligned measure (+-1) |
| `dc` | 10 | 10 | 9 | 100% (10/10) | 90% (9/10) | 90% (9/10) | – | supported | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `ds` | 6 | 6 | 2 | 33% (2/6) | 33% (2/6) | 17% (1/6) | – | partial | not confused (-0.09) | same element/value at the aligned measure (+-1) |
| `fine` | 10 | 10 | 11 | 90% (9/10) | 70% (7/10) | 50% (5/10) | – | partial | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `system-break` | 581 | 101 | 0 | 0% (0/581) | 0% (0/581) | 0% (0/581) | – | **unsupported** — element never emitted | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `page-break` | 90 | 10 | 0 | 0% (0/90) | 0% (0/90) | 0% (0/90) | – | **unsupported** — element never emitted | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `multi-page` | 26 | 10 | 0 | 86% (17552/20298) | 87% (17637/20298) | 80% (16284/20298) | – | supported | not confused (-0.38) | pitch recall of the notes on pages 2+ (sem) |
| `x-volta-3` | 1 | 1 | 4 | 100% (1/1) | 100% (1/1) | 0% (0/1) | – | supported — low n (1) | not confused (+0.00) | same element/value at the aligned measure (+-1) |

## Symbols: lyrics

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `lyrics` | 1791 | 23 | 839 | 91% (774/848) | 92% (776/848) | 63% (532/848) | 98% | supported | not confused (-0.27) | lyric on the aligned note |
| `lyrics-multi-verse` | 320 | 13 | 349 | 92% (335/366) | 90% (330/366) | 75% (275/366) | 98% | supported | not confused (-0.02) | lyric on the aligned note |
| `lyrics-melisma` | 135 | 18 | 59 | 86% (49/57) | 79% (45/57) | 60% (34/57) | 98% | partial | not confused (+0.01) | lyric on the aligned note |
| `lyrics-extender` | 91 | 16 | 39 | 84% (36/43) | 74% (32/43) | 49% (21/43) | 100% | partial | not confused (+0.01) | lyric on the aligned note |
| `lyrics-hyphen` | 395 | 23 | 291 | 88% (260/296) | 88% (261/296) | 74% (219/296) | 97% | supported | not confused (-0.01) | lyric on the aligned note |
| `lyrics-elision` | 11 | 1 | 9 | 88% (7/8) | 50% (4/8) | 63% (5/8) | 100% | partial | not confused (+0.00) | lyric on the aligned note |
| `lyrics-non-ascii` | 30 | 2 | 3 | 0% (0/19) | 0% (0/19) | 0% (0/19) | 100% | **unsupported** | not confused (+0.00) | lyric on the aligned note |
| `stanza-text` | 39 | 10 | – | 97% (1045/1079) | 96% (1042/1080) | 91% (922/1010) | – | supported | – | lyric precision (stanza text blocks not underlaid as lyrics) (sem) |

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
| `melody` | 32 | 98% | 97% | 88% | 100% | 91% | 100% | 0 | 0.922 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.980 | supported |
| `piano` | 29 | 100% | 100% | 93% | 100% | 100% | 100% | 0 | 0.943 | supported |
| `voice-piano` | 3 | 100% | 100% | 77% | 100% | 100% | 100% | 0 | 0.959 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 99% | 0 | 0.925 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 5% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.992 | supported |
| `choir-piano` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.961 | supported |
| `string-quartet` | 6 | 87% | 96% | 57% | 100% | 88% | 99% | 0 | 0.973 | supported |
| `orchestral` | 2 | 92% | 93% | 89% | 100% | 82% | 98% | 0 | 0.967 | supported |
| `lead-sheet` | 2 | 83% | 83% | 67% | 100% | 50% | 100% | 0 | 0.940 | supported |
| `hymnal-stanzas` | 9 | 99% | 100% | 99% | 100% | 100% | 99% | 0 | 0.982 | supported |
| `divisi` | 2 | 100% | 96% | 99% | 100% | 88% | 100% | 0 | 0.970 | supported |
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
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 2083 | 243 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.925 | 0.879 | 4 → 4 | 3103 | 246 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 1.000 | 1.000 | 0.972 | 5 → 5 | 4086 | 329 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 2867 | 240 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.996 | 0.992 | 0.982 | 4 → 4 | 2032 | 264 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.348 | 4 → 4 | 2096 | 239 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.884 | 0.889 | 0.794 | 1 → 1 | 1426 | 261 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 5243 | 328 |
| `layouts/divisi-strings-lament` | divisi | 0.974 | 0.953 | 0.938 | 4 → 4 | 2379 | 255 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 3273 | 244 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 3156 | 250 |
| `layouts/melody-cello-elegy-2page` | melody | 0.886 | 0.843 | 0.707 | 1 → 1 | 1342 | 257 |
| `layouts/melody-flute-air` | melody | 0.959 | 0.977 | 0.972 | 1 → 1 | 1359 | 244 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 1911 | 251 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.973 | 0.958 | 0.898 | 9 → 9 | 4084 | 435 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.987 | 0.948 | 0.775 | 1 → 1 | 2340 | 270 |
| `layouts/piano-grand-staff-prelude` | piano | 0.899 | 0.954 | 0.952 | 1 → 1 | 1647 | 239 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.987 | 0.775 | 4 → 4 | 4265 | 348 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1494 | 236 |
| `layouts/voice-piano-night-song` | voice-piano | 0.979 | 0.935 | 0.471 | 2 → 2 | 2244 | 240 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.985 | 0.979 | 0.890 | 1 → 1 | 2436 | 242 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.975 | 0.975 | 0.943 | 1 → 1 | 3018 | 248 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 1464 | 256 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1642 | 258 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.984 | 0.968 | 0.780 | 1 → 1 | 1642 | 220 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.953 | 0.949 | 0.842 | 1 → 1 | 2268 | 240 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.982 | 0.956 | 0.723 | 1 → 1 | 2035 | 246 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.970 | 0.960 | 0.836 | 1 → 1 | 2318 | 252 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.980 | 0.993 | 0.907 | 2 → 2 | 2135 | 245 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.977 | 0.911 | 4 → 4 | 2587 | 291 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.924 | 0.895 | 1 → 1 | 2031 | 246 |
| `notes/nt01-note-values` | melody | 0.895 | 0.924 | 0.673 | 1 → 1 | 1753 | 234 |
| `notes/nt02-dots` | melody | 0.963 | 0.936 | 0.879 | 1 → 1 | 1706 | 226 |
| `notes/nt03-chords` | piano | 0.974 | 0.970 | 0.900 | 1 → 1 | 1541 | 241 |
| `notes/nt04-beams` | melody | 0.985 | 0.971 | 0.978 | 1 → 1 | 1816 | 266 |
| `notes/nt05-flags-stems` | melody | 0.847 | 0.850 | 0.759 | 1 → 1 | 1776 | 220 |
| `notes/nt06-ledger-lines` | piano | 1.000 | 0.953 | 0.953 | 1 → 1 | 1480 | 245 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.927 | 0.912 | 1 → 1 | 1764 | 241 |
| `notes/nt08-cue-notes` | melody | 0.960 | 0.946 | 0.947 | 1 → 1 | 1534 | 222 |
| `notes/nt09-tremolos` | piano | 0.719 | 0.751 | 0.635 | 1 → 1 | 1514 | 245 |
| `notes/nt10-piano-etude` | piano | 0.989 | 0.988 | 0.959 | 1 → 1 | 1634 | 260 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.639 | 3 → 2 | 1964 | 235 |
| `perf/perf-hymn-a3-300dpi` | hymnal-stanzas | 0.999 | 0.998 | 0.998 | 4 → 4 | 4295 | 353 |
| `perf/perf-hymn-a4-100dpi` | hymnal-stanzas | 0.925 | 0.931 | 0.784 | 4 → 4 | 5260 | 360 |
| `perf/perf-hymn-a4-150dpi` | hymnal-stanzas | 0.983 | 0.955 | 0.964 | 4 → 4 | 4675 | 308 |
| `perf/perf-hymn-a4-200dpi` | hymnal-stanzas | 0.996 | 0.977 | 0.921 | 4 → 4 | 4712 | 334 |
| `perf/perf-hymn-a4-300dpi` | hymnal-stanzas | 0.997 | 0.997 | 0.984 | 4 → 4 | 4550 | 327 |
| `perf/perf-hymn-a4-400dpi` | hymnal-stanzas | 0.997 | 0.997 | 0.964 | 4 → 4 | 4807 | 322 |
| `perf/perf-hymn-a4-600dpi` | hymnal-stanzas | 1.000 | 0.997 | 0.981 | 4 → 4 | 4606 | 316 |
| `perf/perf-hymn-letter-300dpi` | hymnal-stanzas | 0.998 | 0.991 | 0.966 | 4 → 4 | 4817 | 330 |
| `perf/perf-pages-01` | piano | 0.981 | 0.968 | 0.918 | 1 → 1 | 2639 | 330 |
| `perf/perf-pages-05` | piano | 0.939 | 0.942 | 0.921 | 1 → 1 | 3048 | 504 |
| `perf/perf-pages-10` | piano | 0.935 | 0.930 | 0.897 | 1 → 1 | 3092 | 639 |
| `perf/perf-pages-20` | piano | 0.942 | 0.937 | 0.906 | 1 → 1 | 2982 | 686 |
| `perf/perf-pages-40` | piano | 0.929 | 0.918 | 0.883 | 1 → 1 | 2926 | 790 |
| `perf/perf-piano-a3-300dpi` | piano | 0.964 | 0.929 | 0.870 | 1 → 1 | 4415 | 303 |
| `perf/perf-piano-a4-100dpi` | piano | 0.886 | 0.744 | 0.706 | 1 → 1 | 3321 | 272 |
| `perf/perf-piano-a4-150dpi` | piano | 0.938 | 0.890 | 0.810 | 1 → 1 | 2849 | 287 |
| `perf/perf-piano-a4-200dpi` | piano | 0.964 | 0.883 | 0.817 | 1 → 1 | 2882 | 265 |
| `perf/perf-piano-a4-300dpi` | piano | 0.946 | 0.950 | 0.768 | 1 → 1 | 2881 | 273 |
| `perf/perf-piano-a4-400dpi` | piano | 0.932 | 0.940 | 0.884 | 1 → 1 | 2849 | 275 |
| `perf/perf-piano-a4-600dpi` | piano | 0.960 | 0.952 | 0.943 | 1 → 1 | 2904 | 262 |
| `perf/perf-piano-letter-300dpi` | piano | 0.954 | 0.930 | 0.782 | 1 → 1 | 2904 | 271 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.976 | 0.994 | 0.869 | 1 → 1 | 1572 | 254 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.877 | 0.927 | 0.843 | 1 → 1 | 1861 | 241 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1805 | 225 |
| `pitch/pitch-cov-clefs-all` | melody | 0.741 | 0.727 | 0.733 | 1 → 1 | 1753 | 253 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.772 | 0.955 | 0.756 | 4 → 4 | 2265 | 246 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.989 | 0.974 | 0.813 | 1 → 1 | 2002 | 234 |
| `pitch/pitch-cov-keys-major-flats` | piano | 1.000 | 1.000 | 0.678 | 1 → 1 | 1796 | 229 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 1.000 | 0.911 | 0.952 | 1 → 1 | 1826 | 219 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.967 | 0.971 | 0.885 | 1 → 1 | 1834 | 248 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.965 | 0.978 | 0.532 | 1 → 1 | 1857 | 243 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 1.000 | 1.000 | 1.000 | 1 → 1 | 1485 | 244 |
| `pitch/pitch-cov-ottava-piano` | piano | 1.000 | 0.958 | 0.925 | 1 → 1 | 1798 | 235 |
| `rests/rst01-rest-values` | melody | 0.867 | 0.841 | 0.725 | 1 → 1 | 1713 | 224 |
| `rests/rst02-dotted-rests` | melody | 0.934 | 0.948 | 0.798 | 1 → 1 | 1786 | 228 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.904 | 0.904 | 0.701 | 1 → 1 | 1616 | 243 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.989 | 1.000 | 0.940 | 1 → 1 | 1640 | 241 |
| `rests/rst05-multibar-rests` | melody | 0.881 | 0.807 | 0.626 | 1 → 1 | 1919 | 259 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.863 | 0.840 | 1 → 1 | 1739 | 233 |
| `rests/rst07-piano-rests` | piano | 0.954 | 0.959 | 0.943 | 1 → 1 | 1829 | 217 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.863 | 0.846 | 0.367 | 1 → 1 | 2055 | 243 |
| `rests/rst09-quartet-rests` | string-quartet | 0.995 | 0.976 | 0.929 | 4 → 4 | 3337 | 311 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.944 | 1 → 1 | 1590 | 250 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.980 | 1 → 1 | 1818 | 246 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.467 | 4 → 4 | 5055 | 318 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 1987 | 238 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.481 | 1 → 1 | 2046 | 260 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.976 | 0.948 | 0.844 | 2 → 2 | 3288 | 460 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.975 | 0.957 | 7 → 7 | 4014 | 492 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.996 | 0.983 | 0.964 | 1 → 1 | 1335 | 414 |
| `time/t01-simple-meters` | melody | 0.962 | 0.961 | 0.855 | 1 → 1 | 1780 | 243 |
| `time/t02-compound-irregular` | melody | 1.000 | 1.000 | 0.971 | 1 → 1 | 1828 | 221 |
| `time/t03-common-cut-piano` | piano | 0.991 | 1.000 | 0.931 | 1 → 1 | 1785 | 265 |
| `time/t04-pickup-song` | melody-lyrics | 0.953 | 0.966 | 0.955 | 1 → 1 | 1976 | 242 |
| `time/t05-triplets-duplets` | melody | 0.848 | 0.875 | 0.841 | 1 → 1 | 1831 | 249 |
| `time/t06-quint-sext-sept` | melody | 0.973 | 0.971 | 0.920 | 1 → 1 | 1440 | 225 |
| `time/t07-nested-tuplets` | melody | 0.819 | 0.812 | 0.827 | 1 → 1 | 1460 | 229 |
| `time/t08-ties-systems-pages` | piano | 0.984 | 0.997 | 0.409 | 1 → 1 | 1455 | 265 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.933 | 0.933 | 0.765 | 1 → 1 | 1498 | 248 |
| `time/t10-quartet-meters` | string-quartet | 0.987 | 0.962 | 0.643 | 4 → 4 | 2377 | 249 |
