'use strict';
// Time signatures through the piece (L16 / L21).
//
// readMeters(fr, asm) runs once per page at the start of buildScore (score.js) and reads every
// time signature on the page, not only the first system's header:
//   - the header of every system (cv.js readHeaders reads numbers on the first system only);
//   - after a barline inside a system (a meter change, after the key change when there is one);
//   - after the last barline of a system (a courtesy signature announcing the next system's
//     meter: it is not a bar, and heads found on its digits are dropped with the bar they made).
// Numbers are matched against the Bravura digit templates (cv.js readTime); C and cut C against
// the time-C / time-cut templates. Each system gets sy.meters: [{x, beats, type, symbol, header,
// courtesy}] in x order, where x is the barline (or staff start) from which the meter holds.
// buildScore (score.js) takes the meter in force at each bar from them when the page shows a
// change of meter, and writes <time> where it changes.
const { readTime, makeJsApi } = require('./cv');
const { labelComponents } = require('./cc');

let api0 = null;
const matcher = () => (api0 ||= makeJsApi());

// ink of R inside box b (components whose centre is inside), trimmed; null when none
function crop(R, b, minArea) {
  const x0 = Math.max(0, Math.floor(b.x0)), y0 = Math.max(0, Math.floor(b.y0));
  const x1 = Math.min(R.width - 1, Math.ceil(b.x1)), y1 = Math.min(R.height - 1, Math.ceil(b.y1));
  if (x1 <= x0 || y1 <= y0) return null;
  const w = x1 - x0 + 1, h = y1 - y0 + 1, img = { width: w, height: h, data: new Uint8Array(w * h) };
  for (let y = 0; y < h; y++) img.data.set(R.data.subarray((y + y0) * R.width + x0, (y + y0) * R.width + x0 + w), y * w);
  const { labels, comps } = labelComponents(img);
  const keep = comps.filter(c => c.area >= minArea && (!b.inner || b.inner(c.x0 + x0, c.y0 + y0, c.x1 + x0, c.y1 + y0)));
  if (!keep.length) return null;
  const ids = new Set(keep.map(c => c.id));
  let gx0 = w, gy0 = h, gx1 = -1, gy1 = -1;
  for (const c of keep) { gx0 = Math.min(gx0, c.x0); gy0 = Math.min(gy0, c.y0); gx1 = Math.max(gx1, c.x1); gy1 = Math.max(gy1, c.y1); }
  const gw = gx1 - gx0 + 1, gh = gy1 - gy0 + 1, data = new Uint8Array(gw * gh);
  for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) if (ids.has(labels[(y + gy0) * w + x + gx0])) data[y * gw + x] = 1;
  return { img: { w: gw, h: gh, data }, x0: gx0 + x0, y0: gy0 + y0, x1: gx1 + x0, y1: gy1 + y0 };
}

// staff-line removal leaves short vertical gaps: fill them where ink is above and below
function heal(img, n) {
  const { w, h, data } = img;
  for (let x = 0; x < w; x++) {
    let last = -1;
    for (let y = 0; y < h; y++) {
      if (!data[y * w + x]) continue;
      if (last >= 0 && y - last > 1 && y - last - 1 <= n) for (let k = last + 1; k < y; k++) data[k * w + x] = 1;
      last = y;
    }
  }
  return img;
}

const C_OTHERS = ['head-filled', 'head-half', 'rest-quarter', 'rest-8th', 'acc-sharp', 'acc-flat', 'acc-natural', 'clef-C', 'digit-2', 'digit-3', 'digit-4', 'digit-6', 'digit-8', 'digit-9'];
// a C or cut C starting within [xa, xb]: centred on the middle line, about two spaces high
// (the cut stroke reaches further up and down)
function readCommon(R, st, xa, xb, sp) {
  const xm = (xa + xb) / 2, l0 = st.yAt(0, xm), l2 = st.yAt(2, xm), l4 = st.yAt(4, xm);
  // the glyph's first piece starts in [xa, xb]; the rest of it (the C's terminals and the
  // cut stroke, cut apart by staff-line removal) within 1.5 spaces of it
  const minA = Math.max(3, 0.03 * sp * sp), band = (cy0, cy1) => Math.abs((cy0 + cy1) / 2 - l2) < 1.4 * sp;
  const first = crop(R, { x0: xa, x1: xb + 2.4 * sp, y0: l0 - 1.2 * sp, y1: l4 + 1.2 * sp,
    inner: (cx0, cy0, cx1, cy1) => cx0 >= xa - 0.1 * sp && cx0 <= xb && cx1 - cx0 < 2.2 * sp && band(cy0, cy1) }, minA);
  if (!first) return null;
  const g = crop(R, { x0: first.x0 - 1, x1: first.x0 + 3 * sp, y0: l0 - 1.2 * sp, y1: l4 + 1.2 * sp,
    inner: (cx0, cy0, cx1, cy1) => cx0 >= first.x0 - 1 && cx0 <= first.x0 + 1.5 * sp && cx1 - cx0 < 2.2 * sp && band(cy0, cy1) }, minA);
  if (!g) return null;
  const w = (g.x1 - g.x0 + 1) / sp, h = (g.y1 - g.y0 + 1) / sp, cy = (g.y0 + g.y1) / 2;
  if (w < 0.9 || w > 2.1 || h < 1.6 || h > 4.6 || Math.abs(cy - l2) > 0.5 * sp) return null;
  const sc = matcher().scores(heal(g.img, Math.max(2, Math.round(0.18 * sp))), sp, ['time-C', 'time-cut'].concat(C_OTHERS));
  const k = sc['time-cut'] > sc['time-C'] ? 'time-cut' : 'time-C';
  const other = Math.max(...C_OTHERS.map(n => sc[n]));
  if (sc[k] < 0.5 || sc[k] - other < 0.05) return null;
  // the cut stroke runs well past the C's top and bottom
  const cut = k === 'time-cut' && h >= 2.6;
  return { beats: cut ? 2 : 4, type: cut ? 2 : 4, symbol: cut ? 'cut' : 'common', x0: g.x0, x1: g.x1, score: sc[k] };
}

// barline x positions of a system (the staves' barlines clustered)
function systemBars(fr, sy) {
  const sis = new Set(sy.staves.map(s => s.si));
  const xs = fr.barlines.filter(b => sis.has(b.staff)).map(b => b.x).sort((a, b) => a - b);
  const cl = [];
  for (const x of xs) {
    const last = cl[cl.length - 1];
    if (last && x - last[last.length - 1] < 1.2 * fr.ss) last.push(x); else cl.push([x]);
  }
  return cl.map(c => c.reduce((a, b) => a + b, 0) / c.length);
}

const DIGITS = ['digit-0', 'digit-1', 'digit-2', 'digit-3', 'digit-4', 'digit-5', 'digit-6', 'digit-7', 'digit-8', 'digit-9'];
const NOT_DIGITS = ['rest-quarter', 'rest-8th', 'acc-sharp', 'acc-flat', 'acc-natural', 'head-filled', 'head-half', 'time-C'];
const TYPES = new Set([1, 2, 4, 8, 16, 32]);

// the number in one half of the staff read from all the ink in the band (not by components: on
// a worn scan staff-line removal breaks the digits into pieces, and the two numbers run together
// across the middle line). The number's columns: from the first ink column on, to a gap.
function bandNumber(R, x0, x1, ya, yb, sp) {
  const W = R.width, X0 = Math.max(0, Math.round(x0)), X1 = Math.min(W - 1, Math.round(x1)), Y0 = Math.max(0, Math.round(ya)), Y1 = Math.min(R.height - 1, Math.round(yb));
  const col = (x) => { let n = 0; for (let y = Y0; y <= Y1; y++) n += R.data[y * W + x] ? 1 : 0; return n; };
  // (past the barline's columns, ink from top to bottom of the band)
  let a = X0;
  while (a <= X1 && col(a) >= 0.85 * (Y1 - Y0 + 1)) a++;
  while (a <= X1 && col(a) < 2) a++;
  if (a > X1) return null;
  let b = a, gap = 0;
  for (let x = a; x <= X1 && x - a < 2.4 * sp; x++) { if (col(x) >= 1) { b = x; gap = 0; } else if (++gap > 0.3 * sp) break; }
  const w = b - a + 1;
  if (w < 0.4 * sp || w > 2.4 * sp) return null;
  const read = (xa, xb) => {
    const g = crop(R, { x0: xa, x1: xb, y0: Y0, y1: Y1 }, 2);
    if (!g || g.y1 - g.y0 + 1 < 1.0 * sp) return null;
    const sc = matcher().scores(heal(g.img, Math.max(2, Math.round(0.18 * sp))), sp, DIGITS.concat(NOT_DIGITS));
    const d = DIGITS.reduce((p, n) => (sc[n] > sc[p] ? n : p), DIGITS[0]), o = Math.max(...NOT_DIGITS.map(n => sc[n]));
    return sc[d] >= 0.5 && sc[d] > o + 0.02 ? { v: DIGITS.indexOf(d), score: sc[d] } : null;
  };
  // one digit, or two side by side (12): split at the emptiest column of the middle third
  let best = null;
  const one = read(a, b);
  if (one) best = { n: one.v, score: one.score };
  if (w >= 1.3 * sp) {
    let cut = -1, cm = Infinity;
    for (let x = a + Math.round(w / 3); x <= b - Math.round(w / 3); x++) { const c = col(x); if (c < cm) { cm = c; cut = x; } }
    const l = read(a, cut), r = l && l.v > 0 ? read(cut + 1, b) : null;
    if (l && r && Math.min(l.score, r.score) > (best ? best.score + 0.05 : 0)) best = { n: 10 * l.v + r.v, score: Math.min(l.score, r.score) };
  }
  return best ? { ...best, x0: a, x1: b } : null;
}

function bandTime(R, st, x, sp) {
  const xm = x + sp, l0 = st.yAt(0, xm), l2 = st.yAt(2, xm), l4 = st.yAt(4, xm);
  const top = bandNumber(R, x, x + 3 * sp, l0 - 0.3 * sp, l2 - 0.08 * sp, sp);
  if (!top || top.n < 2 || top.n > 16) return null;
  const bot = bandNumber(R, x, x + 3 * sp, l2 + 0.08 * sp, l4 + 0.3 * sp, sp);
  if (!bot || !TYPES.has(bot.n) || Math.min(top.x1, bot.x1) - Math.max(top.x0, bot.x0) < 0.3 * sp) return null;
  return { beats: top.n, type: bot.n, x0: Math.min(top.x0, bot.x0), x1: Math.max(top.x1, bot.x1), score: Math.min(top.score, bot.score) };
}

// a time signature on staff s starting at about x (after a barline or a key change)
function meterAt(R, s, x, sp) {
  const st = s.st, api = matcher();
  const t = readTime(api, R, st, x - 0.1 * sp, x + 3.4 * sp, sp, 0.55) || bandTime(R, st, x - 0.1 * sp, sp);
  if (t && t.x0 < x + 1.3 * sp && t.beats >= 1) return { beats: t.beats, type: t.type, symbol: '', x0: t.x0, x1: t.x1, score: t.score };
  const c = readCommon(R, st, x - 0.1 * sp, x + 1.3 * sp, sp);
  return c;
}

const valueOf = (m) => `${m.beats}/${m.type}/${m.symbol || ''}`;
// meters that occur in practice: a worn 3 or 5 read as 11, or a stem read as a 1, gives none of these
const PLAUSIBLE_BEATS = new Set([2, 3, 4, 5, 6, 7, 8, 9, 12]), PLAUSIBLE_TYPES = new Set([2, 4, 8, 16]);
const plausible = (m) => !!m && PLAUSIBLE_BEATS.has(m.beats) && PLAUSIBLE_TYPES.has(m.type);

function readMeters(fr, asm, stats = {}) {
  const R = fr && fr.R;
  if (!R || !asm) return stats;
  asm.systems.forEach((sy, si) => {
    const bars = systemBars(fr, sy);
    const found = []; // {x, staff, m}
    for (const s of sy.staves) {
      const st = s.st, sp = st.space || fr.ss, h = s.hdr;
      if (!h) continue;
      const drop = []; // x ranges whose 'heads' are digits
      try {
        // the header (the first system's numbers are read by cv.js readHeaders)
        if (h.time && !h.time.beats && si > 0) {
          const t = readTime(matcher(), R, st, h.time.x0 - 0.3 * sp, h.time.x1 + 0.3 * sp, sp, 0.45);
          if (t) { h.time.beats = t.beats; h.time.type = t.type; h.time.cv = true; stats.timeRead = (stats.timeRead || 0) + 1; }
        } else if (!h.time) {
          const x0 = h.end - 0.4 * sp;
          const t = si > 0 ? readTime(matcher(), R, st, x0, x0 + 3.6 * sp, sp, 0.55) : null;
          const m = t && t.x0 < h.end + 1.5 * sp ? { beats: t.beats, type: t.type, symbol: '', x0: t.x0, x1: t.x1 } : readCommon(R, st, h.end - 0.3 * sp, h.end + 1.5 * sp, sp);
          if (m) {
            h.time = { x0: m.x0, x1: m.x1, beats: m.beats, type: m.type, symbol: m.symbol || undefined, cv: true };
            h.end = Math.max(h.end, m.x1 + 0.2 * sp);
            drop.push([-Infinity, h.end]);
            stats.timeFound = (stats.timeFound || 0) + 1;
          }
        } else if (h.time.symbol === 'common' || (!h.time.beats && !h.time.symbol)) {
          // a C read by its back: cut C has the stroke through it
          const c = readCommon(R, st, h.time.x0 - 0.3 * sp, h.time.x0 + 0.6 * sp, sp);
          if (c) Object.assign(h.time, { beats: c.beats, type: c.type, symbol: c.symbol });
        }
        if (h.time && h.time.beats) found.push({ x: st.left, staff: s, header: true, m: { beats: h.time.beats, type: h.time.type, symbol: h.time.symbol || '' } });
        // after each barline (after a key change standing there)
        for (const bx of bars) {
          if (bx < h.end + sp || bx > st.right - 0.3 * sp) continue;
          let x = bx + 0.3 * sp;
          const kc = (s.changes || []).find(ch => ch.fifths != null && ch.box && ch.box.x0 > bx && ch.box.x0 < bx + 2 * sp);
          if (kc) x = kc.box.x1 + 0.2 * sp;
          const m = meterAt(R, s, x, sp);
          if (!m) continue;
          found.push({ x: bx, staff: s, m });
        }
        // a signature after a barline that was missed: stacked digits whose top number fills the
        // upper half of the staff, away from the barlines already looked at (it splits the bar)
        const tops = (asm.comps || []).filter(c => {
          const xm = (c.x0 + c.x1) / 2, w = (c.x1 - c.x0 + 1) / sp, hh = (c.y1 - c.y0 + 1) / sp;
          // (the two numbers may touch once the middle line is removed: one glyph the staff's height)
          const half = hh >= 1.4 && hh <= 2.5 && Math.abs(c.y1 - st.yAt(2, xm)) <= 0.45 * sp, full = hh >= 3.3 && hh <= 4.6 && Math.abs(c.y1 - st.yAt(4, xm)) <= 0.45 * sp;
          return c.x0 > h.end + 2 * sp && c.x1 < st.right - 2 * sp && w >= 0.7 && w <= 2.3 && (half || full) &&
            Math.abs(c.y0 - st.yAt(0, xm)) <= 0.8 * sp && !bars.some(b => c.x0 > b - sp && c.x0 < b + 3.5 * sp);
        });
        for (const c of tops) {
          if (found.some(f => f.staff === s && !f.header && Math.abs(f.m.x0 - c.x0) < 2 * sp)) continue;
          const t = readTime(matcher(), R, st, c.x0 - 0.3 * sp, c.x0 + 3.4 * sp, sp, 0.48);
          if (!t || Math.abs(t.x0 - c.x0) > 0.5 * sp) continue;
          found.push({ x: t.x0 - 0.6 * sp, staff: s, m: { beats: t.beats, type: t.type, symbol: '', x0: t.x0, x1: t.x1, score: t.score }, split: true });
        }
      } catch (e) { stats.errors = (stats.errors || 0) + 1; }
      if (drop.length) {
        const n = s.chords.length;
        s.chords = s.chords.filter(c => !drop.some(([a, b]) => c.x >= a && c.x <= b));
        stats.headsDropped = (stats.headsDropped || 0) + n - s.chords.length;
      }
    }
    // one meter per barline (readings within a space and a half of each other): the value most
    // staves read there (a lone reading on a system of three staves or more is not enough)
    const meters = [];
    const groups = [];
    for (const f of found.filter(f => !f.header).sort((a, b) => a.x - b.x)) {
      const g = groups[groups.length - 1];
      if (g && f.x - g[g.length - 1].x < 1.5 * fr.ss) g.push(f); else groups.push([f]);
    }
    const hdr = found.filter(f => f.header);
    if (hdr.length) groups.unshift(hdr);
    for (const fs of groups) {
      const cnt = {};
      for (const f of fs) if (plausible(f.m)) cnt[valueOf(f.m)] = (cnt[valueOf(f.m)] || 0) + 1;
      if (!Object.keys(cnt).length) continue;
      const [v, n] = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0];
      if (sy.staves.length >= 3 && n < 2) continue;
      const f = fs.find(g => valueOf(g.m) === v);
      // with no barline before it: two staves agreeing, or one clear reading
      if (fs.every(g => g.split) && n < 2 && !(f.m.score >= 0.6)) continue;
      meters.push({ x: f.header ? Math.min(...sy.staves.map(s => s.st.left)) : Math.min(...fs.map(g => g.x)), beats: f.m.beats, type: f.m.type, symbol: f.m.symbol || '', header: !!f.header, split: fs.every(g => g.split) });
      if (f.header) continue;
      // the digits are no notes on any staff of the system (a staff that did not read them too)
      const xa = Math.min(...fs.map(g => g.m.x0)) - 0.3 * fr.ss, xb = Math.max(...fs.map(g => g.m.x1)) + 0.3 * fr.ss;
      for (const s of sy.staves) {
        const n = s.chords.length;
        s.chords = s.chords.filter(c => c.x < xa || c.x > xb);
        stats.headsDropped = (stats.headsDropped || 0) + n - s.chords.length;
      }
    }
    meters.sort((a, b) => a.x - b.x);
    // a signature with no barline before it: the bar is split there
    for (const m of meters) {
      if (!m.split) continue;
      const k = sy.measures.findIndex(([xa, xb]) => m.x - xa > 2 * fr.ss && xb - m.x > 2 * fr.ss);
      if (k >= 0) { const [xa, xb] = sy.measures[k]; sy.measures.splice(k, 1, [xa, m.x], [m.x, xb]); stats.barsSplit = (stats.barsSplit || 0) + 1; }
    }
    // a signature after the system's last barline with no notes after it announces the next
    // system's meter
    const right = Math.max(...sy.staves.map(s => s.st.right));
    for (const m of meters) {
      if (m.header) continue;
      const later = bars.filter(b => b > m.x + 0.5 * fr.ss);
      const notes = sy.staves.some(s => s.chords.some(c => c.x > m.x + 0.5 * fr.ss));
      if (!later.length && !notes && right - m.x < 6 * fr.ss) m.courtesy = true;
    }
    // bars left empty by the digits dropped (the courtesy signature's 'bar')
    const before = sy.measures.length;
    sy.measures = sy.measures.filter(([xa, xb]) => {
      const sp = fr.ss;
      if (xb - xa > 6 * sp) return true;
      if (sy.staves.some(s => s.chords.some(c => c.x > xa && c.x < xb))) return true;
      return !meters.some(m => !m.header && m.x >= xa - sp && m.x <= xb);
    });
    stats.barsDropped = (stats.barsDropped || 0) + before - sy.measures.length;
    sy.meters = meters;
    stats.meters = (stats.meters || 0) + meters.filter(m => !m.header).length;
  });
  return stats;
}

module.exports = { readMeters, readCommon, systemBars, plausibleMeter: plausible, matcher, crop, heal };
