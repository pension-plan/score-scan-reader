# Score Scan Reader

Converts **scanned sheet music** (image-only PDFs, PNG or JPG) into **MusicXML 4.0**, entirely in the browser.

- Lyrics are read with OCR and kept as MusicXML lyrics (syllables, verses).
- When one staff carries two voices, as in closed-score SATB hymns, the voices are split into separate parts (Soprano, Alto, Tenor, Bass).
- Piano grand staves are kept as one part.

- **Live app:** https://pension-plan.github.io/score-scan-reader/app/
- **Build log, plan, research and accuracy tracker:** https://pension-plan.github.io/score-scan-reader/status/
- **Build timeline (AEDT):** [docs/TIMELINE.md](docs/TIMELINE.md), also at https://pension-plan.github.io/score-scan-reader/docs/TIMELINE.html
- **Software design document:** https://pension-plan.github.io/score-scan-reader/docs/SDD.html (source: [docs/SDD.md](docs/SDD.md))

All three are deployed to GitHub Pages from this repository on every push to `main` (`.github/workflows/pages.yml`).

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
