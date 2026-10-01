"""review/grid-<tag>.jpg: rows = beats, columns = evenly spaced times (top 1180 px of each frame)."""
import sys
from render import *
names=sys.argv[2].split(',');cols=int(sys.argv[3]) if len(sys.argv)>3 else 6
sheet=Image.new('RGB',(cols*324,len(names)*354),'#DDD')
for r,nm in enumerate(names):
    b=S[nm];dur=b['end']-b['start']
    for k in range(cols):
        lt=dur*(k+.5)/cols;t=b['start']+lt
        im=frame(round(t*30),person_at(t) if b['mode']=='split' else None)
        sheet.paste(im.crop((0,0,1080,1180)).resize((324,354)),(k*324,r*354))
sheet.save(P/f'review/grid-{sys.argv[1]}.jpg');print('ok')
