#!/usr/bin/env bash
set -euo pipefail
BASE="$HOME/.local/share/laya-router"
SKILL_DIR="$HOME/.agents/skills/laya-router"

if command -v codex >/dev/null 2>&1; then
  codex mcp remove laya >/dev/null 2>&1 || true
fi

if [[ -L "$SKILL_DIR" ]]; then
  rm "$SKILL_DIR"
elif [[ -d "$SKILL_DIR" ]]; then
  echo "Refusing to delete non-symlink skill directory: $SKILL_DIR" >&2
fi

rm -rf "$BASE"
echo "laya-router runtime removed. Repository checkout was not deleted."
