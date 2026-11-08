'use strict';
// tesseract.js evaluation on oracle lyric strips. Usage:
//   node src/tess_eval.js '<json config>' SHARD NSHARDS OUT.jsonl
// config: {model: fast|best_int|best, lang: matched|combined|eng|lat|deu, psm: 7, prep: raw|norm|clean, target: 40, dict: on|off}
const fs = require('fs'), path = require('path');
const { createWorker } = require('tesseract.js');
const { listJobs, oracleCrop, loadPage } = require('./jobs');
const IMG = require('./img');

const cfg = JSON.parse(process.argv[2]);
const shard = +process.argv[3], nshard = +process.argv[4], out = process.argv[5];
const MODELS = path.join(__dirname, '..', 'models', 'tessdata');
const LANGS = { matched: null, combined: 'eng+deu+lat', eng: 'eng', lat: 'lat', deu: 'deu' };

(async () => {
  const jobs = listJobs(cfg.variants).filter((_, i) => i % nshard === shard);
  const workers = {};
  const getWorker = async (langs) => {
    if (!workers[langs]) {
      const t0 = Date.now();
      const init = cfg.dict === 'off' ? { load_system_dawg: '0', load_freq_dawg: '0' } : {};
      const w = await createWorker(langs, 1, {
        langPath: path.join(MODELS, cfg.model), gzip: cfg.model === 'best_int', cacheMethod: 'none',
      }, init);
      await w.setParameters({ tessedit_pageseg_mode: String(cfg.psm || 7), user_defined_dpi: '300' });
      workers[langs] = w;
      workers[langs + ':initMs'] = Date.now() - t0;
    }
    return workers[langs];
  };
  const fd = fs.openSync(out, 'w');
  for (const j of jobs) {
    const langs = LANGS[cfg.lang] || j.lang;
    const w = await getWorker(langs);
    const page = loadPage(j.png);
    const c = oracleCrop(page, j.line, cfg.prep || 'norm', cfg.target || 40);
    const buf = IMG.toPNG(c);
    const t0 = process.hrtime.bigint();
    const { data } = await w.recognize(buf, {}, { text: true, blocks: true });
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    const words = [];
    for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const wd of l.words)
      words.push({ t: wd.text, c: Math.round(wd.confidence), b: [wd.bbox.x0, wd.bbox.y0, wd.bbox.x1, wd.bbox.y1].map(v => Math.round(v / c.scale)) });
    fs.writeSync(fd, JSON.stringify({ key: j.key, lang: j.lang, ocr: data.text.replace(/\n+/g, ' ').trim(), conf: Math.round(data.confidence), ms: Math.round(ms), w: c.width, h: c.height, words, initMs: workers[langs + ':initMs'] }) + '\n');
  }
  fs.closeSync(fd);
  for (const k of Object.keys(workers)) if (!k.includes(':')) await workers[k].terminate();
})().catch(e => { console.error(e); process.exit(1); });
