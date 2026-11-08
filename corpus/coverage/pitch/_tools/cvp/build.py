"""Build one coverage-suite item (pitch family).  Derived from corpus/challenge/pitch/_tools/pk/build.py.
Order: engraving + instrumented twin first, then the engraved stems/beams are copied into the model,
then the truth is written and checked.  Original description:
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
from .rendercheck import annotate_stems, check as render_check, notehead_positions, parse_log
from .counts import CONVENTIONS, count_truth
from .acc import layout_staves

CAT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/coverage/pitch
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
CC0_NOTE = ('Composition, engraving, rasterisation and damage simulation produced for the OMR coverage suite '
            '(corpus/coverage/pitch/_tools, derived from corpus/challenge/pitch/_tools); dedicated to the public '
            'domain (CC0 1.0).')
VENV_PY = '/Users/d.sloane/music/.venv/bin/python'


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



def _dilate(m):
    out = m.copy()
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    o2 = out.copy()
    o2[:, 1:] |= out[:, :-1]
    o2[:, :-1] |= out[:, 1:]
    return o2


def twin_diff(a, b):
    """fraction of pixels that are ink in one render but have no ink within 1 px in the other
    (tolerates anti-aliasing differences of the coloured note heads, catches any layout shift)"""
    ma, mb = a < 200, b < 200
    return float(np.mean((ma & ~_dilate(mb)) | (mb & ~_dilate(ma))))


def music21_check(path):
    code = ('import sys, music21\n'
            's = music21.converter.parse(sys.argv[1], format="musicxml")\n'
            'n = len(s.recurse().notes); r = len(s.recurse().getElementsByClass("Rest"))\n'
            'print(len(s.parts), n, r)\n')
    rc, out, err = run([VENV_PY, '-c', code, path], timeout=300)
    if rc != 0:
        return {'ok': False, 'error': err[-800:]}
    a = out.split()
    return {'ok': True, 'parts': int(a[0]), 'notes_and_chords': int(a[1]), 'rests': int(a[2])}


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
        ost = opts.get('ottava_style', 'numbers')
        # ---- engraving (clean) + instrumented twin
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
        log['warnings'] = warns[:30]
        if warns:
            raise RuntimeError(f'lilypond warnings: {warns[:5]}')
        rows = parse_log(err_i)
        rchk = render_check(score, layout, rows, ost)
        log['render_check'] = rchk
        if not rchk['ok']:
            raise RuntimeError(f'render check failed: {json.dumps(rchk, default=str)[:4000]}')
        # every system break is explicit -> <print new-system> in the truth is exact
        exp_ls = [1] + [i + 1 for i, m in enumerate(score.measures) if m.brk and i > 0]
        if rchk['line_start_measures'] != exp_ls:
            raise RuntimeError(f'system starts {rchk["line_start_measures"]} != explicit breaks {exp_ls}')
        stem_rep = annotate_stems(score, layout, rows)
        log['stems'] = stem_rep
        # ---- truth
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        rc, out, err = run(['xmllint', '--noout', '--nonet', '--schema', XSD, truth])
        log['xsd_valid'] = rc == 0
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err[-1500:])
        m21 = music21_check(truth)
        log['music21'] = m21
        if not m21['ok']:
            raise RuntimeError('music21 parse failed: ' + m21['error'])
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
        # (2) counts from the truth file + cross-checks against the engraving log
        counts, positions = count_truth(truth)
        sid_of = {}
        for sid, voices in layout_staves(layout):
            for pid, vk in voices:
                sid_of[(pid, score.part(pid).voice(vk).staff)] = sid
        nh = notehead_positions(rows)
        pos_bad = []
        npos = 0
        for (pid, st, onset, pit), sp in positions.items():
            k = (sid_of[(pid, st)], onset, pit)
            npos += 1
            if nh.get(k) != sp:
                pos_bad.append(f'{k}: truth {sp} engraved {nh.get(k)}')
        if pos_bad or npos != len(nh):
            raise RuntimeError(f'notehead staff positions differ ({npos} truth / {len(nh)} engraved): {pos_bad[:8]}')
        acc = rchk['accidentals']
        n_acc = sum(v for k, v in counts.items() if k.startswith('acc-') and k != 'acc-courtesy') + \
            counts.get('x-acc-natural-sharp', 0) + counts.get('x-acc-natural-flat', 0)
        xchk = {
            'accidentals_truth_vs_printed': [n_acc, acc['printed']],
            'double_accidentals_truth_vs_printed': [counts.get('acc-double-sharp', 0) + counts.get('acc-double-flat', 0),
                                                    acc['double']],
            'extra_naturals_truth_vs_printed': [counts.get('x-acc-natural-sharp', 0) + counts.get('x-acc-natural-flat', 0),
                                                acc['extra_natural']],
            'parenthesized_truth_vs_printed': [counts.get('x-acc-courtesy-paren', 0), acc['parenthesized']],
            'stems_up_truth_vs_engraved': [counts.get('stem-up', 0), stem_rep['up']],
            'stems_down_truth_vs_engraved': [counts.get('stem-down', 0), stem_rep['down']],
            'flags_truth_vs_engraved': [counts.get('flag', 0), stem_rep['flags']],
            'beam_groups_truth_vs_engraved': [counts.get('beam', 0), stem_rep['beam_groups']],
            'clef_changes_truth_vs_engraved': [counts.get('clef-change', 0),
                                               sum(v['rendered_changes'] for v in rchk['clefs'].values())],
            'system_breaks_truth_vs_engraved': [counts.get('system-break', 0) + counts.get('page-break', 0),
                                                rchk['systems'] - 1],
            'noteheads_with_positions_checked': [npos, len(nh)],
        }
        bad = {k: v for k, v in xchk.items() if v[0] != v[1]}
        log['cross_checks'] = xchk
        if bad:
            raise RuntimeError(f'truth counts differ from the engraving: {bad}')
        # (3) lyrics
        log['lyric_text_found'] = lyric_text_check(score, pdf)
        if log['lyric_text_found'] is not None and log['lyric_text_found'] < 1.0:
            raise RuntimeError(f'lyrics not all found in vector PDF: {log["lyric_text_found"]}')
        # layout identity of instrumented twin
        g_clean = render_gray(pdf, 100, workdir, 'lc')
        g_inst = render_gray(pdf_i, 100, workdir, 'li')
        log['twin_layout_diff_exact'] = float(np.mean([np.mean((a < 200) != (b < 200))
                                                       for a, b in zip(g_clean, g_inst)])) if len(g_clean) == len(g_inst) else 1.0
        log['twin_layout_diff'] = float(np.mean([twin_diff(a, b) for a, b in zip(g_clean, g_inst)])) \
            if len(g_clean) == len(g_inst) else 1.0
        if log['twin_layout_diff'] > 0.0002:
            raise RuntimeError(f'instrumented layout differs: {log["twin_layout_diff"]}')
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # clean raster
        clean_dpi = 300
        cpages = render_gray(pdf, clean_dpi, workdir)
        exp_pages = 1 + sum(1 for m in score.measures if m.brk == 'page')
        if len(cpages) != exp_pages:
            raise RuntimeError(f'{len(cpages)} pages engraved, {exp_pages} expected from explicit page breaks')
        if len(cpages) > 1:
            counts['multi-page'] = 1
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
                'dpi': dpi, 'seed': spec['seed'], 'level': spec.get('level', ''),
                'color': {'RGB': 'rgb', 'L': 'gray', '1': 'bilevel'}[mode],
                'encoding': 'png (1-bit)' if mode == '1' else ('png' if fmt == 'png' else
                                                                f'jpeg q{spec.get("jpeg", 75)}'
                                                                + (f' x{spec.get("jpeg_passes")} passes'
                                                                   if spec.get('jpeg_passes', 1) > 1 else '')),
                'pages_in_pdf': io_['pages'], 'pixel_size': [imgs[0].size[0], imgs[0].size[1]],
                'summary': spec.get('summary', ''),
                'ops': spec['ops'],
                'generator': 'corpus/coverage/pitch/_tools/cvp/scanfx.py run_pipeline(seed)',
            }
            if plog.get('pencil'):
                degr[fname]['pencil_marks'] = plog['pencil']
            if plog.get('crop_px'):
                degr[fname]['crop_px_LRTB'] = plog['crop_px']
        log['files'] = files
        counts = dict(sorted(counts.items()))
        missing_focus = [t for t in item['focus'] if not counts.get(t)]
        if missing_focus:
            raise RuntimeError(f'focus tags absent from truth: {missing_focus}')
        meta = {
            'id': iid, 'family': 'pitch', 'title': item['title'],
            'symbols': sorted(k for k, v in counts.items() if v),
            'focus': item['focus'],
            'layout': item['layout'],
            'expected': {
                'parts': [p.name for p in score.parts],
                'must_not_split': item.get('must_not_split', False),
                'staves': sum(p.staves for p in score.parts),
                'notes': item['expected_notes'],
            },
            'counts': counts,
            'count_conventions': CONVENTIONS,
            'degradations': degr,
            'dpi': dict({'clean.pdf': clean_dpi}, **{k: v['dpi'] for k, v in degr.items()}),
            'pages': len(cpages),
            'measures': len(score.measures),
            'systems': rchk['systems'],
            'license': 'CC0',
            'notes': item.get('truth_notes', []),
            'engraving': {'engraver': 'GNU LilyPond 2.24.3', 'paper': opts.get('paper', 'a4'),
                          'staff_size_pt': opts.get('staff_size', 20), 'ottava_style': ost,
                          'layout_desc': item.get('layout_desc', '')},
            'validation': {
                'xsd_valid': True,
                'music21': m21,
                'midi_attacks_match_truth_file': True,
                'attacks': cmp_truth['n_truth'],
                'printed_accidentals_match': True,
                'accidentals': {k: v for k, v in rchk['accidentals'].items() if k not in ('missing', 'extra', 'different')},
                'clefs': rchk['clefs'], 'keys': rchk['keys'], 'ottava': rchk['ottava'],
                'time_signatures': rchk['time_signatures'],
                'line_start_measures': rchk['line_start_measures'],
                'stems_beams_from_engraving': stem_rep,
                'truth_vs_engraving_cross_checks': xchk,
                'twin_layout_diff': log['twin_layout_diff'],
                'scan_files_image_only': {k: v['image_only'] for k, v in files.items()},
            },
            'source': item.get('source', 'composed for this corpus'),
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
