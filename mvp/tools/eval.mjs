#!/usr/bin/env node
// OMR evaluation harness: scan.pdf -> v1 pipeline -> MusicXML, scored against truth.musicxml.
//
//   node tools/eval.mjs --out work/eval-r1-<key>.json [--only id,...] [--no-ocr] [--jobs N]
//                       [--src dir] [--dpi 200|native|app] [--timeout sec]
//                       [--set synthetic|real|challenge|coverage] [--ml] [--ocr-lang eng|app|<langs>]
//                       [--ocr-workers N] [--lang-path dir] [--shard k/n]
//
// --shard k/n keeps every n-th item (sorted by id, starting with the k-th; k = 1..n), so n CI jobs
// together score the whole set.
// --ml-opts '<json>' implies --ml and passes options to wrapConverter (kinds, add, remove...).
// --ml wraps each conversion with the optional copista-2m detector (src/ml.js wrapConverter,
// onnxruntime-node; ORT_NODE overrides its path), as the app does when the detector is on.
// --ocr-lang picks the Tesseract languages: eng (default), app (lyrics.js OCR_CONFIG, what the
// page ships: eng+deu) or an explicit list such as eng+deu. --ocr-workers (default 2, as the page)
// is the number of Tesseract workers taking the reads a page starts together. --lang-path is the
// folder of {lang}.traineddata.gz (default dist/assets; tools/regress.mjs points it at each ref's own).
//
// Items: every corpus/{synthetic,real}/<id>/ holding scan.pdf + truth.musicxml (the default
// benchmark). --set challenge instead scores corpus/challenge/<category>/<id>/: every scan*.pdf
// (scan, scan-mild, scan-severe) is a separate item with id <category>/<id>/<variant>, scored
// against that folder's truth.musicxml; --only takes ids or prefixes (category, category/id).
// Challenge reports add summary.by_category and summary.by_variant.
// --set coverage scores corpus/coverage/<family>/<id>/ (the synthetic symbol/layout coverage
// suite; COVERAGE_DIR overrides the root): clean.pdf and every scan*.pdf is an item with id
// <family>/<id>/<variant>; folders without meta.json + truth.musicxml (still being written)
// are skipped. Coverage reports add summary.by_family, summary.by_variant and summary.perf;
// tools/coverage.mjs turns them into the per-symbol support matrix (docs/COVERAGE.md).
// Pages are rasterised once (pdftoppm -gray -r DPI) into work/cache/ (atomic, shared
// between concurrent runs). --dpi native rasterises each PDF at the resolution of its
// embedded scan image (pdfimages -list); --dpi app mimics the browser app (pages scaled to
// 2300 px wide). Each item runs in its own child process (parallel pool).
// Produced MusicXML lands in <out minus .json>.out/<set>__<id>.musicxml.
// Performance, per item: wall_ms (raster + child), runtime_ms (convert), page_ms[] (per page,
// from the converter's progress events) and assemble_ms, ms_per_page, raster px/megapixels,
// peak_rss_mb (child maxRSS; /proc VmHWM poll as fallback for crashed/timed-out children).
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
  const a = { out: null, only: null, ocr: true, jobs: 0, src: path.join(MVP, 'src'), dpi: 200, timeout: 0, set: null, child: null, quiet: false, ml: false, mlOpts: null, ocrLang: 'eng', ocrWorkers: 2, langPath: path.join(MVP, 'dist/assets') };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const v = () => argv[++i];
    if (k === '--out') a.out = path.resolve(v());
    else if (k === '--only') a.only = v().split(',').map(s => s.trim()).filter(Boolean);
    else if (k === '--shard') { const m = /^(\d+)\/(\d+)$/.exec(v() || ''); a.shard = m && [+m[1], +m[2]]; if (!a.shard || a.shard[0] < 1 || a.shard[0] > a.shard[1]) throw new Error('--shard takes k/n with 1 <= k <= n'); }
    else if (k === '--no-ocr') a.ocr = false;
    else if (k === '--jobs' || k === '-j') a.jobs = +v();
    else if (k === '--src') a.src = path.resolve(v());
    else if (k === '--dpi') { const x = v(); a.dpi = x === 'native' || x === 'app' ? x : +x; if (!(a.dpi === 'native' || a.dpi === 'app' || a.dpi > 0)) throw new Error('--dpi takes a number, native or app'); }
    else if (k === '--timeout') a.timeout = +v();
    else if (k === '--set') a.set = v();
    else if (k === '--quiet') a.quiet = true;
    else if (k === '--ml') a.ml = true;
    else if (k === '--ml-opts') { a.ml = true; a.mlOpts = JSON.parse(v()); }
    else if (k === '--ocr-lang') a.ocrLang = v();
    else if (k === '--ocr-workers') a.ocrWorkers = Math.max(1, +v() || 1);
    else if (k === '--lang-path') a.langPath = path.resolve(v());
    else if (k === '--child') a.child = v();
    else if (k === '-h' || k === '--help') { const L = fs.readFileSync(__filename, 'utf8').split('\n'); let e = 1; while (e < L.length && L[e].startsWith('//')) e++; console.log(L.slice(1, e).join('\n')); process.exit(0); }
    else throw new Error('unknown arg ' + k);
  }
  if (!a.timeout) a.timeout = a.ocr ? 900 : 300;
  return a;
}

// ---------------------------------------------------------------- child mode
async function childMain(specPath) {
  const tChild = performance.now();
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const req = createRequire(path.join(spec.src, 'x.js'));
  const { readGray } = req(path.join(spec.src, 'image.js'));
  const omr = req(path.join(spec.src, 'omr.js'));
  // the app's path: pages read one at a time (each page file loaded only when its turn
  // comes), each page's big buffers released after its step (converter releasePage, as
  // the page worker does), then finish; --ml wraps the converter with ml.wrapConverter
  let wrap = (c) => c, det = null;
  if (spec.ml) {
    const ml = req(path.join(spec.src, 'ml.js'));
    det = await ml.createNodeDetector({ assets: path.join(MVP, 'assets-src/ml'), ortPath: process.env.ORT_NODE || path.join(ROOT, 'spike/ml/node_modules/onnxruntime-node') });
    // ML_CACHE=<dir> keeps each page's detections (keyed by the page pixels), so runs that
    // only change how the corrections are applied skip the detector
    let detect = det.detect;
    if (process.env.ML_CACHE) {
      const crypto = await import('node:crypto');
      detect = async (g, o) => {
        const f = path.join(process.env.ML_CACHE, crypto.createHash('sha1').update(g.data).digest('hex') + '.json');
        if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'));
        const r = await det.detect(g, o);
        fs.mkdirSync(process.env.ML_CACHE, { recursive: true });
        fs.writeFileSync(f + '.' + process.pid, JSON.stringify({ dets: r.dets }));
        fs.renameSync(f + '.' + process.pid, f);
        return r;
      };
    }
    wrap = (c) => ml.wrapConverter(c, detect, spec.mlOpts || {});
  }
  const pages = spec.pages.map(() => null); // [width, height] once read
  const convert = async (files, o) => {
    if (!omr.createConverter) return omr.convert(files.map((f, i) => { const g = readGray(f); pages[i] = [g.width, g.height]; return g; }), o);
    // as the page runs it with OCR (and without the ML detector): each page's text read after its
    // step (deferText), a notes-only preview once the pages are analysed, then the full score
    const defer = !!(o.ocr && !spec.ml);
    const c = wrap(omr.createConverter(Object.assign({}, o, { deferText: defer })));
    for (let i = 0; i < files.length; i++) {
      let g = readGray(files[i]);
      pages[i] = [g.width, g.height];
      const e = await c.addPage(g, i, files.length);
      g = null;
      if (e && c.releasePage) { c.releasePage(e); (e.spread || []).forEach((h) => c.releasePage(h)); }
      await new Promise((r) => setTimeout(r, 0));
    }
    if (defer && c.preview && c.settle) { c.preview(); await c.settle(); }
    return c.finish();
  };
  let ocr = null, worker = null, extraWorker = null, more = [];
  if (spec.ocr) {
    // tesseract.js: the OCR spike's copy where it is installed, else the repository's dependency (CI)
    const spikeTess = path.join(ROOT, 'spike/ocr/node_modules/tesseract.js');
    const { createWorker } = require(fs.existsSync(spikeTess) ? spikeTess : createRequire(path.join(ROOT, 'package.json')).resolve('tesseract.js'));
    const lang = spec.ocrLang || 'eng';
    const cfg = lang === 'app' ? req(path.join(spec.src, 'lyrics.js')).OCR_CONFIG : null;
    worker = await createWorker(cfg ? cfg.langs : lang, cfg && cfg.oem != null ? cfg.oem : 1, { langPath: spec.langPath || path.join(MVP, 'dist/assets'), gzip: true, cacheMethod: 'none' });
    await worker.setParameters(cfg && cfg.params ? cfg.params : { tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
    // the image goes to Tesseract as a binary PGM: the same pixels as an RGBA PNG (identical words,
    // confidences and boxes), without the PNG encode and decode. The comment line keeps pixel bytes
    // out of the first 500 bytes, where tesseract.js looks for an EXIF orientation tag.
    const read = (wk) => async (img) => {
      const pgm = Buffer.concat([Buffer.from(`P5\n#${' '.repeat(500)}\n${img.width} ${img.height}\n255\n`), Buffer.from(img.data.buffer, img.data.byteOffset, img.data.byteLength)]);
      const { data } = await wk.recognize(pgm, {}, { text: true, blocks: true });
      const words = [];
      for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const w of l.words) words.push({ text: w.text, conf: w.confidence, x0: w.bbox.x0, x1: w.bbox.x1 });
      return words;
    };
    // more workers with the same languages (spec.ocrWorkers): a read waits for a free worker
    for (let k = 1; k < (spec.ocrWorkers || 1); k++) {
      const w = await createWorker(cfg ? cfg.langs : lang, cfg && cfg.oem != null ? cfg.oem : 1, { langPath: spec.langPath || path.join(MVP, 'dist/assets'), gzip: true, cacheMethod: 'none' });
      await w.setParameters(cfg && cfg.params ? cfg.params : { tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
      more.push(w);
    }
    const idle = [worker, ...more], queue = [];
    const give = (w) => { const r = queue.shift(); if (r) r(w); else idle.push(w); };
    const take = () => (idle.length ? Promise.resolve(idle.pop()) : new Promise((r) => queue.push(r)));
    const pool = { async recognize(...a) { const w = await take(); try { return await w.recognize(...a); } finally { give(w); } } };
    ocr = read(pool);
    // --ocr-lang app: the app's second pass (OCR_CONFIG.extraLangs), its worker made on first use
    if (cfg && cfg.extraLangs) {
      let w2 = null;
      ocr.extra = async (img) => {
        // (no user-words file: the Italian model's config asks for one that is not shipped)
        if (!w2) { w2 = await createWorker(cfg.extraLangs, cfg.oem != null ? cfg.oem : 1, { langPath: spec.langPath || path.join(MVP, 'dist/assets'), gzip: true, cacheMethod: 'none' }, { user_words_suffix: '' }); await w2.setParameters(cfg.params); extraWorker = w2; }
        return read(w2)(img);
      };
    }
  }
  // timing only: page i starts at its first progress event, assembly at the 'parts' stage
  const pageStart = [], perf = { assembleAt: null };
  const onProgress = (_m, info) => {
    if (!info) return;
    const now = performance.now();
    if (info.stage === 'parts') { if (perf.assembleAt == null) perf.assembleAt = now; }
    else if (Number.isInteger(info.page) && pageStart[info.page] == null) pageStart[info.page] = now;
  };
  const t0 = Date.now(), p0 = performance.now();
  const r = await convert(spec.pages, { ocr, onProgress });
  const ms = Date.now() - t0, p1 = performance.now();
  if (worker) await worker.terminate();
  // the ML detector's worker thread
  if (det && det.release) await det.release();
  for (const w of more) await w.terminate();
  if (extraWorker) await extraWorker.terminate();
  const ends = pages.map((_, i) => { for (let k = i + 1; k < pages.length; k++) if (pageStart[k] != null) return pageStart[k]; return perf.assembleAt ?? p1; });
  const page_ms = pages.map((_, i) => Math.round((ends[i] - (pageStart[i] ?? (i ? ends[i - 1] : p0))) * 10) / 10);
  fs.writeFileSync(spec.xmlOut, (r.score && r.score.xml) || '');
  fs.writeFileSync(spec.metaOut, JSON.stringify({
    ms, warnings: r.warnings || [], ...(r.ml ? { ml: r.ml } : {}),
    parts: ((r.score && r.score.parts) || []).map((p, i) => ({ name: p.name, notes: r.score.nNotes ? r.score.nNotes[i] : null })),
    measures: r.score && r.score.measures, fifths: r.score && r.score.fifths, time: r.score && r.score.time,
    perf: {
      page_ms, assemble_ms: perf.assembleAt == null ? null : Math.round((p1 - perf.assembleAt) * 10) / 10,
      px: pages, load_ms: Math.round(p0 - tChild),
      max_rss_mb: Math.round(process.resourceUsage().maxRSS / 1024 * 10) / 10,
    },
  }));
}

// ---------------------------------------------------------------- items + raster cache
const CHALLENGE = path.join(CORPUS, 'challenge');
const VARIANT_RANK = { scan: 0, 'scan-mild': 1, 'scan-severe': 2 };
function listChallengeItems(args) {
  const items = [];
  if (!fs.existsSync(CHALLENGE)) return items;
  const only = args.only && args.only.map(o => o.replace(/^challenge\//, '').replace(/\/+$/, ''));
  const rank = v => VARIANT_RANK[v] ?? 9;
  for (const cat of fs.readdirSync(CHALLENGE).sort()) {
    const cdir = path.join(CHALLENGE, cat);
    if (cat.startsWith('_') || cat.startsWith('.') || !fs.statSync(cdir).isDirectory()) continue;
    for (const id of fs.readdirSync(cdir).sort()) {
      const d = path.join(cdir, id), truth = path.join(d, 'truth.musicxml');
      if (id.startsWith('_') || id.startsWith('.') || !fs.statSync(d).isDirectory() || !fs.existsSync(truth)) continue;
      const variants = fs.readdirSync(d).filter(f => /^scan[^/]*\.pdf$/.test(f)).map(f => f.slice(0, -4))
        .sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
      for (const variant of variants) {
        const cid = `${cat}/${id}/${variant}`;
        if (only && !only.some(o => cid === o || cid.startsWith(o + '/'))) continue;
        items.push({ set: 'challenge', id: cid, category: cat, item: id, variant, pdf: path.join(d, variant + '.pdf'), truth, key: `challenge__${cat}__${id}__${variant}` });
      }
    }
  }
  return items;
}

// coverage suite: corpus/coverage/<family>/<id>/{clean,scan,scan-severe,...}.pdf; only complete
// folders (meta.json + truth.musicxml; generators write meta last) are listed
const COVERAGE = process.env.COVERAGE_DIR ? path.resolve(process.env.COVERAGE_DIR) : path.join(CORPUS, 'coverage');
const COV_RANK = { clean: 0, scan: 1, 'scan-mild': 2, 'scan-severe': 3 };
function listCoverageItems(args) {
  const items = [];
  if (!fs.existsSync(COVERAGE)) return items;
  const only = args.only && args.only.map(o => o.replace(/^coverage\//, '').replace(/\/+$/, ''));
  const rank = v => COV_RANK[v] ?? 9;
  const isDir = p => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };
  for (const fam of fs.readdirSync(COVERAGE).sort()) {
    const fdir = path.join(COVERAGE, fam);
    if (fam.startsWith('_') || fam.startsWith('.') || !isDir(fdir)) continue;
    for (const id of fs.readdirSync(fdir).sort()) {
      const d = path.join(fdir, id), truth = path.join(d, 'truth.musicxml'), meta = path.join(d, 'meta.json');
      if (id.startsWith('_') || id.startsWith('.') || !isDir(d) || !fs.existsSync(truth) || !fs.existsSync(meta)) continue;
      const variants = fs.readdirSync(d).filter(f => /^(clean|scan[^/]*)\.pdf$/.test(f) && fs.statSync(path.join(d, f)).size > 0)
        .map(f => f.slice(0, -4)).sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
      for (const variant of variants) {
        const cid = `${fam}/${id}/${variant}`;
        if (only && !only.some(o => cid === o || cid.startsWith(o + '/'))) continue;
        items.push({ set: 'coverage', id: cid, family: fam, item: id, variant, dir: d, pdf: path.join(d, variant + '.pdf'), truth, meta, key: `coverage__${fam}__${id}__${variant}` });
      }
    }
  }
  return items;
}

// pdfinfo / pdfimages facts about the input PDF (coverage perf table)
async function pdfFacts(pdf) {
  const o = {};
  const info = await run('pdfinfo', ['-f', '1', '-l', '1', pdf]);
  const pg = info.out.match(/^Pages:\s+(\d+)/m); if (pg) o.pdf_pages = +pg[1];
  const sz = info.out.match(/^Page\s+1 size:\s+([\d.]+) x ([\d.]+) pts/m); if (sz) o.page_pts = [+(+sz[1]).toFixed(1), +(+sz[2]).toFixed(1)];
  o.src_ppi = await nativeDpi(pdf);
  return o;
}
async function nativeDpi(pdf) {
  const r = await run('pdfimages', ['-list', pdf]);
  const ppi = r.out.split('\n').slice(2).map(l => l.trim().split(/\s+/)).filter(c => c.length >= 14 && c[2] === 'image').map(c => Math.round(+c[12])).filter(x => x > 0);
  if (!ppi.length) return null;
  const cnt = {}; for (const x of ppi) cnt[x] = (cnt[x] || 0) + 1;
  return +Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a])[0];
}

function listItems(args) {
  if (args.set === 'challenge') return listChallengeItems(args);
  if (args.set === 'coverage') return listCoverageItems(args);
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
    // peak resident memory of the child (Linux VmHWM), polled; survives timeouts and crashes
    let hwmKb = 0, poll = null;
    if (opts.trackRss && p.pid && fs.existsSync('/proc/self/status')) {
      const sample = () => { try { const m = fs.readFileSync(`/proc/${p.pid}/status`, 'utf8').match(/^VmHWM:\s+(\d+)/m); if (m) hwmKb = Math.max(hwmKb, +m[1]); } catch {} };
      poll = setInterval(sample, 200);
      p.on('exit', sample);
    }
    const done = () => { if (timer) clearTimeout(timer); if (poll) clearInterval(poll); };
    p.on('close', (code, signal) => { done(); resolve({ code, signal, out, err, timedOut, hwmKb }); });
    p.on('error', e => { done(); resolve({ code: -1, out, err: String(e), timedOut, hwmKb }); });
  });
}

async function rasterize(item, dpi) {
  const st = fs.statSync(item.pdf);
  const stamp = `${st.size}:${Math.floor(st.mtimeMs)}:${dpi}`;
  const dir = path.join(CACHE, `${item.key}__r${dpi}`);
  // 'app': same raster size as the browser app (pdf.js page scaled to 2300 px wide)
  const res = dpi === 'app' ? ['-scale-to-x', '2300', '-scale-to-y', '-1'] : ['-r', String(dpi)];
  const pagesIn = d => fs.readdirSync(d).filter(f => f.endsWith('.pgm')).sort((a, b) => parseInt(a.match(/(\d+)\.pgm$/)[1]) - parseInt(b.match(/(\d+)\.pgm$/)[1])).map(f => path.join(d, f));
  try {
    if (fs.readFileSync(path.join(dir, 'stamp.txt'), 'utf8') === stamp) { const p = pagesIn(dir); if (p.length) return p; }
  } catch {}
  fs.mkdirSync(CACHE, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(CACHE, `.tmp-${item.key}-`));
  const r = await run('pdftoppm', ['-gray', ...res, item.pdf, path.join(tmp, 'p')]);
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
          const pt = kid(c, 'pitch'), un = kid(c, 'unpitched');
          const rest = !!kid(c, 'rest') || (!pt && !un);
          let midi = null;
          if (pt) midi = (+txt(pt, 'octave') + 1) * 12 + STEP[txt(pt, 'step')] + Math.round(+txt(pt, 'alter') || 0);
          // an unpitched (percussion) note: its staff position (display step and octave), kept apart
          // from pitches (+1000) so a drum note matches only a drum note at the same position
          else if (un) midi = 1000 + (+txt(un, 'display-octave') + 1) * 12 + STEP[txt(un, 'display-step')];
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
  let items = listItems(args);
  if (args.shard) {
    const [k, n] = args.shard, keep = new Set(items.map(it => it.key).sort().filter((_, i) => i % n === k - 1));
    items = items.filter(it => keep.has(it.key));
  }
  if (!items.length) throw new Error('no corpus items with scan.pdf + truth.musicxml' + (args.only ? ' matching --only' : ''));
  // shared host: never more than OMR_MAX_JOBS (default 16) child processes, and while the
  // machine is over 90% busy (load1 > 0.9 x CPUs) wait before starting heavy work (not in CI:
  // the runner is ours alone, and the previous step's load would only delay this one)
  const CAP = Math.max(1, +(process.env.OMR_MAX_JOBS || 16));
  const jobs = Math.min(CAP, items.length, args.jobs > 0 ? args.jobs : CAP);
  for (let w = 0; w < 30 && !process.env.CI && os.loadavg()[0] > 0.9 * os.cpus().length; w++) {
    if (w === 0) console.error(`eval: host over 90% busy (load ${os.loadavg()[0].toFixed(0)}), waiting up to 5 min before starting`);
    await new Promise((r) => setTimeout(r, 10000));
  }
  const outDir = args.out.replace(/\.json$/i, '') + '.out';
  fs.mkdirSync(outDir, { recursive: true });
  const schema = findSchema();
  const t0 = Date.now();
  const log = (...m) => { if (!args.quiet) console.error(...m); };
  log(`eval: ${items.length} items, jobs=${jobs}, ocr=${args.ocr}${args.ocr ? ' (' + args.ocrLang + ')' : ''}${args.ml ? ', ml=on' : ''}, dpi=${args.dpi}, src=${args.src}, schema=${schema || 'none (well-formedness only)'}`);

  const results0 = await pool(items, jobs, async (it) => {
    const res = { id: it.id, set: it.set, crash: 0 };
    if (it.set === 'challenge') Object.assign(res, { category: it.category, item: it.item, variant: it.variant });
    if (it.set === 'coverage') Object.assign(res, { family: it.family, item: it.item, variant: it.variant, key: it.key });
    const tStart = Date.now();
    try {
      if (it.set === 'coverage') Object.assign(res, await pdfFacts(it.pdf));
      const dpi = args.dpi === 'native' ? (res.src_ppi || await nativeDpi(it.pdf) || 300) : args.dpi;
      if (typeof args.dpi !== 'number') res.raster_dpi = dpi;
      const pages = await rasterize(it, dpi);
      res.raster_ms = Date.now() - tStart;
      res.pagesN = pages.length;
      const xmlOut = path.join(outDir, it.key + '.musicxml');
      const metaOut = path.join(outDir, it.key + '.meta.json');
      const specPath = path.join(outDir, it.key + '.spec.json');
      for (const f of [xmlOut, metaOut]) fs.rmSync(f, { force: true });
      fs.writeFileSync(specPath, JSON.stringify({ src: args.src, pages, ocr: args.ocr, ocrLang: args.ocrLang, ocrWorkers: args.ocrWorkers, langPath: args.langPath, ml: args.ml, mlOpts: args.mlOpts, xmlOut, metaOut }));
      const tChild = Date.now();
      const r = await run(process.execPath, ['--max-old-space-size=8192', __filename, '--child', specPath], { timeoutMs: args.timeout * 1000, cwd: MVP, trackRss: true });
      res.child_ms = Date.now() - tChild;
      if (r.hwmKb) res.peak_rss_mb = Math.round(r.hwmKb / 1024 * 10) / 10;
      fs.writeFileSync(path.join(outDir, it.key + '.log'), `exit=${r.code} signal=${r.signal} timedOut=${r.timedOut}\n--- stdout\n${r.out}\n--- stderr\n${r.err}`);
      res.wall_ms = Date.now() - tStart;
      if (r.code !== 0 || !fs.existsSync(metaOut)) {
        res.crash = 1;
        res.error = r.timedOut ? `timeout after ${args.timeout}s` : (r.err.trim().split('\n').slice(-3).join(' | ') || `exit ${r.code}`);
      } else {
        const meta = JSON.parse(fs.readFileSync(metaOut, 'utf8'));
        res.runtime_ms = meta.ms; res.warnings = meta.warnings;
        if (meta.ml) res.ml = meta.ml;
        const pf = meta.perf;
        if (pf) {
          res.page_ms = pf.page_ms; res.assemble_ms = pf.assemble_ms; res.load_ms = pf.load_ms; res.px = pf.px;
          res.megapixels = +(pf.px.reduce((s, [w, h]) => s + w * h, 0) / 1e6).toFixed(3);
          if (pf.max_rss_mb) res.peak_rss_mb = Math.max(pf.max_rss_mb, res.peak_rss_mb || 0);
        }
        if (res.pagesN) res.ms_per_page = Math.round(meta.ms / res.pagesN);
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
      // coverage generators rewrite their folders: an input that vanished mid-run is not an app crash
      if (it.set === 'coverage') {
        let changed = false; try { changed = fs.statSync(it.pdf).mtimeMs >= t0 || fs.statSync(it.truth).mtimeMs >= t0; } catch { changed = true; }
        if ((e && e.code === 'ENOENT') || changed) res.skipped = 'input missing or rewritten during the run (corpus being regenerated)';
      }
    }
    res.aggregate = aggOf(res);
    log(`  ${res.skipped ? 'SKIP ' : res.crash ? 'CRASH' : 'done '} ${it.key}  agg=${res.aggregate.toFixed(3)}  ${((Date.now() - tStart) / 1000).toFixed(1)}s${res.error ? '  ' + res.error.slice(0, 160) : ''}`);
    return res;
  });

  const skipped = results0.filter(r => r.skipped).map(r => ({ id: r.id, why: r.skipped }));
  const results = results0.filter(r => !r.skipped);
  if (skipped.length) log(`skipped ${skipped.length} item(s) whose input vanished during the run: ${skipped.map(s => s.id).join(', ')}`);
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
  const chal = results.filter(r => r.set === 'challenge');
  if (chal.length) {
    const groupBy = (rs, k) => { const g = {}; for (const r of rs) (g[r[k]] ||= []).push(r); return Object.fromEntries(Object.keys(g).sort().map(x => [x, summarize(g[x])])); };
    summary.challenge = summarize(chal);
    summary.challenge_aggregate = summary.challenge.aggregate;
    summary.by_category = groupBy(chal, 'category');
    summary.by_variant = groupBy(chal, 'variant');
  }
  const cov = results.filter(r => r.set === 'coverage');
  if (cov.length) {
    const groupBy = (rs, k) => { const g = {}; for (const r of rs) (g[r[k]] ||= []).push(r); return Object.fromEntries(Object.keys(g).sort().map(x => [x, summarize(g[x])])); };
    const med = a => { const b = a.filter(x => x != null).sort((x, y) => x - y); return b.length ? b[b.length >> 1] : null; };
    const ok = cov.filter(r => !r.crash);
    summary.coverage = summarize(cov);
    summary.coverage_aggregate = summary.coverage.aggregate;
    summary.by_family = groupBy(cov, 'family');
    summary.by_variant = groupBy(cov, 'variant');
    summary.perf = {
      n: ok.length, jobs, ms_per_page_median: med(ok.map(r => r.ms_per_page)), ms_per_page_max: Math.max(0, ...ok.map(r => r.ms_per_page || 0)),
      peak_rss_mb_median: med(cov.map(r => r.peak_rss_mb)), peak_rss_mb_max: Math.max(0, ...cov.map(r => r.peak_rss_mb || 0)),
      ms_per_megapixel: (() => { const mp = ok.reduce((s, r) => s + (r.megapixels || 0), 0); return mp ? Math.round(ok.reduce((s, r) => s + (r.megapixels ? r.runtime_ms : 0), 0) / mp) : null; })(),
    };
  }
  const report = {
    when: new Date().toISOString(), wall_s: Math.round((Date.now() - t0) / 100) / 10,
    config: { ocr: args.ocr, ...(args.ocr ? { ocr_lang: args.ocrLang } : {}), ...(args.ml ? { ml: args.mlOpts || true } : {}), dpi: args.dpi, jobs, src: args.src, src_hash: srcHash(args.src), schema, weights: W, outputs: outDir, ...(chal.length ? { set: 'challenge' } : {}), ...(cov.length ? { set: 'coverage', coverage_dir: COVERAGE, cpus: os.cpus().length, loadavg: os.loadavg().map(x => +x.toFixed(1)) } : {}) },
    summary, items: results, ...(skipped.length ? { skipped } : {}),
  };
  fs.writeFileSync(args.out, JSON.stringify(report, null, 1));

  // compact table
  const pad = (s, n) => String(s).padEnd(n).slice(0, n);
  const f = x => x == null ? '  -  ' : x.toFixed(3);
  const IW = chal.length || cov.length ? Math.max(38, ...results.map(r => r.id.length)) : 38;
  const rows = [`${pad('item', IW)} ${pad('set', 4)}  agg   pitch  dur   rests lyric parts xml   parts(T/P) notes(T/P)  sec  crash${cov.length ? '  pg  ms/pg   MP    MB' : ''}`];
  for (const r of results) {
    const pd = r.parts_detail || {}, c = r.counts || {};
    const perf = cov.length ? `  ${pad(r.pagesN ?? '-', 3)} ${pad(r.ms_per_page ?? '-', 7)} ${pad(r.megapixels != null ? r.megapixels.toFixed(1) : '-', 5)} ${pad(r.peak_rss_mb != null ? Math.round(r.peak_rss_mb) : '-', 5)}` : '';
    rows.push(`${pad(r.id, IW)} ${pad(r.set.slice(0, 4), 4)}  ${f(r.aggregate)} ${f(r.pitch)} ${f(r.duration)} ${f(r.rests)} ${f(r.lyrics)} ${f(r.parts)} ${f(r.xml_valid)} ${pad(`${pd.truth ?? '-'}/${pd.ours ?? '-'}`, 10)} ${pad(`${c.tp ?? '-'}/${c.pp ?? '-'}`, 11)} ${pad(((r.runtime_ms || 0) / 1000).toFixed(1), 5)} ${cov.length ? (r.crash ? 'X' : ' ') + perf : (r.crash ? 'X' : '')}`);
  }
  rows.push('-'.repeat(IW + 82));
  const groups = [['ALL', summary.all], ['synthetic', summary.synthetic], ['real', summary.real]];
  if (chal.length) for (const k of ['by_category', 'by_variant']) for (const [g, s] of Object.entries(summary[k])) groups.push([g, s]);
  if (cov.length) for (const k of ['by_family', 'by_variant']) for (const [g, s] of Object.entries(summary[k])) groups.push([g, s]);
  for (const [name, s] of groups) {
    if (!s.n) continue;
    rows.push(`${pad(`${name} (n=${s.n})`, IW)} ${pad('', 4)}  ${f(s.aggregate)} ${f(s.pitch)} ${f(s.duration)} ${f(s.rests)} ${f(s.lyrics)} ${f(s.parts)} ${f(s.xml_valid)} crashes=${s.crashes} mean_runtime=${(s.runtime_ms_mean / 1000).toFixed(1)}s`);
  }
  console.log(rows.join('\n'));
  if (chal.length) console.log(`challenge_aggregate=${f(summary.challenge_aggregate)} ${Object.entries(summary.by_category).map(([k, s]) => `${k}=${f(s.aggregate)}`).join(' ')} crashes=${summary.challenge.crashes}  -> ${args.out}  (${report.wall_s}s)`);
  else if (cov.length) console.log(`coverage_aggregate=${f(summary.coverage_aggregate)} ${Object.entries(summary.by_family).map(([k, s]) => `${k}=${f(s.aggregate)}`).join(' ')} crashes=${summary.coverage.crashes} ms/page(median)=${summary.perf.ms_per_page_median} peakMB(max)=${summary.perf.peak_rss_mb_max}  -> ${args.out}  (${report.wall_s}s)`);
  else console.log(`aggregate=${f(summary.aggregate)} synthetic=${f(summary.synthetic_aggregate)} real_scan_aggregate=${f(summary.real_scan_aggregate)}  -> ${args.out}  (${report.wall_s}s)`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) main().catch(e => { console.error(e.stack || e); process.exit(1); });

export { scoreItem, extractScore, parseXML, align };
