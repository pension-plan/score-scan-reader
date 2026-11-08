'use strict';
// Heads the blob finder misses on degraded pages (faded heads broken into speckle, hollow heads
// whose thin outline breaks open): the filled and half head templates are matched at every staff
// position along a staff, on the lenient staff-removed binary, where there is head-sized ink and
// no head was found. A match must beat the templates of the glyphs that also sit on staff
// positions (accidentals, rests, digits). front.js runs it on staves whose head count looks short.
const { makeJsApi } = require('../../../mvp/src/cv');

let api0 = null;
const OTHERS = ['acc-sharp', 'acc-flat', 'acc-natural', 'rest-quarter', 'rest-8th', 'digit-4', 'dot'];

function crop(L, x0, y0, x1, y1) {
  x0 = Math.max(0, Math.round(x0)); y0 = Math.max(0, Math.round(y0)); x1 = Math.min(L.width - 1, Math.round(x1)); y1 = Math.min(L.height - 1, Math.round(y1));
  const w = x1 - x0 + 1, h = y1 - y0 + 1;
  if (w < 3 || h < 3) return null;
  const data = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) data.set(L.data.subarray((y + y0) * L.width + x0, (y + y0) * L.width + x0 + w), y * w);
  return { w, h, data };
}

// speckle joined: a closing (two dilations, one erosion, 3x3) of the binary, once per page
const closedOf = new WeakMap();
function closed(L) {
  let c = closedOf.get(L);
  if (c) return c;
  const { width: w, height: h } = L;
  const step = (src, grow) => { const o = new Uint8Array(w * h); for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { let v = grow ? 0 : 1; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const yy = y + dy, xx = x + dx; const s = yy >= 0 && yy < h && xx >= 0 && xx < w ? src[yy * w + xx] : 0; if (grow ? s : !s) v = grow ? 1 : 0; } o[y * w + x] = v; } return o; };
  const d = step(step(L.data, true), true), e = step(d, false);
  c = { width: w, height: h, data: e };
  closedOf.set(L, c);
  return c;
}

function scanHeads(L0, st, heads, opts = {}) {
  const api = api0 ||= makeJsApi();
  const L = opts.close === false ? L0 : closed(L0);
  const sp = st.space, W = L.width;
  const minScore = opts.minScore ?? 0.5;
  const found = [];
  const taken = (x, p) => heads.concat(found).some(h => h.staff === st.index && Math.abs(h.x - x) < 1.0 * sp && Math.abs(h.p - p) <= 1);
  for (let x = st.left + 4 * sp; x < st.right - 0.6 * sp; x += 0.5 * sp) {
    for (let p = -7; p <= 7; p++) {
      const y = st.yAt(2, x) - (p * sp) / 2;
      // head-sized ink here (a third of a head's box at least)
      let ink = 0, tot = 0;
      for (let yy = Math.round(y - 0.4 * sp); yy <= Math.round(y + 0.4 * sp); yy++) for (let xx = Math.round(x - 0.55 * sp); xx <= Math.round(x + 0.55 * sp); xx++) {
        if (yy < 0 || yy >= L.height || xx < 0 || xx >= W) continue; tot++; ink += L.data[yy * W + xx];
      }
      if (!tot || ink / tot < 0.3 || taken(x, p)) continue;
      const img = crop(L, x - 0.8 * sp, y - 0.65 * sp, x + 0.8 * sp, y + 0.65 * sp);
      if (!img) continue;
      const sc = api.scores(img, sp, ['head-filled', 'head-half']);
      const k = sc['head-filled'] >= sc['head-half'] ? 'head-filled' : 'head-half';
      if (sc[k] < minScore) continue;
      const so = api.scores(img, sp, OTHERS), o = Math.max(...OTHERS.map(n => so[n]));
      if (sc[k] < o + 0.05) continue;
      found.push({ x, y, staff: st.index, p, sp, kind: k === 'head-half' ? 'hollow' : 'filled', score: sc[k], w: 1.2 * sp, blob: -1, x0: Math.round(x - 0.6 * sp), x1: Math.round(x + 0.6 * sp), scanned: true });
    }
  }
  // one head per place: the best of neighbours a half space apart
  const out = [];
  for (const h of found.sort((a, b) => b.score - a.score)) if (!out.some(o => Math.abs(o.x - h.x) < 0.9 * sp && Math.abs(o.p - h.p) <= 1)) out.push(h);
  return out;
}

module.exports = { scanHeads };
