// truth noteheads (LilyPond SVG boxes, by duration log) vs the front end's heads on clean pages:
// found / kind / stem, per duration
const fs = require('fs'), path = require('path');
const src = process.env.SRC || '/Users/d.sloane/music/mvp/src/';
const { readGray } = require(src + 'image.js'), { front } = require(src + 'front.js');
const C = '/Users/d.sloane/music/mvp/work/cache', B = '/Users/d.sloane/music/spike/opencv/data/boxes';
const stats = {}, miss = [];
for (const key of process.argv.slice(2)) {
  const boxes = JSON.parse(fs.readFileSync(path.join(B, key + '.json'), 'utf8'));
  boxes.pages.forEach((pg, p) => {
    const f = path.join(C, `coverage__${key}__clean__r200`, `p-${p + 1}.pgm`); if (!fs.existsSync(f)) return;
    const fr = front(readGray(f), { orient: false }), k0 = (200 / 300) * fr.scale;
    if (Math.abs(fr.skew.angle) >= 0.05) return;
    for (const s of pg.symbols.filter(s => s.cls === 'NoteHead')) {
      const dl = s.attrs.dlog; const b = s.box.map(v => v * k0), cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;
      if ((s.attrs.style || '') !== '' && s.attrs.style !== 'default') continue;
      const h = fr.heads.find(h => Math.abs(h.x - cx) < 0.6 * fr.ss && Math.abs(h.y - cy) < 0.5 * fr.ss);
      const st = (stats[dl] ||= { n: 0, found: 0, hollow: 0, stem0: 0 });
      st.n++; if (h) { st.found++; if (h.kind === 'hollow') st.hollow++; if (!h.stemDir) st.stem0++; } else if (dl === '0' && miss.length < 8) miss.push([key, p, Math.round(cx), Math.round(cy)]);
    }
  });
}
console.log(JSON.stringify(stats)); console.log('missed whole e.g.', JSON.stringify(miss));
