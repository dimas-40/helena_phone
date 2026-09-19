#!/data/data/com.termux/files/usr/bin/bash
# 8번 — ADB 상태 확인 + shell
# Ultra S25: Samsung Android 15 무선 ADB Tailscale 차단 → SSH(8022) fallback
export PATH=/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/sbin:$PATH
export TERM=xterm-256color
export COLORTERM=truecolor
termux-wake-lock 2>/dev/null
pgrep -x sshd > /dev/null || sshd 2>/dev/null
clear

echo '╔══════════════════════════════════════════╗'
echo '║  8번 — shell 진입                        ║'
echo '║  Ultra S25 / Tab S9 / Helena S21         ║'
echo '╚══════════════════════════════════════════╝'
echo ''

WSL_IP=100.90.83.128
WSL_PORT=2222
SSH_USER=dtsli
ULTRA_IP=100.103.250.45
HELENA_IP=100.97.231.3
TABLET_IP=100.86.15.50
ADB_PORT=5555
ULTRA_SSH_PORT=8022

SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ServerAliveInterval=30"

# Ultra SSH 상태 확인 (Tailscale 직접)
echo '▶ 상태 확인...'
if timeout 5 bash -c "(echo >/dev/tcp/${ULTRA_IP}/${ULTRA_SSH_PORT}) 2>/dev/null"; then
    U_ST=ok
else
    U_ST=off
fi

# WSL 경유 ADB 상태 확인 (Tab, Helena)
if timeout 8 bash -c "(echo >/dev/tcp/${WSL_IP}/${WSL_PORT}) 2>/dev/null"; then
    ADB_OUT=$(ssh -p ${WSL_PORT} ${SSH_OPTS} ${SSH_USER}@${WSL_IP} "
for ip_port in '${TABLET_IP}:${ADB_PORT}' '${HELENA_IP}:${ADB_PORT}'; do
    ip=\${ip_port%:*}; port=\${ip_port#*:}
    if timeout 4 bash -c \"(echo >/dev/tcp/\${ip}/\${port}) 2>/dev/null\"; then
        adb connect \${ip}:\${port} >/dev/null 2>&1
        state=\$(adb -s \${ip}:\${port} get-state 2>/dev/null)
        [ \"\$state\" = device ] && echo ok || echo fail
    else
        echo off
    fi
done
" 2>/dev/null)
    T_ST=$(echo "$ADB_OUT" | sed -n '1p')
    H_ST=$(echo "$ADB_OUT" | sed -n '2p')
    WSL_OK=1
else
    T_ST=off; H_ST=off; WSL_OK=0
fi

icon() { [ "$1" = "ok" ] && echo "✅" || echo "❌"; }

echo ''
echo '  단말기 선택:'
printf '  1) S25 Ultra    %s (SSH)\n' "$(icon $U_ST)"
printf '  2) Galaxy Tab   %s (ADB)\n' "$(icon $T_ST)"
printf '  3) Helena S21   %s (ADB)\n' "$(icon $H_ST)"
echo '  0) 종료'
echo ''
read -p '선택: ' CHOICE

case "$CHOICE" in
    1)
        if [ "$U_ST" = "ok" ]; then
            # Ultra: Tailscale 직접 SSH (WSL 경유 불필요)
            ssh -p ${ULTRA_SSH_PORT} ${SSH_OPTS} -tt 100.103.250.45
        else
            echo "  ❌ Ultra SSH(${ULTRA_IP}:${ULTRA_SSH_PORT}) 불가"
            read -p 'Enter로 종료...' _
        fi
        ;;
    2)
        if [ "$T_ST" = "ok" ] && [ "$WSL_OK" = "1" ]; then
            ssh -p ${WSL_PORT} ${SSH_OPTS} -tt ${SSH_USER}@${WSL_IP} \
                "adb -s ${TABLET_IP}:${ADB_PORT} shell"
        else
            echo "  ❌ Tab ADB offline"
            read -p 'Enter로 종료...' _
        fi
        ;;
    3)
        if [ "$H_ST" = "ok" ] && [ "$WSL_OK" = "1" ]; then
            ssh -p ${WSL_PORT} ${SSH_OPTS} -tt ${SSH_USER}@${WSL_IP} \
                "adb -s ${HELENA_IP}:${ADB_PORT} shell"
        else
            echo "  ❌ Helena ADB offline"
            read -p 'Enter로 종료...' _
        fi
        ;;
    0|*) echo '  종료' ;;
esac

