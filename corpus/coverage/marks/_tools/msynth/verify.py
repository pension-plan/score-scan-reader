"""Truth-vs-engraving verification for the coverage/marks corpus.

1. LilyPond runs with dump.ly.  Every music event heard by each Voice (notes with chord-internal
   fingerings, rests, ties, beams, slurs, articulations, ornaments, fermatas, dynamics, hairpins,
   pedal, fingering, text scripts, arpeggios, breath marks), every tempo / mark event and every
   ChordNames pitch is compared with the score model the truth is written from (multiset equality
   on exact rational moments).
2. Grob census: the number of printed grobs of every relevant kind (Script, DynamicText, Hairpin,
   SustainPedal, Fingering, TextScript, MetronomeMark, RehearsalMark, ChordName, Arpeggio,
   BreathingSign, Slur, Tie, Beam, NoteHead, Rest, MultiMeasureRest, Accidental) equals the
   model; every printed accidental (staff, moment, pitch, alteration) equals the truth's.
3. Stem directions and the side (above / below) of every articulation, ornament, fermata and
   fingering are read back from the engraving (final grob directions) into the truth.
4. LilyPond MIDI (onset, pitch) attack multiset == truth.
5. truth.musicxml re-parsed with music21: notes / rests / onsets / durations == model (marks seen by
   music21 are reported for information); xmllint against the MusicXML 4.0 XSD.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections import Counter
from fractions import Fraction as F

from .lily import vname
from .midi import read_midi
from .model import KIND_INTERVALS, LOG, STEP_PC, Score, midi, staff_events

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'dump.ly')
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
DIR = {None: '()', 'above': '1', 'below': '-1'}


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly_path, workdir):
    base = os.path.splitext(os.path.basename(ly_path))[0]
    ev = os.path.join(workdir, base + '.events')
    if os.path.exists(ev):
        os.remove(ev)
    rc, out, err = run(['lilypond', '-dno-point-and-click', f'-dinclude-settings={DUMP}', '-o', base,
                        os.path.basename(ly_path)], cwd=workdir)
    warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
    mid = None
    for ext in ('.midi', '.mid'):
        if os.path.exists(os.path.join(workdir, base + ext)):
            mid = os.path.join(workdir, base + ext)
    return rc, warns, err, os.path.join(workdir, base + '.pdf'), mid, ev


def parse_events(path):
    out = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 7:
            continue
        ctype, cid, mom, gr, bar, mpos, kind = f[:7]
        rec = {'ctype': ctype, 'id': cid, 't': F(mom) * 4, 'g': F(gr) * 4, 'bar': int(bar), 'kind': kind,
               'args': f[7:]}
        out.setdefault((ctype, cid), []).append(rec)
    return out


# ---------------------------------------------------------------- expectations

def expected_voice(score: Score, st):
    out = []
    for i, t, ev in staff_events(score, st):
        if ev.kind == 'clef':
            continue
        if ev.kind == 'note':
            for p in ev.pitches:
                out.append(('note', t, midi(p), LOG[ev.dtype], ev.dots))
                if len(ev.pitches) > 1:
                    for dg, pl, fp in ev.fingering:
                        if fp == p:
                            out.append(('ifinger', t, midi(p), dg, DIR[pl]))
            if ev.tie_start:
                out.append(('tie', t))
            if len(ev.pitches) == 1:
                for dg, pl, fp in ev.fingering:
                    out.append(('finger', t, dg, DIR[pl]))
        elif ev.measure_rest:
            out.append(('mmrest', t, ev.dur))
        else:
            out.append(('rest', t, LOG[ev.dtype], ev.dots))
        if ev.beam_start:
            out.append(('beam', t, -1))
        if ev.beam_stop:
            out.append(('beam', t, 1))
        if ev.slur_start:
            out.append(('slur', t, -1))
        if ev.slur_stop:
            out.append(('slur', t, 1))
        for typ, pl in ev.marks:
            out.append(('artic', t, typ, DIR[pl]))
        for d in ev.dynamics:
            out.append(('dyn', t, d))
        for wd in ev.wedges:
            if wd == 'crescendo':
                out.append(('cresc', t, -1))
            elif wd == 'diminuendo':
                out.append(('decresc', t, -1))
            elif wd == 'stop':
                out.append(('cresc', t, 1))
        for pd in ev.pedal:
            out.append(('sustain', t, -1 if pd == 'start' else 1))
        for txt, pl in ev.words:
            out.append(('text', t, txt, DIR[pl]))
        if ev.arpeggio:
            out.append(('arpeggio', t))
        if ev.breath:
            out.append(('breathe', t + ev.dur))
    return out


def got_voice(recs):
    out = []
    for r in recs:
        t, k, a = r['t'], r['kind'], r['args']
        if r['g'] != 0:
            out.append(('grace?', t, k))
            continue
        if k == 'note':
            log, dots, scale = a[1].split()
            out.append(('note', t, int(a[0]), int(log), int(dots)))
            if F(scale) != 1:
                out.append(('scaled', t, a[1]))
            for inner in filter(None, a[2].split(',') if len(a) > 2 else []):
                cls, dg, dr = inner.split(':')
                if cls == 'fingering-event':
                    out.append(('ifinger', t, int(a[0]), int(dg), dr))
                else:
                    out.append(('inner?', t, inner))
        elif k == 'rest':
            log, dots, scale = a[0].split()
            out.append(('rest', t, int(log), int(dots)))
        elif k == 'mmrest':
            log, dots, scale = a[0].split()
            out.append(('mmrest', t, F(4) / F(2) ** int(log) * (2 - F(1, 2 ** int(dots))) * F(scale)))
        elif k == 'tie':
            out.append(('tie', t))
        elif k in ('beam', 'slur', 'cresc', 'decresc', 'sustain'):
            out.append((k, t, int(a[0])))
        elif k == 'artic':
            out.append(('artic', t, a[0], a[1]))
        elif k == 'dyn':
            out.append(('dyn', t, a[0]))
        elif k == 'finger':
            out.append(('finger', t, int(a[0]), a[1]))
        elif k == 'text':
            out.append(('text', t, a[0], a[1]))
        elif k in ('arpeggio', 'breathe'):
            out.append((k, t))
    return out


def _diff(exp, got, limit=15):
    ce, cg = Counter(exp), Counter(got)
    miss, extra = ce - cg, cg - ce
    return {'ok': not miss and not extra, 'n_expected': sum(ce.values()), 'n_got': sum(cg.values()),
            'missing': [str(x) for x in sorted(miss.elements(), key=str)[:limit]],
            'extra': [str(x) for x in sorted(extra.elements(), key=str)[:limit]]}


def expected_grobs(score: Score):
    c = Counter()
    for p, st in score.staves():
        evs = [ev for _, _, ev in staff_events(score, st)]
        beamed = set()
        inb = False
        for ev in evs:
            if ev.beam_start:
                inb = True
            if inb:
                beamed.add(id(ev))
            if ev.beam_stop:
                inb = False
        for ev in evs:
            if ev.kind == 'clef':
                continue
            c['Script'] += len(ev.marks)
            c['DynamicText'] += len(ev.dynamics)
            c['Hairpin'] += sum(1 for w in ev.wedges if w in ('crescendo', 'diminuendo'))
            c['SustainPedal'] += 1 if ev.pedal else 0
            c['Fingering'] += len(ev.fingering)
            c['TextScript'] += len(ev.words)
            c['MetronomeMark'] += 1 if ev.tempo else 0
            c['Arpeggio'] += 1 if ev.arpeggio else 0
            c['BreathingSign'] += 1 if ev.breath else 0
            c['Slur'] += 1 if ev.slur_start else 0
            c['Tie'] += len(ev.tie_start)
            c['Beam'] += 1 if ev.beam_start else 0
            if ev.kind == 'note':
                c['NoteHead'] += len(ev.pitches)
                c['Accidental'] += len(ev.accidentals)
                if ev.dtype in ('eighth', '16th', '32nd', '64th') and id(ev) not in beamed:
                    c['Flag'] += 1
            elif ev.measure_rest:
                c['MultiMeasureRest'] += 1
            else:
                c['Rest'] += 1
        c['ChordName'] += len(p.chords) if st.number == 1 else 0
    c['RehearsalMark'] = sum(1 for m in score.measures if m.mark)
    return c


GROB_KINDS = ['Script', 'DynamicText', 'Hairpin', 'SustainPedal', 'Fingering', 'TextScript', 'MetronomeMark',
              'RehearsalMark', 'ChordName', 'Arpeggio', 'BreathingSign', 'Slur', 'Tie', 'Beam', 'NoteHead',
              'Rest', 'MultiMeasureRest', 'Accidental']


def compare_engraving(score: Score, events_path: str):
    ev = parse_events(events_path)
    rep = {'voices': {}, 'score': None, 'chords': {}, 'grobs': None, 'accidentals': None}
    ok = True
    for p, st in score.staves():
        recs = ev.get(('Voice', vname(st)), [])
        d = _diff(expected_voice(score, st), got_voice(recs))
        rep['voices'][vname(st)] = d
        ok &= d['ok']
    # score-level events
    offs = score.offsets()
    exp = []
    for p, st in score.staves():
        for i, t, e in staff_events(score, st):
            if e.tempo:
                tp = e.tempo
                unit = '-'
                if tp['unit']:
                    unit = f"{LOG[tp['unit']]} {tp['dots']} 1"
                exp.append(('tempo', t, tp['text'] or '()', unit, str(tp['bpm']) if tp['bpm'] else '#f'))
    for i, m in enumerate(score.measures):
        if m.mark:
            exp.append(('mark', offs[i], '()'))
    got = []
    for (ct, cid), recs in ev.items():
        if ct != 'Score':
            continue
        for r in recs:
            if r['kind'] == 'tempo':
                got.append(('tempo', r['t'], r['args'][0], r['args'][1], r['args'][2]))
            elif r['kind'] == 'mark':
                got.append(('mark', r['t'], r['args'][0]))
    d = _diff(exp, got)
    rep['score'] = d
    ok &= d['ok']
    # chord names: pitch-class content per onset
    for p in score.parts:
        if not p.chords:
            continue
        recs = ev.get(('ChordNames', 'cn' + p.id), [])
        byt = {}
        for r in recs:
            if r['kind'] == 'cnote':
                byt.setdefault(r['t'], set()).add(int(r['args'][0]) % 12)
        exp = []
        for c in p.chords:
            root = (STEP_PC[c['root'][0]] + c['root'][1]) % 12
            pcs = {(root + iv) % 12 for iv in KIND_INTERVALS[c['kind']]}
            if c['bass']:
                pcs.add((STEP_PC[c['bass'][0]] + c['bass'][1]) % 12)
            exp.append((c['t'], tuple(sorted(pcs))))
        got = [(t, tuple(sorted(v))) for t, v in byt.items()]
        d = _diff(exp, got)
        rep['chords'][p.id] = d
        ok &= d['ok']
    # grob census
    gc = Counter()
    texts = {}
    accs = []
    for (ct, cid), recs in ev.items():
        if ct != 'Score':
            continue
        for r in recs:
            if r['kind'] != 'G':
                continue
            name = r['args'][0]
            gc[name] += 1
            if name in ('DynamicText', 'TextScript', 'ChordName', 'Fingering', 'MetronomeMark', 'RehearsalMark',
                        'SustainPedal', 'Script'):
                texts.setdefault(name, Counter())[r['args'][2] if len(r['args']) > 2 else ''] += 1
            if name == 'Accidental':
                accs.append((r['args'][1], r['t'], int(r['args'][2]), F(r['args'][3])))
    eg = expected_grobs(score)
    gd = {k: {'expected': eg.get(k, 0), 'printed': gc.get(k, 0)} for k in GROB_KINDS}
    bad = {k: v for k, v in gd.items() if v['expected'] != v['printed']}
    rep['grobs'] = {'ok': not bad, 'counts': gd, 'mismatch': bad,
                    'printed_texts': {k: dict(v) for k, v in texts.items()}}
    ok &= not bad
    exp_acc = []
    alt = {'sharp': 1, 'flat': -1, 'natural': 0, 'double-sharp': 2, 'flat-flat': -2}
    for p, st in score.staves():
        for i, t, e in staff_events(score, st):
            for pit, name in e.accidentals.items():
                exp_acc.append((vname(st), t, midi(pit), F(alt[name], 2)))
    d = _diff(exp_acc, accs)
    rep['accidentals'] = d
    ok &= d['ok']
    rep['ok'] = ok
    return rep


def read_engraved(score: Score, events_path: str):
    """Set ev.stem, ev.mark_dirs and ev.finger_dirs from the engraving (final Stem / Script /
    Fingering directions); a forced placement in the model must agree with the engraving."""
    ev = parse_events(events_path)
    n, nd, missing, conflicts = 0, 0, [], []
    side = {1: 'above', -1: 'below'}
    for p, st in score.staves():
        recs = ev.get(('Voice', vname(st)), [])
        by, scr, fng = {}, {}, {}
        for r in recs:
            a = r['args']
            if r['kind'] == 'stem':
                pitches = tuple(sorted(int(x) for x in a[3].split())) if len(a) > 3 else ()
                by[(F(a[0]) * 4, pitches)] = (int(a[1]), int(a[2]))
            elif r['kind'] == 'scriptdir':
                scr.setdefault((F(a[0]) * 4, a[1]), []).append(int(a[2]))
            elif r['kind'] == 'fingerdir':
                fng.setdefault((F(a[0]) * 4, int(a[1])), []).append(int(a[2]))
        for i, t, e in staff_events(score, st):
            if e.kind == 'clef':
                continue
            if e.kind == 'note':
                key = (t, tuple(sorted(midi(x) for x in e.pitches)))
                if key not in by:
                    missing.append(('stem',) + key)
                else:
                    dlog, dr = by[key]
                    e.stem = None if dlog < 1 else ('up' if dr == 1 else 'down')
                    n += 1
            e.mark_dirs = []
            for typ, pl in e.marks:
                lst = scr.get((t, typ))
                if not lst:
                    missing.append(('script', t, typ))
                    e.mark_dirs.append(pl)
                    continue
                d = side[lst.pop(0)]
                if pl and pl != d:
                    conflicts.append(('script', t, typ, pl, d))
                e.mark_dirs.append(d)
                nd += 1
            e.finger_dirs = []
            for dg, pl, fp in e.fingering:
                lst = fng.get((t, dg))
                if not lst:
                    missing.append(('finger', t, dg))
                    e.finger_dirs.append(pl)
                    continue
                d = side[lst.pop(0)]
                if pl and pl != d:
                    conflicts.append(('finger', t, dg, pl, d))
                e.finger_dirs.append(d)
                nd += 1
        left = [k for k, v in list(scr.items()) + list(fng.items()) if v]
        missing.extend(('unmatched',) + k for k in left)
    return {'ok': not missing and not conflicts, 'stems_read': n, 'directions_read': nd,
            'missing': [str(x) for x in missing[:10]], 'conflicts': [str(x) for x in conflicts[:10]]}


def compare_midi(score: Score, midi_path: str):
    div, tracks = read_midi(midi_path)
    got = Counter()
    for tr in tracks:
        for t, p in tr['notes']:
            got[(F(t, div), p)] += 1
    exp = Counter()
    for p, st in score.staves():
        for i, t, e in staff_events(score, st):
            if e.kind == 'note':
                for pit in e.pitches:
                    if pit not in e.tie_stop:
                        exp[(t, midi(pit))] += 1
    miss, extra = exp - got, got - exp
    return {'ok': not miss and not extra, 'expected_attacks': sum(exp.values()), 'midi_attacks': sum(got.values()),
            'missing': [str(x) for x in sorted(miss.elements())[:10]],
            'extra': [str(x) for x in sorted(extra.elements())[:10]]}


def compare_music21(score: Score, truth_path: str):
    from music21 import articulations, chord, converter, dynamics, expressions, harmony, note, tempo
    s = converter.parse(truth_path, format='musicxml', forceSource=True)
    m21parts = list(s.parts)
    rep = {}
    ok = True
    k = 0
    info = Counter()
    for part in score.parts:
        staffs = m21parts[k:k + len(part.staves)]
        k += len(part.staves)
        notes, rests = [], []
        for ps in staffs:
            for n in ps.recurse().notesAndRests:
                if isinstance(n, harmony.ChordSymbol):
                    info['ChordSymbol'] += 1
                    continue
                off = F(n.getOffsetInHierarchy(ps)).limit_denominator(10000)
                ql = F(n.duration.quarterLength).limit_denominator(10000)
                if isinstance(n, note.Rest):
                    rests.append((off, ql))
                    continue
                ps_ = [x.midi for x in (n.pitches if isinstance(n, chord.Chord) else [n.pitch])]
                notes.append((off, tuple(sorted(ps_)), ql))
                for a in n.articulations:
                    info[type(a).__name__] += 1
                for x in n.expressions:
                    info[type(x).__name__] += 1
            for x in ps.recurse().getElementsByClass(dynamics.Dynamic):
                info['Dynamic:' + x.value] += 1
            for x in ps.recurse().getElementsByClass((expressions.TextExpression,)):
                info['TextExpression'] += 1
            for x in ps.recurse().getElementsByClass((expressions.RehearsalMark,)):
                info['RehearsalMark'] += 1
            for x in ps.recurse().getElementsByClass((tempo.MetronomeMark,)):
                info['MetronomeMark'] += 1
        en, er = [], []
        for st in part.staves:
            for i, t, e in staff_events(score, st):
                if e.kind == 'note':
                    en.append((t, tuple(sorted(midi(x) for x in e.pitches)), e.dur))
                elif e.kind == 'rest':
                    er.append((t, e.dur))
        r = {'notes': _diff(en, notes), 'rests': _diff(er, rests)}
        rep[part.id] = r
        ok &= all(x['ok'] for x in r.values())
    for sp in s.spannerBundle:
        info['spanner:' + type(sp).__name__] += 1
    rep['music21_marks_seen'] = dict(sorted(info.items()))
    rep['ok'] = ok
    return rep


def xsd_validate(path):
    rc, out, err = run(['xmllint', '--noout', '--schema', XSD, path], timeout=120)
    return {'ok': rc == 0, 'message': (err.strip().splitlines() or [''])[-1][:300]}
