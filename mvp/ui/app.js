/* global pdfjsLib, Tesseract, opensheetmusicdisplay, omrRequire */
(function () {
  'use strict';
  const { convert } = omrRequire('./omr');
  const $ = (id) => document.getElementById(id);
  const MAX_PAGES = 8;
  const MAX_CODE_LINES = 3000;
  const SAMPLE = { url: 'assets/sample-st-anselm.pdf', name: 'sample-st-anselm.pdf', label: 'St. Anselm (J. Barnby), Methodist Hymnal 1905' };
  let busy = false;
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
  // events: page rendering here, then convert()'s onProgress messages (or a
  // structured {stage} second argument when the pipeline provides one).
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
    progress() {
      // share of the seven stages that are done, for the file row meter
      const done = this.state.filter((s) => s === 'complete' || s === 'skipped').length;
      return Math.min(1, (done + (this.cur >= 0 ? 0.5 : 0)) / STEPS.length);
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
      const meter = $('fileMeter');
      if (meter) {
        const pct = Math.round(this.progress() * 100);
        meter.setAttribute('aria-valuenow', String(pct));
        $('fileMeterBar').style.width = pct + '%';
      }
    },
    snapshot() { return STEPS.map((s, i) => ({ id: s.id, state: this.state[i], detail: this.detail[i] })); },
  };

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
  function detailOf(msg) {
    const m = String(msg || '');
    let r = m.match(/\((\d+)\/(\d+) lines?\)/);
    if (r) return `line ${r[1]} of ${r[2]}`;
    r = m.match(/page (\d+)\s*(?:\/|of)\s*(\d+)/i);
    if (r) return `page ${r[1]} of ${r[2]}`;
    r = m.match(/page (\d+)/i);
    if (r) return `page ${r[1]}`;
    return null;
  }
  function onPipelineProgress(msg, info) {
    status(msg);
    const id = stageOf(msg, info);
    if (id) stepper.go(id, detailOf(msg));
  }

  // Facts for each completed stage, read from the result.
  function stepFacts(res, nPages, ocrUsed) {
    const pages = res.pages || [];
    const sum = (f) => pages.reduce((a, p) => a + (f(p) || 0), 0);
    const skews = pages.map((p) => Math.abs((p.fr && p.fr.skew && p.fr.skew.angle) || 0));
    const maxSkew = skews.length ? Math.max(...skews) : 0;
    stepper.set('render', null, plural(nPages, 'page'));
    stepper.set('cleanup', null, maxSkew >= 0.05 ? `deskewed ${maxSkew.toFixed(1)}°` : 'no skew');
    const nStaves = sum((p) => p.fr && p.fr.staves && p.fr.staves.length);
    const nSys = sum((p) => (p.asm && p.asm.systems && p.asm.systems.length) || (p.fr && p.fr.systems && p.fr.systems.length));
    stepper.set('staves', null, `${plural(nStaves, 'staff', 'staves')} · ${plural(nSys, 'system')}`);
    stepper.set('notes', null, plural(sum((p) => p.fr && p.fr.heads && p.fr.heads.length), 'head'));
    const verses = Object.values(res.lyricsBySystem || {}).flat();
    const syl = verses.reduce((a, v) => a + ((v.syllables && v.syllables.length) || 0), 0);
    if (!ocrUsed) stepper.set('lyrics', 'skipped', 'text reader off');
    else stepper.set('lyrics', null, verses.length ? `${plural(verses.length, 'line')} · ${syl} syl.` : 'no lyric lines');
    const sc = res.score || {};
    stepper.set('parts', null, `${plural((sc.parts || []).length, 'part')} · ${plural(sc.measures || 0, 'bar')}`);
    const nLines = (sc.xml || '').split('\n').length;
    stepper.set('xml', null, plural(nLines, 'line'));
  }

  // ----------------------------------------------------------- dropzone ---
  const drop = {
    state: 'idle', name: '', prose: false,
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
        error: `Could not convert ${n}`,
      };
      const hints = {
        idle: `PDF, PNG or JPG. The first ${MAX_PAGES} pages are read.`,
        over: 'Release to convert. The file stays in this browser.',
        busy: 'Reading the scan. This takes a few seconds per page.',
        done: 'Drop another scan here, or choose a file.',
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
    delete $('fileRow').dataset.done;
  }
  function fileFinished(ok) {
    $('fileDone').toggleAttribute('hidden', !ok);
    if (ok) $('fileRow').dataset.done = '';
    $('fileMeter').setAttribute('aria-valuenow', ok ? '100' : $('fileMeter').getAttribute('aria-valuenow'));
    if (ok) $('fileMeterBar').style.width = '100%';
  }

  // -------------------------------------------------------------- input ---
  function canvasToGray(c) {
    const ctx = c.getContext('2d');
    const d = ctx.getImageData(0, 0, c.width, c.height).data;
    const g = new Uint8ClampedArray(c.width * c.height);
    for (let i = 0, j = 0; i < g.length; i++, j += 4) g[i] = (d[j] * 299 + d[j + 1] * 587 + d[j + 2] * 114) / 1000;
    return { width: c.width, height: c.height, data: g };
  }
  async function pdfToGray(buf) {
    if (typeof pdfjsLib === 'undefined') throw new Error('the PDF reader did not load; try a PNG or JPG instead');
    const pdf = await pdfjsLib.getDocument({ data: buf, isEvalSupported: false }).promise;
    const out = [];
    const n = Math.min(pdf.numPages, MAX_PAGES);
    for (let i = 1; i <= n; i++) {
      status(`Rendering page ${i} of ${n}`);
      stepper.go('render', `page ${i} of ${n}`);
      await nextPaint();
      const page = await pdf.getPage(i);
      const v1 = page.getViewport({ scale: 1 });
      const scale = Math.max(1.5, Math.min(5, 2300 / v1.width));
      const vp = page.getViewport({ scale });
      const c = document.createElement('canvas');
      c.width = Math.round(vp.width); c.height = Math.round(vp.height);
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
      await page.render({ canvasContext: ctx, viewport: vp }).promise;
      out.push(canvasToGray(c));
    }
    return { pages: out, total: pdf.numPages };
  }
  async function imageToGray(file) {
    stepper.go('render', 'page 1 of 1');
    const bmp = await createImageBitmap(file);
    const s = bmp.width > 3200 ? 3200 / bmp.width : 1;
    const c = document.createElement('canvas');
    c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(bmp, 0, 0, c.width, c.height);
    return { pages: [canvasToGray(c)], total: 1 };
  }

  // ------------------------------------------------------------- render ---
  // Each part gets a colour and a marker shape, so the overlay does not rely
  // on colour alone. Shapes are drawn the same way on the canvas and in SVG.
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
  function traceShape(ctx, shape, x, y, r) {
    ctx.beginPath();
    const p = shapePoints(shape, r);
    if (!p) { ctx.arc(x, y, r, 0, Math.PI * 2); return; }
    p.forEach(([dx, dy], i) => (i ? ctx.lineTo(x + dx, y + dy) : ctx.moveTo(x + dx, y + dy)));
    ctx.closePath();
  }
  function shapeSVG(shape, color, cls) {
    const p = shapePoints(shape, 5.2);
    const body = p ? `<polygon points="${p.map(([x, y]) => `${(7 + x).toFixed(2)},${(7 + y).toFixed(2)}`).join(' ')}"` : '<circle cx="7" cy="7" r="5.2"';
    return `<svg class="${cls || 'mark'}" viewBox="0 0 14 14" aria-hidden="true">${body} fill="${esc(color)}" stroke="${esc(color)}" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
  }
  const partShape = (i) => SHAPES[i % SHAPES.length];
  const OV = { staff: 'rgba(30,140,90,.6)', bar: 'rgba(43,55,176,.7)', none: '#8a8f96' };

  function drawOverlay(res) {
    const host = $('pages');
    host.textContent = '';
    const parts = res.score.parts || [];
    const legend = $('legend');
    legend.innerHTML = parts.map((p, i) => `<li>${shapeSVG(partShape(i), p.color)}<span>${esc(p.name)}</span></li>`).join('') +
      '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><path d="M1 4h12M1 10h12" stroke="' + OV.staff + '" stroke-width="2"/></svg><span>Staff edges</span></li>' +
      '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v12" stroke="' + OV.bar + '" stroke-width="2.4"/></svg><span>Barline</span></li>' +
      '<li class="aux"><svg class="mark" viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="' + OV.none + '" stroke-width="1.6" stroke-dasharray="2 2"/></svg><span>Head in no part</span></li>';
    const multi = res.pages.length > 1;
    for (const pg of res.pages) {
      const fr = pg.fr;
      if (multi) {
        const lab = document.createElement('p');
        lab.className = 'pagelabel';
        lab.textContent = `Page ${pg.index + 1}`;
        host.appendChild(lab);
      }
      const frame = document.createElement('div');
      frame.className = 'pageframe';
      const base = grayToCanvas(fr.gray);
      base.setAttribute('role', 'img');
      base.setAttribute('aria-label', `Page ${pg.index + 1} of the scan, straightened`);
      const ov = document.createElement('canvas');
      ov.className = 'ov';
      ov.width = base.width; ov.height = base.height;
      ov.setAttribute('aria-hidden', 'true');
      const ctx = ov.getContext('2d');
      const lw = Math.max(1.5, fr.ss / 8);
      ctx.lineWidth = lw;
      ctx.strokeStyle = OV.staff;
      for (const st of fr.staves) {
        for (let k = 0; k < 5; k += 4) {
          ctx.beginPath();
          for (let x = st.left; x <= st.right; x += 20) ctx.lineTo(x, st.yAt(k, x));
          ctx.stroke();
        }
      }
      ctx.strokeStyle = OV.bar;
      for (const b of fr.barlines) { ctx.beginPath(); ctx.moveTo(b.x, b.top); ctx.lineTo(b.x, b.bot); ctx.stroke(); }
      ctx.lineWidth = Math.max(2, fr.ss / 7);
      for (const h of fr.heads) {
        const idx = h.parts || [];
        const r = (h.sp || fr.ss) * 0.62;
        if (!idx.length) {
          ctx.strokeStyle = OV.none;
          ctx.setLineDash([3, 3]);
          traceShape(ctx, 'circle', h.x, h.y, r); ctx.stroke();
          ctx.setLineDash([]);
          continue;
        }
        // a head shared by several parts (unison) gets one ring per part
        idx.forEach((pi, k) => {
          ctx.strokeStyle = parts[pi] ? parts[pi].color : OV.none;
          traceShape(ctx, partShape(pi), h.x, h.y, r * (1 + 0.38 * k));
          ctx.stroke();
        });
      }
      frame.appendChild(base);
      frame.appendChild(ov);
      host.appendChild(frame);
    }
    if (!res.pages.length) host.innerHTML = '<p class="muted">No staves were found, so there is nothing to mark up.</p>';
    applyOverlay();
  }
  function applyOverlay() {
    const on = $('overlayToggle').getAttribute('aria-pressed') === 'true';
    $('pages').classList.toggle('ov-off', !on);
  }

  const CLEF = { G: 'treble', F: 'bass', C: 'C clef' };
  const clefName = (c) => CLEF[c] || (c ? c + ' clef' : 'clef unknown');
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

  let osmd = null;
  async function renderNotation(xml) {
    const host = $('osmd');
    $('osmdNote').textContent = '';
    if (!xml || typeof opensheetmusicdisplay === 'undefined') { $('osmdNote').textContent = 'The notation preview is unavailable because its library did not load.'; return; }
    try {
      host.textContent = '';
      osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(host, { autoResize: true, drawTitle: false, backend: 'svg', drawPartNames: true });
      await osmd.load(xml);
      osmd.render();
    } catch (e) {
      $('osmdNote').textContent = 'The preview could not draw this MusicXML: ' + e.message;
    }
  }

  // ---------------------------------------------------------------- run ---
  function setBusy(b) {
    busy = b;
    $('sample').disabled = b;
    $('choose').disabled = b;
  }
  async function run(getPages, file) {
    if (busy) { status('Wait for the current conversion to finish.'); return; }
    setBusy(true);
    const t0 = performance.now();
    $('alert').hidden = true;
    stepper.reset();
    drop.set('busy', file.title || file.name, !!file.title);
    showFile(file.name, file.size);
    let ocrUsed = false;
    try {
      status(`Reading ${file.label || file.name}`);
      const ocrP = getOCR();
      const { pages, total, size } = await getPages();
      if (size != null) $('fileSize').textContent = fmtBytes(size);
      $('fileSize').textContent += ($('fileSize').textContent ? ' · ' : '') + (total > pages.length ? `${pages.length} of ${total} pages` : plural(total, 'page'));
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
      // convert() starts with page 1's image analysis, which runs without a
      // break; paint that stage first so the stepper does not skip it.
      stepper.go('cleanup', pages.length > 1 ? `page 1 of ${pages.length}` : null);
      status(`Page 1 of ${pages.length}: cleaning up and finding staves and notes`);
      await nextPaint();
      const res = await convert(pages, { ocr, onProgress: onPipelineProgress });
      res.ocrError = ocrError;
      if (ocrError) res.warnings.unshift('Lyrics were not read: the text reader is unavailable (' + ocrError + ').');
      if (total > pages.length) res.warnings.unshift(`Only the first ${pages.length} of ${total} pages were read.`);
      stepper.go('xml');
      status('Writing MusicXML and drawing the preview');
      lastRes = res;
      drawOverlay(res);
      renderParts(res);
      renderLyrics(res);
      renderWarnings(res.warnings || []);
      renderCode(res.score.xml);
      stepFacts(res, pages.length, ocrUsed);
      await nextPaint();
      await renderNotation(res.score.xml);
      stepper.finish();
      fileFinished(true);
      drop.set('done');
      status(`Done in ${((performance.now() - t0) / 1000).toFixed(1)} s: ${file.label || file.name}`);
      window.__omrResult = {
        parts: res.score.parts.map((p) => p.name), nNotes: res.score.nNotes, measures: res.score.measures,
        lyrics: Object.values(res.lyricsBySystem).flat().length, warnings: res.warnings, xmlLength: (res.score.xml || '').length,
        steps: stepper.snapshot(),
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
      setBusy(false);
    }
  }

  function handleFile(file) {
    if (!file) return;
    const isPDF = file.type === 'application/pdf' || /\.pdf$/i.test(file.name);
    const isImg = /^image\/(png|jpe?g)$/.test(file.type) || /\.(png|jpe?g)$/i.test(file.name);
    if (!isPDF && !isImg) {
      drop.set('error', file.name, false);
      status(`${file.name} is not a PDF, PNG or JPG file.`);
      return;
    }
    const f = { name: file.name, size: file.size };
    if (isPDF) run(async () => pdfToGray(new Uint8Array(await file.arrayBuffer())), f);
    else run(() => imageToGray(file), f);
  }

  function loadSample() {
    run(async () => {
      const r = await fetch(SAMPLE.url);
      if (!r.ok) throw new Error('the sample file was not found (' + r.status + ')');
      const buf = new Uint8Array(await r.arrayBuffer());
      const size = buf.length; // read before pdf.js transfers (detaches) the buffer
      const out = await pdfToGray(buf);
      out.size = size;
      return out;
    }, { name: SAMPLE.name, title: 'the sample hymn', label: 'sample: ' + SAMPLE.label, size: null });
  }

  // ---------------------------------------------------------------- wire ---
  stepper.build();
  $('choose').addEventListener('click', () => $('file').click());
  $('file').addEventListener('change', (e) => { const f = e.target.files[0]; e.target.value = ''; handleFile(f); });
  $('sample').addEventListener('click', loadSample);
  $('copy').addEventListener('click', copyXML);
  $('copy').disabled = true;
  const ovSaved = store.get('ssr.overlay');
  if (ovSaved === 'off') $('overlayToggle').setAttribute('aria-pressed', 'false');
  $('overlayToggle').addEventListener('click', () => {
    const on = $('overlayToggle').getAttribute('aria-pressed') !== 'true';
    $('overlayToggle').setAttribute('aria-pressed', String(on));
    store.set('ssr.overlay', on ? 'on' : 'off');
    applyOverlay();
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
    const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) handleFile(f);
  });
  window.__dropDepth = () => depth;

  drop.set('idle');
  renderWarnings([]);
  if (typeof pdfjsLib === 'undefined') status('The PDF reader did not load; PNG and JPG files still work.');
  loadSample();
})();
