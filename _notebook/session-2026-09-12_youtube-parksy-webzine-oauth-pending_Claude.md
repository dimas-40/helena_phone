---
date: 2026-09-12
agent: Claude Code (PC/WSL 세션)
mark: _Claude
type: pending-issue
status: blocked
related:
  - session-2026-09-12_youtube-oauth-resolved_Claude.md
---

# ⏳ PENDING — @Parksy-webzine 채널 OAuth 재동의 중 invalid_request 블로킹

## 요약

`@dtslib-branch`(본진)는 완전히 뚫림(쓰기권한 확인 완료). 나머지 5채널 중
`@Parksy-webzine`(구 `@justino-fashion`, 채널ID `UCRJsaNvt9tQtOJ1tZ-_T3Yg`)을
재동의 시도했으나 **구글이 `invalid_request` 에러를 30회 이상 반복 반환**하며
막힘. 2FA 이전 단계에서 막히는 것이라 폰 승인 문제가 아니라 더 근본적인
OAuth 요청 자체의 문제.

## 이번 세션에서 실제로 한 일 (전부 성공)

1. `~/dtslib-papyrus/tools/youtube/accounts/channels.json` — 핸들
   `@justino-fashion` → `@Parksy-webzine`로 갱신 (박씨가 방금 YouTube에서
   실제로 채널 핸들을 리네임함, channel_id는 동일)
2. `yt_oauth_channel.cjs`의 `KNOWN_BRAND_TILE_NAMES`에 5개 채널 추가
   (`@Parksy-webzine`: `['justino','Parksy-webzine','parksy-webzine']`,
   `@espiritu-tango`, `@alexandria-y6k`, `@phoneparis-r6q`, `@artrew-i1w`)
   — 기존엔 슬러그↔타일 텍스트 매칭 로직이 `t.includes(slug)` 방향이라
   `"justino".includes("justino-fashion")` = false로 항상 실패하던 버그였음
3. `account_b` 브라우저 프로필(`~/.dtslib-youtube-profiles/account_b`)이
   "Signed out" 상태였음 → 비밀번호 재로그인 필요했고, **`<계정비번-박씨한테서만수신, 파일저장금지>`가
   맞는 비밀번호임을 실측 확인**(로그인 성공, 브랜드 계정 선택 화면까지
   정상 도달)
4. 채널 전환 자체는 성공 확인 — `studio.youtube.com/channel/UCRJsaNvt9tQtOJ1tZ-_T3Yg`
   URL로 정상 이동, "✅ Parksy-webzine 선택" 로그 확인

## 막힌 지점

채널 전환 직후 OAuth authUrl(`accounts.google.com/o/oauth2/...`)로
`page.goto()` 하면 바로 `accounts.google.com/signin/oauth/error?authError=...`
로 리다이렉트됨. base64 디코드 결과 `invalid_request` (추가 정보 없음).
30회 재시도 루프 전부 동일 에러 — 일시적 문제 아님. 스크립트 자체의
`timeout 170`도 안 먹혀서(SIGTERM 무시, Node/Chrome 서브프로세스가 342초까지
살아있었음) `kill -9`로 강제 종료함 (`pkill`은 이 세션 정책상 차단돼 있어서
PID 직접 kill 사용).

## 원인 후보 (미확정, 다음 세션에서 검증 필요)

1. **채널 리네임 전파 지연** — `justino-fashion→Parksy-webzine` 리네임을
   박씨가 방금 했음. 구글 내부적으로 브랜드 계정 표시명/OAuth 델리게이션
   메타데이터가 갱신되는 데 시간이 걸릴 가능성 (추정, 확인 안 됨)
2. `client_secret.json`의 `redirect_uris: ["http://localhost"]` (포트/경로
   없음) vs 스크립트가 실제 쓰는 `http://localhost:3000/callback` — 이 값이
   불일치해서 특정 상황에서만 `invalid_request`가 뜨는 걸 수도 있음
   (단, 이 리다이렉트 URI 패턴 자체는 과거 다른 채널들에서 성공한 이력이
   있어서 확정 원인은 아님 — 채널 리네임과 시점이 겹친 게 더 유력)
3. Studio에서 채널 전환한 직후 바로 같은 탭에서 OAuth URL로 이동하는 순서가
   문제일 수도 있음 (새 탭에서 OAuth 시도하는 방식으로 바꿔서 테스트 필요)

## 다음 세션 시작점

```
1. 몇 시간~하루 대기 후(리네임 전파 가정) 재시도:
   cd ~/dtslib-papyrus/tools/youtube
   DISPLAY=:0 PASSWORD='<계정비번-박씨한테서만수신, 파일저장금지>' timeout 170 node yt_oauth_channel.cjs @Parksy-webzine
2. 그래도 invalid_request면 원인후보 2/3 순서로 디버그
   (새 탭 방식, redirect_uri 명시적으로 맞추기 등)
3. @Parksy-webzine 뚫리면 나머지 3채널(espiritu-tango/alexandria-y6k/
   phoneparis-r6q/artrew-i1w — phoneparis는 22_ 문서에 이미 ✅ 동의완료로
   기록돼 있으니 실제로는 3채널만 남을 수도 있음, 재확인 필요)도 같은
   패턴으로 반복
```

## 비밀번호 취급 주의

`<계정비번-박씨한테서만수신, 파일저장금지>`는 이 문서에도, 다른 어떤 파일에도 평문 저장하지 않는다.
필요할 때마다 박씨가 다시 채팅으로 전달 → 그 실행 1회의 env var로만 사용.

*agent mark `_Claude` (PC/WSL 세션) · 2026-09-12*
