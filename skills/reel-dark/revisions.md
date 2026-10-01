# Revision recipes (voice cut and visuals)

All timings are seconds on the reel timeline. Word onsets/ends come from `edit/transcript.json`
(Fish Audio + local word alignment, final cut). Beats in `edit/beats.json`. Segments are `edit/segments/NN.mkv`, listed in
`edit/concat.txt`; `edit/tight.mkv` is their stream-copy concat. Master is the aligned camera file
in the original project (`edl.json.sources.src`).

Always: `cp edit/tight.mkv edit/tight-vN.mkv` before changing the cut.

## Remove a whole beat ("cut the part where I say …")
1. Find the beat in `beats.json`; `dur = end - start`.
2. Drop its range from `edl.json`, drop its `file 'segments/NN.mkv'` line from `concat.txt`,
   re-concat with `ffmpeg -f concat -safe 0 -i edit/concat.txt -c copy edit/tight.mkv`.
3. `beats.json`: delete the beat, shift every later beat by −dur.
4. `transcript.json`: delete words inside the beat, shift later words by −dur.
5. Remove the beat from `FULL`/`CAPY` in `render.py`, any cue for it in `mix.py`, its branch in `scenes.py`.
6. Splice audit: `python3 ~/.claude/skills/reel-dark/scripts/splice_audit.py edit/edl.json edit/tight.mkv --language en`
   and quote the new join text in the report.

## Remove a word inside a take ("making on its own" → "making its own")
1. Fine RMS scan (5–10 ms) around the word; cut from the trough after the previous word's end to
   just before the next word's onset (protect ~30 ms of the onset). Snap both to 1/30 s frames.
2. Map cut points to master time: `master = range.start + (cut − beat.start)`.
3. Re-encode the take as two segments `NNa`/`NNb` with the template encode
   (`fps=30`, `pcm_s16le`, 4 ms fade in/out), replace `NN` in `concat.txt`, split the edl range.
4. Shift beats/words after the cut by the removed duration. Re-insert any word the filter dropped
   whose onset moved (keep its text, new start = cut point).
5. Splice-audit the new join (`scripts/splice_audit.py`); it must read the intended phrase.

## Trim the head of a take ("is that they have taken" → "they have taken")
Same as above but only the segment start moves: `range.start += floor((word.start − beat.start − .03)*30)/30`;
re-encode that segment, shorten that beat, shift later beats/words.

## Timing feels late
Lead the visual by 0.13 s (`ons = at(...) − .13`) and shorten the spring (≈0.26 s). Don't move the voice.

## "Empty screen" complaint
Something must move for the whole beat: staggered block build, selection frame hopping with a size
label, paint sweep, cursor route, pile-up. Check with a strip at 0.2/0.6/1.0/1.5 s.

## Transparent-looking element
Either draw order (composite the focused element last) or translucent fills replacing alpha.
`draw.rr` blends RGBA fills with alpha < 255; keep it that way.

## After any change
Before re-rendering: no word stamps/labels over scenes (rule 32), and no link chip in the CTA (rule 20).
`python3 render.py && python3 mix.py`, then the gates, extract frames at the changed times,
repack the editable zip, `SendUserFile` the MP4, update README (duration, scene table, cue count).

## Wrong product name in the recording (the creator said "Acmi", the product is "Acme")
Never patch the voice. Put the real name on every surface and in `prepare.py` `FIX` (`12: "Acme,"`) so the
caption carries it, keep `at()` lookups on the corrected token, and lead the delivery note with the mismatch plus
the exact one-line re-record that would remove it. If the creator re-records, cut the new line as its own beat
(its own segment), keep the old cut as `edit/tight-vN.mkv`, re-run `~/.claude/skills/mehdiagent/scripts/transcribe.py` + `prepare.py` + the splice audit.

## A take that runs on into an aborted sentence ("…write code, but where it takes around 200—")
Find the 20–40 ms trough between the last wanted word and the next onset on the 10 ms RMS profile, pin the end with
`FORCE_END` (whole frames, never past the trough) and give that beat a 12–15 ms `FADE_OUT`. The splice audit must read
the join as one sentence.

## "Make the hook X does Y to Z"
Build it as one function: hits on the stressed words (`at()` lead 0.05 s), swap the prop and the per-hit effect, keep the
break on the rival's name. Preview with a 3×2 sheet of 540 px frames, not only the thin strip.
