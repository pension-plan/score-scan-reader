"""Model (+ harvested engraving facts) -> MusicXML 4.0 partwise truth.

Derived from corpus/challenge/layout/_tools/lsynth/mxl.py (copied, extended): grace notes,
octave-shift, ornaments (trill, mordent, turn, tremolo), arpeggiate, fingering, breath marks,
staccatissimo / strong-accent, <stem> and <beam> exactly as engraved, printed accidentals
(incl. parentheses / cautionary), key cancellation, tuplet bracket visibility, page layout
defaults, credits, part groups, print breaks, voltas, repeats, tempo/metronome, rehearsal marks.
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from xml.sax.saxutils import escape, quoteattr

from .acc import GLYPH, acc_value
from .model import Event, Score, staff_roles

CLEF_XML = {
    'treble': ('G', 2, 0), 'treble_8': ('G', 2, -1), 'treble^8': ('G', 2, 1),
    'bass': ('F', 4, 0), 'bass_8': ('F', 4, -1), 'alto': ('C', 3, 0), 'tenor': ('C', 4, 0),
    'soprano': ('C', 1, 0), 'percussion': ('percussion', None, 0),
}
BAR_STYLE = {'final': 'light-heavy', 'double': 'light-light', 'repeat-end': 'light-heavy'}
OTTAVA = {1: ('down', 8), 2: ('down', 15), -1: ('up', 8), -2: ('up', 15)}


def _lcm(a, b):
    return a * b // math.gcd(a, b)


def divisions_for(score: Score):
    d = 1
    for p in score.parts:
        for m in p.measures:
            for evs in m.values():
                for e in evs:
                    d = _lcm(d, F(e.dur).denominator)
    for m in score.measures:
        d = _lcm(d, F(m.dur).denominator)
    return d


def _attr(d):
    return ''.join(f' {k}={quoteattr(str(v))}' for k, v in d.items() if v is not None)


def _words_xml(text, style):
    a = {}
    if style == 'italic':
        a['font-style'] = 'italic'
    elif style == 'bold':
        a['font-weight'] = 'bold'
    return f'<words{_attr(a)}>{escape(text)}</words>'


def mark_xml(mk, staff):
    st = f'<staff>{staff}</staff>' if staff else ''
    kind = mk['kind']
    dts = []
    sound = None
    if kind == 'tempo':
        if mk.get('text'):
            dts.append(_words_xml(mk['text'], 'bold'))
        if mk.get('bpm'):
            dot = '<beat-unit-dot/>' if mk.get('dots') else ''
            par = ' parentheses="yes"' if mk.get('text') else ''
            dts.append(f'<metronome{par}><beat-unit>{mk.get("unit", "quarter")}</beat-unit>{dot}'
                       f'<per-minute>{mk["bpm"]}</per-minute></metronome>')
            q = F(mk['bpm']) * {'quarter': 1, 'half': 2, 'eighth': F(1, 2)}[mk.get('unit', 'quarter')]
            if mk.get('dots'):
                q = q * F(3, 2)
            sound = f'<sound tempo="{float(q):g}"/>'
        elif mk.get('sound_tempo'):
            sound = f'<sound tempo="{mk["sound_tempo"]}"/>'
    elif kind == 'segno':
        dts.append('<segno/>')
        sound = '<sound segno="segno"/>'
    elif kind == 'coda':
        dts.append('<coda/>')
        sound = '<sound coda="coda"/>'
    elif kind == 'rehearsal':
        dts.append(f'<rehearsal enclosure="square">{escape(mk["text"])}</rehearsal>')
    elif kind == 'words':
        dts.append(_words_xml(mk['text'], mk.get('style', 'italic')))
        snd = mk.get('sound')
        if snd:
            sound = '<sound' + ''.join(f' {k}="{v}"' for k, v in snd.items()) + '/>'
    else:
        raise ValueError(kind)
    body = ''.join(f'<direction-type>{d}</direction-type>' for d in dts)
    return f'      <direction placement="above">{body}{st}{sound or ""}</direction>'


def _clef_xml(name, number, ind):
    sign, line, oc = CLEF_XML[name]
    na = f' number="{number}"' if number else ''
    s = f'{ind}<clef{na}><sign>{sign}</sign>'
    if line is not None:
        s += f'<line>{line}</line>'
    if oc:
        s += f'<clef-octave-change>{oc}</clef-octave-change>'
    return s + '</clef>'


def write_musicxml(score: Score, path: str, beams=None, tuplet_vis=None, key_cancel=None,
                   software='coverage/perf corpus generator', date='2026-11-08'):
    beams = beams or {}
    tuplet_vis = tuplet_vis or {}
    key_cancel = key_cancel or set()
    div = divisions_for(score)
    out = []
    w = out.append
    w('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    w('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
      '"http://www.musicxml.org/dtds/partwise.dtd">')
    w('<score-partwise version="4.0">')
    if score.title:
        w(f'  <work><work-title>{escape(score.title)}</work-title></work>')
    w('  <identification>')
    for role, val in (('composer', score.composer), ('lyricist', score.lyricist), ('arranger', score.arranger)):
        if val:
            w(f'    <creator type="{role}">{escape(val)}</creator>')
    if score.rights:
        w(f'    <rights>{escape(score.rights)}</rights>')
    w('    <encoding>')
    w(f'      <software>{escape(software)}</software>')
    w(f'      <encoding-date>{date}</encoding-date>')
    w('    </encoding>')
    if score.source:
        w(f'    <source>{escape(score.source)}</source>')
    w('  </identification>')
    if score.page:
        pg = score.page
        mm = pg['staff_size'] * 25.4 / 72.0
        tenths = lambda v: f'{v / mm * 40:.2f}'
        w('  <defaults>')
        w(f'    <scaling><millimeters>{mm:.4f}</millimeters><tenths>40</tenths></scaling>')
        w(f'    <page-layout><page-height>{tenths(pg["height_mm"])}</page-height>'
          f'<page-width>{tenths(pg["width_mm"])}</page-width></page-layout>')
        w('  </defaults>')
    for cr in score.credits:
        w(f'  <credit page="{cr["page"]}">')
        w(f'    <credit-type>{escape(cr["type"])}</credit-type>')
        w(f'    <credit-words>{escape(cr["text"])}</credit-words>')
        w('  </credit>')
    w('  <part-list>')
    starts, stops = {}, {}
    for gi, g in enumerate(score.groups, 1):
        starts.setdefault(g['first'], []).append((gi, g))
        stops.setdefault(g['last'], []).append((gi, g))
    for p in score.parts:
        for gi, g in starts.get(p.id, []):
            w(f'    <part-group type="start" number="{gi}">')
            if g.get('name'):
                w(f'      <group-name>{escape(g["name"])}</group-name>')
            w(f'      <group-symbol>{g.get("symbol", "bracket")}</group-symbol>')
            w(f'      <group-barline>{"yes" if g.get("barline", True) else "no"}</group-barline>')
            w('    </part-group>')
        w(f'    <score-part id="{p.id}">')
        w(f'      <part-name>{escape(p.name)}</part-name>')
        if p.abbr:
            w(f'      <part-abbreviation>{escape(p.abbr)}</part-abbreviation>')
        w('    </score-part>')
        for gi, g in stops.get(p.id, []):
            w(f'    <part-group type="stop" number="{gi}"/>')
    w('  </part-list>')

    marks_pid = score.marks_part or score.parts[0].id
    offs = score.measure_offsets()
    for p in score.parts:
        w(f'  <part id="{p.id}">')
        volta_num = None
        for i, m in enumerate(p.measures):
            mi = score.measures[i]
            attrs = ' implicit="yes"' if mi.implicit else ''
            w(f'    <measure number="{mi.number}"{attrs}>')
            if mi.brk == 'page':
                w('      <print new-page="yes"/>')
            elif mi.brk == 'system':
                w('      <print new-system="yes"/>')
            a = []
            if i == 0:
                a.append(f'        <divisions>{div}</divisions>')
            if mi.key or i == 0:
                k = mi.key or score.current_key(i)
                canc = ''
                if i > 0 and i in key_cancel:
                    canc = f'<cancel>{score.current_key(i - 1)[0]}</cancel>'
                a.append(f'        <key>{canc}<fifths>{k[0]}</fifths><mode>{k[1]}</mode></key>')
            if mi.time or i == 0:
                (tn, td), sym = score.current_time(i)
                sa = f' symbol="{sym}"' if sym in ('common', 'cut') and (tn, td) in ((4, 4), (2, 2)) else ''
                a.append(f'        <time{sa}><beats>{tn}</beats><beat-type>{td}</beat-type></time>')
            if i == 0:
                if p.staves > 1:
                    a.append(f'        <staves>{p.staves}</staves>')
                for s in range(p.staves):
                    a.append(_clef_xml(p.clefs[s], s + 1 if p.staves > 1 else None, '        '))
            if a:
                w('      <attributes>')
                out.extend(a)
                w('      </attributes>')
            lb = []
            if mi.left_bar == 'repeat-start':
                lb.append('<bar-style>heavy-light</bar-style>')
            if mi.volta_start:
                volta_num = mi.volta_start
                lb.append(f'<ending number="{mi.volta_start}" type="start">{escape(mi.volta_start)}.</ending>')
            if mi.left_bar == 'repeat-start':
                lb.append('<repeat direction="forward"/>')
            if lb:
                w('      <barline location="left">' + ''.join(lb) + '</barline>')
            top_staff = 1 if p.staves > 1 else None
            if p.id == marks_pid:
                for mk in mi.marks:
                    w(mark_xml(mk, top_staff))
            roles = {}
            for s in range(1, p.staves + 1):
                vk = [(v.key, m.get(v.key, [])) for v in p.voices if v.staff == s]
                roles.update(staff_roles(vk))
            order = sorted(p.voices, key=lambda v: (v.staff, int(v.key) if v.key.isdigit() else 99))
            pos = F(0)
            first_voice = True
            for v in order:
                evs = list(m.get(v.key, []))
                filled = sum((e.dur for e in evs), F(0))
                if filled < mi.dur:
                    evs.append(Event('space', mi.dur - filled))
                if not first_voice and pos > 0:
                    w(f'      <backup><duration>{int(pos * div)}</duration></backup>')
                    pos = F(0)
                first_voice = False
                ott_size = 8
                for ev in evs:
                    st_num = (ev.staff or v.staff) if p.staves > 1 else None
                    st = f'<staff>{st_num}</staff>' if st_num else ''
                    vst = f'<voice>{v.key}</voice>{st}'
                    if ev.kind == 'clef':
                        w('      <attributes>')
                        w(_clef_xml(ev.clef, st_num, '        '))
                        w('      </attributes>')
                        continue
                    if ev.kind == 'ottava':
                        if ev.ottava:
                            typ, ott_size = OTTAVA[ev.ottava]
                            w(f'      <direction placement="{"above" if ev.ottava > 0 else "below"}"><direction-type>'
                              f'<octave-shift type="{typ}" size="{ott_size}"/></direction-type>{vst}</direction>')
                        else:
                            w(f'      <direction><direction-type><octave-shift type="stop" size="{ott_size}"/>'
                              f'</direction-type>{vst}</direction>')
                        continue
                    d = int(ev.dur * div)
                    if ev.kind == 'space':
                        w(f'      <forward><duration>{d}</duration>{vst}</forward>')
                        pos += ev.dur
                        continue
                    for kind in ev.pedal:
                        w(f'      <direction><direction-type><pedal type="{kind}" line="no" sign="yes"/>'
                          f'</direction-type>{vst}</direction>')
                    for wd in ev.wedge:
                        if wd == 'stop':
                            w(f'      <direction><direction-type><wedge type="stop"/></direction-type>{vst}</direction>')
                    for dyn in ev.dynamics:
                        w(f'      <direction><direction-type><dynamics><{dyn}/></dynamics></direction-type>'
                          f'{vst}</direction>')
                    for wd in ev.wedge:
                        if wd != 'stop':
                            w(f'      <direction><direction-type><wedge type="{wd}"/></direction-type>{vst}</direction>')
                    for text, place, style in ev.words:
                        w(f'      <direction placement="{place}"><direction-type>{_words_xml(text, style)}'
                          f'</direction-type>{vst}</direction>')
                    if ev.kind == 'rest':
                        _note(w, ev, None, 0, d, v.key, st_num, beams, tuplet_vis, offs[i])
                    else:
                        for k, pit in enumerate(ev.pitches):
                            _note(w, ev, pit, k, d, v.key, st_num, beams, tuplet_vis, offs[i])
                    pos += ev.dur
            if p.id == marks_pid:
                for mk in mi.end_marks:
                    w(mark_xml(mk, top_staff))
            rb = []
            if mi.right_bar in BAR_STYLE:
                rb.append(f'<bar-style>{BAR_STYLE[mi.right_bar]}</bar-style>')
            if mi.volta_end:
                rb.append(f'<ending number="{volta_num}" type="{mi.volta_end}"/>')
            if mi.right_bar == 'repeat-end':
                rb.append('<repeat direction="backward"/>')
            if rb:
                w('      <barline location="right">' + ''.join(rb) + '</barline>')
            w('    </measure>')
        w('  </part>')
    w('</score-partwise>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def _acc_xml(h, ev, pit):
    if not h or not h.get('acc'):
        return None
    a = h['acc']
    alter = GLYPH[a['glyph']]
    val = acc_value(alter, a['restore_first'])
    attrs = ''
    if a['paren']:
        attrs = ' cautionary="yes" parentheses="yes"'
    return f'<accidental{attrs}>{val}</accidental>'


def _note(w, ev, pit, k, d, voice, staff, beams, tuplet_vis, m_off):
    first = k == 0
    nid = ev.ids[k] if ev.ids else None
    h = ev.hv.get(nid) if (pit is not None and nid) else None
    w('      <note>')
    if ev.grace:
        w('        <grace slash="yes"/>' if ev.grace == 'slash' else '        <grace/>')
    if k > 0:
        w('        <chord/>')
    if ev.kind == 'rest':
        w('        <rest measure="yes"/>' if ev.measure_rest else '        <rest/>')
    else:
        step, alter, octv = pit
        al = f'<alter>{alter}</alter>' if alter else ''
        w(f'        <pitch><step>{step}</step>{al}<octave>{octv}</octave></pitch>')
    if not ev.grace:
        w(f'        <duration>{d}</duration>')
    tie_stop = pit is not None and pit in ev.tie_stop
    tie_start = pit is not None and pit in ev.tie_start
    if tie_stop:
        w('        <tie type="stop"/>')
    if tie_start:
        w('        <tie type="start"/>')
    w(f'        <voice>{voice}</voice>')
    if not ev.measure_rest and ev.dtype:
        w(f'        <type>{ev.dtype}</type>')
        for _ in range(ev.dots):
            w('        <dot/>')
    acc = _acc_xml(h, ev, pit) if pit is not None else None
    if acc:
        w(f'        {acc}')
    if ev.tuplet:
        w(f'        <time-modification><actual-notes>{ev.tuplet[0]}</actual-notes>'
          f'<normal-notes>{ev.tuplet[1]}</normal-notes></time-modification>')
    if h and h.get('stem') and h.get('stem_visible'):
        w(f'        <stem>{h["stem"]}</stem>')
    if staff:
        w(f'        <staff>{staff}</staff>')
    if first and nid in beams:
        for lv, val in beams[nid]:
            w(f'        <beam number="{lv}">{val}</beam>')
    nots = []
    if tie_stop:
        nots.append('<tied type="stop"/>')
    if tie_start:
        nots.append('<tied type="start"/>')
    if first:
        for _ in range(ev.slur_stop):
            nots.append('<slur type="stop" number="1"/>')
        for _ in range(ev.slur_start):
            nots.append('<slur type="start" number="1"/>')
        if ev.tuplet and ev.tuplet_start:
            vis = tuplet_vis.get(nid)
            br = '' if vis is None else f' bracket="{"yes" if vis else "no"}"'
            nots.append(f'<tuplet type="start"{br}/>')
        if ev.tuplet and ev.tuplet_stop:
            nots.append('<tuplet type="stop"/>')
        orn = []
        for o in ev.orn:
            orn.append({'trill': '<trill-mark/>', 'mordent': '<mordent/>', 'turn': '<turn/>'}[o])
        if ev.trem:
            orn.append(f'<tremolo type="single">{ev.trem}</tremolo>')
        if orn:
            nots.append('<ornaments>' + ''.join(orn) + '</ornaments>')
        arts = []
        for a_ in ev.artic:
            arts.append('<strong-accent type="up"/>' if a_ == 'strong-accent' else f'<{a_}/>')
        if ev.breath:
            arts.append('<breath-mark/>')
        if arts:
            nots.append('<articulations>' + ''.join(arts) + '</articulations>')
        if ev.fermata:
            nots.append('<fermata type="upright"/>')
    if pit is not None and pit in ev.fing:
        nots.append(f'<technical><fingering>{ev.fing[pit]}</fingering></technical>')
    if ev.arpeggio and pit is not None:
        nots.append('<arpeggiate/>')
    if nots:
        w('        <notations>' + ''.join(nots) + '</notations>')
    if first and ev.kind == 'note':
        for num in sorted(ev.lyrics):
            ly = ev.lyrics[num]
            ext = '<extend/>' if ly.extend else ''
            w(f'        <lyric number="{num}"><syllabic>{ly.syllabic}</syllabic>'
              f'<text>{escape(ly.text)}</text>{ext}</lyric>')
    w('      </note>')
