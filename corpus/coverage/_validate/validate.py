#!/usr/bin/env python3
"""Independent validator for corpus/coverage/<family>/<id>/ items (all families).

Adapted copy of corpus/challenge/_validate/validate.py (the truth parser, MIDI check, PDF checks and
clean.pdf pixel comparison are the same code). Coverage-specific changes:
  * items are discovered under corpus/coverage/<family>/<id>/ (folders starting with '_' are skipped)
  * scan-severe.pdf is a required file; every scan*.pdf needs a degradations record (seed + params)
  * meta: id, family, title, symbols[] (taxonomy tags or x-*), layout (layout tag), expected{parts[],
    must_not_split}, counts{tag: n}, degradations, dpi, pages (= clean.pdf pages), license (CC0/PD)
  * every taxonomy tag in meta.symbols has a count > 0; the harness tagger (tools/coverage.mjs
    extract(), run through tagcount.mjs) must find the declared tags in truth.musicxml, and tags it
    finds in the truth but meta does not declare are reported as warnings
  * cue notes (<cue/>) take time but do not sound, so they are not expected in LilyPond's MIDI
  * the generator's own verification record (meta.validation) must not contain a false check

Original description follows.


Checks per item (nothing in the item folders is modified):
  files     engraving.ly, truth.musicxml, clean.pdf, scan.pdf, meta.json, ATTRIBUTION.txt present
  xsd       every truth*.musicxml validates (xmllint --schema mvp/work/schema/musicxml.xsd)
  music21   truth.musicxml parses with music21 (note/rest counts recorded)
  pdf       every *.pdf opens (pdfinfo), renders (pdftoppm), has no fonts (pdffonts), no text
            (pdftotext) and at least one image per page (pdfimages -list)
  meta      required keys: id (= folder), category (= parent folder), title, edge_cases[],
            expected{parts[], must_not_split, shared_staves[], notes}, degradations{<file>: {seed,..}}
            for every scan*.pdf, dpi, license; expected.parts vs the truth part names
  midi      engraving.ly re-rendered with LilyPond 2.24 (in a scratch dir): every truth attack
            (onset, pitch; ties merged, graces separate) and every truth lyric syllable
            (onset, text) is matched against LilyPond's own MIDI output
  clean     clean.pdf is pixel-compared (ink masks, 2 px tolerance) with a fresh raster of the
            LilyPond PDF at the same dpi, page by page

Usage: python validate.py [--jobs N] [--only cat/id,...] [--out report.json] [--scratch DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CH = HERE.parent                      # corpus/coverage
ROOT = CH.parent.parent
XSD = ROOT / 'mvp' / 'work' / 'schema' / 'musicxml.xsd'
TAXONOMY = {
    'notes': 'note-breve note-whole note-half note-quarter note-8th note-16th note-32nd note-64th dot double-dot chord beam flag stem-up stem-down ledger-above ledger-below grace grace-slash cue-note tremolo'.split(),
    'rests': 'rest-breve rest-whole rest-half rest-quarter rest-8th rest-16th rest-32nd rest-64th rest-dotted rest-whole-bar rest-multibar'.split(),
    'pitch': ('clef-treble clef-bass clef-alto clef-tenor clef-soprano clef-treble-8vb clef-treble-8va clef-bass-8vb clef-change key-0 '
              + ' '.join(f'key-s{i}' for i in range(1, 8)) + ' ' + ' '.join(f'key-f{i}' for i in range(1, 8))
              + ' key-change acc-sharp acc-flat acc-natural acc-double-sharp acc-double-flat acc-courtesy ottava-8va ottava-8vb ottava-15ma').split(),
    'time': 'time-2-4 time-3-4 time-4-4 time-2-2 time-3-2 time-6-8 time-9-8 time-12-8 time-5-4 time-5-8 time-7-8 time-common time-cut time-change pickup tuplet-3 tuplet-2 tuplet-5 tuplet-6 tuplet-7 tuplet-nested tie tie-across-system'.split(),
    'marks': 'slur staccato staccatissimo accent tenuto marcato fermata trill mordent turn arpeggio breath dyn-pp dyn-p dyn-mp dyn-mf dyn-f dyn-ff dyn-sfz hairpin-cresc hairpin-dim pedal fingering text-expression tempo-mark metronome rehearsal-mark chord-symbol'.split(),
    'structure': 'barline-double barline-final repeat-start repeat-end volta-1 volta-2 segno coda dc ds fine system-break page-break multi-page'.split(),
    'lyrics': 'lyrics lyrics-multi-verse lyrics-melisma lyrics-extender lyrics-hyphen lyrics-elision lyrics-non-ascii stanza-text'.split(),
}
TAGS = [t for v in TAXONOMY.values() for t in v]
TAGSET = set(TAGS)
LAYOUTS = ['melody', 'melody-lyrics', 'piano', 'voice-piano', 'choir-closed-satb', 'choir-open-satb', 'choir-sab', 'choir-ttbb',
           'choir-ssaa', 'choir-piano', 'organ', 'string-quartet', 'orchestral', 'lead-sheet', 'hymnal-stanzas', 'divisi',
           'cross-staff', 'two-voices-one-staff-instrument', 'percussion-none']
# taxonomy tags the harness tagger cannot see in MusicXML (no element for them)
NOT_TAGGABLE = {'stanza-text'}
TPQ = 384


def sh(cmd, timeout=600, cwd=None):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout, cwd=cwd)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def sha(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:16]


# ------------------------------------------------------------------ truth parsing
def norm_text(s):
    import unicodedata
    s = unicodedata.normalize('NFKC', s or '').lower()
    return ''.join(ch for ch in s if ch.isalnum())


def truth_events(path):
    """-> dict(parts=[names], attacks=Counter((tick,pitch)), graces=[(tick_main,pitch)],
    lyrics=Counter((tick,text)), n_notes, n_rests, measures)"""
    root = ET.parse(path).getroot()
    names = {sp.get('id'): (sp.findtext('part-name') or '').strip() for sp in root.iter('score-part')}
    parts = root.findall('part')
    per_part = []
    nmeas = max((len(p.findall('measure')) for p in parts), default=0)
    mlen = [F(0)] * nmeas
    for p in parts:
        div = 1
        evs = []
        for mi, m in enumerate(p.findall('measure')):
            pos = F(0)
            last = F(0)
            mx = F(0)
            pending_graces = []
            for c in m:
                if c.tag == 'attributes':
                    d = c.findtext('divisions')
                    if d:
                        div = int(d)
                elif c.tag == 'backup':
                    pos -= F(int(c.findtext('duration')), div)
                elif c.tag == 'forward':
                    pos += F(int(c.findtext('duration')), div)
                    mx = max(mx, pos)
                elif c.tag == 'note':
                    pitch = c.find('pitch')
                    midi = None
                    if pitch is not None:
                        alter = float(pitch.findtext('alter') or 0)
                        midi = (int(pitch.findtext('octave')) + 1) * 12 + 'C D EF G A B'.index(pitch.findtext('step')) + round(alter)
                    if c.find('cue') is not None:      # cue notes take time but do not sound
                        if c.find('chord') is None:
                            last = pos
                            pos += F(int(c.findtext('duration') or 0), div)
                            mx = max(mx, pos)
                        continue
                    if c.find('grace') is not None:
                        if midi is not None:
                            pending_graces.append(midi)
                        continue
                    chord = c.find('chord') is not None
                    dur = F(int(c.findtext('duration') or 0), div)
                    on = last if chord else pos
                    if not chord:
                        last = pos
                        pos += dur
                        mx = max(mx, pos)
                    ties = {t.get('type') for t in c.findall('tie')}
                    lyr = []
                    for l in c.findall('lyric'):
                        t = norm_text(''.join(x.text or '' for x in l.findall('text')))
                        if t:
                            lyr.append(t)
                    is_rest = c.find('rest') is not None or midi is None
                    evs.append((mi, on, midi, is_rest, 'stop' in ties, lyr, list(pending_graces) if not is_rest else []))
                    if not is_rest:
                        pending_graces = []
            mlen[mi] = max(mlen[mi], mx)
        per_part.append(evs)
    start = [F(0)] * (nmeas + 1)
    for i in range(nmeas):
        start[i + 1] = start[i] + mlen[i]
    att, lyr, graces = Counter(), Counter(), []
    n_notes = n_rests = 0
    for evs in per_part:
        for mi, on, midi, is_rest, tie_stop, ly, gr in evs:
            t = start[mi] + on
            tick = round(t * TPQ)
            if is_rest:
                n_rests += 1
                continue
            n_notes += 1
            for g in gr:
                graces.append((tick, g))
            if not tie_stop:
                att[(tick, midi)] += 1
            for x in ly:
                lyr[(tick, x)] += 1
    return dict(parts=[names.get(p.get('id'), p.get('id')) for p in parts], attacks=att, graces=graces,
                lyrics=lyr, n_notes=n_notes, n_rests=n_rests, measures=nmeas)


# ------------------------------------------------------------------ midi
def _vlq(b, i):
    v = 0
    while True:
        c = b[i]
        i += 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return v, i


def read_midi(path):
    data = Path(path).read_bytes()
    assert data[:4] == b'MThd'
    hlen = struct.unpack('>I', data[4:8])[0]
    _, ntrk, div = struct.unpack('>HHH', data[8:14])
    pos = 8 + hlen
    notes, lyrics = Counter(), Counter()
    for _ in range(ntrk):
        ln = struct.unpack('>I', data[pos + 4:pos + 8])[0]
        b = data[pos + 8:pos + 8 + ln]
        pos += 8 + ln
        i, t, status = 0, 0, None
        while i < len(b):
            d, i = _vlq(b, i)
            t += d
            c = b[i]
            if c == 0xFF:
                typ = b[i + 1]
                n, j = _vlq(b, i + 2)
                if typ == 0x05:
                    txt = norm_text(b[j:j + n].decode('utf-8', 'replace'))
                    if txt:
                        lyrics[(round(F(t, div) * TPQ), txt)] += 1
                i = j + n
                continue
            if c in (0xF0, 0xF7):
                n, j = _vlq(b, i + 1)
                i = j + n
                continue
            if c & 0x80:
                status = c
                i += 1
            hi = status & 0xF0
            if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                a1, a2 = b[i], b[i + 1]
                i += 2
                if hi == 0x90 and a2 > 0:
                    notes[(round(F(t, div) * TPQ), a1)] += 1
            else:
                i += 1
    return notes, lyrics


def fuzzy_diff(exp: Counter, got: Counter, tol=2):
    """multiset diff with +-tol tick tolerance -> (missing, extra) Counters"""
    exp, got = Counter(exp), Counter(got)
    common = exp & got
    exp -= common
    got -= common
    for (t, p), n in list(exp.items()):
        for dt in range(1, tol + 1):
            for tt in (t - dt, t + dt):
                k = (tt, p)
                while n and got.get(k, 0):
                    got[k] -= 1
                    n -= 1
                    exp[(t, p)] -= 1
        if not got:
            break
    return +exp, +got


def midi_check(truth, midi_paths):
    exp = truth['attacks']
    notes, lyrics = read_midi(midi_paths[0])
    for extra_file in midi_paths[1:]:
        # a second \score (e.g. a separate Amen system) restarts the MIDI clock at 0:
        # place it at the offset where it matches the most truth attacks
        n2, l2 = read_midi(extra_file)
        if not n2:
            continue
        first = min(t for t, _ in n2)
        rest = exp - notes
        best_off, best_hit = 0, -1
        for off in sorted({t - first for t, _ in rest}):
            hit = sum((rest & Counter({(t + off, p): n for (t, p), n in n2.items()})).values())
            if hit > best_hit:
                best_off, best_hit = off, hit
        notes += Counter({(t + best_off, p): n for (t, p), n in n2.items()})
        lyrics += Counter({(t + best_off, x): n for (t, x), n in l2.items()})
    # a grace note before the very first beat makes LilyPond start the MIDI clock at the grace:
    # find the global offset that best aligns the MIDI with the truth
    t0 = min((t for t, _ in exp), default=0)
    cands = sorted({0} | {t - t0 for t, _ in sorted(notes)[:8]})
    best = min(cands, key=lambda off: (sum(fuzzy_diff(exp, Counter({(t - off, p): n for (t, p), n in notes.items()}))[0].values()), abs(off)))
    if best:
        notes = Counter({(t - best, p): n for (t, p), n in notes.items()})
        lyrics = Counter({(t - best, x): n for (t, x), n in lyrics.items()})
    missing, extra = fuzzy_diff(exp, notes)
    # extra MIDI notes explained by grace notes (LilyPond plays graces before the beat)
    gpool = Counter(truth['graces'])
    explained = 0
    for (t, p), n in list(extra.items()):
        for (gt, gp) in list(gpool):
            if gp == p and gpool[(gt, gp)] and -2 * TPQ <= t - gt <= TPQ // 2:
                k = min(n, gpool[(gt, gp)])
                gpool[(gt, gp)] -= k
                extra[(t, p)] -= k
                n -= k
                explained += k
                if not n:
                    break
    extra = +extra
    # duplicates only (unison voices / "a 2" written once): set-level agreement
    set_missing = {k for k in missing if k not in notes and not any((k[0] + d, k[1]) in notes for d in (-2, -1, 1, 2))}
    set_extra = {k for k in extra if k not in exp and not any((k[0] + d, k[1]) in exp for d in (-2, -1, 1, 2))}
    lmiss, lextra = fuzzy_diff(truth['lyrics'], lyrics)
    fmt = lambda c: [[round(t / TPQ, 3), p, n] for (t, p), n in sorted(c.items())[:12]]
    return dict(
        midi_offset_quarters=round(best / TPQ, 4),
        truth_attacks=sum(exp.values()), midi_attacks=sum(notes.values()), grace_extras=explained,
        missing=sum(missing.values()), extra=sum(extra.values()),
        set_missing=len(set_missing), set_extra=len(set_extra),
        missing_sample=fmt(missing), extra_sample=fmt(extra),
        truth_syllables=sum(truth['lyrics'].values()), midi_syllables=sum(lyrics.values()),
        lyr_missing=sum(lmiss.values()), lyr_extra=sum(lextra.values()),
        lyr_missing_sample=fmt(lmiss), lyr_extra_sample=fmt(lextra),
        notes_ok=not set_missing and not set_extra,
        notes_exact=not missing and not extra,
        lyrics_ok=not lmiss and not lextra,
    )


# ------------------------------------------------------------------ pdf
def pdf_check(pdf, scratch):
    r = {'file': pdf.name}
    code, out, err = sh(['pdfinfo', str(pdf)], 60)
    r['opens'] = code == 0
    m = re.search(r'^Pages:\s+(\d+)', out, re.M)
    r['pages'] = int(m.group(1)) if m else 0
    code, out, _ = sh(['pdffonts', str(pdf)], 60)
    r['fonts'] = max(0, len([l for l in out.splitlines() if l.strip()]) - 2) if code == 0 else -1
    code, out, _ = sh(['pdftotext', '-q', str(pdf), '-'], 60)
    r['text_chars'] = len(out.strip())
    code, out, _ = sh(['pdfimages', '-list', str(pdf)], 60)
    rows = [l.split() for l in out.splitlines()[2:] if l.strip()]
    r['images'] = len(rows)
    try:
        r['image_ppi'] = sorted({int(x[12]) for x in rows if len(x) > 13})
        r['image_px'] = [[int(x[3]), int(x[4])] for x in rows][:16]
        r['image_color'] = sorted({x[5] for x in rows})
    except Exception:
        pass
    d = Path(tempfile.mkdtemp(dir=scratch))
    code, _, err = sh(['pdftoppm', '-gray', '-r', '12', str(pdf), str(d / 'p')], 300)
    r['renders'] = code == 0 and len(list(d.glob('*.pgm'))) == r['pages'] and not re.search(r'error', err, re.I)
    if not r['renders']:
        r['render_err'] = err[-300:]
    shutil.rmtree(d, ignore_errors=True)
    r['image_only'] = r['fonts'] == 0 and r['text_chars'] == 0 and r['images'] >= r['pages'] > 0
    r['ok'] = r['opens'] and r['renders'] and r['image_only']
    return r


def ink(path_png):
    a = np.asarray(Image.open(path_png).convert('L'), dtype=np.uint8)
    return a < 150


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == dy == 0:
                continue
            s = np.zeros_like(m)
            ys = slice(max(dy, 0), m.shape[0] + min(dy, 0))
            yd = slice(max(-dy, 0), m.shape[0] + min(-dy, 0))
            xs = slice(max(dx, 0), m.shape[1] + min(dx, 0))
            xd = slice(max(-dx, 0), m.shape[1] + min(-dx, 0))
            s[yd, xd] = m[ys, xs]
            out |= s
    return out


def clean_compare(clean_pdf, ly_pdf, dpi, scratch):
    d = Path(tempfile.mkdtemp(dir=scratch))
    try:
        sh(['pdftoppm', '-gray', '-png', '-r', str(dpi), str(clean_pdf), str(d / 'c')], 600)
        sh(['pdftoppm', '-gray', '-png', '-aa', 'yes', '-aaVector', 'yes', '-r', str(dpi), str(ly_pdf), str(d / 'l')], 600)
        key = lambda p: int(re.search(r'(\d+)\.png$', p.name).group(1))
        cs = sorted(d.glob('c-*.png'), key=key)
        ls = sorted(d.glob('l-*.png'), key=key)
        res = {'clean_pages': len(cs), 'ly_pages': len(ls), 'pages': []}
        for a, b in zip(cs, ls):
            A, B = ink(a), ink(b)
            h, w = min(A.shape[0], B.shape[0]), min(A.shape[1], B.shape[1])
            size_delta = [A.shape[0] - B.shape[0], A.shape[1] - B.shape[1]]
            A, B = A[:h, :w], B[:h, :w]
            na, nb = int(A.sum()), int(B.sum())
            prec = float((A & dilate(B, 2)).sum() / max(na, 1))
            rec = float((B & dilate(A, 2)).sum() / max(nb, 1))
            res['pages'].append({'size_delta': size_delta, 'ink_clean': na, 'ink_ly': nb,
                                 'clean_in_ly': round(prec, 4), 'ly_in_clean': round(rec, 4)})
        res['min_overlap'] = min([min(p['clean_in_ly'], p['ly_in_clean']) for p in res['pages']] or [0])
        res['ok'] = res['clean_pages'] == res['ly_pages'] and res['min_overlap'] >= 0.97
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------ meta
def _has_seed(rec):
    if isinstance(rec, dict):
        return any(('seed' in k and v not in (None, '')) or _has_seed(v) for k, v in rec.items())
    if isinstance(rec, list):
        return any(_has_seed(x) for x in rec)
    return False


def _false_checks(v, path='validation'):
    """paths of boolean False values in the generator's own verification record"""
    out = []
    if isinstance(v, dict):
        for k, x in v.items():
            if x is False and not re.search(r'warn|skip|error|fail|missing|crash|problem|differ|mismatch|^has_|_needed$|optional', k, re.I):
                out.append(f'{path}.{k}')
            elif isinstance(x, (dict, list)):
                out += _false_checks(x, f'{path}.{k}')
    elif isinstance(v, list):
        for i, x in enumerate(v):
            out += _false_checks(x, f'{path}[{i}]')
    return out


def meta_check(meta, fam, iid, scans, truth_parts, clean_pages):
    probs, warns = [], []
    need = ['id', 'family', 'title', 'symbols', 'layout', 'expected', 'counts', 'degradations', 'dpi', 'pages', 'license']
    for k in need:
        if k not in meta or meta[k] in (None, '', [], {}):
            probs.append(f'missing/empty meta.{k}')
    if meta.get('id') != iid:
        probs.append(f'meta.id {meta.get("id")!r} != folder {iid!r}')
    if meta.get('family') != fam:
        probs.append(f'meta.family {meta.get("family")!r} != {fam!r}')
    if not isinstance(meta.get('title'), str) or not meta.get('title', '').strip():
        probs.append('meta.title missing')
    if meta.get('layout') not in LAYOUTS:
        probs.append(f'meta.layout {meta.get("layout")!r} is not a layout tag')
    for l in meta.get('layout_also') or []:
        if l not in LAYOUTS:
            probs.append(f'meta.layout_also {l!r} is not a layout tag')
    sy = meta.get('symbols')
    if not isinstance(sy, list) or not all(isinstance(x, str) and x for x in sy or []):
        probs.append('meta.symbols must be a non-empty list of strings')
        sy = []
    bad = [x for x in sy if x not in TAGSET and not x.startswith('x-')]
    if bad:
        probs.append(f'meta.symbols has tags outside the taxonomy without an x- prefix: {bad}')
    if len(set(sy)) != len(sy):
        warns.append('meta.symbols has duplicates')
    cnt = meta.get('counts')
    if not isinstance(cnt, dict):
        probs.append('meta.counts is not an object')
        cnt = {}
    nonnum = [k for k, v in cnt.items() if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0]
    if nonnum:
        probs.append(f'meta.counts has non-numeric/negative values: {nonnum[:8]}')
    nocount = [x for x in sy if x in TAGSET and not (isinstance(cnt.get(x), (int, float)) and cnt.get(x) > 0)]
    if nocount:
        probs.append(f'taxonomy symbols without a positive count: {nocount}')
    undeclared = sorted(k for k, v in cnt.items() if k in TAGSET and isinstance(v, (int, float)) and v > 0 and k not in sy)
    if undeclared:
        warns.append(f'counted but not listed in meta.symbols: {undeclared}')
    ex = meta.get('expected') or {}
    if not isinstance(ex.get('parts'), list) or not ex.get('parts'):
        probs.append('expected.parts missing/empty')
    if not isinstance(ex.get('must_not_split'), bool):
        probs.append('expected.must_not_split not a bool')
    deg = meta.get('degradations') or {}
    for s in ('scan.pdf', 'scan-severe.pdf'):
        if s not in scans:
            probs.append(f'{s} missing')
    for s in scans:
        rec = deg.get(s)
        if not isinstance(rec, dict):
            probs.append(f'degradations[{s}] missing')
            continue
        if not _has_seed(rec) and not _has_seed({'seed': meta.get('seed')}):
            probs.append(f'degradations[{s}] has no seed')
        body = {k: v for k, v in rec.items() if k != 'seed'}
        if not body:
            probs.append(f'degradations[{s}] has no parameters')
    lic = str(meta.get('license', ''))
    if not re.search(r'cc0|public domain|public-domain', lic, re.I):
        probs.append(f'license is not CC0/public domain: {lic[:80]!r}')
    pages = meta.get('pages')
    if not isinstance(pages, int) or pages < 1:
        probs.append(f'meta.pages {pages!r} is not a positive integer')
    elif clean_pages and pages != clean_pages:
        probs.append(f'meta.pages {pages} != clean.pdf pages {clean_pages}')
    if isinstance(ex.get('parts'), list) and truth_parts is not None:
        if [str(x) for x in ex['parts']] != truth_parts:
            warns.append(f'expected.parts {ex["parts"]} != truth part names {truth_parts}')
    if not meta.get('notes') and not meta.get('truth_limitations'):
        warns.append('meta.notes missing (truth limitations not stated)')
    fc = _false_checks(meta.get('validation'))
    if fc:
        warns.append(f'generator verification record has false checks: {fc[:6]}')
    return probs, warns


def tagger_check(meta, tagc):
    """declared symbols vs the harness tagger's view of truth.musicxml"""
    probs, warns = [], []
    if not tagc or '_error' in tagc:
        probs.append(f'harness tagger cannot read truth: {(tagc or {}).get("_error")}')
        return probs, warns, {}
    sy = set(meta.get('symbols') or [])
    declared_missing = sorted(t for t in sy if t in TAGSET and t not in NOT_TAGGABLE and not tagc.get(t))
    found_undeclared = sorted(t for t, n in tagc.items() if t in TAGSET and n and t not in sy)
    if declared_missing:
        warns.append(f'declared but the harness tagger finds none in truth: {declared_missing}')
    if found_undeclared:
        warns.append(f'in truth (harness tagger) but not declared in meta.symbols: {found_undeclared}')
    cnt = meta.get('counts') or {}
    cmp = {t: [cnt.get(t, 0), tagc.get(t, 0)] for t in sorted(set(t for t in cnt if t in TAGSET) | set(t for t in tagc if t in TAGSET)) if cnt.get(t, 0) != tagc.get(t, 0)}
    return probs, warns, {'declared_missing': declared_missing, 'found_undeclared': found_undeclared, 'count_differs': cmp}


# ------------------------------------------------------------------ per item
REQUIRED = ['engraving.ly', 'truth.musicxml', 'clean.pdf', 'scan.pdf', 'scan-severe.pdf', 'meta.json', 'ATTRIBUTION.txt']


def check_item(task):
    fam, iid, scratch, tagc = task
    d = CH / fam / iid
    r = {'family': fam, 'id': iid, 'problems': [], 'warnings': []}
    P, Wn = r['problems'], r['warnings']
    for f in REQUIRED:
        if not (d / f).exists() or not (d / f).stat().st_size:
            P.append(f'missing {f}')
    scans = sorted(p.name for p in d.glob('scan*.pdf'))
    r['scans'] = scans
    r['xsd'] = {}
    for t in sorted(d.glob('truth*.musicxml')):
        code, out, err = sh(['xmllint', '--noout', '--nonet', '--schema', str(XSD), str(t)], 300)
        r['xsd'][t.name] = code == 0
        if code != 0:
            P.append(f'{t.name} fails XSD: ' + ' | '.join(err.splitlines()[:3]))
    truth = None
    try:
        truth = truth_events(d / 'truth.musicxml')
        r['truth'] = {k: truth[k] for k in ('parts', 'n_notes', 'n_rests', 'measures')}
        r['truth']['attacks'] = sum(truth['attacks'].values())
        r['truth']['syllables'] = sum(truth['lyrics'].values())
        r['truth']['graces'] = len(truth['graces'])
    except Exception as e:
        P.append(f'truth parse error: {e}')
    try:
        code, out, err = sh([sys.executable, '-c',
                             'import sys,music21;s=music21.converter.parse(sys.argv[1],format="musicxml",forceSource=True);'
                             'print(len(s.parts),len(list(s.recurse().notes)),len(list(s.recurse().getElementsByClass("Rest"))))',
                             str(d / 'truth.musicxml')], 1200)
        if code != 0:
            P.append('music21 cannot parse truth: ' + (err.strip().splitlines() or ['?'])[-1][:200])
        else:
            a = out.split()
            r['music21'] = {'parts': int(a[0]), 'notes_and_chords': int(a[1]), 'rests': int(a[2])}
    except Exception as e:
        P.append(f'music21 error: {e}')
    r['pdfs'] = {}
    for pdf in sorted(d.glob('*.pdf')):
        pr = pdf_check(pdf, scratch)
        r['pdfs'][pdf.name] = pr
        if not pr['ok']:
            P.append(f'{pdf.name}: opens={pr["opens"]} renders={pr["renders"]} fonts={pr["fonts"]} text={pr["text_chars"]} images={pr["images"]}/{pr["pages"]}')
    clean_pages = r['pdfs'].get('clean.pdf', {}).get('pages')
    for s in scans:
        sp = r['pdfs'].get(s, {}).get('pages')
        if clean_pages and sp and sp != clean_pages:
            Wn.append(f'{s} has {sp} pages, clean.pdf {clean_pages} (check meta.degradations: spread/merged capture?)')
    try:
        meta = json.loads((d / 'meta.json').read_text())
        probs, warns = meta_check(meta, fam, iid, scans, truth['parts'] if truth else None, clean_pages)
        P.extend(probs)
        Wn.extend(warns)
        tp, tw, tinfo = tagger_check(meta, tagc)
        P.extend(tp)
        Wn.extend(tw)
        r['tagger'] = tinfo
        r['layout'] = meta.get('layout')
        r['symbols'] = meta.get('symbols')
    except Exception as e:
        P.append(f'meta.json unreadable: {e}')
    att = d / 'ATTRIBUTION.txt'
    if att.exists() and not re.search(r'cc0|public domain|public-domain', att.read_text(errors='replace'), re.I):
        Wn.append('ATTRIBUTION.txt does not mention CC0/public domain')
    r['hash'] = {'engraving': sha(d / 'engraving.ly') if (d / 'engraving.ly').exists() else None,
                 'truth': sha(d / 'truth.musicxml') if (d / 'truth.musicxml').exists() else None,
                 'clean': sha(d / 'clean.pdf') if (d / 'clean.pdf').exists() else None}
    return r


def render_check(task):
    """LilyPond render of one unique engraving + MIDI/truth + clean.pdf comparison."""
    fam, iid, scratch = task[:3]
    d = CH / fam / iid
    w = Path(scratch) / 'ly' / f'{fam}__{iid}'
    shutil.rmtree(w, ignore_errors=True)
    w.mkdir(parents=True)
    shutil.copy(d / 'engraving.ly', w / 'engraving.ly')
    r = {}
    import time as _t
    t0 = _t.time()
    code, out, err = sh(['lilypond', '-dno-point-and-click', '-o', 'out', 'engraving.ly'], 1800, cwd=w)
    r['lilypond_s'] = round(_t.time() - t0, 1)
    r['lilypond_exit'] = code
    r['lilypond_warnings'] = [l for l in err.splitlines() if re.search(r'warning|error', l, re.I)][:20]
    pdf = w / 'out.pdf'
    mids = sorted(w.glob('out*.mid*'))
    if code != 0 or not pdf.exists() or not mids:
        r['ok'] = False
        r['error'] = 'lilypond failed: ' + err[-400:]
        return r
    truth = truth_events(d / 'truth.musicxml')
    mids.sort(key=lambda m: int((re.search(r'-(\d+)\.midi?$', m.name) or [0, -1])[1]))
    r['midi_files'] = [m.name for m in mids]
    r['midi'] = midi_check(truth, mids)
    if len(mids) > 1:
        r['midi']['note'] = f'{len(mids)} \\score blocks: later MIDI files placed at their best-matching offset'
    code, out, _ = sh(['pdfimages', '-list', str(d / 'clean.pdf')], 60)
    rows = [l.split() for l in out.splitlines()[2:] if l.strip()]
    dpi = int(rows[0][12]) if rows else 300
    r['clean_dpi'] = dpi
    r['clean'] = clean_compare(d / 'clean.pdf', pdf, dpi, scratch)
    r['ok'] = r['midi']['notes_ok'] and r['midi']['lyrics_ok'] and r['clean']['ok']
    shutil.rmtree(w, ignore_errors=True)
    return r


def discover(only):
    tasks = []
    for fd in sorted(CH.iterdir()):
        if not fd.is_dir() or fd.name.startswith(('_', '.')):
            continue
        for d in sorted(fd.iterdir()):
            if not d.is_dir() or d.name.startswith(('_', '.')):
                continue
            if only and f'{fd.name}/{d.name}' not in only and fd.name not in only:
                continue
            tasks.append((fd.name, d.name))
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=48)
    ap.add_argument('--only', default='')
    ap.add_argument('--no-render', action='store_true', help='skip the LilyPond re-render (MIDI / clean.pdf checks)')
    ap.add_argument('--out', default=str(HERE / 'report.json'))
    ap.add_argument('--scratch', default=os.environ.get('VALIDATE_SCRATCH', str(Path(tempfile.gettempdir()) / 'coverage-validate')))
    a = ap.parse_args()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    only = {x.strip() for x in a.only.split(',') if x.strip()}
    found = discover(only)
    truths = [str(CH / f / i / 'truth.musicxml') for f, i in found if (CH / f / i / 'truth.musicxml').exists()]
    code, out, err = sh(['node', str(HERE / 'tagcount.mjs'), *truths], 1200)
    tagcounts = json.loads(out) if code == 0 and out.strip() else {}
    if code != 0:
        print('tagcount.mjs failed:', err[-500:], file=sys.stderr)
    tasks = [(f, i, a.scratch, tagcounts.get(str(CH / f / i / 'truth.musicxml'))) for f, i in found]
    with ProcessPoolExecutor(a.jobs) as ex:
        items = list(ex.map(check_item, tasks))
    for it in items:
        it['tagger_counts'] = tagcounts.get(str(CH / it['family'] / it['id'] / 'truth.musicxml'))
    groups = {}
    for it, t in zip(items, tasks):
        h = it['hash']
        groups.setdefault((h['engraving'], h['truth'], h['clean']), []).append((it, t))
    reps = [v[0][1] for v in groups.values()]
    if a.no_render:
        rend = [{'ok': None, 'skipped': True} for _ in reps]
    else:
        # largest engravings first so they do not end up last on one worker
        order = sorted(range(len(reps)), key=lambda k: -(CH / reps[k][0] / reps[k][1] / 'truth.musicxml').stat().st_size)
        with ProcessPoolExecutor(a.jobs) as ex:
            res = dict(zip(order, ex.map(render_check, [reps[k] for k in order])))
        rend = [res[k] for k in range(len(reps))]
    for (key, members), rr in zip(groups.items(), rend):
        for it, _ in members:
            it['render'] = rr if it is members[0][0] else {'same_as': f'{members[0][1][0]}/{members[0][1][1]}', 'ok': rr.get('ok')}
            if rr.get('skipped'):
                continue
            if not rr.get('ok'):
                m = rr.get('midi', {})
                c = rr.get('clean', {})
                if 'error' in rr:
                    it['problems'].append(rr['error'][:300])
                if m and not m['notes_ok']:
                    it['problems'].append(f'MIDI vs truth notes: {m["set_missing"]} truth attacks absent from MIDI, {m["set_extra"]} MIDI attacks absent from truth')
                if m and not m['lyrics_ok']:
                    it['problems'].append(f'MIDI vs truth lyrics: {m["lyr_missing"]} missing, {m["lyr_extra"]} extra')
                if c and not c.get('ok'):
                    it['problems'].append(f'clean.pdf vs LilyPond render: pages {c.get("clean_pages")}/{c.get("ly_pages")}, min ink overlap {c.get("min_overlap")}')
            m = rr.get('midi') or {}
            if m and m.get('notes_ok') and not m.get('notes_exact'):
                it['warnings'].append(f'MIDI multiplicity differs (unisons written once): {m["missing"]} truth attacks without own MIDI note, {m["extra"]} MIDI extras')
            if rr.get('lilypond_warnings'):
                it['warnings'].append(f'LilyPond printed {len(rr["lilypond_warnings"])} warning line(s): {rr["lilypond_warnings"][0][:160]}')
    ok = [it for it in items if not it['problems']]
    fams = sorted({i['family'] for i in items})
    rep = {'n_items': len(items), 'n_ok': len(ok), 'n_renders': len(reps), 'rendered': not a.no_render,
           'by_family': {f: {'items': sum(1 for i in items if i['family'] == f),
                             'ok': sum(1 for i in ok if i['family'] == f),
                             'scan_files': sum(len(i['scans']) for i in items if i['family'] == f)} for f in fams},
           'failed': [{'id': f'{i["family"]}/{i["id"]}', 'problems': i['problems']} for i in items if i['problems']],
           'warnings': [{'id': f'{i["family"]}/{i["id"]}', 'warnings': i['warnings']} for i in items if i['warnings']],
           'items': items}
    Path(a.out).write_text(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
    print(json.dumps({k: rep[k] for k in ('n_items', 'n_ok', 'n_renders', 'by_family')}, indent=1))
    for f in rep['failed']:
        print('FAIL', f['id'], *f['problems'], sep='\n   ')


if __name__ == '__main__':
    main()
