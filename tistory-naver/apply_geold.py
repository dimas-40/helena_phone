"""
티스토리 스킨 <head> JSON-LD 주입 (GEO — AI가 읽는 원조 정체 그래프)
- GET  /manage/design/skin/html.json → {html, css, ...}
- html 의 </head> 앞에 JSON-LD <script> (Person @id→GitHub #person + WebSite + sameAs) 주입
- 마커 <!-- HELENA-GEO-START/END --> 로 멱등 (재적용 시 블록 교체)
- css 는 그대로 두고 html 만 교체 → POST html.json {html, css, isPreview:false}
- 정체 그래프: 모든 티스토리 블로그의 <head>가 같은 Person @id(GitHub)를 가리키게 →
  LLM 크롤러가 "이 블로그도 결국 GitHub의 Helena Park"로 재구성. (헌법 제17조 GEO)
실행: python3 tistory-naver/apply_geold.py [--account galaxys21] [--all] [--dry-run]
"""

import asyncio, argparse, json, time, sys, re
from pathlib import Path
from playwright.async_api import async_playwright

BASE          = Path(__file__).parent
ACCOUNTS_FILE = BASE / "accounts.json"
COOKIES_DIR   = BASE / "cookies"

GEO_START = "<!-- HELENA-GEO-START -->"
GEO_END   = "<!-- HELENA-GEO-END -->"

# 블로그별 메타 (WebSite name + GitHub 대응 레포 + YouTube 채널) — accounts.json 의 id 키
# SSOT: dtslib-papyrus hq/TISTORY-ENDPRODUCT-MAPPING-2026-08-22.md §2.5 (16레포 전수, v3 08-27)
BLOG_META = {
    "dtslib1k":          ("dtslib 대표·문학 — 경제방송 HQ", "dtslib-branch", "@dtslib-branch"),
    "hitop":             ("phoneparis 과학", "phoneparis", "@phoneparis-r6q"),
    "lafilosofia":       ("alexandria 철학·요양원", "alexandria-sanctuary", "@alexandria-y6k"),
    "midmath":           ("buckleychang 수학·논리", "buckleychang.com", "@dtslib-branch"),
    "midsocial":         ("buddies 사회·소상공인", "buddies.kr", "@dtslib-branch"),
    "korean-parksy":     ("koosy 지사 대표", "koosy", "@dtslib-branch"),
    "kr-merit-bluff":    ("gohsy 허세교양", "gohsy", "@dtslib-branch"),
    "kr-merit-shaman":   ("artrew 샤먼·예술", "artrew", "@artrew-i1w"),
    "kr-merit-halfblood":("papafly 혼종어학", "papafly", "@dtslib-branch"),
    "kr-merit-aggro":    ("justino 어그로", "justino", "@justino-fashion"),
}

PERSON_ID = "https://github.com/dtslib1979#person"


def render_geold(blog_name, blog_url, repo, channel):
    """JSON-LD 정체 그래프 블록. Person(@id=GitHub dtslib1979) + WebSite(publisher→Person) + 레포→채널 동선."""
    same_as = [
        "https://github.com/dtslib1979",
        "https://dtslib.kr",
        "https://www.youtube.com/@dtslib-branch",
        "https://www.youtube.com/@phoneparis-r6q",
        "https://www.youtube.com/@alexandria-y6k",
        "https://www.youtube.com/@artrew-i1w",
        "https://www.youtube.com/@justino-fashion",
    ]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": PERSON_ID,
                "name": "dtslib",
                "url": "https://github.com/dtslib1979",
                "description": "경제방송 — 16레포×10블로그×6채널, 1인 미디어 출판·방송",
                "sameAs": same_as,
            },
            {
                "@type": "WebSite",
                "@id": f"{blog_url}#website",
                "name": blog_name,
                "url": blog_url,
                "inLanguage": "ko",
                "publisher": {"@id": PERSON_ID},
                "about": {
                    "@type": "SoftwareSourceCode",
                    "name": repo,
                    "codeRepository": f"https://github.com/dtslib1979/{repo}",
                },
                "sameAs": [f"https://www.youtube.com/{channel}"],
            },
        ],
    }
    inner = json.dumps(ld, ensure_ascii=False, indent=2)
    return f"{GEO_START}\n<script type=\"application/ld+json\">\n{inner}\n</script>\n{GEO_END}"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


async def kakao_login(page, email, pw):
    log(f"  재로그인: {email}")
    await page.goto("https://www.tistory.com/auth/login",
                    wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)
    try:
        btn = page.locator("a.btn_login.link_kakao_id, a:has-text('카카오계정으로 로그인')").first
        await btn.wait_for(state="visible", timeout=8000)
        await btn.click()
        await page.wait_for_timeout(4000)
    except Exception as e:
        log(f"  카카오 버튼 없음: {e}")
        return False
    try:
        await page.wait_for_selector("#loginId--1, input[name='loginId'], input[autocomplete='username']", timeout=15000)
        await page.fill("#loginId--1, input[name='loginId'], input[autocomplete='username']", email)
        await page.fill("#password--2, input[name='password'], input[type='password']", pw)
        await page.click("button[type='submit'], .btn_g.btn_confirm, button.submit")
        await page.wait_for_timeout(5000)
    except Exception as e:
        log(f"  폼 입력 실패: {e}")
    for _ in range(10):
        url = page.url
        if "tistory.com" in url and "login" not in url and "kakao.com" not in url:
            return True
        await page.wait_for_timeout(1000)
    return False


async def ensure_logged_in(page, email, pw, html_url):
    cookies = await page.context.cookies("https://www.tistory.com")
    if any(c["name"] == "TSSESSION" for c in cookies):
        try:
            r = await page.request.get(html_url)
            ct = r.headers.get("content-type", "") or ""
            if r.status == 200 and "application/json" in ct:
                log("  ✅ 기존 세션 유효 (TSSESSION + JSON 응답)")
                return True
            log("  ⚠️ TSSESSION 만료 감지 (JSON 아님) — 재로그인")
        except Exception as e:
            log(f"  세션 검증 실패: {e}")
    return await kakao_login(page, email, pw)


def replace_block(text, start_marker, end_marker, new_block):
    """마커 블록 교체 (멱등). 없으면 None 반환."""
    if start_marker in text and end_marker in text:
        s = text.index(start_marker)
        e = text.index(end_marker, s) + len(end_marker)
        return text[:s] + new_block + text[e:]
    return None


def inject_head(html, block):
    """</head> 앞에 블록 주입. 없으면 <body> 앞, 그것도 없으면 html 끝. 멱등은 호출부에서."""
    m = re.search(r"</head\s*>", html, re.IGNORECASE)
    if m:
        return html[:m.start()] + block + "\n" + html[m.start():]
    m = re.search(r"<body\b", html, re.IGNORECASE)
    if m:
        return html[:m.start()] + block + "\n" + html[m.start():]
    return block + "\n" + html


async def inject_geo(page, acc, dry_run):
    """로그인된 세션에서 한 블로그에 GEO 블록 주입."""
    account_id = acc["id"]
    slug = acc["blog"]
    blog_url = f"https://{slug}.tistory.com/"
    blog_name, repo, channel = BLOG_META.get(account_id, (slug, "", ""))

    log(f"=== GEO 주입 (account={account_id}, blog={slug}) ===")
    html_url = f"https://{slug}.tistory.com/manage/design/skin/html.json"

    resp = await page.request.get(html_url)
    if resp.status != 200:
        log(f"  ❌ GET 실패: {resp.status}")
        return False
    j = await resp.json()
    html = j.get("html", "")
    css = j.get("css", "")
    log(f"  skinname={j.get('skinname')} | html={len(html)}자 | css={len(css)}자")

    block = render_geold(blog_name, blog_url, repo, channel)
    replaced = replace_block(html, GEO_START, GEO_END, block)
    if replaced is not None:
        new_html = replaced
        log("  기존 GEO 블록 교체")
    else:
        new_html = inject_head(html, block)
        log("  신규 GEO 블록 주입 (</head> 앞)")

    if dry_run:
        has_head = bool(re.search(r"</head\s*>", html, re.IGNORECASE))
        log(f"  [dry-run] </head>={has_head}, 블록={len(block)}자 — 저장 생략")
        return True

    payload = {"html": new_html, "css": css, "isPreview": False}
    log(f"  POST {html_url} (html={len(new_html)}자)")
    save = await page.request.post(html_url, data=payload)
    body = await save.text()
    log(f"  POST status={save.status} | 응답: {body[:200]}")

    if save.status < 300:
        chk = await page.request.get(html_url)
        cj = await chk.json()
        ok = GEO_START in cj.get("html", "")
        log(f"  {'✅ GEO 주입 완료·검증' if ok else '⚠️ 저장은 됐으나 재조회 마커 없음 — 수동 확인'} {slug}")
        return ok
    log(f"  ❌ 저장 실패: {save.status} — {body[:300]}")
    return False


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", type=str, default="", help="콤마구분 계정 id (예: dtslib1k,hitop)")
    parser.add_argument("--all", action="store_true", help="accounts.json 전 계정 순회")
    parser.add_argument("--dry-run", action="store_true", help="GET만 하고 저장 안 함")
    args = parser.parse_args()

    data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    pw = data["password"]
    only = {x.strip() for x in args.account.split(",") if x.strip()}

    # email 기준 그룹핑 — 계정마다 로그인 1회 → 그 계정 소속 블로그만 순회 (batch_apply.py 와 동일)
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

            # state 쿠키 복원 (per-email — batch_apply.py 와 공유)
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

            # 로그인 1회 (첫 블로그 html_url 로 세션 검증)
            first_url = f"https://{members[0]['blog']}.tistory.com/manage/design/skin/html.json"
            if not await ensure_logged_in(page, email, pw, first_url):
                log(f"❌ 로그인 실패({email}) — 다음 계정으로")
                await ctx.close()
                continue
            await ctx.storage_state(path=str(st_path))

            for a in members:
                try:
                    await inject_geo(page, a, args.dry_run)
                except Exception as e:
                    log(f"  ❌ 예외 ({a['id']}): {e}")
            await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
