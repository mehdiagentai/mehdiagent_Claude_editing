"""Report runs with no voice present in a cut.

TH is calibrated to the master's noise floor: on the studio-mic master speech sits at
p50 -36 / p95 -27 dBFS and true air is below -70, so -55 marks "no voice" without
counting quiet syllables and word tails as silence (the old -55 -> -40 value was tuned
for the camera mic, whose -57 dBFS room tone masked real pauses)."""
import subprocess, math, json, sys
import numpy as np
src = sys.argv[1] if len(sys.argv) > 1 else 'edit/tight.mkv'
TH = float(sys.argv[2]) if len(sys.argv) > 2 else -55.0
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                     capture_output=True).stdout
a = np.frombuffer(raw, dtype='<i2').astype(np.float32)
W = 160; n = len(a) // W
db = 20 * np.log10(np.maximum(np.sqrt((a[:n*W].reshape(n, W)**2).mean(1)), 1.0) / 32768.0)
runs = []; st = None
for i, v in enumerate(db):
    if v <= TH:
        if st is None: st = i
    else:
        if st is not None and (i - st) >= 15: runs.append((st/100, i/100, (i-st)/100))
        st = None
if st is not None and (len(db) - st) >= 15: runs.append((st/100, len(db)/100, (len(db)-st)/100))
B = json.load(open('edit/beats.json'))
bad = [r for r in runs if r[2] >= 0.30]
for s, e, d in runs:
    nb = next((b['name'] for b in B if b['start'] <= s < b['end']), '?')
    edge = any(abs(s - b['end']) < 0.12 or abs(e - b['start']) < 0.12 for b in B)
    print(f'  {s:6.2f}-{e:6.2f}  {d:5.2f}s  in {nb:10s}' + ('  [join]' if edge else '  [INSIDE TAKE]')
          + ('   <-- >=0.30' if d >= 0.30 else ''))
print(f'TH={TH} dBFS | {len(runs)} quiet runs >=0.15s; {len(bad)} at or over 0.30s')
