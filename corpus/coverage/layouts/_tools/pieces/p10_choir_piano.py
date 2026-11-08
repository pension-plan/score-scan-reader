"""choir-piano: closed-score SATB choir above a piano accompaniment (piano intro and outro bar)."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, satb, scans

SOP = ("R1 | e'4 g' c'' b' | a'4 g' e'2 | f'4 a' g' e' | d'4 e' d'2 | "
       "c''4 c'' b' a' | g'4 a' g'2 | e'4 g' f' d' | c'4 d' c'2 | R1")
CHORDS = ['C', 'C', 'Am', 'G', 'F', 'C', 'Am', 'Dm', 'F', 'C', 'Am', 'G', 'C', 'G',
          'C', 'Am', 'G', 'F', 'C', 'F', 'C', 'Am', 'C', 'Dm', 'G', 'C', 'G', 'C']
TEXT = ("Come, ye peo -- ple, raise the song, let the cho -- rus now be strong; "
        "hand in hand and voice with voice, all cre -- a -- tion, now re -- joice.")
RH = ("<e' g' c''>2\\mf <d' g' b'>2 | <e' g' c''>2 <c' e' a'>4 <d' g' b'>4 | <c' f' a'>2 <c' e' g'>2 | "
      "<d' f' a'>2 <c' e' g'>2 | <b d' g'>2 <b d' g'>2 | <e' g' c''>4 <c' e' a'>4 <d' g' b'>4 <c' f' a'>4 | "
      "<e' g' c''>2 <c' e' g'>2 | <c' e' a'>2 <d' f' a'>4 <b d' g'>4 | <c' e' g'>2\\< <b d' g'>2 | "
      "<e' g' c''>1\\!\\f\\fermata")
LH = ("c4 g, c g, | c4 e a, g, | f,4 a, c2 | d4 f c a, | g,4 d g,2 | a,4 f, g, f, | c4 f, c2 | "
      "a,4 c d g, | c4 g, c2 | <c, c>1\\fermata")


def make():
    v = satb(SOP, CHORDS, 0)
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble']), mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('T', 'Tenor', 'T.', 'voice', 1, ['bass']), mk_part('B', 'Bass', 'B.', 'voice', 1, ['bass'])]
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (0, 'major'), [(p, {'1': v[p.id]}) for p in parts] + [(pn, {'1': RH, '5': LH})])
    set_verses(sc, 'S', '1', [TEXT], mode='attack')
    for pid in ('S', 'T'):
        first_note(sc, pid, '1', 1).dynamics.append('mf')
        first_note(sc, pid, '1', 5).dynamics.append('f')
    add_mark(sc, 0, 'tempo', text='Joyfully', unit='quarter', bpm=112)
    breaks(sc, systems=(5,))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Song of Rejoicing', 'for SATB choir and piano', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [
        {'type': 'ChoirStaff', 'staves': [
            {'id': 'sa', 'clef': 'treble', 'name': ['Soprano', 'Alto'], 'short': ['S.', 'A.'],
             'voices': [('S', '1'), ('A', '1')],
             'lyrics': [{'voice': ('S', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]},
            {'id': 'tb', 'clef': 'bass', 'name': ['Tenor', 'Bass'], 'short': ['T.', 'B.'],
             'voices': [('T', '1'), ('B', '1')]}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'short': 'Pno.', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    return sc, lay, opts(hdr, 18, extra_paper=['indent = 18\\mm', 'short-indent = 9\\mm',
                                                'system-system-spacing.basic-distance = #20'])


ITEM = dict(
    id='choir-piano-song-of-rejoicing',
    title='Song of Rejoicing - closed SATB choir with piano accompaniment',
    layout='choir-piano', make=make, pages=1, must_not_split=True,
    shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
    expected_notes=('FIVE parts: Soprano, Alto, Tenor, Bass (closed score: S+A share the treble staff, T+B the bass '
                    'staff; split by stem direction) and Piano (ONE part with two staves joined by a brace - must '
                    'not be split). The choir is silent in m.1 and m.10 (piano intro/outro): each choir staff shows '
                    'two whole-bar rests (one per part). Lyrics between the choir staves belong to the Soprano.'),
    truth_limitations=['Lyrics are encoded on the Soprano only.'],
    layout_desc='A4 portrait, staff size 18, 2 systems (5 + 5 measures) of 4 staves: bracketed choir + braced piano',
    scans=scans(10, 'T1', 'S2'),
    attribution='Song of Rejoicing for SATB choir and piano - music, harmonisation (corpus voice-leading solver) and '
                'words composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
