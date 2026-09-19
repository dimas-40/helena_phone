#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# samsung_app_launcher.sh — 삼성 필수앱 ADB 런처 (패치테크: 폰 앱 → 모듈)
#
# 실측 근거: WSL 세션 ADB-SAMSUNG-APP-SWEEP-2026-08-22 (성공 19개)
#   방법: adb shell monkey -p <패키지> -c LAUNCHER — 패키지명만 알면
#         액티비티명 몰라도 즉시 실행 확인됨
#   저장: ~/termux-bridge/docs/05-adb/ADB-SAMSUNG-APP-SWEEP-2026-08-22.md (커밋 04543cf)
#         ※ 이 폰 레포에는 아직 push 안 됨 → 패키지명은 기기 자가검증으로 보정
#
# ⚠️ 금지 (의도된 보안 — 헌법 제1조급, 함정6급): 시큐어폴더(Knox TrustZone 격리)는
#    절대 시도 금지. 잠금화면 뜨면 즉시 중단, 재시도 금지.
# ⚠️ 가드레일: 본인 폰 + 승인된 ADB 조건에서만. 타인 기기 금지.
#
# 사용법:
#   samsung_app_launcher.sh --list          # 매니페스트 출력
#   samsung_app_launcher.sh --all           # 19개 전부 실행
#   samsung_app_launcher.sh 카메라          # 앱 하나만 실행 (이름/패키지)
#   PHONE_IP=1.2.3.4 samsung_app_launcher.sh --all   # IP 재정의
# ═══════════════════════════════════════════════════════════════════
set -uo pipefail

# ═══ 디바이스 설정 ═══
PHONE_IP="${PHONE_IP:-100.103.250.45}"   # 이 폰(S25) Tailscale IP (메시 기준)
ADB="${ADB:-$(command -v adb 2>/dev/null || echo /data/data/com.termux/files/usr/bin/adb)}"

# ═══ 앱 매니페스트 — 성공 18개 (WSL 2026-08-22 원본 실측 표 기준) ═══
# ✓ 원본 문서(ADB-SAMSUNG-APP-SWEEP-2026-08-22.md) 확보 후 패키지명 보정 완료.
# ⚠️ 정직 기록: 원본 표 = 18 OK / 7 FAIL (삼성 클라우드 포함), 머리글 "19 OK/6 FAIL"과 내부 불일치 — 표 기준 채택.
# 기기 pm list 검증도 그대로 유지 (이중 보정).
declare -A APPS=(
  [전화]="com.samsung.android.dialer"
  [문자]="com.samsung.android.messaging"
  [카메라]="com.sec.android.app.camera"
  [음성녹음기]="com.sec.android.app.voicenote"
  [노트]="com.samsung.android.app.notes"
  [갤러리]="com.sec.android.gallery3d"
  [마이파일]="com.sec.android.app.myfiles"
  [캘린더]="com.samsung.android.calendar"
  [연락처]="com.samsung.android.app.contacts"
  [삼성인터넷]="com.sec.android.app.sbrowser"
  [뮤직]="com.sec.android.app.music"
  [계산기]="com.sec.android.app.popupcalculator"
  [삼성헬스]="com.sec.android.app.shealth"
  [삼성패스]="com.samsung.android.samsungpass"
  [삼성월렛]="com.samsung.android.spay"
  [스마트폰찾기]="com.samsung.android.app.find"
  [SmartThings]="com.samsung.android.oneconnect"
  [게임런처]="com.samsung.android.game.gamehome"
)

# ═══ 금지 목록 — 절대 시도 금지 ═══
FORBIDDEN=("com.samsung.knox.securefolder")

# ═══ 디바이스 찾기 ═══
find_device() {
  "$ADB" devices 2>/dev/null | awk '/\tdevice$/{print $1; exit}'
}

# ═══ 무선디버깅 포트 발견 (adb 붙을 디바이스 없을 때 — 이 폰 자기 자신) ═══
scan_and_connect() {
  echo "▶ adb 연결된 디바이스 없음 → $PHONE_IP 무선디버깅 포트 스캔..."
  local pyth=$(command -v python3 || echo /usr/bin/python3)
  local ports
  ports=$("$pyth" - <<PYEOF 2>/dev/null
import socket, concurrent.futures, sys
target="$PHONE_IP"
def t(p):
    s=socket.socket(); s.settimeout(0.4)
    try: s.connect((target,p)); s.close(); return p
    except Exception: return None
with concurrent.futures.ThreadPoolExecutor(max_workers=300) as ex:
    res=list(ex.map(t, range(30000,65536)))
print('\n'.join(str(p) for p in res if p))
PYEOF
)
  [ -z "$ports" ] && { echo "  ❌ $PHONE_IP에 열린 포트 없음 — 무선디버깅(개발자 옵션) 켜졌는지 확인. WSL 메시가 이미 붙어 있으면 이 폰에서 따로 필요 없음."; return 1; }
  local ok=0
  for port in $ports; do
    local r; r=$(timeout 3 "$ADB" connect "$PHONE_IP:$port" 2>&1)
    if echo "$r" | grep -q "connected to"; then
      echo "  ✅ adb → $PHONE_IP:$port"
      ok=1; break
    fi
  done
  [ "$ok" -eq 0 ] && { echo "  ❌ 포트는 열렸지만 adb 연결 실패"; return 1; }
}

# ═══ 앱 실행 (1개) ═══
launch() {
  local name="$1" pkg="$2"
  # 금지 목록 가드
  for f in "${FORBIDDEN[@]}"; do
    [ "$pkg" = "$f" ] && { echo "  ⛔ $name — 금지 항목(Knox 격리). 시도 안 함."; return 2; }
  done
  # 패키지 존재 확인 (자가검증 — 틀린 패키지명 자동 발견)
  if ! "$ADB" shell pm list packages 2>/dev/null | grep -q "package:$pkg$"; then
    echo "  ❌ $name — 기기에 없는 패키지 ($pkg) — 이름 보정 필요"
    return 1
  fi
  "$ADB" shell monkey -p "$pkg" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
  sleep 2
  local pid; pid=$("$ADB" shell pidof "$pkg" 2>/dev/null | tr -d '\r')
  if [ -n "$pid" ]; then
    echo "  ✅ $name ($pkg) — 실행됨 pid=$pid"
    return 0
  else
    echo "  ⚠️ $name ($pkg) — 실행 시도했지만 pid 확인 안 됨 (권한팝업/백그라운드일 수 있음)"
    return 1
  fi
}

# ═══ 메인 ═══
case "${1:---list}" in
  --list)
    echo "삼성 필수앱 매니페스트 (성공 19개 · WSL 실측 기준)"
    echo "  (보고는 19개 성공, 이름 18개 명시 — 1개 push 대기 확인 필요)"
    echo "  ⛔ 금지: 시큐어폴더 (Knox TrustZone — 절대 시도 금지)"
    echo
    for k in $(printf '%s\n' "${!APPS[@]}" | sort); do
      printf '  %-14s → %s\n' "$k" "${APPS[$k]}"
    done
    ;;
  --all)
    dev=$(find_device) || true
    if [ -z "$dev" ]; then scan_and_connect || exit 1; dev=$(find_device); fi
    [ -z "$dev" ] && { echo "❌ adb 디바이스 없음"; exit 1; }
    echo "▶ 디바이스: $dev — 전부 실행"
    for k in $(printf '%s\n' "${!APPS[@]}" | sort); do
      launch "$k" "${APPS[$k]}"
    done
    ;;
  *)
    # 이름 또는 패키지로 1개 실행
    want="$1"
    found=""
    for k in "${!APPS[@]}"; do
      if [ "$k" = "$want" ] || [ "${APPS[$k]}" = "$want" ]; then found="$k"; pkg="${APPS[$k]}"; break; fi
    done
    if [ -z "$found" ]; then
      echo "❌ '$want' 매니페스트에 없음. --list로 확인."; exit 1
    fi
    dev=$(find_device) || true
    if [ -z "$dev" ]; then scan_and_connect || exit 1; dev=$(find_device); fi
    echo "▶ 디바이스: $dev"
    launch "$found" "$pkg"
    ;;
esac
