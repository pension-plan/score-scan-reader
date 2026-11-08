"""coverage/notes items: the music (all composed for this corpus, CC0 1.0), layouts and expected results.

Each make() returns (score, layout, opts).  Pieces are short (10-16 bars) and dense in the target
symbols; everything else is kept plain (no dynamics, articulations or lyrics) so each symbol is
isolated and countable.  Stems: every stemmed note gets an explicit direction (standard rule unless
the source forces one with \\stemUp / \\stemDown) which the engraving is forced to use.
"""
from __future__ import annotations

from .rdsl import build_score

COMPOSER = 'OMR coverage corpus (CC0)'


def single_layout(pid, name, short=None, clef='treble', vkeys=('1',)):
    st = {'id': f'st{pid}', 'clef': clef, 'name': name, 'voices': [(pid, k) for k in vkeys], 'lyrics': []}
    if short:
        st['short'] = short
    return {'groups': [{'type': None, 'staves': [st]}]}


def piano_layout(pid, name='Piano', short='Pno.'):
    g = {'type': 'PianoStaff', 'name': name, 'short': short,
         'staves': [{'id': f'st{pid}s1', 'clef': 'treble', 'voices': [(pid, '1')], 'lyrics': []},
                    {'id': f'st{pid}s2', 'clef': 'bass', 'voices': [(pid, '5')], 'lyrics': []}]}
    return {'groups': [g]}


def opts_for(title, subtitle=None, staff_size=20, extra_paper=(), extra_layout=()):
    hdr = {'title': title, 'composer': COMPOSER}
    if subtitle:
        hdr['subtitle'] = subtitle
    return {'header': hdr, 'staff_size': staff_size, 'paper': 'a4',
            'paper_extra': ['system-system-spacing.basic-distance = #16'] + list(extra_paper),
            'layout_extra': list(extra_layout)}


def melody(title, subtitle, name, abbr, music, systems, clef='treble', staff_size=20):
    spec = dict(title=title, composer=COMPOSER, rights='CC0 1.0',
                parts=[dict(id='P1', name=name, abbr=abbr, instrument='other', clefs=[clef],
                            voices=[dict(key='1', music=music)])],
                systems=systems)
    sc = build_score(spec)
    return sc, single_layout('P1', name, clef=clef), opts_for(title, subtitle, staff_size)


def piano(title, subtitle, rh, lh, systems, staff_size=20, pages=None):
    spec = dict(title=title, composer=COMPOSER, rights='CC0 1.0',
                parts=[dict(id='P1', name='Piano', abbr='Pno.', instrument='piano', staves=2,
                            clefs=['treble', 'bass'],
                            voices=[dict(key='1', staff=1, music=rh), dict(key='5', staff=2, music=lh)])],
                systems=systems, pages=pages)
    sc = build_score(spec)
    return sc, piano_layout('P1'), opts_for(title, subtitle, staff_size)


# ======================================================================
# nt01  every note value, breve .. 64th, beamed and flagged
# ======================================================================
NT01 = r"""
\time 4/2 g'\breve |
a'1 b'1 |
c''1 d''2 e''2 |
f''\breve |
\time 4/4 e''4 c''4 a'4 f'4 |
g'8[ a'] b'8[ c''] d''8 e''8 f''8 d''8 |
e'8 f'8 g'8[ a'] b'8[ c''] d''4 |
c''16[ d'' e'' f''] g''16[ f'' e'' d''] c''16 b'16 a'16 g'16 f'4 |
e'16[ f' g' a'] b'16[ c'' d'' e''] f''16 g''16 a''16 b''16 c'''4 |
c'''32[ b'' a'' g'' f'' e'' d'' c''] b'32[ a' g' f' e' d' c' d'] e'32 f'32 g'32 a'32 b'8 c''4 |
d''32[ e'' f'' g'' a'' b'' c''' d'''] c'''32 b''32 a''32 g''32 f''8 e''2 |
c''64[ d'' e'' f'' g'' a'' b'' c''' d''' c''' b'' a'' g'' f'' e'' d''] c''64 b'64 a'64 g'64 f'16 e'8 d'2 |
e'64[ f' g' a' b' c'' d'' e''] f''64[ g'' a'' b'' c''' b'' a'' g''] f''64 e''64 d''64 c''64 b'16 a'8 g'2 |
\time 4/2 a'1 g'2 e'2 |
c''\breve
"""


def mk_nt01():
    return melody('Note Values', 'breve to sixty-fourth, beamed and flagged', 'Violin', 'Vln.', NT01,
                  [4, 3, 2, 2, 2, 2])


# ======================================================================
# nt02  dots and double dots on every value, dotted chords
# ======================================================================
NT02 = r"""
\time 3/2 c''1. |
d''2. b'2. |
g'2.. a'8 b'2 |
e'2. f'2. |
\time 4/4 g'4. a'8 b'4. c''8 |
d''4.. e''16 f''4.. d''16 |
c''8.[ d''16] e''8.[ f''16] g''16[ a''8.] b''8.[ g''16] |
a''8..[ g''32] f''8..[ e''32] d''16.[ c''32] b'16.[ a'32] g'8.[ a'16] |
b'16.[ c''32 d''16. e''32] f''32.[ g''64 a''32. b''64 c'''16 b''16] a''4. g''8 |
<e' g'>4. <f' a'>8 <g' b'>2 |
<c'' e''>2. <b' d''>4 |
\time 6/8 e''4. d''8.[ c''16 b'8] |
a'4. g'4. |
\time 4/4 c''16..[ d''64 e''16.. f''64] g''4.. a''16 b'4 |
a'2.. b'8 |
c''1
"""


def mk_nt02():
    return melody('Dotted Rhythms', 'single and double dots on every value', 'Oboe', 'Ob.', NT02,
                  [4, 3, 2, 2, 3, 2])


# ======================================================================
# nt03  chords of 2 to 6 notes (piano)
# ======================================================================
NT03_RH = r"""
\time 4/4 <e' g'>4 <e' g' c''>4 <d' f' g' b'>4 <c' e' g' c''>4 |
<c' e' g' c'' e''>2 <d' f' a' c'' e'' g''>2 |
<g' a'>4 <f' g' b'>4 <e' f' g'>8[ <d' e' g'>8] <c' d'>4 |
<fis' a' d''>8[ <g' bes' d''>8 <a' cis'' e''>8 <bes' d'' f''>8] <c'' ees'' g'' c'''>2 |
<a'' c''' e'''>4 <g'' b'' d''' g'''>4 <f'' a'' c''' f'''>2 |
<e' gis' b' e''>16[ <fis' a' c''>16 <gis' b' d''>16 <a' c'' e''>16] <b' d'' f''>16[ <c'' e'' g''>16 <d'' f'' a''>16 <e'' g'' b''>16] <c'' e'' a'' c'''>2 |
<c' e' g' c''>2. <b d' g'>4 |
<c' g' c'' e'' g''>1 |
<d' f' a'>2 <e' g' c'' e'' g'' c'''>2 |
<c' e' g' c''>1
"""
NT03_LH = r"""
\time 4/4 <c g>2 <g, d g>2 |
<c, c>2 <f, c f a>2 |
<e, b, e g>4 <a, e a>4 <d, a, d f>4 <g, d g b>4 |
<d a>8[ <g, d g>8 <a, e a>8 <bes, f bes>8] <c g c'>2 |
<a, e a>4 <g, d g b>4 <f, c f a>2 |
<e, b, e>2 <a, e a c'>2 |
<c, g, c e g>2. <g, d f>4 |
<c, c>1 |
<d, a, d f>2 <c, g, c e g c'>2 |
<c, g, c e>1
"""


def mk_nt03():
    return piano('Chord Study', 'chords of two to six notes', NT03_RH, NT03_LH, [3, 3, 2, 2])


# ======================================================================
# nt04  beam groupings
# ======================================================================
NT04 = r"""
\time 2/4 c''8[ d''] e''8[ f''] |
g''16[ f'' e'' d''] c''16[ b' a' g'] |
\time 3/4 a'8[ b' c'' d'' e'' f''] |
g''8[ e''] c''8[ a'] f'8[ d'] |
\time 6/8 e'8[ g' c''] e''8[ c'' g'] |
a'16[ b' c'' d'' e'' f''] g''16[ f'' e'' d'' c'' b'] |
c''8[ r8 c''8] d''8[ e''16 f''16 g''8] |
\time 4/4 a''8[ g'' f'' e'' d'' c'' b' a'] |
g'16[ a' b' c'' \sb d'' e'' f'' g''] a''16[ g'' f'' e'' \sb d'' c'' b' a'] |
b'8.[ c''16] d''16[ e''8.] f''8[ g''16 a''] b''16[ a'' g''8] |
c'''16[ r16 b''16 a''16] g''16[ r8 f''16] e''16[ r16 d''16 c''16] c''32[ d'' e'' f'' g''16 a''16] |
b''32[ a'' g'' f'' e'' d'' c'' b'] a'32[ g' f' e' d' e' f' g'] a'32[ b' c'' d''] e''16[ c''] g'8[ e'8] |
c''32[ d''16.] e''16.[ f''32] g''8[ f'' e'' d''] c''4 |
\time 3/4 e''8[ r8 d''8 r8 c''8 b'8] |
\time 4/4 <g' c''>8[ <a' d''> <b' e''> <c'' f''>] <d'' g''>2 |
c''1
"""


def mk_nt04():
    return melody('Beam Groups', 'two to eight notes per beam, beams over rests, secondary beams', 'Flute', 'Fl.',
                  NT04, [4, 3, 2, 2, 2, 3])


# ======================================================================
# nt05  flags and stem directions
# ======================================================================
NT05 = r"""
\time 3/4 c'8 d'8 e'8 f'8 g'8 a'8 |
b'8 c''8 d''8 e''8 f''8 g''8 |
a''16 g''16 f''16 e''16 d''8 c''8 b'4 |
g'16 f'16 e'16 d'16 c'8 d'8 e'4 |
c''32 d''32 e''32 f''32 g''16 a''16 b''8 c'''8 d'''4 |
a'32 g'32 f'32 e'32 d'16 c'16 b8 c'8 d'4 |
e''64 f''64 g''64 a''64 b''64 a''64 g''64 f''64 e''8 d''8 c''8 b'4 |
d'64 e'64 f'64 g'64 a'64 g'64 f'64 e'64 d'8 \stemDown c'8 d'8 e'4 |
\stemUp f''8 g''8 a''8 b''8 c'''4 |
\stemDown g'16 a'16 b'16 c''16 \stemUp d''16 e''16 f''16 g''16 \stemNeutral a''4 |
b'8 b'8 \stemUp b'8 b'8 \stemNeutral b'4 |
\stemUp g''2 \stemDown d'4 |
\stemNeutral e''4 c''4 a'4 |
g'2.
"""


def mk_nt05():
    return melody('Flags and Stems', 'unbeamed values, stems up and down, forced stems', 'Violin', 'Vln.', NT05,
                  [4, 3, 3, 4])


# ======================================================================
# nt06  ledger lines up to five above and below (piano)
# ======================================================================
NT06_RH = r"""
\time 4/4 a''4 c'''4 e'''4 g'''4 |
b'''2 c''''2 |
c'''8[ d''' e''' f'''] g'''8[ a''' b''' c''''] |
<a'' c''' e'''>2 <c''' e''' g''' b'''>2 |
c'4 a4 f4 d4 |
b,2 <c' e'>2 |
b16[ a g f] e16[ d c b,] c'8[ e' g' c''] |
g'''1 |
<f' a' c''>2 a'''2 |
c''1
"""
NT06_LH = r"""
\time 4/4 e,4 c,4 a,,4 f,,4 |
d,,2 c,,2 |
c,,8[ d,, e,, f,,] g,,8[ a,, b,, c,] |
<a,, c, e,>2 <f,, a,, c,>2 |
c'4 e'4 g'4 b'4 |
d''2 e''2 |
d''16[ c'' b' a'] g'16[ f' e' d'] c'8[ a f d] |
<c,, c,>1 |
<c' e' g'>2 <e' g' b'>2 |
c1
"""


def mk_nt06():
    return piano('Ledger Lines', 'one to five ledger lines above and below both staves', NT06_RH, NT06_LH,
                 [3, 3, 2, 2], staff_size=19)


# ======================================================================
# nt07  grace notes
# ======================================================================
NT07 = r"""
\time 4/4 \acc d''8 c''4 \app d''8 c''4 \grace e''16 d''4 \sgrace e''8 d''4 |
\grace { c''16[ d''] } e''4 \grace { e''16[ f'' g''] } a''4 \grace { a''16[ g'' f'' e''] } d''4 \grace { f''32[ e'' d'' c''] } b'4 |
\app e''4 d''2 \acc fis''8 g''4 \acc cis''8 d''4 |
\app { a'16[ b'] } c''4 \grace <e'' g''>8 f''4 \grace { g'16[ a' b'] } c''2 |
\acc g'8 a'4 \acc bes'8 a'4 \acc gis'8 a'4 \acc b'8 a'4 |
\grace { d'16[ e' f' g' a' b'] } c''2. \sgrace b'8 c''4 |
\grace { c'''32[ b'' a'' g''] } f''4 \grace { d''16 } e''4 \app f''16 e''4 \acc g''8 f''4 |
\sgrace c'''8 b''2 \app { c'''16[ b''] } a''2 |
\acc a''8 g''4 \acc f''8 e''4 \acc d''8 c''2 |
\grace { b'16[ c'' d''] } c''1
"""


def mk_nt07():
    return melody('Grace Notes', 'acciaccaturas, appoggiaturas, slashed and unslashed graces, grace groups',
                  'Flute', 'Fl.', NT07, [3, 3, 2, 2])


# ======================================================================
# nt08  cue notes (flute part with oboe / violin cues)
# ======================================================================
NT08_MAIN = r"""
\time 4/4 c''4 d''4 e''4 f''4 |
g''2 e''2 |
R1 |
R1 |
r2 g'4 a'4 |
b'2 c''2 |
R1 |
r4 e''4 d''4 c''4 |
R1 |
c''1
"""
NT08_CUE = r"""
s1 |
s1 |
e''8[^"Ob." f''] g''8[ a''] b''4 a''4 |
g''4. f''8 e''2 |
d''8[ c''] b'8[ a'] s2 |
s1 |
c''16[^"Vln._I" d'' e'' f''] g''4 g'2 |
f'4 s2. |
a'4^"Ob." b'4 <c'' e''>2 |
s1
"""


def mk_nt08():
    spec = dict(title='Cue Notes', composer=COMPOSER, rights='CC0 1.0',
                parts=[dict(id='P1', name='Flute', abbr='Fl.', instrument='other', clefs=['treble'],
                            voices=[dict(key='1', music=NT08_MAIN), dict(key='2', music=NT08_CUE, cue=True)])],
                systems=[3, 3, 4])
    sc = build_score(spec)
    return sc, single_layout('P1', 'Flute', vkeys=('1', '2')), opts_for('Cue Notes', 'flute part with cues', 20)


# ======================================================================
# nt09  tremolos (piano)
# ======================================================================
NT09_RH = r"""
\time 4/4 c''4:8 d''4:16 e''4:32 f''4:16 |
g''2:16 e''2:32 |
c''1:16 |
c''8:16[ d''8:16] e''8:32[ f''8:32] g''4:16 <c'' e'' g''>4:16 |
\trem 4 { c''16 e''16 } \trem 4 { d''16 f''16 } |
\trem 8 { <c'' e''>16 <g'' c'''>16 } |
\trem 8 { e'32 g'32 } \trem 8 { f'32 a'32 } |
<e' g' c''>2:16 <c' e' g' c''>2:32 |
c''1
"""
NT09_LH = r"""
\time 4/4 c4:16 g,4:16 c4:16 g,4:16 |
\trem 4 { c,16 c16 } \trem 4 { g,,16 g,16 } |
\trem 8 { c,16 c16 } |
<c g>2:16 <c e g>2:32 |
f,2:32 g,2:32 |
\trem 8 { c,32 g,32 } \trem 8 { c,32 g,32 } |
c,1:32 |
<c, c>1:16 |
c,1
"""


def mk_nt09():
    return piano('Tremolos', 'single-note and two-note tremolos', NT09_RH, NT09_LH, [3, 3, 3])


# ======================================================================
# nt10  piano etude mixing all note symbols
# ======================================================================
NT10_RH = r"""
\time 4/4 e''8[ c'' g' c''] e''16[ d'' c'' d''] e''8.[ g''16] |
<f'' a''>4 <e'' g''>8[ <d'' f''>] \acc d''8 c''4 r4 |
a'16[ b' c'' d'' e'' f'' g'' a''] b''32[ a'' g'' f'' e'' d'' c'' b'] c''4 |
<g' b' d'' g''>2 \grace { a''16[ b''] } c'''2 |
c'''16[ b'' a'' g''] f''8.[ e''16] d''4.. c''16 |
<e' g' c''>4. <f' a' d''>8 <g' b' e''>4 <a' c'' f''>4 |
g''8[ r8 a''8 b''8] c'''16[ d''' e''' f'''] g'''4 |
f'''32[ e''' d''' c''' b'' a'' g'' f''] e''8[ d''] c''4 b'4 |
\sgrace d''8 c''4 b'8[ a'] g'16[ a' b' c''] d''4 |
<c'' e'' g'' c'''>1
"""
NT10_LH = r"""
\time 4/4 c4 <e g>4 c4 <e g>4 |
f,8[ c f a] g,8[ d g b] |
a,4 <c e a>4 d4 <f a d'>4 |
g,,2 <g, d g b>2 |
f,16[ a, c f] a,16[ c f a] b,8[ d] g,4 |
c4. f,8 g,4 f,4 |
e,4 c,4 f,,4 g,,4 |
c,8[ e, g, c] d,4 g,4 |
a,,4 <e, a, c>4 g,,4 <d, g, b,>4 |
<c,, c,>1
"""


def mk_nt10():
    return piano('Etude in C', 'all note symbols in a piano texture', NT10_RH, NT10_LH, [3, 3, 4])
