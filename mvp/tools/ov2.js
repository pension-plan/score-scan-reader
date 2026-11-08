const { readGray, writePNGrgb } = require('../src/image');
const { front } = require('../src/front');
const g0 = readGray(process.argv[2]);
const t0=Date.now(); const r = front(g0); console.log('ms',Date.now()-t0,'ss',r.ss.toFixed(2),'scale',r.scale.toFixed(2),'staves',r.staves.length,'sys',JSON.stringify(r.systems),'heads',r.heads.length,'bars',r.barlines.length);
const g=r.gray, W=g.width,H=g.height, rgb=new Uint8Array(W*H*3);
for(let i=0;i<W*H;i++){const v=g.data[i]*0.6+100; rgb[i*3]=rgb[i*3+1]=rgb[i*3+2]=v;}
const px=(x,y,c)=>{x=Math.round(x);y=Math.round(y);if(x<0||y<0||x>=W||y>=H)return;rgb.set(c,(y*W+x)*3)};
for(const st of r.staves) for(let k=0;k<5;k++) for(let x=st.left;x<=st.right;x+=2) px(x,st.yAt(k,x),[0,170,0]);
for(const b of r.barlines) for(let y=b.top;y<=b.bot;y++){px(b.x-2,y,[0,120,255]);px(b.x+2,y,[0,120,255]);}
for(const b of r.beams) for(let x=b.x0;x<=b.x1;x++){px(x,b.y0,[255,140,0]);px(x,b.y1,[255,140,0]);}
for(const h of r.heads){const d=h.stem?h.stem.dir:0;const c=d===1?[220,0,0]:d===-1?[0,0,220]:d===2?[200,0,200]:[0,150,150];const R=h.sp*0.6;for(let a=0;a<6.3;a+=0.04){px(h.x+R*Math.cos(a),h.y+R*Math.sin(a),c);px(h.x+(R+1)*Math.cos(a),h.y+(R+1)*Math.sin(a),c);} if(h.kind!=='filled')for(let dd=-4;dd<=4;dd++)px(h.x+dd,h.y,c);}
writePNGrgb(process.argv[3],W,H,rgb);
if(process.argv[4]){const [a,b,c2,d]=process.argv[4].split(',').map(Number);require('child_process').execSync(`python3 -c "from PIL import Image; Image.open('${process.argv[3]}').crop((${a},${b},${c2},${d})).save('${process.argv[3]}')"`);}
