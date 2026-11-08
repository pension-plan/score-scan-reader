#!/usr/bin/env bash
# Build degraded test set: data/set/<piece>_<dpi>_<cond>.png + .json (truth).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/data/set"; mkdir -p "$OUT"
PIECES="${PIECES:-satb20 satb16 melody piano}"
DPIS="${DPIS:-150 200 300}"
CONDS="${CONDS:-$(python3 "$HERE/tools/degrade.py" --list)}"
jobs=()
seed=1
for p in $PIECES; do for r in $DPIS; do for c in $CONDS; do
  seed=$((seed+1))
  echo "$HERE/data/raster/${p}_${r}-1.pgm $HERE/data/truth/${p}_${r}.json $r $c $OUT/${p}_${r}_${c}.png $OUT/${p}_${r}_${c}.json $seed"
done; done; done | xargs -P 96 -L 1 python3 "$HERE/tools/degrade.py"
ls "$OUT"/*.png | wc -l
