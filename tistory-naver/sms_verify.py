import asyncio, time
from pathlib import Path
from playwright.async_api import async_playwright

CODE_FILE = Path("sms_code2.txt")
if CODE_FILE.exists(): CODE_FILE.unlink()

async def main():
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context("cookies/galaxys21", headless=True,
            viewport={"width":1280,"height":900}, args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.tistory.com/auth/login", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        await page.locator('a.btn_login.link_kakao_id, a:has-text("카카오계정으로 로그인")').first.click()
        await page.wait_for_timeout(3000)
        await page.fill("#loginId--1", "eae_kr@kakao.com")
        await page.fill("#password--2", "think4good*")
        await page.click("button[type=submit], .btn_g.btn_confirm, button.submit")
        await page.wait_for_timeout(5000)
        print("URL1:", page.url, flush=True)
        if "ActionPenalty" in page.url:
            await page.locator('text=전화번호 인증').first.click()
            await page.wait_for_timeout(3000)
            print("URL2:", page.url, flush=True)
            if "selectContactPhoneNumberForActionPenalty" in page.url:
                await page.locator('button:has-text("다음"), a:has-text("다음")').first.click()
                await page.wait_for_timeout(3000)
                print("URL2b:", page.url, flush=True)
            print("BODY2:", (await page.evaluate("document.body.innerText.slice(0,300)")), flush=True)
            print("WAITING_FOR_CODE", flush=True)
            code = None
            for _ in range(180):
                if CODE_FILE.exists():
                    code = CODE_FILE.read_text().strip()
                    if code: break
                await asyncio.sleep(1)
            if not code:
                print("TIMEOUT_NO_CODE", flush=True)
                await ctx.close(); return
            print("GOT_CODE:", code, flush=True)
            inp = page.locator("input[type=text], input[type=tel], input[type=number]").first
            await inp.click()
            await inp.press_sequentially(code, delay=120)
            await page.wait_for_timeout(500)
            try:
                await page.locator('button:has-text("확인"), button[type=submit]').first.click()
            except Exception as e:
                print("SUBMIT_CLICK_ERR:", e, flush=True)
            await page.wait_for_timeout(4000)
            print("URL3:", page.url, flush=True)
            print("BODY3:", (await page.evaluate("document.body.innerText.slice(0,300)")), flush=True)
        await ctx.storage_state(path="cookies/eae-kr_state.json")
        await ctx.close()

asyncio.run(main())
