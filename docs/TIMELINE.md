# Build timeline

All times are Sydney daylight time (AEDT, UTC+11) on 2026-11-08. Generated from the status page on every push; last updated 2026-11-08 17:04 AEDT.

## Events

| Time | Event |
|---|---|
| 14:47 | Environment checked. LilyPond 2.24 installed to make test scans. |
| 14:52 | First workflow started, built around born-digital vector PDFs. |
| 14:56 | Restarted with scanned (image) PDFs as the main input. |
| 14:58 | Restarted again with more agents in parallel: 7 research, 3 design, 9 build, 5 per improvement round, 6 review, 7 fix. |
| 15:12 | Web research on OMR methods finished: docs/research-omr.md. |
| 15:16 | Web research on voice and part splitting finished: docs/research-voices.md. |
| 15:19 | Asked to deliver as soon as possible. Fast-track first version started. Main workflow will restart from its research results with a single design step and at most 2 improvement rounds. |
| 15:20 | Software design document started; it will appear on this page. |
| 15:21 | Research section added: one entry per research item with findings and decisions. |
| 15:21 | Agent record added: every agent from all runs, generated from the workflow journals, with timings, tool-call counts and full outcomes. |
| 15:22 | Software design document finished (docs/SDD.md, 14 sections) and added to this page. |
| 15:30 | First version (v1) finished and published as its own artifact: https://pension-plan.github.io/score-scan-reader/app/. Sample converts in 6–9 s with lyrics; verified in headless Chromium under the artifact CSP. |
| 15:33 | Generic UI mock-up drawn in Excalidraw and added to this page (redrawn with rough.js from the same scene). Three component patterns pulled from 21st.dev (dropzone, stepper, code block) and written to docs/ui-refs/ for the UI builder. |
| 15:37 | Switched to fail fast, fix forward: the planned full rebuild is dropped. Fix-forward round 1 started on the live v1 (harness, then 5 parallel owners, then integrate and ship). The main workflow keeps running only until its research returns, then stops; its findings feed later rounds. |
| 15:38 | Known-limits tracker added. Every v1 limit now has an owner; from round 2 the integrator must report each one as resolved, partial or open with evidence. Unassigned limits (tuplets, clef/key changes, part names, page cap, stanza text) added to the round script. |
| 15:42 | Synthetic test set finished: 17 scored items, 20 pages, 293 measures, all checks passed. It is the benchmark for fix-forward rounds. |
| 15:50 | Plain-JS image trial finished: geometry near perfect, noteheads F1 98.5 on synthetic scans, but about 65–70% recall on real 1906 engraving. Its fixes feed round 2 (limit L1). |
| 15:51 | Round 1 baseline measured on 19 scored items (17 synthetic, 2 real): aggregate 0.589, pitch 0.49, duration 0.54, lyrics 0.44, parts 0.73, schema-valid 19/19, no crashes. Four new problems added to the tracker (L6–L9), the most serious being piano split into SATB. |
| 15:55 | Challenge test set started: 6 parallel generators (voices and parts, rhythm, pitch and notation, lyrics, layout and structure, scan damage extremes), then validation and a baseline score. Kept in corpus/challenge/ so the 19-item benchmark stays comparable across rounds. |
| 15:58 | Real-scan test set finished: 8 public-domain scans, 3 hand-transcribed (America, St. Anselm, a Schumann piano piece). The benchmark grows to 20 items. |
| 15:59 | Lyric OCR trial finished: lyric lines found 100% of the time, about 1.5% character error. Round 2 will switch to tesseract best_int eng/deu/lat models and port the line detector. |
| 16:02 | Round 1 UI owner finished: wireframe layout with the three 21st.dev patterns ported (drag-depth dropzone, accessible 7-step stepper driven by real progress, line-numbered MusicXML block with Copy). Passes 33 of 33 UI checks under the artifact CSP, up from 14. The build now refuses to write a page that breaks artifact rules. Interim score with other owners’ in-progress changes: 0.664, up from 0.589. Not shipped yet; the integrator verifies first. |
| 16:05 | Code published to GitHub: pension-plan/score-scan-reader (private), 573 files: app, harness, corpora (test-only Bach items excluded), design docs, status page, orchestration scripts, CI and release-please workflows. Every update from now on is committed and pushed. |
| 16:10 | Challenge set, lyrics: 8 items (Latin melismas, 6 German stanzas, French refrain and elisions, Latin + italic English, Welsh SATB with four separate lyric lines, hymnal text block, Italian triple elisions, Scandinavian multilingual), each with mild, standard and severe scans. All truths verified syllable by syllable against the engraving. |
| 16:10 | GitHub Pages live: app, status page and all docs now deploy from the repo on every push (pension-plan.github.io/score-scan-reader). Repo made public, which free-plan Pages requires. |
| 16:11 | Round 1 lyrics owner finished: lyric OCR syllable F 0.71 → 0.88; benchmark lyrics 0.71 → 0.81. Interim aggregate with all round-1 changes so far: 0.862 (baseline 0.589). Not yet integrated or shipped. |
| 16:12 | Round 1 voices owner finished: correct part count on 20 of 20 items (was 13), piano never split, rhythm repaired per measure instead of padding with rests (over-full voice-measures 259 → 0), printed rests detected. Interim aggregate 0.877. L6, L7 and L9 resolved. |
| 16:12 | Challenge set, rhythm: 8 items (tuplet etude, ties and double dots across system and page breaks, meter changes on piano, a rest zoo with multi-bar rests, grace notes and fermatas, closed SATB cross-rhythms and more), each with mild, standard and severe scans. |
| 16:12 | GitHub Pages first deploy succeeded; CI green on main. |
| 16:12 | Challenge set, scan damage: 85 items from 4 pieces (Amazing Grace SATB, a melody with 2 verses, two piano pieces that must not split) × 21 damage types, each mild/standard/severe: skew up to 10°, 90° and 180° pages (mixed orientation across pages), phone photo, book curl, yellowed paper, bleed-through, stains and pencil, punch holes and staple, cropped staff ends, halftone moiré, JPEG 15, thin and thick photocopy, 100–600 dpi, blur, noise, 2-up spreads, page scale mismatch, and everything combined. 336 image-only PDFs. |
| 16:12 | Challenge set, pitch and notation: 8 items (key-signature odyssey through 7 sharps and 7 flats, clef carousel with alto and tenor clefs changing mid-bar, accidental storm with double sharps and courtesy signs, extreme ledger lines and 8va/8vb across line breaks, chromatic closed SATB, enharmonic TTBB, a 2-page song with a key change at the page turn), each with mild, standard and severe scans. |
| 16:16 | Round 1 symbols owner finished: key signatures now right on every synthetic item (most read 0 before), treble-8vb clef recognised, accidentals judged on their own pixels. Pitch 0.74 → 0.86 on the same code snapshot. Interim aggregate 0.882. |
| 16:17 | Round 1 noteheads owner finished: missed quarter notes 609 → 250, false notes cut by two thirds, faint staff lines now detected (Haupt 1867: 1 → 6 staves). Pitch 0.65 → 0.86 on its own. All five round-1 owners done; the integrator is now measuring, reverting regressions and preparing the ship. |
| 16:18 | Challenge set, layout and structure: 7 items (12-page piano variations with repeats and endings, SATB anthem in closed score over piano with D.S. al Coda, 3-staff organ chorale scanned sideways, cross-staff piano nocturne, hymn with a small descant staff and a small Amen, piano trio reduction with bracket vs brace, and more), each with mild, standard and severe scans. |
| 16:19 | Challenge set, voices and parts: 7 items (closed SATB with voice crossing and every kind of unison, German labels with lyric lines that switch voice mid-line, SAB with the alto crossing to the bass staff, and more), each with mild, standard and severe scans. All six generators done (about 123 items); the validator is now checking every item and scoring the app against them. |
| 16:21 | Round 1 shipped: aggregate 0.589 → 0.884, real scans 0.618 → 0.865, 0 crashes, all 20 outputs schema-valid, browser check passed at 1280 and 400 px in light and dark. Nothing reverted: removing any owner’s change lowered the score. App republished and pushed (GitHub Pages redeploys). |
| 16:21 | Round 2 started: 5 owners in parallel working on beamed 8ths/16ths and dense chords, broken bass-staff clefs, tuplets and mid-staff clef changes, missing dots and flags, barline reconciliation, lyric voice assignment, merged OCR words, part-name labels, the 8-page cap and the stanza verses below the music; then integrate and ship. |
| 16:28 | All times on this page and in the repo timeline are now Sydney daylight time (AEDT, UTC+11). |
| 16:28 | Challenge set validated: 123 items, 365 image-only scans, all truths verified against LilyPond. Baseline with round 1 code: 0.747 (OCR), 0 crashes, but 35 files produce no notes. Worst: 90° pages, halftone screens, heavy noise, 2-up spreads, tuplets (8 divisions per quarter cannot represent them), double dots, multi-bar rests, double accidentals, 8va, mid-piece key/time changes, C clefs, two voices inside one part, bracketed instrument pairs read as piano. Nine new limits (L10–L18) queued for round 3. Committed to the repo except the 300 MB of scan-damage PDFs, which rebuild in about 40 s. |
| 16:30 | ML model trial finished: copista-2m (Apache-2.0, 2 MB ONNX) scores notehead F1 0.996 and voice-slot 0.991 on the trial scans and runs in the browser under artifact rules at about 4–5 s per page. All 7 research items are now done; the old main workflow was stopped as planned. Round 3 will add the model as a second detector and ship it only if it scores better. |
| 16:38 | Release 0.2.0 published on GitHub (round 1 code) with downloads: web app zip, source zip, design document. Release PRs will be merged after each round ships. |
| 16:38 | copista-2m ML demo page started, for GitHub Pages at /ml-demo/. |
| 16:42 | copista-2m ML demo published on GitHub Pages: https://pension-plan.github.io/score-scan-reader/ml-demo/ — runs the model in your browser on a sample hymn (124 noteheads split exactly S/A and T/B on the sample) or your own scan. Live check passed: 203 symbols in 7.0 s, no errors. On a real 1905 scan the model’s voice slots fail (208 of 213 in one slot), so the app keeps its own voice logic. |
| 16:42 | Round 2 lyrics owner finished: words spanning several notes split into syllables, the trial’s line detector ported, part-name labels and stanza text now read. Lyrics 0.82 → 0.86 on its own; live tree with other owners’ work so far: aggregate 0.914, real scans 0.893. |
| 16:45 | Round 2 UI owner finished: L5a resolved. Reads up to 40 pages (was 8), one page at a time with progress, a page strip and a Stop button; recognition moved to a Web Worker (main-thread freeze on an 8-page PDF 23.2 s → 2.2 s, memory 310 MB → 50 MB). 35 of 35 UI checks pass. |
| 17:00 | Round 2 voices owner finished: lyric lines assigned to the right voice for the whole piece, melisma extenders written, printed part names read and applied (they also steer splitting), stanza text kept as MusicXML lyrics credits. Live tree: aggregate 0.918, real scans 0.900; challenge set 0.878 → 0.903. L3e, L4a, L4b resolved. |
| 17:04 | Release 0.3.0 published at 17:02 AEDT (round 2 so far), shipped first and then regression-tested against 0.2.0. Benchmark with OCR 0.897 → 0.918, real scans 0.870 → 0.900, no item worse. Challenge set 0.689 → 0.784 (93 items better), but 4 items dropped by more than 0.05: tracked as L19 for round 3. |
| 17:04 | Policy from now on: ship first, then test for regressions. CI runs tools/regress.mjs against the last release on every push; /app/ now shows a changelog panel and which engine it runs. |

## Accuracy by round

Scores are against the benchmark of synthetic and real scans with exact answers (1.00 is perfect).

| Run | Overall | Pitch | Duration | Lyrics | Parts | Schema-valid | Real scans |
|---|---|---|---|---|---|---|---|
| v1 baseline | 0.589 | 0.493 | 0.542 | 0.439 | 0.727 | 1.000 | 0.618 |
| Round 1 (shipped) | 0.884 | 0.863 | 0.822 | 0.817 | 0.987 | 1.000 | 0.865 |
| Challenge set baseline (round 1 code, OCR) | 0.747 | – | – | – | – | – | – |
| Round 2 (interim) | 0.918 | – | – | 0.911 | – | 1.000 | 0.900 |
| v0.3.0 released (benchmark, OCR) | 0.918 | 0.891 | 0.851 | 0.911 | 0.992 | 1.000 | 0.900 |

## Known limits

| ID | Limit | Owner | Status | Evidence |
|---|---|---|---|---|
| L1 | Hollow noteheads sometimes missed (main source of rhythm errors) | Noteheads and staves | Partial (round 1) | Hollow heads: wider insides filled, broken outlines closed, outline eaten by staff removal restored. Missed half notes 81 → 28, false whole notes 156 → 3. On the faint 1867 Haupt scan heads found 54 → 105. Beamed 8ths/16ths are now the largest miss source (598) — round 2. |
| L2 | Key signatures unreliable on old engraving | Symbols | Resolved on synthetic, partial on real (round 1) | Header read left to right (clef, key, time); accidentals checked against where each sharp or flat should sit for the clef. Correct on every synthetic item; America 1 sharp and St. Anselm 4 sharps correct. Some broken bass staves on St. Anselm still guess the clef. |
| L3a | Rests not detected | Symbols | Partial (round 1) | Printed rests now detected (whole, half, quarter, eighth) and placed; rests F1 0.14 → 0.41. Over-full voice-measures 259 → 0. |
| L3b | Ties and slurs not detected; a stray slur can create a false 16th | Symbols | In progress (round 1) |  |
| L3c | Triplets and other tuplets not detected | Symbols | Queued for round 2 |  |
| L3d | Mid-piece clef and key changes not detected | Symbols | Partial (round 1) | Treble-8vb clef detected; broken clefs re-joined; two treble clefs in a piano system kept as read. Per-system clef changes are read but not yet applied by score.js (round 2). |
| L3e | Part names not read from the labels at the start of each system | Lyrics (OCR) + voices (apply) | Resolved (round 2) | Part-name labels read by OCR and parsed against a multilingual lexicon (Sopran, Canto, Pianoforte, Tenor II…); labels also steer the layout. SAB item 4 → 3 parts. |
| L4a | Lyric alignment drifts when the note count is off | Voices + lyrics | Resolved (round 2) | Each lyric line is assigned to one voice for the whole piece from syllable-to-onset evidence; alignment allows left-aligned melisma syllables and never uses rests. bwv3-6 +0.135, Beach +0.271 lyrics. |
| L4b | No melisma or extender handling | Lyrics + voices | Resolved (round 2) | Words over several notes split into syllables (lyrics owner); melismas now carry <extend> start/stop bounded by the printed extender line; 189 extenders in the benchmark output, all schema-valid. |
| L5a | At most 8 PDF pages processed | UI | Resolved (round 2) | Up to 40 PDF pages, read one at a time with per-page progress and a Stop button; recognition runs in a Web Worker. 8-page PDF: main thread blocked 23.2 s → 2.2 s, wall time 44.5 s → 27.1 s, memory 310 MB → 50 MB; 40 of 40 pages in 138 s. |
| L5b | Stanza text printed below the last system dropped for SATB | Lyrics + voices | Partial (round 2) | Stanza text below the music is read and written as MusicXML lyrics credits, matching the truth files (lyr06 verses 4–6). Setting it under the notes is not attempted. |
| L6 | Piano wrongly split: grand staves become S/A/T/B, voice+piano gets 4 parts instead of 2 (breaks the never-split-piano rule) | Voices (score.js) | Resolved (round 1) | All 20 benchmark items now get the right part count (was 13 of 20). Piano grand staves are recognised by barlines running through both staves and are never split; Bach bwv67, Clara Schumann, Lindenbaum, Dichterliebe, Beach and Aloha fixed. |
| L7 | Lyrics attached to every part in closed score (3–4× too many syllables) | Voices + lyrics | Resolved (round 1) | Lyrics between staves go to the upper voice only; lines under the lowest split staff go to both its voices; copying to every voice is opt-in. Lyrics 0.60 → 0.82. |
| L8 | Lyric text or other glyphs read as noteheads on single-melody pages | Noteheads and staves | Resolved (round 1) | A notehead outside the staff must sit on or next to ledger lines, which removes lyric letters, tuplet numbers and dynamics. Jeanie 0.48 → 0.88, Silent Night 0.56 → 0.96. |
| L9 | Part names generic or wrong (open score shows Staff N; TTBB named SATB, with an octave error) | Voices + lyrics | Resolved (round 1) | Part names from the clef pattern: SATB, TTBB (new treble-8vb clef), SSAA, SAB, solo above SATB, Voice. Reading printed name labels is still tracked under L3e. |
| L10 | Pages rotated 90° produce nothing; 180° pages read badly (pitch 0.21) | Noteheads and staves (page orientation) | Queued for round 3 | Challenge baseline: rot90 0.15 (all 12 files empty), rot180 0.50. |
| L11 | Halftone screens and heavy noise blank the page | Noteheads and staves (binarisation) | Queued for round 3 | Challenge: halftone 0.37 (6 of 12 empty), noise 0.50; 35 of 365 files produce no notes. |
| L12 | Two-page spreads read as one wide system (8–13 parts) | Noteheads and staves (page split) | Queued for round 3 | Challenge: 2-up spread 0.56. |
| L13 | Tuplets cannot be represented: 8 divisions per quarter | Symbols + voices + MusicXML | Queued for round 3 | Challenge: 0.2% of 461 tuplet notes have the right duration. Needs divisions 24+ and tuplet markup. |
| L14 | Double dots, multi-bar rests and whole-bar rests | Symbols + voices | Queued for round 3 | Challenge: double-dotted 0%; rh04 26 bars instead of 40; whole-bar rests 17%. |
| L15 | Double sharps/flats and 8va/8vb brackets | Symbols | Queued for round 3 | Challenge: double accidentals 1 of 9 pitches; 9% under 8va. |
| L16 | Key and time-signature changes mid-piece not written; C clefs (alto/tenor) | Symbols + voices | Queued for round 3 | Challenge: later keys 31%, time changes 35%, C clefs 29%. (Overlaps L3d.) |
| L17 | Two voices inside one part (piano right hand, divisi) merged into chords | Voices + MusicXML | Queued for round 3 | Challenge: always merged in 9 pieces. |
| L18 | A bracketed instrument pair (violin + cello) read as a piano grand staff; organ pedal staff becomes a separate part | Voices (layout) | Queued for round 3 | Challenge: trio and clef-carousel read as Piano; organ comes out Piano + Voice. |
| L19 | Regressions found after shipping 0.3.0: 4 challenge items dropped > 0.05 vs 0.2.0 (wind-melody thick-photocopy severe −0.067, satb-closed-lyrics-both-staves-de severe −0.061, lyr08 Scandinavian −0.056, hymn-descant mild −0.050) | Round 3 owners (heads, lyrics, score) | Queued for round 3 | docs/regressions/v0.3.0-vs-v0.2.0.md |

## Runs

| Run | What | Status | Agents returned | Note |
|---|---|---|---|---|
| Run 1 | Vector-PDF design | stopped | 0 of 4 | Stopped at 14:56 AEDT when the input was clarified as scanned images. |
| Run 2 | Scanned-PDF design | stopped | 0 of 4 | Stopped at 14:58 AEDT to restart with more agents in parallel. |
| Run 4 | Fix-forward round 1 (shipped 0.884) | done | 7 of 7 |  |
| Run 5 | Challenge test set (edge cases + scan damage) | running | 7 of 7 |  |
| Run 6 | Fix-forward round 2 | running | 3 of 5 |  |
| Run 3 | Max-parallel main workflow (research) | stopped | 7 of 10 | Stopped at 16:30 AEDT once all 7 research items returned, as planned; its 3 design-proposal agents had just started and were stopped with it. The full rebuild was replaced by fix-forward rounds on v1. |
| Side | Agents launched directly from the session | running | 3 of 3 |  |

## Agents

Every agent started for this build, including stopped runs. Outcomes are on the status page.

| Run | Phase | Agent | Status | Started | Finished | Minutes | Tool calls |
|---|---|---|---|---|---|---|---|
| Run 1 | Research | research:omr | stopped | 14:52 | 14:55 | 3 | 35 |
| Run 1 | Research | research:voices | stopped | 14:52 | 14:55 | 3 | 55 |
| Run 1 | Research | research:pdfjs-probe | stopped | 14:52 | 14:55 | 3 | 14 |
| Run 1 | Research | research:corpus | stopped | 14:52 | 14:55 | 3 | 10 |
| Run 2 | Research | research:omr | stopped | 14:57 | 14:57 | 0 | 6 |
| Run 2 | Research | research:voices | stopped | 14:57 | 14:57 | 0 | 6 |
| Run 2 | Research | research:spike | stopped | 14:57 | 14:57 | 0 | 3 |
| Run 2 | Research | research:corpus | stopped | 14:57 | 14:57 | 0 | 0 |
| Run 4 | Harness | harness | done | 15:36 | 15:51 | 15 | 22 |
| Run 4 | Fix | fix:r1:heads | done | 15:51 | 16:16 | 25 | 185 |
| Run 4 | Fix | fix:r1:symbols | done | 15:51 | 16:16 | 25 | 173 |
| Run 4 | Fix | fix:r1:score | done | 15:51 | 16:11 | 20 | 130 |
| Run 4 | Fix | fix:r1:lyrics | done | 15:51 | 16:11 | 20 | 129 |
| Run 4 | Fix | fix:r1:ui | done | 15:51 | 16:01 | 10 | 47 |
| Run 4 | Integrate | integrate:r1 | done | 16:16 | 16:21 | 5 | 45 |
| Run 5 | Generate | gen:voices | done | 15:55 | 16:18 | 23 | 128 |
| Run 5 | Generate | gen:rhythm | done | 15:55 | 16:11 | 16 | 97 |
| Run 5 | Generate | gen:pitch | done | 15:55 | 16:12 | 17 | 82 |
| Run 5 | Generate | gen:lyrics | done | 15:55 | 16:10 | 15 | 83 |
| Run 5 | Generate | gen:layout | done | 15:55 | 16:18 | 23 | 120 |
| Run 5 | Generate | gen:degradation | done | 15:55 | 16:12 | 17 | 87 |
| Run 5 | Validate | validate+baseline | done | 16:18 | 16:28 | 10 | 70 |
| Run 6 | Fix | fix:r2:heads | run | 16:21 |  | 43 | 241 |
| Run 6 | Fix | fix:r2:symbols | run | 16:21 |  | 43 | 202 |
| Run 6 | Fix | fix:r2:score | done | 16:21 | 17:00 | 39 | 170 |
| Run 6 | Fix | fix:r2:lyrics | done | 16:21 | 16:41 | 20 | 109 |
| Run 6 | Fix | fix:r2:ui | done | 16:21 | 16:45 | 24 | 87 |
| Run 3 | Research | web:omr | done | 14:58 | 15:11 | 13 | 77 |
| Run 3 | Research | web:voices | done | 14:58 | 15:15 | 17 | 120 |
| Run 3 | Research | spike:ml | done | 14:58 | 16:30 | 92 | 193 |
| Run 3 | Research | spike:classical | done | 14:58 | 15:50 | 52 | 120 |
| Run 3 | Research | spike:ocr | done | 14:58 | 15:58 | 60 | 129 |
| Run 3 | Research | corpus:synthetic | done | 14:58 | 15:42 | 44 | 82 |
| Run 3 | Research | corpus:real | done | 14:58 | 15:57 | 59 | 189 |
| Run 3 | Design | design:proposal-1 | stopped | 16:30 | 16:30 | 0 | 2 |
| Run 3 | Design | design:proposal-2 | stopped | 16:30 | 16:30 | 0 | 1 |
| Run 3 | Design | design:proposal-3 | stopped | 16:30 | 16:30 | 0 | 1 |
| Side | ML demo | copista-2m demo page for GitHub Pages | done | 16:38 | 16:41 | 3 | 21 |
| Side | Fast track | First version build (mvp/) | done | 15:19 | 15:29 | 10 | 69 |
| Side | Fast track | Software design document | done | 15:20 | 15:22 | 2 | 16 |
