"""Normalise the per-file degradation records of the six challenge categories (each generator
logged its damage in its own shape) into one set of damage-family tags per scan file.

    tags(record, meta, filename) -> sorted list of family names

Families (a file usually carries several):
  skew rot90 rot180 perspective curl_gutter spread_2up scale_mismatch lighting paper_colour
  bleed_through stain_foxing pencil holes_staple crop halftone_moire blur noise saltpepper
  jpeg_low(q<=35) jpeg(q 36-60) photocopy_bilevel ink_fade low_dpi(<=150) high_dpi(>=400)
  clean_control (degradation/*-clean scan.pdf only)
"""
from __future__ import annotations

import json
import re

FAMILY_KEYWORDS = [
    ('perspective', r'perspective|keystone|\bphone\b|"phone"|phone_photo'),
    ('curl_gutter', r'curl|gutter|"wave"|book'),
    ('spread_2up', r'two_up|spread2up|"spread_2up": \{|"spread_2up": \[|2-up|2up|double.page'),
    ('lighting', r'gradient|vignette|lighting|hand_shadow|"shadow"|lamp'),
    ('bleed_through', r'bleed'),
    ('stain_foxing', r'coffee|stain|foxing|blotch'),
    ('pencil', r'pencil|highlighter|ballpoint|circled_note|"annotations": \[\[\{|red_pen|fingering'),
    ('holes_staple', r'punch|"holes"|staple|"fold"|dogear|dog_ear'),
    ('crop', r'crop'),
    ('halftone_moire', r'halftone|moire'),
    ('blur', r'blur|"motion"|defocus'),
    ('saltpepper', r'saltpepper|salt_pepper|salt-and-pepper|salt & pepper'),
    ('photocopy_bilevel', r'binari|bilevel|photocopy|"1"\]|1-bit|ink_weight'),
    ('ink_fade', r'ink_dropout|"dropout"|"fade"|faded'),
    ('scale_mismatch', r'"scale"|scale_pages|page_scale|"op": "scale"'),
]


def _walk(o, key=''):
    if isinstance(o, dict):
        if 'op' in o and isinstance(o['op'], str):
            yield ('op:' + o['op'], o)
        for k, v in o.items():
            yield (k, v)
            yield from _walk(v, k)
    elif isinstance(o, list):
        if len(o) == 2 and isinstance(o[0], str):
            yield ('op:' + o[0], o[1])
        for v in o:
            yield from _walk(v, key)


def _num(x):
    try:
        return float(x)
    except Exception:
        return None


def rotations(rec):
    """-> (small skew degrees list, quarter-turn degrees list)"""
    skews, turns = [], []
    for k, v in _walk(rec):
        if k == 'op:rot90':
            kk = v.get('k', v.get('params')) if isinstance(v, dict) else v
            if isinstance(kk, (int, float)):
                turns.append(int(kk) * 90 % 360)
        elif k in ('page_rotated_deg',) and _num(v) is not None:
            turns.append(int(_num(v)) % 360)
        elif k in ('page_rotate',) and isinstance(v, dict):
            turns += [int(_num(x)) % 360 for x in v.values() if _num(x) is not None]
        elif k == 'op:rotate' and isinstance(v, dict):
            d = _num(v.get('deg', (v.get('params') or {}).get('deg') if isinstance(v.get('params'), dict) else None))
            if d is not None:
                (turns if abs(d) >= 45 else skews).append(d % 360 if abs(d) >= 45 else d)
        elif k in ('skew_rotation_deg', 'rotate', 'skew_deg') and _num(v) is not None:
            skews.append(_num(v))
        elif k in ('rotate_pages', 'skew_pages') and isinstance(v, dict):
            skews += [_num(x) for x in v.values() if _num(x) is not None]
    for t in re.findall(r'rotation_([+-]?\d+(?:\.\d+)?)deg|skew_(\d+(?:\.\d+)?)deg', json.dumps(rec)):
        x = _num(t[0] or t[1])
        if x is not None:
            skews.append(x)
    return [s for s in skews if 0.05 <= abs(s) <= 20], [t for t in turns if t]


def dpi_of(rec, meta, fname):
    for k in ('output_dpi', 'dpi'):
        if _num(rec.get(k)):
            return int(_num(rec[k]))
    d = meta.get('dpi')
    if isinstance(d, dict):
        d = d.get(fname)
    return int(_num(d)) if _num(d) else None


def jpeg_q(rec):
    s = json.dumps(rec).lower()
    qs = []
    if _num(rec.get('jpeg_quality')):
        qs.append(_num(rec['jpeg_quality']))
    qs += [float(x) for x in re.findall(r'jpeg[ _]?q(\d+)', s)]
    qs += [float(x) for x in re.findall(r'"jpeg": (\d+)', s)]
    qs += [float(x) for x in re.findall(r'"format": "jpeg", "quality": (\d+)', s)]
    qs += [float(x) for x in re.findall(r'"quality": (\d+)', s)]
    return min(qs) if qs else None


def _prune(o):
    if isinstance(o, dict):
        return {k: _prune(v) for k, v in o.items() if v not in (None, False, [], {}, '')}
    if isinstance(o, list):
        return [_prune(v) for v in o]
    return o


def tags(rec, meta, fname, pdf=None):
    """pdf: optional validator record of the file (pdfimages colour/ppi are used when given)"""
    if not isinstance(rec, dict):
        return []
    rec = _prune(rec)
    out = set()
    if meta.get('category') == 'degradation' and meta.get('variant') == 'clean' and fname == 'scan.pdf':
        out.add('clean_control')
    s = json.dumps(rec, ensure_ascii=False).lower()
    # drop the always-present scanner-bed edge shadow and paper/ink keys before keyword matching
    s2 = re.sub(r'"edge_shadow": [0-9.]+', '', s)
    for fam, rx in FAMILY_KEYWORDS:
        if re.search(rx, s2):
            out.add(fam)
    skews, turns = rotations(rec)
    if skews:
        out.add('skew')
    if any(t in (90, 270) for t in turns) or 'rotated_90' in s or 'rotated_270' in s:
        out.add('rot90')
    if any(t == 180 for t in turns) or 'rotated_180' in s or 'upside' in s:
        out.add('rot180')
    # colour paper scan
    if pdf and pdf.get('image_color'):
        if 'rgb' in pdf['image_color']:
            out.add('paper_colour')
    elif re.search(r'"(mode|color|colour)": "rgb"|"image_mode": \["rgb|coloured_paper|yellow', s):
        out.add('paper_colour')
    if re.search(r'"(noise|gaussian_noise_sigma|sigma)"', s) and 'noise' in s:
        out.add('noise')
    q = jpeg_q(rec)
    if q is not None and q <= 35:
        out.add('jpeg_low')
    elif q is not None and q <= 60:
        out.add('jpeg')
    ppi = (pdf or {}).get('image_ppi') or ([dpi_of(rec, meta, fname)] if dpi_of(rec, meta, fname) else [])
    if ppi and min(ppi) <= 150:
        out.add('low_dpi')
    if ppi and max(ppi) >= 400:
        out.add('high_dpi')
    return sorted(out)


def describe(rec, meta, fname):
    """short human summary of one file's damage"""
    if not isinstance(rec, dict):
        return ''
    for k in ('summary',):
        if isinstance(rec.get(k), str) and rec[k]:
            return rec[k]
    if isinstance(rec.get('tags'), list) and rec['tags']:
        return ', '.join(map(str, rec['tags']))
    return ', '.join(tags(rec, meta, fname))
