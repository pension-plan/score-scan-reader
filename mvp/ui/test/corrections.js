// User corrections (src/corrections.js) on a real page: with none the
// MusicXML is unchanged; an accidental, a dot, a rest and a dynamic each land
// on the note they name and the result stays well-formed (xmllint when present).
//   node ui/test/corrections.js [cache-dir-name]
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const MVP = path.join(__dirname, '../..');
const { readGray } = require(path.join(MVP, 'src/image'));
const Sess = require(path.join(MVP, 'ui/session.js'))();
const C = require(path.join(MVP, 'src/corrections'));
const req = (n) => require(path.join(MVP, 'src', n.replace(/^\.\//, '').replace(/\.js$/, '') + '.js'));
const dir = path.join(MVP, 'work/cache', process.argv[2] || 'coverage__layouts__choir-open-satb-gloria__clean__r200');
const fails = [];
const ok = (c, t) => { if (!c) fails.push(t); };
(async () => {
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.pgm')).sort();
  const s = Sess.createSession(req, {});
  const views = [];
  for (let i = 0; i < files.length; i++) { const e = await s.addPage(readGray(path.join(dir, files[i])), i, files.length); views.push(e ? Sess.pageView(e, i, req) : null); if (e && s.releasePage) s.releasePage(e); }
  const res = Sess.resultSummary(s.finish());
  const pages = {};
  res.pages.forEach(p => { const v = views[p.index]; if (v) pages[p.index] = { ss: v.ss, heads: v.heads, notes: p.notes }; });
  const xml = res.score.xml;
  ok(C.correctScore(res.score, [], pages).xml === xml, 'no corrections changed the MusicXML');
  // a note with a written line, away from the bar start
  const pg = pages[0], ss = pg.ss;
  const k = pg.notes.findIndex((n, j) => n && n[7] >= 0 && n[5] === 0 && j > 4);
  const [x, y] = pg.heads[k], n = pg.notes[k];
  const L = xml.split('\n');
  ok(L[n[7]].includes(`<step>${n[0]}</step>`) && L[n[7]].includes(`<octave>${n[2]}</octave>`), 'head line points at its note');
  const box = (cx, cy) => [cx - 0.3 * ss, cy - 0.6 * ss, cx + 0.3 * ss, cy + 0.6 * ss];
  const idents = [
    { id: 1, page: 0, box: box(x - 1.2 * ss, y), type: 'acc', sub: 'sharp' },
    { id: 2, page: 0, box: box(x + 1.1 * ss, y - 0.2 * ss), type: 'dot' },
    { id: 3, page: 0, box: box(x + 0.9 * ss, y), type: 'rest', sub: 'eighth' },
    { id: 4, page: 0, box: box(x, y + 5 * ss), type: 'dyn', sub: 'mf' },
    { id: 5, page: 0, box: box(x, y - 8 * ss), type: 'noise' },
    { id: 6, page: 0, box: box(x, y - 8 * ss), type: 'text', detail: 'dolce' },
  ];
  const out = C.correctScore(res.score, idents, pages);
  const cs = out.corrections;
  console.log(JSON.stringify(cs, null, 1));
  ok(cs.applied.length === 4, `4 corrections applied (got ${cs.applied.length}: ${JSON.stringify(cs.skipped)})`);
  ok(cs.hidden === 1 && cs.labels === 1, 'noise hidden, text kept as a label');
  ok(/<alter>1<\/alter>/.test(out.xml.split('\n').find(l => l.includes('<accidental>sharp</accidental>')) || ''), 'sharp sets alter 1 with an accidental');
  ok(/<direction placement="(above|below)"><direction-type><dynamics><mf\/>/.test(out.xml), 'mf direction added');
  ok(/<note><rest\/><duration>\d+<\/duration><voice>\d+<\/voice><type>eighth<\/type>/.test(out.xml), 'eighth rest inserted');
  ok((out.xml.match(/<dot\/>/g) || []).length > (xml.match(/<dot\/>/g) || []).length, 'dot added');
  try {
    const f = path.join(require('os').tmpdir(), 'ssr-corr-test.musicxml');
    fs.writeFileSync(f, out.xml);
    execFileSync('xmllint', ['--noout', f], { stdio: 'pipe' });
  } catch (e) { if (e.code !== 'ENOENT') fails.push('corrected MusicXML not well-formed: ' + String(e.stderr || e.message).slice(0, 300)); }
  console.log(fails.length ? 'CORRECTIONS FAIL\n' + fails.join('\n') : 'CORRECTIONS OK');
  process.exit(fails.length ? 1 : 0);
})();
