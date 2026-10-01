"""Frame-level gates on the FINAL render: no blank frames, Instagram safe top, nothing under the captions.
Reel-agnostic: modes come from scenes.json (written by render.py), the render is renders/FINAL-*.mp4.

- blank: min per-frame std over the whole reel (a fully blank off-white frame reads ~0; a real cut reads > 4)
- safe top: rows 0..180 must be pure ground colour in every frame (Instagram trims/overlays the top)
- full-screen beats: the band under the cinematic words (y 1400..1920) must stay empty
"""
import json,subprocess,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
SJ=json.load(open(P/'scenes.json'));B=SJ['scenes'];FX=SJ.get('fx',[])   # fx = [start,end] windows where a full-frame effect is allowed everywhere
F=Path(sys.argv[1]) if len(sys.argv)>1 else sorted((P/'renders').glob('FINAL-*.mp4'),key=lambda p:p.stat().st_mtime)[-1]
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(F),'-vf','fps=30,scale=270:480','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
a=np.frombuffer(raw,np.uint8).reshape(-1,480,270,3).astype(np.int16);n=len(a)
sys.path.insert(0,str(P));from draw import BG as _BG                     # dark mode: the ground comes from draw.py, never a literal
BG=np.array([int(_BG[i:i+2],16) for i in (1,3,5)]);dist=np.abs(a-BG).max(axis=3)            # per-pixel distance from the ground colour
std=a.reshape(n,-1).std(axis=1);print(f'{F.name}: frames {n} | min frame std {std.min():.2f} at {std.argmin()/30:.2f}s'+('   <-- BLANK FRAME' if std.min()<3 else ''))
fx=np.zeros(n,bool)
for s_,e_ in FX:fx[round(s_*30):round(e_*30)]=True
top=dist[:,:45,:].max(axis=(1,2));top[fx]=0;bad=np.where(top>14)[0]
print(f'fx windows (full-frame effect allowed): {FX}')
print(f'safe top (y<180): {len(bad)} frames with ink'+(f', first at {bad[0]/30:.2f}s   <-- FIX' if len(bad) else ''))
for b in B:
    s,e=round(b['start']*30),round(b['end']*30)
    ink=np.where(dist[s:e].max(axis=0)>14);y0,y1=ink[0].min()*4,ink[0].max()*4;low=''
    if b.get('mode')=='full':
        keep=~fx[s:e];under=int(dist[s:e][keep][:,350:,:].max()) if keep.any() else 0;low=f' | under-caption band max dist {under}'+('   <-- something is drawn under the words' if under>14 else '')
    print(f"  {b['name']:9s} ink y {y0:4d}..{y1:4d}{low}")
