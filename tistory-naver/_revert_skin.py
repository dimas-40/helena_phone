#!/usr/bin/env python3
"""스킨에서 PARKSY-PLAYER 마커 블록(내가 주입한 wt-viewer) 제거 — 신규글발행 구조로 되돌림."""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_DIR = Path('/root/work/tistory-naver/cookies')
MARKER_START = "<!-- PARKSY-PLAYER-START -->"
MARKER_END = "<!-- PARKSY-PLAYER-END -->"
SLUG = "kr-merit-aggro"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(COOKIES_DIR / SLUG), headless=True, args=["--no-sandbox"])
    pg = ctx.new_page()
    pg.on("dialog", lambda d: d.accept())

    pg.goto(f"https://{SLUG}.tistory.com/manage/design/skin/edit#/source/html", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    if "#/source/html" not in pg.url:
        el = pg.query_selector("text=html 편집")
        if el:
            el.click(force=True); pg.wait_for_timeout(2500)

    cur = pg.evaluate("() => window.monaco.editor.getModels()[0].getValue()")
    log(f"스킨 HTML 길이: {len(cur)} / 마커 존재: {MARKER_START in cur}")

    if MARKER_START in cur:
        new_val = re.sub(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), "", cur, flags=re.S)
        # 주변 빈 줄 정리
        new_val = re.sub(r"\n{3,}", "\n\n", new_val)
        pg.evaluate("(v) => window.monaco.editor.getModels()[0].setValue(v)", new_val)
        pg.wait_for_timeout(1000)
        removed = MARKER_START not in pg.evaluate("() => window.monaco.editor.getModels()[0].getValue()")
        log(f"마커 제거: {'OK' if removed else '실패'}")
        # 저장
        for sel in ["button:has-text('적용')", "button:has-text('저장')"]:
            btn = pg.locator(sel).first
            try:
                if btn.is_visible(timeout=3000):
                    btn.click(); pg.wait_for_timeout(2500)
                    log(f"저장 완료 ({sel})")
                    break
            except Exception:
                pass
    else:
        log("마커 없음 — 되돌릴 것 없음")

    ctx.close()
