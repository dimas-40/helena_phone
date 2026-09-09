# 미니PC → Termius(폰) 접속 호스트 3종

> Windows PC와 동일한 3포트 구조. 미니PC Tailscale IP 기준(100.81.134.89).
> ※ 폰→미니PC Tailscale이 현재 안 뚫리면, 먼저 Tailscale ACL/라우팅 점검 필요.

## Termius 호스트 등록 값

| 프로필명 | 호스트 | 포트 | 유저 | 설명 |
|----------|--------|------|------|------|
| mini-pc (셸) | 100.81.134.89 | 22 | dtsli | 일반 셸 (관제/수리) |
| mini-claude | 100.81.134.89 | 2201 | dtsli | 접속 즉시 Claude Code 진입 |
| mini-ds | 100.81.134.89 | 2202 | dtsli | 접속 즉시 DeepSeek(ds) 진입 |

## 동일 구조 원본 (Windows PC)
- win (100.81.24.124:22) / win-claude (…:2201) / win-ds (…:2202)
- WSL은 100.90.83.128:2222 (mosh, Termux 전용)

## 등록 방법 (Termius)
1. Hosts → New Host
2. Address = 100.81.134.89, Port = 위 표, Username = dtsli
3. Key = 랩탑 ~/.ssh/id_ed25519 (기존 win/profile과 동일 키)
4. 저장 후 탭 = 에이전트 즉시 호출 (ForceCommand가 알아서 claude/ds 실행)
