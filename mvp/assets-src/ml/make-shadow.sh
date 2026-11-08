#!/bin/bash
# Builds a shadow copy of mvp/src whose omr.convert() runs the ML detector (src/ml.js),
# for A/B evaluation until the harness has its own switch:
#   bash assets-src/ml/make-shadow.sh <dir>
#   node tools/eval.mjs --src <dir> --out <file> [--set challenge] [--no-ocr]
# Options for the refinement can be passed as JSON in ML_OPTS (e.g. '{"add":false}').
set -e
D=${1:?usage: make-shadow.sh <dir>}
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$(cd "$HERE/../../src" && pwd)
# onnxruntime-node: ORT_NODE if set, else the spike's install (see docs/spike-ml.md)
ORT=${ORT_NODE:-$(cd "$HERE/../../.." && pwd)/spike/ml/node_modules/onnxruntime-node}
rm -rf "$D" && mkdir -p "$D"
cp "$SRC"/*.js "$D"/
mv "$D/omr.js" "$D/omr_base.js"
cat > "$D/omr.js" <<JS
'use strict';
// shadow: omr.convert() with the copista-2m detector wrapped around createConverter()
const base = require('./omr_base');
const ml = require('./ml');
let detP = null;
async function convert(pages, opts = {}) {
  detP = detP || ml.createNodeDetector({ assets: '$HERE', ortPath: '$ORT' });
  const det = await detP;
  const c = ml.wrapConverter(base.createConverter(opts), det.detect, process.env.ML_OPTS ? JSON.parse(process.env.ML_OPTS) : {});
  for (let i = 0; i < pages.length; i++) await c.addPage(pages[i], i, pages.length);
  return c.finish();
}
module.exports = Object.assign({}, base, { convert });
JS
echo "shadow src with ML in $D"
