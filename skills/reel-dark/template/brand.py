"""Brand tiles for dark-style scenes. Never draw person figures - use these.

- tile_app(name)      an official App Store icon filling the squircle (assets/icons/<name>.png; fetch more with the
                      iTunes Search API: itunes.apple.com/search?term=<app>&entity=software -> artworkUrl512)
- tile_icon(name)     white tile + a mark from assets/icons (lobehub / official PNGs)
- tile_fluent(name)   white tile + a Microsoft Fluent 3D emoji (assets/icons/fluent, MIT)
- tile_emoji(ch)      white tile + a colour emoji (Apple on macOS, Noto elsewhere);  emoji(ch) = the glyph alone (native 160 px)
- tile_q(size)        the unrevealed hero: dark tile with a white "?"
- tile_claude(size)   the Claude app tile;  tile_software(size) = a generic app-window glyph
Official icon sources, in order: the brand site's apple-touch-icon / rel="icon", the project's repo assets (redraw
the SVG with Pillow so it stays sharp), then lobehub icons-static-png on jsDelivr.
"""
from draw import *
import numpy as np
import fonts as _fonts

def _mask(im,size):
    im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel('A')),np.array(squircle_mask(size)))));return im

def _ring(im,size,color=(255,255,255,40)):
    """Hairline squircle ring (light, for the dark ground: dark tiles need it, white tiles keep it subtle)."""
    q=2;big=squircle_mask(size*q).resize((size,size),Image.Resampling.LANCZOS)
    inner=squircle_mask(size-4).resize((size-4,size-4));m=Image.new('L',(size,size));m.paste(inner,(2,2))
    edge=Image.fromarray(np.clip(np.array(big).astype(int)-np.array(m).astype(int),0,255).astype('uint8'))
    lay=Image.new('RGBA',(size,size),color);lay.putalpha(Image.fromarray((np.array(edge)*(color[3]/255)).astype('uint8')))
    im.alpha_composite(lay);return im




@lru_cache(None)
def tile_q(size):
    im=blank(size,size);ImageDraw.Draw(im).rectangle((0,0,size,size),fill='#2C2C2E')   # dark mode: raised grey, not ink
    f=sf(size*.66,'Heavy');ImageDraw.Draw(im).text((size/2,size/2),'?',font=f,fill='white',anchor='mm')
    return _ring(_mask(im,size),size,(255,255,255,56))

@lru_cache(None)
def tile_claude(size):return apptile('Claude',size)

@lru_cache(None)
def emoji(ch,size=160):
    """Colour emoji bitmap (Apple Color Emoji on macOS, Noto Color Emoji elsewhere). Rendered at the font's native
    strike (160 / 109 px) and resized to `size` - keep sizes at or below the native strike for crisp edges."""
    fp,native=_fonts.emoji_font();f=ImageFont.truetype(fp,native);im=blank(native*2,native*2);ImageDraw.Draw(im).text((native,native),ch,font=f,embedded_color=True,anchor='mm')
    bb=im.getbbox();im=im.crop(bb) if bb else im
    if size!=max(im.size):
        k=size/max(im.size);im=im.resize((max(1,round(im.width*k)),max(1,round(im.height*k))),Image.Resampling.LANCZOS)
    return im


@lru_cache(None)
def tile_emoji(ch,size,frac=.62,bg='white'):
    im=blank(size,size);ImageDraw.Draw(im).rectangle((0,0,size,size),fill=bg)
    e=emoji(ch,round(size*frac));im.alpha_composite(e,((size-e.width)//2,(size-e.height)//2))
    return _ring(_mask(im,size),size) if bg=='white' else _mask(im,size)


@lru_cache(None)
def tile_software(size,bg='white'):
    """Generic software: a little macOS window with traffic lights and three content lines."""
    im=blank(size,size);ImageDraw.Draw(im).rectangle((0,0,size,size),fill=bg);q=4;S=size*q;w=blank(S,S);d=ImageDraw.Draw(w)
    x0,y0,x1,y1=S*.16,S*.22,S*.84,S*.78;r=S*.06
    d.rounded_rectangle((x0,y0,x1,y1),radius=r,fill='#F4F4F6',outline='#C9C9CE',width=q*2)
    d.rounded_rectangle((x0,y0,x1,y0+S*.13),radius=r,fill='#E4E4E8');d.rectangle((x0,y0+S*.07,x1,y0+S*.13),fill='#E4E4E8')
    for i,c in enumerate(['#FF5F57','#FEBC2E','#28C840']):d.ellipse((x0+S*.04+i*S*.06,y0+S*.045,x0+S*.04+i*S*.06+S*.04,y0+S*.085),fill=c)
    for i in range(3):
        ln=(.44,.30,.38)[i];d.rounded_rectangle((x0+S*.07,y0+S*.21+i*S*.11,x0+S*.07+S*ln,y0+S*.21+i*S*.11+S*.05),radius=S*.025,fill='#B9B9C0' if i else '#8E8E93')
    im.alpha_composite(w.resize((size,size),Image.Resampling.LANCZOS))
    return _ring(_mask(im,size),size) if bg=='white' else _mask(im,size)


@lru_cache(None)
def tile_fluent(name,size,frac=.70):
    """White tile + a Microsoft Fluent 3D emoji figure (assets/icons/fluent/<name>.png, 256 px, MIT)."""
    im=blank(size,size);ImageDraw.Draw(im).rectangle((0,0,size,size),fill='white');k=round(size*frac)
    fig=Image.open(P/'assets/icons/fluent'/f'{name}.png').convert('RGBA').resize((k,k),Image.Resampling.LANCZOS)
    im.alpha_composite(fig,((size-k)//2,(size-k)//2+round(size*.03)));return _ring(_mask(im,size),size)


@lru_cache(None)
def tile_app(name,size):
    """An official App Store icon (assets/icons/<name>.png, 512 px) filling the squircle - Salesforce, Notion, Slack, HubSpot, Zoom, Dropbox..."""
    if name=='Notion':return tile_icon('Notion',size,.70)
    im=Image.open(P/'assets/icons'/f'{name}.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
    return _ring(_mask(im,size),size)


@lru_cache(None)
def tile_icon(name,size,frac=.66,bg='white'):
    """White tile + a mark from assets/icons (lobehub / official PNGs)."""
    im=blank(size,size);ImageDraw.Draw(im).rectangle((0,0,size,size),fill=bg);k=round(size*frac);im.alpha_composite(icon(name,k),((size-k)//2,(size-k)//2))
    return _ring(_mask(im,size),size)



def tracked(im,s,cx,y,n,color,gap,weight='Medium'):
    """Letter-spaced small caps on ONE baseline (anchor 'ls'); centred on cx, y is the baseline."""
    f=sf(n,weight);wd=sum(f.getlength(c) for c in s)+gap*(len(s)-1);x=cx-wd/2;d=ImageDraw.Draw(im)
    for c in s:
        d.text((x,y),c,font=f,fill=color,anchor='ls');x+=f.getlength(c)+gap
