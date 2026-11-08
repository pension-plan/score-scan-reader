#!/bin/bash
# Symbol boxes for every coverage item: LilyPond SVG (tagged) -> data/boxes/<family>__<id>.json
# usage: mkboxes.sh [families...]   (runs <= 6 lilypond jobs at once)
set -u
H=/Users/d.sloane/music/spike/opencv
COV=/Users/d.sloane/music/corpus/coverage
mkdir -p $H/data/svg $H/data/boxes
one() {
  d=$1; fam=$(basename $(dirname $d)); id=$(basename $d); key=${fam}__${id}
  [ -s $H/data/boxes/$key.json ] && return
  out=$H/data/svg/$key
  timeout 300 lilypond -dbackend=svg -dno-point-and-click -dinclude-settings=$H/tools/svgtag.ly -o $out $d/engraving.ly >/dev/null 2>$out.log || { echo "FAIL $key"; return; }
  python3 -I - "$out" "$H/data/boxes/$key.json" <<'PY'
import sys, glob, json, re, subprocess
out, dst = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(out + '.svg') + glob.glob(out + '-*.svg'), key=lambda f: int(re.search(r'-(\d+)\.svg$', f).group(1)) if re.search(r'-(\d+)\.svg$', f) else 0)
sys.path.insert(0, '/Users/d.sloane/music/spike/opencv/tools')
import svgboxes
pages = [svgboxes.main(f, 300) for f in files]
json.dump({'pages': pages}, open(dst, 'w'))
PY
  echo "ok $key"
}
export -f one; export H
fams=${@:-rests pitch time marks notes layouts}
for f in $fams; do for d in $COV/$f/*/; do [ -f $d/engraving.ly ] && [ -f $d/meta.json ] && echo ${d%/}; done; done | xargs -P 6 -I{} bash -c 'one {}'
