"""Score model for the coverage/perf generator.

One model feeds both writers: lily.py (engraving.ly) and mxl.py (truth.musicxml).
Engraving decisions that LilyPond makes on its own (stem directions, beams, printed
accidentals, staff positions -> ledger lines) are harvested from an instrumented
LilyPond run (harvest.py) and written into the truth, so the truth describes exactly
what is printed.

Durations are Fractions of a quarter note.  Pitches are SOUNDING pitches
(step, alter, octave) - ottava brackets only change the display.
Derived from corpus/challenge/layout/_tools/lsynth/model.py (copied, extended).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F
from typing import Dict, List, Optional, Tuple

STEP_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
STEPS = 'CDEFGAB'
TYPE_QL = {'breve': F(8), 'whole': F(4), 'half': F(2), 'quarter': F(1), 'eighth': F(1, 2),
           '16th': F(1, 4), '32nd': F(1, 8), '64th': F(1, 16)}
TYPE_FLAGS = {'breve': 0, 'whole': 0, 'half': 0, 'quarter': 0, 'eighth': 1, '16th': 2, '32nd': 3, '64th': 4}

Pitch = Tuple[str, int, int]


def midi(p: Pitch) -> int:
    return 12 * (p[2] + 1) + STEP_PC[p[0]] + p[1]


def display_ql(dtype: str, dots: int) -> F:
    base = TYPE_QL[dtype]
    tot, add = base, base
    for _ in range(dots):
        add /= 2
        tot += add
    return tot


def split_plain(ql: F):
    out = []
    rem = F(ql)
    order = sorted(TYPE_QL.items(), key=lambda kv: -kv[1])
    while rem > 0:
        best = None
        for t, _b in order:
            for dots in (2, 1, 0):
                d = display_ql(t, dots)
                if d <= rem and (best is None or d > best[2]):
                    best = (t, dots, d)
        if best is None:
            raise ValueError(f'cannot split {ql}')
        out.append(best)
        rem -= best[2]
    return out


@dataclass
class Lyric:
    text: str
    syllabic: str = 'single'
    extend: bool = False


@dataclass
class Event:
    kind: str                      # note | rest | space | clef | ottava
    dur: F = F(0)                  # sounding duration in quarters (0 for grace notes)
    pitches: List[Pitch] = field(default_factory=list)
    dtype: Optional[str] = None
    dots: int = 0
    tuplet: Optional[Tuple[int, int]] = None
    tuplet_start: bool = False
    tuplet_stop: bool = False
    grace: Optional[str] = None    # None | 'plain' | 'slash'
    tie_start: set = field(default_factory=set)
    tie_stop: set = field(default_factory=set)
    slur_start: int = 0
    slur_stop: int = 0
    artic: List[str] = field(default_factory=list)   # staccato staccatissimo accent tenuto strong-accent
    fermata: bool = False
    orn: List[str] = field(default_factory=list)     # trill mordent turn
    arpeggio: bool = False
    fing: Dict[Pitch, int] = field(default_factory=dict)
    breath: bool = False
    trem: int = 0                  # single-note tremolo: number of strokes
    trem_ly: int = 0               # LilyPond :N value
    dynamics: List[str] = field(default_factory=list)
    wedge: List[str] = field(default_factory=list)   # crescendo | diminuendo | stop
    pedal: List[str] = field(default_factory=list)   # start | stop
    words: List[tuple] = field(default_factory=list)  # (text, above|below, italic|bold)
    lyrics: Dict[int, Lyric] = field(default_factory=dict)
    force_acc: set = field(default_factory=set)
    caut_acc: set = field(default_factory=set)
    clef: Optional[str] = None
    ottava: int = 0
    measure_rest: bool = False
    staff: Optional[int] = None    # cross-staff: printed staff if not the voice's home staff
    beam: str = ''                 # manual beam marks ('[' / ']') when autobeaming is off
    # filled by harvest.py
    ids: List[str] = field(default_factory=list)      # one LilyPond grob id per pitch (or one for a rest)
    hv: Dict[str, dict] = field(default_factory=dict)  # id -> harvested engraving data

    def is_attack(self):
        return self.kind == 'note' and any(p not in self.tie_stop for p in self.pitches)

    def is_tie_continuation(self):
        return self.kind == 'note' and bool(self.pitches) and all(p in self.tie_stop for p in self.pitches)


@dataclass
class MeasureInfo:
    number: int
    dur: F
    nominal: F
    time: Optional[Tuple[int, int]] = None
    time_symbol: Optional[str] = None           # common | cut
    key: Optional[Tuple[int, str]] = None       # (fifths, mode)
    left_bar: Optional[str] = None              # repeat-start
    right_bar: Optional[str] = None             # repeat-end | double | final
    implicit: bool = False
    volta_start: Optional[str] = None
    volta_end: Optional[str] = None             # stop | discontinue
    marks: List[dict] = field(default_factory=list)       # tempo / rehearsal / words / segno / coda
    end_marks: List[dict] = field(default_factory=list)   # words at measure end (D.C., Fine ...)
    brk: Optional[str] = None                   # 'system' | 'page' : new system/page starts here


@dataclass
class VoiceDef:
    key: str
    staff: int


@dataclass
class Part:
    id: str
    name: str
    abbr: str = ''
    instrument: str = 'voice'
    staves: int = 1
    clefs: List[str] = field(default_factory=lambda: ['treble'])
    voices: List[VoiceDef] = field(default_factory=list)
    measures: List[Dict[str, List[Event]]] = field(default_factory=list)

    def voice(self, key):
        for v in self.voices:
            if v.key == key:
                return v
        raise KeyError(key)


@dataclass
class Score:
    title: str = ''
    composer: str = ''
    lyricist: str = ''
    arranger: str = ''
    rights: str = ''
    source: str = ''
    credits: list = field(default_factory=list)
    measures: List[MeasureInfo] = field(default_factory=list)
    parts: List[Part] = field(default_factory=list)
    groups: List[dict] = field(default_factory=list)
    marks_part: Optional[str] = None
    page: Optional[dict] = None                 # {'name','width_mm','height_mm','staff_size'}

    def part(self, pid) -> Part:
        for p in self.parts:
            if p.id == pid:
                return p
        raise KeyError(pid)

    def measure_offsets(self):
        offs, t = [], F(0)
        for m in self.measures:
            offs.append(t)
            t += m.dur
        return offs

    def current_time(self, i):
        for j in range(i, -1, -1):
            if self.measures[j].time:
                return self.measures[j].time, self.measures[j].time_symbol
        return (4, 4), None

    def current_key(self, i):
        for j in range(i, -1, -1):
            if self.measures[j].key:
                return self.measures[j].key
        return (0, 'major')


def voice_events(score: Score, part: Part, vkey: str):
    offs = score.measure_offsets()
    for i, mdict in enumerate(part.measures):
        t = offs[i]
        for ev in mdict.get(vkey, []):
            yield i, t, ev
            t += ev.dur


def renumber(score: Score):
    n = 0 if score.measures and score.measures[0].implicit else 1
    for m in score.measures:
        m.number = n
        n += 1


def staff_roles(voice_keys_contents):
    """ordered [(vkey, events)] sharing a staff in one measure -> {vkey: role}; 0 = alone."""
    present = [k for k, evs in voice_keys_contents if any(e.kind in ('note', 'rest') for e in evs)]
    roles = {}
    if len(present) <= 1:
        for k, _ in voice_keys_contents:
            roles[k] = 0
        return roles
    for k, _ in voice_keys_contents:
        roles[k] = present.index(k) + 1 if k in present else 0
    return roles


# ---------------------------------------------------------------- lyrics

def compute_extenders(score: Score):
    """A word-final syllable followed by a melisma gets an extender line."""
    for p in score.parts:
        for v in p.voices:
            evs = [ev for _, _, ev in voice_events(score, p, v.key)]
            verses = sorted({n for ev in evs for n in ev.lyrics})
            for verse in verses:
                last, melisma = None, False
                for ev in evs:
                    if ev.kind == 'rest':
                        if last is not None:
                            last.extend = melisma and last.syllabic in ('single', 'end')
                        last, melisma = None, False
                        continue
                    if ev.kind != 'note' or ev.grace:
                        continue
                    if verse in ev.lyrics:
                        if last is not None:
                            last.extend = melisma and last.syllabic in ('single', 'end')
                        last, melisma = ev.lyrics[verse], False
                    elif last is not None:
                        melisma = True
                if last is not None:
                    last.extend = melisma and last.syllabic in ('single', 'end')


def parse_lyric_text(text: str):
    toks = text.split()
    out = []
    hy_next = False
    for tk in toks:
        if tk == '--':
            hy_next = True
            if out and out[-1] is not None:
                out[-1].syllabic = 'begin' if out[-1].syllabic == 'single' else (
                    'middle' if out[-1].syllabic == 'end' else out[-1].syllabic)
            continue
        if tk == '_':
            out.append(None)
            continue
        out.append(Lyric(tk.replace('~', ' '), 'end' if hy_next else 'single'))
        hy_next = False
    return out


def lyric_slots(score: Score, pid: str, vkey: str, slur_melisma=True):
    """note events that take a syllable: attacks that are not tie continuations, not grace notes,
    and (with slur_melisma) not inside a slur that started on an earlier note."""
    part = score.part(pid)
    out = []
    in_slur = False
    for i, t, ev in voice_events(score, part, vkey):
        if ev.kind != 'note' or ev.grace:
            continue
        if ev.is_tie_continuation():
            if ev.slur_stop:
                in_slur = False
            continue
        if not (slur_melisma and in_slur):
            out.append(ev)
        if ev.slur_start:
            in_slur = True
        if ev.slur_stop and not ev.slur_start:
            in_slur = False
    return out


def set_verses(score: Score, pid: str, vkey: str, verses: List[str]):
    slots = lyric_slots(score, pid, vkey)
    for vn, text in enumerate(verses, 1):
        syls = parse_lyric_text(text)
        if len(syls) != len(slots):
            raise ValueError(f'{pid}:{vkey} verse {vn}: {len(syls)} syllables for {len(slots)} slots')
        for ev, ly in zip(slots, syls):
            if ly is not None:
                ev.lyrics[vn] = ly
    compute_extenders(score)


# ---------------------------------------------------------------- checks

def sanitize_ties(score: Score):
    """ties only between consecutive notes of a voice with the same pitch"""
    for p in score.parts:
        for v in p.voices:
            prev = None
            for mm in p.measures:
                for ev in mm.get(v.key, []):
                    if ev.kind in ('clef', 'ottava'):
                        continue
                    if ev.kind != 'note' or ev.grace:
                        if ev.kind != 'note':
                            if prev is not None:
                                prev.tie_start = set()
                            prev = None
                        continue
                    if prev is None:
                        ev.tie_stop = set()
                    else:
                        valid = {x for x in prev.tie_start if x in ev.pitches}
                        prev.tie_start = valid
                        ev.tie_stop = set(valid)
                    prev = ev
            if prev is not None:
                prev.tie_start = set()


def check(score: Score):
    nm = len(score.measures)
    for p in score.parts:
        assert len(p.measures) == nm, (p.id, len(p.measures), nm)
        for i, m in enumerate(p.measures):
            for k, evs in m.items():
                tot = sum((e.dur for e in evs), F(0))
                if tot > score.measures[i].dur:
                    raise ValueError(f'{p.id} voice {k} measure {i + 1}: {tot} > {score.measures[i].dur}')
                for e in evs:
                    if e.kind in ('note', 'rest') and not e.measure_rest:
                        d = display_ql(e.dtype, e.dots)
                        if e.tuplet:
                            d = d * e.tuplet[1] / e.tuplet[0]
                        if e.grace:
                            d = F(0)
                        if d != e.dur:
                            raise ValueError(f'{p.id} m{i + 1} duration mismatch {e.dtype} {e.dots} {e.tuplet} {e.dur}')
    return True
