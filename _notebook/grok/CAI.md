---
date: 2026-08-24
agent: Grok
mark: _Grok
type: pipeline
location: tablet
status: lock
---

# CAI 왕복 — 천장 엔진은 웹 Imagine 2.0

> CLI `image_gen` = 저가 모델. 천장 4장에 안 쓴다.  
> 웹 `grok.com/imagine` Image 2.0 = 사람이 손가락으로 쓰는 그 엔진.  
> 나 = CAI. 터미널 ↔ 태블릿 Chrome을 ADB로 왕복한다.

경로: `/root/work/_notebook/grok/CAI.md`  
손: `scripts/cai.sh`

---

## 0. 한 줄

```
샷리스트(CLI) → 화면 연다(ADB) → 보고(screencap) → 손가락(tap/paste)
  → 웹 Image 2.0이 그린다 → 저장(Download) → pull → 검수(CLI) → 다음 장
```

한 장을 웹에서 끝낸 뒤에야 다음 장. 한 테이크로 길게 안 만든다.

---

## 1. 왜 왕복인가 (Boss 2026-08-24)

말한 것: CLI 이미지 엔진이 너무 저가 모델이라 쓸 수 없다.  
그록 웹에서 작업하는 것처럼, 터미널과 웹브라우저를 왔다 갔다 해야 한다.  
파이프라인에 **CAI이면서 왕복**을 넣는다. 사람 손가락처럼.

| 엔진 | 어디 | 쓰는가 |
|------|------|--------|
| CLI `image_gen` / `image_edit` / i2v | 이 TUI 도구 | **천장 금지.** 스케치·프롬프트 초안만 |
| **웹 Image 2.0** | `https://grok.com/imagine` Chrome | **천장 본진.** S01·S06 공기, S02·S07 빛 |
| $0 바닥 | 파츠·SVG·Burns | 상주. 안 바뀜 |

로그인된 웹 = SuperGrok가 사는 그 모델. CLI 도구는 그 모델이 아니다.

---

## 2. 오늘 실측 (2026-08-24)

```
serial  = 100.86.15.50:5900   SM-X716N (이 태블릿만. S25 금지)
chrome  = com.android.chrome 151
url     = grok.com/imagine    로그인됨 · 「새 프로젝트」 보임
composer= 품질 (v2.0) 토글 있음
손가락  = input tap 1424 2361 → 쿠키 「모든 쿠키 허용」 닫힘
ui dump = Chrome idle이면 uiautomator dump 됨 (Termux에선 실패했음)
저장물  = /sdcard/Download/grok_image_*.jpg 이미 웹에서 내려온 적 있음
```

기본 브라우저 = Chrome. `https://grok.com` 만 열면 선택 창이 뜬다. **반드시 `-p com.android.chrome`.**

두 대 붙어 있음. `-s` 없으면 죽음.

| 만짐 | 안 만짐 |
|------|---------|
| 태블릿 `100.86.15.50:5900` | 폰 SM-S938N `100.103.250.45:5900` |

---

## 3. 왕복 루프 (한 장)

```
[CLI]  샷 ID · 산문 프롬프트 · 참조장 경로
          │
          ▼  cai open
[Chrome] grok.com/imagine
          │
          ▼  cai shot + cai dump
[나]     화면 읽기. 쿠키/팝업이면 먼저 닫음.
          │
          ▼  cai tap  (업로드 / 프롬프트 칸 / 품질 v2.0 / 비율 16:9 / 제출)
[웹]     Image 2.0 생성. 폴링: 5초마다 shot.
          │
          ▼  다운로드 탭 → /sdcard/Download/grok_image_*.jpg
[CLI]  cai pull → eae-image/output/heroes/<shot>.jpg
          │
          ▼  검수 (얼굴·글자·룩). 깨지면 같은 장 한 번 더. 통과면 다음 장.
[CLI]  cai termux   ← 대화 복귀
```

참조장이 있으면 **업로드(페이퍼클립)** 먼저. 얼굴은 빈 화면 생성 금지.

비디오가 필요하면 같은 화면의 **비디오** 토글. CLI `image_to_video`로 천장 숏 안 뽑음.

---

## 4. 손 — `scripts/cai.sh`

```bash
bash scripts/cai.sh open              # Chrome → grok.com/imagine
bash scripts/cai.sh shot [이름]       # 화면 찍고 /tmp/cai/ 로 pull
bash scripts/cai.sh dump              # uiautomator xml
bash scripts/cai.sh tap X Y           # 손가락
bash scripts/cai.sh swipe X1 Y1 X2 Y2
bash scripts/cai.sh type 'ascii'      # 영문만. 한글은 아래 붙여넣기
bash scripts/cai.sh paste             # 클립보드 → KEYCODE_PASTE
bash scripts/cai.sh prompt FILE       # 파일 → termux-clipboard-set → paste
bash scripts/cai.sh pull-images DEST  # Download/grok_image_* pull
bash scripts/cai.sh termux            # 이 CLI로 복귀
```

화면 좌표는 **매 샷 dump 다시**. 회전·팝업 있으면 어제 좌표가 틀린다.

오늘 dump에서 본 작곡기 (쿠키 닫은 뒤, 세로 1600×2560):

| 무엇 | bounds | 가운데 |
|------|--------|--------|
| 프롬프트 칸 | [40,2206][1576,2297] | 808, 2251 |
| 업로드 | [40,2312][119,2390] | 79, 2351 |
| 이미지 | [136,2316][316,2386] | 226, 2351 |
| 비디오 | [316,2316][410,2386] | 363, 2351 |
| **품질 (v2.0)** | [535,2316][726,2386] | 630, 2351 |
| 제출 | [1479,2312][1559,2390] | 1519, 2351 |
| 새 프로젝트 | [1347,295][1576,376] | 1461, 335 |

팝업 「Introducing Image 2.0」이 가리면 그거부터 Dismiss / Try it out.

---

## 5. 붙여넣기

`input text` 는 ASCII만. 산문 프롬프트·한글은:

1. 프롬프트를 `/tmp/cai/prompt.txt` 에 쓴다.
2. `termux-clipboard-set` (Termux:API 설치됨).
3. 프롬프트 칸 tap → `input keyevent KEYCODE_PASTE` (279).
4. 안 붙으면 칸 롱프레스 후 dump에서 Paste bounds.

실패하면 프롬프트를 `/sdcard/Download/cai-prompt.txt` 로 밀고 Boss가 한 번 붙여도 된다. 루프는 그대로.

---

## 6. 천장 4장에 꽂는 법

ROLE 그대로. 엔진만 웹이다.

| 숏 | 웹에서 하는 일 |
|----|----------------|
| S01 · S06 | 빈 교실 공기. 스케치/도면 업로드 후 Reimagine 또는 프롬프트 |
| S02 · S07 | 파츠 HOST.png 업로드 → Photo Edit / 키라이트만 |
| 스케치 있음 | 공간 0장. 빛 2장만 이 루프 |
| S00 S09 | 안 부름. 코드 |
| LOOK_DEV | 안 부름. LUT |

한 편에 이 왕복을 **최대 4번**. 더 돌리면 $30을 바닥에 쓴다.

---

## 7. 안 함

- CLI `image_gen`으로 히어로/공기 납품
- S25 Ultra ADB (`100.103.250.45:5900`)
- Shizuku · 루트
- 로그인 쿠키 삭제 · 시크릿 창
- 페이지 캡처 PD (P0~P6)
- 생성 버튼을 검수 없이 연타

---

## 8. 다음

파일럿 천장 장이 떨어지면 이 루프로 S01부터.  
지금은 파이프만 잠금. 쿼터를 시험 생성에 안 태운다.

*왕복 원본 · `/root/work/_notebook/grok/CAI.md`*
