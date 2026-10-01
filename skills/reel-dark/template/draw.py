"""Apple-styled drawing primitives: SF Pro type, macOS windows, squircle app icons.

DARK MODE: every reel renders on a near-black ground with Apple's dark-appearance colours.
Tokens: BG ground, CARD surface, CARD2 raised surface / controls, INK primary label (light), GRAY secondary label,
LINE separators, HAIR the 1 px light edge every dark card carries so it reads on the ground.
"""
from pathlib import Path
from functools import lru_cache
import math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parent
import sys as _sys;_sys.path.insert(0,str(P))
BG='#0A0A0B';CARD='#1C1C1E';CARD2='#2C2C2E';INK='#F5F5F7';GRAY='#98989D';LINE='#38383A';HAIR=(255,255,255,26)
BLUE='#0A84FF';GREEN='#30D158';RED='#FF453A';TERRA='#D97757';YELLOW='#FFD60A'
W,H=1080,1920
import fonts as _fonts   # Apple system fonts on macOS, bundled open fonts elsewhere (see fonts.py)
def sf(n,weight='Regular',mono=False):return _fonts.font('mono' if mono else 'sans',int(n),weight)
def ny(n,weight='Regular'):return _fonts.font('serif',int(n),weight)
def ease(v):return 1-(1-max(0,min(1,v)))**3
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def spring(v):
 v=max(0,min(1,v));return 1-math.exp(-6*v)*math.cos(7*v)*(1-v)**.5 if v<1 else 1
def lerp(a,b,v):return a+(b-a)*v
def blank(w,h):return Image.new('RGBA',(int(w),int(h)))
def _clear(c):return isinstance(c,tuple) and len(c)==4 and c[3]<255
def rr(im,box,fill='white',r=20,outline=None,width=1):
 box=tuple(round(v) for v in box)
 if (_clear(fill) or _clear(outline)) and im.mode=='RGBA':
  # translucent fill or edge (the dark-mode HAIR): blend over existing pixels instead of replacing their alpha
  lay=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(lay).rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width);im.alpha_composite(lay);return
 ImageDraw.Draw(im).rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
def txt(im,s,x,y,n=30,color=INK,center=False,weight='Regular',mono=False,font=None,tracking=0):
 d=ImageDraw.Draw(im);f=font or sf(n,weight,mono)
 if tracking:
  wtot=sum(f.getlength(c) for c in s)+tracking*(len(s)-1);cx=x-wtot/2 if center else x
  for c in s:
   b=d.textbbox((0,0),c,font=f);d.text((round(cx),round(y-b[1])),c,font=f,fill=color);cx+=f.getlength(c)+tracking
  return wtot
 b=d.textbbox((0,0),s,font=f);d.text((round(x-(b[2]-b[0])/2) if center else round(x),round(y-b[1])),s,font=f,fill=color);return b[2]-b[0]
def tw(s,n=30,weight='Regular',font=None):return (font or sf(n,weight)).getlength(s)
def line(im,points,color=LINE,width=2):ImageDraw.Draw(im).line(points,fill=color,width=width,joint='curve')
@lru_cache(None)
def icon(name,size):return Image.open(P/'assets/icons'/f'{name}.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
@lru_cache(None)
def squircle_mask(size):
 q=4;m=Image.new('L',(size*q,size*q));d=ImageDraw.Draw(m);n=5;r=size*q/2
 pts=[]
 for i in range(720):
  a=i/720*2*math.pi;c,s=math.cos(a),math.sin(a)
  pts.append((r+r*math.copysign(abs(c)**(2/n),c),r+r*math.copysign(abs(s)**(2/n),s)))
 d.polygon(pts,fill=255);return m.resize((size,size),Image.Resampling.LANCZOS)
@lru_cache(None)
def apptile(name,size):
 """macOS-style squircle app icon using the real brand mark."""
 spec={'Apple':('white','Apple',.62,None),'Notion':('white','Notion',.70,None),'Duolingo':(None,'Duolingo',1,None),'Claude':('#D97757','Claude',.62,'white'),'ChatGPT':('white','ChatGPT',.66,None)}
 bgc,ic,frac,tint=spec[name];im=blank(size,size)
 if bgc is None:ic_im=icon(ic,size);im.alpha_composite(ic_im);
 else:
  ImageDraw.Draw(im).rectangle((0,0,size,size),fill=bgc);k=round(size*frac);m=icon(ic,k)
  if tint:
   solid=Image.new('RGBA',m.size,tint);solid.putalpha(m.getchannel('A'));m=solid
  im.alpha_composite(m,((size-k)//2,(size-k)//2))
 im.putalpha(Image.fromarray(__import__('numpy').minimum(__import__('numpy').array(im.getchannel('A')),__import__('numpy').array(squircle_mask(size)))))
 # hairline for white tiles
 if bgc=='white':
  ring=blank(size,size);q=4;big=blank(size*q,size*q);d=ImageDraw.Draw(big)
  big.putalpha(squircle_mask(size*q).resize((size*q,size*q)) if False else big.getchannel('A'))
 return im
@lru_cache(maxsize=256)
def shadow(w,h,r=22,blur=22,alpha=110,dy=10):
 im=blank(w+120,h+120);rr(im,(60,60+dy,w+60,h+60+dy),(0,0,0,alpha),r);return im.filter(ImageFilter.GaussianBlur(blur))
def place(im,obj,x,y,scale=1,opacity=1,sh=False,rot=0):
 if opacity<=0:return
 w,h=obj.size
 if scale!=1:obj=obj.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.LANCZOS);x+=(w-obj.width)/2;y+=(h-obj.height)/2
 if rot:
  ow,oh=obj.size;obj=obj.rotate(rot,resample=Image.Resampling.BICUBIC,expand=True);x-=(obj.width-ow)/2;y-=(obj.height-oh)/2
 if sh:
  s=shadow(obj.width,obj.height).copy()
  if opacity<1:s.putalpha(s.getchannel('A').point(lambda a:int(a*opacity)))
  im.alpha_composite(s,(round(x)-60,round(y)-60))
 if opacity<1:obj=obj.copy();obj.putalpha(obj.getchannel('A').point(lambda a:int(a*opacity)))
 im.alpha_composite(obj,(round(x),round(y)))
def panel(w,h,fill=CARD,r=18,edge=HAIR):
 im=blank(w,h);rr(im,(0,0,w-1,h-1),fill,r)
 if edge:rr(im,(0,0,w-1,h-1),None,r,edge,2)
 return im
def window(w,h,url=None,title=None,fill='#1E1E1E',bar=52,r=16):
 """macOS Sonoma window in dark appearance: traffic lights, optional Safari-style address field."""
 p=blank(w,h);rr(p,(0,0,w-1,h-1),fill,r);rr(p,(0,0,w-1,bar+r),'#2A2A2C',r);ImageDraw.Draw(p).rectangle((0,bar-2,w-1,bar+r),fill=fill if url is None else fill)
 ImageDraw.Draw(p).rectangle((0,bar,w-1,bar),fill='#3A3A3C');rr(p,(0,0,w-1,h-1),None,r,HAIR,2)
 for i,c in enumerate(['#FF5F57','#FEBC2E','#28C840']):ImageDraw.Draw(p).ellipse((16+i*20,bar/2-6,28+i*20,bar/2+6),fill=c)
 if url:
  fw=min(w*.52,520);rr(p,(w/2-fw/2,9,w/2+fw/2,bar-9),'#3A3A3C',9)
  txt(p,'' if False else '',0,0,1)
  d=ImageDraw.Draw(p);lx=w/2-tw(url,15)/2-14;d.rounded_rectangle((lx-8,bar/2-6,lx,bar/2+3),2,outline='#98989D',width=1);d.arc((lx-7,bar/2-11,lx-1,bar/2-3),180,360,fill='#98989D',width=1)
  txt(p,url,w/2+4,bar/2-8,15,'#EBEBF5',True)
 if title:txt(p,title,w/2,bar/2-9,15,'#EBEBF5',True,'Semibold')
 return p
def pill(im,s,x,y,w,h,fill=BLUE,fg='white',n=17,weight='Medium',outline=None):
 rr(im,(x,y,x+w,y+h),fill,h/2,outline,1);txt(im,s,x+w/2,y+h/2-n*.58,n,fg,True,weight)
def reveal(s,t,d=.65):return s[:max(0,min(len(s),int(len(s)*t/d)))]
def enter(im,obj,x,y,t,delay=0,sh=True):
 e=ease((t-delay)/.30);place(im,obj,x,y+22*(1-e),.96+.04*e,e,sh)
def cursor_default():pass
def heart(size,fill=RED):
 q=4;im=blank(size*q,size*q);pts=[]
 for i in range(120):
  a=i/120*2*math.pi;xx=16*math.sin(a)**3;yy=13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a)
  pts.append((size*q/2+xx*size*q/36,size*q/2-yy*size*q/36+size*q*.04))
 ImageDraw.Draw(im).polygon(pts,fill=fill);return im.resize((size,size),Image.Resampling.LANCZOS)
def checkmark(im,x,y,r=12,color=GREEN):
 d=ImageDraw.Draw(im);d.ellipse((x-r,y-r,x+r,y+r),fill=color);line(im,[(x-r*.45,y),(x-r*.1,y+r*.35),(x+r*.48,y-r*.32)],'white',max(2,round(r*.2)))
_ac=Image.Image.alpha_composite
def _ac2(self,im,dest=(0,0),source=(0,0)):return _ac(self,im,tuple(int(round(v)) for v in dest),tuple(int(round(v)) for v in source))
Image.Image.alpha_composite=_ac2
