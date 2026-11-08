'use strict';
// Sequential single-process timing (node, 1 thread per engine). Usage: node src/bench.js [nPerVariant]
const os = require('os');
const IMG = require('./img'), S = require('./strips'), E = require('./engines');
const { listJobs, oracleCrop, loadPage, VARIANTS } = require('./jobs');
(async () => {
  const n = +(process.argv[2] || 8);
  const jobs = []; for (const v of VARIANTS) { const js = listJobs([v]); for (let i = 0; i < n; i++) jobs.push(js[Math.floor(i * js.length / n)]); }
  const res = { load: os.loadavg(), cpus: os.cpus().length, cpu: os.cpus()[0].model, node: process.version, strips: jobs.length };
  const cfgs = [
    ['tess fast eng (compress)', { model: 'fast' }, 'eng', 'compress'],
    ['tess best_int eng (compress)', { model: 'best_int' }, 'eng', 'compress'],
    ['tess best_int eng+deu+lat (compress)', { model: 'best_int' }, 'eng+deu+lat', 'compress'],
    ['tess fast eng+deu+lat (compress)', { model: 'fast' }, 'eng+deu+lat', 'compress'],
    ['paddle latin_v5 (norm, 1 thread)', { model: 'latin_v5' }, null, 'norm'],
    ['paddle latin_v5 (norm, 4 threads)', { model: 'latin_v5', threads: 4 }, null, 'norm'],
  ];
  for (const [label, cfg, langs, prep] of cfgs) {
    const t0 = Date.now();
    const eng = langs ? await E.tess({ ...cfg, psm: 7 }, langs) : await E.paddle(cfg);
    const init = Date.now() - t0;
    const crops = jobs.map(j => oracleCrop(loadPage(j.png), j.line, prep, 40));
    await eng.recognize(crops[0]);   // warm-up
    const t1 = process.hrtime.bigint();
    let px = 0; for (const c of crops) { await eng.recognize(c); px += c.width; }
    const ms = Number(process.hrtime.bigint() - t1) / 1e6;
    await eng.terminate();
    res[label] = { initMs: init, msPerStrip: Math.round(ms / crops.length), msPer1000px: +(1000 * ms / px).toFixed(1), rssMB: Math.round(process.memoryUsage().rss / 1e6) };
    console.error(label, res[label]);
  }
  // detection
  const pages = []; for (const v of VARIANTS) { const js = listJobs([v]); for (let i = 0; i < 4; i++) pages.push(js[Math.floor(i * js.length / 4)].png); }
  const det = {};
  for (const p of [...new Set(pages)]) { const img = IMG.readGray(p); const t0 = process.hrtime.bigint(); const r = S.detectLyricLines(img); const v = p.split('/').slice(-2)[0]; (det[v] ||= []).push(Number(process.hrtime.bigint() - t0) / 1e6); }
  res.detectMsPerPage = Object.fromEntries(Object.entries(det).map(([k, a]) => [k, Math.round(a.reduce((x, y) => x + y, 0) / a.length)]));
  res.loadAfter = os.loadavg();
  console.log(JSON.stringify(res, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
