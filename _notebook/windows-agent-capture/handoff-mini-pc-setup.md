# 핸드오프 — 미니PC 에이전트 설치 (터미우스 → 나, 레인2)

## 상황
- 사용자가 **미니PC 물리 리부팅**하러 감 (전원 스위치 껐다 10~30초 후 켬).
- 리부팅 후 **미니PC(dev-batch, Linux)**에 "Termius→에이전트" 구조 설치 예정.
- Windows 에이전트(터미우스)가 20초 간격 폴러로 sshd 복귀 대기 중. **터미우스 세션은 사용자가 걸어가면 끊김 → 내가 이어받아 실행.**

## 목표 (설치 후 결과)
미니PC에 Windows PC와 동일한 접속 구조:
| 포트 | 동작 |
|------|------|
| 22   | 일반 셸 |
| 2201 | ForceCommand `claude-agent` (Claude Code, Anthropic) |
| 2202 | ForceCommand `ds-agent` (DeepSeek V4 Flash skin) |

→ 폰 Termius에 `mini`/`mini-claude`/`mini-ds` 호스트 3개 추가 = 탭 1번으로 에이전트 호출.

## 핵심 산출물 (로컬 복사 완료)
- **`mini-pc-agent-setup.sh`** (189줄) — 본 폴더에 있음.
  - 내용: 환경감지 → 패키지(openssh/curl/git/python/node20) → Claude Code(npm) → `claude-agent`/`ds-agent` 래퍼 → sshd 3포트+ForceCommand → Tailscale → 검증.

## 설치 절차 (리부팅 후 내가 실행할 순서)
1. `ssh dtsli@192.168.219.101` (안 되면 root) — 유저/distro 실측.
2. `mini-pc-agent-setup.sh` 실행 (ssh stdin 파이프: `ssh ... 'bash -s' < mini-pc-agent-setup.sh`).
3. **DeepSeek API 키 주입**: `~/.claude-deepseek/ANTHROPIC_API_KEY.txt`.
4. 검증: `ss -ltnp | grep -E ':22|:2201|:2202'` + `sshd -t` + 실제 접속 스모크.
5. 랩탑 `~/.ssh/config`에 `mini`/`mini-claude`/`mini-ds` 3항목 추가.

## 연결 정보
- 미니PC LAN: `192.168.219.101` (랩탑에서 ping <1ms).
- 미니PC Tailscale: `100.81.134.89` (dev-batch).
- **폰→미니PC Tailscale: 현재 100% 손실** → 리부팅 후 판가름. (a)과부하 해소면 해결 / (b)ACL 문제면 Tailscale 콘솔에서 폰↔미니PC 개방.

## 남은 미결 (내가 챙길 것)
- **DeepSeek API 키 원본 위치** 확인 필요: Windows `~/.claude-deepseek/ANTHROPIC_API_KEY.txt` 또는 폰 `.secrets.env`.
- 5-Lane tmux(`tab_claude`/`phone_aider`)는 WSL 전용 → 미니PC엔 미포함. 원하면 플레이북에 추가.
