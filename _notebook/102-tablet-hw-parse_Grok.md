---
date: 2026-08-18
agent: Grok
mark: _Grok
cli: grok
type: hardware-parse
boss: true
status: measured
related:
  - 101-grok-mercenary-3loc_Grok.md
  - tablet-broadcast-studio_Claude.md
---

# 태블릿 로케이션 — 하드웨어·프로트 실측 (2026-08-18)

> **원본 이전:** `_notebook/grok/hardware.md` (세션 시작 때 읽는 책상).  
> 용병 규칙: 켠 방의 수첩·기기를 **문서 가정이 아니라 센다.**  
> 직전 리포트에서 이 프로세스를 S21이라고 한 것은 **문서 관성. 철회.**  
> Boss: 「여기서 구동할 거야 · 태블릿 3번 환경」.

---

## 0. 한 줄 판정

```
이 방 = Galaxy Tab S9 계열 (8GB / 128GB)
        Snapdragon 8 Gen 2 + Adreno 740 + S-Pen
        Termux → proot Ubuntu 26.04 → grok 1.0.5

S21(Exynos 2100 / Mali-G78 / ENPU) 이 아니다.
S25 Ultra(8 Elite) 도 아니다.
getprop는 proot에서 막혀 모델코드(SM-X710/X716)는 못 읽음.
근거는 CPU MIDR + GPU + S-Pen IRQ + 저장 크기.
```

---

## 1. 왜 Tab S9인가

| 신호 | 실측 | 맞는 기기 | 아닌 것 |
|------|------|-----------|---------|
| CPU 8코어 | A510×3 + A710×2 + A715×2 + X3×1 | **8 Gen 2** | S21=X1+A78+A55. S25=Oryon |
| GPU | `/dev/kgsl-3d0` **Adreno740v2** max 719MHz | 8 Gen 2 Galaxy | S21=`/dev/mali0` 없음(오늘 확인) |
| SoC | `soc0/family=Snapdragon` · `soc_id=519` | SM8550 계열 | Exynos 2100 아님 |
| S-Pen | `hall_wacom` + `sec_epen_irq` + `sec_epen_pdct` | 삼성 펜 기기 | S21 펜 없음 |
| RAM | MemTotal **7386700 kB ≈ 7.0GiB** (8GB 기기) | Tab S9 8GB | Tab S9+ 는 보통 12GB |
| 저장 | userdata **106G** (사용 31G / 남 76G) | **128GB** 기기 | S23 Ultra 최소 256GB → 탈락 |
| NPU 스택 | SNPE + **Hexagon HTP v73** + CDSP. eden/mali **없음** | 퀄컴 | S21 ENPU 아님 |

모델 문자열(`SM-X710` Wi-Fi / `SM-X716` 5G)은 안 열림. Wi-Fi/LTE 구분은 이 셸에서 미확정.  
Download에 `ONEstoreClient_SKT`·`F-Droid.apk` 있음 — 오늘 태블릿 설치 흔적과 맞음.

---

## 2. CPU (실측)

WALT 거버너. 클러스터 3+2+2+1.

| 코어 | MIDR part | 이름 | min–max | 측정 시 |
|------|-----------|------|---------|---------|
| 0–2 | `0xd46` | Cortex-A510 | 307–2016 MHz | ~1018 |
| 3–4 | `0xd4d` | Cortex-A715 | 499–2803 MHz | 2803 |
| 5–6 | `0xd47` | Cortex-A710 | 499–2803 MHz | 2803 |
| 7 | `0xd4e` | Cortex-X3 | 595–**3360** MHz | 864 |

AES/SHA/i8mm/bf16/SVE 계열 ASIMD 플래그 있음. 로컬 가속은 **이론**, proot에서 DSP/GPU 직통은 별개.

---

## 3. 메모리 · 저장 · 열

| 항목 | 실측 |
|------|------|
| RAM | 7213 MB 총 · 가용 ~1.6 GB (빠듯) |
| Swap | 8191 MB · 사용 ~45% + zram ~1 GB |
| GPU 메모리 | GpuTotal ~495 MB · KgslShmem ~465 MB |
| 디스크 | f2fs userdata 106G · `/` 와 `/sdcard` 같은 블록 |
| microSD | `/storage` = `emulated`+`self` 만. **카드 안 보임** |
| 열 (m°C) | battery 30.9 · xo-therm 34.3 · gpuss ~37–40 · cpuss ~41–46 |

배터리 % · 충전 여부는 `power_supply` 권한 거절. Termux:API `termux-battery-status` **없음**.

---

## 4. GPU / NPU — 부품은 있고 proot는 못 씀

**있는 것**

- GPU: Adreno 740 v2. 주파수 124.8–719 MHz. 유휴 ~220 MHz · busy 2%.
- OpenCL: `/vendor/lib64/libOpenCL.so` + `libEGL_adreno.so` (bionic).
- NPU: `libSnpeHtpV73Stub.so` · `libqnnengine.so` · `libcdsprpc.so` (Hexagon v73).

**막힌 것**

- proot(glibc) → 벤더 .so(bionic) `dlopen` 불가. S21 Mali 때와 **같은 벽**, 부품만 다름.
- `getprop` / `toybox` = Operation not permitted.
- `/dev/mali0` · ENPU · `libneuralnetworks.so` 경로 없음.

이미지 생성은 **클라우드(이 CLI의 Imagine)**. 로컬 Adreno/Hexagon 추론은 이 방에서 아직 못 연다.

---

## 5. 프로트 · 소프트웨어 (여기서 구동하는 층)

| 층 | 실측 |
|----|------|
| 호스트 | Termux `aid_u0_a267` · prefix bind 됨 |
| 게스트 | **Ubuntu 26.04 LTS** (Resolute) · proot-distro `ubuntu` |
| uname | `6.17.0-PRoot-Distro` (가짜 커널 문자열. 기기 커널 아님) |
| grok | **1.0.5** `/usr/local/bin/grok` |
| claude | 2.1.234 |
| node | v22.22.1 |
| python | **3.14.4** — pillow/numpy/torch **없음** |
| ffmpeg | **없음** (proot도 Termux도) |
| git remote | `dimas-40/helena_phone` (태블릿 계정. 빈 원격) |
| `/sdcard` | bind OK. DCIM/Screenshots · Documents 빔 |
| inbox | 없음 |
| phone-mcp :3456 | 꺼짐 |
| 건강 08:40 | **Grade C** · pass 10 / warn 16 / fail 7 |

`/sdcard` 읽기·쓰기는 됨. 갤러리 스캔 API는 Termux:API 미설치라 이 셸에서 안 됨.

---

## 6. 이 방에서 칸 ①②

| 일 | 되는가 | 조건 |
|----|--------|------|
| 칸 ① 잡지 구도 → 웹 코드 | **됨** | 이 CLI |
| 칸 ① 이미지 교체 | **됨** | 클라우드 Imagine |
| 칸 ② 사진 합성 + 10초 I2V | **됨** | 클라우드. 사진만 `/sdcard`나 인자로 |
| 칸 ② 이어 붙이기 | **안 됨** | ffmpeg 없음 |
| 로컬 RVC/torch 더빙 | **안 됨** | torch 없음 · RAM 가용 1.6G |
| S-Pen 스케치 받기 | **배관만 됨** | `/sdcard` 보임. 노트 앱 폴더는 아직 비어 있음 |

---

## 7. 직전 오판

문서(`CLAUDE.md` · `83` §8)는 S21 Mali를 전제한다.  
이 프로세스는 그 레포(`helena_phone`)를 클론해 앉아 있을 뿐, **실리콘은 태블릿**이다.  
remote가 `dimas-40`인 것도 이 판정과 맞다.

*실측 · agent mark `_Grok` · 2026-08-18 08:40 UTC*
