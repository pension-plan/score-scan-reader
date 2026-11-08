// UI feature check for dist/index.html under a simulated artifact CSP.
//   node ui/test/ui-check.js [--html path/to/index.html] [--out work/ui-check.json] [--shots prefix] [--no-drop]
// Serves the page (default dist/index.html) with dist/assets, converts the bundled
// sample at 1280 px (light, dark) and 400 px (light, dark), and checks: console errors,
// horizontal scroll, the 7-step stepper (structure, aria, states painted during the run),
// drag-depth dropzone, a real drop conversion, overlay toggle, per-part provenance,
// code block line numbers, Copy (clipboard and fallback), token contrast in both themes.
// Prints a JSON report; the score is passed checks / total checks.
const http = require('http'), fs = require('fs'), path = require('path');
const MVP = path.join(__dirname, '../..');
const { chromium } = require(path.join(MVP, 'tools/pw/node_modules/playwright'));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const HTML = path.resolve(arg('--html', path.join(MVP, 'dist/index.html')));
const OUT = arg('--out', null);
const SHOTS = arg('--shots', null);
const DIST = path.join(MVP, 'dist');
const CSP = "default-src 'self'; script-src https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'wasm-unsafe-eval' blob:; connect-src 'self' blob: data:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com";
const types = { '.html': 'text/html', '.js': 'text/javascript', '.pdf': 'application/pdf', '.gz': 'application/gzip' };

const srv = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html', 'Content-Security-Policy': CSP });
    return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>[hidden]{display:none!important}</style></head><body>' + fs.readFileSync(HTML, 'utf8') + '</body></html>');
  }
  const f = path.join(DIST, p);
  if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream', 'Content-Security-Policy': CSP });
  fs.createReadStream(f).pipe(res);
});

// records which stepper step was current at each painted frame
const PAINT_LOG = `(() => { window.__paintLog = []; const tick = () => {
  const li = document.querySelector('#steps li[aria-current="step"]');
  const id = li ? (li.querySelector('.step-title') || li).textContent.replace(/,.*$/, '').trim() : null;
  const L = window.__paintLog; if (id && L[L.length - 1] !== id) L.push(id);
  requestAnimationFrame(tick); }; requestAnimationFrame(tick); })();`;

function lum(hex) {
  const m = hex.replace('#', '');
  const v = (m.length === 3 ? m.split('').map((c) => c + c) : m.match(/../g)).map((h) => parseInt(h, 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
}
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const PAIRS = [['--ink', '--panel', 4.5], ['--ink', '--bg', 4.5], ['--muted', '--panel', 4.5], ['--muted', '--bg', 4.5], ['--muted', '--panel-2', 4.5],
  ['--accent', '--panel', 4.5], ['--accent', '--bg', 3], ['--accent-ink', '--accent', 4.5], ['--warn-ink', '--warn-bg', 4.5], ['--ok', '--panel', 4.5],
  ['--syn-tag', '--panel', 4.5], ['--syn-attr', '--panel', 4.5], ['--syn-val', '--panel', 4.5], ['--rule-strong', '--panel', 3], ['--accent', '--accent-wash', 4.5]];

srv.listen(0, async () => {
  const port = srv.address().port;
  const url = `http://localhost:${port}/`;
  const browser = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell' });
  const checks = {};
  const info = {};
  const ok = (name, pass, detail) => { checks[name] = { pass: !!pass, ...(detail !== undefined ? { detail } : {}) }; };
  const views = [[1280, 'light'], [400, 'light'], [400, 'dark'], [1280, 'dark']];
  for (const [width, scheme] of views) {
    const tag = `${width}${scheme === 'dark' ? 'd' : ''}`;
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
    await page.addInitScript(PAINT_LOG);
    const t0 = Date.now();
    await page.goto(url);
    let res = null;
    try { await page.waitForFunction(() => window.__omrResult, null, { timeout: 180000 }); res = await page.evaluate(() => window.__omrResult); } catch (e) { errors.push('no result: ' + e.message); }
    info['secs' + tag] = (Date.now() - t0) / 1000;
    info['parts' + tag] = res && res.parts;
    ok(`${tag}: converts sample, no console errors`, res && !res.error && errors.length === 0, errors.slice(0, 5));
    ok(`${tag}: no horizontal page scroll`, !(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)));
    ok(`${tag}: notation preview drawn`, (await page.evaluate(() => document.querySelectorAll('#osmd svg').length)) > 0);
    if (SHOTS) await page.screenshot({ path: `${SHOTS}-${tag}.png`, fullPage: width === 1280 && scheme === 'light' });

    if (tag === '1280') {
      // stepper structure and states
      const st = await page.evaluate(() => {
        const nav = document.querySelector('nav[aria-label="Conversion progress"]');
        const lis = nav ? [...nav.querySelectorAll('ol > li')] : [];
        return { nav: !!nav, n: lis.length, states: lis.map((l) => l.dataset.state), titles: lis.map((l) => (l.querySelector('.step-title') || l).textContent),
          details: lis.map((l) => (l.querySelector('.step-detail') || {}).textContent || ''), sepHidden: [...document.querySelectorAll('#steps .sep')].every((s) => s.getAttribute('aria-hidden') === 'true') };
      });
      info.stepTitles = st.titles; info.stepDetails = st.details;
      ok('stepper: nav[aria-label] > ol with 7 steps', st.nav && st.n === 7, st.n);
      ok('stepper: every step complete/skipped at end, with result facts', st.n === 7 && st.states.every((s) => s === 'complete' || s === 'skipped') && st.details.filter(Boolean).length >= 6, st.states);
      ok('stepper: state read aloud (sr-only), separators aria-hidden', st.titles.length === 7 && st.titles.every((t) => /, (completed|skipped|current|upcoming|failed)/.test(t)) && st.sepHidden);
      const log = await page.evaluate(() => window.__paintLog || []);
      info.paintLog = log;
      ok('stepper: at least 4 distinct stages painted as current during the run', new Set(log).size >= 4, log);
      // parts provenance
      const prov = await page.evaluate(() => [...document.querySelectorAll('#parts li .part-src')].map((e) => e.textContent));
      info.provenance = prov;
      ok('parts: each part states the staff it came from', prov.length > 0 && prov.length === (await page.evaluate(() => window.__omrResult.parts.length)) && prov.every((t) => /staff \d|staves \d/i.test(t)), prov);
      ok('parts: summary line (parts, staves, key, time, measures)', /part.*staves?.*(major|key).*\d+\/\d+.*measure/i.test(await page.evaluate(() => (document.getElementById('partsSummary') || {}).textContent || '')));
      // code block
      const cb = await page.evaluate(() => {
        const g = document.getElementById('gutter'), x = window.__omrResult.xmlLength;
        const ta = document.getElementById('xml');
        return { gutter: g ? g.textContent.split('\n').length : 0, first: g ? g.textContent.split('\n')[0] : '', lines: ta ? ta.value.split('\n').length : 0, full: ta ? ta.value.length : 0, x,
          sel: g ? getComputedStyle(g).userSelect : '', label: !!document.querySelector('.code-head'),
          aligned: !!g && !!document.getElementById('code') && g.scrollHeight === document.getElementById('code').parentNode.scrollHeight };
      });
      ok('code block: line-number gutter (not selectable) + header', cb.gutter > 10 && cb.first === '1' && cb.sel === 'none' && cb.label, cb);
      ok('code block: gutter rows line up with code rows', cb.aligned, cb);
      ok('code block: hidden textarea keeps the full MusicXML', cb.full === cb.x && cb.full > 0);
      // copy: clipboard path
      await page.click('#copy');
      await page.waitForTimeout(150);
      const c1 = await page.evaluate(async () => ({ label: document.getElementById('copy').textContent.trim(), clip: (await navigator.clipboard.readText()).length, x: window.__omrResult.xmlLength }));
      await page.waitForTimeout(1300);
      const c1b = await page.evaluate(() => document.getElementById('copy').textContent.trim());
      ok('copy: writes full text, label flips to Copied then back', /Copied/.test(c1.label) && c1.clip === c1.x && /^Copy$/.test(c1b), { ...c1, after: c1b });
      // copy: fallback when the clipboard refuses
      await page.evaluate(() => { navigator.clipboard.writeText = () => Promise.reject(new Error('denied')); });
      await page.click('#copy');
      await page.waitForTimeout(150);
      const c2 = await page.evaluate(() => { const ta = document.getElementById('xml'); return { visible: !!ta && ta.offsetParent !== null, selected: ta ? ta.selectionEnd - ta.selectionStart : 0, x: window.__omrResult.xmlLength, msg: (document.getElementById('copied') || {}).textContent || '' }; });
      ok('copy: fallback selects full text and says Ctrl/Cmd+C', c2.visible && c2.selected === c2.x && /Ctrl.*C/.test(c2.msg), c2);
      // overlay toggle
      const tg = await page.$('#overlayToggle');
      if (tg) {
        const before = await page.evaluate(() => ({ p: document.getElementById('overlayToggle').getAttribute('aria-pressed'), v: getComputedStyle(document.querySelector('#pages .ov')).visibility }));
        await tg.click();
        const after = await page.evaluate(() => ({ p: document.getElementById('overlayToggle').getAttribute('aria-pressed'), v: getComputedStyle(document.querySelector('#pages .ov')).visibility }));
        await tg.click();
        ok('overlay: toggle button (aria-pressed) hides and shows the markup', before.p === 'true' && before.v === 'visible' && after.p === 'false' && after.v === 'hidden', { before, after });
      } else ok('overlay: toggle button (aria-pressed) hides and shows the markup', false, 'no toggle');
      ok('overlay: legend names parts with distinct marker shapes', await page.evaluate(() => {
        const marks = [...document.querySelectorAll('#legend li svg')].map((s) => s.innerHTML.replace(/fill="[^"]*"|stroke="[^"]*"/g, ''));
        const n = (window.__omrResult.parts || []).length;
        return marks.length >= n && new Set(marks.slice(0, n)).size === n;
      }));
      // dropzone drag depth
      const dz = await page.evaluate(() => {
        const zone = document.getElementById('drop');
        if (!zone) return { ok: false };
        const dt = new DataTransfer(); dt.items.add(new File(['x'], 'x.pdf', { type: 'application/pdf' }));
        const fire = (el, type) => el.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt }));
        const kids = zone.querySelectorAll('button, h2, p');
        const title = () => (document.getElementById('dropTitle') || zone).textContent;
        const over = () => zone.classList.contains('over') || zone.dataset.state === 'over';
        fire(zone, 'dragenter'); fire(kids[0], 'dragenter'); fire(zone, 'dragleave');
        const mid = { over: over(), title: title(), live: (document.getElementById('dropLive') || {}).textContent };
        fire(kids[0], 'dragleave');
        return { mid, endOver: over(), endTitle: title() };
      });
      ok('dropzone: drag-depth counter keeps "over" while crossing children', dz.mid && dz.mid.over && /Drop it here/.test(dz.mid.title) && /Release to convert/.test(dz.mid.live || '') && !dz.endOver, dz);
      ok('dropzone: hidden file input opened by a visible button', await page.evaluate(() => { const i = document.getElementById('file'); const b = document.getElementById('choose'); return !!i && !!b && i.offsetWidth <= 1 && b.offsetWidth > 1; }));
      if (!process.argv.includes('--no-drop')) {
        // drop a real file (the sample) and wait for the second conversion
        await page.evaluate(() => { window.__omrResult = null; });
        await page.evaluate(async () => {
          const buf = await (await fetch('assets/sample-st-anselm.pdf')).arrayBuffer();
          const dt = new DataTransfer(); dt.items.add(new File([buf], 'dropped-hymn.pdf', { type: 'application/pdf' }));
          const zone = document.getElementById('drop');
          zone.dispatchEvent(new DragEvent('dragenter', { bubbles: true, cancelable: true, dataTransfer: dt }));
          zone.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
        });
        let dres = null;
        try { await page.waitForFunction(() => window.__omrResult, null, { timeout: 120000 }); dres = await page.evaluate(() => ({ r: window.__omrResult, title: (document.getElementById('dropTitle') || {}).textContent, file: (document.getElementById('fileName') || {}).textContent, tick: !!document.querySelector('#fileDone:not([hidden])') })); } catch (e) { dres = { err: e.message }; }
        ok('dropzone: dropping a PDF converts it; title and file row report it', dres && dres.r && !dres.r.error && /dropped-hymn\.pdf converted/.test(dres.title || '') && dres.file === 'dropped-hymn.pdf' && dres.tick, dres && { title: dres.title, file: dres.file, tick: dres.tick, err: dres.err });
      }
      // keyboard reachability
      ok('keyboard: main controls are focusable buttons', await page.evaluate(() => ['choose', 'sample', 'overlayToggle', 'copy'].every((id) => { const e = document.getElementById(id); return e && e.tagName === 'BUTTON' && e.tabIndex >= 0; })));
      ok('status: aria-live progress region', await page.evaluate(() => { const s = document.getElementById('status'); return !!s && (s.getAttribute('aria-live') === 'polite' || s.getAttribute('role') === 'status'); }));
    }
    if (tag === '400') {
      const cap = await page.evaluate(() => { const c = document.getElementById('stepCaption'); const t = document.querySelector('#steps .step-title'); return { cap: c ? c.offsetHeight > 0 : false, titleW: t ? t.getBoundingClientRect().width : 99, stepW: (document.getElementById('steps') || document.body).scrollWidth <= window.innerWidth }; });
      ok('400: stepper fits; only the current step title is shown', cap.cap && cap.titleW <= 1 && cap.stepW, cap);
    }
    if (scheme === 'dark' || tag === '1280') {
      const tok = await page.evaluate((pairs) => { const cs = getComputedStyle(document.documentElement); const o = {}; for (const [a, b] of pairs) { o[a] = cs.getPropertyValue(a).trim(); o[b] = cs.getPropertyValue(b).trim(); } return o; }, PAIRS);
      const bad = PAIRS.filter(([a, b, min]) => !/^#[0-9a-f]{3,6}$/i.test(tok[a] || '') || !/^#[0-9a-f]{3,6}$/i.test(tok[b] || '') || ratio(tok[a], tok[b]) < min).map(([a, b, min]) => `${a}/${b}=${tok[a] && tok[b] && /^#/.test(tok[a]) && /^#/.test(tok[b]) ? ratio(tok[a], tok[b]).toFixed(2) : 'n/a'}<${min}`);
      if (tag === '1280' || tag === '1280d') ok(`${scheme}: token contrast (text 4.5:1, graphics 3:1)`, bad.length === 0, bad);
    }
    await ctx.close();
  }
  await browser.close();
  srv.close();
  const names = Object.keys(checks);
  const passed = names.filter((n) => checks[n].pass).length;
  const report = { html: path.relative(MVP, HTML), score: +(passed / names.length).toFixed(3), passed, total: names.length, checks, info };
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(report, null, 1));
  console.log(JSON.stringify({ score: report.score, passed, total: names.length, failed: names.filter((n) => !checks[n].pass), secs: [info.secs1280, info.secs400, info['secs400d'], info['secs1280d']], paintLog: info.paintLog, stepDetails: info.stepDetails, provenance: info.provenance }, null, 1));
});
