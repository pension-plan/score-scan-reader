"""Symbol counts (coverage taxonomy tags) computed from a truth.musicxml file.

Counting rules (also in coverage/rests/manifest.json "counting_rules"):
  * an "event" is a <note> without <chord/> together with the <chord/> notes that follow it;
    note-<type>, chord, dot, double-dot, stem-*, flag, grace count events; ledger-* and tie count
    note heads
  * note-<type>: non-grace, non-cue pitched events by <type>; rests are not notes
  * dot / double-dot: events (notes AND rests, grace excluded) with exactly 1 / 2 <dot/>
  * beam: beam groups (<beam number="1">begin</beam>); flag: unbeamed events of eighth or shorter
  * ledger-above / ledger-below: note heads at staff position >= +6 / <= -6 (they need ledger lines)
  * rest-<type>: <rest/> without measure="yes", by <type>; rest-dotted: such rests with >= 1 dot
  * rest-whole-bar: <rest measure="yes"/> outside a multi-bar rest block; rest-multibar: blocks
    (<multiple-rest>); the bars inside a block are not counted again
  * clef-*: every <clef> element (initial and changes); clef-change: <clef> after the first measure
  * key-0 / key-sN / key-fN, time-*: every <key> / <time> element; *-change: after the first measure
  * system-break / page-break: <print new-system/new-page> (first part only)
  * x-rest-raised / x-rest-lowered: rests with <display-step>/<display-octave> above / below the middle
    line (the normal position); x-rest-in-tuplet: rests with <time-modification>; x-rest-in-beam: rests
    inside an open beam group of their voice; x-rest-fermata: rests with <fermata>;
    x-rest-multibar-symbols / x-rest-multibar-hbar: <multiple-rest use-symbols="yes"/"no">;
    x-rest-whole-bar-shared-staff: whole-bar rests in a measure where another voice of the same staff
    has notes or rests
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter

STEPS = 'CDEFGAB'
TYPE_TAG = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
FLAGGED = {'eighth', '16th', '32nd', '64th', '128th'}
MIDLINE = {('G', 2, 0): ('B', 4), ('G', 2, -1): ('B', 3), ('G', 2, 1): ('B', 5), ('F', 4, 0): ('D', 3),
           ('F', 4, -1): ('D', 2), ('F', 3, 0): ('F', 3), ('C', 3, 0): ('C', 4), ('C', 4, 0): ('A', 3),
           ('C', 1, 0): ('G', 4), ('C', 2, 0): ('E', 4), ('C', 5, 0): ('F', 3), ('percussion', None, 0): ('B', 4)}
CLEF_TAG = {('G', 2, 0): 'clef-treble', ('G', 2, -1): 'clef-treble-8vb', ('G', 2, 1): 'clef-treble-8va',
            ('F', 4, 0): 'clef-bass', ('F', 4, -1): 'clef-bass-8vb', ('C', 3, 0): 'clef-alto',
            ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano'}
TIME_TAGS = {'2-4', '3-4', '4-4', '2-2', '3-2', '6-8', '9-8', '12-8', '5-4', '5-8', '7-8'}
ARTIC = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
         'strong-accent': 'marcato', 'breath-mark': 'breath'}
DYN = {'pp': 'dyn-pp', 'p': 'dyn-p', 'mp': 'dyn-mp', 'mf': 'dyn-mf', 'f': 'dyn-f', 'ff': 'dyn-ff',
       'sfz': 'dyn-sfz'}


def _steps(step, octave):
    return int(octave) * 7 + STEPS.index(step)


def _clef_key(c):
    sign = c.findtext('sign')
    line = c.findtext('line')
    oc = c.findtext('clef-octave-change')
    return (sign, int(line) if line else None, int(oc) if oc else 0)


def count_truth(path, pages=1):
    root = ET.parse(path).getroot()
    C = Counter()
    parts = root.findall('part')
    for pi, part in enumerate(parts):
        clefs = {}
        beam_open = {}          # voice -> bool
        mr_left = 0
        for mi, meas in enumerate(part.findall('measure')):
            first = mi == 0
            if pi == 0:
                for pr in meas.findall('print'):
                    if pr.get('new-page') == 'yes':
                        C['page-break'] += 1
                    elif pr.get('new-system') == 'yes':
                        C['system-break'] += 1
                for d in meas.iter('rehearsal'):
                    C['rehearsal-mark'] += 1
                for w in meas.iter('words'):
                    C['tempo-mark' if w.get('font-weight') == 'bold' else 'text-expression'] += 1
                if first and meas.get('implicit') == 'yes':
                    C['pickup'] += 1
            for d in meas.iter('metronome'):
                C['metronome'] += 1
            for d in meas.iter('dynamics'):
                for ch in d:
                    C[DYN.get(ch.tag, 'x-dyn-' + ch.tag)] += 1
            for wdg in meas.iter('wedge'):
                if wdg.get('type') == 'crescendo':
                    C['hairpin-cresc'] += 1
                elif wdg.get('type') == 'diminuendo':
                    C['hairpin-dim'] += 1
            # voices active per staff in this measure (for shared-staff whole-bar rests)
            active = {}
            for n in meas.findall('note'):
                st = n.findtext('staff') or '1'
                active.setdefault(st, set()).add(n.findtext('voice') or '1')
            new_block = 0
            for el in meas:
                if el.tag == 'attributes':
                    for c in el.findall('clef'):
                        k = _clef_key(c)
                        clefs[c.get('number', '1')] = k
                        C[CLEF_TAG.get(k, f'x-clef-{k[0]}{k[1]}{k[2]:+d}')] += 1
                        if not first:
                            C['clef-change'] += 1
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths'))
                        C['key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')] += 1
                        if not first:
                            C['key-change'] += 1
                    for t in el.findall('time'):
                        sym = t.get('symbol')
                        b, bt = t.findtext('beats'), t.findtext('beat-type')
                        if sym == 'common':
                            C['time-common'] += 1
                        elif sym == 'cut':
                            C['time-cut'] += 1
                        else:
                            tag = f'{b}-{bt}'
                            C[('time-' if tag in TIME_TAGS else 'x-time-') + tag] += 1
                        if not first:
                            C['time-change'] += 1
                    for ms in el.iter('multiple-rest'):
                        C['rest-multibar'] += 1
                        C['x-rest-multibar-symbols' if ms.get('use-symbols') == 'yes' else
                          'x-rest-multibar-hbar'] += 1
                        new_block = int(ms.text)
                elif el.tag == 'barline':
                    bs = el.findtext('bar-style')
                    rep = el.find('repeat')
                    if rep is not None:
                        C['repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'] += 1
                    elif bs == 'light-heavy':
                        C['barline-final'] += 1
                    elif bs == 'light-light':
                        C['barline-double'] += 1
                    for e in el.findall('ending'):
                        if e.get('type') == 'start':
                            C[f'volta-{e.get("number")}'] += 1
            if new_block:
                mr_left = new_block
            in_block = mr_left > 0
            # notes: group chords into events
            events = []
            for n in meas.findall('note'):
                if n.find('chord') is not None and events:
                    events[-1].append(n)
                else:
                    events.append([n])
            for ev in events:
                n0 = ev[0]
                voice = n0.findtext('voice') or '1'
                staff = n0.findtext('staff') or '1'
                grace = n0.find('grace')
                typ = n0.findtext('type')
                ndots = len(n0.findall('dot'))
                rest = n0.find('rest')
                notations = n0.find('notations')
                beams = {b.get('number', '1'): b.text for b in n0.findall('beam')}
                if rest is not None:
                    ds = rest.findtext('display-step')
                    if ds:
                        clef = clefs.get(staff, ('G', 2, 0))
                        mid = MIDLINE[clef]
                        pos = _steps(ds, rest.findtext('display-octave')) - _steps(*mid)
                        if pos > 0:
                            C['x-rest-raised'] += 1
                        elif pos < 0:
                            C['x-rest-lowered'] += 1
                    if rest.get('measure') == 'yes':
                        if not in_block:
                            C['rest-whole-bar'] += 1
                            if len(active.get(staff, ())) > 1:
                                C['x-rest-whole-bar-shared-staff'] += 1
                    else:
                        C['rest-' + TYPE_TAG.get(typ, typ)] += 1
                        if ndots:
                            C['rest-dotted'] += 1
                    if n0.find('time-modification') is not None:
                        C['x-rest-in-tuplet'] += 1
                    if beam_open.get(voice):
                        C['x-rest-in-beam'] += 1
                    if notations is not None and notations.find('fermata') is not None:
                        C['x-rest-fermata'] += 1
                else:
                    if grace is not None:
                        C['grace'] += 1
                        if grace.get('slash') == 'yes':
                            C['grace-slash'] += 1
                    elif n0.find('cue') is not None:
                        C['cue-note'] += 1
                    else:
                        C['note-' + TYPE_TAG.get(typ, typ)] += 1
                    if len(ev) > 1:
                        C['chord'] += 1
                    st = n0.findtext('stem')
                    if st in ('up', 'down'):
                        C['stem-' + st] += 1
                    if typ in FLAGGED and not beams:
                        C['flag'] += 1
                    if beams.get('1') == 'begin':
                        C['beam'] += 1
                    clef = clefs.get(staff, ('G', 2, 0))
                    mid = MIDLINE[clef]
                    for n in ev:
                        p = n.find('pitch')
                        if p is None:
                            continue
                        pos = _steps(p.findtext('step'), p.findtext('octave')) - _steps(*mid)
                        if pos >= 6:
                            C['ledger-above'] += 1
                        elif pos <= -6:
                            C['ledger-below'] += 1
                        for t in n.findall('tie'):
                            if t.get('type') == 'start':
                                C['tie'] += 1
                        acc = n.findtext('accidental')
                        if acc:
                            C[{'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural',
                               'double-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
                              .get(acc, 'x-acc-' + acc)] += 1
                    if n0.find('notations/tremolo') is not None or n0.find('.//tremolo') is not None:
                        C['tremolo'] += 1
                if grace is None:
                    if ndots == 1:
                        C['dot'] += 1
                    elif ndots == 2:
                        C['double-dot'] += 1
                if notations is not None:
                    for s in notations.findall('slur'):
                        if s.get('type') == 'start':
                            C['slur'] += 1
                    if notations.find('fermata') is not None:
                        C['fermata'] += 1
                    for t in notations.findall('tuplet'):
                        if t.get('type') == 'start':
                            tm = n0.find('time-modification')
                            a = tm.findtext('actual-notes') if tm is not None else '?'
                            C[f'tuplet-{a}' if a in ('2', '3', '5', '6', '7') else f'x-tuplet-{a}'] += 1
                    arts = notations.find('articulations')
                    if arts is not None:
                        for a in arts:
                            C[ARTIC.get(a.tag, 'x-' + a.tag)] += 1
                    orn = notations.find('ornaments')
                    if orn is not None:
                        for o in orn:
                            C[{'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent',
                               'turn': 'turn'}.get(o.tag, 'x-' + o.tag)] += 1
                    if notations.find('arpeggiate') is not None:
                        C['arpeggio'] += 1
                for ly in n0.findall('lyric'):
                    C['lyrics'] += 1
                # beam state after this event (rests between begin and end are "in beam")
                if rest is None and grace is None:
                    b1 = beams.get('1')
                    if b1 == 'begin':
                        beam_open[voice] = True
                    elif b1 == 'end':
                        beam_open[voice] = False
            if mr_left > 0:
                mr_left -= 1
    if pages > 1:
        C['multi-page'] = 1
    return dict(sorted((k, v) for k, v in C.items() if v))


def model_rest_counts(score):
    """rest tags counted from the score model (cross-check of the truth writer)"""
    C = Counter()
    T = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
         '16th': '16th', '32nd': '32nd', '64th': '64th'}
    for p in score.parts:
        for mm in p.measures:
            for evs in mm.values():
                for ev in evs:
                    if ev.kind != 'rest':
                        continue
                    if ev.measure_rest:
                        if ev.multirest > 1:
                            C['rest-multibar'] += 1
                        elif not ev.multirest_cont:
                            C['rest-whole-bar'] += 1
                    else:
                        C['rest-' + T[ev.dtype]] += 1
                        if ev.dots:
                            C['rest-dotted'] += 1
                    if ev.tuplet:
                        C['x-rest-in-tuplet'] += 1
                    if ev.fermata:
                        C['x-rest-fermata'] += 1
    return dict(C)
