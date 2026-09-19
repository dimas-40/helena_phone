# ADB 안 되는 이유 분석 — 왜 하루가 걸렸나 (교재용 챕터)

> 2026-08-21 실측 기반. "성공 레시피는 널렸는데 왜 안 되는지는 없다" — 그 빈칸을 채우는 장.

## 1. 5555 = 에뮬레이터 대역 함정 (오늘의 진짜 범인)

```
5555~5585 = adb 에뮬레이터 포트 대역
adb는 5555 연결을 무조건 에뮬레이터로 취급 → emulator-5554 offline
```

- `adb tcpip 5555`로 설정해도, 연결하면 adb가 "에뮬레이터"로 오인
- 상태가 `offline` = **핸드셰이크 불가** (에뮬레이터 프로토콜을 기대)
- **증상**: 하루 종일 모든 클라이언트(WSL/폰 자체 adb/Shizuku)가 5555에서 실패
- **해법**: `adb tcpip 5900` (5585 초과) → 정상 기기로 인식

## 2. offline vs unauthorized — 완전히 다른 상태

| 상태 | 의미 | 대응 |
|---|---|---|
| `offline` | adbd가 응답 안 함 (대화 자체 불가) | 포트/모드 문제 |
| `unauthorized` | adbd 살아있음, 승인만 남음 | RSA 팝업 → "항상 허용" |
| `device` | 완성 | — |

- 하루 종일 `offline` → 포트 문제였음 (5555 대역)
- `unauthorized`가 뜨면 그건 "거의 됐다"는 신호

## 3. Tailscale(WireGuard)과 mDNS 페어링의 구조적 충돌

- 무선 디버깅 페어링(mDNS/SPAKE2)은 로컬 네트워크 가정
- Tailscale은 CGNAT 대역(100.x) → mDNS 광고가 tailscale0에 뜸
- Shizuku는 wlan0에서 찾음 → 서로 다른 인터페이스 → 영원히 못 만남
- **해법**: mDNS 페어링 대신 IP:PORT 직결(legacy tcpip) 사용

## 4. Shizuku 포크 TCP 모드 = 5900 설정이 먹히려면 재부팅 필요

- thedjchi 포크: TCP 포트 설정(5900)이 있지만, `service.adb.tcp.port=5555` 잠금 상태에선 무시됨
- **순서**: 재부팅(잠금 해제) → 포크 TCP 5900 설정 → 무선 시작
- 워치독은 Shizuku 서버만 살리고, adbd TCP 모드는 부팅 시 시작이 복구

## 5. 삼성 특이사항 모음

- `service.adb.tls.port` getprop = **Access denied** (앱이 못 읽음) → 부팅 스크립트 자동복구 깨짐
- `settings` CLI = INTERACT_ACROSS_USERS 필요 (WRITE_SECURE_SETTINGS만으론 부족)
- RSA 팝업은 **폰 잠금 해제 상태에서만** 표시
- Auto Blocker / VPN / 네임스페이스 격리는 **오진이었음** (전부 무관)

## 결론 (교재용 한 줄)

> ADB가 "안 되는" 이유는 대부분 포트 대역·상태 머신·네트워크 인터페이스의 **조합**이고,
> `offline`을 보면 포트를 의심하고, `unauthorized`를 보면 거의 다 됐다고 생각하라.
