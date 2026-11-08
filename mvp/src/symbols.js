'use strict';
// Overlay data: where every symbol the pipeline recognised on a page stands,
// and the ink it did not explain. Read-only: it reads the page as front()
// and assemblePage() left it and changes nothing they or buildScore use.
// Boxes are [x0, y0, x1, y1] in the page's deskewed frame (the heads' frame).

const { detectRests } = require('./rests');
const { accidentalGlyph } = require('./assemble');
const { classifyMarks, ROLE_LABEL, _slurLike: slurLike } = require('./text');

const r1 = (v) => Math.round(v * 10) / 10;
const box = (b) => [r1(b.x0), r1(b.y0), r1(b.x1), r1(b.y1)];
// y of staff position k (0 top line .. 4 bottom line, fractions between)
const lineY = (st, k, x) => st.yAt(0, x) + k * (st.yAt(4, x) - st.yAt(0, x)) / 4;

// What the note reader explains (out: the symbol layers) and the leftover
// components that touch none of it (left).
function explain(fr, asm) {
  const out = { clefs: [], keys: [], times: [], rests: [], accs: [], dots: [], stems: [], beams: [], tuplets: [], bars: [], unknown: [] };
  const left = [];
  if (!fr || !fr.R || !asm) return { out, left };
  const R = fr.R, comps = asm.comps || [], ss = fr.ss;
  const known = []; // boxes that explain ink
  const add = (b, pad = 0) => known.push([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad]);
  const dotOf = (h, sp, st) => {
    // the augmentation dot's blob right of a dotted head (dotBlob's window)
    let best = null, bd = Infinity;
    for (const c of comps) {
      const w = c.x1 - c.x0 + 1, hh = c.y1 - c.y0 + 1;
      if (c.x0 < h.x + 0.5 * sp || c.x0 > h.x + 2.0 * sp || w < 0.15 * sp || w > 0.8 * sp || hh < 0.15 * sp || hh > 0.8 * sp) continue;
      const cy = (c.y0 + c.y1) / 2;
      if (Math.abs(cy - h.y) > 0.9 * sp) continue;
      const d = c.x0 - h.x + Math.abs(cy - h.y);
      if (d < bd) { bd = d; best = c; }
    }
    return best;
  };
  for (const sys of asm.systems || []) {
    for (const s of sys.staves) {
      const st = s.st, sp = st.space || ss, hdr = s.hdr || {}, left = st.left;
      const yTop = lineY(st, 0, left + 4 * sp), yBot = lineY(st, 4, left + 4 * sp);
      // header clef: the ink from the staff start to where the clef ends
      if (hdr.clef && hdr.clefEnd != null && !hdr.clefGuessed) {
        const cs = comps.filter(c => c.x0 >= left - 0.5 * sp && c.x1 <= hdr.clefEnd + 0.2 * sp && (c.x0 + c.x1) / 2 < hdr.clefEnd &&
          (c.y0 + c.y1) / 2 > yTop - 1.5 * sp && (c.y0 + c.y1) / 2 < yBot + 1.5 * sp && c.y1 - c.y0 < 9 * sp && c.y0 > yTop - 3.5 * sp && c.y1 < yBot + 3.5 * sp &&
          c.area >= 0.04 * sp * sp);
        const b = cs.length ? [Math.min(...cs.map(c => c.x0)), Math.min(...cs.map(c => c.y0)), Math.max(...cs.map(c => c.x1)), Math.max(...cs.map(c => c.y1))]
          : [left, yTop - 1.5 * sp, hdr.clefEnd, yBot + 1.5 * sp];
        out.clefs.push([...b.map(r1), hdr.clef, 0]);
        add(b);
      } else if (hdr.clef) {
        // assumed (not read): marked at the staff start, explains nothing
        out.clefs.push([r1(left), r1(yTop), r1(left + 2.5 * sp), r1(yBot), hdr.clef, 2]);
      }
      if (hdr.keyBox) { const b = box(hdr.keyBox); out.keys.push([...b, hdr.fifths, 0]); add(b); }
      if (hdr.time) {
        const b = [r1(hdr.time.x0), r1(yTop), r1(hdr.time.x1), r1(yBot)];
        out.times.push([...b, hdr.time.beats || 0, hdr.time.type || 0, hdr.time.symbol || '']);
        add(b, 0.2 * sp);
      }
      for (const ch of s.changes || []) {
        if (!ch.box) continue;
        const b = box(ch.box);
        if (ch.clef) out.clefs.push([...b, ch.clef, 1]);
        else if (ch.fifths != null) out.keys.push([...b, ch.fifths, 1]);
        add(b);
      }
      for (const t of s.tuplets || []) { const b = box(t); out.tuplets.push([...b, t.actual, t.normal]); add(b); }
      // rests, read as buildScore reads them (each measure of the system)
      for (const [xa, xb] of sys.measures || []) {
        let rs = [];
        try { rs = detectRests({ R, comps, s, xa, xb }); } catch (e) { rs = []; }
        for (const r of rs) {
          const b = box(r.box);
          out.rests.push([...b, r.kind, r1(r.q * 100) / 100, r.dots, r.multi || 0]);
          add(b);
        }
      }
      // accidentals and dots of the notes on this staff
      for (const c of s.chords) {
        const hs = c.heads;
        for (const h of hs) {
          let g = null;
          try { g = accidentalGlyph(R, comps, h, hdr.end != null ? hdr.end : -Infinity, hs.length > 1 ? 3.2 : 1.9); } catch (e) { g = null; }
          if (g) { const b = box(g); out.accs.push([...b, g.kind]); add(b); }
          if (h.dur && h.dur.dots) {
            const d = dotOf(h, h.sp || sp, st);
            if (d) { out.dots.push([r1((d.x0 + d.x1) / 2), r1((d.y0 + d.y1) / 2), r1(Math.max(d.x1 - d.x0, d.y1 - d.y0) / 2 + 1)]); add(box(d)); }
          }
        }
      }
    }
  }
  // stems (each chord's up / down stem from its outer head to the tip) and beams
  for (const c of fr.chords || []) {
    if (!c.heads || !c.heads.length) continue;
    const ys = c.heads.map(h => h.y);
    if (c.upX >= 0 && c.upEnd != null) { const s = [r1(c.upX), r1(c.upEnd), r1(Math.max(...ys))]; out.stems.push(s); add([s[0] - 1, s[1], s[0] + 1, s[2]], 1); }
    if (c.downX >= 0 && c.downEnd != null) { const s = [r1(c.downX), r1(Math.min(...ys)), r1(c.downEnd)]; out.stems.push(s); add([s[0] - 1, s[1], s[0] + 1, s[2]], 1); }
  }
  for (const b of fr.beams || []) { const bb = box(b); out.beams.push(bb); add(bb); }
  // barlines: double / final pairs (barlines.js merges them) and repeat dots
  for (const b of fr.barlines || []) {
    const st = fr.staves[b.staff];
    let type = b.double ? 'double' : 'single';
    add([b.x0 != null ? b.x0 : b.x - 1, b.top, b.x1 != null ? b.x1 : b.x + 1, b.bot], 1);
    if (st) {
      const sp = st.space || ss;
      const isDot = (c, k) => {
        const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
        return w >= 0.2 * sp && w <= 0.75 * sp && h >= 0.2 * sp && h <= 0.75 * sp && Math.abs((c.y0 + c.y1) / 2 - lineY(st, k, b.x)) <= 0.3 * sp;
      };
      const x0 = b.x0 != null ? b.x0 : b.x, x1 = b.x1 != null ? b.x1 : b.x;
      for (const side of [-1, 1]) {
        const inWin = (c) => (side < 0 ? c.x1 < x0 && c.x1 >= x0 - 1.2 * sp : c.x0 > x1 && c.x0 <= x1 + 1.2 * sp);
        const a = comps.find(c => inWin(c) && isDot(c, 1.5)), z = comps.find(c => inWin(c) && isDot(c, 2.5));
        if (a && z) { type = side < 0 ? (type === 'repeat-start' ? 'repeat-both' : 'repeat-end') : (type === 'repeat-end' ? 'repeat-both' : 'repeat-start'); add(box(a)); add(box(z)); }
      }
    }
    out.bars.push([r1(b.x), r1(b.top), r1(b.bot), type, r1(b.x0 != null ? b.x0 : b.x), r1(b.x1 != null ? b.x1 : b.x)]);
  }
  for (const h of fr.heads || []) { const sp = h.sp || ss; add([h.x - 0.65 * sp, h.y - 0.55 * sp, h.x + 0.65 * sp, h.y + 0.55 * sp]); }
  // what is left: ink after staff-line removal that touches none of the above
  // (specks and staff-line remnants aside)
  const grid = new Map(), G = Math.max(16, Math.round(4 * ss));
  known.forEach((k, i) => {
    for (let gx = Math.floor(k[0] / G); gx <= Math.floor(k[2] / G); gx++) for (let gy = Math.floor(k[1] / G); gy <= Math.floor(k[3] / G); gy++) {
      const key = gx * 65536 + gy;
      if (!grid.has(key)) grid.set(key, []);
      grid.get(key).push(i);
    }
  });
  const minA = 0.1 * ss * ss;
  for (const c of comps) {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
    if (c.area < minA || Math.max(w, h) < 0.35 * ss) continue;
    // a thin horizontal sliver along a staff line is what line removal left
    if (h <= 0.25 * ss && w < 1.5 * ss) continue;
    // a slur or tie reaches into the boxes of the heads it joins: a thin bowed
    // curve is left over even where its box touches them
    if (w >= 1.2 * ss && h <= 0.8 * w && c.area / w <= 0.5 * ss && slurLike(fr.R, c, ss)) { left.push(c); continue; }
    let hit = false;
    for (let gx = Math.floor(c.x0 / G); gx <= Math.floor(c.x1 / G) && !hit; gx++) for (let gy = Math.floor(c.y0 / G); gy <= Math.floor(c.y1 / G) && !hit; gy++) {
      for (const i of grid.get(gx * 65536 + gy) || []) {
        const k = known[i];
        if (c.x0 <= k[2] && c.x1 >= k[0] && c.y0 <= k[3] && c.y1 >= k[1]) { hit = true; break; }
      }
    }
    if (!hit) left.push(c);
  }
  return { out, left };
}

// The page's marks (text.js classifyMarks over the leftover ink), computed
// once per page and kept on fr (not enumerable: never cloned or compared);
// readPageText() fills in the text it reads.
function pageMarks(fr, asm) {
  if (!fr || !asm) return null;
  if (fr._marks && fr._marks.asm === asm) return fr._marks.marks;
  const { out, left } = explain(fr, asm);
  let marks;
  try { marks = classifyMarks(fr, asm, left); } catch (e) { marks = { text: [], dyns: [], wedges: [], slurs: [], fermatas: [], braces: [], ledgers: [], grace: [], pedals: [], fingerings: [], rehearsals: [], rest: left }; }
  Object.defineProperty(marks, 'sym', { value: out, enumerable: false, configurable: true });
  Object.defineProperty(fr, '_marks', { value: { asm, marks }, enumerable: false, configurable: true, writable: true });
  return marks;
}

// Overlay layers. Beyond the note symbols: text [box, role, label],
// dyns [box, value], wedges [box, type], slurs [box], fermatas [box], braces [box, kind],
// ledgers [box]; unknown is the ink none of these explain.
function pageSymbols(fr, asm) {
  const marks = pageMarks(fr, asm);
  if (!marks) return explain(fr, asm).out;
  const out = { ...marks.sym };
  const b4 = (b) => b.map(Math.round);
  // an unread chord-symbol candidate is still ink nobody explained
  const unreadChord = marks.text.filter(t => t.role === 'chordcand');
  out.text = marks.text.filter(t => t.role !== 'chordcand').map(t => {
    const name = ROLE_LABEL[t.role] || 'Text';
    const mm = t.metro ? `${{ quarter: '♩', eighth: '♪', half: '𝅗𝅥', '16th': '𝅘𝅥𝅯' }[t.metro.unit] || '♩'}${t.metro.dotted ? '.' : ''} = ${t.metro.bpm || '?'}` : '';
    const body = [t.text, mm].filter(Boolean).join(' ');
    const label = t.role === 'measure' ? (t.text ? `Bar ${t.text}` : 'Bar ? (number not read)') : body ? `${name}: ${body}` : name;
    return [...b4(t.box), t.role, label];
  });
  out.dyns = marks.dyns.map(d => [...b4(d.box), d.value]).concat((marks.pedals || []).map(p => [...b4(p.box), p.type === 'start' ? 'Ped.' : p.type === 'change' ? 'Ped. change' : '✽ (pedal up)']));
  out.slurs = (out.slurs || []);
  out.text = out.text.concat((marks.rehearsals || []).map(r => [...b4(r.box), 'rehearsal', `Rehearsal ${r.text}${r.guessed ? ' (letter by order)' : ''}`]));
  // fingering digits show with the text, labelled by their digit
  out.text = out.text.concat((marks.fingerings || []).map(f => [...b4(f.box), 'fingering', `Finger ${f.digit}`]));
  out.wedges = marks.wedges.map(w => [...b4(w.box), w.type === 'crescendo' ? 'cresc.' : 'dim.']);
  out.slurs = marks.slurs.map(s => b4(s.box));
  // pedal bracket lines are drawn with the dynamics
  out.dyns = (out.dyns || []).concat((marks.pedalLines || []).map(p => [...b4(p.box), 'pedal line']));
  out.fermatas = marks.fermatas.map(s => b4(s.box));
  out.braces = marks.braces.map(s => [...b4(s.box), s.kind]);
  out.ledgers = marks.ledgers.map(s => b4(s.box));
  out.grace = (marks.grace || []).map(g => [...b4(g.box), g.heads.length, g.slash ? 1 : 0]);
  out.unknown = marks.rest.concat(unreadChord.flatMap(t => t.comps || [])).map(c => [c.x0, c.y0, c.x1, c.y1]);
  return out;
}

module.exports = { pageSymbols, pageMarks };
