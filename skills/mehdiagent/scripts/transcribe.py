"""One entry point for both reel styles: transcribe with the provider the creator picked during setup.

    python3 ~/.claude/skills/mehdiagent/scripts/transcribe.py <video> [--edit-dir edit] [--language xx] [--provider fish|openrouter]

Writes <edit_dir>/transcripts/<stem>.json = {"words":[{"text","start","end","type":"word",...}], ...} for either provider.
- fish:       Fish Audio transcribe-1 (word times from Fish; best on English and many languages).
- openrouter: Gemini 2.5 via OpenRouter + local forced alignment (best when captions use another script, e.g. Darija
              in Arabic letters with English terms - it also writes the Latin sound-spellings the aligner needs).
"""
import argparse, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from settings import load  # noqa: E402

cfg = load()
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--edit-dir"); ap.add_argument("--language")
ap.add_argument("--provider", default=cfg.get("transcriber", "fish"), choices=["fish", "openrouter"])
a, rest = ap.parse_known_args()
lang = a.language or cfg.get("speech_language")
cmd = [sys.executable, str(HERE / ("transcribe_fish.py" if a.provider == "fish" else "transcribe_openrouter.py")), a.video]
if a.edit_dir: cmd += ["--edit-dir", a.edit_dir]
if lang and a.provider == "fish":
    lang = lang.split("-")[0]          # Fish wants an ISO code: ar-darija -> ar
if lang: cmd += ["--language", lang]
sys.exit(subprocess.call(cmd + rest))
