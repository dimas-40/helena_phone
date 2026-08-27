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
