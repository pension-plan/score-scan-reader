"""The 4 simple source pieces of the degradation-extremes challenge set.

Every piece is built with the (copied) synthetic-corpus model, so truth.musicxml
and engraving.ly come from the same score object; build_piece() validates the
LilyPond output against the truth (MIDI attack multiset, MIDI lyric events,
lyric text in the vector PDF) before any damage is applied.

Licensing: melodies/texts are public domain (New Britain 1829 / Newton 1779,
"Ah! vous dirai-je, maman" c. 1761, Rossetti 1872); all settings, harmonisations,
the piano piece and the engravings are original to this corpus and CC0-1.0.
"""
from __future__ import annotations

import copy

from synth.dsl import build_score
from synth.harmonize import harmonize
from synth.items import closed_layout, choir_group
from synth.model import Part, VoiceDef, set_verses

CC0_NOTE = ('Setting, engraving, rasterisation and damage simulation produced for the OMR challenge corpus '
            '(corpus/challenge/degradation/_tools); these files are dedicated to the public domain (CC0 1.0).')


# ---------------------------------------------------------------- P1: SATB closed hymn
AG_S = ("d'4 | g'2 b'8( g'8) | b'2 a'4 | g'2 e'4 | d'2 d'4 | g'2 b'8( g'8) | b'2 a'4 | d''2.~ | d''2 b'4 | "
        "d''4.( b'8) d''8( b'8) | g'2 d'4 | e'4.( g'8) g'8( e'8) | d'2 d'4 | g'2 b'8( g'8) | b'2 a'4 | g'2.~ | g'2")
AG_CH = ['G',
         'G', '-', '~', 'Em', 'D', 'C', '-', 'G', 'G/B',
         'G', 'Em', '~', 'Em', 'D', 'D', '~', 'G',
         'G', '~', 'G/B', '~', 'C', 'G', 'Em', '~', 'C', '~', 'G', 'D',
         'G', 'Em', '~', 'G/D', 'D7', 'G', '~']
AG_V = [
    "A -- ma -- zing _ grace! how sweet the sound That saved a _ wretch like me! "
    "I once _ was _ lost, but now _ am _ found, Was blind, but _ now I see.",
    "'Twas grace that _ taught my heart to fear, And grace my _ fears re -- lieved; "
    "How pre -- _ cious _ did that grace _ ap -- _ pear The hour I _ first be -- lieved!",
    "Through ma -- ny _ dan -- gers, toils, and snares, I have al -- _ rea -- dy come; "
    "'Tis grace _ hath _ brought me safe _ thus _ far, And grace will _ lead me home.",
]


def mk_hymn():
    sc = build_score({'S': AG_S}, time=(3, 4), key=(1, 'major'),
                     parts=[{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'voice': 'S'}])
    smeas = [m['1'] for m in sc.part('S').measures]
    a, t, b = harmonize(smeas, AG_CH, 7)
    for pid, name, abbr, clef, meas in (('A', 'Alto', 'A.', 'treble', a), ('T', 'Tenor', 'T.', 'bass', t),
                                        ('B', 'Bass', 'B.', 'bass', b)):
        p = Part(id=pid, name=name, abbr=abbr, clefs=[clef], voices=[VoiceDef('1', 1)])
        p.measures = [{'1': m} for m in meas]
        sc.parts.append(p)
    set_verses(sc, 'S', '1', AG_V, mode='attack')
    sc.title = 'Amazing Grace'
    sc.composer = 'NEW BRITAIN (American folk melody, 1829)'
    sc.lyricist = 'John Newton (1779)'
    sc.arranger = 'SATB setting generated for this corpus (CC0)'
    sc.rights = 'Public domain melody and text; setting CC0'
    choir_group(sc, 'S', 'B')
    lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                        [(('S', '1'), [1, 2, 3], 'below')])
    opts = {'header': {'title': 'Amazing Grace', 'poet': 'John Newton, 1779',
                       'composer': 'NEW BRITAIN  C.M.', 'arranger': 'American folk melody, 1829'},
            'staff_size': 20, 'paper': 'a4', 'font': 'TeX Gyre Schola',
            'paper_extra': ['indent = 0', 'system-count = 4', 'system-system-spacing.basic-distance = #16',
                            'top-margin = 15\\mm', 'left-margin = 16\\mm', 'right-margin = 16\\mm'],
            'auto_beam_off_vocal': True}
    return sc, lay, opts


# ---------------------------------------------------------------- P2: melody with 2 verses
WIND_S = ("c'4 | f'4 f'4 g'4 | a'2 a'4 | c''4 bes'4 a'4 | g'2 c'4 | f'4 g'4 a'4 | bes'4 d''4. c''8 | "
          "a'2 g'4 | c''4 bes'4 a'4 | g'2( e'4) | f'2")
WIND_V = [
    # verse 1 has one syllable fewer in line 3: "trem" is held over two notes
    "Who has seen the wind? Nei -- ther I nor you: But when the leaves hang trem -- _ bling, "
    "The wind is pass -- ing _ through.",
    "Who has seen the wind? Nei -- ther you nor I: But when the trees bow down their heads, "
    "The wind is pass -- ing _ by.",
]


def mk_melody():
    sc = build_score({'M': WIND_S}, time=(3, 4), key=(-1, 'major'),
                     parts=[{'id': 'V', 'name': 'Voice', 'abbr': '', 'voice': 'M'}])
    set_verses(sc, 'V', '1', WIND_V, mode='attack')
    sc.title = 'Who Has Seen the Wind?'
    sc.composer = 'Melody composed for this corpus (CC0)'
    sc.lyricist = 'Christina Rossetti (1872)'
    sc.rights = 'Text public domain; melody and engraving CC0'
    opts = {'header': {'title': 'Who Has Seen the Wind?', 'poet': 'Christina Rossetti, 1872',
                       'composer': 'Melody: corpus (CC0)'},
            'staff_size': 24, 'paper': 'a4', 'font': 'TeX Gyre Bonum',
            'paper_extra': ['indent = 0', 'system-count = 4', 'top-margin = 20\\mm',
                            'system-system-spacing.basic-distance = #22'],
            'auto_beam_off_vocal': True}
    lay = {'groups': [{'type': None, 'staves': [
        {'id': 'voice', 'clef': 'treble', 'voices': [('V', '1')],
         'lyrics': [{'voice': ('V', '1'), 'verses': [1, 2], 'place': 'below'}]}]}]}
    return sc, lay, opts


# ---------------------------------------------------------------- piano helpers
def piano_score(rh_voices, lh_voices, time, key, title, composer):
    """rh_voices / lh_voices: list of DSL strings (1 or 2 voices per staff).
    Builds a single 'Piano' part with 2 staves (voice keys 1,2 on staff 1 and
    5,6 on staff 2)."""
    names = {}
    for i, txt in enumerate(rh_voices):
        names[f'R{i}'] = txt
    for i, txt in enumerate(lh_voices):
        names[f'L{i}'] = txt
    tmp = build_score(names, time=time, key=key,
                      parts=[{'id': k, 'name': k, 'voice': k} for k in names])
    p = Part(id='P', name='Piano', abbr='Pno.', instrument='piano', staves=2, clefs=['treble', 'bass'])
    nm = len(tmp.measures)
    p.measures = [dict() for _ in range(nm)]
    for staff, prefix, base in ((1, 'R', 1), (2, 'L', 5)):
        for i, k in enumerate([x for x in names if x.startswith(prefix)]):
            vk = str(base + i)
            p.voices.append(VoiceDef(vk, staff))
            for j in range(nm):
                p.measures[j][vk] = copy.deepcopy(tmp.part(k).measures[j]['1'])
    tmp.parts = [p]
    tmp.groups = []
    tmp.title, tmp.composer = title, composer
    return tmp


def piano_layout(rh_keys, lh_keys):
    return {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'pu', 'clef': 'treble', 'voices': [('P', k) for k in rh_keys], 'lyrics': []},
        {'id': 'pl', 'clef': 'bass', 'voices': [('P', k) for k in lh_keys], 'lyrics': []}]}]}


# ---------------------------------------------------------------- P3: short piano piece (CC0)
# D major, 4/4, 16 bars; right hand splits into two voices in bars 13-16.
AND_RH1 = ("a'4\\p( d''4 fis''4 e''4) | d''4( cis''8 b'8) a'2 | b'4( d''4 g''4 fis''4) | e''2 r4 a'4 | "
           "a'4( d''4 fis''4 a''4) | g''4( fis''8 e''8) d''4 b'4 | a'4-. d''4-. e''4-. cis''4-. | d''2. r4 | "
           "fis''4\\mf( g''8 a''8 g''4 fis''4) | e''4( fis''8 g''8 fis''4 e''4) | d''4( e''8 fis''8 e''4 d''4) | "
           "cis''2 a'2 | a''2\\f( g''4 fis''4) | e''2 d''4 cis''4 | d''4 fis''4 e''4 cis''4 | d''1\\fermata")
AND_RH2 = ("s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | "
           "d''2 cis''2 | b'2 a'4 g'4 | fis'4 a'4 g'4 e'4 | fis'1")
AND_LH = ("d4 <fis a>4 a,4 <fis a>4 | d4 <fis a>4 a,4 <fis a>4 | g,4 <g b>4 d4 <g b>4 | a,4 <e g cis'>4 a,4 r4 | "
          "d4 <fis a>4 a,4 <fis a>4 | g,4 <g b>4 g,4 <g b>4 | a,4-. a,4-. a,4-. a,4-. | d2. r4 | "
          "d4 <a d'>4 d4 <a d'>4 | a,4 <a cis'>4 a,4 <a cis'>4 | b,4 <fis b>4 b,4 <fis b>4 | a,2 <e a cis'>2 | "
          "d2 a,2 | g,2 a,2 | d2 a,2 | <d, d>1\\fermata")


def mk_piano_short():
    # the DSL has no spacer token: voice 2 is written with whole rests in bars
    # 1-12, which are then replaced by invisible 'space' events
    from fractions import Fraction as F

    from synth.model import Event
    rh2 = AND_RH2.replace('s1 | ', 'r1 | ')
    sc = piano_score([AND_RH1, rh2], [AND_LH], (4, 4), (2, 'major'), 'Andantino',
                     'Corpus composition (CC0)')
    p = sc.part('P')
    for j in range(12):
        p.measures[j]['2'] = [Event('space', F(4))]
    sc.rights = 'CC0 (original composition for this corpus)'
    opts = {'header': {'title': 'Andantino', 'subtitle': 'for piano', 'composer': 'Corpus composition (CC0)'},
            'staff_size': 22, 'paper': 'a4', 'font': 'TeX Gyre Pagella',
            'paper_extra': ['top-margin = 18\\mm', 'system-count = 4', 'system-system-spacing.basic-distance = #20']}
    return sc, piano_layout(['1', '2'], ['5']), opts


# ---------------------------------------------------------------- P4: 2-page piano piece
# Theme ("Ah! vous dirai-je, maman", French, c. 1761, public domain) + one variation (CC0).
TW_RH1 = (
    # theme (12 bars)
    "c''4\\mp c''4 g''4 g''4 | a''4 a''4 g''2 | f''4 f''4 e''4 e''4 | d''4 d''4 c''2 | "
    "g''4 g''4 f''4 f''4 | e''4 e''4 d''2 | g''4 g''4 f''4 f''4 | e''4 e''4 d''2 | "
    "c''4 c''4 g''4 g''4 | a''4 a''4 g''2 | f''4 f''4 e''4 e''4 | d''4 d''4 c''2 | "
    # variation (12 bars): eighth-note figuration over a held lower voice
    "c''8\\mf( d''8 c''8 d''8) g''8( a''8 g''8 a''8) | a''8( b''8 a''8 b''8) g''2 | "
    "f''8( g''8 f''8 g''8) e''8( f''8 e''8 f''8) | d''8( e''8 d''8 e''8) c''2 | "
    "g''8( a''8 g''8 a''8) f''8( g''8 f''8 g''8) | e''8( f''8 e''8 f''8) d''2 | "
    "g''8( a''8 g''8 a''8) f''8( g''8 f''8 g''8) | e''8( f''8 e''8 f''8) d''2 | "
    "c''8\\f( d''8 c''8 d''8) g''8( a''8 g''8 a''8) | a''8( b''8 a''8 b''8) g''2 | "
    "f''8( g''8 f''8 g''8) e''8( f''8 e''8 fis''8) | g''4 d''4 c''2\\fermata")
TW_RH2 = (
    "r1 | r1 | r1 | r1 | r1 | r1 | r1 | r1 | r1 | r1 | r1 | r1 | "
    "e'2 e'2 | f'2 e'2 | a'2 g'2 | f'2 e'2 | "
    "e'2 d'2 | c'2 b2 | e'2 d'2 | c'2 b2 | "
    "e'2 e'2 | f'2 e'2 | a'2 g'4 c''4 | f'4 f'4 e'2")
TW_LH = (
    "c2 e2 | f2 e2 | d2 c2 | g,2 c2 | e2 d2 | c2 g,2 | e2 d2 | c2 g,2 | c2 e2 | f2 e2 | d2 c2 | g,2 c2 | "
    "c4 g4 e4 g4 | f4 a4 e4 g4 | d4 a4 c4 g4 | g,4 g4 c4 g4 | "
    "e4 g4 d4 g4 | c4 g4 g,4 g4 | e4 g4 d4 g4 | c4 g4 g,4 g4 | "
    "c4 g4 e4 g4 | f4 a4 e4 g4 | d4 a4 c4 a4 | g,2 <c, c>2\\fermata")


def mk_piano_two_page():
    from fractions import Fraction as F

    from synth.model import Event
    sc = piano_score([TW_RH1, TW_RH2], [TW_LH], (4, 4), (0, 'major'), 'Theme and Variation',
                     'Corpus composition (CC0)')
    p = sc.part('P')
    for j in range(12):
        p.measures[j]['2'] = [Event('space', F(4))]
    sc.measures[11].right_bar = 'double'
    sc.rights = 'Theme public domain (French air, c. 1761); variation and engraving CC0'
    opts = {'header': {'title': 'Theme and Variation',
                       'subtitle': 'on "Ah! vous dirai-je, maman"',
                       'composer': 'Corpus composition (CC0)', 'arranger': 'Theme: French air, c. 1761'},
            'staff_size': 25, 'paper': 'a4', 'font': 'C059',
            'paper_extra': ['top-margin = 15\\mm', 'bottom-margin = 15\\mm', 'system-count = 6',
                            'systems-per-page = 3', 'system-system-spacing.basic-distance = #20']}
    return sc, piano_layout(['1', '2'], ['5']), opts


PIECES = {
    'hymn': dict(
        make=mk_hymn, title='Amazing Grace (SATB, closed score, 3 verses)',
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], must_not_split=False,
        shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        base_tags=['lyrics', 'multi_verse', 'satb_closed', 'multi_voice_staff', 'shared_staves', 'pickup',
                   'melisma', 'slurs', 'ties', 'compound_lyric_hyphen_over_melisma', 'hymn', 'key_signature',
                   'time_3_4'],
        notes=('Closed-score SATB: Soprano+Alto share the treble staff, Tenor+Bass share the bass staff. '
               'A correct conversion yields FOUR parts (Soprano, Alto, Tenor, Bass), each with its own notes; '
               'all three verses belong to the Soprano part (lyric numbers 1-3) and must stay attached to '
               'soprano notes, including melisma skips (e.g. "pre - cious" spans a slurred melisma).'),
        license='Public domain melody (NEW BRITAIN, 1829) and text (John Newton, 1779); SATB setting and '
                'engraving CC0-1.0',
        attribution=['Amazing Grace. Melody: NEW BRITAIN, American folk melody (Virginia Harmony, 1831; '
                     'earliest 1829) - public domain.',
                     'Text: John Newton, Olney Hymns (1779), verses 1-3 - public domain.',
                     'SATB harmonisation: generated by the corpus voice-leading solver, CC0.']),
    'melody': dict(
        make=mk_melody, title='Who Has Seen the Wind? (melody, 2 verses)',
        expected_parts=['Voice'], must_not_split=False, shared_staves=[],
        base_tags=['lyrics', 'multi_verse', 'melody', 'pickup', 'melisma', 'slurs', 'unequal_verse_syllables',
                   'key_signature', 'time_3_4', 'large_staff'],
        notes=('Single-staff melody with two stacked verses. Verse 1 has one syllable fewer than verse 2 in '
               'line 3 ("trem-_-bling" vs "bow down their heads"): bar 6 beat 3 (c\'\'8) carries a verse-2 '
               'syllable ("their") but NO verse-1 syllable. The final melisma "pass-ing _" is slurred in '
               'both verses.'),
        license='Text public domain (Christina Rossetti, Sing-Song, 1872); melody and engraving CC0-1.0',
        attribution=['Text: Christina Rossetti, "Who has seen the wind?", Sing-Song (1872) - public domain.',
                     'Melody: composed for this corpus, CC0.']),
    'piano': dict(
        make=mk_piano_short, title='Andantino (piano, grand staff)',
        expected_parts=['Piano'], must_not_split=True, shared_staves=[],
        base_tags=['piano', 'grand_staff', 'must_not_split', 'grand_staff_multi_voice', 'chords', 'dynamics',
                   'slurs', 'staccato', 'fermata', 'key_signature'],
        notes=('Piano solo on ONE grand staff (brace). A correct conversion yields exactly ONE part "Piano" '
               'with 2 staves; it must NOT be split into right/left hand parts, and the second right-hand '
               'voice in bars 13-16 must stay inside the piano part (voice 2), not become a new part.'),
        license='Original composition and engraving, CC0-1.0',
        attribution=['"Andantino" for piano: original composition for this corpus, CC0.']),
    'piano2p': dict(
        make=mk_piano_two_page, title='Theme and Variation on "Ah! vous dirai-je, maman" (piano, 2 pages)',
        expected_parts=['Piano'], must_not_split=True, shared_staves=[],
        base_tags=['piano', 'grand_staff', 'must_not_split', 'grand_staff_multi_voice', 'multi_page',
                   'double_barline', 'dynamics', 'slurs', 'fermata', 'chords'],
        notes=('Two-page piano piece on ONE grand staff. A correct conversion yields exactly ONE part "Piano" '
               '(2 staves, 24 bars, measures continue across the page turn); the held lower right-hand voice '
               'in the variation (bars 13-24) is voice 2 of the piano part, not a separate part.'),
        license='Theme public domain (French air "Ah! vous dirai-je, maman", c. 1761); variation, setting '
                'and engraving CC0-1.0',
        attribution=['Theme: "Ah! vous dirai-je, maman", French air (c. 1761) - public domain.',
                     'Setting and variation: composed for this corpus, CC0.']),
}
