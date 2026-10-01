---
name: reel-dark
description: mehdiagent DARK style - edit a talking-head video into a 9:16 dark-mode reel (near-black ground, Apple dark colours, recreated app UI with no screenshots, physical no-face hook, cinematic captions in any language incl. right-to-left Arabic, speaker cut out of their background, sound design). Use when the mehdiagent skill routes a video here, or the user asks for "the dark style", "dark reel", "black style", or a revision of a dark reel ("remove the part where I say…", "make X full screen", "show Y instead of Z"). Run the mehdiagent setup first if ~/.mehdiagent/config.json is missing.
argument-hint: [video file, or the revision you want on the current reel]
---

# Reel Dark

You build 1080×1920 30 fps reels from the creator's video with fully recreated, Apple-styled product UI **in dark
mode** (colour tokens at the top of `style.md`) and a fast revision loop. Every claim about the output is verified
from decoded frames and signal checks; never say you listened.

`$M` = `~/.claude/skills/mehdiagent/scripts`, `$K` = `~/.claude/skills/reel-dark`.
**Settings first:** `python3 $M/settings.py show`. If not onboarded, run the `mehdiagent` setup. The settings decide
language, caption script/direction, transcriber, footage type, background removal, music, CTA keyword, demo brand
(default **Acme.ai**) and hero tool (default **Claude**). They override every default below.
Runs on macOS, Windows and Linux. On a Mac it uses Apple's SF fonts, Apple Color Emoji and Apple Vision for the cut-out;
elsewhere it uses the bundled open fonts (Inter, Noto Sans Arabic, JetBrains Mono, Source Serif 4), Noto Color Emoji
and rembg (see `template/fonts.py`, `helpers/personmask_rembg.py`). `MEHDIAGENT_PORTABLE=1` previews that mode on a Mac.

Read `style.md` (visual + sound contract) before authoring, and `revisions.md` before any revision.

## Process — one pre-cut video (`footage: precut`, the default)

Full recipe with every command: `references/workflow-single-video.md`. Short version:
1. `bash $K/template/simple/setup.sh <video> <slug>` → project folder in `projects_dir`, template copied, cut-out
   mattes (`edit/mask_person.mkv`, `edit/mask_subject.mkv`), `edit/tight.mkv` and the transcript (`$M/transcribe.py`).
2. Read the transcript. Fix words (meaning, product names, numbers) in `prepare.py`, set `BEATS`, run it →
   `edit/transcript.json` + `edit/beats.json`. Fact-check every product name and claim on the live site first.
3. Beat map, `scenes.py` (start from `template/simple/scenes_example.py`), preview, render, mix, gates, deliver.

## Process — raw takes (`footage: raw`)

1. Two files (camera `.MP4` + screen-recorder `.mov` with the good mic) → `python3 align.py CAMERA.MP4 OBS.mov`
   builds `edit/master.mkv` (camera picture + mic voice) and `edit/teleprompter.jpg` (read it: it is the script).
   One file → `edit/master.mkv` is that file.
2. `python3 $M/transcribe.py edit/master.mkv --edit-dir edit/raw`. Pick the clean takes (last take of a line wins;
   drop spoken notes/false starts), write `build_cut.py`: one keep-range per beat, scan outward from the word edges to the RMS trough (outward edge scan,
   fixed 70/100 ms pads, hook 1.12× with pitch kept, 0.22 s ring-out on the CTA). Split one take into two beats at a
   breath ≥ 0.3 s. Only tighten gaps the 10 ms RMS confirms. Output `edit/tight.mkv`, `edit/edl.json`.
3. Re-transcribe the cut (`--edit-dir edit/final-timing`), run `scripts/splice_audit.py edit/edl.json edit/tight.mkv`
   (every join must read as the intended sentence), then continue as for a pre-cut video from step 2.

## Building the reel (both paths)

- **Beat map first.** One row per spoken beat: mode (full/split), surface, action, payoff. ~10–13 beats per 30–35 s,
  alternate full screen and split (graphics top, creator bottom) at meaningful lines: full for the hook, hero object,
  numbers, real pages, the reveal; the face for reactions, the name and the CTA. Build an arc: mystery ("?" tile) →
  tease → reveal (tile flips on the name) → proof → honest caveat → fix → CTA. Mark 1–3 *feeling* lines for a meme
  (`references/memes.md`).
- **Write `scenes.py`.** Recreate every UI with Pillow (`window()`, `apptile()`, `panel()`, `sf()`, real brand PNGs
  in `assets/icons`). No screenshots. Translucent fills/edges through `rr()`.
- **Preview before rendering.** `python3 render.py --preview` (contact sheet), `--strip <beat> t1,t2,…`,
  `python3 gridstrip.py <tag> beatA,beatB 6`, `python3 strips.py <beat> t0 t1 12` for choreography. Read the images.
  Smoke-test the first/middle/last frame of every beat before a full render.
- **Render, mix, verify.** `python3 render.py && python3 mix.py` in the background (wait on
  `grep -qE "^mixed|Traceback" renders/render.log`), then `check_frames.py` (no blank frame, zero ink in the top
  180 px, nothing under the cinematic words), `check_motion.py` (no beat still > 0.6 s), `check_air.py` (raw path),
  true peak < −1 dBFS on the MP4 (`ebur128=peak=true`). With background removal on, sample 8 split frames and look at
  hair, glasses, hands and held props: no room pixels. Fix and re-render until all pass.
- **Deliver** with `SendUserFile`; list the caption script with uncertain words flagged; offer a README + zip.

## Scene recipes (build them in `scenes.py`; `template/simple/scenes_example.py` shows most of them working)

- **Physical hook:** the hero tile (the "?" until named) does something to the target on stressed words — a scythe
  splitting cards (`props.scythe` + `props.split_halves`, as in the example), a projectile firing at a rival's
  official icon, a tile crushing/eating/unplugging another. One hit per stressed word, the last hit breaks it.
- **Real page → push-in → count-up → highlighter:** rebuild the page from its live copy, camera push-in, the spoken
  number counts up and lands with a frame, a yellow highlighter sweeps the exact row, cursor on the tip.
- **App rebuilds:** Ads Manager tables, Business Manager, Instagram comments + DM banner (`helpers/instagram_comment`),
  chat windows, Safari pages, Claude/ChatGPT apps — recreated with `window()`, `panel()`, real icons.
- **Literal props:** MacBook (drawn) for "local / on your computer", a balance scale for comparisons, a calendar that
  lights day by day for durations, a money bag + hourglass for "saves time and money", a stopwatch for "fast".
- **Diagrams that move:** curved connectors drawn progressively, bars on a shared axis, gauges, a training curve,
  split-flap counters for big spoken amounts, a country's real outline from GeoJSON (`assets/geo`) with icons on cities.
- **Figures:** Fluent 3D emoji tiles (`brand.tile_fluent`) and official app icons (`brand.tile_app`) — never drawn people.

## Critical rules

0. **Dark mode, always.** Ground `#0A0A0B`, cards `#1C1C1E` with a hairline edge, light text, Apple dark system colours,
   products in their own dark theme. Use the tokens in `draw.py`; see `style.md`.
   Check every preview sheet for dark-on-dark elements.
1. Recreate UI; never screenshot. Real icons, Apple chrome, product-true colours and copy.
2. The hook is no-face and physical, big (tiles ≥ 280 px, cards ≥ 600 px wide), something moving on frame 0. If the
   creator describes a hook, build exactly that.
3. Caption click sound on the first and last word of every full-screen caption group; presenter chips stay silent.
4. Full-screen beats: UI in the upper area, cinematic words centred around scene y≈980–1150, nothing below. Graphics
   are shifted down `TOP_SHIFT=90` and faded above screen y 180 (`render.fade_top`) — Instagram covers the top.
5. Each beat a distinct surface; never replay a screen for another line.
6. Cues that land on a word lead it by ~0.13 s (shots/impacts 0.05 s); springs ≤ 0.3 s.
7. Nothing static for more than ~0.6 s inside a beat: build, select, hover, sweep, pile up.
8. Never retime the voice to fit graphics; retime graphics to word onsets via `at(beat, word)`.
9. Voice edits follow `revisions.md` and get a splice audit.
10. Report honestly: checks are signal- and frame-based.
11. Display words are drawn as one string (`ImageDraw.text(..., anchor=...)`), never letter by letter with tracking.
12. Row text is centred on the row's centre line (`anchor='lm'`); strike-throughs go through the x-height middle.
13. Raw-takes hook: voice ~1.12× (`atempo`, pitch kept), no air between list items, exact trough times at joins.
14. Captions: break before each named item; the payoff gets its own group, larger and green (`big`, `color`);
    highlight single key words with `hl`. Right-to-left languages: whole line RTL, English terms included
    (`helpers/ar_caption.py`), unless the settings say otherwise.
15. Music only if the creator gave a track (`music` setting). Never download music they didn't provide.
16. **Fact-check before you draw.** Product names, numbers and claims come from the live site/repo, never from memory.
    If the creator said a name wrong: keep the voice, show the truth, flag it first in the report.
17. **Every number on screen is spoken or sourced.** Spoken numbers count up and land on their word with a frame (red
    rival, green hero). No invented benchmarks, badges or percentages — use bars, sparklines, skeleton rows instead.
18. **No empty halves.** A card that will get a second row starts small and grows; a waiting tile sits centred and
    slides aside when its partner lands. No placeholder outlines.
19. **Keep the hero tool a mystery ("?" tile) until its name is spoken**, flip to the real mark exactly on the name.
20. **Literal objects for literal words:** "local" → MacBook; "cloud" → a packet on a route; "faster" → a race or
    gauge; "trained" → a curve; "cut a campaign" → a scythe through it; "comment X" → the comment UI typing and
    posting X (no link chip under it — the link goes in the DM).
21. **Never draw people.** People, professions and props come from icons: Apple Color Emoji (native 160 px, never
    upscaled), Microsoft Fluent 3D emoji (`assets/icons/fluent`, MIT; more at
    `raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/<Name>/3D/…png`), official app icons via the iTunes
    Search API (`artworkUrl512`). The hero tile is the only character you draw.
22. A named country gets its real outline from GeoJSON, and something happens on it on the word.
23. Shell game = the hero tile in 🎩 with two terracotta arms; the money is under the hat.
24. No grey sub-line under a row title or card headline; one line per row.
25. A question / thinking beat = the Apple 🤔 (`brand.emoji('🤔')`, native 160 px), rocking and hopping on the question word.
26. Dismissed props are thrown away one per stressed word, ≈0.9 s apart.
27. Nothing grows off the top of a card; size cards so the tallest element stays inside.
28. Choreography spanning two beats is one function called with continued time — no re-entry, no flicker.
29. One to three memes per reel, on feeling lines only (`references/memes.md`), never on a proof beat.
30. The hero's gestures (pointing, fist) are drawn in its colour, never emoji hands.
31. Photo people hold their props (sleeves to the grips); diagram connectors are curves.
32. **No stamp/label overlays.** Never slam a word over a scene to announce what happened (GONE, DONE, NEW, FREE, WOW,
    rubber stamps, banners). The caption carries the word; the animation shows it. Allowed: text that is part of a
    recreated real interface and spoken/sourced numbers. Remove a stamp's sound cue with it.

## Template entry points

- `template/simple/` — the pre-cut pipeline: `setup.sh`, `prepare.py`, `render.py` (cut-out matte, RTL/LTR captions,
  safe-top fade), `mix.py` (SFX cue sheet, optional music), `scenes_example.py`.
- `template/` root — `draw.py` (tokens + primitives), `brand.py` (tiles: official icons, Fluent figures, emoji, "?"), `helpers/props.py` (scythe, gradients, card split),
  `align.py` (two-file master), gates (`check_frames.py`, `check_motion.py`, `check_air.py`, `check_provenance.py`),
  review sheets (`gridstrip.py`, `strips.py`), `helpers/` (`personmask.swift`, `ar_caption.py`, `instagram_comment.py`,
  `pointer_motion.py`, `gif_frames.py`), `audio/sources/` SFX (synthesized by `audio/make_sfx.py`).

If the request is a revision, do only that revision, re-render, re-verify, re-send, and keep the previous cut.
