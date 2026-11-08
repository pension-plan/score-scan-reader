#!/usr/bin/env node
'use strict';
// Sequential timing benchmark: min over N repetitions per stage.
// usage: node tools/bench.js N img1 [img2 ...]
const { readGray } = require('../src/image');
const { runOMR } = require('../src/pipeline');
const [N, ...imgs] = process.argv.slice(2);
for (const f of imgs) {
  const g = readGray(f);
  let best = null, bestTot = 1e9;
  const stageMin = {};
  for (let i = 0; i < +N; i++) {
    const t0 = performance.now();
    const r = runOMR(g);
    const tot = performance.now() - t0;
    if (tot < bestTot) { bestTot = tot; best = r.timings; }
    for (const [k, v] of Object.entries(r.timings)) stageMin[k] = Math.min(stageMin[k] ?? 1e9, v);
  }
  console.log(JSON.stringify({ img: f.split('/').pop(), px: `${g.width}x${g.height}`, totalMinMs: Math.round(bestTot), stageMinMs: stageMin }));
}
