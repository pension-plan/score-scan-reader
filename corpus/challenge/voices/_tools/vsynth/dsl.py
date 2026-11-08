"""LilyPond-like note DSL for self-authored pieces (absolute pitch).

  "f'4 | a'2 bes'4 | c''2 a'4\\nostem | ..."

tokens: pitch [a-g](is|es)*[',]* or r (rest) or s (invisible spacer: empty voice) or R (full-bar rest, e.g. R2. in 3/4); duration 1 2 4 8 16 (sticky) +
dots; chords <c' e' g'>4.  Suffixes on a note/rest token (no spaces):
  ~            tie to the next note of the same voice
  ( )          slur start / stop
  \\fermata -. -> \\p \\mf ...
  \\hide        note is in the truth but engraved as a spacer (a2 / unis.):
               an identical printed note must exist in another voice of the staff
  \\nostem      unison drawn with one head and one stem (this voice's stem omitted)
  ^"a+2" _"div."   printed italic words above/below ('+' = space); also truth <words>
Stand-alone tokens (attach to the following event):
  @upper @lower @<staffid>   \\change Staff = "<id>"
  @v0 @v1 @v2 @v3 @v4        \\oneVoice / \\voiceOne ...
  @raw:<lilypond>            raw code, '+' = space
'|' separates measures.  Measure lengths are checked by build_part/assemble.
(Extended copy of corpus/synthetic/_tools/synth/dsl.py.)
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, MeasureInfo, Part, Score, VoiceDef, display_ql, renumber

DUR_TYPE = {'1': 'whole', '2': 'half', '4': 'quarter', '8': 'eighth', '16': '16th', '32': '32nd'}
TOK = re.compile(r"^(?P<p>(?:<[^>]+>)|[a-g](?:isis|eses|is|es|s)?[',]*|r|s|R)(?P<d>1|2|4|8|16|32)?(?P<dots>\.*)(?P<suf>.*)$")
PIT = re.compile(r"^(?P<s>[a-g])(?P<a>isis|eses|is|es|s)?(?P<o>[',]*)$")
ACC = {None: 0, 'is': 1, 'es': -1, 's': -1, 'isis': 2, 'eses': -2}
ROLE = {'0': '\\oneVoice', '1': '\\voiceOne', '2': '\\voiceTwo', '3': '\\voiceThree', '4': '\\voiceFour'}


def parse_pitch(t):
    m = PIT.match(t)
    if not m:
        raise ValueError(t)
    o = m.group('o')
    octv = 3 + o.count("'") - o.count(',')
    return (m.group('s').upper(), ACC[m.group('a')], octv)


def parse_voice(text):
    """-> list of measures (list of Event)."""
    measures = []
    cur = []
    last_d, last_dots = '4', 0
    pending_raw = []
    text = re.sub(r'<([^>]*)>', lambda m: '<' + '_'.join(m.group(1).split()) + '>', text)
    text = text.replace('|', ' | ')
    for tk in text.split():
        if tk == '|':
            measures.append(cur)
            cur = []
            continue
        if tk.startswith('@'):
            body = tk[1:]
            if body.startswith('raw:'):
                pending_raw.append(body[4:].replace('+', ' '))
            elif body.startswith('v') and body[1:] in ROLE:
                pending_raw.append(ROLE[body[1:]])
            else:
                pending_raw.append(f'\\change Staff = "{body}"')
            continue
        m = TOK.match(tk)
        if not m:
            raise ValueError(f'bad token {tk!r}')
        p, d, dots, suf = m.group('p'), m.group('d'), m.group('dots'), m.group('suf')
        if d:
            last_d, last_dots = d, len(dots)
        elif dots:
            last_dots = len(dots)
        dtype = DUR_TYPE[last_d]
        nd = last_dots
        kind = {'r': 'rest', 's': 'space', 'R': 'rest'}.get(p, 'note')
        ev = Event(kind, display_ql(dtype, nd), dtype=dtype, dots=nd)
        if p == 'R':
            ev.measure_rest = True
        if p.startswith('<'):
            ev.pitches = [parse_pitch(x) for x in p[1:-1].split('_')]
        elif p not in ('r', 's', 'R'):
            ev.pitches = [parse_pitch(p)]
        for place, txt in re.findall(r'([\^_])"([^"]*)"', suf):
            ev.words.append(('above' if place == '^' else 'below', txt.replace('+', ' ')))
        suf = re.sub(r'([\^_])"([^"]*)"', '', suf)
        if '~' in suf:
            ev.tie_start = set(ev.pitches)
        if '\\fermata' in suf:
            ev.fermata = True
        if '\\hide' in suf:
            ev.hidden = True
        if '\\nostem' in suf:
            ev.nostem = True
        if '(' in suf:
            ev.slur_start = 1
        if ')' in suf:
            ev.slur_stop = 1
        if '-.' in suf:
            ev.artic.append('staccato')
        if '->' in suf:
            ev.artic.append('accent')
        if '--' in suf:
            ev.artic.append('tenuto')
        for dyn in re.findall(r'\\(ppp|pp|p|mp|mf|ff|fff|f|sfz|sf)(?![a-z])', suf):
            ev.dynamics.append(dyn)
        rest_suf = re.sub(r'\\(fermata|hide|nostem|ppp|pp|p|mp|mf|ff|fff|f|sfz|sf)(?![a-z])|[~()]|-\.|->|--', '', suf)
        if rest_suf.strip():
            raise ValueError(f'unparsed suffix {rest_suf!r} in {tk!r}')
        ev.raw_before = pending_raw
        pending_raw = []
        cur.append(ev)
    if cur:
        measures.append(cur)
    if pending_raw:
        raise ValueError('dangling @ directive at end of voice')
    prev = None
    for mm in measures:
        for ev in mm:
            if ev.kind != 'note':
                prev = None
                continue
            if prev is not None and prev.tie_start:
                ev.tie_stop = {p for p in ev.pitches if p in prev.tie_start}
            prev = ev
    return measures


def assemble(parts_spec, time=(4, 4), key=(0, 'major'), time_symbol=None, pickup=None, final_bar=True,
             time_changes=None):
    """parts_spec: list of dicts {id, name, abbr, instrument, staves, clefs, voices: [(vkey, staff, dsl)]}.
    Every voice must fill every measure exactly (pickup = first measure length in quarters)."""
    parsed = {}
    for ps in parts_spec:
        for vkey, staff, txt in ps['voices']:
            parsed[(ps['id'], vkey)] = parse_voice(txt)
    lens = {k: len(v) for k, v in parsed.items()}
    nm = max(lens.values())
    if any(l != nm for l in lens.values()):
        raise ValueError(f'measure count mismatch {lens}')
    time_changes = time_changes or {}
    sc = Score()
    cur_time = time
    for i in range(nm):
        if i in time_changes:
            cur_time = time_changes[i]
        nominal = F(cur_time[0] * 4, cur_time[1])
        dur = nominal
        if i == 0 and pickup is not None:
            dur = F(pickup)
        mi = MeasureInfo(number=i + 1, dur=dur, nominal=nominal)
        if i == 0:
            mi.time, mi.time_symbol, mi.key = time, time_symbol, key
            mi.implicit = dur < nominal
        elif i in time_changes:
            mi.time = time_changes[i]
        for k, mm in parsed.items():
            tot = sum((e.dur for e in mm[i]), F(0))
            if tot != dur:
                raise ValueError(f'{k} measure {i}: {tot} quarters, expected {dur}')
        sc.measures.append(mi)
    if final_bar:
        sc.measures[-1].right_bar = 'final'
    for ps in parts_spec:
        p = Part(id=ps['id'], name=ps.get('name', ''), abbr=ps.get('abbr', ''),
                 instrument=ps.get('instrument', 'voice'), staves=ps.get('staves', 1),
                 clefs=list(ps.get('clefs', ['treble'])))
        p.voices = [VoiceDef(vkey, staff) for vkey, staff, _ in ps['voices']]
        for i in range(nm):
            p.measures.append({vkey: parsed[(ps['id'], vkey)][i] for vkey, _, _ in ps['voices']})
        sc.parts.append(p)
    renumber(sc)
    return sc
