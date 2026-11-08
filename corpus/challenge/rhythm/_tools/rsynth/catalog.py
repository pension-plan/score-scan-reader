"""Rhythm challenge catalog: items, expected conversion results, edge-case tags and
scan-damage variants (params + seed recorded verbatim in meta.json)."""
from . import items as I

CC0_ATT = I.CC0
LIC = 'CC0-1.0 (music composed for this corpus; engraving, truth and scans CC0)'

GRACE_TRUTH = ('Grace notes are <grace/> notes without <duration> (slash="yes" for acciaccaturas); the slur that '
               'LilyPond engraves for \\acciaccatura / \\appoggiatura is encoded as slur number 2.')
BEAM_TRUTH = ('<beam> elements reproduce the engraved beam groups exactly (manual beaming); notes only - a rest '
              'inside a beam carries no <beam> element.')
TUPLET_TRUTH = ('<tuplet bracket=...> follows LilyPond\'s default: bracket omitted only when one beam covers exactly '
                'the tuplet; implied tuplets have bracket="no" show-number="none".')
PENCIL = ('Pencil marks in the damaged scans (circles, fingering digits, a fake "3" above notes, ticks, words) are '
          'not part of the music and are absent from the truth.')


def V(seed, dpi, ops, color='gray', fmt='jpeg', jpeg=None, passes=1):
    v = {'seed': seed, 'dpi': dpi, 'color': color, 'ops': ops, 'format': fmt}
    if fmt == 'jpeg':
        v['jpeg'] = jpeg
        v['jpeg_passes'] = passes
    return v


ITEMS = [
    dict(
        id='rh01-tuplet-etude', title='Tuplet Etude (flute)', make=I.mk_rh01, pages=2,
        source='Composed for this corpus (CC0).', license=LIC,
        attribution='Tuplet Etude for flute - composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['eighth_triplets', 'quarter_triplets', 'half_note_triplets_cut_time', 'tuplet_with_rests',
                    'tuplet_mixed_values', 'quintuplet_16ths', 'quintuplet_8ths', 'sextuplet', 'septuplet',
                    'implied_triplets_no_number', 'duplets_6_8', 'duplets_12_8', 'quadruplets_6_8_12_8',
                    'sixteenth_triplets', 'thirtysecond_triplets', 'beam_across_two_tuplets',
                    'tuplet_inside_longer_beam', 'tie_into_tuplet', 'beam_across_rest_in_tuplet',
                    'beam_across_rest_6_8', 'time_signature_changes', 'common_time_symbol', 'cut_time_symbol',
                    'numeric_4_4_after_C', 'compound_6_8', 'compound_12_8', 'courtesy_time_signature_at_system_end',
                    'fermata_on_rest', 'multi_page', 'pencil_fake_tuplet_numbers'],
        expected=dict(parts=['Flute'], must_not_split=False, shared_staves=[],
                      notes='Single-staff flute part, 2 pages, 23 bars. A correct conversion must read every tuplet '
                            'with its ratio: 3:2 on eighths, quarters (bars 2, 7, 21) and halves (bars 9, 11; cut '
                            'time), 5:4 on 16ths (bar 4) and on eighths (bar 21, half-bar quintuplet), 6:4 and 7:4 '
                            '(bars 4, 22), 2:3 duplets and 4:3 quadruplets in 6/8 and 12/8 (bars 14-16, 18), 3:2 '
                            'sixteenth and 32nd triplets (bars 19-20); tuplets containing rests (bars 3, 12) and '
                            'mixed values (quarter+eighth, bars 3, 11, 22); the four triplets of bar 6 print no '
                            '"3" and no bracket (implied) and must still be 3:2. Time signatures take effect at bars '
                            '1 (C), 9 (2/2 cut symbol), 14 (6/8), 18 (12/8), 20 (4/4 numeric) - the courtesy '
                            'signatures at the end of the preceding systems are not changes. Tie g\'\'2 -> first '
                            'note of a quarter-note triplet (bar 7); fermata on the quarter rest of bar 8 and on '
                            'the final c\'\'\'. Pencil "3"s/fingerings in scan.pdf and scan-severe.pdf are not music.'),
        truth_limitations=[TUPLET_TRUTH, BEAM_TRUTH, PENCIL],
        variants={
            'scan.pdf': V(710101, 300, [
                {'op': 'paper', 'rgb': [238, 228, 198], 'texture': 6},
                {'op': 'pencil', 'circles': 4, 'fake_triplets': 2, 'fingerings': 3, 'ticks': 2, 'words': ['rit.']},
                {'op': 'rotate', 'deg': 1.8, 'bg': [215, 215, 215]},
                {'op': 'gradient', 'strength': 0.12},
                {'op': 'blur', 'sigma': 0.6},
                {'op': 'noise', 'sigma': 4, 'chroma': 1.5}], color='rgb', jpeg=45),
            'scan-mild.pdf': V(710102, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': -0.5, 'bg': 240},
                {'op': 'blur', 'sigma': 0.4},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710103, 150, [
                {'op': 'paper', 'rgb': [240, 236, 226], 'texture': 4},
                {'op': 'curl', 'side': 'gutter', 'amp': 35, 'width': 0.3},
                {'op': 'gutter', 'side': 'gutter', 'width': 0.08, 'dark': 0.6},
                {'op': 'two_up', 'seam_px': 6, 'seam': 40},
                {'op': 'perspective', 'margin': 0.04, 'jitter': 0.02, 'keystone': 0.03, 'bg': [60, 55, 50]},
                {'op': 'vignette', 'strength': 0.3},
                {'op': 'motion_blur', 'length': 5, 'angle': 10},
                {'op': 'noise', 'sigma': 6, 'chroma': 2}], color='rgb', jpeg=20),
        }),
    dict(
        id='rh02-ties-dots-song', title='Who Has Seen the Wind? (voice, ties and dots)', make=I.mk_rh02, pages=2,
        source='Text: Christina Rossetti, "Who has seen the wind?", Sing-Song (1872), public domain. Melody composed '
               'for this corpus (CC0).',
        license='Text public domain (Rossetti 1872); music, engraving, truth and scans CC0-1.0',
        attribution='Text: Christina Rossetti, "Who has seen the wind?" from Sing-Song (1872) - public domain.\n'
                    'Melody: composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['pickup_anacrusis', 'incomplete_final_bar', 'ties_across_barlines', 'tie_across_system_break',
                    'tie_across_page_break', 'tie_across_time_signature_change', 'double_dotted_quarter',
                    'double_dotted_half', 'double_dotted_eighth_plus_32nd', 'dotted_rhythms', 'syncopation',
                    'slur_on_repeated_pitch_not_tie', 'lyrics', 'lyric_melisma_extender', 'lyrics_with_ties',
                    'vocal_flags_unbeamed', 'time_signature_changes', 'compound_6_8', 'compound_9_8',
                    'multi_page', 'binarized_photocopy', 'page_rotated_180', 'page_scale_mismatch'],
        expected=dict(parts=['Voice'], must_not_split=False, shared_staves=[],
                      notes='21 bars on 2 pages: pickup bar of one eighth (measure 0, implicit) and an incomplete '
                            'final bar of 5 eighths (2.5 quarters) - neither may be padded. Ties: c\'\' 2->3, f\' '
                            '4->5 (across the system break AND the 3/4->4/4 change), g\' 9->10->11 (across the page '
                            'break), c\'\' 12->13, f\' 14->15, d\'\' inside 17, f\' 19->20. Slurs on repeated pitches '
                            'are NOT ties: bar 4 f\'16-(f\'4 (two attacks), bar 7 c\'\'16-(c\'\'8 (two attacks). '
                            'Double-dotted values: g\'4.. + f\'16, d\'\'4.. + c\'\'16, f\'2.. + r8, bes\'8.. + a\'32. '
                            'Time signatures 3/4, 4/4 (bar 5), 3/4 (8), 6/8 (12), 9/8 (18), 3/4 (19). One lyric '
                            'line (stanzas 1 and 2 through-composed): one syllable per attack, none on tie '
                            'continuations, melismas with extenders ("you", "bling", "-ing", "heads").'),
        truth_limitations=[BEAM_TRUTH,
                           'Lyric hyphens may not be printed where syllables are close ("Neither"); truth keeps '
                           'syllabic begin/end as entered.'],
        variants={
            'scan.pdf': V(710201, 200, [
                {'op': 'paper', 'rgb': [250, 250, 250]},
                {'op': 'punch_holes', 'n': 2, 'side': 'left', 'bg': 20},
                {'op': 'crop', 'side': 'right', 'into_staff': 0.5, 'bg': 255},
                {'op': 'rotate', 'deg': 0.8, 'bg': 255},
                {'op': 'speckle', 'per_mpx': 60},
                {'op': 'binarize', 'threshold': 80, 'pre_blur': 0.7, 'noise': 16}], fmt='png1'),
            'scan-mild.pdf': V(710202, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 3},
                {'op': 'rotate', 'deg': 0.6, 'bg': 235},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710203, 200, [
                {'op': 'ink_weight', 'px': 1},
                {'op': 'paper', 'rgb': [248, 248, 248]},
                {'op': 'rotate', 'deg': -1.2, 'bg': 255, 'pages': [0]},
                {'op': 'rotate', 'deg': 2.0, 'bg': 255, 'pages': [1]},
                {'op': 'scale', 'factor': 0.94, 'dx': 0.01, 'dy': -0.015, 'pages': [1]},
                {'op': 'rot90', 'k': 2, 'pages': [1]},
                {'op': 'binarize', 'threshold': 185, 'pre_blur': 1.0, 'noise': 25},
                {'op': 'saltpepper', 'amount': 0.002}], fmt='png1'),
        }),
    dict(
        id='rh03-meter-changes-piano', title='Changing Meters (piano)', make=I.mk_rh03, pages=1,
        source='Composed for this corpus (CC0).', license=LIC,
        attribution='Changing Meters for piano - composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['piano_grand_staff_must_not_split', 'two_voices_in_right_hand', 'time_signature_changes',
                    'irregular_meter_5_8', 'irregular_meter_7_8', 'beaming_3_2_and_2_2_3', 'half_note_beat_3_2',
                    'compound_9_8', 'meter_2_4', 'cut_time_symbol', 'common_time_symbol', 'numeric_4_4',
                    'courtesy_time_signature_at_system_end', 'whole_bar_rest_one_staff_only', 'pickup_anacrusis',
                    'incomplete_final_bar', 'tie_across_system_break', 'tie_across_time_signature_change',
                    'chord_tie_across_barline', 'double_dotted_chord', 'tie_quarter_to_16th',
                    'beam_across_rest', 'fermata_all_staves', 'phone_capture'],
        expected=dict(parts=['Piano'], must_not_split=True, shared_staves=[],
                      notes='ONE part with 2 staves (grand staff); the right hand\'s two voices (bars 1-2, 9, 13-15) '
                            'belong to that part and must not become separate parts. 16 bars: quarter pickup in 4/4 '
                            '(numeric) and incomplete 3-beat final bar; meters 3/4 (bar 3), 5/8 beamed 3+2 (4-5), '
                            '7/8 beamed 2+2+3 (6-7), 2/4 (8), 3/2 (9), 9/8 (10-11), 2/2 with cut symbol (12-13), '
                            '4/4 with C symbol (14-15); bars 3, 6, 9 and 12 start systems with a new meter, so '
                            'courtesy signatures end the previous systems. Whole-bar rests in one staff only: LH bar 3 (3/4), RH bar 12 '
                            '(2/2). Ties: RH a\'\'2~a\'\'8 over the system break and the 4/4->3/4 change (2->3), '
                            'c\'\'\'4~c\'\'\'16 (bar 2), e\'\'4.~e\'\'8 (5), f\'\'2~f\'\'8 (13), LH chord <c e>4.~ '
                            'over the barline 10->11. LH <e, b,>2.. fills a 7/8 bar. Fermatas on the final chords of '
                            'both staves.'),
        truth_limitations=[BEAM_TRUTH, TUPLET_TRUTH],
        variants={
            'scan.pdf': V(710301, 200, [
                {'op': 'paper', 'rgb': [245, 243, 238], 'texture': 3},
                {'op': 'perspective', 'margin': 0.06, 'jitter': 0.02, 'keystone': 0.04, 'bg': [80, 70, 60]},
                {'op': 'blotch', 'strength': 0.15},
                {'op': 'vignette', 'strength': 0.25},
                {'op': 'shadow', 'strength': 0.25, 'pos': 0.25, 'soft': 0.06},
                {'op': 'blur', 'sigma': 1.0},
                {'op': 'noise', 'sigma': 4, 'chroma': 2}], color='rgb', jpeg=40),
            'scan-mild.pdf': V(710302, 300, [
                {'op': 'paper', 'rgb': [247, 246, 242], 'texture': 2},
                {'op': 'perspective', 'margin': 0.05, 'jitter': 0.008, 'keystone': 0.015, 'bg': [90, 85, 80]},
                {'op': 'vignette', 'strength': 0.1},
                {'op': 'blur', 'sigma': 0.5},
                {'op': 'noise', 'sigma': 2}], color='rgb', jpeg=60),
            'scan-severe.pdf': V(710303, 200, [
                {'op': 'paper', 'rgb': [238, 235, 228], 'texture': 4},
                {'op': 'perspective', 'margin': 0.05, 'jitter': 0.035, 'keystone': 0.07, 'bg': [50, 45, 40]},
                {'op': 'shadow', 'strength': 0.45, 'pos': 0.15, 'soft': 0.08},
                {'op': 'gradient', 'strength': 0.2},
                {'op': 'motion_blur', 'length': 6, 'angle': 20},
                {'op': 'noise', 'sigma': 8, 'chroma': 3},
                {'op': 'downsample', 'dpi': 100}], color='rgb', jpeg=15),
        }),
    dict(
        id='rh04-rest-zoo-part', title='Interlude - oboe part (every rest type, multi-bar rests)', make=I.mk_rh04,
        pages=1, source='Composed for this corpus (CC0).', license=LIC,
        attribution='Interlude (oboe part) - composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['multi_measure_rest_hbar', 'multi_measure_rest_church_symbols', 'rehearsal_marks',
                    'general_pause_fermata_on_whole_bar_rest', 'whole_bar_rest_3_4', 'whole_bar_rest_6_8',
                    'whole_bar_rest_4_2_breve', 'plain_whole_rest_not_measure_rest', 'breve_rest', 'whole_rest',
                    'half_rest', 'quarter_rest', 'eighth_rest', '16th_rest', '32nd_rest', '64th_rest',
                    'dotted_quarter_rest', 'dotted_eighth_rest', 'double_dotted_eighth_rest',
                    'double_dotted_half_rest', 'rest_in_triplet', 'rest_in_duplet', 'beam_across_rest_6_8',
                    'beam_across_rest_in_triplet', '64th_notes', 'fermata_on_rest', 'time_signature_changes',
                    'meter_4_2', 'cut_time_symbol', 'page_rotated_90', 'high_dpi_400', 'halftone_moire',
                    'skew_10_degrees'],
        expected=dict(parts=['Oboe'], must_not_split=False, shared_staves=[],
                      notes='40 measures although only 22 bars are drawn: the multi-bar rests must expand to 12 '
                            '(bars 1-12, H-bar with "12"), 3 (bars 18-20, 3/4, church-rest symbols), 5 (bars 27-31, '
                            '2/2, church-rest symbols) and 2 (bars 36-37, 4/4) measures of rest; rehearsal marks A '
                            '(13), B (21), C (27), D (36). Bar 21 is a G.P.: whole-bar rest in 3/4 with fermata. '
                            'Rest values: 64th, 32nd, 16th, 8th, quarter (bar 13), half (39), dotted quarter (14, 23), dotted '
                            'eighth and double-dotted eighth (15), double-dotted half (16), whole-bar rest in 6/8 '
                            '(25), duplet containing a rest (26), triplet starting with a rest (32), plain whole rest '
                            'r1 in 2/2 (33, NOT a measure rest) and in 4/2 (34), whole-bar rest in 4/2 drawn as a '
                            'breve rest (35), double-dotted eighth rest (38), triplet with a rest under a beam (39), '
                            'fermatas on the final dotted half note and quarter rest. Beams span eighth rests in '
                            '6/8 (bar 22).'),
        truth_limitations=['Whole-bar rests are <rest measure="yes"/> with the bar duration and no <type>; each bar of '
                           'a multi-bar rest has its own measure rest and the first bar carries <measure-style>'
                           '<multiple-rest> (use-symbols="yes" where LilyPond draws church-rest symbols).',
                           BEAM_TRUTH],
        variants={
            'scan.pdf': V(710401, 400, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 2.5, 'bg': 30},
                {'op': 'rot90', 'k': 1},
                {'op': 'noise', 'sigma': 5},
                {'op': 'saltpepper', 'amount': 0.0005}], jpeg=50),
            'scan-mild.pdf': V(710402, 400, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 0.5, 'bg': 240},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710403, 300, [
                {'op': 'paper', 'rgb': [240, 238, 232], 'texture': 3},
                {'op': 'halftone', 'lpi': 85, 'angle': 45, 'supersample': 2},
                {'op': 'rotate', 'deg': 10, 'bg': 40},
                {'op': 'blur', 'sigma': 0.8},
                {'op': 'noise', 'sigma': 6}], jpeg=35),
        }),
    dict(
        id='rh05-graces-fermatas', title='Air with Graces (violin and piano)', make=I.mk_rh05, pages=1,
        source='Composed for this corpus (CC0).', license=LIC,
        attribution='Air with Graces for violin and piano - composed for the OMR rhythm challenge corpus.\n\n'
                    + CC0_ATT + '\n\nRevision 2026-11-08: regenerated (same seeds) after a generator fix. The violin\'s grace '
                    'note before the very first note had no matching grace time in the piano staves, so LilyPond '
                    'printed each piano staff\'s clef a second time with the key signature over the time digits '
                    '(an engraving defect, not an edge case). lily.py now adds a grace skip there; truth.musicxml is '
                    'unchanged. Checked by eye on the regenerated clean.pdf / scan.pdf: one clef, key and time per staff.',
        edge_cases=['acciaccatura', 'appoggiatura', 'grace_group_16ths', 'grace_group_32nds', 'grace_at_bar_start',
                    'grace_before_first_note', 'unslashed_single_grace', 'fermata_on_note', 'fermata_on_rest',
                    'fermata_on_chord', 'simultaneous_fermatas_all_staves', 'sixteenth_beamed_groups',
                    '32nd_beamed_groups', 'dotted_16th_32nd', 'dotted_eighth_32nd_32nd', 'beam_across_16th_rest',
                    'beamlet_hook', 'tie_quarter_to_16th', 'piano_grand_staff_must_not_split', 'instrument_plus_piano',
                    'coffee_stain', 'foxing', 'bleed_through', 'yellowed_paper_rgb'],
        expected=dict(parts=['Violin', 'Piano'], must_not_split=True, shared_staves=[],
                      notes='Two parts: Violin (1 staff) and Piano (ONE part, 2 staves). 8 bars of 4/4 in D major. '
                            'Grace notes take no time: slashed acciaccaturas (bar 1 beat 1 = before the very first '
                            'note, bar 4 beat 1, bar 6 last eighth), unslashed appoggiatura (bar 1), unslashed grace '
                            'groups of 2 x 16th (bar 1), 3 x 32nd (bar 2), 4 x 16th (bar 5) and a single unslashed '
                            'grace (bar 7). Fermatas sound together in all three staves: bar 2 beat 1 (violin note, '
                            'piano chords), bar 4 beat 1, bar 8 (final chord AND final quarter rest in every staff). '
                            'Beamed 16th/32nd groups including 8.+32+32, 8+r16+16 (beam over a 16th rest, backward '
                            'beamlet) and an 8-note 32nd run; tie b\'4~b\'16 (bar 7).'),
        truth_limitations=[GRACE_TRUTH, BEAM_TRUTH],
        variants={
            'scan.pdf': V(710501, 300, [
                {'op': 'paper', 'rgb': [236, 224, 190], 'texture': 7, 'bleed': {'strength': 0.12}},
                {'op': 'foxing', 'n': 80, 'strength': 0.5},
                {'op': 'coffee', 'n': 1, 'radius_mm': 35, 'strength': 0.4, 'partial': True},
                {'op': 'rotate', 'deg': -0.7, 'bg': [200, 200, 200]},
                {'op': 'gradient', 'strength': 0.1},
                {'op': 'blur', 'sigma': 0.5},
                {'op': 'noise', 'sigma': 3, 'chroma': 1.5}], color='rgb', jpeg=55),
            'scan-mild.pdf': V(710502, 300, [
                {'op': 'paper', 'rgb': [242, 236, 215], 'texture': 4, 'bleed': {'strength': 0.05}},
                {'op': 'foxing', 'n': 25, 'strength': 0.3},
                {'op': 'blur', 'sigma': 0.4},
                {'op': 'noise', 'sigma': 2}], color='rgb', jpeg=60),
            'scan-severe.pdf': V(710503, 300, [
                {'op': 'ink_dropout', 'amount': 0.2},
                {'op': 'paper', 'rgb': [228, 212, 170], 'texture': 9, 'bleed': {'strength': 0.25}, 'ink_var': 30},
                {'op': 'foxing', 'n': 200, 'strength': 0.7},
                {'op': 'coffee', 'n': 3, 'radius_mm': 45, 'strength': 0.6},
                {'op': 'rotate', 'deg': 1.4, 'bg': [190, 190, 190]},
                {'op': 'blur', 'sigma': 0.9},
                {'op': 'noise', 'sigma': 4, 'chroma': 2}], color='rgb', jpeg=20),
        }),
    dict(
        id='rh06-closed-satb-crossrhythm', title='O God, Our Help in Ages Past (closed SATB, cross-voice rhythms)',
        make=I.mk_rh06, pages=1,
        source='Text: Isaac Watts, "O God, our help in ages past" (1719), public domain. Music composed for this '
               'corpus (CC0) - not the traditional tune St Anne.',
        license='Text public domain (Watts 1719); music, engraving, truth and scans CC0-1.0',
        attribution='Text: Isaac Watts, "Our God, our help in ages past" (The Psalms of David Imitated, 1719), '
                    'verses 1 and 2 as printed in later hymnals ("O God...") - public domain.\n'
                    'Music (SATB setting): composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['satb_closed_score', 'two_voices_per_staff_split', 'cross_voice_rhythm_differences',
                    'triplets_against_duplets', 'tuplet_in_one_voice_only', 'tie_in_one_voice_only',
                    'rest_in_one_voice_only', 'whole_bar_rest_lower_voice', 'unison_shared_notehead',
                    'dotted_vs_straight_between_voices', 'fermatas_at_different_onsets', 'pickup_anacrusis',
                    'incomplete_final_bar', 'lyrics', 'two_verses', 'lyrics_on_lower_staff_with_own_rhythm',
                    'lyric_melisma', 'high_dpi_600', 'halftone_moire', 'low_dpi'],
        expected=dict(parts=['Soprano', 'Alto', 'Tenor', 'Bass'], must_not_split=False,
                      shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
                      notes='Closed score: split into 4 parts. Upper staff S (stems up) / A (stems down), lower staff '
                            'T (up) / B (down), with independent rhythms: A quarter-note triplets against S quarters '
                            '(bars 1, 3), A four eighths against S dotted quarter + eighth (bar 2), A ties against '
                            'S dotted notes (bars 4, 7), A rests while S sings (bar 3 beat 1; bar 5 A half rest vs S '
                            'quarter rest); T eighth-note triplets (bars 1, 3) and dotted rhythms against B; B '
                            'whole-bar rest in bar 5 while T sings; T and B in unison on d at bar 8 beat 4 (one '
                            'shared notehead, two notes). Quarter pickup, incomplete final bar of 3 beats; fermatas '
                            'per voice at different onsets. Lyrics: Soprano verses 1 and 2 (between the staves, '
                            'aligned to the soprano rhythm, melisma on "hope"/"saints"); Bass verse 1 (below the '
                            'bass staff, aligned to the bass rhythm). Alto and Tenor have no lyrics in the score '
                            'and in the truth.'),
        truth_limitations=[BEAM_TRUTH, TUPLET_TRUTH,
                           'Lyrics are attached only to the voices they are engraved under (S verses 1-2, B verse 1).'],
        variants={
            'scan.pdf': V(710601, 600, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'halftone', 'lpi': 110, 'angle': 30, 'supersample': 1},
                {'op': 'rotate', 'deg': -1.2, 'bg': 230},
                {'op': 'noise', 'sigma': 4}], jpeg=60),
            'scan-mild.pdf': V(710602, 600, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 0.3, 'bg': 240},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710603, 120, [
                {'op': 'paper', 'rgb': [244, 243, 240], 'texture': 3},
                {'op': 'rotate', 'deg': 1.5, 'bg': 220},
                {'op': 'blur', 'sigma': 0.9},
                {'op': 'noise', 'sigma': 6}], jpeg=15),
        }),
    dict(
        id='rh07-compound-meter-fiddle', title='The Crooked Road (fiddle: jig, slip jig, slide)', make=I.mk_rh07,
        pages=1, source='Composed for this corpus (CC0).', license=LIC,
        attribution='The Crooked Road (fiddle tune) - composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['compound_6_8', 'compound_9_8', 'compound_12_8', 'hemiola_bar_in_3_4', 'pickup_eighth',
                    'incomplete_final_bar', 'beam_across_rest_6_8', 'siciliano_dotted_figures', 'dotted_rests',
                    'duplet_12_8', 'grace_cuts_acciaccatura', 'plain_grace', 'double_stop_chord', 'chord_tie',
                    'tie_across_barline_and_time_change', 'fermata_mid_piece', 'rehearsal_marks',
                    'low_dpi_150', 'staple', 'punch_holes', 'pencil_annotations', 'cropped_edges',
                    'skew_4_and_7_degrees', 'gutter_shadow'],
        expected=dict(parts=['Fiddle'], must_not_split=False, shared_staves=[],
                      notes='19 bars: eighth pickup (measure 0) and incomplete final bar of 5 eighths. 6/8 (bars '
                            '1-6, 8, 15-18), one hemiola bar in 3/4 (7) entered by a tie a\'8~a\'4 across the '
                            'barline and the time change, 9/8 slip jig (9-12, mark B) with beam over a rest, '
                            'dotted quarter rests (12), 12/8 slide (13-14, mark C) with a 2:3 duplet and a tied '
                            'double stop <d\' b\'>4.~<d\' b\'>4. Grace cuts: slashed acciaccaturas (bars 1, 15) and '
                            'one plain grace (bar 11). Fermata mid-piece (bar 16). In scan-severe.pdf the left crop '
                            'removes most of the instrument name and the right crop cuts the staff ends / final '
                            'barlines; the part is still "Fiddle".'),
        truth_limitations=[GRACE_TRUTH, BEAM_TRUTH, PENCIL],
        variants={
            'scan.pdf': V(710701, 150, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 3},
                {'op': 'staple', 'corner': 'tl'},
                {'op': 'punch_holes', 'n': 2, 'side': 'left', 'bg': 30},
                {'op': 'rotate', 'deg': 4.0, 'bg': 200},
                {'op': 'gutter', 'side': 'left', 'width': 0.06, 'dark': 0.5},
                {'op': 'saltpepper', 'amount': 0.001},
                {'op': 'noise', 'sigma': 4}], jpeg=50),
            'scan-mild.pdf': V(710702, 150, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 0.7, 'bg': 230},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710703, 200, [
                {'op': 'paper', 'rgb': [244, 243, 238], 'texture': 3},
                {'op': 'pencil', 'circles': 5, 'fake_triplets': 2, 'fingerings': 5, 'ticks': 2,
                 'words': ['rit.', 'slow!']},
                {'op': 'crop', 'side': 'left', 'into_staff': -0.3, 'bg': 255},
                {'op': 'crop', 'side': 'right', 'into_staff': 0.5, 'bg': 255},
                {'op': 'rotate', 'deg': 7.0, 'bg': 60},
                {'op': 'perspective', 'margin': 0.03, 'jitter': 0.02, 'keystone': 0.03, 'bg': [60, 60, 60]},
                {'op': 'blur', 'sigma': 0.8}], jpeg=20),
        }),
    dict(
        id='rh08-dense-runs-piano', title='Toccatina (piano: 16th/32nd/64th runs)', make=I.mk_rh08, pages=1,
        source='Composed for this corpus (CC0).', license=LIC,
        attribution='Toccatina for piano - composed for the OMR rhythm challenge corpus.\n\n' + CC0_ATT,
        edge_cases=['piano_grand_staff_must_not_split', 'two_voices_in_right_hand', 'sixteenth_beamed_groups',
                    '32nd_run', '64th_run', 'sextuplets', 'sixteenth_triplets', 'dotted_16th_32nd',
                    'double_dotted_eighth_32nd', 'dotted_eighth_32nd_32nd', 'beam_across_rest',
                    'beam_starting_after_rest', 'beamlet_hooks', 'tie_quarter_to_16th', 'fermata_all_staves',
                    'motion_blur', 'pencil_fingerings', 'binarized_thick_low_dpi_100'],
        expected=dict(parts=['Piano'], must_not_split=True, shared_staves=[],
                      notes='ONE part with 2 staves; right-hand voice 2 (16th accompaniment, bars 1-2; c\'4 r4 in '
                            'bar 11) stays inside the piano part. 12 bars of 2/4: 32nd run of 8 (bar 3), 64th run of '
                            '8 (bar 7), sextuplet 16ths (bar 5), 16th triplets (bars 6 LH, 10 RH), dotted-16th + 32nd '
                            'pairs and double-dotted eighth + 32nd (bar 6), 8.+32+32 (bar 4), beams across 16th and '
                            'eighth rests (LH bars 5, 8; RH bar 9), groups that start after a 16th rest (bar 8), tie '
                            'e\'4~e\'16 (bar 11), fermatas on the final chords. At 100 dpi (scan-severe.pdf) 32nd and '
                            '64th beams merge into solid bands: the number of beams must still be inferred.'),
        truth_limitations=[BEAM_TRUTH, TUPLET_TRUTH, PENCIL],
        variants={
            'scan.pdf': V(710801, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'pencil', 'circles': 2, 'fake_triplets': 1, 'fingerings': 8, 'ticks': 1, 'words': [],
                 'bracket': False},
                {'op': 'motion_blur', 'length': 4, 'angle': 0},
                {'op': 'blur', 'sigma': 0.7},
                {'op': 'noise', 'sigma': 4}], jpeg=35),
            'scan-mild.pdf': V(710802, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'blur', 'sigma': 0.4},
                {'op': 'noise', 'sigma': 2}], jpeg=60),
            'scan-severe.pdf': V(710803, 100, [
                {'op': 'paper', 'rgb': [246, 246, 244]},
                {'op': 'rotate', 'deg': -0.9, 'bg': 255},
                {'op': 'binarize', 'threshold': 170, 'pre_blur': 0.6, 'noise': 10}], fmt='png1'),
        }),
]
