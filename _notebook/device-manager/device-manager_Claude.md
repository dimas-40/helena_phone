---
date: 2026-08-18
agent: Claude Code (출판부)
mark: _Claude
type: reference
status: active
source: 실측 (proot Ubuntu 26.04 on Galaxy Tab S9 · remote dimas-40)
related:
  - 102-tablet-hw-parse_Grok.md
  - tablet-broadcast-studio_Claude.md
  - tablet-setup-parksy-method_Claude.md
---

# 장치 관리자 (Device Manager) — 이 태블릿에서 커맨드로 건드릴 수 있는 것 / 없는 것

> **발단:** Boss가 "Galaxy 태블릿 잠금 화면 좀 없애라 / 찾고 잠기는 게 싫다"고 함.
> 이 방(proot Ubuntu on Tab S9)에서 **장치 설정을 커맨드로 관리할 수 있는 범위**를 실측해 한 장에 정리.
> 이 수첩이 "장치 관리자" 폴더의 기준 문서다. 이후 장치 제어 실측은 여기 아래로 쌓는다.

---

## 0. 한 줄 판정

```
이 방은 Termux(untusted_app) 위 proot Ubuntu = "가짜 root".
Android 보안 설정을 바꾸는 바이너리는 전부 SELinux가 차단.
→ 잠금 화면 / 원격 잠금 / 권한 등 "OS 보안 레버"는 여기서 못 건드림.
→ 읽기(하드웨어 실측, /sdcard)는 됨. 쓰기는 사용자 파일 영역만.
```

---

## 1. 실측 매트릭스 (2026-08-18 · 이 방에서 직접 때려본 결과)

| 시도 | 결과 | 판정 |
|------|------|------|
| `/system/bin/settings` (읽기·쓰기) | `Operation not permitted` | ❌ 차단 |
| `/system/bin/locksettings` | `Operation not permitted` | ❌ 차단 |
| `/system/bin/am` / `cmd` / `pm` | `Operation not permitted` | ❌ 차단 |
| `getprop` / `toybox` | `Operation not permitted` | ❌ 차단 |
| `termux-am start` (설정 화면 열기) | `Could not connect to socket` | ❌ Termux:API 앱 없음 |
| `termux-battery-status` · 갤러리 스캔 | 없음 (Termux:API 미설치) | ❌ |
| `/sdcard` 읽기·쓰기 (DCIM/Documents 등) | bind OK | ✅ |
| 하드웨어 실측 (CPU/GPU/저장/열) | `/sys`, `/proc` 일부 읽힘 | ✅ |
| Termux prefix (`/data/data/com.termux/files/usr`) | reachable | ✅ |
| grok / claude / node / python / git | 동작 | ✅ |

> **핵심:** "읽기·사용자 파일 영역"은 되고, "시스템 설정 변경"은 전부 막힌다.

---

## 2. 왜 막히는가 — 벽의 정체

1. **가짜 root.** `id`는 `uid=0`이지만 이건 proot이 흉내 낸 것. 실제는 Termux 앱 권한.
2. **SELinux 도메인 = `untrusted_app_27`** (`/proc/self/attr/current` 실측). 이 도메인은
   `settings`/`locksettings`/`am`/`cmd`/`pm` 같은 Android 시스템 바이너리 실행 자체를 거부.
3. **bionic/glibc ABI 벽.** 벤더 `.so`(bionic)는 proot(glibc)에서 `dlopen` 불가 — GPU/NPU 직통이
   막히는 것과 같은 벽. (`102-tablet-hw-parse_Grok.md` §4와 동일)

> 쉽게: 우리는 이 태블릿의 "손님(앱)"이지 "주인(root)"이 아니다. 손님 방(사용자 파일)은
> 쓰게 해주지만, 현관문 잠금장치(잠금 화면·보안 설정)는 못 고치게 해놨다.

---

## 3. 발단 건 — 잠금 화면 (여기서 못 푼다)

**일반 잠금 화면** 없애기 = 태블릿 화면에서 직접 (30초):
```
설정 → 잠금 화면 → 화면 잠금 방식 → "없음" 또는 "스와이프"
```

**"찾고 잠기는" 원격 잠금** = 별개. 삼성/구글 원격 찾기 기능이 강제 잠금:
```
설정 → 생체 인식 및 보안 → 내 모바일 찾기 → 끄기
설정 → Google → 내 기기 찾기 → 끄기
```

> 내가 여기서 대신 해줄 수 있는 손잡이는 **없음** (위 매트릭스로 확인). 사람 손 + 화면 조작이 필요.

---

## 4. 앞으로 — 커맨드 제어를 진짜 열려면

| 경로 | 필요 조건 | 상태 |
|------|-----------|------|
| **Shizuku (F-Droid)** ⭐ | 무선 디버깅 페어링(화면 1회) → Shizuku 시작 → 셸로 `locksettings` | ⏳ 미셋업 (권장) |
| **adb (무선 디버깅)** | 개발자 옵션 → 무선 디버깅 ON + 페어링 코드 → Termux에 `adb` 설치 | ⏳ 미셋업 |
| root | 하지 않음 (설계 원칙) | ❌ |
| Termux:API 앱 | F-Droid에서 설치 | ⏳ 미설치 |

### 4-1. Shizuku — "나 같은 놈"을 위한 오픈소스 정답 (2026-08-18 실측·검색)

- **뭐냐:** F-Droid 무료·오픈소스. **root 없이** 다른 앱에 **adb(셸) 권한**을 빌려주는 브릿지.
  무선 디버깅으로 돌아서 **PC 불필요**. (패키지 `moe.shizuku.privileged.api`)
- **세팅 (1회, 태블릿 화면):**
  1. 설정 → 개발자 옵션 켜기 (빌드 번호 7번 탭) → **무선 디버깅** ON
  2. Shizuku → **Pairing** → "페어링 코드로 페어링" → 6자리 코드 입력
  3. Shizuku → **Start**
- **잠금 화면 OFF (셸 명령):**
  ```sh
  locksettings clear --old <현재PIN>   # 기존 PIN/패턴 있으면 먼저 제거
  locksettings set-disabled true        # 잠금 화면 비활성화
  locksettings get-disabled             # 확인
  ```
- **주의:**
  - **재부팅마다 Shizuku 재시작 필요** (서비스가 유지 안 됨).
  - 삼성 One UI에서 동작하나, 재부팅 후 자동 시작은 별도 조치 필요.
  - Shizuku는 **"찾고 잠기는" 원격 잠금(내 모바일 찾기)은 못 막음** — 그건 §3 계정 설정에서 꺼야 함.

- adb가 붙으면 `adb shell locksettings set-disabled true --user 0` 한 줄로 잠금 화면 OFF 가능.
- **단, 페어링은 태블릿 화면에서 한 번 손으로 해야 한다** (보안상 자동화 불가).

---

## 5. 이 수첩의 쓰임

- 이 폴더(`_notebook/device-manager/`)는 **장치 관리 실측의 기준점**. 이후 장치 제어 시도(되면/안 되면)는
  여기에 새 파일로 쌓는다.
- 판정 기준은 항상 **"구동이 되는가"** (말이 아니라 실측).
- 에이전트 마크 `_Claude` 유지, 다른 에이전트 마크 파일은 덮어쓰지 않는다.

*실측 · agent mark `_Claude` · 2026-08-18*
