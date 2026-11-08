"""Truth-vs-engraving verification for the rhythm challenge corpus.

1. LilyPond is run with an event-dump engraver (dump.ly).  Every note / rest /
   multi-measure rest / tie / beam / slur / articulation / lyric syllable /
   hyphen / extender heard by each Voice and Lyrics context is written with its
   exact rational moment (main + grace part), bar number and measure position,
   and every time-signature grob created in each Staff.  These are compared with
   the score model the truth MusicXML is written from (multiset equality).
2. LilyPond MIDI: (onset, pitch) attack multiset == truth (as the synthetic corpus
   tools do; grace notes, which LilyPond plays before the beat, are excluded by pitch).
3. truth.musicxml re-parsed with music21: notes/rests/onsets/durations/tuplets/
   graces/ties/lyrics == model.
4. truth.musicxml validated against the MusicXML 4.0 XSD with xmllint.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections import Counter
from fractions import Fraction as F

from .lily import lyrics_name, vname
from .midicheck import read_midi
from .model import Score, attacks, display_ql, midi, voice_events

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, 'dump.ly')
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
LOG = {'breve': -1, 'whole': 0, 'half': 1, 'quarter': 2, 'eighth': 3, '16th': 4, '32nd': 5, '64th': 6}


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


# ---------------------------------------------------------------- dump parsing

def _fr(x):
    return F(x)


def parse_events(path):
    out = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 7:
            continue
        ctype, cid, mom, gr, bar, mpos, kind = f[:7]
        args = f[7:]
        rec = {'ctype': ctype, 'id': cid, 't': _fr(mom) * 4, 'g': _fr(gr) * 4, 'bar': int(bar),
               'mpos': None if mpos == '?' else _fr(mpos), 'kind': kind, 'args': args}
        out.setdefault(cid, []).append(rec)
    return out


def _dur_ql(log, dots, scale):
    base = F(4) / (F(2) ** log)
    tot = base * (2 - F(1, 2 ** dots))
    return tot * scale


def dump_records(recs):
    """normalise dump lines of one context into comparable tuples"""
    out = []
    for r in recs:
        t, g, k, a = r['t'], r['g'], r['kind'], r['args']
        if k == 'note':
            log, dots, scale = a[1].split()
            out.append(('note', t, g, int(a[0]), int(log), int(dots), F(scale)))
        elif k == 'rest':
            log, dots, scale = a[0].split()
            out.append(('rest', t, g, int(log), int(dots), F(scale)))
        elif k == 'mmrest':
            log, dots, scale = a[0].split()
            out.append(('mmrest', t, _dur_ql(int(log), int(dots), F(scale))))
        elif k in ('tie',):
            out.append(('tie', t, g))
        elif k in ('beam', 'slur'):
            out.append((k, t, g, int(a[0])))
        elif k in ('artic', 'mmartic'):
            out.append(('artic', t, g, a[0]))
        elif k == 'lyric':
            if a[0].strip():          # '_' skips are lyric events with text " "
                out.append(('lyric', t, a[0]))
        elif k in ('hyphen', 'extender'):
            out.append((k, t))
        elif k == 'timesig':
            out.append(('timesig', t, int(a[0]), int(a[1]), a[2]))
    return out


# ---------------------------------------------------------------- expectations from the model

def grace_offsets(evs, k):
    """grace moment (quarters, negative) of grace event k in list evs"""
    j = k
    tot = F(0)
    while j < len(evs) and evs[j].grace:
        tot += display_ql(evs[j].dtype, evs[j].dots)
        j += 1
    return -tot


def expected_voice(score: Score, part, vkey):
    out = []
    pos = []      # (t, bar, mpos) for non-grace notes/rests
    offs = score.measure_offsets()
    for i, mdict in enumerate(part.measures):
        mi = score.measures[i]
        t = offs[i]
        evs = mdict.get(vkey, [])
        for k, ev in enumerate(evs):
            g = grace_offsets(evs, k) if ev.grace else F(0)
            if ev.kind == 'note':
                scale = F(ev.tuplet[1], ev.tuplet[0]) if ev.tuplet else F(1)
                for p in ev.pitches:
                    out.append(('note', t, g, midi(p), LOG[ev.dtype], ev.dots, scale))
                if ev.tie_start:
                    out.append(('tie', t, g))
            elif ev.kind == 'rest':
                if ev.measure_rest:
                    if not ev.multirest_cont:
                        n = ev.multirest or 1
                        out.append(('mmrest', t, ev.dur * n))
                else:
                    scale = F(ev.tuplet[1], ev.tuplet[0]) if ev.tuplet else F(1)
                    out.append(('rest', t, g, LOG[ev.dtype], ev.dots, scale))
            if ev.kind in ('note', 'rest'):
                if ev.beam_start:
                    out.append(('beam', t, g, -1))
                if ev.beam_stop:
                    out.append(('beam', t, g, 1))
                if ev.slur_start or ev.grace_slur_start:
                    out.append(('slur', t, g, -1))
                if ev.slur_stop or ev.grace_slur_stop:
                    out.append(('slur', t, g, 1))
                if ev.fermata:
                    out.append(('artic', t, g, 'fermata'))
                for a in ev.artic:
                    out.append(('artic', t, g, a))
                if not ev.grace and not ev.multirest_cont:
                    mpos = (t - offs[i]) / 4
                    if i == 0 and mi.implicit:
                        mpos = (t - offs[i] - mi.dur) / 4
                    pos.append((ev.kind, t, max(1, mi.number), mpos))
            t += ev.dur
    return out, pos


def expected_lyrics(score: Score, part, vkey, verse):
    out = []
    for i, t, ev in voice_events(score, part, vkey):
        if ev.kind != 'note' or ev.grace:
            continue
        ly = ev.lyrics.get(verse)
        if ly is None:
            continue
        out.append(('lyric', t, ly.text))
        if ly.syllabic in ('begin', 'middle'):
            out.append(('hyphen', t))
        elif ly.extend:
            out.append(('extender', t))
    return out


def expected_timesigs(score: Score):
    out = []
    offs = score.measure_offsets()
    for i, mi in enumerate(score.measures):
        if mi.time:
            n, d = mi.time
            style = None
            if (n, d) in ((4, 4), (2, 2)):
                style = 'C' if mi.time_symbol in ('common', 'cut') else 'numbered'
            out.append(('timesig', offs[i], n, d, style))
    return out


def _diff(exp, got, limit=12):
    ce, cg = Counter(exp), Counter(got)
    miss = ce - cg
    extra = cg - ce
    return {'ok': not miss and not extra, 'n_expected': sum(ce.values()), 'n_got': sum(cg.values()),
            'missing': [str(x) for x in sorted(miss.elements(), key=str)[:limit]],
            'extra': [str(x) for x in sorted(extra.elements(), key=str)[:limit]]}


def compare_engraving(score: Score, layout: dict, events_path: str):
    ev = parse_events(events_path)
    rep = {'voices': {}, 'lyrics': {}, 'timesig': {}, 'positions': {}}
    ok = True
    for p in score.parts:
        for v in p.voices:
            name = vname(p.id, v.key)
            exp, pos = expected_voice(score, p, v.key)
            recs = ev.get(name, [])
            got = [r for r in dump_records(recs) if r[0] not in ('lyric', 'hyphen', 'extender', 'timesig')]
            d = _diff(exp, got)
            rep['voices'][name] = d
            ok &= d['ok']
            # bar number / measure position of every note and rest
            gotpos = []
            for r in recs:
                if r['kind'] in ('note', 'rest', 'mmrest') and r['g'] == 0:
                    gotpos.append(('note' if r['kind'] == 'note' else 'rest', r['t'], r['bar'], r['mpos']))
            gp = sorted(set(gotpos), key=str)
            ep = sorted(set(pos), key=str)
            dp = _diff(ep, gp)
            rep['positions'][name] = dp
            ok &= dp['ok']
    # lyrics
    for g in layout['groups']:
        for st in g['staves']:
            for l in st.get('lyrics', []):
                pid, vk = l['voice']
                for vn in l['verses']:
                    nm = lyrics_name(pid, vk, vn)
                    exp = expected_lyrics(score, score.part(pid), vk, vn)
                    got = [r for r in dump_records(ev.get(nm, [])) if r[0] in ('lyric', 'hyphen', 'extender')]
                    d = _diff(exp, got)
                    rep['lyrics'][nm] = d
                    ok &= d['ok']
    # every voice with lyrics in the model must be engraved with them
    for p in score.parts:
        for v in p.voices:
            for vn in sorted({n for m in p.measures for e in m.get(v.key, []) for n in e.lyrics}):
                if lyrics_name(p.id, v.key, vn) not in rep['lyrics']:
                    rep['lyrics'][lyrics_name(p.id, v.key, vn)] = {'ok': False, 'error': 'not engraved'}
                    ok = False
    # time signatures per staff
    exp_ts = expected_timesigs(score)
    for g in layout['groups']:
        for st in g['staves']:
            got = [r for r in dump_records(ev.get(st['id'], [])) if r[0] == 'timesig']
            got = [(a, t, n, d, (s if (n, d) in ((4, 4), (2, 2)) else None)) for a, t, n, d, s in got]
            dd = _diff(exp_ts, got)
            rep['timesig'][st['id']] = dd
            ok &= dd['ok']
    rep['ok'] = ok
    return rep


# ---------------------------------------------------------------- MIDI

def compare_midi(score: Score, midi_path: str):
    div, tracks = read_midi(midi_path)
    got = Counter()
    for tr in tracks:
        for t, p in tr['notes']:
            got[(t, p)] += 1
    # a grace note before the first beat makes LilyPond start the MIDI timeline earlier
    lead = F(0)
    for p_ in score.parts:
        for v in p_.voices:
            evs = p_.measures[0].get(v.key, []) if p_.measures else []
            k = next((j for j, e in enumerate(evs) if e.kind != 'clef'), None)
            if k is not None and evs[k].grace:
                lead = max(lead, -grace_offsets(evs, k))
    # compare on the MIDI tick grid (quintuplets etc. are not tick-exact).  With a leading
    # grace LilyPond shifts the whole timeline by the grace's performed length: pick the
    # constant shift that matches the most attacks (0 when there is no leading grace).
    base = Counter((int(round(F(t) * div)), p) for t, p, _, _ in attacks(score))
    shifts = {0}
    if lead:
        first = sorted(base)[:40]
        for (gt, gp) in got:
            for (et, ep) in first:
                if gp == ep and 0 < gt - et <= lead * div:
                    shifts.add(gt - et)
    best = max(shifts, key=lambda sh: sum((Counter({(t + sh, p): n for (t, p), n in base.items()}) & got).values()))
    exp = Counter({(t + best, p): n for (t, p), n in base.items()})
    fuzzy = Counter()
    for (t, p), n in list((exp - got).items()):
        for dt in (-1, 1):
            if (got - exp)[(t + dt, p)]:
                fuzzy[(t, p)] += 1
                exp[(t, p)] -= 1
                exp[(t + dt, p)] += 1
                break
    grace_p = Counter()
    for p in score.parts:
        for v in p.voices:
            for _, _, e in voice_events(score, p, v.key):
                if e.grace:
                    for pit in e.pitches:
                        grace_p[midi(pit)] += 1
    missing = exp - got
    extra = got - exp
    # grace notes are performed before the beat (stolen time): discount by pitch
    extra_by_p = Counter()
    for (t, p), n in extra.items():
        extra_by_p[p] += n
    unexplained = extra_by_p - grace_p
    return {'ok': not missing and not unexplained, 'expected_attacks': sum(exp.values()),
            'tick_rounded': sum(fuzzy.values()), 'leading_grace_offset_quarters': str(lead), 'midi_shift_ticks': best,
            'midi_attacks': sum(got.values()), 'grace_notes': sum(grace_p.values()),
            'missing': [str(x) for x in sorted(missing.elements())[:10]],
            'unexplained_extra': [str(x) for x in sorted(unexplained.elements())[:10]]}


# ---------------------------------------------------------------- music21 round trip

def _model_m21_view(score: Score, part):
    notes, rests, lyr, ties = [], [], [], []
    for v in part.voices:
        for i, t, ev in voice_events(score, part, v.key):
            if ev.kind == 'note':
                ql = F(0) if ev.grace else ev.dur
                notes.append((t, tuple(sorted(midi(p) for p in ev.pitches)), ql, bool(ev.grace),
                              ev.tuplet or (1, 1)))
                for p in ev.pitches:
                    if p in ev.tie_start:
                        ties.append((t, midi(p), 'start'))
                for n, ly in ev.lyrics.items():
                    lyr.append((t, n, ly.text, ly.syllabic))
            elif ev.kind == 'rest':
                rests.append((t, ev.dur))
    return notes, rests, lyr, ties


def compare_music21(score: Score, truth_path: str):
    from music21 import chord, converter, note
    s = converter.parse(truth_path, format='musicxml', forceSource=True)
    m21parts = list(s.parts)
    rep = {}
    ok = True
    k = 0
    for part in score.parts:
        staffs = m21parts[k:k + part.staves]
        k += part.staves
        notes, rests, lyr, ties = [], [], [], []
        for ps in staffs:
            for n in ps.recurse().notesAndRests:
                off = F(n.getOffsetInHierarchy(ps)).limit_denominator(10000)
                ql = F(n.duration.quarterLength).limit_denominator(10000)
                if isinstance(n, note.Rest):
                    rests.append((off, ql))
                    continue
                pitches = [p.midi for p in (n.pitches if isinstance(n, chord.Chord) else [n.pitch])]
                tup = n.duration.tuplets
                ratio = (tup[0].numberNotesActual, tup[0].numberNotesNormal) if tup else (1, 1)
                notes.append((off, tuple(sorted(pitches)), ql, bool(n.duration.isGrace), ratio))
                if isinstance(n, chord.Chord):
                    for nn in n.notes:
                        if nn.tie is not None and nn.tie.type in ('start', 'continue'):
                            ties.append((off, nn.pitch.midi, 'start'))
                elif n.tie is not None and n.tie.type in ('start', 'continue'):
                    ties.append((off, n.pitch.midi, 'start'))
                for ly in n.lyrics:
                    lyr.append((off, ly.number, ly.text, ly.syllabic))
        en, er, el, et = _model_m21_view(score, part)
        r = {'notes': _diff(en, notes), 'rests': _diff(er, rests), 'lyrics': _diff(el, lyr),
             'ties': _diff(et, ties)}
        rep[part.id] = r
        ok &= all(x['ok'] for x in r.values())
    rep['ok'] = ok
    return rep


def xsd_validate(path):
    rc, out, err = run(['xmllint', '--noout', '--schema', XSD, path], timeout=120)
    return {'ok': rc == 0, 'message': (err.strip().splitlines() or [''])[-1][:300]}


# ---------------------------------------------------------------- coverage/rests: layout read-back
# Base Y extents (staff spaces, relative to the middle staff line) of LilyPond 2.24 rest glyphs at
# their normal position (staff-position 0); measured with the Emmentaler font.  A rest drawn at
# staff-position p must have extents base + p/2 (one bound may grow by a ledger line outside the staff).
REST_BASE = {-1: (0.0, 1.0), 0: (0.375, 1.0), 1: (0.0, 0.625), 2: (-1.25, 1.5625), 3: (-1.05, 0.82),
             4: (-2.05, 0.82), 5: (-2.05, 1.82), 6: (-3.05, 1.82)}
MMR_BASE = {'whole': (0.375, 1.0), 'breve': (0.0, 1.0)}


def _num(x):
    return None if x in ('?', '()', '') else float(x)


def layout_records(events_path):
    rests, stems = {}, {}
    for line in open(events_path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 8 or f[6] not in ('restpos', 'mmrestpos', 'stem'):
            continue
        key = (f[1], F(f[2]) * 4, F(f[3]) * 4)
        if f[6] == 'stem':
            log, d = _num(f[7]), _num(f[8])
            if log is not None and log >= 1:
                stems.setdefault(key, []).append(int(d))
        elif f[6] == 'restpos':
            rests.setdefault(key, []).append(('rest', int(_num(f[7])), _num(f[8]), _num(f[9]), _num(f[10])))
        else:
            rests.setdefault(key, []).append(('mmrest', None, _num(f[7]), _num(f[8]), _num(f[9])))
    return rests, stems


def expected_rest_positions(score: Score):
    """(voice name, onset, 0) -> (kind, log, expected staff position, measure index, event)"""
    from .model import active_voices, clef_at, clef_timeline, staff_pos
    tl = clef_timeline(score)
    out = {}
    problems = []
    offs = score.measure_offsets()
    for p in score.parts:
        for v in p.voices:
            for i, mm in enumerate(p.measures):
                t = offs[i]
                for k, ev in enumerate(mm.get(v.key, [])):
                    if ev.kind == 'rest' and not ev.multirest_cont:
                        clef = clef_at(tl, p.id, v.staff, t, k)
                        pos = staff_pos(ev.display, clef) if ev.display is not None else 0
                        if ev.display is None and len(active_voices(score, p, v.staff, i)) > 1:
                            problems.append(f'{p.id}/{v.key} m{i + 1} t={t}: rest in a multi-voice measure '
                                            'without explicit position')
                        kind = 'mmrest' if ev.measure_rest else 'rest'
                        log = None if ev.measure_rest else LOG[ev.dtype]
                        out[(vname(p.id, v.key), t, F(0))] = (kind, log, pos, i, ev)
                    t += ev.dur
    return out, problems


def check_rest_layout(score: Score, events_path: str):
    rests, _ = layout_records(events_path)
    exp, problems = expected_rest_positions(score)
    bad = list(problems)
    n_ok = 0
    for key, (kind, log, pos, i, ev) in exp.items():
        got = rests.get(key, [])
        if len(got) != 1:
            bad.append(f'{key}: {len(got)} engraved rest grobs')
            continue
        gk, glog, gpos, lo, hi = got[0]
        if gk != kind or (kind == 'rest' and glog != log):
            bad.append(f'{key}: engraved {gk}/{glog}, truth {kind}/{log}')
            continue
        if gpos is None:
            gpos = 0.0
        if abs(gpos - pos) > 1e-6:
            bad.append(f'{key}: staff-position {gpos} != {pos}')
            continue
        if kind == 'rest':
            base = REST_BASE[log]
        elif ev.multirest > 1:
            base = None            # church-rest / H-bar block: glyph depends on the bar count
        else:
            base = MMR_BASE['breve' if ev.dur >= 8 else 'whole']
        if base is not None and lo is not None:
            if not (abs(lo - (base[0] + pos / 2)) < 0.02 or abs(hi - (base[1] + pos / 2)) < 0.02):
                bad.append(f'{key}: extent {lo:.3f}..{hi:.3f} != base {base} + {pos}/2')
                continue
        n_ok += 1
    extra = [k for k in rests if k not in exp]
    for k in extra:
        bad.append(f'{k}: engraved rest not in truth')
    return {'ok': not bad, 'rests_checked': len(exp), 'rests_ok': n_ok,
            'explicit_positions': sum(1 for x in exp.values() if x[4].display is not None),
            'problems': bad[:20]}


def assign_stems(score: Score, events_path: str):
    """set Event.stem from the engraved Stem grobs (notes of half value or shorter)"""
    _, stems = layout_records(events_path)
    offs = score.measure_offsets()
    used = set()
    missing = []
    n = 0
    for p in score.parts:
        for v in p.voices:
            for i, mm in enumerate(p.measures):
                t = offs[i]
                evs = mm.get(v.key, [])
                for k, ev in enumerate(evs):
                    if ev.kind == 'note' and ev.dtype not in ('whole', 'breve'):
                        g = grace_offsets(evs, k) if ev.grace else F(0)
                        key = (vname(p.id, v.key), t, g)
                        d = stems.get(key)
                        if not d or len(d) != 1:
                            missing.append(str(key) + f' {d}')
                            ev.stem = None
                        else:
                            ev.stem = 'up' if d[0] > 0 else 'down'
                            used.add(key)
                            n += 1
                    t += ev.dur
    extra = [str(k) for k in stems if k not in used]
    return {'ok': not missing and not extra, 'stems': n, 'missing': missing[:10], 'extra': extra[:10]}
