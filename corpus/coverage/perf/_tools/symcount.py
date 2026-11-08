#!/usr/bin/env python3
"""Count coverage-taxonomy symbols in a MusicXML file (truth or converter output).

usage: python symcount.py file.musicxml [--json]

The same rules are used for meta.json "counts" of every coverage/perf item, so running this on
the app's output gives directly comparable per-symbol numbers.  Counting rules:

  note-<type>      note heads (each chord tone) that are not grace / cue notes
  chord            note events with >= 2 heads;  dot / double-dot  note events with 1 / 2 dots
  beam             beams (<beam number="1">begin</beam>);  flag  unbeamed note events eighth or shorter
  stem-up/-down    note events with <stem>up/down</stem>
  ledger-above/-below  note heads (incl. grace, chord tones) outside the staff that need ledger
                   lines (staff position >= 6 / <= -6 from the clef and any octave-shift)
  grace / grace-slash  grace note events (all / slashed);  cue-note  cue heads;  tremolo  <tremolo>
  rest-<type>      rests (not whole-bar);  rest-whole-bar  <rest measure="yes"/>;  rest-dotted;
                   rest-multibar  <multiple-rest>
  clef-*           <clef> declarations per staff (initial + changes);  clef-change  changes only
  key-*, time-*    distinct (measure, value) declarations over all parts;  key-change / time-change
                   declarations after the first measure;  time-common / time-cut  symbol= forms
                   (then not counted as time-4-4 / time-2-2);  pickup  implicit first measure
  acc-*            <accidental> values (natural-sharp -> acc-sharp, natural-flat -> acc-flat);
                   acc-courtesy  accidentals with cautionary / parentheses / editorial
  ottava-8va/8vb/15ma  <octave-shift> starts (down 8 / up 8 / down 15)
  tuplet-N         tuplet starts by actual-notes;  tuplet-nested  starts inside an open tuplet
  tie              <tie type="start">;  tie-across-system  ties into a measure that starts a system/page
  slur, staccato, staccatissimo, accent, tenuto, marcato (strong-accent), fermata, trill
                   (trill-mark), mordent (mordent / inverted-mordent), turn, breath (breath-mark),
                   fingering   element counts (notation elements are written once per event)
  arpeggio         note events with <arpeggiate>
  dyn-*            <dynamics> children;  hairpin-cresc / -dim  <wedge> starts;  pedal  <pedal type="start">
  tempo-mark       directions with tempo words or <sound tempo>;  metronome  <metronome>
  text-expression  other <words>;  rehearsal-mark, chord-symbol (<harmony>), segno, coda, dc, ds, fine
  barline-*, repeat-*, volta-1/2, system-break, page-break   distinct per measure over all parts
  multi-page       1 if any page break
  lyrics           <lyric> syllables (all verses);  lyrics-multi-verse  number of verse lines if > 1;
                   lyrics-hyphen  begin/middle syllables;  lyrics-extender  <extend>;  lyrics-elision;
                   lyrics-melisma  syllables followed by >= 1 further attack before the next syllable;
                   lyrics-non-ascii  syllables with non-ASCII characters
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter

TYPE_TAG = {'breve': 'note-breve', 'whole': 'note-whole', 'half': 'note-half', 'quarter': 'note-quarter',
            'eighth': 'note-8th', '16th': 'note-16th', '32nd': 'note-32nd', '64th': 'note-64th'}
REST_TAG = {'breve': 'rest-breve', 'whole': 'rest-whole', 'half': 'rest-half', 'quarter': 'rest-quarter',
            'eighth': 'rest-8th', '16th': 'rest-16th', '32nd': 'rest-32nd', '64th': 'rest-64th'}
FLAGGED = {'eighth', '16th', '32nd', '64th', '128th'}
STEPS = 'CDEFGAB'
CLEF_TAG = {('G', 2, 0): 'clef-treble', ('F', 4, 0): 'clef-bass', ('C', 3, 0): 'clef-alto',
            ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano', ('G', 2, -1): 'clef-treble-8vb',
            ('G', 2, 1): 'clef-treble-8va', ('F', 4, -1): 'clef-bass-8vb'}
CLEF_REF = {'G': ('G', 4), 'F': ('F', 3), 'C': ('C', 4)}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat', 'natural-sharp': 'acc-sharp',
           'natural-flat': 'acc-flat'}
DYN = {'pp', 'p', 'mp', 'mf', 'f', 'ff', 'sfz'}


def dia(step, octave):
    return octave * 7 + STEPS.index(step)


def key_tag(fifths):
    f = int(fifths)
    return 'key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')


def count(path):
    root = ET.parse(path).getroot()
    c = Counter()
    keys, times, bars, prints = set(), set(), set(), {}
    lyric_numbers = set()
    parts = root.findall('part')
    for part in parts:
        clef = {}            # staff -> middle-line diatonic index
        shift = {}           # staff -> display octave offset
        open_ties = {}       # (voice, step, alter, octave) -> measure index of the start
        tuplet_open = Counter()
        voice_lyr = {}       # (voice, verse) -> state for melisma detection
        measures = part.findall('measure')
        for mi, m in enumerate(measures):
            pr = m.find('print')
            if pr is not None:
                if pr.get('new-page') == 'yes':
                    prints[mi] = 'page'
                elif pr.get('new-system') == 'yes':
                    prints.setdefault(mi, 'system')
            if mi == 0 and m.get('implicit') == 'yes':
                c['pickup'] = 1
            prev_event = None
            for el in m:
                if el.tag == 'attributes':
                    for k in el.findall('key'):
                        fx = k.findtext('fifths')
                        if fx is not None:
                            keys.add((mi, int(fx)))
                    for t in el.findall('time'):
                        beats, bt = t.findtext('beats'), t.findtext('beat-type')
                        times.add((mi, beats, bt, t.get('symbol')))
                    for cl in el.findall('clef'):
                        sign = cl.findtext('sign')
                        line = int(cl.findtext('line') or 0)
                        oc = int(cl.findtext('clef-octave-change') or 0)
                        st = int(cl.get('number') or 1)
                        tag = CLEF_TAG.get((sign, line, oc), f'x-clef-{sign}{line}{oc:+d}')
                        c[tag] += 1
                        if st in clef:
                            c['clef-change'] += 1
                        if sign in CLEF_REF:
                            rs, ro = CLEF_REF[sign]
                            clef[st] = dia(rs, ro) - (line - 3) * 2 + oc * 7
                    for ms in el.iter('multiple-rest'):
                        c['rest-multibar'] += 1
                elif el.tag == 'barline':
                    style = el.findtext('bar-style')
                    rep = el.find('repeat')
                    loc = el.get('location', 'right')
                    if rep is not None:
                        bars.add((mi, loc, 'repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'))
                    elif style == 'light-light':
                        bars.add((mi, loc, 'barline-double'))
                    elif style == 'light-heavy':
                        bars.add((mi, loc, 'barline-final'))
                    for en in el.findall('ending'):
                        if en.get('type') == 'start':
                            for num in (en.get('number') or '').replace(' ', '').split(','):
                                bars.add((mi, 'ending', f'volta-{num}'))
                elif el.tag == 'direction':
                    st = int(el.findtext('staff') or 1)
                    snd = el.find('sound')
                    has_metro = el.find('.//metronome') is not None
                    tempo = has_metro or (snd is not None and snd.get('tempo'))
                    for dt in el.findall('direction-type'):
                        for x in dt:
                            if x.tag == 'dynamics':
                                for d in x:
                                    c[('dyn-' + d.tag) if d.tag in DYN else ('x-dyn-' + d.tag)] += 1
                            elif x.tag == 'wedge':
                                if x.get('type') == 'crescendo':
                                    c['hairpin-cresc'] += 1
                                elif x.get('type') == 'diminuendo':
                                    c['hairpin-dim'] += 1
                            elif x.tag == 'pedal':
                                if x.get('type') == 'start':
                                    c['pedal'] += 1
                            elif x.tag == 'octave-shift':
                                ty, sz = x.get('type'), x.get('size', '8')
                                if ty in ('up', 'down'):
                                    c[{('down', '8'): 'ottava-8va', ('up', '8'): 'ottava-8vb',
                                       ('down', '15'): 'ottava-15ma', ('up', '15'): 'x-ottava-15mb'}
                                      .get((ty, sz), 'x-ottava')] += 1
                                    o = (int(sz) - 1) // 7
                                    shift[st] = -o if ty == 'down' else o
                                else:
                                    shift[st] = 0
                            elif x.tag == 'metronome':
                                c['metronome'] += 1
                            elif x.tag == 'words':
                                if snd is not None and snd.get('dacapo') == 'yes':
                                    c['dc'] += 1
                                elif snd is not None and snd.get('dalsegno'):
                                    c['ds'] += 1
                                elif snd is not None and snd.get('fine'):
                                    c['fine'] += 1
                                elif tempo:
                                    c['tempo-mark'] += 1
                                elif (x.text or '').strip():
                                    c['text-expression'] += 1
                            elif x.tag == 'rehearsal':
                                c['rehearsal-mark'] += 1
                            elif x.tag == 'segno':
                                c['segno'] += 1
                            elif x.tag == 'coda':
                                c['coda'] += 1
                    if has_metro and not any(x.tag == 'words' for dt in el.findall('direction-type') for x in dt):
                        c['tempo-mark'] += 1
                elif el.tag == 'harmony':
                    c['chord-symbol'] += 1
                elif el.tag == 'note':
                    _note(el, c, clef, shift, open_ties, tuplet_open, voice_lyr, lyric_numbers, mi, prints)
    for mi, fx in keys:
        c[key_tag(fx)] += 1
        if mi > 0:
            c['key-change'] += 1
    for mi, beats, bt, sym in times:
        if sym == 'common':
            c['time-common'] += 1
        elif sym == 'cut':
            c['time-cut'] += 1
        else:
            c[f'time-{beats}-{bt}'] += 1
        if mi > 0:
            c['time-change'] += 1
    for _mi, _loc, tag in bars:
        c[tag] += 1
    for mi, kind in prints.items():
        c['page-break' if kind == 'page' else 'system-break'] += 1
    if any(k == 'page' for k in prints.values()):
        c['multi-page'] = 1
    if len(lyric_numbers) > 1:
        c['lyrics-multi-verse'] = len(lyric_numbers)
    # melismas: finalise open syllables
    return {k: v for k, v in sorted(c.items()) if v}


def _note(n, c, clef, shift, open_ties, tuplet_open, voice_lyr, lyric_numbers, mi, prints):
    is_chord = n.find('chord') is not None
    grace = n.find('grace')
    cue = n.find('cue') is not None
    rest = n.find('rest')
    voice = n.findtext('voice') or '1'
    st = int(n.findtext('staff') or 1)
    typ = n.findtext('type')
    ndots = len(n.findall('dot'))
    if rest is not None:
        if rest.get('measure') == 'yes' or typ is None:
            c['rest-whole-bar'] += 1
        else:
            c[REST_TAG.get(typ, 'x-rest-' + typ)] += 1
        if ndots:
            c['rest-dotted'] += 1
        _lyric_rest(voice, voice_lyr)
    else:
        pitch = n.find('pitch')
        if pitch is not None:
            step, octv = pitch.findtext('step'), int(pitch.findtext('octave'))
            alter = float(pitch.findtext('alter') or 0)
            if st in clef:
                pos = dia(step, octv + shift.get(st, 0)) - clef[st]
                if pos >= 6:
                    c['ledger-above'] += 1
                elif pos <= -6:
                    c['ledger-below'] += 1
            for t in n.findall('tie'):
                k = (voice, step, alter, octv)
                if t.get('type') == 'start':
                    c['tie'] += 1
                    open_ties[k] = mi
                elif t.get('type') == 'stop' and k in open_ties:
                    m0 = open_ties.pop(k)
                    if m0 < mi and any(j in prints for j in range(m0 + 1, mi + 1)):
                        c['tie-across-system'] += 1
        if cue:
            c['cue-note'] += 1
        elif grace is None and typ:
            c[TYPE_TAG.get(typ, 'x-note-' + typ)] += 1
        if not is_chord:
            c['_events'] += 0
            if grace is not None:
                c['grace'] += 1
                if grace.get('slash') == 'yes':
                    c['grace-slash'] += 1
            if ndots == 1:
                c['dot'] += 1
            elif ndots == 2:
                c['double-dot'] += 1
            stem = n.findtext('stem')
            if stem == 'up':
                c['stem-up'] += 1
            elif stem == 'down':
                c['stem-down'] += 1
            beams = n.findall('beam')
            if any(b.get('number', '1') == '1' and (b.text or '').strip() == 'begin' for b in beams):
                c['beam'] += 1
            if typ in FLAGGED and not beams:
                n.set('_flag_candidate', '1')
                c['flag'] += 1
            _lyric_note(n, voice, voice_lyr, lyric_numbers, c)
        else:
            c['_chord_tones'] += 0
    acc = n.find('accidental')
    if acc is not None and (acc.text or '').strip():
        c[ACC_TAG.get(acc.text.strip(), 'x-acc-' + acc.text.strip())] += 1
        if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes' or acc.get('editorial') == 'yes' \
                or acc.get('bracket') == 'yes':
            c['acc-courtesy'] += 1
    for nots in n.findall('notations'):
        for x in nots:
            if x.tag == 'slur' and x.get('type') == 'start':
                c['slur'] += 1
            elif x.tag == 'tuplet' and x.get('type') == 'start':
                tm = n.find('time-modification')
                an = tm.findtext('actual-notes') if tm is not None else '?'
                if tuplet_open[voice] > 0:
                    c['tuplet-nested'] += 1
                tuplet_open[voice] += 1
                c[f'tuplet-{an}'] += 1
            elif x.tag == 'tuplet' and x.get('type') == 'stop':
                tuplet_open[voice] = max(0, tuplet_open[voice] - 1)
            elif x.tag == 'fermata':
                c['fermata'] += 1
            elif x.tag == 'arpeggiate' and not is_chord:
                c['arpeggio'] += 1
            elif x.tag == 'articulations':
                for a in x:
                    tag = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent',
                           'tenuto': 'tenuto', 'strong-accent': 'marcato', 'breath-mark': 'breath'}.get(a.tag)
                    c[tag or 'x-artic-' + a.tag] += 1
            elif x.tag == 'ornaments':
                for o in x:
                    tag = {'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent',
                           'turn': 'turn', 'inverted-turn': 'turn', 'delayed-turn': 'turn',
                           'tremolo': 'tremolo'}.get(o.tag)
                    c[tag or 'x-orn-' + o.tag] += 1
            elif x.tag == 'technical':
                for t in x:
                    if t.tag == 'fingering':
                        c['fingering'] += 1
            elif x.tag == 'dynamics':
                for d in x:
                    c[('dyn-' + d.tag) if d.tag in DYN else ('x-dyn-' + d.tag)] += 1


def _lyric_rest(voice, voice_lyr):
    for (v, num), stt in list(voice_lyr.items()):
        if v == voice:
            stt['open'] = False


def _lyric_note(n, voice, voice_lyr, lyric_numbers, c):
    tie_stop = any(t.get('type') == 'stop' for t in n.findall('tie'))
    lyr = {}
    for l in n.findall('lyric'):
        num = l.get('number', '1')
        lyric_numbers.add(num)
        txt = ''.join(x.text or '' for x in l.findall('text'))
        lyr[num] = l
        c['lyrics'] += 1
        if (l.findtext('syllabic') or 'single') in ('begin', 'middle'):
            c['lyrics-hyphen'] += 1
        if l.find('extend') is not None:
            c['lyrics-extender'] += 1
        c['lyrics-elision'] += len(l.findall('elision'))
        if any(ord(ch) > 127 for ch in txt):
            c['lyrics-non-ascii'] += 1
    if n.find('grace') is not None:
        return
    # melisma detection per (voice, verse)
    for (v, num), stt in voice_lyr.items():
        if v != voice or num in lyr:
            continue
        if stt.get('open') and not tie_stop and not stt.get('counted'):
            c['lyrics-melisma'] += 1
            stt['counted'] = True
    for num in lyr:
        voice_lyr[(voice, num)] = {'open': True, 'counted': False}


def main():
    res = count(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(res, indent=1))
    else:
        for k, v in res.items():
            print(f'{k:24s} {v}')


if __name__ == '__main__':
    main()
