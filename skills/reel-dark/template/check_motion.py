"""Gate for rule 7: no graphics area held still for more than ~0.6 s inside a beat.
Reel-agnostic: modes come from scenes.json (written by render.py), the render is renders/FINAL-*.mp4.
Mean frame delta at 270 px under-reads small elements - a floor, not a substitute for reading the strips."""
import json,subprocess,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
B=json.load(open(P/'scenes.json'))['scenes'];SPLIT_Y=858
F=Path(sys.argv[1]) if len(sys.argv)>1 else sorted((P/'renders').glob('FINAL-*.mp4'),key=lambda p:p.stat().st_mtime)[-1]
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(F),'-vf','fps=30,scale=270:480','-f','rawvideo','-pix_fmt','gray','pipe:1'])
a=np.frombuffer(raw,np.uint8).reshape(-1,480,270).astype(np.int16);gy=round(SPLIT_Y*480/1920);worst=[]
for b in B:
    s,e=round(b['start']*30),round(b['end']*30)
    reg=a[s:e] if b.get('mode')=='full' else a[s:e,:gy]          # split scenes: only the graphics half
    d=np.abs(np.diff(reg,axis=0)).mean(axis=(1,2));run=0;mx=0;at_=0
    for i,v in enumerate(d):
        if v<0.08:
            run+=1
            if run>mx:mx=run;at_=i-run+1
        else:run=0
    worst.append((b['name'],round(mx/30,2),round(b['start']+at_/30,2)))
bad=[w for w in worst if w[1]>0.60]
for n,d,t in worst:print(f'  {n:10s} longest still run {d:5.2f}s'+(f'  at {t:.2f}s   <-- over 0.60' if d>0.60 else ''))
print(f'{F.name}: beats with a still run over 0.60 s: {len(bad)}')
