#!/bin/bash
# adb_revive.sh — ADB mesh 자동 복구 (박씨 손길 0)
# Usage: adb_revive.sh phone|tab|all

PHONE_IP="100.103.250.45"
TAB_IP="100.74.21.77"

revive() {
  local TARGET=$1 NAME=$2

  if adb devices 2>/dev/null | grep -E "^$TARGET:.*device$" -q; then
    PORT=$(adb devices | grep -E "^$TARGET:.*device$" | head -1 | grep -oE ':[0-9]+' | tr -d ':')
    echo "▶ $NAME ($TARGET): ✅ 이미 살아있음 ($PORT)"
    return 0
  fi

  echo "▶ $NAME ($TARGET) 복구 중..."

  PORTS=$(nmap -p 30000-65535 --open -T4 -oG - $TARGET 2>/dev/null \
    | grep -oE '[0-9]+/open' | grep -oE '[0-9]+')

  for port in $PORTS; do
    r=$(timeout 3 adb connect $TARGET:$port 2>&1)
    if echo "$r" | grep -q "connected to"; then
      sleep 1
      if adb devices | grep -E "^$TARGET:$port\s.*device$" -q; then
        echo "  ✅ WSL→$TARGET:$port"
        return 0
      fi
      adb disconnect $TARGET:$port >/dev/null 2>&1
    fi
  done

  if [ "$NAME" = "폰" ]; then
    PEER=$TAB_IP; PEER_NAME="탭"
  else
    PEER=$PHONE_IP; PEER_NAME="폰"
  fi

  if ssh -p 8022 -o ConnectTimeout=3 -o StrictHostKeyChecking=no $PEER "echo OK" 2>/dev/null | grep -q OK; then
    for port in $PORTS; do
      r=$(ssh -p 8022 $PEER "adb connect $TARGET:$port" 2>&1)
      if echo "$r" | grep -q "connected to"; then
        sleep 1
        if ssh -p 8022 $PEER "adb devices" 2>/dev/null | grep -E "^$TARGET:$port\s.*device$" -q; then
          echo "  ✅ $PEER_NAME→$TARGET:$port (mesh)"
          adb connect $TARGET:$port >/dev/null 2>&1
          return 0
        fi
      fi
    done
  fi

  echo "  ❌ 실패. SSH/무선디버깅 토글 확인 필요."
  return 1
}

case "$1" in
  phone) revive "$PHONE_IP" "폰" ;;
  tab)   revive "$TAB_IP" "탭" ;;
  all|"") revive "$PHONE_IP" "폰"; revive "$TAB_IP" "탭" ;;
  *) echo "Usage: $0 phone|tab|all"; exit 1 ;;
esac

echo
echo "=== adb devices ==="
adb devices

