"""lyrics: elisions - three numbered verses (Latin, Italian, Spanish) with two syllables sung on one note."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

# 3/4, F major, quarter pickup; 24 syllable slots, melismas (slurred pairs) on slots 6 and 20
VOICE = ("c'4\\mp | f'4 g' a' | bes'4( a') g' | a'2 f'4 | c''4\\< c'' d'' | c''2.\\! | "
         "a'4 bes' c'' | g'2 g'4 | a'4( bes') a' | g'2\\> e'4 | f'2\\!")
VERSES = [
    # Latin, Gloria (public-domain liturgical text): a~in, et~in
    "Glo -- ri -- a~in ex -- cel -- _ sis De -- o, et~in ter -- ra pax "
    "ho -- mi -- ni -- bus bo -- nae _ vo -- lun -- ta -- tis.",
    # Italian (written for this item, CC0): ta~e, da~il, ta~an, ra~u, ce~e
    "Can -- ta~e lo -- da~il Si -- _ gno -- re, can -- ta~an -- co -- ra~u -- na "
    "vol -- ta con la vo -- ce~e _ con il cuo -- re.",
    # Spanish (written for this item, CC0): ta~y, ba~al, ta~o, y~el
    "Can -- ta~y a -- la -- ba~al _ Se -- ñor, can -- ta~o -- tra vez con "
    "a -- mor, y con la voz _ y~el co -- ra -- zón.",
]


def make():
    v = mk_part('P1', 'Voice', 'V.', 'voice', 1, ['treble'])
    sc = assemble((3, 4), (-1, 'major'), [(v, {'1': VOICE})])
    set_verses(sc, 'P1', '1', VERSES, mode='attack')
    add_mark(sc, 0, 'tempo', text='Andante', unit='quarter', bpm=76)
    breaks(sc, systems=(6,))
    hdr = header(sc, 'Canticle of Elisions', composer='Melody: coverage suite (2026)',
                 lyricist='Words: Gloria (trad.); vv. 2-3 coverage suite')
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'v', 'clef': 'treble', 'voices': [('P1', '1')],
         'lyrics': [{'voice': ('P1', '1'), 'verses': [1, 2, 3], 'place': 'below', 'stanza': True}]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 0', 'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='lyr01-elisions-three-languages',
    title='Canticle of Elisions - melody with three numbered verses and lyric elisions',
    layout='melody-lyrics', make=make, pages=1, must_not_split=False,
    engraving_only_counts={'stanza-text': 3},
    printed_not_in_truth={'stanza-text': 3},
    expected_notes=('ONE part "Voice", one staff, pickup + 10 measures of 3/4 on 2 systems. THREE verses under the '
                    'staff, numbered "1."-"3." (Latin, Italian, Spanish). 11 lyric elisions: two syllables sung on '
                    'one note and joined by an undertie (a~in, et~in, ta~e, da~il, ta~an, ra~u, ce~e, ta~y, ba~al, '
                    'ta~o, y~el); each must stay ONE lyric on ONE note (MusicXML <text>a</text><elision/><text>in'
                    '</text>), not two notes or two lyrics. Two slurred melismas per verse (extender or hyphen), '
                    'non-ASCII syllables in verse 3 (Se-ñor, co-ra-zón).'),
    truth_limitations=['Elided syllables are one <lyric> with <syllabic>/<text> pairs separated by <elision>'
                       '‿</elision>; the first part keeps the hyphen to the previous syllable, the last part '
                       'the hyphen to the next.',
                       'Stanza numbers "1."-"3." are printed but MusicXML has no element for them (lyric '
                       'number="1".."3" only): stanza-text is counted from the engraving, not the truth.'],
    layout_desc='A4 portrait, staff size 20, pickup + 10 measures on 2 systems, 3 numbered verses',
    scans=scans(41, 'T1', 'S3'),
    source='Melody and the Italian/Spanish verses composed for the coverage suite (2026); Latin text: Gloria '
           '(traditional liturgical text, public domain)',
    attribution='Canticle of Elisions - melody and the Italian and Spanish verses composed for the OMR coverage '
                'suite (2026) - CC0 1.0. Verse 1 is the opening of the Latin Gloria (traditional liturgical '
                'text, public domain).\n\n' + CC0_NOTE,
)
