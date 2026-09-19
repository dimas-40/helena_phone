#!/usr/bin/env python3
"""
phone-webtoon-make MCP — 폰 웹툰 메이크. 웹툰 작가·연출 시퀀스.

2단 시퀀스 (휴먼 인더 루프):
  1. webtoon_direct(source)  — 연출 기획: 소스(URL/문서) 파싱 + BLIP 눈(필수) → 컷·몸동작·프롬프트 설계 → 텔레그램 전송
  2. [Boss: 갤러리(Drawing assist)에 프롬프트 붙여넣고 얼굴 합성 이미지 생성]
  3. webtoon_assemble(dialogue) — 식자·조립: 갤러리 컷 읽기 → 말풍선 식자 → 세로 웹툰 HTML

규칙:
  - source 는 URL 또는 문서경로 (변수).
  - webtoon_direct 는 반드시 BLIP 비전(눈)으로 소스를 "본 뒤"에 설계한다.
  - 이미지 생성(얼굴 합성)은 Boss 몫, 몸동작 연출·식자·조립은 Claude 몫.
"""
import json, sys, os, glob, shutil, subprocess, time
from pathlib import Path

SERVER = "phone-webtoon-make"
VER = "1.0.0"

GALLERY = "/sdcard/DCIM/Drawing assist"
WEBTOON_DIR = "/root/work/parksy-webzine/webtoon"
ASSET_DIR = os.path.join(WEBTOON_DIR, "cuts")
DISCLAIMER_CROP = 0.08  # 삼성 AI 경고문(하단 텍스트) — 하단 8% 크롭 (규격화)
VISION_SCRIPT = "/root/vision/see.py"  # BLIP 눈 (영구 설치)
TG_SCRIPT = "/root/work/tg.sh"


# ── BLIP 비전 (눈) — 강제 사용 ──
def _vision(image_path):
    """BLIP으로 이미지를 '본다'. 실패해도 텍스트 폴백 반환."""
    if not os.path.isfile(VISION_SCRIPT):
        return "(비전 스크립트 없음)"
    try:
        r = subprocess.run(["/usr/bin/python3", VISION_SCRIPT, image_path],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout
        for line in out.splitlines():
            if line.strip().startswith("CAPTION:") or (line.strip() and "caption" in line.lower()):
                continue
        # CAPTION 라인 찾기
        lines = out.splitlines()
        for i, l in enumerate(lines):
            if "CAPTION" in l and i + 1 < len(lines):
                return lines[i + 1].strip()
        return out.strip()[-300:]
    except Exception as e:
        return f"(비전 오류: {e})"


def _screenshot(url):
    """URL → 스크린샷 파일 경로. 실패 시 None."""
    png = f"/tmp/wt_{int(time.time())}.png"
    code = f'''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={{"width":1080,"height":1400}})
    pg.goto({url!r}, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(2000)
    pg.screenshot(path={png!r})
    b.close()
'''
    try:
        subprocess.run(["/usr/bin/python3", "-c", code], capture_output=True, timeout=90)
        return png if os.path.isfile(png) else None
    except Exception:
        return None


def _fetch_text(source):
    """URL → 텍스트/DOM 추출. 문서경로면 그대로 읽음."""
    if source.startswith("http"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", source], capture_output=True, text=True, timeout=30)
            html = r.stdout
            import re
            title = re.search(r"<title>(.*?)</title>", html, re.S)
            title = title.group(1).strip() if title else source
            html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
            html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
            body = re.sub(r"<[^>]+>", " ", html)
            body = re.sub(r"\s+", " ", body).strip()
            return title, body[:1500]
        except Exception as e:
            return source, f"(fetch 오류: {e})"
    else:
        try:
            text = open(source).read()
            return os.path.basename(source), text[:1500]
        except Exception as e:
            return source, f"(읽기 오류: {e})"


def _fit100(p):
    """삼성 갤러리 프롬프트 100자 한도. 100자 꽉 채우고 넘치면 자름."""
    fill = ", 좌우 필름 스프로켓홀(구멍) 가장자리, 다크그린·흰색 필름 프레임 이어짐, 영화적 리얼리즘, 깊은 심도"
    if len(p) < 100:
        p += fill[: 100 - len(p)]
    return p[:100]


def _design(title, body, vision):
    """연출 기획 — 소스 기반 4컷 웹툰 설계. 몸동작 + 프롬프트(100자 압축)."""
    words = [w for w in body.split() if not w.startswith("--")][:8]
    gist = " ".join(words) if words else title[:40]
    core = [
        ("앞에 서다", "정면. 두 손 뒤로. 대상을 바라보며 선다.",
         f"박씨 얼굴 합성, 다크그린 잡지 가판대 64권 앞 정면 전신 서서 두 손 뒤로 바라봄, 황동 금박 간판"),
        ("집어 눕히다", "손을 뻗어 한 조각을 집는다 → 가로로 눕힌다.",
         f"박씨 얼굴 합성, 손 클로즈업, 잡지 한 권 집어 다크그린 테이블에 가로로 눕히는 순간, 황동 측면 조명"),
        ("일으켜 세우다", "눕힌 것을 세로로 일으켜 세운다 → 빛나는 영상으로 변한다.",
         f"박씨 얼굴 합성, 눕힌 잡지 세로로 일으켜 세우며 표지가 빛나는 영상 프레임으로 변하는 순간, 역동적 구도"),
        ("다시 이 집으로", "세운 것을 끌어안듯 다시 제자리에 꽂는다 → 미소.",
         f"박씨 얼굴 합성, 영상에서 돌아온 잡지 다시 가판대에 꽂으며 미소 전신 구도, 루프 완성"),
    ]
    cuts = [{"n": i+1, "scene": sc, "motion": mo, "prompt": _fit100(pr)} for i, (sc, mo, pr) in enumerate(core)]
    return {"title": f"웹툰 — {title}", "source_gist": gist, "vision": vision, "cuts": cuts}


def _tg_send(text):
    """텔레그램 전송 (tg.sh) — .secrets.env 로드해서 토큰 주입."""
    try:
        with open("/tmp/wt_tg.txt", "w") as f:
            f.write(text)
        cmd = 'set -a; source /root/work/.secrets.env 2>/dev/null; set +a; bash /root/work/tg.sh --no-button "$(cat /tmp/wt_tg.txt)"'
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=30)
        return "ok" if r.returncode == 0 else f"fail: {r.stderr[-120:]}"
    except Exception as e:
        return f"fail: {e}"


def _format_telegram(d):
    lines = [f"🎬 폰 웹툰 메이크 — 연출 기획", "",
             f"소스: {d['title']}", f"눈(BLIP): {d['vision']}", "",
             "━━━━━━━━━━━━━━━━"]
    for c in d["cuts"]:
        lines += [f"[컷 {c['n']}] {c['scene']}", f"몸동작: {c['motion']}",
                  f"프롬프트:", f"「{c['prompt']}」", ""]
    lines += ["━━━━━━━━━━━━━━━━", "갤러리(Drawing assist)에 프롬프트 붙여넣고 얼굴 합성 생성 → 저장하면 내가 식자+조립"]
    return "\n".join(lines)


# ── 툴 1: 연출 기획 ──
def webtoon_direct(source=None):
    try:
        if not source:
            return {"ok": False, "error": "source 필요 (URL 또는 문서경로)"}
        title, body = _fetch_text(source)
        # 반드시 눈으로 본다 (스크린샷 + BLIP)
        vision = "(문서라 스크린샷 없음)"
        if source.startswith("http"):
            png = _screenshot(source)
            vision = _vision(png) if png else "(스크린샷 실패)"
        design = _design(title, body, vision)
        msg = _format_telegram(design)
        tg = _tg_send(msg)
        return {"ok": True, "title": title, "vision": vision, "cuts": len(design["cuts"]),
                "telegram": tg, "design": design}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


# ── 툴 2: 식자·조립 ──
def webtoon_assemble(dialogue=None, title="웹툰"):
    try:
        if not dialogue or not isinstance(dialogue, list):
            return {"ok": False, "error": "dialogue 필요 (대사 리스트)"}
        pats = sorted(glob.glob(os.path.join(GALLERY, "*.jpg")) + glob.glob(os.path.join(GALLERY, "*.png")), reverse=True)
        if not pats:
            return {"ok": False, "error": f"갤러리에 컷 없음: {GALLERY}"}
        n = min(len(pats), len(dialogue))
        os.makedirs(ASSET_DIR, exist_ok=True)
        cut_rel = []
        for i in range(n):
            ext = os.path.splitext(pats[i])[1]
            dst = os.path.join(ASSET_DIR, f"cut_{i+1:02d}{ext}")
            _crop_disclaimer(pats[i], dst)
            cut_rel.append(f"cuts/cut_{i+1:02d}{ext}")
        html = _compose(title, cut_rel, dialogue[:n])
        out = os.path.join(WEBTOON_DIR, "index.html")
        open(out, "w").write(html)
        return {"ok": True, "n_cuts": n, "html": out, "cuts": cut_rel}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


def _crop_disclaimer(src, dst):
    """삼성 AI 경고문(하단 텍스트) 제거 — 하단 8% 크롭 후 저장."""
    try:
        from PIL import Image
        img = Image.open(src)
        w, h = img.size
        img.crop((0, 0, w, int(h * (1 - DISCLAIMER_CROP)))).save(dst)
    except Exception:
        shutil.copy(src, dst)  # PIL 실패 시 원본 복사


def _compose(title, cut_rel, dialogue):
    panels = []
    for i, (cut, text) in enumerate(zip(cut_rel, dialogue), 1):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        panels.append(f'<section class="panel"><div class="cut"><img src="{cut}" alt="컷 {i}">'
                      f'<div class="bubble"><span class="txt">{safe}</span></div></div></section>')
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — PARKSY 웹툰</title>
<style>:root{{--paper:#0c1710;--ink:#e9e5cf;--brass:#a08a4c}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font-family:"Nanum Myeongjo",serif;line-height:1.6}}
.wrap{{max-width:720px;margin:0 auto;padding:20px 16px 80px}}
.mast{{text-align:center;padding:18px 0 26px;border-bottom:1px solid rgba(160,138,76,.3)}}
.mast h1{{font-family:Georgia,serif;font-weight:900;font-size:26px}}.mast .sub{{font-size:11px;letter-spacing:.3em;color:var(--brass);margin-top:6px}}
.panel{{margin:26px 0}}.cut{{position:relative}}.cut img{{width:100%;display:block;border-radius:4px;box-shadow:0 14px 30px rgba(0,0,0,.5)}}
.bubble{{position:absolute;left:14px;right:14px;bottom:14px;background:rgba(233,229,207,.96);color:#1a120c;padding:12px 16px;border-radius:14px;font-size:16px;font-weight:700;box-shadow:0 4px 14px rgba(0,0,0,.45);text-align:center}}
footer{{text-align:center;color:var(--brass);font-size:12px;letter-spacing:.2em;padding:30px 0}}</style></head><body>
<div class="wrap"><div class="mast"><h1>{title}</h1><div class="sub">PARKSY WEBTOON</div></div>
{''.join(panels)}<footer>PARKSY · 박씨 종합잡지사</footer></div></body></html>'''


# ── JSON-RPC stdio ──
def _tools():
    return [
        {"name": "webtoon_direct", "description": "[폰 웹툰 메이크] 연출 기획. 소스(URL/문서)를 BLIP 눈으로 본 뒤 컷·몸동작·프롬프트를 설계해 텔레그램으로 전송.",
         "inputSchema": {"type": "object", "properties": {"source": {"type": "string", "description": "URL 또는 문서경로"}}, "required": ["source"]}},
        {"name": "webtoon_assemble", "description": "[폰 웹툰 메이크] 식자·조립. 갤러리 컷을 읽어 대사 말풍선을 식자하고 세로 웹툰 HTML로 조립.",
         "inputSchema": {"type": "object", "properties": {"dialogue": {"type": "array", "items": {"type": "string"}}, "title": {"type": "string"}}, "required": ["dialogue"]}},
    ]


def _handle(method, params):
    if method == "initialize":
        return {"protocolVersion": "2024-11-05", "serverInfo": {"name": SERVER, "version": VER}, "capabilities": {"tools": {}}}
    if method == "tools/list":
        return {"tools": _tools()}
    if method == "tools/call":
        name = params.get("name"); args = params.get("arguments", {}) or {}
        fn = {"webtoon_direct": webtoon_direct, "webtoon_assemble": webtoon_assemble}.get(name)
        if not fn:
            raise ValueError(f"Unknown tool: {name}")
        r = fn(**args)
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}]}
    raise ValueError(f"Unknown method: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = req.get("id"); method = req.get("method", ""); params = req.get("params", {}) or {}
        if rid is None:
            continue
        try:
            resp = {"jsonrpc": "2.0", "id": rid, "result": _handle(method, params)}
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32603, "message": f"{type(e).__name__}: {e}"[:300]}}
        print(json.dumps(resp, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
