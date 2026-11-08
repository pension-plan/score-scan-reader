"""Tiny LilyPond-like note DSL for self-authored pieces (absolute pitch).

  voice = "\\partial g'4 | g'2 fis'4 e' | d'2.\\fermata r4 | ..."
tokens: pitch [a-g](is|es)*[',]* or r (rest); duration 1 2 4 8 16 (sticky) +
dots; suffixes ~ (tie)  \\fermata  ( )  -. ->  \\p \\f ...
'|' separates measures (checked against the time signature; first measure
may be a pickup, last may be short).  <c' e'>4 chords are supported.
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, MeasureInfo, Part, Score, VoiceDef, display_ql, renumber

DUR_TYPE = {'1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th', '32': '32nd'}
TOK = re.compile(r"^(?P<p>(?:<[^>]+>)|[a-g](?:isis|eses|is|es|s)?[',]*|r)(?P<d>16|32|1|2|4|8)?(?P<dots>\.*)(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es|s)?(?P<o>[',]*)$")
ACC = {None: 0, 'is': 1, 'es': -1, 's': -1, 'isis': 2, 'eses': -2}


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(t)
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    return (m.group('s').upper(), ACC[m.group('a')], octv)


def parse_voice(text, time=(4, 4)):
    nominal = F(time[0] * 4, time[1])
    measures = []
    cur = []
    last_d, last_dots = '4', 0
    pending_tie = None
    text = text.replace('|', ' | ')
    text = re.sub(r'<([^>]+)>', lambda m: '<' + '_'.join(m.group(1).split()) + '>', text)
    toks = text.split()
    for tk in toks:
        if tk == '|':
            measures.append(cur)
            cur = []
            continue
        if tk == '\\partial':
            continue
        m = TOK.match(tk)
        if not m:
            raise ValueError(f'bad token {tk!r}')
        p, d, dots, suf = m.group('p'), m.group('d'), m.group('dots'), m.group('suf')
        if d:
            last_d, last_dots = d, len(dots)
        elif dots:
            last_dots = len(dots)
        dtype = DUR_TYPE[last_d]
        nd = last_dots
        ev = Event('rest' if p == 'r' else 'note', display_ql(dtype, nd), dtype=dtype, dots=nd)
        if p.startswith('<'):
            ev.pitches = [parse_pitch(x) for x in p[1:-1].split('_')]
        elif p != 'r':
            ev.pitches = [parse_pitch(p)]
        if '~' in suf:
            ev.tie_start = set(ev.pitches)
        if '\\fermata' in suf:
            ev.fermata = True
        if '(' in suf:
            ev.slur_start = 1
        if ')' in suf:
            ev.slur_stop = 1
        if '-.' in suf:
            ev.artic.append('staccato')
        if '->' in suf:
            ev.artic.append('accent')
        for dyn in re.findall(r'\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf)(?![a-z])', suf):
            ev.dynamics.append(dyn)
        cur.append(ev)
    if cur:
        measures.append(cur)
    # ties: mark stops
    prev = None
    for mm in measures:
        for ev in mm:
            if ev.kind != 'note':
                prev = None
                continue
            if prev is not None and prev.tie_start:
                ev.tie_stop = {p for p in ev.pitches if p in prev.tie_start}
            prev = ev
    return measures


def build_score(voices, time=(4, 4), key=(0, 'major'), time_symbol=None, parts=None):
    """voices: dict name -> dsl text.  parts: list of dicts {id,name,abbr,clef,voice}
    Returns Score where each part has one voice ('1')."""
    parsed = {k: parse_voice(v, time) for k, v in voices.items()}
    lens = {k: len(v) for k, v in parsed.items()}
    nm = max(lens.values())
    assert all(l == nm for l in lens.values()), lens
    nominal = F(time[0] * 4, time[1])
    sc = Score()
    first = next(iter(parsed.values()))
    for i in range(nm):
        dur = max(sum((e.dur for e in parsed[k][i]), F(0)) for k in parsed)
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        elif dur != nominal and i != nm - 1:
            raise ValueError(f'measure {i} has duration {dur}')
        sc.measures.append(mi)
    sc.measures[-1].right_bar = 'final'
    for spec in parts:
        p = Part(id=spec['id'], name=spec.get('name', ''), abbr=spec.get('abbr', ''),
                 instrument=spec.get('instrument', 'voice'), clefs=[spec.get('clef', 'treble')])
        p.voices = [VoiceDef('1', 1)]
        for i in range(nm):
            p.measures.append({'1': parsed[spec['voice']][i]})
        sc.parts.append(p)
    renumber(sc)
    return sc
