"""Instrumented LilyPond run -> engraving facts -> merged into the model -> verified.

The instrumented twin of engraving.ly (lily.LilyWriter(instrument=True)) gives every note head
and rest a grob id (\\tweak id) and overrides after-line-breaking of the grob types listed in
lily.py so that every LIVE grob prints one line on stderr:

  COVLOG <staff> <grob-type> (<moment-main> <moment-grace>) <id> <original-address> <data>

harvest() turns that into
  * per note-head facts: sounding pitch + duration of the causing event, onset moment, staff
    position (-> ledger lines), stem direction, beam membership + beaming, live flag, printed
    accidental (glyph, parentheses, extra natural), dot count
  * per staff / score counts of every other symbol (scripts, dynamics, hairpins, pedals,
    fingerings, arpeggios, tremolo, breath marks, clefs, keys, time signatures, ottavas, tuplets,
    slurs, ties (and ties broken across a system), barlines, lyrics, stanza numbers,
    rehearsal / tempo / text marks, voltas)
merge() copies stem / beam / accidental / staff-position into the model events (written into
the truth by mxl.py) and verify() checks pitch, duration, onset of EVERY note and rest against
the model.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from fractions import Fraction as F

from .model import STEPS, Score, display_ql, midi

LOG2 = {'breve': -1, 'whole': 0, 'half': 1, 'quarter': 2, 'eighth': 3, '16th': 4, '32nd': 5, '64th': 6}

LOGGER_SCM = r"""
% ---- instrumentation (verification twin only; not part of the published engraving) ----
#(define (cov-mom g)
  (let* ((it (if (ly:spanner? g) (ly:spanner-bound g LEFT) g))
         (col (and (ly:item? it) (ly:item-get-column it))))
    (if col (let ((m (ly:grob-property col 'when))) (list (ly:moment-main m) (ly:moment-grace m))) #f)))
#(define (cov-ev g)
  (let ((c (ly:grob-property g 'cause)))
    (cond ((ly:stream-event? c) c)
          ((ly:grob? c) (cov-ev c))
          (else #f))))
#(define (cov-pitch ev)
  (let ((p (and ev (ly:event-property ev 'pitch #f))))
    (if (ly:pitch? p) (list (ly:pitch-octave p) (ly:pitch-notename p) (ly:pitch-alteration p)) #f)))
#(define (cov-dur ev)
  (let ((d (and ev (ly:event-property ev 'duration #f))))
    (if (ly:duration? d) (list (ly:duration-log d) (ly:duration-dot-count d) (ly:duration-scale d)) #f)))
#(define (cov-str x) (if (string? x) x #f))
#(define (cov-live g) (and (ly:grob? g) (grob::is-live? g)))
#(define (cov-addr g) (object-address (ly:grob-original g)))
#(define (cov-data tag grob ev)
  (case tag
    ((NoteHead)
      (let* ((st (ly:grob-object grob 'stem))
             (acc (ly:grob-object grob 'accidental-grob))
             (dot (ly:grob-object grob 'dot))
             (bm (and (ly:grob? st) (ly:grob-object st 'beam)))
             (fl (and (ly:grob? st) (ly:grob-object st 'flag))))
        (list (cov-pitch ev) (cov-dur ev) (ly:grob-property grob 'staff-position)
              (if (ly:grob? st) (ly:grob-property st 'direction) #f)
              (if (cov-live bm) (cov-addr bm) #f)
              (if (cov-live bm) (ly:grob-property st 'beaming #f) #f)
              (cov-live fl)
              (if (cov-live acc) (list (ly:grob-property acc 'glyph-name) (ly:grob-property acc 'parenthesized #f)
                                       (ly:grob-property acc 'restore-first #f) (ly:grob-property acc 'alteration #f)) #f)
              (if (cov-live dot) (ly:grob-property dot 'dot-count) 0)
              (if (and (ly:grob? st) (ly:grob-property st 'stencil #f)) #t #f))))
    ((Rest) (list (cov-dur ev) (let ((d (ly:grob-object grob 'dot))) (if (cov-live d) (ly:grob-property d 'dot-count) 0))))
    ((MultiMeasureRest) (list (ly:grob-property grob 'measure-count #f)))
    ((Accidental AccidentalCautionary) (list (ly:grob-property grob 'glyph-name) (ly:grob-property grob 'parenthesized #f)))
    ((Script) (list (and ev (ly:event-property ev 'articulation-type #f))))
    ((DynamicText) (list (and ev (cov-str (ly:event-property ev 'text #f)))))
    ((Hairpin) (list (ly:grob-property grob 'grow-direction #f)))
    ((SustainPedal) (list (cov-str (ly:grob-property grob 'text #f)) (and ev (ly:event-property ev 'span-direction #f))))
    ((Fingering) (list (and ev (ly:event-property ev 'digit #f))))
    ((StemTremolo) (list (ly:grob-property grob 'flag-count #f)))
    ((Clef) (list (ly:grob-property grob 'glyph-name) (ly:item-break-dir grob)))
    ((KeySignature KeyCancellation) (list (ly:grob-property grob 'alteration-alist) (ly:item-break-dir grob)))
    ((TimeSignature) (list (ly:grob-property grob 'fraction) (ly:grob-property grob 'style #f) (ly:item-break-dir grob)))
    ((OttavaBracket) (list (and ev (ly:event-property ev 'ottava-number #f)) (cov-mom (ly:spanner-bound grob RIGHT))))
    ((TupletBracket TupletNumber) (list (and ev (ly:event-property ev 'denominator #f)) (and ev (ly:event-property ev 'numerator #f))
                                       (let ((s (ly:grob-property grob 'stencil #f))) (and (ly:stencil? s) (not (ly:stencil-empty? s))))))
    ((BarLine) (list (cov-str (ly:grob-property grob 'glyph-name #f)) (ly:item-break-dir grob)))
    ((Tie Slur Beam LyricHyphen LyricExtender VoltaBracket)
      (list (length (ly:spanner-broken-into (ly:grob-original grob)))))
    ((LyricText StanzaNumber) (list (cov-str (ly:grob-property grob 'text #f))))
    ((RehearsalMark TextMark MetronomeMark VoltaBracket) (list))
    (else '())))
#(define (cov-logger tag staff)
  (let ((orig (assoc-get 'after-line-breaking (assoc-get tag all-grob-descriptions))))
   (lambda (grob)
    (if (procedure? orig) (orig grob))
    (if (grob::is-live? grob)
     (let ((ev (cov-ev grob)))
      (ly:message "COVLOG ~s ~s ~s ~s ~s ~s" staff tag (cov-mom grob) (ly:grob-property grob 'id #f)
                  (cov-addr grob) (cov-data tag grob ev)))))))
"""


# --------------------------------------------------------------- s-expression reader (from pitch/_tools/pk)

def _tokens(s):
    return re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|#<[^>]*>|[^\s()]+', s)


def _parse(toks, i=0):
    if toks[i] == '(':
        out = []
        i += 1
        dotted = False
        while toks[i] != ')':
            if toks[i] == '.':
                i += 1
                v, i = _parse(toks, i)
                out = (out[0] if len(out) == 1 else list(out), v)
                dotted = True
                continue
            v, i = _parse(toks, i)
            out.append(v)
        return (out if not dotted else ('PAIR',) + tuple(out)), i + 1
    t = toks[i]
    if t.startswith('"'):
        return bytes(t[1:-1], 'utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8', 'replace'), i + 1
    if t == '#f':
        return False, i + 1
    if t == '#t':
        return True, i + 1
    if re.fullmatch(r'-?\d+(/\d+)?', t):
        return F(t), i + 1
    if re.fullmatch(r'-?\d+\.\d*(e-?\d+)?', t):
        return float(t), i + 1
    return t, i + 1


def parse_log(stderr):
    rows = []
    for line in stderr.splitlines():
        if not line.startswith('COVLOG '):
            continue
        toks = _tokens(line[7:])
        i = 0
        vals = []
        while i < len(toks):
            v, i = _parse(toks, i)
            vals.append(v)
        staff, tag, mom, gid, addr, data = vals[:6]
        when = None
        if isinstance(mom, list):
            when = (F(mom[0]) * 4, F(mom[1]) * 4)
        rows.append({'staff': staff, 'tag': str(tag), 'when': when, 'id': gid if gid else None,
                     'addr': int(addr), 'data': data})
    return rows


def _beaming(b):
    """LilyPond stem 'beaming (left-list . right-list) -> (set, set)"""
    if b is False or b is None:
        return set(), set()
    if isinstance(b, tuple) and b and b[0] == 'PAIR':
        left, right = b[1], b[2]
    elif isinstance(b, list) and b:
        left, right = b[0], b[1:]
    else:
        return set(), set()
    # beam indices are signed (secondary beams of up-stems are numbered -1, -2 ...): level = |index|
    ls = set(abs(int(x)) for x in left) if isinstance(left, list) else set()
    rs = set(abs(int(x)) for x in right) if isinstance(right, list) else set()
    return ls, rs


def _lp_pitch(lp):
    octv, nn, alt = lp
    return (STEPS[int(nn)], int(F(alt) * 2), int(octv) + 4)


# --------------------------------------------------------------- model <-> ids

def assign_ids(score: Score):
    n = 0
    for p in score.parts:
        for i, m in enumerate(p.measures):
            for vk, evs in m.items():
                for ev in evs:
                    if ev.kind == 'note':
                        ev.ids = [f'n{n}.{j}' for j in range(len(ev.pitches))]
                        n += 1
                    elif ev.kind == 'rest':
                        ev.ids = [f'r{n}']
                        n += 1


def event_index(score: Score):
    """id -> (part, vkey, measure index, onset, event, pitch-or-None)"""
    idx = {}
    offs = score.measure_offsets()
    for p in score.parts:
        for v in p.voices:
            for i, m in enumerate(p.measures):
                t = offs[i]
                evs = m.get(v.key, [])
                for k, ev in enumerate(evs):
                    if ev.kind == 'note':
                        g = F(0)
                        if ev.grace:
                            j = k
                            while j < len(evs) and evs[j].grace:
                                g -= display_ql(evs[j].dtype, evs[j].dots)
                                j += 1
                        for pid_, pit in zip(ev.ids, ev.pitches):
                            idx[pid_] = (p, v.key, i, t, g, ev, pit)
                    elif ev.kind == 'rest':
                        idx[ev.ids[0]] = (p, v.key, i, t, F(0), ev, None)
                    t += ev.dur
    return idx


def harvest(rows):
    heads, rests = {}, {}
    for r in rows:
        if r['tag'] == 'NoteHead' and r['id']:
            d = r['data']
            heads[r['id']] = {
                'staff': r['staff'], 'when': r['when'], 'pitch': _lp_pitch(d[0]) if d[0] else None,
                'dur': tuple(d[1]) if d[1] else None, 'pos': int(d[2]),
                'stem': {1: 'up', -1: 'down'}.get(int(d[3]) if d[3] not in (False, None) else 0),
                'beam': d[4] if d[4] is not False else None, 'beaming': _beaming(d[5]),
                'flag': bool(d[6]),
                'acc': ({'glyph': d[7][0], 'paren': bool(d[7][1]), 'restore_first': bool(d[7][2])}
                        if d[7] else None),
                'dots': int(d[8]), 'stem_visible': bool(d[9])}
        elif r['tag'] in ('Rest', 'MultiMeasureRest') and r['id']:
            rests[r['id']] = {'staff': r['staff'], 'when': r['when'], 'tag': r['tag'], 'data': r['data']}
    return heads, rests


def merge(score: Score, heads):
    """copy engraving facts into the model events"""
    for p in score.parts:
        for m in p.measures:
            for evs in m.values():
                for ev in evs:
                    if ev.kind == 'note':
                        ev.hv = {i: heads.get(i) for i in ev.ids}


def beam_values(score: Score, heads):
    """per note id: list of (level, value) MusicXML beam values, from LilyPond's beams"""
    groups = defaultdict(list)
    for nid, h in heads.items():
        if h['beam'] is not None:
            groups[h['beam']].append((h['when'], nid))
    out = {}
    for addr, mem in groups.items():
        # one stem per chord: keep one id per moment (stems of a chord share beaming)
        by_t = {}
        for w, nid in sorted(mem):
            by_t.setdefault(w, []).append(nid)
        times = sorted(by_t)
        bm = [heads[by_t[t][0]]['beaming'] for t in times]
        for k, t in enumerate(times):
            L, R = bm[k]
            levels = sorted(L | R)
            vals = []
            for lv in levels:
                cl = lv in L and k > 0 and lv in bm[k - 1][1]
                cr = lv in R and k + 1 < len(times) and lv in bm[k + 1][0]
                if cl and cr:
                    v = 'continue'
                elif cr:
                    v = 'begin'
                elif cl:
                    v = 'end'
                elif lv in L:
                    v = 'backward hook'
                else:
                    v = 'forward hook'
                vals.append((lv + 1, v))
            for nid in by_t[t]:
                out[nid] = vals
    return out


def verify(score: Score, rows, heads, rests):
    """every model note / rest must appear with the same pitch, duration, onset (and grace
    offset) and on the expected staff; nothing unexpected may be engraved."""
    idx = event_index(score)
    problems = []
    seen = set()
    staff_of = getattr(score, '_staff_name', {})
    for nid, (p, vk, i, t, g, ev, pit) in idx.items():
        h = heads.get(nid) if pit is not None else rests.get(nid)
        if h is None:
            if ev.kind == 'rest' and ev.measure_rest and not ev.ids:
                continue
            problems.append(f'{nid} ({p.id}:{vk} m{i + 1} {pit}) not engraved')
            continue
        seen.add(nid)
        if h['when'] is None or h['when'][0] != t or (pit is not None and h['when'][1] != g):
            problems.append(f'{nid} onset {h["when"]} != model {(t, g)}')
        sn = (ev.staff or p.voice(vk).staff)
        want_staff = staff_of.get((p.id, sn))
        if want_staff and h['staff'] != want_staff:
            problems.append(f'{nid} on staff {h["staff"]} != {want_staff}')
        if pit is not None:
            if h['pitch'] != pit:
                problems.append(f'{nid} pitch {h["pitch"]} != {pit}')
            log, dots, scale = h['dur']
            want_scale = F(ev.tuplet[1], ev.tuplet[0]) if ev.tuplet else F(1)
            if (int(log), int(dots), F(scale)) != (LOG2[ev.dtype], ev.dots, want_scale):
                problems.append(f'{nid} duration {h["dur"]} != {ev.dtype} {ev.dots} {ev.tuplet}')
            if h['dots'] != ev.dots:
                problems.append(f'{nid} printed dots {h["dots"]} != {ev.dots}')
        elif h['tag'] == 'Rest':
            d = h['data'][0]
            want_scale = F(ev.tuplet[1], ev.tuplet[0]) if ev.tuplet else F(1)
            if (int(d[0]), int(d[1]), F(d[2])) != (LOG2[ev.dtype], ev.dots, want_scale):
                problems.append(f'{nid} rest duration {d} != {ev.dtype} {ev.dots}')
    for nid in set(heads) | set(rests):
        if nid not in idx:
            problems.append(f'unexpected engraved id {nid}')
    anon = [r for r in rows if r['tag'] in ('NoteHead', 'Rest') and not r['id']]
    if anon:
        problems.append(f'{len(anon)} note heads/rests without id (not from the model)')
    return {'ok': not problems, 'checked': len(seen), 'problems': problems[:40], 'n_problems': len(problems)}


# --------------------------------------------------------------- engraved symbol counts

def line_starts(rows):
    """moments at which systems start (clefs printed at the beginning of a line)"""
    return sorted({r['when'][0] for r in rows if r['tag'] == 'Clef' and r['data'][1] == 1 and r['when']})


def engraved_counts(rows, heads):
    """counts of engraved symbols, de-duplicated across line breaks (original grob)"""
    c = Counter()
    seen = set()

    def once(r):
        k = (r['tag'], r['addr'])
        if k in seen:
            return False
        seen.add(k)
        return True

    for r in rows:
        t, d = r['tag'], r['data']
        if t in ('Tie', 'Slur', 'Beam', 'Hairpin', 'LyricHyphen', 'LyricExtender', 'OttavaBracket',
                 'TupletBracket', 'TupletNumber', 'VoltaBracket', 'SustainPedal'):
            if not once(r):
                continue
        if t == 'Tie':
            c['tie'] += 1
            if d and d[0] > 1:
                c['tie-across-system'] += 1
        elif t == 'Slur':
            c['slur'] += 1
        elif t == 'Beam':
            c['beam'] += 1
        elif t == 'Flag':
            c['flag'] += 1
        elif t == 'Script':
            a = str(d[0]) if d and d[0] else '?'
            c['script:' + a] += 1
        elif t == 'DynamicText':
            c['dyn:' + str(d[0])] += 1
        elif t == 'Hairpin':
            c['hairpin:' + ('cresc' if d[0] == 1 else 'dim')] += 1
        elif t == 'SustainPedal':
            c['pedal-mark:' + str(d[1])] += 1
        elif t == 'Fingering':
            c['fingering'] += 1
        elif t == 'Arpeggio':
            c['arpeggio'] += 1
        elif t == 'StemTremolo':
            c['tremolo'] += 1
        elif t == 'BreathingSign':
            c['breath'] += 1
        elif t == 'TextScript':
            c['text-script'] += 1
        elif t in ('Accidental', 'AccidentalCautionary'):
            c['acc:' + str(d[0]) + (':paren' if d[1] else '')] += 1
        elif t == 'OttavaBracket':
            c['ottava:' + str(d[0])] += 1
        elif t == 'TupletNumber':
            c[f'tuplet:{d[0]}/{d[1]}'] += 1
        elif t == 'Clef':
            if d[1] != 1 and r['when'] and r['when'][0] > 0:
                c['clef-change-grob'] += 1
        elif t == 'TimeSignature':
            c['timesig'] += 1
        elif t == 'KeySignature':
            c['keysig'] += 1
        elif t == 'KeyCancellation':
            c['keycancel'] += 1
        elif t == 'BarLine':
            if d[0] not in ('|', '', None, False):
                c['bar:' + str(d[0]) + ':' + str(d[1])] += 1
        elif t == 'LyricText':
            if d[0] and str(d[0]).strip():
                c['lyric'] += 1
        elif t == 'LyricHyphen':
            c['lyric-hyphen'] += 1
        elif t == 'LyricExtender':
            c['lyric-extender'] += 1
        elif t == 'StanzaNumber':
            c['stanza'] += 1
        elif t == 'RehearsalMark':
            c['rehearsal'] += 1
        elif t == 'MetronomeMark':
            c['metronome-mark'] += 1
        elif t == 'TextMark':
            c['text-mark'] += 1
        elif t == 'VoltaBracket':
            c['volta'] += 1
        elif t == 'SegnoMark':
            c['segno'] += 1
        elif t == 'CodaMark':
            c['coda'] += 1
        elif t == 'MultiMeasureRest':
            c['mmrest'] += 1
        elif t == 'Dots':
            c['dots-grob'] += 1
    for h in heads.values():
        if h['pos'] >= 6:
            c['ledger-above'] += 1
        elif h['pos'] <= -6:
            c['ledger-below'] += 1
        if h['acc']:
            c['acc-on-head'] += 1
    return c
