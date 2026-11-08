"""choir-sab: three-part choir (Soprano, Alto, Baritone) on three bracketed staves, lyrics under each."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, scans

S = ("b'4 b' a' g' | a'4 b' g'2 | b'4 c'' d'' b' | a'4 g' a'2 | "
     "d''4 d'' c'' b' | c''4 b' a'2 | g'4 b' a' g' | fis'4 a' g'2\\fermata")
A = ("g'4 g' fis' e' | fis'4 g' d'2 | g'4 a' b' g' | fis'4 e' fis'2 | "
     "b'4 b' a' g' | a'4 g' fis'2 | e'4 g' fis' e' | d'4 c' b2\\fermata")
BAR = ("g4 e d c | d4 g b,2 | e4 a g e | d4 c d2 | "
       "g4 b, a, e | c4 g d2 | c4 g d e | d4 d g2\\fermata")
TEXT = ("Green the fields and blue the sky, swift the swal -- lows dart and fly; "
        "sing, O sing, the sum -- mer long, all the earth is full of song.")


def make():
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble']), mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('B', 'Baritone', 'Bar.', 'voice', 1, ['bass'])]
    src = {'S': S, 'A': A, 'B': BAR}
    sc = assemble((4, 4), (1, 'major'), [(p, {'1': src[p.id]}) for p in parts], time_symbol='common')
    for p in parts:
        set_verses(sc, p.id, '1', [TEXT], mode='attack')
        first_note(sc, p.id, '1', 0).dynamics.append('mp')
        first_note(sc, p.id, '1', 4).dynamics.append('f')
        first_note(sc, p.id, '1', 6).wedge.append('diminuendo')
        first_note(sc, p.id, '1', 7, 1).wedge.append('stop')
    add_mark(sc, 0, 'tempo', text='Lightly', unit='quarter', bpm=104)
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Summer Song', 'for three-part choir (SAB)', lyricist='Words: coverage suite (2026)')
    staves = []
    for pid, clef, nm, sh in (('S', 'treble', 'Soprano', 'S.'), ('A', 'treble', 'Alto', 'A.'),
                              ('B', 'bass', 'Baritone', 'Bar.')):
        staves.append({'id': pid.lower(), 'clef': clef, 'name': nm, 'short': sh, 'voices': [(pid, '1')],
                       'lyrics': [{'voice': (pid, '1'), 'verses': [1], 'place': 'below', 'stanza': False}]})
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': staves}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 18\\mm', 'short-indent = 9\\mm',
                                                'system-system-spacing.basic-distance = #22'])


ITEM = dict(
    id='choir-sab-summer-song',
    title='Summer Song - SAB choir on three bracketed staves',
    layout='choir-sab', make=make, pages=1, must_not_split=False,
    expected_notes=('THREE parts, one staff each: Soprano, Alto (both treble clef) and Baritone (bass clef). The two '
                    'treble staves are separate parts, not a piano right hand. Each staff has its own copy of the '
                    'lyrics (same text, same rhythm). Common-time signature symbol.'),
    truth_limitations=[],
    layout_desc='A4 portrait, staff size 19, 2 systems of 4 measures on 3 bracketed staves, full then short names',
    scans=scans(7, 'T5', 'S2'),
    attribution='Summer Song for SAB choir - music and words composed for the OMR coverage suite (2026) - CC0 1.0.'
                '\n\n' + CC0_NOTE,
)
