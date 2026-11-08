"""Scan / photocopy / phone-capture damage for the rhythm challenge corpus.

Extends the ideas of corpus/synthetic/_tools/synth/degrade.py and
spike/classical/tools/degrade.py (numpy + Pillow only) with RGB paper, foxing,
coffee stains, pencil annotations, punch holes, staples, cropped edges, halftone
moire, motion blur, large/90/180 degree rotations, 2-up book spreads and per-page
scale mismatch.

A variant is {'dpi': int, 'color': 'rgb'|'gray', 'ops': [op, ...], 'format': 'jpeg'|'png'|'png1',
'jpeg': q, 'jpeg_passes': n, 'seed': int}.  Ops are applied in list order (author keeps a
physical order: print -> paper -> capture geometry -> lighting -> optics/sensor ->
processing).  Ops before {'op': 'paper'} act on the ink-coverage map, later ops on the
image.  {'op': 'two_up'} merges consecutive pages into book spreads; ops after it act
on the spreads.  Any op may carry 'pages': [indices] to restrict it.
Nothing here alters the musical content: every op keeps all notes visible (crop is
limited to the margin / staff-end region, see op docs).
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

Image.MAX_IMAGE_PIXELS = None
FONT_SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_ITAL = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'


# ---------------------------------------------------------------- helpers

def render_pages(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'r{dpi}')
    for f in glob.glob(prefix + '-*.pgm'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                   check=True, timeout=600)
    files = sorted(glob.glob(prefix + '-*.pgm'))
    pages = [np.array(Image.open(f), dtype=np.uint8) for f in files]
    for f in files:
        os.remove(f)
    return pages


def smooth_field(shape, rng, cells=(6, 8), lo=-1.0, hi=1.0):
    small = rng.uniform(lo, hi, size=cells).astype(np.float32)
    im = Image.fromarray(small, mode='F').resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def _box_sizes(sigma, n=3):
    """box widths whose n-fold convolution approximates a gaussian of the given sigma"""
    wi = math.sqrt(12 * sigma * sigma / n + 1)
    wl = int(math.floor(wi))
    if wl % 2 == 0:
        wl -= 1
    wu = wl + 2
    m = round((12 * sigma * sigma - n * wl * wl - 4 * n * wl - 3 * n) / (-4 * wl - 4))
    return [wl if i < m else wu for i in range(n)]


def _box1d(a, r, axis):
    if r <= 0:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def gblur(a, sigma):
    """gaussian blur of a float 2D array (3 box passes per axis, edge padding)"""
    if sigma <= 0.15:
        return a.astype(np.float32)
    out = a.astype(np.float32)
    for w in _box_sizes(sigma):
        r = (w - 1) // 2
        out = _box1d(out, r, 0)
        out = _box1d(out, r, 1)
    return out


def per_channel(img, fn):
    return np.stack([fn(img[:, :, c]) for c in range(img.shape[2])], axis=2)


def remap(chan, xs, ys, fill):
    h, w = chan.shape
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
    fx = (xs - x0).astype(np.float32)
    fy = (ys - y0).astype(np.float32)
    valid = (x0 >= 0) & (y0 >= 0) & (x0 < w - 1) & (y0 < h - 1)
    x0c = np.clip(x0, 0, w - 2)
    y0c = np.clip(y0, 0, h - 2)
    a = chan[y0c, x0c]
    b = chan[y0c, x0c + 1]
    c = chan[y0c + 1, x0c]
    d = chan[y0c + 1, x0c + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    return np.where(valid, out, fill).astype(np.float32)


def to_pil(img):
    a = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(a[:, :, 0], 'L') if a.shape[2] == 1 else Image.fromarray(a, 'RGB')


def from_pil(im, C):
    a = np.asarray(im, dtype=np.float32)
    if a.ndim == 2:
        a = a[:, :, None]
    if C == 1 and a.shape[2] == 3:
        a = a.mean(axis=2, keepdims=True)
    return a


def bgcol(v, C):
    v = v if isinstance(v, (list, tuple)) else [v, v, v]
    return np.array(v[:C] if C == 3 else [float(np.mean(v))], np.float32)


def staff_info(gray):
    """Staff geometry of a clean page: list of dicts(top, bottom, sp, x0, x1, lines)."""
    dark = gray < 140
    h, w = gray.shape
    rowfrac = dark.mean(axis=1)
    rows = np.where(rowfrac > 0.22)[0]
    lines = []
    for r in rows:
        if lines and r - lines[-1][-1] <= 1:
            lines[-1].append(r)
        else:
            lines.append([r])
    centers = [float(np.mean(l)) for l in lines]
    staves = []
    k = 0
    while k + 4 < len(centers):
        grp = centers[k:k + 5]
        gaps = np.diff(grp)
        if gaps.max() < 1.5 * gaps.min() and gaps.max() < h * 0.03:
            sp = float(gaps.mean())
            band = dark[int(grp[0]):int(grp[-1]) + 1]
            colhit = band.mean(axis=0) > 0.5
            xs = np.where(colhit)[0]
            x0, x1 = (int(xs.min()), int(xs.max())) if len(xs) else (0, w - 1)
            staves.append({'top': grp[0], 'bottom': grp[-1], 'sp': sp, 'x0': x0, 'x1': x1,
                           'lines': [int(round(c)) for c in grp]})
            k += 5
        else:
            k += 1
    return staves


def ink_columns(gray, st):
    """x positions with ink in the staff band, staff lines removed (note candidates)."""
    sp = st['sp']
    y0, y1 = int(st['top'] - 2 * sp), int(st['bottom'] + 2 * sp)
    band = (gray[max(0, y0):y1, st['x0']:st['x1']] < 120).astype(np.float32)
    for ly in st['lines']:
        for dy in (-1, 0, 1):
            r = ly + dy - max(0, y0)
            if 0 <= r < band.shape[0]:
                band[r] = 0
    col = band.sum(axis=0)
    xs = np.where(col > sp * 0.9)[0] + st['x0']
    return xs, band, max(0, y0)


# ---------------------------------------------------------------- ops on coverage (print stage)

def op_ink_weight(cov, o, ctx):
    px = int(o.get('px', 1))
    pil = Image.fromarray((np.clip(cov, 0, 1) * 255).astype(np.uint8))
    for _ in range(abs(px)):
        pil = pil.filter(ImageFilter.MaxFilter(3) if px > 0 else ImageFilter.MinFilter(3))
    return np.asarray(pil, dtype=np.float32) / 255.0


def op_ink_dropout(cov, o, ctx):
    rng = ctx['rng']
    f = smooth_field(cov.shape, rng, (40, 30), 0, 1)
    fine = rng.random(cov.shape).astype(np.float32)
    drop = (f > 1 - o['amount']) & (fine < 0.5)
    return np.where(drop, cov * 0.4, cov)


# ---------------------------------------------------------------- paper stage (image, HxWxC)

def op_paper(cov, o, ctx):
    rng, C = ctx['rng'], ctx['C']
    h, w = cov.shape
    paper = bgcol(o.get('rgb', [246, 246, 244]), C)
    ink = bgcol(o.get('ink', [22, 22, 26]), C)
    tex = float(o.get('texture', 0))
    pf = np.broadcast_to(paper, (h, w, C)).astype(np.float32).copy()
    if tex:
        fld = tex * smooth_field((h, w), rng, (14, 10)) + tex * 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
        fib = gblur(rng.normal(0, 1, (h, w)).astype(np.float32), 1.2 * ctx['sc']) * tex * 0.8
        pf += (fld + fib)[:, :, None]
    if o.get('bleed'):
        b = o['bleed']
        mir = cov[:, ::-1]
        mir = gblur(mir, b.get('blur', 2.5) * ctx['sc'])
        mir = np.roll(mir, int(b.get('shift', 0.012) * h), axis=0)
        mir = np.roll(mir, int(b.get('xshift', 0.006) * w), axis=1)
        pf *= (1 - b['strength'] * mir)[:, :, None]
    if o.get('ink_var'):
        ink = ink[None, None, :] + o['ink_var'] * smooth_field((h, w), rng, (10, 8), 0, 1)[:, :, None]
    c3 = cov[:, :, None]
    return pf * (1 - c3) + ink * c3


def op_foxing(img, o, ctx):
    rng, sc, C = ctx['rng'], ctx['sc'], ctx['C']
    h, w = img.shape[:2]
    col = bgcol(o.get('rgb', [160, 110, 60]), C)
    mask = np.zeros((h, w), np.float32)
    n = int(o.get('n', 60))
    clusters = [(rng.uniform(0, w), rng.uniform(0, h)) for _ in range(max(1, n // 12))]
    for _ in range(n):
        cx, cy = clusters[rng.integers(len(clusters))]
        x = int(np.clip(cx + rng.normal(0, w * 0.08), 0, w - 1))
        y = int(np.clip(cy + rng.normal(0, h * 0.06), 0, h - 1))
        r = rng.uniform(*o.get('radius_mm', (0.3, 2.0))) * ctx['dpi'] / 25.4
        R = int(r * 2.5) + 2
        y0, y1, x0, x1 = max(0, y - R), min(h, y + R), max(0, x - R), min(w, x + R)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        d = np.sqrt((yy - y) ** 2 + (xx - x) ** 2) / r
        a = np.clip(1.2 - d, 0, 1) ** 1.5 * rng.uniform(0.35, 1.0)
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], a)
    s = float(o.get('strength', 0.5))
    m = (s * mask)[:, :, None]
    return img * (1 - m) + (img * col / 255.0) * m


def op_coffee(img, o, ctx):
    rng, C = ctx['rng'], ctx['C']
    h, w = img.shape[:2]
    col = bgcol(o.get('rgb', [150, 95, 45]), C)
    total = np.zeros((h, w), np.float32)
    for k in range(int(o.get('n', 1))):
        r = o.get('radius_mm', 38) * ctx['dpi'] / 25.4 * rng.uniform(0.85, 1.15)
        cx = rng.uniform(0.15, 0.85) * w if 'cx' not in o else o['cx'] * w
        cy = rng.uniform(0.15, 0.85) * h if 'cy' not in o else o['cy'] * h
        R = int(r * 1.3)
        y0, y1, x0, x1 = max(0, int(cy - R)), min(h, int(cy + R)), max(0, int(cx - R)), min(w, int(cx + R))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        ang = np.arctan2(yy - cy, xx - cx)
        wob = 1 + 0.06 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.04 * np.sin(7 * ang + rng.uniform(0, 6))
        d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2) / (r * wob)
        ring = np.exp(-((d - 1.0) / 0.035) ** 2)
        fill = np.clip(1 - d, 0, 1) ** 0.3 * 0.35
        if o.get('partial'):            # a cup ring that only touched the page partly
            fill *= (np.cos(ang - rng.uniform(0, 6)) > -0.2)
        a = np.clip(ring + fill, 0, 1) * (d < 1.08)
        noise = smooth_field(a.shape, rng, (9, 9), 0.6, 1.0)
        total[y0:y1, x0:x1] = np.maximum(total[y0:y1, x0:x1], a * noise)
    m = (float(o.get('strength', 0.45)) * total)[:, :, None]
    return img * (1 - m) + (img * col / 255.0) * m


def _hand_poly(draw, pts, rng, width, fill):
    pts = [(x + rng.normal(0, width * 0.25), y + rng.normal(0, width * 0.25)) for x, y in pts]
    draw.line(pts, fill=fill, width=max(1, int(width)), joint='curve')


def op_pencil(img, o, ctx):
    """graphite annotations: circles around notes, fingering digits, a misleading '3'
    over a group of notes, breath ticks, 'rit.'-style words, a bracket.  Not music."""
    rng, C, dpi = ctx['rng'], ctx['C'], ctx['dpi']
    h, w = img.shape[:2]
    staves = ctx['staves']
    gray = ctx['clean']
    if not staves:
        return img
    layer = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(layer)
    lw = max(1.0, 0.32 * dpi / 25.4)
    log = []
    for _ in range(int(o.get('circles', 3))):
        st = staves[rng.integers(len(staves))]
        xs, band, by0 = ink_columns(gray, st)
        if len(xs) == 0:
            continue
        x = int(xs[rng.integers(len(xs))])
        colwin = band[:, max(0, x - st['x0'] - int(st['sp'] / 2)): x - st['x0'] + int(st['sp'] / 2)]
        ys = np.where(colwin.sum(axis=1) > 0)[0]
        y = by0 + (int(np.median(ys)) if len(ys) else int((st['top'] + st['bottom']) / 2 - by0))
        rx, ry = st['sp'] * rng.uniform(1.2, 1.7), st['sp'] * rng.uniform(1.6, 2.4)
        a0 = rng.uniform(0, 2 * np.pi)
        span = 2 * np.pi * rng.uniform(1.02, 1.15)
        t = np.linspace(a0, a0 + span, 60)
        rr = 1 + 0.05 * np.sin(3 * t + rng.uniform(0, 6))
        pts = list(zip(x + rx * rr * np.cos(t), y + ry * rr * np.sin(t)))
        _hand_poly(dr, pts, rng, lw, 255)
        log.append(['circle', x, y])
    font_size = int(staves[0]['sp'] * 2.0)
    try:
        fnt = ImageFont.truetype(FONT_ITAL, font_size)
        fnt_s = ImageFont.truetype(FONT_SANS, int(font_size * 0.8))
    except OSError:
        fnt = fnt_s = ImageFont.load_default()

    def text(x, y, s, f, rot):
        tw = int(f.getlength(s)) + 8
        tl = Image.new('L', (tw, font_size * 2), 0)
        ImageDraw.Draw(tl).text((4, 0), s, fill=255, font=f)
        tl = tl.rotate(rot, expand=True, resample=Image.BICUBIC)
        layer.paste(255, (int(x), int(y)), tl)
    for _ in range(int(o.get('fake_triplets', 1))):
        st = staves[rng.integers(len(staves))]
        x = rng.uniform(st['x0'] + 0.2 * (st['x1'] - st['x0']), st['x1'] - 4 * st['sp'])
        text(x, st['top'] - 4.2 * st['sp'], '3', fnt, rng.uniform(-12, 12))
        log.append(['fake_3', int(x), int(st['top'] - 4.2 * st['sp'])])
    for _ in range(int(o.get('fingerings', 4))):
        st = staves[rng.integers(len(staves))]
        x = rng.uniform(st['x0'] + 0.15 * (st['x1'] - st['x0']), st['x1'] - 3 * st['sp'])
        text(x, st['top'] - 3.4 * st['sp'], str(rng.integers(1, 6)), fnt_s, rng.uniform(-8, 8))
        log.append(['digit', int(x)])
    for _ in range(int(o.get('ticks', 2))):
        st = staves[rng.integers(len(staves))]
        x = rng.uniform(st['x0'] + 0.1 * (st['x1'] - st['x0']), st['x1'] - 2 * st['sp'])
        y = st['top'] - 1.8 * st['sp']
        _hand_poly(dr, [(x, y), (x + 0.5 * st['sp'], y + 1.0 * st['sp']), (x + 1.4 * st['sp'], y - 0.6 * st['sp'])],
                   rng, lw, 255)
        log.append(['tick', int(x)])
    for word in o.get('words', ['rit.']):
        st = staves[rng.integers(len(staves))]
        x = rng.uniform(st['x0'] + 0.3 * (st['x1'] - st['x0']), st['x1'] - 8 * st['sp'])
        text(x, st['bottom'] + 4.5 * st['sp'], word, fnt, rng.uniform(-6, 6))
        log.append(['word', word, int(x)])
    if o.get('bracket', True):
        st = staves[rng.integers(len(staves))]
        x = rng.uniform(st['x0'] + 0.2 * (st['x1'] - st['x0']), st['x1'] - 10 * st['sp'])
        y = st['top'] - 2.6 * st['sp']
        L = rng.uniform(5, 9) * st['sp']
        _hand_poly(dr, [(x, y + st['sp']), (x, y), (x + L, y + rng.normal(0, 2)), (x + L, y + st['sp'])], rng, lw, 255)
        log.append(['bracket', int(x)])
    a = np.asarray(layer.filter(ImageFilter.GaussianBlur(0.6 * ctx['sc'])), dtype=np.float32) / 255.0
    grain = 0.55 + 0.45 * rng.random(a.shape).astype(np.float32)
    a = a * grain * float(o.get('strength', 0.65))
    col = bgcol(o.get('rgb', [95, 95, 100]), C)
    ctx['log'].append({'pencil_marks': log})
    m = a[:, :, None]
    return img * (1 - m) + np.minimum(img, col) * m


def op_punch_holes(img, o, ctx):
    C, dpi = ctx['C'], ctx['dpi']
    h, w = img.shape[:2]
    mm = dpi / 25.4
    n = int(o.get('n', 2))
    d = o.get('diameter_mm', 6.0) * mm
    edge = o.get('edge_mm', 12.0) * mm
    pitch = o.get('pitch_mm', 80.0 if n == 2 else 108.0 / 2) * mm
    side = o.get('side', 'left')
    bg = bgcol(o.get('bg', 25), C)
    cy0 = h / 2 - pitch * (n - 1) / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # holes must not cover music: move each hole vertically into the nearest gap
    # between staff bands (staff +- 2.5 staff spaces) that reach into the hole column
    placed = []
    for k in range(n):
        cy = cy0 + k * pitch
        cx = edge if side == 'left' else w - edge
        if side == 'top':
            cx, cy = w / 2 - pitch * (n - 1) / 2 + k * pitch, edge
        else:
            bands = [(st['top'] - 2.5 * st['sp'] - d / 2 - 4, st['bottom'] + 2.5 * st['sp'] + d / 2 + 4)
                     for st in ctx['staves']
                     if (side == 'left' and st['x0'] < cx + d) or (side == 'right' and st['x1'] > cx - d)]
            best = None
            for dy in range(0, h, 4):
                for c in (cy + dy, cy - dy):
                    if d < c < h - d and not any(lo < c < hi for lo, hi in bands) and \
                            all(abs(c - q) > 2 * d for q in placed):
                        best = c
                        break
                if best is not None:
                    break
            if best is None:
                continue
            cy = best
        placed.append(cy)
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        hole = np.clip(d / 2 - dist + 1, 0, 1)
        rim = np.clip(1 - np.abs(dist - d / 2 - 2) / 3, 0, 1) * 0.35
        img = img * (1 - rim[:, :, None]) * (1 - hole[:, :, None]) + bg * hole[:, :, None]
    ctx['log'].append({'punch_holes_xy_px': [[int(cx), int(q)] for q in placed]})
    return img


def op_staple(img, o, ctx):
    rng, C, dpi = ctx['rng'], ctx['C'], ctx['dpi']
    h, w = img.shape[:2]
    mm = dpi / 25.4
    L, Wd = 12 * mm, 0.9 * mm
    corner = o.get('corner', 'tl')
    cx = 10 * mm if 'l' in corner else w - 10 * mm
    cy = 10 * mm if 't' in corner else h - 10 * mm
    ang = math.radians(o.get('angle', 45 if corner in ('tl', 'br') else -45))
    lay = Image.new('L', (w, h), 0)
    hl = Image.new('L', (w, h), 0)
    sh = Image.new('L', (w, h), 0)
    dx, dy = math.cos(ang) * L / 2, -math.sin(ang) * L / 2
    ImageDraw.Draw(sh).line([(cx - dx + 3, cy - dy + 4), (cx + dx + 3, cy + dy + 4)], fill=150, width=int(Wd * 1.6))
    ImageDraw.Draw(lay).line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=255, width=int(Wd))
    ImageDraw.Draw(hl).line([(cx - dx, cy - dy - 1), (cx + dx, cy + dy - 1)], fill=255, width=max(1, int(Wd / 3)))
    s = gblur(np.asarray(sh, np.float32) / 255, 2 * ctx['sc'])[:, :, None]
    a = np.asarray(lay, np.float32)[:, :, None] / 255
    b = np.asarray(hl, np.float32)[:, :, None] / 255
    img = img * (1 - 0.6 * s)
    img = img * (1 - a) + bgcol(90, C) * a
    img = img * (1 - b) + bgcol(200, C) * b
    return img


def op_crop(img, o, ctx):
    """Edge of the original not captured (oversized page on the copier glass).
    'into_staff': staff spaces the cut reaches past the outermost staff end.  Right: cuts
    final barlines / staff ends (LilyPond keeps >= 1 staff space between the last note and
    the barline; the cut is limited to 0.8 staff space).  Left: clamped to <= 0, i.e. only
    instrument names, braces/brackets and bar numbers are cut, never clefs or key signatures."""
    C = ctx['C']
    h, w = img.shape[:2]
    st = ctx['staves']
    bg = bgcol(o.get('bg', 255), C)
    side = o.get('side', 'right')
    sp = st[0]['sp'] if st else 20
    into = min(float(o.get('into_staff', 0.4)), 0.8)
    if side == 'right':
        x = int(max(s['x1'] for s in st) - into * sp) if st else int(w * 0.95)
        img[:, x:] = bg
    elif side == 'left':
        # left: only the margin (instrument names, braces, system-start lines, bar numbers);
        # never into the staff, where clefs and key signatures start right at the line ends
        into = min(into, 0.0)
        x = int(min(s['x0'] for s in st) + into * sp) if st else int(w * 0.05)
        img[:, :x] = bg
    elif side == 'top':
        y = int(o.get('frac', 0.03) * h)
        img[:y] = bg
    else:
        y = int(o.get('frac', 0.03) * h)
        img[h - y:] = bg
    ctx['log'].append({'crop_x' if side in ('left', 'right') else 'crop_y': x if side in ('left', 'right') else y})
    return img


def op_halftone(img, o, ctx):
    """Re-screened print (e.g. a facsimile reprint): luminance halftoned with an AM dot
    screen at 'lpi' lines/inch and 'angle', supersampled x2 and resampled back -> moire."""
    C = ctx['C']
    h, w = img.shape[:2]
    lum = img.mean(axis=2)
    ss = int(o.get('supersample', 2))
    big = np.asarray(Image.fromarray(lum, mode='F').resize((w * ss, h * ss), Image.BILINEAR), np.float32)
    cell = ctx['dpi'] * ss / float(o.get('lpi', 85))
    th = math.radians(o.get('angle', 45))
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    u = (xx * math.cos(th) + yy * math.sin(th)) * (2 * math.pi / cell)
    v = (-xx * math.sin(th) + yy * math.cos(th)) * (2 * math.pi / cell)
    screen = 0.5 + 0.25 * (np.cos(u) + np.cos(v))
    del xx, yy, u, v
    dens = 1 - big / 255.0
    dots = (dens > screen).astype(np.float32)
    paper = float(o.get('paper', 250))
    inkv = float(o.get('ink', 25))
    out = paper * (1 - dots) + inkv * dots
    small = np.asarray(Image.fromarray(out, mode='F').resize((w, h), Image.BOX), np.float32)
    if C == 1:
        return small[:, :, None]
    tint = img / np.maximum(lum, 1)[:, :, None]
    return np.clip(tint * small[:, :, None], 0, 255)


# ---------------------------------------------------------------- capture geometry

def op_curl(img, o, ctx):
    h, w = img.shape[:2]
    sc = ctx['sc']
    side = o.get('side', 'left')
    if side == 'gutter':
        side = 'right' if ctx['page'] % 2 == 0 else 'left'
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    amp = o['amp'] * sc
    width = o.get('width', 0.25) * w
    t = np.clip((width - xx) / width, 0, 1) if side == 'left' else np.clip((xx - (w - width)) / width, 0, 1)
    dy = amp * t ** 2 * ((yy - h / 2) / (h / 2))
    dx = (amp * 0.6) * t ** 2 * (1 if side == 'left' else -1)
    xs, ys = xx - dx, yy - dy
    fill = ctx['paper_bg']
    return np.stack([remap(img[:, :, c], xs, ys, fill[c]) for c in range(img.shape[2])], axis=2)


def op_wave(img, o, ctx):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dy = o['amp'] * ctx['sc'] * np.sin(2 * np.pi * xx / (o.get('period', 1.3) * w) + o.get('phase', 0.3))
    fill = ctx['paper_bg']
    return np.stack([remap(img[:, :, c], xx, yy - dy, fill[c]) for c in range(img.shape[2])], axis=2)


def op_gutter(img, o, ctx):
    h, w = img.shape[:2]
    side = o.get('side', 'left')
    if side == 'gutter':
        side = 'right' if ctx['page'] % 2 == 0 else 'left'
    gw = int(o.get('width', 0.06) * w)
    prof = np.linspace(1, 0, gw, dtype=np.float32) ** 2 * o.get('dark', 0.55)
    if side == 'left':
        img[:, :gw] *= (1 - prof)[None, :, None]
    else:
        img[:, w - gw:] *= (1 - prof[::-1])[None, :, None]
    return img


def op_rotate(img, o, ctx):
    """skew on the scanner bed; expand=True so no music is lost; background = lid/bed colour"""
    C = img.shape[2]
    bg = o.get('bg', 235)
    bgv = tuple(int(x) for x in bgcol(bg, 3)) if C == 3 else int(bgcol(bg, 1)[0])
    im = to_pil(img).rotate(o['deg'], resample=Image.BICUBIC, expand=o.get('expand', True), fillcolor=bgv)
    return from_pil(im, C)


def op_rot90(img, o, ctx):
    return np.ascontiguousarray(np.rot90(img, k=int(o.get('k', 1)), axes=(0, 1)))


def op_scale(img, o, ctx):
    """content scaled about the centre inside the same canvas (page-to-page zoom mismatch)"""
    C = img.shape[2]
    h, w = img.shape[:2]
    f = float(o['factor'])
    im = to_pil(img).resize((int(w * f), int(h * f)), Image.LANCZOS)
    bgv = ctx['paper_bg']
    canvas = np.empty((h, w, C), np.float32)
    canvas[:] = bgv
    sm = from_pil(im, C)
    sh, sw = sm.shape[:2]
    oy, ox = (h - sh) // 2 + int(o.get('dy', 0) * h), (w - sw) // 2 + int(o.get('dx', 0) * w)
    ys, xs = max(0, oy), max(0, ox)
    ye, xe = min(h, oy + sh), min(w, ox + sw)
    canvas[ys:ye, xs:xe] = sm[ys - oy:ye - oy, xs - ox:xe - ox]
    return canvas


def perspective_coeffs(src, dst):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)).tolist()


def op_perspective(img, o, ctx):
    """phone capture: page on a table background, camera tilt (keystone) + jitter"""
    rng, C = ctx['rng'], img.shape[2]
    h, w = img.shape[:2]
    m = int(o.get('margin', 0.06) * w)
    bg = bgcol(o.get('bg', [70, 62, 55]), C)
    H, W = h + 2 * m, w + 2 * m
    canvas = np.empty((H, W, C), np.float32)
    canvas[:] = bg
    canvas += (14 * smooth_field((H, W), rng, (4, 4)))[:, :, None]
    canvas[m:m + h, m:m + w] = img
    jit = o.get('jitter', 0.03)
    ks = o.get('keystone', 0.0)
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    src = [(x + rng.uniform(-jit, jit) * W, y + rng.uniform(-jit, jit) * H) for x, y in dst]
    # keystone: top edge further from the camera -> appears narrower
    src[0] = (src[0][0] - ks * W, src[0][1])
    src[1] = (src[1][0] + ks * W, src[1][1])
    coeffs = perspective_coeffs(src, dst)
    fill = tuple(int(x) for x in bgcol(o.get('bg', [70, 62, 55]), 3)) if C == 3 else int(bg[0])
    im = to_pil(canvas).transform((W, H), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC, fillcolor=fill)
    return from_pil(im, C)


# ---------------------------------------------------------------- lighting

def op_gradient(img, o, ctx):
    rng = ctx['rng']
    h, w = img.shape[:2]
    ang = o.get('angle', rng.uniform(0, 2 * np.pi))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = ((xx / w - 0.5) * np.cos(ang) + (yy / h - 0.5) * np.sin(ang)) + 0.5
    return img * (1 - o['strength'] * np.clip(t, 0, 1))[:, :, None]


def op_vignette(img, o, ctx):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx / w - 0.5)) ** 2 + ((yy / h - 0.5) * 0.9) ** 2) / 0.7
    return img * (1 - o['strength'] * r ** 2)[:, :, None]


def op_blotch(img, o, ctx):
    f = np.clip(smooth_field(img.shape[:2], ctx['rng'], (5, 4), -0.5, 1), 0, 1)
    return img * (1 - o['strength'] * f)[:, :, None]


def op_shadow(img, o, ctx):
    """soft shadow of the phone / hand across one side of the page"""
    rng = ctx['rng']
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = rng.uniform(0, 2 * np.pi)
    d = (xx / w - 0.5) * np.cos(ang) + (yy / h - 0.5) * np.sin(ang)
    edge = o.get('pos', 0.25)
    s = 1 / (1 + np.exp(-(d - edge) / o.get('soft', 0.05)))
    return img * (1 - o['strength'] * s)[:, :, None]


# ---------------------------------------------------------------- optics / sensor

def op_blur(img, o, ctx):
    return per_channel(img, lambda a: gblur(a, o['sigma'] * ctx['sc']))


def op_motion_blur(img, o, ctx):
    L = max(2, int(o['length'] * ctx['sc']))
    th = math.radians(o.get('angle', 0))
    acc = np.zeros_like(img)
    for k in range(L):
        s = k - (L - 1) / 2
        dx, dy = int(round(s * math.cos(th))), int(round(s * math.sin(th)))
        acc += np.roll(np.roll(img, dy, axis=0), dx, axis=1)
    return acc / L


def op_noise(img, o, ctx):
    rng = ctx['rng']
    n = rng.normal(0, o['sigma'], img.shape[:2]).astype(np.float32)[:, :, None]
    if img.shape[2] == 3 and o.get('chroma', 0):
        n = n + rng.normal(0, o['chroma'], img.shape).astype(np.float32)
    return img + n


def op_saltpepper(img, o, ctx):
    rng = ctx['rng']
    h, w = img.shape[:2]
    n = int(o['amount'] * h * w)
    ys, xs = rng.integers(0, h, n), rng.integers(0, w, n)
    vals = np.where(rng.random(n) < o.get('dark_frac', 0.6), 15.0, 250.0)
    img[ys, xs] = vals[:, None]
    return img


def op_speckle(img, o, ctx):
    rng, sc = ctx['rng'], ctx['sc']
    h, w = img.shape[:2]
    n = int(o['per_mpx'] * (w * h) / 1e6)
    for _ in range(n):
        r = rng.uniform(0.6, 2.2) * sc
        cy, cx = rng.integers(0, h), rng.integers(0, w)
        y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
        x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
        img[y0:y1, x0:x1][mask] = 20 + rng.uniform(0, 60)
    return img


def op_binarize(img, o, ctx):
    """photocopy / fax: optional blur + noise, then global threshold -> 1-bit.
    thick copy = high threshold (strokes swell, beams merge); thin copy = low threshold
    (staff lines and thin stems break up)."""
    rng = ctx['rng']
    lum = img.mean(axis=2)
    if o.get('pre_blur'):
        lum = gblur(lum, o['pre_blur'] * ctx['sc'])
    if o.get('noise'):
        lum = lum + rng.normal(0, o['noise'], lum.shape).astype(np.float32)
    out = np.where(lum > o['threshold'], 255.0, 0.0).astype(np.float32)
    ctx['binary'] = True
    return out[:, :, None] if img.shape[2] == 1 else np.repeat(out[:, :, None], 3, axis=2)


def op_downsample(img, o, ctx):
    """scan at a lower resolution than the working one (sets the output dpi)"""
    C = img.shape[2]
    h, w = img.shape[:2]
    f = o['dpi'] / ctx['dpi']
    im = to_pil(img).resize((max(1, int(w * f)), max(1, int(h * f))), Image.BOX if f < 1 else Image.BICUBIC)
    ctx['out_dpi'] = o['dpi']
    return from_pil(im, C)


OPS = {k[3:]: v for k, v in globals().items() if k.startswith('op_')}
COVERAGE_OPS = {'ink_weight', 'ink_dropout'}


def two_up(images, o, ctx):
    """pair pages into book spreads (left = even index), with a dark gutter seam"""
    out = []
    for k in range(0, len(images), 2):
        L = images[k]
        R = images[k + 1] if k + 1 < len(images) else np.full_like(L, ctx['paper_bg'])
        h = max(L.shape[0], R.shape[0])
        C = L.shape[2]

        def padh(a):
            if a.shape[0] == h:
                return a
            p = np.empty((h, a.shape[1], C), np.float32)
            p[:] = ctx['paper_bg']
            p[:a.shape[0]] = a
            return p
        seam = int(o.get('seam_px', 6) * ctx['sc'])
        S = np.empty((h, seam, C), np.float32)
        S[:] = bgcol(o.get('seam', 40), C)
        out.append(np.concatenate([padh(L), S, padh(R)], axis=1))
    return out


def apply_variant(pages, V, workdir=None):
    """pages: clean gray uint8 arrays rendered at V['dpi'].  Returns (PIL images, out_dpi, log)."""
    rng = np.random.default_rng(V['seed'])
    C = 3 if V.get('color', 'gray') == 'rgb' else 1
    dpi = V['dpi']
    ctx_base = {'rng': rng, 'C': C, 'dpi': dpi, 'sc': dpi / 300.0, 'log': [], 'out_dpi': dpi}
    ops = V['ops']
    split = next((k for k, o in enumerate(ops) if o['op'] == 'two_up'), None)
    pre, post = (ops[:split], ops[split + 1:]) if split is not None else (ops, [])
    imgs = []
    for pi, pg in enumerate(pages):
        ctx = dict(ctx_base)
        ctx.update({'page': pi, 'clean': pg, 'staves': staff_info(pg), 'log': ctx_base['log']})
        paper_rgb = next((o.get('rgb', [246, 246, 244]) for o in ops if o['op'] == 'paper'), [246, 246, 244])
        ctx['paper_bg'] = bgcol(paper_rgb, C)
        cov = 1.0 - pg.astype(np.float32) / 255.0
        img = None
        for o in pre:
            if 'pages' in o and pi not in o['pages']:
                continue
            name = o['op']
            if name in COVERAGE_OPS:
                assert img is None, f'{name} must precede paper'
                cov = OPS[name](cov, o, ctx)
            elif name == 'paper':
                img = op_paper(cov, o, ctx)
            else:
                if img is None:
                    img = op_paper(cov, {}, ctx)
                img = OPS[name](img, o, ctx)
        if img is None:
            img = op_paper(cov, {}, ctx)
        ctx_base['out_dpi'] = ctx['out_dpi']
        ctx_base['binary'] = ctx.get('binary', False)
        imgs.append(np.clip(img, 0, 255))
    if split is not None:
        ctx = dict(ctx_base)
        ctx['paper_bg'] = bgcol(next((o.get('rgb', [246] * 3) for o in ops if o['op'] == 'paper'), [246] * 3), C)
        imgs = two_up(imgs, ops[split], ctx)
        for k in range(len(imgs)):
            ctx.update({'page': k, 'staves': [], 'clean': None})
            for o in post:
                if 'pages' in o and k not in o['pages']:
                    continue
                imgs[k] = np.clip(OPS[o['op']](imgs[k], o, ctx), 0, 255)
            ctx_base['out_dpi'] = ctx['out_dpi']
            ctx_base['binary'] = ctx.get('binary', ctx_base.get('binary', False))
    pil = []
    for a in imgs:
        im = to_pil(a)
        if ctx_base.get('binary'):
            im = im.convert('L').point(lambda v: 255 if v > 127 else 0).convert('1', dither=Image.NONE)
        pil.append(im)
    return pil, ctx_base['out_dpi'], ctx_base['log']


def save_pdf(images, dpi, out_pdf, fmt='jpeg', quality=75, jpeg_passes=1):
    """image-only PDF via img2pdf (lossless pass-through of the JPEG/PNG streams)"""
    with tempfile.TemporaryDirectory() as td:
        files = []
        for k, im in enumerate(images):
            if fmt == 'jpeg' and im.mode != '1':
                cur = im
                for _ in range(jpeg_passes - 1):
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


def describe(V):
    """short tags for a variant"""
    tags = []
    for o in V['ops']:
        n = o['op']
        if n == 'rotate':
            tags.append(f"rotation_{o['deg']:+g}deg")
        elif n == 'rot90':
            tags.append(f"page_rotated_{90 * o.get('k', 1)}deg" + (f"_p{o['pages']}" if 'pages' in o else ''))
        elif n == 'binarize':
            tags.append('binarized_photocopy_' + ('thick' if o['threshold'] >= 150 else 'thin'))
        elif n == 'paper':
            if V.get('color') == 'rgb':
                tags.append('coloured_paper_rgb')
            if o.get('texture'):
                tags.append('paper_texture')
            if o.get('bleed'):
                tags.append('bleed_through')
        elif n == 'downsample':
            tags.append(f"downsampled_{o['dpi']}dpi")
        elif n == 'two_up':
            tags.append('double_page_spread_2up')
        elif n == 'scale':
            tags.append('page_scale_mismatch')
        elif n == 'perspective':
            tags.append('perspective_phone_capture')
        else:
            tags.append(n)
    if V.get('format', 'jpeg') == 'jpeg':
        tags.append(f"jpeg_q{V.get('jpeg', 75)}")
    return tags
