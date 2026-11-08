"""Pitch challenge catalog: items, edge-case tags, expectations and damage recipes."""
from .items import mk_abide, mk_accstorm, mk_bright, mk_clefs, mk_dayover, mk_keys, mk_lead, mk_ledger

LIC = 'CC0-1.0 (music, engraving, scans); lyrics texts public domain where present'
ABIDE_COURTESY = []
DAY_COURTESY = []

PAPER_WHITE = {'op': 'paper', 'rgb': [245, 244, 240], 'texture': 2}
YELLOW = [236, 224, 196]


def att(*lines):
    return '\n'.join(lines)


ITEMS = [
    # ------------------------------------------------------------------ 1
    dict(
        id='pitch-keysig-odyssey', title='Odyssey Through the Keys (solo violin)', make=mk_keys(),
        edge_cases=['key_change_mid_piece', 'key_7_sharps', 'key_7_flats', 'key_cancellation_naturals',
                    'enharmonic_key_change', 'key_change_mid_system', 'key_change_without_double_bar',
                    'courtesy_key_signature_at_line_end', 'double_sharp', 'double_flat', 'natural_in_sharp_key',
                    'natural_in_flat_key', 'enharmonic_spelling_B_sharp_C_flat_F_flat_E_sharp',
                    'octave_boundary_spelling', 'minor_key_final_section'],
        expected_notes=(
            'One part (Violin), one staff, 32 bars of 4/4.  Key signature changes at bars 5 (C# major, 7 sharps), '
            '9 (Db major: 7 naturals + 5 flats), 13 (Cb major, 7 flats), 17 (B major: 7 naturals + 5 sharps), '
            '21 (F# major, no double bar), 25 (Gb major: 6 naturals + 6 flats, mid-system, no double bar) and 29 '
            '(A minor: 6 naturals).  Bars 9-28 are pairs of enharmonically equivalent keys, so the same staff '
            'positions must be read with different signatures.  A correct conversion has every <key> change at '
            'the right bar (fifths 7,-5,-7,5,6,-6,0) and spells B#4 (bar 6/7), F##5, Bbb4, Fb5, E#5, B#5 exactly; '
            'note B#4/B#5 belong to octave 4/5 (they sound C5/C6) and Cb5 to octave 5.  The cancellation naturals '
            'before each new signature are not notes.  The key change at bar 5 sits at a line break: LilyPond '
            'prints a courtesy key signature at the end of system 1.'),
        source='composed for this corpus', license=LIC,
        attribution=att('"Odyssey Through the Keys" - melody composed for the pitch challenge corpus (2026).'),
        layout_desc='single treble staff, 6 systems, explicit line breaks (4/6 bars per system)',
        damage={
            'scan.pdf': dict(dpi=200, seed=11001, jpeg=40,
                             summary='yellowed paper (RGB) with texture and bleed-through, 3.5 deg skew, light '
                                     'gradient, slight focus blur, noise, JPEG q40',
                             ops=[{'op': 'paper', 'rgb': YELLOW, 'ink_rgb': [40, 34, 30], 'texture': 6, 'fibers': 3,
                                   'bleed': 0.12},
                                  {'op': 'rotate', 'deg': 3.5, 'fill': [250, 250, 248], 'expand': True},
                                  {'op': 'lighting', 'gradient': 0.12, 'angle': 30},
                                  {'op': 'blur', 'radius_px300': 0.6},
                                  {'op': 'noise', 'sigma': 4, 'chroma': 1.5}]),
            'scan-mild.pdf': dict(dpi=300, seed=11002, jpeg=60,
                                  summary='clean office scan: 0.6 deg skew, grey, light noise, JPEG q60',
                                  ops=[PAPER_WHITE, {'op': 'rotate', 'deg': 0.6},
                                       {'op': 'blur', 'radius_px300': 0.4}, {'op': 'noise', 'sigma': 2},
                                       {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=120, seed=11003, jpeg=20,
                                    summary='120 dpi, old yellowed copy: coffee ring + foxing, strong bleed-through, '
                                            '9.5 deg skew, gradient + vignette, focus blur, noise, JPEG q20',
                                    ops=[{'op': 'paper', 'rgb': [222, 205, 170], 'ink_rgb': [48, 40, 34], 'texture': 8,
                                          'fibers': 4, 'bleed': 0.18},
                                         {'op': 'stain', 'cx': 0.70, 'cy': 0.36, 'r': 0.14, 'strength': 0.45,
                                          'rgb': [150, 100, 55]},
                                         {'op': 'foxing', 'n': 60, 'strength': 0.45},
                                         {'op': 'rotate', 'deg': -9.5, 'fill': [245, 245, 242], 'expand': True},
                                         {'op': 'lighting', 'gradient': 0.25, 'vignette': 0.2, 'angle': 200},
                                         {'op': 'blur', 'radius_px300': 1.6},
                                         {'op': 'noise', 'sigma': 6, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 2
    dict(
        id='pitch-clef-carousel', title='Clef Carousel (viola and violoncello)', make=mk_clefs(),
        edge_cases=['clef_change_mid_staff', 'clef_change_mid_measure', 'alto_clef', 'tenor_clef',
                    'treble_clef_cello', 'clef_change_at_line_break_courtesy_clef', 'two_clef_changes_same_bar',
                    'same_staff_position_different_pitch', 'ledger_lines_in_alto_clef', 'phone_photo'],
        expected_notes=(
            'Two parts (Viola, Violoncello), one staff each, 20 bars of 3/4 in F major.  Viola: alto clef, '
            'treble from bar 13 (at a line break: courtesy clef at the end of system 3) back to alto before beat 3 '
            'of bar 17.  Cello: bass -> tenor at bar 5 (line start, courtesy clef at end of system 1) -> treble '
            'before beat 2 of bar 6 -> tenor at bar 9 (line start) -> bass at bar 11 -> tenor before beat 2 of bar '
            '17 -> bass at bar 19.  Small mid-bar clefs change the pitch of every following note; a correct '
            'conversion places each <clef> change at the exact beat and keeps all pitches (e.g. cello bar 6: G4 '
            'in tenor clef then Bb4, D5 in treble clef).  Courtesy clefs at system ends are not clef changes '
            'of the following bar content beyond what is listed.'),
        source='composed for this corpus', license=LIC,
        attribution=att('"Clef Carousel" - duet composed for the pitch challenge corpus (2026).'),
        layout_desc='StaffGroup of two single staves, 5 systems x 4 bars',
        damage={
            'scan.pdf': dict(dpi=200, seed=12001, jpeg=45,
                             summary='phone photo: perspective keystone on dark desk, uneven light + vignette + '
                                     'warm cast, motion blur (3 px@300dpi, 20 deg), sensor noise, JPEG q45 (RGB)',
                             ops=[{'op': 'paper', 'rgb': [240, 238, 232], 'texture': 4},
                                  {'op': 'lighting', 'gradient': 0.15, 'blotch': 0.2, 'vignette': 0.3, 'warm': 0.06,
                                   'angle': 120},
                                  {'op': 'phone', 'margin': 0.06, 'bg': [62, 58, 54], 'jitter': 0.035},
                                  {'op': 'blur', 'motion_px300': 3, 'angle': 20},
                                  {'op': 'noise', 'sigma': 5, 'chroma': 2}]),
            'scan-mild.pdf': dict(dpi=250, seed=12002, jpeg=60,
                                  summary='gentle phone photo: small keystone, mild gradient, slight blur, JPEG q60',
                                  ops=[{'op': 'paper', 'rgb': [242, 240, 236], 'texture': 3},
                                       {'op': 'lighting', 'gradient': 0.1, 'angle': 60},
                                       {'op': 'phone', 'margin': 0.04, 'bg': [80, 76, 70], 'jitter': 0.015},
                                       {'op': 'blur', 'radius_px300': 0.5}, {'op': 'noise', 'sigma': 3}]),
            'scan-severe.pdf': dict(dpi=150, seed=12003, jpeg=30,
                                    summary='page scanned sideways (rotated 90 deg) + 1.2 deg skew, two punch holes, '
                                            '150 dpi grey, gaussian + salt-and-pepper noise, JPEG q30',
                                    ops=[PAPER_WHITE,
                                         {'op': 'holes', 'n': 2, 'side': 'left', 'd_mm': 6, 'offset_mm': 9,
                                          'spacing_mm': 80, 'fill': [30, 30, 32]},
                                         {'op': 'rotate', 'deg': 1.2},
                                         {'op': 'rot90', 'k': 1},
                                         {'op': 'noise', 'sigma': 9, 'saltpepper': 0.003},
                                         {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 3
    dict(
        id='pitch-accidental-storm', title='Accidental Storm (flute study)', make=mk_accstorm(),
        edge_cases=['accidental_carries_through_bar', 'barline_cancels_accidental_no_courtesy',
                    'courtesy_accidental_parenthesized', 'courtesy_accidental_unparenthesized', 'double_sharp',
                    'double_flat', 'natural_sharp_after_double_sharp', 'natural_flat_after_double_flat',
                    'chromatic_scale_ascending_sharps', 'chromatic_scale_descending_flats',
                    'tie_across_barline_accidental_restated', 'accidental_octave_specific', 'e_sharp',
                    'c_flat', 'binarized_photocopy'],
        expected_notes=(
            'One part (Flute), G major, 20 bars.  Bar 2: second C#5 has no sign (carried within the bar).  Bar 3: '
            'C5 is natural with NO printed natural (barline cancels the C# of bar 2).  Bar 6: D5 with a '
            'parenthesised courtesy natural; bar 8: C5 with an unparenthesised courtesy natural.  Bar 9: F##5, G#5, '
            'then F#5 printed as natural+sharp, then F5 natural.  Bar 11: Bb4, Bbb4, Bb4 (natural+flat), Ab4.  '
            'Bars 13-16: chromatic scales (sharps up, flats down; E#4 in bar 13; F5 natural in bar 14 then a '
            'parenthesised courtesy sharp on F#5 in bar 15).  Bars 17-18: G#4 tied over the barline; the next '
            'G#4 in bar 18 carries its sharp again.  Bar 19: C#5 then C4 without sign (accidentals only bind '
            'their own octave, so C4 is natural) then C5 with a natural sign.  Courtesy accidentals are '
            'encoded as <accidental cautionary="yes"> (with parentheses="yes" where printed in parentheses).'),
        source='composed for this corpus', license=LIC,
        attribution=att('"Accidental Storm" - study composed for the pitch challenge corpus (2026).'),
        layout_desc='single treble staff, 5 systems x 4 bars',
        damage={
            'scan.pdf': dict(dpi=300, seed=13001, format='png',
                             summary='thick binarised photocopy: ink spread (+1 px), 1.5 deg skew, toner speckles, '
                                     'threshold 165 with noise -> 1-bit PNG',
                             ops=[{'op': 'ink', 'weight': 1}, PAPER_WHITE, {'op': 'rotate', 'deg': 1.5},
                                  {'op': 'noise', 'speckle': 150},
                                  {'op': 'binarize', 'threshold': 165, 'noise': 18, 'pre_blur_px300': 0.6}]),
            'scan-mild.pdf': dict(dpi=300, seed=13002, jpeg=55,
                                  summary='light grey photocopy: -0.5 deg skew, faint noise, JPEG q55',
                                  ops=[{'op': 'paper', 'rgb': [242, 242, 240], 'texture': 2},
                                       {'op': 'rotate', 'deg': -0.5}, {'op': 'noise', 'sigma': 3}, {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=150, seed=13003, format='png',
                                    summary='thin light photocopy at 150 dpi: -2.2 deg skew, low threshold (105) '
                                            'with noise -> dotted/broken staff lines and thin stems, salt-and-pepper, '
                                            '1-bit PNG',
                                    ops=[PAPER_WHITE,
                                         {'op': 'rotate', 'deg': -2.2, 'expand': True},
                                         {'op': 'noise', 'saltpepper': 0.003},
                                         {'op': 'binarize', 'threshold': 105, 'noise': 18, 'pre_blur_px300': 0.6}]),
        }),
    # ------------------------------------------------------------------ 4
    dict(
        id='pitch-ledger-ottava', title='Heights and Depths (flute and tuba)', make=mk_ledger(),
        edge_cases=['extreme_ledger_lines_high', 'extreme_ledger_lines_low', 'ottava_8va', 'ottava_8vb',
                    'ottava_starting_mid_measure', 'ottava_spanning_line_break', 'same_display_position_after_ottava',
                    'passage_written_with_and_without_ottava', 'pencil_annotations', 'cropped_staff_ends',
                    'halftone_moire', 'high_dpi'],
        expected_notes=(
            'Two parts (Flute, Tuba), C major, 16 bars.  Pitches in the truth are SOUNDING pitches; 8va / 8vb '
            'brackets are <octave-shift> directions (type down = 8va, type up = 8vb, MusicXML convention).  '
            'Flute reaches D7 (6 ledger lines when written at pitch, bars 2, 7, 15); bars 5-6 and 7-8 are the '
            'same music with and without 8va; bar 9 starts 8va on beat 2; bar 10 has C7 under 8va then C6 loco '
            '(same staff position, different octave); bars 11-13 8va crosses the line break.  Tuba goes down to '
            'C1 (5 ledger lines below the bass staff, bars 7, 16); 8vb (bars 5-6, 9-10, 12-13, the last across a '
            'line break).  A correct conversion must output the sounding octave for every note under a bracket '
            'and must NOT apply a bracket to notes after it ends.  Pencil marks (circles, breath marks, words) in '
            'the scans are not part of the music.  The scans are cropped through the left/right ends of the '
            'staves (instrument names, brackets and the final barline ends are cut; no notes are cut).'),
        source='composed for this corpus', license=LIC,
        attribution=att('"Heights and Depths" - duet composed for the pitch challenge corpus (2026).'),
        layout_desc='StaffGroup of two single staves, 4 systems x 4 bars',
        damage={
            'scan.pdf': dict(dpi=400, seed=14001, jpeg=55,
                             summary='400 dpi RGB: pencil circles / breath marks / words, page cropped through the '
                                     'staff starts (0.6 mm into the staff) and staff ends (0.8 mm), 0.8 deg skew, JPEG q55',
                             ops=[{'op': 'paper', 'rgb': [245, 244, 240], 'texture': 3},
                                  {'op': 'pencil', 'circles': 6, 'breath_marks': 3, 'texts': ['slow', 'breathe'],
                                   'alpha': 0.7},
                                  {'op': 'crop', 'left_into_mm': 0.6, 'right_into_mm': 0.8},
                                  {'op': 'rotate', 'deg': 0.8},
                                  {'op': 'blur', 'radius_px300': 0.4}, {'op': 'noise', 'sigma': 3}]),
            'scan-mild.pdf': dict(dpi=400, seed=14002, jpeg=60,
                                  summary='400 dpi grey: slight crop of the system brackets, three pencil circles, '
                                          '0.3 deg skew, JPEG q60',
                                  ops=[PAPER_WHITE, {'op': 'pencil', 'circles': 3, 'alpha': 0.6},
                                       {'op': 'crop', 'left_into_mm': 0.2},
                                       {'op': 'rotate', 'deg': -0.3}, {'op': 'noise', 'sigma': 2}, {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=300, seed=14003, jpeg=25,
                                    summary='halftone-screened reproduction (110 lpi, 45 deg) rescanned -> moire, '
                                            'bluish recycled paper, deeper crop (1.2 mm into staff starts and ends), '
                                            '4 deg skew, JPEG q25',
                                    ops=[{'op': 'paper', 'rgb': [226, 231, 236], 'texture': 4, 'ink_rgb': [35, 38, 45]},
                                         {'op': 'crop', 'left_into_mm': 1.2, 'right_into_mm': 1.2},
                                         {'op': 'halftone', 'lpi': 110, 'angle': 45, 'oversample': 2},
                                         {'op': 'rotate', 'deg': 4.0, 'expand': True, 'fill': [236, 236, 236]},
                                         {'op': 'noise', 'sigma': 5}]),
        }),
    # ------------------------------------------------------------------ 5
    dict(
        id='pitch-satb-chromatic-closed', title='Abide with Me (SATB closed score, chromatic)', make=mk_abide(ABIDE_COURTESY),
        courtesy_report=ABIDE_COURTESY,
        edge_cases=['satb_closed_score', 'shared_staff_accidentals', 'accidental_carried_from_other_voice',
                    'chromatic_voice_leading', 'german_augmented_sixth', 'enharmonic_spelling_Cb_A_natural',
                    'secondary_dominants', 'courtesy_accidental_parenthesized', 'barline_cancels_accidental_no_courtesy',
                    'natural_in_flat_key', 'lyrics_two_verses', 'pickup_measure', 'page_rotated_180'],
        must_not_split=False, shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        expected_notes=(
            'Closed score: Soprano+Alto share the treble staff, Tenor+Bass the bass staff; a correct conversion '
            'outputs FOUR parts (Soprano, Alto, Tenor, Bass) with the two verses of lyrics on the Soprano.  Eb '
            'major, pickup + 12 bars, chromatic harmony: A natural (F7), Cb (Ab minor), E natural (C7), F# (D7), '
            'B natural (G7), Db (Eb7) and a German sixth (Cb-Eb-Gb-A) in bar 8.  Bar 2: the alto A4 natural on beat 2 '
            'also governs the soprano A4 on beat 4, which therefore has NO printed natural on the shared staff (the '
            'split Soprano part must still be A natural).  Bar 7: the alto F4 on beat 4 carries a natural on the '
            'shared staff only because the soprano sang F#4 on beat 3.  On a shared staff an accidental '
            'binds BOTH voices for the rest of the bar (LilyPond default, same octave only), so some notes of one '
            'voice carry no sign because the other voice already altered that pitch (listed in '
            'shared_staff_accidental_differences); the split parts must still get the altered pitch.  Some '
            'cancellations in the bar after an alteration are shown as parenthesised courtesy accidentals, others '
            'are left to the barline rule (courtesy_accidentals).'),
        truth_limitations=[
            'The truth encodes separate parts, so <accidental> elements are those a correct per-part transcription '
            'displays; on the engraved shared staves a few printed accidentals differ (see '
            'shared_staff_accidental_differences).  Pitches are identical either way.'],
        source='harmonisation composed for this corpus; text H. F. Lyte (1847)', license=LIC,
        attribution=att('"Abide with Me" - text by Henry Francis Lyte (1847), public domain.',
                        'Melody and chromatic SATB harmonisation composed for the pitch challenge corpus (2026), '
                        'voiced with the corpus voice-leading solver (harmonize2.py).'),
        layout_desc='closed score (ChoirStaff, 2 staves), 4 systems, 2 verses between the staves',
        damage={
            'scan.pdf': dict(dpi=300, seed=15001, jpeg=50,
                             summary='sheet fed upside down: page rotated 180 deg (+0.7 deg skew), grey, '
                                     'light gradient, noise, JPEG q50',
                             ops=[PAPER_WHITE, {'op': 'rotate', 'deg': 0.7},
                                  {'op': 'lighting', 'gradient': 0.1, 'angle': 90},
                                  {'op': 'rot90', 'k': 2}, {'op': 'noise', 'sigma': 4}, {'op': 'gray'}]),
            'scan-mild.pdf': dict(dpi=300, seed=15002, jpeg=60,
                                  summary='upright office scan, 0.8 deg skew, grey, JPEG q60',
                                  ops=[PAPER_WHITE, {'op': 'rotate', 'deg': 0.8}, {'op': 'noise', 'sigma': 2},
                                       {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=150, seed=15003, jpeg=15,
                                    summary='bound hymnal scanned upside down at 150 dpi: page curl + dark gutter '
                                            'shadow, rotated 180 deg, vignette, blur, noise, JPEG q15',
                                    ops=[PAPER_WHITE,
                                         {'op': 'curl', 'side': 'right', 'amp': 28, 'width': 0.3},
                                         {'op': 'gutter', 'side': 'right', 'width': 0.08, 'dark': 0.6},
                                         {'op': 'rot90', 'k': 2},
                                         {'op': 'lighting', 'vignette': 0.35},
                                         {'op': 'blur', 'radius_px300': 1.0}, {'op': 'noise', 'sigma': 6},
                                         {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 6
    dict(
        id='pitch-ttbb-enharmonic-keys', title='Now the Day Is Over (TTBB closed, enharmonic key change)',
        make=mk_dayover(DAY_COURTESY), courtesy_report=DAY_COURTESY,
        edge_cases=['ttbb_closed_score', 'treble_8vb_clef', 'key_6_flats', 'key_6_sharps',
                    'enharmonic_key_change_same_sounding_music', 'key_cancellation_12_glyphs', 'key_change_mid_system',
                    'double_flat_in_chord', 'double_sharp_in_chord', 'b_sharp', 'shared_staff_accidentals',
                    'lyrics', 'staple', 'punch_holes', 'book_page_curl'],
        must_not_split=False, shared_staves=[['Tenor I', 'Tenor II'], ['Baritone', 'Bass']],
        expected_notes=(
            'Closed male-voice score: Tenor I + Tenor II on a treble-8vb staff (sounding an octave below the '
            'written treble pitch), Baritone + Bass on a bass staff -> FOUR parts with lyrics on Tenor I.  Stanza 1 '
            '(bars 1-8) in Gb major (6 flats), stanza 2 (bars 9-16) in F# major (6 sharps) - the SAME sounding '
            'melody respelled; the change at bar 9 is mid-system and LilyPond prints 6 naturals + 6 sharps.  Coda '
            '(bars 17-20) in D major (4 cancelling naturals).  Chromatic chords give Ebb (Cb minor, bar 5), C '
            'natural (Ab7), B# (G#7), F## (D#7), D natural (B minor), E and D naturals (E7), Bb (G minor).  Every '
            'Tenor I/II pitch must be one octave below the written treble position (clef-octave-change -1).'),
        truth_limitations=[
            'Per-part <accidental> display (see shared_staff_accidental_differences for the few notes where the '
            'engraved shared staff prints differently).'],
        source='music composed for this corpus; text S. Baring-Gould (1865)', license=LIC,
        attribution=att('"Now the Day Is Over" - text by Sabine Baring-Gould (1865), public domain.',
                        'Melody and TTBB harmonisation composed for the pitch challenge corpus (2026), voiced with '
                        'the corpus voice-leading solver.'),
        layout_desc='closed TTBB score (treble_8 + bass), 4 systems x 5 bars',
        damage={
            'scan.pdf': dict(dpi=300, seed=16001, jpeg=55,
                             summary='photocopied page from a bound book: yellowed RGB paper, left page curl + gutter '
                                     'shadow, staple at top-left, three punch holes (scanner lid shows white), JPEG q55',
                             ops=[{'op': 'paper', 'rgb': [238, 228, 205], 'texture': 5, 'fibers': 2,
                                   'ink_rgb': [36, 32, 30]},
                                  {'op': 'staple', 'corner': 'tl', 'angle': -30, 'x_mm': 10, 'y_mm': 8},
                                  {'op': 'holes', 'n': 3, 'side': 'left', 'd_mm': 5.0, 'offset_mm': 5,
                                   'spacing_mm': 95, 'fill': [246, 246, 244]},
                                  {'op': 'curl', 'side': 'left', 'amp': 18, 'width': 0.28},
                                  {'op': 'gutter', 'side': 'left', 'width': 0.06, 'dark': 0.5},
                                  {'op': 'rotate', 'deg': -0.6},
                                  {'op': 'noise', 'sigma': 3, 'chroma': 1}]),
            'scan-mild.pdf': dict(dpi=300, seed=16002, jpeg=60,
                                  summary='light gutter shadow, ivory paper, 0.4 deg skew, JPEG q60',
                                  ops=[{'op': 'paper', 'rgb': [244, 238, 222], 'texture': 3},
                                       {'op': 'gutter', 'side': 'left', 'width': 0.05, 'dark': 0.4},
                                       {'op': 'rotate', 'deg': 0.4}, {'op': 'noise', 'sigma': 2}]),
            'scan-severe.pdf': dict(dpi=200, seed=16003, jpeg=20,
                                    summary='strong book curl with wavy warp and deep gutter, vertical camera shake '
                                            '(motion blur 5 px@300dpi), noise, JPEG q20 (RGB)',
                                    ops=[{'op': 'paper', 'rgb': [234, 222, 196], 'texture': 6},
                                         {'op': 'curl', 'side': 'left', 'amp': 40, 'width': 0.35, 'wave': 10},
                                         {'op': 'gutter', 'side': 'left', 'width': 0.1, 'dark': 0.7},
                                         {'op': 'blur', 'motion_px300': 5, 'angle': 80},
                                         {'op': 'noise', 'sigma': 7, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 7
    dict(
        id='pitch-enharmonic-song-2page', title='Lead, Kindly Light (soprano, 2 pages, enharmonic chromaticism)',
        make=mk_lead(),
        edge_cases=['chromatic_ascending_with_sharps_in_flat_key', 'chromatic_descending_naturals_in_sharp_key',
                    'enharmonic_spelling_Cb_Fb_Bbb_B#_E#_F##', 'key_change_at_page_turn', 'courtesy_key_at_page_end',
                    'tie_across_barline_with_accidental', 'melisma_with_accidentals', 'lyrics', 'multi_page',
                    'double_page_spread_2up', 'page_scale_mismatch', 'bleed_through'],
        expected_notes=(
            'One part (Soprano) with one lyric line, 39 bars on two pages.  Stanza 1 in Ab major, stanza 2 '
            '(bar 21, first bar of page 2) in E major: 4 cancelling naturals + 4 sharps, with the courtesy key '
            'signature at the end of page 1.  Spellings to preserve: C#5/D5 natural (bar 5), Cb5 (bar 8), Fb4 (bar '
            '9), D natural then Db (bar 11), Gb5 and E natural (bars 14-15), Bbb4 (bar 18); in E major B#4 (bar 23, '
            'sounds C5 but octave 4), E#5 and F##5 (bar 24, melisma into G#5), D/C naturals and A#4 (bars 26-28), '
            'B#4 tied over the barline into bar 31, G naturals (bars 33-34), D natural then D# (bar 37).  The '
            'scans show the two pages side by side (2-up) or as separate pages at slightly different scales; the '
            'conversion must treat them as one continuous part.'),
        source='music composed for this corpus; text J. H. Newman (1833)', license=LIC,
        attribution=att('"Lead, Kindly Light" ("The Pillar of the Cloud") - text by John Henry Newman (1833), '
                        'public domain.', 'Melody composed for the pitch challenge corpus (2026).'),
        layout_desc='single staff + lyrics, 2 pages (page break before bar 21), 10 systems',
        damage={
            'scan.pdf': dict(dpi=200, seed=17001, jpeg=50,
                             summary='open booklet scanned as one 2-up spread: ivory paper, bleed-through from the '
                                     'facing page, page 2 printed 3.5% smaller, inner-edge curl + gutter shadow, '
                                     '0.9 deg skew, JPEG q50 (RGB)',
                             ops=[{'op': 'paper', 'rgb': [240, 232, 214], 'texture': 5, 'bleed': 0.14,
                                   'bleed_from': 'next', 'ink_rgb': [34, 30, 28]},
                                  {'op': 'scale', 'factor': 0.965, 'pages': [1], 'fill': [240, 232, 214]},
                                  {'op': 'spread2up', 'curl_amp': 30, 'gutter_dark': 0.55, 'gutter_width': 0.07,
                                   'bg': [45, 40, 38], 'offset_mm': 3},
                                  {'op': 'rotate', 'deg': 0.9, 'fill': [45, 40, 38]},
                                  {'op': 'lighting', 'gradient': 0.12, 'angle': 0},
                                  {'op': 'noise', 'sigma': 3, 'chroma': 1}]),
            'scan-mild.pdf': dict(dpi=250, seed=17002, jpeg=60,
                                  summary='two separate grey pages, page 2 scanned at 98.5% scale, different skews '
                                          '(+0.7 / -1.2 deg), JPEG q60',
                                  ops=[PAPER_WHITE, {'op': 'scale', 'factor': 0.985, 'pages': [1]},
                                       {'op': 'rotate', 'deg': [0.7, -1.2]}, {'op': 'noise', 'sigma': 2},
                                       {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=110, seed=17003, jpeg=25,
                                    summary='phone photo of the open booklet at 110 dpi: 2-up spread with strong inner '
                                            'curl, page 2 at 103.5% scale, foxing, heavy bleed-through, perspective, '
                                            'vignette, blur, noise, JPEG q25 (RGB)',
                                    ops=[{'op': 'paper', 'rgb': [232, 220, 196], 'texture': 7, 'bleed': 0.2,
                                          'bleed_from': 'next'},
                                         {'op': 'foxing', 'n': 80, 'strength': 0.4},
                                         {'op': 'scale', 'factor': 1.035, 'pages': [1], 'fill': [232, 220, 196]},
                                         {'op': 'spread2up', 'curl_amp': 45, 'gutter_dark': 0.7, 'gutter_width': 0.09,
                                          'bg': [50, 46, 44]},
                                         {'op': 'phone', 'margin': 0.04, 'bg': [50, 46, 44], 'jitter': 0.04},
                                         {'op': 'lighting', 'vignette': 0.35},
                                         {'op': 'blur', 'radius_px300': 1.2},
                                         {'op': 'noise', 'sigma': 6, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 8
    dict(
        id='pitch-satb-ledger-extremes', title='All Things Bright and Beautiful (SATB closed, extreme ranges)',
        make=mk_bright(),
        edge_cases=['satb_closed_score', 'ledger_lines_between_staves', 'soprano_to_D6', 'bass_to_A1',
                    'tenor_to_A4_in_bass_clef', 'alto_to_A3_below_treble', 'ledger_lines_near_lyrics',
                    'lyrics_two_verses', 'pencil_reminder_accidentals', 'coffee_stain', 'high_dpi_600', 'low_dpi_100'],
        must_not_split=False, shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        expected_notes=(
            'Closed score -> FOUR parts (Soprano, Alto, Tenor, Bass), D major 3/4, 12 bars, two verses under the '
            'Soprano.  Extreme ledger-line notes: Soprano D6 and C#6 (bar 8), A5/B5 often; Alto A3 (2 ledger lines '
            'below the treble staff, bar 1); Tenor up to A4 (above 3 ledger lines over the bass staff, bars 7 and '
            '10); Bass down to A1 (3 ledger lines below the bass staff, bars 3, 5, 11) and B1 (bars 2, 7).  The '
            'alto/tenor ledger lines intrude into the lyric band between the staves.  Pencil sharps/flats drawn '
            'next to some notes in the scans only REMIND of the existing key-signature/accidental pitch (they agree '
            'with the truth); pencil circles, breath marks and words are not music.'),
        source='music composed for this corpus; text C. F. Alexander (1848)', license=LIC,
        attribution=att('"All Things Bright and Beautiful" - text by Cecil Frances Alexander (1848), public domain.',
                        'Descant-style SATB setting composed for the pitch challenge corpus (2026).'),
        layout_desc='closed score (ChoirStaff, 2 staves), 2 systems x 6 bars, 2 verses between the staves',
        damage={
            'scan.pdf': dict(dpi=600, seed=18001, jpeg=60,
                             summary='600 dpi RGB scan of a rehearsal copy: pencil circles, reminder sharps, breath '
                                     'marks and words, coffee ring at top right, 0.4 deg skew, JPEG q60',
                             ops=[{'op': 'paper', 'rgb': [246, 246, 243], 'texture': 2},
                                  {'op': 'pencil', 'circles': 6, 'reminders': 4, 'breath_marks': 3,
                                   'texts': ['breathe!', 'tenors sing out'], 'alpha': 0.75},
                                  {'op': 'stain', 'cx': 0.82, 'cy': 0.12, 'r': 0.09, 'strength': 0.4},
                                  {'op': 'rotate', 'deg': 0.4},
                                  {'op': 'noise', 'sigma': 2}]),
            'scan-mild.pdf': dict(dpi=400, seed=18002, jpeg=60,
                                  summary='400 dpi grey, three pencil circles, -0.3 deg skew, JPEG q60',
                                  ops=[PAPER_WHITE, {'op': 'pencil', 'circles': 3, 'alpha': 0.6},
                                       {'op': 'rotate', 'deg': -0.3}, {'op': 'noise', 'sigma': 2}, {'op': 'gray'}]),
            'scan-severe.pdf': dict(dpi=100, seed=18003, jpeg=15,
                                    summary='100 dpi grey, 6 deg skew, focus blur, heavy noise, JPEG q15',
                                    ops=[PAPER_WHITE, {'op': 'rotate', 'deg': 6.0, 'expand': True},
                                         {'op': 'blur', 'radius_px300': 0.9}, {'op': 'noise', 'sigma': 8},
                                         {'op': 'gray'}]),
        }),
]
