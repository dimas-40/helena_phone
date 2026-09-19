---
date: 2026-08-18
agent: Claude Code (출판부)
mark: _Claude
type: troubleshooting
status: resolved
related:
  - session-2026-08-18_Claude.md
---

# Grok CLI 설치 · 삽질 기록 (2026-08-18)

> Boss 지시: 내가 설치 과정에서 삽질한 것 + 원상복구한 것을 기록. (삭제·변경한 것 + 그 이유)

## 요약
- 설치·로그인: **성공** (grok 1.0.5, dtslib1979@gmail.com)
- 에러 1건: `grok "안녕"` → `No such device or address (os error 6)`
- 내 **오진 → 삽질 2건 → 원인 규명 → 전부 원상복구**

---

## 삽질 ① ENXIO 에러를 네트워크(IPv6) 문제로 오진

**증상:** `grok "안녕"` → `Error: No such device or address (os error 6)`

**오진 판단:** `getent hosts api.x.ai` 가 IPv6 주소(`2606:4700::...`)만 반환하는 걸 보고
"proot에 IPv6 인터페이스가 없어서 grok이 IPv6 연결을 시도하다 실패"라고 단정.

**삽질 A — `/etc/gai.conf` 수정:**
- IPv4 우선 precedence(`::ffff:0:0/96 100`) 주석 해제 → 그 과정에서 중복 라인 생성.
- 결과: 효과 없음. (grok 여전히 동일 에러)

**삽질 B — `/etc/hosts` 수정:**
- `api.x.ai`, `cli-chat-proxy.grok.com` 의 IPv4를 하드코딩 추가.
- 결과: 효과 없음. (`getent hosts`가 여전히 IPv6만 반환 — proot DNS 인터셉트 때문)

**진짜 원인:** `/dev/tty` 부재. 이 셸은 **헤드리스(비대화형)** 라 grok(TUI)이 터미널을 못 연다.
`os.open('/dev/tty')` → `OSError: [Errno 6] No such device or address` 로 확정.

**증명:** pty(가짜 터미널)로 감싸서 실행 → **정상 동작** (API 연결 + "Korean Hello Greeting Session Start" 응답 확인).

**복구:** `/etc/gai.conf`(백업 복원) + `/etc/hosts`(추가 줄 제거) **전부 원상복구 완료** ✅

**교훈:** `No such device or address`(ENXIO) = **장치(TTY) 부재**지 네트워크 문제가 아니다.
네트워크를 의심하기 전에 `/dev/tty`(또는 `os.open('/dev/tty')`)부터 확인할 것.

---

## 삽질 ② grok/gr alias 통일 반복 실패 (old==new 버그)

**상황:** Termux alias에서 `grok`과 `gr`을 동일하게 만들려 했는데,
교체 스크립트의 old/new 문자열을 **매번 똑같이** 써서 no-op이 5~6회 반복.

**해결:** `assert old != new` 로 버그를 잡고, 정답인 `gr` 라인의 명령을 **복사해서** `grok`에 적용.

**교훈:** 문자열 replace 시 old != new 검증(또는 정답 소스에서 복사) 필수.

---

## 최종 상태 (정상)

| 항목 | 값 |
|------|-----|
| 설치 | grok 1.0.5 (linux-aarch64) — `~/.grok/bin/{grok,agent}` + `/usr/local/bin` 심링크 + `~/.bashrc` PATH |
| 로그인 | dtslib1979@gmail.com — `~/.grok/auth.json` |
| Termux alias | `grok` = `gr` = `proot-distro login ubuntu -- bash -lc "cd /root/work && /root/.grok/bin/grok"` (`.bashrc` + `.profile` 둘 다) |
| 실행 조건 | TTY 있는 대화형(Termux)에선 정상. 헤드리스 스크립트에선 pty 래퍼(`script -qec ...`) 필요 |
