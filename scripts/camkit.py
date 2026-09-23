#!/usr/bin/env python3
"""camkit.py — 카메라 키트: 나레이터 루프 영상을 화면 우하단에 띄운다 (_Claude 2026-09-23)

Boss 그림 (원문):
  "crt 모니터에다가 내가 단순한 영상 계속 반복해 가지고 떠드는 거 나레이터와 모델같이
   만든 영상 띄우는 거 만들라고 했잖아? ... 오른쪽 하단에다가"

어저께(09-22) 미니PC에서 만든 루프 영상을 폰에서 실제로 띄우는 조각이다.
(그때는 미니PC에서 본 것 — 폰에는 결과물만 복사돼 있었다.)

■ 왜 이렇게 하는가 (2026-09-23 실측)

삼성 비디오 플레이어는 **가로모드를 강제**한다. 그냥 freeform 으로 띄우면
화면 전체가 눕고 창이 2340x1080 기준으로 벌어진다 → 우하단 구석방이 안 나온다.

  처방: cmd window set-ignore-orientation-request true
        → 앱의 회전 요청을 시스템이 무시 → 세로 유지된 채 구석방이 된다.

그리고 am 에는 --bounds 가 없다(Android 16). 태스크를 만든 뒤 따로 리사이즈한다:

  am start ... --windowingMode 5
  am task resizeable <TASK_ID> 2
  am task resize <TASK_ID> <L> <T> <R> <B>

실측 결과(1080x2340): 태스크 Rect(716,1630 - 1056,2180) = 우하단 340x550 정확히 박힘.

■ 파일

`a_tv_frame.mp4`(CRT 모니터 베젤 — Boss 가 말한 그거) 5초짜리를 12번 이어붙여 60초로.
`/sdcard` 에 있어야 앱이 읽는다(proot 안 `/root/work` 은 안드로이드 앱에게 안 보인다).
MediaStore 등록까지 해야 content:// 로 열린다.

쓰는 법:
  python3 scripts/camkit.py --on              # 우하단에 띄운다
  python3 scripts/camkit.py --off             # 닫는다
  python3 scripts/camkit.py --on --pos bl --w 300
  python3 scripts/camkit.py --build --style tv   # 60초 루프 다시 굽기
  python3 scripts/camkit.py --status
"""
import argparse
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import axis_arm  # noqa: E402  (adb/ensure_device 재사용)

CAMWORK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "_staging", "ovl", "camwork")
SD_DIR = "/sdcard/Movies/camkit"

PLAYER_PKG = "com.samsung.android.video"
PLAYER_ACT = "com.samsung.android.video.player.activity.MoviePlayer"
PLAYER_TASK = "com.samsung.android.video.movieplayer"

# 스타일 → 원본 클립 (미니PC 세션 1c5394be 산출물)
STYLES = {
    "tv":   "a_tv_frame.mp4",      # CRT 모니터 베젤 (Boss 지정)
    "cam":  "b_camera_frame.mp4",
    "art":  "c_artistic.mp4",
    "lens": "unit7_1min.mp4",      # 초록 렌즈 + REC HUD
    "rec":  "restore_1min.mp4",    # 무채색 렌즈 + REC HUD
}
DEFAULT_STYLE = "tv"

W_DEFAULT = 340          # 구석방 가로
MARGIN_R = 24            # 오른쪽 여백
MARGIN_B = 160           # 아래 여백 (내비바 위)
ASPECT = 650 / 402       # CRT 베젤 세로/가로


def log(m):
    print(m, flush=True)


def uri_of(device, path):
    """MediaStore 에서 content:// URI 를 얻는다. 없으면 스캔부터."""
    where = "_data LIKE '%%%s%%'" % os.path.basename(path)
    q = ["content", "query", "--uri", "content://media/external/video/media",
         "--projection", "_id", "--where", '"%s"' % where]
    rc, out = axis_arm.adb(device, *q, timeout=40)
    m = re.search(r"_id=(\d+)", out)
    if not m:
        axis_arm.adb(device, "content", "call", "--uri", "content://media/external/file",
                     "--method", "scan_file", "--arg", path, timeout=40)
        time.sleep(2)
        rc, out = axis_arm.adb(device, *q, timeout=40)
        m = re.search(r"_id=(\d+)", out)
    return "content://media/external/video/media/" + m.group(1) if m else None


def screen_size(device):
    rc, out = axis_arm.adb(device, "wm", "size", timeout=20)
    m = re.search(r"Override size:\s*(\d+)x(\d+)", out) or \
        re.search(r"Physical size:\s*(\d+)x(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 2340)


def bounds_for(pos, w, W, H, margin_t=140):
    """pos = br|bl|tr|tl. 세로 여백은 아래=내비바, 위=상태바를 피한다."""
    h = int(w * ASPECT)
    left = (W - MARGIN_R - w) if pos in ("br", "tr") else MARGIN_R
    top = (H - MARGIN_B - h) if pos in ("br", "bl") else margin_t
    return (left, top, left + w, top + h)


def task_id_of(device):
    rc, out = axis_arm.adb(device, "dumpsys", "activity", "activities", timeout=45)
    for line in out.splitlines():
        if PLAYER_TASK in line and "Task{" in line:
            m = re.search(r"#(\d+)", line)
            if m:
                return m.group(1)
    return None


def find_task(device, tries=8):
    for _ in range(tries):
        t = task_id_of(device)
        if t:
            return t
        time.sleep(0.7)
    return None


def build(device, style):
    """스타일 클립을 60초 루프로 만들어 /sdcard 에 넣는다."""
    src = os.path.join(CAMWORK, STYLES.get(style, STYLES[DEFAULT_STYLE]))
    if not os.path.exists(src):
        log(f"[!] 원본 없음: {src}")
        return None
    out_name = f"parksy_{style}_60s.mp4"
    dst = f"{SD_DIR}/{out_name}"
    subprocess.run(["mkdir", "-p", SD_DIR], check=False)
    # 5초짜리는 12번 반복, 이미 60초대면 그대로 복사
    rc = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "csv=p=0", src], capture_output=True, text=True)
    try:
        dur = float(rc.stdout.strip())
    except ValueError:
        dur = 0.0
    if dur and dur < 30:
        reps = max(1, int(round(60 / dur)))
        cmd = ["ffmpeg", "-v", "error", "-stream_loop", str(reps - 1), "-i", src,
               "-c", "copy", "-movflags", "+faststart", dst, "-y"]
    else:
        cmd = ["cp", src, dst]
    subprocess.run(cmd, check=False)
    log(f"[+] 루프 생성: {dst}")
    return dst


def on(device, style, pos, w, dry=False):
    path = f"{SD_DIR}/parksy_{style}_60s.mp4"
    if not os.path.exists(path):
        log(f"[*] 루프가 없다 — 굽는다 ({style})")
        path = build(device, style)
    if not path or not os.path.exists(path):
        return 2
    uri = uri_of(device, path)
    if not uri:
        log(f"[!] MediaStore 에 못 넣었다: {path}")
        return 2

    W, H = screen_size(device)
    b = bounds_for(pos, w, W, H)
    log(f"[*] 화면 {W}x{H} · 자리 {pos} · 창 {b[2]-b[0]}x{b[3]-b[1]} @ {b}")

    if dry:
        return 0

    # ① 가로 강제를 무시시킨다 — 이게 없으면 화면 전체가 눕는다
    axis_arm.adb(device, "cmd", "window", "user-rotation", "lock", "0", timeout=25)
    axis_arm.adb(device, "cmd", "window", "set-ignore-orientation-request", "true", timeout=25)

    # ② freeform 으로 띄운다
    rc, out = axis_arm.adb(
        device, "am", "start", "-n", f"{PLAYER_PKG}/{PLAYER_ACT}",
        "-a", "android.intent.action.VIEW", "-d", uri, "-t", "video/mp4",
        "--windowingMode", "5", timeout=50)
    if "Error" in out or "Exception" in out:
        log(f"[!] 기동 실패: {out}")
        return 2

    # ③ 태스크를 구석으로 리사이즈한다
    tid = find_task(device)
    if not tid:
        log("[!] 태스크를 못 찾았다")
        return 2
    axis_arm.adb(device, "am", "task", "resizeable", tid, "2", timeout=30)
    axis_arm.adb(device, "am", "task", "resize", tid, *[str(v) for v in b], timeout=30)
    time.sleep(1.5)
    log(f"[+] 카메라 키트 ON — 태스크 #{tid} @ {b}")
    return 0


def off(device):
    axis_arm.adb(device, "am", "force-stop", PLAYER_TASK, timeout=30)
    axis_arm.adb(device, "am", "force-stop", PLAYER_PKG, timeout=30)
    # 회전 무시를 되돌린다 (전역 설정이라 켜두면 계속 영향이 간다)
    axis_arm.adb(device, "cmd", "window", "set-ignore-orientation-request", "reset", timeout=25)
    log("[+] 카메라 키트 OFF")
    return 0


def status(device):
    rc, out = axis_arm.adb(device, "dumpsys", "window", "windows", timeout=45)
    hit = [l.strip() for l in out.splitlines()
           if "Window #" in l and "samsung.android.video" in l]
    ign = axis_arm.adb(device, "cmd", "window", "get-ignore-orientation-request", timeout=25)[1]
    log(f"  플레이어 창: {len(hit)}개")
    for l in hit:
        log(f"    {l[:90]}")
    log(f"  회전 무시  : {ign.strip()}")
    return 0 if hit else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--on", action="store_true")
    ap.add_argument("--off", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--style", default=DEFAULT_STYLE, choices=sorted(STYLES))
    ap.add_argument("--pos", default="br", choices=["br", "bl", "tr", "tl"])
    ap.add_argument("--w", type=int, default=W_DEFAULT)
    ap.add_argument("--device", default=axis_arm.DEFAULT_DEVICE)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not axis_arm.ensure_device(a.device):
        log(f"[!] 기기에 붙지 못했습니다: {a.device}")
        return 2

    if a.off:
        return off(a.device)
    if a.status:
        return status(a.device)
    if a.build:
        return 0 if build(a.device, a.style) else 2
    return on(a.device, a.style, a.pos, a.w, dry=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
