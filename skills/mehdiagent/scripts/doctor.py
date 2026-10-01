"""Check a computer is ready for mehdiagent reels. Prints OK / MISSING with the exact fix; changes nothing.

    python3 ~/.claude/skills/mehdiagent/scripts/doctor.py
"""
import importlib.util, platform, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings import load, key  # noqa: E402

cfg = load(); bad = 0
def row(ok, what, fix=""):
    global bad
    bad += 0 if ok else 1
    print(f"  {'OK     ' if ok else 'MISSING'}  {what}" + ("" if ok else f"\n           fix: {fix}"))

mac = platform.system() == "Darwin"
print(f"mehdiagent doctor - {platform.system()} {platform.machine()}, Python {platform.python_version()}")
row(sys.version_info >= (3, 9), "Python 3.9+", "install Python from python.org")
row(bool(shutil.which("ffmpeg")), "ffmpeg", "macOS: brew install ffmpeg  |  Windows: winget install ffmpeg")
for mod, pkg in [("numpy", "numpy"), ("PIL", "pillow"), ("requests", "requests"), ("arabic_reshaper", "arabic-reshaper"),
                 ("torch", "torch"), ("torchaudio", "torchaudio")]:
    row(importlib.util.find_spec(mod) is not None, f"python package {pkg}", f"python3 -m pip install {pkg}")
style = cfg.get("style")
if style in ("dark", "ask") and cfg.get("background_removal"):
    if mac:
        row(bool(shutil.which("swiftc")), "Swift compiler (Apple Vision background removal)", "xcode-select --install")
    else:
        vpy = Path.home() / ".mehdiagent/venv-rembg" / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
        print(f"  {'OK     ' if vpy.exists() else 'LATER  '}  rembg background removal ({'installed' if vpy.exists() else 'installs itself on the first reel, ~2 min'})")
if style in ("white", "ask"):
    row(bool(shutil.which("npx")), "Node.js / npx (white style renders cards with hyperframes)", "install Node.js LTS from nodejs.org")
t = cfg.get("transcriber", "fish")
row(bool(key("FISH_API_KEY" if t == "fish" else "OPENROUTER_API_KEY")),
    f"{'Fish Audio' if t == 'fish' else 'OpenRouter'} API key", "run the mehdiagent setup and paste the key into ~/.mehdiagent/.env")
m = cfg.get("music")
if m:
    row(Path(str(m)).expanduser().is_file(), f"music track {m}", "python3 settings.py set music null  (or point to an existing file)")
row(bool(cfg.get("onboarded")), "first-run setup done", "in Claude Code type: /mehdiagent")
print("all good" if not bad else f"{bad} thing(s) to fix")
sys.exit(1 if bad else 0)
