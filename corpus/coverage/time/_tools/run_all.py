#!/usr/bin/env python3
"""Build the coverage items of family 'time' in parallel and write the family manifest.

usage: /Users/d.sloane/music/.venv/bin/python corpus/coverage/time/_tools/run_all.py [item-id ...] [--keep-work]

Per item (tsynth/build.py): engraving.ly, truth.musicxml, clean.pdf, scan.pdf, scan-severe.pdf,
meta.json, ATTRIBUTION.txt in corpus/coverage/time/<id>/ ; logs in corpus/coverage/time/_logs/<id>.json ;
manifest corpus/coverage/time/manifest.json.
Copied from corpus/challenge/rhythm/_tools/run_all.py (nothing outside corpus/coverage/time is modified).
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsynth.build import ROOT, build_item  # noqa: E402
from tsynth.catalog import ITEMS  # noqa: E402

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
            print(f"OK  {lg['id']:28s} {lg['seconds']:6.1f}s bars={m['expected']['measures']} pages={m['pages']} {extra}")
        else:
            print(f"ERR {lg['id']:28s} {lg['seconds']:6.1f}s {lg.get('error', '')[:3000]}")
    old = {}
    if os.path.exists(MANIFEST):
        try:
            old = {e['id']: e for e in json.load(open(MANIFEST))['items']}
        except Exception:
            old = {}
    for lg in logs:
        if lg.get('ok'):
            m = dict(lg['meta'])
            m['path'] = f"time/{m['id']}"
            old[lg['id']] = m
        elif lg['id'] in old:
            del old[lg['id']]
    entries = [old[it['id']] for it in ITEMS if it['id'] in old]
    totals = {}
    for e in entries:
        for k, v in e['counts'].items():
            totals[k] = totals.get(k, 0) + v
    from tsynth.counts import COUNT_RULES
    sym_items = {}
    for e in entries:
        for k in e['symbols']:
            sym_items.setdefault(k, []).append(e['id'])
    man = {'family': 'time',
           'description': 'Time-signature / meter / pickup / tuplet / tie coverage: every taxonomy time tag '
                          '(numeric 2/4 3/4 4/4 2/2 3/2 5/4 6/8 9/8 12/8 5/8 7/8, C, cut, changes, pickups, '
                          'tuplets 2/3/5/6/7 and nested, ties incl. across system and page breaks) in 10 short '
                          'CC0 pieces, each with exact truth.musicxml, clean.pdf, scan.pdf, scan-severe.pdf.',
           'n_items': len(entries), 'n_scan_files': sum(len(e['degradations']) for e in entries),
           'generator': 'corpus/coverage/time/_tools/run_all.py',
           'validator': 'corpus/coverage/time/_tools/validate.py (report: _tools/validate_report.json)',
           'license': 'CC0',
           'count_rules': COUNT_RULES,
           'layouts': {e['id']: e['layout'] for e in entries},
           'symbol_totals': dict(sorted(totals.items())),
           'symbol_items': dict(sorted(sym_items.items())),
           'items': entries}
    with open(MANIFEST, 'w') as f:
        json.dump(man, f, indent=2, ensure_ascii=False, default=str)
    print('manifest:', MANIFEST, len(entries), 'items')


if __name__ == '__main__':
    main()
