"""Dual-source master in one command:  python3 align.py CAMERA.MP4 "OBS RECORDING.mov"

the creator shoots reels on two devices. PICTURE = the camera file (portrait via rotation metadata), VOICE = the OBS
.mov, because the studio mic in shot is plugged into the machine running OBS. Never ship the camera's own mic.

What it does (all measured, nothing read off a lag estimator):
  1. extracts both audio tracks at 16 kHz mono into edit/
  2. validates the estimator on a synthetic +1234 ms shift (asserts)
  3. brute-force scans 1 kHz log-envelope correlation for OFF (camera time T  <->  mic time T+OFF), globally and
     in 20 s windows, and reports drift in ppm
  4. builds edit/master.mkv = camera picture (autorotated, x264 crf16) + mic audio from OFF (pcm 48 kHz mono)
  5. verifies the built master back against the camera's own audio (residual should be a few ms) and prints both
     noise floors so the README can quote them
It also grabs a teleprompter frame (edit/teleprompter.jpg): READ IT - it is the script, and it tells you the topic
before you spend transcription credits. Fact-check every product name in it (prompters can misspell them).
"""
import subprocess,sys,wave
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;E=P/'edit';E.mkdir(exist_ok=True)
CAM,MIC=sys.argv[1],sys.argv[2]
def wav16(src,out):subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(out)],check=True)
def load(p):
    w=wave.open(str(p));return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)
H=16                                                     # 1 ms hop
def env(a):
    n=len(a)//H;return np.log10(np.sqrt((a[:n*H].reshape(n,H)**2).mean(1))+10.0)
def score(ec,em,off,t0,t1):
    a=ec[int(t0*1000):int(t1*1000)];s=int(t0*1000)+off
    if s<0 or s+len(a)>len(em):return -2
    b=em[s:s+len(a)];a=a-a.mean();b=b-b.mean();return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))
def scan(ec,em,t0,t1,lo=-30000,hi=30000,step=5):
    best=max(range(lo,hi,step),key=lambda o:score(ec,em,o,t0,t1))
    best=max(range(best-6,best+7),key=lambda o:score(ec,em,o,t0,t1));return best,score(ec,em,best,t0,t1)
def floor(a):
    n=len(a)//320;r=np.sqrt((a[:n*320].reshape(n,320)**2).mean(1));d=20*np.log10(np.maximum(r,1e-3)/32768);return np.percentile(d,5),np.percentile(d,95)

wav16(CAM,E/'cam16.wav');wav16(MIC,E/'mic16.wav');cam,mic=load(E/'cam16.wav'),load(E/'mic16.wav');ec,em=env(cam),env(mic)
syn=np.concatenate([np.zeros(1234)+ec[:1234].mean(),ec]);o,_=scan(ec,syn,20,min(140,len(ec)/1000-5),-3000,3000)
assert o==1234,f'estimator failed its synthetic check ({o})';print('synthetic +1234 ms -> 1234  ok')
dur=min(len(ec),len(em))/1000;t0_,t1_=dur*.30,dur*.70    # centre window so +-30 s of offset keeps full overlap
OFF,c=scan(ec,em,t0_,t1_);print(f'GLOBAL OFF {OFF} ms  corr {c:.3f}')
assert c>.5,'weak correlation - are these two recordings of the same take?'
res=[]
for t0 in range(10,int(dur)-25,15):
    oo,ss=scan(ec,em,t0,t0+20,OFF-300,OFF+300,1);res.append((t0+10,oo,ss));print(f'  @{t0+10:4d}s  off {oo:6d} ms  corr {ss:.3f}')
good=np.array([(t,oo) for t,oo,ss in res if ss>.5])
if len(good)>2:k,b=np.polyfit(good[:,0],good[:,1],1);print(f'drift {k*1000:.1f} ppm  ({k*dur:.1f} ms over the take) -> {"constant offset is fine" if abs(k*dur)<15 else "CONSIDER a drift-corrected build"}')
off=OFF/1000
cmd=['ffmpeg','-v','error','-y']+(['-i',CAM,'-ss',f'{off:.3f}','-i',MIC] if off>=0 else ['-ss',f'{-off:.3f}','-i',CAM,'-i',MIC])
subprocess.run(cmd+['-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000','-ac','1','-shortest',str(E/'master.mkv')],check=True)
wav16(str(E/'master.mkv'),E/'master16.wav');ms=env(load(E/'master16.wav'))
if off<0:ec=ec[int(-off*1000):]                           # master timeline starts later than the camera's
r=max(range(-60,61),key=lambda o:score(ec,ms,o,15,min(150,dur-15)));print(f'residual master vs camera audio: {r} ms')
fc,fm=floor(cam),floor(load(E/'master16.wav'));print(f'noise floor  camera {fc[0]:.1f} dBFS (speech p95 {fc[1]:.1f})   mic/master {fm[0]:.1f} dBFS (speech p95 {fm[1]:.1f})')
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(dur*.25),'-i',MIC,'-frames:v','1','-vf','scale=1280:-1',str(E/'teleprompter.jpg')])
for f in ('cam16.wav','mic16.wav','master16.wav'):(E/f).unlink()
print('built edit/master.mkv   |   now READ edit/teleprompter.jpg (the script) and fact-check the names in it')
