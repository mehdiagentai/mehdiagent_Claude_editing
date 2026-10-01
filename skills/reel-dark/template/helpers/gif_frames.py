"""GIF -> 30 fps JPEG frame folder for meme cards (see references/memes.md).

usage: python3 helpers/gif_frames.py IN.gif OUT_DIR [WIDTH]     # resamples the GIF's own frame durations to 30 fps
       python3 helpers/gif_frames.py IN.gif --peek               # writes IN-peek.jpg (frame ~10) to read before using it
"""
import sys
from pathlib import Path
from PIL import Image
src=Path(sys.argv[1]);im=Image.open(src);n=im.n_frames
if len(sys.argv)>2 and sys.argv[2]=='--peek':
    im.seek(min(10,n-1));out=src.with_name(src.stem+'-peek.jpg');im.convert('RGB').save(out);print(out,im.size,n,'frames');sys.exit()
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True);w=int(sys.argv[3]) if len(sys.argv)>3 else 900
frames=[];times=[];cum=0
for i in range(n):
    im.seek(i);d=(im.info.get('duration',70) or 70)/1000;frames.append(im.convert('RGB').copy());times.append(cum);cum+=d
N=int(cum*30);i=0
for f in range(N):
    tt=f/30
    while i+1<n and times[i+1]<=tt:i+=1
    fr=frames[i];h=round(fr.height*w/fr.width);fr.resize((w,h),Image.Resampling.LANCZOS).save(out/f'{f:03d}.jpg',quality=92)
print(f'{src.name}: {n} GIF frames, {cum:.2f}s -> {N} frames at 30 fps, {w}x{h} in {out}')
