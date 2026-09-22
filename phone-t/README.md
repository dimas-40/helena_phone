# Phone T — 폰 안에서 도는 편집 라인 (컨테이너의 원본)

> **한 줄:** 화면녹화 raw → 유튜브 규격 mp4. 도커 없이, 클라우드 없이, **이 폰 안에서** 끝난다.
> 컨테이너 `po-edit-cell` 의 **백업 플랜**이고, 동시에 그 컨테이너의 **원본**이다.

작성 2026-09-22 · `_Claude`

---

## 1. 왜 이게 있나 (예비 전력)

`po-edit-cell` 은 같은 도구를 컨테이너로 구운 것이다. 그런데 컨테이너는
**레지스트리가 살아 있어야** 돌고, **받아야** 돌고, **PC 가 있어야** 돈다.

폰은 그 셋이 전부 필요 없다. 그래서 이 라인은:

| 상황 | 컨테이너 | Phone T |
|---|---|---|
| 오프라인 | ✗ (pull 불가) | ✓ |
| GHCR 장애 | ✗ | ✓ |
| PC 없는 사람에게 주기 | ✓ (curl 2줄) | ✓ (파일 1개 복사) |
| 상시 가동 | ✗ | ✓ |

**둘이 같은 파일을 쓴다.** 그래서 "컨테이너가 죽으면 폰으로" 가 성립한다.

---

## 2. 알맹이는 파일 하나다

```
scripts/yt_edit.py     ← 이게 전부다. python3 표준 라이브러리 + ffmpeg CLI 만 쓴다.
scripts/phonet.sh      ← 껍데기(진입점). 없어도 python3 yt_edit.py 로 돌아간다.
```

**컨테이너와 폰의 차이는 이거뿐이다:**

```
컨테이너 =  python:3.12-slim  +  ffmpeg  +  이 파일
폰       =  (이미 있는) python3 + ffmpeg  +  이 파일
             ↑ pip 설치 0건. requirements.txt 없음. 추가 패키지 없음.
```

즉 **컨테이너를 다시 만들려면 이 파일을 그대로 넣으면 된다.** 다른 걸 넣으면 그건 다른 도구다.

---

## 3. 컨테이너가 반드시 똑같이 맞춰야 하는 값

이 값들은 **추측이 아니라 실측·기존 자산에서 온 출처가 있는 값**이다.
바꾸려면 여기도 같이 바꿔야 한다 (`scripts/yt_edit.py` 상단).

| 값 | 값 | 출처 |
|---|---|---|
| `TOP_CUT` | `0.090` | 앱스토어 PWA `lecture-long/app.js:64` `devices.S25_ULTRA.topCutPct` |
| `BOTTOM_CUT` | `0.040` | 같은 곳 `bottomCutPct` |
| `TARGET_LUFS` | `-14.0` | YouTube 정규화 목표 (미리 맞춰야 재인코딩 손실이 줄어든다) |
| `TRUE_PEAK` / `LRA` | `-1.5` / `11.0` | loudnorm 표준 |
| `VIDEO_ENCODER` | `libx264` | |
| `PRESET` / `CRF` | `veryfast` / `18` | CRF 23 은 **화면 글자가 뭉갠다** — 강의는 글자가 본체다 |
| `MAX_FPS` | `60.0` | 120fps 녹화는 강의에 과하다. 프레임만 2배, 화질 이득 0 |
| `AUDIO_BITRATE` / `AUDIO_RATE` | `192k` / `48000` | |
| `BG_BLUR` / `BG_DARK` | `40` / `0.18` | 배경 블러 강도·어둡기 |

레인 3종 (`LANES`) — 이름 하나로 캔버스·크롭·배경이 전부 결정된다:

| 레인 | 캔버스 | 푸터 | 쓰임 |
|---|---|---|---|
| `lecture` | 1920x1080 | `dtslib.kr` | 강의. 세로녹화를 가운데 놓고 좌우를 블러로 채움 |
| `tour` | 1920x1080 | `dtslib.kr` | 웹앱 투어 |
| `narration` | 1080x1920 | (없음) | 쇼츠·릴스. 크롭해서 꽉 채움 |

---

## 4. ⚠️ 컨테이너에 아직 살아 있는 버그 — 이식할 때 반드시 같이 가져갈 것

**2026-09-22 발견. 컨테이너 안의 `yt_edit.py` 는 아직 고쳐지지 않았다.**

삼성 화면녹화기는 **VFR**(가변 프레임레이트)이다. 컨테이너가 선언하는 값은
`r_frame_rate=60/1` 인데, 실제 프레임 간격은 `avg_frame_rate = nb_frames/duration` 이다.
실측한 파일에서는 **82.73fps** 였다.

예전 코드는 컷을 지우고 `setpts=N/FRAME_RATE/TB` 로 이어붙였다.
`FRAME_RATE` 는 *선언값 60* 이라, 프레임 N 을 N/60초 자리에 놓는다.
그런데 실제 간격은 1/82.73초 → **영상이 소리보다 훨씬 빨리 흘러간다.**

> 실측 피해: 44.40초 오디오에 **62.10초 영상**. **17.7초 어긋남.**

**고친 방법 — fps 를 두 개로 나눈다:**

```python
nominal = _rate(video.get("r_frame_rate"))     # 60.0  → 인코딩 출력 fps
average = _rate(video.get("avg_frame_rate"))   # 82.73 → 컷 이어붙일 때 쓸 간격
retime  = average if average > 0 else nominal
```

```python
vf = f"select='{keep}',setpts=N/{retime_fps:.6f}/TB"   # ← average 를 쓴다
af = f"aselect='{keep}',asetpts=N/SR/TB"
```

출력 fps 는 여전히 `fps=60` 필터로 맞춘다 (이 필터는 타임스탬프를 알고 있어서
알아서 복제/드롭한다). **`-r 60` / `-fps_mode cfr` 를 출력 옵션으로 주는 건 안 된다** —
그건 타임스탬프를 모른 채 개수만 세므로 같은 버그가 난다.

**고친 뒤 실측:** 영상 44.38초(2663프레임) / 소리 44.40초 — **오차 0.02초, 컷도 적용됨.**

### 그리고 하나 더 — `select` 만 쓰고 `setpts` 를 빼면 컷이 조용히 무시된다

`setpts=PTS-STARTPTS` 는 동기화는 맞지만 **간격을 메우지 않는다**.
`select` 가 남긴 구멍이 그대로 남아서, 컷이 안 먹은 것처럼 보인다.
**`setpts=N/{retime_fps}/TB` 여야 둘 다 된다.** (실패 → 성공 → 최종, 두 번 갈아엎었다.)

---

## 5. 배경 블러는 **한 장만** 만든다

세로녹화를 16:9 캔버스에 올리면 좌우가 남는다. 그걸 매 프레임 블러하면 낭비다 —
**뒤가 안 변하는데 매번 다시 계산하고 있었다.**

```
매 프레임 블러 : 15초 편집 = 38초
한 장 만들어 재사용 : 15초 편집 = 12초     ← 2026-09-22 S25 Ultra 실측
```

구현은 `make_backdrop()` — 첫 프레임 한 장을 블러·어둡게 해서 `bg.png` 로 굽고,
`-loop 1 -i bg.png` 로 깔고 그 위에 영상을 `overlay` 한다.

---

## 6. 쓰는 법

```bash
# 어디서든 `phonet` 한 마디로 (symlink 걸어 뒀다 — 실측 확인함)
phonet --quick lecture "/sdcard/DCIM/Screen recordings/xxx.mp4"

# ① job JSON — 테이크 여러 개·컷·챕터를 다 쓰려면 이쪽
phonet job.json
phonet job.json --dry-run                     # 인코딩 없이 계획만

# ② 빠른 모드 — 파일 하나를 레인에 태운다
phonet --quick lecture "/sdcard/DCIM/Screen recordings/xxx.mp4"
phonet --quick narration "/sdcard/.../xxx.mp4" /sdcard/Download/out.mp4
#  (안 걸려 있으면 bash scripts/phonet.sh ... 로 똑같이 된다)
```

job JSON 스키마 (예시는 `phone-t/job.example.json`):

```json
{
  "output": "/sdcard/Download/final.mp4",
  "lane": "lecture",
  "overlay": "Phone T",
  "footer": "dtslib.kr",
  "takes": [
    {"file": "take1.mp4", "title": "1. 문제 제기", "cuts": [[12.5, 18.0]]},
    {"file": "take2.mp4", "title": "2. 방법",     "cuts": []},
    {"file": "take3.mp4", "title": "3. 마무리",   "cuts": [[3.0, 9.2]]}
  ],
  "loudness": -14.0
}
```

- `cuts` 는 **그 테이크의 원본 타임라인** 기준 초. 뒤 컷이 앞 컷에 영향받지 않는다.
- 챕터 타임스탬프는 컷 반영 후 **출력 타임라인**으로 자동 계산돼 `.chapters.txt` 로 나온다.
- 테이크 경계 = 챕터 경계 = 모듈 경계 = 광고 브레이크. **넷이 같은 자리다.**

---

## 7. 한계 (정직하게)

- **앱 자체 UI 는 못 지운다.** 크롭이 지우는 건 시스템 상태바·내비바뿐이다.
- **한글 제목은 지금 안 나온다.** drawtext 는 폰트가 있어야 그리는데 폰에 한글 폰트가 없다.
  **그리고 없는 글자는 오류 없이 조용히 안 그려진다** — 실패를 눈치채기 어렵다.
  영문(`Phone T`, `dtslib.kr`)은 정상 렌더 확인했다. 한글을 쓰려면 폰트를 먼저 넣어야 한다.
- **컨테이너가 더 나은 건 폰트다.** `python:3.12-slim` 에는 fontconfig 조차 없다.
  컨테이너에 한글 폰트를 안 넣으면 컨테이너도 똑같이 조용히 안 그린다.
- 하드웨어 인코더(`h264_mediacodec`)는 **proot 에서 무한 대기**한다. `libx264` 로 간다.

---

## 8. 재현·검증한 것 (2026-09-22)

| 항목 | 결과 |
|---|---|
| 도구 단독 실행 (`--help`) | exit 0 — 컨테이너 없이 폰에서 돈다 |
| A/V 어긋남 버그 | 재현 62.10s vs 44.40s → 수정 44.38s vs 44.40s |
| 레인 출력 | 1920x1080, 44.366667 / 44.400000, 7.6MB, **프레임 눈으로 확인** |
| 빠른 모드 (`--quick lecture`) | 6.0s 입력 → 1920x1080 CFR 60, 영상 6.022333 / 소리 6.022333, 0.8MB |
| 폰 MCP 6종 | 8015·8016·8018·8020·8023·8789 전부 HTTP 200 |

---

## 9. 아직 안 된 것

- **컨테이너 안의 `yt_edit.py` 는 아직 예전 코드다.** (VFR 버그 + 레인 없음)
  원격: `dtslib1979/parksy-image` → `cell/services/edit/yt_edit.py`
  → 이 폰의 `scripts/yt_edit.py` 를 그대로 올려야 같아진다.
- 컨테이너 이름 변경은 Boss 결정 사항 (GHCR 에 rename 기능이 없다 — 새 이름으로 다시 push 해야 한다).
- `po-edit-cell` 앱스토어 등록은 다른 세션이 동시에 편집 중이다.
