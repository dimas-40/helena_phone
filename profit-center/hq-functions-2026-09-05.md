# 🏛️ 본사(HQ) 기능 전수 추출 — dtslib-papyrus

> 기준일: 2026-09-05 · `_Claude` · profit-center 저장
> 성격: 본사(Headquarters)가 "어떤 기능을 하는 기관으로 설계되어 있는지"를 기능 단위로 분해한 전수 추출.
> 출처: dtslib-papyrus 레포 `hq/`, `docs/`, `maps/`, 루트 BOT·ORG 문서 22종. **추측 금지 — 각 항목에 근거 파일명 표기.**

---

## 1. 본사 조직 구조 (Org Chart)

본사는 두 축(수직: 비즈니스↔인프라, 수평: 턴키 파트너↔직영)의 **십자 구조(Cross Architecture)** 위에 5-Tier로 28레포를 편제한다.

### 1-1. 십자 구조 (수직·수평축)
- **수직축:** 상단=비즈니스(돈·사람·브랜드) → 중앙=HQ(dtslib-papyrus, 모든 것의 원점) → 브리지=phoneparis(철학, WHY) → 하단=인프라(생산→배포 파이프라인)
- **수평축:** 좌=턴키 파트너(박씨가 구조 설계 → 파트너 운영 → 독립) / 우=직영(박씨가 처음부터 끝까지 책임)
- 근거: `docs/DTSLIB_LAUNCHER_ORG_CHART_v2.md` §1 · `maps/launcher_org_chart_whitepaper_v2.md` §1

### 1-2. 5-Tier 편제 (홈화면 런처 = 조직도)
| Tier | 역할 | 구성 | 개수 |
|------|------|------|:---:|
| **T1 HQ** | 그룹 총괄 · SSOT · 헌법 | dtslib-papyrus (홈화면 정중앙 Row3, 이동 금지) | 1 |
| **T2 운영본부** | 프랜차이즈 OS · 물성 HQ · 커머스 HQ · 사내대학 | dtslib-branch / espiritu-tango / gohsy-fashion / eae-univ | 4 |
| **T3 실행** | 방송국3 · 스튜디오3 · 물성2 · 직영점4 | parksy.kr·eae.kr·dtslib.kr / audio·image·OrbitPrompt / hoyadang·gohsy-production / phoneparis·alexandria·buddies·buckley | 12 |
| **T4 브랜치+길드** | 턴키 브랜치5 + 길드1(2단계 복제) | koosy·gohsy·artrew·papafly·justino / namoneygoal(12슬롯) | 6 |
| **T5 인프라** | 생산·배포·지식 | apk-lab·cloud-appstore·termux-bridge·localpc·parksy-logs | 5 |

- 합계: 1+4+12+6+5 = **28 (완전수)**
- 근거: `docs/DTSLIB_LAUNCHER_ORG_CHART_v2.md` §2·§3 · `maps/launcher_org_chart_whitepaper_v2.md` §3·§6

### 1-3. 5층 건물 은유 (허세 중심, Phase A 시점)
B1 엔진룸(Parksy Capture·로그·RAG) → 1F 쇼룸(공개 플렉스) → 2F 마법사의 작업실 → 3F 대학(레포/앱 파싱) → 4F 방송국(강의 템플릿·인터랙티브). 근거: `hq/BUSINESS-PLAN-2026-02.md` §2

### 1-4. 본사/지사/직영/길드 계정·권한 구조
- **본사 계정:** dtslib1979(👑 OWNER, 28레포) · dimas-40(구 계정, 전 레포 push). 근거: `hq/CONTACTS.md`
- **레이블 체계:** 👑OWNER / 👤FAMILY(누나) / 🐷FIELD / 🎓TEACHER / 🔬RESEARCH(강박사·권박사) / 🧑‍🤝‍🧑FRIEND / 🥖BAKERY / ⏳PENDING / 💧DROPPED / 👀FOLLOW. 근거: `hq/CONTACTS.md`
- **티스토리 계정단위 본사/지사:** dtslib1k=본사그룹(HQ+직영점4) / dtslib2k=지사그룹(브랜치5). 근거: `hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md` §2

---

## 2. 본사 기능 분해 (기능 단위)

본사가 수행하는 기능을 아래 9개 기능군으로 분해한다. 각 기능에 근거 파일명 명시.

### 2-1. 기획 (Planning) — 비즈니스 모델·가격·타겟 설계
- **정체성 정의:** "글 안 써. 말로 던지고 그걸로 방송해" — 복제 가능한 1인 미디어 OS 이식(OS Transplant). Swagger(연기) vs Structure(구조) 분리.
- **타겟·가격:** 허세 시장 → 한국 내 중국 부자(면자 문화). 이중 가격(정가 300만원, 베타 100만원, 중국 부자 300/500/800만원 티어). 2년 로드맵(Year1 보급형 10명 3천~5천만원, Year2 황제학 1000만원+).
- **서비스 범위:** 포함=fork+세팅+도메인+30분 인수인계+CLAUDE.md. 미포함(지옥문 방지)=사후수정·기능추가·질문응대·유지보수.
- **역할 분담:** 우의정(GPT)=전략·메시지 / 좌의정(Claude)=실행·코드 / 왕(박씨)=최종결정. 동선이=생산 플러그인(리더·기획·클라이언트 접점 금지).
- 근거: `hq/BUSINESS-PLAN-2026-02.md` (전문)

### 2-2. 운영 (Operations) — 30일 거래 1사이클 완주
- **목표:** 30일 내 '문의→견적→거래' 1사이클 완주(금액 무관, 0건이면 메시지/타겟/상품 수정).
- **MVP:** hoyadang.com = 방송국 1호점(YouTube Kit + MSMR). 가격 50만원(협상 30, 최저 20).
- **Phase 로드맵:** A(생존전환, 거래1건) → B(대체불가화, 반복포맷3) → C(지위확정, 선택권).
- **DM 응대 문구·쇼츠 스크립트 고정.**
- 근거: `hq/OPERATIONS.md` (SSOT)

### 2-3. 레포 전략 (Repo Strategy) — 25레포 상태 분류
- **상태 분류:** ACTIVE 6 / STANDBY 8 / FROZEN 11(브랜치5·미디어3·기타3). 30일간 FROZEN 손 안 댐.
- **원칙:** "새로 만들지 않는다. 있는 거 연결한다."
- **SSOT 위치:** dtslib-papyrus = 작전본부(OPERATIONS.md, 00_TRUTH/immutable, CLAUDE.md).
- 근거: `hq/REPO-STRATEGY.md`

### 2-4. 채널 매칭 (Channel Matching) — 방송국↔YouTube 계정·채널 1:1
- **계정 3개:** A(Thomas)=개인/교육/코어 · B(dtslib1979)=경제/비즈니스 · C(dimas)=페르소나/실험.
- **매칭:** EAE Univ.+@BeingEduartEngineer-4 → eae.kr(eae-blueprint)+eae-univ(관리) / dtslib → dtslib.kr / 5 페르소나 채널 → parksy.kr/category/.
- **5-Layer 퍼널:** L0 YouTube 8채널(찌라시) → L1 parksy.kr(개체) → L2 eae.kr(정체성) → L3 dtslib.kr(회사) → L4 eae-univ(내부 성소).
- 근거: `hq/YOUTUBE-CHANNEL-MATCHING.md` · `hq/YOUTUBE-BROADCAST-INTEGRATION-PLAN.md`

### 2-5. 업로드 게이트 (Upload Gate) — 내부 자동화/외부 수작업
- **원칙:** 자동 업로드 의도적 비사용. 내부(레포·PWA·Draft JSON)는 자동화 OK, 외부(YouTube Public 업로드·채널홈 노출·메타데이터·공개 버튼)는 **사람만** 통과.
- **구현체:** Draft Injection(생성 자동 → RustDesk/PC 수작업 전달 → YouTube Studio 반자동 → 사람이 공개 결정). safety_lock=true.
- **8채널 최소 단위:** dtslib 1 / EAE Univ 1 / 페르소나 5 / @BeingEduartEngineer-4 1.
- 근거: `hq/YOUTUBE-UPLOAD-GATE-POLICY.md` · `hq/VIDEO-CLASSIFICATION-CRITERIA.md`

### 2-6. 티스토리 매핑 (Tistory Mapping) — 10유닛→16레포 1:1
- **2티어 단순화:** HQ 1 + 브랜치 9 = 정확히 10 = 티스토리 블로그 10(dtslib1k 5 + dtslib2k 5).
- **3단 매핑:** T1 repo↔채널 1:1(`channel-repo-map.json`) / T2 블로그↔카카오계정 1:1 / T3 티스토리세계↔유튜브세계(계정 단위).
- **16레포 전수 확정(v3):** 나머지 6레포(dtslib.kr·gohsy-fashion·gohsy-production·hoyadang·namoneygoal·termux-bridge) → dtslib1k.tistory.com(HQ 공동관리) 귀속.
- 근거: `hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md`

### 2-7. 회계·데이터 철학 (Data/Accounting) — 엑셀 = 렌더 모드
- **한 문장:** "엑셀은 소프트웨어가 아니라 포맷. 포맷은 쓰고 앱은 안 쓴다."
- **구조 분리:** 데이터=CSV/git, 연산=파이썬(읽힘·이력), 엑셀=렌더 모드 하나, 사람=결과만 받음.
- **로데이터 2종:** 재조회 가능(보관 안 함) vs 배타적(본인 매출·거래, 이것만 관리). LLM 가짜 데이터는 만들지도 보관하지도 않음.
- **계정 권한 명부(회계 원장):** GitHub 계정→실명→역할→권한 관계도 마스터 매트릭스(12계정).
- 근거: `hq/EXCEL-PHILOSOPHY-2026-08-23.md` · `hq/CONTACTS.md`

### 2-8. 증거 관리 (Evidence Management) — 검증 가능한 개발 기록
- **성격:** 계획이 아닌 "실행/부분실행된 시스템만" 기록. 측정법 명시(git rev-list, find+wc).
- **지표:** 30레포(33디렉-3중복) · 4,731커밋 · 31 CLAUDE.md · 33 00_TRUTH · 72 GitHub Actions · ~185,000+ LOC.
- **3분류:** Implemented(검증) / Partially Implemented(코드 있음, 파이프 미검증) / Not Claimed(상용 APK·수익·완전자동화 등 미주장).
- **구속→결정 인과표:** PC없음→모바일퍼스트, 편집시간없음→PWA칠판, 1인→프랜차이즈, 예산없음→자체앱 등.
- 근거: `hq/EVIDENCE-WHITEPAPER-2026-02.md`

### 2-9. 개발 철학·카테고리 락 (Dev Philosophy / Category Lock)
- **5카테고리(변경금지, 확장만):** PHL(철학/언어) / Audio / Visual / Action / Infra. 어디에도 안 맞으면 **개발하지 않음**.
- **개발자 유형:** Orchestrator/Systems Integrator/Toolsmith — "기능 만드는 개발자가 아니라 시스템을 반복 생산하는 사람."
- **역제안 시스템:** AI는 모든 태스크 자동 카테고리 판정. 허용 내용=카테고리 판정/Now·Defer·Discard/사유/시점. 금지="이거 꼭 만들어"·감정적 밀어붙임.
- **메모리 락:** ~/CLAUDE.md + MEMORY.md에 락 상주, 어떤 레포 세션이든 1턴부터 판정 유지.
- 근거: `hq/DEV-PHILOSOPHY-CATEGORY-LOCK.md`

### 2-10. 연락처·권한 관리 (Contacts / Access Control)
- **레이블 10종** + 권한 관계도(소유자→27레포 push 위임 그래프) + 마스터 매트릭스(12계정 상태).
- **핵심 권한:** dimas-40=동일인 전 레포 push, 누나=전 레포 push, 박사2=27레포 초대(수락 대기), 동선이=4레포, 드랍 1(gohsy-fashion).
- 근거: `hq/CONTACTS.md`

### 2-11. 시즌1 운영 (Season 1 Planning — Φ7-I-C-K-P-7AXIS)
- **7레포 전수:** 2,818커밋 · 11 MCP server.py. **4대 레포 할당:** L1 OrbitPrompt(철학) → L2 eae-univ(출판) → L3 eae.kr(방송) → L4 phoneparis(비즈니스). 쿼터 190K, 117편/일.
- **PD 분담:** 박씨=데스크, Claude PD=실행 두뇌(철학·출판), DeepSeek PD=손(업로드·pending/·upload.cjs·MCP).
- **언어 정책:** 시즌1 전면 한국어(472/518 = 91%), 46개 영어 페이지 전환 대상.
- 근거: `hq/config/s1-kickoff-report.md` · `hq/config/s1-season-plan.md` · `hq/config/season1-lang-audit.md`

---

## 3. 봇 조직 (BOT Department) — 본사가 운용하는 봇·에이전트 편제

### 3-1. 설계 원리
- **인지과학 근거:** Miller's Law(7±2 청크) → 9봇 = 28레포 관리 최적 구간. Dunbar's Number, Hick's Law 부가.
- **봇의 성격 전환:** "알림 도구" → **부서 진행자(Facilitator)** — 매일 스탠드업, 커밋 요약, 배치 보고, 메시지 라우팅, 장애 알림+복구 지시.
- **조직도 원칙:** "리포팅 라인이 조직보다 우선" — 레포 소속은 '누가 그 보고를 받는가'로 결정.
- 근거: `BOT_DEPARTMENT_DESIGN.md` · `BOT_STANDUP_ARCHITECTURE.md` · `ORG_BOT_MAP_FINAL.md`

### 3-2. 9부서봇 편제
| # | 부서 | 봇 | 담당 레포 |
|---|------|-----|----------|
| 1 | 🎵 Audio | @Parksy_Audio_Claude_bot | parksy-audio · parksy-diffsinger |
| 2 | 📡 Broadcast | @parksy_bridges_bot | 전체 28레포 알림·CI/CD |
| 3 | 🎨 Image | @parksy_bridge_bot(공유) | parksy-image |
| 4 | 🏛️ Papyrus 본사 | @dtslib_papyrus_book_bot | dtslib-papyrus · parksy-logs · parksy.kr |
| 5 | 🏢 Branch 지사 | @dtslib_branch_book_bot | dtslib-branch · hoyadang · philosopher-parksy · OrbitPrompt |
| 6 | 🎓 Edu 교육 | @eae_univ_book_bot | eae-univ · eae.kr · academy-master |
| 7 | 👗 Fashion | @gohsy_fashion_book_bot | gohsy · gohsy-fashion · gohsy-production |
| 8 | 🔧 Infra | @termius_check_bot | dtslib-apk-lab · dtslib-localpc · termux-bridge |
| 9 | 📱 Mobile | @phoneconfcall_bot | phoneparis · helena_phone · helena-metalcare · helana_log |

- **봇-레포 매핑(2버전 존재):** `BOT_REPO_FINAL_MAP.md`(9부서봇, Edu가 5레포=univ·eae·academy·logs·Orbit) vs `ORG_BOT_MAP_FINAL.md`(리포팅라인 기준, Branch가 13레포, Edu가 logs 포함). 차이는 소유권(친구 턴키=Branch) vs 기능(지식=에듀) 기준.
- 근거: `BOT_REPO_FINAL_MAP.md` · `BOT_REPO_MAP.md` · `ORG_BOT_MAP_FINAL.md`

### 3-3. 미구현 부분 (정직 표기)
- 부서별 Telegram 그룹 생성, 봇 초대, 스탠드업 자동 스크립트, 커밋→봇 요약, 주간 리포트 — **전부 미구현(박씨 수동 대기)**.
- 근거: `BOT_STANDUP_ARCHITECTURE.md` §구현상태

---

## 4. 핵심 정책·게이트 (실제 규칙 명시)

### 4-1. 업로드 게이트 (Human Gate) — 가장 강한 게이트
```
[내부 — 자동화 OK]      [외부 — 수작업 ONLY]
레포 생성                YouTube Public 업로드
PWA 칠판 생성            채널홈 노출 결정
Draft JSON 생성          메타데이터 최종 확인
Unlisted 소재 관리        공개 버튼 클릭
        └──── Human Gate ────┘
```
근거: `hq/YOUTUBE-UPLOAD-GATE-POLICY.md`

### 4-2. 영상 공개 3단 분류 규칙
| 설정 | 조건 | PWA 재생 | 채널홈 | 알림 |
|------|------|:---:|:---:|:---:|
| Public | 완성물+외부노출 | O | O | O |
| Unlisted | 소재/부품/임베드 | O | X | X |
| Private | **사용 금지** | **X** | X | X |

- 판단 플로차트: 완성물? → 외부 노출 OK? → 채널홈 노출? (Private는 선택지 없음).
- 전환 규칙: Public→Private 금지(Unlisted로만 내림). Unlisted→Public 허용.
- 방송국별 기본값: parksy.kr=Public 위주 / eae.kr=Unlisted 위주 / dtslib.kr=Public 위주.
- 근거: `hq/VIDEO-CLASSIFICATION-CRITERIA.md`

### 4-3. 개발 금지 규칙 (Category Lock)
- 5카테고리 밖 → 개발 금지. "재밌어 보임/남들 함/증거 없는 개념" → 금지(문서만).
- AI는 카테고리 자동 판정 + 역제안은 명시 요청 시에만.
- 근거: `hq/DEV-PHILOSOPHY-CATEGORY-LOCK.md`

### 4-4. 운영 금지사항 (공통 7+항목)
- 새 레포 생성 금지 · 새 기능 추가 금지 · 설명/튜토리얼 콘텐츠 금지 · 맞춤 개발 약속 금지 · 장기 유지보수 계약 금지 · 가격 경쟁 금지 · 사후관리(지옥문) 금지 · FROZEN 레포 터치 금지.
- 근거: `hq/BUSINESS-PLAN-2026-02.md` §11 · `hq/OPERATIONS.md` · `hq/REPO-STRATEGY.md`

### 4-5. 시즌1 업로드 파이프라인 (PD 실행 프로토콜)
```
LLM 발화 추출 → TTS(박씨 음성) → FFmpeg 합성 → Draft JSON(pending/)
→ node upload.cjs {account} {ts}.json (privacy: private)
→ done/ 이동 → 텔레그램 보고 → 박씨 OK → YouTube Studio 공개 전환
```
- 업로드 기본값: `privacy: private` (Human Gate).
- 근거: `hq/config/s1-season-plan.md` §7 · `hq/config/s1-kickoff-report.md` §5

### 4-6. 디스트리뷰터 MCP (본사 자동화 계층)
- **parksy-distributor** 11툴: telegram(텍스트·사진)·youtube(MP4, private)·naver·tistory·discord·all(4채널 라우터)·status·list_channels·refresh_tokens.
- **OrbitPrompt MCP 8개:** 철학카운터·달러시스템·파이낸스·정치·ID-MANIFEST·브랜치철학·단말기조건·철학B2B.
- 근거: `hq/config/s1-season-plan.md` §2

---

## 5. 본사 기능 → 파일 매핑 요약

| 기능군 | 근거 파일 |
|--------|----------|
| 기획(비즈니스 모델·가격·타겟) | `hq/BUSINESS-PLAN-2026-02.md` |
| 운영(30일 1사이클) | `hq/OPERATIONS.md` |
| 레포 전략(ACTIVE/STANDBY/FROZEN) | `hq/REPO-STRATEGY.md` |
| 채널 매칭(방송국↔유튜브) | `hq/YOUTUBE-CHANNEL-MATCHING.md` · `hq/YOUTUBE-BROADCAST-INTEGRATION-PLAN.md` |
| 업로드 게이트 | `hq/YOUTUBE-UPLOAD-GATE-POLICY.md` · `hq/VIDEO-CLASSIFICATION-CRITERIA.md` |
| 티스토리 매핑 | `hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md` |
| 회계·데이터 철학 | `hq/EXCEL-PHILOSOPHY-2026-08-23.md` · `hq/CONTACTS.md` |
| 증거 관리 | `hq/EVIDENCE-WHITEPAPER-2026-02.md` |
| 개발 철학·카테고리 락 | `hq/DEV-PHILOSOPHY-CATEGORY-LOCK.md` |
| 연락처·권한 | `hq/CONTACTS.md` |
| 시즌1 운영 | `hq/config/s1-kickoff-report.md` · `hq/config/s1-season-plan.md` · `hq/config/season1-lang-audit.md` |
| 봇 부서 편제 | `BOT_DEPARTMENT_DESIGN.md` · `BOT_REPO_FINAL_MAP.md` · `BOT_REPO_MAP.md` · `BOT_STANDUP_ARCHITECTURE.md` · `ORG_BOT_MAP_FINAL.md` |
| 조직도(런처 5-Tier) | `docs/DTSLIB_LAUNCHER_ORG_CHART_v2.md` · `maps/launcher_org_chart_whitepaper_v2.md` |

---

*_Claude · 2026-09-05 · SSOT: dtslib-papyrus(hq/·docs/·maps/·BOT·ORG 문서 22종)*
