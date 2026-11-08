#!/usr/bin/env python3
"""Make size-reduced variants of an fp32 ONNX model and report sizes.

variants
  fp16w  weights stored as fp16, a Cast->fp32 after each (compute stays fp32; ORT folds the casts at load).
         Works on every EP incl. onnxruntime-web wasm.  Size ~1/2.
  int8w  weights >= 1024 elems stored int8 per-output-channel (symmetric) + DequantizeLinear -> fp32 compute.
         Size ~1/4, accuracy close to fp32, speed ~= fp32.
  fp16   full fp16 graph (onnxconverter-common, keep_io_types).  Needs fp16 kernels (WebGPU); on CPU/wasm
         many ops have no fp16 kernel -> fails or falls back slowly.
  int8d  onnxruntime.quantization.quantize_dynamic (QInt8 weights; MatMulInteger/ConvInteger, activations
         quantized at run time).  Size ~1/4.
Usage: quantize.py <model.onnx> <out_prefix> [variants...]
"""
import os, sys, json
import numpy as np
import onnx
from onnx import helper, numpy_helper, TensorProto

MIN_ELEMS = 1024


def _consumers(model):
    cons = {}
    for n in model.graph.node:
        for i, x in enumerate(n.input):
            cons.setdefault(x, []).append((n, i))
    return cons


def weight_only(model, mode):
    g = model.graph
    cons = _consumers(model)
    new_inits, new_nodes = [], []
    for init in list(g.initializer):
        if init.data_type != TensorProto.FLOAT:
            continue
        w = numpy_helper.to_array(init)
        if w.size < MIN_ELEMS:
            continue
        users = cons.get(init.name, [])
        if not users:
            continue
        name = init.name
        if mode == "fp16w":
            q = numpy_helper.from_array(w.astype(np.float16), name + "_f16")
            node = helper.make_node("Cast", [q.name], [name], to=TensorProto.FLOAT, name=name + "_cast")
            new_inits.append(q)
        else:  # int8w, per output channel (axis 0) symmetric
            # MatMul weights are [K, N] (out channels on axis 1); Conv/Gemm(transB) are [O, ...] (axis 0)
            axis = 0
            op = users[0][0].op_type
            if op == "MatMul" and w.ndim == 2:
                axis = 1
            if op == "Gemm":
                tb = next((a.i for a in users[0][0].attribute if a.name == "transB"), 0)
                axis = 0 if tb else 1
            if w.ndim == 1:
                axis = 0
                amax = np.abs(w).max(keepdims=True)
                scale = (np.maximum(amax, 1e-12) / 127.0).astype(np.float32).reshape(1)
                qw = np.clip(np.round(w / scale), -127, 127).astype(np.int8)
                sc = numpy_helper.from_array(scale.reshape(()), name + "_scale")
                zp = numpy_helper.from_array(np.zeros((), np.int8), name + "_zp")
                node = helper.make_node("DequantizeLinear", [name + "_q", sc.name, zp.name], [name], name=name + "_dq")
            else:
                red = tuple(i for i in range(w.ndim) if i != axis)
                amax = np.abs(w).max(axis=red)
                scale = (np.maximum(amax, 1e-12) / 127.0).astype(np.float32)
                shp = [1] * w.ndim
                shp[axis] = -1
                qw = np.clip(np.round(w / scale.reshape(shp)), -127, 127).astype(np.int8)
                sc = numpy_helper.from_array(scale, name + "_scale")
                zp = numpy_helper.from_array(np.zeros(scale.shape, np.int8), name + "_zp")
                node = helper.make_node("DequantizeLinear", [name + "_q", sc.name, zp.name], [name],
                                        axis=axis, name=name + "_dq")
            new_inits += [numpy_helper.from_array(qw, name + "_q"), sc, zp]
        g.initializer.remove(init)
        new_nodes.append(node)
    # prepend producer nodes (topological order: they only depend on initializers)
    nodes = list(g.node)
    del g.node[:]
    g.node.extend(new_nodes + nodes)
    g.initializer.extend(new_inits)
    # DequantizeLinear with axis needs opset >= 13
    for op in model.opset_import:
        if op.domain in ("", "ai.onnx") and op.version < 13:
            op.version = 13
    return model


def make(src, prefix, variant):
    out = f"{prefix}.{variant}.onnx"
    if variant in ("fp16w", "int8w"):
        m = onnx.load(src)
        if min(o.version for o in m.opset_import if o.domain in ("", "ai.onnx")) < 13:
            from onnx import version_converter
            m = version_converter.convert_version(m, 13)
        m = weight_only(m, variant)
        onnx.save(m, out)
    elif variant == "fp16":
        from onnxconverter_common import float16
        m = onnx.load(src)
        m16 = float16.convert_float_to_float16(m, keep_io_types=True)
        onnx.save(m16, out)
    elif variant == "int8d":
        from onnxruntime.quantization import quantize_dynamic, QuantType
        from onnxruntime.quantization.shape_inference import quant_pre_process
        tmp = out + ".pre.onnx"
        try:
            quant_pre_process(src, tmp, skip_symbolic_shape=True)
        except Exception as e:  # noqa: BLE001
            print("pre_process failed:", e, file=sys.stderr)
            tmp = src
        quantize_dynamic(tmp, out, weight_type=QuantType.QInt8, per_channel=True)
        if tmp != src and os.path.exists(tmp):
            os.remove(tmp)
    else:
        raise ValueError(variant)
    return out


def describe(path):
    m = onnx.load(path, load_external_data=False)
    ops = {}
    for n in m.graph.node:
        ops[n.op_type] = ops.get(n.op_type, 0) + 1
    params = sum(int(np.prod(i.dims)) for i in m.graph.initializer)
    ins = [(i.name, [d.dim_param or d.dim_value for d in i.type.tensor_type.shape.dim]) for i in m.graph.input]
    outs = [(o.name, [d.dim_param or d.dim_value for d in o.type.tensor_type.shape.dim]) for o in m.graph.output]
    return {"bytes": os.path.getsize(path), "params": params, "opset": [(o.domain or "ai.onnx", o.version) for o in m.opset_import],
            "ir": m.ir_version, "inputs": ins, "outputs": outs, "ops": ops, "producer": f"{m.producer_name} {m.producer_version}"}


if __name__ == "__main__":
    src, prefix = sys.argv[1], sys.argv[2]
    variants = sys.argv[3:] or ["fp16w", "int8w", "fp16", "int8d"]
    rep = {"fp32": describe(src)}
    for v in variants:
        try:
            p = make(src, prefix, v)
            d = describe(p)
            rep[v] = {"bytes": d["bytes"], "ops": d["ops"]}
        except Exception as e:  # noqa: BLE001
            rep[v] = {"error": repr(e)[:300]}
        print(v, rep[v].get("bytes", rep[v].get("error")), flush=True)
    with open(prefix + ".quant.json", "w") as f:
        json.dump(rep, f, indent=1)
