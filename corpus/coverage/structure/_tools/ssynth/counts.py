"""Coverage-taxonomy symbol counts read from truth.musicxml.

Counting rules (also written to meta.json 'count_rules'):
  * score-wide tags are counted ONCE per score position even when MusicXML repeats them in every
    part: barline-double, barline-final, repeat-start, repeat-end, volta-N, segno, coda, dc, ds,
    fine, x-to-coda, system-break, page-break, multi-page, rehearsal-mark, tempo-mark, metronome,
    key-*, key-change, time-*, time-change, pickup;
  * every other tag is counted per occurrence in every part (also listed per part in
    'counts_by_part'):
      note-<type>  note events (a chord counts once, as its stem/duration), no grace / cue notes
      chord        note events with two or more noteheads
      dot / double-dot  dotted / double-dotted note events;  rest-dotted  dotted rests
      beam         beam groups (<beam number="1">begin);  flag  unbeamed note events of 8th or shorter
      stem-up / stem-down  note events with that <stem>
      ledger-above / ledger-below  noteheads on or beyond the first ledger line (per clef in force)
      rest-<type>  rests that are not whole-bar rests;  rest-whole-bar  <rest measure="yes"/>
      clef-*       <clef> elements (initial and changes);  clef-change  clefs after the first measure
      acc-*        printed <accidental> elements;  acc-courtesy  cautionary / parenthesised ones
      tie          <tie type="start"> per notehead;  tie-across-system  ties whose end note starts a
                   new system or page
      slur, staccato, accent, tenuto, ..., fermata   per element;  dyn-*  per dynamic;  hairpin-*  per
      wedge start;  pedal  per pedal start;  text-expression  words that are not tempo / jump text
      lyrics  <lyric> syllables;  lyrics-hyphen  begin/middle syllables;  lyrics-extender  <extend>
      lyrics-multi-verse  syllables of verse 2 and higher
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter

STEPS = 'CDEFGAB'
TYPE_TAG = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
CLEF_TAG = {('G', 2, 0): 'clef-treble', ('F', 4, 0): 'clef-bass', ('C', 3, 0): 'clef-alto',
            ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano', ('G', 2, -1): 'clef-treble-8vb',
            ('G', 2, 1): 'clef-treble-8va', ('F', 4, -1): 'clef-bass-8vb'}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
ARTIC_TAG = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
             'strong-accent': 'marcato', 'breath-mark': 'breath'}
ORN_TAG = {'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent', 'turn': 'turn',
           'inverted-turn': 'turn', 'tremolo': 'tremolo'}
TEMPO_WORDS = re.compile(r'^(a tempo|tempo|allegr|andant|moderat|adagio|lento|largo|presto|vivace|grave|'
                         r'maestoso|tranquill|più|piu|meno|poco|con moto|tempo di|larghetto|risoluto|'
                         r'animato|scherzando|grazioso|cantabile|marziale|alla )', re.I)


def middle(sign, line, oc):
    """diatonic index of the middle staff line for a clef"""
    if sign == 'G':
        ref = 4 * 7 + STEPS.index('G') + (3 - line) * 2
    elif sign == 'F':
        ref = 3 * 7 + STEPS.index('F') + (3 - line) * 2
    elif sign == 'C':
        ref = 4 * 7 + STEPS.index('C') + (3 - line) * 2
    else:
        return None
    return ref + 7 * oc


def count_truth(path, pages):
    root = ET.parse(path).getroot()
    names = {sp.get('id'): sp.findtext('part-name') for sp in root.find('part-list').findall('score-part')}
    per_part = {}
    score_wide = {}          # (tag, position key) -> 1
    for part in root.findall('part'):
        pid = part.get('id')
        C = Counter()
        clef_mid = {}
        open_ties = {}
        brk_measures = set()
        for mi, meas in enumerate(part.findall('measure')):
            pr = meas.find('print')
            if pr is not None and pr.get('new-system') == 'yes':
                score_wide[('system-break', mi)] = 1
                brk_measures.add(mi)
            if pr is not None and pr.get('new-page') == 'yes':
                score_wide[('page-break', mi)] = 1
                brk_measures.add(mi)
            if mi == 0 and meas.get('implicit') == 'yes':
                score_wide[('pickup', 0)] = 1
            prev_note = None
            for el in meas:
                tag = el.tag
                if tag == 'attributes':
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths'))
                        kt = 'key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')
                        score_wide[(kt, mi)] = 1
                        if mi > 0:
                            score_wide[('key-change', mi)] = 1
                    for t in el.findall('time'):
                        sym = t.get('symbol')
                        b, bt = t.findtext('beats'), t.findtext('beat-type')
                        tt = {'common': 'time-common', 'cut': 'time-cut'}.get(sym, f'time-{b}-{bt}')
                        score_wide[(tt, mi)] = 1
                        if mi > 0:
                            score_wide[('time-change', mi)] = 1
                    for c in el.findall('clef'):
                        sign, line = c.findtext('sign'), int(c.findtext('line') or 0)
                        oc = int(c.findtext('clef-octave-change') or 0)
                        C[CLEF_TAG.get((sign, line, oc), f'x-clef-{sign}{line}{oc:+d}')] += 1
                        if mi > 0:
                            C['clef-change'] += 1
                        clef_mid[int(c.get('number', '1'))] = middle(sign, line, oc)
                elif tag == 'barline':
                    st = el.findtext('bar-style')
                    rep = el.find('repeat')
                    loc = el.get('location', 'right')
                    if rep is not None:
                        d = rep.get('direction')
                        score_wide[('repeat-start' if d == 'forward' else 'repeat-end', mi, loc)] = 1
                    elif st == 'light-light':
                        score_wide[('barline-double', mi, loc)] = 1
                    elif st == 'light-heavy':
                        score_wide[('barline-final', mi, loc)] = 1
                    for en in el.findall('ending'):
                        if en.get('type') == 'start':
                            for num in re.split(r'[,\s]+', en.get('number').strip()):
                                tg = f'volta-{num}' if num in ('1', '2') else f'x-volta-{num}'
                                score_wide[(tg, mi)] = 1
                elif tag == 'direction':
                    has_voice = el.find('voice') is not None
                    dts = [x for dt in el.findall('direction-type') for x in dt]
                    has_metro = any(x.tag == 'metronome' for x in dts)
                    snd = el.find('sound')
                    for x in dts:
                        if x.tag == 'segno':
                            score_wide[('segno', mi)] = 1
                        elif x.tag == 'coda':
                            score_wide[('coda', mi, len(score_wide))] = 1 if not has_voice else 1
                        elif x.tag == 'rehearsal':
                            score_wide[('rehearsal-mark', mi, x.text)] = 1
                        elif x.tag == 'metronome':
                            score_wide[('metronome', mi)] = 1
                        elif x.tag == 'dynamics':
                            for d in x:
                                C['dyn-' + d.tag if d.tag in ('pp', 'p', 'mp', 'mf', 'f', 'ff', 'sfz')
                                  else 'x-dyn-' + d.tag] += 1
                        elif x.tag == 'wedge':
                            if x.get('type') == 'crescendo':
                                C['hairpin-cresc'] += 1
                            elif x.get('type') == 'diminuendo':
                                C['hairpin-dim'] += 1
                        elif x.tag == 'pedal':
                            if x.get('type') == 'start':
                                C['pedal'] += 1
                        elif x.tag == 'octave-shift':
                            if x.get('type') in ('up', 'down'):
                                size = x.get('size', '8')
                                C['ottava-15ma' if size == '15' else ('ottava-8va' if x.get('type') == 'down'
                                                                      else 'ottava-8vb')] += 1
                        elif x.tag == 'words':
                            txt = (x.text or '').strip()
                            if re.match(r'^(D\.\s*C\.|Da Capo)', txt):
                                score_wide[('dc', mi)] = 1
                            elif re.match(r'^(D\.\s*S\.|Dal Segno)', txt):
                                score_wide[('ds', mi)] = 1
                            elif txt == 'Fine':
                                score_wide[('fine', mi)] = 1
                            elif re.match(r'^To Coda', txt):
                                score_wide[('x-to-coda', mi)] = 1
                            elif not has_voice and (has_metro or (snd is not None and snd.get('tempo'))
                                                    or TEMPO_WORDS.match(txt)):
                                score_wide[('tempo-mark', mi, txt)] = 1
                            else:
                                C['text-expression'] += 1
                elif tag == 'note':
                    chord = el.find('chord') is not None
                    grace = el.find('grace') is not None
                    cue = el.find('cue') is not None
                    rest = el.find('rest')
                    typ = el.findtext('type')
                    dots = len(el.findall('dot'))
                    staff = int(el.findtext('staff') or 1)
                    voice = el.findtext('voice') or '1'
                    if rest is not None:
                        if rest.get('measure') == 'yes':
                            C['rest-whole-bar'] += 1
                        else:
                            C['rest-' + TYPE_TAG[typ]] += 1
                        if dots:
                            C['rest-dotted'] += 1
                        prev_note = None
                    else:
                        p = el.find('pitch')
                        step, octv = p.findtext('step'), int(p.findtext('octave'))
                        mid = clef_mid.get(staff)
                        if mid is not None:
                            pos = octv * 7 + STEPS.index(step) - mid
                            if pos >= 6:
                                C['ledger-above'] += 1
                            elif pos <= -6:
                                C['ledger-below'] += 1
                        if not chord:
                            if grace:
                                C['grace'] += 1
                                if el.find('grace').get('slash') == 'yes':
                                    C['grace-slash'] += 1
                            elif cue:
                                C['cue-note'] += 1
                            else:
                                C['note-' + TYPE_TAG[typ]] += 1
                                if dots == 1:
                                    C['dot'] += 1
                                elif dots >= 2:
                                    C['double-dot'] += 1
                                beams = el.findall('beam')
                                if any(b.get('number') == '1' and b.text == 'begin' for b in beams):
                                    C['beam'] += 1
                                if not beams and typ in ('eighth', '16th', '32nd', '64th'):
                                    C['flag'] += 1
                                stem = el.findtext('stem')
                                if stem == 'up':
                                    C['stem-up'] += 1
                                elif stem == 'down':
                                    C['stem-down'] += 1
                            prev_note = el
                        elif prev_note is not None and prev_note.get('_chord') != '1':
                            C['chord'] += 1
                            prev_note.set('_chord', '1')
                        acc = el.find('accidental')
                        if acc is not None:
                            C[ACC_TAG.get(acc.text, 'x-acc-' + (acc.text or ''))] += 1
                            if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes' \
                                    or acc.get('editorial') == 'yes':
                                C['acc-courtesy'] += 1
                        pk = (voice, step, int(float(p.findtext('alter') or 0)), octv)
                        for ti in el.findall('tie'):
                            if ti.get('type') == 'stop' and pk in open_ties:
                                s = open_ties.pop(pk)
                                if any(s < b <= mi for b in brk_measures):
                                    C['tie-across-system'] += 1
                        for ti in el.findall('tie'):
                            if ti.get('type') == 'start':
                                C['tie'] += 1
                                open_ties[pk] = mi
                    nots = el.find('notations')
                    if nots is not None and not chord:
                        for s in nots.findall('slur'):
                            if s.get('type') == 'start':
                                C['slur'] += 1
                        if nots.find('fermata') is not None:
                            C['fermata'] += 1
                        if nots.find('arpeggiate') is not None:
                            C['arpeggio'] += 1
                        for grp in nots.findall('articulations') + nots.findall('ornaments') + \
                                nots.findall('technical'):
                            for a in grp:
                                if a.tag in ARTIC_TAG:
                                    C[ARTIC_TAG[a.tag]] += 1
                                elif a.tag in ORN_TAG:
                                    C[ORN_TAG[a.tag]] += 1
                                elif a.tag == 'fingering':
                                    C['fingering'] += 1
                                elif a.tag not in ('accidental-mark',):
                                    C['x-' + a.tag] += 1
                        tup = nots.find('tuplet')
                        if tup is not None and tup.get('type') == 'start':
                            tm = el.find('time-modification')
                            C[f'tuplet-{tm.findtext("actual-notes")}'] += 1
                    for ly in el.findall('lyric'):
                        C['lyrics'] += 1
                        if int(ly.get('number', '1')) >= 2:
                            C['lyrics-multi-verse'] += 1
                        if ly.findtext('syllabic') in ('begin', 'middle'):
                            C['lyrics-hyphen'] += 1
                        if ly.find('extend') is not None:
                            C['lyrics-extender'] += 1
                        if ly.find('elision') is not None:
                            C['lyrics-elision'] += 1
                        if any(ord(ch) > 127 for ch in (ly.findtext('text') or '')):
                            C['lyrics-non-ascii'] += 1
                elif tag == 'harmony':
                    C['chord-symbol'] += 1
        per_part[names[pid]] = C
    total = Counter()
    for C in per_part.values():
        total.update(C)
    sw = Counter(k[0] for k in score_wide)
    total.update(sw)
    if pages > 1:
        total['multi-page'] = pages
    total = {k: v for k, v in sorted(total.items()) if v}
    by_part = {n: {k: v for k, v in sorted(C.items()) if v} for n, C in per_part.items()}
    return total, by_part
