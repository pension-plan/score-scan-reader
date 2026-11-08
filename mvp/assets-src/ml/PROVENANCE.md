# Provenance of spike/ml/assets

Everything here is derived from **kobimusic copista** weights, licensed **Apache-2.0** (weights and the
copisteria reader code). Apache-2.0 §4 obligations when shipping: keep `LICENSE.copista-Apache-2.0.txt`,
keep the `NOTICE.*` files, credit KobiMusic with a link to the Hugging Face repo, and state that the files
were modified (converted to ONNX, split into two graphs, weights re-encoded). No GPL/AGPL code or weights.

Checksums of every file: `SHA256SUMS`.

## Sources (downloaded 2026-11-08)

| Source file | From | Revision | sha256 |
|---|---|---|---|
| `small/v7_obj-recall_best.pt` (copista-2m detector, 1,921,591 params, arch `obj-recall`, epoch 14) | https://huggingface.co/kobimusic/copista-2m | HF repo sha `c37d89e1e52edc95c1a73bda0aea5f2f71a9c763`, lastModified 2026-10-06 | `b6dd1d9e0431e267f088ab5a2201c102920cd3da806f77950c9df6217aeb76e4` |
| `small/v7_obj-recall-30m_best.pt` (copista-28m detector, 28,721,631 params, arch `obj-recall-30m`, epoch 17) | https://huggingface.co/kobimusic/copista-28m | HF repo sha `44464d11234a22ba23634ec8eb1e31e3b012021a`, lastModified 2026-10-06 | `9f1db282271fb1064461387da4a2e15de14b099c49b619c21429cdc45be85cfe` |
| model code (`copisteria.detector.small.arch2/arch9/models`) | https://github.com/kobimusic/copisteria | commit `c685f280914d91a694494588d9f6a376d7917eba` (2026-10-28), package version 1.3.4 | n/a |

The detector is a custom PyTorch CenterNet-style model (stride-4 dense trunk + a 2-3 layer transformer
"relational" verifier over the peak candidates). It is **not** an Ultralytics/YOLO model, so the Ultralytics
AGPL does not apply. Training data per the model card: rendered pages (the evidence model: 31,800 pages from
28,000 PDMX scores with scan effects; the detector: "87K pages", corpus not itemised in the card).

## Conversion (reproducible)

```
# 1. ONNX export (torch 2.15.0+cpu, torchvision 0.29.2, legacy exporter, opset 17), parity-checked vs torch
spike/ml/.venv-cop/bin/python spike/ml/src/export_copista.py
#    -> copista{2m,28m}-dense.onnx  x[1,1,H,W] -> f, obj, reg      (H, W multiples of 32; white = 1.0)
#    -> copista{2m,28m}-rel.onnx    f, reg, cy[1,n], cx[1,n] -> cls[1,n,271], ref, attr[1,n,64], r
#    The relational decoder's nn.TransformerEncoder is re-implemented with -1 reshapes (same weights, max diff
#    3e-6) so the candidate count n stays dynamic.  Max |onnx - torch| on random input: 2.3e-5 (obj logits).
# 2. size variants (onnx 1.23.x, onnxruntime 1.31.1 quantization tools)
spike/ml/.venv/bin/python spike/ml/src/quantize.py out/onnx/copista2m-dense.onnx out/onnx/copista2m-dense fp16w int8w
#    fp16w = initializers stored fp16 + Cast (fp32 compute);  int8w = per-output-channel symmetric int8
#    initializers + DequantizeLinear (fp32 compute).  int8d (ORT dynamic quantization) was evaluated and rejected:
#    3x SLOWER under onnxruntime-web wasm.
# 3. 28m only: split weights into <= 14 MB external-data files (artifact per-file limit 15 MB)
spike/ml/.venv/bin/python spike/ml/src/split_external.py out/onnx/copista28m-dense.int8w.onnx out/onnx/copista28m-dense.int8w.split.onnx 14
```

## Files

| File | Bytes | What | Status |
|---|---:|---|---|
| `copista2m-dense.int8w.onnx` | 1,765,488 | dense trunk, int8 weight storage | **recommended** |
| `copista2m-rel.int8w.onnx` | 290,981 | relational verifier, int8 weight storage | **recommended** |
| `copista2m-dense.fp16w.onnx` / `copista2m-rel.fp16w.onnx` | 3.38 MB / 0.52 MB | fp16 weight storage | equivalent alternative |
| `copista2m-dense.onnx` / `copista2m-rel.onnx` | 6.71 MB / 1.01 MB | fp32 reference export | reference |
| `copista2m-classes.json` | | 270 class names, attribute vocabularies/offsets, stride 4, k_infer 4000, target staff space 10.6 px | required |
| `copista28m/copista28m-dense.int8w.split.onnx` + `.data0` (13.7 MB) + `.data1` (13.0 MB) | | 28m trunk, int8 weights split for the 15 MB limit | optional, ~47 s/page in wasm (Chromium, 1 thread) |
| `copista28m/copista28m-rel.int8w.onnx` | 2.25 MB | 28m verifier | optional |

Runtime to pair with (not copied here, self-host from the npm tarball):
`onnxruntime-web@1.30.0/dist/ort-wasm-simd-threaded.wasm` (14,239,897 bytes,
sha256 `3398c10d07d229bd91b364548e130e0e51a8e5704b88c7c083ebbeb78842dee2`) with
`ort.wasm.bundle.min.mjs` from `https://cdn.jsdelivr.net/npm/onnxruntime-web@1.30.0/dist/` (or cdnjs
`https://cdnjs.cloudflare.com/ajax/libs/onnxruntime-web/1.30.0/`), MIT licence.
Fallback: `onnxruntime-web@1.18.0` `ort.wasm.min.js` (UMD) + self-hosted `ort-wasm-simd.wasm`
(10,595,041 bytes, sha256 `f533b5f21790563d7556c611c3835ac65848ee326da2689aac54ed7d9cc8c6a4`).

JS pipeline that uses these files: `spike/ml/src/copista_core.mjs` (no deps; staff-space estimate, resample,
peak picking, box decode, NMS); Python reference `spike/ml/src/omr_copista.py`.

Loading rules measured under an artifact-like CSP (details in `docs/spike-ml.md`): set `ort.env.wasm.numThreads = 1`;
with 1.30.0 pass `wasmPaths = { wasm: <absolute URL of the .wasm> }` (a string prefix makes ORT import the `.mjs` glue
from the same origin, which script-src blocks); load the bundle via dynamic `import()` in a blob: module worker.
Do not use ORT dynamic-int8 (`int8d`) models: 3x slower in wasm, and ORT-web 1.18.0 lacks ConvInteger.
