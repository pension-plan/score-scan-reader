Layout-challenge corpus generator (corpus/challenge/layout/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~70 s):
  /Users/d.sloane/music/.venv/bin/python corpus/challenge/layout/_tools/run_all.py [item-id ...] [--keep-work]

Code (copied from corpus/synthetic/_tools/synth and extended; nothing outside this folder is modified):
  lsynth/model.py     score model + cross-staff, cue, stem, words, pedal, hairpin, hidden-rest fields;
                      measure-level voltas, segno/coda/D.S./D.C./Fine marks, system/page breaks, staff sizes
  lsynth/dsl.py       note DSL (chords, \st1/\st2 cross-staff, \cueOn, \tup3/2, ^"words", \sustainOn, \< \!, [ ])
  lsynth/mxl.py       truth writer (MusicXML 4.0: credits, part-groups, part-symbol, staff-details, print,
                      ending, sound segno/coda/tocoda/dalsegno/dacapo/fine, metronome, pedal, wedge, cue)
  lsynth/lily.py      LilyPond writer (multiple \score segments e.g. a smaller Amen, forced breaks, voltas,
                      text marks, cross-staff \change Staff, cue size, explicit stems)
  lsynth/midicheck.py MIDI (one track per Voice, one file per \score) vs truth attack multiset
  lsynth/degrade2.py  scan/photocopy/phone damage (RGB): skew, 90/180 page rotation, scale mismatch,
                      perspective/keystone, curl, gutter, 2-up spreads, lighting, vignette, paper colour/texture,
                      bleed-through, coffee/foxing, pencil annotations, punch holes, staple, ink-aware crop,
                      halftone moire, focus/motion blur, noise, salt&pepper, speckles, binarisation, JPEG, dpi
  build.py            per item: truth -> XSD (xmllint) -> music21 parse -> LilyPond -> MIDI check -> page count
                      -> lyric syllables in PDF text -> raster -> scan.pdf / scan-mild.pdf / scan-severe.pdf /
                      clean.pdf (image-only, img2pdf) -> meta.json, ATTRIBUTION.txt
  pieces/*.py         the 7 items; pieces/__init__.py holds the damage plans (params + seeds)
Build logs: corpus/challenge/layout/_logs/<id>.json
