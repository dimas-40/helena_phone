# 네이버 블로그 — Marine Quilt (손바느질 발행)

> 웹진 워크센터 — 미끼·티저 퍼널 입구  
> **정본: 자동화 폐기 → 스킨 1회 + 서식 + TG 손바느질**

## 핵심
네이버 포스팅 공식 API 없음.  
**Marine Quilt** = 해병대 구조(시범→따라→실전) + 퀼트 표면(한 땀 붙여넣기).

## 정본 패키지
| 파일 | 용도 |
|------|------|
| [`naver/quilt/BOSS-CARD.md`](../naver/quilt/BOSS-CARD.md) | 3분 설치 |
| [`naver/quilt/skin-custom.css`](../naver/quilt/skin-custom.css) | 스킨 CSS |
| [`naver/quilt/weekly-seosik-preview.html`](../naver/quilt/weekly-seosik-preview.html) | 서식 미리보기 |
| [`naver/quilt/tg-package-template.md`](../naver/quilt/tg-package-template.md) | TG 배달 포맷 |

## 관련
- [Marine Quilt 디자인 노트](../_notebook/42-marine-quilt-naver-design_Grok.md)
- [네이버 웹진 솔루션](../_notebook/23-naver-webzine-solution.md)
- [Naver 파싱](../_notebook/26-naver-parsing-solution.md)
- [Paste Pipeline](../_notebook/24-paste-pipeline.md)

## 퍼널 위치
TG 패키지 → Naver 퀼트 티저 → YouTube 조교 강의.


---

## 업데이트 (2026-08-27) — ADB 실터치 자동화 부활 확인 (재검증 필요, 임시 병행)

**"자동화 폐기" 결론은 CDP/Playwright 기반 시도(headless든 headed든) 한정이었다.**
오늘 WSL PC 세션에서 Tab S9 + AutoJS6(accessibility 기반 실터치, ADB gesture injection)로
dtslib/eae_kr 2계정 로그인을 캡차·SMS벽 없이 통과시킴 — CDP 자동화 지문이 전혀 없는
경로라 기존에 막혔던 ncaptcha 벽을 처음으로 뚫었을 가능성이 있음.

- 스크립트: `/storage/emulated/0/Scripts/ax6-tap.js` (Tab S9, 이 폰에도 동일 배포 예정)
- 트리거: `am start -a android.intent.action.VIEW -d file:///storage/emulated/0/Scripts/ax6-tap.js org.autojs.autojs6/org.autojs.autojs.external.open.RunIntentActivity`
- 막혔던 지점: Chrome 자동입력(저장된 비밀번호) 바텀시트가 입력 가로챔 → 스크립트가
  뒤로가기로 감지·해제(사람이 하듯 반응형 처리, OS 설정 안 건드림)
- 결과: dtslib/eae_kr 2계정 SUBMITTED, 로그인 후 naver.com 홈에서 실제 계정명 확인됨
- parksy_kr은 쿼터증설+아리랑 통합런칭 이슈로 의도적 제외(하드코딩 스킵)

**주의: 1회 성공이 재현성을 보장하지 않는다.** 반복 안정성(며칠 연속 성공 여부),
포스팅까지 이어지는지, 뜸한 계정 SMS벽 재발 여부는 미검증. Marine Quilt(손바느질)
정본 폐기하지 말고 이 자동화가 N회 연속 안정 확인될 때까지 병행 유지할 것.


---

## 최종 확정 (2026-08-27, v2) — 로그인+발행 E2E 실측 성공, 재검증 아님

**앞의 "재검증 필요" 상태를 넘어섰다. 오늘 같은 세션에서 로그인 → 제목/본문 작성 →
실제 발행 버튼 클릭까지 통째로 완주했고, 진짜 라이브 포스트로 발행 확인 후 삭제까지
검증했다. 다음은 진짜 콘텐츠(GitHub/YouTube/허브 링크 3개 조합)로 재발행해서
`PostView.naver`에 실제 게시된 걸 재확인함(태그 자동파싱까지 확인).**

### 핵심 함정 3가지 (여기서 막히면 이 문서부터 다시 볼 것)

1. **세션은 브라우저에 1개뿐** — 로그인 A → 로그인 B 연달아 하면 B가 A 세션을
   덮어쓴다. "계정 A 로그인 → A 작업 끝 → 계정 B 로그인 → B 작업" 순서로만 갈 것.
2. **Chrome 자동입력(저장된 비밀번호) 바텀시트**가 로그인 필드 입력을 가로챈다 —
   뜨면 뒤로가기로 닫고 계속(OS 설정 건드리지 말 것, 반응형 처리로 충분).
3. **SmartEditor 제목/본문은 React contenteditable이라 `setText()`/`node.paste()`
   둘 다 리턴값은 성공인데 실제 DOM엔 반영 안 됨.** 유일하게 실제로 먹히는 방법은
   **롱프레스 → 컨텍스트 메뉴의 "붙여넣기" 버튼 클릭**뿐이다(클립보드 제안 칩
   좌표 탭도 안 됨). 클립보드 접근 권한 팝업("허용/차단")이 뜨면 허용 후 재시도.

### 마스터 스크립트

`/storage/emulated/0/Scripts/ax6-tap.js` (양쪽 기기 동일 배포)
트리거: `am start -a android.intent.action.VIEW -d file:///storage/emulated/0/Scripts/ax6-tap.js org.autojs.autojs6/org.autojs.autojs.external.open.RunIntentActivity`

전체 소스는 이 레포 `tistory-naver/ax6-tap.js`에 그대로 저장됨 — 로그인(`loginAccount`),
붙여넣기(`pasteOnce`/`setTextAtFocus`), 발행(`publishPost`) 함수 재사용 가능.

### 실측 좌표 (Tab S9, 1600x2560 기준 — 기기별 해상도 다르면 재측정 필요)

- 제목 필드: (330, 636)
- 본문 필드: (559, 804)
- 발행 버튼(1차, 에디터 상단): (1504, 301)
- 발행 확정 버튼(2차, 설정패널 내부): 패널 열린 후 `hit("발행")`로 재탐색

### 다음에 이어서 할 것

- eae_kr 계정도 같은 방식으로 실측 재확인(로그인만 확인됨, 발행까지는 dtslib만 확인)
- parksy_kr은 여전히 의도적 제외(쿼터증설+아리랑 통합런칭 이슈)
- 여러 계정 연속 발행 시 반드시 "로그인→발행→다음 계정 로그인" 순서 지킬 것(세션 덮어쓰기 방지)
