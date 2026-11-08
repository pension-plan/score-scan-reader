#!/usr/bin/env python3
"""Evaluate alexanderalber/satb-line-omr (MIT CRNN+CTC line model) on the spike scans.

Uses the repo's own reference preprocessing (src/omr/staves.py detect, normalize.py) and decode
(ir.py decode_line/_records/_classify).  The model assumes one voice per staff (voice = staff index
inside a system), so on closed score it reads only one of the two voices per staff (by design).
Score: per GT voice, LCS of (midi, quarter-length) sequence / GT note count ("note acc") and
pitch-only LCS ("pitch acc"); plus timing per line (onnxruntime CPU, 1 thread).
Usage: .venv/bin/python src/eval_satbline.py  -> out/satbline/results.jsonl
"""
import glob, json, os, sys, time
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "dl", "satb-line-omr")
sys.path.insert(0, os.path.join(REPO, "src"))
sys.path.insert(0, os.path.join(ROOT, "src"))
from omr import staves as ST  # noqa: E402
from omr.normalize import normalize_staff  # noqa: E402
from omr import ir as IR  # noqa: E402
from eval_xml import lcs  # noqa: E402

STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
KEY_G = {"F": 1}  # key signature of all spike pieces (G major): apply to un-altered F


def read_page(sess, i2w, gray, det=None):
    det = det or ST.detect(gray)
    lines = []
    t_model = 0.0
    for b in det["boxes"]:
        crop = gray[b["y"]:b["y"] + b["h"], b["x"]:b["x"] + b["w"]].astype(np.float32) / 255.0
        norm = normalize_staff(crop, b["line_spacing"], staff_offset=b.get("pad_up"))
        x = (1.0 - norm)[None, None].astype(np.float32)
        t0 = time.perf_counter()
        logits = sess.run(None, {"input": x})[0][0]
        t_model += time.perf_counter() - t0
        ev = IR.decode_line(logits, i2w)
        els = [IR._classify(r) for r in IR._records(ev)]
        notes = []
        for e in els:
            if not e or e.get("kind") != "note":
                continue
            p = e["pitch"]
            alter = p["alter"] if p["alter"] else KEY_G.get(p["step"], 0)
            midi = 12 * (p["octave"] + 1) + STEPS[p["step"]] + alter
            notes.append((midi, round(e["duration"]["divisions"] / 48.0, 4)))
        lines.append({"system": b["system"], "voice": b["voice"], "notes": notes, "width": int(x.shape[-1])})
    return det, lines, t_model


def main():
    import onnxruntime as ort
    so = ort.SessionOptions()
    so.intra_op_num_threads = 1
    variants = {v: os.path.join(REPO, "model-public-domain", f"omr-line.{v}.onnx") for v in ("fp32", "fp16", "int8")}
    vocab = json.load(open(os.path.join(REPO, "model-public-domain", "vocab.json")))["tokens"]
    i2w = [None] + vocab
    os.makedirs(os.path.join(ROOT, "out", "satbline"), exist_ok=True)
    outf = open(os.path.join(ROOT, "out", "satbline", "results.jsonl"), "w")
    imgs = sorted(glob.glob(os.path.join(ROOT, "scans", "*_*_*.png")))
    for v, path in variants.items():
        sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        for img in imgs:
            stem = os.path.basename(img)[:-4]
            piece = stem.rsplit("_", 2)[0]
            gt = json.load(open(os.path.join(ROOT, "scans", "gt", piece + ".json")))
            gray = np.asarray(Image.open(img).convert("L"))
            # noiseblur / jpeg variants share the clean page's geometry: also score them with the staff
            # boxes found on the clean page, to separate CRNN robustness from staff-finder failure
            det0 = None
            if stem.endswith(("_noiseblur", "_jpeg")):
                clean = np.asarray(Image.open(img.rsplit("_", 1)[0] + "_clean.png").convert("L"))
                det0 = ST.detect(clean)
            try:
                det, lines, tm = read_page(sess, i2w, gray, det0)
            except Exception as e:  # noqa: BLE001
                rec = {"variant": v, "image": stem, "error": repr(e)[:200]}
                outf.write(json.dumps(rec) + "\n"); print(rec); continue
            staves_per_sys = [len(s) for s in gt["staves"]]
            nst = len(staves_per_sys)
            # voice k of a system -> GT staff k (open score: one voice; closed: staff holds 2 voices)
            per_staff = {}
            for ln in sorted(lines, key=lambda l: (l["system"], l["voice"])):
                per_staff.setdefault(ln["voice"], []).extend(ln["notes"])
            tot = ok = okp = 0
            per_voice = {}
            for si, vids in enumerate(gt["staves"]):
                pred = per_staff.get(si, [])
                for vid in vids:
                    g = [(n["midi"], round(n["quarters"], 4)) for n in gt["voices"][vid] if not n["rest"]]
                    m = lcs(g, pred, lambda a, b: a == b)
                    mp = lcs([x[0] for x in g], [x[0] for x in pred], lambda a, b: a == b)
                    per_voice[vid] = round(m / len(g), 3)
                    tot += len(g); ok += m; okp += mp
            rec = {"variant": v, "image": stem, "piece": piece, "n_systems": len(det["systems"]),
                   "n_lines": len(lines), "staves_found": len(det["staves"]),
                   "note_acc": round(ok / tot, 4), "pitch_acc": round(okp / tot, 4), "per_voice": per_voice,
                   "model_ms_total": round(tm * 1000), "boxes_from_clean": det0 is not None, "ms_per_line": round(tm * 1000 / max(1, len(lines)))}
            outf.write(json.dumps(rec) + "\n")
            print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
