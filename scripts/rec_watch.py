#!/usr/bin/env python3
"""rec_watch.py — 삼성 화면 녹화 시작 감지 → 오버레이 키트 자동 무장 (_Claude 2026-09-23)

Boss 그림 (원문):
  "화면 녹화하면은 그 오버레이키트 2개가 자동으로 연결돼 가지고 마치 화면 녹화에
   내장 기능처럼 활성화가 돼야 되고 ... 내가 그거 보면서 화면 녹화하면 되는 거고"

경로:
  삼성 녹화기 시작 → /sdcard/DCIM/Screen recordings/Screen_Recording_*.mp4 등장
                   → (저장된 콘티 로드) Axis OFF→ARM
                   → Laser Pen 그려지고 있는지 확인
                   → (--cam-style 주면) 카메라 키트 우하단에

키트별 문 (2026-09-23 실측):

  Axis  kr.parksy.axis
        am broadcast -a kr.parksy.axis.ARM -n .../AxisArmReceiver --es rundown '...'
        → 문 있음. 단 무장 중 재무장은 크래시 → axis_arm.arm() 이 OFF 를 선행한다.

  Laser com.dtslib.laser_pen_overlay
        cmd statusbar click-tile com.dtslib.laser_pen_overlay/.LaserPenTileService
        → **이것뿐이다.** 리시버 없음. OverlayService 는 not exported 라
          `am start-foreground-service` 가 거부된다(uid 10696). 타일도 한 번 먹고
          이후로는 안 먹는다. 그래서 여기서는 "확인 → 안 되면 크게 경고"만 한다.
          스스로 켜지지 않은 녹화는 Boss 가 손으로 켜야 한다는 뜻이다.

  나레이터 액자 (오른쪽 아래 CRT)
        → kr.parksy.axis 안의 **네이티브 TvOverlayService**. Axis 문 하나로 뜬다:
          am broadcast -a kr.parksy.axis.TV -n <AxisArmReceiver>

        ⚠️ 2026-09-23 — 여기 원래 `camkit.py`(삼성 비디오 플레이어를 freeform 창으로)가
        물려 있었다. **버렸다.** 실측으로 두 가지가 안 됐다:
          ① 플레이어가 재생 컨트롤(▶·탐색바·0:10)을 같이 띄워 녹화에 찍힌다.
             창 위에 파란 손잡이 막대도 붙는다.
          ② **창이 1분을 못 버틴다** — 14:21 에 띄운 창이 14:22 에 사라졌다.
             Boss 가 "잠깐 떴다가 사라지는 거 봤다"고 한 그 증상.
        반면 TvOverlayService 는 포그라운드 서비스라 죽지 않고, 액자가 영상에
        구워져 있어 컨트롤·장식이 **구조적으로 생길 수 없다.**

쓰는 법:
  python3 scripts/rec_watch.py                 # 감시 시작 (포그라운드)
  python3 scripts/rec_watch.py --once          # 한 번만 스캔
  python3 scripts/rec_watch.py --arm-now       # 감시 없이 지금 무장 (테스트)
  python3 scripts/rec_watch.py --tv-on-now     # 나레이터 액자만 지금 띄운다
  python3 scripts/rec_watch.py --tv            # 녹화 감지 시 액자도 같이
  python3 scripts/rec_watch.py --dir /tmp/x    # 감시 폴더 바꿔서 (테스트)

  백그라운드 상주:
  setsid nohup python3 scripts/rec_watch.py --daemon >/dev/null 2>&1 &
  bash scripts/rec_watch.sh status|stop        # 래퍼
"""
import argparse
import glob
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import axis_arm  # noqa: E402

REC_DIR = "/sdcard/DCIM/Screen recordings"
REC_GLOB = "Screen_Recording_*.mp4"
PEN_PKG = "com.dtslib.laser_pen_overlay"
PEN_TILE = PEN_PKG + "/.LaserPenTileService"

PIDFILE = os.path.expanduser("~/.rec_watch.pid")
LOGFILE = os.path.expanduser("~/.rec_watch.log")

# 레이저펜이 실제로 그려지고 있는지 — 창 레코드는 꺼져도 남으므로
# mDrawState=HAS_DRAWN 만이 진짜 신호다(실측: 켜짐 2, 꺼짐 0).
PEN_AWK = ("awk '/Window #/{n=($0 ~ /u0 " + PEN_PKG + "}:/)} "
           "n&&/mDrawState=HAS_DRAWN/{c++} END{print c+0}'")


def log(msg):
    line = time.strftime("[%H:%M:%S] ") + msg
    print(line, flush=True)
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


# ── 녹화 파일 ──────────────────────────────────────────────────────────────

def recordings(d):
    """{경로: (mtime, size)} — 녹화 중이면 크기가 계속 는다."""
    out = {}
    for p in glob.glob(os.path.join(d, REC_GLOB)):
        try:
            st = os.stat(p)
        except OSError:
            continue
        out[p] = (st.st_mtime, st.st_size)
    return out


# ── 녹화 상태 감지 ─────────────────────────────────────────────────────────
#
# 삼성 녹화기 자체는 **SystemUI/SmartCapture 안**에 있다. 거기 버튼을 넣는 건
# 못 한다 — `com.samsung.android.app.smartcapture` 는 시스템 서명 앱이고
# 화면녹화 API 는 `signature|privileged` 로 잠겨 있다. 2026-09-23 시도해서
# 막힌 문들 (다시 파지 말 것):
#
#   · ScreenRecorderProvider (content://com.samsung.android.app.screenrecorder.provider)
#     → SecurityException. uid 2000 에게 ACCESS_SCREEN_RECORDER_SVC 가 없다.
#   · ScreenRecorderReceiver → 필터가 설정 체크 액션뿐. 시작/끝 방송이 없다.
#   · 녹화 전용 패키지 → 없다. 삼성 녹화기는 smartcapture 6.0.31.19 안에 들어있다.
#
# 대신 **시작 순간을 관측**한다. 버튼을 다는 것보다 이게 낫다 — Boss 가
# 아무것도 안 눌러도 된다. 신호 셋, 싼 것부터:
#
#   ① media_projection — MediaProjection 은 녹화가 시작되기 **전에** 만들어진다.
#      가장 이른 신호다. dumpsys 한 번이라 싸다.
#      안 돌 때의 출력은 정확히 `Media Projection: \nnull` (실측).
#   ② notification — smartcapture 의 `CHANNEL_ID_RECORDING_SCREEN`('화면 녹화')
#      채널에 상시 알림이 뜬다. ⚠️ **채널 정의는 평소에도 보인다** —
#      `dumpsys notification` 의 AppSettings 절에 항상 있다. 그래서 채널 이름만
#      찾으면 오탐이다. **NotificationRecord(=실제로 뜬 알림)** 를 봐야 한다.
#   ③ 파일 — 기존 방식. 남겨두는 이유는 ① ② 가 다 실패했을 때의 바닥이고,
#      Boss 가 "녹화 끝"을 판정하는 근거로도 쓴다(파일이 안 자라면 끝).
#
# 셋 중 뭐가 먼저 잡혔는지 **근거를 로그에 남긴다.** 그래야 실녹화 1회로
# 어느 신호가 진짜인지 판정된다.

MP_CMD = "dumpsys media_projection"
NOTI_CMD = "dumpsys notification --noredact"
REC_CHANNEL = "CHANNEL_ID_RECORDING_SCREEN"
REC_PKG = "com.samsung.android.app.smartcapture"


def _mp_recording(device):
    """MediaProjection 이 살아 있는가. 못 읽으면 None(모름)."""
    rc, out = axis_arm.adb(device, MP_CMD, timeout=30)
    if rc != 0:
        return None
    body = out.split("Media Projection:", 1)[-1].strip()
    if not body:
        return None
    return body.splitlines()[0].strip() != "null"


def _noti_recording(device):
    """녹화 상시 알림이 실제로 떠 있는가. 못 읽으면 None(모름).

    NotificationRecord 줄에만 반응한다 — 채널 정의(AppSettings 절)는 평소에도
    있으므로 그걸로 판정하면 녹화 중이 아닐 때도 켜진다고 거짓말한다.
    """
    rc, out = axis_arm.adb(device, NOTI_CMD, timeout=45)
    if rc != 0:
        return None
    for line in out.splitlines():
        if "NotificationRecord" in line and REC_PKG in line and REC_CHANNEL in line:
            return True
    return False


def rec_state(device):
    """(녹화중인가, 근거). 판단이 안 서면 (False, '판단불가')."""
    mp = _mp_recording(device)
    if mp:
        return True, "media_projection"
    noti = _noti_recording(device)
    if noti:
        return True, "notification"
    if mp is None and noti is None:
        return False, "판단불가"
    return False, "없음"


def age_of(path):
    try:
        return time.time() - os.stat(path).st_mtime
    except OSError:
        return -1.0


# ── 레이저펜 ───────────────────────────────────────────────────────────────

def pen_drawing(device):
    """그려지고 있는 레이저펜 창 수. 0이면 펜이 안 보인다."""
    rc, out = axis_arm.adb(device, "dumpsys window windows | " + PEN_AWK, timeout=40)
    if rc != 0:
        return -1
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return -1


def pen_ensure(device):
    """펜이 꺼져 있으면 타일을 한 번 눌러본다. 안 되면 경고만."""
    n = pen_drawing(device)
    if n > 0:
        log(f"  레이저펜: 그려지는 중 (창 {n}개) — 손 안 댐")
        return True
    log(f"  레이저펜: 안 보임 (창 {n}개) — 타일 시도")
    axis_arm.adb(device, "cmd statusbar click-tile " + PEN_TILE, timeout=30)
    time.sleep(2)
    n = pen_drawing(device)
    if n > 0:
        log(f"  레이저펜: 켜짐 (창 {n}개)")
        return True
    log("  ⚠️ 레이저펜을 못 켰다 — **손으로 켜야 한다** "
        "(리시버 없음 · 서비스 not exported · 타일은 한 번만 먹음)")
    return False


# ── 무장 ───────────────────────────────────────────────────────────────────

def fire(device, tv_on=False):
    """녹화가 시작됐다 — 콘티로 무장하고, 원하면 나레이터 액자까지."""
    if not os.path.exists(axis_arm.STORE):
        log(f"  ⚠️ 저장된 콘티가 없다: {axis_arm.STORE} — "
            "먼저 `python3 scripts/axis_arm.py --url <URL> --show 0`")
        return
    with open(axis_arm.STORE, encoding="utf-8") as f:
        rd = __import__("json").load(f)
    log(f"  콘티: {rd.get('root','')} / {len(rd.get('stages',[]))}단계")

    if not axis_arm.ensure_device(device):
        log(f"  ⚠️ adb 붙지 못함: {device}")
        return
    # 순서: **보이는 것 먼저.** Boss 요구가 "누르면 바로 뜬다"이므로 화면에
    # 나타나는 두 창을 먼저 다 올리고, 레이저펜 확인은 맨 뒤로 뺀다.
    # 펜 확인은 dumpsys 왕복 + 2초 대기라 2~4초를 먹는다 — 그 시간 동안
    # Boss 눈에는 아직 아무것도 안 떠 있다.

    # ① 콘티 (Flutter 창, 뜨는 데 ~1.4초)
    rc, out = axis_arm.arm(device, rd, show=1)
    log(f"  Axis 무장: {out}")

    # ② 나레이터 액자 (네이티브 VideoView, broadcast 왕복 0.42초 · 재생 시작 ~2초)
    if tv_on:
        rc, out = axis_arm.tv(device, on=True)
        log(f"  나레이터 액자: {out}")

    # ③ 레이저펜 — 문이 없어 실패해도 나머지는 이미 떠 있다
    pen_ensure(device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=axis_arm.DEFAULT_DEVICE)
    ap.add_argument("--dir", default=REC_DIR, help="감시 폴더 (테스트용)")
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--stop-after", type=float, default=10.0,
                    help="이 초 동안 파일이 안 자라면 녹화 끝으로 본다")
    ap.add_argument("--off-on-stop", action="store_true",
                    help="녹화 끝나면 Axis 내린다 (기본: 그대로 둔다)")
    ap.add_argument("--once", action="store_true", help="한 번만 스캔")
    ap.add_argument("--arm-now", action="store_true", help="감시 없이 즉시 무장")
    ap.add_argument("--tv", action="store_true",
                    help="녹화 감지 시 나레이터 액자(CRT)도 같이 띄운다")
    ap.add_argument("--tv-on-now", action="store_true",
                    help="감시 없이 나레이터 액자만 지금 띄운다")
    ap.add_argument("--daemon", action="store_true", help="pidfile 쓴다")
    ap.add_argument("--probe", action="store_true",
                    help="감지 신호만 찍는다 (오버레이 안 띄움) — 실녹화 판정용")
    a = ap.parse_args()

    if a.arm_now:
        if not axis_arm.ensure_device(a.device):
            log(f"⚠️ adb 붙지 못함: {a.device}")
            return 2
        fire(a.device, a.tv)
        return 0

    if a.tv_on_now:
        if not axis_arm.ensure_device(a.device):
            log(f"⚠️ adb 붙지 못함: {a.device}")
            return 2
        rc, out = axis_arm.tv(a.device, on=True)
        log(f"나레이터 액자: {out}")
        return rc

    if a.daemon:
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpid()))

    log(f"감시 시작 — {a.dir} (간격 {a.interval}s, PID {os.getpid()})")
    seen = recordings(a.dir)
    log(f"  기준선 {len(seen)}개")

    if a.once:
        for p in sorted(seen):
            log(f"  · {os.path.basename(p)}")
        return 0

    # 감지 신호가 셋이라 로그에 **어느 게 먼저 잡혔는지**를 남긴다. 실녹화 1회로
    # ①(media_projection) ②(notification) ③(파일) 중 뭐가 진짜인지 판정된다.
    if a.probe:
        log("  [probe] 신호만 찍는다 — 오버레이는 안 띄운다. 녹화를 시작해 보라.")
        while True:
            mp = _mp_recording(a.device)
            noti = _noti_recording(a.device)
            n = len(recordings(a.dir))
            log(f"  media_projection={mp}  notification={noti}  파일={n}")
            time.sleep(a.interval)

    fired = False          # 지금 "녹화 중"이라고 보고 있는가
    why_now = ""
    active = None          # 파일 감시용 (보조)
    last_move = 0.0

    while True:
        t0 = time.time()
        try:
            cur = recordings(a.dir)
        except Exception as e:                      # noqa: BLE001
            log(f"  ⚠️ 스캔 실패: {e}")
            time.sleep(a.interval)
            continue

        on, why = rec_state(a.device)

        fresh = [p for p in cur if p not in seen]
        if fresh:
            newest = max(fresh, key=lambda p: cur[p][0])
            age = age_of(newest)
            log(f"  · 새 파일: {os.path.basename(newest)} "
                f"({cur[newest][1] / 1024:.0f}KB, 나이 {age:.1f}s)")
            if age > 60:
                # 삼성 녹화기가 파일을 **끝날 때** 만든다면 이 신호는 쓸모가 없다.
                log("  ⚠️ 이 파일이 이미 60초 묵었다 — 시작이 아니라 끝을 잡았을 수 있다")
            on, why = True, (why if why != "없음" else "file")
            active, last_move = newest, time.time()

        # 상태 판정과 파일 신호의 합치
        if on and not fired:
            log(f"● 녹화 시작 (근거: {why})")
            fire(a.device, a.tv)
            fired, why_now = True, why
        elif not on and fired:
            log(f"○ 녹화 끝 (근거: {why})")
            if a.off_on_stop:
                axis_arm.disarm(a.device)
                log("  Axis 하강")
                if a.tv:
                    axis_arm.tv(a.device, on=False)
                    log("  나레이터 액자 하강")
            fired, why_now = False, ""

        # 보조: 상태 신호가 판단불가일 때만 파일 성장으로 끝을 잡는다
        if fired and active and active in cur:
            if cur[active] != seen.get(active):
                last_move = time.time()
            elif why == "판단불가" and time.time() - last_move > a.stop_after:
                log(f"○ 녹화 끝(파일이 {a.stop_after:.0f}s 안 자람): "
                    f"{os.path.basename(active)} "
                    f"({cur[active][1] / 1048576:.1f}MB)")
                if a.off_on_stop:
                    axis_arm.disarm(a.device)
                    log("  Axis 하강")
                    if a.tv:
                        axis_arm.tv(a.device, on=False)
                        log("  나레이터 액자 하강")
                fired, active = False, None

        seen = cur
        time.sleep(max(0.2, a.interval - (time.time() - t0)))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("중단")
        sys.exit(0)
