"""Build one layout-challenge item.

truth.musicxml and engraving.ly come from the same internal model; validation:
  * truth validates against the MusicXML 4.0 XSD (xmllint) and parses in music21
  * LilyPond MIDI (one track per Voice, one file per \\score segment) reproduces the
    truth's (onset, pitch) attack multiset exactly (cue notes included)
  * no bar-check / programming errors in the LilyPond log
  * the engraved PDF has the planned number of pages
  * every lyric syllable of the truth is found in the vector PDF text
Then the vector PDF is rasterised (pdftoppm) and damaged (lsynth/degrade2.py) into
scan.pdf, scan-mild.pdf, scan-severe.pdf (image-only, img2pdf) + clean.pdf (undamaged raster).
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import time
import traceback
from fractions import Fraction as F

import numpy as np
from PIL import Image

from lsynth import degrade2 as D
from lsynth.lily import LilyWriter
from lsynth.midicheck import compare_multi
from lsynth.model import (check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics)
from lsynth.mxl import write_musicxml

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)                       # corpus/challenge/layout
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
CATEGORY = 'layout'


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def segments_of(score, layout):
    segs = layout.get('segments')
    if not segs:
        return [{'start': 0, 'end': len(score.measures), 'groups': layout['groups']}]
    return segs


def mark_hidden_rests(score, layout):
    """Rests on staves that LilyPond removes (\\RemoveAllEmptyStaves) in a system become
    print-object="no" in the truth.  Systems come from the explicit breaks."""
    hidden_report = []
    for seg in segments_of(score, layout):
        a, b = seg['start'], seg['end']
        present = {tuple(v) for g in seg['groups'] for st in g['staves'] for v in st['voices']}
        for p in score.parts:
            for v in p.voices:
                if (p.id, v.key) in present:
                    continue
                for i in range(a, b):
                    for ev in p.measures[i].get(v.key, []):
                        if ev.kind == 'note':
                            raise RuntimeError(f'voice {p.id}:{v.key} has notes in segment without its staff')
                        if ev.kind == 'rest':
                            ev.hidden = True
                hidden_report.append({'staff': f'{p.name} (not engraved in this score block)',
                                      'measures': [score.measures[a].number, score.measures[b - 1].number]})
        starts = [a] + [i for i in range(a + 1, b) if score.measures[i].brk]
        systems = [(s, (starts[k + 1] if k + 1 < len(starts) else b)) for k, s in enumerate(starts)]
        for g in seg['groups']:
            for st in g['staves']:
                if not any('RemoveAllEmptyStaves' in x or 'RemoveEmptyStaves' in x for x in st.get('with', [])):
                    continue
                for s0, s1 in systems:
                    empty = True
                    for pid, vk in st['voices']:
                        p = score.part(pid)
                        for i in range(s0, s1):
                            for ev in p.measures[i].get(vk, []):
                                if ev.kind == 'note':
                                    empty = False
                    if empty:
                        for pid, vk in st['voices']:
                            p = score.part(pid)
                            for i in range(s0, s1):
                                for ev in p.measures[i].get(vk, []):
                                    if ev.kind == 'rest':
                                        ev.hidden = True
                        hidden_report.append({'staff': st['id'], 'measures': [score.measures[s0].number,
                                                                              score.measures[s1 - 1].number]})
    return hidden_report


def lyric_text_check(score, pdf):
    rc, out, err = run(['pdftotext', '-layout', pdf, '-'])
    text = re.sub(r'\s+', ' ', out)
    flat = text.replace('-', '').replace(' ', '')
    syls = []
    for pid, vk, vs in voices_with_lyrics(score):
        p = score.part(pid)
        for m in p.measures:
            for ev in m.get(vk, []):
                for ly in ev.lyrics.values():
                    syls.append(ly.text)
    if not syls:
        return None, 0
    found = 0
    for s_ in syls:
        core = re.sub(r'[\W_]+', '', s_)
        if not core or core in flat or s_ in text:
            found += 1
    return round(found / len(syls), 4), len(syls)


def render_pages(pdf, dpi, workdir, tag):
    prefix = os.path.join(workdir, f'r{tag}{dpi}')
    for f in glob.glob(prefix + '-*.pgm'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=900)
    files = sorted(glob.glob(prefix + '-*.pgm'))
    return [np.array(Image.open(f), dtype=np.uint8) for f in files]


def image_only(pdf, n_expected):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    return {'fonts': len(font_lines), 'images': n_imgs, 'pages': pages, 'text_chars': len(txt.strip()),
            'image_only': not font_lines and n_imgs == pages == n_expected and not txt.strip()}


def build_item(item: dict, keep_work=False):
    t0 = time.time()
    iid = item['id']
    outdir = os.path.join(ROOT, iid)
    workdir = os.path.join(ROOT, '_work', iid)
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    log = {'id': iid}
    try:
        score, layout, opts = item['make']()
        sanitize_ties(score)
        fix_unbalanced_slurs(score)
        compute_extenders(score)
        check(score)
        hidden = mark_hidden_rests(score, layout)
        log['hidden_staves'] = hidden
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        rc, out, err = run(['xmllint', '--noout', '--schema', XSD, truth])
        log['xsd'] = {'rc': rc, 'msg': (out + err).strip()[-500:]}
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err[-1500:])
        # music21 sanity parse
        rc, out, err = run(['/Users/d.sloane/music/.venv/bin/python', '-c',
                            'import sys,music21;s=music21.converter.parse(sys.argv[1]);'
                            'print(len(s.parts), len(s.flatten().notes))', truth])
        log['music21'] = (out or err).strip()[-300:]
        if rc != 0:
            raise RuntimeError('music21 parse failed: ' + err[-800:])
        ly = os.path.join(workdir, 'engraving.ly')
        with open(ly, 'w', encoding='utf-8') as f:
            f.write(LilyWriter(score, layout, opts).document())
        rc, out, err = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files', '-o', 'engraving',
                            'engraving.ly'], cwd=workdir)
        warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
        log['lilypond'] = {'rc': rc, 'warnings': warns[:40]}
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-3000:])
        bad = [w for w in warns if 'barcheck' in w or 'error' in w or 'programming' in w]
        if bad:
            raise RuntimeError('lilypond bar-check/errors: ' + '\n'.join(bad[:10]))
        pdf = os.path.join(workdir, 'engraving.pdf')
        segs = segments_of(score, layout)
        offs = score.measure_offsets()
        mids = []
        for k, seg in enumerate(segs):
            p = os.path.join(workdir, 'engraving.midi' if k == 0 else f'engraving-{k}.midi')
            mids.append((p, offs[seg['start']]))
        cmp_ = compare_multi(score, mids)
        log['midi'] = cmp_
        if not cmp_['ok']:
            raise RuntimeError('MIDI vs truth mismatch: ' + json.dumps(cmp_))
        rc, info, _ = run(['pdfinfo', pdf])
        npages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        log['pages'] = npages
        if item.get('pages') and npages != item['pages']:
            raise RuntimeError(f'page count {npages} != planned {item["pages"]}')
        lyr_found, n_syl = lyric_text_check(score, pdf)
        log['lyric_text_found'] = lyr_found
        if lyr_found is not None and lyr_found < 1.0:
            raise RuntimeError(f'lyric syllables missing from engraving: {lyr_found}')
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        shutil.copy(pdf, os.path.join(workdir, 'vector.pdf'))
        # ---------------- rasterise + damage
        cache = {}

        def pages_at(dpi):
            if dpi not in cache:
                cache[dpi] = render_pages(pdf, dpi, workdir, 'p')
            return cache[dpi]

        clean_dpi = item.get('clean_dpi', 300)
        clean_pages = pages_at(clean_dpi)
        D.save_pdf([Image.fromarray(p) for p in clean_pages], clean_dpi, os.path.join(outdir, 'clean.pdf'), fmt='png')
        degr = {}
        checks = {'clean.pdf': image_only(os.path.join(outdir, 'clean.pdf'), npages)}
        for fname, spec in item['scans'].items():
            P = dict(spec['params'])
            seed = spec['seed']
            pages = pages_at(P['dpi'])
            outs = D.degrade_document(pages, P, seed)
            imgs = [o[0] for o in outs]
            out_dpi = P.get('out_dpi', P['dpi'])
            fmt = P.get('format', 'jpeg')
            path = os.path.join(outdir, fname)
            D.save_pdf(imgs, out_dpi, path, fmt='png' if fmt in ('png', 'png1') else 'jpeg',
                       quality=P.get('jpeg', 75))
            if fmt == 'jpeg':
                pass
            chk = image_only(path, len(imgs))
            checks[fname] = chk
            if not chk['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {chk}')
            degr[fname] = {
                'seed': seed,
                'render_dpi': P['dpi'],
                'dpi': out_dpi,
                'format': fmt if fmt != 'jpeg' else f'jpeg q{P.get("jpeg", 75)}',
                'colour': 'bw' if (P.get('binarize') or P.get('mode') == 'bw') else P.get('mode', 'rgb'),
                'pdf_pages': [{'image': k + 1, 'source_pages': o[2], 'size_px': list(o[0].size),
                               'ops': o[1]} for k, o in enumerate(outs)],
                'params': P,
                'summary': spec.get('summary', ''),
                'bytes': os.path.getsize(path),
            }
        log['image_checks'] = checks
        # ---------------- metadata
        parts = [p.name for p in score.parts]
        lyr = [{'part': score.part(pid).name, 'verses': len(vs)} for pid, vk, vs in voices_with_lyrics(score)]
        n_notes = sum(1 for p in score.parts for m in p.measures for evs in m.values() for e in evs
                      if e.kind == 'note' for _ in e.pitches)
        meta = {
            'id': iid,
            'category': CATEGORY,
            'title': item['title'],
            'edge_cases': item['edge_cases'],
            'expected': {
                'parts': parts,
                'must_not_split': item['must_not_split'],
                'shared_staves': item.get('shared_staves', []),
                'staves_per_part': {p.name: p.staves for p in score.parts},
                'lyrics': lyr,
                'notes': item['expected_notes'],
            },
            'truth_limitations': item.get('truth_limitations', ''),
            'layout': item.get('layout_desc', ''),
            'pages': npages,
            'measures': len(score.measures),
            'notes_in_truth': n_notes,
            'hidden_staff_systems': hidden,
            'dpi': degr['scan.pdf']['dpi'],
            'degradations': degr,
            'files': sorted(os.listdir(outdir)) + ['meta.json', 'ATTRIBUTION.txt'],
            'license': item['license'],
            'source': item['source'],
            'engraver': 'internal model -> LilyPond 2.24 (custom writer, layout-challenge edition)',
            'validation': {
                'xsd_valid': True,
                'music21_parse': log['music21'],
                'midi_attacks_match_truth': True,
                'attacks': cmp_['expected_attacks'],
                'lilypond_warnings': warns[:20],
                'lyric_syllables_found_in_engraving': lyr_found,
                'lyric_syllables': n_syl,
                'pages_planned': item.get('pages'),
                'image_only': {k: v['image_only'] for k, v in checks.items()},
            },
        }
        meta['files'] = sorted(set(meta['files']))
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(item['attribution'].strip() + '\n')
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)[:6000]
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
