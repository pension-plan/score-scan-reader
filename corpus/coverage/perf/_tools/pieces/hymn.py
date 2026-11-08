"""One-page SATB hymn (closed score, four stanzas underlaid between the staves).

Tune "BENCHMARK" C.M. and its harmonisation: composed for this corpus (CC0); harmonisation by the
corpus voice-leading solver (cov/harmonize.py) from the chord plan below.
Text: Isaac Watts, "O God, our help in ages past" (1719), stanzas 1-4 - public domain.
"""
from __future__ import annotations

import copy
from fractions import Fraction as F

from cov.dsl import parse_voice
from cov.harmonize import harmonize
from cov.model import Event, split_plain

from .common import CC0_NOTE, PAPER, add_mark, assemble, finish_measures, mk_part

SOP = ("bes'4\\mf | ees''2 d''4 | c''2 bes'4 | aes'4( g'4) f'4 | g'2\\fermata bes'4 | "
       "ees''2 f''4 | g''4.( f''8) ees''4 | d''2\\fermata bes'4\\f | ees''2 g''4 | aes''4( g''8 f''8) ees''4 | "
       "c''2 d''4 | ees''2\\fermata bes'4\\p | c''2\\> aes'4 | g'2 f'4\\! | ees'2.\\fermata")
CHORDS = ['Eb',
          'Eb', 'Bb/D', 'Cm', 'Eb', 'Fm', '~', 'Bb', 'Eb', 'Bb7',
          'Eb', 'Bb', 'Cm', '~', 'Ab', 'Bb', 'Eb',
          'Eb', 'Eb7', 'Ab', '~', '~', 'Cm', 'F7', 'Bb', 'Eb', '-',
          'Ab', 'Fm', 'Eb/Bb', 'Bb7', 'Eb']
VERSES = [
    "O God, our help in a -- ges past, Our hope for years to come, "
    "Our shel -- ter from the storm -- y blast, And our e -- ter -- nal home.",
    "Un -- der the sha -- dow of thy throne Thy saints have dwelt se -- cure; "
    "Suf -- fi -- cient is thine arm a -- lone, And our de -- fence is sure.",
    "Be -- fore the hills in or -- der stood, Or earth re -- ceived her frame, "
    "From ev -- er -- last -- ing thou art God, To end -- less years the same.",
    "A thou -- sand a -- ges in thy sight Are like an eve -- ning gone; "
    "Short as the watch that ends the night Be -- fore the ris -- ing sun.",
]


def _merge_holds(measures):
    """lower voices from the solver repeat the soprano rhythm with ties on held chords: merge a held
    chain inside one measure into one note when the total is a plain duration; drop copied slurs."""
    out = []
    for mm in measures:
        new = []
        for ev in mm:
            ev = copy.copy(ev)
            ev.slur_start = ev.slur_stop = 0
            ev.dynamics = []
            ev.wedge = []
            if new and ev.kind == 'note' and new[-1].kind == 'note' and new[-1].tie_start and \
                    ev.pitches == new[-1].pitches:
                prev = new[-1]
                tot = prev.dur + ev.dur
                sp = split_plain(tot)
                if len(sp) == 1:
                    prev.dur = tot
                    prev.dtype, prev.dots = sp[0][0], sp[0][1]
                    prev.tie_start = set(ev.tie_start)
                    prev.fermata = prev.fermata or ev.fermata
                    continue
            new.append(ev)
        out.append(new)
    # re-derive tie stops
    prev = None
    for mm in out:
        for ev in mm:
            if ev.kind != 'note':
                prev = None
                continue
            ev.tie_stop = set(p for p in ev.pitches if prev is not None and p in prev.tie_start)
            prev = ev
    return out


def make(paper='A4'):
    sop = parse_voice(SOP)
    alt, ten, bas = harmonize(sop, CHORDS, 3)
    alt, ten, bas = (_merge_holds(x) for x in (alt, ten, bas))
    # tenor carries the same dynamics as the soprano (printed on the lower staff)
    for mi, mm in enumerate(sop):
        for k, ev in enumerate(mm):
            if ev.dynamics and ev.kind == 'note':
                t = sum((e.dur for e in mm[:k]), F(0))
                tt = F(0)
                for e2 in ten[mi]:
                    if tt == t and e2.kind == 'note':
                        e2.dynamics = list(ev.dynamics)
                        break
                    tt += e2.dur
    parts = [mk_part('S', 'Soprano', 'S.'), mk_part('A', 'Alto', 'A.'),
             mk_part('T', 'Tenor', 'T.', clefs=('bass',)), mk_part('B', 'Bass', 'B.', clefs=('bass',))]
    sc = assemble((3, 4), (-3, 'major'), [(parts[0], {'1': sop}), (parts[1], {'1': alt}),
                                         (parts[2], {'1': ten}), (parts[3], {'1': bas})])
    sc.measures[-1].right_bar = 'final'
    finish_measures(sc)
    from cov.model import set_verses
    set_verses(sc, 'S', '1', VERSES)
    add_mark(sc, 0, 'tempo', text='Moderato', unit='quarter', bpm=92)
    for i in (4, 8, 12):
        sc.measures[i].brk = 'system'
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    sc.title = 'O God, Our Help in Ages Past'
    sc.composer = 'BENCHMARK C.M. (coverage corpus, CC0)'
    sc.lyricist = 'Isaac Watts, 1719'
    sc.rights = 'Text public domain; tune, harmonisation and engraving CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'O God, Our Help in Ages Past'},
                  {'page': 1, 'type': 'subtitle', 'text': 'BENCHMARK  C.M.'},
                  {'page': 1, 'type': 'lyricist', 'text': 'Isaac Watts, 1719'},
                  {'page': 1, 'type': 'composer', 'text': 'Tune and harmony: coverage corpus (CC0)'}]
    pname, wmm, hmm = PAPER[paper]
    scale = {'A4': 1.0, 'Letter': 1.0, 'A3': 2 ** 0.5}[paper]
    staff = 18.5 * scale
    sc.page = {'name': paper, 'width_mm': wmm, 'height_mm': hmm, 'staff_size': staff}
    layout = {'groups': [{'type': 'ChoirStaff', 'staves': [
        {'id': 'sa', 'clef': 'treble', 'voices': [('S', '1'), ('A', '1')],
         'lyrics': [{'voice': ('S', '1'), 'verses': [1, 2, 3, 4], 'stanza': True}]},
        {'id': 'tb', 'clef': 'bass', 'voices': [('T', '1'), ('B', '1')]}]}]}
    mg = lambda v: f'{v * scale:.2f}\\mm'
    tb = 7 if paper == 'Letter' else 12          # US letter is 17.6 mm shorter than A4
    opts = {'header': {'title': 'O God, Our Help in Ages Past', 'subtitle': 'BENCHMARK  C.M.',
                       'poet': 'Isaac Watts, 1719', 'composer': 'Tune and harmony: coverage corpus (CC0)'},
            'staff_size': round(staff, 3), 'paper': pname,
            'paper_extra': [f'top-margin = {mg(tb)}', f'bottom-margin = {mg(tb)}', f'left-margin = {mg(15)}',
                            f'right-margin = {mg(15)}', 'indent = 0', 'ragged-last-bottom = ##f',
                            'system-system-spacing.basic-distance = #12'],
            'layout_extra': ['\\context { \\Score \\remove "Bar_number_engraver" }']}
    info = dict(
        layout='hymnal-stanzas', layout_also=['choir-closed-satb'],
        parts=['Soprano', 'Alto', 'Tenor', 'Bass'], must_not_split=False,
        expected_notes=('Closed SATB score: Soprano + Alto share the treble staff (stems up / down), Tenor + '
                        'Bass the bass staff; they must become 4 separate parts. Four stanzas are underlaid '
                        'below the treble staff and belong to the Soprano part (lyric numbers 1-4).'),
        truth_limitations=('Stanza labels "1."-"4." are printed but MusicXML has no element for them (only '
                           'lyric number=1..4); stanza-text count comes from the engraving. Lyrics printed '
                           'between the staves are encoded on the Soprano part only. Dynamics printed on both '
                           'staves are encoded on Soprano and Tenor.'),
        title='O God, Our Help in Ages Past (BENCHMARK C.M.) - 1-page SATB hymn, 4 stanzas',
        license='CC0', source='own composition (tune + harmony) on a public-domain text (Watts 1719)',
        attribution='\n'.join([
            'O God, Our Help in Ages Past.',
            'Text: Isaac Watts (1674-1748), Psalm 90, 1719 - public domain.',
            'Tune BENCHMARK C.M. and SATB harmonisation: composed for the coverage corpus - CC0 1.0.',
            '', CC0_NOTE]),
    )
    return sc, layout, opts, info
