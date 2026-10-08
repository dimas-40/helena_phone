#!/usr/bin/env python3
"""48칸 URL 목록을 다시 만든다 — **한 줄씩 실제로 두드려 본 뒤에** 적는다.

    python3 scripts/pd_url_list.py            # 만들기 (라이브 확인 포함, ~1분)
    python3 scripts/pd_url_list.py --dry      # 파일은 안 쓰고 화면에만

왜 스크립트인가: 손으로 적은 목록이 **낡아서 41개라고 적힌 동안 실제로는 45개**였다
(2026-10-09). 목록의 요점은 "이 주소가 진짜 열리는가"이므로, 코드를 확인하지 않고
적은 주소는 **없는 페이지를 광고하는 것**과 같다.

곡 목록의 정본은 `scripts/pd_dashboard.py` 의 QUEUE 다 — 여기서 베껴 적지 않는다.
보류 칸도 표식 파일(`midi_lane/pd/*/NN.HOLD`)에서 읽는다.
손으로 쓴 살아 있는 주석(`   ↳ …`)은 **옛 파일에서 골라 와 그 곡 아래에 그대로 둔다.**
"""
import importlib.util
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://parksy.kr/channel/musician/piano"
OUT = Path("/root/work/_notebook/pd48-url-list_Claude.txt")
DASH = Path("/root/work/scripts/pd_dashboard.py")


def code_of(url):
    """URL 이 열리는지 코드로 답한다. 모르면 예외 이름을 그대로 적는다."""
    req = urllib.request.Request(url + "/", method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)


def keep_notes(path):
    """옛 파일의 `   ↳ …` 주석을 번호별로 살려 온다(우리가 손으로 쓴 기록이다).

    ⚠️ 주석이 **곡 머리줄 바로 아래** 있을 수도 있고(사람이 그렇게 적었을 때),
    **URL 줄 아래** 있을 수도 있다(이 스크립트가 쓰는 순서). 위로 두 줄까지 훑어
    곡 머리줄을 찾는다 — 한 가지 순서만 가정했다가 주석 두 개를 통째로 날렸다.
    """
    notes = {}
    if not path.is_file():
        return notes
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(lines):
        if not l.strip().startswith("↳"):
            continue
        for j in (i - 1, i - 2):
            if j >= 0 and " · " in lines[j] and lines[j][:1].isdigit():
                notes[lines[j].split(" · ")[0].strip()] = l
                break
    return notes


def main():
    spec = importlib.util.spec_from_file_location("dash", DASH)
    dash = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dash)

    notes = keep_notes(OUT)
    out = ["박씨 렌더링 — 퍼블릭 도메인 피아노 48칸 · URL 전량",
           "대시보드: %s/" % BASE,
           "=" * 76, ""]
    live, hold, none = [], [], []
    for no, title, meta, cell, slug in dash.QUEUE:
        if no in dash.HOLD:
            hold.append((no, title, meta, cell, dash.HOLD[no]))
        elif slug:
            live.append((no, title, meta, cell, slug, code_of("%s/%s" % (BASE, slug))))
        else:
            none.append((no, title, meta, cell))

    out.append("■ 지금 쓰는 링크 — %d개 (전부 두드려서 확인한 코드)" % len(live))
    out.append("-" * 74)
    for no, title, meta, cell, slug, code in live:
        if code != 200:
            out.append("%s · %s · %s (%s)  ⚠️ HTTP %s" % (no, cell, title, meta, code))
        else:
            out.append("%s · %s · %s (%s)" % (no, cell, title, meta))
        out.append("   %s/%s" % (BASE, slug))
        if no in notes:
            out.append(notes[no])
    out.append("")
    out.append("■ 보류 — %d개 (표식 파일 NN.HOLD 가 있는 칸. **라이브에 없어야 정상**)"
               % len(hold))
    out.append("-" * 74)
    for no, title, meta, cell, reason in hold:
        out.append("%s · %s · %s (%s)" % (no, cell, title, meta))
        out.append("   ⛔ %s" % reason)
    out.append("")
    out.append("■ 페이지 미제작 — %d개" % len(none))
    for no, title, meta, cell in none:
        out.append("%s · %s · %s (%s)" % (no, cell, title, meta))
    out.append("")
    out.append("생성: 스크립트 `scripts/pd_url_list.py` · 곡 정본은 `scripts/pd_dashboard.py` QUEUE.")
    out.append("      링크는 **한 줄씩 실제로 두드려** HTTP 코드를 확인한 것이다 — 지어낸 주소는 없다.")
    out.append("      보류 칸은 `midi_lane/pd/*/NN.HOLD` 에서 읽는다. 라이브에 있으면 안 된다")
    out.append("      (`scripts/pd_check_live.py` 가 그걸 검사한다).")

    bad = [x for x in live if x[5] != 200]
    print("링크 %d(200 아님 %d) · 보류 %d · 미제작 %d"
          % (len(live), len(bad), len(hold), len(none)))
    for x in bad:
        print("  ⚠️ %s → HTTP %s" % (x[4], x[5]))
    if "--dry" in sys.argv:
        print("\n".join(out))
        return 1 if bad else 0
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("→ %s (%d 줄)" % (OUT, len(out)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
