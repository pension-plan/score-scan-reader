"""choir-ssaa: women's choir in closed score on TWO treble staves (S I+II, A I+II)."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, scans

S1 = ("c''4 c'' d'' | c''4 a' f' | g'2. | a'4 bes' c'' | d''4 c'' bes' | a'2. | "
      "f''4 e'' d'' | c''4 bes' a' | g'2. | a'4 c'' bes' | a'4 g' f'8( g') | f'2.\\fermata")
S2 = ("a'4 a' bes' | a'4 f' d' | e'2. | f'4 g' a' | bes'4 a' g' | f'2. | "
      "a'4 g' f' | f'4 g' f' | e'4( d' e') | f'4 a' g' | f'4 e' d'8( e') | c'2.\\fermata")
A1 = ("f'4 f' f' | f'4 c' a | c'2. | c'4 d' f' | f'4 f' d' | c'2. | "
      "f'4 e' d' | c'4 d' c' | c'2. | c'4 f' e' | c'4 bes bes | a2.\\fermata")
A2 = ("c'4 c' bes | f4 f f | g2. | a4 bes a | bes4 a g | a2. | "
      "d'4 c' bes | a4 g f | g2. | a4 a c' | a4 g g | f2.\\fermata")
TEXT = ("Snow is fall -- ing soft and white, cov -- er -- ing the hills to -- night; "
        "hush, the world is fast a -- sleep, stars their qui -- et vig -- il _ keep.")


def make():
    parts = [mk_part('S1', 'Soprano I', 'S. I', 'voice', 1, ['treble']),
             mk_part('S2', 'Soprano II', 'S. II', 'voice', 1, ['treble']),
             mk_part('A1', 'Alto I', 'A. I', 'voice', 1, ['treble']),
             mk_part('A2', 'Alto II', 'A. II', 'voice', 1, ['treble'])]
    src = {'S1': S1, 'S2': S2, 'A1': A1, 'A2': A2}
    sc = assemble((3, 4), (-1, 'major'), [(p, {'1': src[p.id]}) for p in parts])
    set_verses(sc, 'S1', '1', [TEXT], mode='attack')
    for pid in ('S1', 'A1'):
        first_note(sc, pid, '1', 0).dynamics.append('p')
        first_note(sc, pid, '1', 6).dynamics.append('mp')
        first_note(sc, pid, '1', 9).wedge.append('diminuendo')
        first_note(sc, pid, '1', 11).wedge.append('stop')
        first_note(sc, pid, '1', 11).dynamics.append('pp')
    add_mark(sc, 0, 'tempo', text='Tranquillo', unit='quarter', bpm=72)
    breaks(sc, systems=(6,))
    sc.groups = [{'first': 'S1', 'last': 'A2', 'symbol': 'bracket'}]
    sc.marks_part = 'S1'
    hdr = header(sc, 'Winter Night', "for women's choir (SSAA)", lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
        {'id': 'ss', 'clef': 'treble', 'name': ['Soprano I', 'Soprano II'], 'short': ['S. I', 'S. II'],
         'voices': [('S1', '1'), ('S2', '1')],
         'lyrics': [{'voice': ('S1', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]},
        {'id': 'aa', 'clef': 'treble', 'name': ['Alto I', 'Alto II'], 'short': ['A. I', 'A. II'],
         'voices': [('A1', '1'), ('A2', '1')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 22\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='choir-ssaa-winter-night',
    title='Winter Night - SSAA choir in closed score on two treble staves',
    layout='choir-ssaa', make=make, pages=1, must_not_split=False,
    shared_staves=[['Soprano I', 'Soprano II'], ['Alto I', 'Alto II']],
    expected_notes=('FOUR parts: Soprano I + II share the upper treble staff, Alto I + II share the LOWER staff, which '
                    'is ALSO a treble staff (not a bass staff, not a piano). Split each staff by stem direction. '
                    'Lyrics between the staves belong to Soprano I. 3/4, 12 measures.'),
    truth_limitations=['Lyrics are encoded on Soprano I only.'],
    layout_desc='A4 portrait, staff size 20, 2 systems of 6 measures, bracketed two-staff closed score',
    scans=scans(9, 'T4', 'S5'),
    attribution="Winter Night for SSAA choir - music and words composed for the OMR coverage suite (2026) - CC0 1.0."
                "\n\n" + CC0_NOTE,
)
