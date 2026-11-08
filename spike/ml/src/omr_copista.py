#!/usr/bin/env python3
"""Reference (numpy + onnxruntime) copy of the browser-side copista detector pipeline.

Everything except the two ONNX graphs is plain array code meant to be ported 1:1 to JS:
  staff space estimate (vertical run lengths) -> resize so staff space = 10.6 px -> pad to /32 (white)
  -> dense graph -> sigmoid objectness -> 3x3 local maxima > 0.025, top 4000 -> rel graph
  -> softmax class (270 + background), score = obj * p(class), refine box -> score > 0.05 -> per-class NMS 0.7
Usage: omr_copista.py <image> [--size 2m|28m] [--variant fp32|fp16w|int8d|...] -> JSON detections on stdout
"""
import json, os, sys, time, argparse
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_SP = 10.6


def staff_space(gray):
    """Most common (black run + white run) vertical period over dark-ish columns: classic OMR estimate."""
    ink = gray < 128
    h, w = ink.shape
    cols = ink[:, :: max(1, w // 400)]
    bl = np.zeros(64, np.int64)
    wh = np.zeros(256, np.int64)
    for c in cols.T:
        d = np.diff(np.concatenate([[0], c.astype(np.int8), [0]]))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        if len(starts) < 2:
            continue
        b = ends - starts
        wgap = starts[1:] - ends[:-1]
        np.add.at(bl, np.clip(b, 0, 63), 1)
        np.add.at(wh, np.clip(wgap, 0, 255), 1)
    line = int(np.argmax(bl[1:]) + 1)
    gap = int(np.argmax(wh[2:]) + 2)
    return float(line + gap), line, gap


def imgsz_for(sp, long_side):
    return int(min(4096, max(640, round(long_side * TARGET_SP / sp / 32) * 32)))


def prepare(gray, imgsz):
    from PIL import Image
    im = Image.fromarray(gray)
    s = imgsz / max(im.width, im.height)
    w2, h2 = max(32, round(im.width * s)), max(32, round(im.height * s))
    arr = np.asarray(im.resize((w2, h2), Image.LANCZOS), dtype=np.float32) / 255.0
    H, W = -(-h2 // 32) * 32, -(-w2 // 32) * 32
    x = np.ones((1, 1, H, W), np.float32)
    x[0, 0, :h2, :w2] = arr
    return x, s


def peaks(obj_logit, K=4000, thresh=0.025):
    p = 1.0 / (1.0 + np.exp(-obj_logit[0, 0]))
    H, W = p.shape
    pad = np.pad(p, 1, constant_values=-1)
    mx = np.max(np.stack([pad[dy:dy + H, dx:dx + W] for dy in range(3) for dx in range(3)]), 0)
    cand = np.flatnonzero(((p == mx) & (p > thresh)).ravel())
    sc = p.ravel()[cand]
    order = np.argsort(-sc, kind="stable")[:K]
    idx = cand[order]
    return sc[order], idx // W, idx % W


def nms(boxes, scores, iou=0.7):
    order = np.argsort(-scores)
    keep = []
    x0, y0, x1, y1 = boxes.T
    area = (x1 - x0) * (y1 - y0)
    while len(order):
        i = order[0]
        keep.append(i)
        xx0 = np.maximum(x0[i], x0[order[1:]]); yy0 = np.maximum(y0[i], y0[order[1:]])
        xx1 = np.minimum(x1[i], x1[order[1:]]); yy1 = np.minimum(y1[i], y1[order[1:]])
        inter = np.clip(xx1 - xx0, 0, None) * np.clip(yy1 - yy0, 0, None)
        o = inter / (area[i] + area[order[1:]] - inter + 1e-9)
        order = order[1:][o <= iou]
    return np.array(keep, np.int64)


class Copista:
    def __init__(self, dense_path, rel_path, meta_path, threads=1):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self.sd = ort.InferenceSession(dense_path, so, providers=["CPUExecutionProvider"])
        self.sr = ort.InferenceSession(rel_path, so, providers=["CPUExecutionProvider"])
        self.meta = json.load(open(meta_path))
        self.classes = self.meta["classes"]
        self.attr_cls = np.array([c.partition("_")[0] in self.meta["attr_class_prefixes"] for c in self.classes])

    def run(self, gray, conf=0.05, sp=None):
        t = {}
        t0 = time.perf_counter()
        if sp is None:
            sp, _, _ = staff_space(gray)
        imgsz = imgsz_for(sp, max(gray.shape))
        x, s = prepare(gray, imgsz)
        t["prep_ms"] = (time.perf_counter() - t0) * 1e3
        t0 = time.perf_counter()
        f, obj, reg = self.sd.run(None, {"x": x})
        t["dense_ms"] = (time.perf_counter() - t0) * 1e3
        t0 = time.perf_counter()
        sc, cy, cx = peaks(obj, thresh=conf * 0.5)
        t["peaks_ms"] = (time.perf_counter() - t0) * 1e3
        n = len(sc)
        if n == 0:
            return [], {**t, "imgsz": imgsz, "sp": sp, "n_cand": 0, "input": list(x.shape)}
        t0 = time.perf_counter()
        cls_l, ref, attr, r = self.sr.run(None, {"f": f, "reg": reg, "cy": cy[None].astype(np.int64),
                                                 "cx": cx[None].astype(np.int64)})
        t["rel_ms"] = (time.perf_counter() - t0) * 1e3
        t0 = time.perf_counter()
        cl = cls_l[0].astype(np.float64)
        e = np.exp(cl - cl.max(1, keepdims=True))
        p = e / e.sum(1, keepdims=True)
        pc = p[:, :-1].max(1)
        cls = p[:, :-1].argmax(1)
        score = sc * pc
        rr = r[0] + ref[0][:, [2, 3, 0, 1]]
        stride = self.meta["stride"]
        w = np.exp(rr[:, 0]) * stride; h = np.exp(rr[:, 1]) * stride
        xc = (cx + rr[:, 2]) * stride; yc = (cy + rr[:, 3]) * stride
        boxes = np.stack([xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2], 1)
        keep = score > conf
        boxes, score, cls, at = boxes[keep], score[keep], cls[keep], attr[0][keep]
        # batched NMS: offset boxes per class
        off = cls[:, None] * 1e5
        k = nms(boxes + off, score, 0.7) if len(boxes) else np.zeros(0, np.int64)
        boxes, score, cls, at = boxes[k], score[k], cls[k], at[k]
        dets = []
        vocab, offs, sizes = self.meta["attr_vocab"], self.meta["attr_offsets"], self.meta["attr_sizes"]
        for b, scv, c, a in zip(boxes, score, cls, at):
            b = [float(v) / s for v in b]
            rec = {"cls": self.classes[c], "conf": round(float(scv), 3), "xyxy": [round(v, 1) for v in b]}
            if self.attr_cls[c]:
                rec["attrs"] = {}
                for name in vocab:
                    lg = a[offs[name]:offs[name] + sizes[name]]
                    rec["attrs"][name] = vocab[name][int(np.argmax(lg))]
            dets.append(rec)
        t["post_ms"] = (time.perf_counter() - t0) * 1e3
        return dets, {**{k2: round(v, 1) for k2, v in t.items()}, "imgsz": imgsz, "sp": sp, "n_cand": int(n),
                      "input": list(x.shape)}


def model_paths(size, variant):
    d = os.path.join(ROOT, "out", "onnx")
    suf = "" if variant == "fp32" else "." + variant
    return (os.path.join(d, f"copista{size}-dense{suf}.onnx"), os.path.join(d, f"copista{size}-rel{suf}.onnx"),
            os.path.join(d, f"copista{size}-classes.json"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--size", default="2m")
    ap.add_argument("--variant", default="fp32")
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    from PIL import Image
    gray = np.asarray(Image.open(a.image).convert("L"))
    m = Copista(*model_paths(a.size, a.variant), threads=a.threads)
    dets, t = m.run(gray)
    print(json.dumps({"timing": t, "dets": dets}))
