// Page logic: load a scan (sample, upload or drop), rasterise it, send it to the inference worker,
// draw the detections as an SVG overlay and summarise them.
const PDFJS_WORKER = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
const MAX_SIDE = 2600; // px; long side of a rendered PDF page (about 240 dpi on letter paper)

const $ = (id) => document.getElementById(id);
const SVGNS = 'http://www.w3.org/2000/svg';

// Families in legend order. Noteheads are split by voice slot.
const FAMILIES = [
  { key: 'v1', label: 'Noteheads, voice 1 (stems up)', on: true },
  { key: 'v2', label: 'Noteheads, voice 2 (stems down)', on: true },
  { key: 'vx', label: 'Noteheads, other voice slot', on: true },
  { key: 'rest', label: 'Rests', on: true },
  { key: 'accid', label: 'Accidentals', on: true },
  { key: 'clef', label: 'Clefs', on: true },
  { key: 'sig', label: 'Key and time signatures', on: true },
  { key: 'bar', label: 'Barlines', on: true },
  { key: 'stem', label: 'Beams, flags, dots', on: false },
  { key: 'other', label: 'Slurs, ties, dynamics, other', on: false },
  { key: 'measure', label: 'Measure boxes', on: false },
];
const famOf = (d) => {
  const c = d.cls;
  if (c.startsWith('note_')) {
    const v = d.attrs && d.attrs.voice_slot;
    return v === '1' ? 'v1' : v === '2' ? 'v2' : 'vx';
  }
  if (c.startsWith('rest_') || c.startsWith('mRest') || c.startsWith('multiRest')) return 'rest';
  if (c.startsWith('accid_')) return 'accid';
  if (c.startsWith('clef_')) return 'clef';
  if (c.startsWith('keySig_') || c.startsWith('meterSig_')) return 'sig';
  if (c.startsWith('barLine_')) return 'bar';
  if (c === 'measure') return 'measure';
  if (c === 'beam' || c === 'flag' || c.startsWith('dots_')) return 'stem';
  return 'other';
};
const CLEF_NAME = (c) => (c.startsWith('clef_G') ? 'treble' : c.startsWith('clef_F') ? 'bass' : c.startsWith('clef_C') ? 'C clef' : 'clef');

const state = { run: 0, dets: [], hidden: new Set(FAMILIES.filter((f) => !f.on).map((f) => f.key)), pdf: null, srcName: '' };
window.__demo = state;

// ---------- worker ----------
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
const pending = new Map();
worker.onmessage = (e) => {
  const { id, progress, result, error } = e.data;
  const p = pending.get(id);
  if (!p) return;
  if (progress) return p.progress(progress);
  pending.delete(id);
  error ? p.reject(new Error(error)) : p.resolve(result);
};
worker.onerror = (e) => {
  for (const p of pending.values()) p.reject(new Error('The inference worker failed to start: ' + (e.message || 'unknown error')));
  pending.clear();
};
function infer(img, onProgress) {
  const id = ++state.run;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject, progress: onProgress });
    worker.postMessage({ id, img }, [img.data.buffer]);
  });
}

// ---------- status ----------
function setStatus(text, kind = 'busy') {
  $('status').textContent = text;
  $('status').dataset.kind = kind;
  document.body.dataset.state = kind;
}

// ---------- input ----------
async function rasterFromImage(blob) {
  const bmp = await createImageBitmap(blob);
  const c = $('canvas');
  c.width = bmp.width; c.height = bmp.height;
  c.getContext('2d').drawImage(bmp, 0, 0);
  bmp.close && bmp.close();
}
async function rasterFromPdfPage(n) {
  const page = await state.pdf.getPage(n);
  const vp1 = page.getViewport({ scale: 1 });
  const scale = Math.min(400 / 72, MAX_SIDE / Math.max(vp1.width, vp1.height));
  const vp = page.getViewport({ scale });
  const c = $('canvas');
  c.width = Math.round(vp.width); c.height = Math.round(vp.height);
  const g = c.getContext('2d');
  g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height);
  await page.render({ canvasContext: g, viewport: vp }).promise;
}
function grayFromCanvas() {
  const c = $('canvas');
  const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
  const a = new Uint8ClampedArray(c.width * c.height);
  for (let i = 0; i < a.length; i++) a[i] = (d[i * 4] * 299 + d[i * 4 + 1] * 587 + d[i * 4 + 2] * 114) / 1000;
  return { width: c.width, height: c.height, data: a };
}

async function openBlob(blob, name) {
  state.srcName = name;
  state.pdf = null;
  $('pagepick').hidden = true;
  clearResults();
  try {
    const isPdf = blob.type === 'application/pdf' || /\.pdf$/i.test(name);
    if (isPdf) {
      if (!window.pdfjsLib) throw new Error('pdf.js did not load, so PDFs cannot be opened. Try a PNG or JPG.');
      setStatus('Reading the PDF');
      pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER;
      state.pdf = await pdfjsLib.getDocument({ data: new Uint8Array(await blob.arrayBuffer()) }).promise;
      if (state.pdf.numPages > 1) {
        $('page').innerHTML = Array.from({ length: state.pdf.numPages }, (_, i) => `<option value="${i + 1}">${i + 1} of ${state.pdf.numPages}</option>`).join('');
        $('pagepick').hidden = false;
      }
      await runPdfPage(1);
    } else {
      setStatus('Decoding the image');
      await rasterFromImage(blob);
      await runCanvas();
    }
  } catch (err) {
    fail(err);
  }
}
async function runPdfPage(n) {
  setStatus(`Rendering page ${n}`);
  await rasterFromPdfPage(n);
  await runCanvas(state.pdf && state.pdf.numPages > 1 ? `page ${n}` : '');
}
async function runCanvas(pageLabel = '') {
  const c = $('canvas');
  $('overlay').setAttribute('viewBox', `0 0 ${c.width} ${c.height}`);
  $('caption').textContent = `${state.srcName}${pageLabel ? ', ' + pageLabel : ''} · ${c.width} × ${c.height} px`;
  const myRun = state.run + 1;
  const res = await infer(grayFromCanvas(), (msg) => { if (state.run === myRun) setStatus(msg + '…'); });
  if (state.run !== myRun) return; // a newer page replaced this one
  state.dets = res.dets.map((d, i) => ({ ...d, i, fam: famOf(d) }));
  state.timing = res.timing;
  render();
  const nh = state.dets.filter((d) => d.cls.startsWith('note_')).length;
  setStatus(`Found ${state.dets.length} symbols, ${nh} of them noteheads, in ${(res.timing.total_ms / 1000).toFixed(1)} s.`, 'done');
}
function fail(err) {
  console.warn(err);
  setStatus('Could not read this file: ' + (err.message || err), 'error');
}
function clearResults() {
  state.dets = [];
  $('overlay').replaceChildren();
  $('facts').replaceChildren();
  $('staves').replaceChildren();
  $('fam').replaceChildren();
  showPick(null);
}

// ---------- drawing ----------
function render() {
  const svg = $('overlay');
  const frag = document.createDocumentFragment();
  // big boxes first so small ones stay on top and hoverable
  const order = [...state.dets].sort((a, b) => area(b) - area(a));
  for (const d of order) {
    const [x0, y0, x1, y1] = d.xyxy;
    const r = document.createElementNS(SVGNS, 'rect');
    r.setAttribute('x', x0); r.setAttribute('y', y0);
    r.setAttribute('width', Math.max(1, x1 - x0)); r.setAttribute('height', Math.max(1, y1 - y0));
    r.setAttribute('class', 'box f-' + d.fam);
    r.dataset.i = d.i;
    frag.appendChild(r);
  }
  svg.replaceChildren(frag);
  applyHidden();
  renderLegend();
  renderSummary();
}
const area = (d) => (d.xyxy[2] - d.xyxy[0]) * (d.xyxy[3] - d.xyxy[1]);
function applyHidden() {
  for (const f of FAMILIES) $('overlay').classList.toggle('hide-' + f.key, state.hidden.has(f.key));
}

function renderLegend() {
  const counts = countBy(state.dets, (d) => d.fam);
  $('legend').innerHTML = FAMILIES.map((f) => `<li><label class="chip">
    <input type="checkbox" data-fam="${f.key}" ${state.hidden.has(f.key) ? '' : 'checked'}>
    <span class="swatch f-${f.key}" aria-hidden="true"></span>
    <span class="name">${f.label}</span><span class="n">${counts[f.key] || 0}</span></label></li>`).join('');
}
$('legend').addEventListener('change', (e) => {
  const k = e.target.dataset.fam;
  if (!k) return;
  e.target.checked ? state.hidden.delete(k) : state.hidden.add(k);
  applyHidden();
});

// ---------- summary ----------
const countBy = (xs, f) => xs.reduce((m, x) => ((m[f(x)] = (m[f(x)] || 0) + 1), m), {});
function staves() {
  // one staff per clef row: clefs whose vertical centres are within a clef height of each other merge
  const clefs = state.dets.filter((d) => d.fam === 'clef' && d.conf >= 0.3)
    .map((d) => ({ y: (d.xyxy[1] + d.xyxy[3]) / 2, h: d.xyxy[3] - d.xyxy[1], kind: CLEF_NAME(d.cls), x: d.xyxy[0] }))
    .sort((a, b) => a.y - b.y);
  const rows = [];
  for (const c of clefs) {
    const last = rows[rows.length - 1];
    if (last && Math.abs(c.y - last.y) < Math.max(c.h, last.h) * 0.6) {
      if (c.x < last.x) { last.kind = c.kind; last.x = c.x; }
    } else rows.push({ ...c });
  }
  return rows;
}
function renderSummary() {
  const t = state.timing;
  const notes = state.dets.filter((d) => d.cls.startsWith('note_'));
  const fact = (k, v) => `<dt>${k}</dt><dd>${v}</dd>`;
  $('facts').innerHTML = [
    fact('Detection time', `${(t.total_ms / 1000).toFixed(2)} s <span class="muted">(trunk ${(t.dense_ms / 1000).toFixed(2)} s, verifier ${(t.rel_ms / 1000).toFixed(2)} s)</span>`),
    fact('Model load', `${(t.load_ms / 1000).toFixed(2)} s <span class="muted">(once per visit)</span>`),
    fact('Model input', `${t.input[3]} × ${t.input[2]} px, staff space ${t.sp} px`),
    fact('Symbols', `${state.dets.length} <span class="muted">from ${t.n_cand} candidates</span>`),
    fact('Noteheads', String(notes.length)),
  ].join('');

  const rows = staves();
  const tally = rows.map(() => ({ v1: 0, v2: 0, vx: 0 }));
  const unassigned = { v1: 0, v2: 0, vx: 0 };
  for (const n of notes) {
    const y = (n.xyxy[1] + n.xyxy[3]) / 2;
    let best = -1, bd = Infinity;
    rows.forEach((r, i) => { const dd = Math.abs(r.y - y); if (dd < bd) { bd = dd; best = i; } });
    (best >= 0 ? tally[best] : unassigned)[n.fam]++;
  }
  const SATB = { treble: ['S', 'A'], bass: ['T', 'B'] };
  const head = '<thead><tr><th scope="col">Staff</th><th scope="col"><span class="swatch f-v1"></span>Voice 1</th><th scope="col"><span class="swatch f-v2"></span>Voice 2</th><th scope="col">Other</th></tr></thead>';
  const cell = (n, tag) => `${n}${tag && n ? ` <span class="muted">${tag}</span>` : ''}`;
  const body = rows.map((r, i) => {
    const sv = SATB[r.kind] || [];
    return `<tr><th scope="row">${i + 1} <span class="muted">${r.kind}</span></th><td>${cell(tally[i].v1, sv[0])}</td><td>${cell(tally[i].v2, sv[1])}</td><td>${tally[i].vx}</td></tr>`;
  });
  if (!rows.length) body.push(`<tr><th scope="row">No clefs found</th><td>${unassigned.v1}</td><td>${unassigned.v2}</td><td>${unassigned.vx}</td></tr>`);
  $('staves').innerHTML = head + '<tbody>' + body.join('') + '</tbody>';
  const v1 = notes.filter((n) => n.fam === 'v1').length, v2 = notes.filter((n) => n.fam === 'v2').length;
  $('voicewarn').hidden = !(notes.length >= 20 && Math.min(v1, v2) < notes.length * 0.1);

  const byFam = {};
  for (const d of state.dets) (byFam[d.fam] ||= []).push(d);
  $('fam').innerHTML = '<thead><tr><th scope="col">Family</th><th scope="col">Count</th><th scope="col">Most common classes</th></tr></thead><tbody>' +
    FAMILIES.filter((f) => byFam[f.key]).map((f) => {
      const top = Object.entries(countBy(byFam[f.key], (d) => d.cls)).sort((a, b) => b[1] - a[1]).slice(0, 3)
        .map(([c, n]) => `<code>${c}</code>&nbsp;${n}`).join(', ');
      return `<tr><th scope="row"><span class="swatch f-${f.key}"></span>${f.label}</th><td>${byFam[f.key].length}</td><td>${top}</td></tr>`;
    }).join('') + '</tbody>';
}

// ---------- picking ----------
let pinned = null;
function showPick(d) {
  const el = $('pick');
  document.querySelectorAll('#overlay .box.sel').forEach((b) => b.classList.remove('sel'));
  if (!d) { el.innerHTML = '<p class="muted">Hover or click a box on the page.</p>'; return; }
  const box = document.querySelector(`#overlay .box[data-i="${d.i}"]`);
  box && box.classList.add('sel');
  const fam = FAMILIES.find((f) => f.key === d.fam);
  const attrs = d.attrs ? Object.entries(d.attrs).filter(([, v]) => v !== '<na>')
    .map(([k, v]) => `<dt>${k.replace('_', ' ')}</dt><dd>${v}</dd>`).join('') : '';
  const [x0, y0, x1, y1] = d.xyxy.map(Math.round);
  el.innerHTML = `<p class="cls"><span class="swatch f-${d.fam}"></span><code>${d.cls}</code></p>
    <dl class="facts"><dt>Family</dt><dd>${fam.label}</dd><dt>Confidence</dt><dd>${(d.conf * 100).toFixed(1)} %</dd>${attrs}
    <dt>Box</dt><dd>${x0}, ${y0} to ${x1}, ${y1}</dd></dl>${pinned ? '<p class="muted">Pinned. Click it again or press Escape to release.</p>' : ''}`;
}
const detAt = (t) => (t && t.classList && t.classList.contains('box') ? state.dets[Number(t.dataset.i)] : null);
$('overlay').addEventListener('pointerover', (e) => { if (!pinned) { const d = detAt(e.target); d && showPick(d); } });
$('overlay').addEventListener('click', (e) => {
  const d = detAt(e.target);
  pinned = d && pinned !== d ? d : null;
  showPick(d);
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && pinned) { pinned = null; showPick(null); } });

// ---------- wiring ----------
function loadSample(btn) {
  document.querySelectorAll('.sample').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
  setStatus('Fetching the sample');
  fetch(btn.dataset.src).then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.blob();
  }).then((b) => openBlob(b, btn.dataset.name)).catch(fail);
}
document.querySelectorAll('.sample').forEach((b) => b.addEventListener('click', () => loadSample(b)));
$('file').addEventListener('change', (e) => {
  const f = e.target.files[0];
  if (!f) return;
  document.querySelectorAll('.sample').forEach((b) => b.setAttribute('aria-pressed', 'false'));
  openBlob(f, f.name);
  e.target.value = '';
});
$('page').addEventListener('change', (e) => runPdfPage(Number(e.target.value)).catch(fail));
const drop = $('drop');
for (const ev of ['dragenter', 'dragover']) document.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); });
for (const ev of ['dragleave', 'drop']) document.addEventListener(ev, (e) => { e.preventDefault(); if (ev === 'drop' || !e.relatedTarget) drop.classList.remove('over'); });
document.addEventListener('drop', (e) => {
  const f = e.dataTransfer && e.dataTransfer.files[0];
  if (!f) return;
  document.querySelectorAll('.sample').forEach((b) => b.setAttribute('aria-pressed', 'false'));
  openBlob(f, f.name);
});

renderLegend();
loadSample(document.querySelector('.sample[aria-pressed="true"]'));
