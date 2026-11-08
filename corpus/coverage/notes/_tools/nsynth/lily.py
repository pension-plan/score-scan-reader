"""Internal model + staff layout -> LilyPond source (absolute pitch).

coverage/notes copy of corpus/challenge/rhythm/_tools/rsynth/lily.py, extended with explicit stem
directions for every stemmed note (\\stemUp / \\stemDown whenever the direction changes), single-note
tremolos (c4:16), two-note tremolos (\\repeat tremolo), secondary-beam breaks
(stemRightBeamCount / stemLeftBeamCount), CueVoice contexts and words above notes.

Rhythm-challenge copy of corpus/synthetic/_tools/synth/lily.py, extended with grace
notes, explicit beams (\\autoBeamOff + [ ]), hidden tuplets, multi-measure rests,
rehearsal marks / tempo words, forced system/page breaks and named Lyrics contexts
(used by the event-dump verification)."""
from __future__ import annotations

from fractions import Fraction as F

from .model import Score, lyric_verses, staff_roles

ACC = {0: '', 1: 'is', -1: 'es', 2: 'isis', -2: 'eses'}
DUR = {'breve': '\\breve', 'whole': '1', 'half': '2', 'quarter': '4', 'eighth': '8',
       '16th': '16', '32nd': '32', '64th': '64'}
KEY_MAJ = {0: 'c', 1: 'g', 2: 'd', 3: 'a', 4: 'e', 5: 'b', 6: 'fis', 7: 'cis', -1: 'f', -2: 'bes',
           -3: 'ees', -4: 'aes', -5: 'des', -6: 'ges', -7: 'ces'}
KEY_MIN = {0: 'a', 1: 'e', 2: 'b', 3: 'fis', 4: 'cis', 5: 'gis', 6: 'dis', 7: 'ais', -1: 'd', -2: 'g',
           -3: 'c', -4: 'f', -5: 'bes', -6: 'ees', -7: 'aes'}
ROLE_CMD = {0: '\\oneVoice', 1: '\\voiceOne', 2: '\\voiceTwo', 3: '\\voiceThree', 4: '\\voiceFour'}
ARTIC = {'staccato': '-.', 'accent': '->', 'tenuto': '--'}
GRACE_CMD = {'grace': '\\grace', 'acciaccatura': '\\acciaccatura', 'appoggiatura': '\\appoggiatura',
             'slashed': '\\slashedGrace'}


def ly_dur_of_ql(q):
    from .model import ql_to_type
    t = ql_to_type(F(q))
    if t:
        return DUR[t[0]] + '.' * t[1]
    return frac_whole(q)


def lyrics_name(pid, vkey, verse):
    return f'L{vname(pid, vkey)}x{verse}'


def pitch_ly(p):
    step, alter, octv = p
    name = step.lower() + ACC[alter]
    if name == 'ees':
        name = 'ees'
    k = octv - 3
    return name + ("'" * k if k > 0 else ',' * (-k))


def frac_whole(q: F) -> str:
    """quarters -> '1*n/d' whole-note multiplier string"""
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


def default_layout(score: Score, choir_name=None):
    """open layout: one staff per part staff; vocal parts grouped in a ChoirStaff,
    piano parts in PianoStaff."""
    groups = []
    vocal = []
    for p in score.parts:
        if p.instrument == 'piano' or p.staves > 1:
            if vocal:
                groups.append({'type': 'ChoirStaff' if len(vocal) > 1 else None, 'staves': vocal})
                vocal = []
            staves = []
            for s in range(1, p.staves + 1):
                staves.append({'id': f'st{p.id}s{s}', 'clef': p.clefs[s - 1],
                               'voices': [(p.id, v.key) for v in p.voices if v.staff == s],
                               'lyrics': []})
            groups.append({'type': 'PianoStaff', 'name': p.name, 'short': p.abbr, 'staves': staves})
        else:
            lyr = []
            for v in p.voices:
                vs = lyric_verses(p, v.key)
                if vs:
                    lyr.append({'voice': (p.id, v.key), 'verses': vs, 'place': 'below'})
            if len(lyr) == 2:
                lyr[0]['place'] = 'above'
            vocal.append({'id': f'st{p.id}', 'clef': p.clefs[0], 'name': p.name, 'short': p.abbr,
                          'voices': [(p.id, v.key) for v in p.voices], 'lyrics': lyr})
    if vocal:
        groups.append({'type': 'ChoirStaff' if len(vocal) > 1 else None, 'staves': vocal})
    return {'groups': groups}


class LilyWriter:
    def __init__(self, score: Score, layout: dict, opts: dict):
        self.s = score
        self.layout = layout
        self.o = opts
        self._master_done = False

    # ------------------------------------------------------------------ voices
    def timing_plan(self):
        """Per measure: partial / measurePosition reset / barline / barcheck."""
        if getattr(self, '_plan', None) is not None:
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
            nominal = mi.nominal
            if mi.dur > mi.nominal:
                nominal = mi.dur
            if i == 0 and mi.dur < mi.nominal:
                e['partial'] = frac_whole(mi.dur)
                pos = mi.nominal - mi.dur
            elif i == nm - 1 and pos == 0 and mi.dur < mi.nominal:
                pass        # incomplete final bar: starts on the barline and simply ends early
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
        # no bar check right before a measurePosition reset (the reset in the
        # master voice is processed before other voices' checks at that moment)
        for i in range(nm - 1):
            if plan[i + 1]['reset'] is not None:
                plan[i]['check'] = False
        self._plan = plan
        return plan

    def voice_music(self, pid, vkey, staff_voices, lyrics_voice, master=False, staff_first=False):
        s = self.s
        part = s.part(pid)
        plan = self.timing_plan()
        out = []
        if lyrics_voice:
            out.append("\\set melismaBusyProperties = #'()")
        out.append('\\autoBeamOff')
        if master:
            if any(ev.multirest for p_ in s.parts for mm in p_.measures for evs in mm.values() for ev in evs):
                out.append('\\set Score.skipBars = ##t')
            if self.o.get('forced_breaks', True):
                out.append('\\autoLineBreaksOff \\autoPageBreaksOff')
        if self.o.get('stem_cmd'):
            out.append(self.o['stem_cmd'])
        prev_role = None
        self._stem = None
        self._left1 = False
        for i, mi in enumerate(s.measures):
            e = plan[i]
            line = []
            if (i == 0 or mi.time) and master:
                (tn, td), sym = s.current_time(i)
                if (tn, td) in ((4, 4), (2, 2)):
                    line.append('\\defaultTimeSignature' if sym in ('common', 'cut') else '\\numericTimeSignature')
                line.append(f'\\time {tn}/{td}')
            if (i == 0 or mi.key) and staff_first:
                fifths, mode = mi.key or s.current_key(i)
                tonic = (KEY_MIN if mode == 'minor' else KEY_MAJ)[fifths]
                line.append(f'\\key {tonic} \\{mode}')
            if master and e['mlen'] is not None:
                ml = e['mlen']
                line.append(f'\\set Timing.measureLength = #(ly:make-moment {ml.numerator}/{ml.denominator})')
            if master and e['partial']:
                line.append(f'\\partial {e["partial"]}')
            if master and e['reset'] is not None:
                w = e['reset']
                line.append(f'\\set Timing.measurePosition = #(ly:make-moment {w.numerator}/{w.denominator})')
            if master and mi.rehearsal:
                line.append(f'\\mark {lq(mi.rehearsal)}')
            if master and mi.words:
                line.append(f'\\tempo {lq(mi.words)}')
            roles = staff_roles([((p_, k), s.part(p_).measures[i].get(k, [])) for p_, k in staff_voices])
            role = roles.get((pid, vkey), 0) if len(staff_voices) > 1 else None
            if role is not None and role != prev_role:
                line.append(ROLE_CMD[role])
                prev_role = role
                self._stem = '?'      # role commands change Stem.direction: re-state it
            evs = part.measures[i].get(vkey, [])
            if any(ev.multirest_cont for ev in evs):
                assert not line or all(x.startswith('\\voice') or x == '\\oneVoice' for x in line), (i, line)
                continue
            tot = sum((x.dur for x in evs), F(0))
            nm_ = len(s.measures)
            self._allow_R = e['reset'] is None and (i + 1 >= nm_ or plan[i + 1]['reset'] is None)
            line.extend(self.events_ly(evs))
            if tot < mi.dur:
                line.append('s' + frac_whole(mi.dur - tot))
            blk = max([ev.multirest for ev in evs] + [1])
            last = i + blk - 1          # multi-measure rest: barline/check/break of the block's last bar
            e_end = plan[last]
            if master and e_end['bar']:
                line.append(f'\\bar "{e_end["bar"]}"')
            if e_end['check']:
                line.append('|')
            if master and last + 1 < nm_:
                nxt = s.measures[last + 1]
                if nxt.new_page:
                    line.append('\\pageBreak')
                elif nxt.new_system:
                    line.append('\\break')
            out.append(' '.join(line))
        return '\n    '.join(out)

    def events_ly(self, evs):
        out = []
        in_tup = False
        tup_ratio = None
        k = 0
        while k < len(evs):
            ev = evs[k]
            if ev.kind == 'clef':
                out.append(f'\\clef "{ev.clef}"')
                k += 1
                continue
            if ev.kind == 'space':
                if in_tup:
                    out.append('}')
                    in_tup = False
                out.append('s' + frac_whole(ev.dur))
                k += 1
                continue
            if ev.grace:
                j = k
                while j < len(evs) and evs[j].grace == ev.grace:
                    j += 1
                grp = [self.event_ly(x) for x in evs[k:j]]
                cmd = GRACE_CMD[ev.grace]
                if len(grp) == 1:
                    out.append(f'{cmd} {grp[0]}')
                else:
                    out.append(f'{cmd} {{ ' + ' '.join(grp) + ' }')
                k = j
                continue
            if ev.kind == 'note' and ev.stem and ev.stem != self._stem:
                out.append('\\stemUp' if ev.stem == 'up' else '\\stemDown')
                self._stem = ev.stem
            if ev.trem2 == 'start':
                nxt = evs[k + 1]
                assert nxt.trem2 == 'stop'
                out.append(f'\\repeat tremolo {ev.trem2_reps} {{ ' + self.trem_note_ly(ev) + ' ' +
                           self.trem_note_ly(nxt) + ' }')
                k += 2
                continue
            if self._left1 and ev.kind in ('note', 'rest'):
                out.append('\\set stemLeftBeamCount = #1')
                self._left1 = False
            if ev.sub_break:
                out.append('\\set stemRightBeamCount = #1')
                self._left1 = True
            if ev.tuplet and (not in_tup or ev.tuplet != tup_ratio or ev.tuplet_start):
                if in_tup:
                    out.append('}')
                a, n = ev.tuplet
                span = ''
                if not ev.tuplet_start:
                    from .model import display_ql, ql_to_type
                    sp = display_ql(ev.dtype, 0) * n
                    t = ql_to_type(sp)
                    if t:
                        span = ' ' + DUR[t[0]] + '.' * t[1]
                if ev.tuplet_hidden:
                    out.append('\\once \\omit TupletNumber \\once \\omit TupletBracket')
                out.append(f'\\tuplet {a}/{n}{span} {{')
                in_tup, tup_ratio = True, ev.tuplet
            elif not ev.tuplet and in_tup:
                out.append('}')
                in_tup = False
            out.append(self.event_ly(ev))
            if ev.tuplet and ev.tuplet_stop and in_tup:
                out.append('}')
                in_tup = False
            k += 1
        if in_tup:
            out.append('}')
        return out

    def event_ly(self, ev):
        if ev.kind == 'rest':
            if ev.measure_rest and ev.multirest > 1:
                s = 'R' + ly_dur_of_ql(ev.dur) + f'*{ev.multirest}'
                if ev.multirest_hbar:
                    s = '\\once \\override MultiMeasureRest.expand-limit = #1 ' + s
            elif ev.measure_rest and getattr(self, '_allow_R', True):
                s = 'R' + ly_dur_of_ql(ev.dur)
            elif ev.measure_rest:
                from .model import split_plain
                s = ' '.join('r' + DUR[t] + '.' * d for t, d, _ in split_plain(ev.dur))
            else:
                s = 'r' + dur_ly(ev)
            if ev.fermata:
                s += '\\fermata'
            if ev.beam_start:
                s += '['
            if ev.beam_stop:
                s += ']'
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
        if ev.trem:
            s += f':{ev.trem}'
        if ev.beam_start:
            s += '['
        if ev.beam_stop:
            s += ']'
        if ev.words:
            s += '^' + lq(ev.words)
        for a in ev.artic:
            s += ARTIC.get(a, '')
        if ev.fermata:
            s += '\\fermata'
        for d in ev.dynamics:
            s += '\\' + d
        if ev.slur_stop:
            s += ')'
        if ev.slur_start:
            s += '('
        return s

    def trem_note_ly(self, ev):
        if len(ev.pitches) == 1:
            return pitch_ly(ev.pitches[0]) + ev.trem2_sub
        return '<' + ' '.join(pitch_ly(p) for p in ev.pitches) + '>' + ev.trem2_sub

    # ------------------------------------------------------------------ lyrics
    def lyric_tokens(self, pid, vkey, verse):
        part = self.s.part(pid)
        toks = []
        for m in part.measures:
            for ev in m.get(vkey, []):
                if ev.kind != 'note' or ev.grace:
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
        # wrap
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
    def staff_ly(self, st, ind):
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
        out = [f'{ind}\\new Staff = "{st["id"]}"{w} {{ \\clef "{st["clef"]}"']
        if len(voices) > 1:
            out.append(f'{ind}  <<')
        for j, (pid, vk) in enumerate(voices):
            master = not self._master_done
            self._master_done = True
            mus = self.voice_music(pid, vk, voices, (pid, vk) in lyr_voices, master=master, staff_first=(j == 0))
            is_cue = any(ev.cue for m in self.s.part(pid).measures for ev in m.get(vk, []))
            ctx = 'CueVoice' if is_cue else 'Voice'
            out.append(f'{ind}    \\new {ctx} = "{vname(pid, vk)}" {{\n    {mus}\n{ind}    }}')
        if len(voices) > 1:
            out.append(f'{ind}  >>')
        out.append(f'{ind}}}')
        return '\n'.join(out)

    def _markup_name(self, name):
        if isinstance(name, (list, tuple)):
            return '\\markup \\center-column { ' + ' '.join(lq(x) for x in name) + ' }'
        return lq(name)

    def lyrics_ly(self, st, ind):
        out = []
        above = [l for l in st.get('lyrics', []) if l.get('place') == 'above']
        below = [l for l in st.get('lyrics', []) if l.get('place') != 'above']
        for group, align in ((above, 'alignAboveContext'), (below, None)):
            for l in group:
                pid, vk = l['voice']
                verses = l['verses']
                for vn in (reversed(verses) if align else verses):
                    toks = self.lyric_tokens(pid, vk, vn)
                    if not toks:
                        continue
                    stanza = ''
                    if l.get('stanza', len(verses) > 1):
                        lab = l.get('labels', {}).get(vn, f'{vn}.')
                        stanza = f'\\set stanza = {lq(lab)} '
                    w = f' \\with {{ {align} = "{st["id"]}" }}' if align else ''
                    out.append(f'{ind}\\new Lyrics = "{lyrics_name(pid, vk, vn)}"{w} \\lyricsto "{vname(pid, vk)}" '
                               f'{{ {stanza}\n      {toks}\n{ind}}}')
        return out

    def document(self):
        o = self.o
        s = self.s
        L = ['\\version "2.24.0"']
        sz = o.get('staff_size')
        if sz:
            L.append(f'#(set-global-staff-size {sz})')
        hdr = o.get('header', {})
        L.append('\\header {')
        for k in ('dedication', 'title', 'subtitle', 'poet', 'composer', 'arranger', 'meter', 'piece', 'opus',
                  'copyright'):
            v = hdr.get(k)
            if v:
                L.append(f'  {k} = {lq(v) if not v.startswith("\\markup") else v}')
        L.append('  tagline = ##f')
        L.append('}')
        L.append('\\paper {')
        L.append(f'  #(set-paper-size "{o.get("paper", "a4")}")')
        if o.get('font'):
            L.append(f'  property-defaults.fonts.serif = "{o["font"]}"')
        for x in o.get('paper_extra', []):
            L.append('  ' + x)
        L.append('}')
        L.append('\\score {')
        L.append('  <<')
        for g in self.layout['groups']:
            gt = g.get('type')
            ind = '    '
            if gt:
                with_ = []
                if g.get('name'):
                    with_.append(f'instrumentName = {self._markup_name(g["name"])}')
                if g.get('short'):
                    with_.append(f'shortInstrumentName = {self._markup_name(g["short"])}')
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
        for x in o.get('layout_extra', []):
            L.append('    ' + x)
        L.append('  }')
        L.append('  \\midi { \\tempo 4 = 90 \\context { \\Staff \\remove "Staff_performer" } '
                 '\\context { \\Voice \\consists "Staff_performer" } }')
        L.append('}')
        return '\n'.join(L) + '\n'
