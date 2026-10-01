from draw import *
from pathlib import Path
import json,subprocess,re,math,sys,numpy as np
sys.path.insert(0,str(P/'helpers'));import ar_caption as arc
import scenes
CFG=json.load(open(Path.home()/'.mehdiagent/config.json')) if (Path.home()/'.mehdiagent/config.json').exists() else {}
RTL=CFG.get('caption_direction','ltr')=='rtl';BGR=bool(CFG.get('background_removal',True)) and (P/'edit/mask_person.mkv').exists()
# Pre-cut pipeline. Graphics in the 1080x1920 scene canvas, moved down TOP_SHIFT (Instagram safe top) and faded above y 180.
# Presenter: if background_removal is on, alpha = person matte (soft hair edges) gated by a dilated subject matte (kills
# leaks like furniture, keeps a held mic) - both from Apple Vision (helpers/personmask). Captions follow the settings:
# caption_direction rtl = whole line right-to-left (English words included), ltr = left-to-right.
# ---- EDIT PER REEL: CROP_Y, FULL, CAPY, OVERRIDE ----
TOP_SHIFT=90;SPLIT_Y=768+TOP_SHIFT;PH=1920-SPLIT_Y;CROP_Y=250
B=json.load(open(P/'edit/beats.json'));D=B[-1]['end'];N=round(D*30);S={b['name']:b for b in B}
FULL={'hook','read','decision','test','diff','claude'}
CAPY={'hook':1010,'read':1010,'decision':1010,'test':800,'diff':1010,'claude':1010}
TOK=json.load(open(P/'edit/transcript.json'))['words']
OVERRIDE={
 'hook':    [(2,{}),(3,{}),(2,{}),(3,{'hl':{'تقطع':RED}}),(2,{}),(2,{})],
 'read':    [(3,{}),(2,{'hl':{'data':BLUE}}),(2,{})],
 'decision':[(3,{}),(3,{'hl':{'decision':GREEN}}),(3,{})],
 'test':    [(4,{}),(3,{'hl':{'تلت':GREEN}}),(3,{})],
 'diff':    [(4,{}),(3,{}),(2,{'hl':{'advanced':GREEN}}),(4,{})],
 'claude':  [(2,{}),(2,{'big':150,'color':TERRA}),(3,{})],
}
def bare(s):return re.sub(r'[.,،!?؟"\s]','',s.lower())
def at(name,word,default=0,nth=0):
 b=S[name];ww=[w for w in TOK if b['start']-.01<=w['start']<b['end']-.01 and bare(w['text'])==bare(word)]
 return ww[nth]['start']-b['start'] if len(ww)>nth else default
GROUPS=[]
for b in B:
 b['mode']='full' if b['name'] in FULL else 'split'
 ww=[w for w in TOK if b['start']<=w['start']<b['end']];groups=[]
 if b['name'] in OVERRIDE:
  i=0
  for n,opt in OVERRIDE[b['name']]:
   if i<len(ww):groups.append((ww[i:i+n],opt));i+=n
  if i<len(ww):groups.append((ww[i:],{}))
 else:
  cur=[]
  for w in ww:
   if cur and (len(cur)>=4 or len(' '.join(x['text'] for x in cur+[w]))>24):groups.append((cur,{}));cur=[]
   cur.append(w)
   if re.search(r'[.,،!?]$',w['text']) and len(cur)>=2:groups.append((cur,{}));cur=[]
  if cur:groups.append((cur,{}))
 for k,(ws,opt) in enumerate(groups):
  GROUPS.append({'scene':b['name'],'mode':b['mode'],'text':' '.join(w['text'] for w in ws),
   'start':math.floor(ws[0]['start']*30)/30,'end':math.floor(groups[k+1][0][0]['start']*30)/30 if k+1<len(groups) else b['end'],
   'words':[{'text':w['text'],'entry_frame':math.floor(w['start']*30)} for w in ws],**opt})
json.dump(GROUPS,open(P/'caption-groups.json','w'),ensure_ascii=False,indent=2);json.dump({'duration':D,'scenes':B},open(P/'scenes.json','w'),indent=2)
def graphics(b,t):return scenes.graphics(b,t,S,at)
def caption(im,b,n):
 t=n/30;gg=[g for g in GROUPS if g['scene']==b['name'] and g['start']<=t<g['end']]
 if not gg:return
 g=gg[0]
 if g['mode']=='full':
  obj=arc.render_words(g,n,rtl=RTL);place(im,obj,(1080-obj.width)/2,CAPY.get(b['name'],1010)+TOP_SHIFT-obj.height/2)
 else:
  row=arc.chip_text([w['text'] for w in g['words']],44,960,rtl=RTL);wd=row.width+48
  rr(im,((1080-wd)/2,SPLIT_Y-42,(1080+wd)/2,SPLIT_Y+42),'#1C1C1E',12,'#3A3A3C',2);place(im,row,(1080-row.width)/2,SPLIT_Y-row.height/2+4)
_TOPM=None
def fade_top(im):
 """Guard for the Instagram safe top: graphics fade to the ground between screen y 180 and 216."""
 global _TOPM
 if _TOPM is None:_TOPM=Image.fromarray(np.tile(np.clip((np.arange(220)-180)/36,0,1)[:,None]*255,(1,1080)).astype(np.uint8))
 top=im.crop((0,0,1080,220));bg=Image.new("RGBA",(1080,220),BG);bg.paste(top,(0,0),_TOPM);im.paste(bg,(0,0))
def frame(n,person=None):
 t=n/30;b=next((b for b in B if round(b['start']*30)<=n<round(b['end']*30)),B[-1]);g_=graphics(b,t-b['start']);im=Image.new('RGBA',g_.size,BG);im.alpha_composite(g_.crop((0,0,g_.width,g_.height-TOP_SHIFT)),(0,TOP_SHIFT))
 fade_top(im)
 if b['mode']=='split' and person is not None:place(im,person,0,SPLIT_Y)
 caption(im,b,n);return im.convert('RGB')
def matte(pm,sm):
 """person matte gated by the subject matte grown ~24 px (at 1/4 res) and feathered."""
 s=Image.fromarray(sm).resize((270,PH//4),Image.Resampling.BILINEAR).filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(3)).resize((1080,PH),Image.Resampling.BILINEAR)
 a=np.minimum(pm.astype(np.float32),np.array(s,np.float32))/255.
 return (np.clip(a,0,1)**1.15*255).astype(np.uint8)
def cutout(rgb,pm,sm):
 im=Image.frombytes('RGB',(1080,PH),rgb).convert('RGBA')
 if pm is None:return im
 im.putalpha(Image.fromarray(matte(np.frombuffer(pm,np.uint8).reshape(PH,1080),np.frombuffer(sm,np.uint8).reshape(PH,1080))));return im
def _grab(src,t,fmt):
 return subprocess.check_output(['ffmpeg','-v','error','-ss',f'{t:.4f}','-i',str(P/src),'-frames:v','1','-vf',f'crop=1080:{PH}:0:{CROP_Y}','-f','rawvideo','-pix_fmt',fmt,'pipe:1'])
def person_at(t):return cutout(_grab('edit/tight.mkv',t,'rgb24'),_grab('edit/mask_person.mkv',t,'gray') if BGR else None,_grab('edit/mask_subject.mkv',t,'gray') if BGR else None)
def preview(frac=.65,tag='preview'):
 sheet=Image.new('RGB',(6*270,2*480),'#222')
 for i,b in enumerate(B):
  t=b['start']+min((b['end']-b['start'])*frac,2.3);n=round(t*30);im=frame(n,person_at(t));im.save(P/f'renders/{tag}-{b["name"]}.jpg');sheet.paste(im.resize((270,480)),((i%6)*270,(i//6)*480))
 sheet.save(P/f'renders/contact-{tag}.jpg')
def strip(name,times,out):
 b=S[name];sheet=Image.new('RGB',(len(times)*270,480),'#222')
 for i,lt in enumerate(times):
  t=b['start']+lt;im=frame(round(t*30),person_at(t) if b['mode']=='split' else None);sheet.paste(im.resize((270,480)),(i*270,0))
 sheet.save(out)
def render():
 def dec(src,fmt):return subprocess.Popen(['ffmpeg','-v','error','-i',str(P/src),'-vf',f'fps=30,crop=1080:{PH}:0:{CROP_Y}','-f','rawvideo','-pix_fmt',fmt,'pipe:1'],stdout=subprocess.PIPE)
 dv=dec('edit/tight.mkv','rgb24');dp,ds=(dec('edit/mask_person.mkv','gray'),dec('edit/mask_subject.mkv','gray')) if BGR else (None,None)
 out=P/'renders/clean-voice.mp4'
 enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','30','-i','pipe:0','-i',str(P/'edit/tight.mkv'),'-map','0:v','-map','1:a','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(N/30),'-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 for n in range(N):
  rgb=dv.stdout.read(1080*PH*3);pm=dp.stdout.read(1080*PH) if BGR else None;sm=ds.stdout.read(1080*PH) if BGR else None
  if len(rgb)!=1080*PH*3 or (BGR and (len(pm)!=1080*PH or len(sm)!=1080*PH)):raise RuntimeError(f'Short frame {n}')
  b=next((b for b in B if round(b['start']*30)<=n<round(b['end']*30)),B[-1])
  enc.stdin.write(frame(n,cutout(rgb,pm,sm) if b['mode']=='split' else None).tobytes())
  if n%150==0:print(f'{n}/{N}',flush=True)
 enc.stdin.close();assert enc.wait()==0
 for d_ in (dv,dp,ds):
  if d_:d_.stdout.close();d_.wait()
 print(out)
if __name__=='__main__':
 if '--preview' in sys.argv:preview()
 elif '--strip' in sys.argv:
  i=sys.argv.index('--strip');strip(sys.argv[i+1],[float(x) for x in sys.argv[i+2].split(',')],P/f'renders/strip-{sys.argv[i+1]}.jpg')
 else:render()
