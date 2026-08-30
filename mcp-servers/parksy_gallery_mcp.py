#!/usr/bin/env python3
"""
박씨 갤러리 MCP 서버 — 삼성 그리기 어시스트(Creative Studio) 텍스트→이미지→저장

툴:
  generate_image(prompt, style)  — 프롬프트로 이미지 생성 + 갤러리 저장 (스타일 10종)
  restyle_image(source, style, prompt) — 프리셋/기존 사진 업로드해 재스타일·합성
  list_styles()                  — 지원 스타일 목록

의존: 태블릿 ADB 연결 (100.86.15.50:5900)
결과: /sdcard/DCIM/Drawing assist/Drawing_assist_*.jpg

2026-08-30 restyle_image 재작성 (좌표 하드코딩 → uiautomator dump 동적 탐색):
  실측으로 확인한 원인 4가지 —
  1) "스타일 변경" 진입 시 열리는 시스템 사진피커는 기본이 "사진"(전체, 최신순) 탭이라
     구버전처럼 "앨범→박씨 갤러리→고정좌표" 방식은 엉뚱한 썸네일을 찍음.
  2) "박씨 갤러리"라는 이름의 앨범이 앨범탭에 있지만 이건 실제 폴더 전체가 아니라
     MediaStore가 이전에 캐싱해둔 부분집합(4장)이라 새로 넣은 프리셋이 안 잡힘.
  3) 삼성 갤러리의 "사진"(전체 타임라인) 탭은 EXIF/date_modified가 없는 파일을
     Drawing_assist_YYYYMMDD_HHMMSS.jpg 같은 파일명 패턴에서 날짜를 파싱해 배치한다
     — 그 패턴이 아닌 파일은 타임라인에서 실종된다. 파일명 패턴을 맞춰도 "오늘" 섹션은
     이 태블릿에서 도는 다른 자동화(인스타/발행 등)가 그날 찍은 스크린샷과 계속 경합해서
     여전히 불안정하다(실측 확인 — 신뢰 불가).
  4) 해법: /sdcard/Pictures/parksy_stage/ 라는 이 파이프라인 전용 격리 폴더를 만들어
     대상 사진 한 장만 그 안에 둔다 — 그럼 "앨범" 탭에 "parksy_stage"라는 이름의,
     정확히 그 한 장만 들어있는 앨범이 뜬다(실측 확인). 매번 uiautomator dump로
     "앨범" 탭 → parksy_stage 앨범 → 그 안의 유일한 썸네일을 실시간으로 찾아서 탭한다
     (좌표 고정 대신 텍스트 매칭으로 위치를 매번 다시 계산 — 다른 자동화의 스크린샷과
     절대 안 겹침).
"""
import re
import subprocess
import time

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("parksy-gallery")  # 박씨 갤러리

TAB = "100.86.15.50:5900"
PKG = "com.samsung.android.app.sketchbook"
ACT = "com.samsung.android.app.sketchbook.application.DrawingActivity"

# 스타일 → 좌표 (태블릿 1600x2560 기준, "모두 보기" 전체 스타일 그리드 좌표)
# 그리드: 4열 × 3행, "스타일" 시트에서 uiautomator로 검증됨
STYLES = {
    # 1행
    "아르 누보": (273, 357),
    "아르누보": (273, 357),
    "웹툰": (624, 357),
    "소프트 일러스트": (975, 357),
    "인스타툰": (1326, 357),
    # 2행
    "수채화": (273, 625),
    "일러스트": (624, 625),
    "팝아트": (975, 625),
    "스케치": (1326, 625),
    # 3행
    "3D 카툰": (273, 893),
    "3D카툰": (273, 893),
    "유화": (624, 893),
}

# 스타일 사용 매뉴얼 (Boss 지정) — 용도 → 스타일 역제안용
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

# 좌표 상수 (앱 자체 UI — generate_image에서 실측 검증됨, 그대로 유지)
NEW = (1443, 119)         # "새로 작성" (앱 리셋)
TEXT_INPUT = (500, 1896)  # 텍스트 입력창
VIEW_ALL = (1287, 2114)   # "모두 보기" (전체 스타일 그리드 열기)
GENERATE = (800, 2275)    # "생성" 버튼
SAVE = (851, 270)         # "저장" 버튼 (생성 완료 후 상단)
PHOTO_ATTACH = (242, 1897)  # "스타일 변경" 진입 (사진 첨부 아이콘)

# 박씨 고정 프리셋 — po-deepfake MCP(FACE_LIBRARY)와 동일한 소스(parksy_30s, 전신크롭)를
# 여기서도 기본값으로 씀. 웹툰 컷마다 다른 얼굴로 흔들리는 것 방지 (2026-08-30 확정).
DEFAULT_SOURCE = "parksy_30s.png"

# 갤러리 경로
GALLERY_DIR = "/sdcard/DCIM/박씨 갤러리"    # 박씨 갤러리 전용 폴더
DRAWING_DIR = "/sdcard/DCIM/Drawing assist"  # 앱 기본 저장 폴더
PRESET_DIR = GALLERY_DIR + "/프리셋"          # 얼굴/가족 등 참조 사진
STAGE_DIR = "/sdcard/Pictures/parksy_stage"   # restyle_image 전용 격리 스테이징 폴더
STAGE_ALBUM_NAME = "parksy_stage"             # 사진피커 앨범탭에 뜨는 이름 (폴더명과 동일)

_DUMP_REMOTE = "/sdcard/_pw_dump.xml"
_DUMP_LOCAL = "/tmp/_pw_dump.xml"


def _adb(*args):
    return subprocess.run(
        ["adb", "-s", TAB, *args], capture_output=True, text=True, timeout=60
    )


def _tap(x, y):
    _adb("shell", "input", "tap", str(x), str(y))


def _dump_ui() -> str:
    """현재 화면의 uiautomator XML을 받아온다 (좌표 하드코딩 대신 실시간 탐색용)."""
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
    """text(정확히 일치, 필요시 resource_id도)로 노드를 찾아 중심좌표를 반환."""
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
    """화면에 있는 이미지 썸네일 중 가장 위·왼쪽 것의 중심좌표.

    삼성 사진피커는 RecyclerView 항목에 clickable=true를 안 붙여놓는 경우가 많아
    (실측 확인됨) 텍스트/좌표 기준 탐색이 유일하게 신뢰 가능한 방법이다.
    """
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


def _stage_preset_for_picker(source: str):
    """프리셋(또는 박씨 갤러리 안의 기존 파일)을 전용 격리 폴더(STAGE_DIR)에 딱 한 장만 둔다.

    이 태블릿엔 다른 자동화(인스타/발행 등)가 남기는 스크린샷이 계속 쌓이기 때문에
    "오늘" 타임라인 순서에 의존하면 그날그날 다른 자동화 활동에 따라 깨진다(실측 확인).
    STAGE_DIR은 이 파이프라인 전용이라 앨범탭에 "parksy_stage"라는, 정확히 이 한 장만
    들어있는 앨범으로 뜬다 — 매번 비우고 새로 하나만 넣어서 완전히 결정론적으로 만든다.

    반환: 스테이징된 파일의 디바이스 경로, 없으면 None.
    """
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
    # 이전 스테이징 잔여물 제거 (이 폴더는 이 파이프라인 전용이라 안전하게 비울 수 있음)
    _adb("shell", f"rm -f '{STAGE_DIR}'/*")
    dst = f"{STAGE_DIR}/stage.jpg"
    _adb("shell", f"cp '{src}' '{dst}'")
    _adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
         "-d", "file://" + dst)
    time.sleep(1)
    return dst


def _move_latest_to_gallery() -> str:
    """방금 생성된 이미지를 '박씨 갤러리' 폴더로 이동하고 새 경로를 반환."""
    _adb("shell", "mkdir", "-p", GALLERY_DIR)
    script = (
        f"latest=$(ls -t '{DRAWING_DIR}/'Drawing_assist_*.jpg 2>/dev/null | head -1); "
        f"if [ -n \"$latest\" ]; then mv \"$latest\" '{GALLERY_DIR}/'; fi; "
        f"echo \"$latest\""
    )
    r = _adb("shell", script)
    moved = r.stdout.strip()
    # 갤러리(MediaStore) 갱신을 위한 미디어 스캔
    _adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
         "-d", "file://" + GALLERY_DIR)
    if not moved:
        return None
    return GALLERY_DIR + "/" + moved.split("/")[-1]


def _crop_bottom_watermark(path: str, crop_bottom: float = 8.0) -> str:
    """이미지 하단의 'AI 생성물' 워터마크를 크롭해서 제거한다 (crop_bottom: %).

    pull → 하단 crop_bottom% 잘라내기 → 다시 push.
    """
    import os
    import shutil

    from PIL import Image

    local = "/tmp/pg_crop.jpg"
    # 이전 실패로 남은 파일/디렉토리 정리
    if os.path.isdir(local):
        shutil.rmtree(local, ignore_errors=True)
    elif os.path.isfile(local):
        os.remove(local)
    subprocess.run(["adb", "-s", TAB, "pull", path, local],
                   capture_output=True, text=True, timeout=60)
    if not os.path.isfile(local):  # pull 실패(파일 아님) 시 원본 그대로 반환
        return path
    im = Image.open(local)
    w, h = im.size
    new_h = int(h * (1.0 - crop_bottom / 100.0))
    im.crop((0, 0, w, new_h)).save(local, quality=95)
    subprocess.run(["adb", "-s", TAB, "push", local, path],
                   capture_output=True, text=True, timeout=60)
    return path


@mcp.tool()
def generate_image(prompt: str, style: str = "아르 누보", wait: int = 20, crop_bottom: float = 8.0) -> dict:
    """프롬프트로 이미지를 생성해 갤러리(박씨 갤러리)에 저장한다.

    Args:
        prompt: 이미지 설명. 예: "cute golden retriever puppy"
        style: 스타일 10종 (아르 누보/웹툰/소프트 일러스트/인스타툰/수채화/일러스트/팝아트/스케치/3D 카툰/유화)
        wait: 생성 대기 시간(초), 기본 20초
        crop_bottom: 하단 'AI 생성물' 워터마크 크롭 비율(%). 0이면 크롭 안 함. 기본 8%

    Returns:
        ok / prompt / style / path (저장 경로)
    """
    if style not in STYLES:
        return {"ok": False, "error": f"지원하지 않는 스타일: {style}", "styles": list(STYLES)}

    # 1. 앱 강제 재시작 (깨끗한 상태 보장)
    _adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    _adb("shell", "am", "start", "-n", f"{PKG}/{ACT}")
    time.sleep(4)
    _tap(*NEW)
    time.sleep(2)

    # 2. 텍스트 입력 (공백은 input text에서 %s 로 치환)
    _tap(*TEXT_INPUT)
    time.sleep(1.2)
    _adb("shell", "input", "text", prompt.replace(" ", "%s"))
    time.sleep(1.2)

    # 3. 키보드 닫기 (스타일/생성 버튼이 가려지므로 필수)
    _adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(1.5)

    # 4. "모두 보기" → 전체 스타일 그리드 열기 → 스타일 선택
    _tap(*VIEW_ALL)
    time.sleep(2.0)
    _tap(*STYLES[style])
    time.sleep(1.5)

    # 5. 생성
    _tap(*GENERATE)
    time.sleep(wait)

    # 6. 저장
    _tap(*SAVE)
    time.sleep(4)

    # 7. 박씨 갤러리 전용 폴더로 이동
    path = _move_latest_to_gallery()
    if path is None:
        return {"ok": False, "error": "생성 실패 — 새 이미지가 저장되지 않음", "prompt": prompt, "style": style}

    # 8. 하단 워터마크 크롭 (crop_bottom=0 이면 스킵)
    if crop_bottom > 0:
        path = _crop_bottom_watermark(path, crop_bottom)

    return {
        "ok": True,
        "prompt": prompt,
        "style": style,
        "path": path,
        "cropped": crop_bottom > 0,
    }


@mcp.tool()
def list_styles() -> dict:
    """지원 스타일 목록 + 용도 매뉴얼(Boss 지정)을 반환한다."""
    return {"styles": STYLE_USE, "default": "아르 누보"}


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

    ⚠️ 2026-08-30: 이 폴더에 실물 신분증 등 민감사진이 섞여있던 사례가 있었음.
    restyle_image에 넘기기 전에 파일명만으로 판단하지 말고 필요시 확인할 것.
    """
    r = _adb("shell", f"ls '{PRESET_DIR}/'")
    files = [f for f in r.stdout.strip().split("\n") if f]
    return {"preset_dir": PRESET_DIR, "count": len(files), "presets": files}


@mcp.tool()
def extract_character(prompt: str, wait: int = 20, crop_bottom: float = 0.0) -> dict:
    """누끼(캐릭터 추출) — '소프트 일러스트' 스타일(배경 없음)로 생성해 캐릭터를 분리한다.

    Boss 지정: 누끼는 항상 '소프트 일러스트' 기준 (배경이 없어서 추출이 쉬움).
    crop_bottom 기본 0(워터마크 크롭 안 함 — 배경 없는 캐릭터라 하단 크롭 불필요).
    """
    return generate_image(prompt=prompt, style="소프트 일러스트",
                          wait=wait, crop_bottom=crop_bottom)


# ── 자기소개 만화 스토리 (작가 설정) ──────────────────────
INTRO_STORY = {
    "title": "에듀 아트 엔지니어 — 나를 소개합니다",
    "style": "아르 누보",
    "accent": "#d4a84b",
    "face_source": DEFAULT_SOURCE,
    "shots": [
        {"prompt": "front-facing portrait, confident, art nouveau style", "text": "안녕하세요."},
        {"prompt": "holding a book, teaching gesture, warm light", "text": "저는 교육을 사랑합니다."},
        {"prompt": "holding a paintbrush and palette, artistic", "text": "예술을 사랑합니다."},
        {"prompt": "at a desk with code and gears, focused", "text": "공학을 사랑합니다."},
        {"prompt": "surrounded by book, brush and gear merging into one glowing emblem", "text": "셋을 하나로 잇습니다."},
        {"prompt": "standing tall, emblem on chest, proud", "text": "그게 바로, 에듀 아트 엔지니어."},
        {"prompt": "working in a studio, screens and art around", "text": "기술로 예술을 만들고,\n예술로 사람을 가르칩니다."},
        {"prompt": "holding a phone, glowing screen, art bursting out", "text": "온디바이스에서,\n명령어 한 줄로."},
        {"prompt": "warm smile, reaching out hand, soft golden light", "text": "그리고 언제나, 사람을 향해."},
    ],
}


@mcp.tool()
def restyle_image(source: str = DEFAULT_SOURCE, style: str = "아르 누보", prompt: str = "",
                  wait: int = 20, crop_bottom: float = 8.0) -> dict:
    """박씨 고정 프리셋(기본 parksy_30s, 전신크롭)을 업로드해 배경/화풍만 바꾼다.

    Boss 지정: 웹툰 컷마다 인물이 흔들리면 안 되므로 source를 안 넘기면
    항상 po-deepfake MCP와 동일한 고정 프리셋(parksy_30s.png)을 쓴다.
    다른 인물(가족 등)이 필요할 때만 source를 명시적으로 넘긴다.

    2026-08-30 재작성: 좌표 하드코딩 대신 uiautomator dump로 사진피커를
    실시간 탐색한다(/sdcard/Pictures/parksy_stage/ 전용 격리 폴더 경유 —
    이 파이프라인 전용이라 다른 자동화의 스크린샷과 절대 안 겹침).

    Args:
        source: 프리셋 파일명(박씨 갤러리/프리셋/ 안) 또는 박씨 갤러리 안의 기존 파일명.
                기본값 parksy_30s.png(박씨 전신, po-deepfake와 동일 소스)
        style: 스타일 10종
        prompt: (선택) 합성/배경 변경 프롬프트. 비우면 화풍만 변경
        wait: 생성 대기(초)
        crop_bottom: 워터마크 크롭 비율(%)
    """
    if style not in STYLES:
        return {"ok": False, "error": f"지원하지 않는 스타일: {style}", "styles": list(STYLES)}

    staged = _stage_preset_for_picker(source)
    if staged is None:
        return {"ok": False, "error": f"소스 파일을 못 찾음: {source} (프리셋/박씨갤러리 둘 다 없음)"}

    # 1. 앱 강제 재시작
    _adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    _adb("shell", "am", "start", "-n", f"{PKG}/{ACT}")
    time.sleep(4)

    # 2. "스타일 변경" 진입 → 시스템 사진피커 ("사진" 탭 기본 오픈)
    _tap(*PHOTO_ATTACH)
    time.sleep(2.5)

    # 3. "앨범" 탭으로 전환 (기본은 "사진"=전체타임라인이라 다른 자동화 스크린샷과 경합함)
    xml = _dump_ui()
    album_tab = _node_center(xml, "앨범", resource_id="com.sec.android.gallery3d:id/title")
    if album_tab is None:
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": "사진피커에서 '앨범' 탭을 못 찾음 (uiautomator dump 실패)"}
    _tap(*album_tab)
    time.sleep(2)

    # 4. parksy_stage 앨범(스테이징한 사진 딱 한 장만 들어있음) → uiautomator dump로 실시간 탐색
    xml = _dump_ui()
    stage_album = _node_center(xml, STAGE_ALBUM_NAME, resource_id="com.sec.android.gallery3d:id/title")
    if stage_album is None:
        # "주요 앨범"에 안 뜨면 "모두 보기"를 눌러서 전체 목록에서 재탐색
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

    # 5. 그 앨범 안의 유일한 썸네일 탭
    xml = _dump_ui()
    pos = _first_thumbnail(xml)
    if pos is None:
        _adb("shell", f"rm -f '{staged}'")
        return {"ok": False, "error": "parksy_stage 앨범 안에서 썸네일을 못 찾음"}
    _tap(*pos)
    time.sleep(3)

    # 4. (선택) 프롬프트 편집 (합성/배경 변경)
    if prompt:
        _tap(800, 1896)  # 텍스트 수정 탭
        time.sleep(1.5)
        _tap(1503, 1866)  # 입력한 텍스트 삭제
        time.sleep(1)
        _tap(500, 1896)
        time.sleep(1)
        _adb("shell", "input", "text", prompt.replace(" ", "%s"))
        time.sleep(1)
        _adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(1.5)

    # 5. 모두 보기 → 스타일 선택
    _tap(*VIEW_ALL)
    time.sleep(2)
    _tap(*STYLES[style])
    time.sleep(1.5)

    # 6. 생성
    _tap(*GENERATE)
    time.sleep(wait)

    # 7. 저장 + 박씨 갤러리 이동 + 크롭
    _tap(*SAVE)
    time.sleep(4)
    path = _move_latest_to_gallery()
    # 스테이징용 임시 사본 정리 (성공/실패 무관)
    _adb("shell", f"rm -f '{staged}'")
    if path is None:
        return {"ok": False, "error": "생성 실패 — 새 이미지가 저장되지 않음", "source": source}
    if crop_bottom > 0:
        path = _crop_bottom_watermark(path, crop_bottom)

    return {
        "ok": True,
        "style": style,
        "source": source,
        "prompt": prompt,
        "path": path,
        "cropped": crop_bottom > 0,
    }


@mcp.tool()
def generate_intro() -> dict:
    """자기소개 만화(9컷)를 얼굴 사진 + 아르 누보로 생성한다.

    INTRO_STORY(작가 설정) 기반 — 얼굴 + 컷별 프롬프트 → 새 장면 재생성.
    """
    results = []
    shots = INTRO_STORY["shots"]
    for i, shot in enumerate(shots):
        r = restyle_image(source=INTRO_STORY["face_source"], style=INTRO_STORY["style"],
                          prompt=shot["prompt"], wait=18)
        results.append({
            "cut": i + 1,
            "text": shot["text"],
            "ok": r.get("ok"),
            "path": r.get("path"),
        })
        print(f"[generate_intro] {i+1}/{len(shots)} ok={r.get('ok')}", flush=True)
    return {
        "ok": all(x["ok"] for x in results),
        "title": INTRO_STORY["title"],
        "style": INTRO_STORY["style"],
        "shots": results,
    }


if __name__ == "__main__":
    mcp.run()
