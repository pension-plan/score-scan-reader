#!/usr/bin/env python3
"""Build the lyrics challenge set (corpus/challenge/lyrics/<id>/) in parallel and
write corpus/challenge/lyrics/manifest.json (array of meta objects).

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/lyrics/_tools/run_all.py [item-id ...] [--keep-work]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build import ROOT, build_item  # noqa: E402
from items import ITEMS  # noqa: E402

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
            v = m['validation']
            extra = (f"pages={m['engraved_pages']} attacks={v['attacks']} syl={v['syllables_checked']} "
                     f"lines={v['lyric_lines_checked']} scans={list(v['scans_image_only'].values())}")
        else:
            extra = lg.get('error', '')[:1500]
        print(f"{'OK ' if lg.get('ok') else 'ERR'} {lg['id']:40s} {lg['seconds']:6.1f}s {extra}")
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
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
