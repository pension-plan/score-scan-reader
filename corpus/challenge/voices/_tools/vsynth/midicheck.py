"""Minimal MIDI reader + comparison of LilyPond's MIDI output against the truth
model (onset, pitch) multiset.  This proves the engraving matches truth."""
from __future__ import annotations

import struct
from collections import Counter
from fractions import Fraction as F

from .model import Score, attacks


def read_midi(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'MThd'
    hlen = struct.unpack('>I', data[4:8])[0]
    fmt, ntrk, div = struct.unpack('>HHH', data[8:14])
    pos = 8 + hlen
    tracks = []
    for _ in range(ntrk):
        assert data[pos:pos + 4] == b'MTrk', data[pos:pos + 4]
        ln = struct.unpack('>I', data[pos + 4:pos + 8])[0]
        trk = data[pos + 8:pos + 8 + ln]
        pos += 8 + ln
        tracks.append(_parse_track(trk))
    return div, tracks


def _vlq(b, i):
    v = 0
    while True:
        c = b[i]
        i += 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return v, i


def _parse_track(b):
    i, t, status = 0, 0, None
    notes = []
    name = ''
    lyrics = []
    while i < len(b):
        d, i = _vlq(b, i)
        t += d
        c = b[i]
        if c == 0xFF:
            typ = b[i + 1]
            ln, j = _vlq(b, i + 2)
            payload = b[j:j + ln]
            if typ == 0x03:
                name = payload.decode('latin-1')
            elif typ in (0x05, 0x01):
                lyrics.append((t, payload.decode('utf-8', 'replace')))
            i = j + ln
            continue
        if c in (0xF0, 0xF7):
            ln, j = _vlq(b, i + 1)
            i = j + ln
            continue
        if c & 0x80:
            status = c
            i += 1
        hi = status & 0xF0
        if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
            a1, a2 = b[i], b[i + 1]
            i += 2
            if hi == 0x90 and a2 > 0:
                notes.append((t, a1))
        else:
            i += 1
    return {'name': name, 'notes': notes, 'lyrics': lyrics}


def compare(score: Score, midi_path: str):
    div, tracks = read_midi(midi_path)
    got = Counter()
    for tr in tracks:
        for t, p in tr['notes']:
            got[(F(t, div), p)] += 1
    exp = Counter((F(t), p) for t, p, _, _ in attacks(score))
    missing = exp - got
    extra = got - exp
    n = sum(exp.values())
    ok = not missing and not extra
    # unison voices on a shared staff may be merged by some performers; tolerate
    # only exact duplicates
    return {
        'ok': ok,
        'expected_attacks': n,
        'midi_attacks': sum(got.values()),
        'missing': sorted(missing.elements())[:10],
        'extra': sorted(extra.elements())[:10],
        'n_missing': sum(missing.values()),
        'n_extra': sum(extra.values()),
    }


# ---------------------------------------------------------------- challenge/voices: detailed checks

def voice_attacks(score: Score, include_hidden=False):
    """{(pid, vkey): Counter((onset, midi))} of printed (or all) attacks."""
    from .model import midi as _midi, voice_events
    out = {}
    for p in score.parts:
        for v in p.voices:
            c = Counter()
            for i, t, ev in voice_events(score, p, v.key):
                if ev.kind == 'note' and (include_hidden or not ev.hidden):
                    for pit in ev.pitches:
                        if pit not in ev.tie_stop:
                            c[(F(t), _midi(pit))] += 1
            out[(p.id, v.key)] = c
    return out


def compare_detailed(score: Score, midi_path: str, lyric_lines, vname):
    """Per-Voice MIDI track == printed attacks of that truth voice; every
    lyric line's MIDI lyric events == expected (onset, syllable) list."""
    div, tracks = read_midi(midi_path)
    exp = voice_attacks(score)
    res = {'ok': True, 'voices': {}, 'lyric_lines': [], 'errors': []}
    used = set()
    for (pid, vk), c in exp.items():
        nm = vname(pid, vk)
        cand = [k for k, tr in enumerate(tracks) if tr['name'].split(':')[-1] == nm]
        if len(cand) != 1:
            res['ok'] = False
            res['errors'].append(f'voice {nm}: {len(cand)} MIDI tracks')
            continue
        tr = tracks[cand[0]]
        used.add(cand[0])
        got = Counter((F(t, div), p) for t, p in tr['notes'])
        miss, extra = c - got, got - c
        okv = not miss and not extra
        res['voices'][f'{pid}:{vk}'] = {'ok': okv, 'attacks': sum(c.values()),
                                        'missing': sorted(miss.elements())[:6], 'extra': sorted(extra.elements())[:6]}
        if not okv:
            res['ok'] = False
            res['errors'].append(f'voice {nm} mismatch')
    for k, tr in enumerate(tracks):
        if k not in used and tr['notes']:
            res['ok'] = False
            res['errors'].append(f'unexpected note track {tr["name"]!r}')
    # lyric tracks: unnamed tracks with lyric events (skip the header track)
    ltracks = [[(F(t, div), txt) for t, txt in tr['lyrics'] if txt.strip()] for tr in tracks
               if not tr['notes'] and tr['lyrics'] and not any('creator' in x for _, x in tr['lyrics'])]
    free = list(range(len(ltracks)))
    for ln in lyric_lines:
        expl = ln['expected']
        hit = None
        for j in free:
            if ltracks[j] == expl:
                hit = j
                break
        res['lyric_lines'].append({'line': {k: v for k, v in ln.items() if k != 'expected'},
                                   'syllables': len(expl), 'ok': hit is not None})
        if hit is None:
            res['ok'] = False
            res['errors'].append(f'lyric line {ln.get("voice") or ln.get("sources")} v{ln["verse"]} not matched; '
                                 f'expected {expl[:5]}... tracks {[lt[:4] for lt in ltracks]}')
        else:
            free.remove(hit)
    if free:
        res['ok'] = False
        res['errors'].append(f'{len(free)} unexpected lyric tracks')
    return res


def lyricsto_expected(score: Score, pid, vkey, verse):
    from .model import voice_events
    part = score.part(pid)
    out = []
    for i, t, ev in voice_events(score, part, vkey):
        if ev.kind == 'note' and not ev.hidden and verse in ev.lyrics:
            out.append((F(t), ev.lyrics[verse].text))
    return out


def check_hidden_carriers(score: Score, staff_of):
    """Each hidden event must be duplicated (onset, pitches, duration, tie state)
    by a printed note of another voice engraved on the same staff.
    staff_of: (pid, vkey) -> staff id in the engraving."""
    from .model import voice_events
    printed = {}
    for p in score.parts:
        for v in p.voices:
            for i, t, ev in voice_events(score, p, v.key):
                if ev.kind == 'note' and not ev.hidden:
                    printed.setdefault((staff_of[(p.id, v.key)], F(t)), []).append(
                        (sorted(ev.pitches), ev.dur, (p.id, v.key), bool(ev.tie_start)))
    n, errors = 0, []
    for p in score.parts:
        for v in p.voices:
            for i, t, ev in voice_events(score, p, v.key):
                if ev.hidden:
                    n += 1
                    cands = printed.get((staff_of[(p.id, v.key)], F(t)), [])
                    if not any(c[0] == sorted(ev.pitches) and c[1] == ev.dur and c[2] != (p.id, v.key)
                               and c[3] == bool(ev.tie_start) for c in cands):
                        errors.append(f'hidden {p.id}:{v.key} m{i} t={t} {ev.pitches} has no carrier')
    return {'ok': not errors, 'hidden_events': n, 'errors': errors}
