# Hooks — one per video, built from what THIS video says

The hook is the first 2–4 seconds. It decides whether people keep watching, so it is designed fresh for every reel.
**Never reuse the previous reel's hook, and never copy the hook from an example file** (the scythe in
`scenes_example.py` belonged to one video about cutting ad campaigns — it is not a default).

## 1. Read the opening line, then pick

From the transcript, take everything said before the first full stop (usually 1.5–4 s) and write down:

- **the action** (main verb): cut, kill, replace, save, beat, steal, hide, stop, build, grow, lose, find…
- **the object**: what it is done to (a campaign, an app, money, hours, a job, a rival tool…)
- **the emotion**: shock, relief, fear of missing out, curiosity, anger, "finally"
- **any number or name** said in it (they must appear and land on their word)

Then pick the archetype whose trigger matches. Use the creator's literal words — the best hook *is* the sentence,
acted out.

| the opening says… | hook archetype | what happens on screen (dark style) | white-style version |
|---|---|---|---|
| cut / kill / delete / stop paying for X | **Destroy** | the hero tile slices, crushes, shoots or unplugs X's tile; the last hit on X's name breaks it | logo slam → shatter on the name |
| X is dead / replaced / over | **Replace** | X's tile cracks and falls; the new tile drops into its exact slot | letter-morph or swap card |
| save hours / money / do it in minutes | **Counter** | a split-flap or count-up runs the wrong way (hours draining, money piling) and lands on the spoken number | big number count-up + curve |
| faster / better / beats X | **Race** | two tiles race on a track or a gauge needle sweeps; the hero crosses first on the comparative word | versus card with bars |
| nobody tells you / hidden / secret | **Reveal** | a lens, cup, curtain or blurred card hides the thing; it is uncovered on the key word | blurred card → sharp |
| if you're still doing X… / stop doing X | **Callout** | the old way plays out (endless tabs, spinning loader, manual rows) and gets slammed shut / struck through on "stop" | crossed-out list |
| question: why / how / what if | **Question** | 🤔 rocks, question marks spring around a mystery tile, it hops on the question word | big question word pop |
| I tested / tried N things | **Lineup** | N tiles drop in a row on each count, one gets the green frame | numbered tiles 1-2-3 |
| from X to Y / before and after | **Transform** | the BEFORE state is on screen from frame 1, it flips/morphs into AFTER on the word | hookswap card |
| a number is the point ("$50k", "10x", "3 days") | **Number** | the number is the hero: split-flap or count-up landing on the spoken word, then it *does* something | giant number stamp-free pop |
| a famous name / news ("Claude just…", "Meta banned…") | **Headline** | the real app tile or a recreated real headline card; the event happens to it physically | logo + one word |
| a promise to the viewer ("you will…") | **Payoff-first** | flash the end result (finished dashboard, money, booked calendar) for 1 s, then rewind | result card → rewind |

Still no clear match? Combine the action + the object literally (e.g. "your campaigns are bleeding money" → a
campaign card with a draining red bar and coins falling out of it). Never fall back to a generic hook.

## 2. Rules every hook keeps

- **No face, physical, big:** tiles ≥ 280 px, cards ≥ 600 px wide; real app icons; something already moving on frame 0.
- **Lands on the spoken words:** one action per stressed word, the payoff exactly on the key word (`at(beat, word)`),
  impacts lead by 0.05 s, other landings by ~0.13 s.
- **The hero stays a mystery** ("?" tile) if its name is spoken later in the reel.
- **No stamped labels** (GONE, NEW, WOW) — the action itself must say it.
- **If the creator describes a hook, build exactly that** — it overrides this table.

## 3. Variety — check the history first

Before choosing, read the recent hooks:

```bash
python3 ~/.claude/skills/mehdiagent/scripts/hooks.py recent
```

Do not repeat the **archetype** used in either of the last 2 reels, and never repeat the same **prop** (scythe, gun,
race track, split-flap, scale…) within the last 5. If the best-fitting archetype was just used, keep the archetype
only if the video truly demands it and change the prop and the motion completely.

After the reel is delivered, record it:

```bash
python3 ~/.claude/skills/mehdiagent/scripts/hooks.py add --style dark --archetype Destroy --prop scythe --line "ما بقيتيش غادي تفكر واش خاصك تقطع شي campaign"
```

Tell the creator in one line which hook you picked and why ("Opening says *cut a campaign* → a scythe slices the
losing campaign cards on *تقطع*"), so they can ask for another one.
