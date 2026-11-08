#!/usr/bin/env python3
"""Build the coverage/perf family (performance set) and write ../manifest.json.

usage: /Users/d.sloane/music/.venv/bin/python corpus/coverage/perf/_tools/run_all.py [item-id-substring ...]
       [--keep-work] [--jobs N]

Items (21):
  perf-hymn-a4-{100,150,200,300,400,600}dpi     same 1-page SATB hymn, A4, six scan resolutions
  perf-piano-a4-{100,150,200,300,400,600}dpi    same dense 1-page piano page, A4, six resolutions
  perf-{hymn,piano}-{letter,a3}-300dpi           page-size variants (A4 = the 300 dpi items above)
  perf-pages-{01,05,10,20,40}                    piano documents of 1/5/10/20/40 pages, A4, 300 dpi
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

import build as B  # noqa: E402
from pieces import hymn, piano, variations  # noqa: E402

ROOT = B.ROOT
DPIS = [100, 150, 200, 300, 400, 600]
PAGES = [1, 5, 10, 20, 40]
YELLOWED = (236, 226, 198)


# --------------------------------------------------------------------------- engravings

def mk_hymn(paper):
    return lambda: hymn.make(paper)


def mk_piano(paper):
    return lambda: piano.make(paper)


def mk_var(n):
    return lambda: variations.make(n)


ENGRAVINGS = {}
for paper in ('A4', 'Letter', 'A3'):
    ENGRAVINGS[f'hymn-{paper}'] = (mk_hymn(paper), 1)
    ENGRAVINGS[f'piano-{paper}'] = (mk_piano(paper), 1)
for n in PAGES:
    ENGRAVINGS[f'var-{n}'] = (mk_var(n), n)


# --------------------------------------------------------------------------- damage plans

def typical(rotate, seed, extra=None):
    p = dict(mode='gray', texture=2, rotate=rotate, gradient=0.05, blur=0.5, noise=3, jpeg=80)
    p.update(extra or {})
    return {'seed': seed, 'params': p,
            'summary': f'typical flatbed scan: grey, {rotate:+.1f} deg skew, slight lighting gradient, '
                       'light blur + sensor noise, JPEG q80'}


HYMN_SEVERE = {'seed': 51002, 'summary': 'phone photo of a yellowed copy: perspective / keystone, 2.5 deg '
               'rotation, uneven light, vignette, motion + focus blur, colour noise, JPEG q30',
               'params': dict(mode='rgb', paper_rgb=YELLOWED, texture=5, rotate=2.5,
                              phone={'margin': 0.05, 'bg': 60, 'jitter': 0.03, 'keystone': 0.04},
                              blotch=0.25, vignette=0.3, motion_blur={'len': 4, 'angle': 20}, blur=0.8, noise=7,
                              jpeg=30)}
PIANO_SEVERE = {'seed': 52002, 'summary': 'binarised (1-bit) photocopy: -3 deg skew, faded strokes, blur before '
                'thresholding, salt & pepper, toner speckles',
                'params': dict(rotate=-3.0, ink_dropout=0.12, blur=0.8, noise=10, binarize=150, binarize_noise=18,
                               saltpepper=0.0015, speckle=80, format='png1')}


def pages_typical(n, seed):
    rng = random.Random(seed)
    rot = {k: round(rng.choice([-1, 1]) * rng.uniform(0.2, 1.0), 2) for k in range(40)}
    p = dict(mode='gray', texture=2, rotate_pages={k: rot[k] for k in range(n)}, gradient=0.05, blur=0.5, noise=3,
             jpeg=80)
    return {'seed': seed, 'params': p, 'summary': 'typical sheet-fed scan of every page: grey, 0.2-1.0 deg skew '
            'that differs per page, light blur + noise, JPEG q80'}


def pages_severe(n, seed):
    rng = random.Random(seed)
    rot = {k: round(rng.choice([-1, 1]) * rng.uniform(1.5, 3.5), 2) for k in range(40)}
    p = dict(mode='gray', texture=4, rotate_pages={k: rot[k] for k in range(n)}, bleed=0.12, gradient=0.15,
             blur=1.0, noise=9, speckle=60, jpeg=35)
    return {'seed': seed, 'params': p, 'summary': 'worn photocopies scanned in grey: 1.5-3.5 deg skew per page, '
            'bleed-through of the next page, strong lighting gradient, blur, noise, toner speckles, JPEG q35'}


# --------------------------------------------------------------------------- items

def items():
    out = []
    for dpi in DPIS:
        out.append(dict(id=f'perf-hymn-a4-{dpi}dpi', eng='hymn-A4', dpi=dpi, paper='A4',
                        scans={'scan.pdf': typical(0.6, 51001), 'scan-severe.pdf': HYMN_SEVERE},
                        axis='dpi', group='hymn'))
    for dpi in DPIS:
        out.append(dict(id=f'perf-piano-a4-{dpi}dpi', eng='piano-A4', dpi=dpi, paper='A4',
                        scans={'scan.pdf': typical(-0.8, 52001), 'scan-severe.pdf': PIANO_SEVERE},
                        axis='dpi', group='piano'))
    for paper in ('Letter', 'A3'):
        out.append(dict(id=f'perf-hymn-{paper.lower()}-300dpi', eng=f'hymn-{paper}', dpi=300, paper=paper,
                        scans={'scan.pdf': typical(0.6, 51001), 'scan-severe.pdf': HYMN_SEVERE},
                        axis='pageSize', group='hymn'))
    for paper in ('Letter', 'A3'):
        out.append(dict(id=f'perf-piano-{paper.lower()}-300dpi', eng=f'piano-{paper}', dpi=300, paper=paper,
                        scans={'scan.pdf': typical(-0.8, 52001), 'scan-severe.pdf': PIANO_SEVERE},
                        axis='pageSize', group='piano'))
    for n in PAGES:
        out.append(dict(id=f'perf-pages-{n:02d}', eng=f'var-{n}', dpi=300, paper='A4',
                        scans={'scan.pdf': pages_typical(n, 53001), 'scan-severe.pdf': pages_severe(n, 53002)},
                        axis='pages', group='pages'))
    return out


# --------------------------------------------------------------------------- stage 4

def assemble(args):
    it, eng, page_recs = args
    t0 = time.time()
    iid = it['id']
    od = os.path.join(ROOT, iid)
    shutil.rmtree(od, ignore_errors=True)
    os.makedirs(od)
    ew = os.path.join(B.WORK, 'eng', it['eng'])
    shutil.copy(os.path.join(ew, 'engraving.ly'), os.path.join(od, 'engraving.ly'))
    shutil.copy(os.path.join(ew, 'truth.musicxml'), os.path.join(od, 'truth.musicxml'))
    info = eng['info']
    npages = eng['pages']
    degr, checks = {}, {}
    files = ['clean.pdf'] + list(it['scans'])
    for fname in files:
        recs = sorted([r for r in page_recs if r['file'] == fname], key=lambda r: r['page'])
        assert len(recs) == npages, (iid, fname, len(recs))
        pdf = os.path.join(od, fname)
        subprocess.run(['img2pdf', '--imgsize', f'{it["dpi"]}dpi', '-o', pdf] + [r['path'] for r in recs],
                       check=True, capture_output=True, timeout=3600)
        chk = B.image_only(pdf, npages)
        checks[fname] = chk
        if not chk['image_only']:
            raise RuntimeError(f'{iid}/{fname} not image-only: {chk}')
        if fname == 'clean.pdf':
            degr[fname] = {'seed': None, 'params': {'dpi': it['dpi'], 'format': 'png', 'colour': 'gray',
                                                    'damage': 'none (anti-aliased raster of the engraving)'},
                           'size_px': recs[0]['size'], 'bytes': os.path.getsize(pdf)}
            continue
        plan = it['scans'][fname]
        P = dict(plan['params'])
        P['dpi'] = it['dpi']
        fmt = P.get('format', 'jpeg')
        degr[fname] = {
            'seed': plan['seed'], 'page_seeds': [r['seed'] for r in recs],
            'seed_rule': 'page k (0-based) is damaged with numpy default_rng(seed * 1000 + k)',
            'dpi': it['dpi'], 'format': f'jpeg q{P.get("jpeg", 75)}' if fmt == 'jpeg' else fmt,
            'colour': 'bw' if P.get('binarize') else P.get('mode', 'rgb'),
            'params': P, 'summary': plan['summary'], 'bytes': os.path.getsize(pdf),
            'pdf_pages': [{'page': r['page'] + 1, 'size_px': r['size'], 'mode': r.get('mode'), 'ops': r['ops']}
                          for r in recs],
        }
    w, h = page_recs[0]['size'] if page_recs[0]['file'] == 'clean.pdf' else \
        next(r['size'] for r in page_recs if r['file'] == 'clean.pdf')
    mp = round(w * h / 1e6, 3)
    counts = eng['counts']
    symbols = sorted(counts)
    notes = [
        'counts follow the rules in _tools/symcount.py (run it on a converter output for comparable numbers); '
        'every count except stanza-text is computed from truth.musicxml and was cross-checked against the '
        'LilyPond grob log of the engraving (ties, slurs, beams, flags, articulations, ornaments, dynamics, '
        'hairpins, pedals, fingerings, accidentals, ottavas, tuplets, ledger lines, lyrics, rehearsal / tempo '
        'marks, voltas, whole-bar rests, clef changes).',
        'ledger-above / ledger-below count note heads that need ledger lines (derived from clef + octave-shift; '
        'MusicXML does not encode ledger lines).',
        'stem-up / stem-down / beam / flag / accidental elements in the truth are exactly what LilyPond engraved '
        '(harvested from the instrumented engraving).',
    ]
    if 'stanza-text' in counts:
        notes.append('stanza-text: the stanza numbers "1."-"4." are printed but MusicXML has no element for them; '
                     'the count comes from the engraving, not from truth.musicxml.')
    notes.append(info['truth_limitations'])
    meta = {
        'id': iid, 'family': B.FAMILY, 'title': info['title'],
        'symbols': symbols, 'layout': info['layout'], 'layout_also': info.get('layout_also', []),
        'expected': {'parts': info['parts'], 'must_not_split': info['must_not_split'],
                     'notes': info['expected_notes']},
        'counts': counts,
        'degradations': degr,
        'dpi': it['dpi'], 'pages': npages, 'license': 'CC0',
        'perf': {'dpi': it['dpi'], 'pageSize': it['paper'], 'pages': npages, 'megapixels': mp,
                 'megapixels_total': round(mp * npages, 3), 'page_px': [w, h], 'axis': it['axis'],
                 'group': it['group'], 'engraving': it['eng'],
                 'file_bytes': {f: degr[f]['bytes'] for f in files},
                 'measures': eng['measures'], 'systems': eng['systems'], 'notes_in_truth': eng['notes_in_truth'],
                 'rests_in_truth': eng['rests_in_truth'],
                 'staff_size_pt': eng['staff_size'], 'paper_mm': [eng['paper']['width_mm'], eng['paper']['height_mm']]},
        'notes': notes,
        'truth_limitations': info['truth_limitations'],
        'source': info['source'],
        'validation': {
            'xsd_valid': eng['xsd_valid'], 'music21_parse': eng['music21'],
            'engraving_matches_model': eng['verify_notes'],
            'midi_vs_truth': eng['midi'], 'accidentals_cross_check': eng['accidentals'],
            'symbol_cross_check': eng['cross_check'], 'twin_identical': eng['twin_identical'],
            'lilypond_warnings': eng['lilypond_warnings'], 'image_only': {k: v['image_only'] for k, v in checks.items()},
        },
        'files': sorted(os.listdir(od) + ['meta.json', 'ATTRIBUTION.txt']),
    }
    if info.get('pages_plan'):
        meta['pages_plan'] = info['pages_plan']
    with open(os.path.join(od, 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(od, 'ATTRIBUTION.txt'), 'w') as f:
        f.write(info['attribution'].strip() + '\n')
    return {'id': iid, 'ok': True, 'seconds': round(time.time() - t0, 1), 'meta': meta}


def _engrave(key):
    mk, pages = ENGRAVINGS[key]
    return B.engrave(key, mk, pages)


def _render(args):
    key, dpi, k = args
    out = os.path.join(B.WORK, 'eng', key, f'r{dpi}')
    os.makedirs(out, exist_ok=True)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', '-f', str(k + 1),
                    '-l', str(k + 1), '-singlefile', os.path.join(B.WORK, 'eng', key, 'engraving.pdf'),
                    os.path.join(out, f'p-{k:03d}')], check=True, timeout=3600)
    return key, dpi, k


def main():
    t0 = time.time()
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = 64
    if '--jobs' in sys.argv:
        jobs = int(sys.argv[sys.argv.index('--jobs') + 1])
    its = [it for it in items() if not want or any(w in it['id'] for w in want)]
    keys = sorted({it['eng'] for it in its})
    print(f'{len(its)} items, {len(keys)} engravings', flush=True)
    with ProcessPoolExecutor(max_workers=min(len(keys), jobs)) as ex:
        engs = dict(zip(keys, ex.map(_engrave, keys)))
    bad = [k for k, r in engs.items() if not r['ok']]
    for k, r in engs.items():
        print(f"ENG {'OK ' if r['ok'] else 'ERR'} {k:14s} {r['seconds']:6.1f}s pages={r.get('pages')} "
              f"notes={r.get('notes_in_truth')} {r.get('error', '')[:1500]}", flush=True)
    if bad:
        sys.exit(1)
    # stage 2: render
    rtasks = sorted({(it['eng'], it['dpi'], k) for it in its for k in range(engs[it['eng']]['pages'])})
    for key, dpi in {(a, b) for a, b, _ in rtasks}:
        shutil.rmtree(os.path.join(B.WORK, 'eng', key, f'r{dpi}'), ignore_errors=True)
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        list(ex.map(_render, rtasks))
    print(f'rendered {len(rtasks)} pages  ({time.time() - t0:.0f}s)', flush=True)
    # stage 3: pages (clean + damaged), heavy pages first
    ptasks = []
    for it in its:
        shutil.rmtree(os.path.join(B.WORK, 'items', it['id']), ignore_errors=True)
        n = engs[it['eng']]['pages']
        for fname in ['clean.pdf'] + list(it['scans']):
            plan = it['scans'].get(fname)
            for k in range(n):
                ptasks.append((it['id'], fname, k, n, it['eng'], it['dpi'], plan))
    ptasks.sort(key=lambda t: -t[5])
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        recs = list(ex.map(B.page_task, ptasks, chunksize=1))
    print(f'damaged/encoded {len(recs)} page images  ({time.time() - t0:.0f}s)', flush=True)
    by_item = {}
    for r in recs:
        by_item.setdefault(r['item'], []).append(r)
    with ProcessPoolExecutor(max_workers=min(jobs, len(its))) as ex:
        res = list(ex.map(assemble, [(it, engs[it['eng']], by_item[it['id']]) for it in its]))
    for r in res:
        m = r['meta']
        print(f"OK  {r['id']:26s} pages={m['pages']:2d} dpi={m['dpi']} {m['perf']['pageSize']:6s} "
              f"MP/page={m['perf']['megapixels']:6.2f} symbols={len(m['symbols'])} "
              f"bytes={m['perf']['file_bytes']}", flush=True)
    # manifest (merge with existing entries for items not rebuilt)
    man = os.path.join(ROOT, 'manifest.json')
    old = []
    if os.path.exists(man):
        try:
            old = json.load(open(man))
        except Exception:
            old = []
    by_id = {e['id']: e for e in old}
    for r in res:
        e = dict(r['meta'])
        e['path'] = f'perf/{r["id"]}'
        e['scan_files'] = [f for f in ('scan.pdf', 'scan-severe.pdf') if f in e['degradations']]
        by_id[r['id']] = e
    order = [it['id'] for it in items()]
    entries = [by_id[i] for i in order if i in by_id]
    json.dump(entries, open(man, 'w'), indent=1, ensure_ascii=False, default=str)
    log = {'seconds': round(time.time() - t0, 1), 'engravings': {k: {x: r.get(x) for x in
           ('ok', 'seconds', 'pages', 'measures', 'notes_in_truth')} for k, r in engs.items()},
           'page_tasks': [{k: r[k] for k in ('item', 'file', 'page', 'size', 'seconds')} for r in recs]}
    os.makedirs(os.path.join(ROOT, '_logs'), exist_ok=True)
    json.dump(log, open(os.path.join(ROOT, '_logs', 'build.json'), 'w'), indent=1, default=str)
    if '--keep-work' not in sys.argv:
        shutil.rmtree(os.path.join(B.WORK, 'items'), ignore_errors=True)
        for key in keys:
            for d in os.listdir(os.path.join(B.WORK, 'eng', key)):
                if d.startswith('r') and d[1:].isdigit():
                    shutil.rmtree(os.path.join(B.WORK, 'eng', key, d), ignore_errors=True)
    print(f'manifest: {man} ({len(entries)} items)  total {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
