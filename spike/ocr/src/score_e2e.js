'use strict';
// Score end-to-end results (detected strips). Usage: node src/score_e2e.js PREFIX > results/summary_e2e_*.json
const fs = require('fs'), path = require('path');
const M = require('./metrics');
const { DATA } = require('./jobs');
const RAW = path.join(__dirname, '..', 'results', 'raw');
const prefix = process.argv[2];
const DASH = /^[\-‐-―−_~]+$/;

function fuse(tokens, hyphens, mode) {
  // mode: 'union' (OCR dash tokens or geometric bars) | 'geo' (geometry only)
  const toks = [], ocrDash = [];
  for (const [t, x0, x1] of tokens) { if (DASH.test(t)) ocrDash.push((x0 + x1) / 2); else toks.push({ t: mode === 'geo' ? t.replace(/^[\-‐-―]+|[\-‐-―_]+$/g, '') : t, x0, x1 }); }
  const geo = hyphens.map(([a, b]) => (a + b) / 2);
  const ev = mode === 'geo' ? geo : geo.concat(ocrDash);
  const has = (a, b) => ev.some(c => c > a && c < b);
  let s = '';
  if (toks.length && has(-1e9, toks[0].x0)) s += '- ';
  toks.forEach((tk, i) => {
    s += tk.t;
    const nx = toks[i + 1];
    if (nx) s += (has(tk.x1 - 2, nx.x0 + 2) && !/-$/.test(tk.t)) ? ' - ' : ' ';
    else if (has(tk.x1 - 2, 1e9) && !/-$/.test(tk.t)) s += ' -';
  });
  return s.trim();
}

const out = {};
for (const f of fs.readdirSync(RAW).filter(f => f.startsWith(prefix) && f.endsWith('.jsonl'))) {
  const cfg = f.replace(/\.\d+\.jsonl$/, '');
  const C = (out[cfg] ||= { rows: { raw: [], union: [], geo: [] }, byVariant: {}, det: { gt: 0, found: 0, dets: 0, fp: 0, dup: 0 }, geoHy: { tp: 0, fp: 0, fn: 0 }, geoExt: { tp: 0, fp: 0, fn: 0 }, detMs: 0, pages: 0, ocrMs: 0, sizeErr: [] });
  for (const ln of fs.readFileSync(path.join(RAW, f), 'utf8').split('\n')) {
    if (!ln) continue;
    const P = JSON.parse(ln);
    const gt = JSON.parse(fs.readFileSync(path.join(DATA, P.page + '.gt.json'), 'utf8'));
    C.pages++; C.detMs += P.detMs;
    const V = (C.byVariant[P.variant] ||= { raw: [], union: [], gt: 0, found: 0, fp: 0 });
    const LG = ((C.byLang ||= {})[P.lang] ||= []);
    C.det.dets += P.dets.length;
    const used = new Set();
    for (const d of P.dets) { if (d.gi < 0) { C.det.fp++; V.fp++; } else if (used.has(d.gi)) C.det.dup++; else used.add(d.gi); C.ocrMs += d.ms; }
    gt.lines.forEach((G, gi) => {
      C.det.gt++; V.gt++;
      const d = P.dets.find(x => x.gi === gi);
      if (d) { C.det.found++; V.found++; C.sizeErr.push(Math.abs(d.sizePx - G.size_px) / G.size_px); }
      const raw = d ? d.ocr : '';
      const sr = M.scoreLine(G, raw); sr.ms = d ? d.ms : 0;
      C.rows.raw.push(sr); V.raw.push(sr); LG.push(sr);
      const su = M.scoreLine(G, d ? fuse(d.tokens, d.hyphens, 'union') : ''); C.rows.union.push(su); V.union.push(su);
      C.rows.geo.push(M.scoreLine(G, d ? fuse(d.tokens, d.hyphens, 'geo') : ''));
      if (!d) return;
      // geometric hyphen / extender detection vs GT syllable gaps
      const sy = G.syllables;
      const hc = d.hyphens.map(([a, b]) => (a + b) / 2), ec = d.extenders;
      const usedH = new Set(), usedE = new Set();
      for (let k = 0; k < sy.length; k++) {
        const gx0 = sy[k].x1, gx1 = k + 1 < sy.length ? sy[k + 1].x0 : sy[k].x1 + 3 * G.size_px;
        const hi = hc.findIndex((c, i) => !usedH.has(i) && c > gx0 - 2 && c < gx1 + 2);
        if (sy[k].hyph_printed) { if (hi >= 0) { C.geoHy.tp++; usedH.add(hi); } else C.geoHy.fn++; }
        const ei = ec.findIndex(([a, b], i) => !usedE.has(i) && Math.min(b, gx1) - Math.max(a, gx0) > 0.3 * (b - a));
        if (sy[k].ext_printed) { if (ei >= 0) { C.geoExt.tp++; usedE.add(ei); } else C.geoExt.fn++; }
      }
      C.geoHy.fp += hc.length - usedH.size; C.geoExt.fp += ec.length - usedE.size;
      // hyphens before the first syllable (leading) count as tp if GT has lead_hyphen
      if (G.lead_hyphen) { const i = hc.findIndex((c, i) => !usedH.has(i) && c < sy[0].x0); if (i >= 0) { C.geoHy.fp--; C.geoHy.tp++; } else C.geoHy.fn++; }
    });
  }
}
const res = {};
for (const [cfg, C] of Object.entries(out)) {
  const pr = (o) => ({ P: o.tp / Math.max(1, o.tp + o.fp), R: o.tp / Math.max(1, o.tp + o.fn), tp: o.tp, fp: o.fp, fn: o.fn });
  const se = C.sizeErr.sort((a, b) => a - b);
  res[cfg] = {
    pages: C.pages, det: { ...C.det, recall: C.det.found / C.det.gt, precision: (C.det.dets - C.det.fp - C.det.dup) / Math.max(1, C.det.dets) },
    sizeRelErrMedian: se[Math.floor(se.length / 2)], sizeRelErrP90: se[Math.floor(se.length * 0.9)],
    detMsPerPage: C.detMs / C.pages, ocrMsPerPage: C.ocrMs / C.pages,
    raw: M.aggregate(C.rows.raw), union: M.aggregate(C.rows.union), geo: M.aggregate(C.rows.geo),
    geoHyphen: pr(C.geoHy), geoExtender: pr(C.geoExt),
    byLang: Object.fromEntries(Object.entries(C.byLang).map(([k, a]) => [k, M.aggregate(a)])),
    byVariant: Object.fromEntries(Object.entries(C.byVariant).map(([k, V]) => [k, { recall: V.found / V.gt, fp: V.fp, raw: M.aggregate(V.raw), union: M.aggregate(V.union) }])),
  };
}
process.stdout.write(JSON.stringify(res, null, 1));
