"""Build + validate one source piece: truth.musicxml (MusicXML 4.0, XSD-checked),
engraving.ly (custom LilyPond writer), vector PDF, and validation that the
LilyPond output matches the truth exactly:
  * MIDI (one track per Voice): (onset, pitch) attack multiset == truth
  * MIDI lyric events: (onset, syllable) sequence == truth lyrics, every verse
  * every truth syllable appears in the vector PDF text layer
  * no LilyPond bar-check warnings / errors
Output goes to _pieces/<key>/ (shared by every damaged variant of the piece).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from synth.build import lilypond, lyric_text_check  # noqa: E402
from synth.lily import LilyWriter, default_layout  # noqa: E402
from synth.midicheck import compare, read_midi  # noqa: E402
from synth.model import (check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voice_events,  # noqa: E402
                         voices_with_lyrics)
from synth.mxl import write_musicxml  # noqa: E402

from pieces import PIECES  # noqa: E402

XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
PIECE_DIR = os.path.join(os.path.dirname(HERE), '_pieces')


def run(cmd, cwd=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def truth_lyric_events(score):
    """per (part, voice): {verse: [(onset, text)]}"""
    out = {}
    for pid, vk, vs in voices_with_lyrics(score):
        p = score.part(pid)
        d = {}
        for i, t, ev in voice_events(score, p, vk):
            for vn, ly in ev.lyrics.items():
                d.setdefault(vn, []).append((F(t), ly.text))
        out[(pid, vk)] = d
    return out


def midi_lyric_check(score, midi_path):
    """LilyPond writes each Lyrics context into the MIDI file as lyric meta
    events; compare the (onset, syllable) multiset per verse with the truth."""
    div, tracks = read_midi(midi_path)
    got = Counter()
    for tr in tracks:
        for t, txt in tr['lyrics']:
            if t == 0 and (txt.startswith('LilyPond') or txt.startswith('creator:')):
                continue   # header text events, not lyrics
            core = re.sub(r'[\s\-_]+$', '', txt.strip())
            core = core.strip()
            if core:
                got[(F(t, div), core)] += 1
    exp = Counter()
    for (pid, vk), d in truth_lyric_events(score).items():
        for vn, evs in d.items():
            for t, txt in evs:
                exp[(t, txt)] += 1
    if not exp:
        return {'ok': True, 'expected': 0, 'midi': sum(got.values()), 'note': 'no lyrics'}
    missing = exp - got
    extra = got - exp
    return {'ok': not missing and not extra, 'expected': sum(exp.values()), 'midi': sum(got.values()),
            'missing': sorted(missing.elements(), key=str)[:10], 'extra': sorted(extra.elements(), key=str)[:10]}


def build_piece(key):
    spec = PIECES[key]
    out = os.path.join(PIECE_DIR, key)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    score, layout, opts = spec['make']()
    sanitize_ties(score)
    fix_unbalanced_slurs(score)
    compute_extenders(score)
    check(score)
    truth = os.path.join(out, 'truth.musicxml')
    write_musicxml(score, truth)
    rc, so, se = run(['xmllint', '--noout', '--nonet', '--schema', XSD, truth])
    xsd_ok = rc == 0
    ly = os.path.join(out, 'engraving.ly')
    open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout or default_layout(score), opts).document())
    rc, warns, pdf, mid = lilypond(ly, out)
    if rc != 0:
        raise RuntimeError(f'lilypond failed for {key}: {warns}')
    bad = [w for w in warns if 'barcheck' in w or 'error' in w]
    cmp_ = compare(score, mid)
    lyr_midi = midi_lyric_check(score, mid)
    lyr_pdf = lyric_text_check(score, pdf)
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    # music21 can read the truth (sanity)
    m21 = None
    try:
        from music21 import converter
        s = converter.parse(truth)
        m21 = {'parts': [p.partName for p in s.parts], 'notes': len(s.flatten().notes)}
    except Exception as e:  # pragma: no cover
        m21 = {'error': repr(e)}
    v = {
        'piece': key, 'xsd_valid': xsd_ok, 'lily_warnings': warns, 'bad_warnings': bad,
        'midi_attacks': cmp_, 'midi_lyrics': lyr_midi, 'lyric_text_found_in_pdf': lyr_pdf,
        'vector_pages': pages, 'measures': len(score.measures), 'music21': m21,
        'parts': [p.name for p in score.parts],
        'lyrics': [{'part': score.part(pid).name, 'verses': len(vs)} for pid, vk, vs in voices_with_lyrics(score)],
    }
    v['ok'] = bool(xsd_ok and not bad and cmp_['ok'] and lyr_midi['ok'] and (lyr_pdf in (None, 1.0)))
    with open(os.path.join(out, 'validation.json'), 'w') as f:
        json.dump(v, f, indent=1, default=str)
    if mid and os.path.exists(mid):
        os.replace(mid, os.path.join(out, 'engraving.midi'))
    return v


if __name__ == '__main__':
    keys = sys.argv[1:] or list(PIECES)
    for k in keys:
        v = build_piece(k)
        print(k, 'OK' if v['ok'] else 'FAIL', 'pages', v['vector_pages'], 'attacks', v['midi_attacks']['expected_attacks'],
              'midi_ok', v['midi_attacks']['ok'], 'lyr_midi', v['midi_lyrics'], 'lyr_pdf', v['lyric_text_found_in_pdf'],
              'xsd', v['xsd_valid'], 'warn', v['lily_warnings'][:5], 'm21', v['music21'])
