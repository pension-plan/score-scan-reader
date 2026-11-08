"""melody: a single-staff instrumental melody (flute), 16 bars on 4 systems."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

FLUTE = ("a'8(\\mf d'' fis'' a'' | g''8 fis'' e'' d'') | cis''8-. d''-. e''-. fis''-. | e''4\\trill d''8 r8 | "
         "a''4->(\\f g''8 fis'') | e''16( fis'' g'' e'' cis''8) a'-. | \\tup3/2 b'8( cis'' d'' \\tupend e''8 fis'') | "
         "d''4\\breathe r4 | "
         "fis''8.(\\p g''16 a''8 fis'') | e''8.( fis''16 g''8 e'') | d''8-- cis''-- b'-- ais'-- | b'2~\\< | "
         "b'8\\! cis''(\\mp d'' e'' | f''8 e'' d'' c'') | b'8\\> a'( g' e') | d'2\\!\\fermata")


def make():
    fl = mk_part('P1', 'Flute', 'Fl.', 'other', 1, ['treble'])
    sc = assemble((2, 4), (2, 'major'), [(fl, {'1': FLUTE})])
    add_mark(sc, 0, 'tempo', text='Allegretto', unit='quarter', bpm=96)
    add_mark(sc, 8, 'rehearsal', text='A')
    breaks(sc, systems=(4, 8, 12))
    hdr = header(sc, 'Air for Flute')
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'fl', 'clef': 'treble', 'name': 'Flute', 'voices': [('P1', '1')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 16\\mm', 'system-system-spacing.basic-distance = #14'])


ITEM = dict(
    id='melody-flute-air',
    title='Air for Flute - single-staff instrumental melody',
    layout='melody', make=make, pages=1, must_not_split=False,
    expected_notes=('ONE part "Flute", one treble staff, one voice. 16 measures of 2/4 on 4 systems; triplet in m.7, '
                    'trill in m.4, breath mark in m.8, tie across the system break m.12-13, rehearsal mark A at m.9.'),
    truth_limitations=[],
    layout_desc='A4 portrait, staff size 20, 4 systems of 4 measures, instrument name on the first system',
    scans=scans(1, 'T2', 'S2'),
    attribution='Air for Flute, composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
