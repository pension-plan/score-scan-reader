#!/usr/bin/env node
// Regression check: score the current pipeline and a released version on the same
// corpus with the same options, and report what got worse.
//
//   node tools/regress.mjs [--base <tag>] [--set default|challenge] [--ocr] [--jobs N] [--out file.md]
//
// --base defaults to the latest score-scan-reader-v* tag. The base's mvp/src is
// extracted with `git archive` into mvp/work/regress/<tag>/src and scored with
// eval.mjs --src. Exit status 1 when the overall aggregate drops by more than
// 0.005, the real-scan aggregate by more than 0.01, the crash count rises, or
// any single item drops by more than 0.05. Policy: ship first, then run this
// after every push (CI does it too) and fix forward.
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const git = (...a) => execFileSync('git', a, { cwd: ROOT, encoding: 'utf8' }).trim();

const base = opt('--base', git('tag', '--list', 'score-scan-reader-v*', '--sort=-v:refname').split('\n')[0]);
if (!base) { console.error('no release tag found'); process.exit(2); }
const set = opt('--set', 'default');
const ocr = argv.includes('--ocr');
const jobs = opt('--jobs', '8');
const work = path.join(ROOT, 'mvp/work/regress', base);
const baseSrc = path.join(work, 'src');

if (!fs.existsSync(path.join(baseSrc, 'omr.js'))) {
  fs.mkdirSync(work, { recursive: true });
  const tar = execFileSync('git', ['archive', base, 'mvp/src'], { cwd: ROOT, maxBuffer: 1 << 28 });
  spawnSync('tar', ['-x', '-C', work, '--strip-components=1'], { input: tar });
}

const run = (label, src) => {
  const out = path.join(ROOT, `mvp/work/regress-${label}-${set}${ocr ? '-ocr' : ''}.json`);
  const a = ['mvp/tools/eval.mjs', '--out', out, '--jobs', jobs, '--quiet'];
  if (src) a.push('--src', src);
  if (set !== 'default') a.push('--set', set);
  if (!ocr) a.push('--no-ocr');
  const r = spawnSync(process.execPath, a, { cwd: ROOT, stdio: ['ignore', 'ignore', 'inherit'] });
  if (r.status !== 0 && !fs.existsSync(out)) { console.error(`eval failed for ${label}`); process.exit(2); }
  return JSON.parse(fs.readFileSync(out, 'utf8'));
};

const A = run(base, baseSrc), B = run('head', null);
const head = git('rev-parse', '--short', 'HEAD');
const sA = A.summary, sB = B.summary;
const f = (v) => (typeof v === 'number' ? v.toFixed(3) : '–');
const d = (a, b) => (typeof a === 'number' && typeof b === 'number' ? (b - a >= 0 ? '+' : '') + (b - a).toFixed(3) : '');
const L = [];
L.push(`## Regression check: ${head} vs ${base} (${set === 'default' ? 'benchmark' : set}, ${ocr ? 'with' : 'without'} OCR)`);
L.push('');
L.push(`| Metric | ${base} | ${head} | Change |`);
L.push('|---|---|---|---|');
for (const k of ['aggregate', 'pitch', 'duration', 'rests', 'lyrics', 'parts', 'xml_valid', 'crashes']) L.push(`| ${k} | ${f(sA.all[k])} | ${f(sB.all[k])} | ${d(sA.all[k], sB.all[k])} |`);
if (sA.real && sB.real) L.push(`| real-scan aggregate | ${f(sA.real.aggregate)} | ${f(sB.real.aggregate)} | ${d(sA.real.aggregate, sB.real.aggregate)} |`);
const byId = new Map(A.items.map((it) => [it.id, it]));
const rows = B.items.map((it) => ({ id: it.id, a: byId.get(it.id)?.aggregate, b: it.aggregate })).filter((r) => typeof r.a === 'number' && typeof r.b === 'number');
const worse = rows.filter((r) => r.b < r.a - 0.05).sort((x, y) => (x.b - x.a) - (y.b - y.a));
const better = rows.filter((r) => r.b > r.a + 0.05).length;
L.push('');
L.push(`${rows.length} items compared: ${better} improved by more than 0.05, ${worse.length} dropped by more than 0.05.`);
if (worse.length) {
  L.push('');
  L.push('| Item that got worse | Before | After | Change |');
  L.push('|---|---|---|---|');
  for (const r of worse.slice(0, 25)) L.push(`| ${r.id} | ${f(r.a)} | ${f(r.b)} | ${d(r.a, r.b)} |`);
}
const fails = [];
if (sB.all.aggregate < sA.all.aggregate - 0.005) fails.push(`aggregate dropped ${d(sA.all.aggregate, sB.all.aggregate)}`);
if (sA.real && sB.real && sB.real.aggregate < sA.real.aggregate - 0.01) fails.push(`real-scan aggregate dropped ${d(sA.real.aggregate, sB.real.aggregate)}`);
if ((sB.all.crashes || 0) > (sA.all.crashes || 0)) fails.push(`crashes rose ${sA.all.crashes} → ${sB.all.crashes}`);
if (worse.length) fails.push(`${worse.length} item(s) dropped by more than 0.05`);
L.push('');
L.push(fails.length ? `**REGRESSION:** ${fails.join('; ')}.` : '**No regression.**');
const md = L.join('\n') + '\n';
process.stdout.write(md);
const outMd = opt('--out', null);
if (outMd) fs.writeFileSync(outMd, md);
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, md);
process.exit(fails.length ? 1 : 0);
