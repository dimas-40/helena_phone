# 🏭 Content Manufacturing OS — 개념 설계도 (최종 정리본)

> 작성: 2026-09-02 · `_Claude` · 상태: **설계도 확정, 실행 대기**
> 이 문서는 `108`(2축 모델) · `109`(구현 계획)을 하나로 통합한 **정본**. 과거 문서는 이력으로 보존(삭제 안 함).
> 실물: `configs/content-fab.json`(마스터 데이터) + `scripts/fab.py`(실행기) — **`order --run` 실동작 확인됨(EXIT=0).**

---

## 0. 목표 한 줄

콘텐츠를 **제품군×공정**으로 재분해해, 1인이 **스토리(raw material)만 공급하면 런시트가 나머지를 다 만드는** 산업용 OS를 만든다.

## 1. 왜 이거냐 (포지셔닝)

- 시장엔 이미 **"AI Content Factory"**가 있음 — 다만 대부분 "기존 인력 압축"(노동력 대체).
- 이건 한 단계 아래: **Factory를 설명·설계하는 산업용 OS** (제품군·BOM·공정·QA 단위).
- 반도체 FAB의 **Division/BOM/원가 사고를 콘텐츠 제조 아키텍처로 이식**한 사례는 아직 없음 → 빈 자리.

## 2. 핵심 원리 2개

1. **콘텐츠를 제품군(무엇)×공정(어떻게)으로 분리한다.** 부품(교체 가능한 것)과 공정(순서가 있는 것)은 다른 축. 이 둘을 섞지 않는 게 전부.
2. **자동화 = 기계가 읽는 스펙(문서) + 실행기.** 어렵고 값진 쪽은 스펙. 스펙이 있으면 실행기가 반복 → 양산. **"문서 작업"이 곧 자동화의 본체.**

## 3. 두 축

| 축 | 반도체 | 콘텐츠 | 질문 |
|----|--------|--------|------|
| **Division** | 제품군 분류 | Memory/Logic/Analog/Discrete/Power | 무엇인가 |
| **FAB** | 제조 공정 | Generate→Process→Integrate→QA→Package | 어떻게 만드나 |

## 4. Division 5종 (무엇)

| Division | 담당 신호 | 예시 |
|----------|-----------|------|
| **Memory** | 원재료 저장 | 라이브러리·대사 DB·영상 클립·프롬프트·템플릿 |
| **Logic** | 구조/규칙 | Script·Scene order·Timing·Cut·Caption·출판 형식 |
| **Analog** | 감각 신호 | BGM·Voice·Ambience·SFX·Emotion/Mood |
| **Discrete** | 독립 부품 | 캐릭터/배경 이미지·Thumbnail·Short·Animation·Overlay |
| **Power** | 실행 에너지(Runtime) | API·GPU/CPU·자동화·렌더링·인코딩·배포 인프라 |

> **Power 정정:** "배포"가 아니라 "실행 에너지/Runtime" — Power Semiconductor의 실제 역할(전력 공급)에 맞춤.

## 5. FAB 5단계 (어떻게)

| 단계 | 내용 |
|------|------|
| ① Generate | 생성 — 부품 생산 |
| ② Process | 가공 — 편집·렌더·트림 |
| ③ Integrate | 연결 — 조립·합성·burn-in |
| ④ QA | 검사 — 품질 게이트 |
| ⑤ Package | 패키징 — 포맷·인코딩·배포 |

## 6. 반도체 8대 공정 → 콘텐츠 (공법 그대로 이식)

| 반도체 공정 | 콘텐츠 매칭 |
|---|---|
| 웨이퍼 제조 | 원자재/소스 정리 (Memory) |
| 산화 | 템플릿·포맷 골격 (Logic) |
| 포토리소그래피 | 스토리보드·레이아웃 (Logic) |
| 식각 | 편집·트림·압축 (Logic) |
| 증착 | 자산 생성 — 이미지/영상(Discrete)·BGM(Analog) |
| 이온주입 | 톤·감정·분위기 (Analog) |
| 금속배선 | 부품 조립 → 하나의 SoC |
| 테스트 | 품질 게이트 (gap·Vision QA) |
| 패키징 | 포맷·인코딩·배포 (Power) |

## 7. 마스터 데이터 (이게 핵심)

**IMR(Item Master Record) = 제품 하나에 대한 마스터 레코드.** 그 안에 3종이 걸림:

| 마스터 데이터 | 반도체 | 우리 쪽 |
|--------------|--------|---------|
| **Item Master** | 제품 정체·속성 | product 항목 |
| **BOM** | 무엇으로 (자재 명세) | bom |
| **Routing(=런시트)** | 어떻게 (공정 순서표) | recipe.steps |

> **런시트(run sheet) = routing** — 한 랏이 거쳐야 할 공정 순서표. 작업자(MES)가 한 줄씩 따라가면 제품이 나옴.
> **"IMR 규정·저장 → 런시트 → 실행기가 반복 → 양산."** 나머지는 실행기가 읽는 것뿐.

## 8. 동영상 4중 분해 (모놀리스 → BOM)

| 영상의 층 | Division |
|-----------|----------|
| Video Asset | Discrete |
| Video Editing | Logic |
| Video Sound | Analog |
| Video Source Library | Memory |

> "영상을 어떻게 다시 만들지" → **"각 부품을 어떻게 다시 생산하지"**. 작품이 "제조 가능한 BOM"으로 전환 → 이게 스케일의 문.

## 9. Multi-FAB (원천 → 여러 제품)

```
SOURCE (하나의 아이디어 = raw material)
   │
   ├─ Book      → 출판 FAB → eBook/Paper
   ├─ Video     → 영상 FAB → Shorts/YouTube
   ├─ Audio     → 오디오 FAB → Podcast
   ├─ Education → 교육 FAB → 강의/코스
   └─ Web       → 웹 FAB → 앱/인터랙티브
```

**같은 원천, 제품별 FAB Recipe만 다름.** 이게 실제 제조업 사고와 정확히 일치.

## 10. Product Division (콘텐츠 제품군)

Publishing(책·블로그·뉴스레터) · Video(영화·Shorts) · Audio(음악·Podcast·오디오북) · Education(강의·교재) · Interactive(웹·앱) · Game · Social(SNS·카드뉴스) · Live(공연·라이브).

## 11. 실행기 (MES)

`scripts/fab.py` — IMR 읽어서 런시트 순서대로 실행:

```
fab.py list                # 제품군·제품 목록
fab.py bom <product>       # BOM (부품 × Division)
fab.py recipe <product>    # 런시트(공정 순서)
fab.py order <product> --run   # 주문 실행 (순서·env·실패중단 자동)
```

- **order = 주문 = 레시피 호출.** `needs_env` 스텝은 자동 스킵, 실패 시 중단.
- **Route = BOR:** 워크센터(S21/S25/Tab/PC)별로 같은 레시피라도 공법(명령)이 다름 → 라우팅으로 분기.

## 12. 실동작 증명 (출판 = 1호 Division)

`fab.py order publishing --run` 실행 결과:

| 단계 | 결과 |
|------|------|
| ① Generate (build_webzine) | ✅ gap_count=0 |
| ② QA (check_webpages) | ✅ 통과 |
| ③ Route (publish_route) | ✅ 실행 |
| ④ Package (publishing_metrics) | ✅ 실행 (md=149 html=153) |
| ⑤ Publish (발행) | ⏭ env라 스킵 (외부 발행, 승인 필요) |
| **전체** | **EXIT=0** |

## 13. 메타 패턴 — 타 산업으로 확장

이 구조는 콘텐츠 전용이 아니라 **"생산"의 보편 패턴**이다:

> **어떤 산업이든 = 제품군(Division) × 마스터데이터(IMR: 정체+BOM+런시트) × 실행기(MES) → 양산**

| 산업 | BOM | 런시트(FAB) | 실행기 |
|------|-----|-------------|--------|
| **콘텐츠** (현재) | 부품(이미지·BGM·원고) | 조판→게이트→발행 | fab.py |
| **소프트웨어** | 코드 모듈·의존성 | build→test→deploy | CI/CD (이미 이 패턴) |
| **교육** | 커리큘럼·슬라이드·실습 | 설계→제작→검수→LMS | (동일) |
| **일반 제조** | 자재·부품 | 공정→검사→포장 | MES (원래 도메인) |

> **핵심 관찰:** 소프트웨어는 이미 이걸 **CI/CD**라는 이름으로 쓰고 있다 (package.json=IMR, GitHub Actions=MES). 콘텐츠에 그걸 가져오는 것. → 이 설계도는 "콘텐츠 제조 OS"이자, 재사용 가능한 **"생산 OS" 일반 패턴**.

## 14. 1인 = CEO + Fab Manager + Product Architect

과거엔 부서 = 사람(작가·디자이너·편집자·개발). AI 시대엔 부서 = 모듈. **AI를 노동력이 아니라 생산설비로.** "100인 기능을 모듈화해 1인이 오케스트레이션"하는 실험.

## 15. 구현 현황 & 로드맵

| 상태 | 항목 |
|------|------|
| ✅ | 2축 모델·IMR·런시트 개념 확정 (`108`) |
| ✅ | v0.1 스캐폴드 — `content-fab.json` + `fab.py` |
| ✅ | 출판 런시트 실동작 (order --run EXIT=0) |
| ⏳ | 발행 게이트 붙이기 (env + 승인 절차) |
| ⏳ | 위성레포(helena-programming) 8 gap → 게이트로 승격 |
| ⏳ | Route=BOR 워크센터 분기 |
| ⏳ | Recipe → MCP "주문" 서버 |
| ⏳ | Multi-FAB — 영상·오디오·교육 런시트 복제 |

## 16. 원칙 (불변)

스캐폴드 우선(일단 작동) · **백서 금지**(기계가 읽는 스펙만, 산문 금지) · 작게 자주 커밋 · 각 단계가 실제 모듈 태깅하며 등장.
