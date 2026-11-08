#!/usr/bin/env python3
"""Build the degradation-extremes challenge set.

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/degradation/_tools/run.py [--pieces] [id-substring ...]

  --pieces   rebuild + revalidate the 4 source pieces first (build_piece.py)
Output: corpus/challenge/degradation/<id>/{engraving.ly, truth.musicxml, clean.pdf, scan.pdf,
        scan-mild.pdf, scan-severe.pdf, meta.json, ATTRIBUTION.txt} and manifest.json
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import damage as D  # noqa: E402
from build_piece import PIECE_DIR, XSD, build_piece  # noqa: E402
from pieces import CC0_NOTE, PIECES  # noqa: E402
from variants import PIECE_IDS, catalogue  # noqa: E402

OUT = os.path.dirname(HERE)                       # corpus/challenge/degradation
THUMBS = os.environ.get('DEG_THUMBS')             # optional preview dir (QA only)
FACING = os.path.join(PIECE_DIR, '_facing', 'facing.pdf')
# reverse side used for bleed-through: (piece, page) per page of each piece
REVERSE = {'hymn': [('piano', 0)], 'melody': [('hymn', 0)], 'piano': [('piano2p', 0)],
           'piano2p': [('melody', 0), ('hymn', 0)]}
FILE_SEED = {'scan': 0, 'scan-mild': 1, 'scan-severe': 2}

_cache = {}


def pdf_of(pk):
    return os.path.join(PIECE_DIR, pk, 'engraving.pdf')


def pages_at(pdf, dpi, tmp):
    key = (pdf, dpi)
    if key not in _cache:
        if len(_cache) > 6:
            _cache.clear()
        _cache[key] = D.render_gray(pdf, dpi, tmp, f'p{abs(hash(pdf)) % 10 ** 8}')
    return _cache[key]


def run(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def image_only(pdf):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int([l for l in info.splitlines() if l.startswith('Pages:')][0].split()[1])
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    size = [l for l in info.splitlines() if l.startswith('Page size:')][0].split(':', 1)[1].strip()
    return {'image_only': (not font_lines) and n_imgs == pages and not txt.strip(), 'fonts': font_lines,
            'pages': pages, 'images': n_imgs, 'page_size': size, 'bytes': os.path.getsize(pdf)}


def do_file(task):
    iid, fname, spec, pk, seed, infos = task
    t0 = time.time()
    try:
        with tempfile.TemporaryDirectory(dir=os.path.join(OUT, '_work')) as tmp:
            dpi = spec['dpi']
            clean = pages_at(pdf_of(pk), dpi, tmp)
            ctx = {}
            if spec.get('content', {}).get('bleed'):
                ctx['reverse'] = [pages_at(pdf_of(rp), dpi, tmp)[ri] for rp, ri in REVERSE[pk]]
            if spec.get('assembly') == 'spread' and len(clean) == 1:
                ctx['facing'] = pages_at(FACING, dpi, tmp)[0]
            imgs, notes = D.apply_spec(clean, spec, ctx, infos, seed)
            out = os.path.join(OUT, iid, fname + '.pdf')
            D.save_pdf(imgs, dpi, out, spec.get('out', {}))
            chk = image_only(out)
            if THUMBS:
                im = imgs[0]
                im = im.convert('RGB') if im.mode in ('1', 'L') else im
                im.thumbnail((700, 700))
                im.save(os.path.join(THUMBS, f'{iid}--{fname}.jpg'), quality=85)
            return {'id': iid, 'file': fname, 'ok': chk['image_only'], 'check': chk, 'spec': spec, 'seed': seed,
                    'annotations': notes, 'px': [[im.width, im.height] for im in imgs],
                    'modes': [im.mode for im in imgs], 'seconds': round(time.time() - t0, 1)}
    except Exception as e:
        return {'id': iid, 'file': fname, 'ok': False, 'error': repr(e), 'trace': traceback.format_exc()[-3000:]}


def do_clean(task):
    iid, pk, dpi = task
    try:
        with tempfile.TemporaryDirectory(dir=os.path.join(OUT, '_work')) as tmp:
            pages = pages_at(pdf_of(pk), dpi, tmp)
            out = os.path.join(OUT, iid, 'clean.pdf')
            D.save_pdf([Image.fromarray(p) for p in pages], dpi, out, {'format': 'png'})
            return {'id': iid, 'file': 'clean', 'ok': True, 'check': image_only(out), 'dpi': dpi}
    except Exception as e:
        return {'id': iid, 'file': 'clean', 'ok': False, 'error': repr(e), 'trace': traceback.format_exc()[-3000:]}


# ---------------------------------------------------------------- meta
CONTENT_ORDER = ['ink_weight', 'fade', 'halftone', 'paper', 'bleed', 'ink_color', 'ink_var', 'stains', 'foxing',
                 'highlighter', 'annotations', 'holes', 'staple', 'dogear', 'crop']


def steps(spec):
    st = [{'op': 'rasterise', 'dpi': spec['dpi'], 'tool': 'pdftoppm -gray -aa yes -aaVector yes (LilyPond PDF)'}]
    C = spec.get('content', {})
    for k in CONTENT_ORDER:
        if k in C:
            st.append({'op': k, 'params': C[k], 'stage': 'content'})
    for op, p in spec.get('page_geom', []):
        st.append({'op': op, 'params': p, 'stage': 'page_geometry'})
    for pi, ov in sorted(spec.get('page_overrides', {}).items()):
        st.append({'op': 'page_override', 'page': int(pi) + 1, 'params': ov})
    if spec.get('assembly') == 'spread':
        st.append({'op': 'two_up_spread', 'params': spec['spread'], 'stage': 'assembly'})
    for op, p in spec.get('global', []):
        st.append({'op': op, 'params': p, 'stage': 'global'})
    st.append({'op': 'background', 'params': spec.get('bg', {}), 'stage': 'composite'})
    st.append({'op': 'output', 'params': spec.get('out', {}), 'stage': 'encode'})
    return st


def write_item(item, results, pval):
    pk = item['piece']
    P = PIECES[pk]
    iid = item['id']
    d = os.path.join(OUT, iid)
    shutil.copy(os.path.join(PIECE_DIR, pk, 'truth.musicxml'), os.path.join(d, 'truth.musicxml'))
    shutil.copy(os.path.join(PIECE_DIR, pk, 'engraving.ly'), os.path.join(d, 'engraving.ly'))
    rc, so, se = run(['xmllint', '--noout', '--nonet', '--schema', XSD, os.path.join(d, 'truth.musicxml')])
    degr = {}
    files = {}
    ok = True
    for fname in ('scan', 'scan-mild', 'scan-severe'):
        r = results.get((iid, fname))
        if r is None:
            continue
        ok &= r['ok']
        degr[fname + '.pdf'] = {'seed': r.get('seed'), 'dpi': r['spec']['dpi'] if 'spec' in r else None,
                                'pages': r['check']['pages'] if 'check' in r else None,
                                'image_px': r.get('px'), 'image_mode': r.get('modes'),
                                'steps': steps(r['spec']) if 'spec' in r else None,
                                'annotations': r.get('annotations')}
        files[fname.replace('-', '_')] = f'{iid}/{fname}.pdf'
    cr = results.get((iid, 'clean'))
    ok &= bool(cr and cr['ok'])
    degr['clean.pdf'] = {'seed': None, 'dpi': cr['dpi'] if cr else None,
                         'steps': [{'op': 'rasterise', 'dpi': cr['dpi'] if cr else None,
                                    'tool': 'pdftoppm -gray (LilyPond PDF)'}, {'op': 'output',
                                    'params': {'mode': 'L', 'format': 'png'}}]}
    files['clean'] = f'{iid}/clean.pdf'
    files['truth'] = f'{iid}/truth.musicxml'
    files['engraving'] = f'{iid}/engraving.ly'
    tags = list(dict.fromkeys(P['base_tags'] + item['tags']))
    if pval['vector_pages'] > 1 and 'multi_page' not in tags:
        tags.append('multi_page')
    notes = P['notes'] + ' DAMAGE (' + item['variant'] + '): ' + item['notes']
    if item.get('limits'):
        notes += ' TRUTH LIMITATIONS: ' + item['limits']
    sib = [x for x in ITEM_IDS if x.startswith(PIECE_IDS[pk] + '-') and x != iid]
    scan_dpi = degr.get('scan.pdf', {}).get('dpi')
    meta = {
        'id': iid, 'category': 'degradation', 'piece': PIECE_IDS[pk], 'variant': item['variant'],
        'title': f"{P['title']} - {item['variant']}",
        'edge_cases': tags,
        'expected': {'parts': P['expected_parts'], 'must_not_split': P['must_not_split'],
                     'shared_staves': P['shared_staves'], 'notes': notes},
        'truth_limitations': item.get('limits') or 'none: truth matches the engraving exactly (MIDI attacks, MIDI '
                                                    'lyric events and PDF lyric text verified)',
        'degradations': degr,
        'dpi': scan_dpi,
        'license': P['license'],
        'files': files,
        'measures': pval['measures'], 'vector_pages': pval['vector_pages'], 'lyrics': pval['lyrics'],
        'shares_truth_with': sib,
        'validation': {
            'truth_xsd_valid': rc == 0,
            'midi_attacks_match_truth': pval['midi_attacks']['ok'],
            'attacks': pval['midi_attacks']['expected_attacks'],
            'midi_lyric_events_match_truth': pval['midi_lyrics']['ok'],
            'lyric_syllables': pval['midi_lyrics']['expected'],
            'lyric_text_found_in_engraving_pdf': pval['lyric_text_found_in_pdf'],
            'lilypond_warnings': pval['lily_warnings'],
            'scan_files_image_only': {k: results[(iid, k.replace('.pdf', ''))]['check']['image_only']
                                      for k in degr if (iid, k.replace('.pdf', '')) in results
                                      and 'check' in results[(iid, k.replace('.pdf', ''))]},
        },
        'origin': 'synthetic-scan (challenge: degradation extremes)',
        'seed': item['seed'],
    }
    with open(os.path.join(d, 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(d, 'ATTRIBUTION.txt'), 'w') as f:
        f.write('\n'.join(P['attribution'] + ['', 'Damage: ' + item['variant'] + ' (simulated scan; see meta.json).',
                                              '', CC0_NOTE]) + '\n')
    return meta, ok and rc == 0


ITEM_IDS = []


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--pieces' in sys.argv or not all(os.path.exists(os.path.join(PIECE_DIR, k, 'validation.json')) for k in PIECES):
        for k in PIECES:
            v = build_piece(k)
            print('piece', k, 'OK' if v['ok'] else 'FAIL')
            if not v['ok']:
                raise SystemExit(f'piece {k} failed validation: {json.dumps(v, default=str)[:2000]}')
    if not os.path.exists(FACING):
        subprocess.run(['lilypond', '-dno-point-and-click', '-o', 'facing', 'facing.ly'],
                       cwd=os.path.dirname(FACING), check=True, capture_output=True, timeout=300)
    pval = {k: json.load(open(os.path.join(PIECE_DIR, k, 'validation.json'))) for k in PIECES}
    assert all(v['ok'] for v in pval.values())
    os.makedirs(os.path.join(OUT, '_work'), exist_ok=True)
    infos = {}
    with tempfile.TemporaryDirectory(dir=os.path.join(OUT, '_work')) as tmp:
        for k in PIECES:
            infos[k] = [D.analyse_page(g, 300) for g in D.render_gray(pdf_of(k), 300, tmp, k)]
    with open(os.path.join(PIECE_DIR, 'page_analysis.json'), 'w') as f:
        json.dump({k: [{kk: vv for kk, vv in i.items() if kk != 'notes_mm'} for i in v] for k, v in infos.items()},
                  f, indent=1)
    items = catalogue(infos)
    ITEM_IDS[:] = [it['id'] for it in items]
    sel = [it for it in items if not args or any(a in it['id'] for a in args)]
    tasks, ctasks = [], []
    for it in sel:
        d = os.path.join(OUT, it['id'])
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        for fname, sp in it['files'].items():
            tasks.append((it['id'], fname, sp, it['piece'], it['seed'] + FILE_SEED[fname], infos[it['piece']]))
        ctasks.append((it['id'], it['piece'], it['files']['scan']['dpi']))
    # heavy (high dpi) first
    tasks.sort(key=lambda t: -t[2]['dpi'])
    results = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(96, len(tasks) + len(ctasks))) as ex:
        futs = [ex.submit(do_file, t) for t in tasks] + [ex.submit(do_clean, t) for t in ctasks]
        for fu in as_completed(futs):
            r = fu.result()
            results[(r['id'], r['file'])] = r
            if not r['ok']:
                print('FAIL', r['id'], r['file'], r.get('error'), (r.get('trace') or '')[-1500:], flush=True)
    print(f'rendered {len(results)} files in {time.time() - t0:.0f}s', flush=True)
    metas, bad = [], []
    for it in sel:
        m, ok = write_item(it, results, pval[it['piece']])
        metas.append(m)
        if not ok:
            bad.append(it['id'])
    # manifest: merge with existing entries of items not rebuilt
    man = os.path.join(OUT, 'manifest.json')
    old = {}
    if args and os.path.exists(man):
        old = {m['id']: m for m in json.load(open(man))}
    for m in metas:
        old[m['id']] = m
    entries = [old[i] for i in ITEM_IDS if i in old]
    with open(man, 'w') as f:
        json.dump(entries, f, indent=1, ensure_ascii=False, default=str)
    shutil.rmtree(os.path.join(OUT, '_work'), ignore_errors=True)
    print('items', len(metas), 'bad', bad, 'manifest', len(entries))


if __name__ == '__main__':
    main()
