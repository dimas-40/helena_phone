import asyncio, json, sys, time
from pathlib import Path
sys.path.insert(0, 'mcp-servers')
import phone_webtoon_make_mcp as m

BASE = Path('tistory-naver')
ACCOUNTS_FILE = BASE / 'accounts.json'
COOKIES_DIR = BASE / 'cookies'

# 스킨 레벨 연출 엔진 (모바일·데스크톱 모두 살아남음)
JS_ENGINE = m.IMAGE_JS + m.INTERACTIVE_JS
CSS_BLOCK = """/* WEBTOON-ENGINE-START */
[data-tl]{will-change:transform,opacity,filter}
.cut{overflow:hidden;border-radius:4px;box-shadow:0 14px 30px rgba(0,0,0,.5)}
.cut img{width:100%;display:block}
.cap{margin:14px 0 0;background:rgba(233,229,207,.96);color:#1a120c;padding:12px 16px;border-radius:14px;font-size:13px;font-weight:700;text-align:center}
.wt-bubble{transition:opacity .4s;will-change:transform}
.wt-char{display:inline-block}
.wt-js .wt-bubble{opacity:0}
.wt-js .wt-bubble.wt-in{opacity:1}
.wt-js .wt-char{opacity:0}
.wt-js .wt-in .wt-char{animation:wttype .4s cubic-bezier(.34,1.56,.64,1) forwards}
@keyframes wttype{0%{opacity:0;transform:translateY(6px) scale(1.4)}100%{opacity:1;transform:translateY(0) scale(1)}}
/* WEBTOON-ENGINE-END */"""

MARK_START = "/* WEBTOON-ENGINE-START */"
MARK_END = "/* WEBTOON-ENGINE-END */"

async def main():
    data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    acc = next(a for a in data["accounts"] if a["id"] == "kr-merit-aggro")
    slug = acc["blog"]

    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            str(COOKIES_DIR / "kr-merit-aggro"), headless=True,
            viewport={"width":1280,"height":900}, locale="ko-KR",
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        cookies = await ctx.cookies("https://www.tistory.com")
        if not any(c["name"]=="TSSESSION" for c in cookies):
            print("❌ TSSESSION 없음 — 먼저 cdp_session_lend 필요"); sys.exit(1)
        print(f"✅ 세션 유효 (TSSESSION) — 블로그={slug}")

        url = f"https://{slug}.tistory.com/manage/design/skin/html.json"
        resp = await page.request.get(url)
        if resp.status != 200:
            print(f"❌ GET {resp.status}"); sys.exit(1)
        j = await resp.json()
        html, css = j.get("html",""), j.get("css","")
        print(f"skinname={j.get('skinname')} | html={len(html)}자 | css={len(css)}자")

        # JS 주입 (html의 </body> 앞)
        if "WEBTOON-ENGINE" not in html:
            idx = html.rfind("</body>")
            if idx == -1: idx = len(html)
            html = html[:idx] + JS_ENGINE + html[idx:]
            print("  JS 엔진 주입 (</body> 앞)")
        else:
            print("  JS 이미 주입됨")

        # CSS 주입 (마커 멱등)
        block = f"{MARK_START}\n{CSS_BLOCK}\n{MARK_END}"
        if MARK_START in css:
            s = css.index(MARK_START); e = css.index(MARK_END, s) + len(MARK_END)
            css = css[:s] + block + css[e:]
        else:
            css = css + "\n" + block
        print("  CSS 주입")

        payload = {"html": html, "css": css, "isPreview": False}
        save = await page.request.post(url, data=payload)
        print(f"  POST status={save.status}")
        print(f"  응답: {(await save.text())[:200]}")

asyncio.run(main())
