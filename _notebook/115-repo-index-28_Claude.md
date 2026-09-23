# 28레포 전수 파싱 — 인덱스 (2026-09-23)

> 작성: `_Claude` · Boss 지시 ("너 내 28개 레포 다 파싱해 봐")
> 선행: `112-repo-inventory-master_Claude.md` (2026-09-04, 로컬 접근 가능한 **10곳만**)
> 이번: `dtslib1979` 계정 **28/28 전수** — **클론 없이** GitHub API로.

---

## 0. 방법 (왜 클론 안 했나)

- 28레포 합계 **3.26GB · 27,027 파일**. proot 폰에서 전량 클론은 디스크·시간 모두 무리.
- 그래서 `git/trees?recursive=1` API로 **파일 목록만** 받아 파싱 (레포당 1콜, 총 28콜).
- 스크립트: `scripts/repo_index_Claude.py` · 재현:
  ```bash
  export GH_TOKEN=$(grep -m1 '^GITHUB_TOKEN=' .secrets.env | cut -d= -f2-)
  python3 scripts/repo_index_Claude.py
  ```
- 실측 데이터: `_notebook/data/repo-index-28.json` (구조) · `_notebook/data/repo-identity-28.json` (정체 문서)
- **주의:** `truncated` 레포 **0개** → 28개 트리 전부 완전 수신 (부분 파싱 아님).

---

## 1. 총계

| 항목 | 값 |
|------|-----|
| 레포 | **28** (private 27 · public 1) |
| 파일 | **27,027** |
| 문서(md/txt/rst) | **15,286** |
| 용량(git) | **3.26GB** |
| 최신 push | 2026-09-23 (papyrus · alexandria · buckleychang) |
| 9월 이후 활동 | **15개** |
| 8월 이전 멈춤 | **13개** |

- **public은 `dtslib-apk-lab` 1개뿐.** 112문서(2026-09-04)는 "26 private + 2 public"이라 적었는데, 지금 실측은 **27+1**. 공개/비공개 비율이 바뀌었다.
- 문서 15,286개 중 **11,852개(77.5%)가 `parksy-logs` 한 곳**. 나머지 27레포 합계는 3,434개.

---

## 2. 28레포 전수표 (파일수 내림차순)

| # | 레포 | 공개 | 파일 | 문서 | 용량 | 최종push | 설명(레포 자기 신고) |
|---|------|------|------|------|------|----------|----------------------|
| 1 | `parksy-logs` | PRI | 12162 | 11852 | 29MB | 26-08-11 | Personal text capture archive (Android Share Intent 자동저장) |
| 2 | `parksy-image` | PRI | 3773 | 471 | 933MB | 26-09-22 | 썸네일 + AI 영상생성 씨앗 |
| 3 | `dtslib-papyrus` | PRI | 2157 | 994 | 129MB | 26-09-23 | DTSLIB Digital Papyrus (허브) |
| 4 | `parksy-audio` | PRI | 1404 | 171 | 964MB | 26-09-17 | 오디오 실험·나레이션·음원 자산 |
| 5 | `parksy-webzine` | PRI | 1159 | 230 | 369MB | 26-09-21 | 에브럼 — 웹진·웹툰 서사 |
| 6 | `OrbitPrompt` | PRI | 618 | 187 | 10MB | 26-07-24 | Multiple query gen engine to AI |
| 7 | `phoneparis` | PRI | 576 | 173 | 177MB | 26-09-04 | 모바일 유통·현장판매 실험 |
| 8 | `dtslib-cloud-appstore` | PRI | 514 | 188 | 3MB | 26-09-22 | 클라우드 앱 배포 실험 |
| 9 | `dtslib-apk-lab` | **PUB** | 513 | 75 | 2MB | 26-09-22 | APK 빌드·패키징 실험실 |
| 10 | `termux-bridge` | PRI | 510 | 204 | 5MB | 26-09-19 | PC↔Termux 간극 도구 (CDP·QA) |
| 11 | `parksy.kr` | PRI | 366 | 73 | 18MB | 26-07-30 | EduArt Engineer's Grimoire |
| 12 | `dtslib-localpc` | PRI | 350 | 145 | 33MB | 26-09-16 | 로컬 PC 실행 노드 |
| 13 | `buddies.kr` | PRI | 342 | 77 | 21MB | 26-07-29 | 오프라인 유통 지사 |
| 14 | `papafly` | PRI | 301 | 52 | 81MB | 26-09-17 | papafly incubation |
| 15 | `eae-univ` | PRI | 276 | 78 | 3MB | 26-08-23 | AI시대 온라인 학습 플랫폼 |
| 16 | `koosy` | PRI | 222 | 20 | 37MB | 26-07-30 | Bluffing editing CELEB story |
| 17 | `gohsy-production` | PRI | 201 | 38 | 258MB | 26-07-30 | 방송 스튜디오 3레인 |
| 18 | `artrew` | PRI | 200 | 24 | 51MB | 26-07-30 | KOOSY 자매 사이트 |
| 19 | `dtslib-branch` | PRI | 192 | 60 | 19MB | 26-09-04 | Boilerplate dev / 실모델 |
| 20 | `gohsy-fashion` | PRI | 192 | 39 | 15MB | 26-07-30 | DONGSEON Studio (Tier 2) |
| 21 | `namoneygoal` | PRI | 161 | 13 | 17MB | 26-07-30 | 부동산·사업 길드 실험 |
| 22 | `eae.kr` | PRI | 144 | 20 | 6MB | 26-07-30 | EAE PWA Books |
| 23 | `alexandria-sanctuary` | PRI | 139 | 26 | 7MB | 26-09-23 | 팔공산 영성 돌봄 커뮤니티 |
| 24 | `hoyadang.com` | PRI | 128 | 18 | 39MB | 26-09-17 | 식당 프로토콜 (espiritu 포크) |
| 25 | `gohsy` | PRI | 128 | 16 | 56MB | 26-07-30 | gohsy comes true |
| 26 | `espiritu-tango` | PRI | 110 | 24 | 16MB | 26-09-14 | Tango Magenta 방송 구조 |
| 27 | `dtslib.kr` | PRI | 110 | 7 | 16MB | 26-07-30 | 경제방송 허브 |
| 28 | `buckleychang.com` | PRI | 79 | 11 | 22MB | 26-09-23 | Buckley Chang CPA |

---

## 3. 파싱이 드러낸 것 (구조만 봐도 보이는 사실)

### 3.1 CLAUDE.md 28개 전부 존재 — 그런데 27개가 같은 템플릿
- 28/28 전부 `CLAUDE.md` 보유. 최소 1.2KB(parksy-audio) ~ 최대 116KB(papyrus).
- **27개가 동일한 "DTSLIB-LAW-PACK" 블록**을 포함 (`<!-- DTSLIB-LAW-PACK-END -->` 마커 실측).
  - 여기엔 **레포와 무관한 내용**도 들어 있다: `WSLg Playwright 크래시 3종`, `YouTube 채널 API OAuth 16채널 현황`, `@BeingEduartEngineer-4 차단 확인` 등.
  - 즉 **식당 레포(hoyadang)에도 YouTube OAuth 매뉴얼이 박혀 있다.** 템플릿 일괄 주입의 부작용.
- 템플릿 준수율(= 공통 112줄이 차지하는 비중): `parksy-audio` 100% · `alexandria-sanctuary` 96.3% · `parksy-logs` 84.1% vs `dtslib-papyrus` 15.5% · `parksy-image` 23.8% · `gohsy-production` 24.2%.
  - **준수율 높음 = 그 레포만의 지시가 없다는 뜻.** 상위 3개는 사실상 빈 문서.

### 3.2 유일한 예외 = parksy-audio
- 28개 중 **LAW-PACK이 없는 유일한 레포**. 1.2KB짜리 YouTube 포인터 한 줄이 전부.
- 그런데 이 레포가 **용량 1위(964MB)**. 964MB를 가진 레포에 정작 "이게 뭔지" 설명이 제일 없다.

### 3.3 규모가 한 곳에 쏠려 있다
- 문서의 77.5%가 `parksy-logs` (자동 캡처 아카이브, 2026-08-11 이후 멈춤).
- 용량 상위 2개(`parksy-audio` 964MB + `parksy-image` 933MB) = **전체의 58%**.
- 3MB 이하 레포는 1개(`dtslib-apk-lab`)뿐 — 즉 나머지는 전부 자산을 품고 있다.

### 3.4 절반이 7월 이후 멈춰 있다
- 9월 활동 15개 / 8월 이전 멈춤 13개.
- 멈춘 13개는 대부분 **7월 30일 동시 정지**: `gohsy` `gohsy-fashion` `gohsy-production` `artrew` `koosy` `namoneygoal` `dtslib.kr` `eae.kr` `parksy.kr` — 같은 날 일괄 중단된 그룹. 지사(支社) 계열로 보임.
- 반대로 9월까지 살아있는 건 **허브 + 도구 + 실험실** 계열(papyrus · apk-lab · cloud-appstore · localpc · termux-bridge · parksy-*).

---

## 4. 이번 파싱이 **안 한** 것 (정직하게)

- **문서 15,286개의 본문은 안 읽었다.** 이번엔 (1) 파일 목록 트리, (2) 레포별 `CLAUDE.md` 전문, (3) 레포 메타데이터 — 여기까지.
- `parksy-logs` 11,852개, `papyrus` 994개 같은 본문 다이제스트는 미착수.
- 참고로 112문서(09-04)가 잡은 "md ~1,080개"는 **로컬 접근 10곳 기준**이었다. API 전수로 세면 **15,286개** — 14배 차이. 그때 숫자는 "우리가 가진 것"이 아니라 "손에 있던 것"이었다.

## 5. 다음 후보 (지시 대기 — 임의 착수 안 함)

1. **본문 다이제스트** — 관심 레포 몇 개로 좁혀서 문서 요약 (전량은 15,286개라 대상 한정 필요)
2. **LAW-PACK 정리** — 27개 레포에서 무관 블록(YouTube/WSLg) 걷어내고 레포별 고유 지시 보강
3. **정지 그룹 판정** — 7월 30일 동시 정지한 9개 레포를 ACTIVE/STANDBY/FROZEN로 재분류 (`hq/REPO-STRATEGY.md` 갱신)
