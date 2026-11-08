"""str04: Segno / To Coda / D.S. al Coda / Coda (violin, 16 bars, 4/4, B-flat major, 4 systems)."""
from __future__ import annotations

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, mk_part

VIOLIN = ("bes'4 d'' f'' d'' | c''2 r2 | f''4. es''8 d''4 bes' | c''4 d''8 es'' f''2 | "
          "g''4 f'' es'' d'' | c''4 bes' a' c'' | d''4 f'' es'' c'' | bes'1 | "
          "d''4 d''8 es'' f''4 bes'' | a''4 g''8 f'' es''4 c'' | f''4 es'' d'' c'' | bes'2 f'2 | "
          "bes'4 c''8 d'' es''4 f'' | g''4 a''8 bes'' a''4 f'' | d''4 c'' es'' a' | bes'1")


def make():
    vn = mk_part('VN', 'Violin', 'Vl.', 'other', 1, ['treble'])
    sc = assemble((4, 4), (-2, 'major'), [(vn, {'1': VIOLIN})])
    m = sc.measures
    add_mark(sc, 0, 'tempo', text='Moderato', unit='quarter', bpm=96)
    m[1].right_bar = 'double'                                   # end of the introduction
    add_mark(sc, 2, 'segno')                                    # m.3
    add_end_mark(sc, 7, 'To Coda', style='italic', coda_sign=True, sound={'tocoda': 'coda'})   # after m.8
    add_end_mark(sc, 11, 'D.S. al Coda', style='bold-italic', sound={'dalsegno': 'segno'})   # after m.12
    m[11].right_bar = 'double'
    add_mark(sc, 12, 'coda')                                    # m.13
    m[15].right_bar = 'final'
    for n in (5, 9, 13):
        m[n - 1].brk = 'system'
    sc.title = 'Round Trip'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'vn', 'clef': 'treble', 'name': 'Violin', 'voices': [('VN', '1')]}]}]}
    opts = {'header': {'title': 'Round Trip', 'subtitle': 'Segno, To Coda, D.S. al Coda',
                       'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 20, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 14\\mm', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #18']}
    return sc, lay, opts


ITEM = dict(
    id='str04-segno-coda-ds',
    title='Round Trip - Segno, To Coda, D.S. al Coda, Coda (violin)',
    make=make, pages=1, layout='melody', must_not_split=False,
    focus=['segno', 'coda', 'x-to-coda', 'ds', 'barline-double', 'barline-final'],
    expect_counts={'segno': 1, 'coda': 2, 'x-to-coda': 1, 'ds': 1, 'barline-double': 2, 'barline-final': 1},
    structure=('Notated order (do not unroll): intro mm.1-2 (double bar), Segno sign at m.3, "To Coda" + coda sign '
               'after m.8, "D.S. al Coda" after m.12 (double bar), Coda sign at m.13 (start of the last system), '
               'final bar after m.16. Played form: 1-12, 3-8, 13-16.'),
    expected_notes=('One part (Violin), B-flat major, 4/4. Jumps as directions with playback: <segno/> + '
                    '<sound segno="segno"/> at m.3; words "To Coda" + <coda/> + <sound tocoda="coda"/> at the end of '
                    'm.8; words "D.S. al Coda" + <sound dalsegno="segno"/> at the end of m.12; <coda/> + '
                    '<sound coda="coda"/> at m.13. Tempo "Moderato" with metronome quarter = 96.'),
    notes=('Truth limitation: the coda glyph printed after the words "To Coda" is encoded as a second '
           'direction-type <coda/> in the same <direction> as the words, so counts.coda = 2 (that glyph + the Coda '
           'sign at m.13). Segno/coda are directions (not <barline> children).'),
    attribution='\n'.join(['"Round Trip" for violin, composed for this corpus (2026) - CC0 1.0.', '', CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 44001, 'summary': 'flatbed scan, 200 dpi grey, -1.2 deg skew, paper texture, noise, '
                     'JPEG q70',
                     'params': dict(dpi=200, mode='gray', texture=3, rotate=-1.2, blur=0.4, noise=4, jpeg=70)},
        'scan-severe.pdf': {'seed': 44002, 'summary': 'old yellowed copy, 150 dpi RGB: 7 deg skew, strong '
                            'bleed-through, foxing and a coffee ring, focus blur, JPEG q20',
                            'params': dict(dpi=150, mode='rgb', paper_rgb=(232, 219, 186), texture=6, rotate=7.0,
                                           bleed=0.15, foxing={'n': 60}, coffee={'n': 1, 'r': 0.1, 'strength': 0.9},
                                           blur=1.3, noise=8, jpeg=20)},
    },
)
