"""Cinematic captions for any language, right-to-left or left-to-right.
rtl=True: the whole line runs right-to-left, English words included (first spoken word on the right) - Arabic/Darija.
rtl=False: normal left-to-right.
Arabic words: SF Arabic (macOS) / Noto Sans Arabic, shaped with arabic_reshaper and drawn glyph-reversed.
Latin words: SF Pro (macOS) / Inter. Each word pops in on its own spoken onset (0.96 -> 1.0 over 3 frames), never re-animates."""
import math
from functools import lru_cache
import arabic_reshaper
from PIL import Image,ImageDraw,ImageFont
INK='#F5F5F7'
def is_ar(w):return any('؀'<=c<='ۿ' for c in w)
def shape(w):return arabic_reshaper.reshape(w)[::-1] if is_ar(w) else w
import sys as _sys,os as _os;_sys.path.insert(0,_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import fonts as _fonts   # SF Arabic / SF Pro on macOS, Noto Sans Arabic / Inter elsewhere
def font(size,ar=True,weight='Bold'):return _fonts.font('arabic' if ar else 'sans',int(size),weight)
def clean(w):return w.strip('.,،!?؟"')
def layout(words,size,maxw):
 while True:
  fs=[font(size*(.92 if not is_ar(w) else 1),is_ar(w)) for w in words]
  gap=size*.30;width=sum(f.getlength(shape(w)) for w,f in zip(words,fs))+gap*(len(words)-1)
  if width<=maxw or size<40:return fs,gap,width,size
  size-=3
def render_words(g,n,size=118,maxw=940,rtl=True):
 """g: {'words':[{'text','entry_frame'}], optional 'big','color','hl':{word:color}}. Returns RGBA, RTL."""
 words=[clean(w['text']) for w in g['words']];size=g.get('big',size)
 fs,gap,width,size=layout(words,size,maxw)
 asc=round(size*1.25);desc=round(size*.62);row=Image.new('RGBA',(math.ceil(width)+64,asc+desc+32))
 x=row.width-32 if rtl else 32
 for w,f,tm in zip(words,fs,g['words']):
  s=shape(w);ww=f.getlength(s);x=x-ww if rtl else x;age=n-tm['entry_frame']
  if age>=0:
   col=g.get('hl',{}).get(w,g.get('color',INK))
   tile=Image.new('RGBA',(math.ceil(ww)+40,row.height));ImageDraw.Draw(tile).text((20,16+asc),s,font=f,fill=col,anchor='ls')
   k=.96+.04*(1-(1-min(1,age/3))**3)
   if k!=1:
    o=tile.resize((round(tile.width*k),round(tile.height*k)),Image.Resampling.LANCZOS);row.alpha_composite(o,(round(x-20+(tile.width-o.width)/2),round((tile.height-o.height)/2)))
   else:row.alpha_composite(tile,(round(x-20),0))
  x=x-gap if rtl else x+ww+gap
 return row.crop(row.getbbox()) if row.getbbox() else row
def chip_text(words,size=46,maxw=960,rtl=True):
 """Presenter chip line (split beats): same RTL order, smaller, all words at once."""
 words=[clean(w) for w in words];fs,gap,width,size=layout(words,size,maxw)
 asc=round(size*1.25);desc=round(size*.62);row=Image.new('RGBA',(math.ceil(width)+8,asc+desc));x=row.width-4
 for w,f in zip(words,fs):
  s=shape(w);x-=f.getlength(s);ImageDraw.Draw(row).text((x,asc),s,font=f,fill='white',anchor='ls');x-=gap
 return row
