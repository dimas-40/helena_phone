#!/usr/bin/env python3
"""곡 페이지를 폰 폭에서 실제로 열어본다. 눈으로만 보지 않고 숫자로 확인한다.

    python3 scripts/pd_check_pages.py midi_lane/pd/_localtest 8791
    python3 scripts/pd_check_pages.py . 0 --live      # 라이브 parksy.kr 검사
    python3 scripts/pd_check_pages.py midi_lane/pd/_localtest 8791 --only=18,46

전편 검사는 46편 × 4해상도라 오래 걸린다. 쪽지 한 장을 고친 뒤 그 곡만 보려면
--only=NN,NN 을 쓴다. **다만 이때 마지막 줄은 '전부 통과'가 아니라 '고른 N편 통과'다** —
부분 검사를 전편 검사로 오해하지 않게 그렇게 적는다.

검사: 콘솔 에러 / 가로 넘침 / 독 높이·칩 줄바꿈 / 노트 로드 수 / barhint 문구 /
      타임라인 클릭 이동 / 감정 수레바퀴 하이라이트 / 폰에서 칸 누르기.

⚠️ 로컬 검사에는 **Range 를 지원하는 서버**가 필요하다. 파이썬 기본 핸들러는
   항상 200 을 돌려주고, 그러면 `audio.seekable` 이 비어서 `currentTime = X` 가
   조용히 무시된다 — 라이브(GitHub Pages)는 멀쩡한데 로컬만 실패한다.
   그래서 아래 Q 핸들러가 206 을 직접 만든다.
"""
import http.server
import os
import sys
import threading
import functools
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PORT = int(sys.argv[2] if len(sys.argv) > 2 else 8791)
LIVE = "--live" in sys.argv
BASE = "https://parksy.kr/channel/musician/piano"
_LANE = Path("/root/work/midi_lane/pd")
# 곡 폴더만 — [0-9][0-9]- 로 좁히지 않으면 site/assets/ 가 곡으로 잡힌다.
PAGES = [(p.name[:2], p.name) for p in sorted(_LANE.glob("*/site/[0-9][0-9]-*/"))]
# --only=18,46 — 쪽지 한 장 고친 뒤 그 곡만 다시 본다. '=붙임' 꼴이라야 한다:
# positional 인자(ROOT·PORT)를 밀어내지 않으려고 값을 한 토큰에 담는다.
ONLY = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)
if ONLY:
    want = {s.strip().zfill(2) for s in ONLY.split(",") if s.strip()}
    PAGES = [p for p in PAGES if p[0] in want]
    if not PAGES:
        print("--only=%s 에 맞는 곡이 없다 (아는 곡: %s)"
              % (ONLY, " ".join(sorted(p.name[:2] for p in
                                      _LANE.glob("*/site/[0-9][0-9]-*/")))))
        sys.exit(2)
WIDTHS = [(360, 740), (414, 896), (768, 1024), (1280, 900)]


class Q(http.server.SimpleHTTPRequestHandler):
    """Range 를 지원한다 — 파이썬 기본 핸들러는 200 만 돌려준다.

    그러면 브라우저의 `audio.seekable` 이 비어서 `currentTime = X` 가
    **조용히 무시된다**. 로컬 검사만 실패하고 라이브(GitHub Pages)는 멀쩡한데,
    그 차이를 모르면 "클릭이 안 먹는다"는 없는 버그를 쫓게 된다. 실측으로 겪었다.
    """

    def log_message(self, *a):
        pass

    def end_headers(self):
        if not self._sent_ar:
            self.send_header("Accept-Ranges", "bytes")
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def send_head(self):
        self._sent_ar = False
        rng = self.headers.get("Range")
        if not rng or not rng.startswith("bytes="):
            return http.server.SimpleHTTPRequestHandler.send_head(self)
        path = self.translate_path(self.path)
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404)
            return None
        size = os.fstat(f.fileno()).st_size
        try:
            a, b = rng[6:].split("-", 1)
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if (a and b) else size - 1
        except ValueError:
            f.close()
            self.send_error(400)
            return None
        start = max(0, start)
        end = min(end, size - 1)
        if start > end:
            f.close()
            self.send_error(416)
            return None
        self.send_response(206)
        ctype = self.guess_type(path)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self._sent_ar = True
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f.seek(start)
        self._range_left = end - start + 1
        return f

    def copyfile(self, src, dst):
        left = getattr(self, "_range_left", None)
        if left is None:
            return http.server.SimpleHTTPRequestHandler.copyfile(self, src, dst)
        try:
            while left > 0:
                chunk = src.read(min(65536, left))
                if not chunk:
                    break
                dst.write(chunk)
                left -= len(chunk)
        except (ConnectionResetError, BrokenPipeError):
            # 오디오를 실어 보내는 중에 브라우저가 **정상적으로** 끊는 일이 있다
            # (탐색·재로드). 예전에는 이때 서버 스레드가 트레이스백을 쏟았고,
            # 그게 페이지 콘솔에 net::ERR_CONNECTION_ABORTED 로 뜨면서
            # **17호를 3개 해상도에서 없는 실패로 만들었다**(1280 에서는 ✓).
            # 끊긴 것은 끊긴 것일 뿐 결함이 아니므로 조용히 넘긴다.
            pass


def serve():
    h = functools.partial(Q, directory=str(ROOT))
    # ⚠️ 단일 스레드 서버로는 모자라다. 페이지 하나가 오디오 range 요청과
    # 문서 요청을 겹쳐 보내는데, 그걸 한 줄로 세우면 큰 음원(46호 9MB)에서
    # 연결이 끊기고 위의 가짜 ERR 로 이어진다. 스레드로 받는다.
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), h)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    if not LIVE:
        serve()
    bad = 0
    # 서버 뿌리에 없는 곡(보류 NN.HOLD · 쪽지 미작성)은 **검사 대상이 아니다.**
    # 배포 묶음에 들어가는지는 pd_build_deploy.sh 가 정하고, 여기서는 검사한 곡만
    # 문제로 센다 — 지금 채보 중인 곡 때문에 게이트가 영원히 빨간불이 되면
    # 사람이 검사기를 무시하게 된다(그게 진짜 손해다). 대신 **조용히 넘기지 않는다**:
    # 무엇을 못 봤는지 마지막에 이름으로 남긴다.
    absent = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for tag, slug in PAGES:
            url = ("%s/%s/" % (BASE, slug)) if LIVE else ("http://127.0.0.1:%d/%s/" % (PORT, slug))
            for w, h in WIDTHS:
                ctx = b.new_context(viewport={"width": w, "height": h},
                                    device_scale_factor=2, is_mobile=w < 700,
                                    has_touch=w < 700)
                pg = ctx.new_page()
                errs = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append("pageerror: %s" % e))
                pg.goto(url, wait_until="load")
                # #au 가 없으면 **여기서 멈추지 말고 이 곡을 실패로 보고한다.**
                # 2026-10-08: 서버 뿌리에 없는 곡(보류·쪽지 미작성)을 열면 404 페이지가
                # 뜨는데, 예전 코드는 그 자리에서 null.readyState 로 **예외를 던져
                # 검사 전체를 죽였다.** 게다가 죽은 곡이 아니라 그 **다음** 곡 이름을
                # 가리켜서(로그상 42호로 보였다) 없는 버그를 쫓게 만들었다 — 실제로는
                # 39호(보류)가 묶음에 없어서 난 것이었다. 이제 원인을 그 자리에서 말한다.
                if not pg.evaluate("() => !!document.getElementById('au')"):
                    absent.append(slug)
                    ctx.close()
                    continue
                # 파이썬 http.server 는 Range 를 지원하지 않는다 — 앞으로 감기는
                # 버퍼가 차야 먹는다. 브라우저에서 재생 준비를 기다린다.
                pg.evaluate("""() => new Promise(r => {
                  const a = document.getElementById('au');
                  if (a.readyState >= 3) return r();
                  a.preload = 'auto';
                  a.addEventListener('canplay', () => r(), {once: true});
                  setTimeout(r, 12000);
                })""")
                pg.wait_for_timeout(400)

                info = pg.evaluate("""() => {
                  const d = document.documentElement;
                  const au = document.getElementById('au');
                  const dock = document.getElementById('dock');
                  const bh = document.getElementById('barhint');
                  const wheel = document.getElementById('wheel');
                  const hot = wheel ? wheel.querySelector('.spoke.hot') : null;
                  let widest = 0, who = '';
                  document.querySelectorAll('body *').forEach(e => {
                    const r = e.getBoundingClientRect();
                    if (r.right > widest) { widest = r.right; who = e.tagName + '.' + (e.className||''); }
                  });
                  return {
                    notes: (window.PIECE && window.PIECE.notes.length) || 0,
                    blocks: (window.PIECE && window.PIECE.blocks.length) || 0,
                    audio: au ? au.duration : null,
                    dockh: dock ? Math.round(dock.getBoundingClientRect().height) : null,
                    barhint: bh ? bh.textContent.trim() : null,
                    wheelHere: wheel ? wheel.getAttribute('data-here') : null,
                    whichH: Math.round(document.getElementById('which').getBoundingClientRect().height),
                    whichTxt: document.getElementById('which').textContent,
                    wheelHot: hot ? [...wheel.querySelectorAll('.spoke')].indexOf(hot) : null,
                    spokes: wheel ? wheel.querySelectorAll('.spoke').length : 0,
                    hscroll: d.scrollWidth - d.clientWidth,
                    widest: Math.round(widest), who: who,
                    tlItems: document.querySelectorAll('.tl li').length,
                    barH: document.getElementById('bars') ?
                          Math.round(document.getElementById('bars').getBoundingClientRect().height) : null,
                    rollH: document.getElementById('roll') ?
                           Math.round(document.getElementById('roll').getBoundingClientRect().height) : null,
                  };
                }""")

                # 타임라인 클릭 → 이동.
                # ⚠️ `.tl` 은 0.5초 넘는 틈·저음 칸을 적어 둔 **손으로 쓴** 목록이다(자동 생성 아님).
                #    2026-10-09: 18호·46호에 이 목록이 없어 li.length 가 0 이 되었고,
                #    li[0] 이 undefined 라 target.getAttribute 에서 **검사 전체가 죽었다** —
                #    18호 이후 곡들의 판정을 아무도 못 봤다(46호는 그 전 세션에 이미 배포됐다).
                #    이제 없으면 **그 사실을 문제로 적고** 넘어간다.
                tl_n = pg.evaluate("() => document.querySelectorAll('.tl li').length")
                jumped = after = None
                if tl_n:
                    jumped = pg.evaluate("""() => {
                      const li = document.querySelectorAll('.tl li');
                      const target = li[Math.floor(li.length/2)];
                      const t = parseFloat(target.getAttribute('data-t'));
                      target.click();
                      return {t: t, at: document.getElementById('au').currentTime};
                    }""")
                    pg.wait_for_timeout(350)
                    after = pg.evaluate("() => document.getElementById('au').currentTime")
                ok_jump = bool(tl_n) and abs(after - jumped["t"]) < 0.5

                # 재현 구간으로 보내 칩의 **가장 긴 문구**("재현 · 살라만더")를 재본다.
                # 로드 직후엔 "원곡 · 이시자카"라 길이가 짧아서 넘침을 못 잡는다.
                tap = pg.evaluate("""() => {
                  const w = document.getElementById('wheel');
                  if (!w) return null;
                  const n = document.getElementById('wheelnote');
                  if (!n) return null;
                  const initial = n.textContent.trim();
                  const gs = [...w.querySelectorAll('.spoke')];
                  // 스포크가 둘 미만이면 고를 칸이 없다 — 여기서 죽지 말고 보고한다.
                  // 2026-10-09: 18호에서 bars 가 canvas 가 아니라 piano.js 가 첫 줄에서
                  // 예외를 던졌고(getContext is not a function), 바퀴가 아예 안 그려져
                  // 스포크 0개 → gs[-1].dispatchEvent 로 **검사가 또 죽었다.**
                  if (gs.length < 2) return {initial: initial, after: null, changed: false,
                                             spokes: gs.length};
                  const hot = gs.findIndex(x => x.classList.contains('hot'));
                  const other = gs.findIndex((x, i) => i !== hot && i !== 0);
                  if (other < 0) return {initial: initial, after: null, changed: false,
                                         spokes: gs.length};
                  gs[other].dispatchEvent(new MouseEvent('click', {bubbles: true}));
                  return {initial: initial, after: n.textContent.trim().slice(0, 20),
                          changed: n.textContent.trim() !== initial, spokes: gs.length};
                }""")
                if tap:
                    info["wheelNoteInit"] = tap["initial"]
                b_chip = pg.evaluate("""() => {
                  const a = document.getElementById('au'), w = document.getElementById('which');
                  a.currentTime = a.duration * 0.95;
                  w.className = 'b'; w.textContent = '재현 · 살라만더';
                  return {h: Math.round(w.getBoundingClientRect().height),
                          r: Math.round(w.getBoundingClientRect().right)};
                }""")
                info["whichH"] = b_chip["h"]

                flag = []
                if errs:
                    flag.append("ERR " + " | ".join(errs[:2]))
                if info["hscroll"] > 1:
                    flag.append("가로넘침 %dpx (%s)" % (info["hscroll"], info["who"]))
                if not info["notes"]:
                    flag.append("PIECE 없음")
                if not info["barhint"]:
                    flag.append("barhint 빈값")
                if info["spokes"] == 0:
                    # #roll/#bars 가 <canvas> 가 아니면 piano.js 가 첫 줄에서 죽고
                    # 바퀴가 아예 안 그려진다 — 그때 여기서 이름을 붙여 준다.
                    flag.append("바퀴 스포크 0개 — piano.js 가 중간에 죽었다")
                if not ok_jump:
                    flag.append("타임라인(.tl) 없음" if not tl_n
                                else "클릭이동 실패 %.2f→%.2f" % (jumped["t"], after))
                if w < 700 and info["dockh"] and info["dockh"] > h * 0.3:
                    flag.append("독 %.0fpx 과대" % info["dockh"])
                if w < 700 and info["whichH"] > 30:
                    flag.append("독 칩 %dpx — 줄바꿈(%s)" % (info["whichH"], info["whichTxt"]))
                if tap and tap["spokes"] >= 2:
                    if not tap["changed"]:
                        flag.append("휠 칸을 눌러도 설명이 안 바뀐다")
                    if w < 700 and "눌러보세요" not in tap["initial"]:
                        flag.append("폰인데 '마우스를 올려보세요' (%s)" % tap["initial"][:24])
                if info["spokes"] and (info["wheelHere"] is None
                                       or info["wheelHot"] != int(info["wheelHere"])):
                    flag.append("휠 하이라이트 %s≠%s (data-here 누락?)"
                                % (info["wheelHot"], info["wheelHere"]))
                if flag:
                    bad += 1
                print("%s %s %4dx%-4d notes=%-4d blocks=%-3d dock=%-4s barhint=%s"
                      % ("✗" if flag else "✓", tag, w, h, info["notes"], info["blocks"],
                         info["dockh"], (info["barhint"] or "")[:44]))
                print("      bars=%s roll=%s tl=%d wheel=%s(hot %s/%s) hscroll=%d widest=%d"
                      % (info["barH"], info["rollH"], info["tlItems"],
                         info["wheelHere"], info["wheelHot"], info["spokes"],
                         info["hscroll"], info["widest"]))
                if flag:
                    print("      ⚠ " + " · ".join(flag))
                if (w, h) in ((360, 740), (1280, 900)):
                    out = "/root/work/midi_lane/pd/_shot_%s_%d.png" % (tag, w)
                    pg.screenshot(path=out, full_page=(w > 700))
                    print("      shot → %s" % out)
                ctx.close()
        b.close()
    if absent:
        uniq = sorted(set(absent))
        print("\n묶음에 없어 검사하지 못한 곡 %d:" % len(uniq))
        for s in uniq:
            print("  · %s" % s)
        print("  (보류 NN.HOLD 거나 쪽지(page.py)를 아직 안 쓴 곡이다 — 배포 묶음 "
              "`pd_build_deploy.sh` 출력과 대조할 것)")
    if bad:
        print("\n%s" % ("%d개 조합에서 문제" % bad
                        if not ONLY else "고른 %d편에서 %d개 조합 문제" % (len(PAGES), bad)))
    elif ONLY:
        # 부분 검사를 전편 검사로 읽으면 안 된다 — 그렇게 읽히지 않게 적는다.
        print("\n고른 %d편 통과 (%s) — ⚠️ 전편 검사가 아니다"
              % (len(PAGES), ONLY))
    else:
        print("\n전부 통과")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
