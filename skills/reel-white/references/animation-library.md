# Animation library / schemas (palette for reels)

A broad catalog of animated elements for the upper half of reels. The first sections are
Common in popular tech reels; the last section is extra ideas to use so you don't repeat yourself.
Everything renders with HyperFrames (HTML/CSS/SVG/GSAP). Golden rules: snappy entrances (0.15-0.25s),
graphics that DRAW themselves/grow, no pulsing of the boxes, contiguous and synchronized to the words.

## Already implemented in scripts/gen.py (GREEN example)
intro-aerial (motionPath) · stat+count-up · summary (keyword) · line-graph (dashoffset, up/down) ·
CRM rows · listcheck · calendar · comstep (step-by-step) · iphone reveal · wachat (WhatsApp dark) ·
msgtpl (template with placeholder) · vflow (vertical flow) · cta (meter).

## Reusable ORANGE-accent techniques
- **pricestrike**: brand logo + big price, then a red strike that "wipes it out" (staged entrances: logo → price → strike). For the "stop paying for X" hook.
- **versus**: "A vs B" header with the two logos + metric rows as BARS (track + fill scaleX, value on the right). One metric "tied", one that makes yours win (e.g. POWER tied, COST 1× vs 5× red). The strongest comparison schema.
- **glmreveal / brandreveal**: big logo entering (scale+rotate back.out) + wordmark + "OPEN SOURCE" badge. For the "I'm talking about X".
- **terminal (run | prompt)**: macOS window (3 dots + title) with rows in stagger and a blinking cursor. `run` = "$ claude / ● model … / ✔ connected"; `prompt` = a typed command with tokens in accent color (path, functions, url).
- **testbench (chips)**: versus header + a grid of icon+label chips, one highlights on the word. For "different use cases".
- **abquiz / abreveal**: two browser frames side by side (A|B) with **REAL screenshots** (object-fit:cover, top), a central "?"; then a reveal of the winner (scale + accent glow + "✓" ribbon), loser faded. For "who generated what?".
- **costtag**: giant multiplier with count-up (1→5) + "LESS". For "costs N times less".
- **stepflow**: numbered vertical steps (number circle + title + sub) with arrows, one per trigger word. For a setup "1 API key → 2 paste → 3 use".
- **ctacomment**: large accent pill with the word to comment in quotes (NO emoji) + "and I'll send you the prompt". For the "comment X" CTA.

## Observed in the reels — TO ADD when needed

### Data / numbers
- **Bar chart / columns**: vertical bars that grow (scaleY 0→1, stagger, transform-origin:bottom). For comparisons/quantities.
- **Gauge / needle speedometer**: SVG arc + a needle that sweeps (rotate) up to the value, number in the center. For "cost/speed/level".
- **Donut / progress ring**: SVG circle with stroke-dasharray that fills + % in the center.
- **Heatmap / contribution grid**: a grid of cells that light up in sequence (opacity/scale stagger). For "activity/coverage".
- **Horizontal progress bar**: already in cta (meter), reusable as a standalone element.
- **Star rating**: 5 stars that fill one by one.
- **Table**: rows×columns, rows in stagger; highlight a column/cell.

### Tech / product
- **Terminal / code window**: macOS window (3 dots) with animated typing (width step or opacity per row). (all the tech reels)
- **Code diff**: a git diff with +green / −red highlighted rows, the rows enter in stagger, + a token counter.
- **Chip/tile with icons**: a row/grid of small cards with icon+label, one highlights on the word.
- **Waveform / EQ**: audio bars that bounce (decorative use, or for "voice/audio"); do NOT use it as an omnipresent generic pseudo-sync, but as an element of an audio scene.

### Layout / reveal
- **2-panel comparison** (✗ red strikethrough vs ✓ green): already done as comstep+compare; the full two-column version with an arrow is strong.
- **Device reveal**: a real screenshot inside a mockup (iphone) that enters (slide/scale). For the "real product".
- **Chat mockup**: WhatsApp/iMessage dark, in/out bubbles in stagger, header with logo.
- **Flow / pipeline**: boxes+arrows, vertical (top→bottom, Riccardo's preference) or horizontal.

## Extra ideas (not in the reels — to vary, as requested)
- **Odometer / number flip**: digits that roll (slot machine) instead of a smooth count-up.
- **Map + pin/route**: for trips/places (e.g. a map with destination pins that light up).
- **Marker / highlighter sweep**: a highlighter that passes over a keyword.
- **Carousel / card stack**: cards that scroll/stack (e.g. travel offers).
- **Pie chart** that draws itself slice by slice.
- **Timeline / milestones**: a line with stages that light up.
- **Toast / notifications** that enter stacking up (e.g. "new reactivated lead").
- **Leaderboard / racing bars** (bar race).
- **Counter "+N" rising** (e.g. "+12 reactivated clients" incrementing).
- **Kinetic typography**: a keyword that explodes/assembles (beyond the karaoke).
- **Comparison slider** (before/after with a sliding line).

## How to add one to gen.py
1. Add a new `type` in `inner(i,t,p)` (HTML+CSS of the element, final state).
2. Add the tweens in `tw` for that type (entrance + draw/grow, anchored to `s` or to a word trigger).
3. Put it in the `BEATS` with the right trigger. Keep it CONTIGUOUS and SYNCHRONIZED.
4. Render → extract a frame → compare against the reel → iterate.

## More techniques
Ready-made snippets, anchor the animations to the real word timings (find/find_after).

- **Staged hook with a big LOGO**: stage1 text ("4 SKILL") that pops on a word, then exits
  (`opacity:0,scale:0.85`) when the next keyword starts; stage2 = `<img>` big logo
  (height ~360px) that enters (`scale:0.4,rotate:-30 -> 1,0`); stage3 = red "ILLEGAL" stamp below
  the logo on another word. Anchor each stage to a DIFFERENT word with find().
- **Per-word pill with emoji**: as the user lists things (output/text/email), one pill per word
  appears on the `find()` of that word (`opacity:0,y:18,scale:0.85 -> 1`), with a themed emoji (📄 ✍🏻 📧).
  Then the pills dim (`opacity:0.3`) and a green result appears centered on another word.
- **TYPEWRITER terminal** (real typing, NOT TextPlugin): a terminal window (bar with 3 dots + title,
  monospace body). Typing = tween on a counter + `textContent=val.slice(0,Math.round(n))`, `ease:"none"`,
  duration ∝ length. Use `textContent` (not innerHTML/TextPlugin) so the `<role></role>` tags show up
  LITERAL. Cursor `▋` blinks via CSS. A confused state (gray) → empties → a perfect state (green, XML).
- **Count-up vs POP**: count-up (`tl.to({v:0},{v:N,onUpdate...})`) ONLY if the beat lasts >1.2s; below that, POP the
  final number (`opacity:0,scale:1.45 -> 1`, back.out) so it's legible. For "91.000+" format with `toLocaleString` + "+".
- **"Card" blocks 1-2-3-4**: N green rounded-rects entering staggered; ANCHOR them with
  `find_after("queste quattro", beat_start)` if the anchor word recurs earlier (in the hook) — otherwise they start too soon.
- **User B-roll in the upper band**: see the "B-roll" section in SKILL.md. Full-bleed `scale=-2:864,crop=1080:864`
  for landscape screen captures, `scale=-2:824` centered for portrait documents; a black band below + enable=between(t,A,B).

## Glass-shatter logo (destroy a brand/thing on its word)
Slam a logo in, then on the trigger word it shatters into triangular shards that spin out and fall. Recipe (python-generated):
- Container `.shardbox{position:relative;width:260px;height:260px}` holding N copies of the logo `<img class="shard">` (absolute, full-size), each clipped to a triangle: 3x3 grid, each cell split into 2 triangles via `clip-path:polygon(...)` → 18 shards that perfectly tile the intact logo.
- A `.crack` overlay (radial white gradient, opacity 0) flashes 0.05s before impact: `fromTo(opacity 0→1, yoyo repeat 1, immediateRender:false)`.
- On the trigger word each shard tweens `x/y/rotation/opacity` with `power2.in`: dx = (shard-centroid − center)·(2.2–3.8×) + jitter, dy = centroid·1.4 + fall 120–420px, rotation ±160°, duration 0.55–0.8s, per-shard delay 0–0.06s (crack-then-crumble feel). Pair with a red shockwave ring + container shake. Seed the RNG for reproducible renders.

## Head-popout over a floating frame (white "futuristic" layout)
Alternative composite: white background, cards re-themed for white, the talking-head inside a floating rounded card whose top edge is pushed DOWN, with the speaker's head CUTOUT popping above the frame line.
Recipe:
1. **White cards**: copy gen.py → gen_white.py and retheme: body bg #fff; big text #fff→#141414; dark pill/tile backgrounds → rgba(ACCENT,0.07); grid lines 0.05→0.14 alpha; glow 0.26→0.13; white-fill logos need dark variants (rewrite `fill="#ffffff"`→`#141414` — NEVER inject a second fill attr, duplicate attributes = broken-image icon); white crack-flash → accent-colored.
2. **Black captions**: patched captions.py (text fill (20,20,20), halo (255,255,255,170)); pass CAPTION_FONT env var.
3. **Segmentation**: rembg (venv: `python3 -m venv .venv-rembg && pip install rembg onnxruntime`), u2net session reused across frames. Extract frames at 25fps scaled 1080:-2, `remove(im, only_mask=True)` per frame (~1-2s/frame CPU, run in background). Find head-top first on 4 sample frames via matte bbox to place the layout.
4. **Layout math**: choose screen offset so head-top ≈ frame_top−100 (pop amount). e.g.: content offset +450 (screen_y=src_y+450), frame rect (30,1080)-(1050,1890) radius 36, popout strip = src 420..630 → RGBA pngs (rgb crop + matte crop as alpha).
5. **Composite order**: white cards (base) → frame drop-shadow PNG (PIL rounded rect alpha 90, GaussianBlur 22 — REQUIRED: without it the frame edge is invisible on white and the popout reads as nothing) → video crop alphamerged with rounded-corner mask → popout RGBA sequence overlay → captions. Then loudnorm+music, then SFX remix.

## Letter-morph rebrand (e.g. BRAND -> BRANT)
Turn one brand word into another by swapping a single letter — smooth and clean, no slam. Recipe:
- Word as per-letter spans; the swapped slot is `position:relative` holding BOTH letters stacked (`.ychar{position:absolute;top:0;left:0;opacity:0}`), container has `perspective:900px`.
- Letters rise in individually (y:40->0, 0.05s stagger) in the OLD brand's color.
- On the trigger word: old letter `rotationX:88,y:-30,opacity:0,transformOrigin:"50% 100%"` (power2.in, 0.28s); new letter fromTo `rotationX:-88->0` from below (power3.out, 0.34s, immediateRender:false) in the accent color; remaining letters tween `color` old-brand -> #fff/#141414 over 0.4s.
- Settle: whole word scale 1.05 yoyo once (sine). No shake, no ring — this one is meant to feel smooth.

## Ping-pong exchange (two agents going back and forth)
Two logos on opposite ends of a thin track; a glowing accent ball bounces between them while the voiceover describes an exchange ("Claude checks with Codex, back and forth until..."). Used on the codex tutorial reel. Recipe:
- Row: logo — `.bftrack` (460x10px rounded, accent 0.18 alpha) — logo. Ball: 34px accent circle, absolute center of the track, `box-shadow: 0 0 26px ACCENT`.
- Logos slide in from ±120 on the sentence start; track scales in scaleX 0.4->1.
- Ball: `fromTo(x:-215 -> 215, duration:0.55, repeat:N-1, yoyo:true, ease:"power1.inOut")` starting on the exchange verb ("check"). Each arrival bumps the RECEIVING logo (scale 1.13 yoyo, 0.11s) at `t0+(k+1)*leg-0.06` — alternate targets. Pair each arrival with a quiet tick SFX (0.20).
- Resolution: ball fades on the payoff word ("solution"), an accent CHECK badge (SVG circle+check) pops mid-track `back.out(2.2)` + ding; whole row breathes 1.05 once on the closing phrase.

## Question-mark hook
For hooks that ASK ("What is best, X or Y?"): a giant accent "?" (font ~340px, glow shadow) slams in (scale 2.6->1, power4.out + small shake) on the question words, then exits up (scale 0.5, y-50, power2.in) just before the first subject visual lands. The question gets its own visual beat before the answer's.

## Orbit-merge (two logos become one thing)
Replaces a static "+" for "both together" moments. Stages on their words:
1. Logos pop in at opposite ends of a 640px `.orb` container (absolute holders `.oh.l/.oh.r`).
2. ORBIT: rotate `#orb` 0->360 (power1.inOut, ~1.3s) while counter-rotating each logo -360 so they stay upright — they circle each other.
3. SNAP on the merge word: holders tween x to ±90 (power4.in, 0.16s) so the logos land TOUCHING (separation >= logo width — overlapping reads messy, verify a frame), with a shake + 10 accent `.bdot` particles bursting outward (random ±260/±200, fade 0.55s, immediateRender:false).
4. PAYOFF on the closing word: fast pair-spin (`rotation:"+=360"` on orb + "-=360" on both logos, 0.55s power2.inOut) over a radial glow `.bloom` scaling 0.5->1.25.
Python-generated tween strings: mind the f-string braces — GSAP `{}` must be `{{}}` in every generator layer, or the burst tweens ship as broken JS.
