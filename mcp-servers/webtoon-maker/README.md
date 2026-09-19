# 웹툰메이커 (phone-webtoon-make) — 폰 작가주의 레인

> 정체: **웹툰 "그리기"가 아니라 "제작·프로덕션"**. 드로잉(손맛·추상화 재미)은 Boss가 따로 하고,
> 이 MCP는 그리기 뒤의 귀찮은 제작(편집·조립·발행·영상화)을 삼킨다.

## 본질 (Boss 2026-09-18 확정)
- **드로잉** = Boss가 손으로(관찰·추상화, 그 자체가 목적·엔드스테이션).
- **이 MCP** = 그리기 뒤의 지루한 공정 자동화.
- **Boss는 코드 못 치고 STT로 말만** → 에이전트(Claude)가 이 코드를 만든다.
- **이미지 생성** = 삼성 온디바이스(GUI 자동화·무료). 그리기는 기계, 제작은 이 MCP.

## 투트랙 (트레인)
- **프로덕션 트레인**(태블릿/WSL): 양산·노멀라이즈. ADB 생성+QA+자동발행.
- **작가주의 트레인**(폰/이 MCP): 예술성·개성. "특이한 것만" — 사진술+편집술+인터랙티브+인포그래픽.

## 도구 (감옥원칙 — 기획=풀어줌 / 공장=수갑)
| 도구 | 단계 | 역할 |
|---|---|---|
| `webtoon_direct(source, captions)` | 기획(풀어줌) | 연출 기획: BLIP 눈(실험) 또는 작가 captions(눈 탈부착) |
| `webtoon_assemble(captions, dialogue)` | 공장(수갑) | 식자·조립 → 세로 웹툰 HTML |
| `webtoon_record(html, url)` | 공장(수갑) | 화면 녹화 → 스토리텔링 영상(mp4), 스크롤=카메라 |

## 핵심 파일
- `phone_webtoon_make_mcp.py` — MCP 본체 (이 폴더에 사본)
- `engine.js` — 연출 엔진(SCROLL_FIX+IMAGE_JS+INTERACTIVE_JS+INFO_JS) — GitHub Pages 호스팅본
- `skin_sync.js` — PC//m/ 스킨 정규화(WSL SKIN_SYNC_JS 전체 이식)

## 연출 문법 (작가주의 자산)
- `SHOTS`(카메라 숏 10종) · `SHOT_SEQ`(설정→오버숄더→인서트→극클로즈업) · `SHOT_TIMELINES`(5키프레임)
- `SPEC`(Tistory Interactive Comic Spec v1: vanilla JS + transform/filter/clip/mask)
- `DEFAULT_TL`(타임라인 DSL) · KO(한글 번역)

## 경제·해자 (왜 이게 되는지)
- 온디바이스 GPU = 고정비(이미 산 기기), 변동비 0.
- ADB 역조작 = 대체 입력(접근성 유사) → 범용 해자(이미지→동영상→더), 애플 제외.

## 관련 메모리
`webtoon-philosophy` · `webtoon-economics` · `webtoon-samsung-moat` · `mcp-jail-principle` · `webtoon-two-lanes` · `dtslib-28-repos` · `webtoon-eval-frame`
