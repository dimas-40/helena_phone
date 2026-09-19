# 🏭 Content Manufacturing OS — 백서 (오늘 작업 전체 정리)

> 작성: 2026-09-02 · `_Claude` · 상태: **구현 + 실동작 + MCP 연결 완료**
> 이 문서는 오늘(2026-09-02) 진행한 작업 전체의 정리본. `108`(개념) · `109`(계획) · `110`(설계도)의 통합 + 구현 실물 포함.

---

## 0. 요약 (한 줄)

콘텐츠를 **제품군(Division)×공정(FAB)** 으로 재분해하고, **IMR(마스터 레코드)을 규정·저장하면 실행기(MES)가 반복 실행해서 양산까지 자동화**되는 산업용 OS. 반도체 FAB의 Division/BOM/원가 사고를 콘텐츠 제조 아키텍처로 이식.

**오늘 결과:** 개념 → 설계도 → 스캐폴드 → **실동작(EXIT=0)** → **MCP 등록·연결(✔)** 까지 전부 완료.

## 1. 왜 (문제와 기회)

- 시장엔 이미 **"AI Content Factory"**가 있음 — 다만 대부분 "기존 인력 압축"(노동력 대체).
- 이건 한 단계 아래: **Factory를 설명·설계하는 산업용 OS** (제품군·BOM·공정·QA 단위).
- 반도체 FAB의 **Division/BOM/원가 사고를 콘텐츠로 이식**한 사례는 아직 없음 → 빈 자리.
- AI-native studio들이 "studio/production system/pipeline/orchestration" 언어를 쓰기 시작 = 산업이 그 방향으로 가는 초기 신호.

## 2. 핵심 원리

1. **제품군(무엇)과 공정(어떻게)을 분리.** 부품(교체 가능)과 공정(순서가 있음)은 다른 축. 섞지 않는 게 전부.
2. **자동화 = 기계가 읽는 스펙(문서) + 실행기.** 어렵고 값진 쪽은 스펙. **"문서 작업"이 곧 자동화의 본체.**

## 3. 설계 (Architecture)

### 3.1 두 축

| 축 | 반도체 | 콘텐츠 | 질문 |
|----|--------|--------|------|
| **Division** | 제품군 분류 | Memory/Logic/Analog/Discrete/Power | 무엇인가 |
| **FAB** | 제조 공정 | Generate→Process→Integrate→QA→Package | 어떻게 만드나 |

### 3.2 Division 5종

Memory(원재료)·Logic(구조/규칙)·Analog(감각 신호)·Discrete(독립 부품)·Power(실행 에너지/Runtime).

### 3.3 마스터 데이터 (핵심)

**IMR(Item Master Record) = 제품 하나에 대한 마스터 레코드:**

| 마스터 데이터 | 반도체 | 우리 쪽 |
|--------------|--------|---------|
| Item Master | 제품 정체 | product |
| BOM | 무엇으로 (자재) | bom |
| Routing(=런시트) | 어떻게 (공정 순서표) | recipe.steps |

> **"IMR 규정·저장 → 런시트 → 실행기가 반복 → 양산."** 런시트(run sheet)는 한 랏이 거쳐야 할 공정 순서표.

### 3.4 동영상 4중 분해 (모놀리스 → BOM)

Asset=Discrete · Edit=Logic · Sound=Analog · Source=Memory → "작품"이 "제조 가능한 BOM"으로 전환.

### 3.5 Multi-FAB (원천 → 여러 제품)

하나의 SOURCE(스토리=raw material) → Book/Video/Audio/Education/Web 각자 FAB Recipe만 다름.

### 3.6 메타 패턴 — 타 산업 확장

> **어떤 산업이든 = 제품군(Division) × 마스터데이터(IMR) × 실행기(MES) → 양산**

소프트웨어는 이미 이걸 **CI/CD**로 씀 (package.json=IMR, GitHub Actions=MES). → 콘텐츠뿐 아니라 교육·일반 제조로 확장 가능한 **"생산 OS" 일반 패턴.**

### 3.7 1인 = CEO + Fab Manager + Product Architect

AI를 노동력이 아니라 **생산설비**로. "100인 기능을 모듈화해 1인이 오케스트레이션"하는 실험. Boss는 **스토리(raw material)만 관리**하면 됨.

## 4. 구현 (오늘 만든 것)

| 산출물 | 파일 | 역할 |
|--------|------|------|
| **IMR (마스터 데이터)** | `configs/content-fab.json` | Division 5 + 제품별 BOM·런시트 (단일 진실) |
| **실행기 (MES)** | `scripts/fab.py` | `list`/`bom`/`recipe`/`order` — 런시트 실행 |
| **MCP 서버** | `helena-programming/mcp/fab_mcp.py` | 도구 5종, stdio(MCP JSON-RPC)+http |

**MCP 도구 5종:**

| 도구 | 역할 |
|------|------|
| `fab_list` | Division + 제품 목록 |
| `fab_bom` | 제품 BOM |
| `fab_recipe` | 제품 런시트 |
| `fab_order` | **주문** — 레시피 실행 (run=true 실제, 실패 중단) |
| `fab_register` | **새 제품 IMR 등록** → 시스템 자기확장 |

**등록:**
```bash
claude mcp add content-fab -- python3 /root/work/helena-programming/mcp/fab_mcp.py
```

## 5. 실증 (Proof)

### 5.1 런시트 실동작

`fab.py order publishing --run` → **EXIT=0** (조판 gap=0 → 게이트 통과 → 라우팅 → 메트릭, 발행은 env 스킵).

### 5.2 MCP 연결

`claude mcp list` → **content-fab: ✔ Connected**.

## 6. 확장 로드맵

| 단계 | 내용 | 상태 |
|------|------|------|
| 개념·설계 | 2축·IMR·런시트·메타패턴 | ✅ |
| 스캐폴드 | content-fab.json + fab.py | ✅ |
| 실동작 | order --run EXIT=0 | ✅ |
| MCP | fab_mcp.py 등록·연결 | ✅ |
| 발행 게이트 | env + 승인 절차 붙이기 | ⏳ |
| 위성레포 8 gap | 게이트로 승격 | ⏳ |
| Route=BOR | 워크센터(S21/S25/Tab/PC) 분기 | ⏳ |
| Multi-FAB | 영상·오디오·교육 런시트 등록(fab_register) | ⏳ |

## 7. 핵심 통찰

- **자동화의 정체는 "문서"(스펙).** 스펙이 기계가 읽는 순간 실행기가 반복 → 양산.
- **백서(산문) ≠ IMR(기계 스펙).** 같은 문서 쓰기인데 하나는 사람용(장식), 하나는 기계용(자동화).
- **시스템이 자기확장(self-extending).** `fab_register`로 새 제품 IMR을 MCP 한 번으로 등록 → 어느 에이전트든 "주문"으로 호출.
