import { scoreItem } from '/Users/d.sloane/music/mvp/tools/eval.mjs';
import fs from 'node:fs';
import path from 'node:path';
const CH = '/Users/d.sloane/music/corpus/challenge';
let bad = 0, n = 0;
for (const c of fs.readdirSync(CH)) {
  const cd = path.join(CH, c);
  if (c.startsWith('_') || !fs.statSync(cd).isDirectory()) continue;
  for (const id of fs.readdirSync(cd)) {
    const t = path.join(cd, id, 'truth.musicxml');
    if (id.startsWith('_') || !fs.existsSync(t)) continue;
    const x = fs.readFileSync(t, 'utf8');
    const s = scoreItem(x, x); n++;
    const ok = [s.pitch, s.duration, s.rests, s.lyrics, s.parts].every(v => Math.abs(v - 1) < 1e-9);
    if (!ok) { bad++; console.log(c, id, s.pitch, s.duration, s.rests, s.lyrics, s.parts, JSON.stringify(s.parts_detail)); }
  }
}
console.log(`self-score: ${n} truths, ${bad} not perfect`);
