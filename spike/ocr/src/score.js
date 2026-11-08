'use strict';
// Aggregate raw OCR jsonl results against GT. Usage: node src/score.js [prefix-filter] > results/summary_*.json
const fs = require('fs'), path = require('path');
const M = require('./metrics');
const { listJobs } = require('./jobs');
const RAW = path.join(__dirname, '..', 'results', 'raw');
const filt = process.argv[2] || '';
const jobs = new Map(listJobs().map(j => [j.key, j]));
const byCfg = {};
for (const f of fs.readdirSync(RAW).filter(f => f.endsWith('.jsonl') && f.startsWith(filt))) {
  const cfg = f.replace(/\.\d+\.jsonl$/, '');
  for (const ln of fs.readFileSync(path.join(RAW, f), 'utf8').split('\n')) {
    if (!ln) continue; const r = JSON.parse(ln); const j = jobs.get(r.key); if (!j) continue;
    const s = M.scoreLine(j.line, r.ocr); s.ms = r.ms;
    (byCfg[cfg] ||= []).push({ j, s, r });
  }
}
const out = {};
for (const [cfg, rows] of Object.entries(byCfg)) {
  const g = (fn) => { const m = {}; for (const x of rows) (m[fn(x)] ||= []).push(x.s); return Object.fromEntries(Object.entries(m).map(([k, v]) => [k, M.aggregate(v)])); };
  out[cfg] = { n: rows.length, all: M.aggregate(rows.map(x => x.s)), byVariant: g(x => x.j.variant), byLang: g(x => x.j.lang), byLayout: g(x => x.j.layout),
    byFont: g(x => x.j.line.font.replace(/-.*$/, '') + (/Italic/.test(x.j.line.font) ? '-It' : '')) };
}
process.stdout.write(JSON.stringify(out, null, 1));
