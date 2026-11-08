#!/usr/bin/env node
// OMR evaluation harness: scan.pdf -> v1 pipeline -> MusicXML, scored against truth.musicxml.
//
//   node tools/eval.mjs --out work/eval-r1-<key>.json [--only id,...] [--no-ocr] [--jobs N]
//                       [--src dir] [--dpi 200] [--timeout sec] [--set synthetic|real]
//
// Items: every corpus/{synthetic,real}/<id>/ holding scan.pdf + truth.musicxml.
// Pages are rasterised once (pdftoppm -gray -r DPI) into work/cache/ (atomic, shared
// between concurrent runs). Each item runs in its own child process (parallel pool).
// Produced MusicXML lands in <out minus .json>.out/<set>__<id>.musicxml.
//
// Metrics, all in [0,1] per item (higher is better):
//   pitch     F1 of pitch-correct notes on a per-part sequence alignment (measure+onset aware,
//             tolerant to insertions/deletions)
//   duration  F1 of aligned notes/rests whose duration (in quarters) is exact
//   rests     F1 of aligned rest pairs with exact duration (1 when neither side has rests)
//   lyrics    mean of syllable-text and syllabic accuracy on aligned notes, normalised by
//             max(truth lyrics, produced lyrics) (1 when neither side has lyrics)
//   parts     mean of part-count match, part-name match, share of recognised notes that
//             landed in the right part (alignment against the merged truth of all parts)
//   xml_valid 1 = XSD-valid (MusicXML 4.0), 0.5 = well-formed only, 0 = broken/missing
//   aggregate 0.3 pitch + 0.2 duration + 0.2 parts + 0.2 lyrics + 0.1 xml_valid
// Crashes (non-zero exit, timeout, no output) score 0 on everything.
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const __filename = fileURLToPath(import.meta.url);
const TOOLS = path.dirname(__filename);
const MVP = path.resolve(TOOLS, '..');
const ROOT = path.resolve(MVP, '..');
const CORPUS = path.join(ROOT, 'corpus');
const CACHE = path.join(MVP, 'work', 'cache');
const SCHEMA_DIRS = [path.join(ROOT, 'test', 'schema'), path.join(MVP, 'work', 'schema')];
const require = createRequire(import.meta.url);

// ---------------------------------------------------------------- args
function parseArgs(argv) {
  const a = { out: null, only: null, ocr: true, jobs: 0, src: path.join(MVP, 'src'), dpi: 200, timeout: 0, set: null, child: null, quiet: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const v = () => argv[++i];
    if (k === '--out') a.out = path.resolve(v());
    else if (k === '--only') a.only = v().split(',').map(s => s.trim()).filter(Boolean);
    else if (k === '--no-ocr') a.ocr = false;
    else if (k === '--jobs' || k === '-j') a.jobs = +v();
    else if (k === '--src') a.src = path.resolve(v());
    else if (k === '--dpi') a.dpi = +v();
    else if (k === '--timeout') a.timeout = +v();
    else if (k === '--set') a.set = v();
    else if (k === '--quiet') a.quiet = true;
    else if (k === '--child') a.child = v();
    else if (k === '-h' || k === '--help') { console.log(fs.readFileSync(__filename, 'utf8').split('\n').slice(1, 24).join('\n')); process.exit(0); }
    else throw new Error('unknown arg ' + k);
  }
  if (!a.timeout) a.timeout = a.ocr ? 900 : 300;
  return a;
}

// ---------------------------------------------------------------- child mode
async function childMain(specPath) {
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const req = createRequire(path.join(spec.src, 'x.js'));
  const { readGray } = req(path.join(spec.src, 'image.js'));
  const { convert } = req(path.join(spec.src, 'omr.js'));
  const pages = spec.pages.map(p => readGray(p));
  let ocr = null, worker = null;
  if (spec.ocr) {
    const { createWorker } = require(path.join(ROOT, 'spike/ocr/node_modules/tesseract.js'));
    const { PNG } = require('pngjs');
    worker = await createWorker('eng', 1, { langPath: path.join(MVP, 'dist/assets'), gzip: true, cacheMethod: 'none' });
    await worker.setParameters({ tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
    ocr = async (img) => {
      const png = new PNG({ width: img.width, height: img.height });
      for (let i = 0; i < img.data.length; i++) { png.data[i * 4] = png.data[i * 4 + 1] = png.data[i * 4 + 2] = img.data[i]; png.data[i * 4 + 3] = 255; }
      const { data } = await worker.recognize(PNG.sync.write(png), {}, { text: true, blocks: true });
      const words = [];
      for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const w of l.words) words.push({ text: w.text, conf: w.confidence, x0: w.bbox.x0, x1: w.bbox.x1 });
      return words;
    };
  }
  const t0 = Date.now();
  const r = await convert(pages, { ocr });
  const ms = Date.now() - t0;
  if (worker) await worker.terminate();
  fs.writeFileSync(spec.xmlOut, (r.score && r.score.xml) || '');
  fs.writeFileSync(spec.metaOut, JSON.stringify({
    ms, warnings: r.warnings || [],
    parts: ((r.score && r.score.parts) || []).map((p, i) => ({ name: p.name, notes: r.score.nNotes ? r.score.nNotes[i] : null })),
    measures: r.score && r.score.measures, fifths: r.score && r.score.fifths, time: r.score && r.score.time,
  }));
}

// ---------------------------------------------------------------- items + raster cache
function listItems(args) {
  const items = [];
  for (const set of ['synthetic', 'real']) {
    if (args.set && args.set !== set) continue;
    const dir = path.join(CORPUS, set);
    if (!fs.existsSync(dir)) continue;
    for (const id of fs.readdirSync(dir).sort()) {
      if (id.startsWith('_') || id === 'tools') continue;
      const d = path.join(dir, id);
      const pdf = path.join(d, 'scan.pdf'), truth = path.join(d, 'truth.musicxml');
      if (!fs.existsSync(pdf) || !fs.existsSync(truth)) continue;
      if (args.only && !args.only.includes(id) && !args.only.includes(`${set}/${id}`)) continue;
      items.push({ set, id, pdf, truth, key: `${set}__${id}` });
    }
  }
  return items;
}

function run(cmd, argv, opts = {}) {
  return new Promise((resolve) => {
    const p = spawn(cmd, argv, { stdio: ['ignore', 'pipe', 'pipe'], ...opts });
    let out = '', err = '';
    p.stdout.on('data', d => { out += d; if (out.length > 4e6) out = out.slice(-2e6); });
    p.stderr.on('data', d => { err += d; if (err.length > 4e6) err = err.slice(-2e6); });
    let timer = null, timedOut = false;
    if (opts.timeoutMs) timer = setTimeout(() => { timedOut = true; p.kill('SIGKILL'); }, opts.timeoutMs);
    p.on('close', (code, signal) => { if (timer) clearTimeout(timer); resolve({ code, signal, out, err, timedOut }); });
    p.on('error', e => { if (timer) clearTimeout(timer); resolve({ code: -1, out, err: String(e), timedOut }); });
  });
}

async function rasterize(item, dpi) {
  const st = fs.statSync(item.pdf);
  const stamp = `${st.size}:${Math.floor(st.mtimeMs)}:${dpi}`;
  const dir = path.join(CACHE, `${item.key}__r${dpi}`);
  const pagesIn = d => fs.readdirSync(d).filter(f => f.endsWith('.pgm')).sort((a, b) => parseInt(a.match(/(\d+)\.pgm$/)[1]) - parseInt(b.match(/(\d+)\.pgm$/)[1])).map(f => path.join(d, f));
  try {
    if (fs.readFileSync(path.join(dir, 'stamp.txt'), 'utf8') === stamp) { const p = pagesIn(dir); if (p.length) return p; }
  } catch {}
  fs.mkdirSync(CACHE, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(CACHE, `.tmp-${item.key}-`));
  const r = await run('pdftoppm', ['-gray', '-r', String(dpi), item.pdf, path.join(tmp, 'p')]);
  if (r.code !== 0) { fs.rmSync(tmp, { recursive: true, force: true }); throw new Error('pdftoppm failed: ' + r.err.slice(0, 300)); }
  fs.writeFileSync(path.join(tmp, 'stamp.txt'), stamp);
  try {
    if (fs.existsSync(dir)) { const old = dir + '.old-' + process.pid + '-' + Date.now(); fs.renameSync(dir, old); fs.rmSync(old, { recursive: true, force: true }); }
    fs.renameSync(tmp, dir);
  } catch {
    // a concurrent run won the race; use whichever complete copy exists
    if (!fs.existsSync(path.join(dir, 'stamp.txt'))) return pagesIn(tmp);
    fs.rmSync(tmp, { recursive: true, force: true });
  }
  return pagesIn(dir);
}

async function pool(items, n, fn) {
  const res = new Array(items.length);
  let next = 0;
  await Promise.all(Array.from({ length: Math.max(1, Math.min(n, items.length)) }, async () => {
    while (next < items.length) { const i = next++; res[i] = await fn(items[i], i); }
  }));
  return res;
}

// ---------------------------------------------------------------- minimal XML parser
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };
const decode = s => s.replace(/&(#x[0-9a-f]+|#\d+|\w+);/gi, (m, e) => e[0] === '#' ? String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : +e.slice(1)) : (ENT[e] ?? m));
function parseXML(s) {
  const root = { name: '#root', attrs: {}, children: [], text: '' };
  const stack = [root];
  const re = /<!--[\s\S]*?-->|<!\[CDATA\[([\s\S]*?)\]\]>|<\?[\s\S]*?\?>|<!DOCTYPE(?:[^>\[]|\[[\s\S]*?\])*>|<\/([^\s>]+)\s*>|<([^\s>\/!?]+)((?:\s+[^\s=\/>]+\s*=\s*(?:"[^"]*"|'[^']*'))*)\s*(\/?)>|([^<]+)/g;
  let m;
  while ((m = re.exec(s))) {
    const top = stack[stack.length - 1];
    if (m[1] !== undefined) top.text += m[1];
    else if (m[2]) { if (stack.length > 1) stack.pop(); }
    else if (m[3]) {
      const attrs = {};
      m[4].replace(/([^\s=]+)\s*=\s*("([^"]*)"|'([^']*)')/g, (_, k, __, a, b) => { attrs[k] = decode(a ?? b); });
      const el = { name: m[3], attrs, children: [], text: '' };
      top.children.push(el);
      if (!m[5]) stack.push(el);
    } else if (m[6]) top.text += decode(m[6]);
  }
  return root;
}
const kids = (el, name) => el ? el.children.filter(c => c.name === name) : [];
const kid = (el, name) => el ? el.children.find(c => c.name === name) : undefined;
const txt = (el, name) => { const k = kid(el, name); return k ? k.text.trim() : undefined; };
function find(el, name) { if (!el) return; if (el.name === name) return el; for (const c of el.children) { const r = find(c, name); if (r) return r; } }

// ---------------------------------------------------------------- MusicXML -> note events
const STEP = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const TYPEQ = { maxima: 32, long: 16, breve: 8, whole: 4, half: 2, quarter: 1, eighth: 0.5, '16th': 0.25, '32nd': 0.125, '64th': 0.0625, '128th': 0.03125 };
const normText = s => (s || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');

function extractScore(xml) {
  const doc = parseXML(xml);
  const sp = find(doc, 'score-partwise');
  if (!sp) throw new Error('no score-partwise root');
  const names = {};
  const pl = kid(sp, 'part-list');
  for (const s of kids(pl, 'score-part')) names[s.attrs.id] = txt(s, 'part-name') || '';
  const parts = [];
  for (const p of kids(sp, 'part')) {
    let div = 1;
    const notes = [];
    let staves = 1;
    const measures = kids(p, 'measure');
    measures.forEach((m, mi) => {
      let t = 0, last = 0;
      for (const c of m.children) {
        if (c.name === 'attributes') {
          const d = +txt(c, 'divisions'); if (d > 0) div = d;
          const s = +txt(c, 'staves'); if (s > 0) staves = Math.max(staves, s);
        } else if (c.name === 'backup') t -= (+txt(c, 'duration') || 0) / div;
        else if (c.name === 'forward') t += (+txt(c, 'duration') || 0) / div;
        else if (c.name === 'note') {
          if (kid(c, 'grace')) continue;
          const chord = !!kid(c, 'chord');
          let dur = (+txt(c, 'duration') || 0) / div;
          if (!dur) {
            const ty = TYPEQ[txt(c, 'type')] || 0;
            const dots = kids(c, 'dot').length;
            dur = ty * (2 - Math.pow(0.5, dots));
          }
          const on = chord ? last : t;
          if (!chord) { last = t; t += dur; }
          if (kid(c, 'cue')) continue;
          const pt = kid(c, 'pitch');
          const rest = !!kid(c, 'rest') || !pt;
          let midi = null;
          if (pt) midi = (+txt(pt, 'octave') + 1) * 12 + STEP[txt(pt, 'step')] + Math.round(+txt(pt, 'alter') || 0);
          const lyrics = kids(c, 'lyric').map((l, k) => ({
            num: l.attrs.number || String(k + 1),
            text: normText(kids(l, 'text').map(x => x.text).join('')),
            syl: txt(l, 'syllabic') || 'single',
          })).filter(l => l.text);
          notes.push({ m: mi, on: Math.round(on * 1e4) / 1e4, dur: Math.round(dur * 1e4) / 1e4, rest, midi, staff: +txt(c, 'staff') || 1, lyrics });
        }
      }
    });
    notes.sort((a, b) => a.m - b.m || a.on - b.on || (a.rest - b.rest) || (b.midi ?? -1) - (a.midi ?? -1));
    parts.push({ id: p.attrs.id, name: names[p.attrs.id] ?? p.attrs.id, notes, measures: measures.length, staves });
  }
  return parts;
}

// ---------------------------------------------------------------- alignment (Needleman-Wunsch)
function pairScore(a, b) {
  let s;
  if (a.rest && b.rest) s = 2;
  else if (a.rest || b.rest) return -2;
  else if (a.midi === b.midi) s = 3;
  else if (Math.abs(a.midi - b.midi) <= 2) s = 0.5;
  else s = -0.5;
  if (a.m === b.m) s += Math.abs(a.on - b.on) < 1e-3 ? 1 : 0.3;
  if (a.label !== undefined && a.label === b.want) s += 0.25; // tie-break unisons toward the assigned part
  return s;
}
const GAP = -1;
function align(T, P) {
  const n = T.length, m = P.length, W = m + 1;
  const tb = new Uint8Array((n + 1) * W); // 1 diag, 2 up (gap in P: truth deleted), 3 left (insertion)
  let prev = new Float64Array(W), cur = new Float64Array(W);
  for (let j = 1; j <= m; j++) { prev[j] = j * GAP; tb[j] = 3; }
  for (let i = 1; i <= n; i++) {
    cur[0] = i * GAP; tb[i * W] = 2;
    for (let j = 1; j <= m; j++) {
      const d = prev[j - 1] + pairScore(T[i - 1], P[j - 1]);
      const u = prev[j] + GAP, l = cur[j - 1] + GAP;
      if (d >= u && d >= l) { cur[j] = d; tb[i * W + j] = 1; }
      else if (u >= l) { cur[j] = u; tb[i * W + j] = 2; }
      else { cur[j] = l; tb[i * W + j] = 3; }
    }
    [prev, cur] = [cur, prev];
  }
  const pairs = [];
  let i = n, j = m;
  while (i > 0 || j > 0) {
    const t = tb[i * W + j];
    if (t === 1) { pairs.push([i - 1, j - 1]); i--; j--; }
    else if (t === 2) i--;
    else j--;
  }
  return pairs.reverse();
}

// ---------------------------------------------------------------- scoring
function normName(s) {
  return (s || '').toLowerCase().replace(/\bii\b/g, '2').replace(/\bi\b/g, '1').replace(/[^a-z0-9]/g, '');
}
function nameCredit(a, b) {
  const x = normName(a), y = normName(b);
  if (!x || !y) return 0;
  if (x === y) return 1;
  const bx = x.replace(/\d+/g, ''), by = y.replace(/\d+/g, '');
  if (bx && bx === by) return 0.75;
  if (bx && by && (bx.includes(by) || by.includes(bx))) return 0.5;
  return 0;
}

function matchParts(T, P) {
  const map = new Array(T.length).fill(-1), used = new Set();
  T.forEach((t, i) => { const j = P.findIndex((p, j) => !used.has(j) && normName(p.name) === normName(t.name) && normName(t.name)); if (j >= 0) { map[i] = j; used.add(j); } });
  const restP = P.map((_, j) => j).filter(j => !used.has(j));
  T.forEach((_, i) => { if (map[i] < 0 && restP.length) { map[i] = restP.shift(); used.add(map[i]); } });
  return map;
}

const f1 = (hits, a, b) => (a + b) ? 2 * hits / (a + b) : 1;

function scoreItem(truthXml, prodXml) {
  const T = extractScore(truthXml);
  const P = extractScore(prodXml);
  const map = matchParts(T, P);
  const tot = { tp: 0, pp: 0, pitchHit: 0, ta: 0, pa: 0, durHit: 0, tr: 0, pr: 0, restHit: 0, tl: 0, pl: 0, plOnLyricParts: 0, lyrText: 0, lyrSyl: 0 };
  const perPart = [];
  const count = (notes) => ({ pitched: notes.filter(n => !n.rest).length, rests: notes.filter(n => n.rest).length, all: notes.length, lyr: notes.reduce((s, n) => s + n.lyrics.length, 0) });
  T.forEach((t, i) => {
    const p = map[i] >= 0 ? P[map[i]] : null;
    const ct = count(t.notes), cp = p ? count(p.notes) : { pitched: 0, rests: 0, all: 0, lyr: 0 };
    let pitchHit = 0, durHit = 0, restHit = 0, lyrText = 0, lyrSyl = 0;
    if (p) {
      for (const [a, b] of align(t.notes, p.notes)) {
        const x = t.notes[a], y = p.notes[b];
        if (!x.rest && !y.rest && x.midi === y.midi) pitchHit++;
        if (x.rest === y.rest && Math.abs(x.dur - y.dur) < 1e-3) { durHit++; if (x.rest) restHit++; }
        if (!x.rest && !y.rest && x.lyrics.length) {
          const ys = [...y.lyrics].sort((u, v) => +u.num - +v.num);
          [...x.lyrics].sort((u, v) => +u.num - +v.num).forEach((l, k) => {
            const c = y.lyrics.find(z => z.num === l.num) || ys[k];
            if (!c) return;
            if (c.text === l.text) lyrText++;
            if (c.syl === l.syl) lyrSyl++;
          });
        }
      }
    }
    tot.tp += ct.pitched; tot.pp += cp.pitched; tot.pitchHit += pitchHit;
    tot.ta += ct.all; tot.pa += cp.all; tot.durHit += durHit;
    tot.tr += ct.rests; tot.pr += cp.rests; tot.restHit += restHit;
    tot.tl += ct.lyr; tot.pl += cp.lyr; if (ct.lyr) tot.plOnLyricParts += cp.lyr; tot.lyrText += lyrText; tot.lyrSyl += lyrSyl;
    perPart.push({ truth: t.name, ours: p ? p.name : null, tNotes: ct.pitched, pNotes: cp.pitched, tMeasures: t.measures, pMeasures: p ? p.measures : 0,
      tStaves: t.staves, pStaves: p ? p.staves : 0, pitch: +f1(pitchHit, ct.pitched, cp.pitched).toFixed(4), duration: +f1(durHit, ct.all, cp.all).toFixed(4),
      tLyr: ct.lyr, pLyr: cp.lyr, lyrText, lyrSyl });
  });
  // produced parts that matched no truth part: everything they hold is spurious
  P.forEach((p, j) => {
    if (map.includes(j)) return;
    const cp = count(p.notes);
    tot.pp += cp.pitched; tot.pa += cp.all; tot.pr += cp.rests; tot.pl += cp.lyr;
    perPart.push({ truth: null, ours: p.name, tNotes: 0, pNotes: cp.pitched, pMeasures: p.measures, pStaves: p.staves, pitch: 0, duration: 0, tLyr: 0, pLyr: cp.lyr });
  });
  // share of recognised notes that sit in the right part: align each produced part
  // against the merged truth of all parts and look at the labels of matched notes
  const merged = [];
  T.forEach((t, i) => t.notes.forEach(n => { if (!n.rest) merged.push({ ...n, label: i }); }));
  merged.sort((a, b) => a.m - b.m || a.on - b.on || b.midi - a.midi || a.label - b.label);
  let recognised = 0, right = 0;
  P.forEach((p, j) => {
    const want = map.indexOf(j);
    const pn = p.notes.filter(n => !n.rest).map(n => ({ ...n, want }));
    for (const [a, b] of align(merged, pn)) {
      if (merged[a].midi !== pn[b].midi) continue;
      recognised++; if (merged[a].label === want) right++;
    }
  });
  const countScore = Math.max(T.length, P.length) ? 1 - Math.abs(T.length - P.length) / Math.max(T.length, P.length) : 1;
  const nameScore = T.length ? T.reduce((s, t, i) => s + (map[i] >= 0 ? nameCredit(t.name, P[map[i]].name) : 0), 0) / Math.max(T.length, P.length) : 1;
  const share = recognised ? right / recognised : 0;
  const lyrDen = tot.tl + tot.pl;
  return {
    pitch: f1(tot.pitchHit, tot.tp, tot.pp),
    duration: f1(tot.durHit, tot.ta, tot.pa),
    rests: f1(tot.restHit, tot.tr, tot.pr),
    lyrics: lyrDen ? 0.5 * (2 * tot.lyrText / lyrDen) + 0.5 * (2 * tot.lyrSyl / lyrDen) : 1,
    lyrics_text: lyrDen ? 2 * tot.lyrText / lyrDen : 1,
    lyrics_syllabic: lyrDen ? 2 * tot.lyrSyl / lyrDen : 1,
    // diagnostic only: ignores produced lyrics on parts whose truth part carries none
    lyrics_lenient: (tot.tl + tot.plOnLyricParts) ? (tot.lyrText + tot.lyrSyl) / (tot.tl + tot.plOnLyricParts) : (tot.pl ? 0 : 1),
    parts: (countScore + nameScore + share) / 3,
    parts_detail: { truth: T.length, ours: P.length, count: countScore, names: nameScore, right_part_share: share, recognised, right },
    counts: tot, perPart,
  };
}

// ---------------------------------------------------------------- XML validity
function findSchema() {
  for (const d of SCHEMA_DIRS) { const f = path.join(d, 'musicxml.xsd'); if (fs.existsSync(f)) return f; }
  return null;
}
async function xmlValid(file, schema) {
  if (!fs.existsSync(file) || !fs.statSync(file).size) return { score: 0, wellFormed: false, xsd: null, err: 'missing/empty' };
  const wf = await run('xmllint', ['--noout', '--nonet', file]);
  if (wf.code !== 0) return { score: 0, wellFormed: false, xsd: null, err: wf.err.slice(0, 400) };
  if (!schema) return { score: 1, wellFormed: true, xsd: null };
  const v = await run('xmllint', ['--noout', '--nonet', '--schema', schema, file]);
  return { score: v.code === 0 ? 1 : 0.5, wellFormed: true, xsd: v.code === 0, err: v.code === 0 ? undefined : v.err.split('\n').filter(l => l && !/fails to validate/.test(l)).slice(0, 5).join('\n') };
}

// ---------------------------------------------------------------- main
const W = { pitch: 0.3, duration: 0.2, parts: 0.2, lyrics: 0.2, xml_valid: 0.1 };
const aggOf = r => W.pitch * r.pitch + W.duration * r.duration + W.parts * r.parts + W.lyrics * r.lyrics + W.xml_valid * r.xml_valid;
const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;

function srcHash(dir) {
  const h = crypto.createHash('sha1');
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.js')).sort()) h.update(f).update(fs.readFileSync(path.join(dir, f)));
  return h.digest('hex').slice(0, 12);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.child) return childMain(args.child);
  if (!args.out) throw new Error('--out <file.json> is required');
  const items = listItems(args);
  if (!items.length) throw new Error('no corpus items with scan.pdf + truth.musicxml' + (args.only ? ' matching --only' : ''));
  const jobs = args.jobs > 0 ? args.jobs : Math.min(items.length, Math.max(1, os.cpus().length - 2));
  const outDir = args.out.replace(/\.json$/i, '') + '.out';
  fs.mkdirSync(outDir, { recursive: true });
  const schema = findSchema();
  const t0 = Date.now();
  const log = (...m) => { if (!args.quiet) console.error(...m); };
  log(`eval: ${items.length} items, jobs=${jobs}, ocr=${args.ocr}, dpi=${args.dpi}, src=${args.src}, schema=${schema || 'none (well-formedness only)'}`);

  const results = await pool(items, jobs, async (it) => {
    const res = { id: it.id, set: it.set, crash: 0 };
    const tStart = Date.now();
    try {
      const pages = await rasterize(it, args.dpi);
      res.pagesN = pages.length;
      const xmlOut = path.join(outDir, it.key + '.musicxml');
      const metaOut = path.join(outDir, it.key + '.meta.json');
      const specPath = path.join(outDir, it.key + '.spec.json');
      for (const f of [xmlOut, metaOut]) fs.rmSync(f, { force: true });
      fs.writeFileSync(specPath, JSON.stringify({ src: args.src, pages, ocr: args.ocr, xmlOut, metaOut }));
      const r = await run(process.execPath, ['--max-old-space-size=8192', __filename, '--child', specPath], { timeoutMs: args.timeout * 1000, cwd: MVP });
      fs.writeFileSync(path.join(outDir, it.key + '.log'), `exit=${r.code} signal=${r.signal} timedOut=${r.timedOut}\n--- stdout\n${r.out}\n--- stderr\n${r.err}`);
      res.wall_ms = Date.now() - tStart;
      if (r.code !== 0 || !fs.existsSync(metaOut)) {
        res.crash = 1;
        res.error = r.timedOut ? `timeout after ${args.timeout}s` : (r.err.trim().split('\n').slice(-3).join(' | ') || `exit ${r.code}`);
      } else {
        const meta = JSON.parse(fs.readFileSync(metaOut, 'utf8'));
        res.runtime_ms = meta.ms; res.warnings = meta.warnings;
      }
      res.xml = await xmlValid(xmlOut, schema);
      res.xml_valid = res.crash ? 0 : res.xml.score;
      let s = null;
      if (!res.crash) {
        const prod = fs.readFileSync(xmlOut, 'utf8');
        try { s = prod.trim() ? scoreItem(fs.readFileSync(it.truth, 'utf8'), prod) : null; }
        catch (e) { res.score_error = String(e.message || e); }
      }
      if (s) Object.assign(res, s);
      else Object.assign(res, { pitch: 0, duration: 0, rests: 0, lyrics: 0, parts: 0 });
      if (res.crash) res.xml_valid = 0;
    } catch (e) {
      res.crash = 1; res.error = String(e.stack || e).split('\n').slice(0, 3).join(' | ');
      Object.assign(res, { pitch: 0, duration: 0, rests: 0, lyrics: 0, parts: 0, xml_valid: 0 });
    }
    res.aggregate = aggOf(res);
    log(`  ${res.crash ? 'CRASH' : 'done '} ${it.key}  agg=${res.aggregate.toFixed(3)}  ${((Date.now() - tStart) / 1000).toFixed(1)}s${res.error ? '  ' + res.error.slice(0, 160) : ''}`);
    return res;
  });

  const keys = ['aggregate', 'pitch', 'duration', 'rests', 'lyrics', 'lyrics_lenient', 'parts', 'xml_valid'];
  const summarize = rs => {
    const o = { n: rs.length };
    for (const k of keys) o[k] = rs.length ? +mean(rs.map(r => r[k] || 0)).toFixed(4) : null;
    o.crashes = rs.filter(r => r.crash).length;
    o.runtime_ms_mean = rs.length ? Math.round(mean(rs.map(r => r.runtime_ms || 0))) : null;
    return o;
  };
  const syn = results.filter(r => r.set === 'synthetic'), real = results.filter(r => r.set === 'real');
  const summary = {
    all: summarize(results), synthetic: summarize(syn), real: summarize(real),
    aggregate: summarize(results).aggregate, synthetic_aggregate: summarize(syn).aggregate, real_scan_aggregate: summarize(real).aggregate,
  };
  const report = {
    when: new Date().toISOString(), wall_s: Math.round((Date.now() - t0) / 100) / 10,
    config: { ocr: args.ocr, dpi: args.dpi, jobs, src: args.src, src_hash: srcHash(args.src), schema, weights: W, outputs: outDir },
    summary, items: results,
  };
  fs.writeFileSync(args.out, JSON.stringify(report, null, 1));

  // compact table
  const pad = (s, n) => String(s).padEnd(n).slice(0, n);
  const f = x => x == null ? '  -  ' : x.toFixed(3);
  const rows = [`${pad('item', 38)} ${pad('set', 4)}  agg   pitch  dur   rests lyric parts xml   parts(T/P) notes(T/P)  sec  crash`];
  for (const r of results) {
    const pd = r.parts_detail || {}, c = r.counts || {};
    rows.push(`${pad(r.id, 38)} ${pad(r.set.slice(0, 4), 4)}  ${f(r.aggregate)} ${f(r.pitch)} ${f(r.duration)} ${f(r.rests)} ${f(r.lyrics)} ${f(r.parts)} ${f(r.xml_valid)} ${pad(`${pd.truth ?? '-'}/${pd.ours ?? '-'}`, 10)} ${pad(`${c.tp ?? '-'}/${c.pp ?? '-'}`, 11)} ${pad(((r.runtime_ms || 0) / 1000).toFixed(1), 5)} ${r.crash ? 'X' : ''}`);
  }
  rows.push('-'.repeat(120));
  for (const [name, s] of [['ALL', summary.all], ['synthetic', summary.synthetic], ['real', summary.real]]) {
    if (!s.n) continue;
    rows.push(`${pad(`${name} (n=${s.n})`, 38)} ${pad('', 4)}  ${f(s.aggregate)} ${f(s.pitch)} ${f(s.duration)} ${f(s.rests)} ${f(s.lyrics)} ${f(s.parts)} ${f(s.xml_valid)} crashes=${s.crashes} mean_runtime=${(s.runtime_ms_mean / 1000).toFixed(1)}s`);
  }
  console.log(rows.join('\n'));
  console.log(`aggregate=${f(summary.aggregate)} synthetic=${f(summary.synthetic_aggregate)} real_scan_aggregate=${f(summary.real_scan_aggregate)}  -> ${args.out}  (${report.wall_s}s)`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) main().catch(e => { console.error(e.stack || e); process.exit(1); });

export { scoreItem, extractScore, parseXML, align };
