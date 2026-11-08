"""hymnal-stanzas: hymnal page - closed SATB, four numbered stanzas interlined between the staves, pickup."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, satb, scans

SOP = ("d'4 | g'4 a' b' g' | c''4 b' a'\\fermata d'' | b'4 g' a' b' | a'4 g' fis'\\fermata d' | "
       "g'4 a' b' c'' | d''4 c'' b'\\fermata b' | c''4 b' a' g' | a'4 fis' g'\\fermata")
CHORDS = ['G', 'G', 'D', 'G', 'Em', 'C', 'G', 'D', 'G', 'G', 'C', 'D', 'Em', 'D', 'Em', 'D', 'G',
          'G', 'D', 'G', 'Am', 'G', 'Am', 'Em', 'G', 'C', 'G', 'Am', 'Em', 'Am', 'D7', 'G']
STANZAS = [
    "O Light that breaks the dark of night, shine on the path our feet must tread; "
    "make plain the way, make clear the sight, and lead us where the lost are led.",
    "O Word that speaks through wind and flame, call out our names in ev -- ery land; "
    "teach us to praise your ho -- ly name, and hold us in your gen -- tle hand.",
    "O Love that will not let us go, come down like rain on thirst -- y ground; "
    "make deep the roots, make strong the flow, till all the lost at last are found.",
    "To Fa -- ther, Son, and Spir -- it be all praise and hon -- or, glo -- ry, might, "
    "through all the a -- ges yet to be, in end -- less day and change -- less light.",
]


def make():
    v = satb(SOP, CHORDS, 7)
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble']), mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('T', 'Tenor', 'T.', 'voice', 1, ['bass']), mk_part('B', 'Bass', 'B.', 'voice', 1, ['bass'])]
    sc = assemble((4, 4), (1, 'major'), [(p, {'1': v[p.id]}) for p in parts])
    set_verses(sc, 'S', '1', STANZAS, mode='attack')
    add_mark(sc, 0, 'tempo', text='Steadily', unit='half', bpm=56)
    breaks(sc, systems=(3, 6))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Light of Ages', 'L.M.', composer='Tune and harmony: coverage suite (2026)',
                 lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
        {'id': 'sa', 'clef': 'treble', 'voices': [('S', '1'), ('A', '1')],
         'lyrics': [{'voice': ('S', '1'), 'verses': [1, 2, 3, 4], 'place': 'below', 'stanza': True}]},
        {'id': 'tb', 'clef': 'bass', 'voices': [('T', '1'), ('B', '1')]}]}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 0', 'system-system-spacing.basic-distance = #20'],
                         extra_layout=['\\context { \\Score \\remove "Bar_number_engraver" }'])


ITEM = dict(
    id='hymnal-stanzas-light-of-ages',
    title='Light of Ages - hymnal page: closed SATB with four stanzas between the staves',
    layout='hymnal-stanzas', make=make, pages=1, must_not_split=False,
    shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
    expected_notes=('FOUR parts (Soprano, Alto, Tenor, Bass) in hymnal closed score without part names: S+A share the '
                    'treble staff, T+B the bass staff (split by stem direction). FOUR stanzas are interlined between '
                    'the staves (lyric lines 1-4, numbered "1."-"4." at the start), aligned to the Soprano. Pickup '
                    'measure, fermatas at the line ends, no bar numbers.'),
    truth_limitations=['All four stanzas are encoded on the Soprano (<lyric number="1".."4">); stanza numbers are not '
                       'encoded.'],
    layout_desc='A4 portrait, staff size 19, 3 systems (pickup + 2, 3, 3 measures), four lyric lines between the staves',
    scans=scans(15, 'T1', 'S5'),
    attribution='Light of Ages - tune, harmonisation (corpus voice-leading solver) and the four stanzas composed for '
                'the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
