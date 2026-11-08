#!/usr/bin/env python3
"""Build the synthetic-scan corpus in parallel and write the manifest.

usage: /Users/d.sloane/music/.venv/bin/python corpus/synthetic/_tools/run_all.py [item-id ...] [--keep-work]
"""
import json
import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synth.build import ROOT, build_item  # noqa: E402
from synth.catalog import ITEMS  # noqa: E402

CORPUS = os.path.dirname(ROOT)
MANIFEST = os.path.join(CORPUS, 'manifest-synthetic.json')


def _one(args):
    idx, keep = args
    return build_item(ITEMS[idx], keep_work=keep)


def main():
    keep = '--keep-work' in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    idxs = [i for i, it in enumerate(ITEMS) if not want or it['id'] in want]
    with ProcessPoolExecutor(max_workers=min(len(idxs), 32)) as ex:
        logs = list(ex.map(_one, [(i, keep) for i in idxs]))
    os.makedirs(os.path.join(ROOT, '_logs'), exist_ok=True)
    for lg in logs:
        with open(os.path.join(ROOT, '_logs', lg['id'] + '.json'), 'w') as f:
            json.dump(lg, f, indent=1, default=str)
        status = 'OK ' if lg.get('ok') else 'ERR'
        extra = ''
        if lg.get('ok'):
            e = lg['entry']
            extra = (f"pages={lg['pages']} dpi={e['dpi']} parts={len(e['expected_parts'])} "
                     f"lyr={lg.get('lyric_text_found')} img_only={lg['image_only']} "
                     f"{lg['scan_bytes']//1024}KB eng={'m2l' if 'musicxml2ly' in lg['engraver'] else 'lily'}")
        else:
            extra = lg.get('error', '')[:300]
        print(f"{status} {lg['id']:40s} {lg['seconds']:6.1f}s {extra}")
    # merge into manifest (keep entries of items not rebuilt)
    old = []
    if os.path.exists(MANIFEST):
        try:
            old = json.load(open(MANIFEST))
        except Exception:
            old = []
    by_id = {e['id']: e for e in old}
    for lg in logs:
        if lg.get('ok'):
            e = lg['entry']
            feats = list(e['features'])
            if lg['pages'] > 1 and 'multi_page' not in feats:
                feats.append('multi_page')
            if e['dpi'] <= 150 and 'low_dpi' not in feats:
                feats.append('low_dpi')
            e['features'] = feats
            by_id[e['id']] = e
        elif lg['id'] in by_id:
            del by_id[lg['id']]
    order = [it['id'] for it in ITEMS]
    entries = [by_id[i] for i in order if i in by_id]
    with open(MANIFEST, 'w') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    # default app sample
    for lg in logs:
        if lg.get('ok') and lg['id'] == 'sample-embed-old100':
            shutil.copy(os.path.join(ROOT, lg['id'], 'scan.pdf'), os.path.join(CORPUS, 'sample-embed.pdf'))
            shutil.copy(os.path.join(ROOT, lg['id'], 'truth.musicxml'),
                        os.path.join(CORPUS, 'sample-embed.truth.musicxml'))
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
