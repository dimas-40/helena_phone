#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot ADB TCP 자동 활성화 훅
# 설치 위치: ~/.termux/boot/adb-tcp.sh (타깃 기기에서)
# Helena S21 / Galaxy Tab S9 공용

exec >> "$HOME/.termux/boot/adb-tcp.log" 2>&1
echo "[$(date)] ADB boot hook 시작"

# 시스템 완전 부팅 대기
sleep 15

# sshd 기동
pgrep -x sshd || sshd 2>/dev/null
echo "[$(date)] sshd OK"

# 루팅 있는 경우 — setprop으로 영구 TCP 5555 + iptables Tailscale 제한
if su -c 'id' 2>/dev/null | grep -q 'uid=0'; then
    su -c '
        setprop service.adb.tcp.port 5555
        stop adbd
        start adbd
        sleep 2
        # ADB를 tailscale0 인터페이스에만 허용
        if ip link show tailscale0 > /dev/null 2>&1; then
            iptables -D INPUT -p tcp --dport 5555 -j DROP 2>/dev/null || true
            iptables -A INPUT -i tailscale0 -p tcp --dport 5555 -j ACCEPT
            iptables -A INPUT -p tcp --dport 5555 -j DROP
            echo "iptables: ADB restricted to tailscale0"
        fi
    ' 2>/dev/null && echo "[$(date)] root ADB TCP 5555 OK" \
                  || echo "[$(date)] root ADB 실패"
else
    # 루팅 없는 경우 — WRITE_SECURE_SETTINGS 권한으로 무선 디버깅 자동 ON
    if settings put global adb_wifi_enabled 1 2>/dev/null; then
        echo "[$(date)] 무선 디버깅 자동 ON (WRITE_SECURE_SETTINGS OK)"
        sleep 3
    else
        echo "[$(date)] WRITE_SECURE_SETTINGS 없음 — 무선 디버깅 수동 필요"
        echo "[$(date)] 해결: 8번 위젯 → 옵션 5 (최초 1회 ADB 권한 부여)"
    fi
    adb kill-server 2>/dev/null
    sleep 2
    adb start-server 2>/dev/null
    adb tcpip 5555 2>/dev/null
    echo "[$(date)] non-root ADB tcpip 5555 시도"
fi

echo "[$(date)] ADB boot hook 완료"

