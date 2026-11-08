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
  // Two bundled samples: the rag (piano grand staff, converted on load) and a
  // real 1905 hymnal scan (closed-score SATB with lyrics: the four-part split).
  const SAMPLES = {
    rag: { url: 'assets/sample-maple-leaf-rag.pdf', name: 'sample-maple-leaf-rag.pdf', title: 'the sample rag', label: 'Maple Leaf Rag (Scott Joplin, 1899), engraved and aged like a scan' },
    hymn: { url: 'assets/sample-st-anselm.pdf', name: 'sample-st-anselm.pdf', title: 'the sample hymn', label: 'St. Anselm (Methodist Hymnal, 1905), a real scan' },
  };
  // Every redistributable benchmark scan (assets/samples.json, written by
  // tools/sync-samples.mjs), offered in the "All examples" picker.
  let catalogue = [];
  let busy = false;
  let stopAsked = false;
  let lastXML = '';
  let lastRes = null;

  const status = (t) => { $('status').textContent = t; };
  const store = {
    get(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
    del(k) { try { window.localStorage.removeItem(k); } catch (e) { /* storage blocked */ } },
  };
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const fmtBytes = (n) => n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(n < 10240 ? 1 : 0) + ' KB' : (n / 1048576).toFixed(1) + ' MB';
  const plural = (n, one, many) => `${n.toLocaleString('en')} ${n === 1 ? one : (many || one + 's')}`;
  const nextPaint = () => new Promise((r) => { let done = false; const go = () => { if (!done) { done = true; setTimeout(r, 0); } }; requestAnimationFrame(go); setTimeout(go, 60); });
  const mark = (n) => { try { performance.mark('ssr:' + n); } catch (e) { /* marks unsupported */ } };
  const fmtSecs = (s) => s < 60 ? `${Math.max(1, Math.round(s))} s` : `${Math.floor(s / 60)} min ${String(Math.round(s % 60)).padStart(2, '0')} s`;

  // ---------------------------------------------------------------- OCR ---
  // Languages, engine and page mode come from the pipeline (lyrics.js
  // OCR_CONFIG), so the page reads text the way the benchmark does.
  function ocrConfig() {
    const def = { langs: 'eng', oem: 1, params: { tessedit_pageseg_mode: '7', user_defined_dpi: '300' } };
    try {
      const c = omrRequire('./lyrics').OCR_CONFIG;
      if (c && typeof c.langs === 'string' && /^[a-z_]+(\+[a-z_]+)*$/.test(c.langs)) return { langs: c.langs, oem: c.oem == null ? 1 : c.oem, params: Object.assign({}, def.params, c.params || {}) };
    } catch (e) { /* bundle without lyrics config */ }
    return def;
  }
  let ocrLangs = '';
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
        const cfg = ocrConfig();
        const make = (langs) => Tesseract.createWorker(langs, cfg.oem, {
          workerPath: workerURL,
          corePath: coreURL + '#core.js',
          langPath: base.replace(/\/$/, ''),
          gzip: true, workerBlobURL: false, cacheMethod: 'none',
        });
        // the pipeline's language set (eng+deu: umlauts and German words), or
        // English alone if a language file is missing
        let w, langs = cfg.langs;
        try { w = await make(langs); } catch (e) { if (langs === 'eng') throw e; langs = 'eng'; w = await make(langs); }
        await w.setParameters(cfg.params);
        ocrLangs = langs;
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
  // pdf.js decodes page images in its worker. Its worker script is on the page
  // as a plain script (which makes pdf.js decode on the main thread); give it
  // a real worker instead: a blob: worker that importScripts the same pinned
  // URL. If that worker does not answer, pdf.js keeps its main-thread fallback.
  let pdfWorkerP = null;
  function pdfWorkerReady() {
    if (!pdfWorkerP) {
      pdfWorkerP = (async () => {
        const tag = document.querySelector('script[src*="pdf.worker"]');
        if (typeof pdfjsLib === 'undefined' || !pdfjsLib.GlobalWorkerOptions || !tag || typeof Worker === 'undefined') return false;
        const src = `try{importScripts(${JSON.stringify(tag.src)});self.postMessage({ssrPdfWorker:1})}catch(e){self.postMessage({ssrPdfWorker:0,msg:String(e&&e.message||e)})}`;
        let w;
        try { w = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' }))); } catch (e) { return false; }
        const ok = await new Promise((resolve) => {
          const t = setTimeout(() => resolve(false), 6000);
          const on = (ev) => { if (ev.data && 'ssrPdfWorker' in ev.data) { clearTimeout(t); w.removeEventListener('message', on); resolve(!!ev.data.ssrPdfWorker); } };
          w.addEventListener('message', on);
          w.addEventListener('error', (e) => { e.preventDefault(); clearTimeout(t); resolve(false); }, { once: true });
        });
        if (!ok) { w.terminate(); return false; }
        pdfjsLib.GlobalWorkerOptions.workerPort = w;
        return true;
      })();
    }
    return pdfWorkerP;
  }
  async function pdfSource(buf, name) {
    if (typeof pdfjsLib === 'undefined') throw new Error('the PDF reader did not load; try a PNG or JPG instead');
    await pdfWorkerReady();
    const pdf = await pdfjsLib.getDocument({ data: buf, isEvalSupported: false }).promise;
    const pages = [];
    for (let k = 1; k <= pdf.numPages; k++) {
      pages.push({
        label: pdf.numPages > 1 ? `${name}, page ${k}` : name,
        async render() {
          mark('render');
          const page = await pdf.getPage(k);
          const v1 = page.getViewport({ scale: 1 });
          const scale = Math.max(1.5, Math.min(5, 2300 / v1.width));
          const vp = page.getViewport({ scale });
          const c = document.createElement('canvas');
          c.width = Math.round(vp.width); c.height = Math.round(vp.height);
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
          await page.render({ canvasContext: ctx, viewport: vp }).promise;
          mark('gray');
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
      // OMR_ASSET_BASE: a blob: worker cannot resolve relative URLs; src/cv.js loads OpenCV.js from it
      const src = `self.OMR_ASSET_BASE=${JSON.stringify(new URL('assets/', location.href).href)};\n${__omrBundle.toString()}\n__omrBundle();\nconst Sess=(${__omrSessionModule.toString()})();\nSess.workerMain(self, self.omrRequire);\n`;
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
      const eng = { kind: 'worker', dead: false };
      const settle = (ok, v) => { const x = waiter; waiter = null; if (x) { clearTimeout(x.timer); (ok ? x.resolve : x.reject)(v); } };
      // a page that never answers (worker out of memory, say) ends the run instead of hanging it
      const wait = (type, ms) => eng.dead ? Promise.reject(new Error('the recognition worker stopped')) : new Promise((resolve, reject) => {
        waiter = { type, resolve, reject, timer: setTimeout(() => { eng.dead = true; w.terminate(); settle(false, new Error(`the recognition worker did not answer within ${ms / 1000} s`)); }, ms) };
      });
      const timer = setTimeout(() => { if (!alive) { w.terminate(); rejectEngine(new Error('the recognition worker did not start')); } }, 5000);
      w.onmessage = (ev) => {
        const m = ev.data || {};
        if (m.t === 'alive') {
          alive = true; clearTimeout(timer);
          resolveEngine(Object.assign(eng, {
            init(useOcr) { const p = wait('ready', 60000); w.postMessage({ t: 'init', ocr: !!useOcr }); return p; },
            addPage(gray, i, n) { const p = wait('page-done', 300000); if (!eng.dead) w.postMessage({ t: 'page', i, n, gray, maxW: THUMB_W }, [gray.data.buffer]); return p; },
            finish() { const p = wait('done', 300000); if (!eng.dead) w.postMessage({ t: 'finish' }); return p.then((m2) => m2.result); },
            dispose() { eng.dead = true; w.terminate(); settle(false, new Error('stopped')); },
          }));
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
        if (!alive) { clearTimeout(timer); w.terminate(); rejectEngine(err); } else { eng.dead = true; w.terminate(); settle(false, err); }
      };
    });
  }
  function mainEngine(ocrFn, onProgress) {
    let session = null;
    return {
      kind: 'main', dead: false,
      async init(useOcr) { session = Sess.createSession(omrRequire, { ocr: useOcr ? ocrFn : null, onProgress }); },
      async addPage(gray, i, n) {
        // the page analysis runs without a break here; paint its stage first
        onProgress(`Page ${i + 1}/${n}: finding staves and notes`, { stage: 'cleanup', page: i, pages: n });
        await nextPaint();
        const t0 = performance.now();
        const entry = await session.addPage(gray, i, n);
        if (!entry) return { view: null, ms: performance.now() - t0 };
        const view = Sess.pageView(entry, i, omrRequire);
        const thumb = Sess.shrink(entry.fr.gray, THUMB_W);
        if (session.releasePage) session.releasePage(entry);
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
  const OV = { staff: 'rgba(84,110,122,.6)', bar: 'rgba(43,55,176,.7)', none: '#8a8f96', found: '#2b37b0' };
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
        renderLayers(null);
        repair.setOn(false);
        $('repairToggle').disabled = true;
        repair.renderList();
        return;
      }
      host.appendChild(this.frame(p));
      renderLayers(p.view);
      fitLabels();
      repair.attach(host.querySelector('.pageframe'), p);
      $('repairToggle').disabled = false;
      // how the page was read: turned, smoothed, split as a spread, straightened
      const notes = Sess.pageNotes(p.view);
      if (notes.length) {
        const ul = document.createElement('ul');
        ul.className = 'pagenotes';
        ul.setAttribute('aria-label', `How page ${i + 1} was read`);
        ul.innerHTML = notes.map((t) => `<li>${esc(t)}</li>`).join('');
        host.appendChild(ul);
      }
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
      const ss = v.ss;
      const sw = Math.max(1.5, ss / 8);
      const f1 = (n) => (Math.round(n * 10) / 10).toString();
      const pts = (a) => a.map(([x, y]) => `${x},${y}`).join(' ');
      const sy = v.sym || {};
      const g = (layer, body, attrs) => (body ? `<g class="ov-l ov-${layer}"${attrs || ''}>${body}</g>` : '');
      const rect = (b, pad, extra) => `<rect x="${f1(b[0] - pad)}" y="${f1(b[1] - pad)}" width="${f1(b[2] - b[0] + 2 * pad)}" height="${f1(b[3] - b[1] + 2 * pad)}"${extra || ''}/>`;
      let s = `<svg class="ov" viewBox="0 0 ${v.width} ${v.height}" preserveAspectRatio="none" aria-hidden="true" focusable="false">`;
      // staves and barlines (double / final pairs drawn as two lines)
      let bars = `<g class="ov-staff" fill="none" stroke="${OV.staff}" stroke-width="${f1(sw)}">` + v.staves.map((st) => `<polyline points="${pts(st.top)}"/><polyline points="${pts(st.bot)}"/>`).join('') + '</g>';
      const barList = sy.bars || v.barlines.map(([x, t, b]) => [x, t, b, 'single', x, x]);
      bars += `<g stroke="${OV.bar}" stroke-width="${f1(sw)}">` + barList.map(([x, t, b, type, x0, x1]) => (type === 'single' ? `<line x1="${x}" y1="${t}" x2="${x}" y2="${b}"/>`
        : `<line x1="${x0}" y1="${t}" x2="${x0}" y2="${b}"/><line x1="${x1}" y1="${t}" x2="${x1}" y2="${b}" stroke-width="${f1(sw * 2)}"/>`)).join('') + '</g>';
      s += g('bars', bars);
      // stems and beams under the heads
      let nb = '';
      if (sy.stems && sy.stems.length) nb += `<path class="ov-stem" fill="none" stroke-width="${f1(sw)}" d="${sy.stems.map(([x, a, b]) => `M${x},${a}V${b}`).join('')}"/>`;
      if (sy.beams && sy.beams.length) nb += `<g class="ov-beam" fill="none" stroke-width="${f1(sw)}">${sy.beams.map((b) => rect(b, 0)).join('')}</g>`;
      const hp = this.headParts && this.headParts.get(p.i);
      const parts = this.parts || [];
      const hw = Math.max(2, ss / 7).toFixed(1);
      if (!hp) {
        // still converting: heads are found but not yet assigned to parts
        nb += `<path class="ov-found ov-head" stroke="${OV.found}" stroke-width="${hw}" d="${v.heads.map(([x, y, r]) => markPath('circle', x, y, r)).join('')}"/>`;
      } else {
        const byPart = new Map();
        const none = [];
        v.heads.forEach(([x, y, r], k) => {
          const idx = hp[k] || [];
          if (!idx.length) { none.push(markPath('circle', x, y, r)); return; }
          idx.forEach((pi, j) => { if (!byPart.has(pi)) byPart.set(pi, []); byPart.get(pi).push(markPath(partShape(pi), x, y, r * (1 + 0.38 * j))); });
        });
        for (const [pi, d] of byPart) nb += `<path class="ov-head" stroke="${esc(parts[pi] ? parts[pi].color : OV.none)}" stroke-width="${hw}" stroke-linejoin="round" d="${d.join('')}"/>`;
        if (none.length) nb += `<path class="ov-head" stroke="${OV.none}" stroke-width="${hw}" stroke-dasharray="3 3" d="${none.join('')}"/>`;
      }
      s += g('notes', nb);
      // rests: rounded boxes
      s += g('rests', (sy.rests || []).map((b) => rect(b, ss * 0.15, ` rx="${f1(ss * 0.3)}"`)).join(''), ` fill="none" stroke-width="${f1(sw * 1.2)}"`);
      // clefs: corner brackets (dashed when the clef was assumed, not read)
      const corners = (b, pad) => {
        const x0 = b[0] - pad, y0 = b[1] - pad, x1 = b[2] + pad, y1 = b[3] + pad, l = Math.min(ss * 0.8, (x1 - x0) / 2, (y1 - y0) / 2);
        return `M${f1(x0)},${f1(y0 + l)}V${f1(y0)}H${f1(x0 + l)}M${f1(x1 - l)},${f1(y0)}H${f1(x1)}V${f1(y0 + l)}M${f1(x1)},${f1(y1 - l)}V${f1(y1)}H${f1(x1 - l)}M${f1(x0 + l)},${f1(y1)}H${f1(x0)}V${f1(y1 - l)}`;
      };
      const clefs = sy.clefs || [];
      s += g('clefs', clefs.filter((c) => c[5] !== 2).map((c) => rect(c, ss * 0.2, ' class="bg"')).join('') + (clefs.some((c) => c[5] !== 2) ? `<path d="${clefs.filter((c) => c[5] !== 2).map((c) => corners(c, ss * 0.2)).join('')}"/>` : '') +
        clefs.filter((c) => c[5] === 2).map((c) => rect(c, 0, ' stroke-dasharray="4 4"')).join(''), ` fill="none" stroke-width="${f1(sw * 1.6)}"`);
      // key signatures: dashed boxes; time signatures: pills
      s += g('keys', (sy.keys || []).map((b) => rect(b, ss * 0.2, ` stroke-dasharray="${f1(sw * 3)} ${f1(sw * 1.5)}"`)).join(''), ` fill="none" stroke-width="${f1(sw * 1.3)}"`);
      s += g('times', (sy.times || []).map((b) => rect(b, ss * 0.25, ` rx="${f1(Math.min(b[2] - b[0], b[3] - b[1]) / 2 + ss * 0.25)}"`)).join(''), ` fill="none" stroke-width="${f1(sw * 1.3)}"`);
      // accidentals (square boxes), augmentation dots (rings), tuplet numbers (dotted boxes)
      const sub = (cls, body) => (body ? `<g class="${cls}">${body}</g>` : '');
      s += g('marks', sub('ov-acc', (sy.accs || []).map((b) => rect(b, ss * 0.1)).join('')) +
        sub('ov-dot', (sy.dots || []).map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${f1(r + ss * 0.15)}"/>`).join('')) +
        sub('ov-tup', (sy.tuplets || []).map((b) => rect(b, ss * 0.15, ` stroke-dasharray="${f1(sw)} ${f1(sw)}"`)).join('')), ` fill="none" stroke-width="${f1(sw)}"`);
      // lyric syllables the score used: a bracket under each
      const lyr = this.lyricBoxes(p);
      s += g('lyrics', lyr.map(([x0, y0, x1, y1]) => `<path d="M${f1(x0)},${f1(y1 - ss * 0.3)}V${f1(y1 + ss * 0.15)}H${f1(x1)}V${f1(y1 - ss * 0.3)}"/>`).join(''), ` fill="none" stroke-width="${f1(sw)}"`);
      // ink nothing explains: swiped with a yellow highlighter
      const unk = (sy.unknown || []).filter((b) => !lyr.some((l) => b[0] < l[2] && b[2] > l[0] && b[1] < l[3] && b[3] > l[1]));
      // text read off the page (titles, credits, instrument names, bar
      // numbers, tempo and expression), dynamics and hairpins, and the curves
      // and lines around the notes: a box each, text and dynamics labelled
      const named = (b, label) => `<g><title>${esc(label)}</title>${rect(b, ss * 0.12)}<text x="${f1(b[0])}" y="${f1(b[1] - ss * 0.3)}" font-size="${f1(ss * 0.75)}">${esc(label)}</text></g>`;
      s += g('text', (sy.text || []).filter((t) => t[4] !== 'lyrics').map((t) => named(t, t[5])).join(''), ` stroke-width="${f1(sw)}"`);
      s += g('dyns', (sy.dyns || []).concat(sy.wedges || []).map((d) => named(d, d[4])).join(''), ` stroke-width="${f1(sw)}"`);
      s += g('curves', [].concat(sy.slurs || [], sy.fermatas || [], sy.braces || [], sy.ledgers || []).map((b) => rect(b, ss * 0.08)).join(''), ` stroke-width="${f1(sw * 0.8)}" stroke-dasharray="${f1(sw * 2)} ${f1(sw)}"`);
      s += g('unknown', unk.map((b) => rect(b, ss * 0.18, ` rx="${f1(ss * 0.25)}"`)).join(''));
      s += g('labels', this.labels(p));
      return s + '</svg>';
    },
    // syllable boxes of the lyric lines the score used on page p (not on a
    // two-up spread, whose halves read their own text)
    lyricBoxes(p) {
      const out = [];
      const by = (lastRes && lastRes.lyricsBySystem) || {};
      if (!p.view || p.view.spread) return out;
      for (const k of Object.keys(by)) {
        if (Number(k.split(':')[0]) !== p.i) continue;
        for (const v of by[k]) if (v.y != null && v.y1 != null) for (const sl of v.syllables || []) if (sl.x0 != null && sl.x1 != null) out.push([sl.x0, v.y, sl.x1, v.y1]);
      }
      return out;
    },
    // Text labels: each note's pitch and written value above the staff for
    // the upper voice (stems up) and below it for the lower, a rest's value,
    // each clef, key and time signature. Stacks move outwards until clear of
    // the labels already placed.
    labels(p) {
      const v = p.view, ss = v.ss, sy = v.sym || {};
      const fs = ss * 0.85, lh = fs * 1.1, cw = fs * 0.56;
      const notes = this.headNotes && this.headNotes.get(p.i);
      const items = []; // {x, y (anchor edge), side -1 up / 1 down, lines: [[text, cls]]}
      if (notes) {
        const cols = [];
        v.heads.forEach((h, k) => {
          const n = notes[k];
          if (!n) return;
          const [x, y, r, dir, top, bot] = h;
          const side = dir === -1 ? 1 : -1;
          let c = cols.find((o) => o.side === side && Math.abs(o.x - x) < 0.7 * ss && Math.abs(o.top - (top != null ? top : y)) < 2 * ss);
          if (!c) { c = { x, side, top: top != null ? top : y - 2 * ss, bot: bot != null ? bot : y + 2 * ss, heads: [] }; cols.push(c); }
          c.heads.push({ y, r, n });
        });
        for (const c of cols) {
          const hs = c.heads.sort((a, b) => a.y - b.y);
          const pitch = [...new Set(hs.map((h) => pitchText(h.n)))];
          const durs = [...new Set(hs.map((h) => durText(h.n[3], h.n[4], h.n[5], h.n[6])))];
          const pl = pitch.map((t) => [t, 'lp']), dl = [durs.join(' / '), 'ld'];
          const y = c.side < 0 ? Math.min(c.top, hs[0].y - hs[0].r) - 0.4 * ss : Math.max(c.bot, hs[hs.length - 1].y + hs[hs.length - 1].r) + 0.4 * ss;
          // the value outermost: above the pitches over the staff, below them under it
          items.push({ x: c.x, y, side: c.side, lines: c.side < 0 ? [dl].concat(pl) : pl.concat([dl]) });
        }
      }
      for (const r of sy.rests || []) items.push({ x: (r[0] + r[2]) / 2, y: r[1] - 0.3 * ss, side: -1, lines: [[restText(r[4], r[5], r[6], r[7]), 'lr']] });
      for (const c of sy.clefs || []) items.push({ x: (c[0] + c[2]) / 2, y: c[1] - 0.3 * ss, side: -1, lines: [[clefLabel(c[4]) + (c[5] === 1 ? ' (change)' : c[5] === 2 ? ' (assumed)' : ''), 'ls']] });
      for (const k of sy.keys || []) items.push({ x: (k[0] + k[2]) / 2, y: k[3] + 0.4 * ss, side: 1, lines: [[keyLabel(k[4]) + (k[5] ? ' (change)' : ''), 'ls']] });
      const time = lastRes && lastRes.score && lastRes.score.time;
      for (const t of sy.times || []) {
        const txt = t[4] ? `${t[6] === 'common' ? 'C = ' : t[6] === 'cut' ? '¢ = ' : ''}${t[4]}/${t[5]}` : time && time.beats ? `${time.beats}/${time.type}` : 'time signature';
        items.push({ x: (t[0] + t[2]) / 2, y: t[1] - 0.4 * ss, side: -1, lines: [[txt, 'ls']] });
      }
      // a double bar or repeat once per system (barlines are found staff by staff)
      const barSeen = [];
      for (const b of (sy.bars || []).slice().sort((u, w) => u[1] - w[1])) {
        if (b[3] === 'single' || barSeen.some((o) => Math.abs(o[0] - b[0]) < ss && b[1] - o[2] < 2.5 * ss && o[3] === b[3])) { if (b[3] !== 'single') barSeen.push(b); continue; }
        barSeen.push(b);
        items.push({ x: b[0], y: b[1] - 0.3 * ss, side: -1, lines: [[{ double: 'double bar', 'repeat-start': 'repeat ‖:', 'repeat-end': 'repeat :‖', 'repeat-both': 'repeat :‖:' }[b[3]] || b[3], 'lb']] });
      }
      // place: outermost line first for stacks above, nearest first below
      const placed = [];
      const hit = (a) => placed.some((b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0);
      let out = '';
      items.sort((a, b) => a.x - b.x);
      for (const it of items) {
        const w = Math.max(...it.lines.map(([t]) => t.length)) * cw + 0.2 * ss, h = it.lines.length * lh;
        const bx = { x0: it.x - w / 2, x1: it.x + w / 2, y0: it.side < 0 ? it.y - h : it.y, y1: it.side < 0 ? it.y : it.y + h };
        for (let k = 0; k < 40 && hit(bx); k++) { const d = it.side * lh * 0.5; bx.y0 += d; bx.y1 += d; }
        placed.push(bx);
        it.lines.forEach(([t, cls], j) => {
          out += `<text class="${cls}" x="${(Math.round(it.x * 10) / 10)}" y="${(Math.round((bx.y0 + (j + 0.82) * lh) * 10) / 10)}">${esc(t)}</text>`;
        });
      }
      return out ? `<g font-size="${(Math.round(fs * 10) / 10)}" stroke-width="${(Math.round(fs * 0.3 * 10) / 10)}" text-anchor="middle">${out}</g>` : '';
    },
    applyResult(res) {
      this.parts = (res.score && res.score.parts) || [];
      this.headParts = new Map((res.pages || []).map((p) => [p.index, p.parts]));
      this.headNotes = new Map((res.pages || []).map((p) => [p.index, p.notes || []]));
      this.show(this.sel);
    },
  };
  // Label texts
  const ACC = { 1: '♯', 2: '𝄪', '-1': '♭', '-2': '𝄫' };
  const pitchText = (n) => `${n[0]}${ACC[n[1]] || ''}${n[2]}`;
  const TYPE_FRAC = { maxima: '8/1', long: '4/1', breve: '2/1', whole: '1', half: '1/2', quarter: '1/4', eighth: '1/8', '16th': '1/16', '32nd': '1/32', '64th': '1/64', '128th': '1/128' };
  function durText(q, type, dots, tuplet) {
    let t = TYPE_FRAC[type];
    if (!t) return `${+q.toFixed(2)} q`;
    t += '.'.repeat(dots || 0);
    return tuplet ? `${t} (${tuplet})` : t;
  }
  const REST_FRAC = { whole: '1', half: '1/2', quarter: '1/4', flag1: '1/8', flag2: '1/16', flag3: '1/32', flag4: '1/64', breve: '2 bars', long: '4 bars' };
  function restText(kind, q, dots, multi) {
    if (kind === 'multi') return `rest, ${multi || '?'} bars`;
    return `rest ${REST_FRAC[kind] || kind}${'.'.repeat(dots || 0)}`;
  }
  const C_NAME = { C1: 'soprano', C2: 'mezzo', C3: 'alto', C4: 'tenor', C5: 'baritone' };
  function clefLabel(c) {
    c = String(c || '');
    if (c === 'G8') return 'G clef 8vb';
    if (c === 'G8va') return 'G clef 8va';
    if (/^C[1-5]$/.test(c)) return `C clef (${C_NAME[c]})`;
    return c ? `${c.charAt(0)} clef` : 'clef';
  }
  const keyLabel = (f) => (f ? `${Math.abs(f)}${f > 0 ? '♯' : '♭'}` : 'no ♯/♭');
  // Overlay layers the reader can switch off one by one (remembered).
  const LAYERS = [
    ['notes', 'Notes, stems, beams'], ['rests', 'Rests'], ['clefs', 'Clefs'], ['keys', 'Key signatures'], ['times', 'Time signatures'],
    ['bars', 'Staves, barlines'], ['marks', 'Accidentals, dots, tuplets'], ['lyrics', 'Lyric syllables'], ['labels', 'Pitch and value labels'],
    ['text', 'Titles, names, text'], ['dyns', 'Dynamics, hairpins'], ['curves', 'Slurs, ties, fermatas, braces, ledger lines'], ['unknown', 'Not recognised'],
  ];
  const LAYER_ICON = {
    notes: '<path d="M9 2v8" stroke-width="1.4" class="ovk-stem"/><circle cx="6.5" cy="10" r="2.6" stroke-width="1.6"/>',
    rests: '<rect x="2.5" y="3" width="9" height="8" rx="2.2" stroke-width="1.8"/>',
    clefs: '<path d="M2 5V2h3M9 2h3v3M12 9v3H9M5 12H2V9" stroke-width="1.8"/>',
    keys: '<rect x="2" y="2.5" width="10" height="9" stroke-width="1.6" stroke-dasharray="3 1.6"/>',
    times: '<rect x="3.5" y="1.5" width="7" height="11" rx="3.5" stroke-width="1.6"/>',
    bars: '<path d="M1 4h12M1 10h12" stroke-width="1.4" class="ovk-staff"/><path d="M7 1v12" stroke-width="2.2"/>',
    marks: '<rect x="1" y="3" width="4.5" height="8" stroke-width="1.4" class="ovk-acc"/><circle cx="8.6" cy="7" r="1.8" stroke-width="1.4" class="ovk-dot"/><rect x="11" y="4" width="2.4" height="6" stroke-width="1" class="ovk-tup"/>',
    lyrics: '<path d="M2 8v3h10V8" stroke-width="1.6"/>',
    labels: '<text x="7" y="10.5" font-size="9" text-anchor="middle" stroke="none" fill="currentColor">C5</text>',
    text: '<text x="7" y="10.5" font-size="9.5" text-anchor="middle" stroke="none" fill="currentColor" font-family="serif">Aa</text>',
    dyns: '<text x="5.5" y="10.5" font-size="9" text-anchor="middle" stroke="none" fill="currentColor" font-style="italic" font-weight="700" font-family="serif">f</text><path d="M8.5 7l4.5-2.5M8.5 7l4.5 2.5" stroke-width="1"/>',
    curves: '<path d="M2 9c2-4 8-4 10 0" stroke-width="1.6"/>',
    unknown: '<rect x="1.5" y="3.5" width="11" height="7" rx="1.6" stroke-width=".8"/>',
  };
  const layerOff = new Set((() => { try { return JSON.parse(store.get('ssr.layers') || '[]'); } catch (e) { return []; } })());
  function layerCounts(v) {
    const sy = (v && v.sym) || {};
    return {
      notes: v ? v.heads.length : 0, rests: (sy.rests || []).length, clefs: (sy.clefs || []).length, keys: (sy.keys || []).length, times: (sy.times || []).length,
      bars: v ? (sy.bars || v.barlines).length : 0, marks: (sy.accs || []).length + (sy.dots || []).length + (sy.tuplets || []).length,
      lyrics: null, labels: null, unknown: (sy.unknown || []).length,
      text: (sy.text || []).filter((t) => t[4] !== 'lyrics').length, dyns: (sy.dyns || []).length + (sy.wedges || []).length,
      curves: (sy.slurs || []).length + (sy.fermatas || []).length + (sy.braces || []).length + (sy.ledgers || []).length,
    };
  }
  function renderLayers(v) {
    const c = layerCounts(v);
    $('layers').innerHTML = LAYERS.map(([k, name]) => {
      const n = c[k];
      const cnt = n == null || !v ? '' : ` <span class="layer-n">${n.toLocaleString('en')}</span>`;
      return `<li><button type="button" class="layer" data-layer="${k}" aria-pressed="${!layerOff.has(k)}"><svg class="mark ovk-${k}" viewBox="0 0 14 14" aria-hidden="true" fill="none">${LAYER_ICON[k]}</svg><span>${esc(name)}${cnt}</span>${k === 'labels' ? '<span class="layer-hint">zoom in to read</span>' : ''}</button></li>`;
    }).join('');
  }
  function applyLayers() {
    const host = $('pages');
    LAYERS.forEach(([k]) => host.classList.toggle('hide-' + k, layerOff.has(k)));
  }
  function legend(parts) {
    const aux = '';
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
    $('layers').hidden = !on;
  }
  // Labels are drawn only while they can be read: a staff space of at least
  // 11 screen pixels (the page zoom times the browser's pinch zoom).
  function fitLabels() {
    const fr = $('pages').querySelector('.pageframe:not(.placeholder)');
    const p = book.pages[book.sel];
    let small = true;
    if (fr && p && p.view) {
      const img = fr.querySelector('img');
      const vv = window.visualViewport;
      const k = (img.clientWidth / p.view.width) * (vv && vv.scale ? vv.scale : 1);
      small = p.view.ss * k < 11;
    }
    $('pages').classList.toggle('lbl-small', small);
    $('layers').classList.toggle('lbl-small', small);
  }
  const ZOOMS = [1, 1.5, 2, 3, 4, 6];
  let zoom = ZOOMS.includes(+store.get('ssr.zoom')) ? +store.get('ssr.zoom') : 1;
  function applyZoom() {
    $('pages').style.setProperty('--zoom', String(zoom));
    $('zoomLabel').textContent = zoom === 1 ? 'Fit' : `${zoom}×`;
    $('zoomOut').disabled = zoom <= ZOOMS[0];
    $('zoomIn').disabled = zoom >= ZOOMS[ZOOMS.length - 1];
    fitLabels();
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
    // a label from the pipeline (score.js) wins when it provides one
    if (p.layoutLabel) return esc(p.layoutLabel);
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
    const turned = views.filter((v) => v.orientation).length, smooth = views.filter((v) => v.mode && v.mode !== 'default').length, spreads = views.filter((v) => v.spread).length;
    const clean = [];
    if (turned) clean.push(views.length > 1 ? `${turned} turned` : `turned ${views.find((v) => v.orientation).orientation}°`);
    if (spreads) clean.push(views.length > 1 ? `${spreads} split` : '2-up split');
    if (smooth) clean.push(views.length > 1 ? `${smooth} smoothed` : 'smoothed');
    clean.push(maxSkew >= 0.05 ? `deskewed ${maxSkew.toFixed(1)}°` : 'no skew');
    stepper.set('cleanup', null, clean.join(' · '));
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
  // The first measures of a long score as their own MusicXML, so the preview
  // parses and draws only what it shows.
  function previewXML(xml, upTo) {
    return xml.replace(/<measure\b[^>]*\bnumber="(\d+)"[\s\S]*?<\/measure>\s*/g, (m, n) => (+n > upTo ? '' : m));
  }
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
      mark('osmd-load');
      await osmd.load(capped ? previewXML(xml, PREVIEW_MEASURES) : xml);
      mark('osmd-render');
      osmd.render();
      mark('osmd-end');
      if (capped) {
        note.textContent = `The preview shows the first ${PREVIEW_MEASURES} of ${measures} measures; the MusicXML has them all.`;
        $('osmdAll').hidden = false;
      }
    } catch (e) {
      note.textContent = 'The preview could not draw this MusicXML: ' + e.message;
    }
    // playback (ui/player.js): the whole MusicXML, the drawn preview, the scan's heads
    if (window.ScorePlayer) window.ScorePlayer.attach({ xml, osmd, book, res: lastRes });
  }

  // ---------------------------------------------------------------- run ---
  function setBusy(b) {
    busy = b;
    $('sample').disabled = b;
    $('sampleHymn').disabled = b;
    $('sampleAll').disabled = b;
    $('choose').disabled = b;
  }
  // the previous result stays visible but dimmed while a new scan is read
  function setStale(on) {
    const had = !!lastRes;
    $('staleNote').hidden = !(on && had);
    ['margin', 'previewPanel'].forEach((id) => { if (on && had) $(id).dataset.stale = ''; else delete $(id).dataset.stale; });
  }
  // doc: async () => ({ pages: [{label, render}], total, size, close }); file: {name, size, title, label}
  async function run(openDoc, file) {
    if (busy) { status('Wait for the current conversion to finish.'); return; }
    setBusy(true);
    setStale(true);
    stopAsked = false;
    const t0 = performance.now();
    $('alert').hidden = true;
    stepper.reset();
    drop.nPages = 1;
    drop.set('busy', file.title || file.name, !!file.title);
    showFile(file.name, file.size);
    repair.open(file.name, file.size);
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
        const left = (n - curPage - 1) * mean / 1000;
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
        const key = n > 1 ? String(curPage) : (id || '') + ':' + curPage;
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
          if (n === 1) throw e;
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
        let r;
        try { r = await done; } catch (e) {
          // one bad page does not end a long document; a stopped worker does
          if (engine.dead || n === 1) throw e;
          extraWarn.push(`Page ${i + 1} could not be read (${(e && e.message) || e}).`);
          book.setState(i, 'failed');
          if (!nextGray && i + 1 < n && !stopAsked) nextGray = renderPage(i + 1);
          continue;
        }
        if (!nextGray && i + 1 < n && !stopAsked) nextGray = renderPage(i + 1);
        mark('page-done');
        if (r.view && r.thumb) {
          const url = await thumbURL(r.thumb);
          mark('show');
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
      mark('finish');
      const res = await engine.finish();
      mark('results');
      engine.dispose();
      engine = null;
      res.ocrError = ocrError;
      res.pagesRead = read;
      if (ocrError) res.warnings.unshift('Lyrics were not read: the text reader is unavailable (' + ocrError + ').');
      if (stopAsked && read < n) res.warnings.unshift(`Stopped at your request after page ${read} of ${n}; the MusicXML covers ${read === 1 ? 'page 1' : `pages 1 to ${read}`}.`);
      if (total > n) res.warnings.unshift(`Only the first ${n} of ${total} pages were read (the page reads at most ${MAX_PAGES}).`);
      res.warnings.unshift(...extraWarn);
      stepper.go('xml');
      meter.set(0.97);
      status('Writing MusicXML and drawing the preview');
      lastRes = res;
      setStale(false);
      legend((res.score && res.score.parts) || []);
      book.applyResult(res);
      renderParts(res);
      renderLyrics(res);
      renderWarnings(res.warnings || []);
      mark('code');
      renderCode(res.score.xml);
      mark('facts');
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
        ocrLangs: ocrUsed ? ocrLangs : null, file: file.name,
        pageNotes: book.pages.map((p) => Sess.pageNotes(p.view)),
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
      setStale(false);
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

  function loadSample(kind) {
    const S = typeof kind === 'object' ? kind : SAMPLES[kind] || SAMPLES.rag;
    const pick = catalogue.findIndex((c) => 'assets/' + c.file === S.url);
    $('sampleAll').value = pick >= 0 ? String(pick) : '';
    run(async () => {
      const r = await fetch(S.url);
      if (!r.ok) throw new Error('the sample file was not found (' + r.status + ')');
      const buf = new Uint8Array(await r.arrayBuffer());
      const size = buf.length; // read before pdf.js transfers (detaches) the buffer
      const src = await pdfSource(buf, S.name);
      return { pages: src.pages, size, close: src.close };
    }, { name: S.name, title: S.title, label: 'sample: ' + S.label, size: null });
  }

  // ---------------------------------------------------------------- wire ---
  stepper.build();
  $('choose').addEventListener('click', () => $('file').click());
  $('file').addEventListener('change', (e) => { const fs = Array.prototype.slice.call(e.target.files || []); e.target.value = ''; handleFiles(fs); });
  $('sample').addEventListener('click', () => loadSample('rag'));
  fetch('assets/samples.json').then((r) => (r.ok ? r.json() : [])).then((list) => {
    catalogue = Array.isArray(list) ? list : [];
    const sel = $('sampleAll');
    const groups = new Map();
    catalogue.forEach((c, i) => {
      if (!groups.has(c.group)) { const g = document.createElement('optgroup'); g.label = c.group; groups.set(c.group, g); sel.appendChild(g); }
      const o = document.createElement('option');
      o.value = String(i);
      o.textContent = c.title;
      o.title = c.license;
      groups.get(c.group).appendChild(o);
    });
    const cur = catalogue.findIndex((c) => c.file === 'sample-maple-leaf-rag.pdf');
    if (cur >= 0 && !sel.value) sel.value = String(cur);
  }).catch(() => { $('sampleAll').hidden = true; });
  $('sampleAll').addEventListener('change', (e) => {
    const c = catalogue[+e.target.value];
    if (!c || e.target.value === '') return;
    loadSample({ url: 'assets/' + c.file, name: c.file, title: c.title, label: c.title + ' (' + c.group.toLowerCase().replace(/s$/, '') + ')' });
  });
  $('sampleHymn').addEventListener('click', () => loadSample('hymn'));
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
  $('layers').addEventListener('click', (e) => {
    const b = e.target.closest('button.layer');
    if (!b) return;
    const k = b.dataset.layer;
    if (layerOff.has(k)) layerOff.delete(k); else layerOff.add(k);
    b.setAttribute('aria-pressed', String(!layerOff.has(k)));
    store.set('ssr.layers', JSON.stringify([...layerOff]));
    applyLayers();
  });
  renderLayers(null);
  applyLayers();
  const setZoom = (dir) => {
    const i = ZOOMS.indexOf(zoom);
    zoom = ZOOMS[Math.max(0, Math.min(ZOOMS.length - 1, (i < 0 ? 0 : i) + dir))];
    store.set('ssr.zoom', String(zoom));
    applyZoom();
  };
  $('zoomIn').addEventListener('click', () => setZoom(1));
  $('zoomOut').addEventListener('click', () => setZoom(-1));
  applyZoom();
  window.addEventListener('resize', fitLabels);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', fitLabels);

  // ------------------------------------------------------ repair marks ---
  // The reader draws over a page to mark what the reading got wrong. Marks are
  // kept in the page's full-resolution frame (the overlay's viewBox), per page
  // and per document (file name and size), and export as JSON for a later
  // repair pass (docs/SDD.md, repair notes).
  const RP_TOOL = { pen: 'Pen', line: 'Line', box: 'Box', ellipse: 'Circle' };
  const repair = {
    doc: null, file: null, size: 0, marks: {}, hist: [], on: false, tool: 'pen', drawing: null, seq: 0,
    key() { return 'ssr.repair:' + this.doc; },
    open(name, size) {
      this.size = typeof size === 'number' ? size : null; this.doc = `${name}:${this.size == null ? 'sample' : this.size}`; this.file = name; this.hist = []; this.marks = {};
      try { const j = JSON.parse(store.get(this.key()) || 'null'); if (j && j.marks) this.marks = j.marks; } catch (e) { this.marks = {}; }
      this.seq = Math.max(0, ...Object.values(this.marks).flat().map((m) => m.id || 0));
    },
    save() {
      if (!this.doc) return;
      const any = Object.values(this.marks).some((a) => a.length);
      if (any) store.set(this.key(), JSON.stringify({ v: 1, marks: this.marks })); else store.del(this.key());
    },
    page() { return book.pages[book.sel]; },
    list(i) { return this.marks[i] || []; },
    change(i, next) {
      this.hist.push({ i, prev: this.list(i).slice() });
      if (this.hist.length > 200) this.hist.shift();
      this.marks[i] = next;
      this.save();
      this.paint();
    },
    undo() {
      const p = this.page();
      let k = this.hist.length - 1;
      while (k >= 0 && (!p || this.hist[k].i !== p.i)) k--;
      if (k < 0) { msgRP('Nothing to undo on this page.'); return; }
      const h = this.hist.splice(k, 1)[0];
      this.marks[h.i] = h.prev;
      this.save();
      this.paint();
      msgRP('Undone.');
    },
    setOn(on) {
      const p = this.page();
      on = !!on && !!(p && p.view);
      this.on = on;
      $('repairToggle').setAttribute('aria-pressed', String(on));
      $('repairBar').hidden = !on;
      $('pages').classList.toggle('drawing', on);
      if (!on) this.drawing = null;
    },
    // the page's layer, drawn on (or redrawn after) show()
    attach(fig, p) {
      const v = p.view;
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('class', 'rp');
      svg.setAttribute('viewBox', `0 0 ${v.width} ${v.height}`);
      svg.setAttribute('preserveAspectRatio', 'none');
      svg.setAttribute('aria-hidden', 'true');
      fig.appendChild(svg);
      const at = (e) => {
        const r = svg.getBoundingClientRect();
        return [Math.round(((e.clientX - r.left) / r.width) * v.width * 10) / 10, Math.round(((e.clientY - r.top) / r.height) * v.height * 10) / 10];
      };
      const unit = () => v.width / Math.max(1, svg.getBoundingClientRect().width); // page px per screen px
      svg.addEventListener('pointerdown', (e) => {
        if (!this.on || e.button > 0) return;
        e.preventDefault();
        try { svg.setPointerCapture(e.pointerId); } catch (err) { /* synthetic pointer */ }
        const pt = at(e);
        this.drawing = { tool: this.tool, shift: e.shiftKey, pts: [pt, pt], id: e.pointerId };
        this.paint();
      });
      svg.addEventListener('pointermove', (e) => {
        const d = this.drawing;
        if (!d || d.id !== e.pointerId) return;
        e.preventDefault();
        const pt = at(e);
        if (d.tool === 'pen' && !(d.shift || e.shiftKey)) {
          const q = d.pts[d.pts.length - 1];
          if (d.pts.length === 2 && d.pts[0] === d.pts[1]) d.pts[1] = pt;
          else if (Math.hypot(pt[0] - q[0], pt[1] - q[1]) >= 2 * unit()) d.pts.push(pt);
        } else { d.pts = [d.pts[0], pt]; if (d.tool === 'pen') d.straight = true; }
        this.paint();
      });
      const end = (e, keep) => {
        const d = this.drawing;
        if (!d || d.id !== e.pointerId) return;
        this.drawing = null;
        const b = bboxOf(d.pts);
        if (!keep || Math.max(b[2] - b[0], b[3] - b[1]) < 4 * unit()) { this.paint(); return; }
        const tool = d.tool === 'pen' && (d.straight || d.shift) ? 'line' : d.tool;
        const m = { id: ++this.seq, tool, pts: tool === 'pen' ? d.pts : [d.pts[0], d.pts[d.pts.length - 1]], note: '', at: new Date().toISOString() };
        this.change(p.i, this.list(p.i).concat([m]));
        msgRP(`Mark ${this.list(p.i).length} added (${RP_TOOL[tool].toLowerCase()}). Add a note below if it helps.`);
      };
      svg.addEventListener('pointerup', (e) => end(e, true));
      svg.addEventListener('pointercancel', (e) => end(e, false));
      this.paint();
    },
    paint() {
      const p = this.page();
      const svg = $('pages').querySelector('svg.rp');
      if (svg && p && p.view) {
        const ss = p.view.ss;
        let s = this.list(p.i).map((m, k) => markSVG(m, ss, k + 1)).join('');
        if (this.drawing) s += markSVG({ tool: this.drawing.tool === 'pen' && this.drawing.straight ? 'line' : this.drawing.tool, pts: this.drawing.pts }, ss, 0);
        svg.innerHTML = s;
      }
      this.renderList();
    },
    renderList() {
      const p = this.page();
      const ms = p ? this.list(p.i) : [];
      const ol = $('rpList');
      // keep a note being typed: only rebuild when the marks themselves changed
      const sig = ms.map((m) => m.id).join(',') + '@' + (p ? p.i : '');
      if (ol.dataset.sig === sig) return;
      ol.dataset.sig = sig;
      ol.innerHTML = ms.map((m, k) => `<li data-id="${m.id}"><span class="rp-num" aria-hidden="true">${k + 1}</span><span>${esc(RP_TOOL[m.tool] || m.tool)}</span>` +
        `<input type="text" maxlength="160" value="${esc(m.note || '')}" placeholder="Note, e.g. missed chord note" aria-label="Note for mark ${k + 1}">` +
        `<button class="btn icon small" type="button" data-del="${m.id}" aria-label="Delete mark ${k + 1}">×</button></li>`).join('');
    },
  };
  const msgRP = (t) => { $('rpMsg').textContent = t; };
  function bboxOf(pts) {
    const xs = pts.map((q) => q[0]), ys = pts.map((q) => q[1]);
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  }
  // a mark's outline as path data (page frame)
  function markPathD(m) {
    const P = m.pts, r1 = (v) => Math.round(v * 10) / 10;
    if (m.tool === 'box' || m.tool === 'ellipse') {
      const [x0, y0, x1, y1] = bboxOf(P);
      if (m.tool === 'box') return `M${r1(x0)},${r1(y0)}H${r1(x1)}V${r1(y1)}H${r1(x0)}Z`;
      const rx = (x1 - x0) / 2, ry = (y1 - y0) / 2, cx = x0 + rx;
      return `M${r1(cx - rx)},${r1(y0 + ry)}a${r1(rx)},${r1(ry)} 0 1,0 ${r1(2 * rx)},0a${r1(rx)},${r1(ry)} 0 1,0 ${r1(-2 * rx)},0Z`;
    }
    const pts = m.tool === 'line' ? [P[0], P[P.length - 1]] : P;
    return 'M' + pts.map((q) => `${r1(q[0])},${r1(q[1])}`).join('L');
  }
  function markSVG(m, ss, n) {
    const d = markPathD(m), w = Math.max(3, ss * 0.22);
    let s = `<g class="rp-mark"><path class="rp-halo" d="${d}" stroke-width="${(w * 4).toFixed(1)}"/><path class="rp-core" d="${d}" stroke-width="${w.toFixed(1)}" stroke-dasharray="${(w * 3).toFixed(1)} ${(w * 2).toFixed(1)}"/>`;
    if (n) {
      const [x0, y0] = bboxOf(m.pts), r = ss * 0.75;
      s += `<g class="rp-badge"><circle cx="${(x0 - r * 0.6).toFixed(1)}" cy="${(y0 - r * 0.6).toFixed(1)}" r="${r.toFixed(1)}"/><text x="${(x0 - r * 0.6).toFixed(1)}" y="${(y0 - r * 0.6 + r * 0.42).toFixed(1)}" font-size="${(r * 1.2).toFixed(1)}">${n}</text></g>`;
    }
    return s + '</g>';
  }
  // What the reading found inside a mark's box, in the terms the repair pass needs.
  function repairInside(p, b) {
    const v = p.view;
    if (!v) return null;
    const sy = v.sym || {}, ss = v.ss;
    const hit = (x0, y0, x1, y1) => x0 <= b[2] && x1 >= b[0] && y0 <= b[3] && y1 >= b[1];
    const boxHit = (a) => hit(a[0], a[1], a[2], a[3]);
    const hp = (book.headParts && book.headParts.get(p.i)) || [], hn = (book.headNotes && book.headNotes.get(p.i)) || [], parts = book.parts || [];
    const heads = [];
    v.heads.forEach((h, k) => {
      if (!hit(h[0] - h[2], h[1] - h[2], h[0] + h[2], h[1] + h[2])) return;
      const n = hn[k];
      heads.push({ k, x: h[0], y: h[1], stem: h[3] === 1 ? 'up' : h[3] === -1 ? 'down' : h[3] === 2 ? 'both' : 'none',
        pitch: n ? pitchText(n) : null, value: n ? durText(n[3], n[4], n[5], n[6]) : null, quarters: n ? n[3] : null, parts: (hp[k] || []).map((pi) => (parts[pi] ? parts[pi].name : pi)) });
    });
    const pick = (a, f) => (a || []).filter(boxHit).map(f);
    const bx = (a) => a.slice(0, 4);
    let measures = null;
    const mm = lastRes && lastRes.score && lastRes.score.measureMap;
    if (mm && !v.spread) measures = [...new Set(mm.filter((m) => m.page === p.i && hit(m.xa, m.y0 - 2 * ss, m.xb, m.y1 + 2 * ss)).map((m) => m.n))].sort((x, y) => x - y);
    return {
      measures, heads,
      rests: pick(sy.rests, (r) => ({ box: bx(r), kind: r[4], quarters: r[5], dots: r[6], text: restText(r[4], r[5], r[6], r[7]) })),
      clefs: pick(sy.clefs, (c) => ({ box: bx(c), clef: c[4], text: clefLabel(c[4]), change: c[5] === 1, assumed: c[5] === 2 })),
      keys: pick(sy.keys, (c) => ({ box: bx(c), fifths: c[4], text: keyLabel(c[4]), change: !!c[5] })),
      times: pick(sy.times, (c) => ({ box: bx(c), beats: c[4] || null, beatType: c[5] || null, symbol: c[6] || null })),
      accidentals: pick(sy.accs, (c) => ({ box: bx(c), kind: c[4] })),
      dots: (sy.dots || []).filter(([x, y, r]) => hit(x - r, y - r, x + r, y + r)).map(([x, y]) => ({ x, y })),
      tuplets: pick(sy.tuplets, (c) => ({ box: bx(c), actual: c[4], normal: c[5] })),
      barlines: (sy.bars || []).filter((r) => hit(r[4], r[1], r[5], r[2])).map((r) => ({ x: r[0], top: r[1], bottom: r[2], type: r[3] })),
      text: pick(sy.text, (t) => ({ box: bx(t), role: t[4], label: t[5] })),
      dynamics: pick((sy.dyns || []).concat(sy.wedges || []), (d) => ({ box: bx(d), value: d[4] })),
      unrecognised: (sy.unknown || []).filter(boxHit),
    };
  }
  function repairNotes() {
    const pages = [];
    book.pages.forEach((p) => {
      const ms = repair.list(p.i);
      if (!ms.length) return;
      const v = p.view;
      pages.push({
        page: p.i + 1, width: v ? v.width : null, height: v ? v.height : null, staffSpace: v ? v.ss : null, spread: v ? v.spread || 0 : 0,
        marks: ms.map((m, k) => { const b = bboxOf(m.pts).map((x) => Math.round(x)); return { n: k + 1, id: m.id, tool: m.tool, note: m.note || '', points: m.pts, bbox: b, drawn: m.at, found: repairInside(p, b) }; }),
      });
    });
    const sc = (lastRes && lastRes.score) || {};
    return {
      format: 'score-scan-reader/repair-notes', version: 1, file: repair.file, size: repair.size, exported: new Date().toISOString(),
      frame: 'page pixels of the straightened page as read (the detection overlay frame); x right, y down',
      score: { parts: (sc.parts || []).map((p) => p.name), measures: sc.measures || 0, fifths: sc.fifths, time: sc.time || null },
      pages,
    };
  }
  const notesName = (ext) => `${String(repair.file || 'score').replace(/\.[^.]+$/, '')}-repair${ext}`;
  // The page may not offer download links (tools/build.js, artifact rules), so
  // a file opens in a new tab, where the browser saves it; where new tabs are
  // blocked the copy button still works.
  function openBlob(blob, what) {
    const url = URL.createObjectURL(blob);
    let w = null;
    try { w = window.open(url, '_blank'); if (w) w.opener = null; } catch (e) { w = null; }
    setTimeout(() => URL.revokeObjectURL(url), 120000);
    msgRP(w ? `${what} opened in a new tab: save it from there.` : `${what} could not open here (new tabs are blocked); use Copy repair notes.`);
  }
  function countMarks() { return Object.values(repair.marks).reduce((a, m) => a + m.length, 0); }
  function copyRepair() {
    const n = countMarks();
    if (!n) { msgRP('There are no repair marks to copy yet.'); return; }
    const txt = JSON.stringify(repairNotes(), null, 1);
    const ok = () => { $('rpOut').hidden = true; msgRP(`Copied ${plural(n, 'repair mark')} as JSON.`); };
    const fallback = () => { const ta = $('rpOut'); ta.value = txt; ta.hidden = false; ta.focus(); ta.select(); msgRP('This page cannot reach the clipboard. The notes are selected below: press Ctrl+C (Cmd+C on a Mac).'); };
    try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(ok, fallback); else fallback(); } catch (e) { fallback(); }
  }
  function downloadRepairJSON() {
    if (!countMarks()) { msgRP('There are no repair marks to download yet.'); return; }
    openBlob(new Blob([JSON.stringify(repairNotes(), null, 1)], { type: 'application/json' }), `Repair notes (${notesName('.json')})`);
  }
  function downloadRepairPNG() {
    const p = repair.page();
    if (!p || !p.view || !p.url) return;
    const v = p.view, img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = img.naturalWidth; c.height = img.naturalHeight;
      const g = c.getContext('2d');
      g.drawImage(img, 0, 0);
      const k = c.width / v.width, ss = v.ss, w = Math.max(3, ss * 0.22);
      g.scale(k, k);
      const css = getComputedStyle(document.documentElement);
      const halo = css.getPropertyValue('--rp-halo').trim() || 'rgba(118,255,3,.55)', ink = css.getPropertyValue('--rp-ink').trim() || '#0b0c0e';
      const badge = css.getPropertyValue('--rp-badge-ink').trim() || '#b2ff59';
      g.lineCap = 'round'; g.lineJoin = 'round';
      repair.list(p.i).forEach((m, n) => {
        const path = new Path2D(markPathD(m));
        g.setLineDash([]); g.strokeStyle = halo; g.lineWidth = w * 4; g.stroke(path);
        g.setLineDash([w * 3, w * 2]); g.strokeStyle = ink; g.lineWidth = w; g.stroke(path);
        const [x0, y0] = bboxOf(m.pts), r = ss * 0.75, cx = x0 - r * 0.6, cy = y0 - r * 0.6;
        g.setLineDash([]); g.fillStyle = ink; g.beginPath(); g.arc(cx, cy, r, 0, 2 * Math.PI); g.fill();
        g.fillStyle = badge; g.font = `700 ${r * 1.2}px sans-serif`; g.textAlign = 'center'; g.fillText(String(n + 1), cx, cy + r * 0.42);
      });
      c.toBlob((b) => { if (b) openBlob(b, `Page ${p.i + 1} with its marks`); c.width = c.height = 0; }, 'image/png');
    };
    img.src = p.url;
  }
  $('repairToggle').addEventListener('click', () => repair.setOn(!repair.on));
  document.querySelectorAll('input[name="rpTool"]').forEach((r) => r.addEventListener('change', () => { if (r.checked) repair.tool = r.value; }));
  $('rpUndo').addEventListener('click', () => repair.undo());
  $('rpClear').addEventListener('click', () => {
    const p = repair.page();
    if (!p || !repair.list(p.i).length) { msgRP('This page has no marks.'); return; }
    repair.change(p.i, []);
    msgRP(`Cleared page ${p.i + 1}. Undo brings the marks back.`);
  });
  $('rpCopy').addEventListener('click', copyRepair);
  $('rpJson').addEventListener('click', downloadRepairJSON);
  $('rpPng').addEventListener('click', downloadRepairPNG);
  $('rpList').addEventListener('input', (e) => {
    const li = e.target.closest('li[data-id]'), p = repair.page();
    if (!li || !p) return;
    const m = repair.list(p.i).find((x) => String(x.id) === li.dataset.id);
    if (m) { m.note = e.target.value; repair.save(); }
  });
  $('rpList').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-del]'), p = repair.page();
    if (!b || !p) return;
    repair.change(p.i, repair.list(p.i).filter((x) => String(x.id) !== b.dataset.del));
    msgRP('Mark deleted. Undo brings it back.');
  });
  document.addEventListener('keydown', (e) => {
    if (!repair.on) return;
    if (e.key === 'Escape') { repair.drawing = null; repair.setOn(false); $('repairToggle').focus(); msgRP(''); return; }
    const typing = /^(INPUT|TEXTAREA)$/.test(e.target.tagName) && e.target.type !== 'radio';
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === 'z' || e.key === 'Z') && !typing) { e.preventDefault(); repair.undo(); }
  });

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
  loadSample('rag');
})();
