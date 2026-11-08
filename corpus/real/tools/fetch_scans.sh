#!/usr/bin/env bash
# Re-fetch the real-scan corpus pages from the Internet Archive and wrap each
# page image (unmodified JPEG bytes, no re-encode) into a one-page image-only PDF.
# Usage: corpus/real/tools/fetch_scans.sh   (requires curl, img2pdf)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# id | archive.org identifier | BookReader leaf index (page/nN) | ppi used for PDF page size
ITEMS="
golden1923-america|goldenbookoffavo00beat_0|2|500
methodist1905-st-anselm|methodisthymnalo00meth|63|400
klauser1867-schumann-melodie|b26976821|2|300
haupt1867-aus-meines-herzens-grunde|bub_gb_T75IAAAAcAAJ|22|300
efss1906-cold-blows-the-wind|englishfolksongs00goul|23|300
methodist1905-tappan-dennis|methodisthymnalo00meth|82|400
golden1923-auld-lang-syne|goldenbookoffavo00beat_0|36|500
sharp1911-rambling-sailor|folksongsfromsom00shar|17|350
"
echo "$ITEMS" | while IFS='|' read -r id ia leaf ppi; do
  [ -z "$id" ] && continue
  d="$ROOT/$id"; mkdir -p "$d"
  url="https://archive.org/download/$ia/page/n$leaf.jpg"
  curl -sfL -o "$d/source-page.jpg" "$url"
  img2pdf -s "${ppi}dpix${ppi}dpi" --producer "img2pdf (corpus/real/tools/fetch_scans.sh)" \
          --title "$id" -o "$d/scan.pdf" "$d/source-page.jpg"
  echo "$id <- $url ($(stat -c %s "$d/scan.pdf") bytes)"
done
