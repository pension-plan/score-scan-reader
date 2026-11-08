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

  // Plain, cloneable overlay data for one page, in the deskewed frame.
  function pageView(entry, index) {
    const fr = entry.fr;
    const W = fr.gray.width, H = fr.gray.height;
    const r1 = (v) => Math.round(v * 10) / 10;
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
      heads: (fr.heads || []).map((h) => [r1(h.x), r1(h.y), r1((h.sp || fr.ss) * 0.62)]),
      nStaves: fr.staves.length,
      nSystems: (entry.asm && entry.asm.systems && entry.asm.systems.length) || (fr.systems || []).length,
    };
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
      pages: res.pages.map((p) => ({
        index: p.index,
        parts: (p.fr.heads || []).map((h) => (h.parts ? h.parts.slice() : [])),
      })),
    };
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
        const view = pageView(entry, m.i);
        const thumb = shrink(entry.fr.gray, m.maxW || 1400);
        // only a session that says what it can spare frees page buffers
        if (session.releasePage) session.releasePage(entry);
        post({ t: 'page-done', i: m.i, ms: Date.now() - t0, view, thumb }, [thumb.data.buffer]);
      } else if (m.t === 'finish') {
        const res = session.finish();
        post({ t: 'done', result: resultSummary(res) });
      }
    }
    post({ t: 'alive' });
  }

  return { createSession, release, shrink, pageView, plain, scoreSummary, resultSummary, workerMain };
}
if (typeof module !== 'undefined' && module.exports) module.exports = __omrSessionModule;
