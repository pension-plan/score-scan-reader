Synthetic-scan corpus generator (corpus/synthetic/<id>/, manifest ../manifest-synthetic.json)

Rebuild everything (parallel, ~1 min):
  /Users/d.sloane/music/.venv/bin/python corpus/synthetic/_tools/run_all.py [item-id ...] [--keep-work]

Pipeline per item (synth/build.py):
  1. score model (synth/model.py) from the music21 corpus (synth/m21import.py, normalised:
     grace notes dropped, hidden rests -> spacers, pickups/split bars get real length,
     ties sanitised) or self-authored (synth/dsl.py + synth/harmonize.py voice-leading solver)
  2. truth.musicxml  <- synth/mxl.py   (MusicXML 4.0 partwise; validates against the W3C XSD)
  3. engraving.ly    <- synth/lily.py  (closed score: \voiceOne/\voiceTwo on shared staves +
     \lyricsto) or musicxml2ly (truth -> ly, post-processed); falls back to synth/lily.py
     when the musicxml2ly result does not match the truth
  4. validation: LilyPond MIDI (one track per Voice) must reproduce exactly the truth's
     (onset, pitch) attack multiset; no bar-check warnings; lyric syllables found in the
     vector PDF text
  5. pdftoppm -gray at 150/200/300 dpi -> synth/degrade.py (rotation, page curl/wave,
     perspective phone capture, paper texture, lighting gradient/vignette/gutter, bleed-
     through, blur, noise, salt&pepper, speckles, binarised photocopy, JPEG) ->
     scan.pdf (image-only, via img2pdf) and clean.pdf (undegraded raster, PNG)
  Item list, layouts and degradation parameters: synth/catalog.py, synth/items.py.
Per item files: scan.pdf, truth.musicxml, clean.pdf, engraving.ly, meta.json, ATTRIBUTION.txt
Build logs: corpus/synthetic/_logs/<id>.json
