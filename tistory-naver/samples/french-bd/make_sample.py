#!/usr/bin/env python3
"""프랑스 BD 웹툰 샘플: 2컷 생성 + wt-viewer 포스트 JSON 빌드."""
import subprocess, base64, json

W, H = 800, 1200
FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"

def R(x1,y1,x2,y2): return f"rectangle {x1},{y1} {x2},{y2}"
def C(cx,cy,r): return f"circle {cx},{cy} {cx+r},{cy}"
def E(cx,cy,rx,ry): return f"ellipse {cx},{cy} {rx},{ry} 0,360"
def L(x1,y1,x2,y2): return f"line {x1},{y1} {x2},{y2}"
def P(pts): return "polygon " + " ".join(f"{x},{y}" for x,y in pts)

def make_panel(bubble_text, caption, bubble_cy=300, bg_sky="#dce9f2", accent_mariniere="#2f5fa8"):
    shapes = []
    def add(fill, stroke, w, *draws):
        shapes.append((fill, stroke, w, " ".join(draws)))
    # 배경
    add(bg_sky, None, 0, R(24,24,776,560))
    add("#e9e1d2", None, 0, R(24,560,776,1176))
    add("#b9cddb", None, 0, *(C(x,y,3) for y in range(58,542,44) for x in range(58,762,44)))
    add(None, "#1a1a1a", 5, L(24,560,776,560))
    # 에펠탑
    add("#3a3a3a", None, 0, P([(622,560),(642,322),(662,322),(682,560)]))
    add(None, "#3a3a3a", 7, L(626,502,678,502), L(630,442,674,442), L(634,382,670,382))
    add("#3a3a3a", None, 0, P([(652,304),(662,322),(670,322)]))
    # 마리니에르 몸통 + 줄무늬
    add("#ffffff", "#1a1a1a", 7, P([(302,650),(428,650),(438,892),(292,892)]))
    add(accent_mariniere, None, 0, *(P([(300,y),(430,y),(434,y+18),(296,y+18)]) for y in range(688,868,40)))
    add("#ffffff", "#1a1a1a", 7, P([(302,668),(252,698),(252,802),(302,812)]), P([(428,668),(522,690),(527,722),(432,712)]))
    add("#f2c9a4", "#1a1a1a", 6, C(254,802,16), C(524,718,16))
    add("#d9a24f", "#7a4a12", 6, E(560,762,62,17))
    add(None, "#7a4a12", 5, L(520,705,600,762), L(570,755,604,772), L(565,758,600,776))
    # 머리+베레모
    add("#f2c9a4", "#1a1a1a", 7, C(366,540,58))
    add("#5a3a1a", "#1a1a1a", 5, P([(310,520),(318,488),(414,488),(422,520),(412,504),(312,504)]))
    add("#b23a2a", "#1a1a1a", 7, E(366,492,58,20))
    add(None, "#1a1a1a", 6, L(366,474,366,462), C(366,460,5))
    # 얼굴
    add("#1a1a1a", None, 0, C(342,540,5), C(390,540,5), L(338,566,394,566))
    add("#e88a7a", None, 0, C(324,558,8), C(408,558,8))
    # 말풍선
    add("#ffffff", "#1a1a1a", 8, E(360,bubble_cy,205,92))
    add("#ffffff", "#1a1a1a", 8, P([(296,bubble_cy+74),(340,bubble_cy+152),(248,bubble_cy+88)]))
    # 캡션
    add("#f7d94e", "#1a1a1a", 6, R(50,50,300,120))
    # 패널 테두리
    add(None, "#1a1a1a", 10, R(24,24,776,1176))

    cmd = ["magick", "-size", f"{W}x{H}", "xc:#f5efe0"]
    for fill, stroke, w, draw in shapes:
        cmd += ["-fill", fill if fill else "none"]
        cmd += (["-stroke", stroke, "-strokewidth", str(w)] if stroke else ["-stroke", "none"])
        cmd += ["-draw", draw]
    cmd += ["-font", FONT, "-fill", "#111", "-pointsize", "42", "-gravity", "north", "-annotate", f"+0+{bubble_cy-38}", bubble_text]
    cmd += ["-fill", "#111", "-pointsize", "30", "-gravity", "northwest", "-annotate", "+68+82", caption]
    return cmd

def render(cmd, out):
    subprocess.run(cmd + ["-quality", "88", out], check=True)

# 2컷
render(make_panel("Bonjour !", "EPISODE 4 · CUT 1"), "/tmp/bd_cut1.jpg")
render(make_panel("C'est la vie !", "EPISODE 4 · CUT 2", bubble_cy=300, accent_mariniere="#a8322f"), "/tmp/bd_cut2.jpg")

# base64
def b64(path):
    return "data:image/jpeg;base64," + base64.b64encode(open(path,'rb').read()).decode()

# wt-viewer 포스트 빌드
tpl = open("/root/gifts/webtoon-viewer/wt-viewer-post.html", encoding="utf-8").read()
images = [b64("/tmp/bd_cut1.jpg"), b64("/tmp/bd_cut2.jpg")]
cfg = {
    "images": images,
    "title": "파리에서 온 편지",
    "episode": 4,
    "series": "프랑스 만화 테스트",
    "ctaText": "다음 편 보기",
    "ctaUrl": ""
}
import re
tpl = re.sub(r"(var CONFIG = )\{.*?\n  \};", lambda m: m.group(1)+json.dumps(cfg, ensure_ascii=False, indent=4)+";", tpl, flags=re.DOTALL)

post = {
    "account": "eae-kr",
    "blog": "eae-kr",
    "title": "프랑스 BD 스타일 웹툰 샘플 (말풍선 오버레이)",
    "content": tpl,
    "tags": ["웹툰", "프랑스만화", "샘플"],
    "category": "웹툰",
    "visibility": "public",
}
import pathlib
pathlib.Path("/root/work/tistory-naver/posts").mkdir(exist_ok=True)
out = "/root/work/tistory-naver/posts/eae-kr-french-bd-sample.json"
json.dump(post, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("post json:", out, "size:", len(post["content"]), "chars")
print("cuts:", len(images))
