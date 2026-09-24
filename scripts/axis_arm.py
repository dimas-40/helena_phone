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
import math
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


# ── 한 줄에 담기는 양 (2026-09-24 실측 + 소스 확인) ─────────────────────────
#
# 이 앱은 **폰트를 창 크기에 비례**시킨다. 창을 키우면 글자도 커진다:
#
#   lib/widgets/tree_view.dart:150
#       s  = (창W/260 + 창H/300)/2      ← OverlayDefaults 260x300
#       fs = 14*s,   px = 12*s
#   android/.../AxisArmReceiver.java:174
#       창 = (w × overlayScale) dp
#
# 그래서 **상자를 키워도 담기는 글자 수가 늘지 않는다.** 유도하면:
#
#   담기는 단위 = (w − K_HEAD·D) / (K_UNIT·D),   D = w/260 + h/300
#
# overlayScale 은 약분되어 사라진다 — 크게 잡든 작게 잡든 글자 수는 같다.
#
# 실측 검산(2026-09-24, 1080x2340 @450dpi): 콘티 w=260 h=450 → 창 365x632px
#   = 130x225dp, s=0.625, fs=8.75dp. 그 화면에 "누나의 생각을"(한글6+공백1)이
#   딱 들어갔다 → 6.0 단위.  식: (260 − 28.1·2.5)/(12.6·2.5) = 6.02  ✓
#
# ⚠️ 세로 맞춤 때문에 h 가 w 를 따라 커져서, 6단계 기준 담기는 양은 **어느
#    상자 크기에서나 ~7.7단위로 포화**한다(w=300·400·500 전부 7.69).
#    즉 **문장형 카테고리는 이 앱에서 수학적으로 안 들어간다.** 폭을 키우는 건
#    여유를 사는 것뿐이고, 진짜 해법은 카테고리를 짧게 쓰는 것이다.
#    (APK 를 고쳐 두 줄 줄바꿈을 켜면 되지만, 재설치 때 SYSTEM_ALERT_WINDOW
#     권한이 회수되므로 그 값을 치를 만하지 않다. 메모리 참조.)
K_HEAD = 28.1        # 테두리·여백·접두기호('├─ ')가 fs 에 비례해 먹는 양
K_UNIT = 12.6        # 표시폭 1단위(한글 1자)가 fs 에 비례해 먹는 양
ACTIVE_LOSS = 2.2    # 활성 행은 '◀●' 를 달고 있어 그만큼 글자가 덜 들어간다
BOX_N_DEF = 5        # 기본 단계 수 — 담기는 글자 수가 여기서 정해진다
                     # (n=5 → 6.8단위 / n=6 → 5.6 / n=7 → 4.4)


def _disp_width(s):
    """한글 1.0 · 그 외 0.55 로 센 표시폭. 한글 폰트가 라틴보다 넓다."""
    return sum(0.55 if ord(c) < 0x2000 else 1.0 for c in s)


def capacity(w, h):
    """이 상자 한 줄에 담기는 표시폭 단위 수. overlayScale 곱하기 **전** w·h."""
    D = w / 260.0 + h / 300.0
    if D <= 0:
        return 0.0
    return max(0.0, (w - K_HEAD * D) / (K_UNIT * D))


def title_capacity(w, h):
    """제목줄에 담기는 단위 수 — 제목 폰트가 fs×1.1 이라 행보다 조금 넓다."""
    D = w / 260.0 + h / 300.0
    if D <= 0:
        return 1.0
    return max(1.0, (w - 12.0 * D) / (13.86 * D))


def _cut_units(s, max_units):
    """표시폭 max_units 안으로 자른다. 단어 경계를 살리되, 안 되면 글자로."""
    if _disp_width(s) <= max_units:
        return s
    cur = ""
    for word in s.split(" "):
        trial = (cur + " " + word) if cur else word
        if _disp_width(trial) <= max_units:
            cur = trial
        else:
            break
    if _disp_width(cur) >= max_units * 0.5:
        return cur.rstrip(" ·—-|:+")      # 끊고 남은 구분기호는 뗀다
    out, wsum = "", 0.0                       # 한 단어가 통째로 길다
    for ch in s:
        cw = 0.55 if ord(ch) < 0x2000 else 1.0
        if wsum + cw > max_units:
            break
        out += ch
        wsum += cw
    return out.rstrip()


def _tidy(h, max_units=None):
    """긴 헤딩을 **화면이 실제로 담는 길이**로 줄인다.

    예전엔 18글자로 잘랐는데 그건 담기는 양의 3배였다. 그래서 녹화본에
    "구형 폰 한 ..." 처럼 잘려 나왔다 — 자르는 쪽과 그리는 쪽이 서로 다른
    숫자를 알고 있었다. 이제 한 곳(capacity)만 본다.
    """
    h = re.sub(r"^[\d]+(\.[\d]+)*[.)]?\s*", "", h.strip())      # 앞 번호 제거
    h = re.sub(r"\s*[(（].*?[)）]\s*", " ", h)                    # 괄호 부제 제거
    h = re.split(r"\s+[—–·|]\s+", h)[0]                          # 대시 뒤 부제 제거
    h = h.replace("**", "").strip(" ·—-|:")
    return _cut_units(h, DEFAULT_UNITS if max_units is None else max_units)


def stages_from_url(url, limit=BOX_N_DEF, max_units=None):
    p = _Heads()
    p.feed(fetch(url))
    seen, out = set(), []
    for h in p.heads:
        h = _tidy(h, max_units)
        key = h.replace(" ", "")
        if len(h) < 2 or key in seen:
            continue
        seen.add(key)
        out.append(h)
    title = re.sub(r"\s*[—–]\s*S21 Phone.*$", "", (p.title or "").strip())
    return title, out[:limit]


# ── 무장 ────────────────────────────────────────────────────────────────────

# ── 상자 크기 자동 (높이 + 폭) ──────────────────────────────────────────────
#
# 세로 넘침 조건:  K·(w/260 + h/300)/2 > h      (K = s=1 기준 내용 높이)
# h 에 대해 풀면:  h ≥ 15·K·w / (13·(600 − K))   ← K→600 이면 발산
#
# K 는 실측 3점("BOTTOM OVERFLOWED BY N" 를 읽어 역산)으로 맞췄다:
#     제목1줄 + 6단계  → 넘침 0    K = 300
#     제목2줄 + 6단계  → 넘침 15   K = 330
#     제목1줄 + 12단계 → 넘침 107  K = 514
K_BASE = 56.0
K_TITLE = 30.0
K_ROW = 35.7
H_MAX = 700.0        # 이보다 큰 상자는 화면 밖으로 나간다
H_MIN = 220.0
W_DEF = 340.0        # 창 = w×overlayScale = 170dp (화면 384dp 의 44%)
TITLE_LINES_MAX = 1  # 제목도 여기까지만. 안 자르면 상자를 밀어올려 **담기는
                     # 양을 오히려 깎는다** — 실측: 제목 4줄 → h=700 → 2.98단위.
                     # 2줄로 늘리면 K_TITLE 30 을 더 먹어 단계당 1단위를 잃는다
                     # (6단계 기준 5.58 → 4.55). 제목은 짧은 라벨로 쓴다.


def _box_h(root, n, w, margin=1.06, title_lines_max=TITLE_LINES_MAX):
    """이 (제목, 단계수, 폭) 에서 세로로 안 넘치는 높이 → (h, K).

    **제목 줄 수를 먼저 묶고** 높이를 푼다. 순서를 뒤집으면(높이 먼저) 제목이
    접히며 상자를 키우고, 커진 상자가 다시 담기는 양을 깎는 나선에 빠진다.
    """
    tw = _disp_width(root)
    h = H_MIN
    for _ in range(12):
        allowed = title_lines_max * max(1.0, capacity(w, h))
        tl = max(1, math.ceil(min(tw, allowed) / max(1.0, title_capacity(w, h))))
        K = K_BASE + K_TITLE * tl + K_ROW * n
        if K >= 600.0:
            return H_MAX, K
        need = (15.0 * K * w) / (13.0 * (600.0 - K))
        nh = max(H_MIN, min(H_MAX, need * margin))
        if abs(nh - h) < 1.0:
            return nh, K
        h = nh
    return h, K


def box_size(root, n, w=W_DEF):
    """(w, h, 담기는단위) — 이 콘티가 다 들어가는 상자."""
    h, _ = _box_h(root, n, w)
    h = int(round(h))
    return int(w), h, capacity(w, h)


def usable_units(w, h):
    """활성 행('◀●' 를 달고 있다)까지 감안해 **실제로 쓸 수 있는** 단위 수."""
    return max(2.0, capacity(w, h) - ACTIVE_LOSS)


DEFAULT_UNITS = usable_units(*box_size("", BOX_N_DEF)[:2])


def rundown(root, stages, pos="bottomLeft", w=None, h=None, theme="amber",
            font="mono", opacity=0.92, stroke=1.5, scale=0.5):
    """콘티 JSON.

    w·h 를 안 주면 단계 수와 제목에 맞춰 잡고, **카테고리도 담기는 길이로
    자른다.** 고정값으로 두면 자르는 쪽과 그리는 쪽이 다른 숫자를 알게 되어
    반드시 어긋난다 — 2026-09-24 녹화본의 "구형 폰 한 ..." 이 그 사고다.
    제목(root)은 자르지 않는다. 여러 줄로 접히기 때문이다.
    """
    n = len(stages)
    if w is None:
        w = int(W_DEF)
    if h is None:
        h, K = _box_h(root, n, w)
        h = int(round(h))
        if K >= 600.0:
            print(f"[!] 단계가 너무 많다({n}개) — 상자를 {h}dp 로 잘랐다. "
                  f"뒤쪽 카테고리가 안 보일 수 있다", file=sys.stderr)
    cap = usable_units(w, h)
    root = _cut_units(root, TITLE_LINES_MAX * capacity(w, h))
    return {"root": root, "stages": [_cut_units(s, cap) for s in stages],
            "pos": pos, "w": w, "h": h, "theme": theme, "font": font,
            "opacity": opacity, "stroke": stroke, "overlayScale": scale, "version": 9}


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


# ── 넘침 측정 (화면에서 직접) ──────────────────────────────────────────────
#
# 위 _box_h() 는 **한 방에 못 맞춘다.** 상자를 키우면 s 가 커지고 → 폰트가 커지고
# → 제목이 한 줄 더 접혀서 내용이 또 커진다. 되먹임이라 닫힌 식이 안 선다.
# 실측: h=345 에서 제목 2줄·넘침 4.1px → h=382 로 키웠더니 제목 3줄·넘침 13px.
# **키웠는데 더 나빠졌다.**
#
# 그래서 마지막 한 단계는 화면을 본다. Flutter 는 넘칠 때 창 하단에 노란 줄무늬
# 배너("BOTTOM OVERFLOWED BY N PIXELS")를 그린다. 그 노랑을 찾으면 넘친 것이다.

def _window_frame(device):
    """콘티 창(gr=BOTTOM LEFT)의 frame=[l,t][r,b]. 못 찾으면 None.

    ⚠️ 창이 둘이다(콘티·TV). 이름도 크기도 같아서 **gravity 로 가른다** —
    콘티는 BOTTOM LEFT, TV 는 TOP START. (axis_arm 주석의 그 함정)
    """
    rc, out = adb(device, "dumpsys window windows", timeout=45)
    if rc != 0:
        return None
    blk = []
    for line in out.splitlines():
        if "Window #" in line:
            blk = []
            continue
        blk.append(line)
        if "frame=[" in line and any("BOTTOM LEFT" in b for b in blk):
            m = re.search(r"frame=\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]", line)
            if m:
                return tuple(int(g) for g in m.groups())
    return None


def overflow_px(device):
    """지금 콘티 창의 넘침 픽셀 수. 0=안 넘침, None=못 쟀다."""
    fr = _window_frame(device)
    if not fr:
        return None
    l, t, r, b = fr
    if r - l < 20 or b - t < 20:
        return None
    p = subprocess.run(["adb", "-s", device, "exec-out", "screencap", "-p"],
                       capture_output=True, timeout=30)
    if p.returncode != 0 or len(p.stdout) < 1000:
        return None
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(p.stdout)).convert("RGB")
    except Exception:                                  # noqa: BLE001
        return None
    # 배너는 창 맨 아래에 붙는다. 아래 12% 만 본다.
    band = im.crop((max(0, l), max(0, b - max(12, int((b - t) * 0.12))), r, b))
    # 노랑: R·G 높고 B 낮음. 줄무늬라 몇 개만 있어도 잡힌다.
    pix = band.get_flattened_data() if hasattr(band, "get_flattened_data") else band.getdata()
    hit = sum(1 for px in pix if px[0] > 190 and px[1] > 190 and px[2] < 90)
    return 1 if hit > 40 else 0


def fit_h(device, rd, tries=6, step=1.18, cap=900):
    """넘침이 사라질 때까지 상자 높이를 올린다. 화면을 보며 맞춘다.

    높이는 창을 만들 때만 잡히므로 매번 --fresh 로 새로 만든다. 대신 창이
    재시작되니 Boss 가 끌어놓은 자리는 풀린다 — **그래서 이건 1회 보정용**이고,
    맞춘 값을 rundown() 이 기본값으로 쓰게 하는 게 목적이다.
    """
    h = rd.get("h") or _box_h(rd.get("root", ""), len(rd.get("stages", [])),
                              rd.get("w", W_DEF))[0]
    for i in range(tries):
        rd = dict(rd, h=int(h))
        arm(device, rd, show=1, fresh=True)
        time.sleep(3.0)
        ov = overflow_px(device)
        print(f"  h={int(h):4d} → 넘침 {ov}")
        if ov is None:
            print("  [!] 넘침을 못 쟀다 — 창이 안 떴거나 screencap 실패")
            return None
        if ov == 0:
            return int(h)
        h *= step
        if h > cap:
            print(f"  [!] {cap}dp 까지 키워도 안 맞는다 — 내용을 줄여야 한다 "
                  f"(단계 수·제목 길이)")
            return None
    print("  [!] 시도 횟수 초과")
    return None


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
    ap.add_argument("--fit", action="store_true",
                    help="상자 높이를 화면 보며 맞춘다 (넘침 배너가 사라질 때까지)")
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

    if a.fit:
        print(f"[*] 높이 맞추기 — 시작 {rd['h']}dp")
        got = fit_h(a.device, rd)
        if got is None:
            return 2
        print(f"[+] 넘침 없는 높이: {got}dp")
        rd = dict(rd, h=got)

    save(rd)
    rc, out = arm(a.device, rd, show=a.show, fresh=a.fresh)
    print(out)
    print(f"[+] 콘티 저장: {STORE}" + (" (화면엔 안 띄움)" if a.show == 0 else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
