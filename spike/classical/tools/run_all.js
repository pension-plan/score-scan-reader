#!/usr/bin/env node
'use strict';
// Evaluate every image in data/set (or a glob filter) in parallel worker processes.
// usage: node tools/run_all.js <out.jsonl> [filterRegex] [--opts json] [-j N]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const args = process.argv.slice(2);
const out = args[0];
const filter = args[1] && !args[1].startsWith('-') ? new RegExp(args[1]) : null;
const opi = args.indexOf('--opts');
const ji = args.indexOf('-j');
const J = ji >= 0 ? +args[ji + 1] : 96;
const dir = path.join(__dirname, '..', 'data', 'set');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.png') && (!filter || filter.test(f))).sort();
const results = [];
let next = 0, running = 0;
const t0 = Date.now();
function launch() {
  while (running < J && next < files.length) {
    const f = files[next++];
    running++;
    const a = [path.join(__dirname, 'eval.js'), path.join(dir, f), path.join(dir, f.replace('.png', '.json'))];
    if (opi >= 0) a.push('--opts', args[opi + 1]);
    const p = spawn(process.execPath, a);
    let buf = '', err = '';
    p.stdout.on('data', d => { buf += d; });
    p.stderr.on('data', d => { err += d; });
    p.on('close', code => {
      running--;
      if (code === 0) results.push(buf.trim()); else console.error('FAIL', f, err.split('\n').slice(0, 4).join(' | '));
      if (next < files.length) launch();
      else if (running === 0) {
        fs.writeFileSync(out, results.join('\n') + '\n');
        console.error(`${results.length}/${files.length} images in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${out}`);
      }
    });
  }
}
launch();
