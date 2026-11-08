# python3 -I tools/score_cmp.py truth.musicxml ours.musicxml : per-part pitch-sequence accuracy
import sys, xml.etree.ElementTree as ET
def parts(f):
    r=ET.parse(f).getroot(); names={sp.get('id'):(sp.findtext('part-name') or '') for sp in r.iter('score-part')}
    out={}
    for p in r.iter('part'):
        seq=[];lyr=[]
        for n in p.iter('note'):
            if n.find('rest') is not None or n.find('chord') is not None: continue
            pt=n.find('pitch'); 
            if pt is None: continue
            seq.append(pt.findtext('step')+str(int(float(pt.findtext('alter') or 0)))+pt.findtext('octave'))
            l=n.find('lyric'); 
            if l is not None and l.findtext('text'): lyr.append(l.findtext('text').lower().strip(".,;:!?'’"))
        out[names[p.get('id')]]=(seq,lyr)
    return out
def ed(a,b):
    d=list(range(len(b)+1))
    for i in range(1,len(a)+1):
        prev=d[0]; d[0]=i
        for j in range(1,len(b)+1):
            cur=d[j]; d[j]=min(d[j]+1,d[j-1]+1,prev+(a[i-1]!=b[j-1])); prev=cur
    return d[-1]
T=parts(sys.argv[1]); O=parts(sys.argv[2])
for (tn,(ts,tl)),(on,(os_,ol)) in zip(T.items(),O.items()):
    e=ed(ts,os_); el=ed(tl,ol)
    print(f"{tn:10s} vs {on:10s} truth {len(ts):3d} ours {len(os_):3d} pitch-acc {max(0,1-e/max(1,len(ts))):.2f}  lyrics truth {len(tl)} ours {len(ol)} syl-acc {max(0,1-el/max(1,len(tl))):.2f}")
