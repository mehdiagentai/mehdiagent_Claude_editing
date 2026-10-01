"""Instagram-style comment animation. Returns a transparent 900x430 Pillow image.
UI illustration only; no account action. Configure keyword, timings and viewer label.
"""
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(None)
def font(size):return ImageFont.truetype(str(ROOT/'assets/fonts/Inter.ttf'),size)
def text(im,s,x,y,size=30,color='#F5F5F5',center=False):
 d=ImageDraw.Draw(im);f=font(size);b=d.textbbox((0,0),s,font=f)
 d.text((x-(b[2]-b[0])/2 if center else x,y-b[1]),s,font=f,fill=color)
# Dark mode: Instagram's own dark comment sheet is the default in the reel-dark skill.
THEMES={'dark':dict(bg='#1F1F1F',edge=(255,255,255,26),text='#F5F5F5',sub='#A8A8A8',line='#363636',av='#3A3A3A',av_fg='#8E8E8E',
                    field='#3A3A3A',post='#0095F6',post_off='#1F4A6B'),
        'light':dict(bg='white',edge=None,text='#262626',sub='#8E8E8E',line='#EFEFEF',av='#DBDBDB',av_fg='white',
                     field='#DBDBDB',post='#0095F6',post_off='#B3DBF7')}
def avatar(im,x,y,r=25,c=THEMES['dark']):
 d=ImageDraw.Draw(im);d.ellipse((x-r,y-r,x+r,y+r),fill=c['av']);d.ellipse((x-r*.30,y-r*.58,x+r*.30,y+.02*r),fill=c['av_fg']);d.ellipse((x-r*.6,y+r*.1,x+r*.6,y+r*.86),fill=c['av_fg'])
def heart(im,x,y,size=25,color='#F5F5F5',fill=None):
 # Cubic-style sampled outline, no font/emoji dependency. fill= draws the liked (solid red) state.
 import math
 pts=[]
 for i in range(65):
  a=i/64*2*math.pi;xx=16*math.sin(a)**3;yy=13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a)
  pts.append((x+xx*size/32,y-yy*size/32))
 if fill:ImageDraw.Draw(im).polygon(pts,fill=fill)
 else:ImageDraw.Draw(im).line(pts,fill=color,width=2,joint='curve')
def render(t,keyword='GEMINI',viewer='you',type_start=.25,type_duration=.6,post_at=1.95,theme='dark',like_at=None):
 c=THEMES[theme];im=Image.new('RGBA',(900,430));d=ImageDraw.Draw(im)
 d.rounded_rectangle((0,0,899,429),radius=19,fill=c['bg'])
 if c['edge']:
  lay=Image.new('RGBA',im.size);ImageDraw.Draw(lay).rounded_rectangle((0,0,899,429),radius=19,outline=c['edge'],width=2);im.alpha_composite(lay)
 text(im,'Comments',450,34,34,c['text'],True)
 d.line([(43,36),(29,51),(43,66)],fill=c['text'],width=3,joint='curve')
 d.line([(1,97),(898,97)],fill=c['line'],width=2)
 posted=t>=post_at
 if posted:
  avatar(im,51,159,25,c);text(im,viewer,98,128,29,c['text']);text(im,keyword,98,168,52,c['text'])
  text(im,'1s',98,236,23,c['sub']);text(im,'Reply',143,236,23,c['sub'])
  liked=like_at is not None and t>=like_at
  if liked:
   import math;u=t-like_at;k=1+.35*math.sin(min(1,u/.22)*math.pi)
   heart(im,843,167,round(28*k),fill='#FF3040')
  else:heart(im,843,167,28,c['text'])
 else:
  text(im,'No comments yet.',450,165,35,c['text'],True)
  text(im,'Start the conversation.',450,221,27,c['sub'],True)
 d.line([(1,297),(898,297)],fill=c['line'],width=2)
 avatar(im,48,361,25,c)
 d.rounded_rectangle((91,319,869,402),radius=41,outline=c['field'],width=2)
 fraction=max(0,min(1,(t-type_start)/type_duration));typed=keyword[:int(len(keyword)*fraction)] if not posted else ''
 if typed:text(im,typed,121,338,44,c['text'])
 else:text(im,'Add a comment…',121,347,29,c['sub'])
 text(im,'Post',813,347,29,c['post'] if typed else c['post_off'],True)
 return im
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--time',type=float,default=1);ap.add_argument('--keyword',default='GEMINI');a=ap.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True);render(a.time,a.keyword).save(a.out)
