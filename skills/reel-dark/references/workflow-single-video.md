# Dark style — one pre-cut video (the default path)

The creator sends ONE video they already cut (phone or camera, any aspect; audio inside). You never pick takes and
never cut their words. Their settings (`~/.mehdiagent/config.json`) say the language, caption script and direction,
transcriber, background removal, music, CTA keyword, demo brand and hero tool.

Reference project: `template/simple/scenes_example.py` — a 34.6 s reel in Moroccan Darija with Arabic right-to-left
captions (English terms kept in Latin), background removed, no music: 11 beats, F S F S F S F S F F S.

## Steps

1. **Setup** — `bash ~/.claude/skills/reel-dark/template/simple/setup.sh <video> <slug>` (≈3–5 min). Builds
   `<projects_dir>/<date>-<slug>/`: template files, `edit/tight.mkv` (1080×1920, 30 fps, PCM), the cut-out mattes
   `edit/mask_person.mkv` + `edit/mask_subject.mkv` (if `background_removal`), and `edit/transcripts/tight.json`. It ends by
   printing every word with its index. Say "background removal is on" to the creator when it is.
2. **Fix the words** in `prepare.py` → `FIX`:
   - Gemini/OpenRouter transcripts are usually right already: fix product names, numbers and the odd mishearing.
   - Fish on a non-Latin language (e.g. Darija) returns rough spellings. Rewrite every word in the creator's caption
     script **with a Latin sound-spelling** (`"بزاف|bzaf"`, `"Claude|klod"`), split/merge with lists/tuples; the aligner
     then re-times them (tested: median 1 ms from hand-checked times). Typical Fish Darija mishearings: "بالزيف" = بزاف,
     "حش" = حيت, "مشان" = باش/ملي, "كلمةش" = كلمة + the keyword, "بجليق" = ب + Claude.
   - Fact-check every product name and claim on the live site before drawing.
   Run `python3 prepare.py` until the word list reads right; words the aligner scored 0 keep their rough time — pin
   them in `MANUAL` from an RMS plot (loudness envelope with word marks) if a graphic lands on them.
3. **Beats** — set `BEATS` (name, first word index), run `python3 prepare.py` again: it prints each beat with
   beat-local word onsets. ~11 beats per 35 s. Face layout (default): the creator is under every beat, no-face footage
   goes full screen by itself; classic layout: alternate full (graphics only) and split (graphics + creator).
4. **Scenes** — design the hook for THIS video first (`~/.claude/skills/mehdiagent/references/hooks.md`, check
   `hooks.py recent`; the example's scythe is not a default), then rewrite `scenes.py`: one function per beat, landings from `at(beat, word)`, the hero
   tool as the "?" tile until its name is spoken. Every rule in SKILL.md and `style.md` applies.
5. **render.py** — face layout: set `FULL` (beats whose scenes use the tall area, shrunk to fit the top box),
   `OVERRIDE`, and if needed `PRES_SCALE` (creator size) / `HEAD_Y` (head position); it prints which beats had no face
   and went full screen (`edit/face.json`). Classic layout: set `FULL` (full-screen beats), `CAPY` (caption centre per full beat), `OVERRIDE` (caption group
   sizes per full beat; `hl` = colour one word, `big`/`color` = payoff), `CROP_Y` (top of the presenter crop on the
   1080×1920 frame — hair just under the caption chip; check the preview). Preview:
   `python3 render.py --preview`, `python3 render.py --strip <beat> t1,t2,…`. Read every sheet.
6. **mix.py** — rewrite the cue block for the new scenes (caption clicks are automatic). Music only if the settings
   name a track.
7. **Render + gates** — `python3 render.py && python3 mix.py` (background, ~6 min); `check_frames.py`,
   `check_motion.py`, true peak (`ffmpeg -i renders/FINAL-*.mp4 -af ebur128=peak=true -f null -`). Then sample 8 split
   frames from the FINAL and look at the cut-out (hair, glasses, hands, held props): no room pixels.
8. **Deliver** — record the hook (`hooks.py add …`), `SendUserFile` the MP4; list the caption lines with every uncertain word flagged; offer README + zip.

## How the pieces work

- **Cut-out**: macOS → `helpers/personmask.swift` (Apple Vision, nothing downloaded); Windows/Linux →
  `helpers/personmask_rembg.py` (rembg u2net_human_seg in `~/.mehdiagent/venv-rembg`, writes the same two files). `person` = person segmentation (soft hair,
  can leak furniture), `subject` = foreground instance mask (no leaks, keeps a held mic, jagged edges).
  `render.matte()` = min(person, subject grown ~24 px and feathered) ** 1.15. AVFoundation can't read `.mkv` — setup
  feeds it an `.mp4` copy of the edit master so mattes and picture line up exactly.
- **Captions**: `helpers/ar_caption.py`. This Pillow has no raqm → `arabic_reshaper` + per-word glyph reversal, words
  laid out by hand (`rtl` from `caption_direction`). The Arabic font has no Latin glyphs → Latin words use the sans font (`fonts.py`).
  `render.at()` keeps non-Latin letters when matching words.
- **Safe top**: `render.fade_top()` fades graphics to the ground between screen y 180–216 (falling tiles and swung
  props otherwise put ink where Instagram's UI sits; `check_frames` requires zero ink above y 180).
- **Python certificates**: python.org builds without certifi make `torch.hub` downloads fail; `align_latin.ensure_model`
  downloads the aligner with `curl` instead (never disable verification).
