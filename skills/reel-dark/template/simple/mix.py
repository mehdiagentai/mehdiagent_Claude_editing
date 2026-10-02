"""Voice + SFX (+ the creator's own music track if the settings name one). Caption clicks on the first/last word of every full-screen group, a whoosh per
scythe slash, thuds on tile landings, pops on every landing/absorb, click on toggles/posts. Times mirror scenes.py."""
from pathlib import Path
import json,subprocess,wave,re,numpy as np
P=Path(__file__).resolve().parent;A=P/'audio/sources'
B=json.load(open(P/'edit/beats.json'));S={b['name']:b for b in B};D=B[-1]['end'];sr=48000
TOK=json.load(open(P/'edit/transcript.json'))['words']
def bare(s):return re.sub(r'[.,،!?؟"\s]','',s.lower())
def at(name,word,default=0,nth=0):
 b=S[name];ww=[w for w in TOK if b['start']-.01<=w['start']<b['end']-.01 and bare(w['text'])==bare(word)]
 return ww[nth]['start']-b['start'] if len(ww)>nth else default
out=np.zeros((round(D*sr),2));cues=[];_cache={}
def cue(t,f,peak,role):
 if f not in _cache:_cache[f]=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(A/f),'-f','f32le','-ac','2','-ar',str(sr),'pipe:1']),np.float32).reshape(-1,2).astype(float)
 x=_cache[f]*10**(peak/20)/(abs(_cache[f]).max()+1e-12);s=max(0,round(t*sr));e=min(len(out),s+len(x))
 if e>s:out[s:e]+=x[:e-s]
 cues.append({'time':round(t,4),'source':'sources/'+f,'peak_dbfs':peak,'role':role})
def L(b,t):return S[b]['start']+t
G=json.load(open(P/'caption-groups.json'));frames=set()
for g in G:
 if g['mode']=='full':frames.update([g['words'][0]['entry_frame'],g['words'][-1]['entry_frame']])
 elif g['mode']=='face':frames.add(g['words'][0]['entry_frame'])   # face layout: one soft click per caption group
for n in sorted(frames):cue(n/30,'caption-click.wav',-25 if n/30<S['hook']['end'] else -27,'full-screen caption click')
# hook
s1=at('hook','تقطع',2.44);s2=max(s1+.55,at('hook','ولا',3.28)-.05)
for s in (s1,s2):cue(L('hook',s-.11),'whoosh.wav',-22,'scythe slash')
cue(L('hook',at('hook','لا.',3.52)),'pop.wav',-28,'survivor glow')
# pain
for w in ('media','owners'):cue(L('pain',at('pain',w)),'thud.wav',-24,'figure tile lands')
cue(L('pain',at('pain','كيضيعو')-.1),'pop.wav',-29,'hourglass')
cue(L('pain',at('pain','Business')-.12),'whoosh.wav',-29,'Business Manager rises')
# read
cue(L('read',at('read','يقراو')),'whoosh.wav',-31,'table pans')
cue(L('read',at('read','ويفهمو')-.1),'pop.wav',-28,'thinking emoji')
cue(L('read',at('read','data')-.05),'whoosh.wav',-31,'column highlight')
# saves
cue(L('saves',at('saves','AI')),'thud.wav',-21,'? tile lands')
cue(L('saves',at('saves','بزاف')-.1),'pop.wav',-28,'money bag')
for k in range(0,12,2):cue(L('saves',at('saves','بزاف')+.05+k*.11+.5),'pop.wav',-33,'bill into bag')
cue(L('saves',at('saves','الوقت')-.1),'whoosh.wav',-29,'hourglass rewinds')
# decision
cue(L('decision',at('decision','أحسن')-.1),'pop.wav',-28,'winner frame')
cue(L('decision',at('decision','decision')),'click.wav',-26,'toggle A off')
cue(L('decision',at('decision','أقصر')-.1),'pop.wav',-29,'stopwatch')
# data
tg=at('data','كيجمع',.98)
for i in range(8):cue(L('data',tg-.1+i*.06+.3),'pop.wav',-33,'metric absorbed')
cue(L('data',at('data','data.')),'pop.wav',-26,'tile pulse')
# test
tt=at('test','test',1.02);t3=at('test','تلت',1.42);ts=at('test','سريع.',2.52)
for t in (tt,(tt+t3)/2,t3):cue(L('test',t-.05),'pop.wav',-29,'day lights')
cue(L('test',ts-.35),'whoosh.wav',-24,'? streaks in');cue(L('test',ts),'click.wav',-27,'winner check')
# give
cue(L('give',at('give','باش')),'click.wav',-26,'file dropped')
cue(L('give',at('give','analyse.')-.1),'pop.wav',-29,'chart grows')
# diff / claude
cue(L('diff',at('diff','advanced')),'thud.wav',-19,'advanced lands');cue(L('diff',at('diff','مبتدئ.')),'thud.wav',-25,'beginner lands')
tn=at('claude','Claude',.94);cue(L('claude',tn-.22),'whoosh.wav',-27,'tile flips to Claude');cue(L('claude',tn+.30+.18),'thud.wav',-18,'Claude lands, scale levels')
# cta
cue(L('cta',at('cta','الكومونتير')+.12),'click.wav',-26,'Post');cue(L('cta',at('cta','نصيفط')-.13),'pop.wav',-27,'DM banner')
for w in ('prompt','guides'):cue(L('cta',at('cta',w)-.1),'pop.wav',-29,'attachment')
cue(L('cta',at('cta','كاملين.')),'pop.wav',-30,'like')
with wave.open(str(P/'audio/sfx.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
json.dump(cues,open(P/'audio/cue-sheet.json','w'),indent=2,ensure_ascii=False)
CFG=json.load(open(Path.home()/'.mehdiagent/config.json')) if (Path.home()/'.mehdiagent/config.json').exists() else {}
MUS=Path(str(CFG.get('music') or '')).expanduser() if CFG.get('music') else None
if MUS and MUS.is_file():   # music under the voice: -29 LUFS, ducked by the voice, faded at both ends
 fc=f'[0:a]asplit=2[v][sc];[2:a]highpass=f=100,loudnorm=I=-29:TP=-9:LRA=7,afade=t=in:d=0.15,afade=t=out:st={D-.8}:d=0.8[m];[m][sc]sidechaincompress=threshold=0.03:ratio=2:attack=15:release=250[duck];[v][1:a][duck]amix=inputs=3:duration=first:normalize=0,alimiter=limit=.68:level=false:latency=true[a]'
 extra=['-stream_loop','-1','-i',str(MUS)]
else:
 fc='[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.68:level=false:latency=true[a]';extra=[]
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'renders/clean-voice.mp4'),'-i',str(P/'audio/sfx.wav'),*extra,'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t',str(D),'-movflags','+faststart',str(P/f'renders/FINAL-{P.name}.mp4')],check=True)
print('mixed',len(cues),'cues')
