---
date: 2026-08-22
agent: Claude Code (출판부 · 양산)
mark: _Claude
type: session-note
status: active
related:
  - 02-network.md
  - session-2026-08-22_youtube-oauth_Claude.md
---

# 🗺️ YouTube 쿼터 2계정 → 채널 확정 + 역산 플랫폼 매핑 (_Claude · 2026-08-22)

> **Boss 지시:** "dtslib1979(60k) · thomas.tj.park(60k)에 해당하는 출판 방송 미디어를 각각 구분해서, 주력 폰에서 두 계정의 YouTube 채널을 확정짓고 역산해서 티스토리 등 플랫폼을 깔아야 한다."
> 출처: papyrus `hq/config/channel-repo-map.json` (SSOT v2.0 · 2026-06-09) + `automation/TISTORY_25_SLOTS.md` (2026-03-16 전수 확정) + 이 폰 `tistory-naver/accounts.json`

---

## 1. 쿼터 승인 2계정 → YouTube 채널 확정 (SSOT)

### b — dtslib1979@gmail.com · 경제방송 · 60,000 units/day

| # | 채널 | 레포·도메인 | 상태 |
|---|------|------------|------|
| 1 | **@dtslib-branch** | dtslib-branch · dtslib.kr · buckleychang.com · gohsy.com 외 10 | 60편 (시즌제외) |
| 2 | @espiritu-tango | espiritu-tango | 물성 HQ · 보류 |
| 3 | @artrew-i1w | artrew (artrew.com) | AI 미대생 |
| 4 | @phoneparis-r6q | phoneparis.kr · termux-bridge | 모바일 유통 |
| 5 | @alexandria-y6k | alexandria-sanctuary | 요양원 |
| 6 | @justino-fashion | abraham (dtslib1979.github.io/abraham) | 쇼핑몰 프랜차이즈 |

### c — thomas.tj.park@gmail.com · 교육방송 · 60,000 units/day

| # | 채널 | 레포·도메인 | 상태 |
|---|------|------------|------|
| 1 | **@EAE-University** | eae-univ (dtslib1979.github.io/eae-univ) | 87편 |
| 2 | **@BeingEduartEngineer-4** | eae.kr (www.eae.kr) | 11편 |

> ⚠️ 15CH 레지스트리 구버전에 "@EAE-* → dtslib 계정(?)" 혼동 줄이 있음 — **SSOT(channel-repo-map v2.0) + youtube-data.json 둘 다 EAE = c 계정** 확정. 구버전 대체.

---

## 2. 역산 — 채널 ↔ 티스토리 세계 매핑 (papyrus 21슬롯 · 세계 단위)

| 세계 | Google 계정 | YouTube 채널 | 티스토리 계정 | 티스토리 블로그 | 이 폰 연결 |
|------|------------|--------------|---------------|----------------|-----------|
| **EAE (c)** | thomas.tj.park | 2 (EAE-Univ · BeingEduartEngineer) | eae_kr | **5 (eae-kr·broadcast·music·image·video)** | ❌ **탭 전용** (이 폰서 제거) |
| **dtslib1k (b)** | dtslib1979 | 경제방송 6채널 | dtslib1k | **5 (dtslib1k·hitop·midmath·midsocial·lafilosofia)** | ✅ **연결됨** |
| **dtslib2k (b)** | dtslib1979 | 경제방송 6채널 | dtslib2k | **5 (korean-parksy·kr-merit×4)** | ✅ **연결됨** |
| **dtslib (a·보류)** | dimas.thomas.sancho | KR방송 | dtslib | **5 (polyglot14·dtslib·webtoon-park·programmer-park·musician-park)** | ❌ **아리랑 맨 마지막** |
| **parksy (a·보류)** | dimas.thomas.sancho | KR방송 5채널 | parksy_kr | **5 (parksy 전용)** | ❌ **아리랑 맨 마지막** |

**핵심:** 이 폰(`tistory-naver/accounts.json`)엔 **b 세계 dtslib1k·dtslib2k 10블로그만** 연결돼 있음. eae(교육)는 탭 전용, dtslib·parksy_kr(아리랑)은 a계정 쿼터 미승인 → 맨 마지막 보류.

---

## 3. 갭 + 설치 순서 (Boss 재편 확정)

1. **b 세계 티스토리 (dtslib1k·dtslib2k 10블로그) = 지금** — 쿼터 60k 있는 주 계정 세계. 폰/b계정 비즈니스방송과 연계.
2. **eae (교육방송) = 탭 전용으로 분리** — 이 폰에서 제거. 태블릿 에이전트 담당.
3. **dtslib·parksy_kr (아리랑방송) = 맨 마지막** — a계정 쿼터 미승인 + 글래스 로드맵. 쿼터 확정 후.

**원칙:** 세계(계정)별 미디어 구분 — 채널·블로그·레포가 같은 세계 안에서만 짝. 세계 간 섞지 않음. 티스토리↔유튜브는 **계정 단위 연계** (블로그↔채널 1:1 아님, §6).

---

## 4. 기기×계정×방송 토폴로지 확정 (Boss · 2026-08-22)

| 기기 | 계정 | 방송 | 상태 |
|------|------|------|------|
| **탭(태블릿)** | c (thomas.tj.park) | 교육방송 2채널 + **eae 티스토리 5** | 스튜디오 완성 후 론칭 |
| **폰(S25 Ultra)** | b (dtslib1979) | 경제방송 6채널 + **dtslib1k·dtslib2k 티스토리 10** | **시작 = 여기** (쿼터 60k) |
| a (dimas.thomas.sancho) | KR방송 + dtslib·parksy_kr 티스토리 | 쿼터 미승인 · 기기 미매칭 | 별도 처리 · 맨 마지막 |
| **S21 (proot Ubuntu 2)** | — | 경제방송 **양산 공장 노드** | 매칭 (papyrus: 누나폰 공장·자체 생산) |

- **경제방송 콘텐츠 모델 (Boss):** dtslib-branch(브랜치들)와 함께 스토리 제작 · 그 사람들 도움 · 비즈니스 소설. **이 방송부터 시작.**
- **proot Ubuntu 2 = S21** (papyrus `ecosystem.json.template` devices tier1) — 이 폰(S25)=proot Ubuntu 1. S21 = 경제방송 양산 공장 노드로 매칭.
- 메모리: `device-account-broadcast-topology.md` 저장.

---

## 5. 티스토리 → 비즈니스 방송 연계 — 재편 확정 (Boss · 2026-08-22 2차)

**Boss 1차:** "이 두 가지 계정으로 폰 히스토리 월드(비즈니스 방송)와 연계해야 되지 않냐?"
**Boss 2차 재편:** "eae는 태블릿 전용으로 뺄 거야. 그리고 1k 2k 계정을 비즈니스와 연동해서 다시 재편."

**papyrus `tools/tistory/accounts.json` 마스터 → 이 폰 최종 매핑 (10블로그):**

| 카카오 계정 | 컨셉 | 블로그 (5) | 세계 | 이 폰 |
|------------|------|-----------|------|-------|
| dtslib1k@kakao.com | 📚 대학개론서→고딩언어 | dtslib1k·hitop·midmath·midsocial·lafilosofia | **경제 (폰/b)** | ✅ 연결 |
| dtslib2k@kakao.com | 🏆 KR메리트/한국인특질 | korean-parksy·kr-merit-bluff·kr-merit-halfblood·kr-merit-aggro·kr-merit-shaman | **경제 (폰/b)** | ✅ 연결 |

**제외 (이 폰에서):**
- `eae_kr@kakao.com` (교육방송 5) → **탭 전용** 분리. 태블릿 에이전트 담당.
- `dtslib@kakao.com` (한글 OJT 5) · `parksy_kr@kakao.com` (영문 OJT 5) → **a계정/아리랑방송**, 맨 마지막. 쿼터 미승인과 일치.

**실행:** `tistory-naver/accounts.json` = **dtslib1k·dtslib2k 10블로그** (id=슬러그 유니크, post.py acc_map 요구). 비밀번호 = 기존 공유 (papyrus와 동일). template 동기화 완료.

**구성:** post.py 계정별 로그인(각 email + 공유 pw) ✅ · verify_accounts.py는 accounts[0]만 로그인 → **계정별 실행 필요** (알려진 한계).

---

## 6. 3단 매핑 — GitHub repo ↔ YouTube ↔ Tistory (다대일 수렴 · 2026-08-22 확정)

> **자료 전수 확인:** 블로그↔채널 1:1로 적힌 문서는 아무 데도 없음. (TISTORY_25_SLOTS = blog→카카오계정, channel-repo-map = 채널→레포, distributor channel_map = blog→계정). 연계 지점은 **세계(계정) 단위**뿐.

### 3단 구조

| 단 | 매핑 | 1:1? | 근거 문서 |
|----|------|------|----------|
| **T1** | GitHub repo ↔ YouTube 채널 | ✅ 1:1 | `channel-repo-map.json` v2.0 (채널 15 = 레포 묶음) |
| **T2** | 티스토리 blog ↔ 카카오 계정 | ✅ 1:1 | `accounts.json` · `TISTORY_25_SLOTS.md` (21슬롯) |
| **T3** | 티스토리 세계 ↔ YouTube 세계 | ❌ **계정 단위 연계** | Boss 확정 · 본 수첩 §2/§4/§5 |

### T3 — 다대일 수렴 (폰/b계정 비즈니스)

```
[티스토리 세계]                      [유튜브 세계 — 폰/b계정]
dtslib1k 5블로그 ─┐
 (문학·과·수·사·철) ├→  dtslib.kr 비즈니스방송 ─→ @dtslib-branch  ← 주력 깔때기
dtslib2k 5블로그 ─┘      (SEO·텍스트 코퍼스)     (dtslib.kr 등 11레포)
                                                @espiritu-tango (보류)
                                                @artrew · @phoneparis
                                                @alexandria · @justino  ← 별개 버티컬(레포·도메인 각자)
```

- **10개 블로그 = 비즈니스 세계의 텍스트·SEO 코퍼스** → 주력 채널 `@dtslib-branch`로 수렴
- 나머지 5채널(탱고·artrew·phoneparis·alexandria·justino)은 각자 레포·도메인 세계 → 블로그와 무관
- **왜 1:1이 아니냐:** dtslib1k/2k 콘텐츠(문학·과학·수학·사회·철학·KR메리트)는 6채널의 버티컬(탱고·AI미대생·모바일유통·요양원·패션)과 내용 불일치. 1:1은 창작에 불과.

*`_Claude` · 2026-08-22 · 출처: papyrus SSOT + TISTORY_25_SLOTS + Boss 재편 확정*
