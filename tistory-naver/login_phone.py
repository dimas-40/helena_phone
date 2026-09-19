#!/usr/bin/env python3
"""
login_phone.py — 폰 단독 티스토리 로그인 + 카카오 2FA(SMS 자동) + 세션 저장/갱신

폰(proot Ubuntu)에서 돌리는 세션 프로세스:
  크롬(chromium+Xvfb) 카카오 로그인 → 2FA SMS(termux-sms-list로 자동 조회)
  → 코드 입력 → 세션 쿠키 저장(cookies/<account>_state.json)

갱신: 세션 만료되면 이 스크립트 재실행 (멱등). 쿠키 재사용은 apply_*/post.py 가 처리.

사용:
  xvfb-run -a /usr/bin/python3 tistory-naver/login_phone.py dtslib2k
"""
import asyncio, argparse, json, re, subprocess, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
ACCOUNTS_FILE = BASE / "accounts.json"
COOKIES_DIR = BASE / "cookies"


def _latest_sms():
    """termux-sms-list 최신 카카오 Verification Code 반환 (id, received, code)."""
    try:
        r = subprocess.run(["termux-sms-list"], capture_output=True, text=True, timeout=20)
        sms = json.loads(r.stdout)
        recent = sorted(sms, key=lambda x: x.get("received", ""), reverse=True)
        for m in recent[:6]:
            m2 = re.search(r"Verification Code:\s*(\d{6})", m.get("body", ""))
            if m2:
                return m.get("_id"), m.get("received"), m2.group(1)
    except Exception:
        pass
    return None, None, None


def get_sms_code(wait=75):
    """로그인 전 기준(baseline)과 '다른' 새 코드가 올 때까지 폴링."""
    base_id, base_time, base_code = _latest_sms()
    t0 = time.time()
    while time.time() - t0 < wait:
        _id, _time, code = _latest_sms()
        if code and code != base_code:
            return code
        time.sleep(4)
    return None


async def kakao_login(email, pw):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        ctx = await b.new_context()
        pg = await ctx.new_page()
        await pg.goto("https://www.tistory.com/auth/login", wait_until="domcontentloaded", timeout=30000)
        await pg.wait_for_timeout(2000)
        await pg.locator("a.btn_login.link_kakao_id").first.click()
        await pg.wait_for_timeout(4000)
        await pg.fill("#loginId--1", email)
        await pg.fill("#password--2", pw)
        await pg.locator("button.btn_g.highlight.submit, button[type='submit']").first.click()
        await pg.wait_for_timeout(5000)
        # 2FA 코드 입력
        code = get_sms_code()
        if code:
            print(f"  SMS 코드: {code}", flush=True)
            for sel in ["input[inputmode='numeric']", "input[type='tel']",
                        "input[name*='code']", "input[placeholder*='인증']",
                        "input[placeholder*='코드']", "input[placeholder*='번호']"]:
                try:
                    if await pg.locator(sel).count() > 0:
                        await pg.locator(sel).first.fill(code)
                        print(f"  코드 입력: {sel}", flush=True)
                        break
                except Exception:
                    pass
            for btn in ["button:has-text('확인')", "button:has-text('인증')",
                        "button[type='submit']", ".btn_g.highlight.submit"]:
                try:
                    if await pg.locator(btn).count() > 0:
                        await pg.locator(btn).first.click()
                        print(f"  2FA 제출: {btn}", flush=True)
                        break
                except Exception:
                    pass
            await pg.wait_for_timeout(8000)
        ok = "tistory.com" in pg.url and "login" not in pg.url
        if ok:
            cookies = await ctx.cookies()
            (COOKIES_DIR / f"{account}_state.json").write_text(
                json.dumps(cookies, ensure_ascii=False, indent=2))
            print(f"✅ 로그인 성공 — 세션 저장 ({len(cookies)} 쿠키)", flush=True)
        else:
            print(f"⚠️ 미완 — URL: {pg.url[:90]}", flush=True)
        await b.close()
        return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("account", help="계정 id (예: dtslib2k)")
    a = ap.parse_args()
    account = a.account
    accs = json.load(open(ACCOUNTS_FILE)).get("accounts", [])
    acc = next((x for x in accs if x.get("id") == account), None)
    if not acc:
        sys.exit(f"계정 없음: {account}")
    email = acc["email"]
    pw = json.load(open(ACCOUNTS_FILE)).get("password", "")
    ok = asyncio.run(kakao_login(email, pw))
    sys.exit(0 if ok else 1)
