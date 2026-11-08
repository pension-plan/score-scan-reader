# Spike: OpenCV.js as a fallback symbol identifier

Date: 2026-11-08 (pre-clean update the same day). Scope: should OpenCV.js be added to the browser OMR app as a fallback for identifying music symbols where the classical reading (`mvp/src/*.js`) and the copista-2m ML pass are missing or weak? Everything below was measured on this machine (Linux, 192 cores, shared and heavily loaded: load average 115–170 during the runs) with the corpus as it stands on disk. Experiment code, data and logs are in `spike/opencv/`. The compact results are in `spike/opencv/results/`, and every number can be regenerated (see "Reproduce").

## Update: 32nd and 64th rests whose hooks read as heads (rest gaps)

On scans a 32nd or 64th rest often carries two or three "heads" (its hooks), not one, and `rests.js` only asked the
template reader about a tall glyph with a single head on it. Now a tall glyph with up to three filled heads, each at
most 1.05 spaces wide (narrower than noteheads; real two-note chords on flagged stems are 1.2–1.3 wide and stay
notes), goes to `readRestGlyph` as well, and all the heads on it are dropped when it is a 16th–64th rest. Coverage
(no OCR, clean / scan / severe): `rest-64th` 25 / 10 / 7 → 26 / 22 / 12 of 30, `rest-32nd` 97 / 81 / 60 → 97 / 95 /
79 of 102. A/B: coverage +0.0003 per item (`rst01` scan +0.043, severe +0.051), no item down; challenge and benchmark
unchanged.

Tried and not shipped: cue-size heads (`nt08-cue-notes`, 24 cue notes, all missed: they open to 0.65–0.72 space wide,
under the 0.8 floor). Admitting small solid blobs finds them but adds false heads elsewhere and the cue notes are then
written as ordinary notes in the bar: coverage −0.0026 (`nt08` −0.12, `perc01` −0.10, `nt07` −0.07). They need
`score.js` to write them as `<cue/>` notes outside the bar's count before detection can be switched on.

## Update: upside-down pages whose staves end in keys

`pitch-cov-keys-minor-sharps` severe is printed upside down. The front end did not turn it: its staves end in sharp
keys, so they are dense at both ends (`invertedShare` 0.25), and the clef-count test in `omr.js` does not catch it
either (upside-down treble clefs read as bass clefs). `front.js` now also checks for a title block below the music
with no ink at all above it (`titleBelow`, the mirror of `titleAbove`). When it finds one, it reads the page turned
and keeps the turn only when the clefs at the staff starts match their templates better by 0.1 on average
(`cv.js` `clefScore`). That item went 0.589 → 0.911 with all eight keys right. Nothing else moved: coverage, challenge
(the rot90 / rot180 items included) and benchmark are otherwise unchanged.

## Update: hollow heads on ledger lines of scans (L1)

`nt06-ledger-lines` lost 19 of its 37 half and whole notes on the plain scan. A hollow head on a ledger line is
judged by its ink with the ledger rows left out, relative to the page: hollow when under 0.66 and 0.15 under the
lightest "filled-looking" head (≥ 0.66). On the scan the hollow heads read 0.61–0.68 and the filled ones 0.79–0.94,
so the 0.67 hollow ones set the reference and the cut-off fell to 0.52. Now only clearly filled heads (≥ 0.75) set
the reference, and the cut-off is 0.1 under the lightest of them, at most 0.7. Severe pages whose values run together
still keep their heads filled. Coverage (OCR, clean / scan / severe): `note-half` 1426 / 1311 / 650 → 1432 / 1351 /
716 of 1510, `note-whole` severe 85 → 95 of 199. A/B (no OCR): coverage +0.0010 per item (`nt06` scan 0.953 →
1.000, `nt03-chords` severe +0.048), worst −0.005; challenge +0.0003, worst −0.015 (`pitch-satb-ledger-extremes`
severe); benchmark +0.0002.

Tried and not shipped: (1) the same test for heads on staff lines, where a blurred scan leaves the line in R through
the head (`organ-three-staves` scan reads 6 of 20 such half notes as quarters). Coverage −0.0013: filled heads on
lines read lighter than the page's ledger heads, so grace and cue notes and dotted notes turned hollow. (2) Cutting
an arpeggio's wavy line off a hollow chord it fuses with, and letting stacks taller than four heads give their top
head. That fixes chords on `perf-pages-40` page 21 but measured 0.0000 overall, with `voice-piano-night-song` severe
−0.017.

## Update: key signatures read slot by slot (L24 severe scans, L2 old engraving)

The component parse in `assemble.js` misses key signature signs that touch something: a flat fused with the treble
clef (`golden1923-auld-lang-syne` system 1 read no key), four flats run together on a bass staff (the same page,
system 5, read 0 for A-flat major), sharps cut by a shadow on a curled severe scan (4 read as 1), flats filled solid
on heavy severe prints, and the narrow flats of old engravings. `cv.js` `readKeySig` (called from `readHeaders`,
`assemble.js` untouched) reads the signature slot by slot. Signs stand at fixed positions for each clef (sharps
F C G D A E B, flats B E A D G C F; treble, bass and alto clefs), so for each next sign it takes the best match of
the Bravura sharp (or flat) template in a window at that slot's height, 0.6–1.7 spaces right of the previous one
(the first may overlap the clef's end). A slot counts at score ≥ 0.42 when it beats noteheads by 0.05 and digits
(time signatures; a solid flat looks like a 4), naturals and the other accidental at all. The result only ever adds
signs: it replaces the parse when it finds more of the same kind, or (first sign ≥ 0.55) when the parse found none.
Then the header end moves past the last sign, and heads read on the signs are dropped.

On the five real scans of L2 it agrees with every key the parse already had right, and fixes both auld-lang-syne
misses. golden1923-america, methodist1905 st-anselm and tappan-dennis, and haupt1867 were already right at every
system start, so L2 there is down to mid-piece key changes. A/B on the same source (no OCR): coverage +0.0012 per
item, no item down (`perf-piano-a4-300dpi` severe +0.058, `keys-minor-sharps` severe +0.057); challenge +0.0005, no
item down (`pitch-ttbb-enharmonic-keys` severe 0.473 → 0.622); benchmark unchanged. Coverage per tag (OCR, severe):
`key-s1` 13 → 14 of 16, `key-f7` 0 → 1 of 2, `key-change` 15 → 16 of 34. `key-0` 35 → 34: the upside-down
`keys-minor-sharps` severe page, which is read wrongly either way (front.js does not turn it; raised with the
structure agent).

## Update: heads beside accidentals, courtesy accidentals (L24)

Courtesy accidentals were not misread signs: the notes they stand before were lost. On `pitch-cov-accidentals-melody`
(clean) 13 of 49 heads were missing, almost all right of an accidental. Two front-end causes (plain JS, no templates):
- `heads.js`: `fillHoles` fills the paper between an accidental and its head where staff lines close it above and
  below, so the two fuse into one blob. `headWindows` then centred the head window too far left (up to 0.4 space),
  so the stem search missed the stem and the head was dropped. When the blob was over 2.4 spaces wide (a sharp, or a
  parenthesised sign) it was thrown away as a beam. Now columns with almost no ink of their own in R inside such a blob
  are treated as paper. The part left of the gap is dropped, and so no longer counts towards the blob width, when three
  things hold: the part right of the gap is head-wide; the left part has an accidental's stroke (2.2–3.3 spaces in B,
  taller than a time-signature digit and shorter than a stem or barline; a stem of a fused neighbour cost
  `klauser1867` 0.021 before the upper limit); and the gap is at least 0.2 space wide (the digits of 12/8 sit 0.14
  apart, and reading the "2" as a head turned 12/8 into 2/8 in `rst04`).
- `front.js` `accidentalBefore`: a parenthesised sign or a natural's box filled solid reads as a lone head with a short
  "stem" (the sign's stroke). A single-head chord whose stroke is under 2.6 spaces, does not end in a beam (beamed
  notes under a low beam have short stems: Twinkle piano lost 0.025 without this check), has two strokes 1.6 spaces
  or taller through its row (a sharp's or natural's pair; a grace note has one stem: the first version, 6b891a8, cost
  `grace` 117 → 95 of 252 on severe coverage scans, now 116) and stands 0.8–3.6 spaces left of a chord level with it
  (±1 position) is dropped. The regress check still counts fewer `<grace>` elements (benchmark 36 → 29, challenge
  288 → 264): the ones that went were sharps read as small heads (the benchmark truth has no grace notes at all).

Coverage (OCR, clean / scan / severe): `acc-courtesy` 2 / 5 / 5 → **9 / 9 / 8** of 9, `acc-sharp` 53 / 62 / 37 →
**77 / 75 / 49** of 82, `acc-flat` 21 / 24 / 26 → 27 / 27 / 23 of 28, `acc-natural` 43 / 45 / 34 → 49 / 49 / 40 of 53.
A/B on the same source (no OCR): coverage mean +0.0024 per item (`accidentals-melody` clean 0.810 → 0.918,
`chords-piano` clean 0.976 → 1.000), worst `perf-piano-a4-200dpi` severe −0.015; challenge +0.0008, worst −0.007;
benchmark +0.0026, real scans 0.811 → 0.810. `<accidental cautionary="yes">` is still never written (score.js), so
the matrix caps the tag at partial.

## Update: rests from templates (L3a)

Glyph-level (truth rest boxes, current code): 32nd rests were found 22 / 15 / 3 times of 22 / 22 / 17 (clean / scan /
severe), 64th 7 / 1 / 0 of 10, quarter rests on severe scans 76 of 129: misses, not confusions. Two causes:
- a 16th / 32nd / 64th rest's hooks pass for a notehead, so the tall glyph had a "head" on it and was skipped as part
  of a note (and the head became a false note);
- glyphs the shape rules could not classify were dropped.
`rests.js` now asks `cv.js` `readRestGlyph` (Bravura quarter–64th rest templates against heads, flags, single
accidentals, digits, dynamics letters and an F clef; score ≥ 0.62 and 0.08 above every other glyph) in both cases: a
tall glyph with one head on it becomes a 16th–64th rest when the template says so (the head is dropped by
`mergeRests`), and an unclassified glyph becomes a rest unless it stands just left of a chord (an arpeggio's wavy
line matched a quarter rest: `mk04` lost 0.048 before that rule). Glyph-level after: 32nd 22 / 18 / 7 of 22 / 22 / 17,
64th 10 / 5 / 3 of 10, 16th severe 81 → 94 %, quarter severe 60 → 67 %.

Coverage per tag (no OCR, clean / scan / severe): `rest-32nd` 97 / 40 / 21 → **102 / 80 / 57** of 102, `rest-64th`
12 / 4 / 0 → **24 / 11 / 4** of 30, `rest-quarter` +3 / +2 / +11, `rest-16th` +1 / +2 / +7, `note-32nd` +22 / +47 / +15,
`note-quarter` −8 / −11 / +63; false notes in bars with 32nd / 64th rests 88 → 78 / 63 → 56 (clean). Aggregates: coverage
0.8032 → 0.8036 (rests +0.0078; largest drop −0.0012), challenge 0.8313 → 0.8314 (rests +0.0071; largest drop
−0.0006), benchmark with OCR 0.951 = 0.951 (one item −0.0003).

## Update: beam pieces taken for heads (L23, part 4)

The false notes in bars with dotted rhythms (`dot` "confused" in the matrix) were not dots: on `nt02-dots` the extra
notes are filled "heads" found on beams (a beam's end segment at the last stem, or a 16th / 32nd beam stack between
two stems). Their ink is a beam's thickness tall: 0.43–0.65 of a space at the head's columns against 1.0–1.2 for
real filled heads on the coverage notes family (gaps of a staff line's thickness bridged: line removal cuts heads on
lines; without the bridge, heads on lines were lost and hymn pages dropped up to 0.04). `front.js` now drops filled
heads under 0.72 of a space tall, next to the existing hollow-at-stem-tip filter. `nt02-dots` page 1: 93 → 82 heads.

Coverage (no OCR): false notes in bars with dots 790 → 725, with 16ths 519 → 438, with 32nds 112 → 97 (clean);
`dot` +27 / +17 / +4, `note-8th` +15 / +27 / −5, `note-16th` +10 / +3 / −4, `stem-down` +50 / +37 / +1, `slur` clean +13.
Aggregates: coverage 0.7870 → 0.7878 (42 items changed, largest drop −0.007), challenge 0.8288 → 0.8290 (largest drop
−0.020, `agrace-satb-photocopy-thick` mild), benchmark with OCR 0.9502 → 0.9501 (one item −0.003).

## Update: hollow heads on ledger lines (L23, part 3)

Half and whole notes on a ledger line came out filled (24 of 73 half-note chords on the clean pages checked; all
at |p| ≥ 6, even): the ledger is left in R and runs through the head's middle, where the hollow test looks. For
such heads `heads.js` now measures the ink over the head's box with the ledger's rows left out: 0.52–0.64 for
hollow heads and ≥ 0.85 for filled ones on clean pages; on degraded scans the values run together (0.63–0.95), so a
head is called hollow only under 0.66 and 0.15 under the page's lightest filled-looking ledger head (a fixed 0.72
cost `rh03-meter-changes-piano` severe 0.051). Filled half-note chords 24 → 2.

Coverage per tag (no OCR, clean / scan / severe): `note-whole` 139 / 129 / 91 → **216 / 192 / 120** of 537, `note-half`
3360 / 3071 / 1832 → **3692 / 3148 / 1838** of 4977, `ledger-below` +53 / +43 / +23, `dot` +12 / +6 / −1, `ledger-above`
severe −8. Aggregates: coverage 0.7845 → 0.7870 (duration +0.0075; largest drop −0.018), challenge 0.8282 → 0.8288
(largest drop −0.018), benchmark with OCR 0.9500 → 0.9502.

## Update: stacked hollow chords (L23, part 2)

A stack of hollow heads (a whole- or half-note chord in thirds) is one tall blob; `heads.js` cut it into equal steps
whose centres fell on the outlines between the heads, so only the top head survived. Now, for a tall blob about a
head wide, `heads.js` also lists the staff positions down it whose inside is empty and closed on both sides (a ledger
line through the middle is tolerated) as `stacked` candidates; `assemble.js` adds a candidate to the chord found at
that x only right of the staff's header and only next to the chord's own heads (clef loops and "6" / "8" digits of a
time signature, and text above a lead sheet, pass the hollow test too: adding them straight into the head list
cost up to 0.13 on severe scans). The added head shares the found head's stem.

Coverage per tag (no OCR, clean / scan / severe): `note-whole` 136 / 112 / 83 → 139 / 129 / 91 of 537, `note-half`
3351 / 3050 / 1769 → 3360 / 3071 / 1832, `chord` +54 / +79 / +140, stems and dots up a little; `ledger-below` clean
−1. Aggregates: coverage 0.7843 → 0.7845 (73 items changed, the largest drop −0.019); challenge 0.8282 = 0.8282
(21 changed, drops ≤ 0.005); benchmark with OCR unchanged.

## Update: 32nd and 64th notes (L23, part 1)

`assemble.js`: `countBeams` searched beams over 1.6 spaces from the stem tip and capped the count at 3, and the
divisions per quarter (840) could not express a 64th. 32nds were read as 16ths, 64ths as 16ths or 8ths
(truth stems by duration log on the notes family: 32nd → 1 of 86 right, 64th → 0 of 42). Now the count within 1.6
spaces is kept as it was, and beams beyond it count only when they continue the stack at the same gap (±0.12
space) and thickness (±25 %) as the first two, up to four; `DIV` = 1680; quintuplets / septuplets of 32nds take
the 5:8 / 7:8 ratio (a beat), not 5:4 / 7:4 (only reachable now that 32nds are read).

Coverage (no OCR, per tag, clean / scan / severe; `spike/opencv/results/r9-*.txt`): `note-32nd` **40 / 42 / 21 →
394 / 403 / 370 of 709**, `note-64th` **0 → 69 / 66 / 33 of 123**, `note-quarter` +226 / +238 / +158 (bars that
add up), `tuplet-7` 68 → 75, `rest-32nd` +3; down: `rest-64th` 16 / 7 → 11 / 3 of 30, `note-8th` scan −8,
`note-half` severe −3. Aggregates: coverage 0.7821 → 0.7843 (duration +0.010; 44 items up, 4 down:
`perf-piano-a4-150dpi` severe −0.029, `perf-piano-a4-600dpi` severe −0.028, `perf-piano-letter-300dpi` scan
−0.020, `perf-piano-a4-100dpi` severe −0.002 — the same pieces' clean and other variants gain up to +0.030; their
64ths are now read, and the alignment of the rest of those degraded pages shifts); challenge 0.8278 → 0.8282 (9 up,
4 down by at most 0.0045); benchmark with OCR 0.9499 → 0.9500.

## Update: double sharps and double flats from templates (L24)

`cv.js` `fallbackAccidental`, asked by `assemble.js` `headAccidental` only when the classical accidental reader finds
nothing left of a head. The classical reader never outputs double accidentals (its candidates are 1.3–3.8 spaces
tall; a double sharp is a one-space x). Candidates: a component (or pieces within a quarter space of each other:
staff-line removal cuts an x on a line in two) about a space square, centred on the head's height, scored against
the Bravura double-sharp template, or a 1–2.4 × 1.5–3.4 space glyph whose bowl sits at the head's height against
the double-flat template; accepted at a score ≥ 0.55 and 0.08 above heads, dots, rests and single accidentals.

Coverage (no OCR, per tag; `spike/opencv/results/r8-*.txt`): `acc-double-sharp` **0 → 65 / 55 / 11 of 124**
(clean / scan / severe), `acc-double-flat` **0 → 9 / 11 / 9 of 13**; with the right accidentals the bars add up and
note values follow (`note-8th` clean +59, `note-16th` +29, `stem-down` +103, `tuplet-6` +22); `acc-flat` clean
39 → 38. Aggregates: coverage 0.7818 → 0.7821 (35 items up, 2 down by 0.0026), challenge 0.8277 → 0.8278 (8 up,
none down), benchmark with OCR unchanged (0.9499). Key signatures with 4+ signs read 13–17 of 15–17 on clean and
scan already (the earlier 25 % / 0 % figures were from an older matrix); their severe-scan losses and courtesy
accidentals (16 / 39) are left for later.

## Update: dashed staves re-anchored; local threshold tried (not shipped)

**Re-anchor** (`staves.js` `detectDashedStaves`): with four of five lines allowed, the comb also matched a staff one
line off (an empty position above, the real bottom line left out; L11 page 1 staff 2: fitted at 565 / 578 / 591 /
603 / 616 px, the dashes at 578 … 628). Each fallback staff is now shifted by one line when the five positions one
line up or down carry clearly more ink (weakest line × 1.2). L11 `hymn-descant-cue-notes-amen-small` severe **0.228 →
0.550** (pitch 0.12 → 0.64, duration 0.08 → 0.43, parts 0.38 → 0.86): heads on the staff lines are no longer removed
with them, clefs read (G / F), 4 + 3 and 4 + 5 measures found. Challenge 0.8268 → 0.8277, 2 items changed, both up
(also `wind-melody-phone` severe +0.020); coverage unchanged. Still missing on L11: barlines in some measures, about a
third of the heads on the descant staff, the 75 % descant staff's own system and the Amen staff on page 2.

**Local (Sauvola) threshold**, window three staff spaces, tried on rereads of pages whose reading looks broken:
- L19 `satb-closed-lyrics-both-staves-de` severe gains (k = 0.1: barlines 7 → 20, measures 2 + 4 → 5 + 5;
  aggregate 0.635 → 0.680), but
- gated on a broken first reading, the reading-coherence check is fooled by the extra barlines Sauvola invents on
  noisy pages: challenge −0.004 (`andantino-piano-combo` scan −0.63, `wind-melody-phone` scan −0.57,
  `lyr04` severe −0.25);
- gated on the severe-phone quality rule instead: L19 +0.045, but `andantino-piano-phone` severe −0.385,
  `twinkle-piano2p-phone` severe −0.100, `agrace-satb-phone` severe −0.094.
No gate separated L19 from the pages it hurts without fitting to that one item, so it is not shipped
(`binarize.js` already has `sauvola()`; front.js would only need a mode to use it).

## Update: dashed-staff fallback finder (L11)

`staves.js` `detectDashedStaves`, called from `front.js` only when the normal finder (all binarisation modes) found
no staff at all. Staff lines that survive only as dashes never give a strip five clean projection peaks, and the
staff-space estimate is wrong (L11 severe: estimated 24 px, true 12.4 px). The fallback:
- staff space from the autocorrelation of the thin-line row profile over 10 wide strips (lag 5–40 px, the lag
  whose double also matches; sub-pixel by a parabola): 12.53 / 12.31 px on the two L11 pages;
- per strip, rows where four of five lines at that spacing carry line ink and the rows between them are
  lighter (a text block or beam is dense throughout); local maxima tracked across strips; lines fitted equally
  spaced; extents trimmed / extended along the staff's slope while one-space windows show dashes on three lines,
  and extended to the page's shared margins when a third of the way still shows dashes.

Result (`spike/opencv/results/r6-*.txt`): L11 `hymn-descant-cue-notes-amen-small` severe **0.113 → 0.228** (4 + 4
staves found where there were none; pitch 0 → 0.12, parts 0.07 → 0.38). Challenge 0.8265 → 0.8268, 2 items changed,
both up (also `wind-melody-phone` severe +0.013); coverage unchanged (its two pages without staves,
`pitch-cov-clef-changes-piano` and `rst08-tuplet-beam-rests` severe, have their staff lines erased altogether, not
dashed: nothing to fit). What breaks next on L11: on the found staves only 8–18 heads per staff are detected
(about a third), barlines are not found (one measure per system), and on page 2 the 75 % descant staff and the
14-pt Amen staff are missed or merged; the cue-size notes are not reached yet. The head and barline detectors
would need the same dashed-line tolerance.

## Update: dewarp of photographed / curled pages, flatten for severe phone shots (plain JS)

**Dewarp** (`cv.js` `dewarpPage`, `dewarpReading`; hook in `omr.js` `analyse`). After the global deskew a phone
shot still has staves at different slopes, and its barlines and staff ends lean (perspective). Systems then split
and barlines go unfound (`andantino-piano-phone` severe: 6 systems of 1–2 staves, 1 measure each).
- Mesh warp from the staves: each staff's middle line and space (a quadratic fit along it, so a misread line end
  cannot bend the page) become a horizontal line with one common space; gaps between staves are rescaled by the
  local space; the right margin (justified staff ends) is made upright, and the left margin too when its staff
  starts lie on one line (keystone), otherwise a plain shear. The map is computed on an 8 px grid.
- Tried first and dropped: a single homography fitted to the staff geometry (photographed pages are not flat
  enough: fit errors of 1–2 staff spaces), and a horizontal rescale from the staff space (the space shrinks
  differently across and down the page; it sheared barlines between the staves of a system).
- Gated twice: the page's staves must disagree (slope spread > 0.6 %, bend > 0.5 space, or right-margin lean
  > 1.5 %; clean pages measure ≤ 0.13 %, ≤ 0.05, ≤ 1.2 %), **and** the plain reading must look broken (systems of
  unequal size, or under two measures per system). The page is then read again and the second reading is kept
  only if it has clearly more staff-measure cells (a system split into single staves gains nothing). Two-up
  spreads, their halves and landscape sheets are left alone (dewarping them lost up to 0.47).

**Flatten for severe phone shots**: `mid` > 0.5, `bgLow` > 0.33, `bgStd` > 4.5, `speck` < 200 (milder phone
shots lose with it). If a repaired page shows no staves at all (`wind-melody-phone` severe: noise in the dark
surround amplified into texture), `front()` reads the page as it was.

A/B, same src otherwise (`spike/opencv/results/r5-*.txt`):

| set | aggregate | items changed |
|---|---|---|
| challenge (no OCR, 365) | 0.8228 → **0.8265** (pitch +0.006, duration +0.006, rests +0.011) | 9, all up; none down |
| coverage (no OCR, 306) | 0.7770 → **0.7818** | 7, all up (up to +0.44); none down |
| benchmark with OCR (20) | 0.9499 → 0.9499, real 0.9295 = | 0 |

| class (challenge) | all | scan | scan-mild | scan-severe |
|---|---|---|---|---|
| phone | 0.824 → **0.865** | = | = | 0.708 → **0.829** |
| book | 0.888 → 0.892 | = | = | 0.883 → 0.896 |
| combo | 0.856 → 0.862 | 0.856 → 0.873 | = | = |

| item | before | after | what changed |
|---|---|---|---|
| andantino-piano-phone severe | 0.576 | **0.924** | dewarp (4 systems × 2 staves, 3–4 measures each) + flatten |
| agrace-satb-phone severe | 0.638 | **0.763** | flatten |
| twinkle-piano2p-phone severe | 0.891 | 0.900 | flatten |
| twinkle-piano2p-book severe | 0.942 | **0.993** | dewarp |
| L19 satb-closed-lyrics-both-staves-de severe | 0.545 | **0.635** (duration 0.298 → 0.613) | flatten |
| L11 hymn-descant-cue-notes-amen-small severe | 0.113 | 0.113 | not fixed |
| wind-melody-phone severe | 0.727 | 0.727 | flatten tried, no staves → plain reading kept |
| other phone / book items | | unchanged | |
| elsewhere: nocturne-cross-staff scan +0.219, song-one-system-poem-block severe +0.354, lyr07 severe +0.078, twinkle combo scan +0.069; coverage choir-piano-song-of-rejoicing severe +0.442, perf-hymn 150/200 dpi severe +0.26 / +0.22 | | | |

**L19 diagnosis**: it is a phone shot (dark surround, slight perspective, 12 px staff space). The page's binary had
lost the faint staff lines and stems (lines dashed, stems gone), so barlines went unfound and each system read as
one measure: duration 0.298. Flattening the paper first restores them (duration 0.613). Its dewarp reread was
rejected by the coherence check. Remaining: lyrics (OCR off here) and pitch 0.70.

**L11 diagnosis**: page and recipe: 100 dpi (from 300) binarised photocopy of a halftoned page, 2.5° skew. At 100 dpi
the staff space is ~6 px, and the 1-px staff lines survive only as dashes covering well under half their length.
No staff is found on either page, so nothing downstream (cue-size notes, the 14-pt Amen staff) is reached. Tried:
deskew + grey closing along rows with windows of 9–23 px (up to two spaces): the dashes do not join into lines
the staff finder accepts (still 0 staves). This needs a staff finder that accepts dashed collinear runs (a Hough /
RANSAC line fit over short runs at a common spacing), which is a change to `staves.js`, not a pre-clean; not done.

## Update: pre-clean moved to plain JS; OpenCV.js removed from the app

The five pre-clean repairs (below) were ported to plain JS (separable Gaussian, running max / min,
elliptical grey closing, area resize, bilinear resize, divide, all with OpenCV's border rules) and compared
with the OpenCV build on the same pages (`spike/opencv/probe/js-vs-cv.js`, `results/preclean-js-vs-opencv-*.txt`):

| page (plan) | OpenCV ms | JS ms | pixels, mean / max abs difference |
|---|---:|---:|---|
| andantino photocopy-thick scan (thin) | 19 | 219 | 0 / 0 |
| agrace photocopy-thin severe (close) | 10 | 85 | 0 / 0 |
| andantino blur severe (sharpen) | 194 | 313 | 0.44 / 2 |
| andantino halftone scan (descreen) | 56 | 153 | 0.03 / 1 |
| andantino combo severe (flatten) | 200 | 459 | 0.05 / 5 |
| andantino yellowed severe (flatten) | 133 | 381 | 0.06 / 3 |

End to end the JS port scores the same: challenge 0.8227 (OpenCV) → **0.8228** (JS), 8 of 365 items moved by
less than 0.015 either way; benchmark with OCR 0.9499 = 0.9499, real scans 0.9295 =. OpenCV is faster per repair
(by 0.1–0.26 s on a degraded page), but needs a 10.4 MB self-hosted file and ≈1.1 s (browser worker) / 0.17 s (node)
to load before the first repair, and a patched third-party build. It does not clearly beat plain JS on quality
or speed for a few degraded pages, so **the app now uses the JS port and no longer ships OpenCV.js** (the
`assets-src/opencv` folder, the dist asset and its build.js entry are removed; `spike/opencv/tools/patch-noeval.js`
keeps the CSP patch for the record). Clean pages are still returned untouched (same object).

## Update: plain-JS header reader (shipped, default on)

`mvp/src/cv.js` `readHeaders(fr, asm)` now runs on every page, called from `omr.js` `analyse()` right after
`assemblePage` (after the orientation clef count, so orientation still judges the plain reading). It is the
section 4 template reader in plain JS (Bravura templates, normalised correlation), with the OpenCV symbol paths,
the rest fallback and `wrapConverter` removed. Changes since the spike:
- matching stays inside the header: a few glyphs per staff, and the template only shifts ±0.35 staff space
  around the glyph's centre: **≈15–100 ms per page** (was 283 ms with a full search).
- the two numbers are cut at the middle line (they often touch once the line is removed), and the search for a
  missed time signature may start on the tail of the key signature (the first three ink groups are tried).
- when a missed time signature is found the header ends after it, so its digits are no longer taken for notes
  or accidentals, and the overlay's time-signature layer (`symbols.js` reads `hdr.time`) shows it. Maple Leaf Rag
  (benchmark page, 200 dpi): time signatures 1 → 2 (both 2/4 read), the false head on the treble digits dropped,
  no accidental boxed on the digits.

A/B (same src, pre-clean on in both arms; `spike/opencv/results/header-*.txt`):

| set | aggregate | first time signature right | items changed |
|---|---|---|---|
| challenge (no OCR, 365) | 0.8212 → **0.8227** (pitch +0.0031, duration +0.0029) | 342 → **352** | 63; one drop −0.023 (`andantino-piano-photocopy-thin` severe, meter became right) |
| benchmark with OCR (20) | 0.9496 → **0.9499**, real scans 0.9295 = | 19 = | 2, both up (`joplin-maple-leaf-piano` +0.001, `schumann-dichterliebe2` +0.005) |

## Update: pre-clean for degraded scans (shipped; first with OpenCV, now plain JS, see above)

Scope extension: OpenCV now runs as a **pre-clean stage before binarisation**, only on pages a cheap
quality check calls degraded. This supersedes the "do not add OpenCV.js" verdict below for this use; the
symbol-reader findings in sections 1–7 still hold.

**How it works** (`mvp/src/cv.js`, hook `mvp/src/front.js` `frontSteps`):
- `pageQuality(gray)` in plain JS (30–70 ms per page) measures: share of mid-grey pixels (`mid`), mid-grey share of inked
  pixels (`midShare`), lightest-1 % level (`p1`), paper darkness and unevenness from 32 px cells (`bgLow`,
  `bgUneven`), paper texture (`bgStd`), isolated specks per Mpx (`speck`), staff-line thickness / staff space (`ltss`).
- `precleanPlan(q)` picks repairs; an empty plan returns **the same gray object**, so clean pages are read exactly as
  before and OpenCV is never loaded for them (verified: the clean class and every unaffected item are unchanged).
- Otherwise OpenCV.js (patched 4.10.0, self-hosted `dist/assets/opencv-4.10.0-noeval.js`) is loaded **synchronously**
  (front() is synchronous): node reads the file; the recognition Web Worker uses a synchronous XHR + `blob:`
  `importScripts`, and the embedded wasm is compiled with `new WebAssembly.Module` through `instantiateWasm`
  (the patch makes the UMD wrapper read `globalThis.__opencvModuleArgs`). On a page's main thread (worker
  unavailable) the pre-clean is skipped. `OMR_PRECLEAN=off` disables it (node).

| repair | when (plan rule) | OpenCV ops |
|---|---|---|
| `thin` | binary page (`bgStd` < 0.5, `mid` < 0.03), `ltss` > 0.16 (thick photocopy) | `dilate` 3×3 (paper grows) × n, n = round((lt − 0.11·ss)/2) clamped 1–3 |
| `close` | binary page, 300 < `speck` < 2000 (thin photocopy broken into dots) | `erode` 2×2 (ink grows 1 px) |
| `descreen` | `speck` > 25000 and `bgStd` > 4 (halftone screen) | `GaussianBlur` σ = ss/14 |
| `flatten` | `mid` > 0.15 and (`bgUneven` < 0.4, `bgLow` > 0.12, `midShare` > 0.8 — yellowed/stained) or `bgStd` > 6.8 (combined damage) | 4× `resize`, `morphologyEx` CLOSE (ellipse 0.8·ss), `GaussianBlur`, `resize` back, gain capped at 2.5×, `divide` |
| `sharpen` | `midShare` > 0.94 and `p1` > 100 (heavy blur) | unsharp mask: `GaussianBlur` σ = ss/5, `addWeighted` 3, −2 |

**Per class, challenge degradation set** (aggregate, `eval.mjs --set challenge --no-ocr --jobs 8`, same src snapshot,
`OMR_PRECLEAN=off` vs on; `spike/opencv/results/preclean-perclass.txt`):

| class | ops used | all | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| photocopy-thick | thin | 0.681 → **0.816** | 0.756 → 0.868 | 0.831 → 0.888 | 0.456 → **0.691** |
| blur | sharpen (severe only) | 0.754 → **0.839** | = | = | 0.542 → **0.796** |
| combo | flatten (severe) | 0.804 → **0.855** | = | = | 0.669 → **0.823** |
| halftone | descreen | 0.813 → **0.855** | 0.842 → 0.873 | 0.786 → 0.854 | 0.811 → 0.839 |
| yellowed | flatten (severe) | 0.859 → 0.868 | = | = | 0.809 → 0.838 |
| photocopy-thin | close (severe) | 0.806 → 0.815 | = | = | 0.668 → 0.695 |
| clean, bleed, book, crop, highdpi, holes-staple, jpeg, lowdpi, noise, phone, rot90/180, scale, skew, spread, stain-pencil | none | unchanged | | | |

Whole challenge set: **0.8091 → 0.8212** (+0.0121; pitch +0.023, duration +0.023, rests +0.013); degradation
0.8493 → 0.8651, pitch category +0.007, lyrics +0.0045, rhythm +0.0043, layout and voices unchanged; scan-severe
0.7354 → 0.7623. Largest item drop −0.009 (`agrace-satb-photocopy-thick/scan-severe`), 46 items up.
Benchmark **with OCR**: **0.9480 → 0.9496**, real scans 0.9256 → **0.9295**, synthetic 0.9519 → 0.9531, no item down
(`golden1923-america` +0.012 flatten, `bach-bwv3-6` +0.011 flatten, `bach-bwv166-6` +0.010 thin).

Named limits: the severe photocopies improve (`andantino` thick severe 0.616 → 0.854, `wind-melody` thick severe
0.351 → 0.711, `agrace` thin severe 0.595 → 0.657; `agrace` thick severe stays at 0.25). **Not helped**: L11
`hymn-descant-cue-notes-amen-small` severe (0.113; its staff lines are broken into dashes — a 1×ss horizontal
closing was tried and did not help), L19 `satb-closed-lyrics-both-staves-de` severe (0.545) and phone shots
(`andantino-piano-phone` severe 0.576): flattening phone shots measured worse (class 0.824 → 0.771 even with the
gain cap), so phone pages are left alone; dewarping was not attempted.

What was tried and rejected (`results/preclean-trials.txt`, 12 items per class): 3×3 / 5×5 **median** destroys 1–2 px
staff lines (halftone 0.813 → 0.643, noise 0.869 → 0.473); **despeckle** (drop tiny components) erases the dotted staff
lines of thin photocopies (0.806 → 0.690); a second thinning pass ruins mild thick photocopies (mild 0.888 → 0.254),
hence the thickness-driven pass count; descreen on random noise is slightly worse (0.869 → 0.865); flatten without the
gain cap turns a photographed page's dark surround into texture (phone severe 0.708 → 0.448).

**Cost.** Asset: `opencv-4.10.0-noeval.js` 10,376,412 B (≈3.4 MB gzip), plus licence and notice (dist/assets total
49.9 MB of 64 MB). Node: quality check 30–70 ms per page; OpenCV load ≈170 ms once; repairs 40–240 ms per degraded page
(`results/preclean-timing.txt`). Headless Chromium, CSP blob worker (`spike/opencv/probe/browser-preclean.js`): the
first degraded page costs ≈1.1 s extra (sync fetch of 10 MB, wasm compile, then the repair); clean pages cost only the
quality check; results match node exactly (same plans, staves and heads).

## Recommendation (TL;DR)

1. **Do not add OpenCV.js as a dependency now.** The one approach that wins is **template matching against SMuFL glyphs** (approach a), and a plain-JS implementation of the same matcher produces **byte-identical output** on 671 eval items (challenge + coverage: 0 items changed). It needs no 10.4 MB asset, no CSP patch, and no wasm load. OpenCV.js only makes the matching faster: 38 ms per page against 283 ms in JS. In the browser it costs about 0.85 s to load, so it breaks even after 3–4 pages.
2. **Adopt template matching (approach a) for time-signature numbers and unread clefs.** The classical header finds numbered time signatures but **never reads their digits** (0 of 182 read on the coverage patches). Bravura digit templates read **99.8 %** of digits on scans and **90.9 %** on severe scans. End to end, with the fallback on, the first time signature is right in **+23 coverage items (246 → 269 of 306)** and **+8 challenge items (333 → 341 of 365)**, with no item moving away from the truth. Aggregate scores change by +0.0003 (coverage), +0.0004 (challenge) and 0 (benchmark). The eval metric does not score time signatures directly; the gain shows up in duration, rests and the coverage time tags (`time-6-8` 0 → 3 of 31 on scans, `time-4-4` severe 33 → 41 of 79). Reading unread clefs fixed one piano spread outright (+0.147 aggregate).
3. **Do not adopt approaches b (contour features + kNN) or c (HOG + linear SVM)** as fallbacks. On isolated glyphs they are no better than the classical readers where those exist (rests, accidentals, clefs). They cannot recognise classes missing from their training items (32nd and 64th rests: 0 % recall under an item-level split). They would also ship training vectors. For digits, HOG-kNN beats templates on severe scans (95.9 % against 90.9 %), but it is trained on this corpus's engraving font.
4. **Do not enable the rest fallback.** Template matching as a second opinion on glyphs `rests.js` leaves unclassified raised rests F1 on the benchmark (+0.030) and challenge (+0.006) but lowered it on coverage (−0.010; false rests on piano scores with pedal marks and fingering). The code is in `cv.js` behind `opts.rests`, and the hook is in `spike/opencv/hooks/rests-hook.patch`, not applied.
5. Prototype delivered: **`mvp/src/cv.js`**, default **off**, used like `ml.js` (`wrapConverter`). It has two interchangeable matchers: `createJsCv()` (recommended, no asset) and `createNodeCv()` / `createBrowserCv()` (OpenCV.js). `node mvp/tools/build.js` and `node mvp/tools/pw/test.js` both pass with it in the bundle. The eval harness switch is a ready patch: `spike/opencv/hooks/eval-cv.patch` adds `--cv js|opencv` to `mvp/tools/eval.mjs`. It applies cleanly and was tested on a temporary copy, but is not applied, because that file belongs to the harness owner.

## 1. Runtime feasibility

### 1.1 Builds, sizes, licence

| package (npm, jsDelivr) | published | `opencv.js` | gzip | wasm | licence |
|---|---|---:|---:|---|---|
| `@techstark/opencv-js@4.10.0-release.1` (pinned) | 2024-08-25 | 10,378,215 B | 3,389,608 B | inlined as base64 (`SINGLE_FILE=1`) | Apache-2.0 |
| `@techstark/opencv-js@4.11.0-release.1` | 2025-06-04 | 11,386,540 B | 3,870,043 B | inlined | Apache-2.0 |
| `@techstark/opencv-js@4.12.0-release.1` | 2025-11-08 | 10,872,779 B | – | inlined | Apache-2.0 |
| `@techstark/opencv-js@5.0.0-release.1` | 2026-06-24 | 13,298,869 B | – | inlined | Apache-2.0 |

A single file, under the 15 MB asset limit. cdnjs has no OpenCV.js package. The official build at docs.opencv.org is the same emscripten/embind build.

Modules compiled in (4.10.0 `getBuildInformation()`): `calib3d core dnn features2d flann imgproc js objdetect photo video`. **Disabled: `ml`** (so no `cv.ml_KNearest`, no `cv.ml_SVM`), `imgcodecs`, `highgui`. Also missing from the JS bindings: **`cv.HuMoments`** (I computed it from `cv.moments` nu values) and **`HOGDescriptor.compute`** (only `detectMultiScale` / `setSVMDetector` are bound; I computed HOG from `cv.Sobel` + `cv.cartToPolar`, with JS binning). `matchTemplate`, `moments`, `findContours`, `convexHull`, `connectedComponentsWithStats`, `resize`, `threshold`, `morphologyEx` and `distanceTransform` are present.

### 1.2 The artifact CSP blocks every published build

Loaded from the pinned jsDelivr URL under the app's CSP (`script-src` has `'wasm-unsafe-eval'` and `blob:`, but no `'unsafe-eval'` and no `'self'`), **all four builds fail to initialise**: *"Evaluating a string as JavaScript violates the following Content Security Policy directive … 'unsafe-eval'"*. Embind builds every binding invoker with `new Function(...)` (`craftInvokerFunction`, `createNamedFunction`, `makeDynCaller`, `__emval_get_method_caller`). 4.11+ removed `createNamedFunction`'s eval but still crafts invokers with `newFunc(Function, …)`.

Fix: `spike/opencv/tools/patch-noeval.js` rewrites those four generators as equivalent closures. This is the logic emscripten itself emits with `-s DYNAMIC_EXECUTION=0`. The patch makes exact-string replacements and fails loudly on any other build. The patched 4.10.0 file (10,376,402 B) cannot come from a CDN `<script>`. It must be **self-hosted and run from a `blob:` URL** (fetch from `'self'` via `connect-src`, then `<script src=blob:>` or `importScripts(blob:)` in the recognition worker). Inside a `blob:` worker, the asset base must be an absolute URL. On GitHub Pages (no CSP) the patched file loads directly.

Speed is unchanged by the patch (100 calls each, node): `moments` 5.9 ms vs 5.8 ms stock, `findContours` 6.0 vs 5.3, `matchTemplate` + `minMaxLoc` 14.3 vs 12.2.

### 1.3 Load time and memory

| where | load | memory | probe |
|---|---|---|---|
| node 24, stock package `require` | 235–274 ms | RSS +71–80 MB (+128 MB `external`) | `probe/load.js` |
| node 24, patched file | 140–182 ms | RSS +79–84 MB | `probe/micro.js`, `probe/timing.js` |
| headless Chromium 1208, page, patched via `blob:` script | 852–865 ms | JS heap 168.5 MB | `probe/browser.js` |
| headless Chromium, `blob:` Web Worker, `importScripts(blob:)` | 853–854 ms | (not observable in a worker) | `probe/browser.js` |
| headless Chromium, stock build from jsDelivr | **fails** (CSP eval) | | `probe/browser.js` |

One `matchTemplate` (TM_CCOEFF_NORMED) of a 40×40 template over a 2000×2800 page takes 211–224 ms in Chromium.

## 2. Ground truth for symbol-level measurement

The coverage corpus (`corpus/coverage`) is LilyPond-engraved, so exact glyph positions are available:

1. `spike/opencv/tools/svgtag.ly` is an include-settings file with a Scheme engraver. It sets `output-attributes` (a callback, read at output time) on every Rest, MultiMeasureRest, Accidental, Clef, TimeSignature, Script, DynamicText, Flag, Dots and NoteHead grob, so LilyPond's SVG backend wraps each one in `<g class=…>` with `data-*` detail (duration log, glyph name, fraction). `tools/svgboxes.py` turns the SVG paths into pixel boxes at 300 dpi. They align with `clean.pdf` (checked by ink inside and outside each box).
2. `tools/patches.js` runs the pipeline's own front end (`front()`, src snapshot) on `clean`, `scan` and `scan-severe`. Each truth box is carried onto the scan by its staff (staff index, fraction along the staff, offset from the middle line in staff spaces), which follows skew, scaling and mild warps. The patch is the union of the staff-removed page's (`fr.R`) components whose centres fall inside the box. This is exactly what a fallback sees at run time.
3. 70 items (rests, pitch, time, marks, notes and layouts families), 15,247 patches. Used after dropping flags, which are attached to stems and so are not glyph patches: 14,150 samples. Of these, 4,000 are other-component negatives, 3,500 noteheads and 529 other scripts. Rests: 1,195 (incl. 14 H-bars, 176 whole/bar rests). Accidentals: 467 (incl. 15 double flats and 18 double sharps). Clefs: 1,289 (incl. 119 C clefs). Time-signature digits: 1,548, plus 110 C / cut glyphs. Also 332 fermatas, 451 dynamics and 705 dots.
4. Evaluation uses a 2-fold, **item-level** split, so items never straddle train and test. Training uses all three variants of the train items; testing is per variant.

## 3. Isolated-glyph results (patch level)

### 3.1 The three approaches, family micro precision / recall (%), test folds

`a-template`: best normalised correlation against Bravura 1.392 templates (SIL OFL 1.1) scaled by the measured staff space (×0.85/1/1.15) with small shifts, `neg` below a threshold tuned on the train fold. `b-shape-knn`: Hu moments, aspect, size and staff position, fill, solidity, holes, components and 4×4 zoning; standardised 3-NN in JS. `c-hog-svm` / `c-hog-knn`: HOG (32×32, 8 px cells, 9 bins, L2-Hys) plus size and position; one-vs-rest linear SVM (Pegasos) or 3-NN in JS. `ac`: HOG plus the template scores as features.

**scan** (typical 200–300 dpi scan)

| approach | rests | accidentals | clefs | time digits + C | fermata | dynamics | dots | negatives |
|---|---|---|---|---|---|---|---|---|
| a-template | 33/83 | 99/83 | 100/96 | 97/99 | 100/99 | 91/69 | 0/0 | 89/67 |
| b-shape-knn | 82/81 | 94/88 | 97/100 | 97/99 | 100/99 | 93/96 | 80/85 | 94/92 |
| c-hog-svm | 95/73 | 99/71 | 100/98 | 98/90 | 99/96 | 99/94 | 80/84 | 82/94 |
| c-hog-knn | 84/83 | 93/88 | 100/100 | 97/99 | 100/99 | 98/95 | 84/86 | 94/94 |
| ac-hog+tpl-svm | 96/76 | 98/70 | 100/98 | 100/90 | 99/96 | 99/95 | 85/84 | 83/97 |

**scan-severe** (photocopies, phone photos, 100–150 dpi)

| approach | rests | accidentals | clefs | time digits + C | fermata | dynamics | dots | negatives |
|---|---|---|---|---|---|---|---|---|
| a-template | 31/86 | 94/72 | 100/71 | 91/87 | 98/77 | 76/53 | 0/0 | 83/74 |
| b-shape-knn | 66/77 | 68/80 | 94/95 | 87/88 | 94/95 | 93/92 | 63/71 | 94/87 |
| c-hog-svm | 95/51 | 86/64 | 99/89 | 98/66 | 99/88 | 98/81 | 64/52 | 75/96 |
| c-hog-knn | 81/81 | 76/79 | 97/95 | 94/90 | 100/95 | 94/95 | 68/71 | 92/93 |
| ac-hog+tpl-svm | 96/54 | 87/68 | 99/89 | 99/67 | 98/89 | 98/81 | 72/54 | 76/97 |

Cost per patch (features + prediction, node, OpenCV.js): template 10.3 ms (31 classes × 3 scales), shape-kNN 0.42 ms, HOG-SVM 0.41 ms, HOG-kNN 2.5 ms.

Per-class findings (`results/patch-classifiers.json`):
- **Templates are font-independent and precise.** The corpus is engraved in Emmentaler and the templates are Bravura, yet on scans: quarter to 64th rests 100 % precision (recall 91–100 %), sharps / flats / naturals 98–100 / 84–87, G / F / C clefs 100 / 92–100, digits 100 / 95–100, fermata 100 / 99. They fail where shape alone is ambiguous: whole and half rests are the same glyph (rest-whole precision 59 %, half recall 0), and the dot template loses to block-rest and notehead templates (dot recall 0). That is the low "rests" and "dots" precision in the tables.
- **Trained models cannot see unseen classes.** All 32nd and 64th rests sit in one fold, so b and c score 0 % on them, while the templates score 100 %.
- **Double accidentals:** HOG-kNN double flat 100/100 (n = 5), double sharp 100/71 (n = 7). The classical classifier never outputs them, but the counts are too small to act on.

### 3.2 Time-signature digits, given the time-signature box

| reader | clean | scan | scan-severe |
|---|---|---|---|
| templates only (no training) | 100.0 % (532) | **99.8 %** (532) | 90.9 % (484) |
| HOG-kNN (other fold) | 99.6 % | 99.4 % | **95.9 %** |
| combined (template unless kNN confident) | 100.0 % | 99.6 % | 93.4 % |

### 3.3 The classical readers on the same truth glyphs (`tools/classical.js`, `results/patch-classical.json`)

| family, P / R % | clean | scan | scan-severe |
|---|---|---|---|
| rests (`detectRests` over each staff, after `assemblePage`) | 93/94 | 96/90 | 80/67 |
| accidentals (`classifyAccidental` on every 1–4-space glyph; precision is low because non-accidentals are tried too, which the pipeline does not do) | 27/90 | 48/89 | 39/79 |
| clefs (staff header / clef change) | 100/98 | 100/98 (C clef 77 %) | 100/93 (C clef 68 %) |
| numbered time signatures: found / numbers read | 169 / 0 of 308 | 160 / 0 of 308 | 142 / 0 of 284 |

So on isolated glyphs the classical rest, accidental and clef readers are already as good as b and c (coverage's accidental recall of about 50 % end to end comes from association and detection, not classification). The **only family the pipeline cannot read at all is time-signature numbers**. Unread C clefs and the severe-scan rest recall are the next gaps.

## 4. Prototype: `mvp/src/cv.js`

- **When it runs:** after `createConverter().addPage` (the same pattern as `ml.wrapConverter`), only where the classical reading is missing:
  1. A numbered time signature the header found (`hdr.time` with no `beats`) on the **first system of a page**: each row (lines 1–3 and 3–5) is read as one digit, or as two digits split at a gap, whichever matches better. Accepted only if every digit scores ≥ 0.45 and beats every rest, accidental and notehead template; beats 2–16, beat type 1–32.
  2. No time signature found: two stacked digits right after the clef / key (score ≥ 0.55). The signature is set and "heads" found on it are dropped.
  3. `hdr.clefGuessed`: the tall glyph at the staff start is matched against G / F / C (≥ 0.45, margin 0.05); a C clef takes its line from its centre. A bass clef over a treble clef in a two-staff system is rejected, as in `assemblePage`.
  4. `opts.rests` (off; needs the `rests.js` hook): quarter to 64th rest templates for glyphs `detectRests` left unclassified.
- **Why only the first system:** later systems carry meter changes, which `score.js` does not model (one meter per piece). An early version read every staff and made pieces starting in 3/4 come out in 6/8 (`time/t04-pickup-song`).
- **Matchers:** `createJsCv()` (plain JS: area resize, threshold, TM_CCOEFF_NORMED by direct correlation with integral-image window sums). `createNodeCv()` (`OPENCV_JS=path`, else `mvp/assets-src/opencv/…` or `spike/opencv/vendor/…`). `createBrowserCv({ base })` (fetch the patched file, then `blob:`, then `importScripts` / `<script>`). Templates: 27 Bravura glyphs at 24 px per staff space, 1 bit per pixel, 12 KB inline. Scores agree to a mean of 0.0001 (max 0.012) and the argmax agrees on 565 of 566 sampled patches (`probe/parity.js`).
- **Browser check** (`probe/browser-cv.js`, src bundled like `build.js`, blob worker, artifact CSP): both matchers read 6/8 on `time/t02-compound-irregular` scan, the same as node. Matching time: 51 ms (OpenCV) vs 272 ms (JS); total with the first-page load: 2.1 s vs 1.6 s.
- **Not done:** no UI toggle (that is the UI owner's file). Today the option is reached by calling `wrapConverter` in node, the worker or tests. The patched OpenCV file is not copied into `dist/assets` (10.4 MB for an option that is off, and the recommended matcher does not need it).

## 5. End-to-end A/B (same src snapshot, fallback off vs on)

The snapshot of `mvp/src` (md5 of the concatenated files: `7385b7ac…`) was copied to `spike/opencv/src-ab`. The only addition is `cv.js` plus an env switch in the copy's `omr.js`. The eval is `mvp/tools/eval.mjs --no-ocr --jobs 16 --src …` (OCR off in both arms: the fallback does not touch lyrics). Full output: `results/ab-eval.txt`.

| set (n) | aggregate | pitch | duration | rests | first time signature right | items changed | runtime per item |
|---|---|---|---|---|---|---|---|
| benchmark (20) | 0.8042 → 0.8042 | = | = | = | 19 → 19 | 0 | +235 ms |
| challenge (365) | 0.8091 → **0.8095** | +0.0009 | +0.0007 | = | **333 → 341** | 9 | +256 ms |
| coverage (306) | 0.7766 → **0.7769** | +0.0003 | +0.0012 | **+0.0103** | **246 → 269** | 23 | +467 ms |

- Every time-signature change moved to the truth: 6/8 ×14, 4/4 ×13, 3/2 ×2, 2/4 ×1, 3/8 ×1. A few items lose a little aggregate even though the meter became right (`rests/rst04` severe −0.042 at 3/8, `notes/nt04-beams` clean −0.023 at 2/4); rhythm repair in `score.js` fits the bars differently under the true meter.
- Largest gains: `challenge degradation/twinkle-piano2p-spread/scan-severe` +0.147 (clefs read on staves the header had guessed), `coverage notes/nt03-chords/clean` +0.048, `perf/perf-pages-05` +0.013 to +0.022.
- Coverage matrix (`tools/coverage.mjs` on both reports; `results/coverage-matrix-{off,on}.json`): `time-6-8` 0 → 2 / 3 / 1 of 31 (clean / scan / severe), `time-4-4` 43 → 45 clean and 33 → 41 severe, `time-3-2` 0 → 1, `time-2-4` 3 → 4 clean, `x-time-3-8` 0 → 1. Note values gain slightly from the right bar length (`note-8th` +41 to +45 hits per variant).
- The runtime increase in node is mostly loading OpenCV.js in each eval child process (about 0.18 s). Measured directly over 30 pages: the fallback's matching takes **38 ms per page with OpenCV and 283 ms with the JS matcher**, against a 1.2 s conversion. The JS matcher's end-to-end eval output is **identical** to the OpenCV one (challenge 0/365, coverage 0/306 items changed).

Rest fallback (`src-ab2`, fallback on, rests hook off vs on):

| set | aggregate | rests F1 |
|---|---|---|
| benchmark | 0.8042 → 0.8044 | 0.8015 → 0.8311 |
| challenge | 0.8095 → 0.8097 | 0.7587 → 0.7645 |
| coverage | 0.7769 → 0.7764 | 0.6249 → 0.6147 |

The rest fallback loses on coverage: piano pages (`perf-piano-*`, `marks/mk04` pedal and fingering) gain false rests. Not recommended without position and context checks.

## 6. What OpenCV.js would and would not buy

- **Would:** about 7× faster template matching (38 vs 283 ms per page here). That matters only for full-page or multi-scale detection, such as searching whole staves for missed rests or fermatas; per-glyph second opinions do not need it.
- **Would not:** any accuracy. The OpenCV build ships no `ml` module and no HOG `compute`, and its contour and moment functions are a few lines of JS each. The recommendation in `docs/research-omr.md` §7.2 (plain typed-array JS) still holds. The new information is that the CDN builds do not run under the artifact CSP at all without the no-eval patch.
- **Costs:** 10.4 MB self-hosted asset (3.4 MB gzip), about 0.85 s load and about 170 MB heap in the browser, a patched third-party file to maintain, and `Mat.delete()` memory management.

## 7. Next steps (owners)

1. Harness owner: apply `spike/opencv/hooks/eval-cv.patch` (`--cv js|opencv`), so `mvp/src/cv.js` can be measured without the spike copy.
2. UI / session owner: an opt-in "Read time signatures from templates" setting calling `cv.wrapConverter(conv, cv.createJsCv())` in the recognition worker. With +0.3 s per page and no regressions in the first-time-signature check, it is a candidate to turn on by default after review.
3. Score owner: meter changes (`time-change`, 110 occurrences) are now the limit. `cv.js` can read every staff's numbers once `score.js` models more than one meter per piece.
4. Rests owner: if the rest fallback is wanted, it needs context rules (no fingering or pedal zones, voice position) before `spike/opencv/hooks/rests-hook.patch` is applied.

## Files

- `mvp/src/cv.js`: the prototype (default off; not called by any existing code path).
- `spike/opencv/tools/`: `patch-noeval.js` (CSP patch), `svgtag.ly` + `svgboxes.py` + `mkboxes.sh` (LilyPond truth boxes), `templates.js` (Bravura templates via Chromium), `patches.js` (glyph patches), `samples.js`, `features.js`, `classifiers.js`, `exp.js`, `digits-exp.js` (patch experiments), `classical.js` + `classical-report.js` (classical baseline), `ab.sh`, `ab-rests.sh`, `abcmp.js` (end-to-end A/B), `cvload.js`.
- `spike/opencv/probe/`: `load.js`, `hog.js`, `micro.js`, `browser.js` (CSP / load probes), `browser-cv.js` (prototype in a CSP blob worker), `parity.js` (OpenCV vs JS matcher), `timing.js`, `one.js`, `smoke-mvp.js`, debug probes.
- `spike/opencv/hooks/`: `eval-cv.patch`, `rests-hook.patch` (not applied).
- `spike/opencv/results/`: `ab-eval.txt`, `patch-classifiers.json`, `patch-classical.json`, `coverage-matrix-off.json`, `coverage-matrix-on.json`.
- `spike/opencv/fonts/LICENSE.txt`: Bravura's OFL 1.1 licence (the font files themselves are ignored).

## Licences

- OpenCV.js 4.10.0 (`@techstark/opencv-js` 4.10.0-release.1): **Apache-2.0**. The no-eval patch is a modification and must be stated in a NOTICE if the file is ever shipped.
- Bravura 1.392 (Steinberg Media Technologies): **SIL OFL 1.1**. `cv.js` embeds bitmaps rendered from 27 of its glyphs, credited in the file header.
- LilyPond 2.24 (GPL) is used offline only, to make truth boxes; nothing from it ships.

## Reproduce

```
cd spike/opencv
npm install                                                    # @techstark/opencv-js 4.10.0-release.1
node tools/patch-noeval.js node_modules/@techstark/opencv-js/dist/opencv.js vendor/opencv-4.10.0-noeval.js
for f in redist/woff/Bravura.woff2 LICENSE.txt; do curl -sfL -o fonts/$(basename $f) https://cdn.jsdelivr.net/gh/steinbergmedia/bravura@bravura-1.392/$f; done
node tools/templates.js 24                                     # data/templates.json
tools/mkboxes.sh                                               # data/boxes (LilyPond SVG truth)
ls data/boxes | sed 's/.json$//' | xargs -P 6 -I{} node tools/patches.js {}
node tools/exp.js --feat && node tools/digits-exp.js           # section 3
ls data/patches/*.jsonl | xargs -n1 basename | sed 's/.jsonl$//' | xargs -P 5 -I{} node tools/classical.js {}; node tools/classical-report.js
cp -r ../../mvp/src src-ab && cp ../../mvp/src/cv.js src-ab/   # then the OMR_CV_FALLBACK switch in src-ab/omr.js convert()
tools/ab.sh; node tools/abcmp.js data/eval/ab-coverage-cv0.json data/eval/ab-coverage-cv1.json
```
