# Coverage matrix: symbols, layouts, performance

Generated 2026-11-08 14:07 UTC by `tools/coverage.mjs` from `mvp/work/eval-coverage.json` (eval 2026-11-08 14:04, app source hash `868df105a7b3`, OCR on, raster 200 dpi).
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

**Totals:** 64 supported, 59 partial, 31 unsupported, 30 not measurable, 0 taxonomy tags without items yet.

## Symbols: notes

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `note-breve` | 29 | 3 | 0 | 0% (0/29) | 0% (0/29) | 0% (0/29) | 34% | **unsupported** | **confused** (+0.09) | duration of the aligned note (sem) |
| `note-whole` | 512 | 50 | 487 | 48% (257/537) | 40% (217/537) | 24% (129/537) | 57% | partial | not confused (-0.01) | duration of the aligned note (sem) |
| `note-half` | 4857 | 96 | 4270 | 82% (4100/4977) | 71% (3531/4977) | 39% (1965/4977) | 86% | partial | not confused (+0.00) | duration of the aligned note (sem) |
| `note-quarter` | 11462 | 101 | 11962 | 85% (10125/11863) | 84% (10012/11863) | 73% (8695/11863) | 89% | supported | not confused (-0.00) | duration of the aligned note (sem) |
| `note-8th` | 9382 | 81 | 9333 | 83% (7899/9464) | 83% (7875/9464) | 75% (7058/9464) | 87% | supported | not confused (-0.02) | duration of the aligned note (sem) |
| `note-16th` | 2464 | 34 | 2679 | 75% (1840/2464) | 74% (1827/2464) | 69% (1712/2464) | 87% | partial | not confused (-0.06) | duration of the aligned note (sem) |
| `note-32nd` | 709 | 21 | 408 | 54% (385/709) | 46% (329/709) | 45% (319/709) | 60% | partial | not confused (-0.08) | duration of the aligned note (sem) |
| `note-64th` | 123 | 16 | 83 | 51% (63/123) | 51% (63/123) | 27% (33/123) | 76% | partial | not confused (+0.00) | duration of the aligned note (sem) |
| `dot` | 1513 | 69 | 2258 | 89% (1993/2233) | 84% (1871/2233) | 74% (1646/2233) | 91% | supported | not confused (-0.02) | <dot/> count + duration |
| `double-dot` | 23 | 12 | 22 | 91% (21/23) | 87% (20/23) | 39% (9/23) | 87% | supported | not confused (+0.04) | <dot/> count + duration |
| `chord` | 4333 | 42 | 10754 | 83% (8823/10585) | 83% (8834/10585) | 75% (7971/10585) | 84% | supported | not confused (+0.01) | element on the aligned note |
| `beam` | 3452 | 68 | 9892 | 77% (8519/11082) | 73% (8102/11082) | 62% (6851/11082) | 86% | partial | not confused (-0.06) | element on the aligned note |
| `flag` | 649 | 51 | 2130 | 69% (382/551) | 65% (356/551) | 47% (261/551) | 75% | partial | not confused (-0.02) | duration of the flagged note (sem) |
| `stem-up` | 6550 | 88 | 6407 | 88% (5567/6356) | 86% (5490/6356) | 76% (4802/6356) | 88% | supported | not confused (+0.00) | element on the aligned note |
| `stem-down` | 16719 | 93 | 15602 | 86% (14323/16719) | 86% (14304/16719) | 76% (12747/16719) | 87% | supported | not confused (-0.20) | element on the aligned note |
| `ledger-above` | 5241 | 79 | 4978 | 84% (4283/5076) | 86% (4371/5076) | 79% (4019/5076) | 86% | supported | not confused (+0.00) | pitch (sem) |
| `ledger-below` | 1128 | 66 | 1102 | 87% (983/1128) | 89% (1002/1128) | 80% (905/1128) | 89% | supported | not confused (+0.03) | pitch (sem) |
| `grace` | 252 | 14 | 404 | 27% (69/252) | 35% (88/252) | 47% (118/252) | 35% | partial | not confused (+0.03) | <grace/> note, same pitch, aligned measure |
| `grace-slash` | 114 | 14 | 33 | 16% (18/114) | 0% (0/114) | 0% (0/114) | 33% | **unsupported** | not confused (+0.03) | <grace slash="yes"/> |
| `cue-note` | 24 | 1 | 0 | 0% (0/24) | 0% (0/24) | 0% (0/24) | 0% | **unsupported** — element never emitted | unclear (+0.20) | <cue/> note, same pitch, aligned measure |
| `tremolo` | 163 | 11 | 0 | 0% (0/163) | 0% (0/163) | 0% (0/163) | 54% | **unsupported** — element never emitted | not confused (-0.07) | element on the aligned note |

## Symbols: rests

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `rest-breve` | 7 | 2 | 0 | 86% (6/7) | 71% (5/7) | 29% (2/7) | 100% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-whole` | 11 | 4 | 3 | 100% (11/11) | 100% (11/11) | 73% (8/11) | 100% | supported | **confused** (+0.07) | aligned rest with the same duration (sem) |
| `rest-half` | 59 | 25 | 52 | 86% (51/59) | 81% (48/59) | 63% (37/59) | 83% | supported | not confused (-0.05) | aligned rest with the same duration (sem) |
| `rest-quarter` | 224 | 45 | 176 | 79% (178/224) | 74% (166/224) | 39% (87/224) | 78% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-8th` | 148 | 24 | 132 | 75% (111/148) | 77% (114/148) | 63% (93/148) | 86% | partial | not confused (+0.05) | aligned rest with the same duration (sem) |
| `rest-16th` | 68 | 15 | 71 | 71% (48/68) | 69% (47/68) | 43% (29/68) | 90% | partial | not confused (-0.03) | aligned rest with the same duration (sem) |
| `rest-32nd` | 102 | 7 | 42 | 95% (97/102) | 39% (40/102) | 21% (21/102) | 41% | partial | not confused (-0.08) | aligned rest with the same duration (sem) |
| `rest-64th` | 30 | 4 | 7 | 40% (12/30) | 13% (4/30) | 0% (0/30) | 20% | **unsupported** | not confused (+0.01) | aligned rest with the same duration (sem) |
| `rest-dotted` | 38 | 14 | 34 | 84% (32/38) | 87% (33/38) | 50% (19/38) | 89% | supported | **confused** (+0.06) | aligned rest with the same duration (sem) |
| `rest-whole-bar` | 210 | 22 | 216 | 90% (190/210) | 83% (175/210) | 48% (101/210) | 90% | supported | not confused (-0.04) | aligned rest with the same duration (sem) |
| `rest-multibar` | 9 | 1 | 7 | 67% (6/9) | 67% (6/9) | 0% (0/9) | – | partial | – | every bar of the block read as a full-bar rest (sem) |

## Symbols: pitch

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `clef-treble` | 157 | 92 | 151 | 95% (149/157) | 95% (149/157) | 86% (135/157) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass` | 115 | 66 | 107 | 90% (104/115) | 90% (104/115) | 78% (90/115) | – | supported | not confused (+0.03) | same clef/key/time at the aligned measure (+-1) |
| `clef-alto` | 19 | 14 | 13 | 68% (13/19) | 68% (13/19) | 68% (13/19) | – | partial | **confused** (+0.08) | same clef/key/time at the aligned measure (+-1) |
| `clef-tenor` | 10 | 4 | 0 | 0% (0/10) | 0% (0/10) | 0% (0/10) | – | **unsupported** — element never emitted | **confused** (+0.33) | same clef/key/time at the aligned measure (+-1) |
| `clef-soprano` | 6 | 2 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | **confused** (+0.43) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8vb` | 10 | 6 | 5 | 50% (5/10) | 50% (5/10) | 40% (4/10) | – | partial | **confused** (+0.29) | same clef/key/time at the aligned measure (+-1) |
| `clef-treble-8va` | 6 | 2 | 0 | 0% (0/6) | 0% (0/6) | 0% (0/6) | – | **unsupported** — element never emitted | **confused** (+0.61) | same clef/key/time at the aligned measure (+-1) |
| `clef-bass-8vb` | 5 | 2 | 0 | 0% (0/5) | 0% (0/5) | 0% (0/5) | – | **unsupported** — element never emitted | **confused** (+0.67) | same clef/key/time at the aligned measure (+-1) |
| `clef-change` | 101 | 14 | 49 | 44% (44/101) | 45% (45/101) | 27% (27/101) | – | partial | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `key-0` | 47 | 42 | 59 | 86% (38/44) | 84% (37/44) | 80% (35/44) | – | supported | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `key-s1` | 32 | 26 | 45 | 79% (23/29) | 76% (22/29) | 72% (21/29) | – | partial | **confused** (+0.11) | same clef/key/time at the aligned measure (+-1) |
| `key-s2` | 18 | 12 | 31 | 100% (15/15) | 93% (14/15) | 93% (14/15) | – | supported | not confused (-0.11) | same clef/key/time at the aligned measure (+-1) |
| `key-s3` | 15 | 9 | 18 | 60% (9/15) | 67% (10/15) | 60% (9/15) | – | partial | **confused** (+0.25) | same clef/key/time at the aligned measure (+-1) |
| `key-s4` | 15 | 14 | 14 | 87% (13/15) | 87% (13/15) | 33% (5/15) | – | supported | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-s5` | 5 | 4 | 4 | 80% (4/5) | 60% (3/5) | 60% (3/5) | – | partial | **confused** (+0.29) | same clef/key/time at the aligned measure (+-1) |
| `key-s6` | 8 | 6 | 12 | 88% (7/8) | 88% (7/8) | 75% (6/8) | – | supported | **confused** (+0.65) | same clef/key/time at the aligned measure (+-1) |
| `key-s7` | 8 | 5 | 9 | 88% (7/8) | 75% (6/8) | 75% (6/8) | – | partial | not confused (+0.02) | same clef/key/time at the aligned measure (+-1) |
| `key-f1` | 19 | 15 | 22 | 100% (16/16) | 100% (16/16) | 94% (15/16) | – | supported | not confused (-0.10) | same clef/key/time at the aligned measure (+-1) |
| `key-f2` | 11 | 9 | 14 | 100% (11/11) | 100% (11/11) | 100% (11/11) | – | supported | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `key-f3` | 27 | 25 | 55 | 92% (24/26) | 92% (24/26) | 65% (17/26) | – | supported | not confused (-0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-f4` | 17 | 15 | 15 | 94% (16/17) | 76% (13/17) | 29% (5/17) | – | partial | **confused** (+0.23) | same clef/key/time at the aligned measure (+-1) |
| `key-f5` | 6 | 4 | 7 | 67% (4/6) | 67% (4/6) | 50% (3/6) | – | partial | **confused** (+0.11) | same clef/key/time at the aligned measure (+-1) |
| `key-f6` | 7 | 5 | 6 | 100% (7/7) | 86% (6/7) | 0% (0/7) | – | supported | **confused** (+0.08) | same clef/key/time at the aligned measure (+-1) |
| `key-f7` | 9 | 6 | 9 | 100% (9/9) | 100% (9/9) | 11% (1/9) | – | supported | not confused (+0.04) | same clef/key/time at the aligned measure (+-1) |
| `key-change` | 129 | 18 | 139 | 81% (105/129) | 77% (99/129) | 47% (61/129) | – | partial | **confused** (+0.16) | same clef/key/time at the aligned measure (+-1) |
| `acc-sharp` | 411 | 35 | 331 | 68% (278/411) | 70% (288/411) | 60% (247/411) | 71% | partial | not confused (+0.02) | spelled pitch (step, alter, octave) (sem) |
| `acc-flat` | 51 | 26 | 49 | 76% (39/51) | 80% (41/51) | 84% (43/51) | 80% | supported | not confused (-0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-natural` | 356 | 30 | 299 | 85% (302/356) | 82% (293/356) | 77% (275/356) | 82% | supported | not confused (-0.03) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-sharp` | 124 | 15 | 55 | 53% (66/124) | 44% (55/124) | 9% (11/124) | 45% | partial | not confused (+0.04) | spelled pitch (step, alter, octave) (sem) |
| `acc-double-flat` | 13 | 10 | 11 | 69% (9/13) | 85% (11/13) | 77% (10/13) | 85% | supported | not confused (-0.08) | spelled pitch (step, alter, octave) (sem) |
| `acc-courtesy` | 39 | 14 | 0 | 44% (17/39) | 51% (20/39) | 51% (20/39) | 51% | partial — <accidental> never emitted | **confused** (+0.06) | spelled pitch (step, alter, octave) (sem) |
| `ottava-8va` | 21 | 13 | 65 | 39% (87/221) | 47% (103/221) | 35% (77/221) | 46% | partial | not confused (+0.04) | sounding pitch of the notes under the line (sem) |
| `ottava-8vb` | 20 | 13 | 307 | 67% (207/310) | 65% (203/310) | 65% (201/310) | 63% | partial | **confused** (+0.18) | sounding pitch of the notes under the line (sem) |
| `ottava-15ma` | 5 | 3 | 24 | 35% (22/63) | 32% (20/63) | 32% (20/63) | 31% | partial | **confused** (+0.11) | sounding pitch of the notes under the line (sem) |
| `x-acc-natural-flat` | 1 | 1 | 0 | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% | partial — <accidental> never emitted; low n (1) | unclear (+0.14) | spelled pitch (step, alter, octave) (sem) |
| `x-acc-natural-sharp` | 2 | 2 | 0 | 50% (1/2) | 100% (2/2) | 100% (2/2) | 100% | partial — <accidental> never emitted; low n (2) | not confused (-0.07) | spelled pitch (step, alter, octave) (sem) |
| `x-clef-percussion` | 2 | 1 | 0 | 0% (0/2) | 0% (0/2) | 0% (0/2) | – | **unsupported** — element never emitted; low n (2) | not confused (+0.10) | same clef/key/time at the aligned measure (+-1) |

## Symbols: time

| Tag | Occurrences | Items | Emitted | Accuracy clean | Accuracy scan | Accuracy scan-severe | Read | Status | Confusion | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `time-2-4` | 21 | 13 | 18 | 94% (17/18) | 83% (15/18) | 72% (13/18) | – | supported | **confused** (+0.53) | same clef/key/time at the aligned measure (+-1) |
| `time-3-4` | 60 | 45 | 89 | 88% (45/51) | 90% (46/51) | 71% (36/51) | – | supported | not confused (-0.02) | same clef/key/time at the aligned measure (+-1) |
| `time-4-4` | 86 | 58 | 122 | 96% (76/79) | 94% (74/79) | 87% (69/79) | – | supported | **confused** (+0.05) | same clef/key/time at the aligned measure (+-1) |
| `time-2-2` | 5 | 3 | 5 | 100% (5/5) | 100% (5/5) | 60% (3/5) | – | supported | **confused** (+0.26) | same clef/key/time at the aligned measure (+-1) |
| `time-3-2` | 8 | 6 | 8 | 63% (5/8) | 100% (8/8) | 50% (4/8) | – | supported | **confused** (+0.11) | same clef/key/time at the aligned measure (+-1) |
| `time-6-8` | 34 | 27 | 35 | 94% (29/31) | 94% (29/31) | 55% (17/31) | – | supported | not confused (-0.08) | same clef/key/time at the aligned measure (+-1) |
| `time-9-8` | 8 | 6 | 8 | 100% (8/8) | 100% (8/8) | 88% (7/8) | – | supported | **confused** (+0.12) | same clef/key/time at the aligned measure (+-1) |
| `time-12-8` | 8 | 6 | 7 | 100% (8/8) | 88% (7/8) | 75% (6/8) | – | supported | **confused** (+0.38) | same clef/key/time at the aligned measure (+-1) |
| `time-5-4` | 5 | 4 | 5 | 100% (5/5) | 100% (5/5) | 60% (3/5) | – | supported | **confused** (+0.47) | same clef/key/time at the aligned measure (+-1) |
| `time-5-8` | 8 | 4 | 8 | 100% (5/5) | 100% (5/5) | 80% (4/5) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-7-8` | 10 | 5 | 10 | 100% (7/7) | 86% (6/7) | 86% (6/7) | – | supported | not confused (+0.01) | same clef/key/time at the aligned measure (+-1) |
| `time-common` | 25 | 19 | 29 | 95% (21/22) | 95% (21/22) | 91% (20/22) | – | supported | **confused** (+0.15) | same clef/key/time at the aligned measure (+-1) |
| `time-cut` | 20 | 15 | 19 | 94% (16/17) | 88% (15/17) | 53% (9/17) | – | supported | not confused (-0.03) | same clef/key/time at the aligned measure (+-1) |
| `time-change` | 190 | 32 | 193 | 93% (157/169) | 92% (155/169) | 67% (114/169) | – | supported | **confused** (+0.13) | same clef/key/time at the aligned measure (+-1) |
| `pickup` | 17 | 17 | 14 | 82% (14/17) | 76% (13/17) | 71% (12/17) | – | partial | not confused (+0.00) | first measure has the pickup length (sem) |
| `tuplet-3` | 412 | 19 | 892 | 68% (816/1208) | 68% (822/1208) | 56% (679/1208) | 90% | partial | not confused (-0.05) | duration + <time-modification> ratio |
| `tuplet-2` | 40 | 10 | 0 | 0% (0/77) | 0% (0/77) | 0% (0/77) | 68% | **unsupported** — element never emitted | not confused (+0.03) | duration + <time-modification> ratio |
| `tuplet-5` | 58 | 14 | 204 | 82% (232/284) | 68% (193/284) | 54% (152/284) | 98% | partial | not confused (-0.10) | duration + <time-modification> ratio |
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
| `slur` | 628 | 40 | 271 | 45% (280/628) | 41% (259/628) | 36% (223/628) | 93% | partial | not confused (-0.02) | element on the aligned note |
| `staccato` | 1267 | 19 | 1277 | 38% (477/1267) | 38% (484/1267) | 35% (438/1267) | 87% | partial | not confused (-0.04) | element on the aligned note |
| `staccatissimo` | 17 | 10 | 18 | 100% (17/17) | 76% (13/17) | 53% (9/17) | 76% | partial | not confused (+0.01) | element on the aligned note |
| `accent` | 246 | 20 | 219 | 57% (141/246) | 59% (145/246) | 56% (139/246) | 89% | partial | not confused (+0.02) | element on the aligned note |
| `tenuto` | 173 | 19 | 173 | 48% (83/173) | 50% (86/173) | 42% (73/173) | 77% | partial | **confused** (+0.19) | element on the aligned note |
| `marcato` | 119 | 14 | 113 | 30% (36/119) | 34% (40/119) | 30% (36/119) | 82% | partial | **confused** (+0.07) | element on the aligned note |
| `fermata` | 398 | 53 | 190 | 63% (249/398) | 38% (152/398) | 27% (107/398) | 81% | partial | not confused (-0.04) | element on the aligned note |
| `trill` | 42 | 15 | 0 | 0% (0/42) | 0% (0/42) | 0% (0/42) | 93% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `mordent` | 53 | 13 | 0 | 0% (0/58) | 0% (0/58) | 0% (0/58) | 90% | **unsupported** — element never emitted | not confused (-0.05) | element on the aligned note |
| `turn` | 33 | 13 | 0 | 0% (0/35) | 0% (0/35) | 0% (0/35) | 97% | **unsupported** — element never emitted | not confused (-0.09) | element on the aligned note |
| `arpeggio` | 92 | 12 | 0 | 0% (0/312) | 0% (0/312) | 0% (0/312) | 70% | **unsupported** — element never emitted | not confused (+0.01) | element on the aligned note |
| `breath` | 26 | 13 | 0 | 0% (0/26) | 0% (0/26) | 0% (0/26) | 88% | **unsupported** — element never emitted | not confused (-0.03) | element on the aligned note |
| `dyn-pp` | 29 | 17 | 28 | 86% (25/29) | 86% (25/29) | 79% (23/29) | – | supported | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `dyn-p` | 77 | 38 | 45 | 52% (40/77) | 58% (45/77) | 42% (32/77) | – | partial | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `dyn-mp` | 34 | 21 | 35 | 94% (32/34) | 97% (33/34) | 59% (20/34) | – | supported | **confused** (+0.17) | same element/value at the aligned measure (+-1) |
| `dyn-mf` | 93 | 46 | 52 | 90% (84/93) | 45% (42/93) | 31% (29/93) | – | partial | **confused** (+0.05) | same element/value at the aligned measure (+-1) |
| `dyn-f` | 94 | 38 | 64 | 68% (64/94) | 68% (64/94) | 60% (56/94) | – | partial | **confused** (+0.12) | same element/value at the aligned measure (+-1) |
| `dyn-ff` | 35 | 17 | 32 | 77% (27/35) | 91% (32/35) | 77% (27/35) | – | supported | **confused** (+0.08) | same element/value at the aligned measure (+-1) |
| `dyn-sfz` | 14 | 11 | 4 | 29% (4/14) | 29% (4/14) | 7% (1/14) | – | partial | not confused (-0.08) | same element/value at the aligned measure (+-1) |
| `hairpin-cresc` | 104 | 30 | 43 | 45% (47/104) | 41% (43/104) | 11% (11/104) | – | partial | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `hairpin-dim` | 92 | 35 | 38 | 39% (36/92) | 38% (35/92) | 13% (12/92) | – | partial | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `pedal` | 268 | 17 | 0 | 0% (0/268) | 0% (0/268) | 0% (0/268) | – | **unsupported** — element never emitted | not confused (+0.04) | same element/value at the aligned measure (+-1) |
| `fingering` | 292 | 12 | 0 | 0% (0/292) | 0% (0/292) | 0% (0/292) | 77% | **unsupported** — element never emitted | not confused (+0.02) | element on the aligned note |
| `text-expression` | 65 | 23 | 14 | 22% (11/51) | 27% (14/51) | 18% (9/51) | – | partial | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `tempo-mark` | 175 | 74 | 172 | 48% (89/184) | 47% (86/184) | 36% (67/184) | – | partial | **confused** (+0.16) | same element/value at the aligned measure (+-1) |
| `metronome` | 144 | 54 | 141 | 88% (127/144) | 88% (127/144) | 78% (112/144) | – | supported | **confused** (+0.19) | same element/value at the aligned measure (+-1) |
| `rehearsal-mark` | 124 | 19 | 0 | 0% (0/124) | 0% (0/124) | 0% (0/124) | – | **unsupported** — element never emitted | **confused** (+0.18) | same element/value at the aligned measure (+-1) |
| `chord-symbol` | 61 | 2 | 0 | 0% (0/61) | 0% (0/61) | 0% (0/61) | – | **unsupported** — element never emitted | not confused (-0.06) | same element/value at the aligned measure (+-1) |
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
| `barline-double` | 133 | 26 | 134 | 94% (125/133) | 89% (119/133) | 81% (108/133) | – | supported | not confused (-0.06) | same element/value at the aligned measure (+-1) |
| `barline-final` | 123 | 101 | 206 | 100% (110/110) | 99% (109/110) | 91% (100/110) | – | supported | not confused (-0.03) | same element/value at the aligned measure (+-1) |
| `repeat-start` | 33 | 14 | 51 | 97% (32/33) | 94% (31/33) | 70% (23/33) | – | supported | not confused (+0.02) | same element/value at the aligned measure (+-1) |
| `repeat-end` | 40 | 16 | 67 | 98% (39/40) | 98% (39/40) | 78% (31/40) | – | supported | not confused (-0.01) | same element/value at the aligned measure (+-1) |
| `volta-1` | 16 | 13 | 32 | 88% (14/16) | 88% (14/16) | 56% (9/16) | – | supported | not confused (+0.01) | same element/value at the aligned measure (+-1) |
| `volta-2` | 16 | 13 | 21 | 38% (6/16) | 38% (6/16) | 13% (2/16) | – | partial | not confused (+0.00) | same element/value at the aligned measure (+-1) |
| `segno` | 6 | 6 | 8 | 100% (6/6) | 100% (6/6) | 67% (4/6) | – | supported | **confused** (+0.61) | same element/value at the aligned measure (+-1) |
| `coda` | 8 | 6 | 8 | 100% (8/8) | 100% (8/8) | 100% (8/8) | – | supported | not confused (-0.11) | same element/value at the aligned measure (+-1) |
| `dc` | 10 | 10 | 5 | 80% (8/10) | 50% (5/10) | 40% (4/10) | – | partial | not confused (-0.05) | same element/value at the aligned measure (+-1) |
| `ds` | 6 | 6 | 2 | 33% (2/6) | 33% (2/6) | 17% (1/6) | – | partial | not confused (-0.09) | same element/value at the aligned measure (+-1) |
| `fine` | 10 | 10 | 4 | 20% (2/10) | 10% (1/10) | 20% (2/10) | – | **unsupported** | **confused** (+0.07) | same element/value at the aligned measure (+-1) |
| `system-break` | 581 | 101 | 0 | 0% (0/581) | 0% (0/581) | 0% (0/581) | – | **unsupported** — element never emitted | not confused (-0.04) | same element/value at the aligned measure (+-1) |
| `page-break` | 90 | 10 | 0 | 0% (0/90) | 0% (0/90) | 0% (0/90) | – | **unsupported** — element never emitted | **confused** (+0.09) | same element/value at the aligned measure (+-1) |
| `multi-page` | 26 | 10 | 0 | 86% (17485/20298) | 86% (17530/20298) | 80% (16144/20298) | – | supported | not confused (-0.38) | pitch recall of the notes on pages 2+ (sem) |
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
| `melody` | 32 | 97% | 96% | 88% | 100% | 88% | 100% | 0 | 0.910 | supported |
| `melody-lyrics` | 4 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.980 | supported |
| `piano` | 29 | 100% | 100% | 93% | 100% | 100% | 100% | 0 | 0.941 | supported |
| `voice-piano` | 3 | 100% | 100% | 77% | 100% | 100% | 100% | 0 | 0.959 | supported |
| `choir-closed-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.989 | supported |
| `choir-open-satb` | 1 | 100% | 100% | 100% | 100% | 100% | 99% | 0 | 0.925 | supported |
| `choir-sab` | 1 | 100% | 100% | 23% | 100% | 100% | 100% | 0 | 0.996 | supported |
| `choir-ttbb` | 1 | 100% | 100% | 5% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `choir-ssaa` | 1 | 100% | 98% | 99% | 100% | 94% | 100% | 0 | 0.992 | supported |
| `choir-piano` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 1.000 | supported |
| `organ` | 2 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.961 | supported |
| `string-quartet` | 6 | 87% | 96% | 57% | 100% | 88% | 99% | 0 | 0.973 | supported |
| `orchestral` | 2 | 92% | 93% | 89% | 100% | 82% | 98% | 0 | 0.966 | supported |
| `lead-sheet` | 2 | 83% | 83% | 67% | 100% | 50% | 100% | 0 | 0.940 | supported |
| `hymnal-stanzas` | 9 | 99% | 100% | 99% | 100% | 100% | 99% | 0 | 0.982 | supported |
| `divisi` | 2 | 100% | 96% | 99% | 100% | 88% | 100% | 0 | 0.970 | supported |
| `cross-staff` | 1 | 100% | 100% | 100% | 100% | 100% | 100% | 0 | 0.889 | supported |
| `two-voices-one-staff-instrument` | 3 | 89% | 89% | 89% | 100% | 67% | 100% | 0 | 0.931 | supported |
| `percussion-none` | 1 | 44% | 44% | 44% | 0% | 33% | 100% | 0 | 0.628 | partial |

## Performance

Source: `mvp/work/eval-coverage-perf.json` (perf family; 63 PDFs; raster native, OCR on, 8 parallel jobs on 192 CPUs, load average 55.9 at the start). Times are the converter in a Node child process, per page, run as the browser worker runs it (`createConverter()`: each page read from disk when its turn comes, `addPage`, then `releasePage` frees its image buffers and keeps the staff-removed binary bit-packed, then `finish`); peak memory is the child's peak RSS (`maxRSS`), including Node itself (~50 MB) and the OCR engine when OCR is on. Pages are rasterised at the resolution of the scan image, so pixel count follows the source dpi.

**By source scan dpi**

| Scan dpi | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 6 | 0.968 | 4857 | 5783 | 312.2 | 371.6 |
| 150 | 6 | 2.178 | 4769 | 6006 | 315.9 | 389.4 |
| 200 | 6 | 3.869 | 4599 | 6417 | 304 | 390 |
| 300 | 33 | 8.703 | 4909 | 6487 | 366.5 | 662.4 |
| 400 | 6 | 15.475 | 8066 | 10045 | 445.7 | 566 |
| 600 | 6 | 34.806 | 5784 | 6811 | 401.1 | 444.9 |

**By page size**

| Page size | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| ~A3 | 1 | 20.49 | 6487 | 6487 | 416 | 416 |
| ~B4 | 6 | 10.25 | 6417 | 10045 | 444.9 | 566 |
| ~Letter | 1 | 9.965 | 6218 | 6218 | 466.8 | 466.8 |
| A3 | 5 | 17.403 | 5034 | 5300 | 344.6 | 369.3 |
| A4 | 45 | 8.703 | 4547 | 8182 | 345.9 | 662.4 |
| Letter | 5 | 8.415 | 5445 | 5866 | 322.8 | 344.8 |

**By page count**

| Pages | PDFs | MP/page | ms/page (median) | ms/page (max) | peak MB (median) | peak MB (max) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 51 | 8.703 | 5163 | 10045 | 339.4 | 566 |
| 5 | 3 | 8.703 | 4052 | 4170 | 518 | 523 |
| 10 | 3 | 8.703 | 4203 | 4246 | 552.2 | 553 |
| 20 | 3 | 8.703 | 4010 | 4138 | 598.8 | 603.8 |
| 40 | 3 | 8.703 | 3940 | 4096 | 658.9 | 662.4 |

**Linear fits.** ms per page = 4439.2 + **51.91 ms per megapixel** × MP per page (n=63, R²=0.158). Peak MB = 349.9 + 1.09 MB per megapixel × total MP (n=63, R²=0.659). Overall: 454 ms of conversion per megapixel.

## Items

| Item | Layout | Aggregate clean | Aggregate scan | Aggregate scan-severe | Parts (expected → scan) | ms/page | peak MB |
|---|---|---:|---:|---:|---|---:|---:|
| `layouts/choir-closed-satb-light-of-morning` | choir-closed-satb | 0.982 | 0.989 | 0.986 | 4 → 4 | 2207 | 230 |
| `layouts/choir-open-satb-gloria` | choir-open-satb | 0.916 | 0.925 | 0.879 | 4 → 4 | 2957 | 254 |
| `layouts/choir-piano-song-of-rejoicing` | choir-piano | 1.000 | 1.000 | 0.972 | 5 → 5 | 4145 | 342 |
| `layouts/choir-sab-summer-song` | choir-sab | 0.984 | 0.996 | 0.328 | 3 → 3 | 2767 | 216 |
| `layouts/choir-ssaa-winter-night` | choir-ssaa | 0.996 | 0.992 | 0.982 | 4 → 4 | 2265 | 243 |
| `layouts/choir-ttbb-evening-bells` | choir-ttbb | 1.000 | 1.000 | 0.348 | 4 → 4 | 2294 | 232 |
| `layouts/cross-staff-piano-arpeggio-study` | cross-staff | 0.884 | 0.889 | 0.794 | 1 → 1 | 1928 | 234 |
| `layouts/divisi-choir-bright-new-day` | divisi | 0.988 | 0.988 | 0.942 | 4 → 4 | 5063 | 301 |
| `layouts/divisi-strings-lament` | divisi | 0.974 | 0.953 | 0.938 | 4 → 4 | 2499 | 265 |
| `layouts/hymnal-stanzas-light-of-ages` | hymnal-stanzas | 1.000 | 0.999 | 0.996 | 4 → 4 | 3288 | 259 |
| `layouts/lead-sheet-long-road` | lead-sheet | 0.888 | 0.920 | 0.840 | 1 → 1 | 3007 | 241 |
| `layouts/melody-cello-elegy-2page` | melody | 0.886 | 0.843 | 0.707 | 1 → 1 | 1567 | 286 |
| `layouts/melody-flute-air` | melody | 0.959 | 0.977 | 0.972 | 1 → 1 | 1756 | 235 |
| `layouts/melody-lyrics-morning-song` | melody-lyrics | 1.000 | 1.000 | 0.938 | 1 → 1 | 2147 | 260 |
| `layouts/orchestral-festive-march-9-staves` | orchestral | 0.973 | 0.957 | 0.896 | 9 → 9 | 4537 | 448 |
| `layouts/organ-three-staves-chorale-prelude` | organ | 0.987 | 0.948 | 0.775 | 1 → 1 | 2431 | 223 |
| `layouts/piano-grand-staff-prelude` | piano | 0.899 | 0.954 | 0.952 | 1 → 1 | 1924 | 242 |
| `layouts/string-quartet-minuet` | string-quartet | 0.777 | 0.987 | 0.775 | 4 → 4 | 4581 | 306 |
| `layouts/two-voices-piano-song-without-words` | two-voices-one-staff-instrument | 0.996 | 0.996 | 0.723 | 1 → 1 | 1797 | 221 |
| `layouts/voice-piano-night-song` | voice-piano | 0.979 | 0.935 | 0.471 | 2 → 2 | 2497 | 275 |
| `lyrics/lyr01-elisions-three-languages` | melody-lyrics | 0.985 | 0.979 | 0.890 | 1 → 1 | 2602 | 241 |
| `lyrics/lyr02-non-ascii-four-languages` | melody-lyrics | 0.975 | 0.975 | 0.943 | 1 → 1 | 3101 | 230 |
| `marks/mk01-articulations-violin` | melody | 0.974 | 0.974 | 0.967 | 1 → 1 | 1785 | 231 |
| `marks/mk02-ornaments-fermatas-flute` | melody | 0.951 | 0.958 | 0.959 | 1 → 1 | 1664 | 226 |
| `marks/mk03-dynamics-hairpins-cello` | melody | 0.984 | 0.968 | 0.780 | 1 → 1 | 1900 | 257 |
| `marks/mk04-piano-pedal-arpeggio-fingering` | piano | 0.953 | 0.949 | 0.842 | 1 → 1 | 2435 | 249 |
| `marks/mk05-tempo-text-rehearsal-oboe` | melody | 0.982 | 0.956 | 0.723 | 1 → 1 | 2130 | 234 |
| `marks/mk06-lead-sheet-chord-symbols` | lead-sheet | 0.970 | 0.960 | 0.836 | 1 → 1 | 2277 | 254 |
| `marks/mk07-vocalise-voice-piano` | voice-piano | 0.980 | 0.993 | 0.907 | 2 → 2 | 2395 | 237 |
| `marks/mk08-string-quartet-marks` | string-quartet | 0.979 | 0.977 | 0.911 | 4 → 4 | 2525 | 253 |
| `marks/mk09-stacked-marks-viola` | melody | 0.935 | 0.920 | 0.895 | 1 → 1 | 2129 | 249 |
| `notes/nt01-note-values` | melody | 0.895 | 0.924 | 0.673 | 1 → 1 | 1964 | 253 |
| `notes/nt02-dots` | melody | 0.963 | 0.936 | 0.879 | 1 → 1 | 1985 | 230 |
| `notes/nt03-chords` | piano | 0.974 | 0.970 | 0.900 | 1 → 1 | 1869 | 228 |
| `notes/nt04-beams` | melody | 0.985 | 0.971 | 0.978 | 1 → 1 | 2216 | 241 |
| `notes/nt05-flags-stems` | melody | 0.847 | 0.850 | 0.759 | 1 → 1 | 2080 | 216 |
| `notes/nt06-ledger-lines` | piano | 1.000 | 0.953 | 0.953 | 1 → 1 | 1826 | 230 |
| `notes/nt07-grace-notes` | melody | 0.971 | 0.927 | 0.912 | 1 → 1 | 1939 | 250 |
| `notes/nt08-cue-notes` | melody | 0.960 | 0.946 | 0.947 | 1 → 1 | 1756 | 254 |
| `notes/nt09-tremolos` | piano | 0.719 | 0.751 | 0.635 | 1 → 1 | 1887 | 242 |
| `notes/nt10-piano-etude` | piano | 0.989 | 0.988 | 0.959 | 1 → 1 | 1950 | 229 |
| `percussion/perc01-parade-flute-snare-drumset` | percussion-none | 0.646 | 0.628 | 0.637 | 3 → 2 | 2223 | 211 |
| `perf/perf-hymn-a3-300dpi` | hymnal-stanzas | 0.999 | 0.998 | 0.998 | 4 → 4 | 4730 | 320 |
| `perf/perf-hymn-a4-100dpi` | hymnal-stanzas | 0.925 | 0.931 | 0.784 | 4 → 4 | 5091 | 342 |
| `perf/perf-hymn-a4-150dpi` | hymnal-stanzas | 0.983 | 0.955 | 0.964 | 4 → 4 | 4659 | 323 |
| `perf/perf-hymn-a4-200dpi` | hymnal-stanzas | 0.996 | 0.977 | 0.921 | 4 → 4 | 4779 | 304 |
| `perf/perf-hymn-a4-300dpi` | hymnal-stanzas | 0.997 | 0.997 | 0.984 | 4 → 4 | 5093 | 305 |
| `perf/perf-hymn-a4-400dpi` | hymnal-stanzas | 0.997 | 0.997 | 0.964 | 4 → 4 | 4935 | 329 |
| `perf/perf-hymn-a4-600dpi` | hymnal-stanzas | 1.000 | 0.997 | 0.981 | 4 → 4 | 4931 | 324 |
| `perf/perf-hymn-letter-300dpi` | hymnal-stanzas | 0.998 | 0.991 | 0.966 | 4 → 4 | 5038 | 348 |
| `perf/perf-pages-01` | piano | 0.981 | 0.968 | 0.918 | 1 → 1 | 3463 | 332 |
| `perf/perf-pages-05` | piano | 0.939 | 0.942 | 0.914 | 1 → 1 | 3981 | 555 |
| `perf/perf-pages-10` | piano | 0.933 | 0.927 | 0.893 | 1 → 1 | 3844 | 622 |
| `perf/perf-pages-20` | piano | 0.941 | 0.934 | 0.903 | 1 → 1 | 3570 | 724 |
| `perf/perf-pages-40` | piano | 0.927 | 0.914 | 0.878 | 1 → 1 | 3542 | 674 |
| `perf/perf-piano-a3-300dpi` | piano | 0.964 | 0.929 | 0.866 | 1 → 1 | 5479 | 332 |
| `perf/perf-piano-a4-100dpi` | piano | 0.885 | 0.743 | 0.709 | 1 → 1 | 3013 | 269 |
| `perf/perf-piano-a4-150dpi` | piano | 0.936 | 0.890 | 0.802 | 1 → 1 | 2932 | 241 |
| `perf/perf-piano-a4-200dpi` | piano | 0.964 | 0.878 | 0.817 | 1 → 1 | 2867 | 248 |
| `perf/perf-piano-a4-300dpi` | piano | 0.946 | 0.950 | 0.768 | 1 → 1 | 3032 | 261 |
| `perf/perf-piano-a4-400dpi` | piano | 0.932 | 0.940 | 0.884 | 1 → 1 | 3048 | 270 |
| `perf/perf-piano-a4-600dpi` | piano | 0.960 | 0.907 | 0.943 | 1 → 1 | 3118 | 255 |
| `perf/perf-piano-letter-300dpi` | piano | 0.954 | 0.930 | 0.782 | 1 → 1 | 3031 | 255 |
| `pitch/pitch-cov-accidentals-chords-piano` | piano | 0.976 | 0.994 | 0.869 | 1 → 1 | 1953 | 246 |
| `pitch/pitch-cov-accidentals-melody` | melody | 0.877 | 0.927 | 0.843 | 1 → 1 | 1985 | 223 |
| `pitch/pitch-cov-clef-changes-piano` | piano | 0.945 | 1.000 | 0.367 | 1 → 1 | 1809 | 235 |
| `pitch/pitch-cov-clefs-all` | melody | 0.741 | 0.727 | 0.733 | 1 → 1 | 1945 | 232 |
| `pitch/pitch-cov-clefs-quartet` | string-quartet | 0.772 | 0.955 | 0.756 | 4 → 4 | 2247 | 226 |
| `pitch/pitch-cov-key-changes-organ` | organ | 0.989 | 0.974 | 0.813 | 1 → 1 | 2078 | 260 |
| `pitch/pitch-cov-keys-major-flats` | piano | 1.000 | 1.000 | 0.678 | 1 → 1 | 1949 | 243 |
| `pitch/pitch-cov-keys-major-sharps` | melody | 0.997 | 0.911 | 0.948 | 1 → 1 | 2024 | 222 |
| `pitch/pitch-cov-keys-minor-flats` | melody | 0.967 | 0.971 | 0.885 | 1 → 1 | 1931 | 226 |
| `pitch/pitch-cov-keys-minor-sharps` | melody | 0.621 | 0.613 | 0.532 | 1 → 1 | 2435 | 239 |
| `pitch/pitch-cov-ottava-ledger-melody` | melody | 1.000 | 1.000 | 1.000 | 1 → 1 | 1830 | 225 |
| `pitch/pitch-cov-ottava-piano` | piano | 0.981 | 0.938 | 0.905 | 1 → 1 | 1957 | 252 |
| `rests/rst01-rest-values` | melody | 0.850 | 0.829 | 0.695 | 1 → 1 | 2057 | 251 |
| `rests/rst02-dotted-rests` | melody | 0.934 | 0.948 | 0.786 | 1 → 1 | 2202 | 231 |
| `rests/rst03-whole-bar-rests-simple` | melody | 0.904 | 0.904 | 0.701 | 1 → 1 | 2065 | 255 |
| `rests/rst04-whole-bar-rests-compound` | melody | 0.989 | 1.000 | 0.940 | 1 → 1 | 2046 | 230 |
| `rests/rst05-multibar-rests` | melody | 0.881 | 0.807 | 0.626 | 1 → 1 | 2175 | 227 |
| `rests/rst06-two-voice-rests` | two-voices-one-staff-instrument | 0.856 | 0.863 | 0.840 | 1 → 1 | 1964 | 238 |
| `rests/rst07-piano-rests` | piano | 0.954 | 0.959 | 0.940 | 1 → 1 | 2194 | 230 |
| `rests/rst08-tuplet-beam-rests` | melody | 0.863 | 0.842 | 0.367 | 1 → 1 | 2519 | 249 |
| `rests/rst09-quartet-rests` | string-quartet | 0.990 | 0.976 | 0.921 | 4 → 4 | 3851 | 343 |
| `structure/str01-double-final-barlines` | melody | 1.000 | 1.000 | 0.944 | 1 → 1 | 1915 | 212 |
| `structure/str02-repeat-signs-piano` | piano | 0.988 | 0.990 | 0.980 | 1 → 1 | 2011 | 269 |
| `structure/str03-voltas-string-quartet` | string-quartet | 0.983 | 0.980 | 0.467 | 4 → 4 | 4921 | 368 |
| `structure/str04-segno-coda-ds` | melody | 0.882 | 0.883 | 0.909 | 1 → 1 | 2250 | 214 |
| `structure/str05-fine-dc-al-fine-piano` | piano | 1.000 | 1.000 | 0.481 | 1 → 1 | 2227 | 259 |
| `structure/str06-breaks-two-pages-song` | voice-piano | 0.976 | 0.948 | 0.844 | 2 → 2 | 3447 | 456 |
| `structure/str07-orchestral-five-pages` | orchestral | 0.982 | 0.975 | 0.957 | 7 → 7 | 3761 | 453 |
| `structure/str08-variations-twelve-pages-piano` | piano | 0.996 | 0.983 | 0.964 | 1 → 1 | 1805 | 466 |
| `time/t01-simple-meters` | melody | 0.962 | 0.961 | 0.855 | 1 → 1 | 2237 | 218 |
| `time/t02-compound-irregular` | melody | 1.000 | 1.000 | 0.971 | 1 → 1 | 2218 | 245 |
| `time/t03-common-cut-piano` | piano | 0.991 | 1.000 | 0.931 | 1 → 1 | 2438 | 225 |
| `time/t04-pickup-song` | melody-lyrics | 0.953 | 0.966 | 0.955 | 1 → 1 | 2432 | 237 |
| `time/t05-triplets-duplets` | melody | 0.848 | 0.875 | 0.841 | 1 → 1 | 2114 | 241 |
| `time/t06-quint-sext-sept` | melody | 0.973 | 0.971 | 0.920 | 1 → 1 | 1705 | 225 |
| `time/t07-nested-tuplets` | melody | 0.819 | 0.812 | 0.833 | 1 → 1 | 1782 | 233 |
| `time/t08-ties-systems-pages` | piano | 0.984 | 0.997 | 0.409 | 1 → 1 | 1681 | 291 |
| `time/t09-two-voices-guitar` | two-voices-one-staff-instrument | 0.933 | 0.933 | 0.765 | 1 → 1 | 1777 | 241 |
| `time/t10-quartet-meters` | string-quartet | 0.987 | 0.962 | 0.643 | 4 → 4 | 2708 | 257 |
