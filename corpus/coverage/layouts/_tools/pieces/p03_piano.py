"""piano: solo piano on a grand staff (one part, two staves joined by a brace)."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

RH = ("b'4(-3\\p d''8 c'' b'4 a' | g'4 a'8 b' c''4 e'') | d''4.(\\< c''8 b'4 g'\\!) | <fis' a'>2 <d' fis' a'>2\\arpeggio | "
      "b'8(\\mf c'' d'' e'' fis''4-4 g''-5) | e''4( d''8 cis'' d''2) | c''4-.\\< b'-. a'-. g'-. | <fis' a' d''>1\\f | "
      "g''4(\\p fis''16 e'' d'' c'' b'4 a') | g'8( a' bes' a' g'4 f') | e'4(\\> fis'8 g' a'4 c''\\!) | "
      "<b' d'' g''>1-1-2-5\\arpeggio\\fermata")
LH = ("g,8\\sustainOn d b d g, d b d\\sustainOff | c8\\sustainOn g e' g a, e c' e\\sustainOff | "
      "d8 a fis' a g, d b d | d,2 <d c'>2 | "
      "g,4 <d g b> b,4 <d g b> | a,4 <e g cis'> d4 <fis a> | d4-. e-. fis-. g-. | d,8 a, d fis a fis d a, | "
      "e,8 b, e g c g e c | bes,8 d g d c4 d | c4 a, d d, | <g,, g,>1\\fermata")


def make():
    pn = mk_part('P1', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (1, 'major'), [(pn, {'1': RH, '5': LH})])
    add_mark(sc, 0, 'tempo', text='Andante', unit='quarter', bpm=76)
    breaks(sc, systems=(4, 8))
    sc.measures[7].right_bar = 'double'
    hdr = header(sc, 'Prelude in G', 'for piano')
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P1', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P1', '5')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 14\\mm', 'system-system-spacing.basic-distance = #16'])


ITEM = dict(
    id='piano-grand-staff-prelude',
    title='Prelude in G - solo piano on a braced grand staff',
    layout='piano', make=make, pages=1, must_not_split=True,
    expected_notes=('ONE part "Piano" with two staves (treble + bass) joined by a brace; it must not be split into '
                    'two parts. Chords (incl. rolled chords) stay chords. 12 measures, 3 systems of 4 measures.'),
    truth_limitations=['Sustain-pedal marks are <pedal type="start"/"stop" sign="yes" line="no">.'],
    layout_desc='A4 portrait, staff size 20, 3 systems of 4 measures, instrument name on the first system only',
    scans=scans(3, 'T1', 'S1'),
    attribution='Prelude in G for piano, composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
