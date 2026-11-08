"""str02: repeat signs in a piano score (16 bars, 3/4, F major, 4 systems).

* mm. 1-4 repeated with NO start-repeat sign (implied return to the beginning), end-repeat at a
  system end;
* start-repeat at a system start (m. 5); back-to-back end+start repeat mid-system (mm. 6|7);
* end+start repeat at a system break (mm. 8|9: ':|.' ends system 2, '.|:' starts system 3);
* plain end-repeat mid-system (m. 10), a double bar (m. 12), and an end-repeat closing the piece."""
from __future__ import annotations

from .common import CC0_NOTE, assemble, mk_part, waltz_lh

CHORDS = ['F', 'C7', 'F', 'C', 'Bb', 'C7', 'Dm', 'C', 'F', 'C7', 'Bb', 'C', 'F', 'Bb', 'C7', 'F']
RH = ("c''4 a' f' | g'4 c'' e'' | f''2 a'4 | g'2. | d''4 f'' d'' | c''4 bes' g' | a'4 d'' f'' | e''2. | "
      "a''4 g''8 f'' e'' f'' | g''4 c'' bes' | d''4 bes' f' | g'2 r4 | c''8 d'' c'' bes' a' c'' | "
      "d''4 f'' bes'' | a''4 g'' e'' | f''2.")


def make():
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((3, 4), (-1, 'major'), [(pn, {'1': RH, '5': waltz_lh(CHORDS, 41, 52, 55)})])
    m = sc.measures
    m[3].right_bar = 'repeat-end'                       # m.4  (system end), implied start at m.1
    m[4].left_bar = 'repeat-start'                      # m.5  (system start)
    m[5].right_bar = 'repeat-end'                       # m.6 :|.|: m.7
    m[6].left_bar = 'repeat-start'
    m[7].right_bar = 'repeat-end'                       # m.8 :|.  // system break // .|: m.9
    m[8].left_bar = 'repeat-start'
    m[9].right_bar = 'repeat-end'                       # m.10
    m[11].right_bar = 'double'                          # m.12
    m[12].left_bar = 'repeat-start'                     # m.13 (system start)
    m[15].right_bar = 'repeat-end'                      # m.16 end of piece
    for n in (5, 9, 13):
        m[n - 1].brk = 'system'
    sc.title = 'Waltz in Repeats'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': 'Waltz in Repeats', 'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 20, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 14\\mm', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #18']}
    return sc, lay, opts


ITEM = dict(
    id='str02-repeat-signs-piano',
    title='Waltz in Repeats - start/end repeat signs in every position (piano)',
    make=make, pages=1, layout='piano', must_not_split=True,
    focus=['repeat-start', 'repeat-end', 'barline-double', 'system-break'],
    expect_counts={'repeat-start': 4, 'repeat-end': 5, 'barline-double': 1, 'system-break': 3},
    structure=('Notated order (do not unroll): ||: implied :|| after m.4 (no start sign at m.1); start repeat m.5 '
               '(system start); end+start repeat between mm.6|7 (one :|.|: glyph); end repeat after m.8 at the end '
               'of system 2 and start repeat at the beginning of system 3 (m.9) - LilyPond splits the combined glyph '
               'across the line break; end repeat after m.10; double bar after m.12; start repeat m.13 (system '
               'start); end repeat after m.16 closes the piece. Played form: 1-4,1-4,5-6,5-6,7-8,7-8,9-10,9-10,11-12,'
               '13-16,13-16.'),
    expected_notes=('One part (Piano) on a grand staff (2 staves, must NOT be split), F major, 3/4. Repeat signs: '
                    'forward repeats on the LEFT barline of mm. 5, 7, 9, 13 (<repeat direction="forward"/>, '
                    'heavy-light); backward repeats on the RIGHT barline of mm. 4, 6, 8, 10, 16 '
                    '(<repeat direction="backward"/>, light-heavy). The repeat at m.1 is implied, so measure 1 has '
                    'NO forward repeat.'),
    notes=('No truth limitations. Repeat barlines appear in the truth once per part (one part here); in the '
           'engraving the repeat dots appear on both staves of the grand staff.'),
    attribution='\n'.join(['"Waltz in Repeats" for piano, composed for this corpus (2026) - CC0 1.0.', '', CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 42001, 'summary': 'flatbed scan, 250 dpi grey, -0.8 deg skew, paper texture, '
                     'faint bleed-through, JPEG q75',
                     'params': dict(dpi=250, mode='gray', texture=3, rotate=-0.8, bleed=0.04, blur=0.4, noise=3,
                                    jpeg=75)},
        'scan-severe.pdf': {'seed': 42002, 'summary': 'phone photo of the page: perspective/keystone, uneven '
                            'lamp light and vignette, motion blur, cream paper, 150 dpi, JPEG q22',
                            'params': dict(dpi=150, mode='rgb', paper_rgb=(243, 236, 214), texture=6, rotate=-3.0,
                                           phone={'margin': 0.06, 'bg': 55, 'jitter': 0.04, 'keystone': 0.07},
                                           blotch=0.3, vignette=0.35, motion_blur={'len': 5, 'angle': 25},
                                           noise=7, jpeg=22)},
    },
)
