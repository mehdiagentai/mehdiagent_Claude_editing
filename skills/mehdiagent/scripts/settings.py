"""mehdiagent settings: the creator's choices (config.json) and their API keys (.env), both in ~/.mehdiagent/.

Keys never live in the repo or in a skill folder. Nothing here prints a key: `check` shows only which keys are set.

    python3 settings.py show                 # print config.json (keys are never in it)
    python3 settings.py get style
    python3 settings.py set style dark       # values are parsed as JSON when possible (true, 3, "x")
    python3 settings.py check                # which keys exist (masked) + whether onboarding is done
    python3 settings.py env-path             # path of the .env file to open in an editor
    python3 settings.py init-env             # create .env from the template (chmod 600) if missing
"""
from __future__ import annotations
import json, os, stat, sys
from pathlib import Path

HOME = Path(os.environ.get("MEHDIAGENT_HOME", Path.home() / ".mehdiagent")).expanduser()
CONFIG = HOME / "config.json"
ENV = HOME / ".env"
KEYS = {
    "FISH_API_KEY": "Fish Audio - transcription (fish.audio > API keys)",
    "OPENROUTER_API_KEY": "OpenRouter - Gemini 2.5 transcription (openrouter.ai/keys)",
}
DEFAULTS = {
    "version": 1,
    "onboarded": False,
    "creator_name": "",
    "style": "ask",                     # dark | white | ask
    "speech_language": "en",            # what the creator speaks: en, ar-darija, fr, es, ...
    "caption_script": "latin",          # latin | arabic
    "caption_direction": "ltr",         # ltr | rtl (rtl = whole line right-to-left, English words included)
    "keep_english_terms": True,         # keep tech words (AI, data, campaign...) in Latin inside non-Latin captions
    "transcriber": "fish",              # fish | openrouter
    "openrouter_model": "google/gemini-2.5-flash",
    "footage": "precut",                # precut (creator already cut it) | raw (pick takes, cut silences)
    "layout": "face",                   # dark style: face = creator always on screen (graphics top, captions middle, creator bottom) | classic = alternate full-screen and split beats
    "background_removal": True,         # macOS only (Apple Vision)
    "music": None,                      # null = no music, or a path to the creator's own track
    "broll": "none",                    # none | higgsfield | own
    "cta_keyword": "",                  # default comment keyword, e.g. GUIDE
    "demo_brand": "Acme.ai",             # fictional brand used on demo screens
    "hero_tool": "Claude",              # the tool the reels usually show
    "projects_dir": "~/Desktop/reels",
}
ENV_TEMPLATE = """# mehdiagent API keys - this file stays on your computer (chmod 600). Never paste keys into a chat.
# Fill in ONLY the one you chose during setup, save, close.
FISH_API_KEY=
OPENROUTER_API_KEY=
"""

def load() -> dict:
    cfg = dict(DEFAULTS)
    if CONFIG.is_file():
        cfg.update(json.loads(CONFIG.read_text()))
    return cfg

def save(cfg: dict) -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")

def key(name: str) -> str:
    """Environment first, then ~/.mehdiagent/.env, then a .env in the working folder. Parsed, never executed."""
    if os.environ.get(name, "").strip():
        return os.environ[name].strip()
    for path in (ENV, Path.cwd() / ".env"):
        if path.is_file():
            for line in path.read_text().splitlines():
                k, sep, v = line.strip().removeprefix("export ").partition("=")
                if sep and k.strip() == name and v.strip().strip('"').strip("'"):
                    return v.strip().strip('"').strip("'")
    return ""

def init_env() -> Path:
    HOME.mkdir(parents=True, exist_ok=True)
    if not ENV.exists():
        ENV.write_text(ENV_TEMPLATE)
    ENV.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return ENV

def _parse(v: str):
    try:
        return json.loads(v)
    except ValueError:
        return v

def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "show"
    cfg = load()
    if cmd == "show":
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
    elif cmd == "get":
        print(json.dumps(cfg.get(argv[1]), ensure_ascii=False))
    elif cmd == "set":
        cfg[argv[1]] = _parse(" ".join(argv[2:])); save(cfg); print(f"{argv[1]} = {cfg[argv[1]]!r}")
    elif cmd == "check":
        print(f"config: {CONFIG} ({'onboarded' if cfg.get('onboarded') else 'NOT onboarded - run the mehdiagent setup'})")
        for k, label in KEYS.items():
            v = key(k)
            print(f"  {k:20s} {'set (' + str(len(v)) + ' chars)' if v else 'missing'}   {label}")
    elif cmd == "env-path":
        print(ENV)
    elif cmd == "init-env":
        print(init_env())
    else:
        print(__doc__); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
