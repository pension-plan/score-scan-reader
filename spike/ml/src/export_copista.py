#!/usr/bin/env python3
"""Export the copista detectors (kobimusic/copista-2m, -28m; Apache-2.0) to ONNX as two graphs.

  copista<size>-dense.onnx : x [1,1,H,W] (gray 0..1, white=1, H,W multiples of 32)
                             -> f [1,C,H/4,W/4], obj [1,1,H/4,W/4] (logit), reg [1,4,H/4,W/4]
  copista<size>-rel.onnx   : f, reg, cy [1,n] int64, cx [1,n] int64  (candidate peak cells)
                             -> cls [1,n,271] logits (last = background), ref [1,n,4], attr [1,n,64], r [1,n,4]
Peak picking (3x3 max, thresh, top-k), box decode and NMS are plain array code (JS-friendly), see
omr_copista.py.  Run with .venv-cop/bin/python src/export_copista.py
"""
import os, sys, json, time
import torch
import torch.nn as nn
import torchvision.ops  # noqa: F401  (import before tracing: roi_align)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COP = os.path.join(ROOT, "dl", "copisteria")
sys.path.insert(0, os.path.join(COP, "src"))
from copisteria.detector.small import models as M  # noqa: E402

OUT = os.path.join(ROOT, "out", "onnx")
os.makedirs(OUT, exist_ok=True)


class Dense(nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, x):
        o = self.m(x)
        return o["f"], o["obj"], o["reg"]


class ExportDecoder(nn.Module):
    """Same math as nn.TransformerEncoder(norm_first, gelu, no padding) but with -1 reshapes so the
    legacy ONNX exporter keeps the candidate count n dynamic (MHA fast path bakes n into Reshape)."""

    def __init__(self, dec):
        super().__init__()
        self.layers = dec.enc.layers

    def forward(self, x, pad_mask=None):
        for L in self.layers:
            a = L.self_attn
            h, d = a.num_heads, a.embed_dim
            dh = d // h
            y = L.norm1(x)
            qkv = torch.nn.functional.linear(y, a.in_proj_weight, a.in_proj_bias)      # [1, n, 3d]
            q, k, v = qkv.split(d, dim=-1)
            q = q.reshape(1, -1, h, dh).transpose(1, 2)
            k = k.reshape(1, -1, h, dh).transpose(1, 2)
            v = v.reshape(1, -1, h, dh).transpose(1, 2)
            att = torch.softmax(torch.matmul(q, k.transpose(-1, -2)) * (dh ** -0.5), dim=-1)
            o = torch.matmul(att, v).transpose(1, 2).reshape(1, -1, d)
            x = x + a.out_proj(o)
            y = L.norm2(x)
            x = x + L.linear2(torch.nn.functional.gelu(L.linear1(y)))
        return x


class Rel(nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, f, reg, cy, cx):
        pad = torch.zeros_like(cy, dtype=torch.bool)
        cls_logit, ref, attr, r = self.m._run({"f": f, "reg": reg}, cy, cx, pad)
        return cls_logit, ref, attr, r


def main():
    meta = {}
    for size, ck_path in (("2m", "models/small/v7_obj-recall_best.pt"), ("28m", "models/small/v7_obj-recall-30m_best.pt")):
        ck = torch.load(os.path.join(COP, ck_path), map_location="cpu", weights_only=False)
        m = M.build(ck["arch"], ck["classes"]).eval()
        m.load_state_dict(ck["ema"])
        nparam = sum(p.numel() for p in m.parameters())
        dense_p = sum(p.numel() for n, p in m.named_parameters() if n.split(".")[0] in ("enc", "fpn", "obj", "reg"))
        x = torch.ones(1, 1, 512, 384)
        x[0, 0, 100:110, 50:300] = 0.0
        d = Dense(m).eval()
        with torch.no_grad():   # check the re-implemented decoder against the original on random tokens
            tok = torch.randn(1, 37, m.d)
            ref_out = m.dec(tok, torch.zeros(1, 37, dtype=torch.bool))
            m.dec = ExportDecoder(m.dec)
            dec_diff = float((m.dec(tok) - ref_out).abs().max())
        r = Rel(m).eval()
        with torch.no_grad():
            f, obj, reg = d(x)
            n = 50
            cy = torch.randint(0, f.shape[2], (1, n))
            cx = torch.randint(0, f.shape[3], (1, n))
        t0 = time.time()
        dense_path = os.path.join(OUT, f"copista{size}-dense.onnx")
        torch.onnx.export(d, (x,), dense_path, input_names=["x"], output_names=["f", "obj", "reg"],
                          dynamic_axes={"x": {2: "H", 3: "W"}, "f": {2: "h", 3: "w"}, "obj": {2: "h", 3: "w"},
                                        "reg": {2: "h", 3: "w"}}, opset_version=17, dynamo=False)
        rel_path = os.path.join(OUT, f"copista{size}-rel.onnx")
        torch.onnx.export(r, (f, reg, cy, cx), rel_path, input_names=["f", "reg", "cy", "cx"],
                          output_names=["cls", "ref", "attr", "r"],
                          dynamic_axes={"f": {2: "h", 3: "w"}, "reg": {2: "h", 3: "w"}, "cy": {1: "n"}, "cx": {1: "n"},
                                        "cls": {1: "n"}, "ref": {1: "n"}, "attr": {1: "n"}, "r": {1: "n"}},
                          opset_version=17, dynamo=False)
        # parity check with onnxruntime
        import onnxruntime as ort
        import numpy as np
        sd = ort.InferenceSession(dense_path, providers=["CPUExecutionProvider"])
        sr = ort.InferenceSession(rel_path, providers=["CPUExecutionProvider"])
        x2 = torch.rand(1, 1, 640, 448)
        with torch.no_grad():
            tf, to, treg = d(x2)
            cy2 = torch.randint(0, tf.shape[2], (1, 300))
            cx2 = torch.randint(0, tf.shape[3], (1, 300))
            tc, tref, ta, tr = r(tf, treg, cy2, cx2)
        of, oo, oreg = sd.run(None, {"x": x2.numpy()})
        oc, oref, oa, orr = sr.run(None, {"f": tf.numpy(), "reg": treg.numpy(), "cy": cy2.numpy(), "cx": cx2.numpy()})
        diff = {"f": float(np.abs(of - tf.numpy()).max()), "obj": float(np.abs(oo - to.numpy()).max()),
                "cls": float(np.abs(oc - tc.numpy()).max()), "attr": float(np.abs(oa - ta.numpy()).max())}
        meta[size] = {"arch": ck["arch"], "params_total": nparam, "params_dense": dense_p,
                      "n_classes": len(ck["classes"]), "epoch": ck.get("epoch"),
                      "dense_bytes": os.path.getsize(dense_path), "rel_bytes": os.path.getsize(rel_path),
                      "export_s": round(time.time() - t0, 1), "max_abs_diff_vs_torch": diff,
                      "k_infer": m.k_infer, "stride": m.stride, "decoder_reimpl_max_diff": dec_diff}
        print(size, json.dumps(meta[size]), flush=True)
        with open(os.path.join(OUT, f"copista{size}-classes.json"), "w") as fh:
            from copisteria.detector.small.export import ATTR_VOCAB
            from copisteria.detector.small.data import ATTR_OFFSETS, ATTR_SIZES
            json.dump({"classes": ck["classes"], "attr_vocab": ATTR_VOCAB, "attr_offsets": ATTR_OFFSETS,
                       "attr_sizes": ATTR_SIZES, "attr_class_prefixes": list(M.ATTR_CLASS_PREFIXES),
                       "stride": m.stride, "k_infer": m.k_infer, "target_staff_space_px": 10.6}, fh)
    with open(os.path.join(OUT, "copista-export.json"), "w") as fh:
        json.dump(meta, fh, indent=1)


if __name__ == "__main__":
    main()
