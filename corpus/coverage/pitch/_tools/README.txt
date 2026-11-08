Coverage suite, pitch family (corpus/coverage/pitch/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~10 s on this machine):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/pitch/_tools/run_all.py [item-id ...] [--keep-work] [--no-damage]
Independent validation (fresh LilyPond render, MIDI vs truth, clean.pdf pixel compare, XSD, music21, meta schema):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/pitch/_tools/validate_cov.py [--jobs N]
  -> _logs/validate-report.json

Code (cvp/) is copied from corpus/challenge/pitch/_tools/pk (not modified there) and extended:
  items.py     the music (12 items, all self-composed, CC0; key tours generated from spelled scales)
  catalog.py   focus tags, layout tag, expectations, truth notes, damage recipes (params + seeds) per item
  dsl2.py      + multi-staff parts (piano / organ: one voice per staff, keys 1 / 5 / 9), chords <..> fixed
  lily.py      + instrumentation of Stem (direction, beaming, flag, heads), NoteHead (staff-position),
               ClefModifier, TimeSignature, BarLine, OttavaBracket text/direction; ottava_style option
  rendercheck  + clef octave modifiers, ottava type/text/direction, time signatures, double/final barlines,
               annotate_stems(): engraved stem directions and beams (begin/continue/end/hooks) -> model
  mxl.py       + <stem>, <beam>, <print new-system/new-page> (explicit breaks only), octave-shift numbered per staff
  counts.py    taxonomy counter: every meta.counts tag is recomputed from truth.musicxml itself
               (conventions in counts.CONVENTIONS, copied into each meta.json)
  build.py     engrave + instrumented twin -> render check -> stems/beams into the model -> truth.musicxml
               -> xmllint XSD, music21 parse, LilyPond MIDI == truth attacks, truth counts == engraving
               (accidental glyphs, double/extra-natural/parenthesised accidentals, stems up/down, flags,
               beam groups, clef changes, system breaks, every notehead's staff position incl. ledger lines),
               twin layout identity (1 px tolerance) -> clean.pdf (300 dpi) + scan.pdf (typical) +
               scan-severe.pdf (heavy damage, scanfx.py, seeded) -> meta.json, ATTRIBUTION.txt
Every system break is explicit (\break) and checked against the render, so <print new-system> is exact.
