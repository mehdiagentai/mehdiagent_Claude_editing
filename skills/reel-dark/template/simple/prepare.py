"""Transcript -> edit/transcript.json (corrected, timed words) + edit/beats.json. Re-run after every edit below.

Input: edit/transcripts/tight.json (from $M/transcribe.py edit/tight.mkv --edit-dir edit).
Only the three blocks marked EDIT change per video:

FIX     word index -> corrected text, or a list of tokens to split it into, each optionally "text|latin".
        A tuple key merges several transcriber words into one. Use it for: wrong spellings, product names, numbers
        written as words, and (Fish on a non-Latin language) the real script of every word.
        Give "|latin" sound-spellings when the caption script is not Latin: the aligner then re-times those words.
MANUAL  (text, rough_start) -> start: pin a word the aligner could not time (score 0) from the RMS profile.
BEATS   (beat_name, index of the beat's first word in the CORRECTED list) - printed below after each run.
"""
import json, sys
from pathlib import Path
P = Path(__file__).resolve().parent
sys.path.insert(0, str(Path.home() / ".claude/skills/mehdiagent/scripts"))

# ---- EDIT -------------------------------------------------------------------------------------------------------
FIX = {
    # 6: "بزاف|bzaf",                 # replace one word (with its sound-spelling for the aligner)
    # 8: ["خاصك|khassek", "تقطع|tqta"], # split one word into two
    # (20, 21): "كيضيعو|kaydiyyou",    # merge two words into one
}
MANUAL = {
    # ("وقت.", 16.8): 16.40,
}
BEATS = [
    # ("hook", 0), ("pain", 14), ("cta", 94),
]
# -----------------------------------------------------------------------------------------------------------------

src = json.load(open(P / "edit/transcripts/tight.json"))["words"]
src = [w for w in src if w.get("type", "word") == "word" and w.get("start") is not None]
# Fish can stack several words on one onset (40 ms grid): spread each run up to the next distinct onset (<= 0.12 s apart)
k = 0
while k < len(src):
    j = k
    while j + 1 < len(src) and abs(src[j + 1]["start"] - src[k]["start"]) < 1e-6:
        j += 1
    if j > k:
        nxt = src[j + 1]["start"] if j + 1 < len(src) else src[j]["end"]
        step = min(.12, max(.001, (nxt - src[k]["start"]) / (j - k + 1)))
        for m in range(k, j + 1):
            src[m] = dict(src[m], start=round(src[k]["start"] + (m - k) * step, 3))
    k = j + 1
words, relat = [], False
i = 0
keys = {(k if isinstance(k, tuple) else (k,)): v for k, v in FIX.items()}
starts = {k[0]: k for k in keys}
while i < len(src):
    if i in starts:
        idx = starts[i]; out = keys[idx]; toks = out if isinstance(out, list) else [out]
        a, b = src[idx[0]]["start"], max(src[idx[-1]]["end"], src[idx[0]]["start"] + .05)
        for k, tk in enumerate(toks):
            text, _, lat = tk.partition("|")
            w = {"text": text, "start": round(a + (b - a) * k / len(toks), 3), "end": round(a + (b - a) * (k + 1) / len(toks), 3), "type": "word"}
            if lat:
                w["latin"] = lat; relat = True
            words.append(w)
        i = idx[-1] + 1
    else:
        words.append({k: v for k, v in src[i].items() if k in ("text", "start", "end", "type", "latin", "timing", "score")}); i += 1
if relat:   # re-time with the local aligner (only meaningful when every word has a sound-spelling)
    from align_latin import align_words
    words = align_words(P / "edit/tight.mkv", words)
for w in words:
    k = (w["text"], round(w.get("start", -1), 2))
    for (mt, ms), new in MANUAL.items():
        if mt == w["text"] and abs(ms - w["start"]) < .6:
            w["start"], w["end"], w["timing"] = new, round(new + .2, 3), "manual"
bad = [(a, b) for a, b in zip(words, words[1:]) if a["start"] >= b["start"]]
for a, b in bad:
    print(f"WARNING order: {a['text']}@{a['start']} >= {b['text']}@{b['start']} - pin one of them in MANUAL")
json.dump({"words": words}, open(P / "edit/transcript.json", "w"), ensure_ascii=False, indent=1)

dur = float(__import__("subprocess").check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(P / "edit/tight.mkv")]))
if not BEATS:
    print("No BEATS yet - corrected words with their index:")
    for k, w in enumerate(words):
        print(f"{k:4d} {w['start']:6.2f} {w['text']}")
    sys.exit(0)
beats = [{"name": n, "start": 0 if j == 0 else round(words[k]["start"] - .04, 3)} for j, (n, k) in enumerate(BEATS)]
for j, b in enumerate(beats):
    b["end"] = beats[j + 1]["start"] if j + 1 < len(beats) else round(dur, 3)
json.dump(beats, open(P / "edit/beats.json", "w"), indent=1)
for b in beats:
    print(f"{b['name']:10s}{b['start']:6.2f}-{b['end']:6.2f} {b['end']-b['start']:5.2f}s  " +
          " | ".join(f"{w['text']}@{w['start']-b['start']:.2f}" for w in words if b["start"] <= w["start"] < b["end"]))
