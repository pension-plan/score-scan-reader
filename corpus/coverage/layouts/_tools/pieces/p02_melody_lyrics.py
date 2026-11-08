"""melody-lyrics: a song melody with one verse of lyrics under the staff."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

VOICE = ("c'4\\mp | f'4 g' a' | bes'4 a'8( g') f'4 | g'2.~ | g'4 r4 c'4 | "
         "f'4\\< a' c'' | d''4\\! c''8( bes') a'4 | g'2.\\breathe | r2 c''4\\mf | "
         "a'4 bes' c'' | d''4 c''8( bes') a'4 | g'2.~ | g'4 r4 c'4\\p | "
         "f'4 g' a' | c''4\\> a' g'8( a') | f'2.~ | f'2\\! r4")
TEXT = ("The morn -- ing light is on _ the hill, the riv -- er runs so clear _ and still; "
        "come walk with me a -- long _ the way, and sing the sun -- rise in -- to _ day.")


def make():
    v = mk_part('P1', 'Voice', 'V.', 'voice', 1, ['treble'])
    sc = assemble((3, 4), (-1, 'major'), [(v, {'1': VOICE})])
    set_verses(sc, 'P1', '1', [TEXT], mode='attack')
    add_mark(sc, 0, 'tempo', text='Gently', unit='quarter', bpm=84)
    breaks(sc, systems=(5, 9, 13))
    hdr = header(sc, 'Morning Song', composer='Coverage suite (2026)', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'v', 'clef': 'treble', 'voices': [('P1', '1')],
         'lyrics': [{'voice': ('P1', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 0', 'system-system-spacing.basic-distance = #15'])


ITEM = dict(
    id='melody-lyrics-morning-song',
    title='Morning Song - vocal melody with one verse of lyrics',
    layout='melody-lyrics', make=make, pages=1, must_not_split=False,
    expected_notes=('ONE part "Voice" (no instrument name printed), one staff, one voice, one verse of lyrics '
                    'under the staff: 36 syllables incl. hyphenated words and melismas on slurred eighth pairs '
                    '(beamed only within the melisma, other eighths flagged per vocal convention). Pickup measure '
                    '(m.0), ties across barlines, breath mark in m.7.'),
    truth_limitations=['Lyrics are encoded as <lyric number="1"> on the voice; melisma extenders as <extend/>.'],
    layout_desc='A4 portrait, staff size 20, pickup + 16 measures on 4 systems, no instrument name',
    scans=scans(2, 'T3', 'S3'),
    attribution='Morning Song - melody and words composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
