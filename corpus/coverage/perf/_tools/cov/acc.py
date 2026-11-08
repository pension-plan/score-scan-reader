"""Accidental display simulator (LilyPond 2.24 'default' style), copied from
corpus/challenge/pitch/_tools/pk/acc.py and extended for grace notes (own moments).

Used as an independent cross-check of the accidentals harvested from the engraving:
the truth's <accidental> elements come from what LilyPond printed (per engraved staff);
this simulation recomputes them per PART staff.  If the two disagree (e.g. two parts share a
staff in a closed score and one part's accidental is implied by the other part's) the build
fails, so the truth is right both as a picture of the page and as per-part notation.
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import STEPS, display_ql

SHARP_ORDER = 'FCGDAEB'


def key_alters(fifths):
    alt = {s: 0 for s in STEPS}
    if fifths > 0:
        for s in SHARP_ORDER[:fifths]:
            alt[s] = 1
    elif fifths < 0:
        for s in SHARP_ORDER[::-1][:-fifths]:
            alt[s] = -1
    return alt


def simulate(score, staves, line_start_measures=()):
    """staves: [(staff_id, [(pid, vkey, staffnum-or-None)])].  -> {(event id, pitch): decision}"""
    offs = score.measure_offsets()
    out = {}
    lsm = set(line_start_measures)
    for sid, voices in staves:
        for i, mi in enumerate(score.measures):
            kalt = key_alters(score.current_key(i)[0])
            state = {}
            evs = []
            for pid, vk, sn in voices:
                part = score.part(pid)
                home = part.voice(vk).staff
                t = offs[i]
                lst = part.measures[i].get(vk, [])
                for k, ev in enumerate(lst):
                    if ev.kind == 'note' and (sn is None or (ev.staff or home) == sn):
                        g = F(0)
                        if ev.grace:
                            j = k
                            while j < len(lst) and lst[j].grace:
                                g -= display_ql(lst[j].dtype, lst[j].dots)
                                j += 1
                        evs.append(((t, g), ev))
                    t += ev.dur
            evs.sort(key=lambda x: x[0])
            k = 0
            while k < len(evs):
                tg = evs[k][0]
                grp = []
                while k < len(evs) and evs[k][0] == tg:
                    grp.append(evs[k][1])
                    k += 1
                updates = {}
                for ev in grp:
                    for p in ev.pitches:
                        step, alt, octv = p
                        cur = state.get((octv, step), kalt[step])
                        if p in ev.tie_stop:
                            if i in lsm and tg == (offs[i], F(0)) and alt != cur:
                                out[(id(ev), p)] = {'alter': alt, 'restore_first': False, 'paren': False,
                                                    'tie_line_start': True}
                            continue
                        forced = p in ev.force_acc
                        caut = p in ev.caut_acc
                        if alt != cur or forced or caut:
                            rf = (alt != 0 and cur != 0 and (alt > 0) == (cur > 0) and abs(cur) > abs(alt))
                            out[(id(ev), p)] = {'alter': alt, 'restore_first': rf, 'paren': caut}
                        updates[(octv, step)] = alt
                state.update(updates)
    return out


ACC_NAME = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}
GLYPH = {'accidentals.sharp': 1, 'accidentals.flat': -1, 'accidentals.natural': 0,
         'accidentals.doublesharp': 2, 'accidentals.flatflat': -2}


def acc_value(alter, restore_first):
    if restore_first and alter == 1:
        return 'natural-sharp'
    if restore_first and alter == -1:
        return 'natural-flat'
    return ACC_NAME[alter]
