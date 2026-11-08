"""Internal model -> MusicXML 4.0 partwise (ground truth), layout-challenge edition.

Adds to the synthetic-corpus writer: credits (title/composer/page headers and
numbers), part-group symbols (brace/bracket), part-symbol (organ: brace on
manual staves only), staff-size changes (<staff-details>), system/page breaks
(<print>), volta endings, segno/coda/D.S./D.C./Fine with <sound> playback
attributes, tempo (words + metronome), words directions, hairpins, pedal marks,
cue notes (<cue/> + type size="cue"), cross-staff notes (<staff> differs from the
voice's home staff) and invisible rests of staves hidden in a system
(print-object="no").
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from xml.sax.saxutils import escape, quoteattr

from .model import STEPS, Event, Score, display_ql, staff_roles

CLEF_XML = {
    'treble': ('G', 2, 0), 'treble_8': ('G', 2, -1), 'treble^8': ('G', 2, 1),
    'bass': ('F', 4, 0), 'bass_8': ('F', 4, -1), 'varbaritone': ('F', 3, 0),
    'alto': ('C', 3, 0), 'tenor': ('C', 4, 0), 'soprano': ('C', 1, 0),
    'mezzosoprano': ('C', 2, 0), 'baritone': ('C', 5, 0), 'percussion': ('percussion', None, 0),
}
SHARP_ORDER = 'FCGDAEB'
ACC_NAME = {-2: 'flat-flat', -1: 'flat', 0: 'natural', 1: 'sharp', 2: 'double-sharp'}
BAR_STYLE = {'final': 'light-heavy', 'double': 'light-light', 'repeat-end': 'light-heavy',
             'dashed': 'dashed'}


def key_alters(fifths):
    alt = {s: 0 for s in STEPS}
    if fifths > 0:
        for s in SHARP_ORDER[:fifths]:
            alt[s] = 1
    elif fifths < 0:
        for s in SHARP_ORDER[::-1][:-fifths]:
            alt[s] = -1
    return alt


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
    elif style == 'bold-italic':
        a['font-style'] = 'italic'
        a['font-weight'] = 'bold'
    return f'<words{_attr(a)}>{escape(text)}</words>'


def mark_xml(mk, staff):
    """measure-level mark dict -> <direction> string"""
    st = f'<staff>{staff}</staff>' if staff else ''
    kind = mk['kind']
    place = mk.get('placement', 'above')
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
    elif kind == 'segno':
        dts.append('<segno/>')
        sound = f'<sound segno="{mk.get("id", "segno")}"/>'
    elif kind == 'coda':
        dts.append('<coda/>')
        sound = f'<sound coda="{mk.get("id", "coda")}"/>'
    elif kind == 'rehearsal':
        dts.append(f'<rehearsal>{escape(mk["text"])}</rehearsal>')
    elif kind == 'words':
        dts.append(_words_xml(mk['text'], mk.get('style', 'italic')))
        if mk.get('coda_sign'):
            dts.append('<coda/>')
        snd = mk.get('sound')
        if snd:
            sound = '<sound' + ''.join(f' {k}="{v}"' for k, v in snd.items()) + '/>'
    else:
        raise ValueError(kind)
    body = ''.join(f'<direction-type>{d}</direction-type>' for d in dts)
    return f'      <direction placement="{place}">{body}{st}{sound or ""}</direction>'


def write_musicxml(score: Score, path: str, software='layout-challenge corpus builder', date='2026-11-08'):
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
    if score.composer:
        w(f'    <creator type="composer">{escape(score.composer)}</creator>')
    if score.lyricist:
        w(f'    <creator type="lyricist">{escape(score.lyricist)}</creator>')
    if score.arranger:
        w(f'    <creator type="arranger">{escape(score.arranger)}</creator>')
    if score.rights:
        w(f'    <rights>{escape(score.rights)}</rights>')
    w('    <encoding>')
    w(f'      <software>{escape(software)}</software>')
    w(f'      <encoding-date>{date}</encoding-date>')
    w('    </encoding>')
    if score.source:
        w(f'    <source>{escape(score.source)}</source>')
    w('  </identification>')
    for cr in getattr(score, 'credits', []) or []:
        w(f'  <credit page="{cr["page"]}">')
        w(f'    <credit-type>{escape(cr["type"])}</credit-type>')
        w(f'    <credit-words>{escape(cr["text"])}</credit-words>')
        w('  </credit>')
    # part list
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

    marks_pid = getattr(score, 'marks_part', None) or score.parts[0].id
    for p in score.parts:
        w(f'  <part id="{p.id}">')
        volta_num = None
        for i, m in enumerate(p.measures):
            mi = score.measures[i]
            attrs = ' implicit="yes"' if mi.implicit else ''
            num = mi.label if mi.label else mi.number
            w(f'    <measure number="{num}"{attrs}>')
            if mi.brk == 'page':
                w('      <print new-page="yes"/>')
            elif mi.brk == 'system':
                w('      <print new-system="yes"/>')
            fifths, mode = score.current_key(i)
            a = []
            if i == 0:
                a.append(f'        <divisions>{div}</divisions>')
            if mi.key or i == 0:
                k = mi.key or (fifths, mode)
                a.append(f'        <key><fifths>{k[0]}</fifths><mode>{k[1]}</mode></key>')
            if mi.time or i == 0:
                (tn, td), sym = score.current_time(i)
                sa = f' symbol="{sym}"' if sym in ('common', 'cut') and (tn, td) in ((4, 4), (2, 2)) else ''
                a.append(f'        <time{sa}><beats>{tn}</beats><beat-type>{td}</beat-type></time>')
            if i == 0:
                if p.staves > 1:
                    a.append(f'        <staves>{p.staves}</staves>')
                ps = getattr(p, 'part_symbol', None)
                if ps:
                    a.append(f'        <part-symbol top-staff="{ps[1]}" bottom-staff="{ps[2]}">{ps[0]}</part-symbol>')
                for s in range(p.staves):
                    a.append(_clef_xml(p.clefs[s], s + 1 if p.staves > 1 else None, '        '))
            size = None
            if i == 0 and getattr(p, 'staff_size', None):
                size = p.staff_size
            if mi.staff_size and p.id in mi.staff_size:
                size = mi.staff_size[p.id]
            if size:
                for s in range(p.staves):
                    na = f' number="{s + 1}"' if p.staves > 1 else ''
                    a.append(f'        <staff-details{na}><staff-size>{size}</staff-size></staff-details>')
            if a:
                w('      <attributes>')
                out.extend(a)
                w('      </attributes>')
            # left barline: repeat start and/or volta start
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
                    w(mark_xml(mk, mk.get('staff', top_staff)))
            kalt = key_alters(fifths)
            acc_state = {s: {} for s in range(1, p.staves + 1)}
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
                role = roles.get(v.key, 0)
                hq = []
                if p.id == marks_pid and v is order[0]:
                    hq = sorted((F(o), sym) for (hi, o, sym) in score.harmonies if hi == i)
                for ev in evs:
                    while hq and hq[0][0] <= pos and ev.kind != 'clef':
                        if hq[0][0] != pos:
                            raise ValueError(f'harmony at {hq[0][0]} not on an event onset in measure {i + 1}')
                        w(harmony_xml(hq.pop(0)[1], f'<staff>{1}</staff>' if p.staves > 1 else ''))
                    st_num = (ev.staff or v.staff) if p.staves > 1 else None
                    if ev.kind == 'clef':
                        w('      <attributes>')
                        w(_clef_xml(ev.clef, st_num, '        '))
                        w('      </attributes>')
                        continue
                    d = int(ev.dur * div)
                    st = f'<staff>{st_num}</staff>' if st_num else ''
                    if ev.kind == 'space':
                        w(f'      <forward><duration>{d}</duration><voice>{v.key}</voice>{st}</forward>')
                        pos += ev.dur
                        continue
                    for kind in ev.pedal:
                        w(f'      <direction placement="below"><direction-type><pedal type="{kind}" line="no" '
                          f'sign="yes"/></direction-type><voice>{v.key}</voice>{st}</direction>')
                    for wd in ev.wedge:
                        w(f'      <direction placement="below"><direction-type><wedge type="{wd}"/></direction-type>'
                          f'<voice>{v.key}</voice>{st}</direction>')
                    for dyn in ev.dynamics:
                        w(f'      <direction placement="below"><direction-type><dynamics><{dyn}/></dynamics>'
                          f'</direction-type><voice>{v.key}</voice>{st}</direction>')
                    for text, place, style in ev.words:
                        w(f'      <direction placement="{place}"><direction-type>{_words_xml(text, style)}'
                          f'</direction-type><voice>{v.key}</voice>{st}</direction>')
                    if ev.kind == 'rest':
                        _note(w, ev, None, False, d, v.key, st_num, role, None, True)
                    else:
                        for k, pit in enumerate(ev.pitches):
                            acc = ev.acc.get(pit)
                            _note(w, ev, pit, k > 0, d, v.key, st_num, role, acc, k == 0, k)
                    pos += ev.dur
                if hq:
                    raise ValueError(f'unplaced harmonies in measure {i + 1}: {hq}')
            if p.id == marks_pid:
                for mk in mi.end_marks:
                    w(mark_xml(mk, mk.get('staff', top_staff)))
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


def _clef_xml(name, number, ind):
    sign, line, oc = CLEF_XML.get(name, ('G', 2, 0))
    na = f' number="{number}"' if number else ''
    s = f'{ind}<clef{na}><sign>{sign}</sign>'
    if line is not None:
        s += f'<line>{line}</line>'
    if oc:
        s += f'<clef-octave-change>{oc}</clef-octave-change>'
    return s + '</clef>'


def _accidental(pit, ev, state, kalt):
    step, alter, octv = pit
    keyp = (step, octv)
    cur = state.get(keyp, kalt[step])
    if pit in ev.tie_stop:
        state[keyp] = alter
        return None
    state[keyp] = alter
    if alter != cur:
        return ACC_NAME.get(alter)
    return None


def _note(w, ev, pit, chord, d, voice, staff, role, acc, first, k=0):
    po = ' print-object="no"' if ev.hidden else ''
    w(f'      <note{po}>')
    if ev.cue:
        w('        <cue/>')
    if chord:
        w('        <chord/>')
    if ev.kind == 'rest':
        w('        <rest measure="yes"/>' if ev.measure_rest else '        <rest/>')
    else:
        step, alter, octv = pit
        al = f'<alter>{alter}</alter>' if alter else ''
        w(f'        <pitch><step>{step}</step>{al}<octave>{octv}</octave></pitch>')
    w(f'        <duration>{d}</duration>')
    tie_stop = pit is not None and pit in ev.tie_stop
    tie_start = pit is not None and pit in ev.tie_start
    if not ev.cue:
        if tie_stop:
            w('        <tie type="stop"/>')
        if tie_start:
            w('        <tie type="start"/>')
    w(f'        <voice>{voice}</voice>')
    if not ev.measure_rest and ev.dtype:
        sz = ' size="cue"' if ev.cue else ''
        w(f'        <type{sz}>{ev.dtype}</type>')
        for _ in range(ev.dots):
            w('        <dot/>')
    if acc:
        w(f'        <accidental>{acc}</accidental>')
    if ev.tuplet:
        w(f'        <time-modification><actual-notes>{ev.tuplet[0]}</actual-notes>'
          f'<normal-notes>{ev.tuplet[1]}</normal-notes></time-modification>')
    if ev.kind == 'note' and ev.stem_dir:
        w(f'        <stem>{ev.stem_dir}</stem>')
    if staff:
        w(f'        <staff>{staff}</staff>')
    if ev.kind == 'note':
        for lev in sorted(ev.beams):
            w(f'        <beam number="{lev}">{ev.beams[lev]}</beam>')
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
            nots.append('<tuplet type="start"/>')
        if ev.tuplet and ev.tuplet_stop:
            nots.append('<tuplet type="stop"/>')
        if ev.fermata:
            nots.append('<fermata type="upright"/>')
        if ev.ornaments:
            nots.append('<ornaments>' + ''.join(f'<{o}/>' for o in ev.ornaments) + '</ornaments>')
        arts = [('<strong-accent type="up"/>' if a == 'strong-accent' else f'<{a}/>') for a in ev.artic]
        if ev.breath:
            arts.append('<breath-mark/>')
        if arts:
            nots.append('<articulations>' + ''.join(arts) + '</articulations>')
    if ev.kind == 'note' and k < len(ev.fingering) and ev.fingering[k]:
        nots.append(f'<technical><fingering>{ev.fingering[k]}</fingering></technical>')
    if ev.kind == 'note' and ev.arpeggio and len(ev.pitches) > 1:
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


HKIND = {'': ('major', ''), 'm': ('minor', 'm'), '7': ('dominant', '7'), 'm7': ('minor-seventh', 'm7'),
         'maj7': ('major-seventh', 'maj7'), 'sus4': ('suspended-fourth', 'sus4'), 'dim': ('diminished', 'dim'),
         '6': ('major-sixth', '6'), 'm6': ('minor-sixth', 'm6'), '9': ('dominant-ninth', '9')}


def harmony_xml(sym, staff=''):
    import re as _re
    m = _re.match(r'^(?P<r>[A-G])(?P<ra>#|b)?(?P<q>maj7|m7|m6|m|dim|sus4|7|6|9)?(?:/(?P<b>[A-G])(?P<ba>#|b)?)?$', sym)
    if not m:
        raise ValueError(sym)
    al = {'#': 1, 'b': -1, None: 0}
    r = f'<root><root-step>{m.group("r")}</root-step>'
    if al[m.group('ra')]:
        r += f'<root-alter>{al[m.group("ra")]}</root-alter>'
    r += '</root>'
    kind, text = HKIND[m.group('q') or '']
    r += f'<kind text="{text}">{kind}</kind>'
    if m.group('b'):
        r += f'<bass><bass-step>{m.group("b")}</bass-step>'
        if al[m.group('ba')]:
            r += f'<bass-alter>{al[m.group("ba")]}</bass-alter>'
        r += '</bass>'
    return f'      <harmony print-frame="no">{r}{staff}</harmony>'
