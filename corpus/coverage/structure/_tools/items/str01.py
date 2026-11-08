"""str01: double and final bar lines (flute melody, 16 bars, 4 systems).

Seven double bar lines (five mid-system, two at system ends, two consecutive bars closed by
double bars) and two final bar lines (one mid-piece at a system end, one at the end)."""
from __future__ import annotations

from .common import CC0_NOTE, assemble, mk_part

FLUTE = ("c''4 e'' g'' e'' | f''4 d'' c''2 | g'8 a' b' c'' d''4 g' | e''4 d''8 c'' d''2 | "
         "e''4. f''8 g''4 c'' | a'4 b' c''2 | d''8 e'' f'' d'' e''4 c'' | b'4 d'' c''2 | "
         "a''4 g'' f'' e'' | d''2 g'' | c'''4 b'' a'' g'' | f''2. r4 | "
         "e''8 f'' g'' a'' g''4 e'' | f''4 a'' g''2 | c''4 e''8 d'' c''4 b' | c''1")

DOUBLE_AFTER = [2, 4, 6, 10, 11, 12, 14]     # measure numbers closed by a double bar
FINAL_AFTER = [8, 16]


def make():
    fl = mk_part('FL', 'Flute', 'Fl.', 'other', 1, ['treble'])
    sc = assemble((4, 4), (0, 'major'), [(fl, {'1': FLUTE})])
    for n in DOUBLE_AFTER:
        sc.measures[n - 1].right_bar = 'double'
    for n in FINAL_AFTER:
        sc.measures[n - 1].right_bar = 'final'
    for n in (5, 9, 13):
        sc.measures[n - 1].brk = 'system'
    sc.title = 'Sectional Study'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'fl', 'clef': 'treble', 'name': 'Flute', 'voices': [('FL', '1')]}]}]}
    opts = {'header': {'title': 'Sectional Study', 'subtitle': 'double and final bar lines',
                       'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 20, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 12\\mm', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #16']}
    return sc, lay, opts


ITEM = dict(
    id='str01-double-final-barlines',
    title='Sectional Study - double and final bar lines (flute)',
    make=make, pages=1, layout='melody', must_not_split=False,
    focus=['barline-double', 'barline-final', 'system-break'],
    expect_counts={'barline-double': 7, 'barline-final': 2, 'system-break': 3},
    structure=('16 bars in 4 systems of 4. Double bar lines close mm. 2, 4, 6, 10, 11, 12, 14 (mm. 4 and 12 at '
               'system ends, mm. 11 and 12 back to back); final bar lines close m. 8 (mid-piece, end of system 2) '
               'and m. 16. No repeats, no jumps: the piece is played straight through.'),
    expected_notes=('One part (Flute), treble clef, C major, 4/4. Every double bar must be <bar-style>light-light'
                    '</bar-style> and every final bar light-heavy on the right barline of its measure; ordinary '
                    'bar lines need no <barline> element. A final bar line in the middle of the piece does not '
                    'end the piece.'),
    notes=('No truth limitations: all symbols of this item are represented exactly. System breaks are encoded as '
           '<print new-system="yes"/>.'),
    attribution='\n'.join(['"Sectional Study" for flute, composed for this corpus (2026) - CC0 1.0.', '', CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 41001, 'summary': 'office flatbed scan, 300 dpi grey, 0.6 deg skew, light paper '
                     'texture and noise, JPEG q80',
                     'params': dict(dpi=300, mode='gray', texture=2, rotate=0.6, blur=0.3, noise=3, jpeg=80)},
        'scan-severe.pdf': {'seed': 41002, 'summary': 'faded binarised photocopy, 150 dpi (from 300), 4.5 deg skew, '
                            'ink drop-out breaking thin lines, salt & pepper and toner speckles',
                            'params': dict(dpi=300, out_dpi=150, ink_dropout=0.18, rotate=4.5, blur=0.7, noise=9,
                                           binarize=120, binarize_noise=18, saltpepper=0.0015, speckle=120,
                                           format='png1')},
    },
)
