coverage/perf - performance set of the synthetic coverage suite (corpus/coverage/perf/<id>/, manifest ../manifest.json)

Rebuild everything (parallel, about 1-2 minutes on 192 cores):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/perf/_tools/run_all.py [item-id-substring ...] [--keep-work]
Independent validation of the published folders (re-renders every engraving.ly, writes ../_logs/validate.json):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/perf/_tools/validate.py
Count taxonomy symbols in any MusicXML file (truth or app output), same rules as meta.json "counts":
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/perf/_tools/symcount.py file.musicxml [--json]

Items (21):
  perf-hymn-a4-{100,150,200,300,400,600}dpi   1-page closed-score SATB hymn, 4 stanzas (A4)
  perf-piano-a4-{100,150,200,300,400,600}dpi  symbol-dense 1-page piano page "Toccatina" (A4)
  perf-{hymn,piano}-letter-300dpi             same music on US Letter
  perf-{hymn,piano}-a3-300dpi                 same music on A3 (A4 layout enlarged x sqrt 2)
  perf-pages-{01,05,10,20,40}                 piano book of 1/5/10/20/40 pages (one variation per page, A4, 300 dpi)
Each item: engraving.ly, truth.musicxml (MusicXML 4.0), clean.pdf (undamaged raster), scan.pdf (typical scan),
scan-severe.pdf (heavy damage), meta.json (coverage keys + perf{dpi, pageSize, pages, megapixels, ...}), ATTRIBUTION.txt.

Code (nothing outside this folder is used or modified at run time):
  cov/model.py      score model (copied from corpus/challenge/layout/_tools/lsynth/model.py, extended: grace notes,
                    ornaments, arpeggio, fingering, breath, tremolo, ottava, forced/cautionary accidentals, harvest fields)
  cov/dsl.py        LilyPond-like note DSL (\g / \gs grace, \tupN/M, \ottava=n, \clef=x, \trill \mordent \turn \arpeggio
                    \breathe, -. -! -> -- -^, -N fingering, :32 tremolo, pitch! / pitch? accidentals ...)
  cov/lily.py       LilyPond writer (from lsynth/lily.py) + instrumented twin (\tweak id on every note head / rest,
                    after-line-breaking grob logger on every staff, lyrics line and the score)
  cov/harvest.py    parses the grob log: per note head pitch, duration, onset, staff, staff position, stem direction,
                    beam membership + beaming, live flag, printed accidental, dots; per staff counts of every other grob.
                    verify() checks EVERY model note / rest against the engraving (pitch, notated duration, tuplet
                    scale, onset incl. grace offset, staff); beam_values() turns LilyPond beaming into <beam> values
  cov/mxl.py        truth writer (from lsynth/mxl.py): stems, beams and accidentals exactly as engraved, grace, octave-shift,
                    ornaments, technical fingering, arpeggiate, breath, tuplet bracket visibility, key cancel, page layout
  cov/acc.py        per-part accidental simulation (from pitch/_tools/pk/acc.py) used to cross-check the printed accidentals
  cov/harmonize.py  SATB voice-leading solver (copy of lsynth/harmonize.py) for the hymn
  cov/degrade2.py   scan / photocopy / phone damage (copy of lsynth/degrade2.py); build.py calls it per page with
                    numpy default_rng(seed * 1000 + page)
  cov/validate_lib.py  copy of corpus/challenge/_validate/validate.py (truth reader, MIDI reader + check, PDF checks)
  symcount.py       taxonomy symbol counter (rules in its docstring)
  build.py          engrave(): twin -> harvest -> verify -> truth -> xmllint XSD -> music21 -> clean engraving ->
                    raster(twin) == raster(clean) -> MIDI attacks + lyrics == truth -> accidental cross-check ->
                    symcount(truth) == engraved grob counts for 40 symbol classes -> pages == plan, no LilyPond warning
  run_all.py        items, damage recipes (params + seeds), parallel render / damage / assembly, meta.json, manifest.json
  pieces/hymn.py    "O God, Our Help in Ages Past": tune BENCHMARK C.M. + harmony (CC0), text Watts 1719 (PD)
  pieces/piano.py   "Toccatina": 18 bars, 4 keys, 4 metres, repeat/voltas, Fine / D.C., ~85 symbol tags (CC0)
  pieces/variations.py  "Forty Variations": 23 textures x 30 keys, procedurally composed (CC0)
Logs: ../_logs/build.json (per-page damage timings), ../_logs/validate.json; per-engraving verification reports are in
each meta.json "validation".
