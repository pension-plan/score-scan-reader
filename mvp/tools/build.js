// Bundles src/*.js (CommonJS) + ui/ into dist/index.html (artifact format) and
// checks the artifact contract, failing the build on any violation:
//   - no doctype/html/head/body tags; <title> of 2-4 words in the first 8 KB
//   - external scripts only from cdnjs/jsdelivr/unpkg, pinned to an exact version;
//     stylesheets only from Google Fonts
//   - no alert/confirm/prompt/print calls and no download links in page code, except
//     the guarded helper in ui/player.js (between <guarded-download> markers): the app's
//     primary home is GitHub Pages, where a .mid export should save as a file, so that
//     helper makes a real <a download> only when the page is not framed and opens a new
//     tab inside the claude.ai artifact frame (whose rules forbid download links)
//   - every relative require() between src modules resolves inside the bundle
//   - required assets present; each asset <= 15 MB, total <= 64 MB, page <= 16 MB
// Usage: node tools/build.js [--quiet]
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const SRC = path.join(ROOT, 'src');
const DIST = path.join(ROOT, 'dist');
// the page lives in mvp/ui/ only (the old src/ui copy is gone; no fallback)
const UI = path.join(ROOT, 'ui');
const quiet = process.argv.includes('--quiet');
const MB = 1024 * 1024;
// ML: the optional copista-2m detector (src/ml.js): model, onnxruntime-web wasm, and the
// licence / notice files that must ship with them (copy with node assets-src/ml/sync.js).
const ML_ASSETS = ['copista2m-dense.int8w.onnx', 'copista2m-rel.int8w.onnx', 'copista2m-classes.json', 'ort-wasm-simd-threaded.wasm',
  'LICENSE.copista-Apache-2.0.txt', 'NOTICE.copista-2m', 'NOTICE.copisteria', 'LICENSE.onnxruntime-web-MIT.txt', 'NOTICE.ml.txt'];
// playback: the sampled General MIDI subset (tools/soundfont.mjs) and its licence notice
const SOUND_ASSETS = ['gm-piano.json', 'gm-organ.json', 'gm-choir.json', 'gm-oohs.json', 'gm-strings.json', 'gm-flute.json', 'gm-clarinet.json', 'gm-brass.json', 'NOTICE.soundfont.txt'];
const REQUIRED_ASSETS = [...SOUND_ASSETS, 'tesseract-worker.min.js', 'tesseract-core-simd-lstm.wasm.js', 'eng.traineddata.gz', 'deu.traineddata.gz', 'sample-st-anselm.pdf', 'sample-maple-leaf-rag.pdf', 'samples.json', ...ML_ASSETS];
const SCRIPTS = [
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/tesseract.js/7.0.0/tesseract.min.js',
  'https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.9/build/opensheetmusicdisplay.min.js',
];
const FONTS = 'https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400..600&display=swap';

const errors = [];
const fail = (m) => errors.push(m);
for (const f of ['body.html', 'style.css', 'app.js']) if (!fs.existsSync(path.join(UI, f))) { console.error(`BUILD FAILED: ui/${f} is missing`); process.exit(1); }
if (fs.existsSync(path.join(SRC, 'ui'))) fail('src/ui/ exists again; the page is built from mvp/ui/ only, so edit there and remove src/ui/');

// ---- bundle: every src/*.js module (definitions are lazy, so unused ones cost bytes only)
const mods = fs.readdirSync(SRC).filter((f) => f.endsWith('.js')).map((f) => f.slice(0, -3)).sort();
if (!mods.includes('omr')) fail('src/omr.js is missing');
// The bundle is one named function, called once on the page; the page also
// starts a Web Worker from its source text (with ui/session.js), so recognition
// runs off the main thread without a second copy of the code.
// Node-only debug switches (process.env.X) in a module must not throw in the
// page: the bundle sees an empty process.env (in Node the modules run unbundled).
let bundle = 'function __omrBundle(){\nconst process=(typeof globalThis!=="undefined"&&globalThis.process&&globalThis.process.env)?globalThis.process:{env:{}};\nconst defs={},cache={};\nfunction req(n){n=n.replace(/^\\.\\//,"").replace(/\\.js$/,"");if(cache[n])return cache[n].exports;if(!defs[n])return {};const m={exports:{}};cache[n]=m;defs[n](req,m,m.exports);return m.exports;}\n';
for (const m of mods) {
  const code = fs.readFileSync(path.join(SRC, m + '.js'), 'utf8');
  for (const r of code.matchAll(/require\(\s*['"]\.\/([\w.-]+?)(?:\.js)?['"]\s*\)/g)) {
    if (!mods.includes(r[1])) fail(`src/${m}.js requires ./${r[1]}, which is not in src/`);
  }
  bundle += `defs[${JSON.stringify(m)}]=function(require,module,exports){\n${code}\n};\n`;
}
bundle += '(typeof self!=="undefined"?self:window).omrRequire=req;\n}\n__omrBundle();\n';

const css = fs.readFileSync(path.join(UI, 'style.css'), 'utf8');
const body = fs.readFileSync(path.join(UI, 'body.html'), 'utf8');
const app = fs.readFileSync(path.join(UI, 'app.js'), 'utf8');
// playback module (optional files): its CSS after style.css, its script before app.js
const playerCss = fs.existsSync(path.join(UI, 'player.css')) ? fs.readFileSync(path.join(UI, 'player.css'), 'utf8') : '';
const player = fs.existsSync(path.join(UI, 'player.js')) ? fs.readFileSync(path.join(UI, 'player.js'), 'utf8') : '';
const sessionPath = path.join(UI, 'session.js');
const session = fs.existsSync(sessionPath) ? fs.readFileSync(sessionPath, 'utf8') : '';
if (!session) fail('ui/session.js is missing (incremental per-page conversion)');
else if (!/function __omrSessionModule\(/.test(session)) fail('ui/session.js does not define __omrSessionModule()');
if (/<\/script/i.test(bundle + app + session + player)) fail('a script terminator (</script) appears inside the bundle or app');
if (/<\/style/i.test(css + playerCss)) fail('a </style> appears inside style.css');

const html = `<title>Score Scan Reader</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
${css}${playerCss}</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}">
${body}
${SCRIPTS.map((s) => `<script src="${s}"></script>`).join('\n')}
<script>
${bundle}</script>
<script>
${session}</script>
${player ? `<script>\n${player}</script>\n` : ''}<script>
${app}</script>
`;

// ---- artifact contract checks
const shell = html.replace(/<script>[\s\S]*?<\/script>/g, '<script></script>').replace(/<style>[\s\S]*?<\/style>/g, '<style></style>');
if (/<!doctype|<html[\s>]|<\/html>|<head[\s>]|<\/head>|<body[\s>]|<\/body>/i.test(shell)) fail('page shell contains doctype/html/head/body tags');
const title = (html.slice(0, 8192).match(/<title>([^<]*)<\/title>/) || [])[1];
if (!title) fail('no <title> in the first 8 KB');
else if (title.trim().split(/\s+/).length < 2 || title.trim().split(/\s+/).length > 4) fail(`title "${title}" is not 2-4 words`);
for (const m of shell.matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)) {
  const u = m[1];
  if (!/^https:\/\/(cdnjs\.cloudflare\.com\/ajax\/libs\/|cdn\.jsdelivr\.net\/npm\/|unpkg\.com\/)/.test(u)) fail(`script from a host outside the allowlist: ${u}`);
  if (!/(@|\/)\d+\.\d+\.\d+(\/|$)/.test(u)) fail(`script not pinned to an exact version: ${u}`);
}
for (const m of shell.matchAll(/<link\b[^>]*rel="stylesheet"[^>]*>/g)) {
  if (!/href="https:\/\/fonts\.googleapis\.com\//.test(m[0])) fail(`stylesheet outside Google Fonts: ${m[0]}`);
}
// the guarded download helper is the one place a download attribute may be set
const GUARD = /\/\/ <guarded-download>[\s\S]*?\/\/ <\/guarded-download>/;
const guarded = (player.match(GUARD) || [''])[0];
if (guarded && !/function framed\(\)[\s\S]*window\.self !== window\.top[\s\S]*if \(!framed\(\)\)/.test(guarded)) fail('ui/player.js: the guarded download helper must check the frame (framed()) before setting a download attribute');
const code = bundle + '\n' + session + '\n' + app + '\n' + player.replace(GUARD, '');
const banned = code.match(/(^|[^.\w$])(alert|confirm|prompt|print)\s*\(|window\.(alert|confirm|prompt|print)\b/m);
if (banned) fail(`banned dialog/print call in page code: "${banned[0].trim()}"`);
if (/\sdownload(=|\s|>)/i.test(shell) || /\.download\s*=|setAttribute\(\s*['"]download/.test(code)) fail('download link in page');
if (/(src|href)="\/(?!\/)/.test(shell) || /fetch\(\s*['"]\//.test(app)) fail('absolute-path asset reference; use relative assets/ paths');
if (!/:root\s*{/.test(css) || !/prefers-color-scheme:\s*dark/.test(css) || !/:root\[data-theme="dark"\]/.test(css)) fail('theme tokens for light and dark are incomplete');
if (!/max\(16px,\s*env\(safe-area-inset-left/.test(css)) fail('side gutter does not use max(16px, env(safe-area-inset-left))');

// ---- assets
// every language the pipeline's OCR config names (src/lyrics.js OCR_CONFIG) ships as traineddata
const lyrSrc = fs.existsSync(path.join(SRC, 'lyrics.js')) ? fs.readFileSync(path.join(SRC, 'lyrics.js'), 'utf8') : '';
// the second-pass languages (OCR_CONFIG.extraFiles: loaded only for accented lyric rows) and their notice
const ocrExtra = ((lyrSrc.match(/extraFiles:\s*\[([^\]]*)\]/) || [])[1] || '').match(/[\w.]+\.traineddata\.gz/g) || [];
for (const f of ocrExtra.concat(ocrExtra.length ? ['NOTICE.ocr-langs.txt'] : [])) if (!fs.existsSync(path.join(DIST, 'assets', f))) fail(`optional OCR asset dist/assets/${f} is missing`);
const ocrLangs = ((lyrSrc.match(/OCR_CONFIG\s*=\s*{[\s\S]*?langs:\s*['"]([\w+]+)['"]/) || [])[1] || 'eng').split('+');
for (const l of ocrLangs) if (!fs.existsSync(path.join(DIST, 'assets', `${l}.traineddata.gz`))) fail(`OCR_CONFIG names ${l}, but dist/assets/${l}.traineddata.gz is missing`);
const rows = [];
let total = 0;
for (const a of REQUIRED_ASSETS) if (!fs.existsSync(path.join(DIST, 'assets', a))) fail(`missing asset dist/assets/${a}`);
for (const f of fs.existsSync(path.join(DIST, 'assets')) ? fs.readdirSync(path.join(DIST, 'assets')) : []) {
  const n = fs.statSync(path.join(DIST, 'assets', f)).size;
  total += n;
  rows.push([`assets/${f}`, n]);
  if (n > 15 * MB) fail(`asset ${f} is ${(n / MB).toFixed(1)} MB (limit 15 MB)`);
}
const pageBytes = Buffer.byteLength(html);
if (pageBytes > 16 * MB) fail(`index.html is ${(pageBytes / MB).toFixed(1)} MB (limit 16 MB)`);
total += pageBytes;
if (total > 64 * MB) fail(`total ${(total / MB).toFixed(1)} MB exceeds 64 MB`);

if (errors.length) {
  console.error('BUILD FAILED (dist/index.html left unchanged):\n  - ' + errors.join('\n  - '));
  process.exit(1);
}
// atomic write, so a concurrent browser test never reads a half-written page
const tmp = path.join(DIST, `.index.html.${process.pid}.tmp`);
fs.writeFileSync(tmp, html);
fs.renameSync(tmp, path.join(DIST, 'index.html'));
if (!quiet) {
  rows.unshift(['index.html', pageBytes]);
  console.log(`ui: ${path.relative(ROOT, UI)}/  modules: ${mods.length} (${mods.join(', ')})`);
  for (const [f, n] of rows) console.log(`  ${f.padEnd(42)} ${(n / 1024).toFixed(0).padStart(7)} KB`);
  console.log(`  ${'total'.padEnd(42)} ${(total / 1024).toFixed(0).padStart(7)} KB`);
}
console.log('dist/index.html', html.length, 'bytes');
