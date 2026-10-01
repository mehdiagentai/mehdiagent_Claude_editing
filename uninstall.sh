#!/usr/bin/env bash
# Removes the mehdiagent skills from ~/.claude/skills. Keeps your settings and API keys unless you pass --purge.
set -euo pipefail
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
case "$SKILLS_DIR" in ""|/|"$HOME"|"$HOME/") echo "refusing to touch $SKILLS_DIR"; exit 1;; esac
for s in mehdiagent reel-dark reel-white; do
  if [ -f "$SKILLS_DIR/$s/.mehdiagent" ]; then rm -rf "$SKILLS_DIR/$s"; echo "removed $s"; fi
done
if [ "${1:-}" = "--purge" ]; then rm -rf "$HOME/.mehdiagent"; echo "removed ~/.mehdiagent (settings + API keys)"; else
  echo "kept ~/.mehdiagent (settings + API keys) — run with --purge to delete them too"; fi
echo "Optional extras stay installed; remove them in Claude Code with /plugin uninstall."
