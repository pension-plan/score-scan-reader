"""L5: 'Old Hundredth' hymn page: SATB closed score, verses 1-3; then verse 4 (Doxology) with a
DESCANT on a reduced-size staff above (hidden in the verse 1-3 systems) that opens with cue-size
notes of the melody; finally an 'Amen' engraved as a separate system at a smaller staff size.
Harmonisation by the corpus voice-leading solver (CC0); melody and texts public domain."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from .common import CC0_NOTE, add_mark, mk_part
from lsynth.dsl import parse_voice
from lsynth.harmonize import harmonize
from lsynth.model import MeasureInfo, Score, renumber, set_verses

OLD100_S = ("g'2 | g'4 fis' e' d' | g' a' b'2\\fermata | b'2 b'4 b' | a' g' c'' b' | a'2\\fermata g'2 | "
            "a'4 b' a' g' | e' fis' g'2\\fermata | d''2 b'4 g' | a' c'' b' a' | g'2\\fermata")
OLD100_CH = ['G', 'Em', 'D', 'C', 'G/B', 'C', 'D', 'G',
             'G', 'Em', 'Bm', 'D', 'Em', 'C', 'G', 'D',
             'G', 'D/F#', 'G', 'D', 'Em', 'C', 'D', 'G',
             'G', 'Em', 'C', 'D', 'Am', 'G', 'D7', 'G']
VERSES = [
    "All peo -- ple that on earth do dwell, Sing to the Lord with cheer -- ful voice; "
    "Him serve with fear, his praise forth tell, Come ye be -- fore him and re -- joice.",
    "The Lord, ye know, is God in -- deed; With -- out our aid he did us make; "
    "We are his folk, he doth us feed, And for his sheep he doth us take.",
    "O en -- ter then his gates with praise, Ap -- proach with joy his courts un -- to; "
    "Praise, laud, and bless his name al -- ways, For it is seem -- ly so to do.",
]
DOXOLOGY = ("Praise God, from whom all bless -- ings flow; Praise him, all crea -- tures here be -- low; "
            "Praise him a -- bove, ye heaven -- ly host; Praise Fa -- ther, Son, and Ho -- ly Ghost.")
DESC_PASS2 = ("\\cueOn g'2^\"(melody)\" | g'4 fis' e' d' | g' a' b'2 \\cueOff | d''2\\f g''4 fis'' | fis''4 e'' e'' d'' | "
              "d''2\\fermata b'2 | d''4 d'' fis'' g'' | g''4 a'' b''2\\fermata | b''2 g''4 e'' | fis''4 e'' d'' c'' | "
              "b'2\\fermata")
DESC_TEXT = ("_ _ _ _ _ _ _ _ Praise him, all crea -- tures here be -- low; Praise him a -- bove, ye heaven -- ly host; "
             "Praise Fa -- ther, Son, and Ho -- ly Ghost.")
NPASS = 11     # measures per pass
MAIN_SIZE, AMEN_SIZE = 18, 14


def make():
    sop = parse_voice(OLD100_S)
    alt, ten, bas = harmonize(sop, OLD100_CH, 7)
    amen_s = parse_voice("g'1 | g'1\\fermata")
    a_a, a_t, a_b = harmonize(amen_s, ['C', 'G'], 7)
    desc1 = parse_voice("R2 | R1 | R1 | R1 | R1 | R1 | R1 | R1 | R1 | R1 | R2")
    desc2 = parse_voice(DESC_PASS2)
    desc_amen = parse_voice("R1 | R1")
    voices = {
        'D': desc1 + desc2 + desc_amen,
        'S': sop + copy.deepcopy(sop) + amen_s,
        'A': alt + copy.deepcopy(alt) + a_a,
        'T': ten + copy.deepcopy(ten) + a_t,
        'B': bas + copy.deepcopy(bas) + a_b,
    }
    nm = 2 * NPASS + 2
    sc = Score()
    for i in range(nm):
        d = sum((e.dur for e in voices['S'][i]), F(0))
        sc.measures.append(MeasureInfo(number=i + 1, dur=d, nominal=F(4)))
    sc.measures[0].time, sc.measures[0].time_symbol, sc.measures[0].key = (4, 4), 'common', (1, 'major')
    sc.measures[0].implicit = True
    parts = []
    for pid, name, abbr, clef in (('D', 'Descant', 'Desc.', 'treble'), ('S', 'Soprano', 'S.', 'treble'),
                                  ('A', 'Alto', 'A.', 'treble'), ('T', 'Tenor', 'T.', 'bass'),
                                  ('B', 'Bass', 'B.', 'bass')):
        p = mk_part(pid, name, abbr, 'voice', 1, [clef])
        p.measures = [{'1': m} for m in voices[pid]]
        parts.append(p)
    parts[0].staff_size = 75
    sc.parts = parts
    renumber(sc)
    # lyrics: soprano verses 1-3 (pass 1), verse 4 (pass 2), Amen (line 1)
    n = 32
    skips = ' '.join(['_'] * n)
    v1 = ' '.join([VERSES[0], skips, 'A -- men.'])
    v2 = ' '.join([VERSES[1], skips, '_ _'])
    v3 = ' '.join([VERSES[2], skips, '_ _'])
    v4 = ' '.join([skips, DOXOLOGY, '_ _'])
    set_verses(sc, 'S', '1', [v1, v2, v3, v4], mode='attack')
    set_verses(sc, 'D', '1', [DESC_TEXT], mode='attack')
    # dynamics
    def first_note(pid, i):
        return [e for e in sc.part(pid).measures[i]['1'] if e.kind == 'note'][0]
    for pid in ('S', 'T'):
        first_note(pid, 0).dynamics.append('mf')
        first_note(pid, NPASS).dynamics.append('f')
    first_note('S', 2 * NPASS).words.append(('rall.', 'above', 'italic'))
    first_note('T', 2 * NPASS).dynamics.append('p')
    first_note('S', 2 * NPASS).dynamics.append('p')
    # structure
    add_mark(sc, 0, 'tempo', text='Maestoso', unit='half', bpm=60)
    add_mark(sc, NPASS, 'words', text='Verse 4 (Doxology) - with descant', style='bold')
    sc.measures[NPASS - 1].right_bar = 'double'
    sc.measures[2 * NPASS - 1].right_bar = 'double'
    sc.measures[-1].right_bar = 'final'
    sc.measures[6].brk = 'system'
    sc.measures[NPASS].brk = 'page'
    sc.measures[NPASS + 6].brk = 'system'
    sc.measures[2 * NPASS].brk = 'system'
    pct = round(100 * AMEN_SIZE / MAIN_SIZE)
    sc.measures[2 * NPASS].staff_size = {p: pct for p in ('S', 'A', 'T', 'B')}
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    sc.title = 'Old Hundredth'
    sc.composer = 'Genevan Psalter (1551), attr. Louis Bourgeois'
    sc.lyricist = 'William Kethe (1561); Doxology: Thomas Ken (1674)'
    sc.arranger = 'Harmonisation and descant: layout-challenge corpus (CC0)'
    sc.rights = 'Melody and texts public domain; harmonisation, descant and engraving CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'Old Hundredth'},
                  {'page': 1, 'type': 'subtitle', 'text': 'All people that on earth do dwell'},
                  {'page': 1, 'type': 'lyricist', 'text': 'William Kethe (1561); Doxology: Thomas Ken (1674)'},
                  {'page': 1, 'type': 'composer', 'text': 'Genevan Psalter (1551)'},
                  {'page': 1, 'type': 'text', 'text': 'L.M.'},
                  {'page': 2, 'type': 'page number', 'text': '2'}]
    choir1 = [
        {'id': 'sa', 'clef': 'treble', 'voices': [('S', '1'), ('A', '1')],
         'lyrics': [{'voice': ('S', '1'), 'verses': [1, 2, 3, 4], 'place': 'below', 'stanza': True}]},
        {'id': 'tb', 'clef': 'bass', 'voices': [('T', '1'), ('B', '1')]}]
    choir2 = [
        {'id': 'sa', 'clef': 'treble', 'voices': [('S', '1'), ('A', '1')],
         'lyrics': [{'voice': ('S', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]},
        {'id': 'tb', 'clef': 'bass', 'voices': [('T', '1'), ('B', '1')]}]
    lay = {'segments': [
        {'start': 0, 'end': 2 * NPASS, 'groups': [
            {'type': None, 'staves': [
                {'id': 'desc', 'clef': 'treble', 'name': 'Descant', 'voices': [('D', '1')],
                 'with': ['\\RemoveAllEmptyStaves', '\\magnifyStaff #3/4'],
                 'lyrics': [{'voice': ('D', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]}]},
            {'type': 'ChoirStaff', 'staves': choir1}]},
        {'start': 2 * NPASS, 'end': nm, 'staff_size': AMEN_SIZE,
         'layout_extra': ['\\context { \\Staff \\omit TimeSignature }'],
         'groups': [{'type': 'ChoirStaff', 'staves': choir2}]},
    ]}
    opts = {'header': {'title': 'Old Hundredth', 'subtitle': 'All people that on earth do dwell',
                       'poet': 'William Kethe (1561); Doxology: Thomas Ken (1674)',
                       'composer': 'Genevan Psalter (1551)', 'meter': 'L.M.',
                       'arranger': 'Harmonisation and descant: layout-challenge corpus'},
            'staff_size': MAIN_SIZE, 'paper': 'letter', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'auto_beam_off_vocal': True,
            'paper_extra': ['indent = 0', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #16',
                            'score-system-spacing.basic-distance = #14'],
            'layout_extra': ['\\context { \\Score \\remove "Bar_number_engraver" }']}
    return sc, lay, opts


ITEM = dict(
    id='hymn-descant-cue-notes-amen-small',
    title='Old Hundredth - closed SATB, reduced-size descant staff with cue notes, Amen at a smaller staff size',
    make=make, pages=2,
    edge_cases=['satb_closed_score', 'descant_small_staff', 'mixed_staff_sizes_on_page', 'cue_notes',
                'amen_smaller_staff_size', 'separate_score_block', 'hidden_empty_staff',
                'systems_with_different_staff_counts', 'multi_verse', 'stanza_number_labels', 'lyrics',
                'split_measures_between_passes', 'pickup', 'fermata', 'tempo_text', 'section_heading_text',
                'page_numbers'],
    must_not_split=False,
    shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
    expected_notes=('Five parts: Descant, Soprano, Alto, Tenor, Bass. S+A share the treble staff and T+B the bass '
                    'staff (closed score - split by stem direction). The Descant staff (75 % size) is hidden in the '
                    'verse 1-3 systems (truth: invisible measure rests) and appears for verse 4; its first three '
                    'measures are CUE-SIZE notes of the melody (encoded <cue/>, not sung): a correct conversion '
                    'marks them as cue notes or omits them (rests) - they must not become sounding Descant notes '
                    'and carry no lyrics. The hymn is written out twice (verses 1-3, then verse 4 + descant: the '
                    'last bar of pass 1 and the pickup of pass 2 are both 2-beat measures). The final "Amen" (2 '
                    'measures) is a separate smaller system (78 % staff size) continuing the S/A/T/B parts; the '
                    'Descant has invisible rests there. Lyrics: Soprano lines 1-3 in pass 1, line 4 (Doxology) in '
                    'pass 2, line 1 "A-men"; Descant line 1 from its 4th measure.'),
    truth_limitations=('Cue notes are encoded with <cue/> and <type size="cue"> (they have no MIDI meaning). '
                       'Staff sizes are <staff-details><staff-size> percentages. Stanza labels ("1."-"4.") are not '
                       'encoded. Lyrics under the S+A staff are attached to Soprano only. The Amen is engraved as a '
                       'second LilyPond \\score; in the truth it simply continues the parts.'),
    layout_desc='US letter, staff size 18; page 1: title + 2 closed-score systems (3 verses); page 2: 2 systems '
                'with the 75 % descant staff, then the Amen system at staff size 14',
    license='Melody and texts public domain; harmonisation, descant and engraving CC0-1.0',
    source='self-authored harmonisation/descant (layout-challenge corpus); melody Genevan Psalter 1551, texts '
           'W. Kethe 1561 and T. Ken 1674',
    attribution='\n'.join(['Old Hundredth. Melody: Genevan Psalter (1551), attr. Louis Bourgeois - public domain.',
                           'Text: William Kethe (1561); Doxology: Thomas Ken (1674) - public domain.',
                           'SATB harmonisation (corpus voice-leading solver), descant and Amen - CC0 1.0.', '',
                           CC0_NOTE]),
)
