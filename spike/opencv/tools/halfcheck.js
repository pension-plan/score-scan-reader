// half-note stems (LilyPond Stem duration log 1) whose chord's head came out filled: positions
const fs = require('fs'), path = require('path');
const src = process.env.SRC || '/Users/d.sloane/music/mvp/src/';
const { readGray } = require(src + 'image.js'), { front } = require(src + 'front.js'), { assemblePage } = require(src + 'assemble.js');
const C = '/Users/d.sloane/music/mvp/work/cache', B = '/Users/d.sloane/music/spike/opencv/data/boxes';
let n = 0, filled = 0; const ex = [];
for (const key of process.argv.slice(2)) {
  const boxes = JSON.parse(fs.readFileSync(path.join(B, key + '.json'), 'utf8'));
  boxes.pages.forEach((pg, p) => {
    const f = path.join(C, `coverage__${key}__clean__r200`, `p-${p + 1}.pgm`); if (!fs.existsSync(f)) return;
    const fr = front(readGray(f), { orient: false }); if (Math.abs(fr.skew.angle) >= 0.05) return;
    const asm = assemblePage(fr, p), k0 = (200 / 300) * fr.scale;
    const chords = []; for (const sy of asm.systems) for (const st of sy.staves) for (const c of st.chords) chords.push(c);
    for (const s of pg.symbols.filter(s => s.cls === 'Stem' && s.attrs.dlog === '1')) {
      const b = s.box.map(v => v * k0), sx = (b[0] + b[2]) / 2;
      const c = chords.find(c => [c.upX, c.downX].some(x => x >= 0 && Math.abs(x - sx) < 0.4 * fr.ss) && c.heads.some(h => h.y > b[1] - fr.ss && h.y < b[3] + fr.ss));
      if (!c) continue; n++;
      const h = c.heads.find(h => h.kind === 'filled'); if (h) { filled++; if (ex.length < 12) ex.push([key, p, Math.round(h.x), Math.round(h.y), h.p, c.heads.length]); }
    }
  });
}
console.log('half chords', n, 'with a filled head', filled); console.log(JSON.stringify(ex));
