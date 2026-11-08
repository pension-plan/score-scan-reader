# Score Scan Reader

### ▶ Start here: **https://pension-plan.github.io/score-scan-reader/**

The site links to the converter, the build log and accuracy tracker, the design document, the research, and the ML detector demo.

Converts **scanned sheet music** (image-only PDFs, PNG or JPG, up to 40 pages) into **MusicXML 4.0**, entirely in the browser: nothing is uploaded.

**New here? Read the [user guide](docs/USER-GUIDE.md)** (also at https://pension-plan.github.io/score-scan-reader/docs/USER-GUIDE.html).

- **Reads** staves (also faint, broken or one-line percussion staves), clefs (G, F, C, treble 8vb, percussion), key and time signatures and their changes, notes from whole to 64th with dots, beams, chords, tuplets, grace and cue notes, rests and multi-bar rests, accidentals, ties and slurs, repeats, voltas, D.C./D.S./segno/coda, dynamics and hairpins, articulations, fermatas, ottava lines, tempo and metronome marks, titles and credits, chord symbols, fingering, pedal marks, rehearsal marks and bar numbers.
- **Lyrics** are read with OCR (English and German, with a second pass in French, Spanish, Italian and Czech where accents show) and kept as MusicXML lyrics: verses, syllables, melismas, elisions; stanzas printed below the music can be set as verses.
- **Parts**: two voices on one staff (closed-score SATB, SSAA, TTBB, divisi) are split into separate parts; piano and organ staves stay one part; printed part names are kept. Drum parts are written as unpitched notes with a General MIDI drum kit.
- **Shows its reading** over the scan (all marks, or only what it could not recognise), lets you **label unrecognised marks** (accidentals, rests, dots and dynamics you identify are written into the MusicXML) and **mark the page for repair** (exported as JSON or a marked PNG).
- **Plays the score** (General MIDI instruments, tempo, click, count-in, loops, parts mixer, repeats and dynamics) and saves it as a **MIDI file**.
- Long scans are read page by page with a progress strip; on a slow connection the notes are shown before the lyrics are in. An optional ML assist (the copista-2m detector) rechecks note values.

- **Home (start here):** https://pension-plan.github.io/score-scan-reader/
- **Live app:** https://pension-plan.github.io/score-scan-reader/app/
- **User guide:** https://pension-plan.github.io/score-scan-reader/docs/USER-GUIDE.html (source: [docs/USER-GUIDE.md](docs/USER-GUIDE.md))
- **What it reads, symbol by symbol:** [docs/COVERAGE.md](docs/COVERAGE.md)
- **Build log, plan, research and accuracy tracker:** https://pension-plan.github.io/score-scan-reader/status/
- **Build timeline (AEDT):** [docs/TIMELINE.md](docs/TIMELINE.md), also at https://pension-plan.github.io/score-scan-reader/docs/TIMELINE.html
- **Software design document:** https://pension-plan.github.io/score-scan-reader/docs/SDD.html (source: [docs/SDD.md](docs/SDD.md))

All of these are deployed to GitHub Pages from this repository on every push to `main` (`.github/workflows/pages.yml`).

## Quick start

Requirements: Node.js 24, `pdftoppm` (poppler-utils) and `xmllint` (libxml2-utils) for the tests.

```sh
npm install                 # pngjs, tesseract.js (node OCR), playwright (browser test)
npm run build               # bundles mvp/src + mvp/ui into mvp/dist/index.html
python3 -m http.server -d mvp/dist 8080   # then open http://localhost:8080
```

The page must be served over HTTP (not opened as a file) because it loads its OCR worker,
WebAssembly and sample scan from `mvp/dist/assets/` by relative URL.

Build the GitHub Pages site (app, status page and rendered docs) into `site/`:

```sh
npm run build && npm run site
python3 -m http.server -d site 8080
```

## Test

```sh
npm test               # scores the pipeline against every corpus item with a truth file (no OCR, fast)
npm run test:ocr       # same, with lyric OCR
npx playwright install chromium && npm run test:browser   # loads the built page and converts the sample
```

`npm test` writes `mvp/work/eval-ci.json` with per-item scores for pitch, duration, rests, lyrics,
part assignment and MusicXML validity, and an aggregate score
(0.3 pitch + 0.2 duration + 0.2 parts + 0.2 lyrics + 0.1 valid XML).
Useful options: `node mvp/tools/eval.mjs --out f.json --only <id,...> --set synthetic|real|challenge --jobs N`.

Convert one page from the command line:

```sh
pdftoppm -gray -r 200 corpus/real/methodist1905-st-anselm/scan.pdf page   # -> page-1.pgm
node mvp/tools/run.js page-1.pgm out.musicxml --no-ocr
```

## Layout

| Path | What |
|---|---|
| `mvp/src/` | The recognition pipeline (plain JS, runs in node and the browser) |
| `mvp/ui/` | Page markup, styles and app script |
| `mvp/tools/` | `build.js` (bundler + artifact-contract checks), `eval.mjs` (scoring), `run.js`, `pw/` (browser test) |
| `mvp/dist/` | Built page and self-hosted assets (the published app) |
| `corpus/` | Test scores: `synthetic/` (engraved + degraded, exact truth), `real/` (public-domain scans), `challenge/` (edge cases) |
| `docs/` | Software design document, research, feasibility trials, UI references, status page source |
| `spike/` | Feasibility-trial code (data, models and results are not committed) |
| `tools/` | `build-site.mjs` (GitHub Pages site), `push.sh` (commit and push) |
| `orchestration/` | The multi-agent workflow scripts that built and improve the app |

## Releases

Commits on `main` use Conventional Commits. Every push to `main` runs CI and redeploys GitHub Pages. release-please opens a release PR; merging it tags a
release and the workflow attaches downloadable copies: the built web app (zip), the full source
(zip) and the design document.

## Licences

Code: MIT. pdf.js and tesseract.js are Apache-2.0; OpenSheetMusicDisplay is BSD-3-Clause.
Test scores are public domain or CC0 unless an item's `ATTRIBUTION.txt` says otherwise.
Six Bach chorale test items are not in this repository because their source encodings are
licensed for testing only; rebuild them locally with `corpus/synthetic/_tools/run_all.py`
(needs music21 and LilyPond).
