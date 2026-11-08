Coverage corpus - STRUCTURE family (corpus/coverage/structure/<id>/, manifest ../manifest.json)

Rebuild all items in parallel (~70 s; the 12-page item dominates):
  /Users/d.sloane/music/.venv/bin/python corpus/coverage/structure/_tools/run_all.py [item-id ...] [--keep-work]
Logs with the full verification report per item: corpus/coverage/structure/_logs/<id>.json

Items (all compositions CC0, written for this corpus):
  str01-double-final-barlines        melody          1 p   7 double bars, 2 final bars (one mid-piece), 3 system breaks
  str02-repeat-signs-piano           piano           1 p   implied start repeat, start repeats at system starts, :|.|:
                                                           mid-system and split across a system break, end repeat at end
  str03-voltas-string-quartet        string-quartet  1 p   1st/2nd endings x3, a 3rd ending, a 2-bar ending broken
                                                           across a system break, open vs closed brackets
  str04-segno-coda-ds                melody          1 p   Segno, To Coda + coda sign, D.S. al Coda, Coda sign
  str05-fine-dc-al-fine-piano        piano           1 p   Fine on a mid-piece final bar, D.C. al Fine, Trio heading
  str06-breaks-two-pages-song        voice-piano     2 pp  irregular explicit system breaks, page break, 1st ending
                                                           across the page turn, ties across system/page breaks, 2 stanzas
  str07-orchestral-five-pages        orchestral      5 pp  7 staves, rehearsal marks A-D, Segno, Fine, D.S. al Fine,
                                                           1st ending across a page turn, tacet whole-bar rests
  str08-variations-twelve-pages-piano piano          12 pp 146 bars, repeats in every section, 2 volta variations,
                                                           key changes, To Coda (p.1) ... D.C. al Coda (p.11), Coda

Files per item: engraving.ly, truth.musicxml (MusicXML 4.0 partwise), clean.pdf (300 dpi lossless raster),
scan.pdf (typical 200-300 dpi office scan), scan-severe.pdf (heavy damage), meta.json, ATTRIBUTION.txt.

Code (copied from corpus/challenge/layout/_tools/lsynth and corpus/challenge/rhythm/_tools/rsynth/dump.ly and
extended; nothing outside this folder is used or modified):
  ssynth/model.py      score model (Event.beams added)
  ssynth/dsl.py        LilyPond-like note DSL
  ssynth/notation.py   NEW: explicit beaming (per beat unless the DSL gives [ ]) and explicit stem directions
                       for every stemmed note -> engraved with \autoBeamOff + \stemUp/\stemDown, written to the
                       truth as <beam number=n> and <stem>
  ssynth/mxl.py        truth writer (adds <beam>, no <stem> on whole notes, tuplet bracket="no" when beamed)
  ssynth/lily.py       LilyPond writer (adds \autoBeamOff everywhere, named Lyrics contexts, split repeat bar
                       glyphs ".|:-||" / ".|:-|." when a double/final bar ends a system before a start repeat,
                       and a lyric skip for every tied continuation note - without it LilyPond (with
                       melismaBusyProperties = '()) gives tied notes their own syllable and shifts the text)
  ssynth/verify.py     NEW: re-reads truth.musicxml (ElementTree) and compares it with what LilyPond engraved
  ssynth/counts.py     NEW: taxonomy symbol counts from truth.musicxml (rules in its docstring and meta.count_rules)
  ssynth/harmonize.py  4-part chorale solver (string quartet inner parts)
  ssynth/degrade2.py   scan damage simulator (seeded; params + per-page ops recorded in meta.degradations)
  ssynth/midicheck.py  LilyPond MIDI attacks == truth attacks
  dump.ly              event/grob dump engraver: per Voice notes, rests, full-bar rests, ties, beams, slurs,
                       articulations, dynamics, hairpins, pedal, text scripts; per Staff clefs, keys, time
                       signatures (only non-default = real changes); per Score bar-line glyphs per staff, volta
                       brackets with their start/end moments, segno/coda/text/rehearsal/metronome marks, explicit
                       stem directions, line/page break events
  breaks.ly            verification-only re-render with tagged bar numbers on every system; pdftotext -bbox per
                       page gives the measures that start each system on each page (must equal the <print> elements)
  build.py             one item: model -> truth -> XSD (mvp/work/schema/musicxml.xsd) -> music21 -> LilyPond (no
                       warnings allowed) -> verify -> MIDI -> page count -> rasters + damage -> image-only check ->
                       counts -> meta.json (planned focus counts are asserted)
  items/*.py           the 8 compositions, layouts, expected structure, truth limitations, damage plans + seeds

Volta bracket hooks: LilyPond 2.24 draws the closing hook of a volta bracket from the NAME of the bar line that
ends it (tested, also at line breaks): hooked for "|.", ":|.", ":|.|:", ".|:-|", ".|:-|." (truth
<ending type="stop">), open for "|", "||", ".|:", ".|:-||" (truth type="discontinue"). verify.py enforces it.

Counting (meta.counts): score-wide structure tags (bar styles, repeats, endings, jumps, breaks, rehearsal/tempo/
metronome marks, key/time signatures) are counted once per score position although MusicXML repeats bar lines
and endings in every part; all other tags are counted per element in every part (meta.counts_by_part splits
them by part). multi-page = number of pages. x-volta-3 = third ending, x-to-coda = "To Coda" instruction (its
coda glyph is also counted under coda).
