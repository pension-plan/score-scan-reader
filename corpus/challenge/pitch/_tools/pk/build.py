"""Build one pitch-challenge item:
  model -> truth.musicxml (MusicXML 4.0, XSD-validated with xmllint)
        -> engraving.ly (custom LilyPond writer) -> vector PDF + MIDI
  checks: (1) LilyPond MIDI (one track per Voice) == truth (onset, pitch) multiset, read
              back from truth.musicxml itself (independent XML reader) and from the model
          (2) instrumented engraving: printed accidentals / clefs / key signatures /
              cancellations / ottava brackets == model (rendercheck)
          (3) lyric syllables present in the vector PDF text; no bar-check warnings
  raster (pdftoppm) -> scanfx damage pipelines -> scan*.pdf (image only, verified with
  pdffonts / pdfimages / pdftotext) + clean.pdf (undamaged 300 dpi raster)
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
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction as F

import numpy as np
from PIL import Image

from . import scanfx as S
from .lily import LilyWriter
from .midicheck import compare, read_midi
from .model import STEP_PC, check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics
from .mxl import write_musicxml
from .rendercheck import check as render_check, parse_log

CAT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/challenge/pitch
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
CC0_NOTE = ('Composition, engraving, rasterisation and damage simulation produced for the pitch challenge corpus '
            '(corpus/challenge/pitch/_tools); dedicated to the public domain (CC0 1.0).')


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly_path, workdir):
    base = os.path.splitext(os.path.basename(ly_path))[0]
    rc, out, err = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files', '-o', base,
                        os.path.basename(ly_path)], cwd=workdir)
    warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
    midi = None
    for ext in ('.midi', '.mid'):
        if os.path.exists(os.path.join(workdir, base + ext)):
            midi = os.path.join(workdir, base + ext)
    return rc, warns, os.path.join(workdir, base + '.pdf'), midi, err


def truth_attacks(path):
    """independent reader: (onset quarters, midi) multiset straight from truth.musicxml"""
    root = ET.parse(path).getroot()
    out = Counter()
    lyr = []
    for part in root.findall('part'):
        div = 1
        t0 = F(0)
        for meas in part.findall('measure'):
            pos = F(0)
            last_onset = F(0)
            mlen = F(0)
            for el in meas:
                if el.tag == 'attributes':
                    d = el.find('divisions')
                    if d is not None:
                        div = int(d.text)
                elif el.tag == 'backup':
                    pos -= F(int(el.find('duration').text), div)
                elif el.tag == 'forward':
                    pos += F(int(el.find('duration').text), div)
                elif el.tag == 'note':
                    dur = F(int(el.find('duration').text), div)
                    if el.find('chord') is not None:
                        onset = last_onset
                    else:
                        onset = pos
                        pos += dur
                    last_onset = onset
                    p = el.find('pitch')
                    if p is not None:
                        ties = [t.get('type') for t in el.findall('tie')]
                        if 'stop' not in ties:
                            alt = p.find('alter')
                            m = 12 * (int(p.find('octave').text) + 1) + STEP_PC[p.find('step').text] + \
                                (int(alt.text) if alt is not None else 0)
                            out[(t0 + onset, m)] += 1
                    for ly in el.findall('lyric'):
                        lyr.append(ly.find('text').text)
                mlen = max(mlen, pos)
            t0 += mlen
    return out, lyr


def midi_attacks(midi_path):
    div, tracks = read_midi(midi_path)
    got = Counter()
    for tr in tracks:
        for t, p in tr['notes']:
            got[(F(t, div), p)] += 1
    return got


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
        return None
    found = sum(1 for s_ in syls if (re.sub(r'[\W_]+', '', s_) or '') in flat or s_ in text)
    return round(found / len(syls), 4)


def render_gray(pdf, dpi, workdir, tag='g'):
    prefix = os.path.join(workdir, f'{tag}{dpi}')
    for f in glob.glob(prefix + '-*'):
        os.remove(f)
    run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix])
    files = sorted(glob.glob(prefix + '-*.pgm'))
    return [np.array(Image.open(f), dtype=np.uint8) for f in files]


def render_color(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'c{dpi}')
    for f in glob.glob(prefix + '-*'):
        os.remove(f)
    run(['pdftoppm', '-png', '-r', str(dpi), '-aa', 'no', '-aaVector', 'no', pdf, prefix])
    return sorted(glob.glob(prefix + '-*.png'))


def image_only(pdf):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    return {'fonts': len(font_lines), 'images': n_imgs, 'pages': pages, 'text_chars': len(txt.strip()),
            'image_only': not font_lines and n_imgs == pages and not txt.strip()}


def build_item(item: dict, keep_work=False):
    t0 = time.time()
    iid = item['id']
    outdir = os.path.join(CAT_ROOT, iid)
    workdir = os.path.join(CAT_ROOT, '_work', iid)
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
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        rc, out, err = run(['xmllint', '--noout', '--nonet', '--schema', XSD, truth])
        log['xsd_valid'] = rc == 0
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err[-1500:])
        # engraving (clean) + instrumented twin
        ly = os.path.join(workdir, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts).document())
        rc, warns, pdf, mid, _err = lilypond(ly, workdir)
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + _err[-3000:])
        lyi = os.path.join(workdir, 'instr.ly')
        open(lyi, 'w', encoding='utf-8').write(LilyWriter(score, layout, dict(opts, instrument=True)).document())
        rci, warns_i, pdf_i, _mid_i, err_i = lilypond(lyi, workdir)
        if rci != 0:
            raise RuntimeError('instrumented lilypond failed: ' + err_i[-3000:])
        bad_warn = [w for w in warns if 'barcheck' in w or 'error' in w or 'bar check' in w]
        log['warnings'] = warns[:30]
        if bad_warn:
            raise RuntimeError(f'bar-check warnings: {bad_warn[:5]}')
        # (1) MIDI vs model and vs truth file
        cmp_model = compare(score, mid)
        got = midi_attacks(mid)
        tr, tr_lyr = truth_attacks(truth)
        cmp_truth = {'ok': got == tr, 'n_truth': sum(tr.values()), 'n_midi': sum(got.values()),
                     'missing': [str(x) for x in list((tr - got).elements())[:10]],
                     'extra': [str(x) for x in list((got - tr).elements())[:10]]}
        log['midi_vs_model'] = cmp_model
        log['midi_vs_truth_file'] = cmp_truth
        if not cmp_model['ok'] or not cmp_truth['ok']:
            raise RuntimeError(f'MIDI mismatch: model {cmp_model} truth {cmp_truth}')
        # (2) render log
        rows = parse_log(err_i)
        rchk = render_check(score, layout, rows)
        log['render_check'] = rchk
        if not rchk['ok']:
            raise RuntimeError(f'render check failed: {json.dumps(rchk, default=str)[:4000]}')
        # (3) lyrics
        log['lyric_text_found'] = lyric_text_check(score, pdf)
        if log['lyric_text_found'] is not None and log['lyric_text_found'] < 1.0:
            raise RuntimeError(f'lyrics not all found in vector PDF: {log["lyric_text_found"]}')
        # layout identity of instrumented twin
        g_clean = render_gray(pdf, 100, workdir, 'lc')
        g_inst = render_gray(pdf_i, 100, workdir, 'li')
        log['twin_layout_diff'] = float(np.mean([np.mean(np.abs(a.astype(int) - b.astype(int)) > 60)
                                                 for a, b in zip(g_clean, g_inst)])) if len(g_clean) == len(g_inst) else 1.0
        if log['twin_layout_diff'] > 0.002:
            raise RuntimeError(f'instrumented layout differs: {log["twin_layout_diff"]}')
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # clean raster
        clean_dpi = 300
        cpages = render_gray(pdf, clean_dpi, workdir)
        S.save_pdf([Image.fromarray(p) for p in cpages], clean_dpi, os.path.join(outdir, 'clean.pdf'), fmt='png')
        # damaged files
        ss_pt = opts.get('staff_size', 20) / 4.0
        degr = {}
        files = {}
        for fname, spec in item['damage'].items():
            dpi = spec['dpi']
            grays = render_gray(pdf, dpi, workdir)
            ctx = {'staff_space_px': ss_pt * dpi / 72.0,
                   'staff_extent': [S.staff_extent(g, dpi) for g in grays]}
            if any(o['op'] == 'pencil' for o in spec['ops']):
                cps = render_color(pdf_i, dpi, workdir)
                ctx['anchors'] = [S.find_anchors(c, dpi, ctx['staff_space_px']) for c in cps]
            imgs, mode, plog = S.run_pipeline(grays, spec, dpi, spec['seed'], ctx)
            outp = os.path.join(outdir, fname)
            fmt = 'png' if mode == '1' or spec.get('format') == 'png' else 'jpeg'
            S.save_pdf(imgs, dpi, outp, fmt=fmt, quality=spec.get('jpeg', 75), passes=spec.get('jpeg_passes', 1))
            io_ = image_only(outp)
            if not io_['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {io_}')
            files[fname] = io_
            degr[fname] = {
                'dpi': dpi, 'seed': spec['seed'], 'color': {'RGB': 'rgb', 'L': 'gray', '1': 'bilevel'}[mode],
                'encoding': 'png (1-bit)' if mode == '1' else ('png' if fmt == 'png' else
                                                                f'jpeg q{spec.get("jpeg", 75)}'
                                                                + (f' x{spec.get("jpeg_passes")} passes'
                                                                   if spec.get('jpeg_passes', 1) > 1 else '')),
                'pages_in_pdf': io_['pages'], 'pixel_size': [imgs[0].size[0], imgs[0].size[1]],
                'summary': spec.get('summary', ''),
                'ops': spec['ops'],
            }
            if plog.get('pencil'):
                degr[fname]['pencil_marks'] = plog['pencil']
            if plog.get('crop_px'):
                degr[fname]['crop_px_LRTB'] = plog['crop_px']
        log['files'] = files
        # metadata
        parts = [p.name for p in score.parts]
        notes = item['notes']
        meta = {
            'id': iid, 'category': 'pitch', 'title': item['title'],
            'edge_cases': item['edge_cases'],
            'expected': {
                'parts': parts,
                'must_not_split': item.get('must_not_split', False),
                'shared_staves': item.get('shared_staves', []),
                'lyrics': [{'part': score.part(pid).name, 'verses': len(vs)} for pid, vk, vs in voices_with_lyrics(score)],
                'notes': notes,
            },
            'truth_limitations': item.get('truth_limitations', []),
            'degradations': degr,
            'dpi': {k: v['dpi'] for k, v in degr.items()},
            'clean_pdf': {'dpi': clean_dpi, 'note': 'undamaged 300 dpi grey raster of the LilyPond engraving (image only)'},
            'license': item['license'],
            'source': item['source'],
            'measures': len(score.measures), 'pages': len(cpages),
            'layout': item.get('layout_desc', ''),
            'validation': {
                'xsd_valid': True,
                'midi_attacks_match_truth_file': True,
                'attacks': cmp_truth['n_truth'],
                'printed_accidentals_match': True,
                'accidentals': {k: v for k, v in rchk['accidentals'].items() if k not in ('missing', 'extra', 'different')},
                'clefs': rchk['clefs'], 'keys': rchk['keys'], 'ottava': rchk['ottava'],
                'systems': rchk['systems'], 'line_start_measures': rchk['line_start_measures'],
                'lyric_text_found_in_engraving': log['lyric_text_found'],
                'scan_files_image_only': {k: v['image_only'] for k, v in files.items()},
            },
            'files': ['engraving.ly', 'truth.musicxml', 'clean.pdf'] + list(item['damage'].keys()) +
                     ['meta.json', 'ATTRIBUTION.txt'],
        }
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, default=str, ensure_ascii=False)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(item['attribution'].strip() + '\n\n' + CC0_NOTE + '\n')
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)
        log['trace'] = traceback.format_exc()[-5000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
