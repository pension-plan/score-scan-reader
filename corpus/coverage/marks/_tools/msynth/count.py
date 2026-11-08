"""Count coverage-taxonomy symbol tags in a truth.musicxml (independent of the model).

Counting rules (written to meta.json 'counting_rules'):
  note-<type>, dot, double-dot, ledger-above/below, acc-*, tie, fingering: per notehead (<note>)
  chord, stem-up/down, flag, arpeggio, articulations, ornaments, fermata, slur: per stem/chord event
  beam: per beam group (<beam number="1">begin</beam> on the first note of a chord)
  rest-*: per rest (<rest measure="yes"/> -> rest-whole-bar), rest-dotted: dotted rests
  clef-*, key-*, time-*: per element in the truth (per part; clefs per staff); *-change: elements
    after the first of that kind in the part/staff
  dyn-*, hairpin-*, pedal, text-expression, tempo-mark, metronome, rehearsal-mark: per <direction>
    child (per hairpin start; pedal releases "*" are counted separately as x-pedal-release);
    tempo-mark = bold <words> (the engraved tempo text), text-expression = other <words>
  chord-symbol: per <harmony>; system-break / page-break: per <print new-system|new-page> of the first
    part (once per score)
  ledger-above / ledger-below: noteheads that need at least one ledger line above / below the staff
    (from the clef in force)
  tie-across-system: tie starting on the last note of a measure that ends a system
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter

TYPE_TAG = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
STEP_I = {s: i for i, s in enumerate('CDEFGAB')}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
ART_TAG = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
           'strong-accent': 'marcato', 'breath-mark': 'breath', 'detached-legato': 'x-portato',
           'caesura': 'x-caesura'}
ORN_TAG = {'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'x-inverted-mordent', 'turn': 'turn',
           'inverted-turn': 'x-inverted-turn', 'tremolo': 'tremolo'}
DYN_STD = {'pp', 'p', 'mp', 'mf', 'f', 'ff', 'sfz'}
TIME_STD = {(2, 4), (3, 4), (4, 4), (2, 2), (3, 2), (6, 8), (9, 8), (12, 8), (5, 4), (5, 8), (7, 8)}


def _clef_bottom(sign, line, octave_change):
    """diatonic index (octave*7+step) of the bottom staff line"""
    ref = {'G': 4 * 7 + 4, 'F': 3 * 7 + 3, 'C': 4 * 7 + 0}[sign]
    return ref - 2 * (line - 1) + 7 * octave_change


def count_truth(path, pages=1):
    root = ET.parse(path).getroot()
    c = Counter()
    for pidx, part in enumerate(root.findall('part')):
        clefs = {}          # staff -> bottom line index
        seen_clef, seen_key, seen_time = Counter(), 0, 0
        measures = part.findall('measure')
        for mi, meas in enumerate(measures):
            pr = meas.find('print')
            if pr is not None and pr.get('new-system') == 'yes' and pidx == 0:
                c['system-break'] += 1
            if pr is not None and pr.get('new-page') == 'yes' and pidx == 0:
                c['page-break'] += 1
            if meas.get('implicit') == 'yes':
                c['pickup'] += 1
            last_note_first = None
            for el in meas:
                if el.tag == 'attributes':
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths'))
                        c['key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')] += 1
                        if seen_key:
                            c['key-change'] += 1
                        seen_key += 1
                    for t in el.findall('time'):
                        b, bt = int(t.findtext('beats')), int(t.findtext('beat-type'))
                        sym = t.get('symbol')
                        if sym == 'common':
                            c['time-common'] += 1
                        elif sym == 'cut':
                            c['time-cut'] += 1
                        elif (b, bt) in TIME_STD:
                            c[f'time-{b}-{bt}'] += 1
                        else:
                            c[f'x-time-{b}-{bt}'] += 1
                        if seen_time:
                            c['time-change'] += 1
                        seen_time += 1
                    for cl in el.findall('clef'):
                        n = int(cl.get('number', '1'))
                        sign, line = cl.findtext('sign'), int(cl.findtext('line') or 0)
                        oc = int(cl.findtext('clef-octave-change') or 0)
                        tag = {('G', 2, 0): 'clef-treble', ('F', 4, 0): 'clef-bass', ('C', 3, 0): 'clef-alto',
                               ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano', ('G', 2, -1): 'clef-treble-8vb',
                               ('G', 2, 1): 'clef-treble-8va', ('F', 4, -1): 'clef-bass-8vb'}.get(
                            (sign, line, oc), f'x-clef-{sign}{line}')
                        c[tag] += 1
                        if seen_clef[n]:
                            c['clef-change'] += 1
                        seen_clef[n] += 1
                        clefs[n] = _clef_bottom(sign, line, oc)
                    for ms in el.findall('measure-style/multiple-rest'):
                        c['rest-multibar'] += 1
                elif el.tag == 'harmony':
                    c['chord-symbol'] += 1
                elif el.tag == 'direction':
                    for dt in el.findall('direction-type'):
                        for x in dt:
                            if x.tag == 'dynamics':
                                for d in x:
                                    c[f'dyn-{d.tag}' if d.tag in DYN_STD else f'x-dyn-{d.tag}'] += 1
                            elif x.tag == 'wedge' and x.get('type') in ('crescendo', 'diminuendo'):
                                c['hairpin-cresc' if x.get('type') == 'crescendo' else 'hairpin-dim'] += 1
                            elif x.tag == 'pedal':
                                c['pedal' if x.get('type') == 'start' else 'x-pedal-release'] += 1
                            elif x.tag == 'words':
                                c['tempo-mark' if x.get('font-weight') == 'bold' else 'text-expression'] += 1
                            elif x.tag == 'metronome':
                                c['metronome'] += 1
                            elif x.tag == 'rehearsal':
                                c['rehearsal-mark'] += 1
                            elif x.tag == 'segno':
                                c['segno'] += 1
                            elif x.tag == 'coda':
                                c['coda'] += 1
                            elif x.tag == 'octave-shift' and x.get('type') != 'stop':
                                c[{8: 'ottava-8va' if x.get('type') == 'down' else 'ottava-8vb',
                                   15: 'ottava-15ma'}.get(int(x.get('size', 8)), 'x-ottava')] += 1
                elif el.tag == 'barline':
                    bs = el.findtext('bar-style')
                    rep = el.find('repeat')
                    if rep is not None:
                        c['repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'] += 1
                    elif bs == 'light-light':
                        c['barline-double'] += 1
                    elif bs == 'light-heavy':
                        c['barline-final'] += 1
                    for e in el.findall('ending'):
                        if e.get('type') == 'start':
                            c[f"volta-{e.get('number')}"] += 1
                    if el.find('fermata') is not None:
                        c['fermata'] += 1
                elif el.tag == 'note':
                    is_chord_member = el.find('chord') is not None
                    if el.find('grace') is not None:
                        c['grace'] += 1
                        if el.find('grace').get('slash') == 'yes':
                            c['grace-slash'] += 1
                        continue
                    if el.find('cue') is not None:
                        c['cue-note'] += 1
                    typ = el.findtext('type')
                    ndots = len(el.findall('dot'))
                    rest = el.find('rest')
                    if rest is not None:
                        if rest.get('measure') == 'yes':
                            c['rest-whole-bar'] += 1
                        else:
                            c['rest-' + TYPE_TAG[typ]] += 1
                            if ndots:
                                c['rest-dotted'] += 1
                    else:
                        c['note-' + TYPE_TAG[typ]] += 1
                        if ndots == 1:
                            c['dot'] += 1
                        elif ndots >= 2:
                            c['double-dot'] += 1
                        pitch = el.find('pitch')
                        staff = int(el.findtext('staff') or 1)
                        di = int(pitch.findtext('octave')) * 7 + STEP_I[pitch.findtext('step')]
                        bottom = clefs.get(staff)
                        if bottom is not None:
                            if di >= bottom + 10:
                                c['ledger-above'] += 1
                            elif di <= bottom - 2:
                                c['ledger-below'] += 1
                        acc = el.find('accidental')
                        if acc is not None:
                            c[ACC_TAG.get(acc.text, 'x-acc-' + (acc.text or ''))] += 1
                            if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes':
                                c['acc-courtesy'] += 1
                        for t in el.findall('tie'):
                            if t.get('type') == 'start':
                                c['tie'] += 1
                                if _next_system(measures, mi) and _last_in_voice(meas, el):
                                    c['tie-across-system'] += 1
                        if not is_chord_member:
                            last_note_first = el
                            stem = el.findtext('stem')
                            if stem in ('up', 'down'):
                                c['stem-' + stem] += 1
                            if typ in ('eighth', '16th', '32nd', '64th') and el.find('beam') is None:
                                c['flag'] += 1
                            for b in el.findall('beam'):
                                if b.get('number') == '1' and b.text == 'begin':
                                    c['beam'] += 1
                        elif last_note_first is not None and last_note_first.get('_chord') is None:
                            c['chord'] += 1
                            last_note_first.set('_chord', '1')
                    nots = el.findall('notations')
                    for n in nots:
                        for x in n:
                            if x.tag == 'technical':
                                for y in x:
                                    if y.tag == 'fingering':
                                        c['fingering'] += 1
                                    else:
                                        c['x-technical-' + y.tag] += 1
                            if is_chord_member:
                                continue
                            if x.tag == 'slur' and x.get('type') == 'start':
                                c['slur'] += 1
                            elif x.tag == 'articulations':
                                for y in x:
                                    c[ART_TAG.get(y.tag, 'x-' + y.tag)] += 1
                            elif x.tag == 'ornaments':
                                for y in x:
                                    c[ORN_TAG.get(y.tag, 'x-' + y.tag)] += 1
                            elif x.tag == 'fermata':
                                c['fermata'] += 1
                            elif x.tag == 'arpeggiate':
                                c['arpeggio'] += 1
                            elif x.tag == 'tuplet' and x.get('type') == 'start':
                                tm = el.find('time-modification')
                                n = tm.findtext('actual-notes') if tm is not None else '?'
                                c[f'tuplet-{n}' if n in ('2', '3', '5', '6', '7') else f'x-tuplet-{n}'] += 1
                    if el.findall('lyric'):
                        c['lyrics'] += 1
    if pages > 1:
        c['multi-page'] = pages
    for k in [k for k, v in c.items() if not v]:
        del c[k]
    return dict(sorted(c.items()))


def _last_in_voice(meas, note):
    v = note.findtext('voice')
    notes = [n for n in meas.findall('note') if n.findtext('voice') == v and n.find('chord') is None]
    first = note
    if note.find('chord') is not None:
        return False
    return notes and notes[-1] is first


def _next_system(measures, mi):
    if mi + 1 >= len(measures):
        return False
    pr = measures[mi + 1].find('print')
    return pr is not None and (pr.get('new-system') == 'yes' or pr.get('new-page') == 'yes')
