# 전 레포 문서 재고 조사 — 종합 마스터 리포트

> 작성: 2026-09-04 · `_Claude` · Boss 지시 ("연결 레포 전체 문서 파싱 + 재고조사 문서 전수")
> 범위: 로컬에서 실측 접근 가능한 연결 레포 10곳 · 마크다운 문서 ~1,080개 · 전체 파일 ~5,800개
> 방법: 전 레포 `grep` 재고/인벤토리 키워드 전수 + 3개 병렬 파서(블로그·MCP·자산 / 반도체·러브레터·프로필 / helena·fridge) 교차 정리

---

## 0. 연결 레포 지도 (실측, 2026-09-04)

> 문서 속 "REDACTED" = GitHub 실제 계정 **`dtslib1979`** (git remote 실측 확인).
> "28레포"는 26개 private + 2개 public으로 구성되어, 로컬에서 실측 가능한 것은 public 부분 + helena 계열뿐.

| # | 레포 | 로컬 경로 | md | 파일 | 상태 |
|---|------|-----------|----|----|------|
| 1 | dtslib-papyrus (SSOT 허브) | `/root/papyrus` | 676 | 1,845 | ✅ 로컬 |
| 2 | helena_phone (현재 작업레포) | `/root/work` | 298 | 3,021 | ✅ 로컬 |
| 3 | helena-programming | `/root/work/helena-programming` | 19 | 253 | ✅ 로컬(무 git) |
| 4 | dtslib-apk-lab | `/root/work/_import/dtslib-apk-lab` | 23 | 239 | ✅ 로컬 |
| 5 | dtslib-cloud-appstore | `/root/work/_import/dtslib-cloud-appstore` | 6 | 49 | ✅ 로컬 |
| 6 | parksy-image | `/root/work/parksy-image` | 0 | 0 | ⚠️ .git만(워크트리空) |
| 7 | helena-piano | `/tmp/survey/helena-piano` | 10 | 79 | ✅ 클론 |
| 8 | helena-metalcare | `/tmp/survey/helena-metalcare` | 2 | 25 | ✅ 클론 |
| 9 | helana-faith | `/tmp/survey/helana-faith` | 2 | 24 | ✅ 클론 |
| 10 | helana_log | `/tmp/survey/helana_log` | 44 | 114 | ✅ 클론 |
| — | **합계** | | **~1,080** | **~5,649** | |

- dtslib1979 계정 공개 레포 실측: `dtslib-apk-lab` 1개만 public으로 노출. 나머지 26개는 private (로컬 클론: apk-lab·cloud-appstore·parksy-image·papyrus).
- helena751107 계정: 6개 전부 public (helena_phone·helena-piano·helena-metalcare·helana-faith·helana_log + 프로필 레포).
- dimas-40 계정: helena_phone 1개.

---

## 1. "재고 조사" 문서 시리즈 (연대기)

"재고 조사"는 단일 문서가 아니라 **시점별로 반복 생산된 전수 조사 시리즈**. 전 레포에 걸쳐 존재.

| 날짜 | 문서 | 성격·핵심 수치 |
|------|------|----------------|
| 2026-01-22 | `GITHUB_REPORT.md` | 22레포 (공개13/비공개9) · Pages 17 · 커스텀도메인 9 · 점수 9.6/10 |
| 2026-04-12 | `docs/SESSION-REPORT-2026-04-12-FULL-REPO-SURVEY.md` | **32레포 전수** (운영24/진행6/초기2) · YouTube 2계정 120K units/일 |
| 2026-06-05 | `docs/ASSET-INVENTORY-20260605.md` | "전체 자산 재고 조사" · 29레포 · AI음성모델 4 · MCP 17 · tmux 9 |
| 2026-07-06 | `PARKSY-END-STATION-…WHITEPAPER` §13 | "OS 재고조사" 팩트체크 |
| 2026-07-28 | `parksy-profile/inventory-hard-evidence` | **28레포 전수 재고조사** (ChatGPT 진단 vs Claude 반박 실증) |
| 2026-08-14 | `love-letter/04_inventory` | "마지막 재고조사" · 판정 🟢7 / 🟡21 / 🔴1 |
| 2026-08-16 | `_notebook/97` + `97b` + `97c` | S21 솔루션 재고조사 + Grok 평가 + AI 한계 역평가 |
| (상시) | `parksy.kr/backup/blogs/*/_INVENTORY.md` ×5 | 티스토리 블로그 5개 포스트 인벤토리 (합계 140포스트) |
| (상시) | `helena-piano/fridge/*.md` ×6 | "냉장고" 자산 공유 인벤토리 (parksy-audio 986MB 등) |

---

## 2. 레포별 재고 요약

### 2.1 dtslib-papyrus (허브 · 676 md)
디렉토리 분포: docs 281 · ad 73 · infra-history 34 · tools 29 · docs_backup 22 · recipes 21 · mcp-semicon 20 · telegram 16 · hq 15 · plans 14 · threads 10 등.

- **블로그 재고 (5개 _INVENTORY)**: 티스토리 5 페르소나 포스트 **140개** (dtslib 39 · programmer-park 37 · polyglot14 31 · musician-park 18 · webtoon-park 15). **추출 완료 1건뿐** — 인벤토리는 "본문 미백업 대기" 목록 상태.
- **MCP 인벤토리**: 3레이어 설계(IDEATION→POSTING→DISPLAY). 실 코드 MCP 4개(writer 9툴·platform 11툴·scm 11툴·alexandria 5툴). **배포 ACTIVE MCP = 0** (Railway stub 9·502 1). DISPLAY(dtslib-cloud-appstore) 100% 완성.
- **디자인 모듈 인벤토리**: 웹 32개 스캔 → 고유 11개 → **KEEP 20 / SKIP 7**. Cinema Family(Shutter·FilmGrain·GoldParticle·Timecode)가 최고 퀄리티.
- **반도체 FAB 재고 (mcp-semicon)**: 28레포 = 28 원자재 창고, BOM/BOR/Lot 메타포. 실측 총 **140GB · 67만 LOC · 353만 단어 · MD 12,740 · WAV 763 · MIDI 1,043 · JSONL 82,211줄 · AI모델 9버전 · 라이브도메인 14**.

### 2.2 helena_phone (현재 레포 · 298 md)
수첩 151장 (Grok 52 · Claude 39 · Boss 11 · 무표기 49). 루트 문서 10종(CLAUDE·CONSTITUTION·README 등).

- **97 재고조사**: 23일 · **436커밋 · 121장 수첩 · 110+ 웹진페이지** · 스크립트 70. **솔루션 8종** (피아노 웹진 · S21 시그니처 디자인 · PD V10 · 출판 파이프 · 티스토리 엔진 · 디렉터 게이트 · RVC 3음색 · 저사양 AI 생존).
- **97b Grok 평가**: 완성도 8.5 · 정직 9 · 해자 8 · 스토리 8. "재고 장부로 잘 뽑았다".
- **97c AI 한계 역평가**: AI = 대필작가(잣대 Boss, 붓 Claude). 해자 = "폰 한 대 + $20 + 목소리로 산 퍼포먼스".

### 2.3 helena-piano (위성 · 10 md) — "냉장고(fridge)" 원본
`fridge/` 6문서 = **재고조사 실물**. parksy-audio 986MB 전수 인벤토리 · S21 실행가능 목록 · MIDI→YouTube 파이프 지도 · YouTube 39영상 카탈로그.

### 2.4 helena-programming (19 md) — 앱·파이프 뼈대
`app-registry.json` 10개 등록: 앱 4 · 파이프 5 · MCP 1(pd-pipeline-mcp 9도구). GitHub Actions = 공짜 클라우드(7GB 러너) 전제.

### 2.5 helana_log (44 md) — 누나 라이프 아카이브
"헬레나가 사는 법" — 조현병과 사는 누나의 삶 기록(기술일지 아님). IDENTITY + METHOD(5섹션 스토리 구조) + care-daemon 5트랙 + 기자 8 + 로그.

### 2.6 기타
- dtslib-apk-lab (23 md): APK 빌드 실험실 — 앱 9개 · Play Store 9 · 활성다운로드 4 · Dart 15K줄.
- dtslib-cloud-appstore (6 md): PWA 12개 앱 스토어 (WebCodecs·FFmpeg.wasm).
- parksy-image: 워크트리 비어 있음 (로컬 캐시 없음).

---

## 3. 핵심 자산 수치 (재고조사 시리즈 교차 일치값)

| 자산 | 수치 | 출처 |
|------|------|------|
| 레포 총계 | 28(dtslib) + 6(helena) = 34 | fridge/01 · 46-architecture |
| parksy-audio | 986MB · 파일 72,602 · MP3 744 · docs 27종 | fridge/02 · love-letter/04 |
| parksy-logs | 14,184파일 · jsonl 18 · 로그 294 · 샘플 4,218 | love-letter/04 · SESSION-REPORT |
| parksy-image | 이미지 193 (8,875은 허위 — NUMBERS_AUDIT 시인) | NUMBERS_AUDIT-2026-07-31 |
| YouTube | 채널 "뮤지션 박씨" 39영상 · 계정 4·채널 15 (토큰 완비, 업로드 0) | fridge/05 · love-letter/05 |
| MIDI | 855 (실측) · 1,043 (BOM 집계) | NUMBERS_AUDIT · mcp-semicon |
| MCP 서버 | 17(자산) / 19(OS) · **배포 ACTIVE 0** | ASSET-INVENTORY · inventory-hard-evidence |
| AI 음성모델 | matched_v2 627MB · genie_onnx 321MB 등 4종 | ASSET-INVENTORY |
| 커밋 | papyrus 947 · apk-lab 923 · parksy.kr 1,518 | love-letter/04 |

---

## 4. 공통 진단 (전 재고조사가 반복하는 결론)

1. **시스템/자산은 두텁고, 외부 산출물·검증이 비어 있다.** 08-14 실사 🟢7/🟡21/🔴1 — 20레포가 "랜딩 있고 콘텐츠 0", YouTube 15채널 토큰 완비인데 업로드 0편.
2. **숫자는 실측으로 바로잡아야 한다.** "8,875 이미지"(실 193) 사건 — NUMBERS_AUDIT이 자체 시인. 재고조사의 가치는 "실물+숫자" 정직에 있음.
3. **병목은 배포/외부검증.** MCP ACTIVE 0, 블로그 백업 140포스트 중 추출 1건, "baptism.sh 1건이 증명의 시작".
4. **해자(최종 재정의, 97b)**: 코드는 복제 가능 → 전부 공개. 남는 건 "이 스토리를 실제로 산 사람"의 퍼포먼스·진정성. 폰 한 대(갤럭시 S21) + $20 + 목소리 + 동기(누나) + 수익화 안 함.

---

## 5. 원본 위치 (재고조사 문서 전수 인덱스)

```
/root/papyrus/docs/ASSET-INVENTORY-20260605.md
/root/papyrus/docs/DESIGN-MODULE-INVENTORY.md
/root/papyrus/docs/MCP-INVENTORY-2026-04-24.md
/root/papyrus/docs/MCP-STATUS-ONE-PAGE-2026-04-24.md
/root/papyrus/docs/SESSION-REPORT-2026-04-12-FULL-REPO-SURVEY.md
/root/papyrus/docs/parksy-profile/inventory-hard-evidence-2026-07-28.md
/root/papyrus/mcp-semicon/RAW_MATERIAL_INVENTORY.md
/root/papyrus/mcp-semicon/BOM_REGISTRY.md
/root/papyrus/mcp-semicon/FULL_ANALYSIS.md
/root/papyrus/love-letter/04_inventory_2026-08-14.md
/root/papyrus/love-letter/05_infra_assessment.md
/root/papyrus/GITHUB_REPORT.md · NUMBERS_AUDIT-2026-07-31.md · REPOSITORY_TREE.md · 00-INDEX.md
/root/papyrus/parksy.kr/backup/blogs/{dtslib,musician-park,polyglot14,programmer-park,webtoon-park}/_INVENTORY.md
/root/papyrus/docs/28-repos-reorganization-blueprint.md · 28-repos-homescreen-layout.md
/root/work/_notebook/46-fridge-architecture_Claude.md
/root/work/_notebook/97-s21-solutions-showcase_Claude.md · 97b · 97c · 96
/root/work/_notebook/99-devlog.md §85–86 (28레포 자산 감사/재평가)
/tmp/survey/helena-piano/fridge/{README,01-repo-list,02-parksy-audio-inventory,03-s21-capabilities,04-pipeline-map,05-youtube-catalog}.md
```
