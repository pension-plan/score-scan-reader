const { readGray, writePNGrgb } = require('../src/image');
const { runOMR } = require('../src/pipeline');
const g = readGray(process.argv[2]);
const r = runOMR(g, JSON.parse(process.argv[4]||'{}'));
const W=g.width,H=g.height, rgb=new Uint8Array(W*H*3);
for(let i=0;i<W*H;i++){const v=g.data[i]*0.6+100; rgb[i*3]=rgb[i*3+1]=rgb[i*3+2]=v;}
const px=(x,y,c)=>{x=Math.round(x);y=Math.round(y);if(x<0||y<0||x>=W||y>=H)return;rgb.set(c,(y*W+x)*3)};
for(const st of r.staves) for(const l of st.lines) for(let i=1;i<l.length;i++){const [x0,y0]=l[i-1],[x1,y1]=l[i];for(let t=0;t<=1;t+=1/(x1-x0+1))px(x0+(x1-x0)*t,y0+(y1-y0)*t,[0,160,0]);}
for(const b of r.barlines) for(let y=b.y0;y<=b.y1;y++){px(b.x-1,y,[0,0,255]);px(b.x+1,y,[0,0,255]);}
for(const h of r.heads){const c=h.stem===1?[220,0,0]:h.stem===-1?[0,0,220]:[200,0,200];const R=r.staffSpace*0.6;for(let a=0;a<6.3;a+=0.05){px(h.x+R*Math.cos(a),h.y+R*Math.sin(a),c);px(h.x+(R+1)*Math.cos(a),h.y+(R+1)*Math.sin(a),c);} if(h.kind!=='filled')for(let d=-3;d<=3;d++)px(h.x+d,h.y,c);}
writePNGrgb(process.argv[3],W,H,rgb);
