"""orchestral: a 9-staff full-score excerpt (woodwinds bracket, trumpet, timpani, strings bracket with a
square sub-bracket on the violins), one system per page, two pages."""
from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

FL = ("fis''4\\f a'' fis'' d'' | e''4 g'' e'' cis'' | d''8 e'' fis'' g'' a''4 a'' | a''2 r2 | "
      "b''4.\\mf a''8 g''4 b'' | a''4 fis'' e''8 fis'' g'' e'' | d''4\\< fis''8 e'' d''4 b' | d''1\\!\\ff\\fermata")
OB = ("d''4\\f fis'' d'' a' | cis''4 e'' cis'' a' | a'8 cis'' d'' e'' fis''4 fis'' | e''2 r2 | "
      "d''4.\\mf d''8 d''4 d'' | d''4 d'' cis''2 | a'4\\< d''8 cis'' b'4 g' | a'1\\!\\ff\\fermata")
BN = ("d4\\f d d d | a,4 a, a, a, | d4 d d d | a,2 r2 | "
      "g,4\\mf g, g, g, | a,4 a, a,2 | d4\\< d g, g, | d1\\!\\ff\\fermata")
TP = ("d''4\\f d'' d'' d'' | a'4 a' a' a' | d''4 d''8 d'' d''4 d'' | a'2 r2 | "
      "R1 | R1 | d''4\\< d'' d'' d'' | d''1\\!\\ff\\fermata")
TI = ("d4\\f r4 a,4 r4 | a,4 r4 a,4 r4 | d4 r4 d4 r4 | a,2 r2 | "
      "R1 | a,4\\mf r4 a,4 r4 | d4\\< r4 d4 r4 | d1\\!\\ff\\fermata")
V1 = ("a'8\\f d'' fis'' a'' d'''4 a'' | g''8 e'' cis'' a' e''4 cis'' | d''16 e'' fis'' g'' a''8 a'' d'''4 a'' | "
      "<cis'' a''>2 r2 | b''8\\mf a'' g'' fis'' g''4 b'' | a''8 g'' fis'' e'' e''2 | d''8\\< e'' fis'' d'' b'4 g'' | "
      "<d'' fis''>1\\!\\ff\\fermata")
V2 = ("fis'8\\f a' d'' fis'' a''4 fis'' | e''8 cis'' a' g' cis''4 a' | a'16 cis'' d'' e'' fis''8 fis'' a''4 fis'' | "
      "<e' a'>2 r2 | g''8\\mf fis'' e'' d'' d''4 g'' | fis''8 e'' d'' cis'' cis''2 | a'8\\< cis'' d'' a' g'4 d'' | "
      "<a' d''>1\\!\\ff\\fermata")
VA = ("d'4\\f d' d' d' | e'4 e' e' e' | d'4 d'8 d' d'4 d' | e'2 r2 | "
      "d'4\\mf d' d' d' | a4 a a2 | a4\\< a8 a d'4 d' | d'1\\!\\ff\\fermata")
VC = ("d4\\f d d d | a,4 a, a, a, | d4 d8 d d4 d | a,2 r2 | "
      "g,4\\mf g, g, g, | a,4 a, a,2 | d4\\< d g, g, | d,1\\!\\ff\\fermata")

INSTR = [('FL', 'Flute', 'Fl.', 'treble', FL), ('OB', 'Oboe', 'Ob.', 'treble', OB), ('BN', 'Bassoon', 'Bn.', 'bass', BN),
         ('TP', 'Trumpet in C', 'Tpt.', 'treble', TP), ('TI', 'Timpani', 'Timp.', 'bass', TI),
         ('V1', 'Violin I', 'Vn. I', 'treble', V1), ('V2', 'Violin II', 'Vn. II', 'treble', V2),
         ('VA', 'Viola', 'Va.', 'alto', VA), ('VC', 'Violoncello', 'Vc.', 'bass', VC)]


def make():
    parts = [mk_part(pid, nm, sh, 'other', 1, [clef]) for pid, nm, sh, clef, _ in INSTR]
    sc = assemble((4, 4), (2, 'major'), [(p, {'1': src}) for p, (_, _, _, _, src) in zip(parts, INSTR)])
    add_mark(sc, 0, 'tempo', text='Allegro marziale', unit='quarter', bpm=116)
    add_mark(sc, 4, 'rehearsal', text='B')
    breaks(sc, pages=(4,))
    sc.groups = [{'first': 'FL', 'last': 'BN', 'symbol': 'bracket'},
                 {'first': 'V1', 'last': 'VC', 'symbol': 'bracket'},
                 {'first': 'V1', 'last': 'V2', 'symbol': 'square'}]
    hdr = header(sc, 'Festive March', 'full score (excerpt)',
                 extra_credits=[{'page': 2, 'type': 'page number', 'text': '2'}])

    def st(pid, nm, sh, clef):
        return {'id': pid.lower(), 'clef': clef, 'name': nm, 'short': sh, 'voices': [(pid, '1')]}
    s = {pid: st(pid, nm, sh, clef) for pid, nm, sh, clef, _ in INSTR}
    lay = {'groups': [
        {'type': 'StaffGroup', 'staves': [s['FL'], s['OB'], s['BN']]},
        {'type': None, 'staves': [s['TP']]},
        {'type': None, 'staves': [s['TI']]},
        {'type': 'StaffGroup', 'staves': [
            {'type': 'GrandStaff', 'with': ["systemStartDelimiter = #'SystemStartSquare"],
             'staves': [s['V1'], s['V2']]},
            s['VA'], s['VC']]}]}
    return sc, lay, opts(hdr, 15, extra_paper=['indent = 22\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #14',
                                                'print-page-number = ##t', 'print-first-page-number = ##f'])


ITEM = dict(
    id='orchestral-festive-march-9-staves',
    title='Festive March - 9-staff orchestral full score, two pages',
    layout='orchestral', make=make, pages=2, must_not_split=True,
    expected_notes=('NINE parts, one per staff: Flute, Oboe, Bassoon (bracketed woodwinds), Trumpet in C (written at '
                    'sounding pitch, no transposition), Timpani, Violin I, Violin II (square sub-bracket inside the '
                    'strings bracket), Viola (alto clef), Violoncello. One system per page; page 2 uses short names. '
                    'Violin double stops in m.4/m.8 are chords. Trumpet and timpani have whole-bar rests.'),
    truth_limitations=['Part groups: woodwinds bracket, strings bracket, violins square (nested part-group); '
                       'trumpet and timpani are not grouped.'],
    layout_desc='A4 portrait, staff size 15, page 1: title + one 9-staff system (mm.1-4), page 2: one system '
                '(mm.5-8) with abbreviated names',
    scans=scans(13, 'T4', 'S3'),
    attribution='Festive March (full-score excerpt) composed for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
