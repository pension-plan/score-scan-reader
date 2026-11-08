"""coverage/notes catalog: items, layout tags, expected conversion results, truth notes and the two
damage variants per item (scan.pdf = typical 200-300 dpi office scan, scan-severe.pdf = heavy
damage); every op's parameters and the seed are copied verbatim into meta.json."""
from . import items as I

ATT = 'Composed for this corpus by the coverage/notes generator (no third-party material).'

STEM_NOTE = ('Every stemmed note carries <stem>: the engraving is forced to exactly that direction (standard '
             'middle-line rule, the extreme note of a chord / beam group / two-note tremolo decides, middle line '
             'goes down; graces up; explicit \\stemUp/\\stemDown passages kept). Whole notes and breves carry no '
             '<stem>.')
BEAM_NOTE = ('<beam> elements reproduce the engraved beams level by level (manual beaming): level 1 joins the whole '
             'group, a secondary level joins neighbours that both carry it; a rest inside a beam carries no <beam> '
             'element but a 16th rest between 16ths keeps the secondary beam continuous (as LilyPond draws it), '
             'so the note after it continues the level; beamlets are forward/backward hooks.')
GRACE_NOTE = ('Grace notes are <grace/> notes without <duration>; slash="yes" for acciaccaturas and \\slashedGrace '
              'notes only (both single notes). The slur LilyPond draws for \\acciaccatura / \\appoggiatura is slur '
              'number 2. Grace notes are excluded from all note-value, stem, beam, flag and ledger counts.')
CUE_NOTE = ('Cue notes are <cue/> notes with <type size="cue"> in their own voice (voice 2, stems up) above the '
            'rests of the real part (voice 1); they are engraved in a LilyPond CueVoice (font size -4) and do not '
            'sound (absent from the MIDI check). The cue instrument names are <words> directions.')
TREM_NOTE = ('Single-note tremolos: <ornaments><tremolo type="single">n</tremolo> with n = strokes drawn on the stem '
             '(beamed eighths: subdivision beams minus the beam). Two-note tremolos: both notes carry the printed '
             'value of the whole tremolo (e.g. two half notes filling a half-note beat) with '
             '<time-modification>2:1</time-modification> and <tremolo type="start|stop">n</tremolo> (n = beams '
             'between them); the repeated sounding notes are NOT unfolded in the truth (standard MusicXML), so the '
             'truth duration of each note is half its printed value.')
LEDGER_NOTE = ('Ledger-line counts are noteheads (main notes) needing >= 1 ledger line; counts_detail gives the '
               'number needing exactly 1..5 lines (staff position from the pitch and clef, cross-checked against '
               'LilyPond\'s NoteHead staff positions).')


def V(seed, dpi, ops, level, color='gray', fmt='jpeg', jpeg=None, passes=1):
    v = {'seed': seed, 'dpi': dpi, 'color': color, 'ops': ops, 'format': fmt, 'level': level}
    if fmt == 'jpeg':
        v['jpeg'] = jpeg
        v['jpeg_passes'] = passes
    return v


def typical(seed, dpi, deg, jpeg, noise=3.0, blur=0.5, paper=(245, 244, 240), texture=2, gradient=0.06,
            color='gray'):
    """typical flatbed/office scan: slight skew, light blur, sensor noise, JPEG"""
    return V(seed, dpi, [
        {'op': 'paper', 'rgb': list(paper), 'texture': texture},
        {'op': 'rotate', 'deg': deg, 'bg': [232, 232, 232]},
        {'op': 'gradient', 'strength': gradient},
        {'op': 'blur', 'sigma': blur},
        {'op': 'noise', 'sigma': noise}], 'typical', color=color, jpeg=jpeg)


SEVERE = {
    'photocopy-thick': lambda s: V(s, 200, [
        {'op': 'ink_weight', 'px': 1},
        {'op': 'paper', 'rgb': [250, 250, 250]},
        {'op': 'rotate', 'deg': 2.4, 'bg': 255},
        {'op': 'speckle', 'per_mpx': 70},
        {'op': 'binarize', 'threshold': 178, 'pre_blur': 1.0, 'noise': 22},
        {'op': 'saltpepper', 'amount': 0.002}], 'severe', fmt='png1'),
    'low-dpi-jpeg': lambda s: V(s, 300, [
        {'op': 'paper', 'rgb': [240, 238, 230], 'texture': 4},
        {'op': 'rotate', 'deg': -3.1, 'bg': 225},
        {'op': 'blur', 'sigma': 1.0},
        {'op': 'noise', 'sigma': 7},
        {'op': 'downsample', 'dpi': 100}], 'severe', jpeg=18),
    'phone-capture': lambda s: V(s, 200, [
        {'op': 'paper', 'rgb': [244, 241, 232], 'texture': 3},
        {'op': 'perspective', 'margin': 0.05, 'jitter': 0.03, 'keystone': 0.06, 'bg': [60, 52, 45]},
        {'op': 'shadow', 'strength': 0.4, 'pos': 0.2, 'soft': 0.07},
        {'op': 'vignette', 'strength': 0.3},
        {'op': 'motion_blur', 'length': 5, 'angle': 15},
        {'op': 'noise', 'sigma': 7, 'chroma': 2}], 'severe', color='rgb', jpeg=20),
    'faded-foxed': lambda s: V(s, 300, [
        {'op': 'ink_dropout', 'amount': 0.35},
        {'op': 'paper', 'rgb': [232, 218, 180], 'texture': 7, 'bleed': {'strength': 0.2}, 'ink_var': 35},
        {'op': 'foxing', 'n': 140, 'strength': 0.6},
        {'op': 'rotate', 'deg': 1.8, 'bg': [200, 200, 200]},
        {'op': 'blur', 'sigma': 0.9},
        {'op': 'noise', 'sigma': 6, 'chroma': 2}], 'severe', color='rgb', jpeg=25),
    'photocopy-thin': lambda s: V(s, 200, [
        {'op': 'paper', 'rgb': [252, 252, 252]},
        {'op': 'rotate', 'deg': -1.6, 'bg': 255},
        {'op': 'speckle', 'per_mpx': 90},
        {'op': 'binarize', 'threshold': 72, 'pre_blur': 0.8, 'noise': 18}], 'severe', fmt='png1'),
    'halftone-skew': lambda s: V(s, 300, [
        {'op': 'paper', 'rgb': [242, 240, 234], 'texture': 3},
        {'op': 'halftone', 'lpi': 85, 'angle': 45, 'supersample': 2},
        {'op': 'rotate', 'deg': 4.0, 'bg': 40},
        {'op': 'blur', 'sigma': 0.8},
        {'op': 'noise', 'sigma': 6}], 'severe', jpeg=30),
    'book-curl': lambda s: V(s, 200, [
        {'op': 'paper', 'rgb': [240, 236, 224], 'texture': 4},
        {'op': 'curl', 'side': 'right', 'amp': 40, 'width': 0.35},
        {'op': 'gutter', 'side': 'right', 'width': 0.1, 'dark': 0.6},
        {'op': 'rotate', 'deg': 2.0, 'bg': [210, 210, 210]},
        {'op': 'gradient', 'strength': 0.25},
        {'op': 'blur', 'sigma': 0.8},
        {'op': 'noise', 'sigma': 6, 'chroma': 2}], 'severe', color='rgb', jpeg=25),
    'coffee-stained': lambda s: V(s, 300, [
        {'op': 'ink_dropout', 'amount': 0.2},
        {'op': 'paper', 'rgb': [230, 214, 175], 'texture': 8, 'bleed': {'strength': 0.15}},
        {'op': 'coffee', 'n': 2, 'radius_mm': 40, 'strength': 0.6},
        {'op': 'foxing', 'n': 150, 'strength': 0.6},
        {'op': 'rotate', 'deg': -2.2, 'bg': [190, 190, 190]},
        {'op': 'blur', 'sigma': 1.0},
        {'op': 'noise', 'sigma': 5, 'chroma': 2}], 'severe', color='rgb', jpeg=22),
    'heavy-skew-noise': lambda s: V(s, 150, [
        {'op': 'paper', 'rgb': [238, 238, 236], 'texture': 3},
        {'op': 'rotate', 'deg': 6.0, 'bg': 50},
        {'op': 'blur', 'sigma': 1.2},
        {'op': 'noise', 'sigma': 12},
        {'op': 'saltpepper', 'amount': 0.004}], 'severe', jpeg=15),
    'recompressed-150': lambda s: V(s, 150, [
        {'op': 'paper', 'rgb': [244, 243, 238], 'texture': 3},
        {'op': 'rotate', 'deg': 3.0, 'bg': 220},
        {'op': 'blur', 'sigma': 0.9},
        {'op': 'noise', 'sigma': 8}], 'severe', jpeg=20, passes=3),
}


def variants(n, dpi, deg, jpeg, severe, **kw):
    base = 960000 + n * 100
    sev = SEVERE[severe](base + 2)
    sev['recipe'] = severe
    return {'scan.pdf': typical(base + 1, dpi, deg, jpeg, **kw), 'scan-severe.pdf': sev}


ITEMS = [
    dict(id='nt01-note-values', title='Note Values (violin)', make=I.mk_nt01, layout='melody', pages=1,
         description='Every note value from breve to 64th on one treble staff: 4/2 bars of breves, wholes and '
                     'halves, then 4/4 bars of quarters, eighths, 16ths, 32nds and 64ths, each value both beamed and '
                     'flagged and with stems up and down.',
         focus=['note-breve', 'note-whole', 'note-half', 'note-quarter', 'note-8th', 'note-16th', 'note-32nd',
                'note-64th', 'beam', 'flag', 'stem-up', 'stem-down'],
         min_counts={'note-breve': 3, 'note-64th': 30, 'note-32nd': 20, 'flag': 20},
         expected=dict(must_not_split=False,
                       notes='One part (Violin), 15 bars: 4/2 (bars 1-4), 4/4 (5-13), 4/2 (14-15). Breves in bars '
                             '1, 4, 15. Each 4/4 bar mixes beamed groups and unbeamed (flagged) notes of the same '
                             'value; the 64th bars hold groups of 16 and 8 beamed 64ths plus four flagged 64ths.'),
         notes=[STEM_NOTE, BEAM_NOTE],
         variants=variants(1, 300, 0.7, 60, 'photocopy-thick')),
    dict(id='nt02-dots', title='Dotted Rhythms (oboe)', make=I.mk_nt02, layout='melody', pages=1,
         description='Single and double dots on whole, half, quarter, eighth, 16th and 32nd notes; dotted '
                     'values beamed with their complements (hooks), dotted two-note chords.',
         focus=['dot', 'double-dot', 'note-whole', 'note-half', 'note-quarter', 'note-8th', 'note-16th',
                'note-32nd', 'note-64th', 'beam', 'chord'],
         min_counts={'dot': 20, 'double-dot': 8},
         expected=dict(must_not_split=False,
                       notes='One part (Oboe), 16 bars in 3/2, 4/4, 6/8, 4/4. Dotted whole (bar 1), double-dotted '
                             'half (3), double-dotted quarters (6, 14), double-dotted eighths + 32nd (8), dotted '
                             '16th + 32nd (8, 9), dotted 32nd + 64th (9), double-dotted 16th + 64th (14), dotted '
                             'chords (10, 11). Every dot belongs to the note it follows; no rests.'),
         notes=[STEM_NOTE, BEAM_NOTE, 'dot / double-dot count noteheads (each head of a dotted chord has a dot).'],
         variants=variants(2, 300, -1.1, 55, 'low-dpi-jpeg')),
    dict(id='nt03-chords', title='Chord Study (piano)', make=I.mk_nt03, layout='piano', pages=1,
         description='Chords of 2, 3, 4, 5 and 6 notes in both hands: close and open positions, seconds '
                     '(displaced noteheads), accidentals inside chords, beamed eighth- and 16th-note chords, '
                     'dotted and whole-note chords, chords with ledger lines.',
         focus=['chord', 'note-whole', 'note-half', 'note-quarter', 'note-8th', 'note-16th', 'beam', 'stem-up',
                'stem-down', 'acc-sharp', 'acc-flat', 'acc-natural'],
         min_counts={'chord': 40},
         expected=dict(must_not_split=True,
                       notes='ONE part (Piano) on a grand staff (2 staves), 10 bars of 4/4; every simultaneity is a '
                             'chord on one stem (must stay a chord, not separate voices or parts). Chord sizes per '
                             'counts_detail; 6-note chords in bars 2 and 9 (RH) and bar 9 (LH).'),
         notes=[STEM_NOTE, BEAM_NOTE, 'chord counts chord events (one stem); chord tones are counted as noteheads '
                'in note-<value>.'],
         variants=variants(3, 300, 0.4, 65, 'phone-capture')),
    dict(id='nt04-beams', title='Beam Groups (flute)', make=I.mk_nt04, layout='melody', pages=1,
         description='Beams of 2, 3, 4, 6 and 8 eighths, 4/6/8 16ths, 32nds; beamed groups in 2/4, 3/4, 6/8 and '
                     '4/4; mixed values with forward/backward beamlets; secondary beams broken inside a group; '
                     'beams across eighth and 16th rests; beamed chords.',
         focus=['beam', 'note-8th', 'note-16th', 'note-32nd', 'stem-up', 'stem-down'],
         min_counts={'beam': 35},
         expected=dict(must_not_split=False,
                       notes='One part (Flute), 16 bars, meters 2/4, 3/4, 6/8, 4/4, 3/4, 4/4. Beam groups exactly '
                             'as in the truth <beam> elements: e.g. bar 9 = two groups of eight 16ths whose '
                             'secondary beam breaks after the 4th note; rests inside beams in bars 7, 11, 14.'),
         notes=[STEM_NOTE, BEAM_NOTE],
         variants=variants(4, 200, 1.3, 70, 'faded-foxed')),
    dict(id='nt05-flags-stems', title='Flags and Stems (violin)', make=I.mk_nt05, layout='melody', pages=1,
         description='Unbeamed eighths, 16ths, 32nds and 64ths with flags on up-stems and down-stems; passages '
                     'with stems forced against the middle-line rule (\\stemUp on high notes, \\stemDown on low '
                     'notes, both directions on the middle line).',
         focus=['flag', 'stem-up', 'stem-down', 'note-8th', 'note-16th', 'note-32nd', 'note-64th'],
         min_counts={'flag': 60},
         expected=dict(must_not_split=False,
                       notes='One part (Violin), 14 bars of 3/4, no beams at all: every short note has its own '
                             'flag. Stem directions as in <stem> (bars 8-12 are forced).'),
         notes=[STEM_NOTE],
         variants=variants(5, 300, -0.5, 60, 'photocopy-thin')),
    dict(id='nt06-ledger-lines', title='Ledger Lines (piano)', make=I.mk_nt06, layout='piano', pages=1,
         description='Notes and chords needing 1 to 5 ledger lines above and below the treble and the bass '
                     'staff: single notes, beamed scales, chords and whole notes, C1 to C7.',
         focus=['ledger-above', 'ledger-below', 'chord', 'note-whole', 'note-half', 'note-quarter', 'note-8th',
                'note-16th'],
         min_counts={'ledger-above': 35, 'ledger-below': 35},
         expected=dict(must_not_split=True,
                       notes='ONE part (Piano), grand staff, 10 bars of 4/4, no clef changes or ottavas: the '
                             'extreme pitches (C7, B6 in the right hand; C1, D1 in the left hand; B2 in the right '
                             'hand, D5/E5 in the left hand) must be read from 5 ledger lines.'),
         notes=[STEM_NOTE, BEAM_NOTE, LEDGER_NOTE],
         variants=variants(6, 300, 0.9, 55, 'halftone-skew')),
    dict(id='nt07-grace-notes', title='Grace Notes (flute)', make=I.mk_nt07, layout='melody', pages=1,
         description='Acciaccaturas (slashed, slurred), appoggiaturas (eighth, quarter and 16th, slurred), plain '
                     'and slashed graces without slur, beamed grace groups of 2-6 16ths and of 32nds, a grace '
                     'chord, graces with accidentals, graces at the start of bars and of the piece.',
         focus=['grace', 'grace-slash', 'slur', 'note-quarter', 'note-half'],
         min_counts={'grace': 40, 'grace-slash': 12},
         expected=dict(must_not_split=False,
                       notes='One part (Flute), 10 bars of 4/4. Grace notes take no time: every bar holds exactly '
                             '4 beats of main notes. Slashed: acciaccaturas and \\slashedGrace singles.'),
         notes=[STEM_NOTE, GRACE_NOTE],
         variants=variants(7, 250, 1.0, 60, 'book-curl')),
    dict(id='nt08-cue-notes', title='Cue Notes (flute part)', make=I.mk_nt08, layout='melody', pages=1,
         description='A flute part with small cue notes (oboe / violin cues) above whole-bar and half-bar rests: '
                     'beamed cue eighths and 16ths, dotted cue note, cue chord, cue instrument names.',
         focus=['cue-note', 'rest-whole-bar', 'text-expression'],
         min_counts={'cue-note': 20},
         expected=dict(must_not_split=True,
                       notes='ONE part (Flute), 10 bars of 4/4, one staff. The small notes are cues (another '
                             'instrument): a correct conversion marks them <cue/> or leaves them out; they must not '
                             'become sounding flute notes and must not create a second part. The real flute music '
                             'is voice 1 (rests under the cues in bars 3-5, 7-9).'),
         notes=[STEM_NOTE, BEAM_NOTE, CUE_NOTE],
         variants=variants(8, 300, -0.8, 65, 'coffee-stained')),
    dict(id='nt09-tremolos', title='Tremolos (piano)', make=I.mk_nt09, layout='piano', pages=1,
         description='Single-note tremolos with 1, 2 and 3 strokes on quarters, halves, wholes, beamed eighths and '
                     'chords; two-note (alternating) tremolos between notes, octaves and chords filling half and '
                     'whole bars.',
         focus=['tremolo', 'note-whole', 'note-half', 'note-quarter', 'note-8th', 'chord'],
         min_counts={'tremolo': 30},
         expected=dict(must_not_split=True,
                       notes='ONE part (Piano), grand staff, 9 bars of 4/4. Tremolo strokes are not beams of '
                             'separate notes: c\'\'4:16 is ONE quarter note with 2 strokes; a two-note tremolo is '
                             'two notes of the printed value (e.g. two half notes) occupying together one half note.'),
         notes=[STEM_NOTE, BEAM_NOTE, TREM_NOTE],
         variants=variants(9, 200, 0.6, 60, 'heavy-skew-noise')),
    dict(id='nt10-piano-etude', title='Etude in C (piano)', make=I.mk_nt10, layout='piano', pages=1,
         description='A piano etude combining all note symbols in context: beamed 8ths/16ths/32nds, dotted and '
                     'double-dotted values, chords of 2-5 notes, grace notes, ledger lines, flags, both stem '
                     'directions, a beam across a rest.',
         focus=['note-half', 'note-quarter', 'note-8th', 'note-16th', 'note-32nd', 'dot', 'double-dot', 'chord',
                'beam', 'flag', 'grace', 'ledger-above', 'ledger-below'],
         min_counts={'chord': 15},
         expected=dict(must_not_split=True,
                       notes='ONE part (Piano), grand staff, 10 bars of 4/4, one voice per staff.'),
         notes=[STEM_NOTE, BEAM_NOTE, GRACE_NOTE],
         variants=variants(10, 300, -1.4, 50, 'recompressed-150')),
]

for _it in ITEMS:
    _it['attribution'] = ATT
