"""Pitch-challenge items: all music self-composed for this corpus (CC0); texts public domain.

Each item: make() -> (Score, layout, lilypond options); 'damage' = output file -> op pipeline.
"""
from __future__ import annotations

from .dsl2 import build, parse_voice
from .harmonize2 import TTBB, harmonize
from .model import Part, VoiceDef, renumber, set_verses

PD_TEXT = 'public domain'
CC0 = 'CC0-1.0 (composition, engraving and scans); texts, where present, public domain'


# ----------------------------------------------------------------- layout helpers

def single_staff_layout(parts, group=None, names=True):
    staves = []
    for pid, name, abbr, clef, lyr in parts:
        st = {'id': f'st{pid}', 'clef': clef, 'voices': [(pid, '1')],
              'lyrics': [{'voice': (pid, '1'), 'verses': lyr, 'place': 'below'}] if lyr else []}
        if names:
            st['name'], st['short'] = name, abbr
        staves.append(st)
    return {'groups': [{'type': group, 'staves': staves}]}


def closed_layout(upper, lower, lyr_upper, names=None, clefs=('treble', 'bass')):
    st1 = {'id': 'upper', 'clef': clefs[0], 'voices': upper,
           'lyrics': [{'voice': v, 'verses': vs, 'place': pl} for v, vs, pl in lyr_upper]}
    st2 = {'id': 'lower', 'clef': clefs[1], 'voices': lower, 'lyrics': []}
    if names:
        st1['name'], st2['name'] = names[0], names[1]
        st1['short'], st2['short'] = names[2], names[3]
    return {'groups': [{'type': 'ChoirStaff', 'staves': [st1, st2]}]}


def base_opts(title, subtitle='', composer='', poet='', size=20, extra_paper=(), extra_layout=(), font='TeX Gyre Schola'):
    hdr = {'title': title, 'composer': composer}
    if subtitle:
        hdr['subtitle'] = subtitle
    if poet:
        hdr['poet'] = poet
    return {'header': hdr, 'staff_size': size, 'paper': 'a4', 'font': font,
            'paper_extra': ['indent = 16\\mm', 'ragged-bottom = ##t'] + list(extra_paper),
            'layout_extra': list(extra_layout), 'auto_beam_off_vocal': False}


def satb_from_soprano(sop_text, chords, key, time, tonic_pc, names, ranges=None, pickup=False):
    """soprano DSL + one chord symbol per soprano attack -> 4-part Score (homophonic)."""
    sc = build([{'id': names[0][0], 'name': names[0][1], 'abbr': names[0][2], 'clef': 'treble',
                 'music': sop_text}], time=time, key=key)
    smeas = [m['1'] for m in sc.part(names[0][0]).measures]
    a, t, b = harmonize(smeas, chords, tonic_pc, ranges)
    for (pid, name, abbr), meas in zip(names[1:], (a, t, b)):
        p = Part(id=pid, name=name, abbr=abbr, clefs=['treble'], voices=[VoiceDef('1', 1)])
        p.measures = [{'1': m} for m in meas]
        sc.parts.append(p)
    renumber(sc)
    return sc


def add_courtesy(score, staves, every=2):
    """Courtesy accidentals the way editors add them: the first note of a bar whose
    (octave, step) was altered differently in the previous bar on the same engraved
    staff.  Every `every`-th candidate gets a parenthesised courtesy accidental ('?');
    the others are left bare (strict rule: the barline cancels).  Returns a report."""
    from .acc import key_alters
    offs = score.measure_offsets()
    rep = []
    k = 0
    for sid, voices in staves:
        prev_bar = {}
        for i, mi in enumerate(score.measures):
            kalt = key_alters(score.current_key(i)[0])
            evs = []
            for pid, vk in voices:
                t = offs[i]
                for ev in score.part(pid).measures[i].get(vk, []):
                    if ev.kind == 'note':
                        evs.append((t, pid, ev))
                    t += ev.dur
            evs.sort(key=lambda x: x[0])
            seen = {}
            cur_bar = {}
            for t, pid, ev in evs:
                for p in ev.pitches:
                    step, alt, octv = p
                    kk = (octv, step)
                    if kk not in seen and p not in ev.tie_stop and alt == kalt[step] and \
                            kk in prev_bar and prev_bar[kk] != alt and not score.measures[i].key:
                        if k % every == 0:
                            ev.caut_acc.add(p)
                            rep.append({'measure': score.measures[i].number, 'part': score.part(pid).name,
                                        'pitch': f'{step}{"#" * alt if alt > 0 else "b" * -alt}{octv}',
                                        'courtesy': 'parenthesised'})
                        else:
                            rep.append({'measure': score.measures[i].number, 'part': score.part(pid).name,
                                        'pitch': f'{step}{"#" * alt if alt > 0 else "b" * -alt}{octv}',
                                        'courtesy': 'none (barline cancels)'})
                        k += 1
                    seen.setdefault(kk, alt)
                    cur_bar[kk] = alt
            prev_bar = cur_bar
    return rep


# ================================================================= 1. key signatures

KEYS_VLN = r"""
c''4 e''8 d'' c''4 g'4 | a'8 b' c'' d'' e''4 c''4 | f''4 e''8 d'' c''4 b'4 | c''2 r2 \bar=|| |
\break \key=7 cis''4 eis''8 dis'' cis''4 gis'4 | ais'8 bis' cis'' dis'' eis''4 fisis''4 |
  gis''4 fisis''8 eis'' dis''4 bis'4 | cis''2 r2 \bar=|| |
\key=-5 des''4 f''8 ees'' des''4 aes'4 | bes'8 c'' des'' ees'' f''4 g''4 |
\break aes''4 g''8 f'' ees''4 c''4 | des''2 r2 \bar=|| |
\key=-7 ces''4 ees''8 des'' ces''4 ges'4 | aes'8 bes' ces'' des'' ees''4 f''4 |
\break ges''4 f''8 ees'' des''4 beses'4 | ces''2 r2 \bar=|| |
\key=5 b'4 dis''8 cis'' b'4 fis'4 | gis'8 ais' b' cis'' dis''4 eis''4 | fis''4 eis''8 dis'' cis''4 a'4 | b'2 r2 |
\break \key=6 fis'4 ais'8 gis' fis'4 cis''4 | dis''8 eis'' fis'' gis'' ais''4 bis''4 |
  cis'''4 bis''8 ais'' gis''4 e''4 | fis''2 r2 |
\key=-6 ges'4 bes'8 aes' ges'4 des''4 | ees''8 f'' ges'' aes'' bes''4 c'''4 |
\break des'''4 c'''8 bes'' aes''4 fes''4 | ges''2 r2 \bar=|| |
\key=0:minor a'4 c''8 b' a'4 e''4 | f''8 gis'' a'' b'' c'''4 b''4 | a''4 gis''8 fis'' e''4 dis''4 | e''4 gis'4 a'2 |
"""


def mk_keys():
    def make():
        sc = build([{'id': 'V', 'name': 'Violin', 'abbr': 'Vln.', 'clef': 'treble', 'instrument': 'violin',
                     'music': KEYS_VLN}], time=(4, 4), key=(0, 'major'))
        sc.title = 'Odyssey Through the Keys'
        sc.composer = 'Pitch challenge corpus (CC0)'
        sc.rights = 'CC0 1.0 - composed for the OMR challenge corpus'
        lay = single_staff_layout([('V', 'Violin', 'Vln.', 'treble', [])])
        opts = base_opts('Odyssey Through the Keys', 'for solo violin', 'challenge corpus (CC0)', size=19,
                         extra_paper=['system-system-spacing.basic-distance = #13', 'top-margin = 14\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 2. clefs (viola + cello)

CLEF_VLA = r"""
a4 c' f' | d'4 f' bes' | c''4 bes' e' | f'2. |
\break f4 g a | bes4 d' bes | e'4 c' e' | f'2. |
\break bes4 f d | c4 e g | a4 c' f' | g'4 e' c' |
\break \clef=treble a'4 c'' f'' | e''4 cis'' a' | d''4 f'' a'' | g''4 f'' d'' |
\break d''4 bes' \clef=alto g' | e'4 c' e' | g'4 e' c' | a2. |
"""
CLEF_VC = r"""
f,4 a, c | bes,4 d f | c4 e g | f2. |
\clef=tenor d'4 e' f' | g'4 \clef=treble bes' d'' | c''4 bes' g' | a'2. |
\clef=tenor f'4 d' bes | g4 c' e' | \clef=bass f4 c a, | c4 g, c |
f,4 c f | a,4 cis e | d4 a, f, | bes,4 d f |
g4 \clef=tenor d' bes | c'4 e' g' | \clef=bass bes4 g e | f2. |
"""


def mk_clefs():
    def make():
        sc = build([{'id': 'VA', 'name': 'Viola', 'abbr': 'Vla.', 'clef': 'alto', 'instrument': 'viola',
                     'music': CLEF_VLA},
                    {'id': 'VC', 'name': 'Violoncello', 'abbr': 'Vc.', 'clef': 'bass', 'instrument': 'cello',
                     'music': CLEF_VC}], time=(3, 4), key=(-1, 'major'))
        sc.title = 'Clef Carousel'
        sc.composer = 'Pitch challenge corpus (CC0)'
        sc.rights = 'CC0 1.0 - composed for the OMR challenge corpus'
        sc.groups = [{'first': 'VA', 'last': 'VC', 'symbol': 'bracket'}]
        lay = single_staff_layout([('VA', 'Viola', 'Vla.', 'alto', []), ('VC', 'Violoncello', 'Vc.', 'bass', [])],
                                  group='StaffGroup')
        opts = base_opts('Clef Carousel', 'duet for viola and violoncello', 'challenge corpus (CC0)', size=20,
                         extra_paper=['indent = 18\\mm', 'short-indent = 9\\mm',
                                      'system-system-spacing.basic-distance = #16'])
        opts['paper_extra'] = [x for x in opts['paper_extra'] if x != 'indent = 0']
        return sc, lay, opts
    return make


# ================================================================= 3. accidental storm (flute)

ACC_FL = r"""
g'4 b'8 d'' cis''4 d''4 | e''8 cis'' d'' b' cis''4 a'4 | c''4 b'8 a' g'4 fis'4 | g'2 r4 d''4 |
\break dis''4 e''8 fis'' g''4 dis''4 | e''4 d''?4 c''8 b' a'4 | ais'4 b'8 cis'' d''4 cis''4 | c''!4 b'2 r4 |
\break fisis''4 gis''8 fis'' f''4 e''4 | ees''4 d''8 des'' c''4 ces''4 | bes'4 beses'8 bes' aes'4 g'4 | fis'2 r4 d'4 |
\break d'8 dis' e' eis' fis' g' gis' a' | ais'8 b' c'' cis'' d'' dis'' e'' f'' |
  fis''?8 f'' e'' ees'' d'' des'' c'' b' | bes'8 a' aes' g' fis'4 r4 |
\break g'4 gis'2.~ | gis'4 gis'4 a'2 | cis''8 e'' a'4 c'8 e' c''4 | b'2 g'2 |
"""


def mk_accstorm():
    def make():
        sc = build([{'id': 'FL', 'name': 'Flute', 'abbr': 'Fl.', 'clef': 'treble', 'instrument': 'flute',
                     'music': ACC_FL}], time=(4, 4), key=(1, 'major'))
        sc.title = 'Accidental Storm'
        sc.composer = 'Pitch challenge corpus (CC0)'
        sc.rights = 'CC0 1.0 - composed for the OMR challenge corpus'
        lay = single_staff_layout([('FL', 'Flute', 'Fl.', 'treble', [])])
        opts = base_opts('Accidental Storm', 'study for flute', 'challenge corpus (CC0)', size=21,
                         extra_paper=['system-system-spacing.basic-distance = #15', 'top-margin = 16\\mm'])
        return sc, lay, opts
    return make


# ================================================================= 4. ledger lines + ottava (flute + tuba)

LED_FL = r"""
c''4 e'' g'' c''' | e'''4 g''' c''''2 | b'''4 a''' g''' f''' | e'''2 r2 |
\break \ottava=1 c''''4 d'''' b''' g''' | a'''4 c'''' g'''2 \ottava=0 | c''''4 d'''' b''' g''' | a'''4 c'''' g'''2 |
\break g''4 \ottava=1 g'''4 a''' b''' | c''''2 \ottava=0 c'''2 | e'''4 \ottava=1 f''' a''' c'''' | b'''4 g''' e''' f''' |
\break d'''4 b'' \ottava=0 c'''2 | g''4 c''' e''' g''' | c''''1 | c'''1 |
"""
LED_TUBA = r"""
c,1 | g,,2 c,2 | g,,1 | c,2 r2 |
\ottava=-1 c,,4 e,, g,, c, | f,,4 a,, g,,2 \ottava=0 | c,,4 e,, g,, c, | f,,4 a,, g,,2 |
c,2 \ottava=-1 c,,2 | e,,4 d,, c,,2 \ottava=0 | c,1 | \ottava=-1 g,,2 d,,2 |
c,,2 \ottava=0 c,2 | e,2 g,2 | c,1 | c,,1 |
"""


def mk_ledger():
    def make():
        sc = build([{'id': 'FL', 'name': 'Flute', 'abbr': 'Fl.', 'clef': 'treble', 'instrument': 'flute',
                     'music': LED_FL},
                    {'id': 'TU', 'name': 'Tuba', 'abbr': 'Tba.', 'clef': 'bass', 'instrument': 'tuba',
                     'music': LED_TUBA}], time=(4, 4), key=(0, 'major'))
        sc.title = 'Heights and Depths'
        sc.composer = 'Pitch challenge corpus (CC0)'
        sc.rights = 'CC0 1.0 - composed for the OMR challenge corpus'
        lay = single_staff_layout([('FL', 'Flute', 'Fl.', 'treble', []), ('TU', 'Tuba', 'Tba.', 'bass', [])],
                                  group='StaffGroup')
        opts = base_opts('Heights and Depths', 'duet for flute and tuba', 'challenge corpus (CC0)', size=19,
                         extra_paper=['indent = 15\\mm', 'short-indent = 8\\mm',
                                      'system-system-spacing.basic-distance = #22'])
        opts['paper_extra'] = [x for x in opts['paper_extra'] if x != 'indent = 0']
        return sc, lay, opts
    return make


# ================================================================= 5. SATB closed, chromatic (Abide with me)

ABIDE_S = r"""
g'4 | g'4 aes'4 bes'4 ees''4 | d''4 c''4 bes'4 a'4 | bes'2 r4 bes'4 |
\break c''4 ces''4 bes'4 aes'4 | g'4 f'4 e'4 f'4 | g'2 r4 g'4 |
\break aes'4 g'4 fis'4 g'4 | c''4 bes'4 aes'4 a'4 | bes'2 r4 bes'4 |
\break ees''4 d''4 des''4 c''4 | b'4 c''4 aes'4 f'4 | ees'2. |
"""
ABIDE_CH = ['Eb',
            '-', 'Fm', 'Eb/G', 'Ab',
            'Bb', 'Cm', 'Gm', 'F7',
            'Bb', 'Eb',
            'Ab', 'Abm', 'Eb/Bb', 'Bb7',
            'Eb', 'Bb/D', 'C7', 'Fm',
            'Eb/G', 'Cm',
            'Fm', 'Cm', 'D7', 'Gm',
            'Ab', 'Eb', 'Abm', 'Cbger6',
            'Eb/Bb', 'Bb7',
            'Eb', 'Bb/D', 'Eb7', 'Ab',
            'G7', 'Cm', 'Fm', 'Bb7',
            'Eb']
ABIDE_V = [
    "A -- bide with me; fast falls the e -- ven -- tide; The dark -- ness deep -- ens; Lord, with me a -- bide. "
    "When oth -- er help -- ers fail and com -- forts flee, Help of the help -- less, O a -- bide with me.",
    "Swift to its close ebbs out life's lit -- tle day; Earth's joys grow dim, its glo -- ries pass a -- way; "
    "Change and de -- cay in all a -- round I see; O thou who chang -- est not, a -- bide with me.",
]
SATB_NAMES = [('S', 'Soprano', 'S.'), ('A', 'Alto', 'A.'), ('T', 'Tenor', 'T.'), ('B', 'Bass', 'B.')]


# hand re-voicing after the solver (bar index 0 = pickup): creates the two shared-staff cases
#   bar 2: Bb - F7 - Bb/D - F7, alto A4-natural on beat 2 carries to the soprano A4 on beat 4
#   bar 7: beat 4 Gm7, alto F4 after the soprano F#4 needs a natural on the shared staff only
ABIDE_REVOICE = {
    ('A', 2): [('B', -1, 4), ('A', 0, 4), ('F', 0, 4), ('E', -1, 4)],
    ('T', 2): [('B', -1, 3), ('E', -1, 4), ('B', -1, 3), ('C', 0, 4)],
    ('B', 2): [('B', -1, 2), ('F', 0, 3), ('D', 0, 3), ('F', 0, 3)],
    ('T', 3): [('B', -1, 3), None, None],
    ('A', 7): [None, None, None, ('F', 0, 4)],
}


def revoice(sc, table):
    for (pid, mi), pitches in table.items():
        evs = [e for e in sc.part(pid).measures[mi]['1'] if e.kind in ('note', 'rest')]
        assert len(evs) == len(pitches), (pid, mi, len(evs))
        for ev, p in zip(evs, pitches):
            if p is None:
                continue
            assert ev.kind == 'note' and not ev.tie_start and not ev.tie_stop
            ev.pitches = [p]


def mk_abide(report):
    def make():
        sc = satb_from_soprano(ABIDE_S, ABIDE_CH, (-3, 'major'), (4, 4), 3, SATB_NAMES)
        revoice(sc, ABIDE_REVOICE)
        set_verses(sc, 'S', '1', ABIDE_V, mode='attack')
        for pid, c in (('T', 'bass'), ('B', 'bass')):
            sc.part(pid).clefs = [c]
        sc.title = 'Abide with Me'
        sc.composer = 'chromatic harmonisation: pitch challenge corpus (CC0)'
        sc.lyricist = 'Henry Francis Lyte (1847)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')], [(('S', '1'), [1, 2], 'below')],
                            names=('S. A.', 'T. B.', 'S.A.', 'T.B.'))
        from .acc import layout_staves
        report[:] = add_courtesy(sc, layout_staves(lay), every=2)
        opts = base_opts('Abide with Me', '', 'chromatic setting (CC0)', 'H. F. Lyte, 1847', size=20,
                         extra_paper=['indent = 12\\mm', 'system-system-spacing.basic-distance = #18'],
                         extra_layout=['\\context { \\Score \\remove "Bar_number_engraver" }'])
        opts['paper_extra'] = [x for x in opts['paper_extra'] if x != 'indent = 0']
        opts['auto_beam_off_vocal'] = True
        return sc, lay, opts
    return make


# ================================================================= 6. TTBB enharmonic key change (Now the day is over)

DAY_T1 = r"""
bes4 bes4 ces'4 ces'4 | des'2 bes2 | aes4 aes4 bes4 ges4 | aes1 | bes4 bes4 ces'4 ces'4 |
\break des'2 ees'2 | des'4 ces'4 bes4 aes4 | ges1 \bar=|| |
\key=6 ais4 ais4 b4 b4 | cis'2 ais2 |
\break gis4 gis4 ais4 fis4 | gis1 | ais4 ais4 b4 b4 | cis'2 dis'2 | cis'4 b4 ais4 gis4 |
\break fis1 \bar=|| | \key=2 fis'4 e'4 d'4 cis'4 | d'1 | d'1 | d'1 |
"""
DAY_CH = (['Gb', 'Ebm', 'Cb', 'Abm', 'Db', 'Gb', 'Db', 'Abm', 'Gb', 'Ab7', 'Db',
           'Gb', 'Bbm', 'Cb', 'Cbm', 'Bbm', 'Cb', 'Gb/Db', 'Db7', 'Gb', 'Db7', 'Gb'] +
          ['F#', 'D#m', 'B', 'G#m', 'C#', 'F#', 'G#m', 'E7', 'F#', 'G#7', 'C#',
           'F#', 'D#7', 'G#m', 'Bm', 'F#/C#', 'B', 'F#/C#', 'C#7', 'F#', 'C#7', 'F#'] +
          ['D', 'A', 'Bm', 'A7', 'D', 'Gm', 'D'])
DAY_V = ["Now the day is o -- ver, Night is draw -- ing nigh, Shad -- ows of the eve -- ning Steal a -- cross the sky. "
         "Now the dark -- ness gath -- ers, Stars be -- gin to peep, Birds and beasts and flow -- ers "
         "Soon will be a -- sleep. Soon will be a -- sleep. A -- men."]
TTBB_NAMES = [('T1', 'Tenor I', 'T. I'), ('T2', 'Tenor II', 'T. II'), ('BR', 'Baritone', 'Bar.'),
              ('BS', 'Bass', 'B.')]


def mk_dayover(report):
    def make():
        sc = satb_from_soprano(DAY_T1, DAY_CH, (-6, 'major'), (4, 4), 6, TTBB_NAMES, ranges=TTBB)
        set_verses(sc, 'T1', '1', DAY_V, mode='attack')
        for pid, c in (('T1', 'treble_8'), ('T2', 'treble_8'), ('BR', 'bass'), ('BS', 'bass')):
            sc.part(pid).clefs = [c]
        sc.title = 'Now the Day Is Over'
        sc.composer = 'pitch challenge corpus (CC0)'
        sc.lyricist = 'Sabine Baring-Gould (1865)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'T1', 'last': 'BS', 'symbol': 'bracket'}]
        lay = closed_layout([('T1', '1'), ('T2', '1')], [('BR', '1'), ('BS', '1')], [(('T1', '1'), [1], 'below')],
                            names=('T. I II', 'Bar. B.', 'T.', 'B.'), clefs=('treble_8', 'bass'))
        from .acc import layout_staves
        report[:] = add_courtesy(sc, layout_staves(lay), every=3)
        opts = base_opts('Now the Day Is Over', 'for male voices (TTBB)', 'challenge corpus (CC0)',
                         'Sabine Baring-Gould, 1865', size=19,
                         extra_paper=['indent = 14\\mm', 'system-system-spacing.basic-distance = #17'])
        opts['paper_extra'] = [x for x in opts['paper_extra'] if x != 'indent = 0']
        opts['auto_beam_off_vocal'] = True
        return sc, lay, opts
    return make


# ================================================================= 7. 2-page chromatic song (Lead, kindly Light)

LEAD_S = r"""
c''2 bes'4 aes'4 | ees''2 r4 c''4 | des''4 c''4 bes'4 g'4 | aes'2 r2 |
\break c''4 cis''4 d''2 | ees''2. r4 | r4 c''4 des''4 c''4 | ces''2 bes'4 aes'4 |
\break g'4 aes'4 fes'4 ees'4~ | ees'2 r2 | ees''4 d''4 des''2 | c''2. r4 |
\break aes'4 bes'4 c''4 des''4 | r4 ees''4 f''4 ges''4 | f''4 e''4 f''2 | r4 ees''4 des''4 c''4 |
\break bes'2 r4 aes'4 | g'4 aes'4 bes'4 beses'4 | aes'1 | r1 \bar=|| |
\pagebreak \key=4 gis'4 a'4 b'4 cis''4 | dis''4 e''2 b'4 | bis'4 cis''4 e''2 | e''4 eis''4 fis''4 fisis''4( |
\break gis''2.) r4 | r4 e''4 dis''4 d''4 | cis''2 c''4 b'4 | ais'4 b'4 r4 b'4 |
\break e''1 | gis'4 a'4 b'4 bis'4~ | bis'2 cis''4 r4 | r4 b'4 cis''4 d''4 |
\break e''4 fis''4 g''2 | r4 g''4 fis''4 eis''4 | fis''1 | a''4 gis''4 fis''4 e''4 |
\break r4 cis''4 d''4 dis''4 | e''4 dis''4 e''2~ | e''1 |
"""
LEAD_V = ["Lead, kind -- ly Light, a -- mid th'en -- cir -- cling gloom, Lead thou me on; "
          "The night is dark, and I am far from home; Lead thou me on. "
          "Keep thou my feet; I do not ask to see The dis -- tant scene; one step e -- nough for me. "
          "I was not ev -- er thus, nor prayed that thou Shouldst lead me on; _ "
          "I loved to choose and see my path; but now Lead thou me on. _ "
          "I loved the gar -- ish day, and, spite of fears, Pride ruled my will: re -- mem -- ber not past years."]


def mk_lead():
    def make():
        sc = build([{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'clef': 'treble', 'music': LEAD_S}],
                   time=(4, 4), key=(-4, 'major'))
        set_verses(sc, 'S', '1', LEAD_V, mode='attack')
        sc.title = 'Lead, Kindly Light'
        sc.composer = 'pitch challenge corpus (CC0)'
        sc.lyricist = 'John Henry Newman (1833)'
        sc.rights = 'Text public domain; music CC0 1.0'
        lay = single_staff_layout([('S', 'Soprano', 'S.', 'treble', [1])])
        opts = base_opts('Lead, Kindly Light', 'song for soprano (two stanzas)', 'challenge corpus (CC0)',
                         'J. H. Newman, 1833', size=23,
                         extra_paper=['system-system-spacing.basic-distance = #17', 'top-margin = 15\\mm',
                                      'print-page-number = ##t'])
        opts['auto_beam_off_vocal'] = True
        return sc, lay, opts
    return make


# ================================================================= 8. SATB closed, ledger extremes

BRIGHT_S = r"""d''4 fis'' a'' | b''4 a'' fis'' | a''2 r4 | g''4 fis'' e'' | fis''4 e''2 | d''2. |
\break d''4 fis'' a'' | d'''4 cis''' b'' | a''2 r4 | b''4 a'' g'' | fis''4 e''2 | d''2. |"""
BRIGHT_A = r"""a4 d' fis' | g'4 d' d' | e'2 r4 | e'4 d' cis' | d'4 cis'2 | d'2. |
fis'4 d'' cis'' | b'4 a' fis' | cis''2 r4 | d''4 d'' b' | d''4 cis''2 | a'2. |"""
BRIGHT_T = r"""fis4 a d' | d'4 a b | cis'2 r4 | b4 a a | a4 g2 | fis2. |
d'4 a' a' | g'4 e' d' | e'2 r4 | g'4 a' e' | fis'4 g'2 | fis'2. |"""
BRIGHT_B = r"""d,4 fis, a, | g,4 fis, b,, | a,,2 r4 | e,4 fis, a,, | d,4 a,,2 | d,2. |
b,,4 d, fis, | g,4 a, b, | a,2 r4 | g,4 fis, e, | a,,4 a,,2 | d,2. |"""
BRIGHT_V = ["All things bright and beau -- ti -- ful, All crea -- tures great and small, "
            "All things wise and won -- der -- ful, The Lord God made them all.",
            "Each lit -- tle flower that o -- pens, Each lit -- tle bird that sings, "
            "He made their glow -- ing col -- ours, He made their ti -- ny wings."]


def mk_bright():
    def make():
        sc = build([{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'clef': 'treble', 'music': BRIGHT_S},
                    {'id': 'A', 'name': 'Alto', 'abbr': 'A.', 'clef': 'treble', 'music': BRIGHT_A},
                    {'id': 'T', 'name': 'Tenor', 'abbr': 'T.', 'clef': 'bass', 'music': BRIGHT_T},
                    {'id': 'B', 'name': 'Bass', 'abbr': 'B.', 'clef': 'bass', 'music': BRIGHT_B}],
                   time=(3, 4), key=(2, 'major'))
        set_verses(sc, 'S', '1', BRIGHT_V, mode='attack')
        sc.title = 'All Things Bright and Beautiful'
        sc.composer = 'descant setting: pitch challenge corpus (CC0)'
        sc.lyricist = 'Cecil Frances Alexander (1848)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        lay = closed_layout([('S', '1'), ('A', '1')], [('T', '1'), ('B', '1')], [(('S', '1'), [1, 2], 'below')])
        opts = base_opts('All Things Bright and Beautiful', 'SATB, extreme ranges', 'challenge corpus (CC0)',
                         'C. F. Alexander, 1848', size=20,
                         extra_paper=['system-system-spacing.basic-distance = #20', 'top-margin = 18\\mm'])
        opts['auto_beam_off_vocal'] = True
        return sc, lay, opts
    return make
