"""L6: Minuet and Trio for violin, violoncello and piano, printed as a piano score: the two string
staves are reduced (75 %) and joined by a BRACKET (treble + bass - visually a 'grand staff' that must
NOT be merged into one part) above the piano grand staff joined by a BRACE (one part).  Menuetto with
'Fine', Trio in another key ending 'Menuetto D.C. al Fine'; instrument names only on the first system."""
from __future__ import annotations

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, bass_note, chord_ly, close_chord, mk_part

CHORDS = ['G', 'D7', 'G', 'D', 'G', 'C', 'D7', 'G', 'D', 'A7', 'D', 'D7', 'G', 'C', 'D7', 'G',
          'C', 'G7', 'C', 'G', 'F', 'C', 'G7', 'C', 'G', 'C', 'D7', 'G', 'C', 'F', 'G7', 'C']
VIOLIN = ("d''2\\p b'4 | c''4 a' fis' | g'8( a' b' c'') d''4 | e''4( d''2) | b'4 d'' g'' | e''4 c'' g' | "
          "fis'8( g' a' b' c'' a') | g'2 r4 | "
          "a'4\\f d'' fis'' | e''4 cis'' a' | d''8( e'' fis'' g'') a''4 | c''4 a' fis' | g'4\\p b' d'' | "
          "e''4 g'' e'' | d''8( c'' b' a' c'' a') | g'2. | "
          "e''2\\mf^\"dolce\" g''4 | f''4 d'' b' | c''4 e'' g'' | d''2. | a''4 f'' c'' | g''4 e'' c'' | "
          "d''8( e'' f'' d'' b' g') | c''2 r4 | "
          "b'4 d'' g'' | g''4 e'' c'' | fis''4 d'' c'' | d''2 r4 | e''4\\< g'' c''' | a''4\\!\\f f'' c'' | "
          "b'8( c'' d'' f'' e'' d'') | c''2.")
CELLO = ("g,4\\p b, d | fis,2 d,4 | g,4 b, g, | d,4 fis, a, | g,2. | c4 e c | d4 c d, | g,2 r4 | "
         "d4\\f fis a | a,4 cis e | d2. | c2 a,4 | b,4\\p d g | c4 e g | d2 d,4 | g,2. | "
         "c2.\\mf | b,2 g,4 | c4 e g | g,2. | f,4 a, c | e,4 g, c | g,2 f,4 | c2 r4 | "
         "g,4 b, d | c4 e g | fis,2 d,4 | g,2 r4 | c4\\< e g | f,4\\!\\f a, c | g,4 f, g, | c2.")


def piano():
    rh, lh = [], []
    for i, sym in enumerate(CHORDS):
        c = chord_ly(close_chord(sym, 67, 3))
        b = bass_note(sym, 43, 54)
        lo = (b[0], b[1], b[2] - 1)
        r = f'r4 {c}4-. {c}4-.'
        l = f'{chord_ly([lo, b])}4 r4 r4'
        if i in (0, 12, 16, 24):
            r = r.replace('4-.', '4-.\\p', 1) if i in (0, 12) else r.replace('4-.', '4-.\\mf', 1)
        if i == 8:
            r = r.replace('4-.', '4-.\\f', 1)
        rh.append(r)
        lh.append(l)
    return ' | '.join(rh), ' | '.join(lh)


def make():
    rh, lh = piano()
    vn = mk_part('VN', 'Violin', 'Vn.', 'other', 1, ['treble'])
    vc = mk_part('VC', 'Violoncello', 'Vc.', 'other', 1, ['bass'])
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((3, 4), (1, 'major'), [(vn, {'1': VIOLIN}), (vc, {'1': CELLO}), (pn, {'1': rh, '5': lh})])
    vn.staff_size = 75
    vc.staff_size = 75
    add_mark(sc, 0, 'tempo', text='Tempo di Menuetto', unit='quarter', bpm=120)
    add_mark(sc, 0, 'words', text='Menuetto', style='bold')
    sc.measures[7].right_bar = 'repeat-end'
    sc.measures[8].left_bar = 'repeat-start'
    sc.measures[15].right_bar = 'repeat-end'
    add_end_mark(sc, 15, 'Fine', style='bold-italic', sound={'fine': 'yes'})
    sc.measures[16].left_bar = 'repeat-start'
    sc.measures[16].key = (0, 'major')
    add_mark(sc, 16, 'words', text='Trio', style='bold')
    sc.measures[23].right_bar = 'repeat-end'
    sc.measures[24].left_bar = 'repeat-start'
    sc.measures[31].right_bar = 'repeat-end'
    add_end_mark(sc, 31, 'Menuetto D.C. al Fine', style='bold-italic', sound={'dacapo': 'yes'})
    for i in (4, 8, 12, 20, 24, 28):
        sc.measures[i].brk = 'system'
    sc.measures[16].brk = 'page'
    sc.groups = [{'first': 'VN', 'last': 'VC', 'symbol': 'bracket'}]
    sc.title = 'Minuet and Trio'
    sc.composer = 'Layout-challenge corpus (2026), CC0'
    sc.rights = 'Dedicated to the public domain (CC0 1.0)'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'Minuet and Trio'},
                  {'page': 1, 'type': 'subtitle', 'text': 'for violin, violoncello and piano'},
                  {'page': 1, 'type': 'text', 'text': 'Piano score'},
                  {'page': 1, 'type': 'composer', 'text': 'Layout-challenge corpus (2026)'},
                  {'page': 1, 'type': 'rights', 'text': 'Dedicated to the public domain (CC0 1.0)'},
                  {'page': 2, 'type': 'page number', 'text': '2'}]
    small = ['\\magnifyStaff #3/4']
    lay = {'groups': [
        {'type': 'StaffGroup', 'staves': [
            {'id': 'vn', 'clef': 'treble', 'name': 'Violin', 'voices': [('VN', '1')], 'with': small},
            {'id': 'vc', 'clef': 'bass', 'name': 'Violoncello', 'voices': [('VC', '1')], 'with': small}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]},
    ]}
    opts = {'header': {'title': 'Minuet and Trio', 'subtitle': 'for violin, violoncello and piano',
                       'subsubtitle': 'Piano score', 'composer': 'Layout-challenge corpus (2026)',
                       'copyright': 'Dedicated to the public domain (CC0 1.0)'},
            'staff_size': 17, 'paper': 'letter', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'paper_extra': ['left-margin = 24\\mm', 'indent = 22\\mm', 'short-indent = 0', 'ragged-bottom = ##t',
                            'system-system-spacing.basic-distance = #12', 'top-margin = 12\\mm',
                            'bottom-margin = 12\\mm'],
            'layout_extra': []}
    return sc, lay, opts


ITEM = dict(
    id='trio-minuet-bracket-vs-brace-dc',
    title='Minuet and Trio - reduced string staves in a bracket above a braced piano, Fine / D.C. al Fine',
    make=make, pages=2,
    edge_cases=['bracket_vs_brace', 'bracketed_treble_bass_pair_is_two_parts', 'mixed_staff_sizes_on_page',
                'reduced_instrument_staves', 'instrument_names_first_system_only', 'piano_grand_staff',
                'must_not_split', 'dc_al_fine', 'fine', 'repeats', 'key_change', 'section_heading_text',
                'tempo_text', 'dynamics_text', 'hairpin', 'staccato', 'slurs', 'page_numbers'],
    must_not_split=True,
    expected_notes=('Three parts: Violin (small treble staff), Violoncello (small bass staff) and Piano (normal-size '
                    'grand staff, ONE part). The violin and cello staves form a treble+bass pair joined by a '
                    'BRACKET - they are two separate instruments and must NOT be merged into one two-staff part; '
                    'the piano staves are joined by a BRACE and must NOT be split. Instrument names appear only on '
                    'the first system. Menuetto (mm. 1-16, repeats, "Fine" after m.16), Trio (mm. 17-32, C major, '
                    'repeats, "Menuetto D.C. al Fine" after m.32) - notated order, not unrolled.'),
    truth_limitations=('Beaming not encoded. Reduced staves are <staff-details><staff-size>75</staff-size>. '
                       'The D.C./Fine semantics are <sound dacapo="yes"/> and <sound fine="yes"/>.'),
    layout_desc='US letter, staff size 17 (strings 75 %), 4 systems of 4 staves per page, Trio on page 2',
    license='CC0-1.0 (composition, engraving, scans)',
    source='self-authored (layout-challenge corpus)',
    attribution='\n'.join(['Minuet and Trio for violin, violoncello and piano, composed for this corpus - CC0 1.0.',
                           '', CC0_NOTE]),
)
