#!/usr/bin/env node
'use strict';
// Print notehead features around given truth heads (debug helper).
// usage: node tools/probe.js <image> <truth.json> <x,y> [<x,y> ...]
const fs = require('fs');
const { readGray } = require('../src/image');
const { runOMR } = require('../src/pipeline');
const { classify, DEFAULTS } = require('../src/noteheads');
const { integral } = require('../src/cc');
const [img, tr, ...pts] = process.argv.slice(2);
const det = runOMR(readGray(img), { debug: true });
const { B, R, staves } = det._debug;
const { labelComponents } = require('../src/cc');
const cc = labelComponents(R);
const IB = integral(B), IR = integral(R);
const truth = JSON.parse(fs.readFileSync(tr, 'utf8'));
for (const s of pts) {
  const [tx, ty] = s.split(',').map(Number);
  const t = truth.heads.find(h => Math.hypot(h.c[0] - tx, h.c[1] - ty) < 6) || {};
  let st = staves[0], bd = 1e9;
  for (const S of staves) { const d = Math.abs(S.yAt(2, tx) - ty); if (d < bd) { bd = d; st = S; } }
  const sp = st.spaceAt(tx);
  const p = Math.round((st.yAt(2, tx) - ty) / (sp / 2));
  const res = [];
  const dbg = { ...DEFAULTS, explain: true };
  for (let x = Math.round(tx - 0.4 * sp); x <= Math.round(tx + 0.4 * sp); x++) {
    const yc = st.yAt(2, x) - p * sp / 2;
    const real = classify(IB, IR, R, cc.labels, B.width, x, yc, sp, p, DEFAULTS);
    const f = classify(IB, IR, R, cc.labels, B.width, x, yc, sp, p, dbg);
    res.push({ dx: x - Math.round(tx), kind: real ? real.kind : '-' + (f && f.why ? f.why : ''), f: f && f.f });
  }
  console.log(`truth ${t.kind} pos=${t.staffPos} p=${p} sp=${sp.toFixed(1)} at ${tx},${ty}`);
  for (const r of res.filter((r, i) => i % 2 === 0)) console.log(' dx', r.dx, r.kind, r.f ? Object.entries(r.f).map(([k, v]) => k + '=' + (typeof v === 'number' ? v.toFixed(2) : v)).join(' ') : '');
}
