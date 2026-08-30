#!/usr/bin/env python3
"""프랑스 BD(ligne claire) 스타일 웹툰 컷 — ImageMagick 드로잉."""
import subprocess

W, H = 800, 1200
FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"

# shape = (fill, stroke, strokewidth, draw_string)
shapes = []

def R(x1,y1,x2,y2): return f"rectangle {x1},{y1} {x2},{y2}"
def C(cx,cy,r): return f"circle {cx},{cy} {cx+r},{cy}"
def E(cx,cy,rx,ry): return f"ellipse {cx},{cy} {rx},{ry} 0,360"
def L(x1,y1,x2,y2): return f"line {x1},{y1} {x2},{y2}"
def P(pts): return "polygon " + " ".join(f"{x},{y}" for x,y in pts)

def add(fill, stroke, w, *draws):
    shapes.append((fill, stroke, w, " ".join(draws)))

# ── 배경 ──
add("#dce9f2", None, 0, R(24,24,776,560))          # 하늘
add("#e9e1d2", None, 0, R(24,560,776,1176))        # 땅
add("#b9cddb", None, 0, *(C(x,y,3) for y in range(58,542,44) for x in range(58,762,44)))  # 할프톤
add(None, "#1a1a1a", 5, L(24,560,776,560))         # 수평선

# ── 에펠탑 실루엣 (오른쪽 배경) ──
add("#3a3a3a", None, 0, P([(622,560),(642,322),(662,322),(682,560)]))
add(None, "#3a3a3a", 7, L(626,502,678,502), L(630,442,674,442), L(634,382,670,382))
add("#3a3a3a", None, 0, P([(652,304),(662,322),(670,322)]))

# ── 캐릭터 — 마리니에르 몸통 ──
add("#ffffff", "#1a1a1a", 7, P([(302,650),(428,650),(438,892),(292,892)]))
add("#2f5fa8", None, 0, *(P([(300,y),(430,y),(434,y+18),(296,y+18)]) for y in range(688,868,40)))  # 줄무늬
# 팔
add("#ffffff", "#1a1a1a", 7, P([(302,668),(252,698),(252,802),(302,812)]))
add("#ffffff", "#1a1a1a", 7, P([(428,668),(522,690),(527,722),(432,712)]))
# 손
add("#f2c9a4", "#1a1a1a", 6, C(254,802,16), C(524,718,16))
# 바게트
add("#d9a24f", "#7a4a12", 6, E(560,762,62,17))
add(None, "#7a4a12", 5, L(520,705,600,762), L(570,755,604,772), L(565,758,600,776))

# ── 머리 + 베레모 ──
add("#f2c9a4", "#1a1a1a", 7, C(366,540,58))       # 얼굴
add("#5a3a1a", "#1a1a1a", 5, P([(310,520),(318,488),(414,488),(422,520),(412,504),(312,504)]))  # 머리카락
add("#b23a2a", "#1a1a1a", 7, E(366,492,58,20))    # 베레모
add(None, "#1a1a1a", 6, L(366,474,366,462), C(366,460,5))

# ── 얼굴 표정 ──
add("#1a1a1a", None, 0, C(342,540,5), C(390,540,5), L(338,566,394,566))  # 눈+미소
add("#e88a7a", None, 0, C(324,558,8), C(408,558,8))  # 볼터치

# ── 말풍선 ──
add("#ffffff", "#1a1a1a", 8, E(360,300,205,92))
add("#ffffff", "#1a1a1a", 8, P([(296,374),(340,452),(248,388)]))

# ── 캡션 박스 ──
add("#f7d94e", "#1a1a1a", 6, R(50,50,300,120))

# ── 패널 테두리 (최상단, 굵게) ──
add(None, "#1a1a1a", 10, R(24,24,776,1176))

# ── magick 명령 조립 ──
cmd = ["magick", "-size", f"{W}x{H}", "xc:#f5efe0"]
for fill, stroke, w, draw in shapes:
    if fill: cmd += ["-fill", fill]
    else: cmd += ["-fill", "none"]
    if stroke: cmd += ["-stroke", stroke, "-strokewidth", str(w)]
    else: cmd += ["-stroke", "none"]
    cmd += ["-draw", draw]

# 텍스트 (annotate)
cmd += ["-font", FONT]
cmd += ["-fill", "#111", "-pointsize", "42", "-gravity", "north", "-annotate", "+0+262", "Bonjour !"]
cmd += ["-fill", "#111", "-pointsize", "30", "-gravity", "northwest", "-annotate", "+68+82", "EPISODE 4"]
cmd += ["-quality", "90", "/tmp/french_bd_01.jpg"]

subprocess.run(cmd, check=True)
print("done")
