"""Accidental display simulator.

Implements the LilyPond 2.24 'default' accidental style as observed empirically
(see _tools/README.txt):
  * state is kept per staff (all voices on a staff share it), per (octave, step)
  * the state resets to the key signature at every barline
  * notes sounding at the same moment are judged against the state *before* that
    moment (simultaneous notes do not affect each other)
  * tie-continuation notes print no accidental and do NOT update the state
    (so an untied repeat of the same altered pitch later in the new bar gets its
    accidental again); exception: a tie continuation at the very start of a
    system prints its accidental (LilyPond default) - reported separately
  * '!' (forced) always prints; '?' (cautionary) prints in parentheses
  * extraNatural: a reduction of a double alteration (x -> #, bb -> b) prints a
    natural before the accidental (MusicXML natural-sharp / natural-flat)

The same function is used twice:
  - per *part* staff  -> <accidental> elements of truth.musicxml (what a correct
    per-part transcription displays)
  - per *engraved* staff (closed score: two parts share a staff) -> expected
    printed accidentals, compared against LilyPond's own grob log
"""
from __future__ import annotations

from .model import STEPS

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
    """staves: list of (staff_id, [(pid, vkey), ...]).
    Returns (decisions, tie_line_start) where decisions maps (id(event), pitch) ->
    dict(staff, onset, pitch, alter, restore_first, paren, forced, required)."""
    offs = score.measure_offsets()
    out = {}
    tls = []
    lsm = set(line_start_measures)
    for sid, voices in staves:
        for i, mi in enumerate(score.measures):
            fifths, _mode = score.current_key(i)
            kalt = key_alters(fifths)
            state = {}
            evs = []
            for pid, vk in voices:
                t = offs[i]
                for ev in score.part(pid).measures[i].get(vk, []):
                    if ev.kind == 'note':
                        evs.append((t, ev))
                    t += ev.dur
            evs.sort(key=lambda x: x[0])
            k = 0
            while k < len(evs):
                t = evs[k][0]
                grp = []
                while k < len(evs) and evs[k][0] == t:
                    grp.append(evs[k][1])
                    k += 1
                updates = {}
                for ev in grp:
                    for p in ev.pitches:
                        step, alt, octv = p
                        cur = state.get((octv, step), kalt[step])
                        if p in ev.tie_stop:
                            if i in lsm and t == offs[i] and alt != cur:
                                tls.append({'staff': sid, 'onset': t, 'pitch': p, 'alter': alt})
                            continue
                        forced = p in ev.force_acc
                        caut = p in ev.caut_acc
                        required = alt != cur
                        if required or forced or caut:
                            rf = (alt != 0 and cur != 0 and (alt > 0) == (cur > 0) and abs(cur) > abs(alt))
                            out[(id(ev), p)] = {'staff': sid, 'onset': t, 'pitch': p, 'alter': alt,
                                                'restore_first': rf, 'paren': caut, 'forced': forced,
                                                'required': required}
                        updates[(octv, step)] = alt
                state.update(updates)
    return out, tls


def part_staves(score):
    """one staff entry per (part, staff number) - the truth's own staves"""
    res = []
    for p in score.parts:
        for s in range(1, p.staves + 1):
            res.append((f'{p.id}/{s}', [(p.id, v.key) for v in p.voices if v.staff == s]))
    return res


def layout_staves(layout):
    res = []
    for g in layout['groups']:
        for st in g['staves']:
            res.append((st['id'], [tuple(v) for v in st['voices']]))
    return res


ACC_NAME = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}


def acc_value(d):
    a = d['alter']
    if d['restore_first'] and a == 1:
        return 'natural-sharp'
    if d['restore_first'] and a == -1:
        return 'natural-flat'
    return ACC_NAME[a]


def key_cancel_steps(old_fifths, new_fifths):
    o, n = key_alters(old_fifths), key_alters(new_fifths)
    return sorted(s for s in STEPS if o[s] != 0 and n[s] != o[s])
