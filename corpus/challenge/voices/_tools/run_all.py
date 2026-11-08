#!/usr/bin/env python3
"""Build the challenge/voices items in parallel and write ../manifest.json.

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/voices/_tools/run_all.py [item-id ...] [--keep-work]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vsynth.build import ROOT, build_item  # noqa: E402
from vsynth.items import ITEMS  # noqa: E402

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
            json.dump(lg, f, indent=1, default=str, ensure_ascii=False)
        if lg.get('ok'):
            m = lg['meta']
            extra = (f"pages={m['pages_engraved']} meas={m['measures']} attacks={m['validation']['attacks_truth']} "
                     f"hidden={m['validation']['attacks_hidden_in_engraving_carried_by_other_voice']} "
                     f"files={','.join(m['files']['scans'])}")
            print(f"OK  {lg['id']:38s} {lg['seconds']:6.1f}s {extra}")
        else:
            print(f"ERR {lg['id']:38s} {lg['seconds']:6.1f}s {lg.get('error', '')[:1500]}")
    # manifest = meta.json of every built item, in catalog order
    entries = []
    for it in ITEMS:
        p = os.path.join(ROOT, it['id'], 'meta.json')
        if os.path.exists(p):
            entries.append(json.load(open(p)))
    with open(MANIFEST, 'w') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
