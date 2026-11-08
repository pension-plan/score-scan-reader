#!/usr/bin/env bash
# Render every score in scores/ twice (clean + colour-coded truth) and rasterize
# both at 150/200/300 dpi.  Clean = anti-aliased grey (realistic "perfect scan"),
# truth = colour PPM without anti-aliasing (exact grob colours).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PDF="$HERE/data/pdf"; RAS="$HERE/data/raster"
mkdir -p "$PDF" "$RAS"
PIECES="${PIECES:-satb20 satb16 melody piano}"
DPIS="${DPIS:-150 200 300}"
cd "$HERE/scores"
for f in $PIECES; do
  (
    lilypond -dno-point-and-click -o "$PDF/$f" "$f.ly" > "$PDF/$f.clean.log" 2>&1
    rm -f "$PDF/$f.truth.txt"
    OMR_TRUTH=1 OMR_TRUTH_LOG="$PDF/$f.truth.txt" lilypond -dno-point-and-click -o "$PDF/$f.truth" "$f.ly" > "$PDF/$f.truth.log" 2>&1
    for r in $DPIS; do
      pdftoppm -gray -r "$r" "$PDF/$f.pdf" "$RAS/${f}_${r}"
      pdftoppm -r "$r" -aa no -aaVector no "$PDF/$f.truth.pdf" "$RAS/${f}_${r}.truth"
    done
    echo "rendered $f"
  ) &
done
wait
