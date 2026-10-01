# Memes in a reel (optional, 1–3 per reel)

A meme is a reaction shot for a line about a *feeling* the viewer shares. It replaces the recreated UI for that beat;
it never replaces a proof beat (numbers, real pages, the product).

| line type | meme job |
|---|---|
| "if you're like me…" / shared pain | grimace / cringe reaction |
| the payoff / "and boom" | celebration |
| disbelief ("how is that possible?") | jaw-drop / confused reaction |
| "think about it" | head-tap "use your brain" |
| a rival's failure | someone walking away / no-yes reaction |

- Lands on the *feeling word*, with something already moving on frame 0 of the beat.
- One card per beat, 940 px wide, 26 px corners, soft shadow, nothing inside the card. **Crop platform watermarks out.**
- If the creator names a GIF for a line ("show this only"), it fills the whole panel (cover-crop 940×560).
- Play the GIF at its own pace (`helpers/gif_frames.py` resamples to 30 fps); loop if the beat is longer.

## Finding one
1. **The creator's links first** (Giphy/Tenor/Pinterest URL): `curl -sL <url> -o assets/gif/<name>.gif`; a Giphy page
   becomes `https://media.giphy.com/media/<id>/giphy.gif`.
2. Otherwise search `https://giphy.com/search/<two-word feeling>` or `https://tenor.com/search/<phrase>-gifs` in the
   built-in browser and pick a recognisable reaction. Ask the creator before using clips from films/TV if they plan to
   monetise the reel.
3. Check frame ~10 (`python3 helpers/gif_frames.py assets/gif/x.gif --peek`): a face that reads at 760 px in 0.5 s,
   ≥ 400 px source, no burned-in caption.
