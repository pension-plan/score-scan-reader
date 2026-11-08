# Coverage suite: every common notation symbol and score layout, with exact truth

102 items in 10 families, 306 image-only PDFs (102 clean rasters + 204 damaged scans). Each item is a short piece (mostly 4-16 bars; the `perf` and `structure` families add 2-40 page scores) written so that the target symbols are isolated, frequent and countable. All 139 taxonomy symbol tags and all 19 layout tags have at least one item. All music is composed for the suite (CC0) or public domain (Latin Gloria, Watts 1719, Blake 1794).

Validation (`_validate/validate.py`, re-run from the published files): **102/102 items pass**. See [Validation](#validation).

## Files of an item

`<family>/<id>/` holds:

| file | content |
|---|---|
| `engraving.ly` | LilyPond 2.24 source |
| `truth.musicxml` | exact truth, MusicXML 4.0 partwise, XSD-valid (`mvp/work/schema/musicxml.xsd`), parses in music21 |
| `clean.pdf` | undamaged image-only raster of the engraving (300 dpi; the perf DPI set uses its own dpi) |
| `scan.pdf` | typical 200-300 dpi scan: slight skew, noise, paper tint, JPEG |
| `scan-severe.pdf` | heavy damage: binarised photocopies, phone photos, 100-150 dpi, stains, curl, spreads, rotation |
| `meta.json` | `id, family, title, symbols[], layout, expected{parts[], must_not_split}, counts{tag: n}, degradations{file: params + seed}, dpi, pages, license, notes[]` (truth limitations), plus family-specific detail (count rules, focus symbols, generator validation) |
| `ATTRIBUTION.txt` | sources and licence |

`manifest.json` here merges all families: per item a trimmed meta object plus `path`, `scan_files`, `eval_ids` (ids used by `eval.mjs --set coverage`), `pdf` (pages and image resolution per file) and `validation_coverage`; at the top `symbol_coverage`, `layout_coverage`, `x_tags`, `missing_tags`, `missing_layouts`. Each family also keeps its own `<family>/manifest.json` and its generator in `<family>/_tools/`.

## Families

| family | items | PDFs | pages (clean) | focus | rebuild |
|---|---:|---:|---:|---|---|
| notes | 10 | 30 | 10 | Note values breve-64th, dots and double dots, chords up to 6 notes, beams (groups, hooks, over rests), flags, stems, ledger lines to 5 above/below, grace notes (slashed, beamed, chords), cue notes, tremolos. | `notes/_tools/` |
| rests | 9 | 27 | 9 | Every rest value breve-64th, dotted rests, whole-bar rests in simple and compound meters, multi-bar rests (H-bar and old-style symbols), rests in two-voice staves, piano and quartet, rests inside tuplets and beams. | `rests/_tools/` |
| pitch | 12 | 36 | 12 | All 8 clefs and clef changes, all 15 major and 15 minor key signatures and key changes, every accidental incl. double sharps/flats and courtesy accidentals, 8va/8vb/15ma lines vs ledger lines. | `pitch/_tools/` |
| time | 10 | 30 | 11 | All simple, compound and irregular meters, C and cut time, meter changes, pickups, triplets to septuplets, duplets/quadruplets, nested tuplets, ties across barlines, systems and pages. | `time/_tools/` |
| marks | 9 | 27 | 9 | Articulations, ornaments, fermatas, breath marks, every dynamic and hairpin, pedal, arpeggios, fingering, tempo/metronome marks, text expressions, rehearsal marks, chord symbols. | `marks/_tools/` |
| structure | 8 | 24 | 24 | Double and final barlines, repeats, 1st/2nd/3rd endings, segno/coda/D.S./D.C./Fine, system and page breaks, multi-page scores up to 12 pages. | `structure/_tools/` |
| lyrics | 2 | 6 | 2 | Lyric elisions (two syllables on one note), non-ASCII lyrics in four languages (German, French, Spanish, Czech), numbered multi-verse lyrics, hyphens, extenders, melismas. | `lyrics/_tools/` |
| layouts | 20 | 60 | 22 | One exemplar per score layout: melody, song, piano, voice+piano, five choir layouts, choir+piano, organ, quartet, orchestra, lead sheet, hymnal, divisi, cross-staff, two voices on one staff. | `layouts/_tools/` |
| percussion | 1 | 3 | 1 | Percussion layout (percussion-none): one-line snare staff and 5-line drum set (percussion clef, x noteheads, two voices) beside a pitched melody. | `percussion/_tools/` |
| perf | 21 | 63 | 92 | Speed/memory sets: one hymn page and one piano page at 100-600 dpi and on Letter/A4/A3, and a piano book of 1, 5, 10, 20 and 40 pages (identical pages across books). | `perf/_tools/` |
| **total** | **102** | **306** | **192** | | |

Rebuild a family with `/Users/d.sloane/music/.venv/bin/python corpus/coverage/<family>/_tools/run_all.py` (`percussion`: `_tools/build.py`); each `_tools/README.txt` explains its generator and its own engraving checks. Then re-run `_validate/validate.py` and `_validate/build_index.py`.

## Symbol coverage

Items = items whose `meta.symbols` lists the tag; occurrences = sum of `meta.counts`. Counting conventions differ slightly between families (see [Counting conventions](#counting-conventions)), so occurrences are indicative; `tools/coverage.mjs` re-counts every tag from the truth with one tagger for the app scores.

### notes

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `note-breve` | 3 | 29 | `notes/nt01-note-values`, `rests/rst03-whole-bar-rests-simple`, `perf/perf-pages-40` |
| `note-whole` | 50 | 512 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `note-half` | 96 | 4857 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `note-quarter` | 101 | 11462 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `note-8th` | 81 | 9382 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `note-16th` | 34 | 2464 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `note-32nd` | 21 | 709 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt04-beams` |
| `note-64th` | 16 | 123 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt05-flags-stems` |
| `dot` | 69 | 1513 | `notes/nt02-dots`, `notes/nt10-piano-etude`, `rests/rst02-dotted-rests` |
| `double-dot` | 12 | 23 | `notes/nt02-dots`, `notes/nt10-piano-etude`, `rests/rst02-dotted-rests` |
| `chord` | 42 | 4333 | `notes/nt02-dots`, `notes/nt03-chords`, `notes/nt06-ledger-lines` |
| `beam` | 68 | 3452 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt03-chords` |
| `flag` | 51 | 649 | `notes/nt01-note-values`, `notes/nt05-flags-stems`, `notes/nt10-piano-etude` |
| `stem-up` | 88 | 6550 | `notes/nt01-note-values`, `notes/nt03-chords`, `notes/nt04-beams` |
| `stem-down` | 93 | 16719 | `notes/nt01-note-values`, `notes/nt03-chords`, `notes/nt04-beams` |
| `ledger-above` | 79 | 5241 | `notes/nt06-ledger-lines`, `notes/nt10-piano-etude`, `pitch/pitch-cov-clef-changes-piano` |
| `ledger-below` | 66 | 1128 | `notes/nt06-ledger-lines`, `notes/nt10-piano-etude`, `pitch/pitch-cov-clef-changes-piano` |
| `grace` | 14 | 252 | `notes/nt07-grace-notes`, `notes/nt10-piano-etude`, `perf/perf-pages-05` |
| `grace-slash` | 14 | 114 | `notes/nt07-grace-notes`, `notes/nt10-piano-etude`, `perf/perf-pages-05` |
| `cue-note` | 1 | 24 | `notes/nt08-cue-notes` |
| `tremolo` | 11 | 163 | `notes/nt09-tremolos`, `perf/perf-pages-20`, `perf/perf-pages-40` |

### rests

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `rest-breve` | 2 | 7 | `rests/rst01-rest-values`, `perf/perf-pages-40` |
| `rest-whole` | 4 | 11 | `rests/rst01-rest-values`, `perf/perf-pages-10`, `perf/perf-pages-20` |
| `rest-half` | 25 | 59 | `rests/rst01-rest-values`, `rests/rst07-piano-rests`, `rests/rst09-quartet-rests` |
| `rest-quarter` | 45 | 224 | `rests/rst01-rest-values`, `rests/rst07-piano-rests`, `rests/rst09-quartet-rests` |
| `rest-8th` | 24 | 148 | `rests/rst01-rest-values`, `rests/rst07-piano-rests`, `rests/rst09-quartet-rests` |
| `rest-16th` | 15 | 68 | `rests/rst01-rest-values`, `rests/rst07-piano-rests`, `notes/nt04-beams` |
| `rest-32nd` | 7 | 102 | `rests/rst01-rest-values`, `rests/rst07-piano-rests`, `rests/rst02-dotted-rests` |
| `rest-64th` | 4 | 30 | `rests/rst01-rest-values`, `perf/perf-pages-10`, `perf/perf-pages-20` |
| `rest-dotted` | 14 | 38 | `rests/rst02-dotted-rests`, `rests/rst07-piano-rests`, `rests/rst09-quartet-rests` |
| `rest-whole-bar` | 21 | 123 | `notes/nt08-cue-notes`, `rests/rst03-whole-bar-rests-simple`, `rests/rst04-whole-bar-rests-compound` |
| `rest-multibar` | 1 | 9 | `rests/rst05-multibar-rests` |

### pitch

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `clef-treble` | 92 | 157 | `pitch/pitch-cov-clef-changes-piano`, `pitch/pitch-cov-clefs-all`, `pitch/pitch-cov-clefs-quartet` |
| `clef-bass` | 66 | 115 | `rests/rst09-quartet-rests`, `pitch/pitch-cov-clef-changes-piano`, `pitch/pitch-cov-clefs-all` |
| `clef-alto` | 14 | 19 | `rests/rst04-whole-bar-rests-compound`, `rests/rst09-quartet-rests`, `pitch/pitch-cov-clefs-all` |
| `clef-tenor` | 4 | 10 | `pitch/pitch-cov-clefs-all`, `pitch/pitch-cov-clefs-quartet`, `layouts/melody-cello-elegy-2page` |
| `clef-soprano` | 2 | 6 | `pitch/pitch-cov-clefs-all`, `perf/perf-pages-40` |
| `clef-treble-8vb` | 6 | 10 | `pitch/pitch-cov-clefs-all`, `time/t09-two-voices-guitar`, `layouts/choir-open-satb-gloria` |
| `clef-treble-8va` | 2 | 6 | `pitch/pitch-cov-clefs-all`, `perf/perf-pages-40` |
| `clef-bass-8vb` | 2 | 5 | `pitch/pitch-cov-clefs-all`, `perf/perf-pages-40` |
| `clef-change` | 14 | 101 | `pitch/pitch-cov-clef-changes-piano`, `pitch/pitch-cov-clefs-all`, `pitch/pitch-cov-clefs-quartet` |
| `key-0` | 42 | 47 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps` |
| `key-s1` | 26 | 32 | `pitch/pitch-cov-accidentals-melody`, `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps` |
| `key-s2` | 12 | 18 | `pitch/pitch-cov-clefs-quartet`, `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps` |
| `key-s3` | 9 | 15 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps` |
| `key-s4` | 14 | 15 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps` |
| `key-s5` | 4 | 5 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps` |
| `key-s6` | 6 | 8 | `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps`, `perf/perf-pages-05` |
| `key-s7` | 5 | 8 | `pitch/pitch-cov-keys-major-sharps`, `pitch/pitch-cov-keys-minor-sharps`, `perf/perf-pages-10` |
| `key-f1` | 15 | 19 | `pitch/pitch-cov-clef-changes-piano`, `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-flats` |
| `key-f2` | 9 | 11 | `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats`, `marks/mk06-lead-sheet-chord-symbols` |
| `key-f3` | 25 | 27 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats` |
| `key-f4` | 15 | 17 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats` |
| `key-f5` | 4 | 6 | `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats`, `perf/perf-pages-20` |
| `key-f6` | 5 | 7 | `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats`, `perf/perf-pages-10` |
| `key-f7` | 6 | 9 | `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-minor-flats`, `perf/perf-pages-05` |
| `key-change` | 18 | 129 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-flats`, `pitch/pitch-cov-keys-major-sharps` |
| `acc-sharp` | 35 | 411 | `notes/nt03-chords`, `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `acc-flat` | 26 | 51 | `notes/nt03-chords`, `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `acc-natural` | 30 | 356 | `notes/nt03-chords`, `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody` |
| `acc-double-sharp` | 15 | 124 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody`, `pitch/pitch-cov-keys-minor-sharps` |
| `acc-double-flat` | 10 | 13 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody`, `perf/perf-piano-a3-300dpi` |
| `acc-courtesy` | 14 | 39 | `pitch/pitch-cov-accidentals-chords-piano`, `pitch/pitch-cov-accidentals-melody`, `perf/perf-pages-05` |
| `ottava-8va` | 13 | 21 | `pitch/pitch-cov-ottava-ledger-melody`, `pitch/pitch-cov-ottava-piano`, `perf/perf-pages-10` |
| `ottava-8vb` | 13 | 20 | `pitch/pitch-cov-ottava-ledger-melody`, `pitch/pitch-cov-ottava-piano`, `perf/perf-pages-10` |
| `ottava-15ma` | 3 | 5 | `pitch/pitch-cov-ottava-ledger-melody`, `pitch/pitch-cov-ottava-piano`, `perf/perf-pages-40` |

### time

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `time-2-4` | 13 | 21 | `rests/rst03-whole-bar-rests-simple`, `time/t01-simple-meters`, `time/t04-pickup-song` |
| `time-3-4` | 45 | 60 | `rests/rst03-whole-bar-rests-simple`, `time/t01-simple-meters`, `time/t04-pickup-song` |
| `time-4-4` | 58 | 86 | `rests/rst03-whole-bar-rests-simple`, `time/t01-simple-meters`, `time/t03-common-cut-piano` |
| `time-2-2` | 3 | 5 | `time/t01-simple-meters`, `time/t03-common-cut-piano`, `perf/perf-pages-40` |
| `time-3-2` | 6 | 8 | `rests/rst03-whole-bar-rests-simple`, `time/t01-simple-meters`, `notes/nt02-dots` |
| `time-6-8` | 27 | 34 | `rests/rst04-whole-bar-rests-compound`, `time/t02-compound-irregular`, `time/t04-pickup-song` |
| `time-9-8` | 6 | 8 | `rests/rst04-whole-bar-rests-compound`, `time/t02-compound-irregular`, `time/t05-triplets-duplets` |
| `time-12-8` | 6 | 8 | `rests/rst04-whole-bar-rests-compound`, `time/t02-compound-irregular`, `time/t05-triplets-duplets` |
| `time-5-4` | 4 | 5 | `rests/rst03-whole-bar-rests-simple`, `time/t01-simple-meters`, `perf/perf-pages-20` |
| `time-5-8` | 4 | 8 | `rests/rst04-whole-bar-rests-compound`, `time/t02-compound-irregular`, `time/t10-quartet-meters` |
| `time-7-8` | 5 | 10 | `rests/rst04-whole-bar-rests-compound`, `time/t02-compound-irregular`, `time/t10-quartet-meters` |
| `time-common` | 19 | 25 | `rests/rst03-whole-bar-rests-simple`, `time/t03-common-cut-piano`, `time/t06-quint-sext-sept` |
| `time-cut` | 15 | 20 | `rests/rst03-whole-bar-rests-simple`, `time/t03-common-cut-piano`, `time/t05-triplets-duplets` |
| `time-change` | 32 | 190 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano` |
| `pickup` | 17 | 17 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano` |
| `tuplet-3` | 19 | 412 | `rests/rst08-tuplet-beam-rests`, `time/t05-triplets-duplets`, `time/t07-nested-tuplets` |
| `tuplet-2` | 9 | 38 | `rests/rst08-tuplet-beam-rests`, `time/t05-triplets-duplets`, `time/t07-nested-tuplets` |
| `tuplet-5` | 14 | 58 | `rests/rst08-tuplet-beam-rests`, `time/t06-quint-sext-sept`, `time/t07-nested-tuplets` |
| `tuplet-6` | 12 | 62 | `rests/rst08-tuplet-beam-rests`, `time/t06-quint-sext-sept`, `perf/perf-pages-20` |
| `tuplet-7` | 4 | 37 | `rests/rst08-tuplet-beam-rests`, `time/t06-quint-sext-sept`, `perf/perf-pages-20` |
| `tuplet-nested` | 1 | 8 | `time/t07-nested-tuplets` |
| `tie` | 22 | 87 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano` |
| `tie-across-system` | 19 | 54 | `time/t01-simple-meters`, `time/t02-compound-irregular`, `time/t03-common-cut-piano` |

### marks

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `slur` | 40 | 628 | `notes/nt07-grace-notes`, `marks/mk01-articulations-violin`, `marks/mk08-string-quartet-marks` |
| `staccato` | 19 | 1267 | `marks/mk01-articulations-violin`, `marks/mk07-vocalise-voice-piano`, `marks/mk08-string-quartet-marks` |
| `staccatissimo` | 10 | 17 | `marks/mk01-articulations-violin`, `marks/mk09-stacked-marks-viola`, `perf/perf-piano-a3-300dpi` |
| `accent` | 20 | 246 | `marks/mk01-articulations-violin`, `marks/mk07-vocalise-voice-piano`, `marks/mk08-string-quartet-marks` |
| `tenuto` | 19 | 173 | `marks/mk01-articulations-violin`, `marks/mk07-vocalise-voice-piano`, `marks/mk08-string-quartet-marks` |
| `marcato` | 14 | 119 | `marks/mk01-articulations-violin`, `marks/mk08-string-quartet-marks`, `marks/mk09-stacked-marks-viola` |
| `fermata` | 53 | 398 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk07-vocalise-voice-piano`, `marks/mk08-string-quartet-marks` |
| `trill` | 15 | 42 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola`, `layouts/melody-flute-air` |
| `mordent` | 13 | 53 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola`, `perf/perf-pages-10` |
| `turn` | 13 | 33 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk09-stacked-marks-viola`, `perf/perf-pages-10` |
| `arpeggio` | 12 | 92 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano`, `layouts/piano-grand-staff-prelude` |
| `breath` | 13 | 26 | `marks/mk02-ornaments-fermatas-flute`, `marks/mk07-vocalise-voice-piano`, `layouts/melody-flute-air` |
| `dyn-pp` | 17 | 29 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `dyn-p` | 38 | 77 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `dyn-mp` | 21 | 34 | `marks/mk03-dynamics-hairpins-cello`, `structure/str08-variations-twelve-pages-piano`, `lyrics/lyr01-elisions-three-languages` |
| `dyn-mf` | 46 | 93 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `dyn-f` | 38 | 94 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk07-vocalise-voice-piano`, `marks/mk08-string-quartet-marks` |
| `dyn-ff` | 17 | 35 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk08-string-quartet-marks`, `marks/mk09-stacked-marks-viola` |
| `dyn-sfz` | 11 | 14 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk08-string-quartet-marks`, `marks/mk09-stacked-marks-viola` |
| `hairpin-cresc` | 30 | 104 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `hairpin-dim` | 35 | 92 | `marks/mk03-dynamics-hairpins-cello`, `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano` |
| `pedal` | 17 | 268 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk07-vocalise-voice-piano`, `layouts/cross-staff-piano-arpeggio-study` |
| `fingering` | 12 | 292 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk09-stacked-marks-viola`, `layouts/piano-grand-staff-prelude` |
| `text-expression` | 23 | 65 | `notes/nt08-cue-notes`, `marks/mk05-tempo-text-rehearsal-oboe`, `marks/mk07-vocalise-voice-piano` |
| `tempo-mark` | 74 | 175 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk05-tempo-text-rehearsal-oboe`, `marks/mk06-lead-sheet-chord-symbols` |
| `metronome` | 54 | 144 | `marks/mk04-piano-pedal-arpeggio-fingering`, `marks/mk05-tempo-text-rehearsal-oboe`, `marks/mk06-lead-sheet-chord-symbols` |
| `rehearsal-mark` | 19 | 124 | `rests/rst05-multibar-rests`, `marks/mk05-tempo-text-rehearsal-oboe`, `marks/mk08-string-quartet-marks` |
| `chord-symbol` | 2 | 61 | `marks/mk06-lead-sheet-chord-symbols`, `layouts/lead-sheet-long-road` |

### structure

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `barline-double` | 26 | 133 | `pitch/pitch-cov-key-changes-organ`, `pitch/pitch-cov-keys-major-sharps`, `structure/str01-double-final-barlines` |
| `barline-final` | 101 | 123 | `structure/str01-double-final-barlines`, `structure/str03-voltas-string-quartet`, `structure/str04-segno-coda-ds` |
| `repeat-start` | 14 | 33 | `structure/str02-repeat-signs-piano`, `structure/str03-voltas-string-quartet`, `structure/str05-fine-dc-al-fine-piano` |
| `repeat-end` | 16 | 40 | `structure/str02-repeat-signs-piano`, `structure/str03-voltas-string-quartet`, `structure/str05-fine-dc-al-fine-piano` |
| `volta-1` | 13 | 16 | `structure/str03-voltas-string-quartet`, `structure/str06-breaks-two-pages-song`, `structure/str07-orchestral-five-pages` |
| `volta-2` | 13 | 16 | `structure/str03-voltas-string-quartet`, `structure/str06-breaks-two-pages-song`, `structure/str07-orchestral-five-pages` |
| `segno` | 6 | 6 | `structure/str04-segno-coda-ds`, `structure/str07-orchestral-five-pages`, `perf/perf-pages-05` |
| `coda` | 6 | 8 | `structure/str04-segno-coda-ds`, `structure/str08-variations-twelve-pages-piano`, `perf/perf-pages-05` |
| `dc` | 10 | 10 | `structure/str05-fine-dc-al-fine-piano`, `structure/str08-variations-twelve-pages-piano`, `perf/perf-piano-a3-300dpi` |
| `ds` | 6 | 6 | `structure/str04-segno-coda-ds`, `structure/str07-orchestral-five-pages`, `perf/perf-pages-05` |
| `fine` | 10 | 10 | `structure/str05-fine-dc-al-fine-piano`, `structure/str07-orchestral-five-pages`, `perf/perf-piano-a3-300dpi` |
| `system-break` | 101 | 581 | `time/t08-ties-systems-pages`, `structure/str01-double-final-barlines`, `structure/str02-repeat-signs-piano` |
| `page-break` | 10 | 90 | `time/t08-ties-systems-pages`, `structure/str06-breaks-two-pages-song`, `structure/str07-orchestral-five-pages` |
| `multi-page` | 10 | 26 | `time/t08-ties-systems-pages`, `structure/str06-breaks-two-pages-song`, `structure/str07-orchestral-five-pages` |

### lyrics

| tag | items | occurrences | example items |
|---|---:|---:|---|
| `lyrics` | 23 | 1791 | `time/t04-pickup-song`, `structure/str06-breaks-two-pages-song`, `lyrics/lyr01-elisions-three-languages` |
| `lyrics-multi-verse` | 13 | 320 | `structure/str06-breaks-two-pages-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages` |
| `lyrics-melisma` | 16 | 129 | `time/t04-pickup-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages` |
| `lyrics-extender` | 16 | 91 | `time/t04-pickup-song`, `structure/str06-breaks-two-pages-song`, `lyrics/lyr01-elisions-three-languages` |
| `lyrics-hyphen` | 23 | 395 | `time/t04-pickup-song`, `structure/str06-breaks-two-pages-song`, `lyrics/lyr01-elisions-three-languages` |
| `lyrics-elision` | 1 | 11 | `lyrics/lyr01-elisions-three-languages` |
| `lyrics-non-ascii` | 2 | 30 | `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages` |
| `stanza-text` | 10 | 39 | `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages`, `perf/perf-hymn-a3-300dpi` |

**Every one of the 139 taxonomy tags has at least one item.**

Tags with exactly one item (accuracy for them rests on one piece): `cue-note` (notes/nt08-cue-notes, 24x), `rest-multibar` (rests/rst05-multibar-rests, 9x), `tuplet-nested` (time/t07-nested-tuplets, 8x), `lyrics-elision` (lyrics/lyr01-elisions-three-languages, 11x).

Extra tags (`x-` prefix) used by the families for symbols outside the taxonomy:

`x-acc-courtesy-paren` (2), `x-acc-natural-flat` (1), `x-acc-natural-sharp` (2), `x-clef-percussion0+0` (1), `x-cross-staff-note` (1), `x-dyn-fff` (1), `x-dyn-fp` (1), `x-dyn-fz` (1), `x-dyn-ppp` (1), `x-dyn-sf` (2), `x-dyn-sfp` (1), `x-group-bracket` (11), `x-group-square` (1), `x-inverted-mordent` (2), `x-inverted-turn` (1), `x-key-cancel` (1), `x-key-minor` (3), `x-multi-staff-part` (6), `x-pedal-release` (2), `x-portato` (1), `x-rest-fermata` (4), `x-rest-in-beam` (1), `x-rest-in-tuplet` (1), `x-rest-lowered` (2), `x-rest-multibar-hbar` (1), `x-rest-multibar-symbols` (1), `x-rest-raised` (3), `x-rest-whole-bar-shared-staff` (1), `x-tie-across-page` (1), `x-time-3-8` (1), `x-time-4-2` (3), `x-time-6-4` (1), `x-time-courtesy` (8), `x-to-coda` (2), `x-tuplet-4` (2), `x-two-voice-staff-measure` (5), `x-volta-3` (1).

## Layout coverage

| layout | items (primary) | also tagged | examples |
|---|---:|---:|---|
| `melody` | 32 | 0 | `notes/nt01-note-values`, `notes/nt02-dots`, `notes/nt04-beams` |
| `melody-lyrics` | 4 | 0 | `time/t04-pickup-song`, `lyrics/lyr01-elisions-three-languages`, `lyrics/lyr02-non-ascii-four-languages` |
| `piano` | 29 | 0 | `notes/nt03-chords`, `notes/nt06-ledger-lines`, `notes/nt09-tremolos` |
| `voice-piano` | 3 | 0 | `marks/mk07-vocalise-voice-piano`, `structure/str06-breaks-two-pages-song`, `layouts/voice-piano-night-song` |
| `choir-closed-satb` | 1 | 8 | `layouts/choir-closed-satb-light-of-morning`, `perf/perf-hymn-a3-300dpi`, `perf/perf-hymn-a4-100dpi` |
| `choir-open-satb` | 1 | 0 | `layouts/choir-open-satb-gloria` |
| `choir-sab` | 1 | 0 | `layouts/choir-sab-summer-song` |
| `choir-ttbb` | 1 | 0 | `layouts/choir-ttbb-evening-bells` |
| `choir-ssaa` | 1 | 0 | `layouts/choir-ssaa-winter-night` |
| `choir-piano` | 1 | 0 | `layouts/choir-piano-song-of-rejoicing` |
| `organ` | 2 | 0 | `pitch/pitch-cov-key-changes-organ`, `layouts/organ-three-staves-chorale-prelude` |
| `string-quartet` | 6 | 0 | `rests/rst09-quartet-rests`, `pitch/pitch-cov-clefs-quartet`, `time/t10-quartet-meters` |
| `orchestral` | 2 | 0 | `structure/str07-orchestral-five-pages`, `layouts/orchestral-festive-march-9-staves` |
| `lead-sheet` | 2 | 0 | `marks/mk06-lead-sheet-chord-symbols`, `layouts/lead-sheet-long-road` |
| `hymnal-stanzas` | 9 | 0 | `layouts/hymnal-stanzas-light-of-ages`, `perf/perf-hymn-a3-300dpi`, `perf/perf-hymn-a4-100dpi` |
| `divisi` | 2 | 0 | `layouts/divisi-choir-bright-new-day`, `layouts/divisi-strings-lament` |
| `cross-staff` | 1 | 0 | `layouts/cross-staff-piano-arpeggio-study` |
| `two-voices-one-staff-instrument` | 3 | 11 | `rests/rst06-two-voice-rests`, `time/t09-two-voices-guitar`, `layouts/two-voices-piano-song-without-words` |
| `percussion-none` | 1 | 0 | `percussion/perc01-parade-flute-snare-drumset` |

**Every one of the 19 layout tags has at least one item.** `expected.parts` and `expected.must_not_split` in each meta.json give the part structure a converter must produce (e.g. a piano grand staff or an organ is one part; closed SATB is four parts).

## Items

### notes

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `nt01-note-values`<br>Note Values (violin) | melody | Violin (False) | 1 | note-breve, note-whole, note-half, note-quarter, note-8th, note-16th, note-32nd, note-64th, beam, flag, stem-up, stem-down | typical-office-scan | photocopy-thick |
| `nt02-dots`<br>Dotted Rhythms (oboe) | melody | Oboe (False) | 1 | dot, double-dot, note-whole, note-half, note-quarter, note-8th, note-16th, note-32nd, note-64th, beam, chord | typical-office-scan | low-dpi-jpeg |
| `nt03-chords`<br>Chord Study (piano) | piano | Piano (True) | 1 | chord, note-whole, note-half, note-quarter, note-8th, note-16th, beam, stem-up, stem-down, acc-sharp, acc-flat, acc-natural | typical-office-scan | phone-capture |
| `nt04-beams`<br>Beam Groups (flute) | melody | Flute (False) | 1 | beam, note-8th, note-16th, note-32nd, stem-up, stem-down | typical-office-scan | faded-foxed |
| `nt05-flags-stems`<br>Flags and Stems (violin) | melody | Violin (False) | 1 | flag, stem-up, stem-down, note-8th, note-16th, note-32nd, note-64th | typical-office-scan | photocopy-thin |
| `nt06-ledger-lines`<br>Ledger Lines (piano) | piano | Piano (True) | 1 | ledger-above, ledger-below, chord, note-whole, note-half, note-quarter, note-8th, note-16th | typical-office-scan | halftone-skew |
| `nt07-grace-notes`<br>Grace Notes (flute) | melody | Flute (False) | 1 | grace, grace-slash, slur, note-quarter, note-half | typical-office-scan | book-curl |
| `nt08-cue-notes`<br>Cue Notes (flute part) | melody | Flute (True) | 1 | cue-note, rest-whole-bar, text-expression | typical-office-scan | coffee-stained |
| `nt09-tremolos`<br>Tremolos (piano) | piano | Piano (True) | 1 | tremolo, note-whole, note-half, note-quarter, note-8th, chord | typical-office-scan | heavy-skew-noise |
| `nt10-piano-etude`<br>Etude in C (piano) | piano | Piano (True) | 1 | note-half, note-quarter, note-8th, note-16th, note-32nd, dot, double-dot, chord, beam, flag, grace, ledger-above, ledger-below | typical-office-scan | recompressed-150 |

### rests

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `rst01-rest-values`<br>Rest Values (oboe): every rest from breve to 64th | melody | Oboe (False) | 1 | rest-breve, rest-whole, rest-half, rest-quarter, rest-8th, rest-16th, rest-32nd, rest-64th | dpi=300, jpeg_quality=65 | dpi=150, jpeg_quality=25 |
| `rst02-dotted-rests`<br>Dotted Rests (violoncello): dotted and double-dotted rests | melody | Violoncello (False) | 1 | rest-dotted, double-dot, dot | dpi=200, jpeg_quality=70 | dpi=200, jpeg_quality=None |
| `rst03-whole-bar-rests-simple`<br>Whole-Bar Rests I (violin): simple meters | melody | Violin (False) | 1 | rest-whole-bar, time-2-4, time-3-4, time-4-4, time-common, time-cut, time-3-2, time-5-4, x-time-4-2 | dpi=300, jpeg_quality=60 | dpi=150, jpeg_quality=25 |
| `rst04-whole-bar-rests-compound`<br>Whole-Bar Rests II (viola): compound and irregular meters | melody | Viola (False) | 1 | rest-whole-bar, clef-alto, time-6-8, time-9-8, time-12-8, time-5-8, time-7-8, x-time-3-8, x-time-6-4 | dpi=200, jpeg_quality=60 | dpi=200, jpeg_quality=22 |
| `rst05-multibar-rests`<br>Tacet Interludes (trumpet part): multi-bar rests | melody | Trumpet in C (False) | 1 | rest-multibar, x-rest-multibar-hbar, x-rest-multibar-symbols, rehearsal-mark | dpi=300, jpeg_quality=70 | dpi=150, jpeg_quality=30 |
| `rst06-two-voice-rests`<br>Hocket for Two Flutes: raised and lowered rests on one staff | two-voices-one-staff-instrument | Flutes 1.2 (True) | 1 | x-rest-raised, x-rest-lowered, x-rest-whole-bar-shared-staff, stem-up, stem-down | dpi=300, jpeg_quality=65 | dpi=200, jpeg_quality=24 |
| `rst07-piano-rests`<br>Left-Hand Silences (piano): rests in both hands | piano | Piano (True) | 1 | rest-quarter, rest-8th, rest-16th, rest-32nd, rest-half, rest-dotted, rest-whole-bar, x-rest-raised, x-rest-lowered | dpi=200, jpeg_quality=65 | dpi=150, jpeg_quality=28 |
| `rst08-tuplet-beam-rests`<br>Rests in Tuplets and Beams (flute) | melody | Flute (False) | 1 | x-rest-in-tuplet, x-rest-in-beam, tuplet-3, tuplet-5, tuplet-6, tuplet-7, tuplet-2, beam | dpi=300, jpeg_quality=55 | dpi=150, jpeg_quality=22 |
| `rst09-quartet-rests`<br>Quartet Fughetta: rests in a string quartet | string-quartet | Violin I, Violin II, Viola, Violoncello (False) | 1 | rest-whole-bar, rest-quarter, rest-8th, rest-16th, rest-half, rest-dotted, x-rest-fermata, clef-alto, clef-bass | dpi=300, jpeg_quality=65 | dpi=200, jpeg_quality=None |

### pitch

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `pitch-cov-accidentals-chords-piano`<br>Chromatic Chords | piano | Piano (True) | 1 | chord, acc-sharp, acc-flat, acc-natural, acc-double-sharp, acc-double-flat, acc-courtesy, x-acc-natural-sharp, key-f4 | typical office scan: 250 dpi RGB, -0.8 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q65 | rehearsal copy at 200 dpi: pencil circles around accidentals, pencil reminder accidentals and fingerings (NOT in the truth), coffee ring, 2.5 deg skew, blur, JP |
| `pitch-cov-accidentals-melody`<br>Accidental Etude | melody | Flute (False) | 1 | acc-sharp, acc-flat, acc-natural, acc-double-sharp, acc-double-flat, acc-courtesy, x-acc-courtesy-paren, x-acc-natural-sharp, x-acc-natural-flat, key-s1 | typical office scan: 300 dpi grey, +1.4 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q65 | 100 dpi grey: 5 deg skew, focus blur 1.2 px@300dpi, heavy noise, JPEG q15 - sharps, naturals and double sharps become blobs of a few pixels |
| `pitch-cov-clef-changes-piano`<br>Changing Hands | piano | Piano (True) | 1 | clef-treble, clef-bass, clef-change, key-f1, ledger-below, ledger-above | typical office scan: 250 dpi grey, -0.9 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q65 | thin light binarised photocopy at 150 dpi: -3 deg skew, low threshold (108) with noise -> broken staff lines and thin stems, salt-and-pepper, 1-bit PNG |
| `pitch-cov-clefs-all`<br>Eight Clefs | melody | Melody (False) | 1 | clef-treble, clef-bass, clef-alto, clef-tenor, clef-soprano, clef-treble-8vb, clef-treble-8va, clef-bass-8vb, clef-change, ledger-above, ledger-below | typical office scan: 300 dpi grey, +0.7 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q70 | old yellowed copy at 150 dpi: strong bleed-through, foxing, 6.5 deg skew, gradient + vignette, focus blur 1.4 px@300dpi, noise, JPEG q20 (RGB) - the small octav |
| `pitch-cov-clefs-quartet`<br>Quartet in Changing Clefs | string-quartet | Violin I, Violin II, Viola, Violoncello (False) | 1 | clef-treble, clef-alto, clef-tenor, clef-bass, clef-change, key-s2 | typical office scan: 300 dpi RGB, +0.5 deg skew, light paper texture, slight blur, noise sigma 2, JPEG q70 | phone photo at 150 dpi: perspective keystone on a dark desk, uneven light + vignette + warm cast, motion blur (3 px@300dpi), sensor noise, JPEG q25 (RGB) |
| `pitch-cov-key-changes-organ`<br>Modulating Chorale | organ | Organ (True) | 1 | key-s4, key-f3, key-0, key-s3, key-s2, key-f1, key-s5, key-change, x-key-cancel, x-key-minor, barline-double, chord | typical office scan: 300 dpi grey, -0.5 deg skew, light paper texture, slight blur, noise sigma 2, JPEG q70 | bound book photocopy at 150 dpi: strong left page curl with wavy warp, deep gutter shadow, vertical camera shake (motion blur 4 px@300dpi), noise, JPEG q20 (RGB |
| `pitch-cov-keys-major-flats`<br>Flats Descending | piano | Piano (True) | 1 | key-f1, key-f2, key-f3, key-f4, key-f5, key-f6, key-f7, key-change, chord | typical office scan: 300 dpi grey, +1.0 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q65 | thick binarised photocopy at 200 dpi: ink spread (+2 px) fills the flat glyphs, 4 deg skew, toner speckles, threshold 170 -> 1-bit PNG |
| `pitch-cov-keys-major-sharps`<br>Sharps Ascending | melody | Violin (False) | 1 | key-0, key-s1, key-s2, key-s3, key-s4, key-s5, key-s6, key-s7, key-change, barline-double | typical office scan: 200 dpi grey, -1.2 deg skew, light paper texture, slight blur, noise sigma 4, JPEG q60 | 120 dpi grey copy: coffee ring over the key signatures, 9 deg skew, gradient, focus blur 1.6 px@300dpi, noise, JPEG q18 |
| `pitch-cov-keys-minor-flats`<br>Minor Keys with Flats | melody | Viola (False) | 1 | key-f1, key-f2, key-f3, key-f4, key-f5, key-f6, key-f7, x-key-minor, key-change, acc-natural, acc-sharp, clef-alto | typical office scan: 200 dpi RGB, -0.6 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q60 | halftone-screened reproduction (100 lpi, 45 deg) rescanned -> moire, bluish recycled paper, page cropped 1.5 mm into the staff starts (cuts into clef + key sign |
| `pitch-cov-keys-minor-sharps`<br>Minor Keys with Sharps | melody | Violoncello (False) | 1 | key-0, key-s1, key-s2, key-s3, key-s4, key-s5, key-s6, key-s7, x-key-minor, key-change, acc-sharp, acc-double-sharp, clef-bass | typical office scan: 250 dpi grey, +0.4 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q70 | page fed upside down at 150 dpi: rotated 180 deg + 2 deg skew, grey, gradient, blur, noise, JPEG q28 |
| `pitch-cov-ottava-ledger-melody`<br>Ledger Lines and Octave Signs | melody | Melody (False) | 1 | ottava-8va, ottava-8vb, ottava-15ma, ledger-above, ledger-below | typical office scan: 250 dpi RGB, -1.5 deg skew, light paper texture, slight blur, noise sigma 3, JPEG q60 | low-light phone photo at 150 dpi: strong keystone, dark vignette, focus blur 1.3 px@300dpi, heavy sensor noise, JPEG q18 (RGB) - ledger lines merge |
| `pitch-cov-ottava-piano`<br>Octave Signs | piano | Piano (True) | 1 | ottava-8va, ottava-8vb, ottava-15ma, ledger-above, ledger-below | typical office scan: 200 dpi grey, +0.9 deg skew, light paper texture, slight blur, noise sigma 4, JPEG q60 | page scanned sideways (rotated 90 deg) + 1.5 deg skew, two punch holes, 150 dpi grey, gaussian + salt-and-pepper noise, JPEG q30 |

### time

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `t01-simple-meters`<br>Simple Meters (flute) | melody | Flute (False) | 1 | time-2-4, time-3-4, time-4-4, time-5-4, time-2-2, time-3-2, time-change, x-time-courtesy, pickup, tie, tie-across-system | dpi=300, jpeg_quality=70 | dpi=150, jpeg_quality=None |
| `t02-compound-irregular`<br>Compound and Irregular Meters (violoncello) | melody | Violoncello (False) | 1 | time-6-8, time-9-8, time-12-8, time-5-8, time-7-8, time-change, x-time-courtesy, pickup, tie, tie-across-system, rest-dotted | dpi=250, jpeg_quality=65 | dpi=120, jpeg_quality=18 |
| `t03-common-cut-piano`<br>Common and Cut Time (piano) | piano | Piano (True) | 1 | time-common, time-cut, time-4-4, time-2-2, time-change, x-time-courtesy, pickup, tie, tie-across-system, chord | dpi=200, jpeg_quality=60 | dpi=120, jpeg_quality=22 |
| `t04-pickup-song`<br>The Tyger (voice, pickup and meter changes with lyrics) | melody-lyrics | Voice (False) | 1 | pickup, time-3-4, time-6-8, time-2-4, time-change, tie, tie-across-system, lyrics | dpi=300, jpeg_quality=75 | dpi=150, jpeg_quality=None |
| `t05-triplets-duplets`<br>Triplets and Duplets (oboe) | melody | Oboe (False) | 1 | tuplet-3, tuplet-2, x-tuplet-4, time-2-4, time-cut, time-6-8, time-9-8, time-12-8, time-change, tie, tie-across-system | dpi=300, jpeg_quality=55 | dpi=150, jpeg_quality=20 |
| `t06-quint-sext-sept`<br>Fives, Sixes and Sevens (flute) | melody | Flute (False) | 1 | tuplet-5, tuplet-6, tuplet-7, time-common, pickup, tie, tie-across-system, double-dot | dpi=250, jpeg_quality=65 | dpi=100, jpeg_quality=20 |
| `t07-nested-tuplets`<br>Nested Tuplets (violin) | melody | Violin (False) | 1 | tuplet-nested, tuplet-3, tuplet-5, tuplet-2, time-4-4, time-6-8, time-change, tie | dpi=300, jpeg_quality=70 | dpi=200, jpeg_quality=25 |
| `t08-ties-systems-pages`<br>Tied Across the Page (piano, 2 pages) | piano | Piano (True) | 2 | tie, tie-across-system, x-tie-across-page, chord, time-3-4, time-6-8, time-change, page-break, multi-page, system-break | dpi=200, jpeg_quality=60 | dpi=150, jpeg_quality=20 |
| `t09-two-voices-guitar`<br>Hemiola for Guitar (two voices on one staff) | two-voices-one-staff-instrument | Guitar (True) | 1 | time-6-8, time-3-4, time-change, tuplet-2, tuplet-3, pickup, tie, tie-across-system, clef-treble-8vb | dpi=300, jpeg_quality=60 | dpi=200, jpeg_quality=None |
| `t10-quartet-meters`<br>Quartet in Changing Meters (string quartet) | string-quartet | Violin I, Violin II, Viola, Violoncello (False) | 1 | time-4-4, time-3-4, time-5-8, time-7-8, time-2-4, time-6-8, time-common, time-cut, time-change, x-time-courtesy, tuplet-3, tuplet-5, tuplet-2, tie, tie-across-system, clef-alto | dpi=250, jpeg_quality=62 | dpi=110, jpeg_quality=16 |

### marks

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `mk01-articulations-violin`<br>Bowing Study in Articulations | melody | Violin (True) | 1 | staccato, staccatissimo, accent, tenuto, marcato, x-portato, slur | typical scan: 300 dpi gray, +0.6 deg skew, blur 0.5, noise 4, JPEG q70 | 150 dpi 1-bit photocopy: 3.5 deg skew, thick threshold (dots and wedges swell), salt-and-pepper and speckle dirt that looks like staccato dots |
| `mk02-ornaments-fermatas-flute`<br>Pastorale with Ornaments | melody | Flute (True) | 1 | trill, mordent, x-inverted-mordent, turn, x-inverted-turn, fermata, breath | typical scan: 250 dpi gray, -0.9 deg skew, blur 0.6, noise 4, JPEG q65 | phone photo: perspective keystone on a dark desk, uneven light + vignette, motion blur, sensor noise, JPEG q25 |
| `mk03-dynamics-hairpins-cello`<br>Elegy in Dynamics | melody | Violoncello (True) | 1 | dyn-pp, dyn-p, dyn-mp, dyn-mf, dyn-f, dyn-ff, dyn-sfz, x-dyn-ppp, x-dyn-fff, x-dyn-fp, x-dyn-sf, x-dyn-fz, x-dyn-sfp, hairpin-cresc, hairpin-dim | typical scan: 200 dpi gray, +1.2 deg skew, blur 0.5, noise 4, JPEG q60 | aged yellowed paper: faded ink with dropouts, bleed-through of the reverse, foxing, -4 deg skew, blur, downsampled to 150 dpi, JPEG q30 |
| `mk04-piano-pedal-arpeggio-fingering`<br>Nocturne Study (pedal, arpeggio, fingering) | piano | Piano (True) | 1 | pedal, x-pedal-release, arpeggio, fingering, tempo-mark, metronome, hairpin-cresc, hairpin-dim, dyn-p, dyn-mf, dyn-pp | typical scan: 300 dpi rgb, -0.5 deg skew, blur 0.5, noise 3, JPEG q70 | book scan: page curl and dark gutter on the left, 2.5 deg skew, blur, heavy noise, JPEG q25 at 200 dpi |
| `mk05-tempo-text-rehearsal-oboe`<br>Promenade (tempo, text, rehearsal marks) | melody | Oboe (True) | 1 | tempo-mark, metronome, text-expression, rehearsal-mark | typical scan: 250 dpi gray, +0.8 deg skew, blur 0.6, noise 5, JPEG q60 | very low resolution: rendered at 300 dpi, blurred, downsampled to 110 dpi (text and box outlines smear), -2 deg skew, JPEG q30 |
| `mk06-lead-sheet-chord-symbols`<br>Harbour Lights (lead sheet) | lead-sheet | Melody (True) | 1 | chord-symbol, tempo-mark, metronome | typical scan: 200 dpi gray, -1 deg skew, blur 0.5, noise 4, JPEG q65 | halftoned copy of a copy: halftone moire, thin-threshold 1-bit binarisation (thin strokes break up), 1.5 deg skew, 200 dpi |
| `mk07-vocalise-voice-piano`<br>Vocalise (voice and piano) | voice-piano | Voice, Piano (True) | 1 | dyn-p, dyn-mf, dyn-f, dyn-pp, hairpin-cresc, hairpin-dim, breath, fermata, pedal, arpeggio, text-expression, tempo-mark, metronome, tenuto, accent, staccato | typical scan: 300 dpi rgb, +0.4 deg skew, blur 0.5, noise 3, JPEG q70 | crumpled page with a coffee ring over the middle systems, wavy staff lines, -3 deg skew, hand shadow, noise, JPEG q22 |
| `mk08-string-quartet-marks`<br>Scherzino for String Quartet | string-quartet | Violin I, Violin II, Viola, Violoncello (True) | 1 | dyn-f, dyn-p, dyn-ff, dyn-sfz, hairpin-cresc, hairpin-dim, staccato, accent, tenuto, marcato, fermata, slur, rehearsal-mark, tempo-mark, metronome, text-expression | typical scan: 250 dpi gray, -0.7 deg skew, blur 0.5, noise 4, JPEG q65 | over-inked copy (strokes thickened), 5 deg skew, salt-and-pepper, blur, downsampled to 150 dpi, JPEG q30 |
| `mk09-stacked-marks-viola`<br>Etude in Stacked Marks | melody | Viola (True) | 1 | staccato, staccatissimo, accent, tenuto, marcato, fingering, trill, mordent, x-inverted-mordent, turn, fermata, dyn-p, dyn-mf, dyn-f, dyn-ff, dyn-sfz, x-dyn-sf, hairpin-cresc, hairpin-dim, text-expression, tempo-mark, metronome, slur | typical scan: 200 dpi gray, +0.9 deg skew, blur 0.5, noise 5, JPEG q60 | faded ink with dropouts photographed at an angle: perspective keystone, light gradient, heavy noise, JPEG q20 |

### structure

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `str01-double-final-barlines`<br>Sectional Study - double and final bar lines (flute) | melody | Flute (False) | 1 | barline-double, barline-final, system-break | office flatbed scan, 300 dpi grey, 0.6 deg skew, light paper texture and noise, JPEG q80 | faded binarised photocopy, 150 dpi (from 300), 4.5 deg skew, ink drop-out breaking thin lines, salt & pepper and toner speckles |
| `str02-repeat-signs-piano`<br>Waltz in Repeats - start/end repeat signs in every position (piano) | piano | Piano (True) | 1 | repeat-start, repeat-end, barline-double, system-break | flatbed scan, 250 dpi grey, -0.8 deg skew, paper texture, faint bleed-through, JPEG q75 | phone photo of the page: perspective/keystone, uneven lamp light and vignette, motion blur, cream paper, 150 dpi, JPEG q22 |
| `str03-voltas-string-quartet`<br>Three Endings - 1st, 2nd and 3rd endings incl. a 2-bar ending across a system break (string quartet) | string-quartet | Violin I, Violin II, Viola, Violoncello (False) | 1 | volta-1, volta-2, x-volta-3, repeat-start, repeat-end, barline-double, barline-final | flatbed scan, 300 dpi, cream paper (RGB), 1.0 deg skew, slight blur and noise, JPEG q70 | dark, thickened binarised photocopy at 200 dpi, -5 deg skew, heavy blur and noise, salt & pepper, staple, two punch holes in the left margin |
| `str04-segno-coda-ds`<br>Round Trip - Segno, To Coda, D.S. al Coda, Coda (violin) | melody | Violin (False) | 1 | segno, coda, x-to-coda, ds, barline-double, barline-final | flatbed scan, 200 dpi grey, -1.2 deg skew, paper texture, noise, JPEG q70 | old yellowed copy, 150 dpi RGB: 7 deg skew, strong bleed-through, foxing and a coffee ring, focus blur, JPEG q20 |
| `str05-fine-dc-al-fine-piano`<br>Minuet and Trio - Fine with a mid-piece final bar, D.C. al Fine (piano) | piano | Piano (True) | 1 | fine, dc, barline-final, repeat-start, repeat-end | flatbed scan, 300 dpi grey, 0.4 deg skew, mild gradient lighting, noise, JPEG q85 | page fed upside down (180 deg) through a fax-like copier: 100 dpi (from 300) binarised, 3 deg skew, broken thin lines, speckles |
| `str06-breaks-two-pages-song`<br>Morning and Evening - explicit system/page breaks, 1st ending across a page turn (voice and piano, 2 pages) | voice-piano | Voice, Piano (True) | 2 | system-break, page-break, multi-page, tie-across-system, volta-1, volta-2, repeat-start, repeat-end | two-page flatbed scan, 300 dpi grey, pages skewed 0.7 and -0.9 deg, light texture, faint bleed-through of the other page, JPEG q75 | book-style capture: both pages as ONE 2-up image (double-page spread) with gutter shadow and page curl, yellowed paper, -2.5 deg rotation, vignette, motion blur |
| `str07-orchestral-five-pages`<br>Little Overture - rehearsal marks, Segno, Fine, D.S. al Fine, endings across a page turn (orchestra, 5 pages) | orchestral | Flute, Oboe, Bassoon, Violin I, Violin II, Viola, Violoncello (False) | 5 | multi-page, page-break, system-break, segno, fine, ds, volta-1, volta-2, repeat-start, repeat-end, barline-final, barline-double, rehearsal-mark | sheet-fed scan of 5 pages, 300 dpi grey, a different small skew per page (-1.0..1.1 deg), light noise, JPEG q75 | worn photocopy set, 200 dpi binarised: per-page skew up to 6 deg, page 4 fed upside down, page 2 at 97 % scale, toner speckles, broken thin lines |
| `str08-variations-twelve-pages-piano`<br>Theme and Variations in A - 12-page piano score: repeats in every section, endings, key changes, To Coda on page 1 and D.C. al Coda on page 11 | piano | Piano (True) | 12 | multi-page, page-break, system-break, repeat-start, repeat-end, volta-1, volta-2, dc, coda, x-to-coda, barline-double, barline-final | 12 pages from a sheet feeder, 200 dpi grey, small random skew per page, paper texture, noise, JPEG q70 | ring-binder photocopies at 150 dpi: punch holes, skew -4..5 deg per page, page 6 upside down, pages 3 and 9 at a different scale, strong bleed-through, binarise |

### lyrics

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `lyr01-elisions-three-languages`<br>Canticle of Elisions - melody with three numbered verses and lyric elisions | melody-lyrics | Voice (False) | 1 | lyrics, lyrics-multi-verse, lyrics-hyphen, lyrics-elision, lyrics-melisma, lyrics-extender, stanza-text, lyrics-non-ascii | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20 |
| `lyr02-non-ascii-four-languages`<br>Morning in Four Tongues - melody with four numbered verses in four languages (non-ASCII lyrics) | melody-lyrics | Voice (False) | 1 | lyrics, lyrics-multi-verse, lyrics-hyphen, lyrics-non-ascii, lyrics-melisma, lyrics-extender, stanza-text, beam | 200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70 | phone photo of the page: perspective/keystone, uneven light, vignette, motion blur, 150 dpi, JPEG q25 |

### layouts

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `choir-closed-satb-light-of-morning`<br>Light of Morning - SATB choir in closed score (two staves) | choir-closed-satb | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, fermata, ledger-above, ledger-below, beam, lyrics-hyphen, slur, dyn-mf | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20 |
| `choir-open-satb-gloria`<br>Gloria - SATB choir in open score with imitative entries | choir-open-satb | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, flag, lyrics-melisma, slur, rest-whole-bar, dyn-f, dyn-mf | 200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, salt & pepper, toner specks |
| `choir-piano-song-of-rejoicing`<br>Song of Rejoicing - closed SATB choir with piano accompaniment | choir-piano | Soprano, Alto, Tenor, Bass, Piano (True) | 1 | ledger-below, lyrics, chord, ledger-above, rest-whole-bar, lyrics-hyphen, dyn-f, dyn-mf | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | phone photo of the page: perspective/keystone, uneven light, vignette, motion blur, 150 dpi, JPEG q25 |
| `choir-sab-summer-song`<br>Summer Song - SAB choir on three bracketed staves | choir-sab | Soprano, Alto, Baritone (False) | 1 | lyrics, lyrics-hyphen, dyn-f, dyn-mp, fermata, hairpin-dim, ledger-below, key-s1 | 240 dpi grey scan, -0.5 deg skew, faint bleed-through, JPEG q72 | phone photo of the page: perspective/keystone, uneven light, vignette, motion blur, 150 dpi, JPEG q25 |
| `choir-ssaa-winter-night`<br>Winter Night - SSAA choir in closed score on two treble staves | choir-ssaa | Soprano I, Soprano II, Alto I, Alto II (False) | 1 | ledger-below, lyrics, dot, lyrics-hyphen, fermata, slur, beam, dyn-mp | 250 dpi grey scan, 1.2 deg skew, soft focus, toner specks, JPEG q65 | old yellowed copy: bleed-through, foxing, coffee ring, pencil annotations, 150 dpi colour, 2 deg skew, JPEG q30 |
| `choir-ttbb-evening-bells`<br>Evening Bells - TTBB male choir in closed score | choir-ttbb | Tenor I, Tenor II, Baritone, Bass (False) | 1 | lyrics, fermata, lyrics-hyphen, ledger-above, clef-treble-8vb, dyn-mf, dyn-p, dyn-pp | 300 dpi colour scan on cream paper, 0.4 deg skew, noise, JPEG q80 | thick dark binarised photocopy at 200 dpi: ink spread, 2.5 deg skew, staple, two punch holes, salt & pepper |
| `cross-staff-piano-arpeggio-study`<br>Arpeggio Study - piano with cross-staff left-hand arpeggios (kneed beams) | cross-staff | Piano (True) | 1 | ledger-below, beam, acc-natural, slur, chord, fermata, note-whole, pedal | 300 dpi colour scan on cream paper, 0.4 deg skew, noise, JPEG q80 | low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20 |
| `divisi-choir-bright-new-day`<br>Bright New Day - open SATB with soprano divisi (two voices) and bass octave divisi (chords) | divisi | Soprano, Alto, Tenor, Bass (True) | 1 | lyrics, lyrics-hyphen, chord, dyn-mf, fermata, ledger-below, text-expression, clef-treble-8vb | 250 dpi grey scan, 1.2 deg skew, soft focus, toner specks, JPEG q65 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, salt & pepper, toner specks |
| `divisi-strings-lament`<br>Lament - string orchestra with divisi (two voices on one staff, and chords) | divisi | Violin I, Violin II, Viola, Violoncello (True) | 1 | chord, acc-sharp, fermata, note-whole, text-expression, beam, dyn-f, dyn-mf | 200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70 | old yellowed copy: bleed-through, foxing, coffee ring, pencil annotations, 150 dpi colour, 2 deg skew, JPEG q30 |
| `hymnal-stanzas-light-of-ages`<br>Light of Ages - hymnal page: closed SATB with four stanzas between the staves | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-multi-verse, fermata, lyrics-hyphen, ledger-below, ledger-above, key-s1, metronome | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | old yellowed copy: bleed-through, foxing, coffee ring, pencil annotations, 150 dpi colour, 2 deg skew, JPEG q30 |
| `lead-sheet-long-road`<br>The Long Road - lead sheet: melody, chord symbols, two verses, 1st/2nd endings | lead-sheet | Melody (False) | 1 | lyrics, chord-symbol, lyrics-multi-verse, lyrics-hyphen, flag, note-whole, dot, barline-double | 240 dpi grey scan, -0.5 deg skew, faint bleed-through, JPEG q72 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, salt & pepper, toner specks |
| `melody-cello-elegy-2page`<br>Elegy - two-page solo cello melody (bass clef, tenor-clef passage) | melody | Violoncello (False) | 2 | slur, dot, accent, beam, ledger-above, rest-quarter, acc-sharp, clef-change | 240 dpi grey scan, -0.5 deg skew, faint bleed-through, JPEG q72 | old yellowed copy: bleed-through, foxing, coffee ring, pencil annotations, 150 dpi colour, 2 deg skew, JPEG q30 |
| `melody-flute-air`<br>Air for Flute - single-staff instrumental melody | melody | Flute (False) | 1 | beam, slur, note-16th, staccato, tenuto, ledger-above, acc-natural, dot | 200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70 | phone photo of the page: perspective/keystone, uneven light, vignette, motion blur, 150 dpi, JPEG q25 |
| `melody-lyrics-morning-song`<br>Morning Song - vocal melody with one verse of lyrics | melody-lyrics | Voice (False) | 1 | lyrics, lyrics-extender, lyrics-hyphen, beam, dot, lyrics-melisma, slur, ledger-below | 300 dpi colour scan on cream paper, 0.4 deg skew, noise, JPEG q80 | low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20 |
| `orchestral-festive-march-9-staves`<br>Festive March - 9-staff orchestral full score, two pages | orchestral | Flute, Oboe, Bassoon, Trumpet in C, Timpani, Violin I, Violin II, V... (True) | 2 | beam, ledger-above, rest-quarter, dyn-f, dyn-ff, fermata, hairpin-cresc, note-whole | 250 dpi grey scan, 1.2 deg skew, soft focus, toner specks, JPEG q65 | low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20 |
| `organ-three-staves-chorale-prelude`<br>Chorale Prelude - organ on three staves (manuals + pedal) | organ | Organ (True) | 1 | fermata, ledger-above, acc-sharp, ledger-below, beam, note-whole, text-expression, dyn-f | 200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70 | thick dark binarised photocopy at 200 dpi: ink spread, 2.5 deg skew, staple, two punch holes, salt & pepper |
| `piano-grand-staff-prelude`<br>Prelude in G - solo piano on a braced grand staff | piano | Piano (True) | 1 | beam, chord, staccato, slur, fingering, ledger-above, ledger-below, note-16th | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, salt & pepper, toner specks |
| `string-quartet-minuet`<br>Minuet - string quartet on four bracketed staves | string-quartet | Violin I, Violin II, Viola, Violoncello (True) | 1 | accent, slur, staccato, ledger-above, rest-quarter, beam, dot, text-expression | 300 dpi colour scan on cream paper, 0.4 deg skew, noise, JPEG q80 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, salt & pepper, toner specks |
| `two-voices-piano-song-without-words`<br>Song without Words - piano right hand with two voices on one staff | two-voices-one-staff-instrument | Piano (True) | 1 | chord, dot, slur, fermata, dyn-mf, dyn-p, key-s4, ledger-below | 300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75 | thick dark binarised photocopy at 200 dpi: ink spread, 2.5 deg skew, staple, two punch holes, salt & pepper |
| `voice-piano-night-song`<br>Night Song - voice with lyrics above a piano grand staff | voice-piano | Voice, Piano (True) | 1 | lyrics, chord, beam, rest-quarter, fermata, flag, note-whole, slur | 250 dpi grey scan, 1.2 deg skew, soft focus, toner specks, JPEG q65 | thick dark binarised photocopy at 200 dpi: ink spread, 2.5 deg skew, staple, two punch holes, salt & pepper |

### percussion

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `perc01-parade-flute-snare-drumset`<br>Village Parade - flute with snare drum (one-line staff) and drum set (percussion clef) | percussion-none | Flute, Snare Drum, Drum Set (False) | 1 | beam, rest-quarter, note-16th, chord, accent, dyn-f, dot, dyn-mf | 300 dpi grey flatbed scan, 0.7 deg skew, light paper texture and noise, JPEG q72 | thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, -3 deg skew, broken lines, salt & pepper, toner specks |

### perf

| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |
|---|---|---|---:|---|---|---|
| `perf-hymn-a3-300dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-100dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-150dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-200dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-300dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-400dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-a4-600dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-hymn-letter-300dpi`<br>O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas | hymnal-stanzas | Soprano, Alto, Tenor, Bass (False) | 1 | lyrics, lyrics-hyphen, fermata, lyrics-melisma, ledger-above, lyrics-extender, dot, lyrics-multi-verse | typical flatbed scan: grey, +0.6 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | phone photo of a yellowed copy: perspective / keystone, 2.5 deg rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30 |
| `perf-pages-01`<br>Forty Variations for piano - 1-page document | piano | Piano (True) | 1 | chord, ledger-above, note-whole, tenuto, ledger-below, fermata, acc-sharp, dyn-mf | typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew that differs per page, light blur + noise, JPEG q80 | worn photocopies scanned in grey: 1.5-3.5 deg skew per page, bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35 |
| `perf-pages-05`<br>Forty Variations for piano - 5-page document | piano | Piano (True) | 5 | ledger-above, beam, chord, note-16th, staccato, pedal, slur, acc-natural | typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew that differs per page, light blur + noise, JPEG q80 | worn photocopies scanned in grey: 1.5-3.5 deg skew per page, bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35 |
| `perf-pages-10`<br>Forty Variations for piano - 10-page document | piano | Piano (True) | 10 | ledger-above, chord, beam, staccato, note-16th, note-32nd, ledger-below, tuplet-3 | typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew that differs per page, light blur + noise, JPEG q80 | worn photocopies scanned in grey: 1.5-3.5 deg skew per page, bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35 |
| `perf-pages-20`<br>Forty Variations for piano - 20-page document | piano | Piano (True) | 20 | ledger-above, chord, beam, note-16th, dot, staccato, ledger-below, note-32nd | typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew that differs per page, light blur + noise, JPEG q80 | worn photocopies scanned in grey: 1.5-3.5 deg skew per page, bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35 |
| `perf-pages-40`<br>Forty Variations for piano - 40-page document | piano | Piano (True) | 40 | ledger-above, chord, beam, note-16th, dot, staccato, ledger-below, note-32nd | typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew that differs per page, light blur + noise, JPEG q80 | worn photocopies scanned in grey: 1.5-3.5 deg skew per page, bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35 |
| `perf-piano-a3-300dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-100dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-150dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-200dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-300dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-400dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-a4-600dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |
| `perf-piano-letter-300dpi`<br>Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres) | piano | Piano (True) | 1 | ledger-above, beam, chord, note-16th, dot, ledger-below, slur, staccato | typical flatbed scan: grey, -0.8 deg skew, slight lighting gradient, light blur + sensor noise, JPEG q80 | binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before thresholding, salt & pepper, toner speckles |

## Validation

`_validate/validate.py` is an adapted copy of `corpus/challenge/_validate/validate.py` (same truth parser, MIDI comparison, PDF checks and pixel comparison). For every item it checks:

- all seven files present; `truth.musicxml` passes the MusicXML 4.0 XSD (`xmllint`) and parses in music21;
- every PDF opens, renders, has no fonts, no text and at least one image per page (image-only);
- `meta.json`: id = folder, family = parent folder, title, `symbols[]` (taxonomy tags or `x-*`), `layout` (a layout tag), `expected.parts[]`, `expected.must_not_split` (bool), `counts` (a positive count for every taxonomy symbol listed), `degradations` with seed and parameters for `scan.pdf` and `scan-severe.pdf`, `dpi`, `pages` (= clean.pdf pages), CC0/public-domain licence; the generator's own verification record has no failed check;
- the harness tagger (`tools/coverage.mjs` `extract()`, via `_validate/tagcount.mjs`) finds every declared taxonomy tag in the truth (except `stanza-text`, which MusicXML cannot encode) and warns about tags it finds that meta does not declare;
- `engraving.ly` is re-rendered with LilyPond 2.24 in a scratch folder: every truth attack (onset, pitch; ties merged, grace notes separate, cue notes silent, unpitched notes at their `<midi-unpitched>` key) and every lyric syllable must match LilyPond's MIDI, and `clean.pdf` must match a fresh raster of the LilyPond PDF (ink overlap >= 0.97 both ways, page by page).

Each family generator additionally checked its truth against LilyPond's own layout (grob/event dumps of note heads, stems, beams, flags, accidentals, rests, articulations, dynamics, lyrics, barlines, voltas, clefs, keys, times, system/page starts); see `<family>/_tools/README.txt` and `meta.validation`.

Result: **102/102 items pass**, 102 LilyPond renders, every MIDI comparison exact. layouts 20/20; lyrics 2/2; marks 9/9; notes 10/10; percussion 1/1; perf 21/21; pitch 12/12; rests 9/9; structure 8/8; time 10/10;

Warnings (not failures):

- `layouts/choir-sab-summer-song`: meta.notes missing (truth limitations not stated)
- `layouts/cross-staff-piano-arpeggio-study`: LilyPond printed 7 warning line(s): engraving.ly:40:39: warning: no viable initial configuration found: may not find good beam slope
- `layouts/lead-sheet-long-road`: in truth (harness tagger) but not declared in meta.symbols: ['lyrics-melisma']
- `layouts/melody-flute-air`: meta.notes missing (truth limitations not stated)
- `layouts/string-quartet-minuet`: meta.notes missing (truth limitations not stated)
- `layouts/two-voices-piano-song-without-words`: meta.notes missing (truth limitations not stated)
- `notes/nt07-grace-notes`: in truth (harness tagger) but not declared in meta.symbols: ['chord']
- `notes/nt08-cue-notes`: in truth (harness tagger) but not declared in meta.symbols: ['chord']
- `notes/nt09-tremolos`: in truth (harness tagger) but not declared in meta.symbols: ['tuplet-2']
- `perf/perf-pages-05`: declared but the harness tagger finds none in truth: ['text-expression']
- `perf/perf-pages-10`: declared but the harness tagger finds none in truth: ['text-expression']
- `perf/perf-pages-20`: declared but the harness tagger finds none in truth: ['text-expression']
- `perf/perf-pages-40`: declared but the harness tagger finds none in truth: ['text-expression']
- `rests/rst05-multibar-rests`: in truth (harness tagger) but not declared in meta.symbols: ['rest-whole-bar']
- `structure/str05-fine-dc-al-fine-piano`: declared but the harness tagger finds none in truth: ['text-expression']
- `structure/str06-breaks-two-pages-song`: scan-severe.pdf has 1 pages, clean.pdf 2 (check meta.degradations: spread/merged capture?); in truth (harness tagger) but not declared in meta.symbols: ['lyrics-melisma']
- `structure/str08-variations-twelve-pages-piano`: declared but the harness tagger finds none in truth: ['text-expression']
- `time/t08-ties-systems-pages`: scan-severe.pdf has 1 pages, clean.pdf 2 (check meta.degradations: spread/merged capture?)

Most warnings are definitional: the harness tagger counts chords and tuplet markings on grace/cue notes and on two-note tremolos (encoded with `<time-modification>` 2:1), multi-bar rests as whole-bar rests too, and "To Coda" as a separate tag; two scan-severe files capture a 2-page score as one open-book spread on purpose.

Re-run: `/Users/d.sloane/music/.venv/bin/python corpus/coverage/_validate/validate.py --jobs 48` (about 2 minutes; add `--no-render` for the static checks only, `--only family[/id],...` to select).

## Counting conventions

Counts in `meta.counts` are read back from `truth.musicxml` by each family generator; the rules are written in each meta.json (`count_rules` / `counting_rules` / `count_conventions`). Differences to keep in mind:

- `note-*`, `dot`, `acc-*`, `ledger-*`, `tie`: per notehead in notes/pitch/time/marks/perf; per note event (a chord once) in layouts/lyrics/percussion (`layouts/_tools/count_symbols.py`). `chord`, `flag`, `stem-*`: per stem.
- Note-family tags count main notes only (not grace or cue notes) in the notes family.
- Clef/key/time/barline tags: one per MusicXML element and part (a quartet counts four) in most families; score-wide marks once per score position in structure and layouts.
- `stanza-text` has no MusicXML element; it is counted from the engraving (`printed_not_in_truth`).
- `tools/coverage.mjs` uses its own tagger on truth and app output alike, so its per-tag accuracies do not depend on these differences.

## Truth limitations (summary; each meta.json `notes` has the item-specific list)

- Courtesy clefs, keys and time signatures at system ends are printed but implied in MusicXML (not counted).
- Stanza numbers and whether an ottava reads "8va" or "8" cannot be encoded.
- Two-note tremolos: both notes carry the printed value with `<time-modification>` 2:1.
- Multi-bar rests: one measure rest per bar plus `<multiple-rest>`; old-style rest symbols are not encoded glyph by glyph.
- Rest heights use `<display-step>/<display-octave>` (MuseScore convention); placement of marks is only above/below.
- Unpitched percussion: `<unpitched>` display positions (treble positions; a one-line staff uses B4) and `<midi-unpitched>` instruments.

## Evaluating the app

```
cd /Users/d.sloane/music/mvp
node tools/eval.mjs --set coverage --jobs 48 --out work/eval-coverage-baseline.json            # accuracy (OCR on)
node tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 --out work/eval-coverage-perf.json   # speed/memory
cd .. && node tools/coverage.mjs --eval mvp/work/eval-coverage-baseline.json --perf mvp/work/eval-coverage-perf.json
```

`tools/coverage.mjs` writes `docs/COVERAGE.md` and `docs/coverage.json`: per tag occurrences, how often the app emits it, accuracy on clean/scan/scan-severe, status (supported >= 0.8, partial, unsupported < 0.2), confusion; per layout part structure scores; ms/page and peak memory by dpi, page size and page count.

