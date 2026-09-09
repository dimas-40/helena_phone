#!/usr/bin/env bash
# ============================================================================
# mini-pc 관제 허브 셋업 — Windows PC의 "Termius → 에이전트" 구조를 Linux에 복제
#   Windows 원본: sshd Port 22(셸) / 2201(ForceCommand claude) / 2202(ForceCommand ds)
#   Linux 미니PC: 동일하게 22 / 2201(claude-agent) / 2202(ds-agent)
# ============================================================================
set -uo pipefail

RUN_LOG=/tmp/mini-pc-agent-setup.log
exec > >(tee -a "$RUN_LOG") 2>&1

say(){ printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }
err(){ printf '\033[1;31m[실패] %s\033[0m\n' "$*"; }

# ---------- 0. 권한/환경 감지 ----------
say "0. 환경 감지"
if [[ $EUID -ne 0 ]]; then
  SUDO=sudo
  if ! command -v sudo >/dev/null 2>&1; then err "sudo 없음, root 필요"; exit 1; fi
else
  SUDO=""
fi
command -v curl >/dev/null 2>&1 || { $SUDO true; }

# distro / package manager 감지
if command -v apt-get >/dev/null 2>&1; then PM=apt
elif command -v apk >/dev/null 2>&1; then PM=apk
elif command -v dnf >/dev/null 2>&1; then PM=dnf
elif command -v pacman >/dev/null 2>&1; then PM=pacman
else PM=unknown; fi
OS_ID="$(grep -E '^ID=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')"
echo "PM=$PM  OS_ID=$OS_ID  USER=$(whoami)  HOME=$HOME"

# ---------- 1. 필수 패키지 설치 ----------
say "1. 필수 패키지 설치 (sshd/curl/git/python3/node/npm)"
install_pkgs() {
  case "$PM" in
    apt)   $SUDO apt-get update -y && $SUDO apt-get install -y "$@" ;;
    apk)   $SUDO apk add --no-cache "$@" ;;
    dnf)   $SUDO dnf install -y "$@" ;;
    pacman) $SUDO pacman -Sy --noconfirm "$@" ;;
    *) err "지원 안 되는 패키지 매니저: $PM"; return 1 ;;
  esac
}

install_pkgs openssh-server curl git python3 ca-certificates

# node/npm (Claude Code 필수). 이미 있으면 스킵.
if command -v node >/dev/null 2>&1; then
  echo "node: $(node -v) / npm: $(npm -v 2>/dev/null || echo 없음)"
else
  say "1b. Node.js 20 설치 (NodeSource)"
  case "$PM" in
    apt)
      $SUDO curl -fsSL https://deb.nodesource.com/setup_20.x | $SUDO bash -
      $SUDO apt-get install -y nodejs ;;
    *) err "Node 설치 규칙 없음(PM=$PM) — 수동 설치 필요"; ;;
  esac
fi

# ---------- 2. Claude Code 설치 ----------
say "2. Claude Code 설치 (npm global)"
if command -v claude >/dev/null 2>&1; then
  echo "claude 이미 있음: $(command -v claude)"
else
  $SUDO npm install -g @anthropic-ai/claude-code
fi
CLAUDE_BIN="$(command -v claude || true)"
if [[ -z "$CLAUDE_BIN" ]]; then
  # npm global bin 경로 직접 탐색
  for c in /usr/bin/claude /usr/local/bin/claude "$HOME/.npm-global/bin/claude" \
           "$HOME/.local/bin/claude"; do
    [[ -f "$c" || -L "$c" ]] && CLAUDE_BIN="$c" && break
  done
fi
echo "CLAUDE_BIN=$CLAUDE_BIN"
[[ -z "$CLAUDE_BIN" ]] && { err "claude 바이너리 못 찾음"; exit 1; }

# ---------- 3. 에이전트 래퍼 스크립트 ----------
say "3. 에이전트 래퍼 스크립트 (/usr/local/bin)"

# 3-1. claude-agent (공식 Anthropic 백엔드, ~/.claude)
$SUDO tee /usr/local/bin/claude-agent >/dev/null <<EOF
#!/usr/bin/env bash
# 공식 Claude Code (Anthropic) — ForceCommand 전용
unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_MODEL 2>/dev/null || true
export CLAUDE_CONFIG_DIR="\$HOME/.claude"
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
export TERM="\${TERM:-xterm-256color}"
exec "$CLAUDE_BIN" --dangerously-skip-permissions "\$@"
EOF

# 3-2. ds-agent (DeepSeek V4 Flash 백엔드, ~/.claude-deepseek)
$SUDO tee /usr/local/bin/ds-agent >/dev/null <<EOF
#!/usr/bin/env bash
# ds — Claude Code skin + DeepSeek V4 Flash 백엔드 (Linux)
set -uo pipefail
KEYFILE="\$HOME/.claude-deepseek/ANTHROPIC_API_KEY.txt"
if [[ ! -f "\$KEYFILE" ]]; then
  echo "❌ DeepSeek API 키 없음: \$KEYFILE" >&2
  exit 1
fi
API_KEY="\$(tr -d '\r\n' < "\$KEYFILE")"
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_API_KEY="\$API_KEY"
export ANTHROPIC_AUTH_TOKEN="\$API_KEY"
export CLAUDE_CONFIG_DIR="\$HOME/.claude-deepseek"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
export TERM="\${TERM:-xterm-256color}"
echo "━━━ ds: Claude Code skin + DeepSeek V4 Flash ━━━"
exec "$CLAUDE_BIN" --bare --model deepseek-v4-flash --dangerously-skip-permissions "\$@"
EOF

$SUDO chmod +x /usr/local/bin/claude-agent /usr/local/bin/ds-agent
ls -l /usr/local/bin/claude-agent /usr/local/bin/ds-agent

# ---------- 4. DeepSeek 설정 디렉토리 ----------
say "4. DeepSeek 설정 디렉토리 생성"
mkdir -p "$HOME/.claude-deepseek"
touch "$HOME/.claude-deepseek/ANTHROPIC_API_KEY.txt"
cat > "$HOME/.claude-deepseek/settings.json" <<EOF
{
  "permissions": { "defaultMode": "bypassPermissions" },
  "skipDangerousModePermissionPrompt": true,
  "model": "deepseek-v4-flash",
  "autoUpdaterStatus": "disabled"
}
EOF
echo "키 파일 자리: $HOME/.claude-deepseek/ANTHROPIC_API_KEY.txt (아직 값은 별도 주입)"

# ---------- 5. sshd 다중 포트 + ForceCommand ----------
say "5. sshd 설정 (Port 22/2201/2202 + Match LocalPort)"
SSHD_MAIN=/etc/ssh/sshd_config
DROPIN=/etc/ssh/sshd_config.d/99-agents.conf
CONF_BLOCK=$(cat <<'EOF'
# === mini-pc agent ports (Windows PC 구조 복제) ===
Port 22
Port 2201
Port 2202
Match LocalPort 2201
    ForceCommand /usr/local/bin/claude-agent
Match LocalPort 2202
    ForceCommand /usr/local/bin/ds-agent
EOF
)

if [[ -d /etc/ssh/sshd_config.d ]]; then
  echo "$CONF_BLOCK" | $SUDO tee "$DROPIN" >/dev/null
  echo "드롭인 적용: $DROPIN"
else
  echo "$CONF_BLOCK" | $SUDO tee -a "$SSHD_MAIN" >/dev/null
  echo "본설정에 추가: $SSHD_MAIN"
fi

# sshd 재시작 (서비스 매니저 자동 감지)
if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
  $SUDO systemctl enable --now ssh 2>/dev/null || $SUDO systemctl enable --now sshd 2>/dev/null || true
  $SUDO systemctl restart ssh 2>/dev/null || $SUDO systemctl restart sshd 2>/dev/null || true
else
  $SUDO service ssh restart 2>/dev/null || $SUDO rc-service sshd restart 2>/dev/null || true
fi

# ---------- 6. Tailscale (선택 — 이미 있으면 스킵) ----------
say "6. Tailscale 확인"
if command -v tailscale >/dev/null 2>&1; then
  echo "tailscale 이미 있음: $(tailscale version 2>/dev/null | head -1)"
else
  echo "Tailscale 미설치 → 설치 시도 (데비안/우분투 기준)"
  $SUDO curl -fsSL https://tailscale.com/install.sh | $SUDO sh || true
fi
if command -v tailscale >/dev/null 2>&1; then
  $SUDO tailscale up 2>&1 | tail -3 || true
  echo "※ 미인증이면 위 auth URL로 로그인 필요"
fi

# ---------- 7. 검증 ----------
say "7. 검증"
$SUDO sshd -t 2>&1 && echo "sshd_config 문법 OK" || echo "sshd_config 문법 오류"
$SUDO ss -ltnp 2>/dev/null | grep -E ':22 |:2201 |:2202 ' || \
$SUDO netstat -ltnp 2>/dev/null | grep -E ':22 |:2201 |:2202 ' || \
echo "(ss/netstat 없음 — 포트 확인 생략)"
echo "---"
echo "완료. Termius에서 아래 3개 호스트로 접속:"
echo "  셸       : <미니PC IP> :22"
echo "  Claude   : <미니PC IP> :2201"
echo "  DeepSeek : <미니PC IP> :2202"
