#!/usr/bin/env python3
"""Score an OMR MusicXML output against the spike ground truth (scans/gt/<piece>.json).

Metrics (all 0..1, higher is better):
  mp_f1   measure-pitch F1: per-measure multiset of MIDI pitches, voice/part agnostic
  mpd_f1  same with (pitch, duration) pairs
  voice_acc  one-to-one assignment of predicted (part,staff,voice) streams to GT voices
             (Hungarian on LCS matches of (pitch,duration) sequences); a stream holding
             chords can only serve ONE GT voice, so un-separated closed score scores ~0.5
  n_parts, n_streams   structure of the prediction
Usage: eval_xml.py <pred.musicxml> <piece_id>  (prints JSON)
"""
import json, os, sys, re
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def strip_ns(root):
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return root


def parse_pred(path):
    """-> parts: [{id, measures:[[event...]]}], event=(stream_key, midi|None, quarters, onset)"""
    root = strip_ns(ET.parse(path).getroot())
    parts = []
    for part in root.findall("part"):
        pid = part.get("id")
        divisions = 1.0
        measures = []
        for meas in part.findall("measure"):
            t = 0.0
            last_onset = 0.0
            evs = []
            for el in meas:
                if el.tag == "attributes":
                    d = el.find("divisions")
                    if d is not None:
                        divisions = float(d.text)
                elif el.tag == "backup":
                    t -= float(el.find("duration").text) / divisions
                elif el.tag == "forward":
                    t += float(el.find("duration").text) / divisions
                elif el.tag == "note":
                    if el.find("grace") is not None:
                        continue
                    dur_el = el.find("duration")
                    q = float(dur_el.text) / divisions if dur_el is not None else 0.0
                    is_chord = el.find("chord") is not None
                    onset = last_onset if is_chord else t
                    v = el.findtext("voice", "1")
                    s = el.findtext("staff", "1")
                    p = el.find("pitch")
                    midi = None
                    if p is not None:
                        midi = 12 * (int(p.findtext("octave")) + 1) + STEPS[p.findtext("step")] + int(
                            round(float(p.findtext("alter", "0"))))
                    evs.append(((pid, s, v), midi, round(q, 4), round(onset, 4), is_chord))
                    if not is_chord:
                        last_onset = t
                        t += q
            measures.append(evs)
        parts.append({"id": pid, "measures": measures})
    return parts


def lcs(a, b, eq):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        for j in range(1, m + 1):
            cur[j] = prev[j - 1] + 1 if eq(a[i - 1], b[j - 1]) else max(prev[j], cur[j - 1])
        prev = cur
    return prev[m]


def hungarian_max(W):
    """small brute-force/greedy-optimal assignment (rows=GT voices <= 4)."""
    import itertools
    R = len(W)
    C = len(W[0]) if R else 0
    best = 0
    if C == 0:
        return 0
    cols = list(range(C))
    if C < R:
        for perm in itertools.permutations(range(R), C):
            best = max(best, sum(W[perm[k]][k] for k in range(C)))
        return best
    for perm in itertools.permutations(cols, R):
        best = max(best, sum(W[r][perm[r]] for r in range(R)))
    return best


def evaluate(pred_path, piece):
    gt = json.load(open(os.path.join(ROOT, "scans", "gt", piece + ".json")))
    gvoices = gt["voices"]
    nmeas = max(n["measure"] for v in gvoices.values() for n in v) + 1
    g_m = [Counter() for _ in range(nmeas)]
    g_md = [Counter() for _ in range(nmeas)]
    for v in gvoices.values():
        for n in v:
            if n["rest"]:
                continue
            g_m[n["measure"]][n["midi"]] += 1
            g_md[n["measure"]][(n["midi"], round(n["quarters"], 4))] += 1
    try:
        parts = parse_pred(pred_path)
    except Exception as e:  # unreadable output
        return {"error": str(e), "mp_f1": 0, "mpd_f1": 0, "voice_acc": 0}
    # align measures by index; for a piece with pickup both GT and pred start with the pickup bar
    p_m = [Counter() for _ in range(max(nmeas, max((len(p["measures"]) for p in parts), default=0)))]
    p_md = [Counter() for _ in range(len(p_m))]
    streams = {}
    for p in parts:
        for mi, evs in enumerate(p["measures"]):
            for key, midi, q, onset, is_chord in evs:
                if midi is None:
                    continue
                p_m[mi][midi] += 1
                p_md[mi][(midi, q)] += 1
                st = streams.setdefault(key, {})
                st.setdefault((mi, onset), [set(), q])[0].add(midi)

    def f1(G, P):
        tp = sum(sum((G[i] & P[i]).values()) for i in range(min(len(G), len(P))))
        ng = sum(sum(c.values()) for c in G)
        npred = sum(sum(c.values()) for c in P)
        prec = tp / npred if npred else 0.0
        rec = tp / ng if ng else 0.0
        return (2 * prec * rec / (prec + rec) if prec + rec else 0.0), prec, rec

    mp, mp_p, mp_r = f1(g_m, p_m)
    mpd, _, _ = f1(g_md, p_md)
    # voice streams
    gseqs = {vid: [(n["measure"], n["midi"], round(n["quarters"], 4)) for n in v if not n["rest"]]
             for vid, v in gvoices.items()}
    pseqs = []
    for key, evmap in streams.items():
        seq = [(mi, pitches, q) for (mi, on), (pitches, q) in sorted(evmap.items())]
        pseqs.append((key, seq))
    eq = lambda g, p: g[0] == p[0] and g[1] in p[1] and abs(g[2] - p[2]) < 1e-3
    vids = list(gseqs)
    W = [[lcs(gseqs[vid], ps, eq) for _, ps in pseqs] for vid in vids]
    total = sum(len(s) for s in gseqs.values())
    vacc = hungarian_max(W) / total if total and pseqs else 0.0
    return {"mp_f1": round(mp, 4), "mp_prec": round(mp_p, 4), "mp_rec": round(mp_r, 4),
            "mpd_f1": round(mpd, 4), "voice_acc": round(vacc, 4),
            "n_parts": len(parts), "n_streams": len(pseqs),
            "n_meas_pred": max((len(p["measures"]) for p in parts), default=0), "n_meas_gt": nmeas}


if __name__ == "__main__":
    print(json.dumps(evaluate(sys.argv[1], sys.argv[2])))
