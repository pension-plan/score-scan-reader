'use strict';
// Lyric text rows: find them under each staff of a system (between staves and
// below the last one), crop, OCR (injected engine), split into syllables.
// Rows are screened twice: by their ink (stems, ties, fermatas are not text)
// and by what OCR reads (lyric rows are mostly confident lower-case words).
// Verses are numbered top-down per staff; a stack under the bottom staff that
// starts with a printed "2." is stanza text set after the music and dropped.
// Rows are found by connected components and baselines (spike strips.js),
// measured along the staff lines (curled / keystoned pages), cleaned of scan
// specks and, on heavy-stroke pages, thinned before OCR. Text above a staff
// is kept when it follows that staff's notes (row.above, band = that staff).
const { makeGray } = require('./image');
const { labelComponents } = require('./cc');

const DEFAULTS = {
  widen: true,        // stretch word gaps before OCR (stops "workswith" merges)
  gapSp: 0.3,         // min blank run (staff spaces) that counts as a word gap
  addSp: 0.8,         // blank columns inserted into each word gap (staff spaces)
  hyGaps: true,       // also open up the gaps either side of a tight hyphen ("Her-ze-leid")
  rules: true,        // erase vertical rules (barlines, brackets, stems) crossing the text row
  targetH: 56,        // OCR crop height in px (incl. padding)
  norm: true,         // contrast-stretch the crop (paper -> white, ink -> black)
  minWordConf: 20,    // words below this confidence are dropped ...
  relaxLow: true,     // ... unless they look like clean words on a confident row
  minLineConf: 50,
  secondPassSlack: 2,  // second OCR pass (ocr.extra, rows with accent marks): kept within this much of the first pass's confidence
  geomCheck: true,    // reject rows whose ink does not look like a text line (stems, fermatas, ties)
  goodFrac: 0.4,      // share of tokens that must be confident word-like tokens ...
  goodAbs: 6,         // ... or at least this many of them
  lastStaffSp: 14,    // how far below the last staff of a system verse rows may reach ...
  maxRowGapSp: 1.5,   // ... provided each row follows the previous one within this gap
  ccLines: true,      // find lines by components + baselines and OCR masked strips (spike strips.js)
  attachedLetters: true, // keep text-zone pixels of letters that touch stems / notes
  ccLastStaffSp: 24,  // component lines: depth searched under a system's last staff (stacked verses stay contiguous)
  maxGapFont: 0,      // close up word gaps wider than this share of the font size (0 = off; hurt here)
  wordGapFont: 0,     // ... separate cap for gaps not next to a hyphen (0 = same)
  titleCheck: true,   // reject captions: title-case or bracketed lines, oversized type
  partLabels: true,   // OCR the part names left of the first system -> fr.partLabels
  stanzas: true,      // OCR stanza text printed below the last system -> fr.stanzas
  targetCap: 28,      // OCR scale: cap height in px (component lines)
  splitByNotes: true, // split tokens that span several note onsets (unprinted hyphens, merged words)
  gluedWords: true,   // component lines: whole words glued into one component vote as letters (bold type, thick copies)
  despeck: true,      // component lines: drop isolated specks from the OCR strip
  dropJunk: true,     // drop unsure short tokens without a vowel ("t", "CL": stems and specks read as letters)
  followStaff: true,  // component lines: measure text baselines along the staff lines (curled / keystoned pages)
  aboveLines: true,   // text rows above a staff (and the lower rows between staves) that follow that staff's notes
  aboveSp: 7,         // ... searched up to this many staff spaces above the system's top staff
  verseGaps: true,    // verse numbers: count rows by line pitch and printed stanza numbers (rows OCR lost keep their number free)
  thinAt: 0.245,      // thin text strokes before OCR when the page's stroke width / letter height exceeds this (0 = off)
  lang: null,         // underlay language for syllable rules ('en' | 'de' | 'la'); null = detect
};

// Returns [{band, sys, y0, y1, x0, x1}] text-line boxes in deskewed page coords.
function findTextLines(fr, sysIdx, nextTop, opts) {
  const o = { ...DEFAULTS, ...(opts || {}) };
  const { B, staves } = fr;
  const sys = fr.systems[sysIdx];
  const w = B.width;
  const out = [];
  sys.forEach((si, k) => {
    const st = staves[si];
    const sp = st.space;
    const xL = st.left, xR = st.right;
    const yA = Math.round(Math.max(...[xL, (xL + xR) / 2, xR].map(x => st.yAt(4, x))) + 1.2 * sp);
    let yB, ySoft = Infinity;
    if (k + 1 < sys.length) yB = Math.round(Math.min(...[xL, (xL + xR) / 2, xR].map(x => staves[sys[k + 1]].yAt(0, x))) - 2.0 * sp);
    else {
      // below the last staff: rows must start within 6 sp, but a stack of
      // verses may run further down as long as the rows stay contiguous
      yB = Math.round(Math.min(nextTop - 2.5 * sp, yA + o.lastStaffSp * sp, B.height - 1));
      ySoft = yA + 6 * sp;
    }
    if (yB - yA < 0.8 * sp) return;
    const first = out.length;
    // row profile of small-ink content (text) within the staff's x range
    const prof = [];
    for (let y = yA; y <= yB; y++) { let n = 0; for (let x = xL; x <= xR; x++) n += B.data[y * w + x]; prof.push(n); }
    const thr = Math.max(3, 0.004 * (xR - xL));
    let y = 0;
    while (y < prof.length) {
      if (prof[y] < thr) { y++; continue; }
      let y1 = y; while (y1 < prof.length && prof[y1] >= thr * 0.5) y1++;
      const hgt = y1 - y;
      if (hgt >= 0.6 * sp && hgt <= 2.6 * sp) out.push({ band: k, sys: sysIdx, last: k === sys.length - 1, y0: yA + y, y1: yA + y1, x0: xL, x1: xR, sp });
      else if (hgt > 2.6 * sp) {
        // tightly stacked verses: split the block at the profile valleys
        let mx = 0; for (let i = y; i < y1; i++) mx = Math.max(mx, prof[i]);
        const t2 = 0.18 * mx;
        for (let i = y; i < y1;) {
          if (prof[i] < t2) { i++; continue; }
          let j = i; while (j < y1 && prof[j] >= t2) j++;
          if (j - i >= 0.5 * sp && j - i <= 2.6 * sp) {
            const a = Math.max(y, i - Math.round(0.25 * sp)), b = Math.min(y1, j + Math.round(0.25 * sp));
            out.push({ band: k, sys: sysIdx, last: k === sys.length - 1, y0: yA + a, y1: yA + b, x0: xL, x1: xR, sp });
          }
          i = j;
        }
      }
      y = y1;
    }
    if (ySoft < Infinity) {
      let keep = first, prevEnd = -Infinity;
      for (let i = first; i < out.length; i++) {
        const r = out[i];
        if (r.y0 > ySoft && r.y0 - prevEnd > o.maxRowGapSp * sp) break;
        prevEnd = r.y1; keep = i + 1;
      }
      out.length = keep;
    }
  });
  return out;
}

// ---- component-based lyric lines (port of spike/ocr/src/strips.js) -------
// In each band under a staff, connected components that do not touch the band
// edges (those hang off the staff: notes, stems, beams) and are letter sized
// vote for baselines; each baseline with enough letters is a text line whose
// members are the components between ascender and descender height. The OCR
// strip keeps member pixels only (stems and noteheads poking into the text are
// masked out). Flat members are hyphens (mid height) or extenders (baseline).
const median = (a) => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[s.length >> 1]; };

// prevBot: page y where the previous system's music ends (0 for the first):
// with o.aboveLines the band above the system's top staff is searched too
// (text printed above a staff: rows marked above, nearest the staff first).
function findTextLinesCC(fr, sysIdx, nextTop, o, prevBot = 0) {
  const { B, gray, staves } = fr;
  const sys = fr.systems[sysIdx];
  const W = B.width, H = B.height;
  const out = [];
  const specs = sys.map((si, k) => ({ k, above: false }));
  if (o.aboveLines) specs.push({ k: 0, above: true });
  specs.forEach(({ k, above }) => {
    const si = sys[k];
    const st = staves[si], sp = st.space;
    const xs = [st.left, (st.left + st.right) / 2, st.right];
    const last = !above && k === sys.length - 1;
    let y0, y1;
    if (above) {
      const top = Math.min(...xs.map(x => st.yAt(0, x)));
      y1 = Math.round(top - 0.4 * sp);
      y0 = Math.round(Math.max(prevBot, top - o.aboveSp * sp, 0));
    } else {
      y0 = Math.round(Math.max(...xs.map(x => st.yAt(4, x))) + 0.4 * sp);
      y1 = Math.round(last ? Math.min(nextTop - 1.0 * sp, y0 + o.ccLastStaffSp * sp, H - 1)
        : Math.min(...xs.map(x => staves[sys[k + 1]].yAt(0, x))) - 0.4 * sp);
    }
    if (y1 - y0 < 1.5 * sp) return;
    const x0 = Math.max(0, Math.round(st.left - 2 * sp)), x1 = Math.min(W - 1, Math.round(st.right + 1 * sp));
    const bw = x1 - x0 + 1, bh = y1 - y0 + 1;
    const band = { width: bw, height: bh, data: new Uint8Array(bw * bh) };
    for (let y = 0; y < bh; y++) band.data.set(B.data.subarray((y0 + y) * W + x0, (y0 + y) * W + x0 + bw), y * bw);
    const { labels, comps } = labelComponents(band);
    const cand = comps.filter(c => c.y0 > 0 && c.y1 < bh - 1 && c.area >= 3 && c.y1 - c.y0 + 1 <= 4 * sp && c.x1 - c.x0 + 1 <= 30 * sp);
    const candSet = new Set(cand);
    // letter-sized components; in bold type or thick photocopies the letters
    // of a word run together into one component: wide, but solid like text
    // (slurs, ties and hairpins are thin strokes with little fill)
    const letters = cand.filter(c => {
      const h = c.y1 - c.y0 + 1, w = c.x1 - c.x0 + 1;
      if (h < 0.45 * sp || h > 3.2 * sp || w < 0.12 * sp) return false;
      return w <= 4 * sp || (o.gluedWords && w <= 9 * h && c.area >= 0.3 * w * h);
    });
    if (letters.length < 4) return;
    // a glued word's bottom is its lowest descender: its baseline is the
    // bottom most of its columns share
    for (const c of letters) {
      c.base = c.y1;
      if (!o.gluedWords || c.x1 - c.x0 + 1 <= 1.5 * (c.y1 - c.y0 + 1)) continue;
      const cnt = new Map();
      for (let x = c.x0; x <= c.x1; x++) {
        for (let y = c.y1; y >= c.y0; y--) if (labels[y * bw + x] === c.id) { cnt.set(y, (cnt.get(y) || 0) + 1); break; }
      }
      let by = c.y1, bn = 0;
      for (const [y, n] of cnt) if (n > bn || (n === bn && y > by)) { by = y; bn = n; }
      c.base = by;
    }
    // text lines run parallel to the staves: on a curled or keystoned page
    // the staff lines tilt differently from one staff to the next, so y is
    // measured from a line that follows the staff above (and, between two
    // staves, blends into the one below) instead of a horizontal
    const xm = (st.left + st.right) / 2, nb = last || above ? null : staves[sys[k + 1]];
    const refLine = above ? 0 : 4;
    const yAm = st.yAt(refLine, xm), yBm = nb ? nb.yAt(0, xm) : 0;
    const shiftAt = (xp, yp) => {
      const a = st.yAt(refLine, xp) - yAm;
      if (!nb || yBm <= yAm) return a;
      const t = Math.max(0, Math.min(1, (yp - yAm) / (yBm - yAm)));
      return (1 - t) * a + t * (nb.yAt(0, xp) - yBm);
    };
    let tilt = false;
    if (o.followStaff) for (const xp of [x0, x1]) for (const yp of [y0, y1]) if (Math.abs(shiftAt(xp, yp)) > 0.5 * sp) tilt = true;
    for (const c of cand) {
      c.sh = tilt ? shiftAt(x0 + (c.x0 + c.x1) / 2, y0 + (c.base ?? c.y1)) : 0;
      c.sy0 = c.y0 - c.sh; c.sy1 = c.y1 - c.sh; c.sb = (c.base ?? c.y1) - c.sh;
    }
    const hist = new Float64Array(bh + 1);
    for (const c of letters) { const b = Math.round(c.sb); if (b >= 0 && b <= bh) hist[b]++; }
    const R = Math.max(1, Math.round(0.15 * sp)), sm = new Float64Array(bh + 1);
    for (let y = 0; y <= bh; y++) { let s = 0; for (let d = -R; d <= R; d++) { const yy = y + d; if (yy >= 0 && yy <= bh) s += hist[yy]; } sm[y] = s; }
    const peaks = [];
    for (const y of [...sm.keys()].sort((a, b) => sm[b] - sm[a])) {
      if (sm[y] < 4) break;
      if (peaks.some(p => Math.abs(p - y) < 1.4 * sp)) continue;
      peaks.push(y);
    }
    peaks.sort((a, b) => a - b);
    const lines = [];
    for (const bl of peaks) {
      const core = letters.filter(c => Math.abs(c.sb - bl) <= 0.25 * sp + 1);
      if (core.length < 4) continue;
      const hs = core.map(c => c.base - c.y0 + 1).sort((a, b) => a - b);
      const xh = median(hs.slice(0, Math.max(1, hs.length >> 1))), tall = median(hs.slice(hs.length >> 1));
      if (tall < 0.6 * sp || median(core.map(c => c.area)) < 0.15 * sp * sp) continue;   // rows of specks
      lines.push({ bl, xh, tall, core, mem: [] });
    }
    if (!lines.length) return;
    // members: each candidate goes to the line whose window holds it and whose baseline is nearest its bottom
    for (const c of cand) {
      let best = null, bd = Infinity;
      for (const ln of lines) {
        if (c.sy0 < ln.bl - 1.9 * ln.tall || c.sy1 > ln.bl + 0.6 * ln.tall || c.y1 - c.y0 + 1 > 2.2 * ln.tall) continue;
        const d = Math.abs(c.sb - ln.bl);
        if (d < bd) { bd = d; best = ln; }
      }
      if (best) best.mem.push(c);
    }
    // scan specks: tiny blobs that are neither a dot or accent over a letter
    // (i, ä, é) nor punctuation on the baseline right after a letter; they
    // make tesseract drop whole lines. Flat hyphens and extenders are kept.
    if (o.despeck) for (const ln of lines) {
      const T = ln.tall, bl = ln.bl, xh = ln.xh;
      const big = ln.mem.filter(c => c.y1 - c.y0 + 1 >= 0.45 * T || c.x1 - c.x0 + 1 >= 0.45 * T);
      ln.mem = ln.mem.filter(c => {
        const ch = c.y1 - c.y0 + 1, cw = c.x1 - c.x0 + 1;
        if (Math.max(ch, cw) >= 0.3 * T || cw >= 1.6 * ch) return true;
        if (c.sy1 < bl - 0.55 * xh) return big.some(b => b.x0 - c.x1 <= 0.2 * T && c.x0 - b.x1 <= 0.2 * T);
        if (Math.abs(c.sy1 - bl) <= 0.2 * xh + 1) return big.some(b => c.x0 - b.x1 >= -1 && c.x0 - b.x1 <= 0.3 * T);
        return false;
      });
    }
    const stW = st.right - st.left;
    let prevBl = null;
    // above a staff the rows are taken from the staff upwards
    if (above) lines.reverse();
    for (const ln of lines) {
      const mem = ln.mem;
      if (!mem.length) continue;
      const lx0 = Math.min(...mem.map(c => c.x0)), lx1 = Math.max(...mem.map(c => c.x1));
      if (lx1 - lx0 < 0.2 * stW && ln.core.length < 8) continue;
      // under the last staff: the first line starts within 7 sp, later ones follow on
      if (last && (prevBl == null ? ln.bl > 7 * sp + ln.tall : ln.bl - prevBl > 3.2 * sp)) break;
      // above the top staff: the first line ends within 6 sp of it, more follow upwards
      if (above && (prevBl == null ? bh - ln.bl > 6 * sp : prevBl - ln.bl > 3.2 * sp)) break;
      // text above a staff spans most of it (titles and tempo marks do not)
      if (above && lx1 - lx0 < 0.5 * stW) continue;
      prevBl = ln.bl;
      const hyphens = [], extenders = [];
      for (const c of mem) {
        const ch = c.y1 - c.y0 + 1, cw = c.x1 - c.x0 + 1, cy = (c.sy0 + c.sy1 + 1) / 2;
        if (ch <= Math.max(2, 0.4 * ln.xh) && cw >= 1.6 * ch) {
          if (cy < ln.bl - 0.15 * ln.xh && cy > ln.bl - 0.95 * ln.xh && cw <= 3.5 * ln.xh) { hyphens.push({ x0: x0 + c.x0, x1: x0 + c.x1 + 1 }); c.hy = true; }
          else if (Math.abs(cy - ln.bl) <= 0.3 * ln.xh + 1 && cw >= 1.2 * ln.xh) { extenders.push({ x0: x0 + c.x0, x1: x0 + c.x1 + 1 }); c.ext = true; }
        }
      }
      // masked strip: member pixels (dilated by 1 px for the soft glyph edges) from the gray page
      const pad = Math.max(2, Math.round(0.4 * ln.xh));
      const sx0 = Math.max(0, lx0 - pad), sx1 = Math.min(bw - 1, lx1 + pad);
      // (straightened rows may reach past the band's edges where it tilts)
      const sy0 = Math.max(tilt ? -bh : 0, Math.round(Math.min(ln.bl - 1.6 * ln.tall, ...mem.map(c => c.sy0))) - 2);
      const sy1 = Math.min(tilt ? 2 * bh : bh - 1, Math.round(Math.max(ln.bl + 0.5 * ln.tall, ...mem.map(c => c.sy1))) + 2);
      const SW = sx1 - sx0 + 1, SH = sy1 - sy0 + 1;
      // per band column: rows the (straightened) line is shifted by
      const lsh = new Int32Array(bw);
      if (tilt) for (let x = 0; x < bw; x++) lsh[x] = Math.round(shiftAt(x0 + x, y0 + ln.bl));
      const lab = (x, y) => { const yy = y + lsh[x]; return yy >= 0 && yy < bh ? labels[yy * bw + x] : 0; };
      const keep = new Set(mem.filter(c => !c.ext).map(c => c.id));
      // letters touching a stem or note hang off the staff as one component:
      // keep such components' pixels inside the text zone, minus thin
      // vertical strokes crossing the whole zone (stems, barlines)
      const zt = Math.round(ln.bl - 1.15 * ln.tall), zb = Math.round(ln.bl + 0.5 * ln.tall), zh = zb - zt + 1;
      const part = new Map();   // label -> Set of erased columns (band x)
      if (o.attachedLetters) for (const c of comps) {
        if (candSet.has(c) || c.y1 < zt + lsh[c.x0] - 1 || c.y0 > zb + lsh[c.x0] + 1 || c.x1 < lx0 || c.x0 > lx1) continue;
        if (c.y1 < zt + Math.min(lsh[c.x0], lsh[c.x1]) || c.y0 > zb + Math.max(lsh[c.x0], lsh[c.x1])) continue;
        const colFull = [];
        for (let x = c.x0; x <= c.x1; x++) {
          let run = 0, best = 0;
          for (let y = zt; y <= zb; y++) { if (lab(x, y) === c.id) { run++; if (run > best) best = run; } else run = 0; }
          colFull.push(best >= 0.9 * zh);
        }
        const erase = new Set();
        for (let i = 0; i < colFull.length;) {
          if (!colFull[i]) { i++; continue; }
          let j = i; while (j < colFull.length && colFull[j]) j++;
          if (j - i <= Math.max(3, 0.35 * sp)) for (let q = i - 1; q <= j; q++) erase.add(c.x0 + q);
          i = j;
        }
        part.set(c.id, erase);
      }
      const mask = new Uint8Array(SW * SH);
      for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
        const l = lab(sx0 + x, sy0 + y);
        if (!l) continue;
        if (keep.has(l)) mask[y * SW + x] = 1;
        else if (part.has(l) && sy0 + y >= zt && sy0 + y <= zb && !part.get(l).has(sx0 + x)) mask[y * SW + x] = 1;
      }
      const data = new Uint8ClampedArray(SW * SH).fill(255);
      for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
        let m = mask[y * SW + x];
        if (!m) {
          if (lab(sx0 + x, sy0 + y)) continue;   // ink of another component
          for (let dy = -1; dy <= 1 && !m; dy++) for (let dx = -1; dx <= 1 && !m; dx++) {
            const yy = y + dy, xx = x + dx;
            if (yy >= 0 && yy < SH && xx >= 0 && xx < SW && mask[yy * SW + xx]) m = 1;
          }
        }
        const gy = y0 + sy0 + y + lsh[sx0 + x];
        if (m && gy >= 0 && gy < H) data[y * SW + x] = gray.data[gy * W + x0 + sx0 + x];
      }
      const sw = strokeWidth(mask, SW, SH);
      out.push({
        band: k, sys: sysIdx, last, above, sp, x0: st.left, x1: st.right, y0: y0 + sy0, y1: y0 + sy1,
        baseline: y0 + ln.bl, xh: ln.xh, tall: ln.tall, hyphens, extenders, sw,
        strip: { width: SW, height: SH, data, x0: x0 + sx0, y0: y0 + sy0, mask },
      });
    }
  });
  return out;
}

// typical stroke width of the text in a mask: median length of the
// horizontal ink runs (runs across vertical strokes dominate in text)
function strokeWidth(mask, w, h) {
  const hist = new Int32Array(64);
  let n = 0;
  for (let y = 0; y < h; y++) {
    let run = 0;
    for (let x = 0; x <= w; x++) {
      if (x < w && mask[y * w + x]) { run++; continue; }
      if (run) { hist[Math.min(63, run)]++; n++; run = 0; }
    }
  }
  if (!n) return 0;
  let acc = 0;
  for (let i = 1; i < 64; i++) { acc += hist[i]; if (acc >= n / 2) return i; }
  return 63;
}

// row analysis on a masked strip (same shape as analyseRow's result)
function stripRow(ln) {
  const { width: n, height: Hh, mask } = ln.strip;
  const ink = new Int32Array(n), rule = new Uint8Array(n);
  for (let x = 0; x < n; x++) { let c = 0; for (let y = 0; y < Hh; y++) c += mask[y * n + x]; ink[x] = c; }
  const clusters = [];
  for (let i = 0; i < n;) {
    if (!ink[i]) { i++; continue; }
    let j = i; while (j < n && ink[j]) j++;
    clusters.push([i, j]); i = j;
  }
  const hy = clusters.map(([a, b]) => ln.hyphens.some(h => h.x0 - ln.strip.x0 >= a - 1 && h.x1 - ln.strip.x0 <= b + 1 && b - a <= h.x1 - h.x0 + 2));
  let cov = 0; for (const [a, b] of clusters) cov += b - a;
  return { xa: 0, ya: 0, yb: Hh - 1, n, ink, rule, clusters, hy, cov: cov / Math.max(1, n) };
}

// Column analysis of a text row on the binary page: vertical rules that cross
// the whole (padded) row, blank runs between glyph clusters, and simple shape
// statistics used to reject rows that are stems / ties / fermatas, not text.
function analyseRow(B, ln, pad) {
  const w = B.width;
  const ya = Math.max(0, ln.y0 - pad), yb = Math.min(B.height - 1, ln.y1 + pad);
  const xa = ln.x0, xb = ln.x1;
  const H = yb - ya + 1;
  const n = xb - xa + 1;
  const ink = new Int32Array(n), rule = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const x = xa + i;
    let c = 0, run = 0, best = 0;
    for (let y = ya; y <= yb; y++) {
      if (B.data[y * w + x]) { c++; run++; if (run > best) best = run; } else run = 0;
    }
    ink[i] = c;
    if (best >= 0.85 * H) rule[i] = 1;
  }
  // a rule is thin: drop marks on columns that belong to wide solid blobs
  for (let i = 0; i < n;) {
    if (!rule[i]) { i++; continue; }
    let j = i; while (j < n && rule[j]) j++;
    if (j - i > Math.max(3, 0.35 * ln.sp)) for (let k = i; k < j; k++) rule[k] = 0;
    i = j;
  }
  // clusters of inked columns (rules count as blank)
  const clusters = [];
  for (let i = 0; i < n;) {
    if (ink[i] < 1 || rule[i]) { i++; continue; }
    let j = i; while (j < n && ink[j] >= 1 && !rule[j]) j++;
    clusters.push([i, j]);
    i = j;
  }
  let cov = 0; for (const [a, b] of clusters) cov += b - a;
  // hyphen-like clusters: a short thin dash in the middle band of the row
  const hy = clusters.map(([a, b]) => {
    const wdt = b - a;
    if (wdt < 0.25 * ln.sp || wdt > 1.3 * ln.sp) return false;
    let top = Infinity, bot = -1;
    for (let x = xa + a; x < xa + b; x++) for (let y = ya; y <= yb; y++) if (B.data[y * w + x]) { if (y < top) top = y; if (y > bot) bot = y; }
    if (bot < 0) return false;
    const mid = (top + bot) / 2, rel = (mid - ln.y0) / Math.max(1, ln.y1 - ln.y0);
    return bot - top + 1 <= Math.max(3, 0.22 * ln.sp) && rel > 0.3 && rel < 0.85;
  });
  return { xa, ya, yb, n, ink, rule, clusters, hy, cov: cov / n };
}

// Build the OCR crop: blank vertical rules, stretch word gaps (tesseract
// otherwise glues tightly set underlay words together), contrast-stretch,
// scale. Returns {img, toPage(xCrop) -> page x}.
function buildCrop(g, row, ln, o) {
  const gapMin = Math.max(3, o.gapSp * ln.sp);
  const add = o.widen ? Math.round(o.addSp * ln.sp) : 0;
  // word gaps wider than ~half the font size are closed up (syllables spread
  // under the notes break tesseract's word segmentation and LSTM context)
  const cap = o.maxGapFont && ln.tall ? Math.max(gapMin + add, Math.round(o.maxGapFont * ln.tall / 0.7)) : Infinity;
  // segments of source columns, with inserted blank columns before each
  const segs = []; // {sx, len, before}
  const { clusters, n } = row;
  if ((!o.widen && cap === Infinity) || !clusters.length) segs.push({ sx: 0, len: n, before: 0 });
  else {
    let start = 0, ins = 0;
    for (let c = 1; c < clusters.length; c++) {
      const a = clusters[c - 1][1], b = clusters[c][0], gap = b - a;
      if (gap >= gapMin || (o.hyGaps && (row.hy[c] || row.hy[c - 1]))) {
        const hyAdj = row.hy[c] || row.hy[c - 1];
        const cp = hyAdj ? cap : (o.wordGapFont && ln.tall ? Math.max(cap, Math.round(o.wordGapFont * ln.tall / 0.7)) : cap);
        const keep = Math.min(gap, cp), l = Math.ceil(keep / 2);
        segs.push({ sx: start, len: a + l - start, before: ins });
        start = b - (keep - l);
        ins = Math.max(0, Math.min(add, cp - keep));
      }
    }
    segs.push({ sx: start, len: n - start, before: ins });
  }
  const srcW = segs.reduce((a, s) => a + s.len + s.before, 0);
  const srcH = row.yb - row.ya + 1;
  const scale = Math.min(3, Math.max(0.5, ln.tall && o.targetCap ? o.targetCap / ln.tall : o.targetH / srcH));
  // source column for each virtual column (-1 = inserted blank)
  const vcol = new Int32Array(srcW);
  let v = 0;
  for (const s of segs) {
    for (let k = 0; k < s.before; k++) vcol[v++] = -1;
    for (let k = 0; k < s.len; k++) vcol[v++] = s.sx + k;
  }
  // background level: bright percentile of the row
  const hist = new Int32Array(256);
  for (let y = row.ya; y <= row.yb; y++) for (let i = 0; i < n; i += 2) hist[g.data[y * g.width + row.xa + i]]++;
  let tot = 0; for (let i = 0; i < 256; i++) tot += hist[i];
  let acc = 0, bg = 255; for (let i = 255; i >= 0; i--) { acc += hist[i]; if (acc >= 0.3 * tot) { bg = i; break; } }
  // dark level: ink percentile, for an optional contrast stretch
  acc = 0; let dk = 0; for (let i = 0; i < 256; i++) { acc += hist[i]; if (acc >= 0.02 * tot) { dk = i; break; } }
  const stretch = o.norm && bg - dk > 40;
  const lut = new Uint8ClampedArray(256);
  for (let i = 0; i < 256; i++) lut[i] = stretch ? Math.round(255 * (i - dk) / (bg - dk)) : i;
  const W = Math.max(1, Math.round(srcW * scale)), Hh = Math.max(1, Math.round(srcH * scale));
  const img = makeGray(W, Hh, stretch ? 255 : bg);
  const real = (v) => vcol[v] >= 0 && !(o.rules && row.rule[vcol[v]]);
  for (let x = 0; x < W; x++) {
    const vi = Math.min(srcW - 1, Math.floor(x / scale));
    if (!real(vi)) continue;
    const sx = row.xa + vcol[vi];
    for (let y = 0; y < Hh; y++) {
      const sy = Math.min(g.height - 1, row.ya + Math.floor(y / scale));
      img.data[y * W + x] = lut[g.data[sy * g.width + sx]];
    }
  }
  // heavy strokes (bold type, thick photocopies, blur) make tesseract's
  // line layout drop whole lines: thin them towards a normal weight
  if (ln.thin) maxFilter(img, ln.thin);
  const toPage = (xc) => {
    const vi = Math.max(0, Math.min(srcW - 1, Math.floor(xc / scale)));
    // nearest real column
    for (let d = 0; d < srcW; d++) {
      if (vi + d < srcW && vcol[vi + d] >= 0) return row.xa + vcol[vi + d];
      if (vi - d >= 0 && vcol[vi - d] >= 0) return row.xa + vcol[vi - d];
    }
    return row.xa;
  };
  return { img, toPage, scale };
}

// gray max filter (white grows, dark strokes thin by r px a side), in place
function maxFilter(img, r) {
  const { width: w, height: h, data } = img;
  const tmp = new Uint8ClampedArray(data.length);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let m = 0;
    for (let d = -r; d <= r; d++) { const xx = x + d; if (xx >= 0 && xx < w) m = Math.max(m, data[y * w + xx]); }
    tmp[y * w + x] = m;
  }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let m = 0;
    for (let d = -r; d <= r; d++) { const yy = y + d; if (yy >= 0 && yy < h) m = Math.max(m, tmp[yy * w + x]); }
    data[y * w + x] = m;
  }
}

function cropGray(g, x0, y0, x1, y1, scale) {
  const w = Math.round((x1 - x0) * scale), h = Math.round((y1 - y0) * scale);
  const out = makeGray(w, h, 255);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const sx = Math.min(g.width - 1, Math.round(x0 + x / scale)), sy = Math.min(g.height - 1, Math.round(y0 + y / scale));
    out.data[y * w + x] = g.data[sy * g.width + sx];
  }
  return out;
}

const HY = /[-‐‑‒–—―~]/;
const LETTER = /[A-Za-zÀ-ɏ]/;

// Does an OCR token look like part of a lyric (word, syllable, hyphen, verse number)?
// Two words joined by an elision slur (a small arc under the baseline across
// the gap: "da‿il", one note) become one word with '‿' (score.js splits it
// again around the mark). Words in page coordinates.
function joinElisions(fr, ln, words) {
  const R = fr.R, sp = ln.sp;
  if (!R || !R.data || !sp || words.length < 2) return words;
  const W = R.width, rowH = ln.y1 - ln.y0;
  const y0 = Math.max(0, Math.round(ln.y0 + 0.7 * rowH)), y1 = Math.min(R.height - 1, Math.round(ln.y1 + 1.0 * sp));
  const out = [words[0]];
  for (let i = 1; i < words.length; i++) {
    const a = out[out.length - 1], b = words[i];
    const gap = b.x0 - a.x1;
    if (gap > 1.5 * sp || gap < -0.2 * sp || /[-‐‑‒–—―~]$/.test(a.text) || /^[-‐‑‒–—―~]/.test(b.text)) { out.push(b); continue; }
    // an arc spanning the gap: its own thin component under the baseline (not a
    // descender, which reaches down from a letter above), wider than tall and
    // sagging in the middle (not a straight extender line)
    if (gap > 1.0 * sp) { out.push(b); continue; }
    const cx0 = Math.max(0, Math.round(a.x1 - 0.8 * sp)), cx1 = Math.min(W - 1, Math.round(b.x0 + 0.8 * sp));
    const cw = cx1 - cx0 + 1, ch = y1 - y0 + 1;
    if (cw < 3 || ch < 3) { out.push(b); continue; }
    const crop = { width: cw, height: ch, data: new Uint8Array(cw * ch) };
    for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) crop.data[y * cw + x] = R.data[(y0 + y) * W + cx0 + x] ? 1 : 0;
    const mid = (a.x1 + b.x0) / 2 - cx0;
    const arc = labelComponents(crop).comps.find(c => {
      const w = c.x1 - c.x0 + 1, h = c.y1 - c.y0 + 1;
      return c.y0 > 0 && c.x0 > 0 && c.x1 < cw - 1 && w >= 0.6 * sp && h <= 0.45 * sp && w >= 2.5 * h && c.x0 <= mid && c.x1 >= mid;
    });
    let bowed = false;
    if (arc) {
      const ym = (x) => { let s = 0, n = 0; for (let y = arc.y0; y <= arc.y1; y++) if (crop.data[y * cw + x]) { s += y; n++; } return n ? s / n : null; };
      const l = ym(arc.x0), r = ym(arc.x1), m = ym(Math.round((arc.x0 + arc.x1) / 2));
      bowed = l != null && r != null && m != null && m - Math.min(l, r) >= 1;
    }
    if (bowed) out[out.length - 1] = { ...a, text: a.text.replace(/[,.;:!?]+$/, '') + '‿' + b.text, conf: Math.min(a.conf, b.conf), x1: b.x1, ok: true };
    else out.push(b);
  }
  return out;
}

// Accent marks in a text row image (gray, dark ink): small marks just above a
// letter wider than an i or j (whose dots are not accents): á é ü ñ č and so on.
function accentMarks(img) {
  const w = img.width, h = img.height, bin = { width: w, height: h, data: new Uint8Array(w * h) };
  for (let i = 0; i < w * h; i++) bin.data[i] = img.data[i] < 128 ? 1 : 0;
  const { comps } = labelComponents(bin);
  const hs = comps.filter(c => c.area >= 6).map(c => c.y1 - c.y0 + 1).sort((a, b) => a - b);
  if (hs.length < 4) return 0;
  const med = hs[hs.length >> 1];
  const letters = comps.filter(c => c.y1 - c.y0 + 1 >= 0.6 * med);
  let n = 0;
  for (const m of comps) {
    const mw = m.x1 - m.x0 + 1, mh = m.y1 - m.y0 + 1;
    if (m.area < 3 || mh > 0.45 * med || mw > 0.9 * med) continue;
    const below = letters.find(c => c.y0 > m.y1 && c.y0 - m.y1 <= 0.5 * med && c.x0 <= (m.x0 + m.x1) / 2 && c.x1 >= (m.x0 + m.x1) / 2);
    // a vowel-wide letter (an i or j with its serifs is narrower than 0.7 x-height)
    if (below && below.x1 - below.x0 + 1 >= 0.7 * med && below.y1 - below.y0 + 1 <= 1.1 * med) n++;
  }
  return n;
}

function plausible(t) {
  if (/_/.test(t)) return t.split(/_+/).filter(Boolean).every(plausible);
  const s = t.replace(/^[|_.,;:!?'"“”‘’()]+|[|_.,;:!?'"“”‘’()]+$/g, '');
  if (!s) return false;
  if (/^[-‐‑‒–—―~]+$/.test(s)) return true;
  if (/^\d{1,2}$/.test(s)) return true;
  // letters with optional leading/internal/trailing hyphens and apostrophes; no digits or odd symbols
  return /^[-‐‑‒–—―~]*[\p{L}'’]+(?:[-‐‑‒–—―~]+[\p{L}'’]+)*[-‐‑‒–—―~]*$/u.test(s);
}

// Split OCR words that glue two words together: "thee,Sweet", "song.Let",
// "GodtoThee", "we_on" -> pieces with proportional x extents.
function splitMerged(words) {
  const out = [];
  for (const wd of words) {
    const t = wd.text.replace(/_+/g, ' ').replace(/([,.;:!?])(?=\p{L})/gu, '$1 ').replace(/(\p{Ll})(?=\p{Lu})/gu, '$1 ');
    const parts = t.split(/\s+/).filter(Boolean);
    if (parts.length <= 1) { out.push({ ...wd, text: parts[0] || '' }); continue; }
    const tot = parts.reduce((a, p) => a + p.length, 0);
    let x = wd.x0;
    for (const p of parts) {
      const ww = (wd.x1 - wd.x0) * p.length / tot;
      out.push({ ...wd, text: p, x0: x, x1: x + ww });
      x += ww;
    }
  }
  return out.filter(w => w.text);
}

// confident word-like token: lower case and a vowel (or the words A / I / O)
function goodWord(w, minLen = 1) {
  const letters = w.text.replace(/[^\p{L}]/gu, '');
  if (!w.ok || w.conf < 50 || letters.length < minLen) return false;
  if (/^[AIO]$/.test(letters)) return true;
  return /\p{Ll}/u.test(letters) && /[aeiouyäöüàâæçéèêëîïôœùûÿáíóúñ]/i.test(letters);
}

// words: [{text, conf, x0, x1}] in page coordinates
function toSyllables(words) {
  const toks = [];
  for (const wd of words) {
    let t = wd.text.replace(/[|*^{}\[\]<>«»]/g, '').replace(/_+/g, ' ').trim();
    if (!t) continue;
    // an OCR word can still hold spaces (after "_" removal): split proportionally
    const sub = t.split(/\s+/).filter(Boolean);
    const totalLen = sub.reduce((a, s) => a + s.length, 0) || 1;
    let wx = wd.x0;
    for (const s0 of sub) {
      const sw = (wd.x1 - wd.x0) * s0.length / totalLen;
      // split on hyphens, keeping hyphen markers
      const parts = s0.split(/([-‐‑‒–—―~]+)/).filter(Boolean);
      const letters = parts.reduce((a, p) => a + (HY.test(p[0]) ? 0 : p.length), 0) || 1;
      let cx = wx;
      for (const p of parts) {
        if (HY.test(p[0])) { toks.push({ hy: true }); continue; }
        const ww = sw * p.length / letters;
        toks.push({ text: p, x: cx + ww / 2, x0: cx, x1: cx + ww, conf: wd.conf });
        cx += ww;
      }
      wx += sw;
    }
  }

  // drop leading verse number like "1." / "2" / "3.O" (number glued to the first word)
  // (scan noise such as a bracket read as "Wi" may precede it: drop that too)
  let number = null, numberConf = 0;
  for (let i = 0; i < Math.min(3, toks.length); i++) {
    if (toks[i].hy) continue;
    const m = toks[i].text.match(/^([1-9][0-9]?)[.,:]\s*(.*)$/) || toks[i].text.match(/^([1-9][0-9]?)$/);
    const roman = /^[IVX]{1,3}[.,]$/.test(toks[i].text);
    if (!m && !roman) continue;
    if (i > 0 && !(m && /[.,:]/.test(toks[i].text)) && !roman) continue; // bare digit later in the row: not a verse number
    if (m) { number = parseInt(m[1], 10); numberConf = toks[i].conf; }
    const rest = m && m[2] && LETTER.test(m[2]) ? { ...toks[i], text: m[2] } : null;
    toks.splice(0, i + 1);
    if (rest) toks.unshift(rest);
    break;
  }
  // a language tag after the stanza number ("1. EN Fairest", multilingual hymnals)
  // (also after a misread number: "i. EN Fairest")
  const TAG = /^(EN|DE|DA|SV|NO|NL|FR|IT|LA|ES|FI|IS|CY|PL|CS|HU|PT)$/;
  if (number != null && toks[0] && !toks[0].hy && TAG.test(toks[0].text)) toks.shift();
  else if (number == null && toks.length > 3 && !toks[1].hy && TAG.test(toks[1].text) && !toks[0].hy && !/\p{L}{2}/u.test(toks[0].text)) toks.splice(0, 2);
  // a lone "1" / "0" inside a line is the word I / O (verse numbers are handled above)
  for (const t of toks) if (!t.hy && /^[10][,.;:!?]?$/.test(t.text)) t.text = (t.text[0] === '1' ? 'I' : 'O') + t.text.slice(1);
  const syl = [];
  for (let i = 0; i < toks.length; i++) {
    const t = toks[i];
    if (t.hy) continue;
    if (!LETTER.test(t.text)) continue;
    const hyBefore = i > 0 && toks[i - 1].hy && syl.length;
    const hyAfter = i + 1 < toks.length && toks[i + 1].hy;
    const syllabic = hyBefore ? (hyAfter ? 'middle' : 'end') : (hyAfter ? 'begin' : 'single');
    syl.push({ text: t.text.replace(/^[^\p{L}'’]+|[^\p{L}'’!?,.;:]+$/gu, ''), x: t.x, x0: t.x0, x1: t.x1, syllabic, conf: t.conf });
  }
  return { number, numberConf, syllables: syl.filter(s => s.text) };
}

// ---- unprinted hyphens and merged words --------------------------------
// Engravers drop the hyphen when two syllables sit close ("Jeannie" over two
// notes), and OCR glues tightly set words ("rapturethrills"). A token whose
// letters span several note onsets of the staff above is split into one
// syllable per onset, at the syllable break (vowel groups + consonant rules)
// nearest to where the notes say it should be; a blank gap at the break marks
// a word boundary instead of a syllable boundary.

const VOWELS = 'aeiouyäöüàâæéèêëîïôœùûÿáíóúåøœ';
const isV = (w, i) => {
  const c = w[i];
  if (c === 'y') return i > 0 && !VOWELS.includes(w[i + 1] || '#');
  if (c === 'u' && i > 0 && (w[i - 1] === 'q')) return false;
  return VOWELS.includes(c);
};

// language of the underlay (decides silent final e and Latin vowel hiatus)
function detectLang(texts) {
  const s = ' ' + texts.join(' ').toLowerCase().replace(/[^\p{L}' ]+/gu, ' ').replace(/\s+/g, ' ') + ' ';
  const cnt = (re) => (s.match(re) || []).length;
  const de = 2 * cnt(/[äöüß]/g) + cnt(/ (?:und|der|die|das|ich|ein|eine|einen|nicht|mit|dem|den|zu|ist|sich|auf|mich|mir|dich|dir|du|wie|im|von|wir|ihr|sein|seine|nun|herz|gott|es|er|sie|so|wo|noch|nach|aus)(?= )/g);
  const la = cnt(/ (?:et|est|cum|dei|deo|deus|non|qui|quae|quod|tu|te|nos|nobis|ad|sancte|sanctus|domine|dominus|gloria|pacem|excelsis|ave|mater|filius|spiritus|amen|mea|meum|tibi|sicut|erat|sunt|pax|alleluia)(?= )/g)
    + 0.3 * cnt(/\p{L}(?:us|um|ae|is|unt|orum|ibus) /gu);
  const en = cnt(/ (?:the|and|of|to|my|thy|thee|with|is|that|for|our|all|thou|his|her|be|we|you|i|on|from|love|me|he|she|they|was|are|o'er|when|where)(?= )/g);
  if (de > en && de >= la) return 'de';
  if (la > en && la > de) return 'la';
  return 'en';
}

// vowel groups of a lower-case letter string: [{a, b}] (letter index ranges)
function vowelGroups(w, lang) {
  const g = [];
  for (let i = 0; i < w.length; i++) {
    if (!isV(w, i)) continue;
    const last = g[g.length - 1];
    const pair = w[i - 1] + w[i];
    const joins = lang !== 'la' || pair === 'ae' || pair === 'oe' || pair === 'au' || pair === 'eu';
    if (last && last.b === i && joins) { last.b = i + 1; continue; }
    g.push({ a: i, b: i + 1 });
  }
  if (lang === 'en' && g.length > 1) {
    const n = w.length, L = g[g.length - 1];
    // silent final e ("love", "smile"), but "-le" after a consonant is sung ("ta-ble")
    if (L.a === n - 1 && L.b === n && w[n - 1] === 'e' && !(w[n - 2] === 'l' && n >= 3 && !isV(w, n - 3))) g.pop();
    // silent "-gue(s)" / "-que(s)" ("tongues")
    else if (/[gq]ues?$/.test(w) && L.b >= n - 1 && w[L.a - 1] && /[gq]/.test(w[L.a - 1])) g.pop();
    // silent -es / -ed ("hopes", "named"), not after sibilants / t, d
    else if (L.a === n - 2 && L.b === n - 1 && w[n - 2] === 'e' && ((w[n - 1] === 'd' && !/[td]/.test(w[n - 3])) || (w[n - 1] === 's' && !/[szxgch]/.test(w[n - 3])))) g.pop();
  }
  return g;
}

const UNITS = new Set(['ch', 'sh', 'th', 'ph', 'wh', 'sch', 'ck', 'qu', 'chr', 'thr', 'shr']);
const ONSETS = new Set(['bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'tr', 'ch', 'sh', 'th', 'ph', 'wh', 'qu', 'sp', 'st', 'sc', 'sk', 'sl', 'sm', 'sn', 'sw', 'tw', 'str', 'spr', 'scr', 'spl', 'thr', 'shr', 'chr', 'sch', 'squ']);
// preferred break (letter index: break before it) in the consonants w[a..b)
function preferredBreak(w, a, b, lang) {
  const c = w.slice(a, b);
  // English suffix "-ing": "wait-ing", "sigh-ing", but "sob-bing"
  if (lang === 'en' && /^ings?$/.test(w.slice(b)) && c.length && !(c.length >= 2 && c[c.length - 1] === c[c.length - 2])) return b;
  if (c === 'gh' || c.endsWith('gh')) return b;          // "sigh-ing", "night-ly"
  if (c.length <= 1) return c === 'x' ? b : a;           // V-CV ("va-por"); "ex-alt"
  if (UNITS.has(c)) return a;                           // "la-chen", "fa-thers"
  if (c === 'ng' && lang === 'en') return b;            // "sing-ing"
  for (let L = Math.min(3, c.length - 1); L >= 2; L--) if (ONSETS.has(c.slice(c.length - L)) && !(lang === 'de' && c.slice(c.length - L) === 'st')) return b - L;
  return b - 1;                                         // VC-CV ("Brun-nen", "win-ning")
}

// s: syllable {text, x, x0, x1, syllabic}; voices: [[onset x...]] of the staff
// above (one list, or upper / lower voice of a two-voice staff); r: where a
// note sits within its syllable on this row (0.5 centred, ~0.2 left-aligned)
function splitSyllable(s, voices, lang, r, hyphens) {
  const text = s.text;
  if (s.x0 == null || text.length < 2) return [s];
  const cw = (s.x1 - s.x0) / text.length;
  // a printed hyphen inside the token that OCR did not read ("mu-sic" -> "music")
  const hy = (hyphens || []).filter(x => x > s.x0 + 0.8 * cw && x < s.x1 - 0.8 * cw);
  if (hy.length) {
    const pieces = cutAt(s, hy.map(x => ({ x })), lang, null);
    if (pieces.length > 1) return pieces.flatMap(p => splitSyllable(p, voices, lang, r, null));
  }
  let inside = [];
  for (const ons of voices) {
    const ins = ons.filter(x => x > s.x0 + 0.5 * cw && x < s.x1 - 0.5 * cw);
    if (ins.length > inside.length) inside = ins;
  }
  if (inside.length < 2) return [s];
  // target for each boundary: the next syllable starts r of its width left of its note
  const tgt = [];
  const k = inside.length;
  for (let m = 0; m + 1 < k; m++) tgt.push({ x: inside[m + 1] - r * (inside[m + 1] - inside[m]) });
  return cutAt(s, tgt, lang, inside);
}

// cut a token at k-1 syllable breaks nearest the target x positions; pieces
// take the onset x when given (ons), else their own centre
function cutAt(s, tgt, lang, ons) {
  const text = s.text;
  const cw = (s.x1 - s.x0) / text.length;
  const k = tgt.length + 1;
  const idx = []; let low = '';
  for (let i = 0; i < text.length; i++) if (/\p{L}/u.test(text[i])) { idx.push(i); low += text[i].toLowerCase(); }
  const groups = vowelGroups(low, lang);
  // more notes than syllables: a melisma or another voice's notes; leave it
  if (groups.length < k) return [s];
  const xOf = (ci) => s.x0 + ci * cw;
  // candidate breaks per gap between vowel groups
  const gaps = [];
  for (let j = 0; j + 1 < groups.length; j++) {
    const a = groups[j].b, b = groups[j + 1].a, pref = preferredBreak(low, a, b, lang);
    const list = [];
    for (let li = Math.max(1, a); li <= b; li++) list.push({ li, x: xOf(idx[li]), pen: li === pref ? 0 : 1.2 + 0.3 * Math.abs(li - pref) });
    gaps.push(list);
  }
  // DP: boundary m placed in gap j (gaps strictly increasing)
  const G = gaps.length;
  const best = Array.from({ length: k - 1 }, () => new Array(G).fill(null));
  for (let m = 0; m < k - 1; m++) for (let j = m; j < G; j++) {
    let prev = m === 0 ? { cost: 0 } : null;
    if (m > 0) for (let jj = m - 1; jj < j; jj++) if (best[m - 1][jj] && (!prev || best[m - 1][jj].cost < prev.cost)) prev = best[m - 1][jj];
    if (!prev) continue;
    let bc = null;
    for (const c of gaps[j]) { const v = prev.cost + Math.abs(c.x - tgt[m].x) / cw + c.pen; if (!bc || v < bc.cost) bc = { cost: v, c, prev: m > 0 ? prev : null }; }
    best[m][j] = bc;
  }
  let end = null;
  for (let j = 0; j < G; j++) if (best[k - 2][j] && (!end || best[k - 2][j].cost < end.cost)) end = best[k - 2][j];
  if (!end) return [s];
  const cuts = [];
  for (let b = end; b; b = b.prev) cuts.unshift(b.c);
  const out = [];
  const first = s.syllabic === 'middle' || s.syllabic === 'end', last = s.syllabic === 'begin' || s.syllabic === 'middle';
  let from = 0;
  cuts.concat([null]).forEach((c, m) => {
    const to = c ? idx[c.li] : text.length;
    const before = m > 0 || first, after = m < cuts.length || last;
    out.push({ ...s, text: text.slice(from, to), x: ons ? ons[m] : (xOf(from) + xOf(to)) / 2, x0: xOf(from), x1: xOf(to), split: true,
      syllabic: before ? (after ? 'middle' : 'end') : (after ? 'begin' : 'single') });
    from = to;
  });
  return out.filter(p => /\p{L}/u.test(p.text));
}

// extender lines (geometry) -> the syllable just left of each is a melisma:
// extend = true, extendTo = page x where the line ends (alignment hint)
function markExtenders(syl, ext, sp) {
  for (const e of ext || []) {
    let best = null;
    for (const s of syl) if (s.x1 != null && s.x0 < e.x0 && e.x0 - s.x1 < 2.5 * sp && (!best || s.x1 > best.x1)) best = s;
    if (best && !(best.syllabic === 'begin' || best.syllabic === 'middle')) { best.extend = true; best.extendTo = Math.max(best.extendTo || 0, e.x1); }
  }
}

// a printed hyphen between two syllables (geometry) links them even when
// OCR read it as "." or missed it ("Fair . est" -> Fair- est)
function linkHyphens(syl, hyphens) {
  if (!hyphens || !hyphens.length) return;
  for (let i = 0; i + 1 < syl.length; i++) {
    const a = syl[i], b = syl[i + 1];
    if (a.x1 == null || b.x0 == null || a.syllabic === 'begin' || a.syllabic === 'middle') continue;
    if (!hyphens.some(x => x > a.x1 - 2 && x < b.x0 + 2)) continue;
    a.syllabic = a.syllabic === 'end' ? 'middle' : 'begin';
    b.syllabic = b.syllabic === 'begin' ? 'middle' : (b.syllabic === 'single' ? 'end' : b.syllabic);
  }
}

// note onsets of one staff between x0 and x1: one list, or two (upper and
// lower voice) when the staff carries two voices (opposed stems at one x)
function staffVoices(fr, staff, x0, x1, sp) {
  const hs = (fr.heads || []).filter(h => h.staff === staff && h.x >= x0 && h.x <= x1).sort((a, b) => a.x - b.x);
  const cl = [];
  for (const h of hs) {
    const last = cl[cl.length - 1];
    if (last && h.x - last.xr < 1.2 * sp) { last.xr = h.x; last.hs.push(h); } else cl.push({ xr: h.x, hs: [h] });
  }
  const mean = (a) => a.reduce((t, h) => t + h.x, 0) / a.length;
  const all = cl.map(c => mean(c.hs));
  const up = (h) => h.stemDir === 1 || h.stemDir === 2, dn = (h) => h.stemDir === -1;
  const both = cl.filter(c => c.hs.some(up) && c.hs.some(dn)).length;
  if (cl.length < 4 || both < 0.3 * cl.length) return [all];
  const U = [], D = [];
  for (const c of cl) {
    const u = c.hs.filter(h => !dn(h)), d = c.hs.filter(h => !up(h));
    if (u.length) U.push(mean(u));
    if (d.length) D.push(mean(d));
  }
  return [U, D];
}

// where a note sits inside its (single-note) word on a row: 0.5 = centred
// (modern engraving), ~0.2 = syllables left-aligned to their notes
function noteOffset(syl, voices) {
  const rs = [];
  for (const s of syl) {
    if (s.x0 == null || s.x1 - s.x0 < 1) continue;
    const cw = (s.x1 - s.x0) / Math.max(1, s.text.length);
    const ins = voices[0].filter(x => x > s.x0 - 0.2 * cw && x < s.x1);
    if (ins.length === 1) rs.push((ins[0] - s.x0) / (s.x1 - s.x0));
  }
  if (rs.length < 3) return 0.5;
  rs.sort((a, b) => a - b);
  return Math.max(0.15, Math.min(0.5, rs[rs.length >> 1]));
}

// ---- part labels at the start of the first system (L3e) -----------------
// "Soprano", "Alto I / Alto II", "Piano", "S. A." are printed left of the
// bracket / brace, centred on their staff (or between the two staves of a
// grand staff). Text-sized components there are grouped into lines, each line
// is OCR'd from a masked crop and assigned to the staff (or staves) it faces.
function labelLines(fr, sysIdx) {
  const { B, staves } = fr;
  const sys = fr.systems[sysIdx];
  const W = B.width;
  const sts = sys.map(i => staves[i]);
  const sp = sts[0].space;
  const left = Math.min(...sts.map(s => s.left));
  const xr = Math.round(left - 0.3 * sp);
  const yTop = Math.max(0, Math.round(sts[0].yAt(0, left) - 1.5 * sp));
  const yBot = Math.min(B.height - 1, Math.round(sts[sts.length - 1].yAt(4, left) + 1.5 * sp));
  if (xr < 2 * sp || yBot - yTop < 2 * sp) return [];
  const bw = xr, bh = yBot - yTop + 1;
  const band = { width: bw, height: bh, data: new Uint8Array(bw * bh) };
  for (let y = 0; y < bh; y++) band.data.set(B.data.subarray((yTop + y) * W, (yTop + y) * W + bw), y * bw);
  const { labels, comps } = labelComponents(band);
  const cs = comps.filter(c => {
    const h = c.y1 - c.y0 + 1, w = c.x1 - c.x0 + 1;
    return h >= 0.35 * sp && h <= 2.5 * sp && w <= 4 * sp && c.area >= 4 && c.x1 < bw - 1 && c.y0 > 0 && c.y1 < bh - 1;
  }).sort((a, b) => (a.y0 + a.y1) - (b.y0 + b.y1));
  // single-linkage grouping: same text row (vertical overlap) and close (word gaps)
  const par = cs.map((_, i) => i);
  const find = (i) => { while (par[i] !== i) { par[i] = par[par[i]]; i = par[i]; } return i; };
  for (let i = 0; i < cs.length; i++) for (let j = i + 1; j < cs.length; j++) {
    const a = cs[i], b = cs[j];
    const ov = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) + 1;
    const gap = Math.max(a.x0 - b.x1, b.x0 - a.x1);
    if (ov >= 0.4 * Math.min(a.y1 - a.y0 + 1, b.y1 - b.y0 + 1) && gap <= 1.5 * sp) par[find(i)] = find(j);
  }
  const groups = new Map();
  cs.forEach((c, i) => { const r = find(i); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(c); });
  const lines = [...groups.values()].map(mem => ({ mem, x0: Math.min(...mem.map(c => c.x0)), x1: Math.max(...mem.map(c => c.x1)), y0: Math.min(...mem.map(c => c.y0)), y1: Math.max(...mem.map(c => c.y1)) }));
  const out = [];
  for (const ln of lines) {
    const big = ln.mem.filter(c => c.y1 - c.y0 + 1 >= 0.6 * sp);
    if (!big.length || ln.x1 - ln.x0 + 1 < 0.5 * sp) continue;
    const tall = Math.max(...big.map(c => c.y1 - c.y0 + 1));
    const pad = Math.round(0.4 * tall);
    const sx0 = Math.max(0, ln.x0 - pad), sx1 = Math.min(bw - 1, ln.x1 + pad), sy0 = Math.max(0, ln.y0 - pad), sy1 = Math.min(bh - 1, ln.y1 + pad);
    const keep = new Set(ln.mem.map(c => c.id));
    const SW = sx1 - sx0 + 1, SH = sy1 - sy0 + 1;
    const data = new Uint8ClampedArray(SW * SH).fill(255);
    for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
      const lab = labels[(sy0 + y) * bw + sx0 + x];
      if (lab && keep.has(lab)) data[y * SW + x] = fr.gray.data[(yTop + sy0 + y) * W + sx0 + x];
    }
    const cy = yTop + (ln.y0 + ln.y1) / 2;
    // the staff it faces, or the two staves it sits between (grand staff)
    let on = sys.filter(i => cy >= staves[i].yAt(0, left) - 0.8 * sp && cy <= staves[i].yAt(4, left) + 0.8 * sp);
    if (!on.length) for (let k = 0; k + 1 < sys.length; k++) if (cy > staves[sys[k]].yAt(4, left) && cy < staves[sys[k + 1]].yAt(0, left)) on = [sys[k], sys[k + 1]];
    if (!on.length) continue;
    out.push({ system: sysIdx, staves: on, y: Math.round(cy), x0: sx0, tall, strip: { width: SW, height: SH, data } });
  }
  return out;
}

async function readPartLabels(fr, ocr, o, onLine) {
  const res = [];
  if (!fr.systems.length) return res;
  for (const ln of labelLines(fr, 0)) {
    const scale = Math.min(3, Math.max(0.5, o.targetCap / ln.tall));
    // white margin around the word helps tesseract on very short crops
    const m = Math.round(0.6 * ln.tall);
    const W = Math.round((ln.strip.width + 2 * m) * scale), H = Math.round((ln.strip.height + 2 * m) * scale);
    const img = makeGray(W, H, 255);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const sx = Math.floor(x / scale) - m, sy = Math.floor(y / scale) - m;
      if (sx >= 0 && sy >= 0 && sx < ln.strip.width && sy < ln.strip.height) img.data[y * W + x] = ln.strip.data[sy * ln.strip.width + sx];
    }
    let words = [];
    try { words = await ocr(img); } catch (e) { words = []; }
    if (onLine) onLine();
    // words (letters, abbreviation dot) or a voice number; mixed letter/digit tokens are junk
    const toks = words.filter(w => w.conf >= 40).map(w => w.text.replace(/[^\p{L}\p{N}.'’]/gu, '')).filter(t => /^[\p{L}'’]+\.?$/u.test(t) || /^\d\.?$/.test(t));
    if (!toks.length) continue;
    // roman voice numbers misread: "Alto IT" / "Tenor Il" -> II
    const text = toks.map((t, i) => i > 0 && /^[Il|T]{1,3}$/.test(t) && /[Il|]/.test(t + (t.length > 1 ? 'I' : '')) ? 'I'.repeat(t.length) : t).join(' ').replace(/\s+/g, ' ').trim();
    if (!/\p{L}/u.test(text)) continue;
    const conf = Math.round(words.reduce((a, w) => a + w.conf, 0) / words.length);
    res.push({ system: ln.system, staff: ln.staves[0], staves: ln.staves, text, conf, y: ln.y });
  }
  // several labels on one staff (e.g. "Soprano I" / "Soprano II"): top-down = voice 1, 2
  const by = {};
  res.forEach(r => (by[r.staves.join('+')] ||= []).push(r));
  for (const k in by) by[k].sort((a, b) => a.y - b.y).forEach((r, i, a) => { r.voice = a.length > 1 ? i + 1 : 0; });
  return res;
}

// ---- stanza text below the music (L5b) -----------------------------------
// Verses printed as a poem after the last system (often in two columns, each
// stanza starting "4.", "5." ...) are read line by line: text lines are found
// by baseline voting over the whole page width, split into column chunks at
// wide gaps, OCR'd, and grouped into stanzas by their leading number.
function stanzaChunks(fr, yStart) {
  const { B, gray } = fr;
  const W = B.width, H = B.height;
  const sp = fr.staves.length ? fr.staves[fr.systems[fr.systems.length - 1][0]].space : 16;
  const y0 = Math.max(0, Math.round(yStart)), y1 = H - 1;
  if (y1 - y0 < 2 * sp) return [];
  const bw = W, bh = y1 - y0 + 1;
  const band = { width: bw, height: bh, data: B.data.subarray(y0 * W, (y1 + 1) * W) };
  const { labels, comps } = labelComponents(band);
  const cand = comps.filter(c => c.y0 > 0 && c.area >= 3 && c.y1 - c.y0 + 1 <= 3 * sp && c.x1 - c.x0 + 1 <= 6 * sp);
  const letters = cand.filter(c => { const h = c.y1 - c.y0 + 1, w = c.x1 - c.x0 + 1; return h >= 0.45 * sp && h <= 2.5 * sp && w >= 0.12 * sp && w <= 3 * sp; });
  if (letters.length < 6) return [];
  const hist = new Float64Array(bh + 1);
  for (const c of letters) hist[c.y1]++;
  const R = Math.max(1, Math.round(0.15 * sp)), sm = new Float64Array(bh + 1);
  for (let y = 0; y <= bh; y++) { let s = 0; for (let d = -R; d <= R; d++) { const yy = y + d; if (yy >= 0 && yy <= bh) s += hist[yy]; } sm[y] = s; }
  const peaks = [];
  for (const y of [...sm.keys()].sort((a, b) => sm[b] - sm[a])) {
    if (sm[y] < 4) break;
    if (peaks.some(p => Math.abs(p - y) < 1.2 * sp)) continue;
    peaks.push(y);
  }
  peaks.sort((a, b) => a - b);
  const chunks = [];
  for (const bl of peaks) {
    const core = letters.filter(c => Math.abs(c.y1 - bl) <= 0.25 * sp + 1);
    if (core.length < 4) continue;
    const hs = core.map(c => c.y1 - c.y0 + 1).sort((a, b) => a - b);
    const tall = median(hs.slice(hs.length >> 1));
    if (tall < 0.5 * sp) continue;
    const mem = cand.filter(c => c.y0 >= bl - 1.6 * tall && c.y1 <= bl + 0.6 * tall).sort((a, b) => a.x0 - b.x0);
    // split at column gaps
    let cur = null;
    const gapMax = Math.max(3 * sp, 2.5 * tall);
    for (const c of mem) {
      if (cur && c.x0 - cur.x1 <= gapMax) { cur.mem.push(c); cur.x1 = Math.max(cur.x1, c.x1); continue; }
      cur = { mem: [c], x0: c.x0, x1: c.x1, bl, tall };
      chunks.push(cur);
    }
  }
  const out = [];
  for (const ch of chunks) {
    const nCore = ch.mem.filter(c => Math.abs(c.y1 - ch.bl) <= 0.25 * sp + 1 && c.y1 - c.y0 + 1 >= 0.45 * sp).length;
    if (nCore < 3) continue;
    const pad = Math.round(0.4 * ch.tall);
    const sx0 = Math.max(0, ch.x0 - pad), sx1 = Math.min(bw - 1, ch.x1 + pad);
    const sy0 = Math.max(0, Math.min(...ch.mem.map(c => c.y0)) - pad), sy1 = Math.min(bh - 1, Math.max(...ch.mem.map(c => c.y1)) + pad);
    const keep = new Set(ch.mem.map(c => c.id));
    const SW = sx1 - sx0 + 1, SH = sy1 - sy0 + 1;
    const data = new Uint8ClampedArray(SW * SH).fill(255);
    for (let y = 0; y < SH; y++) for (let x = 0; x < SW; x++) {
      const lab = labels[(sy0 + y) * bw + sx0 + x];
      if (lab && keep.has(lab)) data[y * SW + x] = gray.data[(y0 + sy0 + y) * W + sx0 + x];
    }
    out.push({ x0: sx0, y: y0 + ch.bl, tall: ch.tall, sp, strip: { width: SW, height: SH, data } });
  }
  return out;
}

async function readStanzas(fr, ocr, o, yStart) {
  const lines = [];
  for (const ch of stanzaChunks(fr, yStart)) {
    const scale = Math.min(3, Math.max(0.5, o.targetCap / ch.tall));
    const m = Math.round(0.3 * ch.tall);
    const W = Math.round((ch.strip.width + 2 * m) * scale), H = Math.round((ch.strip.height + 2 * m) * scale);
    const img = makeGray(W, H, 255);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const sx = Math.floor(x / scale) - m, sy = Math.floor(y / scale) - m;
      if (sx >= 0 && sy >= 0 && sx < ch.strip.width && sy < ch.strip.height) img.data[y * W + x] = ch.strip.data[sy * ch.strip.width + sx];
    }
    let words = [];
    try { words = await ocr(img); } catch (e) { words = []; }
    if (!words.length) continue;
    const conf = words.reduce((a, w) => a + w.conf, 0) / words.length;
    const text = words.filter(w => w.conf >= 30).map(w => w.text).join(' ').replace(/[|_]+/g, ' ').replace(/\s+/g, ' ').trim();
    const nWords = (text.match(/\p{L}{2,}/gu) || []).length;
    if (conf < 55 || nWords < 2) continue;
    lines.push({ x0: ch.x0, y: ch.y, sp: ch.sp, text, conf: Math.round(conf) });
  }
  if (!lines.length) return [];
  // columns: left edges more than 10 staff spaces apart
  lines.sort((a, b) => a.x0 - b.x0);
  const cols = [];
  for (const ln of lines) {
    const c = cols.find(c => Math.abs(ln.x0 - c.x0) <= 10 * ln.sp);
    if (c) c.lines.push(ln); else cols.push({ x0: ln.x0, lines: [ln] });
  }
  const stanzas = [];
  for (const c of cols) {
    const ls = c.lines.sort((a, b) => a.y - b.y);
    const pitches = ls.slice(1).map((l, i) => l.y - ls[i].y).sort((a, b) => a - b);
    const pitch = pitches.length ? pitches[pitches.length >> 1] : 3 * ls[0].sp;
    const widths = ls.map(l => l.text.length).sort((a, b) => a - b), wMed = widths[widths.length >> 1];
    let cur = null, prevY = null;
    for (const ln of ls) {
      // a wide vertical gap ends a stanza (prose, a credit or another piece follows)
      if (prevY != null && ln.y - prevY > Math.max(1.8 * pitch, 4 * ln.sp)) cur = null;
      prevY = ln.y;
      const m = ln.text.match(/^([1-9][0-9]?)\s*[.,)]\s*(.*)$/);
      if (m) { cur = { number: +m[1], label: m[1] + '.', lines: [] }; stanzas.push(cur); if (m[2]) cur.lines.push(m[2]); continue; }
      if (!cur) continue;
      // credits / captions / prose inside the block: all caps, bracketed, title case, much longer lines
      const ws = ln.text.replace(/[^\p{L}\s]/gu, ' ').split(/\s+/).filter(w => w.length >= 2);
      const caps = ws.filter(w => /^\p{Lu}/u.test(w)).length;
      if (!/\p{Ll}/u.test(ln.text) || /^[(\[].*[)\]]$/.test(ln.text) || (ws.length >= 3 && caps === ws.length) || ln.text.length > 1.8 * wMed) { cur = null; continue; }
      cur.lines.push(ln.text);
    }
  }
  for (const s of stanzas) s.text = s.lines.join('\n');
  return stanzas.filter(s => s.lines.length);
}

// split a word into sung syllables by the same rules as the note-aware split
// ("promised" -> pro-mised): for fitting stanza text to the melody
function syllabify(word, lang = 'en') {
  const idx = []; let low = '';
  for (let i = 0; i < word.length; i++) if (/\p{L}/u.test(word[i])) { idx.push(i); low += word[i].toLowerCase(); }
  const g = vowelGroups(low, lang);
  if (g.length < 2) return [word];
  const cuts = [];
  for (let j = 0; j + 1 < g.length; j++) cuts.push(idx[preferredBreak(low, g[j].b, g[j + 1].a, lang)]);
  const out = []; let from = 0;
  for (const c of cuts) { if (c > from) { out.push(word.slice(from, c)); from = c; } }
  out.push(word.slice(from));
  return out;
}

// how far a row's syllables follow the notes of a staff: the share printed
// under an onset (centred under the note, or starting at it: melisma) minus
// the share a row of random x positions would reach (the part of the row's
// width within reach of an onset: near 1 on a staff dense with notes)
function rowFit(fr, staff, syl, x0, x1, sp) {
  if (!syl.length) return -1;
  const voices = staffVoices(fr, staff, x0, x1, sp);
  let best = -1;
  const xa = Math.min(...syl.map(s => s.x0 ?? s.x)), xb = Math.max(...syl.map(s => s.x1 ?? s.x));
  for (const ons of voices) {
    if (!ons.length || !syl.length) continue;
    let hit = 0;
    for (const s of syl) {
      let d = Infinity;
      for (const x of ons) d = Math.min(d, Math.abs(x - s.x), s.x0 != null ? Math.abs(x - (s.x0 + 0.55 * sp)) : Infinity);
      if (d <= 1.0 * sp) hit++;
    }
    let cov = 0;
    const n = Math.max(1, Math.round((xb - xa) / 2));
    for (let i = 0; i < n; i++) { const x = xa + (i + 0.5) * (xb - xa) / n; if (ons.some(o => Math.abs(o - x) <= 1.0 * sp)) cov++; }
    best = Math.max(best, hit / syl.length - cov / n);
  }
  return best;
}

// Rows above a staff stay only when they follow its notes (titles, tempo
// and composer lines do not). Between two staves, a bottom row whose
// syllables sit under the lower staff's notes and clearly not under the
// upper staff's (each voice with its own words, e.g. the tenor's text above
// the bass staff) belongs to the lower staff: band + 1, above.
function placeRows(fr, out, geo) {
  for (const k in out) {
    for (const v of out[k].filter(v => v.above)) {
      const g = geo.get(v);
      if (!g || v.syllables.length < 5 || !wordyRow(v.syllables) || rowFit(fr, g.staff, v.syllables, g.x0, g.x1, g.sp) < 0.35) { out[k] = out[k].filter(u => u !== v); geo.delete(v); }
    }
  }
  // the bottom row of each inter-staff band, judged over the whole page (a
  // verse stack of a homophonic hymn may fit the lower staff by chance on
  // one system; a line that belongs to the lower staff does so throughout)
  const cands = {};
  for (const k in out) {
    const sys = fr.systems[k];
    for (let b = 0; b + 1 < sys.length; b++) {
      const rows = out[k].filter(v => v.band === b && !v.above).sort((a, c) => c.y - a.y);
      const v = rows[0], g = v && geo.get(v);
      if (rows.length < 2 || !g) continue;
      const fa = rowFit(fr, sys[b], v.syllables, g.x0, g.x1, g.sp), fb = rowFit(fr, sys[b + 1], v.syllables, g.x0, g.x1, g.sp);
      (cands[b] ||= []).push({ v, g, fa, fb, staff: sys[b + 1] });
    }
  }
  for (const b in cands) {
    const c = cands[b], n = c.length;
    const mean = (f) => c.reduce((t, x) => t + f(x), 0) / n;
    if (mean(x => x.fb - x.fa) < 0.2 || mean(x => x.fb) < 0.35 || c.filter(x => x.fb >= x.fa + 0.2).length < 0.5 * n) continue;
    for (const { v, g, fa, fb, staff } of c) {
      if (fb < fa + 0.1) continue;
      v.band = +b + 1; v.above = true;
      g.staff = staff;
    }
  }
}

// mostly real words: lower-case letter pairs or capitalised words
function wordyRow(syl) {
  return syl.filter(s => /\p{Ll}{2}/u.test(s.text) || /^\p{Lu}\p{Ll}/u.test(s.text)).length >= 0.5 * syl.length;
}

// Verse numbers of the text rows of one page ({system: [row]}): per system
// and band the rows top-down are verses 1..n, except that
// - a row missing inside a stack (OCR rejected it) leaves its number free:
//   rows are counted in steps of the page's line pitch, not one by one;
// - confidently printed stanza numbers ("3.") place the stack: a stack whose
//   top verse was lost starts at 2 when its rows read "3.", "4." ...
//   (a single printed number may only explain rows missing on this page);
// - below the bottom staff, a stack whose top row is printed "2." (or later)
//   is the remaining stanzas set as a poem after the music (v.stanza).
function numberVerses(out, o) {
  const stacks = [];
  for (const k in out) {
    const byBand = {};
    out[k].forEach(v => (byBand[v.band + (v.above ? 'a' : '')] ||= []).push(v));
    for (const b in byBand) stacks.push(byBand[b].sort((a, c) => a.y - c.y));
  }
  const blOf = (v) => (v.geo ? v.geo.bl : v.y1 ?? v.y);
  const gaps = [];
  for (const rows of stacks) for (let i = 1; i < rows.length; i++) gaps.push(blOf(rows[i]) - blOf(rows[i - 1]));
  const pitch = median(gaps);
  const maxRows = Math.max(0, ...stacks.map(r => r.length));
  for (const rows of stacks) {
    const conf = (v) => (v.geo ? v.geo.numberConf : 100);
    if (rows[0].last && rows[0].printed >= 2 && conf(rows[0]) >= 60) { rows.forEach(v => { v.stanza = true; }); continue; }
    // position in the stack, in line pitches (a double gap = one row lost)
    const idx = [0];
    for (let i = 1; i < rows.length; i++) {
      const g = blOf(rows[i]) - blOf(rows[i - 1]);
      const step = o.verseGaps && pitch > 0 && gaps.length >= 3 ? Math.max(1, Math.min(3, Math.round(g / pitch))) : 1;
      idx.push(idx[i - 1] + step);
    }
    // offset from confident printed numbers
    let off = 0;
    if (o.verseGaps) {
      const votes = new Map();
      rows.forEach((v, i) => {
        if (v.printed == null || v.printed > 12 || conf(v) < 70) return;
        const d = v.printed - 1 - idx[i];
        if (d >= 0) votes.set(d, (votes.get(d) || 0) + 1);
      });
      let best = null;
      for (const [d, n] of votes) if (!best || n > best.n || (n === best.n && d < best.d)) best = { d, n };
      if (best && best.d > 0 && (best.n >= 2 || (best.d <= 2 && rows.length + best.d <= maxRows + 1))) off = best.d;
    }
    rows.forEach((v, i) => { v.number = idx[i] + 1 + off; });
  }
}

// ocr(grayImage) -> Promise<[{text, conf, x0, x1}]> in the given image's pixels
async function readLyrics(fr, ocr, onProgress, opts) {
  const o = { ...DEFAULTS, ...(opts || {}) };
  const out = {};
  const sysTops = fr.systems.map(sys => fr.staves[sys[0]].yAt(0, fr.staves[sys[0]].left));
  let done = 0;
  const all = [];
  const geo = new Map();
  const finder = o.ccLines ? findTextLinesCC : findTextLines;
  fr.systems.forEach((sys, si) => {
    const prev = si > 0 ? fr.staves[fr.systems[si - 1][fr.systems[si - 1].length - 1]] : null;
    const prevBot = prev ? Math.max(prev.yAt(4, prev.left), prev.yAt(4, prev.right)) + 1.0 * prev.space : 0;
    const rows = finder(fr, si, sysTops[si + 1] ?? fr.gray.height, o, prevBot);
    // a row above this system that the previous one already took (its lyrics)
    all.push(...rows.filter(r => !r.above || !all.some(q => q.sys === si - 1 && Math.min(q.y1, r.y1) - Math.max(q.y0, r.y0) > 0.5 * (r.y1 - r.y0))));
  });
  // part labels left of the first system (L3e); fr.partLabels for score.js
  if (o.partLabels) {
    try { fr.partLabels = await readPartLabels(fr, ocr, o); } catch (e) { fr.partLabels = []; }
  }
  const talls = all.filter(l => l.tall).map(l => l.tall).sort((a, b) => a - b);
  const tallMed = talls.length >= 3 ? talls[talls.length >> 1] : 0;
  // stroke weight is a property of the page (type, copy, blur): decided
  // once from the median stroke width / letter height of its text lines
  const swr = median(all.filter(l => l.sw && l.tall && !l.above).map(l => l.sw / l.tall));
  if (o.thinAt && swr > o.thinAt) for (const l of all) l.thin = 1;
  // each row's crop is cut first and all first-pass reads are started together (a pool of
  // OCR workers reads them side by side; the results do not depend on the order of reads),
  // then the rows are taken in order as before
  const rowsIn = all.map((ln) => {
    // a row that is a title, credit or tempo line (o.skipBoxes: text.js
    // marks above the music) is not underlay
    if (o.skipBoxes && o.skipBoxes.some(b => Math.min(b[3], ln.y1) - Math.max(b[1], ln.y0) > 0.5 * Math.min(b[3] - b[1], ln.y1 - ln.y0) && (ln.x0 == null || (b[0] < ln.x1 && b[2] > ln.x0)))) return null;
    const pad = Math.round(0.3 * ln.sp);
    const row = ln.strip ? stripRow(ln) : analyseRow(fr.B, ln, pad);
    const ox = ln.strip ? ln.strip.x0 : 0;
    // opts.debug (an array) collects per-row decisions for tuning tools
    const dbg = o.debug ? { sys: ln.sys, band: ln.band, y: ln.y0, h: ln.y1 - ln.y0, sp: +ln.sp.toFixed(1), cov: +row.cov.toFixed(3), ncl: row.clusters.length } : null;
    if (dbg) o.debug.push(dbg);
    // text rows have many glyph clusters and a fair share of inked columns;
    // rows of stems, ties or fermatas have few, thin ones
    if (o.geomCheck && (ln.strip ? row.clusters.length < 3 : (row.cov < 0.08 || row.clusters.length < 4))) { if (dbg) dbg.reject = 'geom'; return null; }
    const crop = buildCrop(ln.strip || fr.gray, row, ln, o);
    let read;
    try { read = Promise.resolve(ocr(crop.img)).catch(() => []); } catch (e) { read = Promise.resolve([]); }
    return { row, ox, dbg, crop, read };
  });
  for (let li = 0; li < all.length; li++) {
    const ln = all[li], pre = rowsIn[li];
    const step = () => { done++; if (onProgress) onProgress(done, all.length); };
    if (!pre) { step(); continue; }
    const { row, ox, dbg, crop } = pre, img = crop.img, toPage = (x) => crop.toPage(x) + ox;
    let words = await pre.read;
    // second pass (ocr.extra: more languages, loaded on first use): a row with
    // accent marks over its letters is read again
    if (typeof ocr.extra === 'function' && o.secondPass !== false) {
      const conf = (ws) => ws.reduce((a, w) => a + w.conf, 0) / Math.max(1, ws.length);
      const c1 = conf(words);
      // signs of accented text the first pass half-read: a letter outside ASCII, a
      // word mixing letters and digits ("V6" for Vö)
      // (German umlauts and ß the first pass reads itself)
      const suspect = words.some(w => /[^\x00-\x7fäöüÄÖÜß’‘“”„–—]/.test(w.text) && /\p{L}/u.test(w.text)) || words.some(w => /\p{L}/u.test(w.text) && /\d/.test(w.text) && !/^\d+[.,]?$/.test(w.text));
      // words of French, Spanish, Italian or Czech (the languages the second pass adds)
      const toks = words.map(w => w.text.toLowerCase().replace(/[^\p{L}']/gu, '')).filter(Boolean);
      const other = toks.filter(t => /^(le|les|du|des|au|aux|et|est|une|sur|dans|pour|qui|que|el|los|las|y|en|con|por|mi|del|il|di|che|per|nel|della|je|se|ze|na|nad|pod|jsem|ty)$/.test(t)).length;
      const en = toks.filter(t => /^(the|and|of|to|my|thy|thee|with|is|that|for|our|all|thou|his|be|we|you|on|from|me|he)$/.test(t)).length;
      // (umlauts the first pass already read are marks too: such rows are German)
      // (German words without their umlauts read: "fur", "uber" ... the first pass handles them)
      const german = words.some(w => /[äöüÄÖÜß]/.test(w.text)) || toks.filter(t => /^(und|der|die|das|den|dem|des|ich|du|er|wir|ihr|mein|dein|sein|nicht|mit|von|zu|auf|im|ist|ein|eine|wie|so|nun|herr|gott|fur|uber|schon|horen)$/.test(t)).length >= 1;
      if (words.length && (suspect || (other >= 2 && other > en) || (!german && en <= 1 && accentMarks(img) >= 2))) {
        let w2 = [];
        try { w2 = await ocr.extra(img); } catch (e) { w2 = []; }
        // kept only when it reads accented letters the first pass did not, at no loss of confidence
        const acc = (ws) => ws.reduce((a, w) => a + (w.text.match(/[^\x00-\x7f\p{P}]/gu) || []).length, 0);
        const good = (ws) => ws.filter(w => plausible(w.text)).length;
        if (w2.length && conf(w2) >= c1 - o.secondPassSlack && acc(w2) > acc(words) && good(w2) >= good(words) - 1) { words = w2; if (dbg) dbg.second = true; }
      }
    }
    const mapped = splitMerged(words.map(w => ({ ...w, x0: toPage(w.x0), x1: toPage(Math.max(w.x0, w.x1 - 1)) + 1 }))).map(w => ({ ...w, ok: plausible(w.text) }));
    // line-level sanity: lyric rows are mostly clean words
    const nOk = mapped.filter(w => w.ok).length;
    const meanConf = mapped.reduce((a, w) => a + w.conf, 0) / Math.max(1, mapped.length);
    const kept = mapped.filter(w => w.conf >= o.minWordConf || (o.relaxLow && w.ok && meanConf >= o.minLineConf));
    if (dbg) { dbg.raw = mapped.map(w => w.text + '(' + Math.round(w.conf) + ')').join(' '); dbg.meanConf = Math.round(meanConf); dbg.okFrac = +(nOk / Math.max(1, mapped.length)).toFixed(2); }
    // a lyric row has several confident, word-like tokens (lower case, a vowel, 2+ letters);
    // rows of stems, dynamics or ties read as capitals, symbols and single letters
    const nGood = mapped.filter(w => goodWord(w)).length, nGood2 = mapped.filter(w => goodWord(w, 2)).length;
    const nTok = mapped.filter(w => !/^[-‐‑‒–—―~_|.,;:'"]+$/.test(w.text)).length;
    if (dbg) dbg.good = nGood + '/' + nTok;
    if (!mapped.length || meanConf < o.minLineConf * 0.8 || nOk < 0.6 * mapped.length || nGood2 < 2 || (nGood < o.goodFrac * nTok && nGood < o.goodAbs)) { if (dbg) dbg.reject = 'ocr'; step(); continue; }
    // captions under the music ("God Bless Our Native Land", "(Tune: America)"): title case, brackets, bigger type
    if (o.titleCheck) {
      const wordsL = mapped.map(w => w.text.replace(/[^\p{L}]/gu, '')).filter(t => t.length >= 2);
      const caps = wordsL.filter(t => /^\p{Lu}/u.test(t)).length;
      const txt = mapped.map(w => w.text).join(' ').trim();
      // bigger type: a caption, unless the row reads as lower-case words (accents
      // and umlauts on capitals make a lyric row taller, not a caption)
      const lowerWords = wordsL.filter(t => /^\p{Ll}/u.test(t)).length;
      const big = ln.tall && tallMed && ln.tall > 1.35 * tallMed && !(wordsL.length >= 4 && lowerWords >= 0.6 * wordsL.length);
      if ((wordsL.length >= 2 && caps >= 0.8 * wordsL.length && wordsL.length <= 8) || /^[(\[].*[)\]]$/.test(txt) || big) { if (dbg) dbg.reject = 'title'; step(); continue; }
    }
    // unsure short tokens without a vowel ("t", "T", "CL", "gs") are stems,
    // slurs and specks read as letters, not syllables
    const junk = (w) => {
      if (!o.dropJunk || w.conf >= 50) return false;
      const t = w.text.replace(/[^\p{L}]/gu, '');
      return t.length >= 1 && t.length <= 3 && !/[aeiouyàâäéèêëîïôöùûüåæøœáíóúñ]/i.test(t);
    };
    const { number, numberConf, syllables } = toSyllables(joinElisions(fr, ln, kept.filter(w => (w.ok || w.conf >= 60) && !junk(w))));
    const entry = { band: ln.band, last: ln.last, y: ln.y0, y1: ln.y1, printed: number, number, syllables, raw: mapped.map(w => w.text).join(' '), conf: meanConf };
    if (ln.above) entry.above = true;
    Object.defineProperty(entry, 'geo', { value: { bl: ln.baseline ?? ln.y1, numberConf, sp: ln.sp }, enumerable: false });
    (out[ln.sys] ||= []).push(entry);
    geo.set(entry, { sp: ln.sp, staff: fr.systems[ln.sys][ln.band], x0: ln.x0, x1: ln.x1, extenders: ln.extenders || [],
      hyphens: ln.hyphens ? ln.hyphens.map(h => (h.x0 + h.x1) / 2) : row.clusters.filter((c, i) => row.hy[i]).map(([a, b]) => row.xa + (a + b) / 2) });
    step();
  }
  for (const [v, g] of geo) linkHyphens(v.syllables, g.hyphens);
  // melisma: an extender line after a syllable holds it over the following notes
  for (const [v, g] of geo) markExtenders(v.syllables, g.extenders, g.sp);
  // text above a staff belongs to that staff only when it follows its notes;
  // the lower rows between two staves may belong to the staff below
  if (o.aboveLines) placeRows(fr, out, geo);
  // unprinted hyphens / merged words: split tokens spanning several onsets
  if (o.splitByNotes) {
    const lang = o.lang || detectLang(Object.values(out).flat().map(v => v.syllables.map(s => s.text).join(' ')));
    for (const [v, g] of geo) {
      const voices = staffVoices(fr, g.staff, g.x0, g.x1, g.sp);
      const r = noteOffset(v.syllables, voices);
      v.syllables = v.syllables.flatMap(s => splitSyllable(s, voices, lang, r, g.hyphens));
    }
    Object.defineProperty(out, 'lang', { value: lang, enumerable: false });
  }
  // verse numbers: per system and band, rows top-down are verses 1..n
  for (const k in out) out[k] = out[k].filter(v => v.syllables.length >= 2);
  numberVerses(out, o);
  for (const k in out) out[k] = out[k].filter(v => !v.stanza);
  // stanza text printed after the music (L5b) -> fr.stanzas for score.js
  if (o.stanzas && fr.systems.length) {
    const ls = fr.systems.length - 1, lsys = fr.systems[ls], bot = fr.staves[lsys[lsys.length - 1]];
    let yStart = Math.max(bot.yAt(4, bot.left), bot.yAt(4, bot.right)) + 1.0 * bot.space;
    for (const v of out[ls] || []) if (v.band === lsys.length - 1 && v.y1 != null) yStart = Math.max(yStart, v.y1 + 0.3 * bot.space);
    try { fr.stanzas = await readStanzas(fr, ocr, o, yStart); } catch (e) { fr.stanzas = []; }
  }
  // a word hyphenated across a system break: the first syllable of the next
  // system's matching verse continues it ("o-" | "cean" -> end, not single)
  const keys = Object.keys(out).map(Number).sort((a, b) => a - b);
  for (let i = 1; i < keys.length; i++) {
    if (keys[i] !== keys[i - 1] + 1) continue;
    for (const v of out[keys[i]]) {
      const prev = out[keys[i - 1]].find(u => u.band === v.band && u.number === v.number);
      const last = prev && prev.syllables[prev.syllables.length - 1];
      if (!last || !(last.syllabic === 'begin' || last.syllabic === 'middle') || !v.syllables.length) continue;
      const f = v.syllables[0];
      if (f.syllabic === 'single') f.syllabic = 'end';
      else if (f.syllabic === 'begin') f.syllabic = 'middle';
    }
  }
  return out;
}

// Recommended tesseract.js setup for the injected ocr() (docs/spike-ocr.md):
// tesseract.js 7 LSTM core, best_int models (NOT tessdata_best float: it
// aborts in tesseract.js 7), one masked text line per call (PSM 7).
// Round 2 benchmark, lyrics vs eng alone: eng+deu +0.005 at 1.4x OCR time,
// eng+deu+lat +0.005 at 2.1x (the lat model is weak, spike 5a) -> eng+deu.
const OCR_CONFIG = {
  langs: 'eng+deu',
  // second pass for rows with accents or low confidence (readLyrics), loaded on first use
  extraLangs: 'eng+deu+fra+spa+ita+ces',
  extraFiles: ['fra.traineddata.gz', 'spa.traineddata.gz', 'ita.traineddata.gz', 'ces.traineddata.gz'],
  oem: 1,
  files: ['eng.traineddata.gz', 'deu.traineddata.gz'],
  params: { tessedit_pageseg_mode: '7', user_defined_dpi: '300' },
};

module.exports = { _accentMarks: accentMarks, OCR_CONFIG, readLyrics, readPartLabels, readStanzas, syllabify, findTextLines, findTextLinesCC, toSyllables, splitSyllable, vowelGroups, detectLang, cropGray, DEFAULTS, _analyseRow: analyseRow };
