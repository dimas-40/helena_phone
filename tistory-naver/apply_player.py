"""
티스토리 10개 블로그 스킨에 ParksyPlayer(웹툰 플레이어) 주입 — 웹툰 솔루션 옵션①
- GET /manage/design/skin/html.json → {html, css}
- </body> 앞에 player.html 내용을 마커(<!-- PARKSY-PLAYER-START/END -->)로 주입 (멱등)
- email 기준 그룹핑 (2계정 → 로그인 2회) + batch_apply가 저장한 세션 재사용
실행: python3 tistory-naver/apply_player.py [--account dtslib1k,hitop] [--dry-run]
"""

import asyncio, argparse, json, time, sys, re
from pathlib import Path
from playwright.async_api import async_playwright

BASE          = Path(__file__).parent
ACCOUNTS_FILE = BASE / "accounts.json"
COOKIES_DIR   = BASE / "cookies"
PLAYER_FILE   = BASE / "player.html"

MARKER_START = "<!-- PARKSY-PLAYER-START -->"
MARKER_END   = "<!-- PARKSY-PLAYER-END -->"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def replace_block(text, start_marker, end_marker, new_block):
    if start_marker in text and end_marker in text:
        s = text.index(start_marker)
        e = text.index(end_marker, s) + len(end_marker)
        return text[:s] + new_block + text[e:]
    return None


def inject_body(html, block):
    """</body> 앞에 주입. 없으면 html 끝에 덧붙임."""
    m = re.search(r"</body\s*>", html, re.IGNORECASE)
    if m:
        return html[:m.start()] + block + "\n" + html[m.start():]
    return html + "\n" + block


async def ensure_logged_in(page, email, pw, html_url):
    cookies = await page.context.cookies("https://www.tistory.com")
    if any(c["name"] == "TSSESSION" for c in cookies):
        try:
            r = await page.request.get(html_url)
            ct = r.headers.get("content-type", "") or ""
            if r.status == 200 and "application/json" in ct:
                return True
        except Exception:
            pass
    log(f"  ⚠️ 세션 만료 — 재로그인 필요: {email}")
    return False


async def inject_player(page, acc, player_block, dry_run):
    slug = acc["blog"]
    log(f"=== player 주입 (blog={slug}) ===")
    html_url = f"https://{slug}.tistory.com/manage/design/skin/html.json"

    resp = await page.request.get(html_url)
    if resp.status != 200:
        log(f"  ❌ GET 실패: {resp.status}")
        return False
    j = await resp.json()
    html = j.get("html", "")
    css = j.get("css", "")
    log(f"  skinname={j.get('skinname')} | html={len(html)}자 | css={len(css)}자")

    block = f"{MARKER_START}\n{player_block}\n{MARKER_END}"
    replaced = replace_block(html, MARKER_START, MARKER_END, block)
    if replaced is not None:
        new_html = replaced
        log("  기존 player 블록 교체")
    else:
        new_html = inject_body(html, block)
        log("  신규 player 블록 주입 (</body> 앞)")

    if dry_run:
        has_body = bool(re.search(r"</body\s*>", html, re.IGNORECASE))
        log(f"  [dry-run] </body>={has_body}, 블록={len(block)}자 — 저장 생략")
        return True

    payload = {"html": new_html, "css": css, "isPreview": False}
    log(f"  POST {html_url} (html={len(new_html)}자)")
    save = await page.request.post(html_url, data=payload)
    body = await save.text()
    log(f"  POST status={save.status} | 응답: {body[:160]}")

    if save.status < 300:
        chk = await page.request.get(html_url)
        cj = await chk.json()
        ok = MARKER_START in cj.get("html", "")
        log(f"  {'✅ player 주입 완료·검증' if ok else '⚠️ 저장됐으나 마커 재조회 실패'} {slug}")
        return ok
    log(f"  ❌ 저장 실패: {save.status} — {body[:300]}")
    return False


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", type=str, default="", help="콤마구분 계정 id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    pw = data["password"]
    only = {x.strip() for x in args.account.split(",") if x.strip()}

    player_block = PLAYER_FILE.read_text(encoding="utf-8")
    log(f"player.html 로드: {len(player_block)}자")

    groups: dict[str, list[dict]] = {}
    for a in data["accounts"]:
        if only and a["id"] not in only:
            continue
        groups.setdefault(a["email"], []).append(a)

    async with async_playwright() as pw:
        for email, members in groups.items():
            ctx_key = email.split("@")[0]
            log(f"\n=== 계정 {email} ({len(members)}개 블로그) ===")
            ctx = await pw.chromium.launch_persistent_context(
                str(COOKIES_DIR / ctx_key),
                headless=True,
                viewport={"width": 1280, "height": 900},
                locale="ko-KR",
                args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

            st_path = COOKIES_DIR / f"{ctx_key}_state.json"
            if st_path.exists():
                st = json.loads(st_path.read_text())
                now = int(time.time())
                cks = []
                for c in st.get("cookies", []):
                    if c.get("domain") in (".tistory.com", ".www.tistory.com", "www.tistory.com", ".daum.net"):
                        if c.get("expires", -1) == -1:
                            c["expires"] = now + 86400 * 7
                        cks.append(c)
                if cks:
                    await ctx.add_cookies(cks)

            first_url = f"https://{members[0]['blog']}.tistory.com/manage/design/skin/html.json"
            if not await ensure_logged_in(page, email, pw, first_url):
                log(f"❌ 로그인 필요({email}) — 세션 없음")
                await ctx.close()
                continue
            await ctx.storage_state(path=str(st_path))

            for a in members:
                try:
                    await inject_player(page, a, player_block, args.dry_run)
                except Exception as e:
                    log(f"  ❌ 예외 ({a['id']}): {e}")
            await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
