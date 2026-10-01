"""Gate: every unretimed take in the cut must correlate ~1.0 with the master at a tiny lag (48 kHz, lag-searched).
A near-zero correlation means the segment was cut from the wrong place or the concat drifted; ±0.5 ms is timestamp
rounding in the MKV concat and is fine. Retimed takes (speed != 1) are reported and skipped.
usage: python3 check_provenance.py  (reads edit/edl.json, edit/tight.mkv, edit/master.mkv)"""
import json,subprocess,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-ac','1','-ar','48000','-f','f32le','pipe:1']),np.float32)
v=pcm(P/'edit/tight.mkv');E=json.load(open(P/'edit/edl.json'));m=pcm(Path(E['sources'][E['ranges'][0]['src']]) if E['ranges'][0]['src'] in E['sources'] else P/'edit/master.mkv')
off=0;sr=48000;bad=0
for r in E['ranges']:
    sp=r.get('speed',1);dur=round(round((r['end']-r['start'])/sp*30)/30,8)
    if sp!=1:print(f"  {r['_']:10s} retimed {sp}x, excluded");off+=dur;continue
    t=.3;n=min(int((dur-.5)*sr),sr);a=v[round((off+t)*sr):round((off+t)*sr)+n];best=(0,-9)
    for lag in range(-1440,1441,4):
        c=m[round((r['start']+t)*sr)+lag:round((r['start']+t)*sr)+lag+n]
        if len(c)==n:
            cc=float(np.corrcoef(a,c)[0,1])
            if cc>best[1]:best=(lag,cc)
    lag=best[0];fine=max(((l,float(np.corrcoef(a,m[round((r['start']+t)*sr)+l:round((r['start']+t)*sr)+l+n])[0,1])) for l in range(lag-4,lag+5)),key=lambda x:x[1])
    flag='' if fine[1]>.99 and abs(fine[0])<=48 else '   <-- CHECK'
    bad+=bool(flag);print(f"  {r['_']:10s} corr {fine[1]:.4f} at lag {fine[0]/48:+.2f} ms{flag}");off+=dur
print(f'{bad} take(s) flagged' if bad else 'provenance ok: every unretimed take correlates ~1.0 with the master')
sys.exit(1 if bad else 0)
