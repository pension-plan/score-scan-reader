"""Notation pre-pass for the coverage suite (layouts family).

Decides, from the score model + staff layout, every detail that the truth must state and the
engraving must print identically:

  * printed staff of every event (layout staff id; closed scores put two parts on one staff,
    cross-staff notes move to the other staff of their part)
  * beams: explicit beam groups (LilyPond gets \\autoBeamOff + [ ]), per level begin/continue/end and
    forward/backward hooks (truth <beam number="n">)
  * stems: an explicit direction for every stemmed note (LilyPond gets \\stemUp/\\stemDown,
    truth <stem>)
  * accidentals: LilyPond 2.24 'default' accidental style simulated per staff (state per
    (octave, step), reset at barlines, simultaneous notes judged against the state before the moment,
    tie continuations print nothing and do not update the state, except at the start of a system)
      - per PART staff  -> truth <accidental>
      - per PRINTED staff -> expected printed accidentals (checked against LilyPond's grob log)

Nothing here changes pitches or durations.
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import STEPS, Score, staff_roles

SHARP_ORDER = 'FCGDAEB'
ACC_NAME = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}
NBEAMS = {'eighth': 1, '16th': 2, '32nd': 3, '64th': 4}
STEMLESS = ('whole', 'breve')
# clef -> (reference step diatonic index on its line, line, octave change)
CLEF_DEF = {
    'treble': ('G', 2, 0), 'treble_8': ('G', 2, -1), 'treble^8': ('G', 2, 1),
    'bass': ('F', 4, 0), 'bass_8': ('F', 4, -1), 'varbaritone': ('F', 3, 0),
    'alto': ('C', 3, 0), 'tenor': ('C', 4, 0), 'soprano': ('C', 1, 0),
    'mezzosoprano': ('C', 2, 0), 'baritone': ('C', 5, 0),
}
SIGN_REF = {'G': 4 * 7 + 4, 'F': 3 * 7 + 3, 'C': 4 * 7 + 0}


def dia(p):
    return p[2] * 7 + STEPS.index(p[0])


def clef_mid(clef):
    """diatonic index of the (sounding) pitch on the middle staff line"""
    sign, line, oc = CLEF_DEF[clef]
    return SIGN_REF[sign] + (3 - line) * 2 + 7 * oc


def staff_pos(p, clef):
    return dia(p) - clef_mid(clef)


def key_alters(fifths):
    alt = {s: 0 for s in STEPS}
    if fifths > 0:
        for s in SHARP_ORDER[:fifths]:
            alt[s] = 1
    elif fifths < 0:
        for s in SHARP_ORDER[::-1][:-fifths]:
            alt[s] = -1
    return alt


# ------------------------------------------------------------------ layout helpers

def segments_of(score, layout):
    segs = layout.get('segments')
    if not segs:
        return [{'start': 0, 'end': len(score.measures), 'groups': layout['groups']}]
    return segs


def staff_tables(score, layout):
    """per segment: ids[(pid, part_staff)] -> staff id, order[staff id] -> vertical index,
    clef0[staff id] -> initial clef, home[(pid, vkey)] -> staff id"""
    out = []
    for seg in segments_of(score, layout):
        ids, order, clef0, voices = {}, {}, {}, {}
        k = 0
        for g in seg['groups']:
            for st in g['staves']:
                order[st['id']] = k
                k += 1
                clef0[st['id']] = st['clef']
                voices[st['id']] = [tuple(v) for v in st['voices']]
                for pid, vk in st['voices']:
                    sn = score.part(pid).voice(vk).staff
                    ids.setdefault((pid, sn), st['id'])
                if st.get('part_staff'):
                    ids[tuple(st['part_staff'])] = st['id']
        out.append({'start': seg['start'], 'end': seg['end'], 'ids': ids, 'order': order, 'clef0': clef0,
                    'voices': voices})
    return out


def seg_index(tables, i):
    for k, t in enumerate(tables):
        if t['start'] <= i < t['end']:
            return k
    raise IndexError(i)


def system_starts(score, layout):
    """measure indices that start a system (forced breaks + segment starts)"""
    s = {0}
    for seg in segments_of(score, layout):
        s.add(seg['start'])
    for i, m in enumerate(score.measures):
        if m.brk:
            s.add(i)
    return s


# ------------------------------------------------------------------ printed staff + clefs

def assign_printed_staves(score, tables):
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                t = tables[seg_index(tables, i)]
                for ev in m.get(v.key, []):
                    ev.printed_staff = t['ids'][(p.id, ev.staff or v.staff)]


def clef_timeline(score, tables):
    """printed staff id -> sorted list of (abs onset, order, clef); includes segment initial clefs"""
    offs = score.measure_offsets()
    tl = {}
    for t in tables:
        for sid, c in t['clef0'].items():
            tl.setdefault(sid, []).append((offs[t['start']], -1, c))
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                pos = offs[i]
                for k, ev in enumerate(m.get(v.key, [])):
                    if ev.kind == 'clef':
                        tl.setdefault(ev.printed_staff, []).append((pos, k, ev.clef))
                    pos += ev.dur
    for sid in tl:
        tl[sid].sort(key=lambda x: (x[0], x[1]))
    return tl


def clef_at(tl, sid, onset):
    cur = None
    for t, _, c in tl[sid]:
        if t <= onset:
            cur = c
        else:
            break
    return cur


# ------------------------------------------------------------------ beams

def beat_windows(time):
    """list of window lengths (quarters) for one bar"""
    n, d = time
    if d == 8 and n in (6, 9, 12):
        return [F(3, 2)] * (n // 3)
    if (n, d) == (5, 8):
        return [F(3, 2), F(1)]
    if (n, d) == (7, 8):
        return [F(1), F(1), F(3, 2)]
    if d == 8:
        return [F(1, 2)] * n
    unit = F(4, d)
    return [unit] * n


def window_index(wins, t, implicit_shift=F(0)):
    t = t + implicit_shift
    acc = F(0)
    for k, w in enumerate(wins):
        if t < acc + w:
            return k
        acc += w
    return len(wins) + int((t - acc) // wins[-1])


def beam_groups_auto(score, part, vkey, i, vocal):
    m = part.measures[i].get(vkey, [])
    mi = score.measures[i]
    (tn, td), _ = score.current_time(i)
    wins = beat_windows((tn, td))
    shift = mi.nominal - mi.dur if (i == 0 and mi.implicit) else F(0)
    groups, cur, cur_win = [], [], None
    t = F(0)
    tup_open = False
    for ev in m:
        if ev.kind == 'clef':
            continue
        beamable = ev.kind == 'note' and ev.dtype in NBEAMS
        w = window_index(wins, t, shift)
        brk = (not beamable or w != cur_win or (ev.tuplet_start) or (bool(ev.tuplet) != tup_open)
               or (cur and cur[-1].cue != ev.cue))
        if vocal and beamable and ev.lyrics and not ev.is_tie_continuation():
            brk = True
        if brk:
            if len(cur) > 1:
                groups.append(cur)
            cur, cur_win = [], None
        if beamable:
            if not cur:
                cur_win = w
            cur.append(ev)
        tup_open = bool(ev.tuplet) and not ev.tuplet_stop
        if ev.tuplet and ev.tuplet_stop:
            if len(cur) > 1:
                groups.append(cur)
            cur, cur_win = [], None
        t += ev.dur
    if len(cur) > 1:
        groups.append(cur)
    return groups


def beam_groups_manual(evs):
    groups, cur, inside = [], [], False
    for ev in evs:
        if ev.kind == 'clef':
            continue
        if ev.beam == '[':
            inside = True
            cur = [ev]
            continue
        if inside:
            cur.append(ev)
            if ev.beam == ']':
                groups.append(cur)
                cur, inside = [], False
    if inside:
        raise ValueError('unterminated manual beam')
    return groups


def assign_beams(score, part, vkey, groups):
    for g in groups:
        for ev in g:
            if ev.kind != 'note' or ev.dtype not in NBEAMS:
                raise ValueError(f'{part.id}:{vkey}: unbeamable event in beam group {ev.dtype}')
        n = len(g)
        for k, ev in enumerate(g):
            ev.beams = {1: 'begin' if k == 0 else ('end' if k == n - 1 else 'continue')}
        for lev in (2, 3, 4):
            k = 0
            while k < n:
                if NBEAMS[g[k].dtype] < lev:
                    k += 1
                    continue
                j = k
                while j + 1 < n and NBEAMS[g[j + 1].dtype] >= lev:
                    j += 1
                if j == k:
                    g[k].beams[lev] = 'forward hook' if k == 0 else 'backward hook'
                else:
                    for q in range(k, j + 1):
                        g[q].beams[lev] = 'begin' if q == k else ('end' if q == j else 'continue')
                k = j + 1


# ------------------------------------------------------------------ main

def prepare(score: Score, layout: dict, opts: dict):
    """Fill ev.printed_staff, ev.beams, ev.beam ('['/']' for LilyPond), ev.stem_dir, ev.acc.
    Returns a report dict (printed accidentals per staff etc.)."""
    tables = staff_tables(score, layout)
    assign_printed_staves(score, tables)
    tl = clef_timeline(score, tables)
    offs = score.measure_offsets()
    vocal_beaming = opts.get('vocal_beaming', True)
    # ---------------- beams
    beam_groups = []
    for p in score.parts:
        for v in p.voices:
            evs_all = [ev for m in p.measures for ev in m.get(v.key, [])]
            manual = any(ev.beam for ev in evs_all)
            vocal = vocal_beaming and p.instrument == 'voice' and any(ev.lyrics for ev in evs_all)
            for i in range(len(score.measures)):
                if manual:
                    groups = beam_groups_manual(p.measures[i].get(v.key, []))
                else:
                    groups = beam_groups_auto(score, p, v.key, i, vocal)
                for ev in p.measures[i].get(v.key, []):
                    ev.beams = {}
                    ev.beam = ''
                assign_beams(score, p, v.key, groups)
                for g in groups:
                    g[0].beam = '['
                    g[-1].beam = ']'
                    beam_groups.append((p.id, v.key, i, g))
    # ---------------- stems
    group_of = {}
    for pid, vk, i, g in beam_groups:
        for ev in g:
            group_of[id(ev)] = g
    onset_of = {}
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                t = offs[i]
                for ev in m.get(v.key, []):
                    onset_of[id(ev)] = t
                    t += ev.dur
    role_of = {}
    for k, t in enumerate(tables):
        for sid, vlist in t['voices'].items():
            for i in range(t['start'], t['end']):
                if len(vlist) < 2:
                    continue
                roles = staff_roles([((pid, vk), score.part(pid).measures[i].get(vk, [])) for pid, vk in vlist])
                for (pid, vk), r in roles.items():
                    role_of[(pid, vk, i)] = r

    def extent(ev):
        clef = clef_at(tl, ev.printed_staff, onset_of[id(ev)])
        ps = [staff_pos(pp, clef) for pp in ev.pitches]
        return max(ps) + min(ps)

    done = set()
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                seg = tables[seg_index(tables, i)]
                for ev in m.get(v.key, []):
                    if ev.kind != 'note' or id(ev) in done:
                        continue
                    if ev.dtype in STEMLESS:
                        ev.stem_dir = None
                        done.add(id(ev))
                        continue
                    if ev.stem:
                        ev.stem_dir = ev.stem
                        done.add(id(ev))
                        continue
                    r = role_of.get((p.id, v.key, i), 0)
                    if r:
                        ev.stem_dir = 'up' if r in (1, 3) else 'down'
                        done.add(id(ev))
                        continue
                    g = group_of.get(id(ev))
                    if g is None:
                        ev.stem_dir = 'down' if extent(ev) >= 0 else 'up'
                        done.add(id(ev))
                        continue
                    staves = {e.printed_staff for e in g}
                    if any(e.stem for e in g):
                        d = next(e.stem for e in g if e.stem)
                        for e in g:
                            e.stem_dir = e.stem or d
                    elif len(staves) > 1:
                        top = min(staves, key=lambda s: seg['order'][s])
                        for e in g:
                            e.stem_dir = 'down' if e.printed_staff == top else 'up'
                    else:
                        tot = sum(extent(e) for e in g)
                        for e in g:
                            e.stem_dir = 'down' if tot >= 0 else 'up'
                    for e in g:
                        done.add(id(e))
    # ---------------- accidentals
    starts = system_starts(score, layout)

    def simulate(key_fn):
        """key_fn(part, voice, ev) -> staff key.  Returns {(id(ev), pitch): name} of printed accidentals"""
        bystaff = {}
        for p in score.parts:
            for v in p.voices:
                for i, m in enumerate(p.measures):
                    t = offs[i]
                    for ev in m.get(v.key, []):
                        if ev.kind == 'note':
                            bystaff.setdefault((key_fn(p, v, ev), i), []).append((t, ev))
                        t += ev.dur
        res = {}
        for (sk, i), evs in bystaff.items():
            kalt = key_alters(score.current_key(i)[0])
            state = {}
            evs.sort(key=lambda x: x[0])
            k = 0
            while k < len(evs):
                t = evs[k][0]
                grp = []
                while k < len(evs) and evs[k][0] == t:
                    grp.append(evs[k][1])
                    k += 1
                upd = {}
                for ev in grp:
                    for pp in ev.pitches:
                        step, alt, octv = pp
                        cur = state.get((octv, step), kalt[step])
                        if pp in ev.tie_stop:
                            if i in starts and t == offs[i] and alt != cur:
                                res[(id(ev), pp)] = ACC_NAME[alt]
                            continue
                        if alt != cur:
                            if alt != 0 and cur != 0 and (alt > 0) == (cur > 0) and abs(cur) > abs(alt):
                                raise ValueError(f'extraNatural case not supported: {pp}')
                            res[(id(ev), pp)] = ACC_NAME[alt]
                        upd[(octv, step)] = alt
                state.update(upd)
        return res

    truth_acc = simulate(lambda p, v, ev: (p.id, ev.staff or v.staff))
    printed_acc = simulate(lambda p, v, ev: ev.printed_staff)
    for p in score.parts:
        for m in p.measures:
            for evs in m.values():
                for ev in evs:
                    if ev.kind == 'note':
                        ev.acc = {pp: truth_acc[(id(ev), pp)] for pp in ev.pitches if (id(ev), pp) in truth_acc}
    # printed expectation per staff
    printed = []
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                for ev in m.get(v.key, []):
                    if ev.kind == 'note':
                        for pp in ev.pitches:
                            if (id(ev), pp) in printed_acc:
                                printed.append((ev.printed_staff, str(onset_of[id(ev)]), pp, printed_acc[(id(ev), pp)]))
    diff = len(truth_acc) != len(printed_acc) or any(truth_acc.get(k) != v for k, v in printed_acc.items())
    return {'tables': tables, 'clef_timeline': tl, 'onset_of': onset_of, 'beam_groups': beam_groups,
            'printed_acc': printed, 'truth_acc_n': len(truth_acc), 'printed_acc_n': len(printed_acc),
            'acc_truth_differs_from_print': diff, 'system_starts': sorted(starts)}
