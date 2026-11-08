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
