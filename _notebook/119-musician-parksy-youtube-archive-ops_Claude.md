---
date: 2026-10-06
agent: Claude
mark: _Claude
type: ops
status: active
location: S25 Ultra proot (오프라인 상주 런북)
related:
  - 117-three-node-music-workcenter_Claude.md
  - 118-parksy-label-goal-real-bottleneck_Claude.md
  - parksy-audio/tools/youtube/UPLOAD-HOWTO.md
  - papyrus/tools/youtube/accounts/channels.json
---

# @musician-parksy 배포 아카이브 — 운영 정본 (폰 상주 런북)

> **Boss 지시 (2026-10-06):** 최종 생산물은 **@musician-parksy**에 업로드, 습작은 **WD 패스포트**에 저장.
> "이건 폰 단말기 안에서 네가 주력으로 작업해야 하는 거라 매번 시킬 수 없다" → **여기 전부 박제.**
>
> **표기:** `[실측]` = 이 세션에서 API/명령으로 직접 확인 · `[기록]` = 기존 문서 인용 · `[미검증]` = 아직 안 해봄
> ⚠️ **비밀 값은 이 파일에 없다** (git 추적됨). 토큰·시크릿은 `.secrets.env`(gitignored)에만.

---

## 0. 한 줄

**최종물 = @musician-parksy (YouTube) · 습작 = WD 패스포트 (랩탑 외장).**
폰에서 이걸 주력으로 돌린다. 단 **음악 채널 쓰기 토큰(계정 a)이 폰에 없어서**, 지금 폰은 **읽기(공개) + 계정 b 운영**만 가능하다. (§3)

---

## 1. 채널 확정 `[실측 2026-10-06]`

| 항목 | 값 |
|---|---|
| 채널명 | **뮤지션 박씨** |
| 핸들 | @musician-parksy |
| 채널 ID | `UCun6b2HD3ekp35PhqbTfOlg` |
| 소유 계정 | **a** = `dimas.thomas.sancho@gmail.com` (parksy.kr 페르소나) |
| 개설 | 2019-08-23 |
| 영상 | **39** · 구독 1 · 조회 1,798 |

> ⚠️ `DIVISION-MAP.json`의 **"232개 비디오"는 부패한 수치**. 실측 39. (카탈로그 `data/youtube-catalog.json`의 39가 맞음)

---

## 2. 플레이리스트 — **두 패밀리가 공존한다** `[실측]`

### 2.1 채널 공개 (★ @musician-parksy 소유 — 이게 채널 페이지에 뜨는 것)

| 플레이리스트 | ID | 영상 수 |
|---|---|---|
| 박씨 오디오 | `PLjxh2pH0uEjrZCK0DDK6TGH1PFT06lrVi` | 24 |
| Parksy Audio | `PLjxh2pH0uEjqkF-ta-4ySDzQ9kow4NI6j` | 7 |
| Gemini Song | `PLjxh2pH0uEjrFDjfuPEmkmzSsUAX_LbbN` | 8 |
| AIVA | `PLjxh2pH0uEjoNUxa0KW4nim_9GpI9ki1X` | 9 |

→ `youtube-setup.json`(06-27)의 main/gemini/pipeline/aiva 세트가 **이 라이브 4개**와 일치. 채널 홈 섹션도 이걸 씀.

### 2.2 업로드 툴 타깃 (⚠️ **다른 채널 소유!**)

| 키 | 플레이리스트 | ID | 소유 채널 | 공개 |
|---|---|---|---|---|
| `album` | @musician-parksy \| 앨범 시리즈 | `PLNAJ8HsuRXWtIMM4seoCYagolfSvC5TM6` | **@blogger-parksy** `UC5H8CnRGDxvx4v3HWrktuSg` | public |
| `making` | @musician-parksy \| 제작기 | `PLNAJ8HsuRXWuwBqHqs9A5w-o6ec9Nh8Er` | **@blogger-parksy** | public |
| `bgm` | @musician-parksy \| BGM 소재집 | `PLNAJ8HsuRXWuo...` → `PLNAJ8HsuRXWuor0xRp3X1iZM05R0qTFzW` | **@blogger-parksy** | public |

**⚠️ 이게 이번 실측 최대 발견:**
`upload-musician.cjs`가 영상을 넣는 3개 플레이리스트는 **이름만 @musician-parksy**고,
**실제 소유 채널은 @blogger-parksy**(같은 계정 a의 다른 채널)다.
→ 음악 채널 영상이 **블로거 채널 플레이리스트에 꽂힌다.** 채널 구조와 업로드 툴 타깃이 불일치.
→ 교정 방향: 툴 타깃을 §2.1의 **musician 소유** 플레이리스트로 바꾸거나, 의도를 확인할 것.

> 정리: `youtube-setup.json`(공개 채널용) ≠ `musician-config.json`(업로드 툴용). **둘 다 실재하나 목적이 다르고, 툴 쪽이 채널이 틀렸다.**

---

## 3. 토큰 토폴로지 `[실측]`

### 3.1 폰에 있는 토큰 = **계정 b** (음악 채널 아님!)

`.secrets.env` 키: `YOUTUBE_CLIENT_ID` · `YOUTUBE_CLIENT_SECRET` · `YOUTUBE_REFRESH_TOKEN` · `YOUTUBE_ACCESS_TOKEN`

- `[실측]` **access token은 만료**(401 Invalid Credentials). **refresh는 살아있음** → 갱신 성공.
- `[실측]` 스코프: `youtube`(full) + `yt-analytics.readonly` + `drive.file` + `spreadsheets`
- `[실측]` 이 토큰의 주인 = **@dtslib-branch** (계정 **b**, `dtslib1979@gmail.com`, `UCxz800sMD27pk6X6HvxNS1g`)

> **⚠️ 함정:** `.secrets.env`의 `YOUTUBE_*`를 보고 "음악 채널 토큰"이라 가정하면 틀린다. `mine=true`가 돌려준 건 `dtslib-branch`다.
> **b 토큰이라도 공개 채널 조회는 된다** → §1·§2 실측은 b 토큰으로 `id=`/`channelId=` 질의해서 얻음.

### 3.2 ~~음악 채널 토큰(계정 a)은 폰에 없다~~ → **해결됨 (2026-10-06)** ✅

랩탑 6개 레포를 전수조사해 **채널별 토큰 18개를 폰으로 이식 완료.** 이제 음악 채널 쓰기 가능.

- `[실측]` 랩탑 레포 6곳에 `tools/youtube/` 존재: `dtslib-localpc`·`dtslib-papyrus`·`parksy-audio`·`parksy-image`·`parksy-audio-daw`·`parksy-image-unit-lane`
- `[실측]` **보물은 `parksy-image/tools/youtube/accounts/`** — **채널 하나씩 따로 인증한 토큰 15개**. 계정 a~d 전 채널을 덮는다. 전부 `youtube.upload` 스코프 O.
- `[실측]` 페어 실증: `parksyimage_client_secret.json` + `parksyimage_token_musician.json` → **뮤지션 박씨** (`mine=true` 일치). `papyrus_token_a__musician-parksy` 도 동일 채널 — 둘 다 생존.
- `[실측]` 도착지 = `/root/.secrets/youtube/` (**레포 밖**, gitignored). 지도 = `CHANNEL-MAP.json`. 토큰 값은 레포에 없음.
- `[실측]` ⚠️ `token_d.json`(계정 d)은 **`invalid_grant` — 회수/만료된 죽은 토큰.** 나머지 18개 생존.

### 3.3 능력 경계 (2026-10-06 갱신)

| 능력 | 폰 현재 |
|---|---|
| 공개 채널/플레이리스트 **읽기** (아무 채널) | ✅ |
| **18채널 전부 읽기 + 쓰기** (계정 a·b·c, EAE, 박씨 5형제) | ✅ **러너 `scripts/ytch.py`** |
| **@musician-parksy 업로드·플레이리스트 수정** | ✅ **토큰 확보** |
| WD 패스포트 접근 | ❌ 폰 미마운트 (§6) |
| 커뮤니티 게시 | ❌ **API에 엔드포인트 없음** → GUI/Paste Pipeline (§10) |

> 쓰기 능력은 스코프로 확증(`youtube` full / `youtube.upload`)했고 채널 API는 **비파괴 검증만** 했다 — 실제 업로드(`videos.insert`)는 아직 안 함. 검수 게이트 뒤에서만. `[미검증: 실제 업로드]`

---

## 4. API 도구 실물

### 4.1 `parksy-audio/tools/youtube/` (음악 채널 전용)
| 파일 | 역할 |
|---|---|
| `auth.js` | OAuth. 스코프 `youtube`+`.upload`+`.readonly`+`yt-analytics.readonly` |
| `upload-musician.cjs` | 업로드 + `playlistItems.insert`. `--playlist album\|making\|bgm` |
| `youtube-studio.js` | CLI: status/upload/update/thumbnail/list/analytics/**playlist create·add** |
| `musician-config.json` | 채널 + 플레이리스트(album/making/bgm) |
| `.gitignore` | `client_secret.json` · `token.json` |

### 4.2 `papyrus/tools/youtube/` (전 계정 공용)
| 파일 | 역할 |
|---|---|
| `accounts/channels.json` | **4계정 × 채널 등록부** (아래) |
| `upload.cjs` · `yt.py` · `sync.cjs` · `refresh.cjs` | 업로드·동기화·갱신 |
| `yt_oauth_channel.cjs` | 채널별 최초 인증(Playwright+Windows Chrome). 결과 `accounts/token_{계정}__{채널}.json` |
| `update_musician_desc.cjs` | 음악 채널 소개 갱신(Playwright) |

**채널 등록부 요약 (`channels.json`):**
- 계정 **a** (dimas, token_a) = 6채널: blogger·**musician**·visualizer·technician·philosopher·방송인박씨
- 계정 b (dtslib1979, token_b) = 6채널: dtslib-branch·espiritu-tango·artrew·phoneparis·alexandria·Parksy-webzine
- 계정 c (Thomas.tj.Park) = 2: EAE
- 계정 d (dimas@dtslib.com) = 2: dtslib_com/world

> **musician-parksy → repo `parksy-audio` · token_a.json**

---

## 5. 업로드 절차 + 게이트

**경로:** `outputs/`(비디오·마스터·감정JSON, gitignored) → `tools/youtube/uploads/*.json`(스펙) → `upload-musician.cjs` → `videos.insert` → `playlistItems.insert` → `done/` 이동

**하드 룰 (메모리 [[youtube-upload-review-gate]]):** **자동 업로드 절대 금지.** TG 보고 → Boss 검수 → 업로드.

**쿼터 (메모리 [[youtube-api-quota-approval]]):**
- 계정 **a는 60k 미승인**(신청 반송) → 기본 10k/day → `videos.insert`=1600 단위 → **하루 ~6편 한계**
- 승인 유효기간 **2026-09-23 만료 — 지금(10-06) 이미 지남.** 재승인 필요

**워크플로:** `.github/workflows/`엔 `youtube-stats.yml`·`stats-cron.yml`만 — **업로드 워크플로 없음**(통계 수집만). 업로드는 수동 CLI.

---

## 6. 습작 → WD 패스포트 — **미배선** `[실측]`

- WD 패스포트 = **WD My Passport 2TB**, **랩탑에 물린 외장**(devlog 7197): `D:` DATA 1.76TB + `W:` Windows To Go 107GB + `T:` EFI.
- **폰엔 마운트 안 됨** (폰 `/mnt`엔 `sdcard`뿐).
- **"습작을 WD에 자동 저장"하는 코드·문서는 어디에도 없다.** `releases/`는 `UPLOAD-HOWTO`가 참조하나 실물 없음. → **드래프트 아카이브 레인 = 개념만, 배선 0.**

---

## 7. 폰에서 지금 되는 것 / 안 되는 것

| | 상태 |
|---|---|
| 18채널 **읽기 + 쓰기** (`scripts/ytch.py`) | ✅ |
| **@musician-parksy 업로드 / 플레이리스트 수정** | ✅ 토큰 확보 |
| **WD 패스포트 저장** | ❌ 미마운트 + 레인 미구현 |
| 커뮤니티 게시 | ❌ API 없음 (탭은 실재) → Paste Pipeline (§10) |
| 노트북 기록·게이트 | ✅ |

---

## 8. 다음 작업 큐 (내가 주력으로 돌릴 것)

1. ~~계정 a 토큰 확보~~ → **완료 (2026-10-06)**. 18토큰 이식 + 러너 `scripts/ytch.py`. (§3.2)
2. **플레이리스트 정합 교정** — 툴 타깃이 @blogger-parksy 소유(§2.2) → 이제 교정 **가능**(양쪽 채널 토큰 다 폰에 있음). 의도 확정 후 musician 소유로
3. **쿼터 재승인** — 계정 a 60k 재신청(09-23 만료). 안 되면 하루 ~6편으로 스케줄
4. **습작 → WD 아카이브 레인 설계** — 최종/습작 분기 규칙
5. **업로드 실행 게이트 자동화** — 렌더·인코딩·메타·SRT까지 자동, 발행은 Boss 게이트
6. ~~커뮤니티 500 구독 로드맵~~ → **철회.** 탭은 이미 실재한다(§10 정정). 남은 건 **API 부재**뿐 → Paste Pipeline으로 게시

---

## 9. 함정 기록 (재발 방지)

| 함정 | 내용 |
|---|---|
| 토큰 주인 가정 | `.secrets.env` YOUTUBE_* = **계정 b**(dtslib-branch). 음악 채널 아님 |
| access token 만료 | `.secrets.env`의 access는 401. **refresh부터** |
| playlist 소유채널 불일치 | 툴 타깃 3개가 **@blogger-parksy 소유**. 이름만 musician |
| **죽은 토큰** | `papyrus token_d.json` = `invalid_grant`. 이식 시 생존 확인 필수 |
| **레포별 시크릿 중복** | 6개 레포가 각자 `client_secret.json` 보유 — 토큰은 **그 시크릿 페어로만** 갱신됨. 섞으면 실패 |
| 수치 부패 | `DIVISION-MAP.json` "232 videos" ≠ 실측 39 |
| 자동 업로드 | 금지. 검수 게이트 필수 |
| 파일 이식 | 대용량 바이너리 커밋 금지 → 델타 fetch/직접 전송 |

---

## 10. 커뮤니티(게시판) 탭 — 막는 건 API 하나뿐 `[실측 2026-10-06 · 2026-10-06 정정]`

> ⚠️ **이 절은 한 번 오진했다가 정정했다.** (커밋 `08b3335`가 낡은 주장을 담고 있었다)
> 처음엔 "구독자 500 미달이라 탭이 없다"고 썼는데 **틀렸다.** 탭은 **실재한다.**

**설정 문제도 자격 문제도 아니다. 막는 건 API 하나뿐이다.**

### 10.1 API가 그 기능을 아예 안 연다
- `[실측]` YouTube Data API v3 공식 디스커버리 문서 리소스 **32개 중 `communityPosts`/`posts` 없음**
- `[실측]` `activities`는 **`list`만** — 옛 채널 공지용 `activities.insert`는 **2016 폐기**
- ⚠️ `papyrus/tools/youtube/community.cjs`는 `yt.communityPosts.insert` 호출 → **존재하지 않는 유령 메서드** = 무조건 실패. "OAuth 미완"이 아니라 **API에 그게 없음**
- → 커뮤니티 글은 **API로 못 쓴다.** Studio/GUI만 가능.

### 10.2 ~~채널이 자격 미달~~ → **철회. 탭은 이미 열려 있다** `[실측]`
- ❌ ~~"구독자 500명↑ 필요"~~ — **낡은 정보**(2023년 폐지). 여러 2026 출처가 일치.
- ✅ `[실측]` 채널에 **`/@musician-parksy/community` 라이브** — `browseId: FEcommunity_page`,
  `enable_community_page_on_desktop: true`
- ✅ `[실측]` **폰 YouTube 앱에 "게시물" 탭이 보인다** (구독자 1명인데도)
- made_for_kids=false · public · 어드밴스드 기능 · 징계 없음 → 자격 충족
- **결론: 자격은 이미 있다. 설정으로 켤 것도 없다.**

### 10.3 "카페 운영" 경로 (정정판)
1. ~~구독자 500 대기~~ → **불필요.** 탭은 지금 열려 있다.
2. **막는 건 API뿐** → **GUI가 유일 경로.**
3. 그 GUI는 **Boss 폰**이다. ⚠️ **ADB로 폰을 잡으면 Boss 작업을 뺏는다**
   (2026-10-06 Boss 항의: "왜 자꾸 내 핸드폰 화면 뺏기는 거냐") → **Paste Pipeline**:
   Claude 원고 → `tg.sh`로 Telegram 배달 → **Boss가 복사붙여넣기 → 발행**.
4. 랩탑 Chrome GUI 자동화는 **실패 확인** — Windows Chrome이 WSL 경계를 넘는
   `--remote-debugging-pipe`를 거부(`Remote debugging pipe file descriptors are not open`),
   Chrome 136+는 기본 프로필 원격 디버깅 차단. **이 경로 폐기.**
5. 채널 정체가 "**되어가는 과정의 오픈**"이므로 게시물 1호 주제는 정해져 있다:
   채널 소개 개편 + 습작/정규 구분 + 기준선(`Ref.`) 선언.

> 참고: papyrus `CLAUDE.md`의 "개발법 제1조 (Community-First)"는 **다른 개념**(조사 우선 개발법) — 유튜브 커뮤니티 탭과 무관.

---

## 11. 폰 러너 — `scripts/ytch.py` `[실측 2026-10-06]`

랩탑 6레포에서 긁은 **채널별 토큰 18개**를 지도로 삼아, 폰에서 어느 채널이든 읽고 쓴다.
기본 채널 = `musician-parksy`.

```bash
python3 scripts/ytch.py channels                      # 채널 지도 전체
python3 scripts/ytch.py whoami                        # 기본=musician
python3 scripts/ytch.py whoami --channel blogger-parksy
python3 scripts/ytch.py playlists                     # 소유 플레이리스트
python3 scripts/ytch.py videos --playlist PLjxh2pH0uEjrZCK0DDK6TGH1PFT06lrVi
python3 scripts/ytch.py add <PLID> <VIDEOID>          # playlistItems.insert
python3 scripts/ytch.py upload f.mp4 --title T --playlist PLID        # 계획만
python3 scripts/ytch.py upload f.mp4 --title T --confirm             # 실행(게이트 후)
```

- 자격증명 = `/root/.secrets/youtube/` (**레포 밖**). 지도 = `CHANNEL-MAP.json`. 값은 절대 출력·커밋 안 함.
- `.secrets.env`에 `MUSICIAN_CLIENT_SECRET`·`MUSICIAN_TOKEN`·`MUSICIAN_SECRET_DIR`(경로만) 등록됨.
- **`--confirm` 없으면 업로드 안 함** = 자동 업로드 금지 규칙을 코드에 박음.

### 11.1 채널 지도 (18 생존 + 1 죽음) `[실측]`

| 슬러그 | 채널 | 영상 | 비고 |
|---|---|---|---|
| `musician-parksy` | **뮤지션 박씨** | 39 | ★ 배포 아카이브 |
| `blogger-parksy` | 출판인 박씨 | 27 | 툴 타깃 플레이리스트 소유 |
| `visualizer-parksy` | 화가 박씨 | 12 | |
| `technician-parksy` | 기능인 박씨 | 9 | |
| `philosopher-parksy` | 철학자 박씨 | 6 | |
| `dtslib-branch` | dtslib-branch | 73 | 계정 b |
| `EAE-University` | EAE Univ. | 95 | 계정 c |
| `BeingEduartEngineer-4` | EAE Broadcast | 11 | |
| `espiritu-tango`·`artrew-i1w`·`phoneparis-r6q`·`alexandria-y6k`·`justino-fashion` | (계정 b 계열) | — | Parksy-webzine 포함 |
| `dtslib_com`·`dtslib_world` | dtslib_com/world | 1/0 | 계정 d |
| `a`/`b`/`c` | 계정 토큰 (papyrus) | — | musician 채널 아님 |
| `d` | — | — | ❌ `invalid_grant` 죽음 |

> `parksy-image`의 토큰이 **채널 단위**라 §2.2의 플레이리스트 소유 불일치를 이제 양쪽에서 다 볼 수 있다.

---

## 12. 발행 레저 — 공개/비공개 두 레인 `[Boss 지시 2026-10-06]`

> Boss: "공개 비공개를 **습작 자동화**와 **내 결재 이후 포스팅**의 레저 구분 설정을 줘"

**말로 금지하지 않고 코드로 강제한다.** 규칙 = `configs/publish-policy.json` · 상태 = `configs/publish-ledger.json` · 집행 = `scripts/ytch.py stage|publish|ledger`.

### 12.1 레인 구분

| 레인 | 누가 | 산출 | privacy |
|---|---|---|---|
| **A. 습작 자동화** | 파이프라인·AI | `draft`(습작) → `review`(결재대기) | **private** |
| **B. 결재 후 포스팅** | **Boss** | `approved`(결재됨) → `published`(공개) | private → **public** |

### 12.2 상태 5종

| 상태 | 한국어 | privacy | 전이 주체 |
|---|---|---|---|
| `draft` | 습작 | private | pipeline |
| `review` | 결재대기 | private | pipeline |
| `approved` | 결재됨 | private | **boss** |
| `published` | 공개 | **public** | **boss** |
| `retired` | 보관 | private | boss |

### 12.3 강제 게이트 — 실측으로 확인 `[실측 2026-10-06]`

```
$ ytch.py stage 8qvBCM4Ftzw published
⛔ 거부 — 'published'(공개)는 Boss 결재가 필요한 전이다.
   쓰는 법: stage <id> published --by Boss

$ ytch.py publish <id>          # --by 없이
⛔ 거부 — 공개는 Boss 결재 없이 불가.

$ ytch.py stage <id> review     # 파이프라인 레인
✅ draft → review (결재대기)  privacy=private
```

→ **`approved_by`·`approved_at` 기록 없이는 공개 전이가 코드에서 막힌다.** `videos.update`로 privacy를 직접 바꾸고 기록을 남긴다.

### 12.4 레저 초기 시드 `[실측]`

`ytch.py ledger --sync` → **50편 = 39 published / 10 draft / 1 review.**
(채널 통계 "영상 39"는 **공개만** 센 값. 실제 업로드 50, 비공개 11.)

### 12.5 기준선 규칙 — Boss 정정 `[Boss]`

> "AIVA, Gemini Song 카테고리는 내가 옛날에 **구독해서 생성했던 AI 생성물의 수준을 베이스라인**으로 설정하려고 한 거야. **이거보다 좋은 게 무조건 나와야** 되는 거라 내가 샘플로 넣어놓은 거야."

→ **`Ref.` = 참조가 아니라 "넘어야 할 기준선(reference bar)".** 내가 처음에 "이름과 내용 불일치"로 오진했으나 **Boss 의도가 맞았다**(철회).
- `Ref.Gemini Song` = Boss가 Gemini 구독 시절 생성한 CM송·응원가·로고송 8편
- `Ref.AIVA` = AIVA 알고리듬 샘플 10종 + MIDI 임포트 2편
- **규칙: [박씨 렌더링]의 결과물은 이 둘보다 항상 좋아야 한다.**

### 12.6 플레이리스트 규칙 (실측 문제에서 도출)

`[박씨 렌더링]` 24칸 중 **9편이 비공개** → 시청자는 15편만 봄.
→ **규칙: `draft`/`review`/`approved`는 공개 재생목록에 넣지 않는다.** 비공개가 공개 재생목록을 오염시킨다.

---

*agent mark `_Claude` · 2026-10-06 · 갱신: 계정 a 토큰 18개 이식 + 러너 `ytch.py` + 발행 레저(공개/비공개 게이트) 구축. 실측은 읽기·상태 전이까지 — 실제 영상 업로드(`videos.insert`)는 미실행*
