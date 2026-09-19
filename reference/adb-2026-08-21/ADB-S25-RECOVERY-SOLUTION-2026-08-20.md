# ADB S25 Ultra — 오진단 정정 + 진짜 복구 솔루션

> 날짜: 2026-08-20
> 결론: "네임스페이스 격리로 Tailscale 경유 ADB 불가" = 오진단. 무선디버깅 토글 꺼짐이 1차 원인.
> 원본 근거: termux-bridge/docs/05-adb/ADB-WHITEPAPER-2026-06-16.md

---

## 1. 결론 (한 줄)

ADB over Tailscale은 **2026-06-16에 이미 성공했다.** 지금 안 되는 건
Samsung/네임스페이스 문제가 아니라 **무선디버깅 토글이 꺼져 있는 것**.
SSH fallback은 임시방편으로 두고, 무선디버깅 재활성화 → 기존 자동복구 체인 회귀가 정답.

## 2. 근거 (실측)

| 항목 | 값 | 해석 |
|---|---|---|
| 6/16 백서 ADB 상태 | `100.103.250.45:40083 device` (TLS) / `:5555 device` (legacy) | Tailscale IP로 ADB device 연결 성공했었음 |
| 현재 `getprop service.adb.tls.port` | (빈 값) | 무선디버깅 포트 미활성 = 꺼짐 |
| 현재 `settings get global adb_wifi_enabled` | (빈 값) | 무선디버깅 꺼짐 |
| 현재 `adb devices` | `:35517 offline`, `:5555 offline` | 옛 transport 잔재(offline), adbd 미수신 |
| WSL `adb-connect.sh` cron | `* * * * *` (1분) | 자동복구 크론 동작 중 |
| 폰 `~/.termux/boot/adb_restore.sh` | 존재 | 재부팅 시 TLS 포트 저장 스크립트 살아있음 |
| WSL `adb-connect.sh` / `adb_revive.sh` / `adb-watchdog.sh` | 전부 존재 | 복구 체인 인프라 멀쩡 |

## 3. 8/20 진단의 오류

| 기존 주장 | 판정 |
|---|---|
| "Android 시스템 네임스페이스 격리로 Tailscale/WSL 경유 접근 불가" | ❌ 6/16 실측(`:40083 device`)으로 반증 |
| "adb pair TLS 핸드셰이크 Samsung 버그로 cert 저장 실패" | ⚠️ 근거 없음. 출처/재현실험 필요 |
| "SSH(8022)로 대체가 답" | ⚠️ scrcpy/pm grant/앱제어 포기하는 퇴보 |

## 4. 진짜 솔루션 (더 좋은 방법)

1. S25 개발자옵션 → 무선디버깅 **재활성화** (토글 ON)
2. 인증 재등록 — TLS(`adb pair IP:포트 코드`) 또는 legacy(`adb tcpip 5555`, USB 1회)
3. 이후 기존 체인이 자동 복구:
   - 폰 재부팅 → `adb_restore.sh`가 TLS 포트 저장
   - WSL `adb-connect.sh`(cron 1분)이 SSH로 포트 읽어 `adb connect`
4. SSH는 fallback으로만 유지 (위젯 8번은 그대로)

## 5. 복구 후 기대 상태

```
100.103.250.45:<tls>    device (TLS 인증)
100.103.250.45:5555     device (legacy TCP)
```

## 6. 추가 스터디 (콘텐츠 소재)

1. 무선디버깅이 왜 꺼졌나 — 재부팅 / Android·Samsung 업데이트 / 토글 이벤트 추적
2. "Samsung cert 저장 실패" 재현실험 + 문서화된 버그인지 근거 확보
3. 재페어링 자동화 — 백서의 "화면 자동조작 pair 등록"을 스크립트로 재현 가능한가
4. legacy 5555 vs TLS 포트 — 재부팅 후 어느 쪽이 더 오래 유지되는가

## 7. 핵심 인사이트 (대중 콘텐츠용)

> "망했다고 SSH로 도망쳤는데, 알고 보니 토글 하나 꺼져 있던 거였다."
> ADB를 포기하지 마라. 꺼진 걸 켜면 이미 만들어 둔 복구 체인이 다 알아서 한다.
