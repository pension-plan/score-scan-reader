/* global pdfjsLib, Tesseract, opensheetmusicdisplay, omrRequire */
(function () {
  'use strict';
  const { convert } = omrRequire('./omr');
  const $ = (id) => document.getElementById(id);
  const status = (t) => { $('status').textContent = t; };
  const MAX_PAGES = 8;
  let busy = false;
  let lastXML = '';

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

  // -------------------------------------------------------------- input ---
  function canvasToGray(c) {
    const ctx = c.getContext('2d');
    const d = ctx.getImageData(0, 0, c.width, c.height).data;
    const g = new Uint8ClampedArray(c.width * c.height);
    for (let i = 0, j = 0; i < g.length; i++, j += 4) g[i] = (d[j] * 299 + d[j + 1] * 587 + d[j + 2] * 114) / 1000;
    return { width: c.width, height: c.height, data: g };
  }
  async function pdfToGray(buf) {
    const pdf = await pdfjsLib.getDocument({ data: buf, isEvalSupported: false }).promise;
    const out = [];
    const n = Math.min(pdf.numPages, MAX_PAGES);
    for (let i = 1; i <= n; i++) {
      status(`Rendering page ${i}/${n}`);
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
  function drawOverlay(res) {
    const host = $('pages');
    host.textContent = '';
    const parts = res.score.parts || [];
    $('legend').innerHTML = '';
    parts.forEach(p => {
      const s = document.createElement('span');
      s.innerHTML = `<i style="background:${p.color}"></i>`;
      s.appendChild(document.createTextNode(p.name));
      $('legend').appendChild(s);
    });
    for (const pg of res.pages) {
      const fr = pg.fr;
      const c = grayToCanvas(fr.gray);
      const ctx = c.getContext('2d');
      const lw = Math.max(1.5, fr.ss / 8);
      ctx.lineWidth = lw;
      ctx.strokeStyle = 'rgba(30,140,90,.55)';
      for (const st of fr.staves) {
        for (let k = 0; k < 5; k += 4) {
          ctx.beginPath();
          for (let x = st.left; x <= st.right; x += 20) ctx.lineTo(x, st.yAt(k, x));
          ctx.stroke();
        }
      }
      ctx.strokeStyle = 'rgba(60,90,200,.6)';
      for (const b of fr.barlines) { ctx.beginPath(); ctx.moveTo(b.x, b.top); ctx.lineTo(b.x, b.bot); ctx.stroke(); }
      ctx.lineWidth = Math.max(2, fr.ss / 7);
      for (const h of fr.heads) {
        const idx = h.parts || [];
        const r = h.sp * 0.62;
        if (!idx.length) {
          ctx.strokeStyle = '#888';
          ctx.beginPath(); ctx.arc(h.x, h.y, r, 0, Math.PI * 2); ctx.stroke();
          continue;
        }
        idx.forEach((pi, k) => {
          ctx.strokeStyle = parts[pi] ? parts[pi].color : '#888';
          const a0 = (k / idx.length) * Math.PI * 2, a1 = ((k + 1) / idx.length) * Math.PI * 2;
          ctx.beginPath(); ctx.arc(h.x, h.y, r, a0, a1); ctx.stroke();
        });
      }
      c.setAttribute('aria-label', `Page ${pg.index + 1} with detected staves and noteheads`);
      host.appendChild(c);
    }
    if (!res.pages.length) host.innerHTML = '<p class="muted">Nothing detected.</p>';
  }

  function renderSummary(res) {
    const sc = res.score;
    const pe = $('parts');
    if (!sc.parts || !sc.parts.length) { pe.textContent = 'No parts.'; }
    else {
      const tbl = document.createElement('table');
      tbl.innerHTML = '<tr><th>Part</th><th>Clef</th><th class="num">Notes</th><th class="num">Range</th></tr>';
      sc.parts.forEach((p, i) => {
        const tr = document.createElement('tr');
        const clef = (sc.clefs || [])[p.src[0].staff] === 'F' ? 'Bass' : 'Treble';
        tr.innerHTML = `<td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color};margin-right:6px"></span></td><td>${clef}</td><td class="num">${sc.nNotes[i]}</td><td class="num">${(sc.ranges && sc.ranges[i]) || '-'}</td>`;
        tr.firstChild.appendChild(document.createTextNode(p.name));
        tbl.appendChild(tr);
      });
      pe.textContent = '';
      pe.classList.remove('muted');
      const meta = document.createElement('p');
      meta.className = 'muted';
      const ks = sc.fifths > 0 ? `${sc.fifths} sharp${sc.fifths > 1 ? 's' : ''}` : sc.fifths < 0 ? `${-sc.fifths} flat${sc.fifths < -1 ? 's' : ''}` : 'no sharps or flats';
      meta.textContent = `${sc.measures} measures, key signature ${ks}, time ${sc.time.beats}/${sc.time.type}.`;
      pe.appendChild(meta);
      pe.appendChild(tbl);
    }
    const le = $('lyrics');
    le.textContent = '';
    const keys = Object.keys(res.lyricsBySystem);
    if (!keys.length) le.textContent = res.ocrError ? 'Lyrics OCR unavailable: ' + res.ocrError : 'No lyric lines found.';
    for (const k of keys) {
      for (const v of res.lyricsBySystem[k]) {
        const d = document.createElement('div');
        const b = document.createElement('b');
        b.textContent = `Sys ${+k.split(':')[1] + 1} v${v.number}`;
        d.appendChild(b);
        d.appendChild(document.createTextNode(v.syllables.map(s => s.text + (s.syllabic === 'begin' || s.syllabic === 'middle' ? ' -' : '')).join(' ')));
        le.appendChild(d);
      }
    }
    if (keys.length) le.classList.remove('muted');
    const we = $('warnings');
    we.textContent = '';
    for (const w of res.warnings) {
      const li = document.createElement('li');
      if (/^(Closed score|Grand staff|Staff \d|Time signature inferred)/.test(w)) li.className = 'info';
      li.textContent = w;
      we.appendChild(li);
    }
    lastXML = sc.xml || '';
    $('xml').value = lastXML;
  }

  let osmd = null;
  async function renderNotation(xml) {
    const host = $('osmd');
    $('osmdNote').textContent = '';
    if (!xml || typeof opensheetmusicdisplay === 'undefined') { $('osmdNote').textContent = 'Notation preview unavailable.'; return; }
    try {
      host.textContent = '';
      osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(host, { autoResize: true, drawTitle: false, backend: 'svg', drawPartNames: true });
      await osmd.load(xml);
      osmd.render();
    } catch (e) {
      $('osmdNote').textContent = 'Preview could not render this MusicXML: ' + e.message;
    }
  }

  // ---------------------------------------------------------------- run ---
  async function run(getPages, label) {
    if (busy) return;
    busy = true;
    $('sample').disabled = true;
    const t0 = performance.now();
    try {
      status(`Reading ${label}`);
      const ocrP = getOCR();
      const { pages, total } = await getPages();
      let ocr = null, ocrError = null;
      try {
        status('Loading text recogniser');
        const w = await withTimeout(ocrP, 45000);
        ocr = async (img) => {
          const { data } = await w.recognize(grayToCanvas(img), {}, { text: true, blocks: true });
          const words = [];
          for (const b of data.blocks || []) for (const p of b.paragraphs) for (const l of p.lines) for (const wd of l.words)
            words.push({ text: wd.text, conf: wd.confidence, x0: wd.bbox.x0, x1: wd.bbox.x1 });
          return words;
        };
      } catch (e) { ocrError = e.message || String(e); }
      const res = await convert(pages, { ocr, onProgress: status });
      res.ocrError = ocrError;
      if (ocrError) res.warnings.unshift('Lyrics OCR unavailable (' + ocrError + '); notes only.');
      if (total > pages.length) res.warnings.unshift(`Only the first ${pages.length} of ${total} pages were processed.`);
      drawOverlay(res);
      renderSummary(res);
      status(`Done in ${((performance.now() - t0) / 1000).toFixed(1)} s: ${label}`);
      await renderNotation(res.score.xml);
      window.__omrResult = { parts: res.score.parts.map(p => p.name), nNotes: res.score.nNotes, measures: res.score.measures, lyrics: Object.values(res.lyricsBySystem).flat().length, warnings: res.warnings, xmlLength: (res.score.xml || '').length };
    } catch (e) {
      status('Could not convert: ' + (e.message || e));
      $('warnings').innerHTML = '';
      const li = document.createElement('li'); li.textContent = 'Conversion failed: ' + (e.message || e); $('warnings').appendChild(li);
      window.__omrResult = { error: String(e && e.message || e) };
    } finally {
      busy = false;
      $('sample').disabled = false;
    }
  }

  function handleFile(file) {
    if (!file) return;
    const isPDF = file.type === 'application/pdf' || /\.pdf$/i.test(file.name);
    if (isPDF) run(async () => pdfToGray(new Uint8Array(await file.arrayBuffer())), file.name);
    else if (/^image\//.test(file.type) || /\.(png|jpe?g)$/i.test(file.name)) run(() => imageToGray(file), file.name);
    else status('Unsupported file type: please use PDF, PNG or JPG.');
  }

  function loadSample() {
    run(async () => {
      const r = await fetch('assets/sample-st-anselm.pdf');
      if (!r.ok) throw new Error('sample not found (' + r.status + ')');
      return pdfToGray(new Uint8Array(await r.arrayBuffer()));
    }, 'sample: St. Anselm (J. Barnby), Methodist Hymnal 1905');
  }

  $('file').addEventListener('change', (e) => { handleFile(e.target.files[0]); e.target.value = ''; });
  const drop = $('drop');
  ['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', (e) => handleFile(e.dataTransfer.files[0]));
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', (e) => { e.preventDefault(); if (!drop.contains(e.target)) handleFile(e.dataTransfer.files[0]); });
  $('sample').addEventListener('click', loadSample);
  $('copy').addEventListener('click', () => {
    const ta = $('xml');
    const done = () => { $('copied').textContent = 'Copied'; setTimeout(() => { $('copied').textContent = ''; }, 2000); };
    try {
      navigator.clipboard.writeText(ta.value).then(done, () => { ta.focus(); ta.select(); $('copied').textContent = 'Press Ctrl/Cmd+C'; });
    } catch (e) { ta.focus(); ta.select(); $('copied').textContent = 'Press Ctrl/Cmd+C'; }
  });

  if (typeof pdfjsLib === 'undefined') status('PDF library failed to load; images still work.');
  loadSample();
})();
