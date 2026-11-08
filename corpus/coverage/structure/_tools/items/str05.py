"""str05: Fine and D.C. al Fine in a Minuet and Trio for piano (16 bars, 3/4, G major, 4 systems).

Menuet: ||: mm.1-4 :|| mm.5-8 "Fine" + final bar (mid-piece).  Trio: ||: mm.9-12 :||: mm.13-16 :||
"D.C. al Fine" (the combined end/start repeat falls on the system break 12|13)."""
from __future__ import annotations

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, mk_part, waltz_lh

CHORDS = ['G', 'D7', 'G', 'D', 'G', 'C', 'D7', 'G', 'C', 'G', 'Am', 'D', 'G', 'C', 'D7', 'G']
RH = ("d''4 g' a'8 b' | c''4 a' fis' | g'8 a' b' c'' d''4 | a'2. | b'4 d'' g'' | e''4 c''8 d'' e'' c'' | "
      "a'4 fis'' a'' | g''2. | e''4 g'' e'' | d''4 b'8 c'' d'' b' | c''4 a' c'' | fis'2. | "
      "g'4 b' d'' | e''8 d'' c'' b' a' g' | fis'4 a' c'' | b'2.")


def make():
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((3, 4), (1, 'major'), [(pn, {'1': RH, '5': waltz_lh(CHORDS, 43, 54, 55)})])
    m = sc.measures
    add_mark(sc, 0, 'tempo', text='Tempo di Minuetto')
    m[3].right_bar = 'repeat-end'                         # m.4 (implied start)
    m[7].right_bar = 'final'                              # m.8
    add_end_mark(sc, 7, 'Fine', style='bold-italic', sound={'fine': 'yes'})
    m[8].left_bar = 'repeat-start'                        # m.9
    add_mark(sc, 8, 'words', text='Trio', style='bold')
    m[11].right_bar = 'repeat-end'                        # m.12 :|.|: m.13 at the system break
    m[12].left_bar = 'repeat-start'
    m[15].right_bar = 'repeat-end'                        # m.16
    add_end_mark(sc, 15, 'D.C. al Fine', style='bold-italic', sound={'dacapo': 'yes'})
    for n in (5, 9, 13):
        m[n - 1].brk = 'system'
    sc.title = 'Minuet and Trio'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': 'Minuet and Trio', 'subtitle': 'Fine and D.C. al Fine',
                       'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 20, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 14\\mm', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #18']}
    return sc, lay, opts


ITEM = dict(
    id='str05-fine-dc-al-fine-piano',
    title='Minuet and Trio - Fine with a mid-piece final bar, D.C. al Fine (piano)',
    make=make, pages=1, layout='piano', must_not_split=True,
    focus=['fine', 'dc', 'barline-final', 'repeat-start', 'repeat-end'],
    expect_counts={'fine': 1, 'dc': 1, 'barline-final': 1, 'repeat-start': 2, 'repeat-end': 3,
                   'system-break': 3},
    structure=('Notated order (do not unroll): Menuet ||: mm.1-4 :|| (implied start) mm.5-8, "Fine" + final bar '
               'after m.8; Trio (heading) ||: mm.9-12 :||: mm.13-16 :|| (the combined repeat sits on the system break '
               '12|13), "D.C. al Fine" after m.16. Played form: 1-4,1-4,5-8,9-12,9-12,13-16,13-16,1-8 (repeats are '
               'customarily not taken after D.C.).'),
    expected_notes=('One part (Piano), grand staff (must NOT be split), G major, 3/4. "Fine" = words + <sound '
                    'fine="yes"/> at the end of m.8, whose right barline is light-heavy (a final bar in the middle of '
                    'the piece); "D.C. al Fine" = words + <sound dacapo="yes"/> at the end of m.16. "Trio" is a '
                    'section heading (text), "Tempo di Minuetto" a tempo text without metronome mark.'),
    notes=('Truth limitation: whether repeats are taken after the D.C. is a performance convention and is not '
           'encoded. Fine/D.C. are words directions with <sound> playback attributes (the only MusicXML encoding).'),
    attribution='\n'.join(['"Minuet and Trio" for piano, composed for this corpus (2026) - CC0 1.0.', '', CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 45001, 'summary': 'flatbed scan, 300 dpi grey, 0.4 deg skew, mild gradient lighting, '
                     'noise, JPEG q85',
                     'params': dict(dpi=300, mode='gray', texture=2, rotate=0.4, gradient=0.05, blur=0.3, noise=3,
                                    jpeg=85)},
        'scan-severe.pdf': {'seed': 45002, 'summary': 'page fed upside down (180 deg) through a fax-like copier: '
                            '100 dpi (from 300) binarised, 3 deg skew, broken thin lines, speckles',
                            'params': dict(dpi=300, out_dpi=100, rotate=3.0, page_rotate={0: 180},
                                           ink_dropout=0.12, blur=0.8, noise=10, binarize=115, binarize_noise=15,
                                           speckle=100, format='png1')},
    },
)
