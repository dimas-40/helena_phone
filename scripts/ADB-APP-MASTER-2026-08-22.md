# ADB 앱 모듈 마스터 — 삼성 필수앱 25종 전수 실측 (2026-08-22)

> **베이스라인 선언 (Boss 확정):** 이 문서는 **"폰 앱 = 콘텐츠 생산 모듈"**로 쓰는 기준선이다.
> 이 베이스라인을 계속 **뜯어 고치고 확장해서** 콘텐츠를 만든다. (패치테크 드라이버)
> 수정·확장 시 이 문서를 갱신하고 날짜·누가(_Claude/_Grok/_Aider/_Boss)를 남긴다.

---

## 1. 이게 뭔가

- 폰의 **삼성 필수앱 25종**을 adb로 **즉시 실행 가능한 모듈**로 만든 것.
- **방법:** `adb shell monkey -p <패키지> -c LAUNCHER` — **패키지명만 알면 액티비티명 몰라도 즉시 실행**.
- **용도 (1인 미디어 생산):** 카메라→촬영 · 음성녹음기→VO · 갤러리→이미지 소스 · 노트→원고 · 문자→수신확인 등. 예전 회사/에이전시가 하던 생산 공정을 폰 앱 모듈로 압축.
- **원본 실측:** WSL 세션 `~/termux-bridge/docs/05-adb/ADB-SAMSUNG-APP-SWEEP-2026-08-22.md` (커밋 04543cf). **2026-08-22 SSH로 이 폰에 수령** → `/root/work/scripts/ADB-SAMSUNG-APP-SWEEP-2026-08-22.md` + `SAMSUNG-FRIENDLY-ADB-CONTENT-GUIDE-2026-08-22.md` 저장. **이 마스터 = 폰 워크센터 SSOT** (패키지명·수치는 원본 표 기준).

---

## 2. 전수 실측 결과 (25종)

### ✅ 성공 18개 — WSL 실측 확정 (표 기준)

> ⚠️ **19 vs 18 불일치 해소 (원본 표 기준 채택):** WSL 머리글은 "19 OK / 6 FAIL"이나
> **실측 표 = 18 OK / 7 FAIL** (삼성 클라우드 = 7번째 FAIL, 요약에서 누락). 숫자는 표 기준 확정.
> 패키지명 4건 보정 완료 (연락처 · 삼성월렛 · 스마트폰찾기 · 게임런처 — 아래 굵게).

| # | 앱 | 패키지명 | 검증 |
|---|----|----------|------|
| 1 | 전화(다이얼러) | `com.samsung.android.dialer` | ✅ WSL 실측 |
| 2 | 문자(메시지) | `com.samsung.android.messaging` | ✅ WSL 실측 |
| 3 | 카메라 | `com.sec.android.app.camera` | ✅ WSL 실측 |
| 4 | 음성녹음기 | `com.sec.android.app.voicenote` | ✅ WSL 실측 |
| 5 | 노트 | `com.samsung.android.app.notes` | ✅ WSL 실측 |
| 6 | 갤러리 | `com.sec.android.gallery3d` | ✅ WSL 실측 |
| 7 | 마이파일 | `com.sec.android.app.myfiles` | ✅ WSL 실측 |
| 8 | 캘린더 | `com.samsung.android.calendar` | ✅ WSL 실측 |
| 9 | **연락처** | **`com.samsung.android.app.contacts`** | ✅ WSL 실측 |
| 10 | 삼성인터넷 | `com.sec.android.app.sbrowser` | ✅ WSL 실측 |
| 11 | 뮤직 | `com.sec.android.app.music` | ✅ WSL 실측 |
| 12 | 계산기 | `com.sec.android.app.popupcalculator` | ✅ WSL 실측 |
| 13 | 삼성헬스 | `com.sec.android.app.shealth` | ✅ WSL 실측 |
| 14 | 삼성패스 | `com.samsung.android.samsungpass` | ✅ WSL 실측 |
| 15 | **삼성월렛(Pay)** | **`com.samsung.android.spay`** | ✅ WSL 실측 |
| 16 | **스마트폰찾기** | **`com.samsung.android.app.find`** | ✅ WSL 실측 |
| 17 | SmartThings | `com.samsung.android.oneconnect` | ✅ WSL 실측 |
| 18 | **게임런처** | **`com.samsung.android.game.gamehome`** | ✅ WSL 실측 |

### ❌ 실패 7개 — "못 뚫음"이 아니라 4종류로 다름

| # | 앱 | 원인 분류 | 후속 (뜯어 고치기) |
|---|----|-----------|-------------------|
| 1 | 삼성 클라우드 | **독립 런처 없음** — 설정 하위 진입만 가능(추정) | 서브 액티비티 지정 (미조사) |
| 2 | 테마스토어 / 퀵툴(엣지패널) / 빅스비 / DeX | **독립앱 아님** — 진입점이 다른 화면 하위에 물림 | 서브 액티비티 직접 지정 (미조사 → 다음 단계) |
| 3 | 리마인더 | **최초실행 권한팝업**이 가로챔 | `pm grant` 사전 부여로 뚫릴 것 (미검증) |
| 4 | 시큐어폴더 | **진짜 의도된 보안** — Knox TrustZone 격리, shell로 절대 불가 | ⛔ **시도 금지** (함정6급 — 잠금화면 뜨면 즉시 중단, 재시도 금지) |

---

## 3. 실행 인프라 (ADB)

- **3노드 메시:** WSL ↔ 폰(S25) ↔ 탭 — 무선디버깅 + Tailscale. 자동복구: `adb_revive.sh` (mesh, 포트 자동발견).
- **폰 IP:** `100.103.250.45` (Tailscale). **탭 IP:** `100.74.21.77`.
- **이 폰(S25) 실측 (2026-08-22):**
  - 무선디버깅 **살아있음** — Tailscale IP 포트 `40837`이 adb handshake 수용.
  - ⚠️ proot의 adb RSA 키 **미인증** → offline. 폰에서 "허용" 탭 1회 (또는 `adb pair` 코드) 필요.
  - tailscaled는 proot에서 안 돌고 Android 앱으로 동작.

---

## 4. 자동화 (워크센터)

| 파일 | 역할 |
|------|------|
| `scripts/samsung_app_launcher.sh` | 매니페스트 내장 런처. `adb shell monkey -p <pkg> -c LAUNCHER` + 기기 `pm list`/`pidof` 자가검증 + 시큐어폴더 금지 가드. `--list / --all / <앱>` 3모드 |
| `scripts/SAMSUNG_APP_SWEEP-LIST.md` | 이 마스터의 축약 리스트 |
| `scripts/ADB-SAMSUNG-APP-SWEEP-2026-08-22.md` | **WSL 원본** — 25종 실측 표 (SSH 수령, md5 일치 확인) |
| `scripts/SAMSUNG-FRIENDLY-ADB-CONTENT-GUIDE-2026-08-22.md` | **WSL 원본** — 콘텐츠 분류 가이드 (Safe/No-Go) |

```bash
bash scripts/samsung_app_launcher.sh --list   # 리스트
bash scripts/samsung_app_launcher.sh --all    # 전부 실행
bash scripts/samsung_app_launcher.sh 카메라   # 1개 실행
```

---

## 5. 확장 계획 (이 베이스라인을 어떻게 뜯어 고칠까)

- [ ] **종속앱 4종** (테마스토어/퀵툴/빅스비/DeX): 서브 액티비티 직접 지정 조사
- [ ] **리마인더**: `pm grant` 사전 부여 검증
- [ ] **25종 밖 추가 앱 스윕** (전체 설치 앱 후보)
- [ ] **앱 실행 → 콘텐츠 공정 연결**: 카메라 촬영 → 편집 → 발행 파이프라인에 모듈로 삽입
- [x] **패키지명 보정 완료** — 원본 표 확보로 4건 수정 (연락처/spay/find/gamehome). 19번째 앱은 없음 — 표 기준 **18 OK 확정**

---

## 6. 가드레일 (헌법 제1조급 — 이 조건 없으면 헌법 위반)

```
- 본인 폰 + 이미 승인된 ADB에서만.
- 타인 기기 금지 / 미승인 기기 금지 / 소유자 확인 없이 진행 금지.
- 시큐어폴더(Knox TrustZone 격리) 절대 시도 금지 — 잠금화면 뜨면 즉시 중단, 재시도 금지.
- 작업 끝나면 폰은 홈 화면 복귀 (부작용 없이).
```

---

*작성: Claude Code (_Claude) · 2026-08-22 · 베이스라인 문서 — 수정 시 마크 갱신*
