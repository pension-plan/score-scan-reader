"""Helpers shared by the layout-challenge pieces."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from lsynth.dsl import mdur, parse_voice
from lsynth.harmonize import chord_tones
from lsynth.model import STEP_PC, Event, MeasureInfo, Part, Score, VoiceDef, midi, renumber

ACC = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}
CC0_NOTE = ('Engraving, rasterisation and damage simulation produced by the layout-challenge generator '
            '(corpus/challenge/layout/_tools); these derived files are dedicated to the public domain (CC0 1.0).')


def lyp(p):
    """(step, alter, octave) -> absolute LilyPond pitch name"""
    s, a, o = p
    k = o - 3
    return s.lower() + ACC[a] + ("'" * k if k > 0 else ',' * (-k))


def from_midi_spelled(m, tones):
    """spell midi number m with the (step, alter) of a chord tone of the same pitch class"""
    for st, al in tones:
        if (STEP_PC[st] + al) % 12 == m % 12:
            o = (m - STEP_PC[st] - al) // 12 - 1
            return (st, al, o)
    raise ValueError((m, tones))


def chord_cands(sym, lo=24, hi=96):
    tones, bass, q = chord_tones(sym)
    out = []
    for m in range(lo, hi + 1):
        for st, al in tones:
            if (STEP_PC[st] + al) % 12 == m % 12:
                out.append((m, from_midi_spelled(m, tones)))
    return tones, bass, out


def close_chord(sym, center, n=None, below=None):
    """close-position voicing (one of each chord tone) with mean nearest to center (midi);
    optionally all notes strictly below `below`."""
    tones, bass, cands = chord_cands(sym)
    k = n or len(tones)
    best = None
    for i in range(len(cands) - k + 1):
        win = cands[i:i + k]
        pcs = {m % 12 for m, _ in win}
        if len(pcs) != min(k, len(tones)):
            continue
        if below is not None and win[-1][0] >= below:
            continue
        sc = abs(sum(m for m, _ in win) / k - center)
        if best is None or sc < best[0]:
            best = (sc, [p for _, p in win])
    return best[1]


def bass_note(sym, lo, hi):
    """root (or slash bass) between midi lo..hi"""
    tones, bass, q = chord_tones(sym)
    for m in range(lo, hi + 1):
        if (STEP_PC[bass[0]] + bass[1]) % 12 == m % 12:
            o = (m - STEP_PC[bass[0]] - bass[1]) // 12 - 1
            return (bass[0], bass[1], o)
    raise ValueError(sym)


def chord_ly(ps):
    if len(ps) == 1:
        return lyp(ps[0])
    return '<' + ' '.join(lyp(p) for p in ps) + '>'


def mk_part(pid, name, abbr='', instrument='voice', staves=1, clefs=('treble',), voices=(('1', 1),)):
    p = Part(id=pid, name=name, abbr=abbr, instrument=instrument, staves=staves, clefs=list(clefs))
    p.voices = [VoiceDef(k, s) for k, s in voices]
    return p


def assemble(time, key, parts_voices, time_symbol=None, nominal_override=None):
    """parts_voices: list of (Part, {vkey: dsl text}).  Builds MeasureInfo from the longest voice per
    measure.  Returns Score."""
    parsed = []
    nm = None
    for part, vd in parts_voices:
        pv = {}
        for k, txt in vd.items():
            ms = parse_voice(txt, time)
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
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        sc.measures.append(mi)
    for part, pv in parsed:
        part.measures = [{k: pv[k][i] for k in pv} for i in range(nm)]
        sc.parts.append(part)
    renumber(sc)
    return sc


def set_time(sc, i, time, time_symbol=None):
    """time signature change at measure index i (call before durations are re-derived)"""
    sc.measures[i].time = time
    sc.measures[i].time_symbol = time_symbol
    nominal = F(time[0] * 4, time[1])
    for j in range(i, len(sc.measures)):
        if j > i and sc.measures[j].time:
            break
        sc.measures[j].nominal = nominal


def add_mark(sc, i, kind, **kw):
    sc.measures[i].marks.append(dict(kind=kind, **kw))


def add_end_mark(sc, i, text, **kw):
    sc.measures[i].end_marks.append(dict(kind='words', text=text, **kw))


def staff_with_names(name, short=None):
    d = {'name': name}
    if short:
        d['short'] = short
    return d


REMOVE_EMPTY = ['\\RemoveAllEmptyStaves']
