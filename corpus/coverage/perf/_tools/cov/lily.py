"""Model + staff layout -> LilyPond 2.24 source (absolute pitch).

Derived from corpus/challenge/layout/_tools/lsynth/lily.py (copied, extended with grace notes,
ottava, ornaments, arpeggio, fingering, tremolo, breath marks, forced/cautionary accidentals and an
instrumented twin: every note head / rest gets a grob id and every staff logs its grobs, see
harvest.py).

layout: {'groups': [{'type': 'PianoStaff'|'ChoirStaff'|None, 'name', 'staves': [staff...]}]}
staff:  {'id', 'clef', 'voices': [(pid, vkey)...], 'lyrics': [{'voice', 'verses', 'stanza'}], 'name', 'with'}
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import Score, lyric_slots, split_plain, staff_roles

ACC = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}
DUR = {'breve': '\\breve', 'whole': '1', 'half': '2', 'quarter': '4', 'eighth': '8',
       '16th': '16', '32nd': '32', '64th': '64'}
KEY_MAJ = {0: 'c', 1: 'g', 2: 'd', 3: 'a', 4: 'e', 5: 'b', 6: 'fis', 7: 'cis', -1: 'f', -2: 'bes',
           -3: 'ees', -4: 'aes', -5: 'des', -6: 'ges', -7: 'ces'}
KEY_MIN = {0: 'a', 1: 'e', 2: 'b', 3: 'fis', 4: 'cis', 5: 'gis', 6: 'dis', 7: 'ais', -1: 'd', -2: 'g',
           -3: 'c', -4: 'f', -5: 'bes', -6: 'ees', -7: 'aes'}
ROLE_CMD = {0: '\\oneVoice', 1: '\\voiceOne', 2: '\\voiceTwo', 3: '\\voiceThree', 4: '\\voiceFour'}
ARTIC = {'staccato': '-.', 'staccatissimo': '-!', 'accent': '->', 'tenuto': '--', 'strong-accent': '-^'}
ORN = {'trill': '\\trill', 'mordent': '\\mordent', 'turn': '\\turn'}
WEDGE = {'crescendo': '\\<', 'diminuendo': '\\>', 'stop': '\\!'}
UNIT = {'quarter': '4', 'half': '2', 'eighth': '8'}

# grob types logged by the instrumented twin (per staff / per lyrics line / score level)
STAFF_GROBS = ['NoteHead', 'Rest', 'MultiMeasureRest', 'Accidental', 'AccidentalCautionary', 'Stem', 'Flag',
               'Beam', 'Dots', 'Slur', 'Tie', 'Script', 'DynamicText', 'Hairpin', 'SustainPedal',
               'Fingering', 'Arpeggio', 'StemTremolo', 'BreathingSign', 'TextScript', 'Clef', 'KeySignature',
               'KeyCancellation', 'TimeSignature', 'OttavaBracket', 'TupletBracket', 'TupletNumber', 'BarLine',
               'LedgerLineSpanner']
LYRIC_GROBS = ['LyricText', 'LyricHyphen', 'LyricExtender', 'StanzaNumber']
SCORE_GROBS = ['RehearsalMark', 'MetronomeMark', 'TextMark', 'VoltaBracket', 'SegnoMark', 'CodaMark',
               'SystemStartBrace', 'SystemStartBracket']


def pitch_ly(p):
    step, alter, octv = p
    k = octv - 3
    return step.lower() + ACC[alter] + ("'" * k if k > 0 else ',' * (-k))


def frac_whole(q: F) -> str:
    w = F(q) / 4
    return '1' if w == 1 else f'1*{w.numerator}/{w.denominator}'


def lq(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def vname(pid, vkey):
    return f'v{pid}x{vkey}'


def words_markup(text, style):
    if style == 'bold':
        return f'\\markup {{ \\bold {lq(text)} }}'
    if style == 'plain':
        return f'\\markup {{ {lq(text)} }}'
    return f'\\markup {{ \\italic {lq(text)} }}'


def logger_with(tags, name):
    return ' '.join(f'\\override {t}.after-line-breaking = #(cov-logger \'{t} {lq(name)})' for t in tags)


class LilyWriter:
    def __init__(self, score: Score, layout: dict, opts: dict, instrument=False):
        self.s = score
        self.layout = layout
        self.o = opts
        self.instr = instrument
        self._plan = None
        self.staff_ids = {}
        for g in layout['groups']:
            for st in g['staves']:
                for pid, vk in st['voices']:
                    sn = score.part(pid).voice(vk).staff
                    self.staff_ids.setdefault((pid, sn), st['id'])
                for ps in st.get('part_staves', []):
                    self.staff_ids[tuple(ps)] = st['id']

    # ------------------------------------------------------------------ timing
    def timing_plan(self):
        if self._plan is not None:
            return self._plan
        s = self.s
        nm = len(s.measures)
        plan = []
        pos = F(0)
        for i, mi in enumerate(s.measures):
            e = {'partial': None, 'reset': None, 'bar': None, 'check': False}
            if i == 0 and mi.dur < mi.nominal:
                e['partial'] = frac_whole(mi.dur)
                pos = mi.nominal - mi.dur
            elif i > 0 and (pos != 0 or mi.dur < mi.nominal):
                newpos = mi.nominal - mi.dur if mi.dur < mi.nominal else F(0)
                e['reset'] = newpos / 4
                pos = newpos
            pos += mi.dur
            right = mi.right_bar
            left_next = s.measures[i + 1].left_bar if i + 1 < nm else None
            bar = None
            if right == 'repeat-end' and left_next == 'repeat-start':
                bar = ':|.|:'
            elif right == 'repeat-end':
                bar = ':|.'
            elif left_next == 'repeat-start':
                bar = '.|:'
            elif right == 'final':
                bar = '|.'
            elif right == 'double':
                bar = '||'
            at_end = pos >= mi.nominal
            if not at_end and i + 1 < nm and bar is None:
                bar = '|'
            e['bar'] = bar
            e['check'] = at_end
            if at_end:
                pos = F(0)
            plan.append(e)
        for i in range(nm - 1):
            if plan[i + 1]['reset'] is not None:
                plan[i]['check'] = False
        self._plan = plan
        return plan

    # ------------------------------------------------------------------ master commands
    def master_start(self, i):
        s = self.s
        mi = s.measures[i]
        out = []
        if i == 0:
            out.append('\\autoLineBreaksOff')
            out.append('\\autoPageBreaksOff')
            if mi.left_bar == 'repeat-start':
                out.append('\\bar ".|:"')
        elif mi.brk == 'page':
            out.append('\\pageBreak')
        elif mi.brk == 'system':
            out.append('\\break')
        cmds = []
        if i > 0 and s.measures[i - 1].volta_end:
            cmds.append('(volta #f)')
        if mi.volta_start:
            cmds.append(f'(volta {lq(mi.volta_start + ".")})')
        if cmds:
            out.append("\\set Score.repeatCommands = #'(" + ' '.join(cmds) + ')')
        texts = []
        for mk in mi.marks:
            k = mk['kind']
            if k == 'tempo':
                t = lq(mk['text']) if mk.get('text') else ''
                mm = ''
                if mk.get('bpm'):
                    mm = f' {UNIT[mk.get("unit", "quarter")]}{"." if mk.get("dots") else ""} = {mk["bpm"]}'
                out.append(('\\tempo ' + t + mm).replace('\\tempo  ', '\\tempo '))
            elif k == 'segno':
                out.append('\\segnoMark 1')
            elif k == 'coda':
                out.append('\\codaMark 1')
            elif k == 'rehearsal':
                out.append(f'\\mark \\markup {{ \\box \\bold {lq(mk["text"])} }}')
            elif k == 'words':
                texts.append(words_markup(mk['text'], mk.get('style', 'italic')).replace('\\markup ', '', 1))
        if texts:
            out.append('\\textMark \\markup ' + (texts[0] if len(texts) == 1 else
                                                 '\\column { ' + ' '.join(texts) + ' }'))
        return out

    def master_end(self, i):
        mi = self.s.measures[i]
        parts = [words_markup(mk['text'], mk.get('style', 'italic')).replace('\\markup ', '', 1)
                 for mk in mi.end_marks]
        if not parts:
            return []
        if len(parts) == 1:
            return ['\\textEndMark \\markup ' + parts[0]]
        return ['\\textEndMark \\markup \\right-column { ' + ' '.join(parts) + ' }']

    # ------------------------------------------------------------------ voices
    def voice_music(self, pid, vkey, staff_voices, lyrics_voice, master=False, staff_first=False):
        s = self.s
        part = s.part(pid)
        home = part.voice(vkey).staff
        plan = self.timing_plan()
        out = []
        self._cur_staff = home
        self._home = home
        self._pid = pid
        if lyrics_voice:
            out.append("\\set melismaBusyProperties = #'(melismaBusy slurMelismaBusy tieMelismaBusy)")
        if part.instrument == 'voice' or self.o.get('auto_beam_off'):
            out.append('\\autoBeamOff')
        prev_role = None
        for i in range(len(s.measures)):
            mi = s.measures[i]
            e = plan[i]
            line = []
            if master:
                line += self.master_start(i)
                if i == 0 or mi.time:
                    (tn, td), sym = s.current_time(i)
                    if (tn, td) in ((4, 4), (2, 2)):
                        line.append('\\defaultTimeSignature' if sym in ('common', 'cut') else '\\numericTimeSignature')
                    line.append(f'\\time {tn}/{td}')
            if (i == 0 or mi.key) and staff_first:
                fifths, mode = mi.key or s.current_key(i)
                tonic = (KEY_MIN if mode == 'minor' else KEY_MAJ)[fifths]
                line.append(f'\\key {tonic} \\{mode}')
            if master and e['partial']:
                line.append(f'\\partial {e["partial"]}')
            if master and e['reset'] is not None:
                w = e['reset']
                line.append(f'\\set Timing.measurePosition = #(ly:make-moment {w.numerator}/{w.denominator})')
            roles = staff_roles([((p_, k), s.part(p_).measures[i].get(k, [])) for p_, k in staff_voices])
            role = roles.get((pid, vkey), 0) if len(staff_voices) > 1 else None
            if role is not None and role != prev_role:
                line.append(ROLE_CMD[role])
                prev_role = role
            evs = part.measures[i].get(vkey, [])
            tot = sum((x.dur for x in evs), F(0))
            self._allow_R = e['reset'] is None and e['partial'] is None
            line.extend(self.events_ly(evs))
            if tot < mi.dur:
                line.append('s' + frac_whole(mi.dur - tot))
            if master:
                line += self.master_end(i)
            if master and e['bar'] and not (i == len(s.measures) - 1 and e['bar'] == '|'):
                line.append(f'\\bar "{e["bar"]}"')
            if e['check']:
                line.append('|')
            out.append(' '.join(line))
        if master and s.measures[-1].volta_end:
            out.append("\\set Score.repeatCommands = #'((volta #f))")
        return '\n    '.join(out)

    def events_ly(self, evs):
        out = []
        in_tup, tup_ratio = False, None
        k = 0
        while k < len(evs):
            ev = evs[k]
            if ev.kind == 'clef':
                out.append(f'\\clef "{ev.clef}"')
                k += 1
                continue
            if ev.kind == 'ottava':
                out.append(f'\\ottava #{ev.ottava}')
                k += 1
                continue
            if ev.kind == 'space':
                if in_tup:
                    out.append('}')
                    in_tup = False
                out.append('s' + frac_whole(ev.dur))
                k += 1
                continue
            want = ev.staff or self._home
            if want != self._cur_staff:
                out.append(f'\\change Staff = "{self.staff_ids[(self._pid, want)]}"')
                self._cur_staff = want
            if ev.grace:
                grp = [ev]
                while k + len(grp) < len(evs) and evs[k + len(grp)].grace:
                    grp.append(evs[k + len(grp)])
                cmd = '\\slashedGrace' if ev.grace == 'slash' else '\\grace'
                out.append(cmd + ' { ' + ' '.join(self.event_ly(g) for g in grp) + ' }')
                k += len(grp)
                continue
            if ev.tuplet and (not in_tup or ev.tuplet != tup_ratio or ev.tuplet_start):
                if in_tup:
                    out.append('}')
                a, n = ev.tuplet
                out.append(f'\\tuplet {a}/{n} {{')
                in_tup, tup_ratio = True, ev.tuplet
            elif not ev.tuplet and in_tup:
                out.append('}')
                in_tup = False
            out.append(self.event_ly(ev))
            if ev.breath:
                out.append('\\breathe')
            if ev.tuplet and ev.tuplet_stop and in_tup:
                out.append('}')
                in_tup = False
            k += 1
        if in_tup:
            out.append('}')
        return out

    def _tw(self, ev, j):
        if not self.instr or not ev.ids:
            return ''
        return f'\\tweak id #{lq(ev.ids[j])} '

    def event_ly(self, ev):
        dur = DUR[ev.dtype] + '.' * ev.dots if ev.dtype else ''
        if ev.kind == 'rest':
            if ev.measure_rest and getattr(self, '_allow_R', True):
                s = self._tw(ev, 0) + 'R' + frac_whole(ev.dur)
            elif ev.measure_rest:
                s = ' '.join('r' + DUR[t] + '.' * d for t, d, _ in split_plain(ev.dur))
            else:
                s = self._tw(ev, 0) + 'r' + dur
            if ev.fermata:
                s += '\\fermata'
            for wd in ev.wedge:
                if wd == 'stop':
                    s += WEDGE[wd]
            for d in ev.dynamics:
                s += '\\' + d
            for wd in ev.wedge:
                if wd != 'stop':
                    s += WEDGE[wd]
            for kind in ev.pedal:
                s += '\\sustainOn' if kind == 'start' else '\\sustainOff'
            for text, place, style in ev.words:
                s += ('^' if place == 'above' else '_') + words_markup(text, style)
            return s

        def one(p):
            t = pitch_ly(p)
            if p in ev.force_acc:
                t += '!'
            elif p in ev.caut_acc:
                t += '?'
            return t
        if len(ev.pitches) == 1:
            p = ev.pitches[0]
            s = self._tw(ev, 0) + one(p) + dur
            if ev.trem_ly:
                s += f':{ev.trem_ly}'
            if p in ev.fing:
                s += f'-{ev.fing[p]}'
            if p in ev.tie_start:
                s += '~'
        else:
            all_tied = ev.tie_start and all(p in ev.tie_start for p in ev.pitches)
            inner = []
            for j, p in enumerate(ev.pitches):
                t = self._tw(ev, j) + one(p)
                if p in ev.fing:
                    t += f'-{ev.fing[p]}'
                if p in ev.tie_start and not all_tied:
                    t += '~'
                inner.append(t)
            s = '<' + ' '.join(inner) + '>' + dur
            if ev.trem_ly:
                s += f':{ev.trem_ly}'
            if all_tied:
                s += '~'
        for a in ev.artic:
            s += ARTIC[a]
        if ev.fermata:
            s += '\\fermata'
        for o in ev.orn:
            s += ORN[o]
        if ev.arpeggio:
            s += '\\arpeggio'
        for wd in ev.wedge:
            if wd == 'stop':
                s += WEDGE[wd]
        for d in ev.dynamics:
            s += '\\' + d
        for wd in ev.wedge:
            if wd != 'stop':
                s += WEDGE[wd]
        for kind in ev.pedal:
            s += '\\sustainOn' if kind == 'start' else '\\sustainOff'
        for text, place, style in ev.words:
            s += ('^' if place == 'above' else '_') + words_markup(text, style)
        if ev.beam:
            s += ev.beam
        if ev.slur_stop:
            s += ')'
        if ev.slur_start:
            s += '('
        return s

    # ------------------------------------------------------------------ lyrics
    def lyric_tokens(self, pid, vkey, verse, label=None):
        toks = []
        for ev in lyric_slots(self.s, pid, vkey):
            ly = ev.lyrics.get(verse)
            if ly is None:
                toks.append('_')
                continue
            t = lq(ly.text)
            if ly.syllabic in ('begin', 'middle'):
                t += ' --'
            elif ly.extend:
                t += ' __'
            toks.append(t)
        while toks and toks[-1] == '_':
            toks.pop()
        if not toks:
            return ''
        if label:
            k = next(j for j, t in enumerate(toks) if t != '_')
            toks[k] = f'\\set stanza = {lq(label)} ' + toks[k]
        lines = [' '.join(toks[j:j + 12]) for j in range(0, len(toks), 12)]
        return '\n      '.join(lines)

    # ------------------------------------------------------------------ document
    def staff_ly(self, st, ind):
        voices = st['voices']
        lyr_voices = {tuple(l['voice']) for l in st.get('lyrics', [])}
        with_ = []
        if st.get('name'):
            with_.append(f'instrumentName = {lq(st["name"])}')
        if st.get('short'):
            with_.append(f'shortInstrumentName = {lq(st["short"])}')
        with_ += st.get('with', [])
        if self.instr:
            with_.append(logger_with(STAFF_GROBS, st['id']))
        w = (' \\with { ' + ' '.join(with_) + ' }') if with_ else ''
        out = [f'{ind}\\new Staff = "{st["id"]}"{w} {{ \\clef "{st["clef"]}"']
        if len(voices) > 1:
            out.append(f'{ind}  <<')
        for j, (pid, vk) in enumerate(voices):
            master = not self._master_done
            self._master_done = True
            mus = self.voice_music(pid, vk, voices, (pid, vk) in lyr_voices, master=master, staff_first=(j == 0))
            out.append(f'{ind}    \\new Voice = "{vname(pid, vk)}" {{\n    {mus}\n{ind}    }}')
        if len(voices) > 1:
            out.append(f'{ind}  >>')
        out.append(f'{ind}}}')
        return '\n'.join(out)

    def lyrics_ly(self, st, ind):
        out = []
        for l in st.get('lyrics', []):
            pid, vk = l['voice']
            for vn in l['verses']:
                lab = f'{vn}.' if l.get('stanza') else None
                toks = self.lyric_tokens(pid, vk, vn, lab)
                if not toks:
                    continue
                w = ''
                if self.instr:
                    w = ' \\with { ' + logger_with(LYRIC_GROBS, f'lyr:{st["id"]}:{vn}') + ' }'
                out.append(f'{ind}\\new Lyrics{w} \\lyricsto "{vname(pid, vk)}" {{\n      {toks}\n{ind}}}')
        return out

    def document(self):
        o = self.o
        L = ['\\version "2.24.0"']
        if self.instr:
            from .harvest import LOGGER_SCM
            L.append(LOGGER_SCM)
        if o.get('staff_size'):
            L.append(f'#(set-global-staff-size {o["staff_size"]})')
        hdr = o.get('header', {})
        L.append('\\header {')
        for k in ('dedication', 'title', 'subtitle', 'poet', 'composer', 'arranger', 'meter', 'piece', 'opus',
                  'copyright'):
            v = hdr.get(k)
            if v:
                L.append(f'  {k} = {lq(v)}')
        L.append('  tagline = ##f')
        L.append('}')
        L.append('\\paper {')
        L.append(f'  #(set-paper-size "{o.get("paper", "a4")}")')
        L.append('  property-defaults.fonts.serif = "TeX Gyre Schola"')
        for x in o.get('paper_extra', []):
            L.append('  ' + x)
        L.append('}')
        self._master_done = False
        L.append('\\score {')
        L.append('  <<')
        for g in self.layout['groups']:
            gt = g.get('type')
            ind = '    '
            if gt:
                with_ = []
                if g.get('name'):
                    with_.append(f'instrumentName = {lq(g["name"])}')
                if g.get('short'):
                    with_.append(f'shortInstrumentName = {lq(g["short"])}')
                with_ += g.get('with', [])
                w = (' \\with { ' + ' '.join(with_) + ' }') if with_ else ''
                L.append(f'    \\new {gt}{w} <<')
                ind = '      '
            for st in g['staves']:
                L.append(self.staff_ly(st, ind))
                L.extend(self.lyrics_ly(st, ind))
            if gt:
                L.append('    >>')
        L.append('  >>')
        L.append('  \\layout {')
        L.append('    \\context { \\Score \\override CodaMark.break-visibility = ##(#f #t #t) '
                 '\\override SegnoMark.break-visibility = ##(#f #t #t) }')
        if self.instr:
            L.append('    \\context { \\Score ' + logger_with(SCORE_GROBS, 'score') + ' }')
        for x in o.get('layout_extra', []):
            L.append('    ' + x)
        L.append('  }')
        L.append('  \\midi { \\tempo 4 = 90 \\context { \\Staff \\remove "Staff_performer" } '
                 '\\context { \\Voice \\consists "Staff_performer" } }')
        L.append('}')
        return '\n'.join(L) + '\n'
