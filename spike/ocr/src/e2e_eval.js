'use strict';
// End-to-end: detect lyric strips on full pages (strips.js), OCR each strip, match to GT lines.
//   node src/e2e_eval.js '<json config>' SHARD NSHARDS OUT.jsonl
// config: {engine: tess|paddle, model, lang: matched|combined|eng, psm, target: 40, compress: true|false, dropHyphens: false, variants: [...]}
const fs = require('fs'), path = require('path');
const IMG = require('./img'), S = require('./strips'), E = require('./engines');
const { compressGaps, VARIANTS, DATA } = require('./jobs');
const cfg = JSON.parse(process.argv[2]);
const shard = +process.argv[3], nshard = +process.argv[4], out = process.argv[5];
const LANGS = { combined: 'eng+deu+lat', eng: 'eng', lat: 'lat', deu: 'deu' };

(async () => {
  const pages = [];
  for (const v of cfg.variants || VARIANTS) for (const f of fs.readdirSync(path.join(DATA, v)).filter(f => f.endsWith('.gt.json')).sort()) pages.push({ v, f });
  const mine = pages.filter((_, i) => i % nshard === shard);
  const engines = {};
  const getEngine = async (lang) => {
    const key = cfg.engine === 'tess' ? (LANGS[cfg.lang] || lang) : 'p';
    if (!engines[key]) engines[key] = cfg.engine === 'tess' ? await E.tess(cfg, key) : (cfg.engine === 'none' ? await E.none() : await E.paddle(cfg));
    return engines[key];
  };
  const fd = fs.openSync(out, 'w');
  for (const { v, f } of mine) {
    const gt = JSON.parse(fs.readFileSync(path.join(DATA, v, f), 'utf8'));
    const page = IMG.readGray(path.join(DATA, v, f.replace('.gt.json', '.png')));
    const t0 = process.hrtime.bigint();
    const det = S.detectLyricLines(page, { dropHyphens: !!cfg.dropHyphens });
    const detMs = Number(process.hrtime.bigint() - t0) / 1e6;
    const eng = await getEngine(gt.lang);
    const dets = [];
    for (const [di, L] of det.lines.entries()) {
      const cx = (L.bbox[0] + L.bbox[2]) / 2;
      const blPage = S.unshearY(cx, L.baseline, det.skewDeg);
      // match GT
      let best = -1, bestD = 1e9;
      gt.lines.forEach((G, gi) => {
        const d = Math.abs(G.baseline - blPage);
        const ov = Math.min(G.bbox[2], L.bbox[2]) - Math.max(G.bbox[0], L.bbox[0]);
        if (d < 0.45 * G.size_px && ov > 0.5 * (G.bbox[2] - G.bbox[0]) && d < bestD) { bestD = d; best = gi; }
      });
      const scale = (cfg.target || 40) / L.sizePx;
      let img = L.strip; if (Math.abs(scale - 1) > 0.08) img = IMG.resize(img, scale);
      let xmap = null;
      if (cfg.compress) { const c = compressGaps(img, 0.5 * (cfg.target || 40)); xmap = c.xmap; img = c; }
      const t1 = process.hrtime.bigint();
      const r = await eng.recognize(img);
      const ms = Number(process.hrtime.bigint() - t1) / 1e6;
      const toPage = (x) => { const xx = xmap ? xmap[Math.max(0, Math.min(xmap.length - 1, Math.round(x)))] : x; return L.strip.x0 + xx / scale; };
      dets.push({ di, gi: best, ocr: r.text, conf: Math.round(r.conf), ms: Math.round(ms), sizePx: +L.sizePx.toFixed(1), xh: L.xHeight, nComps: L.nComps,
        bbox: L.bbox.map(Math.round), hyphens: L.hyphens.map(hh => [hh.x0, hh.x1]), extenders: L.extenders.map(e => [e.x0, e.x1]),
        tokens: r.tokens.map(t => [t.t, Math.round(toPage(t.x0)), Math.round(toPage(t.x1))]) });
    }
    fs.writeSync(fd, JSON.stringify({ page: `${v}/${f.replace('.gt.json', '')}`, variant: v, lang: gt.lang, layout: gt.layout, detMs: Math.round(detMs), skew: +det.skewDeg.toFixed(2), tilt: gt.tilt_deg || 0, nStaves: det.staves.length, nGt: gt.lines.length, dets }) + '\n');
  }
  fs.closeSync(fd);
  for (const e of Object.values(engines)) await e.terminate();
})().catch(e => { console.error(e); process.exit(1); });
