#!/usr/bin/env python3
"""parksy_axis_mcp.py — Axis 오버레이 오토킷을 MCP 로 (_Claude 2026-09-24)

Boss 그림 (원문):
  "사전 작업으로 MCP 를 뛰었을 때 너가 그 오버레이키트 안에다가 카테고리
   프롬프트를 넣어 주는 거. 이게 프롬프팅이라고 내가 얘기한 거야."

그래서 이 서버는 **URL 하나 받아서 진행 상태판에 카테고리를 밀어넣는 문**이다.
Boss 가 손으로 치지 않는다 — 도구를 부르면 콘티가 만들어져 저장되고,
녹화를 시작하면 그게 자동으로 뜬다.

    axis_arm(url="https://...")   ← 프롬프트 넣기 (핵심)
    axis_tv(on=True)              ← 나레이터 액자
    axis_watch(action="start")    ← 녹화 감지 자동무장 켜기
    axis_status()                 ← 지금 뭐가 떠 있나
    axis_off()                    ← 전부 내리기

실제 일은 `scripts/axis_arm.py` 와 `scripts/rec_watch.py` 가 한다. 여기는
껍데기지 로직이 아니다 — 로직이 둘로 갈라지면 반드시 어긋난다.

⚠️ 이 서버는 stdio 로 뜬다. 직접 돌려도 터미널에 아무것도 안 나오는 게 정상이다.
   확인하려면 Claude Code 에 붙여서 도구를 부르거나 `axis_status()` 를 쓴다.
"""
import json
import os
import subprocess
import sys

from mcp.server.mcpserver import MCPServer

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.abspath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import axis_arm  # noqa: E402
import rec_watch  # noqa: E402

server = MCPServer(
    "parksy-axis",
    version="0.1.0",
    instructions=(
        "Axis 오버레이 오토킷. URL 을 주면 강의용 진행 상태판(콘티)을 만들어 "
        "저장하고, 화면 녹화를 시작하면 그게 자동으로 뜬다."
    ),
)

DEVICE = axis_arm.DEFAULT_DEVICE


def _dev(device=""):
    """도구가 준 기기, 없으면 기본. 로직은 전부 scripts/ 쪽에 있다."""
    return device.strip() or DEVICE


# ── 프롬프트 넣기 (핵심 도구) ──────────────────────────────────────────────

@server.tool()
def axis_arm_prompt(url: str = "", stages: str = "", root: str = "",
                    show: bool = True, device: str = "",
                    fit: bool = False) -> str:
    """URL(또는 카테고리 목록)을 진행 상태판에 넣는다. — Boss 가 말한 "프롬프팅".

    ⚠️ **카테고리는 짧게 써라.** 이 앱은 폰트를 창 크기에 비례시켜서 한 줄에
    담기는 양에 상한이 있다(실측 + 소스 유도). 5단계 기준 **6.8단위**
    (한글 1자 = 1.0, 공백·라틴 = 0.55)가 천장이고, 상자를 키워도 늘지 않는다.
    넘치면 코드가 알아서 자르지만, 자르고 나면 "누나를"/"누나의" 처럼
    뭉툭해진다. **처음부터 짧게 쓰는 게 맞다** — 어차피 리마인더판이다.
    제목도 1줄로 잘린다.

    Args:
        url: 페이지 주소(또는 로컬 HTML 경로). h1~h3 를 뽑아 카테고리로 쓴다.
        stages: 쉼표로 구분한 카테고리 (url 대신 직접 줄 때).
        root: 오버레이 상단 제목. 비우면 페이지 제목에서 뽑는다. **1줄로 잘린다.**
        show: True=지금 띄운다 / False=저장만 (녹화 시작 때 뜨게).
        device: adb 시리얼. 비우면 기본(127.0.0.1:5900).
        fit: True 면 상자 높이를 화면 보며 맞춘다 — 마지막 카테고리가 잘리지 않게.

    Returns:
        저장된 콘티 요약 + 무장 결과.
    """
    d = _dev(device)
    if not axis_arm.ensure_device(d):
        return f"adb 붙지 못함: {d} — `adb connect {d}` 확인"

    if stages.strip():
        items = [s.strip() for s in stages.split(",") if s.strip()]
        title = root or "[LIVE]"
    elif url.strip():
        try:
            title, items = axis_arm.stages_from_url(url)
        except Exception as e:                       # noqa: BLE001
            return f"URL 못 읽음: {url} — {e}"
        title = root or (f"[LIVE] {title}"[:48] if title else "[LIVE]")
        if not items:
            return f"페이지에서 제목/헤딩을 못 찾았다: {url}"
    else:
        return "url 또는 stages 중 하나는 필요하다"

    rd = axis_arm.rundown(title, items)
    if fit:
        got = axis_arm.fit_h(d, rd)
        if got:
            rd = dict(rd, h=got)

    axis_arm.save(rd)
    rc, out = axis_arm.arm(d, rd, show=1 if show else 0)
    lines = [
        f"제목: {title}",
        f"카테고리 {len(items)}개: " + " · ".join(items),
        f"상자: {rd['w']}x{rd['h']}dp",
        "저장: " + axis_arm.STORE,
        ("띄움" if show else "저장만 (녹화 시작 때 뜬다)") + f" — {out}",
    ]
    return "\n".join(lines)


# ── 나레이터 액자 ──────────────────────────────────────────────────────────

@server.tool()
def axis_narrator(on: bool = True, device: str = "") -> str:
    """오른쪽 나레이터 CRT 액자를 켜거나 끈다 (Axis v11.4.0 TvOverlayService)."""
    rc, out = axis_arm.tv(_dev(device), on=on)
    return ("액자 올림" if on else "액자 내림") + f" — {out}"


# ── 녹화 감지 자동무장 ─────────────────────────────────────────────────────

@server.tool()
def axis_watch(action: str = "status", device: str = "") -> str:
    """삼성 화면 녹화를 감시한다 — 녹화가 시작되면 키트가 자동으로 뜬다.

    Args:
        action: start | stop | status | log
    """
    a = action.strip().lower()
    if a == "status":
        pid = _watch_pid()
        return (f"감시자 살아있음 (PID {pid})" if pid else "감시자 없음")
    if a == "stop":
        pid = _watch_pid()
        if not pid:
            return "감시자 없음"
        subprocess.run(["kill", str(pid)], check=False)
        return f"감시자 중단 (PID {pid})"
    if a == "log":
        try:
            with open(rec_watch.LOGFILE, encoding="utf-8") as f:
                return "\n".join(f.read().splitlines()[-25:]) or "(로그 비어 있음)"
        except OSError as e:
            return f"로그 못 읽음: {e}"
    if a != "start":
        return f"모르는 action: {action} (start | stop | status | log)"

    if _watch_pid():
        return "이미 돌고 있다"
    cmd = [sys.executable, os.path.join(_SCRIPTS, "rec_watch.py"),
           "--tv", "--daemon", "--device", _dev(device)]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return "감시자 시작 — 녹화 버튼을 누르면 키트 둘이 자동으로 뜬다"


def _watch_pid():
    try:
        with open(rec_watch.PIDFILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


# ── 상태 / 내리기 ──────────────────────────────────────────────────────────

@server.tool()
def axis_status(device: str = "") -> str:
    """지금 뭐가 떠 있는지. 콘티 창·액자·감시자·저장된 콘티."""
    d = _dev(device)
    if not axis_arm.ensure_device(d):
        return f"adb 붙지 못함: {d}"
    arms = axis_arm.is_armed(d)
    tv_on = axis_arm.is_tv(d)
    pid = _watch_pid()
    of = axis_arm.overflow_px(d)
    out = [
        f"진행 상태판(콘티) : {'떠 있음' if arms else '내려감'}",
        f"나레이터 액자      : {'떠 있음' if tv_on else '내려감'}",
        f"녹화 감시자        : {('PID ' + str(pid)) if pid else '없음'}",
        f"넘침               : {'못 쟀다' if of is None else str(of)}  (0=정상)",
    ]
    try:
        with open(axis_arm.STORE, encoding="utf-8") as f:
            rd = json.load(f)
        out.append(f"저장된 콘티        : {rd.get('root', '')} "
                   f"({len(rd.get('stages', []))}단계, {rd.get('h')}dp)")
    except (OSError, ValueError):
        out.append("저장된 콘티        : 없음")
    return "\n".join(out)


@server.tool()
def axis_off(device: str = "") -> str:
    """키트 둘을 모두 내린다. 감시자는 안 건드린다(녹화하면 다시 뜬다)."""
    d = _dev(device)
    rc1, o1 = axis_arm.disarm(d)
    rc2, o2 = axis_arm.tv(d, on=False)
    return f"콘티 내림: {o1}\n액자 내림: {o2}"


if __name__ == "__main__":
    server.run(transport="stdio")
