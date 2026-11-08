// truth noteheads (by duration log) vs the duration the assembled page gives the matching head
const fs = require('fs'), path = require('path');
const src = process.env.SRC || '/Users/d.sloane/music/mvp/src/';
const { readGray } = require(src + 'image.js'), { front } = require(src + 'front.js'), { assemblePage } = require(src + 'assemble.js');
const C = '/Users/d.sloane/music/mvp/work/cache', B = '/Users/d.sloane/music/spike/opencv/data/boxes';
const variant = process.env.VAR || 'clean', want = (process.env.DLOG || '').split(',').filter(Boolean);
const stats = {};
for (const key of process.argv.slice(2)) {
  const boxes = JSON.parse(fs.readFileSync(path.join(B, key + '.json'), 'utf8'));
  boxes.pages.forEach((pg, p) => {
    const f = path.join(C, `coverage__${key}__${variant}__r200`, `p-${p + 1}.pgm`); if (!fs.existsSync(f)) return;
    const fr = front(readGray(f), { orient: false }); if (Math.abs(fr.skew.angle) >= 0.05 || fr.dewarped) return;
    const asm = assemblePage(fr, p), k0 = (200 / 300) * fr.scale;
    const heads = []; for (const sy of asm.systems) for (const s of sy.staves) for (const c of s.chords) for (const h of c.heads) heads.push(h);
    // by stem: LilyPond's Stem carries the note's duration log (NoteHead caps it at 2); the chord whose
    // stem column is that stem, its head nearest the stem's head end
    const chords = []; for (const sy of asm.systems) for (const st of sy.staves) for (const c of st.chords) chords.push(c);
    for (const s of pg.symbols.filter(s => s.cls === 'Stem')) {
      const dl = s.attrs.dlog; if (want.length && !want.includes(dl)) continue;
      const b = s.box.map(v => v * k0), sx = (b[0] + b[2]) / 2;
      const c = chords.find(c => [c.upX, c.downX].some(x => x >= 0 && Math.abs(x - sx) < 0.4 * fr.ss) && c.heads.some(h => h.y > b[1] - fr.ss && h.y < b[3] + fr.ss));
      const h = c && c.heads[0];
      const st = (stats[dl] ||= { n: 0, miss: 0, q: {}, kind: {} }); st.n++;
      if (!h) { st.miss++; continue; }
      const q = h.dur ? +(h.dur.q / (h.dur.dots ? 1.5 : 1)).toFixed(4) : 'none'; st.q[q] = (st.q[q] || 0) + 1; st.kind[h.kind] = (st.kind[h.kind] || 0) + 1;
    }
  });
}
for (const [dl, s] of Object.entries(stats).sort()) console.log('dlog', dl, 'n', s.n, 'missed', s.miss, 'q', JSON.stringify(s.q), 'kind', JSON.stringify(s.kind));
