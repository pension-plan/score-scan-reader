#!/usr/bin/env node
// Copy the benchmark scans that may be redistributed into dist/assets as example PDFs,
// and write dist/assets/samples.json (the app's example picker reads it).
//
//   node mvp/tools/sync-samples.mjs
//
// Items come from corpus/manifest-{real,synthetic}.json. Anything whose ATTRIBUTION.txt
// says "used by permission" or names Greentree (the restricted Bach encodings) is left
// out, as it is from the repository. Scans already shipped under another name (the two
// original samples) are reused by content hash instead of copied twice.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '../..');
const ASSETS = path.join(ROOT, 'mvp/dist/assets');
const RESTRICTED = /used by permission|greentree/i;
const hash = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');

const shipped = new Map();
for (const f of fs.readdirSync(ASSETS)) if (f.endsWith('.pdf')) shipped.set(hash(path.join(ASSETS, f)), f);

const out = [];
for (const [kind, group] of [['real', 'Real scans'], ['synthetic', 'Synthetic scans']]) {
  const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, `corpus/manifest-${kind}.json`), 'utf8'));
  for (const m of manifest) {
    const dir = path.join(ROOT, 'corpus', kind, m.id);
    const scan = path.join(dir, 'scan.pdf');
    if (!fs.existsSync(scan)) continue;
    const attr = path.join(dir, 'ATTRIBUTION.txt');
    if (fs.existsSync(attr) && RESTRICTED.test(fs.readFileSync(attr, 'utf8'))) continue;
    let file = shipped.get(hash(scan));
    if (!file) {
      file = `example-${m.id}.pdf`;
      fs.copyFileSync(scan, path.join(ASSETS, file));
    }
    out.push({ id: m.id, group, title: m.title, license: m.license, source: m.source_url || '', file, bytes: fs.statSync(scan).size });
  }
}
fs.writeFileSync(path.join(ASSETS, 'samples.json'), JSON.stringify(out, null, 1) + '\n');
console.log(`samples.json: ${out.length} examples, ${(out.reduce((a, s) => a + s.bytes, 0) / 1048576).toFixed(1)} MB`);
