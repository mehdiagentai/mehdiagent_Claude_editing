"""Transcribe a video with Fish Audio and pin every word to its time (drop-in for the old Scribe transcribe.py).

Fish Audio (transcribe-1) decides what was said and, in practice, times every word itself (one segment per
word). align_words.py keeps those times, restores the punctuation, and force-aligns locally (MMS_FA) only if
Fish returns multi-word segments. Output goes to <edit_dir>/transcripts/<stem>.json in the shape
fix_words.py / render.py / mix.py already read:
    { "words": [ {"text": "...", "start": 0.12, "end": 0.34, "type": "word", "timing": "fish", ...} ],
      "segments": [...fish phrases...], "text": "...", "provider": "fish-audio", ... }

The raw Fish response is cached next to it (<stem>.fish.json): re-running (or re-aligning after an aligner
change) never pays for a second upload of the same file. Change the file, language or model and it re-uploads.

Usage:
    python3 transcribe_fish.py <video> [--edit-dir edit/final-timing] [--language en] [--model transcribe-1]
                                          [--force-align]   # re-time every word with the local aligner
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from align_words import ALIGN_VERSION, SR, align, clean_text, load_audio  # noqa: E402
from fish_audio import MAX_UPLOAD, MODEL, asr, load_api_key  # noqa: E402

import numpy as np  # noqa: E402


def extract(video: Path, dest: Path, mp3: bool = False) -> None:
    codec = ["-c:a", "libmp3lame", "-b:a", "64k"] if mp3 else ["-c:a", "pcm_s16le"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", str(SR), *codec,
                    str(dest)], check=True)


def fish_response(video: Path, out_dir: Path, language, model) -> tuple[dict, np.ndarray]:
    st = video.stat()
    signature = {"source": str(video.resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns,
                 "provider": "fish-audio", "model": model, "language": language}
    raw_path = out_dir / f"{video.stem}.fish.json"
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{video.stem}.wav"
        extract(video, wav)
        audio = load_audio(wav)
        if raw_path.exists():
            cached = json.loads(raw_path.read_text())
            if cached.get("signature") == signature:
                print(f"  cached Fish response: {raw_path.name}")
                return cached["response"], audio
        upload = wav
        if wav.stat().st_size > MAX_UPLOAD:
            upload = Path(tmp) / f"{video.stem}.mp3"
            extract(video, upload, mp3=True)
            if upload.stat().st_size > MAX_UPLOAD:
                sys.exit(f"{video.name} is too long for one Fish request (~60 min max): split it first.")
        mb = upload.stat().st_size / 2**20
        print(f"  uploading {upload.name} to Fish Audio ({mb:.1f} MB, model {model})", flush=True)
        response = asr(upload.read_bytes(), upload.name, load_api_key(), language, model)
    raw_path.write_text(json.dumps({"signature": signature, "response": response}, indent=1))
    return response, audio


def transcribe_one(video: Path, edit_dir: Path, language=None, model=MODEL, force_align=False) -> Path:
    out_dir = edit_dir / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{video.stem}.json"
    t0 = time.time()
    response, audio = fish_response(video, out_dir, language, model)
    segments = response.get("segments") or []
    if not segments and clean_text(response.get("text", "")):
        segments = [{"text": response["text"], "start": 0.0, "end": len(audio) / SR}]
    words = align(audio, segments, language, full_text=response.get("text", ""), force=force_align)
    payload = {"provider": "fish-audio", "model": model, "aligner": ALIGN_VERSION,
               "language_code": response.get("language_code") or language,
               "duration": response.get("duration") or len(audio) / SR,
               "text": clean_text(response.get("text", "")), "segments": segments, "words": words}
    out_path.write_text(json.dumps(payload, indent=1))
    spoken = [w for w in words if w["type"] == "word"]
    loose = [w for w in spoken if not w.get("aligned")]
    weak = [w for w in spoken if w.get("aligned") and w.get("score", 1) < 0.2]
    by = {k: sum(w["timing"] == k for w in spoken) for k in ("fish", "aligner", "estimated")}
    print(f"  saved: {out_path} in {time.time() - t0:.1f}s - {len(spoken)} words in {len(segments)} Fish segments; "
          f"timed by fish {by['fish']}, aligner {by['aligner']}, estimated {by['estimated']}")
    for w in loose:
        print(f"    ~ {w['text']!r} {w['start']:.2f}-{w['end']:.2f}  estimated (no letters to align / failed chunk)")
    for w in weak:
        print(f"    ? {w['text']!r} {w['start']:.2f}-{w['end']:.2f}  low alignment score {w['score']}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe with Fish Audio + local word alignment")
    ap.add_argument("video", type=Path)
    ap.add_argument("--edit-dir", type=Path, default=None, help="default: <video_parent>/edit")
    ap.add_argument("--language", default=None, help="ISO code hint, e.g. en, da. Omit to auto-detect.")
    ap.add_argument("--model", default=MODEL, help="transcribe-1 (default) or transcribe-1-pro")
    ap.add_argument("--force-align", action="store_true", help="re-time every word with the local MMS_FA aligner")
    ap.add_argument("--num-speakers", type=int, default=None, help=argparse.SUPPRESS)  # Scribe-era flag, ignored
    a = ap.parse_args()
    video = a.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")
    transcribe_one(video, (a.edit_dir or video.parent / "edit").resolve(), a.language, a.model, a.force_align)


if __name__ == "__main__":
    main()
