#!/usr/bin/env node
'use strict';
// Build ground truth JSON from a colour-coded LilyPond render (see scores/omrtruth.ily).
// usage: node tools/truth.js <truth.ppm> <truth-log.txt> <out.json> [clean.pgm]
// Geometry conventions (so tools/degrade.py can transform them generically):
//   c: [x,y] point, bb: [x0,y0,x1,y1] box, p0/p1: endpoints, pts: polyline.
const fs = require('fs');
const path = require('path');
const { readRGB, readGray } = require('../src/image');

const CLASS_NAMES = {
  10: 'staff', 20: 'ledger', 30: 'barline', 31: 'spanbar', 40: 'stemUp', 41: 'stemDown', 42: 'stem',
  50: 'headFilled', 51: 'headHalf', 52: 'headWhole', 53: 'headBreve', 60: 'rest', 70: 'beam', 71: 'flag',
  80: 'accidental', 81: 'key', 82: 'clef', 83: 'time', 84: 'keycancel', 90: 'dots', 91: 'tie', 92: 'slur',
  100: 'lyric', 101: 'hyphen', 102: 'extender', 103: 'stanza', 110: 'dynamic', 111: 'text', 112: 'tempo',
  120: 'systemStart', 121: 'other',
};

function parseLog(file) {
  const recs = new Map();
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    if (!line) continue;
    const f = line.split('\t');
    const id = +f[1];
    if (f[0] === 'head') {
      const [nn, alt, oct] = f[8].split(':');
      recs.set(id, { type: 'head', cls: +f[2], voice: f[3], durLog: +f[4], dots: +f[5], staffPos: +f[6], stemDir: +f[7],
        pitch: f[8] === '-' ? null : { step: 'CDEFGAB'[+nn], alter: evalFrac(alt) * 2, octave: +oct + 4 } });
    } else if (f[0] === 'stem') recs.set(id, { type: 'stem', cls: +f[2], dir: +f[3] });
    else if (f[0] === 'bar') recs.set(id, { type: 'bar', glyph: f[3] });
    else if (f[0] === 'lyric') recs.set(id, { type: 'lyric', text: f[3] });
    else recs.set(id, { type: f[3] || 'obj', cls: +f[2] });
  }
  return recs;
}
function evalFrac(s) { if (!s) return 0; if (s.includes('/')) { const [a, b] = s.split('/'); return +a / +b; } return +s; }

function build(truthPPM, logFile, cleanPGM) {
  const img = readRGB(truthPPM);
  const { width: W, height: H, data } = img;
  const log = parseLog(logFile);
  const objs = new Map(); // key cls*65536+id -> stats
  const staffMask = new Uint8Array(W * H);
  const ledgerMask = new Uint8Array(W * H);
  const sysMask = new Uint8Array(W * H);
  for (let y = 0, i = 0; y < H; y++) {
    for (let x = 0; x < W; x++, i++) {
      const r = data[i * 3], g = data[i * 3 + 1], b = data[i * 3 + 2];
      if (r === 255 && g === 255 && b === 255) continue;
      if (r === 0) continue; // black = un-instrumented (titles, bar numbers)
      if (r === 10) { staffMask[i] = 1; continue; }
      if (r === 20) ledgerMask[i] = 1;
      if (r === 120 || r === 31) sysMask[i] = 1;
      const key = r * 65536 + g * 256 + b;
      let o = objs.get(key);
      if (!o) { o = { cls: r, id: g * 256 + b, n: 0, x0: x, y0: y, x1: x, y1: y, sx: 0, sy: 0 }; objs.set(key, o); }
      o.n++; o.sx += x; o.sy += y;
      if (x < o.x0) o.x0 = x; if (x > o.x1) o.x1 = x; if (y < o.y0) o.y0 = y; if (y > o.y1) o.y1 = y;
    }
  }
  // ---- staff lines from staffMask: horizontal projection -> line clusters
  const proj = new Float64Array(H);
  for (let y = 0; y < H; y++) { let s = 0; for (let x = 0; x < W; x++) s += staffMask[y * W + x]; proj[y] = s; }
  const lines = [];
  for (let y = 0; y < H; y++) {
    if (proj[y] < W * 0.05) continue;
    let y1 = y; let sw = 0, swy = 0;
    while (y1 < H && proj[y1] >= W * 0.05) { sw += proj[y1]; swy += proj[y1] * y1; y1++; }
    // x extent
    const mid = Math.round(swy / sw);
    let x0 = W, x1 = -1;
    for (let x = 0; x < W; x++) if (staffMask[mid * W + x]) { if (x < x0) x0 = x; x1 = x; }
    lines.push({ y: swy / sw, thick: sw / (x1 - x0 + 1), x0, x1 });
    y = y1;
  }
  const staves = [];
  for (let i = 0; i + 4 < lines.length;) {
    const g = lines.slice(i, i + 5);
    const gaps = g.slice(1).map((l, k) => l.y - g[k].y);
    const mg = gaps.reduce((a, b) => a + b) / 4;
    if (Math.max(...gaps) - Math.min(...gaps) < 0.15 * mg) {
      const x0 = Math.min(...g.map(l => l.x0)), x1 = Math.max(...g.map(l => l.x1));
      const step = 40;
      staves.push({
        space: mg, thickness: g.reduce((a, l) => a + l.thick, 0) / 5,
        lines: g.map(l => { const pts = []; for (let x = x0; x < x1; x += step) pts.push([x, l.y]); pts.push([x1, l.y]); return { pts }; }),
      });
      i += 5;
    } else i++;
  }
  // assign system index: staves connected by systemStart objects (class 120) or same y-band
  const ss = staves.length ? staves.reduce((a, s) => a + s.space, 0) / staves.length : 0;
  const thick = staves.length ? staves.reduce((a, s) => a + s.thickness, 0) / staves.length : 0;
  const yMid = s => s.lines[2].pts[0][1];
  // staves k-1 and k are in one system if some column of system-start/span-bar
  // pixels (class 120/31) covers >= 90% of the gap between them
  let sys = -1;
  staves.forEach((s, k) => {
    let linked = false;
    if (k > 0) {
      const ya = Math.ceil(staves[k - 1].lines[4].pts[0][1]), yb = Math.floor(s.lines[0].pts[0][1]);
      for (let x = 0; x < W && !linked; x++) {
        let n = 0;
        for (let y = ya; y <= yb; y++) n += sysMask[y * W + x];
        if (n >= 0.9 * (yb - ya + 1)) linked = true;
      }
    }
    if (!linked) sys++;
    s.system = sys; s.index = k;
  });
  const nearestStaff = (y) => { let best = -1, bd = 1e9; staves.forEach((s, k) => { const d = Math.abs(yMid(s) - y); if (d < bd) { bd = d; best = k; } }); return best; };

  const heads = [], stems = [], barlines = [], others = [];
  for (const o of objs.values()) {
    const rec = log.get(o.id) || {};
    const bb = [o.x0, o.y0, o.x1 + 1, o.y1 + 1];
    const c = [(o.x0 + o.x1 + 1) / 2, (o.y0 + o.y1 + 1) / 2];
    if (o.cls >= 50 && o.cls <= 53) {
      heads.push({ id: o.id, kind: o.cls === 50 ? 'filled' : (o.cls === 51 ? 'half' : (o.cls === 52 ? 'whole' : 'breve')),
        c, bb, n: o.n, voice: rec.voice, durLog: rec.durLog, dots: rec.dots, staffPos: rec.staffPos,
        stemDir: rec.stemDir, pitch: rec.pitch, staff: nearestStaff(c[1]) });
    } else if (o.cls >= 40 && o.cls <= 42) {
      stems.push({ id: o.id, dir: o.cls === 40 ? 1 : (o.cls === 41 ? -1 : 0), p0: [c[0], o.y0], p1: [c[0], o.y1 + 1], width: o.x1 - o.x0 + 1 });
    } else if (o.cls === 30) {
      // which staff: barline spans a staff vertically
      const st = nearestStaff(c[1]);
      barlines.push({ id: o.id, glyph: rec.glyph, p0: [c[0], o.y0], p1: [c[0], o.y1 + 1], bb, width: o.x1 - o.x0 + 1, staff: st });
    } else {
      const extra = rec.type === 'lyric' ? { text: rec.text } : {};
      others.push({ id: o.id, cls: o.cls, type: CLASS_NAMES[o.cls] || String(o.cls), bb, c, n: o.n, ...extra });
    }
  }
  // merge visually coincident heads (unisons shared by two voices)
  heads.sort((a, b) => a.c[0] - b.c[0]);
  const merged = [];
  for (const h of heads) {
    const m = merged.find(g => Math.abs(g.c[0] - h.c[0]) < 0.3 * ss && Math.abs(g.c[1] - h.c[1]) < 0.3 * ss);
    if (m) { m.voices.push(h.voice); m.stemDirs.push(h.stemDir); m.ids.push(h.id); if (h.kind !== 'filled') m.kind = m.kind === 'filled' ? h.kind : m.kind; }
    else merged.push({ ...h, voices: [h.voice], stemDirs: [h.stemDir], ids: [h.id] });
  }
  // heads completely hidden under another head (unison shared by two voices):
  // attach to the visible head with the same pitch/staff-position and nearest id
  const visibleIds = new Set(heads.map(h => h.id));
  let hidden = 0;
  for (const [id, r] of log) {
    if (r.type !== 'head' || visibleIds.has(id)) continue;
    let best = null, bd = 1e9;
    for (const m of merged) {
      if (m.staffPos !== r.staffPos || !m.pitch || !r.pitch || m.pitch.step !== r.pitch.step || m.pitch.octave !== r.pitch.octave) continue;
      const d = Math.min(...m.ids.map(v => Math.abs(v - id)));
      if (d < bd) { bd = d; best = m; }
    }
    if (best && bd < 40) { best.voices.push(r.voice); best.stemDirs.push(r.stemDir); best.ids.push(id); best.hiddenUnison = true; hidden++; }
  }
  const loggedHeads = [...log.values()].filter(r => r.type === 'head').length;

  let layoutCheck = null;
  if (cleanPGM) {
    // sanity: clean render and truth render must have identical layout
    const g = readGray(cleanPGM);
    let inter = 0, uni = 0;
    for (let i = 0; i < W * H; i++) {
      const a = g.data[i] < 128;
      const b = !(data[i * 3] === 255 && data[i * 3 + 1] === 255 && data[i * 3 + 2] === 255);
      if (a && b) inter++; if (a || b) uni++;
    }
    layoutCheck = { iou: inter / uni };
  }
  return {
    meta: { source: path.basename(truthPPM), width: W, height: H, staffSpace: ss, lineThickness: thick,
      loggedHeads, visibleHeads: heads.length, hiddenUnisonHeads: hidden, layoutCheck, transform: { rotDeg: 0 } },
    staves, heads: merged, stems, barlines, others,
  };
}

if (require.main === module) {
  const [ppm, logf, out, clean] = process.argv.slice(2);
  const t = build(ppm, logf, clean);
  fs.writeFileSync(out, JSON.stringify(t));
  const m = t.meta;
  console.log(`${path.basename(out)}: ${t.staves.length} staves, ss=${m.staffSpace.toFixed(2)} lt=${m.lineThickness.toFixed(2)}, heads ${t.heads.length} (visible grobs ${m.visibleHeads}/${m.loggedHeads}), stems ${t.stems.length}, barlines ${t.barlines.length}` + (m.layoutCheck ? `, layout IoU ${m.layoutCheck.iou.toFixed(4)}` : ''));
}
module.exports = { build, parseLog };
