"""Internal model + staff layout -> LilyPond source (absolute pitch), layout-challenge edition.

Layout dict:
  {'segments': [ {'start': i0, 'end': i1, 'groups': [...], 'layout_extra': [...], 'staff_size': 15}, ... ]}
  or {'groups': [...]} (one segment over the whole score).
  group: {'type': 'PianoStaff'|'ChoirStaff'|'StaffGroup'|'GrandStaff'|None, 'name', 'short', 'with': [...],
          'staves': [staff, ...]}
  staff: {'id', 'clef', 'voices': [(pid, vkey)...], 'lyrics': [{'voice','verses','place'}], 'name', 'short',
          'with': [...], 'part_staff': (pid, staffnum)}
Each segment becomes its own \\score block (e.g. an "Amen" at a smaller staff size).
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import Score, display_ql, lyric_verses, ql_to_type, split_plain, staff_roles

ACC = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}
DUR = {'breve': '\\breve', 'whole': '1', 'half': '2', 'quarter': '4', 'eighth': '8',
       '16th': '16', '32nd': '32', '64th': '64'}
KEY_MAJ = {0: 'c', 1: 'g', 2: 'd', 3: 'a', 4: 'e', 5: 'b', 6: 'fis', 7: 'cis', -1: 'f', -2: 'bes',
           -3: 'ees', -4: 'aes', -5: 'des', -6: 'ges', -7: 'ces'}
KEY_MIN = {0: 'a', 1: 'e', 2: 'b', 3: 'fis', 4: 'cis', 5: 'gis', 6: 'dis', 7: 'ais', -1: 'd', -2: 'g',
           -3: 'c', -4: 'f', -5: 'bes', -6: 'ees', -7: 'aes'}
ROLE_CMD = {0: '\\oneVoice', 1: '\\voiceOne', 2: '\\voiceTwo', 3: '\\voiceThree', 4: '\\voiceFour'}
ARTIC = {'staccato': '-.', 'accent': '->', 'tenuto': '--'}
WEDGE = {'crescendo': '\\<', 'diminuendo': '\\>', 'stop': '\\!'}
UNIT = {'quarter': '4', 'half': '2', 'eighth': '8'}


def pitch_ly(p):
    step, alter, octv = p
    name = step.lower() + ACC[alter]
    k = octv - 3
    return name + ("'" * k if k > 0 else ',' * (-k))


def frac_whole(q: F) -> str:
    w = F(q) / 4
    if w == 1:
        return '1'
    return f'1*{w.numerator}/{w.denominator}'


def dur_ly(ev):
    return DUR[ev.dtype] + '.' * ev.dots


def lq(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def vname(pid, vkey):
    return f'v{pid}x{vkey}'


def lyrics_name(pid, vkey, verse):
    return f'L{pid}x{vkey}x{verse}'


def words_markup(text, style):
    if style == 'bold':
        return f'\\markup {{ \\bold {lq(text)} }}'
    if style == 'plain':
        return f'\\markup {{ {lq(text)} }}'
    if style == 'bold-italic':
        return f'\\markup {{ \\bold \\italic {lq(text)} }}'
    return f'\\markup {{ \\italic {lq(text)} }}'


class LilyWriter:
    def __init__(self, score: Score, layout: dict, opts: dict):
        self.s = score
        self.layout = layout
        self.o = opts
        self._plan = None
        segs = layout.get('segments')
        if not segs:
            segs = [{'start': 0, 'end': len(score.measures), 'groups': layout['groups'],
                     'layout_extra': layout.get('layout_extra', [])}]
        self.segments = segs
        # staff id lookup (pid, staffnum) -> staff id, per segment
        self.staff_ids = []
        for seg in segs:
            ids = {}
            for g in seg['groups']:
                for st in g['staves']:
                    for pid, vk in st['voices']:
                        sn = score.part(pid).voice(vk).staff
                        ids.setdefault((pid, sn), st['id'])
                    if st.get('part_staff'):
                        ids[tuple(st['part_staff'])] = st['id']
            self.staff_ids.append(ids)

    # ------------------------------------------------------------------ timing
    def timing_plan(self):
        if self._plan is not None:
            return self._plan
        s = self.s
        nm = len(s.measures)
        plan = []
        pos = F(0)
        for i, mi in enumerate(s.measures):
            e = {'partial': None, 'reset': None, 'bar': None, 'check': False, 'mlen': None}
            if mi.dur > mi.nominal:
                e['mlen'] = mi.dur / 4
            elif i > 0 and s.measures[i - 1].dur > s.measures[i - 1].nominal:
                e['mlen'] = mi.nominal / 4
            nominal = mi.nominal if mi.dur <= mi.nominal else mi.dur
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
            elif right == 'dashed':
                bar = '!'
            at_bar_end = pos >= nominal
            if not at_bar_end and i + 1 < nm and bar is None:
                bar = '|'
            e['bar'] = bar
            e['check'] = at_bar_end
            if at_bar_end:
                pos = F(0)
            plan.append(e)
        for i in range(nm - 1):
            if plan[i + 1]['reset'] is not None:
                plan[i]['check'] = False
        self._plan = plan
        return plan

    # ------------------------------------------------------------------ voices
    def master_cmds_start(self, i, seg_start, seg_idx):
        s = self.s
        mi = s.measures[i]
        out = []
        if i == seg_start:
            if self.o.get('forced_breaks'):
                out.append('\\autoLineBreaksOff')
                if self.o.get('forced_pages', True):
                    out.append('\\autoPageBreaksOff')
            if seg_start > 0:
                out.append(f'\\set Score.currentBarNumber = #{mi.number}')
        elif mi.brk == 'page':
            out.append('\\pageBreak')
        elif mi.brk == 'system':
            out.append('\\break')
        # volta commands
        cmds = []
        if i > seg_start and s.measures[i - 1].volta_end:
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
                out.append(f'\\tempo {t}{mm}'.replace('\\tempo  ', '\\tempo '))
            elif k == 'segno':
                out.append('\\segnoMark 1')
            elif k == 'coda':
                out.append('\\codaMark 1')
            elif k == 'rehearsal':
                out.append(f'\\mark \\markup {{ \\box \\bold {lq(mk["text"])} }}')
            elif k == 'words':
                texts.append(words_markup(mk['text'], mk.get('style', 'italic')).replace('\\markup ', '', 1))
        if texts:
            out.append('\\textMark \\markup \\column { ' + ' '.join(texts) + ' }' if len(texts) > 1
                       else '\\textMark \\markup ' + texts[0])
        return out

    def master_cmds_end(self, i):
        mi = self.s.measures[i]
        parts = []
        for mk in mi.end_marks:
            t = words_markup(mk['text'], mk.get('style', 'italic')).replace('\\markup ', '', 1)
            if mk.get('coda_sign'):
                t = f'{{ \\line {{ {t[1:-1]} \\hspace #0.5 \\raise #0.6 \\musicglyph "scripts.coda" }} }}'
            parts.append(t)
        if not parts:
            return []
        if len(parts) == 1:
            return ['\\textEndMark \\markup ' + parts[0]]
        return ['\\textEndMark \\markup \\right-column { ' + ' '.join(parts) + ' }']

    def voice_music(self, seg_idx, pid, vkey, staff_voices, lyrics_voice, master=False, staff_first=False):
        s = self.s
        seg = self.segments[seg_idx]
        a, b = seg['start'], seg['end']
        part = s.part(pid)
        home = part.voice(vkey).staff
        plan = self.timing_plan()
        out = []
        self._cur_staff = home
        self._home = home
        self._ids = self.staff_ids[seg_idx]
        self._pid = pid
        self._cue = False
        self._stem = None
        if lyrics_voice:
            out.append("\\set melismaBusyProperties = #'()")
        out.append('\\autoBeamOff')
        prev_role = None
        for i in range(a, b):
            mi = s.measures[i]
            e = plan[i]
            line = []
            if master:
                line += self.master_cmds_start(i, a, seg_idx)
            if (i == a or mi.time) and master:
                (tn, td), sym = s.current_time(i)
                if (tn, td) in ((4, 4), (2, 2)):
                    line.append('\\defaultTimeSignature' if sym in ('common', 'cut') else '\\numericTimeSignature')
                line.append(f'\\time {tn}/{td}')
            if (i == a or mi.key) and staff_first:
                fifths, mode = mi.key or s.current_key(i)
                tonic = (KEY_MIN if mode == 'minor' else KEY_MAJ)[fifths]
                line.append(f'\\key {tonic} \\{mode}')
            if master and e['mlen'] is not None:
                ml = e['mlen']
                line.append(f'\\set Timing.measureLength = #(ly:make-moment {ml.numerator}/{ml.denominator})')
            if master and e['partial'] and i == a:
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
            self._allow_R = (e['reset'] is None and e['partial'] is None and
                             (i + 1 >= len(s.measures) or plan[i + 1]['reset'] is None))
            line.extend(self.events_ly(evs))
            if tot < mi.dur:
                line.append('s' + frac_whole(mi.dur - tot))
            if master:
                line += self.master_cmds_end(i)
            if master and e['bar'] and not (i == b - 1 and e['bar'] == '|'):
                line.append(f'\\bar "{e["bar"]}"')
            if e['check']:
                line.append('|')
            out.append(' '.join(line))
        if self._cue:
            out.append('\\unset fontSize')
        if master and s.measures[b - 1].volta_end:
            out.append("\\set Score.repeatCommands = #'((volta #f))")
        return '\n    '.join(out)

    def events_ly(self, evs):
        out = []
        in_tup = False
        tup_ratio = None
        for ev in evs:
            if ev.kind == 'clef':
                out.append(f'\\clef "{ev.clef}"')
                continue
            if ev.kind == 'space':
                if in_tup:
                    out.append('}')
                    in_tup = False
                out.append('s' + frac_whole(ev.dur))
                continue
            # cross-staff
            want = ev.staff or self._home
            if want != self._cur_staff:
                out.append(f'\\change Staff = "{self._ids[(self._pid, want)]}"')
                self._cur_staff = want
            # explicit stems
            if ev.kind == 'note' and ev.stem != self._stem:
                out.append({'up': '\\stemUp', 'down': '\\stemDown', None: '\\stemNeutral'}[ev.stem])
                self._stem = ev.stem
            # cue size
            if ev.cue and not self._cue:
                out.append('\\set fontSize = #-4')
                self._cue = True
            elif not ev.cue and self._cue:
                out.append('\\unset fontSize')
                self._cue = False
            if ev.tuplet and (not in_tup or ev.tuplet != tup_ratio or ev.tuplet_start):
                if in_tup:
                    out.append('}')
                a, n = ev.tuplet
                span = ''
                if not ev.tuplet_start:
                    sp = display_ql(ev.dtype, 0) * n
                    t = ql_to_type(sp)
                    if t:
                        span = ' ' + DUR[t[0]] + '.' * t[1]
                out.append(f'\\tuplet {a}/{n}{span} {{')
                in_tup, tup_ratio = True, ev.tuplet
            elif not ev.tuplet and in_tup:
                out.append('}')
                in_tup = False
            out.append(self.event_ly(ev))
            if ev.tuplet and ev.tuplet_stop and in_tup:
                out.append('}')
                in_tup = False
        if in_tup:
            out.append('}')
        return out

    def event_ly(self, ev):
        if ev.kind == 'rest':
            if ev.measure_rest and getattr(self, '_allow_R', True):
                s = 'R' + frac_whole(ev.dur)
            elif ev.measure_rest:
                s = ' '.join('r' + DUR[t] + '.' * d for t, d, _ in split_plain(ev.dur))
            else:
                s = 'r' + dur_ly(ev)
            if ev.fermata:
                s += '\\fermata'
            for text, place, style in ev.words:
                s += ('^' if place == 'above' else '_') + words_markup(text, style)
            return s
        if len(ev.pitches) == 1:
            p = ev.pitches[0]
            s = pitch_ly(p) + dur_ly(ev)
            if p in ev.tie_start:
                s += '~'
        else:
            all_tied = ev.tie_start and all(p in ev.tie_start for p in ev.pitches)
            inner = []
            for p in ev.pitches:
                t = pitch_ly(p)
                if p in ev.tie_start and not all_tied:
                    t += '~'
                inner.append(t)
            s = '<' + ' '.join(inner) + '>' + dur_ly(ev)
            if all_tied:
                s += '~'
        for a in ev.artic:
            s += ARTIC.get(a, '')
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
        if ev.beam:
            s += ev.beam
        if ev.slur_stop:
            s += ')'
        if ev.slur_start:
            s += '('
        return s

    # ------------------------------------------------------------------ lyrics
    def lyric_tokens(self, seg_idx, pid, vkey, verse, label=None):
        seg = self.segments[seg_idx]
        part = self.s.part(pid)
        toks = []
        for m in part.measures[seg['start']:seg['end']]:
            for ev in m.get(vkey, []):
                if ev.kind != 'note' or ev.is_tie_continuation():
                    continue
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
        if all(t == '_' for t in toks):
            return ''
        if label:
            k = next(j for j, t in enumerate(toks) if t != '_')
            toks[k] = f'\\set stanza = {lq(label)} ' + toks[k]
        lines, cur = [], []
        for t in toks:
            cur.append(t)
            if len(cur) >= 12:
                lines.append(' '.join(cur))
                cur = []
        if cur:
            lines.append(' '.join(cur))
        return '\n      '.join(lines)

    # ------------------------------------------------------------------ document
    def staff_ly(self, seg_idx, st, ind):
        voices = st['voices']
        lyr_voices = {tuple(l['voice']) for l in st.get('lyrics', [])}
        with_ = []
        if st.get('name'):
            with_.append(f'instrumentName = {self._markup_name(st["name"])}')
        if st.get('short'):
            with_.append(f'shortInstrumentName = {self._markup_name(st["short"])}')
        for x in st.get('with', []):
            with_.append(x)
        w = (' \\with { ' + ' '.join(with_) + ' }') if with_ else ''
        clef = st['clef']
        out = [f'{ind}\\new Staff = "{st["id"]}"{w} {{ \\clef "{clef}"']
        if len(voices) > 1:
            out.append(f'{ind}  <<')
        for j, (pid, vk) in enumerate(voices):
            master = not self._master_done
            self._master_done = True
            mus = self.voice_music(seg_idx, pid, vk, voices, (pid, vk) in lyr_voices, master=master,
                                   staff_first=(j == 0))
            pre = st.get('voice_cmds', {}).get((pid, vk))
            if pre:
                mus = pre + '\n    ' + mus
            out.append(f'{ind}    \\new Voice = "{vname(pid, vk)}" {{\n    {mus}\n{ind}    }}')
        if len(voices) > 1:
            out.append(f'{ind}  >>')
        out.append(f'{ind}}}')
        return '\n'.join(out)

    def _markup_name(self, name):
        if isinstance(name, (list, tuple)):
            return '\\markup \\center-column { ' + ' '.join(lq(x) for x in name) + ' }'
        return lq(name)

    def lyrics_ly(self, seg_idx, st, ind):
        out = []
        above = [l for l in st.get('lyrics', []) if l.get('place') == 'above']
        below = [l for l in st.get('lyrics', []) if l.get('place') != 'above']
        for group, align in ((above, 'alignAboveContext'), (below, None)):
            for l in group:
                pid, vk = l['voice']
                verses = l['verses']
                for vn in (reversed(verses) if align else verses):
                    lab = None
                    if l.get('stanza', len(verses) > 1):
                        lab = l.get('labels', {}).get(vn, f'{vn}.')
                    toks = self.lyric_tokens(seg_idx, pid, vk, vn, lab)
                    if not toks:
                        continue
                    stanza = ''
                    w = f' \\with {{ {align} = "{st["id"]}" }}' if align else ''
                    out.append(f'{ind}\\new Lyrics = "{lyrics_name(pid, vk, vn)}"{w} \\lyricsto "{vname(pid, vk)}" '
                               f'{{ {stanza}\n      {toks}\n{ind}}}')
        return out

    def document(self):
        o = self.o
        L = ['\\version "2.24.0"']
        sz = o.get('staff_size')
        if sz:
            L.append(f'#(set-global-staff-size {sz})')
        hdr = o.get('header', {})
        L.append('\\header {')
        for k in ('dedication', 'title', 'subtitle', 'subsubtitle', 'poet', 'composer', 'arranger', 'meter',
                  'piece', 'opus', 'instrument', 'copyright'):
            v = hdr.get(k)
            if v:
                L.append(f'  {k} = {v if v.startswith(chr(92) + "markup") else lq(v)}')
        L.append('  tagline = ##f')
        L.append('}')
        L.append('\\paper {')
        L.append(f'  #(set-paper-size "{o.get("paper", "a4")}")')
        if o.get('font'):
            L.append(f'  property-defaults.fonts.serif = "{o["font"]}"')
        for x in o.get('paper_extra', []):
            L.append('  ' + x)
        L.append('}')
        for x in o.get('before_markup', []):
            L.append(x)
        for si, seg in enumerate(self.segments):
            self._master_done = False
            L.append('\\score {')
            L.append('  <<')
            for g in seg['groups']:
                gt = g.get('type')
                ind = '    '
                if gt:
                    with_ = []
                    if g.get('name'):
                        with_.append(f'instrumentName = {self._markup_name(g["name"])}')
                    if g.get('short'):
                        with_.append(f'shortInstrumentName = {self._markup_name(g["short"])}')
                    with_ += g.get('with', [])
                    w = (' \\with { ' + ' '.join(with_) + ' }') if with_ else ''
                    L.append(f'    \\new {gt}{w} <<')
                    ind = '      '
                for st in g['staves']:
                    L.append(self.staff_ly(si, st, ind))
                    L.extend(self.lyrics_ly(si, st, ind))
                if gt:
                    L.append('    >>')
            L.append('  >>')
            L.append('  \\layout {')
            if seg.get('staff_size'):
                L.append(f'    #(layout-set-staff-size {seg["staff_size"]})')
            L.append('    \\context { \\Score \\override CodaMark.break-visibility = ##(#f #t #t) '
                     '\\override SegnoMark.break-visibility = ##(#f #t #t) }')
            for x in o.get('layout_extra', []) + seg.get('layout_extra', []):
                L.append('    ' + x)
            L.append('  }')
            L.append('  \\midi { \\tempo 4 = 90 \\context { \\Staff \\remove "Staff_performer" } '
                     '\\context { \\Voice \\consists "Staff_performer" } }')
            L.append('}')
        for x in o.get('after_markup', []):
            L.append(x)
        return '\n'.join(L) + '\n'
