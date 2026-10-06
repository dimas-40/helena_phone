# 124. 박씨 렌더링 채널 — 1호 완성, 그리고 42호 레시피

> 2026-10-06 · `_Claude`
> 계기: Boss — "42개를 YouTube에서 받아 쌀만데르로 렌더링 하면서 그 음원과 같이 이어 붙여 가지고,
> 각각 역사적 배경·평가·허세용 코멘트·플루치크 매칭 이유까지 넣어서 웹페이지를 만들어"
> 산출물: `music-channel/01-satie-gymnopedie/` (음원 + 웹페이지)
> 앞 문서: `_notebook/122-pd-piano-emotion-map_Claude.md` (소재 지도) · `123-bgm-emotion-master_Claude.md` (마스터)

---

## 0. 한 줄

**원곡 연주와 우리 재현을 한 트랙에 이어 붙이고, 그 6분에 맞춰 스토리텔링하는 웹페이지.**

`music-channel/01-satie-gymnopedie/`
```
index.html          30KB — 역사·평가·감정·약자사전·타임라인 17지점
audio/combined.mp3  8.4MB — 원곡 183.6s + 침묵 2s + 재현 186.0s = 371.6s
img/                5장, 1400px 이하로 축소 (원본 16MB → 202KB)
```

---

## 1. 1호 실측 — 짐노페디 제1번

| 항목 | 값 |
|---|---|
| 원곡 연주 | Robin Alciatore, piano · Wikimedia Commons **Public domain** · 183.59s |
| 채보 | `piano_transcription_inference` · RAW 472음 · 83.5 BPM · D4 major · 180.6s |
| 렌더 | 랩탑 + Salamander Grand Piano V3 · 잔향 0.85 · 딜레이 190ms · loudnorm −16 LUFS |
| 합본 | 원곡 loudnorm(2패스) → 침묵 2초 → 재현 · **−15.9 vs −15.7 LUFS** |
| 채보 소요 | 9분 (183초 음원, CPU 553%) |

⚠️ **1호의 렌더 엔진을 지금 검증할 수 없다.** 이 표는 원래 "fluidsynth"라고 적었는데,
2026-10-06에 랩탑에 들어가려니 SSH 키가 거부됐다(`Permission denied (publickey,password)`) —
`~/tmp/sal/run.sh` 를 직접 볼 수 없었다. **2호는 sfizz_render 인 게 확실**하고(내가 돌렸다),
1호는 기록(이 표)만 남았다. 확증 없이 "fluidsynth였다"고도 "sfizz였다"고도 못 쓴다.
**다음에 랩탑 들어갈 때 `~/tmp/sal/run.sh` 와 `build2.log` 로 확정할 것.** 그때까지
1호 공개 페이지의 엔진 표기는 손대지 않는다(모르는 걸 고치면 그것도 거짓말이다).

### PD 레인 규칙 재확인 — RAW 그대로, 그리고 **사후 증명**

`--no-mono --grid 0 --keep-raw` 로 돌렸지만 **조 정렬은 걸렸다** (43음 이동).
최종적으로 **RAW를 렌더**했다 (노트북 121 §6.5: PD 레인은 손대지 않은 채보).
`gymnopedie.mid`(조 정렬판)도 렌더해뒀다 — Boss가 원하면 교체.

RAW와 조정렬의 차이는 **스케일 밖 음 43개**(C 30 · F 13)다. 처음엔 "귀로만 판정 가능"이라고
적었는데, **원본 파형을 FFT로 재서 판정했다** — 그리고 RAW가 맞았다.

#### 결말이 증거다 — 이 연주는 라단조로 끝난다

마지막 화음(176.80s~)의 스펙트럼:

| 주파수 | 에너지 | 음 |
|---|---|---|
| 73.1 Hz | 31.0 dB | D2 |
| 110.0 | 42.3 | A2 |
| 293.8 | 37.7 | D4 |
| **350.0** | **46.8** | **F4** ← 이 화음에서 가장 센 배음 |
| 366.9 | 23.0 | F#4 ← **24dB 아래** |
| 440.8 | 42.4 | A4 |

→ **D·F·A = 라단조.** 직전 화음(173.20s~)은 A2·C4·E4·G3 = **A단조7**.
즉 **Am7 → Dm**, 곡은 장조로 시작해 **단조로 끝난다.**

**그리고 조 정렬이 이걸 지운다.** D장조 스케일에 파(F)가 없으니 마지막 화음의 F4를
E4로 옮긴다 — 라단조가 "라·미·라"라는 어정쩡한 화음이 된다. RAW 파일에는 F4가 살아 있다.
재현 렌더도 확인: **F 51.2dB / F# −0.6dB.** 같은 라단조.

⚠️ 귀로 못 듣는 내가 "어느 쪽이 맞는지 모른다"고 넘겼으면 **웨이브에서 5분이면 끝날 일**이었다.
**소리 문제는 소리를 재서 푼다.** 렌더 엔진이 바뀌어도 이 측정법은 남는다.

#### 부수 확인 — 시소의 정체
저음 블록(다음 저음까지)마다 화음을 모으면 딱 두 개다:
**G장조7 (G·B·D·F#)** ↔ **D장조7 (D·F#·A·C#)**. 곡 전체가 이 왕복이다.

---

## 1.5 2호 — 바흐 프렐류드 C장조 BWV 846 (2026-10-06)

| 항목 | 값 |
|---|---|
| 원곡 연주 | **Kimiko Ishizaka**, piano · Wikimedia Commons **CC0 1.0** (raw 위키텍스트에서 `{{cc-zero}}` 확인) · 162.92s |
| 채보 | RAW · **553음** · 온셋 379개 · 간격 중앙값 0.2773s · 선두 침묵 1.30s |
| 렌더 | 랩탑 **sfizz_render 1.2.3** + Salamander Grand Piano V3 (SFZ) · loudnorm −16 LUFS |
| 합본 | 원곡 + 침묵 2.0s + 재현 = **326.51s** |

### 왜 YouTube 를 안 쓰나 — Boss 가 물어서 적어둔다
Boss: *"YouTube 음원에서 내려받아 가지고 음원 추출한 다음에 그거 쌀만대로 렌더링하고 있는 거 맞아?"*
**앞부분은 아니다.** 파이프라인(추출→채보→렌더→이어붙이기)은 맞지만 **소스가 YouTube 가 아니다.**
작곡가가 PD 라도 **연주·녹음에는 별개 저작권**이 있다(퍼포먼스/레코딩 라이선스).
그래서 Commons 에서 **라이선스가 메타데이터에 명시된 녹음만** 골랐다 — 1호 Public domain, 2호 CC0.

### 2호에서 잰 것 (전부 파형·MIDI 에서, 기억 아님)

| 물음 | 답 | 어떻게 알았나 |
|---|---|---|
| 마디당 음 수 | **16~17** (34마디), 마지막 마디만 **4** | MIDI 온셋을 4.430s 마디로 잘라 셈 |
| 슈베ン케 마디가 있나 | **없다** | 있으면 36마디다. 553음 ÷ 35마디 = 15.8 |
| 파#→내림라 (22→23마디) | **F#2 93.0Hz(41.2dB) @91.5s → G#2 104.0Hz(43.1dB) @96.5s** | 원본 스펙트럼. **렌더도 재현함**(F#2 53.1dB · G#2 103.5Hz 53.5dB) |
| 다이내믹 | LRA **7.20 LU** (1호 짐노페디는 12.00) | loudnorm 1패스 |
| 마지막 화음 | C·E·G 4옥타브, 152.5s→162.92s **약 11초** | MIDI 지속시간 |
| 감정 자리 | **신뢰/수용** (기쁨/평온과 겹침) | §1 표 · 123 문서 §1② |

**"34마디 동안 한 번도 안 어긋났다"가 이 곡의 감정 그 자체다** — 플루치크의 신뢰(trust) 최약강도
수용(acceptance)이 그거다. 그래서 하수(BGM)로 깔아도 안 지친다.

### 페이지 — 다크 시네마틱 + 인터랙티브 (Boss 지시로 전면 교체)

> Boss: *"웹페이지 디자인 좀 멋있게 만들어 봐 세련되게. 너무 촌스럽잖아. 인터랙티브한 요소도 하나도 없고."*
> → 종이 테마 폐기. 1호의 베이지 테마가 그 "촌스러움"이었다.

`site/assets/piano.css` + `site/assets/piano.js` = **42곡 공용 디자인 시스템**.
곡 페이지는 `data.js`(음표·파형)만 갈아끼우면 된다.

| 요소 | 무엇에 물렸나 |
|---|---|
| 하단 독(웨이브폼·재생·구간칩) | 오디오. 파형 클릭 = 탐색, 구간 칩이 원곡/침묵/재현으로 자동 전환 |
| 타임라인 12지점 | 클릭 = 그 시각으로 점프. 재생 중이면 **현재 지점이 켜진다** |
| 피아노롤 | 553음을 원곡(warm)·재현(cool) **양쪽 다** 그림. 반투명 = 같은 음이 두 번 |
| 마디 스트립 | 마디당 음 수. **마지막 마디만 빨강** — 위의 "4음"이 눈에 보인다 |
| 감정 바퀴 | 8칸 SVG. hover 하면 설명이 바뀐다. **신뢰 칸이 teal** |
| 약자 사전 | 입력창이 12개 항목을 실시간 필터 |

⚠️ **`.rv` 등장 애니메이션은 `html.js` 로 잠가야 한다.** 안 그러면 JS 없는 환경(그리고
스크린샷)에서 **본문 전체가 opacity:0** — 안 보이는 본문은 본문이 아니다.
`<head>` 에 `<script>document.documentElement.className+=' js';</script>` 한 줄로 깜빡임도 막는다.

---

## 2. 감상 가이드 — 어떻게 "진짜로 잰" 타임라인을 만드는가

⚠️ **기억으로 시각을 적지 않는다.** 전부 원본 파형과 MIDI에서 계산한 값이다.

### 2.1 파형에서 얻는 것 — 침묵·경계
50ms 창 RMS → `20*log10` → 중앙값 −8dB 문턱 → 0.25s 이상 연속 조용한 구간.
짐노페디: **선두 침묵 2.15s · 88.55–90.35의 1.8s 침묵 · 미주 4.3s**.
이 1.8초가 3분짜리 곡의 유일한 진짜 경계다 — 악보가 아니라 **연주자가 만든 침묵**.

### 2.2 음표에서 얻는 것 — 화성 골격
최저음(≤A2)만 뽑아 **라벨이 바뀌는 시각**을 찍는다. 그게 저음 진행이다.

```
   2.21 G2 ─┐
   4.59 D2  │ 2.45초마다 G↔D 시소 (36초간)
   7.09 G2 ─┘
  38.67 F#2 → 40.76 B1 → 42.94 E2     ← 처음 깨짐. B1 = 곡 전체 최저음
  71.45 E2 … 84.65 A2                 ← 13.2초간 D2로 안 돌아옴 = B 구간
  90.37 G2                            ← 되돌아옴
 125.89 F#2 → 128.02 B1 → 130.24 E2   ← 0:38의 정확히 +87.2초. 같은 자리
 158.56 E2 … 173.20 A2                ← 14.6초 마지막 어둠
 173.20 A2 + A·C·E·G                  ← A단조7. 조성이 여기서 뒤집힌다
 176.80 D2 + D·F·A·D                  ← 라단조 종지. 350Hz F가 F#보다 24dB 세다
```

### 2.3 반복 검증 — 주장하기 전에 세라
"같은 음악이 두 번 온다"고 쓰기 전에 전반부 237음과 후반부 229음을 시각 0.35초 창으로 대조:
**72.6% 대응 · 시각 오차 중앙값 0.169s**. → "같은 음악"이 아니라 **"같은 골격"** 이라고 써야 맞다.
(정확 반복이라 썼으면 과장이었다.)

### 2.4 재현 구간 시각
`오프셋 = 원본 길이 + 침묵 = 183.589 + 2.0 = 185.589`
채보는 원본 오디오의 절대시각을 그대로 쓰므로 **시각만 더하면 된다**. 그래서
원곡 1:28의 침묵이 재현 4:34에 그대로 있고, 그게 "그냥 웨이브 튼 게 아니다"의 증거가 된다.
**이게 페이지에서 제일 강한 한 줄이다** — 검증도 공짜다.

---

## 3. 파이프라인 (2호부터 이대로)

```bash
# 1) 소재 — PD 연주 + PD 이미지를 Wikimedia Commons 에서 (User-Agent 필수, 없으면 403)
#    파일: asset/original.ogg, asset/*.jpg|png

# 2) 채보 (폰, ~10분) — PD 레인은 RAW
PYTHONPATH=/root/.venvs/parksy-phone/lib python3 scripts/midi_extract.py \
  asset/original.ogg -o . --name <name> --no-mono --grid 0 --keep-raw

# 3) 렌더 (랩탑) — 2호부터는 sfizz_render + SFZ
scp <name>_raw.mid dtsli@100.81.24.124:~/tmp/<slug>/
ssh ... '~/salamander/sfizz_render --sfz "<SFZ>" --midi <name>_raw.mid \
   --wav r.wav --samplerate 44100'
ssh ... 'ffmpeg -i r.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
   -codec:a libmp3lame -qscale:a 2 <name>.mp3'

# 4) 합본 (폰) — 원곡 2패스 loudnorm → 침묵 2s → 재현 concat
ffmpeg -i original.ogg -i <name>.mp3 -filter_complex \
 "[0:a]loudnorm=...:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..,aresample=44100,aformat=channel_layouts=stereo[a];\
  [1:a]aresample=44100,aformat=channel_layouts=stereo[b];\
  anullsrc=r=44100:cl=stereo,atrim=0:2.0[s];[a][s][b]concat=n=3:v=0:a=1[out]" \
 -map "[out]" audio/combined.mp3

# 5) 이미지 축소 1400px 이하 (원본 16MB jpg 가 그대로 올라가면 안 된다)

# 6) 웹페이지 — index.html 템플릿 복사 후 역사·평가·감정·타임라인 교체
```

---

## 4. 함정 (이번에 밟은 것)

| 함정 | 증상 | 처방 |
|---|---|---|
| **Salamander 는 SF2 가 아니라 SFZ 다** | 랩탑에 SF2 를 찾으니 없다. 메모리엔 "SF2 1.18GB" 라고 적혀 있었다 | 실제 자산은 `SalamanderGrandPianoV3_44.1khz16bit.tar.bz2` (**488MB**, archive.org). fluidsynth 로는 못 연다 → **`sfizz_render`**. `~/salamander/` 에 영구 설치할 것 — `~/tmp/` 에 두면 또 사라진다 |
| **sfizz 1.2.3 tarball 은 빌드가 안 된다** | `CMake Error at cmake/SfizzDeps.cmake:81 (add_subdirectory)` — 원인이 화면에 안 보인다 | tarball 에 **git 서브모듈이 없다**(`external/st_audiofile`). `git clone --depth 1 --branch 1.2.3 --recurse-submodules --shallow-submodules` 로 받아야 한다. cmake 실패 시 **출력을 파일로 빼서 grep** 할 것 |
| **fluidsynth 가 stdin 을 먹는다** | ssh heredoc 스크립트가 첫 렌더 뒤 전부 사라짐. `Parse error ... 'ho "==="'` | `fluidsynth ... < /dev/null`. `ffmpeg -f null -` 과 **같은 부류** — 소리 도구는 stdin 을 본다 |
| **`ffmpeg -v error` 는 volumedetect 를 숨긴다** | "무음 검사했는데 출력이 없다" | volumedetect 는 INFO 레벨. `-v error` 빼고 `-hide_banner` |
| **원본이 −25.9 LUFS 로 아주 조용하다** | 재현(−15.7)과 10dB 차이 | 원본에 2패스 loudnorm. 그냥 gain 주면 TP +3.1 dBTP 로 클리핑 |
| **16MB jpg** | 그대로 Pages 에 올라감 | `scale='min(1400,iw)':-2` 로 축소. 16MB → 202KB |
| **Pages 는 `main`, 작업은 `master`** | 새 페이지가 안 뜬다 (118커밋 차이) | 미리보기는 로컬 http.server. **공개는 Boss 판단** |

---

## 4.5 납품지 — **parksy.kr/channel/musician/piano/** (2026-10-06 Boss 확정)

> Boss: "https://parksy.kr/ 여기 **뮤지션 박씨 폴더** 여기에다 저장해 놔. **앞으로도 계속 여기다 저장할 거야.**"

레포 = `dtslib1979/parksy.kr` (**private**, 기본 브랜치 `main`, Pages = branch/main 루트 → **커밋 = 즉시 공개**).

```
channel/musician/piano/
├── index.html                    ← 곡 목록 (여기서 계속 늘어난다)
├── assets/                       ← 42곡 공용 (2호에서 신설)
│   ├── piano.css                 다크 시네마틱 디자인 시스템
│   └── piano.js                  인터랙션 (독·롤·바퀴·타임라인)
├── 01-satie-gymnopedie/
│   ├── index.html                자체 <style> 인라인 (구 테마)
│   ├── audio/combined.mp3        8.4MB
│   └── img/ 5장
└── 02-bach-prelude-c/
    ├── index.html                assets/ 를 링크
    ├── data.js                   12KB — 음표 553개 + 파형 (base64)
    ├── audio/combined.mp3        7.5MB
    └── img/ 4장
```

**라이브 확인 (2026-10-06, 2호 업로드 후):** 전부 **200**.

| URL | 코드 |
|---|---|
| `https://parksy.kr/channel/musician/piano/` | 200 (목록에 01·02) |
| `…/01-satie-gymnopedie/` · `…/audio/combined.mp3` | 200 |
| `https://parksy.kr/channel/musician/piano/02-bach-prelude-c/` | 200 |
| `…/02-bach-prelude-c/data.js` | 200 · application/javascript |
| `…/02-bach-prelude-c/audio/combined.mp3` | 200 · audio/mp3 |
| `…/02-bach-prelude-c/img/*.jpg` (4장) | 200 · image/jpeg |
| `…/assets/piano.css` · `…/assets/piano.js` | 200 |

**라이브 동작 검증 (Playwright, 2026-10-06):** 553음 로드 · 재생 1.69s 진행 ·
타임라인 클릭 → `2:44` 로 점프 + 칩이 `재현 · 살라만더` 로 전환 · 콘솔 에러 0.

⚠️ **Pages 빌드에 ~40초 걸린다.** 업로드 직후 curl 하면 **404 가 뜬다** — 실패가 아니다.
`200` 이 나올 때까지 폴링할 것. (이번에 처음에 404 6개 보고 놀랐다.)

### 올리는 법 — `scripts/parksy_push.py`

```bash
set -a && . ./.secrets.env && set +a
python3 scripts/parksy_push.py <로컬폴더> "channel/musician/piano" "<커밋 메시지>"
```
Git Data API 로 **blob → tree → commit → ref** 를 한 번에. 중간 상태가 안 남는다.
`DTSLIB_GITHUB_TOKEN` 은 **죽었다**(Bad credentials — 2026-10-06 실측). **`GITHUB_TOKEN`** 을 쓴다
(`dtslib1979/parksy.kr` 에 **push 권한 있음** 실측).

### 함정 (이번에 밟은 것)
| 함정 | 증상 | 처방 |
|---|---|---|
| **urllib 이 대용량 blob 에서 죽는다** | 11MB blob POST → `400 malformed` | **curl 로 보낸다.** 같은 페이로드가 curl 로는 7초에 201 |
| **GitHub blob API 의 산발적 400** | 같은 요청이 어떤 땐 400 `malformed … resubmit` | **진짜로 재제출하면 된다**(문구가 문자 그대로다). 400 도 재시도 대상에 넣을 것 |
| **private 레포지만 Pages 는 공개** | 커밋하는 순간 세계 공개 | 올리기 전에 초안 확인. Boss 지시로 올리는 것이므로 게이트는 Boss 승인 |
| **canonical·JSON-LD 가 helena 주소로 남는다** | 검색엔진이 원조를 엉뚱한 데로 본다 | parksy.kr 판은 `parksy.kr/#person` · `parksy.kr/channel/musician/piano/…` 로 **치환 후 업로드** |

### ⚠️ 사본이 둘로 갈린다
로컬 작업본은 `helena_phone:music-channel/` 에도 있다. **납품지는 parksy.kr 쪽**이므로
둘을 계속 맞추거나, 한쪽을 버려야 한다. **Boss 판단 대기.**

---

## 5. 남은 일

- [x] ~~2호 — Bach Prelude in C BWV 846~~ → **완성·납품** (§1.5)
- [x] ~~공개 경로~~ → **parksy.kr/channel/musician/piano/** (Boss 확정, §4.5)
- [x] ~~미리보기 서버~~ → 납품지는 parksy.kr (로컬 서버 불필요, 정리 대상)
- [ ] **Boss 판정** — RAW vs 조정렬 / 딜레이 유지 여부 / 페이지 문구 / **다크 테마 수용 여부**
- [ ] **1호를 새 디자인으로 이식할지** — Boss 가 "촌스럽다"고 한 건 1호 테마다.
      2호만 새 옷을 입으면 채널 안에서 두 곡이 따로 논다. **Boss 판단 대기.**
- [ ] **1호 렌더 엔진 확정** — 랩탑 SSH 키가 막혀 못 봤다(§1 ⚠️). `~/tmp/sal/run.sh`
- [ ] **사본 정리** — `helena_phone:music-channel/` 을 버릴지 Boss 판단
- [ ] **`midi_lane/` 은 gitignored** — 42곡 소재(원본 ogg·MIDI·렌더)가 **폰에만** 있다.
      폰이 죽으면 소재가 사라진다. 42곡 다 모이기 전에 어디론가 올려야 한다. **Boss 판단 대기.**
- [ ] 이미지 자동 수급 스크립트 — 지금은 손으로 Commons API
- [ ] 42곡 소재 목록 확정 (`_notebook/122` §3은 6곡까지만)
- [ ] 3호 — `_notebook/122` §3 우선순위 3

---

*`_Claude` · 2026-10-06 · 1호 완성 · 2호부터 이 레시피를 그대로 쓴다*
