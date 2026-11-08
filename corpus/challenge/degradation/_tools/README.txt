Degradation-extremes challenge set (corpus/challenge/degradation/<id>/, manifest ../manifest.json)

Rebuild everything (parallel, ~40 s on 192 cores):
  /Users/d.sloane/music/.venv/bin/python corpus/challenge/degradation/_tools/run.py [--pieces] [id-substring ...]
  (DEG_THUMBS=<dir> also writes JPEG previews of every damaged file for visual QA)

4 simple source pieces (pieces.py) x 21-22 damage types (variants.py) = 85 items.  Every item
of a piece shares the same truth.musicxml / engraving.ly (built once into ../_pieces/<piece>/ by
build_piece.py and validated: MIDI attack multiset == truth, MIDI lyric events == truth lyrics
(every verse), every syllable present in the vector PDF, XSD-valid truth, no LilyPond warnings).

Per item: scan.pdf (damaged, image-only), scan-mild.pdf / scan-severe.pdf (same page, lighter /
heavier damage; all items except the 4 clean controls, which have scan-mild only), clean.pdf
(undamaged raster at the scan dpi), truth.musicxml, engraving.ly, meta.json, ATTRIBUTION.txt.
meta.json.degradations lists, per file, every damage step with its parameters, the seed, dpi, the
output encoding, and (for stain/pencil items) the position of every handwritten mark.

Code: synth/ is a copy of corpus/synthetic/_tools/synth (score model, MusicXML writer, LilyPond
writer, MIDI check; dsl.py patched to accept chords); damage.py is the RGB damage engine
(numpy + Pillow); run.py renders, damages, verifies (pdffonts/pdfimages/pdftotext) and writes
meta + manifest.
