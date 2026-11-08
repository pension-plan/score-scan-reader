'use strict';
// Orchestrator: gray pages -> score (parts, MusicXML), overlay data, warnings.
// createConverter() takes the pages one at a time (the page's worker session
// uses it: addPage per page, then finish); convert() runs it over a list.
// Per page it also recovers from two scan layouts the image stages assume
// away: a page scanned sideways or upside down (turned until clefs read), and
// a two-up spread (two book pages side by side on one sheet: read as the left
// page, then the right page).
const { front } = require('./front');
const { assemblePage } = require('./assemble');
const { readLyrics } = require('./lyrics');
const { readPageText } = require('./text');
const { pageMarks } = require('./symbols');
const { buildScore } = require('./score');
const { makeGray } = require('./image');
const { readHeaders, dewarpReading } = require('./cv');

// gray page turned clockwise by quarter turns (1, 2 or 3)
function turnGray(g, turns) {
  const w = g.width, h = g.height, s = g.data;
  if (turns === 2) {
    const o = makeGray(w, h), d = o.data, n = s.length;
    for (let i = 0; i < n; i++) d[i] = s[n - 1 - i];
    return o;
  }
  const o = makeGray(h, w), d = o.data;
  if (turns === 1) { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) d[x * h + (h - 1 - y)] = s[y * w + x]; }
  else { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) d[(w - 1 - x) * h + y] = s[y * w + x]; }
  return o;
}

function cropGray(g, x0, x1) {
  const w = x1 - x0, o = makeGray(w, g.height);
  for (let y = 0; y < g.height; y++) o.data.set(g.data.subarray(y * g.width + x0, y * g.width + x1), y * w);
  return o;
}

// front end + measure assembly of one page image; clefs: staves whose clef was read
function analyse(gray, idx, frOpts, dewarp = true) {
  let fr = front(gray, frOpts);
  if (!fr.staves.length) return { fr, asm: null, n: 0, read: 0 };
  let asm = assemblePage(fr, idx);
  // a photographed / curled page whose reading came out broken: read it again dewarped (src/cv.js);
  // not a two-up spread or one of its halves (the gutter's curl misleads it there)
  const dw = dewarp && spreadGutter(fr) == null && dewarpReading(fr, asm, (g) => { const f = front(g, Object.assign({}, frOpts, { preclean: false })); return f.staves.length ? { fr: f, asm: assemblePage(f, idx) } : null; });
  if (dw) ({ fr, asm } = dw);
  let n = 0, read = 0;
  for (const sy of asm.systems) for (const s of sy.staves) { n++; if (!s.hdr.clefGuessed) read++; }
  // header glyphs the parse left unread (time-signature numbers, unread clefs): template
  // matching in src/cv.js; after the count above, so orientation still judges the plain reading
  readHeaders(fr, asm);
  return { fr, asm, n, read };
}

// Orientation: an upright page has staves and reads its clefs at the start of
// each staff. A page with no staves is tried turned a quarter either way; a
// page whose clefs mostly fail to read is tried upside down, and the turn
// that reads clearly more clefs wins.
function analyseOriented(gray, idx, frOpts) {
  let best = { ...analyse(gray, idx, frOpts), turns: 0, gray };
  // a front end that settles the orientation itself (it reports it) is not
  // second-guessed: that would only repeat its work
  if (best.fr && best.fr.orientation !== undefined) return best;
  const better = (a, b) => a.read > b.read || (a.read === b.read && a.n > b.n);
  if (!best.n && gray.width > 50 && gray.height > 50) {
    for (const t of [1, 3]) {
      const g = turnGray(gray, t);
      const c = { ...analyse(g, idx, frOpts), turns: t, gray: g };
      if (better(c, best)) best = c;
      if (best.n && best.read >= 0.5 * best.n) break;
    }
  }
  if (best.n && best.read < 0.5 * best.n) {
    const g = turnGray(best.gray, 2);
    const c = { ...analyse(g, idx, frOpts), turns: (best.turns + 2) % 4, gray: g };
    if (c.n && c.read >= 0.5 * c.n && c.read >= best.read + Math.max(1, 0.25 * best.n)) best = c;
  }
  return best;
}

// Two-up spread: the staves fall into a left and a right column that do not
// overlap, each narrower than 60% of the sheet. Returns the gutter x or null.
function spreadGutter(fr) {
  const st = fr.staves.slice().sort((a, b) => a.left - b.left);
  if (st.length < 4) return null;
  const W = fr.gray.width;
  for (let i = 2; i <= st.length - 2; i++) {
    const L = st.slice(0, i), R = st.slice(i);
    const lr = Math.max(...L.map(s => s.right)), rl = Math.min(...R.map(s => s.left));
    if (lr >= rl - 2 * fr.ss) continue;
    const wl = lr - Math.min(...L.map(s => s.left)), wr = Math.max(...R.map(s => s.right)) - rl;
    if (wl < 0.6 * W && wr < 0.6 * W && Math.min(wl, wr) > 0.25 * W) return Math.round((lr + rl) / 2);
  }
  return null;
}

function createConverter(opts = {}) {
  const progress = opts.onProgress || (() => {});
  const pages = [];
  const lyricsBySystem = {};
  const warnings = [];

  async function readPageLyrics(entry, label, i, n) {
    if (!opts.ocr) return;
    progress(`${label}: reading lyrics`, { stage: 'lyrics', page: i, pages: n });
    try {
      const lyr = await readLyrics(entry.fr, opts.ocr, (d, m) => progress(`${label}: reading lyrics (${d}/${m} lines)`, { stage: 'lyrics', page: i, pages: n }));
      for (const k in lyr) lyricsBySystem[entry.index + ':' + k] = lyr[k];
    } catch (e) { warnings.push(`Lyrics OCR failed: ${e.message}`); }
    // titles, credits, instrument names, tempo and expression text
    progress(`${label}: reading titles and text`, { stage: 'lyrics', page: i, pages: n });
    try { await readPageText(entry.fr, pageMarks(entry.fr, entry.asm), opts.ocr); } catch (e) { warnings.push(`Text OCR failed: ${e.message}`); }
  }

  return {
    // returns the page entry ({fr, asm, index}) to show, or null when the page has no staves
    async addPage(gray, i, n) {
      const label = `Page ${i + 1}${n ? '/' + n : ''}`;
      progress(`${label}: finding staves and notes`, { stage: 'cleanup', page: i, pages: n });
      const frOpts = { onProgress: (m, info) => progress(`${label}: ${m}`, Object.assign({ page: i, pages: n }, info || {})) };
      let a;
      try { a = analyseOriented(gray, i, frOpts); } catch (e) { warnings.push(`Page ${i + 1}: image analysis failed (${e.message}).`); return null; }
      (a.fr.warnings || []).forEach(w => warnings.push(`Page ${i + 1}: ${w}`));
      if (!a.n) return null;
      if (a.turns) warnings.push(`Page ${i + 1}: the scan was ${a.turns === 2 ? 'upside down' : 'turned sideways'}; read it turned ${a.turns === 2 ? 'the right way up' : a.turns === 1 ? 'a quarter clockwise' : 'a quarter anticlockwise'}.`);
      progress(`${label}: reading note symbols`, { stage: 'notes', page: i, pages: n });
      const gx = spreadGutter(a.fr);
      if (gx != null) {
        // read each half as its own page; the whole sheet stays the page shown
        const g = a.fr.gray, halves = [];
        for (const [k, x0, x1] of [[0, 0, gx], [1, gx, g.width]]) {
          let h;
          try { h = analyse(cropGray(g, x0, x1), i + 0.5 * k, frOpts, false); } catch (e) { continue; }
          if (!h.n) continue;
          const entry = { fr: h.fr, asm: h.asm, index: i + 0.5 * k };
          pages.push(entry);
          halves.push(entry);
          await readPageLyrics(entry, `${label} (${k ? 'right' : 'left'} half)`, i, n);
        }
        if (halves.length) {
          warnings.push(`Page ${i + 1}: two book pages side by side; read the left page, then the right.`);
          return { fr: a.fr, asm: a.asm, index: i, spread: halves };
        }
      }
      const entry = { fr: a.fr, asm: a.asm, index: i };
      pages.push(entry);
      await readPageLyrics(entry, label, i, n);
      return entry;
    },
    // big page buffers nothing after the page step reads (buildScore needs fr.R and asm.comps)
    releasePage(entry) {
      if (!entry || !entry.fr) return;
      const fr = entry.fr;
      if (fr.gray) fr.gray = { width: fr.gray.width, height: fr.gray.height, data: null, released: true };
      fr.B = null;
      fr.L = null;
    },
    finish() {
      progress('Building parts', { stage: 'parts' });
      let score;
      try { score = buildScore(pages, lyricsBySystem, { ocr: !!opts.ocr, copyLyrics: !!opts.copyLyrics, debug: opts.debug }); }
      catch (e) { score = { parts: [], warnings: ['Assembly failed: ' + e.message], xml: '' }; }
      // show only the text lines that were attached to notes (stanza text printed
      // below the music, titles and dynamics are not underlay)
      if (score.layout && Object.values(lyricsBySystem).some(l => l.some(v => v.used))) {
        for (const k in lyricsBySystem) lyricsBySystem[k] = lyricsBySystem[k].filter(v => v.used);
      }
      if (!pages.length) warnings.push('No staves were detected. Try a cleaner or higher-resolution scan.');
      return { pages, score, lyricsBySystem, warnings: warnings.concat(score.warnings || []) };
    },
  };
}

async function convert(grayPages, opts = {}) {
  const c = createConverter(opts);
  for (let i = 0; i < grayPages.length; i++) {
    await c.addPage(grayPages[i], i, grayPages.length);
    await tick();
  }
  return c.finish();
}

const tick = () => new Promise(r => setTimeout(r, 0));

module.exports = { convert, createConverter, _turnGray: turnGray, _spreadGutter: spreadGutter };
