---
date: 2026-10-03
agent: Claude
mark: _Claude
type: study
status: draft
related:
  - 102-tablet-hw-parse_Grok.md
  - 103-adb-mesh-revive_Claude.md
  - 101-ending-page_Claude.md
  - 22-s21-benchmark.md
  - HANDOFF_DEEPFAKE_MCP_CLOUD_2026-09-19.md
---

# 3노드 음악 워크센터 — 스터디 전문 (2026-10-03)

> 이 문서는 2026-10-03 세션에서 실측·리서치한 것을 전부 모은 것이다.
> **표기 규칙:** `[실측]` = 이 세션에서 직접 명령을 돌려 확인 · `[리서치]` = 커뮤니티/공식 문서 ·
> `[미검증]` = 아직 안 해봄 · `[기록]` = 기존 레포 문서에서 인용.

## 0. 한 줄

폰 proot을 **음악 전용 워크센터**로 쓰기로 한 결정, 그리고 **랩탑·proot·안드로이드 3노드로
MIDI 기반 작곡·편곡·가상악기·가상 보컬을 하는 구상**. 오늘 그 실현 가능성을 실측했고,
가속기(NPU/GPU) 경로를 리서치했다.

---

## 1. 결정 — 왜 폰은 "음악 전용"인가

### 1.1 네 작업의 성격 비교

| 작업 | 막히는 지점 | 성격 |
|---|---|---|
| 영상 | 커널이 도커를 막음 ([[HANDOFF_DEEPFAKE_MCP_CLOUD_2026-09-19]] §2) | 구조적 |
| 시각·이미지 | **화면이 필요함 → 그 화면은 Boss의 것** | 물리적 |
| 웹 발행 | 애초에 연산이 아님 (텍스트 변환) | 정의상 |
| **음악** | **없음** | **맞음** |

음악만 **화면도, 도커도, GUI도 안 쓴다.** 파일 들어가고 파일 나오는 결정적 작업이다.
FluidSynth가 스트리밍이라 램도 거의 안 먹는다.

### 1.2 폰 RAM 실측 [실측]

```
(세션 초)  used 8.9Gi · free 682Mi · available 1.9Gi · swap 6.0Gi/6.0Gi (여유 1.0Mi)
           → 스왑 100% 소진. "벼랑"
(정리 후)  used 6.7Gi · free 900Mi · available 4.1Gi · swap 6.0Gi/4.3Gi (여유 1.7Gi)
```

**중요:** `free`가 보여주는 건 proot이 아니라 **폰 전체(안드로이드 포함)** 다. proot 몫은 약 450MB(5%)뿐이고,
최대 소비자는 Claude 자신(343MB → 289MB)이다.

세션 초의 "벼랑"은 **연산이 아니라 앱 잔더미**였다:

```
423MB  Bixby 온디바이스 한국어 ASR (:kokr:asr)
380MB  Chrome 샌드박스 렌더러      ┐
243MB  Chrome 본체                ├ 856MB
233MB  Chrome privileged          ┘
226MB  넷플릭스 · 184MB Adobe 리더 · 150MB 티스토리 · 131MB Facebook · 120MB 엑셀
```

→ **음악은 이 상황에서도 80배속으로 통과했다.** 음악이 램을 안 먹는다는 증거다.

### 1.3 램 한도의 정체 = 사운드폰트 크기

```
TimGM6mb.sf2   5.9MB   ← 안전 (오늘 실측 통과)
SSO (압축해제)  461MB   ← 여유
VSCO2_CE_SFZ   1.8GB   ← 가용 1.9GB + 스왑 꽉 찬 상태에선 위험
디스크          58G 여유
```

"램 터질 것 같을 때"는 **음악의 조건이 아니다.** 램이 터지는 건 영상 쪽이고, 영상은 이미 폰 밖에 있다.
음악에서 랩탑을 부를 진짜 이유는 **"그 악기가 폰에 없을 때"** 하나뿐이다.

---

## 2. 3노드 실측 인벤토리

### ① 랩탑 (Windows + WSL2)

```
CPU      Intel Core i7-8550U (2017, 4코어 ULV 15W)   [실측]
GPU      nvidia-smi 없음 · CUDA 없음                  [실측]
메모리    7.8Gi (used 3.1Gi / buff-cache 4.7Gi)        [실측]
WSL      Linux 6.6.87.2-microsoft-standard-WSL2, x86_64
ORT      onnxruntime 1.22.1 → ['AzureExecutionProvider','CPUExecutionProvider']  ← CPU 전용
```

**가진 것:**

| 항목 | 내용 |
|---|---|
| REAPER | `/mnt/c/Program Files/REAPER (x64)` |
| **Spitfire Audio (BBC SO)** | `/mnt/c/Program Files/Spitfire Audio` |
| 그 외 가상악기 | Modartt(Pianoteq) · Audio Modeling(SWAM) · Ample Sound · Soundpaint · Native Instruments · Steinberg · Propellerhead · Avid · Splice |
| 무료 오케스트라 | `/mnt/d/PARKSY/SSO.zip` (461MB) · `VSCO2_CE_SFZ.zip` (1.8GB) |
| 사운드폰트 | FluidR3_GM.sf2 · SalamanderGrandPiano.sf2 |
| 오디오 레포 | `/mnt/d/PARKSY/parksy-audio` (+ `local-agent/`) |
| **가상 보컬** | DiffSinger · DiffSingerMiniEngine · GPT-SoVITS · rvc_models (§4) |
| CI 러너 | `~/actions-runner`, **등록됨** `wsl2-device-farm` → dtslib1979/dtslib-apk-lab, `--startuptype service` |

**약점 [기록]:** BBC SO의 AUNTIE 엔진은 **오프라인 렌더 맥락을 차단해 -91dB 무음**을 낸다.
`bbcso_render_auto.sh` 주석: `42230 = Offline Render (BBC SO에서 무음, 사용 금지)`.
그래서 Play+Record를 GUI로 실시간 자동화한다 → **랩탑이 깨어 있고 REAPER가 떠 있어야 함.**
3노드 중 유일하게 자동화가 안 되는, 가장 취약한 고리.

### ② proot Ubuntu (이 세션, Claude가 사는 곳)

```
아키텍처   aarch64 · glibc · Ubuntu 26.04 LTS
가용 램    1.9 ~ 4.1GB (변동)
디스크     58G 여유
```

| 항목 | 상태 |
|---|---|
| **REAPER 7.81 linux_aarch64** | ✅ **[실측]** 설치·기동·헤드리스 오프라인 렌더 전부 성공 (§6) |
| **FluidSynth 2.6.0** | ✅ [실측] 파반 6분 → 4.5초 (**~80배속**) |
| ffmpeg 8.1.2 | ✅ [실측] (x11grab은 미포함) |
| TimGM6mb 사운드폰트 | ✅ [실측] `/usr/share/sounds/sf2/` |
| **NPU/GPU 접근** | ❌ **[기록+실측]** glibc↔bionic ABI — 구조적 벽 |

### ③ 안드로이드 (SM8750)

**가속기 부품 실측 [실측]** — `/vendor/lib64/`:

```
libSnpeHtpV79Stub.so        ← HTP V79 확정 (Snapdragon 8 Elite)
libSNPE.so · libSnpeCpu.so · libSnpeGpu.so
libsnpe_wrapper.so · libsnpe_dsp_domains_v3.so
libsnap_qnn.so              ← QNN
libcdsprpc.so (497KB)       ← FastRPC 클라이언트
libadsprpc.so · libsdsprpc.so · libmdsprpc.so
cdsp_face.so · libsysmon_cdsp_skel.so
```

`/dev/`: `fastrpc-cdsp` · `fastrpc-cdsp-secure` · `remoteproc-cdsp-md` · `glink_pkt_data_cdsp` 등 전부 존재.

**부품은 다 있다. proot이 못 여는 것뿐이다.**

⚠️ `libQnnHtp.so`는 없다 — 그건 QAIRT/`com.qualcomm.qti:qnn-runtime` 패키지로 따로 온다.
SNPE 쪽은 이미 온전하므로 **SNPE 경로가 더 짧을 수 있다.**

---

## 3. 연결 — 이미 배선돼 있다 [실측]

### 3.1 relay.sh ping (2026-10-03 실행)

```
OK
dtslib        ← 호스트명
x86_64        ← 랩탑 아키텍처 (폰은 aarch64 — 다른 두뇌)
26756         ← phone-to-laptop.md 바이트
1432          ← laptop-to-phone.md 바이트
```

`scripts/relay.sh`가 폰 ↔ 랩탑 **파일 메일박스**를 SSH 너머로 이미 운영 중이다.
(설계 이유가 문서에 있다: "양쪽이 동시에 살아있는 때가 드물다. 소켓은 한쪽이 꺼지면 증발하지만 파일은 남는다.")

### 3.2 노드 도달성 [실측]

| 노드 | 주소 | 결과 |
|---|---|---|
| Windows/WSL 랩탑 | `100.81.24.124:2222` | ✅ 도달 (relay OK) |
| 태블릿 tab-s9 | `100.86.15.50:8022` | ✅ 도달 |
| 폰 자기 자신 | `100.103.250.45:8022` | ✅ 도달 |
| WSL (별도 노드) | `100.90.83.128:2222` | ❌ 응답 없음 |

### 3.3 ⚠️ 이름 정정 — ADB가 아니다

- **ADB = 안드로이드 ↔ 안드로이드 선.** 폰 ↔ 태블릿이 여기 해당.
- **랩탑(Windows/WSL)은 ADB 대상이 아니다.** 폰 ↔ 랩탑은 **SSH**다.
- 두 선이 다른 것이고, **둘 다 이미 살아 있다.**
- 참고: `[[103-adb-mesh-revive_Claude]]`의 3노드 mesh는 WSL↔폰↔탭이고, 랩탑은 그 mesh 바깥의 SSH 노드다.

---

## 4. 자산 — 가상 보컬이 **이미 ONNX로 있다** [실측]

```
~/DiffSinger/parksy_onnx/parksy_ko_v1.onnx                 ← 한국어 가창 모델
~/DiffSinger/checkpoints/pc_nsf_hifigan_44.1k_hop512_128bin_2025.02/model.ckpt
~/DiffSingerMiniEngine/assets/vocoder/nsf_hifigan.onnx     ← 보코더 (ONNX)
~/DiffSingerMiniEngine/{server.py, synthesis.py, utils.py}  ← 경량 서빙 엔진
~/GPT-SoVITS/{api.py, api_v2.py, Dockerfile}
~/rvc_models/  helena_rvc · hoyadang_rvc · mother_rvc · parksy_rvc · parksy_rvc_v3 · sop
~/rvc_models/onnx/  ·  VOICE_CATALOG.md  ·  send_rvc_to_helena.sh
```

**ONNX가 다리다.** ONNX Runtime은 CPU·QNN(NPU)·QNN GPU·NNAPI 프로바이더를 전부 같은 파일로 먹는다.
PyTorch 모델이었다면 훨씬 막막했을 것이다.

→ **"가상 보컬 넣기"는 새로 만들 일이 아니라, 이미 있는 걸 어느 노드에서 돌리느냐의 문제다.**

⚠️ 단, **ONNX라는 것과 QNN에서 돌아간다는 것은 다른 얘기다.** 연산자 지원·FP16 정밀도·양자화를
실제로 태워봐야 안다. `[미검증]`

---

## 5. 가속기 스터디

### 5.1 NNAPI는 죽었다 [리서치]

**NNAPI는 Android 15에서 공식 폐기됐다.** Google 마이그레이션 가이드가 나왔고,
NNAPI를 쓰면 **CPU로 폴백**한다. 개발자 실측도 "NNAPI가 기본 CPU 프로바이더보다 느리다".

대체 경로:
- **LiteRT(구 TFLite) in Google Play Services** — 그러나 GPU·XNNPACK 델리게이트만 있고 **NNAPI 델리게이트 없음**
- LiteRT의 NPU 지원은 **Qualcomm AI Engine 한정**
- **ONNX Runtime QNN Execution Provider** — Qualcomm 전용, **양자화 모델 필요**

→ **CLAUDE.md의 "Termux NDK로 sherpa-onnx NNAPI 크로스컴파일" 전략은 낡았다.**
  2026년 경로는 QNN이다.

### 5.2 옛 실패 기록 — 그리고 그게 verdict가 아닌 이유

`_notebook/99-devlog.md` 607행 [기록]:

```
- Piper + Kokoro 모델을 NNAPI로 실측 → **둘 다 CPU보다 느림**
- NNAPI(NPU 가속) TTS 경로는 폐기 확정
...
> NNAPI 경로는 Piper·Kokoro로 대리 검증했고 둘 다 CPU보다 느려서 폐기.
> **NPU 가속 + GPT-SoVITS 조합은 이중으로 불가능 확인된 셈.**
```

**그때 잰 건 NPU가 아니라 이미 죽어가던 API(NNAPI)였다.** 5.1에 따라 NNAPI는 CPU로 폴백하므로,
그 실험은 NPU 성능을 측정한 것이 아니다. **닫힌 문이 아니라 잘못된 문을 두드린 것이다.**

또한 devlog 611-613 [기록]: `sherpa-onnx가 GPT-SoVITS 파일 포맷(.ckpt/.pth)을 애초에 지원 안 함`
→ 별개의 문제. sherpa-onnx는 포맷 미지원이고, 이건 **ONNX 변환으로 우회 가능**하다(§4).

### 5.3 2026 경로 = QNN over FastRPC [리서치]

```
ONNX Runtime + QNN Execution Provider
  패키지:  onnxruntime-android-qnn  +  com.qualcomm.qti:qnn-runtime (libQnnHtp.so)
  설정:    backend_path = libQnnHtp.so
  모드:    burst / balanced / power_saver / sustained_high_performance
```

**결정적 함정:** `targetSdk >= 31` 앱은 매니페스트에 아래를 선언하지 않으면
**링커가 벤더 라이브러리를 네임스페이스에서 숨긴다** → `QNN_DEVICE_ERROR_INVALID_CONFIG`로 실패.
오류 메시지가 오해를 유발한다(셸 도구 `qnn-net-run`은 잘 돌아가서 더 헷갈림).

```xml
<uses-native-library android:name="libcdsprpc.so" android:required="false" />
```

**그런데 셸/Termux는 네임스페이스 제한을 안 받는다.** 비루팅 Termux가 `/system`·`/vendor`에서
`libQnn*`/`libcdsprpc.so`를 `dlopen`하고 `QnnInterface_getProviders`를 `dlsym`해 HTP 백엔드 슬롯을
호출한 사례가 보고돼 있다. **이 폰에 유리한 조건.** [리서치 — 독립 검증은 안 된 포럼 보고]

### 5.4 모델별 실측 — GPU vs NPU vs CPU [리서치]

| 모델 | 하드웨어 | 수치 |
|---|---|---|
| **Whisper** Small | SD 8 Elite **NPU** | 인코더 ~70ms/30초 구간 · 디코더 ~8.4ms (**약 400배속**) |
| Whisper Medium | SD 8 Elite NPU | 인코더 ~175ms · 디코더 ~23.4ms |
| **MusicGen** Small | SD 8 Gen 3 | HTP **180ms/step** · Adreno GPU 182ms/step · CPU 201ms/step (**NPU 이득 ~10%뿐**) |
| **OmniVoice** (SM8750) | HTP V79 | 디퓨전 예측기 NPU FP16 ~5초/32스텝(짧은), ~19초/32스텝(롱/클론). **보코더+인코더는 CPU(XNNPACK) 폴백** — HTP에서 FP16 수치 불안정. **INT8(16a8w)은 손실 과다** |
| **Basic Pitch** LiteRT | Galaxy S26 | GPU 248ms p50 · **NPU 4544ms p50** · RPi5 CPU 24ms p50 |
| HTP 실측 지속 | SM8750 | **4.3 TOPS int8 / 1.1 TFLOP/s fp16** (마케팅 45 TOPS는 피크/스파스값) |

**⚠️ 5.4 표 해석 주의:** Basic Pitch 행에서 **라즈베리파이 5 CPU가 24ms인데 Galaxy S26 GPU가 248ms**라는 건
말이 안 된다 → **행마다 측정 조건이 다르다.** 사과 대 사과인 것은 *같은 기기·같은 설정*의 GPU vs NPU 비교뿐이고,
그 비교에서도 조건 차이 가능성을 배제할 수 없다. **"GPU가 18배 빠르다"고 단정하면 과장이다.**

**그래도 일관되게 나오는 패턴:**
- Whisper처럼 HTP에 **잘 맞는** 모델은 극적으로 빠르다 (400배속)
- MusicGen처럼 **이득이 거의 없는** 모델도 있다 (~10%)
- **보코더는 HTP에 자주 못 올라간다** (FP16 불안정 → CPU 폴백)
- **INT8은 오디오 디퓨전/TTS에 손실이 크다.** FP16이 사실상 하한선

### 5.5 이 폰에서 확실한 것 / 미지인 것

```
[확실] 가속기 하드웨어 실재 (HTP V79 + Adreno 830, libSnpeHtpV79Stub.so 확인)
[확실] NNAPI는 죽은 경로 → QNN으로 가야 함
[확실] Whisper류는 폰 NPU가 랩탑 CPU를 압도 (400배속 vs 실시간 1~3배)
[미지] Demucs의 온디바이스 실측 — 아무도 수치를 공개 안 함 (ONNX + QNN GPU로 개발 중인 앱만 존재)
[미지] DiffSinger parksy_ko_v1.onnx가 QNN에서 도는지
[미지] Termux에서 QNN이 실제로 열리는지 (← 첫 실험)
```

---

## 6. REAPER 폰 실증 [실측]

### 6.1 설치·기동

```
reaper781_linux_aarch64.tar.xz  12.3MB / 5.2초
ldd ./reaper                    7 NEEDED / 0 not found
필요 추가 패키지                 libgtk-3-0t64 하나
                                 (libSwell.so가 gdk_init_check 요구 → 없으면 symbol lookup error)
```

`Xvfb :98 -screen 0 1280x800x24` + `DISPLAY=:98 ./reaper -nosplash` →
**전체 DAW UI(트랙·믹서·트랜스포트·타임라인)가 실제로 그려짐.**
`~/.config/REAPER/` 트리 생성 + **arm64 VST 스캔 성공**
(`reaper-vstplugins_arm64.ini`에 ReaComp·ReaDelay·ReaControlMIDI 등 동봉 플러그인 등록).

### 6.2 헤드리스 오프라인 렌더

```
reaper -renderproject test.rpp   →   test.wav (20.000초, pcm_s24le, 44100Hz, 스테레오)

원본 src20.wav   RMS -24.8dBFS   peak -12.3dBFS
렌더 test.wav    RMS -24.8dBFS   peak -12.3dBFS      ← 정확히 일치 = 무음 아님
```

**막는 다이얼로그 2개 (자동화하려면 닫아야 함):**

| 다이얼로그 | 원인 | 대응 |
|---|---|---|
| `Error opening devices` | proot에 오디오 장치 없음 (렌더엔 무해) | `xdotool key --window <id> Return` |
| `Project Load Warning` | 내가 지어낸 `RENDER_OUTPUT` 토큰 | **그 토큰만 빼면 안 뜸** |

**재현 자산:** `/root/work/_staging/reaper-test/` (`REAPER/`, `proj/test.rpp`, `dismiss.sh`)

### 6.3 최소 .rpp 골격

```
<REAPER_PROJECT 0.1 "7.81/linux-aarch64" ...>
  <TRACK
    NAME ...
    <ITEM
      POSITION 0 / LENGTH 20
      <SOURCE WAVE
        FILE "src20.wav"        ← 프로젝트 파일 기준 상대경로
      >
    >
  >
  <RENDER_CFG ... >
>
```

알아낸 것: `RENDER_OUTPUT`은 **존재하지 않는 토큰**이다(직접 넣어보고 경고로 확인). `RENDER_CFG`는 통과.

### 6.4 함정 — `pkill -f`는 셸 자살

```
pkill -f "REAPER/reaper"   → 출력 없이 exit 144
```

`bash -c "..."` 명령줄 자체에 패턴 문자열이 들어있어서 **자기 셸과 일치해 죽인다.**
→ `pkill -x 이름`을 쓸 것. (이 세션에서 두 번 당했다.)

---

## 7. 음악 파이프라인 실측 인벤토리

### 7.1 parksy-audio (뒤끝: `dtslib1979/parksy-audio`, ~963MB, private)

```
run.py  5단계 CLI:  Humanize → Quality Gate → FluidSynth+SF2 렌더 → Master(ffmpeg loudnorm) → Visual MP4
README: "Emotion Driver Axiom (공리 0)" · 총 제작비 $0
```

**⚠️ 폰 이식 걸림돌 [실측]:** `run.py`의 SF2 경로가 **윈도우를 가리킨다.**

```python
SF2_MAP = {
  "SGM":  os.environ.get("PARKSY_SF2_SGM",  "/mnt/d/VST/SGM-V2.01.sf2"),
  "TOH4": os.environ.get("PARKSY_SF2_TOH4", "/mnt/d/VST/TOH-4.sf2"),
}
```

확인 결과 **`/mnt/d/VST` 자체가 존재하지 않는다.** → 폰 로컬 사운드폰트로 갈아끼워야 함.

### 7.2 `local-agent/` — 여기에 신경망이 두 단계 있다

```
steal.py:            URL → yt-dlp → Demucs 소스 분리 → basic-pitch MIDI 추출 → 편곡/인간화
extract_midi.py:     basic-pitch (ICASSP_2022 모델) — predict_and_save / ICASSP_2022_MODEL_PATH
requirements.txt:    basic-pitch>=0.3.0
bot.py --separate:   Demucs 소스 분리 후 멜로디 추출
```

**Demucs와 basic-pitch는 둘 다 신경망** → 가속 후보. `[미검증]` 폰 이식 여부.

### 7.3 기타 미비

- proot에 `mido`·`soundfile`·`scipy` 미설치
- `labs/bbcso/`는 윈도우 전용 (`render_auto.sh`가 `powershell.exe` 사용)
- `.github/workflows/`에 **렌더 워크플로 없음** (apk·pages·stats·manifest·youtube-stats만)

---

## 8. 3노드 분업 (확정 아님 · 제안)

```
작곡·편곡 (MIDI)             → proot (지휘소)
가상악기 (x86 VST)           → 랩탑 (대안 없음 — aarch64 REAPER는 x86 VST 못 읽음)
무료 오케스트라 (SF2/SFZ)     → proot (80배속 실측)
가상 보컬 (DiffSinger/RVC)    → 어디든 (ONNX). 가속은 안드로이드
믹싱·마스터                  → proot REAPER
```

**프로토콜 = MIDI와 WAV.** 세 노드가 완전히 다른 세계(x86 Windows / aarch64 Linux / Android bionic)라
공통분모는 파일뿐이다. 각 홉이 `MIDI in → WAV out`. 그 연결선은 `relay.sh`로 이미 살아 있다.

### 각 노드가 대체 불가능하게 가진 것

| 노드 | 유일 소유 |
|---|---|
| 랩탑 | **라이선스 가상악기** (Spitfire·Pianoteq·SWAM·Ample Sound) — 복제 불가 |
| proot | **항상 켜져 있고 Claude가 있는 지휘소** + REAPER aarch64 + 무료 오케스트라 |
| 안드로이드 | **가속기** (HTP V79 + Adreno 830) — 다른 둘 다 없음 |

### 정직한 난제 3개

1. **aarch64 REAPER는 x86 VST를 못 연다.** 폰이 Spitfire·Pianoteq·SWAM을 영원히 못 여는 이유.
   단 aarch64 Linux용 무료 VST는 있다 (sfizz · Surge XT · Vital · Dexed · Helm) — 폰도 가상악기를 *일부* 갖는다. `[미검증]`
2. **BBC SO 오프라인 렌더가 -91dB 무음** → 실시간 GUI 자동화. 랩탑이 깨어 있어야 함.
3. **보코더는 NPU에 안 올라갈 가능성이 크다** (이 칩에서 OmniVoice가 그랬다).
   전형적 분담: 음향 모델=NPU, 보코더=CPU/GPU.

---

## 9. 다음 실험 (제안 · 아직 안 함)

**1순위 — 안드로이드 노드에서 ONNX Runtime이 가속기를 여는가**

```
1. Termux에 clang 설치
2. libSnpeHtpV79Stub.so / libcdsprpc.so dlopen + QnnInterface_getProviders dlsym
3. Adreno OpenCL(GPU) 쪽도 같이 확인
4. 열리면 → nsf_hifigan.onnx(작고 단순)를 먼저 태워 프로바이더 확인
5. 그다음 → parksy_ko_v1.onnx (한국어 가창)
```

**열리면** 3노드 구상이 실체가 된다. **안 열리면** 가속 레인 전체가 moot — 거기서 접는다.

**2순위 — proot 음악 라인 정비**
```
1. run.py의 SF2 경로를 폰 로컬로 교체 (윈도우 경로 제거)
2. mido · soundfile · scipy 설치
3. MIDI → Emotion → MP4 전 체인 폰에서 완주 (계획의 진짜 증명)
4. 사운드폰트 등급 결정 (TimGM 5.9MB / SSO 461MB / VSCO2 1.8GB)
```

---

## 10. 함정 기록 (재발 방지)

| 함정 | 증상 | 대응 |
|---|---|---|
| `pkill -f "패턴"` | 셸이 자기 명령줄과 일치해 자살, **출력 없이 exit 144** | `pkill -x 이름` |
| proot의 `/proc` | uptime·ps 시작시각이 거짓말 | 신뢰하지 말 것 ([[proot-no-full-filesystem-scan]]) |
| `free` | proot이 아니라 **폰 전체** 메모리를 보여줌 | 안드로이드 몫은 `dumpsys meminfo`로 |
| `find /mnt/... -maxdepth N -iname A -o -iname B` | `-o` 그룹핑 없으면 결과 누락 (BBC SO를 못 찾은 원인) | `\( -iname A -o -iname B \)` |
| NAS/드라이브 전역 `find` | 2분 타임아웃 | 경로를 먼저 좁혀라 |
| REAPER 첫 실행 | `libSwell.so: undefined symbol: gdk_init_check` | `libgtk-3-0t64` 설치 |
| `ffmpeg x11grab` | Termux 빌드에 없음 | `xwininfo`(창 확인) + ImageMagick `import`(캡처) |

---

## 11. 출처

**레포 내부**
- `_notebook/99-devlog.md` §NPU (607, 611, 641, 1121-1177, 5633-5655행)
- `_notebook/102-tablet-hw-parse_Grok.md` — 태블릿 SNPE/Hexagon HTP v73
- `_notebook/103-adb-mesh-revive_Claude.md` — 3노드 mesh, IP/포트
- `_notebook/101-ending-page_Claude.md` — proot ABI 벽, "벽은 파워가 아니라 구조"
- `HANDOFF_DEEPFAKE_MCP_CLOUD_2026-09-19.md` — 폰 도커 불가, GH Actions 러너 사양

**외부**
- [NNAPI 마이그레이션 가이드 (Android Developers)](https://developer.android.com/ndk/guides/neuralnetworks/migration-guide)
- [LiteRT Play Services NPU 이슈 #3936](https://github.com/google-ai-edge/LiteRT/issues/3936)
- [thedevguy/whisper-htp-android — ORT C API + QNN EP](https://github.com/thedevguy/whisper-htp-android)
- [acul3/omnivoice-executorch-qnn-sm8750 — SM8750 HTP V79](https://huggingface.co/acul3/omnivoice-executorch-qnn-sm8750)
- [Qualcomm Whisper-Small 벤치마크](https://huggingface.co/qualcomm/Whisper-Small)
- [MusicGen Small Stereo ONNX — HTP/GPU/CPU 비교](https://huggingface.co/chinedudave06/musicgen-small-stereo-onnx)
- [demucs-onnx — htdemucs 4/6스템](https://huggingface.co/chinedudave06/demucs-onnx)
- [StemSplit/demucs-onnx](https://github.com/StemSplit/demucs-onnx)
- [litert-community/Basic-Pitch-LiteRT](https://huggingface.co/litert-community/Basic-Pitch-LiteRT)
- [Google LiteRT 샘플 PR #190 — Basic Pitch 전사](https://github.com/google-ai-edge/litert-samples/pull/190)
- [Snapdragon 8 Elite HTP 실측 (4.3 TOPS int8 / 1.1 TFLOP/s fp16)](https://github.com/alpharomercoma/snapdragon-vs-mediatek/blob/main/snapdragon-8-elite/REPORT.md)
- [QNN Execution Provider (ONNX Runtime)](https://mintlify.wiki/microsoft/onnxruntime/execution-providers/qnn)

---

*agent mark `_Claude` · 2026-10-03 · 전부 1차 가설 — `[미검증]` 항목은 실행 전까지 확정 아님*
