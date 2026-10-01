#!/usr/bin/env bash
# mehdiagent — Claude Code video-editing skills. Installs into ~/.claude/skills and prepares ~/.mehdiagent.
#   ./install.sh               interactive (asks before installing anything)
#   ./install.sh --yes         say yes to the required Python packages, skip the optional extras
#   ./install.sh --with-extras also install ui-ux-pro-max and caveman (official plugins)
# Safe to re-run: it updates the skills, never touches your settings or API keys.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
HOME_DIR="$HOME/.mehdiagent"
YES=0; EXTRAS=ask
for a in "$@"; do case "$a" in --yes|-y) YES=1; [ "$EXTRAS" = ask ] && EXTRAS=no;; --with-extras) EXTRAS=yes;; --no-extras) EXTRAS=no;; esac; done
b(){ printf "\033[1m%s\033[0m\n" "$*"; }; ok(){ printf "  \033[32m✓\033[0m %s\n" "$*"; }; warn(){ printf "  \033[33m!\033[0m %s\n" "$*"; }
ask(){ [ $YES = 1 ] && return 0; [ -t 0 ] || return 1; read -r -p "  $1 [y/N] " r; [[ "$r" =~ ^[Yy] ]]; }

b "mehdiagent installer"
OS=$(uname -s)
[ "$OS" = Darwin ] && ok "macOS — both styles, exact Apple fonts" || ok "$OS — both styles (open fonts + rembg background removal)"

b "1/4  Tools"
command -v python3 >/dev/null || { warn "Python 3 is missing → install it from https://www.python.org/downloads/ and re-run"; exit 1; }
ok "python3 $(python3 -c 'import platform;print(platform.python_version())')"
if command -v ffmpeg >/dev/null; then ok "ffmpeg"; else
  warn "ffmpeg is missing (needed to read and write video)"
  if command -v brew >/dev/null && ask "Install ffmpeg with Homebrew now?"; then brew install ffmpeg; else
    echo "     → macOS: install Homebrew (https://brew.sh) then: brew install ffmpeg | Windows: winget install ffmpeg | Linux: sudo apt install ffmpeg"; fi
fi
command -v node >/dev/null && ok "Node.js (white style cards)" || warn "Node.js missing — needed only for the WHITE style → https://nodejs.org (LTS)"
[ "$OS" = Darwin ] && { command -v swiftc >/dev/null && ok "Swift (background removal)" || warn "Swift missing — needed for background removal → run: xcode-select --install"; }
[ "$OS" != Darwin ] && ok "background removal: rembg installs itself on your first reel (~2 min, once)"

b "2/4  Python packages"
missing=()
for m in numpy:numpy PIL:pillow requests:requests arabic_reshaper:arabic-reshaper torch:torch torchaudio:torchaudio; do
  python3 -c "import ${m%%:*}" 2>/dev/null && ok "${m#*:}" || missing+=("${m#*:}")
done
if [ ${#missing[@]} -gt 0 ]; then
  warn "missing: ${missing[*]}"
  if ask "Install them now with pip (python3 -m pip install --user …)?"; then
    plain=(); for p in "${missing[@]}"; do [ "$p" != torchaudio ] && plain+=("$p"); done
    [ ${#plain[@]} -gt 0 ] && python3 -m pip install --user "${plain[@]}"
    if [[ " ${missing[*]} " == *" torchaudio "* ]]; then
      TV=$(python3 -c 'import torch;print(torch.__version__.split("+")[0])')
      python3 -m pip install --user "torchaudio==$TV" 2>/dev/null || {
        # torchaudio stopped publishing for some torch versions: newest one, without letting pip change torch
        warn "no torchaudio $TV for this Python — installing the newest compatible build next to torch $TV"
        python3 -m pip install --user --no-deps torchaudio; }
      python3 -c "import torchaudio" && ok "torchaudio" || warn "torchaudio still failing — run the doctor after install"
    fi
  else warn "skipped — the doctor will remind you"; fi
fi

b "3/4  Skills → $SKILLS_DIR"
case "$SKILLS_DIR" in ""|/|"$HOME"|"$HOME/") echo "refusing to install into $SKILLS_DIR"; exit 1;; esac
mkdir -p "$SKILLS_DIR"
for s in "$REPO"/skills/*/; do
  name=$(basename "$s"); dest="$SKILLS_DIR/$name"
  if [ -e "$dest" ] && [ ! -f "$dest/.mehdiagent" ]; then
    bk="$HOME/.claude/skills-backup/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$bk"; mv "$dest" "$bk/"; warn "existing $name moved to $bk"
  fi
  rm -rf "$dest"; cp -R "$s" "$dest"; echo "$(cd "$REPO" && git rev-parse --short HEAD 2>/dev/null || echo local)" > "$dest/.mehdiagent"
  find "$dest" -name '__pycache__' -prune -exec rm -rf {} +
  ok "$name"
done
mkdir -p "$HOME_DIR"; python3 "$SKILLS_DIR/mehdiagent/scripts/settings.py" init-env >/dev/null
ok "settings folder $HOME_DIR (your API key goes in $HOME_DIR/.env — never in a chat)"

b "4/4  Optional extras (official plugins, installed from their own GitHub repos)"
extra(){ # $1 label  $2 marketplace repo  $3 plugin@marketplace
  if ! command -v claude >/dev/null; then warn "Claude Code CLI not found — install $1 later: /plugin marketplace add $2"; return; fi
  if [ "$EXTRAS" = yes ] || { [ "$EXTRAS" = ask ] && ask "Install $1?"; }; then
    claude plugin marketplace add "$2" >/dev/null 2>&1 || true
    claude plugin install "$3" && ok "$1" || warn "$1 failed — inside Claude Code run: /plugin marketplace add $2 then /plugin install $3"
  fi; }
extra "ui-ux-pro-max (design intelligence for UI/cards, MIT — nextlevelbuilder)" nextlevelbuilder/ui-ux-pro-max-skill ui-ux-pro-max@ui-ux-pro-max-skill
extra "caveman (shorter, cheaper Claude answers, Apache-2.0 — Julius Brussee)" JuliusBrussee/caveman caveman@caveman

echo; b "Done."
echo "  Next: open Claude Code anywhere and type   /mehdiagent"
echo "  It asks a few questions once (dark or white style, your language, captions, API key…), then send it a video."
echo "  Check your setup any time:  python3 $SKILLS_DIR/mehdiagent/scripts/doctor.py"
