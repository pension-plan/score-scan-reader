"""Rasterise an engraved PDF and simulate scanning / photocopying / phone
capture.  numpy + Pillow only.  Output: image-only PDF via img2pdf."""
from __future__ import annotations

import glob
import io
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None


def render_pages(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'r{dpi}')
    for f in glob.glob(prefix + '-*.pgm'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True)
    files = sorted(glob.glob(prefix + '-*.pgm'))
    return [np.array(Image.open(f), dtype=np.uint8) for f in files]


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def remap(img, xs, ys, fill=255.0):
    h, w = img.shape
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = (xs - x0).astype(np.float32)
    fy = (ys - y0).astype(np.float32)
    valid = (x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1)
    x0c = np.clip(x0, 0, w - 2)
    y0c = np.clip(y0, 0, h - 2)
    a = img[y0c, x0c]
    b = img[y0c, x0c + 1]
    c = img[y0c + 1, x0c]
    d = img[y0c + 1, x0c + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(valid, out, fill).astype(np.float32)


def perspective_coeffs(src, dst):
    """coefficients mapping dst->src for PIL.Image.transform"""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)).tolist()


def degrade(page: np.ndarray, P: dict, rng: np.random.Generator):
    """page: uint8 gray (white paper, black ink).  Returns PIL image."""
    img = page.astype(np.float32)
    h, w = img.shape
    dpi = P['dpi']
    sc = dpi / 300.0
    # --- ink weight (before anything else)
    ink = P.get('ink_weight', 0)
    if ink:
        pil = Image.fromarray(img.astype(np.uint8))
        for _ in range(abs(ink)):
            pil = pil.filter(ImageFilter.MinFilter(3) if ink > 0 else ImageFilter.MaxFilter(3))
        img = np.asarray(pil, dtype=np.float32)
    if P.get('ink_dropout'):
        # faded / broken strokes: lighten ink with blotchy field
        f = smooth_field(img.shape, rng, (40, 30), 0, 1)
        fine = rng.random(img.shape).astype(np.float32)
        drop = (f > 1 - P['ink_dropout']) & (fine < 0.5)
        img = np.where(drop & (img < 200), img + (255 - img) * 0.6, img)
    # --- geometry: curl near a side edge (book gutter) and gentle waves
    if P.get('curl') or P.get('wave'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dy = np.zeros_like(xx)
        dx = np.zeros_like(xx)
        if P.get('curl'):
            c = P['curl']
            amp = c['amp'] * sc
            width = c.get('width', 0.25) * w
            if c.get('side', 'left') == 'left':
                t = np.clip((width - xx) / width, 0, 1)
            else:
                t = np.clip((xx - (w - width)) / width, 0, 1)
            dy += amp * t ** 2 * ((yy - h / 2) / (h / 2))
            dx += (amp * 0.6) * t ** 2 * (1 if c.get('side', 'left') == 'left' else -1)
        if P.get('wave'):
            wv = P['wave']
            dy += wv['amp'] * sc * np.sin(2 * np.pi * xx / (wv.get('period', 1.3) * w) + wv.get('phase', 0.3))
        img = remap(img, xx - dx, yy - dy)
        del yy, xx, dx, dy
    # --- rotation
    if P.get('rotate'):
        pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        pil = pil.rotate(P['rotate'], resample=Image.BICUBIC, fillcolor=255)
        img = np.asarray(pil, dtype=np.float32)
    # --- coverage composite onto paper
    cov = 1.0 - img / 255.0
    if P.get('bleed'):
        mir = cov[:, ::-1]
        mpil = Image.fromarray((mir * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5 * sc))
        shift = int(rng.integers(-20, 20) * sc)
        mir = np.roll(np.asarray(mpil, dtype=np.float32) / 255.0, shift, axis=0)
        cov = np.clip(cov + P['bleed'] * mir, 0, 1)
    paper = P.get('paper', 245.0)
    tex = P.get('texture', 0)
    paper_f = np.full(img.shape, paper, np.float32)
    if tex:
        paper_f += tex * smooth_field(img.shape, rng, (14, 10))
        paper_f += tex * 0.5 * rng.normal(0, 1, img.shape).astype(np.float32)
    ink_level = P.get('ink_level', 20.0)
    ink_f = ink_level + P.get('ink_var', 0) * smooth_field(img.shape, rng, (10, 8), 0, 1)
    out = paper_f * (1 - cov) + ink_f * cov
    # --- lighting
    if P.get('gradient'):
        g = P['gradient']
        ang = rng.uniform(0, 2 * np.pi)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        t = ((xx / w - 0.5) * np.cos(ang) + (yy / h - 0.5) * np.sin(ang)) + 0.5
        out = out * (1 - g * np.clip(t, 0, 1))
        del yy, xx
    if P.get('blotch'):
        out = out * (1 - P['blotch'] * np.clip(smooth_field(img.shape, rng, (5, 4), -0.5, 1), 0, 1))
    if P.get('vignette'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx / w - 0.5) * 1.0) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
        out = out * (1 - P['vignette'] * r ** 2)
        del yy, xx, r
    if P.get('gutter'):
        gw = int(P['gutter'].get('width', 0.06) * w)
        side = P['gutter'].get('side', 'left')
        prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * P['gutter'].get('dark', 0.55)
        if side == 'left':
            out[:, :gw] *= (1 - prof)[None, :]
        else:
            out[:, w - gw:] *= (1 - prof[::-1])[None, :]
    if P.get('border'):
        b = P['border']
        bw = int(b.get('width', 30) * sc)
        lvl = b.get('level', 35)
        side = b.get('side', 'top')
        if side == 'top':
            out[:bw, :] = lvl + rng.normal(0, 6, (bw, w))
        elif side == 'bottom':
            out[h - bw:, :] = lvl + rng.normal(0, 6, (bw, w))
        elif side == 'left':
            out[:, :bw] = lvl + rng.normal(0, 6, (h, bw))
        else:
            out[:, w - bw:] = lvl + rng.normal(0, 6, (h, bw))
    # --- phone capture: place page on a background and apply a perspective
    if P.get('phone'):
        ph = P['phone']
        m = int(ph.get('margin', 0.05) * w)
        bg = ph.get('bg', 70)
        H, W = h + 2 * m, w + 2 * m
        canvas = np.full((H, W), bg, np.float32) + 12 * smooth_field((H, W), rng, (4, 4))
        canvas[m:m + h, m:m + w] = out
        jit = ph.get('jitter', 0.03)
        dst = [(0, 0), (W, 0), (W, H), (0, H)]
        src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in dst]
        coeffs = perspective_coeffs(src, dst)
        pil = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
        pil = pil.transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC, fillcolor=int(bg))
        out = np.asarray(pil, dtype=np.float32)
        h, w = out.shape
    # --- optics + sensor
    if P.get('blur'):
        pil = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(P['blur'] * sc))
        out = np.asarray(pil, dtype=np.float32)
    if P.get('noise'):
        out = out + rng.normal(0, P['noise'], out.shape).astype(np.float32)
    if P.get('saltpepper'):
        n = int(P['saltpepper'] * out.size)
        ys = rng.integers(0, h, n)
        xs = rng.integers(0, w, n)
        vals = np.where(rng.random(n) < 0.6, ink_level, paper)
        out[ys, xs] = vals
    if P.get('speckle'):
        n = int(P['speckle'] * (w * h) / 1e6)
        for _ in range(n):
            r = rng.uniform(0.6, 2.2) * sc
            cy, cx = rng.integers(0, h), rng.integers(0, w)
            y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
            x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
            out[y0:y1, x0:x1][mask] = ink_level + rng.uniform(0, 60)
    out = np.clip(out, 0, 255)
    if P.get('binarize'):
        thr = P['binarize']
        if P.get('binarize_noise'):
            out = out + rng.normal(0, P['binarize_noise'], out.shape)
        bil = (out > thr)
        return Image.fromarray((bil * 255).astype(np.uint8)).convert('1', dither=Image.NONE)
    return Image.fromarray(out.astype(np.uint8), mode='L')


def save_pdf(pages, dpi, out_pdf, fmt='jpeg', quality=75, jpeg_passes=1):
    """Wrap page images (JPEG or PNG, lossless pass-through) in a PDF with the
    img2pdf CLI (image-only, page size from dpi)."""
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(pages):
            if fmt == 'jpeg':
                cur = im
                for _ in range(jpeg_passes - 1):
                    b2 = io.BytesIO()
                    cur.save(b2, 'JPEG', quality=max(10, quality + 15))
                    b2.seek(0)
                    cur = Image.open(b2).convert('L')
                fn = os.path.join(td, f'p{k:03d}.jpg')
                cur.save(fn, 'JPEG', quality=quality, dpi=(dpi, dpi), optimize=True)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{dpi}dpi', '-o', out_pdf] + files, check=True,
                       capture_output=True)


def describe(P):
    names = []
    m = {'ink_weight': 'ink_weight', 'ink_dropout': 'faded_ink', 'curl': 'page_curl', 'wave': 'wavy_warp',
         'rotate': 'rotation', 'bleed': 'bleed_through', 'texture': 'paper_texture', 'gradient': 'lighting_gradient',
         'blotch': 'uneven_lighting', 'vignette': 'vignette', 'gutter': 'gutter_shadow', 'border': 'scanner_border',
         'phone': 'perspective_phone_capture', 'blur': 'blur', 'noise': 'gaussian_noise',
         'saltpepper': 'salt_pepper', 'speckle': 'speckles', 'binarize': 'binarized_photocopy'}
    for k, v in m.items():
        if P.get(k):
            names.append(v)
    if P.get('format', 'jpeg') == 'jpeg':
        names.append(f'jpeg_q{P.get("jpeg", 75)}')
    return names
