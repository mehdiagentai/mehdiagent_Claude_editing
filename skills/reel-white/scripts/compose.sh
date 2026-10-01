#!/bin/bash
# Final composite: talking-head (bottom) + cards (top band) + subtitles + music.
# Usage: compose.sh <cut.mp4> <cards.mp4> <capt_dir> <out.mp4> [crop_y=420]
# crop_y = vertical offset of the face crop: TUNE it on the clip (a test frame) until
#          head+shoulders are well framed in the bottom band.
# Fixed layout: face in the bottom ~55% (overlay y=864), top band 0-864 black for the cards.
# The card's top band is opaque black => only the 1080x864 crop overlaps (no alpha needed).
set -e
CUT="$1"; CARDS="$2"; CAPT="$3"; OUT="$4"; CY="${5:-420}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Music: $MUSIC, else the creator's `music` setting, else none (no track is bundled - copyright).
MUSIC="${MUSIC:-$(python3 ~/.claude/skills/mehdiagent/scripts/settings.py get music 2>/dev/null | tr -d '"')}"; MUSIC="${MUSIC/#\~/$HOME}"
if [ -z "$MUSIC" ] || [ "$MUSIC" = "null" ] || [ ! -f "$MUSIC" ]; then MUSIC_IN=(-f lavfi -t 3600 -i anullsrc=r=48000:cl=stereo); MUSIC_VOL=0; else MUSIC_IN=("${MUSIC_IN[@]}"); fi
MUSIC_VOL="${MUSIC_VOL:-0.06}"   # music LOW by default (the voice must dominate)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CUT")
FOUT=$(python3 -c "print(max(0,$DUR-2))")

ffmpeg -y -i "$CUT" -i "$CARDS" -framerate 12 -i "$CAPT/%05d.png" -filter_complex \
"[0:v]scale=1080:-2,crop=1080:1056:0:$CY[v];color=c=black:s=1080x1920[bg];[bg][v]overlay=0:864:shortest=1[stage];[1:v]crop=1080:864:0:0[ctop];[stage][ctop]overlay=0:0[wc];[wc][2:v]overlay=0:78[final]" \
-map "[final]" -map 0:a -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "$OUT.noaudio.mp4"

# Audio: VOICE normalized to dialog level (loudnorm I=-16, robust for loud or quiet voice),
# MUSIC low (default 6%), the track from its 0:04 second, fade in/out.
# +faststart => moov atom up front: the file opens in QuickTime/Preview and streams online instantly.
ffmpeg -y -i "$OUT.noaudio.mp4" "${MUSIC_IN[@]}" -filter_complex \
"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[vo];[1:a]atrim=start=4,asetpts=PTS-STARTPTS,volume=$MUSIC_VOL,afade=in:st=0:d=0.5,afade=out:st=$FOUT:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
rm -f "$OUT.noaudio.mp4"
echo "DONE -> $OUT"
