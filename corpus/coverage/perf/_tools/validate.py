#!/usr/bin/env python3
"""Independent validator for corpus/coverage/perf/<id>/ items (reads only the published files).

Per item:
  files    engraving.ly, truth.musicxml, clean.pdf, scan.pdf, scan-severe.pdf, meta.json, ATTRIBUTION.txt
  xsd      truth.musicxml validates (xmllint, mvp/work/schema/musicxml.xsd)
  music21  truth parses (parts / notes / rests recorded)
  meta     coverage keys: id, family, title, symbols, layout, expected{parts, must_not_split}, counts,
           degradations (seed + params for every scan file), dpi, pages, license == CC0, perf{dpi, pageSize,
           pages, megapixels}; expected.parts == truth part names; symbols == keys of counts;
           counts == symcount.py(truth) (+ engraving-only stanza-text); perf.pages == PDF pages;
           perf.megapixels == clean.pdf page pixels; dpi == embedded image resolution
  pdf      every PDF opens, renders, has no fonts / text and one image per page (challenge validate.py)
  render   the published engraving.ly is re-rendered with LilyPond 2.24 in a scratch dir: MIDI attacks and
           lyric syllables == truth (challenge validate.py midi_check); clean.pdf ink == fresh raster
Uses the functions of corpus/challenge/_validate/validate.py (copied as cov/validate_lib.py).

usage: python validate.py [--jobs N] [--out report.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from cov import validate_lib as V  # noqa: E402
import symcount  # noqa: E402

ROOT = TOOLS.parent
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
FILES = ['engraving.ly', 'truth.musicxml', 'clean.pdf', 'scan.pdf', 'scan-severe.pdf', 'meta.json', 'ATTRIBUTION.txt']


def sh(cmd, timeout=1800, cwd=None):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout, cwd=cwd)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def check_item(args):
    iid, scratch = args
    d = ROOT / iid
    P = []
    r = {'id': iid}
    for f in FILES:
        if not (d / f).exists() or not (d / f).stat().st_size:
            P.append(f'missing {f}')
    code, out, err = sh(['xmllint', '--noout', '--nonet', '--schema', XSD, str(d / 'truth.musicxml')], 600)
    r['xsd'] = code == 0
    if code:
        P.append('XSD: ' + err[-300:])
    code, out, err = sh([sys.executable, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1],format="musicxml",'
                         'forceSource=True);print(len(s.parts),len(list(s.recurse().notes)),'
                         'len(list(s.recurse().getElementsByClass("Rest"))))', str(d / 'truth.musicxml')], 3600)
    r['music21'] = out.strip()
    if code:
        P.append('music21: ' + err.strip().splitlines()[-1][:200])
    truth = V.truth_events(d / 'truth.musicxml')
    meta = json.loads((d / 'meta.json').read_text())
    for k in ('id', 'family', 'title', 'symbols', 'layout', 'expected', 'counts', 'degradations', 'dpi', 'pages',
              'license', 'perf'):
        if k not in meta:
            P.append(f'meta.{k} missing')
    if meta.get('id') != iid or meta.get('family') != 'perf' or meta.get('license') != 'CC0':
        P.append('meta id/family/license wrong')
    ex = meta.get('expected', {})
    if ex.get('parts') != truth['parts'] or not isinstance(ex.get('must_not_split'), bool):
        P.append(f'expected.parts {ex.get("parts")} vs truth {truth["parts"]}')
    counts = symcount.count(d / 'truth.musicxml')
    mc = {k: v for k, v in meta.get('counts', {}).items() if k != 'stanza-text'}
    if counts != mc:
        diff = {k: (mc.get(k), counts.get(k)) for k in set(mc) | set(counts) if mc.get(k) != counts.get(k)}
        P.append(f'meta.counts != symcount(truth): {diff}')
    if sorted(meta.get('symbols', [])) != sorted(meta.get('counts', {})):
        P.append('meta.symbols != keys of meta.counts')
    for s in ('scan.pdf', 'scan-severe.pdf'):
        dg = meta.get('degradations', {}).get(s, {})
        if 'seed' not in dg or not dg.get('params'):
            P.append(f'degradations[{s}] lacks seed/params')
    pf = meta.get('perf', {})
    for k in ('dpi', 'pageSize', 'pages', 'megapixels'):
        if k not in pf:
            P.append(f'perf.{k} missing')
    r['pdfs'] = {}
    for f in ('clean.pdf', 'scan.pdf', 'scan-severe.pdf'):
        pr = V.pdf_check(d / f, scratch)
        r['pdfs'][f] = {k: pr.get(k) for k in ('ok', 'pages', 'images', 'image_ppi', 'image_px', 'image_color')}
        if not pr['ok']:
            P.append(f'{f} not a valid image-only PDF: {pr}')
        if pr['pages'] != meta.get('pages') or pr['pages'] != pf.get('pages'):
            P.append(f'{f}: {pr["pages"]} pages, meta says {meta.get("pages")}')
        if pr.get('image_ppi') and pr['image_ppi'] != [meta.get('dpi')]:
            P.append(f'{f}: image ppi {pr["image_ppi"]} != meta.dpi {meta.get("dpi")}')
    px = r['pdfs']['clean.pdf'].get('image_px') or [[0, 0]]
    if round(px[0][0] * px[0][1] / 1e6, 3) != pf.get('megapixels'):
        P.append(f'perf.megapixels {pf.get("megapixels")} != clean page {px[0]}')
    r['problems'] = P
    return r


def render_check(args):
    iid, scratch = args
    d = ROOT / iid
    w = Path(scratch) / 'ly' / iid
    shutil.rmtree(w, ignore_errors=True)
    w.mkdir(parents=True)
    shutil.copy(d / 'engraving.ly', w / 'engraving.ly')
    code, out, err = sh(['lilypond', '-dno-point-and-click', '-o', 'out', 'engraving.ly'], 3600, cwd=w)
    r = {'lilypond_exit': code, 'warnings': [l for l in err.splitlines() if re.search(r'warning|error', l, re.I)][:10]}
    mids = sorted(w.glob('out*.mid*'))
    truth = V.truth_events(d / 'truth.musicxml')
    m = V.midi_check(truth, mids)
    r['midi'] = {k: m[k] for k in ('truth_attacks', 'midi_attacks', 'grace_extras', 'missing', 'extra', 'notes_exact',
                                   'truth_syllables', 'midi_syllables', 'lyrics_ok')}
    dpi = json.loads((d / 'meta.json').read_text())['dpi']
    c = V.clean_compare(d / 'clean.pdf', w / 'out.pdf', dpi, scratch)
    r['clean'] = {k: c[k] for k in ('clean_pages', 'ly_pages', 'min_overlap', 'ok')}
    r['ok'] = code == 0 and not r['warnings'] and m['notes_exact'] and m['lyrics_ok'] and c['ok']
    shutil.rmtree(w, ignore_errors=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=48)
    ap.add_argument('--out', default=str(ROOT / '_logs' / 'validate.json'))
    ap.add_argument('--scratch', default=os.environ.get('VALIDATE_SCRATCH', str(ROOT / '_work' / 'validate')))
    a = ap.parse_args()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    ids = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('_'))
    with ProcessPoolExecutor(a.jobs) as ex:
        items = list(ex.map(check_item, [(i, a.scratch) for i in ids]))
        rend = list(ex.map(render_check, [(i, a.scratch) for i in ids]))
    for it, rr in zip(items, rend):
        it['render'] = rr
        if not rr['ok']:
            it['problems'].append(f'render check failed: {rr}')
    rep = {'n_items': len(items), 'n_ok': sum(1 for i in items if not i['problems']),
           'failed': [{'id': i['id'], 'problems': i['problems']} for i in items if i['problems']], 'items': items}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1, default=str))
    print(json.dumps({k: rep[k] for k in ('n_items', 'n_ok')}))
    for f in rep['failed']:
        print('FAIL', f['id'], *f['problems'], sep='\n   ')
    shutil.rmtree(a.scratch, ignore_errors=True)


if __name__ == '__main__':
    main()
