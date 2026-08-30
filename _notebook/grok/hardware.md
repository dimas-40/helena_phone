---
date: 2026-08-18
agent: Grok
mark: _Grok
cli: grok
type: hardware-parse
location: tablet
measured: 2026-08-18 08:40 UTC
---

# 태블릿 하드웨어 · 프로트 실측

> 원본은 이 파일. `_notebook/102-tablet-hw-parse_Grok.md`는 여기로 가는 포인터.

## 한 줄

```
Galaxy Tab S9 계열 · 8GB / 128GB
Snapdragon 8 Gen 2 + Adreno 740 v2 + S-Pen
Termux → proot Ubuntu 26.04 → grok 1.0.5
S21 아님. S25 Ultra 아님.
```

## 왜 Tab S9인가

| 신호 | 실측 | 탈락 |
|------|------|------|
| CPU | A510×3 + A710×2 + A715×2 + X3×1 (8 Gen 2) | S21=X1+A78+A55 · S25=Oryon |
| GPU | `/dev/kgsl-3d0` Adreno740v2 max 719MHz | S21 Mali `/dev/mali0` 없음 |
| SoC | Snapdragon · soc_id=519 | Exynos 2100 아님 |
| S-Pen | hall_wacom + sec_epen_irq + sec_epen_pdct | S21 펜 없음 |
| RAM | 7386700 kB ≈ 7.0GiB (8GB 기기) | Tab S9+ 보통 12GB |
| 저장 | userdata 106G = **128GB** | S23 Ultra 최소 256GB |
| NPU | Hexagon HTP v73 / SNPE / CDSP | S21 ENPU 아님 |

모델코드(SM-X710 / X716)는 getprop 거절로 못 읽음. Wi-Fi/5G 미확정.

## CPU

WALT. 3+2+2+1.

| 코어 | part | 이름 | min–max |
|------|------|------|---------|
| 0–2 | 0xd46 | A510 | 307–2016 MHz |
| 3–4 | 0xd4d | A715 | 499–2803 MHz |
| 5–6 | 0xd47 | A710 | 499–2803 MHz |
| 7 | 0xd4e | X3 | 595–3360 MHz |

## 메모리 · 저장 · 열 (08:40)

| | |
|--|--|
| RAM | 총 7213 MB · 가용 ~1.6 GB |
| Swap | 8191 MB · ~45% + zram ~1 GB |
| 디스크 | f2fs 106G · 씀 31 / 남 76 |
| microSD | 안 보임 |
| 열 | battery 30.9°C · GPU 37–40 · CPU 41–46 |

배터리 % · 와이파이 SSID = Termux:API 없음.

## GPU / NPU

있음: Adreno 740 · OpenCL 벤더 lib · Hexagon v73.  
막힘: proot glibc ↔ bionic. 로컬 가속 불가. 이미지는 클라우드.

## 프로트 소프트웨어

| | |
|--|--|
| Ubuntu | 26.04 LTS |
| grok | 1.0.5 |
| claude | 2.1.234 (DeepSeek 과금) |
| python | 3.14.4 · pillow/numpy/torch 없음 |
| ffmpeg | **없음** |
| git | origin `dimas-40/helena_phone` (원격 빈 레포) |
| /sdcard | bind OK |
| phone-mcp | 꺼짐 |
| 건강 | Grade C |

## 칸 ①②

| 일 | |
|----|--|
| ① 구도→웹+클라우드 이미지 | 됨 |
| ② 합성+10초 I2V | 됨 (클라우드) |
| ② concat / 로컬 RVC | 안 됨 |
