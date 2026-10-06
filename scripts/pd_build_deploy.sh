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
PIECES=(01-satie-gymnopedie 02-bach-prelude-c)
SRC_ASSETS=02-bach-prelude-c/site/assets   # 공용 자산 정본은 여기 하나뿐이다

rm -rf _deploy _localtest
mkdir -p _deploy/assets _localtest
cp "$SRC_ASSETS/piano.css" "$SRC_ASSETS/piano.js" _deploy/assets/
# 목록 페이지 정본
cp 02-bach-prelude-c/site/index.html _deploy/index.html

for p in "${PIECES[@]}"; do
  d="$(ls -d */site/"$p" | head -1)"
  mkdir -p "_deploy/$p"
  cp "$d/index.html" "$d/data.js" "_deploy/$p/"
done

cp -r _deploy/. _localtest/
for p in "${PIECES[@]}"; do
  d="$(ls -d */site/"$p" | head -1)"
  cp -r "$d/img" "$d/audio" "_localtest/$p/"
done
echo "deploy:"; find _deploy -type f | sort | sed 's/^/  /'
echo "localtest: $(find _localtest -type f | wc -l) files"
