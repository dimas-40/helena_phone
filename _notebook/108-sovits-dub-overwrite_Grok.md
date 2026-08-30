---
date: 2026-08-24
agent: Grok
mark: _Grok
type: challenge
location: tablet
status: open
boss: true
---

# 챌린지 — Grok 영상에 SoVITS 성우 덮어쓰기 (2026-08-24)

> **Boss:** 「너 이거 업무 수첩에다 저장해. 이거 챌린징해서 작업할 거야.」  
> 말한 형식: 그록이 만든 샘플에서 텍스트 대사를 추출하고 타이밍을 뺀 다음, 그 정보에 맵핑해서 **성우 더빙을 오버라이트**한다.

책상 카드: `_notebook/grok/DUB-OVERWRITE.md`  
샷리스트: `_notebook/grok/SHOT-HOST-01-STORY.md`  
샘플: `output/lens-pilot/host01-gest-40s.mp4`  
타이밍: `output/lens-pilot/host01-gest-40s.timing.json`  
손: `scripts/dub_overwrite.sh`

---

## 0. 한 줄

```
그록 = 얼굴·입·제스처·배경. 소리는 버린다.
샷리스트 = 대사 원본. STT는 검수.
ffmpeg silencedetect = 입이 쉬는 칸.
SoVITS wav를 그 칸에 깔고 영상은 copy.
웹에서 성우 교체 불가. CLI+이 프로트 ffmpeg.
```

이게 칸 ②(10초 다큐)의 **목소리 레인**이다. 그록 프리셋 `leo`는 파일럿 자리표시.

---

## 1. 왜 챌린지인가

- 그록 `voices=` / 웹 Video 1.5는 **xAI 프리셋**만. SoVITS 경로를 안 받는다.
- 같은 글을 입이랑 SoVITS가 읽게 해서 **대략** 맞춘다. 프레임 립싱크는 약속 아님.
- 이 탭에 ParksyTTS 가중치 없음 (models/ 370KB wav뿐). SoVITS 추론은 S21(또는 가중치 있는 방).
- 붙이기는 **여기 proot ffmpeg** (8.0.1 실측). 「탭에 ffmpeg 없음」은 폐기.

---

## 2. 이미 있는 것 (시작선)

| 것 | 경로 |
|----|------|
| 정장 REF | `/sdcard/Download/REF_HOST_SUIT.jpg` |
| 제스처 40초 (4×10s) | `output/lens-pilot/host01-gest-40s.mp4` |
| 발화/침묵 맵 | `output/lens-pilot/host01-gest-40s.timing.json` |
| 덮기 스크립트 | `scripts/dub_overwrite.sh <mp4> <wav>` |
| 보고 | `@dtslib_tablet_bot` |

S01 실측 예: 10초 안에 발화 4덩이, 침묵 0.6–1.1초. 그 쉼을 살려야 손·입이 안 깨진다.

---

## 3. 챌린지 작업 순서

1. 샷리스트 글은 고치지 않는다 (`SHOT-HOST-01-STORY.md`).
2. `timing.json` 발화 구간마다 SoVITS wav. 탭이 아니라 **가중치 있는 방**.
3. `atempo`로 칸 길이에 맞춤 (0.9–1.15만. 그 밖이면 글을 줄이거나 숏을 다시).
4. `bash scripts/dub_overwrite.sh output/lens-pilot/host01-gest-40s.mp4 parksy.wav`
5. 검수: 침묵 칸에 말이 새지 않는지. 입 대략.
6. `@dtslib_tablet_bot` 보고.

---

## 4. 안 하는 것

그록 `voices=`에 SoVITS. 웹 Imagine에서 성우 교체. 이 탭에서 ParksyTTS 7분 추론. 웨이브립을 이번 챌린지 성공 조건으로 걸기.

---

## 5. 성공

`host01-gest-40s.dub.mp4` — 화면은 그록 제스처판, 목소리는 박씨 SoVITS, 40초 concat 유지, 텔레그램 1회.

*챌린지 원장 · `_Grok` · 2026-08-24*
