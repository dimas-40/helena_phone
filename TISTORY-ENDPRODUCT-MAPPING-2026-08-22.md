# 티스토리 × 엔드프로덕 1:1 매핑 — 비즈니스 세계 10유닛 (2026-08-22)

> **상태:** Boss 확정 초안 (koosy↔midmath 확정 · 2강 · 5중 · 1약 — §2 참조)
> **작성:** Claude Code (출판부 · 양산) · _Claude
> **SSOT 출처:** 이 문서 (dtslib-papyrus) + `hq/config/channel-repo-map.json` v2.0 + `automation/TISTORY_25_SLOTS.md` + `configs/ecosystem.json.template`

---

## 1. 핵심 전제 — 숫자 정렬 (Boss 2026-08-22)

> **HQ 1 + 직영점(Tier3) 4 + 브랜치(Tier4) 5 = 정확히 10 = 티스토리 블로그 10(dtslib1k 5 + dtslib2k 5).**

기존 개념(교수법/국가특성 "모듈")에서 티스토리 블로그 10개를 떼어내,
**엔드프로덕 단위 10곳에 1:1 재배치**한다. 각 블로그 = 해당 유닛의 SEO·텍스트 코퍼스 목소리.

티어 구조 SSOT: papyrus `CLAUDE.md` (Tier 3 직영점 4 · Tier 4 브랜치 5 · Tier 2 운영본부 중 dtslib-branch = HQ).

---

## 2. 1:1 매핑 테이블

| # | Unit | Tier | 역할 (SSOT) | YouTube 채널 | 블로그 | 확신 |
|---|------|------|-------------|--------------|--------|------|
| 1 | **dtslib-branch** | HQ | 프랜차이즈 OS · 서사 허브 (경제방송 dtslib.kr) | @dtslib-branch | **dtslib1k** (중년고딩문학) | 🔒 강 |
| 2 | **phoneparis** | 직영 | 모바일 유통 · 세팅 (phoneparis.kr) | @phoneparis-r6q | **hitop** (중년고딩과학) | 중 |
| 3 | **alexandria-sanctuary** | 직영 | 신개념 요양원 | @alexandria-y6k | **midsocial** (중년고딩사회) | 🔒 강 |
| 4 | **buddies.kr** | 직영 | 소기업 인스톨레이션 (buddies.kr) | ❓ 미확인 | **kr-merit-shaman** | ⚠️ 약 |
| 5 | **buckleychang.com** | 직영 | 1인회사 컨설팅 (buckleychang.com) | ❓ 미확인 | **korean-parksy** (대표) | 중 |
| 6 | **koosy** | 브랜치 | 수학과외 · AI 천재소년 | ❓ 미확인 | **midmath** (중년고딩수학) | ✅ **확정** |
| 7 | **gohsy** | 브랜치 | 배우/PD 에이전트 | ❓ 미확인 | **kr-merit-bluff** (허세교양) | 중 |
| 8 | **artrew** | 브랜치 | AI 미대생 육성 (artrew.com) | @artrew-i1w | **lafilosofia** (중년고딩철학) | 중 |
| 9 | **papafly** | 브랜치 | K-도넛 글로벌화 | ❓ 미확인 | **kr-merit-halfblood** (하프블러드 어학) | 중 |
| 10 | **abraham** | 브랜치 | 족발집 실운영 · 크리에이터 (구 justino) | @justino-fashion | **kr-merit-aggro** (편집강박 어그로) | 중 |

### 확신 레벨

- ✅ **확정 1:** koosy ↔ midmath (Boss 지정 · 내용상 수학과외=수학)
- 🔒 **강 2:** dtslib-branch↔dtslib1k (HQ=서사·문학=비즈니스 소설) · alexandria↔midsocial (요양원=노년 사회복지 도메인)
- 중 **5:** hitop↔phoneparis(기기=과학) · korean-parksy↔buckleychang(컨설팅=대표 자문) · kr-merit-bluff↔gohsy(연예계 허세문화) · lafilosofia↔artrew(미학=철학 분과) · kr-merit-halfblood↔papafly(K-맛×세계입맛 혼종)
- ⚠️ **약 1:** kr-merit-shaman↔buddies.kr (소상공인×샤먼 — 가장 느슨, **Boss 확정 필요**)

### 채널 미확인 5곳

buddies.kr · buckleychang.com · koosy · gohsy · papafly — 현재 YouTube 채널 미확인.
기존 6채널 중 매칭되는 게 있는지, 신규 발급인지 후속 확인 필요. (b 계정 확보 채널: @dtslib-branch · @espiritu-tango · @artrew-i1w · @phoneparis-r6q · @alexandria-y6k · @justino-fashion)

---

## 3. 3단 매핑 구조 (2026-08-22 확정)

| 단 | 매핑 | 1:1? | 근거 문서 |
|----|------|------|----------|
| **T1** | GitHub repo ↔ YouTube 채널 | ✅ 1:1 | `hq/config/channel-repo-map.json` v2.0 |
| **T2** | 티스토리 blog ↔ 카카오 계정 | ✅ 1:1 | `tools/tistory/accounts.json` · `automation/TISTORY_25_SLOTS.md` |
| **T3** | 티스토리 세계 ↔ YouTube 세계 | 계정 단위 연계 | 본 문서 §2 · 세션수첩 §6 |

> **핵심:** 블로그↔채널 1:1로 적힌 기존 문서는 없음(전수 확인). 연계 지점은 세계(계정) 단위.
> 이 문서 §2가 **블로그 → 엔드프로덕(레포=채널 1:1) → 세계**를 처음으로 연결한다.

### 세계 배치 (Boss 재편 확정)

- **폰/b계정 (dtslib1979 · 경제방송):** dtslib1k + dtslib2k 티스토리 10 = 본 문서 대상. **지금 시작.**
- **탭/c계정 (thomas.tj.park · 교육방송):** eae 티스토리 5 — **탭 전용 분리** (이 폰에서 제거). 스튜디오 완성 후 교육방송부터 론칭.
- **a계정 (dimas.thomas.sancho · 아리랑):** dtslib·parksy_kr 티스토리 10 — **맨 마지막.** 쿼터 미승인 + 글래스 로드맵. "한국인이 AI로 이런 걸 만든다" 스토리.

---

## 4. 롤아웃 스토리 (Boss 2026-08-22 확정)

```
폰 (S25, 비즈니스) ── 사람 만나며 대화 ──→ 지금 시작 (경제방송 + 티스토리 10)
탭 (태블릿, 교육)  ── 스튜디오 영상 업데이트 ──→ 그다음 (eae 티스토리 5)
a계정 (아리랑)    ── 한국인×AI 다큐 ─────────→ 맨 마지막 (dtslib·parksy_kr)
```

---

## 5. 참조

- `hq/config/channel-repo-map.json` — repo↔채널 SSOT
- `automation/TISTORY_25_SLOTS.md` — 21슬롯 전수 (blog→계정)
- `tools/tistory/accounts.json` — 카카오 계정 마스터
- `docs/28-repos-reorganization-blueprint.md` §6 — S21 선물 배포 경로 (`gift/*`)
- 폰 세션수첩: `_notebook/session-2026-08-22_quota-channel-map_Claude.md`

*_Claude · 2026-08-22 · SSOT: dtslib-papyrus*
