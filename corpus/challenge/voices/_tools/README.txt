challenge/voices generator (corpus/challenge/voices/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~1 min):
  /Users/d.sloane/music/.venv/bin/python corpus/challenge/voices/_tools/run_all.py [item-id ...] [--keep-work]

Code (copied from corpus/synthetic/_tools/synth and extended; originals untouched):
  vsynth/model.py      score model (+ engraving directives: hidden = in truth but printed by a carrier
                       voice (a 2 / unis.), nostem = unison drawn with one head + one stem, words, raw)
  vsynth/dsl.py        note DSL (+ chords, s spacer, R full-bar rest, @lower/@upper staff change,
                       @v0-4 voice roles, ^"text" words, \hide, \nostem)
  vsynth/mxl.py        truth.musicxml writer (MusicXML 4.0 partwise, + <words> directions)
  vsynth/lily.py       LilyPond writer (closed score, role overrides for cross-staff, timed lyric
                       lines that switch voice)
  vsynth/harmonize.py  voice-leading solver (ranges configurable), vlcheck.py = dev aid
  vsynth/midicheck.py  per-Voice MIDI track == printed truth voice; MIDI lyric events == truth;
                       hidden notes must have an identical printed carrier on the same staff
  vsynth/degrade2.py   RGB damage simulator (ops listed in each meta.json, seeded)
  vsynth/build.py      per item: truth (xmllint XSD + music21 re-parse) -> engraving -> checks ->
                       clean.pdf (300 dpi PNG raster) + scan*.pdf (image only, verified)
  vsynth/items.py      the 7 items (own CC0 music on public-domain texts) + damage recipes
