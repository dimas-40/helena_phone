#!/usr/bin/env bash
# relay.sh — 폰 ↔ 랩탑 에이전트 통신선 (폰 쪽 끝)
#
# 랩탑에 있는 ~/agent-relay/ 메일박스를 SSH 너머로 읽고 쓴다.
# 폰과 랩탑의 Claude 가 사람을 거치지 않고 주고받기 위한 것.
#
#   relay.sh read          랩탑이 보낸 편지 읽기
#   relay.sh send "..."    랩탑에 편지 쓰기
#   relay.sh recv <텍스트>  랩탑이 보낸 것으로 기록 (랩탑 대신 쓸 때)
#   relay.sh log "..."     결정/사실 기록
#   relay.sh ping          연결 확인
#
# 왜 파일인가: 양쪽이 동시에 살아있는 때가 드물다. 소켓은 한쪽이 꺼지면
# 증발하지만 파일은 남는다.

set -euo pipefail

KEY="/data/data/com.termux/files/home/.ssh/id_ed25519"
HOST="dtsli@100.81.24.124"
PORT=2222
RELAY="\$HOME/agent-relay/relay"

_ssh() {
  ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=10 -p "$PORT" "$HOST" "$@" 2>&1 \
    | grep -v -E 'WARNING|post-quantum|store now|openssh.com' || true
}

case "${1:-}" in
  read)
    _ssh "$RELAY read"
    ;;
  send)
    shift
    ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=10 -p "$PORT" "$HOST" "$RELAY laptop" <<<"$*" 2>&1 \
      | grep -v -E 'WARNING|post-quantum|store now|openssh.com' || true
    echo "[보냄] $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M KST')"
    ;;
  recv)
    shift
    ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=10 -p "$PORT" "$HOST" "$RELAY phone" <<<"$*" 2>&1 \
      | grep -v -E 'WARNING|post-quantum|store now|openssh.com' || true
    ;;
  log)
    shift
    _ssh "$RELAY log $*"
    ;;
  ping)
    _ssh "echo OK; hostname; uname -m; wc -c < \$HOME/agent-relay/phone-to-laptop.md; wc -c < \$HOME/agent-relay/laptop-to-phone.md"
    echo "--- 위가 OK/hostname/x86_64/phone-to-laptop bytes/laptop-to-phone bytes 순서 ---"
    ;;
  *)
    sed -n '2,17p' "$0" | sed 's/^# \?//'
    exit 2
    ;;
esac
