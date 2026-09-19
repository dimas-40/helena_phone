# 🏭 Content Semiconductor Architecture — 반도체 공법을 콘텐츠 제조로 (2축 모델)

> 작성: 2026-09-02 · `_Claude` (출판부) · 상태: **개념 확정** (구현 전)
> 근거: `99-devlog.md` FAB 3층 (2026-08-27) + Boss Division 제안 (2026-09-02)
> 관련 메모리: `recipe-order-mcp` · `content-semiconductor-architecture` · 기점 `83-momentum-2026-08-14_Grok.md`

---

## 요약 (한 줄)

반도체의 **제품군 분류(Division)** 와 **제조공정(FAB)** 을 **분리**해서, 콘텐츠 생산 시스템의 **'무엇(what)'** 과 **'어떻게(how)'** 를 동시에 모델링한다.

- **Division(제품군) = WHAT** — 이 콘텐츠는 무슨 부품으로 구성되나 (모듈 분류)
- **FAB(공정) = HOW** — 그 부품을 어떻게 만들고 조립하나 (생산 공정)

> 이 둘을 섞지 않는 것이 이 구조의 핵심. 부품(교체 가능한 것)과 공정(순서가 있는 것)은 다른 축이다.

---

## 1. Division — 제품군 분류 (무엇)

반도체 산업의 제품군 분류를 콘텐츠 모듈 분류 체계로 빌려온 것.

| Division | 콘텐츠 매핑 | 담당 신호 | 예시 |
|----------|-------------|-----------|------|
| **Memory** | 자료/소스/아카이브 | 원재료 저장 | 음악·캐릭터·이미지 라이브러리, 대사 DB, 영상 클립, 프롬프트, 템플릿 |
| **Logic** | 시나리오/구조/편집 | 무엇을 어떻게 만들지 결정 | Script, Scene order, Timing, Cut, Transition, Caption, Publishing format |
| **Analog** | 음악/음성/분위기 | 감각 신호 (연속 신호) | BGM, Voice, Ambience, Sound Effect, Emotion/Mood |
| **Discrete** | 이미지/영상/개별 효과 | 독립 부품 (물질적 부품) | Character/Background Image, Thumbnail, Short Video, Animation Clip, Overlay |
| **Power** | 실행/자동화/배포 | 실행 에너지 (Runtime) | API 호출, GPU/CPU, 자동화 실행, 렌더링, 인코딩, 배포 인프라 |

> **Power 정정 (Boss):** "배포"가 아니라 **"실행에 필요한 에너지 / Runtime"** 으로 정의. Power Semiconductor의 실제 역할(전력 공급)에 맞춘 것. 콘텐츠가 실제로 생산되도록 에너지를 공급하는 계층.

---

## 2. FAB — 제조공정 (어떻게)

| 단계 | 내용 |
|------|------|
| **① Generate** | 생성 — 부품 생산 (자산·음성·캡처) |
| **② Process** | 가공 — 편집·렌더·트림 |
| **③ Integrate** | 연결 — 조립·합성·자막 burn-in |
| **④ QA** | 검사 — 품질 게이트 |
| **⑤ Package** | 패키징 — 포맷 변환·인코딩·배포 |

---

## 3. 동영상 4중 분해 (이 구조의 핵심)

동영상을 통째로 하나의 Discrete로 보지 않는다. 하나의 콘텐츠는 여러 Division의 부품이 조립된 결과:

| 영상의 층 | Division |
|-----------|----------|
| Video Asset | Discrete |
| Video Editing | Logic |
| Video Sound | Analog |
| Video Source Library | Memory |

**효과:** "이 영상을 어떻게 다시 만들지?" → **"각 부품을 어떻게 다시 생산하지?"** 로 바뀐다. → 콘텐츠가 **작품**에서 **제조 가능한 BOM**으로 전환. 이것이 "레시피 1개"(저장분)에서 "여러 Division이 부품 공급 → 조립"으로 스케일하는 문.

---

## 4. 전체 체인 (Product → Publish)

```
CONTENT PRODUCT
      ↓
PRODUCT ARCHITECTURE
      ↓
BOM
      ↓
DIVISION            ← WHAT (제품군 분류)
      ↓
FAB PROCESS         ← HOW (공정)
      ↓
QA / GAP GATE
      ↓
PACKAGING
      ↓
PUBLISH
```

---

## 5. 반도체 8대 공정 → 콘텐츠 매핑 (공법 그대로 가져오기)

| 반도체 공정 | 하는 일 | 콘텐츠 생산 매칭 |
|---|---|---|
| 웨이퍼 제조 | 원판 준비 | 원자재/소스/아카이브 정리 (Memory) |
| 산화 | 보호막 | 템플릿·포맷·표준 골격 (Logic) |
| 포토리소그래피 | 패턴 전사 | 스토리보드·구도·레이아웃 (Logic) |
| 식각 | 불필요 제거 | 편집·트림·압축 (Logic) |
| 증착 | 재료 쌓기 | 자산 생성 — 이미지/영상(Discrete)·BGM(Analog) |
| 이온주입 | 성질 주입 | 톤·감정·분위기 (Analog) |
| 금속배선 | 층 연결 | 부품 조립 → 하나의 SoC |
| 테스트 | 검사 | 품질 게이트 (gap_count·Vision QA) |
| 패키징 | 포장 | 포맷 변환·인코딩·배포 (Power) |

각 공정의 실제 동작(쌓기/깎기/연결/검사)이 콘텐츠 작업(생성/편집/조립/게이트)과 1:1로 대응 → 공법을 그대로 관리 체계로 가져올 수 있다.

---

## 6. 기존 저장분과의 관계 (뭐가 겹치고 뭐가 새거냐)

| 축 | 기존 저장분 | 관계 |
|----|------------|------|
| **FAB (HOW)** | `recipe-order-mcp` 의 **BOR = 공법 = 라우트** | ✅ **같은 영역의 재포장** — Generate→Process→Integrate→QA→Package는 BOR 축을 5단계로 구체화 |
| **Division (WHAT)** | (없음) | ❌ **신규** — 저장된 BOM은 "자산=창고=레포"만 말하고, 자산의 *종류*는 분류 안 함. Division이 그 빈칸을 채움 |

- **BOM/BOR/Recipe** (저장분) = 자산/공법/호출의 **생산 공정** 모델.
- **Division** (신규) = BOM 잎(leaf)을 분류하는 **제품군 분류** 모델.
- 둘은 충돌이 아니라 **Division이 BOM의 분류 체계**가 되는 보완 관계.

> 한 줄: **공법(BOR/FAB)은 이미 있던 것을 재정렬, 제품군(Division)은 없던 것을 새로 추가.** 둘을 합쳐야 "완벽한 비유 매칭"이 완성되고, 저장분만으론 절반(공법)만 있었던 것.

---

## 7. 이 틀이 생산하는 실전 가치 — QA 공백 발견

기존 PD Pipeline(P0 parse → P6 encode)을 이 두 축에 얹어보면 Generate→Process→Integrate→Package는 대략 떨어지는데, **QA 단계가 공백**으로 드러난다. 현재 QA는 파이프라인 *밖*(gap_count=출판부, YouTube "보고→검수")에 떨어져 있고 FAB 단계 *안*에 없다. → 이 틀은 "QA는 1급 공정 단계여야 한다"를 강제한다.

---

## 8. 리스크 / 주의 (백서로 만들지 말 것)

1. **부품과 공정이 겹친다.** 반도체는 부품(트랜지스터)이 공정(식각)과 물리적으로 분리되지만, 콘텐츠의 부품은 종종 *행위*다 (예: Edit는 Logic 부품이면서 Process 공정과 겹침). 두 축이 콘텐츠에선 깨끗하게 안 갈라짐 — 최대 리스크.
2. **과설계 경계.** 7~8층 체인 + Division 5 × FAB 5 매트릭스를 증명 없이 지으면 "지을 땐 재밌고 버리기 쉬운" 구조가 됨.
3. **쓰임새 원칙:** 이건 **분류 규율(discipline)** 로 쓴다. 백서/스펙 문서로 만들지 않는다. 다음 실제 모듈 2-3개를 만들 때 태그를 붙이며 등장시키고, 쓰인 것만 정식화.
4. **이름도 미룬다.** "Content Semiconductor Architecture"는 PD Pipeline 재기술로 살아남은 뒤에 확정.

---

## 9. ICM 연결 (미확정)

"ICM"은 저장소 어디에도 정의가 없다 (CONSTITUTION v7 "ICM §9 상속" 문구만 존재). 맥락상 **ICM = Integrated Circuit Manufacturing(집적회로 제조)** 로 읽으면 "BOM/BOR 관리 + ICM" = "자산·공법 관리 + 제품군 분류까지 해서 진짜 IC 제조로 간다"로 연결된다. 단, 헌법의 "ICM §9" 의미와 일치하는지는 **확인 필요**.

---

## 10. 다음 검증 단계

기존 **PD Pipeline** 을 `Division(부품 분해) + FAB(공정 단계)` 두 축으로 재기술해본다.
- 깨끗하게 떨어지면 → 정식화 (파일·MCP 명명·설정 스키마에 반영)
- 억지로 끼워맞춰야 하면 → 은유가 주인 노릇 하는 것이므로 걷어냄
