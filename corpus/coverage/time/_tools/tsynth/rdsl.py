"""[coverage/time copy of challenge/rhythm rsynth/rdsl.py; nested \\tuplet groups allowed]
Rhythm DSL: LilyPond-like note text (absolute pitch) -> score model.

Voice text tokens (whitespace separated; chords <c' e'> may contain spaces):
  |                         bar line (all voices must have the same number of bars and
                            the same length in every bar; use s (spacer) where a voice is silent)
  \\time 3/4   \\time 4/4:common   \\time 2/2:cut    (master voice, at bar start)
  \\key bes:major  \\key e:minor                       (master voice, at bar start)
  \\mark:A                   rehearsal mark (master)
  \\words:Allegro_moderato   tempo words (master; '_' -> space)
  \\clef bass
  \\tuplet 3/2 { ... }       tuplet;  \\tuplet* 3/2 { ... } = implied tuplet (no number/bracket)
  \\grace { ... }  \\sgrace { ... }  \\acc x  \\app x  \\acc { ... }   grace notes
  notes: pitch[dur][dots][suffixes]   r = rest, s = spacer, R = whole-bar rest, R1*8 = multi-bar rest
  durations: \\breve 1 2 4 8 16 32 64 (sticky incl. dots, as in LilyPond)
  suffixes: ~ [ ] ( ) \\fermata -. -> -- \\p \\mf ...   chord ties: <c'~ e'> or <c' e'>~
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, MeasureInfo, Part, Score, VoiceDef, display_ql, renumber

DUR_TYPE = {'\\breve': 'breve', '1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th',
            '32': '32nd', '64': '64th'}
TOK = re.compile(r"^(?P<p><[^>]+>|[a-g](?:isis|eses|is|es)?[',]*|r|s|R)"
                 r"(?P<d>\\breve|128|64|32|16|8|4|2|1)?(?P<dots>\.*)(?:\*(?P<mult>\d+))?(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es)?(?P<o>[',]*)(?P<tie>~?)$")
ACC = {None: 0, 'is': 1, 'es': -1, 'isis': 2, 'eses': -2}
KEYS_MAJ = {'c': 0, 'g': 1, 'd': 2, 'a': 3, 'e': 4, 'b': 5, 'fis': 6, 'cis': 7, 'f': -1, 'bes': -2, 'ees': -3,
            'aes': -4, 'des': -5, 'ges': -6, 'ces': -7}
KEYS_MIN = {'a': 0, 'e': 1, 'b': 2, 'fis': 3, 'cis': 4, 'gis': 5, 'dis': 6, 'ais': 7, 'd': -1, 'g': -2, 'c': -3,
            'f': -4, 'bes': -5, 'ees': -6, 'aes': -7}
SUFFIXES = [':h', '\\fermata', '~', '[', ']', '(', ')', '-.', '->', '--']
DYN = re.compile(r'^\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf)(?![a-z])')
GRACE_KW = {'\\grace': 'grace', '\\sgrace': 'slashed', '\\acc': 'acciaccatura', '\\app': 'appoggiatura'}


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(f'bad pitch {t!r}')
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    return (m.group('s').upper(), ACC[m.group('a')], octv), bool(m.group('tie'))


def tokenize(text):
    text = re.sub(r'<([a-g][^<>]*)>', lambda m: '<' + m.group(1).replace(' ', '\x01') + '>', text)
    text = text.replace('|', ' | ').replace('{', ' { ').replace('}', ' } ')
    return [t.replace('\x01', ' ') for t in text.split()]


class VoiceParse:
    def __init__(self):
        self.measures = []      # list of dict(events, time, sym, key, mark, words)
        self.cur = self._new()

    @staticmethod
    def _new():
        return {'events': [], 'time': None, 'sym': None, 'key': None, 'mark': None, 'words': None}


def parse_voice(text):
    toks = tokenize(text)
    vp = VoiceParse()
    cur = vp.cur
    last_d, last_dots = '4', 0
    stack = []            # ('tuplet', ratio, hidden, start_idx) | ('grace', kind, start_idx)
    single_grace = None   # grace kind applying to the next note token only
    pending_grace_stop = False
    i = 0

    def close_measure():
        nonlocal cur
        if stack:
            raise ValueError('bar line inside tuplet/grace group')
        vp.measures.append(cur)
        cur = VoiceParse._new()

    while i < len(toks):
        tk = toks[i]
        i += 1
        if tk == '|':
            close_measure()
            continue
        if tk == '\\partial':     # informational only: a short first bar is a pickup
            continue
        if tk == '\\time':
            spec = toks[i]
            i += 1
            frac, _, sym = spec.partition(':')
            n, d = frac.split('/')
            cur['time'], cur['sym'] = (int(n), int(d)), (sym or None)
            continue
        if tk == '\\key':
            spec = toks[i]
            i += 1
            ton, _, mode = spec.partition(':')
            mode = mode or 'major'
            cur['key'] = ((KEYS_MIN if mode == 'minor' else KEYS_MAJ)[ton], mode)
            continue
        if tk.startswith('\\mark:'):
            cur['mark'] = tk[6:].replace('_', ' ')
            continue
        if tk.startswith('\\words:'):
            cur['words'] = tk[7:].replace('_', ' ')
            continue
        if tk == '\\clef':
            cur['events'].append(Event('clef', F(0), clef=toks[i]))
            i += 1
            continue
        if tk in ('\\tuplet', '\\tuplet*'):
            a, n = toks[i].split('/')
            assert toks[i + 1] == '{', 'tuplet needs {'
            i += 2
            stack.append(('tuplet', (int(a), int(n)), tk.endswith('*'), len(cur['events'])))
            continue
        if tk in GRACE_KW:
            if toks[i] == '{':
                i += 1
                stack.append(('grace', GRACE_KW[tk], len(cur['events'])))
            else:
                single_grace = GRACE_KW[tk]
            continue
        if tk == '}':
            top = stack.pop()
            evs = [e for e in cur['events'][top[-1]:] if e.kind in ('note', 'rest')]
            if not evs:
                raise ValueError('empty group')
            if top[0] == 'tuplet':
                lvl = sum(1 for fr in stack if fr[0] == 'tuplet')     # depth of the closed group
                evs[0].tuplet_start = True
                evs[-1].tuplet_stop = True
                evs[0].tup_starts.append(lvl)
                evs[-1].tup_stops.append(lvl)
            else:
                if top[1] in ('acciaccatura', 'appoggiatura'):
                    evs[0].grace_slur_start = True
                    pending_grace_stop = True
            continue
        m = TOK.match(tk)
        if not m:
            raise ValueError(f'bad token {tk!r}')
        p, d, dots, mult, suf = m.group('p'), m.group('d'), m.group('dots'), m.group('mult'), m.group('suf')
        if p == 'R' and not d:
            # whole-bar rest whose length comes from the time signature (filled in by build_score)
            n = int(mult or 1)
            ev = Event('rest', F(-1), measure_rest=True, dtype=None)
            ev.multirest = n if n > 1 else 0
            _suffixes(ev, suf, tk)
            cur['events'].append(ev)
            for _ in range(n - 1):
                close_measure()
                cur['events'].append(Event('rest', F(-1), measure_rest=True, multirest_cont=True))
            continue
        if d:
            last_d, last_dots = d, len(dots)
        elif dots:
            raise ValueError(f'dots without duration in {tk!r}')
        dtype, nd = DUR_TYPE[last_d], last_dots
        base = display_ql(dtype, nd)
        tup = None
        hidden = False
        in_grace = None
        levels = []
        for fr in stack:
            if fr[0] == 'tuplet':
                levels.append(fr[1])
                hidden = hidden or fr[2]
            else:
                in_grace = fr[1]
        if levels:
            a_, n_ = 1, 1
            for a0, n0 in levels:
                a_, n_ = a_ * a0, n_ * n0
            tup = (a_, n_)
            if len(levels) > 1 and hidden:
                raise ValueError('hidden nested tuplets not supported')
        if single_grace:
            in_grace, single_grace_now = single_grace, True
        else:
            single_grace_now = False
        dur = base * tup[1] / tup[0] if tup else base
        if p == 's':
            cur['events'].append(Event('space', dur))
            continue
        if p == 'R':
            n = int(mult or 1)
            ev = Event('rest', base, measure_rest=True, dtype=None)
            ev.multirest = n if n > 1 else 0
            _suffixes(ev, suf, tk)
            cur['events'].append(ev)
            for _ in range(n - 1):
                close_measure()
                cur['events'].append(Event('rest', base, measure_rest=True, multirest_cont=True))
            continue
        ev = Event('rest' if p == 'r' else 'note', dur, dtype=dtype, dots=nd)
        if tup:
            ev.tuplet, ev.tuplet_hidden = tup, hidden
            ev.tup_levels = list(levels)
        if p.startswith('<'):
            for x in p[1:-1].split():
                pit, tie = parse_pitch(x)
                ev.pitches.append(pit)
                if tie:
                    ev.tie_start.add(pit)
        elif p != 'r':
            pit, _ = parse_pitch(p)
            ev.pitches = [pit]
        _suffixes(ev, suf, tk)
        if in_grace:
            if ev.kind != 'note':
                raise ValueError('grace rest')
            ev.grace = in_grace
            ev.dur = F(0)
            if single_grace_now:
                single_grace = None
                if in_grace in ('acciaccatura', 'appoggiatura'):
                    ev.grace_slur_start = True
                    pending_grace_stop = True
        elif pending_grace_stop:
            if ev.kind != 'note':
                raise ValueError('grace must be followed by a note')
            ev.grace_slur_stop = True
            pending_grace_stop = False
        cur['events'].append(ev)
    if cur['events'] or cur['time']:
        vp.measures.append(cur)
    if stack:
        raise ValueError('unclosed group')
    _link_ties(vp.measures)
    return vp.measures


def _suffixes(ev, suf, tk):
    s = suf
    while s:
        m = DYN.match(s)
        if m:
            ev.dynamics.append(m.group(1))
            s = s[m.end():]
            continue
        for x in SUFFIXES:
            if s.startswith(x):
                if x == ':h':
                    ev.multirest_hbar = True
                elif x == '~':
                    ev.tie_start = set(ev.pitches)
                elif x == '[':
                    ev.beam_start = True
                elif x == ']':
                    ev.beam_stop = True
                elif x == '(':
                    ev.slur_start = 1
                elif x == ')':
                    ev.slur_stop = 1
                elif x == '\\fermata':
                    ev.fermata = True
                elif x == '-.':
                    ev.artic.append('staccato')
                elif x == '->':
                    ev.artic.append('accent')
                elif x == '--':
                    ev.artic.append('tenuto')
                s = s[len(x):]
                break
        else:
            raise ValueError(f'bad suffix {s!r} in {tk!r}')


def _link_ties(measures):
    prev = None
    for mm in measures:
        for ev in mm['events']:
            if ev.kind == 'clef' or ev.grace:
                continue
            if prev is not None and prev.tie_start:
                if ev.kind != 'note' or not prev.tie_start <= set(ev.pitches):
                    raise ValueError(f'tie without matching next note: {prev.pitches} -> {ev.pitches}')
                ev.tie_stop = set(prev.tie_start)
            prev = ev if ev.kind == 'note' else None


def build_score(spec):
    """spec: dict(title, composer, lyricist, rights, parts=[dict(id, name, abbr, instrument,
    staves, clefs, voices=[dict(key, staff, music)])], systems=[bars per system],
    pages=[systems per page], groups=[...])"""
    parsed = []
    for p in spec['parts']:
        for v in p['voices']:
            parsed.append((p['id'], v['key'], parse_voice(v['music'])))
    nms = {(a, b): len(m) for a, b, m in parsed}
    nm = len(parsed[0][2])
    if any(n != nm for n in nms.values()):
        raise ValueError(f'bar counts differ: {nms}')
    master = parsed[0][2]
    sc = Score(title=spec.get('title', ''), composer=spec.get('composer', ''), lyricist=spec.get('lyricist', ''),
               arranger=spec.get('arranger', ''), rights=spec.get('rights', ''), source=spec.get('source', ''))
    time, sym = (4, 4), None
    for i in range(nm):
        mm = master[i]
        if mm['time']:
            time, sym = mm['time'], mm['sym']
        nominal = F(time[0] * 4, time[1])
        for a, b, m in parsed:
            for e in m[i]['events']:
                if e.dur == -1:
                    e.dur = nominal
        lens = {(a, b): sum((e.dur for e in m[i]['events']), F(0)) for a, b, m in parsed}
        dur = max(lens.values())
        bad = {k: v for k, v in lens.items() if v != dur}
        if bad:
            raise ValueError(f'bar {i}: voice lengths differ {lens}')
        if 0 < i < nm - 1 and dur != nominal:
            raise ValueError(f'bar {i}: length {dur} != {nominal}')
        if dur > nominal:
            raise ValueError(f'bar {i}: overfull {dur} > {nominal}')
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if mm['time'] or i == 0:
            mi.time, mi.time_symbol = time, sym
        if mm['key'] or i == 0:
            mi.key = mm['key'] or spec.get('key', (0, 'major'))
        mi.rehearsal, mi.words = mm['mark'], mm['words']
        if i == 0:
            mi.implicit = dur < nominal
        for a, b, m in parsed[1:]:
            if m[i]['time'] and m[i]['time'] != mm['time']:
                raise ValueError(f'bar {i}: time signature only in master voice')
        sc.measures.append(mi)
    sc.measures[-1].right_bar = 'final'
    for p in spec['parts']:
        part = Part(id=p['id'], name=p['name'], abbr=p.get('abbr', ''), instrument=p.get('instrument', 'voice'),
                    staves=p.get('staves', 1), clefs=list(p.get('clefs', ['treble'])))
        part.voices = [VoiceDef(v['key'], v.get('staff', 1)) for v in p['voices']]
        part.measures = [dict() for _ in range(nm)]
        for a, b, m in parsed:
            if a == p['id']:
                for i in range(nm):
                    part.measures[i][b] = m[i]['events']
        sc.parts.append(part)
    # forced breaks
    systems = spec.get('systems')
    if systems:
        assert sum(systems) == nm, (sum(systems), nm)
        starts = []
        k = 0
        for n in systems:
            starts.append(k)
            k += n
        pages = spec.get('pages') or [len(systems)]
        assert sum(pages) == len(systems)
        page_starts = set()
        k = 0
        for n in pages:
            page_starts.add(starts[k])
            k += n
        for j, st in enumerate(starts):
            if st == 0:
                continue
            if st in page_starts:
                sc.measures[st].new_page = True
            else:
                sc.measures[st].new_system = True
    sc.groups = spec.get('groups', [])
    renumber(sc)
    return sc
