"""cross-staff: piano piece whose left-hand arpeggios climb onto the treble staff (kneed beams across the
staves) and whose right hand once dips onto the bass staff; still ONE piano part."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

RH = ("g'2(\\p f'2 | ees'2 d'2) | c''2( bes'2 | aes'2 g'2) | "
      "ees''2(\\mf d''2 | c''2 b'2) | c''4 \\st2 g4( \\st0 c''2) | <ees' g' c''>1\\fermata")
LH = ("c8[\\sustainOn g \\st1 c' ees'] \\st0 b,8[ g\\sustainOff \\st1 d' f'] \\st0 | "
      "c8[ g \\st1 c' ees'] \\st0 g,8[ g \\st1 b d'] \\st0 | "
      "aes,8[\\sustainOn ees \\st1 c' ees'] \\st0 ees8[ g\\sustainOff \\st1 bes ees'] \\st0 | "
      "f,8[ c \\st1 aes c'] \\st0 g,8[ d \\st1 b d'] \\st0 | "
      "c8[\\< g \\st1 c' ees'] \\st0 g,8[ d \\st1 b f'\\!] \\st0 | "
      "aes,8[ ees \\st1 c' ees'] \\st0 g,8[ d \\st1 g b] \\st0 | "
      "c8[ g \\st1 c' ees'] \\st0 f,8[ c \\st1 aes c'] \\st0 | <c, c>1\\fermata")


def make():
    pn = mk_part('P1', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (-3, 'minor'), [(pn, {'1': RH, '5': LH})])
    add_mark(sc, 0, 'tempo', text='Con moto', unit='quarter', bpm=80)
    breaks(sc, systems=(4,))
    hdr = header(sc, 'Arpeggio Study', 'for piano')
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P1', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P1', '5')]}]}]}
    return sc, lay, opts(hdr, 20, extra_paper=['indent = 14\\mm', 'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='cross-staff-piano-arpeggio-study',
    title='Arpeggio Study - piano with cross-staff left-hand arpeggios (kneed beams)',
    layout='cross-staff', make=make, pages=1, must_not_split=True,
    # forced knee stems on cross-staff beams: LilyPond's beam quanting reports a cosmetic slope warning
    allow_warnings=[r'no viable initial configuration found: may not find good beam slope'],
    expected_notes=('ONE part "Piano" (two staves, brace). In every measure the left hand plays groups of four '
                    'eighths beamed ACROSS the staves: two notes on the bass staff (stems up) and two on the treble '
                    'staff (stems down) - these treble-staff notes belong to the LEFT hand (voice 5, <staff>1</staff>), '
                    'not to the right-hand melody. In m.7 one right-hand note (g, stem down) is printed on the bass '
                    'staff (voice 1, <staff>2</staff>).'),
    truth_limitations=['Cross-staff notes keep their voice and carry the staff they are printed on (<staff>).'],
    layout_desc='A4 portrait, staff size 20, 2 systems of 4 measures, kneed cross-staff beams',
    scans=scans(18, 'T3', 'S3'),
    attribution='Arpeggio Study for piano composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
