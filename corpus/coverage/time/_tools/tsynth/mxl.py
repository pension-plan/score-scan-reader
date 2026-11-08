"""Internal model -> MusicXML 4.0 partwise (ground truth).

coverage/time copy of corpus/challenge/rhythm/_tools/rsynth/mxl.py (nested tuplets: time-modification =
product of all levels, one numbered <tuplet> per level with tuplet-actual/tuplet-normal for nested groups,
bracket per level by LilyPond's rule).  The rhythm copy extended corpus/synthetic/_tools/synth/mxl.py with:
  * explicit <beam> elements (levels 1..n, begin/continue/end/forward hook/backward hook)
    computed from the model's beam groups (the engraving uses exactly these groups:
    \\autoBeamOff + manual [ ]); beams are written on notes only, a rest inside a beam
    group carries no <beam> element
  * grace notes (<grace/> / <grace slash="yes"/>, no <duration>) and the slur that
    \\acciaccatura / \\appoggiatura engrave (slur number 2)
  * multi-measure rests (<measure-style><multiple-rest>) + one measure rest per bar
  * <print new-system/new-page> for the forced line/page breaks of the engraving
  * rehearsal marks and words directions
  * tuplet display (bracket yes/no as engraved, show-number none for implied tuplets)
  * accidentals computed per staff in time order (LilyPond 'default' accidental style)
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from xml.sax.saxutils import escape

from .model import STEPS, Event, Score, staff_roles

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
NBEAMS = {'eighth': 1, '16th': 2, '32nd': 3, '64th': 4, '128th': 5}


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


# ---------------------------------------------------------------- beams

def beam_groups(evs):
    """list of lists of event indices (notes and rests) forming one beam each.
    Grace notes form their own groups (they are beamed inside \\grace { })."""
    groups = []
    cur = None
    for k, ev in enumerate(evs):
        if ev.kind not in ('note', 'rest'):
            continue
        if ev.beam_start and cur is None:
            cur = [k]
            if ev.beam_stop:
                groups.append(cur)
                cur = None
            continue
        if cur is not None:
            # graces and main notes never share a beam
            if bool(ev.grace) != bool(evs[cur[0]].grace):
                continue
            cur.append(k)
            if ev.beam_stop:
                groups.append(cur)
                cur = None
    if cur is not None:
        raise ValueError('unterminated beam')
    return groups


def beam_elements(evs):
    """dict event-index -> list of (level, status) for notes in beam groups."""
    out = {}
    for g in beam_groups(evs):
        notes = [k for k in g if evs[k].kind == 'note']
        nb = {k: NBEAMS.get(evs[k].dtype, 0) for k in notes}
        for pos, k in enumerate(notes):
            els = []
            for lvl in range(1, nb[k] + 1):
                if lvl == 1:
                    if pos == 0:
                        st = 'begin'
                    elif pos == len(notes) - 1:
                        st = 'end'
                    else:
                        st = 'continue'
                    els.append((1, st))
                    continue
                left = pos > 0 and nb[notes[pos - 1]] >= lvl and not _rest_between(evs, notes[pos - 1], k)
                right = pos < len(notes) - 1 and nb[notes[pos + 1]] >= lvl and not _rest_between(evs, k, notes[pos + 1])
                if left and right:
                    st = 'continue'
                elif right:
                    st = 'begin'
                elif left:
                    st = 'end'
                else:
                    st = 'forward hook' if pos == 0 else 'backward hook'
                els.append((lvl, st))
            out[k] = els
    return out


def _rest_between(evs, a, b):
    return any(evs[j].kind == 'rest' for j in range(a + 1, b))


def tuplet_groups(evs):
    """coverage/time: every tuplet group of a voice-measure (all nesting levels).
    -> list of dict(level, ratio, start, stop, members, nested, unit=(type, dots), bracket)."""
    from .model import display_ql, ql_to_type
    groups, open_ = [], {}
    for k, ev in enumerate(evs):
        if ev.kind not in ('note', 'rest') or not ev.tup_levels:
            continue
        for L in sorted(ev.tup_starts):
            open_[L] = {'level': L, 'ratio': ev.tup_levels[L], 'start': k, 'members': []}
        for L, g in open_.items():
            g['members'].append(k)
        for L in sorted(ev.tup_stops, reverse=True):
            g = open_.pop(L)
            g['stop'] = k
            groups.append(g)
    if open_:
        raise ValueError(f'unterminated tuplet group {open_}')
    bgroups = beam_groups(evs)
    for g in groups:
        L = g['level']
        a, n = g['ratio']
        tot = F(0)
        for k in g['members']:
            ev = evs[k]
            d = display_ql(ev.dtype, ev.dots)
            for a2, n2 in ev.tup_levels[L + 1:]:
                d = d * n2 / a2
            tot += d
        unit = ql_to_type(tot / a)
        if unit is None:
            raise ValueError(f'tuplet unit not expressible: {tot}/{a}')
        g['unit'] = unit
        g['nested'] = L > 0 or any(len(evs[k].tup_levels) > L + 1 for k in g['members'])
        # LilyPond 2.24 Tuplet_bracket::print: bracket omitted when the first and last note
        # columns of the tuplet have stems on one beam whose first/last stems are exactly
        # those notes (equally long); rests have no stem -> bracket printed.
        first, last = evs[g['start']], evs[g['stop']]
        hidden = False
        if first.kind == 'note' and last.kind == 'note':
            for bg in bgroups:
                notes = [k for k in bg if evs[k].kind == 'note']
                if notes and notes[0] == g['start'] and notes[-1] == g['stop']:
                    hidden = True
        g['bracket'] = 'no' if hidden else 'yes'
    return groups


def tuplet_brackets(evs):
    """dict index-of-tuplet-start -> 'yes'/'no' (LilyPond default tupletBracketVisibility
    'if-no-beam: the bracket is omitted only when one beam starts on the tuplet's first
    note and ends on its last note)."""
    out = {}
    spans = {(g[0], g[-1]) for g in beam_groups(evs)}
    k = 0
    while k < len(evs):
        ev = evs[k]
        if ev.tuplet and ev.tuplet_start:
            j = k
            while not evs[j].tuplet_stop:
                j += 1
            members = [i for i in range(k, j + 1) if evs[i].kind in ('note', 'rest')]
            covered = (members[0], members[-1]) in spans
            out[k] = 'no' if covered else 'yes'
            k = j + 1
            continue
        k += 1
    return out


# ---------------------------------------------------------------- accidentals

def staff_accidentals(score, p, m, mi_index, kalt):
    """LilyPond default accidental style: per staff, same octave, until end of
    measure; all notes sounding at one moment are judged against the state
    before that moment.  Returns dict (id(ev), pitch) -> accidental name."""
    res = {}
    for s in range(1, p.staves + 1):
        items = []
        for vo, v in enumerate(p.voices):
            if v.staff != s:
                continue
            t = F(0)
            for k, ev in enumerate(m.get(v.key, [])):
                if ev.kind == 'note':
                    gk = 0 if ev.grace else 1
                    items.append((t, gk, k, vo, ev))
                t += ev.dur
        # group by (onset, grace-ness, position among graces)
        items.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
        state = {}
        i = 0
        while i < len(items):
            j = i
            key_ = items[i][:3] if items[i][1] == 0 else items[i][:2]
            while j < len(items) and (items[j][:3] if items[j][1] == 0 else items[j][:2]) == key_:
                j += 1
            new_state = {}
            for _, _, _, _, ev in items[i:j]:
                for pit in ev.pitches:
                    step, alter, octv = pit
                    kp = (step, octv)
                    cur = state.get(kp, kalt[step])
                    if pit in ev.tie_stop:
                        new_state[kp] = alter
                        continue
                    if alter != cur:
                        res[(id(ev), pit)] = ACC_NAME.get(alter)
                    new_state[kp] = alter
            state.update(new_state)
            i = j
    return res


# ---------------------------------------------------------------- writer

def write_musicxml(score: Score, path: str, software='rhythm challenge corpus builder', date='2026-11-08'):
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

    for pi, p in enumerate(score.parts):
        w(f'  <part id="{p.id}">')
        for i, m in enumerate(p.measures):
            mi = score.measures[i]
            attrs = ' implicit="yes"' if mi.implicit else ''
            w(f'    <measure number="{mi.number}"{attrs}>')
            if mi.new_page:
                w('      <print new-page="yes"/>')
            elif mi.new_system:
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
                for s in range(p.staves):
                    a.append(_clef_xml(p.clefs[s], s + 1 if p.staves > 1 else None, '        '))
            # multi-measure rest block (all voices of the part rest)
            mr, hbar = 0, False
            for v in p.voices:
                for ev in m.get(v.key, []):
                    if ev.multirest:
                        mr = max(mr, ev.multirest)
                        hbar = hbar or ev.multirest_hbar
            if mr > 1:
                # LilyPond engraves blocks of up to 10 bars with church-rest symbols unless forced to an H-bar
                sym = 'no' if (hbar or mr > 10) else 'yes'
                a.append(f'        <measure-style><multiple-rest use-symbols="{sym}">{mr}</multiple-rest>'
                         '</measure-style>')
            if a:
                w('      <attributes>')
                out.extend(a)
                w('      </attributes>')
            if mi.left_bar == 'repeat-start':
                w('      <barline location="left"><bar-style>heavy-light</bar-style>'
                  '<repeat direction="forward"/></barline>')
            if pi == 0 and mi.rehearsal:
                w('      <direction placement="above"><direction-type>'
                  f'<rehearsal>{escape(mi.rehearsal)}</rehearsal></direction-type></direction>')
            if pi == 0 and mi.words:
                w('      <direction placement="above"><direction-type>'
                  f'<words font-weight="bold">{escape(mi.words)}</words></direction-type></direction>')
            kalt = key_alters(fifths)
            accs = staff_accidentals(score, p, m, i, kalt)
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
                staff_attr = v.staff if p.staves > 1 else None
                role = roles.get(v.key, 0)
                beams = beam_elements(evs)
                brackets = {}
                for g in tuplet_groups(evs):
                    brackets.setdefault(g['start'], {'starts': [], 'stops': []})['starts'].append(g)
                    brackets.setdefault(g['stop'], {'starts': [], 'stops': []})['stops'].append(g)
                for k, ev in enumerate(evs):
                    if ev.kind == 'clef':
                        w('      <attributes>')
                        w(_clef_xml(ev.clef, staff_attr, '        '))
                        w('      </attributes>')
                        continue
                    d = int(ev.dur * div)
                    if ev.kind == 'space':
                        st = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                        w(f'      <forward><duration>{d}</duration><voice>{v.key}</voice>{st}</forward>')
                        pos += ev.dur
                        continue
                    for dyn in ev.dynamics:
                        st = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                        w(f'      <direction placement="below"><direction-type><dynamics><{dyn}/></dynamics>'
                          f'</direction-type><voice>{v.key}</voice>{st}</direction>')
                    bm = beams.get(k, [])
                    br = brackets.get(k)
                    if ev.kind == 'rest':
                        _note(w, ev, None, False, d, v.key, staff_attr, role, None, True, bm, br)
                    else:
                        for c, pit in enumerate(ev.pitches):
                            _note(w, ev, pit, c > 0, d, v.key, staff_attr, role, accs.get((id(ev), pit)),
                                  c == 0, bm, br)
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


def _note(w, ev, pit, chord, d, voice, staff, role, acc, first, beams, bracket):
    w('      <note>')
    if ev.grace:
        w('        <grace slash="yes"/>' if ev.grace in ('acciaccatura', 'slashed') else '        <grace/>')
    if chord:
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
    if acc:
        w(f'        <accidental>{acc}</accidental>')
    if ev.tuplet:
        w(f'        <time-modification><actual-notes>{ev.tuplet[0]}</actual-notes>'
          f'<normal-notes>{ev.tuplet[1]}</normal-notes></time-modification>')
    if ev.kind == 'note' and role in (1, 3):
        w('        <stem>up</stem>')
    elif ev.kind == 'note' and role in (2, 4):
        w('        <stem>down</stem>')
    if staff:
        w(f'        <staff>{staff}</staff>')
    if ev.kind == 'note':
        for lvl, st in beams:
            w(f'        <beam number="{lvl}">{st}</beam>')
    nots = []
    if tie_stop:
        nots.append('<tied type="stop"/>')
    if tie_start:
        nots.append('<tied type="start"/>')
    if first:
        for _ in range(ev.slur_stop):
            nots.append('<slur type="stop" number="1"/>')
        if ev.grace_slur_stop:
            nots.append('<slur type="stop" number="2"/>')
        for _ in range(ev.slur_start):
            nots.append('<slur type="start" number="1"/>')
        if ev.grace_slur_start:
            nots.append('<slur type="start" number="2"/>')
        tinfo = bracket or {'starts': [], 'stops': []}
        for g in sorted(tinfo['stops'], key=lambda g: -g['level']):
            nots.append(f'<tuplet type="stop" number="{g["level"] + 1}"/>')
        for g in sorted(tinfo['starts'], key=lambda g: g['level']):
            num = g['level'] + 1
            if ev.tuplet_hidden:
                nots.append(f'<tuplet type="start" number="{num}" bracket="no" show-number="none"/>')
            elif g['nested']:
                ut, ud = g['unit']
                dots = '<tuplet-dot/>' * ud
                a, n = g['ratio']
                nots.append(f'<tuplet type="start" number="{num}" bracket="{g["bracket"]}">'
                            f'<tuplet-actual><tuplet-number>{a}</tuplet-number><tuplet-type>{ut}</tuplet-type>{dots}'
                            f'</tuplet-actual><tuplet-normal><tuplet-number>{n}</tuplet-number>'
                            f'<tuplet-type>{ut}</tuplet-type>{dots}</tuplet-normal></tuplet>')
            else:
                nots.append(f'<tuplet type="start" number="{num}" bracket="{g["bracket"]}"/>')
        if ev.fermata:
            nots.append('<fermata type="upright"/>')
        if ev.artic:
            nots.append('<articulations>' + ''.join(f'<{a}/>' for a in ev.artic) + '</articulations>')
    if nots:
        w('        <notations>' + ''.join(nots) + '</notations>')
    if first and ev.kind == 'note' and not ev.grace:
        for num in sorted(ev.lyrics):
            ly = ev.lyrics[num]
            ext = '<extend/>' if ly.extend else ''
            w(f'        <lyric number="{num}"><syllabic>{ly.syllabic}</syllabic>'
              f'<text>{escape(ly.text)}</text>{ext}</lyric>')
    w('      </note>')
