'use strict';
// Run many OCR configs x shards in parallel. Usage: node src/grid.js GRIDNAME [concurrency]
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'results', 'raw');
fs.mkdirSync(RAW, { recursive: true });
const GRIDS = {
  tess1: () => {
    const c = [];
    for (const model of ['fast', 'best_int', 'best']) for (const lang of ['matched', 'combined']) c.push({ model, lang, psm: 7, prep: 'norm', target: 40 });
    const b = { model: 'best_int', lang: 'matched', psm: 7, prep: 'norm', target: 40 };
    c.push({ ...b, psm: 6 }, { ...b, psm: 13 }, { ...b, prep: 'raw' }, { ...b, prep: 'clean' }, { ...b, target: 30 }, { ...b, target: 56 },
      { ...b, dict: 'off' }, { ...b, lang: 'eng' }, { ...b, lang: 'lat' }, { model: 'fast', lang: 'matched', psm: 7, prep: 'norm', target: 40, dict: 'off' },
      { model: 'best', lang: 'matched', psm: 7, prep: 'clean', target: 40 }, { model: 'fast', lang: 'matched', psm: 7, prep: 'clean', target: 40 });
    return c.map(x => ({ engine: 'tess', ...x }));
  },
};
function name(c) { return [c.e2e ? 'e2e' : '', c.engine, c.model, c.engine === 'tess' ? c.lang : '', c.engine === 'tess' ? 'psm' + (c.psm || 7) : '', c.e2e ? (c.compress ? 'compress' : 'plain') : (c.prep || 'norm'), 't' + (c.target || 40), c.dict === 'off' ? 'nodict' : ''].filter(Boolean).join('_'); }
const grid = process.argv[2], conc = +(process.argv[3] || 170), NSH = +(process.argv[4] || 16);
const cfgs = (GRIDS[grid] || (() => JSON.parse(fs.readFileSync(grid, 'utf8'))))().map(c => grid.includes('e2e') ? { ...c, e2e: true } : c);
const tasks = [];
for (const c of cfgs) for (let s = 0; s < NSH; s++) tasks.push({ c, s, out: path.join(RAW, `${name(c)}.${s}.jsonl`) });
let running = 0, done = 0, fail = 0; const t0 = Date.now();
function next() {
  while (running < conc && tasks.length) {
    const t = tasks.shift(); running++;
    const script = t.c.e2e ? 'e2e_eval.js' : (t.c.engine === 'tess' ? 'tess_eval.js' : 'paddle_eval.js');
    const p = spawn(process.execPath, [path.join(__dirname, script), JSON.stringify(t.c), String(t.s), String(NSH), t.out], { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = ''; p.stderr.on('data', d => err += d);
    p.on('exit', code => { running--; done++; if (code) { fail++; console.error('FAIL', t.out, err.slice(0, 500)); } if (done % 32 === 0) console.log(`${done} done, ${((Date.now() - t0) / 1000).toFixed(0)}s`); next(); if (!running && !tasks.length) console.log(`all done ${done} fail ${fail} in ${((Date.now() - t0) / 1000).toFixed(0)}s`); });
  }
}
fs.writeFileSync(path.join(RAW, `${path.basename(grid)}.configs.json`), JSON.stringify(cfgs.map(c => ({ name: name(c), ...c })), null, 1));
next();
