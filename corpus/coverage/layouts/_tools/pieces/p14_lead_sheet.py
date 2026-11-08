"""lead-sheet: melody with chord symbols above and two verses of lyrics, repeat with 1st/2nd endings."""
from fractions import Fraction as F

from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

MEL = ("bes'4\\mf c'' d'' f'' | ees''2 d''4 c'' | bes'4. c''8 d''4 bes' | c''1 | "
       "bes'4 c'' d'' f'' | g''2 f''4 ees'' | d''4 c''8 bes' c''4 d'' | bes'1 | bes'2. r4 | "
       "g''4 g'' f'' ees'' | d''2 c''2 | f''4 f'' ees'' d'' | c''1 | "
       "bes'4 c'' d'' ees'' | f''4 g''8 f'' d''4 c'' | bes'1\\fermata")
V1 = ("Walk -- ing down the long and wind -- ing road, the sun is warm up -- on my face, and all the "
      "world is wide to -- day. _ "
      "Oh, the road goes on and on, through the val -- ley, o -- ver the hill and back a -- gain to you.")
V2 = ("Sing -- ing ev -- ery song I know, the wind is soft and slow, I'm go -- ing where the riv -- ers run, "
      "I'll find my _ way.")
CHORDS = [(0, 0, 'Bb'), (0, 2, 'Gm7'), (1, 0, 'Cm7'), (1, 2, 'F7'), (2, 0, 'Bb'), (2, 2, 'Dm'),
          (3, 0, 'Cm7'), (3, 2, 'F7'), (4, 0, 'Bb'), (4, 2, 'Gm7'), (5, 0, 'Eb'), (5, 2, 'F7'),
          (6, 0, 'Bb/D'), (6, 2, 'Cm7'), (6, 3, 'F7'), (7, 0, 'Bb'), (7, 2, 'F7'), (8, 0, 'Bb'),
          (9, 0, 'Eb'), (9, 2, 'Ebm'), (10, 0, 'Bb/F'), (10, 2, 'G7'), (11, 0, 'Cm7'), (11, 2, 'F7'),
          (12, 0, 'Cm7'), (12, 2, 'F7'), (13, 0, 'Bb'), (13, 2, 'Gm'), (14, 0, 'Cm7'), (14, 2, 'F7'),
          (15, 0, 'Bb6')]


def make():
    m = mk_part('P1', 'Melody', '', 'voice', 1, ['treble'])
    sc = assemble((4, 4), (-2, 'major'), [(m, {'1': MEL})])
    # verse 1: A section (mm.1-8, 1st ending) + B section; verse 2: A section with the 2nd ending (m.9)
    set_verses(sc, 'P1', '1', [V1, V2], mode='attack', strict=False)
    sc.harmonies = [(i, F(o), s) for i, o, s in CHORDS]
    add_mark(sc, 0, 'tempo', text='Moderately', unit='quarter', bpm=100)
    sc.measures[7].volta_start, sc.measures[7].volta_end, sc.measures[7].right_bar = '1', 'stop', 'repeat-end'
    sc.measures[8].volta_start, sc.measures[8].volta_end, sc.measures[8].right_bar = '2', 'discontinue', 'double'
    breaks(sc, systems=(4, 9, 13))
    hdr = header(sc, 'The Long Road', 'lead sheet', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'mel', 'clef': 'treble', 'voices': [('P1', '1')],
         'lyrics': [{'voice': ('P1', '1'), 'verses': [1, 2], 'place': 'below', 'stanza': True}]}]}]}
    o = opts(hdr, 20, extra_paper=['indent = 0', 'system-system-spacing.basic-distance = #17'])
    o['chordnames_with'] = ["majorSevenSymbol = \\markup { maj7 }"]
    return sc, lay, o


ITEM = dict(
    id='lead-sheet-long-road',
    title='The Long Road - lead sheet: melody, chord symbols, two verses, 1st/2nd endings',
    layout='lead-sheet', make=make, pages=1, must_not_split=False,
    printed_not_in_truth={'stanza-text': 2},
    expected_notes=('ONE part (melody, no instrument name) with chord symbols above the staff (31 <harmony> '
                    'elements, some changing in the middle of a whole note: <offset>) and two lyric lines under '
                    'the repeated A section (verse 1 continues into the 1st ending and the B section, verse 2 into '
                    'the 2nd ending). Repeat with 1st ending (m.8) and 2nd ending (m.9), notated order.'),
    truth_limitations=['Chord symbols are <harmony> (root/kind/bass); LilyPond prints them in its own style '
                       '(e.g. superscript 7, "m7"); the stanza numbers "1."/"2." are not encoded.'],
    layout_desc='A4 portrait, staff size 20, 4 systems (4+5+4+3 measures), chord names above the staff',
    scans=scans(14, 'T5', 'S1'),
    attribution='The Long Road - melody, chords and words composed for the OMR coverage suite (2026) - CC0 1.0.\n\n'
                + CC0_NOTE,
)
