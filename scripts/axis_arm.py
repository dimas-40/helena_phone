#!/usr/bin/env python3
"""axis_arm.py — URL/텍스트 → 콘티(rundown) → Axis 오버레이 무장 (_Claude 2026-09-23)

Boss 그림: "내가 URL 주면 파싱해 가지고 카테고리 거기에다가 표현하는 거 미리 작업해서 저장하고,
그거 보면서 화면 녹화하면 되는 거."

경로 (2026-09-23 실측):
  adb shell am broadcast --user 0 -a kr.parksy.axis.ARM \\
    -n kr.parksy.axis/flutter.overlay.window.flutter_overlay_window.AxisArmReceiver \\
    --es rundown '<콘티 JSON>' --ei show 1

  ⚠️ rundown 없이 보내면 앱이 거부한다 — `W/AxisArm: ARM 인데 rundown 이 없습니다`

  나레이터 액자 (오른쪽 아래 CRT) — 2026-09-23 추가:
  am broadcast --user 0 -a kr.parksy.axis.TV \\
    -n kr.parksy.axis/flutter.overlay.window.flutter_overlay_window.AxisArmReceiver

쓰는 법:
  python3 scripts/axis_arm.py --url https://...        # URL 파싱 → 콘티 → 무장
  python3 scripts/axis_arm.py --stages "오프닝,주제,근거,반전,정리" --root "[LIVE] 강의 01"
  python3 scripts/axis_arm.py --off                    # 하강
  python3 scripts/axis_arm.py --show 0 --url ...       # 저장만 (화면 안 건드림)
  python3 scripts/axis_arm.py --last                   # 저장해 둔 콘티로 재무장
  python3 scripts/axis_arm.py --tv                     # 나레이터 액자 띄운다
  python3 scripts/axis_arm.py --tv-off                 # 액자 내린다
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser

DEFAULT_DEVICE = "127.0.0.1:5900"
COMPONENT = ("kr.parksy.axis/flutter.overlay.window."
             "flutter_overlay_window.AxisArmReceiver")
STORE = os.path.expanduser("~/.axis_rundown.json")
UA = "Mozilla/5.0 (Linux; Android 16) axis-arm/1.0"

# ── 나레이터 액자 (오른쪽 아래 CRT) ────────────────────────────────────────
#
# 2026-09-23 정본 교체. 이전엔 `camkit.py` 가 **삼성 비디오 플레이어를 freeform
# 창으로** 띄웠다. 버렸다. 이유 두 가지, 둘 다 실측:
#
#   ① 삼성 플레이어가 **재생 컨트롤(▶·탐색바·0:10)** 을 같이 띄운다 → 녹화에 찍힌다.
#      창 위에 파란 손잡이 막대까지 붙는다.
#   ② **창이 1분을 못 버틴다.** 14:21 에 띄운 창이 14:22 에 사라졌다. Boss 가
#      "잠깐 떴다가 사라지는 거 봤다"고 한 그 증상이다.
#
# 대신 Boss 가 2026-09-22 에 직접 만든 `TvOverlayService`(네이티브 VideoView,
# 포그라운드 서비스)가 이미 폰에 깔려 있었다 — `kr.parksy.axis` **v11.4.0**,
# lastUpdateTime 09-22 18:31. 그게 어저께 "잘 띄워지더만" 하던 그 판이다.
#
#   액자는 **영상에 구워져 있다** (`assets/axis_tv.mp4` = `a_tv_frame.mp4`,
#   둘 다 201711바이트). 그래서 합성이 필요 없다 — 파일 하나 재생하면 액자째 나온다.
#   APK 자산이라 **저장소 권한도 필요 없다** (앱 권한에 READ_MEDIA_* 가 없다).
#
#   am broadcast --user 0 -a kr.parksy.axis.TV -n <COMPONENT>
#   am broadcast --user 0 -a kr.parksy.axis.TV_OFF -n <COMPONENT>
#
#   extras(전부 선택): w/h 크기(dp, 기본 96x155 — 액자 비율 402:650)
#                      x/y 오른쪽·아래 여백(dp, 기본 6/6) — **처음 띄울 때만**
#                      video 절대경로(안 주면 APK 기본 액자) · mute 1=무음(기본)
#
#   ⚠️ x/y 는 Boss 가 손으로 끌면 그 자리가 저장되어 **이후 무시된다**
#      (`shared_prefs/axis_tv_position.xml`). 명령으로 매번 되돌리면 Boss 가
#      옮겨놓은 자리가 계속 풀린다 — 그래서 여기서도 안 준다.
TV_ACTION = "kr.parksy.axis.TV"
TV_OFF_ACTION = "kr.parksy.axis.TV_OFF"

# ── 살아있는지 판별 (2026-09-23 실측) ──────────────────────────────────────
#
# 창 이름으로는 못 가른다. 콘티 창도 TV 창도 **둘 다 `kr.parksy.axis`** 로 뜬다.
# 크기로도 못 가른다(콘티 366x422px · TV 270x436px — 너무 가깝다).
# **서비스 레코드가 유일한 구분자다:**
#     콘티 = kr.parksy.axis/flutter.overlay.window.flutter_overlay_window.OverlayService
#     TV   = kr.parksy.axis/.TvOverlayService
SVC_OVERLAY = "flutter_overlay_window.OverlayService"
SVC_TV = "kr.parksy.axis/.TvOverlayService"


# ── URL 파싱 ────────────────────────────────────────────────────────────────

class _Heads(HTMLParser):
    """<title> + h1~h3 를 뽑는다. 태그는 버리고 텍스트만."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.heads = []
        self._buf = []
        self._tag = None

    def handle_starttag(self, tag, attrs):
        if tag in ("title", "h1", "h2", "h3", "h4"):
            self._tag, self._buf = tag, []

    def handle_endtag(self, tag):
        if tag == self._tag:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if tag == "title":
                self.title = self.title or text
            elif text:
                self.heads.append(text)
            self._tag, self._buf = None, []

    def handle_data(self, data):
        if self._tag:
            self._buf.append(data)


def fetch(path_or_url):
    if re.match(r"^https?://", path_or_url):
        req = urllib.request.Request(path_or_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
    else:
        with open(path_or_url, "rb") as f:
            raw = f.read()
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def _tidy(h, width=18):
    """오버레이는 260px 폭이다 — 긴 헤딩을 카테고리 길이로 줄인다."""
    h = re.sub(r"^[\d]+(\.[\d]+)*[.)]?\s*", "", h.strip())      # 앞 번호 제거
    h = re.sub(r"\s*[(（].*?[)）]\s*", " ", h)                    # 괄호 부제 제거
    h = re.split(r"\s+[—–·|]\s+", h)[0]                          # 대시 뒤 부제 제거
    h = h.replace("**", "").strip(" ·—-|:")
    return h[:width].strip()


def stages_from_url(url, limit=6):
    p = _Heads()
    p.feed(fetch(url))
    seen, out = set(), []
    for h in p.heads:
        h = _tidy(h)
        key = h.replace(" ", "")
        if len(h) < 2 or key in seen:
            continue
        seen.add(key)
        out.append(h)
    title = re.sub(r"\s*[—–]\s*S21 Phone.*$", "", (p.title or "").strip())
    return title, out[:limit]


# ── 무장 ────────────────────────────────────────────────────────────────────

def rundown(root, stages, pos="bottomLeft", w=260, h=300, theme="amber",
            font="mono", opacity=0.92, stroke=1.5, scale=0.5):
    return {"root": root, "stages": stages, "pos": pos, "w": w, "h": h,
            "theme": theme, "font": font, "opacity": opacity,
            "stroke": stroke, "overlayScale": scale, "version": 9}


def adb(device, *remote, timeout=25):
    # JSON 안에 공백이 있어서 원격 명령을 한 덩어리 문자열로 넘긴다.
    cmd = " ".join(remote)
    p = subprocess.run(["adb", "-s", device, "shell", cmd],
                       capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def ensure_device(device):
    rc, out = adb(device, "echo", "ping", timeout=15)
    if rc == 0 and "ping" in out:
        return True
    subprocess.run(["adb", "connect", device], capture_output=True, timeout=20)
    rc, out = adb(device, "echo", "ping", timeout=15)
    return rc == 0 and "ping" in out


def broadcast(device, action, rd=None, show=None):
    parts = ["am", "broadcast", "--user", "0", "-a", action, "-n", COMPONENT]
    if rd is not None:
        # JSON 에 작은따옴표가 없다는 전제 — 있으면 제거해 안전하게 만든다
        parts += ["--es", "rundown", "'" + json.dumps(rd, ensure_ascii=False).replace("'", "") + "'"]
    if show is not None:
        parts += ["--ei", "show", str(show)]
    return adb(device, *parts)


def save(rd):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(rd, f, ensure_ascii=False, indent=1)
    return STORE


def disarm(device):
    """오버레이 하강."""
    return broadcast(device, "kr.parksy.axis.OFF")


def service_up(device, needle):
    """그 서비스가 살아 있는가. dumpsys 한 번으로 둘 다 본다."""
    rc, out = adb(device, "dumpsys activity services kr.parksy.axis", timeout=45)
    return rc == 0 and needle in out


def is_armed(device):
    """콘티(Flutter 오버레이)가 떠 있는가."""
    return service_up(device, SVC_OVERLAY)


def is_tv(device):
    """나레이터 액자가 떠 있는가."""
    return service_up(device, SVC_TV)


def tv(device, on=True, w=None, h=None, video=None, mute=True):
    """나레이터 액자(CRT) 켜기/끄기.

    크기·여백을 **주지 않는 게 기본**이다. 서비스가 액자 비율(402:650)로 크기를
    계산하고, 오른쪽 아래 여백 6dp 로 앉힌다. 여기서 숫자를 정하면 서비스 기본값과
    두 곳에서 관리하게 되어 반드시 어긋난다(AxisArmReceiver 주석의 같은 교훈).
    """
    parts = ["am", "broadcast", "--user", "0",
             "-a", TV_ACTION if on else TV_OFF_ACTION, "-n", COMPONENT]
    if on:
        if w is not None:
            parts += ["--ei", "w", str(w)]
        if h is not None:
            parts += ["--ei", "h", str(h)]
        if video:
            parts += ["--es", "video", video]
        parts += ["--ei", "mute", "1" if mute else "0"]
    return adb(device, *parts)


def arm(device, rd, show=1, settle=1.5, fresh=False):
    """무장. **반드시 이 함수로만.**

    show=0 은 **저장만** 한다 — 화면을 건드리지 않는다. 예전엔 이 경우에도
    OFF 를 먼저 보내서, "저장만"이라던 명령이 떠 있던 오버레이를 내려버렸다.
    (`--show 0` 과 `--off` 가 같은 일을 하고 있었다.)

    show=1 이고 **이미 떠 있을 때만** OFF → 대기 → ARM 을 탄다.

    ⚠️ 2026-09-23 실측 — 무장된 상태에서 ARM 을 다시 보내면 옛 프로세스가
    OverlayService.onDestroy 에서 죽는다:

        java.lang.RuntimeException: Unable to stop service
          flutter.overlay.window...OverlayService: java.lang.RuntimeException:
          Cannot execute operation because FlutterJNI is not attached to native.
            at FlutterJNI.ensureAttachedToNative(FlutterJNI.java:516)
            at ActivityThread.handleStopService(ActivityThread.java:6137)

    새 프로세스가 이어받아 화면은 살아나지만, 크래시 다이얼로그가 뜨면
    **그게 녹화에 그대로 찍힌다.** OFF 로 먼저 내리고 1.5초 쉬면
    3회 반복 실측 전부 깨끗했다(창 4개 유지, 크래시 0).

    ── 그래서 이미 떠 있으면 **아예 안 건드린다** (2026-09-23) ────────────────
    OFF→ARM 바운스보다 나은 길이 앱 안에 있었다. `show=0` 은 서비스를 죽이지
    않고 **소켓에 reload 만 넣어 콘티를 갈아끼운다** — AxisArmReceiver 주석의
    설계 의도가 정확히 이것이다("재시작 없음 = 안 깜빡임").

    이 경로가 위 바운스보다 나은 이유 셋:
      ① **Boss 가 끌어놓은 자리가 산다.** 창이 재시작되면 위치가 기본 좌하단으로
         풀린다(실측: 끌어놓은 [40,1744] → 재무장 후 [0,1784]). 서비스를 안 죽이면
         안 풀린다. Boss 요구 "전부 다 내가 위치 이동할 수 있게"가 이걸 요구한다.
      ② **1.5초 대기가 사라진다.** 녹화 시작 경로가 그만큼 빨라진다.
      ③ 크래시 경로를 아예 안 탄다 — 바운스는 크래시를 피하려던 것이지
         없애려던 게 아니었다.

    `fresh=True` 로 부르면 예전처럼 OFF→ARM 바운스를 탄다(창 규격을 바꿔야 할 때).
    """
    if not show:
        return broadcast(device, "kr.parksy.axis.ARM", rd=rd, show=0)

    if not fresh and is_armed(device):
        # 살아 있는 창에 콘티만 갈아끼운다 — 자리·크기 그대로, 깜빡임 없음.
        return broadcast(device, "kr.parksy.axis.ARM", rd=rd, show=0)

    if fresh and is_armed(device):
        disarm(device)
        time.sleep(settle)
    return broadcast(device, "kr.parksy.axis.ARM", rd=rd, show=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="파싱할 URL 또는 로컬 HTML 경로")
    ap.add_argument("--stages", help="쉼표로 구분한 카테고리 (수동)")
    ap.add_argument("--root", default="", help="오버레이 상단 제목")
    ap.add_argument("--show", type=int, default=1, help="1=띄운다 0=저장만")
    ap.add_argument("--off", action="store_true", help="오버레이 하강")
    ap.add_argument("--last", action="store_true", help="저장해 둔 콘티로 재무장")
    ap.add_argument("--tv", action="store_true",
                    help="나레이터 액자(CRT)를 오른쪽 아래에 띄운다")
    ap.add_argument("--tv-off", action="store_true", help="나레이터 액자 내린다")
    ap.add_argument("--tv-sound", action="store_true",
                    help="액자 소리를 켠다 (기본 무음 — 녹화에 섞이지 않게)")
    ap.add_argument("--tv-h", type=int, default=None,
                    help="액자 세로 크기 dp (기본 96x155 — 액자 비율)")
    ap.add_argument("--device", default=DEFAULT_DEVICE)
    ap.add_argument("--fresh", action="store_true",
                    help="떠 있어도 창을 새로 만든다 (자리·크기를 처음부터 다시 잡을 때)")
    ap.add_argument("--dry-run", action="store_true", help="방송 없이 콘티만 출력")
    a = ap.parse_args()

    if not ensure_device(a.device):
        print(f"[!] 기기에 붙지 못했습니다: {a.device} — `adb connect {a.device}` 확인", file=sys.stderr)
        return 2

    if a.off:
        rc, out = disarm(a.device)
        print(out)
        return rc

    if a.tv or a.tv_off:
        rc, out = tv(a.device, on=a.tv, h=a.tv_h, mute=not a.tv_sound)
        print(out)
        return rc

    if a.last:
        if not os.path.exists(STORE):
            print(f"[!] 저장된 콘티 없음: {STORE}", file=sys.stderr)
            return 2
        rd = json.load(open(STORE, encoding="utf-8"))
    else:
        if a.stages:
            stages = [s.strip() for s in a.stages.split(",") if s.strip()]
            root = a.root or "[LIVE]"
        elif a.url:
            title, stages = stages_from_url(a.url)
            root = a.root or (f"[LIVE] {title}"[:48] if title else "[LIVE]")
            if not stages:
                print("[!] 페이지에서 제목/헤딩을 못 찾았습니다", file=sys.stderr)
                return 2
        else:
            ap.error("--url 또는 --stages 또는 --off 또는 --last 가 필요합니다")
        rd = rundown(root, stages)

    print(json.dumps(rd, ensure_ascii=False))
    if a.dry_run:
        return 0

    save(rd)
    rc, out = arm(a.device, rd, show=a.show, fresh=a.fresh)
    print(out)
    print(f"[+] 콘티 저장: {STORE}" + (" (화면엔 안 띄움)" if a.show == 0 else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
