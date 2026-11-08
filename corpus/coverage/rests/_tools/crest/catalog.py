"""coverage/rests catalog: items, layouts, expected conversion results, truth notes, minimum
symbol counts (build guard rails) and the two damage variants per item (scan.pdf = typical
200-300 dpi office scan, scan-severe.pdf = heavy damage), params + seed recorded in meta.json."""
from . import items as I

ATT = I.CC0

REST_POS = ('Rest vertical positions: a rest drawn away from its normal place carries <display-step>/'
            '<display-octave> = the pitch whose staff position it takes (LilyPond pitched rest, or '
            'MultiMeasureRest staff-position). The middle staff line is the normal position for EVERY rest value '
            '(so display B4 in treble clef = a whole rest hanging from the 4th line as usual, the MuseScore '
            'convention); other pitches shift the symbol by the same number of staff steps. Rests without '
            '<display-step> are at their normal position. Every rest position was read back from the LilyPond '
            'layout (staff-position and glyph extent) and matches the truth.')
MMR = ('Whole-bar rests are <rest measure="yes"/> with the bar duration and no <type> (the glyph is a whole rest, '
       'or a breve rest in 4/2). A multi-bar rest is one measure per bar, each with a measure rest; the first bar '
       'carries <measure-style><multiple-rest use-symbols="yes|no">n</multiple-rest>. The number printed above '
       'the rest is implied by n; the exact church-rest glyph combination (longa / breve / whole rest symbols) is '
       'not encoded beyond use-symbols="yes".')
BEAMS = ('<beam> elements reproduce the engraved beam groups (manual beaming); notes only: a rest under a beam '
         'carries no <beam> element (the beam is continued by the notes either side; secondary beams around a '
         'rest are written as hooks).')
STEMS = '<stem> is written for every stemmed note from the engraved stem direction (read back from the layout).'
TUPLETS = ('<tuplet bracket="yes|no"> follows LilyPond\'s default (bracket omitted only when one beam spans exactly '
           'the tuplet); rests inside tuplets carry <time-modification> and may start/stop the tuplet.')
LIC = 'CC0'


def V(seed, dpi, ops, color='gray', fmt='jpeg', jpeg=None, passes=1, severity='typical'):
    v = {'seed': seed, 'dpi': dpi, 'color': color, 'ops': ops, 'format': fmt, 'severity': severity}
    if fmt == 'jpeg':
        v['jpeg'] = jpeg
        v['jpeg_passes'] = passes
    return v


def typical(seed, dpi=300, deg=0.6, jpeg=65, noise=4, blur=0.5, paper=(244, 242, 236)):
    """typical flatbed/office scan: slight skew, a little blur and sensor noise, JPEG"""
    return V(seed, dpi, [
        {'op': 'paper', 'rgb': list(paper), 'texture': 3},
        {'op': 'rotate', 'deg': deg, 'bg': 235},
        {'op': 'gradient', 'strength': 0.06},
        {'op': 'blur', 'sigma': blur},
        {'op': 'noise', 'sigma': noise}], jpeg=jpeg)


ITEMS = [
    dict(
        id='rst01-rest-values', title='Rest Values (oboe): every rest from breve to 64th', make=I.mk_rst01,
        layout='melody', pages=1,
        focus=['rest-breve', 'rest-whole', 'rest-half', 'rest-quarter', 'rest-8th', 'rest-16th', 'rest-32nd',
               'rest-64th'],
        expected=dict(parts=['Oboe'], must_not_split=False,
                      notes='16 bars, one staff. 4/4 bars 1-11: quarter, half, eighth, 16th, 32nd and 64th rests, '
                            'many as "rest ladders" (64th+32nd+16th+8th+quarter rests after one short note, bars '
                            '9-11). 4/2 bars 12-16: whole rests (bars 12, 14, 16), half rests and two ordinary '
                            'breve rests (bars 13, 15) that fill the 4/2 bar but are entered as breve rests '
                            '(type breve), not as whole-bar rests.'),
        notes=['Bars 13 and 15 contain an ordinary breve rest (<rest/><type>breve</type>), not a whole-bar rest: '
               'LilyPond places it at the left like a note value, whereas a whole-bar rest is centred. A converter '
               'that writes <rest measure="yes"/> there has the right duration but the wrong rest kind.',
               STEMS, BEAMS],
        min_counts={'rest-breve': 2, 'rest-whole': 3, 'rest-half': 4, 'rest-quarter': 8, 'rest-8th': 20,
                    'rest-16th': 15, 'rest-32nd': 10, 'rest-64th': 10},
        attribution='Rest Values for oboe - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810101, 300, deg=0.6, jpeg=65),
            'scan-severe.pdf': V(810102, 200, [
                {'op': 'ink_dropout', 'amount': 0.2},
                {'op': 'paper', 'rgb': [236, 230, 214], 'texture': 6, 'bleed': {'strength': 0.25}},
                {'op': 'rotate', 'deg': -3.2, 'bg': [90, 85, 80]},
                {'op': 'gradient', 'strength': 0.25},
                {'op': 'blur', 'sigma': 1.1},
                {'op': 'noise', 'sigma': 9, 'chroma': 2},
                {'op': 'speckle', 'per_mpx': 120},
                {'op': 'downsample', 'dpi': 150}], color='rgb', jpeg=25, severity='severe'),
        }),
    dict(
        id='rst02-dotted-rests', title='Dotted Rests (violoncello): dotted and double-dotted rests',
        make=I.mk_rst02, layout='melody', pages=1,
        focus=['rest-dotted', 'double-dot', 'dot'],
        expected=dict(parts=['Violoncello'], must_not_split=False,
                      notes='16 bars, bass clef. Dotted rests of every value: dotted half (bar 1; dotted half in '
                            '12/8 bar 14), dotted quarter (2, 9, 11-15), dotted eighth (3, 10, 16), dotted 16th '
                            '(4), dotted 32nd (5), double-dotted quarter (6), double-dotted eighth (7, 16), '
                            'double-dotted half (8). Meters 4/4, 3/4 (9), 6/8 (11), 9/8 (13), 12/8 (14), 4/4 (16). '
                            'Each dotted rest is followed by the short note that completes its beat.'),
        notes=['dot / double-dot counts include rests (an augmentation dot after a rest is the same glyph).',
               STEMS, BEAMS],
        min_counts={'rest-dotted': 18},
        attribution='Dotted Rests for violoncello - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810201, 200, deg=-0.9, jpeg=70, noise=3, blur=0.4),
            'scan-severe.pdf': V(810202, 200, [
                {'op': 'paper', 'rgb': [250, 250, 250]},
                {'op': 'rotate', 'deg': 2.4, 'bg': 255},
                {'op': 'speckle', 'per_mpx': 250},
                {'op': 'binarize', 'threshold': 165, 'pre_blur': 1.1, 'noise': 28},
                {'op': 'saltpepper', 'amount': 0.003}], fmt='png1', severity='severe'),
        }),
    dict(
        id='rst03-whole-bar-rests-simple', title='Whole-Bar Rests I (violin): simple meters', make=I.mk_rst03,
        layout='melody', pages=1,
        focus=['rest-whole-bar', 'time-2-4', 'time-3-4', 'time-4-4', 'time-common', 'time-cut', 'time-3-2',
               'time-5-4', 'x-time-4-2'],
        expected=dict(parts=['Violin'], must_not_split=False,
                      notes='16 bars alternating one bar of notes and one whole-bar rest per meter: 2/4, 3/4, '
                            '4/4 (numeric), C, cut time, 3/2, 5/4 (rest with fermata = general pause) and 4/2 '
                            '(whole-bar rest drawn as a breve rest). Every whole-bar rest must last the full bar '
                            'of its meter (2, 3, 4, 4, 4, 6, 5, 8 quarters).'),
        notes=[MMR, 'The 5/4 whole-bar rest (bar 14) carries a fermata (general pause); no "G.P." text is printed.',
               'Bar 7 restates 4/4 as the C symbol after a numeric 4/4 (a time-signature style change, counted as '
               'time-change).', STEMS],
        min_counts={'rest-whole-bar': 8},
        attribution='Whole-Bar Rests I for violin - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810301, 300, deg=1.1, jpeg=60, noise=5),
            'scan-severe.pdf': V(810302, 150, [
                {'op': 'ink_weight', 'px': 1},
                {'op': 'paper', 'rgb': [240, 236, 226], 'texture': 5},
                {'op': 'pencil', 'circles': 3, 'ticks': 3, 'fingerings': 2, 'words': ['tacet?']},
                {'op': 'perspective', 'margin': 0.04, 'jitter': 0.02, 'keystone': 0.035, 'bg': [60, 55, 50]},
                {'op': 'vignette', 'strength': 0.3},
                {'op': 'motion_blur', 'length': 4, 'angle': 15},
                {'op': 'noise', 'sigma': 8, 'chroma': 2}], color='rgb', jpeg=25, severity='severe'),
        }),
    dict(
        id='rst04-whole-bar-rests-compound', title='Whole-Bar Rests II (viola): compound and irregular meters',
        make=I.mk_rst04, layout='melody', pages=1,
        focus=['rest-whole-bar', 'clef-alto', 'time-6-8', 'time-9-8', 'time-12-8', 'time-5-8', 'time-7-8',
               'x-time-3-8', 'x-time-6-4'],
        expected=dict(parts=['Viola'], must_not_split=False,
                      notes='16 bars in alto clef alternating one bar of notes and one whole-bar rest per meter: '
                            '3/8, 6/8, 9/8, 12/8, 5/8, 7/8, 6/4 and 3/4 (last rest with fermata). Every whole-bar '
                            'rest is a whole-rest glyph centred in the bar and must last the full bar (1.5, 3, '
                            '4.5, 6, 2.5, 3.5, 6, 3 quarters).'),
        notes=[MMR, STEMS, BEAMS],
        min_counts={'rest-whole-bar': 8},
        attribution='Whole-Bar Rests II for viola - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810401, 200, deg=0.4, jpeg=60, noise=4, blur=0.6, paper=(246, 244, 240)),
            'scan-severe.pdf': V(810402, 200, [
                {'op': 'paper', 'rgb': [232, 224, 200], 'texture': 7, 'ink_var': 30},
                {'op': 'foxing', 'n': 50},
                {'op': 'coffee', 'n': 1},
                {'op': 'rotate', 'deg': -4.0, 'bg': [70, 70, 70]},
                {'op': 'shadow', 'pos': 0.2, 'strength': 0.45},
                {'op': 'blur', 'sigma': 1.3},
                {'op': 'noise', 'sigma': 10, 'chroma': 3}], color='rgb', jpeg=22, passes=2, severity='severe'),
        }),
    dict(
        id='rst05-multibar-rests', title='Tacet Interludes (trumpet part): multi-bar rests', make=I.mk_rst05,
        layout='melody', pages=1,
        focus=['rest-multibar', 'x-rest-multibar-hbar', 'x-rest-multibar-symbols', 'rehearsal-mark'],
        expected=dict(parts=['Trumpet in C'], must_not_split=False,
                      notes='94 measures although only 16 bars are drawn. Multi-bar rests must be expanded to the '
                            'right number of measures: H-bar 16 (bars 1-16, 4/4), church-rest symbols 2 (18-19), '
                            '3 (21-23), 4 (25-28, a longa rest), 6 in 3/4 (29-34), forced H-bar 5 in 3/4 (36-40), '
                            'H-bar 12 in 6/8 (42-53), church-rest symbols 7 in cut time (54-60), H-bar 32 in 4/4 '
                            '(61-92); rehearsal marks A (17), B (29), C (54), D (61). Bars of notes: 17, 20, 24, 35, '
                            '41, 93, 94.'),
        notes=[MMR, 'The four time-signature changes fall at the start of a multi-bar rest (bars 29, 54, 61) or of a '
               'bar of notes (41).', STEMS],
        min_counts={'rest-multibar': 9},
        attribution='Tacet Interludes (trumpet in C part) - composed for the OMR coverage corpus (rests family).\n\n'
                    + ATT,
        variants={
            'scan.pdf': typical(810501, 300, deg=-0.5, jpeg=70, noise=3),
            'scan-severe.pdf': V(810502, 200, [
                {'op': 'ink_dropout', 'amount': 0.3},
                {'op': 'paper', 'rgb': [244, 240, 230], 'texture': 4},
                {'op': 'halftone', 'lpi': 85, 'angle': 45},
                {'op': 'rotate', 'deg': 3.0, 'bg': 30},
                {'op': 'noise', 'sigma': 7},
                {'op': 'saltpepper', 'amount': 0.002},
                {'op': 'downsample', 'dpi': 150}], jpeg=30, severity='severe'),
        }),
    dict(
        id='rst06-two-voice-rests', title='Hocket for Two Flutes: raised and lowered rests on one staff',
        make=I.mk_rst06, layout='two-voices-one-staff-instrument', pages=1,
        focus=['x-rest-raised', 'x-rest-lowered', 'x-rest-whole-bar-shared-staff', 'stem-up', 'stem-down'],
        expected=dict(parts=['Flutes 1.2'], must_not_split=True,
                      notes='12 bars, ONE part (instrumental staff "Flutes 1.2") with two voices: voice 1 stems '
                            'up, voice 2 stems down. Every rest of voice 1 is raised (quarter/eighth/16th/half/'
                            'dotted-quarter rests at the F5 position, whole-bar rests hanging from the top line), '
                            'every rest of voice 2 lowered (E4 position, whole-bar rests hanging from the bottom '
                            'line). The voices alternate (hocket), so most rests of one voice sound against notes '
                            'of the other; bars 8 and 10 have rests in both voices at once and bar 9 a whole-bar '
                            'rest in each voice. A converter should keep one part with two voices and assign each '
                            'rest to its voice by its height.'),
        notes=[REST_POS, 'Bars 4, 5, 9: whole-bar rests of one voice (or both) in a two-voice staff are '
               '<rest measure="yes"> in that voice, with display-step/octave.', STEMS],
        min_counts={'x-rest-raised': 15, 'x-rest-lowered': 15},
        attribution='Hocket for Two Flutes - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810601, 300, deg=0.8, jpeg=65),
            'scan-severe.pdf': V(810602, 200, [
                {'op': 'paper', 'rgb': [238, 232, 216], 'texture': 6, 'bleed': {'strength': 0.3}},
                {'op': 'perspective', 'margin': 0.05, 'jitter': 0.025, 'keystone': 0.04, 'bg': [50, 45, 40]},
                {'op': 'gradient', 'strength': 0.3, 'angle': 30},
                {'op': 'blur', 'sigma': 1.2},
                {'op': 'noise', 'sigma': 9, 'chroma': 2},
                {'op': 'speckle', 'per_mpx': 100}], color='rgb', jpeg=24, severity='severe'),
        }),
    dict(
        id='rst07-piano-rests', title='Left-Hand Silences (piano): rests in both hands', make=I.mk_rst07,
        layout='piano', pages=1,
        focus=['rest-quarter', 'rest-8th', 'rest-16th', 'rest-32nd', 'rest-half', 'rest-dotted', 'rest-whole-bar',
               'x-rest-raised', 'x-rest-lowered'],
        expected=dict(parts=['Piano'], must_not_split=True,
                      notes='14 bars, ONE part with two staves (grand staff). Left-hand rests: quarter (1), eighth '
                            '(2), 16th (3, before beamed 16ths), whole-bar (5, 4/4; 10, 3/4), half (6), dotted '
                            'quarter (7), 32nd/16th/eighth/quarter ladder (8), dotted eighth (9); bars 11-12: two '
                            'left-hand voices with raised (A3 position) and lowered (G2 position) rests. Right-hand '
                            'rests: whole-bar (4), half (6), eighth and quarter (7), quarter (9, 12). Bar 13: '
                            'whole-bar rests with fermatas in both hands (general pause). Meters 4/4, 3/4 (9-12), '
                            '4/4 (13-14).'),
        notes=[REST_POS, MMR, 'Voice 6 (second left-hand voice) only sounds in bars 11-12; elsewhere it is absent '
               '(<forward>), not resting.', STEMS, BEAMS],
        min_counts={'rest-whole-bar': 5, 'x-rest-raised': 3, 'x-rest-lowered': 3},
        attribution='Left-Hand Silences for piano - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810701, 200, deg=-0.7, jpeg=65, noise=4),
            'scan-severe.pdf': V(810702, 150, [
                {'op': 'paper', 'rgb': [242, 238, 228], 'texture': 5},
                {'op': 'crop', 'side': 'right', 'into_staff': 0.4, 'bg': 255},
                {'op': 'punch_holes', 'n': 3, 'side': 'left', 'bg': 25},
                {'op': 'rotate', 'deg': 3.6, 'bg': 255},
                {'op': 'curl', 'side': 'right', 'amp': 20, 'width': 0.25},
                {'op': 'blur', 'sigma': 1.0},
                {'op': 'noise', 'sigma': 8}], jpeg=28, severity='severe'),
        }),
    dict(
        id='rst08-tuplet-beam-rests', title='Rests in Tuplets and Beams (flute)', make=I.mk_rst08,
        layout='melody', pages=1,
        focus=['x-rest-in-tuplet', 'x-rest-in-beam', 'tuplet-3', 'tuplet-5', 'tuplet-6', 'tuplet-7', 'tuplet-2',
               'beam'],
        expected=dict(parts=['Flute'], must_not_split=False,
                      notes='12 bars. Rests at the start, middle and end of tuplets: eighth triplets (1, 8), '
                            'quarter triplets (2), 16th quintuplets and sextuplets (3), septuplets (4), 16th '
                            'triplets (8), duplets in 6/8 (9) and a quadruplet (12). Beams that continue over '
                            'eighth, 16th and 32nd rests (bars 1, 3-8, 10-12): the rest is inside the beam group '
                            'and keeps its own duration. Meters 4/4 (1-8), 6/8 (9-12).'),
        notes=[TUPLETS, BEAMS,
               'Rests under a beam are moved up or down by LilyPond to clear the beam (single voice, no explicit '
               'position in the source); their engraved staff position was read back from the layout and written '
               'as <display-step>/<display-octave>, so they also count as x-rest-raised / x-rest-lowered. ' + REST_POS,
               'No nested tuplets in this item (tuplet-nested is not covered by the rests family).', STEMS],
        min_counts={'x-rest-in-tuplet': 20, 'x-rest-in-beam': 20},
        attribution='Rests in Tuplets and Beams for flute - composed for the OMR coverage corpus (rests family).\n\n'
                    + ATT,
        variants={
            'scan.pdf': typical(810801, 300, deg=0.3, jpeg=55, noise=5, blur=0.6),
            'scan-severe.pdf': V(810802, 200, [
                {'op': 'ink_weight', 'px': -1},
                {'op': 'paper', 'rgb': [248, 246, 240], 'texture': 3},
                {'op': 'rotate', 'deg': -2.8, 'bg': 245},
                {'op': 'wave', 'amp': 6, 'period': 0.7},
                {'op': 'blur', 'sigma': 0.9},
                {'op': 'noise', 'sigma': 10},
                {'op': 'downsample', 'dpi': 150}], jpeg=22, severity='severe'),
        }),
    dict(
        id='rst09-quartet-rests', title='Quartet Fughetta: rests in a string quartet', make=I.mk_rst09,
        layout='string-quartet', pages=1,
        focus=['rest-whole-bar', 'rest-quarter', 'rest-8th', 'rest-16th', 'rest-half', 'rest-dotted',
               'x-rest-fermata', 'clef-alto', 'clef-bass'],
        expected=dict(parts=['Violin I', 'Violin II', 'Viola', 'Violoncello'], must_not_split=False,
                      notes='12 bars in 3/4, F major, four parts on four staves (bracket): treble, treble, alto '
                            'and bass clef. Staggered fugato entries: Violin II rests bars 1-2, viola bars 1-4 '
                            '(whole-bar rests, one per bar, no multi-bar rests in a score), cello bars 1-2. Bar 9 '
                            'is a general pause: a whole-bar rest with fermata in every part. Quarter, eighth, '
                            'half and dotted-eighth rests throughout; dotted-quarter notes followed by eighth '
                            'rests (bar 11).'),
        notes=[MMR, STEMS, BEAMS],
        min_counts={'rest-whole-bar': 13, 'x-rest-fermata': 4},
        attribution='Quartet Fughetta - composed for the OMR coverage corpus (rests family).\n\n' + ATT,
        variants={
            'scan.pdf': typical(810901, 300, deg=-1.0, jpeg=65, noise=4),
            'scan-severe.pdf': V(810902, 200, [
                {'op': 'paper', 'rgb': [250, 250, 250]},
                {'op': 'rotate', 'deg': -2.2, 'bg': 255},
                {'op': 'speckle', 'per_mpx': 180},
                {'op': 'binarize', 'threshold': 95, 'pre_blur': 0.8, 'noise': 22},
                {'op': 'saltpepper', 'amount': 0.004}], fmt='png1', severity='severe'),
        }),
]
