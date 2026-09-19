# PO-MKT-001 — Parksy 판매 조사 결과 (근거 기반)

> 실행일: 2026-09-04 · 조사 방식: GitHub API 39레포 전수 + 로컬 클론 직접 열람 + papyrus 문서 감사
> 원칙: 추측 금지. 모든 주장에 근거 경로. 데이터 없으면 "데이터 없음" 명시.

---

## Q1. 완성도 스캔 — 상위 3개 레포

### 스캔 범위와 방법
- 39개 레포 전수(`dimas-40` 6 + `dtslib1979` 28 + `helena751107` 5)에 대해 GitHub API로 `pushed_at`·`size`·`language`·`description` 수집, `readme` 엔드포인트로 README 존재 여부 확인(200/404).
- README 없는 7개: `alexandria-sanctuary`, `dtslib-papyrus`, `eae-univ`, `espiritu-tango`, `gohsy-fashion`, `gohsy-production`, `hoyadang.com` (단 `dtslib-papyrus`는 README 대신 `00-INDEX.md`+`CLAUDE.md`+`HANDBOOK.md`가 있음 — "README 대체 문서" 보유).
- 실행 가능성은 로컬 클론에서 진입점(run.py/스크립트/설치 스크립트)과 의존성 선언을 확인. 실제 실행은 하지 않음(규칙상 dry-run/진입점 존재로 판단).

### 완성도 상위 3 (근거)

**1위 — `dtslib1979/parksy-audio` (박씨 뮤지션 제품 본체)**
- 마지막 push: 2026-09-03 (API `pushed_at`), size 986MB, 401커밋(자체 stats)~476커밋(papyrus 감사).
- README 완비: E2E 파이프라인 명시 — `python3 run.py input.mid`, `--dry-run --emotion-mode` 옵션까지 문서화.
  → `/tmp/survey/clones/parksy-audio/README.md`
- 실행 가능: 진입점 `run.py`(5단계: Humanize→Gate→Render→Master→Visual), `core/humanize.py`, `core/gate.py`, `engines/render_orchestral.py`, 스크립트 30+개(`scripts/batch_emotion.py`, `batch_render_all.py`, `tts_engine.py`, `singing_pipeline.py` 등).
  → `/tmp/survey/clones/parksy-audio/scripts/`, `engines/`, `core/`
- 실산출물 증거: YouTube 39영상·조회 1,726·구독 1 (`web/data/stats.json` 2026-06-30), 렌더 영상 230편/18,755MB, 감정트랙 329곡.
  → `/tmp/survey/clones/parksy-audio/web/data/stats.json`
- 외부 의존성: FluidSynth + FFmpeg + 사운드폰트 필요(README 명시) → **완전 단독은 아니나 단일 명령 진입**.

**2위 — `dtslib1979/dtslib-apk-lab` (앱 배포 랩 · 최다 커밋 923)**
- 마지막 push: 2026-09-01, language Dart.
- README 완비: "폰 중심 온디바이스 월드" 아키텍처 + 앱 카탈로그.
  → `/root/work/_import/dtslib-apk-lab/README.md`
- 실행 가능: `app-registry.json`에 앱 18종 등록, 9종 `store-registered`, 4종 `download_active: true` (Parksy Capture 11.0.0, Parksy Pen 1.0.31 등), 버전·workflow·라인수(dart/kotlin)까지 기계적으로 관리.
  → `/root/work/_import/dtslib-apk-lab/app-registry.json`
- CI 23개 workflow (papyrus 감사), Play Store 등록 = 실제 사용자 존재 증거.
  → `/root/papyrus/docs/강이철박사-미팅자료/inventory-hard-evidence-2026-07-28.md`
- 외부 의존성: Flutter/Android SDK 빌드 필요 → 단독 실행은 빌드 환경 필요.

**3위 — `dtslib1979/parksy-image` (이미지·영상 시드 제품)**
- 마지막 push: 2026-09-04 (**39레포 중 가장 최신**), language Python.
- README 완비: 운용 백서·역할분리(Aider=설계/Grok=실행) 명시.
  → `/tmp/survey/clones/parksy-image/README.md`
- 실행 가능: `run_actor_pipeline.py`, `comfyui_bot/`, `tools/grok_gen*.py`, `mcp-servers/parksy_gallery_mcp.py` 등 스크립트 다수 존재.
  → `/tmp/survey/clones/parksy-image/`
- 단점(정직): 감사 문서가 "outputs 거의 비어있음(4KB씩)" 지적 — 산출물보다 문서·프롬프트 중심.
  → `/root/papyrus/docs/강이철박사-미팅자료/inventory-hard-evidence-2026-07-28.md` 2장
- 외부 의존성: Grok CLI · ComfyUI · RunPod — 외부 의존이 가장 큼.

### (참고) 3위 경쟁 후보
- `termux-bridge`(push 09-01): "curl 한 줄 → 박씨 폰 환경 10분 재현" 설치 스크립트. **단독 실행·패키징 관점에선 최상**이나, 제품 콘텐츠가 아닌 인프라/설치 도구라 본문 3위에서 제외.
  → `/tmp/survey/clones/termux-bridge/README.md`
- `dtslib-papyrus`(push 08-28, 871커밋): 676개 md를 담은 지식 허브. README.md는 없지만 `00-INDEX.md` 등 문서 풍부. 제품이 아닌 뇌/코디네이터.

---

## Q2. 타겟 고객 추론 — "이미 반응한 사람들" (로그 기반)

### 1) 실존 협업자 1명 — 강이철 박사 (문서상 "강희철" 표기 혼재)
- 정체: ESG·디지털기술 협회장, CS 박사, 국책과제 심사위원 시선.
  → `/root/papyrus/docs/강이철박사-미팅자료/pitch-priority-2026-07-28.md`
- 실제 미팅: 2026-07-29 (레벨 미팅). "파워 유저" 프레임으로 접근, 기능 복제 가능성 검증에 관심.
  → `/root/papyrus/docs/강이철박사-미팅자료/meeting-retrospective-2026-07-29.md`
- 그가 요구한 스펙: 국책과제 포장, **"복제 단가"** 질문에 답, ESG(환경·사회·거버넌스) 교육 프로그램, "과거 박씨를 판매하는 번역자·전파자" 슬롯.
  → `/root/papyrus/docs/강이철박사-미팅자료/01_ESG_뮤지션OS_사업제안_20260705.md`, `solution-collaborator-kang-2026-07-28.md`
- 상태: 공식 협업 계약 없음(레벨 미팅). 단 슬롯 구조(박씨=계속 창작, 강박사=과거 박씨 포장·판매) 확정.

### 2) 텔레그램 과외 4명 (강이철 경유 — 실제 학습자)
| 학습자 | 사업 | 연결 레포 |
|--------|------|-----------|
| 호야당 아저씨 | 빵집 | hoyadang.com |
| 오복집 | 족발집(실운영) | obokzip → justino |
| 고시 | 패션 | gohsy-fashion |
| 쿠시 | 셀럽 스토리 | koosy |

- 근거: "강이철이 이미 텔레그램으로 4명을 과외 중" — 시스템 사용자 4명/학습자 4명으로 정정.
  → `/root/papyrus/docs/강이철박사-미팅자료/counter-two-track-2026-07-28.md`
- 단, 이 4명의 개별 성과·결제·문의 기록은 레포에 없음 → "과외 진행 중" 외의 정량 데이터는 0건.

### 3) 브랜치 비즈니스 6개 사업체 (라이브 도메인)
- 빵집 hoyadang.com(77KB) · 변리사 buckleychang.com(43KB) · 패션몰 gohsyfashion.com(36KB) · 부동산 namoneygoal.kr(70KB) · 쇼핑몰 papafly.kr(39KB) · AI세팅 phoneparis.kr(18KB).
  → `/root/papyrus/docs/강이철박사-미팅자료/inventory-hard-evidence-2026-07-28.md` "6개 라이브 웹사이트" 표
- 이들은 "고객이 반응한" 사례가 아니라 박씨가 만들어준 동업/조력 사업체. 매출·문의 수치는 데이터 없음.

### 4) YouTube 실제 시청·반응자 (하드 통계)
- 4계정 15채널: **구독자 합계 19명 · 조회수 합계 26,640회 · 영상 180개 · 댓글 있는 영상 23개**.
  → `/root/papyrus/docs/hq/youtube-data.json` (2026-04-21 스냅샷)
- 채널별: @EAE-University 13,054회/11구독 · @dtslib-branch 11,154회/7구독 · @musician-parksy 1,616회/1구독 · @philosopher-parksy 353회.
- 뮤지션 채널(제품 본체) 단독: 구독 1 · 조회 1,726 · 영상 39개.
  → `/tmp/survey/clones/parksy-audio/web/data/stats.json`, `/tmp/survey/clones/parksy-audio/data/youtube-catalog.json`
- 실제 반응(댓글/좋아요) 상위: 가족사진(조회 1,154/좋아요 6/댓글 2), Outdoor Office(436/2/2), JAZZ PIANO(355/1/1), 다이소갓성비(313/1/1), Github Repo Apps(302/1/0).
  → `/root/papyrus/docs/hq/youtube-data.json` (videos[].commentCount/likeCount)

### 5) "타겟 검증 데이터 0건" 항목 (정직 고지)
- **황권중**: papyrus·work·survey 전부 grep 무히트 → **데이터 0건**.
- **피드백/문의/결제 로그**: `feedback/feedback.json`은 `entries: []` (total_events 0)로 빈 배열.
  → `/root/papyrus/feedback/feedback.json`
- **parksy-logs**: 외부 문의가 아니라 박씨 본인의 ChatGPT/Claude 대화 자가기록(logs/ 2025-12~) → 외부 고객 검증 데이터 아님.
  → `/tmp/survey/clones/parksy-logs/README.md`, `logs/`
- **블로그 댓글**: 티스토리 백업 5개 `_INVENTORY.md`는 "포스트 제목 목록"만 있고 조회수·댓글·반응 수치는 없음.
  → `/root/papyrus/parksy.kr/backup/blogs/*/_INVENTORY.md`

**결론:** 반응자는 ①강이철(협업자 1) ②과외 4명(간접) ③YouTube 시청자(구독 19·조회 2.6만·댓글영상 23)로 3개 층이 식별됨. "구매·문의·결제로 반응한 고객"은 **0건** — 현재 반응은 '협업 관심 + 유튜브 미량 조회' 수준이며, 실구매 전환 데이터는 없다.

---

## Q3. 판매 형태 타당성 매트릭스

### 1) parksy-audio
| 판매 형태 | 판단 | 근거 |
|-----------|------|------|
| 1회성(패키징) | **가능** | `run.py`+`scripts/`+`engines/`+MIDI 라이브러리(감정트랙 329)가 템플릿/zip 패키징 대상. 단 26GB 산출물(mp4/wav)은 바이너리라 제외, "파이프라인+프롬프트+템플릿" 형태. |
| 구독형 | **약함** | 업로드 이력이 버스트형: 2025-06(8곡)→2026-02(15곡)→2026-05(15곡). 주간 리듬은 `docs/schedule/CALENDAR.md`에 계획만 있고 체크박스 미완(□). |
| 컨설팅형 | **가능** | `run.py` 단일 명령 + `--dry-run` + `scripts/batch_*.py` 등 반복 재현 스크립트 존재. |

### 2) dtslib-apk-lab
| 판매 형태 | 판단 | 근거 |
|-----------|------|------|
| 1회성(패키징) | **가능** | `app-registry.json`(18앱)+APK 산출물+빌드 workflow가 패키징 단위. |
| 구독형 | **없음** | Play Store 9개 등록·4개 활성 다운로드지만 구독/정기 과금 모델 아님. |
| 컨설팅형 | **가능** | 앱별 `theme_strategy`/`constants_class`/workflow 템플릿 구조가 재현 스크립트로 재사용 가능. |

### 3) parksy-image
| 판매 형태 | 판단 | 근거 |
|-----------|------|------|
| 1회성(패키징) | **제한적** | `run_actor_pipeline.py` 등 존재하나 산출물(outputs)이 거의 빈 상태(감사 4KB). 프롬프트·백서 문서는 풍부. |
| 구독형 | **약함** | 10초 인트로 소스(`intros/`) 있으나 정기 배포 이력 없음. |
| 컨설팅형 | **가능** | `tools/grok_gen*.py`, `comfyui_bot/`, `on_demand/` 등 재현 스크립트 존재. 단 Grok/RunPod/ComfyUI 외부 의존이 큼. |

### (보론) 컨설팅형 최적 후보 — termux-bridge
- "curl 한 줄 → DeepSeek 키만 있으면 박씨 폰과 동일 환경 10분 재현" 설치 스크립트(`g`, `install.sh`, `setup.sh`).
  → `/tmp/survey/clones/termux-bridge/README.md`
- **컨설팅형·1회성 판매에 가장 적합한 재현 스크립트**이나, 제품(콘텐츠)이 아니라 인프라 설치 도구라는 한계.

---

## 조사한 레포 / 데이터 출처 목록

**GitHub API (PAT 경유, 토큰 비노출):**
- `api.github.com/repos/{owner}/{repo}` — 39레포 pushed_at/size/language/description
- `api.github.com/repos/{owner}/{repo}/readme` — README 존재 여부

**로컬 클론 (직접 열람):**
- `/root/papyrus` = dtslib-papyrus (docs/강이철박사-미팅자료/, docs/hq/youtube-data.json, feedback/feedback.json, parksy.kr/backup/blogs/*/_INVENTORY.md, telegram/)
- `/root/work` = helena_phone
- `/root/work/_import/dtslib-apk-lab`, `/root/work/_import/dtslib-cloud-appstore`
- `/tmp/survey/clones/` — parksy-audio, parksy-image, parksy-logs, parksy.kr, termux-bridge, dtslib-localpc, dtslib-branch, phoneparis (sparse: md/py/js/sh/json/yml/yaml/html/css/txt만)
- `/tmp/survey/helena-piano`, `helena-metalcare`, `helana-faith`, `helana_log`

**핵심 근거 파일:**
- `/root/papyrus/docs/강이철박사-미팅자료/inventory-hard-evidence-2026-07-28.md`
- `/root/papyrus/docs/강이철박사-미팅자료/meeting-retrospective-2026-07-29.md`
- `/root/papyrus/docs/강이철박사-미팅자료/counter-two-track-2026-07-28.md`
- `/root/papyrus/docs/강이철박사-미팅자료/pitch-priority-2026-07-28.md`
- `/root/papyrus/docs/강이철박사-미팅자료/solution-collaborator-kang-2026-07-28.md`
- `/root/papyrus/docs/hq/youtube-data.json`
- `/tmp/survey/clones/parksy-audio/README.md`, `web/data/stats.json`, `data/youtube-catalog.json`, `docs/schedule/CALENDAR.md`
- `/root/work/_import/dtslib-apk-lab/app-registry.json`, `README.md`
- `/tmp/survey/clones/parksy-image/README.md`
- `/tmp/survey/clones/termux-bridge/README.md`

*본 보고서의 모든 수치는 위 경로에서 직접 추출. 황권중·외부 구매/문의/결제 데이터는 존재하지 않아 "데이터 0건"으로 표기.*
