#!/usr/bin/env python3
"""Build the rhythm challenge items in parallel and write the category manifest.

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/rhythm/_tools/run_all.py [item-id ...] [--keep-work]

Per item (rsynth/build.py): truth.musicxml, engraving.ly, clean.pdf, scan.pdf,
scan-mild.pdf, scan-severe.pdf, meta.json, ATTRIBUTION.txt in
corpus/challenge/rhythm/<id>/ ; logs in corpus/challenge/rhythm/_logs/<id>.json ;
manifest corpus/challenge/rhythm/manifest.json (array of meta objects).
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rsynth.build import ROOT, build_item  # noqa: E402
from rsynth.catalog import ITEMS  # noqa: E402

MANIFEST = os.path.join(ROOT, 'manifest.json')


def _one(args):
    idx, keep = args
    return build_item(ITEMS[idx], keep_work=keep)


def main():
    keep = '--keep-work' in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    idxs = [i for i, it in enumerate(ITEMS) if not want or it['id'] in want]
    with ProcessPoolExecutor(max_workers=max(1, min(len(idxs), 16))) as ex:
        logs = list(ex.map(_one, [(i, keep) for i in idxs]))
    os.makedirs(os.path.join(ROOT, '_logs'), exist_ok=True)
    for lg in logs:
        with open(os.path.join(ROOT, '_logs', lg['id'] + '.json'), 'w') as f:
            json.dump(lg, f, indent=1, default=str)
        if lg.get('ok'):
            m = lg['meta']
            d = m['degradations']
            extra = ' '.join(f"{k}:{v['dpi']}dpi/{v['output_pages']}p/{v['bytes'] // 1024}KB" for k, v in d.items())
            print(f"OK  {lg['id']:32s} {lg['seconds']:6.1f}s bars={m['expected']['measures']} pages={m['pages']} {extra}")
        else:
            print(f"ERR {lg['id']:32s} {lg['seconds']:6.1f}s {lg.get('error', '')[:1500]}")
    old = []
    if os.path.exists(MANIFEST):
        try:
            old = json.load(open(MANIFEST))
        except Exception:
            old = []
    by_id = {e['id']: e for e in old}
    for lg in logs:
        if lg.get('ok'):
            by_id[lg['id']] = lg['meta']
        elif lg['id'] in by_id:
            del by_id[lg['id']]
    entries = [by_id[it['id']] for it in ITEMS if it['id'] in by_id]
    with open(MANIFEST, 'w') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
