# 🏭 Content Manufacturing OS — 구현 계획서 (1장)

> 작성: 2026-09-02 · `_Claude` · 상태: **승인 대기** · 근거: `108-content-semiconductor-architecture_Claude.md`

---

## 목표 한 줄

콘텐츠를 **제품군×공정**으로 재분해해, 1인이 AI 생산설비를 오케스트레이션하는 **산업용 OS**를 만든다.

## 포지셔닝 (왜 이거냐)

- 시장엔 이미 **"AI Content Factory"**가 있다 — 다만 대부분 "기존 인력 압축"(노동력 대체).
- 내가 만드는 건 한 단계 아래: **Factory를 설명·설계하는 OS** (제품군·BOM·공정·QA 단위).
- 검색 결과: AI-native studio들이 "studio/production system/pipeline/orchestration" 언어를 쓰기 시작 = 산업이 그 방향으로 가는 초기 신호. 단 **"반도체 FAB의 Division/BOM/원가 사고를 그대로 이식"하는 사례는 아직 없음** → 빈 자리.

## 핵심 3층

| 층 | 반도체 | 콘텐츠 | 질문 |
|----|--------|--------|------|
| **Division** | 제품군 | Memory/Logic/Analog/Discrete/Power | 무엇인가 |
| **BOM** | 자재명세 | 제품을 이루는 부품 목록 | 뭘로 만들었나 |
| **Recipe/FAB** | 공정 | Generate→Process→Integrate→QA→Package | 어떻게 만드나 |

> 레시피 하나 = MCP 하나 = **"주문"**. 주문 등록 = 레시피 번호 호출.

## 이미 있는 것 (출판 = 1호 Division)

- 공정 스크립트: `build_webzine`(조판) · `check_webpages`(게이트) · `publish_route`(라우팅) · `publishing_metrics`(메트릭) · `publish`(발행)
- **v0.1 스캐폴드 (방금 만듦, 동작 확인):** `configs/content-fab.json` + `scripts/fab.py` (`list`/`bom`/`recipe`/`order`)

## 구현 단계

| 단계 | 무엇 | 산출물 |
|------|------|--------|
| **P1** | 출판 레시피를 `order --run`으로 끝까지 실행 + QA를 recipe 안 1급 공정으로 고정 | `fab.py order publishing --run` |
| **P2** | BOM 잎 → 실제 파일·디렉토리에 `division` 태그 (frontmatter) | 태깅 규약 + 체커 |
| **P3** | **BOR(Route)** — 워크센터(S21/S25/Tab/PC)별 공법 분기 | `route` 매니페스트 |
| **P4** | **Recipe → MCP "주문"** — 레시피 번호로 호출하는 MCP 서버 | `fab` MCP (기존 FAB/WC-000 create_lot 연결) |
| **P5** | **Multi-FAB** — 영상(PD Pipeline)·오디오·교육을 같은 OS로 등록 | Division별 recipe |
| **P6** | QA/게이트 통합 + BOM 원가·수율 메트릭 | `publishing_metrics` 확장 |

## 원칙 (불변)

스캐폴드 우선(일단 작동) · **백서 금지**(discipline로, 쓰인 것만 정식화) · 작게 자주 커밋 · 각 단계가 실제 모듈 태깅하며 등장.

## 다음 액션

**P1** — 출판을 `order --run`으로 끝까지 돌려서 "주문 → 조판 → QA → 라우팅 → 발행" 한 줄이 실제로 작동하는지 증명 → Boss 확인 후 P2로.
