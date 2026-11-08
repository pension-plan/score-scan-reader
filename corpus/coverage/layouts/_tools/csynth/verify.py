"""Engraving-vs-truth verification from the LilyPond grob log (cvlog.ly).

expected_from_model() derives, from the prepared score model (the same model the truth is written
from), what must be printed; parse_log() reads LilyPond's own grob log; compare() returns a report
with every category, and 'ok' = all categories identical.
"""
from __future__ import annotations

import re
from collections import Counter
from fractions import Fraction as F

from .model import STEP_PC, midi

DURLOG = {'breve': -1, 'whole': 0, 'half': 1, 'quarter': 2, 'eighth': 3, '16th': 4, '32nd': 5, '64th': 6}
NBEAMS = {'eighth', '16th', '32nd', '64th'}
GLYPH = {'sharp': 'accidentals.sharp', 'flat': 'accidentals.flat', 'natural': 'accidentals.natural',
         'double-sharp': 'accidentals.doublesharp', 'flat-flat': 'accidentals.flatflat'}
SCRIPT = {'staccato': 'staccato', 'accent': 'sforzato', 'tenuto': 'tenuto', 'strong-accent': 'marcato',
          'staccatissimo': 'staccatissimo'}
ORN = {'trill-mark': 'trill', 'mordent': 'mordent', 'turn': 'turn'}
SCRIPT_NAMES = ['staccatissimo', 'staccato', 'sforzato', 'tenuto', 'marcato', 'fermata', 'trill', 'mordent',
                'turn', 'prall']
DELIM = {'PianoStaff': 'SystemStartBrace', 'GrandStaff': 'SystemStartBrace', 'ChoirStaff': 'SystemStartBracket',
         'StaffGroup': 'SystemStartBracket'}


def parse_log(path):
    rows = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) >= 5:
                rows.append(p)
    return rows


def _when(x):
    try:
        return F(x) * 4
    except Exception:
        return None


def expected_from_model(score, layout, opts, prep):
    from .notation import iter_groups, iter_staves, segments_of, system_starts
    offs = score.measure_offsets()
    E = {k: Counter() for k in ('heads', 'stems', 'acc', 'rests', 'scripts', 'dyn', 'hairpin', 'lyric',
                                'chordname', 'fingering')}
    n = Counter()
    for p in score.parts:
        for v in p.voices:
            prev_tie = None
            for i, m in enumerate(p.measures):
                for ev in m.get(v.key, []):
                    if ev.kind == 'rest':
                        if ev.hidden:
                            continue
                        if ev.measure_rest:
                            n['rests'] += 1
                        else:
                            n['rests'] += 1
                            E['rests'][(DURLOG[ev.dtype], ev.dots)] += 1
                        if ev.fermata:
                            E['scripts']['fermata'] += 1
                        n['textscript'] += len(ev.words)
                        continue
                    if ev.kind != 'note':
                        continue
                    for pp in ev.pitches:
                        E['heads'][(min(DURLOG[ev.dtype], 2), ev.dots)] += 1
                    if ev.stem_dir:
                        E['stems'][(1 if ev.stem_dir == 'up' else -1, DURLOG[ev.dtype])] += 1
                    if ev.dtype in NBEAMS and not ev.beams and not ev.cue:
                        n['flags'] += 1
                    if ev.dtype in NBEAMS and not ev.beams and ev.cue:
                        n['flags'] += 1
                    for a in ev.artic:
                        E['scripts'][SCRIPT[a]] += 1
                    for o in ev.ornaments:
                        E['scripts'][ORN[o]] += 1
                    if ev.fermata:
                        E['scripts']['fermata'] += 1
                    n['slurs'] += ev.slur_start
                    n['ties'] += len(ev.tie_start)
                    for d in ev.dynamics:
                        E['dyn'][d] += 1
                    for w in ev.wedge:
                        if w != 'stop':
                            E['hairpin'][1 if w == 'crescendo' else -1] += 1
                    n['textscript'] += len(ev.words)
                    if ev.tuplet and ev.tuplet_start:
                        n['tuplets'] += 1
                    n['pedal'] += len(ev.pedal)
                    n['breath'] += 1 if ev.breath else 0
                    n['arpeggio'] += 1 if (ev.arpeggio and len(ev.pitches) > 1) else 0
                    for fg in ev.fingering:
                        if fg:
                            E['fingering'][str(fg)] += 1
                    for vn, ly in ev.lyrics.items():
                        E['lyric'][ly.text] += 1
                        if ly.syllabic in ('begin', 'middle'):
                            n['hyphens'] += 1
                        if ly.extend:
                            n['extenders'] += 1
    for pid_, vk, i, g in prep['beam_groups']:
        n['beams'] += 1
    # accidentals printed per engraved staff
    seg_off = {}
    for seg in segments_of(score, layout):
        for i in range(seg['start'], seg['end']):
            seg_off[i] = offs[seg['start']]
    for sid, onset, pp, name in prep['printed_acc']:
        E['acc'][(sid, str(F(onset)), midi(pp), GLYPH[name])] += 1
    for i, o, sym in score.harmonies:
        E['chordname'][sym] += 1
    # system delimiters
    nsys = len(system_starts(score, layout))
    delim = Counter()
    for seg in segments_of(score, layout):
        a, b = seg['start'], seg['end']
        ns = len([i for i in system_starts(score, layout) if a <= i < b])
        for g in iter_groups(seg['groups']):
            gt = g.get('type')
            if gt in DELIM and len(list(iter_staves([g]))) >= 2:
                d = DELIM[gt]
                for w in g.get('with', []):
                    if 'SystemStartSquare' in w:
                        d = 'SystemStartSquare'
                    elif 'SystemStartBrace' in w:
                        d = 'SystemStartBrace'
                delim[d] += ns
    return E, n, delim, nsys


def compare(score, layout, opts, prep, log_rows):
    from .notation import segments_of
    E, n, delim, nsys = expected_from_model(score, layout, opts, prep)
    offs = score.measure_offsets()
    segs = segments_of(score, layout)
    G = {k: Counter() for k in E}
    g = Counter()
    gdelim = Counter()
    seen = {}
    # segment offsets: the moment restarts at 0 in every \score; staff ids are reused per segment,
    # so map a log row to its segment by order of appearance is not possible -> use per-segment
    # staff id sets when unique, else assume the first segment.
    seg_starts = [offs[s['start']] for s in segs]

    def uniq(row):
        key = (row[0], row[4])
        if key in seen:
            return False
        seen[key] = True
        return True

    acc_rows = []
    for r in log_rows:
        nm, sid, when = r[0], r[1], r[2]
        f = r[5:]
        if nm == 'NoteHead':
            G['heads'][(int(f[1]), int(f[3]))] += 1
        elif nm == 'Stem':
            dl = int(f[1])
            if dl >= 1 and int(f[3]) > 0:      # rests also get (invisible, head-less) Stem grobs
                G['stems'][(int(f[0]), dl)] += 1
        elif nm == 'Flag':
            g['flags'] += 1
        elif nm == 'Beam':
            if uniq(r):
                g['beams'] += 1
        elif nm == 'Accidental':
            acc_rows.append((sid, _when(when), int(f[1]) if f[1].lstrip('-').isdigit() else f[1], f[0]))
        elif nm in ('Rest',):
            g['rests'] += 1
            G['rests'][(int(f[0]), int(f[1]))] += 1
        elif nm == 'MultiMeasureRest':
            g['rests'] += 1
        elif nm == 'Script':
            s = f[0]
            name = next((x for x in SCRIPT_NAMES if x in s), s)
            G['scripts'][name] += 1
        elif nm == 'Slur':
            if uniq(r):
                g['slurs'] += 1
        elif nm == 'Tie':
            if uniq(r):
                g['ties'] += 1
        elif nm == 'DynamicText':
            G['dyn'][f[0]] += 1
        elif nm == 'Hairpin':
            if uniq(r):
                G['hairpin'][int(f[0])] += 1
        elif nm == 'TextScript':
            g['textscript'] += 1
        elif nm == 'LyricText':
            G['lyric'][f[0]] += 1
        elif nm == 'LyricHyphen':
            if uniq(r):
                g['hyphens'] += 1
        elif nm == 'LyricExtender':
            if uniq(r):
                g['extenders'] += 1
        elif nm == 'ChordName':
            G['chordname'][f[0]] += 1
        elif nm == 'TupletNumber':
            if uniq(r):
                g['tuplets'] += 1
        elif nm == 'SustainPedal':
            g['pedal'] += 1
        elif nm == 'BreathingSign':
            g['breath'] += 1
        elif nm == 'Arpeggio':
            g['arpeggio'] += 1
        elif nm == 'Fingering':
            G['fingering'][f[0]] += 1
        elif nm in ('LyricHyphenInk', 'LyricExtenderInk'):
            k = ('ink', nm, r[4])
            seen[k] = max(seen.get(k, 0), int(f[0]))
        elif nm in ('SystemStartBrace', 'SystemStartBracket', 'SystemStartSquare'):
            gdelim[nm] += 1
    g['hyphens_visible'] = sum(v for k, v in seen.items() if isinstance(k, tuple) and k[0] == 'ink'
                               and k[1] == 'LyricHyphenInk')
    g['extenders_visible'] = sum(v for k, v in seen.items() if isinstance(k, tuple) and k[0] == 'ink'
                                 and k[1] == 'LyricExtenderInk')
    n['hyphens_visible'] = n['hyphens']
    n['extenders_visible'] = n['extenders']
    # accidentals: rows carry the moment within their \score; add the segment offset (staff id sets
    # per segment are checked against the expectation with every possible offset)
    exp_acc = E['acc']
    got_acc = Counter()
    for sid, w, pm, glyph in acc_rows:
        cands = [(sid, str(w + so), pm, glyph) for so in seg_starts]
        pick = next((c for c in cands if exp_acc.get(c, 0) > got_acc.get(c, 0)), cands[0])
        got_acc[pick] += 1
    G['acc'] = got_acc
    rep = {'ok': True, 'systems_expected': nsys, 'mismatch': {}}
    for k in E:
        if k == 'chordname':
            # chord names are compared by count (LilyPond prints its own spelling, e.g. superscripts)
            if sum(E[k].values()) != sum(G[k].values()):
                rep['mismatch'][k] = {'expected': sum(E[k].values()), 'printed': sum(G[k].values()),
                                      'printed_texts': sorted(G[k].elements())[:40]}
            continue
        if E[k] != G[k]:
            miss = E[k] - G[k]
            extra = G[k] - E[k]
            rep['mismatch'][k] = {'missing_in_print': [str(x) for x in sorted(miss.elements(), key=str)][:20],
                                  'extra_in_print': [str(x) for x in sorted(extra.elements(), key=str)][:20]}
    for k in set(n) | set(g):
        if k in ('rests_split',):
            continue
        if n.get(k, 0) != g.get(k, 0):
            rep['mismatch'][k] = {'expected': n.get(k, 0), 'printed': g.get(k, 0)}
    if +delim != +gdelim:
        rep['mismatch']['system_delimiters'] = {'expected': dict(delim), 'printed': dict(gdelim)}
    rep['ok'] = not rep['mismatch']
    rep['printed_summary'] = {
        'noteheads': sum(G['heads'].values()), 'stems_up': sum(v for (d, _), v in G['stems'].items() if d == 1),
        'stems_down': sum(v for (d, _), v in G['stems'].items() if d == -1), 'accidentals': sum(G['acc'].values()),
        'rests': g['rests'], 'beams': g['beams'], 'flags': g['flags'], 'slurs': g['slurs'], 'ties': g['ties'],
        'scripts': dict(G['scripts']), 'dynamics': dict(G['dyn']), 'lyric_syllables': sum(G['lyric'].values()),
        'hyphens': g['hyphens'], 'extenders': g['extenders'], 'hyphens_visible': g['hyphens_visible'],
        'extenders_visible': g['extenders_visible'], 'chord_names': sum(G['chordname'].values()),
        'system_delimiters': dict(gdelim)}
    return rep
