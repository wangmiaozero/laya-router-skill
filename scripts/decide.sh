#!/usr/bin/env bash
set -euo pipefail
BASE="$HOME/.local/share/laya-router"
if [[ $# -lt 1 ]]; then
  echo "usage: $0 <task>" >&2
  exit 2
fi
exec "$BASE/.venv/bin/python" "$BASE/server.py" "$*"
