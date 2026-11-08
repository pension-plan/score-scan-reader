Synthetic coverage suite, family "marks" (corpus/coverage/marks/<id>/, manifest ../manifest.json)

Rebuild (parallel, about 15 s):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/marks/_tools/run_all.py [id-substring ...] [--keep-work]

Items: articulations (staccato, staccatissimo, accent, tenuto, marcato, portato), ornaments (trill, mordent,
inverted mordent, turn, inverted turn), fermatas, breath marks, every dynamic and hairpins, sustain pedal,
arpeggios, fingering (single notes and stacked on chords), text expressions, tempo + metronome marks,
rehearsal marks, chord symbols (lead sheet), in melody / piano / voice-piano / string-quartet / lead-sheet
layouts.  All music composed for this corpus, CC0.

Code (msynth/, new; ideas and the damage engine come from corpus/challenge/rhythm/_tools/rsynth, nothing
outside this folder is used or modified):
  model.py   score model + LilyPond-like note DSL with every mark as a postfix (see its docstring), chord-symbol
             DSL, hairpin / slur / beam / pedal / tie balance checks, LilyPond-default accidental display
  lily.py    model -> engraving.ly (\autoBeamOff + manual beams, \autoLineBreaksOff + explicit \break,
             ChordNames for chord symbols, boxed rehearsal letters)
  dump.ly    LilyPond event + grob dump (-dinclude-settings): every Voice music event, tempo / mark events,
             ChordNames pitches, every grob created, and the final direction of every Stem / Script / Fingering
  verify.py  engraving vs model (event multiset on exact moments, grob census per kind, printed accidentals,
             chord-name pitch classes), stem + mark-side read-back into the truth, MIDI attacks == truth,
             music21 re-parse == model, xmllint against mvp/work/schema/musicxml.xsd
  mxl.py     model -> truth.musicxml (MusicXML 4.0; encoding conventions in its docstring and in meta.notes)
  count.py   taxonomy symbol counter that reads truth.musicxml only (rules in its docstring = meta.counting_rules);
             build.py requires its marks counts to equal counts taken from the model
  scan.py    RGB scan / photocopy / phone damage (copy of rsynth/scan.py), midi.py MIDI reader (copy)
  items.py   the 9 pieces, focus tags, expected-result notes, damage recipes (params + seed)
  build.py   one item end to end; fails the item on any mismatch, LilyPond warning or non-image-only PDF
Build logs with the full verification reports: corpus/coverage/marks/_logs/<id>.json
