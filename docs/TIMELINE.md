# Build timeline

All times are Sydney daylight time (AEDT, UTC+11) on 2026-11-08. Generated from the status page on every push; last updated 2026-11-08 16:28 AEDT.

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

## Accuracy by round

Scores are against the benchmark of synthetic and real scans with exact answers (1.00 is perfect).

| Run | Overall | Pitch | Duration | Lyrics | Parts | Schema-valid | Real scans |
|---|---|---|---|---|---|---|---|
| v1 baseline | 0.589 | 0.493 | 0.542 | 0.439 | 0.727 | 1.000 | 0.618 |
| Round 1 (shipped) | 0.884 | 0.863 | 0.822 | 0.817 | 0.987 | 1.000 | 0.865 |

## Known limits

| ID | Limit | Owner | Status | Evidence |
|---|---|---|---|---|
| L1 | Hollow noteheads sometimes missed (main source of rhythm errors) | Noteheads and staves | Partial (round 1) | Hollow heads: wider insides filled, broken outlines closed, outline eaten by staff removal restored. Missed half notes 81 → 28, false whole notes 156 → 3. On the faint 1867 Haupt scan heads found 54 → 105. Beamed 8ths/16ths are now the largest miss source (598) — round 2. |
| L2 | Key signatures unreliable on old engraving | Symbols | Resolved on synthetic, partial on real (round 1) | Header read left to right (clef, key, time); accidentals checked against where each sharp or flat should sit for the clef. Correct on every synthetic item; America 1 sharp and St. Anselm 4 sharps correct. Some broken bass staves on St. Anselm still guess the clef. |
| L3a | Rests not detected | Symbols | Partial (round 1) | Printed rests now detected (whole, half, quarter, eighth) and placed; rests F1 0.14 → 0.41. Over-full voice-measures 259 → 0. |
| L3b | Ties and slurs not detected; a stray slur can create a false 16th | Symbols | In progress (round 1) |  |
| L3c | Triplets and other tuplets not detected | Symbols | Queued for round 2 |  |
| L3d | Mid-piece clef and key changes not detected | Symbols | Partial (round 1) | Treble-8vb clef detected; broken clefs re-joined; two treble clefs in a piano system kept as read. Per-system clef changes are read but not yet applied by score.js (round 2). |
| L3e | Part names not read from the labels at the start of each system | Lyrics (OCR) + voices (apply) | Queued for round 2 |  |
| L4a | Lyric alignment drifts when the note count is off | Voices + lyrics | Partial (round 1) | Syllables now matched to notes by left-to-right alignment instead of nearest note; a lyric line goes to the staff above it. |
| L4b | No melisma or extender handling | Lyrics + voices | Partial (round 1) | Hyphens carried across system breaks; extender underscores handled. Splitting unhyphenated words over several notes still open. |
| L5a | At most 8 PDF pages processed | UI | Queued for round 2 |  |
| L5b | Stanza text printed below the last system dropped for SATB | Lyrics + voices | Partial (round 1) | Stanza blocks below the music are now detected and kept out of the underlay (no more poem text as lyrics). Attaching them as extra verses still open. |
| L6 | Piano wrongly split: grand staves become S/A/T/B, voice+piano gets 4 parts instead of 2 (breaks the never-split-piano rule) | Voices (score.js) | Resolved (round 1) | All 20 benchmark items now get the right part count (was 13 of 20). Piano grand staves are recognised by barlines running through both staves and are never split; Bach bwv67, Clara Schumann, Lindenbaum, Dichterliebe, Beach and Aloha fixed. |
| L7 | Lyrics attached to every part in closed score (3–4× too many syllables) | Voices + lyrics | Resolved (round 1) | Lyrics between staves go to the upper voice only; lines under the lowest split staff go to both its voices; copying to every voice is opt-in. Lyrics 0.60 → 0.82. |
| L8 | Lyric text or other glyphs read as noteheads on single-melody pages | Noteheads and staves | Resolved (round 1) | A notehead outside the staff must sit on or next to ledger lines, which removes lyric letters, tuplet numbers and dynamics. Jeanie 0.48 → 0.88, Silent Night 0.56 → 0.96. |
| L9 | Part names generic or wrong (open score shows Staff N; TTBB named SATB, with an octave error) | Voices + lyrics | Resolved (round 1) | Part names from the clef pattern: SATB, TTBB (new treble-8vb clef), SSAA, SAB, solo above SATB, Voice. Reading printed name labels is still tracked under L3e. |

## Runs

| Run | What | Status | Agents returned | Note |
|---|---|---|---|---|
| Run 1 | Vector-PDF design | stopped | 0 of 4 | Stopped at 14:56 AEDT when the input was clarified as scanned images. |
| Run 2 | Scanned-PDF design | stopped | 0 of 4 | Stopped at 14:58 AEDT to restart with more agents in parallel. |
| Run 3 | Max-parallel main workflow | running | 6 of 7 | Research only from here. It will be stopped when research returns; the full rebuild was dropped in favour of fix-forward rounds on v1. |
| Run 4 | Fix-forward round 1 (shipped 0.884) | done | 7 of 7 |  |
| Run 5 | Challenge test set (edge cases + scan damage) | running | 6 of 7 |  |
| Run 6 | Fix-forward round 2 | running | 0 of 5 |  |
| Side | Agents launched directly from the session | running | 2 of 2 |  |

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
| Run 3 | Research | web:omr | done | 14:58 | 15:11 | 13 | 77 |
| Run 3 | Research | web:voices | done | 14:58 | 15:15 | 17 | 120 |
| Run 3 | Research | spike:ml | run | 14:58 |  | 75 | 184 |
| Run 3 | Research | spike:classical | done | 14:58 | 15:50 | 52 | 120 |
| Run 3 | Research | spike:ocr | done | 14:58 | 15:58 | 60 | 129 |
| Run 3 | Research | corpus:synthetic | done | 14:58 | 15:42 | 44 | 82 |
| Run 3 | Research | corpus:real | done | 14:58 | 15:57 | 59 | 189 |
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
| Run 5 | Validate | validate+baseline | run | 16:18 |  | 10 | 67 |
| Run 6 | Fix | fix:r2:heads | run | 16:21 |  | 7 | 80 |
| Run 6 | Fix | fix:r2:symbols | run | 16:21 |  | 6 | 69 |
| Run 6 | Fix | fix:r2:score | run | 16:21 |  | 7 | 52 |
| Run 6 | Fix | fix:r2:lyrics | run | 16:21 |  | 6 | 49 |
| Run 6 | Fix | fix:r2:ui | run | 16:21 |  | 6 | 33 |
| Side | Fast track | First version build (mvp/) | done | 15:19 | 15:29 | 10 | 69 |
| Side | Fast track | Software design document | done | 15:20 | 15:22 | 2 | 16 |
