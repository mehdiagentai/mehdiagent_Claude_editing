"""Pin every word to the audio with torchaudio's MMS_FA aligner, using a Latin spelling of how each word SOUNDS.

Works for any language/script: the caption keeps the real spelling ("بزاف", "Claude"), the aligner gets the sound
("bzaf", "klod"). Gemini (transcribe_openrouter.py) supplies the spellings automatically; for Fish transcripts in a
non-Latin language, write them by hand (one lowercase a-z token per word).

    from align_latin import align_words
    words = align_words("edit/tight.mkv", [{"text": "بزاف", "latin": "bzaf", "start": 1.5, "end": 1.9}, ...])

Rough start/end (from the transcriber) choose the audio window of each chunk (<= 25 s, split at the widest gaps);
the aligner then sets start/end/score. A word scoring < 0.05 keeps its rough time (timing="rough"); order is kept
strictly increasing. First use downloads the MMS_FA checkpoint (~1.2 GB) into ~/.cache/torch/hub/checkpoints;
if Python's SSL store is broken (python.org builds), it falls back to curl - never to disabling verification.
"""
from __future__ import annotations
import re, subprocess
from pathlib import Path
import numpy as np

SR = 16000
MODEL_URL = "https://dl.fbaipublicfiles.com/mms/torchaudio/ctc_alignment_mling_uroman/model.pt"
MODEL_PATH = Path.home() / ".cache/torch/hub/checkpoints/model.pt"
CHUNK = 25.0
_M = None

def load_audio(path) -> np.ndarray:
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()

def ensure_model() -> None:
    if MODEL_PATH.is_file() and MODEL_PATH.stat().st_size > 1_000_000_000:
        return
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = MODEL_PATH.with_suffix(".part")
    print("  downloading the MMS_FA aligner (~1.2 GB, once)…", flush=True)
    subprocess.run(["curl", "-fL", "--retry", "3", "-C", "-", "-o", str(tmp), MODEL_URL], check=True)
    tmp.rename(MODEL_PATH)

def _model():
    global _M
    if _M is None:
        ensure_model()
        import torchaudio
        b = torchaudio.pipelines.MMS_FA
        _M = (b.get_model(with_star=False), b.get_tokenizer(), b.get_aligner())
    return _M

def latinize(s: str) -> str:
    """Keep what the MMS tokenizer knows: a-z and apostrophe. Digits/others are dropped."""
    s = s.lower()
    s = re.sub(r"[^a-z']+", "", s)
    return s or ""

def _chunks(words):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and w["start"] - words[cur[0]]["start"] > CHUNK:
            # cut at the widest gap inside the current chunk's second half
            gaps = [(words[j + 1]["start"] - words[j]["end"], j) for j in cur[len(cur) // 2:-1]] or [(0, cur[-1])]
            _, j = max(gaps)
            k = cur.index(j) + 1
            out.append(cur[:k]); cur = cur[k:]
        cur.append(i)
    if cur:
        out.append(cur)
    return out

def align_words(audio_or_path, words: list[dict], margin: float = 0.6) -> list[dict]:
    import torch
    audio = load_audio(audio_or_path) if not isinstance(audio_or_path, np.ndarray) else audio_or_path
    dur = len(audio) / SR
    model, tok, aligner = _model()
    for w in words:
        w["_lat"] = latinize(w.get("latin") or w["text"])
        w.setdefault("timing", "rough")
    for idx in _chunks(words):
        todo = [i for i in idx if words[i]["_lat"]]
        if not todo:
            continue
        t0 = max(0.0, words[idx[0]]["start"] - margin)
        t1 = min(dur, words[idx[-1]]["end"] + margin) if idx[-1] + 1 >= len(words) else min(dur, words[idx[-1] + 1]["start"] + margin / 2)
        clip = torch.from_numpy(audio[int(t0 * SR):int(t1 * SR)]).unsqueeze(0)
        with torch.inference_mode():
            em, _ = model(clip)
        try:
            spans = aligner(em[0], tok([words[i]["_lat"] for i in todo]))
        except Exception:
            continue
        ratio = clip.shape[1] / em.shape[1] / SR
        for i, sp in zip(todo, spans):
            sc = float(np.mean([s.score for s in sp]))
            words[i]["score"] = round(sc, 3)
            if sc >= 0.05:
                words[i].update(start=round(t0 + sp[0].start * ratio, 3), end=round(t0 + sp[-1].end * ratio, 3), timing="aligner")
    for a, b in zip(words, words[1:]):       # keep order strictly increasing
        if b["start"] <= a["start"]:
            b["start"] = round(a["start"] + 0.04, 3); b["end"] = max(b["end"], b["start"] + 0.05); b["timing"] = "nudged"
    for w in words:
        w.pop("_lat", None)
    return words
