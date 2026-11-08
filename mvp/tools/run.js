// node tools/run.js page.pgm [out.musicxml] [--no-ocr] [--ml]
// OCR uses the app's languages (lyrics.js OCR_CONFIG); --ml adds the copista-2m detector
// (src/ml.js, onnxruntime-node; ORT_NODE overrides its path) as the app does when it is on.
const fs = require('fs'), path = require('path');
const { readGray } = require('../src/image');
const omr = require('../src/omr');
const T = path.join(__dirname, '../../spike/ocr/node_modules/tesseract.js');
(async () => {
  const g = readGray(process.argv[2]);
  let ocr = null, worker = null;
  if (!process.argv.includes('--no-ocr')) {
    const { createWorker } = require(T);
    const { PNG } = require('pngjs');
    const cfg = require('../src/lyrics').OCR_CONFIG;
    worker = await createWorker(cfg.langs, cfg.oem, { langPath: path.join(__dirname, '../dist/assets'), gzip: true, cacheMethod: 'none' });
    await worker.setParameters(cfg.params);
    ocr = async (img) => {
      const png = new PNG({ width: img.width, height: img.height });
      for (let i = 0; i < img.data.length; i++) { png.data[i*4]=png.data[i*4+1]=png.data[i*4+2]=img.data[i]; png.data[i*4+3]=255; }
      const { data } = await worker.recognize(PNG.sync.write(png), {}, { text: true, blocks: true });
      const words = [];
      for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const w of l.words) words.push({ text: w.text, conf: w.confidence, x0: w.bbox.x0, x1: w.bbox.x1 });
      return words;
    };
  }
  const t0 = Date.now();
  let r;
  if (process.argv.includes('--ml')) {
    const ml = require('../src/ml');
    const det = await ml.createNodeDetector({ ortPath: process.env.ORT_NODE || path.join(__dirname, '../../spike/ml/node_modules/onnxruntime-node') });
    const c = ml.wrapConverter(omr.createConverter({ ocr }), det.detect, {});
    await c.addPage(g, 0, 1);
    r = c.finish();
    await det.release();
  } else r = await omr.convert([g], { ocr });
  if (worker) await worker.terminate();
  console.log('ms', Date.now() - t0);
  console.log('parts', r.score.parts.map((p, i) => p.name + ':' + r.score.nNotes[i]).join(' '), 'measures', r.score.measures, 'key', r.score.fifths, 'time', r.score.time);
  for (const k in r.lyricsBySystem) for (const v of r.lyricsBySystem[k]) console.log('lyr', k, 'band', v.band, 'v' + v.number, v.syllables.map(s => s.text + (s.syllabic === 'begin' || s.syllabic === 'middle' ? '-' : '')).join(' '));
  console.log(r.warnings.join('\n'));
  if (process.argv[3] && !process.argv[3].startsWith('--')) fs.writeFileSync(process.argv[3], r.score.xml);
})().catch(e => { console.error(e); process.exit(1); });
