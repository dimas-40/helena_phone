#!/usr/bin/env python3
"""곡 페이지(index.html)를 page.json + data.js 에서 만든다.

    python3 scripts/pd_page.py midi_lane/pd/11-beethoven-waldstein-1

왜 만들었나: 페이지마다 <head>·표제·띠·독(dock)은 모양이 같고, 사람이 손으로
옮겨 적는 동안 **계산해야 할 것**을 손으로 적어서 틀렸다. 09호는 축(axis) 가운데
칸을 `0:29 · 침묵 · 0:30` 으로 적었는데 실제 값은 `0:58 · 침묵 · 1:00` 이었고,
10호도 같은 자리를 한 번 고쳤다. 축과 독의 시각은 *데이터에서 나오는 값*이지
*쓰는 값*이 아니다. 그래서 여기서 계산한다.

page.json 이 담는 것 = 사람이 쓰는 것(문장·표·출처).
이 스크립트가 담는 것 = 기계가 세는 것(축 5칸, 독 시각, canonical, JSON-LD).

page.json 최소 골격:
    {"no","slug","title","desc","og_title","og_desc","og_type",
     "ld_work":{"name","composer","birth","death","date","key"},
     "eyebrow_tail","catno","h1","subtitle","marking",
     "hero_img","hero_alt","hero_cap","sections": "<section>…</section>…"}

`sections` 안에는 표제 다음부터 독 앞까지가 통째로 들어간다. 그 안의 시각은
사람이 쓰되, **띠 축과 독만은 이 스크립트가 덮어쓴다.**
"""
import json
import re
import sys
from pathlib import Path


def fmt(t):
    """초 → m:ss (음수·None 방어). 1시간 넘으면 h:mm:ss."""
    if t is None:
        return "—"
    s = int(t)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)


def read_data_js(p):
    """data.js 의 window.PIECE 를 읽는다. 없으면 그 사실을 말하고 멈춘다."""
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"window\.PIECE\s*=\s*(\{.*\})\s*;?\s*$", txt, re.S)
    if not m:
        m = re.search(r"window\.PIECE\s*=\s*(\{.*\})", txt, re.S)
    if not m:
        sys.exit("data.js 에서 window.PIECE 를 못 찾았다: %s" % p)
    return json.loads(m.group(1))


def axis_html(d):
    """띠 아래 축 5칸 — 전부 데이터에서 계산한다.

    가운데 칸만 두 시각(원곡 끝 · 침묵 끝)을 함께 적는다. 이 자리를 손으로
    적어서 09·10 두 번 틀렸으므로 여기서만은 반드시 계산한다.
    """
    dur = d["duration"]
    oe, ge = d["origEnd"], d["gapEnd"]
    return ('<div class="axis"><span>%s</span><span>%s</span>'
            '<span>%s · 침묵 · %s</span><span>%s</span><span>%s</span></div>'
            % (fmt(0), fmt(oe / 2), fmt(oe), fmt(ge),
               fmt((ge + dur) / 2), fmt(dur)))


HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://parksy.kr/channel/musician/piano/{slug}/">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="https://parksy.kr/channel/musician/piano/{slug}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/piano.css">
<script>document.documentElement.className+=' js';</script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@graph":[
    {{"@type":"Person","@id":"https://parksy.kr/#person","name":"Parksy",
     "url":"https://parksy.kr/channel/musician/",
     "sameAs":["https://parksy.kr/channel/musician/","https://www.youtube.com/channel/UCun6b2HD3ekp35PhqbTfOlg"]}},
    {{"@type":"WebPage","@id":"https://parksy.kr/channel/musician/piano/{slug}/#page",
     "url":"https://parksy.kr/channel/musician/piano/{slug}/",
     "name":"{ld_name}",
     "inLanguage":"ko",
     "author":{{"@id":"https://parksy.kr/#person"}},
     "publisher":{{"@id":"https://parksy.kr/#person"}},
     "about":{{"@id":"https://parksy.kr/channel/musician/piano/{slug}/#work"}}}},
    {{"@type":"MusicComposition","@id":"https://parksy.kr/channel/musician/piano/{slug}/#work",
     "name":"{ldw_name}",
     "composer":{{"@type":"Person","name":"{ldw_composer}","birthDate":"{ldw_birth}","deathDate":"{ldw_death}"}},
     "datePublished":"{ldw_date}",
     "musicalKey":"{ldw_key}",
     "inLanguage":"zxx"}}
  ]
}}
</script>
</head>
<body>
<div id="prog"></div>

<!-- ══ 표제 ══════════════════════════════════════════════ -->
<header class="hero">
  <div class="wide">
    <div class="hero-grid">
      <div class="rv">
        <p class="eyebrow"><a href="../">박씨 렌더링</a> &nbsp;·&nbsp; {eyebrow_tail}</p>
        <span class="catno">{catno}</span>
        <h1>{h1}</h1>
        <p class="subtitle">{subtitle}</p>
        <span class="marking">{marking}</span>
      </div>
      <figure class="hero-figure rv">
        <img src="{hero_img}" alt="{hero_alt}">
        <figcaption>
          {hero_cap}
        </figcaption>
      </figure>
    </div>
  </div>
</header>
"""

TAIL = """
<!-- ══ 독 ═══════════════════════════════════════════════ -->
<div id="dock">
  <div class="in">
    <button id="play" aria-label="재생"></button>
    <div id="wavewrap"><canvas id="wave"></canvas></div>
    <span id="which">원곡</span>
    <span id="time">0:00 / {total}</span>
  </div>
</div>

<audio id="au" src="audio/combined.mp3" preload="metadata"></audio>
<script src="data.js"></script>
<script src="../assets/piano.js"></script>
</body>
</html>
"""

AXIS_RE = re.compile(r'<div class="axis">.*?</div>', re.S)
DOCKTIME_RE = re.compile(r'(<span id="time">)0:00 / [^<]*(</span>)')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pdir = Path(sys.argv[1]).resolve()
    out = pdir / "site" / pdir.name / "index.html"
    dj = pdir / "site" / pdir.name / "data.js"
    if not dj.exists():
        sys.exit("없다: %s" % dj)

    # 쪽지는 파이썬 파일(page.py)로 쓴다. HTML 덩어리를 JSON 문자열로 넣으면
    # 따옴표를 매번 이스케이프해야 하고, 그러다 문장 하나가 조용히 깨진다.
    # 삼중따옴표가 그냥 되는 쪽이 낫다 — 사람이 읽고 고칠 수 있어야 한다.
    pj = pdir / "site" / pdir.name / "page.py"
    if pj.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("page_%s" % pdir.name.replace("-", "_"), pj)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        page = mod.PAGE
    else:
        j = pdir / "site" / pdir.name / "page.json"
        if not j.exists():
            sys.exit("없다: %s 도 %s 도" % (pj, j))
        page = json.loads(j.read_text(encoding="utf-8"))
    data = read_data_js(dj)

    sec = page["sections"]
    # 축은 언제나 계산값으로 덮어쓴다 — 손으로 적은 축이 있으면 여기서 죽는다.
    if AXIS_RE.search(sec):
        sec = AXIS_RE.sub(axis_html(data), sec, count=1)
    else:
        print("⚠ sections 안에 <div class=\"axis\"> 가 없다 — 축을 못 채웠다")

    lw = page["ld_work"]
    html = HEAD.format(
        title=page["title"], desc=page["desc"], slug=page["slug"],
        og_title=page["og_title"], og_desc=page["og_desc"], og_type=page["og_type"],
        ld_name=page.get("ld_name", page["og_title"]),
        ldw_name=lw["name"], ldw_composer=lw["composer"], ldw_birth=lw["birth"],
        ldw_death=lw["death"], ldw_date=lw["date"], ldw_key=lw["key"],
        eyebrow_tail=page["eyebrow_tail"], catno=page["catno"], h1=page["h1"],
        subtitle=page["subtitle"], marking=page["marking"],
        hero_img=page["hero_img"], hero_alt=page["hero_alt"], hero_cap=page["hero_cap"],
    )
    tail = DOCKTIME_RE.sub(lambda m: m.group(1) + "0:00 / " + fmt(data["duration"]) + m.group(2),
                           TAIL.format(total=fmt(data["duration"])))
    out.write_text(html + sec + tail, encoding="utf-8")

    # 채운 값이 데이터와 맞는지 스스로 확인한다.
    body = (html + sec + tail)
    ok_axis = fmt(data["origEnd"]) in body and fmt(data["gapEnd"]) in body
    ok_dock = ("0:00 / " + fmt(data["duration"])) in body
    print("→ %s (%d 바이트)" % (out, len(body.encode())))
    print("   길이 %s · 원곡끝 %s · 침묵끝 %s · 칸 %d"
          % (fmt(data["duration"]), fmt(data["origEnd"]), fmt(data["gapEnd"]),
             len(data["blocks"])))
    print("   축 %s · 독 %s" % ("OK" if ok_axis else "실패!", "OK" if ok_dock else "실패!"))
    if not (ok_axis and ok_dock):
        sys.exit(1)


if __name__ == "__main__":
    main()
