"""Symbol counts read back from a truth.musicxml (independent of the score model).

Every count is "occurrences in the truth file" under the rules in COUNT_RULES (written into
meta.json).  The notes-family tags are cross-checked against the LilyPond engraving
(engraved_counts(), from the grob/event dump) by build.py.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

STEPS = 'CDEFGAB'
TYPE_TAG = {'breve': 'note-breve', 'whole': 'note-whole', 'half': 'note-half', 'quarter': 'note-quarter',
            'eighth': 'note-8th', '16th': 'note-16th', '32nd': 'note-32nd', '64th': 'note-64th'}
REST_TAG = {'breve': 'rest-breve', 'whole': 'rest-whole', 'half': 'rest-half', 'quarter': 'rest-quarter',
            'eighth': 'rest-8th', '16th': 'rest-16th', '32nd': 'rest-32nd', '64th': 'rest-64th'}
CLEF_TAG = {('G', '2', 0): 'clef-treble', ('F', '4', 0): 'clef-bass', ('C', '3', 0): 'clef-alto',
            ('C', '4', 0): 'clef-tenor', ('C', '1', 0): 'clef-soprano', ('G', '2', -1): 'clef-treble-8vb',
            ('G', '2', 1): 'clef-treble-8va', ('F', '4', -1): 'clef-bass-8vb'}
CLEF_MIDDLE = {('G', '2', 0): ('B', 4), ('F', '4', 0): ('D', 3), ('C', '3', 0): ('C', 4), ('C', '4', 0): ('A', 3),
               ('C', '1', 0): ('G', 4), ('G', '2', -1): ('B', 3), ('G', '2', 1): ('B', 5), ('F', '4', -1): ('D', 2)}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
ARTIC_TAG = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
             'strong-accent': 'marcato', 'breath-mark': 'breath'}
DYN_TAG = {'pp': 'dyn-pp', 'p': 'dyn-p', 'mp': 'dyn-mp', 'mf': 'dyn-mf', 'f': 'dyn-f', 'ff': 'dyn-ff',
           'sfz': 'dyn-sfz'}

TAXONOMY = set("""
note-breve note-whole note-half note-quarter note-8th note-16th note-32nd note-64th dot double-dot chord beam flag
stem-up stem-down ledger-above ledger-below grace grace-slash cue-note tremolo
rest-breve rest-whole rest-half rest-quarter rest-8th rest-16th rest-32nd rest-64th rest-dotted rest-whole-bar
rest-multibar
clef-treble clef-bass clef-alto clef-tenor clef-soprano clef-treble-8vb clef-treble-8va clef-bass-8vb clef-change
key-0 key-s1 key-s2 key-s3 key-s4 key-s5 key-s6 key-s7 key-f1 key-f2 key-f3 key-f4 key-f5 key-f6 key-f7 key-change
acc-sharp acc-flat acc-natural acc-double-sharp acc-double-flat acc-courtesy ottava-8va ottava-8vb ottava-15ma
time-2-4 time-3-4 time-4-4 time-2-2 time-3-2 time-6-8 time-9-8 time-12-8 time-5-4 time-5-8 time-7-8 time-common
time-cut time-change pickup tuplet-3 tuplet-2 tuplet-5 tuplet-6 tuplet-7 tuplet-nested tie tie-across-system
slur staccato staccatissimo accent tenuto marcato fermata trill mordent turn arpeggio breath dyn-pp dyn-p dyn-mp
dyn-mf dyn-f dyn-ff dyn-sfz hairpin-cresc hairpin-dim pedal fingering text-expression tempo-mark metronome
rehearsal-mark chord-symbol
barline-double barline-final repeat-start repeat-end volta-1 volta-2 segno coda dc ds fine system-break page-break
multi-page
lyrics lyrics-multi-verse lyrics-melisma lyrics-extender lyrics-hyphen lyrics-elision lyrics-non-ascii stanza-text
""".split())

COUNT_RULES = {
    '_scope': 'Counts are read from truth.musicxml. "Main notes" = <note> elements with <pitch> that are neither '
              '<grace/> nor <cue/>; note-family tags count main notes only, grace and cue notes are counted by '
              'grace / grace-slash / cue-note. Cross-checked against the LilyPond engraving (grob dump).',
    'note-<value>': 'main noteheads (<note> elements, chord tones included) with that <type>; two-note-tremolo '
                    'notes count with their printed type',
    'dot': 'main noteheads with exactly one <dot/> (every head of a dotted chord carries its own dot)',
    'double-dot': 'main noteheads with exactly two <dot/>',
    'chord': 'main chord events: a note without <chord/> followed by >= 1 <chord/> notes (sizes in counts_detail)',
    'beam': 'beam groups among main notes (= <beam number="1">begin</beam>); grace beam groups in counts_detail',
    'flag': 'main stems (chord = one stem) of value eighth or shorter without <beam> and not in a two-note tremolo',
    'stem-up / stem-down': 'main stems (chord = one stem) with <stem>up</stem> / <stem>down</stem>; whole notes and '
                           'breves have no stem',
    'ledger-above / ledger-below': 'main noteheads that need >= 1 ledger line above / below the 5-line staff '
                                   '(staff position from pitch and the clef in force); per-depth numbers in '
                                   'counts_detail (ledger-above-1 .. -5 = heads needing exactly n lines)',
    'grace': 'grace noteheads', 'grace-slash': 'grace noteheads with <grace slash="yes"/>',
    'cue-note': 'cue noteheads (<cue/>)',
    'tremolo': 'tremolo marks: single-note tremolos (per stem) + two-note tremolos (per pair, type="start")',
    'rest-<value>': 'rests (not measure rests) with that <type>', 'rest-dotted': 'dotted rests',
    'rest-whole-bar': '<rest measure="yes"/> (each bar of a multi-bar rest counts)',
    'rest-multibar': '<multiple-rest> blocks',
    'acc-*': 'printed <accidental> elements on any note (main, grace or cue)',
    'acc-courtesy': '<accidental cautionary="yes"> or parentheses="yes"',
    'clef-*': '<clef> elements (one per staff at the start)', 'clef-change': '<clef> elements after the first '
              'attributes of the part',
    'key-*': '<key> elements', 'time-*': '<time> elements (C / cut symbol counted as time-common / time-cut only)',
    'slur': '<slur type="start"> (includes the slur LilyPond draws for \\acciaccatura/\\appoggiatura)',
    'tie': '<tie type="start">', 'barline-final': 'light-heavy barlines without repeat',
    'system-break': '<print new-system="yes">', 'page-break': '<print new-page="yes">',
    'multi-page': '1 when the engraving has more than one page',
    'text-expression': '<words> directions that are not tempo marks (bold measure-start words)',
}


def _ln(tag):
    return tag.split('}')[-1]


def dnum(step, octv):
    return octv * 7 + STEPS.index(step)


def ledger_lines(pos):
    if pos >= 6:
        return (pos - 4) // 2
    if pos <= -6:
        return -((-pos - 4) // 2)
    return 0


def truth_counts(path, pages=1):
    root = ET.parse(path).getroot()
    c = Counter()
    detail = Counter()
    for part in root.findall('part'):
        clefs = {}            # staff -> clef key
        first_attrs = True
        prev_main = None      # (voice) -> last non-chord main note element info for chord detection
        chord_size = {}
        open_ties = 0
        for mi, meas in enumerate(part.findall('measure')):
            if meas.get('implicit') == 'yes' and mi == 0:
                c['pickup'] += 1
            for pr in meas.findall('print'):
                if pr.get('new-system') == 'yes':
                    c['system-break'] += 1
                if pr.get('new-page') == 'yes':
                    c['page-break'] += 1
            for el in meas:
                tag = _ln(el.tag)
                if tag == 'attributes':
                    for cl in el.findall('clef'):
                        key = (cl.findtext('sign'), cl.findtext('line'), int(cl.findtext('clef-octave-change') or 0))
                        num = cl.get('number', '1')
                        clefs[num] = key
                        if key in CLEF_TAG:
                            c[CLEF_TAG[key]] += 1
                        else:
                            c['x-clef-other'] += 1
                        if not first_attrs:
                            c['clef-change'] += 1
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths'))
                        c['key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')] += 1
                        if not first_attrs:
                            c['key-change'] += 1
                    for t in el.findall('time'):
                        sym = t.get('symbol')
                        b, bt = t.findtext('beats'), t.findtext('beat-type')
                        if sym == 'common':
                            c['time-common'] += 1
                        elif sym == 'cut':
                            c['time-cut'] += 1
                        else:
                            c[f'time-{b}-{bt}'] += 1
                        if not first_attrs:
                            c['time-change'] += 1
                    for ms in el.findall('measure-style'):
                        if ms.find('multiple-rest') is not None:
                            c['rest-multibar'] += 1
                    first_attrs = False
                elif tag == 'direction':
                    for dt in el.findall('direction-type'):
                        for x in dt:
                            n = _ln(x.tag)
                            if n == 'words':
                                if x.get('font-weight') == 'bold' and el.find('sound') is None:
                                    c['tempo-mark'] += 1
                                elif el.find('sound') is not None and el.find('sound').get('tempo'):
                                    c['tempo-mark'] += 1
                                else:
                                    c['text-expression'] += 1
                            elif n == 'rehearsal':
                                c['rehearsal-mark'] += 1
                            elif n == 'dynamics':
                                for d in x:
                                    c[DYN_TAG.get(_ln(d.tag), 'x-dyn-' + _ln(d.tag))] += 1
                            elif n == 'wedge':
                                if x.get('type') == 'crescendo':
                                    c['hairpin-cresc'] += 1
                                elif x.get('type') == 'diminuendo':
                                    c['hairpin-dim'] += 1
                            elif n == 'pedal' and x.get('type') == 'start':
                                c['pedal'] += 1
                            elif n == 'metronome':
                                c['metronome'] += 1
                            elif n == 'octave-shift' and x.get('type') in ('up', 'down'):
                                size = x.get('size', '8')
                                c['ottava-15ma' if size == '15' else ('ottava-8va' if x.get('type') == 'down'
                                                                       else 'ottava-8vb')] += 1
                            elif n == 'segno':
                                c['segno'] += 1
                            elif n == 'coda':
                                c['coda'] += 1
                elif tag == 'harmony':
                    c['chord-symbol'] += 1
                elif tag == 'barline':
                    st = el.findtext('bar-style')
                    rep = el.find('repeat')
                    if rep is not None:
                        c['repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'] += 1
                    elif st == 'light-heavy':
                        c['barline-final'] += 1
                    elif st == 'light-light':
                        c['barline-double'] += 1
                    end = el.find('ending')
                    if end is not None and end.get('type') == 'start':
                        for num in end.get('number', '').replace(' ', '').split(','):
                            if num in ('1', '2'):
                                c[f'volta-{num}'] += 1
                elif tag == 'note':
                    _count_note(el, c, detail, clefs, chord_size)
    if pages > 1:
        c['multi-page'] = 1
    # anything outside the canonical taxonomy is reported with the x- prefix
    c = Counter({(k if (k in TAXONOMY or k.startswith('x-')) else 'x-' + k): v for k, v in c.items()})
    return c, detail


def _count_note(el, c, detail, clefs, chord_size):
    grace = el.find('grace')
    cue = el.find('cue') is not None
    is_chord = el.find('chord') is not None
    rest = el.find('rest')
    typ = el.findtext('type')
    dots = len(el.findall('dot'))
    voice = el.findtext('voice', '1')
    staff = el.findtext('staff', '1')
    notations = el.find('notations')
    beams = el.findall('beam')
    acc = el.find('accidental')
    if acc is not None:
        c[ACC_TAG.get(acc.text, 'x-acc-' + str(acc.text))] += 1
        if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes':
            c['acc-courtesy'] += 1
    for t in el.findall('tie'):
        if t.get('type') == 'start':
            c['tie'] += 1
    if notations is not None:
        for sl in notations.findall('slur'):
            if sl.get('type') == 'start':
                c['slur'] += 1
        for tp in notations.findall('tuplet'):
            if tp.get('type') == 'start':
                tm = el.find('time-modification')
                an = tm.findtext('actual-notes') if tm is not None else '?'
                c[f'tuplet-{an}'] += 1
        for f in notations.findall('fermata'):
            c['fermata'] += 1
        for ar in notations.findall('articulations'):
            for a in ar:
                n = _ln(a.tag)
                c[ARTIC_TAG.get(n, 'x-artic-' + n)] += 1
        for orn in notations.findall('ornaments'):
            for o in orn:
                n = _ln(o.tag)
                if n == 'tremolo':
                    tt = o.get('type', 'single')
                    if tt in ('single', 'start'):
                        c['tremolo'] += 1
                        detail[f'tremolo-{"single" if tt == "single" else "two-note"}-{o.text}'] += 1
                elif n == 'trill-mark':
                    c['trill'] += 1
                elif n in ('mordent', 'inverted-mordent'):
                    c['mordent'] += 1
                elif n in ('turn', 'inverted-turn'):
                    c['turn'] += 1
        if notations.find('arpeggiate') is not None:
            c['arpeggio'] += 1
        tech = notations.find('technical')
        if tech is not None and tech.find('fingering') is not None:
            c['fingering'] += len(tech.findall('fingering'))
    if el.findall('lyric'):
        c['lyrics'] += len(el.findall('lyric'))
    if rest is not None:
        if rest.get('measure') == 'yes':
            c['rest-whole-bar'] += 1
        else:
            c[REST_TAG.get(typ, 'x-rest-' + str(typ))] += 1
            if dots:
                c['rest-dotted'] += 1
        return
    if grace is not None:
        c['grace'] += 1
        if grace.get('slash') == 'yes':
            c['grace-slash'] += 1
        if not is_chord and any(b.get('number') == '1' and b.text == 'begin' for b in beams):
            detail['grace-beam-groups'] += 1
        return
    if cue:
        c['cue-note'] += 1
        detail[f'cue-{typ}'] += 1
        return
    # main notes
    c[TYPE_TAG.get(typ, 'x-note-' + str(typ))] += 1
    if dots == 1:
        c['dot'] += 1
    elif dots == 2:
        c['double-dot'] += 1
    pitch = el.find('pitch')
    step, octv = pitch.findtext('step'), int(pitch.findtext('octave'))
    ck = clefs.get(staff, ('G', '2', 0))
    ms, mo = CLEF_MIDDLE[ck]
    pos = dnum(step, octv) - dnum(ms, mo)
    nl = ledger_lines(pos)
    if nl > 0:
        c['ledger-above'] += 1
        detail[f'ledger-above-{nl}'] += 1
    elif nl < 0:
        c['ledger-below'] += 1
        detail[f'ledger-below-{-nl}'] += 1
    if is_chord:
        return
    # new stem event (chord tones above were counted as heads only)
    two_note = False
    if notations is not None:
        for orn in notations.findall('ornaments'):
            for o in orn:
                if _ln(o.tag) == 'tremolo' and o.get('type') in ('start', 'stop'):
                    two_note = True
    st = el.findtext('stem')
    if st == 'up':
        c['stem-up'] += 1
    elif st == 'down':
        c['stem-down'] += 1
    if typ in ('eighth', '16th', '32nd', '64th') and not beams and not two_note:
        c['flag'] += 1
        detail[f'flag-{typ}'] += 1
    for b in beams:
        if b.get('number') == '1' and b.text == 'begin':
            c['beam'] += 1
    for b in beams:
        detail[f'beam-level-{b.get("number")}-{b.text.replace(" ", "-")}'] += 1


def finalize_chords(path):
    """chord-size histogram (separate pass, simple and explicit)"""
    root = ET.parse(path).getroot()
    sizes = Counter()
    for part in root.findall('part'):
        for meas in part.findall('measure'):
            cur = None
            for el in meas:
                if _ln(el.tag) != 'note':
                    continue
                if el.find('rest') is not None or el.find('grace') is not None or el.find('cue') is not None:
                    if cur and cur > 1:
                        sizes[cur] += 1
                    cur = None
                    continue
                if el.find('chord') is not None:
                    cur += 1
                else:
                    if cur and cur > 1:
                        sizes[cur] += 1
                    cur = 1
            if cur and cur > 1:
                sizes[cur] += 1
    return sizes


def all_counts(path, pages=1):
    c, detail = truth_counts(path, pages)
    sizes = finalize_chords(path)
    if sizes:
        c['chord'] = sum(sizes.values())
        for k, v in sorted(sizes.items()):
            detail[f'chord-{k}-notes'] = v
    return dict(sorted((k, v) for k, v in c.items() if v)), dict(sorted(detail.items()))
