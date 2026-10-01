"""Transcribe with Gemini 2.5 through OpenRouter, then pin every word locally (align_latin.py).

Gemini returns each word in the script the creator writes (Arabic script for Darija with English/French tech words
kept in Latin, Latin for English, ...) plus a Latin spelling of how it sounds; MMS_FA turns those into exact times.
Output: <edit_dir>/transcripts/<stem>.json  {"words":[{"text","start","end","type":"word","latin","timing","score"}],
"text","language","provider":"openrouter","model"}  - the same shape the reel skills read. The raw model answer is
cached as <stem>.openrouter.json (same file + model + language = no second paid call).

    python3 transcribe_openrouter.py <video> [--edit-dir edit] [--language ar-darija] [--model google/gemini-2.5-flash]
    python3 transcribe_openrouter.py --check     # free key check (GET /api/v1/key), prints no account data
"""
from __future__ import annotations
import argparse, base64, hashlib, json, subprocess, sys, tempfile, time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings import key, load  # noqa: E402

API = "https://openrouter.ai/api/v1"
PROMPT = """You are a verbatim transcriber for short-form video captions.
Transcribe EVERY spoken word of this audio, in order, exactly as said (no summarising, no fixing grammar).
Speech language hint: {lang}.
Spelling rules for "text":
- Write each word the way a native creator would type it in captions{script_rule}.
- Keep brand names and English/French tech or marketing terms in Latin letters (e.g. Claude, AI, data, campaign, prompt).
- Keep punctuation attached to the word it follows (".", ",", "?", "،").
For each word also give "latin": a lowercase a-z spelling of how the word SOUNDS (no digits, no accents, no spaces),
used by a forced aligner (e.g. "بزاف" -> "bzaf", "Claude" -> "klod", "3" spoken as "three" -> "three").
Give approximate "start"/"end" in seconds from the start of the audio.
Answer ONLY with JSON: {{"language": "<code>", "words": [{{"text": "...", "latin": "...", "start": 0.0, "end": 0.0}}]}}"""
SCRIPT_RULE = {
    "arabic": " (Arabic script for Arabic/Darija words)",
    "latin": " (Latin script)",
}

def extract_wav(video: Path, dest: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dest)], check=True)

def ask(wav: bytes, lang: str, script: str, model: str, api_key: str) -> dict:
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT.format(lang=lang or "auto-detect", script_rule=SCRIPT_RULE.get(script, ""))},
            {"type": "input_audio", "input_audio": {"data": base64.b64encode(wav).decode(), "format": "wav"}},
        ]}],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "X-Title": "mehdiagent"}
    for attempt in range(4):
        r = requests.post(f"{API}/chat/completions", headers=headers, json=body, timeout=600)
        if r.status_code in (429, 502, 503) and attempt < 3:
            time.sleep(4 * (attempt + 1)); continue
        if r.status_code != 200:
            raise RuntimeError(f"OpenRouter HTTP {r.status_code}: {r.text[:300]}")
        content = r.json()["choices"][0]["message"]["content"]
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(content)
    raise RuntimeError("OpenRouter kept rate-limiting; try again in a minute")

def check() -> int:
    k = key("OPENROUTER_API_KEY")
    if not k:
        print("OPENROUTER_API_KEY missing - put it in", Path.home() / ".mehdiagent/.env"); return 1
    r = requests.get(f"{API}/key", headers={"Authorization": f"Bearer {k}"}, timeout=30)
    print(f"OpenRouter authentication {'verified' if r.status_code == 200 else 'FAILED'} (HTTP {r.status_code}). No account data displayed.")
    return 0 if r.status_code == 200 else 1

def transcribe(video: Path, edit_dir: Path, language: str | None, model: str, script: str) -> Path:
    from align_latin import align_words
    out_dir = edit_dir / "transcripts"; out_dir.mkdir(parents=True, exist_ok=True)
    out_path, raw_path = out_dir / f"{video.stem}.json", out_dir / f"{video.stem}.openrouter.json"
    st = video.stat(); sig = hashlib.sha1(f"{video.resolve()}|{st.st_size}|{st.st_mtime}|{model}|{language}|{script}".encode()).hexdigest()
    t0 = time.time()
    if raw_path.is_file() and json.loads(raw_path.read_text()).get("signature") == sig:
        resp = json.loads(raw_path.read_text())["response"]; print("  cached model answer reused")
    else:
        api_key = key("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("OPENROUTER_API_KEY missing. Run the mehdiagent setup (never paste keys into a chat).")
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / "a.wav"; extract_wav(video, wav); data = wav.read_bytes()
        if len(data) > 25 * 1024 * 1024:
            raise SystemExit("Audio over ~13 min - split the video first (reels should be short).")
        print(f"  sending {len(data)/1e6:.1f} MB to {model} via OpenRouter…", flush=True)
        resp = ask(data, language, script, model, api_key)
        raw_path.write_text(json.dumps({"signature": sig, "response": resp}, ensure_ascii=False, indent=1))
    words = [{"text": str(w["text"]).strip(), "latin": w.get("latin", ""), "start": float(w.get("start", 0)),
              "end": float(w.get("end", w.get("start", 0))), "type": "word"} for w in resp.get("words", []) if str(w.get("text", "")).strip()]
    words = align_words(video, words)
    payload = {"provider": "openrouter", "model": model, "language": resp.get("language", language),
               "text": " ".join(w["text"] for w in words), "words": words}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    n_al = sum(w["timing"] == "aligner" for w in words)
    print(f"  saved: {out_path} in {time.time()-t0:.1f}s - {len(words)} words, {n_al} pinned by the aligner, {len(words)-n_al} rough")
    return out_path

def main() -> int:
    cfg = load()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video", type=Path, nargs="?")
    ap.add_argument("--edit-dir", type=Path, default=None)
    ap.add_argument("--language", default=cfg.get("speech_language"))
    ap.add_argument("--model", default=cfg.get("openrouter_model", "google/gemini-2.5-flash"))
    ap.add_argument("--script", default=cfg.get("caption_script", "latin"), choices=["latin", "arabic"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if not a.video:
        ap.error("video required")
    transcribe(a.video, a.edit_dir or a.video.parent / "edit", a.language, a.model, a.script)
    return 0

if __name__ == "__main__":
    sys.exit(main())
