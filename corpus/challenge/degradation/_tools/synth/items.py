"""Corpus item definitions (sources, transforms, staff layout, degradations)."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from music21 import corpus

from .dsl import build_score
from .harmonize import harmonize
from .m21import import from_music21
from .model import (Part, VoiceDef, clear_lyrics, derive_lyrics, lyric_verses, renumber, set_verses,
                    transpose_octaves, truncate)

M21 = 'https://github.com/cuthbertLab/music21/tree/master/music21/corpus/'
SATB = [{'src': [0], 'id': 'S', 'name': 'Soprano', 'abbr': 'S.'},
        {'src': [1], 'id': 'A', 'name': 'Alto', 'abbr': 'A.'},
        {'src': [2], 'id': 'T', 'name': 'Tenor', 'abbr': 'T.'},
        {'src': [3], 'id': 'B', 'name': 'Bass', 'abbr': 'B.'}]
GREENTREE = ('Encoding: music21 corpus (from Margaret Greentree\'s jsbchorales.net MusicXML, '
             '"used by permission"); composition public domain. Test-corpus use only.')


def bach(bwv, unroll=False):
    s = corpus.parse(f'bach/{bwv}')
    if unroll:
        s = s.expandRepeats()
    return from_music21(s, copy.deepcopy(SATB))


def closed_layout(upper, lower, lyr_upper, lyr_lower=(), names=None, clefs=('treble', 'bass'),
                  group='ChoirStaff', extra=None):
    """upper/lower: [(pid, vkey), (pid, vkey)]"""
    st1 = {'id': 'upper', 'clef': clefs[0], 'voices': upper,
           'lyrics': [{'voice': v, 'verses': vs, 'place': pl} for v, vs, pl in lyr_upper]}
    st2 = {'id': 'lower', 'clef': clefs[1], 'voices': lower,
           'lyrics': [{'voice': v, 'verses': vs, 'place': pl} for v, vs, pl in lyr_lower]}
    if names:
        st1['name'], st2['name'] = names[0], names[1]
        if len(names) > 2:
            st1['short'], st2['short'] = names[2], names[3]
    groups = [{'type': group, 'staves': [st1, st2]}]
    if extra:
        groups += extra
    return {'groups': groups}


def set_clefs(sc, mapping):
    for pid, c in mapping.items():
        sc.part(pid).clefs = [c]


def choir_group(sc, first, last):
    sc.groups = [{'first': first, 'last': last, 'symbol': 'bracket'}]


def merge_parts_to_piano(sc, assign, pid='P', name='Piano', abbr='Pno.'):
    """assign: list of (src_pid, staff) -> one piano part with 2 staves."""
    p = Part(id=pid, name=name, abbr=abbr, instrument='piano', staves=2, clefs=['treble', 'bass'])
    keys = {1: 1, 2: 5}
    nm = len(sc.measures)
    p.measures = [dict() for _ in range(nm)]
    for spid, staff in assign:
        k = str(keys[staff])
        keys[staff] += 1
        p.voices.append(VoiceDef(k, staff))
        src = sc.part(spid)
        for i in range(nm):
            p.measures[i][k] = copy.deepcopy(src.measures[i]['1'])
            for ev in p.measures[i][k]:
                ev.lyrics = {}
    sc.parts = [p]
    sc.groups = []
    return sc


def fix_repeats(sc):
    """drop unmatched repeat-starts after truncation"""
    open_i = None
    for i, m in enumerate(sc.measures):
        if m.left_bar == 'repeat-start':
            if open_i is not None:
                sc.measures[open_i].left_bar = None
            open_i = i
        if m.right_bar == 'repeat-end':
            open_i = None
    if open_i is not None:
        sc.measures[open_i].left_bar = None


def rename(sc, mapping):
    for p in sc.parts:
        if p.id in mapping:
            p.name, p.abbr = mapping[p.id]


# ======================================================================
# Self-authored hymns (melodies public domain; harmonisations generated
# for this corpus and dedicated CC0)
# ======================================================================

OLD100_S = ("g'2\\fermata | g'4 fis' e' d' | g' a' b'2\\fermata | b'2 b'4 b' | a' g' c'' b' | "
            "a'2\\fermata g'2 | a'4 b' a' g' | e' fis' g'2\\fermata | d''2 b'4 g' | a' c'' b' a' | g'2\\fermata")
OLD100_S = OLD100_S.replace("g'2\\fermata | g'4 fis'", "g'2 | g'4 fis'", 1)
OLD100_CH = ['G', 'Em', 'D', 'C', 'G/B', 'C', 'D', 'G',
             'G', 'Em', 'Bm', 'D', 'Em', 'C', 'G', 'D',
             'G', 'D/F#', 'G', 'D', 'Em', 'C', 'D', 'G',
             'G', 'Em', 'C', 'D', 'Am', 'G', 'D7', 'G']
OLD100_V = [
    "All peo -- ple that on earth do dwell, Sing to the Lord with cheer -- ful voice; "
    "Him serve with fear, his praise forth tell, Come ye be -- fore him and re -- joice.",
    "The Lord, ye know, is God in -- deed; With -- out our aid he did us make; "
    "We are his folk, he doth us feed, And for his sheep he doth us take.",
    "O en -- ter then his gates with praise, Ap -- proach with joy his courts un -- to; "
    "Praise, laud, and bless his name al -- ways, For it is seem -- ly so to do.",
    "For why? the Lord our God is good; His mer -- cy is for ev -- er sure; "
    "His truth at all times firm -- ly stood, And shall from age to age en -- dure.",
]

JOY_S = ("b'4 b' c'' d'' | d'' c'' b' a' | g' g' a' b' | b'4. a'8 a'2 | "
         "b'4 b' c'' d'' | d'' c'' b' a' | g' g' a' b' | a'4. g'8 g'2 | "
         "a'4 a' b' g' | a' b'8( c'') b'4 g' | a' b'8( c'') b'4 a' | g' a' d'2 | "
         "b'4 b' c'' d'' | d'' c'' b' a' | g' g' a' b' | a'4. g'8 g'2")
_P1 = ['G', 'Em', 'C', 'G', 'D', 'D7', 'G', 'D', 'Em', 'C', 'D', 'G']
JOY_CH = (_P1 + ['Em', 'D', '-'] + _P1 + ['D7', 'G', '-'] +
          ['D', 'D/F#', 'G', 'Em', 'D', 'G', '~', 'G', 'Em', 'D', 'Em', '~', 'G', 'D', 'C', 'A7', 'D'] +
          _P1 + ['D7', 'G', '-'])
JOY_V = [
    "Joy -- ful, joy -- ful, we a -- dore thee, God of glo -- ry, Lord of love; "
    "Hearts un -- fold like flowers be -- fore thee, O -- pening to the sun a -- bove. "
    "Melt the clouds of sin and _ sad -- ness; Drive the _ dark of doubt a -- way; "
    "Giv -- er of im -- mor -- tal glad -- ness, Fill us with the light of day!",
    "All thy works with joy sur -- round thee, Earth and heaven re -- flect thy rays, "
    "Stars and an -- gels sing a -- round thee, Cen -- ter of un -- bro -- ken praise. "
    "Field and for -- est, vale and _ moun -- tain, Flower -- y _ mead -- ow, flash -- ing sea, "
    "Sing -- ing bird and flow -- ing foun -- tain Call us to re -- joice in thee.",
    "Mor -- tals, join the hap -- py cho -- rus Which the morn -- ing stars be -- gan; "
    "Fa -- ther love is reign -- ing o'er us, Broth -- er love binds man to man. "
    "Ev -- er sing -- ing, march we _ on -- ward, Vic -- tors _ in the midst of strife, "
    "Joy -- ful mu -- sic leads us sun -- ward In the tri -- umph song of life.",
]

SILENT_S = ("g'4. a'8 g'4( | e'2.) | g'4. a'8 g'4( | e'2.) | d''2 d''4 | b'2. | c''2 c''4 | g'2. | "
            "a'2 a'4 | c''4. b'8 a'4 | g'4. a'8 g'4( | e'2.) | a'2 a'4 | c''4. b'8 a'4 | g'4. a'8 g'4 | e'2. | "
            "d''2 d''4 | f''4. d''8 b'4 | c''2.( | e''2.) | c''4 g' e' | g'4. f'8( d'4) | c'2.~ | c'2.")
SILENT_V = [
    "Si -- lent night, _ ho -- ly night, _ All is calm, all is bright, "
    "Round yon vir -- gin moth -- er and child. _ Ho -- ly in -- fant so ten -- der and mild, "
    "Sleep in heav -- en -- ly peace, _ Sleep in heav -- en -- ly _ peace.",
    "Si -- lent night, _ ho -- ly night, _ Shep -- herds quake at the sight; "
    "Glo -- ries stream from heav -- en a -- far, _ Heav -- en -- ly hosts sing Al -- le -- lu -- ia! "
    "Christ the Sav -- ior is born, _ Christ the Sav -- ior is _ born!",
    "Si -- lent night, _ ho -- ly night, _ Son of God, love's pure light; "
    "Ra -- diant beams from thy ho -- ly face _ With the dawn of re -- deem -- ing _ grace, "
    "Je -- sus, Lord, at thy birth, _ Je -- sus, Lord, at thy _ birth.",
]

PASSION_EN = [
    "O sa -- cred Head, now wound -- ed, with grief and shame weighed down, "
    "now scorn -- ful -- ly sur -- round -- ed with thorns, thine on -- ly crown; "
    "how pale thou art with an -- guish, with sore a -- buse and scorn! "
    "How does that vis -- age lan -- guish, which once was bright as morn!",
    "What thou, my Lord, hast suf -- fered was all for sin -- ners' gain; "
    "mine, mine was the trans -- gres -- sion, but thine the dead -- ly pain. "
    "Lo, here I fall, my Sav -- ior! 'Tis I de -- serve thy place; "
    "look on me with thy fa -- vor, vouch -- safe to me thy grace.",
    "What lan -- guage shall I bor -- row to thank thee, dear -- est friend, "
    "for this thy dy -- ing sor -- row, thy pi -- ty with -- out end? "
    "O make me thine for -- ev -- er; and should I faint -- ing be, "
    "Lord, let me nev -- er, nev -- er out -- live my love to thee.",
]


def hymn_satb(sop, chords, verses, time, key, tonic_pc, title, composer, lyricist, time_symbol=None):
    sc = build_score({'S': sop}, time=time, key=key, time_symbol=time_symbol,
                     parts=[{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'voice': 'S'}])
    smeas = [m['1'] for m in sc.part('S').measures]
    a, t, b = harmonize(smeas, chords, tonic_pc)
    for pid, name, abbr, clef, meas in (('A', 'Alto', 'A.', 'treble', a), ('T', 'Tenor', 'T.', 'bass', t),
                                        ('B', 'Bass', 'B.', 'bass', b)):
        p = Part(id=pid, name=name, abbr=abbr, clefs=[clef], voices=[VoiceDef('1', 1)])
        p.measures = [{'1': m} for m in meas]
        sc.parts.append(p)
    set_verses(sc, 'S', '1', verses, mode='attack')
    sc.title, sc.composer, sc.lyricist = title, composer, lyricist
    sc.arranger = 'SATB harmonization generated for this corpus (CC0)'
    choir_group(sc, 'S', 'B')
    return sc


# ---------------------------------------------------------------- makers

def mk_old100(sample=False):
    def make():
        sc = hymn_satb(OLD100_S, OLD100_CH, OLD100_V, (4, 4), (1, 'major'), 7, 'Old Hundredth',
                       'Louis Bourgeois, Genevan Psalter (1551)', 'William Kethe (1561)', time_symbol='common')
        sc.rights = 'Public domain melody and text; harmonization CC0 (synthetic corpus)'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1, 2, 3, 4], 'below')])
        opts = {'header': {'title': 'Old Hundredth', 'subtitle': 'All people that on earth do dwell',
                           'poet': 'William Kethe, 1561', 'composer': 'Genevan Psalter, 1551',
                           'meter': 'L.M.'},
                'staff_size': 21, 'paper': 'letter', 'font': 'TeX Gyre Schola',
                'paper_extra': ['indent = 0', 'ragged-last = ##f', 'top-margin = 18\\mm',
                                'system-system-spacing.basic-distance = #16'],
                'layout_extra': ['\\context { \\Score \\remove "Bar_number_engraver" }'],
                'auto_beam_off_vocal': True}
        return sc, lay, opts
    return make


def mk_joyful():
    def make():
        sc = hymn_satb(JOY_S, JOY_CH, JOY_V, (4, 4), (1, 'major'), 7, 'Hymn to Joy',
                       'Ludwig van Beethoven (1824), adapted', 'Henry van Dyke (1907)')
        sc.rights = 'Public domain melody and text; harmonization CC0 (synthetic corpus)'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1, 2, 3], 'below')])
        opts = {'header': {'title': 'Joyful, Joyful, We Adore Thee', 'poet': 'Henry van Dyke, 1907',
                           'composer': 'HYMN TO JOY  87.87 D', 'arranger': 'Melody: L. van Beethoven, 1824'},
                'staff_size': 19, 'paper': 'a4', 'font': 'TeX Gyre Termes',
                'paper_extra': ['indent = 0', 'system-system-spacing.basic-distance = #14'],
                'auto_beam_off_vocal': False}
        return sc, lay, opts
    return make


def mk_silent():
    def make():
        sc = build_score({'M': SILENT_S}, time=(6, 8), key=(0, 'major'),
                         parts=[{'id': 'V', 'name': 'Voice', 'abbr': '', 'voice': 'M'}])
        set_verses(sc, 'V', '1', SILENT_V, mode='attack')
        sc.title, sc.composer, sc.lyricist = 'Silent Night', 'Franz Xaver Gruber (1818)', \
            'Joseph Mohr (1816), tr. John Freeman Young (1859)'
        sc.rights = 'Public domain'
        opts = {'header': {'title': 'Silent Night', 'poet': 'Joseph Mohr, tr. J. F. Young',
                           'composer': 'Franz X. Gruber'},
                'staff_size': 22, 'paper': 'a4', 'font': 'URW Bookman',
                'paper_extra': ['indent = 0'], 'auto_beam_off_vocal': True}
        return sc, None, opts
    return make


def mk_passion_en():
    def make():
        sc = bach('bwv244.62', unroll=True)
        set_verses(sc, 'S', '1', PASSION_EN, mode='lyric')
        for p in ('A', 'T', 'B'):
            clear_lyrics(sc, p)
        set_clefs(sc, {'S': 'treble', 'A': 'treble', 'T': 'bass', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title = 'O Sacred Head, Now Wounded'
        sc.composer = 'Hans Leo Hassler (1601), harm. J. S. Bach (BWV 244/62)'
        sc.lyricist = 'Paul Gerhardt (1656), tr. James W. Alexander (1830)'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1, 2, 3], 'below')])
        opts = {'header': {'title': 'O Sacred Head, Now Wounded', 'poet': 'P. Gerhardt, tr. J. W. Alexander',
                           'composer': 'H. L. Hassler, harm. J. S. Bach', 'meter': '76.76 D'},
                'staff_size': 20, 'paper': 'letter', 'font': 'C059', 'paper_extra': ['indent = 0']}
        return sc, lay, opts
    return make


def mk_bach_closed_sb(bwv, title):
    def make():
        sc = bach(bwv)
        n, miss = derive_lyrics(sc, ('S', '1'), ('B', '1'))
        assert miss == 0, miss
        set_clefs(sc, {'S': 'treble', 'A': 'treble', 'T': 'bass', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title, sc.composer = title, 'J. S. Bach'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1], 'below')], [(('B', '1'), [1], 'below')],
                            names=[['Soprano', 'Alto'], ['Tenor', 'Bass']])
        opts = {'header': {'title': title, 'composer': 'J. S. Bach', 'subtitle': f'Choral ({bwv.upper()})'},
                'staff_size': 18, 'paper': 'a4', 'font': 'TeX Gyre Pagella'}
        return sc, lay, opts
    return make


def mk_bach_closed_repeat(bwv, title):
    def make():
        sc = bach(bwv)
        set_clefs(sc, {'S': 'treble', 'A': 'treble', 'T': 'bass', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title, sc.composer = title, 'J. S. Bach'
        vs = lyric_verses(sc.part('S'), '1')
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), vs, 'below')])
        opts = {'header': {'title': title, 'composer': 'Joh. Seb. Bach'},
                'staff_size': 20, 'paper': 'a4', 'font': 'Nimbus Roman',
                'paper_extra': ['indent = 0']}
        return sc, lay, opts
    return make


def mk_bach_ttbb(bwv, title):
    def make():
        sc = bach(bwv)
        transpose_octaves(sc, 'S', -1)
        transpose_octaves(sc, 'A', -1)
        rename(sc, {'S': ('Tenor I', 'T. I'), 'A': ('Tenor II', 'T. II'), 'T': ('Baritone', 'Bar.'),
                    'B': ('Bass', 'B.')})
        set_clefs(sc, {'S': 'treble_8', 'A': 'treble_8', 'T': 'bass', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title, sc.composer = title, 'J. S. Bach, arr. for male voices'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1], 'below')], clefs=('treble_8', 'bass'),
                            names=[['Tenor I', 'Tenor II'], ['Baritone', 'Bass'], ['T. I', 'T. II'],
                                   ['Bar.', 'B.']])
        opts = {'header': {'title': title, 'subtitle': 'for male chorus (TTBB)',
                           'composer': 'J. S. Bach'},
                'staff_size': 20, 'paper': 'a4', 'font': 'DejaVu Serif'}
        return sc, lay, opts
    return make


def mk_aloha_closed():
    def make():
        s = corpus.parse('liliuokalani/aloha_oe.mxl')
        sc = from_music21(s, copy.deepcopy(SATB))
        truncate(sc, 14, 23)
        sc.measures[0].implicit = True
        sc.measures[0].time = sc.measures[0].time or (4, 4)
        sc.measures[0].key = sc.measures[0].key or (1, 'major')
        renumber(sc)
        set_clefs(sc, {'S': 'treble', 'A': 'treble', 'T': 'bass', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title, sc.composer = 'Aloha Oe (Chorus)', 'Liliuokalani'
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')],
                            [(('S', '1'), [1, 2], 'below')], [(('T', '1'), [1, 2], 'below')])
        opts = {'header': {'title': 'Aloha Oe', 'subtitle': 'Chorus', 'composer': 'Liliuokalani'},
                'staff_size': 20, 'paper': 'letter', 'font': 'Liberation Serif'}
        return sc, lay, opts
    return make


def mk_aloha_full():
    def make():
        s = corpus.parse('liliuokalani/aloha_oe.mxl')
        spec = copy.deepcopy(SATB) + [
            {'src': [4], 'id': 'V', 'name': 'Solo Voice', 'abbr': 'Solo'},
            {'src': [5, 6], 'id': 'P', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano'}]
        sc = from_music21(s, spec)
        # Solo first, then SATB, then piano (common vocal-score order)
        order = ['V', 'S', 'A', 'T', 'B', 'P']
        sc.parts = [sc.part(x) for x in order]
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        sc.title, sc.composer = 'Aloha Oe', 'Liliuokalani (1878)'
        opts = {'header': {'title': 'Aloha Oe', 'subtitle': 'Farewell to Thee',
                           'composer': 'Liliuokalani'},
                'staff_size': 16, 'paper': 'a4', 'font': 'TeX Gyre Bonum'}
        return sc, None, opts
    return make


def mk_beach_ssaa():
    def make():
        s = corpus.parse('beach/prayer_of_a_tired_child.musicxml')
        spec = [{'src': [0], 'id': 'S1', 'name': 'Soprano I', 'abbr': 'S. I'},
                {'src': [1], 'id': 'S2', 'name': 'Soprano II', 'abbr': 'S. II'},
                {'src': [2], 'id': 'A1', 'name': 'Alto I', 'abbr': 'A. I'},
                {'src': [3], 'id': 'A2', 'name': 'Alto II', 'abbr': 'A. II'},
                {'src': [4, 5], 'id': 'P', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano'}]
        sc = from_music21(s, spec)
        truncate(sc, 0, 18)
        clear_lyrics(sc, 'S2')
        clear_lyrics(sc, 'A1')
        sc.groups = [{'first': 'S1', 'last': 'A2', 'symbol': 'bracket'}]
        sc.title, sc.composer = 'A Prayer of a Tired Child', 'Amy Beach, Op. 75 No. 4'
        piano = {'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'pu', 'clef': sc.part('P').clefs[0], 'voices': [('P', v.key) for v in sc.part('P').voices if v.staff == 1], 'lyrics': []},
            {'id': 'pl', 'clef': sc.part('P').clefs[1], 'voices': [('P', v.key) for v in sc.part('P').voices if v.staff == 2], 'lyrics': []}]}
        lay = closed_layout([('S1', '1'), ('S2', '1')], [('A1', '1'), ('A2', '1')],
                            [(('S1', '1'), [1], 'below')], [(('A2', '1'), [1], 'below')],
                            clefs=('treble', 'treble'),
                            names=[['Soprano I', 'Soprano II'], ['Alto I', 'Alto II'], ['S. I-II'], ['A. I-II']],
                            extra=[piano])
        lay['groups'][0]['staves'][1]['short'] = 'A. I-II'
        lay['groups'][0]['staves'][0]['short'] = 'S. I-II'
        opts = {'header': {'title': 'A Prayer of a Tired Child', 'composer': 'Amy Beach, Op. 75, No. 4',
                           'subtitle': 'for women\'s chorus (SSAA) and piano'},
                'staff_size': 17, 'paper': 'letter', 'font': 'P052'}
        return sc, lay, opts
    return make


def mk_bach_open(bwv, title):
    def make():
        sc = bach(bwv)
        for p in ('A', 'T', 'B'):
            n, miss = derive_lyrics(sc, ('S', '1'), (p, '1'))
            assert miss == 0, (p, miss)
        set_clefs(sc, {'S': 'treble', 'A': 'treble', 'T': 'treble_8', 'B': 'bass'})
        choir_group(sc, 'S', 'B')
        sc.title, sc.composer = title, 'J. S. Bach'
        opts = {'header': {'title': title, 'composer': 'J. S. Bach'},
                'staff_size': 18, 'paper': 'a4', 'font': 'C059'}
        return sc, None, opts
    return make


def mk_foster():
    def make():
        s = corpus.parse('leadSheet/fosterBrownHair.mxl')
        sc = from_music21(s, [{'src': [0], 'id': 'V', 'name': 'Voice', 'abbr': ''}])
        sc.title, sc.composer, sc.lyricist = 'Jeanie with the Light Brown Hair', 'Stephen C. Foster (1854)', \
            'Stephen C. Foster'
        sc.rights = 'Public domain'
        opts = {'header': {'title': 'Jeanie with the Light Brown Hair', 'composer': 'Stephen C. Foster'},
                'staff_size': 20, 'paper': 'letter', 'font': 'TeX Gyre Schola'}
        return sc, None, opts
    return make


def mk_piano_chorale(bwv, title):
    def make():
        sc = bach(bwv)
        merge_parts_to_piano(sc, [('S', 1), ('A', 1), ('T', 2), ('B', 2)])
        sc.title, sc.composer = title, 'J. S. Bach, arr. for piano'
        opts = {'header': {'title': title, 'subtitle': 'Chorale for keyboard', 'composer': 'J. S. Bach'},
                'staff_size': 21, 'paper': 'a4', 'font': 'TeX Gyre Termes'}
        lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'pu', 'clef': 'treble', 'voices': [('P', '1'), ('P', '2')], 'lyrics': []},
            {'id': 'pl', 'clef': 'bass', 'voices': [('P', '5'), ('P', '6')], 'lyrics': []}]}]}
        return sc, lay, opts
    return make


def mk_corpus_piece(name, measures, spec, title, composer, opts_extra, renames=None, keep_slurs=True):
    def make():
        s = corpus.parse(name)
        sc = from_music21(s, copy.deepcopy(spec) if spec else None)
        if measures:
            truncate(sc, measures[0], measures[1])
            m0 = sc.measures[0]
            if measures[0] > 0:
                (t, sym) = sc.current_time(0)
            fix_repeats(sc)
        if renames:
            rename(sc, renames)
        sc.title, sc.composer = title, composer
        opts = dict(opts_extra)
        return sc, None, opts
    return make


def restate_first(sc_func, time, key):
    def make():
        sc, lay, opts = sc_func()
        m0 = sc.measures[0]
        m0.time = m0.time or time
        m0.key = m0.key or key
        return sc, lay, opts
    return make
