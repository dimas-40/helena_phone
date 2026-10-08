#!/usr/bin/env python3
"""라이브 전수 점검 — 곡마다 쪽지·data·그림·음원이 200이고 **바이트가 로컬과 같은지**.

    python3 scripts/pd_check_live.py

왜 필요한가: 쪽지가 떴는데 그림 한 장이 404인 페이지는 **눈으로 보면 안다고 착각한다**
(스크롤을 안 내려가면 안 보인다). 그래서 파일 단위로 로컬 크기와 견준다.

그리고 이 검사가 실제로 잡은 것 — 2026-10-09:
  **23호가 `23.HOLD` 표식 없이 배포 묶음에 들어가 라이브에 있었다.** 게다가 그 쪽지는
  피아노 채보인데 실린 음원은 **옛 현악 녹음**(9,177,837B ↔ 새 피아노 6,903,873B)이었다.
  Boss 가 "바이올린 들어가 있잖아"라고 지적한 그 소리가 라이브에서 나오고 있었던 것이다.
  그래서 여기서 **보류 곡은 라이브에 '없어야' 통과**로 본다(있으면 ✗).

크기는 HEAD 의 ETag 뒤 16진 조각(`<mtime>-<size>`)에서 읽는다 — Content-Length 를
안 주는 응답이 있어서다. 46호 음원(9MB)을 46번 받아오지 않으려는 이유도 있다.
"""
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://parksy.kr/channel/musician/piano"
LANE = Path("/root/work/midi_lane/pd")


def size_of(url):
    """(HTTP 코드, 크기 또는 None). HEAD 가 막히면 Range 로 받아 본다."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, cl = r.status, r.headers.get("Content-Length")
            et = r.headers.get("ETag") or ""
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, str(e)
    if code != 200:
        return code, None
    if cl:
        return code, int(cl)
    m = re.match(r'W?"[0-9a-f]+-([0-9a-f]+)"', et)
    return code, (int(m.group(1), 16) if m else None)


def main():
    songs = {}
    for d in sorted(LANE.glob("[0-9][0-9]-*/site/[0-9][0-9]-*/")):
        songs[d.name] = d
    # 보류는 **파일에서 읽는다**(손으로 적은 목록이 아니다 — 그게 23호 사고의 원인이었다).
    held = {f.stem[:2] for f in LANE.glob("[0-9][0-9]-*/*.HOLD")}
    bad = []
    n = 0
    for slug, d in sorted(songs.items()):
        no = slug[:2]
        if no in held:
            continue
        if not (d / "index.html").is_file():
            continue                      # 쪽지를 아직 안 쓴 곡 — 배포 묶음에도 없다
        files = ["index.html", "data.js"]
        for sub in ("img", "audio"):
            sd = d / sub
            if sd.is_dir():
                files += ["%s/%s" % (sub, f.name) for f in sorted(sd.iterdir())
                          if f.is_file()]
        miss, diff = [], []
        for rel in files:
            local = (d / rel).stat().st_size
            code, got = size_of("%s/%s/%s" % (BASE, slug, rel))
            n += 1
            if code != 200:
                miss.append("%s(%s)" % (rel, code))
            elif got is not None and got != local:
                diff.append("%s 라이브 %d ↔ 로컬 %d" % (rel, got, local))
        if miss or diff:
            bad.append(slug)
        print("%s %s  파일 %d" % ("✗" if (miss or diff) else "✓", slug, len(files)),
              flush=True)
        for m in miss:
            print("      없음/오류 %s" % m, flush=True)
        for x in diff:
            print("      크기 다름 %s" % x, flush=True)

    # 보류 곡은 **라이브에 없어야 한다.** 표식 파일을 만들었는데 묶음에서 안 빠지거나,
    # 이미 올라간 것이 안 내려갔으면 여기서 잡힌다.
    for no in sorted(held):
        # 쪽지를 아직 안 쓴 보류 곡(30호)은 site/NN-*/ 자체가 없다. 그래도 **폴더 이름으로
        # 원격을 두드려 본다** — 안 그러면 이 곡만 검사에서 조용히 빠진다.
        names = [d.name for d in LANE.glob("%s-*/site/%s-*/" % (no, no))] \
            or [d.name for d in LANE.glob("%s-*/" % no) if d.is_dir()]
        for name in names:
            code, _ = size_of("%s/%s/index.html" % (BASE, name))
            n += 1
            if code == 200:
                bad.append(name + "(보류인데 라이브에 있다)")
                print("✗ %s — 보류인데 라이브에 있다" % name, flush=True)
            else:
                print("✓ %s — 보류, 라이브에 없음(%s)" % (name, code), flush=True)

    print("\n검사한 파일 %d · 문제 있는 곡 %d" % (n, len(bad)), flush=True)
    for s in bad:
        print("  · %s" % s, flush=True)
    print("전부 일치" if not bad else "위 곡들을 확인할 것", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
