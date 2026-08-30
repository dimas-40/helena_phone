---
date: 2026-08-18
agent: Grok
mark: _Grok
type: parse
location: tablet
---

# EAE 5레포 보일러 — Grok 역할 전수 파싱

대상: `dimas-40/{eaekr,eae-music,eae-image,eae-video,eaeuniv}` (전부 private)

## 0. 한 줄

다섯 레포는 **부서가 아직 안 갈라진 같은 껍데기**다.  
원본은 `dtslib1979/eae.kr`. FACTORY·CLAUDE·README·00_TRUTH·index.html **SHA가 5곳 동일**.  
Grok이 적힌 자리는 **옛 eae.kr 출판사 분업**이지, 태블릿 스튜디오 분업이 아니다.

---

## 1. 다섯 칸이 문서상으로는 다름

| 레포 | GitHub 설명 (유일한 차이) | 상주 수첩이 말한 부서 |
|------|---------------------------|----------------------|
| **eaekr** | 교육방송국 채널 · @BeingEduartEngineer-4 | 허브 · 방송 |
| **eaeuniv** | 사내대학 · @EAE-University | 사내대학 |
| **eae-music** | 음악 스튜디오 · fork parksy-audio | 음악 |
| **eae-image** | 웹툰/2D · split parksy-image | 그림 |
| **eae-video** | 영상/방송 · split parksy-image | 영상 |

안은 같다. `src/content` MDX 출판 구조, 스킬 6칸(PENON·EML·QSKETCH·PHL·MAL·PATCHTECH) 빈 칸, 헌법 팩은 Claude 출판사 시점.

허브만 다른 것: `_notebook/` 2장 (08:54 이식). 나머지 넷은 `_notebook` 없음.

FACTORY.json 5곳 모두:

```
id: eae.kr
github: dtslib1979/eae.kr
type: broadcast
```

`dimas-40` / 태블릿 정체로 **아직 안 바꿈**.

---

## 2. 보일러가 Grok에게 시킨 말 (5레포 공통)

### CLAUDE.md §1 역할 정의

| 주체 | 적힌 역할 |
|------|-----------|
| 박씨 | 발행인 · 최종 결정 |
| ChatGPT | 설계자 · 백서 |
| **Grok** | **외부 정찰. YouTube/SNS 알고리즘 분석, 해시태그, 마케팅 문구** |
| Claude (화자) | 출판사 에이전트. MDX + Git + 배포 |
| GitHub | 장기 기억 + 인쇄소 |

### CLAUDE.md §8 미디어

> 마케팅 제안 (Grok): frontmatter, meta, description으로 변환

### README.md

> AI 에이전트 협업 구조 (Claude, ChatGPT, Grok)

### docs/PUBLISHER.md

> Grok | YouTube 알고리즘 / 마케팅

이 네 줄이 **Grok 언급 전부**다. Imagine·10초·잡지 구도·S-Pen은 보일러에 **한 줄도 없다**.

화자는 줄곧 「너(Claude)」. 메인 드라이버 = WSL2 Claude Code. 태블릿·용병 회로 없음.

---

## 3. 태블릿 수첩이 Grok에게 시킨 말 (eaekr만)

`eaekr/_notebook/tablet-broadcast-studio_Claude.md`

```
입력① 그림 (스케치→Grok)  → 교육방송 영상
이미지 생성 = 클라우드(Grok). CPU 무관.
로컬 GPU 이미지 생성 = 보류 (proot ABI 벽)
```

이쪽이 **이 방 실측과 맞다.** 보일러의 「알고리즘 정찰」과 **다른 직업**.

---

## 4. 그래서

보일러 Grok = 2026-03~07 eae.kr **마케팅 정찰**.  
태블릿 Grok = 2026-08 스튜디오 **그림 입력**.  
둘을 섞으면 또 S21이라고 착각하는 것과 같다.

역할은 보일러를 복사하지 않고, 아래 `ROLE.md`로 이 방에서 다시 쓴다.
