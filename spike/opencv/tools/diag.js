// front-end diagnosis of one page: staves (extent, space, slope), systems, heads, skew
const path = require('path');
const src = process.env.SRC || path.join(__dirname, '../../../mvp/src');
const { readGray } = require(path.join(src, 'image.js'));
const { front } = require(path.join(src, 'front.js'));
const { assemblePage } = require(path.join(src, 'assemble.js'));
const fr = front(readGray(process.argv[2]));
console.log('size', fr.gray.width + 'x' + fr.gray.height, 'scale', fr.scale && fr.scale.toFixed(2), 'skew', JSON.stringify(fr.skew), 'ss', fr.ss.toFixed(2), 'lt', fr.lt.toFixed(2), 'mode', fr.mode, 'preclean', fr.gray.preclean || '-');
for (const st of fr.staves) {
  const sl = (st.yAt(0, st.right) - st.yAt(0, st.left)) / (st.right - st.left);
  const sp0 = (st.yAt(4, st.left) - st.yAt(0, st.left)) / 4, sp1 = (st.yAt(4, st.right) - st.yAt(0, st.right)) / 4;
  console.log(` staff ${st.index} sys ${st.system} x ${st.left}-${st.right} y0 ${st.yAt(0, st.left).toFixed(0)} space L ${sp0.toFixed(1)} R ${sp1.toFixed(1)} slope ${(sl * 100).toFixed(2)}% heads ${fr.heads.filter(h => h.staff === st.index).length}`);
}
const asm = assemblePage(fr, 0);
console.log('systems', asm.systems.length, asm.systems.map(s => s.staves.length + 'st/' + s.measures.length + 'm ' + s.staves.map(x => x.hdr.clef + (x.hdr.clefGuessed ? '?' : '')).join(',')).join(' | '));
