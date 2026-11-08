"""Scan-damage simulator for the degradation challenge set (numpy + Pillow only).

A damage spec (dict, JSON-serialisable, recorded verbatim in meta.json) is
applied in fixed stages:

  1. content  (per page, page coordinates, on the clean grey raster):
       ink weight / fading / halftone screen, paper colour + texture + fibres +
       age darkening, bleed-through of a reverse page, coffee stains, foxing,
       highlighter, pencil / pen annotations (circled notes, fingerings, text,
       breath marks, arrows), punch holes, staple, dog-ear fold, crop
  2. page_geom (per page; spec['page_overrides'][i] replaces / extends it):
       curl, wave, scale (scale mismatch), rot90 (exact 90/180/270), gutter
  3. assembly: separate pages, or a 2-up double-page spread
  4. global (ordered list, per output image): bed (scanner bed margin),
       rotate (any angle, expand), perspective (phone), lighting (gradient,
       vignette, blotch, shadow, gutter_center) - the page mask is composited
       onto the background before the first non-geometric op - then sensor
       ops: blur, motion, noise, saltpepper, speckle, halftone resample,
       binarize
  5. output: mode L / RGB / 1, JPEG quality / passes / chroma subsampling or PNG

Images are float32 RGB (0..255) plus a float32 page mask (1 = paper).
"""
from __future__ import annotations

import glob
import io
import math
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from synth.degrade import perspective_coeffs, remap, smooth_field

Image.MAX_IMAGE_PIXELS = None
HAND_FONT = '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrechorus-mediumitalic.otf'


def mm2px(mm, dpi):
    return float(mm) * dpi / 25.4


# ---------------------------------------------------------------- rendering + page analysis
def render_gray(pdf, dpi, workdir, tag):
    prefix = os.path.join(workdir, f'{tag}-r{dpi}')
    for f in glob.glob(prefix + '-*.pgm'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=900)
    files = sorted(glob.glob(prefix + '-*.pgm'))
    pages = [np.array(Image.open(f), dtype=np.uint8) for f in files]
    for f in files:
        os.remove(f)
    return pages


def _runs(b):
    d = np.diff(np.concatenate([[0], b.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def analyse_page(gray, dpi):
    """Staff geometry of a clean page (in mm): staves with top/bottom line,
    staff space, x extent, safe crop gaps, and notehead-like candidate points."""
    ink = gray < 150
    h, w = ink.shape
    frac = ink.mean(1)
    rows = np.where(frac > 0.3)[0]
    lines = []
    for a, b in _runs(np.isin(np.arange(h), rows)):
        lines.append((a + b - 1) / 2.0)
    staves = []
    i = 0
    while i + 4 < len(lines):
        c = lines[i:i + 5]
        d = np.diff(c)
        if d.max() - d.min() <= max(2.0, 0.2 * d.mean()) and d.mean() < h * 0.03:
            sp = float(d.mean())
            x0s, x1s = [], []
            for cy in c:
                r = int(round(cy))
                best = max(_runs(ink[r]), key=lambda ab: ab[1] - ab[0])
                x0s.append(best[0])
                x1s.append(best[1])
            staves.append({'top': float(c[0]), 'bottom': float(c[4]), 'space': sp, 'lines': [float(x) for x in c],
                           'x0': int(np.median(x0s)), 'x1': int(np.median(x1s))})
            i += 5
        else:
            i += 1
    # safe crop gaps: distance from staff start to first non-barline ink, and
    # from last non-barline ink to staff end
    left_gaps, right_gaps = [], []
    cands = []
    for st in staves:
        top, bot = int(round(st['top'])), int(round(st['bottom']))
        band = ink[top:bot + 1].copy()
        for cy in st['lines']:
            r = int(round(cy)) - top
            band[max(0, r - 2):r + 3] = False
        n_rows = band.any(1).sum() if band.any() else 1
        cnt = band.sum(0)
        full = cnt >= 0.95 * max(1, (band.shape[0] - 5 * 5))
        x0, x1 = st['x0'], st['x1']
        x = x0
        while x < x1 and (cnt[x] == 0 or full[x]):
            x += 1
        left_gaps.append(x - x0)
        x = x1 - 1
        while x > x0 and (cnt[x] == 0 or full[x]):
            x -= 1
        right_gaps.append(x1 - 1 - x)
        # notehead candidates: dense blobs ~ 1 x 1.2 staff spaces, staff lines removed
        sp = st['space']
        y0 = max(0, int(top - 2.5 * sp))
        y1 = min(h, int(bot + 2.5 * sp))
        reg = ink[y0:y1, x0:x1].copy()
        for cy in st['lines']:
            r = int(round(cy)) - y0
            reg[max(0, r - 1):r + 2] = False
        bh, bw = max(2, int(0.8 * sp)), max(2, int(1.0 * sp))
        S = np.pad(reg.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        box = S[bh:, bw:] - S[:-bh, bw:] - S[bh:, :-bw] + S[:-bh, :-bw]
        dens = box / float(bh * bw)
        ys, xs = np.where(dens > 0.55)
        if len(ys):
            step = max(1, len(ys) // 400)
            for yy, xx in zip(ys[::step], xs[::step]):
                cands.append((float(x0 + xx + bw / 2), float(y0 + yy + bh / 2), sp))
        del reg, S, box, dens
    k = 25.4 / dpi
    out = {'dpi': dpi, 'size_mm': [w * k, h * k],
           'staves': [{'top': s['top'] * k, 'bottom': s['bottom'] * k, 'space': s['space'] * k,
                       'lines': [x * k for x in s['lines']], 'x0': s['x0'] * k, 'x1': s['x1'] * k} for s in staves],
           'left_gap_mm': (min(left_gaps) * k) if left_gaps else 0.0,
           'right_gap_mm': (min(right_gaps) * k) if right_gaps else 0.0,
           'notes_mm': [(x * k, y * k, sp * k) for x, y, sp in cands]}
    ys, xs = np.where(gray < 160)
    if len(ys):
        out['ink_bbox_mm'] = [xs.min() * k, ys.min() * k, xs.max() * k, ys.max() * k]
    if staves:
        out['staff_x0_mm'] = min(s['x0'] for s in out['staves'])
        out['staff_x1_mm'] = max(s['x1'] for s in out['staves'])
        out['music_top_mm'] = min(s['top'] for s in out['staves'])
        out['music_bottom_mm'] = max(s['bottom'] for s in out['staves'])
    return out


# ---------------------------------------------------------------- helpers
def _rgb(c):
    if isinstance(c, (int, float)):
        return np.array([c, c, c], np.float32)
    return np.array(c, np.float32)


def _gauss(arr2d, sigma):
    if sigma <= 0:
        return arr2d
    lo, hi = float(arr2d.min()), float(arr2d.max())
    if hi - lo < 1e-6:
        return arr2d
    im = Image.fromarray(((arr2d - lo) / (hi - lo) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(sigma))
    return np.asarray(im, np.float32) / 255 * (hi - lo) + lo


def _blur_rgb(rgb, sigma):
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(sigma)), np.float32)


def _multiply_tint(rgb, alpha, color):
    """darken towards a stain colour: rgb *= 1 - alpha * (1 - color/255)"""
    c = 1.0 - _rgb(color) / 255.0
    rgb *= (1.0 - alpha[..., None] * c[None, None, :])
    return rgb


def _blob_field(shape, cx, cy, r, rng, wobble=0.12, nharm=5):
    """distance-like field d/r_theta (1.0 on the irregular outline)"""
    h, w = shape
    y0, y1 = max(0, int(cy - 1.6 * r)), min(h, int(cy + 1.6 * r) + 1)
    x0, x1 = max(0, int(cx - 1.6 * r)), min(w, int(cx + 1.6 * r) + 1)
    if y1 <= y0 or x1 <= x0:
        return None
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    th = np.arctan2(yy - cy, xx - cx)
    rad = np.ones_like(th)
    for k in range(2, 2 + nharm):
        rad += (wobble / k ** 0.7) * np.sin(k * th + rng.uniform(0, 2 * np.pi))
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (r * rad)
    return (y0, y1, x0, x1), d


# ---------------------------------------------------------------- stage 1: content
def content_stage(gray, C, dpi, rng, info, ctx, page_idx):
    """gray: clean page (uint8).  Returns rgb, mask, annotations list."""
    notes = []
    img = gray.astype(np.float32)
    h, w = img.shape
    sc = dpi / 300.0
    if C.get('ink_weight'):
        pil = Image.fromarray(gray)
        n = int(C['ink_weight'])
        for _ in range(abs(n)):
            pil = pil.filter(ImageFilter.MinFilter(3) if n > 0 else ImageFilter.MaxFilter(3))
        img = np.asarray(pil, np.float32)
    cov = 1.0 - img / 255.0
    if C.get('fade'):
        f = smooth_field(cov.shape, rng, (40, 30), 0, 1)
        fine = rng.random(cov.shape).astype(np.float32)
        drop = (f > 1 - C['fade']) & (fine < 0.55)
        cov = np.where(drop, cov * 0.35, cov)
        del f, fine, drop
    if C.get('halftone'):
        H = C['halftone']
        ss = 2
        big = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).resize((w * ss, h * ss), Image.BILINEAR),
                         np.float32) / 255.0
        tone = H.get('paper_tone', 0.10) + (H.get('ink_tone', 0.9) - H.get('paper_tone', 0.10)) * big
        period = (dpi * ss) / H['lpi']
        a = math.radians(H.get('angle', 45))
        yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
        u = (xx * math.cos(a) + yy * math.sin(a)) * (2 * np.pi / period)
        v = (-xx * math.sin(a) + yy * math.cos(a)) * (2 * np.pi / period)
        thr = 0.5 - 0.25 * (np.cos(u) + np.cos(v))
        del u, v, yy, xx
        dots = (tone > thr).astype(np.uint8) * 255
        del tone, thr, big
        # point-sample back to the scan grid (aliasing => moire)
        rs = H.get('rescale', 1.0)
        nw, nh = int(round(w * rs)), int(round(h * rs))
        small = Image.fromarray(dots).resize((nw, nh), Image.NEAREST)
        cov = np.asarray(small, np.float32) / 255.0
        if (nw, nh) != (w, h):
            canvas = np.zeros((h, w), np.float32)
            oy, ox = (h - nh) // 2, (w - nw) // 2
            canvas[max(0, oy):max(0, oy) + min(h, nh), max(0, ox):max(0, ox) + min(w, nw)] = \
                cov[max(0, -oy):max(0, -oy) + min(h, nh), max(0, -ox):max(0, -ox) + min(w, nw)]
            cov = canvas
        h, w = cov.shape
    # ---- paper
    P = C.get('paper', {})
    pc = _rgb(P.get('color', 246))
    paper = np.empty((h, w, 3), np.float32)
    paper[:] = pc
    tex = P.get('texture', 0)
    if tex:
        f = tex * smooth_field((h, w), rng, (14, 10)) + tex * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        paper += f[..., None]
        del f
    if P.get('fibers'):
        lay = Image.new('L', (w, h), 0)
        dr = ImageDraw.Draw(lay)
        n = int(P['fibers'] * w * h / 1e6)
        for _ in range(n):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            L = mm2px(rng.uniform(0.6, 3.0), dpi)
            a = rng.uniform(0, np.pi)
            dr.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=int(rng.uniform(40, 110)), width=1)
        fib = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.6 * sc)), np.float32) / 255.0
        paper *= (1 - 0.35 * fib)[..., None]
        del fib
    if P.get('age_edges'):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        e = np.minimum(np.minimum(xx / w, 1 - xx / w), np.minimum(yy / h, 1 - yy / h))
        t = np.clip(1 - e / 0.12, 0, 1) ** 2 * (0.6 + 0.4 * smooth_field((h, w), rng, (8, 6), 0, 1))
        paper = _multiply_tint(paper, P['age_edges'] * t, P.get('age_color', (170, 120, 60)))
        del yy, xx, e, t
    # ---- bleed-through from the reverse page
    B = C.get('bleed')
    if B:
        rev = ctx['reverse'][page_idx % len(ctx['reverse'])]
        rc = 1.0 - rev.astype(np.float32) / 255.0
        rc = rc[:, ::-1]
        if rc.shape != (h, w):
            rc = np.asarray(Image.fromarray((rc * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                            np.float32) / 255
        rc = _gauss(rc, B.get('blur', 2.0) * sc)
        dy, dx = int(mm2px(B.get('shift_mm', [3, -2])[0], dpi)), int(mm2px(B.get('shift_mm', [3, -2])[1], dpi))
        rc = np.roll(np.roll(rc, dy, 0), dx, 1)
        a = B['amount'] * rc * (0.75 + 0.25 * smooth_field((h, w), rng, (6, 5), 0, 1))
        paper = paper * (1 - a[..., None]) + _rgb(B.get('color', (70, 65, 60)))[None, None, :] * a[..., None]
        del rc, a
    ink = _rgb(C.get('ink_color', 22))
    iv = C.get('ink_var', 0)
    if iv:
        inkf = ink[None, None, :] + iv * smooth_field((h, w), rng, (10, 8), 0, 1)[..., None]
    else:
        inkf = ink[None, None, :]
    rgb = paper * (1 - cov[..., None]) + inkf * cov[..., None]
    del paper, inkf
    mask = np.ones((h, w), np.float32)
    # ---- stains
    for s in C.get('stains', []):
        r = mm2px(s['radius_mm'], dpi)
        cx = mm2px(s['x_mm'], dpi)
        cy = mm2px(s['y_mm'], dpi)
        res = _blob_field((h, w), cx, cy, r, rng, wobble=s.get('wobble', 0.10))
        if res is None:
            continue
        (y0, y1, x0, x1), d = res
        ring_w = s.get('ring_width', 0.05)
        ring = np.exp(-((d - 1.0) / ring_w) ** 2)
        inner = np.clip(1 - d, 0, 1) ** 0.3 * (d < 1)
        mott = 0.6 + 0.4 * smooth_field(d.shape, rng, (6, 6), 0, 1)
        alpha = (s.get('ring', 0.45) * ring + s.get('fill', 0.12) * inner * mott) * s.get('strength', 1.0)
        if s.get('partial'):
            # an arc only (a cup set down at the edge of the page or half dried)
            th = np.arctan2(*np.mgrid[y0:y1, x0:x1].astype(np.float32) - np.array([cy, cx])[:, None, None])
            keep = np.cos(th - s['partial']) > -0.2
            alpha = alpha * keep
        sub = rgb[y0:y1, x0:x1]
        rgb[y0:y1, x0:x1] = _multiply_tint(sub, np.clip(alpha, 0, 0.9).astype(np.float32),
                                           s.get('color', (150, 100, 45)))
        notes.append({'type': 'stain', 'x_mm': round(s['x_mm'], 1), 'y_mm': round(s['y_mm'], 1),
                      'radius_mm': s['radius_mm']})
    F = C.get('foxing')
    if F:
        n = int(F['n'])
        for _ in range(n):
            r = mm2px(rng.uniform(*F.get('size_mm', (0.4, 2.5))), dpi)
            cx, cy = rng.uniform(0, w), rng.uniform(0, h)
            res = _blob_field((h, w), cx, cy, r, rng, wobble=0.3, nharm=4)
            if res is None:
                continue
            (y0, y1, x0, x1), d = res
            alpha = np.clip(1 - d, 0, 1) ** 0.6 * F.get('strength', 0.4) * rng.uniform(0.5, 1.0)
            rgb[y0:y1, x0:x1] = _multiply_tint(rgb[y0:y1, x0:x1], alpha.astype(np.float32),
                                               F.get('color', (165, 105, 50)))
    # ---- highlighter
    for hl in C.get('highlighter', []):
        staves = info['staves']
        if not staves:
            break
        st = staves[int(rng.integers(0, len(staves)))]
        x0 = mm2px(st['x0'] + rng.uniform(0.1, 0.5) * (st['x1'] - st['x0']), dpi)
        x1 = x0 + mm2px(hl.get('len_mm', 50), dpi)
        y0 = mm2px(st['top'] - st['space'] * 0.8, dpi)
        y1 = mm2px(st['bottom'] + st['space'] * 0.8, dpi)
        yy0, yy1, xx0, xx1 = int(max(0, y0)), int(min(h, y1)), int(max(0, x0)), int(min(w, x1))
        if yy1 > yy0 and xx1 > xx0:
            a = np.full((yy1 - yy0, xx1 - xx0), hl.get('alpha', 0.55), np.float32)
            a *= 0.85 + 0.15 * smooth_field(a.shape, rng, (3, 12), 0, 1)
            rgb[yy0:yy1, xx0:xx1] = _multiply_tint(rgb[yy0:yy1, xx0:xx1], a, hl.get('color', (255, 235, 60)))
            notes.append({'type': 'highlighter', 'x_mm': round(x0 * 25.4 / dpi, 1), 'y_mm': round(y0 * 25.4 / dpi, 1),
                          'w_mm': hl.get('len_mm', 50)})
    # ---- handwriting (pencil / pen)
    for A in C.get('annotations', []):
        lay, marks = draw_annotations((h, w), dpi, info, rng, A)
        cov_a = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.45 * sc)), np.float32) / 255.0
        if A.get('tool', 'pencil') == 'pencil':
            grain = 0.55 + 0.45 * rng.random((h, w)).astype(np.float32)
            cov_a *= grain
        cov_a *= A.get('alpha', 0.7)
        col = _rgb(A.get('color', (75, 75, 82)))
        rgb = rgb * (1 - cov_a[..., None]) + col[None, None, :] * cov_a[..., None]
        notes.extend(marks)
        del cov_a
    # ---- punch holes
    Hh = C.get('holes')
    if Hh:
        dia = mm2px(Hh.get('diam_mm', 6), dpi)
        cx = mm2px(Hh['x_mm'], dpi)
        ys = [h / 2 + mm2px(o, dpi) for o in Hh['offsets_mm']]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for cy in ys:
            y0, y1 = int(max(0, cy - dia)), int(min(h, cy + dia))
            x0, x1 = int(max(0, cx - dia)), int(min(w, cx + dia))
            d = np.sqrt((xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2)
            inside = np.clip(dia / 2 - d + 0.5, 0, 1)
            mask[y0:y1, x0:x1] = np.minimum(mask[y0:y1, x0:x1], 1 - inside)
            rim = np.exp(-((d - dia / 2) / (0.35 * mm2px(1, dpi))) ** 2) * (d >= dia / 2)
            rgb[y0:y1, x0:x1] *= (1 - 0.35 * rim)[..., None]
            notes.append({'type': 'punch_hole', 'x_mm': round(Hh['x_mm'], 1), 'y_mm': round(cy * 25.4 / dpi, 1),
                          'diam_mm': Hh.get('diam_mm', 6)})
        del yy, xx
    S = C.get('staple')
    if S:
        cx, cy = mm2px(S['x_mm'], dpi), mm2px(S['y_mm'], dpi)
        L = mm2px(S.get('len_mm', 12), dpi)
        a = math.radians(S.get('angle', 45))
        dx, dy = L / 2 * math.cos(a), -L / 2 * math.sin(a)
        p0, p1 = (cx - dx, cy - dy), (cx + dx, cy + dy)
        lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        wd = max(2, int(mm2px(0.8, dpi)))
        off = mm2px(0.5, dpi)
        dr.line([(p0[0] + off, p0[1] + off), (p1[0] + off, p1[1] + off)], fill=(40, 40, 40, 150), width=wd + 2)
        dr.line([p0, p1], fill=(120, 122, 128, 255), width=wd)
        dr.line([(p0[0], p0[1] - wd / 3), (p1[0], p1[1] - wd / 3)], fill=(225, 228, 232, 255), width=max(1, wd // 3))
        for p in (p0, p1):
            rr = wd * 0.6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=(60, 60, 62, 255))
        lay = lay.filter(ImageFilter.GaussianBlur(0.4 * sc))
        la = np.asarray(lay, np.float32)
        al = la[..., 3:4] / 255.0
        rgb = rgb * (1 - al) + la[..., :3] * al
        notes.append({'type': 'staple', 'x_mm': S['x_mm'], 'y_mm': S['y_mm']})
        del la, al
    D = C.get('dogear')
    if D:
        L = mm2px(D['size_mm'], dpi)
        corner = D.get('corner', 'tr')
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        X = xx if corner in ('tl', 'bl') else (w - 1 - xx)
        Y = yy if corner in ('tl', 'tr') else (h - 1 - yy)
        s = X + Y
        gone = s < L
        flap = (X < L) & (Y < L) & (s >= L)
        mask[gone] = 0
        back = _rgb(D.get('back', (232, 230, 224)))
        shade = np.clip((s[flap] - L) / L, 0, 1)
        rgb[flap] = back[None, :] * (0.92 + 0.08 * shade[:, None])
        # shadow cast by the flap onto the page
        sh = (~flap) & (~gone) & (X < L + mm2px(2.0, dpi)) & (Y < L + mm2px(2.0, dpi)) & (s < 2 * L + mm2px(2.0, dpi))
        rgb[sh] *= 0.88
        notes.append({'type': 'dog_ear', 'corner': corner, 'size_mm': D['size_mm']})
        del yy, xx, X, Y, s, gone, flap, sh
    Cr = C.get('crop')
    if Cr:
        x0 = int(round(mm2px(Cr['left_mm'], dpi)))
        x1 = int(round(mm2px(Cr['right_mm'], dpi)))
        y0 = int(round(mm2px(Cr['top_mm'], dpi)))
        y1 = int(round(mm2px(Cr['bottom_mm'], dpi)))
        rgb = rgb[max(0, y0):min(h, y1), max(0, x0):min(w, x1)]
        mask = mask[max(0, y0):min(h, y1), max(0, x0):min(w, x1)]
        notes.append({'type': 'crop', 'box_mm': [Cr['left_mm'], Cr['top_mm'], Cr['right_mm'], Cr['bottom_mm']]})
    return np.ascontiguousarray(rgb), np.ascontiguousarray(mask), notes


# ---------------------------------------------------------------- handwriting
WORDS = {
    'hymn': ['breathe', 'slower', 'p', 'cresc.', 'rit.', 'S+A only', 'v.2 soft', 'hold!', 'watch', 'mf'],
    'melody': ['breathe', 'legato', 'p', 'rit.', 'rubato', 'mf', 'softer', 'lift'],
    'piano': ['pedal', 'slower', 'p', 'cresc.', 'rit.', 'mf', 'legato!', 'count!', 'L.H.'],
}
FINGERS = ['1', '2', '3', '4', '5', '2', '3', '1']


def _wobbly_ellipse(cx, cy, rx, ry, rng, overshoot):
    n = 60
    t0 = rng.uniform(0, 2 * np.pi)
    ts = np.linspace(t0, t0 + 2 * np.pi + overshoot, n)
    ph = rng.uniform(0, 2 * np.pi, 3)
    rad = 1 + 0.06 * np.sin(2 * ts + ph[0]) + 0.04 * np.sin(3 * ts + ph[1]) + np.linspace(0, 0.12, n)
    rot = rng.uniform(-0.4, 0.4)
    xs = rx * rad * np.cos(ts)
    ys = ry * rad * np.sin(ts)
    return [(cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot))
            for x, y in zip(xs, ys)]


def _text_layer(txt, size_px, angle, font_path=HAND_FONT):
    font = ImageFont.truetype(font_path, max(8, int(size_px)))
    bb = font.getbbox(txt)
    tw, th = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
    im = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), txt, font=font, fill=255)
    if txt and size_px > 20:
        im = im.filter(ImageFilter.MaxFilter(3))
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def draw_annotations(shape, dpi, info, rng, A):
    """Handwritten marks positioned relative to detected staves / noteheads."""
    h, w = shape
    lay = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(lay)
    width = max(1, int(round(mm2px(A.get('width_mm', 0.35), dpi))))
    staves = info['staves']
    k = dpi / 25.4
    cands = info['notes_mm']
    marks = []
    if not staves:
        return lay, marks
    used = []

    def pick_note():
        for _ in range(60):
            x, y, sp = cands[int(rng.integers(0, len(cands)))]
            if all(abs(x - ux) > 4 * sp or abs(y - uy) > 4 * sp for ux, uy in used):
                used.append((x, y))
                return x, y, sp
        return cands[int(rng.integers(0, len(cands)))]

    for _ in range(A.get('circles', 0)):
        if not cands:
            break
        x, y, sp = pick_note()
        rx = sp * rng.uniform(1.2, 2.0) * k
        ry = sp * rng.uniform(1.1, 1.7) * k
        pts = _wobbly_ellipse(x * k, y * k, rx, ry, rng, rng.uniform(0.2, 0.7))
        dr.line(pts, fill=255, width=width, joint='curve')
        marks.append({'type': 'circled_note', 'x_mm': round(x, 1), 'y_mm': round(y, 1)})
    words = WORDS.get(A.get('vocab', 'hymn'), WORDS['hymn'])
    for _ in range(A.get('texts', 0)):
        st = staves[int(rng.integers(0, len(staves)))]
        sp = st['space']
        txt = words[int(rng.integers(0, len(words)))]
        x = rng.uniform(st['x0'] + 5, max(st['x0'] + 6, st['x1'] - 25))
        above = rng.random() < 0.7
        y = st['top'] - sp * rng.uniform(3.2, 4.5) if above else st['bottom'] + sp * rng.uniform(1.5, 2.5)
        im = _text_layer(txt, sp * k * rng.uniform(1.8, 2.8), rng.uniform(-8, 8))
        _paste_max(lay, im, int(x * k), int(y * k))
        marks.append({'type': 'handwritten_text', 'text': txt, 'x_mm': round(x, 1), 'y_mm': round(y, 1)})
    for _ in range(A.get('fingerings', 0)):
        if not cands:
            break
        x, y, sp = pick_note()
        st = min(staves, key=lambda s: abs((s['top'] + s['bottom']) / 2 - y))
        txt = FINGERS[int(rng.integers(0, len(FINGERS)))]
        yy = min(y, st['top']) - sp * rng.uniform(2.2, 3.2)
        im = _text_layer(txt, sp * k * rng.uniform(1.6, 2.2), rng.uniform(-10, 10))
        _paste_max(lay, im, int((x - sp * 0.4) * k), int(yy * k))
        marks.append({'type': 'fingering', 'text': txt, 'x_mm': round(x, 1), 'y_mm': round(yy, 1)})
    for _ in range(A.get('breaths', 0)):
        st = staves[int(rng.integers(0, len(staves)))]
        sp = st['space']
        x = rng.uniform(st['x0'] + 15, st['x1'] - 5) * k
        y = (st['top'] - sp * rng.uniform(1.2, 2.0)) * k
        s = sp * k * rng.uniform(0.8, 1.2)
        if rng.random() < 0.5:   # tick / V breath mark
            dr.line([(x - s * 0.5, y - s), (x, y), (x + s * 0.7, y - s * 1.4)], fill=255, width=width, joint='curve')
            kind = 'breath_tick'
        else:                    # comma
            dr.arc([x - s * 0.4, y - s, x + s * 0.4, y], 300, 120, fill=255, width=width + 1)
            kind = 'breath_comma'
        marks.append({'type': kind, 'x_mm': round(x / k, 1), 'y_mm': round(y / k, 1)})
    for _ in range(A.get('arrows', 0)):
        st = staves[int(rng.integers(0, len(staves)))]
        sp = st['space']
        x0 = rng.uniform(st['x0'] + 10, st['x1'] - 40) * k
        y0 = (st['bottom'] + sp * rng.uniform(2.0, 3.0)) * k
        L = mm2px(rng.uniform(15, 35), dpi)
        x1, y1 = x0 + L, y0 + rng.uniform(-0.1, 0.1) * L
        mid = ((x0 + x1) / 2, (y0 + y1) / 2 - L * 0.08)
        dr.line([(x0, y0), mid, (x1, y1)], fill=255, width=width, joint='curve')
        hd = mm2px(2.2, dpi)
        dr.line([(x1 - hd, y1 - hd * 0.6), (x1, y1), (x1 - hd, y1 + hd * 0.6)], fill=255, width=width)
        marks.append({'type': 'arrow', 'x_mm': round(x0 / k, 1), 'y_mm': round(y0 / k, 1)})
    for _ in range(A.get('brackets', 0)):
        st = staves[int(rng.integers(0, len(staves)))]
        sp = st['space']
        x0 = rng.uniform(st['x0'] + 10, st['x1'] - 50) * k
        x1 = x0 + mm2px(rng.uniform(25, 50), dpi)
        y = (st['top'] - sp * rng.uniform(2.5, 3.5)) * k
        hh = sp * k * 1.2
        dr.arc([x0, y, x1, y + 2 * hh], 190, 350, fill=255, width=width)
        marks.append({'type': 'phrase_arc', 'x_mm': round(x0 / k, 1), 'y_mm': round(y / k, 1)})
    for _ in range(A.get('scribbles', 0)):
        # a loose zig-zag "cross-hatching" in the margin (no musical meaning)
        x = rng.choice([rng.uniform(3, 12), info['size_mm'][0] - rng.uniform(5, 14)]) * k
        y = rng.uniform(30, info['size_mm'][1] - 30) * k
        pts = [(x + rng.uniform(-1, 1) * mm2px(4, dpi), y + i * mm2px(1.6, dpi)) for i in range(int(rng.integers(6, 14)))]
        dr.line(pts, fill=255, width=width, joint='curve')
        marks.append({'type': 'margin_scribble', 'x_mm': round(x / k, 1), 'y_mm': round(y / k, 1)})
    return lay, marks


def _paste_max(lay, im, x, y):
    W, H = lay.size
    if x >= W or y >= H or x + im.width <= 0 or y + im.height <= 0:
        return
    box = (max(0, x), max(0, y), min(W, x + im.width), min(H, y + im.height))
    sub = im.crop((box[0] - x, box[1] - y, box[2] - x, box[3] - y))
    region = lay.crop(box)
    a = np.maximum(np.asarray(region), np.asarray(sub))
    lay.paste(Image.fromarray(a), box[:2])


# ---------------------------------------------------------------- stage 2: page geometry
def _remap_rgbm(rgb, mask, xs, ys):
    out = np.empty_like(rgb)
    for c in range(3):
        out[..., c] = remap(rgb[..., c], xs, ys, fill=0.0)
    m = remap(mask, xs, ys, fill=0.0)
    return out, m


def page_geom(rgb, mask, ops, dpi, rng, side_hint='left'):
    for op, p in ops:
        h, w = mask.shape
        if op == 'curl':
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            amp = mm2px(p['amp_mm'], dpi)
            width = p.get('width', 0.25) * w
            side = p.get('side', side_hint)
            t = np.clip((width - xx) / width, 0, 1) if side == 'left' else np.clip((xx - (w - width)) / width, 0, 1)
            dy = amp * t ** 2 * ((yy - h / 2) / (h / 2))
            dx = (amp * 0.6) * t ** 2 * (1 if side == 'left' else -1)
            rgb, mask = _remap_rgbm(rgb, mask, xx - dx, yy - dy)
            # the curled part is darker (it bends away from the glass)
            shade = 1 - p.get('shade', 0.25) * t ** 1.5
            rgb *= shade[..., None]
            del yy, xx, t, dy, dx, shade
        elif op == 'wave':
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            dy = mm2px(p['amp_mm'], dpi) * np.sin(2 * np.pi * xx / (p.get('period', 1.3) * w) + p.get('phase', 0.3))
            rgb, mask = _remap_rgbm(rgb, mask, xx, yy - dy)
            del yy, xx, dy
        elif op == 'scale':
            f = p['factor']
            nw, nh = int(round(w * f)), int(round(h * f))
            im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)
            mk = Image.fromarray((mask * 255).astype(np.uint8)).resize((nw, nh), Image.BILINEAR)
            if p.get('keep_canvas', True):
                canvas = np.empty((h, w, 3), np.float32)
                canvas[:] = _rgb(p.get('fill', 246))
                cm = np.ones((h, w), np.float32)
                oy, ox = (h - nh) // 2 + int(mm2px(p.get('dy_mm', 0), dpi)), (w - nw) // 2 + int(mm2px(p.get('dx_mm', 0), dpi))
                ys0, xs0 = max(0, oy), max(0, ox)
                ys1, xs1 = min(h, oy + nh), min(w, ox + nw)
                canvas[ys0:ys1, xs0:xs1] = np.asarray(im, np.float32)[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
                cm[ys0:ys1, xs0:xs1] = np.asarray(mk, np.float32)[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox] / 255
                rgb, mask = canvas, cm
            else:
                rgb, mask = np.asarray(im, np.float32), np.asarray(mk, np.float32) / 255
        elif op == 'rot90':
            k = int(p) % 4
            rgb = np.ascontiguousarray(np.rot90(rgb, k, axes=(0, 1)))
            mask = np.ascontiguousarray(np.rot90(mask, k))
        elif op == 'gutter':
            gw = int(p.get('width', 0.06) * w)
            prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * p.get('dark', 0.5)
            side = p.get('side', side_hint)
            if side == 'left':
                rgb[:, :gw] *= (1 - prof)[None, :, None]
            else:
                rgb[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
        elif op == 'rotate':
            rgb, mask = _rotate(rgb, mask, p['deg'], expand=p.get('expand', True))
        else:
            raise ValueError(op)
    return rgb, mask


def _rotate(rgb, mask, deg, expand=True):
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    mk = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
    im = im.rotate(deg, resample=Image.BICUBIC, expand=expand, fillcolor=(0, 0, 0))
    mk = mk.rotate(deg, resample=Image.BILINEAR, expand=expand, fillcolor=0)
    return np.asarray(im, np.float32).copy(), np.asarray(mk, np.float32) / 255.0


# ---------------------------------------------------------------- stage 3: assembly
def spread(pages, dpi, p):
    """2-up: pages[0] left (verso), pages[1] right (recto) with gutter."""
    (lr, lm), (rr, rm) = pages
    h = max(lr.shape[0], rr.shape[0])

    def padh(a, m):
        if a.shape[0] == h:
            return a, m
        a2 = np.zeros((h,) + a.shape[1:], np.float32)
        m2 = np.zeros((h, a.shape[1]), np.float32)
        a2[:a.shape[0]] = a
        m2[:a.shape[0]] = m
        return a2, m2
    lr, lm = padh(lr, lm)
    rr, rm = padh(rr, rm)
    rgb = np.concatenate([lr, rr], axis=1)
    mask = np.concatenate([lm, rm], axis=1)
    W = rgb.shape[1]
    cx = lr.shape[1]
    gw = int(p.get('gutter_width', 0.05) * W)
    xs = np.arange(W, dtype=np.float32)
    t = np.clip(1 - np.abs(xs - cx) / max(1, gw), 0, 1) ** 2
    rgb *= (1 - p.get('gutter_dark', 0.5) * t)[None, :, None]
    # crease line
    rgb[:, max(0, cx - 1):cx + 1] *= 0.6
    return rgb, mask


# ---------------------------------------------------------------- stage 4: global
GEOM = {'bed', 'rotate', 'perspective', 'rot90'}


def composite(rgb, mask, bg, rng):
    h, w = mask.shape
    col = _rgb(bg.get('color', (232, 232, 230)))
    field = np.empty((h, w, 3), np.float32)
    field[:] = col
    if bg.get('texture', 0):
        field += (bg['texture'] * smooth_field((h, w), rng, (5, 5)))[..., None]
    if bg.get('noise', 0):
        field += rng.normal(0, bg['noise'], (h, w)).astype(np.float32)[..., None]
    if bg.get('edge_shadow', 0.0):
        # dark line along the page edge (thickness of the sheet on the glass)
        m8 = Image.fromarray((mask * 255).astype(np.uint8))
        e = np.asarray(m8.filter(ImageFilter.GaussianBlur(2.0)), np.float32) / 255
        edge = np.clip(1 - np.abs(e - 0.5) * 2, 0, 1)
        field *= (1 - bg['edge_shadow'] * edge)[..., None]
    m = mask[..., None]
    return rgb * m + field * (1 - m)


def global_stage(rgb, mask, ops, dpi, rng, bg):
    sc = dpi / 300.0
    done = False
    for op, p in ops:
        if op not in GEOM and not done:
            rgb = composite(rgb, mask, bg, rng)
            done = True
        h, w = mask.shape
        if op == 'bed':
            m = int(mm2px(p.get('margin_mm', 8), dpi))
            mt = int(mm2px(p.get('top_mm', p.get('margin_mm', 8)), dpi))
            ml = int(mm2px(p.get('left_mm', p.get('margin_mm', 8)), dpi))
            nr = np.zeros((h + mt + m, w + ml + m, 3), np.float32)
            nm = np.zeros((h + mt + m, w + ml + m), np.float32)
            nr[mt:mt + h, ml:ml + w] = rgb
            nm[mt:mt + h, ml:ml + w] = mask
            rgb, mask = nr, nm
        elif op == 'rotate':
            rgb, mask = _rotate(rgb, mask, p['deg'], expand=p.get('expand', True))
        elif op == 'rot90':
            rgb = np.ascontiguousarray(np.rot90(rgb, int(p) % 4, axes=(0, 1)))
            mask = np.ascontiguousarray(np.rot90(mask, int(p) % 4))
        elif op == 'perspective':
            m = int(p.get('margin', 0.06) * w)
            H, W = h + 2 * m, w + 2 * m
            nr = np.zeros((H, W, 3), np.float32)
            nm = np.zeros((H, W), np.float32)
            nr[m:m + h, m:m + w] = rgb
            nm[m:m + h, m:m + w] = mask
            jit = p.get('jitter', 0.04)
            dst = [(0, 0), (W, 0), (W, H), (0, H)]
            ks = p.get('keystone', 0.0)   # top edge narrower (camera tilted back)
            src = []
            for i, (x, y) in enumerate(dst):
                dx = rng.uniform(-jit, jit) * W
                dy = rng.uniform(-jit, jit) * H
                if i in (0, 1):
                    dx += (-1 if i == 0 else 1) * ks * W
                src.append((x + dx, y + dy))
            coeffs = perspective_coeffs(src, dst)
            im = Image.fromarray(np.clip(nr, 0, 255).astype(np.uint8)).transform(
                (W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
            mk = Image.fromarray((nm * 255).astype(np.uint8)).transform(
                (W, H), Image.PERSPECTIVE, coeffs, resample=Image.BILINEAR, fillcolor=0)
            rgb, mask = np.asarray(im, np.float32).copy(), np.asarray(mk, np.float32) / 255
            p['_corners_src'] = [[round(a, 1), round(b, 1)] for a, b in src]
        elif op == 'gradient':
            ang = math.radians(p.get('angle', float(rng.uniform(0, 360))))
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            t = ((xx / w - 0.5) * math.cos(ang) + (yy / h - 0.5) * math.sin(ang)) + 0.5
            rgb *= (1 - p['strength'] * np.clip(t, 0, 1))[..., None]
            del yy, xx, t
        elif op == 'vignette':
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            r = np.sqrt((xx / w - 0.5) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
            rgb *= (1 - p['strength'] * r ** 2)[..., None]
            del yy, xx, r
        elif op == 'blotch':
            rgb *= (1 - p['strength'] * np.clip(smooth_field((h, w), rng, (5, 4), -0.5, 1), 0, 1))[..., None]
        elif op == 'shadow':
            # soft shadow (hand / phone) entering from one side
            ang = math.radians(p.get('angle', float(rng.uniform(0, 360))))
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            t = (xx / w - 0.5) * math.cos(ang) + (yy / h - 0.5) * math.sin(ang)
            edge = p.get('pos', 0.25)
            wob = 0.03 * smooth_field((h, w), rng, (3, 3))
            s = 1 / (1 + np.exp(-(t + wob - edge) / p.get('soft', 0.04)))
            rgb *= (1 - p['strength'] * s)[..., None]
            del yy, xx, t, s, wob
        elif op == 'gutter_center':
            xs = np.arange(w, dtype=np.float32)
            t = np.clip(1 - np.abs(xs - w / 2) / (p.get('width', 0.05) * w), 0, 1) ** 2
            rgb *= (1 - p.get('dark', 0.5) * t)[None, :, None]
        elif op == 'color_cast':
            rgb *= (_rgb(p['rgb']) / 255.0)[None, None, :]
        elif op == 'blur':
            rgb = _blur_rgb(rgb, p['sigma'] * sc)
        elif op == 'motion':
            L = max(2, int(round(p['length'] * sc)))
            a = math.radians(p.get('angle', 0))
            acc = np.zeros_like(rgb)
            for i in range(L):
                t = i - (L - 1) / 2
                dx, dy = int(round(t * math.cos(a))), int(round(t * math.sin(a)))
                acc += np.roll(np.roll(rgb, dy, 0), dx, 1)
            rgb = acc / L
            del acc
        elif op == 'noise':
            n = rng.normal(0, p['sigma'], (h, w)).astype(np.float32)
            if p.get('chroma', 0):
                rgb += rng.normal(0, p['chroma'], (h, w, 3)).astype(np.float32)
            rgb += n[..., None]
            del n
        elif op == 'saltpepper':
            n = int(p['amount'] * h * w)
            ys = rng.integers(0, h, n)
            xs = rng.integers(0, w, n)
            vals = np.where(rng.random(n) < p.get('pepper_ratio', 0.5), 15.0, 245.0).astype(np.float32)
            rgb[ys, xs] = vals[:, None]
        elif op == 'speckle':
            n = int(p['per_mpx'] * (w * h) / 1e6)
            lay = Image.new('L', (w, h), 0)
            dr = ImageDraw.Draw(lay)
            for _ in range(n):
                r = rng.uniform(0.5, p.get('max_r', 2.2)) * sc
                cx, cy = rng.uniform(0, w), rng.uniform(0, h)
                dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(rng.uniform(150, 255)))
            sp = np.asarray(lay, np.float32) / 255
            rgb = rgb * (1 - sp[..., None]) + 25 * sp[..., None]
            del sp
        elif op == 'border':
            bw = int(mm2px(p.get('width_mm', 4), dpi))
            lvl = p.get('level', 30)
            side = p.get('side', 'top')
            noise = rng.normal(0, 6, (h, w)).astype(np.float32)
            sl = {'top': (slice(0, bw), slice(None)), 'bottom': (slice(h - bw, h), slice(None)),
                  'left': (slice(None), slice(0, bw)), 'right': (slice(None), slice(w - bw, w))}[side]
            rgb[sl] = (lvl + noise[sl])[..., None]
            del noise
        elif op == 'downsample':
            # capture at a lower resolution and interpolate back up
            f = p['factor']
            im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
            im = im.resize((max(1, int(w * f)), max(1, int(h * f))), Image.BILINEAR).resize((w, h), Image.BILINEAR)
            rgb = np.asarray(im, np.float32).copy()
        elif op == 'binarize':
            pass   # handled at output
        else:
            raise ValueError(op)
    if not done:
        rgb = composite(rgb, mask, bg, rng)
    return rgb, mask


# ---------------------------------------------------------------- stage 5: output
def to_image(rgb, out, rng):
    mode = out.get('mode', 'L')
    rgb = np.clip(rgb, 0, 255)
    if mode == 'RGB':
        return Image.fromarray(rgb.astype(np.uint8), 'RGB')
    gray = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    if mode == '1':
        B = out['binarize']
        g = gray
        if B.get('pre_blur'):
            g = _gauss(g, B['pre_blur'])
        if B.get('noise'):
            g = g + rng.normal(0, B['noise'], g.shape).astype(np.float32)
        bw = (g > B['thr'])
        im = Image.fromarray((bw * 255).astype(np.uint8))
        for _ in range(int(B.get('dilate', 0))):
            im = im.filter(ImageFilter.MinFilter(3))
        for _ in range(int(B.get('erode', 0))):
            im = im.filter(ImageFilter.MaxFilter(3))
        return im.convert('1', dither=Image.NONE)
    return Image.fromarray(gray.astype(np.uint8), 'L')


def save_pdf(images, dpi, path, out):
    fmt = out.get('format', 'jpeg')
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if fmt == 'jpeg' and im.mode != '1':
                cur = im
                q = int(out.get('quality', 75))
                sub = out.get('subsampling', 2)
                for _ in range(int(out.get('passes', 1)) - 1):
                    b = io.BytesIO()
                    cur.save(b, 'JPEG', quality=min(95, q + 10), subsampling=sub)
                    b.seek(0)
                    cur = Image.open(b)
                    cur.load()
                fn = os.path.join(td, f'p{k:03d}.jpg')
                cur.save(fn, 'JPEG', quality=q, dpi=(dpi, dpi), optimize=True, subsampling=sub)
            else:
                fn = os.path.join(td, f'p{k:03d}.png')
                im.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
            files.append(fn)
        subprocess.run(['img2pdf', '--imgsize', f'{dpi}dpi', '-o', path] + files, check=True, capture_output=True,
                       timeout=600)


def apply_spec(clean_pages, spec, ctx, infos, seed):
    """clean_pages: list of uint8 gray pages at spec['dpi'].  Returns PIL images."""
    rng = np.random.default_rng(seed)
    dpi = spec['dpi']
    content = spec.get('content', {})
    is_spread = spec.get('assembly') == 'spread'
    per = []
    for i, g in enumerate(clean_pages):
        C = dict(content)
        ov = spec.get('page_overrides', {}).get(str(i), {})
        C.update(ov.get('content', {}))
        rgb, mask, notes = content_stage(g, C, dpi, rng, infos[i], ctx, i)
        geom = list(spec.get('page_geom', [])) + list(ov.get('page_geom', []))
        # gutter side: a recto (odd page number / right of a spread) is bound on its left
        if is_spread and len(clean_pages) == 1:
            hint = 'left'
        elif is_spread:
            hint = 'right' if i == 0 else 'left'   # inner edges of a 2-page spread
        else:
            hint = 'right' if i % 2 else 'left'
        rgb, mask = page_geom(rgb, mask, geom, dpi, rng, side_hint=hint)
        per.append((rgb, mask, notes, ov.get('global', None)))
    images, all_notes = [], []
    if is_spread:
        S = spec['spread']
        if len(per) == 1:
            # facing verso page (text only, no music): same paper, no handwriting
            Cf = {k: v for k, v in content.items() if k in ('paper', 'ink_color', 'ink_var', 'fade', 'ink_weight')}
            fr, fm, _ = content_stage(ctx['facing'], Cf, dpi, rng, {'staves': [], 'notes_mm': []}, ctx, 0)
            fr, fm = page_geom(fr, fm, list(spec.get('page_geom', [])), dpi, rng, side_hint='right')
            left, right = (fr, fm), (per[0][0], per[0][1])
        else:
            left, right = (per[0][0], per[0][1]), (per[1][0], per[1][1])
        rgb, mask = spread([left, right], dpi, S)
        rgb, mask = global_stage(rgb, mask, [tuple(x) for x in spec.get('global', [])], dpi, rng, spec.get('bg', {}))
        images.append(to_image(rgb, spec.get('out', {}), rng))
        all_notes = [n for p in per for n in p[2]]
    else:
        for rgb, mask, notes, gov in per:
            ops = gov if gov is not None else spec.get('global', [])
            rgb, mask = global_stage(rgb, mask, [tuple(x) for x in ops], dpi, rng, spec.get('bg', {}))
            images.append(to_image(rgb, spec.get('out', {}), rng))
            all_notes.append(notes)
            del rgb, mask
    return images, all_notes
