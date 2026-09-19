#!/usr/bin/env python3
"""
skin_inject.py — 티스토리 스킨 HTML에 마커 기반 블록(예: 웹툰 플레이어) 주입/갱신
================================================================================
2026-09-12 확정판. skin.py(구버전)의 3가지 문제를 실측으로 찾아 전부 고쳤다:

  1. URL이 옛 경로였음    : /manage/skin/edit → 실제는 /manage/design/skin/edit
  2. 에디터가 바뀌었음    : CodeMirror → Monaco (window.monaco.editor.getModels()[0])
  3. confirm() 다이얼로그  : "html 편집" 버튼 클릭 시 뜨는 네이티브 confirm을
                             Playwright가 기본적으로 자동 취소해서 클릭이 씹혔음
                             → page.on('dialog', accept) 필수

로그인 자체는 카카오 계정당 최초 1회만 필요하고, 그 이후는 브라우저 프로필
(cookies/<account>/)에 세션이 영구 저장되므로 재로그인이 필요 없다.
(2026-09-12 실측: dtslib2k 계정으로 로그인 성공 시 "이 브라우저에서 2단계
인증 사용 안 함"을 체크해뒀기 때문에 다음부턴 SMS 인증조차 안 뜬다.)

혹시 쿠키가 만료돼서 재로그인이 필요해지면:
  - 카카오 로그인 폼 자동 입력 (--password 또는 PASSWORD 환경변수)
  - CAPTCHA(DKAPTCHA, 지도 기반 문제) 발생 시: 스크립트가 스크린샷을 찍고
    captcha_response.txt 파일을 폴링 대기한다. 사람(또는 비전 가능한 AI)이
    스크린샷을 보고 "TEXT:정답" 또는 "CLICK:x,y" 형식으로 그 파일에 써주면
    자동으로 이어서 진행된다. (완전 무인화는 못 함 — 지도 이미지 판독이 필요)
  - SMS 2단계 인증 발생 시: 이 기기 자체의 Termux:API(termux-sms-list)로
    완전 자동 처리한다 — ADB 승인/자기참조 문제 없이 콜드스타트 없이 동작한다
    (2026-09-13 확정, project_adb_sms_kakao_verification 참조). 다른 기기의
    SMS를 읽어야 하는 경우(예: WSL에서 태블릿 SMS 조회)에만 --adb-serial로
    폴백한다.

사용법:
  python3 skin_inject.py --account dtslib2k --slug kr-merit-aggro \
      --player /home/dtsli/parksy-image/tools/tistory/player.html \
      [--password '...']
  # 이 기기(폰)에서 실행 시 --adb-serial 지정 불필요 — Termux:API 자동감지

환경변수(둘 중 하나로 비밀번호 전달, 평문 저장 금지 — 매 실행 1회성 env var로만):
  PASSWORD=... python3 skin_inject.py --account dtslib2k --slug kr-merit-aggro --player player.html
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
COOKIES_DIR = BASE / "cookies"
ACCOUNTS_FILE = BASE / "accounts.json"

MARKER_START = "<!-- PARKSY-PLAYER-START -->"
MARKER_END = "<!-- PARKSY-PLAYER-END -->"

SC_DIR = Path("/tmp/skin_inject_scratch")
SC_DIR.mkdir(exist_ok=True)
RESP_FILE = SC_DIR / "captcha_response.txt"
CODE_FILE = SC_DIR / "sms_code.txt"
LIVE_PNG = SC_DIR / "live.png"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def account_email(account_id: str) -> str:
    data = json.loads(ACCOUNTS_FILE.read_text())
    for acc in data.get("accounts", data if isinstance(data, list) else []):
        if isinstance(acc, dict) and account_id in (acc.get("id"), acc.get("email", "").split("@")[0]):
            return acc.get("email", account_id)
    # accounts.json in this repo is keyed loosely; fall back to id@kakao.com guess
    if "@" in account_id:
        return account_id
    return f"{account_id}@kakao.com"


_SMS_CODE_PATTERNS = [
    re.compile(r"\[Verification Code:\s*(\d{4,8})\]"),
    re.compile(r"\[인증번호:\s*(\d{4,8})\]"),
]


def _extract_code(body: str) -> str | None:
    for pat in _SMS_CODE_PATTERNS:
        m = pat.search(body)
        if m:
            return m.group(1)
    return None


def _termux_sms_available() -> bool:
    """이 환경(폰 자기 자신, proot든 Termux든)에서 termux-sms-list를 바로 쓸 수 있는지.

    2026-09-13 실측 확정: Termux:API 패키지가 설치돼 있으면 proot 안에서도
    Termux 브릿지를 그대로 상속해 호출된다 — ADB 자기참조(내 폰 IP로 내
    폰에 wireless debugging 승인) 없이 곧바로 동작. 자기참조 ADB는 실측
    결과 unauthorized(태블릿처럼 "다른 기기"를 승인한 이력이 없어서
    안 됨) — 그래서 같은 기기의 SMS를 읽을 땐 이 경로가 유일한 무인 해법.
    """
    try:
        r = subprocess.run(["termux-sms-list", "-l", "1"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _read_sms_via_termux_api(after_epoch_ms: int, timeout_s: float) -> str | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = subprocess.run(["termux-sms-list", "-l", "5"], capture_output=True, text=True, timeout=15)
            msgs = json.loads(r.stdout) if r.stdout.strip() else []
        except Exception as e:
            log(f"termux-sms-list 조회 실패: {e}")
            time.sleep(3)
            continue
        for m in msgs:
            try:
                received_ms = int(time.mktime(time.strptime(m["received"], "%Y-%m-%d %H:%M:%S")) * 1000)
            except Exception:
                received_ms = 0
            if received_ms < after_epoch_ms - 5000:  # 5초 여유 (시계 오차)
                continue
            code = _extract_code(m.get("body", ""))
            if code:
                return code
        time.sleep(3)
    return None


def _read_sms_via_adb(adb_serial: str, after_epoch_ms: int, timeout_s: float) -> str | None:
    """박씨 소유 실기기 + 승인된 ADB 전제. content://sms/inbox 직접 조회.

    자기참조(자기 폰 IP로 자기 자신 조회)는 wireless debugging 승인 이력이
    없어 동작 안 함(2026-09-13 실측) — 다른 기기(예: WSL이 폰을 조회, 또는
    폰이 태블릿을 조회)에서만 쓸 수 있다. 같은 기기 SMS는
    _read_sms_via_termux_api()가 우선이고 이건 폴백.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            out = subprocess.run(
                ["adb", "-s", adb_serial, "shell", "content", "query",
                 "--uri", "content://sms/inbox", "--sort", '"date DESC"'],
                capture_output=True, text=True, timeout=15,
            ).stdout
        except Exception as e:
            log(f"adb 조회 실패: {e}")
            time.sleep(3)
            continue
        rows = out.split("Row: ")
        for row in rows[1:3]:
            m_date = re.search(r"date=(\d+)", row)
            code = _extract_code(row)
            if m_date and code and int(m_date.group(1)) >= after_epoch_ms:
                return code
        time.sleep(3)
    return None


def read_sms_code(after_epoch_ms: int, adb_serial: str | None, timeout_s: int = 90) -> str | None:
    """SMS 인증코드 확보 — 환경 자동감지, 콜드스타트 없음(옵션 지정 불필요).

    우선순위: ① 이 기기 자체 Termux:API(termux-sms-list, ADB 불필요·항상
    가장 빠르고 확실) → ② --adb-serial 지정 시 그 기기 ADB 조회(다른 기기의
    SMS를 읽어야 할 때만). 매번 사람이 --adb-serial을 판단해서 넘길 필요
    없이, 실행되는 기기가 자기 SMS를 스스로 읽을 수 있으면 그걸 우선 쓴다.
    """
    if _termux_sms_available():
        log("SMS 코드 확보: Termux:API 직접 (같은 기기, ADB 불필요)")
        return _read_sms_via_termux_api(after_epoch_ms, timeout_s)
    if adb_serial:
        log(f"SMS 코드 확보: ADB 폴백 ({adb_serial})")
        return _read_sms_via_adb(adb_serial, after_epoch_ms, timeout_s)
    return None


def run_login(pg, slug: str, email: str, password: str, adb_serial: str | None):
    RESP_FILE.unlink(missing_ok=True)
    CODE_FILE.unlink(missing_ok=True)

    trigger_ms = int(time.time() * 1000)
    pg.goto(
        f"https://www.tistory.com/auth/login?redirectUrl=https%3A%2F%2F{slug}.tistory.com%2Fmanage",
        wait_until="domcontentloaded", timeout=30000,
    )
    pg.wait_for_timeout(2000)
    el = pg.query_selector('a:has-text("카카오")')
    if el:
        el.click()
    pg.wait_for_timeout(2500)
    pg.fill('input[name="loginId"], input[type="text"]', email)
    pg.fill('input[type="password"]', password)
    pg.click('button:has-text("Log In"), button:has-text("로그인")')
    pg.wait_for_timeout(3000)
    log(f"로그인 제출 완료: {email}")

    deadline = time.time() + 900
    skip_clicked = False
    last_snap = 0.0

    while time.time() < deadline:
        url = pg.url
        try:
            body_text = pg.inner_text("body")
        except Exception:
            body_text = ""

        if time.time() - last_snap > 4:
            try:
                pg.screenshot(path=str(LIVE_PNG))
            except Exception:
                pass
            last_snap = time.time()

        # 2026-09-13 실측 확정: 로케일 따라 안내문구가 영/한으로 다르고, 게다가
        # "닫기" 버튼뿐인 예고 모달(진짜 문제 아님)을 닫아도 그 텍스트가
        # innerText에 잔류해 무한루프에 빠지는 버그가 있었음(body_text 문자열
        # 매칭 방식 자체가 신뢰 불가). 대신 실제 DKAPTCHA 위젯의 존재(iframe
        # src에 "dkaptcha" 포함, §dump_frame 실측 확인된 도메인)로만 판정한다
        # — 이게 유일하게 "지금 화면에 진짜 풀어야 할 문제가 떠 있다"를
        # 보장하는 신호.
        dkaptcha_frame = None
        for fr in pg.frames:
            if "dkaptcha" in fr.url:
                dkaptcha_frame = fr
                break
        is_captcha = dkaptcha_frame is not None

        # 예고 모달("닫기" 버튼만 있는 안내창, 실제 문제 아님)은 자동으로 닫는다.
        if not is_captcha:
            dismiss = pg.query_selector('button:has-text("닫기"), button:has-text("Close")')
            if dismiss:
                try:
                    is_dkaptcha_intro = "안전한 서비스 이용" in body_text or "ensure the safe use" in body_text.lower()
                    if is_dkaptcha_intro:
                        dismiss.click(force=True)
                        log("예고 모달 자동 닫음 (진짜 문제 아님)")
                        time.sleep(1.5)
                        continue
                except Exception:
                    pass

        if is_captcha:
            if not RESP_FILE.exists():
                log(f"CAPTCHA 대기 중 — 스크린샷: {LIVE_PNG} 을 보고 "
                    f"{RESP_FILE}에 'TEXT:정답' 또는 'CLICK:x,y' 써넣을 것")
                time.sleep(2)
                continue
            resp = RESP_FILE.read_text().strip()
            frames = [pg] + pg.frames
            if resp.startswith("CLICK:"):
                x, y = map(float, resp[6:].split(","))
                pg.mouse.click(x, y)
                log(f"CAPTCHA 클릭: {x},{y}")
            elif resp.startswith("TEXT:"):
                ans = resp[5:]
                inp = None
                for fr in frames:
                    try:
                        cand = fr.query_selector("#inpDkaptcha")
                        if cand:
                            inp = cand
                            break
                    except Exception:
                        pass
                if inp:
                    inp.fill(ans)
                    log(f"CAPTCHA 텍스트입력: {ans}")
            time.sleep(1.2)
            submit_btn = None
            for fr in frames:
                try:
                    cand = fr.query_selector(".item_submit_btn, button:has-text('Submit')")
                    if cand:
                        submit_btn = cand
                        break
                except Exception:
                    pass
            if submit_btn:
                submit_btn.click(force=True)
                log("CAPTCHA Submit 클릭")
            RESP_FILE.unlink(missing_ok=True)
            time.sleep(3)
            continue

        if "TwoStepVerification" in url or "verification code" in body_text.lower():
            if not skip_clicked:
                skip = pg.query_selector("text=Do Not Use 2-Step Verification on this Browser")
                if skip:
                    try:
                        skip.click()
                        log("2FA 영구 스킵 체크 — 다음부턴 이 브라우저는 SMS 인증 안 뜸")
                    except Exception as e:
                        log(f"스킵체크 실패: {e}")
                skip_clicked = True

            if not CODE_FILE.exists():
                code = read_sms_code(trigger_ms, adb_serial)
                if code:
                    CODE_FILE.write_text(code)
                    log(f"SMS 코드 자동 확보: {code}")

            if not CODE_FILE.exists():
                log(f"SMS 코드 대기 중 — {CODE_FILE}에 코드 써넣을 것 (자동확보 실패 시 수동)")
                time.sleep(2)
                continue

            code = CODE_FILE.read_text().strip()
            code_input = pg.query_selector('input[type="text"]:visible, input[name*="code" i]')
            if code_input:
                code_input.fill(code)
            confirm = pg.query_selector('button:has-text("Confirm"), button:has-text("확인")')
            if confirm:
                confirm.click()
            log(f"SMS 코드 제출: {code}")
            CODE_FILE.unlink(missing_ok=True)
            time.sleep(3)
            continue

        if "tistory.com" in url and "accounts.kakao.com" not in url and "kauth.kakao.com" not in url:
            log(f"로그인 완료: {url}")
            return True

        time.sleep(2)

    log("로그인 타임아웃")
    return False


def inject_player(pg, slug: str, player_html: str) -> bool:
    edit_url = f"https://{slug}.tistory.com/manage/design/skin/edit#/source/html"
    pg.goto(edit_url, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)

    if "#/source/html" not in pg.url:
        el = pg.query_selector("text=html 편집")
        if not el:
            log("'html 편집' 버튼을 못 찾음 — 스킨 편집 페이지 구조가 바뀌었을 수 있음")
            return False
        el.click(force=True)
        pg.wait_for_timeout(2500)

    has_monaco = pg.evaluate("() => typeof window.monaco !== 'undefined'")
    if not has_monaco:
        log("Monaco 에디터를 못 찾음")
        return False

    cur = pg.evaluate("() => window.monaco.editor.getModels()[0].getValue()")
    log(f"현재 스킨 HTML 길이: {len(cur)}")

    if MARKER_START in cur:
        pattern = re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END)
        new_val = re.sub(pattern, lambda m: MARKER_START + "\n" + player_html + "\n" + MARKER_END, cur, flags=re.S)
        log("기존 마커 블록 교체")
    else:
        inject = f"\n{MARKER_START}\n{player_html}\n{MARKER_END}\n"
        m = re.search(r"<body[^>]*>", cur)
        new_val = (cur[: m.end()] + inject + cur[m.end() :]) if m else (inject + cur)
        log("마커 블록 신규 삽입")

    pg.evaluate("(v) => { window.monaco.editor.getModels()[0].setValue(v); }", new_val)
    pg.wait_for_timeout(1000)

    ok = pg.evaluate("() => window.monaco.editor.getModels()[0].getValue().includes('parksy-webtoon')")
    if not ok:
        log("주입 검증 실패 — parksy-webtoon 마커가 안 보임")
        return False

    for sel in ["button:has-text('적용')", "button:has-text('저장')"]:
        btn = pg.locator(sel).first
        try:
            if btn.is_visible(timeout=3000):
                btn.click(force=True)
                pg.wait_for_timeout(3000)
                log(f"저장 완료 ({sel})")
                return True
        except Exception:
            pass
    log("저장 버튼을 못 찾음")
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--account", required=True, help="카카오 계정 id (cookies/<account>/ 프로필명)")
    ap.add_argument("--slug", required=True, help="티스토리 블로그 슬러그 (예: kr-merit-aggro)")
    ap.add_argument("--player", required=True, help="주입할 player.html 경로")
    ap.add_argument("--email", default=None, help="카카오 로그인 이메일 (미지정시 accounts.json에서 조회)")
    ap.add_argument("--password", default=os.environ.get("PASSWORD"), help="카카오 비번 (평문 저장 금지, env var 권장)")
    ap.add_argument("--adb-serial", default=None,
                     help="다른 기기 SMS 조회용 ADB 폴백 (같은 기기면 Termux:API가 자동으로 우선 사용되므로 보통 불필요)")
    ap.add_argument("--display", default=os.environ.get("DISPLAY"))
    ap.add_argument("--headless", action="store_true", default=None,
                     help="강제 headless. 미지정시 DISPLAY 유무로 자동판단")
    args = ap.parse_args()

    if args.display:
        os.environ["DISPLAY"] = args.display
    headless = args.headless if args.headless is not None else not bool(args.display)
    log(f"headless={headless} (DISPLAY={args.display or '없음'})")

    player_html = Path(args.player).read_text()
    profile_dir = COOKIES_DIR / args.account
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                str(profile_dir), channel="chrome", headless=headless, args=["--no-sandbox"],
            )
            log("실제 Google Chrome으로 실행")
        except Exception:
            # 폰(proot Ubuntu)처럼 시스템 Chrome이 없고 playwright 번들
            # Chromium만 있는 환경 — channel 지정 없이 기본 Chromium 사용.
            ctx = p.chromium.launch_persistent_context(
                str(profile_dir), headless=headless, args=["--no-sandbox"],
            )
            log("Google Chrome 없음 — playwright 번들 Chromium으로 실행")
        pg = ctx.new_page()
        pg.on("dialog", lambda d: d.accept())

        pg.goto(f"https://{args.slug}.tistory.com/manage", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(2000)
        logged_in = "auth/login" not in pg.url
        log(f"기존 세션으로 로그인 상태: {logged_in}")

        if not logged_in:
            if not args.password:
                log("로그인 필요한데 --password/PASSWORD 없음. 중단.")
                ctx.close()
                sys.exit(1)
            email = args.email or account_email(args.account)
            ok = run_login(pg, args.slug, email, args.password, args.adb_serial)
            if not ok:
                ctx.close()
                sys.exit(1)

        ok = inject_player(pg, args.slug, player_html)
        ctx.close()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
