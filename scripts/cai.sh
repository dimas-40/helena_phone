#!/usr/bin/env bash
# cai.sh — 태블릿 Chrome 왕복.
# 2026-08-24: 라벨 있는 버튼은 scripts/hand (접근성). shot은 NEED_VISION만.
# 이 태블릿만. S25 시리얼 넣지 말 것.
set -euo pipefail

TAB="${CAI_SERIAL:-100.86.15.50:5900}"
ADB=(adb -s "$TAB")
TMP="${CAI_TMP:-/tmp/cai}"
URL="${CAI_URL:-https://grok.com/imagine}"
mkdir -p "$TMP"

die() { echo "cai: $*" >&2; exit 1; }

need_tab() {
  "${ADB[@]}" get-state >/dev/null 2>&1 || die "adb not device ($TAB). adb devices -l"
}

HAND="${CAI_HAND:-$(cd "$(dirname "$0")" && pwd)/hand/hand.py}"

cmd="${1:-}"
shift || true

case "$cmd" in
  click|find|tree|start|health)
    exec python3 "$HAND" --serial "$TAB" "$cmd" "$@"
    ;;
  serial|who)
    echo "$TAB"
    "${ADB[@]}" devices -l | grep -F "$TAB" || true
    "${ADB[@]}" shell dumpsys window 2>/dev/null | grep mCurrentFocus | head -1
    ;;
  open)
    need_tab
    "${ADB[@]}" shell am start -a android.intent.action.VIEW -d "$URL" -p com.android.chrome
    echo "opened $URL"
    ;;
  shot)
    need_tab
    name="${1:-$(date +%H%M%S)}"
    remote="/sdcard/Download/cai-${name}.png"
    local="$TMP/${name}.png"
    "${ADB[@]}" shell screencap -p "$remote"
    "${ADB[@]}" pull "$remote" "$local" >/dev/null
    echo "$local"
    ;;
  dump)
    need_tab
    remote="/sdcard/Download/cai-ui.xml"
    "${ADB[@]}" shell uiautomator dump "$remote"
    "${ADB[@]}" pull "$remote" "$TMP/ui.xml" >/dev/null
    echo "$TMP/ui.xml"
    ;;
  tap)
    need_tab
    [ $# -ge 2 ] || die "tap X Y"
    "${ADB[@]}" shell input tap "$1" "$2"
    echo "tap $1 $2"
    ;;
  swipe)
    need_tab
    [ $# -ge 4 ] || die "swipe X1 Y1 X2 Y2 [ms]"
    "${ADB[@]}" shell input swipe "$1" "$2" "$3" "$4" "${5:-300}"
    echo "swipe $1 $2 $3 $4"
    ;;
  type)
    need_tab
    [ $# -ge 1 ] || die "type 'ascii'"
    "${ADB[@]}" shell input text "$(printf '%s' "$1" | sed 's/ /%s/g')"
    ;;
  paste)
    need_tab
    "${ADB[@]}" shell input keyevent 279
    echo "paste"
    ;;
  prompt)
    need_tab
    f="${1:-}"
    [ -f "$f" ] || die "prompt FILE"
    if command -v termux-clipboard-set >/dev/null 2>&1; then
      cat "$f" | termux-clipboard-set
    else
      "${ADB[@]}" push "$f" /sdcard/Download/cai-prompt.txt >/dev/null
      die "no termux-clipboard-set. pushed /sdcard/Download/cai-prompt.txt"
    fi
    "${ADB[@]}" shell input tap 808 2251
    sleep 0.4
    "${ADB[@]}" shell input keyevent 279
    echo "prompt pasted from $f"
    ;;
  pull-images)
    dest="${1:-$TMP/images}"
    mkdir -p "$dest"
    "${ADB[@]}" shell ls /sdcard/Download/grok_image_* 2>/dev/null | while read -r p; do
      [ -n "$p" ] || continue
      "${ADB[@]}" pull "$p" "$dest/" >/dev/null || true
    done
    ls -lt "$dest" | head
    ;;
  termux)
    need_tab
    "${ADB[@]}" shell am start -n com.termux/.app.TermuxActivity
    echo "termux"
    ;;
  focus)
    need_tab
    "${ADB[@]}" shell dumpsys window 2>/dev/null | grep -E 'mCurrentFocus|mFocusedApp' | head -4
    ;;
  *)
    cat <<EOF
usage: bash scripts/cai.sh <cmd>
  health | start | click --text 완료 | find --desc '오후 2:59' | tree
  who | open | shot [name] | dump
  tap X Y | swipe X1 Y1 X2 Y2 [ms]   # last resort coords
  type 'ascii' | paste | prompt FILE
  pull-images [dest] | termux | focus
serial=$TAB
EOF
    [ -n "$cmd" ] && exit 1 || exit 0
    ;;
esac
