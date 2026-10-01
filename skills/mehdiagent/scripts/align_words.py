"""Turn Fish Audio segments into timed words (Fish's own word times, local forced alignment as fallback).

Fish Audio's ASR returns `segments` ({text, start, end}). In practice (transcribe-1) every
segment is ONE word on a 40 ms grid, and those times beat the aligner against measured silence edges (~30 ms vs
~42 ms mean error), so a one-word segment keeps Fish's times (`timing: "fish"`). Fish's docs only promise
phrase segments: any multi-word segment is force-aligned locally with torchaudio's MMS_FA wav2vec2 model
(`timing: "aligner"`, CPU, nothing uploaded). `force=True` aligns everything. The text is never changed here
beyond restoring the punctuation Fish's one-word segments drop.

The aligner's first use downloads the MMS_FA checkpoint (~1.2 GB, Meta via torch.hub) into
~/.cache/torch/hub/checkpoints - it is only loaded when a segment actually needs aligning.

    from align_words import load_audio, align
    audio = load_audio("edit/tight.mkv")                 # float32 mono 16 kHz
    words = align(audio, fish_segments, "en", full_text)  # [{text,start,end,type,timing,aligned,segment}]
"""
from __future__ import annotations

import difflib
import re
import subprocess
import threading
import unicodedata

import numpy as np

SR = 16000
ALIGN_VERSION = "fish-words+mms_fa-2"
CHUNK_S = 30.0          # segments are grouped into chunks up to this long (memory ~ chunk length squared)

_MODEL = None
_LOCK = threading.Lock()

SPEAKER = re.compile(r"<\|[^|>]*\|>")
EVENT = re.compile(r"^\[[^\]]+\]$")
EVENT_ANY = re.compile(r"\[[^\]]+\]")
FOLD = {"æ": "ae", "ø": "o", "å": "aa", "ß": "ss", "œ": "oe", "ð": "d", "þ": "th", "ł": "l", "’": "'", "‘": "'"}
SYMBOL = {"%": " percent ", "&": " and ", "+": " plus ", "@": " at ", "=": " equals ", "#": " number "}
SCALE = {"k": "thousand", "m": "million", "b": "billion", "bn": "billion", "x": "times"}


def load_audio(media, t0: float | None = None, t1: float | None = None) -> np.ndarray:
    """Decode any media file (or a window of it) to float32 mono 16 kHz with ffmpeg."""
    cmd = ["ffmpeg", "-v", "error"]
    if t0 is not None:
        cmd += ["-ss", f"{t0:.3f}"]
    if t1 is not None:
        cmd += ["-t", f"{t1 - (t0 or 0):.3f}"]
    cmd += ["-i", str(media), "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "pipe:1"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def clean_text(text: str) -> str:
    """Drop Fish speaker markers (<|speaker:0|>) and collapse whitespace."""
    return " ".join(SPEAKER.sub(" ", text or "").split())


# ---- spoken form used ONLY for alignment (the output keeps Fish's text) ------------------------
_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen " \
        "sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _int_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + _int_words(n % 100))
    for size, name in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= size:
            return _int_words(n // size) + " " + name + ("" if n % size == 0 else " " + _int_words(n % size))
    return str(n)


def _number_words(digits: str) -> str:
    whole, _, frac = digits.replace(",", "").partition(".")
    out = _int_words(int(whole)) if whole and len(whole) <= 12 else " ".join(_ONES[int(c)] for c in whole)
    if frac:
        out += " point " + " ".join(_ONES[int(c)] for c in frac)
    return out


def spoken(word: str, language: str | None) -> str:
    """'$20M' -> 'twenty million dollars', 'GPT-5.6' -> 'gpt five point six', 'København' -> 'kobenhavn'."""
    w = word.lower()
    for k, v in FOLD.items():
        w = w.replace(k, v)
    w = "".join(c for c in unicodedata.normalize("NFKD", w) if not unicodedata.combining(c))
    english = (language or "en").lower().startswith("en")
    dollars = english and "$" in w
    for k, v in SYMBOL.items():
        if english:
            w = w.replace(k, v)
    if english:
        w = re.sub(r"(\d[\d,]*(?:\.\d+)?)\s*(bn|k|m|b|x)\b",
                   lambda m: _number_words(m.group(1)) + " " + SCALE[m.group(2)], w)
        w = re.sub(r"\d[\d,]*(?:\.\d+)?", lambda m: " " + _number_words(m.group(0)) + " ", w)
    w = re.sub(r"[^a-z']+", " ", w).replace(" '", " ").strip(" '")
    if dollars and w:
        w += " dollars"
    return " ".join(w.split())


# ---- alignment ---------------------------------------------------------------------------------
def _model():
    global _MODEL
    if _MODEL is None:
        import torchaudio
        bundle = torchaudio.pipelines.MMS_FA
        _MODEL = (bundle.get_model(with_star=False), bundle.get_tokenizer(), bundle.get_aligner())
    return _MODEL


def _align_chunk(audio: np.ndarray, t0: float, t1: float, words: list[dict]) -> bool:
    """Align words (those with a spoken form) inside audio[t0:t1]. Writes start/end/score in place."""
    import torch
    model, tokenizer, aligner = _model()
    todo = [w for w in words if w["_spoken"]]
    if not todo:
        return True
    clip = audio[int(t0 * SR):int(t1 * SR)]
    if len(clip) < SR // 10:
        return False
    # one entry per spoken token; a word like "twenty million" spans several tokens
    parts, owner = [], []
    for i, w in enumerate(todo):
        for p in w["_spoken"].split():
            parts.append(p)
            owner.append(i)
    with _LOCK, torch.inference_mode():
        emission, _ = model(torch.from_numpy(clip).unsqueeze(0))
        try:
            spans = aligner(emission[0], tokenizer(parts))
        except Exception:
            return False  # more letters than audio frames, usually a wrong segment window
    ratio = len(clip) / emission.shape[1] / SR
    for i, w in enumerate(todo):
        own = [s for k, sp in enumerate(spans) if owner[k] == i for s in sp]
        w["start"] = round(t0 + own[0].start * ratio, 3)
        w["end"] = round(t0 + own[-1].end * ratio, 3)
        w["score"] = round(float(np.mean([s.score for s in own])), 3)
        w["aligned"], w["timing"] = True, "aligner"
    return True


def _spread(words: list[dict], t0: float, t1: float) -> None:
    """Fallback: share [t0, t1] between the words by letter count (marked aligned=False)."""
    weights = [max(1, len(w["_spoken"] or w["text"])) for w in words]
    step = (t1 - t0) / max(1, sum(weights))
    t = t0
    for w, n in zip(words, weights):
        w["start"], w["end"], w["aligned"], w["timing"] = round(t, 3), round(t + n * step, 3), False, "estimated"
        t += n * step


def _bare(tok: str) -> str:
    return re.sub(r"[\W_]+", "", tok.lower())


def restore_punctuation(words: list[dict], full_text: str) -> None:
    """Fish's one-word segments drop punctuation ("month" vs "month."); captions break on it, so take each
    token's spelling from the full transcript wherever the two sequences agree."""
    tokens = [t for t in clean_text(EVENT_ANY.sub(" ", full_text or "")).split() if _bare(t)]
    spoken_words = [w for w in words if w["type"] == "word"]
    matcher = difflib.SequenceMatcher(None, [_bare(w["text"]) for w in spoken_words], [_bare(t) for t in tokens],
                                      autojunk=False)
    for a, b, n in matcher.get_matching_blocks():
        for k in range(n):
            spoken_words[a + k]["text"] = tokens[b + k]


def align(audio: np.ndarray, segments: list[dict], language: str | None = "en",
          full_text: str | None = None, force: bool = False) -> list[dict]:
    """Fish segments [{text,start,end}] -> word list in the shape the reel scripts expect."""
    duration = len(audio) / SR
    segs = [s for s in segments if clean_text(s.get("text", ""))]
    words: list[dict] = []
    for si, s in enumerate(segs):
        toks = EVENT_ANY.sub(lambda m: " " + m.group(0).replace(" ", "_") + " ", clean_text(s["text"])).split()
        for tok in toks:
            event = bool(EVENT.match(tok))
            word = {"text": tok.replace("_", " ") if event else tok, "type": "audio_event" if event else "word",
                    "segment": si, "_spoken": "" if event else spoken(tok, language)}
            if len(toks) == 1:  # Fish gave this word its own segment: its times are the word's times
                word["fish_start"], word["fish_end"] = float(s["start"]), float(s["end"])
                if not force:
                    word.update(start=round(float(s["start"]), 3), end=round(float(s["end"]), 3),
                                aligned=True, timing="fish")
            words.append(word)
    if full_text:
        restore_punctuation(words, full_text)

    # chunk consecutive segments; each chunk's audio runs from gap-midpoint to gap-midpoint
    chunks, cur = [], []
    for si, s in enumerate(segs):
        if cur and float(s["end"]) - float(segs[cur[0]]["start"]) > CHUNK_S:
            chunks.append(cur)
            cur = []
        cur.append(si)
    if cur:
        chunks.append(cur)
    for ci, idx in enumerate(chunks):
        first, last = segs[idx[0]], segs[idx[-1]]
        prev_end = float(segs[chunks[ci - 1][-1]]["end"]) if ci else 0.0
        next_start = float(segs[chunks[ci + 1][0]]["start"]) if ci + 1 < len(chunks) else duration
        t0 = max(0.0, (prev_end + float(first["start"])) / 2 if ci else 0.0)
        t1 = min(duration, (float(last["end"]) + next_start) / 2 if ci + 1 < len(chunks) else duration)
        members = [w for w in words if w["segment"] in idx]
        if all("start" in w for w in members):
            continue  # Fish already timed every word here: the aligner model is never loaded
        if not _align_chunk(audio, t0, t1, members):
            for si in idx:  # chunk failed: try each segment on its own, then spread
                seg_words = [w for w in words if w["segment"] == si]
                if all("start" in w for w in seg_words):
                    continue
                a, b = max(0.0, float(segs[si]["start"]) - 0.25), min(duration, float(segs[si]["end"]) + 0.25)
                if not _align_chunk(audio, a, b, seg_words):
                    _spread(seg_words, float(segs[si]["start"]), float(segs[si]["end"]))

    # words with no alignable letters ("—", "[laughter]") take the gap between their neighbours
    for i, w in enumerate(words):
        if "start" in w:
            continue
        prev_end = next((words[j]["end"] for j in range(i - 1, -1, -1) if "end" in words[j]), 0.0)
        next_start = next((words[j]["start"] for j in range(i + 1, len(words)) if "start" in words[j]), prev_end)
        w.update(start=round(prev_end, 3), end=round(max(prev_end, next_start), 3), aligned=False, timing="estimated")
    for w in words:
        w.pop("_spoken", None)
    return words
