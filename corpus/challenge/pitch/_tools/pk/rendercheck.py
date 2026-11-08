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


def check(score, layout, rows):
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
        want = [(F(0), CLEF_GLYPH[st['clef']])]
        for pid, vk in voices:
            t = F(0)
            for i, m in enumerate(score.part(pid).measures):
                t = offs[i]
                for ev in m.get(vk, []):
                    if ev.kind == 'clef':
                        c = (t, CLEF_GLYPH[ev.clef])
                        if c not in want:
                            want.append(c)
                    t += ev.dur
        want.sort(key=lambda x: x[0])
        seq = []
        for w_ in want:
            if not seq or seq[-1][1] != w_[1]:
                seq.append(w_)
        gl = sorted({(F(r['when']) * 4, (r['data'][0].replace('_change', ''), int(r['data'][1])))
                     for r in rows if r['tag'] == 'Clef' and r['staff'] == sid and r['data'][2] != -1},
                    key=lambda x: x[0])
        gseq = []
        for g in gl:
            if not gseq or gseq[-1][1] != g[1]:
                gseq.append(g)
        clef_res[sid] = {'expected_changes': len(seq) - 1, 'rendered_changes': len(gseq) - 1}
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
        pieces = sorted((F(r['when']) * 4, F(r['data'][0]) * 4) for r in rows
                        if r['tag'] == 'OttavaBracket' and r['staff'] == sid)
        merged = []
        for a, b in pieces:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        wsp = sorted((a, b) for a, b, _n in spans)
        ott_res[sid] = {'expected': [f'{a}-{b}' for a, b in wsp], 'rendered': [f'{a}-{b}' for a, b in merged],
                        'pieces': len(pieces)}
        if wsp != merged:
            res['ok'] = False
            res['problems'].append(f'ottava mismatch on {sid}: exp {wsp} got {merged}')
    res['ottava'] = ott_res
    return res
