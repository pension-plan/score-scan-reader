"""choir-ttbb: male choir in closed score (Tenor I+II on a treble-8 staff, Baritone+Bass on a bass staff)."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, satb, scans

TI = ("d'4 ees' f' d' | g'4 f' d'2 | c'4 d' ees' c' | f'4 ees' d'2\\fermata | "
      "d'4 f' g' a' | bes'4 a' g'2 | f'4 d' ees' c' | d'4 c' bes2\\fermata")
CHORDS = ['Bb', 'Cm', 'F', 'Bb', 'Gm', 'F', 'Bb', 'F', 'Gm', 'Cm', 'F', 'Bb', 'Eb', 'Bb',
          'Bb', 'Dm', 'Eb', 'F', 'Bb', 'F', 'Gm', 'Bb', 'Gm', 'Cm', 'F', 'Gm', 'F7', 'Bb']
TEXT = ("Hear the bells of eve -- ning ring, o -- ver field and qui -- et spring; "
        "rest, my broth -- ers, day is done, sleep be -- neath the set -- ting sun.")


def make():
    v = satb(TI, CHORDS, 10)
    parts = [mk_part('T1', 'Tenor I', 'T. I', 'voice', 1, ['treble_8']),
             mk_part('T2', 'Tenor II', 'T. II', 'voice', 1, ['treble_8']),
             mk_part('B1', 'Baritone', 'Bar.', 'voice', 1, ['bass']),
             mk_part('B2', 'Bass', 'B.', 'voice', 1, ['bass'])]
    src = {'T1': v['S'], 'T2': v['A'], 'B1': v['T'], 'B2': v['B']}
    sc = assemble((4, 4), (-2, 'major'), [(p, {'1': src[p.id]}) for p in parts])
    set_verses(sc, 'T1', '1', [TEXT], mode='attack')
    for pid in ('T1', 'B1'):
        first_note(sc, pid, '1', 0).dynamics.append('p')
        first_note(sc, pid, '1', 4).dynamics.append('mf')
        first_note(sc, pid, '1', 6).dynamics.append('pp')
    add_mark(sc, 0, 'tempo', text='Calmly', unit='quarter', bpm=69)
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'T1', 'last': 'B2', 'symbol': 'bracket'}]
    sc.marks_part = 'T1'
    hdr = header(sc, 'Evening Bells', 'for male choir (TTBB)', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
        {'id': 'tt', 'clef': 'treble_8', 'name': ['Tenor I', 'Tenor II'], 'short': ['T. I', 'T. II'],
         'voices': [('T1', '1'), ('T2', '1')],
         'lyrics': [{'voice': ('T1', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]},
        {'id': 'bb', 'clef': 'bass', 'name': ['Baritone', 'Bass'], 'short': ['Bar.', 'B.'],
         'voices': [('B1', '1'), ('B2', '1')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 20\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='choir-ttbb-evening-bells',
    title='Evening Bells - TTBB male choir in closed score',
    layout='choir-ttbb', make=make, pages=1, must_not_split=False,
    shared_staves=[['Tenor I', 'Tenor II'], ['Baritone', 'Bass']],
    expected_notes=('FOUR parts: Tenor I + Tenor II share the upper staff (treble clef with 8 below = sounds an octave '
                    'lower; truth pitches are sounding), Baritone + Bass share the bass staff; split each staff by '
                    'stem direction (upper part stems up). Lyrics between the staves belong to Tenor I.'),
    truth_limitations=['Lyrics are encoded on Tenor I only.'],
    layout_desc='A4 portrait, staff size 20, 2 systems of 4 measures, bracketed two-staff closed score',
    scans=scans(8, 'T3', 'S4'),
    attribution='Evening Bells for TTBB choir - tune, harmonisation (corpus voice-leading solver) and words composed '
                'for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
