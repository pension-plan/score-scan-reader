"""Engraving decisions made explicit in the model so that truth and engraving agree exactly.

* beaming: every beam group is decided here (manual '[' ']' in the DSL win; otherwise notes
  shorter than a quarter are grouped per beat).  The LilyPond writer runs with \\autoBeamOff and
  writes the manual beams; the truth gets <beam number="n"> begin/continue/end/forward hook/
  backward hook for every level.
* stems: every stemmed note (half and shorter) gets an explicit direction.  Single-voice staves:
  the note (or chord / beam group) farthest from the middle line decides (above -> down, below ->
  up, tie -> down).  Two voices on a staff: voice 1/3 up, voice 2/4 down.  LilyPond receives
  \\stemUp / \\stemDown before every change; the truth gets <stem> on every stemmed note.
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import STEPS, Score, staff_roles

BEAMS = {'eighth': 1, '16th': 2, '32nd': 3, '64th': 4}
# middle-line reference (step index, octave) and octave shift per clef
CLEF_MID = {'treble': ('B', 4), 'treble_8': ('B', 3), 'treble^8': ('B', 5), 'bass': ('D', 3),
            'bass_8': ('D', 2), 'alto': ('C', 4), 'tenor': ('A', 3), 'soprano': ('G', 4)}


def diatonic(step, octave):
    return octave * 7 + STEPS.index(step)


def staff_pos(pitch, clef):
    """steps above the middle staff line (0 = middle line, +4 top line, -4 bottom line)"""
    ms, mo = CLEF_MID[clef]
    return diatonic(pitch[0], pitch[2]) - diatonic(ms, mo)


def beat_len(time):
    n, d = time
    if d == 8 and n % 3 == 0 and n > 3:
        return F(3, 2)
    if d == 8:
        return F(1, 2) * 1          # 5/8, 7/8, 3/8: per eighth -> handled by explicit beams in the DSL
    if d == 2:
        return F(2)
    return F(4, d)


def _clef_track(score: Score):
    """clef in force per (part id, staff) at each measure start; clef events are applied in order."""
    out = {}
    for p in score.parts:
        cur = {s + 1: p.clefs[s] for s in range(p.staves)}
        for i, m in enumerate(p.measures):
            out[(p.id, i)] = dict(cur)
            for v in p.voices:
                for ev in m.get(v.key, []):
                    if ev.kind == 'clef':
                        cur[v.staff] = ev.clef
    return out


def auto_beam(score: Score):
    """group short notes per beat where the DSL gave no manual beams for that voice-measure"""
    for i, mi in enumerate(score.measures):
        (tn, td), _ = score.current_time(i)
        bl = beat_len((tn, td))
        for p in score.parts:
            for v in p.voices:
                evs = p.measures[i].get(v.key, [])
                if any(e.beam for e in evs):
                    continue
                pos = F(0)
                if i == 0 and mi.implicit:
                    pos = mi.nominal - mi.dur
                groups, cur, cur_beat = [], [], None
                for e in evs:
                    if e.kind == 'clef':
                        continue
                    beat = pos // bl
                    end_beat = (pos + e.dur - F(1, 10000)) // bl
                    beamable = e.kind == 'note' and e.dtype in BEAMS and not e.cue and beat == end_beat
                    if beamable and cur and beat == cur_beat:
                        cur.append(e)
                    else:
                        if len(cur) >= 2:
                            groups.append(cur)
                        cur = [e] if beamable else []
                        cur_beat = beat if beamable else None
                    pos += e.dur
                if len(cur) >= 2:
                    groups.append(cur)
                for g in groups:
                    g[0].beam = '['
                    g[-1].beam = ']'


def beam_groups(score: Score):
    """list of note-event lists (in order) per voice from the '[' / ']' marks"""
    out = []
    for p in score.parts:
        for v in p.voices:
            cur = None
            for m in p.measures:
                for e in m.get(v.key, []):
                    if e.kind not in ('note', 'rest', 'space'):
                        continue
                    if e.beam == '[':
                        if cur is not None:
                            raise ValueError(f'nested beam in {p.id}:{v.key}')
                        cur = [e]
                        continue
                    if cur is not None:
                        if e.kind != 'note':
                            raise ValueError(f'rest/space inside beam in {p.id}:{v.key}')
                        cur.append(e)
                        if e.beam == ']':
                            out.append(cur)
                            cur = None
            if cur is not None:
                raise ValueError(f'unterminated beam in {p.id}:{v.key}')
    return out


def assign_beam_values(score: Score):
    """ev.beams = [(level, value)] for MusicXML <beam number=level>value</beam>"""
    for p in score.parts:
        for m in p.measures:
            for evs in m.values():
                for e in evs:
                    e.beams = []
    for g in beam_groups(score):
        n = len(g)
        levels = [BEAMS[e.dtype] for e in g]
        for e in g:
            if e.dtype not in BEAMS:
                raise ValueError(f'unbeamable {e.dtype} in a beam group')
        for lev in range(1, max(levels) + 1):
            k = 0
            while k < n:
                if levels[k] < lev:
                    k += 1
                    continue
                j = k
                while j + 1 < n and levels[j + 1] >= lev:
                    j += 1
                if j > k:
                    g[k].beams.append((lev, 'begin'))
                    for x in range(k + 1, j):
                        g[x].beams.append((lev, 'continue'))
                    g[j].beams.append((lev, 'end'))
                else:
                    if k == 0:
                        g[k].beams.append((lev, 'forward hook'))
                    elif k == n - 1:
                        g[k].beams.append((lev, 'backward hook'))
                    else:
                        raise ValueError('beamlet in the middle of a group: direction ambiguous, avoid')
                k = j + 1


def _dir_from_positions(posl):
    hi, lo = max(posl), min(posl)
    if hi + lo > 0:
        return 'down'
    if hi + lo < 0:
        return 'up'
    return 'down'


def assign_stems(score: Score):
    clefs = _clef_track(score)
    groups = beam_groups(score)
    in_group = {}
    for gi, g in enumerate(groups):
        for e in g:
            in_group[id(e)] = gi
    # positions per event (needs the clef of the event's printed staff)
    pos_of = {}
    role_of = {}
    for p in score.parts:
        for i, m in enumerate(p.measures):
            cl = dict(clefs[(p.id, i)])
            for s in range(1, p.staves + 1):
                vk = [(v.key, m.get(v.key, [])) for v in p.voices if v.staff == s]
                r = staff_roles(vk)
                for k, evs in vk:
                    for e in evs:
                        role_of[id(e)] = r.get(k, 0)
            for v in p.voices:
                c = dict(cl)
                for e in m.get(v.key, []):
                    if e.kind == 'clef':
                        c[v.staff] = e.clef
                        continue
                    if e.kind == 'note':
                        st = e.staff or v.staff
                        pos_of[id(e)] = [staff_pos(pt, c[st]) for pt in e.pitches]
    group_dir = {}
    for gi, g in enumerate(groups):
        roles = {role_of.get(id(e), 0) for e in g}
        if roles & {1, 3}:
            group_dir[gi] = 'up'
        elif roles & {2, 4}:
            group_dir[gi] = 'down'
        else:
            allp = [x for e in g for x in pos_of[id(e)]]
            group_dir[gi] = _dir_from_positions(allp)
    for p in score.parts:
        for m in p.measures:
            for evs in m.values():
                for e in evs:
                    if e.kind != 'note' or e.dtype in ('whole', 'breve'):
                        if e.kind == 'note':
                            e.stem = None
                        continue
                    if e.stem is not None:
                        continue
                    if id(e) in in_group:
                        e.stem = group_dir[in_group[id(e)]]
                        continue
                    r = role_of.get(id(e), 0)
                    if r in (1, 3):
                        e.stem = 'up'
                    elif r in (2, 4):
                        e.stem = 'down'
                    else:
                        e.stem = _dir_from_positions(pos_of[id(e)])


def prepare(score: Score):
    auto_beam(score)
    assign_beam_values(score)
    assign_stems(score)
