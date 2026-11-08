Pitch challenge items (corpus/challenge/pitch/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~30 s):
  /Users/d.sloane/music/.venv/bin/python corpus/challenge/pitch/_tools/run_all.py [item-id ...] [--keep-work] [--no-damage]

Code (pk/) is copied from corpus/synthetic/_tools/synth and extended:
  model.py      score model (+ forced/cautionary accidentals, ottava events, explicit line/page breaks)
  dsl2.py       LilyPond-like note DSL (\clef= \ottava= \key= \bar= \break \pagebreak, pitch! pitch?)
  harmonize2.py SATB/TTBB voice-leading solver (+ ger6/it6/dim7/aug chords, configurable ranges)
  acc.py        accidental display simulator = LilyPond 2.24 'default' style, determined empirically:
                state per STAFF (shared by all voices on it), same octave only, reset at barlines,
                simultaneous notes judged against the state before the moment, tie continuations
                print nothing and do not update the state (except at a system start), '!' forced,
                '?' parenthesised, extraNatural (x -> # prints natural-sharp, bb -> b natural-flat)
  mxl.py        truth.musicxml writer (MusicXML 4.0; <accidental> from acc.py per *part*,
                <key><cancel>, <octave-shift> with sounding pitches, clef-octave-change)
  lily.py       LilyPond writer (+ instrumented twin: grob logger + coloured note heads)
  rendercheck.py  truth-vs-render: printed accidentals / clefs / key signatures + cancellations /
                ottava spans from the instrumented LilyPond run vs acc.py on the *engraved* staves
  midicheck.py  MIDI reader; build.py also re-reads truth.musicxml with an independent XML reader
                and requires its (onset, pitch) multiset == LilyPond MIDI
  scanfx.py     RGB damage pipelines (paper colour/texture/bleed, coffee ring, foxing, pencil marks
                anchored on real note heads, punch holes, staple, crop through staff ends, page curl,
                gutter, rotation incl. 90/180, scale, 2-up spread, phone perspective, lighting,
                focus/motion blur, halftone moire, noise, salt-and-pepper, binarised photocopy, JPEG)
  items.py      the music (all self-composed, CC0; texts public domain)
  catalog.py    edge-case tags, expected-result notes, damage recipes (params + seeds)
Every item must pass: xmllint XSD, MIDI == truth file, render check, lyric text in vector PDF,
no bar-check warnings, instrumented twin has identical layout, every scan*.pdf image-only.
