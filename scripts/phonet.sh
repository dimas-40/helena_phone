#!/usr/bin/env bash
# Phone T — 화면녹화 → 유튜브 규격. **폰 안에서 전부 끝난다.**
#
# ── 이게 뭔가 ──────────────────────────────────────────────────────────────
# 컨테이너(po-edit-cell)의 **백업 플랜**이다. 클라우드도, 도커도, 빌드도 없이
# 폰의 ffmpeg 하나로 같은 결과를 낸다. 컨테이너가 못 도는 상황(오프라인·레지스트리
# 장애·PC 없는 사람)에서 그대로 쓴다.
#
# ── 왜 이게 컨테이너의 '원본'인가 ──────────────────────────────────────────
# 알맹이는 scripts/yt_edit.py 하나다. 컨테이너는 이 파일에 ffmpeg 를 넣고
# py3.12-slim 으로 구운 것뿐이다. **여기가 정본이고 컨테이너가 사본이다.**
# 그래서 고칠 때도 여기를 고친다.
#
# ── 설치된 것 (폰 기준, 추가 설치 0) ───────────────────────────────────────
#   ffmpeg 8.1.2 · ffprobe · python3 — 이미 다 있다. pip 설치 없음.
#
# ── 쓰는 법 ────────────────────────────────────────────────────────────────
#   # ① job JSON 으로 (테이크 여러 개 · 컷 · 챕터를 다 쓰려면 이쪽)
#   scripts/phonet.sh job.json
#   scripts/phonet.sh job.json --dry-run      # 인코딩 없이 계획만
#
#   # ② 빠른 모드 — 파일 하나를 레인에 태운다
#   scripts/phonet.sh --quick lecture "/sdcard/DCIM/Screen recordings/xxx.mp4"
#   scripts/phonet.sh --quick narration "/sdcard/.../xxx.mp4" /sdcard/Download/out.mp4
#
#   레인   캔버스      쓰임
#   lecture   1920x1080  강의 (세로녹화를 가운데 놓고 좌우 블러)
#   tour      1920x1080  웹앱 투어
#   narration 1080x1920  쇼츠·릴스 (그대로 꽉 채움)
#
# ── 한계 (정직) ────────────────────────────────────────────────────────────
#   ・앱 자체 UI 는 못 지운다. 크롭은 시스템 상태바·내비바만 자른다.
#   ・제목·푸터의 한글은 폰트가 있어야 나온다. 폰(fc-match)엔 한글 폰트가 없어
#     지금은 영문만 확실히 나온다. 없는 글자는 **오류 없이 조용히 안 그려진다.**
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL="$HERE/yt_edit.py"

die() { echo "오류: $*" >&2; exit 1; }

[ -f "$TOOL" ] || die "yt_edit.py 를 찾지 못했습니다: $TOOL"
command -v ffmpeg  >/dev/null || die "ffmpeg 가 없습니다"
command -v ffprobe >/dev/null || die "ffprobe 가 없습니다"

# ── 빠른 모드 ──────────────────────────────────────────────────────────────
if [ "${1:-}" = "--quick" ]; then
  LANE="${2:-}"; SRC="${3:-}"; OUT="${4:-}"
  case "$LANE" in lecture|tour|narration) ;; *) die "모르는 레인입니다: '$LANE'  (lecture | tour | narration)";; esac
  [ -n "$SRC" ] || die "입력 파일을 주십시오"
  [ -f "$SRC" ] || die "입력 파일이 없습니다: $SRC"
  [ -n "$OUT" ] || OUT="/sdcard/Download/$(basename "${SRC%.*}")_${LANE}.mp4"

  TMP="$(mktemp -d /tmp/phonet.XXXXXX)"; trap 'rm -rf "$TMP"' EXIT
  # 경로에 따옴표·역슬래시가 있어도 깨지지 않게 python 으로 JSON 을 만든다.
  python3 - "$SRC" "$OUT" "$LANE" "$TMP/job.json" <<'PY'
import json, sys
src, out, lane, dst = sys.argv[1:5]
json.dump({"lane": lane, "output": out,
           "takes": [{"file": src, "title": "1. 본편", "cuts": []}]},
          open(dst, "w", encoding="utf-8"), ensure_ascii=False)
PY
  echo "레인    : $LANE"
  echo "입력    : $SRC"
  echo "출력    : $OUT"
  exec python3 "$TOOL" "$TMP/job.json"
fi

[ $# -ge 1 ] || { sed -n '3,45p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
exec python3 "$TOOL" "$@"
