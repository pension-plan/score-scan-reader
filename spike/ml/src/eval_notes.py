#!/usr/bin/env python3
"""Notehead-level scoring of raw detector output against scans/<img>.boxes.json.

match_points(): greedy nearest matching of predicted notehead centres to GT centres within
0.6 x GT notehead width.  Returns P/R/F1 and, for matched copista notes, attribute accuracy:
  pos_acc    staff_position (half-spaces from the middle line) vs GT pitch + clef
  stem_acc   stem_dir vs GT voice role (S/T up, A/B down in closed score); melody/open not scored
  voice_acc  voice_slot (1 = voiceOne, 2 = voiceTwo) in closed score
"""
import json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAT = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
MID = {"treble": ("B", 4), "bass": ("D", 3), "treble_8": ("B", 3)}


def gt_info(image_stem):
    b = json.load(open(os.path.join(ROOT, "scans", image_stem + ".boxes.json")))
    piece = image_stem.rsplit("_", 2)[0]
    g = json.load(open(os.path.join(ROOT, "scans", "gt", piece + ".json")))
    import pieces
    P = pieces.PIECES[piece]
    clef = {vid: st["clef"] for st in P["staves"] for vid, _, _ in st["voices"]}
    closed = piece == "satb_closed"
    out = []
    for h in b["noteheads"]:
        n = g["voices"][h["voice"]][h["idx"]]
        ms, mo = MID[clef[h["voice"]]]
        pos = (n["octave"] * 7 + DIAT[n["step"]]) - (mo * 7 + DIAT[ms])
        stem = None
        slot = None
        if closed and n["dur"] != 1:  # whole notes have no stem
            stem = "up" if h["voice"] in ("soprano", "tenor") else "down"
        if closed:
            slot = "1" if h["voice"] in ("soprano", "tenor") else "2"
        out.append({**h, "pos": pos, "stem": stem, "slot": slot})
    return b, out


def match_points(pred, gt, tol_frac=0.6):
    """pred: list of dict(cx, cy, [attrs]); gt: list from gt_info. Greedy by distance."""
    if not gt:
        return {}
    G = np.array([[g["cx"], g["cy"]] for g in gt])
    tol = tol_frac * np.median([g["w"] for g in gt])
    pairs = []
    for i, p in enumerate(pred):
        d = np.hypot(G[:, 0] - p["cx"], G[:, 1] - p["cy"])
        for j in np.flatnonzero(d < tol):
            pairs.append((d[j], i, j))
    pairs.sort()
    used_p, used_g = set(), set()
    matches = []
    for d, i, j in pairs:
        if i in used_p or j in used_g:
            continue
        used_p.add(i); used_g.add(j)
        matches.append((i, j))
    tp = len(matches)
    prec = tp / len(pred) if pred else 0.0
    rec = tp / len(gt)
    res = {"n_gt": len(gt), "n_pred": len(pred), "tp": tp, "prec": round(prec, 4), "rec": round(rec, 4),
           "f1": round(2 * prec * rec / (prec + rec), 4) if tp else 0.0}
    if pred and "attrs" in pred[0]:
        pos_ok = stem_ok = slot_ok = n_cl = 0
        for i, j in matches:
            a = pred[i]["attrs"]
            try:
                pos_ok += int(int(a.get("staff_position", "99")) == gt[j]["pos"])
            except ValueError:
                pass
            if gt[j]["stem"] is not None:
                n_cl += 1
                stem_ok += int(a.get("stem_dir") == gt[j]["stem"])
                slot_ok += int(a.get("voice_slot") == gt[j]["slot"])
        res["pos_acc"] = round(pos_ok / tp, 4) if tp else 0.0
        if n_cl:
            res["stem_acc"] = round(stem_ok / n_cl, 4)
            res["voice_acc"] = round(slot_ok / n_cl, 4)
    return res


def copista_noteheads(dets):
    out = []
    for d in dets:
        if not d["cls"].startswith("note_"):
            continue
        x0, y0, x1, y1 = d["xyxy"]
        out.append({"cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2, "attrs": d.get("attrs", {}), "conf": d["conf"]})
    return out


def mask_noteheads(mask, min_area=10):
    """connected components of a binary notehead mask -> centres (chords split by GT later is not attempted)."""
    import cv2
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    return [{"cx": float(c[0]), "cy": float(c[1]), "area": int(s[4])}
            for c, s in zip(cent[1:], stats[1:]) if s[4] >= min_area]


def mask_recall(mask, gt, frac=0.3):
    """pixel-level: a GT notehead counts as found if >= frac of its box is notehead in the mask;
    precision: fraction of mask pixels that fall inside any (slightly dilated) GT notehead box."""
    hit = 0
    inside = np.zeros_like(mask, dtype=bool)
    for g in gt:
        x0, x1 = int(g["cx"] - g["w"] / 2), int(g["cx"] + g["w"] / 2)
        y0, y1 = int(g["cy"] - g["h"] / 2), int(g["cy"] + g["h"] / 2)
        box = mask[max(0, y0):y1, max(0, x0):x1]
        if box.size and box.mean() >= frac:
            hit += 1
        m = int(0.25 * g["h"])
        inside[max(0, y0 - m):y1 + m, max(0, x0 - m):x1 + m] = True
    npx = int(mask.sum())
    return {"rec_px": round(hit / len(gt), 4), "prec_px": round(float((mask & inside).sum()) / npx, 4) if npx else 0.0}
