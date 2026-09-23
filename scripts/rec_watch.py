#!/usr/bin/env python3
"""rec_watch.py — 삼성 화면 녹화 시작 감지 → 오버레이 키트 자동 무장 (_Claude 2026-09-23)

Boss 그림 (원문):
  "화면 녹화하면은 그 오버레이키트 2개가 자동으로 연결돼 가지고 마치 화면 녹화에
   내장 기능처럼 활성화가 돼야 되고 ... 내가 그거 보면서 화면 녹화하면 되는 거고"

경로:
  삼성 녹화기 시작 → /sdcard/DCIM/Screen recordings/Screen_Recording_*.mp4 등장
                   → (저장된 콘티 로드) Axis OFF→ARM
                   → Laser Pen 그려지고 있는지 확인

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

쓰는 법:
  python3 scripts/rec_watch.py                 # 감시 시작 (포그라운드)
  python3 scripts/rec_watch.py --once          # 한 번만 스캔
  python3 scripts/rec_watch.py --arm-now       # 감시 없이 지금 무장 (테스트)
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

def fire(device, tag):
    """녹화가 시작됐다 — 저장된 콘티로 무장한다."""
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
    pen_ensure(device)
    rc, out = axis_arm.arm(device, rd, show=1)
    log(f"  Axis 무장: {out}")


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
    ap.add_argument("--daemon", action="store_true", help="pidfile 쓴다")
    a = ap.parse_args()

    if a.arm_now:
        if not axis_arm.ensure_device(a.device):
            log(f"⚠️ adb 붙지 못함: {a.device}")
            return 2
        fire(a.device, "수동")
        return 0

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

    active = None          # 녹화 중이라 보고 있는 파일
    last_move = 0.0        # 마지막으로 파일이 자란 시각

    while True:
        try:
            cur = recordings(a.dir)
        except Exception as e:                      # noqa: BLE001
            log(f"  ⚠️ 스캔 실패: {e}")
            time.sleep(a.interval)
            continue

        fresh = [p for p in cur if p not in seen]
        if fresh:
            newest = max(fresh, key=lambda p: cur[p][0])
            log(f"● 녹화 시작 감지: {os.path.basename(newest)} "
                f"({cur[newest][1] / 1024:.0f}KB, 파일나이 {age_of(newest):.1f}s)")
            if age_of(newest) > 60:
                log("  ⚠️ 파일이 이미 60초 묵었다 — 시작이 아니라 **끝**을 잡았을 수 있다")
            fire(a.device, "감지")
            active, last_move = newest, time.time()

        if active and active in cur:
            if cur[active] != seen.get(active):
                last_move = time.time()
            elif time.time() - last_move > a.stop_after:
                log(f"○ 녹화 끝: {os.path.basename(active)} "
                    f"({cur[active][1] / 1048576:.1f}MB)")
                if a.off_on_stop:
                    axis_arm.disarm(a.device)
                    log("  Axis 하강")
                active = None

        seen = cur
        time.sleep(a.interval)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("중단")
        sys.exit(0)
