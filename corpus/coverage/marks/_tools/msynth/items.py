"""The coverage/marks items: music (all composed for this corpus, CC0), layout, focus symbols,
expected-result notes and scan damage (params + seed, recorded verbatim in meta.json).

Pitches are absolute LilyPond (c' = C4).  See model.py for the note DSL."""
from __future__ import annotations

from .model import build_score

COMPOSER = 'OMR coverage corpus (CC0)'


def V(seed, dpi, ops, color='gray', fmt='jpeg', jpeg=None, description=''):
    v = {'seed': seed, 'dpi': dpi, 'color': color, 'ops': ops, 'format': fmt, 'description': description}
    if fmt == 'jpeg':
        v['jpeg'] = jpeg
    return v


def typical(seed, dpi, deg, jpeg, color='gray', noise=4, blur=0.5, paper=(246, 245, 241)):
    """an ordinary flatbed / office scan: slight skew, mild blur, sensor noise, JPEG"""
    ops = [{'op': 'paper', 'rgb': list(paper), 'texture': 2},
           {'op': 'rotate', 'deg': deg, 'bg': [236, 236, 236] if color == 'rgb' else 236},
           {'op': 'blur', 'sigma': blur},
           {'op': 'noise', 'sigma': noise}]
    if color == 'rgb':
        ops.insert(2, {'op': 'gradient', 'strength': 0.05})
        ops[-1]['chroma'] = 1.0
    return V(seed, dpi, ops, color=color, jpeg=jpeg,
             description=f'typical scan: {dpi} dpi {color}, {deg:+g} deg skew, blur {blur}, noise {noise}, '
                         f'JPEG q{jpeg}')


# ---------------------------------------------------------------------------------- mk01

def mk01():
    vln = r"""
      g'8-.[ a'-. b'-. c''-.] d''4-> d''-> |
      e''8-![ d''-! c''-! b'-!] a'4-- g'-- |
      fis'8-.[ g'-. a'-. b'-.] c''4-^ e''^^ |
      d''2-> d''4-- r4 |
      \break b'4-_( c''-_ d''-_ e''-_) |
      fis''8->[ e''-. d''-. c''-.] b'8->[ a'-. g'-. fis'-.] |
      e'4-- fis'_- g'-^ a'-^ |
      b'4-! b'-! b'-! r4 |
      \break <g d'>4-> <g d'>-> <d' a'>2-- |
      g''8-.[ fis''-. e''-. d''-.] c''8-^[ b'-^ a'-^ g'-^] |
      a'4->-. b'->-. c''---. d''---. |
      g'2.-> r4 |
    """
    return build_score('Bowing Study in Articulations', COMPOSER,
                       [{'id': 'P1', 'name': 'Violin', 'abbr': 'Vln.', 'staves': [{'clef': 'treble', 'music': vln}]}],
                       time=(4, 4), key=(1, 'major'))


# ---------------------------------------------------------------------------------- mk02

def mk02():
    fl = r"""
      c''4\trill a'8[ bes'] c''4 |
      d''4\mordent c''\prall bes'\turn |
      a'2\fermata r4\fermata |
      f'4\trill g'8[ a'] bes'4\mordent \breathe |
      \break c''4.\turn d''8 c''4\prall |
      bes'4\reverseturn a'\trill g'\mordent |
      f'2.\fermata \breathe |
      a'8[ bes'] c''4\trill \breathe d''\prall |
      \break e''4\turn f''\mordent g''\trill |
      a''2\fermata g''8[ f''] \breathe |
      e''4\reverseturn d''\prall c''\trill |
      f''2.\fermata |
    """
    return build_score('Pastorale with Ornaments', COMPOSER,
                       [{'id': 'P1', 'name': 'Flute', 'abbr': 'Fl.', 'staves': [{'clef': 'treble', 'music': fl}]}],
                       time=(3, 4), key=(-1, 'major'))


# ---------------------------------------------------------------------------------- mk03

def mk03():
    vc = r"""
      d2\pp\< e4 f\! |
      g2\p a4\> g\! |
      f4\mp e d c |
      d1\mf\> |
      \break a,1\p |
      bes,4\< c d e |
      f2\f e4\sfz d |
      a2\ff\> g4 f\! |
      \break e4\fp d e f |
      g4\sf a bes a\sf |
      g2\mf\< a4 bes |
      c'1\fff |
      \break bes2\fz\> a4 g |
      f2\mp e4\< f\! |
      d2\sfp e4\> cis\! |
      d1\ppp |
    """
    return build_score('Elegy in Dynamics', COMPOSER,
                       [{'id': 'P1', 'name': 'Violoncello', 'abbr': 'Vc.', 'staves': [{'clef': 'bass', 'music': vc}]}],
                       time=(4, 4), key=(-1, 'minor'))


# ---------------------------------------------------------------------------------- mk04

def mk04():
    rh = r"""
      \tempo{Andante|4|72} e''4-3\p d''-2 c''-1 b'-3 |
      <a'^1 c''^2 e''^4>2\arpeggio <gis'^1 b'^2 e''^5>2\arpeggio |
      a'4-1\< b'-2 c''-3 d''-4 |
      e''2-5\! <c'' e''>2\arpeggio |
      \break f''4-4\mf e''-3 d''-2 c''-1 |
      <b'^1 d''^2 f''^4>2\arpeggio <c''^1 e''^2 a''^5>2\arpeggio |
      b'4-2\> a'-1 gis'-3 a'-4 |
      <a' c'' e''>1\arpeggio\! |
      \break c''4-1\p e''-3 g''-5 e''-3 |
      <f'^1 a'^2 d''^5>2\arpeggio <e'^1 gis'^2 b'^3 e''^5>2\arpeggio |
      c''4-3\> b'-2 a'-1 gis'-2 |
      <a'^1 c''^2 e''^3 a''^5>1\arpeggio\pp |
    """
    lh = r"""
      a,4_5\sustainOn e_3 a_1 e_3 |
      <a, e>2\arpeggio\sustainOff\sustainOn <e, e>2\arpeggio\sustainOff\sustainOn |
      f,4_5\sustainOff\sustainOn c_2 f_1 c_2 |
      c,4_5\sustainOff\sustainOn g,_2 c_1 g,_2 |
      d,4_5\sustainOff\sustainOn a,_2 d_1 a,_2 |
      <g, d>2\arpeggio\sustainOff\sustainOn <a, e>2\arpeggio\sustainOff\sustainOn |
      e,4_5\sustainOff\sustainOn b,_2 e_1 b,_2 |
      a,1_5\sustainOff\sustainOn |
      c4_5\sustainOff\sustainOn g_2 c'_1 g_2 |
      <d, a,>2\sustainOff\sustainOn <e, b,>2\sustainOff\sustainOn |
      f,4_5\sustainOff\sustainOn c_3 e,_4\sustainOff\sustainOn b,_2 |
      <a,, a,>2\arpeggio\sustainOff\sustainOn r2\sustainOff |
    """
    return build_score('Nocturne Study (pedal, arpeggio, fingering)', COMPOSER,
                       [{'id': 'P1', 'name': 'Piano', 'abbr': 'Pno.',
                         'staves': [{'clef': 'treble', 'music': rh}, {'clef': 'bass', 'music': lh}]}],
                       time=(4, 4), key=(0, 'minor'))


# ---------------------------------------------------------------------------------- mk05

def mk05():
    ob = r"""
      \mark \tempo{Allegretto|4|112} d'4 fis'8[ a'] d''4 cis''8[ b'] |
      a'4. g'8 fis'4 e' |
      d'8[ e' fis' g'] a'4 b' |
      a'2 r2 |
      \break \mark \tempo{Meno mosso} b'2_"dolce" a'4 g' |
      fis'4. g'8 a'2 |
      b'4^"espress." cis'' d'' b' |
      a'2 g'4^"rit." fis' |
      \break \mark \time=6/8 \tempo{|4.|60} fis'8_"leggiero"[ g' a'] b'[ a' g'] |
      fis'4. e' |
      d'8[ e' fis'] g'[ a' b'] |
      a'4.^"poco rit." r4. |
      \break \mark \time=4/4 \tempo{Tempo I|4|112} d''4^"cantabile" cis''8[ b'] a'4 g' |
      fis'4 e'8[ fis'] g'4 a' |
      b'2^"allargando" cis''4 d'' |
      d''1_"morendo" |
    """
    return build_score('Promenade (tempo, text, rehearsal marks)', COMPOSER,
                       [{'id': 'P1', 'name': 'Oboe', 'abbr': 'Ob.', 'staves': [{'clef': 'treble', 'music': ob}]}],
                       time=(4, 4), key=(2, 'major'))


# ---------------------------------------------------------------------------------- mk06

def mk06():
    mel = r"""
      \tempo{Medium swing|4|120} d''4 c''8[ bes'] f'2 |
      g'4 a' bes' c'' |
      d''2 b'4 g' |
      c''2 a'2 |
      \break f'4 bes' d'' f'' |
      g''2 ees''4 c'' |
      c''4 a' fis' d'' |
      bes'2 g'2 |
      \break ees''4 d'' c'' bes' |
      aes'2 b'2 |
      bes'4 aes' g' ees' |
      e'2 c''2 |
      \break d''4 bes' cis''2 |
      d''4 c'' bes' a' |
      bes'2 a'2 |
      bes'1 |
    """
    chords = ('Bbmaj7:2 Gm7:2 | Cm7:2 F7:2 | Dm7:2 G7:2 | Cm7:2 F9:2 | Bb | Ebmaj7:2 Eb6:2 | Am7b5:2 D7:2 | '
              'Gm:2 Gm6:2 | Cm:2 Cm/Bb:2 | Ab7:2 G7:2 | Ebsus4:2 Eb:2 | Edim7:2 F7:2 | Bb/D:2 Faug:2 | '
              'Gm7:2 C9:2 | Fsus4:2 F7:2 | Bb6 |')
    return build_score('Harbour Lights (lead sheet)', COMPOSER,
                       [{'id': 'P1', 'name': 'Melody', 'abbr': '', 'staves': [{'clef': 'treble', 'music': mel}]}],
                       time=(4, 4), key=(-2, 'major'), chords={'part': 'P1', 'text': chords})


# ---------------------------------------------------------------------------------- mk07

def mk07():
    voice = r"""
      R1 |
      R1 |
      bes'2\p\< c''4 d''\! |
      ees''2-- d''4( c'') \breathe |
      \break bes'4\mf\> aes' g' f'\! |
      g'2._"dolce" r4 |
      c''4\< d'' ees'' f''\! |
      g''2->\f f''4( ees'') \breathe |
      \break d''4\> c'' bes' aes'\! |
      g'2-- f'4^"rit." ees' |
      \tempo{a tempo} bes'2\pp\< c''4 d''\! |
      ees''2.\fermata r4 |
    """
    rh = r"""
      \tempo{Lento|4|60} <g' bes' ees''>2\arpeggio\p <aes' c'' ees''>2\arpeggio |
      <g' bes' ees''>2\arpeggio <f' bes' d''>2\arpeggio |
      <g' bes'>4 <g' bes'> <aes' c''> <aes' c''> |
      <g' bes'>2 <f' aes'>2 |
      <ees' g'>4 <ees' g'> <d' f'> <d' f'> |
      <ees' g' bes'>2.\arpeggio r4 |
      <ees' aes'>4\< <f' aes'> <g' bes'> <aes' c''>\! |
      <bes' ees''>2\f <aes' c''>2 |
      <f' aes'>4\> <ees' g'> <d' f'> <c' ees'>\! |
      <bes ees'>2 <bes d'>2 |
      <g' bes' ees''>2\arpeggio\pp <aes' c'' ees''>2\arpeggio |
      <g' bes' ees''>2.\arpeggio\fermata r4 |
    """
    lh = r"""
      ees,4\sustainOn bes, g bes, |
      ees,2\sustainOff\sustainOn bes,,2\sustainOff\sustainOn |
      ees4-.\sustainOff g-. aes-. aes-. |
      bes,2 bes,2 |
      ees4-. ees-. bes,-. bes,-. |
      ees,2.\sustainOn r4\sustainOff |
      c4 d ees aes, |
      g,2 aes,2 |
      bes,4 bes, bes, bes, |
      ees2 bes,2 |
      ees,2\sustainOn aes,2\sustainOff\sustainOn |
      <ees,, ees,>2.\fermata\sustainOff\sustainOn r4\sustainOff |
    """
    return build_score('Vocalise (voice and piano)', COMPOSER,
                       [{'id': 'P1', 'name': 'Voice', 'abbr': 'V.', 'staves': [{'clef': 'treble', 'music': voice}]},
                        {'id': 'P2', 'name': 'Piano', 'abbr': 'Pno.',
                         'staves': [{'clef': 'treble', 'music': rh}, {'clef': 'bass', 'music': lh}]}],
                       time=(4, 4), key=(-3, 'major'))


# ---------------------------------------------------------------------------------- mk08

def mk08():
    v1 = r"""
      \tempo{Allegro|4|132} d''4-.\f g''-. fis''-. |
      e''8[( d'')] c''[( b')] a'4-> |
      g'4-. b'-. d''-. |
      g''2-> r4 |
      \break \mark b'4\p( c'' d'') |
      e''4\< fis'' g''\! |
      a''2\sfz g''4-- |
      fis''4-- e''-- d''-- |
      \break \mark d''4-^\ff c''-^ b'-^ |
      a'8[ b' c'' d''] e''4\> |
      d''4 c'' b'\! |
      g'2.\fermata\p |
    """
    v2 = r"""
      b'4-.\f d''-. d''-. |
      c''8[( b')] a'[( g')] fis'4-> |
      d'4-. g'-. b'-. |
      b'2-> r4 |
      g'4\p( a' b') |
      c''4\< d'' e''\! |
      fis''2\sfz e''4-- |
      d''4-- c''-- b'-- |
      b'4-^\ff a'-^ g'-^ |
      fis'8[ g' a' b'] c''4\> |
      b'4 a' g'\! |
      d'2.\fermata\p |
    """
    va = r"""
      g4\f^"pizz." b a |
      g4 fis d' |
      b4 d' g' |
      d'2 r4 |
      d'2.\p^"arco"( |
      e'4\< fis' g'\!) |
      a'2\sfz a'4-- |
      a'4-- g'-- fis'-- |
      g'4-^\ff e'-^ d'-^ |
      d'2 a'4\> |
      g'4 fis' d'\! |
      b2.\fermata\p |
    """
    vc = r"""
      g,4\f^"pizz." g, d |
      c4 d d, |
      g,4 g d |
      g,2 r4 |
      g2.\p^"arco" |
      c4\< d e\! |
      d2\sfz cis4-- |
      d4-- d-- d-- |
      g4-^\ff a-^ b-^ |
      d'2 c'4\> |
      d4 d d\! |
      g,2.\fermata\p |
    """
    parts = [{'id': 'P1', 'name': 'Violin I', 'abbr': 'Vln. I', 'staves': [{'clef': 'treble', 'music': v1}]},
             {'id': 'P2', 'name': 'Violin II', 'abbr': 'Vln. II', 'staves': [{'clef': 'treble', 'music': v2}]},
             {'id': 'P3', 'name': 'Viola', 'abbr': 'Vla.', 'staves': [{'clef': 'alto', 'music': va}]},
             {'id': 'P4', 'name': 'Violoncello', 'abbr': 'Vc.', 'staves': [{'clef': 'bass', 'music': vc}]}]
    return build_score('Scherzino for String Quartet', COMPOSER, parts, time=(3, 4), key=(1, 'major'),
                       groups=[{'type': 'StaffGroup', 'parts': ['P1', 'P2', 'P3', 'P4']}])


# ---------------------------------------------------------------------------------- mk09

def mk09():
    va = r"""
      \tempo{Moderato|4|88} c'4-.-1\p ees'_>-2 g'-^-4 c''-1\trill |
      bes'4---3\< aes'-.-2 g'-!-1 f'---4\! |
      ees'4->^0\mf\mordent d'-._2\prall c'--^1\turn b-!_3 |
      c'2-0\fermata_"espress." r4 g-.-1\sfz |
      \break aes4->-2\f( bes-.-3 c'-.-4 d'-.-1) |
      ees'8-.-2[ f'-.-3 g'-.-4 aes'-.-1] bes'4-^-2\sf c''-3\trill\> |
      b'4---2\turn\p c''---3 d''->-4\< ees''-^-4\! |
      c''2.-1\fermata\ff^"sul A" r4 |
    """
    return build_score('Etude in Stacked Marks', COMPOSER,
                       [{'id': 'P1', 'name': 'Viola', 'abbr': 'Vla.', 'staves': [{'clef': 'alto', 'music': va}]}],
                       time=(4, 4), key=(-3, 'minor'))


# ---------------------------------------------------------------------------------- catalog

MUST_NOT_SPLIT = ('Every staff is exactly one part with one voice; double stops / piano chords must stay chords '
                  'and the piano grand staff must stay one part, so no staff may be split into several parts')

ITEMS = [
    dict(id='mk01-articulations-violin', title='Bowing Study in Articulations', make=mk01, pages=1,
         layout='melody', must_not_split=True,
         focus=['staccato', 'staccatissimo', 'accent', 'tenuto', 'marcato', 'x-portato', 'slur'],
         expected_notes='One violin staff, G major, 4/4, 12 bars on 3 systems. Every note carries an articulation '
                        '(staccato dots, staccatissimo wedges, accents, tenuto lines, marcato, portato = tenuto+dot '
                        'under a slur, accent+staccato and tenuto+staccato stacks); bar 9 has double stops (chords) '
                        'with accents / tenuto. Articulation dots must not become augmentation dots or extra notes. '
                        + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810101, 300, 0.6, 70),
             'scan-severe.pdf': V(810102, 150, [
                 {'op': 'paper', 'rgb': [244, 243, 238], 'texture': 3},
                 {'op': 'rotate', 'deg': 3.5, 'bg': 230},
                 {'op': 'blur', 'sigma': 0.9},
                 {'op': 'binarize', 'threshold': 150, 'pre_blur': 0.6, 'noise': 18},
                 {'op': 'saltpepper', 'amount': 0.002},
                 {'op': 'speckle', 'per_mpx': 40}], fmt='png1',
                 description='150 dpi 1-bit photocopy: 3.5 deg skew, thick threshold (dots and wedges swell), '
                             'salt-and-pepper and speckle dirt that looks like staccato dots')}),
    dict(id='mk02-ornaments-fermatas-flute', title='Pastorale with Ornaments', make=mk02, pages=1,
         layout='melody', must_not_split=True,
         focus=['trill', 'mordent', 'x-inverted-mordent', 'turn', 'x-inverted-turn', 'fermata', 'breath'],
         expected_notes='One flute staff, F major, 3/4, 12 bars on 3 systems. Ornament signs above notes: "tr" '
                        'trills, mordents (with vertical stroke), inverted mordents / pralltriller (no stroke), '
                        'turns and inverted turns; fermatas on notes and on a quarter rest (bar 3); comma breath '
                        'marks after bars 4, 7, 10 and mid-bar 8. No ornament may be realised as extra notes. '
                        + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810201, 250, -0.9, 65, noise=4, blur=0.6),
             'scan-severe.pdf': V(810202, 200, [
                 {'op': 'paper', 'rgb': [236, 232, 220], 'texture': 4},
                 {'op': 'perspective', 'margin': 0.05, 'jitter': 0.025, 'keystone': 0.04, 'bg': [70, 62, 55]},
                 {'op': 'gradient', 'strength': 0.3},
                 {'op': 'vignette', 'strength': 0.25},
                 {'op': 'motion_blur', 'length': 4, 'angle': 15},
                 {'op': 'noise', 'sigma': 7, 'chroma': 2}], color='rgb', jpeg=25,
                 description='phone photo: perspective keystone on a dark desk, uneven light + vignette, motion '
                             'blur, sensor noise, JPEG q25')}),
    dict(id='mk03-dynamics-hairpins-cello', title='Elegy in Dynamics', make=mk03, pages=1,
         layout='melody', must_not_split=True,
         focus=['dyn-pp', 'dyn-p', 'dyn-mp', 'dyn-mf', 'dyn-f', 'dyn-ff', 'dyn-sfz', 'x-dyn-ppp', 'x-dyn-fff',
                'x-dyn-fp', 'x-dyn-sf', 'x-dyn-fz', 'x-dyn-sfp', 'hairpin-cresc', 'hairpin-dim'],
         expected_notes='One cello staff (bass clef), D minor, 4/4, 16 bars on 4 systems. Every standard dynamic '
                        '(ppp..fff, sfz, sf, fz, fp, sfp) below the staff, 4 crescendo and 5 diminuendo hairpins; '
                        'the diminuendo of bar 4 runs to the end of the first system and is ended by the p that '
                        'opens the second system; several hairpins end at the next dynamic instead of \\!. Dynamic letters must not be read as notes or '
                        'lyrics. ' + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810301, 200, 1.2, 60),
             'scan-severe.pdf': V(810302, 300, [
                 {'op': 'ink_dropout', 'amount': 0.35},
                 {'op': 'paper', 'rgb': [232, 222, 196], 'texture': 7,
                  'bleed': {'strength': 0.3, 'blur': 2.5, 'shift': 0.01}},
                 {'op': 'foxing', 'n': 70, 'strength': 0.5},
                 {'op': 'rotate', 'deg': -4.0, 'bg': [200, 196, 186]},
                 {'op': 'blur', 'sigma': 1.0},
                 {'op': 'noise', 'sigma': 6, 'chroma': 1.5},
                 {'op': 'downsample', 'dpi': 150}], color='rgb', jpeg=30,
                 description='aged yellowed paper: faded ink with dropouts, bleed-through of the reverse, foxing, '
                             '-4 deg skew, blur, downsampled to 150 dpi, JPEG q30')}),
    dict(id='mk04-piano-pedal-arpeggio-fingering', title='Nocturne Study (pedal, arpeggio, fingering)', make=mk04,
         pages=1, layout='piano', must_not_split=True,
         focus=['pedal', 'x-pedal-release', 'arpeggio', 'fingering', 'tempo-mark', 'metronome', 'hairpin-cresc',
                'hairpin-dim', 'dyn-p', 'dyn-mf', 'dyn-pp'],
         expected_notes='Piano grand staff (one part, two staves), A minor, 4/4, 12 bars on 3 systems. "Ped." / "*" '
                        'sustain marks under the bass staff (a "*Ped." change on most downbeats, final release on '
                        'the last rest), arpeggio wavy lines before 14 chords (separately per staff), fingering '
                        'digits above right-hand notes (stacked above chords) and below left-hand notes. Fingering '
                        'digits must not be read as tuplet numbers or time signatures. ' + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810401, 300, -0.5, 70, color='rgb', noise=3, paper=(244, 240, 230)),
             'scan-severe.pdf': V(810402, 200, [
                 {'op': 'paper', 'rgb': [240, 238, 232], 'texture': 3},
                 {'op': 'curl', 'side': 'left', 'amp': 30, 'width': 0.25},
                 {'op': 'gutter', 'side': 'left', 'width': 0.07, 'dark': 0.6},
                 {'op': 'rotate', 'deg': 2.5, 'bg': 225},
                 {'op': 'blur', 'sigma': 0.9},
                 {'op': 'noise', 'sigma': 8}], jpeg=25,
                 description='book scan: page curl and dark gutter on the left, 2.5 deg skew, blur, heavy noise, '
                             'JPEG q25 at 200 dpi')}),
    dict(id='mk05-tempo-text-rehearsal-oboe', title='Promenade (tempo, text, rehearsal marks)', make=mk05, pages=1,
         layout='melody', must_not_split=True,
         focus=['tempo-mark', 'metronome', 'text-expression', 'rehearsal-mark'],
         expected_notes='One oboe staff, D major, 16 bars on 4 systems, 4/4 -> 6/8 (bar 9) -> 4/4 (bar 13). Boxed '
                        'rehearsal letters A-D at bars 1, 5, 9, 13; bold tempo marks "Allegretto (q = 112)", "Meno '
                        'mosso" (text only), "dotted-q = 60" (metronome only), "Tempo I (q = 112)"; italic '
                        'expression text above and below the staff (dolce, espress., rit., leggiero, poco rit., '
                        'cantabile, allargando, morendo). Text must not become lyrics or notes. ' + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810501, 250, 0.8, 60, noise=5, blur=0.6),
             'scan-severe.pdf': V(810502, 300, [
                 {'op': 'paper', 'rgb': [245, 245, 243], 'texture': 2},
                 {'op': 'rotate', 'deg': -2.0, 'bg': 235},
                 {'op': 'blur', 'sigma': 1.4},
                 {'op': 'noise', 'sigma': 6},
                 {'op': 'downsample', 'dpi': 110}], jpeg=30,
                 description='very low resolution: rendered at 300 dpi, blurred, downsampled to 110 dpi '
                             '(text and box outlines smear), -2 deg skew, JPEG q30')}),
    dict(id='mk06-lead-sheet-chord-symbols', title='Harbour Lights (lead sheet)', make=mk06, pages=1,
         layout='lead-sheet', must_not_split=True,
         focus=['chord-symbol', 'tempo-mark', 'metronome'],
         expected_notes='Lead sheet: one melody staff, B-flat major, 4/4, 16 bars on 4 systems, 30 chord symbols '
                        'above the staff (maj7 as a triangle, m7, 7, 9, 6, m6, m, half-diminished slashed circle, '
                        'dim7 circle, aug +, sus4, slash chords Cm/Bb and Bb/D, roots with flats). Chord symbols '
                        'must not be read as lyrics or text expressions; ideally they become <harmony>. '
                        + MUST_NOT_SPLIT,
         notes=['Chord symbols are encoded as <harmony> with root/kind/bass. The printed superscripts (e.g. the 7 '
                'in G7) are not representable beyond kind@text; LilyPond symbol forms (triangle, circle, slashed '
                'circle, +) are encoded with use-symbols="yes".'],
         variants={
             'scan.pdf': typical(810601, 200, -1.0, 65, noise=4),
             'scan-severe.pdf': V(810602, 300, [
                 {'op': 'paper', 'rgb': [246, 246, 246], 'texture': 1},
                 {'op': 'halftone', 'lpi': 100, 'angle': 45},
                 {'op': 'rotate', 'deg': 1.5, 'bg': 240},
                 {'op': 'binarize', 'threshold': 105, 'pre_blur': 0.8, 'noise': 22},
                 {'op': 'downsample', 'dpi': 200}], fmt='png1',
                 description='halftoned copy of a copy: halftone moire, thin-threshold 1-bit binarisation (thin '
                             'strokes break up), 1.5 deg skew, 200 dpi')}),
    dict(id='mk07-vocalise-voice-piano', title='Vocalise (voice and piano)', make=mk07, pages=1,
         layout='voice-piano', must_not_split=True,
         focus=['dyn-p', 'dyn-mf', 'dyn-f', 'dyn-pp', 'hairpin-cresc', 'hairpin-dim', 'breath', 'fermata',
                'pedal', 'arpeggio', 'text-expression', 'tempo-mark', 'metronome', 'tenuto', 'accent', 'staccato'],
         expected_notes='Voice (wordless vocalise, no lyrics) + piano grand staff, E-flat major, 4/4, 12 bars on 3 '
                        'systems. Expression marks in both parts at once: dynamics and hairpins under the voice and '
                        'under the piano right hand, breath marks in the voice, simultaneous fermatas in all three '
                        'staves (bar 12), arpeggiated piano chords, sustain pedal, "Lento (q = 60)" and the text-only '
                        'tempo mark "a tempo" (bar 11), "dolce" / "rit." text. Parts: Voice, Piano. '
                        + MUST_NOT_SPLIT,
         notes=['The voice part is a wordless vocalise: the truth has no lyrics on purpose.'],
         variants={
             'scan.pdf': typical(810701, 300, 0.4, 70, color='rgb', noise=3, paper=(245, 241, 232)),
             'scan-severe.pdf': V(810702, 250, [
                 {'op': 'paper', 'rgb': [238, 232, 218], 'texture': 5},
                 {'op': 'coffee', 'n': 1, 'radius_mm': 35, 'strength': 0.5, 'cx': 0.65, 'cy': 0.45},
                 {'op': 'wave', 'amp': 6, 'period': 1.1},
                 {'op': 'rotate', 'deg': -3.0, 'bg': [210, 205, 195]},
                 {'op': 'shadow', 'strength': 0.35, 'pos': 0.3},
                 {'op': 'blur', 'sigma': 0.8},
                 {'op': 'noise', 'sigma': 7, 'chroma': 2}], color='rgb', jpeg=22,
                 description='crumpled page with a coffee ring over the middle systems, wavy staff lines, -3 deg '
                             'skew, hand shadow, noise, JPEG q22')}),
    dict(id='mk08-string-quartet-marks', title='Scherzino for String Quartet', make=mk08, pages=1,
         layout='string-quartet', must_not_split=True,
         focus=['dyn-f', 'dyn-p', 'dyn-ff', 'dyn-sfz', 'hairpin-cresc', 'hairpin-dim', 'staccato', 'accent',
                'tenuto', 'marcato', 'fermata', 'slur', 'rehearsal-mark', 'tempo-mark', 'metronome',
                'text-expression'],
         expected_notes='String quartet (Violin I, Violin II, Viola in alto clef, Violoncello; bracketed), G major, '
                        '3/4, 12 bars on 3 systems. The same marks in all four staves at once (f, p, sfz, ff, '
                        'hairpins, staccato / accent / tenuto / marcato, simultaneous fermatas in the last bar), '
                        '"pizz." / "arco" text in viola and cello, boxed rehearsal letters A and B at bars 5 and 9, '
                        '"Allegro (q = 132)". ' + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810801, 250, -0.7, 65, noise=4),
             'scan-severe.pdf': V(810802, 300, [
                 {'op': 'ink_weight', 'px': 1},
                 {'op': 'paper', 'rgb': [242, 241, 236], 'texture': 3},
                 {'op': 'rotate', 'deg': 5.0, 'bg': 225},
                 {'op': 'saltpepper', 'amount': 0.003},
                 {'op': 'blur', 'sigma': 0.7},
                 {'op': 'noise', 'sigma': 6},
                 {'op': 'downsample', 'dpi': 150}], jpeg=30,
                 description='over-inked copy (strokes thickened), 5 deg skew, salt-and-pepper, blur, downsampled '
                             'to 150 dpi, JPEG q30')}),
    dict(id='mk09-stacked-marks-viola', title='Etude in Stacked Marks', make=mk09, pages=1,
         layout='melody', must_not_split=True,
         focus=['staccato', 'staccatissimo', 'accent', 'tenuto', 'marcato', 'fingering', 'trill', 'mordent',
                'x-inverted-mordent', 'turn', 'fermata', 'dyn-p', 'dyn-mf', 'dyn-f', 'dyn-ff', 'dyn-sfz',
                'x-dyn-sf', 'hairpin-cresc', 'hairpin-dim', 'text-expression', 'tempo-mark', 'metronome', 'slur'],
         expected_notes='One viola staff (alto clef), C minor, 4/4, 8 bars on 2 systems. Dense stacks: almost every '
                        'note carries an articulation + a fingering digit (0-4, some forced above / below) and often '
                        'an ornament, dynamic, hairpin or text; notes on ledger lines above the alto staff carry '
                        'marks too. Worst case for false notes: dots, digits and ornament signs crowd the noteheads. '
                        + MUST_NOT_SPLIT,
         variants={
             'scan.pdf': typical(810901, 200, 0.9, 60, noise=5),
             'scan-severe.pdf': V(810902, 200, [
                 {'op': 'ink_dropout', 'amount': 0.3},
                 {'op': 'paper', 'rgb': [240, 238, 230], 'texture': 4},
                 {'op': 'perspective', 'margin': 0.04, 'jitter': 0.03, 'keystone': 0.05, 'bg': [60, 55, 50]},
                 {'op': 'gradient', 'strength': 0.25},
                 {'op': 'noise', 'sigma': 10, 'chroma': 2}], color='rgb', jpeg=20,
                 description='faded ink with dropouts photographed at an angle: perspective keystone, light '
                             'gradient, heavy noise, JPEG q20')}),
]
