"""Helpers shared by the layouts-family pieces (coverage suite)."""
from __future__ import annotations

from fractions import Fraction as F

from csynth.dsl import mdur, parse_voice
from csynth.model import MeasureInfo, Part, Score, VoiceDef, renumber

CC0_NOTE = ('Composition, arrangement, engraving, rasterisation and damage simulation produced for the OMR '
            'coverage suite (corpus/coverage/layouts/_tools, 2026). All files of this item are dedicated to the '
            'public domain (CC0 1.0 Universal).')
COMPOSER = 'Coverage suite (2026)'
RIGHTS = 'CC0 1.0 - dedicated to the public domain'


def mk_part(pid, name, abbr='', instrument='voice', staves=1, clefs=('treble',), voices=(('1', 1),)):
    p = Part(id=pid, name=name, abbr=abbr, instrument=instrument, staves=staves, clefs=list(clefs))
    p.voices = [VoiceDef(k, s) for k, s in voices]
    return p


def assemble(time, key, parts_voices, time_symbol=None):
    """parts_voices: list of (Part, {vkey: dsl text or parsed measure list}).  Every voice must have
    the same number of measures and every non-empty voice the same duration per measure."""
    parsed = []
    nm = None
    for part, vd in parts_voices:
        pv = {}
        for k, txt in vd.items():
            ms = parse_voice(txt, time) if isinstance(txt, str) else txt
            if nm is None:
                nm = len(ms)
            if len(ms) != nm:
                raise ValueError(f'{part.id}:{k} has {len(ms)} measures, expected {nm}')
            pv[k] = ms
        parsed.append((part, pv))
    sc = Score()
    nominal = F(time[0] * 4, time[1])
    for i in range(nm):
        dur = max(mdur(pv[k][i]) for _, pv in parsed for k in pv)
        for part, pv in parsed:
            for k in pv:
                d = mdur(pv[k][i])
                if d not in (dur, F(0)):
                    raise ValueError(f'measure {i + 1}: {part.id}:{k} has {d}, others {dur}')
        if i not in (0, nm - 1) and dur != nominal:
            raise ValueError(f'measure {i + 1} has duration {dur}, bar is {nominal}')
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        sc.measures.append(mi)
    for part, pv in parsed:
        part.measures = [{k: pv[k][i] for k in pv} for i in range(nm)]
        sc.parts.append(part)
    sc.measures[-1].right_bar = 'final'
    renumber(sc)
    return sc


def add_mark(sc, i, kind, **kw):
    sc.measures[i].marks.append(dict(kind=kind, **kw))


def add_end_mark(sc, i, text, **kw):
    sc.measures[i].end_marks.append(dict(kind='words', text=text, **kw))


def breaks(sc, systems=(), pages=()):
    for i in systems:
        sc.measures[i].brk = 'system'
    for i in pages:
        sc.measures[i].brk = 'page'


def header(sc, title, subtitle='', composer=COMPOSER, lyricist='', extra_credits=()):
    sc.title = title
    sc.composer = composer
    sc.lyricist = lyricist
    sc.rights = RIGHTS
    cr = [{'page': 1, 'type': 'title', 'text': title}]
    if subtitle:
        cr.append({'page': 1, 'type': 'subtitle', 'text': subtitle})
    if lyricist:
        cr.append({'page': 1, 'type': 'lyricist', 'text': lyricist})
    cr.append({'page': 1, 'type': 'composer', 'text': composer})
    cr += list(extra_credits)
    sc.credits = cr
    h = {'title': title, 'composer': composer}
    if subtitle:
        h['subtitle'] = subtitle
    if lyricist:
        h['poet'] = lyricist
    return h


def opts(hdr, staff_size=20, paper='a4', extra_paper=(), extra_layout=(), **kw):
    o = {'header': hdr, 'staff_size': staff_size, 'paper': paper, 'font': 'TeX Gyre Schola',
         'forced_breaks': True,
         'paper_extra': ['ragged-bottom = ##t', 'ragged-last-bottom = ##t', 'top-margin = 14\\mm',
                         'bottom-margin = 14\\mm', 'left-margin = 18\\mm', 'right-margin = 16\\mm'] + list(extra_paper),
         # hyphens/extenders must be visible: reserve room for them (LilyPond drops them when syllables are tight)
         'layout_extra': ['\\context { \\Lyrics \\override LyricHyphen.minimum-distance = #1.6 '
                          '\\override LyricExtender.minimum-length = #0.6 }'] + list(extra_layout)}
    o.update(kw)
    return o


def first_note(sc, pid, vkey, i, k=0):
    return [e for e in sc.part(pid).measures[i][vkey] if e.kind == 'note'][k]


# ------------------------------------------------------------------ scan damage presets
CREAM = (243, 236, 214)
YELLOWED = (236, 226, 198)

TYPICAL = {
    'T1': ('300 dpi grey flatbed scan, 0.6 deg skew, light paper texture and noise, JPEG q75',
           dict(dpi=300, mode='gray', texture=2, rotate=0.6, blur=0.4, noise=3, jpeg=75)),
    'T2': ('200 dpi grey office scan, -0.9 deg skew, slight lighting gradient, noise, JPEG q70',
           dict(dpi=200, mode='gray', texture=3, rotate=-0.9, gradient=0.05, blur=0.5, noise=4, jpeg=70)),
    'T3': ('300 dpi colour scan on cream paper, 0.4 deg skew, noise, JPEG q80',
           dict(dpi=300, mode='rgb', paper_rgb=CREAM, texture=3, rotate=0.4, blur=0.4, noise=3, jpeg=80)),
    'T4': ('250 dpi grey scan, 1.2 deg skew, soft focus, toner specks, JPEG q65',
           dict(dpi=250, mode='gray', texture=3, rotate=1.2, blur=0.6, noise=4, speckle=20, jpeg=65)),
    'T5': ('240 dpi grey scan, -0.5 deg skew, faint bleed-through, JPEG q72',
           dict(dpi=240, mode='gray', texture=2, rotate=-0.5, bleed=0.04, blur=0.45, noise=3, jpeg=72)),
}
SEVERE = {
    'S1': ('thin, faded binarised photocopy at 150 dpi (rendered 300): ink dropout, 3 deg skew, broken lines, '
           'salt & pepper, toner specks',
           dict(dpi=300, out_dpi=150, ink_dropout=0.12, rotate=3.0, blur=0.6, noise=8, binarize=118,
                binarize_noise=20, saltpepper=0.0015, speckle=120, format='png1')),
    'S2': ('phone photo of the page: perspective/keystone, uneven light, vignette, motion blur, 150 dpi, JPEG q25',
           dict(dpi=150, mode='rgb', paper_rgb=CREAM, texture=6, rotate=-2.5,
                phone={'margin': 0.06, 'bg': 50, 'jitter': 0.035, 'keystone': 0.06},
                blotch=0.25, vignette=0.3, motion_blur={'len': 5, 'angle': 25}, noise=6, jpeg=25)),
    'S3': ('low-resolution 120 dpi grey scan, -4 deg skew, heavy blur and noise, JPEG q20',
           dict(dpi=240, out_dpi=120, mode='gray', texture=6, rotate=-4.0, blur=1.3, noise=10, jpeg=20)),
    'S4': ('thick dark binarised photocopy at 200 dpi: ink spread, 2.5 deg skew, staple, two punch holes, '
           'salt & pepper',
           dict(dpi=200, ink_weight=1, rotate=2.5, punch_holes={'n': 2, 'side': 'left', 'level': 10},
                staple={'corner': 'tl'}, blur=0.9, noise=12, binarize=200, binarize_noise=20, saltpepper=0.002,
                format='png1')),
    'S5': ('old yellowed copy: bleed-through, foxing, coffee ring, pencil annotations, 150 dpi colour, 2 deg skew, '
           'JPEG q30',
           dict(dpi=150, mode='rgb', paper_rgb=YELLOWED, texture=6, bleed=0.12, foxing={'n': 40},
                coffee={'n': 1, 'r': 0.1, 'strength': 0.9},
                pencil={'circles': 2, 'marks': 3, 'texts': ['rit.', 'breathe', 'p!'], 'lines': 1},
                rotate=2.0, blur=0.7, noise=6, jpeg=30)),
}


def scans(n, typical, severe):
    """damage plan for item number n (seeds 7000+10n..)"""
    ts, tp = TYPICAL[typical]
    ss, sp = SEVERE[severe]
    return {'scan.pdf': {'seed': 7000 + 10 * n + 1, 'preset': typical, 'summary': ts, 'params': dict(tp)},
            'scan-severe.pdf': {'seed': 7000 + 10 * n + 2, 'preset': severe, 'summary': ss, 'params': dict(sp)}}


def satb(sop_text, chords, tonic_pc):
    """soprano DSL + one chord symbol per soprano note -> dict S/A/T/B of parsed measure lists
    (homophonic harmonisation by the corpus voice-leading solver)"""
    from csynth.harmonize import harmonize
    sop = parse_voice(sop_text)
    alt, ten, bas = harmonize(sop, chords, tonic_pc)
    return {'S': sop, 'A': alt, 'T': ten, 'B': bas}
