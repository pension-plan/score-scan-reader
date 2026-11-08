// Classical baseline on the same truth glyphs as the OpenCV experiments: what the current pipeline
// (src snapshot) reads for each labelled patch of one item.
//   node classical.js <family>__<id>  -> data/classical/<key>.jsonl  ({variant, page, box, lab, pred})
// rests: detectRests over each whole staff (after assemblePage, so heads and header are known),
//        matched by centre; detections matching no truth rest are written as lab 'none' (false positives)
// accidentals: the pipeline's accidental classifier on the patch's components (any glyph 1-4 spaces
//        tall is tried, so non-accidentals give false positives)
// clefs: the staff header clef (start of staff) or a clef change box
// time: header time signature; digits are never read (only C / cut set beats)
'use strict';
const fs = require('fs'), path = require('path');
const SRC = process.env.SRC || path.join(__dirname, '../src-snap');
const { readGray } = require(path.join(SRC, 'image.js'));
const { front } = require(path.join(SRC, 'front.js'));
const { assemblePage, _classifyAccidental } = require(path.join(SRC, 'assemble.js'));
const { detectRests } = require(path.join(SRC, 'rests.js'));
const CACHE = path.join(__dirname, '../../../mvp/work/cache');
const key = process.argv[2];
const P = fs.readFileSync(path.join(__dirname, '../data/patches', key + '.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
const out = [];
const KIND = { whole: 'rest-whole', half: 'rest-half', breve: 'rest-breve', long: 'rest-long', quarter: 'rest-quarter', flag1: 'rest-8th', flag2: 'rest-16th', flag3: 'rest-32nd', flag4: 'rest-64th', multi: 'rest-hbar' };
const pages = [...new Set(P.map(o => o.page))];
for (const variant of ['clean', 'scan', 'scan-severe']) for (const p of pages) {
  const ps = P.filter(o => o.variant === variant && o.page === p);
  if (!ps.length) continue;
  const f = path.join(CACHE, `coverage__${key}__${variant}__r200`, `p-${p + 1}.pgm`);
  if (!fs.existsSync(f)) continue;
  const fr = front(readGray(f), { orient: false });
  let asm; try { asm = assemblePage(fr, p); } catch (e) { continue; }
  const R = fr.R, comps = asm.comps;
  const inside = (b, x, y, m) => x >= b.x0 - m && x <= b.x1 + m && y >= b.y0 - m && y <= b.y1 + m;
  // rests
  const restTruth = ps.filter(o => o.lab.startsWith('rest'));
  const det = [];
  for (const sy of asm.systems) for (const s of sy.staves) {
    try { for (const r of detectRests({ R, comps, s, xa: s.st.left, xb: s.st.right + 1 })) det.push({ r, sp: s.st.space }); } catch (e) { /* skip */ }
  }
  const usedDet = new Set();
  for (const o of restTruth) {
    const m = 0.3 * o.sp;
    const d = det.find(d => !usedDet.has(d) && inside(o.box, (d.r.box.x0 + d.r.box.x1) / 2, (d.r.box.y0 + d.r.box.y1) / 2, m));
    if (d) usedDet.add(d);
    let lab = o.lab; if (lab === 'rest-multi') lab = ((o.box.x1 - o.box.x0 + 1) / o.sp) < 2.2 ? 'rest-whole' : 'rest-hbar';
    out.push({ variant, page: p, fam: 'rests', lab, pred: d ? KIND[d.r.kind] || d.r.kind : 'none' });
  }
  for (const d of det) if (!usedDet.has(d)) out.push({ variant, page: p, fam: 'rests', lab: 'none', pred: KIND[d.r.kind] || d.r.kind });
  // accidentals: every truth patch of plausible size
  for (const o of ps) {
    const h = (o.box.y1 - o.box.y0 + 1) / o.sp;
    if (h < 1.2 || h > 4) continue;
    const parts = comps.filter(c => inside(o.box, (c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2, 0));
    if (!parts.length) continue;
    const g = { x0: o.box.x0, y0: o.box.y0, x1: o.box.x1, y1: o.box.y1, parts };
    let k = null; try { k = _classifyAccidental(R, parts.length === 1 ? parts[0] : g, o.sp); } catch (e) { k = null; }
    out.push({ variant, page: p, fam: 'accidentals', lab: o.lab.startsWith('acc') ? o.lab : 'neg', pred: k ? 'acc-' + k : 'neg' });
  }
  // clefs
  for (const o of ps.filter(o => o.lab.startsWith('clef'))) {
    let pred = 'none';
    for (const sy of asm.systems) for (const s of sy.staves) {
      const st = s.st, cx = (o.box.x0 + o.box.x1) / 2, cy = (o.box.y0 + o.box.y1) / 2;
      if (cy < st.yAt(0, st.left) - 4 * st.space || cy > st.yAt(4, st.left) + 4 * st.space) continue;
      if (cx < st.left + 4 * st.space) { if (!s.hdr.clefGuessed && s.hdr.clef) pred = 'clef-' + s.hdr.clef[0]; }
      else for (const ch of s.changes || []) if (ch.clef && ch.box && inside(ch.box, cx, cy, 0.5 * st.space)) pred = 'clef-' + ch.clef[0];
    }
    out.push({ variant, page: p, fam: 'clefs', lab: o.lab, pred });
  }
  // time signatures (whole glyph): found, and numbers read?
  for (const o of ps.filter(o => o.lab === 'time')) {
    let found = false, read = null;
    for (const sy of asm.systems) for (const s of sy.staves) { const t = s.hdr.time; if (t && t.x1 >= o.box.x0 - 4 && t.x0 <= o.box.x1 + 4 && (o.box.y0 + o.box.y1) / 2 > s.st.yAt(0, t.x0) - 2 * s.st.space && (o.box.y0 + o.box.y1) / 2 < s.st.yAt(4, t.x0) + 2 * s.st.space) { found = true; if (t.beats) read = `${t.beats}/${t.type}`; } }
    const m = /\((\d+) \. (\d+)\)/.exec(o.attrs.frac || '');
    out.push({ variant, page: p, fam: 'time', lab: m ? `${m[1]}/${m[2]}` : '?', style: o.attrs.style || '', found, pred: read });
  }
}
const OUT = process.env.CDIR || path.join(__dirname, '../data/classical'); fs.mkdirSync(OUT, { recursive: true });
fs.writeFileSync(path.join(OUT, key + '.jsonl'), out.map(o => JSON.stringify(o)).join('\n') + '\n');
console.log(key, out.length);
