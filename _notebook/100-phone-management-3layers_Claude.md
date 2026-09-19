---
date: 2026-08-21
agent: Claude Code (공장장)
mark: _Claude
type: ops-policy
status: active
related:
  - 31-agent-roles_Grok.md
  - 83-momentum-2026-08-14_Grok.md
---

# 📱 폰 관리 3계층 — 수리 라우팅 원칙 (2026-08-21)

> **Boss 결정 (2026-08-21)** · 기록: **_Claude**  
> 여기 워크센터(S21 proot)의 **공장장 = Claude Code.**  
> "수리를 누가 맡을지"는 이 문서의 계층표로 라우팅한다.

---

## 1. 폰 관리 3계층

| 계층 | 작업 영역 | 담당 | 권한 근거 | 접근 |
|------|----------|------|-----------|------|
| **①** | 앱 / 메모리 / 하드웨어 | **ADB** | shell 권한(uid 2000) = 앱 제어 가능 | `adb -s 100.103.250.45:5900` (WSL) |
| **②** | Git / 파일시스템 | **proot Ubuntu** | 루트 권한, 폰 안 FS 직접 | SSH 8022 → proot-distro |
| **③** | 네트워크 / 터널 | **Tailscale / SSH** | 인프라 계층 | `tailscale status` |

## 2. 라우팅 원칙 — 3줄

1. **"폰 화면 / 앱 / 성능" → ADB** — 가까운 권한(uid 2000)이 최적
2. **"폰 안 리눅스 / 파일 / git" → proot** — 루트 권한으로 폰 안 FS 직접
3. **"중간 경유 늘리지 마라"** — 폰 안에 adb·tailscale 이미 있으니 **이 세션에서 해결**

## 3. 수리 대기열 (2026-08-21 시점)

| # | 수리 | 위험 | 실행 | 방법 |
|---|------|------|------|------|
| **R1** | Git 객체 손상 (`main` HEAD 죽음) | 🔴 중 | 공장장 | ① `git fetch origin 19c4210…` (실종 커밋 되살아나나 확인) → ② 안 되면 `git reset --soft upstream/main` (**`--hard` 금지**, 미커밋 작업 보호) |
| **R2** | 메모리 압박 (swap 78% 참) | 🟡 중 | 공장장 (ADB) | `com.hagaseca.thost9` 강제종료 ✅ · 잔여 대형 프로세스 확인 → 정리 |
| **R3** | NPU/GPU 가속 (장기) | 🟢 저 | **반장 시공** + 공장장 검증 | Termux NDK 크로스컴파일 반복 루프 (CLAUDE.md 전략과 동일) |

**배정 근거:** R1·R2는 컨텍스트가 이 세션에 있고 adb가 폰 안에 있어 "배정하면 더 느린" 케이스 → 공장장 직접. R3는 반복 빌드 루프라 반장(_Aider) 전문 영역.

## 4. 검증 게이트

- **"수리 완료" ≠ "수리 확정"** — 수리 뒤 상태 확인 필수
- 감사(_Claude 감사) 미설치 → **Boss 간이 게이트** (CLAUDE.md 규칙)

## 5. 실측 메모 (2026-08-21 · proot 내부)

- `tailscale status` → Termux tailscaled **미실행**. (Android 앱이 tailnet 관리 중일 수 있음 — 접속 시 `adb devices` / `tailscale status`로 재확인)
- proot 내 리슨 `8022/5900/5555` **없음** — 접속 포트는 세션 시작 시 확인
- thost9 프로세스: `ps`에서 확인 불가 → **정지 확정 ✅**
