#!/usr/bin/env python3
"""Audit every SPLICE of a cut for doubled speech. Run after every cut, before segmentation.

Three defects shipped on the Ad 1 reel and all three sat on a splice:
  "Prøv at, prøv at tænke"     - a stutter whisper auto-completed
  "de leads … de leads"        - two takes butted together, both ending the same way
  "det betyd- det betyder"     - a range end that kept the next take's first word
Whole-file transcribers smooth these over. Transcribing a SHORT window around each
splice in isolation exposes them, and the envelope shows a fragment (a speech blob
shorter than ~180ms right at the join) that no transcriber will print.

usage: python3 splice_audit.py <edl.json> <cut.mkv> [--win 1.4] [--language en] [--model transcribe-1]
  edl   the EDL that produced <cut> (splice times are derived from its ranges)
Prints, per splice: the isolated Fish Audio transcript of the window (words force-aligned locally) and any
  * repeated word inside the window
  * speech fragment shorter than 180ms touching the splice
Needs FISH_API_KEY (see fish_audio.py). An unavailable transcript is a failed audit, never a clean pass.
"""
import argparse, concurrent.futures, hashlib, io, json, os, re, subprocess, sys, wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path.home() / '.claude/skills/mehdiagent/scripts'))  # shared Fish client + aligner
from align_words import ALIGN_VERSION, align, clean_text, load_audio  # noqa: E402
from fish_audio import MODEL, asr, load_api_key  # noqa: E402

# ---- parallel + cached Fish ASR for short windows ------------------------------------------------
_CACHE = os.path.expanduser("~/.cache/fish_asr_windows"); os.makedirs(_CACHE, exist_ok=True)


def _key(media, t0, t1, language, model):
    st = os.stat(media)
    return hashlib.md5(f"{media}|{st.st_size}|{st.st_mtime}|{t0:.3f}|{t1:.3f}|{language}|{model}".encode()).hexdigest()


def fish_raw(media, t0, t1, key, language, model):
    """Fish response for [t0,t1] of media. Cached on (file size+mtime, t0, t1) so re-runs are free."""
    cp = os.path.join(_CACHE, _key(media, t0, t1, language, model) + ".fish.json")
    if os.path.exists(cp):
        return json.load(open(cp))
    wav = cp[:-10] + ".wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", media,
                    "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    try:
        with open(wav, "rb") as f:
            r = asr(f.read(), "window.wav", key, language, model)
        json.dump(r, open(cp, "w"))
    finally:
        if os.path.exists(wav): os.remove(wav)
    return r


def fish_window(media, t0, t1, key, language="en", model=MODEL):
    """Words (window-relative times) for [t0,t1]: Fish text, locally aligned. Cached per aligner version."""
    cp = os.path.join(_CACHE, _key(media, t0, t1, language, model) + f".{ALIGN_VERSION}.words.json")
    if os.path.exists(cp):
        return json.load(open(cp))
    r = fish_raw(media, t0, t1, key, language, model)
    audio = load_audio(media, t0, t1)
    segs = r.get("segments") or ([{"text": r.get("text", ""), "start": 0.0, "end": t1 - t0}]
                                 if clean_text(r.get("text", "")) else [])
    words = [w for w in align(audio, segs, language, r.get("text", "")) if w["type"] == "word"]
    json.dump(words, open(cp, "w"))
    return words


def fish_many(jobs, workers=4):
    """jobs: list of (media, t0, t1, key, language, model). Uploads in parallel, aligns one at a time."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda j: fish_raw(*j), jobs))
    return [fish_window(*j) for j in jobs]


ap = argparse.ArgumentParser()
ap.add_argument("edl"); ap.add_argument("cut")
ap.add_argument("--win", type=float, default=1.4, help="seconds each side of the splice")
ap.add_argument("--language", default="en")
ap.add_argument("--model", default=MODEL)
a = ap.parse_args()

key = load_api_key()

R = json.load(open(a.edl))["ranges"]
splices, t = [], 0.0
for r in R[:-1]:
    t += float(r["end"]) - float(r["start"])
    splices.append(round(t, 3))

SR = 8000
p = subprocess.run(["ffmpeg", "-v", "error", "-i", a.cut, "-vn", "-ac", "1", "-ar", str(SR),
                    "-f", "wav", "pipe:1"], capture_output=True)
w = wave.open(io.BytesIO(p.stdout))
x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
HOP = 40
n = len(x) // HOP
rms = np.sqrt((x[:n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-9
speech = 20 * np.log10(rms / rms.max()) > -40


def blobs(t0, t1):
    i0, i1 = int(t0 * SR / HOP), int(t1 * SR / HOP)
    out, on = [], None
    for i in range(max(0, i0), min(n, i1)):
        if speech[i] and on is None:
            on = i
        if not speech[i] and on is not None:
            out.append((on * HOP / SR, i * HOP / SR)); on = None
    if on is not None:
        out.append((on * HOP / SR, min(n, i1) * HOP / SR))
    return out


def bare(s):
    return re.sub(r"[^\wæøåÆØÅ]", "", s.lower())


try:
    windows = fish_many([(a.cut, max(0, s - a.win), s + a.win, key, a.language, a.model) for s in splices])
except RuntimeError as e:
    sys.exit(f"Splice audit incomplete: {e}")
flags = 0
for k, s in enumerate(splices):
    words = windows[k] or []
    txt = " ".join(x["text"] for x in words)
    notes = []
    b = [bare(x["text"]) for x in words]
    for i in range(len(b) - 1):
        for j in range(i + 1, len(b)):
            close = words[j]["start"] - words[i]["start"] < 0.6
            if b[i] and b[i] == b[j] and (len(b[i]) >= 5 or j == i + 1 or close):
                notes.append(f"repeat '{b[i]}' (words {i} and {j}, {words[j]['start']-words[i]['start']:.2f}s apart)")
    # merge blobs separated by < 25ms, then flag short ones touching the splice
    raw = blobs(s - 0.35, s + 0.35); merged = []
    for b0, b1 in raw:
        if merged and b0 - merged[-1][1] < 0.025:
            merged[-1] = (merged[-1][0], b1)
        else:
            merged.append((b0, b1))
    for (b0, b1) in merged:
        if 0.04 <= b1 - b0 < 0.18 and (abs(b0 - s) < 0.25 or abs(b1 - s) < 0.25):
            notes.append(f"fragment {b0:.3f}-{b1:.3f} ({(b1-b0)*1000:.0f}ms)")
    mark = "  <-- CHECK" if notes else ""
    print(f"splice {k:2d} @ {s:7.3f}s  [{R[k].get('_','')} | {R[k+1].get('_','')}]\n"
          f"      \"{txt}\"{mark}")
    for m in notes:
        print(f"      ! {m}")
    flags += bool(notes)
print(f"\n{flags} splice(s) flagged" if flags else "\nno doubled speech or fragments at any splice")
sys.exit(1 if flags else 0)
