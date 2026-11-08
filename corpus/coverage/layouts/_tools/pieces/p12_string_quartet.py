"""string-quartet: Violin I, Violin II, Viola (alto clef), Violoncello on four bracketed staves."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

VN1 = ("e''4(\\f g'' e'') | d''4-. f''-. d''-. | c''8( d'' e'' f'' g''4) | a''4-> g''-> f''-> | "
       "e''2 g''4 | c'''4( b'' a'') | f''4.( e''8 d''4) | c''2 r4 | "
       "g''4\\p^\"dolce\" a''8( g'' f'' e'') | d''4( g''2) | <c'' e''>4\\< <b' d''> <b' f''>\\! | <e' c''>2.\\fermata")
VN2 = ("c''4(\\f e'' c'') | b'4-. d''-. b'-. | g'4( c'' e'') | f''4-> e''-> d''-> | "
       "c''2 e''4 | a'4( g' fis') | a'4.( g'8 f'4) | e'2 r4 | "
       "e''4\\p f''8( e'' d'' c'') | b'4( d''2) | g'4\\< g' g'\\! | g'2.\\fermata")
VA = ("g'4\\f g' g' | g'4-. g'-. g'-. | e'4 g' c'' | c''4-> c''-> b'-> | "
      "g'2 c''4 | e'4 e' e' | d'4 d' b | c'2 r4 | "
      "c'4\\p^\"pizz.\" r4 c'4 | g4 r4 g4 | e'4^\"arco\"\\< f' d'\\! | e'2.\\fermata")
VC = ("c4\\f c c | g,4-. g,-. g,-. | c4 e g | f4-> g-> g,-> | "
      "c2 c4 | a,4 a, a, | d4 g g, | c2 r4 | "
      "c4\\p^\"pizz.\" r4 c4 | g,4 r4 g,4 | c4^\"arco\"\\< g g,\\! | c2.\\fermata")


def make():
    parts = [mk_part('V1', 'Violin I', 'Vn. I', 'other', 1, ['treble']),
             mk_part('V2', 'Violin II', 'Vn. II', 'other', 1, ['treble']),
             mk_part('VA', 'Viola', 'Va.', 'other', 1, ['alto']),
             mk_part('VC', 'Violoncello', 'Vc.', 'other', 1, ['bass'])]
    src = {'V1': VN1, 'V2': VN2, 'VA': VA, 'VC': VC}
    sc = assemble((3, 4), (0, 'major'), [(p, {'1': src[p.id]}) for p in parts])
    add_mark(sc, 0, 'tempo', text='Tempo di Minuetto', unit='quarter', bpm=126)
    sc.measures[7].right_bar = 'repeat-end'
    breaks(sc, systems=(4, 8))
    sc.groups = [{'first': 'V1', 'last': 'VC', 'symbol': 'bracket'}]
    hdr = header(sc, 'Minuet', 'for string quartet')
    staves = []
    for pid, clef, nm, sh in (('V1', 'treble', 'Violin I', 'Vn. I'), ('V2', 'treble', 'Violin II', 'Vn. II'),
                              ('VA', 'alto', 'Viola', 'Va.'), ('VC', 'bass', 'Violoncello', 'Vc.')):
        staves.append({'id': pid.lower(), 'clef': clef, 'name': nm, 'short': sh, 'voices': [(pid, '1')]})
    lay = {'groups': [{'type': 'StaffGroup', 'staves': staves}]}
    return sc, lay, opts(hdr, 18, extra_paper=['indent = 20\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #16'])


ITEM = dict(
    id='string-quartet-minuet',
    title='Minuet - string quartet on four bracketed staves',
    layout='string-quartet', make=make, pages=1, must_not_split=True,
    expected_notes=('FOUR parts, exactly one per staff: Violin I, Violin II, Viola (alto clef), Violoncello, joined '
                    'by a bracket. Each staff is one part: do not merge staves and do not split a staff - the '
                    'double stops of Violin I (mm.11-12) are chords inside Violin I. "pizz."/"arco" and "dolce" are '
                    'words directions. Repeat sign at the end of m.8.'),
    truth_limitations=[],
    layout_desc='A4 portrait, staff size 18, 3 systems of 4 measures on 4 bracketed staves, full then short names',
    scans=scans(12, 'T3', 'S1'),
    attribution='Minuet for string quartet composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
