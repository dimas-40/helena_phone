---
date: 2026-09-12
agent: Claude Code (PC/WSL 세션)
mark: _Claude
type: session-note
status: active
related:
  - session-2026-08-22_youtube-oauth_Claude.md
  - session-2026-08-22_quota-channel-map_Claude.md
---

# 📺 2026-09-12 — 유튜브 OAuth "미발급" 정정 · 실제 병목=SSOT 위치 분산

> **Boss 지시:** GCP OAuth부터 빨리 끝내라. 계정 관리 방법(환경변수) 문의.
> PC 세션(WSL)이 papyrus 클론을 뒤져서 검증·해결. 기록: **_Claude**

## 0. 결론 먼저

**"GCP 클라이언트 ID/시크릿 미발급"은 틀린 진단이었다.** 08-22 노트가 "진짜 병목"이라
적었던 그 자격증명은 **이미 `~/dtslib-papyrus/tools/youtube/`에 존재**했다 —
`client_secret.json`(GCP 프로젝트 `parksy-youtube`) + `accounts/token_b.json`
(dtslib1979@gmail.com, 지금 6채널 SSOT와 정확히 일치) + `accounts/token_c.json`
(Thomas.tj.Park@gmail.com, 교육방송 2채널).

진짜 문제는 **발급이 아니라 위치** — 이 자격증명이 WSL/랩탑 papyrus 클론에만
있고 폰 런타임(`/root/work/.secrets.env`)으로 한 번도 동기화된 적이 없었음.
"SSOT 따로 놀기"의 또 다른 사례 (오늘 앞서 고친 `yt_upload.py` main/phone
채널키 사고와 같은 패턴).

## 1. 실측 검증 (PC 세션, WSL)

```
$ python3 -c "creds.refresh(Request()); yt.channels().list(mine=True)"
✅ refresh 성공 (token_b.json, 마지막 수정 07-02 → 09-12에도 살아있음, 2달+ 경과)
 - dtslib-branch UCxz800sMD27pk6X6HvxNS1g
```

`accounts/channels.json`에 4개 구글계정 매핑 확정 기록 있음:
| id | email | 채널 |
|---|---|---|
| a | dimas.thomas.sancho@gmail.com | KR방송 5채널 (쿼터 미증설 — 보류) |
| **b** | **dtslib1979@gmail.com** | **경제방송 6채널 (지금 폰 SSOT와 동일)** |
| c | Thomas.tj.Park@gmail.com | 교육방송 2채널 (eae.kr/eae-univ) |
| d | dimas@dtslib.com | 명함도메인 2채널 |

## 2. 폰에 실제로 한 작업 (완료)

1. `client_secret.json` + `accounts/token_b.json` 값 →
   `/root/work/.secrets.env`의 `YOUTUBE_CLIENT_ID/SECRET/ACCESS_TOKEN/REFRESH_TOKEN`에 주입
2. **버그 발견+수정**: `scripts/yt_upload.py get_credentials()`가
   `Credentials(..., scopes=SCOPES)`로 refresh 요청 — 이 토큰이 실제 발급받은
   스코프(구 `yt_oauth_auto.cjs`의 4스코프: youtube+analytics.readonly+
   spreadsheets+drive.file)와 yt_upload.py의 SCOPES(2개: youtube.upload+youtube)가
   달라서 `invalid_scope`로 refresh 거부됨.
   → **`scopes=` 파라미터 제거**로 해결(스코프 미지정 시 서버가 원 발급 스코프
   그대로 사용). `yt_geo_origin.py`는 이 함수를 그대로 재사용하므로 자동 해결됨.
3. 실측 검증:
   - `python3 scripts/yt_upload.py --channel branch --stats` → 구독자 8 / 동영상 75 /
     조회수 11888 (실제 API 응답)
   - 쓰기 권한 실증: `--playlist-create` 테스트 → 생성 확인 → 삭제로 원복

## 3. 중요한 제약 — "6채널 다 됐다"가 아님

`--stats`는 6채널 전부 조회 성공했지만, **채널 통계는 공개 데이터라 인증 없이도
조회 가능** — 이건 쓰기 권한 증명이 아님. 실제 `--playlist-create`로 쓰기 테스트한
결과, **이 토큰(token_b)으로 실제 업로드/쓰기가 가능한 채널은 `@dtslib-branch`
(본진) 1개뿐**임을 확인함. `playlists.list(mine=True)`로 재확인해도 전부
`channelId: UCxz800sMD27pk6X6HvxNS1g`(branch)로만 귀속됨.

**이유**: Google Brand Account 구조상, 한 Google 로그인 밑에 여러 브랜드 채널이
있어도 OAuth 동의 시점에 "활성 채널"이던 것 하나에만 쓰기 권한이 귀속된다.
나머지 5채널(phoneparis/alexandria/artrew/parksy-webzine/espiritu)은 각각
**채널 전환 후 재동의**가 필요 — 이미 이 패턴을 자동화한 스크립트가
`~/dtslib-papyrus/tools/youtube/yt_oauth_channel.cjs`에 있음(브랜드 계정 전환+
동의 자동화, 07-21 삽질기록 `infra-history/21_YOUTUBE_BRAND_ACCOUNT_OAUTH_20260721.md`
참조). 유일하게 자동화 불가한 구간 = 2FA 폰 푸시 승인(채널당 1회, 사람이 직접
눌러야 함).

## 4. 토큰 관리 정책 (Boss 질문 답변)

| 값 | 갱신 필요? |
|---|---|
| CLIENT_ID/SECRET | 거의 영구 (GCP 프로젝트 삭제 전까지 불변) |
| REFRESH_TOKEN | **정기 교체 불필요** — 접근취소/6개월 미사용/비번변경 등 사고성 이벤트에만 무효화. 오늘 실측: 07-02 발급 토큰이 09-12에도 정상(2달+ 경과) |
| ACCESS_TOKEN | 1시간마다 자동 만료 → refresh_token으로 스크립트가 자동 재발급, 수동 개입 불필요 |

→ `.secrets.env`(환경변수) 관리가 정답이고 이미 그 구조. "정기적으로 바꿔야
하나" 걱정은 기우 — 사고 없는 한 세팅 1회로 영구 작동.

## 5. 남은 일

- [ ] `token_c.json`(Thomas.tj.Park@gmail.com, eae.kr/eae-univ)도 동일 방식으로
      폰에 동기화 필요 시 진행
- [ ] branch 외 5채널 — `yt_oauth_channel.cjs @핸들`로 채널별 재동의 (2FA 승인은
      Boss가 폰에서 직접, 채널당 1회)
- [ ] `dimas.thomas.sancho@gmail.com`(계정 a) — 쿼터 미증설 상태라 보류 확정

*agent mark `_Claude` (PC/WSL 세션) · 2026-09-12*
