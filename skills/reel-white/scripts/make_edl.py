#!/usr/bin/env python3
"""Cut 1: from the RAW transcript -> a tight EDL (removes pauses >= GAP) excluding
stumble/repetition windows you choose.
Usage: python make_edl.py <raw_transcript.json> <raw_clip_path> <out_edl.json> [gap=0.20] [exclude="a-b,c-d"]
exclude = windows (source seconds) to drop by midpoint, e.g. "67.5-83.5".
Tight padding (-0.03/+0.04). NB: after this, ALWAYS run the silence trim (silence_keep.py)."""
import json, sys
T, CLIP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.20
EXCL = []
if len(sys.argv) > 5 and sys.argv[5]:
    for part in sys.argv[5].split(","):
        a, b = part.split("-"); EXCL.append((float(a), float(b)))
ws = [w for w in json.load(open(T))["words"] if w.get("type") != "spacing" and w.get("start") is not None]
segs = [[ws[0]]]
for p, w in zip(ws, ws[1:]):
    (segs.append([w]) if w["start"]-p["end"] >= GAP else segs[-1].append(w))
ranges = []
for s in segs:
    a, b = s[0]["start"], s[-1]["end"]; mid = (a+b)/2
    if any(lo <= mid <= hi for lo, hi in EXCL) or b < 0.4: continue
    ranges.append({"source": "src", "start": round(max(0, a-0.03), 2), "end": round(b+0.04, 2),
                   "quote": " ".join(x["text"] for x in s)[:50]})
edl = {"version": 1, "sources": {"src": CLIP}, "ranges": ranges, "grade": "none",
       "overlays": [], "total_duration_s": round(sum(r["end"]-r["start"] for r in ranges), 2)}
json.dump(edl, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"{len(ranges)} segments, duration {edl['total_duration_s']}s -> {OUT}")
