#!/usr/bin/env python3
"""hand — accessibility first, uiautomator second, vision never by default.

AutoJS6 HTTP on the tablet (127.0.0.1:18765) via adb shell curl.
If the radar is down, start it, then fall back to local uiautomator XML
(no LLM). Vision/screenshot is an explicit `hand.py vision-needed` signal.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

DEFAULT_SERIAL = "100.86.15.50:5900"
PORT = 18765
REMOTE_JS = "/sdcard/Scripts/hand-server.js"
REMOTE_ONCE = "/sdcard/Scripts/hand-once.js"
REMOTE_CMD = "/sdcard/Download/grok-cross/cmd.json"
REMOTE_RES = "/sdcard/Download/grok-cross/result.json"
HERE = Path(__file__).resolve().parent
LOCAL_JS = HERE / "autojs" / "hand-server.js"
LOCAL_ONCE = HERE / "autojs" / "hand-once.js"


def adb(serial: str, *args: str, timeout: int = 25) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["adb", "-s", serial, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def autojs_get(serial: str, path: str, timeout: int = 5) -> dict | None:
    """HTTP via adb forward. Android shell has no curl — curl from this host."""
    subprocess.run(
        ["adb", "-s", serial, "forward", f"tcp:{PORT}", f"tcp:{PORT}"],
        capture_output=True,
        text=True,
        timeout=8,
    )
    url = f"http://127.0.0.1:{PORT}{path}"
    r = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout), url],
        capture_output=True,
        text=True,
        timeout=timeout + 4,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def run_intent(serial: str, remote_js: str) -> None:
    adb(
        serial,
        "shell",
        "am",
        "start",
        "-n",
        "org.autojs.autojs6/org.autojs.autojs.external.open.RunIntentActivity",
        "-a",
        "android.intent.action.VIEW",
        "-t",
        "application/x-javascript",
        "-d",
        f"file://{remote_js}",
    )


def push_js(serial: str) -> None:
    adb(serial, "shell", "mkdir", "-p", "/sdcard/Scripts", "/sdcard/Download/grok-cross")
    if LOCAL_ONCE.exists():
        subprocess.run(
            ["adb", "-s", serial, "push", str(LOCAL_ONCE), REMOTE_ONCE],
            check=False,
            capture_output=True,
        )
    if LOCAL_JS.exists():
        subprocess.run(
            ["adb", "-s", serial, "push", str(LOCAL_JS), REMOTE_JS],
            check=False,
            capture_output=True,
        )


def autojs_once(serial: str, doc: dict, timeout: float = 8.0) -> dict | None:
    """File IPC: cmd.json → AutoJS6 once.js → result.json. No LLM."""
    push_js(serial)
    adb(serial, "shell", "rm", "-f", REMOTE_CMD, REMOTE_RES)
    tmp = Path("/tmp/hand-cmd.json")
    tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    subprocess.run(
        ["adb", "-s", serial, "push", str(tmp), REMOTE_CMD],
        check=False,
        capture_output=True,
    )
    run_intent(serial, REMOTE_ONCE)
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(0.25)
        p = adb(serial, "exec-out", "cat", REMOTE_RES)
        if p.returncode == 0 and p.stdout.strip().startswith("{"):
            try:
                return json.loads(p.stdout)
            except json.JSONDecodeError:
                continue
    return None


def start_server(serial: str) -> None:
    if not LOCAL_JS.exists():
        raise SystemExit(f"missing {LOCAL_JS}")
    adb(serial, "shell", "mkdir", "-p", "/sdcard/Scripts", "/sdcard/Download/grok-cross")
    subprocess.run(
        ["adb", "-s", serial, "push", str(LOCAL_JS), REMOTE_JS],
        check=False,
        capture_output=True,
    )
    adb(
        serial,
        "shell",
        "am",
        "start",
        "-n",
        "org.autojs.autojs6/org.autojs.autojs.external.open.RunIntentActivity",
        "-a",
        "android.intent.action.VIEW",
        "-t",
        "application/x-javascript",
        "-d",
        f"file://{REMOTE_JS}",
    )
    for _ in range(12):
        time.sleep(0.4)
        h = autojs_get(serial, "/health")
        if h and h.get("ok"):
            return


def ensure_server(serial: str) -> dict | None:
    h = autojs_get(serial, "/health")
    if h and h.get("ok"):
        return h
    start_server(serial)
    return autojs_get(serial, "/health")


def uia_cmd(serial: str, op: str, **kw: str) -> dict:
    cmd = [sys.executable, str(HERE / "uia.py"), "--serial", serial, op]
    for k, v in kw.items():
        if v:
            cmd.extend([f"--{k}", v])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if not r.stdout.strip():
        return {"ok": False, "engine": "uia", "error": r.stderr.strip() or "empty"}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "engine": "uia", "error": r.stdout[:200]}


def qpath(route: str, **kw: str) -> str:
    qs = urllib.parse.urlencode({k: v for k, v in kw.items() if v})
    return f"{route}?{qs}" if qs else route


def click(serial: str, **kw: str) -> dict:
    # uia first: proven on this tab. AutoJS6 intent is optional (HAND_AUTOJS=1)
    # until RunIntentActivity actually writes result.json.
    import os

    if os.environ.get("HAND_AUTOJS") == "1":
        d = autojs_once(serial, {"op": "click", **kw})
        if d and d.get("ok"):
            d["via"] = "autojs6"
            return d
    u = uia_cmd(serial, "click", **kw)
    u["via"] = "uia"
    if not u.get("ok"):
        u["vision"] = "NEED_VISION"
        u["reason"] = "no accessibility node; canvas/webview only then"
    return u


def find(serial: str, **kw: str) -> dict:
    d = autojs_once(serial, {"op": "find", **kw})
    if d and d.get("ok"):
        d["via"] = "autojs6"
        return d
    u = uia_cmd(serial, "find", **kw)
    u["via"] = "uia"
    return u


def tree(serial: str) -> dict:
    return uia_cmd(serial, "dump")


def chrome_imagine(serial: str) -> dict:
    adb(
        serial,
        "shell",
        "am",
        "start",
        "-a",
        "android.intent.action.VIEW",
        "-d",
        "https://grok.com/imagine",
        "-p",
        "com.android.chrome",
    )
    return {"ok": True, "op": "chrome_imagine"}


def focus(serial: str) -> str:
    r = adb(serial, "shell", "dumpsys", "window")
    lines = [ln.strip() for ln in r.stdout.splitlines() if "mCurrentFocus" in ln or "mFocusedApp" in ln]
    return "\n".join(lines[:4])


def parse_kv(args: list[str]) -> tuple[str, dict[str, str]]:
    serial = DEFAULT_SERIAL
    if args[:1] == ["--serial"] and len(args) >= 2:
        serial = args[1]
        args = args[2:]
    kw: dict[str, str] = {}
    op = args[0] if args else "help"
    i = 1
    rest: list[str] = []
    while i < len(args):
        if args[i] in ("--text", "--desc", "--id", "--timeout") and i + 1 < len(args):
            kw[args[i][2:]] = args[i + 1]
            i += 2
        else:
            rest.append(args[i])
            i += 1
    if rest and "text" not in kw and op in ("click", "find", "input"):
        kw["text"] = " ".join(rest)
    return serial, {**{"_op": op}, **kw}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(
            "hand.py [--serial TAB] health|start|focus|open|tree|find|click|input\n"
            "  click --text 완료\n"
            "  click --desc '오후 2:59'\n"
            "  find  --text References\n"
            "vision is NOT a command. if click fails: NEED_VISION"
        )
        return 0
    serial, kw = parse_kv(argv)
    op = kw.pop("_op")
    if op == "health":
        h = autojs_get(serial, "/health") or autojs_once(serial, {"op": "health"})
        print(json.dumps(h or {"ok": False, "error": "radar_down"}, ensure_ascii=False))
        return 0 if h and h.get("ok") else 1
    if op == "start":
        push_js(serial)
        start_server(serial)
        h = autojs_get(serial, "/health") or autojs_once(serial, {"op": "health"})
        print(json.dumps(h or {"ok": False, "error": "start_failed"}, ensure_ascii=False))
        return 0 if h and h.get("ok") else 1
    if op == "focus":
        print(focus(serial))
        return 0
    if op == "open":
        print(json.dumps(chrome_imagine(serial), ensure_ascii=False))
        return 0
    if op == "tree":
        print(json.dumps(tree(serial), ensure_ascii=False))
        return 0
    if op == "find":
        print(json.dumps(find(serial, **kw), ensure_ascii=False))
        return 0
    if op == "click":
        d = click(serial, **kw)
        print(json.dumps(d, ensure_ascii=False))
        return 0 if d.get("ok") else 1
    if op == "input":
        ensure_server(serial)
        d = autojs_get(serial, qpath("/input", **kw)) or uia_cmd(serial, "find", **kw)
        print(json.dumps(d, ensure_ascii=False))
        return 0 if d.get("ok") else 1
    print("unknown op", op, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
