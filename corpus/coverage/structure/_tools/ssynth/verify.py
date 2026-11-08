"""Truth-vs-engraving verification (coverage corpus, structure family).

The truth is re-read from truth.musicxml (ElementTree, independent of the writer) and compared with
what LilyPond actually engraved, recorded by ../dump.ly:
  * per Voice: notes (onset, MIDI pitch, duration log, dots, tuplet scale), rests, full-bar rests,
    ties, beams (start/end), slurs, articulations + fermatas, dynamics, hairpins, pedal, text
    scripts, explicit stem directions;
  * per Lyrics context: syllables, hyphens, extenders;
  * per Staff: clefs, key signatures, time signatures;
  * structure: bar-line glyph at every measure boundary per staff (double, final, repeat signs),
    volta brackets (text, start and end moment), segno / coda marks, text marks (To Coda, D.S.,
    D.C., Fine ...), rehearsal marks, metronome marks;
  * layout: the measures that start every system on every page, read with pdftotext from a second
    render of the same .ly whose bar numbers are tagged (QQ<n>QQ) and shown on every system.
"""
from __future__ import annotations

import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
DUMP = os.path.join(TOOLS, 'dump.ly')
BRK = os.path.join(TOOLS, 'breaks.ly')
LOG = {'breve': -1, 'whole': 0, 'half': 1, 'quarter': 2, 'eighth': 3, '16th': 4, '32nd': 5, '64th': 6}
STEP_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
ARTIC = {'staccato': 'staccato', 'accent': 'accent', 'tenuto': 'tenuto', 'staccatissimo': 'staccatissimo',
         'strong-accent': 'marcato'}
CLEF_LY = {('G', 2): ('clefs.G', -2), ('F', 4): ('clefs.F', 2), ('C', 3): ('clefs.C', 0),
           ('C', 4): ('clefs.C', 2), ('C', 1): ('clefs.C', -4), ('F', 3): ('clefs.F', 0),
           ('C', 2): ('clefs.C', -2), ('C', 5): ('clefs.C', 4)}


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def norm_text(s):
    return re.sub(r'\s+', ' ', s or '').strip()


# ------------------------------------------------------------------ truth.musicxml -> expectations

def read_truth(path):
    root = ET.parse(path).getroot()
    parts = [sp.get('id') for sp in root.find('part-list').findall('score-part')]
    names = {sp.get('id'): sp.findtext('part-name') for sp in root.find('part-list').findall('score-part')}
    T = {'parts': parts, 'names': names, 'voices': {}, 'lyrics': {}, 'staff_attr': {}, 'bars': {},
         'endings': [], 'marks': [], 'prints': [], 'measure_numbers': [], 'offsets': None}
    first = True
    for part in root.findall('part'):
        pid = part.get('id')
        div = 1
        t0 = F(0)
        offs = []
        staves = 1
        for mi, meas in enumerate(part.findall('measure')):
            offs.append(t0)
            pos = F(0)
            maxpos = F(0)
            last_onset = F(0)
            if first:
                T['measure_numbers'].append(meas.get('number'))
                pr = meas.find('print')
                if pr is not None and (pr.get('new-system') == 'yes' or pr.get('new-page') == 'yes'):
                    T['prints'].append((mi, 'page' if pr.get('new-page') == 'yes' else 'system'))
            for el in meas:
                tag = el.tag
                t = t0 + pos
                if tag == 'attributes':
                    if el.find('divisions') is not None:
                        div = int(el.findtext('divisions'))
                    if el.find('staves') is not None:
                        staves = int(el.findtext('staves'))
                    for k in el.findall('key'):
                        for s in range(1, staves + 1):
                            T['staff_attr'].setdefault((pid, s), []).append(('key', t, int(k.findtext('fifths'))))
                    for tm in el.findall('time'):
                        n, d = int(tm.findtext('beats')), int(tm.findtext('beat-type'))
                        style = None
                        if (n, d) in ((4, 4), (2, 2)):
                            style = 'C' if tm.get('symbol') in ('common', 'cut') else 'numbered'
                        for s in range(1, staves + 1):
                            T['staff_attr'].setdefault((pid, s), []).append(('timesig', t, n, d, style))
                    for c in el.findall('clef'):
                        s = int(c.get('number', '1'))
                        sign, line = c.findtext('sign'), int(c.findtext('line'))
                        oc = int(c.findtext('clef-octave-change') or 0)
                        g, ps = CLEF_LY[(sign, line)]
                        T['staff_attr'].setdefault((pid, s), []).append(('clef', t, g, ps, 7 * oc))
                elif tag == 'backup':
                    pos -= F(int(el.findtext('duration')), div)
                elif tag == 'forward':
                    pos += F(int(el.findtext('duration')), div)
                    maxpos = max(maxpos, pos)
                elif tag == 'barline':
                    loc = el.get('location', 'right')
                    st = el.findtext('bar-style')
                    rep = el.find('repeat')
                    T['bars'].setdefault(pid, {}).setdefault(mi, {})[loc] = (st, rep.get('direction') if rep is not None else None)
                    for en in el.findall('ending'):
                        T['endings'].append((pid, mi, en.get('number'), en.get('type'), norm_text(en.text)))
                elif tag == 'direction':
                    voice = el.findtext('voice')
                    staff = el.findtext('staff')
                    T['ndir'] = T.get('ndir', 0) + 1
                    for dt in el.findall('direction-type'):
                        for x in dt:
                            if voice is None:
                                T['marks'].append((pid, mi, t, x.tag, norm_text(x.text) if x.text else '',
                                                   T['ndir'], _metronome(x)))
                            else:
                                key = (pid, voice)
                                v = T['voices'].setdefault(key, [])
                                if x.tag == 'dynamics':
                                    for d in x:
                                        v.append(('dyn', t, d.tag))
                                elif x.tag == 'wedge':
                                    typ = x.get('type')
                                    if typ == 'crescendo':
                                        v.append(('cresc', t, -1))
                                    elif typ == 'diminuendo':
                                        v.append(('decresc', t, -1))
                                    else:
                                        v.append(('hairpin-stop', t))
                                elif x.tag == 'pedal':
                                    v.append(('sustain', t, -1 if x.get('type') == 'start' else 1))
                                elif x.tag == 'words':
                                    v.append(('textscript', t, norm_text(x.text)))
                elif tag == 'note':
                    if el.find('grace') is not None:
                        raise ValueError('grace notes not supported by this verifier')
                    chord = el.find('chord') is not None
                    dur = F(int(el.findtext('duration')), div)
                    onset = last_onset if chord else t
                    if not chord:
                        last_onset = t
                    voice = el.findtext('voice') or '1'
                    key = (pid, voice)
                    v = T['voices'].setdefault(key, [])
                    tm = el.find('time-modification')
                    scale = F(int(tm.findtext('normal-notes')), int(tm.findtext('actual-notes'))) if tm is not None else F(1)
                    typ = el.findtext('type')
                    dots = len(el.findall('dot'))
                    rest = el.find('rest')
                    if rest is not None:
                        if rest.get('measure') == 'yes':
                            v.append(('mmrest', onset, dur))
                        else:
                            v.append(('rest', onset, LOG[typ], dots, scale))
                    else:
                        p = el.find('pitch')
                        m = 12 * (int(p.findtext('octave')) + 1) + STEP_PC[p.findtext('step')] + int(float(p.findtext('alter') or 0))
                        v.append(('note', onset, m, LOG[typ], dots, scale))
                        if not chord:
                            if any(ti.get('type') == 'start' for ti in el.findall('tie')):
                                v.append(('tie', onset))
                            stem = el.findtext('stem')
                            if stem in ('up', 'down'):
                                v.append(('stem', onset, 1 if stem == 'up' else -1))
                            for b in el.findall('beam'):
                                if b.get('number') == '1' and b.text in ('begin', 'end'):
                                    v.append(('beam', onset, -1 if b.text == 'begin' else 1))
                        elif any(ti.get('type') == 'start' for ti in el.findall('tie')):
                            v.append(('tie', onset))
                    if not chord:
                        nots = el.find('notations')
                        if nots is not None:
                            for s in nots.findall('slur'):
                                v.append(('slur', onset, -1 if s.get('type') == 'start' else 1))
                            if nots.find('fermata') is not None:
                                v.append(('artic', onset, 'fermata'))
                            ar = nots.find('articulations')
                            if ar is not None:
                                for a in ar:
                                    v.append(('artic', onset, ARTIC[a.tag]))
                        for ly in el.findall('lyric'):
                            lk = (pid, voice, ly.get('number'))
                            L = T['lyrics'].setdefault(lk, [])
                            L.append(('lyric', onset, ly.findtext('text')))
                            if ly.findtext('syllabic') in ('begin', 'middle'):
                                L.append(('hyphen', onset))
                            elif ly.find('extend') is not None:
                                L.append(('extender', onset))
                    if not chord:
                        pos += dur
                        maxpos = max(maxpos, pos)
            t0 += maxpos
        offs.append(t0)
        if T['offsets'] is None:
            T['offsets'] = offs
        elif T['offsets'] != offs:
            raise ValueError(f'part {pid} measure offsets differ from the first part')
        first = False
    # dedupe voice records that are per-event but emitted per chord note
    for k, v in T['voices'].items():
        T['voices'][k] = _dedupe_ties(v)
    return T


def _metronome(x):
    if x.tag != 'metronome':
        return None
    return (x.findtext('beat-unit'), x.find('beat-unit-dot') is not None, x.findtext('per-minute'))


def _dedupe_ties(v):
    out, seen = [], set()
    for r in v:
        if r[0] == 'tie':
            if r in seen:
                continue
            seen.add(r)
        out.append(r)
    return out


def expected_barlines(T):
    """{pid: [(t, glyph)]} for every boundary whose glyph is not a plain '|'"""
    out = {}
    offs = T['offsets']
    n = len(offs) - 1
    breaks = {mi for mi, _ in T['prints']}
    for pid in T['parts']:
        bars = T['bars'].get(pid, {})
        res = []
        for k in range(n):
            right = bars.get(k, {}).get('right', (None, None))
            left_next = bars.get(k + 1, {}).get('left', (None, None)) if k + 1 < n else (None, None)
            back = right[1] == 'backward'
            fwd = left_next[1] == 'forward'
            st = right[0]
            if back and fwd:
                g = ':|.|:'
            elif back:
                g = ':|.'
            elif fwd:
                g = {'light-light': '.|:-||', 'light-heavy': '.|:-|.', None: '.|:-|', 'regular': '.|:-|'}.get(st)
                if g is None:
                    raise ValueError(f'unsupported bar combination {st} + forward repeat at measure {k}')
                if st in ('light-light', 'light-heavy') and (k + 1) not in breaks:
                    raise ValueError(f'{st} + forward repeat mid-system at measure {k}: double bar not visible')
            elif st == 'light-heavy':
                g = '|.'
            elif st == 'light-light':
                g = '||'
            elif st in (None, 'regular'):
                g = None
            else:
                raise ValueError(f'unsupported bar-style {st}')
            if g:
                res.append((offs[k + 1], g))
        first_left = bars.get(0, {}).get('left', (None, None))
        if first_left[1] == 'forward':
            res.append((offs[0], '.|:'))
        out[pid] = res
    return out


def expected_voltas(T):
    """[(text, start_t, end_t)] from the first part's endings"""
    offs = T['offsets']
    pid0 = T['parts'][0]
    opened = {}
    res = []
    for pid, mi, num, typ, text in T['endings']:
        if pid != pid0:
            continue
        if typ == 'start':
            opened[num] = (mi, text)
        else:
            s, txt = opened.pop(num)
            res.append((txt, offs[s], offs[mi + 1]))
    if opened:
        raise ValueError(f'unclosed endings {opened}')
    return res


# LilyPond 2.24 draws the closing hook of a volta bracket according to the name of the bar line glyph
# that ends it (checked empirically, also at line breaks): MusicXML type="stop" = hook, "discontinue" = open
HOOKED = {'|.', ':|.', ':|.|:', ':|.:', '.|:-|', '.|:-|.'}
OPEN = {'|', '||', '.|:', '.|:-||'}


def check_volta_hooks(T):
    eb = dict(expected_barlines(T)[T['parts'][0]])
    offs = T['offsets']
    res = []
    for pid, mi, num, typ, text in T['endings']:
        if pid != T['parts'][0] or typ == 'start':
            continue
        g = eb.get(offs[mi + 1], '|')
        if g not in HOOKED | OPEN:
            res.append((mi, num, typ, g, 'unknown glyph'))
        elif (typ == 'stop') != (g in HOOKED):
            res.append((mi, num, typ, g, 'hook mismatch'))
    return {'ok': not res, 'errors': [str(r) for r in res]}


def expected_marks(T):
    out = []
    pid0 = T['parts'][0]
    words_dirs = {d for pid, mi, t, tag, text, d, metro in T['marks'] if tag == 'words'}
    for pid, mi, t, tag, text, did, metro in T['marks']:
        if pid != pid0:
            continue
        if tag == 'segno':
            out.append(('SegnoMark', t))
        elif tag == 'coda':
            # a <coda/> in the same direction as words ("To Coda" + sign) is part of that text mark
            if did not in words_dirs:
                out.append(('CodaMark', t))
        elif tag == 'rehearsal':
            out.append(('RehearsalMark', t, text))
        elif tag == 'words':
            out.append(('words', t, text))
        elif tag == 'metronome':
            out.append(('metronome', t, metro[2]))
    return out


def expected_layout(T):
    """list of pages, each a list of measure numbers that start a system"""
    nums = T['measure_numbers']
    pages = [[nums[0]]]
    for mi, kind in T['prints']:
        if mi == 0:
            continue
        if kind == 'page':
            pages.append([nums[mi]])
        else:
            pages[-1].append(nums[mi])
    return pages


# ------------------------------------------------------------------ dump parsing

def parse_events(path):
    out = []
    for line in open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 7:
            continue
        ctype, cid, mom, gr, bar, mpos, kind = f[:7]
        out.append({'ctype': ctype, 'id': cid, 't': F(mom) * 4, 'g': F(gr) * 4, 'bar': bar, 'kind': kind,
                    'args': f[7:]})
    return out


def _dur(a):
    log, dots, scale = a.split()
    return int(log), int(dots), F(scale)


def got_voice(recs, vid):
    out = []
    for r in recs:
        if r['ctype'] == 'Voice' and r['id'] == vid:
            k, t, a = r['kind'], r['t'], r['args']
            if k == 'note':
                lg, d, s = _dur(a[1])
                out.append(('note', t, int(a[0]), lg, d, s))
            elif k == 'rest':
                lg, d, s = _dur(a[0])
                out.append(('rest', t, lg, d, s))
            elif k == 'mmrest':
                lg, d, s = _dur(a[0])
                base = F(4) / (F(2) ** lg)
                out.append(('mmrest', t, base * (2 - F(1, 2 ** d)) * s))
            elif k == 'tie':
                out.append(('tie', t))
            elif k in ('beam', 'slur', 'cresc', 'decresc', 'sustain'):
                sd = int(a[0])
                if k == 'cresc' and sd == 1:
                    out.append(('hairpin-stop', t))
                else:
                    out.append((k, t, sd))
            elif k == 'artic':
                out.append(('artic', t, a[0]))
            elif k == 'dyn':
                out.append(('dyn', t, a[0]))
            elif k == 'textscript':
                out.append(('textscript', t, norm_text(a[0])))
        elif r['ctype'] == 'Score' and r['kind'] == 'stem' and r['args'][0] == vid:
            out.append(('stem', r['t'], int(r['args'][1])))
    # whole notes / breves have no stem in the truth; LilyPond still creates an invisible Stem grob
    # (with a forced direction under \voiceOne etc.)
    # (rests get an invisible Stem grob too in LilyPond 2.24)
    stemmed = {x[1] for x in out if x[0] == 'note' and x[3] >= 1}
    out = [x for x in out if not (x[0] == 'stem' and x[1] not in stemmed)]
    return _dedupe_ties(out)


def got_lyrics(recs, lid):
    out = []
    for r in recs:
        if r['ctype'] == 'Lyrics' and r['id'] == lid:
            if r['kind'] == 'lyric' and r['args'][0].strip():
                out.append(('lyric', r['t'], r['args'][0]))
            elif r['kind'] in ('hyphen', 'extender'):
                out.append((r['kind'], r['t']))
    return out


def got_staff(recs, sid):
    out = []
    for r in recs:
        if r['ctype'] == 'Staff' and r['id'] == sid:
            a = r['args']
            if r['kind'] == 'timesig':
                n, d = int(a[0]), int(a[1])
                out.append(('timesig', r['t'], n, d, a[2] if (n, d) in ((4, 4), (2, 2)) else None))
            elif r['kind'] == 'clef':
                out.append(('clef', r['t'], a[0], int(a[1]), int(a[2])))
            elif r['kind'] == 'key':
                out.append(('key', r['t'], int(a[0])))
    return out


def _diff(exp, got, limit=12):
    ce, cg = Counter(exp), Counter(got)
    miss, extra = ce - cg, cg - ce
    return {'ok': not miss and not extra, 'n_expected': sum(ce.values()), 'n_got': sum(cg.values()),
            'missing': [str(x) for x in sorted(miss.elements(), key=str)[:limit]],
            'extra': [str(x) for x in sorted(extra.elements(), key=str)[:limit]]}


def compare(truth_path, events_path, staff_map, break_pages):
    """staff_map: {lilypond staff id: (part id, staff number)}; break_pages: from the tagged render"""
    T = read_truth(truth_path)
    recs = parse_events(events_path)
    rep = {'voices': {}, 'lyrics': {}, 'staves': {}, 'barlines': {}, 'voltas': None, 'marks': None,
           'layout': None}
    ok = True
    for (pid, voice), exp in T['voices'].items():
        vid = f'v{pid}x{voice}'
        exp_n = [r for r in exp]
        d = _diff(exp_n, got_voice(recs, vid))
        rep['voices'][vid] = d
        ok &= d['ok']
    for (pid, voice, num), exp in T['lyrics'].items():
        lid = f'L{pid}x{voice}x{num}'
        d = _diff(exp, got_lyrics(recs, lid))
        rep['lyrics'][lid] = d
        ok &= d['ok']
    # every Voice / Lyrics context that produced events must be in the truth
    for vid in {r['id'] for r in recs if r['ctype'] == 'Voice'}:
        if vid not in rep['voices'] and any(x[0] in ('note', 'rest', 'mmrest') for x in got_voice(recs, vid)):
            rep['voices'][vid] = {'ok': False, 'error': 'engraved voice missing from truth'}
            ok = False
    for lid in {r['id'] for r in recs if r['ctype'] == 'Lyrics'}:
        if lid not in rep['lyrics'] and got_lyrics(recs, lid):
            rep['lyrics'][lid] = {'ok': False, 'error': 'engraved lyrics missing from truth'}
            ok = False
    # clefs / keys / times per staff
    for sid, (pid, sn) in staff_map.items():
        d = _diff(T['staff_attr'].get((pid, sn), []), got_staff(recs, sid))
        rep['staves'][sid] = d
        ok &= d['ok']
    # bar lines per staff
    eb = expected_barlines(T)
    for sid, (pid, sn) in staff_map.items():
        got = [(r['t'], r['args'][1]) for r in recs if r['kind'] == 'barline' and r['args'][0] == sid
               and r['args'][1] not in ('|', '', '()')]
        d = _diff(eb[pid], got)
        rep['barlines'][sid] = d
        ok &= d['ok']
    # voltas
    gv = [(norm_text(r['args'][0]), F(r['args'][1]) * 4, F(r['args'][2]) * 4) for r in recs if r['kind'] == 'voltaspan']
    d = _diff(expected_voltas(T), gv)
    d['hooks'] = check_volta_hooks(T)
    d['ok'] = d['ok'] and d['hooks']['ok']
    rep['voltas'] = d
    ok &= d['ok']
    # marks
    gm = []
    for r in recs:
        if r['ctype'] != 'Score':
            continue
        k = r['kind']
        if k in ('SegnoMark', 'CodaMark'):
            gm.append((k, r['t']))
        elif k == 'RehearsalMark':
            gm.append((k, r['t'], norm_text(r['args'][0]).strip('[]')))
        elif k == 'TextMark':
            # the coda glyph inside "To Coda" markup is \musicglyph "scripts.coda" (the truth's <coda/>)
            gm.append(('words', r['t'], norm_text(r['args'][0].replace('scripts.coda', ''))))
        elif k == 'MetronomeMark':
            if norm_text(r['args'][0]) not in ('', '()'):
                gm.append(('words', r['t'], norm_text(r['args'][0])))
            if r['args'][1] not in ('', '()', '#f'):
                gm.append(('metronome', r['t'], r['args'][1]))
    d = _diff(expected_marks(T), gm)
    rep['marks'] = d
    ok &= d['ok']
    # systems and pages
    exp_pages = expected_layout(T)
    d = {'ok': exp_pages == break_pages, 'expected': exp_pages, 'got': break_pages}
    rep['layout'] = d
    ok &= d['ok']
    rep['ok'] = bool(ok)
    return rep, T


def break_render(ly_path, workdir):
    """render the same .ly with tagged bar numbers on every system; return [[measure numbers]] per page"""
    base = 'breakcheck'
    rc, out, err = run(['lilypond', '-dno-point-and-click', f'-dinclude-settings={BRK}', '-o', base,
                        os.path.basename(ly_path)], cwd=workdir)
    if rc != 0:
        raise RuntimeError('break render failed: ' + err[-1500:])
    pdf = os.path.join(workdir, base + '.pdf')
    rc, info, _ = run(['pdfinfo', pdf])
    n = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    pages = []
    for p in range(1, n + 1):
        rc, txt, _ = run(['pdftotext', '-bbox', '-f', str(p), '-l', str(p), pdf, '-'])
        # the tag can be clipped at the left page edge; the trailing QQ always survives
        words = re.findall(r'<word xMin="([-\d.]+)" yMin="([-\d.]+)"[^>]*>Q*(-?\d+)QQ</word>', txt)
        words.sort(key=lambda w: (float(w[1]), float(w[0])))
        pages.append([w[2] for w in words])
    return pages
