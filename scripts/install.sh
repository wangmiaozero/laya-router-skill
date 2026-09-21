#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$HOME/.local/share/laya-router"
VENV="$BASE/.venv"
SKILL_DIR="$HOME/.agents/skills/laya-router"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "laya-router currently targets macOS Apple Silicon (arm64)." >&2
  exit 1
fi

PY="${PYTHON:-python3}"
"$PY" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required")
PY

mkdir -p "$BASE/logs" "$HOME/.agents/skills"
"$PY" -m venv "$VENV"
"$VENV/bin/python" -m pip install -U pip
"$VENV/bin/python" -m pip install laya-mlx mcp

cp "$ROOT/runtime/server.py" "$BASE/server.py"
chmod +x "$BASE/server.py"

if [[ ! -f "$BASE/config.json" ]]; then
  cat > "$BASE/config.json" <<'JSON'
{
  "enabled": true,
  "model": "aac6fef/laya-multilingual-mlx",
  "dtype": "float16",
  "device": "gpu",
  "fallback_on_error": true,
  "persist_task_text": false
}
JSON
fi

# Install/symlink skill for Codex and Pi-compatible Agent Skills discovery.
if [[ -e "$SKILL_DIR" || -L "$SKILL_DIR" ]]; then
  rm -rf "$SKILL_DIR"
fi
ln -s "$ROOT" "$SKILL_DIR"

# Best-effort Codex MCP registration. Never make installation unusable if Codex changes CLI syntax.
if command -v codex >/dev/null 2>&1; then
  codex mcp remove laya >/dev/null 2>&1 || true
  if codex mcp add laya -- "$VENV/bin/python" "$BASE/server.py" --mcp >/dev/null 2>&1; then
    echo "Codex MCP registered: laya"
  else
    echo "Warning: Codex MCP auto-registration failed. Run 'codex mcp add --help' and register:" >&2
    echo "  $VENV/bin/python $BASE/server.py --mcp" >&2
  fi
fi

echo
echo "Installed laya-router skill."
echo "Skill:   $SKILL_DIR"
echo "Runtime: $BASE"
echo "Run:     $ROOT/scripts/healthcheck.sh"
