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

### 3.2 음악 채널 토큰(계정 a)은 **폰에 없다**

- 필요: `client_secret.json` + `accounts/token_a.json` (또는 `token_a__musician-parksy.json`)
- `[기록]` 실물 위치 = **랩탑 WSL**: `/home/dtsli/parksy-audio/tools/youtube/{client_secret.json, accounts/token_a.json}`
- `[실측]` 폰엔 없음 — `/root`, `/root/papyrus` 어디에도 `token_a.json` · `client_secret*.json` 없음
- `[실측]` 파피루스 `tools/youtube/accounts/`엔 `channels.json` + 스크린샷만. 토큰 실물 없음.

### 3.3 능력 경계 (이게 핵심)

| 능력 | 폰 현재 |
|---|---|
| 공개 채널/플레이리스트 **읽기** (아무 채널) | ✅ b 토큰으로 가능 |
| 계정 b(@dtslib-branch) **쓰기** | ✅ 가능 |
| **@musician-parksy 업로드·플레이리스트 수정** | ❌ **토큰 a 없음** |
| WD 패스포트 접근 | ❌ 폰 미마운트 |

> 계정 a 토큰을 폰에 들이려면: (i) 랩탑에서 파일 이식(델타) 또는 (ii) **채널 최초 1회 Boss PC 동의**(`CLAUDE.md` 원칙 — `@musician-parksy`는 ❓미확인 9개 중 하나). `[미검증]`

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
| 공개 채널·플레이리스트 **읽기** (b 토큰) | ✅ |
| 계정 b(@dtslib-branch) 운영 | ✅ |
| **@musician-parksy 업로드 / 플레이리스트 수정** | ❌ 토큰 a 없음 |
| **WD 패스포트 저장** | ❌ 미마운트 + 레인 미구현 |
| 노트북 기록·게이트 | ✅ |

---

## 8. 다음 작업 큐 (내가 주력으로 돌릴 것)

1. **계정 a 토큰 확보** — 랩탑에서 `client_secret.json` + `token_a` 이식(델타) 또는 채널 최초동의. 도착지: `.secrets.env`(또는 별도 gitignored). `[미검증]`
2. **플레이리스트 정합 교정** — 툴 타깃이 @blogger-parksy 소유(§2.2) → 의도 확인 후 musician 소유로 교정
3. **쿼터 재승인** — 계정 a 60k 재신청(09-23 만료). 안 되면 하루 ~6편으로 스케줄
4. **습작 → WD 아카이브 레인 설계** — 최종/습작 분기 규칙
5. **업로드 실행 게이트 자동화** — 렌더·인코딩·메타·SRT까지 자동, 발행은 Boss 게이트

---

## 9. 함정 기록 (재발 방지)

| 함정 | 내용 |
|---|---|
| 토큰 주인 가정 | `.secrets.env` YOUTUBE_* = **계정 b**(dtslib-branch). 음악 채널 아님 |
| access token 만료 | `.secrets.env`의 access는 401. **refresh부터** |
| playlist 소유채널 불일치 | 툴 타깃 3개가 **@blogger-parksy 소유**. 이름만 musician |
| 수치 부패 | `DIVISION-MAP.json` "232 videos" ≠ 실측 39 |
| 자동 업로드 | 금지. 검수 게이트 필수 |
| 파일 이식 | 대용량 바이너리 커밋 금지 → 델타 fetch/직접 전송 |

---

*agent mark `_Claude` · 2026-10-06 · 실측 좌표는 b 토큰(공개 읽기)으로 확보 — 계정 a 쓰기 경로는 미확보*
