#!/usr/bin/env node
// Assembles the GitHub Pages site into site/:
//   site/index.html        landing page
//   site/app/              the converter (mvp/dist, wrapped as a full HTML document)
//   site/status/           build log, plan, research and accuracy tracker
//   site/docs/<name>.html  every docs/*.md rendered (design document, research, trials)
// Usage: node tools/build-site.mjs   (run `npm run build` first so mvp/dist is current)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'site');
const REPO = 'https://github.com/pension-plan/score-scan-reader';
const MERMAID = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js';
// Links that pointed at claude.ai artifacts are rewritten to their Pages equivalents.
const REWRITE = [
  ['https://claude.ai/artifact/6LdzqJaeeVRkJiRPgn9ozv', '../app/'],
  ['https://claude.ai/artifact/ETew3a3LisBiqZaMWpju7R', '../status/'],
];

const head = (title, extra = '') => `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${title}</title>
${extra}</head>
<body>
`;
const wrap = (page, fallbackTitle) => {
  const title = (page.match(/<title>([^<]*)<\/title>/) || [])[1] || fallbackTitle;
  let body = page.replace(/<title>[^<]*<\/title>\s*/, '').replace(/<meta name="claude:viewport-fit-sides"[^>]*>\s*/, '');
  for (const [from, to] of REWRITE) body = body.split(from).join(to);
  return head(title) + body + '\n</body>\n</html>\n';
};
const copyDir = (src, dst) => {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    if (e.isDirectory()) copyDir(s, d); else fs.copyFileSync(s, d);
  }
};

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

// app
copyDir(path.join(ROOT, 'mvp/dist'), path.join(OUT, 'app'));
fs.writeFileSync(path.join(OUT, 'app/index.html'), wrap(fs.readFileSync(path.join(ROOT, 'mvp/dist/index.html'), 'utf8'), 'Score Scan Reader'));

// status page
const statusSrc = path.join(ROOT, 'docs/status/omr-build.html');
if (fs.existsSync(statusSrc)) {
  fs.mkdirSync(path.join(OUT, 'status'), { recursive: true });
  fs.writeFileSync(path.join(OUT, 'status/index.html'), wrap(fs.readFileSync(statusSrc, 'utf8'), 'Scan-to-MusicXML Build'));
}

// copista-2m browser demo (screenshots stay out of the site)
const mlDemo = path.join(ROOT, 'demo/ml');
if (fs.existsSync(mlDemo)) {
  copyDir(mlDemo, path.join(OUT, 'ml-demo'));
  fs.rmSync(path.join(OUT, 'ml-demo/shots'), { recursive: true, force: true });
}

// docs
const DOC_CSS = `<style>
:root { --bg: #fbfbfa; --fg: #1b1e24; --muted: #5a6170; --rule: #dde1e7; --accent: #2456a6; --code: #f0f2f5; }
@media (prefers-color-scheme: dark) { :root { --bg: #13161b; --fg: #e5e8ed; --muted: #a2aab7; --rule: #2b313b; --accent: #82a8ea; --code: #1c2028; color-scheme: dark; } }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.65 "Source Serif 4", Georgia, serif; padding: 32px max(16px, env(safe-area-inset-right, 0px)) 64px max(16px, env(safe-area-inset-left, 0px)); }
main { max-width: 820px; margin: 0 auto; }
h1, h2, h3, h4 { font-family: system-ui, sans-serif; line-height: 1.25; text-wrap: balance; }
a { color: var(--accent); }
code, pre { font-family: ui-monospace, Menlo, monospace; font-size: 0.86em; background: var(--code); border-radius: 4px; }
code { padding: 1px 4px; } pre { padding: 12px 14px; overflow-x: auto; } pre code { padding: 0; background: none; }
table { border-collapse: collapse; display: block; overflow-x: auto; font-size: 0.92em; }
th, td { border: 1px solid var(--rule); padding: 6px 10px; text-align: left; vertical-align: top; }
nav.crumbs { font: 0.85rem system-ui, sans-serif; color: var(--muted); margin-bottom: 24px; }
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
`;
const docsDir = path.join(ROOT, 'docs');
const docs = fs.readdirSync(docsDir).filter((f) => f.endsWith('.md')).sort();
fs.mkdirSync(path.join(OUT, 'docs'), { recursive: true });
const renderer = new marked.Renderer();
const baseCode = renderer.code.bind(renderer);
renderer.code = (tok) => (tok.lang === 'mermaid' ? `<pre class="mermaid">${tok.text}</pre>` : baseCode(tok));
for (const f of docs) {
  let md = fs.readFileSync(path.join(docsDir, f), 'utf8');
  for (const [from, to] of REWRITE) md = md.split(from).join('../' + to.replace(/^\.\.\//, ''));
  const html = marked.parse(md, { renderer, gfm: true });
  const title = (md.match(/^#\s+(.+)$/m) || [])[1] || f.replace(/\.md$/, '');
  fs.writeFileSync(path.join(OUT, 'docs', f.replace(/\.md$/, '.html')),
    head(title, DOC_CSS) + `<main><nav class="crumbs"><a href="../">Score Scan Reader</a> / docs / ${f} · <a href="${REPO}/blob/main/docs/${f}">source</a></nav>\n${html}</main>\n<script src="${MERMAID}"></script>\n<script>window.mermaid && mermaid.initialize({ startOnLoad: true, theme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'default' });</script>\n</body>\n</html>\n`);
}

// landing page
const label = { 'SDD.md': 'Software design document', 'research-omr.md': 'Research: current OMR methods', 'research-voices.md': 'Research: voice and part separation', 'spike-classical.md': 'Trial: plain-JS image pipeline', 'spike-ocr.md': 'Trial: lyric OCR', 'spike-ml.md': 'Trial: pretrained ML models', 'TIMELINE.md': 'Build timeline (AEDT)' };
const docLinks = docs.map((f) => `<li><a href="docs/${f.replace(/\.md$/, '.html')}">${label[f] || f.replace(/\.md$/, '')}</a></li>`).join('\n');
fs.writeFileSync(path.join(OUT, 'index.html'), head('Score Scan Reader', DOC_CSS) + `<main>
<h1>Score Scan Reader</h1>
<p>Converts scanned sheet music (image-only PDFs, PNG or JPG) into MusicXML 4.0 in your browser. Lyrics are kept, closed-score SATB is split into separate parts, and piano grand staves stay together. Your file never leaves the browser.</p>
<ul>
<li><a href="app/"><strong>Open the converter</strong></a></li>
<li><a href="status/">Build log, plan, research findings and accuracy tracker</a></li>
<li><a href="ml-demo/">copista-2m in the browser: the ML symbol detector on a sample scan or your own page</a></li>
<li><a href="${REPO}">Source code</a> · <a href="${REPO}/releases">Releases and downloads</a> · <a href="${REPO}/actions">CI</a></li>
</ul>
<h2>Documents</h2>
<ul>
${docLinks}
</ul>
</main>
</body>
</html>
`);
console.log(`site/ built: app, status, ${docs.length} docs`);

// ---- version bar (top) and release footer (bottom) on every page ------------------
// Says exactly which code the page runs: the latest release, and how many commits
// the build is ahead of it (Pages rebuilds on every push, so it can run unreleased
// code). Ages are computed in the viewer's browser in Sydney time and tick every
// minute; the latest release is re-checked from the GitHub API on load.
{
  const { execSync } = await import('node:child_process');
  const sh = (c) => { try { return execSync(c, { cwd: ROOT, stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch { return ''; } };
  const API = 'https://api.github.com/repos/pension-plan/score-scan-reader';
  const hdrs = { 'user-agent': 'score-scan-reader-site', ...(process.env.GITHUB_TOKEN ? { authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {}) };
  const getJSON = async (u) => { try { const r = await fetch(u, { signal: AbortSignal.timeout(8000), headers: hdrs }); return r.ok ? await r.json() : null; } catch { return null; } };
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
  const sha = process.env.GITHUB_SHA || sh('git rev-parse HEAD');
  const rel = await getJSON(`${API}/releases/latest`);
  let ahead = null;
  if (rel && rel.tag_name && sha) {
    const cmp = await getJSON(`${API}/compare/${encodeURIComponent(rel.tag_name)}...${sha}`);
    if (cmp && typeof cmp.ahead_by === 'number') ahead = cmp.ahead_by;
  }
  const info = {
    version: rel && rel.tag_name ? rel.tag_name.replace(/^.*-v/, '') : pkg.version,
    tag: rel ? rel.tag_name : null,
    releasedAt: rel ? rel.published_at : null,
    releaseUrl: rel ? rel.html_url : `${REPO}/releases`,
    ahead,
    commit: sha.slice(0, 7),
    builtAt: new Date().toISOString(),
  };
  const bar = `
<div class="ssr-verbar" role="note" aria-label="Version" style="font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:6px max(16px,env(safe-area-inset-right,0px)) 6px max(16px,env(safe-area-inset-left,0px));border-bottom:1px solid rgba(127,127,127,.35);display:flex;flex-wrap:wrap;gap:2px 10px;align-items:baseline;overflow-wrap:anywhere">
<span>Version <a class="ssr-rel-link" href="${info.releaseUrl}" style="color:inherit"><b class="ssr-rel-ver">v${info.version}</b></a><span class="ssr-ahead"></span></span>
<span class="ssr-rel-age" style="opacity:.8"></span>
<span style="opacity:.8">build <a href="${REPO}/commit/${info.commit}" style="color:inherit">${info.commit}</a> <span class="ssr-build-age"></span></span>
<span class="ssr-newer"></span>
</div>`;
  const footer = `
<div id="ssr-release" style="font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:10px max(16px,env(safe-area-inset-right,0px)) calc(10px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));border-top:1px solid rgba(127,127,127,.35);opacity:.85;text-align:center;overflow-wrap:anywhere">
<a class="ssr-rel-link" href="${info.releaseUrl}" style="color:inherit"><b class="ssr-rel-ver">v${info.version}</b></a><span class="ssr-ahead"></span> · <span class="ssr-rel-age"></span> · page built from <a href="${REPO}/commit/${info.commit}" style="color:inherit">${info.commit}</a> <span class="ssr-build-age"></span><span class="ssr-newer"></span>
</div>
<script>
(function () {
  var B = ${JSON.stringify(info)};
  var rel = { ver: B.version, tag: B.tag, at: B.releasedAt, url: B.releaseUrl }, newer = null;
  function ago(iso) {
    var s = Math.max(0, (Date.now() - Date.parse(iso)) / 1000);
    if (s < 60) return 'just now';
    var m = Math.floor(s / 60), h = Math.floor(m / 60), d = Math.floor(h / 24);
    if (d >= 1) return d + ' d ' + (h % 24) + ' h ago';
    if (h >= 1) return h + ' h ' + (m % 60) + ' min ago';
    return m + ' min ago';
  }
  function syd(iso) { return new Date(iso).toLocaleString('en-AU', { timeZone: 'Australia/Sydney', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false, timeZoneName: 'short' }); }
  function all(c, f) { var n = document.getElementsByClassName(c); for (var i = 0; i < n.length; i++) f(n[i]); }
  function paint() {
    all('ssr-rel-ver', function (e) { e.textContent = 'v' + rel.ver; });
    all('ssr-rel-link', function (e) { e.href = rel.url; });
    all('ssr-ahead', function (e) { e.textContent = B.ahead > 0 ? ' + ' + B.ahead + ' commit' + (B.ahead === 1 ? '' : 's') + ' (unreleased build)' : (B.ahead === 0 ? ' (exact release)' : ''); });
    all('ssr-rel-age', function (e) { e.textContent = rel.at ? 'released ' + ago(rel.at) + ' (' + syd(rel.at) + ')' : 'not released yet'; });
    all('ssr-build-age', function (e) { e.textContent = ago(B.builtAt); });
    all('ssr-newer', function (e) { e.textContent = newer ? ' · newer release v' + newer + ' is out' : ''; });
  }
  paint();
  setInterval(paint, 60000);
  try {
    fetch('https://api.github.com/repos/pension-plan/score-scan-reader/releases/latest').then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || !j.tag_name) return;
      if (j.tag_name === B.tag) { rel.at = j.published_at; } else { newer = j.tag_name.replace(/^.*-v/, ''); }
      paint();
    }).catch(function () {});
  } catch (e) {}
})();
</script>
`;
  // /app/ only: which engine the page runs, and the changelog of recent releases
  // (CHANGELOG.md is written by release-please; Pages rebuilds on each release merge)
  let changes = '';
  const clPath = path.join(ROOT, 'CHANGELOG.md');
  if (fs.existsSync(clPath)) {
    const secs = fs.readFileSync(clPath, 'utf8').split(/^(?=## \[)/m).filter((x) => x.startsWith('## ['));
    const sec = (x) => marked.parse(x.replace(/^## \[([^\]]+)\]\([^)]*\) \(([^)]*)\)/, '### v$1 · $2'));
    const latest = secs[0] ? sec(secs[0]) : '';
    const older = secs.slice(1, 6).map(sec).join('');
    changes = `
<style>.ssr-cl a{color:inherit}.ssr-cl h3{font-size:15px;margin:10px 0 4px}.ssr-cl ul{margin:4px 0;padding-left:20px}</style>
<details class="ssr-changes" open style="font:14px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif;margin:0;padding:8px max(16px,env(safe-area-inset-right,0px)) 10px max(16px,env(safe-area-inset-left,0px));border-bottom:1px solid rgba(127,127,127,.35);overflow-wrap:anywhere">
<summary style="cursor:pointer;font-weight:600">What's new <span style="font-weight:400;opacity:.8">· engine: plain-JavaScript recognition pipeline (the copista-2m ML detector is not in this app yet; try it in the <a href="../ml-demo/" style="color:inherit">ML demo</a>)</span></summary>
<div class="ssr-cl" style="max-width:72ch;font-size:13px">${latest}
${older ? `<details><summary style="cursor:pointer">Earlier releases</summary>${older}</details>` : ''}
<p style="opacity:.8">Full history: <a href="${REPO}/blob/main/CHANGELOG.md" style="color:inherit">CHANGELOG.md</a> · <a href="${REPO}/releases" style="color:inherit">all releases and downloads</a></p></div>
</details>`;
  }
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]);
  let n = 0;
  for (const f of walk(OUT).filter((f) => f.endsWith('.html'))) {
    let s = fs.readFileSync(f, 'utf8');
    if (s.includes('ssr-verbar')) continue;
    const top = bar + (path.relative(OUT, f) === path.join('app', 'index.html') ? changes : '');
    s = /<body[^>]*>/i.test(s) ? s.replace(/<body[^>]*>/i, (m) => m + top) : top + s;
    s = /<\/body>/i.test(s) ? s.replace(/<\/body>(?![\s\S]*<\/body>)/i, footer + '</body>') : s + footer;
    fs.writeFileSync(f, s); n++;
  }
  console.log(`version bar: v${info.version}${info.ahead != null ? ' + ' + info.ahead + ' commits' : ''} (build ${info.commit}) on ${n} pages`);
}
