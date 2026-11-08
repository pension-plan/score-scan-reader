"""L3: 'Nun danket alle Gott' for organ on three staves (manuals with a brace + pedal staff),
landscape A4.  Manualiter introduction (the pedal staff is hidden in that system), Bach's
harmonisation (BWV 252) laid out S+A on manual I, T on manual II, B in the pedal, the Stollen
repeat written with 1st/2nd endings, registration texts, and a final page holding one system."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from music21 import corpus

from .common import CC0_NOTE, add_mark
from lsynth.dsl import parse_voice
from lsynth.m21import import from_music21
from lsynth.model import MeasureInfo, Part, Score, VoiceDef, renumber

INTRO = {
    '1': ("b'8^\"Man._II:_Gedackt_8',_Flöte_4'\" c'' d''4 d'' e''8 fis'' | g''4 fis''8 e'' d''2 | "
          "e''8 d'' c'' b' a'4 d''4"),
    '2': "s1 | s1 | s2. g'4",
    '5': "g4_\"manualiter\" b d' a | b4 a8 g fis2 | c'4 g d' <g b>4",
    '9': "R1 | R1 | R1",
}
POST = {
    '1': "c''1^\"Man._II\" | b'1\\fermata^\"rit.\"",
    '2': "g'2 a'2 | g'1\\fermata",
    '5': "e'1 | d'1\\fermata",
    '9': "g,1~ | g,1\\fermata",
}


def chorale():
    s = corpus.parse('bach/bwv252')
    sc = from_music21(s, [{'src': [2], 'id': 'S', 'name': 'Soprano'}, {'src': [3], 'id': 'A', 'name': 'Alto'},
                          {'src': [4], 'id': 'T', 'name': 'Tenor'}, {'src': [5], 'id': 'B', 'name': 'Bass'}])
    out = {p.id: [m['1'] for m in p.measures] for p in sc.parts}
    for ms in out.values():          # organ arrangement: no text, no dynamics from the vocal source
        for evs in ms:
            for e in evs:
                e.lyrics = {}
                e.dynamics = []
    return out


def make():
    ch = chorale()
    # re-bar into full 4/4 bars: 1 2 3 | e1 = 4a+0 | e2 = 4a+5 | 6 7 8 | 9+10 | 11 12 13 | 14 (extended)
    plan = [[1], [2], [3], [4, 0], [4, 5], [6], [7], [8], [9, 10], [11], [12], [13], [14]]
    vmap = {'S': '1', 'A': '2', 'T': '5', 'B': '9'}
    intro = {k: parse_voice(v) for k, v in INTRO.items()}
    post = {k: parse_voice(v) for k, v in POST.items()}
    org = Part(id='O', name='Organ', abbr='Org.', instrument='piano', staves=3, clefs=['treble', 'bass', 'bass'])
    org.voices = [VoiceDef('1', 1), VoiceDef('2', 1), VoiceDef('5', 2), VoiceDef('9', 3)]
    org.part_symbol = ('brace', 1, 2)
    measures = []
    for i in range(3):
        measures.append({k: intro[k][i] for k in vmap.values()})
    for src in plan:
        mm = {}
        for pid, vk in vmap.items():
            evs = []
            for j in src:
                evs += copy.deepcopy(ch[pid][j])
            mm[vk] = evs
        measures.append(mm)
    # extend the final chorale chord to a whole note
    for vk, evs in measures[-1].items():
        last = [e for e in evs if e.kind == 'note'][-1]
        tot = sum((e.dur for e in evs), F(0))
        last.dur += F(4) - tot
        last.dtype, last.dots = 'whole', 0
    for i in range(2):
        measures.append({k: post[k][i] for k in vmap.values()})
    org.measures = measures
    sc = Score()
    for i in range(len(measures)):
        mi = MeasureInfo(number=i + 1, dur=F(4), nominal=F(4))
        sc.measures.append(mi)
    sc.measures[0].time, sc.measures[0].key = (4, 4), (1, 'major')
    sc.parts = [org]
    renumber(sc)
    # structure
    sc.measures[3].left_bar = 'repeat-start'
    sc.measures[6].volta_start, sc.measures[6].volta_end, sc.measures[6].right_bar = '1', 'stop', 'repeat-end'
    sc.measures[7].volta_start, sc.measures[7].volta_end = '2', 'discontinue'
    sc.measures[15].right_bar = 'double'
    sc.measures[-1].right_bar = 'final'
    add_mark(sc, 0, 'tempo', text='Andante maestoso', unit='half', bpm=48)
    add_mark(sc, 16, 'words', text='Coda', style='bold')
    # registration texts at the pedal entry
    first_s = [e for e in measures[3]['1'] if e.kind == 'note'][0]
    first_s.words.append(("Man. I: Principal 8', Octave 4'", 'above', 'italic'))
    first_b = [e for e in measures[3]['9'] if e.kind == 'note'][0]
    first_b.words.append(("Ped.: Subbass 16', Octavbass 8'", 'above', 'italic'))
    # systems: 1-3 | 4-8 || 9-11 | 12-14 || 15-18
    sc.measures[3].brk = 'system'
    sc.measures[8].brk = 'page'
    sc.measures[11].brk = 'system'
    sc.measures[14].brk = 'page'
    sc.title = 'Nun danket alle Gott'
    sc.composer = 'Melody: Johann Crüger (1647); harmonisation: J. S. Bach (BWV 252)'
    sc.arranger = 'Organ layout, introduction and coda: layout-challenge corpus (CC0)'
    sc.rights = 'Public domain composition; layout and engraving CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'Nun danket alle Gott'},
                  {'page': 1, 'type': 'subtitle', 'text': 'Chorale for organ (manuals and pedal)'},
                  {'page': 1, 'type': 'composer', 'text': 'J. S. Bach, BWV 252 (melody J. Crüger, 1647)'},
                  {'page': 1, 'type': 'arranger', 'text': 'Organ layout: layout-challenge corpus'},
                  {'page': 2, 'type': 'page number', 'text': '2'},
                  {'page': 3, 'type': 'page number', 'text': '3'}]
    lay = {'groups': [
        {'type': 'PianoStaff', 'name': 'Organ', 'staves': [
            {'id': 'man1', 'clef': 'treble', 'voices': [('O', '1'), ('O', '2')]},
            {'id': 'man2', 'clef': 'bass', 'voices': [('O', '5')]}]},
        {'type': None, 'staves': [
            {'id': 'ped', 'clef': 'bass', 'name': 'Pedal', 'short': 'Ped.', 'voices': [('O', '9')],
             'with': ['\\RemoveAllEmptyStaves']}]},
    ]}
    opts = {'header': {'title': 'Nun danket alle Gott', 'subtitle': 'Chorale for organ (manuals and pedal)',
                       'composer': 'J. S. Bach, BWV 252 (melody J. Crüger, 1647)',
                       'arranger': 'Organ layout: layout-challenge corpus'},
            'staff_size': 19, 'paper': 'a4landscape', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'paper_extra': ['left-margin = 24\\mm', 'indent = 20\\mm', 'ragged-bottom = ##t', 'ragged-last-bottom = ##t',
                            'system-system-spacing.basic-distance = #18'],
            'layout_extra': []}
    return sc, lay, opts


ITEM = dict(
    id='organ-chorale-3-staves-landscape',
    title='Nun danket alle Gott - organ on 3 staves (pedal), landscape, manualiter system, 1st/2nd endings',
    make=make, pages=3,
    edge_cases=['organ_three_staves', 'pedal_staff', 'brace_on_manuals_only', 'landscape_page',
                'hidden_empty_staff', 'systems_with_different_staff_counts', 'single_system_page',
                'two_voices_on_manual_staff', 'volta_1st_2nd_endings', 'repeats', 'registration_text',
                'tempo_text', 'must_not_split', 'fermata', 'page_numbers'],
    must_not_split=True,
    expected_notes=('One part: Organ with THREE staves (manual I treble, manual II bass, pedal bass). Manual I '
                    'carries two voices (soprano stems up, alto stems down) that must stay in the organ part - '
                    'this is not closed-score choir music. The brace joins only the two manual staves; the pedal '
                    'staff is outside the brace but still belongs to the same Organ part. System 1 (mm. 1-3, '
                    'manualiter) has no pedal staff at all; the truth carries invisible whole-measure rests '
                    '(print-object="no") for the pedal there. Endings: m.7 = 1st ending (with repeat), m.8 = 2nd '
                    'ending; notated order, not unrolled. Registration texts and "manualiter" are words, not '
                    'lyrics. Page 3 holds exactly one system.'),
    truth_limitations=('Beaming not encoded. The pedal rests of the hidden system are encoded as '
                       '<note print-object="no"><rest measure="yes"/>. Registration texts are <words> '
                       'directions. Organ represented as ONE part with 3 staves (<staves>3</staves>, '
                       '<part-symbol top-staff="1" bottom-staff="2">brace</part-symbol>).'),
    layout_desc='A4 landscape, staff size 19; page 1: title + system 1 (2 staves, pedal hidden) + system 2 '
                '(3 staves); page 2: two 3-staff systems; page 3: one system',
    license='Public domain composition (Crüger 1647 / Bach BWV 252); intro, coda, layout and engraving CC0-1.0',
    source='music21 corpus bach/bwv252.mxl (soprano, alto, tenor, bass parts) + self-authored intro/coda',
    attribution='\n'.join([
        'J. S. Bach, chorale "Nun danket alle Gott" BWV 252 - public domain; melody Johann Crüger (1647).',
        'Encoding: music21 corpus (from Margaret Greentree\'s jsbchorales.net MusicXML, "used by permission").',
        'Organ layout, manualiter introduction and 2-bar coda: layout-challenge corpus - CC0 1.0.', '', CC0_NOTE]),
)
