# Reel style + schema catalog

## Reference reels (the style to replicate)

Shared DNA: talking-head at the bottom, glass schemas in the upper half, one-word karaoke subtitles, ONE accent per video, graphics ALMOST always present that change every ~2-3s, count-up on numbers, graphs that draw themselves.

**Themeable palette (ONE accent per video):** Default green #2fe081 (default) · Claude orange #f0813f / bright #ffa766 (Claude/GLM content) · red #ff5a5a (expensive/lost) · steel #7f93ad (neutral competitor). Set it at the top of gen.py.

## Schema catalog (types in gen.py)
- **intro**: a plane (✈) flying along a dashed arc that draws itself (MotionPathPlugin) + an elegant title. For hooks.
- **statgraph**: large number with count-up (e.g. 0→340+) + unit + sparkline. For "hundreds of leads".
- **summary**: eyebrow + large keyword (e.g. "THOUSANDS OF €"). A summary sentence, NOT a paragraph.
- **graph**: just a line graph that draws itself, down+red (loss) or up+green (growth).
- **crm**: contact rows (avatar + name + detail + "STALLED" tag), entering in stagger. Up to 5 rows.
- **listcheck**: rows with a checkmark ✓ that enter on the trigger words.
- **calendar**: calendar grid with one day highlighted green. NO red "elsewhere" arrow.
- **comstep**: "BY HAND" list with a red struck-through ✕, items entering ONE PER WORD (step-by-step synced), then an "IMPOSSIBLE" stamp.
- **iphone**: reveal of the real product screenshot (`assets/iphone_phone.png`) + a "POWERED BY" logo row. For the product moment.
- **wachat**: dark WhatsApp chat (header with WhatsApp logo + name + "online", in/out WA-style bubbles, ✓✓), bubbles entering on the words.
- **msgtpl**: a single WhatsApp bubble with a template message and the placeholders highlighted in green, e.g. "Hi [Marco]! You'd been to [Bali]... let me suggest [the Philippines]".
- **vflow**: 3 boxes stacked VERTICALLY (top→bottom) with ↓ arrows (e.g. CONTACTS → AGENT → CLIENTS).
- **cta**: green-bordered card with a keyword + a meter bar that fills up.

## Animations
- Snappy entrances (0.15-0.25s, ease back.out/power3.out). NEVER a pulsing loop on the boxes.
- Graphs/sparklines: stroke-dashoffset 760→0 in ~1s.
- Count-up: tween on a proxy {v} with onUpdate → textContent.
- Decorative (always on, deterministic loops on a scrubbed timeline): particles y-drift + opacity, streaks x-translate, glow scale/move, grid background-position.

## Music + audio mix
the creator's own track (`music` setting; none is bundled). Default: from second 0:04 of the track, from the start of the short, final fade-out (see compose.sh). This is the default background track — swap it for your own with the MUSIC env var.
**The voice must DOMINATE**: compose.sh normalizes the voice to dialogue level (loudnorm I=-16) and keeps the music LOW (volume 0.06, override with `MUSIC_VOL=`). The old default 0.15 = too high, it drowned out the voice.
