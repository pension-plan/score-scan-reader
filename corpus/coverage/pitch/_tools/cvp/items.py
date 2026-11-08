"""Coverage-suite items, pitch family.  All music self-composed for this corpus (CC0).

Each maker returns make() -> (Score, layout, lilypond options).
"""
from __future__ import annotations

from .acc import key_alters
from .dsl2 import build
from .lily import default_layout

STEPS = 'CDEFGAB'
COMPOSER = 'OMR coverage suite (CC0)'
RIGHTS = 'CC0 1.0 - composed for the OMR coverage suite'
ACC_LY = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}


def lyp(step, alter, octave):
    k = octave - 3
    return step.lower() + ACC_LY[alter] + ("'" * k if k > 0 else ',' * (-k))


def from_dia(d, alter=0):
    return lyp(STEPS[d % 7], alter, d // 7)


TONIC_MAJ = {0: 'C', 1: 'G', 2: 'D', 3: 'A', 4: 'E', 5: 'B', 6: 'F', 7: 'C', -1: 'F', -2: 'B', -3: 'E', -4: 'A',
             -5: 'D', -6: 'G', -7: 'C'}
TONIC_MIN = {0: 'A', 1: 'E', 2: 'B', 3: 'F', 4: 'C', 5: 'G', 6: 'D', 7: 'A', -1: 'D', -2: 'G', -3: 'C', -4: 'F',
             -5: 'B', -6: 'E', -7: 'A'}


def deg(fifths, mode, tonic_oct, d, raise_=0):
    """scale degree d (1 = tonic, 8 = tonic an octave up, 0 = leading note below) in the key"""
    tstep = (TONIC_MIN if mode == 'minor' else TONIC_MAJ)[fifths]
    x = tonic_oct * 7 + STEPS.index(tstep) + (d - 1)
    step = STEPS[x % 7]
    return lyp(step, key_alters(fifths)[step] + raise_, x // 7)


# ----------------------------------------------------------------- layout / option helpers

def single_staff_layout(parts, group=None):
    staves = []
    for pid, name, abbr, clef in parts:
        staves.append({'id': f'st{pid}', 'clef': clef, 'voices': [(pid, '1')], 'lyrics': [],
                       'name': name, 'short': abbr})
    return {'groups': [{'type': group, 'staves': staves}]}


def base_opts(title, subtitle='', size=20, extra_paper=(), extra_layout=()):
    hdr = {'title': title, 'composer': COMPOSER}
    if subtitle:
        hdr['subtitle'] = subtitle
    return {'header': hdr, 'staff_size': size, 'paper': 'a4', 'font': 'TeX Gyre Schola',
            'paper_extra': ['indent = 18\\mm', 'short-indent = 8\\mm', 'ragged-bottom = ##t',
                            'ragged-last = ##f'] + list(extra_paper),
            'layout_extra': list(extra_layout), 'auto_beam_off_vocal': False}


def finish(sc, title):
    sc.title = title
    sc.composer = COMPOSER
    sc.rights = RIGHTS
    return sc


# ================================================================= 1. all eight clefs (melody)

# middle-line diatonic index (octave*7 + step) of the *sounding* pitch for each clef
MIDDLE = {'treble': 34, 'bass': 22, 'alto': 28, 'tenor': 26, 'soprano': 32, 'treble_8': 27, 'treble^8': 41,
          'bass_8': 15}
PAT_P = ('{-6}4 {-4} {-2} {0}', '{2}8 {4} {6} {4} {2}4 {0}')
PAT_Q = ('{-5}4 {-3} {-1} {1}', '{3}8 {5} {7}4 {5}8 {3} {1}4')
CLEF_TOUR = [('treble', PAT_P), ('bass', PAT_Q), ('alto', PAT_P), ('tenor', PAT_Q), ('soprano', PAT_P),
             ('treble_8', PAT_Q), ('treble^8', PAT_P), ('bass_8', PAT_Q)]


def _fill(pat, mid):
    import re
    return re.sub(r'\{(-?\d+)\}', lambda m: from_dia(mid + int(m.group(1))), pat)


def mk_clefs_all():
    def make():
        bars = []
        for k, (clef, pat) in enumerate(CLEF_TOUR):
            a, b = (_fill(x, MIDDLE[clef]) for x in pat)
            pre = ''
            if k in (2, 4, 6):
                pre += '\\break '
            if k > 0:
                pre += f'\\clef={clef} '
            bars += [pre + a, b]
        music = ' | '.join(bars) + ' |'
        sc = build([{'id': 'P1', 'name': 'Melody', 'abbr': 'Mel.', 'clef': 'treble', 'instrument': 'other',
                     'music': music}], time=(4, 4), key=(0, 'major'))
        finish(sc, 'Eight Clefs')
        lay = single_staff_layout([('P1', 'Melody', 'Mel.', 'treble')])
        opts = base_opts('Eight Clefs', 'one staff-position pattern read in eight clefs', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #16', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 2. clef changes on a grand staff (piano)

CLEF_PNO_RH = r"""
a'4 c'' f'' | e''4 g'' c'' | f''2 a'4 |
\break bes'4 d'' g'' | a'4 \clef=bass f c | a,4 c f |
\break \clef=treble c''4 a' f' | g'4 bes' e'' | f''4 e''8 d'' c''4 |
\break \clef=bass c'4 a f | g4 \clef=treble bes' d'' | f''2. |
"""
CLEF_PNO_LH = r"""
f,4 c a, | c4 bes, \clef=treble g'4 | f'4 c' a |
\clef=bass g,4 d bes, | f,2 c,4 | d,8 e, f,4 c,4 |
f,4 a, c | \clef=treble c'4 e' \clef=bass c4 | f,4 a, c |
f,2 c4 | c4 \clef=treble e'4 g' | \clef=bass f,2. |
"""


def mk_clef_piano():
    def make():
        sc = build([{'id': 'P1', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
                     'staves': [CLEF_PNO_RH, CLEF_PNO_LH]}], time=(3, 4), key=(-1, 'major'))
        finish(sc, 'Changing Hands')
        lay = default_layout(sc)
        opts = base_opts('Changing Hands', 'clef changes on the grand staff', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #20', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 3. string quartet with C clefs and clef changes

Q_V1 = r"""fis''4 a'' d''' a'' | b''4 g'' e'' cis''' | d'''2 a''2 | g''4 fis'' e'' d'' |
\break fis''4 e''8 d'' cis''4 a' | b'4 d'' g'' fis'' | e''4 a'' g'' cis'' | d''1 |"""
Q_V2 = r"""a'4 d'' fis'' d'' | d''4 b' cis'' e'' | fis''2 fis''2 | b'4 a' g' fis' |
a'4 cis''8 b' a'4 e' | d'4 fis' b' a' | cis''4 e'' b' g' | fis'1 |"""
Q_VA = r"""d'4 fis' a' fis' | g'4 d' e' a' | a'2 \clef=treble d''4 cis'' | d''4 a' b' a' |
\clef=alto d'4 a e' cis' | g4 b d' d' | a4 cis' d' e' | a1 |"""
Q_VC = r"""d4 d a, d | \clef=tenor g4 b a cis' | d'4 \clef=treble fis'4 a' fis' | g'4 e' \clef=tenor d' a |
d'4 cis' b a | \clef=bass g,4 b, d g | a,4 a \clef=tenor b cis' | \clef=bass d1 |"""


def mk_quartet():
    def make():
        sc = build([{'id': 'V1', 'name': 'Violin I', 'abbr': 'Vl. I', 'clef': 'treble', 'instrument': 'violin',
                     'music': Q_V1},
                    {'id': 'V2', 'name': 'Violin II', 'abbr': 'Vl. II', 'clef': 'treble', 'instrument': 'violin',
                     'music': Q_V2},
                    {'id': 'VA', 'name': 'Viola', 'abbr': 'Vla.', 'clef': 'alto', 'instrument': 'viola',
                     'music': Q_VA},
                    {'id': 'VC', 'name': 'Violoncello', 'abbr': 'Vc.', 'clef': 'bass', 'instrument': 'cello',
                     'music': Q_VC}], time=(4, 4), key=(2, 'major'))
        finish(sc, 'Quartet in Changing Clefs')
        sc.groups = [{'first': 'V1', 'last': 'VC', 'symbol': 'bracket'}]
        lay = single_staff_layout([('V1', 'Violin I', 'Vl. I', 'treble'), ('V2', 'Violin II', 'Vl. II', 'treble'),
                                   ('VA', 'Viola', 'Vla.', 'alto'), ('VC', 'Violoncello', 'Vc.', 'bass')],
                                  group='StaffGroup')
        opts = base_opts('Quartet in Changing Clefs', 'alto and tenor clefs, clef changes in viola and cello',
                         size=19, extra_paper=['system-system-spacing.basic-distance = #22', 'indent = 20\\mm',
                                               'short-indent = 10\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 4-7. key tours

def key_tour(keys, mode, bars_fn, time, breaks_at, double_after):
    """keys: list of (fifths, tonic_oct); returns DSL text, one 2-bar segment per key."""
    out = []
    for k, (f, toct) in enumerate(keys):
        a, b = bars_fn(f, mode, toct)
        bi = 2 * k
        pre = ''
        if bi in breaks_at:
            pre += '\\break '
        if k > 0:
            pre += f'\\key={f}' + (':minor' if mode == 'minor' else '') + ' '
        post = ' \\bar=||' if (bi + 1) in double_after else ''
        out += [pre + a, b + post]
    return ' | '.join(out) + ' |'


def bars_major_melody(f, mode, o):
    a = ' '.join(deg(f, mode, o, d) + ('4' if i == 0 else '') for i, d in enumerate((1, 3, 5, 8)))
    b = ' '.join(deg(f, mode, o, d) + ('8' if i == 0 else '') for i, d in enumerate((7, 6, 5, 4, 3, 2))) + \
        ' ' + deg(f, mode, o, 1) + '4'
    return a, b


MAJ_SHARP_KEYS = [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 3), (6, 4), (7, 5)]


def mk_keys_major_sharps():
    def make():
        music = key_tour(MAJ_SHARP_KEYS, 'major', bars_major_melody, (4, 4), {4, 8, 12}, {1, 5, 7, 11, 13})
        sc = build([{'id': 'P1', 'name': 'Violin', 'abbr': 'Vln.', 'clef': 'treble', 'instrument': 'violin',
                     'music': music}], time=(4, 4), key=(0, 'major'))
        finish(sc, 'Sharps Ascending')
        lay = single_staff_layout([('P1', 'Violin', 'Vln.', 'treble')])
        opts = base_opts('Sharps Ascending', 'the eight major keys from C to C sharp', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #16', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


MAJ_FLAT_KEYS = [(-1, 4, 2), (-2, 4, 2), (-3, 4, 2), (-4, 4, 2), (-5, 4, 2), (-6, 4, 2), (-7, 4, 2)]


def mk_keys_major_flats():
    def make():
        rh, lh = [], []
        for k, (f, o, lo) in enumerate(MAJ_FLAT_KEYS):
            pre = ('\\break ' if 2 * k in (4, 8, 12) else '') + (f'\\key={f} ' if k else '')
            post = ' \\bar=||' if k < len(MAJ_FLAT_KEYS) - 1 and k % 2 == 1 else ''
            a = ' '.join(deg(f, 'major', o, d) + ('4' if i == 0 else '') for i, d in enumerate((1, 3, 5, 8)))
            b = '<' + ' '.join(deg(f, 'major', o, d) for d in (5, 7, 9)) + '>2 <' + \
                ' '.join(deg(f, 'major', o, d) for d in (3, 5, 8)) + '>2'
            rh += [pre + a, b + post]
            la = deg(f, 'major', lo, 1) + '2 ' + deg(f, 'major', lo, 5) + '2'
            lb = deg(f, 'major', lo, 5) + '2 ' + deg(f, 'major', lo, 1) + '2'
            lh += [la, lb]
        sc = build([{'id': 'P1', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
                     'staves': [' | '.join(rh) + ' |', ' | '.join(lh) + ' |']}], time=(4, 4), key=(-1, 'major'))
        finish(sc, 'Flats Descending')
        lay = default_layout(sc)
        opts = base_opts('Flats Descending', 'the seven major keys from F to C flat', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #20', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


def bars_minor_cello(f, mode, o):
    a = ' '.join(deg(f, mode, o, d) + ('4' if i == 0 else '') for i, d in enumerate((1, 3, 5)))
    b = deg(f, mode, o, 6) + '8 ' + deg(f, mode, o, 7, raise_=1) + ' ' + deg(f, mode, o, 8) + '2'
    return a, b


MIN_SHARP_KEYS = [(0, 2), (1, 2), (2, 2), (3, 2), (4, 3), (5, 2), (6, 3), (7, 2)]


def mk_keys_minor_sharps():
    def make():
        music = key_tour(MIN_SHARP_KEYS, 'minor', bars_minor_cello, (3, 4), {4, 8, 12}, {1, 3, 7, 9, 13})
        sc = build([{'id': 'P1', 'name': 'Violoncello', 'abbr': 'Vc.', 'clef': 'bass', 'instrument': 'cello',
                     'music': music}], time=(3, 4), key=(0, 'minor'))
        finish(sc, 'Minor Keys with Sharps')
        lay = single_staff_layout([('P1', 'Violoncello', 'Vc.', 'bass')])
        opts = base_opts('Minor Keys with Sharps', 'harmonic minor, A minor to A sharp minor', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #16', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


def bars_minor_viola(f, mode, o):
    a = (deg(f, mode, o, 1) + '4 ' + deg(f, mode, o, 3) + '8 ' + deg(f, mode, o, 5) + '4 ' +
         deg(f, mode, o, 3) + '8')
    b = deg(f, mode, o, 0, raise_=1) + '4 ' + deg(f, mode, o, 2) + '8 ' + deg(f, mode, o, 1) + '4.'
    return a, b


MIN_FLAT_KEYS = [(-1, 4), (-2, 3), (-3, 4), (-4, 3), (-5, 3), (-6, 4), (-7, 3)]


def mk_keys_minor_flats():
    def make():
        music = key_tour(MIN_FLAT_KEYS, 'minor', bars_minor_viola, (6, 8), {4, 8, 12}, {3, 5, 9, 11})
        sc = build([{'id': 'P1', 'name': 'Viola', 'abbr': 'Vla.', 'clef': 'alto', 'instrument': 'viola',
                     'music': music}], time=(6, 8), key=(-1, 'minor'))
        finish(sc, 'Minor Keys with Flats')
        lay = single_staff_layout([('P1', 'Viola', 'Vla.', 'alto')])
        opts = base_opts('Minor Keys with Flats', 'harmonic minor, D minor to A flat minor', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #16', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 8. key changes with cancellations (organ)

# (fifths, mode, tonic octave for manuals, tonic octave for pedal, line break before, double bar before)
ORGAN_KEYS = [(4, 'major', 3, 2, False, False), (-3, 'major', 3, 2, False, True), (0, 'major', 3, 2, True, True),
              (3, 'major', 3, 2, False, True), (2, 'major', 3, 2, True, False), (-1, 'minor', 3, 2, False, True),
              (5, 'major', 3, 2, True, True)]
# I - IV | V - I   (soprano, alto, tenor, bass as scale degrees; 0 = leading note below)
ORGAN_PROG = [((10, 8, 5, 1), (11, 8, 6, 4)), ((9, 7, 5, 5), (10, 8, 5, 1))]


def mk_organ_keys():
    def make():
        rh, lh, ped = [], [], []
        n = len(ORGAN_KEYS)
        for k, (f, mode, o, po, brk, dbl) in enumerate(ORGAN_KEYS):
            for j, (c1, c2) in enumerate(ORGAN_PROG):
                bar_rh, bar_lh, bar_pd = [], [], []
                for (s, a, t, b) in (c1, c2):
                    r7 = 1 if mode == 'minor' else 0
                    def dg(d, oc):
                        return deg(f, mode, oc, d, raise_=r7 if (d % 7) == 0 else 0)
                    bar_rh.append(f'<{dg(a, o)} {dg(s, o)}>2')
                    bar_lh.append(f'{dg(t, o)}2')
                    bar_pd.append(f'{dg(b, po)}2')
                pre = ''
                if j == 0 and k > 0:
                    pre = ('\\break ' if brk else '') + f'\\key={f}' + (':minor ' if mode == 'minor' else ' ')
                post = ''
                if j == 1 and k + 1 < n and ORGAN_KEYS[k + 1][5]:
                    post = ' \\bar=||'
                rh.append(pre + ' '.join(bar_rh) + post)
                lh.append(' '.join(bar_lh))
                ped.append(' '.join(bar_pd))
        sc = build([{'id': 'P1', 'name': 'Organ', 'abbr': 'Org.', 'instrument': 'organ',
                     'clefs': ['treble', 'bass', 'bass'],
                     'staves': [' | '.join(rh) + ' |', ' | '.join(lh) + ' |', ' | '.join(ped) + ' |']}],
                   time=(4, 4), key=(4, 'major'))
        finish(sc, 'Modulating Chorale')
        lay = {'groups': [
            {'type': 'PianoStaff', 'name': 'Organ', 'short': 'Org.', 'staves': [
                {'id': 'stP1s1', 'clef': 'treble', 'voices': [('P1', '1')], 'lyrics': []},
                {'id': 'stP1s2', 'clef': 'bass', 'voices': [('P1', '5')], 'lyrics': []}]},
            {'type': None, 'staves': [
                {'id': 'stP1s3', 'clef': 'bass', 'voices': [('P1', '9')], 'lyrics': [], 'name': 'Pedal',
                 'short': 'Ped.'}]}]}
        opts = base_opts('Modulating Chorale', 'key changes with cancellation naturals', size=19,
                         extra_paper=['system-system-spacing.basic-distance = #22', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 9. accidental etude (melody)

ACC_MEL = r"""
g'4 ais'8 b' cis''4 dis''4 | e''8 eis'' fis''4 f''4 e''4 | fis''?4 ees''4 des''4 c''4 | bes'4 aes'4 g'2 |
\break fisis'4 gis'4 fis'4 f'4 | bes'4 beses'4 bes'4 a'4 | cisis''4 dis''4 eisis''4 fis''4 |
  geses''4 fes''4 eeses''4 des''4 |
\break d''?4 e''!4 fis''!4 g''?4 | c''4 cis'''4 c'''4 cis''4 | f'4 fis'4 f'8 e' dis'4 | a'4 fis'?4 g'2 |
"""


def mk_acc_melody():
    def make():
        sc = build([{'id': 'P1', 'name': 'Flute', 'abbr': 'Fl.', 'clef': 'treble', 'instrument': 'flute',
                     'music': ACC_MEL}], time=(4, 4), key=(1, 'major'))
        finish(sc, 'Accidental Etude')
        lay = single_staff_layout([('P1', 'Flute', 'Fl.', 'treble')])
        opts = base_opts('Accidental Etude', 'sharps, flats, naturals, doubles and courtesy accidentals', size=21,
                         extra_paper=['system-system-spacing.basic-distance = #16', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 10. accidentals in piano chords

CH_RH = r"""
<c'' ees'' aes''>4 <c'' e'' g''>4 <des'' f'' aes''>4 <d'' f'' b'>4 | <ees'' g'' bes''>2 <e'' gis'' b''>2 |
<a' cis'' e''>4 <aes' c'' ees''>4 <fes' aes' ces''>2 | <bes' des'' f''>2 <beses' des'' fes''>2 |
\break <bes'? des'' f''?>2 <b' dis'' fis''>2 | <b' dis'' fisis''>4 <b' dis'' fis''>4 <e'' gis'' b''>2 |
<ees'' g'' bes''>4 <ees'' ges'' beses''>4 <des'' f'' aes''>2 | <c'' ees''! aes''>1 |
"""
CH_LH = r"""
aes,2 g,2 | <ees, ees>2 <e, e>2 | <a, a>4 <aes, aes>4 <fes, fes>2 | <bes,, bes,>2 <ees, bes,>2 |
<bes,, bes,>2 <b,, b,>2 | <b,, b,>2 <e, e>2 | <ees, bes,>2 <des, aes,>2 | <aes,, aes,>1 |
"""


def mk_acc_chords():
    def make():
        sc = build([{'id': 'P1', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
                     'staves': [CH_RH, CH_LH]}], time=(4, 4), key=(-4, 'major'))
        finish(sc, 'Chromatic Chords')
        lay = default_layout(sc)
        opts = base_opts('Chromatic Chords', 'stacked accidentals in chords', size=21,
                         extra_paper=['system-system-spacing.basic-distance = #22', 'top-margin = 15\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 11. ottava brackets (piano, 8va / 8vb / 15ma)

OTT_RH = r"""
c''4 e'' g'' c''' | \ottava=1 e'''4 g''' c''''2 | b'''4 g''' \ottava=0 e'''4 c'''4 | g''4 \ottava=2 c''''4 e'''' g'''' |
\break c'''''2 \ottava=0 c'''2 | \ottava=1 a'''4 f''' d''' b'' | c'''1 \ottava=0 | g''2 e''2 |
\break c''4 \ottava=1 g'''4 a''' b''' | c''''4 d'''' e''''2 \ottava=0 | c'''4 g'' e'' c'' | c''1 |
"""
OTT_LH = r"""
c2 g,2 | c,2 e,2 | \ottava=-1 c,,4 g,, e,,2 \ottava=0 | g,1 |
\ottava=-1 a,,,2 e,,2 | f,,2 g,,2 \ottava=0 | c,1 | e,2 g,2 |
c4 e g c' | \ottava=-1 c,,4 e,, g,, c, | e,,2 \ottava=0 g,2 | c,1 |
"""


def mk_ottava_piano():
    def make():
        sc = build([{'id': 'P1', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'clefs': ['treble', 'bass'],
                     'staves': [OTT_RH, OTT_LH]}], time=(4, 4), key=(0, 'major'))
        finish(sc, 'Octave Signs')
        lay = default_layout(sc)
        opts = base_opts('Octave Signs', '8va, 15ma and 8vb brackets', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #24', 'top-margin = 15\\mm'])
        opts['ottava_style'] = 'ordinals'
        return sc, lay, opts
    return make


# ================================================================= 12. ledger lines vs ottava (melody, numeric "8"/"15")

OTT_MEL = r"""
c'''8 d''' e''' f''' | g'''8 a''' b''' c'''' | \ottava=1 c'''8 d''' e''' f''' | g'''8 a''' b''' c'''' \ottava=0 |
\break a8 g f e | d4 c4 | \ottava=-1 a8 g f e | d4 c4 \ottava=0 |
\break \ottava=2 c''''8 e'''' g'''' c''''' | g''''4 c'''''4 \ottava=0 | c'''4 g''4 | c''2 |
"""


def mk_ottava_melody():
    def make():
        sc = build([{'id': 'P1', 'name': 'Melody', 'abbr': 'Mel.', 'clef': 'treble', 'instrument': 'other',
                     'music': OTT_MEL}], time=(2, 4), key=(0, 'major'))
        finish(sc, 'Ledger Lines and Octave Signs')
        lay = single_staff_layout([('P1', 'Melody', 'Mel.', 'treble')])
        opts = base_opts('Ledger Lines and Octave Signs', 'the same passages with ledger lines and with 8 / 15',
                         size=20, extra_paper=['system-system-spacing.basic-distance = #22', 'top-margin = 15\\mm'])
        opts['ottava_style'] = 'numbers'
        return sc, lay, opts
    return make
