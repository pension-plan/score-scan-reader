"""Build one coverage item (lyrics family; copy of corpus/coverage/layouts/_tools/build.py).

model -> notation pre-pass (beams, stems, accidentals, printed staves)
      -> truth.musicxml (MusicXML 4.0) -> xmllint XSD -> music21 parse
      -> engraving.ly -> LilyPond 2.24 (with the cvlog.ly grob logger via -dinclude-settings; the .ly
         itself is plain) -> MIDI attacks == truth attacks, no bar-check warnings, planned page count,
         lyric syllables present in the vector PDF text, grob log == model (note heads, stems, flags,
         beams, accidentals per printed staff, rests, scripts, slurs, ties, dynamics, hairpins, lyrics,
         hyphens, extenders, chord names, tuplets, pedals, breaths, arpeggios, fingerings, brackets/braces)
      -> count_symbols(truth) -> meta.counts / meta.symbols
      -> clean.pdf (300 dpi raster), scan.pdf (typical scan), scan-severe.pdf (heavy damage)
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

import numpy as np
from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

from count_symbols import count_all  # noqa: E402
from csynth import degrade2 as D  # noqa: E402
from csynth.lily import LilyWriter  # noqa: E402
from csynth.midicheck import compare_multi  # noqa: E402
from csynth.model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics  # noqa
from csynth.mxl import write_musicxml  # noqa: E402
from csynth.notation import iter_staves, prepare, segments_of  # noqa: E402
from csynth.verify import compare as grob_compare, parse_log  # noqa: E402

ROOT = os.path.dirname(TOOLS)                       # corpus/coverage/lyrics
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
PY = '/Users/d.sloane/music/.venv/bin/python'
FAMILY = 'lyrics'
CVLOG = os.path.join(TOOLS, 'csynth', 'cvlog.ly')


def run(cmd, cwd=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def mark_hidden_rests(score, layout):
    """rests of voices absent from a \\score segment become print-object="no" in the truth"""
    rep = []
    for seg in segments_of(score, layout):
        a, b = seg['start'], seg['end']
        present = {tuple(v) for st in iter_staves(seg['groups']) for v in st['voices']}
        for p in score.parts:
            for v in p.voices:
                if (p.id, v.key) in present:
                    continue
                for i in range(a, b):
                    for ev in p.measures[i].get(v.key, []):
                        if ev.kind == 'note':
                            raise RuntimeError(f'voice {p.id}:{v.key} has notes in a segment without its staff')
                        if ev.kind == 'rest':
                            ev.hidden = True
                rep.append({'part': p.name, 'measures': [score.measures[a].number, score.measures[b - 1].number]})
    return rep


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
                   check=True, timeout=600)
    files = sorted(glob.glob(prefix + '-*.pgm'))
    return [np.array(Image.open(f), dtype=np.uint8) for f in files]


def _mm(opts, key, default):
    v = default
    for x in opts.get('paper_extra', []):
        m = re.match(rf'\s*{key}\s*=\s*([\d.]+)\\mm', x)
        if m:
            v = float(m.group(1))
    return v


def margin_check(pages, dpi, opts, tol_mm=1.5, left_tol_mm=4.0):
    """no ink right of the right margin / left of the left margin (overflowing systems or lyrics)"""
    rm, lm = _mm(opts, 'right-margin', 16.0), _mm(opts, 'left-margin', 18.0)
    px = dpi / 25.4
    res = {'ok': True, 'pages': []}
    for k, pg in enumerate(pages):
        ink = pg < 140
        cols = np.where(ink.any(axis=0))[0]
        if not len(cols):
            continue
        w = pg.shape[1]
        right_over = (cols.max() - (w - rm * px)) / px
        left_over = ((lm * px) - cols.min()) / px
        res['pages'].append({'page': k + 1, 'right_overflow_mm': round(float(right_over), 2),
                             'left_overflow_mm': round(float(left_over), 2)})
        if right_over > tol_mm or left_over > left_tol_mm:      # brackets / marks may sit in the left margin
            res['ok'] = False
    return res


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
        prep = prepare(score, layout, opts)
        log['acc_truth_differs_from_print'] = prep['acc_truth_differs_from_print']
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth, software='coverage suite builder (lyrics family)')
        rc, out, err = run(['xmllint', '--noout', '--schema', XSD, truth])
        log['xsd'] = {'rc': rc, 'msg': (out + err).strip()[-500:]}
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err[-1500:])
        rc, out, err = run([PY, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1]);'
                                      'print(len(s.parts), len(s.flatten().notes))', truth])
        log['music21'] = (out or err).strip()[-300:]
        if rc != 0:
            raise RuntimeError('music21 parse failed: ' + err[-800:])
        ly = os.path.join(workdir, 'engraving.ly')
        with open(ly, 'w', encoding='utf-8') as f:
            f.write(LilyWriter(score, layout, opts).document())
        rc, out, err = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files',
                            f'-dinclude-settings={CVLOG}', '-o', 'engraving', 'engraving.ly'], cwd=workdir)
        warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
        log['lilypond'] = {'rc': rc, 'warnings': warns[:40]}
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-3000:])
        bad = [w for w in warns if 'barcheck' in w or 'error' in w or 'programming' in w
               or 'compress' in w or 'not enough space' in w.lower()]
        if bad:
            raise RuntimeError('lilypond bar-check/errors: ' + '\n'.join(bad[:10]))
        allowed = item.get('allow_warnings', [])
        unexpected = [w for w in warns if not any(re.search(pat, w) for pat in allowed)]
        if unexpected:
            raise RuntimeError('lilypond warnings: ' + '\n'.join(unexpected[:10]))
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
        rows = parse_log(os.path.join(workdir, 'engraving.cvlog'))
        grep = grob_compare(score, layout, opts, prep, rows)
        log['grob_check'] = grep
        if not grep['ok']:
            raise RuntimeError('grob log vs truth mismatch: ' + json.dumps(grep['mismatch'], default=str)[:3000])
        counts = count_all(truth)
        # symbols printed by the engraving that MusicXML has no element for (stanza numbers): counted from the
        # model/engraving, declared in meta.symbols/counts and listed in printed_not_in_truth
        for k, v in item.get('engraving_only_counts', {}).items():
            counts[k] = v
        counts = dict(sorted(counts.items()))
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # ---------------- rasterise + damage
        cache = {}

        def pages_at(dpi):
            if dpi not in cache:
                cache[dpi] = render_pages(pdf, dpi, workdir, 'p')
            return cache[dpi]

        clean_dpi = 300
        clean_pages = pages_at(clean_dpi)
        mchk = margin_check(clean_pages, clean_dpi, opts)
        log['margin_check'] = mchk
        if not mchk['ok']:
            raise RuntimeError(f'ink outside the page margins: {mchk}')
        D.save_pdf([Image.fromarray(p) for p in clean_pages], clean_dpi, os.path.join(outdir, 'clean.pdf'), fmt='png')
        degr = {'clean.pdf': {'seed': None, 'dpi': clean_dpi, 'format': 'png (8-bit grey)', 'summary':
                              'undamaged raster of the engraving',
                              'pdf_pages': [{'image': k + 1, 'size_px': [p.shape[1], p.shape[0]]}
                                            for k, p in enumerate(clean_pages)],
                              'bytes': os.path.getsize(os.path.join(outdir, 'clean.pdf'))}}
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
            chk = image_only(path, len(imgs))
            checks[fname] = chk
            if not chk['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {chk}')
            degr[fname] = {
                'seed': seed, 'render_dpi': P['dpi'], 'dpi': out_dpi,
                'format': fmt if fmt != 'jpeg' else f'jpeg q{P.get("jpeg", 75)}',
                'colour': 'bw' if (P.get('binarize') or P.get('mode') == 'bw') else P.get('mode', 'rgb'),
                'pdf_pages': [{'image': k + 1, 'source_pages': o[2], 'size_px': list(o[0].size), 'ops': o[1]}
                              for k, o in enumerate(outs)],
                'params': P, 'summary': spec.get('summary', ''), 'bytes': os.path.getsize(path)}
        log['image_checks'] = checks
        # ---------------- metadata
        parts = [p.name for p in score.parts]
        lyr = [{'part': score.part(pid).name, 'verses': len(vs)} for pid, vk, vs in voices_with_lyrics(score)]
        symbols = [k for k in counts if not k.startswith('x-')] + [k for k in counts if k.startswith('x-')]
        notes = list(item.get('truth_limitations', []))
        pnt = item.get('printed_not_in_truth', {})
        for k, v in pnt.items():
            notes.append(f'Printed but not representable in the MusicXML truth: {k} x{v} (not in counts).')
        if prep['acc_truth_differs_from_print']:
            notes.append(f'Accidentals in the truth are per PART (what a per-part transcription displays): '
                         f'{prep["truth_acc_n"]} in the truth vs {prep["printed_acc_n"]} printed on the shared '
                         f'staves.')
        meta = {
            'id': iid,
            'family': FAMILY,
            'title': item['title'],
            'layout': item['layout'],
            'symbols': symbols,
            'counts': counts,
            'expected': {
                'parts': parts,
                'must_not_split': item['must_not_split'],
                'shared_staves': item.get('shared_staves', []),
                'staves_per_part': {p.name: p.staves for p in score.parts},
                'lyrics': lyr,
                'notes': item['expected_notes'],
            },
            'notes': notes,
            'printed_not_in_truth': pnt,
            'layout_description': item.get('layout_desc', ''),
            'pages': npages,
            'measures': len(score.measures),
            'systems': len(grep.get('systems_expected') and [1] * grep['systems_expected'] or []),
            'noteheads_in_truth': counts.get('x-noteheads', sum(len(e.pitches) for p in score.parts
                                                                for m in p.measures for evs in m.values()
                                                                for e in evs if e.kind == 'note')),
            'hidden_staff_segments': hidden,
            'dpi': degr['scan.pdf']['dpi'],
            'degradations': degr,
            'files': sorted(set(os.listdir(outdir)) | {'meta.json', 'ATTRIBUTION.txt'}),
            'license': 'CC0',
            'license_detail': item.get('license', 'CC0-1.0: composition, arrangement, engraving and scans'),
            'source': item.get('source', 'self-authored for the coverage suite (2026)'),
            'engraver': 'internal model -> LilyPond 2.24 (coverage-suite writer: explicit beams and stems)',
            'validation': {
                'xsd_valid': True,
                'music21_parse': log['music21'],
                'midi_attacks_match_truth': True,
                'attacks': cmp_['expected_attacks'],
                'grob_log_matches_truth': True,
                'printed_summary': grep['printed_summary'],
                'lilypond_warnings': warns[:20],
                'lyric_syllables_found_in_engraving': lyr_found,
                'lyric_syllables': n_syl,
                'pages_planned': item.get('pages'),
                'image_only': {k: v['image_only'] for k, v in checks.items()},
            },
        }
        meta['noteheads_in_truth'] = sum(len(e.pitches) for p in score.parts for m in p.measures
                                         for evs in m.values() for e in evs if e.kind == 'note' and not e.hidden)
        meta['systems'] = grep['systems_expected']
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
