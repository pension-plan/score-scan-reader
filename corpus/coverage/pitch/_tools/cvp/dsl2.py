"""Extended LilyPond-like note DSL (absolute pitch) for the pitch challenge items.

Tokens (whitespace separated, '|' ends a measure):
  pitch   [a-g](isis|eses|is|es)?[',]*  optionally followed by ! (forced accidental)
          or ? (parenthesised cautionary accidental), then duration 1 2 4 8 16 32 (sticky)
          and dots, then suffixes ~ ( ) -. -> \\fermata \\p ...
  r       rest;   <c' e'>4  chord
  \\clef=NAME        clef change (treble bass alto tenor treble_8 ...) at this point
  \\ottava=N         N = 1 (8va), -1 (8vb), 2 (15ma), 0 (end)
  score-level (put them in one voice, at the start of a measure unless noted):
  \\key=F[:minor]    key signature with F fifths from this measure on
  \\bar=||  \\bar=|.  right barline of the *current* measure (anywhere inside it)
  \\break  \\pagebreak  explicit line/page break before this measure
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, MeasureInfo, Part, Score, VoiceDef, display_ql, renumber

DUR_TYPE = {'1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th', '32': '32nd'}
PITCH_RE = r"[a-g](?:isis|eses|is|es)?[',]*[!?]?"
TOK = re.compile(r"^(?P<p>(?:<[^>]+>)|" + PITCH_RE + r"|r)(?P<d>1|2|4|8|16|32)?(?P<dots>\.*)(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es)?(?P<o>[',]*)(?P<m>[!?]?)$")
ACC = {None: 0, 'is': 1, 'es': -1, 'isis': 2, 'eses': -2}
BARS = {'||': 'double', '|.': 'final'}


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(f'bad pitch {t!r}')
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    return (m.group('s').upper(), ACC[m.group('a')], octv), m.group('m')


def parse_voice(text):
    """-> (measures: list[list[Event]], directives: dict measure_idx -> dict)"""
    measures, cur = [], []
    directives = {}
    last_d, last_dots = '4', 0
    toks = []
    for raw in text.split():
        if raw.startswith('\\bar='):
            toks.append(raw)
            continue
        parts = raw.split('|')
        for j, x in enumerate(parts):
            if x:
                toks.append(x)
            if j < len(parts) - 1:
                toks.append('|')
    for tk in toks:
        if tk == '|':
            measures.append(cur)
            cur = []
            continue
        mi = len(measures)
        if tk.startswith('\\clef='):
            cur.append(Event('clef', F(0), clef=tk.split('=', 1)[1]))
            continue
        if tk.startswith('\\ottava='):
            cur.append(Event('ottava', F(0), ottava=int(tk.split('=', 1)[1])))
            continue
        if tk.startswith('\\key='):
            v = tk.split('=', 1)[1]
            f, _, mode = v.partition(':')
            directives.setdefault(mi, {})['key'] = (int(f), mode or 'major')
            continue
        if tk.startswith('\\bar='):
            directives.setdefault(mi, {})['bar'] = BARS[tk.split('=', 1)[1]]
            continue
        if tk in ('\\break', '\\pagebreak'):
            directives.setdefault(mi, {})['brk'] = 'line' if tk == '\\break' else 'page'
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
        if p != 'r':
            items = p[1:-1].split() if p.startswith('<') else [p]
            for x in items:
                pit, mark = parse_pitch(x)
                ev.pitches.append(pit)
                if mark == '!':
                    ev.force_acc.add(pit)
                elif mark == '?':
                    ev.caut_acc.add(pit)
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
        if '--' in suf:
            ev.artic.append('tenuto')
        for dyn in re.findall(r'\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf)(?![a-z])', suf):
            ev.dynamics.append(dyn)
        cur.append(ev)
    if cur:
        measures.append(cur)
    # ties: mark stops (across zero-length clef/ottava events)
    prev = None
    for mm in measures:
        for ev in mm:
            if ev.kind in ('clef', 'ottava'):
                continue
            if ev.kind != 'note':
                prev = None
                continue
            if prev is not None and prev.tie_start:
                ev.tie_stop = {p for p in ev.pitches if p in prev.tie_start}
                missing = prev.tie_start - set(ev.pitches)
                if missing:
                    raise ValueError(f'tie to a different pitch: {missing} -> {ev.pitches}')
            prev = ev
    return measures, directives


def build(parts, time=(4, 4), key=(0, 'major'), time_symbol=None):
    """parts: list of dicts {id, name, abbr, clef, music, instrument}; every part one voice '1'.
    Returns Score; directives (key/bar/brk) merged across parts."""
    parsed = []
    dirs = {}
    for spec in parts:
        meas, d = parse_voice(spec['music'])
        parsed.append(meas)
        for mi, dd in d.items():
            for k, v in dd.items():
                if mi in dirs and k in dirs[mi] and dirs[mi][k] != v:
                    raise ValueError(f'conflicting directive {k} in measure {mi}')
                dirs.setdefault(mi, {})[k] = v
    nm = len(parsed[0])
    for spec, meas in zip(parts, parsed):
        if len(meas) != nm:
            raise ValueError(f"part {spec['id']}: {len(meas)} measures, expected {nm}")
    nominal = F(time[0] * 4, time[1])
    sc = Score()
    for i in range(nm):
        durs = [sum((e.dur for e in meas[i]), F(0)) for meas in parsed]
        dur = max(durs)
        if any(d_ != dur for d_ in durs):
            raise ValueError(f'measure {i + 1}: part durations differ {durs}')
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        elif dur != nominal and i != nm - 1:
            raise ValueError(f'measure {i + 1} has duration {dur}, expected {nominal}')
        d = dirs.get(i, {})
        if 'key' in d:
            mi.key = d['key']
        if 'bar' in d:
            mi.right_bar = d['bar']
        if 'brk' in d:
            mi.brk = d['brk']
        sc.measures.append(mi)
    if not sc.measures[-1].right_bar:
        sc.measures[-1].right_bar = 'final'
    for spec, meas in zip(parts, parsed):
        p = Part(id=spec['id'], name=spec.get('name', ''), abbr=spec.get('abbr', ''),
                 instrument=spec.get('instrument', 'voice'), clefs=[spec.get('clef', 'treble')])
        p.voices = [VoiceDef('1', 1)]
        for i in range(nm):
            p.measures.append({'1': meas[i]})
        sc.parts.append(p)
    renumber(sc)
    return sc
