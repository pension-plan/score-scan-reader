"""Lyrics challenge items: music (own CC0 melodies / harmonisations), public-
domain texts, staff layouts, expected-conversion notes and scan-damage recipes."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from synth.dsl import parse_voice
from synth.harmonize import harmonize
from synth.lily import lq
from synth.model import MeasureInfo, Part, Score, VoiceDef, renumber, set_verses

CC0 = ('Music (melody, harmonisation, accompaniment), engraving, rasterisation and damage were produced '
       'for this corpus by corpus/challenge/lyrics/_tools and are dedicated to the public domain (CC0 1.0).')


def att(*lines):
    return '\n'.join(lines + ('', CC0))


def U(n):
    return ' '.join(['_'] * n)


# ---------------------------------------------------------------- builders
def mk_score(voices, time, key, parts, time_symbol=None):
    """voices: name -> DSL text.  parts: [{'id','name','abbr','instrument',
    'clefs':[...], 'voices':[(vkey, staff, voice_name)]}]"""
    parsed = {k: parse_voice(v, time) for k, v in voices.items()}
    lens = {k: len(v) for k, v in parsed.items()}
    nm = max(lens.values())
    assert all(l == nm for l in lens.values()), lens
    nominal = F(time[0] * 4, time[1])
    sc = Score()
    for i in range(nm):
        durs = {k: sum((e.dur for e in parsed[k][i]), F(0)) for k in parsed}
        dur = max(durs.values())
        if len(set(durs.values())) != 1:
            raise ValueError(f'measure {i}: voices differ {durs}')
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        elif dur != nominal and i != nm - 1:
            raise ValueError(f'measure {i} has duration {dur}')
        sc.measures.append(mi)
    sc.measures[-1].right_bar = 'final'
    for spec in parts:
        clefs = spec.get('clefs', ['treble'])
        p = Part(id=spec['id'], name=spec['name'], abbr=spec.get('abbr', ''),
                 instrument=spec.get('instrument', 'voice'), staves=len(clefs), clefs=list(clefs))
        p.voices = [VoiceDef(vk, st) for vk, st, _ in spec['voices']]
        for i in range(nm):
            p.measures.append({vk: parsed[src][i] for vk, st, src in spec['voices']})
        sc.parts.append(p)
    renumber(sc)
    return sc


def satb_from_soprano(sop, chords, time, key, tonic_pc, time_symbol=None):
    sc = mk_score({'S': sop}, time, key, [{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'voices': [('1', 1, 'S')]}],
                  time_symbol=time_symbol)
    smeas = [m['1'] for m in sc.part('S').measures]
    a, t, b = harmonize(smeas, chords, tonic_pc)
    for pid, name, abbr, clef, meas in (('A', 'Alto', 'A.', 'treble', a), ('T', 'Tenor', 'T.', 'bass', t),
                                        ('B', 'Bass', 'B.', 'bass', b)):
        p = Part(id=pid, name=name, abbr=abbr, clefs=[clef], voices=[VoiceDef('1', 1)])
        p.measures = [{'1': m} for m in meas]
        sc.parts.append(p)
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    return sc


def closed_layout(lyr_upper, lyr_lower=(), names=None, shorts=None):
    st1 = {'id': 'upper', 'clef': 'treble', 'voices': [('S', '1'), ('A', '1')], 'lyrics': list(lyr_upper)}
    st2 = {'id': 'lower', 'clef': 'bass', 'voices': [('T', '1'), ('B', '1')], 'lyrics': list(lyr_lower)}
    if names:
        st1['name'], st2['name'] = names
    if shorts:
        st1['short'], st2['short'] = shorts
    return {'groups': [{'type': 'ChoirStaff', 'staves': [st1, st2]}]}


def voice_piano_layout(sc, vid='V', lyrics=None, vname=None):
    v = sc.part(vid)
    p = sc.part('P')
    vocal = {'id': 'voice', 'clef': v.clefs[0], 'voices': [(vid, '1')],
             'lyrics': lyrics or [{'voice': (vid, '1'), 'verses': [1], 'place': 'below'}]}
    if vname:
        vocal['name'] = vname
    piano = {'type': 'PianoStaff', 'name': p.name, 'staves': [
        {'id': 'pu', 'clef': p.clefs[0], 'voices': [('P', '1')], 'lyrics': []},
        {'id': 'pl', 'clef': p.clefs[1], 'voices': [('P', '5')], 'lyrics': []}]}
    return {'groups': [{'type': None, 'staves': [vocal]}, piano]}


def stanza_block(stanzas, columns, gap=1.2):
    """hymnal-style text stanzas below the last system, in columns"""
    def one(st):
        lines = ' '.join(lq(x) for x in st['lines'])
        return (f'\\line {{ \\bold {lq(st["label"])} \\hspace #0.8 \\column {{ {lines} }} }}')
    cols = []
    for col in columns:
        parts = []
        for k, idx in enumerate(col):
            if k:
                parts.append(f'\\vspace #{gap}')
            parts.append(one(stanzas[idx]))
        cols.append('\\column { ' + ' '.join(parts) + ' }')
    return ['\\markup { \\vspace #1.6 }',
            '\\markup { \\fill-line { \\null ' + ' \\null '.join(cols) + ' \\null } }']


NB = ' '   # French typography: no-break space before ; : ! ?
AP = '’'   # typographic apostrophe

# ======================================================================
# 1. Latin aria: very long melismas, extenders across system breaks
# ======================================================================
ARIA_V = ("a'4 d'' fis''16( e'' d'' e'' fis'' g'' a'' fis'' | g''16 fis'' e'' d'' cis''8 e'') a'4 r8 a'8 | "
          "d''4 e'' fis''2 | e''16( fis'' g'' a'' g'' fis'' e'' d'' cis'' d'' e'' fis'' e'' d'' cis'' b' | "
          "a'8 b' cis'' d'' e''4) r4 | r4 a'8 a' d''4. d''8 | fis''2.~ fis''8( e''16 d'' | "
          "cis''16 d'' e'' fis'' g'' fis'' e'' d'' cis'' b' a' b' cis''8 a') | d''4.( e''8 d''4) r4 | "
          "r8 a' b' cis'' d''4 e''8 fis'' | g''4. fis''8 e''4 d''8( cis'' | d''2) r2 | "
          "a'4 b'8 cis'' d''16( e'' fis'' g'' a'' g'' fis'' e'') | fis''4( e''8 d'' cis''4) r4 | "
          "r4 d''8 d'' e''4 fis''( | g''2 fis''4 e'') | a'2 a'4( b'8 cis'' | d''1)\\fermata")
ARIA_RH = ("<d' fis' a'>2 <d' fis' a'> | <cis' e' a'> <cis' e' a'> | <d' fis' a'> <d' fis' a'> | "
           "<cis' e' a'> <cis' e' g'> | <cis' e' a'> <cis' e' a'> | <d' fis' a'> <d' fis' a'> | "
           "<d' fis' a'> <d' fis' a'> | <cis' e' a'> <cis' e' a'> | <d' fis' a'> <d' fis' a'> | "
           "<cis' e' a'> <d' fis' a'> | <d' g' b'> <cis' e' a'> | <d' fis' a'> <d' fis' a'> | "
           "<d' fis' a'> <cis' e' g'> | <d' fis' a'> <cis' e' a'> | <d' fis' a'> <cis' e' a'> | "
           "<d' g' b'> <cis' e' a'> | <cis' e' a'> <cis' e' g'> | <d' fis' a'>1\\fermata")
ARIA_LH = ("d2 a, | a, a, | d d | a, a, | a, a, | d d | d a, | a, a, | d d | a, d | g, a, | d d | "
           "d a, | d a, | d a, | g, a, | a, a, | d1\\fermata")
ARIA_TXT = ("Glo -- ri -- a " + U(13) + " in ex -- cel -- sis De -- o. " + U(20) + " Et in ter -- ra pax " + U(19) +
            " ho -- mi -- ni -- bus bo -- nae vo -- lun -- ta -- tis. " + U(2) + " Al -- le -- lu -- " + U(8) +
            " ia, " + U(3) + " al -- le -- lu -- ia. " + U(3) + " A -- men. " + U(3))


def mk_aria():
    sc = mk_score({'V': ARIA_V, 'RH': ARIA_RH, 'LH': ARIA_LH}, (4, 4), (2, 'major'), [
        {'id': 'V', 'name': 'Soprano', 'abbr': 'S.', 'voices': [('1', 1, 'V')]},
        {'id': 'P', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
         'voices': [('1', 1, 'RH'), ('5', 2, 'LH')]}], time_symbol='common')
    set_verses(sc, 'V', '1', [ARIA_TXT], mode='attack')
    sc.title, sc.composer, sc.lyricist = 'Gloria in excelsis', 'CC0 setting for this corpus', 'Liturgical text (Latin)'
    sc.rights = 'Text public domain; music CC0'
    lay = voice_piano_layout(sc, vname='Soprano')
    opts = {'header': {'title': 'Gloria in excelsis', 'subtitle': 'Aria for soprano and keyboard',
                       'composer': 'anon. (CC0, 2026)', 'poet': 'Luke 2:14; liturgical'},
            'staff_size': 19, 'paper': 'a4', 'font': 'TeX Gyre Termes', 'breaks': [3, 6, 10, 13],
            'paper_extra': ['indent = 12\\mm', 'ragged-last = ##f']}
    return sc, lay, opts


# ======================================================================
# 2. Claudius, Abendlied: 6 German stanzas between closed SATB staves
# ======================================================================
MOND_S = ("d'4 | g'4 a' b' c'' | b' a'2 d''4 | d'' e'' d'' c'' | b' a'2 g'4 | c'' b' a' g' | "
          "a'( fis' g') d''4 | d'' b' c'' d'' | e'' d''2 b'4 | c'' a' b' c'' | b' a'2 d'4 | g' b' a' g' | "
          "c''4 b'8( a') g'2\\fermata")
MOND_CH = ['D', 'G', 'D/F#', 'G', 'C', 'G', 'D', 'G', 'G', 'C', 'G/B', 'Am', 'Em', 'D', 'G',
           'C', 'G', 'D', 'Em', 'D', '~', 'G', '-', 'G', 'Em', 'Am', 'G/B', 'C', 'D', 'G',
           'Am', 'D', 'G', 'C', 'G', 'D', 'G', 'G', 'Em', 'D', 'C', 'Am', 'G/D', 'D7', 'G']
MOND_V = [
    "Der Mond ist auf -- ge -- gan -- gen, die gold -- nen Stern -- lein pran -- gen am Him -- mel hell und klar; _ _ "
    "der Wald steht schwarz und schwei -- get, und aus den Wie -- sen stei -- get der wei -- ße Ne -- bel "
    "wun -- der -- _ bar.",
    "Wie ist die Welt so stil -- le und in der Dämm -- rung Hül -- le so trau -- lich und so hold! _ _ "
    "Als ei -- ne stil -- le Kam -- mer, wo ihr des Ta -- ges Jam -- mer ver -- schla -- fen und ver -- ges -- sen _ "
    "sollt.",
    "Seht ihr den Mond dort ste -- hen? Er ist nur halb zu se -- hen und ist doch rund und schön. _ _ "
    "So sind wohl man -- che Sa -- chen, die wir ge -- trost be -- la -- chen, weil uns -- re Au -- gen sie nicht _ "
    "sehn.",
    "Wir stol -- ze Men -- schen -- kin -- der sind ei -- tel ar -- me Sün -- der und wis -- sen gar nicht viel; _ _ "
    "wir spin -- nen Luft -- ge -- spin -- ste und su -- chen vie -- le Küns -- te und kom -- men wei -- ter von dem _ "
    "Ziel.",
    "Gott, laß dein Heil uns schau -- en, auf nichts Ver -- gäng -- lichs trau -- en, nicht Ei -- tel -- keit uns freun! _ _ "
    "Laß uns ein -- fäl -- tig wer -- den und vor dir hier auf Er -- den wie Kin -- der fromm und fröh -- lich _ "
    "sein!",
    "Wollst end -- lich son -- der Grä -- men aus die -- ser Welt uns neh -- men durch ei -- nen sanf -- ten Tod! _ _ "
    "Und wenn du uns ge -- nom -- men, laß uns in' Him -- mel kom -- men, du un -- ser Herr und un -- ser _ "
    "Gott!",
]


def mk_mond():
    sc = satb_from_soprano(MOND_S, MOND_CH, (4, 4), (1, 'major'), 7)
    set_verses(sc, 'S', '1', MOND_V, mode='attack')
    sc.title, sc.composer, sc.lyricist = 'Abendlied', 'CC0 melody and harmonisation', 'Matthias Claudius (1779)'
    sc.rights = 'Text public domain; music CC0'
    lay = closed_layout([{'voice': ('S', '1'), 'verses': [1, 2, 3, 4, 5, 6], 'place': 'below'}],
                        names=[['Sopran', 'Alt'], ['Tenor', 'Bass']], shorts=[['S.', 'A.'], ['T.', 'B.']])
    opts = {'header': {'title': 'Abendlied', 'subtitle': '„Der Mond ist aufgegangen“',
                       'poet': 'Text: Matthias Claudius, 1779', 'composer': 'Satz: anon. (CC0)'},
            'staff_size': 22, 'paper': 'a4', 'font': 'TeX Gyre Pagella', 'breaks': [3, 6, 9], 'page_breaks': [6],
            'paper_extra': ['indent = 14\\mm', 'system-system-spacing.basic-distance = #18'],
            'layout_extra': ['\\context { \\Lyrics \\override LyricText.font-size = #0.5 }']}
    return sc, lay, opts


# ======================================================================
# 3. Les anges dans nos campagnes: 4 French stanzas + refrain on one line
# ======================================================================
ANGES_S = ("a'4 a'8 a' a'4 c'' | c''4. bes'8 a'2 | a'4 g'8 g' a'4 c'' | a'4. g'8 f'2 | "
           "a'4 a'8 a' a'4 c'' | c''4. bes'8 a'2 | a'4 g'8 g' a'4 c'' | a'4. g'8 f'2 | "
           "c''2( d''8 c'' bes' a' | bes'2 c''8 bes' a' g' | a'2 bes'8 a' g' f' | g'4.) c'8 f'4 g' | "
           "a'4 bes' a' g' | f'1 | "
           "c''2( d''8 c'' bes' a' | bes'2 c''8 bes' a' g' | a'2 bes'8 a' g' f' | g'4.) c'8 f'4 g' | "
           "a'4 bes' a' g' | f'1\\fermata")
ANGES_V = [
    "Les an -- ges dans nos cam -- pa -- gnes ont en -- ton -- né l'hym -- ne des cieux, "
    "et l'é -- cho de nos mon -- ta -- gnes re -- dit ce chant mé -- lo -- di -- eux" + NB + ":",
    "Ber -- gers, pour qui cet -- te fê -- te" + NB + "? Quel est l'ob -- jet de tous ces chants" + NB + "? "
    "Quel vain -- queur, quel -- le con -- quê -- te mé -- ri -- te ces cris tri -- om -- phants" + NB + "?",
    "Ils an -- non -- cent la nais -- san -- ce du li -- bé -- ra -- teur d'Is -- ra -- ël, "
    "et pleins de re -- con -- nais -- san -- ce chan -- tent en ce jour so -- len -- nel" + NB + ":",
    "Cher -- chons tous l'heu -- reux vil -- la -- ge qui l'a vu naî -- tre sous ses toits" + NB + "; "
    "of -- frons -- lui le ten -- dre~hom -- ma -- ge et de nos cœurs et de nos voix" + NB + "!",
]
ANGES_REFRAIN = ("Glo -- " + U(15) + " ri -- a in ex -- cel -- sis De -- o" + NB + "! ") * 2


def mk_anges():
    sc = mk_score({'M': ANGES_S}, (4, 4), (-1, 'major'), [{'id': 'V', 'name': 'Voice', 'voices': [('1', 1, 'M')]}])
    sc.measures[7].right_bar = 'double'
    verses = [ANGES_V[0] + ' ' + ANGES_REFRAIN] + ANGES_V[1:]
    from synth.model import parse_lyric_text
    n_verse = sum(1 for m in sc.part('V').measures[:8] for ev in m['1'] if ev.kind == 'note')
    for k, v in enumerate(verses):
        n = len(parse_lyric_text(v))
        assert n == (n_verse + 48 if k == 0 else n_verse), (k, n, n_verse)
    set_verses(sc, 'V', '1', verses, mode='attack', strict=False)
    # stanza lines 2-4 stop before the refrain: no extender after their last syllable
    last = sc.part('V').measures[7]['1'][-1]
    for vn in (2, 3, 4):
        last.lyrics[vn].no_extend = True
    # refrain syllables (lyric line 1 only) are named 'refrain'
    for m in sc.part('V').measures[8:]:
        for ev in m['1']:
            if 1 in ev.lyrics:
                ev.lyrics[1].name = 'refrain'
    sc.title, sc.composer, sc.lyricist = 'Les anges dans nos campagnes', 'CC0 melody (after the French carol)', \
        'Traditional French carol (18th c.)'
    sc.rights = 'Text public domain; music CC0'
    lay = {'groups': [{'type': None, 'staves': [{'id': 'm', 'clef': 'treble', 'voices': [('V', '1')],
                                                 'lyrics': [{'voice': ('V', '1'), 'verses': [1, 2, 3, 4],
                                                             'place': 'below'}]}]}]}
    opts = {'header': {'title': 'Les anges dans nos campagnes', 'subtitle': 'Noël',
                       'poet': 'Paroles : traditionnel', 'composer': 'Mélodie : anon. (CC0)'},
            'staff_size': 21, 'paper': 'a4', 'font': 'C059', 'breaks': [3, 7, 11, 15],
            'paper_extra': ['indent = 0', 'ragged-last = ##f', 'system-system-spacing.basic-distance = #15'],
            'auto_beam_off_vocal': False}
    return sc, lay, opts


# ======================================================================
# 4. Veni, veni Emmanuel: Latin line + italic English translation line
# ======================================================================
VENI_S = ("e'4 | g' b' b' b' | a'8( c'') b'4 a'2 | r4 a' b' g' | e' g'8( a') fis'4 e' | d'2 r4 e'4 | "
          "g' b' b' b' | a'8( c'') b'4 a'2 | r4 a' b' g' | e' g'8( a') fis'4 e' | d'2 r4 d''4 | "
          "d''2 b'4 b' | a'4 b'8( c'') b'4 a'( | g'2.) a'4 | b' g' e' g' | a'8( g') fis'4 e'2\\fermata")
VENI_LA = ("Ve -- ni, ve -- ni, Em -- ma -- _ nu -- el, cap -- ti -- vum sol -- ve _ Is -- ra -- el, "
           "qui ge -- mit in ex -- si -- _ li -- o, pri -- va -- tus De -- i _ Fi -- li -- o. "
           "Gau -- de! Gau -- de! Em -- ma -- _ nu -- el _ na -- sce -- tur pro te, Is -- _ ra -- el.")
VENI_EN = ("O come, O come, Em -- man -- _ u -- el, and ran -- som cap -- tive _ Is -- ra -- el, "
           "that mourns in lone -- ly ex -- _ ile here un -- til the Son of _ God ap -- pear. "
           "Re -- joice! Re -- joice! Em -- man -- _ u -- el _ shall come to thee, O Is -- _ ra -- el.")


def mk_veni():
    sc = mk_score({'M': VENI_S}, (4, 4), (1, 'minor'), [{'id': 'V', 'name': 'Voice', 'voices': [('1', 1, 'M')]}])
    set_verses(sc, 'V', '1', [VENI_LA, VENI_EN], mode='attack')
    sc.lyric_line_attrs = {1: {'name': 'Latin'}, 2: {'name': 'translation', 'italic': True}}
    sc.title, sc.composer, sc.lyricist = 'Veni, veni, Emmanuel', 'CC0 modal melody', \
        'Latin hymn (18th c.); English tr. J. M. Neale (1851)'
    sc.rights = 'Texts public domain; music CC0'
    lay = {'groups': [{'type': None, 'staves': [{'id': 'm', 'clef': 'treble', 'voices': [('V', '1')],
                                                 'lyrics': [{'voice': ('V', '1'), 'verses': [1, 2], 'place': 'below',
                                                             'stanza': False, 'italic': [2],
                                                             'with': {2: ['\\override LyricText.font-size = #-1']}}]}]}]}
    opts = {'header': {'title': 'Veni, veni, Emmanuel', 'subtitle': 'O come, O come, Emmanuel',
                       'poet': 'Latin, 18th c.; tr. J. M. Neale, 1851', 'composer': 'Melody: anon. (CC0)'},
            'staff_size': 20, 'paper': 'letter', 'font': 'TeX Gyre Schola', 'breaks': [2, 5, 7, 10, 13],
            'paper_extra': ['indent = 0', 'ragged-last = ##f', 'system-system-spacing.basic-distance = #14'],
            'auto_beam_off_vocal': True}
    return sc, lay, opts


# ======================================================================
# 5. Calon Lân (Welsh): closed SATB, four independent lyric lines
#    (S above upper staff, A below it, T above lower staff, B below it)
# ======================================================================
CALON = {
    'S': "d''4. c''8 b'2 | c''4 e'' d''4. a'8 | b'2 r2 | r4 a' a' d'' | d''4. b'8 g'2 | c''2( a'2) | e''1 | d''1\\fermata",
    'A': "r4 g' g' g' | g' e' fis' fis' | g'4 e'2 e'4 | fis'2 fis'4 a' | g'2 e'2~ | e'2 fis'2 | g'1 | g'1\\fermata",
    'T': "b4 d'8 d' d'4 b | c'4 c' a2 | b4 b8 b g2 | a4 a a2( | b2 g2 | a1) | c'1 | b1\\fermata",
    'B': "g,2 b,4 g, | c2 d2 | e4 e c2 | d4 d fis, a, | g,2 e,2 | a,2( d2) | c1 | g,1\\fermata",
}
CALON_TXT = {
    'S': "Ca -- lon lân yn llawn da -- io -- ni, te -- cach yw na'r li -- li dlos: _ A -- men.",
    'A': "dim ond ca -- lon lân all ga -- nu, ca -- nu'r dydd a cha -- nu'r nos. _ A -- men.",
    'T': "Nid wy'n go -- fyn by -- wyd moe -- thus, aur y byd na'i ber -- lau mân: _ _ _ A -- men.",
    'B': "go -- fyn wyf am ga -- lon ha -- pus, ca -- lon o -- nest, ca -- lon lân. _ A -- men.",
}


def mk_calon():
    sc = mk_score(CALON, (4, 4), (1, 'major'), [
        {'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'voices': [('1', 1, 'S')]},
        {'id': 'A', 'name': 'Alto', 'abbr': 'A.', 'voices': [('1', 1, 'A')]},
        {'id': 'T', 'name': 'Tenor', 'abbr': 'T.', 'clefs': ['bass'], 'voices': [('1', 1, 'T')]},
        {'id': 'B', 'name': 'Bass', 'abbr': 'B.', 'clefs': ['bass'], 'voices': [('1', 1, 'B')]}])
    for pid, txt in CALON_TXT.items():
        set_verses(sc, pid, '1', [txt], mode='attack')
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.title, sc.composer, sc.lyricist = 'Calon Lân', 'CC0 four-part setting', 'Daniel James (Gwyrosydd), c. 1890'
    sc.lyric_placement = {'S': 'above', 'A': 'below', 'T': 'above', 'B': 'below'}
    sc.rights = 'Text public domain; music CC0'
    lay = closed_layout([{'voice': ('S', '1'), 'verses': [1], 'place': 'above'},
                         {'voice': ('A', '1'), 'verses': [1], 'place': 'below'}],
                        [{'voice': ('T', '1'), 'verses': [1], 'place': 'above'},
                         {'voice': ('B', '1'), 'verses': [1], 'place': 'below'}])
    lay['groups'][0]['staves'][0]['name'] = ['Soprano', 'Alto']
    lay['groups'][0]['staves'][1]['name'] = ['Tenor', 'Bass']
    opts = {'header': {'title': 'Calon Lân', 'subtitle': 'quodlibet: four lines of the hymn sung at once',
                       'poet': 'Geiriau: Daniel James (Gwyrosydd)', 'composer': 'Cerddoriaeth: anon. (CC0)'},
            'staff_size': 22, 'paper': 'a4', 'font': 'P052', 'breaks': [3],
            'paper_extra': ['indent = 16\\mm', 'ragged-last = ##f',
                            'system-system-spacing.basic-distance = #20'],
            'auto_beam_off_vocal': True}
    return sc, lay, opts


# ======================================================================
# 6. Amazing Grace: hymnal page, 3 stanzas underlaid + 3 as text block
# ======================================================================
AG_S = ("d'4 | g'2 b'8( g') | b'2 a'4 | g'2 e'4 | d'2 d'4 | g'2 b'8( g') | b'2 a'4 | d''2.~ | d''2 b'4 | "
        "d''4.( b'8) d''( b') | g'2 d'4 | e'4.( g'8) g'( e') | d'2 d'4 | g'2 b'8( g') | b'2 a'4 | g'2.~ | g'2")
AG_CH = ['D', 'G', '~', '~', 'G', 'D', 'Em', 'C', 'G', 'D7', 'G', '~', '~', 'G', 'D', 'D', '~', 'G',
         'G', '~', '-', '~', 'C', 'G', 'C', '~', 'Em', '~', 'G', 'D7', 'G', '~', '~', 'G/D', 'D7', 'G', '~']
AG_V = [
    "A -- maz -- ing _ grace! how sweet the sound That saved a _ wretch like me! "
    "I once _ was _ lost, but now _ am _ found, Was blind, but _ now I see.",
    f"{AP}Twas grace that _ taught my heart to fear, And grace my _ fears re -- lieved; "
    "How pre -- _ cious _ did that grace _ ap -- _ pear The hour I _ first be -- lieved!",
    "Through man -- y _ dan -- gers, toils, and snares, I have al -- _ read -- y come; "
    f"{AP}Tis grace _ hath _ brought me safe _ thus _ far, And grace will _ lead me home.",
    # stanzas 4-6: underlaid only in the alternative truth
    "The Lord has _ prom -- ised good to me, His word my _ hope se -- cures; "
    "He will _ my _ shield and por -- _ tion _ be, As long as _ life en -- dures.",
    "Yea, when this _ flesh and heart shall fail, And mor -- tal _ life shall cease, "
    "I shall _ pos -- _ sess, with -- in _ the _ veil, A life of _ joy and peace.",
    "The earth shall _ soon dis -- solve like snow, The sun for -- _ bear to shine; "
    "But God, _ who _ called me here _ be -- _ low, Will be for -- _ ev -- er mine.",
]
AG_BLOCK = [
    {'label': '4.', 'lines': ['The Lord has promised good to me,', 'His word my hope secures;',
                              'He will my shield and portion be,', 'As long as life endures.']},
    {'label': '5.', 'lines': ['Yea, when this flesh and heart shall fail,', 'And mortal life shall cease,',
                              'I shall possess, within the veil,', 'A life of joy and peace.']},
    {'label': '6.', 'lines': ['The earth shall soon dissolve like snow,', 'The sun forbear to shine;',
                              'But God, who called me here below,', 'Will be forever mine.']},
]


def mk_grace():
    sc = satb_from_soprano(AG_S, AG_CH, (3, 4), (1, 'major'), 7)
    set_verses(sc, 'S', '1', AG_V[:3], mode='attack')
    sc.text_stanzas = copy.deepcopy(AG_BLOCK)
    sc.title, sc.composer, sc.lyricist = 'Amazing Grace', 'NEW BRITAIN (American folk melody, 1829); ' \
        'harmonisation CC0', 'John Newton (1779)'
    sc.rights = 'Melody and text public domain; harmonisation CC0'
    lay = closed_layout([{'voice': ('S', '1'), 'verses': [1, 2, 3], 'place': 'below'}])
    opts = {'header': {'title': 'Amazing Grace', 'meter': 'C.M.', 'poet': 'John Newton, 1779',
                       'composer': 'NEW BRITAIN, Virginia Harmony, 1831; harm. anon. (CC0)'},
            'staff_size': 18, 'paper': 'letter', 'font': 'Liberation Serif', 'breaks': [4, 8, 12],
            'paper_extra': ['indent = 0', 'ragged-last = ##f', 'page-count = #1',
                            'system-system-spacing.basic-distance = #12'],
            'layout_extra': ['\\context { \\Score \\remove "Bar_number_engraver" }'],
            'auto_beam_off_vocal': True,
            'markup_after': stanza_block(AG_BLOCK, [[0, 1], [2]])}
    return sc, lay, opts


def grace_underlaid(sc):
    """alternative truth: stanzas 4-6 syllabified and underlaid as lines 4-6"""
    set_verses(sc, 'S', '1', AG_V, mode='attack')
    sc.text_stanzas = []
    return sc


# ======================================================================
# 7. Tu scendi dalle stelle (Italian): elisions, 6/8, voice + piano
# ======================================================================
TU_V = ("d'8 | g'4 a'8 b'4 c''8 | d''4 c''8 b'4 a'8 | b'4. a'4 d'8 | g'4 a'8 b'4 c''8 | d''4 e''8 d''4 c''8 | "
        "b'4. a'4 b'8 | c''4 b'8 a'4 g'8 | a'4 b'8 g'4. | e''4 d''8 c''4 b'8 | a'4 g'8 fis'4. | "
        "g'4 a'8 b'4 c''8 | d''4. r4 d''8 | e''4 d''8 c''4 b'8 | a'4 b'8 c''4 a'8 | a'4. g'4.\\fermata")
G_, D_, D7_, C_ = "<b d' g'>4.", "<a d' fis'>4.", "<a c' fis'>4.", "<c' e' g'>4."
TU_RH = ("r8 | " + " | ".join(f"{a} {b}" for a, b in [
    (G_, G_), (G_, D_), (G_, D7_), (G_, G_), (G_, G_), (G_, D_), (C_, D_), (D_, G_), (C_, G_), (D_, D7_),
    (G_, G_), (G_, D_), (C_, G_), (D_, D7_), (D_, G_ + "\\fermata")]))
TU_LH = "r8 | " + " | ".join(["<g, d>2."] * 14 + ["<g, d>2.\\fermata"])
TU_V1 = ("Tu scen -- di dal -- le stel -- le~o Re del Cie -- lo, e vie -- ni~in u -- na grot -- ta~al fred -- do~e~al "
         "ge -- lo. O Bam -- bi -- no mio di -- vi -- no, io ti ve -- do qui~a tre -- mar; o Dio be -- a -- to! "
         "Ah, quan -- to ti co -- stò l'a -- ver -- mi~a -- ma -- to!")
TU_V2 = ("A te, che sei del mon -- do~il Cre -- a -- to -- re, man -- ca -- no pan -- ni~e fuo -- co,~o mio "
         "Si -- gno -- re. Ca -- ro~e -- let -- to par -- go -- let -- to, quan -- to que -- sta po -- ver -- tà "
         "più m'in -- na -- mo -- ra, giac -- ché ti fe -- ce~a -- mor po -- ve -- ro~an -- co -- ra!")


def mk_tu():
    sc = mk_score({'V': TU_V, 'RH': TU_RH, 'LH': TU_LH}, (6, 8), (1, 'major'), [
        {'id': 'V', 'name': 'Canto', 'abbr': '', 'voices': [('1', 1, 'V')]},
        {'id': 'P', 'name': 'Pianoforte', 'abbr': 'Pf.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
         'voices': [('1', 1, 'RH'), ('5', 2, 'LH')]}])
    set_verses(sc, 'V', '1', [TU_V1, TU_V2], mode='attack')
    sc.title, sc.composer, sc.lyricist = 'Tu scendi dalle stelle', 'CC0 pastorale setting', \
        'S. Alfonso Maria de’ Liguori (1754)'
    sc.rights = 'Text public domain; music CC0'
    lay = voice_piano_layout(sc, lyrics=[{'voice': ('V', '1'), 'verses': [1, 2], 'place': 'below'}], vname='Canto')
    opts = {'header': {'title': 'Tu scendi dalle stelle', 'subtitle': 'Pastorale',
                       'poet': 'Parole di S. Alfonso M. de’ Liguori', 'composer': 'Musica: anon. (CC0)'},
            'staff_size': 20, 'paper': 'a4', 'font': 'URW Bookman', 'breaks': [3, 6, 9, 12],
            'paper_extra': ['indent = 14\\mm', 'ragged-last = ##f'],
            'auto_beam_off_vocal': True}
    return sc, lay, opts


# ======================================================================
# 8. Dejlig er jorden / Fairest Lord Jesus: five stacked verses in four
#    languages (EN, DA, SV, NO, DA), sans-serif lyrics, verse-only skip
# ======================================================================
DEJ_S = ("d'2 d'4 | e'2 fis'4 | d'2. | fis'2 g'4 | a'2 a'4 | b'4 a'2 | d''2 cis''4 | b'2 a'4 | g'4 fis' e' | d'2. | "
         "fis'2 fis'4 | g'2 g'4 | a'2. | b'2 b'4 | a'2 g'4 | fis'2. | a'2 b'4 | a'2 fis'4 | g'4 fis' e' | d'2.\\fermata")
DEJ_V = [
    "Fair -- est Lord Je -- sus, Rul -- er of all na -- ture, O thou of God and man the Son, "
    "Thee will I cher -- ish, Thee will I hon -- or, Thou, my soul's glo -- ry, joy, and crown.",
    "Dej -- lig er jor -- den, præg -- tig er Guds him -- mel, skøn er sjæ -- le -- nes pil -- grims -- gang. "
    "Gen -- nem de fag -- re ri -- ger på jor -- den går vi til Pa -- ra -- dis med sang.",
    "Här -- lig är jor -- den, här -- lig är Guds him -- mel, skön är sjä -- lar -- nas pil -- grims -- gång. "
    "Ge -- nom de fag -- ra ri -- ken på jor -- den gå vi till pa -- ra -- dis med sång.",
    "Dei -- lig er jor -- den, prek -- tig er Guds him -- mel, skjønn er sje -- le -- nes pil -- grims -- gang. "
    "Gjen -- nom de fag -- re ri -- ker på jor -- den går vi til pa -- ra -- dis med sang.",
    "Ti -- der skal kom -- me, ti -- der skal hen -- rul -- le, slægt skal føl -- ge slæg -- _ ters gang; "
    "al -- drig for -- stum -- mer to -- nen fra him -- len i sjæ -- lens gla -- de pil -- grims -- sang.",
]


def mk_dejlig():
    sc = mk_score({'M': DEJ_S}, (3, 4), (2, 'major'), [{'id': 'V', 'name': 'Voice', 'voices': [('1', 1, 'M')]}])
    set_verses(sc, 'V', '1', DEJ_V, mode='attack')
    sc.lyric_line_attrs = {1: {'name': 'en'}, 2: {'name': 'da'}, 3: {'name': 'sv'}, 4: {'name': 'no'},
                           5: {'name': 'da'}}
    sc.title, sc.composer, sc.lyricist = 'Dejlig er jorden / Fairest Lord Jesus', 'CC0 melody', \
        'B. S. Ingemann (1850); R. S. Willis (1850); C. Bååth-Holmberg (1884)'
    sc.rights = 'Texts public domain; music CC0'
    lay = {'groups': [{'type': None, 'staves': [{'id': 'm', 'clef': 'treble', 'voices': [('V', '1')],
                                                 'lyrics': [{'voice': ('V', '1'), 'verses': [1, 2, 3, 4, 5],
                                                             'place': 'below',
                                                             'labels': {1: '1. EN', 2: '2. DA', 3: '3. SV',
                                                                        4: '4. NO', 5: '5. DA'}}]}]}]}
    opts = {'header': {'title': 'Dejlig er jorden', 'subtitle': 'Härlig är jorden · Deilig er jorden · Fairest Lord Jesus',
                       'poet': 'Ingemann 1850 · Bååth-Holmberg 1884 · Willis 1850',
                       'composer': 'Melodi: CC0'},
            'staff_size': 19, 'paper': 'a4', 'font': 'TeX Gyre Heros', 'breaks': [5, 9, 15],
            'paper_extra': ['indent = 0', 'ragged-last = ##f', 'system-system-spacing.basic-distance = #16'],
            'auto_beam_off_vocal': True}
    return sc, lay, opts


# ======================================================================
# catalog
# ======================================================================
CLOSED = [['Soprano', 'Alto'], ['Tenor', 'Bass']]
PAPER = [244, 243, 238]

ITEMS = [
    dict(id='lyr01-gloria-melisma-latin', limitations=['Melismatic 16th runs are auto-beamed by LilyPond; truth carries no <beam> elements.', 'Extenders that cross a system break are printed in two pieces; truth has one <extend/> on the syllable.'], title='Gloria in excelsis - aria with very long melismas (Latin)',
         make=mk_aria,
         edge_cases=['long_melisma', 'melisma_21_notes', 'sixteenth_note_runs', 'extender_line',
                     'extender_across_system_break', 'extender_across_barline', 'hyphen_across_melisma',
                     'melisma_with_tie', 'slurred_melisma', 'latin_text', 'voice_piano', 'must_not_split',
                     'single_verse'],
         expected={'must_not_split': True, 'shared_staves': [],
                   'notes': 'Two parts: Soprano (one staff, all lyrics) and Piano (ONE part with two staves - never '
                            'split into RH/LH parts). 34 syllables, all lyric number 1. Melismas: "a" of Gloria (14 '
                            'notes), "o" of Deo (21 notes, crosses a system break), "pax" (20 notes incl. a tie, '
                            'crosses a system break), "lu" of the first Alleluia (9 notes, hyphenated melisma: '
                            'syllabic middle, no extend). Word-final melismas carry <extend/>. Melisma notes must '
                            'NOT receive lyric elements. Beams are left to LilyPond (truth has no <beam>).'},
         license='Text: public domain (Latin liturgy, Luke 2:14). Music: CC0-1.0 (own composition).',
         source='Own composition for this corpus; Latin liturgical text.',
         attribution=att('Text: "Gloria in excelsis Deo ... Alleluia, Amen" - Latin liturgical text, public domain.',
                         'Music: original CC0 composition (2026) for the OMR lyrics challenge set.'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5101, mode='gray', jpeg=45, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 4},
                 {'op': 'rotate', 'deg': 1.2},
                 {'op': 'lighting', 'gradient': 0.10, 'angle': 20},
                 {'op': 'blur', 'sigma': 0.8}, {'op': 'noise', 'sigma': 6}]),
             'scan-mild.pdf': dict(dpi=300, seed=5102, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 2}, {'op': 'rotate', 'deg': 0.5},
                 {'op': 'noise', 'sigma': 2}]),
             'scan-severe.pdf': dict(dpi=150, seed=5103, mode='gray', jpeg=20, ops=[
                 {'op': 'paper', 'color': [238, 236, 228], 'texture': 6},
                 {'op': 'rotate', 'deg': -3.5, 'fill': [238, 236, 228]},
                 {'op': 'motion', 'length': 6, 'angle': 20}, {'op': 'noise', 'sigma': 10},
                 {'op': 'saltpepper', 'amount': 0.002}]),
         }),
    dict(id='lyr02-abendlied-6-stanzas-de', limitations=['Lyrics are encoded on the Soprano only; Alto, Tenor and Bass share the rhythm but carry no lyrics in truth.', 'scan.pdf and scan-severe.pdf put both engraved pages side by side on one 2-up sheet; the truth is page-agnostic.'], title='Abendlied (Der Mond ist aufgegangen) - 6 German stanzas, closed SATB',
         make=mk_mond,
         edge_cases=['stacked_verses_6', 'verse_numbers', 'german_umlauts', 'eszett', 'hyphenated_compounds',
                     'apostrophe_in_word', 'punctuation', 'satb_closed', 'lyrics_between_staves',
                     'extender_line', 'hyphen_across_melisma', 'pickup', 'multi_page', 'two_up_spread'],
         expected={'must_not_split': False, 'shared_staves': CLOSED,
                   'notes': 'Closed score: split each staff into two parts -> Soprano, Alto, Tenor, Bass. The six '
                            'stanza lines between the staves belong to the SOPRANO (truth puts lyric numbers 1-6 on '
                            'the soprano only; alto/tenor/bass sing the same rhythm). Verse numbers "1." .. "6." '
                            'are labels, not lyric text. Keep ä ö ü ß and the apostrophe in "in\'" exactly. 2 '
                            'engraved pages; scan.pdf and scan-severe.pdf put both pages side by side on ONE sheet '
                            '(2-up), so the converter must read the left half then the right half.'},
         license='Text: public domain (M. Claudius, 1779). Music: CC0-1.0 (own melody and harmonisation).',
         source='Own composition; text Matthias Claudius, "Abendlied" (1779), stanzas 1-6.',
         attribution=att('Text: Matthias Claudius, "Abendlied" ("Der Mond ist aufgegangen"), 1779 - public domain.',
                         'Melody and SATB harmonisation: original CC0 (harmonisation by the corpus voice-leading solver).'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5201, mode='gray', jpeg=50,
                              page_ops=[{'op': 'spread', 'reduce': 0.707, 'gap_mm': 4}], ops=[
                                  {'op': 'paper', 'color': [243, 242, 236], 'texture': 5},
                                  {'op': 'gutter', 'side': 'center', 'width': 0.05, 'dark': 0.5},
                                  {'op': 'rotate', 'deg': 0.8}, {'op': 'blur', 'sigma': 0.6},
                                  {'op': 'noise', 'sigma': 5}]),
             'scan-mild.pdf': dict(dpi=300, seed=5202, mode='rgb', jpeg=60,
                                   page_ops=[{'op': 'page_scale', 'factors': [1.0, 0.965]}], ops=[
                                       {'op': 'paper', 'color': [240, 232, 205], 'texture': 5, 'fibers': True},
                                       {'op': 'rotate', 'deg': -0.5, 'fill': [240, 232, 205]},
                                       {'op': 'noise', 'sigma': 3}]),
             'scan-severe.pdf': dict(dpi=300, seed=5203, mode='bw', jpeg=None,
                                     binarize={'style': 'thin_photocopy', 'threshold': 112, 'noise': 24, 'blur': 0.5},
                                     page_ops=[{'op': 'spread', 'reduce': 0.707, 'gap_mm': 4}], ops=[
                                         {'op': 'dropout', 'amount': 0.3},
                                         {'op': 'paper', 'color': [246, 246, 246], 'texture': 6},
                                         {'op': 'rotate', 'deg': 2.5}, {'op': 'speckle', 'per_mpx': 200},
                                         {'op': 'saltpepper', 'amount': 0.001}]),
         }),
    dict(id='lyr03-anges-refrain-fr', limitations=['The refrain text is printed once (line 1) and encoded only as lyric number 1; a converter that copies it into lines 2-4 will differ from this truth.', 'French no-break spaces (U+00A0) before ; : ! ? are part of the syllable text.'], title='Les anges dans nos campagnes - 4 French stanzas + shared refrain line',
         make=mk_anges,
         edge_cases=['refrain_shared_line', 'stacked_verses_4', 'verse_numbers', 'french_diacritics',
                     'oe_ligature', 'diaeresis', 'french_punctuation_nbsp', 'apostrophe_elision', 'elision_tie',
                     'long_melisma', 'hyphen_across_melisma', 'melody_only', 'phone_photo', 'rotated_90'],
         expected={'must_not_split': False, 'shared_staves': [],
                   'notes': 'Single melody part. Verse section (bars 1-8): four stacked lines, lyric numbers 1-4. '
                            'Refrain (bars 9-20): text printed ONCE on the first line and sung after every stanza; '
                            'truth encodes it only as lyric number 1 (lyric/@name="refrain"); lines 2-4 have no '
                            'syllables in the refrain. "Glo-" is held over a 16-note melisma (hyphen, syllabic '
                            'begin, no extend). Stanza 4 has an elision "dre‿hom" (two syllables on one note: '
                            '<elision>). French punctuation is preceded by a no-break space (U+00A0) exactly as '
                            'printed; a lenient scorer may normalise whitespace. scan-severe.pdf is a phone photo '
                            'rotated 90 degrees.'},
         license='Text: public domain (traditional French carol). Music: CC0-1.0 (own melody after the carol).',
         source='Own melody; traditional French text "Les anges dans nos campagnes" (stanzas 1-4).',
         attribution=att('Text: "Les anges dans nos campagnes", traditional French carol (18th c.) - public domain.',
                         'Melody: CC0, written for this corpus after the shape of the traditional GLORIA tune.'),
         scans={
             'scan.pdf': dict(dpi=200, seed=5301, mode='rgb', jpeg=50, ops=[
                 {'op': 'paper', 'color': [236, 228, 210], 'texture': 6},
                 {'op': 'curl', 'side': 'right', 'amp': 18, 'width': 0.3, 'fill': [236, 228, 210]},
                 {'op': 'phone', 'margin': 0.06, 'bg': [95, 80, 62], 'keystone': 0.05, 'jitter': 0.015},
                 {'op': 'lighting', 'gradient': 0.25, 'vignette': 0.25, 'tint': [255, 244, 225]},
                 {'op': 'blur', 'sigma': 1.0}, {'op': 'noise', 'sigma': 4, 'chroma': 2}]),
             'scan-mild.pdf': dict(dpi=300, seed=5302, mode='rgb', jpeg=60, ops=[
                 {'op': 'paper', 'color': [242, 234, 212], 'texture': 4},
                 {'op': 'rotate', 'deg': 0.7, 'fill': [242, 234, 212]}]),
             'scan-severe.pdf': dict(dpi=150, seed=5303, mode='rgb', jpeg=25, ops=[
                 {'op': 'paper', 'color': [232, 224, 205], 'texture': 7},
                 {'op': 'curl', 'side': 'left', 'amp': 26, 'width': 0.35, 'fill': [232, 224, 205]},
                 {'op': 'phone', 'margin': 0.08, 'bg': [60, 55, 50], 'keystone': 0.09, 'jitter': 0.03},
                 {'op': 'lighting', 'gradient': 0.45, 'vignette': 0.4, 'blotch': 0.2},
                 {'op': 'motion', 'length': 7, 'angle': 75}, {'op': 'rot90', 'k': 1},
                 {'op': 'noise', 'sigma': 7, 'chroma': 3}]),
         }),
    dict(id='lyr04-veni-latin-italic-en', limitations=['The translation line is lyric number 2 with font-style=italic; its smaller font size is not encoded.'], title='Veni, veni, Emmanuel - Latin with italic English translation line',
         make=mk_veni,
         edge_cases=['translation_line_italic', 'two_languages', 'latin_text', 'unnumbered_lyric_lines',
                     'smaller_font_translation', 'extender_line', 'extender_across_barline',
                     'hyphen_across_melisma', 'rests_between_phrases', 'pickup', 'minor_key',
                     'halftone_moire', 'rotated_180'],
         expected={'must_not_split': False, 'shared_staves': [],
                   'notes': 'Single melody part with two lyric lines: line 1 Latin (roman), line 2 English '
                            'translation printed in a smaller ITALIC font. Truth: lyric number 1 (name "Latin") and '
                            'number 2 (name "translation", <text font-style="italic">). The italic line is a '
                            'translation, not a second stanza, but it is still underlaid note-by-note and must be '
                            'kept as its own lyric line. No verse numbers are printed. scan-severe.pdf is upside '
                            'down (180 degrees).'},
         license='Texts: public domain (Latin hymn; J. M. Neale 1851). Music: CC0-1.0 (own melody).',
         source='Own modal melody; Latin "Veni, veni, Emmanuel" stanza 1 + refrain; English tr. John Mason Neale (1851).',
         attribution=att('Text: "Veni, veni, Emmanuel", Latin hymn (Psalteriolum Cantionum, 1710) - public domain.',
                         'English translation: John Mason Neale, 1851 - public domain.',
                         'Melody: CC0 modal melody written for this corpus.'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5401, mode='gray', jpeg=55, ops=[
                 {'op': 'halftone', 'lpi': 100, 'angle': 45, 'tint': 0.10},
                 {'op': 'resample', 'factor': 0.83, 'filter': 'nearest'},
                 {'op': 'paper', 'color': PAPER, 'texture': 3},
                 {'op': 'rotate', 'deg': 1.5}, {'op': 'noise', 'sigma': 4}]),
             'scan-mild.pdf': dict(dpi=400, seed=5402, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 2}, {'op': 'rotate', 'deg': -0.6},
                 {'op': 'blur', 'sigma': 0.4}]),
             'scan-severe.pdf': dict(dpi=120, seed=5403, mode='gray', jpeg=30, ops=[
                 {'op': 'halftone', 'lpi': 45, 'angle': 30, 'tint': 0.15},
                 {'op': 'resample', 'factor': 0.77, 'filter': 'nearest'},
                 {'op': 'paper', 'color': [240, 239, 233], 'texture': 5},
                 {'op': 'rotate', 'deg': 1.0}, {'op': 'rot90', 'k': 2}, {'op': 'noise', 'sigma': 9}]),
         }),
    dict(id='lyr05-calon-lan-satb-4-lines-cy', limitations=['Printed lyric position is encoded as lyric/@placement (above/below) on every syllable.'], title='Calon Lân - closed SATB with four independent lyric lines (Welsh)',
         make=mk_calon,
         edge_cases=['lyrics_under_different_staves', 'lyrics_above_staff', 'four_lyric_lines_closed_score',
                     'independent_texts_per_voice', 'independent_rhythms', 'welsh_text', 'circumflex',
                     'apostrophe_contractions', 'satb_closed', 'extender_line', 'coffee_stain', 'foxing',
                     'bleed_through', 'cropped_edges'],
         expected={'must_not_split': False, 'shared_staves': CLOSED,
                   'notes': 'Closed score, 2 staves x 2 voices -> 4 parts. Each voice sings DIFFERENT words with '
                            'its own rhythm, and each has its own lyric line: Soprano text ABOVE the treble staff, '
                            'Alto text BELOW the treble staff, Tenor text ABOVE the bass staff (so two lines sit '
                            'between the staves: upper = Alto, lower = Tenor), Bass text BELOW the bass staff. Every '
                            'part has lyric number 1. Attaching a line to the wrong voice (e.g. the Alto line to the '
                            'Tenor) is an error. Welsh â and apostrophes (wy\'n, na\'r, na\'i, nu\'r) must be kept.'},
         license='Text: public domain (Daniel James, d. 1920). Music: CC0-1.0 (own four-part setting).',
         source='Own composition; text "Calon Lân" by Daniel James (Gwyrosydd), chorus and stanza 1 lines.',
         attribution=att('Text: Daniel James (Gwyrosydd, 1848-1920), "Calon Lân" - public domain.',
                         'Four-part quodlibet setting: original CC0 composition (not the John Hughes tune).'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5501, mode='rgb', jpeg=50, ops=[
                 {'op': 'paper', 'color': [240, 233, 214], 'texture': 5},
                 {'op': 'bleed', 'strength': 0.12, 'shift_mm': [4, -6], 'blur': 2.0},
                 {'op': 'foxing', 'n': 70, 'strength': 0.45},
                 {'op': 'stain', 'n': 1, 'radius_mm': [28, 34], 'strength': 0.5, 'where': [[0.62, 0.42]]},
                 {'op': 'rotate', 'deg': -1.0, 'fill': [240, 233, 214]}, {'op': 'noise', 'sigma': 3}]),
             'scan-mild.pdf': dict(dpi=600, seed=5502, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 2}, {'op': 'rotate', 'deg': 0.3},
                 {'op': 'noise', 'sigma': 2}]),
             'scan-severe.pdf': dict(dpi=300, seed=5503, mode='rgb', jpeg=25, ops=[
                 {'op': 'paper', 'color': [236, 226, 200], 'texture': 7},
                 {'op': 'bleed', 'strength': 0.25, 'shift_mm': [-3, 5], 'blur': 1.6},
                 {'op': 'stain', 'n': 2, 'radius_mm': [30, 45], 'strength': 0.75, 'fill': 0.45,
                  'where': [[0.35, 0.30], [0.7, 0.62]]},
                 {'op': 'foxing', 'n': 150, 'strength': 0.6},
                 {'op': 'crop', 'right': 18, 'left': 4, 'bottom': 6},
                 {'op': 'rotate', 'deg': 4.0, 'expand': True, 'fill': [30, 30, 32]},
                 {'op': 'noise', 'sigma': 6, 'chroma': 2}]),
         }),
    dict(id='lyr06-amazing-grace-textblock', limitations=["Stanzas 4-6 are a text block, encoded as <credit> (credit-type 'lyrics') in truth.musicxml; truth-underlaid.musicxml is the alternative with them syllabified as lyric lines 4-6 (syllabification by the corpus author).", 'Lyrics are encoded on the Soprano only (lower voices share the rhythm).'], title='Amazing Grace - hymnal page, stanzas 4-6 as text block below the music',
         make=mk_grace, alt_truths={'truth-underlaid.musicxml': grace_underlaid},
         edge_cases=['text_block_stanzas', 'two_column_text_block', 'stacked_verses_3', 'verse_numbers',
                     'typographic_apostrophes', 'punctuation', 'satb_closed', 'lyrics_between_staves', 'pickup',
                     'short_melisma_extenders', 'hyphen_across_melisma', 'pencil_annotations', 'circled_notes',
                     'punch_holes', 'staple', 'binarized_thick'],
         expected={'must_not_split': False, 'shared_staves': CLOSED,
                   'notes': 'Closed SATB hymn -> 4 parts. Stanzas 1-3 are underlaid between the staves and belong '
                            'to the SOPRANO (lyric numbers 1-3). Stanzas 4-6 are printed as a two-column TEXT BLOCK '
                            'below the music: they are not aligned to notes, so truth.musicxml carries them as '
                            '<credit> elements (credit-type "lyrics", one per stanza, label + lines). '
                            'truth-underlaid.musicxml is an alternative truth for converters that syllabify the '
                            'block and underlay it as lyric lines 4-6 (it has no credits). Pencil marks, circled '
                            'notes and handwritten words ("breathe", "rit." ...) in the scans are NOT part of the '
                            'music or lyrics. Apostrophes are typographic (U+2019).'},
         license='Melody (NEW BRITAIN, 1829/1831) and text (John Newton, 1779): public domain. Harmonisation: CC0-1.0.',
         source='NEW BRITAIN melody (Virginia Harmony 1831); text John Newton, Olney Hymns (1779); own harmonisation.',
         attribution=att('Text: John Newton, "Amazing Grace" (Olney Hymns, 1779), stanzas 1-6 - public domain.',
                         'Melody: NEW BRITAIN (American folk hymn, Virginia Harmony 1831) - public domain.',
                         'SATB harmonisation: generated by the corpus voice-leading solver, CC0.'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5601, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 3},
                 {'op': 'pencil', 'circles': 5, 'ticks': 6, 'lines': 2,
                  'words': ['breathe', 'rit.', 'p', 'v.3 men only', 'cresc.']},
                 {'op': 'holes', 'n': 2, 'side': 'left', 'diam_mm': 6, 'offset_mm': 11, 'spacing_mm': 80},
                 {'op': 'staple', 'corner': 'tl', 'angle': 35},
                 {'op': 'rotate', 'deg': 0.6}, {'op': 'noise', 'sigma': 4}]),
             'scan-mild.pdf': dict(dpi=200, seed=5602, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 2},
                 {'op': 'holes', 'n': 2, 'side': 'left', 'diam_mm': 6, 'offset_mm': 11, 'spacing_mm': 80},
                 {'op': 'fold', 'y': 0.48, 'dark': 0.12}, {'op': 'rotate', 'deg': -0.3}]),
             'scan-severe.pdf': dict(dpi=200, seed=5603, mode='bw', jpeg=None,
                                     binarize={'style': 'thick_photocopy', 'threshold': 200, 'noise': 16, 'blur': 0.8},
                                     ops=[{'op': 'ink', 'weight': 1},
                                          {'op': 'paper', 'color': PAPER, 'texture': 6},
                                          {'op': 'pencil', 'circles': 8, 'ticks': 4, 'lines': 3, 'alpha': 0.9,
                                           'words': ['breathe!', 'p', 'alto only', 'slower', 'v.2 tacet']},
                                          {'op': 'holes', 'n': 4, 'side': 'left', 'diam_mm': 5.5, 'offset_mm': 10,
                                           'spacing_mm': 70},
                                          {'op': 'staple', 'corner': 'tl', 'angle': 50},
                                          {'op': 'rotate', 'deg': -2.0}, {'op': 'speckle', 'per_mpx': 300}]),
         }),
    dict(id='lyr07-tu-scendi-elisions-it', limitations=['Elision symbols are encoded as <elision>U+203F</elision> between the text parts.'], title='Tu scendi dalle stelle - Italian elisions, voice and piano',
         make=mk_tu,
         edge_cases=['elision_tie', 'multiple_elisions_one_note', 'elision_after_comma', 'italian_text',
                     'accented_vowels', 'apostrophes', 'stacked_verses_2', 'verse_numbers', 'compound_meter_6_8',
                     'pickup', 'voice_piano', 'must_not_split', 'book_scan', 'page_curl', 'gutter_shadow',
                     'cropped_edges'],
         expected={'must_not_split': True, 'shared_staves': [],
                   'notes': 'Two parts: Canto (voice, 2 stanzas = lyric numbers 1-2) and Pianoforte (ONE part, two '
                            'staves - never split). Elisions (two or three syllables sung on one note, joined by the '
                            'elision tie "‿") are a single <lyric> with <elision> between the <text> parts, e.g. '
                            '"do‿e‿al" = text do (end) + elision + e (single) + elision + al (single). Do not split an '
                            'elided group over several notes and do not drop the parts after the tie. Apostrophes '
                            '(l\'a-, m\'in-) and accents (stò, tà, più, ché) must be kept.'},
         license='Text: public domain (St Alphonsus Liguori, 1754). Music: CC0-1.0 (own pastorale setting).',
         source='Own composition; text "Tu scendi dalle stelle" (S. Alfonso Maria de\' Liguori), stanzas 1-2.',
         attribution=att('Text: S. Alfonso Maria de’ Liguori, "Tu scendi dalle stelle" (1754) - public domain.',
                         'Music: original CC0 pastorale (not the traditional tune).'),
         scans={
             'scan.pdf': dict(dpi=300, seed=5701, mode='rgb', jpeg=45, ops=[
                 {'op': 'paper', 'color': [238, 230, 208], 'texture': 5, 'fibers': True},
                 {'op': 'curl', 'side': 'left', 'amp': 24, 'width': 0.32, 'fill': [238, 230, 208]},
                 {'op': 'gutter', 'side': 'left', 'width': 0.08, 'dark': 0.6},
                 {'op': 'lighting', 'gradient': 0.12, 'vignette': 0.15},
                 {'op': 'blur', 'sigma': 0.6}, {'op': 'noise', 'sigma': 3}]),
             'scan-mild.pdf': dict(dpi=300, seed=5702, mode='gray', jpeg=60, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 2}, {'op': 'rotate', 'deg': 0.4}]),
             'scan-severe.pdf': dict(dpi=200, seed=5703, mode='rgb', jpeg=18, ops=[
                 {'op': 'paper', 'color': [232, 222, 196], 'texture': 8},
                 {'op': 'curl', 'side': 'left', 'amp': 38, 'width': 0.4, 'fill': [232, 222, 196]},
                 {'op': 'gutter', 'side': 'left', 'width': 0.1, 'dark': 0.75},
                 {'op': 'crop', 'right': 20, 'top': 6},
                 {'op': 'rotate', 'deg': 7.0, 'expand': True, 'fill': [40, 38, 36]},
                 {'op': 'blur', 'sigma': 1.2}, {'op': 'noise', 'sigma': 6}]),
         }),
    dict(id='lyr08-dejlig-multilingual-scandi', limitations=["Language codes in lyric/@name (en, da, sv, no) are metadata, not printed text; the printed labels '1. EN' ... are not encoded."], title='Dejlig er jorden - five stacked verses in EN/DA/SV/NO',
         make=mk_dejlig,
         edge_cases=['multilingual_verses', 'scandinavian_characters', 'ae_ligature', 'o_slash', 'a_ring',
                     'stacked_verses_5', 'verse_labels_with_language', 'verse_specific_melisma',
                     'hyphen_across_skip', 'sans_serif_lyrics', 'melody_only', 'low_dpi_100', 'skew_10deg'],
         expected={'must_not_split': False, 'shared_staves': [],
                   'notes': 'Single melody part, five stacked lyric lines in four languages (1 English, 2 Danish, 3 '
                            'Swedish, 4 Norwegian, 5 Danish stanza 2), lyric numbers 1-5 (lyric/@name holds the '
                            'language code). Labels "1. EN" .. "5. DA" are verse labels, not lyrics. Line 5 has one '
                            'fewer syllable in phrase 3: the note after "slæg-" carries NO syllable in line 5 only '
                            '(hyphen continues), while lines 1-4 have a syllable there. Keep å æ ø ä ö exactly. '
                            'Lyrics are set in a sans-serif font. scan.pdf is only 100 dpi.'},
         license='Texts: public domain (Ingemann 1850, Willis 1850, Bååth-Holmberg 1884). Music: CC0-1.0 (own melody).',
         source='Own melody; texts "Dejlig er jorden" (B. S. Ingemann), Swedish "Härlig är jorden" '
                '(C. Bååth-Holmberg), Norwegian orthography of Ingemann, "Fairest Lord Jesus" (R. S. Willis).',
         attribution=att('Texts: B. S. Ingemann, "Dejlig er jorden" (1850), stanzas 1-2 and Norwegian spelling - public domain;',
                         'Cecilia Bååth-Holmberg, "Härlig är jorden" (1884) - public domain;',
                         'Richard Storrs Willis, "Fairest Lord Jesus" (1850) - public domain.',
                         'Melody: CC0, written for this corpus (not the Silesian folk tune).'),
         scans={
             'scan.pdf': dict(dpi=100, seed=5801, mode='gray', jpeg=40, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 3}, {'op': 'rotate', 'deg': 1.8},
                 {'op': 'blur', 'sigma': 0.5}, {'op': 'noise', 'sigma': 3}]),
             'scan-mild.pdf': dict(dpi=200, seed=5802, mode='rgb', jpeg=60, ops=[
                 {'op': 'paper', 'color': [218, 232, 240], 'texture': 4},
                 {'op': 'rotate', 'deg': -0.4, 'fill': [218, 232, 240]}]),
             'scan-severe.pdf': dict(dpi=150, seed=5803, mode='gray', jpeg=15, ops=[
                 {'op': 'paper', 'color': PAPER, 'texture': 6},
                 {'op': 'rotate', 'deg': 10.0, 'expand': True, 'fill': [250, 250, 250]},
                 {'op': 'motion', 'length': 5, 'angle': -10}, {'op': 'noise', 'sigma': 14},
                 {'op': 'saltpepper', 'amount': 0.004}]),
         }),
]
