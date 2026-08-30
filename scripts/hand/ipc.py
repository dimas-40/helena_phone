#!/usr/bin/env python3
"""grok-cross file IPC. CLI writes task.json, AutoJS/hand consumes it."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

CROSS = Path("/sdcard/Download/grok-cross")
INBOX = CROSS / "tasks" / "inbox"
DONE = CROSS / "tasks" / "done"
OUT = CROSS / "outputs"


def ensure() -> None:
    for p in (INBOX, DONE, OUT):
        p.mkdir(parents=True, exist_ok=True)


def put(op: str, **kw) -> Path:
    ensure()
    tid = kw.pop("id", None) or time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    doc = {"id": tid, "op": op, "created": time.time(), **kw}
    path = INBOX / f"{tid}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def take() -> dict | None:
    ensure()
    files = sorted(INBOX.glob("*.json"))
    if not files:
        return None
    p = files[0]
    doc = json.loads(p.read_text(encoding="utf-8"))
    p.rename(DONE / p.name)
    return doc
