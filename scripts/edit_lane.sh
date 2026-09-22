#!/usr/bin/env bash
# edit_lane.sh — 화면녹화 → 유튜브 규격. **레인 이름 하나로 결정된다.**
#
# ── 왜 이 스크립트가 있나 ──────────────────────────────────────────────────
# 2026-09-22, 폰 화면녹화 하나를 손으로 편집해 봤다. 명령어를 손으로 조립했더니
# 길고, 매번 조금씩 달라지고, 무엇보다 **왜 그 값을 썼는지가 안 남는다.**
# 그래서 레인별로 값을 한 곳에 모으고 명령을 여기서만 만든다.
#
# ── 설계 근거 (전부 실측, 2026-09-22 S25 Ultra) ────────────────────────────
# ① 배경은 **한 장 만들어 재사용**한다. 매 프레임 블러하면 15초 편집이 38초,
#    한 장으로 만들면 12초. 블러는 배경이 안 변하는데도 매번 다시 계산되고 있었다.
# ② **하드웨어 인코더(h264_mediacodec)를 쓰지 않는다.** proot 에서 무한 대기하고
#    SIGTERM 도 무시한다(7시간째 돌던 걸 발견해 kill -9 로 죽였다).
# ③ 크롭 값은 앱스토어 PWA 에서 가져왔다 — lecture-long/app.js:64 의
#    CONFIG.devices.S25_ULTRA { topCutPct: 0.090, bottomCutPct: 0.040 }.
#    상태바·내비바를 잘라낸다. 추측값이 아니라 그 앱이 쓰던 값이다.
#
# ── 쓰는 법 ────────────────────────────────────────────────────────────────
#   scripts/edit_lane.sh lecture   "/sdcard/DCIM/Screen recordings/xxx.mp4"
#   scripts/edit_lane.sh narration "/sdcard/.../xxx.mp4" /sdcard/Download/out.mp4
#
#   레인   캔버스      배치
#   lecture   1920x1080 가로   세로녹화를 가운데 놓고 좌우 블러 배경 (강의)
#   narration 1080x1920 세로   그대로 꽉 채움 — 쇼츠/릴스 (내레이션)
#   tour      1920x1080 가로   웹앱 투어
#
# 환경변수로 덮어쓰기 (안 주면 레인 기본값):
#   TITLE=  FOOTER=  BGM=  CRF=  FPS=  TOP_CUT=  BOTTOM_CUT=  OUT=
#
# ── 한계 (정직) ────────────────────────────────────────────────────────────
# ・**앱 자체 UI 는 못 지운다.** 크롭은 시스템 상태바·내비바만 자른다.
#   앱 하단 좋아요/댓글 바 같은 건 콘텐츠라 프리셋으로 안 지워진다 —
#   녹화할 때 숨겨야 한다. 후보정으로 지우려면 화면을 더 잘라먹어야 한다.
# ・자막은 안 넣는다. 폰 브라우저 PWA 4종에 자막 기능이 아예 없었고,
#   서버쪽 drawtext 를 참고해 넣을 수는 있지만 아직 안 했다.
# ・소리에 오디오가 있어야 한다고 가정한다(화면녹화 기본값).

set -euo pipefail

LANE="${1:-}"
SRC="${2:-}"
OUT_ARG="${3:-}"

die() { echo "오류: $*" >&2; exit 1; }

[ -n "$LANE" ] && [ -n "$SRC" ] || {
  sed -n '3,40p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}
[ -f "$SRC" ] || die "입력 파일이 없습니다: $SRC"
command -v ffmpeg >/dev/null || die "ffmpeg 가 없습니다"

# ── 레인 정의 ──────────────────────────────────────────────────────────────
case "$LANE" in
  lecture)   CANVAS="1920x1080"; TITLE_D="${TITLE:-}" ; FOOTER_D="dtslib.kr" ;;
  tour)      CANVAS="1920x1080"; TITLE_D="${TITLE:-}" ; FOOTER_D="dtslib.kr" ;;
  narration) CANVAS="1080x1920"; TITLE_D="${TITLE:-}" ; FOOTER_D="" ;;
  *) die "모르는 레인입니다: $LANE  (lecture | narration | tour)" ;;
esac

# S25 Ultra 화면녹화 크롭 (lecture-long/app.js:64 에서 가져온 값)
TOP_CUT="${TOP_CUT:-0.090}"
BOTTOM_CUT="${BOTTOM_CUT:-0.040}"

CRF="${CRF:-20}"
FPS="${FPS:-30}"
TITLE="${TITLE:-$TITLE_D}"
FOOTER="${FOOTER:-$FOOTER_D}"
BG_BLUR="${BG_BLUR:-40}"
BG_DARK="${BG_DARK:-0.18}"
BGM="${BGM:-}"
BG_VOL="${BG_VOL:-0.25}"

IN_W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width  -of csv=p=0 "$SRC")
IN_H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$SRC")
[ -n "$IN_W" ] && [ -n "$IN_H" ] || die "영상 크기를 못 읽었습니다: $SRC"

CROP_H=$(python3 -c "print(max(2,int($IN_H*(1-$TOP_CUT-$BOTTOM_CUT))//2*2))")
CROP_Y=$(python3 -c "print(int($IN_H*$TOP_CUT))")
CROP="crop=${IN_W}:${CROP_H}:0:${CROP_Y}"

OUT="${OUT_ARG:-/sdcard/Download/$(basename "${SRC%.*}")_${LANE}.mp4}"
TMP=$(mktemp -d /tmp/editlane.XXXXXX)
trap 'rm -rf "$TMP"' EXIT

echo "레인    : $LANE  (캔버스 $CANVAS)"
echo "입력    : $SRC  ${IN_W}x${IN_H}"
echo "크롭    : y=$CROP_Y 부터 ${CROP_H}px  (상단 $TOP_CUT / 하단 $BOTTOM_CUT)"
echo "출력    : $OUT"

CW=${CANVAS%x*}; CH=${CANVAS#*x}
PORTRAIT_CANVAS=0; [ "$CH" -gt "$CW" ] && PORTRAIT_CANVAS=1

# ── ① 배경 한 장 (가로 캔버스일 때만. 이게 3배 빠르게 만든 부분) ───────────
VF_PARTS=()
INPUTS=(-i "$SRC")

if [ "$PORTRAIT_CANVAS" -eq 0 ]; then
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -frames:v 1 \
    -vf "${CROP},scale=${CW}:${CH}:force_original_aspect_ratio=increase,crop=${CW}:${CH},gblur=sigma=${BG_BLUR},eq=brightness=-${BG_DARK}:saturation=1.1" \
    "$TMP/bg.png"
  INPUTS+=(-loop 1 -i "$TMP/bg.png")
  FG_IN="[0:v]${CROP},scale=-2:${CH}:flags=lanczos[fg];"
  BASE="[1:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1"
else
  # 세로 캔버스는 배경이 필요 없다 — 그대로 꽉 채운다
  FG_IN="[0:v]${CROP},scale=${CW}:${CH}:force_original_aspect_ratio=increase,crop=${CW}:${CH}[bg0];[bg0]null[fg];"
  BASE="[fg]null"
fi

# ── ② 글자 ─────────────────────────────────────────────────────────────────
FONT=$(fc-match -f "%{file}" sans 2>/dev/null || echo "")
DRAW=""
if [ -n "$TITLE" ] && [ -n "$FONT" ]; then
  DRAW="${DRAW},drawtext=fontfile='${FONT}':text='${TITLE}':x=70:y=70:fontsize=52:fontcolor=white@0.9"
fi
if [ -n "$FOOTER" ] && [ -n "$FONT" ]; then
  DRAW="${DRAW},drawtext=fontfile='${FONT}':text='${FOOTER}':x=w-tw-70:y=h-110:fontsize=40:fontcolor=white@0.75"
fi

# ── ③ 소리 — loudnorm 은 앱스토어 clip-shorts/app.js:568 에서 가져온 값 ──────
AUDIO_IN="[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
if [ -n "$BGM" ]; then
  [ -f "$BGM" ] || die "BGM 파일이 없습니다: $BGM"
  # ⚠️ BGM 입력 번호를 하드코딩하면 안 된다 — 가로 캔버스일 때만 배경 PNG 가
  #    끼어들어 번호가 하나 밀린다. 세로 레인에서 조용히 엉뚱한 스트림을 집는다.
  BGM_IDX=${#INPUTS[@]}
  BGM_IDX=$((BGM_IDX / 2))          # -i 마다 인자 2개씩 → 입력 개수
  INPUTS+=(-stream_loop -1 -i "$BGM")
  AUDIO_IN="[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[nar];[${BGM_IDX}:a]volume=${BG_VOL},aresample=48000[bg];[nar][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
  echo "BGM     : $BGM  (볼륨 ${BG_VOL}, 입력 #${BGM_IDX})"
fi

FC="${FG_IN}${BASE}${DRAW},format=yuv420p[vout];${AUDIO_IN}"

echo "인코딩 시작..."
S=$(date +%s)
ffmpeg -hide_banner -loglevel error -y "${INPUTS[@]}" \
  -filter_complex "$FC" \
  -map "[vout]" -map "[aout]" \
  -r "$FPS" -c:v libx264 -preset veryfast -crf "$CRF" \
  -c:a aac -b:a 192k -movflags +faststart \
  "$OUT"
echo "끝. $(( $(date +%s)-S ))초 걸렸습니다."
ls -lh "$OUT" | awk '{print "크기:", $5}'
