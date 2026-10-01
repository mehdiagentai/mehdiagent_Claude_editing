#!/usr/bin/env python3
"""Cut 2 (CRITICAL for sync): detect the REAL silences in the cut's audio and produce
an EDL that removes them. The word-gap method is NOT enough: the transcriber attaches the
silences to the word durations. This uses ffmpeg silencedetect on the audio.

GENTLE by default (costly lesson: at -30/-32dB it cut the soft word releases ->
"output"->"out", "you", "send" truncated). Default -40dB + keep-pad after the voice:
removes only the REAL silences, keeps the word tails. The LAST word is protected
(0.45 pad on the final silence) so it's never lost.

Usage: python silence_keep.py <cut.mp4> <out_edl.json> [thresh_dB=-40] [min_sil=0.35]
Then render, RE-TRANSCRIBE and VERIFY no word is truncated (the transcriber
"auto-completes" cut words: do NOT trust the text alone, check the times/audio)."""
import json, sys, subprocess, re
CUT, OUT = sys.argv[1], sys.argv[2]
DB = sys.argv[3] if len(sys.argv) > 3 else "-40"
# MIN 0.35: ALSO catches inter-sentence pauses 0.35-0.5s (with the old 0.5 they stayed long ->
# recurring "too much pause" feedback on shorts). Word tails are still protected by -40dB
# + the pads. For an even punchier short: pass MIN 0.30 as the 5th argument.
MIN = sys.argv[4] if len(sys.argv) > 4 else "0.35"
PAD_AFTER = 0.12    # how much I keep AFTER the voice ends before cutting the silence (was 0.16, tighter)
PAD_BEFORE = 0.06   # how much I anticipate the voice resuming
PAD_LAST = 0.45     # wider pad on the final silence -> protects the last word (do NOT lower)
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",CUT],
                           capture_output=True, text=True).stdout.strip())
out = subprocess.run(["ffmpeg","-i",CUT,"-af",f"silencedetect=n={DB}dB:d={MIN}","-f","null","-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
sil = list(zip(starts, ends))
keep = []; cur = 0.0
for a, b in sil:
    trailing = b >= dur-0.15     # last silence up to clip end: protect the last word
    pad = PAD_LAST if trailing else PAD_AFTER
    end = round(min(a+pad, dur), 2)
    if end > cur+0.15: keep.append((round(cur, 2), end))
    cur = round(b-PAD_BEFORE, 2)
if dur > cur+0.15: keep.append((round(cur, 2), round(dur, 2)))
edl = {"version": 1, "sources": {"src": CUT},
       "ranges": [{"source": "src", "start": a, "end": b, "quote": ""} for a, b in keep],
       "grade": "none", "overlays": [], "total_duration_s": round(sum(b-a for a, b in keep), 2)}
json.dump(edl, open(OUT, "w"), indent=1)
print(f"silences removed: {len(sil)} | duration {edl['total_duration_s']}s (was {dur:.1f}s) -> {OUT}")
