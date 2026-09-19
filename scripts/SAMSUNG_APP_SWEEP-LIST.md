# 삼성 필수앱 스윕 — 성공 18개 리스트 (2026-08-22)

> 원본: WSL `ADB-SAMSUNG-APP-SWEEP-2026-08-22.md` (이 폰으로 SSH 수령, `/root/work/scripts/`에 저장)
> 방법: `adb shell monkey -p <패키지> -c LAUNCHER 1` → `dumpsys` topResumedActivity 확인 → `KEYCODE_HOME` 복귀
> ⚠️ **정직 기록:** 원본 머리글은 "19 OK / 6 FAIL"이나 **표 실측 = 18 OK / 7 FAIL** (삼성 클라우드 포함) — 표 기준 채택.

## ✅ 성공 18개 (표 실측 기준)

| # | 앱 | 패키지명 | 검증 |
|---|----|----------|------|
| 1 | 전화(다이얼러) | `com.samsung.android.dialer` | ✅ WSL 실측 |
| 2 | 계산기 | `com.sec.android.app.popupcalculator` | ✅ WSL 실측 |
| 3 | 뮤직 | `com.sec.android.app.music` | ✅ WSL 실측 |
| 4 | 삼성월렛(Pay) | `com.samsung.android.spay` | ✅ WSL 실측 |
| 5 | 메시지 | `com.samsung.android.messaging` | ✅ WSL 실측 |
| 6 | SmartThings | `com.samsung.android.oneconnect` | ✅ WSL 실측 |
| 7 | 게임런처 | `com.samsung.android.game.gamehome` | ✅ WSL 실측 |
| 8 | 삼성패스 | `com.samsung.android.samsungpass` | ✅ WSL 실측 |
| 9 | 스마트폰 찾기 | `com.samsung.android.app.find` | ✅ WSL 실측 |
| 10 | 삼성헬스 | `com.sec.android.app.shealth` | ✅ WSL 실측 |
| 11 | 삼성노트 | `com.samsung.android.app.notes` | ✅ WSL 실측 |
| 12 | 마이파일 | `com.sec.android.app.myfiles` | ✅ WSL 실측 |
| 13 | 갤러리 | `com.sec.android.gallery3d` | ✅ WSL 실측 |
| 14 | 캘린더 | `com.samsung.android.calendar` | ✅ WSL 실측 |
| 15 | 연락처 | `com.samsung.android.app.contacts` | ✅ WSL 실측 |
| 16 | 삼성 인터넷 | `com.sec.android.app.sbrowser` | ✅ WSL 실측 |
| 17 | 음성녹음기 | `com.sec.android.app.voicenote` | ✅ WSL 실측 |
| 18 | 카메라 | `com.sec.android.app.camera` | ✅ WSL 실측 |

## ❌ 실패 7개 — 3종류 원인

| # | 앱 | 패키지명 | 원인 분류 | 후속 |
|---|----|----------|-----------|------|
| 1 | 삼성 클라우드 | `com.samsung.android.scloud` | 구조적 (독립 런처 없음 — 설정 하위) | 서브 액티비티 지정 (미조사) |
| 2 | 테마스토어 | `com.samsung.android.themestore` | 구조적 (굿락/설정 경유) | 서브 액티비티 지정 |
| 3 | 퀵툴(엣지패널) | `com.sec.android.app.quicktool` | 구조적 (엣지패널 내부 위젯) | 서브 액티비티 지정 |
| 4 | DeX 데스크탑 | `com.sec.android.desktoplauncher` | 구조적 (외부 디스플레이 시에만) | 정상 — 시도 불가 |
| 5 | 빅스비 | `com.samsung.android.bixby.agent` | 구조적 (음성/롱프레스 트리거 전용) | 서브 액티비티 지정 |
| 6 | 리마인더 | `com.samsung.android.app.reminder` | 최초실행 권한팝업 인터셉트 | `pm grant` 사전 부여 (미검증) |
| 7 | 시큐어폴더 | `com.samsung.knox.securefolder` | **의도된 보안 (Knox 격리)** | ⛔ **시도 금지** |

## 실행

```bash
bash /root/work/scripts/samsung_app_launcher.sh --list   # 리스트
bash /root/work/scripts/samsung_app_launcher.sh --all    # 18개 전부 실행
bash /root/work/scripts/samsung_app_launcher.sh 카메라   # 1개 실행
```

**전제:** adb 디바이스 연결 (이 폰 무선디버깅 인증 1회 필요).
