"""Antialiased, hotspot-anchored pointer with eased curved travel and click depression."""
from PIL import Image, ImageDraw, ImageFilter
from functools import lru_cache
import math

def clamp(v):return max(0.,min(1.,v))
def ease(v):
 v=clamp(v);return v*v*v*(v*(v*6-15)+10)

@lru_cache(None)
def pointer(scale100=100):
 q=6;s=scale100/100
 im=Image.new('RGBA',(60*q, 70*q));d=ImageDraw.Draw(im)
 pts=[(0,0),(0,34),(9,26),(16,40),(23,36),(16,23),(28,22)]
 pts=[((x*s+10)*q,(y*s+10)*q) for x,y in pts]
 d.polygon(pts,fill='#161719');d.line(pts+[pts[0]],fill='white',width=round(1.8*q),joint='curve')
 # Compact natural shadow, no oversized click rings.
 alpha=im.getchannel('A').filter(ImageFilter.GaussianBlur(1.3*q))
 sh=Image.new('RGBA',im.size,(0,0,0,0));sh.putalpha(alpha.point(lambda x:round(x*.20)))
 out=Image.new('RGBA',im.size);out.alpha_composite(sh,(0,2*q));out.alpha_composite(im)
 return out.resize((60,70),Image.Resampling.LANCZOS)

def position(t,points):
 if t<=points[0][0]:return points[0][1:]
 for (a,x0,y0),(b,x1,y1) in zip(points,points[1:]):
  if t<=b:
   u=ease((t-a)/max(.001,b-a));dx=x1-x0;dy=y1-y0;dist=math.hypot(dx,dy)
   bend=min(27,dist*.07)*math.sin(math.pi*u)
   return (x0+dx*u-(dy/dist*bend if dist else 0),y0+dy*u+(dx/dist*bend if dist else 0))
 return points[-1][1:]

def motion(im,t,points,clicks=(),end=None):
 start=points[0][0]
 if t<start or (end is not None and t>end):return
 x,y=position(t,points)
 age=min([t-c for c in clicks if t>=c],default=99)
 # Single mouse-down, short hold, smooth release. Hotspot never shifts.
 if age<.055:s=.90+.10*(1-ease(age/.055))
 elif age<.10:s=.90
 elif age<.23:s=.90+.10*ease((age-.10)/.13)
 else:s=1
 layer=pointer(round(s*100)).copy()
 opacity=min(clamp((t-start)/.08),clamp((end-t)/.14) if end is not None else 1)
 if opacity<1:layer.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
 im.alpha_composite(layer,(round(x)-10,round(y)-10))
