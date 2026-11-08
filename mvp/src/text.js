'use strict';
// Text and expression marks: the ink the note reader leaves unexplained
// (symbols.js leftover components), sorted into what it is.
//  - text lines (letters grouped into words and lines) with a role from where
//    they stand: title, subtitle, composer / lyricist / arranger credit,
//    instrument name (left of the first system) or abbreviation (later
//    systems), measure number, tempo / expression text, lyrics, header,
//    footer, copyright. readPageText() reads them with the lyrics OCR (one
//    line per call, bounded per page); without OCR they keep their role.
//  - dynamics (ppp .. fff, sf, sfz, fz, fp, rf ...) from the shapes of the
//    italic-bold dynamics letters (templates scaled by the staff space; OCR
//    does not read that font), and hairpins (two lines opening or closing).
//  - braces and system brackets, ledger lines, slurs and ties.
// Boxes are [x0, y0, x1, y1] in the page's deskewed frame.
const { _glyphImage: glyphImage } = require('./assemble');
const { makeGray } = require('./image');

// ---------------------------------------------------------------- dynamics glyphs
// Letter templates of the dynamics font: rows of a grid over the glyph box
// ('#' ink, cells about a fifth of a staff space), with the box size in
// staff spaces: [text, w, h, rows] (dynglyphs.js, made by
// tools/dynglyphs.js from engraved pages). Drawn from
// the engraved letters (LilyPond / Emmentaler, the corpus font); bold italic
// letters of other engravers are close enough for the tolerant match below.
const DYN_GLYPHS = require('./dynglyphs');
const DYN_WORDS = new Set(['ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'sf', 'sfz', 'sffz', 'sfp', 'sfpp', 'fz', 'fp', 'rf', 'rfz', 'pppp', 'ffff', 'sfzp', 'fzp', 'n']);

// glyph image (its own ink only) resampled onto a GW x gh grid
function gridOf(img, gh, GW) {
  const { width: w, height: h, data } = img;
  const g = new Float32Array(GW * gh);
  for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < GW; gx++) {
    const xa = Math.floor(gx * w / GW), xb = Math.max(xa + 1, Math.floor((gx + 1) * w / GW));
    const ya = Math.floor(gy * h / gh), yb = Math.max(ya + 1, Math.floor((gy + 1) * h / gh));
    let s = 0, n = 0;
    for (let y = ya; y < yb && y < h; y++) for (let x = xa; x < xb && x < w; x++) { s += data[y * w + x]; n++; }
    g[gy * GW + gx] = n ? s / n : 0;
  }
  return g;
}

// overlap (Dice) of a glyph grid with a template; ink one cell off counts
// a little (NEAR)
function matchGrid(g, t) {
  const gh = t.gh, GW = t.gw;
  let inter = 0, sa = 0, sb = 0;
  for (let y = 0; y < gh; y++) for (let x = 0; x < GW; x++) {
    const v = g[y * GW + x] >= 0.35 ? 1 : 0, tv = t.cells[y * GW + x];
    sa += v; sb += tv;
    if (v && tv) { inter += 1; continue; }
    if (!v && !tv) continue;
    // near miss: the other side has ink in a neighbouring cell
    let near = false;
    for (let dy = -1; dy <= 1 && !near; dy++) for (let dx = -1; dx <= 1 && !near; dx++) {
      const xx = x + dx, yy = y + dy;
      if (xx < 0 || yy < 0 || xx >= GW || yy >= gh) continue;
      near = v ? t.cells[yy * GW + xx] === 1 : g[yy * GW + xx] >= 0.35;
    }
    if (near) inter += NEAR;
  }
  return sa + sb ? (2 * inter) / (sa + sb) : 0;
}

// a near miss (ink one cell off) counts this much: enough for print and
// scan noise, too little for a text letter of the same size to pass
const NEAR = 0.15;
let TPL = null;
function templates() {
  if (TPL) return TPL;
  TPL = DYN_GLYPHS.map(([text, w, h, rows]) => {
    const gh = rows.length, gw = rows[0].length, cells = new Uint8Array(gw * gh);
    rows.forEach((r, y) => { for (let x = 0; x < gw; x++) cells[y * gw + x] = r[x] === '#' ? 1 : 0; });
    return { text, w, h, gh, gw, cells };
  });
  return TPL;
}

// best dynamics letter (or ligature) for one component: {text, score} or null
function dynGlyph(R, c, sp) {
  const w = (c.x1 - c.x0 + 1) / sp, h = (c.y1 - c.y0 + 1) / sp;
  let best = null;
  let img = null;
  for (const t of templates()) {
    if (Math.abs(w - t.w) > 0.3 * t.w + 0.15 || Math.abs(h - t.h) > 0.25 * t.h + 0.15) continue;
    if (!img) img = glyphImage(R, c);
    const s = matchGrid(gridOf(img, t.gh, t.gw), t);
    if (!best || s > best.score) best = { text: t.text, score: s };
  }
  return best;
}

// ---------------------------------------------------------------- shapes
// columns of a component's own ink: [ink runs per column] (thin-line tests)
function columnRuns(img) {
  const { width: w, height: h, data } = img, out = [];
  for (let x = 0; x < w; x++) {
    const runs = [];
    let s = -1;
    for (let y = 0; y <= h; y++) {
      const on = y < h && data[y * w + x];
      if (on && s < 0) s = y;
      else if (!on && s >= 0) { runs.push([s, y - 1]); s = -1; }
    }
    out.push(runs);
  }
  return out;
}

// hairpin: two thin lines meeting at one end (the point) and apart at the
// other, the gap growing steadily. 'crescendo' opens to the right.
function hairpin(R, c, sp) {
  const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
  if (w < 2.2 * sp || h < 0.35 * sp || h > 2.4 * sp || w < 2 * h) return null;
  const cols = columnRuns(glyphImage(R, c));
  const gap = (x) => { const r = cols[x]; if (!r || !r.length) return null; return r.length >= 2 ? r[r.length - 1][0] - r[0][1] : 0; };
  const thin = (x) => cols[x].every(([a, b]) => b - a + 1 <= 0.45 * sp);
  const xs = [0.15, 0.3, 0.5, 0.7, 0.85].map(f => Math.round(f * (w - 1)));
  const gs = xs.map(gap);
  if (gs.some(g => g == null) || !xs.every(thin)) return null;
  const inc = gs.every((g, i) => i === 0 || g >= gs[i - 1] - 1), dec = gs.every((g, i) => i === 0 || g <= gs[i - 1] + 1);
  const span = Math.abs(gs[4] - gs[0]);
  if (span < 0.25 * sp) return null;
  if (inc && gs[4] > gs[0] && cols[xs[4]].length >= 2) return 'crescendo';
  if (dec && gs[0] > gs[4] && cols[xs[0]].length >= 2) return 'diminuendo';
  return null;
}

// a slur or tie: one thin curved stroke, wider than tall, bowed
function slurLike(R, c, sp) {
  const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
  if (w < 1.0 * sp || h > 0.8 * w || h > 4 * sp) return false;
  if (c.area / w > 0.5 * sp) return false;
  const cols = columnRuns(glyphImage(R, c));
  let single = 0, n = 0;
  const mid = [];
  for (let x = 0; x < w; x++) {
    const r = cols[x];
    if (!r.length) continue;
    n++;
    if (r.length === 1 && r[0][1] - r[0][0] + 1 <= 0.5 * sp) single++;
    mid.push((r[0][0] + r[r.length - 1][1]) / 2);
  }
  if (n < 0.8 * w || single < 0.75 * n) return false;
  // bowed: the middle stands off the line joining the ends
  const a = mid[0], b = mid[mid.length - 1], m = mid[mid.length >> 1];
  return Math.abs(m - (a + b) / 2) >= Math.max(1.5, 0.15 * sp);
}

// ---------------------------------------------------------------- lines of text
function groupLines(cs) {
  cs = cs.slice().sort((a, b) => a.x0 - b.x0);
  const par = cs.map((_, i) => i);
  const find = (i) => { while (par[i] !== i) { par[i] = par[par[i]]; i = par[i]; } return i; };
  for (let i = 0; i < cs.length; i++) {
    const a = cs[i], ha = a.y1 - a.y0 + 1;
    for (let j = i + 1; j < cs.length; j++) {
      const b = cs[j], hb = b.y1 - b.y0 + 1;
      const big = Math.max(ha, hb);
      if (b.x0 - a.x1 > 1.3 * big) break;
      // the same text row: letters overlap in height (x-height letters sit
      // inside capitals), and sizes are alike
      const ov = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) + 1;
      if (ov < 0.45 * Math.min(ha, hb) || Math.min(ha, hb) < 0.3 * big) continue;
      par[find(i)] = find(j);
    }
  }
  const g = new Map();
  cs.forEach((c, i) => { const r = find(i); if (!g.has(r)) g.set(r, []); g.get(r).push(c); });
  return [...g.values()].map(mem => {
    mem.sort((a, b) => a.x0 - b.x0);
    const hs = mem.map(c => c.y1 - c.y0 + 1).sort((a, b) => a - b);
    let words = 1;
    const med = hs[hs.length >> 1];
    for (let k = 1; k < mem.length; k++) if (mem[k].x0 - Math.max(...mem.slice(0, k).map(c => c.x1)) > 0.45 * med) words++;
    return { mem, x0: Math.min(...mem.map(c => c.x0)), y0: Math.min(...mem.map(c => c.y0)), x1: Math.max(...mem.map(c => c.x1)), y1: Math.max(...mem.map(c => c.y1)), h: med, words };
  });
}

const ROLE_LABEL = {
  title: 'Title', subtitle: 'Subtitle', composer: 'Composer', lyricist: 'Lyricist', arranger: 'Arranger', credit: 'Credit',
  instrument: 'Instrument', abbrev: 'Instrument', measure: 'Bar', tempo: 'Tempo', expression: 'Expression', lyrics: 'Lyrics',
  header: 'Header', footer: 'Footer', page: 'Page', copyright: 'Copyright', text: 'Text',
};

// Sort leftover components (symbols.js) into marks.
// left: [{x0,y0,x1,y1,area}], fr / asm as front() and assemblePage() left them.
function classifyMarks(fr, asm, left) {
  const out = { text: [], dyns: [], wedges: [], slurs: [], braces: [], ledgers: [], rest: [] };
  const R = fr.R, ss = fr.ss, W = fr.gray.width, H = fr.gray.height;
  const systems = (asm && asm.systems) || [];
  if (!R || !systems.length) { out.rest = left.slice(); return out; }
  const stv = systems.map(sy => sy.staves.map(s => {
    const st = s.st, sp = st.space || ss;
    return { st, si: s.si, sp, left: st.left, right: st.right, top: (x) => st.yAt(0, x), bot: (x) => st.yAt(4, x) };
  }));
  const allSt = stv.flat();
  const L0 = Math.min(...allSt.map(s => s.left)), R0 = Math.max(...allSt.map(s => s.right));
  const firstTop = Math.min(...stv[0].map(s => s.top(s.left)));
  const lastSys = stv[stv.length - 1];
  const lastBot = Math.max(...lastSys.map(s => s.bot(s.left)));
  // the staff nearest a point (vertical distance to its band) and its system
  const nearest = (x, y) => {
    let best = null, bd = Infinity;
    stv.forEach((sts, k) => sts.forEach((s, j) => {
      const xx = Math.max(s.left, Math.min(s.right, x)), t = s.top(xx), b = s.bot(xx);
      const d = y < t ? t - y : y > b ? y - b : 0;
      // a mark between two staves belongs to the upper one on a tie
      if (d < bd - 1e-6 || (Math.abs(d - bd) <= 1e-6 && best && y > b)) { bd = d; best = { sys: k, k: j, s, d, above: y < t, inside: d === 0 }; }
    }));
    return best;
  };
  const inBand = (c) => {
    const n = nearest((c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2);
    return n && n.inside;
  };
  const heads = fr.heads || [];
  const rest = [];
  const letters = [];
  for (const c of left) {
    const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1, cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
    const n = nearest(cx, cy), sp = n ? n.s.sp : ss;
    // brace / system bracket: tall, narrow, at the staves' left edge
    if (h >= 3 * sp && w <= 1.6 * sp && n && cx <= n.s.left + 0.6 * sp && cx >= n.s.left - 2.5 * sp) { out.braces.push({ box: [c.x0, c.y0, c.x1, c.y1], kind: w <= 0.45 * sp ? 'line' : 'brace' }); continue; }
    // ledger line: short, thin, horizontal, off the staff, by a note head
    if (h <= 0.4 * sp && w >= 0.9 * sp && w <= 3.6 * sp && n && !n.inside &&
      heads.some(hd => Math.abs(hd.x - cx) <= 1.5 * sp && Math.abs(hd.y - cy) <= 1.3 * sp + (n.above ? Math.max(0, cy - hd.y) : Math.max(0, hd.y - cy)))) {
      out.ledgers.push({ box: [c.x0, c.y0, c.x1, c.y1] }); continue;
    }
    const hp = hairpin(R, c, sp);
    if (hp) { out.wedges.push({ box: [c.x0, c.y0, c.x1, c.y1], type: hp, sys: n.sys, k: n.k, si: n.s.si }); continue; }
    if (slurLike(R, c, sp)) { out.slurs.push({ box: [c.x0, c.y0, c.x1, c.y1] }); continue; }
    // letter-sized ink (text, dynamics)
    if (h >= 0.35 * sp && h <= 4.5 * sp && w <= 6 * sp && !(h < 0.6 * sp && w > 2.5 * h)) { letters.push(c); continue; }
    rest.push(c);
  }
  // dynamics: a run of letters that all read as dynamics letters and spell a
  // dynamic, off the staff (or in a margin between staves)
  const lines = groupLines(letters);
  const textLines = [];
  for (const ln of lines) {
    const n = nearest((ln.x0 + ln.x1) / 2, (ln.y0 + ln.y1) / 2);
    const sp = n ? n.s.sp : ss;
    const dyn = n && !n.inside && ln.h <= 3.2 * sp ? readDynamic(R, ln, sp) : null;
    if (dyn) { out.dyns.push({ box: [ln.x0, ln.y0, ln.x1, ln.y1], value: dyn.text, score: +dyn.score.toFixed(2), sys: n.sys, k: n.k, si: n.s.si, x: (ln.x0 + ln.x1) / 2 }); continue; }
    // text inside a staff band is rare (text over a staff is more often a
    // misread chord or a stray): left unknown
    if (n && n.inside && ln.x0 > n.s.left) { rest.push(...ln.mem); continue; }
    textLines.push({ ...ln, n });
  }
  // roles from where the lines stand
  const header = textLines.filter(l => l.y1 < firstTop - 0.5 * ss && !(l.x1 < L0 - 0.3 * ss));
  const maxH = Math.max(0, ...header.map(l => l.h));
  const pageMid = (L0 + R0) / 2, wMusic = R0 - L0;
  for (const l of textLines) {
    const cx = (l.x0 + l.x1) / 2, cy = (l.y0 + l.y1) / 2, n = l.n, sp = n ? n.s.sp : ss;
    let role = 'text';
    const sysOf = n ? n.sys : -1;
    const sts = sysOf >= 0 ? stv[sysOf] : null;
    const sysTop = sts ? Math.min(...sts.map(s => s.top(s.left))) : 0, sysBot = sts ? Math.max(...sts.map(s => s.bot(s.left))) : 0;
    const sysLeft = sts ? Math.min(...sts.map(s => s.left)) : L0;
    if (sts && l.x1 < sysLeft - 0.2 * sp && cy > sysTop - 1.5 * sp && cy < sysBot + 1.5 * sp) role = sysOf === 0 ? 'instrument' : 'abbrev';
    else if (l.y1 < 0.06 * H && l.h < 1.6 * ss && l.y1 < firstTop - 3 * ss) role = 'header';
    else if (l.y0 > 0.92 * H && l.y0 > lastBot + 2 * ss) role = 'footer';
    else if (sts && l.y1 <= sysTop + 0.3 * sp && l.y1 >= sysTop - 3.2 * sp && l.x0 <= sysLeft + 2.5 * sp && l.x0 >= sysLeft - 3.5 * sp && l.h <= 1.3 * sp && l.mem.length <= 3 && l.words === 1 &&
      (l.y1 >= firstTop - 3.2 * sp || sysOf > 0)) role = 'measure';
    else if (l.y1 < firstTop - 0.5 * ss) {
      const centred = Math.abs(cx - pageMid) < 0.12 * wMusic && l.x0 > L0 + 0.1 * wMusic;
      if (centred && l.h >= 0.85 * maxH) role = 'title';
      else if (centred) role = 'subtitle';
      else if (l.x1 > R0 - 0.2 * wMusic && l.x0 > pageMid) role = 'composer';
      else if (l.y1 >= firstTop - 4.5 * ss && l.x0 <= L0 + 0.35 * wMusic) role = 'tempo';
      else if (l.x0 <= L0 + 0.25 * wMusic) role = 'lyricist';
      else role = 'credit';
    } else if (l.y0 > lastBot + 2.5 * ss) role = l.y0 > 0.9 * H ? 'footer' : 'text';
    else if (n && !n.above && l.words >= 4 && l.y0 - n.s.bot(cx) < 5 * sp) role = 'lyrics';
    else if (n && n.above && n.k === 0 && l.y1 > sysTop - 5 * sp && ((sysOf === 0 && l.x0 <= sysLeft + 0.3 * wMusic && l.h >= 1.0 * sp) || l.words >= 2)) role = 'tempo';
    else role = 'expression';
    // a lone glyph or specks among the music is more likely a symbol the
    // reader missed (a rest, a flag) than text: left unknown
    if ((role === 'expression' || role === 'text' || role === 'lyrics' || role === 'tempo') && (l.mem.length < 2 || l.h < 0.55 * sp)) { rest.push(...l.mem); continue; }
    out.text.push({ box: [l.x0, l.y0, l.x1, l.y1], role, text: '', h: l.h, words: l.words, sys: sysOf, k: n ? n.k : -1, si: n ? n.s.si : -1, x: l.x0, comps: l.mem });
  }
  // two titles: the larger one wins, the other is a subtitle
  const titles = out.text.filter(t => t.role === 'title').sort((a, b) => b.h - a.h || a.box[1] - b.box[1]);
  titles.slice(1).forEach(t => { t.role = 'subtitle'; });
  // several right-aligned credit lines: the first is the composer; a line
  // above the title is a dedication / header
  const comp = out.text.filter(t => t.role === 'composer').sort((a, b) => a.box[1] - b.box[1]);
  comp.slice(1).forEach(t => { t.role = 'credit'; });
  out.rest = rest;
  return out;
}

// letters of one line read as a dynamic: {text, score} or null
function readDynamic(R, ln, sp) {
  if (ln.mem.length > 5 || ln.x1 - ln.x0 > 5.5 * sp) return null;
  let text = '', sc = 1;
  for (const c of ln.mem) {
    const g = dynGlyph(R, c, sp);
    if (!g || g.score < 0.72) return null;
    text += g.text;
    sc = Math.min(sc, g.score);
  }
  return DYN_WORDS.has(text) ? { text, score: sc } : null;
}

// ---------------------------------------------------------------- OCR
// What a role's text reads as; refines the role from its words.
const TEMPO_RE = /^(tempo|allegr|andant|adagi|larg|lent|prest|vivac|modera|grave|maestos|allegrett|andantin|marcia|marcato|not fast|slow|fast|lively|moderately|brightly|gently|with|rubato|a tempo|tempo di|in time|langsam|schnell|mässig|massig|ruhig|bewegt|lebhaft|sehr|nicht|rasch|innig|zart|mouvement|lent|vif|modéré|anim|swing|ballad|march|waltz|valse|walzer)/i;
const EXPR_RE = /^(cresc|decresc|dim|rit|rall|accel|poco|più|piu|meno|molto|sempre|subito|dolce|espr|leggiero|legato|stacc|sost|smorz|morendo|cantabile|sotto|mezza|con|senza|ten|marc|sfz|simile|una corda|tre corde|pizz|arco|div|unis|solo|tutti|loco|fine|d\.?\s?c|d\.?\s?s|da capo|dal segno|coda|to coda|segno)/i;
function refineRole(t) {
  const s = t.text.trim();
  if (!s) return;
  if (/©|\(c\)|copyright|all rights|public domain|creative commons|cc0|cc-by/i.test(s)) { t.role = 'copyright'; return; }
  if (t.role === 'header' || t.role === 'footer') { if (/^\d{1,3}$/.test(s)) t.role = 'page'; return; }
  if (t.role === 'measure') { if (!/^\d{1,4}$/.test(s.replace(/\s/g, ''))) t.role = 'expression'; return; }
  if (t.role === 'composer' || t.role === 'lyricist' || t.role === 'credit' || t.role === 'subtitle') {
    if (/\barr(\.|anged)?\b|bearb|arrangement/i.test(s)) t.role = 'arranger';
    else if (/\b(words|lyrics|text|poem|poet|dichtung|worte|paroles)\b/i.test(s)) t.role = 'lyricist';
    else if (/\b(music|musik|composed|komp|musique)\b/i.test(s) && t.role !== 'subtitle') t.role = 'composer';
    else if (t.role !== 'subtitle' && TEMPO_RE.test(s)) t.role = 'tempo';
    return;
  }
  if (t.role === 'expression' || t.role === 'tempo' || t.role === 'text') {
    if (TEMPO_RE.test(s) && !EXPR_RE.test(s)) t.role = 'tempo';
    else if (EXPR_RE.test(s)) t.role = 'expression';
  }
}

// Read the text lines of a page's marks (pageMarks() result) with the
// injected OCR (lyrics.js setup: one masked line per call). Lyrics lines are
// lyrics.js's to read; at most maxLines lines per page.
async function readPageText(fr, marks, ocr, opts = {}) {
  if (!ocr || !marks || !fr.gray || !fr.gray.data) return 0;
  const maxLines = opts.maxLines || 16;
  const order = { title: 0, composer: 1, instrument: 2, abbrev: 3, subtitle: 4, lyricist: 5, arranger: 5, credit: 6, tempo: 7, expression: 8, measure: 9, copyright: 10, footer: 11, header: 12, page: 13, text: 14 };
  const todo = marks.text.filter(t => t.role !== 'lyrics').sort((a, b) => (order[a.role] ?? 20) - (order[b.role] ?? 20));
  // only one abbreviation line per staff is needed (they repeat on every system)
  const seenAbbr = new Set();
  let n = 0;
  for (const t of todo) {
    if (n >= maxLines) break;
    if (t.role === 'abbrev') { const key = t.k; if (seenAbbr.has(key)) continue; seenAbbr.add(key); }
    // the instrument names lyrics.js already read (fr.partLabels)
    if (t.role === 'instrument' && fr.partLabels) {
      const cy = (t.box[1] + t.box[3]) / 2;
      const pl = fr.partLabels.find(p => p.y != null && Math.abs(p.y - cy) <= t.h);
      if (pl) { t.text = pl.text; t.conf = pl.conf; continue; }
    }
    const img = lineCrop(fr, t.box, t.h);
    if (!img) continue;
    let words = [];
    try { words = await ocr(img); } catch (e) { words = []; }
    n++;
    const ok = words.filter(w => w.conf >= 30 && /[\p{L}\p{N}]/u.test(w.text));
    t.text = ok.map(w => w.text).join(' ').replace(/\s+/g, ' ').trim();
    t.conf = ok.length ? Math.round(ok.reduce((a, w) => a + w.conf, 0) / ok.length) : 0;
    refineRole(t);
  }
  // the abbreviation read once stands for its staff on every later system
  for (const t of marks.text) if (t.role === 'abbrev' && !t.text) {
    const r = marks.text.find(u => u.role === 'abbrev' && u.k === t.k && u.text);
    if (r) t.text = r.text;
  }
  return n;
}

// gray crop of a text line, upscaled to ~40 px capitals with a white margin
function lineCrop(fr, b, h) {
  const g = fr.gray, W = g.width, H = g.height;
  const pad = Math.round(0.35 * h);
  const x0 = Math.max(0, Math.floor(b[0]) - pad), y0 = Math.max(0, Math.floor(b[1]) - pad);
  const x1 = Math.min(W - 1, Math.ceil(b[2]) + pad), y1 = Math.min(H - 1, Math.ceil(b[3]) + pad);
  const cw = x1 - x0 + 1, ch = y1 - y0 + 1;
  if (cw < 4 || ch < 4) return null;
  const scale = Math.min(3, Math.max(0.5, 40 / Math.max(8, h)));
  const m = Math.round(0.5 * h);
  const OW = Math.round((cw + 2 * m) * scale), OH = Math.round((ch + 2 * m) * scale);
  const img = makeGray(OW, OH, 255);
  for (let y = 0; y < OH; y++) for (let x = 0; x < OW; x++) {
    const sx = Math.floor(x / scale) - m, sy = Math.floor(y / scale) - m;
    if (sx >= 0 && sy >= 0 && sx < cw && sy < ch) img.data[y * OW + x] = g.data[(y0 + sy) * W + x0 + sx];
  }
  return img;
}

module.exports = { classifyMarks, readPageText, refineRole, ROLE_LABEL, DYN_WORDS, _dynGlyph: dynGlyph, _gridOf: gridOf, _hairpin: hairpin, _slurLike: slurLike, _groupLines: groupLines };
