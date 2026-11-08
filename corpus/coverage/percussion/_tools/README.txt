Coverage suite - PERCUSSION family generator (layout tag percussion-none; corpus/coverage/percussion/<id>/)

Rebuild (about 10 s), then validate with the suite-wide validator:
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/percussion/_tools/build.py [--keep-work]
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/_validate/validate.py --only percussion

Item perc01-parade-flute-snare-drumset (CC0): Flute (pitched, G major) + Snare Drum on a ONE-LINE staff
(percussion clef, accents, 16th groups) + Drum Set on a 5-line staff (percussion clef, two voices: hi-hat x
noteheads and snare stems up, bass drum stems down), 8 bars of 4/4 on 2 systems.

build.py is self-contained (the csynth writers of the other families have no unpitched notes): a small
LilyPond-like DSL -> truth.musicxml (MusicXML 4.0: <unpitched> display positions in treble-clef positions,
<instrument> -> <score-instrument>/<midi-instrument> with <midi-unpitched> (GM: bass drum 36, snare 38,
closed hi-hat 42; MusicXML counts from 1), <clef><sign>percussion</sign>, <staff-lines>1</staff-lines>,
<notehead>x</notehead>, explicit <stem> and <beam>) and engraving.ly (Staff + DrumStaff; drums-style table for
the kit, a custom one-line style table for the snare, explicit stems and beams, numeric 4/4).
Checks: XSD, music21, LilyPond without warnings, planned page count, LilyPond MIDI (drum channel) == truth
attacks via <midi-unpitched>, grob log (cvlog.ly copy with DrumStaff added and NoteHead style logged) == truth:
every note head (staff, onset, staff position, notehead style), every stem direction, rests, beams per staff,
accents, clefs, time-signature style; image-only PDFs.
Copied tools: degrade2.py (damage simulator), count_symbols.py (taxonomy counter, layouts family), cvlog.ly.
