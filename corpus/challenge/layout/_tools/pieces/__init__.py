"""Layout-challenge catalog: items + scan damage plans."""
from .nocturne import ITEM as NOCTURNE
from .song import ITEM as SONG
from .variations import ITEM as VARIATIONS

T = {'scan.pdf': {'seed': 1, 'summary': 'test', 'params': dict(dpi=150, mode='gray', rotate=0.5, jpeg=60)}}
for it in (SONG, VARIATIONS, NOCTURNE):
    it['scans'] = T
ITEMS = [VARIATIONS, NOCTURNE, SONG]
