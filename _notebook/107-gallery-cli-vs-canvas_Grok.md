---
date: 2026-08-28
agent: Grok
mark: _Grok
type: inventory
location: s25-ultra
---

# 갤러리 CLI vs 웹 캔버스 — 처리 가능·품질 층

> S25 갤러리 사진을 이 CLI에서 처리해 저장소에 되돌릴 수 있는지, 웹/PC Imagine 캔버스와 품질이 얼마나 다른지 실측과 공식 입구를 잠근다. 책상 원본: `_notebook/grok/GALLERY-CLI.md`.

## 한 줄

```
갤러리 왕복: 됨.
픽셀 = 같은 Imagine 집. 큰 구멍 = 손.
SKU가 2.0이 아니면 픽셀도 한 체급. 같은 장 A/B는 아직 없음.
```

## 갤러리 파이프 (실측)

이 CLI = S25 Ultra SM-S938N. `/sdcard` bind **rw**. write test OK. `termux-media-scan` 있음.

| 저장소 | 실측 |
|--------|------|
| `DCIM/Camera` | 있음 |
| `Pictures/` | 있음 |
| `Download/` · `grok-cross/` | 있음 |
| 원본 | 안 덮음. 새 파일 |

```
원본 /sdcard/…  →  image_edit  →  Pictures/ 또는 Download/grok-cross/
                →  termux-media-scan  → 갤러리
```

## 품질 두 층

| 층 | 이 CLI | 웹/PC 캔버스 |
|----|--------|----------------|
| 엔진 | Imagine `image_gen`/`image_edit` | Imagine Quality = Image 2.0 |
| SKU 선택 | 도구에 칸 없음. 소스 기본 `grok-imagine-image-quality` | `grok-imagine-image-2.0` |
| 통짜 한 장 | 됨 | 됨 + 영역 |
| 마스크·Magic Wand·슬라이더 | 없음 | 여기만 |
| 배치·그리드·포스터 글자 | 깨지기 쉬움 | 캔버스 본업 |

`@grok`: 코어 생성·Quality·참조는 앱=웹. 고급 캔버스만 데스크톱.

## 18개 중 CLI

| CLI로 비슷 | CLI가 짐 |
|------------|----------|
| Reimagine, 배경, 이커머스, 프로필, 히어로, 상품색, UGC, 헤드샷, 룸, 마스코트 | Photo Edit 부분, Smart Resize, Collage, Sprite, Editorial 글자, Icon, Props & UI Kit |

18 전부 웹만큼이라고 말하면 과장. 칸 지정·A/B는 아직 없음.

관련: [`106-imagine-canvas-18_Grok.md`](106-imagine-canvas-18_Grok.md) · [`grok/CANVAS.md`](grok/CANVAS.md) · [`grok/CAN.md`](grok/CAN.md)

- [x] 갤러리 rw · media-scan 실측
- [x] 품질을 모델/손으로 갈라 저장
- [ ] 같은 장 A/B
- [ ] 18 중 쓸 칸

*agent mark `_Grok` · 2026-08-28*
