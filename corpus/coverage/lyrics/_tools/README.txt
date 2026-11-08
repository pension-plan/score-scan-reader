Coverage suite - LAYOUTS family generator (corpus/coverage/layouts/<id>/, manifest ../manifest.json)

Rebuild everything (parallel, ~20 s on 192 cores), then validate independently:
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/layouts/_tools/run_all.py [id-substring ...] [--keep-work]
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/layouts/_tools/validate_layouts.py
Count symbols of ANY MusicXML file (truth or converter output; python stdlib only):
  python3 corpus/coverage/layouts/_tools/count_symbols.py file.musicxml [--json]

One clean exemplar per layout tag (melody has a 2nd, two-page cello variant; divisi has a strings and a
choir variant) = 20 items, each: engraving.ly, truth.musicxml (MusicXML 4.0, XSD + music21 checked),
clean.pdf (300 dpi raster), scan.pdf (typical scan, preset T1-T5), scan-severe.pdf (heavy damage, preset
S1-S5), meta.json, ATTRIBUTION.txt.  All music self-composed for this suite (CC0); Gloria text is the
public-domain Latin liturgy.

Code (csynth/ is a copy of corpus/challenge/layout/_tools/lsynth, extended; nothing outside this folder is
modified):
  csynth/model.py     score model (+ ornaments, fingering, arpeggio, breath; computed beams/stems/accidentals;
                      chord symbols on the score)
  csynth/dsl.py       note DSL (+ \trill \mordent \turn \arpeggio \breathe, -^ marcato, -! staccatissimo,
                      -N fingering, 64ths)
  csynth/notation.py  pre-pass deciding what truth and engraving must both show: printed staff of every event
                      (closed scores, cross-staff), explicit beam groups (per beat; vocal beaming = beams only
                      inside melismas) with level-2+ hooks, an explicit stem direction for every stemmed note
                      (multi-voice roles, chord/beam-group rule, kneed cross-staff beams), accidentals simulated
                      per part staff (truth) and per printed staff (expected print) in LilyPond's default style
  csynth/mxl.py       truth writer (+ <beam>, <stem>, <accidental> from the pre-pass, <harmony> with <offset>,
                      ornaments, technical/fingering, arpeggiate, breath-mark, nested part-groups incl. square)
  csynth/lily.py      LilyPond writer (+ \autoBeamOff with explicit [ ], explicit \stemUp/\stemDown, ChordNames,
                      nested staff groups, skips for tied notes in lyrics)
  csynth/cvlog.ly     grob logger (lilypond -dinclude-settings): every live NoteHead/Stem/Flag/Beam/Accidental/
                      Dots/Rest/Script/Slur/Tie/DynamicText/Hairpin/TextScript/LyricText/LyricHyphen/
                      LyricExtender (incl. whether drawn)/ChordName/TupletNumber/SustainPedal/BreathingSign/
                      Arpeggio/Fingering/SystemStart* after line breaking
  csynth/verify.py    grob log == model: note heads by (staff, onset, pitch), stems up/down by duration, flags,
                      beams, accidentals by (staff, onset, pitch, glyph), rests, scripts by onset, slurs, ties,
                      dynamics by (staff, onset), hairpins, lyrics by (onset, text), visible hyphens and
                      extenders, chord names by onset, tuplets, pedals, breaths, arpeggios, fingerings,
                      bracket/brace/square counts per system
  csynth/midicheck.py LilyPond MIDI (one track per Voice) == truth attack multiset
  csynth/degrade2.py  seeded scan damage (unchanged copy)
  count_symbols.py    taxonomy counter (rules in its docstring) -> meta.counts / meta.symbols
  build.py            per item: model -> pre-pass -> truth -> XSD -> music21 -> LilyPond (+grob log) -> MIDI
                      check, no warnings, planned page count, lyric text in PDF, grob check, no ink outside
                      the page margins -> clean/scan/scan-severe (image-only, verified) -> meta.json
  pieces/pNN_*.py     the 20 items (music, layout, expected result, truth limitations, damage presets)
  pieces/common.py    helpers + damage presets T1-T5 (typical) / S1-S5 (severe)
  chval.py            unmodified copy of corpus/challenge/_validate/validate.py (used by validate_layouts.py)
Logs: ../_logs/<id>.json (full build log incl. grob summary), ../_logs/validation-report.json
