from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
F=sorted((P/'renders').glob('FINAL-*.mp4'),key=lambda p:p.stat().st_mtime)[-1];B=json.load(open(P/'edit/beats.json'));E=json.load(open(P/'edit/edl.json'))
def pcm(path,sr=8000):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar',str(sr),'-f','f32le','pipe:1']),np.float32)
def frame(t):
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);return Image.frombytes('RGB',(1080,1920),b)
# Every scene plus payoff states, decoded from final MP4.
ts=[b['start']+min(2.0,(b['end']-b['start'])*.72) for b in B]
ts += [B[0]['start']+.35,B[0]['start']+1.0,B[0]['end']-.1]+[B[i]['end']-.25 for i in (5,10,15) if i<len(B)-1]+[B[-1]['end']-.1]   # generic: only beats that exist
sheet=Image.new('RGB',(6*216,4*384),'#DDDDDD')
for i,t in enumerate(ts):
 im=frame(t);im.save(P/f'review/final-{i:02d}.jpg');im.thumbnail((216,384));sheet.paste(im,((i%6)*216,(i//6)*384))
sheet.save(P/'review/FINAL-contact.jpg')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(F)]))
voice=pcm(P/'edit/tight.mkv');master=pcm(P/'edit/master.mkv');offset=0;corr=[]
for r in E['ranges']:
 sp=r.get('speed',1);dur=round(round((r['end']-r['start'])/sp*30)/30,8);t=.1 if dur<1 else .3;n=min(int((dur-t-.1)*8000),8000)
 if sp!=1:offset+=dur;corr.append({'take':r['_'],'source_start':r['start'],'source_end':r['end'],'correlation':None,'note':f'retimed {sp}x, excluded'});continue
 a=voice[round((offset+t)*8000):round((offset+t)*8000)+n];c=master[round((r['start']+t)*8000):round((r['start']+t)*8000)+n]
 corr.append({'take':r['_'],'source_start':r['start'],'source_end':r['end'],'correlation':round(float(np.corrcoef(a,c)[0,1]),6)})
 offset+=dur
mix=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(F),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']),np.float32)
report={'output':str(F),'duration':float(probe['format']['duration']),'video':[{k:s.get(k) for k in ['width','height','r_frame_rate','duration','codec_name']} for s in probe['streams'] if s['codec_type']=='video'],'audio':[{k:s.get(k) for k in ['duration','sample_rate','codec_name']} for s in probe['streams'] if s['codec_type']=='audio'],'source_cut_audio_correlations':corr,'mix_peak_dbfs':round(float(20*np.log10(abs(mix).max())),2),'frames_reviewed':ts,'verification_scope':'Decoded scene frames, final-frame captions, duration, signal and Fish Audio splice checks. No full perceptual listening available.'}
json.dump(report,open(P/'verification.json','w'),indent=2)
print(json.dumps(report,indent=2))
