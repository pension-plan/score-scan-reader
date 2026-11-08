#!/usr/bin/env python3
"""Percussion coverage item (layout tag 'percussion-none'): pitched melody + unpitched percussion staves.

One self-contained generator (the csynth writers of the other families have no unpitched notes):
  piece (mini LilyPond-like DSL below) -> truth.musicxml (MusicXML 4.0: <unpitched> display positions,
  <instrument> + <midi-unpitched>, percussion clef, 1-line staff via <staff-lines>, x noteheads)
  -> xmllint XSD -> music21 parse
  -> engraving.ly (Staff for the flute, DrumStaff for the drums: custom 1-line snare style, drums-style kit)
  -> LilyPond 2.24 with the grob logger (cvlog.ly, -dinclude-settings) -> checks:
       MIDI attacks (drums on channel 10: the truth's <midi-unpitched>) == truth attacks
       every note head (staff, onset, staff position, notehead style) == truth (display-step/octave,
       <notehead>), every stem direction, beams per staff, accents, rests, time signatures, clefs
       no LilyPond warnings, planned page count
  -> count_symbols(truth) -> meta.counts / meta.symbols
  -> clean.pdf (300 dpi raster), scan.pdf (typical), scan-severe.pdf (heavy damage)

usage: /Users/d.sloane/music/.venv/bin/python corpus/coverage/percussion/_tools/build.py [--keep-work]
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction as F
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)                      # corpus/coverage/percussion
sys.path.insert(0, TOOLS)
import degrade2 as D  # noqa: E402
from count_symbols import count_all  # noqa: E402

XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
PY = '/Users/d.sloane/music/.venv/bin/python'
FAMILY = 'percussion'
CVLOG = os.path.join(TOOLS, 'cvlog.ly')
DIV = 4                                            # divisions per quarter (16th = 1)

# drum name -> (staff position in its style table, notehead (MusicXML), LilyPond style, GM MIDI note, name)
KIT = {   # LilyPond drums-style positions (ly/drumpitch-init.ly), 0 = middle line
    'bd': (-3, None, 'default', 36, 'Bass Drum'),
    'sn': (1, None, 'default', 38, 'Snare Drum'),
    'hh': (3, 'x', 'cross', 42, 'Hi-Hat'),
}
SNARE1 = {'sn': (0, None, 'default', 38, 'Snare Drum')}   # one-line staff: the note sits on the line
STEPS = 'CDEFGAB'


def pos_to_display(pos):
    """staff position (0 = middle line of a 5-line staff = B4 in treble/percussion clef) -> (step, octave)"""
    d = 4 * 7 + 6 + pos            # diatonic number of B4 + pos
    return STEPS[d % 7], d // 7


# ------------------------------------------------------------------ piece
PIECE = dict(
    id='perc01-parade-flute-snare-drumset',
    title='Village Parade - flute with snare drum (one-line staff) and drum set (percussion clef)',
    time=(4, 4), fifths=1,
    tempo=('Marziale', 112),
    parts=[
        dict(id='P1', name='Flute', abbr='Fl.', kind='pitched', staff='fl', voices={'1': (
            "d''4\\mf b'8[ c''] d''4 g' | a'8[ b' c'' a'] b'2 | c''4 a'8[ b'] c''4 fis' | g'2 r | "
            "b'8[\\< c'' d'' b'] c''4 a'\\! | d''4\\f c''8[ b'] a'2 | b'8[ a' g' a'] b'4 a' | g'2. r4")}),
        dict(id='P2', name='Snare Drum', abbr='S.D.', kind='drums', staff='sd', lines=1, table=SNARE1,
             voices={'1': (
                 "sn8[\\f sn] sn16[ sn sn sn] sn4-> sn | sn4 sn8[ sn] sn4 r | sn8[ sn] sn16[ sn sn8] sn4-> r | "
                 "sn16[ sn sn sn] sn16[ sn sn sn] sn4-> r | sn8[ sn] sn16[ sn sn sn] sn4-> sn | sn4 sn8[ sn] sn4 r | "
                 "sn8[ sn] sn16[ sn sn8] sn4-> r | sn4-> sn sn2->")}),
        dict(id='P3', name='Drum Set', abbr='D.S.', kind='drums', staff='ds', lines=5, table=KIT, voices={
            '1': ("hh8[\\mp hh <hh sn> hh] hh8[ hh <hh sn> hh] | hh8[ hh <hh sn> hh] hh8[ hh <hh sn> hh] | "
                  "hh8[ hh <hh sn> hh] hh8[ hh <hh sn> hh] | hh8[ hh <hh sn> hh] <hh sn>4 r | "
                  "hh8[ hh <hh sn> hh] hh8[ hh <hh sn> hh] | hh8[ hh <hh sn> hh] hh8[ hh <hh sn> hh] | "
                  "hh8[ hh <hh sn> hh] hh8[ hh <hh sn> hh] | hh8[ hh <hh sn> hh] <hh sn>2->"),
            '2': ("bd4 r bd r | bd4 r bd r | bd4 r bd r | bd4 bd bd r | bd4 r bd r | bd4 r bd r | "
                  "bd4 r bd r | bd4 r bd2")}),
    ],
    systems=(4,),            # measure indices starting a new system
    pages=1,
)


# ------------------------------------------------------------------ DSL
TOK = re.compile(r"<[^>]*>\S*|\S+")
NOTE = re.compile(r"^(bd|sn|hh|r|[a-g](?:is|es)?)([',]*)(\d+)?(\.*)(.*)$")


def parse_head(h):
    m = re.match(r"^([a-g])(is|es)?([',]*)$", h)
    if not m:
        return h                                    # drum name
    step = m.group(1).upper()
    alter = {'is': 1, 'es': -1}.get(m.group(2), 0)
    octave = 3 + m.group(3).count("'") - m.group(3).count(',')
    return (step, alter, octave)


def parse_voice(text):
    """-> list of measures; each measure = list of events dict(kind, dur(F quarters), heads, dots, beam, marks)"""
    measures = []
    last_dur = (4, 0)
    for mtxt in text.split('|'):
        evs = []
        for tok in TOK.findall(mtxt):
            if tok.startswith('<'):
                inner, rest = tok[1:].split('>', 1)
                heads = inner.split()
                m = re.match(r'^(\d+)?(\.*)(.*)$', rest)
                dur = (int(m.group(1)), len(m.group(2))) if m.group(1) else last_dur
                tail = m.group(3)
                kind = 'note'
            else:
                m = NOTE.match(tok)
                if not m:
                    raise ValueError(f'bad token {tok!r}')
                name, octs, d, dots, tail = m.groups()
                dur = (int(d), len(dots)) if d else last_dur
                kind = 'rest' if name == 'r' else 'note'
                heads = [] if kind == 'rest' else [name + octs]
            last_dur = dur
            base = F(4, dur[0])
            q = base * (2 - F(1, 2 ** dur[1]))
            ev = dict(kind=kind, dur=q, type=dur[0], dots=dur[1], heads=[parse_head(h) for h in heads],
                      beam=None, marks=[], dyn=None, wedge=None)
            for t in re.findall(r'\[|\]|->|\\[<>!]|\\[fmp]+', tail):
                if t == '[':
                    ev['beam'] = 'begin'
                elif t == ']':
                    ev['beam'] = 'end'
                elif t == '->':
                    ev['marks'].append('accent')
                elif t in ('\\<', '\\>'):
                    ev['wedge'] = 'crescendo' if t == '\\<' else 'diminuendo'
                elif t == '\\!':
                    ev['wedge'] = 'stop'
                else:
                    ev['dyn'] = t[1:]
            evs.append(ev)
        measures.append(evs)
    # beam continue flags
    for evs in measures:
        open_ = False
        for ev in evs:
            if ev['beam'] == 'begin':
                open_ = True
            elif ev['beam'] == 'end':
                open_ = False
            elif open_:
                ev['beam'] = 'continue'
    return measures


TYPE_NAME = {1: 'whole', 2: 'half', 4: 'quarter', 8: 'eighth', 16: '16th', 32: '32nd'}


def pitch_pos(p):
    step, alter, octave = p
    return octave * 7 + STEPS.index(step) - (4 * 7 + 6)


def midi_of(p):
    step, alter, octave = p
    return (octave + 1) * 12 + [0, 2, 4, 5, 7, 9, 11][STEPS.index(step)] + alter


def head_pos(part, h):
    return pitch_pos(h) if isinstance(h, tuple) else part['table'][h][0]


def assign_stems(part, vkey, measures):
    """explicit stem directions: drum voice 1 up / voice 2 down, one-line snare up; flute: extreme note of the
    note or beam group decides (middle line -> down)"""
    groups, cur = [], None
    for evs in measures:
        for ev in evs:
            if ev['kind'] != 'note' or ev['type'] == 1:
                continue
            if ev['beam'] == 'begin':
                cur = [ev]
                groups.append(cur)
            elif ev['beam'] in ('continue', 'end') and cur is not None:
                cur.append(ev)
                if ev['beam'] == 'end':
                    cur = None
            else:
                groups.append([ev])
    for g in groups:
        if part['kind'] == 'drums':
            d = 'down' if (len(part['voices']) > 1 and vkey == '2') else 'up'
        else:
            ps = [head_pos(part, h) for ev in g for h in ev['heads']]
            hi, lo = max(ps), min(ps)
            d = 'down' if hi >= -lo else 'up'
            if hi < 0 and lo < 0:
                d = 'up'
            if hi >= 0 and abs(hi) >= abs(lo):
                d = 'down'
        for ev in g:
            ev['stem'] = d


# ------------------------------------------------------------------ truth
def write_truth(piece, parsed, path):
    w = []
    a = w.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
      '"http://www.musicxml.org/dtds/partwise.dtd">')
    a('<score-partwise version="4.0">')
    a(f'  <work><work-title>{escape(piece["title"].split(" - ")[0])}</work-title></work>')
    a('  <identification><creator type="composer">Coverage suite (2026)</creator>'
      '<rights>CC0 1.0 - dedicated to the public domain</rights>'
      '<encoding><software>coverage suite builder (percussion family)</software>'
      '<encoding-date>2026-11-08</encoding-date></encoding></identification>')
    a('  <part-list>')
    for p in piece['parts']:
        a(f'    <score-part id="{p["id"]}"><part-name>{escape(p["name"])}</part-name>'
          f'<part-abbreviation>{escape(p["abbr"])}</part-abbreviation>')
        if p['kind'] == 'drums':
            used = sorted({h for evs in parsed[p['id']]['1'] + sum((parsed[p['id']].get(k, []) for k in p['voices'] if k != '1'), [])
                           for ev in evs for h in ev['heads']})
            for h in used:
                a(f'      <score-instrument id="{p["id"]}-{h}"><instrument-name>{p["table"][h][4]}</instrument-name>'
                  f'</score-instrument>')
            for h in used:
                a(f'      <midi-instrument id="{p["id"]}-{h}"><midi-channel>10</midi-channel>'
                  f'<midi-unpitched>{p["table"][h][3] + 1}</midi-unpitched></midi-instrument>')
        else:
            a(f'      <score-instrument id="{p["id"]}-I1"><instrument-name>{escape(p["name"])}</instrument-name>'
              f'</score-instrument>')
            a(f'      <midi-instrument id="{p["id"]}-I1"><midi-channel>1</midi-channel><midi-program>74</midi-program>'
              f'</midi-instrument>')
        a('    </score-part>')
    a('  </part-list>')
    nmeas = len(parsed[piece['parts'][0]['id']]['1'])
    mlen = F(piece['time'][0] * 4, piece['time'][1])
    for p in piece['parts']:
        a(f'  <part id="{p["id"]}">')
        vkeys = list(p['voices'])
        for mi in range(nmeas):
            a(f'    <measure number="{mi + 1}">')
            if mi in piece['systems']:
                a('      <print new-system="yes"/>')
            if mi == 0:
                a('      <attributes>')
                a(f'        <divisions>{DIV}</divisions>')
                if p['kind'] == 'pitched':
                    a(f'        <key><fifths>{piece["fifths"]}</fifths><mode>major</mode></key>')
                a(f'        <time><beats>{piece["time"][0]}</beats><beat-type>{piece["time"][1]}</beat-type></time>')
                if p['kind'] == 'pitched':
                    a('        <clef><sign>G</sign><line>2</line></clef>')
                else:
                    a('        <clef><sign>percussion</sign></clef>')
                    if p.get('lines', 5) != 5:
                        a(f'        <staff-details><staff-lines>{p["lines"]}</staff-lines></staff-details>')
                a('      </attributes>')
                if p is piece['parts'][0] and piece.get('tempo'):
                    txt, bpm = piece['tempo']
                    a('      <direction placement="above"><direction-type><words font-weight="bold">'
                      f'{escape(txt)}</words></direction-type><direction-type><metronome><beat-unit>quarter</beat-unit>'
                      f'<per-minute>{bpm}</per-minute></metronome></direction-type><sound tempo="{bpm}"/></direction>')
            for vi, vk in enumerate(vkeys):
                if vi:
                    a(f'      <backup><duration>{int(mlen * DIV)}</duration></backup>')
                for ev in parsed[p['id']][vk][mi]:
                    if ev['dyn']:
                        a(f'      <direction placement="below"><direction-type><dynamics><{ev["dyn"]}/></dynamics>'
                          f'</direction-type><voice>{vk}</voice></direction>')
                    if ev['wedge']:
                        a(f'      <direction placement="below"><direction-type><wedge type="{ev["wedge"]}"/>'
                          f'</direction-type><voice>{vk}</voice></direction>')
                    dur = int(ev['dur'] * DIV)
                    heads = ev['heads'] if ev['kind'] == 'note' else [None]
                    for k, h in enumerate(heads):
                        x = ['      <note>']
                        if k:
                            x.append('<chord/>')
                        if ev['kind'] == 'rest':
                            x.append('<rest/>')
                        elif isinstance(h, tuple):
                            step, alter, octave = h
                            x.append(f'<pitch><step>{step}</step>' + (f'<alter>{alter}</alter>' if alter else '')
                                     + f'<octave>{octave}</octave></pitch>')
                        else:
                            st, oc = pos_to_display(p['table'][h][0])
                            x.append(f'<unpitched><display-step>{st}</display-step><display-octave>{oc}'
                                     f'</display-octave></unpitched>')
                        x.append(f'<duration>{dur}</duration>')
                        if ev['kind'] == 'note' and not isinstance(h, tuple):
                            x.append(f'<instrument id="{p["id"]}-{h}"/>')
                        elif ev['kind'] == 'note':
                            x.append(f'<instrument id="{p["id"]}-I1"/>')
                        x.append(f'<voice>{vk}</voice><type>{TYPE_NAME[ev["type"]]}</type>' + '<dot/>' * ev['dots'])
                        if ev['kind'] == 'note' and ev.get('stem'):
                            x.append(f'<stem>{ev["stem"]}</stem>')
                        if ev['kind'] == 'note' and not isinstance(h, tuple) and p['table'][h][1]:
                            x.append(f'<notehead>{p["table"][h][1]}</notehead>')
                        if ev['kind'] == 'note' and ev['beam'] and k == 0:
                            x.append(f'<beam number="1">{ev["beam"]}</beam>')
                            if ev['type'] >= 16:
                                x.append(f'<beam number="2">{ev["beam2"]}</beam>')
                        elif ev['kind'] == 'note' and ev['beam'] and k > 0:
                            x.append(f'<beam number="1">{ev["beam"]}</beam>')
                            if ev['type'] >= 16:
                                x.append(f'<beam number="2">{ev["beam2"]}</beam>')
                        if ev['kind'] == 'note' and ev['marks'] and k == 0:
                            x.append('<notations><articulations>' + ''.join(f'<{m}/>' for m in ev['marks'])
                                     + '</articulations></notations>')
                        x.append('</note>')
                        a(''.join(x))
            if mi == nmeas - 1:
                a('      <barline location="right"><bar-style>light-heavy</bar-style></barline>')
            a('    </measure>')
        a('  </part>')
    a('</score-partwise>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(w) + '\n')


def assign_beam2(measures):
    """secondary beams (16ths) inside each beam group: begin/continue/end among consecutive 16ths,
    forward/backward hooks for a lone 16th"""
    for evs in measures:
        groups, cur = [], None
        for ev in evs:
            if ev['kind'] == 'note' and ev['beam'] == 'begin':
                cur = [ev]
                groups.append(cur)
            elif cur is not None and ev['kind'] == 'note' and ev['beam'] in ('continue', 'end'):
                cur.append(ev)
                if ev['beam'] == 'end':
                    cur = None
        for g in groups:
            runs, run = [], []
            for ev in g:
                if ev['type'] >= 16:
                    run.append(ev)
                else:
                    if run:
                        runs.append(run)
                    run = []
            if run:
                runs.append(run)
            for r in runs:
                if len(r) == 1:
                    r[0]['beam2'] = 'backward hook' if r[0] is g[-1] else 'forward hook'
                else:
                    for k, ev in enumerate(r):
                        ev['beam2'] = 'begin' if k == 0 else 'end' if k == len(r) - 1 else 'continue'


# ------------------------------------------------------------------ engraving
def lily_head(h):
    if isinstance(h, tuple):
        step, alter, octave = h
        n = step.lower() + {1: 'is', -1: 'es', 0: ''}[alter]
        o = octave - 3
        return n + ("'" * o if o > 0 else ',' * -o)
    return h


def write_ly(piece, parsed, path):
    L = ['\\version "2.24.0"', '#(set-global-staff-size 20)',
         '\\header {', f'  title = "{piece["title"].split(" - ")[0]}"',
         '  composer = "Coverage suite (2026)"', '  tagline = ##f', '}',
         '\\paper {', '  #(set-paper-size "a4")', '  property-defaults.fonts.serif = "TeX Gyre Schola"',
         '  top-margin = 14\\mm', '  bottom-margin = 14\\mm', '  left-margin = 18\\mm', '  right-margin = 16\\mm',
         '  ragged-bottom = ##t', '  ragged-last-bottom = ##t', '  system-system-spacing.basic-distance = #16', '}',
         '#(define snare-line-style (alist->hash-table \'((snare () #f 0))))']
    nmeas = len(parsed[piece['parts'][0]['id']]['1'])

    def voice_ly(p, vk):
        out = []
        for mi, evs in enumerate(parsed[p['id']][vk]):
            toks = []
            if mi in piece['systems']:
                toks.append('\\break')
            for ev in evs:
                s = ''
                if ev['kind'] == 'note' and ev.get('stem'):
                    s += '\\stemUp ' if ev['stem'] == 'up' else '\\stemDown '
                d = f'{ev["type"]}' + '.' * ev['dots']
                if ev['kind'] == 'rest':
                    s += 'r' + d
                elif len(ev['heads']) == 1:
                    s += lily_head(ev['heads'][0]) + d
                else:
                    s += '<' + ' '.join(lily_head(h) for h in ev['heads']) + '>' + d
                if ev['beam'] == 'begin':
                    s += '['
                elif ev['beam'] == 'end':
                    s += ']'
                for m in ev['marks']:
                    s += '->' if m == 'accent' else ''
                if ev['dyn']:
                    s += '\\' + ev['dyn']
                if ev['wedge']:
                    s += {'crescendo': '\\<', 'diminuendo': '\\>', 'stop': '\\!'}[ev['wedge']]
                toks.append(s)
            out.append(' '.join(toks) + (' \\bar "|."' if mi == nmeas - 1 else '') + ' |')
        return '\n      '.join(out)

    tsig = f'\\numericTimeSignature \\time {piece["time"][0]}/{piece["time"][1]}'
    L.append('\\score {')
    L.append('  <<')
    for p in piece['parts']:
        if p['kind'] == 'pitched':
            txt, bpm = piece['tempo']
            L.append(f'    \\new Staff = "{p["staff"]}" \\with {{ instrumentName = "{p["name"]}" shortInstrumentName = "{p["abbr"]}" '
                     f'midiInstrument = "flute" }} {{')
            L.append(f'      \\autoBeamOff \\tempo "{txt}" 4 = {bpm} {tsig} \\key g \\major \\clef treble')
            L.append('      ' + voice_ly(p, '1'))
            L.append('    }')
        else:
            style = '#snare-line-style' if p.get('lines', 5) == 1 else '#drums-style'
            extra = ' \\override StaffSymbol.line-count = #1' if p.get('lines', 5) == 1 else ''
            L.append(f'    \\new DrumStaff = "{p["staff"]}" \\with {{ instrumentName = "{p["name"]}" '
                     f'shortInstrumentName = "{p["abbr"]}" drumStyleTable = {style}{extra} }} <<')
            vks = list(p['voices'])
            for vk in vks:
                vo = ('\\voiceOne ' if vk == '1' else '\\voiceTwo ') if len(vks) > 1 else ''
                L.append(f'      \\new DrumVoice = "{p["staff"]}v{vk}" \\drummode {{ {vo}\\autoBeamOff {tsig}')
                L.append('      ' + voice_ly(p, vk))
                L.append('      }')
            L.append('    >>')
    L.append('  >>')
    L.append('  \\layout { \\context { \\Score \\remove "Bar_number_engraver" } }')
    L.append('  \\midi { }')
    L.append('}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ------------------------------------------------------------------ checks
def run(cmd, cwd=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def expected_grobs(piece, parsed):
    E = {'heads': Counter(), 'stems': Counter(), 'beams': Counter(), 'accents': 0, 'rests': Counter()}
    for p in piece['parts']:
        for vk in p['voices']:
            t = F(0)
            for evs in parsed[p['id']][vk]:
                for ev in evs:
                    when = t / 4                          # whole notes, as LilyPond's moments
                    if ev['kind'] == 'rest':
                        E['rests'][(p['staff'], when)] += 1
                    else:
                        for h in ev['heads']:
                            style = 'default' if isinstance(h, tuple) else p['table'][h][2]
                            E['heads'][(p['staff'], when, head_pos(p, h), style)] += 1
                        if ev['type'] > 1:
                            E['stems'][(p['staff'], when, 1 if ev['stem'] == 'up' else -1)] += 1
                        if ev['beam'] == 'begin':
                            E['beams'][p['staff']] += 1
                        E['accents'] += ev['marks'].count('accent')
                    t += ev['dur']
    return E


def parse_cvlog(path):
    G = {'heads': Counter(), 'stems': Counter(), 'beams': Counter(), 'accents': 0, 'rests': Counter(),
         'clefs': Counter(), 'times': Counter()}
    seen_beam = set()
    for line in open(path, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        nm, sid, when = f[0], f[1], f[2]
        try:
            w = F(when)
        except Exception:
            w = when
        if nm == 'NoteHead':
            G['heads'][(sid, w, int(f[7]), f[10] if len(f) > 10 else 'default')] += 1
        elif nm == 'Stem' and int(f[8]) > 0:
            G['stems'][(sid, w, int(f[5]))] += 1
        elif nm == 'Beam':
            if f[4] not in seen_beam:
                seen_beam.add(f[4])
                G['beams'][sid] += 1
        elif nm == 'Script' and 'sforzato' in f[5]:
            G['accents'] += 1
        elif nm == 'Rest':
            G['rests'][(sid, w)] += 1
        elif nm == 'Clef':
            G['clefs'][(sid, f[5])] += 1
        elif nm == 'TimeSignature' and f[6] in ('1', '0'):
            G['times'][(sid, f[5] + ' ' + (f[7] if len(f) > 7 else '?'))] += 1
    return G


def midi_compare(truth, mid):
    sys.path.insert(0, os.path.join(os.path.dirname(ROOT), '_validate'))
    import validate as V
    tr = V.truth_events(truth)
    notes, _ = V.read_midi(mid)
    miss, extra = V.fuzzy_diff(tr['attacks'], notes)
    return {'truth_attacks': sum(tr['attacks'].values()), 'midi_attacks': sum(notes.values()),
            'missing': sum(miss.values()), 'extra': sum(extra.values()),
            'ok': not miss and not extra}


def percussion_counts(counts, truth):
    """count_symbols.py output + percussion extras: x-clef-percussion (its name for the clef is
    x-clef-percussion0+0), x-staff-1-line, x-unpitched (unpitched note heads), x-notehead-x"""
    import xml.etree.ElementTree as ET
    c = {('x-clef-percussion' if k.startswith('x-clef-percussion') else k): v for k, v in counts.items()}
    r = ET.parse(truth).getroot()
    c['x-unpitched'] = sum(1 for n in r.iter('note') if n.find('unpitched') is not None)
    c['x-notehead-x'] = sum(1 for n in r.iter('note') if (n.findtext('notehead') or '').strip() == 'x')
    c['x-staff-1-line'] = sum(1 for sl in r.iter('staff-lines') if (sl.text or '').strip() == '1')
    return dict(sorted(c.items()))


def image_only(pdf, n_expected):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    return {'fonts': len(font_lines), 'images': n_imgs, 'text_chars': len(txt.strip()),
            'image_only': not font_lines and n_imgs == n_expected and not txt.strip()}


def render_pages(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'r{dpi}')
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=600)
    return [np.array(Image.open(f), dtype=np.uint8) for f in sorted(glob.glob(prefix + '-*.pgm'))]


SCANS = {
    'scan.pdf': {'seed': 7511, 'summary': '300 dpi grey flatbed scan, 0.7 deg skew, light paper texture and noise, '
                                         'JPEG q72',
                 'params': dict(dpi=300, mode='gray', texture=2, rotate=0.7, blur=0.45, noise=3, jpeg=72)},
    'scan-severe.pdf': {'seed': 7512, 'summary': 'thin, faded binarised photocopy at 150 dpi (rendered 300): ink '
                                                'dropout, -3 deg skew, broken lines, salt & pepper, toner specks',
                        'params': dict(dpi=300, out_dpi=150, ink_dropout=0.12, rotate=-3.0, blur=0.6, noise=8,
                                       binarize=118, binarize_noise=20, saltpepper=0.0015, speckle=120,
                                       format='png1')},
}


def build(keep=False):
    t0 = time.time()
    piece = PIECE
    iid = piece['id']
    out = os.path.join(ROOT, iid)
    work = os.path.join(ROOT, '_work', iid)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    log = {'id': iid}
    parsed = {}
    mlen = F(piece['time'][0] * 4, piece['time'][1])
    for p in piece['parts']:
        parsed[p['id']] = {}
        for vk, txt in p['voices'].items():
            ms = parse_voice(txt)
            for k, evs in enumerate(ms):
                if sum(e['dur'] for e in evs) != mlen:
                    raise ValueError(f'{p["id"]}:{vk} measure {k + 1} has {sum(e["dur"] for e in evs)} quarters')
            assign_stems(p, vk, ms)
            assign_beam2(ms)
            parsed[p['id']][vk] = ms
    truth = os.path.join(out, 'truth.musicxml')
    write_truth(piece, parsed, truth)
    rc, o, e = run(['xmllint', '--noout', '--schema', XSD, truth])
    if rc:
        raise RuntimeError('XSD: ' + e[-1500:])
    rc, o, e = run([PY, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1]);'
                              'print(len(s.parts), len(s.flatten().notes))', truth])
    if rc:
        raise RuntimeError('music21: ' + e[-800:])
    log['music21'] = o.strip()
    ly = os.path.join(work, 'engraving.ly')
    write_ly(piece, parsed, ly)
    rc, o, e = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files', f'-dinclude-settings={CVLOG}',
                    '-o', 'engraving', 'engraving.ly'], cwd=work)
    warns = [l for l in e.splitlines() if re.search(r'(warning|error):', l)]
    log['lilypond_warnings'] = warns
    if rc or warns:
        raise RuntimeError('lilypond: ' + '\n'.join(warns[:10]) + e[-1500:])
    pdf = os.path.join(work, 'engraving.pdf')
    rc, info, _ = run(['pdfinfo', pdf])
    npages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    if npages != piece['pages']:
        raise RuntimeError(f'pages {npages} != {piece["pages"]}')
    mc = midi_compare(truth, os.path.join(work, 'engraving.midi'))
    log['midi'] = mc
    if not mc['ok']:
        raise RuntimeError(f'MIDI vs truth: {mc}')
    E = expected_grobs(piece, parsed)
    G = parse_cvlog(os.path.join(work, 'engraving.cvlog'))
    mism = {}
    for k in ('heads', 'stems', 'rests'):
        if E[k] != G[k]:
            mism[k] = {'missing': [list(map(str, x)) for x in (E[k] - G[k])][:12],
                       'extra': [list(map(str, x)) for x in (G[k] - E[k])][:12]}
    if dict(E['beams']) != dict(G['beams']):
        mism['beams'] = {'expected': dict(E['beams']), 'engraved': dict(G['beams'])}
    if E['accents'] != G['accents']:
        mism['accents'] = [E['accents'], G['accents']]
    exp_clefs = Counter({('fl', 'clefs.G'): 1, ('sd', 'clefs.percussion'): 1, ('ds', 'clefs.percussion'): 1})
    first_clefs = Counter()
    for (sid, glyph), n in G['clefs'].items():
        first_clefs[(sid, glyph)] = 1
    exp_times = Counter({(p['staff'], f'({piece["time"][0]} . {piece["time"][1]}) numbered'): 1 for p in piece['parts']})
    if G['times'] != exp_times:
        mism['times'] = {k[0] + ':' + k[1]: v for k, v in G['times'].items()}
    if first_clefs != exp_clefs:
        mism['clefs'] = {k[0] + ':' + k[1]: v for k, v in G['clefs'].items()}
    log['grob_check'] = {'heads': sum(E['heads'].values()), 'stems': sum(E['stems'].values()),
                         'rests': sum(E['rests'].values()), 'beams': dict(G['beams']), 'accents': G['accents'],
                         'clefs': {k[0] + ':' + k[1]: v for k, v in G['clefs'].items()},
                         'times': {k[0] + ':' + k[1]: v for k, v in G['times'].items()}, 'mismatch': mism}
    if mism:
        raise RuntimeError('grob log vs truth: ' + json.dumps(mism)[:3000])
    counts = percussion_counts(count_all(truth), truth)
    shutil.copy(ly, os.path.join(out, 'engraving.ly'))
    pages300 = render_pages(pdf, 300, work)
    D.save_pdf([Image.fromarray(x) for x in pages300], 300, os.path.join(out, 'clean.pdf'), fmt='png')
    checks = {'clean.pdf': image_only(os.path.join(out, 'clean.pdf'), npages)}
    degr = {'clean.pdf': {'seed': None, 'dpi': 300, 'format': 'png (8-bit grey)',
                          'summary': 'undamaged raster of the engraving'}}
    for fname, spec in SCANS.items():
        P = dict(spec['params'])
        pages = pages300 if P['dpi'] == 300 else render_pages(pdf, P['dpi'], work)
        outs = D.degrade_document(pages, P, spec['seed'])
        imgs = [o_[0] for o_ in outs]
        fmt = P.get('format', 'jpeg')
        path = os.path.join(out, fname)
        D.save_pdf(imgs, P.get('out_dpi', P['dpi']), path, fmt='png' if fmt in ('png', 'png1') else 'jpeg',
                   quality=P.get('jpeg', 75))
        checks[fname] = image_only(path, len(imgs))
        if not checks[fname]['image_only']:
            raise RuntimeError(f'{fname} not image-only: {checks[fname]}')
        degr[fname] = {'seed': spec['seed'], 'render_dpi': P['dpi'], 'dpi': P.get('out_dpi', P['dpi']),
                       'format': fmt if fmt != 'jpeg' else f'jpeg q{P.get("jpeg", 75)}',
                       'colour': 'bw' if P.get('binarize') else P.get('mode', 'gray'),
                       'pdf_pages': [{'image': k + 1, 'source_pages': o_[2], 'size_px': list(o_[0].size), 'ops': o_[1]}
                                     for k, o_ in enumerate(outs)],
                       'params': P, 'summary': spec['summary'], 'bytes': os.path.getsize(path)}
    symbols = [k for k in counts if not k.startswith('x-')] + [k for k in counts if k.startswith('x-')]
    meta = {
        'id': iid, 'family': FAMILY, 'title': piece['title'], 'layout': 'percussion-none',
        'symbols': symbols, 'counts': counts,
        'expected': {
            'parts': [p['name'] for p in piece['parts']], 'must_not_split': False,
            'staves_per_part': {p['name']: 1 for p in piece['parts']},
            'notes': ('THREE parts: Flute (pitched, treble clef, G major), Snare Drum (ONE-LINE staff, percussion '
                      'clef, no key signature, all notes on the line, stems up, accents) and Drum Set (5-line staff, '
                      'percussion clef, no key signature, two voices: hi-hat x noteheads + snare stems up, bass drum '
                      'stems down). Percussion notes are unpitched: their staff position (display-step/octave in '
                      'treble positions) and instrument identify them, not a pitch. 8 measures of 4/4 on 2 systems.'),
        },
        'notes': [
            'Unpitched notes are encoded as <unpitched><display-step>/<display-octave> (treble-clef staff '
            'positions: bass drum F4 = first space, snare C5 = third space, hi-hat E5 = fourth space with '
            '<notehead>x</notehead>) plus <instrument id> pointing to a <score-instrument> with <midi-unpitched> '
            '(GM drum map: bass drum 36, snare 38, closed hi-hat 42; MusicXML counts from 1).',
            'The one-line snare staff is <staff-lines>1</staff-lines>; its notes sit on the line, encoded as the '
            'middle-line position B4 (the convention of Finale/MuseScore exports).',
            'Percussion staves have no key signature (no <key> element); the flute alone carries G major.',
            'Drum-kit rests of voice 2 are positioned by LilyPond (no display-step in the truth).',
            'Symbol counts follow corpus/coverage/layouts/_tools/count_symbols.py (copied here): note-* per note '
            'event (chords once), ledger-* from <pitch> only (unpitched notes have no pitch).',
        ],
        'pages': npages, 'measures': len(parsed['P1']['1']), 'systems': 1 + len(piece['systems']),
        'dpi': 300, 'degradations': degr,
        'files': ['ATTRIBUTION.txt', 'clean.pdf', 'engraving.ly', 'meta.json', 'scan-severe.pdf', 'scan.pdf',
                  'truth.musicxml'],
        'license': 'CC0', 'license_detail': 'CC0-1.0: composition, engraving, truth and scans',
        'source': 'self-authored for the coverage suite (2026)',
        'generator': 'corpus/coverage/percussion/_tools/build.py',
        'validation': {'xsd_valid': True, 'music21_parse': log['music21'], 'midi_attacks_match_truth': True,
                       'midi': mc, 'grob_log_matches_truth': True, 'grob_check': log['grob_check'],
                       'lilypond_warnings': warns, 'image_only': {k: v['image_only'] for k, v in checks.items()}},
    }
    with open(os.path.join(out, 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
    with open(os.path.join(out, 'ATTRIBUTION.txt'), 'w') as f:
        f.write('Village Parade - flute melody and percussion parts composed for the OMR coverage suite (2026) - '
                'CC0 1.0.\n\nComposition, engraving, rasterisation and damage simulation produced for the OMR coverage '
                'suite (corpus/coverage/percussion/_tools, 2026). All files of this item are dedicated to the public '
                'domain (CC0 1.0 Universal).\n')
    log['ok'] = True
    log['seconds'] = round(time.time() - t0, 1)
    log['meta'] = meta
    os.makedirs(os.path.join(ROOT, '_logs'), exist_ok=True)
    with open(os.path.join(ROOT, '_logs', iid + '.json'), 'w') as f:
        json.dump(log, f, indent=1, default=str, ensure_ascii=False)
    man = {'family': FAMILY, 'description': 'Percussion layout coverage (layout tag percussion-none): unpitched '
                                            'percussion staves (one-line and 5-line, percussion clef, x noteheads, '
                                            'two-voice drum set) next to a pitched melody.',
           'license': 'CC0', 'generator': '_tools/build.py', 'layouts': ['percussion-none'], 'n_items': 1,
           'symbol_totals': counts, 'items': [dict(meta, path=f'coverage/percussion/{iid}',
                                                    scan_files=['scan-severe.pdf', 'scan.pdf'])]}
    with open(os.path.join(ROOT, 'manifest.json'), 'w') as f:
        json.dump(man, f, indent=2, ensure_ascii=False, default=str)
    if not keep:
        shutil.rmtree(os.path.join(ROOT, '_work'), ignore_errors=True)
    print('OK', iid, log['seconds'], 's', json.dumps(log['grob_check'])[:400])


if __name__ == '__main__':
    build('--keep-work' in sys.argv)
