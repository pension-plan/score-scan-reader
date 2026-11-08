#!/usr/bin/env python3
"""Degrade clean 300dpi renders into scan-like variants and transform GT accordingly.
Usage: degrade.py CLEAN_PNG OUTROOT   (expects CLEAN_PNG with sibling .gt.json)
Variants: scan300 (gray scan, tilt, blur, noise, jpeg), bilevel300 (IMSLP-like 1-bit, thresholded, speckle),
          copy200 (photocopy 200dpi: dark/thick, toner noise, gutter shadow), phone150 (150dpi, uneven light, jpeg q55)."""
import json, os, sys, copy, hashlib
import numpy as np, cv2

def rot(img, ang, border=255):
    h, w = img.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=border), M

def tf_box(b, M, s=1.0):
    x0, y0, x1, y1 = b
    pts = np.array([[x0, y0, 1], [x1, y0, 1], [x0, y1, 1], [x1, y1, 1]], float) @ M.T
    return [round(float(pts[:, 0].min() * s), 1), round(float(pts[:, 1].min() * s), 1), round(float(pts[:, 0].max() * s), 1), round(float(pts[:, 1].max() * s), 1)]

def tf_gt(gt, M, s, W, H, name, ang):
    g = copy.deepcopy(gt)
    g["variant"] = name; g["width"] = W; g["height"] = H; g["dpi"] = round(gt["dpi"] * s); g["tilt_deg"] = ang
    def P(x, y):
        q = M @ np.array([x, y, 1.0])
        return float(q[0] * s), float(q[1] * s)
    for L in g["lines"]:
        bl = L["baseline"]
        cx = (L["bbox"][0] + L["bbox"][2]) / 2
        for k in ("bbox", "fontbox"):
            L[k] = tf_box(L[k], M, s)
        L["size_px"] = round(L["size_px"] * s, 2)
        L["baseline"] = round(P(cx, bl)[1], 1)
        for sy in L["syllables"]:
            sy["x0"] = round(P(sy["x0"], bl)[0], 1); sy["x1"] = round(P(sy["x1"], bl)[0], 1)
    return g

def jpeg(img, q):
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, int(q)])
    return cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)

def illum(h, w, rng, amp):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a, b, c = rng.uniform(-1, 1, 3)
    f = a * (xx / w - 0.5) + b * (yy / h - 0.5) + c * ((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2)
    f = (f - f.min()) / (np.ptp(f) + 1e-6)
    return 1.0 - amp * f

def main():
    src, root = sys.argv[1], sys.argv[2]
    gt = json.load(open(src[:-4] + ".gt.json"))
    base = os.path.basename(src)[:-4]
    seed = int(hashlib.md5(base.encode()).hexdigest()[:8], 16)
    img0 = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
    H0, W0 = img0.shape
    out = {}
    # scan300
    rng = np.random.default_rng(seed + 1)
    ang = float(rng.uniform(-0.35, 0.35))
    im, M = rot(img0, ang)
    im = cv2.GaussianBlur(im, (0, 0), rng.uniform(0.5, 0.9)).astype(np.float32)
    paper = rng.uniform(228, 245)
    im = paper - (255 - im) * rng.uniform(0.8, 0.95)
    im *= illum(H0, W0, rng, 0.08)
    im += rng.normal(0, 6, im.shape)
    im = jpeg(np.clip(im, 0, 255).astype(np.uint8), rng.integers(70, 86))
    out["scan300"] = (im, M, 1.0, ang)
    # bilevel300
    rng = np.random.default_rng(seed + 2)
    ang = float(rng.uniform(-0.3, 0.3))
    im, M = rot(img0, ang)
    im = cv2.GaussianBlur(im, (0, 0), 0.8)
    im = im.astype(np.float32) + rng.normal(0, 10, im.shape)
    t = rng.uniform(105, 165)
    im = np.where(im < t, 0, 255).astype(np.uint8)
    sp = rng.random(im.shape)
    im[sp < 0.0004] = 0
    im[(sp > 0.9995) & (im == 0)] = 255
    out["bilevel300"] = (im, M, 1.0, ang)
    # copy200
    rng = np.random.default_rng(seed + 3)
    ang = float(rng.uniform(-0.4, 0.4))
    im, M = rot(img0, ang)
    s = 2 / 3
    im = cv2.erode(im, np.ones((2, 2), np.uint8)) if rng.random() < 0.6 else im
    im = cv2.resize(im, (int(W0 * s), int(H0 * s)), interpolation=cv2.INTER_AREA).astype(np.float32)
    h, w = im.shape
    im = 245 - (255 - im) * 1.1
    gutter = np.ones((h, w), np.float32)
    side = rng.integers(0, 2); gw = int(w * rng.uniform(0.03, 0.07))
    ramp = np.linspace(0.55, 1.0, gw)[None, :]
    if side == 0: gutter[:, :gw] = ramp
    else: gutter[:, -gw:] = ramp[:, ::-1]
    im *= gutter
    im += rng.normal(0, 9, im.shape)
    tn = rng.random(im.shape) < 0.0015
    im[tn] = rng.uniform(40, 140, tn.sum())
    im = cv2.GaussianBlur(np.clip(im, 0, 255).astype(np.uint8), (0, 0), 0.6)
    out["copy200"] = (im, M, s, ang)
    # phone150
    rng = np.random.default_rng(seed + 4)
    ang = float(rng.uniform(-0.4, 0.4))
    im, M = rot(img0, ang)
    s = 0.5
    im = cv2.GaussianBlur(im, (0, 0), 1.0)
    im = cv2.resize(im, (int(W0 * s), int(H0 * s)), interpolation=cv2.INTER_AREA).astype(np.float32)
    h, w = im.shape
    im = rng.uniform(200, 235) - (255 - im) * rng.uniform(0.65, 0.85)
    im *= illum(h, w, rng, 0.25)
    im += rng.normal(0, 5, im.shape)
    im = jpeg(np.clip(im, 0, 255).astype(np.uint8), 55)
    out["phone150"] = (im, M, s, ang)
    for name, (im, M, s, ang) in out.items():
        d = os.path.join(root, name); os.makedirs(d, exist_ok=True)
        cv2.imwrite(os.path.join(d, base + ".png"), im)
        g = tf_gt(gt, M, s, im.shape[1], im.shape[0], name, ang)
        json.dump(g, open(os.path.join(d, base + ".gt.json"), "w"), ensure_ascii=False, indent=1)
    print(base)

if __name__ == "__main__":
    main()
