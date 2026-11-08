'use strict';
// Enumerate lyric-line jobs from GT files, and build the oracle crops used by every OCR engine.
const fs = require('fs'), path = require('path');
const IMG = require('./img');
const DATA = path.join(__dirname, '..', 'data');
const VARIANTS = ['clean300', 'scan300', 'bilevel300', 'copy200', 'phone150'];

function listJobs(variants = VARIANTS) {
  const jobs = [];
  for (const v of variants) {
    const dir = path.join(DATA, v);
    for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.gt.json')).sort()) {
      const gt = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
      gt.lines.forEach((L, i) => jobs.push({ key: `${v}/${f.replace('.gt.json', '')}/${i}`, variant: v, png: path.join(dir, f.replace('.gt.json', '.png')), lang: gt.lang, layout: gt.layout, line: L, lineIdx: i }));
    }
  }
  return jobs;
}

/** Oracle crop: GT ink bbox padded; prep: raw | norm | clean. targetPx = desired font size in px (≈ 1.4 x cap height). */
function oracleCrop(page, L, prep = 'norm', targetPx = 40) {
  const s = L.size_px;
  const [x0, y0, x1, y1] = L.bbox;
  const padX = 0.8 * s, padY = 0.35 * s;
  let c = IMG.crop(page, x0 - padX, y0 - padY, x1 + padX, y1 + padY);
  const cx0 = c.x0, cy0 = c.y0;
  if (prep === 'clean' || prep === 'cleancompress') {
    // whiten everything outside the tight ink bbox (+margin): removes noteheads/stems above/below the text band
    const m = Math.max(2, 0.1 * s);
    const tx0 = x0 - cx0 - m, tx1 = x1 - cx0 + m, ty0 = y0 - cy0 - m, ty1 = y1 - cy0 + m;
    for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) if (y < ty0 || y >= ty1 || x < tx0 || x >= tx1) c.data[y * c.width + x] = 255;
  }
  let scale = 1;
  if (prep !== 'raw') { scale = targetPx / s; if (Math.abs(scale - 1) > 0.08) c = IMG.resize(c, scale); }
  c.scale = scale; c.ox = cx0; c.oy = cy0;
  if (/compress/.test(prep)) {
    const band = [Math.max(0, Math.round((y0 - cy0) * scale)), Math.round((y1 - cy0) * scale)];
    c = compressGaps(c, (prep === 'compress2' ? 0.35 : 0.5) * (prep === 'raw' ? s : targetPx), band);
  }
  return c;
}

/** Shrink every all-white column run wider than G px down to G px (lyric syllables are spread under notes;
 *  closing the gaps makes the strip look like ordinary typeset text). Keeps xmap: new x -> old x. */
function compressGaps(c, G, band) {
  const { width: w, height: h, data } = c;
  const t = Math.min(200, IMG.otsu(c));
  const [b0, b1] = band || [0, h];
  const ink = new Uint8Array(w);
  for (let x = 0; x < w; x++) { let n = 0; for (let y = b0; y < Math.min(h, b1); y++) if (data[y * w + x] <= t) n++; ink[x] = n > 0 ? 1 : 0; }
  const cols = [];
  let x = 0;
  while (x < w) {
    if (ink[x]) { cols.push(x); x++; continue; }
    let e = x; while (e < w && !ink[e]) e++;
    const run = e - x, keep = Math.min(run, Math.round(G));
    const st = x + Math.floor((run - keep) / 2);
    for (let k = 0; k < keep; k++) cols.push(st + k);
    x = e;
  }
  const W = cols.length, out = new Uint8ClampedArray(W * h);
  for (let y = 0; y < h; y++) for (let i = 0; i < W; i++) out[y * W + i] = data[y * w + cols[i]];
  return { width: W, height: h, data: out, scale: c.scale, ox: c.ox, oy: c.oy, xmap: cols };
}

const pageCache = new Map();
function loadPage(p) {
  if (!pageCache.has(p)) { if (pageCache.size > 8) pageCache.clear(); pageCache.set(p, IMG.readGray(p)); }
  return pageCache.get(p);
}
module.exports = { listJobs, oracleCrop, loadPage, compressGaps, VARIANTS, DATA };
