"""LilyPond-like note DSL (absolute pitch) for the coverage/perf generator.

  "g'4 a'8[ b'] c''4^\"dolce\" d''\\fermata | <c'-1 e'-3 g'-5>2\\p\\< r4 e'4\\! | R1"

Measures are separated by '|'.  Event tokens:
  pitch  [a-g](isis|eses|is|es)?[',]*  then optional ! (forced accidental) or ? (cautionary)
  r rest | s spacer (no truth) | R full-measure rest | <...> chord (each note may carry -N fingering, ! ?)
  duration 1 2 4 8 16 32 64 \\breve (sticky) + dots ;  :N single-note tremolo (e.g. c'2:32)
Suffixes:
  ~ tie   ( ) slur   [ ] manual beam
  -. staccato  -! staccatissimo  -> accent  -- tenuto  -^ marcato  -N fingering (single note)
  \\fermata \\trill \\mordent \\turn \\arpeggio \\breathe
  \\pp \\p \\mp \\mf \\f \\ff \\sfz ...   \\< \\> \\!   \\sustainOn \\sustainOff
  ^"text" / _"text" italic words ('_' inside the quotes = space), ^!"text" bold
Standalone tokens:
  \\g / \\gs   next note is a grace note (plain / slashed); consecutive ones form one group
  \\tup3/2 ... \\tupend      tuplet
  \\clef=bass  \\ottava=1|-1|2|0  \\st1 \\st2 \\st0 (cross-staff / home staff)
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, display_ql

DUR_TYPE = {'\\breve': 'breve', '1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th',
            '32': '32nd', '64': '64th'}
TOK = re.compile(r"^(?P<p>(?:<[^>]+>)|[a-g](?:isis|eses|is|es)?[',]*[!?]?|r|s|R)"
                 r"(?P<d>\\breve|64|32|16|1|2|4|8)?(?P<dots>\.*)(?::(?P<trem>8|16|32|64))?(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es)?(?P<o>[',]*)(?P<f>[!?]?)(?:-(?P<fg>[0-5]))?$")
ACC = {None: 0, 'is': 1, 'es': -1, 'isis': 2, 'eses': -2}
WORDS = re.compile(r'([\^_])(!?)"([^"]*)"')
DYN = re.compile(r'\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf|fp)(?![a-zA-Z])')
ORN = {'\\trill': 'trill', '\\mordent': 'mordent', '\\turn': 'turn'}
LOG2 = {'8': 3, '16': 4, '32': 5, '64': 6}
FLAGS = {'breve': 0, 'whole': 0, 'half': 0, 'quarter': 0, 'eighth': 1, '16th': 2, '32nd': 3, '64th': 4}


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(f'bad pitch {t!r}')
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    p = (m.group('s').upper(), ACC[m.group('a')], octv)
    return p, m.group('f'), (int(m.group('fg')) if m.group('fg') else None)


def parse_voice(text):
    measures, cur = [], []
    last_d, last_dots = '4', 0
    staff = None
    tup, tup_events = None, []
    grace_next = None
    text = text.replace('|', ' | ')
    text = re.sub(r'(?<!\\)<([^<>\\]*)>', lambda m: '<' + m.group(1).strip().replace(' ', '\u00a7') + '>', text)
    for tk in text.split():
        if tk == '|':
            measures.append(cur)
            cur = []
            continue
        if tk in ('\\g', '\\gs'):
            grace_next = 'slash' if tk == '\\gs' else 'plain'
            continue
        m = re.fullmatch(r'\\st([0-3])', tk)
        if m:
            staff = int(m.group(1)) or None
            continue
        m = re.fullmatch(r'\\tup(\d+)/(\d+)', tk)
        if m:
            tup = (int(m.group(1)), int(m.group(2)))
            tup_events = []
            continue
        if tk == '\\tupend':
            if tup_events:
                tup_events[0].tuplet_start = True
                tup_events[-1].tuplet_stop = True
            tup = None
            continue
        m = re.fullmatch(r'\\clef=(\S+)', tk)
        if m:
            cur.append(Event('clef', F(0), clef=m.group(1)))
            continue
        m = re.fullmatch(r'\\ottava=(-?\d)', tk)
        if m:
            cur.append(Event('ottava', F(0), ottava=int(m.group(1))))
            continue
        m = TOK.match(tk)
        if not m:
            raise ValueError(f'bad token {tk!r}')
        p, d, dots, trem, suf = m.group('p'), m.group('d'), m.group('dots'), m.group('trem'), m.group('suf')
        if d:
            last_d, last_dots = d, len(dots)
        elif dots:
            last_dots = len(dots)
        dtype = DUR_TYPE[last_d]
        nd = last_dots
        dur = display_ql(dtype, nd)
        if tup:
            dur = dur * tup[1] / tup[0]
        kind = {'r': 'rest', 's': 'space', 'R': 'rest'}.get(p, 'note')
        ev = Event(kind, dur, dtype=dtype if kind != 'space' else None, dots=nd if kind != 'space' else 0)
        if grace_next and kind == 'note':
            ev.grace = grace_next
            ev.dur = F(0)
            grace_next = None
        if p == 'R':
            ev.measure_rest = True
        if tup and kind != 'space' and not ev.grace:
            ev.tuplet = tup
            tup_events.append(ev)
        if trem:
            ev.trem_ly = int(trem)
            ev.trem = LOG2[trem] - 2 - FLAGS[dtype]
            if ev.trem <= 0:
                raise ValueError(f'tremolo :{trem} on {dtype}')
        if p.startswith('<'):
            for x in p[1:-1].split('\u00a7'):
                if not x:
                    continue
                pit, flag, fg = parse_pitch(x)
                ev.pitches.append(pit)
                if flag == '!':
                    ev.force_acc.add(pit)
                elif flag == '?':
                    ev.caut_acc.add(pit)
                if fg is not None:
                    ev.fing[pit] = fg
        elif kind == 'note':
            pit, flag, _ = parse_pitch(p)
            ev.pitches = [pit]
            if flag == '!':
                ev.force_acc.add(pit)
            elif flag == '?':
                ev.caut_acc.add(pit)
        ev.staff = staff
        for side, bold, txt in WORDS.findall(suf):
            ev.words.append((txt.replace('_', ' '), 'above' if side == '^' else 'below', 'bold' if bold else 'italic'))
        suf = WORDS.sub('', suf)
        if '\\fermata' in suf:
            ev.fermata = True
            suf = suf.replace('\\fermata', '')
        for k, v in ORN.items():
            if k in suf:
                ev.orn.append(v)
                suf = suf.replace(k, '')
        if '\\arpeggio' in suf:
            ev.arpeggio = True
            suf = suf.replace('\\arpeggio', '')
        if '\\breathe' in suf:
            ev.breath = True
            suf = suf.replace('\\breathe', '')
        for k in re.findall(r'\\sustain(On|Off)', suf):
            ev.pedal.append('start' if k == 'On' else 'stop')
        suf = re.sub(r'\\sustain(On|Off)', '', suf)
        for k in re.findall(r'\\([<>!])', suf):
            ev.wedge.append({'<': 'crescendo', '>': 'diminuendo', '!': 'stop'}[k])
        suf = re.sub(r'\\[<>!]', '', suf)
        ev.dynamics += DYN.findall(suf)
        suf = DYN.sub('', suf)
        fm = re.search(r'-([1-5])', suf)
        if fm and kind == 'note':
            if len(ev.pitches) != 1:
                raise ValueError(f'use in-chord fingering in {tk!r}')
            ev.fing[ev.pitches[0]] = int(fm.group(1))
            suf = suf[:fm.start()] + suf[fm.end():]
        if '~' in suf:
            ev.tie_start = set(ev.pitches)
        if '(' in suf:
            ev.slur_start = 1
        if ')' in suf:
            ev.slur_stop = 1
        for sym, name in (('-.', 'staccato'), ('-!', 'staccatissimo'), ('->', 'accent'), ('--', 'tenuto'),
                          ('-^', 'strong-accent')):
            if sym in suf:
                ev.artic.append(name)
        if '[' in suf:
            ev.beam = '['
        if ']' in suf:
            ev.beam = ']'
        rest = re.sub(r'-\.|->|--|-\^|-!|[~()\[\]]', '', suf)
        if rest.strip():
            raise ValueError(f'unparsed suffix {rest!r} in token {tk!r}')
        cur.append(ev)
    if cur:
        measures.append(cur)
    # tie stops
    prev = None
    for mm in measures:
        for ev in mm:
            if ev.kind in ('clef', 'ottava'):
                continue
            if ev.kind != 'note':
                prev = None
                continue
            if ev.grace:
                continue
            if prev is not None and prev.tie_start:
                ev.tie_stop = {p for p in ev.pitches if p in prev.tie_start}
            prev = ev
    return measures


def mdur(evs):
    return sum((e.dur for e in evs), F(0))
