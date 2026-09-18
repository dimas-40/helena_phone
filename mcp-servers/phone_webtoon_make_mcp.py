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
# ⚠️ 작동 원칙 (Boss 2026-09-13 — 절대 오버라이드 금지)
#   Claude = 실행만. 판단·드라이빙 금지. 방향·판단은 전부 Boss가 정한다.
import json, sys, os, glob, shutil, subprocess, time
from pathlib import Path

SERVER = "phone-webtoon-make"
VER = "1.1.0"

GALLERY = "/sdcard/DCIM/Drawing assist"
WEBTOON_DIR = "/root/work/parksy-webzine/webtoon"
ASSET_DIR = os.path.join(WEBTOON_DIR, "cuts")
DISCLAIMER_CROP = 0.08  # 삼성 AI 경고문(하단 텍스트) — 하단 8% 크롭 (규격화)
VISION_SCRIPT = "/root/vision/see.py"  # BLIP 눈 (영구 설치)
TG_SCRIPT = "/root/work/tg.sh"

# ── 필름 스프로켓홀 (Boss 2026-09-13, 변수화) ──
FILM_STRIP_W = 52
FILM_HOLE_W = 24
FILM_HOLE_H = 18
FILM_HOLE_GAP = 30
FILM_STRIP_COLOR = (14, 26, 20)
FILM_HOLE_COLOR = (236, 231, 208)

# ── 식자 말풍선 위치/크기 (변수화) ──
BUBBLE_LEFT = 60
BUBBLE_RIGHT = 60
BUBBLE_BOTTOM = 14
BUBBLE_FONT = 13

# ── 인터랙티브 (Boss 2026-09-13, 셀프컨테인드 — 모바일 표준) ──
INTERACTIVE_CSS = """
/* ★ 기본값은 '보인다' — JS가 살아있을 때만(html.wt-js) 애니메이션.
   티스토리는 본문 <script>를 지우므로, 스크립트가 없으면 정적으로 다 보인다. */
.wt-bubble{transition:opacity .4s;will-change:transform}
.wt-char{display:inline-block}
.wt-js .wt-bubble{opacity:0}
.wt-js .wt-bubble.wt-in{opacity:1}
.wt-js .wt-char{opacity:0}
.wt-js .wt-in .wt-char{animation:wttype .4s cubic-bezier(.34,1.56,.64,1) forwards}
@keyframes wttype{0%{opacity:0;transform:translateY(6px) scale(1.4)}100%{opacity:1;transform:translateY(0) scale(1)}}
.wt-bubble:hover{box-shadow:0 10px 32px rgba(0,0,0,.72),0 0 0 2px rgba(160,138,76,.55)}
"""
INTERACTIVE_JS = """<script>
(function(){document.documentElement.classList.add('wt-js');var bs=document.querySelectorAll('.wt-bubble');if(!bs.length)return;for(var i=0;i<bs.length;i++){var b=bs[i];var t=b.textContent;b.innerHTML=t.split('').map(function(c,j){return '<span class="wt-char" style="animation-delay:'+(j*0.04).toFixed(3)+'s">'+(c===' '?'&nbsp;':c)+'</span>';}).join('');}var shakes={};for(var k=0;k<bs.length;k++){(function(el){el.addEventListener('click',function(){shakes[el]=Date.now()+450;});})(bs[k]);}if('IntersectionObserver'in window){var io=new IntersectionObserver(function(es){for(var j=0;j<es.length;j++){if(es[j].isIntersecting)es[j].target.classList.add('wt-in');else es[j].target.classList.remove('wt-in');}},{threshold:0.3});for(var l=0;l<bs.length;l++)io.observe(bs[l]);}else{for(var m=0;m<bs.length;m++)bs[m].classList.add('wt-in');}function tick(){var now=Date.now(),vh=innerHeight;for(var j=0;j<bs.length;j++){var b=bs[j];if(!b.classList.contains('wt-in'))continue;var r=b.getBoundingClientRect(),c=r.top+r.height/2,d=Math.abs(c-vh/2);var kk=Math.max(0,1-d/(vh/2)),s=0.95+kk*0.13;var sway=Math.sin(now/800+j*1.3)*5;var sh=0;if(shakes[b]&&now<shakes[b]){var tt=(shakes[b]-now)/450;sh=Math.sin(now/40)*9*tt;}b.style.transform='scale('+s.toFixed(3)+') translateX('+(sway+sh).toFixed(1)+'px)';}requestAnimationFrame(tick);}requestAnimationFrame(tick);})();
</script>"""
# ── Tistory Interactive Comic Spec v1 — 제한 규격 (제약이 연출 문법) ──
#   NO external dep · NO WebGL · NO framework.
#   YES: vanilla JS + rAF + IntersectionObserver + DOM + CSS transform/filter/clip-path/mask + SVG + scroll/touch/pointer.
SPEC = {
    "runtime": "vanilla-js-only",
    "objects": {
        "image": "사진 → 확대/이동/회전/투명/blur/clip/mask",
        "text": "문장 → 등장/이동/opacity/scale/시간차",
        "info": "숫자 → 카운트업/막대성장/SVG/그래프 reveal",
    },
    "primitives": {
        "transform": ["translate", "scale", "rotate", "skew", "perspective"],
        "filter": ["blur", "brightness", "contrast", "saturate", "hue-rotate", "grayscale", "sepia", "invert"],
        "clip": ["inset", "circle", "polygon"],
        "mask": ["gradient", "image"],
        "opacity": True,
    },
    "triggers": ["scroll", "touch", "pointer", "time"],
}

# ── 연출 DSL: 객체 타임라인 (기본값) ──
#   p=스크롤 진행(0~1), s=scale, r=rotate(deg), x/y=translate(px), o=opacity,
#   blur/bright/contr/sat/hue/gray=filter, clip=css clip-path, mask=css mask
DEFAULT_TL = ('[{"p":0,"s":1,"r":-1.5,"o":0.3,"blur":2,"y":20},'
              '{"p":0.5,"s":1.12,"r":0,"o":1,"blur":0,"y":0},'
              '{"p":1,"s":1.35,"r":2.5,"o":1,"blur":0,"y":-10}]')

# 숏 타입별 연출 타임라인 — 같은 이미지에 "카메라 워킹"을 부여 (편집 원자 조합)
SHOT_TIMELINES = {
    # 만점 연출 — 5키프레임, 부드럽고 길게 (트리거는 앞당겨져 있음)
    "establishing": '[{"p":0,"s":1.03,"r":0,"o":0,"blur":3,"y":34},{"p":0.25,"s":1.07,"o":0.55,"blur":1.5,"y":18},{"p":0.5,"s":1.13,"o":1,"blur":0,"y":4},{"p":0.78,"s":1.19,"o":1,"y":-7},{"p":1,"s":1.24,"o":1,"y":-12}]',
    "over_shoulder": '[{"p":0,"s":1.13,"r":-2.5,"o":0,"y":52},{"p":0.3,"s":1.08,"r":-1.6,"o":0.7,"y":26},{"p":0.6,"s":1.03,"r":-0.6,"o":1,"y":6},{"p":0.85,"s":1.0,"r":0,"o":1,"y":-9},{"p":1,"s":1.0,"r":0.6,"o":1,"y":-15}]',
    "insert": '[{"p":0,"s":1.36,"o":0.25,"blur":6,"reveal":0.08},{"p":0.3,"s":1.22,"o":0.65,"blur":2,"reveal":0.5},{"p":0.6,"s":1.1,"o":1,"blur":0,"reveal":1},{"p":0.85,"s":1.02,"o":1,"reveal":1},{"p":1,"s":1.0,"o":1,"reveal":1}]',
    "extreme": '[{"p":0,"s":1.5,"r":-3,"o":0.08,"gray":1,"blur":6},{"p":0.3,"s":1.34,"r":-2,"o":0.5,"gray":0.7,"blur":2.5},{"p":0.55,"s":1.17,"r":0,"o":1,"gray":0.2,"blur":0},{"p":0.8,"s":1.06,"r":1.1,"o":1,"gray":0},{"p":1,"s":1.0,"r":1.6,"o":1,"gray":0}]',
    "long": '[{"p":0,"s":1.05,"o":0.3,"y":25},{"p":1,"s":1.15,"o":1,"y":0}]',
    "medium": '[{"p":0,"s":1.15,"o":0.3,"y":15},{"p":1,"s":1.0,"o":1,"y":0}]',
    "closeup": '[{"p":0,"s":1.25,"o":0.2,"blur":4},{"p":1,"s":1.0,"o":1,"blur":0}]',
    "pov": '[{"p":0,"s":1.0,"r":0,"o":0.3},{"p":1,"s":1.15,"r":1.5,"o":1}]',
    "reaction": '[{"p":0,"s":1.0,"o":0.3,"r":-1},{"p":1,"s":1.1,"o":1,"r":0}]',
    "cutaway": '[{"p":0,"s":1.2,"o":0.2,"blur":3},{"p":1,"s":1.0,"o":1,"blur":0}]',
}
IMAGE_JS = """<script>
/* 연출 엔진(SPEC v1) — [data-tl] 타임라인 재생. s/r/x/y=transform, o=opacity, blur/bright/contr/sat/hue/gray/sepia/invert=filter, clip, mask */
(function(){var els=document.querySelectorAll('[data-tl]');if(!els.length)return;
function lerp(a,b,t){return a+(b-a)*t;}
function at(tl,k){if(k<=tl[0].p)return tl[0];for(var i=0;i<tl.length-1;i++){var a=tl[i],b=tl[i+1];if(k>=a.p&&k<=b.p){var t=(k-a.p)/(b.p-a.p),o={};for(var key in a){if(key==='p')continue;o[key]=(typeof a[key]==='number'&&typeof b[key]==='number')?lerp(a[key],b[key],t):b[key];}return o;}}return tl[tl.length-1];}
function apply(el,st){el.style.transform='scale('+(st.s||1)+') rotate('+(st.r||0)+'deg) translate('+(st.x||0)+'px,'+(st.y||0)+'px)';if(st.o!=null)el.style.opacity=st.o;var f=[];if(st.blur!=null)f.push('blur('+st.blur+'px)');if(st.bright!=null)f.push('brightness('+st.bright+')');if(st.contr!=null)f.push('contrast('+st.contr+')');if(st.sat!=null)f.push('saturate('+st.sat+')');if(st.hue!=null)f.push('hue-rotate('+st.hue+'deg)');if(st.gray!=null)f.push('grayscale('+st.gray+')');if(st.sepia!=null)f.push('sepia('+st.sepia+')');if(st.invert!=null)f.push('invert('+st.invert+')');if(f.length)el.style.filter=f.join(' ');if(st.reveal!=null)el.style.clipPath='inset(0 0 '+((1-st.reveal)*100).toFixed(1)+'% 0)';else if(st.clip)el.style.clipPath=st.clip;if(st.mask)el.style.webkitMaskImage=el.style.maskImage=st.mask;}
function tick(){var vh=innerHeight;for(var i=0;i<els.length;i++){var el=els[i],tgt=el.querySelector('img')||el;var r=el.getBoundingClientRect();var k=Math.max(0,Math.min(1,(vh-r.top)/(vh*0.8)));var tl;try{tl=JSON.parse(el.getAttribute('data-tl'));}catch(e){continue;}apply(tgt,at(tl,k));}requestAnimationFrame(tick);}
requestAnimationFrame(tick);})();
</script>"""
INFO_JS = """<script>
/* INFO 객체 연출 — 카운트업 + 막대성장 + 탭 버튼 (SPEC v1: info object) */
(function(){
function ease(p){return p<.5?2*p*p:-1+(4-2*p)*p;}
var ioN=null,ioB=null;
if('IntersectionObserver'in window){
  ioN=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target,t=parseInt(el.getAttribute('data-count'),10),s=el.getAttribute('data-suffix')||'',d=1200,t0=null;function st(ts){if(!t0)t0=ts;var p=Math.min(1,(ts-t0)/d);el.textContent=Math.round(t*ease(p))+s;if(p<1)requestAnimationFrame(st);}requestAnimationFrame(st);ioN.unobserve(el);}});},{threshold:0.5});
  ioB=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.style.width=e.target.getAttribute('data-bar')+'%';ioB.unobserve(e.target);}});},{threshold:0.5});
}
var nums=document.querySelectorAll('[data-count]');nums.forEach(function(n){if(ioN)ioN.observe(n);else n.textContent=n.getAttribute('data-count')+(n.getAttribute('data-suffix')||'');});
var bars=document.querySelectorAll('[data-bar]');bars.forEach(function(b){if(ioB)ioB.observe(b);else b.style.width=b.getAttribute('data-bar')+'%';});
var tabs=document.querySelectorAll('[data-tab]');tabs.forEach(function(t){t.addEventListener('click',function(){var g=t.getAttribute('data-group')||'g';document.querySelectorAll('[data-tab][data-group="'+g+'"]').forEach(function(x){x.style.background='rgba(160,138,76,.15)';x.style.color='#e9e5cf';});t.style.background='#a08a4c';t.style.color='#0c1710';document.querySelectorAll('[data-panel="'+g+'"]').forEach(function(p){p.style.display='none';});var tgt=document.querySelector('[data-panel="'+g+'"][data-pane="'+t.getAttribute('data-pane')+'"]');if(tgt)tgt.style.display='block';});});
})();
</script>"""


# ── BLIP 비전 (눈) — 강제 사용 ──
def _vision(image_path):
    """BLIP 캡션 + 모델 없는 특징을 같이 본다. 반환: {caption, features, blind}."""
    res = {"caption": "", "features": {}, "blind": False}
    if not os.path.isfile(VISION_SCRIPT):
        res["caption"] = "BLIND"
        res["blind"] = True
        return res
    try:
        r = subprocess.run(["/usr/bin/python3", VISION_SCRIPT, image_path],
                           capture_output=True, text=True, timeout=180)
        for line in (r.stdout or "").splitlines():
            line = line.strip()
            if not line or "\t" not in line:
                continue
            parts = line.split("\t")
            kind = parts[0]
            if kind == "CAPTION":
                res["caption"] = parts[-1].strip()
            elif kind == "SEE":
                try:
                    res["features"] = json.loads(parts[-1])
                except Exception:
                    pass
            elif kind.startswith("BLIND"):
                res["blind"] = True
                res["caption"] = "BLIND"
                try:
                    res["features"] = json.loads(parts[-1])
                except Exception:
                    pass
        if not res["caption"] and not res["blind"]:
            res["caption"] = "BLIND"
            res["blind"] = True
    except Exception as e:
        res["caption"] = f"BLIND({type(e).__name__})"
        res["blind"] = True
    return res


def _visible_keywords(caption, maxn=6):
    """BLIP 캡션에서 '보이는 사물' 단어 추출 (불용어 제거)."""
    import re
    stop = {"a", "the", "of", "in", "on", "with", "and", "to", "an", "is", "are",
            "photo", "drawing", "comic", "close", "up", "that", "for", "by", "at",
            "man", "woman", "person", "people"}
    words = [w for w in re.findall(r"[A-Za-z]+", caption or "") if w.lower() not in stop]
    seen, out = set(), []
    for w in words:
        wl = w.lower()
        if wl not in seen:
            seen.add(wl)
            out.append(wl)
    return out[:maxn]


def _feature_notes(feats):
    """모델 없는 특징 → 연출 노트 (조명·톤·품질 경고)."""
    notes = []
    if not feats or "err" in feats:
        return notes
    if feats.get("dark", 0) >= 0.4:
        notes.append("암전 컷 — 밝은 말풍선·SFX 강조")
    if feats.get("warm", 0) > feats.get("cool", 0) + 0.05:
        notes.append("황동·노을 톤")
    elif feats.get("cool", 0) > feats.get("warm", 0) + 0.05:
        notes.append("차가운 톤")
    if feats.get("sat", 0) < 0.08:
        notes.append("저채도(무채색)")
    if feats.get("edge", 0) < 0.015:
        notes.append("디테일 낮음(흐림/백지) 주의")
    return notes


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


# ── 연출 기법: 시네마틱 숏 타입 (영화 문법 → 세로 스크롤 웹툰) ──
#   한 컷 = 한 장의 그림(만화)이 아니라 "하나의 카메라 쇼트"(영화).
#   face=True 일 때만 '박씨 얼굴 합성'을 쓴다 — 얼굴은 연출 자원.
SHOTS = {
    "establishing":  {"ko": "설정 숏",      "camera": "와이드, 장소 전체",        "face": False, "motion": "공간을 세운다. 인물은 작거나 없음."},
    "long":          {"ko": "롱 숏",        "camera": "전신",                    "face": False, "motion": "인물 전체. 배경과의 관계."},
    "medium":        {"ko": "미디엄 숏",    "camera": "허리 위 상반신",          "face": True,  "motion": "상반신. 표정이 읽히기 시작."},
    "closeup":       {"ko": "클로즈업",     "camera": "얼굴 또는 핵심 사물",     "face": True,  "motion": "얼굴/사물. 감정이 선다."},
    "extreme":       {"ko": "극클로즈업",   "camera": "눈·손·질감 디테일",       "face": True,  "motion": "디테일. 가장 세게."},
    "over_shoulder": {"ko": "오버숄더",     "camera": "어깨 너머 시점",          "face": False, "motion": "뒤에서 바라본 시점. 대상에 접근."},
    "pov":           {"ko": "POV",          "camera": "1인칭 시점",              "face": False, "motion": "인물의 눈으로 본다."},
    "reaction":      {"ko": "리액션 숏",    "camera": "표정 반응",               "face": True,  "motion": "표정 반응."},
    "insert":        {"ko": "인서트 숏",    "camera": "사물 인서트",             "face": False, "motion": "사물을 삽입. 손·오브제."},
    "cutaway":       {"ko": "컷어웨이",     "camera": "주변 풍경",               "face": False, "motion": "주변으로 잠깐."},
}

# 4컷 기본 진행: 설정 → 접근 → 행동 → 결정 (얼굴은 마지막에만 공개)
SHOT_SEQ = ["establishing", "over_shoulder", "insert", "extreme"]


# BLIP 영문 캡션 → 한글 사물 (최소 매핑). 없는 단어는 드롭.
KO = {
    "man": "남자", "woman": "여자", "person": "사람", "people": "사람들",
    "standing": "서 있는", "sitting": "앉은", "walking": "걷는",
    "bookcase": "책장", "bookshelf": "책장", "library": "서재", "book": "책",
    "robot": "로봇", "giant": "거대한", "gun": "총", "hand": "손",
    "table": "테이블", "desk": "책상", "chair": "의자", "room": "방",
    "window": "창문", "mirror": "거울", "glass": "유리", "face": "얼굴",
    "hair": "머리", "glasses": "안경", "street": "거리", "building": "건물",
    "car": "차", "food": "음식", "flower": "꽃", "tree": "나무",
}


def _design(title, body, vision):
    """연출 기획 — 눈(BLIP)이 본 것 + 텍스트 gist를 실제로 반영한 4컷 설계.

    2026-09-16 반영(Boss 지적 "눈 달아만 놓고 연출에 안 씀"): vision(caption+features)을
    컷 프롬프트에 실제로 삽입. 이전엔 vision 파라미터가 표시용일 뿐 설계에 0% 반영됐다.
    """
    words = [w.strip(".,!?") for w in body.split() if not w.startswith("--") and len(w) > 1][:12]
    gist = " ".join(words[:6]) if words else title[:40]
    hook = words[0] if words else "이야기"

    cap = (vision or {}).get("caption", "") or ""
    feats = (vision or {}).get("features", {}) or {}
    blind = bool((vision or {}).get("blind"))
    visible = [KO.get(w) for w in _visible_keywords(cap) if w in KO]
    vdesc = " ".join(visible) if visible else ""
    notes = _feature_notes(feats)
    note_str = " / ".join(notes) if notes else ""

    core = []
    for skey in SHOT_SEQ:
        sh = SHOTS[skey]
        face = "박씨 얼굴 합성, " if sh["face"] else ""
        prompt = f"{face}{sh['camera']}, {gist} 주제, 다크그린 황동 조명"
        core.append((sh["ko"], sh["motion"], prompt))
    cuts = []
    for i, (sc, mo, pr) in enumerate(core):
        if vdesc:
            pr = f"{pr}, 보이는 사물: {vdesc}"
        cuts.append({"n": i + 1, "scene": sc, "motion": mo,
                     "shot": SHOT_SEQ[i], "prompt": _fit100(pr)})
    return {"title": f"웹툰 — {title}", "source_gist": gist,
            "vision": {"caption": cap, "features": feats, "blind": blind},
            "visible": visible, "notes": note_str, "cuts": cuts}


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
    v = d.get("vision", {}) or {}
    cap = v.get("caption", "")
    feats = v.get("features", {}) or {}
    blind = v.get("blind", False)
    eye = "BLIND ⚠️" if blind else (cap or "(없음)")
    feat_str = ""
    if feats and "err" not in feats:
        feat_str = (f"b{feats.get('bright','?')} d{feats.get('dark','?')} "
                    f"w{feats.get('warm','?')}/c{feats.get('cool','?')} "
                    f"s{feats.get('sat','?')} e{feats.get('edge','?')}")
    lines = [f"🎬 폰 웹툰 메이크 — 연출 기획", "",
             f"소스: {d['title']}", f"눈(BLIP): {eye}", ""]
    if feat_str:
        lines.append(f"특징: {feat_str}")
    if d.get("notes"):
        lines.append(f"연출노트: {d['notes']}")
    if d.get("visible"):
        lines.append(f"보이는 사물: {' '.join(d['visible'])}")
    lines += ["", "━━━━━━━━━━━━━━━━"]
    for c in d["cuts"]:
        lines += [f"[컷 {c['n']}] {c['scene']}", f"몸동작: {c['motion']}",
                  f"프롬프트:", f"「{c['prompt']}」", ""]
    lines += ["━━━━━━━━━━━━━━━━", "갤러리(Drawing assist)에 프롬프트 붙여넣고 얼굴 합성 생성 → 저장하면 내가 식자+조립"]
    return "\n".join(lines)


# ── 툴 1: 연출 기획 ──
def webtoon_direct(source=None, captions=None):
    try:
        if not source:
            return {"ok": False, "error": "source 필요 (URL 또는 문서경로)"}
        title, body = _fetch_text(source)
        # ── 눈 탈부착: 작가(Boss)가 식자를 주면 BLIP 눈을 건너뛴다. 없으면 실험(BLIP). ──
        if captions is not None:
            vision = {"caption": "(작가 제공 — BLIP 생략)", "features": {}, "blind": False, "source": "author"}
        else:
            vision = {"caption": "", "features": {}, "blind": False}
            if source.startswith("http"):
                png = _screenshot(source)
                if not png:
                    return {"ok": False, "error": "스크린샷 실패 — 눈으로 못 봄"}
                vision = _vision(png)
                if vision.get("blind"):
                    return {"ok": False, "error": "BLIP 눈 없음(BLIND) — 슬라이드쇼 방지를 위해 중단",
                            "vision": vision}
            else:
                vision["caption"] = "(문서라 스크린샷 없음)"
        design = _design(title, body, vision)
        if captions is not None:
            design["captions"] = captions  # 작가 식자를 설계에 첨부
        msg = _format_telegram(design)
        tg = _tg_send(msg)
        return {"ok": True, "title": title, "vision": vision, "cuts": len(design["cuts"]),
                "telegram": tg, "design": design}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


# ── 툴 2: 식자·조립 ──
def webtoon_assemble(dialogue=None, captions=None, title="웹툰"):
    try:
        # ── 눈 탈부착(작가주의): 식자는 Boss(작가)가 직접 준다. BLIP는 webtoon_direct(실험)에서만. ──
        #   captions: list(컷 순서 1-based) 또는 dict("3"=컷번호 / "cut_01" / "cuts/cut_01.jpg")
        lines = captions if captions is not None else dialogue
        if lines is None:
            return {"ok": False, "error": "captions/dialogue 필요 (식자 리스트 또는 딕셔너리)"}
        pats = sorted(glob.glob(os.path.join(GALLERY, "*.jpg")) + glob.glob(os.path.join(GALLERY, "*.png")))
        if not pats:
            return {"ok": False, "error": f"갤러리에 컷 없음: {GALLERY}"}
        if isinstance(lines, dict):
            # n = 최대 숫자 키(컷 번호). 숫자 키 없으면 갤러리 전체(파일명 매핑용)
            nums = [int(k) for k in lines if str(k).isdigit()]
            n = max(nums) if nums else len(pats)
        else:
            n = len(lines)
        n = min(n, len(pats))
        pats = pats[-n:]  # 최신 n개를 생성 순서(오래된→최신)로 — 역순 버그 수정
        if isinstance(lines, dict):
            # dict → 컷 순서(1..n)로 해석. 매핑 없으면 빈 문자열(= 안 본 것, blind 유지)
            resolved = []
            for i in range(1, n + 1):
                c = (lines.get(str(i)) or lines.get(f"cut_{i:02d}")
                     or lines.get(f"cut_{i:02d}.jpg") or lines.get(f"cuts/cut_{i:02d}.jpg") or "")
                resolved.append(c)
            lines = resolved
        else:
            lines = list(lines)
        os.makedirs(ASSET_DIR, exist_ok=True)
        cut_rel = []
        for i in range(n):
            ext = os.path.splitext(pats[i])[1]
            dst = os.path.join(ASSET_DIR, f"cut_{i+1:02d}{ext}")
            _crop_disclaimer(pats[i], dst)
            _add_film_sprocket(dst)
            cut_rel.append(f"cuts/cut_{i+1:02d}{ext}")
        html = _compose(title, cut_rel, lines[:n])
        out = os.path.join(WEBTOON_DIR, "index.html")
        open(out, "w").write(html)
        return {"ok": True, "n_cuts": n, "html": out, "cuts": cut_rel, "eye": "author"}
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


def _add_film_sprocket(path):
    """필름 스프로켓홀 효과 — 좌우 다크그린 스트립 + 흰색 구멍 (Boss 2026-09-13)."""
    try:
        from PIL import Image, ImageDraw
        img = Image.open(path).convert('RGB')
        w, h = img.size
        new_w = w + 2 * FILM_STRIP_W
        out = Image.new('RGB', (new_w, h), FILM_STRIP_COLOR)
        out.paste(img, (FILM_STRIP_W, 0))
        d = ImageDraw.Draw(out)
        y = FILM_HOLE_GAP // 2
        while y + FILM_HOLE_H < h:
            cx_l = FILM_STRIP_W // 2; cx_r = new_w - FILM_STRIP_W // 2
            d.rectangle([cx_l - FILM_HOLE_W // 2, y, cx_l + FILM_HOLE_W // 2, y + FILM_HOLE_H], fill=FILM_HOLE_COLOR)
            d.rectangle([cx_r - FILM_HOLE_W // 2, y, cx_r + FILM_HOLE_W // 2, y + FILM_HOLE_H], fill=FILM_HOLE_COLOR)
            y += FILM_HOLE_GAP + FILM_HOLE_H
        out.save(path, quality=92)
    except Exception:
        pass


def _compose(title, cut_rel, dialogue):
    panels = []
    for i, (cut, text) in enumerate(zip(cut_rel, dialogue), 1):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tl = SHOT_TIMELINES.get(SHOT_SEQ[(i-1) % len(SHOT_SEQ)], DEFAULT_TL)
        tl_attr = tl.replace('"', '&quot;')
        panels.append(f'<section class="panel"><div class="cut" data-tl="{tl_attr}"><img src="{cut}" alt="컷 {i}"></div>'
                      f'<div class="cap wt-bubble"><span class="txt">{safe}</span></div></section>')
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — PARKSY 웹툰</title>
<style>:root{{--paper:#0c1710;--ink:#e9e5cf;--brass:#a08a4c}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font-family:"Nanum Myeongjo",serif;line-height:1.6}}
.wrap{{max-width:720px;margin:0 auto;padding:20px 16px 80px}}
.mast{{text-align:center;padding:18px 0 26px;border-bottom:1px solid rgba(160,138,76,.3)}}
.mast h1{{font-family:Georgia,serif;font-weight:900;font-size:26px}}.mast .sub{{font-size:11px;letter-spacing:.3em;color:var(--brass);margin-top:6px}}
.panel{{margin:26px 0}}.cut{{overflow:hidden;border-radius:4px;box-shadow:0 14px 30px rgba(0,0,0,.5)}}.cut img{{width:100%;display:block;will-change:transform,opacity}}
.cap{{margin:14px 0 0;background:rgba(233,229,207,.96);color:#1a120c;padding:12px 16px;border-radius:14px;font-size:{BUBBLE_FONT}px;font-weight:700;box-shadow:0 4px 14px rgba(0,0,0,.45);text-align:center}}
footer{{text-align:center;color:var(--brass);font-size:12px;letter-spacing:.2em;padding:30px 0}}{INTERACTIVE_CSS}</style></head><body>
<div class="wrap"><div class="mast"><h1>{title}</h1><div class="sub">PARKSY WEBTOON</div></div>
{''.join(panels)}<footer>PARKSY · 박씨 종합잡지사</footer></div>{INTERACTIVE_JS}{IMAGE_JS}</body></html>'''


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
