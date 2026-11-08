"""Score model -> LilyPond 2.24 source (absolute pitch, \\autoBeamOff + manual beams,
\\autoLineBreaksOff + explicit \\break so system breaks are exactly the truth's)."""
from __future__ import annotations

from fractions import Fraction as F

from .model import TYPE_LY, Ev, Score, Staff, display_ql

ACC = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}
KEY_MAJ = {0: 'c', 1: 'g', 2: 'd', 3: 'a', 4: 'e', 5: 'b', 6: 'fis', 7: 'cis', -1: 'f', -2: 'bes',
           -3: 'ees', -4: 'aes', -5: 'des', -6: 'ges', -7: 'ces'}
KEY_MIN = {0: 'a', 1: 'e', 2: 'b', 3: 'fis', 4: 'cis', 5: 'gis', 6: 'dis', 7: 'ais', -1: 'd', -2: 'g',
           -3: 'c', -4: 'f', -5: 'bes', -6: 'ees', -7: 'aes'}
ARTIC_LY = {'staccato': '.', 'staccatissimo': '!', 'accent': '>', 'tenuto': '-', 'marcato': '^', 'portato': '_'}
SIDE = {None: '-', 'above': '^', 'below': '_'}
CHORD_SUFFIX = {'major': '', 'minor': ':m', 'dominant': ':7', 'major-seventh': ':maj7', 'minor-seventh': ':m7',
                'diminished': ':dim', 'augmented': ':aug', 'half-diminished': ':m7.5-', 'suspended-fourth': ':sus4',
                'suspended-second': ':sus2', 'major-sixth': ':6', 'minor-sixth': ':m6', 'dominant-ninth': ':9',
                'diminished-seventh': ':dim7'}


def lq(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def pitch_ly(p):
    step, alter, octv = p
    k = octv - 3
    return step.lower() + ACC[alter] + ("'" * k if k > 0 else ',' * (-k))


def name_ly(step, alter):
    return step.lower() + ACC[alter]


def ql_dur(q: F, unit='4') -> str:
    """quarters -> LilyPond duration (plain or with multiplier)"""
    for t, lyd in TYPE_LY.items():
        for dots in (0, 1, 2):
            if display_ql(t, dots) == q:
                return lyd + '.' * dots
    q = F(q)
    if q.denominator == 1:
        return f'4*{q.numerator}'
    return f'4*{q.numerator}/{q.denominator}'


def vname(st: Staff):
    return 'v' + st.id


def tempo_ly(tp):
    s = '\\tempo '
    if tp['text']:
        s += lq(tp['text'])
    if tp['bpm']:
        s += (' ' if tp['text'] else '') + TYPE_LY[tp['unit']] + '.' * tp['dots'] + f" = {tp['bpm']}"
    return s


def event_ly(ev: Ev, mdur: F) -> str:
    pre = ''
    if ev.tempo:
        pre = tempo_ly(ev.tempo) + ' '
    if ev.kind == 'clef':
        return f'\\clef "{ev.clef}"'
    if ev.kind == 'rest':
        s = ('R' + ql_dur(mdur)) if ev.measure_rest else ('r' + TYPE_LY[ev.dtype] + '.' * ev.dots)
    else:
        if len(ev.pitches) == 1:
            s = pitch_ly(ev.pitches[0])
        else:
            inner = []
            for p in ev.pitches:
                x = pitch_ly(p)
                for dig, place, fp in ev.fingering:
                    if fp == p:
                        x += SIDE[place] + str(dig)
                inner.append(x)
            s = '<' + ' '.join(inner) + '>'
        s += TYPE_LY[ev.dtype] + '.' * ev.dots
        if ev.tie_start:
            assert ev.tie_start == set(ev.pitches), 'partial chord ties not supported'
            s += '~'
    if ev.beam_start:
        s += '['
    if ev.beam_stop:
        s += ']'
    for typ, place in ev.marks:
        if typ in ARTIC_LY:
            s += SIDE[place] + ARTIC_LY[typ]
        else:
            s += ('' if place is None else SIDE[place]) + '\\' + typ
    for dig, place, fp in ev.fingering:
        if fp is None:
            s += SIDE[place] + str(dig)
    for d in ev.dynamics:
        s += '\\' + d
    for w in ev.wedges:
        s += {'stop': '\\!', 'stop-implicit': '', 'crescendo': '\\<', 'diminuendo': '\\>'}[w]
    for pd in ev.pedal:
        s += '\\sustainOn' if pd == 'start' else '\\sustainOff'
    for txt, place in ev.words:
        s += SIDE[place] + '\\markup \\italic ' + lq(txt)
    if ev.arpeggio:
        s += '\\arpeggio'
    if ev.slur_stop:
        s += ')'
    if ev.slur_start:
        s += '('
    if ev.breath:
        s += ' \\breathe'
    return pre + s


class LilyWriter:
    def __init__(self, score: Score, opts: dict | None = None):
        self.s = score
        self.o = opts or {}

    def staff_music(self, st: Staff, master: bool):
        s = self.s
        out = ['\\autoBeamOff']
        if master:
            out.append('\\set Score.rehearsalMarkFormatter = #format-mark-box-letters')
            out.append('\\autoLineBreaksOff \\autoPageBreaksOff')
        for i, mi in enumerate(s.measures):
            line = []
            if master and i > 0 and mi.new_page:
                line.append('\\pageBreak')
            elif master and i > 0 and mi.new_system:
                line.append('\\break')
            if i == 0 or mi.time:
                (tn, td), sym = s.time_at(i)
                if (tn, td) in ((4, 4), (2, 2)):
                    line.append('\\defaultTimeSignature' if sym in ('common', 'cut') else '\\numericTimeSignature')
                if master:
                    line.append(f'\\time {tn}/{td}')
            if i == 0 or mi.key:
                fifths, mode = mi.key or s.key_at(i)
                line.append(f'\\key {(KEY_MIN if mode == "minor" else KEY_MAJ)[fifths]} \\{mode}')
            if master and mi.mark:
                line.append('\\mark \\default')
            for ev in st.measures[i]:
                line.append(event_ly(ev, mi.dur))
            if master and mi.right_bar:
                line.append({'double': '\\bar "||"', 'final': '\\bar "|."'}[mi.right_bar])
            line.append('|')
            out.append(' '.join(line))
        return '\n      '.join(out)

    def chords_ly(self, part):
        out = []
        t = F(0)
        for c in part.chords:
            if c['t'] > t:
                out.append('s' + ql_dur(c['t'] - t))
            x = name_ly(*c['root']) + ql_dur(c['dur']) + CHORD_SUFFIX[c['kind']]
            if c['bass']:
                x += '/' + name_ly(*c['bass'])
            out.append(x)
            t = c['t'] + c['dur']
        return '\\new ChordNames = "cn' + part.id + '" \\chordmode { ' + ' '.join(out) + ' }'

    def staff_ly(self, part, st, master, ind, with_name):
        w = []
        if with_name:
            w.append(f'instrumentName = {lq(part.name)}')
            if self.o.get('short_names') and part.abbr:
                w.append(f'shortInstrumentName = {lq(part.abbr)}')
        wt = (' \\with { ' + ' '.join(w) + ' }') if w else ''
        return (f'{ind}\\new Staff = "{st.id}"{wt} {{ \\clef "{st.clef}"\n'
                f'{ind}  \\new Voice = "{vname(st)}" {{\n{ind}      {self.staff_music(st, master)}\n{ind}  }}\n'
                f'{ind}}}')

    def document(self):
        s, o = self.s, self.o
        L = ['\\version "2.24.0"']
        if o.get('staff_size'):
            L.append(f'#(set-global-staff-size {o["staff_size"]})')
        L.append('\\header {')
        L.append(f'  title = {lq(s.title)}')
        if s.subtitle:
            L.append(f'  subtitle = {lq(s.subtitle)}')
        if s.composer:
            L.append(f'  composer = {lq(s.composer)}')
        L.append('  tagline = ##f')
        L.append('}')
        L.append('\\paper {')
        L.append(f'  #(set-paper-size "{o.get("paper", "a4")}")')
        for x in o.get('paper_extra', []):
            L.append('  ' + x)
        L.append('}')
        L.append('\\score {')
        L.append('  <<')
        grouped = {pid: g for g in s.groups for pid in g['parts']}
        master_done = False
        k = 0
        while k < len(s.parts):
            p = s.parts[k]
            g = grouped.get(p.id)
            members = [p]
            if g:
                members = [x for x in s.parts if x.id in g['parts']]
                gw = (' \\with { systemStartDelimiter = #\'SystemStartBracket }' if g['type'] == 'StaffGroup'
                      else '')
                L.append(f'    \\new {g["type"]}{gw} <<')
                ind = '      '
            else:
                ind = '    '
            for mp in members:
                if mp.chords:
                    L.append(ind + self.chords_ly(mp))
                if len(mp.staves) > 1:
                    L.append(f'{ind}\\new PianoStaff \\with {{ instrumentName = {lq(mp.name)} }} <<')
                    for st in mp.staves:
                        L.append(self.staff_ly(mp, st, not master_done, ind + '  ', False))
                        master_done = True
                    L.append(f'{ind}>>')
                else:
                    L.append(self.staff_ly(mp, mp.staves[0], not master_done, ind, o.get('names', True)))
                    master_done = True
            if g:
                L.append('    >>')
            k += len(members)
        L.append('  >>')
        L.append('  \\layout {')
        for x in o.get('layout_extra', []):
            L.append('    ' + x)
        L.append('  }')
        L.append('  \\midi { }')
        L.append('}')
        return '\n'.join(L) + '\n'
