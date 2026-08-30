# 폰 ↔ PC 무선 ADB 메시 운영 매뉴얼

**구축일**: 2026-08-21
**대상**: SM-S938N (S25 Ultra, Android 16 / One UI)
**폰 Tailscale IP**: `100.103.250.45`
**ADB 포트**: `5900` ← **5555 절대 쓰지 말 것 (함정 1번)**

---

## 0. 이게 뭐냐 (30초 요약)

```
[WSL / PC] ──Tailscale──> [폰]
                           ├─ adb :5900        → uid 2000 시스템 제어
                           ├─ SSH :8022        → Termux
                           └─ proot Ubuntu     → Python/Node/ffmpeg/Claude
```

같은 Wi-Fi 아니어도 붙는다. 케이블 필요 없다. 유선 ADB와 기능 동일.

---

## 1. 매일 쓰는 법

### 연결
```bash
adb connect 100.103.250.45:5900
adb devices          # "device" 나와야 정상
```

### 작업
```bash
adb shell                                    # uid 2000 셸
adb install app.apk
adb push  파일 /sdcard/
adb pull  /sdcard/파일 .
adb shell screencap -p /sdcard/s.png
adb logcat
scrcpy -s 100.103.250.45:5900 --max-size 1024   # 화면 미러링+조작
```

### 끊기
```bash
adb disconnect 100.103.250.45:5900
```

### 스위치 스크립트 (`pw`)
```
pw on      # 연결 + proot 진입
pw off     # proot 종료 + 연결 해제
pw         # 상태 확인
```

---

## 2. ⚠️ 재부팅하면 끊긴다 — 복구 절차

`adb tcpip`는 **재부팅 전까지만** 유지된다. 폰 껐다 켜면 5900이 사라진다.

### 정상이라면 (자동 복구)
Shizuku 포크의 **부팅 시 시작 + 워치독**이 알아서 살린다.
```bash
adb connect 100.103.250.45:5900 && adb devices
```
→ `device` 나오면 끝.

### 안 되면 (수동 복구)
1. 폰: 개발자 옵션 → **무선 디버깅 ON**
2. 폰: Shizuku 앱 열기 → **무선 디버깅으로 시작**
   - 페어링 안 되면 → Shizuku 설정 → **레거시 페어링 ON** 후 재시도
3. 로그에 `Successfully connected on port 5900` 확인
4. PC: `adb connect 100.103.250.45:5900`
5. `unauthorized` 뜨면 → **폰 잠금 해제하고 화면 켠 상태에서** 다시 connect
   → RSA 팝업 → **"항상 허용" 체크** → 허용

---

## 3. 절대 건드리면 안 되는 설정

### 폰 → 개발자 옵션
| 설정 | 상태 | 이유 |
|---|---|---|
| USB 디버깅 | **ON** | 꺼지면 adbd가 인증을 거부 |
| 무선 디버깅 | **ON** | Shizuku 기동 경로 |
| ADB 인증 시간 제한 사용 안 함 | **ON** | 안 켜면 **7일 뒤 승인 만료** |

### 폰 → 설정 → 보안 및 개인정보 보호
| 설정 | 상태 | 이유 |
|---|---|---|
| 보안 위험 자동 차단 | **OFF** | 켜면 USB 디버깅이 스스로 꺼짐 |

### 폰 → Shizuku (thedjchi 포크)
| 설정 | 상태 | 이유 |
|---|---|---|
| 부팅 시 시작 | **ON** | 재부팅 후 자동 복구의 핵심 |
| 지키는 개 (워치독) | **ON** | 삼성이 죽여도 자동 부활 |
| TCP 모드 | **OFF** | 켜면 `tcpip 5555` 실행 → 무선 디버깅을 스스로 꺼버림 |
| TCP 포트 | 5900 | 5555는 에뮬레이터 대역 |
| Auto-disable USB debugging | **OFF** | 켜면 중지할 때 adbd를 죽임 |

### 폰 → 배터리
- Shizuku, Termux: **배터리 제한 없음**
- "사용하지 않는 앱 절전" **OFF**

> ※ 배터리를 "제한 없음"으로 하면 그 앱은 '잠자지 않는 앱' 목록에서 **사라진다**. 정상이다. 제한 없음이 더 강한 설정이므로 목록에 추가할 필요 없음.

---

## 4. 함정 목록 (구축 당일 하루 종일 걸렸음)

### 함정 1 — 5555는 에뮬레이터 대역이다 ★가장 중요
adb 서버는 **5555~5585 홀수 포트를 에뮬레이터로 취급**한다.
5555에 붙으면 `emulator-5554 offline`로 오인되어 인증 흐름이 깨진다.

→ **반드시 5585 초과 포트(5900) 사용.**

### 함정 2 — `offline`과 `unauthorized`는 완전히 다르다
| 상태 | 의미 | 대응 |
|---|---|---|
| `offline` | adbd와 대화 자체가 안 됨 | 포트/tcpip 상태 문제 |
| `unauthorized` | 대화 중, 승인만 남음 | **폰에서 팝업 누르면 끝** |

`unauthorized`가 뜨면 거의 다 온 것이다.

### 함정 3 — RSA 팝업은 잠금 해제 상태에서만 뜬다
폰이 잠겨 있으면 팝업이 **조용히 안 뜨고** `offline`만 반복된다.
반드시 **잠금 해제 + 화면 켠 상태**에서 `adb connect`.
화면 시간 초과를 10분으로 늘려두면 편함.

### 함정 4 — `adb tcpip`는 무선 디버깅을 꺼버린다
`tcpip`를 실행하면 adbd가 레거시 TCP 모드로 재시작되면서 **무선 디버깅이 비활성화**된다.
이 상태는 **재부팅 전까지 유지**되고, 그동안 무선 디버깅으로 뭘 해도 안 된다.

→ 상태가 꼬였다 싶으면 **일단 재부팅**. 그게 가장 빠른 초기화.

### 함정 5 — Tailscale이 켜져 있으면 mDNS 페어링이 안 된다
폰이 무선 디버깅 주소를 `100.x.x.x`(Tailscale)로 광고하는데,
페어링 검색은 로컬 Wi-Fi 인터페이스를 본다 → **"페어링 서비스 검색 중"에서 영원히 멈춤**.

→ 해법 A: Shizuku **레거시 페어링 ON** (코드 직접 입력, mDNS 안 씀)
→ 해법 B: 페어링할 때만 Tailscale 잠깐 끄기

**단, 연결(`adb connect IP:포트`)은 Tailscale로 문제없이 된다.** 페어링(mDNS)만 안 되는 것.

### 함정 6 — 포트는 팝업 띄울 때마다 바뀐다
무선 디버깅의 페어링 포트/연결 포트는 매번 랜덤이다.
스크린샷 찍어둔 숫자는 이미 죽었다고 보면 됨. 그때그때 다시 확인.

### 함정 7 — Termux에서 `settings put`은 막혀 있다
삼성이 `INTERACT_ACROSS_USERS`를 요구해서 앱 컨텍스트에선 실패한다.
`WRITE_SECURE_SETTINGS`를 부여받았어도 안 된다. **정상이다.**
→ 대신 `rish -c 'settings put ...'` 또는 `adb shell settings put ...` 사용.

---

## 5. 이미 적용된 영구 설정 (다시 안 해도 됨)

한 번 넣었고 재부팅해도 유지된다.

```bash
# Termux 백그라운드 면제 4종 — 이미 적용됨
settings put global settings_enable_monitor_phantom_procs false
cmd deviceidle whitelist +com.termux
cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow
cmd appops set com.termux WAKE_LOCK allow

# 권한 — 이미 부여됨
pm grant com.termux android.permission.WRITE_SECURE_SETTINGS
pm grant moe.shizuku.privileged.api android.permission.WRITE_SECURE_SETTINGS
```

이 덕분에 **Termux는 화면을 꺼도, 오래 방치해도 죽지 않는다.**
장시간 파이프라인을 폰에서 돌릴 수 있는 근거가 이것.

---

## 6. 발열 / 배터리 원칙

- adb 연결 대기 + Shizuku 서버: **비용 거의 0** → 켜둬라
- **proot Ubuntu 실행이 진짜 발열 원인** (구축 당일 41°C 기록)
- **원칙: 무거운 작업은 PC(WSL)에서. 폰 proot는 PC 없을 때만.**

Shizuku를 껐다 켜는 습관은 금지. 재기동에 무선 디버깅이 필요해서
꺼둔 사이 상태가 꼬이면 처음부터 다시다. **켜둬라.**

---

## 7. 보안

ADB는 자체 인증이 약하다. 5900이 열려 있으면 닿는 사람은 폰을 다 만질 수 있다.

- **절대 공개 인터넷에 노출 금지.** Tailscale Funnel 금지.
- Tailscale ACL로 PC → 폰 `tcp:5900`만 허용하도록 제한할 것.
- Tailscale 기기 키 만료 켜두면 분실 시 자동 차단.

---

## 8. 문제 생겼을 때 순서표

```
adb devices 결과가...

├─ device            → 정상. 그냥 쓰면 됨.
│
├─ unauthorized      → 폰 잠금 해제 + 화면 켜기
│                      → adb kill-server && adb connect
│                      → 팝업에서 "항상 허용"
│
├─ offline           → adb disconnect && adb kill-server
│                      → adb connect 재시도
│                      → 그래도 offline이면 폰 재부팅
│
└─ 아무것도 안 뜸     → 폰에서 Shizuku 실행 중인지 확인
                       → 안 떠 있으면 §2 수동 복구 절차
```

**막히면 재부팅.** tcpip 잔여 상태가 대부분의 원인이고, 재부팅이 그걸 지운다.

---

## UPDATE (2026-08-21 낮) — 재부팅 자동복구 완성

### 토큰 인텐트로 무인 복구 (수동 구간 제거)

- **토큰**: Shizuku 포크 앱 → 설정 → 고급 → View intents → start 토큰
  - ⚠️ 토큰은 인증 수단 — 문서에 평문 기록 금지. 폰 `~/.termux/boot/00-shizuku.sh`에만.
- **00-shizuku.sh** (Termux:Boot): 부팅 후 30초 간격 START 인텐트 재발사 (최대 10분, 멱등)
  - `am broadcast -a moe.shizuku.privileged.api.START -p moe.shizuku.privileged.api --es token <토큰>`
- **검증됨**: 인텐트가 Termux uid(10xxx)에서 Shizuku 부활 (adb shell 아님 — SSH로 실행해도 Termux 컨텍스트)

### 핵심 통찰 — TCP 모드 = Shizuku 없이도 adb 동작

```
TCP 모드 ON(5900) → adb tcpip 5900 → adbd가 5900 상시 대기
→ Shizuku 꺼져 있어도 adb 5900 device 동작 ✅
→ 재부팅 후에도 tcpip가 살아있으면 adb는 바로 붙음
```

### 워치독 v2 (폰 내부)

- `~/.termux/boot/adb-watchdog-v2.sh` — 5분 간격 adbd/Shizuku/5900 체크 + 자동복구
- 로그: `~/adb_watchdog_v2.log`
- 15~20분마다 삼성이 Shizuku 죽임 → 워치독이 부활시킴 (실전 검증됨)

### 부팅 스크립트 정리

- 제거: adb-auto.sh, adb_restore.sh, adb_wireless.sh (구버전, 백업: `~/.termux/boot_backup_20260821/`)
- 유지: 00-shizuku.sh, adb-watchdog-v2.sh, 00-adb-fix.sh, mcp_watchdog.sh, start_all_mcp.sh, start_sshd.sh, startup.sh

### 알려진 한계

- 재부팅 후 WiFi 붙기까지는 복구 불가 (Android 제약) — 00-shizuku가 10분간 재시도
- 15~20분 사망 주기는 삼성 배터리 정책 — 워치독이 커버
- `adb_wifi_enabled`는 재부팅에 초기화됨 — 인텐트(포크+WSS)가 복구

---

## ✅ FINAL — 재부팅 자동복구 실측 통과 (2026-08-21 오후)

### 검증 결과
```
재부팅 → SSH 15초 복구 → START 인텐트 #1,#2 → Shizuku 기동 → 5900 OPEN → device
```
손 안 대고 무인 복구 확정. 재현 로그: `~/shizuku_boot.log`

### ⚠️ 무인 조건 = WiFi 필수 (중요!)
- 인텐트가 무선디버깅을 켜려면 **네트워크(WiFi) 필수**
- **모바일데이터만 있는 외부에서 재부팅되면 복구 불가** (스크립트 10분 후 실패)
- → "완전 자립"이 아니라 **"WiFi 안에서만 무인"** 이 정확한 표현

### 오늘의 진짜 산출물 (5줄)
1. WSS는 원래 granted — 권한 가설 폐기
2. thedjchi 포크 START 인텐트가 무선디버깅을 스스로 켬 = 순환 차단점
3. 토큰은 앱 UI(View intents)에서만 — shared_prefs는 SELinux 차단
4. TCP모드 5900은 adbd 레벨 = Shizuku 생사 무관 (세션 내 한정, 재부팅은 못 넘음)
5. 30초×20 재발사 루프 = WiFi 감지 대신 멱등 재시도
6. 전제조건: WiFi 필수

### 다음 세션 TODO
- [ ] 워치독 2개(v2 + 포크) 병행 → **1개로 통합** (레이스 방지)
- [ ] 태블릿(tab-s9) Shizuku 적용 — 이 문서 따라가며 재현 검증
- [ ] Tailscale ACL (5900+8022만 허용, Funnel 금지)
