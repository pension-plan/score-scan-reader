"""(copied from corpus/synthetic/_tools/synth/harmonize.py; voice ranges made configurable)
Small SATB voice-leading solver for self-authored hymn harmonisations.

Given a soprano line and one chord symbol per soprano attack, choose alto,
tenor and bass notes (homophonic rhythm) by dynamic programming, penalising
parallel fifths/octaves, large leaps, poor doubling and bad spacing.
Chord symbols: G  Em  D/F#  D7  Am7  Bdim  C/E ; '~' = hold previous chord
(lower voices tie), '-' = same chord re-struck.
"""
from __future__ import annotations

import copy
import itertools
import re

from .model import STEP_PC, STEPS, midi

CH = re.compile(r'^(?P<r>[A-G])(?P<ra>#|b)?(?P<q>m7|maj7|m|dim|7|sus4)?(?:/(?P<b>[A-G])(?P<ba>#|b)?)?$')


def _spell(root, semis, letters):
    rs, ra = root
    step = STEPS[(STEPS.index(rs) + letters) % 7]
    nat = (STEP_PC[step] - STEP_PC[rs]) % 12
    alter = (semis - nat + ra + 6) % 12 - 6
    return (step, alter)


def chord_tones(sym):
    m = CH.match(sym)
    if not m:
        raise ValueError(sym)
    root = (m.group('r'), {'#': 1, 'b': -1, None: 0}[m.group('ra')])
    q = m.group('q') or ''
    third = 3 if q in ('m', 'm7', 'dim') else 4
    if q == 'sus4':
        third = 5
    fifth = 6 if q == 'dim' else 7
    tones = [root, _spell(root, third, 3 if q == 'sus4' else 2), _spell(root, fifth, 4)]
    if q in ('7', 'm7'):
        tones.append(_spell(root, 10, 6))
    if q == 'maj7':
        tones.append(_spell(root, 11, 6))
    bass = root
    if m.group('b'):
        bass = (m.group('b'), {'#': 1, 'b': -1, None: 0}[m.group('ba')])
    return tones, bass, q


def pc(t):
    return (STEP_PC[t[0]] + t[1]) % 12


RANGES = {'B': (40, 62), 'T': (48, 69), 'A': (55, 74)}


def candidates(tones, bass, sop, quality, lead_pc, ranges=None):
    R = dict(RANGES, **(ranges or {}))
    tpcs = [pc(t) for t in tones]
    by_pc = {pc(t): t for t in tones}
    s_m = midi(sop)
    out = []
    def pitches_in(t, lo, hi):
        res = []
        for o in range(1, 7):
            p = (t[0], t[1], o)
            if lo <= midi(p) <= hi:
                res.append(p)
        return res
    B = pitches_in(bass, *R['B'])
    T_all = [p for t in tones for p in pitches_in(t, *R['T'])]
    A_all = [p for t in tones for p in pitches_in(t, *R['A'])]
    for b in B:
        for t in T_all:
            if not (midi(b) <= midi(t) and midi(t) - midi(b) <= 19):
                continue
            for a in A_all:
                if not (midi(t) <= midi(a) <= s_m and s_m - midi(a) <= 12 and midi(a) - midi(t) <= 12):
                    continue
                pcs = [pc(x) for x in (b, t, a)] + [pc(sop)]
                need = {tpcs[0], tpcs[1]}
                if len(tones) == 4:
                    need.add(tpcs[3])
                if not need <= set(pcs):
                    continue
                cost = 0
                if tpcs[2] not in pcs:
                    cost += 1.5
                cnt = {x: pcs.count(x) for x in set(pcs)}
                if cnt.get(tpcs[1], 0) > 1 and quality in ('',):
                    cost += 2.5
                if cnt.get(lead_pc, 0) > 1:
                    cost += 8
                if len(tones) == 4 and cnt.get(tpcs[3], 0) > 1:
                    cost += 8
                if midi(a) == s_m:
                    cost += 3
                if midi(t) == midi(a):
                    cost += 2
                # prefer close-ish spacing centred voices
                cost += abs(midi(a) - (sum(R['A']) / 2)) * 0.05 + abs(midi(t) - (sum(R['T']) / 2)) * 0.05
                out.append(((b, t, a), cost))
    return out


def _parallel(p1, p2, q1, q2):
    """voices p (lower) and q (upper): p1->p2, q1->q2 (midi)."""
    if p1 == p2 and q1 == q2:
        return False
    i1, i2 = (q1 - p1) % 12, (q2 - p2) % 12
    if i1 == i2 and i1 in (0, 7) and (p1 != p2) and (q1 != q2):
        return True
    return False


def transition(v1, s1, v2, s2):
    b1, t1, a1 = (midi(x) for x in v1)
    b2, t2, a2 = (midi(x) for x in v2)
    S1, S2 = midi(s1), midi(s2)
    cost = 0.0
    for x1, x2, w in ((a1, a2, 1.0), (t1, t2, 1.0)):
        d = abs(x2 - x1)
        cost += d * 0.35 * w
        if d > 4:
            cost += (d - 4) * 0.8
        if d > 7:
            cost += 6
    db = abs(b2 - b1)
    cost += db * 0.1
    if db > 7:
        cost += 2
    if db > 12:
        cost += 10
    V1 = [b1, t1, a1, S1]
    V2 = [b2, t2, a2, S2]
    for i in range(4):
        for j in range(i + 1, 4):
            if _parallel(V1[i], V2[i], V1[j], V2[j]):
                cost += 60
    # hidden octaves/fifths in outer voices with soprano leap
    if (b2 - b1) * (S2 - S1) > 0 and (S2 - b2) % 12 in (0, 7) and abs(S2 - S1) > 2:
        cost += 3
    # overlap
    if t2 > a1 or a2 > S1 or b2 > t1 or t2 < b1 or a2 < t1:
        cost += 3
    # contrary motion bonus outer voices
    if (b2 - b1) * (S2 - S1) < 0:
        cost -= 0.5
    return cost


def harmonize(sop_measures, chords, tonic_pc, ranges=None):
    """sop_measures: list of measures (list of Events) for soprano.
    chords: list of chord symbols, one per soprano note event (including tie
    continuations, use '~').  Returns (alto, tenor, bass) measure lists."""
    lead_pc = (tonic_pc - 1) % 12
    sev = [(mi, k, ev) for mi, mm in enumerate(sop_measures) for k, ev in enumerate(mm) if ev.kind == 'note']
    if len(chords) != len(sev):
        raise ValueError(f'{len(chords)} chords for {len(sev)} soprano notes')
    steps = []   # list of (index into sev, candidates or None for hold)
    prev_sym = None
    for (mi, k, ev), sym in zip(sev, chords):
        if sym == '~' or ev.is_tie_continuation():
            steps.append(None)
            continue
        if sym == '-':
            sym = prev_sym
        tones, bass, q = chord_tones(sym)
        cands = candidates(tones, bass, ev.pitches[0], q, lead_pc, ranges)
        if not cands:
            raise ValueError(f'no voicing for {sym} under {ev.pitches[0]}')
        steps.append(cands)
        prev_sym = sym
    # DP over non-hold steps
    idx = [i for i, st in enumerate(steps) if st is not None]
    best = [dict() for _ in idx]
    for j, i in enumerate(idx):
        s_pitch = sev[i][2].pitches[0]
        for vi, (v, c) in enumerate(steps[i]):
            if j == 0:
                best[j][vi] = (c + (0 if midi(v[0]) % 12 == tonic_pc else 0), None)
                continue
            ip = idx[j - 1]
            sp = sev[ip][2].pitches[0]
            bc, bp = None, None
            for pvi, (pv, pc_) in enumerate(steps[ip]):
                if pvi not in best[j - 1]:
                    continue
                tot = best[j - 1][pvi][0] + transition(pv, sp, v, s_pitch) + c
                if bc is None or tot < bc:
                    bc, bp = tot, pvi
            best[j][vi] = (bc, bp)
    # backtrack
    j = len(idx) - 1
    vi = min(best[j], key=lambda k: best[j][k][0])
    choice = {}
    while j >= 0:
        choice[idx[j]] = steps[idx[j]][vi][0]
        vi = best[j][vi][1]
        j -= 1
    # build voices
    outs = ([], [], [])
    cur = None
    flat = []
    for i in range(len(sev)):
        if i in choice:
            cur = choice[i]
            flat.append((cur, False))
        else:
            flat.append((cur, True))
    fi = 0
    for mi, mm in enumerate(sop_measures):
        newm = ([], [], [])
        for ev in mm:
            for vn in range(3):
                e2 = copy.deepcopy(ev)
                e2.lyrics = {}
                e2.dynamics = []
                if ev.kind == 'note':
                    v, hold = flat[fi]
                    p = v[2 - vn]   # alto=index2, tenor=1, bass=0
                    e2.pitches = [p]
                    e2.tie_start = set()
                    e2.tie_stop = {p} if hold else set()
                newm[vn].append(e2)
            if ev.kind == 'note':
                fi += 1
        for vn in range(3):
            outs[vn].append(newm[vn])
    # set tie_start where next is hold
    for vn in range(3):
        evs = [e for mm in outs[vn] for e in mm]
        for a, b in zip(evs, evs[1:]):
            if b.kind == 'note' and b.tie_stop and a.kind == 'note':
                a.tie_start = set(b.pitches)
                b.tie_stop = set(b.pitches)
    return outs
