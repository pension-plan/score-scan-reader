"""Layouts-family items: every module pNN_*.py in this folder defines ITEM (sorted by file name)."""
import importlib
import os
import pkgutil

ITEMS = []
for _m in sorted(m.name for m in pkgutil.iter_modules([os.path.dirname(__file__)]) if m.name.startswith('p')):
    ITEMS.append(importlib.import_module(f'{__name__}.{_m}').ITEM)
