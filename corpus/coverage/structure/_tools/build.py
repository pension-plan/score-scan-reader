"""Build one item of the coverage corpus, structure family.

Pipeline (the item fails on any mismatch):
  model (items/*.py) -> explicit beams + stems (ssynth/notation.py)
  -> truth.musicxml (ssynth/mxl.py) -> xmllint against mvp/work/schema/musicxml.xsd -> music21 parse
  -> engraving.ly (ssynth/lily.py) -> LilyPond 2.24 with the event/grob dump (dump.ly)
  -> verification against the truth re-read from XML (ssynth/verify.py): notes, rests, ties, beams,
     slurs, stems, articulations, dynamics, lyrics, clefs/keys/times, bar-line glyphs, voltas,
     segno/coda/text marks, system/page layout (tagged second render, breaks.ly)
  -> LilyPond MIDI attacks == truth attacks (ssynth/midicheck.py) -> planned page count
  -> clean.pdf (300 dpi lossless raster) + scan.pdf + scan-severe.pdf (ssynth/degrade2.py, seeded)
  -> image-only check (pdffonts/pdfimages/pdftotext) -> symbol counts (ssynth/counts.py) -> meta.json
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

import numpy as np
from PIL import Image

from ssynth import degrade2 as D
from ssynth.counts import __doc__ as COUNT_RULES
from ssynth.counts import count_truth
from ssynth.lily import LilyWriter
from ssynth.midicheck import compare_multi
from ssynth.model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics
from ssynth.mxl import write_musicxml
from ssynth.notation import prepare
from ssynth.verify import DUMP, break_render, compare

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)                       # corpus/coverage/structure
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
PY = '/Users/d.sloane/music/.venv/bin/python'
FAMILY = 'structure'


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def staff_map(score, layout):
    """{lilypond staff id: (part id, staff number)}"""
    out = {}
    segs = layout.get('segments') or [{'groups': layout['groups']}]
    for seg in segs:
        for g in seg['groups']:
            for st in g['staves']:
                pid, vk = st['voices'][0]
                out[st['id']] = (pid, score.part(pid).voice(vk).staff)
    return out


def lyric_text_check(score, pdf):
    rc, out, err = run(['pdftotext', '-layout', pdf, '-'])
    text = re.sub(r'\s+', ' ', out)
    flat = text.replace('-', '').replace(' ', '')
    syls = [ly.text for pid, vk, vs in voices_with_lyrics(score) for m in score.part(pid).measures
            for ev in m.get(vk, []) for ly in ev.lyrics.values()]
    if not syls:
        return None, 0
    found = sum(1 for s in syls if not re.sub(r'[\W_]+', '', s) or re.sub(r'[\W_]+', '', s) in flat or s in text)
    return round(found / len(syls), 4), len(syls)


def render_pages(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'r{dpi}')
    for f in glob.glob(prefix + '-*.pgm'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=900)
    return [np.array(Image.open(f), dtype=np.uint8) for f in sorted(glob.glob(prefix + '-*.pgm'))]


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
        prepare(score)
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        rc, out, err = run(['xmllint', '--noout', '--schema', XSD, truth], timeout=300)
        log['xsd'] = {'rc': rc, 'msg': (out + err).strip()[-300:]}
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err[-1500:])
        rc, out, err = run([PY, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1]);'
                                      'print(len(s.parts), len(s.flatten().notes))', truth], timeout=600)
        log['music21'] = (out or err).strip()[-300:]
        if rc != 0:
            raise RuntimeError('music21 parse failed: ' + err[-800:])
        ly = os.path.join(workdir, 'engraving.ly')
        with open(ly, 'w', encoding='utf-8') as f:
            f.write(LilyWriter(score, layout, opts).document())
        rc, out, err = run(['lilypond', '-dno-point-and-click', f'-dinclude-settings={DUMP}', '-o', 'engraving',
                            'engraving.ly'], cwd=workdir)
        warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
        log['lilypond'] = {'rc': rc, 'warnings': warns[:40]}
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-3000:])
        if warns:
            raise RuntimeError('lilypond warnings/errors: ' + '\n'.join(warns[:10]))
        pdf = os.path.join(workdir, 'engraving.pdf')
        # ---------------- engraving == truth
        pages_brk = break_render(ly, workdir)
        rep, T = compare(truth, os.path.join(workdir, 'engraving.events'), staff_map(score, layout), pages_brk)
        log['verify'] = rep
        if not rep['ok']:
            bad = {k: v for k, v in rep.items() if isinstance(v, dict) and v.get('ok') is False}
            for grp in ('voices', 'lyrics', 'staves', 'barlines'):
                bad.update({f'{grp}:{k}': v for k, v in rep[grp].items() if not v.get('ok')})
            raise RuntimeError('engraving vs truth mismatch: ' + json.dumps(bad, default=str)[:4000])
        offs = score.measure_offsets()
        cmp_ = compare_multi(score, [(os.path.join(workdir, 'engraving.midi'), offs[0])])
        log['midi'] = cmp_
        if not cmp_['ok']:
            raise RuntimeError('MIDI vs truth mismatch: ' + json.dumps(cmp_))
        rc, info, _ = run(['pdfinfo', pdf])
        npages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        log['pages'] = npages
        if npages != item['pages']:
            raise RuntimeError(f'page count {npages} != planned {item["pages"]}')
        lyr_found, n_syl = lyric_text_check(score, pdf)
        if lyr_found is not None and lyr_found < 1.0:
            raise RuntimeError(f'lyric syllables missing from engraving: {lyr_found}')
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # ---------------- rasterise + damage
        cache = {}

        def pages_at(dpi):
            if dpi not in cache:
                cache[dpi] = render_pages(pdf, dpi, workdir)
            return cache[dpi]

        clean_dpi = 300
        D.save_pdf([Image.fromarray(p) for p in pages_at(clean_dpi)], clean_dpi, os.path.join(outdir, 'clean.pdf'),
                   fmt='png')
        checks = {'clean.pdf': image_only(os.path.join(outdir, 'clean.pdf'), npages)}
        degr = {'clean.pdf': {'seed': None, 'render_dpi': clean_dpi, 'dpi': clean_dpi, 'format': 'png (lossless)',
                              'colour': 'gray', 'params': {}, 'summary': 'undamaged raster of the engraving'}}
        for fname, spec in item['scans'].items():
            P = dict(spec['params'])
            outs = D.degrade_document(pages_at(P['dpi']), P, spec['seed'])
            imgs = [o[0] for o in outs]
            out_dpi = P.get('out_dpi', P['dpi'])
            fmt = P.get('format', 'jpeg')
            path = os.path.join(outdir, fname)
            D.save_pdf(imgs, out_dpi, path, fmt='png' if fmt in ('png', 'png1') else 'jpeg', quality=P.get('jpeg', 75))
            chk = image_only(path, len(imgs))
            checks[fname] = chk
            if not chk['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {chk}')
            degr[fname] = {
                'seed': spec['seed'], 'render_dpi': P['dpi'], 'dpi': out_dpi,
                'format': fmt if fmt != 'jpeg' else f'jpeg q{P.get("jpeg", 75)}',
                'colour': 'bw' if (P.get('binarize') or P.get('mode') == 'bw') else P.get('mode', 'rgb'),
                'params': P, 'summary': spec['summary'], 'bytes': os.path.getsize(path),
                'pdf_pages': [{'image': k + 1, 'source_pages': o[2], 'size_px': list(o[0].size), 'ops': o[1]}
                              for k, o in enumerate(outs)],
            }
        degr['clean.pdf']['bytes'] = os.path.getsize(os.path.join(outdir, 'clean.pdf'))
        log['image_checks'] = checks
        # ---------------- counts + metadata
        counts, by_part = count_truth(truth, npages)
        missing_focus = [t for t in item['focus'] if t not in counts]
        if missing_focus:
            raise RuntimeError(f'focus symbols absent from truth: {missing_focus}')
        for tag, n in item.get('expect_counts', {}).items():
            if counts.get(tag) != n:
                raise RuntimeError(f'count of {tag} is {counts.get(tag)}, planned {n}')
        n_notes = sum(1 for p in score.parts for m in p.measures for evs in m.values() for e in evs
                      if e.kind == 'note' for _ in e.pitches)
        lyr = [{'part': score.part(pid).name, 'verses': len(vs)} for pid, vk, vs in voices_with_lyrics(score)]
        meta = {
            'id': iid,
            'family': FAMILY,
            'title': item['title'],
            'symbols': sorted(counts),
            'focus_symbols': item['focus'],
            'layout': item['layout'],
            'expected': {
                'parts': [p.name for p in score.parts],
                'must_not_split': item['must_not_split'],
                'staves_per_part': {p.name: p.staves for p in score.parts},
                'lyrics': lyr,
                'structure': item['structure'],
                'notes': item['expected_notes'],
            },
            'counts': counts,
            'counts_by_part': by_part,
            'count_rules': COUNT_RULES.strip(),
            'degradations': degr,
            'dpi': degr['scan.pdf']['dpi'],
            'pages': npages,
            'systems_per_page': [len(p) for p in pages_brk],
            'system_start_measures': pages_brk,
            'measures': len(score.measures),
            'noteheads_in_truth': n_notes,
            'license': 'CC0',
            'license_detail': 'CC0 1.0 Universal - composition, engraving, truth and scans',
            'notes': item['notes'],
            'files': ['ATTRIBUTION.txt', 'clean.pdf', 'engraving.ly', 'meta.json', 'truth.musicxml'] + sorted(item['scans']),
            'generator': 'corpus/coverage/structure/_tools (model -> MusicXML 4.0 truth + LilyPond 2.24 engraving)',
            'validation': {
                'xsd_valid': True,
                'music21_parse': log['music21'],
                'engraving_matches_truth': True,
                'checked': ['notes', 'rests', 'full-bar rests', 'ties', 'beams', 'slurs', 'stems', 'articulations',
                            'dynamics/hairpins/text', 'lyrics', 'clefs', 'keys', 'times', 'bar-line glyphs',
                            'volta spans', 'segno/coda/text/rehearsal/metronome marks', 'system and page starts',
                            'MIDI attacks'],
                'midi_attacks': cmp_['expected_attacks'],
                'lilypond_warnings': warns,
                'lyric_syllables_found_in_engraving': lyr_found,
                'image_only': {k: v['image_only'] for k, v in checks.items()},
            },
        }
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
