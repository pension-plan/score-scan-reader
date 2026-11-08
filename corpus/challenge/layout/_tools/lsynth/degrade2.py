"""Scan / photocopy / phone-capture simulation for multi-page items (numpy + Pillow).

degrade_document(pages, P, seed) -> (list of PIL images, list of op records)

pages: list of uint8 gray arrays (white paper, black ink) rendered at P['dpi'].
P (all optional except dpi):
  mode          'rgb' | 'gray' | 'bw'
  paper_rgb     paper colour (yellowed / coloured paper), ink_rgb
  texture       paper fibre amplitude (grey levels)
  ink_weight    +n dilate / -n erode (3x3 passes)      ink_dropout  fraction of faded strokes
  pencil        {'circles': n, 'marks': n, 'texts': [..], 'lines': n}  graphite annotations (circled notes ...)
  foxing        {'n': spots}      coffee {'n': rings, 'r': radius as page-width fraction}
  punch_holes   {'n': 2|3, 'side': 'left'|'top', 'level': grey seen through the hole}
  staple        {'corner': 'tl'|'tr'}
  curl          {'side': 'left'|'right'|'inner', 'amp': px@300dpi, 'width': page fraction}
  wave          {'amp': px@300dpi, 'period': page widths}
  gutter        {'side': 'left'|'right'|'inner', 'width': frac, 'dark': 0..1}
  bleed         strength of the mirrored reverse page (next page of the item)
  spread        list of [i, j] page pairs combined into one 2-up image (book opening)
  rotate        degrees (global) ;  rotate_pages {page: deg} overrides
  scale_pages   {page: factor} content scale mismatch between pages
  phone         {'margin': f, 'bg': grey, 'jitter': f}   perspective / keystone
  gradient, blotch, vignette   lighting
  halftone      {'period': px, 'angle': deg, 'amp': grey, 'shrink': f}  print screen + resample -> moire
  blur          gaussian sigma (px@300dpi);  motion_blur {'len': px@300dpi, 'angle': deg}
  noise         gaussian sigma;  saltpepper fraction;  speckle per megapixel
  binarize      threshold (photocopy), binarize_noise
  crop          {'left'|'right'|'top'|'bottom': fraction of width/height cut away}
  page_rotate   {page: 90|180|270} applied to the output image (page fed rotated)
  out_dpi       final resolution (resampled from dpi)
  format        'jpeg' | 'png' | 'png1';  jpeg quality
"""
from __future__ import annotations

import io
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None
HAND_FONT = '/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf'


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def remap(img, xs, ys, fill=0.0):
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
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)).tolist()


def _blur(arr, sigma):
    """gaussian blur of a float array (values 0..1 or 0..255) via 8-bit PIL (quantisation is harmless here)"""
    if sigma <= 0:
        return arr
    unit = float(arr.max()) <= 1.0 + 1e-6
    k = 255.0 if unit else 1.0
    if arr.ndim == 2:
        im = Image.fromarray(np.clip(arr * k, 0, 255).astype(np.uint8), 'L')
    else:
        im = Image.fromarray(np.clip(arr * k, 0, 255).astype(np.uint8), 'RGB')
    return np.asarray(im.filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32) / k


# ---------------------------------------------------------------- paper-space layers

def staff_rows(cov):
    """rows that belong to staff lines (long horizontal ink runs)"""
    rowsum = (cov > 0.5).mean(axis=1)
    return np.where(rowsum > 0.35)[0]


def ink_points(cov, rng, n, sc):
    """random points on dense ink blobs near staves (noteheads-ish)"""
    h, w = cov.shape
    rows = staff_rows(cov)
    if len(rows) == 0:
        return []
    small = cov[::4, ::4]
    pts = []
    tries = 0
    while len(pts) < n and tries < 5000:
        tries += 1
        y = int(rng.choice(rows)) + int(rng.integers(-int(25 * sc), int(25 * sc) + 1))
        x = int(rng.integers(int(0.12 * w), int(0.92 * w)))
        if not (0 <= y < h):
            continue
        y4, x4 = y // 4, x // 4
        win = small[max(0, y4 - 3):y4 + 4, max(0, x4 - 3):x4 + 4]
        if win.size and win.mean() > 0.45:
            if all(abs(x - a) > 80 * sc or abs(y - b) > 80 * sc for a, b in pts):
                pts.append((x, y))
    return pts


def pencil_layer(cov, spec, rng, sc):
    h, w = cov.shape
    im = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(im)
    width = max(2, int(round(3.0 * sc)))
    ops = {'circled': [], 'marks': [], 'texts': [], 'lines': 0}
    for (x, y) in ink_points(cov, rng, spec.get('circles', 0), sc):
        rx, ry = rng.uniform(28, 40) * sc, rng.uniform(22, 32) * sc
        pts = []
        start = rng.uniform(0, 2 * math.pi)
        for k in range(48):
            t = start + 2 * math.pi * 1.12 * k / 47
            jit = 1 + rng.normal(0, 0.03)
            pts.append((x + rx * jit * math.cos(t), y + ry * jit * math.sin(t)))
        dr.line(pts, fill=int(rng.uniform(200, 250)), width=width)
        ops['circled'].append([x, y])
    try:
        font = ImageFont.truetype(HAND_FONT, int(rng.uniform(34, 44) * sc))
    except OSError:
        font = ImageFont.load_default()
    rows = staff_rows(cov)
    for txt in spec.get('texts', []):
        if len(rows) == 0:
            break
        y = int(rng.choice(rows)) - int(rng.uniform(40, 70) * sc)
        x = int(rng.uniform(0.15, 0.8) * w)
        dr.text((x, max(0, y)), txt, fill=int(rng.uniform(200, 250)), font=font)
        ops['texts'].append([txt, x, y])
    for _ in range(spec.get('marks', 0)):   # breath marks / fingering ticks
        if len(rows) == 0:
            break
        y = int(rng.choice(rows)) - int(rng.uniform(30, 60) * sc)
        x = int(rng.uniform(0.12, 0.92) * w)
        s = rng.uniform(10, 16) * sc
        dr.line([(x - s, y - s), (x, y + s * 0.4), (x + s, y - s * 1.2)], fill=int(rng.uniform(200, 250)),
                width=width)
        ops['marks'].append([x, y])
    for _ in range(spec.get('lines', 0)):    # long wobbly underline / arrow
        if len(rows) == 0:
            break
        y = int(rng.choice(rows)) + int(rng.uniform(40, 70) * sc)
        x0 = rng.uniform(0.1, 0.5) * w
        x1 = x0 + rng.uniform(0.15, 0.35) * w
        pts = [(x0 + (x1 - x0) * k / 30, y + 4 * sc * math.sin(k / 3.0) + rng.normal(0, 1.2 * sc)) for k in range(31)]
        dr.line(pts, fill=int(rng.uniform(190, 240)), width=width)
        ops['lines'] += 1
    arr = np.asarray(im, dtype=np.float32) / 255.0
    arr = _blur(arr, 0.8 * sc)
    grain = rng.random(arr.shape).astype(np.float32)
    arr = arr * (0.75 + 0.25 * grain)
    return arr, ops


def stain_layer(shape, P, rng, sc):
    """multiplicative RGB stain field (coffee rings, foxing)"""
    h, w = shape
    mul = np.ones((h, w, 3), np.float32)
    rec = {}
    if P.get('coffee'):
        c = P['coffee']
        rec['coffee'] = []
        for _ in range(c.get('n', 1)):
            r0 = c.get('r', 0.1) * w
            cx = rng.uniform(0.15, 0.85) * w
            cy = rng.uniform(0.15, 0.85) * h
            y0, y1 = int(max(0, cy - 1.4 * r0)), int(min(h, cy + 1.4 * r0))
            x0, x1 = int(max(0, cx - 1.4 * r0)), int(min(w, cx + 1.4 * r0))
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            ang = np.arctan2(yy - cy, xx - cx)
            wob = 1 + 0.06 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.04 * np.sin(7 * ang + rng.uniform(0, 6))
            rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (r0 * wob)
            ring = np.exp(-((rr - 1.0) / 0.035) ** 2) * 0.55 + np.where(rr < 1, 0.18, 0) * (0.6 + 0.4 * rr)
            ring *= c.get('strength', 1.0)
            tint = np.array([0.18, 0.32, 0.55], np.float32)    # brown: absorbs blue most
            mul[y0:y1, x0:x1] *= (1 - ring[..., None] * tint[None, None, :])
            rec['coffee'].append([round(cx), round(cy), round(r0)])
    if P.get('foxing'):
        n = P['foxing'].get('n', 30)
        rec['foxing'] = n
        for _ in range(n):
            r = rng.uniform(2, 9) * sc
            cx, cy = rng.uniform(0, w), rng.uniform(0, h)
            y0, y1 = int(max(0, cy - 3 * r)), int(min(h, cy + 3 * r))
            x0, x1 = int(max(0, cx - 3 * r)), int(min(w, cx + 3 * r))
            if y1 <= y0 or x1 <= x0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)))
            s = rng.uniform(0.25, 0.6)
            tint = np.array([0.25, 0.45, 0.7], np.float32) * s
            mul[y0:y1, x0:x1] *= (1 - g[..., None] * tint[None, None, :])
    return mul, rec


def hole_mask(shape, P, rng, sc):
    """1 where the page has a punch hole (background shows through)."""
    h, w = shape
    m = np.zeros((h, w), np.float32)
    ph = P['punch_holes']
    n = ph.get('n', 3)
    side = ph.get('side', 'left')
    r = 3.0 / 25.4 * 300 * sc          # 6 mm diameter
    off = 11.0 / 25.4 * 300 * sc       # centre 11 mm from the edge
    if n == 2:
        fr = [0.5 - 0.135, 0.5 + 0.135]    # 80 mm spacing on A4
    else:
        fr = [0.5 - 0.365, 0.5, 0.5 + 0.365]
    centers = []
    for f in fr:
        if side == 'left':
            centers.append((off, f * h))
        else:
            centers.append((f * w, off))
    for cx, cy in centers:
        y0, y1 = int(cy - r - 3), int(cy + r + 4)
        x0, x1 = int(max(0, cx - r - 3)), int(cx + r + 4)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        m[y0:y1, x0:x1] = np.clip(r + 0.5 - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2), 0, 1)
    return m, [[round(a), round(b)] for a, b in centers]


def staple_overlay(rgb, P, rng, sc):
    h, w, _ = rgb.shape
    corner = P['staple'].get('corner', 'tl')
    L = 13.0 / 25.4 * 300 * sc
    cx = 0.06 * w if corner == 'tl' else 0.94 * w
    cy = 0.04 * h
    ang = math.radians(35 if corner == 'tl' else -35)
    im = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(im)
    dx, dy = math.cos(ang) * L / 2, math.sin(ang) * L / 2
    dr.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=255, width=max(2, int(4 * sc)))
    m = _blur(np.asarray(im, dtype=np.float32) / 255.0, 0.8 * sc)
    # metallic grey with a shadow
    sh = np.roll(m, (int(3 * sc), int(3 * sc)), axis=(0, 1))
    rgb *= (1 - 0.35 * sh[..., None])
    rgb = rgb * (1 - m[..., None]) + m[..., None] * np.array([120, 122, 130], np.float32)
    return rgb, [round(cx), round(cy)]


# ---------------------------------------------------------------- stage A (paper space)

def stage_a(page, back, P, rng, sc, inner_side):
    """page/back: uint8 gray.  Returns (rgb float32 HxWx3, record)."""
    rec = []
    cov = 1.0 - page.astype(np.float32) / 255.0
    ink = P.get('ink_weight', 0)
    if ink:
        pil = Image.fromarray(page)
        for _ in range(abs(ink)):
            pil = pil.filter(ImageFilter.MinFilter(3) if ink > 0 else ImageFilter.MaxFilter(3))
        cov = 1.0 - np.asarray(pil, dtype=np.float32) / 255.0
        rec.append(['ink_weight', ink])
    if P.get('ink_dropout'):
        f = smooth_field(cov.shape, rng, (40, 30), 0, 1)
        fine = rng.random(cov.shape).astype(np.float32)
        drop = (f > 1 - P['ink_dropout']) & (fine < 0.5)
        cov = np.where(drop, cov * 0.4, cov)
        rec.append(['faded_ink', P['ink_dropout']])
    h, w = cov.shape
    pen = None
    if P.get('pencil'):
        pen, prec = pencil_layer(cov, P['pencil'], rng, sc)
        rec.append(['pencil_annotations', prec])
    holes = None
    if P.get('punch_holes'):
        holes, hrec = hole_mask(cov.shape, P, rng, sc)
        rec.append(['punch_holes', {'side': P['punch_holes'].get('side', 'left'), 'centers_px': hrec}])
    bcov = None
    if P.get('bleed') and back is not None:
        bc = 1.0 - back.astype(np.float32) / 255.0
        bc = bc[:, ::-1]
        if bc.shape != cov.shape:
            bc = np.asarray(Image.fromarray(bc, mode='F').resize((w, h)), dtype=np.float32)
        bcov = _blur(bc, 2.5 * sc)
        shift = int(rng.integers(-20, 21) * sc)
        bcov = np.roll(bcov, shift, axis=0)
        rec.append(['bleed_through', {'strength': P['bleed'], 'shift_px': shift}])
    # geometry in paper space: curl / wave
    curl = P.get('curl')
    if curl or P.get('wave'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dy = np.zeros_like(xx)
        dx = np.zeros_like(xx)
        if curl:
            side = curl.get('side', 'left')
            if side == 'inner':
                side = inner_side or 'left'
            amp = curl['amp'] * sc
            width = curl.get('width', 0.25) * w
            t = np.clip((width - xx) / width, 0, 1) if side == 'left' else np.clip((xx - (w - width)) / width, 0, 1)
            dy += amp * t ** 2 * ((yy - h / 2) / (h / 2))
            dx += (amp * 0.6) * t ** 2 * (1 if side == 'left' else -1)
            rec.append(['page_curl', dict(curl, side=side)])
        if P.get('wave'):
            wv = P['wave']
            dy += wv['amp'] * sc * np.sin(2 * np.pi * xx / (wv.get('period', 1.3) * w) + wv.get('phase', 0.3))
            rec.append(['wavy_warp', wv])
        xs, ys = xx - dx, yy - dy
        del xx, yy, dx, dy
        cov = remap(cov, xs, ys, 0.0)
        if pen is not None:
            pen = remap(pen, xs, ys, 0.0)
        if holes is not None:
            holes = remap(holes, xs, ys, 0.0)
        if bcov is not None:
            bcov = remap(bcov, xs, ys, 0.0)
        del xs, ys
    # composite
    paper = np.array(P.get('paper_rgb', (247, 246, 243)), np.float32)
    inkc = np.array(P.get('ink_rgb', (22, 22, 26)), np.float32)
    rgb = np.empty((h, w, 3), np.float32)
    rgb[:] = paper
    if P.get('texture'):
        t = P['texture']
        fld = t * smooth_field((h, w), rng, (14, 10)) + t * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        rgb += fld[..., None]
        rec.append(['paper_texture', t])
    if P.get('paper_rgb'):
        rec.append(['paper_colour', list(P['paper_rgb'])])
    if P.get('coffee') or P.get('foxing'):
        mul, srec = stain_layer((h, w), P, rng, sc)
        rgb *= mul
        del mul
        rec.append(['stains', srec])
    if bcov is not None:
        b = np.clip(P['bleed'] * bcov, 0, 1)[..., None]
        rgb = rgb * (1 - b) + (rgb * 0.55) * b
    c3 = cov[..., None]
    rgb = rgb * (1 - c3) + inkc[None, None, :] * c3
    if pen is not None:
        graphite = np.array([88, 88, 96], np.float32)
        p3 = np.clip(pen, 0, 1)[..., None]
        rgb = rgb * (1 - p3) + graphite * p3
    if holes is not None:
        lvl = P['punch_holes'].get('level', 35)
        # shadow ring at the hole edge
        sh = _blur(holes, 3 * sc)
        rgb *= (1 - 0.35 * np.clip(sh - holes, 0, 1))[..., None]
        rgb = rgb * (1 - holes[..., None]) + lvl * holes[..., None]
    if P.get('staple'):
        rgb, spos = staple_overlay(rgb, P, rng, sc)
        rec.append(['staple', {'corner': P['staple'].get('corner', 'tl'), 'pos_px': spos}])
    g = P.get('gutter')
    if g:
        side = g.get('side', 'left')
        if side == 'inner':
            side = inner_side or 'left'
        gw = int(g.get('width', 0.06) * w)
        prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * g.get('dark', 0.55)
        if side == 'left':
            rgb[:, :gw] *= (1 - prof)[None, :, None]
        else:
            rgb[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
        rec.append(['gutter_shadow', dict(g, side=side)])
    return rgb, rec


# ---------------------------------------------------------------- stage B (capture)

def rotate_scale(rgb, deg, scale, bg):
    h, w, _ = rgb.shape
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - cx) / scale, (yy - cy) / scale
    xs = cx + c * dx - s * dy
    ys = cy + s * dx + c * dy
    del xx, yy, dx, dy
    out = np.stack([remap(rgb[..., k], xs, ys, bg) for k in range(3)], axis=-1)
    return out


def stage_b(rgb, P, rng, sc, page_idx):
    rec = []
    h, w, _ = rgb.shape
    bg = P.get('bg', 250.0)
    deg = P.get('rotate_pages', {}).get(page_idx, P.get('rotate', 0.0))
    scl = P.get('scale_pages', {}).get(page_idx, 1.0)
    if deg or scl != 1.0:
        rgb = rotate_scale(rgb, deg, scl, bg)
        if deg:
            rec.append(['skew_rotation_deg', deg])
        if scl != 1.0:
            rec.append(['scale', scl])
    if P.get('phone'):
        ph = P['phone']
        m = int(ph.get('margin', 0.05) * w)
        bgp = ph.get('bg', 70)
        H, W = h + 2 * m, w + 2 * m
        canvas = np.empty((H, W, 3), np.float32)
        tint = np.array(ph.get('bg_rgb', (bgp, bgp * 0.95, bgp * 0.9)), np.float32)
        canvas[:] = tint
        canvas += 12 * smooth_field((H, W), rng, (4, 4))[..., None]
        canvas[m:m + h, m:m + w] = rgb
        jit = ph.get('jitter', 0.03)
        dst = [(0, 0), (W, 0), (W, H), (0, H)]
        src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in dst]
        if ph.get('keystone'):
            k = ph['keystone'] * W
            src[0] = (src[0][0] - k, src[0][1])
            src[1] = (src[1][0] + k, src[1][1])
        coeffs = perspective_coeffs(src, dst)
        pil = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), 'RGB')
        pil = pil.transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC,
                            fillcolor=tuple(int(x) for x in tint))
        rgb = np.asarray(pil, dtype=np.float32)
        h, w, _ = rgb.shape
        rec.append(['perspective_phone', dict(ph, corners_src=[[round(a), round(b)] for a, b in src])])
    if P.get('gradient'):
        gpar = P['gradient']
        ang = rng.uniform(0, 2 * np.pi)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        t = ((xx / w - 0.5) * np.cos(ang) + (yy / h - 0.5) * np.sin(ang)) + 0.5
        rgb *= (1 - gpar * np.clip(t, 0, 1))[..., None]
        del yy, xx, t
        rec.append(['lighting_gradient', {'strength': gpar, 'angle_deg': round(math.degrees(ang), 1)}])
    if P.get('blotch'):
        rgb *= (1 - P['blotch'] * np.clip(smooth_field((h, w), rng, (5, 4), -0.5, 1), 0, 1))[..., None]
        rec.append(['uneven_lighting', P['blotch']])
    if P.get('vignette'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx / w - 0.5)) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
        rgb *= (1 - P['vignette'] * r ** 2)[..., None]
        del yy, xx, r
        rec.append(['vignette', P['vignette']])
    if P.get('halftone'):
        ht = P['halftone']
        per = ht.get('period', 4.0) * sc
        a = math.radians(ht.get('angle', 45))
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = (xx * math.cos(a) + yy * math.sin(a)) * 2 * math.pi / per
        v = (-xx * math.sin(a) + yy * math.cos(a)) * 2 * math.pi / per
        scr = np.cos(u) * np.cos(v)
        del xx, yy, u, v
        lum = rgb.mean(axis=2)
        mid = 1 - np.abs(lum / 255.0 - 0.6) / 0.6
        rgb += (ht.get('amp', 25) * scr * np.clip(mid, 0.25, 1))[..., None]
        shrink = ht.get('shrink', 0.8)
        pil = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), 'RGB')
        pil = pil.resize((int(w * shrink), int(h * shrink)), Image.NEAREST).resize((w, h), Image.BILINEAR)
        rgb = np.asarray(pil, dtype=np.float32)
        rec.append(['halftone_moire', ht])
    if P.get('blur'):
        rgb = _blur(rgb, P['blur'] * sc)
        rec.append(['focus_blur_sigma', P['blur']])
    if P.get('motion_blur'):
        mb = P['motion_blur']
        L = max(2, int(mb['len'] * sc))
        a = math.radians(mb.get('angle', 0))
        acc = np.zeros_like(rgb)
        for k in range(L):
            o = k - L / 2
            acc += np.roll(rgb, (int(round(o * math.sin(a))), int(round(o * math.cos(a)))), axis=(0, 1))
        rgb = acc / L
        del acc
        rec.append(['motion_blur', mb])
    if P.get('noise'):
        rgb += rng.normal(0, P['noise'], rgb.shape[:2]).astype(np.float32)[..., None]
        if P.get('mode', 'rgb') == 'rgb':
            rgb += rng.normal(0, P['noise'] * 0.35, rgb.shape).astype(np.float32)
        rec.append(['gaussian_noise_sigma', P['noise']])
    if P.get('saltpepper'):
        n = int(P['saltpepper'] * h * w)
        ys = rng.integers(0, h, n)
        xs = rng.integers(0, w, n)
        vals = np.where(rng.random(n) < 0.6, 20.0, 250.0).astype(np.float32)
        rgb[ys, xs] = vals[:, None]
        rec.append(['salt_pepper', P['saltpepper']])
    if P.get('speckle'):
        n = int(P['speckle'] * (w * h) / 1e6)
        for _ in range(n):
            r = rng.uniform(0.6, 2.2) * sc
            cy, cx = rng.integers(0, h), rng.integers(0, w)
            y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
            x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
            rgb[y0:y1, x0:x1][mask] = 25 + rng.uniform(0, 60)
        rec.append(['speckles_per_mpx', P['speckle']])
    rgb = np.clip(rgb, 0, 255)
    mode = P.get('mode', 'rgb')
    if mode == 'bw' or P.get('binarize'):
        lum = rgb.mean(axis=2)
        thr = P.get('binarize', 128)
        if P.get('binarize_noise'):
            lum = lum + rng.normal(0, P['binarize_noise'], lum.shape)
        img = Image.fromarray(((lum > thr) * 255).astype(np.uint8), 'L').convert('1', dither=Image.NONE)
        rec.append(['binarized_photocopy', {'threshold': thr, 'noise': P.get('binarize_noise', 0)}])
    elif mode == 'gray':
        img = Image.fromarray((rgb @ np.array([0.299, 0.587, 0.114], np.float32)).astype(np.uint8), 'L')
    else:
        img = Image.fromarray(rgb.astype(np.uint8), 'RGB')
    cr = P.get('crop')
    if cr:
        W0, H0 = img.size
        box = (int(cr.get('left', 0) * W0), int(cr.get('top', 0) * H0), W0 - int(cr.get('right', 0) * W0),
               H0 - int(cr.get('bottom', 0) * H0))
        img = img.crop(box)
        rec.append(['crop_edges', cr])
    return img, rec


def finish(img, P, page_idx, rec):
    rot = P.get('page_rotate', {}).get(page_idx)
    if rot:
        img = img.rotate(rot, expand=True)
        rec.append(['page_rotated_deg', rot])
    if P.get('out_dpi') and P['out_dpi'] != P['dpi']:
        f = P['out_dpi'] / P['dpi']
        mode = img.mode
        im2 = img.convert('L') if mode == '1' else img
        im2 = im2.resize((max(1, int(img.size[0] * f)), max(1, int(img.size[1] * f))), Image.LANCZOS)
        img = im2.point(lambda v: 255 if v > 127 else 0).convert('1') if mode == '1' else im2
        rec.append(['resampled_dpi', [P['dpi'], P['out_dpi']]])
    return img


def ink_crop(page, P, side, mm):
    """crop fraction that cuts `mm` millimetres into the outermost ink (staff ends) on `side`"""
    h, w = page.shape
    cols = np.where((page < 128).sum(axis=0) > 2)[0]
    rows = np.where((page < 128).sum(axis=1) > 2)[0]
    px = mm / 25.4 * P['dpi']
    if side == 'right':
        return max(0.0, (w - 1 - cols.max() + px) / w)
    if side == 'left':
        return max(0.0, (cols.min() + px) / w)
    if side == 'bottom':
        return max(0.0, (h - 1 - rows.max() + px) / h)
    return max(0.0, (rows.min() + px) / h)


def degrade_document(pages, P, seed):
    """Returns (images, per-image records).  Output images may combine pages (spreads)."""
    if P.get('crop_ink'):
        outs = []
        rng0 = np.random.default_rng(seed)
        for k, pg in enumerate(pages):
            P2 = dict(P)
            P2['crop'] = {side: round(ink_crop(pg, P, side, mm), 4) for side, mm in P['crop_ink'].items()}
            P2.pop('crop_ink')
            sub = degrade_document([pg] if not P.get('bleed') else [pg] + [pages[(k + 1) % len(pages)]],
                                   dict(P2, page_rotate={0: P.get('page_rotate', {}).get(k)} if
                                        P.get('page_rotate', {}).get(k) else {},
                                        rotate_pages={0: P.get('rotate_pages', {}).get(k, P.get('rotate', 0.0))},
                                        scale_pages={0: P.get('scale_pages', {}).get(k, 1.0)}),
                                   int(rng0.integers(0, 2 ** 31)))
            img, rec, src = sub[0]
            rec.insert(0, ['crop_ink_target_mm_into_staff_ends', P['crop_ink']])
            outs.append((img, rec, [k + 1]))
        return outs
    rng = np.random.default_rng(seed)
    sc = P['dpi'] / 300.0
    n = len(pages)
    spreads = {tuple(s) for s in P.get('spread', [])}
    in_spread = {i: s for s in spreads for i in s}
    outputs = []
    i = 0
    while i < n:
        if i in in_spread and in_spread[i][0] == i:
            a, b = in_spread[i]
            parts = []
            recs = []
            for k, inner in ((a, 'right'), (b, 'left')):
                back = pages[k + 1] if k + 1 < n else (pages[k - 1] if k > 0 else pages[k])
                rgb, r = stage_a(pages[k], back, P, rng, sc, inner)
                parts.append(rgb)
                recs += [[f'p{k + 1}'] + x for x in r]
            hh = max(p.shape[0] for p in parts)
            parts = [np.pad(p, ((0, hh - p.shape[0]), (0, 0), (0, 0)), constant_values=250) for p in parts]
            rgb = np.concatenate(parts, axis=1)
            img, r2 = stage_b(rgb, P, rng, sc, a)
            recs.append(['spread_2up', [a + 1, b + 1]])
            img = finish(img, P, a, r2)
            outputs.append((img, recs + r2, [a + 1, b + 1]))
            i = b + 1
            continue
        back = pages[i + 1] if i + 1 < n else (pages[i - 1] if i > 0 else pages[i])
        rgb, r = stage_a(pages[i], back, P, rng, sc, 'left' if i % 2 else 'right')
        img, r2 = stage_b(rgb, P, rng, sc, i)
        rec = r + r2
        img = finish(img, P, i, rec)
        outputs.append((img, rec, [i + 1]))
        i += 1
    return outputs


def save_pdf(images, dpi, out_pdf, fmt='jpeg', quality=75):
    import os
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if fmt == 'jpeg' and im.mode != '1':
                fn = os.path.join(td, f'p{k:03d}.jpg')
                im.save(fn, 'JPEG', quality=quality, dpi=(dpi, dpi), optimize=True)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{dpi}dpi', '-o', out_pdf] + files, check=True,
                       capture_output=True)
