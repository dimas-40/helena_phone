#!/usr/bin/env python3
"""
삼성 그리기 어시스트(Creative Studio) 자동화 — 텍스트 → 이미지 생성 → 갤러리 저장
MCP처럼 호출: python3 scripts/drawing_assist.py --prompt "강아지" --style "일러스트"

요구: 태블릿 ADB 연결 (100.86.15.50:5900)
결과: /sdcard/DCIM/Drawing assist/Drawing_assist_*.jpg 로 저장됨
"""
import argparse
import subprocess
import sys
import time

TAB = "100.86.15.50:5900"
PKG = "com.samsung.android.app.sketchbook"
ACT = "com.samsung.android.app.sketchbook.application.DrawingActivity"

# 스타일 → 좌표 (태블릿 1600x2560 기준, "모두 보기" 전체 스타일 그리드)
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
    "3D카툰": (273, 893),
    "3D 카툰": (273, 893),
    "유화": (624, 893),
}

# 좌표 상수
NEW = (1443, 119)         # "새로 작성" (앱 리셋)
TEXT_INPUT = (500, 1896)  # 텍스트 입력창
VIEW_ALL = (1287, 2114)   # "모두 보기" (전체 스타일 그리드 열기)
GENERATE = (800, 2275)    # "생성" 버튼
SAVE = (851, 270)         # "저장" 버튼 (생성 완료 후 상단)


def adb(*args, timeout=30):
    return subprocess.run(
        ["adb", "-s", TAB, *args], capture_output=True, text=True, timeout=timeout
    )


def tap(x, y):
    adb("shell", "input", "tap", str(x), str(y))


def main():
    p = argparse.ArgumentParser(description="삼성 그리기 어시스트 이미지 생성")
    p.add_argument("--prompt", required=True, help="이미지 설명 (한국어/영어)")
    p.add_argument("--style", default="일러스트", help=f"스타일: {', '.join(STYLES)}")
    p.add_argument("--wait", type=int, default=20, help="생성 대기(초)")
    p.add_argument("--no-save", action="store_true", help="저장하지 않음")
    args = p.parse_args()

    # 1. 앱 실행 + 새로 작성(리셋)
    adb("shell", "am", "start", "-n", f"{PKG}/{ACT}")
    time.sleep(3)
    tap(*NEW)
    time.sleep(2)

    # 2. 텍스트 입력 (공백은 input text에서 %s 로 치환)
    tap(*TEXT_INPUT)
    time.sleep(1.2)
    prompt = args.prompt.replace(" ", "%s")
    adb("shell", "input", "text", prompt)
    time.sleep(1.2)

    # 3. 키보드 닫기 (스타일/생성 버튼이 가려지므로 필수)
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(1.5)

    # 4. "모두 보기" → 전체 스타일 그리드 → 스타일 선택
    if args.style not in STYLES:
        print(f"⚠️  '{args.style}' 는 지원하지 않음.", file=sys.stderr)
        print(f"    지원: {', '.join(STYLES)}", file=sys.stderr)
        return 1
    tap(*VIEW_ALL)
    time.sleep(2.0)
    tap(*STYLES[args.style])
    time.sleep(1.5)

    # 5. 생성
    tap(*GENERATE)
    print(f"⏳ 생성 중 ({args.wait}초 대기)...")
    time.sleep(args.wait)

    # 6. 저장
    if not args.no_save:
        tap(*SAVE)
        time.sleep(4)
        # 박씨 갤러리 전용 폴더로 이동
        adb("shell", "mkdir", "-p", "/sdcard/DCIM/박씨 갤러리")
        move = (
            "latest=$(ls -t '/sdcard/DCIM/Drawing assist/'Drawing_assist_*.jpg 2>/dev/null | head -1); "
            "if [ -n \"$latest\" ]; then mv \"$latest\" '/sdcard/DCIM/박씨 갤러리/'; fi; echo \"$latest\""
        )
        r = adb("shell", move)
        adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", "file:///sdcard/DCIM/박씨 갤러리")
        print(f"✅ 완료 — 박씨 갤러리/{r.stdout.strip().split('/')[-1]}")
    else:
        print("✅ 생성 완료 (저장 안 함)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
