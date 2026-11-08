"""LilyPond-like note DSL for self-authored pieces (absolute pitch), extended for
the layout-challenge corpus.

  "g'4 a'8[ b'] c''4^"dolce" d''\\fermata | <c' e'>2\\p\\< r4 e'4\\! | R1 | s2 g'2"

Measures are separated by '|'.  Tokens:
  pitch [a-g](is|es)*[',]*  | r (rest) | s (spacer, no truth rest) | R (full-measure rest)
  duration 1 2 4 8 16 32 (sticky) + dots;  <c' e' g'>4 chords
  suffixes:  ~ tie   ( ) slur   [ ] manual beam   -. -> -- articulations   \\fermata
             \\p \\mf ... dynamics   \\< \\> \\! hairpins   \\sustainOn \\sustainOff pedal
             ^"text" / _"text" italic words above/below ('_' inside quotes = space),
             ^!"text" bold words
  standalone: \\cueOn \\cueOff (cue-size notes)   \\st1 \\st2 \\st3 (cross-staff), \\st0 (home staff)
              \\tup3/2 ... \\tupend (tuplet)      \\clef=bass (clef change)
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, MeasureInfo, Part, Score, VoiceDef, display_ql, renumber

DUR_TYPE = {'1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th', '32': '32nd'}
TOK = re.compile(r"^(?P<p>(?:<[^>]+>)|[a-g](?:isis|eses|is|es|s)?[',]*|r|s|R)(?P<d>16|32|1|2|4|8)?(?P<dots>\.*)(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es|s)?(?P<o>[',]*)$")
ACC = {None: 0, 'is': 1, 'es': -1, 's': -1, 'isis': 2, 'eses': -2}
WORDS = re.compile(r'([\^_])(!?)"([^"]*)"')
DYN = re.compile(r'\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf|fp)(?![a-zA-Z])')


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(t)
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    return (m.group('s').upper(), ACC[m.group('a')], octv)


def parse_voice(text, time=(4, 4)):
    measures = []
    cur = []
    last_d, last_dots = '4', 0
    cue = False
    staff = None
    tup = None
    tup_events = []
    text = text.replace('|', ' | ')
    # keep chords <c' e' g'> together (a '<' preceded by a backslash is a hairpin)
    text = re.sub(r'(?<!\\)<([^<>\\]*)>', lambda m: '<' + m.group(1).strip().replace(' ', '\u00a7') + '>', text)
    toks = text.split()
    for tk in toks:
        if tk == '|':
            measures.append(cur)
            cur = []
            continue
        if tk == '\\partial':
            continue
        if tk == '\\cueOn':
            cue = True
            continue
        if tk == '\\cueOff':
            cue = False
            continue
        if re.fullmatch(r'\\st[0-3]', tk):
            n = int(tk[3])
            staff = n or None
            continue
        m = re.fullmatch(r'\\tup(\d+)/(\d+)', tk)
        if m:
            tup = (int(m.group(1)), int(m.group(2)))
            tup_events = []
            continue
        if tk == '\\tupend':
            if tup_events:
                tup_events[0].tuplet_start = True
                tup_events[-1].tuplet_stop = True
            tup = None
            continue
        m = re.fullmatch(r'\\clef=(\S+)', tk)
        if m:
            cur.append(Event('clef', F(0), clef=m.group(1)))
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
        dur = display_ql(dtype, nd)
        if tup:
            dur = dur * tup[1] / tup[0]
        kind = {'r': 'rest', 's': 'space', 'R': 'rest'}.get(p, 'note')
        ev = Event(kind, dur, dtype=dtype if kind != 'space' else None, dots=nd if kind != 'space' else 0)
        if p == 'R':
            ev.measure_rest = True
        if tup and kind != 'space':
            ev.tuplet = tup
            tup_events.append(ev)
        if p.startswith('<'):
            ev.pitches = [parse_pitch(x) for x in p[1:-1].split('\u00a7') if x]
        elif kind == 'note':
            ev.pitches = [parse_pitch(p)]
        ev.cue = cue and kind == 'note'
        ev.staff = staff
        # words first (they may contain characters used by other suffixes)
        for side, bold, txt in WORDS.findall(suf):
            ev.words.append((txt.replace('_', ' '), 'above' if side == '^' else 'below', 'bold' if bold else 'italic'))
        suf = WORDS.sub('', suf)
        if '\\fermata' in suf:
            ev.fermata = True
            suf = suf.replace('\\fermata', '')
        for k in re.findall(r'\\sustain(On|Off)', suf):
            ev.pedal.append('start' if k == 'On' else 'stop')
        suf = re.sub(r'\\sustain(On|Off)', '', suf)
        for k in re.findall(r'\\([<>!])', suf):
            ev.wedge.append({'<': 'crescendo', '>': 'diminuendo', '!': 'stop'}[k])
        suf = re.sub(r'\\[<>!]', '', suf)
        for dyn in DYN.findall(suf):
            ev.dynamics.append(dyn)
        suf = DYN.sub('', suf)
        if '~' in suf:
            ev.tie_start = set(ev.pitches)
        if '(' in suf:
            ev.slur_start = 1
        if ')' in suf:
            ev.slur_stop = 1
        if '-.' in suf:
            ev.artic.append('staccato')
        if '->' in suf:
            ev.artic.append('accent')
        if '--' in suf:
            ev.artic.append('tenuto')
        if '[' in suf:
            ev.beam = '['
        if ']' in suf:
            ev.beam = ']'
        rest = re.sub(r'-\.|->|--|[~()\[\]]', '', suf)
        if rest.strip():
            raise ValueError(f'unparsed suffix {rest!r} in token {tk!r}')
        cur.append(ev)
    if cur:
        measures.append(cur)
    # ties: mark stops
    prev = None
    for mm in measures:
        for ev in mm:
            if ev.kind == 'clef':
                continue
            if ev.kind != 'note':
                prev = None
                continue
            if prev is not None and prev.tie_start:
                ev.tie_stop = {p for p in ev.pitches if p in prev.tie_start}
            prev = ev
    return measures


def mdur(evs):
    return sum((e.dur for e in evs), F(0))


def build_score(voices, time=(4, 4), key=(0, 'major'), time_symbol=None, parts=None):
    """voices: dict name -> dsl text.  parts: list of dicts {id,name,abbr,clef,voice}
    Returns Score where each part has one voice ('1')."""
    parsed = {k: parse_voice(v, time) for k, v in voices.items()}
    lens = {k: len(v) for k, v in parsed.items()}
    nm = max(lens.values())
    assert all(l == nm for l in lens.values()), lens
    nominal = F(time[0] * 4, time[1])
    sc = Score()
    for i in range(nm):
        dur = max(mdur(parsed[k][i]) for k in parsed)
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
