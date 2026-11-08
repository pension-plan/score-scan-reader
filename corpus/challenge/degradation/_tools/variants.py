"""Variant catalogue: every piece x every damage type, 3 strengths each
(scan-mild.pdf, scan.pdf, scan-severe.pdf).  Each function returns
{'tags': [...], 'files': {'scan': spec, 'scan-mild': spec, 'scan-severe': spec},
 'notes': str, 'limits': str}.  Specs are plain JSON (see damage.py)."""
from __future__ import annotations

import copy

import numpy as np

PIECE_IDS = {'hymn': 'agrace-satb', 'melody': 'wind-melody', 'piano': 'andantino-piano',
             'piano2p': 'twinkle-piano2p'}
VOCAB = {'hymn': 'hymn', 'melody': 'melody', 'piano': 'piano', 'piano2p': 'piano'}

LID = {'color': [236, 236, 234], 'noise': 2, 'edge_shadow': 0.35}
DARK = {'color': [32, 32, 34], 'noise': 4, 'texture': 4}
TABLE = {'color': [104, 84, 66], 'noise': 4, 'texture': 18}


def base_content(**kw):
    c = {'paper': {'color': 246, 'texture': 2}, 'ink_color': 22}
    c.update(kw)
    return c


def spec(dpi=300, content=None, page_geom=None, glob=None, out=None, bg=None, **kw):
    s = {'dpi': dpi, 'content': content if content is not None else base_content(),
         'page_geom': page_geom or [], 'global': glob or [], 'bg': bg or dict(LID),
         'out': out or {'mode': 'L', 'format': 'jpeg', 'quality': 80}}
    s.update(kw)
    return s


def L(q=80, **kw):
    d = {'mode': 'L', 'format': 'jpeg', 'quality': q}
    d.update(kw)
    return d


def RGB(q=80, **kw):
    d = {'mode': 'RGB', 'format': 'jpeg', 'quality': q, 'subsampling': 2}
    d.update(kw)
    return d


# ---------------------------------------------------------------- variants
def v_clean(pk, info, rng):
    return {'tags': ['control_clean'],
            'files': {'scan': spec(content={'paper': {'color': 255}, 'ink_color': 0}, bg={'color': [255, 255, 255]},
                                   out={'mode': 'L', 'format': 'png'}),
                      'scan-mild': spec(glob=[['bed', {'margin_mm': 2}], ['rotate', {'deg': 0.3}],
                                              ['noise', {'sigma': 2}]], out=L(85))},
            'notes': 'Clean control: scan.pdf is the undamaged 300 dpi raster (lossless PNG, image-only); '
                     'scan-mild.pdf is a typical good flatbed scan (0.3 deg skew, paper tone, light noise, JPEG 85). '
                     'No severe file. Use as the per-piece baseline when comparing damage types.',
            'limits': ''}


def v_skew(pk, info, rng):
    def mk(deg, extra, q, deg2=None):
        s = spec(glob=[['bed', {'margin_mm': 6}], ['rotate', {'deg': deg}]] + extra, out=L(q))
        if deg2 is not None and pk == 'piano2p':
            s['page_overrides'] = {'1': {'global': [['bed', {'margin_mm': 6}], ['rotate', {'deg': deg2}]] + extra}}
        return s
    return {'tags': ['skew', 'skew_large', 'scanner_bed_visible'],
            'files': {'scan-mild': mk(2.0, [['noise', {'sigma': 2}]], 80, -1.5),
                      'scan': mk(-6.5, [['noise', {'sigma': 3}]], 75, 5.0),
                      'scan-severe': mk(10.0, [['blur', {'sigma': 0.6}], ['noise', {'sigma': 4}]], 65, -8.0)},
            'notes': 'Whole page rotated on a larger scanner bed (page edges visible): mild 2 deg, scan -6.5 deg, '
                     'severe 10 deg (positive = counter-clockwise). For the 2-page piece page 2 is skewed in the '
                     'opposite direction. Staff lines are far from horizontal: deskew is required.',
            'limits': ''}


def v_rot90(pk, info, rng):
    if pk == 'piano2p':
        files = {'scan-mild': spec(glob=[['rot90', 1]], out=L(85)),
                 'scan': spec(glob=[['rot90', 3], ['bed', {'margin_mm': 5}], ['rotate', {'deg': 0.8}],
                                    ['noise', {'sigma': 2}]], out=L(80)),
                 'scan-severe': spec(glob=[['rot90', 1], ['bed', {'margin_mm': 5}], ['rotate', {'deg': -4}],
                                           ['blur', {'sigma': 0.7}], ['noise', {'sigma': 5}]], out=L(55),
                                     page_overrides={'1': {'global': [['rot90', 3], ['bed', {'margin_mm': 5}],
                                                                      ['rotate', {'deg': 2.5}], ['blur', {'sigma': 0.7}],
                                                                      ['noise', {'sigma': 5}]]}})}
        note = ('Pages scanned sideways (landscape images): mild both pages 90 deg CCW; scan both 90 deg CW + 0.8 deg; '
                'severe page 1 90 deg CCW and page 2 90 deg CW (opposite directions) plus skew, blur, JPEG 55.')
        tags = ['rotated_90', 'landscape_image', 'mixed_orientation']
    else:
        files = {'scan-mild': spec(glob=[['rot90', 1]], out=L(85)),
                 'scan': spec(glob=[['rot90', 3], ['bed', {'margin_mm': 5}], ['rotate', {'deg': 0.8}],
                                    ['noise', {'sigma': 2}]], out=L(80)),
                 'scan-severe': spec(glob=[['rot90', 1], ['bed', {'margin_mm': 5}], ['rotate', {'deg': -4}],
                                           ['blur', {'sigma': 0.7}], ['noise', {'sigma': 5}]], out=L(55))}
        note = ('Page scanned sideways (landscape image): mild exactly 90 deg CCW; scan 90 deg CW + 0.8 deg skew; '
                'severe 90 deg CCW + -4 deg skew, blur, noise, JPEG 55. The app must detect the orientation.')
        tags = ['rotated_90', 'landscape_image']
    return {'tags': tags, 'files': files, 'notes': note, 'limits': ''}


def v_rot180(pk, info, rng):
    g_m = [['rot90', 2]]
    g_s = [['rot90', 2], ['bed', {'margin_mm': 5}], ['rotate', {'deg': 1.2}], ['noise', {'sigma': 2}]]
    g_v = [['rot90', 2], ['bed', {'margin_mm': 5}], ['rotate', {'deg': -6}], ['gradient', {'strength': 0.2}],
           ['blur', {'sigma': 0.8}], ['noise', {'sigma': 4}]]
    up_s = [['bed', {'margin_mm': 5}], ['rotate', {'deg': -0.6}], ['noise', {'sigma': 2}]]
    if pk == 'piano2p':
        files = {'scan-mild': spec(glob=[], page_overrides={'1': {'global': g_m}}, out=L(85)),
                 'scan': spec(glob=up_s, page_overrides={'1': {'global': g_s}}, out=L(80)),
                 'scan-severe': spec(glob=[['rot90', 3], ['bed', {'margin_mm': 5}], ['rotate', {'deg': 2}],
                                           ['noise', {'sigma': 4}]], page_overrides={'1': {'global': g_v}}, out=L(60))}
        note = ('Mixed orientation: page 1 upright, page 2 upside down (180 deg) in mild/scan; severe has page 1 '
                'rotated 90 deg CW and page 2 180 deg + -6 deg. Each page needs its own orientation fix.')
        tags = ['rotated_180', 'mixed_orientation', 'upside_down_page']
    else:
        files = {'scan-mild': spec(glob=g_m, out=L(85)), 'scan': spec(glob=g_s, out=L(80)),
                 'scan-severe': spec(glob=g_v, out=L(60))}
        note = 'Page upside down (180 deg): mild exact, scan +1.2 deg, severe -6 deg skew + lighting gradient + blur.'
        tags = ['rotated_180', 'upside_down_page']
    return {'tags': tags, 'files': files, 'notes': note, 'limits': ''}


def v_phone(pk, info, rng):
    c = base_content(paper={'color': [244, 242, 236], 'texture': 3})
    mild = spec(dpi=250, content=c, bg=dict(TABLE), out=RGB(80),
                glob=[['perspective', {'jitter': 0.02, 'keystone': 0.02, 'margin': 0.05}],
                      ['gradient', {'strength': 0.12, 'angle': 30}], ['vignette', {'strength': 0.1}],
                      ['color_cast', {'rgb': [255, 248, 236]}], ['blur', {'sigma': 0.8}],
                      ['noise', {'sigma': 3, 'chroma': 2}]])
    scan = spec(dpi=250, content=c, bg=dict(TABLE), out=RGB(65),
                glob=[['perspective', {'jitter': 0.045, 'keystone': 0.05, 'margin': 0.06}],
                      ['shadow', {'strength': 0.35, 'pos': 0.22, 'angle': 140}],
                      ['gradient', {'strength': 0.2, 'angle': 250}], ['vignette', {'strength': 0.25}],
                      ['color_cast', {'rgb': [255, 244, 225]}], ['blur', {'sigma': 1.1}],
                      ['noise', {'sigma': 5, 'chroma': 3}]])
    sev = spec(dpi=200, content=c, bg=dict(TABLE), out=RGB(45),
               glob=[['perspective', {'jitter': 0.08, 'keystone': 0.09, 'margin': 0.07}],
                     ['shadow', {'strength': 0.5, 'pos': 0.1, 'angle': 200}], ['blotch', {'strength': 0.2}],
                     ['vignette', {'strength': 0.35}], ['color_cast', {'rgb': [255, 236, 210]}],
                     ['motion', {'length': 7, 'angle': 30}], ['blur', {'sigma': 1.4}],
                     ['noise', {'sigma': 7, 'chroma': 4}]])
    return {'tags': ['perspective_phone', 'keystone', 'uneven_lighting', 'vignette', 'hand_shadow', 'rgb_scan',
                     'background_visible'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Phone photo of the page on a wooden table: random corner jitter + keystone (top narrower), '
                     'warm colour cast, lighting gradient, vignette; scan/severe add a soft hand/phone shadow; '
                     'severe adds motion blur and JPEG 45 at 200 dpi.',
            'limits': ''}


def v_book(pk, info, rng):
    mild = spec(page_geom=[['gutter', {'width': 0.06, 'dark': 0.35}]],
                glob=[['bed', {'margin_mm': 4}], ['rotate', {'deg': 0.4}], ['noise', {'sigma': 2}]], out=L(80))
    scan = spec(page_geom=[['curl', {'amp_mm': 6, 'width': 0.3, 'shade': 0.25}],
                           ['gutter', {'width': 0.08, 'dark': 0.6}]], bg=dict(DARK),
                glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': -1.0}], ['gradient', {'strength': 0.1}],
                      ['noise', {'sigma': 3}]], out=L(70))
    sev = spec(page_geom=[['curl', {'amp_mm': 13, 'width': 0.4, 'shade': 0.4}], ['wave', {'amp_mm': 2, 'period': 1.4}],
                          ['gutter', {'width': 0.12, 'dark': 0.8}]], bg=dict(DARK),
               glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': 2.5}], ['vignette', {'strength': 0.2}],
                     ['blur', {'sigma': 0.8}], ['noise', {'sigma': 4}]], out=L(60))
    return {'tags': ['book_gutter_shadow', 'page_curl', 'warped_staff_lines', 'lid_open_dark_border'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Bound book pressed on a flatbed: dark gutter shadow on the binding side (left for a recto, '
                     'right for a verso); scan/severe curl the page near the gutter so staff lines bend and '
                     'compress, lid open (dark surround). Severe: 13 mm curl + wave + 80% gutter darkening.',
            'limits': ''}


def v_yellowed(pk, info, rng):
    mild = spec(content=base_content(paper={'color': [246, 240, 222], 'texture': 3, 'age_edges': 0.15},
                                     ink_color=[40, 36, 32]),
                glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.5}], ['noise', {'sigma': 2}]], out=RGB(80))
    scan = spec(content=base_content(paper={'color': [238, 226, 192], 'texture': 5, 'fibers': 25, 'age_edges': 0.35},
                                     ink_color=[58, 46, 36], ink_var=25, fade=0.1,
                                     foxing={'n': 40, 'strength': 0.4}),
                glob=[['bed', {'margin_mm': 4}], ['rotate', {'deg': -0.8}], ['noise', {'sigma': 3, 'chroma': 2}]],
                out=RGB(70))
    sev = spec(content=base_content(paper={'color': [222, 200, 150], 'texture': 8, 'fibers': 60, 'age_edges': 0.6},
                                    ink_color=[78, 60, 42], ink_var=40, fade=0.25,
                                    foxing={'n': 150, 'strength': 0.55, 'size_mm': [0.4, 3.5]},
                                    bleed={'amount': 0.1, 'blur': 2.0, 'color': [110, 85, 60]}),
               glob=[['bed', {'margin_mm': 4}], ['rotate', {'deg': -1.5}], ['gradient', {'strength': 0.15}],
                     ['blur', {'sigma': 0.7}], ['noise', {'sigma': 5, 'chroma': 3}]], out=RGB(55))
    return {'tags': ['yellowed_paper', 'rgb_scan', 'paper_texture', 'paper_fibres', 'foxing', 'faded_ink',
                     'low_contrast'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Aged paper in an RGB scan: cream to brown paper, brown faded ink with uneven density, age '
                     'darkening at the edges, paper fibres, foxing spots (scan 40, severe 150 spots up to 3.5 mm, '
                     'which can resemble dots/staccato marks). Severe adds faint bleed-through and blur.',
            'limits': 'Foxing spots are random brown dots, not music; some can sit on staff lines and look like '
                      'staccato dots or tiny noteheads. Truth contains none of them.'}


def v_bleed(pk, info, rng):
    def mk(a, blur, paper, extra, q):
        return spec(content=base_content(paper={'color': paper, 'texture': 4},
                                         bleed={'amount': a, 'blur': blur, 'shift_mm': [3, -2]}),
                    glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.4}]] + extra, out=L(q))
    return {'tags': ['bleed_through', 'mirrored_reverse_page', 'low_contrast'],
            'files': {'scan-mild': mk(0.08, 2.5, 244, [['noise', {'sigma': 2}]], 80),
                      'scan': mk(0.2, 2.0, 240, [['noise', {'sigma': 3}]], 75),
                      'scan-severe': mk(0.38, 1.5, 232, [['gradient', {'strength': 0.12}], ['noise', {'sigma': 4}]],
                                        65)},
            'notes': 'Thin paper: the (mirrored, blurred, shifted) music of the reverse side shows through - its '
                     'own staves, clefs and notes appear as grey ghosts, 8% / 20% / 38% strength. The reverse '
                     'page is another piece of this corpus, so ghost notes are a different piece entirely.',
            'limits': 'Ghost notes from the reverse page are NOT part of the truth and must be ignored.'}


def _stain_pos(info, rng, over_music=True):
    st = info['staves']
    if over_music and st:
        s = st[int(rng.integers(0, len(st)))]
        return float(rng.uniform(s['x0'] + 10, s['x1'] - 10)), float((s['top'] + s['bottom']) / 2 + rng.uniform(-8, 8))
    w, h = info['size_mm']
    return float(rng.uniform(15, w - 15)), float(rng.uniform(15, h - 15))


def v_stain_pencil(pk, info, rng):
    voc = VOCAB[pk]
    fing = 1 if pk.startswith('piano') else 0
    x, y = _stain_pos(info, rng, False)
    mild = spec(content=base_content(
        stains=[{'x_mm': x, 'y_mm': y, 'radius_mm': 28, 'strength': 0.5}],
        annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 2, 'texts': 1, 'breaths': 2, 'fingerings': 2 * fing,
                      'alpha': 0.55, 'width_mm': 0.3}]),
        glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.3}], ['noise', {'sigma': 2}]], out=RGB(80))
    x1, y1 = _stain_pos(info, rng, True)
    x2, y2 = _stain_pos(info, rng, False)
    scan = spec(content=base_content(
        stains=[{'x_mm': x1, 'y_mm': y1, 'radius_mm': 34, 'strength': 1.0},
                {'x_mm': x2, 'y_mm': y2, 'radius_mm': 22, 'strength': 0.8, 'partial': 1.2}],
        foxing={'n': 12, 'strength': 0.35, 'color': [140, 95, 50]},
        annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 5, 'texts': 3, 'breaths': 3, 'arrows': 1,
                      'brackets': 1, 'fingerings': 5 * fing, 'alpha': 0.7, 'width_mm': 0.35}]),
        glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': -0.6}], ['noise', {'sigma': 3, 'chroma': 2}]], out=RGB(72))
    stains = []
    for k in range(3):
        xx, yy = _stain_pos(info, rng, k < 2)
        stains.append({'x_mm': xx, 'y_mm': yy, 'radius_mm': [42, 30, 18][k], 'strength': [1.2, 1.0, 1.4][k],
                       'fill': [0.2, 0.12, 0.3][k], **({'partial': float(rng.uniform(0, 6.28))} if k == 1 else {})})
    sev = spec(content=base_content(
        stains=stains, highlighter=[{'len_mm': 45}, {'len_mm': 60, 'color': [255, 150, 200], 'alpha': 0.45}],
        foxing={'n': 30, 'strength': 0.45, 'color': [140, 95, 50]},
        annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 8, 'texts': 5, 'breaths': 4, 'arrows': 2,
                      'brackets': 2, 'scribbles': 2, 'fingerings': 9 * fing, 'alpha': 0.8, 'width_mm': 0.4},
                     {'tool': 'pen', 'vocab': voc, 'circles': 3, 'texts': 2, 'color': [35, 55, 160], 'alpha': 0.85,
                      'width_mm': 0.4}]),
        glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 1.0}], ['blur', {'sigma': 0.5}],
              ['noise', {'sigma': 4, 'chroma': 2}]], out=RGB(65))
    return {'tags': ['coffee_stain', 'pencil_annotations', 'circled_notes', 'handwritten_text', 'breath_marks',
                     'rgb_scan'] + (['handwritten_fingering'] if fing else []),
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Rehearsal copy: coffee ring stains (scan: one ring over the music), graphite pencil marks - '
                     'circled notes, handwritten words ("rit.", "breathe", "p", "cresc." ...), breath ticks/commas, '
                     'arrows, phrase arcs' + (', fingering digits above notes' if fing else '') + '. Severe adds '
                     'three stains, yellow and pink highlighter over staff passages, blue ballpoint circles/words '
                     'and margin scribbles. Exact positions of every mark are listed per file in meta.annotations.',
            'limits': 'Handwritten marks (including handwritten dynamics such as "p", "mf", "cresc.", "rit." and '
                      'fingerings) are NOT in the truth: the truth only contains the engraved music. A conversion '
                      'that adds them as dynamics/words/fingerings is wrong for scoring purposes.'}


def v_holes(pk, info, rng):
    x0 = info.get('staff_x0_mm', 15)
    top = info.get('music_top_mm', 40)
    w = info['size_mm'][0]
    mild = spec(content=base_content(holes={'x_mm': 9, 'offsets_mm': [-40, 40], 'diam_mm': 5.5}),
                glob=[['bed', {'margin_mm': 3}], ['noise', {'sigma': 2}]], out=L(80))
    scan = spec(content=base_content(holes={'x_mm': 10, 'offsets_mm': [-108, 0, 108], 'diam_mm': 6.5},
                                     staple={'x_mm': 12, 'y_mm': 11, 'len_mm': 12, 'angle': 35}),
                bg=dict(DARK), glob=[['bed', {'margin_mm': 4}], ['rotate', {'deg': -0.7}], ['noise', {'sigma': 3}]],
                out=L(75))
    ear = max(8.0, min(24.0, top - 4.0, (w - info.get('staff_x1_mm', w - 12)) + top - 6))
    sev = spec(content=base_content(holes={'x_mm': x0 - 1.0, 'offsets_mm': [-120, -40, 40, 120], 'diam_mm': 7},
                                    staple={'x_mm': 14, 'y_mm': 10, 'len_mm': 13, 'angle': 50},
                                    dogear={'corner': 'tr', 'size_mm': round(ear, 1)}),
               bg=dict(DARK), glob=[['bed', {'margin_mm': 4}], ['rotate', {'deg': 1.5}], ['noise', {'sigma': 3}]],
               out=L(70))
    return {'tags': ['punch_holes', 'staple', 'dog_ear', 'lid_open_dark_border'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Filing damage: mild 2 ISO punch holes in the margin (show the white lid); scan 3 US holes '
                     '(black, lid open) + a staple at the top-left; severe 4 holes centred 1 mm left of the staff '
                     'start (they bite into braces/brackets, the system-start barline and possibly the left edge '
                     'of a clef where they meet a staff) + staple + folded top-right corner.',
            'limits': 'Severe: where a hole meets a system its left end (brace/bracket/start barline, part of the '
                      'clef) is physically missing; the folded corner can hide header text (composer/arranger). '
                      'Music content is unchanged and the truth is complete.'}


def v_crop(pk, info, rng):
    x0, x1 = info['staff_x0_mm'], info['staff_x1_mm']
    lg, rg = info['left_gap_mm'], info['right_gap_mm']
    lgm, rgm = info['left_gap_music_mm'], info['right_gap_music_mm']
    bx0, by0, bx1, by1 = info['ink_bbox_mm']
    cut_l = round(min(0.8, max(0.0, lg - 0.3)), 2)
    cut_r = round(min(0.8, max(0.0, rg - 0.3)), 2)
    sev_l = round(max(0.0, lgm - 0.2), 2)
    sev_r = round(max(0.0, rgm - 0.2), 2)
    top_sev = round(info['header_cut_mm'], 1)
    mild = spec(content=base_content(crop={'left_mm': x0 - 0.4, 'right_mm': x1 + 0.4, 'top_mm': by0 - 2,
                                           'bottom_mm': by1 + 2}),
                glob=[['noise', {'sigma': 2}]], out=L(80))
    scan = spec(content=base_content(crop={'left_mm': x0 + cut_l, 'right_mm': x1 - cut_r, 'top_mm': by0 - 1,
                                           'bottom_mm': by1 + 1}),
                glob=[['noise', {'sigma': 2}]], out=L(78))
    sev = spec(content=base_content(crop={'left_mm': x0 + sev_l, 'right_mm': x1 - sev_r, 'top_mm': top_sev,
                                          'bottom_mm': by1 + 0.6}),
               glob=[['noise', {'sigma': 3}]], out=L(70))
    return {'tags': ['cropped_edges', 'cropped_staff_ends', 'no_margins', 'missing_system_barlines'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': f'Image edges cut through the staves. Mild: tight crop 0.4 mm outside the staff ends (braces/'
                     f'brackets cut off). Scan: {cut_l} mm cut into the staff starts and {cut_r} mm off the staff '
                     f'ends (start barline / brace and end barlines thinned or gone where the cut allows). Severe: '
                     f'header (title, credits) cropped away, {sev_l} mm cut into the staff starts (up to just '
                     f'before the first clef / name / lyric) and {sev_r} mm off the ends. Cut amounts were computed '
                     f'from the clean raster so that no clef, notehead, stem, accidental, lyric or part name is '
                     f'removed (only staff-line ends, brackets/braces and barlines).',
            'limits': 'Barlines at system starts/ends (incl. the final barline) may be partly or completely cut '
                      'off - they are still present in the truth. Severe: title/composer header text is not '
                      'visible; ignore work-title/creators when scoring.'}


def v_halftone(pk, info, rng):
    def mk(lpi, ang, pt, it, rs, extra, q):
        return spec(content=base_content(halftone={'lpi': lpi, 'angle': ang, 'paper_tone': pt, 'ink_tone': it,
                                                   'rescale': rs}, paper={'color': 248, 'texture': 0}),
                    glob=extra, out=L(q))
    return {'tags': ['halftone', 'moire', 'screened_reprint'],
            'files': {'scan-mild': mk(150, 45, 0.06, 0.95, 1.0, [['blur', {'sigma': 0.4}], ['noise', {'sigma': 2}]], 85),
                      'scan': mk(110, 15, 0.10, 0.9, 0.97, [['blur', {'sigma': 0.5}], ['noise', {'sigma': 3}]], 70),
                      'scan-severe': mk(85, 30, 0.18, 0.85, 0.93, [['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.7}],
                                                                   ['blur', {'sigma': 0.6}], ['noise', {'sigma': 4}]],
                                        50)},
            'notes': 'Page reproduced through a clustered-dot halftone screen (offset reprint of a photo of the '
                     'page) and re-scanned by point sampling, giving moire: every stroke and the paper tone are '
                     'made of dots. mild 150 lpi/45 deg, scan 110 lpi/15 deg with 0.97 rescale, severe 85 lpi/30 deg, '
                     '18% paper tone, 0.93 rescale + 0.7 deg rotation and JPEG 50.',
            'limits': 'The 0.97 / 0.93 rescale makes the music slightly smaller than the page (centred).'}


def v_jpeg(pk, info, rng):
    def mk(q, passes, extra):
        return spec(glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.5}]] + extra,
                    out={'mode': 'L', 'format': 'jpeg', 'quality': q, 'passes': passes})
    return {'tags': ['jpeg_artifacts', 'jpeg_q15', 'recompressed'],
            'files': {'scan-mild': mk(60, 1, [['noise', {'sigma': 2}]]),
                      'scan': mk(30, 2, [['noise', {'sigma': 3}]]),
                      'scan-severe': mk(15, 2, [['noise', {'sigma': 4}]])},
            'notes': 'JPEG blocking/ringing: mild quality 60; scan quality 30 after one earlier re-save; severe '
                     'quality 15 after a re-save (8x8 blocks visible, thin staff lines and stems smeared).',
            'limits': ''}


def v_photocopy_thin(pk, info, rng):
    def mk(thr, blur, noise, extra, fade=0.0):
        c = base_content(paper={'color': 250, 'texture': 1})
        if fade:
            c['fade'] = fade
        return spec(content=c, glob=extra, out={'mode': '1', 'format': 'png',
                                                'binarize': {'thr': thr, 'pre_blur': blur, 'noise': noise}})
    return {'tags': ['binarized', 'photocopy', 'photocopy_thin', 'broken_staff_lines', 'thin_strokes'],
            'files': {'scan-mild': mk(115, 0.6, 8, []),
                      'scan': mk(85, 0.8, 10, []),
                      'scan-severe': mk(70, 0.9, 12, [['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.6}],
                                                      ['speckle', {'per_mpx': 40, 'max_r': 1.5}]], fade=0.25)},
            'notes': 'Light photocopy, 1-bit: low binarisation threshold so only the darkest ink survives - staff '
                     'lines, stems, ledger lines, slurs and hollow noteheads thin out and break up. mild thr 115, '
                     'scan thr 85, severe thr 70 + patchy faded ink + 0.6 deg skew + toner dust.',
            'limits': 'Severe: some staff-line segments, ledger lines, ties and lyric hyphens/extenders vanish '
                      'completely; the truth still contains them.'}


def v_photocopy_thick(pk, info, rng):
    def mk(thr, blur, noise, iw, dil, extra, bg=None):
        return spec(content=base_content(ink_weight=iw, paper={'color': 250, 'texture': 1}), glob=extra,
                    bg=bg or dict(LID),
                    out={'mode': '1', 'format': 'png',
                         'binarize': {'thr': thr, 'pre_blur': blur, 'noise': noise, 'dilate': dil}})
    return {'tags': ['binarized', 'photocopy', 'photocopy_thick', 'merged_symbols', 'filled_noteheads',
                     'toner_specks', 'scanner_border'],
            'files': {'scan-mild': mk(170, 0.8, 8, 1, 0, []),
                      'scan': mk(195, 1.0, 10, 1, 1, [['speckle', {'per_mpx': 150}],
                                                      ['border', {'side': 'top', 'width_mm': 4}]]),
                      'scan-severe': mk(210, 1.3, 11, 2, 1, [['bed', {'margin_mm': 4}], ['rotate', {'deg': -1.2}],
                                                             ['speckle', {'per_mpx': 400}],
                                                             ['saltpepper', {'amount': 0.002, 'pepper_ratio': 0.8}],
                                                             ['border', {'side': 'left', 'width_mm': 6}]],
                                        bg=dict(DARK))},
            'notes': 'Dark photocopy, 1-bit: high threshold + ink spread - noteheads fill in (half notes start to '
                     'look like quarters), beams/slurs/ties merge with staff lines, lyrics thicken. scan adds toner '
                     'specks and a black lid edge; severe adds -1.2 deg skew, black surround, heavy specks and '
                     'pepper noise.',
            'limits': 'Severe: some hollow (half/whole) noteheads may be visually filled; durations remain as in the '
                      'truth (they are recoverable from beat counting only).'}


def v_lowdpi(pk, info, rng):
    return {'tags': ['low_dpi', 'low_dpi_100'],
            'files': {'scan-mild': spec(dpi=150, glob=[['noise', {'sigma': 2}]], out=L(75)),
                      'scan': spec(dpi=100, glob=[['noise', {'sigma': 2}]], out=L(70)),
                      'scan-severe': spec(dpi=100, glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 1.5}],
                                                         ['blur', {'sigma': 0.8}], ['noise', {'sigma': 3}]],
                                          out=L(45))},
            'notes': 'Low resolution: mild 150 dpi, scan 100 dpi (staff space ~7 px, lyrics ~10 px high), severe '
                     '100 dpi + 1.5 deg skew + blur + JPEG 45.',
            'limits': ''}


def v_highdpi(pk, info, rng):
    return {'tags': ['high_dpi', 'high_dpi_600', 'large_image'],
            'files': {'scan-mild': spec(dpi=400, glob=[['noise', {'sigma': 2}]], out=L(85)),
                      'scan': spec(dpi=600, glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': 0.3}],
                                                  ['noise', {'sigma': 3}]], out=L(85)),
                      'scan-severe': spec(dpi=600, content=base_content(paper={'color': 242, 'texture': 9,
                                                                                'fibers': 60}),
                                          glob=[['bed', {'margin_mm': 3}], ['rotate', {'deg': -0.8}],
                                                ['speckle', {'per_mpx': 25, 'max_r': 3}], ['noise', {'sigma': 8}]],
                                          out=L(80))},
            'notes': 'High resolution: mild 400 dpi, scan 600 dpi (~5000x7000 px per page), severe 600 dpi with '
                     'visible paper grain, fibres and dust. Tests memory/time limits and scale-dependent '
                     'thresholds.',
            'limits': ''}


def v_blur(pk, info, rng):
    return {'tags': ['blur_focus', 'blur_motion'],
            'files': {'scan-mild': spec(glob=[['blur', {'sigma': 1.3}], ['noise', {'sigma': 2}]], out=L(80)),
                      'scan': spec(glob=[['blur', {'sigma': 2.0}], ['motion', {'length': 6, 'angle': 0}],
                                         ['noise', {'sigma': 2}]], out=L(78)),
                      'scan-severe': spec(glob=[['blur', {'sigma': 2.8}], ['motion', {'length': 14, 'angle': 35}],
                                                ['noise', {'sigma': 4}]], out=L(70))},
            'notes': 'Out-of-focus and moving camera/scanner head: gaussian sigma 1.3 / 2.0 / 2.8 px (at 300 dpi) '
                     'plus horizontal motion blur 6 px (scan) and 14 px at 35 deg (severe). Staff lines blur into '
                     'grey bands; ledger lines and accidentals smear.',
            'limits': ''}


def v_noise(pk, info, rng):
    return {'tags': ['gaussian_noise', 'salt_pepper', 'speckles'],
            'files': {'scan-mild': spec(glob=[['noise', {'sigma': 10}], ['saltpepper', {'amount': 0.002}]], out=L(85)),
                      'scan': spec(glob=[['noise', {'sigma': 25}], ['saltpepper', {'amount': 0.01}]], out=L(80)),
                      'scan-severe': spec(glob=[['noise', {'sigma': 45}], ['saltpepper', {'amount': 0.03}],
                                                ['speckle', {'per_mpx': 300}]], out=L(75))},
            'notes': 'Sensor noise: gaussian sigma 10 / 25 / 45 grey levels plus salt-and-pepper 0.2% / 1% / 3% of '
                     'pixels; severe adds round dark specks (dust) that can mimic dots and noteheads.',
            'limits': 'Speck-like noise is not music; truth unaffected.'}


def v_spread(pk, info, rng):
    two = pk == 'piano2p'
    mild = spec(dpi=200, assembly='spread', spread={'gutter_width': 0.04, 'gutter_dark': 0.35},
                glob=[['bed', {'margin_mm': 4}], ['noise', {'sigma': 2}]], out=L(78))
    scan = spec(dpi=200, assembly='spread', spread={'gutter_width': 0.05, 'gutter_dark': 0.55},
                page_geom=[['curl', {'amp_mm': 5, 'width': 0.25, 'shade': 0.2}]], bg=dict(DARK),
                glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': 1.0}], ['gradient', {'strength': 0.1}],
                      ['noise', {'sigma': 3}]], out=L(72))
    sev = spec(dpi=200, assembly='spread', spread={'gutter_width': 0.07, 'gutter_dark': 0.75},
               content=base_content(paper={'color': [240, 232, 210], 'texture': 5, 'age_edges': 0.2},
                                    ink_color=[45, 40, 35]),
               page_geom=[['curl', {'amp_mm': 10, 'width': 0.35, 'shade': 0.35}]], bg=dict(DARK),
               glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': -3.5}],
                     ['perspective', {'jitter': 0.03, 'keystone': 0.03, 'margin': 0.03}],
                     ['vignette', {'strength': 0.2}], ['blur', {'sigma': 0.8}], ['noise', {'sigma': 4, 'chroma': 2}]],
               out=RGB(60))
    if two:
        note = ('2-up double-page spread: pages 1 and 2 side by side on ONE landscape image (scan.pdf has 1 page); '
                'the app must split the spread and read left page then right page. scan adds curl towards the '
                'gutter and 1 deg rotation; severe adds 3.5 deg rotation, perspective, aged paper (RGB).')
        lim = ''
    else:
        note = ('2-up double-page spread: a text-only facing page (verso, "Notes on the Music", no music) on the '
                'left and the music page (recto) on the right, as ONE landscape image. The app must find the music '
                'on the right half and ignore the prose page. scan adds curl towards the gutter and 1 deg '
                'rotation; severe adds 3.5 deg rotation, perspective, aged paper (RGB).')
        lim = 'The facing page is prose only; its text is not part of the truth (no lyrics, no title).'
    return {'tags': ['two_up_spread', 'double_page', 'book_gutter_shadow', 'landscape_image'] +
                    ([] if two else ['facing_text_page']),
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev}, 'notes': note, 'limits': lim}


def v_scale(pk, info, rng):
    assert pk == 'piano2p'
    bed = [['bed', {'margin_mm': 4}], ['noise', {'sigma': 2}]]
    mild = spec(glob=bed, page_overrides={'1': {'page_geom': [['scale', {'factor': 0.97}]]}}, out=L(80))
    scan = spec(glob=bed, page_overrides={'0': {'page_geom': [['rotate', {'deg': -0.5, 'expand': False}]]},
                                          '1': {'page_geom': [['scale', {'factor': 0.94, 'dx_mm': 4, 'dy_mm': -3}],
                                                              ['rotate', {'deg': 1.5, 'expand': False}]]}}, out=L(78))
    sev = spec(glob=bed, page_overrides={'0': {'page_geom': [['scale', {'factor': 1.04}]]},
                                         '1': {'page_geom': [['scale', {'factor': 0.88, 'dx_mm': -6, 'dy_mm': 5}],
                                                             ['rotate', {'deg': -3, 'expand': False}]]}}, out=L(72))
    return {'tags': ['page_scale_mismatch', 'multi_page', 'per_page_skew'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'The two pages were copied at different enlargements: page 2 content at 97% (mild), 94% + '
                     'offset + 1.5 deg (scan), 88% + offset + -3 deg while page 1 is at 104% (severe). Staff '
                     'size therefore differs between pages of the same piece.',
            'limits': 'Severe: page 1 at 104% loses ~4 mm of its outer margins (no music touched: margins are '
                      '>= 15 mm).'}


def v_combo(pk, info, rng):
    voc = VOCAB[pk]
    fing = 1 if pk.startswith('piano') else 0
    xa, ya = _stain_pos(info, rng, True)
    mild = spec(content=base_content(paper={'color': [242, 234, 212], 'texture': 4, 'age_edges': 0.2},
                                     ink_color=[45, 40, 35], bleed={'amount': 0.1, 'blur': 2.0},
                                     annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 2, 'texts': 1,
                                                   'fingerings': 2 * fing, 'alpha': 0.6}]),
                glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': 3.0}], ['noise', {'sigma': 3}]], out=RGB(60))
    scan = spec(dpi=250, content=base_content(
        paper={'color': [236, 224, 192], 'texture': 5, 'fibers': 20, 'age_edges': 0.35},
        ink_color=[55, 45, 36], ink_var=20,
        stains=[{'x_mm': xa, 'y_mm': ya, 'radius_mm': 32, 'strength': 1.0}],
        annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 4, 'texts': 3, 'breaths': 2,
                      'fingerings': 4 * fing, 'alpha': 0.7}]),
        bg=dict(TABLE),
        glob=[['perspective', {'jitter': 0.04, 'keystone': 0.05, 'margin': 0.06}],
              ['shadow', {'strength': 0.35, 'pos': 0.2, 'angle': 60}], ['vignette', {'strength': 0.25}],
              ['blur', {'sigma': 1.0}], ['noise', {'sigma': 5, 'chroma': 3}]], out=RGB(50))
    xb, yb = _stain_pos(info, rng, True)
    sev = spec(dpi=150, content=base_content(
        paper={'color': [228, 210, 165], 'texture': 7, 'fibers': 50, 'age_edges': 0.5},
        ink_color=[70, 55, 40], ink_var=35, fade=0.15, foxing={'n': 80, 'strength': 0.5},
        bleed={'amount': 0.25, 'blur': 1.8, 'color': [110, 85, 60]},
        stains=[{'x_mm': xb, 'y_mm': yb, 'radius_mm': 38, 'strength': 1.2}],
        annotations=[{'tool': 'pencil', 'vocab': voc, 'circles': 6, 'texts': 4, 'breaths': 3, 'arrows': 1,
                      'fingerings': 6 * fing, 'alpha': 0.8},
                     {'tool': 'pen', 'vocab': voc, 'circles': 2, 'texts': 1, 'color': [35, 55, 160], 'alpha': 0.85}],
        holes={'x_mm': 9, 'offsets_mm': [-40, 40], 'diam_mm': 6}),
        page_geom=[['curl', {'amp_mm': 8, 'width': 0.3, 'shade': 0.3}], ['gutter', {'width': 0.08, 'dark': 0.6}]],
        bg=dict(DARK),
        glob=[['bed', {'margin_mm': 5}], ['rotate', {'deg': -7.0}], ['vignette', {'strength': 0.2}],
              ['motion', {'length': 5, 'angle': 80}], ['blur', {'sigma': 0.9}], ['noise', {'sigma': 8, 'chroma': 3}],
              ['saltpepper', {'amount': 0.003}]], out=RGB(25))
    return {'tags': ['combined_damage', 'yellowed_paper', 'rgb_scan', 'bleed_through', 'pencil_annotations',
                     'circled_notes', 'coffee_stain', 'perspective_phone', 'page_curl', 'book_gutter_shadow',
                     'skew_large', 'punch_holes', 'foxing', 'blur_motion', 'jpeg_q25', 'low_dpi'],
            'files': {'scan-mild': mild, 'scan': scan, 'scan-severe': sev},
            'notes': 'Everything at once. mild: aged paper, bleed-through, a few pencil marks, 3 deg skew, JPEG 60. '
                     'scan: phone photo (250 dpi) of an aged, stained, pencil-marked page with hand shadow, JPEG 50. '
                     'severe: 150 dpi book scan with curl + gutter, -7 deg skew, foxing, 25% bleed-through, stain, '
                     'pencil + ballpoint marks, punch holes, motion blur, noise and JPEG 25 - a worst case.',
            'limits': 'Handwritten marks, stains, foxing and ghost notes are not music and are not in the truth. '
                      'Severe is intentionally at (or beyond) the limit of human legibility at 150 dpi.'}


VARIANTS = [
    ('clean', v_clean), ('skew', v_skew), ('rot90', v_rot90), ('rot180', v_rot180), ('phone', v_phone),
    ('book', v_book), ('yellowed', v_yellowed), ('bleed', v_bleed), ('stain-pencil', v_stain_pencil),
    ('holes-staple', v_holes), ('crop', v_crop), ('halftone', v_halftone), ('jpeg', v_jpeg),
    ('photocopy-thin', v_photocopy_thin), ('photocopy-thick', v_photocopy_thick), ('lowdpi', v_lowdpi),
    ('highdpi', v_highdpi), ('blur', v_blur), ('noise', v_noise), ('spread', v_spread), ('scale', v_scale),
    ('combo', v_combo),
]


def catalogue(infos):
    """infos: piece -> list of page analyses (mm).  Returns item list."""
    import zlib
    items = []
    for pk in ('hymn', 'melody', 'piano', 'piano2p'):
        for vname, fn in VARIANTS:
            if vname == 'scale' and pk != 'piano2p':
                continue
            iid = f'{PIECE_IDS[pk]}-{vname}'
            seed = zlib.crc32(iid.encode()) & 0x7FFFFFFF
            rng = np.random.default_rng(seed)
            v = fn(pk, infos[pk][0], rng)
            items.append({'id': iid, 'piece': pk, 'variant': vname, 'seed': seed, **copy.deepcopy(v)})
    return items
