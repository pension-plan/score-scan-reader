# Challenge corpus: synthetic scanned sheet music with exact truth

123 items in 6 categories, 365 damaged scan PDFs. Every item is a LilyPond engraving with an exact MusicXML 4.0 truth, an undamaged raster (`clean.pdf`) and one to three image-only "scans" with recorded, seeded damage. The set stresses the converter (scanned PDF to MusicXML 4.0, lyrics kept, two voices on one staff split into parts, piano grand staves never split) on the edge cases listed per item below.

## Layout of an item

`<category>/<id>/` holds:

| file | content |
|---|---|
| `engraving.ly` | LilyPond 2.24 source of the page(s) |
| `truth.musicxml` | exact truth, MusicXML 4.0 partwise, XSD-valid (`mvp/work/schema/musicxml.xsd`) |
| `clean.pdf` | undamaged image-only raster of the engraving (mostly 300 dpi) |
| `scan.pdf` | damaged image-only PDF (the main test file) |
| `scan-mild.pdf`, `scan-severe.pdf` | same page(s) with lighter / heavier damage (all items except the 4 `degradation/*-clean` controls, which have `scan-mild.pdf` only) |
| `meta.json` | `id, category, title, edge_cases[], expected{parts[], must_not_split, shared_staves[[..]], notes}, degradations{<file>: params + seed}, dpi, license`, plus truth limitations and generator validation details |
| `ATTRIBUTION.txt` | sources and licences |

`lyrics/lyr06-amazing-grace-textblock` also has `truth-underlaid.musicxml` (stanzas 4-6 of the text block underlaid as lyric lines 4-6; see its meta).

`manifest.json` here is the array of all meta objects (the six `<category>/manifest.json` merged), each with `path`, `scan_files`, `eval_ids`, `damage_families` (normalised damage tags per scan file) and `validation_challenge` added.

## Categories

| category | items | scan files | focus |
|---|---:|---:|---|
| voices | 7 | 21 | Voice separation: closed SATB/SAB/TTBB/SSAA scores with two voices per staff that must become separate parts, crossings, unisons, "a 2"/"unis.", divisi, cross-staff voices, choir + piano (piano must stay one part). |
| rhythm | 8 | 24 | Rhythm and duration: tuplets of every kind, ties across barlines/systems/pages, double dots, meter changes and irregular meters, multi-bar rests, every rest value, grace notes, fermatas, dense 32nd/64th runs. |
| pitch | 8 | 24 | Pitch spelling: 7-sharp/7-flat keys and key changes, clef changes (alto/tenor/treble/bass, mid-bar), accidental carry/cancel rules, double sharps/flats, ledger-line extremes, 8va/8vb, enharmonic respelling, chromatic closed-score SATB. |
| lyrics | 8 | 24 | Lyrics: long melismas and extenders, 6 stacked stanzas, refrains, translations in italics, four independent lyric lines in closed SATB, text-block stanzas that must not be underlaid, elisions, multilingual text with diacritics. |
| layout | 7 | 21 | Page layout: 12-page piano score, closed choir + piano with hidden staves, 3-staff organ in landscape, cross-staff beams, cue notes and small staves, bracket vs brace, one-system page under a text-heavy title block. |
| degradation | 85 | 251 | Controlled damage sweep: 4 simple pieces x 21 damage types (22 for the 2-page piece) x 3 strengths; isolates the effect of each kind of scan damage. |

## Damage coverage

Each scan file records its damage steps, parameters and seed in `meta.json` (`degradations`). The six generators log damage in different shapes; `_validate/damage.py` maps them onto common families (heuristic, used for reporting only). Files per family:

noise 355, skew 236, blur 194, jpeg 105, paper_colour 97, lighting 78, pencil 61, stain_foxing 55, curl_gutter 49, low_dpi 48, jpeg_low 43, photocopy_bilevel 41, bleed_through 39, perspective 36, saltpepper 35, holes_staple 28, high_dpi 26, crop 23, ink_fade 20, rot180 20, spread_2up 20, halftone_moire 20, rot90 19, scale_mismatch 12, clean_control 4

Scan image resolutions (files per dpi): 100: 14, 110: 2, 120: 5, 125: 1, 150: 26, 200: 38, 250: 14, 300: 239, 400: 12, 600: 14. Skew ranges from 0.3 to 10 degrees; 90- and 180-degree pages, mixed page orientation, page-scale mismatch, 2-up spreads, JPEG quality 15-60 and binarised photocopies occur in every category.

## Items: voices

| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| `satb-closed-crossing-unisons`<br>O God, Our Help in Ages Past (closed SATB: crossings and unisons) | Soprano, Alto, Tenor, Bass (False) | satb_closed, shared_staff_two_voices, voice_crossing_alto_above_soprano, voice_exchange_soprano_alto, voice_crossing_tenor_below_bass, unison_one_head_two_stems, unison_one_head_one_stem, unison_unequal_durations_two_heads, unison_dotted_half_final, one_voice_rests_other_sings, lyrics_only_under_treble_staff, multi_verse, pickup, no_part_labels, three_four_time, key_signature_flat | yellowed RGB scan, foxing, bleed-through, pencil circles/breath marks, 2.3 deg skew | clean office scan: 0.6 deg skew, light texture and noise | thin binarized photocopy at 120 dpi, 6.5 deg skew, faded ink, salt-and-pepper |
| `satb-closed-lyrics-both-staves-de`<br>Nun danket alle Gott (closed SATB, German, lyrics under both staves, lyrics switch voice) | Sopran, Alt, Tenor, Bass (False) | satb_closed, shared_staff_two_voices, lyrics_under_each_staff, lyrics_lower_staff_bass, lyric_line_switches_voice, independent_bass_rhythm_lyrics_offset, one_voice_rests_other_sings, whole_bar_rests_in_one_voice, part_labels_german_center_column, unison_one_head_two_stems, german_umlauts, dynamics, fermata, common_time_symbol | phone photo of a book page: keystone perspective, page curl + gutter shadow, vignette, motion blur | careful phone photo: slight perspective, mild gradient | low-light phone photo: strong keystone, deep curl, dark vignette, motion + focus blur, heavy noise, JPEG q18 |
| `sab-cross-staff-alto`<br>All Things Bright and Beautiful (SAB: 3 parts on 2 staves, cross-staff alto) | Soprano, Alto, Baritone (False) | sab_three_parts_two_staves, shared_staff_two_voices, single_voice_lower_staff, voice_moves_to_other_staff, cross_staff_alto_on_bass_staff, part_labels_full_then_abbrev, lyrics_only_under_treble_staff, multi_verse, key_signature_sharps | office photocopy from a ring binder: 3 punch holes, staple, thick ink, right edge cropped through the staff ends, 1.2 deg skew | high-resolution (400 dpi) flatbed scan, 0.4 deg skew | page fed upside down (180 deg) into a fax-like thick binarized copier at 150 dpi, 3.5 deg skew, punch holes, dark scanner border |
| `satb-open-divisi-midpiece`<br>Ave verum corpus (open score; divisi appears mid-piece) | Soprano, Alto, Tenor, Bass (True) | satb_open_score, divisi_mid_piece, divisi_two_voices_one_staff_same_part, divisi_chords_one_stem, bass_octave_divisi_chord, chords_must_stay_chords, div_unis_markings, tenor_treble_8vb_clef, lyrics_under_every_staff, latin_text, part_labels_full_then_abbrev, multi_page, dynamics, fermata, accidental_natural | 2-page flatbed scan; page 2 placed sideways (rotated 90 deg) and photocopied at 96.5%; bleed-through of the facing page | 2-page clean high-resolution scan at 600 dpi, slight skews 0.3/-0.5 deg | open book scanned as one 2-up double-page spread at 150 dpi: gutter shadow and curl, 3 deg skew, yellowed paper, JPEG q28 |
| `ttbb-treble8-a2-unis`<br>Integer vitae (TTBB closed score, octave treble clef, a 2 / unis.) | Tenor I, Tenor II, Bass I, Bass II (False) | ttbb_closed, treble_8vb_clef_octave, shared_staff_two_voices, a2_one_voice_both_parts, unis_one_voice_both_parts, divided_again_after_a2, unison_one_head_two_stems, part_labels_roman_numerals, lyrics_only_under_upper_staff, latin_text, eighth_notes, dynamics, fermata | thick binarized photocopy at 200 dpi with a coffee ring, 4 deg skew | flatbed scan, 0.5 deg skew, light coffee ring | 100 dpi, 9.5 deg skew, out of focus, JPEG q15 (the clef 8 is barely visible) |
| `ssaa-two-treble-staves-piano`<br>Love Came Down at Christmas (SSAA on two treble staves + piano) | Soprano I, Soprano II, Alto I, Alto II, Piano (True) | ssaa_closed, two_treble_choir_staves, shared_staff_two_voices, piano_grand_staff, piano_rh_two_voices_must_not_split, piano_chords_must_stay_chords, choir_tacet_full_bar_rests, merged_full_bar_rests, piano_doubles_choir, lyrics_only_under_top_choir_staff, multi_verse, part_labels_roman_numerals, three_four_time, key_signature_sharps, multi_page | reproduction printed with a halftone screen (tinted paper), rendered at 600 dpi and rescanned at 200 dpi -> moire; page 2 photocopied at 97%; 1.5 / -0.8 deg skew | clean 2-page scan, 0.4 / 0.2 deg skew | rehearsal copy at 110 dpi: heavy pencil (circled notes, part reminders, breath marks), red-pen circles, foxing, 7 / -5 deg skew, page 2 at 95%, motion blur, JPEG q20 |
| `satb-closed-ties-solo-amen-chords`<br>Hark! the Herald Angels Sing (closed SATB, S A / T B labels, ties vs re-attacks, bass solo, chords on one stem) | Soprano, Alto, Tenor, Bass (True) | satb_closed, part_labels_single_letters, unison_whole_phrase_two_stems, tie_in_one_voice_reattack_in_other, one_voice_rests_other_sings, bass_solo_lower_staff_lyrics, lyrics_lower_staff_only_for_solo, chords_on_soprano_stem_closed_score, bass_octave_chord_on_stem, chords_must_stay_chords, merged_rests, cut_time_alla_breve, dynamics, fermata | copy on light-blue paper scanned at 150 dpi with the lid open: dark top border, strong lighting gradient, -1.8 deg skew, JPEG q30 | office scan, 0.7 deg skew | thin binarized copy at 125 dpi, right edge cropped through the staff ends, 10 deg skew, speckles |

## Items: rhythm

| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| `rh01-tuplet-etude`<br>Tuplet Etude (flute) | Flute (False) | eighth_triplets, quarter_triplets, half_note_triplets_cut_time, tuplet_with_rests, tuplet_mixed_values, quintuplet_16ths, quintuplet_8ths, sextuplet, septuplet, implied_triplets_no_number, duplets_6_8, duplets_12_8, quadruplets_6_8_12_8, sixteenth_triplets, thirtysecond_triplets, beam_across_two_tuplets, tuplet_inside_longer_beam, tie_into_tuplet, beam_across_rest_in_tuplet, beam_across_rest_6_8, time_signature_changes, common_time_symbol, cut_time_symbol, numeric_4_4_after_C, compound_6_8, compound_12_8, courtesy_time_signature_at_system_end, fermata_on_rest, multi_page, pencil_fake_tuplet_numbers | coloured_paper_rgb, paper_texture, pencil, rotation_+1.8deg, gradient, blur, noise, jpeg_q45 | paper_texture, rotation_-0.5deg, blur, noise, jpeg_q60 | coloured_paper_rgb, paper_texture, curl, gutter, double_page_spread_2up, perspective_phone_capture, vignette, motion_blur, noise, jpeg_q20 |
| `rh02-ties-dots-song`<br>Who Has Seen the Wind? (voice, ties and dots) | Voice (False) | pickup_anacrusis, incomplete_final_bar, ties_across_barlines, tie_across_system_break, tie_across_page_break, tie_across_time_signature_change, double_dotted_quarter, double_dotted_half, double_dotted_eighth_plus_32nd, dotted_rhythms, syncopation, slur_on_repeated_pitch_not_tie, lyrics, lyric_melisma_extender, lyrics_with_ties, vocal_flags_unbeamed, time_signature_changes, compound_6_8, compound_9_8, multi_page, binarized_photocopy, page_rotated_180, page_scale_mismatch | punch_holes, crop, rotation_+0.8deg, speckle, binarized_photocopy_thin | paper_texture, rotation_+0.6deg, noise, jpeg_q60 | ink_weight, rotation_-1.2deg, rotation_+2deg, page_scale_mismatch, page_rotated_180deg_p[1], binarized_photocopy_thick, saltpepper |
| `rh03-meter-changes-piano`<br>Changing Meters (piano) | Piano (True) | piano_grand_staff_must_not_split, two_voices_in_right_hand, time_signature_changes, irregular_meter_5_8, irregular_meter_7_8, beaming_3_2_and_2_2_3, half_note_beat_3_2, compound_9_8, meter_2_4, cut_time_symbol, common_time_symbol, numeric_4_4, courtesy_time_signature_at_system_end, whole_bar_rest_one_staff_only, pickup_anacrusis, incomplete_final_bar, tie_across_system_break, tie_across_time_signature_change, chord_tie_across_barline, double_dotted_chord, tie_quarter_to_16th, beam_across_rest, fermata_all_staves, phone_capture | coloured_paper_rgb, paper_texture, perspective_phone_capture, blotch, vignette, shadow, blur, noise, jpeg_q40 | coloured_paper_rgb, paper_texture, perspective_phone_capture, vignette, blur, noise, jpeg_q60 | coloured_paper_rgb, paper_texture, perspective_phone_capture, shadow, gradient, motion_blur, noise, downsampled_100dpi, jpeg_q15 |
| `rh04-rest-zoo-part`<br>Interlude - oboe part (every rest type, multi-bar rests) | Oboe (False) | multi_measure_rest_hbar, multi_measure_rest_church_symbols, rehearsal_marks, general_pause_fermata_on_whole_bar_rest, whole_bar_rest_3_4, whole_bar_rest_6_8, whole_bar_rest_4_2_breve, plain_whole_rest_not_measure_rest, breve_rest, whole_rest, half_rest, quarter_rest, eighth_rest, 16th_rest, 32nd_rest, 64th_rest, dotted_quarter_rest, dotted_eighth_rest, double_dotted_eighth_rest, double_dotted_half_rest, rest_in_triplet, rest_in_duplet, beam_across_rest_6_8, beam_across_rest_in_triplet, 64th_notes, fermata_on_rest, time_signature_changes, meter_4_2, cut_time_symbol, page_rotated_90, high_dpi_400, halftone_moire, skew_10_degrees | paper_texture, rotation_+2.5deg, page_rotated_90deg, noise, saltpepper, jpeg_q50 | paper_texture, rotation_+0.5deg, noise, jpeg_q60 | paper_texture, halftone, rotation_+10deg, blur, noise, jpeg_q35 |
| `rh05-graces-fermatas`<br>Air with Graces (violin and piano) | Violin, Piano (True) | acciaccatura, appoggiatura, grace_group_16ths, grace_group_32nds, grace_at_bar_start, grace_before_first_note, unslashed_single_grace, fermata_on_note, fermata_on_rest, fermata_on_chord, simultaneous_fermatas_all_staves, sixteenth_beamed_groups, 32nd_beamed_groups, dotted_16th_32nd, dotted_eighth_32nd_32nd, beam_across_16th_rest, beamlet_hook, tie_quarter_to_16th, piano_grand_staff_must_not_split, instrument_plus_piano, coffee_stain, foxing, bleed_through, yellowed_paper_rgb | coloured_paper_rgb, paper_texture, bleed_through, foxing, coffee, rotation_-0.7deg, gradient, blur, noise, jpeg_q55 | coloured_paper_rgb, paper_texture, bleed_through, foxing, blur, noise, jpeg_q60 | ink_dropout, coloured_paper_rgb, paper_texture, bleed_through, foxing, coffee, rotation_+1.4deg, blur, noise, jpeg_q20 |
| `rh06-closed-satb-crossrhythm`<br>O God, Our Help in Ages Past (closed SATB, cross-voice rhythms) | Soprano, Alto, Tenor, Bass (False) | satb_closed_score, two_voices_per_staff_split, cross_voice_rhythm_differences, triplets_against_duplets, tuplet_in_one_voice_only, tie_in_one_voice_only, rest_in_one_voice_only, whole_bar_rest_lower_voice, unison_shared_notehead, dotted_vs_straight_between_voices, fermatas_at_different_onsets, pickup_anacrusis, incomplete_final_bar, lyrics, two_verses, lyrics_on_lower_staff_with_own_rhythm, lyric_melisma, high_dpi_600, halftone_moire, low_dpi | paper_texture, halftone, rotation_-1.2deg, noise, jpeg_q60 | paper_texture, rotation_+0.3deg, noise, jpeg_q60 | paper_texture, rotation_+1.5deg, blur, noise, jpeg_q15 |
| `rh07-compound-meter-fiddle`<br>The Crooked Road (fiddle: jig, slip jig, slide) | Fiddle (False) | compound_6_8, compound_9_8, compound_12_8, hemiola_bar_in_3_4, pickup_eighth, incomplete_final_bar, beam_across_rest_6_8, siciliano_dotted_figures, dotted_rests, duplet_12_8, grace_cuts_acciaccatura, plain_grace, double_stop_chord, chord_tie, tie_across_barline_and_time_change, fermata_mid_piece, rehearsal_marks, low_dpi_150, staple, punch_holes, pencil_annotations, cropped_edges, skew_4_and_7_degrees, gutter_shadow | paper_texture, staple, punch_holes, rotation_+4deg, gutter, saltpepper, noise, jpeg_q50 | paper_texture, rotation_+0.7deg, noise, jpeg_q60 | paper_texture, pencil, crop, crop, rotation_+7deg, perspective_phone_capture, blur, jpeg_q20 |
| `rh08-dense-runs-piano`<br>Toccatina (piano: 16th/32nd/64th runs) | Piano (True) | piano_grand_staff_must_not_split, two_voices_in_right_hand, sixteenth_beamed_groups, 32nd_run, 64th_run, sextuplets, sixteenth_triplets, dotted_16th_32nd, double_dotted_eighth_32nd, dotted_eighth_32nd_32nd, beam_across_rest, beam_starting_after_rest, beamlet_hooks, tie_quarter_to_16th, fermata_all_staves, motion_blur, pencil_fingerings, binarized_thick_low_dpi_100 | paper_texture, pencil, motion_blur, blur, noise, jpeg_q35 | paper_texture, blur, noise, jpeg_q60 | rotation_-0.9deg, binarized_photocopy_thick |

## Items: pitch

| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| `pitch-keysig-odyssey`<br>Odyssey Through the Keys (solo violin) | Violin (False) | key_change_mid_piece, key_7_sharps, key_7_flats, key_cancellation_naturals, enharmonic_key_change, key_change_mid_system, key_change_without_double_bar, courtesy_key_signature_at_line_end, double_sharp, double_flat, natural_in_sharp_key, natural_in_flat_key, enharmonic_spelling_B_sharp_C_flat_F_flat_E_sharp, octave_boundary_spelling, minor_key_final_section | yellowed paper (RGB) with texture and bleed-through, 3.5 deg skew, light gradient, slight focus blur, noise, JPEG q40 | clean office scan: 0.6 deg skew, grey, light noise, JPEG q60 | 120 dpi, old yellowed copy: coffee ring + foxing, strong bleed-through, 9.5 deg skew, gradient + vignette, focus blur, noise, JPEG q20 |
| `pitch-clef-carousel`<br>Clef Carousel (viola and violoncello) | Viola, Violoncello (False) | clef_change_mid_staff, clef_change_mid_measure, alto_clef, tenor_clef, treble_clef_cello, clef_change_at_line_break_courtesy_clef, two_clef_changes_same_bar, same_staff_position_different_pitch, ledger_lines_in_alto_clef, phone_photo | phone photo: perspective keystone on dark desk, uneven light + vignette + warm cast, motion blur (3 px@300dpi, 20 deg), sensor noise, JPEG q45 (RGB) | gentle phone photo: small keystone, mild gradient, slight blur, JPEG q60 | page scanned sideways (rotated 90 deg) + 1.2 deg skew, two punch holes, 150 dpi grey, gaussian + salt-and-pepper noise, JPEG q30 |
| `pitch-accidental-storm`<br>Accidental Storm (flute study) | Flute (False) | accidental_carries_through_bar, barline_cancels_accidental_no_courtesy, courtesy_accidental_parenthesized, courtesy_accidental_unparenthesized, double_sharp, double_flat, natural_sharp_after_double_sharp, natural_flat_after_double_flat, chromatic_scale_ascending_sharps, chromatic_scale_descending_flats, tie_across_barline_accidental_restated, accidental_octave_specific, e_sharp, c_flat, binarized_photocopy | thick binarised photocopy: ink spread (+1 px), 1.5 deg skew, toner speckles, threshold 165 with noise -> 1-bit PNG | light grey photocopy: -0.5 deg skew, faint noise, JPEG q55 | thin light photocopy at 150 dpi: -2.2 deg skew, low threshold (105) with noise -> dotted/broken staff lines and thin stems, salt-and-pepper, 1-bit PNG |
| `pitch-ledger-ottava`<br>Heights and Depths (flute and tuba) | Flute, Tuba (False) | extreme_ledger_lines_high, extreme_ledger_lines_low, ottava_8va, ottava_8vb, ottava_starting_mid_measure, ottava_spanning_line_break, same_display_position_after_ottava, passage_written_with_and_without_ottava, pencil_annotations, cropped_staff_ends, halftone_moire, high_dpi | 400 dpi RGB: pencil circles / breath marks / words, page cropped through the staff starts (0.6 mm into the staff) and staff ends (0.8 mm), 0.8 deg skew, JPEG q55 | 400 dpi grey: slight crop of the system brackets, three pencil circles, 0.3 deg skew, JPEG q60 | halftone-screened reproduction (110 lpi, 45 deg) rescanned -> moire, bluish recycled paper, deeper crop (1.2 mm into staff starts and ends), 4 deg skew, JPEG q25 |
| `pitch-satb-chromatic-closed`<br>Abide with Me (SATB closed score, chromatic) | Soprano, Alto, Tenor, Bass (False) | satb_closed_score, shared_staff_accidentals, accidental_carried_from_other_voice, chromatic_voice_leading, german_augmented_sixth, enharmonic_spelling_Cb_A_natural, secondary_dominants, courtesy_accidental_parenthesized, barline_cancels_accidental_no_courtesy, natural_in_flat_key, lyrics_two_verses, pickup_measure, page_rotated_180 | sheet fed upside down: page rotated 180 deg (+0.7 deg skew), grey, light gradient, noise, JPEG q50 | upright office scan, 0.8 deg skew, grey, JPEG q60 | bound hymnal scanned upside down at 150 dpi: page curl + dark gutter shadow, rotated 180 deg, vignette, blur, noise, JPEG q15 |
| `pitch-ttbb-enharmonic-keys`<br>Now the Day Is Over (TTBB closed, enharmonic key change) | Tenor I, Tenor II, Baritone, Bass (False) | ttbb_closed_score, treble_8vb_clef, key_6_flats, key_6_sharps, enharmonic_key_change_same_sounding_music, key_cancellation_12_glyphs, key_change_mid_system, double_flat_in_chord, double_sharp_in_chord, b_sharp, shared_staff_accidentals, lyrics, staple, punch_holes, book_page_curl | photocopied page from a bound book: yellowed RGB paper, left page curl + gutter shadow, staple at top-left, three punch holes (scanner lid shows white), JPEG q55 | light gutter shadow, ivory paper, 0.4 deg skew, JPEG q60 | strong book curl with wavy warp and deep gutter, vertical camera shake (motion blur 5 px@300dpi), noise, JPEG q20 (RGB) |
| `pitch-enharmonic-song-2page`<br>Lead, Kindly Light (soprano, 2 pages, enharmonic chromaticism) | Soprano (False) | chromatic_ascending_with_sharps_in_flat_key, chromatic_descending_naturals_in_sharp_key, enharmonic_spelling_Cb_Fb_Bbb_B#_E#_F##, key_change_at_page_turn, courtesy_key_at_page_end, tie_across_barline_with_accidental, melisma_with_accidentals, lyrics, multi_page, double_page_spread_2up, page_scale_mismatch, bleed_through | open booklet scanned as one 2-up spread: ivory paper, bleed-through from the facing page, page 2 printed 3.5% smaller, inner-edge curl + gutter shadow, 0.9 deg skew, JPEG q50 (RGB) | two separate grey pages, page 2 scanned at 98.5% scale, different skews (+0.7 / -1.2 deg), JPEG q60 | phone photo of the open booklet at 110 dpi: 2-up spread with strong inner curl, page 2 at 103.5% scale, foxing, heavy bleed-through, perspective, vignette, blur, noise, JPEG q25 (RGB) |
| `pitch-satb-ledger-extremes`<br>All Things Bright and Beautiful (SATB closed, extreme ranges) | Soprano, Alto, Tenor, Bass (False) | satb_closed_score, ledger_lines_between_staves, soprano_to_D6, bass_to_A1, tenor_to_A4_in_bass_clef, alto_to_A3_below_treble, ledger_lines_near_lyrics, lyrics_two_verses, pencil_reminder_accidentals, coffee_stain, high_dpi_600, low_dpi_100 | 600 dpi RGB scan of a rehearsal copy: pencil circles, reminder sharps, breath marks and words, coffee ring at top right, 0.4 deg skew, JPEG q60 | 400 dpi grey, three pencil circles, -0.3 deg skew, JPEG q60 | 100 dpi grey, 6 deg skew, focus blur, heavy noise, JPEG q15 |

## Items: lyrics

| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| `lyr01-gloria-melisma-latin`<br>Gloria in excelsis - aria with very long melismas (Latin) | Soprano, Piano (True) | long_melisma, melisma_21_notes, sixteenth_note_runs, extender_line, extender_across_system_break, extender_across_barline, hyphen_across_melisma, melisma_with_tie, slurred_melisma, latin_text, voice_piano, must_not_split, single_verse | paper_texture, skew_1.2deg, uneven_lighting, focus_blur, gaussian_noise, jpeg_q45 | paper_texture, skew_0.5deg, gaussian_noise, jpeg_q60 | paper_texture, skew_3.5deg, motion_blur, gaussian_noise, salt_pepper, jpeg_q20, low_dpi_150 |
| `lyr02-abendlied-6-stanzas-de`<br>Abendlied (Der Mond ist aufgegangen) - 6 German stanzas, closed SATB | Soprano, Alto, Tenor, Bass (False) | stacked_verses_6, verse_numbers, german_umlauts, eszett, hyphenated_compounds, apostrophe_in_word, punctuation, satb_closed, lyrics_between_staves, extender_line, hyphen_across_melisma, pickup, multi_page, two_up_spread | two_up_spread, paper_texture, gutter_shadow, skew_0.8deg, focus_blur, gaussian_noise, jpeg_q50 | page_scale_mismatch, coloured_paper, skew_0.5deg, gaussian_noise, rgb_scan, jpeg_q60 | two_up_spread, faded_ink, paper_texture, skew_2.5deg, speckles, salt_pepper, binarized_thin_photocopy |
| `lyr03-anges-refrain-fr`<br>Les anges dans nos campagnes - 4 French stanzas + shared refrain line | Voice (False) | refrain_shared_line, stacked_verses_4, verse_numbers, french_diacritics, oe_ligature, diaeresis, french_punctuation_nbsp, apostrophe_elision, elision_tie, long_melisma, hyphen_across_melisma, melody_only, phone_photo, rotated_90 | coloured_paper, page_curl, phone_perspective, uneven_lighting, focus_blur, gaussian_noise, rgb_scan, jpeg_q50 | coloured_paper, skew_0.7deg, rgb_scan, jpeg_q60 | coloured_paper, page_curl, phone_perspective, uneven_lighting, motion_blur, rotated_90deg, gaussian_noise, rgb_scan, jpeg_q25, low_dpi_150 |
| `lyr04-veni-latin-italic-en`<br>Veni, veni, Emmanuel - Latin with italic English translation line | Voice (False) | translation_line_italic, two_languages, latin_text, unnumbered_lyric_lines, smaller_font_translation, extender_line, extender_across_barline, hyphen_across_melisma, rests_between_phrases, pickup, minor_key, halftone_moire, rotated_180 | halftone_moire, resample_aliasing, paper_texture, skew_1.5deg, gaussian_noise, jpeg_q55 | paper_texture, skew_0.6deg, focus_blur, jpeg_q60, high_dpi_400 | halftone_moire, resample_aliasing, paper_texture, skew_1deg, rotated_180deg, gaussian_noise, jpeg_q30, low_dpi_120 |
| `lyr05-calon-lan-satb-4-lines-cy`<br>Calon Lân - closed SATB with four independent lyric lines (Welsh) | Soprano, Alto, Tenor, Bass (False) | lyrics_under_different_staves, lyrics_above_staff, four_lyric_lines_closed_score, independent_texts_per_voice, independent_rhythms, welsh_text, circumflex, apostrophe_contractions, satb_closed, extender_line, coffee_stain, foxing, bleed_through, cropped_edges | coloured_paper, bleed_through, foxing, coffee_stain, skew_1deg, gaussian_noise, rgb_scan, jpeg_q50 | paper_texture, skew_0.3deg, gaussian_noise, jpeg_q60, high_dpi_600 | coloured_paper, bleed_through, coffee_stain, foxing, cropped_edges, skew_4deg, gaussian_noise, rgb_scan, jpeg_q25 |
| `lyr06-amazing-grace-textblock`<br>Amazing Grace - hymnal page, stanzas 4-6 as text block below the music | Soprano, Alto, Tenor, Bass (False) | text_block_stanzas, two_column_text_block, stacked_verses_3, verse_numbers, typographic_apostrophes, punctuation, satb_closed, lyrics_between_staves, pickup, short_melisma_extenders, hyphen_across_melisma, pencil_annotations, circled_notes, punch_holes, staple, binarized_thick | paper_texture, pencil_annotations, punch_holes, staple, skew_0.6deg, gaussian_noise, jpeg_q60 | paper_texture, punch_holes, fold_crease, skew_0.3deg, jpeg_q60 | ink_thicken, paper_texture, pencil_annotations, punch_holes, staple, skew_2deg, speckles, binarized_thick_photocopy |
| `lyr07-tu-scendi-elisions-it`<br>Tu scendi dalle stelle - Italian elisions, voice and piano | Canto, Pianoforte (True) | elision_tie, multiple_elisions_one_note, elision_after_comma, italian_text, accented_vowels, apostrophes, stacked_verses_2, verse_numbers, compound_meter_6_8, pickup, voice_piano, must_not_split, book_scan, page_curl, gutter_shadow, cropped_edges | coloured_paper, page_curl, gutter_shadow, uneven_lighting, focus_blur, gaussian_noise, rgb_scan, jpeg_q45 | paper_texture, skew_0.4deg, jpeg_q60 | coloured_paper, page_curl, gutter_shadow, cropped_edges, skew_7deg, focus_blur, gaussian_noise, rgb_scan, jpeg_q18 |
| `lyr08-dejlig-multilingual-scandi`<br>Dejlig er jorden - five stacked verses in EN/DA/SV/NO | Voice (False) | multilingual_verses, scandinavian_characters, ae_ligature, o_slash, a_ring, stacked_verses_5, verse_labels_with_language, verse_specific_melisma, hyphen_across_skip, sans_serif_lyrics, melody_only, low_dpi_100, skew_10deg | paper_texture, skew_1.8deg, focus_blur, gaussian_noise, jpeg_q40, low_dpi_100 | coloured_paper, skew_0.4deg, rgb_scan, jpeg_q60 | paper_texture, skew_10deg, motion_blur, gaussian_noise, salt_pepper, jpeg_q15, low_dpi_150 |

## Items: layout

| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |
|---|---|---|---|---|---|
| `variations-piano-12-pages`<br>Variations on "Ah! vous dirai-je, maman" - 12-page piano score with headers, voltas, key/time changes | Piano (True) | multi_page_10plus, page_numbers, running_headers, title_block_text, copyright_footer, tempo_text, section_heading_text, dynamics_text, repeats, volta_1st_2nd_endings, key_change, time_change, triplets, pedal_marks, piano_grand_staff, must_not_split, variation_starts_new_system, fermata, hairpin, cautionary_key_signature | ring-binder photocopies scanned at 200 dpi grey: punch holes, a different skew on every page, page 8 fed upside down (180 deg), 3 pages at a different scale, bleed-through of the reverse page, toner speckles, JPEG q50 | clean flatbed scan, 300 dpi grey, 0.5 deg skew, JPEG q85 | thin, faded binarised photocopy at 150 dpi (from 300): broken staff lines, 2-6 deg skew per page, page 5 upside down, salt & pepper, speckles |
| `anthem-satb-closed-piano-4-pages`<br>All Things Bright and Beautiful - SATB closed score + piano, 4 pages, hidden choir staves, endings, D.S. | Soprano, Alto, Tenor, Bass, Piano (True) | satb_closed_score, choir_plus_piano, bracket_vs_brace, piano_two_voices_on_rh_staff, hidden_empty_staves, systems_with_different_staff_counts, multi_page_3_4, page_numbers, running_headers, volta_1st_2nd_endings, stacked_verses_in_repeat, segno, to_coda, ds_al_coda, coda, rehearsal_marks, tempo_text, dynamics_text, lyrics, lyrics_on_both_choir_staves, must_not_split, ties, fermata | bound octavo scanned as a book: pages 2-3 as ONE 2-up image (double-page spread) with gutter shadow and page curl at the spine, yellowed paper (RGB), slight skew, vignette, JPEG q40 | flatbed 300 dpi RGB, cream paper, -0.6 deg skew, mild gutter | phone photos of two open double-page spreads (pages 1-2, 3-4): perspective/keystone, uneven lamp light, vignette, motion blur, 120 dpi, JPEG q20 |
| `organ-chorale-3-staves-landscape`<br>Nun danket alle Gott - organ on 3 staves (pedal), landscape, manualiter system, 1st/2nd endings | Organ (True) | organ_three_staves, pedal_staff, brace_on_manuals_only, landscape_page, hidden_empty_staff, systems_with_different_staff_counts, single_system_page, two_voices_on_manual_staff, volta_1st_2nd_endings, repeats, registration_text, tempo_text, must_not_split, fermata, page_numbers | landscape pages scanned portrait (all pages rotated 90/270 deg), 150 dpi RGB on yellowed paper with foxing, pencil registration notes and circled notes, 1.5 deg skew, JPEG q45 | 300 dpi grey, upright, 0.5 deg skew | thick dark binarised photocopy, 4 deg skew, page 2 rotated 90 deg, salt & pepper, staple and two punch holes |
| `nocturne-cross-staff-pedal-ds-coda`<br>Nocturne in E-flat - cross-staff beams, pedal marks, Segno / To Coda / D.S. al Coda | Piano (True) | cross_staff_beams, cross_staff_notes_lh_to_treble, cross_staff_notes_rh_to_bass, pedal_marks, segno, to_coda, ds_al_coda, coda, tempo_text, dotted_metronome_mark, expression_text, dynamics_text, hairpin, accidentals_cross_staff, piano_grand_staff, must_not_split, double_barline, ties, slurs, fermata | phone photo: perspective + keystone, page curl, uneven lighting, vignette, coffee ring stain, motion + focus blur, RGB, JPEG q35 | high-resolution 400 dpi grey flatbed scan, 1 deg skew | 150 dpi grey, 10 deg / -8 deg skew, heavy blur, noise, JPEG q15 |
| `hymn-descant-cue-notes-amen-small`<br>Old Hundredth - closed SATB, reduced-size descant staff with cue notes, Amen at a smaller staff size | Descant, Soprano, Alto, Tenor, Bass (False) | satb_closed_score, descant_small_staff, mixed_staff_sizes_on_page, cue_notes, amen_smaller_staff_size, separate_score_block, hidden_empty_staff, systems_with_different_staff_counts, multi_verse, stanza_number_labels, lyrics, split_measures_between_passes, pickup, fermata, tempo_text, section_heading_text, page_numbers | printed hymnal page: halftone screen + resampling moire, strong bleed-through, yellowed paper with foxing, gutter shadow and curl on the left, 200 dpi RGB, JPEG q55 | 300 dpi grey, 0.3 deg skew, faint bleed-through | 100 dpi (from 300) thin binarised copy of the halftoned page, 2.5 deg skew |
| `trio-minuet-bracket-vs-brace-dc`<br>Minuet and Trio - reduced string staves in a bracket above a braced piano, Fine / D.C. al Fine | Violin, Violoncello, Piano (True) | bracket_vs_brace, bracketed_treble_bass_pair_is_two_parts, mixed_staff_sizes_on_page, reduced_instrument_staves, instrument_names_first_system_only, piano_grand_staff, must_not_split, dc_al_fine, fine, repeats, key_change, section_heading_text, tempo_text, dynamics_text, hairpin, staccato, slurs, page_numbers | dark (thick) binarised photocopy at 300 dpi, staple, two punch holes, right edge cropped 2 mm into the staff ends | 300 dpi grey, 0.4 deg skew | page 1 skewed 6 deg, page 2 fed upside down (180 deg), 150 dpi grey, left/right edges cropped into the staves, salt & pepper, JPEG q25 |
| `song-one-system-poem-block`<br>A Red, Red Rose - a page with only one system, poem stanzas as a text block | Voice, Piano (True) | single_system_page, title_block_text, dedication_text, tempo_text, dynamics_text, copyright_footer, extra_stanzas_as_text_block_not_lyrics, pickup, lyrics, voice_piano, piano_grand_staff, must_not_split, stanza_number_label, fermata, hairpin | high-resolution 600 dpi RGB scan of an old yellowed copy: pencil annotations (circled notes, breath marks, words), foxing, a coffee ring, 0.8 deg skew, JPEG q60 | 300 dpi grey, 0.3 deg skew | phone photo at an angle: 7 deg rotation, strong keystone, vignette, motion blur, salt & pepper, 150 dpi, JPEG q18 |

## Items: degradation

Four pieces; every item of a piece shares its `engraving.ly` and `truth.musicxml` byte for byte (only the damage differs). Item id = `<piece>-<damage type>`.

| piece | title | expected parts | must_not_split | edge cases (music) |
|---|---|---|---|---|
| `agrace-satb` | Amazing Grace (SATB, closed score, 3 verses) | Soprano, Alto, Tenor, Bass | False | lyrics, multi_verse, satb_closed, multi_voice_staff, shared_staves, pickup, melisma, slurs, ties, compound_lyric_hyphen_over_melisma, hymn, key_signature, time_3_4 |
| `wind-melody` | Who Has Seen the Wind? (melody, 2 verses) | Voice | False | lyrics, multi_verse, melody, pickup, melisma, slurs, unequal_verse_syllables, key_signature, time_3_4, large_staff |
| `andantino-piano` | Andantino (piano, grand staff) | Piano | True | piano, grand_staff, must_not_split, grand_staff_multi_voice, chords, dynamics, slurs, staccato, fermata, key_signature |
| `twinkle-piano2p` | Theme and Variation on "Ah! vous dirai-je, maman" (piano, 2 pages) | Piano | True | piano, grand_staff, must_not_split, grand_staff_multi_voice, multi_page, double_barline, dynamics, slurs, fermata, chords |

| damage type | items | mild / scan / severe |
|---|---:|---|
| `clean` | 4 | control: lossless raster (scan) / normal good scan (mild); no severe file |
| `skew` | 4 | scanner-bed rotation 2 / 6.5 / 10 deg (2-page piece: pages skewed in opposite directions) |
| `rot90` | 4 | page sideways (90 deg); 2-page severe turns its pages in opposite directions |
| `rot180` | 4 | page upside down; 2-page piece: only page 2 upside down (mixed orientation) |
| `phone` | 4 | phone photo: perspective/keystone, hand shadow, vignette, warm cast, motion blur; colour 250/200 dpi |
| `book` | 4 | book scan: gutter shadow, page curl up to 13 mm, wave, dark open-lid border |
| `yellowed` | 4 | aged paper colour scan: fibres, edge darkening, brown faded ink, up to 150 foxing spots |
| `bleed` | 4 | mirrored reverse page (a different piece) showing through at 8 / 20 / 38 % |
| `stain-pencil` | 4 | coffee rings, pencil circles, handwritten words, fingerings, breath marks, arrows; severe adds highlighter + ballpoint |
| `holes-staple` | 4 | 2 / 3 / 4 punch holes, staple, folded corner; severe holes bite into staff starts |
| `crop` | 4 | tight crop, then header cropped and staff ends cut (never a note, clef or lyric) |
| `halftone` | 4 | halftone screens 150 / 110 / 85 lpi with moire (music rescaled to 0.97 / 0.93) |
| `jpeg` | 4 | JPEG quality 60, 30 (saved twice), 15 (saved twice) |
| `photocopy-thin` | 4 | 1-bit thresholds 115 / 85 / 70: staff lines break up |
| `photocopy-thick` | 4 | 1-bit thresholds 170 / 195 / 210 + ink spread: hollow heads fill in, toner specks, black borders |
| `lowdpi` | 4 | 150 / 100 / 100 dpi + blur + JPEG 45 |
| `highdpi` | 4 | 400 / 600 / 600 dpi with paper grain and dust |
| `blur` | 4 | focus blur + motion blur up to 14 px |
| `noise` | 4 | Gaussian sigma 10 / 25 / 45 + 0.2-3 % salt-and-pepper |
| `spread` | 4 | two pages on one landscape image (single-page pieces get a text-only facing page) |
| `scale` | 1 | 2-page piece only: pages copied at different sizes (97 / 94 / 88 % against 104 %) |
| `combo` | 4 | everything combined, up to 150 dpi, -7 deg, JPEG 25 |

## Truth conventions and limitations

Per-item limitations are in each `meta.json` (`truth_limitations` / `expected.notes`). Common to the set:

- Pitches are sounding pitches (8va/8vb and treble-8vb clefs resolved), with MusicXML octave-shift / clef-octave-change markers where printed.
- Lyrics printed once under a shared choir staff are attached to the voice they align with (usually Soprano or Tenor), following the corpus/synthetic convention.
- Beams, system/page breaks, positions and font sizes are not part of the truth. Repeats, voltas, D.S./D.C. are in notated order (not unrolled).
- In "a 2" / "unis." passages the second part is not drawn; its truth notes are verified copies of the printed line.
- Grace notes have no duration; cue notes are marked `<cue/>` (the eval harness skips both).
- Pencil marks, stains, holes, staples, bleed-through ghosts and handwritten words are damage, never music or lyrics. Crops never remove a note, clef or lyric.
- Stanzas printed as a text block below the music are not lyrics in the truth (lyr06 stores them as credits; the Burns poem in layout/song-one-system-poem-block is not encoded).

## Validation

`_validate/validate.py` (independent of the generators) re-checked all 123 items: **123/123 pass, none dropped**. Per item:

- every `truth*.musicxml` validates against `mvp/work/schema/musicxml.xsd` (xmllint) and parses with music21;
- every PDF opens (pdfinfo) and renders (pdftoppm), has no fonts (pdffonts), no extractable text (pdftotext) and at least one image per page (pdfimages);
- `meta.json` has id (= folder), category (= parent folder), title, edge_cases, expected{parts, must_not_split, shared_staves, notes}, a degradations record with seed for every scan file, dpi and license; `expected.parts` equals the truth part names;
- `engraving.ly` is re-rendered with LilyPond 2.24.3 in a scratch folder: every truth attack (onset, pitch; ties merged) matches LilyPond's MIDI (grace notes and a leading-grace clock offset allowed for; a second `\score` placed at its best offset), and every truth lyric syllable matches a MIDI lyric event (onset, text);
- `clean.pdf` is compared page by page with a fresh raster of that render at the same dpi (ink masks, 2 px tolerance): every page matches (overlap 1.000);
- the eval harness scores every truth against itself as 1.0 on pitch, duration, rests, lyrics and parts (`node _validate/selfscore.mjs`).

Notes from the run: `voices/ttbb-treble8-a2-unis` has 31 truth attacks without their own MIDI note (the "a 2"/"unis." passages are printed once for two parts, by design); LilyPond warnings remain in `lyrics/lyr06` (page-count forced to 1), `layout/nocturne-cross-staff-pedal-ds-coda` (cross-staff beam slopes, one `\voiceXx` hint) and `layout/trio-minuet-bracket-vs-brace-dc` (page 1 compressed); the rendered pages still match `clean.pdf` and the truth. `layout/organ-chorale-3-staves-landscape` takes its notes from the music21 corpus encoding of BWV 252 (Greentree, "used by permission"); the composition is public domain, but re-encode from a public-domain edition if strict provenance of the encoding matters.

Full report: `_validate/report.json`.

## Rebuild and re-check

```sh
cd /Users/d.sloane/music
.venv/bin/python corpus/challenge/voices/_tools/run_all.py
.venv/bin/python corpus/challenge/rhythm/_tools/run_all.py
.venv/bin/python corpus/challenge/pitch/_tools/run_all.py
.venv/bin/python corpus/challenge/lyrics/_tools/run_all.py   (re-check: lyrics/_tools/verify.py)
.venv/bin/python corpus/challenge/layout/_tools/run_all.py
.venv/bin/python corpus/challenge/degradation/_tools/run.py
# independent validation of everything (about 30 s):
.venv/bin/python corpus/challenge/_validate/validate.py --jobs 96 --scratch /tmp/challenge-validate
# merged manifest + this README:
.venv/bin/python corpus/challenge/_validate/build_index.py
```

Each generator only writes inside its own category folder. Rebuilding is deterministic (fixed seeds).

The degradation PDFs are not in git (`.gitignore`); CI rebuilds them with `degradation/_tools/run.py` (cached on its sources) so the challenge gate scores all items. `layout/organ-chorale-3-staves-landscape` is restricted and is not in CI.

## Evaluation

```sh
cd /Users/d.sloane/music/mvp
node tools/eval.mjs --set challenge --jobs 48 --no-ocr --out work/eval-challenge-baseline.json
node tools/eval.mjs --set challenge --only lyrics --jobs 48 --out work/eval-challenge-baseline-lyrics-ocr.json
node tools/eval.mjs --set challenge --only voices/satb-closed-crossing-unisons/scan-mild --out /tmp/x.json   # one file
../.venv/bin/python ../corpus/challenge/_validate/analyze_eval.py work/eval-challenge-baseline.json --ocr work/eval-challenge-baseline-ocr.json --out work/eval-challenge-baseline.analysis.json
```

`--set challenge` scores every scan variant separately (id `<category>/<id>/<variant>`, variant = scan | scan-mild | scan-severe) against the folder's `truth.musicxml`; `--only` accepts ids or prefixes (`lyrics`, `voices/sab-cross-staff-alto`). Without `--set` the harness runs the unchanged synthetic + real benchmark.

### Baseline (979b4b123d46, dpi 200; aggregate = 0.3 pitch + 0.2 duration + 0.2 parts + 0.2 lyrics + 0.1 xml)

| category | files | aggregate (no OCR) | aggregate (OCR) | pitch | duration | parts | lyrics (OCR) | no output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| voices | 21 | 0.624 | 0.742 | 0.757 | 0.730 | 0.776 | 0.591 | 2 |
| rhythm | 24 | 0.699 | 0.728 | 0.698 | 0.461 | 0.759 | 0.894 | 2 |
| pitch | 24 | 0.552 | 0.604 | 0.442 | 0.551 | 0.556 | 0.758 | 1 |
| lyrics | 24 | 0.633 | 0.726 | 0.767 | 0.721 | 0.802 | 0.463 | 1 |
| layout | 21 | 0.570 | 0.612 | 0.471 | 0.489 | 0.618 | 0.780 | 3 |
| degradation | 251 | 0.722 | 0.777 | 0.728 | 0.698 | 0.842 | 0.777 | 26 |
| **all** | 365 | 0.689 | 0.747 | 0.697 | 0.664 | 0.798 | 0.752 | 35 |

By strength: scan 0.715 (pitch 0.734, 9 empty), scan-mild 0.761 (pitch 0.806, 8 empty), scan-severe 0.589 (pitch 0.545, 18 empty) (no OCR).

Controlled damage sweep (degradation category, mean aggregate over 4 pieces; mild / scan / severe):

| damage | mean | mild | scan | severe | pitch | empty outputs |
|---|---:|---:|---:|---:|---:|---:|
| rot90 | 0.150 | 0.150 | 0.150 | 0.150 | 0.000 | 12/12 |
| halftone | 0.373 | 0.150 | 0.355 | 0.615 | 0.262 | 6/12 |
| rot180 | 0.496 | 0.506 | 0.508 | 0.474 | 0.214 | 0/12 |
| noise | 0.503 | 0.872 | 0.314 | 0.325 | 0.430 | 4/12 |
| photocopy-thick | 0.619 | 0.807 | 0.666 | 0.384 | 0.542 | 1/12 |
| photocopy-thin | 0.642 | 0.873 | 0.848 | 0.203 | 0.623 | 3/12 |
| spread | 0.712 | 0.740 | 0.775 | 0.623 | 0.724 | 0/12 |
| blur | 0.726 | 0.859 | 0.821 | 0.499 | 0.731 | 0/12 |
| yellowed | 0.732 | 0.872 | 0.859 | 0.467 | 0.756 | 0/12 |
| combo | 0.786 | 0.873 | 0.841 | 0.645 | 0.801 | 0/12 |
| phone | 0.810 | 0.858 | 0.862 | 0.710 | 0.846 | 0/12 |
| crop | 0.823 | 0.870 | 0.799 | 0.800 | 0.876 | 0/12 |
| lowdpi | 0.845 | 0.866 | 0.850 | 0.819 | 0.932 | 0/12 |
| stain-pencil | 0.860 | 0.866 | 0.868 | 0.846 | 0.941 | 0/12 |
| bleed | 0.865 | 0.866 | 0.866 | 0.863 | 0.943 | 0/12 |
| skew | 0.865 | 0.866 | 0.865 | 0.865 | 0.943 | 0/12 |
| book | 0.866 | 0.865 | 0.875 | 0.857 | 0.941 | 0/12 |
| holes-staple | 0.867 | 0.856 | 0.876 | 0.867 | 0.944 | 0/12 |
| highdpi | 0.871 | 0.870 | 0.877 | 0.865 | 0.951 | 0/12 |
| jpeg | 0.872 | 0.872 | 0.869 | 0.874 | 0.951 | 0/12 |
| clean | 0.872 | 0.872 | 0.872 | - | 0.952 | 0/8 |
| scale | 0.975 | 0.974 | 0.970 | 0.980 | 0.989 | 0/3 |

Edge cases that fail completely at baseline (the produced MusicXML never contains the feature on any item or variant whose truth has it, and under 15 % of the affected notes come out with the right pitch and duration on the mild scans; all notes: 59%):

| edge case | items (degradation pieces counted once) | notes right (mild) | scored by eval | examples |
|---|---:|---:|---|---|
| fermatas | 28 | - | no | degradation/andantino-piano (x21 damage types), degradation/twinkle-piano2p (x22 damage types), layout/anthem-satb-closed-piano-4-pages |
| two voices on one staff | 9 | - | yes | degradation/andantino-piano (x21 damage types), degradation/twinkle-piano2p (x22 damage types), layout/anthem-satb-closed-piano-4-pages |
| repeats / volta endings | 4 | - | no | layout/anthem-satb-closed-piano-4-pages, layout/organ-chorale-3-staves-landscape, layout/trio-minuet-bracket-vs-brace-dc |
| cue-size notes | 1 | - | no | layout/hymn-descant-cue-notes-amen-small |
| tuplets (time-modification) | 7 | 0.2% | yes | layout/variations-piano-12-pages, rhythm/rh01-tuplet-etude, rhythm/rh03-meter-changes-piano |
| double sharps / double flats | 4 | 11.1% | yes | pitch/pitch-accidental-storm, pitch/pitch-enharmonic-song-2page, pitch/pitch-keysig-odyssey |
| 8va/8vb octave shifts | 1 | 8.8% | yes | pitch/pitch-ledger-ottava |
| double-dotted values | 4 | 0.0% | yes | rhythm/rh02-ties-dots-song, rhythm/rh03-meter-changes-piano, rhythm/rh04-rest-zoo-part |
| multi-bar rests | 1 | 0.0% | yes | rhythm/rh04-rest-zoo-part |
| grace notes | 2 | 0.0% | no | rhythm/rh05-graces-fermatas, rhythm/rh07-compound-meter-fiddle |

Never emitted as notation but notes partly right: key changes (5 items, 31% of notes right); time-signature changes (6 items, 35% of notes right); C clefs (alto/tenor) (1 items, 29% of notes right); 32nd/64th note values (5 items, 0% of notes right).

Details: `mvp/work/eval-challenge-baseline.analysis.json` (`feature_recall`, `edge_note_recall`, `edge_case_tags_mild`, `worst_items`, `damage_families`).

## Licences

All music is either public domain (traditional tunes, hymn tunes, Bach BWV 252, the "Ah! vous dirai-je, maman" theme, Amazing Grace / NEW BRITAIN, Old Hundredth) or composed for this corpus and dedicated to the public domain (CC0-1.0). All texts are public domain (Watts, Rinkart, C. F. Alexander, Ave verum corpus, Horace, Rossetti, Wesley, Claudius, Neale, Daniel James, Newton, Liguori, Ingemann, Willis, Baath-Holmberg, Burns, Lyte, Baring-Gould, Newman, Latin liturgy). Engravings, truth files, rasters and damaged scans are CC0-1.0. Each item's `meta.json` (`license`) and `ATTRIBUTION.txt` give the exact sources.

<details><summary>Licence strings in meta.json</summary>

- (22) Theme public domain (French air "Ah! vous dirai-je, maman", c. 1761); variation, setting and engraving CC0-1.0
- (21) Public domain melody (NEW BRITAIN, 1829) and text (John Newton, 1779); SATB setting and engraving CC0-1.0
- (21) Text public domain (Christina Rossetti, Sing-Song, 1872); melody and engraving CC0-1.0
- (21) Original composition and engraving, CC0-1.0
- (8) CC0-1.0 (music, engraving, scans); lyrics texts public domain where present
- (6) CC0-1.0 (music composed for this corpus; engraving, truth and scans CC0)
- (2) CC0-1.0 (composition, engraving, scans)
- (1) Text public domain (Isaac Watts, 1719); music and engraving CC0-1.0
- (1) Text public domain (Martin Rinkart, 1636); music and engraving CC0-1.0
- (1) Text public domain (Cecil Frances Alexander, 1848); music and engraving CC0-1.0
- (1) Text public domain (Ave verum corpus, 14th-century Latin hymn); music and engraving CC0-1.0
- (1) Text public domain (Horace, Odes I.22, c. 23 BC); music and engraving CC0-1.0
- (1) Text public domain (Christina Rossetti, 1885); music and engraving CC0-1.0
- (1) Text public domain (Charles Wesley, 1739; alt. G. Whitefield, 1753); music and engraving CC0-1.0
- (1) Text public domain (Rossetti 1872); music, engraving, truth and scans CC0-1.0
- (1) Text public domain (Watts 1719); music, engraving, truth and scans CC0-1.0
- (1) Text: public domain (Latin liturgy, Luke 2:14). Music: CC0-1.0 (own composition).
- (1) Text: public domain (M. Claudius, 1779). Music: CC0-1.0 (own melody and harmonisation).
- (1) Text: public domain (traditional French carol). Music: CC0-1.0 (own melody after the carol).
- (1) Texts: public domain (Latin hymn; J. M. Neale 1851). Music: CC0-1.0 (own melody).
- (1) Text: public domain (Daniel James, d. 1920). Music: CC0-1.0 (own four-part setting).
- (1) Melody (NEW BRITAIN, 1829/1831) and text (John Newton, 1779): public domain. Harmonisation: CC0-1.0.
- (1) Text: public domain (St Alphonsus Liguori, 1754). Music: CC0-1.0 (own pastorale setting).
- (1) Texts: public domain (Ingemann 1850, Willis 1850, Bååth-Holmberg 1884). Music: CC0-1.0 (own melody).
- (1) Public domain melody; variations, engraving and scans CC0-1.0
- (1) Text public domain (C. F. Alexander 1848); music, arrangement and engraving CC0-1.0
- (1) Public domain composition (Crüger 1647 / Bach BWV 252); intro, coda, layout and engraving CC0-1.0
- (1) Melody and texts public domain; harmonisation, descant and engraving CC0-1.0
- (1) Text public domain (Burns 1794); melody, accompaniment and engraving CC0-1.0

</details>
