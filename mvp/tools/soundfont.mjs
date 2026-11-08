#!/usr/bin/env node
// Builds the player's sampled General MIDI subset (dist/assets/gm-*.json) from the
// FluidR3_GM renders in gleitz/midi-js-soundfonts (CC BY 3.0, see NOTICE.soundfont.txt).
// Every 3rd semitone of each instrument's useful range is kept (the player
// resamples the nearest one by playbackRate, at most a semitone away); each file is
// {name, program, notes: {"<midi>": "<base64 mp3>"}} and is fetched only when a part
// using it is played.
//   node tools/soundfont.mjs [--src <dir of *-mp3.js>]   (default: download to work/soundfont/)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MVP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(MVP, 'dist', 'assets');
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const SRC = arg('--src') || path.join(MVP, 'work', 'soundfont');
const BASE = 'https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/FluidR3_GM/';
// set name -> [gleitz instrument, GM program (0-based), lowest, highest MIDI note kept]
export const SETS = {
  piano: ['acoustic_grand_piano', 0, 21, 108],
  organ: ['church_organ', 19, 24, 96],
  choir: ['choir_aahs', 52, 36, 84],
  oohs: ['voice_oohs', 53, 36, 84],
  strings: ['string_ensemble_1', 48, 28, 100],
  flute: ['flute', 73, 59, 98],
  clarinet: ['clarinet', 71, 50, 91],
  brass: ['trumpet', 56, 40, 86],
};
const NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const noteName = (m) => NAMES[m % 12] + (Math.floor(m / 12) - 1);

fs.mkdirSync(SRC, { recursive: true });
let total = 0;
for (const [set, [inst, program, lo, hi]] of Object.entries(SETS)) {
  const f = path.join(SRC, `${inst}-mp3.js`);
  if (!fs.existsSync(f)) {
    const r = await fetch(BASE + `${inst}-mp3.js`);
    if (!r.ok) throw new Error(`${inst}: HTTP ${r.status}`);
    fs.writeFileSync(f, Buffer.from(await r.arrayBuffer()));
  }
  // the file is a script assigning an object literal: read its strings, never run it
  const text = fs.readFileSync(f, 'utf8');
  const all = new Map([...text.matchAll(/"([A-G]b?\d)":\s*"data:audio\/mp3;base64,([A-Za-z0-9+/=]+)"/g)].map((m) => [m[1], m[2]]));
  const notes = {};
  for (let m = lo; m <= hi; m += 3) {
    const b64 = all.get(noteName(m));
    if (!b64) throw new Error(`${inst}: no ${noteName(m)}`);
    notes[m] = b64;
  }
  const body = JSON.stringify({ name: inst, program, source: 'FluidR3_GM via gleitz/midi-js-soundfonts (CC BY 3.0)', notes });
  fs.writeFileSync(path.join(OUT, `gm-${set}.json`), body);
  total += body.length;
  console.log(`gm-${set}.json  ${Object.keys(notes).length} notes  ${(body.length / 1024).toFixed(0)} KB`);
}
console.log(`total ${(total / 1048576).toFixed(2)} MB`);
