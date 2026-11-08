"""Layout-challenge catalog: items + scan damage plans (scan.pdf, scan-mild.pdf, scan-severe.pdf).

Every plan is a parameter dict for lsynth/degrade2.py plus a seed; build.py records the
parameters and the per-page operations actually applied in meta.json."""
from .anthem import ITEM as ANTHEM
from .hymn import ITEM as HYMN
from .nocturne import ITEM as NOCTURNE
from .organ import ITEM as ORGAN
from .song import ITEM as SONG
from .trio import ITEM as TRIO
from .variations import ITEM as VARIATIONS

CREAM = (243, 236, 214)
YELLOWED = (236, 226, 198)
OLD_PAPER = (232, 219, 186)

VARIATIONS['scans'] = {
    'scan.pdf': {'seed': 11001, 'summary': 'ring-binder photocopies scanned at 200 dpi grey: punch holes, a '
                 'different skew on every page, page 8 fed upside down (180 deg), 3 pages at a different scale, '
                 'bleed-through of the reverse page, toner speckles, JPEG q50',
                 'params': dict(dpi=200, mode='gray', paper_rgb=(246, 246, 244), texture=4, ink_rgb=(25, 25, 25),
                                punch_holes={'n': 3, 'side': 'left', 'level': 28},
                                rotate_pages={0: 0.6, 1: -1.1, 2: 1.8, 3: -0.5, 4: 2.4, 5: -1.6, 6: 0.9, 7: 0.7,
                                              8: -2.9, 9: 1.3, 10: -0.8, 11: 3.4},
                                page_rotate={7: 180}, scale_pages={3: 0.97, 6: 1.025, 10: 0.985},
                                bleed=0.08, gradient=0.08, blur=0.6, noise=4, speckle=60, jpeg=50)},
    'scan-mild.pdf': {'seed': 11002, 'summary': 'clean flatbed scan, 300 dpi grey, 0.5 deg skew, JPEG q85',
                      'params': dict(dpi=300, mode='gray', texture=2, rotate=0.5, noise=2, jpeg=85)},
    'scan-severe.pdf': {'seed': 11003, 'summary': 'thin, faded binarised photocopy at 150 dpi (from 300): broken '
                        'staff lines, 2-6 deg skew per page, page 5 upside down, salt & pepper, speckles',
                        'params': dict(dpi=300, out_dpi=150, ink_dropout=0.15,
                                       rotate_pages={0: 2.1, 1: -3.3, 2: 4.6, 3: -2.2, 4: 3.0, 5: -5.8, 6: 2.7,
                                                     7: -4.1, 8: 6.0, 9: -2.5, 10: 3.8, 11: -3.0},
                                       page_rotate={4: 180}, blur=0.6, noise=8, binarize=118, binarize_noise=20,
                                       saltpepper=0.0015, speckle=150, format='png1')},
}
ANTHEM['scans'] = {
    'scan.pdf': {'seed': 12001, 'summary': 'bound octavo scanned as a book: pages 2-3 as ONE 2-up image '
                 '(double-page spread) with gutter shadow and page curl at the spine, yellowed paper (RGB), '
                 'slight skew, vignette, JPEG q40',
                 'params': dict(dpi=200, mode='rgb', paper_rgb=YELLOWED, texture=5, spread=[[1, 2]],
                                gutter={'side': 'inner', 'width': 0.07, 'dark': 0.6},
                                curl={'side': 'inner', 'amp': 30, 'width': 0.28}, rotate=1.2, vignette=0.15,
                                blur=0.7, noise=4, jpeg=40)},
    'scan-mild.pdf': {'seed': 12002, 'summary': 'flatbed 300 dpi RGB, cream paper, -0.6 deg skew, mild gutter',
                      'params': dict(dpi=300, mode='rgb', paper_rgb=CREAM, texture=3, rotate=-0.6,
                                     gutter={'side': 'inner', 'width': 0.04, 'dark': 0.3}, noise=2, jpeg=80)},
    'scan-severe.pdf': {'seed': 12003, 'summary': 'phone photos of two open double-page spreads (pages 1-2, 3-4): '
                        'perspective/keystone, uneven lamp light, vignette, motion blur, 120 dpi, JPEG q20',
                        'params': dict(dpi=200, out_dpi=120, mode='rgb', paper_rgb=YELLOWED, texture=6,
                                       spread=[[0, 1], [2, 3]], gutter={'side': 'inner', 'width': 0.08, 'dark': 0.7},
                                       curl={'side': 'inner', 'amp': 40, 'width': 0.3}, rotate=-2.0,
                                       phone={'margin': 0.05, 'bg': 60, 'jitter': 0.035, 'keystone': 0.05},
                                       blotch=0.25, vignette=0.35, motion_blur={'len': 6, 'angle': 15}, noise=7,
                                       jpeg=20)},
}
ORGAN['scans'] = {
    'scan.pdf': {'seed': 13001, 'summary': 'landscape pages scanned portrait (all pages rotated 90/270 deg), '
                 '150 dpi RGB on yellowed paper with foxing, pencil registration notes and circled notes, '
                 '1.5 deg skew, JPEG q45',
                 'params': dict(dpi=150, mode='rgb', paper_rgb=YELLOWED, texture=5, foxing={'n': 60},
                                pencil={'circles': 3, 'marks': 2, 'texts': ['Sw.', '+ Oboe', 'II', 'Gt.'],
                                        'lines': 1},
                                rotate=1.5, page_rotate={0: 90, 1: 90, 2: 270}, blur=0.5, noise=4, jpeg=45)},
    'scan-mild.pdf': {'seed': 13002, 'summary': '300 dpi grey, upright, 0.5 deg skew',
                      'params': dict(dpi=300, mode='gray', texture=2, rotate=0.5, noise=2, jpeg=85)},
    'scan-severe.pdf': {'seed': 13003, 'summary': 'thick dark binarised photocopy, 4 deg skew, page 2 rotated '
                        '90 deg, salt & pepper, staple and two punch holes',
                        'params': dict(dpi=200, ink_weight=1, rotate=4.0, page_rotate={1: 90},
                                       punch_holes={'n': 2, 'side': 'left', 'level': 10}, staple={'corner': 'tl'},
                                       blur=0.9, noise=12, binarize=200, binarize_noise=20, saltpepper=0.002,
                                       format='png1')},
}
NOCTURNE['scans'] = {
    'scan.pdf': {'seed': 14001, 'summary': 'phone photo: perspective + keystone, page curl, uneven lighting, '
                 'vignette, coffee ring stain, motion + focus blur, RGB, JPEG q35',
                 'params': dict(dpi=200, mode='rgb', paper_rgb=(246, 242, 232), texture=4,
                                coffee={'n': 1, 'r': 0.11, 'strength': 1.0},
                                curl={'side': 'right', 'amp': 35, 'width': 0.3},
                                phone={'margin': 0.06, 'bg': 50, 'jitter': 0.03, 'keystone': 0.06},
                                blotch=0.3, vignette=0.3, motion_blur={'len': 5, 'angle': 30}, blur=0.8, noise=5,
                                jpeg=35)},
    'scan-mild.pdf': {'seed': 14002, 'summary': 'high-resolution 400 dpi grey flatbed scan, 1 deg skew',
                      'params': dict(dpi=400, mode='gray', texture=2, rotate=1.0, noise=2, jpeg=80)},
    'scan-severe.pdf': {'seed': 14003, 'summary': '150 dpi grey, 10 deg / -8 deg skew, heavy blur, noise, JPEG q15',
                        'params': dict(dpi=150, mode='gray', texture=6, rotate_pages={0: 10.0, 1: -8.0}, blur=1.6,
                                       noise=12, jpeg=15)},
}
HYMN['scans'] = {
    'scan.pdf': {'seed': 15001, 'summary': 'printed hymnal page: halftone screen + resampling moire, strong '
                 'bleed-through, yellowed paper with foxing, gutter shadow and curl on the left, 200 dpi RGB, JPEG q55',
                 'params': dict(dpi=200, mode='rgb', paper_rgb=OLD_PAPER, texture=6, foxing={'n': 25},
                                bleed=0.15, gutter={'side': 'left', 'width': 0.06, 'dark': 0.5},
                                curl={'side': 'left', 'amp': 20, 'width': 0.25}, rotate=-0.8,
                                halftone={'period': 4.2, 'angle': 45, 'amp': 28, 'shrink': 0.83},
                                blur=0.5, noise=3, jpeg=55)},
    'scan-mild.pdf': {'seed': 15002, 'summary': '300 dpi grey, 0.3 deg skew, faint bleed-through',
                      'params': dict(dpi=300, mode='gray', texture=2, bleed=0.04, rotate=0.3, noise=2, jpeg=85)},
    'scan-severe.pdf': {'seed': 15003, 'summary': '100 dpi (from 300) thin binarised copy of the halftoned page, '
                        '2.5 deg skew',
                        'params': dict(dpi=300, out_dpi=100, rotate=2.5, bleed=0.12,
                                       halftone={'period': 4.0, 'angle': 30, 'amp': 30, 'shrink': 0.7},
                                       blur=0.7, noise=8, binarize=105, binarize_noise=15, format='png1')},
}
TRIO['scans'] = {
    'scan.pdf': {'seed': 16001, 'summary': 'dark (thick) binarised photocopy at 300 dpi, staple, two punch holes, '
                 'right edge cropped 2 mm into the staff ends',
                 'params': dict(dpi=300, ink_weight=1, rotate=0.4, punch_holes={'n': 2, 'side': 'left', 'level': 0},
                                staple={'corner': 'tl'}, crop_ink={'right': 2.0}, blur=0.8, noise=10, binarize=185,
                                binarize_noise=18, speckle=40, format='png1')},
    'scan-mild.pdf': {'seed': 16002, 'summary': '300 dpi grey, 0.4 deg skew',
                      'params': dict(dpi=300, mode='gray', texture=2, rotate=-0.4, noise=2, jpeg=85)},
    'scan-severe.pdf': {'seed': 16003, 'summary': 'page 1 skewed 6 deg, page 2 fed upside down (180 deg), 150 dpi '
                        'grey, left/right edges cropped into the staves, salt & pepper, JPEG q25',
                        'params': dict(dpi=150, mode='gray', texture=5, rotate_pages={0: 6.0, 1: -1.5},
                                       page_rotate={1: 180}, crop_ink={'right': 3.0, 'left': 1.5}, blur=0.9,
                                       noise=9, saltpepper=0.003, jpeg=25)},
}
SONG['scans'] = {
    'scan.pdf': {'seed': 17001, 'summary': 'high-resolution 600 dpi RGB scan of an old yellowed copy: pencil '
                 'annotations (circled notes, breath marks, words), foxing, a coffee ring, 0.8 deg skew, JPEG q60',
                 'params': dict(dpi=600, mode='rgb', paper_rgb=YELLOWED, texture=5,
                                pencil={'circles': 4, 'marks': 4, 'texts': ['breathe', 'rit.', 'p!'], 'lines': 2},
                                foxing={'n': 50}, coffee={'n': 1, 'r': 0.09, 'strength': 0.8}, rotate=0.8,
                                blur=0.4, noise=3, jpeg=60)},
    'scan-mild.pdf': {'seed': 17002, 'summary': '300 dpi grey, 0.3 deg skew',
                      'params': dict(dpi=300, mode='gray', texture=2, rotate=0.3, noise=2, jpeg=85)},
    'scan-severe.pdf': {'seed': 17003, 'summary': 'phone photo at an angle: 7 deg rotation, strong keystone, '
                        'vignette, motion blur, salt & pepper, 150 dpi, JPEG q18',
                        'params': dict(dpi=150, mode='rgb', paper_rgb=CREAM, texture=6, rotate=7.0,
                                       phone={'margin': 0.07, 'bg': 45, 'jitter': 0.04, 'keystone': 0.08},
                                       vignette=0.4, blotch=0.2, motion_blur={'len': 7, 'angle': 60}, noise=6,
                                       saltpepper=0.001, jpeg=18)},
}

ITEMS = [VARIATIONS, ANTHEM, ORGAN, NOCTURNE, HYMN, TRIO, SONG]
