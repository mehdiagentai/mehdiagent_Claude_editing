# Dark style — visual and sound contract

## Colour tokens (`template/draw.py`) — never use literal light colours

| role | token / value |
|---|---|
| ground | `BG` `#0A0A0B` near-black |
| card / panel | `CARD` `#1C1C1E` + 2 px hairline `HAIR` `(255,255,255,26)` (the hairline is what separates dark cards) |
| raised surface, pills, rows, controls | `CARD2` `#2C2C2E` |
| primary / secondary text | `INK` `#F5F5F7` / `GRAY` `#98989D` |
| separators, axes | `LINE` `#38383A` |
| blue / green / red / yellow | `#0A84FF` / `#30D158` / `#FF453A` / `#FFD60A` (Apple dark system colours) |
| hero accent | `TERRA` `#D97757` (Claude terracotta) |
| macOS / Safari chrome | `window()`: `#2A2A2C` bar, `#3A3A3C` field, `#1E1E1E` body, traffic lights |
| unrevealed hero | `tile_q`: `#2C2C2E` squircle, white SF Pro Heavy "?", light ring |
| shadows | alpha 110, blur 22 (`shadow()`), always with the hairline |
| highlighter | `(255,214,10,70)` over light text, or a 6 px `YELLOW` underline sweep |
| drawn props (guns, scythes, launchers) | gunmetal `#3A3A40` / `#66666E` — pure black vanishes on the ground |

- Recreated products use **their own dark theme** when they have one (X dark, Instagram dark comments, GitHub dark,
  Safari dark). A product with no dark theme keeps its real light UI inside a dark window. Never invert a brand.
- White brand tiles stay white; dark tiles get the light ring (`brand._ring`).
- Translucent fills **and edges** go through `rr()` (it blends); raw `ImageDraw` with alpha punches see-through holes.
- Every preview sheet: nothing dark-on-dark, no white slab bigger than a brand tile.

## Canvas and layout

- 1080×1920, 30 fps. Scenes are drawn in the scene canvas, then `render.py` shifts graphics down `TOP_SHIFT=90` and
  fades them out above screen y 180 (Instagram covers the top). Never place anything important above scene y 100.
- **Face layout (default, `layout: face`):** every beat shows the creator. Graphics box on screen y 186–826: scene
  y 96–736 at 1:1 (author the card at scene (70,104), 940×≤620), or scene y 96–896 shrunk to 0.8 for beats listed in
  `FULL` (tall scenes). Cinematic captions centred on screen y 900 at 78 px. The creator cut out of their background,
  scaled `PRES_SCALE` (.62) and centred, head top at `HEAD_Y` (985), body running off the bottom; the sides of the
  source frame are feathered so arms never end in a hard line. No-face beats (screen recordings) render as full beats.
- **Split beats (classic):** graphics panel 940×≤620 at scene (70,104); the creator below the split line (screen y 858, crop
  1080×1062 from `CROP_Y`); caption chip centred on the split line.
- **Full beats (classic, and no-face beats):** UI in the upper area (scene y 110–900), cinematic caption centred around scene y 980–1150, nothing
  below it.
- Type (`fonts.py`): SF Pro / Inter for UI, New York / Source Serif 4 for editorial serif, SF Mono / JetBrains Mono for
  code, SF Arabic / Noto Sans Arabic for Arabic (Apple fonts on macOS, bundled open fonts elsewhere).
  Display words are drawn as one string with an anchor, never letter by letter.

## Motion

- Entrances 220–350 ms (`spring()`, `ease()`), children staggered 50–120 ms; springs ≤ 0.3 s.
- A cue that lands on a word leads it by ~0.13 s (impacts/shots 0.05 s); free falls are timed to land on the word.
- Nothing still for more than 0.6 s: build, hover, sweep (`sweep()` light band), pulse, pile up, slow push-in.
- Cursor: `pointer_motion.motion` — approach, settle, one press, release; arrive 2–3 frames early; picks ≥ 0.4 s apart.
- Signature move: **recreated real page → camera push-in (0.6 s `smooth()`) → live count-up landing on the spoken
  number with a frame (green hero / red rival) → yellow highlighter sweep on the exact row**, cursor on the tip.
- Reveal: "?" tile → horizontal flip (`|cos|` over 0.22 s) ending exactly on the spoken name → real tile.
- Cards grow when a second row arrives; a waiting tile sits centred and slides aside when its partner lands.
- Hook: big (tiles ≥ 280 px), physical, already moving on frame 0; one hit per stressed word, the last hit breaks the
  target (shards under gravity, 2-frame camera kick).

## Captions

- Full beats: cinematic words (`helpers/ar_caption.py`), 110–120 px, each word pops in on its own onset (0.96→1.0 over
  3 frames) and never re-animates; groups set per beat in `render.OVERRIDE` (`hl` colours one word, `big` + `color`
  for the payoff — green for the hero's win). Right-to-left languages run the whole line right-to-left, English words
  included, unless the creator chose otherwise.
- Face beats: the same cinematic words at 78 px, centred between the graphics and the creator (screen y 900).
- Split beats (classic): a chip on the split line (`#1C1C1E`, `#3A3A3C` edge), 44 px, up to 4 words per group.
- No word stamps or labels over a scene (GONE, DONE, NEW, FREE, WOW, banners) — the animation shows it.

## Sound (`template/audio/sources`, synthesized by `make_sfx.py`)

| cue | file | level |
|---|---|---|
| first/last word of every full-screen caption group | `caption-click.wav` | −25 dB hook, −27 dB after |
| slash, camera move, transition, flip | `whoosh.wav` | −22 (slash) … −31 dB |
| tile/prop landing, impact | `thud.wav` | −18 … −25 dB |
| chip, emoji, reveal, frame, check | `pop.wav` | −26 … −33 dB |
| toggle, Post, Enter, file drop | `click.wav` | −26 dB |

Voice is normalised to −16 LUFS; the mix is limited (`alimiter=limit=.68`) so the final MP4's true peak stays below
−1 dBFS — measure it on the MP4 (`ebur128=peak=true`), not the WAV. Music only from the creator's own track
(`music` setting), −29 LUFS under the voice with sidechain ducking.
