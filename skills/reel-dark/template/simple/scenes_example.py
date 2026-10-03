"""Example reel (Moroccan Darija, Arabic RTL captions): "stop agonising over which campaign to cut - Claude reads your Ads Manager data".
Dark mode. Every timestamp is local to the beat; landings come from at(beat, word). Recreated UI only.
The AI stays the "?" tile until "Claude" is spoken (claude beat), then flips to the real Claude tile (rule 19).
Demo account = the demo_brand setting. No numbers on screen except the spoken "3" (test beat).
HOOK NOTE: the scythe hook fits THIS video's opening ("...whether to cut a campaign"). Never reuse it by default:
design each reel's hook from its own opening line (~/.claude/skills/mehdiagent/references/hooks.md)."""
from draw import *
import sys,numpy as np
sys.path.insert(0,str(P/'helpers'))
from pointer_motion import motion
import instagram_comment as ig
from brand import tile_q,tile_fluent,tile_icon,emoji,_ring,_mask
from props import scythe,PIV,split_halves,gradient,clip
META='#0866FF'
import json as _j,os as _o
try:_CFG=_j.load(open(_o.path.expanduser('~/.mehdiagent/config.json')))
except Exception:_CFG={}
CREATOR=(_CFG.get('creator_name') or 'creator').lower();DEMO=_CFG.get('demo_brand') or 'mehdiagent.com'
def clamp(v):return max(0,min(1,v))

# ---------------------------------------------------------------- shared pieces
def card(w=940,h=620):return panel(w,h,CARD,26)
def put_card(im,c,t,x=70,y=104,t0=0):
 e=spring(clamp((t-t0)/.34));place(im,c,x,y+30*(1-e),.97+.03*e,min(1,e*1.6),True)
@lru_cache(None)
def claude_tile(size):return _ring(apptile('Claude',size),size)
@lru_cache(None)
def meta_tile(size):return tile_icon('lobe-meta-color',size,.68)
@lru_cache(None)
def fluent(name,size):return Image.open(P/'assets/icons/fluent'/f'{name}.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
@lru_cache(None)
def ig_tile(size):
 im=Image.open(P/'assets/icons/Instagram.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS);return _ring(_mask(im,size),size)
def sweep(c,t,t0=0,speed=560,band=170,alpha=60):
 """Soft diagonal light band gliding across a card (keeps a waiting surface alive)."""
 if t<t0:return
 w,h=c.size;x=((t-t0)*speed)%(w+band*2+h)-band-h;lay=blank(w,h)
 ImageDraw.Draw(lay).polygon([(x,0),(x+band,0),(x+band+h*.6,h),(x+h*.6,h)],fill=(255,255,255,alpha));lay=lay.filter(ImageFilter.GaussianBlur(18))
 lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel('A')),np.array(c.getchannel('A')))));c.alpha_composite(lay)
def drop(t,t_land,h=420):
 """Free fall landing exactly on t_land (g=2600); returns (dy, squash) - dy<0 above the rest position."""
 g=2600;fall=math.sqrt(2*h/g);u=t-(t_land-fall)
 if u<0:return -h,1,0
 if u<fall:return -h+.5*g*u*u,1,1
 v=u-fall;return 0,1-.16*math.exp(-v/.1)*math.cos(28*v),1
def toggle(im,x,y,on,w=64,h=36):
 col=tuple(round(lerp(a,b,on)) for a,b in zip((72,72,74),(8,102,255)))
 rr(im,(x,y,x+w,y+h),col,h/2);k=h-8;cx=x+4+(w-8-k)*on;ImageDraw.Draw(im).ellipse((cx,y+4,cx+k,y+4+k),fill='white')
def spark(w,h,up,prog=1,col=None):
 col=col or (GREEN if up else RED);im=blank(w*2,h*2);pts=[]
 ys=[.70,.62,.66,.48,.52,.34,.38,.18] if up else [.22,.30,.26,.44,.40,.58,.62,.82]
 for i,v in enumerate(ys):pts.append((i/(len(ys)-1)*w*2,v*h*2))
 n=max(2,round(len(pts)*clamp(prog)));ImageDraw.Draw(im).line(pts[:n],fill=col,width=7,joint='curve')
 return im.resize((w,h),Image.Resampling.LANCZOS)
def tile_drop(im,tile,cx,ybase,t,t_land,h=420,fade_in=True):
 dy,sq,vis=drop(t,t_land,h)
 if not vis:return
 sw,shh=tile.size;tt=tile.resize((round(sw*(2-sq)),round(shh*sq)),Image.Resampling.LANCZOS) if sq!=1 else tile
 place(im,tt,cx-tt.width/2,ybase-tt.height+dy,sh=True)
def flip(size,t,t_name,dur=.22):
 """'?' tile until the name, horizontal flip ending exactly on it, Claude tile after."""
 u=(t-(t_name-dur))/dur
 if u<=0:return tile_q(size)
 if u>=1:return claude_tile(size)
 k=abs(math.cos(math.pi*u));src=tile_q(size) if u<.5 else claude_tile(size)
 out=blank(size,size);s=src.resize((max(1,round(size*k)),size),Image.Resampling.LANCZOS);out.alpha_composite(s,((size-s.width)//2,0));return out

# ---------------------------------------------------------------- 1. hook (full): the "?" reaps the losing campaigns
@lru_cache(None)
def reaper_q(angle,tilt=0,size=170):
 c=blank(1120,1120);s=scythe();sc=1.32;s=s.resize((round(s.width*sc),round(s.height*sc)),Image.Resampling.LANCZOS);c.alpha_composite(s,(560-round(PIV[0]*sc),560-round(PIV[1]*sc)))
 c=c.rotate(angle,resample=Image.Resampling.BICUBIC,center=(560,560));ic=tile_q(size)
 if tilt:ic=ic.rotate(tilt,resample=Image.Resampling.BICUBIC,expand=True)
 c.alpha_composite(shadow(ic.width,ic.height,r=size*.22,blur=14,alpha=120,dy=8),(560-ic.width//2-60,560-ic.height//2-60))
 c.alpha_composite(ic,(560-ic.width//2,560-ic.height//2));return c
CAMPS=[('Summer Sale',False),('Retargeting',True),('Broad Audience',False)]
@lru_cache(None)
def camp_card(k,prog10=10,on10=10,glow=0):
 name,up=CAMPS[k];w,h=860,196;c=panel(w,h,CARD,24)
 c.alpha_composite(meta_tile(84),(30,56));ImageDraw.Draw(c).text((136,h/2),name,font=sf(42,'Semibold'),fill=INK,anchor='lm')
 sp=spark(200,96,up,prog10/10);c.alpha_composite(sp,(470,50))
 r=26;cx,cy=712,98;ImageDraw.Draw(c).ellipse((cx-r,cy-r,cx+r,cy+r),fill=(48,209,88,60) if up else (255,69,58,60))
 d=ImageDraw.Draw(c);col=GREEN if up else RED
 d.polygon([(cx,cy-12),(cx-12,cy+8),(cx+12,cy+8)] if up else [(cx,cy+12),(cx-12,cy-8),(cx+12,cy-8)],fill=col)
 toggle(c,w-70-6,h/2-18,on10/10,58,34)
 if glow:rr(c,(1,1,w-2,h-2),None,24,(48,209,88,round(255*glow)),5)
 return c
def hook(t,S,at):
 im=Image.new('RGBA',(W,H),BG);x0=110;ys=[260,490,720];cw,ch=860,196
 s1=at('hook','تقطع',2.44);s2=max(s1+.55,at('hook','ولا',3.28)-.05);ts={0:s1,2:s2};tl=at('hook','لا.',3.52);tw=at('hook','تفكر',1.18)
 for k in range(3):
  e=spring(clamp((t+.12-k*.10)/.36));prog=round(10*clamp((t-.15-k*.1)/.6));a=t-ts.get(k,99)
  glow=.8*math.exp(-max(0,t-tl)/.35) if (k==1 and t>=tl-.05) else 0
  c=camp_card(k,prog,10,round(glow,1))
  if a<0:place(im,c,x0+60*(1-e)*(1 if k%2 else -1),ys[k],scale=.97+.03*e,opacity=min(1,e*1.5),sh=True)
  elif a<.9:
   L,R=split_halves(c);f=ease(a/.5);g=a*a*1500;op=max(0,1-a/.7)
   place(im,R,x0+120*f,ys[k]-60*f+g*.8,opacity=op,rot=-9*f);place(im,L,x0-90*f,ys[k]+30*f+g,opacity=op,rot=7*f)
  if k==1 and t>=tl:   # the survivor hops on "la" (= keep this one)
   pass
  if 0<=a<.2:
   lay=blank(W,H);p0=(x0+cw*.94,ys[k]-30);p1=(x0+cw*.06,ys[k]+ch+30)
   ImageDraw.Draw(lay).line([p0,p1],fill=(217,119,87,int(235*(1-a/.2))),width=26);im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
   ImageDraw.Draw(im).line([p0,p1],fill=(255,255,255,int(255*(1-a/.2))),width=6)
 # reaper route: in from top-left, scans the cards while he says "think", then reaps card 0 and card 2
 A0=(x0+cw-40,ys[0]-40);A2=(x0+cw-40,ys[2]-40)
 route=[(-.2,1240,ys[1]),(.55,860,ys[0]+20),(tw,820,ys[1]-10),(tw+.55,860,ys[2]-60),(s1-.30,A0[0],A0[1]),(s1+.10,A0[0]-90,A0[1]+120),
        (s2-.24,A2[0],A2[1]),(s2+.10,A2[0]-90,A2[1]+120),(s2+.6,860,ys[1]-40)]
 if t<=route[0][0]:px,py=route[0][1:]
 else:
  px,py=route[-1][1:]
  for (a0,xa,ya),(b0,xb,yb) in zip(route,route[1:]):
   if t<=b0:u=smooth((t-a0)/(b0-a0));px,py=lerp(xa,xb,u),lerp(ya,yb,u);break
 ang=70;tilt=-14+8*math.sin(t*7)*(1 if tw<=t<s1-.3 else 0)
 for s in (s1,s2):
  u=(t-(s-.16))/.24
  if 0<=u<1:ang=lerp(70,-80,smooth(u));tilt=lerp(-14,12,smooth(u))
  elif s+.08<=t<s+.5:v=smooth((t-s-.08)/.35);ang=lerp(-80,70,v);tilt=lerp(12,-14,v)
 place(im,reaper_q(round(ang),round(tilt),170),px-560,py-560+4*math.sin(t*5))
 return im

# ---------------------------------------------------------------- 2. pain (split): people stuck in Business Manager
@lru_cache(None)
def bm_window(w=700,h=330):
 p=window(w,h,title=None);d=ImageDraw.Draw(p);p.alpha_composite(meta_tile(30),(80,11));txt(p,'Business Manager',120,15,20,'#EBEBF5',weight='Semibold')
 rr(p,(0,52,170,h-2),'#232325',0);[rr(p,(22,80+i*44,22+(110,90,124,80,100)[i],96+i*44),'#3A3A3C',8) for i in range(5)]
 for i in range(5):
  y=84+i*48;rr(p,(196,y,w-30,y+34),'#2A2A2C',8);rr(p,(212,y+11,212+(180,140,210,160,120)[i],y+23),'#48484A',6);rr(p,(w-150,y+11,w-60,y+23),'#48484A',6)
 return clip(p,16)
def pain(t,S,at):
 im=Image.new('RGBA',(W,H),BG);c=card();cw,ch=c.size
 t1=at('pain','media',.64)-.13;t2=at('pain','owners',1.86)-.13;tl=at('pain','كيضيعو',2.24);tb=at('pain','Business',3.73)
 # Business Manager window rises behind the people on "Business"
 eb=spring(clamp((t-tb+.12)/.4))
 if eb>0:place(c,bm_window(),120,40+60*(1-eb),.94+.06*eb,min(1,eb*1.5),True)
 down=smooth(clamp((t-tb+.12)/.4))
 slide=smooth(clamp((t-t2+.1)/.3))
 for k,(name,tland) in enumerate([('technologist',t1),('man_in_tuxedo',t2)]):
  if t<tland-.6:continue
  size=round(lerp(200,150,down));cx=lerp(470,300,slide) if k==0 else 640;ybase=lerp(470,590,down)
  tile_drop(c,tile_fluent(name,size),cx,ybase,t,tland+.13,380)
 # hourglass flips while time is wasted
 if t>=tl-.13:
  e=spring(clamp((t-tl+.13)/.3));ph=(t-tl)/.55;rot=180*(math.floor(ph)+smooth(ph%1))
  hg=fluent('hourglass',round(150*max(.05,e)));hx=lerp(470,800,down);hy=lerp(130,110,down)
  place(c,hg,hx-hg.width/2,hy-hg.height/2,rot=-rot)
 put_card(im,c,t);return im

# ---------------------------------------------------------------- 3. read (full): the Ads Manager wall of columns
COLS=['Campaign','Delivery','Results','Reach','Impressions','Cost per result','Amount spent','CPM','CTR','CPC','ROAS','Frequency']
@lru_cache(None)
def ads_table():
 cwid=[340,150,140,140,170,190,180,120,120,120,120,150];w=sum(cwid)+40;h=640;p=blank(w,h);rr(p,(0,0,w-1,h-1),'#1E1E1E',0)
 d=ImageDraw.Draw(p);x=20;rows=['Summer Sale','Retargeting','Broad Audience','Lookalike 2%','Ramadan Promo','New Arrivals','Video Views']
 rng=np.random.default_rng(4)
 for j,(cn,cw_) in enumerate(zip(COLS,cwid)):
  txt(p,cn,x+14,22,21,'#EBEBF5',weight='Semibold');d.line([(x,0),(x,h)],fill='#2C2C2E',width=1)
  for i,r in enumerate(rows):
   y=72+i*80
   if j==0:txt(p,r,x+14,y+26,24,INK,weight='Medium')
   elif j==1:d.ellipse((x+16,y+32,x+28,y+44),fill=GREEN if i%3!=2 else '#8E8E93');rr(p,(x+38,y+30,x+38+70,y+46),'#3A3A3C',8)
   else:ww=int(rng.integers(40,cw_-40));rr(p,(x+cw_-20-ww,y+30,x+cw_-20,y+46),'#48484A',8)
  x+=cw_
 for i in range(8):d.line([(0,62+i*80),(w,62+i*80)],fill='#2C2C2E',width=1)
 return p,cwid
def read(t,S,at):
 im=Image.new('RGBA',(W,H),BG);tq=at('read','يقراو',.22);tf=at('read','ويفهمو',.68);td=at('read','data',1.16);tc=at('read','campaigns',1.60)
 w,h=940,760;win=window(w,h,title=None);win.alpha_composite(meta_tile(30),(80,11));txt(win,'Ads Manager',120,15,20,'#EBEBF5',weight='Semibold')
 for i,tb in enumerate(['Campaigns','Ad sets','Ads']):
  x=30+i*170;txt(win,tb,x,74,22,INK if i==0 else GRAY,weight='Semibold' if i==0 else 'Regular')
  if i==0:rr(win,(x,108,x+tw(tb,22,'Semibold'),112),META,2)
 tab,cwid=ads_table();pan=smooth(clamp((t-tq)/1.3))*(tab.width-w+20)
 view=tab.crop((round(pan),0,round(pan)+w-4,640));win.alpha_composite(view,(2,118))
 lay=blank(w,h)
 if t>=td-.05:   # column highlight sweeps on "data"
  u=clamp((t-td+.05)/.5);x=2-pan+sum(cwid[:8])+20;rr(lay,(x,118,x+sum(cwid[8:11]),118+(640)*u),(10,132,255,40),6)
 if t>=tc-.05:   # rows light up one after another on "campaigns"
  for i in range(7):
   a=t-(tc-.05+i*.06)
   if a>0:rr(lay,(6,118+62+i*80,w-6,118+62+i*80+78),(255,214,10,round(46*min(1,a/.12))),6)
 win.alpha_composite(lay);win=clip(win,16)
 e=spring(clamp((t+.1)/.36));place(im,win,70,110+30*(1-e),.97+.03*e,min(1,e*1.5),True)
 if t>=tf-.13:   # the 🤔 pops while he says "understand"
  e2=spring(clamp((t-tf+.13)/.3));th=think(160);rock=7*math.sin((t-tf)*5.2)
  place(im,th,800-th.width/2,700-th.height/2,max(.05,min(1.08,e2)),min(1,e2*2),False,rot=rock)
 return im
@lru_cache(None)
def think(size):
 """The system 🤔 (Apple / Noto colour emoji at the native strike)."""
 return emoji('🤔',min(size,160))

# ---------------------------------------------------------------- 4. saves (split): the AI wins back time and money
def saves(t,S,at):
 im=Image.new('RGBA',(W,H),BG);c=card();ta=at('saves','AI',.63);tk=at('saves','كيربحني',1.07);tb=at('saves','بزاف',1.57)
 tt=at('saves','الوقت',2.02);tm=at('saves','والفلوس.',2.24)
 hop=math.sin(clamp((t-tk)/.3)*math.pi)*36
 tile_drop(c,tile_q(210),470,420-hop,t,ta,460)
 if t>=tb-.13:     # money bag on the right, bills stream from the tile into it
  e=spring(clamp((t-tb+.13)/.3));bag=fluent('money_bag',round(190*max(.05,e)));pulse=1+.12*math.sin(clamp((t-tm)/.25)*math.pi) if t>=tm else 1
  place(c,bag,780-bag.width/2,330-bag.height/2,pulse)
  for k in range(12):
   a=t-(tb+.05+k*.11)
   if 0<a<.5:
    u=a/.5;x=lerp(560,760,u);y=lerp(300,300,u)-170*math.sin(u*math.pi);b=emoji('💵',70)
    place(c,b,x-35,y-35,rot=-40*u+20,opacity=min(1,(1-u)*3))
 if t>=tt-.13:     # hourglass on the left runs backwards
  e=spring(clamp((t-tt+.13)/.3));rot=-200*smooth(clamp((t-tt)/.35))
  hg=fluent('hourglass',round(170*max(.05,e)));place(c,hg,160-hg.width/2,320-hg.height/2,rot=rot)
 put_card(im,c,t);return im

# ---------------------------------------------------------------- 5. decision (full): A/B creatives, the AI picks
@lru_cache(None)
def ad_card(k,w=360,h=500):
 c=panel(w,h,'#000000',22);d=ImageDraw.Draw(c);d.ellipse((18,18,62,62),fill=(TERRA,'#0A84FF')[k]);txt(c,DEMO[:1].upper(),40,26,24,'white',True,'Bold')
 txt(c,DEMO.lower(),74,20,21,'#F5F5F5',weight='Semibold');txt(c,'Sponsored',74,46,17,'#A8A8A8')
 g=gradient(w,300,('#7B4BD6','#0E7C86')[k],('#E36AA0','#3DD6B0')[k]);c.alpha_composite(clip(g,0),(0,80))
 rr(c,(w/2-70,160,w/2+70,300),(255,255,255,235),30);txt(c,DEMO[:1].upper(),w/2,186,72,('#7B4BD6','#0E7C86')[k],True,'Heavy')
 rr(c,(0,380,w,430),'#262626',0);txt(c,'Shop now',20,394,20,'#F5F5F5',weight='Semibold');txt(c,'›',w-30,390,26,'#F5F5F5')
 for i in range(2):rr(c,(20,446+i*24,20+(260,180)[i],460+i*24),'#3A3A3C',6)
 return c
def decision(t,S,at):
 im=Image.new('RGBA',(W,H),BG);tk=at('decision','كيخليني',.40);tb=at('decision','أحسن',1.16);td=at('decision','decision',1.50)
 tq=at('decision','أقصر',2.44);tw_=at('decision','وقت.',2.78)
 xs=[130,590];y0=260;off=smooth(clamp((t-td+.05)/.3))
 for k in range(2):
  e=spring(clamp((t+.1-k*.08)/.36));c=ad_card(k).copy()
  if k==1 and t>=tb-.1:
   g=spring(clamp((t-tb+.1)/.3));rr(c,(2,2,c.width-3,c.height-3),None,22,(48,209,88,round(255*min(1,g))),6)
  op=min(1,e*1.5)*(1-.6*off if k==0 else 1);place(im,c,xs[k],y0+30*(1-e)+(26*off if k==0 else 0),.97+.03*e,op,True)
  tg=blank(120,60);toggle(tg,10,10,1-off if k==0 else 1,80,42);place(im,tg,xs[k]+120,y0+520+(26*off if k==0 else 0),opacity=op)
 # budget bar: the split slides to the winner after the decision
 sp=lerp(.5,.06,smooth(clamp((t-td)/.6)));bx,by,bw=130,875,820
 rr(im,(bx,by,bx+bw,by+20),'#2C2C2E',10);rr(im,(bx,by,bx+bw*sp,by+20),'#636366',10);rr(im,(bx+bw*sp+6,by,bx+bw,by+20),GREEN,10)
 # the ? tile scans both cards, then sits over the winner
 hx=470+250*math.sin((t-tk)*5) if tk<=t<tb else (lerp(470,770,smooth(clamp((t-tb)/.25))) if t>=tb else 470)
 hy=200+6*math.sin(t*4);ti=tile_q(130);place(im,ti,hx-65,hy-65,sh=True)
 if tk<=t<tb:   # scan beam
  lay=blank(W,H);ImageDraw.Draw(lay).polygon([(hx-20,hy+60),(hx+20,hy+60),(hx+140,y0+480),(hx-140,y0+480)],fill=(10,132,255,40));im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
 if t>=tq-.13:   # stopwatch: a fast lap on "shortest time"
  e=spring(clamp((t-tq+.13)/.3));sw=fluent('stopwatch',round(150*max(.05,e)));sh_=6*math.sin((t-tw_)*40)*max(0,1-(t-tw_)/.3) if t>=tw_ else 0
  place(im,sw,250-sw.width/2+sh_,200-sw.height/2,rot=sh_*2)
 return im

# ---------------------------------------------------------------- 6. data (split): metrics fly into the tile
CHIPS=['CPM','CTR','CPC','ROAS','Reach','Frequency','Amount spent','Results']
def data(t,S,at):
 im=Image.new('RGBA',(W,H),BG);c=card();tg=at('data','كيجمع',.98);td=at('data','data.',1.46)
 cx,cy=470,330;pulse=1+.14*math.sin(clamp((t-td)/.28)*math.pi) if t>=td else 1
 for i,ch in enumerate(CHIPS):
  ang=-math.pi/2+i*2*math.pi/len(CHIPS);r=290;x0,y0=cx+math.cos(ang)*r*1.25,cy+math.sin(ang)*r*.82
  e=spring(clamp((t-.02-i*.05)/.3));go=smooth(clamp((t-(tg-.1+i*.06))/.3))
  if go>=1:continue
  x,y=lerp(x0,cx,go),lerp(y0,cy,go);wd=tw(ch,26,'Semibold')+44;p=blank(round(wd),54);rr(p,(0,0,wd-1,53),CARD2,27);rr(p,(0,0,wd-1,53),None,27,HAIR,2)
  txt(p,ch,wd/2,12,26,INK,True,'Semibold');place(c,p,x-wd/2,y-27+4*math.sin(t*3+i),max(.05,min(1,e))*(1-.6*go),min(1,e*2)*(1-go*.5))
 ti=tile_q(190);place(c,ti,cx-95,cy-95,pulse*(1+.04*sum(1 for i in range(len(CHIPS)) if t>=tg+.2+i*.06)/len(CHIPS)),sh=True)
 if t>=td-.1:
  e=spring(clamp((t-td+.1)/.3));bc=fluent('bar_chart',round(120*max(.05,e)));place(c,bc,cx+80,cy-190,opacity=min(1,e*2))
 put_card(im,c,t);return im

# ---------------------------------------------------------------- 7. test (full): a 3-day A/B test, the AI reads it fast
DAYS=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
def test(t,S,at):
 im=Image.new('RGBA',(W,H),BG);tt=at('test','test',1.02);t3=at('test','تلت',1.42);ty=at('test','يام،',1.60);ts=at('test','سريع.',2.52)
 # A/B test header card
 e=spring(clamp((t+.12)/.36));hc=panel(940,190,CARD,24);txt(hc,'A/B test',40,34,34,INK,weight='Semibold')
 for k,(lab,col) in enumerate([('A',TERRA),('B',BLUE)]):
  x=40+k*230;rr(hc,(x,100,x+200,160),CARD2,18);ImageDraw.Draw(hc).ellipse((x+16,112,x+52,148),fill=col);txt(hc,lab,x+34,116,22,'white',True,'Bold')
  rr(hc,(x+66,124,x+66+(110,90)[k],136),'#48484A',6)
  if k==1 and t>=ts:
   g=spring(clamp((t-ts)/.3));checkmark(hc,x+176,130,round(16*max(.1,min(1.1,g))))
 sweep(hc,t,.3,600,150,40);place(im,hc,70,110+30*(1-e),.97+.03*e,min(1,e*1.5),True)
 # calendar: days light one per count, "3" lands on the spoken word
 e2=spring(clamp((t-tt+.25)/.36));cal=panel(940,300,CARD,24);dw=940/7
 lit=[tt-.05,lerp(tt,t3,.5)-.05,t3-.05]
 for i,dn in enumerate(DAYS):
  x=i*dw;txt(cal,dn,x+dw/2,36,24,GRAY,True,'Medium')
  on=i<3 and t>=lit[i];g=spring(clamp((t-lit[i])/.28)) if i<3 else 0
  rr(cal,(x+14,90,x+dw-14,250),(48,209,88,round(70*min(1,g))) if on else CARD2,18)
  if on:
   n=str(i+1);f=sf(round(76*max(.2,min(1.1,g))),'Bold');ImageDraw.Draw(cal).text((x+dw/2,170),n,font=f,fill=GREEN,anchor='mm')
   if i==2:rr(cal,(x+12,88,x+dw-12,252),None,20,GREEN,5)
 bar=smooth(clamp((t-tt)/(ty-tt+.05)));rr(cal,(14,268,14+(3*dw-28)*bar,282),GREEN,7)
 if t>=tt-.25:place(im,cal,70,350+30*(1-e2),.97+.03*e2,min(1,e2*1.5),True)
 # "fast": the ? tile streaks in from the right and lands on variant B
 if t>=ts-.35:
  u=smooth(clamp((t-(ts-.35))/.32));x=lerp(1180,70+40+230+100,u);y=lerp(260,210,u)
  if u<1:
   lay=blank(W,H)
   for j in range(4):ImageDraw.Draw(lay).line([(x+60+j*10,y-30+j*20),(x+60+260*(1-u)+j*10,y-30+j*20)],fill=(255,255,255,90),width=6)
   im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
  place(im,tile_q(110),x-55,y-55,sh=True)
 return im

# ---------------------------------------------------------------- 8. give (split): drop the export, get the analysis
@lru_cache(None)
def csv_file(size=150):
 im=blank(size,round(size*1.25));d=ImageDraw.Draw(im);w,h=im.size;f=w*.28
 d.polygon([(0,0),(w-f,0),(w,f),(w,h),(0,h)],fill='#F2F2F7');d.polygon([(w-f,0),(w,f),(w-f,f)],fill='#C7C7CC')
 rr(im,(w*.12,h*.58,w*.88,h*.80),'#30A46C',8);txt(im,'CSV',w/2,h*.60,round(w*.17),'white',True,'Bold')
 for i in range(3):rr(im,(w*.14,h*.18+i*h*.11,w*.14+w*(.5,.62,.4)[i],h*.18+i*h*.11+h*.04),'#C7C7CC',4)
 return im
def give(t,S,at):
 im=Image.new('RGBA',(W,H),BG);c=card();tg=at('give','تعطيه',.29);tb=at('give','باش',.48);ty=at('give','يديرلك',.83);ta=at('give','analyse.',1.19)
 # chat window
 ch=window(760,520,title=None);ch.alpha_composite(tile_q(30),(80,11));rr(ch,(30,436,730,496),'#2C2C2E',30)
 dropped=t>=tb
 if not dropped:txt(ch,'Reply…',60,454,22,GRAY)
 if dropped:   # the file chip sits in the message
  g=spring(clamp((t-tb)/.25));rr(ch,(400,80,730,160),'#3A3A3C',20);place(ch,csv_file(50),418,89,max(.1,g));txt(ch,'campaigns_export.csv',480,104,20,INK,weight='Medium')
 if t>=ty-.1:   # the reply streams in: lines, then a little chart on "analyse"
  ch.alpha_composite(tile_q(44),(30,190))
  for i in range(4):
   a=clamp((t-(ty-.1+i*.08))/.2);rr(ch,(90,196+i*34,90+(520,460,560,380)[i]*a,214+i*34),'#48484A',8)
  if t>=ta-.1:
   for i,hgt in enumerate([60,92,48,120,140]):
    a=spring(clamp((t-(ta-.1+i*.05))/.25));col=GREEN if i>=3 else '#636366';rr(ch,(110+i*58,420-hgt*a,150+i*58,420),col,6)
 sweep(ch,t,0,520,140,30);place(c,clip(ch,16),90,50)
 if not dropped:   # cursor drags the export into the chat
  u=smooth(clamp((t-.02)/(tb-.02)));fx,fy=lerp(-60,520,u),lerp(520,150,u)
  place(c,csv_file(130),fx,fy,1.0,1,True,rot=-8*(1-u))
  motion(c,t,[(0,fx+80,fy+120),(tb,520+80,150+120)])
 put_card(im,c,t);return im

# ---------------------------------------------------------------- 9+10. diff -> claude (full): one balance-scale choreography
def scale_scene(T,tad,tbeg,tq,tname):
 """tad: advanced lands (left pan), tbeg: beginner lands (right), tq: '?' appears, tname: flips to Claude and drops right."""
 im=Image.new('RGBA',(W,H),BG);cx,cy=540,300;L=380
 e=spring(clamp((T+.1)/.4))
 # beam angle: tips left (advanced heavier), wobbles when the chick lands, levels once Claude joins the beginner
 ang=0;tc=tname+.30
 if T>=tad:ang=-14*(1-math.exp(-(T-tad)/.18)*math.cos(9*(T-tad)))
 if T>=tbeg:ang+=2.5*math.exp(-(T-tbeg)/.25)*math.sin(14*(T-tbeg))
 if T>=tc:k=1-math.exp(-(T-tc)/.22)*math.cos(8*(T-tc));ang=-14*(1-k)
 if tad<=T and T<tbeg:ang+=1.2*math.sin(T*5)
 a=math.radians(ang)
 lay=blank(W,H);d=ImageDraw.Draw(lay)
 d.polygon([(cx-140,880),(cx+140,880),(cx+40,840),(cx-40,840)],fill='#3A3A40');rr(lay,(cx-14,cy,cx+14,850),'#55555C',8)
 ends=[(cx-L*math.cos(a),cy-L*math.sin(a)),(cx+L*math.cos(a),cy+L*math.sin(a))]
 d.line([ends[0],ends[1]],fill='#8E8E96',width=20);d.ellipse((cx-26,cy-26,cx+26,cy+26),fill='#C9A24B')
 pans=[]
 for ex,ey in ends:
  py=ey+230;d.line([(ex,ey),(ex-110,py)],fill='#8E8E96',width=4);d.line([(ex,ey),(ex+110,py)],fill='#8E8E96',width=4)
  d.chord((ex-140,py-50,ex+140,py+50),0,180,fill='#66666E');d.line([(ex-140,py),(ex+140,py)],fill='#8E8E96',width=6);pans.append((ex,py))
 place(im,lay,0,40*(1-e),opacity=min(1,e*1.5))
 # loads
 (lx,ly),(rx,ry)=pans
 if T>=tad-.6:tile_drop(im,tile_fluent('technologist',190),lx,ly-2,T,tad,240)
 if T>=tbeg-.6:tile_drop(im,tile_fluent('hatching_chick',130),rx-(68 if T>=tq else 0),ry-2,T,tbeg,260) if T<tq else place(im,tile_fluent('hatching_chick',130),rx-lerp(0,68,smooth(clamp((T-tq)/.3)))-65,ry-2-130)
 if T>=tq:   # the "?" hovers over the beginner, flips on the name, then drops beside the chick
  e3=spring(clamp((T-tq)/.35));size=130;tile=flip(size,T,tname)
  if T<tc:place(im,tile,rx+68-size/2,ry-400+10*math.sin(T*4)-30*(1-e3),max(.05,min(1,e3)),min(1,e3*2),True)
  else:
   v=T-tc;fall=min(1,v/.18);yy=lerp(ry-400,ry-2-size,fall*fall);place(im,tile,rx+68-size/2,yy,sh=True)
 return im
def diff(t,S,at):
 return scale_scene(t,at('diff','advanced',1.94),at('diff','مبتدئ.',3.76),99,99)
def claude(t,S,at):
 d0=S['diff']['end']-S['diff']['start'];T=t+d0;tn=at('claude','Claude',.94)+d0
 return scale_scene(T,at('diff','advanced',1.94),at('diff','مبتدئ.',3.76),d0+.02,tn)

# ---------------------------------------------------------------- 11. cta (split): comment ADS, the DM lands
def cta(t,S,at):
 im=Image.new('RGBA',(W,H),BG);tk=at('cta','كلمة',.78);tp=at('cta','الكومونتير',1.36);tn=at('cta','نصيفط',2.06)
 tpr=at('cta','prompt',2.84);tg=at('cta','guides',3.38);tl=at('cta','كاملين.',3.64)
 sheet=ig.render(t,'ADS','you',type_start=tk-.05,type_duration=.4,post_at=tp+.12,theme='dark',like_at=tl)
 if t<tk:sweep(sheet,t,0,560,140,28)
 e=spring(clamp((t+.1)/.36));sheet=sheet.resize((765,366),Image.Resampling.LANCZOS);place(im,sheet,157,358+30*(1-e),.97+.03*e,min(1,e*1.5),True)
 if t>=tn-.13:   # iOS-style DM banner drops in, attachments arrive on "prompt" and "guides"
  e2=spring(clamp((t-tn+.13)/.32));grow=smooth(clamp((t-tpr+.1)/.25));bh=round(lerp(118,214,grow))
  bn=panel(900,bh,'#2C2C2E',30);bn.alpha_composite(ig_tile(70),(24,24));txt(bn,'INSTAGRAM',112,26,18,GRAY,weight='Semibold');txt(bn,'now',840,26,18,GRAY)
  txt(bn,f'{CREATOR} sent you a message',112,58,28,INK,weight='Semibold')
  for k,(nm,ta_) in enumerate([('prompt.txt',tpr),('guides.pdf',tg)]):
   if t>=ta_-.1:
    g=spring(clamp((t-ta_+.1)/.28));x=112+k*300;p=blank(280,80);rr(p,(0,0,279,79),'#3A3A3C',18);rr(p,(14,14,58,66),('#0A84FF','#FF453A')[k],8)
    txt(p,nm,74,26,22,INK,weight='Medium');place(bn,p,x,118+20*(1-g),max(.05,min(1,g)),min(1,g*2))
  place(im,bn,90,124-24*(1-e2),opacity=min(1,e2*2),sh=True)
 return im

def graphics(b,t,S,at):
 return {'hook':hook,'pain':pain,'read':read,'saves':saves,'decision':decision,'data':data,'test':test,'give':give,
         'diff':diff,'claude':claude,'cta':cta}[b['name']](t,S,at)
