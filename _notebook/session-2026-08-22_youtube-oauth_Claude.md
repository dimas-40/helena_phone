---
date: 2026-08-22
agent: Claude Code (출판부 · 양산)
mark: _Claude
type: session-note
status: active
related:
  - 06-youtube.md
  - 100-phone-management-3layers_Claude.md
  - 103-adb-mesh-revive_Claude.md
  - 83-momentum-2026-08-14_Grok.md
---

# 📺 2026-08-22 — 유튜브 OAuth 연결 준비 · 시스템 감사 · 3대 우선순위

> **Boss 지시 (2026-08-22):** "유튜브 OAuth부터 연결해. 이것도 평균이 이슈니까 리마인더하고 업무 스토리 다 저장."
> 기록: **_Claude**

---

## 1. 이 폰의 목적 — 3대 우선순위 (Boss 확정)

이 폰(S25 Ultra) = **S21(누나 폰)의 1인 미디어 허브를 이어받아 업그레이드**한 사다리 최상위 노드.
우선순위 순서:

1. **1인 미디어 출판** — 웹진·출판부·PD Pipeline. devlog 기준 80% 병목 = **색인**(GSC/Bing WMT sitemap, 계정 필요)
2. **누나 돌봄 — 통신·Tailscale·ADB** — 3노드 mesh 자동복구(103). 미완: `adb_revive.sh` TAB_IP 갱신 + `pm grant WRITE_SECURE_SETTINGS` 1회
3. **NPU 워크센터 업그레이드** — 고사양(Snapdragon 8 Elite, Hexagon ~45TOPS). R3 = sherpa-onnx NNAPI 크로스컴파일 (반장 `_Aider` 담당)

## 2. 시스템 감사 (Boss · 2026-08-22) — "8 shipped systems"의 실제

| 시스템 | 판정 | 근거 |
|--------|------|------|
| **티스토리** | ✅ **진짜 완성** | `tistory-naver/` 스크립트 35개(login.cjs·post.py·batch_apply.py·care_republish.py·qa_gate.py) — 문서 아님, 실코드. `accounts.json` 실제 계정 5개. 발행 글 11개(draft). 공식 API 죽은 뒤 관리자 화면 내부 API(`/manage/design/skin/...`) 리버스엔지니어링 → 세션쿠키 Playwright 호출 (`_notebook/93-...` 문서화) |
| **텔레그램** | ✅ 단순하지만 정상 | tg.sh + 봇. 2026-08-22 @Proot_25ultra_bot 신규 발급 |
| **디스코드** | ⚠️ **작동하되 리스크** | discord.md 서버 생성 = 이메일+비번으로 개인계정 로그인 API 직접 호출(**셀프봇 방식**) → 디스코드 ToS 위반, **밴 리스크**. 정식 Bot 토큰/OAuth로 전환 필요 |
| **유튜브** | ❌ **미완성** | youtube.md 자체 명시 "설계 완료 · OAuth 연결 대기". `yt_upload.py`(24.8KB)는 완성, **OAuth 자체가 미연결** → 실제 업로드 불가 |

> **정리:** README "8 shipped systems"는 과장. 티스토리 진짜 · 텔레그램 정상 · 디스코드 방식 전환 필요 · 유튜브 미완성.

## 3. 유튜브 OAuth — 현재 상태 (2026-08-22 실측)

| 항목 | 상태 |
|------|------|
| `scripts/yt_oauth_setup.sh` (Device Code Flow 자동화) | ✅ 완성 (curl 기반, 파이썬 불필요) |
| `scripts/yt_upload.py` (업로드·플리·브랜딩·애널리틱스 CLI v2) | ✅ 완성 (256+줄) |
| python deps (`google_auth_oauthlib`·`googleapiclient`·`requests`) | ✅ 2026-08-22 설치 완료 (apt + pip --no-deps, proot `/usr/bin/python3`) |
| **GCP OAuth 클라이언트 ID/SECRET** | ❌ **미발급 (진짜 병목)** — 동의 화면 + TV 클라이언트 ID 수동 필요 |
| `configs/yt_tokens.json` / `.secrets.env YOUTUBE_*` | ❌ 없음 → 자리만 추가 |
| 채널 | @helena_phone ✅ 존재 (UC_IPajoyj6_IO8wt9JwVCAQ) · 동영상 0개 |

### Boss 수동 작업 (폰 브라우저, 1회) — GCP 콘솔 4단계

```
1. console.cloud.google.com → 새 프로젝트 "S21 YouTube"
2. OAuth 동의 화면 → 외부 → 앱이름 "S21 Phone" → 테스트 사용자 추가
3. 사용자 인증 정보 → OAuth 클라이언트 ID → "TV 및 제한된 입력 장치"
4. 클라이언트 ID + 시크릿 복사 → .secrets.env 저장
```

이후 2단계 (나): `bash scripts/yt_oauth_setup.sh` → 폰에서 verification URL + 코드 입력 → 토큰 자동 저장 → `yt_upload.py` 작동.

### deps 설치 메모 (삽질 기록)

- `pip3 install` ❌ → Termux pip3이 PATH에 먼저 잡혀 Termux 파이썬에 설치 시도, `cryptography` Rust 빌드 실패
- **정답:** proot `/usr/bin/python3` + `apt install python3-google-auth-oauthlib python3-google-auth-httplib2 python3-httplib2 python3-uritemplate python3-google-api-core python3-pip` + `python3 -m pip install --break-system-packages --no-deps google-api-python-client` (apt에 없는 googleapiclient만 --no-deps로, cachetools 충돌 회피)

## 4. 리마인더 항목 — "평균이 이슈" (Boss)

> **Boss:** "이것도 평균이 이슈인 거 같으니까 이것도 해야 되니까 리마인더하고."

유튜브 OAuth 연결 이후 **콘텐츠 평균 수준(퀄리티·성과)** 재점검 필요. 세부 해석은 Boss가 확정할 것.
→ TODO: `_notebook/99-devlog.md` 2026-08-22 항목 · 리마인더 등록.

## 5. 이번 세션 완료 (좌표 갱신)

- S21→S25 Ultra 보일러플레이트 좌표 갱신 — 커밋 `3c1dbf0` (7파일, README·CLAUDE·CONSTITUTION·GUIDE·05-optimization)
- 텔레그램 봇 @Proot_25ultra_bot 토큰 교체 (`.secrets.env`) — chat_id는 `/start` 대기

*agent mark `_Claude` · 2026-08-22*
