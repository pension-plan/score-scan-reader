// node tools/headeval.js set/*.png : notehead recall/precision, pitch and part accuracy vs synthetic truth
const fs = require('fs');
const { readGray } = require('../src/image');
const { convert } = require('../src/omr');
(async () => {
  const tot = { t: 0, d: 0, m: 0, pitch: 0, part: 0, dur: 0 };
  for (const f of process.argv.slice(2)) {
    const truth = JSON.parse(fs.readFileSync(f.replace(/\.png$/, '.json')));
    const r = await convert([readGray(f)]);
    const pg = r.pages[0]; if (!pg) { console.log(f, 'no page'); continue; }
    const fr = pg.fr, sc = r.score;
    if (Math.abs(fr.skew.angle) >= 0.05 || fr.scale !== 1) { console.log(f, 'skipped (resampled/rotated frame)'); continue; }
    const used = new Set(); let m = 0, pitch = 0, part = 0, dur = 0;
    for (const t of truth.heads) {
      let best = null, bd = 1e9;
      for (const h of fr.heads) { const d = Math.hypot(h.x - t.c[0], h.y - t.c[1]); if (d < bd && !used.has(h)) { bd = d; best = h; } }
      if (!best || bd > 0.6 * fr.ss) continue;
      used.add(best); m++;
      if (best.pitch && best.pitch.step === t.pitch.step && best.pitch.octave === t.pitch.octave && (best.pitch.alter || 0) === (t.pitch.alter || 0)) pitch++;
      const names = (best.parts || []).map(i => sc.parts[i].name[0]);
      if (t.voices.every(v => names.includes(v)) && names.length === t.voices.length) part++;
      const q = best.dur ? best.dur.q : 0; if (Math.abs(q - Math.pow(2, 2 - t.durLog) * (t.dots ? 1.5 : 1)) < 1e-6) dur++;
    }
    console.log(f.split('/').pop(), 'truth', truth.heads.length, 'det', fr.heads.length, 'matched', m, 'pitch', pitch, 'part', part, 'dur', dur);
    tot.t += truth.heads.length; tot.d += fr.heads.length; tot.m += m; tot.pitch += pitch; tot.part += part; tot.dur += dur;
  }
  const pc = (a, b) => (100 * a / Math.max(1, b)).toFixed(1) + '%';
  console.log(`TOTAL recall ${pc(tot.m, tot.t)} precision ${pc(tot.m, tot.d)} pitch|matched ${pc(tot.pitch, tot.m)} part|matched ${pc(tot.part, tot.m)} dur|matched ${pc(tot.dur, tot.m)}`);
})();
