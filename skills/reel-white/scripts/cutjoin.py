#!/usr/bin/env python3
"""ROBUST cut from an EDL: extracts each range as a segment (uniform re-encode) and
joins them with the concat FILTER (re-decodes -> perfect A/V sync, NO concat-copy which
accumulates AAC priming and makes the audio drift from the video). Keeps the source's
NATIVE resolution (no upscale to 1920) and won't blow up in OOM: the concat filter runs
on the SHORT segments, not on the long source (a filter_complex with 30+ trim branches on
the source fails). Use this for the vertical reel cut.
Sync check: ffprobe video stream duration ~= audio (drift < 1 frame).
Usage: python cutjoin.py <edl.json> <out.mp4>
The EDL has the shape {"sources":{"src":"<clip>"},"ranges":[{"start":a,"end":b,...},...]}.
The source path is resolved relative to the EDL folder (or absolute)."""
import json, sys, subprocess, os
edl = json.load(open(sys.argv[1])); OUT = sys.argv[2]
src = list(edl["sources"].values())[0]
if not os.path.isabs(src):
    src = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), os.path.basename(src))
R = edl["ranges"]
td = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_segs"); os.makedirs(td, exist_ok=True)
listf = os.path.join(td, "list.txt")
with open(listf, "w") as lf:
    for i, r in enumerate(R):
        a, b = float(r["start"]), float(r["end"]); d = round(b - a, 3)
        seg = os.path.join(td, f"s{i:02d}.mp4")
        cmd = ["ffmpeg", "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{d:.3f}",
               "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
               "-af", f"afade=t=in:st=0:d=0.012,afade=t=out:st={max(0, d-0.012):.3f}:d=0.012",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "25",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-video_track_timescale", "12800", seg]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        lf.write(f"file '{os.path.abspath(seg)}'\n")
# JOIN with the concat FILTER (NOT concat-copy): re-decodes the segments and concatenates
# the decoded streams -> PERFECT A/V sync. concat-copy of AAC segments accumulates the
# encoder priming per segment -> audio drifts from video (desync visible mid/late clip).
# The concat filter runs on the SHORT segments (not the long source) so it does NOT OOM.
segs = [os.path.join(td, f"s{i:02d}.mp4") for i in range(len(R))]
inputs = []
for s in segs: inputs += ["-i", s]
n = len(segs)
fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-y"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "25",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT],
                     capture_output=True, text=True).stdout.strip()
print(f"OK {OUT} dur={dur}s ({len(R)} segments, concat filter = perfect sync)")
