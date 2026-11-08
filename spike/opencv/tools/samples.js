// Labelled samples from data/patches/*.jsonl (shared by the experiments).
'use strict';
const fs = require('fs'), path = require('path');
const DIR = path.join(__dirname, '../data/patches');

const FAMILY = (lab) => lab.startsWith('rest') ? 'rests' : lab.startsWith('acc') ? 'accidentals' : lab.startsWith('clef') ? 'clefs'
  : lab.startsWith('digit') || lab.startsWith('time-') ? 'time' : lab === 'fermata' ? 'fermata' : lab === 'dyn' ? 'dynamics' : lab === 'dot' ? 'dots' : 'neg';

function decode(p) { const b = Buffer.from(p.data, 'base64'); return { w: p.w, h: p.h, data: new Uint8Array(b.buffer, b.byteOffset, b.length) }; }

// item-level fold (0/1) from a string hash: items never straddle train and test
function fold(key) { let h = 2166136261; for (const c of key) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return (h >>> 0) % 2; }

function splitTime(o, img) {
  // time-signature patch -> C / cut whole, or the top and bottom numbers cut at the middle line
  const m = /\((\d+) \. (\d+)\)/.exec(o.attrs.frac || '');
  if (!m) return [];
  const style = o.attrs.style || '';
  if (style !== 'numbered' && style !== 'single-digit' && (m[0] === '(4 . 4)' || m[0] === '(2 . 2)')) return [{ lab: m[1] === '4' ? 'time-C' : 'time-cut', img, vtop: o.vtop, vbot: o.vbot }];
  const yMid = Math.round(-o.vtop * o.sp); // middle-line row inside the patch
  if (yMid <= 2 || yMid >= img.h - 2) return [];
  const cut = (y0, y1) => { const h = y1 - y0, d = img.data.slice(y0 * img.w, y1 * img.w); return { w: img.w, h, data: d }; };
  const trim = (im) => { // trim empty rows/cols
    let x0 = im.w, x1 = -1, y0 = im.h, y1 = -1;
    for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) if (im.data[y * im.w + x]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    if (x1 < 0) return null;
    const w = x1 - x0 + 1, h = y1 - y0 + 1, d = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) d[y * w + x] = im.data[(y + y0) * im.w + x + x0];
    return { im: { w, h, data: d }, y0, y1 };
  };
  const out = [];
  for (const [num, y0, y1, base] of [[m[1], 0, yMid, 0], [m[2], yMid, img.h, yMid]]) {
    const t = trim(cut(y0, y1)); if (!t) continue;
    const lab = num.length === 1 ? 'digit-' + num : 'digits-' + num;
    out.push({ lab, img: t.im, vtop: o.vtop + (base + t.y0) / o.sp, vbot: o.vtop + (base + t.y1) / o.sp });
  }
  return out;
}

function load({ maxNeg = 4000 } = {}) {
  const S = [];
  let nNeg = 0;
  for (const f of fs.readdirSync(DIR).filter(f => f.endsWith('.jsonl')).sort()) {
    for (const line of fs.readFileSync(path.join(DIR, f), 'utf8').split('\n')) {
      if (!line) continue;
      const o = JSON.parse(line);
      if (/^flag/.test(o.lab)) continue; // flags are attached to stems: not a glyph-patch problem
      const img = decode(o.patch);
      const base = { key: o.key, fold: fold(o.key), variant: o.variant, sp: o.sp, box: o.box, ncomp: o.ncomp };
      if (o.lab === 'time') { for (const t of splitTime(o, img)) S.push({ ...base, ...t }); continue; }
      let lab = o.lab;
      if (lab === 'rest-multi') lab = (img.w / o.sp) < 2.2 ? 'rest-whole' : 'rest-hbar';
      if (lab === 'neg-other' && nNeg++ >= maxNeg) continue;
      S.push({ ...base, lab, img, vtop: o.vtop, vbot: o.vbot });
    }
  }
  for (const s of S) s.family = FAMILY(s.lab);
  return S;
}

module.exports = { load, FAMILY, fold };
