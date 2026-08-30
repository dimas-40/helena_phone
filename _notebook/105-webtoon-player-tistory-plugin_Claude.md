---
date: 2026-08-22
agent: Claude Code (출판부)
mark: _Claude
type: plugin
status: active
related:
  - tistory-master-guide_Claude.md
  - tablet-broadcast-studio_Claude.md
  - tablet-setup-parksy-method_Claude.md
  - gifts/parksy-webtoon-player (회수 선물)
---

# 웹툰 뷰어 → 티스토리 파이프라인 플러그 옵션 (A급 + 모바일/인스타툰)

> 한 줄: `parksy-image` 웹툰 파이프라인의 **6번째 출력 타겟(티스토리)** 을
> 티스토리 발행 파이프라인에 **플러그 옵션 하나**로 끼워 넣고,
> 웹툰 뷰어(ParksyPlayer)를 **A급 + 모바일(인스타툰) 최적화**로 올렸다.

---

## 0. 배경 — 오늘 무슨 일이 있었나

1. dtslib1k/2k 티스토리 10곳에서 **"빈 웹툰 게시글"** 사고 발견 (이미지 0장 → 뷰어가 빈 화면).
2. 유실 직전의 원본 코드 `parksy-webtoon-player.html` 회수 → `/root/gifts/parksy-webtoon-player/`.
3. 조사 결과: **레포엔 원본이 없고 라이브 블로그에만 있던** 코드였다.
4. 진짜 자산은 코드가 아니라 **"완성 파이프라인 + 완성 콘텐츠가 5개월째 방치"** 였다는 사실.

---

## 1. 핵심 통찰 — "티스토리에 옵션 하나가 빠져 있었다"

`dtslib1979/parksy-image` 의 웹툰 패키징 `webtoon_packager.py` 는
**마스터 캔버스 → 5개 플랫폼 자동 패키징** 을 이미 지원한다.

| 지원 플랫폼 (기존 5종) | 빠진 것 |
|---|---|
| instagram · naver · shorts · broadcast · thumbnail | **tistory** ⬅ 여기 |

→ 티스토리 발행에 **웹툰 뷰어라는 옵션 하나가 빠져 있었고**,
그 빈칸 때문에 완성된 에피소드(ep04 일상편 등)가 3월부터 **5개월째 발행 못 나감**.

**정답은 "새로 짜는 게 아니라 `--platform tistory` 6번째 옵션 추가"에 가깝다.**

---

## 2. 티스토리 파이프라인 = "포스트 타입 하나 = 렌더러 하나"

기존 구조 (실측):

| 렌더러 | 포스트 타입 |
|--------|-------------|
| `template.py` | 기본 글 (아코디언 + 인포그래픽) |
| `magazine.py` | 피아노 웹진 (매거진 레이아웃) |
| **`webtoon.py` (신규)** | **웹툰 (ParksyPlayer v2 주입)** |

→ 이번에 `webtoon.py` 를 추가한 것 = **티스토리 파이프라인에 웹툰 플러그 옵션을 꽂은 것.**

### webtoon.py 동작

```
manifest(에피소드 메타 + 이미지 URL) → webtoon.py
  → assets/parksy-webtoon-player.html 템플릿 로드
  → 설정 JSON 주입 (코드는 단일 원본 유지)
  → posts/<slug>.json 생성 → post.py 가 발행
```

```bash
python3 tistory-naver/webtoon.py tistory-naver/episodes/sample-ep01.json
python3 tistory-naver/webtoon.py episodes/ep01.json --dump   # HTML만 확인
```

manifest 형식은 `tistory-naver/webtoon.py` docstring 참고.
`account`(accounts.json id) + `blog`(블로그 슬러그)는 **필수** (웹툰은 b계정/태블릿 c계정 갈림).

---

## 3. ParksyPlayer v1 → v2 (A급 + 모바일 최적화)

원본 v1 은 잘 만들었지만 3개 약점이 있었고, 코드가 **한 줄 minify** 라서 여기서 튜닝 불가였다.

| 항목 | v1 (회수 원본) | v2 (신규) |
|------|----------------|-----------|
| 빈 `images:[]` 방어 | ❌ 없음 (오늘 사고 원인) | ✅ "콘텐츠 준비 중" 안내 |
| 접근성 | ❌ alt/ARIA 전무 | ✅ `alt` + `role`/`aria-label` |
| 설정 위치 | 코드 안 하드코딩 | ✅ JSON 블록 외부화 (한 곳만 고침) |
| 코드 가독성 | 한 줄 minify | ✅ 주석·변수 분리 (ES5) |
| 모드 | 가로 캐러셀 단일 | ✅ **캐러셀 + 세로 스크롤 듀얼** |
| 모바일 | 최소 대응 | ✅ 풀블리드 + 스크롤스냅 + 큰 터치존 |

### 모바일 = 인스타툰 미러링

- **`mode: "carousel"` (기본)** = 인스타 캐러셀 스타일. 가로 스와이프, 풀블리드, 플로팅 진행바.
- **`mode: "scroll"` (옵션)** = 네이버식 세로 웹툰. 컷 스택 + `scroll-snap`, 하단 도트 내비.
- 모바일에서 `max-width` 해제 → 이미지가 화면 폭을 꽉 채움. 데스크톱은 640px 중앙 정렬.
- 터치 스와이프 / 키보드(←→ / Space / f) / 자동재생 / 전체화면 유지.

### 튜닝 포인트 (여기서 바로 고칠 수 있게)

- 설정 전부 = `<script id="parksy-webtoon-config" type="application/json">` 한 블록.
- 강조색 `accent` 는 CSS 변수 `--pw-accent` 로 주입 → 테마만 바꾸려면 JSON 한 줄.
- `webtoon.py` 가 이 블록만 갈아끼우므로, **플레이어 코드는 단일 원본**(`assets/parksy-webtoon-player.html`).

---

## 4. 남은 결정 1개 (계정 매칭 — 지난 스레드와 동일)

웹툰 원발행 대상 = **b계정 티스토리(dtslib1k/2k, 경제방송 · dtslib1979)**.
그런데 이 워크센터(태블릿) 정체 = **c계정(교육방송 · thomas.tj.park / dimas-40)**.

| 선택 | 의미 |
|------|------|
| ① `account:"dtslib"` (b계정) | 탭이 b계정 작업을 대행. 지금 dimas-40 통합계정 상태에선 자연스럽지만 4계정4세계는 흐려짐 |
| ② `account:"eae-image"` (c계정) | fork 모델 그대로 깔끔, 단 새 채널을 키워야 함 |

`webtoon.py` 는 이걸 **manifest의 account/blog 로 열어둠** — 결정만 하면 고정값으로 바꾸면 됨.

---

## 5. 파일 지도

| 파일 | 역할 |
|------|------|
| `tistory-naver/assets/parksy-webtoon-player.html` | **플레이어 단일 원본 (v2)** |
| `tistory-naver/webtoon.py` | **파이프라인 플러그 렌더러** |
| `tistory-naver/episodes/sample-ep01.json` | manifest 샘플 |
| `tistory-naver/posts/*.json` | 발행 대기 큐 (post.py 입력) |
| `/root/gifts/parksy-webtoon-player/` | 회수 원본 (v1, 증거 보존) |

## 6. 다음 (팬딩)

- [ ] `webtoon_packager.py --platform tistory` 브랜치 (parksy-image 쪽 — 클론 필요)
- [ ] 계정 결정 (① dtslib b계정 vs ② eae-image c계정)
- [ ] dtslib1k/2k 빈 게시글 정리 (삭제 or 복구)

*agent mark `_Claude` · 2026-08-22*
