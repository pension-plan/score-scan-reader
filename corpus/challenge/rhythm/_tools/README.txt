Rhythm challenge corpus generator (corpus/challenge/rhythm/<id>/, manifest ../manifest.json)

Rebuild (parallel, ~20 s):
  /Users/d.sloane/music/.venv/bin/python corpus/challenge/rhythm/_tools/run_all.py [item-id ...] [--keep-work]

Code (rsynth/) - copied from corpus/synthetic/_tools/synth and extended, nothing outside this folder is used
or modified:
  model.py    score model (+ grace notes, explicit beams, implied tuplets, multi-bar rests, rehearsal
              marks / words, forced system and page breaks)
  rdsl.py     LilyPond-like DSL the 8 pieces are written in (absolute pitch, \time / \tuplet / \grace /
              \acc / \app / R*n ...); checks every bar length
  mxl.py      model -> truth.musicxml (MusicXML 4.0; beams with hooks, <grace/>, <multiple-rest>,
              <print new-system/new-page>, tuplet bracket/show-number as engraved)
  lily.py     model -> engraving.ly (\autoBeamOff + manual beams, \autoLineBreaksOff + explicit
              \break/\pageBreak so system breaks are known exactly)
  dump.ly     LilyPond event-dump engraver used for verification (-dinclude-settings)
  verify.py   engraving vs truth: event dump (onset, pitch, type, dots, tuplet scale, grace offsets,
              ties, beams, slurs, fermatas, lyric syllables/hyphens/extenders, bar numbers, measure
              positions, time signatures) == model; LilyPond MIDI attacks == truth; music21 re-parse
              of truth.musicxml == model; xmllint against mvp/work/schema/musicxml.xsd
  scan.py     scan damage (numpy + Pillow; ideas from synth/degrade.py and
              spike/classical/tools/degrade.py): RGB/yellowed paper, texture, bleed-through, foxing,
              coffee stains, pencil marks, punch holes, staples, crop, halftone moire, curl, gutter,
              rotation (any angle, 90/180), perspective, scale mismatch, lighting, focus/motion blur,
              gaussian / salt-pepper noise, speckle, binarised photocopy, downsampling, 2-up spreads,
              JPEG.  Damage never removes music: crops stay in the margin / staff-end region and
              punch holes are moved into gaps between systems.
  items.py    the 8 compositions (CC0) and their layouts
  catalog.py  per item: edge-case tags, expected conversion result, truth limitations, licence,
              damage variants (scan.pdf, scan-mild.pdf, scan-severe.pdf: ops + seed)
  build.py    one item: truth -> engraving -> verification (fails the item on any mismatch or
              LilyPond warning) -> clean.pdf (300 dpi raster) -> damaged scans -> image-only check
              (pdffonts / pdfimages / pdftotext) -> meta.json + ATTRIBUTION.txt
Logs with the full verification reports: corpus/challenge/rhythm/_logs/<id>.json
