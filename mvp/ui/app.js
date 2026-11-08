/* global pdfjsLib, Tesseract, opensheetmusicdisplay, omrRequire, __omrBundle, __omrSessionModule */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const Sess = __omrSessionModule();
  // Pages are read one at a time (render, recognise, show, release), so the
  // cap is set by patience rather than memory: ~2-5 s per page.
  const MAX_PAGES = 40;
  const MAX_CODE_LINES = 3000;
  const PREVIEW_MEASURES = 48; // a longer score previews this many measures first
  const THUMB_W = 1400; // on-screen copy of each page (overlay keeps full-res coordinates)
  const SAMPLE = { url: 'assets/sample-st-anselm.pdf', name: 'sample-st-anselm.pdf', label: 'St. Anselm (J. Barnby), Methodist Hymnal 1905' };
  let busy = false;
  let stopAsked = false;
  let lastXML = '';
  let lastRes = null;

  const status = (t) => { $('status').textContent = t; };
  const store = {
    get(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  };
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const fmtBytes = (n) => n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(n < 10240 ? 1 : 0) + ' KB' : (n / 1048576).toFixed(1) + ' MB';
  const plural = (n, one, many) => `${n.toLocaleString('en')} ${n === 1 ? one : (many || one + 's')}`;
  const nextPaint = () => new Promise((r) => { let done = false; const go = () => { if (!done) { done = true; setTimeout(r, 0); } }; requestAnimationFrame(go); setTimeout(go, 60); });
  const fmtSecs = (s) => s < 60 ? `${Math.max(1, Math.round(s))} s` : `${Math.floor(s / 60)} min ${String(Math.round(s % 60)).padStart(2, '0')} s`;

  // ---------------------------------------------------------------- OCR ---
  let ocrWorkerP = null;
  function getOCR() {
    if (!ocrWorkerP) {
      const base = new URL('assets/', document.baseURI).href;
      ocrWorkerP = (async () => {
        if (typeof Tesseract === 'undefined') throw new Error('tesseract.js did not load');
        // Worker and core are fetched as text and started from blob: URLs, so
        // they run under the page policy (script-src allows blob:, not 'self').
        const blobOf = async (name) => {
          const r = await fetch(base + name);
          if (!r.ok) throw new Error(name + ' ' + r.status);
          return URL.createObjectURL(new Blob([await r.text()], { type: 'text/javascript' }));
        };
        const [workerURL, coreURL] = await Promise.all([blobOf('tesseract-worker.min.js'), blobOf('tesseract-core-simd-lstm.wasm.js')]);
        const w = await Tesseract.createWorker('eng', 1, {
          workerPath: workerURL,
          corePath: coreURL + '#core.js',
          langPath: base.replace(/\/$/, ''),
          gzip: true, workerBlobURL: false, cacheMethod: 'none',
        });
        await w.setParameters({ tessedit_pageseg_mode: '7', user_defined_dpi: '300' });
        return w;
      })();
      ocrWorkerP.catch(() => {});
    }
    return ocrWorkerP;
  }
  function withTimeout(p, ms) {
    return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('timed out')), ms))]);
  }
  function grayToCanvas(img) {
    const c = document.createElement('canvas');
    c.width = img.width; c.height = img.height;
    const ctx = c.getContext('2d');
    const id = ctx.createImageData(img.width, img.height);
    for (let i = 0; i < img.data.length; i++) { id.data[i * 4] = id.data[i * 4 + 1] = id.data[i * 4 + 2] = img.data[i]; id.data[i * 4 + 3] = 255; }
    ctx.putImageData(id, 0, 0);
    return c;
  }

  // ------------------------------------------------------------ stepper ---
  // Seven stages, each a notehead on one staff line. State comes from real
  // events: page rendering here, then the session's progress messages (each
  // carries {stage}). For several pages the first five stages repeat per page.
  const STEPS = [
    { id: 'render', title: 'Render' },
    { id: 'cleanup', title: 'Clean up' },
    { id: 'staves', title: 'Staves' },
    { id: 'notes', title: 'Notes' },
    { id: 'lyrics', title: 'Lyrics' },
    { id: 'parts', title: 'Parts' },
    { id: 'xml', title: 'MusicXML' },
  ];
  const SR_STATE = { complete: 'completed', current: 'current', upcoming: 'upcoming', skipped: 'skipped', failed: 'failed' };
  const stepper = {
    els: [], state: [], detail: [], cur: -1,
    build() {
      const ol = $('steps');
      ol.textContent = '';
      STEPS.forEach((s, i) => {
        const li = document.createElement('li');
        li.className = 'step';
        li.innerHTML = `<div class="step-row"><span class="head" aria-hidden="true"><span class="head-n">${i + 1}</span>` +
          '<svg class="i-done" viewBox="0 0 20 20"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
          '<svg class="i-fail" viewBox="0 0 20 20"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg></span>' +
          (i < STEPS.length - 1 ? '<span class="sep" aria-hidden="true"></span>' : '') + '</div>' +
          `<span class="step-title">${esc(s.title)}<span class="sr-only step-sr"></span></span><span class="step-detail"></span>`;
        ol.appendChild(li);
        this.els.push(li);
      });
      const cap = document.createElement('p');
      cap.className = 'step-caption'; cap.id = 'stepCaption'; cap.setAttribute('aria-hidden', 'true');
      ol.parentNode.appendChild(cap);
      this.reset();
    },
    reset() {
      this.state = STEPS.map(() => 'upcoming');
      this.detail = STEPS.map(() => '');
      this.cur = -1;
      this.paint();
    },
    index(id) { return STEPS.findIndex((s) => s.id === id); },
    go(id, detail) {
      const i = this.index(id);
      if (i < 0) return;
      if (i === this.cur && (detail == null || detail === this.detail[i])) return;
      for (let k = 0; k < STEPS.length; k++) {
        if (k < i) { if (this.state[k] !== 'skipped') this.state[k] = 'complete'; }
        else if (k === i) this.state[k] = 'current';
        else this.state[k] = 'upcoming';
      }
      if (i !== this.cur) { for (let k = i; k < STEPS.length; k++) this.detail[k] = ''; }
      if (detail != null) this.detail[i] = detail;
      this.cur = i;
      this.paint();
    },
    set(id, state, detail) {
      const i = this.index(id);
      if (i < 0) return;
      if (state) this.state[i] = state;
      if (detail != null) this.detail[i] = detail;
      this.paint();
    },
    finish() {
      this.state = this.state.map((s) => (s === 'skipped' || s === 'failed' ? s : 'complete'));
      this.cur = -1;
      this.paint();
    },
    fail(detail) {
      const i = this.cur >= 0 ? this.cur : 0;
      this.state[i] = 'failed';
      this.detail[i] = detail || 'failed';
      this.paint();
    },
    paint() {
      this.els.forEach((li, i) => {
        const st = this.state[i];
        li.dataset.state = st;
        if (st === 'current') li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
        li.querySelector('.step-sr').textContent = ', ' + SR_STATE[st];
        li.querySelector('.step-detail').textContent = this.detail[i];
      });
      const ci = this.cur >= 0 ? this.cur : this.state.indexOf('failed') >= 0 ? this.state.indexOf('failed') : STEPS.length - 1;
      const cap = $('stepCaption');
      if (cap) {
        const word = this.cur >= 0 ? 'Step' : this.state[ci] === 'failed' ? 'Stopped at step' : this.state.every((s) => s === 'upcoming') ? 'Step' : 'Finished step';
        cap.innerHTML = `${word} ${ci + 1} of ${STEPS.length}: <b>${esc(STEPS[ci].title)}</b>` + (this.detail[ci] ? ` <span>${esc(this.detail[ci])}</span>` : '');
      }
    },
    snapshot() { return STEPS.map((s, i) => ({ id: s.id, state: this.state[i], detail: this.detail[i] })); },
  };

  // Overall progress for the file row meter: pages share 92%, then parts and XML.
  const meter = {
    set(frac) {
      const pct = Math.max(0, Math.min(100, Math.round(frac * 100)));
      $('fileMeter').setAttribute('aria-valuenow', String(pct));
      $('fileMeterBar').style.width = pct + '%';
    },
  };
  const STAGE_FRAC = { render: 0.02, cleanup: 0.08, staves: 0.35, notes: 0.6, lyrics: 0.7 };

  // Map a progress message from the pipeline to a stage.
  function stageOf(msg, info) {
    if (info && typeof info === 'object' && info.stage && stepper.index(info.stage) >= 0) return info.stage;
    const m = String(msg || '');
    if (/render/i.test(m)) return 'render';
    if (/staves and notes|binari|deskew|clean|skew/i.test(m)) return 'cleanup';
    if (/stave|system/i.test(m)) return 'staves';
    if (/note|head|symbol|rhythm/i.test(m)) return 'notes';
    if (/lyric|ocr|text line/i.test(m)) return 'lyrics';
    if (/part|voice/i.test(m)) return 'parts';
    if (/musicxml|xml|writ/i.test(m)) return 'xml';
    return null;
  }

  // ----------------------------------------------------------- dropzone ---
  const drop = {
    state: 'idle', name: '', prose: false, nPages: 1,
    set(state, name, prose) {
      if (name != null) { this.name = name; this.prose = !!prose; }
      this.state = state;
      const el = $('drop');
      el.dataset.state = state;
      const n = this.name;
      const titles = {
        idle: 'Drop a scanned PDF or image',
        over: 'Drop it here',
        busy: `Converting ${n}`,
        done: `${n} converted`,
        stopped: `${n} partly converted`,
        error: `Could not convert ${n}`,
      };
      const hints = {
        idle: `A PDF, or one or more PNG or JPG pages. Up to ${MAX_PAGES} pages are read, one at a time.`,
        over: 'Release to convert. The file stays in this browser.',
        busy: this.nPages > 1 ? `Reading ${this.nPages} pages one at a time. Each page appears below when it is done; you can stop early and keep them.` : 'Reading the scan. This takes a few seconds per page.',
        done: 'Drop another scan here, or choose a file.',
        stopped: 'Stopped early: the result covers the pages read so far.',
        error: 'Try a sharper scan (200 dpi or more), or a PDF, PNG or JPG file.',
      };
      const t = titles[state] || titles.idle;
      // a file name is shown exactly as given; only a prose title is capitalised
      $('dropTitle').textContent = this.prose ? t.charAt(0).toUpperCase() + t.slice(1) : t;
      $('dropHint').textContent = hints[state] || hints.idle;
      $('dropLive').textContent = state === 'over' ? 'Release to convert' : '';
    },
  };
  function showFile(name, size) {
    $('fileRow').hidden = false;
    $('fileName').textContent = name;
    $('fileName').title = name;
    $('fileSize').textContent = size != null ? fmtBytes(size) : '';
    $('fileDone').toggleAttribute('hidden', true);
    $('fileEta').hidden = true;
    delete $('fileRow').dataset.done;
    meter.set(0);
  }
  function fileFinished(ok) {
    $('fileDone').toggleAttribute('hidden', !ok);
    $('fileEta').hidden = true;
    $('stop').hidden = true;
    if (ok) { $('fileRow').dataset.done = ''; meter.set(1); }
  }

  // ------------------------------------------------------- page sources ---
  // A document is a list of page sources, each rendered to gray only when its
  // turn comes, so a long PDF never sits in memory as images.
  function canvasToGray(c) {
    const ctx = c.getContext('2d');
    const d = ctx.getImageData(0, 0, c.width, c.height).data;
    const g = new Uint8ClampedArray(c.width * c.height);
    for (let i = 0, j = 0; i < g.length; i++, j += 4) g[i] = (d[j] * 299 + d[j + 1] * 587 + d[j + 2] * 114) / 1000;
    return { width: c.width, height: c.height, data: g };
  }
  async function pdfSource(buf, name) {
    if (typeof pdfjsLib === 'undefined') throw new Error('the PDF reader did not load; try a PNG or JPG instead');
    const pdf = await pdfjsLib.getDocument({ data: buf, isEvalSupported: false }).promise;
    const pages = [];
    for (let k = 1; k <= pdf.numPages; k++) {
      pages.push({
        label: pdf.numPages > 1 ? `${name}, page ${k}` : name,
        async render() {
          const page = await pdf.getPage(k);
          const v1 = page.getViewport({ scale: 1 });
          const scale = Math.max(1.5, Math.min(5, 2300 / v1.width));
          const vp = page.getViewport({ scale });
          const c = document.createElement('canvas');
          c.width = Math.round(vp.width); c.height = Math.round(vp.height);
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
          await page.render({ canvasContext: ctx, viewport: vp }).promise;
          const g = canvasToGray(c);
          c.width = c.height = 0; // free the canvas backing store now
          page.cleanup();
          return g;
        },
      });
    }
    return { pages, close: () => pdf.destroy() };
  }
  function imageSource(file) {
    return {
      pages: [{
        label: file.name,
        async render() {
          const bmp = await createImageBitmap(file);
          const s = bmp.width > 3200 ? 3200 / bmp.width : 1;
          const c = document.createElement('canvas');
          c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
          ctx.drawImage(bmp, 0, 0, c.width, c.height);
          if (bmp.close) bmp.close();
          const g = canvasToGray(c);
          c.width = c.height = 0;
          return g;
        },
      }],
      close() {},
    };
  }
  const isPDF = (f) => f.type === 'application/pdf' || /\.pdf$/i.test(f.name);
  const isImg = (f) => /^image\/(png|jpe?g)$/.test(f.type) || /\.(png|jpe?g)$/i.test(f.name);

  // ------------------------------------------------------------ engines ---
  // The session runs in a Web Worker built from the page's own code (the
  // pipeline bundle and ui/session.js as source text, started from a blob:
  // URL like the OCR worker), so the page stays responsive while a page is
  // recognised. If the worker cannot start, the same session runs here.
  let workerSrcURL = null;
  function workerURL() {
    if (!workerSrcURL) {
      const src = `${__omrBundle.toString()}\n__omrBundle();\nconst Sess=(${__omrSessionModule.toString()})();\nSess.workerMain(self, self.omrRequire);\n`;
      workerSrcURL = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
    }
    return workerSrcURL;
  }
  function workerEngine(ocrFn, onProgress) {
    return new Promise((resolveEngine, rejectEngine) => {
      let w;
      try { w = new Worker(workerURL()); } catch (e) { rejectEngine(e); return; }
      let alive = false;
      let waiter = null;
      const settle = (ok, v) => { const x = waiter; waiter = null; if (x) (ok ? x.resolve : x.reject)(v); };
      const wait = (type) => new Promise((resolve, reject) => { waiter = { type, resolve, reject }; });
      const timer = setTimeout(() => { if (!alive) { w.terminate(); rejectEngine(new Error('the recognition worker did not start')); } }, 5000);
      w.onmessage = (ev) => {
        const m = ev.data || {};
        if (m.t === 'alive') {
          alive = true; clearTimeout(timer);
          resolveEngine({
            kind: 'worker',
            init(useOcr) { const p = wait('ready'); w.postMessage({ t: 'init', ocr: !!useOcr }); return p; },
            addPage(gray, i, n) { const p = wait('page-done'); w.postMessage({ t: 'page', i, n, gray, maxW: THUMB_W }, [gray.data.buffer]); return p; },
            finish() { const p = wait('done'); w.postMessage({ t: 'finish' }); return p.then((m2) => m2.result); },
            dispose() { w.terminate(); settle(false, new Error('stopped')); },
          });
        } else if (m.t === 'progress') onProgress(m.msg, m.info);
        else if (m.t === 'ocr') {
          Promise.resolve().then(() => ocrFn(m.img)).then(
            (words) => w.postMessage({ t: 'ocr-res', id: m.id, words }),
            (e) => w.postMessage({ t: 'ocr-res', id: m.id, error: (e && e.message) || String(e) }));
        } else if (m.t === 'error') settle(false, new Error(m.msg));
        else if (waiter && m.t === waiter.type) settle(true, m);
      };
      w.onerror = (e) => {
        if (e && e.preventDefault) e.preventDefault();
        const err = new Error((e && e.message) || 'the recognition worker stopped');
        if (!alive) { clearTimeout(timer); w.terminate(); rejectEngine(err); } else settle(false, err);
      };
    });
  }
  function mainEngine(ocrFn, onProgress) {
    let session = null;
    return {
      kind: 'main',
      async init(useOcr) { session = Sess.createSession(omrRequire, { ocr: useOcr ? ocrFn : null, onProgress }); },
      async addPage(gray, i, n) {
        // the page analysis runs without a break here; paint its stage first
        onProgress(`Page ${i + 1}/${n}: finding staves and notes`, { stage: 'cleanup', page: i, pages: n });
        await nextPaint();
        const t0 = performance.now();
        const entry = await session.addPage(gray, i, n);
        if (!entry) return { view: null, ms: performance.now() - t0 };
        const view = Sess.pageView(entry, i);
        const thumb = Sess.shrink(entry.fr.gray, THUMB_W);
        Sess.release(entry);
        return { view, thumb, ms: performance.now() - t0 };
      },
      async finish() { await nextPaint(); return Sess.resultSummary(session.finish()); },
      dispose() { session = null; },
    };
  }
  async function startEngine(ocrFn, onProgress) {
    try { return await workerEngine(ocrFn, onProgress); } catch (e) { return mainEngine(ocrFn, onProgress); }
  }

  // ----------------------------------------------------- pages and marks ---
  // Each part gets a colour and a marker shape, so the overlay does not rely
  // on colour alone. Shapes are drawn the same way in the overlay and legend.
  const SHAPES = ['circle', 'triangle-down', 'square', 'diamond', 'triangle-up', 'hexagon'];
  function shapePoints(shape, r) {
    const pts = (n, rot) => Array.from({ length: n }, (_, i) => [Math.cos(rot + (i * 2 * Math.PI) / n) * r, Math.sin(rot + (i * 2 * Math.PI) / n) * r]);
    switch (shape) {
      case 'triangle-down': return pts(3, Math.PI / 2).map(([x, y]) => [x * 1.15, y * 1.15]);
      case 'triangle-up': return pts(3, -Math.PI / 2).map(([x, y]) => [x * 1.15, y * 1.15]);
      case 'square': return pts(4, Math.PI / 4);
      case 'diamond': return pts(4, 0).map(([x, y]) => [x * 1.1, y * 1.1]);
      case 'hexagon': return pts(6, 0);
      default: return null;
    }
  }
  function shapeSVG(shape, color, cls) {
    const p = shapePoints(shape, 5.2);
    const body = p ? `<polygon points="${p.map(([x, y]) => `${(7 + x).toFixed(2)},${(7 + y).toFixed(2)}`).join(' ')}"` : '<circle cx="7" cy="7" r="5.2"';
    return `<svg class="${cls || 'mark'}" viewBox="0 0 14 14" aria-hidden="true">${body} fill="${esc(color)}" stroke="${esc(color)}" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
  }
  const partShape = (i) => SHAPES[i % SHAPES.length];
  const OV = { staff: 'rgba(30,140,90,.6)', bar: 'rgba(43,55,176,.7)', none: '#8a8f96', found: '#2b37b0' };
  function markPath(shape, x, y, r) {
    const p = shapePoints(shape, r);
    if (!p) return `M${(x - r).toFixed(1)},${y.toFixed(1)}a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(2 * r).toFixed(1)},0a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(-2 * r).toFixed(1)},0z`;
    return 'M' + p.map(([dx, dy]) => `${(x + dx).toFixed(1)},${(y + dy).toFixed(1)}`).join('L') + 'z';
  }

  // Per-page state for the page strip and the plate. One page is shown at a
  // time; while converting, the plate follows the newest finished page until
  // the reader picks one.
  const PAGE_STATE = { queued: 'queued', render: 'rendering', work: 'reading', done: 'done', empty: 'no staves found', failed: 'could not be read', skipped: 'not read' };
  const book = {
    n: 0, total: 0, pages: [], sel: 0, follow: true, parts: null, headParts: null, urls: [],
    reset(n, total, labels) {
      this.urls.forEach((u) => URL.revokeObjectURL(u));
      this.urls = [];
      this.n = n; this.total = total; this.sel = 0; this.follow = true; this.parts = null; this.headParts = null;
      this.pages = Array.from({ length: n }, (_, i) => ({ i, state: 'queued', label: labels[i] || `Page ${i + 1}`, view: null, url: null, ms: 0 }));
      $('pageNav').hidden = n <= 1;
      const ol = $('pageChips');
      ol.textContent = '';
      this.pages.forEach((p) => {
        const li = document.createElement('li');
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'chip'; b.textContent = String(p.i + 1);
        b.addEventListener('click', () => { this.follow = false; this.show(p.i); });
        li.appendChild(b);
        ol.appendChild(li);
        p.el = b;
      });
      this.paintChips();
      this.show(0);
    },
    setState(i, state, extra) {
      const p = this.pages[i];
      if (!p) return;
      p.state = state;
      if (extra) Object.assign(p, extra);
      this.paintChips();
      if (state === 'done' || state === 'empty' || state === 'failed') { if (this.follow) this.show(i); else if (i === this.sel) this.show(i); }
      else if (i === this.sel) this.show(i);
    },
    counts() {
      const c = {};
      this.pages.forEach((p) => { c[p.state] = (c[p.state] || 0) + 1; });
      return c;
    },
    paintChips() {
      this.pages.forEach((p) => {
        const b = p.el;
        if (!b) return;
        b.dataset.state = p.state;
        const facts = p.view ? `, ${plural(p.view.nStaves, 'staff', 'staves')}, ${plural(p.view.heads.length, 'note head')}` : '';
        b.setAttribute('aria-label', `Page ${p.i + 1}: ${PAGE_STATE[p.state]}${facts}`);
        if (p.i === this.sel) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
      });
      const c = this.counts();
      const bits = [];
      if (c.done) bits.push(`${c.done} read`);
      if (c.work || c.render) bits.push('1 reading');
      if (c.queued) bits.push(`${c.queued} to go`);
      if (c.empty) bits.push(`${c.empty} without staves`);
      if (c.failed) bits.push(`${c.failed} failed`);
      if (c.skipped) bits.push(`${c.skipped} not read`);
      $('pgSum').textContent = bits.join(' · ');
    },
    show(i) {
      if (!this.pages.length) return;
      i = Math.max(0, Math.min(this.n - 1, i));
      this.sel = i;
      const p = this.pages[i];
      $('pgLabel').textContent = `Page ${i + 1} of ${this.n}` + (this.total > this.n ? ` (of ${this.total})` : '');
      $('pgPrev').disabled = i === 0;
      $('pgNext').disabled = i >= this.n - 1;
      this.paintChips();
      const host = $('pages');
      host.textContent = '';
      if (!p.view || !p.url) {
        const ph = document.createElement('div');
        ph.className = 'pageframe placeholder';
        ph.dataset.state = p.state;
        const msg = {
          queued: `Page ${i + 1} is waiting its turn.`, render: `Rendering page ${i + 1}.`, work: `Reading page ${i + 1}.`,
          empty: `No staves were found on page ${i + 1}, so nothing on it is in the result.`,
          failed: `Page ${i + 1} could not be read.`, skipped: `Page ${i + 1} was not read.`, done: `Page ${i + 1} is done.`,
        }[p.state] || '';
        ph.innerHTML = `<p>${esc(msg)}</p>`;
        host.appendChild(ph);
        return;
      }
      host.appendChild(this.frame(p));
    },
    frame(p) {
      const v = p.view;
      const fig = document.createElement('div');
      fig.className = 'pageframe';
      const img = document.createElement('img');
      img.src = p.url;
      img.width = v.width; img.height = v.height;
      img.decoding = 'async';
      img.alt = `Page ${p.i + 1} of the scan, straightened: ${plural(v.nStaves, 'staff', 'staves')}, ${plural(v.heads.length, 'note head')} found.`;
      fig.appendChild(img);
      fig.insertAdjacentHTML('beforeend', this.overlay(p));
      return fig;
    },
    overlay(p) {
      const v = p.view;
      const sw = Math.max(1.5, v.ss / 8);
      const pts = (a) => a.map(([x, y]) => `${x},${y}`).join(' ');
      let s = `<svg class="ov" viewBox="0 0 ${v.width} ${v.height}" preserveAspectRatio="none" aria-hidden="true" focusable="false">`;
      s += `<g fill="none" stroke="${OV.staff}" stroke-width="${sw.toFixed(1)}">` + v.staves.map((st) => `<polyline points="${pts(st.top)}"/><polyline points="${pts(st.bot)}"/>`).join('') + '</g>';
      s += `<g stroke="${OV.bar}" stroke-width="${sw.toFixed(1)}">` + v.barlines.map(([x, t, b]) => `<line x1="${x}" y1="${t}" x2="${x}" y2="${b}"/>`).join('') + '</g>';
      const hp = this.headParts && this.headParts.get(p.i);
      const parts = this.parts || [];
      const hw = Math.max(2, v.ss / 7).toFixed(1);
      if (!hp) {
        // still converting: heads are found but not yet assigned to parts
        s += `<path class="ov-found" fill="none" stroke="${OV.found}" stroke-width="${hw}" d="${v.heads.map(([x, y, r]) => markPath('circle', x, y, r)).join('')}"/>`;
      } else {
        const byPart = new Map();
        const none = [];
        v.heads.forEach(([x, y, r], k) => {
          const idx = hp[k] || [];
          if (!idx.length) { none.push(markPath('circle', x, y, r)); return; }
          idx.forEach((pi, j) => { if (!byPart.has(pi)) byPart.set(pi, []); byPart.get(pi).push(markPath(partShape(pi), x, y, r * (1 + 0.38 * j))); });
        });
        for (const [pi, d] of byPart) s += `<path fill="none" stroke="${esc(parts[pi] ? parts[pi].color : OV.none)}" stroke-width="${hw}" stroke-linejoin="round" d="${d.join('')}"/>`;
        if (none.length) s += `<path fill="none" stroke="${OV.none}" stroke-width="${hw}" stroke-dasharray="3 3" d="${none.join('')}"/>`;
      }
      return s + '</svg>';
    },
    applyResult(res) {
      this.parts = (res.score && res.score.parts) || [];
      this.headParts = new Map((res.pages || []).map((p) => [p.index, p.parts]));
      this.show(this.sel);
    },
  };
  function legend(parts) {
    const aux = '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><path d="M1 4h12M1 10h12" stroke="' + OV.staff + '" stroke-width="2"/></svg><span>Staff edges</span></li>' +
      '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v12" stroke="' + OV.bar + '" stroke-width="2.4"/></svg><span>Barline</span></li>';
    if (!parts) {
      $('legend').innerHTML = '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="' + OV.found + '" stroke-width="1.6"/></svg><span>Note head found</span></li>' + aux;
      return;
    }
    $('legend').innerHTML = parts.map((p, i) => `<li>${shapeSVG(partShape(i), p.color)}<span>${esc(p.name)}</span></li>`).join('') + aux +
      '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="' + OV.none + '" stroke-width="1.6" stroke-dasharray="2 2"/></svg><span>Head in no part</span></li>';
  }
  function applyOverlay() {
    const on = $('overlayToggle').getAttribute('aria-pressed') === 'true';
    $('pages').classList.toggle('ov-off', !on);
  }
  function thumbURL(t) {
    const c = grayToCanvas(t);
    return new Promise((resolve) => {
      const viaData = () => resolve(c.toDataURL('image/jpeg', 0.82));
      try { c.toBlob((b) => { if (b) resolve(URL.createObjectURL(b)); else viaData(); c.width = c.height = 0; }, 'image/jpeg', 0.82); } catch (e) { viaData(); }
    });
  }

  // ------------------------------------------------------------ results ---
  const CLEF = { G: 'treble', F: 'bass', C: 'C clef' };
  const clefName = (c) => CLEF[String(c).charAt(0)] || (c ? c + ' clef' : 'clef unknown');
  // Where each part's notes came from, in the user's terms.
  function provenance(p, sc) {
    const src = p.src || [];
    const clefs = sc.clefs || [];
    const nSt = (sc.layout && sc.layout.nSt) || clefs.length || 1;
    const staff = (s) => `staff ${s + 1} (${clefName(clefs[s])})`;
    if (!src.length) return '<b>Source</b> not recorded';
    if (src.length > 1) {
      const ids = src.map((s) => s.staff + 1);
      const cl = src.map((s) => clefName(clefs[s.staff])).join(' + ');
      return `<b>Kept together</b> as one ${src.length}-staff part: staves ${ids.join(' and ')} (${esc(cl)})`;
    }
    const s = src[0];
    if (s.voice === 1) return `<b>Split</b> from ${staff(s.staff)}, stems up`;
    if (s.voice === 2) return `<b>Split</b> from ${staff(s.staff)}, stems down`;
    if (s.voice === 'chordal') return nSt === 1 ? `<b>Whole staff</b> (${esc(clefName(clefs[s.staff]))}), not split` : `<b>Whole</b> of ${staff(s.staff)}, not split`;
    return `<b>From</b> ${staff(s.staff)}, voice ${esc(s.voice)}`;
  }
  const MAJOR = ['C♭', 'G♭', 'D♭', 'A♭', 'E♭', 'B♭', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F♯', 'C♯'];
  const MINOR = ['A♭', 'E♭', 'B♭', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F♯', 'C♯', 'G♯', 'D♯', 'A♯'];
  function keyText(f) {
    if (typeof f !== 'number' || f < -7 || f > 7) return 'key unknown';
    const acc = f === 0 ? 'no sharps or flats' : `${Math.abs(f)}${f > 0 ? '♯' : '♭'}`;
    return `${MAJOR[f + 7]} major or ${MINOR[f + 7]} minor (${acc})`;
  }

  function renderParts(res) {
    const sc = res.score || {};
    const parts = sc.parts || [];
    const list = $('parts');
    list.textContent = '';
    if (!parts.length) { $('partsSummary').textContent = 'No parts were recognised.'; return; }
    const nSt = (sc.layout && sc.layout.nSt) || (sc.clefs || []).length;
    const bits = [`${plural(parts.length, 'part')} from ${plural(nSt || 1, 'staff', 'staves')} per system`, keyText(sc.fifths)];
    if (sc.time && sc.time.beats) bits.push(`${sc.time.beats}/${sc.time.type}`);
    bits.push(plural(sc.measures || 0, 'measure'));
    if (res.pagesRead > 1) bits.push(`${res.pagesRead} pages`);
    $('partsSummary').innerHTML = bits.map(esc).join('<span class="sep-dot" aria-hidden="true">·</span><span class="sr-only">, </span>');
    parts.forEach((p, i) => {
      const li = document.createElement('li');
      const n = (sc.nNotes || [])[i] || 0;
      const range = (sc.ranges || [])[i];
      li.innerHTML = shapeSVG(partShape(i), p.color) +
        `<span class="part-name">${esc(p.name)}</span>` +
        `<span class="part-stats">${esc(plural(n, 'note'))}${range ? ' · ' + esc(range) : ''}</span>` +
        `<span class="part-src">${provenance(p, sc)}</span>`;
      list.appendChild(li);
    });
  }

  function renderLyrics(res) {
    const host = $('lyrics');
    host.textContent = '';
    const keys = Object.keys(res.lyricsBySystem || {}).sort((a, b) => {
      const [pa, sa] = a.split(':').map(Number), [pb, sb] = b.split(':').map(Number);
      return pa - pb || sa - sb;
    });
    // join each verse across systems, keyed by text band and verse number
    const verses = new Map();
    for (const k of keys) {
      for (const v of res.lyricsBySystem[k]) {
        const key = (v.band || 0) + ':' + v.number;
        if (!verses.has(key)) verses.set(key, { band: v.band || 0, number: v.number, words: '' });
        const ver = verses.get(key);
        let txt = '';
        (v.syllables || []).forEach((s) => { txt += s.text + (s.syllabic === 'begin' || s.syllabic === 'middle' ? '-' : ' '); });
        ver.words += (ver.words && !/-$/.test(ver.words) ? ' ' : '') + txt.trim();
      }
    }
    if (!verses.size) {
      const p = document.createElement('p');
      p.className = 'muted';
      p.textContent = res.ocrError ? `The text reader is unavailable (${res.ocrError}), so only notes were read.` : 'No lyric lines were found under the staves.';
      host.appendChild(p);
      return;
    }
    const bands = new Set([...verses.values()].map((v) => v.band));
    const sorted = [...verses.values()].sort((a, b) => a.band - b.band || a.number - b.number);
    for (const v of sorted) {
      const p = document.createElement('p');
      p.className = 'verse';
      const n = document.createElement('span');
      n.className = 'verse-n';
      n.textContent = (bands.size > 1 ? `St.${v.band + 1} ` : '') + v.number + '.';
      n.setAttribute('aria-label', (bands.size > 1 ? `Staff ${v.band + 1}, ` : '') + `verse ${v.number}`);
      const t = document.createElement('span');
      t.className = 'verse-t';
      t.textContent = v.words;
      p.appendChild(n); p.appendChild(t);
      host.appendChild(p);
    }
  }

  const INFO_RE = /^(Closed score|Grand staff|Staff \d+: two voices|Time signature inferred)|\bdetected\b/i;
  const ICON_WARN = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5l7 13H1z" fill="currentColor"/><path d="M8 6v4" style="stroke:var(--warn-bg)" stroke-width="1.8" stroke-linecap="round"/><circle cx="8" cy="12.3" r="1" style="fill:var(--warn-bg)"/></svg>';
  const ICON_INFO = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M8 7v4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="8" cy="4.8" r=".95" fill="currentColor"/></svg>';
  function renderWarnings(list) {
    const ul = $('warnings');
    ul.textContent = '';
    let nWarn = 0;
    for (const w of list) {
      const li = document.createElement('li');
      const info = INFO_RE.test(w);
      if (!info) nWarn++;
      li.className = info ? 'info' : 'warn';
      li.innerHTML = (info ? ICON_INFO : ICON_WARN) + `<span><span class="sr-only">${info ? 'Note' : 'Warning'}: </span>${esc(w)}</span>`;
      ul.appendChild(li);
    }
    if (!list.length) ul.innerHTML = '<li class="none">Nothing to report.</li>';
    $('warnCount').textContent = list.length ? `${nWarn} to check · ${list.length - nWarn} notes` : '';
  }

  // Facts for each completed stage, read from the pages and the result.
  function stepFacts(res, ocrUsed) {
    const views = book.pages.map((p) => p.view).filter(Boolean);
    const sum = (f) => views.reduce((a, v) => a + (f(v) || 0), 0);
    const maxSkew = views.length ? Math.max(...views.map((v) => Math.abs(v.skew || 0))) : 0;
    const read = book.pages.filter((p) => p.state === 'done' || p.state === 'empty').length;
    stepper.set('render', null, read < book.total ? `${read} of ${plural(book.total, 'page')}` : plural(read, 'page'));
    stepper.set('cleanup', null, maxSkew >= 0.05 ? `deskewed ${maxSkew.toFixed(1)}°` : 'no skew');
    stepper.set('staves', null, `${plural(sum((v) => v.nStaves), 'staff', 'staves')} · ${plural(sum((v) => v.nSystems), 'system')}`);
    stepper.set('notes', null, plural(sum((v) => v.heads.length), 'head'));
    const verses = Object.values(res.lyricsBySystem || {}).flat();
    const syl = verses.reduce((a, v) => a + ((v.syllables && v.syllables.length) || 0), 0);
    if (!ocrUsed) stepper.set('lyrics', 'skipped', 'text reader off');
    else stepper.set('lyrics', null, verses.length ? `${plural(verses.length, 'line')} · ${syl} syl.` : 'no lyric lines');
    const sc = res.score || {};
    stepper.set('parts', null, `${plural((sc.parts || []).length, 'part')} · ${plural(sc.measures || 0, 'bar')}`);
    const nLines = (sc.xml || '').split('\n').length;
    stepper.set('xml', null, plural(nLines, 'line'));
  }

  // ---------------------------------------------------------- code block ---
  function hlTag(tok) {
    if (/^<[?!]/.test(tok)) return `<span class="t-meta">${esc(tok)}</span>`;
    const m = tok.match(/^(<\/?)([^\s/>]+)([\s\S]*?)(\/?>)?$/);
    if (!m) return esc(tok);
    const attrs = esc(m[3]).replace(/([\w:.-]+)=(&quot;[^&]*?&quot;|'[^']*')/g, '<span class="t-attr">$1</span>=<span class="t-val">$2</span>');
    return `<span class="t-tag">${esc(m[1] + m[2])}</span>${attrs}<span class="t-tag">${esc(m[4] || '')}</span>`;
  }
  function highlight(line) {
    let out = '';
    const re = /<[^>]*>?|[^<]+/g;
    let m;
    while ((m = re.exec(line))) out += m[0][0] === '<' ? hlTag(m[0]) : esc(m[0]);
    return out;
  }
  function renderCode(xml) {
    lastXML = xml || '';
    const lines = lastXML.replace(/\n$/, '').split('\n');
    const shown = lastXML ? lines.slice(0, MAX_CODE_LINES) : [];
    $('gutter').textContent = shown.map((_, i) => i + 1).join('\n');
    $('code').innerHTML = shown.map(highlight).join('\n');
    $('xml').value = lastXML;
    $('xml').hidden = true;
    $('codeBody').hidden = false;
    $('xmlMeta').textContent = lastXML ? `${plural(lines.length, 'line')} · ${fmtBytes(new Blob([lastXML]).size)}` : '';
    const note = $('codeNote');
    note.hidden = lines.length <= MAX_CODE_LINES;
    note.textContent = note.hidden ? '' : `Showing the first ${MAX_CODE_LINES.toLocaleString('en')} of ${lines.length.toLocaleString('en')} lines. Copy takes the whole file.`;
    $('copy').disabled = !lastXML;
  }
  let copyTimer = 0;
  function copyXML() {
    if (!lastXML) return;
    const btn = $('copy'), msg = $('copied');
    const ok = () => {
      clearTimeout(copyTimer);
      btn.classList.add('is-copied');
      $('copyLabel').textContent = 'Copied';
      msg.textContent = `Copied ${lastXML.split('\n').length.toLocaleString('en')} lines of MusicXML.`;
      copyTimer = setTimeout(() => { btn.classList.remove('is-copied'); $('copyLabel').textContent = 'Copy'; msg.textContent = ''; }, 1200);
    };
    const fallback = () => {
      // clipboard refused: show the full text selected so the keyboard can copy it
      const ta = $('xml');
      ta.hidden = false;
      $('codeBody').hidden = true;
      $('codeNote').hidden = true;
      ta.focus();
      ta.select();
      msg.textContent = 'This page cannot reach the clipboard. The full text is selected: press Ctrl+C (Cmd+C on a Mac).';
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(lastXML).then(ok, fallback);
      else fallback();
    } catch (e) { fallback(); }
  }

  // ------------------------------------------------------------ preview ---
  let osmd = null;
  async function renderNotation(xml, measures, all) {
    const host = $('osmd');
    const note = $('osmdNote');
    note.textContent = '';
    $('osmdAll').hidden = true;
    if (!xml || typeof opensheetmusicdisplay === 'undefined') { note.textContent = 'The notation preview is unavailable because its library did not load.'; return; }
    // a long score draws its first measures; drawing all of it can hold the page for a while
    const capped = !all && measures > PREVIEW_MEASURES;
    try {
      host.textContent = '';
      osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(host, { autoResize: true, drawTitle: false, backend: 'svg', drawPartNames: true });
      if (capped) osmd.setOptions({ drawUpToMeasureNumber: PREVIEW_MEASURES });
      await osmd.load(xml);
      osmd.render();
      if (capped) {
        note.textContent = `The preview shows the first ${PREVIEW_MEASURES} of ${measures} measures; the MusicXML has them all.`;
        $('osmdAll').hidden = false;
      }
    } catch (e) {
      note.textContent = 'The preview could not draw this MusicXML: ' + e.message;
    }
  }

  // ---------------------------------------------------------------- run ---
  function setBusy(b) {
    busy = b;
    $('sample').disabled = b;
    $('choose').disabled = b;
  }
  // doc: async () => ({ pages: [{label, render}], total, size, close }); file: {name, size, title, label}
  async function run(openDoc, file) {
    if (busy) { status('Wait for the current conversion to finish.'); return; }
    setBusy(true);
    stopAsked = false;
    const t0 = performance.now();
    $('alert').hidden = true;
    stepper.reset();
    drop.nPages = 1;
    drop.set('busy', file.title || file.name, !!file.title);
    showFile(file.name, file.size);
    legend(null);
    let ocrUsed = false;
    let engine = null;
    let doc = null;
    try {
      status(`Reading ${file.label || file.name}`);
      stepper.go('render', null);
      const ocrP = getOCR();
      doc = await openDoc();
      const total = doc.pages.length;
      const n = Math.min(total, MAX_PAGES);
      const pages = doc.pages.slice(0, n);
      if (doc.size != null) $('fileSize').textContent = fmtBytes(doc.size);
      $('fileSize').textContent += ($('fileSize').textContent ? ' · ' : '') + (total > n ? `${n} of ${total} pages` : plural(total, 'page'));
      drop.nPages = n;
      drop.set('busy');
      book.reset(n, total, pages.map((p) => p.label));
      $('stop').hidden = n <= 1;
      $('stop').disabled = false;
      $('stop').textContent = 'Stop after this page';

      let ocr = null, ocrError = null;
      try {
        status('Loading the text reader');
        const w = await withTimeout(ocrP, 45000);
        ocr = async (img) => {
          const { data } = await w.recognize(grayToCanvas(img), {}, { text: true, blocks: true });
          const words = [];
          for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const wd of l.words)
            words.push({ text: wd.text, conf: wd.confidence, x0: wd.bbox.x0, x1: wd.bbox.x1 });
          return words;
        };
        ocrUsed = true;
      } catch (e) { ocrError = e.message || String(e); }

      // progress from the session: stage, page and lyric line
      let curPage = 0;
      let lastStatusKey = '';
      const pageDur = [];
      const eta = () => {
        if (n <= 1 || !pageDur.length) return '';
        const mean = pageDur.reduce((a, b) => a + b, 0) / pageDur.length;
        const left = (n - curPage - 0.5) * mean / 1000;
        return left > 2 ? `about ${fmtSecs(left)} left` : '';
      };
      const onProgress = (msg, info) => {
        const id = stageOf(msg, info);
        const m = String(msg || '');
        const lines = m.match(/\((\d+)\/(\d+) lines?\)/);
        if (id) {
          const detail = lines ? `line ${lines[1]} of ${lines[2]}` + (n > 1 ? ` · p.${curPage + 1}` : '') : n > 1 && STAGE_FRAC[id] != null ? `page ${curPage + 1} of ${n}` : null;
          stepper.go(id, detail);
          if (STAGE_FRAC[id] != null) {
            const within = id === 'lyrics' && lines ? 0.7 + 0.3 * (+lines[1] / +lines[2]) : STAGE_FRAC[id];
            meter.set(((curPage + within) / n) * 0.92);
          } else if (id === 'parts') meter.set(0.94);
        }
        // the status line (announced politely) changes per page and stage, not per lyric line
        const key = (id || '') + ':' + curPage;
        if (key !== lastStatusKey) { lastStatusKey = key; status(m.replace(/\s*\(\d+\/\d+ lines?\)/, '')); }
      };
      engine = await startEngine(ocr, onProgress);
      const engineKind = engine.kind;
      await engine.init(!!ocr);

      // Render page i+1 here while the worker reads page i.
      const renderPage = (i) => {
        book.setState(i, 'render');
        const p = pages[i].render();
        p.catch(() => {});
        return p;
      };
      const extraWarn = [];
      let nextGray = renderPage(0);
      let read = 0;
      for (let i = 0; i < n; i++) {
        curPage = i;
        if (stopAsked) { for (let k = i; k < n; k++) book.setState(k, 'skipped'); break; }
        const tp = performance.now();
        stepper.go('render', n > 1 ? `page ${i + 1} of ${n}` : null);
        meter.set((i / n) * 0.92);
        let gray;
        try { gray = await nextGray; } catch (e) {
          extraWarn.push(`Page ${i + 1} could not be rendered (${(e && e.message) || e}).`);
          book.setState(i, 'failed');
          nextGray = i + 1 < n ? renderPage(i + 1) : null;
          continue;
        }
        book.setState(i, 'work');
        const done = engine.addPage(gray, i, n);
        gray = null;
        nextGray = null;
        if (engine.kind === 'worker' && i + 1 < n && !stopAsked) nextGray = renderPage(i + 1);
        const r = await done;
        if (!nextGray && i + 1 < n && !stopAsked) nextGray = renderPage(i + 1);
        if (r.view && r.thumb) {
          const url = await thumbURL(r.thumb);
          if (/^blob:/.test(url)) book.urls.push(url);
          book.setState(i, 'done', { view: r.view, url, ms: r.ms });
        } else book.setState(i, 'empty');
        read++;
        pageDur.push(performance.now() - tp);
        if (n > 1) {
          const e = eta();
          $('fileEta').hidden = !e && !stopAsked;
          $('fileEta').textContent = stopAsked ? `Stopping after page ${i + 1}` : `${read} of ${n} pages read${e ? ' · ' + e : ''}`;
        }
        if (n > 1) status(`Page ${i + 1} of ${n} done.`);
      }
      $('stop').hidden = true;
      $('fileEta').hidden = true;
      const res = await engine.finish();
      engine.dispose();
      engine = null;
      res.ocrError = ocrError;
      res.pagesRead = read;
      if (ocrError) res.warnings.unshift('Lyrics were not read: the text reader is unavailable (' + ocrError + ').');
      if (stopAsked && read < n) res.warnings.unshift(`Stopped at your request after page ${read} of ${n}; the MusicXML covers pages 1 to ${read}.`);
      if (total > n) res.warnings.unshift(`Only the first ${n} of ${total} pages were read (the page reads at most ${MAX_PAGES}).`);
      res.warnings.unshift(...extraWarn);
      stepper.go('xml');
      meter.set(0.97);
      status('Writing MusicXML and drawing the preview');
      lastRes = res;
      legend((res.score && res.score.parts) || []);
      book.applyResult(res);
      renderParts(res);
      renderLyrics(res);
      renderWarnings(res.warnings || []);
      renderCode(res.score.xml);
      stepFacts(res, ocrUsed);
      await nextPaint();
      await renderNotation(res.score.xml, res.score.measures || 0, false);
      stepper.finish();
      fileFinished(true);
      const partial = stopAsked && read < n;
      drop.set(partial ? 'stopped' : 'done');
      status(`Done in ${((performance.now() - t0) / 1000).toFixed(1)} s: ${file.label || file.name}` + (n > 1 ? ` (${plural(read, 'page')})` : ''));
      window.__omrResult = {
        parts: res.score.parts.map((p) => p.name), nNotes: res.score.nNotes, measures: res.score.measures,
        lyrics: Object.values(res.lyricsBySystem).flat().length, warnings: res.warnings, xmlLength: (res.score.xml || '').length,
        steps: stepper.snapshot(), engine: engineKind, pages: { total, n, read, states: book.pages.map((p) => p.state) },
        secs: +((performance.now() - t0) / 1000).toFixed(2),
      };
    } catch (e) {
      const msg = (e && e.message) || String(e);
      stepper.fail('stopped');
      fileFinished(false);
      drop.set('error');
      status('Could not convert: ' + msg);
      const al = $('alert');
      al.hidden = false;
      al.textContent = `Could not convert ${file.name}: ${msg}. ` + (lastRes ? 'The previous result is still shown below.' : '');
      window.__omrResult = { error: msg, steps: stepper.snapshot() };
    } finally {
      if (engine) engine.dispose();
      if (doc && doc.close) { try { doc.close(); } catch (e) { /* already closed */ } }
      $('stop').hidden = true;
      setBusy(false);
    }
  }

  // Several files: PDFs and images in name order, as one document.
  function handleFiles(list) {
    const files = Array.prototype.slice.call(list || []).filter(Boolean);
    if (!files.length) return;
    const ok = files.filter((f) => isPDF(f) || isImg(f)).sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
    const bad = files.filter((f) => !(isPDF(f) || isImg(f)));
    if (!ok.length) {
      drop.set('error', files[0].name, false);
      status(`${files[0].name} is not a PDF, PNG or JPG file.`);
      return;
    }
    const size = ok.reduce((a, f) => a + f.size, 0);
    const name = ok.length === 1 ? ok[0].name : `${ok.length} files`;
    run(async () => {
      const parts = [];
      for (const f of ok) parts.push(isPDF(f) ? await pdfSource(new Uint8Array(await f.arrayBuffer()), f.name) : imageSource(f));
      const pages = parts.flatMap((p) => p.pages);
      if (bad.length) status(`Skipped ${bad.map((f) => f.name).join(', ')}: not a PDF, PNG or JPG file.`);
      return { pages, size, close: () => parts.forEach((p) => p.close()) };
    }, { name, size, title: ok.length > 1 ? `${ok.length} files` : null });
  }

  function loadSample() {
    run(async () => {
      const r = await fetch(SAMPLE.url);
      if (!r.ok) throw new Error('the sample file was not found (' + r.status + ')');
      const buf = new Uint8Array(await r.arrayBuffer());
      const size = buf.length; // read before pdf.js transfers (detaches) the buffer
      const src = await pdfSource(buf, SAMPLE.name);
      return { pages: src.pages, size, close: src.close };
    }, { name: SAMPLE.name, title: 'the sample hymn', label: 'sample: ' + SAMPLE.label, size: null });
  }

  // ---------------------------------------------------------------- wire ---
  stepper.build();
  $('choose').addEventListener('click', () => $('file').click());
  $('file').addEventListener('change', (e) => { const fs = Array.prototype.slice.call(e.target.files || []); e.target.value = ''; handleFiles(fs); });
  $('sample').addEventListener('click', loadSample);
  $('copy').addEventListener('click', copyXML);
  $('copy').disabled = true;
  $('stop').addEventListener('click', () => {
    stopAsked = true;
    $('stop').disabled = true;
    $('stop').textContent = 'Stopping…';
    $('fileEta').hidden = false;
    $('fileEta').textContent = 'Stopping after the page being read';
  });
  $('pgPrev').addEventListener('click', () => { book.follow = false; book.show(book.sel - 1); });
  $('pgNext').addEventListener('click', () => { book.follow = false; book.show(book.sel + 1); });
  $('pageChips').addEventListener('keydown', (e) => {
    // arrow keys move between page chips
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    const i = book.sel + (e.key === 'ArrowRight' ? 1 : -1);
    if (i < 0 || i >= book.n) return;
    e.preventDefault();
    book.follow = false;
    book.show(i);
    if (book.pages[i].el) book.pages[i].el.focus();
  });
  $('osmdAll').addEventListener('click', () => { if (lastRes) renderNotation(lastRes.score.xml, lastRes.score.measures || 0, true); });
  const ovSaved = store.get('ssr.overlay');
  if (ovSaved === 'off') $('overlayToggle').setAttribute('aria-pressed', 'false');
  $('overlayToggle').addEventListener('click', () => {
    const on = $('overlayToggle').getAttribute('aria-pressed') !== 'true';
    $('overlayToggle').setAttribute('aria-pressed', String(on));
    store.set('ssr.overlay', on ? 'on' : 'off');
    applyOverlay();
  });
  applyOverlay();

  // Drag and drop anywhere on the page. dragenter/dragleave fire for every
  // child crossed, so count depth and leave the "over" state only at zero.
  let depth = 0;
  let restState = 'idle';
  const hasFiles = (e) => !!(e.dataTransfer && Array.prototype.indexOf.call(e.dataTransfer.types || [], 'Files') >= 0);
  document.addEventListener('dragenter', (e) => {
    if (!hasFiles(e)) return;
    e.preventDefault();
    if (depth++ === 0) { restState = drop.state === 'over' ? restState : drop.state; drop.set('over'); }
  });
  document.addEventListener('dragleave', (e) => {
    if (!hasFiles(e)) return;
    depth = Math.max(0, depth - 1);
    if (depth === 0) drop.set(restState);
  });
  document.addEventListener('dragover', (e) => {
    if (!hasFiles(e)) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = busy ? 'none' : 'copy';
  });
  document.addEventListener('drop', (e) => {
    e.preventDefault();
    depth = 0;
    drop.set(restState);
    const fs = e.dataTransfer && e.dataTransfer.files;
    if (fs && fs.length) handleFiles(fs);
  });
  window.__dropDepth = () => depth;

  drop.set('idle');
  legend(null);
  renderWarnings([]);
  if (typeof pdfjsLib === 'undefined') status('The PDF reader did not load; PNG and JPG files still work.');
  loadSample();
})();
