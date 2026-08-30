# ADB 솔루션 — Shizuku + rish 최종 (2026-08-21 실측 확정)

> **결론: PC-ADB 페어링은 폐기. Shizuku + rish로 폰 내부에서 shell uid(2000) 획득 → 백그라운드 면제 완료.**
> USB 불필요. 사무실/같은 WiFi 불필요. Tailscale SSH가 메인 채널.

---

## 1. 왜 이게 답인가

| 접근 | 결과 |
|---|---|
| PC→폰 무선 페어링 (SPAKE2) | ❌ WireGuard/Tailscale 위에서 원천 불가 (03-26/27 삽질 로그 + 08-21 실측) |
| Termux adb localhost pair | ❌ Android 15 pairing 미지원 |
| **Shizuku + rish** | ✅ **폰 내부에서 uid 2000(shell) 획득** — PC 경유 불필요 |

**원리**: `Tailscale SSH → Termux → rish → uid 2000`. Shizuku가 폰이 자기 자신과 페어링해서 shell 데몬을 띄우고, rish가 그 셸을 잡는다. 삼성 버그·mDNS·WSL NAT 전부 무관.

## 2. 실측 이력 (2026-08-21)

### rish 바이너리 버그
- 폰의 `rish`(21512B)가 **librish.so로 잘못 복사**돼 있어서 `rish id` 실행 시 `Illegal instruction` 크래시
- **수정**: APK(`shizuku-v13.6.0`)에서 `assets/rish`(882B 런처 스크립트) + `assets/rish_shizuku.dex` + `lib/arm64-v8a/librish.so` 추출
  - `$PREFIX/bin/rish` = 런처 스크립트 (chmod +x)
  - `$PREFIX/bin/rish_shizuku.dex` = dex (chmod 400, Android 14+ 필수)
  - `$PREFIX/lib/librish.so` = 네이티브 라이브러리
- 런처에서 `RISH_APPLICATION_ID="PKG"` → `"com.termux"`로 수정

### 권한 팝업 (핵심!)
- 첫 `rish` 실행 시 Shizuku가 **권한 요청 다이얼로그**를 폰 화면에 띄움
- **SSH(원격)로만 실행하면 팝업을 누를 사람이 없어 조용히 실패**
- **해결**: 폰에서 Termux 앱 직접 열고 `rish` 실행 → "허용" 탭 → 이후 SSH로도 사용 가능

### rish 사용법 (SSH)
```bash
# -t (TTY) 필수! rish는 TTY 없으면 조용히 실패
ssh -tt -p 8022 100.103.250.45 'rish -c "id"'
# → uid=2000(shell) ... context=u:r:shell:s0
```

## 3. 백그라운드 면제 명령 (적용 완료, 재부팅 유지)

```bash
rish -c 'settings put global settings_enable_monitor_phantom_procs false'   # phantom 킬 비활성화
rish -c 'cmd deviceidle whitelist +com.termux'                              # Doze 면제
rish -c 'cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow'             # 백그라운드 허용
```

**검증 결과**: `false` / `Added: com.termux` / `allow` — 3종 모두 적용 확인.

## 4. 삼성 서버 유지 (Shizuku 안 죽게)

- **개발자 옵션 → 기본 USB 설정 = "충전만"** (또는 "디버깅 전용") — adbd/Samsung 서비스 안정화
- **설정 → 배터리 및 기기 관리 → 배터리 → 백그라운드 사용 제한 → "잠자지 않는 앱"** 에 Shizuku + Termux 추가 (배터리 무제한과 별개!)
- Shizuku 서버가 죽으면 앱에서 "무선 디버깅으로 시작" 재실행 (재부팅 후 1회)

## 5. 최종 아키텍처

```
[폰] Shizuku server (shell uid) ← rish
   ↑ SSH(8022)
[WSL/PC] Tailscale → ssh -tt → rish -c "명령"
```

- Termux 데몬 안 죽음 (phantom/Doze 면제)
- `settings put global`, `cmd appops`, `cmd deviceidle` 등 shell 권한 작업 가능
- scrcpy 미러링이 진짜 필요할 때만 별도 접근 (그때도 이 구조 활용)

## 6. 참고 문서

- `termux-bridge/logs/ParksyLog_20260326_ADB무선디버깅_삽질.md`
- `termux-bridge/logs/ParksyLog_20260327_ADB완전개통_세션총결산.md`
- `termux-bridge/docs/05-adb/ADB-WHITEPAPER-2026-06-16.md`
- `dtslib-papyrus/ADB-숙제-2026-08-21.md`
- Shizuku GitHub: RikkaApps/Shizuku (이슈 #1459, #1426, #612, #472 — 삼성 서버 킬)

---

## 🏆 최종 성공 UPDATE (2026-08-21 새벽) — REAL ADB 완성

```
100.103.250.45:5900  device  model:SM_S938N
uid=2000(shell)  context=u:r:shell:s0
```

### 진짜 원인 (하루 종일의 정답)
**5555 = adb 에뮬레이터 대역(5555~5585).** 이 폰에서 5555는 adb가 에뮬레이터로 오인해서 `emulator-5554 offline` 상태 → 어떤 클라이언트도 핸드셰이크 불가.

### 해법 (완성 레시피)
1. **재부팅** → `service.adb.tcp.port=5555` 잠금 해제
2. Shizuku 포크 설정 → **TCP 포트 = 5900** (에뮬레이터 대역 밖)
3. 포크 "무선 디버깅으로 시작" → `Successfully connected on port 5900` → 서버 기동
4. **RSA "항상 허용"** → WSL adb `device` 완성
5. `adb tcpip 5900` 유지 → WSL `adb connect 100.103.250.45:5900`

### 사용법
```bash
adb connect 100.103.250.45:5900   # 필요할 때
adb devices                        # device 확인
adb -s 100.103.250.45:5900 shell   # uid 2000 셸
scrcpy -s 100.103.250.45:5900 --max-size 1024   # 화면 미러링
~/bin/pw on|off                    # proot 스위치 (Shizuku/adb는 상시)
```

### 재부팅 대비 (필수 2개)
1. 개발자 옵션 → **ADB 인증 시간 제한 사용 안 함 ON** (7일 만료 방지)
2. Shizuku 포크 → **부팅 시 시작 ON** (재부팅 후 tcpip 5900 복구)
