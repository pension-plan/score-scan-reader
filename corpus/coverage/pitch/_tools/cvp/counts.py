"""Taxonomy counter: canonical coverage-suite symbol tags counted from a truth.musicxml file.

Independent of the score model: everything is read back from the MusicXML file itself, so the
counts describe exactly what the truth contains.  Conventions (also written to meta.json):

  per notehead : note-<type>, dot, double-dot, acc-*, ledger-above, ledger-below, tie (tie starts),
                 grace, cue-note
  per stem     : chord (events with >= 2 heads), stem-up, stem-down, flag (unbeamed 8th or shorter)
  per group    : beam (level-1 beam groups), slur, tuplet-N (tuplet brackets/numbers), hairpins
  per element  : clef-* (initial clefs + changes), key-* (initial + changes, not system-start
                 reprints), time-*, ottava-* (brackets), barline-*, dynamics, articulations
  rest-*       : per rest; rest-whole-bar = <rest measure="yes"/>; rest-dotted = dotted rests
  ledger-*     : a notehead whose displayed staff position is >= 6 / <= -6 half-spaces from the
                 middle line (i.e. it needs at least one ledger line), with clef, clef octave
                 change and octave-shift applied
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction as F

STEPS = 'CDEFGAB'
TYPE_TAG = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
SHORT = ('eighth', '16th', '32nd', '64th', '128th')
TIME_TAGS = {(2, 4), (3, 4), (4, 4), (2, 2), (3, 2), (6, 8), (9, 8), (12, 8), (5, 4), (5, 8), (7, 8)}
ACC_TAG = {'sharp': ['acc-sharp'], 'flat': ['acc-flat'], 'natural': ['acc-natural'],
           'double-sharp': ['acc-double-sharp'], 'sharp-sharp': ['acc-double-sharp'],
           'flat-flat': ['acc-double-flat'], 'natural-sharp': ['x-acc-natural-sharp'],
           'natural-flat': ['x-acc-natural-flat']}
ARTIC = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
         'strong-accent': 'marcato', 'breath-mark': 'breath'}
DYN = {'pp': 'dyn-pp', 'p': 'dyn-p', 'mp': 'dyn-mp', 'mf': 'dyn-mf', 'f': 'dyn-f', 'ff': 'dyn-ff', 'sfz': 'dyn-sfz'}


def dia(step, octave):
    return octave * 7 + STEPS.index(step)


def middle_line(sign, line, octave_change):
    """diatonic index of the *sounding* pitch on the middle line"""
    if sign == 'G':
        base = dia('G', 4)
    elif sign == 'F':
        base = dia('F', 3)
    elif sign == 'C':
        base = dia('C', 4)
    else:
        return None
    return base - (line - 3) * 2 + 7 * octave_change


def clef_tag(sign, line, oc):
    return {('G', 2, 0): 'clef-treble', ('G', 2, -1): 'clef-treble-8vb', ('G', 2, 1): 'clef-treble-8va',
            ('F', 4, 0): 'clef-bass', ('F', 4, -1): 'clef-bass-8vb', ('C', 3, 0): 'clef-alto',
            ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano'}.get((sign, line, oc),
                                                                         f'x-clef-{sign}{line}{oc:+d}')


def key_tag(fifths):
    if fifths == 0:
        return 'key-0'
    return f'key-s{fifths}' if fifths > 0 else f'key-f{-fifths}'


def count_truth(path):
    """-> (Counter of tags, positions dict (part_id, staff, onset, (step, alter, octave)) -> staff position)"""
    root = ET.parse(path).getroot()
    c = Counter()
    positions = {}
    parts = root.findall('part')
    first_part = True
    for part in parts:
        pid = part.get('id')
        div = 1
        clef = {}                 # staff -> (sign, line, oc)
        shift = {}                # staff -> display octave shift (+1 = 8va: displayed an octave lower)
        first_attr_done = False
        verses = set()
        open_ties = 0
        measures = part.findall('measure')
        starts = measure_starts(measures)
        sys_start = set()
        for mi, meas in enumerate(measures):
            pr = meas.find('print')
            if pr is not None and (pr.get('new-system') == 'yes' or pr.get('new-page') == 'yes'):
                sys_start.add(mi)
        for mi, meas in enumerate(measures):
            if mi == 0 and meas.get('implicit') == 'yes' and first_part:
                c['pickup'] += 1
            if first_part:
                pr = meas.find('print')
                if pr is not None and pr.get('new-system') == 'yes':
                    c['system-break'] += 1
                if pr is not None and pr.get('new-page') == 'yes':
                    c['page-break'] += 1
            pos = F(0)
            last_onset = F(0)
            for el in meas:
                if el.tag == 'attributes':
                    d = el.find('divisions')
                    if d is not None:
                        div = int(d.text)
                    for k in el.findall('key'):
                        c[key_tag(int(k.findtext('fifths')))] += 1
                        if (k.findtext('mode') or 'major') == 'minor':
                            c['x-key-minor'] += 1
                        if mi > 0:
                            c['key-change'] += 1
                        if k.find('cancel') is not None:
                            c['x-key-cancel'] += 1
                    for t in el.findall('time'):
                        n, dd = int(t.findtext('beats')), int(t.findtext('beat-type'))
                        sym = t.get('symbol')
                        if sym == 'common':
                            c['time-common'] += 1
                        elif sym == 'cut':
                            c['time-cut'] += 1
                        elif (n, dd) in TIME_TAGS:
                            c[f'time-{n}-{dd}'] += 1
                        else:
                            c[f'x-time-{n}-{dd}'] += 1
                        if mi > 0:
                            c['time-change'] += 1
                    for cl in el.findall('clef'):
                        st = int(cl.get('number', '1'))
                        sign = cl.findtext('sign')
                        line = int(cl.findtext('line') or 0)
                        oc = int(cl.findtext('clef-octave-change') or 0)
                        clef[st] = (sign, line, oc)
                        c[clef_tag(sign, line, oc)] += 1
                        if first_attr_done:
                            c['clef-change'] += 1
                    first_attr_done = True
                elif el.tag == 'backup':
                    pos -= F(int(el.findtext('duration')), div)
                elif el.tag == 'forward':
                    pos += F(int(el.findtext('duration')), div)
                elif el.tag == 'direction':
                    st = int(el.findtext('staff') or 1)
                    for dt in el.findall('direction-type'):
                        for os_ in dt.findall('octave-shift'):
                            typ, size = os_.get('type'), int(os_.get('size', '8'))
                            n = 1 if size == 8 else 2 if size == 15 else 3
                            if typ == 'down':
                                shift[st] = n
                                c['ottava-8va' if n == 1 else 'ottava-15ma' if n == 2 else 'x-ottava-22ma'] += 1
                            elif typ == 'up':
                                shift[st] = -n
                                c['ottava-8vb' if n == 1 else 'x-ottava-15mb' if n == 2 else 'x-ottava-22mb'] += 1
                            elif typ == 'stop':
                                shift[st] = 0
                        for dyn in dt.findall('dynamics'):
                            for x in dyn:
                                c[DYN.get(x.tag, 'x-dyn-' + x.tag)] += 1
                        for w in dt.findall('wedge'):
                            if w.get('type') == 'crescendo':
                                c['hairpin-cresc'] += 1
                            elif w.get('type') == 'diminuendo':
                                c['hairpin-dim'] += 1
                        if dt.find('words') is not None:
                            c['text-expression'] += 1
                        if dt.find('metronome') is not None:
                            c['metronome'] += 1
                        if dt.find('rehearsal') is not None:
                            c['rehearsal-mark'] += 1
                        if dt.find('segno') is not None:
                            c['segno'] += 1
                        if dt.find('coda') is not None:
                            c['coda'] += 1
                        if dt.find('pedal') is not None and dt.find('pedal').get('type') == 'start':
                            c['pedal'] += 1
                elif el.tag == 'barline':
                    style = el.findtext('bar-style')
                    rep = el.find('repeat')
                    if rep is not None:
                        c['repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'] += 1
                    elif style == 'light-light':
                        c['barline-double'] += 1
                    elif style == 'light-heavy':
                        c['barline-final'] += 1
                    for e_ in el.findall('ending'):
                        if e_.get('type') == 'start':
                            c['volta-' + e_.get('number', '1').split(',')[0].strip()] += 1
                elif el.tag == 'note':
                    is_chord = el.find('chord') is not None
                    dur = F(int(el.findtext('duration') or 0), div)
                    if is_chord:
                        onset = last_onset
                    else:
                        onset = pos
                        if el.find('grace') is None:
                            pos += dur
                    last_onset = onset
                    typ = el.findtext('type')
                    ndots = len(el.findall('dot'))
                    st = int(el.findtext('staff') or 1)
                    grace = el.find('grace')
                    if el.find('rest') is not None:
                        r = el.find('rest')
                        if r.get('measure') == 'yes':
                            c['rest-whole-bar'] += 1
                        elif typ:
                            c['rest-' + TYPE_TAG.get(typ, typ)] += 1
                        if ndots:
                            c['rest-dotted'] += 1
                        continue
                    if grace is not None:
                        c['grace'] += 1
                        if grace.get('slash') == 'yes':
                            c['grace-slash'] += 1
                    elif el.find('cue') is not None:
                        c['cue-note'] += 1
                    elif typ:
                        c['note-' + TYPE_TAG.get(typ, typ)] += 1
                    if ndots == 1:
                        c['dot'] += 1
                    elif ndots == 2:
                        c['double-dot'] += 1
                    # chord / stems / beams / flags (first note of the event only)
                    nxt_is_chord = False
                    if not is_chord:
                        sib = list(meas)
                        k = sib.index(el)
                        if k + 1 < len(sib) and sib[k + 1].tag == 'note' and sib[k + 1].find('chord') is not None:
                            nxt_is_chord = True
                        if nxt_is_chord:
                            c['chord'] += 1
                        stem = el.findtext('stem')
                        if stem == 'up':
                            c['stem-up'] += 1
                        elif stem == 'down':
                            c['stem-down'] += 1
                        beams = {b.get('number', '1'): b.text for b in el.findall('beam')}
                        if beams.get('1') == 'begin':
                            c['beam'] += 1
                        if typ in SHORT and not beams and grace is None:
                            c['flag'] += 1
                        nots = el.find('notations')
                        if nots is not None:
                            for sl in nots.findall('slur'):
                                if sl.get('type') == 'start':
                                    c['slur'] += 1
                            for tp in nots.findall('tuplet'):
                                if tp.get('type') == 'start':
                                    tm = el.find('time-modification')
                                    a = tm.findtext('actual-notes') if tm is not None else '3'
                                    c[f'tuplet-{a}'] += 1
                            if nots.find('fermata') is not None:
                                c['fermata'] += 1
                            if nots.find('arpeggiate') is not None:
                                c['arpeggio'] += 1
                            for ar in nots.findall('articulations'):
                                for x in ar:
                                    c[ARTIC.get(x.tag, 'x-artic-' + x.tag)] += 1
                            for orn in nots.findall('ornaments'):
                                for x in orn:
                                    c[{'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent',
                                       'turn': 'turn', 'tremolo': 'tremolo'}.get(x.tag, 'x-orn-' + x.tag)] += 1
                    # pitch-level symbols (every notehead)
                    acc = el.find('accidental')
                    if acc is not None:
                        for tg in ACC_TAG.get(acc.text, ['x-acc-' + (acc.text or '')]):
                            c[tg] += 1
                        if acc.get('cautionary') == 'yes':
                            c['acc-courtesy'] += 1
                            if acc.get('parentheses') == 'yes':
                                c['x-acc-courtesy-paren'] += 1
                    for t in el.findall('tie'):
                        if t.get('type') == 'start':
                            c['tie'] += 1
                            if mi + 1 in sys_start and starts[mi] + onset + dur >= starts[mi + 1]:
                                c['tie-across-system'] += 1
                    p = el.find('pitch')
                    if p is not None and st in clef:
                        sign, line, oc = clef[st]
                        ml = middle_line(sign, line, oc)
                        if ml is not None:
                            step, octv = p.findtext('step'), int(p.findtext('octave'))
                            alter = int(float(p.findtext('alter') or 0))
                            # displayed position: an 8va bracket shows the note an octave lower
                            sp = dia(step, octv) - 7 * shift.get(st, 0) - ml
                            positions[(pid, st, starts[mi] + onset, (step, alter, octv))] = sp
                            if sp >= 6:
                                c['ledger-above'] += 1
                            elif sp <= -6:
                                c['ledger-below'] += 1
                    for ly in el.findall('lyric'):
                        c['lyrics'] += 1
                        verses.add(ly.get('number', '1'))
                        if ly.findtext('syllabic') in ('begin', 'middle'):
                            c['lyrics-hyphen'] += 1
                        if ly.find('extend') is not None:
                            c['lyrics-extender'] += 1
                        if ly.find('elision') is not None:
                            c['lyrics-elision'] += 1
        if len(verses) > 1:
            c['lyrics-multi-verse'] += 1
        first_part = False
    return c, positions


def measure_starts(measures):
    """absolute start (quarters) of every measure, plus the end of the last one"""
    starts, t, dv = [], F(0), 1
    for meas in measures:
        starts.append(t)
        p, mx = F(0), F(0)
        for el in meas:
            if el.tag == 'attributes' and el.find('divisions') is not None:
                dv = int(el.findtext('divisions'))
            elif el.tag == 'backup':
                p -= F(int(el.findtext('duration')), dv)
            elif el.tag == 'forward':
                p += F(int(el.findtext('duration')), dv)
                mx = max(mx, p)
            elif el.tag == 'note' and el.find('chord') is None and el.find('grace') is None:
                p += F(int(el.findtext('duration')), dv)
                mx = max(mx, p)
        t += mx
    starts.append(t)
    return starts


CONVENTIONS = {
    'note-*, dot, double-dot, acc-*, ledger-*, tie': 'per notehead (chord notes counted individually)',
    'chord, stem-up, stem-down, flag': 'per stem (one per chord)',
    'beam': 'number of level-1 beam groups',
    'clef-*': 'initial clef of every staff + every clef change (system-start reprints and courtesy clefs not counted)',
    'clef-change': 'clef elements after the initial clefs',
    'key-*': 'initial key + every key change (system-start reprints and courtesy key signatures not counted); '
             'key-0 = no sharps/flats',
    'key-change': 'key elements after measure 1; x-key-cancel = key changes that print cancellation naturals',
    'key-* / time-* / key-change per part': 'counted per MusicXML <key>/<time> element, i.e. once per part: a '
                                            'multi-staff part (piano, organ) has one <key> for all its staves, so '
                                            'the printed signatures are N_staves times more numerous',
    'x-key-minor': 'key statements in minor mode',
    'time-*': 'time signature statements (time-common / time-cut replace time-4-4 / time-2-2 when the symbol is used)',
    'ottava-*': 'octave-shift brackets (start elements); x-ottava-15mb = 15ma bassa',
    'ledger-above / ledger-below': 'noteheads needing >= 1 ledger line (displayed staff position >= 6 or <= -6 '
                                   'half-spaces from the middle line, after clef / clef-octave-change / ottava)',
    'acc-courtesy': 'accidentals with cautionary="yes" (also counted under their glyph tag); '
                    'x-acc-courtesy-paren = the parenthesised subset',
    'x-acc-natural-sharp / x-acc-natural-flat': 'LilyPond "extra natural" before a single sharp/flat that '
                                                'follows a double sharp/flat in the same bar (natural-sharp / natural-flat)',
    'system-break / page-break': 'explicit <print new-system/new-page> in the first part',
}
