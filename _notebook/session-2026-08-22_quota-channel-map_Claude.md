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
| 2 | @espiritu-tango | espiritu-tango | 물성 HQ |
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

## 2. 역산 — 채널 ↔ 티스토리 1:1 매핑 (papyrus 21슬롯)

| 세계 | Google 계정 | YouTube 채널 | 티스토리 계정 | 티스토리 블로그 | 이 폰 연결 |
|------|------------|--------------|---------------|----------------|-----------|
| **parksy (a)** | dimas.thomas.sancho | 5 (blogger/philosopher/visualizer/musician/technician-parksy) | parksy_kr | 5 (parksy 전용) | ❌ 미연결 |
| **EAE (c)** | thomas.tj.park | 2 (EAE-Univ · BeingEduartEngineer) | eae_kr | **5 (eae-kr/broadcast/music/image/video)** | ✅ **연결됨** |
| **dtslib (b)** | dtslib1979 | 6 (dtslib-branch 외) | dtslib·dtslib1k·dtslib2k | **15 (dtslib·polyglot14·webtoon-park·programmer-park·musician-park · dtslib1k·hitop·midmath·midsocial·lafilosofia · korean-parksy·kr-merit×4)** | ❌ 미연결 |

**핵심:** 이 폰(`tistory-naver/accounts.json`)엔 **c 세계(eae 5블로그)만** 연결돼 있음. b 세계 15블로그·a 세계 5블로그는 papyrus automation에 존재하지만 이 폰에서 안 닿음.

---

## 3. 갭 + 설치 순서 (추천)

1. **b 세계 티스토리 (dtslib 15블로그) 우선** — 쿼터 60k 있는 주 계정 세계. 주력 = `dtslib.tistory.com`(철학자박씨, 39편)·`polyglot14`(31편)·`programmer-park`(37편)
2. **필요 크레덴셜:** `dtslib@kakao.com` · `dtslib1k@kakao.com` · `dtslib2k@kakao.com` (papyrus `tools/tistory/accounts.json`에 있음)
3. a 세계(parksy)는 a계정 쿼터 미승인 + 글래스 로드맵 → 보류 (쿼터 확정 후)

**원칙:** 세계(계정)별 미디어 구분 — 채널·블로그·레포가 같은 세계 안에서만 1:1 짝. 세계 간 섞지 않음.

---

## 5. 티스토리 → 비즈니스 방송 연계 (Boss 질문 → 실행 · 2026-08-22)

**Boss:** "이 두 가지 계정으로 여기 핸드폰 히스토리 월드(비즈니스 방송)와 연계해야 되지 않냐?"

**papyrus `tools/tistory/accounts.json` 마스터 확정 (4계정 20블로그):**

| 카카오 계정 | 컨셉 | 블로그 (5) | 세계 |
|------------|------|-----------|------|
| dtslib@kakao.com | 🧬 한글 OJT (수입) | polyglot14·dtslib·webtoon-park·programmer-park·musician-park | **경제 (폰)** |
| dtslib1k@kakao.com | 📚 대학개론서→고딩언어 | dtslib1k·hitop·midmath·midsocial·lafilosofia | **경제 (폰)** |
| dtslib2k@kakao.com | 🏆 KR메리트/한국인특질 | korean-parksy·kr-merit×4 | **경제 (폰)** |
| eae_kr@kakao.com | 교육방송 | eae-kr·broadcast·music·image·video | 교육 (탭) |
| parksy_kr@kakao.com | 🧬 영문 OJT (수출·1:1 대칭) | blogger·technician·philosopher·visualizer·musician-parksy | **맨 마지막** (Boss) |

**실행:** `tistory-naver/accounts.json`에 **dtslib·dtslib1k·dtslib2k 15블로그 연계** (eae 5 유지 = 총 20). id=슬러그 유니크 (post.py acc_map 요구). 비밀번호 = 기존 공유 (papyrus와 동일 11자 확인). template 동기화. parksy_kr 보류.

**구성:** post.py 계정별 로그인(각 email + 공유 pw) ✅ · verify_accounts.py는 accounts[0]만 로그인 → **계정별 실행 필요** (알려진 한계).

---

## 4. 기기×계정×방송 토폴로지 확정 (Boss · 2026-08-22)

| 기기 | 계정 | 방송 | 상태 |
|------|------|------|------|
| **탭(태블릿)** | c (thomas.tj.park) | 교육방송 2채널 | 스튜디오 완성 후 론칭 |
| **폰(S25 Ultra)** | b (dtslib1979) | 경제방송 6채널 | **시작 = 여기** (쿼터 60k) |
| a (dimas.thomas.sancho) | KR방송 | 쿼터 미승인 · 기기 미매칭 | 별도 처리 |
| **S21 (proot Ubuntu 2)** | — | 경제방송 **양산 공장 노드** | 매칭 (papyrus: 누나폰 공장·자체 생산) |

- **경제방송 콘텐츠 모델 (Boss):** dtslib-branch(브랜치들)와 함께 스토리 제작 · 그 사람들 도움 · 비즈니스 소설. **이 방송부터 시작.**
- **proot Ubuntu 2 = S21** (papyrus `ecosystem.json.template` devices tier1) — 이 폰(S25)=proot Ubuntu 1. S21 = 경제방송 양산 공장 노드로 매칭.
- 메모리: `device-account-broadcast-topology.md` 저장.

*`_Claude` · 2026-08-22 · 출처: papyrus SSOT + TISTORY_25_SLOTS*
