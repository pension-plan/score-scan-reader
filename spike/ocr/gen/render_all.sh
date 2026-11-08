#!/bin/bash
# Render all LilyPond docs and extract GT at 300 dpi, in parallel.
set -e
cd "$(dirname "$0")/.."
ls data/ly/*.ly | xargs -P 64 -n 1 sh -c 'cd data/ly && lilypond -s "$(basename "$0")"' 
mkdir -p data/clean300
ls data/ly/*.pdf | sed 's/\.pdf$//' | xargs -P 64 -I{} .venv/bin/python gen/gt.py {}.pdf {}.meta.json data/clean300 300
ls data/clean300/*.png | xargs -P 64 -n 1 -I{} .venv/bin/python gen/degrade.py {} data
