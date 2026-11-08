# Classical OMR spike (pure JS)

Findings and numbers: [`../../docs/spike-classical.md`](../../docs/spike-classical.md).

```
src/            environment-agnostic core (CommonJS; only image.js file I/O touches node)
  pipeline.js   runOMR(gray, opts) -> { staves, systems, heads, barlines, skew, staffSpace, timings }
  binarize.js   background-normalised Otsu (+contrast guard, lenient companion), Sauvola, despeckle
  skew.js       projection-profile skew estimate (degrees, CCW positive)
  staffspace.js run-length "combo" estimate cross-checked by projection autocorrelation
  staves.js     strip projections -> 5-line (or 4-of-5) patterns -> tracking -> polylines; systems
  staffremoval.js line-tracking run-length staff removal
  cc.js         connected components + integral images
  noteheads.js  staff-position-constrained filled/hollow head detector (box features)
  stems.js      stem search per head (dir +1/-1, 2 = two stems = unison of two voices), stem rule
  barlines.js   staff-spanning thin verticals, span bars, thin+thick merge
  image.js      PGM/PPM/PNG I/O (pngjs), rotation
scores/         LilyPond test scores + omrtruth.ily (colour-coded ground truth)
tools/
  make_scores.sh   lilypond -> clean PDF + truth PDF -> pdftoppm 150/200/300 dpi
  truth.js         truth PPM + grob log -> truth JSON (heads, stems, barlines, staves, lyrics, ...)
  degrade.py       17 degradations (+ exact truth geometry transfer)
  make_dataset.sh  build data/set/<piece>_<dpi>_<cond>.png/.json in parallel
  eval.js          run + score one image (P/R per stage), optional overlay
  run_all.js       parallel evaluation over data/set -> results/*.jsonl
  report.js        markdown tables (--by cond|dpi|piece|cond,dpi --total)
  omr.js           run on any PNG/JPG/PGM page (no truth) with overlay
  debug_errors.js, probe.js, bench.js  error contact sheets, feature probes, timing
```

Reproduce (about 1 minute on a many-core machine):

```
npm install                       # pngjs only
tools/make_scores.sh              # needs lilypond + poppler-utils
for p in satb20 satb16 melody piano; do for r in 150 200 300; do
  node tools/truth.js data/raster/${p}_${r}.truth-1.ppm data/pdf/$p.truth.txt data/truth/${p}_${r}.json; done; done
tools/make_dataset.sh             # python3 + numpy + pillow
node tools/run_all.js results/final.jsonl && node tools/report.js results/final.jsonl --by cond --total
node tools/omr.js data/realscan/english_hymnal_1906_p269.jpg --overlay /tmp/ov.png
```

(`make_scores.sh` writes the truth PPMs that `truth.js` reads; they were deleted
after extraction to save space.)
