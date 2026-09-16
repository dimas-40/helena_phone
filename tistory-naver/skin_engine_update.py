import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, 'mcp-servers')
import phone_webtoon_make_mcp as m

BASE = Path('tistory-naver')
ACCOUNTS_FILE = BASE / 'accounts.json'
COOKIES_DIR = BASE / 'cookies'
JS_ENGINE = m.IMAGE_JS + m.INTERACTIVE_JS
JS_START = "<!-- WEBTOON-ENGINE-JS-START -->"
JS_END = "<!-- WEBTOON-ENGINE-JS-END -->"

def remove_old_js(html):
    # 옛 주입본(무마커) 제거 — 고유 시그니처 기준
    for sig in ("/* 연출 엔진", "classList.add('wt-js')"):
        idx = html.find(sig)
        if idx == -1: continue
        s = html.rfind("<script>", 0, idx)
        e = html.find("</script>", idx) + len("</script>")
        if s != -1 and e > s:
            html = html[:s] + html[e:]
    return html

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
            print("❌ TSSESSION 없음"); sys.exit(1)
        url = f"https://{slug}.tistory.com/manage/design/skin/html.json"
        resp = await page.request.get(url)
        if resp.status != 200: print(f"❌ GET {resp.status}"); sys.exit(1)
        j = await resp.json()
        html, css = j.get("html",""), j.get("css","")

        # 기존 마커 블록 제거
        if JS_START in html and JS_END in html:
            s = html.index(JS_START); e = html.index(JS_END, s) + len(JS_END)
            html = html[:s] + html[e:]
        html = remove_old_js(html)  # 무마커 옛 주입본 제거

        block = f"{JS_START}\n{JS_ENGINE}\n{JS_END}"
        idx = html.rfind("</body>")
        if idx == -1: idx = len(html)
        html = html[:idx] + block + html[idx:]
        print("✅ JS 엔진 교체 (트리거 앞당김)")

        payload = {"html": html, "css": css, "isPreview": False}
        save = await page.request.post(url, data=payload)
        print(f"POST status={save.status} | {(await save.text())[:120]}")

asyncio.run(main())
