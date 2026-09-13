# 세션 — 웹툰 인터랙티브 식자 파이프라인 확정 (_Claude · 2026-09-13)

## 요약
티스토리 콜드스타트(캡차) 해결 + 웹툰 발행 + **인터랙티브 식자(스크롤 연출)** 확정 + 모바일 표준 + MCP 변수화.

## 한 것
1. **티스토리 CDP 세션빌리기** — `cdp_session_lend.py`(신규). 삼성인터넷(Terrace)=본사그룹(dtslib1k 5블로그), 크롬=지사그룹(dtslib2k 5블로그) 세션 자동 빌리기. adb 키 불일치(proot b07fd vs Termux 75f1a)가 원인 → Termux 키로 정렬. 캡차 없이 10블로그 자동 커버.
2. **웹툰 발행** — `kr-merit-aggro.tistory.com/4` "웹진을 눕히고 영상으로 세운다 — PARKSY 웹툰".
3. **카테고리 2레인** — 잡지(16타이틀 FASHION~WATCH) + 몸춤(5카테고리 espiritu-tango).
4. **필름 스프로켓홀** — 좌우 다크그린 스트립+흰 구멍. `_add_film_sprocket` + `_fit100` 프롬프트에 반영.
5. **인터랙티브 식자(핵심)** — 스크롤 위치 스케일 0.95~1.08 + 글자 타이핑(한 글자씩) + 좌우 sway + 호버 글로우 + 탭 흔들림. 셀프컨테인드(콘텐츠에 스타일+JS 내장).
6. **모바일 표준** — 말풍선 13px. 데스크톱/모바일/앱 동일. `/m/4` 자동 리다이렉트 → `/4`.
7. **MCP 변수화** — `FILM_STRIP_W/HOLE_*`, `BUBBLE_LEFT/RIGHT/BOTTOM/FONT`, `INTERACTIVE_CSS/JS`. `_compose`가 13px+인터랙티브 내장 HTML 생성.

## 전환점 (Boss 판단)
- **"과잉 엔지니어링이냐"** → RVC(730MB 모델 전송) 스킵. 스크롤 인터랙티브가 핵심.
- **"모바일 표준 + 폰트만 줄여"** → 리다이렉트·스크롤 삽질 종결. 찌그러짐 원인은 폰트 16px.
- **스크롤 안 됨 원인** = `#s21-particles`/bezel 등 `position:fixed` 오버레이가 휠/터치 이벤트 가로챔 → `pointer-events:none` 한 줄.

## 교훈 (교재 "함정" 챕터용)
1. 기존 인프라·문서 먼저 인벤토리 (RVC 표준 문서를 먼저 안 읽고 ONNX 경로 삽질).
2. 애매하면 묻고, 커지면 멈추고.
3. 표준 베이스라인(모바일) 정하고 규격(폰트)만 통일.

## 메모리
- `parksy-webtoon-fantasy-pipeline.md` · `parksy-edit-obsession-philosophy.md` · `parksy-webtoon-session-lessons.md`
