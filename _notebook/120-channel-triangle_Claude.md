---
date: 2026-10-06
agent: Claude
mark: _Claude
type: charter
status: active
location: S25 Ultra proot (오프라인 상주 정본)
related:
  - 119-musician-parksy-youtube-archive-ops_Claude.md
  - 118-parksy-label-goal-real-bottleneck_Claude.md
  - 117-three-node-music-workcenter_Claude.md
---

# 뮤지션 박씨 — 사각형 정본 (Channel Quad + Loopback)

> **Boss 지시 (2026-10-06):**
> "폰 proot 우분투 업무수첩 · GitHub 이미지 레포 · YouTube 이 채널,
> **이 세 개가 삼각형으로 같이 돌아가야 되니까 다 같이 저장해야 되는 거야.**"
>
> 그리고 **네 번째 노드**:
> "세계가 완벽하게 물려서 돌아갈 거고 **https://parksy.kr/channel/musician/** —
> 여기 내 방송국에서는 **실제로 YouTube에서 할 수 없는 것들만** 여기에서 **루프백** 돌아가지고.
> 내가 **PWA 웹페이지로 경험**할 수 있는,
> **YouTube 저작권이라든지 이런 게 문제가 생길 때**,
> **영상이 아닌 앱**으로 무언가를 해야 될 때는 여기로 가서
> **영상이 아닌 콘텐츠 · 음원이 아닌 콘텐츠**를 만들게 되는 거야. **구조 정확하게 파악해.**"
>
> 그리고 채널의 정체:
> "**옛날에는 그냥 습작**이었고, **이제부터 제대로 채널 운영하면서 AI 활용해서
> 진짜 음악가가 되어 가는 과정 — 그 과정 자체를 오픈**하고 만든 음악들을 여기다 게시할 거야."

---

## 0. 사각형 — 네 노드가 같이 돈다

| # | 노드 | 실물 | 역할 | 방향 |
|---|---|---|---|---|
| ① | **폰 proot 업무수첩** | `/root/work/_notebook/` (+ `notebook/*.html`) | 기억·판단·함정·실측 | 뇌 |
| ② | **GitHub 이미지 레포** | `dtslib1979/parksy-image` | 정체성·자산의 **공개 정본** | 정본 |
| ③ | **YouTube** | @musician-parksy `UCun6b2HD3ekp35PhqbTfOlg` | **송출(out)** — 영상·음원 | 送 |
| ④ | **parksy.kr 방송국** | `parksy.kr/channel/musician/` · 레포 `dtslib1979/parksy.kr` | **루프백(return)** — YouTube가 못 하는 것 | 還 |

**원칙: 하나를 바꾸면 넷 다 저장한다.**
(2026-10-06 실제로 깨졌다 — Boss가 YouTube에서 재생목록 이름을 바꿨는데
소개글·수첩·레포가 옛 이름을 들고 있었다.)

### ③과 ④의 분업 — 이게 핵심이다

| | ③ YouTube | ④ parksy.kr 루프백 |
|---|---|---|
| 매체 | **영상 · 음원** | **영상 아님 · 음원 아님** |
| 형식 | 파일(MP4/오디오) | **앱 (PWA, 상호작용)** |
| 제약 | **저작권·Content ID·정책**이 걸린다 | 걸리지 않는다 (내 루트) |
| 소비 | 보다 | **경험하다** (누르고, 풀고, 틀고) |
| 한계 | YouTube 정책이 상한 | 내가 만든 것만 있으면 무한 |

> **④는 ③의 실패 처리장이 아니라 ③의 반대편이다.**
> YouTube에서 **못 하는 것만** ④로 온다. 할 수 있는 걸 ④로 가져오면 중복이다.

---

## 1. ④ 루프백의 실제 구조 `[실측 2026-10-06 · 코드 확인]`

### 1.1 위치

```
parksy.kr/                       ← 역 로비 (1F Lobby, 5개 채널)
parksy.kr/channel/musician/      ← CH.04 MUSICIAN TV  ← 루프백이 사는 방
parksy.kr/design/loopback.js     ← 엔진 (187행)
parksy.kr/design/loopback.css    ← 껍데기
```

### 1.2 엔진이 선언한 목적 — 코드 첫 줄

```javascript
// PARKSY Loopback Services — YouTube가 못 해주는 것
```

그리고 `loopback.css`는 **모든 섹션 제목 뒤에 문자 그대로 이 문장을 붙인다**:

```css
.lb-section-title::after {
  content: 'YouTube cannot do this';
}
```

→ 루프백은 아이디어가 아니라 **이미 구현된 4종 서비스**다.

### 1.3 서비스 4종 (`window.ParksyLoopback`)

| 서비스 | init 함수 | 하는 일 | 현재 상태 |
|---|---|---|---|
| **퀴즈** | `initQuiz(container, moduleKey)` | KR Merit 자가진단 — 문항·정답 데이터가 JS에 내장 | ✅ 4모듈 가동 |
| **BGM 플레이어** | `initBGM(container, audioUrl)` | `data-url`의 오디오를 **루프 재생** (`audio.loop = true`) | ⏳ `data-url=""` → "Coming Soon" |
| **웹툰 뷰어** | `initWebtoon(container, tistoryUrl)` | 티스토리 CDN을 **iframe으로 임베드** | ⏳ `data-url=""` → "Coming Soon" |
| **프롬프트 뷰어** | `initPrompts(container, prompts)` | **AI 프롬프트 체인 전문을 공개** (PROMPT 1..n) | ⏳ 데이터 없음 |

**자동 초기화:** `DOMContentLoaded`에서 `[data-loopback="quiz|bgm|webtoon|prompts"]` 속성을 스캔해 자동 init.
→ **새 루프백 콘텐츠 추가 = `data-url` / `data-module` / `data-prompts` 한 속성만 채우면 된다. 코드 수정 불필요.**

### 1.4 퀴즈 4모듈 (내장 데이터)

| key | 이름 | 테마색 |
|---|---|---|
| `democracy-fantasy` | 민주주의 판타지 | — |
| `bluff-liberal-arts` | 허세교양 | `#ff6b35` |
| `halfblood-language` | 하프블러드 어학 | `#6baaff` |
| `edit-obsession` | 편집강박 | `#a78bfa` |

각 5문항 · true/false · 점수 → 판정(verdict).

### 1.5 채널 페이지의 나머지 (루프백 아닌 부분)

- 태그: `BGM · Audio · Lyria3 · Music · With-AI`
- 모듈 카드 4장: `korean-parksy`(KR Merit) · `국어`(고교교재·Lyria3) · `Prompt → Essay`(With-AI) · `Chalkboard`(Tistory)
- YouTube 박스: `@musician-parksy` 구독 버튼
- Latest Videos: `Coming Soon` ×2 (**API 연동 안 됨 — `/api/v1/youtube.json`이 원천인데 연결 미구현**)

### 1.6 역 전체에서의 위치

`parksy.kr` 로비 = 5개 채널: `philosopher` · `blogger` · `visualizer` · **`musician`** · `technician`
→ **YouTube 인증된 5채널에만** 프로그램 페이지가 있다 (`docs/CHANNEL-PAGES.md`).
데이터 원천은 `/api/v1/youtube.json` (handle·youtubeUrl·contentType·persona).

**층 구조(역 전체):** 1F Lobby → B1 Channels → B2 Studio → B3 Console → B4 Office(🔒)

### 1.7 트릴로지에서의 위치

```
parksy.kr (개체/날것) → dtslib.kr (회사/상품) → eae.kr (교육/구조)
       ↑ musician 채널은 여기, 1층 로비에서 4번째 문
```

역 문서가 이미 선언한 **YouTube 전략 3줄** (`docs/STATION-ARCHITECTURE.md`):
| 용도 | 내용 |
|---|---|
| **찌라시** | 홍보용 짧은 클립 → 방송국으로 유입 |
| **루프백** | 방송국 콘텐츠 → 숏츠 → 다시 방송국 |
| 레포 설명 강의 | 레포 구조/코드 설명 교육 |

---

## 2. 채널 정체 — 되어가는 과정의 기록 `[Boss]`

- **옛 업로드 (2019~2026년 초)** = 음악가가 되기 전의 **그냥 습작**. → **지우지 않는다.**
- **지금부터** = AI를 붙들고 **진짜 음악가가 되어가는 과정 자체를 오픈**한다.
- **채널의 성격** = 완성된 음악가의 쇼룸이 **아니다**. **되어가는 과정의 기록**이다.

---

## 3. 어디로 가는가 `[Boss · 118]`

```
퍼블릭 도메인 원곡 → 내 편곡 → 내가 만든 가상악기 → 내가 만든 가상보컬 → 레이블
```

- **진짜 병목은 녹음이 아니라 편집**(SFZ 저작·벨로시티 레이어·루프 포인트) — 118.
- 물리적 입구 확보: **바순(조카)** = Slot A.

### 여기서 ④가 다시 필요해진다 — 저작권
원곡이 퍼블릭 도메인이면 ③(YouTube)으로 간다.
**아직 PD가 아니거나 Content ID가 걸리는 것**은 ③에 못 올린다 → **④로 가서 앱으로 만든다.**
이것이 Boss가 말한 "저작권 문제가 생길 때 영상이 아닌 앱으로" 의 정확한 의미다.

---

## 4. 공개/비공개 레저 — 두 레인 `[Boss 지시 2026-10-06]`

정본: `configs/publish-policy.json` · `configs/publish-ledger.json` · 집행 `scripts/ytch.py`

| 레인 | 주체 | 상태 | privacy |
|---|---|---|---|
| **A. 습작 자동화** | 파이프라인·AI | `draft` → `review` | **비공개** |
| **B. 결재 후 포스팅** | **Boss** | `approved` → `published` | → **공개** |

**`approved_by`·`approved_at` 없이는 공개 전이가 코드에서 거부된다** (실측).

**레저는 ③(YouTube)에만 적용된다.** ④(parksy.kr)는 Git이 곧 원장이므로
`draft → main` 병합 = Boss 결재로 갈음한다.

---

## 5. 기준선 규칙 `[Boss 정정]`

> "AIVA, Gemini Song은 내가 옛날에 구독해서 생성했던 **AI 생성물의 수준을 베이스라인**으로
> 설정하려고 한 거야. **이거보다 좋은 게 무조건 나와야** 되는 거라 샘플로 넣어놓은 거야."

- `Ref.` = 참조가 아니라 **넘어야 할 기준선(reference bar)**.
- **규칙: [박씨 렌더링]의 결과물은 항상 이 둘보다 좋아야 한다.**

---

## 6. 재생목록 (2026-10-06 Boss 수작업 반영) `[실측]`

| 재생목록 | ID | 칸 | 시청자 노출 |
|---|---|---|---|
| [박씨 렌더링] | `PLjxh2pH0uEjrZCK0DDK6TGH1PFT06lrVi` | 24 | **15** (9편 비공개) |
| Parksy BGM | `PLjxh2pH0uEjqkF-ta-4ySDzQ9kow4NI6j` | 7 | 7 |
| Ref.Gemini Song | `PLjxh2pH0uEjrFDjfuPEmkmzSsUAX_LbbN` | 8 | 8 |
| Ref.AIVA | `PLjxh2pH0uEjoNUxa0KW4nim_9GpI9ki1X` | 9 | 9 |

- 중복 0 · 공개 미분류 0
- **규칙: 비공개(draft/review/approved)는 공개 재생목록에 넣지 않는다.**

---

## 7. 동기화 표 — 무엇이 어디에 사는가

| 자산 | ① 폰 수첩 | ② parksy-image | ③ YouTube | ④ parksy.kr |
|---|---|---|---|---|
| 채널 정체·소개글 | 이 문서 §2 | `MUSICIAN-CHANNEL-CHARTER.md` | 소개글 968자 ✅ | `channel/musician/index.html` |
| 발행 레저 | §4 + `configs/` | 동일 | API로 집행 | — (Git이 원장) |
| 기준선 규칙 | §5 | 동일 | 재생목록 2개 | — |
| 재생목록 지도 | §6 | 동일 | 실물 | — |
| 루프백 구조 | §1 | — | — | 실제 코드 + `docs/` |
| 프롬프트 체인 | — | — | 영상에 언급 | **`data-prompts`로 전문 공개** |

> ④의 "AI PROMPTS USED" 칸은 **비어 있다.** Boss가 "프롬프트 체인 전문 공개"를
> 채널 서사로 잡았으므로, 실제 프롬프트 원장을 여기로 흘려보내면 **YouTube가 못 하는 것**을
> 그대로 채우게 된다. — 다음 작업 후보.

---

## 8. 노드별 현재 상태 `[실측 2026-10-06]`

| 노드 | 상태 |
|---|---|
| ① 폰 수첩 | 이 문서 · 커버리지 gap 0 |
| ② parksy-image | 이 정본 커밋 (폰 클론은 git 브랜치 손상 → API 경유 push) |
| ③ YouTube | 소개글 968자 ✅ · 재생목록 4개 ✅ · 게시물 탭 실재(API 없음→Paste Pipeline) |
| ④ parksy.kr | **건물 완성** · 루프백 엔진 4종 中 1종만 데이터 있음(퀴즈) · BGM/웹툰/프롬프트 전부 `Coming Soon` |

---

## 9. 함정 기록

| 함정 | 내용 |
|---|---|
| 사각형 깨짐 | YouTube만 고치면 소개글·수첩·레포가 옛 값을 들고 있는다 → **한 번에 넷** |
| 폰 parksy-image 클론 | `fatal: your current branch appears to be broken` — 폰 클론 신뢰 금지 |
| **clone 타임아웃** | 폰에서 `git clone parksy.kr`(18MB)가 2분 초과 — **API 경유가 정답** |
| 폰 화면 뺏기 | **ADB로 폰 GUI를 잡으면 Boss 작업을 뺏는다** → 게시물은 Paste Pipeline |
| 커뮤니티 탭 오진 | "구독자 500 미달이라 탭 없음"은 **낡은 정보**. 탭은 실재. 단 API에 게시물 엔드포인트 없음 |
| 루프백 오해 | ④는 "YouTube 대피소"가 아니다. **YouTube가 할 수 있는 건 ③에 둔다** — 중복 금지 |

---

*agent mark `_Claude` · 2026-10-06 · 사각형: 폰 수첩 ① → parksy-image ② → YouTube ③(송출) → parksy.kr ④(루프백)*
