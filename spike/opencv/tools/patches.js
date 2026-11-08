// Labelled glyph patches for one coverage item: LilyPond truth boxes -> components of the
// pipeline's own staff-removed page R (front() of the src snapshot), for clean / scan / scan-severe.
//   node patches.js <family>__<id>   -> data/patches/<key>.jsonl
// clean: truth boxes are mapped by the raster scale (300 dpi vector page -> 200 dpi cache -> front scale).
// scans: each box is carried over by its staff (index, fraction along the staff, offset from the
// middle line in staff spaces), so skew / scale / small warps of the scan are followed. A patch is the
// union of R components whose centre falls inside the mapped box (+ margin); boxes with no
// component are reported as lost.
'use strict';
const fs = require('fs'), path = require('path');
const SRC = path.join(__dirname, '../src-snap');
const { readGray } = require(path.join(SRC, 'image.js'));
const { front } = require(path.join(SRC, 'front.js'));
const { labelComponents } = require(path.join(SRC, 'cc.js'));
const CACHE = path.join(__dirname, '../../../mvp/work/cache');
const key = process.argv[2];
const boxes = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/boxes', key + '.json'), 'utf8'));

// truth symbol -> class label (null = not a target; 'neg-*' = negatives kept for the classifier)
function label(s) {
  const a = s.attrs || {};
  switch (s.cls) {
    case 'Rest': return { '-1': 'rest-breve', 0: 'rest-whole', 1: 'rest-half', 2: 'rest-quarter', 3: 'rest-8th', 4: 'rest-16th', 5: 'rest-32nd', 6: 'rest-64th' }[a.dlog] || null;
    case 'MultiMeasureRest': return 'rest-multi';
    case 'Accidental': case 'AccidentalCautionary': {
      const g = (a.glyph || '').replace('accidentals.', '');
      return { sharp: 'acc-sharp', flat: 'acc-flat', natural: 'acc-natural', doublesharp: 'acc-double-sharp', flatflat: 'acc-double-flat' }[g] || null;
    }
    case 'Clef': { const g = (a.glyph2 || a.glyph || ''); return /clefs\.G/.test(g) ? 'clef-G' : /clefs\.F/.test(g) ? 'clef-F' : /clefs\.C/.test(g) ? 'clef-C' : null; }
    case 'TimeSignature': return 'time';
    case 'Script': return /fermata/.test(a.script || '') ? 'fermata' : 'neg-script';
    case 'DynamicText': return 'dyn';
    case 'Dots': return 'dot';
    case 'NoteHead': return 'neg-head';
    case 'Flag': return 'flag-' + ({ 3: '8th', 4: '16th', 5: '32nd', 6: '64th' }[a.dlog] || 'x');
    default: return null;
  }
}

function staffOf(staves, x, y) {
  let best = null, bd = Infinity;
  for (const st of staves) {
    if (x < st.left - 6 * st.space || x > st.right + 2 * st.space) continue;
    const ym = st.yAt(2, Math.min(st.right, Math.max(st.left, x)));
    const d = Math.abs(y - ym);
    if (d < bd && d < 7 * st.space) { bd = d; best = st; }
  }
  return best;
}
const rel = (st, x, y) => { const xc = Math.min(st.right, Math.max(st.left, x)); return { u: (x - st.left) / (st.right - st.left), v: (y - st.yAt(2, xc)) / st.space }; };
const absP = (st, r) => { const x = st.left + r.u * (st.right - st.left); const xc = Math.min(st.right, Math.max(st.left, x)); return { x, y: st.yAt(2, xc) + r.v * st.space }; };

function cropComps(R, labels, ids, b) {
  const w = b.x1 - b.x0 + 1, h = b.y1 - b.y0 + 1, out = new Uint8Array(w * h), set = new Set(ids);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = (b.y0 + y) * R.width + b.x0 + x; if (set.has(labels[i])) out[y * w + x] = 1; }
  return { w, h, data: Buffer.from(out).toString('base64') };
}

function pageGray(variant, p) {
  const dir = path.join(CACHE, `coverage__${key}__${variant}__r200`);
  const f = path.join(dir, `p-${p + 1}.pgm`);
  return fs.existsSync(f) ? readGray(f) : null;
}

const lines = [], stats = {};
const bump = (k) => { stats[k] = (stats[k] || 0) + 1; };
for (let p = 0; p < boxes.pages.length; p++) {
  const g0 = pageGray('clean', p);
  if (!g0) { bump('no-clean-raster'); continue; }
  const fr0 = front(g0, { orient: false });
  if (!fr0.staves.length || Math.abs(fr0.skew.angle || 0) >= 0.05) { bump('clean-unusable'); continue; }
  const k0 = (200 / 300) * fr0.scale;
  // truth symbols in the clean front frame, with their staff-relative position
  const syms = [];
  for (const s of boxes.pages[p].symbols) {
    const lab = label(s); if (!lab) continue;
    const b = s.box.map(v => v * k0);
    const cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2, st = staffOf(fr0.staves, cx, cy);
    if (!st) { bump('no-staff'); continue; }
    syms.push({ lab, attrs: s.attrs, b, st: st.index, r0: rel(st, b[0], b[1]), r1: rel(st, b[2], b[3]) });
  }
  // all tagged boxes (for negatives: components touching no tagged box at all)
  const allB = boxes.pages[p].symbols.map(s => s.box.map(v => v * k0));
  for (const variant of ['clean', 'scan', 'scan-severe']) {
    const g = variant === 'clean' ? g0 : pageGray(variant, p);
    if (!g) { bump(variant + ':no-raster'); continue; }
    const fr = variant === 'clean' ? fr0 : front(g, { orient: false });
    if (fr.staves.length !== fr0.staves.length) { bump(variant + ':staff-count-mismatch'); continue; }
    const { labels, comps } = labelComponents(fr.R);
    const cs = comps.filter(c => c.area >= 3);
    const grid = new Map(); // coarse bucket index on centre
    const G = 64;
    for (const c of cs) { c.cx = (c.x0 + c.x1) / 2; c.cy = (c.y0 + c.y1) / 2; const k = ((c.cy / G) | 0) * 100000 + ((c.cx / G) | 0); if (!grid.has(k)) grid.set(k, []); grid.get(k).push(c); }
    const inBox = (b) => { const out = []; for (let gy = (b[1] / G) | 0; gy <= (b[3] / G) | 0; gy++) for (let gx = (b[0] / G) | 0; gx <= (b[2] / G) | 0; gx++) for (const c of grid.get(gy * 100000 + gx) || []) if (c.cx >= b[0] && c.cx <= b[2] && c.cy >= b[1] && c.cy <= b[3]) out.push(c); return out; };
    const used = new Set();
    for (const s of syms) {
      const st = fr.staves[s.st], sp = st.space;
      const a = absP(st, s.r0), z = absP(st, s.r1), m = (variant === 'clean' ? 0.15 : 0.35) * sp;
      const mb = [a.x - m, a.y - m, z.x + m, z.y + m];
      const own = inBox(mb);
      if (!own.length) { bump(variant + ':lost:' + s.lab); continue; }
      const b = { x0: Math.min(...own.map(c => c.x0)), y0: Math.min(...own.map(c => c.y0)), x1: Math.max(...own.map(c => c.x1)), y1: Math.max(...own.map(c => c.y1)) };
      own.forEach(c => used.add(c.id));
      const ym = st.yAt(2, Math.min(st.right, Math.max(st.left, (b.x0 + b.x1) / 2)));
      lines.push(JSON.stringify({ key, page: p, variant, lab: s.lab, attrs: s.attrs, sp: +sp.toFixed(3), box: b, ncomp: own.length,
        vtop: +((b.y0 - ym) / sp).toFixed(3), vbot: +((b.y1 - ym) / sp).toFixed(3), patch: cropComps(fr.R, labels, own.map(c => c.id), b) }));
      bump(variant + ':ok:' + s.lab);
    }
    // negatives: components near a staff that touch no tagged box (clean frame boxes mapped like symbols)
    if (variant === 'clean') {
      let n = 0;
      for (const c of cs) {
        if (n >= 80 || used.has(c.id) || c.area < 10) continue;
        const st = staffOf(fr.staves, c.cx, c.cy); if (!st) continue;
        const sp = st.space, w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
        if (w > 8 * sp || h > 9 * sp || (w < 0.25 * sp && h < 0.25 * sp)) continue;
        if (allB.some(b => c.cx >= b[0] - 2 && c.cx <= b[2] + 2 && c.cy >= b[1] - 2 && c.cy <= b[3] + 2)) continue;
        const ym = st.yAt(2, Math.min(st.right, Math.max(st.left, c.cx)));
        lines.push(JSON.stringify({ key, page: p, variant, lab: 'neg-other', attrs: {}, sp: +sp.toFixed(3), box: { x0: c.x0, y0: c.y0, x1: c.x1, y1: c.y1 }, ncomp: 1,
          vtop: +((c.y0 - ym) / sp).toFixed(3), vbot: +((c.y1 - ym) / sp).toFixed(3), patch: cropComps(fr.R, labels, [c.id], c) }));
        n++;
      }
    }
  }
}
fs.writeFileSync(path.join(__dirname, '../data/patches', key + '.jsonl'), lines.join('\n') + '\n');
console.log(key, JSON.stringify(stats));
