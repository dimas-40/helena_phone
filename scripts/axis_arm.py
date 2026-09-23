#!/usr/bin/env python3
"""axis_arm.py — URL/텍스트 → 콘티(rundown) → Axis 오버레이 무장 (_Claude 2026-09-23)

Boss 그림: "내가 URL 주면 파싱해 가지고 카테고리 거기에다가 표현하는 거 미리 작업해서 저장하고,
그거 보면서 화면 녹화하면 되는 거."

경로 (2026-09-23 실측):
  adb shell am broadcast --user 0 -a kr.parksy.axis.ARM \\
    -n kr.parksy.axis/flutter.overlay.window.flutter_overlay_window.AxisArmReceiver \\
    --es rundown '<콘티 JSON>' --ei show 1

  ⚠️ rundown 없이 보내면 앱이 거부한다 — `W/AxisArm: ARM 인데 rundown 이 없습니다`

쓰는 법:
  python3 scripts/axis_arm.py --url https://...        # URL 파싱 → 콘티 → 무장
  python3 scripts/axis_arm.py --stages "오프닝,주제,근거,반전,정리" --root "[LIVE] 강의 01"
  python3 scripts/axis_arm.py --off                    # 하강
  python3 scripts/axis_arm.py --show 0 --url ...       # 저장만 (화면 안 건드림)
  python3 scripts/axis_arm.py --last                   # 저장해 둔 콘티로 재무장
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


def arm(device, rd, show=1, settle=1.5):
    """OFF → (대기) → ARM. **무장은 반드시 이 함수로만.**

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
    """
    disarm(device)
    time.sleep(settle)
    return broadcast(device, "kr.parksy.axis.ARM", rd=rd, show=show)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="파싱할 URL 또는 로컬 HTML 경로")
    ap.add_argument("--stages", help="쉼표로 구분한 카테고리 (수동)")
    ap.add_argument("--root", default="", help="오버레이 상단 제목")
    ap.add_argument("--show", type=int, default=1, help="1=띄운다 0=저장만")
    ap.add_argument("--off", action="store_true", help="오버레이 하강")
    ap.add_argument("--last", action="store_true", help="저장해 둔 콘티로 재무장")
    ap.add_argument("--device", default=DEFAULT_DEVICE)
    ap.add_argument("--dry-run", action="store_true", help="방송 없이 콘티만 출력")
    a = ap.parse_args()

    if not ensure_device(a.device):
        print(f"[!] 기기에 붙지 못했습니다: {a.device} — `adb connect {a.device}` 확인", file=sys.stderr)
        return 2

    if a.off:
        rc, out = disarm(a.device)
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
    rc, out = arm(a.device, rd, show=a.show)
    print(out)
    print(f"[+] 콘티 저장: {STORE}" + (" (화면엔 안 띄움)" if a.show == 0 else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
