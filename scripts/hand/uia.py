#!/usr/bin/env python3
"""Local uiautomator dump → find by text/desc/id → tap center. No LLM."""
from __future__ import annotations

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from typing import Any

DEFAULT_SERIAL = "100.86.15.50:5900"
REMOTE_XML = "/sdcard/Download/grok-cross/hand-ui.xml"


def adb(serial: str, *args: str, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["adb", "-s", serial, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def dump_xml(serial: str) -> str:
    r = adb(serial, "shell", "uiautomator", "dump", REMOTE_XML)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "uiautomator dump failed")
    p = adb(serial, "exec-out", "cat", REMOTE_XML)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError("pull xml failed")
    return p.stdout


def parse_bounds(s: str) -> tuple[int, int, int, int] | None:
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", s or "")
    if not m:
        return None
    return tuple(int(x) for x in m.groups())  # type: ignore[return-value]


def nodes_from_xml(xml: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml)
    out: list[dict[str, Any]] = []
    for el in root.iter("node"):
        b = parse_bounds(el.attrib.get("bounds", ""))
        if not b:
            continue
        out.append(
            {
                "text": el.attrib.get("text") or "",
                "desc": el.attrib.get("content-desc") or "",
                "id": el.attrib.get("resource-id") or "",
                "className": el.attrib.get("class") or "",
                "package": el.attrib.get("package") or "",
                "clickable": el.attrib.get("clickable") == "true",
                "bounds": list(b),
            }
        )
    return out


def score(n: dict[str, Any], *, text: str = "", desc: str = "", rid: str = "") -> int:
    b = n.get("bounds") or [0, 0, 0, 0]
    if b[2] - b[0] < 8 or b[3] - b[1] < 8:
        return 0
    s = 0
    if text:
        if n["text"] == text or n["desc"] == text:
            s += 100
        elif text in n["text"] or text in n["desc"]:
            s += 40
    if desc:
        if n["desc"] == desc:
            s += 100
        elif desc in n["desc"]:
            s += 40
    if rid:
        if n["id"] == rid or n["id"].endswith("/" + rid):
            s += 100
        elif rid in n["id"]:
            s += 20
    if s and n["clickable"]:
        s += 5
    return s


def find_nodes(nodes: list[dict[str, Any]], **kw: str) -> list[dict[str, Any]]:
    ranked = []
    for n in nodes:
        sc = score(n, text=kw.get("text") or "", desc=kw.get("desc") or "", rid=kw.get("id") or "")
        if sc:
            ranked.append((sc, n))
    ranked.sort(key=lambda x: -x[0])
    return [n for _, n in ranked]


def tap_bounds(serial: str, bounds: list[int]) -> None:
    x = (bounds[0] + bounds[2]) // 2
    y = (bounds[1] + bounds[3]) // 2
    r = adb(serial, "shell", "input", "tap", str(x), str(y))
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "tap failed")


def main(argv: list[str]) -> int:
    import json

    serial = DEFAULT_SERIAL
    args = argv[:]
    if args and args[0] == "--serial":
        serial = args[1]
        args = args[2:]
    if not args:
        print("usage: uia.py [--serial SERIAL] dump|find|click [--text T] [--desc D] [--id I]", file=sys.stderr)
        return 2
    op = args[0]
    kw: dict[str, str] = {}
    i = 1
    while i < len(args):
        if args[i] in ("--text", "--desc", "--id") and i + 1 < len(args):
            key = "id" if args[i] == "--id" else args[i][2:]
            kw[key] = args[i + 1]
            i += 2
        else:
            i += 1
    xml = dump_xml(serial)
    nodes = nodes_from_xml(xml)
    if op == "dump":
        print(json.dumps({"ok": True, "engine": "uia", "n": len(nodes), "nodes": nodes[:80]}, ensure_ascii=False))
        return 0
    hits = find_nodes(nodes, **kw)
    if op == "find":
        print(json.dumps({"ok": bool(hits), "engine": "uia", "node": hits[0] if hits else None, "hits": len(hits)}, ensure_ascii=False))
        return 0 if hits else 1
    if op == "click":
        if not hits:
            print(json.dumps({"ok": False, "engine": "uia", "error": "not_found", "q": kw}, ensure_ascii=False))
            return 1
        tap_bounds(serial, hits[0]["bounds"])
        print(json.dumps({"ok": True, "engine": "uia", "node": hits[0]}, ensure_ascii=False))
        return 0
    print("unknown op", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
