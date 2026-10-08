#!/usr/bin/env bash
# 곡 하나의 그림·음원만 parksy.kr 에 올린다.
#
#   bash scripts/pd_push_assets.sh 12-ravel-alborada-del-gracioso "[커밋메시지]"
#
# 왜 이 스크립트가 있나:
#   pd_build_deploy.sh 의 _deploy 에는 index.html·data.js 만 들어간다(그림·음원 제외).
#   그래서 자산은 따로 올려야 하는데, **곡 폴더를 그대로 parksy_push 에 넘기면
#   page.py 와 __pycache__ 까지 같이 올라가 우리 소스가 공개 사이트에 새어 나간다.**
#   2026-10-08 에 12호에서 실제로 그랬다(page.py·.pyc 가 200 으로 서빙됨).
#   그래서 여기서는 /tmp 에 **img·audio 만 복사한 임시 폴더**를 만들어 그것만 넘긴다.
#
# 곡 폴더(site/<slug>)에서 img/ 와 audio/ 를 찾는다. 둘 다 없으면 아무 것도 안 한다.
set -euo pipefail

SLUG="${1:?곡 슬러그를 주세요 (예: 12-ravel-alborada-del-gracioso)}"
MSG="${2:-$SLUG 자산(그림·음원)}"

LANE=/root/work/midi_lane/pd
SRC="$(ls -d "$LANE"/*/site/"$SLUG" 2>/dev/null | head -1)"
[ -n "$SRC" ] && [ -d "$SRC" ] || { echo "곡 폴더를 찾지 못했다: $SLUG" >&2; exit 1; }

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

n=0
for sub in img audio; do
  if [ -d "$SRC/$sub" ]; then
    cp -r "$SRC/$sub" "$STAGE/"
    n=$(( n + $(find "$SRC/$sub" -type f | wc -l) ))
  fi
done
if [ "$n" -eq 0 ]; then
  echo "img·audio 가 없다 — 올릴 것이 없다 ($SRC)" >&2
  exit 0
fi

# 확실히 우리 소스가 안 섞였는지 확인한다 — 이 스크립트의 존재 이유가 이것이다.
if find "$STAGE" -name '*.py' -o -name '*.pyc' -o -name '__pycache__' | grep -q .; then
  echo "중단: 임시 폴더에 파이썬 파일이 섞였다 — 소스가 공개된다" >&2
  find "$STAGE" -name '*.py' -o -name '*.pyc' >&2
  exit 1
fi

# 큰 것부터 보이게 (음원이 대개 가장 크다)
find "$STAGE" -type f -printf '%s\t%p\n' | sort -rn | awk -F'\t' '{printf "  %10d B  %s\n", $1, $2}'

set -a; . /root/work/.secrets.env; set +a
python3 /root/work/scripts/parksy_push.py \
  "$STAGE" "channel/musician/piano/$SLUG" "$MSG"
