"""Truth-vs-render check for pitch notation.

Parses the PKLOG lines printed by the instrumented engraving (see lily.INSTR_SCM) and
compares, per engraved staff:
  * printed accidentals   (moment, pitch) -> glyph / extra natural / parentheses
                           vs. acc.simulate() on the *engraved* staves
  * clef changes          vs. clef events of the model
  * key signatures        vs. model key changes (fifths) and key cancellations
  * ottava brackets       vs. model ottava spans
The MIDI attack check (midicheck.compare) separately proves the sounding pitches.
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .acc import key_cancel_steps, layout_staves, simulate
from .model import STEPS

CLEF_MOD = {'treble_8': -1, 'treble^8': 1, 'bass_8': -1}
OTT_TEXT = {'ordinals': {1: '8va', -1: '8vb', 2: '15ma', -2: '15mb'},
            'numbers': {1: '8', -1: '8', 2: '15', -2: '15'}}
CLEF_GLYPH = {'treble': ('clefs.G', -2), 'treble_8': ('clefs.G', -2), 'treble^8': ('clefs.G', -2),
              'bass': ('clefs.F', 2), 'bass_8': ('clefs.F', 2), 'alto': ('clefs.C', 0), 'tenor': ('clefs.C', 2),
              'soprano': ('clefs.C', -4), 'mezzosoprano': ('clefs.C', -2), 'baritone': ('clefs.C', 4)}


# --------------------------------------------------------------- tiny s-expression reader

def _tokens(s):
    return re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', s)


def _parse(toks, i=0):
    if toks[i] == '(':
        out = []
        i += 1
        while toks[i] != ')':
            if toks[i] == '.':
                i += 1
                v, i = _parse(toks, i)
                out = (out[0], v) if len(out) == 1 else (tuple(out), v)
                continue
            v, i = _parse(toks, i)
            out.append(v)
        return out, i + 1
    t = toks[i]
    if t.startswith('"'):
        return t[1:-1], i + 1
    if t == '#f':
        return False, i + 1
    if t == '#t':
        return True, i + 1
    if re.fullmatch(r'-?\d+(/\d+)?', t):
        return F(t), i + 1
    return t, i + 1


def sexp(s):
    v, _ = _parse(_tokens(s))
    return v


def parse_log(stderr):
    rows = []
    for line in stderr.splitlines():
        if not line.startswith('PKLOG '):
            continue
        body = line[6:]
        toks = _tokens(body)
        staff, i = _parse(toks, 0)
        tag, i = _parse(toks, i)
        when, i = _parse(toks, i)
        data, i = _parse(toks, i)
        rows.append({'staff': staff, 'tag': str(tag), 'when': when, 'data': data})
    return rows


def _pitch(lp):
    octv, nn, alt = lp
    return (STEPS[int(nn)], int(F(alt) * 2), int(octv) + 4)


def _alist_fifths(al):
    if not al:
        return 0
    vals = [F(a) for (_n, a) in al]
    if all(v > 0 for v in vals):
        return len(vals)
    if all(v < 0 for v in vals):
        return -len(vals)
    return None


def check(score, layout, rows, ottava_style='numbers'):
    res = {'ok': True, 'problems': []}
    offs = score.measure_offsets()
    staves = layout_staves(layout)
    # line starts from clef grobs with break-dir 1 (start of system)
    ls_moments = sorted({F(r['when']) * 4 for r in rows if r['tag'] == 'Clef' and r['data'][2] == 1})
    line_start_measures = {i for i, o in enumerate(offs) if o in ls_moments}
    res['systems'] = len(ls_moments)
    res['line_start_measures'] = sorted(m + 1 for m in line_start_measures)

    # ---------------- accidentals
    dec, tls = simulate(score, staves, line_start_measures)
    exp = {}
    for d in dec.values():
        exp[(d['staff'], d['onset'], d['pitch'])] = (d['alter'], d['restore_first'], d['paren'])
    for t in tls:
        exp[(t['staff'], t['onset'], t['pitch'])] = (t['alter'], False, False)
    got = {}
    for r in rows:
        if r['tag'] not in ('Accidental', 'AccidentalCautionary'):
            continue
        lp, alt, glyph, rf, par = r['data']
        if lp is False:
            res['problems'].append(f'accidental without pitch at {r["when"]}')
            continue
        p = _pitch(lp)
        key = (r['staff'], F(r['when']) * 4, p)
        got[key] = (int(F(alt) * 2), bool(rf), bool(par))
    miss = sorted(set(exp) - set(got), key=str)
    extra = sorted(set(got) - set(exp), key=str)
    diff = sorted([k for k in set(exp) & set(got) if exp[k] != got[k]], key=str)
    res['accidentals'] = {'expected': len(exp), 'printed': len(got), 'missing': [str(x) for x in miss[:10]],
                          'extra': [str(x) for x in extra[:10]], 'different': [f'{k}: exp {exp[k]} got {got[k]}' for k in diff[:10]],
                          'extra_natural': sum(1 for v in got.values() if v[1]),
                          'parenthesized': sum(1 for v in got.values() if v[2]),
                          'double': sum(1 for v in got.values() if abs(v[0]) == 2),
                          'tie_at_line_start': len(tls)}
    if miss or extra or diff:
        res['ok'] = False
        res['problems'].append('accidental mismatch')

    # ---------------- clefs
    clef_res = {}
    for sid, voices in staves:
        st = next(s for g in layout['groups'] for s in g['staves'] if s['id'] == sid)
        def cg(name):
            return CLEF_GLYPH[name] + (CLEF_MOD.get(name, 0),)
        want = [(F(0), cg(st['clef']))]
        for pid, vk in voices:
            t = F(0)
            for i, m in enumerate(score.part(pid).measures):
                t = offs[i]
                for ev in m.get(vk, []):
                    if ev.kind == 'clef':
                        c = (t, cg(ev.clef))
                        if c not in want:
                            want.append(c)
                    t += ev.dur
        want.sort(key=lambda x: x[0])
        seq = []
        for w_ in want:
            if not seq or seq[-1][1] != w_[1]:
                seq.append(w_)
        mods = {(F(r['when']) * 4, int(r['data'][2])): (int(r['data'][1]) if r['data'][0] == '8' else 99)
                for r in rows if r['tag'] == 'ClefModifier' and r['staff'] == sid}
        gl = sorted({(F(r['when']) * 4, (r['data'][0].replace('_change', ''), int(r['data'][1]),
                                         mods.get((F(r['when']) * 4, int(r['data'][2])), 0)))
                     for r in rows if r['tag'] == 'Clef' and r['staff'] == sid and r['data'][2] != -1},
                    key=lambda x: x[0])
        gseq = []
        for g in gl:
            if not gseq or gseq[-1][1] != g[1]:
                gseq.append(g)
        clef_res[sid] = {'expected_changes': len(seq) - 1, 'rendered_changes': len(gseq) - 1,
                         'sequence': [f'{t}:{c[0]}@{c[1]}{"^8" if c[2] == 1 else "_8" if c[2] == -1 else ""}'
                                      for t, c in gseq]}
        if [(t, c) for t, c in seq] != [(t, c) for t, c in gseq]:
            res['ok'] = False
            res['problems'].append(f'clef sequence mismatch on {sid}: exp {seq} got {gseq}')
    res['clefs'] = clef_res

    # ---------------- keys
    key_res = {}
    want = []
    for i, mi in enumerate(score.measures):
        if mi.key or i == 0:
            want.append((offs[i], (mi.key or score.current_key(i))[0]))
    for sid, _v in staves:
        ks = {}
        for r in rows:
            if r['tag'] == 'KeySignature' and r['staff'] == sid and r['data'][1] != -1:
                ks[F(r['when']) * 4] = _alist_fifths(r['data'][0])
        seq = []
        for t in sorted(ks):
            if not seq or seq[-1][1] != ks[t]:
                seq.append((t, ks[t]))
        wseq = []
        for t, f in want:
            if not wseq or wseq[-1][1] != f:
                wseq.append((t, f))
        canc = {}
        for r in rows:
            if r['tag'] == 'KeyCancellation' and r['staff'] == sid:
                canc.setdefault(F(r['when']) * 4, set()).update(STEPS[int(n)] for n, _a in r['data'][0])
        wcanc = {}
        for k in range(1, len(wseq)):
            st_ = key_cancel_steps(wseq[k - 1][1], wseq[k][1])
            if st_:
                wcanc[wseq[k][0]] = set(st_)
        key_res[sid] = {'expected': [f'{t}:{f}' for t, f in wseq], 'rendered': [f'{t}:{f}' for t, f in seq],
                        'cancellations': {str(k): ''.join(sorted(v)) for k, v in canc.items()}}
        if seq != wseq or canc != wcanc:
            res['ok'] = False
            res['problems'].append(f'key mismatch on {sid}: exp {wseq} {wcanc} got {seq} {canc}')
    res['keys'] = key_res

    # ---------------- ottava
    ott_res = {}
    for sid, voices in staves:
        spans = []
        for pid, vk in voices:
            cur = None
            last_note = None
            for i, m in enumerate(score.part(pid).measures):
                t = offs[i]
                for ev in m.get(vk, []):
                    if ev.kind == 'ottava':
                        if cur is not None and last_note is not None:
                            spans.append((cur[0], last_note, cur[1]))
                        cur = (t, ev.ottava) if ev.ottava else None
                        last_note = None
                    elif ev.kind in ('note', 'rest') and cur is not None:
                        last_note = t
                    t += ev.dur
        pieces = sorted((F(r['when']) * 4, F(r['data'][0]) * 4, r['data'][1], int(r['data'][2])) for r in rows
                        if r['tag'] == 'OttavaBracket' and r['staff'] == sid)
        merged = []
        for a, b, txt, dr in pieces:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b), merged[-1][2], merged[-1][3])
            else:
                merged.append((a, b, txt, dr))
        tt = OTT_TEXT[ottava_style]
        wsp = sorted((a, b, tt[n], 1 if n > 0 else -1) for a, b, n in spans)
        ott_res[sid] = {'expected': [f'{a}-{b}:{t}{"^" if d > 0 else "_"}' for a, b, t, d in wsp],
                        'rendered': [f'{a}-{b}:{t}{"^" if d > 0 else "_"}' for a, b, t, d in merged],
                        'pieces': len(pieces)}
        if wsp != merged:
            res['ok'] = False
            res['problems'].append(f'ottava mismatch on {sid}: exp {wsp} got {merged}')
    res['ottava'] = ott_res

    # ---------------- time signatures (statements, not courtesy copies at line ends)
    wts = []
    for i, mi in enumerate(score.measures):
        if mi.time or i == 0:
            (tn, td), sym = score.current_time(i)
            wts.append((offs[i], tn, td, sym in ('common', 'cut') and (tn, td) in ((4, 4), (2, 2))))
    ts_res = {}
    for sid, _v in staves:
        got = {}
        for r in rows:
            if r['tag'] == 'TimeSignature' and r['staff'] == sid and r['data'][3] != -1:
                n, d, style = int(r['data'][0]), int(r['data'][1]), r['data'][2]
                got[F(r['when']) * 4] = (n, d, style == 'C' and (n, d) in ((4, 4), (2, 2)))
        seq = []
        for t in sorted(got):
            if not seq or seq[-1][1:] != got[t]:
                seq.append((t,) + got[t])
        ts_res[sid] = [f'{t}:{n}/{d}{"(sym)" if y else ""}' for t, n, d, y in seq]
        if seq != wts:
            res['ok'] = False
            res['problems'].append(f'time signature mismatch on {sid}: exp {wts} got {seq}')
    res['time_signatures'] = ts_res

    # ---------------- double / final barlines
    ends = [offs[i] + mi.dur for i, mi in enumerate(score.measures)]
    wbar = sorted((ends[i], {'double': '||', 'final': '|.'}[mi.right_bar]) for i, mi in enumerate(score.measures)
                  if mi.right_bar in ('double', 'final'))
    bl_res = {}
    for sid, _v in staves:
        got = sorted({(F(r['when']) * 4, r['data'][0]) for r in rows
                      if r['tag'] == 'BarLine' and r['staff'] == sid and r['data'][1] != 1
                      and r['data'][0] in ('||', '|.')})
        bl_res[sid] = len(got)
        if got != wbar:
            res['ok'] = False
            res['problems'].append(f'barline mismatch on {sid}: exp {wbar} got {got}')
    res['barlines'] = bl_res
    return res


# --------------------------------------------------------------- stems / beams / noteheads

def _side(x):
    if x is False or x is None:
        return set()
    return {int(v) for v in x}


def annotate_stems(score, layout, rows):
    """Copy the engraved stem direction and beaming of every note event into the model
    (ev.stem, ev.beams).  Returns a report; raises on any unmatched note or stem."""
    offs = score.measure_offsets()
    staves = layout_staves(layout)
    stems = {}
    for r in rows:
        if r['tag'] != 'Stem':
            continue
        dr, dlog, beaming, flag, heads = r['data']
        heads = [h for h in heads if h is not False]
        if not heads:
            continue          # rest stem placeholder
        key = (r['staff'], F(r['when']) * 4, frozenset(_pitch(h) for h in heads))
        if key in stems:
            raise RuntimeError(f'duplicate stem {key}')
        stems[key] = {'dir': int(dr), 'dlog': int(dlog),
                      'L': _side(beaming[0]) if beaming else set(), 'R': _side(beaming[1]) if beaming else set(),
                      'beamed': bool(beaming), 'flag': bool(flag), 'used': False}
    rep = {'stems': 0, 'up': 0, 'down': 0, 'beamed': 0, 'flags': 0, 'beam_groups': 0}
    for sid, voices in staves:
        for pid, vk in voices:
            seq = []
            for i, m in enumerate(score.part(pid).measures):
                t = offs[i]
                for ev in m.get(vk, []):
                    if ev.kind == 'note':
                        seq.append((t, ev))
                    t += ev.dur
            recs = []
            for t, ev in seq:
                ev.stem, ev.beams = None, {}
                st = stems.get((sid, t, frozenset(ev.pitches)))
                if st is None:
                    raise RuntimeError(f'no stem logged for {sid} {pid}:{vk} t={t} {ev.pitches}')
                st['used'] = True
                recs.append((ev, st))
            for k, (ev, st) in enumerate(recs):
                if st['dlog'] >= 1:
                    ev.stem = 'up' if st['dir'] > 0 else 'down'
                    rep['stems'] += 1
                    rep[ev.stem] += 1
                if st['flag']:
                    rep['flags'] += 1
                    if st['beamed'] or ev.dtype not in ('eighth', '16th', '32nd', '64th'):
                        raise RuntimeError(f'unexpected flag {sid} {ev.pitches}')
                if not st['beamed']:
                    if ev.dtype in ('eighth', '16th', '32nd', '64th') and not st['flag']:
                        raise RuntimeError(f'short note without flag or beam {sid} {ev.pitches}')
                    continue
                rep['beamed'] += 1
                prv = recs[k - 1][1] if k > 0 else None
                nxt = recs[k + 1][1] if k + 1 < len(recs) else None
                for lv in sorted(st['L'] | st['R']):
                    if lv < 0:
                        raise RuntimeError(f'negative beam index (knee) {sid} {ev.pitches}')
                    inl, inr = lv in st['L'], lv in st['R']
                    if inl and inr:
                        v = 'continue'
                    elif inr:
                        v = 'begin' if (nxt and lv in nxt['L']) else 'forward hook'
                    else:
                        v = 'end' if (prv and lv in prv['R']) else 'backward hook'
                    ev.beams[lv + 1] = v
                if ev.beams.get(1) == 'begin':
                    rep['beam_groups'] += 1
            # sanity: level-1 beams well formed
            open_ = False
            for ev, st in recs:
                b = ev.beams.get(1)
                if b == 'begin':
                    assert not open_, ('beam begin inside beam', sid)
                    open_ = True
                elif b in ('continue', 'end'):
                    assert open_, ('beam continue/end outside beam', sid, ev.pitches)
                    open_ = b == 'continue'
                elif st['beamed']:
                    raise RuntimeError(f'beamed stem without level-1 beam {sid} {ev.pitches}')
            assert not open_, ('unterminated beam', sid)
    unused = [k for k, v in stems.items() if not v['used']]
    if unused:
        raise RuntimeError(f'stems not matched to the model: {unused[:5]}')
    return rep


def notehead_positions(rows):
    """(staff, onset, pitch) -> engraved staff-position (half spaces from the middle line)"""
    out = {}
    for r in rows:
        if r['tag'] == 'NoteHead' and r['data'][0] is not False:
            out[(r['staff'], F(r['when']) * 4, _pitch(r['data'][0]))] = int(r['data'][1])
    return out
