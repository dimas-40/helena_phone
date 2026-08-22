# 티스토리 × 엔드프로덕 1:1 매핑 — 비즈니스 세계 10유닛 (2026-08-22)

> **상태:** ✅ **확정** (2026-08-22 — 실제 YouTube 채널 스위처 스크린샷으로 재검증 완료, 미해결 0건)
> **작성:** Claude Code (출판부 · 양산) · _Claude
> **SSOT 출처:** 이 문서 (dtslib-papyrus) + `hq/config/channel-repo-map.json` v2.0 + `automation/TISTORY_25_SLOTS.md` + `hq/youtube-data.json` + `CLAUDE.md` 4060행(@dtslib-branch 채널 링크 9개 정책)

---

## 1. 핵심 전제 — 숫자 정렬 + 2티어 단순화 (Boss 2026-08-22 최종 확정)

> **HQ 1 + 브랜치 9(직영점·브랜치 구분 없이 나머지 전부) = 정확히 10 = 티스토리 블로그 10(dtslib1k 5 + dtslib2k 5).**

초안(직영4/브랜치5)은 실제 유튜브 채널 보유 현황과 안 맞아서(직영점 중 buddies.kr·buckleychang.com은 채널 자체가 없음)
Boss가 **HQ 제외 전부를 "브랜치"로 통합**하는 2티어 구조로 재확정. Tier3/Tier4 공식 분류는 papyrus `CLAUDE.md`
5-Tier 문서에 그대로 남아있고, 이 매핑 문서에서만 단순화해서 쓴다.

---

## 2. 1:1 매핑 테이블 (최종 확정 v2 — 계정 단위 본사/지사 원칙)

> **원칙 전환 (Boss 2026-08-22):** YouTube가 "본사(HQ) 1계정 아래 전 채널"인 것과 대칭시켜,
> 카카오 계정 자체를 본사그룹/지사그룹으로 먼저 가르고, 그 안에서 콘텐츠 적합도로 배정한다.
> **dtslib1k 계정 = 본사그룹**(HQ+직영점4, 회사 직영) · **dtslib2k 계정 = 지사그룹**(브랜치5명, 개인 운영).

### 본사그룹 — dtslib1k@kakao.com

| Unit | 티스토리 URL (글 수) | YouTube | 확신 |
|---|---|---|---|
| **dtslib-branch**(HQ) | [dtslib1k.tistory.com](https://dtslib1k.tistory.com) — 대표/문학 (39) | @dtslib-branch ✅ | 🔒강 |
| **phoneparis** | [hitop.tistory.com](https://hitop.tistory.com) — 과학 (2) | @phoneparis-r6q ✅ | 중 |
| **alexandria** | [lafilosofia.tistory.com](https://lafilosofia.tistory.com) — 철학 (6) | @alexandria-y6k ✅ | 🔒강 (요양원=인생철학) |
| **buckleychang.com** | [midmath.tistory.com](https://midmath.tistory.com) — 수학 (0) | 없음 — @dtslib-branch 경유 | 🔒강 (컨설팅=논리체계) |
| **buddies.kr** | [midsocial.tistory.com](https://midsocial.tistory.com) — 사회 (3) | 없음 — @dtslib-branch 경유 | 🔒강 (소상공인=지역사회) |

### 지사그룹 — dtslib2k@kakao.com

| Unit | 티스토리 URL (글 수) | YouTube | 확신 |
|---|---|---|---|
| **koosy** | [korean-parksy.tistory.com](https://korean-parksy.tistory.com) — 대표 (0) | 없음 — @dtslib-branch 경유 | 중 (최고참 지사=대표 블로그) |
| **gohsy** | [kr-merit-bluff.tistory.com](https://kr-merit-bluff.tistory.com) — 허세교양 (0) | 없음 — @dtslib-branch 경유 | 🔒강 (연예계=허세문화) |
| **artrew** | [kr-merit-shaman.tistory.com](https://kr-merit-shaman.tistory.com) — 샤먼 (0) | @artrew-i1w ✅ | ⚠️약 (예술적 영감=현대판 샤머니즘 재해석) |
| **papafly** | [kr-merit-halfblood.tistory.com](https://kr-merit-halfblood.tistory.com) — 혼종어학 (0) | 없음 — @dtslib-branch 경유 | 🔒강 (K맛×세계입맛 혼종) |
| **abraham**(구justino) | [kr-merit-aggro.tistory.com](https://kr-merit-aggro.tistory.com) — 어그로 (1) | @justino-fashion ✅ | 🔒강 (크리에이터=어그로) |

### 확신 레벨 요약

- 🔒 **강 7:** dtslib-branch↔dtslib1k · alexandria↔lafilosofia(요양원=인생철학) · buckleychang↔midmath(컨설팅=논리) · buddies.kr↔midsocial(소상공인=지역사회) · gohsy↔kr-merit-bluff(연예계=허세문화) · papafly↔kr-merit-halfblood(K맛×세계혼종) · abraham↔kr-merit-aggro(크리에이터=어그로)
- 중 **2:** hitop↔phoneparis(기기=과학) · korean-parksy↔koosy(최고참 지사=대표 블로그)
- ⚠️ **약(승인) 1:** kr-merit-shaman↔artrew — "샤먼"을 미신이 아니라 **예술적 영감/신들림**(창작의 직관적 순간)으로 재해석해서 채택. 글 0개(빈 슬레이트)라 이 서사로 처음부터 채우면 리스크 없음.

> v1(2026-08-22 초판, 직영/브랜치 개별 매칭)에서 koosy↔midmath가 "확정"이었으나,
> 계정단위 본사/지사 원칙 도입(v2)으로 koosy는 지사그룹(dtslib2k)에 속해야 해서 재배정됨 — midmath는 본사그룹으로 이동.

### 채널 미확인 5곳 → **해소됨 (2026-08-22)**

koosy·gohsy·papafly·buddies.kr·buckleychang.com은 "미확인"이 아니라 **원래부터 개별 채널이 없는 게 맞는 상태**였다.
실제 YouTube 계정 채널 스위처 스크린샷(6개: dtslib-branch·espiritu-tango·artrew·phoneparis·alexandria·justino)과
`hq/youtube-data.json`(GOHSY·buddies.kr·PAPAFLY·KOOSY 영상이 실제로 @dtslib-branch 안에 업로드돼 있음 확인) +
`CLAUDE.md` 4060행 정책("램프업 전=@dtslib-branch 통합 업로드, 램프업 후=각자 채널 개설")으로 교차검증 완료.
espiritu-tango는 Tier2 운영본부라 이 10유닛 목록 대상 밖(별도 채널이지만 티스토리 매칭 없음).

---

## 3. 3단 매핑 구조 (2026-08-22 확정)

| 단 | 매핑 | 1:1? | 근거 문서 |
|----|------|------|----------|
| **T1** | GitHub repo ↔ YouTube 채널 | ✅ 1:1 | `hq/config/channel-repo-map.json` v2.0 |
| **T2** | 티스토리 blog ↔ 카카오 계정 | ✅ 1:1 | `tools/tistory/accounts.json` · `automation/TISTORY_25_SLOTS.md` |
| **T3** | 티스토리 세계 ↔ YouTube 세계 | 계정 단위 연계 | 본 문서 §2 · 세션수첩 §6 |

> **핵심:** 블로그↔채널 1:1로 적힌 기존 문서는 없음(전수 확인). 연계 지점은 세계(계정) 단위.
> 이 문서 §2가 **블로그 → 엔드프로덕(레포=채널 1:1, 5곳은 @dtslib-branch 경유) → 세계**를 처음으로 연결한다.

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
