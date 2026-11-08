#!/usr/bin/env python3
"""Build the coverage/rests items in parallel and write the family manifest.

usage: /Users/d.sloane/music/.venv/bin/python corpus/coverage/rests/_tools/run_all.py [item-id ...] [--keep-work]

Per item (crest/build.py): engraving.ly, truth.musicxml, clean.pdf, scan.pdf, scan-severe.pdf,
meta.json, ATTRIBUTION.txt in corpus/coverage/rests/<id>/ ; full verification logs in
corpus/coverage/rests/_logs/<id>.json ; manifest corpus/coverage/rests/manifest.json.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crest.build import ROOT, build_item  # noqa: E402
from crest.catalog import ITEMS  # noqa: E402
from crest import counts as _counts  # noqa: E402

COUNT_RULES = _counts.__doc__.split('Counting rules (also in coverage/rests/manifest.json "counting_rules"):')[-1].strip()

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
            extra = ' '.join(f"{k}:{v['dpi']}dpi/{v['bytes'] // 1024}KB" for k, v in d.items())
            print(f"OK  {lg['id']:34s} {lg['seconds']:6.1f}s meas={m['expected']['measures']} "
                  f"pages={m['pages']} {extra}")
        else:
            print(f"ERR {lg['id']:34s} {lg['seconds']:6.1f}s {lg.get('error', '')[:3000]}")
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
            e['path'] = f"corpus/coverage/rests/{lg['id']}"
            e['scan_files'] = sorted(e['degradations'])
            by_id[lg['id']] = e
        elif lg['id'] in by_id:
            del by_id[lg['id']]
    entries = [by_id[it['id']] for it in ITEMS if it['id'] in by_id]
    totals = {}
    for e in entries:
        for k, v in e['counts'].items():
            totals[k] = totals.get(k, 0) + v
    man = {
        'family': 'rests',
        'description': 'Coverage family "rests": every rest value (breve..64th), dotted and double-dotted rests, '
                       'whole-bar rests in 16 meters, multi-bar rests (H-bar and church-rest symbols), raised / '
                       'lowered rests in two-voice staves, rests inside tuplets and under beams, rests in the piano '
                       'left hand and in a string quartet. Each item: engraving.ly, truth.musicxml (MusicXML 4.0, '
                       'XSD-valid), clean.pdf, scan.pdf (typical scan), scan-severe.pdf (heavy damage), meta.json, '
                       'ATTRIBUTION.txt.',
        'counting_rules': COUNT_RULES,
        'license': 'CC0',
        'generator': 'corpus/coverage/rests/_tools/run_all.py',
        'n_items': len(entries),
        'symbol_totals': dict(sorted(totals.items())),
        'layouts': sorted({e['layout'] for e in entries}),
        'items': entries,
    }
    with open(MANIFEST, 'w') as f:
        json.dump(man, f, indent=2, ensure_ascii=False, default=str)
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
