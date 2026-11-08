"""two-voices-one-staff-instrument: piano whose right-hand staff carries two independent voices (melody stems
up, inner voice stems down, with its own rests); one part."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

RH1 = ("b'4(\\p cis'' dis'' | e''2 b'4) | cis''4( b' a' | gis'2.) | "
       "b'4(\\mf e'' gis'' | fis''2 e''4) | dis''4( cis'' b' | e''2.)\\fermata")
RH2 = ("gis'2 fis'4 | gis'2 gis'4 | e'2 fis'4 | e'2 r4 | "
       "gis'2 b'4 | a'2 gis'4 | a'4 e' dis' | gis'2.\\fermata")
LH = ("e4 <gis b> <gis b> | e4 <gis b> <gis b> | a,4 <e a> <e a> | e4 <gis b> <gis b> | "
      "e4 <gis b> <gis b> | b,4 <fis a> <fis a> | b,4 <fis a> <fis a> | <e, e>2.\\fermata")


def make():
    pn = mk_part('P1', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('2', 1), ('5', 2)])
    sc = assemble((3, 4), (4, 'major'), [(pn, {'1': RH1, '2': RH2, '5': LH})])
    add_mark(sc, 0, 'tempo', text='Andantino', unit='quarter', bpm=92)
    breaks(sc, systems=(4,))
    hdr = header(sc, 'Song without Words', 'for piano')
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P1', '1'), ('P1', '2')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P1', '5')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 14\\mm', 'system-system-spacing.basic-distance = #16'])


ITEM = dict(
    id='two-voices-piano-song-without-words',
    title='Song without Words - piano right hand with two voices on one staff',
    layout='two-voices-one-staff-instrument', make=make, pages=1, must_not_split=True,
    expected_notes=('ONE part "Piano" (two staves, brace). The treble staff carries TWO voices: melody (voice 1, stems '
                    'up) and inner voice (voice 2, stems down, with a quarter rest in m.4); both stay in the Piano '
                    'part - this is NOT a closed choir score and must not be split into extra parts. Left hand: bass '
                    'note + two-note chords.'),
    truth_limitations=[],
    layout_desc='A4 portrait, staff size 20, 2 systems of 4 measures',
    scans=scans(19, 'T1', 'S4'),
    attribution='Song without Words for piano composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
