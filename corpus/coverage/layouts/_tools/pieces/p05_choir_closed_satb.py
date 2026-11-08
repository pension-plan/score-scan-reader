"""choir-closed-satb: four-part choir in closed score (S+A on a treble staff, T+B on a bass staff)."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, satb, scans

SOP = ("fis'4 a' b' a' | d''4 cis'' b'2 | a'4 b'8( cis'') d''4 a' | g'4 fis' e'2\\fermata | "
       "fis'4 g' a' d'' | cis''4 b' a'2 | b'4 a' g' fis' | e'4 e' d'2\\fermata")
CHORDS = ['D', 'D', 'G', 'D', 'Bm', 'A', 'G', 'D', 'G', 'A', 'D', 'D', 'Em', 'D/F#', 'A',
          'D', 'Em', 'D', 'Bm', 'A', 'G', 'D', 'G', 'D', 'Em', 'D', 'Em', 'A7', 'D']
TEXT = ("Light of morn -- ing, bright and clear, bring the _ wak -- ing world to cheer; "
        "let the val -- leys and the hills sing with all the run -- ning rills.")


def make():
    v = satb(SOP, CHORDS, 2)
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble']), mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('T', 'Tenor', 'T.', 'voice', 1, ['bass']), mk_part('B', 'Bass', 'B.', 'voice', 1, ['bass'])]
    sc = assemble((4, 4), (2, 'major'), [(p, {'1': v[p.id]}) for p in parts])
    set_verses(sc, 'S', '1', [TEXT], mode='attack')
    for pid in ('S', 'T'):
        first_note(sc, pid, '1', 0).dynamics.append('mf')
        first_note(sc, pid, '1', 4).dynamics.append('p')
    first_note(sc, 'S', '1', 6).wedge.append('crescendo')
    first_note(sc, 'S', '1', 7).wedge.append('stop')
    add_mark(sc, 0, 'tempo', text='Moderato', unit='quarter', bpm=88)
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Light of Morning', 'SATB', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
        {'id': 'sa', 'clef': 'treble', 'name': ['Soprano', 'Alto'], 'short': ['S.', 'A.'],
         'voices': [('S', '1'), ('A', '1')],
         'lyrics': [{'voice': ('S', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]},
        {'id': 'tb', 'clef': 'bass', 'name': ['Tenor', 'Bass'], 'short': ['T.', 'B.'],
         'voices': [('T', '1'), ('B', '1')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 18\\mm', 'short-indent = 8\\mm',
                                                'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='choir-closed-satb-light-of-morning',
    title='Light of Morning - SATB choir in closed score (two staves)',
    layout='choir-closed-satb', make=make, pages=1, must_not_split=False,
    shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
    expected_notes=('FOUR parts: Soprano, Alto, Tenor, Bass. Soprano (stems up) and Alto (stems down) share the '
                    'treble staff; Tenor (up) and Bass (down) share the bass staff - split each staff by stem '
                    'direction. One verse of lyrics between the staves, aligned to the Soprano. Fermatas on every '
                    'voice at the phrase ends.'),
    truth_limitations=['Lyrics are encoded on the Soprano only (they are printed once between the staves).'],
    layout_desc='A4 portrait, staff size 20, 2 systems of 4 measures, bracketed choir staves with two-line names',
    scans=scans(5, 'T1', 'S3'),
    attribution='Light of Morning (SATB) - tune, harmonisation (corpus voice-leading solver) and words composed for '
                'the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
