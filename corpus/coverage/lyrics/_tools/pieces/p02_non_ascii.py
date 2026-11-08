"""lyrics: non-ASCII syllables - four numbered verses in German, French, Spanish and Czech (8.7.8.7)."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

# 4/4, G major, 8.7.8.7 trochaic meter; 32 slots: slurred eighth melismas on the 3rd note of lines 2 and 4
VOICE = ("d'4\\mf g' b' a' | g'4 b' d'' d'' | e''4 d''8( c'') b'4 a' | b'4 a' g'2 | "
         "a'4\\< b' c'' a' | b'4 c'' d''\\! b' | c''4\\> b'8( a') g'4 e' | d'4 fis' g'2\\!")
VERSES = [
    # German
    "Mor -- gen -- licht auf grü -- nen Hö -- hen, Vö -- gel _ sin -- gen süß und froh; "
    "laß uns still zum Flus -- se ge -- hen, wo die _ Bä -- che rau -- schen so.",
    # French
    "Dou -- ce lu -- miè -- re au ma -- tin, chan -- te _ l'â -- me et le cœur; "
    "près de l'eau, le long du che -- min, al -- lons _ sans crain -- te ni peur.",
    # Spanish
    "¡Can -- ta, can -- ta, mi co -- ra -- zón! la ma -- _ ña -- na ya lle -- gó. "
    "¿Quién no can -- ta en el cam -- po con el _ rí -- o y el sol?",
    # Czech
    "Zpí -- vej, srd -- ce, rá -- no zá -- ří, slun -- ce _ sví -- tí nad ře -- kou, "
    "ptá -- ci zpí -- va -- jí nad lu -- kou, a my _ jde -- me do -- mů dál.",
]


def make():
    v = mk_part('P1', 'Voice', 'V.', 'voice', 1, ['treble'])
    sc = assemble((4, 4), (1, 'major'), [(v, {'1': VOICE})])
    set_verses(sc, 'P1', '1', VERSES, mode='attack')
    add_mark(sc, 0, 'tempo', text='Freely', unit='quarter', bpm=88)
    breaks(sc, systems=(4,))
    hdr = header(sc, 'Morning in Four Tongues', '8.7.8.7.', composer='Melody: coverage suite (2026)',
                 lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'v', 'clef': 'treble', 'voices': [('P1', '1')],
         'lyrics': [{'voice': ('P1', '1'), 'verses': [1, 2, 3, 4], 'place': 'below', 'stanza': True}]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 0', 'system-system-spacing.basic-distance = #20'])


ITEM = dict(
    id='lyr02-non-ascii-four-languages',
    title='Morning in Four Tongues - melody with four numbered verses in four languages (non-ASCII lyrics)',
    layout='melody-lyrics', make=make, pages=1, must_not_split=False,
    engraving_only_counts={'stanza-text': 4},
    printed_not_in_truth={'stanza-text': 4},
    expected_notes=('ONE part "Voice", one staff, 8 measures of 4/4 on 2 systems. FOUR verses under the staff, '
                    'numbered "1."-"4.": German (ä ö ü ß), French (è â œ), Spanish (ñ ó í ¡ ¿) and Czech (í á ř '
                    'ů ě ...). Lyric text must keep its diacritics and inverted punctuation; hyphenated words and two '
                    'slurred melismas per verse (extender after word ends, hyphen inside words).'),
    truth_limitations=['Stanza numbers "1."-"4." are printed but MusicXML has no element for them (lyric '
                       'number="1".."4" only): stanza-text is counted from the engraving, not the truth.',
                       'Punctuation is part of the syllable text (e.g. "¡Can", "zón!", "gó.").'],
    layout_desc='A4 portrait, staff size 20, 8 measures on 2 systems, 4 numbered verses',
    scans=scans(42, 'T2', 'S2'),
    attribution='Morning in Four Tongues - melody and all four verses composed for the OMR coverage suite (2026) - '
                'CC0 1.0.\n\n' + CC0_NOTE,
)
