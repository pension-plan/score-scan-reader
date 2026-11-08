#!/usr/bin/env python3
"""Read symbol boxes from a LilyPond SVG tagged by svgtag.ly.
   svgboxes.py page.svg dpi -> JSON list of {cls, attrs, box:[x0,y0,x1,y1] in pixels at dpi}
Boxes include Bezier control points (slightly generous on curves)."""
import sys, re, json
import xml.etree.ElementTree as ET
NS = '{http://www.w3.org/2000/svg}'
num = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

def tf(s):
    """translate/scale chain -> (sx, sy, tx, ty) as x' = sx*x + tx"""
    sx, sy, tx, ty = 1.0, 1.0, 0.0, 0.0
    for name, args in re.findall(r'(translate|scale)\(([^)]*)\)', s or ''):
        v = [float(a) for a in num.findall(args)]
        if name == 'translate':
            a, b = v[0], (v[1] if len(v) > 1 else 0.0)
            tx, ty = tx + sx * a, ty + sy * b
        else:
            a, b = v[0], (v[1] if len(v) > 1 else v[0])
            sx, sy = sx * a, sy * b
    return sx, sy, tx, ty

def compose(p, c):
    return (p[0] * c[0], p[1] * c[1], p[0] * c[2] + p[2], p[1] * c[3] + p[3])

def path_pts(d):
    toks = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|' + num.pattern, d)
    pts, i, cmd, x, y, sx0, sy0 = [], 0, None, 0.0, 0.0, 0.0, 0.0
    nargs = dict(M=2, L=2, H=1, V=1, C=6, S=4, Q=4, T=2, A=7, Z=0)
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t):
            cmd = t; i += 1
            if cmd in 'Zz': x, y = sx0, sy0; continue
        n = nargs[cmd.upper()]
        v = [float(a) for a in toks[i:i + n]]; i += n
        rel = cmd.islower(); C = cmd.upper()
        if C == 'H': x = x + v[0] if rel else v[0]; pts.append((x, y))
        elif C == 'V': y = y + v[0] if rel else v[0]; pts.append((x, y))
        elif C == 'A':
            x, y = (x + v[5], y + v[6]) if rel else (v[5], v[6]); pts.append((x, y))
        else:
            for k in range(0, n, 2):
                px, py = (x + v[k], y + v[k + 1]) if rel else (v[k], v[k + 1])
                pts.append((px, py))
            x, y = pts[-1]
            if C == 'M':
                sx0, sy0 = x, y
                cmd = 'l' if rel else 'L'
    return pts

def elem_pts(e):
    tag = e.tag.replace(NS, '')
    if tag == 'path': return path_pts(e.get('d', ''))
    if tag == 'line':
        w = float(e.get('stroke-width', 0)) / 2
        x1, y1, x2, y2 = (float(e.get(k, 0)) for k in ('x1', 'y1', 'x2', 'y2'))
        return [(x1 - w, y1 - w), (x2 + w, y2 + w), (x1 + w, y1 + w), (x2 - w, y2 - w)]
    if tag == 'rect':
        x, y, w, h = (float(e.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        return [(x, y), (x + w, y + h)]
    if tag == 'polygon':
        v = [float(a) for a in num.findall(e.get('points', ''))]
        w = float(e.get('stroke-width', 0)) / 2
        return [(v[k] + dx, v[k + 1] + dy) for k in range(0, len(v), 2) for dx, dy in ((-w, -w), (w, w))]
    if tag in ('circle', 'ellipse'):
        cx, cy = float(e.get('cx', 0)), float(e.get('cy', 0))
        rx = float(e.get('r', e.get('rx', 0))); ry = float(e.get('r', e.get('ry', 0)))
        w = float(e.get('stroke-width', 0)) / 2
        return [(cx - rx - w, cy - ry - w), (cx + rx + w, cy + ry + w)]
    return []

def walk(e, T, out, cur):
    T = compose(T, tf(e.get('transform')))
    cls = e.get('class')
    if cls is not None and e.tag == NS + 'g':
        cur = {'cls': cls, 'attrs': {k[5:]: v for k, v in e.attrib.items() if k.startswith('data-') and v}, 'pts': []}
        out.append(cur)
    if cur is not None:
        for (px, py) in elem_pts(e):
            cur['pts'].append((T[0] * px + T[2], T[1] * py + T[3]))
    for ch in e:
        walk(ch, T, out, cur)

def main(svg, dpi):
    root = ET.parse(svg).getroot()
    vb = [float(a) for a in root.get('viewBox').split()]
    wmm = float(root.get('width').replace('mm', ''))
    k = wmm / vb[2] * dpi / 25.4
    out = []
    walk(root, (1, 1, 0, 0), out, None)
    res = []
    for o in out:
        if not o['pts']: continue
        xs = [p[0] for p in o['pts']]; ys = [p[1] for p in o['pts']]
        res.append({'cls': o['cls'], 'attrs': o['attrs'],
                    'box': [round((min(xs) - vb[0]) * k, 1), round((min(ys) - vb[1]) * k, 1), round((max(xs) - vb[0]) * k, 1), round((max(ys) - vb[1]) * k, 1)]})
    return {'svg': svg, 'dpi': dpi, 'unit_px': k, 'staff_space_px': k * 1.0, 'symbols': res}

if __name__ == '__main__':
    print(json.dumps(main(sys.argv[1], float(sys.argv[2]))))
