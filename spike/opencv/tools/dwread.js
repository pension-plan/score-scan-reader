// analyse() with and without the dewarp reread: systems / measures per page
const path = require('path'), src = process.env.SRC || '/Users/d.sloane/music/spike/opencv/src-dw/';
const { readGray } = require(src + 'image.js'), { front } = require(src + 'front.js'), { assemblePage } = require(src + 'assemble.js'), cvm = require(src + 'cv.js');
for (const f of process.argv.slice(2)) {
  const fr = front(readGray(f)), asm = assemblePage(fr, 0);
  const show = (a) => a.systems.map(s => s.staves.length + 'st/' + s.measures.length + 'm').join(' ');
  process.env.DW_DEBUG = '1';
  const dw = cvm.dewarpReading(fr, asm, (g) => { const f2 = front(g, { preclean: false }); return f2.staves.length ? { fr: f2, asm: assemblePage(f2, 0) } : null; });
  console.log(path.basename(path.dirname(f)), path.basename(f), '| before', show(asm), '| after', dw ? show(dw.asm) : '(kept)');
}
