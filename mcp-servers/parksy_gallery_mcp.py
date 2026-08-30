#!/usr/bin/env python3
"""
박씨 갤러리 MCP 서버 — 삼성 그리기 어시스트(Creative Studio) 텍스트→이미지→저장

툴:
  generate_image(prompt, style)  — 프롬프트로 이미지 생성 + 갤러리 저장 (스타일 10종)
  list_styles()                  — 지원 스타일 목록

의존: 태블릿 ADB 연결 (100.86.15.50:5900)
결과: /sdcard/DCIM/Drawing assist/Drawing_assist_*.jpg
"""
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

# 좌표 상수
NEW = (1443, 119)         # "새로 작성" (앱 리셋)
TEXT_INPUT = (500, 1896)  # 텍스트 입력창
VIEW_ALL = (1287, 2114)   # "모두 보기" (전체 스타일 그리드 열기)
GENERATE = (800, 2275)    # "생성" 버튼
SAVE = (851, 270)         # "저장" 버튼 (생성 완료 후 상단)

# 갤러리 경로
GALLERY_DIR = "/sdcard/DCIM/박씨 갤러리"    # 박씨 갤러리 전용 폴더
DRAWING_DIR = "/sdcard/DCIM/Drawing assist"  # 앱 기본 저장 폴더


def _adb(*args):
    return subprocess.run(
        ["adb", "-s", TAB, *args], capture_output=True, text=True, timeout=60
    )


def _tap(x, y):
    _adb("shell", "input", "tap", str(x), str(y))


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
    """박씨 갤러리 프리셋 사진 목록(딥페이크용 참조 사진)을 반환한다."""
    preset_dir = GALLERY_DIR + "/프리셋"
    r = _adb("shell", f"ls '{preset_dir}/'")
    files = [f for f in r.stdout.strip().split("\n") if f]
    return {"preset_dir": preset_dir, "count": len(files), "presets": files}


@mcp.tool()
def extract_character(prompt: str, wait: int = 20, crop_bottom: float = 0.0) -> dict:
    """누끼(캐릭터 추출) — '소프트 일러스트' 스타일(배경 없음)로 생성해 캐릭터를 분리한다.

    Boss 지정: 누끼는 항상 '소프트 일러스트' 기준 (배경이 없어서 추출이 쉬움).
    crop_bottom 기본 0(워터마크 크롭 안 함 — 배경 없는 캐릭터라 하단 크롭 불필요).
    """
    return generate_image(prompt=prompt, style="소프트 일러스트",
                          wait=wait, crop_bottom=crop_bottom)


# 사진 선택기에서 "박씨 갤러리" 앨범의 사진 위치 (첫 행 4장)
PHOTO_POS = [(150, 348), (410, 348), (670, 348), (930, 348)]
# 얼굴 사진(parksy_casual_crop) 위치 — 앨범 1번째 (상징 일러스트는 폐기 폴더로 이동시킴)
FACE_PHOTO = (150, 348)

# ── 자기소개 만화 스토리 (작가 설정) ──────────────────────
INTRO_STORY = {
    "title": "에듀 아트 엔지니어 — 나를 소개합니다",
    "style": "아르 누보",
    "accent": "#d4a84b",
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
def restyle_image(photo_index: int = 0, style: str = "아르 누보", prompt: str = "",
                  wait: int = 20, crop_bottom: float = 8.0, face: bool = False) -> dict:
    """기존 사진(박씨 갤러리 앨범)을 업로드해 스타일 변경(재스타일/합성)한다.

    Args:
        photo_index: 박씨 갤러리 앨범의 사진 인덱스(0~3)
        style: 스타일 10종
        prompt: (선택) 합성/배경 변경 프롬프트. 비우면 화풍만 변경
        wait: 생성 대기(초)
        crop_bottom: 워터마크 크롭 비율(%)
        face: True면 얼굴 사진(parksy_casual_crop)을 입력으로 사용
    """
    if style not in STYLES:
        return {"ok": False, "error": f"지원하지 않는 스타일: {style}", "styles": list(STYLES)}
    if face:
        photo_pos = FACE_PHOTO
    else:
        if not (0 <= photo_index < len(PHOTO_POS)):
            return {"ok": False, "error": f"photo_index는 0~{len(PHOTO_POS)-1}"}
        photo_pos = PHOTO_POS[photo_index]

    # 1. 앱 강제 재시작
    _adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    _adb("shell", "am", "start", "-n", f"{PKG}/{ACT}")
    time.sleep(4)

    # 2. 스타일 변경 탭 → 사진 선택기
    _tap(242, 1896)
    time.sleep(2.5)

    # 3. 박씨 갤러리 앨범 → 사진 선택
    _tap(1115, 969)
    time.sleep(2.5)
    _tap(*photo_pos)
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
    _tap(1287, 2114)
    time.sleep(2)
    _tap(*STYLES[style])
    time.sleep(1.5)

    # 6. 생성
    _tap(800, 2275)
    time.sleep(wait)

    # 7. 저장 + 박씨 갤러리 이동 + 크롭
    _tap(851, 270)
    time.sleep(4)
    path = _move_latest_to_gallery()
    if path is None:
        return {"ok": False, "error": "생성 실패 — 새 이미지가 저장되지 않음"}
    if crop_bottom > 0:
        path = _crop_bottom_watermark(path, crop_bottom)

    return {
        "ok": True,
        "style": style,
        "photo_index": photo_index,
        "prompt": prompt,
        "path": path,
        "cropped": crop_bottom > 0,
    }


@mcp.tool()
def generate_intro() -> dict:
    """자기소개 만화(10컷)를 얼굴 사진 + 아르 누보로 생성한다.

    INTRO_STORY(작가 설정) 기반 — 얼굴 + 컷별 프롬프트 → 새 장면 재생성.
    """
    results = []
    shots = INTRO_STORY["shots"]
    for i, shot in enumerate(shots):
        r = restyle_image(face=True, style=INTRO_STORY["style"], prompt=shot["prompt"], wait=18)
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
