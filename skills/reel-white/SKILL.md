---
name: reel-white
description: mehdiagent WHITE style - use when the mehdiagent skill routes a video here, or the user asks for "the white style", "white reel", "popout reel". Edits a raw talking-head clip (vertical OR landscape 4K) into a finished vertical reel/short in the WHITE "futuristic popout" style - white background, dark text, orange accent, animated motion-graphics cards on top, and the speaker in a floating rounded video frame with their HEAD CUTOUT popping over the frame edge (AI person segmentation). Black karaoke captions. Optional AI B-roll via the Higgsfield MCP or the creator's own clips. Also "make a short like this <reel link>". Run the mehdiagent setup first if ~/.mehdiagent/config.json is missing. NOT for posting and NOT for long-form YouTube.
---

# Reel White

Turn ONE talking-head clip into a finished 9:16 reel: the speaker in a floating rounded frame, animated motion-graphics
cards above, one-word karaoke subtitles, sound effects, and optionally music and B-roll.

`<skill>` = `~/.claude/skills/reel-white`, `$M` = `~/.claude/skills/mehdiagent/scripts`.
**Settings first:** `python3 $M/settings.py show` (run the `mehdiagent` setup if not onboarded). They decide the
language, caption script/direction, transcriber, footage type (`precut` = skip steps 3–7's take picking and
silence trimming: transcribe the clip once and author cards on it), music (`null` = none), B-roll
(`none` / `higgsfield` / `own`), CTA keyword, demo brand and hero tool. They override every default below.
Work inside one project folder per reel under the `projects_dir` setting.

## Stack
- TRANSCRIPTION: always `python3 $M/transcribe.py <video> --edit-dir <dir>` (Fish Audio or Gemini 2.5 via OpenRouter, whichever the creator chose; word-level times; same `{"words":[{text,start,end}]}` shape every script here reads). For the CUT use `scripts/cutjoin.py` (NOT a generic renderer: see ERRORS).
- `hyperframes` (via `npx hyperframes render`) to render the HTML/GSAP cards. `npx` fetches it on first use; needs Node.js.
- `ffmpeg` for composition + music. **Local ffmpeg usually has no libass** → subtitles are baked with PIL (captions.py), NOT with `subtitles=`.
- Caption font: Montserrat (bundled at `assets/fonts/Montserrat-VariableFont_wght.ttf`, weight 900). captions.py finds it automatically.
- Bundled assets: `assets/logos/` (whatsapp, claude, openai, github). No music is bundled (copyright): use the `music` setting (`MUSIC=<that path>` for compose.sh), or none (`MUSIC_VOL=0`).
- Sound effects: the kit in `~/.claude/skills/reel-dark/template/audio/sources/` (pop, whoosh, thud, click, caption-click).
- **Higgsfield MCP** (only when `broll` = `higgsfield` and the creator connected Higgsfield in Claude) for AI-generated B-roll (Seedance 2.0, image-to-video / text-to-video). Deferred tools — load via ToolSearch before calling (search "higgsfield generate_video media_upload jobs_wait", or `select:` the `mcp__…__generate_video`, `media_upload`, `media_confirm`, `jobs_wait`, `job_display`, `balance` tools of the Higgsfield server; the server-name prefix varies per session).

## Dual-source input (.mov audio + camera video)
When the user supplies TWO recordings of the same take — typically an OBS/screen-recording .mov carrying the good MIC audio and a camera .mp4/.MP4 carrying the good VIDEO (often rotation-metadata vertical) — build an aligned master BEFORE the normal pipeline:
1. Transcribe BOTH files (`$M/transcribe.py`, word timestamps).
2. **Offset from transcripts**: walk the camera transcript, match each normalized word to the mov transcript near the running position, collect `mov_start - cam_start` per match, take the histogram mode + median of the inliers.
3. **Confirm with cross-correlation**: mono 8kHz wavs of both, slide the mov against the camera around the transcript estimate at 5ms steps on a 30s window, take the peak.
4. **Mux**: `ffmpeg -i CAM -ss <offset> -i MOV -map 0:v -map 1:a -c:v copy -c:a aac -shortest edit/master.mp4` (video copied, rotation metadata intact — cutjoin auto-rotates on re-encode).
5. Transcribe the master and continue the normal pipeline (EDL on the master transcript). Lips match the clean audio because both recorded the same performance.

## Pipeline (run in order, inside one project folder, e.g. `~/reels/<name>/`)

0. **If you were given a reference reel (IG/TikTok link)**: study it FIRST (see "Replicate a reference reel"). Download, make a contact-sheet, sample the accent color → set the palette in gen.py.
1. **If the RAW is LANDSCAPE** (e.g. 4K 16:9): pre-crop to vertical 1080x1920 centered on the face, then work on `edit/raw9.mp4`:
   `ffmpeg -i <raw.MP4> -vf "crop=1215:2160:<x>:0,scale=1080:1920" -c:v libx264 -crf 18 -c:a aac edit/raw9.mp4`
   (1215 = 2160*9/16; tune `<x>` by extracting a frame and centering the face; for a 3840-wide source `x≈1293`).
2. **Transcribe the RAW**: `python3 $M/transcribe.py <raw> --edit-dir edit` (language comes from the settings).
3. **Read the transcript word-by-word** (`edit/transcripts/*.json`, print indices+times). Raw clips are often **multi-take with spoken director's notes** ("put a clip of…", "ok so…", "show the bit where…"). Those must NOT end up in the voiceover. **Hand-pick the CLEAN take of every sentence** and build an EDL of KEEP-ranges (the final narration), discarding repetitions, false starts, and director's notes.
4. **Write the EDL** by hand (list of `ranges` with start/end of the good takes) — exact shape: `{"sources":{"src":"<abs path>"},"ranges":[{"start":a,"end":b},...]}` (the top-level key is `sources`, a dict — NOT `source`; cutjoin.py KeyErrors otherwise). `make_edl.py` is fine ONLY for single-take raws; for multi-take, build the keep-list manually. **EXTEND each `end` by +0.2/0.4s** to include the word release + a breath (otherwise you clip it). If the transcriber collapses a multi-take zone into ONE very long "word" (e.g. a 4s blob), that's a red flag: inspect that window with `silencedetect`, SPLIT keeping the clean take and dropping the blob in the middle.
5. **Cut**: `python <skill>/scripts/cutjoin.py edit/edl.json edit/cut.mp4` (extract+concatenate, native resolution, no OOM).
6. **Trim residual silences** (CRITICAL): `python <skill>/scripts/silence_keep.py edit/cut.mp4 edit/edl_sil.json` (defaults: -40dB / MIN 0.35 / PAD 0.12, protects the last word; for a very punchy short add `... -40 0.30`) → `python <skill>/scripts/cutjoin.py edit/edl_sil.json edit/cutF.mp4`. **NEVER -30/-32dB**: it eats the soft word releases. Afterwards, CHECK the gaps in the re-transcribed cut: a `gap = start - prev_end` > 0.30s between two sentences = a pause to tighten.
7. **RE-TRANSCRIBE the final cut** (exact sync): `python3 $M/transcribe.py edit/cutF.mp4 --edit-dir edit/tF`. Then **VERIFY no word is clipped**: the transcriber AUTO-COMPLETES cut words (it prints "output" even if the file only contains "out"). Signs of a clip: a word whose `end` exceeds the file duration, sentences that "jump", a vanishing last word. If you find one → extend that range's `end` in the EDL and re-cut. **Do NOT trust the transcript text alone.**
8. **Author the BEATS** in `cards/gen.py` (copy from `<skill>/scripts/gen.py`) by reading `edit/tF/transcripts/cutF.json`. Each card has a `trigger` = the word/phrase it MUST appear on. Cards are **contiguous**. Timing rule: a beat lasts as long as its sentence; if you need a multi-stage sequence (logo→price→strike) anchor the stages to DIFFERENT words and finish BEFORE the beat's last word (otherwise the exit clips it).
9. **Project assets**: `mkdir -p cards/assets/logos && cp <skill>/assets/logos/* cards/assets/logos/`. Missing logos: find them on svgl, GitHub org avatars, or the brand CDN. For real screenshots (e.g. an A/B comparison of two pages) resize them into `cards/assets/` and show them inside a browser-frame.
10. **Generate + render cards**: `cd cards && python gen.py ../edit/tF/transcripts/cutF.json && npx --yes hyperframes render . -o cards_all.mp4`
11. **Patch transcriber errors + Subtitles**: the transcriber mangles names/terms ("Claude"→"Cloud", etc.); patch the JSON in `cutF_cap.json` (substitute on the "text" field) and generate: `python <skill>/scripts/captions.py edit/tF/transcripts/cutF_cap.json edit/capt 12 92` (last arg = font size; **66 default** - the user's settled preference after 92 and 76 both read too big; long words fall off-frame above ~88). captions.py already has a **soft shadow** (readable over bright B-roll, no hard stroke). The card triggers stay on the ORIGINAL transcript.
12. **B-roll (only if the `broll` setting is `higgsfield` or `own`)**: when it is `higgsfield`, unless the user said "no B-roll" for this reel or supplied their own clips, generate 1–2 B-roll cutaways with the **Higgsfield MCP** and overlay them in the top band — see the "AI B-roll via Higgsfield" section. Pick the windows from the FINAL transcript (`edit/tF`), kick off generation right after the EDL is final (it takes 1–3 min — run it in parallel with card rendering), download the MP4s into `broll/`. User-supplied clips follow the same compositing rules ("User B-roll in the top band").
13. **Compose + music**: `bash <skill>/scripts/compose.sh edit/cutF.mp4 cards/cards_all.mp4 edit/capt renders/<name>-FINAL.mp4 <crop_y>`. For a head-and-shoulders crop (already-vertical source) crop_y varies per clip (~120-300). ALWAYS tune it on test frames (`scale=1080:-2,crop=1080:1056:0:$cy` at 3-4 values, contact-sheet them) so the face sits in the UPPER part of the lower band — "too far down" was real user feedback. compose puts the voice at dialog level (loudnorm) and music at 6% (`MUSIC=<the music setting>`; with no music setting pass `MUSIC_VOL=0`) and adds `+faststart`.
   With B-roll present, compose with an overlay chain (extra `-i broll/*.mp4` inputs + black-band cover + `enable='between(t,A,B)'` overlays) instead of plain compose.sh.
14. **Self-evaluate**: extract a frame (`ffmpeg -ss T -i ...`) of each schema, build a contact-sheet (PIL or `tile`) and COMPARE against the reference reels BEFORE showing it. Show only if it's decent. **Always also check**: first word (not clipped), last word + subtitle (not clipped), subtitles readable over every B-roll, beat-to-beat transitions with no flash, **A/V sync** (`ffprobe` video stream duration ~= audio, drift < 1 frame) and **subtitle == spoken word** (sample 3-4 points at mid/end: the caption must match the transcript, see the desync error).
15. **Retro + self-learning** (MANDATORY, see section below): when the reel is done, say what went well and what went badly, and update THIS skill with the lessons.

## DEFAULT LOOK: white "futuristic popout" (this skill's identity)
This skill's output is ALWAYS the white style:
- **White background** full frame; cards re-themed for white: text #141414, pills/tiles rgba(ACCENT,0.07) with accent borders, grid 0.14 alpha, glow 0.13, dark logo variants (rewrite fill to #141414 - never inject a duplicate fill attr), accent-colored crack flash.
- **Floating video frame + head popout**: speaker in a rounded card (radius 36) whose top edge is pushed down, drop-shadow PNG underneath (PIL rounded rect alpha 90 + GaussianBlur 22 - mandatory, or the edge is invisible), and the speaker's head CUTOUT (rembg u2net per-frame matte) overlaid so it pops ~100px above the frame line. Full recipe + layout math: "Head-popout over a floating frame" in references/animation-library.md.
- **Black captions**: patched captions.py (fill (20,20,20), halo (255,255,255,170)) - white captions are invisible here. Font size ~66.
- Compose does NOT use compose.sh (that's the black-band layout): use the custom ffmpeg chain from the animation-library recipe (cards base -> frame shadow -> alphamerged rounded video -> popout RGBA sequence -> captions), then loudnorm+music, then the SFX remix.
- Head cut-out: on macOS use Apple Vision (`~/.claude/skills/reel-dark/template/helpers/personmask.swift`, compile with `swiftc -O`, `personmask <video.mp4> W H person` streams 8-bit mattes; no download). Elsewhere use rembg (u2net_human_seg) in a venv (`python3 -m venv ~/.mehdiagent/venv-rembg && ~/.mehdiagent/venv-rembg/bin/pip install rembg onnxruntime`). Segmentation of ~600 frames takes minutes - run it in the background right after the final cut, in parallel with card rendering.

## Style (fixed, except the accent color)
- 9:16, talking-head in the bottom ~55% (overlay y=864), top band 0-864 black for the schemas.
- **ONE accent color per video** on black. Default **green #2fe081**. Themeable: for Claude/GLM content use **orange #f0813f** (bright #ffa766). Red/#ff5a5a for "no/lost/expensive", steel-grey #7f93ad for the "neutral competitor". The accent is set at the top of `gen.py` (tokens A/AB/AD/GL).
- Subtitles: Montserrat **Black**, white, UPPERCASE, **ONE word**, **no black outline**, at the edge with the video (CY=700 + overlay y=78). Font ~100px (parametric in captions.py).
- Decorative layer ALWAYS on: rising particles, streaks, a breathing glow, a scrolling grid → the top band is never empty/static.
- Big schemas that FILL the band (keyword ~112px, numbers ~200px, tall graphs).
- **LESS TEXT on cards**: cards carry the VISUAL — a big logo, one word, an icon, a graph. No explanatory sublines ("THE FREE X ALTERNATIVE"), no price pills, no eyebrow+title+chip stacks unless each element earns its place. The voiceover + captions carry the words; if a card needs a sentence to make sense, redesign it. Hooks especially: one visual + at most one word.
- **NO expanding shockwave rings / circle effects**: impact = slam entrance + shake + SFX, never a radiating circle. (Deliberate circular GRAPHICS like a stopwatch dial are fine.)
- **Hero cards hold ~0.3-0.4s** past their sentence before the next beat - extend the hero beat's end and re-anchor the next beat's first element to its new start.

## Sound effects (default ON)
Layer SFX under the card animations after compose, from the bundled kit in `~/.claude/skills/reel-dark/template/audio/sources/`
(copy into `sfx/`): `thud.wav` (slam/impact), `pop.wav` (UI pop, reveals), `whoosh.wav` (morph/transition/shatter),
`click.wav` (tick, counter steps, presses), `caption-click.wav` (soft click).
Cue map = one (file, time, volume) per animation hit: slams/logos → thud 0.4, shatters → whoosh + thud 0.45, pill/tile pops → pop 0.25-0.3, morphs/transitions → whoosh 0.35, calendar/counter steps → click 0.22, CTA/link reveals → pop 0.35. Time the cue at the tween START (a hair before the visual lands feels right for shatters).
Mix with ffmpeg over the composed render, video untouched: each cue `[n:a]volume=V,adelay=ms|ms[sn]`, then `[0:a][s1]..[sN]amix=inputs=N+1:normalize=0:duration=first,alimiter=limit=0.891:level=false[aout]`, `-map 0:v -c:v copy`. **alimiter needs `level=false`** — its auto-level default re-boosts the mix to 0dB (clipping); with it, peaks cap at -1dB and the voice stays at dialog level. Verify with `volumedetect` (max ≤ -1dB).

## Replicate a reference reel (when you're given a link)
1. **Download (study copy only)**: ask the creator first, then `yt-dlp -o ref.%(ext)s "<reel url>"`. Use it only to study
   layout, rhythm and colours: never reuse its footage, audio, text or graphics, and delete it when the reel is done.
2. **Study it closely**: contact-sheet at 2fps with ffmpeg `tile` (`ffmpeg -ss A -t 15 -i ref.mp4 -vf "fps=2,scale=216:384,tile=5x6:padding=4:color=black" sheetA.jpg`) and READ it. Extract: layout (where the talking-head sits, where the schemas go), the VOCABULARY of schemas used (terminal? grid? versus? count-up? command-bar?), the rhythm (how often the graphic changes), the subtitle style.
3. **Sample the accent**: extract a frame with a vivid color and read the bright pixels (PIL) → set A/AB in gen.py.
4. **Map** your beats onto the schemas observed in the reference. Do NOT copy the reference's text: use YOUR content.

## Schema vocabulary
Implemented in the `gen.py` template: intro-plane · stat+count-up · self-drawing line graph (down=red / up=green) · CRM contacts · checklist · calendar · step-by-step compare · iPhone reveal · WhatsApp dark chat + logo · template message ([name]/[place] highlighted) · vertical flow · CTA meter.

**Ready-made cards (copy-paste CODE in `references/card-snippets.md`)**: staged hook with logo · TERMINAL that types (typewriter) · per-word pill + result · numbered blocks 1-2-3-4 · before/after swap · skilltitle (badge+name+chip) · bigstat pop · colored-word CTA.  Copy the card you need, don't rewrite it.

**More card ideas (ORANGE accent)**: **claudehero** (big logo + wordmark + sub, logo pops on its word) · **asciiwin** (mac window typing an ASCII WIREFRAME, e.g. a landing page: nav/hero/CTA/features/footer, typewriter via `textContent` on `<pre>`) · **staged terminal** (typed `/command` + lines appearing after: the model's questions, or scan + ⚠ vulnerability + ✓ done) · **mdfile** (markdown file viewer, `#`/`##`/`li`/`tx` lines revealed in stagger, filename tab + MD badge) · **githubcard** (big logo + top + chip, logo pops on the word) · **risinggraph** (exponential curve that draws itself + stamp) · **triple-pulse hooks** (giant word scale-punch + expanding ring on EACH repetition, for rhetorical triads "X, X, X") · **twopill** (two stacked pills entering on their word). For `<` `>` tags inside the typewriter use `json.dumps(string)` to embed the JS string safely.

**Wider palette to vary (don't limit yourself to the schemas above):** see `references/animation-library.md` — bar chart, gauge/donut, heatmap, star rating, code-diff, terminal, table, map+pin, odometer, carousel, timeline, toast, etc. `references/style.md` has the base catalog + the reference-reel URLs.

## AI B-roll via Higgsfield (when `broll` = `higgsfield`)
With that setting a standard reel gets **1–2 AI-generated B-roll cutaways**. Skip only if the user says "no B-roll", supplies their own clips for every visual moment, or the reel is <20s with wall-to-wall cards. They live in the top band over the cards, same compositing as user B-roll (next section).

**1. Pick the windows (from the FINAL transcript, `edit/tF`)**
- Choose 1–2 sentences that describe something **concrete and filmable** ("I sit down and build it", "clients calling", "working late on the laptop") — not abstract claims or numbers (those belong to cards/schemas).
- NEVER over the hook (first ~2s, the hook card owns it) and NEVER over the CTA.
- Window = the sentence's word times, 2–4s each. Space the two B-rolls apart (e.g. one ~1/3 in, one ~2/3 in), never back-to-back.

**2. Generate (Higgsfield MCP — never local AI tools)**
- Load the deferred Higgsfield tools via ToolSearch first (see Stack).
- **Identity B-roll** (the creator doing the action — preferred when a photo of the user is available or one can be grabbed from a clean raw frame): upload the photo with `media_upload` → `curl --upload-file` to the returned URL → `media_confirm` (`type: "image"`), then `generate_video` with `model: "seedance_2_0"`, the photo as `medias: [{value: <media_id>, role: "image"}]` (role `image`, NOT `start_image` — more dynamic motion), `duration: 10`, `aspect_ratio: "16:9"`, `resolution: "1080p"`.
- **Generic B-roll** (scene without the creator): same call, no media, text-to-video.
- **Prompt recipe**: `<scene/action>, dark moody environment, single accent-light matching #<ACCENT>, cinematic shallow depth of field, slow dolly/slider move, 35mm texture, identity preserved.` Dark/moody is mandatory — the B-roll must blend into the black band and keep the white subtitle readable (bright footage = illegible captions).
- Optionally preflight cost with `get_cost: true` once. Poll with `jobs_wait`/`sync: true`; generation takes 1–3 min, so **fire the jobs right after the EDL is final and render cards while you wait** — don't block the pipeline. If still pending, `ScheduleWakeup` 120s+, never busy-poll.
- Download each result MP4 into `broll/` (`curl -L -o broll/<name>.mp4 "<url>"`).

**3. Trim + place**
- The 10s generation covers a 2–4s window: pick the **best-motion 2–4s slice** (scrub a contact-sheet, `fps=2,tile`) and use `trim=START:END` in the overlay chain — don't just take 0:DUR.
- Composite exactly like user B-roll (next section): full-bleed `scale=-2:864,crop=1080:864`, black-band cover under the window, `enable='between(t,A,B)'`.
- Self-eval extra checks: subtitle readable over the B-roll, no card flash at the window edges, the footage actually matches the spoken sentence (AI B-roll that contradicts the voiceover is worse than none — regenerate or drop it).

## User B-roll in the top band (over the face)
Sometimes you'll get clips (a screen-recording of a site, a report, a list) to show "over the face" while talking about them. They go in the top band (0-864), in their time window, ON TOP of the cards.
- **Map the windows** to the words (e.g. report on "report", site on "website", list on "skills"). Each window = `enable='between(t,A,B)'`.
- **Cover the card** underneath with a black-band for the whole B-roll window (`color=black:s=1080x864` overlay with `enable`), extended to the START of the next beat (so the card doesn't reappear at the edges).
- **Framing**: landscape/screen clip → full-bleed `scale=-2:864,crop=1080:864` (fills the band, no letterbox); portrait clip (a document) → `scale=-2:824` centered. Dark B-roll blends into the black; for bright ones rely on the subtitle shadow.
- **Clip timing**: `[N:v]trim=0:DUR,setpts=PTS-STARTPTS,fps=25,scale=...,setpts=PTS+A/TB[bv]` then `overlay` with enable in the window.

## ERRORS NOT TO REPEAT (learned the hard way)
| Error | Rule |
|--------|--------|
| Card = text inside a box | NO. Use **schemas/graphs/summary phrases**. The WORDS are carried by the subtitles; the cards carry the VISUAL. |
| Boxes that pulse on every word | NEVER per-word pop-scale on the cards. Movement = snappy entrances + continuous decorative layer + self-drawing graphs. |
| Sync computed on paper | It accumulates drift. **ALWAYS re-transcribe the final cut** and anchor cards+subtitles to the real word times. |
| Trimming only word-gaps | Leaves 0.6-1.1s silences. ALWAYS run `silence_keep.py` (silencedetect on the audio). |
| Graphics only at the top | Fill the whole top band + animated decorative layer. |
| Black outline on subtitles | Clean white only, no stroke. |
| Sparse cards (1 every 5s) | Cards **contiguous**, one always present, each on the word that triggers it. |
| "you-plural / everyone" subtitles | Use singular second person consistently (the creator's voice). |
| Showing half-baked versions | Self-evaluate on frames vs reference; come back only if it's decent. |
| **Keeping director's notes in the voiceover** | Raws are multi-take with spoken notes ("put a clip", "ok so"). Hand-pick the clean take of each sentence (keep-EDL), drop the rest. |
| **A generic renderer for the cut** | A renderer that resolves the source path relative to the EDL folder (→ `edit/edit/...`) and forces `scale=1920` will OOM on many segments. Use `cutjoin.py`. |
| **Music too loud** | Old default 0.15 covered the voice. compose now: voice loudnorm -16, music 0.06. Measure levels (`volumedetect`) if the voice was recorded low. |
| **File won't open (QuickTime/IG)** | Needs `+faststart` (moov atom up front). Already in compose.sh; if you remux by hand: `ffmpeg -i in.mp4 -c copy -movflags +faststart out.mp4`. |
| **Subtitles with transcriber typos** | Patch "Cloud"→"Claude" etc. in the CAPTION JSON before generating (card triggers stay on the original transcript). |
| **Multi-stage sequence in a short beat** | Logo→price→strike won't fit if the trigger is the last word. Anchor stages to different words and close before the beat exit. |
| **Clipping words (THE MOST EXPENSIVE)** | At -30dB the silence-trimmer eats soft tails → "output"→"out" etc., 3 rounds of fixes. Rule: silence_keep defaults (-40dB, last word protected) + extended EDL `end`s + **VERIFY the cut's AUDIO**, NOT the transcript alone (it auto-completes cut words). |
| **find() grabs the FIRST occurrence** | A word that occurs earlier (e.g. in the hook AND the next sentence) starts the beat on the wrong occurrence (animation too early). Use `find_after(trig, after)` to anchor to the right one. |
| **White subtitle on white B-roll** | A bright screen-recording (a site) + white subtitle = illegible. captions.py now has the soft shadow; also send bright B-roll full-bleed so the subtitle sits at the dark bottom edge. |
| **TextPlugin for the typewriter** | TextPlugin writes to innerHTML → eats tags like `<role>` (parses them as HTML). To type text with `<` `>` use a tween on a counter + `textContent=val.slice(0,n)`. |
| **Count-up in a tiny beat** | A count-up from 0 to 91,000 in 0.9s is unreadable: if the beat lasts <1.2s, POP the final number (scale-in), no counting. |
| **Card under the B-roll reappearing at the edges** | When a B-roll covers a card in its window, the faded card can flash 1-2 frames when the B-roll detaches. Cover with a black-band (`enable=between`) up to the start of the next beat, not just to the end of the B-roll. |
| **Dupes/false-starts hidden in one long word** | The RAW transcriber collapses repeated takes into ONE long word (a 2s "save" hiding a repeated phrase; an "I'll ma--" before "I'll make"). They only show up by re-transcribing the cut: after cutF, SCAN the transcript for consecutive duplicate phrases and micro-truncations (`ma--`, `us--`), then `silencedetect` the original window to find the split, divide the range dropping the dupe, re-cut. Dropping director's notes from the RAW isn't enough. |
| **A/V desync that grows mid/late clip** | Concat-COPY of AAC segments (old `cutjoin.py`: `concat -c copy`) accumulates encoder priming per segment → audio drifts from video, visible after ~40s (mouth not aligned, so subtitles aren't either). FIX: `cutjoin.py` now JOINS segments with the **concat FILTER** (`[0:v][0:a]...concat=n=N:v=1:a=1`), which re-decodes and concatenates decoded streams → sample-accurate sync. Runs on short segments, no OOM. Verify: `ffprobe` video stream duration ~= audio (drift < 1 frame). |
| **A logo SVG that was broken** | github.svg once had `viewBox 0 0 1024 1024` but path coords 0-16 → invisible. Verify ALL logos on a black background before rendering: no fill = black-on-black. A `currentColor` logo (e.g. openai.svg) loaded via `<img>` = BLACK: bake `fill="#fff"`. |
| **Inter-sentence pauses too long (short not punchy)** | Old `silence_keep.py` default (MIN 0.5, PAD 0.16) left 0.3-0.5s pauses → "too much pause" feedback. Default now MIN **0.35**, PAD_AFTER **0.12** (word tails still protected by -40dB + PAD_LAST 0.45). For a very punchy short pass `MIN 0.30`. After the cut CHECK the gaps in the transcript (`gap = start - prev_end`): if >0.30s between two sentences, tighten. |
| **Key visual entering on the LAST word** | The main element of a card anchored to the beat's last word leaves the card half-empty for 2-3s and "appears late". Anchor the key visual EARLY in the beat (one of the first words or `s+0.2`), not the last; keep it present for the whole beat. |
| **User image with window chrome "baked" in** | Screenshots of windows have the light window border INSIDE the PNG: on a black band it makes an ugly edge. Detect the frame via PIL (bbox of non-cream pixels) and CROP the inside; then on black add an **accent border** via CSS (`border:4px solid {A}`) to separate the dark logo from the black. |
| **Spoken triplets repeated identically** | If the RAW repeats the SAME sentence 3 times ("use hooks, use hooks, use hooks") you usually want to keep ONE in the cut (the cleanest/most emphatic take), not all three. Different from content rule-of-three (lists/numbers): keep those. When in doubt, one. |
| **A bare number stat = sterile** | A big static number ("1000+ HOURS") is flat. Make it a VISUAL: a curve/area that draws itself (svg path + gradient + glow) with the number popping at the peak. Applies to hours/percentages/counts. |
| **"Landscape" source that's actually vertical** | ffprobe can report 1920x1080 while a rotation side_data makes the clip VERTICAL (phone/camera metadata; ffmpeg auto-rotates on decode). Extract a frame and LOOK at it before pre-cropping — a needless crop=1215:2160 here would have failed/mangled. If the frame is portrait, skip step 1 entirely. |
| **silence_keep finds 0 silences (noisy room)** | With a noise floor above -40dB, silence_keep's default threshold detects nothing and long emphasis pauses (0.5-1.1s) survive. Diagnose with `silencedetect=n=-35dB:d=0.35`, then hand-write a tight keep-EDL on the cut (pad ~0.15s around each detected window, protect word tails) and re-cut + re-transcribe. Don't blindly lower silence_keep to -30/-32 (eats releases). |
| **Word-index anchors without a guard** | Anchoring cards to word INDICES is precise but one miscounted index desyncs a beat silently. Put an `EXPECT={idx:"word"}` assert block at the top of gen.py that verifies every anchor word before building the timeline — it catches off-by-ones at generation time instead of in the rendered video. |
| **npx hyperframes ETARGET flake** | npm registry can transiently 404 the latest hyperframes version ("No matching version found"). The package is already in the npx cache: run it directly via `find ~/.npm/_npx -name hyperframes -type d` → `<that>/node_modules/.bin/hyperframes render ...`. |
| **CTA beat empty before its trigger word** | A CTA's key visual (e.g. COMMENT "SKILLS") legitimately MUST anchor late (on the spoken trigger), so the "anchor key visual early" rule can't apply — but that can leave the CTA card as an empty bordered box for ~3s. Fix: fill the beat's FRONT with secondary visuals that echo the sentence (skill pills popping on "this skill" / "all my skills"), then dim them (opacity 0.35) when the key visual pops. A beat may never show >1s of empty card; if the hero must wait, stage supporting elements first. |
| **Retake hidden in CONTINUOUS speech (no silence to split on)** | A >2s "word" blob can hide a retake even when silencedetect at -30dB shows NO gap (speaker restarted without pausing). silencedetect can't find the split. FIX: **slice-transcribe** — extract a ±2s window around the blob (`ffmpeg -ss A -t D`) and run the transcriber on the slice alone; whisper re-resolves the hidden words and exposes the dupe ("use this specific front end— / because Claude is now going to use this specific front-end design skill"). Iterate with narrower slices to pin the clean take's start. It can take 3 slices to find where the clean take restarts. AND assume the blob may hide MORE takes than you found: a "specific" blob hid a THIRD take ("because Claude is now going…" spoken 3×), so the first fix still shipped a dupe. After re-cutting, **slice-transcribe the spliced region of the FINAL cut** (±2s around every splice point) to prove the dupe is gone — the full-pass transcript re-hid the surviving dupe inside a loose neighboring word, so it alone proves nothing. |
| **Noisy room: -35dB is the working middle** | In a noisy room: silence_keep default -40 found 0, but `silence_keep.py cut.mp4 out.json -35 0.35` worked perfectly (7 removed, no clipped words). Before hand-writing a keep-EDL, try -35 explicitly; only -30/-32 eats releases. |
| **Zero-width words in the caption JSON** | After splice-heavy cuts, whisper can emit a word with start==end (e.g. 'specific' 26.64-26.64) and push the neighbor late — the caption flashes 0 frames / desyncs. Scan the final transcript for `end-start==0` and hand-repair those times in `*_cap.json` (estimate from neighbors + speech map). Audio may be fine (verify with silencedetect: no real gap) — it's purely a caption-timing repair. |
| **The transcriber serves a stale cached transcript after a re-cut** | It caches by filename: re-rendering `cutF.mp4` and re-running the transcriber returns "cached: cutF.json" — the OLD transcript — so the clipped-word verification silently passes against stale words. After ANY re-cut, `rm -rf` the edit-dir (or the transcripts json) before re-transcribing, and check the tool didn't print "cached". |
| **Scribe collapses a hyphenated phrase into ONE mega-word** | ElevenLabs Scribe can emit a spoken phrase as a single hyphenated "word" (e.g. "know-everything-about-me", 24 chars, ~1s) — as a one-word karaoke caption it overflows the frame. Scan the final transcript for words >14 chars containing 2+ hyphens; in `*_cap.json` split them into their component words with evenly-interpolated times across the original window. Card triggers can keep the original mega-word (it's a fine anchor). |
| **Identity B-roll drifts wardrobe mid-clip** | Seedance identity B-roll can silently change wardrobe partway through the 10s. When scrubbing the contact-sheet for the best slice, ALSO check wardrobe/identity consistency vs the talking head (hat, glasses, clothing) and slice only from the consistent region. |
| **Emoji icons render ugly in headless chrome** | Some emoji (e.g. the bookmark) render as mismatched glyphs in hyperframes' renderer. For any emoji that IS the card's hero icon, draw an inline SVG instead (orange bookmark = one rounded path). Small emoji inside pills/tiles are fine. |
| **EXPECT anchors break on transcriber casing** | Re-transcribing the same audio can flip casing ('N8N' -> 'N8n') and kill the EXPECT asserts. Compare anchors case-insensitively (got.lower()==want.lower()); keep the strict text otherwise. |
| **Doubled CONNECTORS across kept takes** | Dupes hide as sentence OPENERS, not repeated sentences: keeping the last take of two different sentences can still ship "Well, you don't have to choose. Well, both together." or "And now inside of your project... And now inside of your project...". After the final cut, scan consecutive sentences for identical opening connectors (Well / And now / Now / So) and repeated intro clauses - keep the connector or intro ONCE, micro-cut the second occurrence (a small keep-EDL on the final cut, then re-run captions/cards/windows on the new timeline). |
| **Hook "before" visual waits for its trigger word** | In a "from this to this" hook, anchoring the BEFORE visual to the first "this" leaves the opening ~1.3s of the reel with an empty top band — the worst second to be empty. Rule: the BEFORE state of any before/after hook is on screen from t=0 (frame 1), with only a small scale-punch on its trigger word; the swap to AFTER stays on its word. Also make the swap sequential, not a crossfade: old exits fully (fast, ~0.16s, ending at the trigger) before/as the new pops, or both are semi-visible for several frames. |
| **The transcriber serves a STALE cached transcript after a re-cut** | The transcriber caches by output filename (`cached: cutF.json`). If you re-cut the same filename (new EDL, same `cutF.mp4`) — or a previous session worked in the same project folder — it silently returns the OLD cut's words: timings past EOF, wrong takes. Whenever ffmpeg re-writes a file you're about to transcribe, `rm` the cached `<name>.json` first; treat any `cached:` message after a re-cut as a bug. Symptom that catches it: transcript words ending later than the file's duration. |

## Self-learning (MANDATORY at the end of a reel)
The goal is to **one-shot** the reel. Every edit must make the skill better. When the reel is delivered and approved (or after the last feedback round):
1. **Honest retro in chat**: in brief, say **what went well** and **what went badly** in THIS reel (where you cut it, which bugs, how many rounds, what you should have anticipated). No self-praise: the useful part is the error.
2. **Distill the lesson into a rule**: if the error is repeatable, update this skill and tell the creator what you changed:
   - recurring technical error → a row in the **ERRORS NOT TO REPEAT** table + a fix in the right script (`silence_keep.py`, `captions.py`, `gen.py`, ...).
   - new technique/animation requested → an entry in `references/animation-library.md` (with the snippet) and in the **Schema vocabulary**.
   - a style/content preference → in the Style section or the notes.
3. **Keep the project's `cards/gen.py`** next to the reel: the next reel can start from it.
Over time the errors table + the animation-library get rich enough to do it all on the first try. Every feedback not repeated twice = a skill converging to one-shot.

## Notes
- `hyperframes render` outputs `yuv420p` (no alpha): that's why cards run on a black band and get cropped (0-864). Fine, because the top band is already black.
