#!/bin/bash
# White popout composite: white cards base + frame shadow + rounded video frame + head
# popout RGBA sequence + black captions. Then loudnorm+music. SFX remix is a separate pass.
# Usage: compose_white.sh <cutF.mp4> <cards_white.mp4> <capt_dir> <seg_dir> <out.mp4>
#   seg_dir must contain: frame_mask.png (1020x810 r36), frame_shadow.png (1080x1920),
#   popout/%05d.png (RGBA strips, 25fps). Layout: offset +450, frame (30,1080)-(1050,1890),
#   popout overlay at 0:870. Tune offsets per clip via the head-top probe (see SKILL.md).
set -e
CUT="$1"; CARDS="$2"; CAPT="$3"; SEG="$4"; OUT="$5"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Music: $MUSIC, else the creator's `music` setting, else none (no track is bundled - copyright).
MUSIC="${MUSIC:-$(python3 ~/.claude/skills/mehdiagent/scripts/settings.py get music 2>/dev/null | tr -d '"')}"; MUSIC="${MUSIC/#\~/$HOME}"
if [ -z "$MUSIC" ] || [ "$MUSIC" = "null" ] || [ ! -f "$MUSIC" ]; then MUSIC_IN=(-f lavfi -t 3600 -i anullsrc=r=48000:cl=stereo); MUSIC_VOL=0; else MUSIC_IN=("${MUSIC_IN[@]}"); fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CUT")
FOUT=$(python3 -c "print(max(0,$DUR-2))")
ffmpeg -y -v error -i "$CUT" -i "$CARDS" -loop 1 -i "$SEG/frame_mask.png"  -framerate 25 -i "$SEG/popout/%05d.png" -framerate 12 -i "$CAPT/%05d.png" -loop 1 -i "$SEG/frame_shadow.png"  -filter_complex "[0:v]scale=1080:-2,crop=1020:810:30:630[vf];[2:v]format=gray[mk];[vf][mk]alphamerge[vfa];[1:v][5:v]overlay=0:0:shortest=1[s0];[s0][vfa]overlay=30:1080[s1];[s1][3:v]overlay=0:870[s2];[s2][4:v]overlay=0:78[final]"  -map "[final]" -map 0:a -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "$OUT.noaudio.mp4"
ffmpeg -y -v error -i "$OUT.noaudio.mp4" "${MUSIC_IN[@]}" -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[vo];[1:a]atrim=start=4,asetpts=PTS-STARTPTS,volume=${MUSIC_VOL:-0.06},afade=in:st=0:d=0.5,afade=out:st=$FOUT:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]"  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
rm -f "$OUT.noaudio.mp4"
echo "DONE -> $OUT"
