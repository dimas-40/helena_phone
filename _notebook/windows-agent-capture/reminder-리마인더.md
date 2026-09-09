# 박씨PC 세션 리마인더 (현재 상태) — 2026-09-09

> ⭐ 이 문서 하나만 읽으면 끊긴 세션을 즉시 복구할 수 있다.
> 세션이 끊겼다가 다시 열리면, 이 파일을 먼저 읽고 아래 "다음 세션 즉시 실행"부터 이어가면 된다.

---

## 0. 이 스레드의 주제 (4대 축)

1. **원격 (Remote)** — 어디서든 랩탑/미니PC 접속·복구
2. **Windows 환경 분산 관리** — OS를 여러 물리 매체(NVMe/WTG/microSD/미니PC)로 분산
3. **WSL 관리** — 개발 본진(WSL)을 어떻게 관리할 것인가
4. **미니PC 관제 허브** (신규) — 랩탑 전체가 죽어도 살아있는 독립 상위 레이어

> 장비: Dell XPS 13 9370(랩탑) / WD My Passport 2TB / dev-batch 미니PC(Linux) / S25 Ultra(폰) / Tab S9

---

## 1. 현재 진행 상황 (한 줄)

**미니PC를 "관제 허브"로 만들기 위해, Windows PC와 동일한 Termius→에이전트 구조(SSH 22/2201/2202 + Claude/DeepSeek)를 미니PC에 설치하는 작업 중이다.**

- 미니PC의 sshd가 과부하로 멈춰 있어서(배너 무응답) → **사용자가 물리 리부팅하러 감.**
- **리부팅 완료 후 설치 실행이 곧바로 다음 단계다.**
- 설치 플레이북은 이미 작성 완료 → 리부팅만 되면 바로 실행.

---

## 2. 핵심 아키텍처 (레이어 모델 — 이게 이 스레드의 뼈대)

```
[폰] ─ Termux (mosh) ─▶ WSL      ← 하위 레이어 (Windows 안의 VM)
      └ Termius (SSH) ─▶ Windows  ← 상위 레이어
      └ Termius (SSH) ─▶ 미니PC(Linux) ← 독립 상위 레이어 (랩탑 죽어도 생존)
```

- **Termux 채널 = mosh → WSL.** WSL은 Windows 위에서 돌므로, Windows가 떨어지면 WSL도 같이 죽는다. → Termux 채널도 같이 끊긴다.
- **Termius 채널 = SSH → Windows.** WSL이 죽어도 Windows는 살아있어서, Termius로 Windows에 들어가 `wsl --start`로 WSL을 재호출한다. → **"상위 레이어에서 재호출"** 목적.
- **미니PC = 물리적으로 분리된 독립 Linux.** 랩탑의 Windows/WSL이 통째로 죽어도 생존. → 관제 허브.
- 원칙: **"OS는 자기 자신을 못 고친다. WSL↔Windows 교차 복구."**

> ⚠️ 정확한 기준은 "연결 방향"이 아니라 "레이어(WSL vs Windows vs 독립머신)"다. (사용자가 명시적으로 교정한 부분)

---

## 3. 실측 상태 (2026-09-09 세션에서 측정)

### 네트워크/기기
| 항목 | 값 |
|---|---|
| 랩탑 유선 | 192.168.219.104 (Realtek USB GbE, Dell DA310), 1Gbps |
| 게이트웨이 | 192.168.219.1 (라우터) ← "직결" 아님, LAN 경유 |
| 미니PC LAN | 192.168.219.101 (MAC 18:60:24:23:3e:00), ping 0ms |
| 미니PC Tailscale | 100.81.134.89 (dev-batch) |
| 미니PC 열린 포트 | **22 하나뿐** (ssh 배너 무응답 = sshd 멈춤/과부하) |
| 폰 SSH | 100.103.250.45:8022 ✅ 접속됨 (Termux, u0_a445) |
| 폰 → 미니PC | ❌ 100% 손실 (LAN·Tailscale 둘 다) |
| 폰 Tailscale CLI | ❌ SIGSYS 크래시 (daemon은 정상) |

### ADB 토폴로지
| 연결 | 상태 |
|---|---|
| 랩탑(ADB host) → 폰 | ✅ `adb devices` = SM-S938N @ 100.103.250.45:5900 (네트워크 ADB) |
| 폰(ADB host) → ? | `adb devices` = 빈 목록 |
| 미니PC ADB(5555) | ❌ 닫힘 |

### Windows 원본 에이전트 구조 (복제 대상)
```
sshd_config:
  Port 22 / 2201 / 2202
  Match LocalPort 2201 → ForceCommand claude   (Claude Code)
  Match LocalPort 2202 → ForceCommand ds       (DeepSeek)
```
- `ds` = Claude Code 바이너리를 DeepSeek V4 Flash 백엔드로 돌리는 래퍼.
  - `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`
  - 키: `C:\Users\dtsli\.claude-deepseek\ANTHROPIC_API_KEY.txt`
  - 설정: `C:\Users\dtsli\.claude-deepseek\settings.json` (model=deepseek-v4-flash)
- `claude` = 공식 Claude Code (`C:\Users\dtsli\AppData\Roaming\npm\claude`)

---

## 4. 이 세션에서 만든 파일

| 파일 | 상태 | 설명 |
|---|---|---|
| `C:\Users\dtsli\박씨PC\리마인더.md` | ✅ | **이 문서** — 세션 재개용 |
| `C:\Users\dtsli\박씨PC\설정\mini-pc-agent-setup.sh` | ✅ (189줄, 문법 OK) | 미니PC 설치 플레이북 |
| `C:\Users\dtsli\박씨PC\설정\mini-pc-termius-호스트.md` | ✅ | Termius(폰)에 넣을 호스트 3종 |
| `C:\Users\dtsli\박씨PC\로그\2026-09-09-세션-랩탑-WSL-WTG-포렌식.md` | ✅ (253줄) | 1차 포렌식 로그 (WSL/WTG 전수조사) |
| `C:\Users\dtsli\박씨PC\로그\2026-09-09-세션-원격-Windows분산-WSL관리.md` | ⚠️ 부분작성 | 주제 재구성본 (chunk1만 작성, 리마인더가 대체) |
| `C:\Users\dtsli\박씨PC\INDEX.md` | ✅ | 인덱스 |

### 미니PC 설치 플레이북이 하는 일
1. 패키지(sshd/curl/git/python3/node20/npm) 설치
2. Claude Code npm 설치
3. 래퍼 `/usr/local/bin/claude-agent`(공식) / `ds-agent`(DeepSeek) 생성
4. sshd에 Port 22/2201/2202 + Match LocalPort ForceCommand 추가
5. Tailscale 확인/설치
6. 검증(sshd -t, 포트 리스닝)

---

## 5. 다음 세션 즉시 실행 (체크리스트)

### ① 미니PC sshd 부활 확인
```bash
ssh -o BatchMode=yes -o ConnectTimeout=6 -i /c/Users/dtsli/.ssh/id_ed25519 dtsli@192.168.219.101 'echo ALIVE; whoami; hostname; uname -a'
```
- 실패 시 `root@192.168.219.101`도 시도. (유저 미확정)
- 미니PC OS/distro 확인되면 플레이북의 패키지 매니저 분기가 자동 동작.

### ② 플레이북 실행 (ssh로 stdin 파이프)
```bash
ssh dtsli@192.168.219.101 'bash -s' < "/c/Users/dtsli/박씨PC/설정/mini-pc-agent-setup.sh"
```

### ③ DeepSeek API 키 주입
```bash
cat /c/Users/dtsli/.claude-deepseek/ANTHROPIC_API_KEY.txt | \
  ssh dtsli@192.168.219.101 'cat > ~/.claude-deepseek/ANTHROPIC_API_KEY.txt'
```

### ④ 검증
```bash
ssh dtsli@192.168.219.101 'ss -ltnp | grep -E ":22 |:2201 |:2202 "'
# 그리고 실제 스모크 테스트: 2201→claude, 2202→ds 배너 확인
```

### ⑤ 랩탑 ~/.ssh/config에 미니PC 3항목 추가
```
Host mini          HostName 192.168.219.101  Port 22    User dtsli  IdentityFile ~\.ssh\id_ed25519
Host mini-claude   HostName 192.168.219.101  Port 2201  User dtsli  IdentityFile ~\.ssh\id_ed25519
Host mini-ds       HostName 192.168.219.101  Port 2202  User dtsli  IdentityFile ~\.ssh\id_ed25519
```

### ⑥ 이후 미결 (사용자 확인 후 진행)
1. **미니PC → 폰 역방향** (ssh/adb) — 양방향 한 몸통 완성용 (사용자 확인 필요)
2. **폰→미니PC Tailscale** 안 뚫리는 문제 — 리부팅 후 재측정, ACL이면 수정
3. **진짜 직결 케이블** (직결 이더넷 / USB 가젯 / HID 가젯 중 택) — 라우터 무관 OOB 레이어
4. 기존 미결: wsl-min 정리, BIOS AC Recovery, WTG F12 실검증, 복구문서 기종교정(9570→9370), WSL 기동

---

## 6. IP / GUID 참조표

| 항목 | 값 |
|---|---|
| Windows PC (NVMe) | 100.81.24.124 |
| WSL (랩탑 Ubuntu) | 100.90.83.128 (SSH :2222) |
| 미니PC (dev-batch) | 192.168.219.101 / 100.81.134.89 |
| 폰 (S25 Ultra) | 100.103.250.45 (SSH :8022, ADB :5900) |
| Tab S9 | 100.86.15.50 (:8022) |
| WTG EFI GUID | {c8308535-39f2-11f1-9f65-806e6f6e6963} |
| NVMe GUID | {0f75cbeb-3c54-11f1-9f6e-806e6f6e6963} |

---

## 7. 비밀/키 파일 위치 (값은 파일에만, 평문 노출 금지)

- DeepSeek(Anthropic 호환) 키: `C:\Users\dtsli\.claude-deepseek\ANTHROPIC_API_KEY.txt`
- DeepSeek 설정: `C:\Users\dtsli\.claude-deepseek\settings.json` (GitHub PAT도 여기 있음)
- SSH 키: `C:\Users\dtsli\.ssh\id_ed25519` (+ .pub)

> 🔁 세션 재개 시: 이 파일을 읽고 "5. 다음 세션 즉시 실행"부터 시작하면 된다.
