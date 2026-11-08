"""Dev aid: voice-leading report for hand-written DSL voices (parallel
fifths/octaves between moving voice pairs, ranges, crossings, unisons,
vertical sonorities).  usage: report({'S': dsl, 'A': dsl, ...}, order=['S','A','T','B'])"""
from __future__ import annotations

from fractions import Fraction as F

from .dsl import parse_voice
from .model import midi

NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def timeline(dsl):
    t = F(0)
    out = []   # (start, end, midis or None)
    for mm in parse_voice(dsl):
        for ev in mm:
            out.append((t, t + ev.dur, [midi(p) for p in ev.pitches] if ev.kind == 'note' else None,
                        ev.kind == 'note' and bool(ev.tie_stop)))
            t += ev.dur
    return out


def at(tl, t):
    for s, e, m, tie in tl:
        if s <= t < e:
            return (m, s == t and not tie)
    return (None, False)


def report(voices, order, ranges=None, verbose=False):
    tls = {k: timeline(v) for k, v in voices.items()}
    pts = sorted({s for tl in tls.values() for s, _, _, _ in tl})
    issues = []
    prev = None
    for t in pts:
        cur = {}
        for k in order:
            m, att = at(tls[k], t)
            cur[k] = (m[0] if m and len(m) == 1 else (max(m) if m else None), att)
        if verbose:
            print(float(t), ' '.join(f'{k}:{NAMES[c[0] % 12] + str(c[0] // 12 - 1) if c[0] else "-":5s}' for k, c in cur.items()))
        if prev:
            for i, a in enumerate(order):
                for b in order[i + 1:]:
                    a1, b1 = prev[a][0], prev[b][0]
                    a2, b2 = cur[a][0], cur[b][0]
                    if None in (a1, b1, a2, b2):
                        continue
                    if a1 == a2 or b1 == b2:
                        continue
                    i1, i2 = abs(a1 - b1) % 12, abs(a2 - b2) % 12
                    if i1 == i2 and i1 in (0, 7) and (a2 - a1) * (b2 - b1) > 0:
                        kind = 'unison' if a1 == b1 and a2 == b2 else ('8ve' if i1 == 0 else '5th')
                        issues.append(f't={float(t)} parallel {kind} {a}-{b}')
        for i, a in enumerate(order):
            for b in order[i + 1:]:
                if cur[a][0] is not None and cur[b][0] is not None and cur[a][0] < cur[b][0]:
                    issues.append(f't={float(t)} crossing {a}<{b}')
        prev = cur
    if ranges:
        for k, (lo, hi) in ranges.items():
            ms = [x for s, e, m, _ in tls[k] if m for x in m]
            if ms and (min(ms) < lo or max(ms) > hi):
                issues.append(f'{k} range {min(ms)}-{max(ms)} outside {lo}-{hi}')
    return issues
