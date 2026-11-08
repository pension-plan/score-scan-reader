"""Layout-challenge catalog: items + scan damage plans."""
from .song import ITEM as SONG

SONG['scans'] = {
    'scan.pdf': {'seed': 7001, 'summary': 'test', 'params': dict(dpi=300, mode='rgb', paper_rgb=(238, 228, 204), texture=5, rotate=0.8, pencil={'circles': 3, 'marks': 3, 'texts': ['breathe', '2'], 'lines': 1}, foxing={'n': 40}, noise=3, blur=0.5, jpeg=60)},
}
ITEMS = [SONG]
