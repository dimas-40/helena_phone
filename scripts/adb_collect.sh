#!/bin/bash
# adb_collect.sh — ADB로 Android 온디바이스 데이터를 뽑아 CSV(진실의 원본)에 append
#
# ⚠️ 실행 위치: WSL(또는 adb 연결된 PC). proot에서는 adb가 안 붙음(무선디버깅 OFF).
# 이 스크립트가 "ADB ↔ 엑셀" 연결의 데이터 수집(input) 레이어다.
#   ADB(dumpsys) → data/adb_telemetry.csv → f_xlsx → 엑셀 리포트
#
# 사용법:
#   bash scripts/adb_collect.sh [device_ip:port]   # 기본 $ADB_DEVICE
# cron 등록 시:
#   */30 * * * * bash scripts/adb_collect.sh >> output/adb_collect.log 2>&1

set -u
ADB_DEVICE="${1:-${ADB_DEVICE:-}}"
CSV="data/adb_telemetry.csv"
ADB=(adb)
[ -n "$ADB_DEVICE" ] && ADB+=( -s "$ADB_DEVICE" )

TS=$(date '+%Y-%m-%d %H:%M:%S')

# ── 배터리 (level / temperature / health) ──
BATT=$("${ADB[@]}" shell dumpsys battery 2>/dev/null)
level=$(echo "$BATT" | grep -oP 'level:\s*\K[0-9]+' | head -1)
temp=$(echo "$BATT" | grep -oP 'temperature:\s*\K[0-9]+' | head -1)
health=$(echo "$BATT" | grep -oP 'health:\s*\K[0-9]+' | head -1)

# ── 메모리 (Free RAM MB) ──
MEM=$("${ADB[@]}" shell dumpsys meminfo 2>/dev/null | grep -E 'Free RAM' | head -1)
free_ram=$(echo "$MEM" | grep -oP '[0-9,]+' | tr -d ',' | head -1)

# ── 저장소 (data 파티션 사용률) ──
STOR=$("${ADB[@]}" shell df /data 2>/dev/null | tail -1)
store_pct=$(echo "$STOR" | awk '{print $5}' | tr -d '%')

# ── 헤더 (첫 실행 시) ──
[ -s "$CSV" ] || echo "timestamp,level,temp_c,health,free_ram_mb,storage_pct" > "$CSV"

# temp 는 dumpsys 기준 0.1℃ 단위(예: 320 = 32.0℃)
echo "$TS,${level:--1},${temp:--1},${health:--1},${free_ram:--1},${store_pct:--1}" >> "$CSV"

echo "✅ [$TS] 배터리 ${level:--}% · 온도 ${temp:--} · RAM ${free_ram:--}MB · 저장 ${store_pct:--}% → $CSV"
