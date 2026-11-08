# Build timeline

All times are Sydney daylight time (AEDT, UTC+11) on 2026-11-08. Generated from the status page on every push; last updated 2026-11-08 21:22 AEDT.

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
| 17:06 | Round 2 noteheads owner finished: challenge set 0.745 → 0.784 from the front end alone (pitch 0.785 → 0.841), challenge files with no staves 19 → 4, benchmark 0.905 → 0.918. Only the symbols owner and the integrator remain in round 2. |
| 17:12 | Round 2 symbols owner finished: tuplets read and represented exactly (L3c resolved), key signatures right on every real scan but one (L2 resolved), mid-piece clef and key changes detected, slurs no longer mistaken for beams. Live tree 0.919, real scans 0.902. All five owners done; the round 2 integrator is running. |
| 17:14 | Release 0.4.0 (17:13 AEDT) regression-tested against 0.3.0: no regression on the benchmark (0.918 → 0.919, real scans 0.900 → 0.902) or the challenge set (0.784, no item worse). |
| 17:33 | User reported rests are not transcribed. Confirmed: 70 of 256 benchmark rests produced, the rest left as invisible gaps. A dedicated rests hotfix agent started (new src/rests.js: all rest values, multi-bar rests, rests on piano staves, visible rests instead of gaps). |
| 17:36 | Round 2 integrated (0.925 overall, real scans 0.907) and shipped as v0.5.0 at 17:36 AEDT together with Maple Leaf Rag as the default sample. Regression test against 0.4.0 running. |
| 17:36 | User asked for synthetic tests covering every symbol and layout plus performance: coverage suite workflow started (8 generators by symbol family and layout, per-symbol support matrix, speed and memory by dpi and page count). |
| 17:36 | Round 3 started: 6 owners including the copista-2m ML integration, working on 24 tracked limits including the L19 regressions and beamed 16ths. |
| 17:38 | Release 0.5.0 regression-tested against 0.4.0: no regression. Benchmark 0.919 → 0.925 (pitch +0.013, real scans +0.005); challenge 0.784 → 0.789, 16 items better, none worse, schema-valid 99.5% → 100%. |
| 17:44 | Coverage suite, notes family: 10 items (every note value, dots, chords of 2–6 notes, beams, flags, ledger lines up to 5, grace and cue notes, tremolos), each counted symbol checked against LilyPond's own layout dump. |
| 17:45 | Coverage suite: pitch family (12 items: every clef incl. octave clefs, all 15 key signatures, key changes, every accidental incl. double, 8va/8vb/15ma) and time family (10 items: every time signature, changes, pickups, tuplets 2–7 and nested, ties across systems) done; 3 of 8 families finished. |
| 17:45 | Coverage suite: rests family done (9 items, every rest value, dotted, whole-bar and multi-bar rests, raised and lowered rests on two-voice staves); handed to the rests hotfix agent as extra test data. 4 of 8 families finished. |
| 17:47 | Coverage suite: marks family done (9 items: articulations, fermatas, ornaments, arpeggios, breath marks, every dynamic and hairpin, pedal marks, fingering, tempo, rehearsal marks, chord symbols). 5 of 8 families finished. |
| 17:59 | Rests hotfix shipped as v0.5.1 (17:50 AEDT): rests now detected in every voice including piano; benchmark rests F1 0.445 → 0.581. |
| 17:59 | Incident 17:50–17:58 AEDT: the live app showed ‘Assembly failed’ (0 parts) because a round 3 work-in-progress change used Node-only debug flags, and CI/Pages builds failed because the app’s new ML model files were git-ignored. Fixed forward: a guard in the bundle, model files committed, push script hardened against files changing mid-push. Live app verified converting Maple Leaf Rag again. |
| 17:59 | Shared machine was at 99% CPU; the evaluation tool now caps parallel jobs at 16 (was 190) and waits while the host is over 90% busy. All agents told to keep heavy work low. |
| 17:59 | Round 3 UI owner finished: 41 of 41 UI checks (v0.5.0 page: 35); St. Anselm added as a second sample beside Maple Leaf Rag; English + German lyric OCR shipped; each page notes whether it was rotated, smoothed or split as a 2-up spread; spread pages now colour 98.6% of noteheads by part (was 33%); benchmark 0.934 on the live tree. |
| 18:02 | Release 0.6.0 (18:01 AEDT): rests precision fix (key-signature sharps/naturals were read as quarter rests) plus round 3 UI work. CI and Pages green. Score owner removed all Node-only debug flags; keyboard two-voice split is now the default. |
| 18:05 | Coverage suite: all 8 families generated (structure 8 items, layouts 20, perf 21 incl. 100–600 dpi, A4/Letter/A3 and 1–40 pages) and the harness built (--set coverage, per-symbol support matrix, per-page time and peak memory). First pass on 76 items: 20 symbol tags supported, 40 partial, 90 unsupported; 16 of 19 layouts supported. Validation and the full baseline are running. |
| 18:08 | Round 3 voices owner finished: two voices inside piano parts (L17 resolved), small instrument staves above a piano kept as separate parts (L18 partial), key changes carried across systems, single-staff pieces no longer wrongly split. Live tree: benchmark 0.946 (pitch 0.940, duration 0.910, rests 0.800, real scans 0.922); challenge 0.898. |
| 18:14 | Release 0.7.0 (18:09 AEDT) and regression test: benchmark no regression (0.925 → 0.946, rests 0.436 → 0.800, real scans 0.907 → 0.922); challenge 0.788 → 0.802 with 18 items better and 3 severe scans worse, added to L19. |
| 18:15 | Round 3 noteheads owner finished: benchmark 0.935 → 0.946, challenge 0.891 → 0.899; Maple Leaf Rag 0.897 → 0.955; thin-photocopy pages that found no staves now read. A duplicate copy of this agent (started by mistake when I messaged it) wrote a regressing change in a scratch folder; it never reached the live code. |
| 18:16 | Round 3 ML owner finished: copista-2m integrated as a correction pass over the app’s own reading; benchmark 0.942 → 0.957, real scans 0.922 → 0.943, challenge 0.802 → 0.814, Maple Leaf Rag 0.907 → 0.928. Shipped as an option; turning it on by default needs a small UI change, left to the round 3 integrator. |
| 18:16 | An extra noteheads candidate (snap3) measured: challenge 0.892 → 0.903, fixes several severe yellowed and photocopy scans but regresses a phone-photographed piano scan by 0.26. Not shipped; handed to the round integrator / round 4 (scratchpad/round4-notes.md). |
| 18:20 | User asked to investigate OpenCV as a fallback for identifying symbols: OpenCV.js trial started (template matching, contour features + kNN/SVM, HOG + SVM), as a fallback only, measured on and off, prototype behind an option if it wins. |
| 18:24 | Coverage suite complete (18:22 AEDT): 102 items validated, all 139 symbol tags and 19 layouts covered. App baseline: 22 tags supported, 38 partial, 79 unsupported; 18 of 19 layouts supported. Speed ~2.3–3.7 s per page, flat with page count; memory grows ~46 MB per page. Seven new limits (L20–L26) queued for round 4. Report: docs/COVERAGE.md (also on Pages). |
| 19:28 | Round 3 integrated and shipped: benchmark 0.948, real scans 0.926, challenge 0.910, rests 0.802, all outputs valid, browser check passed; nothing reverted. Limits L10, L12, L13 and L17 resolved this round. |
| 19:34 | Round 3 pushed (7ae1200) after fixing a false-positive credential refusal (vendored OpenCV build now gitignored). Release 0.9.0 merged; regression check vs v0.8.0 running. |
| 19:34 | Maple Leaf Rag (default sample) measured: aggregate 0.959, pitch 0.912, duration 0.929, rests 0.792, parts 1.000. |
| 19:34 | Overlay agent started (Opus xhigh): marks for every recognised symbol class, pitch/duration labels, and highlighting of unrecognised ink. |
| 19:36 | User asked to use OpenCV to pre-clean scans for the edge cases that break detection. Scope given to the opencv agent: a quality-gated pre-clean stage (mvp/src/cv.js) for halftone, noise, JPEG, phone, photocopy, stain, bleed and curl pages, targeting L11 and L19, measured per class on the challenge set. |
| 19:38 | v0.9.0 regression check vs v0.8.0: no regression (benchmark+OCR 0.946 to 0.948, real scans 0.921 to 0.926; challenge 0.808 to 0.809, 0 items down more than 0.05). |
| 19:38 | Pushed 184d5b5: All examples picker in /app/ (19 shareable benchmark scans, 8 real + 11 synthetic; restricted Bach excluded; assets 39.6 MB of 64). |
| 19:38 | User asked for hand-drawn repair marks on the page after detection; added to the overlay agent's scope (freehand/line marks in page coordinates, notes, undo, per-document persistence, JSON + PNG export for a later repair pass). |
| 19:44 | Overlay shipped (42663a6, release 0.10.0): marks for every recognised class, pitch/value labels, zoom control, 'Not recognised' hatching (72 on the rag). Benchmark MusicXML byte-identical; no regression. CI and Pages green. |
| 19:44 | Overlay agent resumed for the repair-drawing mode. |
| 19:44 | User asked to pre-identify text (title, composer, instrument names, bar numbers) and dynamics (mf etc.). textsym agent started (Opus xhigh): text-region classification with OCR, dynamics/hairpin shapes, braces/slurs/grace if cheap, and MusicXML credits, part names and dynamics (L9, L22). |
| 19:46 | Overlay restyle per user: unrecognised ink as yellow highlighter; every identified item filled with a transparent tint of its own type colour (13 distinct type colours; note-head outline keeps the part colour). Verified light/dark. Shipping together with the overlay agent's repair mode (same files); repair marks moving off yellow. |
| 19:46 | OpenCV investigation done: don't ship OpenCV.js for symbols (10.4 MB, needs an eval-free patch, ~170 MB heap); classical rests/clefs/accidentals already match learned classifiers. Real gap: time-signature digits are never read (0/182). A plain-JS Bravura template matcher reads 99.8% of digits on scans (90.9% severe); first time signature right 333 to 341 of 365 challenge, 246 to 269 of 306 coverage; +0.25 s per item. The OpenCV agent was told to ship it default-on, then build the quality-gated pre-clean stage. |
| 19:47 | Sheet view now uses the full page width (plate 1888 px at 1920; side panels flow below as columns); verified at 1920/1280/400, no horizontal scroll. Ships with the overlay agent's repair-mode push; build is waiting on textsym's dynglyphs.js. |
| 19:48 | User flagged bar numbers 5/10/15 as unrecognised; textsym told to recognise them (digit templates or digit-only OCR), label 'Bar N', and cross-check measure counts per system (warning, and fix single missed/extra barlines). Braces also to be recognised and tried as evidence for grand staves (L6, L18). |
| 19:51 | Shipped b10c817 (release 0.11.0 merged): Mark for repair (pen/line/box/circle, notes, undo, per-document storage, JSON with the detections and bar numbers inside each mark; lime highlighter), plus the yellow-highlighter, per-type tints and full-width view. CI and Pages green; regression check: no regression (0 items down more than 0.05). |
| 20:18 | Shipped 6ed273c (release 0.12.0 merged): text classes (title, composer, instrument names, bar numbers, tempo, expression, headers), dynamics ppp to fff + sf/sfz/fz/fp, hairpins, slurs/ties/fermatas/braces/ledger lines on the overlay; MusicXML credits, identification, part abbreviations, dynamics, wedges, words. Maple Leaf Rag unrecognised 72 to 4 in the app. Notes unchanged; regressions clean (benchmark 0.948, challenge 0.809). |
| 20:18 | textsym continues: bar-number measure-count check, braces as grand-staff evidence (L6/L18), grace notes, slurs/ties in MusicXML (L20). |
| 20:31 | Shipped 045d08f (release 0.13.0 merged): OpenCV pre-clean, quality-gated (clean pages untouched, OpenCV never loaded). Challenge 0.809 to 0.821 (23 items up more than 0.05, none down); thick photocopy 0.681 to 0.816, blur 0.754 to 0.839, combo 0.804 to 0.855, halftone 0.813 to 0.855. Benchmark+OCR 0.948 to 0.950, real scans 0.926 to 0.930. Cost: 10.4 MB asset (3.4 MB gzipped), about 1.1 s on the first degraded page. |
| 20:31 | Time-signature digit reader was exported but not wired; the opencv agent was sent back to wire it in, on by default. |
| 20:53 | Shipped 9a124ee + 4aab1af: time-signature digits read by plain-JS templates (on by default; challenge 0.8212 to 0.8227, first time signature right 342 to 352/365); pre-clean ported to plain JS with identical scores, so OpenCV.js (10.4 MB) is no longer shipped (assets back to 39.8 MB). Verified in the app: Maple Leaf Rag shows Time signatures 2, Not recognised 3. |
| 20:56 | User asked: default to the 'not recognised' view, larger and clearer highlights, and a way for users to say what an unrecognised item is. Overlay agent resumed: view presets (Unrecognised only by default), next/previous navigation, bigger highlights with a constant-width ring, click-to-label popover, user corrections applied to the MusicXML (accidentals, rests, dots, dynamics) as a pure post-pass, plus export of labelled crops as training data. |
| 20:58 | User asked to play the transcribed score with MIDI instruments. Playback agent started (Opus xhigh): MusicXML to timed events (ties, voices, repeats, tempo, dynamics), General MIDI program per part written into the MusicXML, self-hosted sampled GM subset (8 MB budget, lazy) with an oscillator fallback, transport + mixer, follow-along cursor on the preview and the scan, MIDI file export. |
| 21:01 | User couldn't see the examples menu (it looked like a third button). Fixed in the tree (chevron, reads 'All 19 examples'); ships with the overlay agent's next push. Changelog moved to the bottom of /app/, collapsed (e0c6c6b). |
| 21:01 | User asked to improve the UI, cut verbiage and streamline usage: uiux agent started (Opus xhigh, design-uiux-canon), coordinating with overlay/playback/textsym on shared UI files. |
| 21:03 | OpenCV agent confirmed the time-signature reader is in v0.14.0 (rag: both 2/4 read; coverage first time signature right 244 to 270/306). Next task for it: phone/book dewarp guided by staff lines, dashed-staff reconstruction (L11), and diagnosis of the German SATB severe scan (L19). |
| 21:15 | Shipped 9d1b30b (release 0.15.0 merged): playback with General MIDI instruments (transport, mixer, follow-along on preview and scan, repeats/voltas/D.C./D.S., tempo, dynamics), MIDI file export, MusicXML midi-instrument per part; FluidR3_GM subset 4.98 MB (CC BY 3.0). Benchmark/challenge unchanged. CI and Pages green (Pages and release zips rebuild from committed source, so committed dist files carrying others' WIP don't reach users). |
| 21:22 | Shipped f0cb830 (release 0.16.0 merged): 'Unrecognised only' default view with Previous/Next (N/P), bigger highlights (at least 1.6 staff spaces, 18 px, 3 px ring), 'What is this mark?' labelling with corrections applied to the MusicXML (src/corrections.js: accidental, rest, dot, dynamic, noise), labelled-crop export; also the uiux streamlining and the examples-menu fix. MusicXML byte-identical without labels; no regression. CI and Pages green. |

## Accuracy by round

Scores are against the benchmark of synthetic and real scans with exact answers (1.00 is perfect).

| Run | Overall | Pitch | Duration | Lyrics | Parts | Schema-valid | Real scans |
|---|---|---|---|---|---|---|---|
| v1 baseline | 0.589 | 0.493 | 0.542 | 0.439 | 0.727 | 1.000 | 0.618 |
| Round 1 (shipped) | 0.884 | 0.863 | 0.822 | 0.817 | 0.987 | 1.000 | 0.865 |
| Challenge set baseline (round 1 code, OCR) | 0.747 | – | – | – | – | – | – |
| Round 2 (interim) | 0.918 | – | – | 0.911 | – | 1.000 | 0.900 |
| v0.3.0 released (benchmark, OCR) | 0.918 | 0.891 | 0.851 | 0.911 | 0.992 | 1.000 | 0.900 |
| v0.4.0 released (benchmark, OCR) | 0.919 | 0.892 | 0.854 | 0.911 | 0.992 | 1.000 | 0.902 |
| Round 2 integrated = v0.5.0 | 0.925 | 0.906 | 0.863 | 0.912 | 0.993 | 1.000 | 0.907 |
| Round 3 (interim, voices owner + rests) | 0.946 | 0.940 | 0.910 | – | – | 1.000 | 0.922 |
| Round 3 integrated | 0.948 | 0.943 | 0.915 | 0.916 | 0.994 | 1.000 | 0.926 |

## Known limits

| ID | Limit | Owner | Status | Evidence |
|---|---|---|---|---|
| L1 | Hollow noteheads sometimes missed (main source of rhythm errors) | Noteheads and staves | Partial (round 3) | Benchmark duration 0.863 (r2) to 0.915. Challenge rhythm-category duration 0.562 to 0.689; all challenge items 0.804 to 0.846. The heads accidental-strip fix gave bwv5-7 0.934 to 0.967. With the ML detector on (opt-in, not shipped in the UI), benchmark duration rises to 0.955. |
| L2 | Key signatures unreliable on old engraving | Symbols | Partial (round 3) | Symbols: challenge scans with the wrong overall key went from 34 to 23. Auld Lang Syne A-flat section 0 to -4, sharp1911 0 to -1. Pitch category, pitch metric: 0.709 to 0.768. Still open: severe scans read key 0, and signs filled into solid rectangles are missed. |
| L3a | Rests not detected | Symbols | Partial (round 3) | Rests F1 on the benchmark 0.436 (r2) to 0.802; on the challenge 0.647 to 0.757. Layout category is still 0.327, voices 0.515. |
| L3b | Ties and slurs not detected; a stray slur can create a false 16th | Symbols | Open | No tie or slur detection. The 264 tie starts in the outputs all come from notes split at barlines. The ties edge-case group improved only through other fixes (0.901 to 0.926). |
| L3c | Triplets and other tuplets not detected | Symbols | Resolved (round 3) | Clara output has 32 time-modification elements (+20 triplet notes in r3). Tuplet edge-case group 0.873 to 0.909. rh01 +0.01 to +0.02, rh08 +0.03 to +0.04. |
| L3d | Mid-piece clef and key changes not detected | Symbols | Resolved (round 3) | pitch-keysig-odyssey scan 0.772 to 0.884; its output writes 8 key elements, matching the 8 in the truth. Clef changes carry across system breaks (rag bars 10-13 left hand in treble). |
| L3e | Part names not read from the labels at the start of each system | Lyrics (OCR) + voices (apply) | Partial (round 3) | Labels are read on most items (Maple 'Piano', S A T B on hymns; benchmark parts 0.994). Single-letter OCR noise is read as 'Alto' on twinkle-phone severe and pitch-ledger-ottava. The integrator fix stops it splitting a piano, but the label reader still returns it. Trio labels are not read. |
| L4a | Lyric alignment drifts when the note count is off | Voices + lyrics | Resolved (round 3) | Benchmark lyrics 0.916 (lenient 0.935); challenge lyrics 0.899 to 0.927. Alignment holds when the note count is off (e.g. Lindenbaum 477 truth notes against 442 produced, lyrics 0.794). |
| L4b | No melisma or extender handling | Lyrics + voices | Partial (round 3) | Extenders are emitted (233 in 14 benchmark outputs) but over-emitted against the truth's 126. |
| L5a | At most 8 PDF pages processed | UI | Resolved (round 3) | Page cap is 40 (r2 multipage test). The UI's r3 8-page run read all pages and Stop works. |
| L5b | Stanza text printed below the last system dropped for SATB | Lyrics + voices | Partial (round 3) | Stanzas below the music are kept as credit text, and lyr06 matches the reference. The stanza edge-case group is 0.623 to 0.656. Stanzas are not set as verses even where they would fit. |
| L6 | Piano wrongly split: grand staves become S/A/T/B, voice+piano gets 4 parts instead of 2 (breaks the never-split-piano rule) | Voices (score.js) | Partial (round 3) | Challenge must_not_split items with the wrong part count: 8 in r2, 4 now, out of 169. andantino-yellowed and twinkle-yellowed are fixed by heads. The integrator fix took twinkle-piano2p-phone severe from 0.660 to 0.891 (1 Piano part). Still wrong: song-one-system-poem-block severe, satb-open-divisi severe, anthem-4-pages severe, trio severe. |
| L7 | Lyrics attached to every part in closed score (3–4× too many syllables) | Voices + lyrics | Partial (round 3) | Lyrics go to the voice they are printed under, but the 'sung by both' copy rule fires on 14 items where the truth gives the text to one voice: aloha-oe-chorus lyric 0.742 (lenient 0.929), bwv3-6 0.722. |
| L8 | Lyric text or other glyphs read as noteheads on single-melody pages | Noteheads and staves | Resolved (round 3) | foster-jeanie-melody produces 93 notes against 95 in the truth (aggregate 0.961). Rest blobs are no longer merged into chords (heads change 3). |
| L9 | Part names generic or wrong (open score shows Staff N; TTBB named SATB, with an octave error) | Voices + lyrics | Partial (text round) | Part-name edge-case group 0.660 to 0.801; ttbb-treble8-a2-unis scan 0.888 to 0.900. Flute/Tuba are named 'Voice 1/Alto' or 'Piano'. Trio names are not read. Text round (6ed273c): instrument text is read and <part-abbreviation> written (Piano/Pno.); work title, composer, lyricist, arranger and rights written as credits and identification. |
| L10 | Pages rotated 90° produce nothing; 180° pages read badly (pitch 0.21) | Noteheads and staves (page orientation) | Resolved (round 3) | No rot90 page is in the no-notes list (v0.3.0 had 9). Rotation and landscape edge-case group 0.921 to 0.935. |
| L11 | Halftone screens and heavy noise blank the page | Noteheads and staves (binarisation) | Partial (round 3) | Challenge items with no notes: 4 in r2, 1 now (35 at v0.3.0). Only hymn-descant-cue-notes-amen-small severe remains. Severe photocopies recovered: agrace 0.117 to 0.650, wind-melody 0.167 to 0.784, andantino 0.367 to 0.766. Pre-clean (045d08f): halftone class 0.813 to 0.855 (descreen); hymn-descant-cue-notes-amen-small severe still 0.113 (staff lines broken into dashes). |
| L12 | Two-page spreads read as one wide system (8–13 parts) | Noteheads and staves (page split) | Resolved (round 3) | No spread item is in the wrong-part-count list (v0.3.0 had twinkle-spread at 4 and 6 parts). Spread edge-case group 0.879 to 0.890. Spread overlay colouring is 98.7%. |
| L13 | Tuplets cannot be represented: 8 divisions per quarter | Symbols + voices + MusicXML | Resolved (round 3) | divisions=840. Clara writes 32 time-modification elements. Tuplet edge-case group 0.909. |
| L14 | Double dots, multi-bar rests and whole-bar rests | Symbols + voices | Partial (round 3) | Whole-bar rests are written in 70 challenge outputs and H-bar multi-rests are detected (rests agent). No multiple-rest element is written. Double dots are not modelled. Edge-case group 0.820 to 0.857. |
| L15 | Double sharps/flats and 8va/8vb brackets | Symbols | Open | None of the 365 challenge outputs contains a double-sharp, a double-flat or an octave-shift. pitch-ledger-ottava scores 0.58 to 0.88. |
| L16 | Key and time-signature changes mid-piece not written; C clefs (alto/tenor) | Symbols + voices | Partial (round 3) | Key changes are written (odyssey 8/8). C clefs are read (3 C clefs in every clef-carousel output; scan 0.899 to 0.920). Mid-piece time-signature changes are not written (rh03: 1 time element against 12 in the truth). |
| L17 | Two voices inside one part (piano right hand, divisi) merged into chords | Voices + MusicXML | Resolved (round 3) | Score r3: Beach piano 0.881 to 0.955 (pitch 0.86 to 0.96), about 40 twinkle-piano variants +0.015 each. Benchmark beach-prayer 0.878 to 0.967. Multi-voice edge-case group 0.908 to 0.929. |
| L18 | A bracketed instrument pair (violin + cello) read as a piano grand staff; organ pedal staff becomes a separate part | Voices (layout) | Partial (round 3) | trio-minuet scan 0.480 to 0.819 (small staves become separate instruments). A bracketed pair with joined barlines is still read as a piano: pitch-ledger-ottava mild comes out as Piano, and trio severe as 1 part. Edge-case group 0.790 to 0.828. |
| L19 | Regressions found after shipping: after 0.3.0, 4 challenge items (wind-melody thick photocopy severe, German SATB severe, lyr08 Scandinavian, hymn-descant mild); after 0.7.0, 3 severe challenge scans (German SATB −0.119, andantino phone −0.072, andantino skew −0.060) | Round 3 owners (heads, lyrics, score) | Partial (round 3) | Against v0.3.0: wind-melody-photocopy-thick severe 0.251, now 0.369 (fixed); lyr08 scan 0.929, now 0.904 (within 0.05). Still more than 0.05 down: satb-closed-lyrics-both-staves-de severe 0.684 to 0.595, and hymn-descant-cue-notes-amen-small mild 0.705 to 0.633. Pre-clean (045d08f): severe photocopies andantino thick 0.616 to 0.854, wind-melody thick 0.351 to 0.711; German SATB severe (0.545) and phone shots unchanged (flattening phone pages hurt, so skipped; no dewarp yet). |
| L20 | Ties never written (only 5 of 79), including ties across systems | Symbols + voices | Queued for round 4 | Coverage: tie 0%; tied pitches themselves read 95%. |
| L21 | Only 2/4, 3/4 and 4/4 written: C, cut time, 2/2, 3/2, 6/8, 9/8, 12/8, 5/4, 5/8, 7/8 and time changes missing | Symbols + voices | Partial (template reader) | Coverage: 110 occurrences never written; time-3-4 55%, time-4-4 71%. 9a124ee: template digit reader on by default; first time signature right 342 to 352 of 365 challenge items; Maple Leaf Rag 2/4 read on both staves (overlay 0 to 2). Mid-piece changes still not written. |
| L22 | Beams, slurs, fermatas, dynamics, hairpins, articulations, repeats and endings never written to MusicXML | Voices (MusicXML) + symbols | Partial (text round) | Coverage: beam 703, slur 100, fermata 130 occurrences, all 0%. Text round (6ed273c): dynamics (27 of 40 benchmark marks, precision 0.84), hairpins (coverage 84-86% clean/scan) and tempo/expression words now written. Beams, slurs, fermatas, articulations, repeats and endings still not written. |
| L23 | Half and whole notes, dots, 32nd/64th notes partial | Noteheads + symbols | Queued for round 4 | Coverage: note-half 76%, note-whole 46%, dot 69% (adds false notes), note-32nd 11%. |
| L24 | Key signatures of 4+ sharps or flats and courtesy accidentals weak | Symbols | Queued for round 4 | Coverage: key-s4 25%, key-s6/s7 0%, acc-courtesy 22%. |
| L25 | Lyrics: non-ASCII and elisions 0%, extenders 58%, multi-verse 73% | Lyrics | Queued for round 4 | Coverage: 4-language item lyrics 0.16. |
| L26 | Memory grows about 46 MB per page (40-page book peaks at 2.2 GB) | UI + score | Queued for round 4 | Coverage perf: peak MB = 297 + 5.2 × total megapixels (R² 0.97); time per page flat at ~2.3–3 s. |

## Runs

| Run | What | Status | Agents returned | Note |
|---|---|---|---|---|
| Run 1 | Vector-PDF design | stopped | 0 of 4 | Stopped at 14:56 AEDT when the input was clarified as scanned images. |
| Run 2 | Scanned-PDF design | stopped | 0 of 4 | Stopped at 14:58 AEDT to restart with more agents in parallel. |
| Run 4 | Fix-forward round 1 (shipped 0.884) | done | 7 of 7 |  |
| Run 5 | Challenge test set (edge cases + scan damage) | done | 7 of 7 |  |
| Run 3 | Max-parallel main workflow (research) | stopped | 7 of 10 | Stopped at 16:30 AEDT once all 7 research items returned, as planned; its 3 design-proposal agents had just started and were stopped with it. The full rebuild was replaced by fix-forward rounds on v1. |
| Run 6 | Fix-forward round 2 (shipped 0.925 as v0.5.0) | done | 6 of 6 |  |
| Run 7 | Coverage suite (102 items, every symbol and layout) | done | 10 of 10 |  |
| Run 8 | Fix-forward round 3 (shipped 0.948) | done | 7 of 7 |  |
| Side | Agents launched directly from the session | running | 3 of 7 |  |

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
| Run 6 | Fix | fix:r2:heads | done | 16:21 | 17:05 | 44 | 243 |
| Run 6 | Fix | fix:r2:symbols | done | 16:21 | 17:12 | 51 | 234 |
| Run 6 | Fix | fix:r2:score | done | 16:21 | 17:00 | 39 | 170 |
| Run 6 | Fix | fix:r2:lyrics | done | 16:21 | 16:41 | 20 | 109 |
| Run 6 | Fix | fix:r2:ui | done | 16:21 | 16:45 | 24 | 87 |
| Run 6 | Integrate | integrate:r2 | done | 17:12 | 17:34 | 22 | 93 |
| Run 7 | Harness | harness:coverage | done | 17:34 | 17:50 | 16 | 98 |
| Run 7 | Generate | gen:notes | done | 17:34 | 17:44 | 10 | 76 |
| Run 7 | Generate | gen:rests | done | 17:34 | 17:45 | 11 | 84 |
| Run 7 | Generate | gen:pitch | done | 17:34 | 17:45 | 11 | 61 |
| Run 7 | Generate | gen:time | done | 17:34 | 17:45 | 11 | 67 |
| Run 7 | Generate | gen:marks | done | 17:34 | 17:46 | 12 | 78 |
| Run 7 | Generate | gen:structure | done | 17:34 | 17:53 | 19 | 95 |
| Run 7 | Generate | gen:layouts | done | 17:34 | 17:56 | 22 | 131 |
| Run 7 | Generate | gen:perf | done | 17:34 | 18:05 | 31 | 92 |
| Run 7 | Baseline | validate+baseline | done | 18:05 | 18:24 | 19 | 113 |
| Run 8 | Fix | fix:r3:heads | done | 17:36 | 18:15 | 39 | 187 |
| Run 8 | Fix | fix:r3:symbols | done | 17:36 | 19:08 | 92 | 273 |
| Run 8 | Fix | fix:r3:score | done | 17:36 | 18:07 | 31 | 134 |
| Run 8 | Fix | fix:r3:lyrics | done | 17:36 | 18:22 | 46 | 156 |
| Run 8 | Fix | fix:r3:ui | done | 17:36 | 17:59 | 23 | 91 |
| Run 8 | Fix | fix:r3:ml | done | 17:36 | 18:08 | 32 | 192 |
| Run 8 | Integrate | integrate:r3 | done | 19:08 | 19:25 | 17 | 107 |
| Side | Fast track | a5575cc38e20927a6 | run | 18:07 |  | 14 | 27 |
| Side | Fast track | ae52f1cf560b35868 | run | 18:15 |  | 4 | 29 |
| Side | ML demo | copista-2m demo page for GitHub Pages | done | 16:38 | 16:41 | 3 | 21 |
| Side | Fast track | First version build (mvp/) | done | 15:19 | 15:29 | 10 | 69 |
| Side | Research | OpenCV.js symbol-fallback investigation | run | 18:20 |  | 68 | 107 |
| Side | Hotfix | Rests fix (L3a, user-reported) | run | 17:33 |  | 35 | 179 |
| Side | Fast track | Software design document | done | 15:20 | 15:22 | 2 | 16 |
