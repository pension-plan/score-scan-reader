#!/usr/bin/env python3
"""Build the pitch challenge items in parallel and write ../manifest.json.

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/pitch/_tools/run_all.py [item-id ...]
       [--keep-work] [--no-damage]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pk.build import CAT_ROOT, build_item  # noqa: E402
from pk.catalog import ITEMS  # noqa: E402

MANIFEST = os.path.join(CAT_ROOT, 'manifest.json')


def _one(args):
    idx, keep, nodmg = args
    it = dict(ITEMS[idx])
    if nodmg:
        it['damage'] = {}
    return build_item(it, keep_work=keep)


def main():
    keep = '--keep-work' in sys.argv
    nodmg = '--no-damage' in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    idxs = [i for i, it in enumerate(ITEMS) if not want or it['id'] in want]
    with ProcessPoolExecutor(max_workers=min(len(idxs), 16)) as ex:
        logs = list(ex.map(_one, [(i, keep, nodmg) for i in idxs]))
    os.makedirs(os.path.join(CAT_ROOT, '_logs'), exist_ok=True)
    for lg in logs:
        with open(os.path.join(CAT_ROOT, '_logs', lg['id'] + '.json'), 'w') as f:
            json.dump(lg, f, indent=1, default=str)
        if lg.get('ok'):
            m = lg['meta']
            rc = m['validation']
            extra = (f"bars={m['measures']} pages={m['pages']} attacks={rc['attacks']} "
                     f"acc={rc['accidentals']['printed']} files={list(m['degradations'])}")
        else:
            extra = lg.get('error', '')[:600]
        print(f"{'OK ' if lg.get('ok') else 'ERR'} {lg['id']:34s} {lg['seconds']:6.1f}s {extra}")
    if nodmg:
        return
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
