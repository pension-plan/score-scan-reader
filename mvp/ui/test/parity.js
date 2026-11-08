// Parity of the page's incremental session (ui/session.js) with omr.convert().
//   node ui/test/parity.js [--ocr] [--only id,...] [--out file.json]
// For each multi- and single-page item in the eval page cache (work/cache, made
// by tools/eval.mjs), runs omr.convert(pages) and the session (addPage per page,
// with the page buffers released as the page does, then finish) and compares
// the MusicXML, warnings and lyrics. Any difference means the session has
// drifted from the pipeline and the page would show a different result.
const fs = require('fs'), path = require('path');
const MVP = path.join(__dirname, '../..');
const ROOT = path.join(MVP, '..');
const { readGray } = require(path.join(MVP, 'src/image'));
const { convert } = require(path.join(MVP, 'src/omr'));
const Sess = require(path.join(MVP, 'ui/session.js'))();
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const useOCR = process.argv.includes('--ocr');
const only = arg('--only') ? arg('--only').split(',') : null;
const req = (n) => require(path.join(MVP, 'src', n.replace(/^\.\//, '').replace(/\.js$/, '') + '.js'));

const CACHE = path.join(MVP, 'work/cache');
const DEFAULT = ['beach-prayer-ssaa-piano', 'aloha-oe-full-score', 'bach-bwv244-62-closed-en-3v', 'methodist1905-st-anselm', 'schubert-lindenbaum-voice-piano', 'golden1923-america'];

async function makeOCR() {
  if (!useOCR) return { ocr: null, done: async () => {} };
  const { createWorker } = require(path.join(ROOT, 'spike/ocr/node_modules/tesseract.js'));
  const { PNG } = require(path.join(ROOT, 'spike/ocr/node_modules/pngjs'));
  const worker = await createWorker('eng', 1, { langPath: path.join(MVP, 'dist/assets'), gzip: true, cacheMethod: 'none' });
  await worker.setParameters({ tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
  const ocr = async (img) => {
    const png = new PNG({ width: img.width, height: img.height });
    for (let i = 0; i < img.data.length; i++) { png.data[i * 4] = png.data[i * 4 + 1] = png.data[i * 4 + 2] = img.data[i]; png.data[i * 4 + 3] = 255; }
    const { data } = await worker.recognize(PNG.sync.write(png), {}, { text: true, blocks: true });
    const words = [];
    for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const w of l.words) words.push({ text: w.text, conf: w.confidence, x0: w.bbox.x0, x1: w.bbox.x1 });
    return words;
  };
  return { ocr, done: () => worker.terminate() };
}

(async () => {
  const dirs = fs.existsSync(CACHE) ? fs.readdirSync(CACHE).filter((d) => !d.startsWith('challenge')) : [];
  const want = only || DEFAULT;
  const items = want.map((id) => [id, dirs.find((d) => d.split('__')[1] === id)]).filter(([, d]) => d);
  const { ocr, done } = await makeOCR();
  const rows = [];
  for (const [id, d] of items) {
    const files = fs.readdirSync(path.join(CACHE, d)).filter((f) => f.endsWith('.pgm')).sort((a, b) => parseInt(a.split('-')[1]) - parseInt(b.split('-')[1]));
    const load = () => files.map((f) => readGray(path.join(CACHE, d, f)));
    let t = Date.now();
    const ref = await convert(load(), { ocr });
    const tRef = Date.now() - t;
    t = Date.now();
    const pages = load();
    const s = Sess.createSession(req, { ocr });
    const views = [];
    for (let i = 0; i < pages.length; i++) {
      const e = await s.addPage(pages[i], i, pages.length);
      pages[i] = null;
      if (e) { views.push(Sess.pageView(e, i)); Sess.shrink(e.fr.gray, 1400); if (s.releasePage) s.releasePage(e); }
    }
    const got = s.finish();
    const tGot = Date.now() - t;
    const summary = Sess.resultSummary(got);
    structuredClone(summary); structuredClone(views); // must cross a worker boundary
    const lyr = (r) => JSON.stringify(Object.keys(r.lyricsBySystem).sort().map((k) => [k, r.lyricsBySystem[k].map((v) => [v.band, v.number, v.syllables.map((x) => x.text + ':' + x.syllabic)])]));
    const row = {
      id, pages: files.length,
      xml: ref.score.xml === got.score.xml,
      warnings: JSON.stringify(ref.warnings) === JSON.stringify(got.warnings),
      lyrics: lyr(ref) === lyr(got),
      heads: JSON.stringify(ref.pages.map((p) => p.fr.heads.map((h) => h.parts || []))) === JSON.stringify(summary.pages.map((p) => p.parts)),
      parts: (got.score.parts || []).map((p) => p.name).join(' '),
      ms: { convert: tRef, session: tGot },
    };
    row.ok = row.xml && row.warnings && row.lyrics && row.heads;
    if (!row.warnings) row.diff = { ref: ref.warnings, got: got.warnings };
    rows.push(row);
    console.log(JSON.stringify(row));
  }
  await done();
  const ok = rows.length > 0 && rows.every((r) => r.ok);
  if (arg('--out')) fs.writeFileSync(arg('--out'), JSON.stringify({ ok, ocr: useOCR, rows }, null, 1));
  console.log(ok ? `PARITY OK (${rows.length} items${useOCR ? ', OCR on' : ''})` : 'PARITY FAILED');
  process.exit(ok ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(1); });
