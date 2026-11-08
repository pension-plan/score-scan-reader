"""L4: Nocturne in E-flat for piano (CC0): left-hand arpeggios whose upper notes are printed on
the treble staff with beams crossing between the staves, a right-hand arpeggio that dips onto the
bass staff, pedal marks every bar, Segno / To Coda / D.S. al Coda / Coda, tempo with a dotted-quarter
metronome mark and lots of expression text."""
from __future__ import annotations

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, from_midi_spelled, lyp, mk_part
from lsynth.harmonize import chord_tones
from lsynth.model import STEP_PC

# one chord per 6/8 bar
CHORDS = (['Eb', 'Eb'] +                                                  # intro
          ['Eb', 'Ab', 'Bb7', 'Eb', 'Cm', 'Fm', 'Bb7', 'Eb'] +                # A (segno)
          ['Cm', 'G7', 'Cm', 'Ab', 'Fm', 'Bb7', 'Eb/G', 'Bb7'] +             # B
          ['Fm', 'Bb7', 'Eb', 'Ab/Eb', 'Eb'])                                # Coda
RH = [
    "r2.", "r4. r8 r8 bes'8",
    # A
    "bes'4.\\mp^\"cantabile\" g''8( f'' ees'')", "c''4.( ees''8 des'' c'')", "d''4 f''8 aes''4 g''8",
    "g''4.~ g''4 r8", "ees''4.^\"cresc.\" c''8( d'' ees'')", "f''4. aes''8( g'' f'')",
    "f''4^\"dim.\" d''8 bes'4 aes'8", "ees''4.~ ees''4 r8",
    # B
    "g''4.\\mf^\"espressivo\" g''8( aes'' g'')", "f''4. d''8( ees'' f'')", "ees''4.\\< c''4.",
    "c''4.\\!\\f ees''8( f'' ees'')", "aes''4.^\"dim.\" f''8( ees'' c'')", "d''4. f''8( aes'' f'')",
    "g''16[\\p( ees'' bes' g' ees' \\st2 bes] g[ bes \\st0 ees' g' bes' ees'')]", "f''4.( d''8 c'' bes')",
    # Coda
    "aes''4.\\pp f''8( ees'' c'')", "d''4. f''8( ees'' d'')", "ees''4.~^\"rit.\" ees''4.",
    "c''4.( ees''4.)", "<g' bes' ees''>2.\\fermata^\"morendo\"",
]


def arpeggio(sym):
    """six eighths: bass + chord tones; notes >= C4 printed on the treble staff (\\st1)."""
    tones, bass, q = chord_tones(sym)
    pcs = [(STEP_PC[s] + a) % 12 for s, a in tones]
    root_pc = pcs[0]
    bass_pc = (STEP_PC[bass[0]] + bass[1]) % 12
    if bass_pc != root_pc:   # slash chord: bass, then 5 ascending chord tones from bass + 5
        b = next(m for m in range(31, 47) if m % 12 == bass_pc)
        ups = [m for m in range(b + 5, b + 40) if m % 12 in pcs][:5]
        seq = [b] + ups
    else:
        r = next(m for m in range(33, 45) if m % 12 == root_pc)
        third = r + (3 if q in ('m', 'm7', 'dim') else 4)
        if q == '7':
            seq = [r, r + 7, r + 12, third + 12, r + 22, third + 24]
        else:
            seq = [r, r + 7, r + 12, third + 12, r + 19, r + 24]
    out = []
    cur = 2
    for k, m in enumerate(seq):
        want = 1 if m >= 60 else 2
        t = ''
        if want != cur:
            t = '\\st1 ' if want == 1 else '\\st0 '
            cur = want
        beam = '[' if k in (0, 3) else (']' if k in (2, 5) else '')
        out.append(f'{t}{lyp(from_midi_spelled(m, tones))}8{beam}')
    s = ' '.join(out)
    if cur == 1:
        s += ' \\st0'
    return s


def lh_bar(i, sym):
    if i == 16:                         # B7: RH dips into the bass staff; LH holds the bass
        return "g,2.\\sustainOff\\sustainOn"
    if i == len(CHORDS) - 1:            # final chord
        return "<ees, bes,>4.\\sustainOff\\sustainOn\\fermata r4.\\sustainOff"
    s = arpeggio(sym)
    toks = s.split(' ')
    for k, t in enumerate(toks):
        if not t.startswith('\\'):
            toks[k] = t + ('\\sustainOn' if i == 0 else '\\sustainOff\\sustainOn')
            if i == 0:
                toks[k] += '\\p_"dolce"'
            break
    return ' '.join(toks)


def make():
    assert len(CHORDS) == len(RH) == 23
    lh = ' | '.join(lh_bar(i, c) for i, c in enumerate(CHORDS))
    p = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((6, 8), (-3, 'major'), [(p, {'1': ' | '.join(RH), '5': lh})])
    add_mark(sc, 0, 'tempo', text='Andante cantabile', unit='quarter', dots=1, bpm=52)
    add_mark(sc, 2, 'segno')
    add_end_mark(sc, 7, 'To Coda', style='italic', coda_sign=True, sound={'tocoda': 'coda'})
    add_end_mark(sc, 17, 'D.S. al Coda', style='bold-italic', sound={'dalsegno': 'segno'})
    sc.measures[17].right_bar = 'double'
    add_mark(sc, 18, 'coda')
    add_mark(sc, 18, 'tempo', text='Tranquillo')
    sc.measures[-1].right_bar = 'final'
    sc.measures[1].right_bar = 'double'
    # systems: 1-4 | 5-8 | 9-12 | 13-16 || page 2: 17-18 | 19-23 (coda)
    for i in (4, 8, 12, 18):
        sc.measures[i].brk = 'system'
    sc.measures[16].brk = 'page'
    sc.title = 'Nocturne in E-flat'
    sc.composer = 'Layout-challenge corpus (2026), CC0'
    sc.rights = 'Dedicated to the public domain (CC0 1.0)'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'Nocturne in E-flat'},
                  {'page': 1, 'type': 'subtitle', 'text': 'for piano'},
                  {'page': 1, 'type': 'composer', 'text': 'Layout-challenge corpus (2026)'},
                  {'page': 1, 'type': 'rights', 'text': 'Dedicated to the public domain (CC0 1.0)'},
                  {'page': 2, 'type': 'page number', 'text': '2'}]
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'up', 'clef': 'treble', 'voices': [('P', '1')]},
        {'id': 'down', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': 'Nocturne in E-flat', 'subtitle': 'for piano',
                       'composer': 'Layout-challenge corpus (2026)',
                       'copyright': 'Dedicated to the public domain (CC0 1.0)'},
            'staff_size': 20, 'paper': 'letter', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'paper_extra': ['indent = 14\\mm', 'ragged-bottom = ##t',
                            'system-system-spacing.basic-distance = #16'],
            'layout_extra': []}
    return sc, lay, opts


ITEM = dict(
    id='nocturne-cross-staff-pedal-ds-coda',
    title='Nocturne in E-flat - cross-staff beams, pedal marks, Segno / To Coda / D.S. al Coda',
    make=make, pages=2,
    edge_cases=['cross_staff_beams', 'cross_staff_notes_lh_to_treble', 'cross_staff_notes_rh_to_bass',
                'pedal_marks', 'segno', 'to_coda', 'ds_al_coda', 'coda', 'tempo_text', 'dotted_metronome_mark',
                'expression_text', 'dynamics_text', 'hairpin', 'accidentals_cross_staff', 'piano_grand_staff',
                'must_not_split', 'double_barline', 'ties', 'slurs', 'fermata'],
    must_not_split=True,
    expected_notes=('One part: Piano (2 staves) - must NOT be split even though left-hand notes appear on the '
                    'treble staff (beams cross between the staves) and right-hand notes on the bass staff. '
                    'Cross-staff notes keep their voice (LH voice 5 / RH voice 1) and carry the staff they are '
                    'printed on (<staff>). Notated order: segno at m.3, "To Coda" after m.8, "D.S. al Coda" after '
                    'm.18, coda from m.19 - do not unroll. "Ped." / "*" signs, "cantabile", "cresc.", "dim.", '
                    '"rit.", "morendo", tempo text are not notes or lyrics.'),
    truth_limitations=('Beaming is not encoded (no <beam>); the cross-staff beams are only visible in the engraving. '
                       'Pedal is encoded as <pedal type="stop"/> + <pedal type="start"/> at each change (LilyPond '
                       'prints "*Ped."). Stem directions are not encoded for single-voice staves.'),
    layout_desc='US letter, staff size 20, 6 systems on 2 pages; page 2 begins with the bars before the D.S.',
    license='CC0-1.0 (composition, engraving, scans)',
    source='self-authored (layout-challenge corpus)',
    attribution='\n'.join(['Nocturne in E-flat, composed for this corpus - CC0 1.0.', '', CC0_NOTE]),
)
