#!/usr/bin/env python3
"""
tablet-webtoon MCP (구 parksy-gallery 개명) — 태블릿 웹툰: 삼성 그리기 어시스트
전자동 생성 + 웹툰 연출·조립 통합.

2026-09-13 통합판:
  A) 이미지 생성 로직 — 태블릿 최신본(uiautomator dump 동적탐색, 522줄/7툴)
     기준으로 좌표 하드코딩판(이 파일의 구버전, restyle_image가 photo_index
     고정좌표를 썼음)을 교체 + CLI(~/parksy-image/scripts/drawing_assist.py)
     에서 같은 날 실측 확정한 4개 수정 반영:
       1. 프롬프트 100자 하드리밋 실측 확정(한/영 동일 코드포인트) →
          compress_prompt(): 쉼표>공백>하드컷 순 자동 압축
       2. 한글 `adb shell input text` NullPointerException →
          ADBKeyboard IME + ADB_INPUT_TEXT broadcast 우회
       3. preflight_hard_reset() — 세로모드강제+절전해제+IME전환+앱재시작을
          모든 생성 호출 앞에 무조건 실행(옵션 없음)
       4. check_token_alive() — 삼성 SAccountTokenManager 토큰 만료(가장 흔한
          "자동화는 되는데 이미지가 안 나옴" 원인)를 logcat으로 감지
  B) 웹툰 연출·조립 — 폰 `phone-webtoon-make`(phone_webtoon_make_mcp.py)의
     webtoon_direct(BLIP눈+텔레그램)/webtoon_assemble(식자+HTML조립)을 이식.
     구판의 "소스 내용 무관 하드코딩 4컷" 버그를 소스 gist 반영 동적설계로 교체.
  C) 신설 webtoon_generate(cuts) — 폰이 설계한 컷을 이 태블릿에서 전자동으로
     직접 생성(restyle_image 반복 호출). 폰 레인이 "화면 뺏기지 않으려고"
     일부러 반자동(박씨가 직접 붙여넣기)으로 남겨뒀던 단계를 대체하는 옵션 —
     강제 아님, 박씨가 "자동으로 해" 라고 할 때만 씀.

트릴로지 위치: 박씨 티칭(parksy-teaching)·판서튜토리얼(po-tutorial)과 같은
"태블릿" 워크센터. 코드 위치는 parksy-image(WSL 원본) + 태블릿 로컬 사본
(/root/work/mcp-servers/) 양쪽 동기화 유지.

의존: 태블릿 ADB 연결(100.86.15.50:5900), ADBKeyboard 사전설치
     (com.android.adbkeyboard), Pillow(워터마크 크롭),
     프리셋(/sdcard/DCIM/박씨 갤러리/프리셋/parksy_30s.png 등)
결과: /sdcard/DCIM/박씨 갤러리/Drawing_assist_*.jpg
      웹툰 HTML: ~/parksy-webzine/webtoon/index.html
"""
import glob
import os
import re
import shutil
import subprocess
import time

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tablet-webtoon")  # 태블릿 웹툰 (구 parksy-gallery)

TAB = "100.86.15.50:5900"
PKG = "com.samsung.android.app.sketchbook"
ACT = "com.samsung.android.app.sketchbook.application.DrawingActivity"
ADB_IME = "com.android.adbkeyboard/.AdbIME"

# 2026-09-13 실측 확정 — 삼성 그리기 어시스트 프롬프트 입력창 하드 리밋.
# 한/영 동일 (코드포인트 기준). 이 값 넘으면 삼성 EditText가 조용히 잘라버림.
PROMPT_MAX_CHARS = 100

STYLES = {
    "아르 누보": (273, 357), "아르누보": (273, 357),
    "웹툰": (624, 357),
    "소프트 일러스트": (975, 357),
    "인스타툰": (1326, 357),
    "수채화": (273, 625),
    "일러스트": (624, 625),
    "팝아트": (975, 625),
    "스케치": (1326, 625),
    "3D 카툰": (273, 893), "3D카툰": (273, 893),
    "유화": (624, 893),
}

STYLE_USE = {
    "아르 누보": "기본값 (전체 기본)",
    "일러스트": "매뉴얼·설명서",
    "스케치": "실사 (사진 업로드 베이스)",
    "소프트 일러스트": "캐릭터 추출 (배경 없음 → 누끼)",
    "웹툰": "웹툰",
    "수채화": "삽화 (문학 작품 등)",
    "팝아트": "포스터·일본 잡지 느낌",
    "3D 카툰": "픽사 느낌",
    "유화": "유화",
    "인스타툰": "❌ 사용 안 함 (버림)",
}

SUGGEST = {
    "기본": "아르 누보", "아르누보": "아르 누보",
    "매뉴얼": "일러스트", "설명서": "일러스트",
    "실사": "스케치", "사진": "스케치", "리얼": "스케치",
    "캐릭터": "소프트 일러스트", "누끼": "소프트 일러스트", "추출": "소프트 일러스트",
    "삽화": "수채화", "문학": "수채화",
    "포스터": "팝아트", "잡지": "팝아트",
    "픽사": "3D 카툰", "3d": "3D 카툰", "3D": "3D 카툰",
    "웹툰": "웹툰", "만화": "웹툰",
}

NEW = (1443, 119)
TEXT_INPUT = (500, 1896)
VIEW_ALL = (1287, 2114)
GENERATE = (800, 2276)
SAVE = (851, 270)
PHOTO_ATTACH = (242, 1897)

DEFAULT_SOURCE = "parksy_30s.png"

GALLERY_DIR = "/sdcard/DCIM/박씨 갤러리"
DRAWING_DIR = "/sdcard/DCIM/Drawing assist"
PRESET_DIR = GALLERY_DIR + "/프리셋"
STAGE_DIR = "/sdcard/Pictures/parksy_stage"
STAGE_ALBUM_NAME = "parksy_stage"

_DUMP_REMOTE = "/sdcard/_pw_dump.xml"
_DUMP_LOCAL = "/tmp/_pw_dump.xml"

WEBTOON_DIR = os.path.expanduser("~/parksy-webzine/webtoon")
ASSET_DIR = os.path.join(WEBTOON_DIR, "cuts")
VISION_SCRIPT = "/root/vision/see.py"  # BLIP 눈 — 이 기기엔 없을 수 있음, 없으면 폴백
TG_SCRIPT = os.path.expanduser("~/work/tg.sh")


# ── ADB 저수준 ──────────────────────────────────────────────────────────────

def _adb(*args):
    return subprocess.run(["adb", "-s", TAB, *args], capture_output=True, text=True, timeout=60)


def _tap(x, y):
    _adb("shell", "input", "tap", str(x), str(y))


def _dump_ui() -> str:
    _adb("shell", "uiautomator", "dump", _DUMP_REMOTE)
    r = _adb("pull", _DUMP_REMOTE, _DUMP_LOCAL)
    if r.returncode != 0:
        return ""
    try:
        with open(_DUMP_LOCAL, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _node_center(xml_text: str, text: str, resource_id: str = None):
    for m in re.finditer(r"<node ([^>]*?)/?>", xml_text):
        attrs = m.group(1)
        if f'text="{text}"' not in attrs:
            continue
        if resource_id and f'resource-id="{resource_id}"' not in attrs:
            continue
        b = re.search(r'bounds="(\[[0-9,\[\]]+\])"', attrs)
        if not b:
            continue
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", b.group(1)))
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def _first_thumbnail(xml_text: str):
    best = None
    for m in re.finditer(r"<node ([^>]*?)/?>", xml_text):
        attrs = m.group(1)
        cls_m = re.search(r'class="([^"]*)"', attrs)
        if not cls_m or "ImageView" not in cls_m.group(1):
            continue
        b = re.search(r'bounds="(\[[0-9,\[\]]+\])"', attrs)
        if not b:
            continue
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", b.group(1)))
        if best is None or (y1, x1) < (best[1], best[0]):
            best = (x1, y1, x2, y2)
    if best is None:
        return None
    x1, y1, x2, y2 = best
    return ((x1 + x2) // 2, (y1 + y2) // 2)


# ── 압축·입력·프리플라이트·토큰체크 (2026-09-13 실측 확정 로직) ──────────────

def compress_prompt(prompt: str, max_chars: int = PROMPT_MAX_CHARS) -> str:
    """삼성 100자 한도에 맞춰 프롬프트를 압축한다 (실측 확정: 한/영 동일 100자).

    쉼표 경계 > 공백(단어) 경계 > 하드컷 순으로 시도. 말줄임표는 안 붙인다
    (그 글자수만큼 원문이 더 잘려나가는 손해가 더 큼 — 삼성이 알아서 자른다).
    """
    prompt = prompt.strip()
    if len(prompt) <= max_chars:
        return prompt
    truncated = prompt[:max_chars]
    last_comma = truncated.rfind(",")
    if last_comma > max_chars * 0.5:
        return truncated[:last_comma].strip()
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.5:
        return truncated[:last_space].strip()
    return truncated


def _input_text_unicode(text: str):
    """한글 포함 유니코드 텍스트를 ADBKeyboard broadcast로 입력한다.

    `adb shell input text`는 한글에 NullPointerException(Android 셸 키맵 한계,
    영어는 정상). ADBKeyboard로 IME 전환 후 ADB_INPUT_TEXT 브로드캐스트 사용.
    로컬+원격 이중 따옴표 필수 — 안 하면 공백에서 인자가 쪼개짐(실측 확인).
    """
    _adb("shell", "ime", "enable", ADB_IME)
    _adb("shell", "ime", "set", ADB_IME)
    time.sleep(0.5)
    escaped = text.replace("'", "'\\''")
    _adb("shell", f"am broadcast -a ADB_INPUT_TEXT --es msg '{escaped}'")


def check_token_alive() -> dict:
    """삼성 계정(SAccountTokenManager) 액세스 토큰 생존 여부를 logcat으로 확인.

    토큰 만료 시 `Token length : 0`으로 찍히고 생성 요청은 에러 팝업도 없이
    조용히 실패한다(2026-09-13 실측 확정 — 가장 흔한 실패 원인). 재부팅하면
    재발급됨(길이 25로 정상화 실측). ADB로는 복구 불가 — 재부팅만이 해법.
    """
    r = subprocess.run(
        ["adb", "-s", TAB, "logcat", "-d", "-s", "SketchBook:I"],
        capture_output=True, text=True, timeout=30
    )
    lines = [l for l in r.stdout.splitlines() if "SAccountTokenManager" in l and "Token length" in l]
    if not lines:
        return {"checked": False, "reason": "로그에 토큰 발급 기록 없음 (앱을 아직 안 띄웠을 수 있음)"}
    last = lines[-1]
    m = re.search(r"Token length\s*:\s*(\d+)", last)
    length = int(m.group(1)) if m else -1
    alive = length > 0
    return {
        "checked": True, "alive": alive, "token_length": length, "raw": last.strip(),
        "advice": None if alive else "토큰 길이 0 — 태블릿 재부팅 필요 (삼성 서버 세션 만료, ADB로 복구 불가)",
    }


def preflight_hard_reset():
    """모든 생성 호출 전 무조건 강제 실행 — 옵션으로 끌 수 없음(박씨 지시).

    세로모드 강제(가로면 좌표 전부 어긋남) → 절전 해제(커버닫힘 등으로
    Dozing 고착 시 WAKEUP 키만으론 안 깨어남, svc power stayon 필수) →
    ADBKeyboard 전환(한글 입력 사전 준비) → 앱 강제 재시작(잔여 상태 제거).
    """
    _adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
    _adb("shell", "settings", "put", "system", "user_rotation", "0")
    _adb("shell", "svc", "power", "stayon", "true")
    _adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
    _adb("shell", "ime", "enable", ADB_IME)
    _adb("shell", "ime", "set", ADB_IME)
    time.sleep(0.5)
    _adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    _adb("shell", "am", "start", "-n", f"{PKG}/{ACT}")
    time.sleep(4)


def _stage_preset_for_picker(source: str):
    preset_path = f"{PRESET_DIR}/{source}"
    existing_path = f"{GALLERY_DIR}/{source}"
    r = _adb("shell",
             f"if [ -f '{preset_path}' ]; then echo PRESET; "
             f"elif [ -f '{existing_path}' ]; then echo EXISTING; "
             f"else echo NONE; fi")
    kind = r.stdout.strip()
    if kind == "NONE":
        return None
    src = preset_path if kind == "PRESET" else existing_path
    _adb("shell", f"mkdir -p '{STAGE_DIR}'")
    _adb("shell", f"rm -f '{STAGE_DIR}'/*")
    dst = f"{STAGE_DIR}/stage.jpg"
    _adb("shell", f"cp '{src}' '{dst}'")
    _adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
         "-d", "file://" + dst)
    time.sleep(1)
    return dst


def _move_latest_to_gallery():
    _adb("shell", "mkdir", "-p", GALLERY_DIR)
    script = (
        f"latest=$(ls -t '{DRAWING_DIR}/'Drawing_assist_*.jpg 2>/dev/null | head -1); "
        f"if [ -n \"$latest\" ]; then mv \"$latest\" '{GALLERY_DIR}/'; fi; "
        f"echo \"$latest\""
    )
    r = _adb("shell", script)
    moved = r.stdout.strip()
    _adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
         "-d", "file://" + GALLERY_DIR)
    if not moved:
        return None
    return GALLERY_DIR + "/" + moved.split("/")[-1]


def _crop_bottom_watermark(path: str, crop_bottom: float = 8.0) -> str:
    from PIL import Image

    local = "/tmp/pg_crop.jpg"
    if os.path.isdir(local):
        shutil.rmtree(local, ignore_errors=True)
    elif os.path.isfile(local):
        os.remove(local)
    subprocess.run(["adb", "-s", TAB, "pull", path, local], capture_output=True, text=True, timeout=60)
    if not os.path.isfile(local):
        return path
    im = Image.open(local)
    w, h = im.size
    new_h = int(h * (1.0 - crop_bottom / 100.0))
    im.crop((0, 0, w, new_h)).save(local, quality=95)
    subprocess.run(["adb", "-s", TAB, "push", local, path], capture_output=True, text=True, timeout=60)
    return path


# ── 툴: 생성 (제너레이트 / 리스타일) ──────────────────────────────────────

@mcp.tool()
def generate_image(prompt: str, style: str = "아르 누보", wait: int = 20, crop_bottom: float = 8.0) -> dict:
    """프롬프트로 이미지를 생성해 갤러리(박씨 갤러리)에 저장한다. 100자 초과시 자동 압축.

    프리플라이트(세로고정/절전해제/한글IME전환/앱재시작)를 무조건 먼저 실행하고,
    저장 직전 삼성 서버 토큰 생존을 확인해 만료 시 재부팅 필요를 명확히 알린다.
    """
    if style not in STYLES:
        return {"ok": False, "error": f"지원하지 않는 스타일: {style}", "styles": list(STYLES)}

    original_prompt = prompt
    prompt = compress_prompt(prompt)
    compressed = prompt != original_prompt

    preflight_hard_reset()
    _tap(*NEW)
    time.sleep(2)
    _tap(*TEXT_INPUT)
    time.sleep(1.2)
    _input_text_unicode(prompt)
    time.sleep(1.2)
    _adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(1.5)
    _tap(*VIEW_ALL)
    time.sleep(2.0)
    _tap(*STYLES[style])
    time.sleep(1.5)
    _tap(*GENERATE)
    time.sleep(wait)

    token_status = check_token_alive()
    if token_status.get("checked") and not token_status.get("alive"):
        return {"ok": False, "error": "삼성 계정 토큰 만료 — 태블릿 재부팅 필요",
                "token_status": token_status, "prompt": prompt}

    _tap(*SAVE)
    time.sleep(4)
    path = _move_latest_to_gallery()
    if path is None:
        return {"ok": False, "error": "생성 실패 — 새 이미지가 저장되지 않음",
                "prompt": prompt, "style": style, "token_status": token_status}
    if crop_bottom > 0:
        path = _crop_bottom_watermark(path, crop_bottom)

    return {"ok": True, "prompt": prompt, "prompt_compressed": compressed,
            "original_prompt": original_prompt if compressed else None,
            "style": style, "path": path, "cropped": crop_bottom > 0}


@mcp.tool()
def restyle_image(source: str = DEFAULT_SOURCE, style: str = "아르 누보", prompt: str = "",
                  wait: int = 20, crop_bottom: float = 8.0) -> dict:
    """박씨 고정 프리셋(기본 parksy_30s, 전신크롭)을 업로드해 배경/화풍만 바꾼다.

    2026-09-13: 구판(photo_index 고정좌표)을 폐기하고 uiautomator dump 동적
    탐색으로 교체 — 삼성 갤러리 UI가 좌표 고정으로는 못 버틴다(실측 확인).
    source를 안 넘기면 항상 po-deepfake MCP와 동일한 고정 프리셋을 써서
    웹툰 컷마다 인물이 흔들리지 않게 한다.
    """
    if style not in STYLES:
        return {"ok": False, "error": f"지원하지 않는 스타일: {style}", "styles": list(STYLES)}

    original_prompt = prompt
    prompt = compress_prompt(prompt) if prompt else prompt
    compressed = bool(prompt) and prompt != original_prompt

    preflight_hard_reset()

    staged = _stage_preset_for_picker(source)
    if staged is None:
        return {"ok": False, "error": f"소스 파일을 못 찾음: {source} (프리셋/박씨갤러리 둘 다 없음)"}

    _tap(*PHOTO_ATTACH)
    time.sleep(2.5)

    xml = _dump_ui()
    album_tab = _node_center(xml, "앨범", resource_id="com.sec.android.gallery3d:id/title")
    if album_tab is None:
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": "사진피커에서 '앨범' 탭을 못 찾음 (uiautomator dump 실패)"}
    _tap(*album_tab)
    time.sleep(2)

    xml = _dump_ui()
    stage_album = _node_center(xml, STAGE_ALBUM_NAME, resource_id="com.sec.android.gallery3d:id/title")
    if stage_album is None:
        view_all = _node_center(xml, "모두 보기", resource_id="com.sec.android.gallery3d:id/view_all")
        if view_all is not None:
            _tap(*view_all)
            time.sleep(2)
            xml = _dump_ui()
            stage_album = _node_center(xml, STAGE_ALBUM_NAME, resource_id="com.sec.android.gallery3d:id/title")
    if stage_album is None:
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": f"앨범 목록에서 '{STAGE_ALBUM_NAME}'을 못 찾음 (미디어스캔 지연 가능)"}
    _tap(*stage_album)
    time.sleep(2)

    xml = _dump_ui()
    pos = _first_thumbnail(xml)
    if pos is None:
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": "parksy_stage 앨범 안에서 썸네일을 못 찾음"}
    _tap(*pos)
    time.sleep(3)

    if prompt:
        xml = _dump_ui()
        edit_tab = _node_center(xml, "", resource_id="com.samsung.android.app.sketchbook:id/text_thumbnail_view")
        _tap(*(edit_tab or (917, 1896)))
        time.sleep(1.5)
        for _ in range(PROMPT_MAX_CHARS + 10):
            _adb("shell", "input", "keyevent", "KEYCODE_DEL")
        _input_text_unicode(prompt)
        time.sleep(1)
        _adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(1.5)

    _tap(*VIEW_ALL)
    time.sleep(2)
    _tap(*STYLES[style])
    time.sleep(1.5)
    _tap(*GENERATE)
    time.sleep(wait)

    token_status = check_token_alive()
    if token_status.get("checked") and not token_status.get("alive"):
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": "삼성 계정 토큰 만료 — 태블릿 재부팅 필요",
                "token_status": token_status, "source": source, "prompt": prompt}

    _tap(*SAVE)
    time.sleep(4)
    path = _move_latest_to_gallery()
    _adb("shell", f"rm -f '{staged}'")
    if path is None:
        return {"ok": False, "error": "생성 실패 — 새 이미지가 저장되지 않음",
                "source": source, "token_status": token_status}
    if crop_bottom > 0:
        path = _crop_bottom_watermark(path, crop_bottom)

    return {"ok": True, "style": style, "source": source, "prompt": prompt,
            "prompt_compressed": compressed,
            "original_prompt": original_prompt if compressed else None,
            "path": path, "cropped": crop_bottom > 0}


@mcp.tool()
def extract_character(prompt: str, wait: int = 20, crop_bottom: float = 0.0) -> dict:
    """누끼(캐릭터 추출) — '소프트 일러스트' 스타일(배경 없음)로 생성."""
    return generate_image(prompt=prompt, style="소프트 일러스트", wait=wait, crop_bottom=crop_bottom)


@mcp.tool()
def check_token() -> dict:
    """삼성 계정 토큰 생존 여부만 확인한다 (이미지 생성 안 함). 자동화가 안 될 때 먼저 이걸로 진단."""
    return check_token_alive()


@mcp.tool()
def list_styles() -> dict:
    """지원 스타일 목록 + 용도 매뉴얼 + 프롬프트 글자수 한도를 반환한다."""
    return {"styles": STYLE_USE, "default": "아르 누보", "prompt_max_chars": PROMPT_MAX_CHARS}


@mcp.tool()
def suggest_style(need: str) -> dict:
    """용도(예: '포스터', '삽화', '실사', '캐릭터')를 보고 스타일을 역제안한다."""
    nl = need.strip().lower()
    for k, v in SUGGEST.items():
        if k in nl or nl in k:
            return {"need": need, "style": v, "use": STYLE_USE.get(v, "")}
    return {"need": need, "style": "아르 누보", "use": "기본값", "fallback": True}


@mcp.tool()
def list_presets() -> dict:
    """박씨 갤러리 프리셋 사진 목록(합성/재스타일용 참조 사진)을 반환한다.

    ⚠️ 이 폴더에 실물 신분증 등 민감사진이 섞여있던 사례가 있었음(2026-08-30).
    """
    r = _adb("shell", f"ls '{PRESET_DIR}/'")
    files = [f for f in r.stdout.strip().split("\n") if f]
    return {"preset_dir": PRESET_DIR, "count": len(files), "presets": files}


# ── 웹툰 연출·조립 (폰 phone-webtoon-make 이식 + 동적 설계로 교체) ──────────

def _fetch_text(source):
    if source.startswith("http"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", source], capture_output=True, text=True, timeout=30)
            html = r.stdout
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


def _screenshot(url):
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
        subprocess.run(["python3", "-c", code], capture_output=True, timeout=90)
        return png if os.path.isfile(png) else None
    except Exception:
        return None


def _vision(image_path):
    """BLIP으로 이미지를 '본다'. 이 기기엔 없을 수 있음 — 실패해도 텍스트 폴백."""
    if not image_path or not os.path.isfile(VISION_SCRIPT):
        return "(비전 스크립트 없음 — 이 기기엔 BLIP 미설치)"
    try:
        r = subprocess.run(["python3", VISION_SCRIPT, image_path],
                           capture_output=True, text=True, timeout=120)
        lines = r.stdout.splitlines()
        for i, l in enumerate(lines):
            if "CAPTION" in l and i + 1 < len(lines):
                return lines[i + 1].strip()
        return r.stdout.strip()[-300:]
    except Exception as e:
        return f"(비전 오류: {e})"


def _design_dynamic(title, body, vision):
    """소스 내용을 반영한 4컷 연출 설계.

    구판(phone_webtoon_make_mcp.py)의 버그: gist를 계산만 하고 프롬프트엔
    한 글자도 안 씀 — 소스가 뭐든 컷 4개가 완전히 동일했음(2026-09-13 발견).
    이 버전은 hook/gist를 실제 프롬프트 문자열에 삽입한다.
    """
    words = [w.strip(".,!?") for w in body.split() if len(w) > 1][:12]
    gist = " ".join(words[:6]) if words else title[:40]
    hook = words[0] if words else "이야기"

    core = [
        ("앞에 서다", "정면. 두 손 뒤로. 대상을 바라보며 선다.",
         f"박씨 얼굴 합성, {hook} 주제 배경 앞 정면 전신, 두 손 뒤로 바라봄, 다크그린 황동 조명"),
        ("집어 눕히다", "손을 뻗어 핵심을 집는다 → 눕힌다.",
         f"박씨 얼굴 합성, 손 클로즈업, {gist} 관련 오브제를 테이블에 눕히는 순간, 측면 조명"),
        ("일으켜 세우다", "눕힌 것을 세운다 → 빛나는 결과로 변한다.",
         f"박씨 얼굴 합성, {hook} 오브제 세로로 세우며 빛나는 프레임으로 변하는 순간, 역동 구도"),
        ("돌아오다", "완성된 것을 끌어안듯 제자리로.",
         f"박씨 얼굴 합성, {gist} 완성물 안고 돌아와 미소, 전신 구도, 루프 완성"),
    ]
    cuts = [{"n": i + 1, "scene": sc, "motion": mo, "prompt": compress_prompt(pr)}
            for i, (sc, mo, pr) in enumerate(core)]
    return {"title": f"웹툰 — {title}", "source_gist": gist, "vision": vision, "cuts": cuts}


def _tg_send(text):
    try:
        with open("/tmp/wt_tg.txt", "w") as f:
            f.write(text)
        cmd = f'set -a; source {os.path.dirname(TG_SCRIPT)}/.secrets.env 2>/dev/null; set +a; bash {TG_SCRIPT} --no-button "$(cat /tmp/wt_tg.txt)"'
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=30)
        return "ok" if r.returncode == 0 else f"fail: {r.stderr[-120:]}"
    except Exception as e:
        return f"fail: {e}"


def _format_telegram(d, auto_available: bool):
    lines = [f"🎬 태블릿 웹툰 — 연출 기획", "", f"소스: {d['title']}", f"눈(BLIP): {d['vision']}", "",
             "━━━━━━━━━━━━━━━━"]
    for c in d["cuts"]:
        lines += [f"[컷 {c['n']}] {c['scene']}", f"몸동작: {c['motion']}", f"프롬프트:", f"「{c['prompt']}」", ""]
    lines += ["━━━━━━━━━━━━━━━━"]
    if auto_available:
        lines += ["'자동으로 해' 라고 하면 이 컷 그대로 태블릿에서 전자동 생성 (화면 잠깐 뺏김).",
                  "직접 하고 싶으면 갤러리(Drawing assist)에 프롬프트 붙여넣고 생성 후 조립 요청."]
    else:
        lines += ["갤러리(Drawing assist)에 프롬프트 붙여넣고 얼굴 합성 생성 → 저장하면 식자+조립"]
    return "\n".join(lines)


@mcp.tool()
def webtoon_direct(source: str) -> dict:
    """연출 기획 — 소스(URL/문서)를 BLIP 눈으로 본 뒤 4컷 설계(소스 내용 반영) → 텔레그램 전송.

    이후 두 갈래: (1) webtoon_generate 로 이 태블릿에서 바로 전자동 생성
    (2) 박씨가 직접 갤러리에 붙여넣고 생성(반자동, 화면 안 뺏김) — 둘 다 가능,
    강요하지 않는다. 어느 쪽이든 끝나면 webtoon_assemble 로 조립.
    """
    try:
        title, body = _fetch_text(source)
        vision = "(문서라 스크린샷 없음)"
        if source.startswith("http"):
            png = _screenshot(source)
            vision = _vision(png) if png else "(스크린샷 실패)"
        design = _design_dynamic(title, body, vision)
        msg = _format_telegram(design, auto_available=True)
        tg = _tg_send(msg)
        return {"ok": True, "title": title, "vision": vision, "cuts": design["cuts"],
                "telegram": tg, "design": design}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


@mcp.tool()
def webtoon_generate(cuts: list) -> dict:
    """webtoon_direct가 설계한 컷들을 이 태블릿에서 전자동으로 직접 생성한다.

    화면이 몇 분간 자동으로 움직인다(박씨가 그 시간 태블릿을 다른 용도로
    쓰려던 참이면 부르지 말 것 — 강제 아님, 옵션). 컷마다 restyle_image를
    고정 프리셋(parksy_30s.png)으로 순차 호출.

    Args:
        cuts: [{"prompt": "...", "style": "아르 누보"(생략시 기본)}, ...]
    """
    results = []
    for i, c in enumerate(cuts):
        prompt = c.get("prompt", "")
        style = c.get("style", "아르 누보")
        r = restyle_image(source=DEFAULT_SOURCE, style=style, prompt=prompt, wait=20)
        results.append({"cut": i + 1, "ok": r.get("ok"), "path": r.get("path"), "error": r.get("error")})
        if not r.get("ok") and r.get("token_status", {}).get("checked") and not r["token_status"].get("alive"):
            return {"ok": False, "error": "토큰 만료로 중단 — 태블릿 재부팅 필요",
                    "done": results, "remaining": len(cuts) - len(results)}
    return {"ok": all(x["ok"] for x in results), "n_cuts": len(results), "results": results}


def _crop_disclaimer(src, dst):
    try:
        from PIL import Image
        img = Image.open(src)
        w, h = img.size
        img.crop((0, 0, w, int(h * (1 - 0.08)))).save(dst)
    except Exception:
        shutil.copy(src, dst)


def _compose(title, cut_rel, dialogue):
    panels = []
    for i, (cut, text) in enumerate(zip(cut_rel, dialogue), 1):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        panels.append(f'<section class="panel"><div class="cut"><img src="{cut}" alt="컷 {i}"></div>'
                      f'<div class="bubble"><span class="txt">{safe}</span></div></section>')
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — PARKSY 웹툰</title>
<style>:root{{--paper:#0c1710;--ink:#e9e5cf;--brass:#a08a4c}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font-family:"Nanum Myeongjo",serif;line-height:1.6}}
.wrap{{max-width:720px;margin:0 auto;padding:20px 16px 80px}}
.mast{{text-align:center;padding:18px 0 26px;border-bottom:1px solid rgba(160,138,76,.3)}}
.mast h1{{font-family:Georgia,serif;font-weight:900;font-size:26px}}.mast .sub{{font-size:11px;letter-spacing:.3em;color:var(--brass);margin-top:6px}}
.panel{{margin:26px 0}}.cut img{{width:100%;display:block;border-radius:4px;box-shadow:0 14px 30px rgba(0,0,0,.5)}}
.bubble{{position:relative;background:var(--ink);color:#1a120c;padding:12px 16px;margin:18px 12px 0;border-radius:14px;font-size:16px;font-weight:700}}
.bubble::before{{content:"";position:absolute;top:-9px;left:32px;width:18px;height:18px;background:var(--ink);border-radius:0 0 4px 0;transform:rotate(45deg)}}
footer{{text-align:center;color:var(--brass);font-size:12px;letter-spacing:.2em;padding:30px 0}}</style></head><body>
<div class="wrap"><div class="mast"><h1>{title}</h1><div class="sub">PARKSY WEBTOON</div></div>
{''.join(panels)}<footer>PARKSY · 박씨 종합잡지사</footer></div></body></html>'''


@mcp.tool()
def webtoon_assemble(dialogue: list, title: str = "웹툰") -> dict:
    """식자·조립 — 갤러리 최신 컷을 읽어 말풍선을 식자하고 세로 웹툰 HTML로 조립한다."""
    try:
        if not dialogue or not isinstance(dialogue, list):
            return {"ok": False, "error": "dialogue 필요 (대사 리스트)"}
        pats = sorted(glob.glob(os.path.join(GALLERY_DIR, "*.jpg")) + glob.glob(os.path.join(GALLERY_DIR, "*.png")), reverse=True)
        if not pats:
            return {"ok": False, "error": f"갤러리에 컷 없음: {GALLERY_DIR}"}
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
        os.makedirs(WEBTOON_DIR, exist_ok=True)
        open(out, "w").write(html)
        return {"ok": True, "n_cuts": n, "html": out, "cuts": cut_rel}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


if __name__ == "__main__":
    mcp.run()
