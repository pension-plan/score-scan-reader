#!/usr/bin/env python3
"""Synthetic scan degradations with exact ground-truth geometry transfer.

usage: degrade.py <clean.pgm> <truth.json> <dpi> <condition> <out.png> <out_truth.json> [seed]

Every geometric distortion is defined as an inverse map G: dst -> src (used to
resample the image); truth coordinates are pushed forward by numerically
inverting G (fixed-point iteration), so the truth JSON stays pixel exact.
Photometric distortions are expressed in physical units (scaled by dpi/300).
"""
import io
import json
import math
import sys

import numpy as np
from PIL import Image, ImageFilter

CONDITIONS = {
    # name: list of (op, params)
    'clean': [],
    'rot+0.6': [('rot', 0.6)],
    'rot-2': [('rot', -2.0)],
    'rot+4': [('rot', 4.0)],
    'blur1': [('blur', 1.0)],
    'blur2': [('blur', 2.0)],
    'noise20': [('noise', 20)],
    'noise45': [('noise', 45)],
    'jpeg25': [('jpeg', 25)],
    'jpeg8': [('jpeg', 8)],
    'light': [('light', 'strong')],
    'speckle': [('speckle', 0.004)],
    'bin_thick': [('blur', 1.0), ('noise', 12), ('threshold', 205)],
    'bin_thin': [('blur', 1.0), ('noise', 12), ('threshold', 60)],   # extreme: 1-2 px lines vanish
    'bin_faded': [('blur', 0.8), ('noise', 15), ('threshold', 95)],  # faded copy, broken lines
    'warp': [('warp', dict(bow=0.004, keystone=0.03, rot=0.8))],
    'scan': [('rot', 0.9), ('blur', 0.7), ('light', 'mild'), ('noise', 8), ('jpeg', 60)],
    'phone': [('warp', dict(bow=0.006, keystone=0.04, rot=-1.4)), ('light', 'strong'), ('blur', 1.2),
              ('noise', 10), ('jpeg', 45)],
}


def bilinear(img, xs, ys, fill=255.0):
    h, w = img.shape
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0
    fy = ys - y0
    valid = (x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1)
    x0c = np.clip(x0, 0, w - 2)
    y0c = np.clip(y0, 0, h - 2)
    a = img[y0c, x0c]
    b = img[y0c, x0c + 1]
    c = img[y0c + 1, x0c]
    d = img[y0c + 1, x0c + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(valid, out, fill)


def make_G(op, p, w, h):
    """Return inverse map G(xd, yd) -> (xs, ys) for a geometric op."""
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if op == 'rot':
        t = math.radians(p)
        c, s = math.cos(t), math.sin(t)

        def G(xd, yd):  # content rotated counter-clockwise by p degrees (y down)
            dx, dy = xd - cx, yd - cy
            return cx + c * dx - s * dy, cy + s * dx + c * dy
        return G
    if op == 'warp':
        t = math.radians(p.get('rot', 0.0))
        c, s = math.cos(t), math.sin(t)
        bow = p.get('bow', 0.0) * h
        ks = p.get('keystone', 0.0)

        def G(xd, yd):
            dx, dy = xd - cx, yd - cy
            xr, yr = cx + c * dx - s * dy, cy + s * dx + c * dy  # rotation
            # keystone: top of page appears narrower (camera tilt)
            scale = 1.0 + ks * (cy - yr) / h
            xk = cx + (xr - cx) * scale
            # page curl: lines bow, strongest in the middle of the page width, and
            # more towards the bottom (book gutter-ish)
            yk = yr - bow * np.sin(np.pi * np.clip(xk / w, 0, 1)) * (0.5 + yr / h)
            return xk, yk
        return G
    raise ValueError(op)


def forward(G, xs, ys, iters=30):
    """Numerically invert G: find d with G(d) = s."""
    xd, yd = np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)
    for _ in range(iters):
        gx, gy = G(xd, yd)
        xd = xd + (xs - gx)
        yd = yd + (ys - gy)
    return xd, yd


def transform_truth(t, fwd):
    def pt(p):
        x, y = fwd(np.array([p[0]]), np.array([p[1]]))
        return [float(x[0]), float(y[0])]

    def bb(b):
        xs = np.array([b[0], b[2], b[0], b[2]], dtype=np.float64)
        ys = np.array([b[1], b[1], b[3], b[3]], dtype=np.float64)
        x, y = fwd(xs, ys)
        return [float(x.min()), float(y.min()), float(x.max()), float(y.max())]

    def walk(o):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if k in ('c', 'p0', 'p1') and isinstance(v, list) and len(v) == 2:
                    o[k] = pt(v)
                elif k == 'bb' and isinstance(v, list) and len(v) == 4:
                    o[k] = bb(v)
                elif k == 'pts' and isinstance(v, list):
                    if v:
                        arr = np.array(v, dtype=np.float64)
                        x, y = fwd(arr[:, 0], arr[:, 1])
                        o[k] = [[float(a), float(b)] for a, b in zip(x, y)]
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(t)


def lighting(img, kind, rng, w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    if kind == 'mild':
        x0, y0 = w * rng.uniform(0.2, 0.8), h * rng.uniform(0.2, 0.8)
        L = 1.0 - 0.12 * (((xx - x0) ** 2 + (yy - y0) ** 2) / (w * w + h * h)) - 0.05 * xx / w
        paper, contrast = 0.93, 0.85
    else:  # strong: phone-under-lamp look, dark corner, gradient, low contrast
        x0, y0 = w * rng.uniform(0.6, 1.0), h * rng.uniform(0.0, 0.4)
        L = 1.0 - 0.55 * (((xx - x0) ** 2 + (yy - y0) ** 2) / (w * w + h * h)) - 0.15 * yy / h
        paper, contrast = 0.85, 0.70
    ink = 1.0 - img / 255.0
    return 255.0 * paper * L * (1.0 - contrast * ink)


def degrade(clean, truth, dpi, cond, seed):
    rng = np.random.default_rng(seed)
    img = clean.astype(np.float64)
    h, w = img.shape
    k = dpi / 300.0
    meta = {'name': cond, 'ops': [], 'rotDeg': 0.0}
    for op, p in CONDITIONS[cond]:
        meta['ops'].append([op, p])
        if op in ('rot', 'warp'):
            G = make_G(op, p, w, h)
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
            xs, ys = G(xx, yy)
            img = bilinear(img, xs, ys)
            transform_truth(truth, lambda a, b, G=G: forward(G, a, b))
            meta['rotDeg'] += p if op == 'rot' else p.get('rot', 0.0)
            if op == 'warp':
                meta['warp'] = p
        elif op == 'blur':
            im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
            img = np.asarray(im.filter(ImageFilter.GaussianBlur(radius=p * k)), dtype=np.float64)
        elif op == 'noise':
            img = img + rng.normal(0, p, img.shape)
        elif op == 'jpeg':
            im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
            buf = io.BytesIO()
            im.save(buf, format='JPEG', quality=int(p))
            img = np.asarray(Image.open(io.BytesIO(buf.getvalue())), dtype=np.float64)
        elif op == 'light':
            img = lighting(img, p, rng, w, h)
        elif op == 'speckle':
            # salt & pepper plus small dark blobs (dust) of ~0.3-0.8 staff-line widths
            m = rng.random(img.shape)
            img = np.where(m < p / 2, 0.0, np.where(m > 1 - p / 2, 255.0, img))
            nblobs = int(400 * k * k)
            r = max(1, int(round(2.0 * k)))
            for _ in range(nblobs):
                x, y = rng.integers(r, w - r), rng.integers(r, h - r)
                rr = rng.integers(1, r + 1)
                img[y - rr:y + rr, x - rr:x + rr] = np.minimum(img[y - rr:y + rr, x - rr:x + rr], 40)
        elif op == 'threshold':
            img = np.where(img < p, 0.0, 255.0)
        else:
            raise ValueError(op)
    truth['meta']['transform'] = meta
    return np.clip(np.rint(img), 0, 255).astype(np.uint8)


def main():
    clean_path, truth_path, dpi, cond, out_png, out_truth = sys.argv[1:7]
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 1234
    clean = np.asarray(Image.open(clean_path).convert('L'))
    truth = json.load(open(truth_path))
    out = degrade(clean, truth, int(dpi), cond, seed)
    Image.fromarray(out).save(out_png, optimize=False, compress_level=3)
    truth['meta']['image'] = out_png.split('/')[-1]
    json.dump(truth, open(out_truth, 'w'))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        print(' '.join(CONDITIONS))
    else:
        main()
