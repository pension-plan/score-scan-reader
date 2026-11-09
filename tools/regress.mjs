#!/usr/bin/env node
// Regression check: score the current pipeline and a released version on the same
// corpus with the same options, and report what got worse.
//
//   node tools/regress.mjs [--base <tag>] [--head <ref>] [--set default|challenge] [--ocr] [--jobs N] [--out file.md]
//
// --head scores a committed ref (git archive, like the base) instead of the working tree's
// mvp/src. Several agents share this working tree, so without --head the head side also
// includes everyone's uncommitted changes; a warning is printed when mvp/src is dirty.
//
// --base defaults to the latest score-scan-reader-v* tag. The base's mvp/src is
// extracted with `git archive` into mvp/work/regress/<tag>/src and scored with
// eval.mjs --src. Exit status 1 when the overall aggregate drops by more than
// 0.005, the real-scan aggregate by more than 0.01, the crash count rises, or
// any single item drops by more than 0.05. Policy: ship first, then run this
// after every push (CI does it too) and fix forward.
//
// With --ocr each side also reads with its own OCR models: mvp/dist/assets/*.traineddata.gz of
// that ref (git archive, next to its src; eval.mjs --lang-path), so a model change is gated like a
// code change. Without --head the head side reads the working tree's models.
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

// Runs are concurrent (several agents share this tree): every run writes to its own paths,
// tagged with the process id, and the shared base checkout is extracted atomically.
const RUN = String(process.pid);
if (!fs.existsSync(path.join(baseSrc, 'omr.js'))) {
  const tmp = path.join(ROOT, 'mvp/work/regress', `.${path.basename(work)}.${RUN}`);
  fs.mkdirSync(tmp, { recursive: true });
  const tar = execFileSync('git', ['archive', base, 'mvp/src'], { cwd: ROOT, maxBuffer: 1 << 28 });
  spawnSync('tar', ['-x', '-C', tmp, '--strip-components=1'], { input: tar });
  fs.mkdirSync(work, { recursive: true });
  try { fs.renameSync(path.join(tmp, 'src'), baseSrc); } catch (e) { /* another run got there first */ }
  fs.rmSync(tmp, { recursive: true, force: true });
}

// the OCR models of a ref (mvp/dist/assets/*.traineddata.gz) next to its src, so a model change is
// scored like a code change; a ref without them reads with the working tree's
function extractModels(ref, dir) {
  if (fs.existsSync(path.join(dir, 'eng.traineddata.gz'))) return dir;
  const tmp = `${dir}.${RUN}`;
  fs.mkdirSync(tmp, { recursive: true });
  const r = spawnSync('git', ['archive', ref, '--', ':(glob)mvp/dist/assets/*.traineddata.gz'], { cwd: ROOT, maxBuffer: 1 << 28 });
  if (r.status === 0 && r.stdout.length) spawnSync('tar', ['-x', '-C', tmp, '--strip-components=3'], { input: r.stdout });
  if (!fs.existsSync(path.join(tmp, 'eng.traineddata.gz'))) { fs.rmSync(tmp, { recursive: true, force: true }); return null; }
  try { fs.renameSync(tmp, dir); } catch (e) { fs.rmSync(tmp, { recursive: true, force: true }); /* another run got there first */ }
  return dir;
}
const baseModels = ocr ? extractModels(base, path.join(work, 'tessdata')) : null;

const run = (label, src, models) => {
  const out = path.join(ROOT, `mvp/work/regress-${label}-${set}${ocr ? '-ocr' : ''}-${RUN}.json`);
  const a = ['mvp/tools/eval.mjs', '--out', out, '--jobs', jobs, '--quiet'];
  if (src) a.push('--src', src);
  if (set !== 'default') a.push('--set', set);
  // with OCR, read text as the page does (eng+deu plus the lazy second pass), not eval's eng-only default
  if (!ocr) a.push('--no-ocr'); else a.push('--ocr-lang', opt('--ocr-lang', 'app'));
  if (ocr && models) a.push('--lang-path', models);
  const r = spawnSync(process.execPath, a, { cwd: ROOT, stdio: ['ignore', 'ignore', 'inherit'] });
  if (r.status !== 0 && !fs.existsSync(out)) { console.error(`eval failed for ${label}`); process.exit(2); }
  return JSON.parse(fs.readFileSync(out, 'utf8'));
};

const headRef = opt('--head', null);
let headSrc = null, headModels = null;
if (headRef) {
  const hw = path.join(ROOT, 'mvp/work/regress', 'head-' + headRef.replace(/[^\w.-]/g, '_') + '-' + RUN);
  headSrc = path.join(hw, 'src');
  fs.rmSync(hw, { recursive: true, force: true });
  fs.mkdirSync(hw, { recursive: true });
  const tar = execFileSync('git', ['archive', headRef, 'mvp/src'], { cwd: ROOT, maxBuffer: 1 << 28 });
  spawnSync('tar', ['-x', '-C', hw, '--strip-components=1'], { input: tar });
  if (ocr) headModels = extractModels(headRef, path.join(hw, 'tessdata'));
} else if (git('status', '--porcelain', '--', 'mvp/src')) {
  console.error('warning: mvp/src has uncommitted changes (possibly other agents\' work); they are scored as head. Use --head <ref> to score a commit.');
}
const A = run(base, baseSrc, baseModels), B = run('head', headSrc, headModels);
if (headSrc) fs.rmSync(path.dirname(headSrc), { recursive: true, force: true });
console.error(`outputs: mvp/work/regress-{${base},head}-${set}${ocr ? '-ocr' : ''}-${RUN}.{json,out}`);
const head = headRef ? git('rev-parse', '--short', headRef) : git('rev-parse', '--short', 'HEAD') + (git('status', '--porcelain', '--', 'mvp/src') ? '+wip' : '');
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
// Notation the scorer does not grade (dynamics, words, ties...) can vanish without moving any
// metric, as when a broken import dropped every dynamic in 0.21.0. Count each element across
// all produced MusicXML files and treat a drop of more than 10% (from at least 10) as a regression.
const MARKS = ['dynamics', 'wedge', 'words', 'metronome', 'credit', 'tie', 'slur', 'fermata', 'grace', 'time', 'key', 'lyric'];
const outDir = (label) => path.join(ROOT, `mvp/work/regress-${label}-${set}${ocr ? '-ocr' : ''}-${RUN}.out`);
const countMarks = (dir) => {
  const n = Object.fromEntries(MARKS.map((m) => [m, 0]));
  if (!fs.existsSync(dir)) return null;
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.musicxml')) continue;
    const x = fs.readFileSync(path.join(dir, f), 'utf8');
    for (const m of MARKS) n[m] += (x.match(new RegExp(`<${m}[\\s/>]`, 'g')) || []).length;
  }
  return n;
};
const mA = countMarks(outDir(base)), mB = countMarks(outDir('head'));
const markDrops = [];
if (mA && mB) {
  L.push('');
  L.push('| Elements written | ' + base + ' | ' + head + ' |');
  L.push('|---|---|---|');
  for (const m of MARKS) {
    L.push(`| ${m} | ${mA[m]} | ${mB[m]} |`);
    if (mA[m] >= 10 && mB[m] < mA[m] * 0.9) markDrops.push(`${m} ${mA[m]} → ${mB[m]}`);
  }
}
const fails = [];
// A run where most items crash on either side compares nothing (e.g. OCR failed to load in a
// worktree without node_modules): every item "unchanged" would read as "No regression".
const nItems = (x) => (x.items || []).length;
const crashed = (x) => (x.items || []).filter((it) => it.crashed || it.error || typeof it.aggregate !== 'number').length;
for (const [lbl, x] of [[base, A], ['head', B]]) {
  if (nItems(x) && crashed(x) > nItems(x) / 2) fails.push(`INVALID RUN: ${crashed(x)} of ${nItems(x)} items failed on ${lbl} (check OCR/node_modules)`);
}
if (markDrops.length) fails.push(`fewer elements written: ${markDrops.join(', ')}`);
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
