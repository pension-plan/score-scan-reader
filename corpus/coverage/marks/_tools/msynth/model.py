"""Score model + note DSL for the coverage/marks generator.

The truth (mxl.py) and the engraving (lily.py) are both written from this model, so the
truth matches what is printed; verify.py then checks the LilyPond event/grob dump and the
MIDI output against the model.

Durations are Fractions of a quarter note.  Pitches are (step, alter, octave), octave as in
MusicXML (c' = C4).

Note DSL (one string per staff, absolute LilyPond pitch, measures separated by '|'):

  pitch      [a-g](is|es|isis|eses)?[',]*   r (rest)   R (whole-bar rest)
  chord      <c'-1 e'-3 g'-5>               (inner -N / ^N / _N = fingering of that note)
  duration   \\breve 1 2 4 8 16 32 64 + dots (sticky like LilyPond)
  postfix    ~ tie   ( ) slur   [ ] beam
             -. staccato  -! staccatissimo  -> accent  -- tenuto  -^ marcato  -_ portato
             (first character '-' = default side, '^' = forced above, '_' = forced below)
             -N ^N _N fingering digit N (single note)
             \\fermata \\trill \\mordent \\prall \\turn \\reverseturn (optionally ^ / _ prefixed)
             \\pp \\p \\mp \\mf \\f \\ff \\sfz \\ppp \\fff \\fp \\sf \\sfp \\fz ...  dynamics
             \\< \\> \\!  hairpins     \\sustainOn \\sustainOff  pedal
             \\arpeggio                  ^"text" / _"text" italic expression text
  standalone \\breathe (after the previous note)   \\tempo{Text|4|120} \\tempo{Text} \\tempo{|4.|60}
             (before the next note)  \\mark (boxed rehearsal letter at bar start)
             \\break \\pageBreak (before this bar)  \\time=3/4  \\key=-1:minor  \\clef=bass  \\bar=||
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction as F
from typing import Dict, List, Optional, Tuple

STEP_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
STEPS = 'CDEFGAB'
TYPE_QL = {'breve': F(8), 'whole': F(4), 'half': F(2), 'quarter': F(1), 'eighth': F(1, 2),
           '16th': F(1, 4), '32nd': F(1, 8), '64th': F(1, 16)}
LOG = {'breve': -1, 'whole': 0, 'half': 1, 'quarter': 2, 'eighth': 3, '16th': 4, '32nd': 5, '64th': 6}
DUR_TYPE = {'\\breve': 'breve', '1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th',
            '32': '32nd', '64': '64th'}
TYPE_LY = {v: k for k, v in DUR_TYPE.items()}
ACC = {None: 0, '': 0, 'is': 1, 'es': -1, 'isis': 2, 'eses': -2}

ARTIC_SHORT = {'.': 'staccato', '!': 'staccatissimo', '>': 'accent', '-': 'tenuto', '^': 'marcato',
               '_': 'portato'}
ARTICS = set(ARTIC_SHORT.values())
ORNAMENTS = ('trill', 'mordent', 'prall', 'turn', 'reverseturn')
FERMATAS = ('fermata',)
SCRIPT_CMDS = ORNAMENTS + FERMATAS
DYNAMICS = ('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff', 'sfz', 'sfp', 'sf', 'fp', 'fz',
            'rfz', 'sffz')
PLACE = {'-': None, '^': 'above', '_': 'below', '': None}

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


@dataclass
class Ev:
    kind: str                       # note | rest | clef
    dur: F = F(0)
    pitches: List[Pitch] = field(default_factory=list)
    dtype: Optional[str] = None
    dots: int = 0
    measure_rest: bool = False
    tie_start: set = field(default_factory=set)
    tie_stop: set = field(default_factory=set)
    beam_start: bool = False
    beam_stop: bool = False
    slur_start: bool = False
    slur_stop: bool = False
    marks: List[Tuple[str, Optional[str]]] = field(default_factory=list)       # (lily type, placement)
    fingering: List[Tuple[int, Optional[str], Optional[Pitch]]] = field(default_factory=list)
    dynamics: List[str] = field(default_factory=list)
    wedges: List[str] = field(default_factory=list)  # crescendo | diminuendo | stop | stop-implicit
    pedal: List[str] = field(default_factory=list)   # stop, start (in that order)
    words: List[Tuple[str, str]] = field(default_factory=list)                 # (text, placement)
    arpeggio: bool = False
    breath: bool = False
    tempo: Optional[dict] = None
    clef: Optional[str] = None
    # filled later (read back from the engraving)
    stem: Optional[str] = None
    mark_dirs: List[str] = field(default_factory=list)       # engraved side of each entry of marks
    finger_dirs: List[str] = field(default_factory=list)     # engraved side of each entry of fingering
    accidentals: Dict[Pitch, str] = field(default_factory=dict)

    @property
    def is_rhythmic(self):
        return self.kind in ('note', 'rest')


@dataclass
class Measure:
    number: int
    dur: F
    time: Optional[Tuple[int, int]] = None
    time_symbol: Optional[str] = None
    key: Optional[Tuple[int, str]] = None
    mark: Optional[str] = None
    new_system: bool = False
    new_page: bool = False
    right_bar: Optional[str] = None     # double | final


@dataclass
class Staff:
    id: str
    clef: str
    voice: str                          # MusicXML voice number
    number: int                         # staff number within the part (1-based)
    measures: List[List[Ev]] = field(default_factory=list)


@dataclass
class Part:
    id: str
    name: str
    abbr: str = ''
    staves: List[Staff] = field(default_factory=list)
    chords: List[dict] = field(default_factory=list)     # {'t': abs onset, 'root': (step, alter), 'kind', 'bass', 'dur'}


@dataclass
class Score:
    title: str = ''
    subtitle: str = ''
    composer: str = ''
    rights: str = ''
    measures: List[Measure] = field(default_factory=list)
    parts: List[Part] = field(default_factory=list)
    groups: List[dict] = field(default_factory=list)     # {'type': PianoStaff|StaffGroup, 'parts': [ids], 'name'}
    pedal_style: str = 'text'           # 'text' (Ped. / *) or 'bracket' (line with notches at changes)
    mark_format: str = 'box-letters'    # rehearsal marks: 'box-letters', 'box-numbers' or 'circle-numbers'

    def offsets(self):
        offs, t = [], F(0)
        for m in self.measures:
            offs.append(t)
            t += m.dur
        return offs

    def time_at(self, i):
        for j in range(i, -1, -1):
            if self.measures[j].time:
                return self.measures[j].time, self.measures[j].time_symbol
        return (4, 4), None

    def key_at(self, i):
        for j in range(i, -1, -1):
            if self.measures[j].key:
                return self.measures[j].key
        return (0, 'major')

    def staves(self):
        for p in self.parts:
            for s in p.staves:
                yield p, s

    def part(self, pid) -> 'Part':
        for p in self.parts:
            if p.id == pid:
                return p
        raise KeyError(pid)


def staff_events(score: Score, st: Staff):
    """yield (measure index, abs onset, event)"""
    offs = score.offsets()
    for i, evs in enumerate(st.measures):
        t = offs[i]
        for ev in evs:
            yield i, t, ev
            t += ev.dur


# ---------------------------------------------------------------- DSL

PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es)?(?P<o>[',]*)$")
NOTE = re.compile(r"^(?P<p><[^>]*>|[a-g](?:isis|eses|is|es)?[',]*|r|R)(?P<d>\\breve|16|32|64|1|2|4|8)?"
                  r"(?P<dots>\.*)(?P<suf>.*)$")
SUFFIX = [
    ('words', re.compile(r'([\^_])"([^"]*)"')),
    ('script', re.compile(r'([\^_]?)\\(' + '|'.join(SCRIPT_CMDS) + r')(?![a-zA-Z])')),
    ('pedal', re.compile(r'\\sustain(On|Off)')),
    ('arpeggio', re.compile(r'\\arpeggio')),
    ('wedge', re.compile(r'\\([<>!])')),
    ('dyn', re.compile(r'\\(' + '|'.join(sorted(DYNAMICS, key=len, reverse=True)) + r')(?![a-zA-Z])')),
    ('artic', re.compile(r'([-^_])([.!>\-^_])')),
    ('finger', re.compile(r'([-^_])(\d)')),
    ('tie', re.compile(r'~')),
    ('slur', re.compile(r'[()]')),
    ('beam', re.compile(r'[\[\]]')),
]


def parse_pitch(t: str) -> Pitch:
    m = PIT.match(t)
    if not m:
        raise ValueError(f'bad pitch {t!r}')
    o = m.group('o')
    return (m.group('s').upper(), ACC[m.group('a')], 3 + o.count("'") - o.count(','))


def tokenize(text: str):
    toks, cur, depth_q, depth_c, depth_b = [], '', False, False, 0
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            depth_q = not depth_q
            cur += c
        elif depth_q:
            cur += c
        elif c == '{':
            depth_b += 1
            cur += c
        elif c == '}':
            depth_b -= 1
            cur += c
        elif depth_b:
            cur += c
        elif c == '<' and not cur and not depth_c:
            depth_c = True
            cur += c
        elif c == '>' and depth_c and (i + 1 >= len(text) or True) and not cur.endswith('-'):
            depth_c = False
            cur += c
        elif depth_c:
            cur += c
        elif c.isspace():
            if cur:
                toks.append(cur)
            cur = ''
        elif c == '|':
            if cur:
                toks.append(cur)
            toks.append('|')
            cur = ''
        else:
            cur += c
        i += 1
    if cur:
        toks.append(cur)
    if depth_q or depth_c or depth_b:
        raise ValueError('unbalanced quote/chord/brace in ' + text[:60])
    return toks


TEMPO = re.compile(r'^\\tempo\{([^|}]*)(?:\|(\d+)(\.?)\|(\d+))?\}$')


def parse_staff(text: str):
    """-> list of measures: {'events': [...], 'cmds': {...}}"""
    measures = []
    cur = {'events': [], 'cmds': {}}
    last_d, last_dots = '4', 0
    pending_tempo = None
    for tk in tokenize(text):
        if tk == '|':
            measures.append(cur)
            cur = {'events': [], 'cmds': {}}
            continue
        if tk == '\\breathe':
            prev = cur['events'] or (measures[-1]['events'] if measures else [])
            prev = [e for e in prev if e.is_rhythmic]
            if not prev:
                raise ValueError('\\breathe without a preceding note')
            prev[-1].breath = True
            continue
        m = TEMPO.match(tk)
        if m:
            pending_tempo = {'text': m.group(1) or None,
                             'unit': DUR_TYPE[m.group(2)] if m.group(2) else None,
                             'dots': len(m.group(3) or ''),
                             'bpm': int(m.group(4)) if m.group(4) else None}
            continue
        if tk == '\\mark':
            cur['cmds']['mark'] = True
            continue
        if tk in ('\\break', '\\pageBreak'):
            if cur['events']:
                raise ValueError(f'{tk} must be at the start of a bar')
            cur['cmds']['new_page' if tk == '\\pageBreak' else 'new_system'] = True
            continue
        m = re.fullmatch(r'\\time=(\d+)/(\d+)(c?)', tk)
        if m:
            cur['cmds']['time'] = (int(m.group(1)), int(m.group(2)))
            if m.group(3):
                cur['cmds']['time_symbol'] = 'common' if cur['cmds']['time'] == (4, 4) else 'cut'
            continue
        m = re.fullmatch(r'\\key=(-?\d+):(major|minor)', tk)
        if m:
            cur['cmds']['key'] = (int(m.group(1)), m.group(2))
            continue
        m = re.fullmatch(r'\\clef=(\S+)', tk)
        if m:
            cur['events'].append(Ev('clef', clef=m.group(1)))
            continue
        m = re.fullmatch(r'\\bar=(\S+)', tk)
        if m:
            cur['cmds']['bar'] = {'||': 'double', '|.': 'final'}[m.group(1)]
            continue
        m = NOTE.match(tk)
        if not m:
            raise ValueError(f'bad token {tk!r}')
        p, d, dots, suf = m.group('p'), m.group('d'), m.group('dots'), m.group('suf')
        if d:
            last_d, last_dots = d, len(dots)
        elif dots:
            last_dots = len(dots)
        dtype = DUR_TYPE[last_d]
        ev = Ev('rest' if p in ('r', 'R') else 'note', display_ql(dtype, last_dots), dtype=dtype, dots=last_dots)
        if p == 'R':
            ev.measure_rest = True
        if p.startswith('<'):
            for inner in p[1:-1].split():
                mm = re.fullmatch(r"([a-g](?:isis|eses|is|es)?[',]*)((?:[-^_]\d)*)", inner)
                if not mm:
                    raise ValueError(f'bad chord member {inner!r} in {tk!r}')
                pit = parse_pitch(mm.group(1))
                ev.pitches.append(pit)
                for side, dig in re.findall(r'([-^_])(\d)', mm.group(2)):
                    ev.fingering.append((int(dig), PLACE[side], pit))
        elif ev.kind == 'note':
            ev.pitches = [parse_pitch(p)]
        if pending_tempo:
            ev.tempo, pending_tempo = pending_tempo, None
        parse_suffix(ev, suf, tk)
        cur['events'].append(ev)
    if cur['events'] or cur['cmds']:
        measures.append(cur)
    if pending_tempo:
        raise ValueError('dangling \\tempo')
    return measures


def parse_suffix(ev: Ev, suf: str, tk: str):
    pos = 0
    while pos < len(suf):
        for kind, rx in SUFFIX:
            m = rx.match(suf, pos)
            if m:
                break
        else:
            raise ValueError(f'unparsed suffix {suf[pos:]!r} in token {tk!r}')
        pos = m.end()
        if kind == 'words':
            ev.words.append((m.group(2), PLACE[m.group(1)]))
        elif kind == 'script':
            ev.marks.append((m.group(2), PLACE[m.group(1)]))
        elif kind == 'pedal':
            ev.pedal.append('start' if m.group(1) == 'On' else 'stop')
        elif kind == 'arpeggio':
            ev.arpeggio = True
        elif kind == 'wedge':
            ev.wedges.append({'<': 'crescendo', '>': 'diminuendo', '!': 'stop'}[m.group(1)])
        elif kind == 'dyn':
            ev.dynamics.append(m.group(1))
        elif kind == 'artic':
            ev.marks.append((ARTIC_SHORT[m.group(2)], PLACE[m.group(1)]))
        elif kind == 'finger':
            if ev.kind != 'note' or len(ev.pitches) != 1:
                raise ValueError(f'fingering postfix only on single notes: {tk!r}')
            ev.fingering.append((int(m.group(2)), PLACE[m.group(1)], None))
        elif kind == 'tie':
            ev.tie_start = set(ev.pitches)
        elif kind == 'slur':
            if m.group(0) == '(':
                ev.slur_start = True
            else:
                ev.slur_stop = True
        elif kind == 'beam':
            if m.group(0) == '[':
                ev.beam_start = True
            else:
                ev.beam_stop = True
    ev.pedal.sort(key=lambda x: 0 if x == 'stop' else 1)


# ---------------------------------------------------------------- chord-symbol DSL

CHORD = re.compile(r'^(?P<r>[A-G])(?P<ra>#|b)?(?P<k>m7b5|maj7|dim7|sus4|sus2|aug|dim|m7|m6|m|7|6|9)?'
                   r'(?:/(?P<b>[A-G])(?P<ba>#|b)?)?(?::(?P<d>\d+))?$')
KIND = {None: 'major', 'm': 'minor', '7': 'dominant', 'maj7': 'major-seventh', 'm7': 'minor-seventh',
        'dim': 'diminished', 'aug': 'augmented', 'm7b5': 'half-diminished', 'sus4': 'suspended-fourth',
        'sus2': 'suspended-second', '6': 'major-sixth', 'm6': 'minor-sixth', '9': 'dominant-ninth',
        'dim7': 'diminished-seventh'}
KIND_INTERVALS = {'major': (0, 4, 7), 'minor': (0, 3, 7), 'dominant': (0, 4, 7, 10),
                  'major-seventh': (0, 4, 7, 11), 'minor-seventh': (0, 3, 7, 10), 'diminished': (0, 3, 6),
                  'augmented': (0, 4, 8), 'half-diminished': (0, 3, 6, 10), 'suspended-fourth': (0, 5, 7),
                  'suspended-second': (0, 2, 7), 'major-sixth': (0, 4, 7, 9), 'minor-sixth': (0, 3, 7, 9),
                  'dominant-ninth': (0, 4, 7, 10, 14), 'diminished-seventh': (0, 3, 6, 9)}
ALT = {None: 0, '#': 1, 'b': -1}


def parse_chords(text: str, score: Score):
    """'C:2 G7:2 | Am7 | - | ...' (':n' = quarters, default = rest of bar, '-' = no chord)"""
    offs = score.offsets()
    out = []
    bars = [b.split() for b in text.split('|')]
    if bars and not bars[-1]:
        bars.pop()
    if len(bars) != len(score.measures):
        raise ValueError(f'chord bars {len(bars)} != measures {len(score.measures)}')
    for i, toks in enumerate(bars):
        t = offs[i]
        end = offs[i] + score.measures[i].dur
        for k, tk in enumerate(toks):
            if tk.startswith('-'):
                d = F(int(tk[2:])) if tk.startswith('-:') else end - t
                t += d
                continue
            m = CHORD.match(tk)
            if not m:
                raise ValueError(f'bad chord {tk!r}')
            d = F(int(m.group('d'))) if m.group('d') else end - t
            c = {'t': t, 'dur': d, 'root': (m.group('r'), ALT[m.group('ra')]), 'kind': KIND[m.group('k')],
                 'suffix': m.group('k') or '', 'bass': (m.group('b'), ALT[m.group('ba')]) if m.group('b') else None,
                 'label': tk.split(':')[0]}
            out.append(c)
            t += d
        if t != end:
            raise ValueError(f'chord bar {i + 1}: durations {t - offs[i]} != {score.measures[i].dur}')
    return out


# ---------------------------------------------------------------- score building

def build_score(title, composer, parts, time=(4, 4), key=(0, 'major'), time_symbol=None, subtitle='',
                groups=None, chords=None, rights='', pedal_style='text', mark_format='box-letters'):
    """parts: [{'id','name','abbr','staves': [{'clef', 'music'}]}];  chords: {'part': id, 'text': ...}"""
    sc = Score(title=title, composer=composer, subtitle=subtitle, rights=rights, pedal_style=pedal_style, mark_format=mark_format)
    parsed = []
    for pd in parts:
        p = Part(pd['id'], pd['name'], pd.get('abbr', ''))
        for k, sd in enumerate(pd['staves']):
            st = Staff(id=f"{pd['id']}s{k + 1}", clef=sd['clef'], voice=str(k + 1), number=k + 1)
            p.staves.append(st)
            parsed.append((st, parse_staff(sd['music'])))
        sc.parts.append(p)
    nm = {len(ms) for _, ms in parsed}
    if len(nm) != 1:
        raise ValueError(f'staves have different measure counts: {[(s.id, len(m)) for s, m in parsed]}')
    nm = nm.pop()
    cur_time = time
    letter = 0
    for i in range(nm):
        cmds = {}
        for st, ms in parsed:
            for k, v in ms[i]['cmds'].items():
                if k in cmds and cmds[k] != v:
                    raise ValueError(f'bar {i + 1}: conflicting {k}')
                cmds[k] = v
        if 'time' in cmds:
            cur_time = cmds['time']
        nominal = F(cur_time[0] * 4, cur_time[1])
        mi = Measure(number=i + 1, dur=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
        if 'time' in cmds:
            mi.time, mi.time_symbol = cmds['time'], cmds.get('time_symbol')
        if 'key' in cmds:
            mi.key = cmds['key']
        if cmds.get('mark'):
            label = str(letter + 1) if mark_format.endswith('numbers') else 'ABCDEFGHJKLMNOPQRSTUVWXYZ'[letter]   # LilyPond letters skip I
            letter += 1
            mi.mark = label
        mi.new_system = bool(cmds.get('new_system'))
        mi.new_page = bool(cmds.get('new_page'))
        mi.right_bar = cmds.get('bar')
        sc.measures.append(mi)
    sc.measures[-1].right_bar = sc.measures[-1].right_bar or 'final'
    for st, ms in parsed:
        for i, mm in enumerate(ms):
            evs = mm['events']
            for ev in evs:
                if ev.measure_rest:
                    ev.dur = sc.measures[i].dur
            tot = sum((e.dur for e in evs), F(0))
            if tot != sc.measures[i].dur:
                raise ValueError(f'{st.id} bar {i + 1}: {tot} quarters != {sc.measures[i].dur}')
            st.measures.append(evs)
    link(sc)
    if chords:
        sc.part(chords['part']).chords = parse_chords(chords['text'], sc)
    sc.groups = groups or []
    compute_accidentals(sc)
    return sc


def link(sc: Score):
    """ties: mark stops; hairpins: implicit stops; check balanced spans"""
    for p, st in sc.staves():
        prev = None
        open_wedge = False
        open_slur = False
        open_beam = False
        pedal_down = False
        for i, t, ev in staff_events(sc, st):
            if ev.kind == 'clef':
                continue
            if ev.kind == 'note' and prev is not None and prev.tie_start:
                ev.tie_stop = {x for x in ev.pitches if x in prev.tie_start}
                if ev.tie_stop != prev.tie_start:
                    raise ValueError(f'{st.id} bar {i + 1}: tie to different pitch')
            elif prev is not None and prev.tie_start:
                raise ValueError(f'{st.id} bar {i + 1}: tie into a rest')
            prev = ev if ev.kind == 'note' else None
            # hairpins
            ws = []
            if open_wedge and (ev.dynamics or any(w in ('crescendo', 'diminuendo') for w in ev.wedges)) \
                    and 'stop' not in ev.wedges:
                ws.append('stop-implicit')
                open_wedge = False
            for w in ev.wedges:
                if w == 'stop':
                    if not open_wedge:
                        raise ValueError(f'{st.id} bar {i + 1}: \\! without hairpin')
                    open_wedge = False
                    ws.insert(0, 'stop')
                else:
                    open_wedge = True
                    ws.append(w)
            ev.wedges = ws
            # slurs / beams / pedal
            if ev.slur_stop:
                if not open_slur:
                    raise ValueError(f'{st.id} bar {i + 1}: slur stop without start')
                open_slur = False
            if ev.slur_start:
                if open_slur:
                    raise ValueError(f'{st.id} bar {i + 1}: nested slur')
                open_slur = True
            if ev.beam_start:
                if open_beam:
                    raise ValueError(f'{st.id} bar {i + 1}: nested beam')
                open_beam = True
            if ev.beam_stop:
                if not open_beam:
                    raise ValueError(f'{st.id} bar {i + 1}: beam stop without start')
                open_beam = False
            for pd in ev.pedal:
                if pd == 'stop':
                    if not pedal_down:
                        raise ValueError(f'{st.id} bar {i + 1}: pedal up without down')
                    pedal_down = False
                else:
                    if pedal_down:
                        raise ValueError(f'{st.id} bar {i + 1}: pedal down twice')
                    pedal_down = True
            if ev.fingering and ev.kind != 'note':
                raise ValueError('fingering on a rest')
        if open_wedge or open_slur or open_beam or pedal_down or (prev is not None and prev.tie_start):
            raise ValueError(f'{st.id}: unterminated span (wedge={open_wedge} slur={open_slur} beam={open_beam} '
                             f'pedal={pedal_down})')


SHARP_ORDER = 'FCGDAEB'
ACC_NAME = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}


def key_alters(fifths):
    alt = {s: 0 for s in STEPS}
    if fifths > 0:
        for s in SHARP_ORDER[:fifths]:
            alt[s] = 1
    elif fifths < 0:
        for s in SHARP_ORDER[::-1][:-fifths]:
            alt[s] = -1
    return alt


def compute_accidentals(sc: Score):
    """LilyPond 2.24 'default' accidental style for one voice per staff: an accidental is
    printed when the alteration differs from the key / from an earlier note of the same
    step and octave in the bar; tie continuations print nothing (pieces avoid ties across
    barlines on altered notes)."""
    for p, st in sc.staves():
        for i, evs in enumerate(st.measures):
            kalt = key_alters(sc.key_at(i)[0])
            state = {}
            for ev in evs:
                if ev.kind != 'note':
                    continue
                ev.accidentals = {}
                new = {}
                for pit in ev.pitches:
                    step, alter, octv = pit
                    cur = state.get((step, octv), kalt[step])
                    if pit in ev.tie_stop:
                        if i > 0 and alter != kalt[step] and ev is evs[0]:
                            raise ValueError(f'{st.id} bar {i + 1}: altered tie across barline (avoid)')
                        new[(step, octv)] = alter
                        continue
                    if alter != cur:
                        ev.accidentals[pit] = ACC_NAME[alter]
                    new[(step, octv)] = alter
                state.update(new)
