---
date: 2026-08-21
agent: Claude
mark: _Claude
type: infra-setup
status: active
related:
  - 102-tablet-hw-parse_Grok.md
  - tablet-broadcast-studio_Claude.md
  - 103-adb-mesh-revive_Claude.md
---

# 태블릿 Termux 위젯 + 워크센터 개념 (2026-08-21)

> 태블릿 = **외부 아웃소싱 디바이스 / 워크센터.** Boss가 일을 던지면, 나(Claude Code)가 이 워크센터에서 PC(WSL/Windows)와 ADB mesh를 제어해서 처리.

## 0. 개념

- 태블릿(tab-s9, Tailscale `100.86.15.50`) = 워크센터.
- **Termux:Widget 6종** (`~/.shortcuts/`) = 이 워크센터의 인터페이스(1탭 실행).

## 1. 위젯 6종

| 위젯 | 역할 |
|------|------|
| `0.MASTER.sh` | 1~5 고정본 **복원**(자기복구, ON-DEMAND) |
| `1.wsl_claude.sh` | SSH→Windows/WSL → tmux `tablet_claude` → claude |
| `2.wsl_aider.sh` | SSH→WSL → tmux `tablet_aider` → `source ~/.env-deepseek && claude` |
| `3.win_claude.sh` | SSH→Windows(경유 WSL) → tmux `win_claude_tablet` |
| `4.win_aider.sh` | SSH→WSL → tmux `win_aider_tablet` → start-win-aider.sh |
| `5.ADB.sh` | ADB mesh 상태 + 자동복구 (Shizuku/rish/5900) |

## 2. 핵심 IP (Tailscale)

| 노드 | 주소 |
|------|------|
| 태블릿 (이 기기) | `100.86.15.50`, SSH 8022 |
| WSL (PC) | `100.90.83.128:2222` |
| Windows (PC) | `100.81.24.124:22` |
| 폰 (S25 Ultra) | `100.103.250.45:5900` (ADB) |

## 3. 5.ADB.sh 동작 (ADB mesh 자동복구, 1탭)

```
1. Shizuku 확인    → rish -c id → uid=2000?
2. 무선 디버깅 ON   → rish settings put adb_wifi_enabled 1
3. sshd 보장        → 8022
4. 백그라운드 면제  → phantom/Doze/appops 4종 재적용
5. adb 5900 확인    → 리스닝 체크
6. 5555 함정 체크   → 에뮬레이터 대역 경고
7. 온도 체크
```

## 4. 실행 구조 (한 줄)

```
Termux(위젯 1탭) → SSH → PC(WSL/Windows) → tmux → claude/aider
                 → Shizuku/rish → uid 2000 → ADB mesh(5900)
```

## 5. 이 워크센터에서 내(Claude Code) 위치

- 나는 **proot Ubuntu**(`/root/work`)에서 돎.
- 위젯 1~4 = PC의 claude/aider 세션을 태블릿에서 원격 조종.
- 위젯 5 = ADB mesh(폰·태블릿 제어) 자동복구.

*agent mark `_Claude` · 2026-08-21*
