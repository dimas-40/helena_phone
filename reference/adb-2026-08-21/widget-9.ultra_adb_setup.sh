#!/data/data/com.termux/files/usr/bin/bash
# Ultra ADB 최초 설정 — pm grant WRITE_SECURE_SETTINGS 1회용
# 이후 재부팅마다 자동 (다시 실행 불필요)

export PATH=/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/sbin:$PATH
export TERM=xterm-256color
termux-wake-lock 2>/dev/null

WSL_IP="100.90.83.128"
WSL_PORT="2222"
SSH_USER="dtsli"
ULTRA_IP="100.103.250.45"

clear
echo '╔══════════════════════════════════════════╗'
echo '║  9번 — Ultra ADB 최초 설정 (1회용)       ║'
echo '║  설정>개발자옵션>무선디버깅 화면 열어둬  ║'
echo '╚══════════════════════════════════════════╝'
echo ''
echo '  ADB 디버깅 주소의 포트 번호만 입력'
echo '  (예: 100.103.250.45:46515 → 46515)'
echo ''
read -p '  포트: ' ADB_PORT

[ -z "$ADB_PORT" ] && echo '❌ 포트 없음' && exit 1

echo "  ▶ WSL에서 연결 + pm grant 실행..."

ssh -p ${WSL_PORT} -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
  ${SSH_USER}@${WSL_IP} "
ULTRA_IP=${ULTRA_IP}
ADB_PORT=${ADB_PORT}

echo '[1/3] ADB 연결'
adb disconnect \${ULTRA_IP} 2>/dev/null
adb connect \${ULTRA_IP}:\${ADB_PORT} && sleep 3

STATE=\$(adb -s \${ULTRA_IP}:\${ADB_PORT} get-state 2>/dev/null)
if [ \"\$STATE\" != 'device' ]; then echo '❌ 연결 실패'; exit 1; fi
echo '✅ 연결됨'

echo '[2/3] pm grant'
adb -s \${ULTRA_IP}:\${ADB_PORT} shell pm grant com.termux android.permission.WRITE_SECURE_SETTINGS && echo '✅ 권한 완료'

echo '[3/3] boot_adb.sh 배포'
adb -s \${ULTRA_IP}:\${ADB_PORT} shell 'mkdir -p ~/.termux/boot && cat > ~/.termux/boot/adb-tcp.sh << EOF
#!/data/data/com.termux/files/usr/bin/bash
exec >> \"\$HOME/.termux/boot/adb-tcp.log\" 2>&1
sleep 15
pgrep -x sshd || sshd 2>/dev/null
settings put global adb_wifi_enabled 1 2>/dev/null && echo adb_wifi ON
adb kill-server 2>/dev/null; sleep 2; adb start-server 2>/dev/null; adb tcpip 5555 2>/dev/null
EOF
chmod +x ~/.termux/boot/adb-tcp.sh && echo boot_script_ok'

echo '✅ 완료 — 다음 재부팅부터 ADB 자동'
"

read -p 'Enter로 종료...' _

