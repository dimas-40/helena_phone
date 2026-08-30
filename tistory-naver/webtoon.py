#!/usr/bin/env python3
"""
webtoon.py — 티스토리 웹툰 발행 렌더러 (parksy-webtoon-player v2 주입)

parksy-image 웹툰 파이프라인의 **6번째 출력 타겟(티스토리)** 을 담당한다.
manifest(에피소드 메타 + 이미지 URL 목록)를 읽어 → A급 웹툰 뷰어 HTML 생성 → posts/<slug>.json.

구조는 template.py(기본 글) / magazine.py(웹진)와 동일 — "포스트 타입 하나 = 렌더러 하나".
즉 이 파일이 티스토리 파이프라인에 **웹툰이라는 플러그 옵션**을 추가하는 것.

manifest JSON 형식:
  {
    "slug": "ep04-restaurant",      // 생략 시 파일명
    "title": "오늘 레스토랑에서 손님이 화",
    "episode": 4,                   // 0이면 헤더에 회차 숨김
    "mode": "carousel",             // "carousel"(인스타 가로 스와이프) | "scroll"(세로 웹툰)
    "accent": "#4285f4",
    "autoplay": false,
    "autoplaySpeed": 5000,
    "fullscreen": true,
    "images": [
      {"src": "https://blog.kakaocdn.net/…", "alt": "씬 1: 식당 입구"},
      {"src": "https://…", "alt": "씬 2: 손님이 화를 내는 장면"}
    ],                              // 또는 ["url1", "url2"] (alt 생략)
    "dialogue": [
      {"cut": 0, "speaker": "주인", "text": "어서 오세요", "pos": "bottom-left"},
      {"cut": 1, "speaker": "손님", "text": "커피 한 잔 주세요", "pos": "bottom-right"}
    ],                              // 말풍선(대사 텍스트). pos: bottom-left/right·top-left/right·center
    "account": "dtslib",            // accounts.json 의 id (필수)
    "blog": "dtslib1k",             // 블로그 슬러그 (필수)
    "category": "웹툰",
    "tags": ["웹툰", "일상"],
    "visibility": "public"          // public | protected | private
  }

사용법:
  python3 webtoon.py episodes/ep04.json
  python3 webtoon.py episodes/ep04.json --dump                # HTML만 stdout 출력
  python3 webtoon.py --images a.jpg,b.jpg --title "제목" \
      --account dtslib --blog dtslib1k --episode 1           # CLI 단축 (임시)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
POSTS_DIR = BASE / "posts"
TEMPLATE = BASE / "assets" / "parksy-webtoon-player.html"
POSTS_DIR.mkdir(exist_ok=True)

# 플레이어 템플릿의 설정 블록만 갈아끼운다 (코드는 단일 원본 유지).
CONFIG_RE = re.compile(
    r'(<script id="parksy-webtoon-config" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)

# 플레이어가 실제로 읽는 키만 주입 (manifest의 발행 메타와 분리).
PLAYER_KEYS = (
    "title", "episode", "images", "mode", "autoplay",
    "autoplaySpeed", "accent", "fullscreen", "dialogue",
)


def load_template() -> str:
    if not TEMPLATE.exists():
        print(f"❌ 템플릿 없음: {TEMPLATE}", file=sys.stderr)
        raise SystemExit(1)
    return TEMPLATE.read_text(encoding="utf-8")


def inject_config(template: str, manifest: dict) -> str:
    player_cfg = {k: manifest[k] for k in PLAYER_KEYS if k in manifest}
    cfg_json = json.dumps(player_cfg, ensure_ascii=False, indent=2)

    def _repl(m: re.Match) -> str:
        return m.group(1) + "\n" + cfg_json + "\n  " + m.group(3)

    html, n = CONFIG_RE.subn(_repl, template)
    if n == 0:
        print("⚠️ 템플릿에서 설정 블록을 못 찾음 — HTML이 그대로 발행될 수 있음", file=sys.stderr)
    return html


def build_post(manifest: dict, slug: str) -> dict:
    required = ("account", "blog")
    for k in required:
        if k not in manifest:
            print(f"❌ manifest에 '{k}' 필수", file=sys.stderr)
            raise SystemExit(1)

    html = inject_config(load_template(), manifest)
    title = manifest.get("title") or f"웹툰 EP.{manifest.get('episode', '?')}"

    return {
        "account": manifest["account"],
        "blog": manifest["blog"],
        "title": title,
        "content": html,
        "tags": [t.strip() for t in manifest.get("tags", []) if t.strip()],
        "category": manifest.get("category", "웹툰"),
        "visibility": manifest.get("visibility", "public"),
    }


def load_manifest(path: Path) -> dict:
    if not path.exists():
        print(f"❌ 없음: {path}", file=sys.stderr)
        raise SystemExit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _from_cli(args) -> dict:
    images = [{"src": u.strip(), "alt": ""} for u in args.images.split(",") if u.strip()]
    if not images:
        print("❌ --images 에 최소 1개 URL 필요", file=sys.stderr)
        raise SystemExit(1)
    return {
        "slug": args.slug,
        "title": args.title,
        "episode": args.episode,
        "mode": args.mode,
        "accent": args.accent,
        "autoplay": args.autoplay,
        "autoplaySpeed": args.autoplay_speed,
        "fullscreen": args.fullscreen,
        "images": images,
        "account": args.account,
        "blog": args.blog,
        "category": args.category,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "visibility": args.visibility,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="티스토리 웹툰 발행 → posts/*.json")
    ap.add_argument("manifest", nargs="?", help="manifest JSON 경로 (생략 시 --images 로 CLI 생성)")
    ap.add_argument("--dump", action="store_true", help="HTML을 stdout 으로 출력만")
    # CLI 단축 옵션 (manifest 없이 임시 발행용)
    ap.add_argument("--images", default="", help="쉼표 구분 이미지 URL")
    ap.add_argument("--title", default="", help="에피소드 제목")
    ap.add_argument("--slug", default="webtoon-episode", help="출력 파일 slug")
    ap.add_argument("--episode", type=int, default=0)
    ap.add_argument("--mode", default="carousel", choices=["carousel", "scroll"])
    ap.add_argument("--accent", default="#4285f4")
    ap.add_argument("--autoplay", action="store_true")
    ap.add_argument("--autoplay-speed", type=int, default=5000)
    ap.add_argument("--fullscreen", action="store_true", default=True)
    ap.add_argument("--account", default="")
    ap.add_argument("--blog", default="")
    ap.add_argument("--category", default="웹툰")
    ap.add_argument("--tags", default="웹툰")
    ap.add_argument("--visibility", default="public", choices=["public", "protected", "private"])
    args = ap.parse_args()

    if args.manifest:
        manifest = load_manifest(Path(args.manifest))
        slug = manifest.get("slug") or Path(args.manifest).stem
    else:
        manifest = _from_cli(args)
        slug = manifest["slug"]

    post = build_post(manifest, slug)

    if args.dump:
        print(post["content"])
        return 0

    out = POSTS_DIR / f"{slug}.json"
    out.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out.name} 생성 — 계정:{post['account']} · 블로그:{post['blog']} · 컷:{len(manifest.get('images', []))}장")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
