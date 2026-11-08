"""music21 Score -> internal model, with normalisation:
 - grace notes and ornaments dropped (not engraved, not in truth)
 - hidden rests/notes become invisible spacers (no truth rests)
 - pickup / split measures get their real (short) duration
 - complex durations are split into tied notes
 - lyric verse numbers renumbered 1..n, verse labels ("1.") stripped
"""
from __future__ import annotations

import warnings
from fractions import Fraction as F

import music21 as m21

from .model import (TYPE_QL, Event, Lyric, MeasureInfo, Part, Score, VoiceDef, clean_text,
                    compute_extenders, display_ql, renumber, sanitize_ties)

warnings.filterwarnings('ignore')

DYN_OK = {'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'sf', 'sfz', 'fp', 'sfp', 'rfz', 'fz'}


def clef_name(c) -> str:
    sign, line, octv = c.sign, c.line, getattr(c, 'octaveChange', 0) or 0
    if sign == 'G' and octv == -1:
        return 'treble_8'
    if sign == 'G' and octv == 1:
        return 'treble^8'
    if sign == 'G':
        return 'treble'
    if sign == 'F' and line == 3:
        return 'varbaritone'
    if sign == 'F':
        return 'bass' if octv == 0 else 'bass_8'
    if sign == 'C':
        return {1: 'soprano', 2: 'mezzosoprano', 3: 'alto', 4: 'tenor', 5: 'baritone'}.get(line, 'alto')
    if sign == 'percussion':
        return 'percussion'
    return 'treble'


def _pitch(p):
    octv = p.octave if p.octave is not None else p.implicitOctave
    alter = int(round(p.alter)) if p.accidental is not None else 0
    return (p.step, alter, octv)


def _is_hidden(el):
    try:
        return bool(el.style.hideObjectOnPrint)
    except Exception:
        return False


def _dur_events(el, base: Event):
    """Return list of Events for a music21 note/rest with tuplets/complex split."""
    d = el.duration
    ql = F(d.quarterLength).limit_denominator(10000)
    if ql == 0:
        return []
    if d.type not in ('complex', 'inexpressible', 'zero') and d.type in TYPE_QL:
        exp = display_ql(d.type, d.dots)
        if d.tuplets and len(d.tuplets) == 1:
            t = d.tuplets[0]
            exp = exp * t.numberNotesNormal / t.numberNotesActual
        if exp != ql and abs(exp - ql) <= max(F(1, 50), ql / 40):
            ql = exp          # sloppy encoder durations (e.g. 85/256 for 1/3)
    if d.tuplets and len(d.tuplets) == 1 and d.type not in ('complex', 'inexpressible', 'zero'):
        t = d.tuplets[0]
        tup = (t.numberNotesActual, t.numberNotesNormal)
        ev = _clone(base)
        ev.dur, ev.dtype, ev.dots, ev.tuplet = ql, d.type, d.dots, tup
        ev.tuplet_start = t.type in ('start', 'startStop')
        ev.tuplet_stop = t.type in ('stop', 'startStop')
        return [ev]
    if d.type not in ('complex', 'inexpressible', 'zero') and not d.tuplets:
        if display_ql(d.type, d.dots) == ql:
            ev = _clone(base)
            ev.dur, ev.dtype, ev.dots = ql, d.type, d.dots
            return [ev]
    # complex: split into components (plain durations), tie notes together
    from .model import split_plain
    comps = split_plain(ql)
    out = []
    for k, (t, dots, cq) in enumerate(comps):
        ev = _clone(base)
        ev.dur, ev.dtype, ev.dots = cq, t, dots
        if base.kind == 'note':
            if k > 0:
                ev.lyrics = {}
                ev.dynamics = []
                ev.slur_start = 0
                ev.tie_stop = set(ev.pitches)
            if k < len(comps) - 1:
                ev.tie_start = set(ev.pitches)
                ev.fermata = False
                ev.slur_stop = 0
            if k == 0:
                ev.tie_stop = set(base.tie_stop)
            if k == len(comps) - 1:
                ev.tie_start = set(base.tie_start)
        out.append(ev)
    return out


def _clone(ev: Event) -> Event:
    import copy
    return copy.deepcopy(ev)


def _barline(bl):
    if bl is None:
        return None
    if isinstance(bl, m21.bar.Repeat):
        return 'repeat-start' if bl.direction == 'start' else 'repeat-end'
    t = bl.type
    if t in ('final', 'light-heavy'):
        return 'final'
    if t in ('double', 'light-light'):
        return 'double'
    if t == 'dashed':
        return 'dashed'
    if t == 'heavy-light':
        return 'repeat-start-plain'
    return None


def from_music21(s, part_spec=None, verse_map=None):
    """part_spec: list of dicts {src:[part indices (staves)], id, name, abbr, instrument}.
    Default: consecutive PartStaffs with equal names are grouped."""
    src_parts = list(s.parts)
    if part_spec is None:
        part_spec = []
        i = 0
        n = 1
        while i < len(src_parts):
            p = src_parts[i]
            idxs = [i]
            if isinstance(p, m21.stream.PartStaff):
                j = i + 1
                while j < len(src_parts) and isinstance(src_parts[j], m21.stream.PartStaff) and \
                        src_parts[j].partName == p.partName:
                    idxs.append(j)
                    j += 1
            part_spec.append({'src': idxs, 'id': f'P{n}', 'name': p.partName or f'Part {n}',
                              'abbr': p.partAbbreviation or '',
                              'instrument': 'piano' if len(idxs) > 1 else 'voice'})
            n += 1
            i = idxs[-1] + 1

    meas_lists = [list(p.getElementsByClass('Measure')) for p in src_parts]
    nmeas = min(len(ml) for ml in meas_lists)
    score = Score()
    md = s.metadata
    if md is not None:
        score.title = md.title or md.movementName or ''
        score.composer = md.composer or ''
        try:
            score.lyricist = md.lyricist or ''
        except Exception:
            pass

    # slur endpoints
    slur_starts, slur_stops = {}, {}
    for sp in s.spannerBundle:
        if 'Slur' in sp.classes:
            els = sp.getSpannedElements()
            if len(els) >= 2:
                a, b = els[0], els[-1]
                slur_starts[id(a)] = slur_starts.get(id(a), 0) + 1
                slur_stops[id(b)] = slur_stops.get(id(b), 0) + 1

    # --- global measure info from first source part
    ts_cur, ks_cur = None, None
    minfo = []
    first = meas_lists[0]
    for i in range(nmeas):
        m = first[i]
        ts = m.timeSignature
        if ts is None:
            tss = list(m.getElementsByClass('TimeSignature'))
            ts = tss[0] if tss else None
        ks = m.keySignature
        if ks is None:
            kss = list(m.getElementsByClass('KeySignature'))
            ks = kss[0] if kss else None
        mi = MeasureInfo(number=i + 1, dur=F(0), nominal=F(0))
        if ts is not None and (ts_cur is None or ts.ratioString != ts_cur.ratioString):
            mi.time = (ts.numerator, ts.denominator)
            mi.time_symbol = ts.symbol if ts.symbol in ('common', 'cut') else None
            ts_cur = ts
        if ks is not None and (ks_cur is None or ks.sharps != ks_cur.sharps):
            mode = getattr(ks, 'mode', None) or 'major'
            mi.key = (ks.sharps, mode if mode in ('major', 'minor') else 'major')
            ks_cur = ks
        if ts_cur is None:
            mi.time = (4, 4)
            ts_cur = m21.meter.TimeSignature('4/4')
        if ks_cur is None and i == 0:
            mi.key = (0, 'major')
        mi.nominal = F(ts_cur.barDuration.quarterLength).limit_denominator(1000)
        # barlines: take from any part that has them
        lb = rb = None
        for ml in meas_lists:
            lb = lb or _barline(ml[i].leftBarline)
            rb = rb or _barline(ml[i].rightBarline)
        if lb == 'repeat-start-plain':
            lb = None
        mi.left_bar, mi.right_bar = lb, (rb if rb != 'repeat-start-plain' else None)
        minfo.append(mi)

    # verse numbering
    numbers = set()
    for p in src_parts:
        for n in p.recurse().notes:
            for l in n.lyrics:
                if l.text and clean_text(l.text):
                    numbers.add(l.number or 1)
    if verse_map is None:
        verse_map = {num: k + 1 for k, num in enumerate(sorted(numbers))}

    # --- build parts
    raw = []   # per model part: list over measures of dict vkey -> list of (offset, Event)
    model_parts = []
    for spec in part_spec:
        part = Part(id=spec['id'], name=spec.get('name', ''), abbr=spec.get('abbr', ''),
                    instrument=spec.get('instrument', 'voice'), staves=len(spec['src']))
        part.clefs = []
        vids_per_staff = []
        for sidx, pi in enumerate(spec['src']):
            ml = meas_lists[pi]
            c0 = None
            for c in src_parts[pi].recurse().getElementsByClass('Clef'):
                c0 = c
                break
            part.clefs.append(clef_name(c0) if c0 is not None else 'treble')
            ids = []
            for i in range(nmeas):
                for v in ml[i].voices:
                    if v.id not in ids:
                        ids.append(v.id)
            def k(x):
                try:
                    return (0, int(x))
                except Exception:
                    return (1, str(x))
            ids.sort(key=k)
            vids_per_staff.append(ids)
        # voice keys
        vmap = []
        for sidx, ids in enumerate(vids_per_staff):
            mp = {}
            base = 4 * sidx
            if not ids:
                mp[None] = str(base + 1)
            else:
                for j, vid in enumerate(ids):
                    mp[vid] = str(base + 1 + j)
                mp[None] = mp[ids[0]]
            vmap.append(mp)
            for key in dict.fromkeys(mp.values()):
                part.voices.append(VoiceDef(key=key, staff=sidx + 1))
        part_raw = []
        for i in range(nmeas):
            mdict = {}
            for sidx, pi in enumerate(spec['src']):
                m = meas_lists[pi][i]
                mp = vmap[sidx]
                containers = []
                if m.hasVoices():
                    for v in m.voices:
                        containers.append((mp.get(v.id, mp[None]), v))
                    loose = [e for e in m.notesAndRests]
                    if loose:
                        containers.append((mp[None], None))
                else:
                    containers.append((mp[None], m))
                for vkey, cont in containers:
                    els = cont.notesAndRests if cont is not None else m.notesAndRests
                    lst = mdict.setdefault(vkey, [])
                    for el in els:
                        if el.duration.isGrace:
                            continue
                        off = F(el.offset).limit_denominator(10000)
                        lst.extend(_convert(el, off, verse_map, slur_starts, slur_stops))
                # clef changes
                first_vkey = mp[None]
                for c in m.getElementsByClass('Clef'):
                    off = F(c.offset).limit_denominator(10000)
                    if i == 0 and off == 0:
                        part.clefs[sidx] = clef_name(c)
                        continue
                    mdict.setdefault(first_vkey, []).append((off, Event('clef', clef=clef_name(c))))
                # dynamics
                for dyn in m.recurse().getElementsByClass('Dynamic'):
                    val = dyn.value
                    if val not in DYN_OK:
                        continue
                    off = F(dyn.getOffsetInHierarchy(m)).limit_denominator(10000)
                    target = None
                    for vk in dict.fromkeys(mp.values()):
                        for o, ev in sorted(mdict.get(vk, []), key=lambda x: x[0]):
                            if ev.kind == 'note' and o >= off:
                                if target is None or o < target[0]:
                                    target = (o, ev)
                                break
                    if target:
                        target[1].dynamics.append(val)
            part_raw.append(mdict)
        raw.append(part_raw)
        model_parts.append(part)

    # --- sequence voices with exact durations (music21 offsets only used for
    # ordering and gap detection, which tolerates sloppy encoder offsets)
    TOL = F(1, 40)
    def snap(x):
        return F(round(x * 48), 48) if abs(x * 48 - round(x * 48)) < F(1, 4) else F(x).limit_denominator(240)
    seqs = []   # per part: list over measures of dict vkey -> list of events
    for part_raw in raw:
        pm = []
        for i in range(nmeas):
            md = {}
            for vkey, lst in part_raw[i].items():
                lst = sorted(lst, key=lambda x: (x[0], 0 if x[1].kind == 'clef' else 1))
                seq, t = [], F(0)
                for off, ev in lst:
                    if ev.kind == 'clef':
                        if off > t + TOL:
                            gap = snap(off - t)
                            seq.append(Event('space', gap))
                            t += gap
                        seq.append(ev)
                        continue
                    if ev.kind == 'space':
                        continue
                    if off > t + TOL:
                        gap = snap(off - t)
                        seq.append(Event('space', gap))
                        t += gap
                    elif off < t - TOL:
                        continue          # overlapping event (encoding error) dropped
                    seq.append(ev)
                    t += ev.dur
                md[vkey] = seq
            pm.append(md)
        seqs.append(pm)

    def real_end(seq):
        t, end = F(0), F(0)
        for e in seq:
            t += e.dur
            if e.kind in ('note', 'rest'):
                end = t
        return end

    def lead_space(seq):
        t = F(0)
        for e in seq:
            if e.kind in ('note', 'rest'):
                return t
            t += e.dur
        return None

    for i in range(nmeas):
        nominal = minfo[i].nominal
        allseq = [md[vk] for pm in seqs for md in [pm[i]] for vk in md]
        if i == 0:
            leads = [lead_space(sq) for sq in allseq]
            leads = [x for x in leads if x is not None]
            lead = min(leads) if leads else F(0)
            if lead > 0:
                for sq in allseq:
                    rem, k = lead, 0
                    while rem > 0 and k < len(sq):
                        x = sq[k]
                        if x.kind == 'clef':
                            k += 1
                            continue
                        if x.kind != 'space':
                            break
                        if x.dur <= rem:
                            rem -= x.dur
                            sq.pop(k)
                        else:
                            x.dur -= rem
                            rem = 0
        ends = [real_end(sq) for sq in allseq]
        end = max(ends) if ends and max(ends) > 0 else nominal
        minfo[i].dur = end
        if i == 0 and end < nominal:
            minfo[i].implicit = True
        for sq in allseq:
            # trim to measure end and drop trailing spaces
            t = F(0)
            keep = []
            for e in sq:
                if t >= end and e.kind != 'clef':
                    break
                if e.kind == 'space' and t + e.dur > end:
                    e.dur = end - t
                keep.append(e)
                t += e.dur
            while keep and keep[-1].kind == 'space':
                keep.pop()
            sq[:] = keep
    for part, pm in zip(model_parts, seqs):
        part.measures = pm
    score.measures = minfo
    score.parts = model_parts
    # merge measure-rest flags
    for p in score.parts:
        for i, m in enumerate(p.measures):
            for vkey, evs in m.items():
                real = [e for e in evs if e.kind != 'clef']
                if len(real) == 1 and real[0].kind == 'rest' and real[0].dur == score.measures[i].dur \
                        and score.measures[i].dur == score.measures[i].nominal:
                    real[0].measure_rest = True
                    real[0].dtype, real[0].dots = None, 0
    renumber(score)
    sanitize_ties(score)
    compute_extenders(score)
    return score


def _convert(el, off, verse_map, slur_starts, slur_stops):
    if isinstance(el, m21.note.Rest):
        if _is_hidden(el):
            return [(off, Event('space', F(el.duration.quarterLength).limit_denominator(10000)))]
        base = Event('rest')
        if any(isinstance(x, m21.expressions.Fermata) for x in el.expressions):
            base.fermata = True
        evs = _dur_events(el, base)
        return _offsets(off, evs)
    if _is_hidden(el):
        return [(off, Event('space', F(el.duration.quarterLength).limit_denominator(10000)))]
    base = Event('note')
    if isinstance(el, m21.chord.Chord):
        notes = list(el.notes)
    else:
        notes = [el]
    seen = set()
    for n in notes:
        p = _pitch(n.pitch)
        if p in seen:
            continue
        seen.add(p)
        base.pitches.append(p)
        tie = n.tie if n.tie is not None else (el.tie if isinstance(el, m21.chord.Chord) else None)
        if tie is not None:
            if tie.type in ('start', 'continue'):
                base.tie_start.add(p)
            if tie.type in ('stop', 'continue'):
                base.tie_stop.add(p)
    base.pitches.sort(key=lambda p: (p[2], 'CDEFGAB'.index(p[0]), p[1]))
    for l in el.lyrics:
        txt = clean_text(l.text or '')
        if not txt:
            continue
        num = verse_map.get(l.number or 1, l.number or 1)
        syl = l.syllabic or 'single'
        if syl == 'composite':
            syl = 'single'
        base.lyrics[num] = Lyric(txt, syl)
    if any(isinstance(x, m21.expressions.Fermata) for x in el.expressions):
        base.fermata = True
    for a in el.articulations:
        nm = type(a).__name__
        if nm == 'Staccato':
            base.artic.append('staccato')
        elif nm == 'Accent':
            base.artic.append('accent')
        elif nm == 'Tenuto':
            base.artic.append('tenuto')
    base.slur_start = slur_starts.get(id(el), 0)
    base.slur_stop = slur_stops.get(id(el), 0)
    return _offsets(off, _dur_events(el, base))


def _offsets(off, evs):
    out = []
    t = off
    for e in evs:
        out.append((t, e))
        t += e.dur
    return out
