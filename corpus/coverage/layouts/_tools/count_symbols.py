#!/usr/bin/env python3
"""Count coverage-taxonomy symbols in a MusicXML 4.0 partwise file.

usage:  python3 count_symbols.py file.musicxml [--json]

Python stdlib only, so the SAME counter can be run on the truth and on a converter's output and the
two count vectors compared tag by tag.  Rules (all objects with print-object="no" are ignored):

  note-<type>      note EVENTS (a chord counts once) by <type>, grace and cue notes excluded
  chord            note events with 2+ pitches
  dot / double-dot note events with 1 / 2 dots
  beam             beam groups (<beam number="1">begin</beam>)
  flag             note events of type eighth or shorter without any <beam>
  stem-up/-down    note events with <stem>up</stem> / <stem>down</stem>
  ledger-above/-below  note HEADS needing ledger lines (staff position from pitch + clef in force on
                   the note's <staff>, octave clefs included)
  grace / grace-slash / cue-note   grace events without / with slash; cue note events
  rest-<type>      rests (not measure rests) by type; rest-dotted = dotted rests;
  rest-whole-bar   <rest measure="yes"> not inside a multi-bar rest; rest-multibar = <multiple-rest>
  clef-<name>      <clef> elements per staff (initial + changes), clef-change = changes only
  key-s<n>/key-f<n>/key-0, key-change, time-<n>-<d>/time-common/time-cut, time-change:
                   statements in the FIRST part (score-wide), initial + changes
  pickup           first measure implicit="yes"
  acc-*            <accidental> by value (sharp, flat, natural, double-sharp, flat-flat);
                   acc-courtesy = cautionary="yes" or parentheses="yes"
  tie              <tied type="start"> (per note head); tie-across-system = ties whose stop is in a
                   measure that starts a new system/page
  tuplet-<n>       <tuplet type="start"> by actual-notes; tuplet-nested = a start inside another
  slur, staccato, staccatissimo, accent, tenuto, marcato(<strong-accent>), fermata, trill, mordent
                   (mordent + inverted-mordent), turn, tremolo, arpeggio (per chord), breath, fingering
  dyn-<x>          <dynamics> children; hairpin-cresc / hairpin-dim = <wedge> starts; pedal = <pedal>
                   start/change
  tempo-mark       directions with <words> AND (<metronome> or <sound tempo>); metronome = <metronome>
  text-expression  other <words> directions (not tempo, not D.C./D.S./Fine/Coda texts)
  rehearsal-mark, segno, coda, dc, ds, fine, chord-symbol (<harmony>)
  barline-double/-final, repeat-start/-end, volta-1/-2, system-break, page-break, multi-page:
                   FIRST part only (score-wide)
  lyrics           <lyric> syllables; lyrics-multi-verse = syllables of verse 2+; lyrics-hyphen =
                   syllabic begin|middle; lyrics-extender = <extend>; lyrics-melisma = syllables
                   followed by further attacks of the same voice before the next syllable of that verse;
                   lyrics-elision = <elision>; lyrics-non-ascii = syllables with non-ASCII text
  x-*              layout extras: x-parts, x-staves, x-measures, x-noteheads, x-multi-staff-part,
                   x-group-bracket/-brace/-square/-line, x-cross-staff-note (note heads on a staff
                   other than the voice's home staff), x-two-voice-staff-measure (part-staff measures
                   holding notes of 2+ voices), x-staff-size-reduced (<staff-size> < 100)
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from fractions import Fraction as F

STEPS = 'CDEFGAB'
TYPE_TAG = {'breve': 'breve', 'whole': 'whole', 'half': 'half', 'quarter': 'quarter', 'eighth': '8th',
            '16th': '16th', '32nd': '32nd', '64th': '64th'}
BEAMABLE = {'eighth', '16th', '32nd', '64th', '128th'}
SIGN_REF = {'G': 4 * 7 + 4, 'F': 3 * 7 + 3, 'C': 4 * 7 + 0}
CLEF_TAG = {('G', 2, 0): 'clef-treble', ('F', 4, 0): 'clef-bass', ('C', 3, 0): 'clef-alto',
            ('C', 4, 0): 'clef-tenor', ('C', 1, 0): 'clef-soprano', ('G', 2, -1): 'clef-treble-8vb',
            ('G', 2, 1): 'clef-treble-8va', ('F', 4, -1): 'clef-bass-8vb'}
ACC_TAG = {'sharp': 'acc-sharp', 'flat': 'acc-flat', 'natural': 'acc-natural', 'double-sharp': 'acc-double-sharp',
           'sharp-sharp': 'acc-double-sharp', 'flat-flat': 'acc-double-flat'}
ART_TAG = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
           'strong-accent': 'marcato', 'breath-mark': 'breath'}
ORN_TAG = {'trill-mark': 'trill', 'mordent': 'mordent', 'inverted-mordent': 'mordent', 'turn': 'turn',
           'inverted-turn': 'turn', 'delayed-turn': 'turn', 'tremolo': 'tremolo'}
STRUCT_WORDS = ('d.c.', 'd.s.', 'fine', 'coda', 'da capo', 'dal segno')


def clef_mid(sign, line, oc):
    return SIGN_REF[sign] + (3 - line) * 2 + 7 * oc


def count(path):
    root = ET.parse(path).getroot()
    c = Counter()
    parts = root.findall('part')
    c['x-parts'] = len(parts)
    for pg in root.iter('part-group'):
        if pg.get('type') == 'start':
            sym = (pg.findtext('group-symbol') or '').strip()
            if sym in ('bracket', 'brace', 'square', 'line'):
                c[f'x-group-{sym}'] += 1
    first = True
    for part in parts:
        _count_part(part, c, first)
        first = False
    if c.get('page-break'):
        c['multi-page'] = 1
    return {k: v for k, v in sorted(c.items()) if v}


def _count_part(part, c, first):
    measures = part.findall('measure')
    if first:
        c['x-measures'] = len(measures)
    divisions = 1
    staves = 1
    clef_seen = set()
    clefs = {}                     # staff -> list of (abs onset, (sign,line,oc))
    open_ties = {}                 # (voice, staff, pitch) -> measure index of start
    open_tuplets = defaultdict(int)
    sys_break_measures = set()
    lyric_slots = defaultdict(list)    # voice -> list of (is_attack, {verse: lyric})
    voice_staff = defaultdict(Counter)
    staff_voices_measure = defaultdict(set)
    heads_staff = []                   # (voice, staff) per note head for cross-staff
    t0 = F(0)
    pending_heads = []                 # (abs onset, staff, step, octave, cue/grace)
    for mi, m in enumerate(measures):
        if first and mi == 0 and m.get('implicit') == 'yes':
            c['pickup'] += 1
        pos = F(0)
        mlen = F(0)
        pr = m.find('print')
        if pr is not None and (pr.get('new-system') == 'yes' or pr.get('new-page') == 'yes'):
            sys_break_measures.add(mi)
            if first:
                c['page-break' if pr.get('new-page') == 'yes' else 'system-break'] += 1
        last_event = None
        for el in m:
            tag = el.tag
            if tag == 'attributes':
                d = el.findtext('divisions')
                if d:
                    divisions = int(d)
                st = el.findtext('staves')
                if st:
                    staves = int(st)
                    c['x-multi-staff-part'] += 1 if staves > 1 else 0
                for sd in el.findall('staff-details'):
                    sz = sd.findtext('staff-size')
                    if sz and float(sz) < 100:
                        c['x-staff-size-reduced'] += 1
                if first:
                    for k in el.findall('key'):
                        f = int(k.findtext('fifths') or 0)
                        c['key-0' if f == 0 else (f'key-s{f}' if f > 0 else f'key-f{-f}')] += 1
                        if mi > 0:
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
                        if mi > 0:
                            c['time-change'] += 1
                for cl in el.findall('clef'):
                    sn = int(cl.get('number') or 1)
                    sign = cl.findtext('sign')
                    line = int(cl.findtext('line') or 0)
                    oc = int(cl.findtext('clef-octave-change') or 0)
                    tagc = CLEF_TAG.get((sign, line, oc), f'x-clef-{sign}{line}{oc:+d}')
                    c[tagc] += 1
                    if sn in clef_seen:
                        c['clef-change'] += 1
                    clef_seen.add(sn)
                    clefs.setdefault(sn, []).append((t0 + pos, (sign, line, oc)))
                for mr in el.iter('multiple-rest'):
                    c['rest-multibar'] += 1
            elif tag == 'backup':
                pos -= F(int(el.findtext('duration'))) / divisions
            elif tag == 'forward':
                pos += F(int(el.findtext('duration'))) / divisions
                mlen = max(mlen, pos)
            elif tag == 'harmony':
                if el.get('print-object') != 'no':
                    c['chord-symbol'] += 1
            elif tag == 'direction':
                _count_direction(el, c)
            elif tag == 'barline' and first:
                bs = el.findtext('bar-style')
                rep = el.find('repeat')
                if rep is not None:
                    c['repeat-start' if rep.get('direction') == 'forward' else 'repeat-end'] += 1
                elif bs == 'light-light':
                    c['barline-double'] += 1
                elif bs == 'light-heavy':
                    c['barline-final'] += 1
                for en in el.findall('ending'):
                    if en.get('type') == 'start':
                        for n in (en.get('number') or '').replace(' ', '').split(','):
                            if n in ('1', '2'):
                                c[f'volta-{n}'] += 1
                            elif n:
                                c[f'x-volta-{n}'] += 1
                if el.find('segno') is not None:
                    c['segno'] += 1
                if el.find('coda') is not None:
                    c['coda'] += 1
            elif tag == 'note':
                dur = F(int(el.findtext('duration') or 0)) / divisions
                is_chord = el.find('chord') is not None
                if is_chord and last_event is not None:
                    onset = last_event[0]
                else:
                    onset = pos
                hidden = el.get('print-object') == 'no'
                voice = el.findtext('voice') or '1'
                sn = int(el.findtext('staff') or 1)
                if not hidden:
                    _count_note(el, c, is_chord, mi, voice, sn, open_ties, open_tuplets, sys_break_measures,
                                lyric_slots, t0 + onset, pending_heads)
                    if el.find('pitch') is not None and el.find('grace') is None:
                        voice_staff[voice][sn] += 1
                        heads_staff.append((voice, sn))
                        staff_voices_measure[(mi, sn)].add(voice)
                if not is_chord:
                    if el.find('grace') is None:
                        pos += dur
                    last_event = (onset, dur)
                mlen = max(mlen, pos)
        t0 += mlen
    # ledger lines (clef in force at the note's onset on its staff)
    for onset, sn, step, octv in pending_heads:
        cl = None
        for t, cd in clefs.get(sn, []):
            if t <= onset:
                cl = cd
        if cl is None or cl[0] not in SIGN_REF:
            continue
        pos = octv * 7 + STEPS.index(step) - clef_mid(*cl)
        if pos >= 6:
            c['ledger-above'] += 1
        elif pos <= -6:
            c['ledger-below'] += 1
    c['x-staves'] += staves
    home = {v: cnt.most_common(1)[0][0] for v, cnt in voice_staff.items()}
    c['x-cross-staff-note'] += sum(1 for v, s in heads_staff if s != home[v])
    c['x-two-voice-staff-measure'] += sum(1 for vs in staff_voices_measure.values() if len(vs) > 1)
    # melismas
    for voice, slots in lyric_slots.items():
        verses = {n for _, lys in slots for n in lys}
        for n in verses:
            last, mel = None, False
            for attack, lys in slots:
                if attack is None:         # rest
                    if last is not None and mel:
                        c['lyrics-melisma'] += 1
                    last, mel = None, False
                    continue
                if n in lys:
                    if last is not None and mel:
                        c['lyrics-melisma'] += 1
                    last, mel = True, False
                elif lys:
                    if last is not None and mel:
                        c['lyrics-melisma'] += 1
                    last, mel = None, False
                elif last is not None and attack:
                    mel = True
            if last is not None and mel:
                c['lyrics-melisma'] += 1


def _count_direction(el, c):
    dts = el.findall('direction-type')
    snd = el.find('sound')
    has_metro = any(dt.find('metronome') is not None for dt in dts)
    has_tempo = has_metro or (snd is not None and snd.get('tempo'))
    words = [w.text or '' for dt in dts for w in dt.findall('words')]
    if snd is not None:
        if snd.get('dacapo') == 'yes':
            c['dc'] += 1
        if snd.get('dalsegno'):
            c['ds'] += 1
        if snd.get('fine'):
            c['fine'] += 1
    for dt in dts:
        for ch in dt:
            t = ch.tag
            if t == 'dynamics':
                for d in ch:
                    c[f'dyn-{d.tag}'] += 1
            elif t == 'wedge':
                if ch.get('type') == 'crescendo':
                    c['hairpin-cresc'] += 1
                elif ch.get('type') == 'diminuendo':
                    c['hairpin-dim'] += 1
            elif t == 'pedal':
                if ch.get('type') in ('start', 'change'):
                    c['pedal'] += 1
            elif t == 'metronome':
                c['metronome'] += 1
            elif t == 'rehearsal':
                c['rehearsal-mark'] += 1
            elif t == 'segno':
                c['segno'] += 1
            elif t == 'coda':
                c['coda'] += 1
            elif t == 'octave-shift':
                if ch.get('type') in ('up', 'down'):
                    size = ch.get('size') or '8'
                    if size == '15':
                        c['ottava-15ma'] += 1
                    else:
                        c['ottava-8va' if ch.get('type') == 'down' else 'ottava-8vb'] += 1
    if words:
        if has_tempo:
            c['tempo-mark'] += 1
        elif not (snd is not None and (snd.get('dacapo') or snd.get('dalsegno') or snd.get('fine')
                                       or snd.get('tocoda'))) and \
                not any(w.strip().lower().startswith(STRUCT_WORDS) for w in words):
            c['text-expression'] += 1


def _count_note(el, c, is_chord, mi, voice, sn, open_ties, open_tuplets, sys_breaks, lyric_slots, onset,
                pending_heads):
    grace = el.find('grace')
    cue = el.find('cue') is not None
    rest = el.find('rest')
    typ = el.findtext('type')
    dots = len(el.findall('dot'))
    pitch = el.find('pitch')
    nots = el.find('notations')
    if rest is not None:
        if el.find('chord') is None:
            if rest.get('measure') == 'yes':
                c['rest-whole-bar'] += 1
            elif typ:
                c[f'rest-{TYPE_TAG.get(typ, typ)}'] += 1
            if dots:
                c['rest-dotted'] += 1
            if nots is not None and nots.find('fermata') is not None:
                c['fermata'] += 1
        return
    # ---- event-level (first note of a chord)
    if not is_chord:
        if grace is not None:
            c['grace-slash' if grace.get('slash') == 'yes' else 'grace'] += 1
        elif cue:
            c['cue-note'] += 1
        else:
            if typ:
                c[f'note-{TYPE_TAG.get(typ, typ)}'] += 1
            if dots == 1:
                c['dot'] += 1
            elif dots >= 2:
                c['double-dot'] += 1
            beams = el.findall('beam')
            if any(b.get('number', '1') == '1' and (b.text or '').strip() == 'begin' for b in beams):
                c['beam'] += 1
            if typ in BEAMABLE and not beams:
                c['flag'] += 1
            st = (el.findtext('stem') or '').strip()
            if st in ('up', 'down'):
                c[f'stem-{st}'] += 1
        # lyric slots for melisma detection (attack = not a tie continuation)
        if grace is None and not cue:
            tied_stop = any(t.get('type') == 'stop' for t in el.findall('tie'))
            lys = {l.get('number', '1'): l for l in el.findall('lyric')}
            lyric_slots[voice].append((not tied_stop, lys))
    if pitch is not None and grace is None and not cue:
        pending_heads.append((onset, sn, pitch.findtext('step'), int(pitch.findtext('octave'))))
    acc = el.find('accidental')
    if acc is not None and grace is None and not cue:
        c[ACC_TAG.get((acc.text or '').strip(), 'x-acc-' + (acc.text or '').strip())] += 1
        if acc.get('cautionary') == 'yes' or acc.get('parentheses') == 'yes':
            c['acc-courtesy'] += 1
    for ly in el.findall('lyric'):
        c['lyrics'] += 1
        if int(ly.get('number', '1') or 1) >= 2:
            c['lyrics-multi-verse'] += 1
        if (ly.findtext('syllabic') or '') in ('begin', 'middle'):
            c['lyrics-hyphen'] += 1
        if ly.find('extend') is not None:
            c['lyrics-extender'] += 1
        if ly.find('elision') is not None:
            c['lyrics-elision'] += 1
        if any(ord(ch) > 127 for t in ly.findall('text') for ch in (t.text or '')):
            c['lyrics-non-ascii'] += 1
    if nots is None:
        return
    if pitch is not None:
        pkey = (voice, sn, pitch.findtext('step'), pitch.findtext('alter') or '0', pitch.findtext('octave'))
    else:
        pkey = (voice, sn, '', '', '')
    for t in nots.findall('tied'):
        if t.get('type') == 'start':
            c['tie'] += 1
            open_ties[pkey] = mi
        elif t.get('type') == 'stop':
            s = open_ties.pop(pkey, None)
            if s is not None and s != mi and any(s < b <= mi for b in sys_breaks):
                c['tie-across-system'] += 1
    for s in nots.findall('slur'):
        if s.get('type') == 'start':
            c['slur'] += 1
    for tp in nots.findall('tuplet'):
        if tp.get('type') == 'start':
            tm = el.find('time-modification')
            an = tm.findtext('actual-notes') if tm is not None else '?'
            c[f'tuplet-{an}' if an in ('2', '3', '5', '6', '7') else f'x-tuplet-{an}'] += 1
            if open_tuplets[voice] > 0:
                c['tuplet-nested'] += 1
            open_tuplets[voice] += 1
        elif tp.get('type') == 'stop':
            open_tuplets[voice] = max(0, open_tuplets[voice] - 1)
    if not is_chord:
        if nots.find('fermata') is not None:
            c['fermata'] += 1
        for a in nots.findall('articulations'):
            for x in a:
                if x.tag in ART_TAG:
                    c[ART_TAG[x.tag]] += 1
        for o in nots.findall('ornaments'):
            for x in o:
                if x.tag in ORN_TAG:
                    c[ORN_TAG[x.tag]] += 1
        if nots.find('arpeggiate') is not None:
            c['arpeggio'] += 1
    for tch in nots.findall('technical'):
        c['fingering'] += len(tch.findall('fingering'))


def count_chords(path):
    """chord events: note events with 2+ pitches (grace/cue excluded)"""
    root = ET.parse(path).getroot()
    n = 0
    for part in root.findall('part'):
        for m in part.findall('measure'):
            prev_first = None
            for el in m:
                if el.tag != 'note' or el.get('print-object') == 'no':
                    continue
                if el.find('rest') is not None or el.find('grace') is not None or el.find('cue') is not None:
                    prev_first = None
                    continue
                if el.find('chord') is not None:
                    if prev_first is not None and not prev_first[1]:
                        n += 1
                        prev_first[1] = True
                else:
                    prev_first = [el, False]
    return n


def count_all(path):
    c = count(path)
    ch = count_chords(path)
    if ch:
        c['chord'] = ch
    return dict(sorted(c.items()))


if __name__ == '__main__':
    res = count_all(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(res, indent=1))
    else:
        for k, v in res.items():
            print(f'{k:28s} {v}')
