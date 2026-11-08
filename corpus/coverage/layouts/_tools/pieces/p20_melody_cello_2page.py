"""melody (variant): a two-page solo cello melody in bass clef with a tenor-clef passage."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

CELLO = ("g,4(\\p a, bes, | c4 d ees) | d4.( c8 bes, a,) | g,2 r4 | "
         "d4(\\mf fis g | a4 bes c') | d'2.~ | d'2 r4 | "
         "\\clef=tenor f'4(\\f ees'8 d' c' bes) | a4( bes c') | d'4-> c'-> bes-> | a2.\\> | "
         "\\clef=bass g4(\\!\\p fis g) | ees4( d c) | d4-- d,-- r4 | g,2.\\fermata")


def make():
    vc = mk_part('P1', 'Violoncello', 'Vc.', 'other', 1, ['bass'])
    sc = assemble((3, 4), (-2, 'minor'), [(vc, {'1': CELLO})])
    add_mark(sc, 0, 'tempo', text='Lento cantabile', unit='quarter', bpm=60)
    breaks(sc, systems=(4, 12), pages=(8,))
    hdr = header(sc, 'Elegy', 'for violoncello solo',
                 extra_credits=[{'page': 2, 'type': 'page number', 'text': '2'}])
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'vc', 'clef': 'bass', 'name': 'Violoncello', 'short': 'Vc.', 'voices': [('P1', '1')]}]}]}
    return sc, lay, opts(hdr, 24, extra_paper=['indent = 22\\mm', 'short-indent = 8\\mm',
                                                'system-system-spacing.basic-distance = #20',
                                                'print-page-number = ##t', 'print-first-page-number = ##f'])


ITEM = dict(
    id='melody-cello-elegy-2page',
    title='Elegy - two-page solo cello melody (bass clef, tenor-clef passage)',
    layout='melody', make=make, pages=2, must_not_split=False,
    expected_notes=('ONE part "Violoncello", one staff, one voice, two pages (forced page break before m.9). '
                    'The clef changes to tenor clef at m.9 (start of page 2) and back to bass clef at m.13 '
                    '(start of the last system); pitches are unaffected by the clef changes.'),
    truth_limitations=['Page numbers are printed (page 2) and recorded only as a <credit> on page 2.'],
    layout_desc='A4 portrait, staff size 24, page 1: title + 2 systems, page 2: 2 systems; full name on the first '
                'system, "Vc." afterwards',
    scans=scans(20, 'T5', 'S5'),
    attribution='Elegy for violoncello solo, composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
