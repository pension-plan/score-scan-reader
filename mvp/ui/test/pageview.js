// Overlay data check for ui/session.js: what the page draws over each scan.
//   node ui/test/pageview.js [--only id,...] [--out file.json] [--session other/session.js]
// For cached pages (work/cache, made by tools/eval.mjs) of awkward layouts
// (two-up spreads, sideways and upside-down scans, halftone screens) plus
// plain pages, runs the page's session (addPage, pageView, release, finish,
// resultSummary) and the page's own head-to-part lookup, and reports:
//   heads      note heads drawn on the page
//   coloured   share of drawn heads that got a part colour (the rest are drawn
//              dashed grey as "head in no part")
//   inBounds   share of drawn heads inside the page image
//   onSheet    share of drawn heads within half a staff space of a head the
//              sheet's own front end found (catches a spread's half-page heads
//              drawn at the wrong place; 1 by construction on other pages)
//   orientation, mode, spread: how the page was read (the page caption)
// Fails (exit 1) when a page with parts has under 90% of its heads coloured
// or under 90% of them on the sheet.
const fs = require('fs'), path = require('path');
const MVP = path.join(__dirname, '../..');
const { readGray } = require(path.join(MVP, 'src/image'));
const arg0 = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const Sess = require(path.resolve(arg0('--session') || path.join(MVP, 'ui/session.js')))();
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const only = arg('--only') ? arg('--only').split(',') : null;
const OUT = arg('--out');
const req = (n) => require(path.join(MVP, 'src', n.replace(/^\.\//, '').replace(/\.js$/, '') + '.js'));
const CACHE = path.join(MVP, 'work/cache');
const DEFAULT = [
  'agrace-satb-spread', 'andantino-piano-spread', 'twinkle-piano2p-spread', 'wind-melody-spread',
  'agrace-satb-rot90', 'agrace-satb-rot180', 'agrace-satb-halftone', 'twinkle-piano2p-rot90',
  'methodist1905-st-anselm', 'beach-prayer-ssaa-piano',
];

// the page's lookup (ui/app.js book.applyResult + overlay): parts of head k on page i
function headPartsMap(res) {
  return new Map((res.pages || []).map((p) => [p.index, p.parts]));
}

(async () => {
  const dirs = fs.existsSync(CACHE) ? fs.readdirSync(CACHE) : [];
  const want = only || DEFAULT;
  const rows = [];
  for (const id of want) {
    // the plain scan variant (not -mild/-severe) of a challenge item, else the item's only one
    const d = dirs.find((x) => x.split('__').includes(id) && /__scan__r\d+$/.test(x)) || dirs.find((x) => x.split('__').includes(id));
    if (!d) { rows.push({ id, missing: true }); continue; }
    const files = fs.readdirSync(path.join(CACHE, d)).filter((f) => f.endsWith('.pgm')).sort((a, b) => parseInt(a.split('-')[1]) - parseInt(b.split('-')[1]));
    const s = Sess.createSession(req, {});
    const views = [], sheets = [];
    const t0 = Date.now();
    for (let i = 0; i < files.length; i++) {
      const entry = await s.addPage(readGray(path.join(CACHE, d, files[i])), i, files.length);
      if (!entry) { views.push(null); sheets.push(null); continue; }
      views.push(Sess.pageView(entry, i));
      sheets.push({ ss: entry.fr.ss, heads: (entry.fr.heads || []).map((h) => [h.x, h.y]) });
      if (s.releasePage) s.releasePage(entry);
    }
    const res = Sess.resultSummary(s.finish());
    const hp = headPartsMap(res);
    const pages = views.map((v, i) => {
      if (!v) return { page: i + 1, heads: 0 };
      const parts = hp.get(i) || [];
      const n = v.heads.length;
      const col = v.heads.filter((_, k) => (parts[k] || []).length).length;
      const inb = v.heads.filter(([x, y]) => x >= 0 && y >= 0 && x < v.width && y < v.height).length;
      const sh = sheets[i];
      const onSheet = v.heads.filter(([x, y]) => sh.heads.some(([a, b]) => Math.abs(a - x) < 0.5 * sh.ss && Math.abs(b - y) < 0.5 * sh.ss)).length;
      return {
        page: i + 1, heads: n, coloured: n ? +(col / n).toFixed(3) : null, inBounds: n ? +(inb / n).toFixed(3) : null, onSheet: n ? +(onSheet / n).toFixed(3) : null,
        orientation: v.orientation, mode: v.mode, spread: v.spread || 0, caption: Sess.pageNotes ? Sess.pageNotes(v) : undefined,
      };
    });
    rows.push({ id, cache: d, secs: (Date.now() - t0) / 1000, parts: (res.score.parts || []).map((p) => p.name), pages });
    console.error(id, JSON.stringify(pages));
  }
  const all = rows.flatMap((r) => (r.pages || []).filter((p) => p.heads).map((p) => ({ ...p, id: r.id, nParts: (r.parts || []).length })));
  const bad = all.filter((p) => p.nParts && (p.coloured < 0.9 || p.onSheet < 0.9));
  const mean = (k) => +(all.reduce((a, p) => a + (p[k] || 0), 0) / Math.max(1, all.length)).toFixed(3);
  const out = { pages: all.length, meanColoured: mean('coloured'), meanOnSheet: mean('onSheet'), failing: bad.map((p) => `${p.id} p${p.page}: coloured ${p.coloured}, on sheet ${p.onSheet}`), rows };
  out.ok = bad.length === 0;
  const txt = JSON.stringify(out, null, 1);
  if (OUT) fs.writeFileSync(OUT, txt);
  console.log(JSON.stringify({ pages: out.pages, meanColoured: out.meanColoured, meanOnSheet: out.meanOnSheet, failing: out.failing, ok: out.ok }, null, 1));
  process.exit(out.ok ? 0 : 1);
})();
