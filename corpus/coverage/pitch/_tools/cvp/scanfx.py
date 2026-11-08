"""Scan / photocopy / phone-photo damage for the pitch challenge items.

Derived from corpus/synthetic/_tools/synth/degrade.py (copied, then extended to RGB,
explicit op pipelines and more damage kinds).  numpy + Pillow only.

A damage spec is an ordered list of ops, each a dict {'op': name, ...params}.  Ops may
carry 'pages': [i, ...] to act on some pages only.  Length parameters ending in _mm are
physical (converted with the render dpi); *_px300 are pixels at 300 dpi (scaled).
The pipeline starts from grey LilyPond renders (white paper, black ink) and keeps an RGB
float image (0..255) per page until an output op ('gray', 'binarize').
"""
from __future__ import annotations

import io
import math
import os
import subprocess
import tempfile
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None
FONT_DIR = '/usr/share/texmf/fonts/opentype/public/tex-gyre/'


# ----------------------------------------------------------------- helpers

def mm(v, dpi):
    return v * dpi / 25.4


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def to_pil(a):
    a = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(a, mode='RGB' if a.ndim == 3 else 'L')


def from_pil(im):
    return np.asarray(im, dtype=np.float32)


def remap(img, xs, ys, fill):
    """bilinear remap of HxWxC float image; xs/ys = source coords per dest pixel"""
    h, w = img.shape[:2]
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = (xs - x0).astype(np.float32)[..., None]
    fy = (ys - y0).astype(np.float32)[..., None]
    valid = ((x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1))[..., None]
    x0c = np.clip(x0, 0, w - 2)
    y0c = np.clip(y0, 0, h - 2)
    a = img[y0c, x0c]
    b = img[y0c, x0c + 1]
    c = img[y0c + 1, x0c]
    d = img[y0c + 1, x0c + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(valid, out, np.array(fill, np.float32)).astype(np.float32)


def perspective_coeffs(src, dst):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)).tolist()


def rgb(v):
    return np.array(v, np.float32).reshape(1, 1, 3)


# ----------------------------------------------------------------- anchors (note heads)

def find_anchors(color_png_path, dpi, staff_space_px):
    """Note-head centres from the instrumented render (heads coloured by category:
    red = sharp w/o printed accidental, blue = flat w/o printed accidental,
    green = natural w/o printed accidental, magenta = has printed accidental)."""
    a = np.asarray(Image.open(color_png_path).convert('RGB'), dtype=np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    masks = {
        'sharp': (R > 160) & (G < 100) & (B < 100),
        'flat': (B > 160) & (R < 100) & (G < 100),
        'natural': (G > 120) & (R < 100) & (B < 100),
        'acc': (R > 160) & (B > 160) & (G < 100),
    }
    blk = max(2, int(round(staff_space_px / 5)))
    out = []
    for kind, m in masks.items():
        h, w = m.shape
        H, W = h // blk, w // blk
        small = m[:H * blk, :W * blk].reshape(H, blk, W, blk).sum(axis=(1, 3))
        cells = small > (blk * blk * 0.25)
        seen = np.zeros_like(cells)
        ys, xs = np.nonzero(cells)
        for y0, x0 in zip(ys, xs):
            if seen[y0, x0]:
                continue
            q = deque([(y0, x0)])
            seen[y0, x0] = True
            pts = []
            while q:
                y, x = q.popleft()
                pts.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and cells[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True
                            q.append((yy, xx))
            arr = np.array(pts)
            hgt = (arr[:, 0].max() - arr[:, 0].min() + 1) * blk
            wid = (arr[:, 1].max() - arr[:, 1].min() + 1) * blk
            if hgt > 2.2 * staff_space_px or wid > 2.6 * staff_space_px:   # chord cluster: still usable
                pass
            if hgt < 0.4 * staff_space_px:
                continue
            out.append({'x': float((arr[:, 1].mean() + 0.5) * blk), 'y': float((arr[:, 0].mean() + 0.5) * blk),
                        'kind': kind, 'w': float(wid), 'h': float(hgt)})
    return out


def staff_extent(gray, dpi):
    """leftmost / rightmost x where long horizontal staff lines exist (clean render)"""
    dark = gray < 128
    rows = dark.sum(axis=1)
    w = gray.shape[1]
    line_rows = np.nonzero(rows > 0.5 * w * 0.6)[0]
    if len(line_rows) == 0:
        return None
    sub = dark[line_rows]
    cols = sub.sum(axis=0) > 0.6 * len(line_rows)
    xs = np.nonzero(cols)[0]
    return int(xs.min()), int(xs.max())


# ----------------------------------------------------------------- pencil

def _jit(rng, s):
    return rng.normal(0, s)


def _stroke(draw, pts, width, fill):
    draw.line([(float(x), float(y)) for x, y in pts], fill=fill, width=max(1, int(round(width))), joint='curve')


def draw_pencil(img, P, rng, dpi, anchors, ss):
    h, w = img.shape[:2]
    layer = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(layer)
    lw = mm(P.get('width_mm', 0.28), dpi)
    used = []
    log = []

    def pick(kinds, n):
        cand = [a for a in anchors if a['kind'] in kinds and a not in used]
        rng.shuffle(cand)
        res = []
        for a in cand:
            if len(res) >= n:
                break
            if any(abs(a['x'] - b['x']) < 6 * ss and abs(a['y'] - b['y']) < 6 * ss for b in used + res):
                continue
            res.append(a)
        used.extend(res)
        return res

    for a in pick(('sharp', 'flat', 'natural', 'acc'), P.get('circles', 0)):
        rx, ry = 1.5 * ss * rng.uniform(0.9, 1.3), 1.25 * ss * rng.uniform(0.9, 1.3)
        t0 = rng.uniform(0, 2 * math.pi)
        pts = []
        for k in range(42):
            t = t0 + 2 * math.pi * 1.12 * k / 41
            rr = 1 + 0.06 * math.sin(3 * t) + _jit(rng, 0.015)
            pts.append((a['x'] + rx * rr * math.cos(t), a['y'] + ry * rr * math.sin(t)))
        _stroke(d, pts, lw, 255)
        log.append({'mark': 'circle', 'x': round(a['x']), 'y': round(a['y'])})
    # reminder accidentals that AGREE with the printed pitch (performer's pencil reminders)
    for a in pick(('sharp', 'flat'), P.get('reminders', 0)):
        x0 = a['x'] - 2.1 * ss
        y0 = a['y']
        if a['kind'] == 'sharp':
            for dx in (-0.35, 0.35):
                _stroke(d, [(x0 + dx * ss + _jit(rng, 0.05 * ss), y0 - 1.3 * ss),
                            (x0 + dx * ss + _jit(rng, 0.05 * ss), y0 + 1.3 * ss)], lw, 255)
            for dy in (-0.45, 0.45):
                _stroke(d, [(x0 - 0.75 * ss, y0 + dy * ss + 0.2 * ss), (x0 + 0.75 * ss, y0 + dy * ss - 0.2 * ss)],
                        lw * 1.3, 255)
        else:
            _stroke(d, [(x0 - 0.3 * ss, y0 - 1.6 * ss), (x0 - 0.3 * ss, y0 + 0.5 * ss)], lw, 255)
            pts = [(x0 - 0.3 * ss + 0.9 * ss * math.sin(math.pi * k / 10),
                    y0 + 0.5 * ss - 0.9 * ss * (k / 10) - 0.15 * ss * math.sin(math.pi * k / 10)) for k in range(11)]
            pts = [(x0 - 0.3 * ss, y0 - 0.3 * ss)] + pts[::-1]
            _stroke(d, pts, lw, 255)
        log.append({'mark': 'reminder_' + a['kind'], 'x': round(a['x']), 'y': round(a['y'])})
    # fingering digits / words
    texts = P.get('texts', [])
    nfing = P.get('fingerings', 0)
    if texts or nfing:
        fpath = os.path.join(FONT_DIR, 'texgyrechorus-mediumitalic.otf')
        size = int(2.6 * ss)
        try:
            font = ImageFont.truetype(fpath, size)
        except OSError:
            font = ImageFont.load_default()
        for a in pick(('sharp', 'flat', 'natural', 'acc'), nfing):
            txt = str(int(rng.integers(1, 5)))
            d.text((a['x'] - 0.4 * ss, a['y'] - 5.2 * ss), txt, fill=255, font=font)
            log.append({'mark': 'digit', 'text': txt, 'x': round(a['x']), 'y': round(a['y'])})
        for txt in texts:
            cand = pick(('sharp', 'flat', 'natural', 'acc'), 1)
            if not cand:
                continue
            a = cand[0]
            d.text((a['x'] - 1.5 * ss, a['y'] - 6.5 * ss), txt, fill=255, font=font)
            log.append({'mark': 'text', 'text': txt, 'x': round(a['x']), 'y': round(a['y'])})
    for _ in range(P.get('breath_marks', 0)):
        cand = pick(('sharp', 'flat', 'natural', 'acc'), 1)
        if not cand:
            break
        a = cand[0]
        x0, y0 = a['x'] + 2.2 * ss, a['y'] - 4.5 * ss
        _stroke(d, [(x0 - 0.5 * ss, y0 - 0.8 * ss), (x0, y0 + 0.6 * ss), (x0 + 0.6 * ss, y0 - 0.9 * ss)], lw, 255)
        log.append({'mark': 'breath', 'x': round(x0), 'y': round(y0)})
    al = np.asarray(layer, np.float32) / 255.0
    grain = 0.55 + 0.45 * rng.random(al.shape).astype(np.float32)
    al = al * grain * P.get('alpha', 0.7)
    al = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.35 * dpi / 300)),
                    np.float32)[..., None] / 255.0
    col = rgb(P.get('rgb', [78, 78, 86]))
    return img * (1 - al) + np.minimum(img, col) * al, log


# ----------------------------------------------------------------- ops

def op_paper(cov, P, rng, dpi, others):
    h, w = cov.shape
    if P.get('bleed'):
        src = others.get('bleed_src', cov)
        mir = src[:, ::-1]
        if mir.shape != cov.shape:
            mir = np.asarray(Image.fromarray((mir * 255).astype(np.uint8)).resize((w, h)), np.float32) / 255
        mpil = Image.fromarray((mir * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(P.get('bleed_blur_px300', 2.5) * dpi / 300))
        shift = int(rng.integers(-25, 25) * dpi / 300)
        bleed = np.roll(np.asarray(mpil, np.float32) / 255.0, shift, axis=0) * P['bleed']
    else:
        bleed = 0
    paper = rgb(P.get('rgb', [246, 246, 244]))
    tex = P.get('texture', 0)
    paper_f = np.broadcast_to(paper, (h, w, 3)).copy()
    if tex:
        f = tex * smooth_field((h, w), rng, (14, 10)) + tex * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        paper_f += f[..., None]
    if P.get('fibers'):
        fib = smooth_field((h, w), rng, (int(h / 6), int(w / 60) + 2), -1, 1)
        paper_f += (P['fibers'] * fib)[..., None]
    ink = rgb(P.get('ink_rgb', [22, 22, 24]))
    ink_f = np.broadcast_to(ink, (h, w, 3)).copy()
    if P.get('ink_var'):
        ink_f += (P['ink_var'] * smooth_field((h, w), rng, (10, 8), 0, 1))[..., None]
    out = paper_f * (1 - cov[..., None]) + ink_f * cov[..., None]
    if P.get('bleed'):
        bt = rgb(P.get('bleed_rgb', [120, 115, 110]))
        out = out * (1 - bleed[..., None] * (1 - bt / 255.0))
    return out


def op_stain(img, P, rng, dpi):
    h, w = img.shape[:2]
    cx, cy = P['cx'] * w, P['cy'] * h
    r = P['r'] * w
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = np.arctan2(yy - cy, xx - cx)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    wob = 1 + 0.07 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.04 * np.sin(7 * ang + rng.uniform(0, 6))
    rn = rr / (r * wob)
    ringw = P.get('ring_width', 0.06)
    ring = np.exp(-((rn - 1) / ringw) ** 2)
    inner = np.clip(1 - rn, 0, 1) ** 0.3 * (rn < 1)
    dens = P.get('strength', 0.35) * (ring + P.get('fill', 0.25) * inner)
    dens *= (0.75 + 0.25 * smooth_field((h, w), rng, (9, 7), 0, 1))
    tint = rgb(P.get('rgb', [150, 100, 55])) / 255.0
    dens = dens[..., None]
    return img * (1 - dens * (1 - tint))


def op_foxing(img, P, rng, dpi):
    h, w = img.shape[:2]
    n = P.get('n', 40)
    tint = rgb(P.get('rgb', [170, 120, 70])) / 255.0
    acc = np.zeros((h, w), np.float32)
    for _ in range(n):
        r = mm(rng.uniform(P.get('rmin_mm', 0.4), P.get('rmax_mm', 2.5)), dpi)
        cx, cy = rng.uniform(0, w), rng.uniform(0, h)
        x0, x1 = int(max(0, cx - 3 * r)), int(min(w, cx + 3 * r))
        y0, y1 = int(max(0, cy - 3 * r)), int(min(h, cy + 3 * r))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)
        acc[y0:y1, x0:x1] = np.maximum(acc[y0:y1, x0:x1], np.exp(-d2) * rng.uniform(0.4, 1.0))
    dens = (P.get('strength', 0.4) * acc)[..., None]
    return img * (1 - dens * (1 - tint))


def op_holes(img, P, rng, dpi):
    h, w = img.shape[:2]
    n = P.get('n', 2)
    rr = mm(P.get('d_mm', 6.0), dpi) / 2
    off = mm(P.get('offset_mm', 11.0), dpi)
    fill = rgb(P.get('fill', [35, 35, 38]))
    side = P.get('side', 'left')
    spacing = mm(P.get('spacing_mm', 80.0), dpi)
    ys = [h / 2 + (k - (n - 1) / 2) * spacing for k in range(n)]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = img.copy()
    for yc in ys:
        xc = off if side == 'left' else w - off
        d = np.sqrt((xx - xc) ** 2 + (yy - yc) ** 2)
        shadow = np.clip(1 - (d - rr) / (0.25 * rr), 0, 1) * (d >= rr) * 0.35
        out = out * (1 - shadow[..., None])
        m = (d < rr)[..., None]
        out = np.where(m, fill + rng.normal(0, 4, (h, w, 1)).astype(np.float32), out)
    return out


def op_staple(img, P, rng, dpi):
    h, w = img.shape[:2]
    L = mm(P.get('len_mm', 12), dpi)
    ang = math.radians(P.get('angle', -35))
    x0, y0 = mm(P.get('x_mm', 14), dpi), mm(P.get('y_mm', 12), dpi)
    if P.get('corner', 'tl') == 'tr':
        x0 = w - x0
    x1, y1 = x0 + L * math.cos(ang), y0 + L * math.sin(ang)
    lay = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(lay)
    lw = max(2, int(mm(0.7, dpi)))
    d.line([(x0 + lw, y0 + lw), (x1 + lw, y1 + lw)], fill=90, width=lw + 2)      # shadow
    sh = np.asarray(lay.filter(ImageFilter.GaussianBlur(lw)), np.float32)[..., None] / 255
    out = img * (1 - 0.6 * sh)
    lay2 = Image.new('L', (w, h), 0)
    d2 = ImageDraw.Draw(lay2)
    d2.line([(x0, y0), (x1, y1)], fill=255, width=lw)
    for (xa, ya) in ((x0, y0), (x1, y1)):
        d2.ellipse([xa - lw, ya - lw, xa + lw, ya + lw], fill=255)
    m = np.asarray(lay2, np.float32)[..., None] / 255
    metal = rgb([150, 152, 158]) + 40 * smooth_field((h, w), rng, (30, 30), -1, 1)[..., None]
    return out * (1 - m) + metal * m


def op_crop(img, P, rng, dpi, ctx, ext):
    """cut the page edges; *_into_mm measure from the outermost staff-line ends inwards
    (positive = into the staff), *_mm from the paper edge"""
    h, w = img.shape[:2]
    L = R = 0
    if 'left_into_mm' in P and ext:
        L = int(ext[0] + mm(P['left_into_mm'], dpi))
    elif 'left_mm' in P:
        L = int(mm(P['left_mm'], dpi))
    if 'right_into_mm' in P and ext:
        R = int(w - 1 - ext[1] + mm(P['right_into_mm'], dpi))
    elif 'right_mm' in P:
        R = int(mm(P['right_mm'], dpi))
    L, R = max(0, L), max(0, R)
    T = int(mm(P.get('top_mm', 0), dpi))
    B = int(mm(P.get('bottom_mm', 0), dpi))
    ctx.setdefault('crop_px', []).append([L, R, T, B])
    return img[T:h - B if B else h, L:w - R if R else w].copy()


def op_curl(img, P, rng, dpi, fill):
    h, w = img.shape[:2]
    sc = dpi / 300
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    amp = P['amp'] * sc
    width = P.get('width', 0.25) * w
    side = P.get('side', 'left')
    if side == 'left':
        t = np.clip((width - xx) / width, 0, 1)
    else:
        t = np.clip((xx - (w - width)) / width, 0, 1)
    dy = amp * t ** 2 * ((yy - h / 2) / (h / 2))
    dx = (amp * 0.6) * t ** 2 * (1 if side == 'left' else -1)
    if P.get('wave'):
        dy += P['wave'] * sc * np.sin(2 * np.pi * xx / (1.3 * w) + 0.3)
    return remap(img, xx - dx, yy - dy, fill)


def op_rotate(img, P, rng, dpi, fill):
    im = to_pil(img)
    im = im.rotate(P['deg'], resample=Image.BICUBIC, fillcolor=tuple(int(v) for v in fill),
                   expand=P.get('expand', False))
    return from_pil(im)


def op_scale(img, P, rng, dpi, fill):
    h, w = img.shape[:2]
    f = P['factor']
    im = to_pil(img).resize((max(1, int(w * f)), max(1, int(h * f))), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), tuple(int(v) for v in fill))
    canvas.paste(im, ((w - im.size[0]) // 2 + int(P.get('dx_px', 0)), (h - im.size[1]) // 2 + int(P.get('dy_px', 0))))
    return from_pil(canvas)


def op_lighting(img, P, rng, dpi):
    h, w = img.shape[:2]
    out = img
    if P.get('gradient'):
        ang = P.get('angle', rng.uniform(0, 360))
        a = math.radians(ang)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        t = ((xx / w - 0.5) * math.cos(a) + (yy / h - 0.5) * math.sin(a)) + 0.5
        out = out * (1 - P['gradient'] * np.clip(t, 0, 1))[..., None]
    if P.get('vignette'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx / w - 0.5)) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
        out = out * (1 - P['vignette'] * r ** 2)[..., None]
    if P.get('blotch'):
        out = out * (1 - P['blotch'] * np.clip(smooth_field((h, w), rng, (5, 4), -0.5, 1), 0, 1))[..., None]
    if P.get('warm'):
        out = out * rgb([1.0, 1.0 - 0.5 * P['warm'], 1.0 - P['warm']])
    return out


def op_gutter(img, P, rng, dpi):
    h, w = img.shape[:2]
    gw = int(P.get('width', 0.06) * w)
    prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * P.get('dark', 0.55)
    out = img.copy()
    if P.get('side', 'left') == 'left':
        out[:, :gw] *= (1 - prof)[None, :, None]
    else:
        out[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
    return out


def op_phone(img, P, rng, dpi):
    h, w = img.shape[:2]
    m = int(P.get('margin', 0.05) * w)
    bg = rgb(P.get('bg', [70, 64, 58]))
    H, W = h + 2 * m, w + 2 * m
    canvas = np.broadcast_to(bg, (H, W, 3)).copy() + (12 * smooth_field((H, W), rng, (4, 4)))[..., None]
    canvas[m:m + h, m:m + w] = img
    jit = P.get('jitter', 0.03)
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    if P.get('corners'):
        src = [(x + cx * W, y + cy * H) for (x, y), (cx, cy) in zip(dst, P['corners'])]
    else:
        src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in dst]
    coeffs = perspective_coeffs(src, dst)
    im = to_pil(canvas).transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC,
                                  fillcolor=tuple(int(v) for v in bg.ravel()))
    return from_pil(im)


def op_blur(img, P, rng, dpi):
    sc = dpi / 300
    out = img
    if P.get('radius_px300'):
        out = from_pil(to_pil(out).filter(ImageFilter.GaussianBlur(P['radius_px300'] * sc)))
    if P.get('motion_px300'):
        L = max(1, int(round(P['motion_px300'] * sc)))
        a = math.radians(P.get('angle', 0))
        acc = np.zeros_like(out)
        for k in range(L):
            t = k - (L - 1) / 2
            dx, dy = int(round(t * math.cos(a))), int(round(t * math.sin(a)))
            acc += np.roll(np.roll(out, dy, axis=0), dx, axis=1)
        out = acc / L
    return out


def op_halftone(img, P, rng, dpi):
    """re-screen the page as a halftone (printed reproduction) and resample -> moire"""
    h, w = img.shape[:2]
    over = P.get('oversample', 2)
    gray = (img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114)
    big = np.asarray(Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8)).resize((w * over, h * over),
                                                                                     Image.BILINEAR), np.float32)
    H, W = big.shape
    period = (dpi * over) / P.get('lpi', 85)
    a = math.radians(P.get('angle', 45))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xx * math.cos(a) + yy * math.sin(a)) * 2 * math.pi / period
    v = (-xx * math.sin(a) + yy * math.cos(a)) * 2 * math.pi / period
    screen = (np.cos(u) * np.cos(v) + 1) / 2          # 0..1
    del xx, yy, u, v
    cov = 1 - big / 255.0
    dots = (cov > screen).astype(np.float32)
    small = np.asarray(Image.fromarray((255 * (1 - dots)).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                       np.float32)
    mix = P.get('mix', 1.0)
    g2 = gray * (1 - mix) + small * mix
    ratio = (g2 + 1) / (gray + 1)
    return np.clip(img * ratio[..., None], 0, 255)


def op_noise(img, P, rng, dpi):
    out = img
    h, w = img.shape[:2]
    if P.get('sigma'):
        n = rng.normal(0, P['sigma'], (h, w, 1)).astype(np.float32)
        if P.get('chroma'):
            n = n + rng.normal(0, P['chroma'], (h, w, 3)).astype(np.float32)
        out = out + n
    if P.get('saltpepper'):
        k = int(P['saltpepper'] * h * w)
        ys = rng.integers(0, h, k)
        xs = rng.integers(0, w, k)
        vals = np.where(rng.random(k) < 0.55, 15.0, 250.0).astype(np.float32)
        out = out.copy()
        out[ys, xs] = vals[:, None]
    if P.get('speckle'):
        out = out.copy()
        n = int(P['speckle'] * (w * h) / 1e6)
        sc = dpi / 300
        for _ in range(n):
            r = rng.uniform(0.6, 2.2) * sc
            cy, cx = rng.integers(0, h), rng.integers(0, w)
            y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
            x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
            out[y0:y1, x0:x1][mask] = 25 + rng.uniform(0, 60)
    return out


def op_ink(gray, P, rng, dpi):
    """morphological ink weight on the grey render (before compose); +n thicker, -n thinner"""
    pil = Image.fromarray(gray.astype(np.uint8))
    k = P.get('weight', 0)
    for _ in range(abs(k)):
        pil = pil.filter(ImageFilter.MinFilter(3) if k > 0 else ImageFilter.MaxFilter(3))
    g = np.asarray(pil, np.float32)
    if P.get('dropout'):
        f = smooth_field(g.shape, rng, (40, 30), 0, 1)
        fine = rng.random(g.shape).astype(np.float32)
        drop = (f > 1 - P['dropout']) & (fine < 0.5)
        g = np.where(drop & (g < 200), g + (255 - g) * 0.6, g)
    return g


def spread2up(pages, P, rng, dpi):
    """two pages side by side as an open book: inner-edge curl + gutter shadow"""
    out = []
    for k in range(0, len(pages), 2):
        pair = pages[k:k + 2]
        if len(pair) == 1:
            out.append(pair[0])
            continue
        a, b = pair
        fill = rgb(P.get('bg', [40, 38, 36])).ravel()
        if P.get('curl_amp'):
            a = op_curl(a, {'side': 'right', 'amp': P['curl_amp'], 'width': P.get('curl_width', 0.2)}, rng, dpi, fill)
            b = op_curl(b, {'side': 'left', 'amp': P['curl_amp'], 'width': P.get('curl_width', 0.2)}, rng, dpi, fill)
        a = op_gutter(a, {'side': 'right', 'width': P.get('gutter_width', 0.07), 'dark': P.get('gutter_dark', 0.5)},
                      rng, dpi)
        b = op_gutter(b, {'side': 'left', 'width': P.get('gutter_width', 0.07), 'dark': P.get('gutter_dark', 0.5)},
                      rng, dpi)
        h = max(a.shape[0], b.shape[0])
        gap = int(mm(P.get('gap_mm', 0), dpi))
        m = int(mm(P.get('margin_mm', 6), dpi))
        W = a.shape[1] + b.shape[1] + gap + 2 * m
        H = h + 2 * m
        canvas = np.broadcast_to(rgb(P.get('bg', [40, 38, 36])), (H, W, 3)).copy()
        dy = int(mm(P.get('offset_mm', 0), dpi))
        canvas[m:m + a.shape[0], m:m + a.shape[1]] = a
        yb = min(max(0, m + dy), H - b.shape[0])
        canvas[yb:yb + b.shape[0], m + a.shape[1] + gap:m + a.shape[1] + gap + b.shape[1]] = b
        out.append(canvas)
    return out


# ----------------------------------------------------------------- pipeline

def run_pipeline(grays, spec, dpi, seed, ctx):
    """grays: list of uint8 grey page renders.  Returns (list of PIL images, mode, log)."""
    rng = np.random.default_rng(seed)
    ops = spec['ops']
    log = {'pencil': [], 'crop_px': None}
    pages = [g.astype(np.float32) for g in grays]
    nP = len(pages)
    lid = rgb(spec.get('lid_rgb', [238, 238, 236])).ravel()
    stage = 'gray'
    mode = 'RGB'

    def sel(P):
        return P.get('pages', list(range(len(pages))))

    for P in ops:
        op = P['op']
        if op == 'ink':
            pages = [op_ink(g, P, rng, dpi) if i in sel(P) else g for i, g in enumerate(pages)]
            continue
        if stage == 'gray':
            if op != 'paper':
                pages = [op_paper(1 - g / 255.0, {}, rng, dpi, {}) for g in pages]
            else:
                covs = [1 - g / 255.0 for g in pages]
                new = []
                for i, c in enumerate(covs):
                    others = {}
                    if P.get('bleed_from') == 'next' and nP > 1:
                        others['bleed_src'] = covs[(i + 1) % nP]
                    new.append(op_paper(c, P, rng, dpi, others))
                pages = new
                stage = 'rgb'
                continue
            stage = 'rgb'
        if op == 'stain':
            pages = [op_stain(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'foxing':
            pages = [op_foxing(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'pencil':
            new = []
            for i, p in enumerate(pages):
                if i in sel(P):
                    p, lg = draw_pencil(p, P, rng, dpi, ctx['anchors'][i], ctx['staff_space_px'])
                    log['pencil'].append({'page': i, 'marks': lg})
                new.append(p)
            pages = new
        elif op == 'holes':
            pages = [op_holes(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'staple':
            pages = [op_staple(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'crop':
            pages = [op_crop(p, P, rng, dpi, ctx, ctx['staff_extent'][i]) if i in sel(P) else p
                     for i, p in enumerate(pages)]
            log['crop_px'] = ctx.get('crop_px')
        elif op == 'curl':
            pages = [op_curl(p, P, rng, dpi, P.get('fill', lid)) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'rotate':
            pages = [op_rotate(p, {'deg': P['deg'][i] if isinstance(P['deg'], list) else P['deg'],
                                   'expand': P.get('expand', False)}, rng, dpi, P.get('fill', lid))
                     if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'scale':
            pages = [op_scale(p, P, rng, dpi, P.get('fill', lid)) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'lighting':
            pages = [op_lighting(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'gutter':
            pages = [op_gutter(p, P, rng, dpi) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'spread2up':
            pages = spread2up(pages, P, rng, dpi)
        elif op == 'phone':
            pages = [op_phone(p, P, rng, dpi) for p in pages]
        elif op == 'blur':
            pages = [op_blur(p, P, rng, dpi) for p in pages]
        elif op == 'halftone':
            pages = [op_halftone(p, P, rng, dpi) for p in pages]
        elif op == 'noise':
            pages = [op_noise(p, P, rng, dpi) for p in pages]
        elif op == 'rot90':
            pages = [np.ascontiguousarray(np.rot90(p, P['k'])) if i in sel(P) else p for i, p in enumerate(pages)]
        elif op == 'gray':
            mode = 'L'
        elif op == 'binarize':
            mode = '1'
        else:
            raise ValueError(f'unknown op {op}')
    # output conversion
    outs = []
    for p in pages:
        p = np.clip(p, 0, 255)
        if mode == 'RGB':
            outs.append(to_pil(p))
            continue
        g = p[..., 0] * 0.299 + p[..., 1] * 0.587 + p[..., 2] * 0.114
        if mode == 'L':
            outs.append(Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), 'L'))
            continue
        B = next(o for o in ops if o['op'] == 'binarize')
        if B.get('pre_blur_px300'):
            g = from_pil(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.GaussianBlur(B['pre_blur_px300'] * dpi / 300)))
        if B.get('noise'):
            g = g + rng.normal(0, B['noise'], g.shape).astype(np.float32)
        bil = g > B['threshold']
        im = Image.fromarray((bil * 255).astype(np.uint8)).convert('1', dither=Image.NONE)
        outs.append(im)
    return outs, mode, log


def save_pdf(images, dpi, out_pdf, fmt='jpeg', quality=75, passes=1):
    """image-only PDF via img2pdf (JPEG for RGB/grey, PNG for 1-bit / lossless)"""
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if fmt == 'jpeg' and im.mode != '1':
                cur = im
                for _ in range(passes - 1):
                    b2 = io.BytesIO()
                    cur.save(b2, 'JPEG', quality=min(95, quality + 15))
                    b2.seek(0)
                    cur = Image.open(b2).convert(im.mode)
                fn = os.path.join(td, f'p{k:03d}.jpg')
                cur.save(fn, 'JPEG', quality=quality, dpi=(dpi, dpi), optimize=True)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{dpi}dpi', '-o', out_pdf] + files, check=True,
                       capture_output=True, timeout=600)
