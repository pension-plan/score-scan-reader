Coverage suite - LYRICS family generator (corpus/coverage/lyrics/<id>/, manifest ../manifest.json)

Rebuild (about 10 s), then validate with the suite-wide validator:
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/lyrics/_tools/run_all.py [id-substring ...] [--keep-work]
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/_validate/validate.py --only lyrics

Items (both layout melody-lyrics, one Voice part, CC0):
  lyr01-elisions-three-languages   3 numbered verses (Latin Gloria [public domain], Italian, Spanish), 11 lyric
                                   elisions (a~in, et~in, ta~e, da~il, ta~an, ra~u, ce~e, ta~y, ba~al, ta~o, y~el),
                                   melismas, hyphens, extenders, non-ASCII (Se-ñor, co-ra-zón)
  lyr02-non-ascii-four-languages   4 numbered verses in German, French, Spanish and Czech (8.7.8.7): 28 non-ASCII
                                   syllables (ä ö ü ß è â œ ñ ó í ¡ ¿ ř ů ...), melismas, hyphens, extenders

Code: a copy of corpus/coverage/layouts/_tools (csynth writers, grob logger, count_symbols.py, damage simulator),
extended (nothing outside this folder is modified):
  csynth/model.py  parse_lyric_text keeps '~' inside a syllable as a lyric elision (it used to become a space)
  csynth/mxl.py    lyric_body(): an elided syllable is ONE <lyric> with <syllabic>/<text> pairs separated by
                   <elision>‿</elision>; the first part keeps the hyphen to the previous syllable, the last part the
                   hyphen to the next (e.g. "Glo-ri-a~in": <syllabic>end</syllabic><text>a</text><elision/>
                   <syllabic>single</syllabic><text>in</text>)
  csynth/lily.py   unchanged: "a~in" is written as a quoted LilyPond syllable; LilyPond draws the tie glyph
  build.py         family 'lyrics'; item key engraving_only_counts adds tags MusicXML cannot encode (stanza-text:
                   the printed "1."-"4.") to meta.counts/symbols; they are also listed in printed_not_in_truth
  pieces/p01_elisions.py, pieces/p02_non_ascii.py   the two items
Build checks (per item, from build.py): XSD, music21, LilyPond without warnings, LilyPond MIDI == truth attacks,
every lyric syllable present in the vector PDF text, grob log == model (note heads, stems, beams, lyrics by
onset and text, visible hyphens and extenders, slurs, dynamics, hairpins), no ink outside the margins, image-only
PDFs. Logs: ../_logs/<id>.json
