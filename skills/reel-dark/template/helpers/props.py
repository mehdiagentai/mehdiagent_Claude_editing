"""Generic props and helpers for dark-style scenes: gradients, rounded clipping, bezier curves, the scythe prop
(pivot PIV = grip point), and split_halves() to cut a card along a diagonal (slash effects)."""
from draw import *
import numpy as np
from PIL import ImageColor
def gradient(w,h,c1,c2,vertical=True):
 rgb=lambda c:ImageColor.getrgb(c)[:3] if isinstance(c,str) else tuple(c)[:3]
 a=np.array(rgb(c1),float);b=np.array(rgb(c2),float)
 t=np.linspace(0,1,h if vertical else w)
 arr=a[None,:]+(b-a)[None,:]*t[:,None]
 arr=np.repeat(arr[:,None,:],w,1) if vertical else np.repeat(arr[None,:,:],h,0)
 return Image.fromarray(arr.astype('uint8'),'RGB').convert('RGBA')
def clip(p,r=16):
 m=Image.new('L',p.size);ImageDraw.Draw(m).rounded_rectangle((0,0,p.width-1,p.height-1),r,fill=255)
 p.putalpha(Image.fromarray(np.minimum(np.array(p.getchannel('A')),np.array(m))));return p
def bezier(p0,p1,p2,n=40):return [((1-u)**2*p0[0]+2*(1-u)*u*p1[0]+u*u*p2[0],(1-u)**2*p0[1]+2*(1-u)*u*p1[1]+u*u*p2[1]) for u in np.linspace(0,1,n)]

@lru_cache(None)
def scythe():
 q=4;w,h=360,540;im=blank(w*q,h*q);d=ImageDraw.Draw(im)
 snath=[(150,530),(158,380),(172,200),(190,70)]
 sm=[(x*q,y*q) for x,y in snath];d.line(sm,fill='#5C3D22',width=15*q,joint='curve');d.line([(x-4*q,y) for x,y in sm],fill='#8C6239',width=5*q,joint='curve')
 d.line([(140*q,335*q),(112*q,352*q)],fill='#4A2F18',width=12*q);d.line([(178*q,178*q),(150*q,195*q)],fill='#4A2F18',width=12*q)
 outer=bezier((192,72),(60,30),(18,240),60);inner=bezier((18,240),(96,118),(190,104),60)
 poly=[(x*q,y*q) for x,y in outer+inner]
 d.polygon(poly,fill='#D8DBE0');d.line(poly+[poly[0]],fill='#6F757D',width=2*q,joint='curve')
 d.line([(x*q,y*q) for x,y in outer],fill='#F7F8FA',width=6*q,joint='curve')
 d.line([(x*q,y*q) for x,y in bezier((150,84),(95,122),(60,190),30)],fill='#B6BAC0',width=2*q,joint='curve')
 d.rounded_rectangle((178*q,62*q,206*q,112*q),6*q,fill='#26262A')
 return im.resize((w,h),Image.Resampling.LANCZOS)
PIV=(166,290)

def split_halves(card):
 w,h=card.size;out=[]
 for poly in [[(0,0),(w*.90,0),(w*.10,h),(0,h)],[(w*.90,0),(w,0),(w,h),(w*.10,h)]]:
  m=Image.new('L',card.size);ImageDraw.Draw(m).polygon(poly,fill=255);piece=card.copy();piece.putalpha(Image.fromarray(np.minimum(np.array(card.getchannel('A')),np.array(m))));out.append(piece)
 return out
