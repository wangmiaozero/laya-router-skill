#!/usr/bin/env bash
set -u
BASE="$HOME/.local/share/laya-router"
PASS=1
check() { printf "%-18s %s\n" "$1" "$2"; }

if [[ "$(uname -s 2>/dev/null)" == "Darwin" && "$(uname -m 2>/dev/null)" == "arm64" ]]; then check "Platform" "OK"; else check "Platform" "FAIL"; PASS=0; fi
if [[ -x "$BASE/.venv/bin/python" ]]; then check "Python venv" "OK"; else check "Python venv" "FAIL"; PASS=0; fi
if "$BASE/.venv/bin/python" -c 'import laya_mlx' >/dev/null 2>&1; then check "laya-mlx" "OK"; else check "laya-mlx" "FAIL"; PASS=0; fi
if "$BASE/.venv/bin/python" -c 'import mlx.core' >/dev/null 2>&1; then check "MLX" "OK"; else check "MLX" "FAIL"; PASS=0; fi
if [[ -f "$BASE/config.json" && -f "$BASE/server.py" ]]; then check "Runtime files" "OK"; else check "Runtime files" "FAIL"; PASS=0; fi
if command -v codex >/dev/null 2>&1; then
  if codex mcp list 2>/dev/null | grep -qi laya; then check "Codex MCP" "OK"; else check "Codex MCP" "WARN"; fi
else
  check "Codex MCP" "SKIP"
fi

if [[ $PASS -eq 1 ]]; then
  echo "Status: READY"
  exit 0
else
  echo "Status: NOT READY"
  exit 1
fi
