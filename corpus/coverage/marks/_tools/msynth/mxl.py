"""Score model -> MusicXML 4.0 partwise truth.

Encoding conventions (also listed in every meta.json 'notes'):
  * articulations: staccato, staccatissimo, accent, tenuto, strong-accent (marcato; type="up" = ^ above,
    "down" = v below),
    detached-legato (portato), breath-mark "comma" on the note the breath mark follows
  * ornaments: trill-mark, mordent (LilyPond \\mordent, with the vertical stroke), inverted-mordent
    (\\prall, no stroke), turn, inverted-turn (\\reverseturn)
  * fermata type="upright" (above) / "inverted" (below); placement of articulations / ornaments /
    fingerings = the side LilyPond engraved (read back from the grobs)
  * fingering in <technical>, on the note it belongs to; arpeggiate on every note of the chord
  * dynamics / wedges / pedal / words / tempo / rehearsal as <direction> placed before the note at
    whose onset they are engraved (wedge stop = the note where the hairpin ends; LilyPond ends a
    hairpin at the next dynamic or \\!).  Pedal marks in LilyPond's default text style ("Ped." / "*")
    are <pedal type="start|stop" line="no" sign="yes"/>; a "*Ped." change is stop + start.
  * tempo marks: <words font-weight="bold"> + <metronome> (parentheses="yes" when the text and the
    number are both printed) + <sound tempo> in quarter notes per minute; expression text:
    <words font-style="italic">; rehearsal marks <rehearsal enclosure="square">
  * score-wide marks (tempo, rehearsal) are written once, in the part whose staff carries them in
    the engraving (the top staff)
  * chord symbols: <harmony> with root / kind / bass; kind@text = the printed suffix, or
    use-symbols="yes" for LilyPond's symbol forms (major-seventh triangle, diminished circle,
    half-diminished slashed circle, augmented +)
  * <stem> as engraved (read back from LilyPond), accidentals as LilyPond's default style prints them,
    <beam> on every note of a beamed chord (levels as engraved, manual beaming)
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from xml.sax.saxutils import escape, quoteattr

from .model import Ev, Score, display_ql

CLEF_XML = {'treble': ('G', 2, 0), 'treble_8': ('G', 2, -1), 'treble^8': ('G', 2, 1), 'bass': ('F', 4, 0),
            'bass_8': ('F', 4, -1), 'alto': ('C', 3, 0), 'tenor': ('C', 4, 0), 'soprano': ('C', 1, 0)}
NBEAMS = {'eighth': 1, '16th': 2, '32nd': 3, '64th': 4}
ARTIC_XML = {'staccato': '<staccato{p}/>', 'staccatissimo': '<staccatissimo{p}/>', 'accent': '<accent{p}/>',
             'tenuto': '<tenuto{p}/>', 'marcato': '<strong-accent{p} type="{up}"/>',
             'portato': '<detached-legato{p}/>'}
ORN_XML = {'trill': 'trill-mark', 'mordent': 'mordent', 'prall': 'inverted-mordent', 'turn': 'turn',
           'reverseturn': 'inverted-turn'}
KIND_TEXT = {'major': '', 'minor': 'm', 'dominant': '7', 'minor-seventh': 'm7', 'suspended-fourth': 'sus4',
             'suspended-second': 'sus2', 'major-sixth': '6', 'minor-sixth': 'm6', 'dominant-ninth': '9'}
KIND_SYMBOL = {'major-seventh', 'diminished', 'augmented', 'half-diminished', 'diminished-seventh'}


def _lcm(a, b):
    return a * b // math.gcd(a, b)


def divisions_for(score: Score):
    d = 1
    for p, st in score.staves():
        for evs in st.measures:
            for e in evs:
                d = _lcm(d, F(e.dur).denominator)
    for m in score.measures:
        d = _lcm(d, F(m.dur).denominator)
    offs = score.offsets()
    for p in score.parts:
        for c in p.chords:
            d = _lcm(d, F(c['t']).denominator)
    return d


def beam_elements(evs):
    """event index -> [(level, status)] for notes in manual beam groups"""
    groups, cur = [], None
    for k, ev in enumerate(evs):
        if not ev.is_rhythmic:
            continue
        if ev.beam_start:
            cur = [k]
        elif cur is not None:
            cur.append(k)
        if ev.beam_stop and cur is not None:
            groups.append(cur)
            cur = None
    out = {}
    for g in groups:
        notes = [k for k in g if evs[k].kind == 'note']
        if len(notes) != len(g):
            raise ValueError('rests inside beams are not supported')
        nb = {k: NBEAMS.get(evs[k].dtype, 0) for k in notes}
        for pos, k in enumerate(notes):
            els = []
            for lvl in range(1, nb[k] + 1):
                if lvl == 1:
                    st = 'begin' if pos == 0 else ('end' if pos == len(notes) - 1 else 'continue')
                else:
                    left = pos > 0 and nb[notes[pos - 1]] >= lvl
                    right = pos < len(notes) - 1 and nb[notes[pos + 1]] >= lvl
                    st = ('continue' if left and right else 'begin' if right else 'end' if left
                          else ('forward hook' if pos == 0 else 'backward hook'))
                els.append((lvl, st))
            out[k] = els
    return out


def _pl(place):
    return f' placement="{place}"' if place else ''


def tempo_direction(tp, staff_el, ind):
    out = [f'{ind}<direction placement="above">']
    if tp['text']:
        out.append(f'{ind}  <direction-type><words font-weight="bold">{escape(tp["text"])}</words></direction-type>')
    if tp['bpm']:
        par = ' parentheses="yes"' if tp['text'] else ''
        dot = '<beat-unit-dot/>' * tp['dots']
        out.append(f'{ind}  <direction-type><metronome{par}><beat-unit>{tp["unit"]}</beat-unit>{dot}'
                   f'<per-minute>{tp["bpm"]}</per-minute></metronome></direction-type>')
    out.append(staff_el)
    if tp['bpm']:
        q = tp['bpm'] * display_ql(tp['unit'], tp['dots'])
        qs = str(int(q)) if q.denominator == 1 else f'{float(q):.4f}'.rstrip('0')
        out.append(f'{ind}  <sound tempo="{qs}"/>')
    out.append(f'{ind}</direction>')
    return [x for x in out if x]


def harmony_xml(c, ind):
    r = f'<root-step>{c["root"][0]}</root-step>'
    if c['root'][1]:
        r += f'<root-alter>{c["root"][1]}</root-alter>'
    kind = c['kind']
    if kind in KIND_SYMBOL:
        k = f'<kind use-symbols="yes" text="">{kind}</kind>'
    else:
        k = f'<kind text={quoteattr(KIND_TEXT[kind])}>{kind}</kind>'
    b = ''
    if c['bass']:
        b = f'<bass><bass-step>{c["bass"][0]}</bass-step>'
        if c['bass'][1]:
            b += f'<bass-alter>{c["bass"][1]}</bass-alter>'
        b += '</bass>'
    return f'{ind}<harmony placement="above"><root>{r}</root>{k}{b}</harmony>'


def write_musicxml(score: Score, path: str, software='coverage/marks corpus builder (msynth)',
                   date='2026-11-08'):
    div = divisions_for(score)
    offs = score.offsets()
    out = []
    w = out.append
    w('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    w('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
      '"http://www.musicxml.org/dtds/partwise.dtd">')
    w('<score-partwise version="4.0">')
    w(f'  <work><work-title>{escape(score.title)}</work-title></work>')
    w('  <identification>')
    if score.composer:
        w(f'    <creator type="composer">{escape(score.composer)}</creator>')
    if score.rights:
        w(f'    <rights>{escape(score.rights)}</rights>')
    w('    <encoding>')
    w(f'      <software>{escape(software)}</software>')
    w(f'      <encoding-date>{date}</encoding-date>')
    w('    </encoding>')
    w('  </identification>')
    w('  <part-list>')
    gstart = {g['parts'][0]: (gi, g) for gi, g in enumerate(score.groups, 1) if g['type'] == 'StaffGroup'}
    gstop = {g['parts'][-1]: (gi, g) for gi, g in enumerate(score.groups, 1) if g['type'] == 'StaffGroup'}
    for p in score.parts:
        if p.id in gstart:
            gi, g = gstart[p.id]
            w(f'    <part-group type="start" number="{gi}">')
            if g.get('name'):
                w(f'      <group-name>{escape(g["name"])}</group-name>')
            w('      <group-symbol>bracket</group-symbol>')
            w('      <group-barline>yes</group-barline>')
            w('    </part-group>')
        w(f'    <score-part id="{p.id}">')
        w(f'      <part-name>{escape(p.name)}</part-name>')
        if p.abbr:
            w(f'      <part-abbreviation>{escape(p.abbr)}</part-abbreviation>')
        w('    </score-part>')
        if p.id in gstop:
            w(f'    <part-group type="stop" number="{gstop[p.id][0]}"/>')
    w('  </part-list>')

    for pi, p in enumerate(score.parts):
        multi = len(p.staves) > 1
        chords_at = {c['t']: c for c in p.chords}
        used_chords = set()
        w(f'  <part id="{p.id}">')
        for i, mi in enumerate(score.measures):
            w(f'    <measure number="{mi.number}">')
            if i > 0 and mi.new_page:
                w('      <print new-page="yes"/>')
            elif i > 0 and mi.new_system:
                w('      <print new-system="yes"/>')
            a = []
            if i == 0:
                a.append(f'        <divisions>{div}</divisions>')
            if i == 0 or mi.key:
                k = mi.key or score.key_at(i)
                a.append(f'        <key><fifths>{k[0]}</fifths><mode>{k[1]}</mode></key>')
            if i == 0 or mi.time:
                (tn, td), sym = score.time_at(i)
                sa = f' symbol="{sym}"' if sym else ''
                a.append(f'        <time{sa}><beats>{tn}</beats><beat-type>{td}</beat-type></time>')
            if i == 0:
                if multi:
                    a.append(f'        <staves>{len(p.staves)}</staves>')
                for st in p.staves:
                    a.append(_clef_xml(st.clef, st.number if multi else None, '        '))
            if a:
                w('      <attributes>')
                out.extend(a)
                w('      </attributes>')
            if mi.mark and pi == 0:
                w('      <direction placement="above"><direction-type>'
                  f'<rehearsal enclosure="square">{escape(mi.mark)}</rehearsal></direction-type></direction>')
            pos = F(0)
            for si, st in enumerate(p.staves):
                if si > 0 and pos > 0:
                    w(f'      <backup><duration>{int(pos * div)}</duration></backup>')
                    pos = F(0)
                staff_attr = st.number if multi else None
                stel = f'<staff>{staff_attr}</staff>' if staff_attr else ''
                evs = st.measures[i]
                beams = beam_elements(evs)
                for k, ev in enumerate(evs):
                    if ev.kind == 'clef':
                        w('      <attributes>')
                        w(_clef_xml(ev.clef, staff_attr, '        '))
                        w('      </attributes>')
                        continue
                    t_abs = offs[i] + pos
                    if si == 0 and t_abs in chords_at:
                        w(harmony_xml(chords_at[t_abs], '      '))
                        used_chords.add(t_abs)
                    _directions(w, ev, st.voice, stel)
                    d = int(ev.dur * div)
                    if ev.kind == 'rest':
                        _note(w, ev, None, False, d, st.voice, staff_attr, [], True)
                    else:
                        for c, pit in enumerate(ev.pitches):
                            _note(w, ev, pit, c > 0, d, st.voice, staff_attr, beams.get(k, []), c == 0)
                    pos += ev.dur
            if mi.right_bar:
                style = {'final': 'light-heavy', 'double': 'light-light'}[mi.right_bar]
                w(f'      <barline location="right"><bar-style>{style}</bar-style></barline>')
            w('    </measure>')
        if set(chords_at) != used_chords:
            raise ValueError(f'chord symbols not on a note/rest onset of {p.id}: '
                             f'{sorted(set(chords_at) - used_chords)}')
        w('  </part>')
    w('</score-partwise>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def _directions(w, ev: Ev, voice, stel):
    ind = '      '
    vel = f'<voice>{voice}</voice>'
    if ev.tempo:
        for x in tempo_direction(ev.tempo, f'{ind}  {stel}' if stel else '', ind):
            w(x)
    for txt, place in ev.words:
        w(f'{ind}<direction{_pl(place)}><direction-type><words font-style="italic">{escape(txt)}</words>'
          f'</direction-type>{vel}{stel}</direction>')
    for dyn in ev.dynamics:
        w(f'{ind}<direction placement="below"><direction-type><dynamics><{dyn}/></dynamics></direction-type>'
          f'{vel}{stel}</direction>')
    for wd in ev.wedges:
        typ = 'stop' if wd.startswith('stop') else wd
        w(f'{ind}<direction placement="below"><direction-type><wedge type="{typ}"/></direction-type>'
          f'{vel}{stel}</direction>')
    for pd in ev.pedal:
        w(f'{ind}<direction placement="below"><direction-type><pedal type="{pd}" line="no" sign="yes"/>'
          f'</direction-type>{vel}{stel}</direction>')


def _clef_xml(name, number, ind):
    sign, line, oc = CLEF_XML[name]
    na = f' number="{number}"' if number else ''
    s = f'{ind}<clef{na}><sign>{sign}</sign><line>{line}</line>'
    if oc:
        s += f'<clef-octave-change>{oc}</clef-octave-change>'
    return s + '</clef>'


def _note(w, ev: Ev, pit, chord, d, voice, staff, beams, first):
    ind = '        '
    w('      <note>')
    if chord:
        w(f'{ind}<chord/>')
    if ev.kind == 'rest':
        w(f'{ind}<rest measure="yes"/>' if ev.measure_rest else f'{ind}<rest/>')
    else:
        step, alter, octv = pit
        al = f'<alter>{alter}</alter>' if alter else ''
        w(f'{ind}<pitch><step>{step}</step>{al}<octave>{octv}</octave></pitch>')
    w(f'{ind}<duration>{d}</duration>')
    tie_stop = pit is not None and pit in ev.tie_stop
    tie_start = pit is not None and pit in ev.tie_start
    if tie_stop:
        w(f'{ind}<tie type="stop"/>')
    if tie_start:
        w(f'{ind}<tie type="start"/>')
    w(f'{ind}<voice>{voice}</voice>')
    if not ev.measure_rest:
        w(f'{ind}<type>{ev.dtype}</type>')
        for _ in range(ev.dots):
            w(f'{ind}<dot/>')
    if pit is not None and pit in ev.accidentals:
        w(f'{ind}<accidental>{ev.accidentals[pit]}</accidental>')
    if ev.kind == 'note' and ev.stem:
        w(f'{ind}<stem>{ev.stem}</stem>')
    if staff:
        w(f'{ind}<staff>{staff}</staff>')
    for lvl, st in beams:
        w(f'{ind}<beam number="{lvl}">{st}</beam>')
    nots = []
    if tie_stop:
        nots.append('<tied type="stop"/>')
    if tie_start:
        nots.append('<tied type="start"/>')
    if first:
        if ev.slur_stop:
            nots.append('<slur type="stop" number="1"/>')
        if ev.slur_start:
            nots.append('<slur type="start" number="1"/>')
        dirs = ev.mark_dirs if len(ev.mark_dirs) == len(ev.marks) else [pl for _, pl in ev.marks]
        marks = [(t, d) for (t, _), d in zip(ev.marks, dirs)]
        arts = [ARTIC_XML[t].format(p=_pl(pl), up='down' if pl == 'below' else 'up') for t, pl in marks
                if t in ARTIC_XML]
        if ev.breath:
            arts.append('<breath-mark>comma</breath-mark>')
        if arts:
            nots.append('<articulations>' + ''.join(arts) + '</articulations>')
        orns = [f'<{ORN_XML[t]}{_pl(pl)}/>' for t, pl in marks if t in ORN_XML]
        if orns:
            nots.append('<ornaments>' + ''.join(orns) + '</ornaments>')
        for t, pl in marks:
            if t == 'fermata':
                nots.append(f'<fermata type="{"inverted" if pl == "below" else "upright"}"/>')
    fdirs = ev.finger_dirs if len(ev.finger_dirs) == len(ev.fingering) else [pl for _, pl, _ in ev.fingering]
    fing = [(dg, d) for (dg, pl, fp), d in zip(ev.fingering, fdirs)
            if (fp is None and first) or (fp is not None and fp == pit)]
    if fing:
        nots.append('<technical>' + ''.join(f'<fingering{_pl(pl)}>{dg}</fingering>' for dg, pl in fing)
                    + '</technical>')
    if ev.arpeggio and ev.kind == 'note':
        nots.append('<arpeggiate/>')
    if nots:
        w(f'{ind}<notations>' + ''.join(nots) + '</notations>')
    w('      </note>')
