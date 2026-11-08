// Node checks of src/ml.js: the wrapped converter on one page (onnxruntime-node), and a
// detector that fails, which must leave the classical MusicXML unchanged plus one warning.
//   node assets-src/ml/node-test.js [page.pgm]
const path = require('path'), assert = require('assert');
const MVP = path.join(__dirname, '../..');
const { readGray } = require(path.join(MVP, 'src/image'));
const omr = require(path.join(MVP, 'src/omr'));
const ml = require(path.join(MVP, 'src/ml'));
const pgm = process.argv[2] || path.join(MVP, 'work/cache/synthetic__joplin-maple-leaf-piano__r200/p-1.pgm');
(async () => {
  const run = async (conv) => { await conv.addPage(readGray(pgm), 0, 1); return conv.finish(); };
  const plain = await run(omr.createConverter({}));
  // 1. a detector that cannot start: classical result, one warning, no retry
  let calls = 0;
  const broken = await run(ml.wrapConverter(omr.createConverter({}), async () => { calls++; throw new Error('offline'); }));
  assert.strictEqual(broken.score.xml, plain.score.xml, 'failed detector changed the MusicXML');
  assert.strictEqual(broken.warnings.filter(w => /ML symbol detector failed/.test(w)).length, 1);
  assert.strictEqual(calls, 1);
  // 2. the real detector
  const det = await ml.createNodeDetector();
  const t0 = Date.now();
  const r = await run(ml.wrapConverter(omr.createConverter({}), det.detect));
  await det.release();
  assert.ok(r.ml && r.ml.pages === 1 && !r.ml.failed, 'detector did not run');
  assert.ok(r.score.xml && r.score.xml.includes('<score-partwise'), 'no MusicXML');
  console.log(JSON.stringify({ ok: true, ms: Date.now() - t0, ml: r.ml, parts: r.score.parts.map((p, i) => p.name + ':' + r.score.nNotes[i]),
    notesPlain: plain.score.nNotes }));
})().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
