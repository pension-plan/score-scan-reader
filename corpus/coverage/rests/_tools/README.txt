Coverage family "rests" generator (corpus/coverage/rests/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~10 s):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/rests/_tools/run_all.py [item-id ...] [--keep-work]
Independent re-check (XSD, music21, image-only PDFs, meta format, LilyPond MIDI vs truth, clean.pdf vs a
fresh render, rest accounting and count recomputation):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/rests/_tools/validate.py
  -> _logs/validate-report.json

Code (crest/) - copied from corpus/challenge/rhythm/_tools/rsynth (itself from corpus/synthetic/_tools/synth)
and extended; nothing outside this folder is used or modified:
  model.py    score model; + Event.display (rest drawn at a staff position), Event.stem (engraved stem
              direction), Event.display_auto, clef timeline / staff-position helpers
  rdsl.py     LilyPond-like DSL (absolute pitch); + pitched rests d''4\rest, r4\at=d'', R\at=g', R*n\at=g'
  lily.py     model -> engraving.ly; + pitched rests and MultiMeasureRest.staff-position overrides
  mxl.py      model -> truth.musicxml (MusicXML 4.0); + <rest><display-step/><display-octave/></rest>,
              <stem> for every stemmed note
  dump.ly     LilyPond event-dump engraver; + post-layout records of every Rest / MultiMeasureRest
              (staff-position, Y extent vs. the staff symbol) and every Stem (direction, note-head count)
  verify.py   event dump == model, MIDI == truth, music21 re-parse == model, XSD; + rest vertical
              positions == truth (glyph extent = base extent + staff-position/2), stem read-back, and
              read-back of rests LilyPond moved itself (rests under beams) into display-step/octave
  counts.py   taxonomy tag counts parsed from truth.musicxml (rules in its docstring and in
              manifest.json "counting_rules"); model cross-check for the rest tags
  scan.py     scan damage (unchanged copy): paper, texture, bleed, foxing, coffee, pencil, punch holes,
              crop, halftone, curl, rotation, perspective, lighting, blur, noise, speckle, binarize,
              downsampling, JPEG
  items.py    the 9 compositions (CC0)
  catalog.py  per item: layout tag, expected result, truth notes, minimum counts, damage variants
              (scan.pdf = typical scan, scan-severe.pdf = heavy damage; ops + seed)
  build.py    one item: engraving -> LilyPond (+dump) -> stems / moved rests read back -> truth ->
              verification (fails the item on any mismatch or LilyPond warning) -> counts -> clean.pdf
              (300 dpi) -> scans -> image-only check -> meta.json + ATTRIBUTION.txt
validate.py   copy of corpus/challenge/_validate/validate.py adapted to the coverage meta format
Logs with the full verification reports: corpus/coverage/rests/_logs/<id>.json

Rest position convention (truth): <display-step>/<display-octave> = the pitch whose staff position the
rest takes; the middle line is the normal position for every rest value (a whole rest at display B4 in
treble clef hangs from the 4th line as usual).  Rests without display-step are at the normal position.
