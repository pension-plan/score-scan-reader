// Incremental conversion session: one page at a time, then the score.
// Runs in three places with the same code: a Web Worker (the normal path in
// the page), the main thread (fallback when a worker cannot start), and Node
// (ui/test/parity.js, which proves the result equals omr.convert()).
// The page bundles this file as one function so the worker can be built from
// its source text (Function.prototype.toString) without a second copy.
function __omrSessionModule() {
  'use strict';

  // Per-page work mirrors omr.convert() step for step: front, assemblePage,
  // readLyrics; finish() mirrors its buildScore and lyric filtering. When the
  // pipeline exports createConverter() with the same addPage/finish shape,
  // that is used instead and this copy is never run.
  function createSession(req, opts) {
    opts = opts || {};
    const progress = opts.onProgress || function () {};
    const omr = req('./omr');
    if (typeof omr.createConverter === 'function') {
      const c = omr.createConverter(opts);
      if (c && typeof c.addPage === 'function' && typeof c.finish === 'function') return c;
    }
    const { front } = req('./front');
    const { assemblePage } = req('./assemble');
    const { readLyrics } = req('./lyrics');
    const { buildScore } = req('./score');
    const pages = [];
    const lyricsBySystem = {};
    const warnings = [];
    return {
      // returns the page entry ({fr, asm, index}) or null when the page has no staves
      async addPage(gray, i, n) {
        progress(`Page ${i + 1}/${n}: finding staves and notes`, { stage: 'cleanup', page: i, pages: n });
        let fr;
        try {
          fr = front(gray, { onProgress: (m, info) => progress(`Page ${i + 1}/${n}: ${m}`, Object.assign({ page: i, pages: n }, info || {})) });
        } catch (e) { warnings.push(`Page ${i + 1}: image analysis failed (${e.message}).`); return null; }
        fr.warnings.forEach((w) => warnings.push(`Page ${i + 1}: ${w}`));
        if (!fr.staves.length) return null;
        progress(`Page ${i + 1}/${n}: reading note symbols`, { stage: 'notes', page: i, pages: n });
        const asm = assemblePage(fr, i);
        const entry = { fr, asm, index: i };
        pages.push(entry);
        if (opts.ocr) {
          progress(`Page ${i + 1}/${n}: reading lyrics`, { stage: 'lyrics', page: i, pages: n });
          try {
            const lyr = await readLyrics(fr, opts.ocr, (d, m) => progress(`Page ${i + 1}/${n}: reading lyrics (${d}/${m} lines)`, { stage: 'lyrics', page: i, pages: n }));
            for (const k in lyr) lyricsBySystem[i + ':' + k] = lyr[k];
          } catch (e) { warnings.push(`Lyrics OCR failed: ${e.message}`); }
        }
        return entry;
      },
      // this copy's finish() needs only fr.R and asm.comps (see release)
      releasePage: release,
      finish() {
        progress('Building parts', { stage: 'parts' });
        let score;
        try { score = buildScore(pages, lyricsBySystem, { ocr: !!opts.ocr, copyLyrics: !!opts.copyLyrics, debug: opts.debug }); }
        catch (e) { score = { parts: [], warnings: ['Assembly failed: ' + e.message], xml: '' }; }
        if (score.layout && Object.values(lyricsBySystem).some((l) => l.some((v) => v.used))) {
          for (const k in lyricsBySystem) lyricsBySystem[k] = lyricsBySystem[k].filter((v) => v.used);
        }
        if (!pages.length) warnings.push('No staves were detected. Try a cleaner or higher-resolution scan.');
        return { pages, score, lyricsBySystem, warnings: warnings.concat(score.warnings || []) };
      },
    };
  }

  // Large page buffers that nothing after the page step reads. buildScore
  // reads fr.R (bar contents) and asm.comps, so those stay. parity.js checks
  // that releasing these leaves the MusicXML unchanged.
  function release(entry) {
    if (!entry || !entry.fr) return;
    const fr = entry.fr;
    if (fr.gray) fr.gray = { width: fr.gray.width, height: fr.gray.height, data: null, released: true };
    fr.B = null;
    fr.L = null;
    // a spread's halves hold their own copies (the converter's own release
    // frees only the sheet)
    (entry.spread || []).forEach(release);
  }

  // Area-average downscale of a gray page (for the on-screen copy).
  function shrink(g, maxW) {
    const f = Math.min(1, maxW / g.width);
    if (f >= 1) return { width: g.width, height: g.height, data: new Uint8ClampedArray(g.data) };
    const w = Math.max(1, Math.round(g.width * f)), h = Math.max(1, Math.round(g.height * f));
    const out = new Uint8ClampedArray(w * h);
    const sx = g.width / w, sy = g.height / h;
    for (let y = 0; y < h; y++) {
      const y0 = Math.floor(y * sy), y1 = Math.max(y0 + 1, Math.floor((y + 1) * sy));
      for (let x = 0; x < w; x++) {
        const x0 = Math.floor(x * sx), x1 = Math.max(x0 + 1, Math.floor((x + 1) * sx));
        let s = 0, c = 0;
        for (let yy = y0; yy < y1 && yy < g.height; yy++) {
          const row = yy * g.width;
          for (let xx = x0; xx < x1 && xx < g.width; xx++) { s += g.data[row + xx]; c++; }
        }
        out[y * w + x] = c ? s / c : 255;
      }
    }
    return { width: w, height: h, data: out };
  }

  // A two-up spread (omr.js) is read as two pages: each half is cropped from
  // the straightened sheet at x0, then may be rescaled and straightened again
  // by its own front end. This maps a point of a half's frame back onto the
  // sheet (the inverse of front.js clean(): resample, then rotateGray).
  function halfToSheet(hfr, x0) {
    const w = hfr.gray.width, h = hfr.gray.height, f = hfr.scale || 1;
    const ang = hfr.skew && Math.abs(hfr.skew.angle || 0) >= 0.05 ? (-hfr.skew.angle * Math.PI) / 180 : 0;
    const c = Math.cos(ang), s = Math.sin(ang), cx = (w - 1) / 2, cy = (h - 1) / 2;
    return (x, y) => {
      const dx = x - cx, dy = y - cy;
      const rx = cx + c * dx - s * dy, ry = cy + s * dx + c * dy;
      return [x0 + (rx + 0.5) / f - 0.5, (ry + 0.5) / f - 0.5];
    };
  }
  // The halves of a spread entry that can be drawn on the sheet, in reading
  // order (the order buildScore received them), each with its x offset.
  function spreadHalves(entry) {
    const halves = (entry && entry.spread) || [];
    if (!halves.length) return null;
    const W = entry.fr.gray.width;
    const out = [];
    for (const hv of halves) {
      const hfr = hv.fr;
      // a half that its own front end turned cannot be mapped back simply
      if (!hfr || !hfr.gray || (hfr.orientation || 0) % 360) return null;
      const right = hv.index - Math.floor(hv.index) > 0.25;
      const x0 = typeof hv.x0 === 'number' ? hv.x0 : right ? W - hfr.gray.width / (hfr.scale || 1) : 0;
      out.push({ hv, map: halfToSheet(hfr, x0) });
    }
    return out;
  }

  // Every recognised symbol of a page (src/symbols.js), for the overlay. A
  // spread's symbols are its halves' drawn back on the sheet: boxes by their
  // mapped corners, stems and barlines by their ends.
  function pageSymbols(entry, req, halves) {
    let mod = null;
    try { mod = req && req('./symbols'); } catch (e) { mod = null; }
    if (!mod || !mod.pageSymbols) return null;
    const r1 = (v) => Math.round(v * 10) / 10;
    const read = (e) => { try { return mod.pageSymbols(e.fr, e.asm); } catch (err) { return null; } };
    if (!halves) return read(entry);
    const out = {};
    for (const { hv, map } of halves) {
      const sy = read(hv);
      if (!sy) continue;
      const f = hv.fr.scale || 1;
      for (const k of Object.keys(sy)) {
        out[k] = (out[k] || []).concat(sy[k].map((a) => {
          if (k === 'stems') { const p = map(a[0], a[1]), q = map(a[0], a[2]); return [r1((p[0] + q[0]) / 2), r1(p[1]), r1(q[1])]; }
          if (k === 'bars') { const p = map(a[0], a[1]), q = map(a[0], a[2]); return [r1((p[0] + q[0]) / 2), r1(p[1]), r1(q[1]), a[3], r1(map(a[4], a[1])[0]), r1(map(a[5], a[1])[0])]; }
          if (k === 'dots') { const p = map(a[0], a[1]); return [r1(p[0]), r1(p[1]), r1(a[2] / f)]; }
          const c = [map(a[0], a[1]), map(a[2], a[1]), map(a[0], a[3]), map(a[2], a[3])];
          const xs = c.map((p) => p[0]), ys = c.map((p) => p[1]);
          return [r1(Math.min(...xs)), r1(Math.min(...ys)), r1(Math.max(...xs)), r1(Math.max(...ys)), ...a.slice(4)];
        }));
      }
    }
    return out;
  }

  // Plain, cloneable overlay data for one page, in the deskewed frame. With
  // the module loader (req), it also carries every symbol read (sym).
  function pageView(entry, index, req) {
    const fr = entry.fr;
    const W = fr.gray.width, H = fr.gray.height;
    const r1 = (v) => Math.round(v * 10) / 10;
    // a spread's notes (and their parts) belong to its halves, so its heads
    // are the halves' heads drawn back on the whole sheet
    const halves = spreadHalves(entry);
    // [x, y, r, stem direction, staff top and bottom at x] (labels sit outside the staff)
    const edges = (f, h) => { const st = f.staves[h.staff]; return st ? [st.yAt(0, h.x), st.yAt(4, h.x)] : [h.y, h.y]; };
    const heads = halves
      ? halves.flatMap(({ hv, map }) => (hv.fr.heads || []).map((h) => {
        const [x, y] = map(h.x, h.y), [t, b] = edges(hv.fr, h);
        return [r1(x), r1(y), r1(((h.sp || hv.fr.ss) * 0.62) / (hv.fr.scale || 1)), h.stemDir || 0, r1(map(h.x, t)[1]), r1(map(h.x, b)[1])];
      }))
      : (fr.heads || []).map((h) => { const [t, b] = edges(fr, h); return [r1(h.x), r1(h.y), r1((h.sp || fr.ss) * 0.62), h.stemDir || 0, r1(t), r1(b)]; });
    const staves = fr.staves.map((st) => {
      const edge = (k) => {
        const pts = [];
        const step = Math.max(10, (st.right - st.left) / 60);
        for (let x = st.left; x < st.right + step / 2; x += step) { const xx = Math.min(x, st.right); pts.push([r1(xx), r1(st.yAt(k, xx))]); }
        return pts;
      };
      return { top: edge(0), bot: edge(4) };
    });
    return {
      index, width: W, height: H, ss: fr.ss,
      skew: (fr.skew && fr.skew.angle) || 0,
      staves,
      barlines: (fr.barlines || []).map((b) => [r1(b.x), r1(b.top), r1(b.bot)]),
      heads,
      nStaves: fr.staves.length,
      nSystems: halves
        ? halves.reduce((a, { hv }) => a + ((hv.asm && hv.asm.systems && hv.asm.systems.length) || (hv.fr.systems || []).length), 0)
        : (entry.asm && entry.asm.systems && entry.asm.systems.length) || (fr.systems || []).length,
      // how the page was read: quarter turns (front end, or the converter's
      // own retry), the clean-up mode, and the halves of a two-up spread
      orientation: (((fr.orientation || 0) + 90 * (entry.turns || 0)) % 360 + 360) % 360,
      mode: fr.mode || 'default',
      spread: halves ? halves.length : 0,
      sym: req ? pageSymbols(entry, req, halves) : null,
    };
  }

  // Plain sentences about how a page was read, for its caption.
  const MODE_NOTE = {
    raw: 'Read without the noise filter, which would erase its thin staff lines.',
    blur1: 'Smoothed before reading (a halftone screen or a broken photocopy).',
    blur2: 'Smoothed strongly before reading (a coarse halftone screen or a broken photocopy).',
  };
  function pageNotes(v) {
    const out = [];
    if (!v) return out;
    if (v.orientation === 180) out.push('The scan was upside down; it was read turned the right way up.');
    else if (v.orientation === 90 || v.orientation === 270) out.push(`The scan was on its side; it was read turned a quarter ${v.orientation === 90 ? 'clockwise' : 'anticlockwise'}.`);
    if (v.spread === 2) out.push('Two book pages side by side: the left page was read first, then the right.');
    else if (v.spread === 1) out.push('Two book pages side by side: only one of them had staves.');
    if (MODE_NOTE[v.mode]) out.push(MODE_NOTE[v.mode]);
    if (Math.abs(v.skew || 0) >= 0.5) out.push(`Straightened by ${Math.abs(v.skew).toFixed(1)}°.`);
    return out;
  }

  // Cloneable copy: plain objects and arrays to a depth, no functions or
  // typed arrays (score objects may point back at page data).
  function plain(v, depth) {
    if (v == null || typeof v !== 'object') return typeof v === 'function' ? undefined : v;
    if (depth <= 0 || ArrayBuffer.isView(v)) return undefined;
    if (Array.isArray(v)) return v.map((x) => plain(x, depth - 1));
    const o = {};
    for (const k of Object.keys(v)) { const x = plain(v[k], depth - 1); if (x !== undefined) o[k] = x; }
    return o;
  }
  function scoreSummary(score) {
    const s = score || {};
    const out = {};
    for (const k of Object.keys(s)) {
      if (k === 'layout') continue;
      const x = plain(s[k], 4);
      if (x !== undefined) out[k] = x;
    }
    if (s.layout) {
      const l = {};
      for (const k of Object.keys(s.layout)) if (k !== 'parts') { const x = plain(s.layout[k], 3); if (x !== undefined) l[k] = x; }
      out.layout = l;
    }
    return out;
  }
  function resultSummary(res) {
    return {
      score: scoreSummary(res.score),
      lyricsBySystem: plain(res.lyricsBySystem, 6) || {},
      warnings: (res.warnings || []).slice(),
      pages: pageParts(res.pages),
    };
  }
  // Parts of each drawn head, per page shown. The halves of a spread (index
  // i and i + 0.5) are one page on screen, so their lists join in reading
  // order, the order pageView() draws their heads in.
  function pageParts(pages) {
    const by = new Map(), notes = new Map();
    for (const p of pages.slice().sort((a, b) => a.index - b.index)) {
      const k = Math.floor(p.index);
      if (!by.has(k)) by.set(k, []);
      for (const h of p.fr.heads || []) by.get(k).push(h.parts ? h.parts.slice() : []);
      // what each drawn head was written as: [step, alter, octave, quarters,
      // type, dots, tuplet number], or 0 when no part wrote it
      if (!notes.has(k)) notes.set(k, []);
      for (const h of p.fr.heads || []) {
        const pt = h.pitch, d = h.shown;
        notes.get(k).push(pt && d ? [pt.step, pt.alter || 0, pt.octave, Math.round(d.q * 1000) / 1000, d.type || '', d.dots || 0, d.tuplet || 0] : 0);
      }
    }
    return [...by].map(([index, parts]) => ({ index, parts, notes: notes.get(index) || [] }));
  }

  // ------------------------------------------------------------ worker side
  // Messages in: init {ocr}, page {i, n, gray}, finish. Out: ready, progress,
  // ocr {id, img} (answered by ocr-res), page-done, done, error.
  function workerMain(scope, req) {
    let session = null;
    let ocrSeq = 0;
    const pending = new Map();
    const post = (m, tr) => scope.postMessage(m, tr || []);
    const ocr = (img) => new Promise((resolve, reject) => {
      const id = ++ocrSeq;
      pending.set(id, { resolve, reject });
      const data = new Uint8ClampedArray(img.data); // own buffer, safe to transfer
      post({ t: 'ocr', id, img: { width: img.width, height: img.height, data } }, [data.buffer]);
    });
    let queue = Promise.resolve();
    scope.onmessage = (ev) => {
      const m = ev.data || {};
      if (m.t === 'ocr-res') {
        const p = pending.get(m.id);
        if (p) { pending.delete(m.id); if (m.error) p.reject(new Error(m.error)); else p.resolve(m.words || []); }
        return;
      }
      // page and finish messages run strictly in order
      queue = queue.then(() => handle(m)).catch((e) => post({ t: 'error', msg: (e && e.message) || String(e) }));
    };
    async function handle(m) {
      if (m.t === 'init') {
        session = createSession(req, {
          ocr: m.ocr ? ocr : null,
          onProgress: (msg, info) => post({ t: 'progress', msg, info: plain(info, 2) || null }),
        });
        post({ t: 'ready' });
      } else if (m.t === 'page') {
        const t0 = Date.now();
        const entry = await session.addPage(m.gray, m.i, m.n);
        m.gray = null;
        if (!entry) { post({ t: 'page-done', i: m.i, ms: Date.now() - t0, view: null }); return; }
        const view = pageView(entry, m.i, req);
        const thumb = shrink(entry.fr.gray, m.maxW || 1400);
        // only a session that says what it can spare frees page buffers
        if (session.releasePage) { session.releasePage(entry); (entry.spread || []).forEach((h) => session.releasePage(h)); }
        post({ t: 'page-done', i: m.i, ms: Date.now() - t0, view, thumb }, [thumb.data.buffer]);
      } else if (m.t === 'finish') {
        const res = session.finish();
        post({ t: 'done', result: resultSummary(res) });
      }
    }
    post({ t: 'alive' });
  }

  return { createSession, release, shrink, pageView, pageNotes, plain, scoreSummary, resultSummary, workerMain };
}
if (typeof module !== 'undefined' && module.exports) module.exports = __omrSessionModule;
