"""Dense frame strips across a transition: python3 strips.py <beat> <t0> <t1> [n=10] -> review/dense-<beat>-<t0>.jpg
Read these before shipping any hand/prop choreography: a snap between phases shows up as a jump between two adjacent frames."""
import sys,json
from render import *
name=sys.argv[1];t0=float(sys.argv[2]);t1=float(sys.argv[3]);n=int(sys.argv[4]) if len(sys.argv)>4 else 10
b=S[name];sheet=Image.new('RGB',(n*180,132),'#DDD')
for i in range(n):
    lt=t0+(t1-t0)*i/(n-1);fr=round((b['start']+lt)*30);im=frame(fr,person_at(fr/30) if b['mode']=='split' else None)
    sheet.paste(im.crop((0,150,1080,780)).resize((180,105)),(i*180,0))
out=P/f'review/dense-{name}-{t0:.2f}.jpg';sheet.save(out);print(out)
