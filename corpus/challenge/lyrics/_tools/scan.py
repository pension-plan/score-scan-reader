"""Scan / photocopy / phone-capture damage for the lyrics challenge set.

numpy + Pillow only, RGB capable.  A damage *recipe* is a plain dict that is
recorded verbatim (with its seed) in meta.json, so every scan can be rebuilt
bit-for-bit:

  {'dpi': 300, 'seed': 1234, 'mode': 'gray'|'rgb'|'bw', 'jpeg': 45 | None,
   'page_ops': [{'op': 'page_scale', 'factors': [1, .97]}, {'op': 'spread', ...}],
   'ops': [{'op': 'paper', ...}, {'op': 'rotate', 'deg': 1.2}, ...]}

Ops run in list order on a float32 RGB image (255 = white paper, 0 = ink).
Physical sizes are given in mm (converted with dpi) or, for blur/noise
style ops, in pixels at 300 dpi (scaled with dpi/300).
"""
from __future__ import annotations

import io
import math
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None

HAND_FONT = '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrechorus-mediumitalic.otf'


# ----------------------------------------------------------------- helpers
def mm(x, dpi):
    return x * dpi / 25.4


def lum(img):
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def to_pil(img):
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')


def from_pil(pil):
    return np.asarray(pil.convert('RGB'), dtype=np.float32)


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def remap_rgb(img, xs, ys, fill):
    h, w = img.shape[:2]
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
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


def blend_color(img, mask, color, alpha=1.0):
    """img (H,W,3); mask (H,W) 0..1 coverage of a pigment with RGB colour"""
    m = (np.clip(mask, 0, 1) * alpha)[..., None]
    col = np.array(color, np.float32)
    # subtractive-ish: pigment darkens towards its colour (multiply), keeps highlights
    return img * (1 - m) + np.minimum(img, col) * m


def staves(L, dpi):
    """detect 5-line staves on a luminance page: list of (top, bottom, spacing)"""
    dark = L < 140
    rows = dark.mean(axis=1)
    cand = np.where(rows > 0.30)[0]
    lines = []
    for r in cand:
        if lines and r - lines[-1][-1] <= 1:
            lines[-1].append(r)
        else:
            lines.append([r])
    ys = [float(np.mean(l)) for l in lines]
    out = []
    i = 0
    while i + 4 < len(ys):
        gaps = np.diff(ys[i:i + 5])
        if gaps.max() < 1.35 * gaps.min() and gaps.min() > mm(0.9, dpi) and gaps.max() < mm(3.5, dpi):
            out.append((ys[i], ys[i + 4], float(gaps.mean())))
            i += 5
        else:
            i += 1
    return out


# ----------------------------------------------------------------- ops
def op_ink(img, p, rng, dpi):
    """thicken (weight>0) or thin (weight<0) the printed ink"""
    pil = to_pil(img).convert('L')
    for _ in range(abs(p['weight'])):
        pil = pil.filter(ImageFilter.MinFilter(3) if p['weight'] > 0 else ImageFilter.MaxFilter(3))
    g = np.asarray(pil, np.float32)
    return np.repeat(g[..., None], 3, axis=2)


def op_dropout(img, p, rng, dpi):
    L = lum(img)
    f = smooth_field(L.shape, rng, (40, 30), 0, 1)
    fine = rng.random(L.shape).astype(np.float32)
    drop = (f > 1 - p['amount']) & (fine < 0.55) & (L < 200)
    L = np.where(drop, L + (255 - L) * 0.65, L)
    return np.repeat(L[..., None], 3, axis=2)


def op_halftone(img, p, rng, dpi):
    """AM halftone screen (printed tint + dotted edges); moire appears when
    the page is later resampled ('resample' op) or simply from the screen
    beating against the staff lines."""
    L = lum(img)
    C = 1 - L / 255.0
    C = np.clip(C + p.get('tint', 0.1) * (1 - C), 0, 1)
    h, w = L.shape
    per = dpi / p.get('lpi', 85)
    a = math.radians(p.get('angle', 45))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = xx * math.cos(a) + yy * math.sin(a)
    v = -xx * math.sin(a) + yy * math.cos(a)
    scr = 0.5 + 0.25 * (np.cos(2 * np.pi * u / per) + np.cos(2 * np.pi * v / per))
    del xx, yy, u, v
    dots = (C > scr).astype(np.float32)
    s = p.get('strength', 1.0)
    C2 = C * (1 - s) + dots * s
    g = Image.fromarray((255 * (1 - C2)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6 * dpi / 300))
    g = np.asarray(g, np.float32)
    return np.repeat(g[..., None], 3, axis=2)


def op_paper(img, p, rng, dpi):
    """composite the ink onto (coloured, textured) paper"""
    L = lum(img)
    C = 1 - L / 255.0
    h, w = L.shape
    col = np.array(p.get('color', [245, 244, 240]), np.float32)
    tex = p.get('texture', 0)
    field = np.zeros((h, w), np.float32)
    if tex:
        field += tex * smooth_field((h, w), rng, (14, 10))
        field += tex * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        if p.get('fibers'):
            # faint horizontal/vertical fibres
            fib = rng.normal(0, 1, (h // 8 + 1, w // 64 + 1)).astype(np.float32)
            fib = np.asarray(Image.fromarray(fib, 'F').resize((w, h), Image.BILINEAR), np.float32)
            field += tex * 0.6 * fib
    paper = col[None, None, :] + field[..., None]
    ink = np.array(p.get('ink', [22, 22, 26]), np.float32)
    ink_f = ink[None, None, :] + p.get('ink_var', 0) * smooth_field((h, w), rng, (10, 8), 0, 1)[..., None]
    return paper * (1 - C[..., None]) + ink_f * C[..., None]


def op_bleed(img, p, rng, dpi, pages=None, index=0):
    """reverse-side print showing through: mirrored page content, blurred"""
    src = p.get('source', 'mirror')
    if src == 'other' and pages is not None and len(pages) > 1:
        other = pages[(index + 1) % len(pages)]
    else:
        other = pages[index] if pages is not None else None
    Lo = other.astype(np.float32) if other is not None else lum(img)
    if Lo.shape != img.shape[:2]:
        Lo = np.asarray(Image.fromarray(Lo.astype(np.uint8)).resize((img.shape[1], img.shape[0])), np.float32)
    M = 1 - Lo[:, ::-1] / 255.0
    sh = p.get('shift_mm', [3, -5])
    M = np.roll(M, (int(mm(sh[1], dpi)), int(mm(sh[0], dpi))), axis=(0, 1))
    M = np.asarray(Image.fromarray((M * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(p.get('blur', 2.0) * dpi / 300)), np.float32) / 255.0
    return blend_color(img, M, p.get('color', [70, 70, 75]), p['strength'])


def op_stain(img, p, rng, dpi):
    """coffee-cup rings / tea stains: irregular ring + translucent fill"""
    h, w = img.shape[:2]
    out = img
    for k in range(p.get('n', 1)):
        R = mm(rng.uniform(*p.get('radius_mm', [22, 38])), dpi)
        if p.get('where') and k < len(p['where']):
            cx, cy = p['where'][k][0] * w, p['where'][k][1] * h
        else:
            cx, cy = rng.uniform(0.15, 0.85) * w, rng.uniform(0.15, 0.85) * h
        x0, x1 = int(max(0, cx - 1.4 * R)), int(min(w, cx + 1.4 * R))
        y0, y1 = int(max(0, cy - 1.4 * R)), int(min(h, cy + 1.4 * R))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        th = np.arctan2(yy - cy, xx - cx)
        rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        mod = np.ones_like(th)
        for f in range(2, 7):
            mod += rng.uniform(0.01, 0.05) * np.sin(f * th + rng.uniform(0, 6.28))
        rad = R * mod
        ring_w = mm(p.get('ring_mm', 1.6), dpi)
        ring = np.exp(-((rr - rad) / ring_w) ** 2)
        partial = rng.uniform(0.55, 1.0)   # rings are often incomplete
        gap = 0.5 + 0.5 * np.cos(th - rng.uniform(0, 6.28))
        ring *= np.clip(gap * 1.6 - (1 - partial), 0, 1)
        fill = np.clip((rad - rr) / (0.25 * R), 0, 1) * p.get('fill', 0.35)
        mottle = smooth_field(rr.shape, rng, (6, 6), 0.6, 1.0)
        mask = np.clip(ring * 1.0 + fill * mottle, 0, 1)
        out[y0:y1, x0:x1] = blend_color(out[y0:y1, x0:x1], mask, p.get('color', [165, 110, 55]),
                                        p.get('strength', 0.45))
    return out


def op_foxing(img, p, rng, dpi):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.float32)
    n = p.get('n', 60)
    for _ in range(n):
        r = mm(rng.uniform(*p.get('size_mm', [0.4, 2.5])), dpi)
        cx, cy = rng.uniform(0, w), rng.uniform(0, h)
        x0, x1 = int(max(0, cx - 3 * r)), int(min(w, cx + 3 * r + 1))
        y0, y1 = int(max(0, cy - 3 * r)), int(min(h, cy + 3 * r + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], np.exp(-d ** 2) * rng.uniform(0.5, 1))
    return blend_color(img, mask, p.get('color', [170, 115, 65]), p.get('strength', 0.5))


def op_pencil(img, p, rng, dpi):
    """graphite annotations: circled notes, breath ticks, hand-written words,
    wobbly lines/arrows.  Not part of the music truth."""
    h, w = img.shape[:2]
    L = lum(img)
    sts = staves(L, dpi)
    cov = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(cov)
    lw = max(1, int(round(mm(p.get('width_mm', 0.35), dpi))))
    placed = []
    if sts:
        dark = L < 110
        for _ in range(p.get('circles', 0)):
            for _try in range(40):
                top, bot, sp = sts[rng.integers(len(sts))]
                y0, y1 = int(top - 2 * sp), int(bot + 2 * sp)
                xa, xb = int(0.12 * w), int(0.92 * w)
                x = int(rng.integers(xa, xb))
                band = dark[max(0, y0):y1, max(0, x - int(sp)):x + int(sp)]
                rowsum = band.mean(axis=1)
                if band.size == 0 or rowsum.max() < 0.55:
                    continue
                cy = max(0, y0) + int(np.argmax(rowsum))
                rx, ry = sp * rng.uniform(1.4, 2.0), sp * rng.uniform(1.1, 1.6)
                pts = []
                a0 = rng.uniform(0, 6.28)
                for t in np.linspace(0, 2 * np.pi * rng.uniform(1.05, 1.25), 60):
                    jit = 1 + 0.06 * math.sin(3 * t + a0)
                    pts.append((x + rx * jit * math.cos(t + a0), cy + ry * jit * math.sin(t + a0)))
                dr.line(pts, fill=int(255 * rng.uniform(0.75, 1)), width=lw, joint='curve')
                placed.append(('circle', x, cy))
                break
        for _ in range(p.get('ticks', 0)):
            top, bot, sp = sts[rng.integers(len(sts))]
            x = rng.uniform(0.15, 0.95) * w
            y = top - rng.uniform(1.0, 2.2) * sp
            s = sp * rng.uniform(0.8, 1.3)
            dr.line([(x - s * 0.4, y - s), (x, y), (x + s * 0.5, y - s * 1.2)], fill=230, width=lw)
            placed.append(('tick', int(x), int(y)))
    words = p.get('words', [])
    if words:
        fsize = int(mm(p.get('word_mm', 4.2), dpi))
        try:
            font = ImageFont.truetype(HAND_FONT, fsize)
        except OSError:
            font = ImageFont.load_default()
        for wd in words:
            if sts and rng.random() < 0.8:
                top, bot, sp = sts[rng.integers(len(sts))]
                y = top - rng.uniform(2.5, 4.5) * sp
            else:
                y = rng.uniform(0.05, 0.95) * h
            x = rng.uniform(0.1, 0.75) * w
            layer = Image.new('L', (int(fsize * len(wd) * 0.8) + 20, int(fsize * 1.8)), 0)
            ImageDraw.Draw(layer).text((8, 4), wd, fill=230, font=font)
            layer = layer.rotate(rng.uniform(-8, 8), resample=Image.BICUBIC, expand=True)
            cov.paste(layer, (int(x), int(y)), layer)
            placed.append(('word', wd, int(x), int(y)))
    for _ in range(p.get('lines', 0)):
        x0, y0 = rng.uniform(0.1, 0.8) * w, rng.uniform(0.1, 0.9) * h
        ln = mm(rng.uniform(15, 45), dpi)
        ang = rng.uniform(-0.3, 0.3)
        pts = []
        for t in np.linspace(0, 1, 30):
            pts.append((x0 + t * ln * math.cos(ang), y0 + t * ln * math.sin(ang) + mm(0.8, dpi) * math.sin(t * 9)))
        dr.line(pts, fill=210, width=lw, joint='curve')
        # arrow head
        xe, ye = pts[-1]
        dr.line([(xe - mm(2, dpi), ye - mm(1.5, dpi)), (xe, ye), (xe - mm(2, dpi), ye + mm(1.5, dpi))],
                fill=210, width=lw)
    m = np.asarray(cov.filter(ImageFilter.GaussianBlur(0.5 * dpi / 300)), np.float32) / 255.0
    # graphite grain
    m *= np.clip(0.65 + 0.35 * rng.random(m.shape).astype(np.float32), 0, 1)
    out = blend_color(img, m, p.get('color', [95, 95, 105]), p.get('alpha', 0.75))
    op_pencil.last_placed = placed
    return out


def op_holes(img, p, rng, dpi):
    """punched filing holes (scanner lid shows through)"""
    h, w = img.shape[:2]
    out = img.copy()
    n = p.get('n', 2)
    r = mm(p.get('diam_mm', 6) / 2, dpi)
    off = mm(p.get('offset_mm', 11), dpi)
    side = p.get('side', 'left')
    spacing = mm(p.get('spacing_mm', 80), dpi)
    col = np.array(p.get('color', [28, 28, 30]), np.float32)
    centers = []
    mid = h / 2 if side in ('left', 'right') else w / 2
    for k in range(n):
        c = mid + (k - (n - 1) / 2) * spacing + rng.uniform(-2, 2)
        if side == 'left':
            centers.append((off, c))
        elif side == 'right':
            centers.append((w - off, c))
        else:
            centers.append((c, off))
    for cx, cy in centers:
        x0, x1 = int(cx - 2 * r), int(cx + 2 * r)
        y0, y1 = int(cy - 2 * r), int(cy + 2 * r)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        hole = np.clip(r - d + 0.5, 0, 1)
        shadow = np.clip(1 - (d - r) / (0.35 * r), 0, 1) * (d > r) * 0.35
        sl = out[y0:y1, x0:x1]
        sl[:] = sl * (1 - hole[..., None]) + col * hole[..., None]
        sl[:] = sl * (1 - shadow[..., None])
    return out


def op_staple(img, p, rng, dpi):
    h, w = img.shape[:2]
    corner = p.get('corner', 'tl')
    ln = mm(p.get('len_mm', 12), dpi)
    ang = math.radians(p.get('angle', 40))
    off = mm(p.get('offset_mm', 9), dpi)
    cx = off if 'l' in corner else w - off
    cy = off if 't' in corner else h - off
    cx += math.cos(ang) * ln * 0.3
    pil = to_pil(img)
    dr = ImageDraw.Draw(pil)
    x0, y0 = cx - math.cos(ang) * ln / 2, cy - math.sin(ang) * ln / 2
    x1, y1 = cx + math.cos(ang) * ln / 2, cy + math.sin(ang) * ln / 2
    wd = max(2, int(mm(0.7, dpi)))
    dr.line([(x0 + 3, y0 + 3), (x1 + 3, y1 + 3)], fill=(150, 150, 150), width=wd + 2)   # shadow
    dr.line([(x0, y0), (x1, y1)], fill=(110, 112, 118), width=wd)
    dr.line([(x0, y0 - 1), (x1, y1 - 1)], fill=(205, 208, 212), width=max(1, wd // 3))   # glint
    for (ex, ey) in ((x0, y0), (x1, y1)):
        dr.ellipse([ex - wd, ey - wd, ex + wd, ey + wd], fill=(60, 60, 64))
    return from_pil(pil)


def op_page_texture_fold(img, p, rng, dpi):
    """a crease/fold line across the page"""
    h, w = img.shape[:2]
    y = p.get('y', 0.5) * h
    width = mm(p.get('width_mm', 1.5), dpi)
    yy = np.arange(h, dtype=np.float32)[:, None]
    tilt = math.tan(math.radians(p.get('tilt', 0.5)))
    xx = np.arange(w, dtype=np.float32)[None, :]
    d = (yy - (y + tilt * (xx - w / 2))) / width
    shade = 1 - p.get('dark', 0.18) * np.exp(-d ** 2) + 0.05 * np.exp(-(d - 1.5) ** 2)
    return img * shade[..., None]


def op_curl(img, p, rng, dpi):
    h, w = img.shape[:2]
    sc = dpi / 300.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    amp = p['amp'] * sc
    width = p.get('width', 0.25) * w
    if p.get('side', 'left') == 'left':
        t = np.clip((width - xx) / width, 0, 1)
        sgn = 1
    else:
        t = np.clip((xx - (w - width)) / width, 0, 1)
        sgn = -1
    dy = amp * t ** 2 * ((yy - h / 2) / (h / 2))
    dx = (amp * 0.6) * t ** 2 * sgn
    if p.get('wave'):
        dy += p['wave'] * sc * np.sin(2 * np.pi * xx / (1.3 * w) + 0.4)
    out = remap_rgb(img, xx - dx, yy - dy, p.get('fill', [250, 250, 250]))
    return out


def op_rotate(img, p, rng, dpi):
    fill = tuple(int(x) for x in p.get('fill', [250, 250, 250]))
    pil = to_pil(img).rotate(p['deg'], resample=Image.BICUBIC, expand=p.get('expand', False), fillcolor=fill)
    return from_pil(pil)


def op_rot90(img, p, rng, dpi):
    return np.ascontiguousarray(np.rot90(img, k=p['k']))


def op_phone(img, p, rng, dpi):
    """photo of the page lying on a table: margin of background, perspective
    (keystone: top edge farther away -> narrower), random corner jitter"""
    h, w = img.shape[:2]
    m = int(p.get('margin', 0.05) * w)
    bg = np.array(p.get('bg', [80, 70, 60]), np.float32)
    H, W = h + 2 * m, w + 2 * m
    canvas = np.empty((H, W, 3), np.float32)
    canvas[:] = bg
    canvas += 14 * smooth_field((H, W), rng, (5, 5))[..., None]
    canvas[m:m + h, m:m + w] = img
    jit = p.get('jitter', 0.02)
    ks = p.get('keystone', 0.05)
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    src = [(ks * W, 0), (W - ks * W, 0), (W, H), (0, H)]
    src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in src]
    # src are where the page corners land in the photo; we need dst->src map for the
    # inverse transform: photo(x) = canvas(T^-1 x).  PIL wants coefficients mapping
    # output pixel -> input pixel, i.e. photo -> canvas: solve with (src as output).
    coeffs = perspective_coeffs(dst, src)
    pil = to_pil(canvas).transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC,
                                   fillcolor=tuple(int(x) for x in bg))
    return from_pil(pil)


def op_lighting(img, p, rng, dpi):
    h, w = img.shape[:2]
    out = img
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if p.get('gradient'):
        ang = math.radians(p['angle']) if 'angle' in p else rng.uniform(0, 2 * np.pi)
        t = ((xx / w - 0.5) * math.cos(ang) + (yy / h - 0.5) * math.sin(ang)) + 0.5
        out = out * (1 - p['gradient'] * np.clip(t, 0, 1))[..., None]
    if p.get('vignette'):
        r = np.sqrt(((xx / w - 0.5)) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
        out = out * (1 - p['vignette'] * r ** 2)[..., None]
    if p.get('blotch'):
        out = out * (1 - p['blotch'] * np.clip(smooth_field((h, w), rng, (5, 4), -0.5, 1), 0, 1))[..., None]
    if p.get('hotspot'):
        cx, cy = rng.uniform(0.3, 0.7) * w, rng.uniform(0.2, 0.5) * h
        r2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (0.25 * (w * w + h * h))
        out = out + p['hotspot'] * 255 * np.exp(-r2 * 6)[..., None] * 0.15
    if p.get('tint'):
        out = out * (np.array(p['tint'], np.float32) / 255.0)[None, None, :]
    return out


def op_gutter(img, p, rng, dpi):
    h, w = img.shape[:2]
    gw = int(p.get('width', 0.06) * w)
    prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * p.get('dark', 0.55)
    side = p.get('side', 'left')
    out = img.copy()
    if side == 'left':
        out[:, :gw] *= (1 - prof)[None, :, None]
    elif side == 'right':
        out[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
    else:   # centre (2-up spread / open book)
        c = int(p.get('x', 0.5) * w)
        prof2 = np.concatenate([prof[::-1], prof])
        x0 = max(0, c - gw)
        x1 = min(w, c + gw)
        out[:, x0:x1] *= (1 - prof2[(x0 - (c - gw)):(x0 - (c - gw)) + (x1 - x0)])[None, :, None]
    return out


def op_crop(img, p, rng, dpi):
    h, w = img.shape[:2]
    l, r = int(mm(p.get('left', 0), dpi)), int(mm(p.get('right', 0), dpi))
    t, b = int(mm(p.get('top', 0), dpi)), int(mm(p.get('bottom', 0), dpi))
    return np.ascontiguousarray(img[t:h - b if b else h, l:w - r if r else w])


def op_blur(img, p, rng, dpi):
    return from_pil(to_pil(img).filter(ImageFilter.GaussianBlur(p['sigma'] * dpi / 300)))


def op_motion(img, p, rng, dpi):
    n = max(2, int(round(p['length'] * dpi / 300)))
    a = math.radians(p.get('angle', 0))
    acc = np.zeros_like(img)
    for k in range(n):
        t = k - (n - 1) / 2
        dx, dy = int(round(t * math.cos(a))), int(round(t * math.sin(a)))
        acc += np.roll(img, (dy, dx), axis=(0, 1))
    return acc / n


def op_resample(img, p, rng, dpi):
    h, w = img.shape[:2]
    f = p['factor']
    flt = {'nearest': Image.NEAREST, 'bilinear': Image.BILINEAR, 'box': Image.BOX}[p.get('filter', 'nearest')]
    pil = to_pil(img).resize((max(1, int(w * f)), max(1, int(h * f))), flt)
    if p.get('restore', True):
        pil = pil.resize((w, h), Image.BILINEAR)
    return from_pil(pil)


def op_noise(img, p, rng, dpi):
    n = rng.normal(0, p['sigma'], img.shape[:2]).astype(np.float32)
    if p.get('chroma'):
        return img + n[..., None] + rng.normal(0, p['chroma'], img.shape).astype(np.float32)
    return img + n[..., None]


def op_saltpepper(img, p, rng, dpi):
    h, w = img.shape[:2]
    n = int(p['amount'] * h * w)
    ys = rng.integers(0, h, n)
    xs = rng.integers(0, w, n)
    vals = np.where(rng.random(n) < p.get('pepper', 0.5), 15.0, 250.0).astype(np.float32)
    out = img.copy()
    out[ys, xs] = vals[:, None]
    return out


def op_speckle(img, p, rng, dpi):
    h, w = img.shape[:2]
    out = img
    n = int(p['per_mpx'] * (w * h) / 1e6)
    sc = dpi / 300
    for _ in range(n):
        r = rng.uniform(0.6, 2.4) * sc
        cy, cx = rng.integers(0, h), rng.integers(0, w)
        y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
        x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
        out[y0:y1, x0:x1][mask] = rng.uniform(15, 70)
    return out


OPS = {
    'ink': op_ink, 'dropout': op_dropout, 'halftone': op_halftone, 'paper': op_paper, 'bleed': op_bleed,
    'stain': op_stain, 'foxing': op_foxing, 'pencil': op_pencil, 'holes': op_holes, 'staple': op_staple,
    'fold': op_page_texture_fold, 'curl': op_curl, 'rotate': op_rotate, 'rot90': op_rot90, 'phone': op_phone,
    'lighting': op_lighting, 'gutter': op_gutter, 'crop': op_crop, 'blur': op_blur, 'motion': op_motion,
    'resample': op_resample, 'noise': op_noise, 'saltpepper': op_saltpepper, 'speckle': op_speckle,
}

TAGS = {
    'ink': lambda p: 'ink_thicken' if p['weight'] > 0 else 'ink_thin', 'dropout': 'faded_ink',
    'halftone': 'halftone_moire', 'paper': lambda p: 'coloured_paper' if p.get('color') and
    (max(p['color']) - min(p['color']) > 12) else 'paper_texture', 'bleed': 'bleed_through',
    'stain': 'coffee_stain', 'foxing': 'foxing', 'pencil': 'pencil_annotations', 'holes': 'punch_holes',
    'staple': 'staple', 'fold': 'fold_crease', 'curl': 'page_curl',
    'rotate': lambda p: f'skew_{abs(p["deg"]):g}deg', 'rot90': lambda p: f'rotated_{90 * p["k"]}deg',
    'phone': 'phone_perspective', 'lighting': 'uneven_lighting', 'gutter': 'gutter_shadow',
    'crop': 'cropped_edges', 'blur': 'focus_blur', 'motion': 'motion_blur', 'resample': 'resample_aliasing',
    'noise': 'gaussian_noise', 'saltpepper': 'salt_pepper', 'speckle': 'speckles',
}


def tags_for(recipe):
    out = []
    for po in recipe.get('page_ops', []):
        out.append({'page_scale': 'page_scale_mismatch', 'spread': 'two_up_spread'}[po['op']])
    for o in recipe['ops']:
        t = TAGS[o['op']]
        out.append(t(o) if callable(t) else t)
    if recipe.get('mode') == 'bw':
        b = recipe.get('binarize', {})
        out.append('binarized_' + b.get('style', 'photocopy'))
    if recipe.get('mode') == 'rgb':
        out.append('rgb_scan')
    if recipe.get('jpeg'):
        out.append(f'jpeg_q{recipe["jpeg"]}')
    d = recipe['dpi']
    if d <= 150:
        out.append(f'low_dpi_{d}')
    elif d >= 400:
        out.append(f'high_dpi_{d}')
    return out


# ----------------------------------------------------------------- page-set ops
def page_scale(pages, factors):
    out = []
    for k, pg in enumerate(pages):
        f = factors[k % len(factors)]
        if abs(f - 1) < 1e-6:
            out.append(pg)
            continue
        h, w = pg.shape
        pil = Image.fromarray(pg).resize((int(w * f), int(h * f)), Image.LANCZOS)
        canvas = Image.new('L', (w, h), 255)
        canvas.paste(pil, ((w - pil.width) // 2, (h - pil.height) // 2))
        out.append(np.asarray(canvas))
    return out


def spread(pages, p, dpi):
    """2-up: consecutive pages side by side on one sheet, reduced"""
    out = []
    gap = int(mm(p.get('gap_mm', 6), dpi))
    for k in range(0, len(pages), 2):
        a = pages[k]
        b = pages[k + 1] if k + 1 < len(pages) else np.full_like(a, 255)
        h = max(a.shape[0], b.shape[0])
        W = a.shape[1] + b.shape[1] + gap
        canvas = np.full((h, W), 255, np.uint8)
        canvas[:a.shape[0], :a.shape[1]] = a
        canvas[:b.shape[0], a.shape[1] + gap:] = b
        r = p.get('reduce', 0.707)
        pil = Image.fromarray(canvas).resize((int(W * r), int(h * r)), Image.LANCZOS)
        out.append(np.asarray(pil))
    return out


# ----------------------------------------------------------------- driver
def damage_pages(pages_gray, recipe):
    """pages_gray: list of uint8 gray arrays rendered at recipe['dpi'].
    Returns list of PIL images ready for the PDF and a log."""
    dpi = recipe['dpi']
    rng = np.random.default_rng(recipe['seed'])
    pages = list(pages_gray)
    for po in recipe.get('page_ops', []):
        if po['op'] == 'page_scale':
            pages = page_scale(pages, po['factors'])
        elif po['op'] == 'spread':
            pages = spread(pages, po, dpi)
    out = []
    log = []
    for idx, pg in enumerate(pages):
        img = np.repeat(pg.astype(np.float32)[..., None], 3, axis=2)
        plog = []
        for o in recipe['ops']:
            if o.get('pages') is not None and idx not in o['pages']:
                continue
            fn = OPS[o['op']]
            if o['op'] == 'bleed':
                img = fn(img, o, rng, dpi, pages=pages, index=idx)
            else:
                img = fn(img, o, rng, dpi)
            if o['op'] == 'pencil':
                plog.append({'pencil_marks': getattr(op_pencil, 'last_placed', [])})
        img = np.clip(img, 0, 255)
        mode = recipe.get('mode', 'gray')
        if mode == 'rgb':
            pil = Image.fromarray(img.astype(np.uint8), 'RGB')
        else:
            L = lum(img)
            if mode == 'bw':
                b = recipe.get('binarize', {})
                if b.get('blur'):
                    L = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(
                        ImageFilter.GaussianBlur(b['blur'] * dpi / 300)), np.float32)
                if b.get('noise'):
                    L = L + rng.normal(0, b['noise'], L.shape).astype(np.float32)
                bil = L > b.get('threshold', 150)
                pil = Image.fromarray((bil * 255).astype(np.uint8)).convert('1', dither=Image.NONE)
            else:
                pil = Image.fromarray(L.astype(np.uint8), 'L')
        out.append(pil)
        log.append({'page': idx + 1, 'size_px': [pil.width, pil.height], 'events': plog})
    return out, log


def save_pdf(images, dpi, out_pdf, jpeg=None, jpeg_passes=1):
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if jpeg and im.mode != '1':
                cur = im
                for _ in range(jpeg_passes - 1):
                    b2 = io.BytesIO()
                    cur.save(b2, 'JPEG', quality=min(95, jpeg + 15))
                    b2.seek(0)
                    cur = Image.open(b2).convert(im.mode)
                fn = os.path.join(td, f'p{k:03d}.jpg')
                cur.save(fn, 'JPEG', quality=jpeg, dpi=(dpi, dpi), optimize=True)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{dpi}dpi', '-o', out_pdf] + files, check=True,
                       capture_output=True, timeout=600)
