#!/usr/bin/env bash
# hand.sh — S25/탭 공통. 접근성 레이더. 비전 좌표 금지.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$ROOT/hand.py" "$@"
