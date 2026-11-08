"""divisi: string orchestra where Violin I splits into two voices on its staff ("div." ... "unis.") and
Violin II plays divisi as chords; each section stays ONE part."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

V1A = ("b'4\\mf e'' g'' fis''8 e'' | dis''4 e'' fis''2 | g''4^\"div.\" a'' b''2 | a''4 g'' fis''2 | "
       "e''4^\"unis.\" g''8 fis'' e''4 b' | c''4 d'' e''2 | fis''4^\"div.\"\\< g'' a'' fis'' | g''1\\!\\f\\fermata")
V1B = ("s1 | s1 | e''4 fis'' g''2 | c''4 b' dis''2 | s1 | s1 | dis''4 e'' c'' a' | e''1\\fermata")
V2 = ("g'4\\mf b' b' a'8 g' | fis'4 g' a'2 | <b' e''>4^\"div.\" <c'' fis''> <d'' g''>2 | <c'' e''>4 <b' d''> <b' dis''>2 | "
      "g'4^\"unis.\" b'8 a' g'4 g' | a'4 b' c''2 | <a' c''>4\\< <b' e''> <a' e''> <fis' c''> | <g' b'>1\\!\\f\\fermata")
VA = ("e'4\\mf g' g' fis' | b4 b dis'2 | e'4 e' d'2 | e'4 e' fis'2 | e'4 e' e' e' | e'4 fis' g'2 | "
      "fis'4\\< g' e' dis' | e'1\\!\\f\\fermata")
VC = ("e4\\mf e e b, | b,4 e b,2 | e4 a g2 | a4 e b,2 | e4 e c c | a,4 b, c2 | b,4\\< e a, b, | e,1\\!\\f\\fermata")


def make():
    v1 = mk_part('V1', 'Violin I', 'Vn. I', 'other', 1, ['treble'], [('1', 1), ('2', 1)])
    v2 = mk_part('V2', 'Violin II', 'Vn. II', 'other', 1, ['treble'])
    va = mk_part('VA', 'Viola', 'Va.', 'other', 1, ['alto'])
    vc = mk_part('VC', 'Violoncello', 'Vc.', 'other', 1, ['bass'])
    sc = assemble((4, 4), (1, 'minor'), [(v1, {'1': V1A, '2': V1B}), (v2, {'1': V2}), (va, {'1': VA}), (vc, {'1': VC})])
    add_mark(sc, 0, 'tempo', text='Andante espressivo', unit='quarter', bpm=72)
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'V1', 'last': 'VC', 'symbol': 'bracket'}]
    hdr = header(sc, 'Lament', 'for string orchestra')
    lay = {'groups': [{'type': 'StaffGroup', 'staves': [
        {'id': 'v1', 'clef': 'treble', 'name': 'Violin I', 'short': 'Vn. I', 'voices': [('V1', '1'), ('V1', '2')]},
        {'id': 'v2', 'clef': 'treble', 'name': 'Violin II', 'short': 'Vn. II', 'voices': [('V2', '1')]},
        {'id': 'va', 'clef': 'alto', 'name': 'Viola', 'short': 'Va.', 'voices': [('VA', '1')]},
        {'id': 'vc', 'clef': 'bass', 'name': 'Violoncello', 'short': 'Vc.', 'voices': [('VC', '1')]}]}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 20\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #16'])


ITEM = dict(
    id='divisi-strings-lament',
    title='Lament - string orchestra with divisi (two voices on one staff, and chords)',
    layout='divisi', make=make, pages=1, must_not_split=True,
    expected_notes=('FOUR parts: Violin I, Violin II, Viola, Violoncello. Violin I is "div." in mm.3-4 and mm.7-8: '
                    'two voices on its staff (upper stems up, lower stems down) that BOTH belong to the Violin I '
                    'part (truth: voice 1 and voice 2) - do not create a fifth part. Violin II plays its divisi as '
                    'two-note chords (mm.3-4, 7-8): chords stay chords. "div."/"unis." are words directions.'),
    truth_limitations=['Violin I voice 2 exists only in the divisi measures; elsewhere it is empty (<forward>).'],
    layout_desc='A4 portrait, staff size 19, 2 systems of 4 measures on 4 bracketed staves',
    scans=scans(16, 'T2', 'S5'),
    attribution='Lament for string orchestra composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
