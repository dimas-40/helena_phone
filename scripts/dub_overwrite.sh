#!/usr/bin/env bash
# dub_overwrite.sh — Grok 영상 비디오 유지, 성우 wav로 오디오만 교체
# 사용: bash scripts/dub_overwrite.sh <video.mp4> <voice.wav> [out.mp4]
set -euo pipefail
VID="${1:?video}"
WAV="${2:?soVITS or other wav}"
OUT="${3:-${VID%.mp4}.dub.mp4}"
ffmpeg -y -i "$VID" -i "$WAV" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k \
  -shortest -movflags +faststart \
  "$OUT"
echo "$OUT"
ffprobe -v error -show_entries format=duration -of default=nw=1 "$OUT"
