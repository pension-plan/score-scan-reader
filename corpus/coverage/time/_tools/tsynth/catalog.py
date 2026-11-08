"""Coverage suite, family 'time': items, layout tags, target symbols, expected conversion results,
truth limitations and the two scan variants per item (scan.pdf = typical 200-300 dpi office scan,
scan-severe.pdf = heavy damage); damage params + seed are recorded verbatim in meta.json."""
from . import items as I

LIC = 'CC0-1.0 (music composed for this corpus; engraving, truth and scans CC0)'

COURTESY = ('Courtesy time signatures that LilyPond prints at the end of a system before a meter change are '
            'NOT separate <time> elements in the truth (MusicXML has no courtesy-time element; the change is '
            'the <time> in the first measure of the next system). Do not count them as extra time changes.')
STEMS = ('Stem directions are not in the truth for single-voice staves (LilyPond chooses them); stem-up / '
         'stem-down are therefore neither listed nor counted for this item.')
BEAMS = ('<beam> elements reproduce the engraved beam groups exactly (manual beaming, \\autoBeamOff); a rest '
         'inside a beam carries no <beam>.')
TUPLET = ('<tuplet bracket="yes|no"> is what LilyPond printed (verified per tuplet by a TupletBracket stencil '
          'callback): the bracket is omitted when one beam spans exactly the tuplet\'s first to last note. '
          'LilyPond prints the actual number only ("3", "5", "2"), MusicXML default show-number="actual".')
NESTED = ('Nested tuplets: <time-modification> carries the product ratio (e.g. 9:4 for 3:2 inside 3:2, 15:8 for '
          '3:2 inside 5:4); every level has its own numbered <tuplet> start/stop with <tuplet-actual>/'
          '<tuplet-normal> giving the per-level ratio and unit. music21 re-reads the levels as a tuple of '
          'Tuplet objects.')
TIES = ('Ties are per notehead (<tie>/<tied> on each tied chord member). A tie across a system or page break '
        'is engraved as two half-ties (one at the end of the first system, one at the start of the next); '
        'the truth has ONE tie (start on the last note of the system, stop on the first note of the next).')
COUNTS = ('Counts follow meta.counting_rules: time-4-4 / time-2-2 count numeric signatures only, C and cut '
          'count as time-common / time-cut; a piano grand staff prints each time signature on both staves but '
          'the truth (and the count) has one <time> per measure.')


def V(seed, dpi, ops, color='gray', fmt='jpeg', jpeg=None, passes=1):
    v = {'seed': seed, 'dpi': dpi, 'color': color, 'ops': ops, 'format': fmt}
    if fmt == 'jpeg':
        v['jpeg'] = jpeg
        v['jpeg_passes'] = passes
    return v


def att(title, extra=''):
    return f'{title} - composed for the OMR coverage suite (family "time").\n{extra}\n' + I.CC0


ITEMS = [
    dict(
        id='t01-simple-meters', title='Simple Meters (flute)', make=I.mk_t01, pages=1, layout='melody',
        targets=['time-2-4', 'time-3-4', 'time-4-4', 'time-5-4', 'time-2-2', 'time-3-2', 'time-change',
                 'x-time-courtesy', 'pickup', 'tie', 'tie-across-system'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Simple Meters for flute'),
        expected=dict(parts=['Flute'], must_not_split=False,
                      notes='One flute staff, 13 measures (quarter-note pickup = measure 0, implicit). The meter '
                            'changes in every bar after m1, cycling twice through numeric 2/4 (m0, m7), 3/4 (m2, '
                            'm8), 4/4 printed as numbers NOT C (m3, m9), 5/4 (m4, m10), 2/2 printed as numbers NOT '
                            'cut (m5, m11) and 3/2 (m6, m12): 12 time signatures, 11 changes; m4, m6, m9 and m11 '
                            'start systems, so courtesy signatures end the previous systems. Ties a\' m3->m4, '
                            'e\'\' m5->m6, d\'\' m8->m9 and c\'\' m10->m11 each cross a system break AND a meter '
                            'change. Key G major.'),
        truth_limitations=[COURTESY, TIES, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730101, 300, [
                {'op': 'paper', 'rgb': [246, 246, 243], 'texture': 2},
                {'op': 'rotate', 'deg': 0.6, 'bg': 235},
                {'op': 'blur', 'sigma': 0.4},
                {'op': 'noise', 'sigma': 3}], jpeg=70),
            'scan-severe.pdf': V(730102, 150, [
                {'op': 'ink_weight', 'px': 1},
                {'op': 'paper', 'rgb': [248, 248, 248]},
                {'op': 'rotate', 'deg': -4.0, 'bg': 255},
                {'op': 'binarize', 'threshold': 175, 'pre_blur': 1.0, 'noise': 22},
                {'op': 'saltpepper', 'amount': 0.002}], fmt='png1'),
        }),
    dict(
        id='t02-compound-irregular', title='Compound and Irregular Meters (violoncello)', make=I.mk_t02, pages=1,
        layout='melody',
        targets=['time-6-8', 'time-9-8', 'time-12-8', 'time-5-8', 'time-7-8', 'time-change', 'x-time-courtesy',
                 'pickup', 'tie', 'tie-across-system', 'rest-dotted'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Compound and Irregular Meters'),
        expected=dict(parts=['Violoncello'], must_not_split=False,
                      notes='One bass-clef staff, 12 measures: eighth pickup in 6/8 (m0, implicit) and an '
                            'incomplete final bar of 5 eighths (m11, NOT padded). The meter changes in every bar '
                            'after m1: 6/8 (m0, m6, m11), 9/8 (m2, m7), 12/8 (m3, m8), 5/8 (m4 beamed 3+2, m9 '
                            'beamed 2+3), 7/8 (m5 beamed 2+2+3, m10 beamed 3+2+2): 11 signatures, 10 changes; m3, '
                            'm5, m8 and m10 start systems. Ties a m2->m3, c\' m4->m5, bes m7->m8 and f m9->m10 '
                            'each cross a system break and a meter change; f inside m11. A dotted-quarter rest in '
                            'm6 and an eighth rest in m8. Key F major.'),
        truth_limitations=[COURTESY, TIES, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730201, 250, [
                {'op': 'paper', 'rgb': [244, 240, 228], 'texture': 3},
                {'op': 'rotate', 'deg': -0.9, 'bg': [225, 225, 225]},
                {'op': 'gradient', 'strength': 0.06},
                {'op': 'noise', 'sigma': 3, 'chroma': 1}], color='rgb', jpeg=65),
            'scan-severe.pdf': V(730202, 200, [
                {'op': 'paper', 'rgb': [238, 234, 225], 'texture': 4},
                {'op': 'perspective', 'margin': 0.05, 'jitter': 0.03, 'keystone': 0.06, 'bg': [55, 50, 45]},
                {'op': 'shadow', 'strength': 0.4, 'pos': 0.2, 'soft': 0.07},
                {'op': 'vignette', 'strength': 0.25},
                {'op': 'motion_blur', 'length': 6, 'angle': 15},
                {'op': 'noise', 'sigma': 7, 'chroma': 3},
                {'op': 'downsample', 'dpi': 120}], color='rgb', jpeg=18),
        }),
    dict(
        id='t03-common-cut-piano', title='Common and Cut Time (piano)', make=I.mk_t03, pages=1, layout='piano',
        targets=['time-common', 'time-cut', 'time-4-4', 'time-2-2', 'time-change', 'x-time-courtesy', 'pickup',
                 'tie', 'tie-across-system', 'chord'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Common and Cut Time for piano'),
        expected=dict(parts=['Piano'], must_not_split=True,
                      notes='ONE part, grand staff (2 staves), 11 measures, three-eighth pickup (m0, implicit; '
                            'left hand has an eighth and a quarter rest). The signature changes in every bar from '
                            'm2, alternating glyphs for the same two meters (printed on both staves): C (m0, m5, '
                            'm9), cut (m2, m6, m10), numeric 4/4 (m3, m7), numeric 2/2 (m4, m8). C and 4/4, cut and '
                            '2/2 are the same meter with different glyphs - the truth distinguishes them with '
                            '<time symbol="common|cut">. Ties: RH g\' m2->m3, b\' m5->m6, b\' m8->m9 (each across a '
                            'system break and a glyph change); LH chord G-B-D m2->m3 (3 ties, across the system '
                            'break) and chord C-E-G m4->m5 (3 ties, across 2/2 -> C).'),
        truth_limitations=[COURTESY, TIES, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730301, 200, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 1.1, 'bg': 230},
                {'op': 'blur', 'sigma': 0.5},
                {'op': 'noise', 'sigma': 3}], jpeg=60),
            'scan-severe.pdf': V(730302, 300, [
                {'op': 'paper', 'rgb': [240, 238, 232], 'texture': 3},
                {'op': 'halftone', 'lpi': 85, 'angle': 45, 'supersample': 2},
                {'op': 'rotate', 'deg': 7.0, 'bg': 50},
                {'op': 'blur', 'sigma': 1.0},
                {'op': 'noise', 'sigma': 6},
                {'op': 'downsample', 'dpi': 120}], jpeg=22),
        }),
    dict(
        id='t04-pickup-song', title='The Tyger (voice, pickup and meter changes with lyrics)', make=I.mk_t04,
        pages=1, layout='melody-lyrics',
        targets=['pickup', 'time-3-4', 'time-6-8', 'time-2-4', 'time-change', 'tie', 'tie-across-system',
                 'lyrics'],
        source='Text: William Blake, "The Tyger", Songs of Experience (1794), public domain. Melody composed for '
               'this corpus (CC0).',
        license='Text public domain (Blake 1794); music, engraving, truth and scans CC0-1.0',
        attribution=att('The Tyger (song)', 'Text: William Blake, "The Tyger" (Songs of Experience, 1794) - '
                                             'public domain.'),
        expected=dict(parts=['Voice'], must_not_split=False,
                      notes='One voice staff with one lyric line, 13 measures: quarter pickup (m0, implicit, '
                            'syllable "Ty-") and an incomplete final bar of 2 beats (m12, NOT padded). Meters 3/4, '
                            '6/8 (m5, system start: courtesy 6/8 ends system 1), 2/4 (m7, mid-system), 3/4 (m9, '
                            'mid-system). Ties: c\'\' inside m2, f\' '
                            'm4->m5 (across the system break AND 3/4 -> 6/8; the tie continuation carries no '
                            'syllable), g\' m10->m11 (across the system break). One syllable per attack; melisma '
                            '"hand" over 3 notes (m7-m8) with an extender; "for- ests" is split by an eighth '
                            'rest. Key F major.'),
        truth_limitations=[COURTESY, TIES, STEMS, BEAMS, COUNTS,
                           'Lyric hyphens may be omitted by LilyPond where syllables are close; truth keeps '
                           'syllabic begin/middle/end as entered.'],
        variants={
            'scan.pdf': V(730401, 300, [
                {'op': 'paper', 'rgb': [247, 247, 245], 'texture': 2},
                {'op': 'rotate', 'deg': -0.4, 'bg': 238},
                {'op': 'noise', 'sigma': 2}], jpeg=75),
            'scan-severe.pdf': V(730402, 150, [
                {'op': 'paper', 'rgb': [250, 250, 250]},
                {'op': 'punch_holes', 'n': 2, 'side': 'left', 'bg': 20},
                {'op': 'rotate', 'deg': 3.0, 'bg': 255},
                {'op': 'speckle', 'per_mpx': 80},
                {'op': 'binarize', 'threshold': 95, 'pre_blur': 0.6, 'noise': 18}], fmt='png1'),
        }),
    dict(
        id='t05-triplets-duplets', title='Triplets and Duplets (oboe)', make=I.mk_t05, pages=1, layout='melody',
        targets=['tuplet-3', 'tuplet-2', 'x-tuplet-4', 'time-2-4', 'time-cut', 'time-6-8', 'time-9-8',
                 'time-12-8', 'time-change', 'tie', 'tie-across-system'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Triplets and Duplets for oboe'),
        expected=dict(parts=['Oboe'], must_not_split=False,
                      notes='One staff, 12 measures, no pickup. 3:2 triplets on eighths (m1 x2, m3, m4 x2, m11), '
                            'quarters (m2, m6 x2), sixteenths (m3 x2, m11) and halves (m5, cut time); a triplet with a rest '
                            'inside (m4: eighth-rest-eighth under one beam) and one of mixed values (m4: eighth + '
                            'quarter, bracket). 2:3 duplets of eighths in 6/8, 9/8 and 12/8 (m7, m9, m10) and of '
                            'quarters in 6/8 (m8, bracket); one 4:3 quadruplet in 9/8 (m9, tagged x-tuplet-4). '
                            'Tie e\'\' from the last quarter-triplet note of m6 into the first duplet note of m7 '
                            '(across the system break and 2/2 -> 6/8). Meters 2/4, cut (m5), 6/8 (m7, system '
                            'start), 9/8 (m9), 12/8 (m10, system start), 2/4 (m11).'),
        truth_limitations=[TUPLET, COURTESY, TIES, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730501, 300, [
                {'op': 'paper', 'rgb': [245, 244, 240], 'texture': 2},
                {'op': 'rotate', 'deg': 1.4, 'bg': [228, 228, 228]},
                {'op': 'blur', 'sigma': 0.5},
                {'op': 'noise', 'sigma': 3, 'chroma': 1}], color='rgb', jpeg=55),
            'scan-severe.pdf': V(730502, 150, [
                {'op': 'paper', 'rgb': [228, 212, 170], 'texture': 8, 'bleed': {'strength': 0.22}, 'ink_var': 25},
                {'op': 'foxing', 'n': 160, 'strength': 0.6},
                {'op': 'coffee', 'n': 2, 'radius_mm': 40, 'strength': 0.55},
                {'op': 'rotate', 'deg': -2.5, 'bg': [190, 190, 190]},
                {'op': 'blur', 'sigma': 1.0},
                {'op': 'noise', 'sigma': 5, 'chroma': 2}], color='rgb', jpeg=20),
        }),
    dict(
        id='t06-quint-sext-sept', title='Fives, Sixes and Sevens (flute)', make=I.mk_t06, pages=1,
        layout='melody',
        targets=['tuplet-5', 'tuplet-6', 'tuplet-7', 'time-common', 'pickup', 'tie', 'tie-across-system',
                 'double-dot'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Fives, Sixes and Sevens for flute'),
        expected=dict(parts=['Flute'], must_not_split=False,
                      notes='One staff in C (common-time symbol), 9 measures: eighth pickup (m0, implicit) and '
                            'final bar of 7 eighths written as a double-dotted half (m8, NOT padded). 5:4 on '
                            'sixteenths (m1 x2, m7 with a sixteenth rest inside), on eighths over a half (m4) and '
                            'on quarters over a whole bar (m5); 6:4 on sixteenths (m2 x2, m7) and on eighths (m4); '
                            '7:4 on sixteenths (m3) and eighths (m6), 7:8 on 32nds (m3). Ties a\' m4->m5 '
                            '(sextuplet -> quintuplet) and e\'\' m5->m6 (quintuplet -> septuplet, across the '
                            'system break).'),
        truth_limitations=[TUPLET, TIES, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730601, 250, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': -0.7, 'bg': 232},
                {'op': 'noise', 'sigma': 2.5}], jpeg=65),
            'scan-severe.pdf': V(730602, 300, [
                {'op': 'ink_dropout', 'amount': 0.25},
                {'op': 'paper', 'rgb': [244, 243, 238], 'texture': 3},
                {'op': 'rotate', 'deg': 5.0, 'bg': 70},
                {'op': 'blur', 'sigma': 0.8},
                {'op': 'noise', 'sigma': 6},
                {'op': 'downsample', 'dpi': 100}], jpeg=20),
        }),
    dict(
        id='t07-nested-tuplets', title='Nested Tuplets (violin)', make=I.mk_t07, pages=1, layout='melody',
        targets=['tuplet-nested', 'tuplet-3', 'tuplet-5', 'tuplet-2', 'time-4-4', 'time-6-8', 'time-change', 'tie'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Nested Tuplets for violin'),
        expected=dict(parts=['Violin'], must_not_split=False,
                      notes='One staff, 7 measures, numeric 4/4 then 6/8 (m6). Nested groups (outer : inner): '
                            '(two measures per system, m5 alone). m1 3:2 eighths containing 3:2 sixteenths (one beam over the outer group: outer bracket '
                            'omitted, inner bracket printed); m2 3:2 quarters starting with a 3:2 eighth triplet '
                            '(both start on c\'\'); m3 5:4 eighths containing 3:2 sixteenths; m4 3:2 quarters '
                            'containing 5:4 sixteenths, then 3:2 quarters ending with a 3:2 eighth triplet (both '
                            'stop on d\'\'); m5 3:2 eighths starting with a rest and containing 3:2 sixteenths, then '
                            '3:2 eighths starting with 3:2 sixteenths (beams cross the inner group boundaries); m6 '
                            '2:3 duplet containing 3:2 sixteenths (both stop on f\'\'). Inner notes have nested '
                            'durations, e.g. 1/9 quarter (3:2 in 3:2 sixteenths) and 2/15 quarter (3:2 in 5:4).'),
        truth_limitations=[NESTED, TUPLET, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730701, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 0.3, 'bg': 240},
                {'op': 'noise', 'sigma': 2}], jpeg=70),
            'scan-severe.pdf': V(730702, 200, [
                {'op': 'paper', 'rgb': [244, 243, 238], 'texture': 3},
                {'op': 'pencil', 'circles': 4, 'fake_triplets': 3, 'fingerings': 4, 'ticks': 2,
                 'words': ['slow!']},
                {'op': 'crop', 'side': 'right', 'into_staff': 0.4, 'bg': 255},
                {'op': 'rotate', 'deg': -6.0, 'bg': 60},
                {'op': 'blur', 'sigma': 0.9},
                {'op': 'noise', 'sigma': 5}], jpeg=25),
        }),
    dict(
        id='t08-ties-systems-pages', title='Tied Across the Page (piano, 2 pages)', make=I.mk_t08, pages=2,
        layout='piano',
        targets=['tie', 'tie-across-system', 'x-tie-across-page', 'chord', 'time-3-4', 'time-6-8', 'time-change',
                 'page-break', 'multi-page', 'system-break'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Tied Across the Page for piano'),
        expected=dict(parts=['Piano'], must_not_split=True,
                      notes='ONE part, grand staff, 16 measures on 2 pages, two measures per system (8 systems, '
                            'page break before m9). Ties in both hands across nearly every system break and across '
                            'the page break (RH d\'\' m8->m9, LH G-D chord m8->m9). Full chord ties: LH C-G m1->m2, '
                            'RH G-B m5->m6, LH G-D m8->m9. Partial chord tie: only a\' of the RH chord F-A in m3 is '
                            'tied (to the chord G-A in m4). Accidental carried by a tie: f#\' m4->m5 (no sharp is '
                            'printed in m5). Tie out of a triplet (RH d\'\' m7->m8). Ties across meter changes '
                            '3/4 -> 6/8 (RH a\' m9->m10, then on inside m10) and 6/8 -> 3/4 (RH g\' m12->m13, '
                            'system break too).'),
        truth_limitations=[TIES, COURTESY, STEMS, BEAMS, COUNTS],
        variants={
            'scan.pdf': V(730801, 200, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': 0.8, 'bg': 235, 'pages': [0]},
                {'op': 'rotate', 'deg': -0.5, 'bg': 235, 'pages': [1]},
                {'op': 'noise', 'sigma': 3}], jpeg=60),
            'scan-severe.pdf': V(730802, 150, [
                {'op': 'paper', 'rgb': [240, 236, 226], 'texture': 4},
                {'op': 'curl', 'side': 'gutter', 'amp': 35, 'width': 0.3},
                {'op': 'gutter', 'side': 'gutter', 'width': 0.08, 'dark': 0.6},
                {'op': 'two_up', 'seam_px': 6, 'seam': 40},
                {'op': 'perspective', 'margin': 0.04, 'jitter': 0.02, 'keystone': 0.03, 'bg': [60, 55, 50]},
                {'op': 'vignette', 'strength': 0.3},
                {'op': 'motion_blur', 'length': 4, 'angle': 10},
                {'op': 'noise', 'sigma': 6, 'chroma': 2}], color='rgb', jpeg=20),
        }),
    dict(
        id='t09-two-voices-guitar', title='Hemiola for Guitar (two voices on one staff)', make=I.mk_t09, pages=1,
        layout='two-voices-one-staff-instrument',
        targets=['time-6-8', 'time-3-4', 'time-change', 'tuplet-2', 'tuplet-3', 'pickup', 'tie',
                 'tie-across-system', 'clef-treble-8vb'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Hemiola for Guitar'),
        expected=dict(parts=['Guitar'], must_not_split=True,
                      notes='ONE part: two voices on one treble-8vb (guitar) staff, stems up = voice 1, stems '
                            'down = voice 2; they must NOT become two parts. 8 measures: eighth pickup (m0: '
                            'voice 1 b, voice 2 eighth rest) and incomplete final bar of 5 eighths (m7). 6/8, 3/4 '
                            '(m3, hemiola), 6/8 (m5). Duplets in voice 1 against dotted quarters in voice 2 (m1, '
                            'm5, m6); triplet against a half note (m4). Ties: voice 1 b\' inside m2, e\' m3->m4 '
                            '(across the system break, into a triplet), e\' m5 (into a duplet), e\' m7; voice 2 '
                            'b, m3->m4 (across the system break), e m7. Pitches are written as sounding an octave '
                            'below the treble position (treble_8 clef, <clef-octave-change>-1).'),
        truth_limitations=[TUPLET, TIES, COURTESY, BEAMS, COUNTS,
                           'Both voices are present in every measure, so the truth gives <stem> up/down for '
                           'every stemmed note and stem-up/stem-down are counted.'],
        variants={
            'scan.pdf': V(730901, 300, [
                {'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                {'op': 'rotate', 'deg': -1.0, 'bg': 232},
                {'op': 'noise', 'sigma': 3}], jpeg=60),
            'scan-severe.pdf': V(730902, 200, [
                {'op': 'paper', 'rgb': [250, 250, 250]},
                {'op': 'staple', 'corner': 'tl'},
                {'op': 'punch_holes', 'n': 2, 'side': 'left', 'bg': 25},
                {'op': 'rotate', 'deg': 4.0, 'bg': 255},
                {'op': 'rot90', 'k': 2},
                {'op': 'binarize', 'threshold': 190, 'pre_blur': 1.0, 'noise': 25},
                {'op': 'saltpepper', 'amount': 0.0015}], fmt='png1'),
        }),
    dict(
        id='t10-quartet-meters', title='Quartet in Changing Meters (string quartet)', make=I.mk_t10, pages=1,
        layout='string-quartet',
        targets=['time-4-4', 'time-3-4', 'time-5-8', 'time-7-8', 'time-2-4', 'time-6-8', 'time-common',
                 'time-cut', 'time-change', 'x-time-courtesy', 'tuplet-3', 'tuplet-5', 'tuplet-2', 'tie',
                 'tie-across-system', 'clef-alto'],
        source='Composed for this corpus (CC0).', license=LIC, attribution=att('Quartet in Changing Meters'),
        expected=dict(parts=['Violin I', 'Violin II', 'Viola', 'Violoncello'], must_not_split=False,
                      notes='Four single-staff parts (bracketed string quartet; viola in alto clef), 8 measures, '
                            '3 systems. All four parts change meter together in every bar: numeric 4/4, 3/4, 5/8, '
                            '7/8, 2/4, 6/8, C, cut - each part carries its own <time> (8 x 4 = 32 in the truth). '
                            'Different tuplets sound at the same time: m1 eighth triplet (Vn I) against quarter '
                            'triplet (Vn II); m2 quarter triplet (Vn I); m5 5:4 sixteenths (Vn I) against an eighth '
                            'triplet (Vn II) and another (Va); m6 2:3 duplet (Vn II) against dotted quarters; m7 '
                            'eighth triplet (Vn I). Ties: Vn I a\' m1->m2, a\' m3->m4 (across the system break and '
                            '5/8 -> 7/8), f\'\' m5->m6, e\'\' m6->m7 (across the system break and 6/8 -> C); Va d\' '
                            'm2->m3. Key A minor.'),
        truth_limitations=[TUPLET, TIES, COURTESY, STEMS, BEAMS,
                           COUNTS + ' In this score every count of a time-signature tag is 4 x the number of '
                                    'changes because each of the 4 parts has its own <time> element.'],
        variants={
            'scan.pdf': V(731001, 250, [
                {'op': 'paper', 'rgb': [246, 245, 241], 'texture': 2},
                {'op': 'rotate', 'deg': 0.9, 'bg': 230},
                {'op': 'blur', 'sigma': 0.4},
                {'op': 'noise', 'sigma': 3}], jpeg=62),
            'scan-severe.pdf': V(731002, 300, [
                {'op': 'paper', 'rgb': [245, 243, 238], 'texture': 3},
                {'op': 'perspective', 'margin': 0.05, 'jitter': 0.035, 'keystone': 0.07, 'bg': [50, 45, 40]},
                {'op': 'shadow', 'strength': 0.45, 'pos': 0.15, 'soft': 0.08},
                {'op': 'gradient', 'strength': 0.2},
                {'op': 'motion_blur', 'length': 6, 'angle': 20},
                {'op': 'noise', 'sigma': 8, 'chroma': 3},
                {'op': 'downsample', 'dpi': 110}], color='rgb', jpeg=16),
        }),
]
