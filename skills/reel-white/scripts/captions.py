#!/usr/bin/env python3
"""Generate karaoke subtitles (one word at a time) as a transparent PNG sequence.
Fixed style: Montserrat Black, white, UPPERCASE, one word, positioned at the edge with the video.
NO hard black outline (stroke) but a soft blurred SHADOW: invisible on black, readable
over bright B-roll (lesson: a white subtitle over a bright screen-recording disappeared).
Usage: python captions.py <cut_transcript.json> <out_dir> [fps=12] [size=100]
The times are ALREADY in the output timeline (ALWAYS transcribe the already-cut video).
NB: the transcriber mangles proper nouns / tech terms. Typos seen before, to patch in the
    caption JSON (the "text" field, times do NOT change): "Cloud"->"Claude", etc.
    BEFORE generating the subtitles, patch those errors in the JSON (substring replace on the
    "text" field of each word) and pass the CORRECTED transcript here. The card triggers in
    gen.py stay anchored to the ORIGINAL transcript (the word times don't change)."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TRANSCRIPT, OUT = sys.argv[1], sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else 100   # 100 default; raise/lower to taste
W, H, CY = 1080, 1920, 700   # CY + overlay y=78 in compose => word sits at the video edge
# Font resolution: prefer the copy bundled with this skill, then the user's font folders.
def _find_font():
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [
        os.path.join(here, "..", "assets", "fonts", "Montserrat-VariableFont_wght.ttf"),
        os.path.expanduser("~/Library/Fonts/Montserrat-VariableFont_wght.ttf"),
        os.path.expanduser("~/.fonts/Montserrat-VariableFont_wght.ttf"),
        "/usr/share/fonts/truetype/montserrat/Montserrat-VariableFont_wght.ttf",
    ]
    env = os.environ.get("CAPTION_FONT")
    if env:
        cands.insert(0, env)
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit("Montserrat font not found. Set CAPTION_FONT=/path/to/Montserrat.ttf "
                     "or keep assets/fonts/Montserrat-VariableFont_wght.ttf in the skill.")
FONT = _find_font()

os.makedirs(OUT, exist_ok=True)
d = json.load(open(TRANSCRIPT))
ws = [w for w in d["words"] if w.get("type") != "spacing" and w.get("start") is not None]
ents = []
for i, w in enumerate(ws):
    a = w["start"]; nxt = ws[i+1]["start"] if i+1 < len(ws) else a+0.4
    b = min(nxt, a+1.0); b = b if b > a else a+0.12
    # user feedback: no trailing punctuation on karaoke words ("SKILL," -> "SKILL")
    ents.append((a, b, w["text"].strip().upper().rstrip(",.;:!?")))

def font(sz):
    f = ImageFont.truetype(FONT, sz)
    try: f.set_variation_by_axes([900])   # Black
    except Exception: pass
    return f
F = font(SIZE)
total = ws[-1]["end"] + 0.3
n = int(total*FPS)
for i in range(n):
    t = i/FPS; word = next((txt for a, b, txt in ents if a <= t < b), None)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if word:
        dr = ImageDraw.Draw(img); bb = dr.textbbox((0, 0), word, font=F); tw = bb[2]-bb[0]
        x = (W-tw)//2
        # SOFT shadow (no hard stroke): blurred semi-transparent black text -> readable halo
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        ds.text((x, CY+4), word, font=F, fill=(0, 0, 0, 180))
        ds.text((x, CY), word, font=F, fill=(0, 0, 0, 180))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9)))
        ImageDraw.Draw(img).text((x, CY), word, font=F, fill=(255, 255, 255, 255))   # clean white on top
    img.save(f"{OUT}/{i:05d}.png")
print(f"caption frames: {n} ({len(ents)} words) -> {OUT}")
