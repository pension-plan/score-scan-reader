#!/usr/bin/env python3
"""Build the layouts-family coverage items in parallel and write ../manifest.json.

usage: /Users/d.sloane/music/.venv/bin/python corpus/coverage/layouts/_tools/run_all.py [item-id ...] [--keep-work]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import ROOT, build_item  # noqa: E402
from pieces import ITEMS  # noqa: E402

MANIFEST = os.path.join(ROOT, 'manifest.json')


def _one(args):
    idx, keep = args
    return build_item(ITEMS[idx], keep_work=keep)


def main():
    keep = '--keep-work' in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    idxs = [i for i, it in enumerate(ITEMS) if not want or any(w in it['id'] for w in want)]
    with ProcessPoolExecutor(max_workers=max(1, min(len(idxs), 24))) as ex:
        logs = list(ex.map(_one, [(i, keep) for i in idxs]))
    os.makedirs(os.path.join(ROOT, '_logs'), exist_ok=True)
    for lg in logs:
        with open(os.path.join(ROOT, '_logs', lg['id'] + '.json'), 'w') as f:
            json.dump(lg, f, indent=1, default=str, ensure_ascii=False)
        if lg.get('ok'):
            m = lg['meta']
            print(f"OK  {lg['id']:44s} {lg['seconds']:6.1f}s pages={m['pages']} measures={m['measures']} "
                  f"parts={len(m['expected']['parts'])} heads={m['noteheads_in_truth']} "
                  f"symbols={len(m['symbols'])}")
        else:
            print(f"ERR {lg['id']:44s} {lg['seconds']:6.1f}s {lg.get('error', '')[:2500]}")
    old = []
    if os.path.exists(MANIFEST):
        try:
            old = json.load(open(MANIFEST)).get('items', [])
        except Exception:
            old = []
    by_id = {e['id']: e for e in old}
    for lg in logs:
        if lg.get('ok'):
            e = dict(lg['meta'])
            e['path'] = f"coverage/layouts/{lg['id']}"
            e['scan_files'] = sorted(k for k in e['degradations'] if k.startswith('scan'))
            by_id[lg['id']] = e
        elif lg['id'] in by_id:
            del by_id[lg['id']]
    ids = [it['id'] for it in ITEMS]
    entries = [by_id[i] for i in ids if i in by_id]
    write_manifest(entries)
    print('manifest:', MANIFEST, len(entries), 'items')


def write_manifest(entries):
    from collections import Counter
    tot = Counter()
    for e in entries:
        tot.update(e['counts'])
    man = {
        'family': 'layouts',
        'description': ('One clean exemplar per score-layout tag (plus variants): every item has an exact '
                        'MusicXML 4.0 truth generated from the same model as its LilyPond engraving, an '
                        'undamaged raster (clean.pdf), a typical scan (scan.pdf) and a heavily damaged scan '
                        '(scan-severe.pdf).'),
        'count_rules': 'see _tools/count_symbols.py (module docstring); counts are computed from truth.musicxml',
        'generator': '_tools/run_all.py (python: /Users/d.sloane/music/.venv/bin/python)',
        'license': 'CC0',
        'layouts': sorted({e['layout'] for e in entries}),
        'n_items': len(entries),
        'n_scan_files': sum(len(e['scan_files']) for e in entries),
        'symbol_totals': dict(sorted(tot.items())),
        'items': entries,
    }
    with open(MANIFEST, 'w') as f:
        json.dump(man, f, indent=2, ensure_ascii=False, default=str)


if __name__ == '__main__':
    main()
