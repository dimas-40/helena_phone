---
date: 2026-08-20
agent: Claude
mark: _Claude
type: infra-setup
status: draft
related:
  - 102-tablet-hw-parse_Grok.md
  - 101-grok-mercenary-3loc_Grok.md
source: dtslib1979/termux-bridge/docs/05-adb/ADB-MESH-AUTO-REVIVE.md (GitHub)
---

# ADB Mesh 자동 복구 — 태블릿(tab-s9) ADB 무선 연결 지식 (2026-08-20)

> 한 장 정리. 나중에 "ADB 설정" 얘기 나오면 이걸 먼저 읽으면 됨.
> 원본 솔루션: `dtslib1979/termux-bridge/docs/05-adb/ADB-MESH-AUTO-REVIVE.md` (2026-05-03 확정).

## 0. 한 줄

```
페어링은 영구, 포트만 휘발성.
한 번 3노드 mesh(WSL↔폰↔탭) 페어링 해두면 평생.
부팅마다 바뀌는 무선디버깅 포트는 nmap으로 5초만에 다시 찾아 연결.
→ adb_revive.sh 한 줄 = 8초 복구, 사람 손길 0.
```

## 1. 왜 ADB 무선이 힘든가 (병목 4가지)

이게 이 환경에서 ADB를 어렵게 만드는 구조적 원인. (내가 2026-08-20 겪은 것 그대로)

| # | 병목 | 영향 |
|---|------|------|
| 1 | 페어링 코드 60초 타임아웃 | STT로 6자리 코드+포트 부르기 거의 불가 |
| 2 | 무선디버깅 포트가 부팅마다 랜덤 변경 | 고정 5555 없음 (Android 보안 설계) |
| 3 | mDNS 자동발견이 Tailscale 위에서 불가 | 멀티캐스트 라우팅 안 됨 |
| 4 | WSL은 USB 직접 못 봄 | Windows adb.exe 우회 필요 |

## 2. 솔루션 — 3노드 mesh + nmap 자동 복구

```
WSL ←→ 폰  (USB 페어링 1회)
WSL ←→ 탭  (자동 페어링)
폰  ←→ 탭  (양방향 페어링) ★ 핵심 — 한 노드 죽으면 다른 노드가 살림
```

- **mesh의 진짜 가치** = WSL이 죽었을 때 폰↔탭끼리 살릴 수 있는 안전망.
- 페어링은 영구 저장. "페어링된 기기" 목록에서 확인.

### 자동 복구 흐름 (`adb_revive.sh phone|tab|all`)
1. 이미 device로 등록? → 끝
2. nmap으로 30000-65535 스캔 (~5초)
3. 후보 포트 4-5개 추출 → 각각 `adb connect` 시도
4. 진짜 device로 등록되는 포트 = 무선디버깅 포트 → 완료
5. 직접 실패 → 살아있는 다른 노드 SSH 경유 mesh 우회

## 3. 현재 IP (⚠️ 2026-08-20 갱신 — 옛 노드 삭제됨)

| 노드 | IP | 상태 |
|------|-----|------|
| **태블릿 (tab-s9)** | **`100.86.15.50`** | ✅ 현재 (Tailscale) |
| ~~탭 옛 노드~~ | ~~`100.74.21.77`~~ | ❌ galaxy-tab-s9-5g, 2026-08-20 삭제 |
| 폰 | `100.103.250.45` | 확인 필요 (문서상 값) |
| WSL (PC) | `100.90.83.128:2222` | SSH |
| Windows | `100.81.24.124:22` | SSH |

⚠️ `adb_revive.sh` 안의 `TAB_IP`가 아직 `100.74.21.77`(옛 노드)로 되어 있음 → **`100.86.15.50`으로 갱신 필요.**

## 4. 이 태블릿 준비 상태 (2026-08-20 실측)

| 항목 | 상태 |
|------|------|
| `adb` (android-tools 36.0.1) | ✅ Termux 설치됨 |
| adbd | ✅ running (`init.svc.adbd: running`) |
| USB 디버깅 | ✅ ON |
| 무선 디버깅 | ⚠️ 설정 화면에서 사람이 ON 해야 함 (proot에서 `settings put` = Permission Denial, `adb tcpip` = no devices) |
| Tailscale | ✅ 100.86.15.50 도달 |
| SSH (Termux sshd) | ✅ 8022 |

## 5. 내가 proot에서 못 하는 것 (삽질 기록)

- `settings put global adb_wifi_enabled 1` → **Permission Denial** (INTERACT_ACROSS_USERS)
- `adb tcpip 5555` (태블릿 자체 실행) → **no devices** (USB로 PC에서 실행해야 함)
- `getprop service.adb.tls.port` → **비어있음/막힘** (proot에선 Operation not permitted, Termux native로도 이 prop 안 보임)
- 무선디버깅 포트/코드 = **회전**(코드 5분 만료, 포트 계속 변경)

→ 결론: **무선 디버깅 ON 토글과 mesh 페어링은 사람/에이전트(PC 쪽)가 해야 함.** 태블릿 안에서 혼자 못 켬.

## 6. 재현 방법 (다음에 ADB 끊겼을 때)

```bash
# WSL 쪽에서:
adb_revive.sh tab     # 탭 복구 (8초)
# 또는 폰/탭 어디서든:
ssh -p 8022 <peer>    # 살아있는 노드로 mesh 우회
```

## 7. 커뮤니티 선례 대비 (정직한 평가)

- 개별 부품(nmap 스캔, 자동 페어링)은 커뮤니티에 이미 있음 (출처 문서에 명시).
- **고유한 건 통합**: Tailscale(mDNS 죽음) + 3노드 무선 mesh + 60초 페어링 자동 우회 + STT + WSL 백업.
- 문서 자체 평가: "기술 천재성 중 · 통합 완성도 상 · 실전 운영 가치 상".
- 운영 철학: "mesh는 안전망이지 의무 시스템이 아님. 하나 죽으면 쉬고 딴 거 하면 됨."

## 8. 진짜 최초 설정 = pm grant (2026-08-20 발견)

원본: `dtslib1979/termux-bridge/widgets/phone/widget_master/9.ultra_adb_setup.sh` (위젯9 "Ultra ADB 최초 설정")

**핵심 한 줄:**
```bash
adb shell pm grant com.termux android.permission.WRITE_SECURE_SETTINGS
```
→ 이 권한을 주면 Termux가 `settings put global adb_wifi_enabled 1` 실행 가능
→ 그때부터 무선 디버깅 ON을 **사람이 손으로 안 켜도 됨** (내가 막혔던 Permission Denial의 정답).

**이 태블릿 준비 상태 (2026-08-20 확인):**
- 부트 스크립트 `~/.termux/boot/adb-tcp.sh` ✅ 이미 배포돼 있음 (루팅/비루팅 분기 + iptables tailscale 제한)
- `WRITE_SECURE_SETTINGS` ❌ 미부여 (settings put → `INTERACT_ACROSS_USERS` Denial)
- `pm grant` 직접 실행 ❌ (`GRANT_RUNTIME_PERMISSIONS` Denial) — **ADB로만 가능**

**남은 1회 (USB 또는 WSL에서):**
```bash
adb shell pm grant com.termux android.permission.WRITE_SECURE_SETTINGS
```
→ 이후 재부팅마다 boot 스크립트가 `adb_wifi_enabled 1` + `adb tcpip 5555` 자동 실행.

*agent mark `_Claude` · 2026-08-20*
