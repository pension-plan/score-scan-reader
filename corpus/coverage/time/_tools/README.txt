Coverage suite, family "time" (corpus/coverage/time/<id>/, manifest ../manifest.json)

Rebuild everything (parallel, ~1 min):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/time/_tools/run_all.py [item-id ...] [--keep-work]
Independent validation (XSD, music21, image-only PDFs, LilyPond MIDI vs truth, clean.pdf vs fresh
render, meta keys, independent re-count of time/tuplet/tie/pickup tags):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/time/_tools/validate.py --jobs 20

Code: tsynth/ is a copy of corpus/challenge/rhythm/_tools/rsynth (itself from corpus/synthetic/_tools/synth);
validate.py is a copy of corpus/challenge/_validate/validate.py.  Nothing outside corpus/coverage/time is
modified.  Changes against the rhythm copy:
  model.py / rdsl.py   nested \tuplet groups (Event.tup_levels / tup_starts / tup_stops, product ratio)
  mxl.py               nested tuplets in MusicXML (time-modification = product, numbered <tuplet> per level
                       with tuplet-actual/-normal); bracket yes/no by LilyPond 2.24's Tuplet_bracket rule
  lily.py              nested \tuplet emission
  dump.ly / verify.py  every printed TupletBracket logged by a stencil callback (onset, ratio, visible) and
                       compared with the truth bracket attribute; ties written inside chords (<f' a'~>) logged
                       per note; music21 nested-ratio comparison
  counts.py            taxonomy counts read back from truth.musicxml (rules in COUNT_RULES -> meta.counting_rules)
  items.py / catalog.py the 10 CC0 pieces, layout tags, target symbols, expected results, damage variants
  build.py             coverage meta.json (family, symbols, layout, counts, count_locations, notes, ...)
An item fails the build on any mismatch: XSD, event dump vs truth, MIDI vs truth, music21 re-parse,
tuplet brackets, LilyPond warnings, page count.
