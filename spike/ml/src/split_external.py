#!/usr/bin/env python3
"""Move an ONNX model's initializers into several external-data files of <= max_mb each so every
supporting file stays under the artifact's 15 MB per-binary limit; onnxruntime-web loads them with
InferenceSession.create(modelBytes, {externalData: [{path, data: url}, ...]}).
Usage: split_external.py <in.onnx> <out.onnx> [max_mb=14]"""
import os, sys
import onnx
from onnx.external_data_helper import set_external_data
src, dst = sys.argv[1], sys.argv[2]
max_b = int(float(sys.argv[3] if len(sys.argv) > 3 else 14) * 1e6)
m = onnx.load(src)
base = os.path.basename(dst)
chunk, off, files = 0, 0, {}
fh = None
for t in m.graph.initializer:
    raw = t.raw_data if t.HasField("raw_data") else onnx.numpy_helper.to_array(t).tobytes()
    if len(raw) < 1024:
        continue
    if fh is None or off + len(raw) > max_b:
        if fh: fh.close()
        name = f"{base}.data{chunk}"; chunk += 1; off = 0
        fh = open(os.path.join(os.path.dirname(dst), name), "wb"); files[name] = 0
    pad = (-off) % 64
    fh.write(b"\0" * pad); off += pad
    fh.write(raw)
    set_external_data(t, location=name, offset=off, length=len(raw))
    t.ClearField("raw_data")
    t.data_location = onnx.TensorProto.EXTERNAL
    off += len(raw); files[name] = off
fh.close()
onnx.save(m, dst)
print(os.path.getsize(dst), files)
