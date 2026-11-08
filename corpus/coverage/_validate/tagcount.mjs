#!/usr/bin/env node
// Tag counts of MusicXML files with the coverage harness's own tagger (tools/coverage.mjs extract()).
//   node tagcount.mjs file.musicxml [...]   -> JSON {file: {tag: count}} on stdout
// Counts: one per tagged <note> (main, grace and cue notes) plus one per tagged event (clef/key/time/
// directions/barlines/prints, per part); 'multi-page' = 1 when the file has a new-page print.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const { extract } = await import(path.join(ROOT, 'tools/coverage.mjs'));
const out = {};
for (const f of process.argv.slice(2)) {
  try {
    const S = extract(fs.readFileSync(f, 'utf8'));
    const c = {};
    for (const n of [...S.notes, ...S.graces, ...S.cues]) for (const t of n.tags) c[t] = (c[t] || 0) + 1;
    for (const e of S.events) for (const t of e.tags) c[t] = (c[t] || 0) + 1;
    if (S.pageBreaks.size) c['multi-page'] = 1;
    out[f] = c;
  } catch (e) { out[f] = { _error: String(e.message || e) }; }
}
process.stdout.write(JSON.stringify(out));
