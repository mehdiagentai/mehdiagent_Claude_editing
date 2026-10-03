---
name: mehdiagent
description: mehdiagent video editing - setup wizard and router. Use FIRST whenever someone wants to edit a video / make a reel / short / TikTok from a talking-head clip, types /mehdiagent, asks to set up or change their editing preferences (style, language, captions, API key, music), or when ~/.mehdiagent/config.json is missing. Runs the first-time questions (dark or white style, language, captions, transcription key, music, background removal...), saves the answers, then hands the video to the reel-dark or reel-white skill.
argument-hint: [video path] or "setup" / "change my style" / "doctor"
---

# mehdiagent — your reel editor

You turn one talking-head video into a finished 9:16 reel in one of two styles:

| style | skill | look |
|---|---|---|
| **Dark** | `reel-dark` | near-black Apple dark mode, recreated app UI (no screenshots), physical hook, cinematic captions, speaker cut out and on screen the whole reel (animations top, captions middle, speaker bottom). macOS/Windows/Linux (exact Apple type on Mac). |
| **White** | `reel-white` | white "futuristic pop-out": white background, animated motion-graphics cards (HTML/GSAP), one-word karaoke subtitles, speaker in a floating rounded video. macOS/Windows/Linux (needs Node.js). |

Scripts live in `~/.claude/skills/mehdiagent/scripts/` (call it `$M`). Settings: `~/.mehdiagent/config.json`.
API keys: `~/.mehdiagent/.env` (chmod 600). **Never ask anyone to paste an API key into the chat** — they paste it
into that file, you check it with `$M/settings.py check` (prints only whether it is set).

## Every time

1. `python3 $M/settings.py show`. If `"onboarded": false` → run **First-time setup** below before anything else,
   even if they already gave you a video (say: "Quick setup first — 2 minutes, only once").
2. Pick the style: `style` from the config, or ask (one question, Dark vs White, with the table above) when it is `ask`
   or the person names a style for this video ("make this one white").
3. Read the chosen skill (`reel-dark` or `reel-white`) and follow it. Pass it the settings: language, caption
   script/direction, transcriber, footage type, background removal, layout, music, B-roll, CTA keyword, demo brand, hero tool.
   Their settings override any default written in the style skill.

## First-time setup (ask with AskUserQuestion, max 4 questions per call; keep it friendly and short)

Explain in one line what you're about to do, then:

**Round 1**
- *Style* — "Which look do you want by default?" Dark / White / Ask me every time. (Describe each in one line.)
- *Language* — "What language do you speak in your videos?" English / Arabic or Darija / French / Other (type it).
- *Captions* — only if not English: "How should captions be written?" e.g. for Arabic/Darija: Arabic script with
  English tech words, whole line right-to-left (recommended) / Arabic script, English words left-to-right / Latin
  letters (Arabizi). For French/Spanish/…: in the spoken language / translated to English.
- *Transcription* — "Which transcription service?" Fish Audio (simple, accurate word timing, pay-as-you-go) /
  Gemini 2.5 through OpenRouter (best for Darija and mixed languages; writes captions in the right script).

**Round 2**
- *Footage* — "Do you cut your video yourself before sending it?" Yes, already cut — just edit it / No, I send raw
  takes — pick the best ones and remove silences.
- *Background* (dark style or ask) — "Remove the background behind you?" Yes, always (recommended) / No.
- *Layout* (dark style or ask) — "How should you appear?" On screen the whole reel: animations on top, captions in the
  middle, you in the bottom half (recommended, needs background removal) / Classic: alternate full-screen animations
  and split screens. Save as `layout` = `face` / `classic`.
- *Music* — No music, voice + sound effects / I'll use my own track (ask for the file path; never download music
  they haven't given you; nothing is bundled for copyright reasons).
- *B-roll / extras* (white style or ask) — No B-roll / AI B-roll with Higgsfield (needs their Higgsfield account
  connected in Claude) / I'll give my own clips.

**Round 3 (free text, one message)** — ask for: their name or handle (used as the creator name on screen), their
usual comment keyword (e.g. GUIDE — optional), the tool they usually talk about (default Claude), and a fake brand
name for demo screens (default mehdiagent.com). Tell them any of these can be skipped.

**Save** each answer: `python3 $M/settings.py set <key> <value>` (keys: style, layout, speech_language, caption_script,
caption_direction, keep_english_terms, transcriber, footage, background_removal, music, broll, creator_name,
cta_keyword, hero_tool, demo_brand, projects_dir).

**API key** — `python3 $M/settings.py init-env`, then open the file for them (`open -e ~/.mehdiagent/.env` on macOS,
`notepad %USERPROFILE%\.mehdiagent\.env` on Windows) and tell them exactly where to get the key:
- Fish Audio → fish.audio → sign in → API keys → create → paste after `FISH_API_KEY=`. Needs a little credit.
- OpenRouter → openrouter.ai/keys → create key → paste after `OPENROUTER_API_KEY=`. Needs a little credit.
Wait for "done", then verify: `python3 $M/fish_audio.py` or `python3 $M/transcribe_openrouter.py --check`
(both free, print no account data).

**Finish** — `python3 $M/doctor.py`; offer to fix what is missing (ask before installing anything); then
`python3 $M/settings.py set onboarded true`, show a 5-line summary of their choices, and say how to change one later
("say: change my style to white"). If they already gave a video, start the edit now.

## Changing settings later
"change my style / language / key / music…" → ask only that question again and `settings.py set` it.
"doctor" / "something's broken" → run `doctor.py` and fix with them.

## Transcription (both styles use this, never a style's own transcriber)
`python3 $M/transcribe.py <video> --edit-dir edit` → `edit/transcripts/<stem>.json` with timed `words`.
- Gemini/OpenRouter already returns the right script + exact times (local aligner, `align_latin.py`).
- Fish on a non-Latin language returns rough spellings: correct the words by meaning, write one Latin
  sound-spelling per word, and re-time with `align_latin.align_words(video, words)` (see reel-dark
  `references/workflow-single-video.md`). Flag every word you were unsure of when you deliver.

## Rules that hold for every reel
- **A new hook for every video**, designed from what its opening line says (`references/hooks.md`); check
  `scripts/hooks.py recent` first and record the hook after delivery. Say which hook you chose and why.
- Never cut or reorder the creator's words unless they asked (precut footage).
- Background removal on → no pixel of their room may show; check sampled frames before delivering.
- Report honestly: checks are signal/frame based — you cannot listen.
- Never put a key in a file inside a project or repo; never print one.
