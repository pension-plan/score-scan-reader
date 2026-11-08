"""RGB scan / photocopy / phone-capture damage simulator (numpy + Pillow only).

A damage recipe is an ordered list of op dicts, e.g.
  [{'op': 'paper', 'rgb': [238, 228, 200], 'texture': 6},
   {'op': 'pencil', 'circles': 3, 'ticks': 2},
   {'op': 'rotate', 'deg': 2.5, 'fill': 236},
   {'op': 'blur', 'sigma': 0.8}, {'op': 'noise', 'sigma': 5}]
plus output settings {'format': 'jpeg'|'png', 'quality': 40, 'jpeg_passes': 1}.
Every op may carry 'pages': [0-based page indices] to restrict it.
Physical sizes are in mm (converted with the working dpi); sigma values are
in pixels at 300 dpi and scaled to the working dpi.

Stages: the page starts as an ink-coverage map (cov ops: ink_weight,
ink_dropout); the 'paper' op composites it onto paper (colour, texture,
bleed-through); after that, ops act on an RGB float image.  A document-level
'spread' option pastes page pairs side by side (2-up book spread) right after
the paper/marking ops (first geometry op).

Derived from corpus/synthetic/_tools/synth/degrade.py and
spike/classical/tools/degrade.py (copied, extended; originals untouched).
"""
from __future__ import annotations

import io
import math
import os
import re
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None
HAND_FONT = '/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf'
COV_OPS = {'ink_weight', 'ink_dropout', 'paper'}
GEOM_OPS = {'curl', 'wave', 'scale', 'rotate', 'rot90', 'perspective', 'crop'}


# ------------------------------------------------------------------ helpers

def render_pages(pdf, dpi, workdir, tag='r'):
    prefix = os.path.join(workdir, f'{tag}{dpi}')
    for f in os.listdir(workdir):
        if f.startswith(os.path.basename(prefix) + '-') and f.endswith('.pgm'):
            os.remove(os.path.join(workdir, f))
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=600)
    files = sorted(f for f in os.listdir(workdir) if f.startswith(os.path.basename(prefix) + '-') and f.endswith('.pgm'))
    return [np.array(Image.open(os.path.join(workdir, f)), dtype=np.uint8) for f in files]


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def gblur(a, sigma):
    """gaussian blur of a float 2-D array (via 8-bit Pillow; fine for masks/fields)."""
    if sigma <= 0:
        return a
    lo, hi = float(a.min()), float(a.max())
    if hi - lo < 1e-6:
        return a
    im = Image.fromarray(np.clip((a - lo) / (hi - lo) * 255 + 0.5, 0, 255).astype(np.uint8), mode='L')
    out = np.asarray(im.filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32)
    return out / 255 * (hi - lo) + lo


def blur_rgb(rgb, sigma):
    if sigma <= 0:
        return rgb
    return np.stack([np.asarray(Image.fromarray(np.clip(rgb[..., c], 0, 255).astype(np.uint8))
                                .filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32) for c in range(3)], -1)


def remap_rgb(rgb, xs, ys, fill):
    h, w = rgb.shape[:2]
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = (xs - x0).astype(np.float32)[..., None]
    fy = (ys - y0).astype(np.float32)[..., None]
    valid = ((x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1))[..., None]
    x0c = np.clip(x0, 0, w - 2)
    y0c = np.clip(y0, 0, h - 2)
    a = rgb[y0c, x0c]
    b = rgb[y0c, x0c + 1]
    c = rgb[y0c + 1, x0c]
    d = rgb[y0c + 1, x0c + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(valid, out, np.array(fill, np.float32)).astype(np.float32)


def to_pil(rgb):
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), mode='RGB')


def from_pil(im):
    return np.asarray(im.convert('RGB'), dtype=np.float32)


def perspective_coeffs(src, dst):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)).tolist()


def fill3(v):
    if isinstance(v, np.ndarray):
        v = v.tolist()
    if isinstance(v, (list, tuple)):
        return [float(x) for x in v]
    return [float(v)] * 3


# ------------------------------------------------------------------ SVG anchors (note positions)

def svg_anchors(ly_path, workdir, page_px):
    """Engrave the .ly with the SVG backend and point-and-click; return per
    page a list of {'x','y' (px at the given page size), 'kind'} for grobs
    linked to the source (note heads, rests, lyric syllables...)."""
    base = 'anch'
    subprocess.run(['lilypond', '-dbackend=svg', '-dpoint-and-click', '-o', base, os.path.basename(ly_path)],
                   cwd=workdir, capture_output=True, timeout=600)
    files = sorted(f for f in os.listdir(workdir) if re.match(base + r'(-\d+)?\.svg$', f))
    files.sort(key=lambda f: int(re.search(r'-(\d+)\.svg$', f).group(1)) if '-' in f else 0)
    src_lines = open(ly_path, encoding='utf-8').read().split('\n')
    pages = []
    for k, f in enumerate(files):
        txt = open(os.path.join(workdir, f), encoding='utf-8').read()
        vb = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', txt)
        vw, vh = float(vb.group(3)), float(vb.group(4))
        W, H = page_px[k] if k < len(page_px) else page_px[-1]
        sx, sy = W / vw, H / vh
        out = []
        for m in re.finditer(r'<a[^>]*href="textedit://[^"]*:(\d+):(\d+):(\d+)"[^>]*>\s*<(path|text|g|rect)[^>]*?'
                             r'transform="translate\(([\-\d.]+),\s*([\-\d.]+)\)', txt):
            line, col = int(m.group(1)), int(m.group(2))
            tok = src_lines[line - 1][col:col + 12] if line - 1 < len(src_lines) else ''
            if tok.startswith('"'):
                kind = 'lyric'
            elif re.match(r"r[\d\s]", tok):
                kind = 'rest'
            elif re.match(r"[a-g<]", tok):
                kind = 'note'
            else:
                kind = 'other'
            out.append({'x': float(m.group(5)) * sx, 'y': float(m.group(6)) * sy, 'kind': kind})
        pages.append(out)
    return pages


def staff_extent(gray):
    """(x_left, x_right) of staff lines on a clean page (rows that are mostly ink)."""
    cov = gray < 128
    rows = cov.mean(axis=1)
    idx = np.where(rows > 0.45)[0]
    if not len(idx):
        return None
    xs_r, xs_l = [], []
    for r in idx[:: max(1, len(idx) // 40)]:
        cols = np.where(cov[r])[0]
        xs_l.append(cols.min())
        xs_r.append(cols.max())
    return int(np.median(xs_l)), int(np.median(xs_r))


# ------------------------------------------------------------------ marks

def _wobbly_ellipse(cx, cy, rx, ry, rng, loops=1.15, n=90):
    t0 = rng.uniform(0, 2 * np.pi)
    ts = t0 + np.linspace(0, 2 * np.pi * loops, n)
    wob = 1 + 0.08 * np.sin(ts * rng.uniform(1.5, 3.0) + rng.uniform(0, 6)) + rng.normal(0, 0.015, n)
    drift = np.linspace(0, rng.uniform(-0.12, 0.12), n)
    return [(cx + rx * (w + d) * np.cos(t), cy + ry * (w + d) * np.sin(t)) for t, w, d in zip(ts, wob, drift)]


def pencil_layer(shape, ctx, P, rng):
    """alpha layer (0..1) of hand-drawn pencil/pen marks."""
    h, w = shape
    mmp = ctx['dpi'] / 25.4
    lay = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(lay)
    lw = max(1, int(round(P.get('width_mm', 0.35) * mmp)))
    anchors = [a for a in ctx.get('anchors', []) if a['kind'] == 'note']
    log = []
    for _ in range(P.get('circles', 0)):
        if not anchors:
            break
        a = anchors[int(rng.integers(0, len(anchors)))]
        rx, ry = rng.uniform(2.6, 4.2) * mmp, rng.uniform(2.2, 3.6) * mmp
        cx, cy = a['x'] + 0.6 * mmp, a['y']
        dr.line(_wobbly_ellipse(cx, cy, rx, ry, rng), fill=255, width=lw, joint='curve')
        log.append(['circle', round(cx / mmp, 1), round(cy / mmp, 1)])
    for _ in range(P.get('ticks', 0)):
        cx, cy = rng.uniform(0.1, 0.9) * w, rng.uniform(0.15, 0.95) * h
        s = rng.uniform(2.5, 4.5) * mmp
        dr.line([(cx - s * 0.4, cy - s * 0.1), (cx, cy + s * 0.35), (cx + s * 0.8, cy - s * 0.7)], fill=255, width=lw)
        log.append(['tick', round(cx / mmp, 1), round(cy / mmp, 1)])
    for _ in range(P.get('breaths', 0)):
        if not anchors:
            break
        a = anchors[int(rng.integers(0, len(anchors)))]
        cx, cy = a['x'] + rng.uniform(2, 4) * mmp, a['y'] - rng.uniform(6, 9) * mmp
        s = rng.uniform(1.6, 2.4) * mmp
        dr.line([(cx - s * 0.5, cy - s), (cx, cy), (cx + s * 0.5, cy - s)], fill=255, width=lw)
        log.append(['breath_V', round(cx / mmp, 1), round(cy / mmp, 1)])
    for _ in range(P.get('arrows', 0)):
        x0, y0 = rng.uniform(0.15, 0.85) * w, rng.uniform(0.15, 0.9) * h
        L = rng.uniform(8, 16) * mmp
        ang = rng.uniform(0, 2 * np.pi)
        x1, y1 = x0 + L * np.cos(ang), y0 + L * np.sin(ang)
        dr.line([(x0, y0), (x1, y1)], fill=255, width=lw)
        for da in (2.6, -2.6):
            dr.line([(x1, y1), (x1 + 2.2 * mmp * np.cos(ang + da), y1 + 2.2 * mmp * np.sin(ang + da))], fill=255,
                    width=lw)
        log.append(['arrow', round(x0 / mmp, 1), round(y0 / mmp, 1)])
    texts = P.get('texts', [])
    if texts:
        font = ImageFont.truetype(HAND_FONT, int(P.get('text_mm', 4.5) * mmp))
        for t in texts:
            if anchors and rng.random() < 0.7:
                a = anchors[int(rng.integers(0, len(anchors)))]
                x, y = a['x'] + rng.uniform(-4, 6) * mmp, a['y'] - rng.uniform(9, 13) * mmp
            else:
                x, y = rng.uniform(0.1, 0.75) * w, rng.uniform(0.04, 0.12) * h
            dr.text((x, y), t, font=font, fill=255)
            log.append(['text', t, round(x / mmp, 1), round(y / mmp, 1)])
    for _ in range(P.get('scribbles', 0)):
        x0, y0 = rng.uniform(0.05, 0.9) * w, rng.uniform(0.9, 0.97) * h
        pts = [(x0 + k * 1.2 * mmp, y0 + rng.uniform(-1.5, 1.5) * mmp) for k in range(int(rng.integers(12, 30)))]
        dr.line(pts, fill=255, width=lw)
        log.append(['scribble', round(x0 / mmp, 1), round(y0 / mmp, 1)])
    a = np.asarray(lay, dtype=np.float32) / 255.0
    a = gblur(a, 0.5 * ctx['dpi'] / 300)
    grain = 0.55 + 0.45 * rng.random(shape).astype(np.float32)
    return np.clip(a * grain * P.get('alpha', 0.6), 0, 1), log


# ------------------------------------------------------------------ ops

def op_paper(state, P, ctx, rng):
    cov = state['cov']
    h, w = cov.shape
    paper = np.array(P.get('rgb', [246, 246, 244]), np.float32)
    ink = np.array(P.get('ink', [22, 22, 26]), np.float32)
    base = np.ones((h, w, 1), np.float32) * paper[None, None, :]
    tex = P.get('texture', 0)
    if tex:
        f = tex * smooth_field((h, w), rng, (14, 10)) + tex * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        base = base + f[..., None]
    if P.get('fibers'):
        fib = gblur(rng.normal(0, 1, (h // 4 + 1, w // 4 + 1)).astype(np.float32), 0.8)
        fib = np.asarray(Image.fromarray(fib, mode='F').resize((w, h), Image.BILINEAR), dtype=np.float32)
        base = base + P['fibers'] * fib[..., None]
    if P.get('bleed'):
        b = P['bleed']
        src = ctx.get('reverse_cov')
        if src is None or src.shape != cov.shape:
            src = cov
        mir = src[:, ::-1]
        mir = gblur(mir, b.get('blur_mm', 0.35) * ctx['dpi'] / 25.4)
        shift = int(b.get('shift_mm', 3.0) * ctx['dpi'] / 25.4)
        mir = np.roll(mir, shift, axis=0)
        base = base * (1 - b.get('strength', 0.1) * mir[..., None])
    ink_var = P.get('ink_var', 0)
    inkf = ink[None, None, :] + (ink_var * smooth_field((h, w), rng, (10, 8), 0, 1))[..., None]
    state['rgb'] = base * (1 - cov[..., None]) + inkf * cov[..., None]
    state['paper'] = paper
    del state['cov']


def op_ink_weight(state, P, ctx, rng):
    n = P.get('n', 1)
    im = Image.fromarray(np.clip((1 - state['cov']) * 255, 0, 255).astype(np.uint8))
    for _ in range(abs(n)):
        im = im.filter(ImageFilter.MinFilter(3) if n > 0 else ImageFilter.MaxFilter(3))
    state['cov'] = 1 - np.asarray(im, dtype=np.float32) / 255


def op_ink_dropout(state, P, ctx, rng):
    cov = state['cov']
    f = smooth_field(cov.shape, rng, (40, 30), 0, 1)
    fine = rng.random(cov.shape).astype(np.float32)
    drop = (f > 1 - P.get('amount', 0.2)) & (fine < 0.5)
    state['cov'] = np.where(drop, cov * 0.4, cov)


def op_foxing(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    col = np.array(P.get('color', [150, 105, 60]), np.float32)
    lo, hi = P.get('size_mm', [0.4, 2.5])
    for _ in range(int(P.get('n', 60))):
        r = rng.uniform(lo, hi) * mmp
        cy, cx = rng.uniform(0, h), rng.uniform(0, w)
        y0, y1 = int(max(0, cy - 2 * r)), int(min(h, cy + 2 * r + 1))
        x0, x1 = int(max(0, cx - 2 * r)), int(min(w, cx + 2 * r + 1))
        if y1 <= y0 or x1 <= x0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** 0.7 * rng.uniform(0.25, 0.7)
        rgb[y0:y1, x0:x1] = rgb[y0:y1, x0:x1] * (1 - a[..., None]) + (col * rgb[y0:y1, x0:x1] / 255) * a[..., None]


def op_coffee(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    cx, cy = P.get('x', 0.7) * w, P.get('y', 0.3) * h
    R = P.get('r_mm', 35) * mmp
    col = np.array(P.get('color', [165, 115, 60]), np.float32)
    st = P.get('strength', 0.5)
    y0, y1 = int(max(0, cy - 1.3 * R)), int(min(h, cy + 1.3 * R))
    x0, x1 = int(max(0, cx - 1.3 * R)), int(min(w, cx + 1.3 * R))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    ang = np.arctan2(yy - cy, xx - cx)
    rmod = R * (1 + 0.06 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.04 * np.sin(7 * ang + rng.uniform(0, 6)))
    d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2) / rmod
    ring = np.exp(-((d - 1) / 0.035) ** 2) * 0.9
    inner = np.where(d < 1, 0.25 + 0.1 * smooth_field(d.shape, rng, (6, 6), -1, 1), 0)
    a = np.clip((ring + inner) * st, 0, 0.85)
    if P.get('partial', True):  # half ring (cup put down near the edge)
        a = a * (np.cos(ang - rng.uniform(0, 6.28)) > -0.3)
    mult = (col / 255)[None, None, :]
    region = rgb[y0:y1, x0:x1]
    rgb[y0:y1, x0:x1] = region * (1 - a[..., None]) + region * mult * a[..., None]


def op_pencil(state, P, ctx, rng):
    rgb = state['rgb']
    a, log = pencil_layer(rgb.shape[:2], ctx, P, rng)
    col = np.array(P.get('color', [70, 70, 78]), np.float32)
    state['rgb'] = rgb * (1 - a[..., None]) + col[None, None, :] * a[..., None]
    ctx['log'].append({'op': 'pencil', 'marks': log})


def op_punch_holes(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    n = P.get('n', 2)
    d = P.get('d_mm', 6.0) * mmp
    edge = P.get('edge_mm', 11.0) * mmp
    sp = P.get('spacing_mm', 80.0) * mmp
    bg = np.array(fill3(P.get('bg', 35)), np.float32)
    side = P.get('side', 'left')
    ys = [h / 2 + (k - (n - 1) / 2) * sp for k in range(n)]
    for y in ys:
        x = edge if side == 'left' else w - edge
        r = d / 2
        y0, y1 = int(y - r - 3), int(y + r + 4)
        x0, x1 = int(x - r - 3), int(x + r + 4)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dist = np.sqrt((yy - y) ** 2 + (xx - x) ** 2)
        hole = np.clip(r - dist + 0.5, 0, 1)
        shadow = np.clip(1 - np.abs(dist - r - 1.5) / 2.5, 0, 1) * 0.35
        reg = rgb[y0:y1, x0:x1]
        reg = reg * (1 - shadow[..., None])
        rgb[y0:y1, x0:x1] = reg * (1 - hole[..., None]) + bg * hole[..., None]


def op_staple(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    x, y = P.get('x_mm', 9) * mmp, P.get('y_mm', 9) * mmp
    L = P.get('len_mm', 12) * mmp
    ang = math.radians(P.get('deg', -40))
    lay = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(lay)
    x1, y1 = x + L * math.cos(ang), y - L * math.sin(ang)
    dr.line([(x, y), (x1, y1)], fill=255, width=max(2, int(0.8 * mmp)))
    a = gblur(np.asarray(lay, dtype=np.float32) / 255, 0.6)
    sh = np.roll(np.roll(a, int(0.5 * mmp), 0), int(0.5 * mmp), 1) * 0.5
    rgb *= (1 - sh[..., None])
    metal = np.array([120, 122, 128], np.float32) + 50 * rng.random((h, w, 1)).astype(np.float32) * 0
    hl = np.clip(a * 1.0, 0, 1)
    state['rgb'] = rgb * (1 - hl[..., None]) + metal * hl[..., None]


def op_halftone(state, P, ctx, rng):
    """AM halftone screen on the luminance (printed reproduction); with a later
    'resample' this aliases into moire."""
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    lpi = P.get('lpi', 110)
    period = ctx['dpi'] / lpi
    ang = math.radians(P.get('deg', 45))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx * math.cos(ang) + yy * math.sin(ang)) * 2 * np.pi / period
    v = (-xx * math.sin(ang) + yy * math.cos(ang)) * 2 * np.pi / period
    screen = (np.cos(u) * np.cos(v) + 1) / 2
    del xx, yy, u, v
    lum = rgb.mean(axis=2) / 255
    dark = 1 - lum
    dots = (dark > screen).astype(np.float32)
    st = P.get('strength', 1.0)
    tone = np.where(dots[..., None] > 0, rgb * 0 + np.array(P.get('ink', [30, 30, 30]), np.float32),
                    np.array(fill3(P.get('white', 250)), np.float32))
    state['rgb'] = rgb * (1 - st) + tone * st


def op_resample(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    f = P['factor']
    filt = {'nearest': Image.NEAREST, 'bilinear': Image.BILINEAR, 'bicubic': Image.BICUBIC,
            'lanczos': Image.LANCZOS, 'box': Image.BOX}[P.get('filter', 'bilinear')]
    nw, nh = max(1, int(round(w * f))), max(1, int(round(h * f)))
    state['rgb'] = from_pil(to_pil(rgb).resize((nw, nh), filt))
    ctx['dpi'] = ctx['dpi'] * f


def op_curl(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    amp = P.get('amp_mm', 4) * mmp
    width = P.get('width', 0.25) * w
    side = P.get('side', 'left')
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((width - xx) / width, 0, 1) if side == 'left' else np.clip((xx - (w - width)) / width, 0, 1)
    dy = amp * t ** 2 * ((yy - h / 2) / (h / 2))
    dx = (amp * 0.6) * t ** 2 * (1 if side == 'left' else -1)
    state['rgb'] = remap_rgb(rgb, xx - dx, yy - dy, fill3(P.get('fill', 40)))
    shade = P.get('shade', 0.35)
    if shade:
        prof = (t ** 2.2 * shade)[..., None]
        state['rgb'] = state['rgb'] * (1 - prof)


def op_wave(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dy = P.get('amp_mm', 1.0) * mmp * np.sin(2 * np.pi * xx / (P.get('period', 1.3) * w) + P.get('phase', 0.3))
    state['rgb'] = remap_rgb(rgb, xx, yy - dy, fill3(P.get('fill', 245)))


def op_scale(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    s = P['s']
    fill = P.get('fill', state.get('paper', [245, 245, 245]))
    im = to_pil(rgb).resize((int(w * s), int(h * s)), Image.BICUBIC)
    canvas = Image.new('RGB', (w, h), tuple(int(x) for x in fill3(fill)))
    ox, oy = int((w - im.width) / 2 + P.get('dx_mm', 0) * ctx['dpi'] / 25.4), \
        int((h - im.height) / 2 + P.get('dy_mm', 0) * ctx['dpi'] / 25.4)
    canvas.paste(im, (ox, oy))
    state['rgb'] = from_pil(canvas)


def op_rotate(state, P, ctx, rng):
    im = to_pil(state['rgb'])
    fill = tuple(int(x) for x in fill3(P.get('fill', 255)))
    im = im.rotate(P['deg'], resample=Image.BICUBIC, expand=P.get('expand', abs(P['deg']) > 2.5), fillcolor=fill)
    state['rgb'] = from_pil(im)


def op_rot90(state, P, ctx, rng):
    state['rgb'] = np.ascontiguousarray(np.rot90(state['rgb'], P.get('k', 1)))


def op_perspective(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    m = int(P.get('margin', 0.06) * w)
    bg = P.get('bg', [70, 64, 58])
    H, W = h + 2 * m, w + 2 * m
    canvas = np.ones((H, W, 3), np.float32) * np.array(fill3(bg), np.float32)
    canvas += (14 * smooth_field((H, W), rng, (4, 4)))[..., None]
    canvas[m:m + h, m:m + w] = rgb
    if P.get('shadow', 0):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        canvas *= (1 - P['shadow'] * np.clip((xx / W - 0.55) * 2, 0, 1) * np.clip(yy / H, 0, 1))[..., None]
    jit = P.get('jitter', 0.03)
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    if P.get('keystone'):
        k = P['keystone']
        src = [(-k * W, 0), (W + k * W, 0), (W, H), (0, H)]   # camera tilted: page top appears narrower
        src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in src]
    else:
        src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in dst]
    coeffs = perspective_coeffs(src, dst)
    fill = tuple(int(x) for x in fill3(bg))
    im = to_pil(canvas).transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC, fillcolor=fill)
    state['rgb'] = from_pil(im)


def op_crop(state, P, ctx, rng):
    """crop page edges (mm). 'cut_staff_right_mm': crop the right edge that many
    mm inside the end of the staff lines (never closer than 2 mm to the last
    linked grob)."""
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    mmp = ctx['dpi'] / 25.4
    L = int(P.get('left_mm', 0) * mmp)
    R = w - int(P.get('right_mm', 0) * mmp)
    T = int(P.get('top_mm', 0) * mmp)
    B = h - int(P.get('bottom_mm', 0) * mmp)
    if P.get('cut_staff_right_mm') and ctx.get('staff_extent'):
        xr = ctx['staff_extent'][1]
        lim = max([a['x'] for a in ctx.get('anchors', []) if a['kind'] in ('note', 'rest')] or [0]) + 2.0 * mmp
        cut = int(max(xr - P['cut_staff_right_mm'] * mmp, lim))
        R = min(R, cut)
        ctx['log'].append({'op': 'crop', 'staff_right_px': xr, 'cut_at_px': cut,
                           'cut_into_staff_mm': round((xr - cut) / mmp, 2)})
    state['rgb'] = np.ascontiguousarray(rgb[T:B, L:R])


def op_gradient(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    ang = P.get('angle', None)
    ang = rng.uniform(0, 2 * np.pi) if ang is None else math.radians(ang)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = ((xx / w - 0.5) * np.cos(ang) + (yy / h - 0.5) * np.sin(ang)) + 0.5
    state['rgb'] = rgb * (1 - P.get('strength', 0.2) * np.clip(t, 0, 1))[..., None]


def op_vignette(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt((xx / w - 0.5) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
    state['rgb'] = rgb * (1 - P.get('strength', 0.3) * r ** 2)[..., None]


def op_blotch(state, P, ctx, rng):
    rgb = state['rgb']
    f = np.clip(smooth_field(rgb.shape[:2], rng, (5, 4), -0.5, 1), 0, 1)
    state['rgb'] = rgb * (1 - P.get('strength', 0.15) * f)[..., None]


def op_gutter(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    gw = int(P.get('width', 0.07) * w)
    prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * P.get('dark', 0.55)
    side = P.get('side', 'left')
    if side in ('left', 'both_center'):
        pass
    if side == 'left':
        rgb[:, :gw] *= (1 - prof)[None, :, None]
    elif side == 'right':
        rgb[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
    elif side == 'center':
        c = w // 2
        rgb[:, c:c + gw] *= (1 - prof)[None, :, None]
        rgb[:, c - gw:c] *= (1 - prof[::-1])[None, :, None]


def op_blur(state, P, ctx, rng):
    state['rgb'] = blur_rgb(state['rgb'], P.get('sigma', 1.0) * ctx['dpi'] / 300)


def op_motion_blur(state, P, ctx, rng):
    rgb = state['rgb']
    L = max(2, int(P.get('len_mm', 0.6) * ctx['dpi'] / 25.4))
    ang = math.radians(P.get('deg', 20))
    acc = np.zeros_like(rgb)
    for k in range(L):
        t = k - (L - 1) / 2
        dx, dy = int(round(t * math.cos(ang))), int(round(t * math.sin(ang)))
        acc += np.roll(np.roll(rgb, dy, 0), dx, 1)
    state['rgb'] = acc / L


def op_noise(state, P, ctx, rng):
    rgb = state['rgb']
    n = rng.normal(0, P.get('sigma', 5), rgb.shape[:2]).astype(np.float32)
    if P.get('chroma', 0):
        state['rgb'] = rgb + n[..., None] + rng.normal(0, P['chroma'], rgb.shape).astype(np.float32)
    else:
        state['rgb'] = rgb + n[..., None]


def op_saltpepper(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    n = int(P.get('amount', 0.001) * h * w)
    ys = rng.integers(0, h, n)
    xs = rng.integers(0, w, n)
    vals = np.where(rng.random(n) < 0.55, 20.0, 250.0).astype(np.float32)
    rgb[ys, xs] = vals[:, None]


def op_speckle(state, P, ctx, rng):
    rgb = state['rgb']
    h, w = rgb.shape[:2]
    sc = ctx['dpi'] / 300
    n = int(P.get('per_mpx', 100) * (w * h) / 1e6)
    for _ in range(n):
        r = rng.uniform(0.6, 2.2) * sc
        cy, cx = rng.integers(0, h), rng.integers(0, w)
        y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
        x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
        rgb[y0:y1, x0:x1][mask] = 25 + rng.uniform(0, 60)


def op_contrast(state, P, ctx, rng):
    rgb = state['rgb']
    g, o = P.get('gain', 1.0), P.get('offset', 0.0)
    state['rgb'] = (rgb - 128) * g + 128 + o


OPS = {k[3:]: v for k, v in globals().items() if k.startswith('op_')}


# ------------------------------------------------------------------ document

def degrade_document(pages, recipe, seed, dpi, anchors=None, staff_ext=None):
    """pages: list of uint8 gray arrays at `dpi`.  Returns (images, out_dpi, log)."""
    ops = recipe['ops']
    mode = recipe.get('mode', 'rgb')            # rgb | gray | bilevel
    spread = recipe.get('spread')               # None | {'pairs': [[0,1]], 'gap_mm': 0, 'gutter': 0.5}
    covs = [1 - p.astype(np.float32) / 255 for p in pages]
    states, ctxs = [], []
    first_geom = next((k for k, o in enumerate(ops) if o['op'] in GEOM_OPS), len(ops))
    log = []
    for k, cov in enumerate(covs):
        rng = np.random.default_rng([seed, k])
        ctx = {'dpi': dpi, 'page': k, 'anchors': (anchors[k] if anchors and k < len(anchors) else []),
               'staff_extent': (staff_ext[k] if staff_ext and k < len(staff_ext) else None), 'log': [],
               'reverse_cov': covs[(k + 1) % len(covs)] if len(covs) > 1 else None}
        st = {'cov': cov}
        for o in ops[:first_geom]:
            if 'pages' in o and k not in o['pages']:
                continue
            if 'cov' in st and o['op'] not in COV_OPS:
                op_paper(st, {}, ctx, rng)
            OPS[o['op']](st, o, ctx, rng)
        if 'cov' in st:
            op_paper(st, {}, ctx, rng)
        states.append(st)
        ctxs.append((ctx, rng))
    # 2-up spreads
    units = []
    if spread:
        used = set()
        for a, b in spread['pairs']:
            A, B = states[a]['rgb'], states[b]['rgb']
            h = max(A.shape[0], B.shape[0])
            gap = int(spread.get('gap_mm', 0) * dpi / 25.4)
            canvas = np.ones((h, A.shape[1] + B.shape[1] + gap, 3), np.float32) * np.array(fill3(spread.get('fill', 60)),
                                                                                           np.float32)
            canvas[:A.shape[0], :A.shape[1]] = A
            canvas[:B.shape[0], A.shape[1] + gap:] = B
            c = A.shape[1] + gap // 2
            gw = int(spread.get('gutter_width', 0.05) * canvas.shape[1])
            prof = np.linspace(1, 0, gw, dtype=np.float32) ** 1.8 * spread.get('gutter', 0.55)
            canvas[:, c:c + gw] *= (1 - prof)[None, :, None]
            canvas[:, c - gw:c] *= (1 - prof[::-1])[None, :, None]
            units.append(({'rgb': canvas, 'paper': states[a].get('paper')}, ctxs[a], [a, b]))
            used.update([a, b])
        for k in range(len(states)):
            if k not in used:
                units.append((states[k], ctxs[k], [k]))
        units.sort(key=lambda u: u[2][0])
    else:
        units = [(states[k], ctxs[k], [k]) for k in range(len(states))]
    out = []
    out_dpi = None
    for st, (ctx, rng), pidx in units:
        for o in ops[first_geom:]:
            if 'pages' in o and not (set(o['pages']) & set(pidx)):
                continue
            OPS[o['op']](st, o, ctx, rng)
        rgb = np.clip(st['rgb'], 0, 255)
        if mode == 'bilevel':
            b = recipe.get('binarize', {})
            lum = rgb.mean(axis=2)
            if b.get('pre_blur'):
                lum = gblur(lum, b['pre_blur'] * ctx['dpi'] / 300)
            if b.get('noise'):
                lum = lum + rng.normal(0, b['noise'], lum.shape)
            img = Image.fromarray(((lum > b.get('thr', 150)) * 255).astype(np.uint8)).convert('1', dither=Image.NONE)
        elif mode == 'gray':
            img = Image.fromarray(rgb.mean(axis=2).astype(np.uint8), mode='L')
        else:
            img = to_pil(rgb)
        out.append(img)
        out_dpi = ctx['dpi']
        log.append({'pages': pidx, 'size_px': list(img.size), 'events': ctx['log']})
    return out, out_dpi, log


def save_pdf(images, dpi, out_pdf, fmt='jpeg', quality=60, jpeg_passes=1):
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if fmt == 'jpeg' and im.mode != '1':
                cur = im
                for _ in range(jpeg_passes - 1):
                    b2 = io.BytesIO()
                    cur.save(b2, 'JPEG', quality=max(10, quality + 15))
                    b2.seek(0)
                    cur = Image.open(b2).convert(im.mode)
                fn = os.path.join(td, f'p{k:03d}.jpg')
                cur.save(fn, 'JPEG', quality=quality, dpi=(round(dpi), round(dpi)), optimize=True)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(round(dpi), round(dpi)), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{round(dpi)}dpi', '-o', out_pdf] + files, check=True,
                       capture_output=True, timeout=600)
