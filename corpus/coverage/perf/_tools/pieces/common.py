"""Helpers shared by the perf pieces (adapted from corpus/challenge/layout/_tools/pieces/common.py)."""
from __future__ import annotations

from fractions import Fraction as F

from cov.dsl import mdur, parse_voice
from cov.model import Event, MeasureInfo, Part, Score, VoiceDef, renumber, split_plain

CC0_NOTE = ('Engraving, truth encoding, rasterisation and scan simulation produced by the coverage/perf '
            'generator (corpus/coverage/perf/_tools); all generated files are dedicated to the public '
            'domain (CC0 1.0).')

# page geometry: name -> (LilyPond paper, width mm, height mm)
PAPER = {'A4': ('a4', 210.0, 297.0), 'Letter': ('letter', 215.9, 279.4), 'A3': ('a3', 297.0, 420.0)}


def mk_part(pid, name, abbr='', instrument='voice', staves=1, clefs=('treble',), voices=(('1', 1),)):
    p = Part(id=pid, name=name, abbr=abbr, instrument=instrument, staves=staves, clefs=list(clefs))
    p.voices = [VoiceDef(k, s) for k, s in voices]
    return p


def assemble(time, key, parts_voices, time_symbol=None, measures=None):
    """parts_voices: [(Part, {vkey: dsl text or parsed measure list})] -> Score.
    Measure lengths come from the longest voice; time changes must be set before with
    `times` = {measure index: ((n, d), symbol)}."""
    parsed = []
    nm = None
    for part, vd in parts_voices:
        pv = {}
        for k, txt in vd.items():
            ms = parse_voice(txt) if isinstance(txt, str) else txt
            if nm is None:
                nm = len(ms)
            if len(ms) != nm:
                raise ValueError(f'{part.id}:{k} has {len(ms)} measures, expected {nm}')
            pv[k] = ms
        parsed.append((part, pv))
    sc = Score()
    for i in range(nm):
        dur = max(mdur(pv[k][i]) for _, pv in parsed for k in pv)
        for part, pv in parsed:
            for k in pv:
                d = mdur(pv[k][i])
                if d not in (dur, F(0)) and not all(e.kind in ('space',) for e in pv[k][i]):
                    raise ValueError(f'measure {i + 1}: {part.id}:{k} has {d}, others {dur}')
        sc.measures.append(MeasureInfo(number=i + 1, dur=dur, nominal=F(time[0] * 4, time[1])))
    m0 = sc.measures[0]
    m0.time, m0.time_symbol, m0.key = time, time_symbol, key
    for part, pv in parsed:
        part.measures = [{k: pv[k][i] for k in pv} for i in range(nm)]
        sc.parts.append(part)
    return sc


def set_time(sc, i, time, symbol=None):
    sc.measures[i].time = time
    sc.measures[i].time_symbol = symbol
    nominal = F(time[0] * 4, time[1])
    for j in range(i, len(sc.measures)):
        if j > i and sc.measures[j].time:
            break
        sc.measures[j].nominal = nominal


def finish_measures(sc):
    """pickup flag, nominal-length checks, numbering"""
    m0 = sc.measures[0]
    m0.implicit = m0.dur < m0.nominal
    for i, mi in enumerate(sc.measures):
        if i > 0 and i < len(sc.measures) - 1 and mi.dur != mi.nominal:
            raise ValueError(f'measure index {i} has {mi.dur}, nominal {mi.nominal}')
    renumber(sc)


def add_mark(sc, i, kind, **kw):
    sc.measures[i].marks.append(dict(kind=kind, **kw))


def full_rest(dur):
    """whole-bar rest event of the given length"""
    ev = Event('rest', F(dur), dtype='whole', dots=0)
    ev.measure_rest = True
    return ev
