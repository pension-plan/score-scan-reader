"""Taxonomy symbol counts read back from a truth.musicxml (coverage suite, family 'time').

Every count is computed from the MusicXML truth file itself (not from the generator's
model), so meta.counts is by construction "number of occurrences in truth".
Counting rules (COUNT_RULES below is copied into meta.json):
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from fractions import Fraction as F

COUNT_RULES = {
    'note-<type>': 'one per pitched, non-grace, non-cue <note> element with that <type> (chord members '
                   'count individually, tie continuations count)',
    'dot / double-dot': 'one per non-grace <note> element (notes AND rests, chord members individually) '
                        'with exactly one / two <dot/>',
    'chord': 'one per chord (a <note> followed by <chord/> members)',
    'beam': 'one per beam group (level-1 <beam>begin</beam> on a non-chord-member note)',
    'flag': 'one per stem (non-grace, non-chord-member note of type eighth or shorter) without any <beam>',
    'ledger-above / ledger-below': 'one per notehead that needs ledger lines above / below its staff '
                                   '(position computed from pitch and the clef in force)',
    'grace / grace-slash': 'one per grace <note> element / with slash="yes"',
    'rest-<type>': 'one per non-measure <rest> with that <type>',
    'rest-dotted': 'one per dotted non-measure rest',
    'rest-whole-bar': 'one per <rest measure="yes"> not inside a multi-bar rest block',
    'rest-multibar': 'one per <multiple-rest> block',
    'clef-<kind>': 'one per <clef> element (initial clefs included; a piano grand staff has two)',
    'clef-change': 'one per <clef> element after the first measure\'s initial attributes',
    'key-0 / key-sN / key-fN': 'one per <key> element (per part)',
    'key-change': 'one per <key> element after measure 1',
    'acc-<kind>': 'one per <accidental> element; acc-courtesy = cautionary/parenthesized accidentals',
    'time-<n>-<d>': 'one per <time> element printed as numbers (per part; a grand staff prints it on '
                    'both staves but the truth has one <time>); 4/4 and 2/2 printed as C / cut are '
                    'time-common / time-cut, NOT time-4-4 / time-2-2',
    'time-change': 'one per <time> element after the first measure of the part',
    'pickup': 'one per part whose first measure is implicit="yes" (anacrusis)',
    'tuplet-<n>': 'one per tuplet group (<tuplet type="start">, every nesting level) by its actual '
                  'number (tuplet-actual/tuplet-number, else time-modification/actual-notes); 4:3 '
                  'quadruplets are x-tuplet-4',
    'tuplet-nested': 'one per tuplet group nested inside another tuplet (<tuplet number="2"> or deeper)',
    'tie': 'one per <tied type="start"> (per notehead: a 3-note chord tie counts 3)',
    'tie-across-system': 'ties whose stop lies after a system break (print new-system OR new-page) '
                         'relative to the start; x-tie-across-page = the subset across a page break',
    'slur': 'one per <slur type="start">',
    'staccato/accent/tenuto/fermata/...': 'one per notation element',
    'dyn-<x>': 'one per dynamics element',
    'tempo-mark': 'one per bold <words> direction at a measure start (engraved with \\tempo)',
    'rehearsal-mark': 'one per <rehearsal>',
    'barline-<x> / repeat-<x>': 'one per <barline> of that style',
    'system-break / page-break': 'one per <print new-system="yes"> / <print new-page="yes"> (part 1 only)',
    'multi-page': '1 when the truth has at least one page break',
    'lyrics': 'one per <lyric> element (syllable)',
    'lyrics-hyphen': 'one per syllable with syllabic begin/middle (a hyphen follows)',
    'lyrics-extender': 'one per <extend/>',
    'lyrics-melisma': 'one per syllable sung on more than one attack (a later non-tied note of the '
                      'same voice before the next syllable of that verse)',
    'lyrics-multi-verse': 'number of lyric lines (verses) when more than one',
}

TYPES = ['breve', 'whole', 'half', 'quarter', 'eighth', '16th', '32nd', '64th']
TAG_TYPE = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
STEP_IDX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
ART_TAG = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
           'strong-accent': 'marcato', 'breath-mark': 'breath'}
DYN_TAG = {'pp': 'dyn-pp', 'p': 'dyn-p', 'mp': 'dyn-mp', 'mf': 'dyn-mf', 'f': 'dyn-f', 'ff': 'dyn-ff',
           'sfz': 'dyn-sfz'}


def _diat(step, octv):
    return octv * 7 + STEP_IDX[step]


def clef_tag(sign, line, oct_change):
    if sign == 'G' and line == 2:
        return {0: 'clef-treble', -1: 'clef-treble-8vb', 1: 'clef-treble-8va'}.get(oct_change, 'x-clef-other')
    if sign == 'F' and line == 4:
        return {0: 'clef-bass', -1: 'clef-bass-8vb'}.get(oct_change, 'x-clef-other')
    if sign == 'C':
        return {1: 'clef-soprano', 3: 'clef-alto', 4: 'clef-tenor'}.get(line, 'x-clef-other')
    return 'x-clef-other'


def clef_bottom_line(sign, line, oct_change):
    """diatonic index of the pitch on the bottom staff line"""
    if sign == 'G':
        ref = _diat('G', 4) - 2 * (line - 1)
    elif sign == 'F':
        ref = _diat('F', 3) - 2 * (line - 1)
    elif sign == 'C':
        ref = _diat('C', 4) - 2 * (line - 1)
    else:
        return None
    return ref + 7 * oct_change


def count_truth(path):
    root = ET.parse(path).getroot()
    C = Counter()
    where = defaultdict(list)       # tag -> measure numbers (with repetition)

    def add(tag, mnum, n=1):
        C[tag] += n
        for _ in range(n):
            where[tag].append(mnum)

    parts = root.findall('part')
    n_pages_breaks = 0
    for pi, part in enumerate(parts):
        measures = part.findall('measure')
        # system index of every measure (from part 1 print elements, they are identical per part)
        sys_idx, page_idx = [], []
        s_i = p_i = 0
        for m in measures:
            pr = m.find('print')
            if pr is not None and pr.get('new-page') == 'yes':
                s_i += 1
                p_i += 1
            elif pr is not None and pr.get('new-system') == 'yes':
                s_i += 1
            sys_idx.append(s_i)
            page_idx.append(p_i)
        clefs = {}          # staff number -> bottom-line diatonic index
        open_ties = {}      # (voice, staff, step, alter, octave) -> measure index
        multirest_left = 0
        verses_seen = set()
        lyr_state = {}      # (voice, verse) -> [mnum, attacks_since]
        for mi, m in enumerate(measures):
            mnum = m.get('number')
            pr = m.find('print')
            if pi == 0 and pr is not None:
                if pr.get('new-page') == 'yes':
                    add('page-break', mnum)
                    n_pages_breaks += 1
                elif pr.get('new-system') == 'yes':
                    add('system-break', mnum)
            if mi == 0 and m.get('implicit') == 'yes':
                add('pickup', mnum)
            first_attr = True
            for el in m:
                tag = el.tag
                if tag == 'attributes':
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths', '0'))
                        add('key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}'), mnum)
                        if mi > 0:
                            add('key-change', mnum)
                    for t in el.findall('time'):
                        sym = t.get('symbol')
                        b, bt = t.findtext('beats'), t.findtext('beat-type')
                        if sym == 'common':
                            add('time-common', mnum)
                        elif sym == 'cut':
                            add('time-cut', mnum)
                        else:
                            add(f'time-{b}-{bt}', mnum)
                        if mi > 0:
                            add('time-change', mnum)
                    for c in el.findall('clef'):
                        sign, line = c.findtext('sign'), int(c.findtext('line', '0') or 0)
                        oc = int(c.findtext('clef-octave-change', '0'))
                        add(clef_tag(sign, line, oc), mnum)
                        if not (mi == 0 and first_attr):
                            add('clef-change', mnum)
                        clefs[int(c.get('number', '1'))] = clef_bottom_line(sign, line, oc)
                    ms = el.find('measure-style/multiple-rest')
                    if ms is not None:
                        add('rest-multibar', mnum)
                        multirest_left = int(ms.text)
                    first_attr = False
                elif tag == 'direction':
                    for dt in el.findall('direction-type'):
                        for d in dt:
                            if d.tag == 'dynamics':
                                for x in d:
                                    add(DYN_TAG.get(x.tag, f'x-dyn-{x.tag}'), mnum)
                            elif d.tag == 'words':
                                add('tempo-mark' if d.get('font-weight') == 'bold' else 'text-expression', mnum)
                            elif d.tag == 'rehearsal':
                                add('rehearsal-mark', mnum)
                            elif d.tag == 'metronome':
                                add('metronome', mnum)
                            elif d.tag == 'wedge' and d.get('type') in ('crescendo', 'diminuendo'):
                                add('hairpin-cresc' if d.get('type') == 'crescendo' else 'hairpin-dim', mnum)
                            elif d.tag == 'segno':
                                add('segno', mnum)
                            elif d.tag == 'coda':
                                add('coda', mnum)
                            elif d.tag == 'octave-shift' and d.get('type') in ('up', 'down'):
                                sz = d.get('size', '8')
                                add({('down', '8'): 'ottava-8va', ('up', '8'): 'ottava-8vb',
                                     ('down', '15'): 'ottava-15ma'}.get((d.get('type'), sz), 'x-ottava'), mnum)
                elif tag == 'barline':
                    st = el.findtext('bar-style')
                    rep = el.find('repeat')
                    if rep is not None:
                        add('repeat-start' if rep.get('direction') == 'forward' else 'repeat-end', mnum)
                    elif st == 'light-heavy':
                        add('barline-final', mnum)
                    elif st == 'light-light':
                        add('barline-double', mnum)
                elif tag == 'note':
                    _note(el, mnum, mi, add, clefs, open_ties, sys_idx, page_idx, multirest_left > 0,
                          verses_seen, lyr_state)
            if multirest_left > 0:
                multirest_left -= 1
        # close lyric melisma states
        for st in lyr_state.values():
            if st and st[1] > 1:
                add('lyrics-melisma', st[0])
        if len(verses_seen) > 1:
            add('lyrics-multi-verse', measures[0].get('number'), len(verses_seen))
    if n_pages_breaks:
        add('multi-page', '1')
    # chord heads after the first are not separate chords; ensure counters exist
    return dict(sorted(C.items())), {k: v for k, v in sorted(where.items())}


def _note(el, mnum, mi, add, clefs, open_ties, sys_idx, page_idx, in_multirest, verses_seen, lyr_state):
    is_chord = el.find('chord') is not None
    grace = el.find('grace')
    cue = el.find('cue') is not None
    rest = el.find('rest')
    typ = el.findtext('type')
    ndots = len(el.findall('dot'))
    voice = el.findtext('voice', '1')
    staff = int(el.findtext('staff', '1'))
    if rest is not None:
        if rest.get('measure') == 'yes':
            if not in_multirest:
                add('rest-whole-bar', mnum)
        else:
            add(f'rest-{TAG_TYPE.get(typ, typ)}', mnum)
            if ndots:
                add('rest-dotted', mnum)
            if ndots == 1:
                add('dot', mnum)
            elif ndots == 2:
                add('double-dot', mnum)
    else:
        p = el.find('pitch')
        step, octv = p.findtext('step'), int(p.findtext('octave'))
        alter = p.findtext('alter') or '0'
        if grace is not None:
            add('grace', mnum)
            if grace.get('slash') == 'yes':
                add('grace-slash', mnum)
        elif cue:
            add('cue-note', mnum)
        else:
            add(f'note-{TAG_TYPE.get(typ, typ)}', mnum)
            if ndots == 1:
                add('dot', mnum)
            elif ndots == 2:
                add('double-dot', mnum)
        bl = clefs.get(staff)
        if bl is not None:
            pos = _diat(step, octv) - bl
            if pos >= 10:
                add('ledger-above', mnum)
            elif pos <= -2:
                add('ledger-below', mnum)
        acc = el.find('accidental')
        if acc is not None:
            add(ACC_TAG.get(acc.text, f'x-acc-{acc.text}'), mnum)
            if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes':
                add('acc-courtesy', mnum)
        # ties
        key = (voice, staff, step, alter, octv)
        for t in el.findall('notations/tied'):
            if t.get('type') == 'stop' and key in open_ties:
                st_mi = open_ties.pop(key)
                if sys_idx[mi] != sys_idx[st_mi]:
                    add('tie-across-system', mnum)
                if page_idx[mi] != page_idx[st_mi]:
                    add('x-tie-across-page', mnum)
        for t in el.findall('notations/tied'):
            if t.get('type') == 'start':
                add('tie', mnum)
                open_ties[key] = mi
        # lyrics / melisma bookkeeping (attacks only)
        tied_stop = any(t.get('type') == 'stop' for t in el.findall('notations/tied'))
        if grace is None and not is_chord:
            lyr_nums = set()
            for ly in el.findall('lyric'):
                n = ly.get('number', '1')
                lyr_nums.add(n)
                verses_seen.add(n)
                add('lyrics', mnum)
                if ly.findtext('syllabic') in ('begin', 'middle'):
                    add('lyrics-hyphen', mnum)
                if ly.find('extend') is not None:
                    add('lyrics-extender', mnum)
            for (v, n), st in list(lyr_state.items()):
                if v != voice:
                    continue
                if n in lyr_nums:
                    if st and st[1] > 1:
                        add('lyrics-melisma', st[0])
                    lyr_state[(v, n)] = None
                elif st is not None and not tied_stop:
                    st[1] += 1
            for n in lyr_nums:
                lyr_state[(voice, n)] = [mnum, 1]
    if rest is not None and grace is None and not is_chord:
        # a rest ends every melisma of its voice
        for (v, n), st in list(lyr_state.items()):
            if v == voice and st is not None:
                if st[1] > 1:
                    add('lyrics-melisma', st[0])
                lyr_state[(v, n)] = None
    # notations shared by the whole chord: count on the first chord member only
    if not is_chord:
        nots = el.find('notations')
        if nots is not None:
            for x in nots:
                if x.tag == 'slur' and x.get('type') == 'start':
                    add('slur', mnum)
                elif x.tag == 'fermata':
                    add('fermata', mnum)
                elif x.tag == 'arpeggiate':
                    add('arpeggio', mnum)
                elif x.tag == 'tuplet' and x.get('type') == 'start':
                    num = x.findtext('tuplet-actual/tuplet-number') or el.findtext('time-modification/actual-notes')
                    if x.findtext('tuplet-actual/tuplet-number') is None and int(x.get('number', '1')) > 1:
                        raise ValueError('nested tuplet without tuplet-actual')
                    add('x-tuplet-4' if num == '4' else f'tuplet-{num}', mnum)
                    if int(x.get('number', '1')) > 1:
                        add('tuplet-nested', mnum)
                elif x.tag == 'articulations':
                    for a in x:
                        add(ART_TAG.get(a.tag, f'x-artic-{a.tag}'), mnum)
                elif x.tag == 'ornaments':
                    for o in x:
                        add({'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent',
                             'turn': 'turn', 'tremolo': 'tremolo'}.get(o.tag, f'x-orn-{o.tag}'), mnum)
                elif x.tag == 'technical':
                    for o in x:
                        if o.tag == 'fingering':
                            add('fingering', mnum)
        if rest is None and grace is None and not cue:
            beams = el.findall('beam')
            if any(b.get('number') == '1' and b.text == 'begin' for b in beams):
                add('beam', mnum)
            if not beams and typ in ('eighth', '16th', '32nd', '64th'):
                add('flag', mnum)


def count_chords(path):
    """number of chords (events with >= 2 noteheads) and their measures"""
    root = ET.parse(path).getroot()
    n, where = 0, []
    for part in root.findall('part'):
        for m in part.findall('measure'):
            notes = m.findall('note')
            for k, el in enumerate(notes):
                if el.find('chord') is None and k + 1 < len(notes) and notes[k + 1].find('chord') is not None:
                    n += 1
                    where.append(m.get('number'))
    return n, where


def count_all(path):
    c, w = count_truth(path)
    n, wh = count_chords(path)
    if n:
        c['chord'] = n
        w['chord'] = wh
    return dict(sorted(c.items())), dict(sorted(w.items()))
