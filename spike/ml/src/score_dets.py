#!/usr/bin/env python3
"""Score every saved copista detection run (node/web harness + torch reference) against GT noteheads.
Usage: .venv/bin/python src/score_dets.py  -> out/dets_scores.json + printed table"""
import glob, json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from eval_notes import gt_info, match_points, copista_noteheads  # noqa: E402

runs = collections.defaultdict(dict)
for d in sorted(glob.glob(os.path.join(ROOT, "out/nodedets/*"))):
    for f in glob.glob(os.path.join(d, "*.json")):
        runs[os.path.basename(d)][os.path.basename(f)[:-5]] = json.load(open(f))
for sysname in ("cop2m", "cop28m"):
    for f in glob.glob(os.path.join(ROOT, f"out/e2e/{sysname}/*/*.dets_*.json")):
        stem = os.path.basename(os.path.dirname(f))
        runs[f"torch-{sysname[3:]}-fp32"][stem] = {"dets": json.load(open(f))}
out = {}
for run, imgs in sorted(runs.items()):
    rows = []
    for stem, r in sorted(imgs.items()):
        if not os.path.exists(os.path.join(ROOT, "scans", stem + ".boxes.json")):
            continue  # e.g. the real 1919 scan: no ground truth
        b, gt = gt_info(stem)
        m = match_points(copista_noteheads(r["dets"]), gt)
        m.update(image=stem, piece=stem.rsplit("_", 2)[0], variant=stem.rsplit("_", 1)[1],
                 cpu_ms=r.get("cpu_ms"), dense_ms=(r.get("timing") or {}).get("dense_ms"))
        rows.append(m)
    out[run] = rows
json.dump(out, open(os.path.join(ROOT, "out/dets_scores.json"), "w"), indent=0)


def avg(rows, k):
    v = [r[k] for r in rows if r.get(k) is not None]
    return sum(v) / len(v) if v else float("nan")


print(f"{'run':28s} {'n':>3s} {'P':>6s} {'R':>6s} {'F1':>6s} {'pos':>6s} {'stem':>6s} {'voice':>6s} {'cpu_ms':>7s}")
for run, rows in out.items():
    print(f"{run:28s} {len(rows):3d} {avg(rows,'prec'):6.3f} {avg(rows,'rec'):6.3f} {avg(rows,'f1'):6.3f} "
          f"{avg(rows,'pos_acc'):6.3f} {avg(rows,'stem_acc'):6.3f} {avg(rows,'voice_acc'):6.3f} {avg(rows,'cpu_ms'):7.0f}")
print()
for run in ("node-2m-fp32-t1", "node-2m-int8w-t1", "node-28m-fp32-t1", "torch-2m-fp32", "torch-28m-fp32"):
    rows = out.get(run, [])
    by = collections.defaultdict(list)
    for r in rows:
        by[r["variant"]].append(r)
    print(run, " | ".join(f"{k}: F1 {avg(v,'f1'):.3f} pos {avg(v,'pos_acc'):.3f} voice {avg(v,'voice_acc'):.3f}" for k, v in sorted(by.items())))
