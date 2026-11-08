#!/usr/bin/env bash
# Engrave a truth MusicXML with musicxml2ly + LilyPond and build a side-by-side image
# (scan | engraving) for visual comparison.  usage: render_check.sh <item-dir> [musicxml-name]
set -euo pipefail
d="$1"; x="${2:-truth-printed.musicxml}"
out="$d/verify"; mkdir -p "$out"
base="$(basename "$x" .musicxml)"
musicxml2ly --no-beaming -o "$out/$base.ly" "$d/$x" >/dev/null 2>&1 || musicxml2ly -o "$out/$base.ly" "$d/$x"
( cd "$out" && lilypond -dno-point-and-click -dresolution=110 --png -o "$base" "$base.ly" >/dev/null 2>"$base.lilypond.log" ) || { tail -20 "$out/$base.lilypond.log"; exit 1; }
pngs=$(ls "$out"/"$base"*.png | grep -v compare | sort)
convert $pngs -append -trim -bordercolor white -border 20 "$out/$base-engraved.png"
convert "$d/source-page.jpg" -resize x1600 "$out/_scan.png"
convert "$out/$base-engraved.png" -resize x1600\> "$out/_eng.png"
convert "$out/_scan.png" "$out/_eng.png" +append "$out/$base-compare.png"
rm -f "$out/_scan.png" "$out/_eng.png" $pngs
echo "$out/$base-compare.png"
