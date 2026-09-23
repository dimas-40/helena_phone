# 오버레이 자동 키트 — 인수인계 (2026-09-23, `_Claude`)

Boss 지시 원문:
> "화면 녹화하면은 그 오버레이키트 2개가 자동으로 연결돼 가지고 마치 화면 녹화에 내장
> 기능처럼 활성화가 돼야 되고 그거 작업하기 전에 엑시스 같은 경우에는 내가 URL 주면은
> 파싱해 가지고 카테고리 거기에다가 표현하는 거 미리 작업해서 저장해야 되고 내가 그거
> 보면서 화면 녹화하면 되는 거고"

중단 시각 상태: **두 오버레이 모두 내려감** (Axis 창 0 · Laser 창 0 · 잔여 프로세스 0).
Boss 가 다른 작업으로 전환하라고 해서 여기서 멈춤.

---

## 1. 지금까지 된 것

| 조각 | 상태 | 실물 |
|---|---|---|
| URL → 카테고리 추출 → 콘티 저장 | ✅ | `scripts/axis_arm.py` |
| 콘티 → Axis 오버레이 무장 | ✅ | 위 스크립트 `arm()` |
| 한글 카테고리 렌더 | ✅ | 오버레이엔 한글이 정상 출력된다 (ffmpeg drawtext 와 다름) |
| 녹화 시작 감지 → 자동 무장 | 🟡 | `scripts/rec_watch.py` — 코드 완성, **실녹화 검증 전** |
| 화면 녹화 동작 확인 | ⏹ | Boss 가 직접 녹화해야 확인됨 (§4) |

**쓰는 법**

```bash
python3 scripts/axis_arm.py --url https://... --show 0   # 파싱·저장만 (화면 안 건드림)
python3 scripts/axis_arm.py --last                       # 저장된 콘티로 무장
python3 scripts/axis_arm.py --off                        # 하강
python3 scripts/rec_watch.py --arm-now                   # 감시 없이 즉시 무장
python3 scripts/rec_watch.py                             # 녹화 감시 (포그라운드)
```

## 2. 문(門) 두 개 — 실측으로 확인한 것

**Axis** `kr.parksy.axis` — 문 있다.
```
am broadcast --user 0 -a kr.parksy.axis.ARM \
  -n kr.parksy.axis/flutter.overlay.window.flutter_overlay_window.AxisArmReceiver \
  --es rundown '<콘티 JSON>' --ei show 1
```
- `--es rundown` 없이 보내면 앱이 거부한다 (`W/AxisArm: ARM 인데 rundown 이 없습니다`).
- ⚠️ **무장된 상태에서 ARM 을 또 보내면 옛 프로세스가 죽는다:**
  ```
  java.lang.RuntimeException: Unable to stop service ...OverlayService:
    java.lang.RuntimeException: Cannot execute operation because
    FlutterJNI is not attached to native.
      at FlutterJNI.ensureAttachedToNative(FlutterJNI.java:516)
      at ActivityThread.handleStopService(ActivityThread.java:6137)
  ```
  화면은 새 프로세스가 이어받아 살아나지만 **크래시 다이얼로그가 뜨면 녹화에 찍힌다.**
- ✅ **처방:** ARM 전에 `kr.parksy.axis.OFF` → 1.5초 → ARM. 3회 반복 실측 전부 깨끗
  (창 4개 유지, 크래시 0). `axis_arm.arm()` 이 이 순서를 강제한다.

**Laser Pen** `com.dtslib.laser_pen_overlay` — **문이 사실상 없다.**
- 커스텀 리시버 0개 (`androidx.profileinstaller` 만).
- `OverlayService` 는 **not exported** → `am start-foreground-service` 거부
  (`Requires permission not exported from uid 10696`).
- `cmd statusbar click-tile .../.LaserPenTileService` → **한 번 먹고 이후 안 먹는다.**
- `run-as` 는 된다(디버거블) 하지만 `shared_prefs` 엔 상태 플래그가 없다.
- 현재 켜짐/꺼짐 판독: `dumpsys window windows` 에서 `mDrawState=HAS_DRAWN` 인 창 수.
  창 레코드는 꺼져도 남으므로 개수 세면 안 된다(켜짐 2 / 꺼짐 0).
- **관찰된 사실:** `am force-stop com.dtslib.laser_pen_overlay` → 즉시 꺼진다.
- **가설(미검증):** force-stop 직후엔 타일이 다시 먹을 것 → 그렇다면
  `force-stop=OFF / click-tile=ON` 으로 문이 생긴다. **다음 세션 첫 실험 후보.**

## 3. `rec_watch.py` 설계

- `/sdcard/DCIM/Screen recordings/Screen_Recording_*.mp4` 를 1초마다 스캔
  (proot 에서 이 폴더가 그대로 읽힌다 — 확인함).
- 새 파일 등장 = 녹화 시작 → 저장된 콘티로 무장 + 레이저펜 확인.
- 파일이 `--stop-after`(기본 10초) 동안 안 자라면 녹화 끝으로 판정.
- `--off-on-stop` 주면 끝날 때 Axis 하강(기본은 그대로 둠).
- `--dir` 로 감시 폴더를 바꿀 수 있다 → **실녹화 없이 감지 로직 시험 가능.**
- 감지 시점에 파일 나이를 로그로 남긴다. 60초 넘게 묵었으면 "시작이 아니라 끝을
  잡았을 수 있다"고 경고한다.

## 4. ⏹ 아직 검증 안 된 단 하나 (Boss 손이 필요함)

**삼성 녹화기가 녹화 *시작* 시점에 파일을 만드는가, *끝*날 때 만드는가.**
파일이 끝날 때 생기면 이 감시자는 아무 의미가 없다(너무 늦다). 이건 실녹화 1회로만
판정된다. 판정법: `rec_watch.py` 를 띄워두고 화면 녹화를 10초쯤 하면, 로그에 뜨는
`파일나이` 값이 작으면(0~2초) 시작 감지 성공, 60초 경고가 뜨면 실패.

실패하면 대안: 녹화 알림(`dumpsys notification`) 또는 MediaProjection 상태를 본다.

## 5. 다음 손 (재개할 때)

1. Boss 녹화 1회 → §4 판정
2. Laser Pen `force-stop → click-tile` 가설 검증 (§2)
3. 통과하면 `rec_watch.sh` 래퍼(start/stop/status, `setsid nohup`)로 상주
4. devlog + `_notebook/` 문서화 (이 파일은 루트 임시 인수인계)

_폰 세션 `_Claude`_
