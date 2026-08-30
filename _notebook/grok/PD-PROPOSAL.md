---
date: 2026-08-18
agent: Grok
mark: _Grok
cli: grok
type: proposal
location: tablet
status: plan
quality_bar: 80-of-A
---

# EAE 「렌즈」— Grok PD 프로포절

> 업무 수첩 원본. ComfyUI 그래프를 돌리지 않는다.  
> 감독 카드·도면 콘티·웹툰 파츠를 **이 CLI로 쥐어짜** 방송 숏을 만든다.  
> 마감 목표: **A급의 80%.** 나머지 20%는 붙이기·색큐브·믹스·업로드.

경로: `/root/work/_notebook/grok/PD-PROPOSAL.md`

---

## 0. 계약

| 항목 | 값 |
|------|-----|
| 채널 | `@BeingEduartEngineer-4` (교육방송). 업로드는 상주/ffmpeg 뒤 |
| 시리즈 | **렌즈 (LENS)** — 같은 내용을 영화 렌즈로 찍는다 |
| 파일럿 | **교육편** 「학생이 왜 공부해요 하고 물었다」 |
| 길이 | **약 55초** (16:9 본편). 나중에 9:16은 같은 숏 재프레이밍 |
| 단위 | 숏 하나 = 6초. 한 숏에 동작 하나 |
| 화질 | 스틸 16:9 · 클립 720p 가능하면 720, 아니면 480 후 업 |
| 80% | 숏이 **각각** 방송처럼 보인다. 얼굴·색·카메라가 회차 안에서 안 흔들린다 |
| 20% | ffmpeg concat · 실 .cube · BGM 덕킹 · 자막 번인 · YT |

ComfyUI 이상: AnimateDiff를 안 돌리고, **기준 장 + 감독 축 + 카메라 한 줄 + 참조 영상**으로 같은 일을 더 선명하게 한다.

---

## 1. 왜 이 회차가 파일럿인가

창고에 **이미 콘티가 끝나 있다.** 대본을 새로 안 짠다.

출처: `dtslib1979/parksy-image`

| 컷 | 카메라 | 동작 | 말 |
|----|--------|------|-----|
| 1 | medium | stand / hold / thoughtfully | (내레이션) 매번 듣는 질문인데, 매번 다르게 들린다. |
| 2 | closeup | stand / point / angrily | (대사) 돈 벌려고요? 시험 때문에요? |
| 3 | medium | walk / slowly | (내레이션) 그 아이 말이 맞다. 대부분의 공부는 돈벌이용이 맞다. |
| 4 | closeup | lean | (내레이션) 근데 진짜 공부는 그게 아니다. 세상이 어떻게 작동하는지 보이기 시작하는 거다. |

시리즈 태그: `교육편`. EAE(에듀·아트·엔지니어)와 맞다.  
도면 SVG 5장 + 컷 JSON 4개 + 웹툰 파츠(얼굴·몸) = 촬영 대본.

---

## 2. 렌즈 잠금 (이 회차만)

`moods.yaml` 교육/워크스루 = `hong_sangsoo + lee_changdong`.  
카메라 바닥은 우선순위 1 **정일성**.

**이 회차 렌즈 = 홍상수 구도 + 정일성 빛.**  
왕가위·봉준호는 시즌 2 「같은 회차, 렌즈만 교체」용으로 남긴다.

| 축 | 값 | 숏에 박는 말 |
|----|-----|----------------|
| 샷 | 미디엄·정면 (홍) / 가끔 인물+공간 (정) | medium, almost frontal, figure in the room |
| 톤 | 담백, 일상 | flat daylight, no glamour |
| 팔레트 | 탈채도, 한국 자연색 | muted korean daylight, grey-beige walls |
| 모션 | 느린 줌 하나 또는 고정 | single slow zoom, or locked off |
| 리듬 | 숨 길게 | hold the beat, no whip pan |
| 프레이밍 | 정면, 여백 | person slightly off-center, empty chair in frame |
| LUT 이름 | `10_desaturated_moody` | 생성 때 이미 이 룩. .cube는 20% |

금지: 앰버-틸, 네온, 핸드헬드 흔들림, 한 숏에 동작 두 개.

---

## 3. 인물 성경 (흔들리면 80% 실패)

웹툰은 완성형 호스트가 아니라 **파츠**다. 그래서 먼저 **마스터 한 장**을 만든다.

조립 재료 (`parksy-image/웹툰/`):

- 윤곽 `얼굴/윤곽/parksy_face-outline-oval_bd_1024_v001.png`
- 눈 `얼굴/눈/parksy_face-eyes-phoenix_bd_400x200_v001.png`
- 눈썹 `얼굴/눈썹/parksy_face-brow-straight_bd_450x100_v001.png`
- 입 `얼굴/입/parksy_face-mouth-bowup_bd_300x200_v001.png`
- 코 `얼굴/코/parksy_face-nose-straight_bd_200x300_v001.png`
- 머리 `헤어/앞머리` + `옆머리` + `뒷머리` sidepart
- 몸 `몸/상체/parksy_body-torso-front_bd_600x800_v001.png`

출력:

1. `REF_FACE.png` — 정면 얼굴, 16:9 안에 앉힘. 이후 모든 숏의 1번 참조.
2. `REF_BODY.png` — 상반신, 같은 빛.
3. 컷2 화남만 입·눈썹을 anger 파츠로 갈아 `REF_FACE_ANGER.png`.

규칙: 얼굴은 CLI `image_gen` 금지. 웹에 REF_FACE를 **업로드**한 뒤 Photo Edit.  
대사 숏(컷2)은 상주 TTS 정본. 웹 립싱크 약속 안 함.

---

## 4. 본편 샷 리스트 — 55초 · 10숏

화면 16:9. 색 `desaturated_moody`. 렌즈 홍+정.

| ID | 초 | 역할 | 화면 | 카메라 | 소리 |
|----|----|------|------|--------|------|
| S00 | 0–3 | 아이덴트 | 워드마크 「렌즈」+ EAE. **코드로 그린다** | 없음 | 지글 0.4초 (placeholder_neutral) |
| S01 | 3–9 | 공간 | 빈 교실·복도. 사람 작게 | 고정 롱 (정일성) | 룸톤 |
| S02 | 9–15 | 컷1 | 호스트 미디엄, 손 모음, 생각 | **느린 줌인** (hong zoom) | 내레이션 ① |
| S03 | 15–21 | 컷2 | 얼굴 클로즈, 손가락 | 고정 클로즈 | **대사** 보이스 |
| S04 | 21–27 | 도면 | SVG overview를 칠판처럼 | **푸시인** (ken_burns 문장) | 내레이션 없음. 숨 |
| S05 | 27–33 | 컷3 | 복도 걷기 | 옆으로 짧은 팬 | 내레이션 ② |
| S06 | 33–39 | 숨 | 창·의자 빈 자리. 사람 없음 | 고정 | 침묵 0.6초 후 룸톤 |
| S07 | 39–45 | 컷4 | 기대어 클로즈 | 아주 느린 줌인 | 내레이션 ③ |
| S08 | 45–51 | 정면 | 호스트가 카메라를 본다 | 고정 | 내레이션 ③ 마지막 문장 잔향 |
| S09 | 51–55 | 엔드 | 제목 + 「교육편」. **코드** | 없음 | 지글 페이드 |

### 대사 확정 (창고 원문, 안 고침)

- 내레이션 ① S02: 매번 듣는 질문인데, 매번 다르게 들린다.
- 대사 S03: 돈 벌려고요? 시험 때문에요?
- 내레이션 ② S05: 그 아이 말이 맞다. 대부분의 공부는 돈벌이용이 맞다.
- 내레이션 ③ S07–S08: 근데 진짜 공부는 그게 아니다. / 세상이 어떻게 작동하는지 보이기 시작하는 거다.

프롬프트를 내가 지어 바꾸지 않는다. (S21 다큐 계약과 같음)

### 숏별 도구

| ID | 스틸 | 움직임 |
|----|------|--------|
| S00 S09 | HTML/CSS → 캡처 | 안 움직임. 또는 1% 밝기 |
| S01 S06 | **웹 Image 2.0** + 도면 업로드 (CAI) | 웹 비디오 토글 6s |
| S04 | SVG + Burns (상주). 웹 안 부름 | Ken Burns |
| S02 S07 | **웹 Photo Edit** + REF_FACE 업로드 (CAI) | 웹 비디오 토글 6s |
| S05 S08 | 80%는 Burns. A만 웹 | Burns / 웹 |
| S03 | ANGER 파츠 + TTS (상주). 웹 안 부름 | 스틸+TTS |

천장 엔진 = `grok.com/imagine` Image 2.0. CLI `image_gen` 납품 금지. 왕복: `CAI.md`.  
웹 비디오 프롬프트는 한두 문장, 현재형, 카메라 하나.  
예 S02: `A young Korean instructor stands still in a grey classroom, thinking. Slow zoom in, documentary, muted daylight.`

---

## 5. 80% A 체크 (숏마다 통과해야 다음)

스틸

- [ ] 얼굴이 REF_FACE와 같은 사람인가
- [ ] 글자가 그림 안에 깨져 있지 않은가 (깨지면 코드로 다시)
- [ ] 색이 회차 룩인가 (채도 낮음, 앰버-틸 없음)
- [ ] 16:9인가

클립

- [ ] 6초인가 (S00/S09 제외)
- [ ] 동작이 하나인가
- [ ] 얼굴이 흔들리지 않는가
- [ ] 카메라가 표와 같은가

패키지 (80% 납품)

```
out/lens/ep01_why_study/
  REF_FACE.png
  REF_FACE_ANGER.png
  REF_BODY.png
  stills/S00.png … S09.png
  clips/S00.mp4 … S09.mp4
  cards/ident.html  end.html  thumb.html
  shot_bible.json
  README.md          ← 이 프로포절 한 장 요약
```

이 폴더가 있으면 **80% 달성.** 한 편으로 이어 붙인 mp4는 20%.

---

## 6. 20% (나중에, 상주+ffmpeg)

1. `ffmpeg` concat demuxer (`-c copy`)
2. LUT `10_desaturated_moody.cube` 한 번 더 (이미 구운 룩 위에 얇게)
3. 내레이션 더빙 + S03 보이스 레벨
4. `assets/audio/webtoon/emotion/` 지글 → 사이드체인
5. ASS 하단 한 줄 (S21 P4b 스타일 가져오되 페이지캡처는 안 가져옴)
6. 16:9 본편 + 9:16 센터컷
7. 썸네일: `썸네일/유튜브/` 틀에 제목 코드로
8. `@BeingEduartEngineer-4` 업로드

---

## 7. 시즌 (파일럿 다음)

파일럿이 80%를 찍은 뒤.

| 회 | 창고 에피소드 | 렌즈 |
|----|----------------|------|
| ep01 | 학생이 왜 공부해요 (이 장) | 홍+정 |
| ep02 | 오늘 레스토랑에서 손님이 화 | 봉준호 (계급·비대칭) |
| ep03 | 슬프게 걸어가는 박씨, 쟁반 | 고레에다 |
| ep04 | 새벽 3시에 혼자 주방을 닦 | 타르코프스키+고레에다 (`ai_pipeline` 무드) |
| ep05 | **같은 ep01, 렌즈만 왕가위** | 「렌즈 한 과」본편 |

ep05가 시리즈의 존재 이유다. 내용 같고 방송이 다르다.

---

## 8. 촬영 순서 (Go 한 마디면)

**D0 머리 이식 (30분, 상주 가능)**  
`eae-video/curator/` 로 YAML 11 + moods만. 3183 복사 금지.  
파일럿 재료 pull: 위 얼굴/몸 파츠 + `도면/svg/학생이_왜_공부해요_하고_물_*.svg` + 컷 JSON 4.

**D1 기준 장**  
REF_FACE / ANGER / BODY. 네가 얼굴 OK 할 때까지.

**D2 스틸 10장**  
S00·S09는 HTML. 나머지 8은 edit.

**D3 클립 10개**  
S03만 r2v. 체크리스트 통과한 것만 남김.

**D4 패키지**  
`shot_bible.json` + thumb HTML. **여기서 80% 마감.**

**D5+** ffmpeg 생기면 20%.

---

## 9. 네가 지금 줄 것 / 안 줘도 되는 것

주면 빨라짐

- 보이스 하나 (r2v 프리셋 이름, 또는 「네가 골라」)
- REF 얼굴 OK / 다시
- S-Pen으로 「이 교실」스케치가 있으면 S01이 산다

안 줘도 됨

- 대본 (창고에 있음)
- Comfy 워크플로
- 3183 전체
- 누나 얼굴 (이 회차 안 씀)

---

## 10. shot_bible.json 초안 스키마

```json
{
  "id": "lens_ep01_why_study",
  "series": "렌즈",
  "chapter": "교육편",
  "title": "학생이 왜 공부해요 하고 물었다",
  "duration_s": 55,
  "aspect": "16:9",
  "lens": ["hong_sangsoo", "jung_ilseong"],
  "lut": "10_desaturated_moody",
  "source": "own_storyboard",
  "ref_composition": "parksy-image 도면+컷JSON",
  "publish": "private",
  "quality_bar": "80-of-A",
  "shots": []
}
```

숏 객체: `id, t0, t1, still, clip, tool, camera, dialogue, narration, audio, pass`.

---

*프로포절 · 찍으라면 D0부터. 고칠 테면 렌즈·보이스·회차만 말해라.*
