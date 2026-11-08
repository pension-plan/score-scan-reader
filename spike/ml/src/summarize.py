#!/usr/bin/env python3
"""Turn the spike's raw result files into the markdown tables used in docs/spike-ml.md.
Usage: .venv/bin/python src/summarize.py > out/tables.md"""
import collections, glob, json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: [json.loads(l) for l in open(os.path.join(ROOT, p)) if l.strip().startswith("{")]  # noqa: E731


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else float("nan")


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else float("nan")


print("## T1 end-to-end (reference Python pipelines), mean over images\n")
rows = J("out/e2e/results.jsonl")
print("| system | piece | images | measure-pitch F1 | +duration F1 | voice-assignment acc | parts out | wall s/page (8 cores, shared box) | failures |")
print("|---|---|---:|---:|---:|---:|---|---:|---:|")
agg = collections.defaultdict(list)
for r in rows:
    agg[(r["system"], r["piece"])].append(r)
for (s, p), v in sorted(agg.items()):
    parts = sorted(set(r.get("n_parts") for r in v if r.get("n_parts")))
    print(f"| {s} | {p} | {len(v)} | {mean([r['mp_f1'] for r in v]):.3f} | {mean([r['mpd_f1'] for r in v]):.3f} | "
          f"{mean([r['voice_acc'] for r in v]):.3f} | {parts} | {med([r['wall_s'] for r in v]):.0f} | {sum(1 for r in v if r.get('error'))} |")

print("\n## T2 end-to-end by degradation (all three pieces, 200+300 dpi)\n")
print("| system | clean | rot 1.3° | noise+blur | JPEG q30 | scan (rot, uneven light, blur, noise, JPEG) | photocopy (binarised, broken lines) |")
print("|---|---|---|---|---|---|---|")
by = collections.defaultdict(list)
for r in rows:
    by[(r["system"], r["image"].rsplit("_", 1)[1])].append(r)
for s in sorted(set(r["system"] for r in rows)):
    cells = []
    for d in ("clean", "rot", "noiseblur", "jpeg", "scan", "photocopy"):
        v = by.get((s, d), [])
        cells.append(f"{mean([r['mp_f1'] for r in v]):.3f} / {mean([r['voice_acc'] for r in v]):.3f}" if v else "–")
    print(f"| {s} | " + " | ".join(cells) + " |")
print("\n(cells: measure-pitch F1 / voice-assignment accuracy)")

print("\n## T3 copista detector through the JS pipeline (src/copista_core.mjs), notehead level\n")
sc = json.load(open(os.path.join(ROOT, "out/dets_scores.json")))
print("| run (runtime-size-weights-threads) | images | notehead P | R | F1 | staff-pos acc | stem acc | voice-slot acc (closed SATB) | median CPU ms/page |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
for run, rr in sc.items():
    print(f"| {run} | {len(rr)} | {mean([r['prec'] for r in rr]):.3f} | {mean([r['rec'] for r in rr]):.3f} | "
          f"{mean([r['f1'] for r in rr]):.3f} | {mean([r.get('pos_acc') for r in rr]):.3f} | {mean([r.get('stem_acc') for r in rr]):.3f} | "
          f"{mean([r.get('voice_acc') for r in rr]):.3f} | {med([r.get('cpu_ms') for r in rr]):.0f} |")
print("\nstaff-position accuracy by degradation:\n")
print("| run | clean | rot | noiseblur | jpeg | scan | photocopy |")
print("|---|---|---|---|---|---|---|")
for run, rr in sc.items():
    b = collections.defaultdict(list)
    for r in rr:
        b[r["variant"]].append(r.get("pos_acc"))
    print(f"| {run} | " + " | ".join(f"{mean(b[d]):.3f}" if b.get(d) else "–" for d in ("clean", "rot", "noiseblur", "jpeg", "scan", "photocopy")) + " |")

print("\n## T4 microbench: one representative input, 1 thread (CPU ms = process CPU time, robust to the busy box)\n")
mb = []
for f in glob.glob(os.path.join(ROOT, "out/micro/*.jsonl")):
    for l in open(f):
        try:
            mb.append(json.loads(l))
        except Exception:  # noqa: BLE001
            pass
by = collections.defaultdict(dict)
for r in mb:
    by[r["model"]][r["runtime"]] = r
print("| model.variant | bytes | input | ort-node 1.30.0 CPU ms | ort-web 1.30.0 wasm CPU ms | status |")
print("|---|---:|---|---:|---:|---|")
INP = {"oemer-unet": "1×256×256×3 u8 window (234/page)", "oemer-seg": "1×288×288×3 u8 window (234/page)",
       "homr-segnet": "1×3×320×320 patch", "homr-enc": "1×1×256×1280 staff", "homr-dec": "1 token step",
       "satbline": "1×1×128×1200 line", "copista2m-dense": "1×1×1760×1248 page", "copista28m-dense": "1×1×1760×1248 page"}
for m in sorted(by):
    n, w = by[m].get("node", {}), by[m].get("web", {})
    inp = next((v for k, v in INP.items() if m.startswith(k)), "load only")
    st = []
    for tag, r in (("node", n), ("web", w)):
        if r.get("error"):
            st.append(f"{tag}: {r['error'][:70]}")
    b = (n or w).get("bytes", 0)
    print(f"| {m} | {b/1e6:.1f} MB | {inp} | {n.get('cpu_ms', '–')} | {w.get('cpu_ms', '–')} | {'; '.join(st) or 'ok'} |")

print("\n## T5 satb-line-omr (MIT line CRNN), repo reference preprocessing\n")
sl = J("out/satbline/results.jsonl")
print("| weights | piece | clean note acc | clean pitch acc | JPEG (clean boxes) | noise+blur (clean boxes) | rot/scan/photocopy | ms/line (CPU EP) |")
print("|---|---|---:|---:|---:|---:|---|---:|")
g = collections.defaultdict(list)
for r in sl:
    if "error" in r:
        continue
    g[(r["variant"], r["piece"])].append(r)
for (v, p), rr in sorted(g.items()):
    d = {r["image"].rsplit("_", 1)[1] + r["image"].split("_")[-2]: r for r in rr}
    pick = lambda k: mean([r["note_acc"] for r in rr if r["image"].endswith(k)])  # noqa: E731
    pickp = lambda k: mean([r["pitch_acc"] for r in rr if r["image"].endswith(k)])  # noqa: E731
    others = mean([r["note_acc"] for r in rr if r["image"].endswith(("rot", "scan", "photocopy"))])
    print(f"| {v} | {p} | {pick('clean'):.3f} | {pickp('clean'):.3f} | {pick('jpeg'):.3f} | {pick('noiseblur'):.3f} | "
          f"{others:.3f} (staff finder found {sum(r['staves_found'] for r in rr if r['image'].endswith(('rot','scan','photocopy')))} staves) | "
          f"{med([r['ms_per_line'] for r in rr if r['ms_per_line']]):.0f} |")

print("\n## T6 browser (headless Chromium 1248 / chrome-headless-shell arm64), copista-2m, satb_closed_300_scan\n")
wr = J("out/web/results.jsonl")
print("| ort-web | loader | CDN | CSP | wasmPaths | weights | threads / COI | result | page ms (run1 / run2) | dense ms | notes found | load ms | errors |")
print("|---|---|---|---|---|---|---|---|---|---|---:|---:|---|")
for r in wr:
    runs = r.get("runs") or []
    t = " / ".join(str(x.get("total_ms")) for x in runs) or "–"
    dm = " / ".join(str(round(x.get("dense_ms") or 0)) for x in runs) or "–"
    notes = runs[-1].get("notes") if runs else "–"
    err = (r.get("error") or "").split("\n")[0][:90]
    pe = "; ".join(sorted(set(r.get("pageErrors") or [])))[:80]
    print(f"| {r['ver']} | {r['mode']} | {r.get('cdn') or 'jsdelivr'} | {r.get('csp')} | {'{wasm}' if r.get('wasmobj') else 'prefix'} | "
          f"{(r.get('dense') or '').replace('copista','').replace('-dense','').replace('.onnx','')} | {r.get('threads', 1)} / {bool(r.get('coi'))} | "
          f"{'OK' if r.get('ok') else 'FAIL'} | {t} | {dm} | {notes} | {r.get('load_ms', '–')} | {err or pe} |")
