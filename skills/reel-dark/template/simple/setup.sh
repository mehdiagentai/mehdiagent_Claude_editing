#!/usr/bin/env bash
# usage: setup.sh <video> <topic-slug>
# Builds <projects_dir>/<YYYY-MM-DD>-<slug>/ for a pre-cut video: template, cut-out mattes (if background_removal),
# 1080x1920 edit master with PCM audio, and the transcript (Fish or Gemini/OpenRouter, from the creator's settings).
set -e
SRC="$1"; SLUG="${2:-reel}"
[ -f "$SRC" ] || { echo "video not found: $SRC"; exit 1; }
SK=~/.claude/skills/reel-dark; M=~/.claude/skills/mehdiagent/scripts
ROOT=$(python3 $M/settings.py get projects_dir | tr -d '"'); ROOT=${ROOT/#\~/$HOME}
BGR=$(python3 $M/settings.py get background_removal)
P="$ROOT/$(date +%F)-$SLUG"; [ -e "$P" ] && P="$P-$(date +%H%M)"
mkdir -p $P/{edit,renders,review,audio/sources}
rsync -a --exclude __pycache__ --exclude simple $SK/template/ $P/
cp $SK/template/simple/{render.py,mix.py,prepare.py} $P/
cp $SK/template/simple/scenes_example.py $P/scenes.py        # starting point - rewrite the scenes for this script
cp "$SRC" "$P/audio/sources/source.${SRC##*.}"
cd $P; IN="audio/sources/source.${SRC##*.}"
echo "• edit master (1080x1920, 30 fps)"
ffmpeg -v error -y -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" -c:v libx264 -crf 12 -preset fast -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 edit/tight.mkv
if [ "$BGR" = "true" ]; then
  ffmpeg -v error -y -i edit/tight.mkv -an -c:v libx264 -crf 12 -pix_fmt yuv420p edit/matte-src.mp4   # AVFoundation can't read .mkv
  if [ "$(uname -s)" = "Darwin" ] && [ "${MEHDIAGENT_PORTABLE:-}" != "1" ] && command -v swiftc >/dev/null; then
    echo "• background cut-out (Apple Vision, ~1-2 min per pass)"
    swiftc -O helpers/personmask.swift -o helpers/personmask 2>/dev/null
    for m in person subject; do ./helpers/personmask edit/matte-src.mp4 1080 1920 $m 1 | ffmpeg -v error -y -f rawvideo -pix_fmt gray -s 1080x1920 -r 30 -i - -c:v ffv1 edit/mask_$m.mkv; done
  else
    echo "• background cut-out (rembg + MediaPipe, open-source - ~8 min for 35 s)"
    VENV="$HOME/.mehdiagent/venv-rembg"; VPY="$VENV/bin/python"; [ -x "$VPY" ] || VPY="$VENV/Scripts/python.exe"
    if [ ! -x "$VPY" ]; then
      python3 -m venv "$VENV"; VPY="$VENV/bin/python"; [ -x "$VPY" ] || VPY="$VENV/Scripts/python.exe"
      "$VPY" -m pip install -q --upgrade pip; "$VPY" -m pip install -q "rembg[cpu]" mediapipe pillow numpy
    fi
    "$VPY" helpers/personmask_rembg.py edit/matte-src.mp4 edit 1080 1920
  fi
fi
echo "• transcript"
python3 $M/transcribe.py edit/tight.mkv --edit-dir edit
python3 prepare.py | head -400
echo "$P"
