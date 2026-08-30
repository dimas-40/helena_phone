---
date: 2026-08-24
agent: Grok
mark: _Grok
type: pipeline
location: tablet
status: challenge-open
---

# 성우 덮어쓰기 — Grok 영상은 몸, SoVITS는 목소리

Boss 2026-08-24: 「저장해. 챌린징해서 작업할 거야.」  
원장: `_notebook/108-sovits-dub-overwrite_Grok.md`

## 한 줄

```
그록 = 얼굴·입·제스처·배경 숨. 소리는 버린다.
샷리스트 = 대사 원본 (영상에서 STT로 원본을 만들지 않음).
ffmpeg silencedetect = 그 숏 안에서 입이 쉬는 칸.
SoVITS wav를 그 칸에 맞춰 깔고, 영상 트랙은 copy.
```

가능. 웹이 아니라 **이 프로트 CLI+ffmpeg**가 맞는 자리.

## 왜 추출이 원본이 아닌가

영상 속 그록 성우(leo)는 샷리스트를 **읽은 결과**다.  
글은 이미 `SHOT-HOST-01-STORY.md`에 있다. STT는 검수일 뿐.

타이밍은 추출이 이긴다. 같은 글이라도 그록이 쉼을 넣는 위치가 숏마다 다르다.  
제스처판 40초 실측: 10초 안에 발화 4덩이 + 침묵 0.3–2.1초. 그 침묵을 살려야 입·손이 안 어긋난다.

맵: `output/lens-pilot/host01-gest-40s.timing.json`

## 덮는 법

```
1) 샷리스트 글 + timing.json 발화 구간
2) SoVITS가 그 글 → wav  (이 탭엔 가중치 없음. S21 또는 가중치 있는 방)
3) atempo로 발화 칸 길이에 맞춤 (너무 늘리면 깨짐. 0.9–1.15)
4) ffmpeg:
     -i host01-gest-40s.mp4 -i parksy.wav
     -map 0:v -map 1:a -c:v copy -shortest
   그록 aac는 버림.
```

입 모양은 **같은 글을 읽게 해서 대략**. 프레임 립싱크 약속 아님.

## 안 하는 것

그록 `voices=`에 SoVITS 경로. 웹에서 성우 교체. 이 탭에서 ParksyTTS 추론.
