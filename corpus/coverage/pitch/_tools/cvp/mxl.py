"""Internal model -> MusicXML 4.0 partwise (ground truth)."""
from __future__ import annotations

import math
from fractions import Fraction as F
from xml.sax.saxutils import escape

from .acc import acc_value, key_cancel_steps, part_staves, simulate
from .model import STEPS, Score, display_ql, staff_roles

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
        for s in reversed(SHARP_ORDER):
            pass
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


def write_musicxml(score: Score, path: str, software='coverage corpus builder (pitch family)', date='2026-11-08'):
    div = divisions_for(score)
    acc_dec, _tls = simulate(score, part_staves(score))
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
    # part list
    w('  <part-list>')
    starts = {}
    stops = {}
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

    for p in score.parts:
        w(f'  <part id="{p.id}">')
        vnum = {}
        for v in p.voices:
            vnum[v.key] = v.key
        clefs_now = list(p.clefs)
        ott_size = {}
        for i, m in enumerate(p.measures):
            mi = score.measures[i]
            attrs = f' implicit="yes"' if mi.implicit else ''
            w(f'    <measure number="{mi.number}"{attrs}>')
            if i > 0 and mi.brk == 'page':
                w('      <print new-page="yes"/>')
            elif i > 0 and mi.brk == 'line':
                w('      <print new-system="yes"/>')
            fifths, mode = score.current_key(i)
            # attributes
            a = []
            if i == 0:
                a.append(f'        <divisions>{div}</divisions>')
            if mi.key or i == 0:
                k = mi.key or (fifths, mode)
                canc = ''
                if i > 0:
                    oldf = score.current_key(i - 1)[0]
                    if key_cancel_steps(oldf, k[0]):
                        canc = f'<cancel>{oldf}</cancel>'
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
            if mi.left_bar == 'repeat-start':
                w('      <barline location="left"><bar-style>heavy-light</bar-style>'
                  '<repeat direction="forward"/></barline>')
            # accidental state per staff
            kalt = key_alters(fifths)
            acc_state = {s: {} for s in range(1, p.staves + 1)}
            # voice roles per staff
            roles = {}
            for s in range(1, p.staves + 1):
                vk = [(v.key, m.get(v.key, [])) for v in p.voices if v.staff == s]
                roles.update(staff_roles(vk))
            # order voices: by staff then key
            order = sorted(p.voices, key=lambda v: (v.staff, int(v.key) if v.key.isdigit() else 99))
            pos = F(0)
            first_voice = True
            for v in order:
                evs = list(m.get(v.key, []))
                filled = sum((e.dur for e in evs), F(0))
                if filled < mi.dur:
                    from .model import Event as _Ev
                    evs.append(_Ev('space', mi.dur - filled))
                if not first_voice and pos > 0:
                    w(f'      <backup><duration>{int(pos * div)}</duration></backup>')
                    pos = F(0)
                first_voice = False
                staff_attr = v.staff if p.staves > 1 else None
                role = roles.get(v.key, 0)
                for ev in evs:
                    if ev.kind == 'clef':
                        w('      <attributes>')
                        w(_clef_xml(ev.clef, staff_attr, '        '))
                        w('      </attributes>')
                        continue
                    if ev.kind == 'ottava':
                        st = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                        if ev.ottava == 0:
                            size = ott_size.pop(v.key, 8)
                            w(f'      <direction><direction-type><octave-shift type="stop" size="{size}" number="{staff_attr or 1}"/>'
                              f'</direction-type><voice>{vnum[v.key]}</voice>{st}</direction>')
                        else:
                            size = 15 if abs(ev.ottava) == 2 else 8
                            typ = 'down' if ev.ottava > 0 else 'up'
                            pl = 'above' if ev.ottava > 0 else 'below'
                            ott_size[v.key] = size
                            w(f'      <direction placement="{pl}"><direction-type><octave-shift type="{typ}" '
                              f'size="{size}" number="{staff_attr or 1}"/></direction-type><voice>{vnum[v.key]}</voice>{st}</direction>')
                        continue
                    d = int(ev.dur * div)
                    if ev.kind == 'space':
                        st = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                        w(f'      <forward><duration>{d}</duration><voice>{vnum[v.key]}</voice>{st}</forward>')
                        pos += ev.dur
                        continue
                    for dyn in ev.dynamics:
                        st = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                        w(f'      <direction placement="below"><direction-type><dynamics><{dyn}/></dynamics>'
                          f'</direction-type><voice>{vnum[v.key]}</voice>{st}</direction>')
                    if ev.kind == 'rest':
                        _note(w, ev, None, False, d, vnum[v.key], staff_attr, role, None, True)
                    else:
                        for k, pit in enumerate(ev.pitches):
                            acc = acc_dec.get((id(ev), pit))
                            _note(w, ev, pit, k > 0, d, vnum[v.key], staff_attr, role, acc, k == 0)
                    pos += ev.dur
            if mi.right_bar in BAR_STYLE:
                rep = '<repeat direction="backward"/>' if mi.right_bar == 'repeat-end' else ''
                w(f'      <barline location="right"><bar-style>{BAR_STYLE[mi.right_bar]}</bar-style>{rep}</barline>')
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


def _note(w, ev, pit, chord, d, voice, staff, role, acc, first):
    w('      <note>')
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
    if tie_stop:
        w('        <tie type="stop"/>')
    if tie_start:
        w('        <tie type="start"/>')
    w(f'        <voice>{voice}</voice>')
    if not ev.measure_rest and ev.dtype:
        w(f'        <type>{ev.dtype}</type>')
        for _ in range(ev.dots):
            w('        <dot/>')
    if acc:
        at = ''
        if acc['paren']:
            at = ' cautionary="yes" parentheses="yes"'
        elif acc['forced'] and not acc['required']:
            at = ' cautionary="yes"'
        w(f'        <accidental{at}>{acc_value(acc)}</accidental>')
    if ev.tuplet:
        w(f'        <time-modification><actual-notes>{ev.tuplet[0]}</actual-notes>'
          f'<normal-notes>{ev.tuplet[1]}</normal-notes></time-modification>')
    if ev.kind == 'note' and ev.stem:
        w(f'        <stem>{ev.stem}</stem>')
    elif ev.kind == 'note' and role in (1, 3):
        w('        <stem>up</stem>')
    elif ev.kind == 'note' and role in (2, 4):
        w('        <stem>down</stem>')
    if staff:
        w(f'        <staff>{staff}</staff>')
    if first and ev.kind == 'note':
        for lvl in sorted(ev.beams):
            w(f'        <beam number="{lvl}">{ev.beams[lvl]}</beam>')
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
            nots.append('<tuplet type="start" bracket="yes"/>')
        if ev.tuplet and ev.tuplet_stop:
            nots.append('<tuplet type="stop"/>')
        if ev.fermata:
            nots.append('<fermata type="upright"/>')
        if ev.artic:
            nots.append('<articulations>' + ''.join(f'<{a}/>' for a in ev.artic) + '</articulations>')
    if nots:
        w('        <notations>' + ''.join(nots) + '</notations>')
    if first and ev.kind == 'note':
        for num in sorted(ev.lyrics):
            ly = ev.lyrics[num]
            ext = '<extend/>' if ly.extend else ''
            w(f'        <lyric number="{num}"><syllabic>{ly.syllabic}</syllabic>'
              f'<text>{escape(ly.text)}</text>{ext}</lyric>')
    w('      </note>')
