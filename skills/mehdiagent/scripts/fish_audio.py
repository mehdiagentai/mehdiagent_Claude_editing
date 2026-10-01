"""Fish Audio speech-to-text client: key loading + one ASR request. Shared by transcribe.py and splice_audit.py.

Key order: FISH_API_KEY (or FISH_AUDIO_API_KEY) in the environment -> the file named by FISH_ENV_FILE ->
~/.mehdiagent/.env (written by the mehdiagent setup) or a .env in the working folder.
Env files are parsed for the one variable, never executed. Never print, embed or copy the key.

    python3 scripts/fish_audio.py        # free auth check (reads the credit endpoint, prints no account data)

ASR: POST https://api.fish.audio/v1/asr, Bearer key, `model` header (transcribe-1 default), multipart `audio`,
`language`, `ignore_timestamps=false`. Returns {text, duration, segments:[{text,start,end}]} - phrase-level
times only; align_words.py adds the per-word times locally.
"""
import os
import time
from pathlib import Path

import requests

API = "https://api.fish.audio"
MODEL = "transcribe-1"
NAMES = ("FISH_API_KEY", "FISH_AUDIO_API_KEY")
MAX_UPLOAD = 19 * 1024 * 1024  # Fish accepts ~20 MB / 60 min per request


def load_api_key() -> str:
    """FISH_API_KEY from the environment or ~/.mehdiagent/.env (see settings.py). Never print it."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from settings import key
    v = key("FISH_API_KEY") or key("FISH_AUDIO_API_KEY")
    if not v:
        raise RuntimeError("Fish Audio key missing. Run the mehdiagent setup, or put FISH_API_KEY=... in "
                           "~/.mehdiagent/.env (python3 settings.py env-path). Never paste the key into a chat.")
    return v


def asr(audio: bytes, filename: str, key: str, language: str | None = None, model: str = MODEL) -> dict:
    """One Fish ASR request. Retries only on 429/503 (not processed, so not billed twice); anything else stops."""
    data = {"ignore_timestamps": "false"}
    if language:
        data["language"] = language
    mime = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    for attempt in range(4):
        r = requests.post(f"{API}/v1/asr", headers={"Authorization": f"Bearer {key}", "model": model},
                          files={"audio": (filename, audio, mime)}, data=data, timeout=1800)
        if r.status_code in (429, 503) and attempt < 3:
            time.sleep(2 * 2 ** attempt)
            continue
        if r.status_code != 200:
            hint = {401: "bad key", 402: "no API credit left", 413: "file too large"}.get(r.status_code, "see status")
            raise RuntimeError(f"Fish Audio ASR returned HTTP {r.status_code} ({hint}). No provider fallback.")
        return r.json()


def main():
    try:
        r = requests.get(f"{API}/wallet/self/api-credit",
                         headers={"Authorization": f"Bearer {load_api_key()}"}, timeout=30)
    except requests.RequestException:
        raise SystemExit("Fish Audio connection failed. No credentials logged.")
    if r.status_code == 200:
        print("Fish Audio authentication verified (HTTP 200). No account data displayed.")
    else:
        raise SystemExit(f"Fish Audio returned HTTP {r.status_code}: 401 = bad key, 402 = no API credit.")


if __name__ == "__main__":
    main()
