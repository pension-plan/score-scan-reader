#!/bin/bash
# A/B of the OpenCV fallback: the same src snapshot (spike/opencv/src-ab), fallback off vs on.
# One eval at a time, 16 jobs, no OCR (the fallback does not touch lyrics); waits while load1 > 170.
H=/Users/d.sloane/music/spike/opencv
export OPENCV_JS=$H/vendor/opencv-4.10.0-noeval.js
tag=${TAG:-ab}
for set in ${SETS:-bench challenge coverage}; do
  for arm in 0 1; do
    while [ "$(cut -d' ' -f1 /proc/loadavg | cut -d. -f1)" -gt 170 ]; do sleep 20; done
    out=$H/data/eval/$tag-$set-rests$arm.json
    sa=""; [ "$set" != bench ] && sa="--set $set"
    echo "$(date -u +%T) $set cv=$arm"
    OMR_CV_FALLBACK=1 OMR_CV_RESTS=$arm timeout 5400 node /Users/d.sloane/music/mvp/tools/eval.mjs $sa --no-ocr --jobs 16 --quiet --src $H/src-ab2 --out $out > $out.log 2>&1 || echo "eval failed: $set $arm"
  done
done
echo done
