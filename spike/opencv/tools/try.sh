#!/bin/bash
# try.sh <tag> <class[,class]> <ops|auto|off>: eval the degradation items of the classes on src-pc2
H=/Users/d.sloane/music/spike/opencv
tag=$1; classes=$2; ops=$3
only=$(for c in ${classes//,/ }; do for p in agrace-satb andantino-piano twinkle-piano2p wind-melody; do printf "degradation/%s-%s," $p $c; done; done)
while [ "$(cut -d' ' -f1 /proc/loadavg | cut -d. -f1)" -gt 170 ]; do sleep 20; done
envs="OPENCV_JS=$H/vendor/opencv-4.10.0-noeval.js"
[ "$ops" = off ] && envs="$envs OMR_PRECLEAN=off"
[ "$ops" != off ] && [ "$ops" != auto ] && envs="$envs OMR_PRECLEAN_OPS=$ops"
env $envs timeout 3000 node /Users/d.sloane/music/mvp/tools/eval.mjs --set challenge --only ${only%,} --no-ocr --jobs 8 --quiet --src $H/src-pc2 --out $H/data/eval/try-$tag.json > $H/data/eval/try-$tag.log 2>&1
node -e '
const R=require(process.argv[1]); const t={};
for (const i of R.items){const m=/-([a-z0-9-]+)\/(scan[^/]*)$/.exec(i.id.replace(/^degradation\/[a-z0-9]+-[a-z0-9]+/,""));(t[i.variant||i.id.split("/").pop()] ||= []).push(i.aggregate||0);}
console.log(process.argv[2].padEnd(30), Object.entries(t).sort().map(([k,a])=>k+" "+(a.reduce((x,y)=>x+y,0)/a.length).toFixed(3)).join("  "), "all", R.summary.all.aggregate);' $H/data/eval/try-$tag.json "$tag"
