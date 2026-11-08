coverage/notes generator (corpus/coverage/notes/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~15 s):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/notes/_tools/run_all.py [item-id ...] [--keep-work]
Independent check (XSD, music21, image-only PDFs, LilyPond MIDI vs truth, clean.pdf vs fresh render,
meta fields, counts re-read from truth):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/notes/_tools/validate_notes.py   (report: ../_logs/validate_report.json)

nsynth/ is a copy of corpus/challenge/rhythm/_tools/rsynth (itself from corpus/synthetic/_tools/synth), extended:
  model.py    + explicit stem per note (assign_positions_and_stems), staff positions / ledger lines,
              cue notes, single- and two-note tremolos, secondary-beam breaks, words above notes
  rdsl.py     + \stemUp/\stemDown/\stemNeutral, c4:16, \trem N { a16 b16 }, \sb, ^"text", voice cue=True
  lily.py     + forced \stemUp/\stemDown, :N tremolos, \repeat tremolo, stemLeft/RightBeamCount, CueVoice
  mxl.py      + <stem> on every stemmed note, <cue/> + <type size="cue">, <tremolo>, beam levels over rests
  dump.ly     + Stem/NoteHead grobs of the final layout (direction, beams left/right, flags, tremolo strokes,
              staff position, font size) and printed accidentals
  verify.py   + grob and accidental comparison, counts measured on the engraving
  counts.py   symbol counts read back from truth.musicxml (rules in COUNT_RULES / meta.count_rules)
  items.py    the 10 pieces (CC0);  catalog.py  tags, expected results, truth notes, damage recipes + seeds
  scan.py     damage engine (unchanged copy of rsynth/scan.py)
Every item must pass: XSD, music21 re-parse == model, LilyPond event dump == model, Stem/NoteHead grobs ==
model, printed accidentals == truth, MIDI attacks == truth, counts(truth) == counts(engraving), no LilyPond
warnings, page count, every PDF image-only.  Logs: corpus/coverage/notes/_logs/<id>.json
