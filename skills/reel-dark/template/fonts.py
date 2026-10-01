"""Font + emoji resolver: Apple's system fonts on macOS, bundled open fonts everywhere else.

macOS                       other systems (or MEHDIAGENT_PORTABLE=1 on a Mac to preview them)
SF Pro            (sans)    Inter              assets/fonts/Inter.ttf            OFL
SF Mono           (mono)    JetBrains Mono     assets/fonts/JetBrainsMono.ttf    OFL
New York          (serif)   Source Serif 4     assets/fonts/SourceSerif4.ttf     OFL
SF Arabic         (arabic)  Noto Sans Arabic   assets/fonts/NotoSansArabic.ttf   OFL
Apple Color Emoji (emoji)   Noto Color Emoji   ~/.mehdiagent/fonts/NotoColorEmoji.ttf (downloaded once, OFL)

Weights use Apple's names everywhere (Regular, Medium, Semibold, Bold, Heavy, …); they are mapped to each font's own.
"""
import os, platform, subprocess
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
APPLE = platform.system() == "Darwin" and os.environ.get("MEHDIAGENT_PORTABLE") != "1"
SYS = "/System/Library/Fonts/"
FILES = {
    "sans":   (SYS + "SFNS.ttf",        HERE / "assets/fonts/Inter.ttf"),
    "mono":   (SYS + "SFNSMono.ttf",    HERE / "assets/fonts/JetBrainsMono.ttf"),
    "serif":  (SYS + "NewYork.ttf",     HERE / "assets/fonts/SourceSerif4.ttf"),
    "arabic": (SYS + "SFArabic.ttf",    HERE / "assets/fonts/NotoSansArabic.ttf"),
}
EMOJI_URLS = ["https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/fonts/NotoColorEmoji.ttf",
              "https://raw.githubusercontent.com/google/fonts/main/ofl/notocoloremoji/NotoColorEmoji-Regular.ttf"]
EMOJI_PATH = Path.home() / ".mehdiagent/fonts/NotoColorEmoji.ttf"
ALIASES = {  # Apple name -> names other variable fonts use, best first
    "Ultralight": ["ExtraLight", "Thin"], "Thin": ["Thin", "ExtraLight"], "Light": ["Light"], "Regular": ["Regular"],
    "Medium": ["Medium"], "Semibold": ["SemiBold", "Bold"], "Bold": ["Bold"], "Heavy": ["ExtraBold", "Black", "Bold"],
    "Black": ["Black", "ExtraBold", "Bold"],
}

def path(kind: str) -> str:
    apple, bundled = FILES[kind]
    return apple if APPLE and os.path.exists(apple) else str(bundled)

@lru_cache(None)
def font(kind: str, size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(path(kind), int(size))
    try:
        names = [n.decode() if isinstance(n, bytes) else n for n in f.get_variation_names()]
    except Exception:
        return f                                   # static font: no weights to set
    for cand in [weight] + ALIASES.get(weight, []):
        if cand in names:
            f.set_variation_by_name(cand); break
    return f

def emoji_font() -> tuple:
    """(path, native pixel size) of the colour-emoji font. Downloads Noto Color Emoji once on non-Apple systems."""
    if APPLE:
        return SYS + "Apple Color Emoji.ttc", 160
    if not EMOJI_PATH.is_file():
        EMOJI_PATH.parent.mkdir(parents=True, exist_ok=True)
        print("  downloading Noto Color Emoji (~10 MB, once)…", flush=True)
        tmp = EMOJI_PATH.with_suffix(".part")
        for url in EMOJI_URLS:                      # Google has moved this file before: try each known location
            if subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", str(tmp), url]).returncode == 0:
                tmp.rename(EMOJI_PATH); break
        else:
            raise RuntimeError("Could not download Noto Color Emoji - put NotoColorEmoji.ttf in " + str(EMOJI_PATH.parent))
    return str(EMOJI_PATH), 109                     # Noto Color Emoji is a CBDT bitmap font with 109 px strikes
