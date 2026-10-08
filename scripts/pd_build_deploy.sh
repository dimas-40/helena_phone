#!/usr/bin/env bash
# 곡 페이지를 배포 묶음으로 조립한다.
#
#   bash scripts/pd_build_deploy.sh
#
# 결과:
#   midi_lane/pd/_deploy/       ← push 할 것만 (그림·음원 제외 — base_tree 가 나머지를 지킨다)
#   midi_lane/pd/_localtest/    ← _deploy + 그림·음원 (로컬 검사용)
#
# 왜 그림·음원을 빼나: parksy_push.py 는 Git Data API 로 blob 을 하나씩 올린다.
# 음원 8MB 를 매번 다시 올리면 커밋이 느리고 히스토리가 부푼다. base_tree 병합이라
# **트리에 없는 경로는 그대로 남는다** — 안 바뀐 것은 안 올리면 된다.
#
# 곡을 추가할 때는 PIECES 에 한 줄 늘리고 폴더 이름 규칙만 맞추면 된다.
set -euo pipefail
LANE=/root/work/midi_lane/pd
cd "$LANE"
# 폴더 이름을 자동으로 긁는다 — 곡이 48개가 되면 손으로 적는 건 반드시 틀린다.
# [0-9][0-9]- 로 좁힌다. 안 그러면 site/assets/ 같은 폴더가 곡으로 잡힌다.
PIECES=($(ls -d */site/[0-9][0-9]-*/ 2>/dev/null | sed 's|.*/site/||; s|/$||' | sort))
SRC_ASSETS=02-bach-prelude-c/site/assets   # 공용 자산 정본은 여기 하나뿐이다

rm -rf _deploy _localtest
mkdir -p _deploy/assets _localtest
cp "$SRC_ASSETS/piano.css" "$SRC_ASSETS/piano.js" _deploy/assets/
# 목록 페이지 정본
cp 02-bach-prelude-c/site/index.html _deploy/index.html

# 쪽지(index.html)가 아직 없는 곡과 **보류(NN.HOLD)된 곡**은 배포 묶음에서 뺀다.
# 왜: 채보만 끝나고 쪽지를 아직 안 쓴 곡이 하나만 있어도 cp 가 실패해
# **모든 곡의 배포가 멈췄다**(2026-10-08, 39호 때문에). 한 곡이 전체를 막지 않게 한다.
SHIP=()
SKIPPED=()
for p in "${PIECES[@]}"; do
  d="$(ls -d */site/"$p" | head -1)"
  no="${p%%-*}"
  root="${d%%/site/*}"                 # i=39-mussorgsky-goldenberg/site/39-... → 39-mussorgsky-goldenberg
  if [ -f "$root/$no.HOLD" ]; then SKIPPED+=("$p (보류 — $no.HOLD)"); continue; fi
  if [ ! -f "$d/index.html" ]; then SKIPPED+=("$p (쪽지 없음)"); continue; fi
  SHIP+=("$p")
done

for p in "${SHIP[@]}"; do
  d="$(ls -d */site/"$p" | head -1)"
  mkdir -p "_deploy/$p"
  cp "$d/index.html" "$d/data.js" "_deploy/$p/"
done

cp -r _deploy/. _localtest/
for p in "${SHIP[@]}"; do
  d="$(ls -d */site/"$p" | head -1)"
  cp -r "$d/img" "$d/audio" "_localtest/$p/"
done
echo "배포 ${#SHIP[@]}곡"
if [ ${#SKIPPED[@]} -gt 0 ]; then
  printf '뺀 곡 %d:\n' "${#SKIPPED[@]}"
  printf '  · %s\n' "${SKIPPED[@]}"
fi
echo "deploy:"; find _deploy -type f | sort | sed 's/^/  /'
echo "localtest: $(find _localtest -type f | wc -l) files"
