---
date: 2026-08-28
agent: Grok
mark: _Grok
type: inventory
location: s25-ultra
status: measured
---

# 갤러리 CLI 처리 vs 웹 캔버스 품질

> Boss: 갤러리 사진을 이 CLI에서 처리해 저장소에 다시 넣을 수 있다. 여기 모델과 웹/PC 캔버스 품질 차이가 크겠냐.
> 번호 수첩: `_notebook/107-gallery-cli-vs-canvas_Grok.md`

## 한 줄

```
갤러리 → 이 CLI → 저장소: 됨 (실측).
픽셀이 하늘과 땅은 아님. 큰 구멍은 손(영역·배치·18템플릿 UI).
SKU가 Image 2.0이 아니면 픽셀도 한 체급 아래일 수 있음. 같은 장 A/B는 아직 안 찍음.
```

## 갤러리 파이프 (2026-08-27 이 기기 실측)

이 CLI = S25 Ultra SM-S938N proot. `/sdcard` bind **rw**.

| 경로 | 상태 |
|------|------|
| `/sdcard` | bind rw. write test OK |
| `DCIM/Camera` | 있음 (예: Dog_094821.jpg) |
| `Pictures/` | 있음 (png 다수) |
| `Download/` | 있음. `grok-cross/` 있음 |
| `termux-media-scan` | PATH에 있음 |
| 원본 덮어쓰기 | 안 함. 새 파일로 저장 |

흐름:

```
/sdcard/DCIM|Pictures|Download  원본
        → image_edit (경로 그대로)
        → /sdcard/Pictures/ 또는 /sdcard/Download/grok-cross/
        → termux-media-scan  → 갤러리에 다시 뜸
```

장 지정 오기 전엔 아무 사진도 안 돌림.

## 품질 — 두 층

| 층 | 이 CLI | 웹/PC 캔버스 |
|----|--------|----------------|
| 엔진 집 | Imagine `image_gen` / `image_edit` | Imagine Quality Mode = **Image 2.0** |
| 모델 ID 고름 | 도구에 SKU 칸 없음 | 화면 Quality / 템플릿 |
| 소스 기본값 (grok-build) | `grok-imagine-image-quality` | `grok-imagine-image-2.0` |
| 한 장 통짜 바꾸기 | 됨 | 됨 + 영역 |
| 마스크 · Magic Wand · Segmentation · 슬라이더 | 없음 | 여기만 |
| Smart Resize · 콜라주 배치 · 스프라이트 그리드 · 포스터 글자 | 통짜라 깨지기 쉬움 | 캔버스가 그 일 하려고 만든 도구 |

공식 `@grok`: 앱·웹 **코어 생성·Quality·참조**는 같고, **고급 캔버스(배치·선택·멀티클립)**만 데스크톱.

## 18개 템플릿 — CLI로 어디까지

**프롬프트 통짜로 비슷하게 굴릴 수 있는 것:** Reimagine, BG Removal & Change, E-Commerce Photos, Profile Picture, Hero Product Reveal, Product Color Change, UGC Photos, Professional Headshot, Room staging, Mascot Maker, Photo Edit-ish(밝기 문장).

**여기서 지는 것:** Photo Edit 부분 보정, Smart Resize, Photo Collage, Character Sprite, Editorial Product Poster 글자, Icon Maker, Props & UI Kit. 모델이 나빠서가 아니라 영역·배치·글자 UI가 없어서다.

18개 전체가 CLI에서 웹만큼 나온다고 말하면 과장.

## 안 한 것

- 같은 장 CLI vs 캔버스 A/B
- 원본 덮어쓰기
- 18개 중 쓸 칸 지정 (Boss 아직 안 말함)

*원본 · `/root/work/_notebook/grok/GALLERY-CLI.md`*
