#!/usr/bin/env python3
"""Watch grok-cross/outputs. Detect new assets. Do NOT fake ffmpeg.

Tab has no ffmpeg. Concat/TTS belongs on S21 factory, not this radar.
This process only stamps NOW.md when a file lands.
"""
from __future__ import annotations

import time
from pathlib import Path

CROSS = Path("/sdcard/Download/grok-cross")
OUT = CROSS / "outputs"
NOW = CROSS / "NOW.md"
SEEN = CROSS / "outputs.seen"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seen = set()
    if SEEN.exists():
        seen = set(SEEN.read_text(encoding="utf-8").splitlines())
    print("[hand-watch] outputs", OUT)
    while True:
        for f in sorted(OUT.iterdir()) if OUT.exists() else []:
            if not f.is_file():
                continue
            if f.suffix.lower() not in {".png", ".jpg", ".jpeg", ".mp4", ".webp"}:
                continue
            if f.name in seen:
                continue
            seen.add(f.name)
            SEEN.write_text("\n".join(sorted(seen)) + "\n", encoding="utf-8")
            line = f"[+] asset {f.name} bytes={f.stat().st_size}\n"
            print(line, end="")
            NOW.write_text(
                f"# NOW\n\nnew output: `{f}`\nS21 factory concat/TTS next. Tab radar does not render.\n",
                encoding="utf-8",
            )
        time.sleep(2)


if __name__ == "__main__":
    main()
