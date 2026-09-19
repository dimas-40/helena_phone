#!/usr/bin/env python3
import asyncio, json, re, subprocess, time, os
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
ACCOUNTS = json.load(open(BASE/"accounts.json"))
EMAIL = "dtslib2k@kakao.com"
PW = ACCOUNTS.get("password","")
_se = open("/root/work/.secrets.env").read()
TG_TOKEN = re.search(r"TG_TOKEN=(\S+)", _se).group(1)
TG_CHAT = re.search(r"TG_CHAT=(\S+)", _se).group(1)

def tg_photo(path, caption):
    subprocess.run(["curl","-s","-X","POST",f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
        "-F",f"chat_id={TG_CHAT}","-F",f"photo=@{path}","-F",f"caption={caption}"], capture_output=True, timeout=30)

def wait_file(path, timeout=360):
    t0=time.time()
    while time.time()-t0 < timeout:
        if os.path.isfile(path):
            v=open(path).read().strip()
            if v: return v
        time.sleep(3)
    return None

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        ctx = await b.new_context()
        pg = await ctx.new_page()
        await pg.goto("https://www.tistory.com/auth/login", wait_until="domcontentloaded", timeout=30000)
        await pg.wait_for_timeout(2000)
        await pg.locator("a.btn_login.link_kakao_id").first.click()
        await pg.wait_for_timeout(4000)
        await pg.fill("#loginId--1", EMAIL)
        await pg.fill("#password--2", PW)
        await pg.locator("button.btn_g.highlight.submit, button[type='submit']").first.click()
        await pg.wait_for_timeout(6000)
        # CAPTCHA
        if await pg.locator("iframe[src*='dkaptcha'], iframe[title*='CAPTCHA']").count() > 0:
            await pg.screenshot(path="/tmp/wt_captcha.png")
            tg_photo("/tmp/wt_captcha.png", "카카오 CAPTCHA — 지도 장소명 알려줘")
            print("CAPTCHA 전송됨 — 답 대기", flush=True)
            ans = wait_file("/tmp/wt_captcha.txt")
            if ans:
                for f in pg.frames:
                    if "dkaptcha" in (f.url or ""):
                        try:
                            await f.locator("input").first.fill(ans)
                            await f.locator("button:has-text('Submit'), .btn_submit_dkaptcha").first.click()
                            print(f"CAPTCHA 답 입력: {ans}", flush=True)
                        except Exception as e:
                            print("CAPTCHA 입력 실패:", str(e)[:60], flush=True)
                await pg.wait_for_timeout(6000)
        # SMS 자동 (termux-sms-list 폴링, 새 코드 기다림)
        print("SMS 폴링 시작", flush=True)
        base=None; code=None; t0=time.time()
        while time.time()-t0 < 120:
            r = subprocess.run(["termux-sms-list"], capture_output=True, text=True, timeout=20)
            sms = json.loads(r.stdout)
            recent = sorted(sms, key=lambda x:x.get("received",""), reverse=True)
            for mm in recent[:5]:
                m2 = re.search(r"(?:Verification Code|인증번호)[:\s]*\[?(\d{6})\]?", mm.get("body",""))
                if m2:
                    c = m2.group(1)
                    if base is None: base=c
                    elif c != base: code=c; break
            if code: break
            time.sleep(4)
        if code:
            print(f"SMS 코드: {code}", flush=True)
            for sel in ["input[inputmode='numeric']","input[type='tel']","input[name*='code']","input[placeholder*='인증']","input[placeholder*='번호']"]:
                try:
                    if await pg.locator(sel).count() > 0:
                        await pg.locator(sel).first.fill(code); print(f"코드 입력: {sel}", flush=True); break
                except: pass
            await pg.locator("button[type='submit'], button:has-text('확인')").first.click()
            await pg.wait_for_timeout(8000)
        ok = "tistory.com" in pg.url and "login" not in pg.url
        if ok:
            cookies = await ctx.cookies()
            (BASE/"cookies"/"dtslib2k_state.json").write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
            print(f"✅ 로그인 성공 — 세션 저장", flush=True)
        else:
            print(f"⚠️ 미완 — {pg.url[:80]}", flush=True)
        await b.close()

asyncio.run(main())
