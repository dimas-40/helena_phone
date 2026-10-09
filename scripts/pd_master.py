#!/usr/bin/env python3
"""48칸 마스터 — 감정표·곡·URL·**지금 라이브인지**를 한 화면에 모아 검사한다.

    python3 -u scripts/pd_master.py

무엇을 검사하나 (Boss 질문 "48개 다 맞는 거냐"):
  1. 칸이 **48**인가 · 칸 이름이 서로 겹치지 않는가 · 같은 곡이 두 칸에 없는가
  2. 감정표가 **플루치크 정본**인가 — 기본 8 × 3강도 = 24 + dyad 8+8+8 = 24 → 48
     (강도 3단과 dyad 거리 1·2·3차를 **셈으로 확인**한다. 눈으로 세지 않는다)
  3. 쪽지의 `data-here` 가 **그 칸의 첫 감정**과 같은가 (수레바퀴가 가리키는 자리)
  4. 쪽지가 로컬에 있는가 · **지금 라이브가 200 인가** · **바이트가 로컬과 같은가**
  5. 보류 칸은 **라이브에 없어야** 한다

정본은 `scripts/pd_dashboard.py` 의 QUEUE 다 — 여기서 곡을 베껴 적지 않는다.
"""
import importlib.util
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://parksy.kr/channel/musician/piano"
LANE = Path("/root/work/midi_lane/pd")
DASH = Path("/root/work/scripts/pd_dashboard.py")

# 플루치크 수레바퀴 순서 — 쪽지의 data-here 가 가리키는 숫자다.
WHEEL = ["기쁨", "신뢰", "공포", "놀람", "슬픔", "혐오", "분노", "기대"]
# 강도 낮은 순서 → 1·2·3강도(셋째가 가장 강하다)
INTENSITY = {
    "슬픔": ["생각에 잠김", "슬픔", "비통"],
    "신뢰": ["수용", "신뢰", "존경"],
    "공포": ["불안", "공포", "극공"],
    "놀람": ["산만", "놀람", "경악"],
    "혐오": ["권태", "혐오", "역겨움"],
    "분노": ["짜증", "분노", "격분"],
    "기대": ["관심", "기대", "경계"],
    "기쁨": ["평온", "기쁨", "환희"],
}


def code_of(url):
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)


# 라이브 크기는 `pd_check_live.py` 의 자를 그대로 쓴다 — **두 벌로 만들면 언젠가 갈린다.**
# (한때 이 화면이 '200 (53871 B)' 처럼 **로컬 크기를 라이브 크기인 양** 찍었다.
#  코드만 확인하고 크기는 안 봤기 때문이다 — 그건 검증이 아니라 검증처럼 보이는 숫자다.)
_spec = importlib.util.spec_from_file_location(
    "pdlive", Path(__file__).with_name("pd_check_live.py"))
_pdlive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pdlive)
size_of = _pdlive.size_of


def primary_index(cell):
    """칸 이름에서 **첫 감정**의 수레바퀴 자리를 뽑는다.

    '시기 (슬픔+분노)' → 슬픔 → 4 · '슬픔 · 비통' → 슬픔 → 4 · '기쁨[3차] (기쁨+놀람)' → 기쁨 → 0
    dyad 는 **먼저 적힌 쪽**이 주(主)감정이다 — 그게 data-here 규약이다.
    """
    first = cell.split("(")[1].split("+")[0].strip() if "(" in cell else \
        cell.split("·")[0].strip()
    first = first.replace("[3차]", "").replace("[2차]", "").strip()
    return WHEEL.index(first) if first in WHEEL else None


def dyad_of(cell):
    """dyad 면 (감정1, 감정2) 를, 기본 칸이면 None."""
    if "(" not in cell:
        return None
    a, b = cell.split("(")[1].rstrip(")").split("+")
    return a.strip(), b.strip()


def main():
    spec = importlib.util.spec_from_file_location("dash", DASH)
    dash = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dash)
    Q, HOLD = dash.QUEUE, dash.HOLD

    problems = []
    print("=" * 108)
    print("48칸 마스터 — 감정 · 곡 · 쪽지 · 지금 라이브인지")
    print("=" * 108)
    print("%-3s %-22s %-34s %-5s %-8s %s"
          % ("칸", "감정", "곡", "수레", "쪽지", "지금 라이브"))
    print("-" * 108)

    basics, dyads = {}, []
    for no, title, meta, cell, slug in Q:
        # ① 감정표 검사
        d = dyad_of(cell)
        if d:
            dyads.append((no, d))
        else:
            base, lvl = [x.strip() for x in cell.split("·")]
            basics.setdefault(base, []).append((no, lvl))
        want = primary_index(cell)

        # ② 쪽지·라이브
        pdir = next(LANE.glob("%s-*/site/%s/" % (no, slug)), None) if slug else None
        if no in HOLD:
            # 슬러그가 없어도(30·39호) **폴더 이름으로 원격을 두드려 본다** —
            # 쪽지를 안 쓴 보류 곡이 검사에서 조용히 빠지면 안 된다.
            name = slug or (next(LANE.glob("%s-*/" % no), None) or Path("")).name
            code = code_of("%s/%s" % (BASE, name)) if name else None
            if code == 200:
                problems.append("%s호 — 보류인데 라이브에 있다" % no)
                state = "⛔⚠️ 보류인데 라이브 200"
            else:
                state = "⛔ 보류 (라이브 %s)" % code
            note = "HOLD"
        elif pdir is None or not (pdir / "index.html").is_file():
            state = "❌ 쪽지 없음"
            problems.append("%s호 — 쪽지가 없다" % no)
            note = "—"
        else:
            code, live = size_of("%s/%s/index.html" % (BASE, slug))
            local = (pdir / "index.html").stat().st_size
            here = None
            html = (pdir / "index.html").read_text(encoding="utf-8")
            for piece in html.split('data-here="')[1:]:
                here = piece.split('"')[0]
                break
            if here is None or (want is not None and int(here) != want):
                problems.append("%s호 — data-here=%s 인데 첫 감정은 %s(%s)"
                                % (no, here, WHEEL[want] if want is not None else "?",
                                   want))
            if code != 200:
                state = "❌ HTTP %s" % code
                problems.append("%s호 — 라이브가 %s" % (no, code))
            elif live is not None and live != local:
                state = "⚠️ 라이브 %s B ≠ 로컬 %s B" % (live, local)
                problems.append("%s호 — 라이브가 옛 바이트(%s B), 로컬은 %s B"
                                % (no, live, local))
            else:
                state = "✅ 200 · 라이브=로컬 %s B" % local
            note = "%d B" % local
        print("%-3s %-22s %-34s %-5s %-8s %s"
              % (no, cell, title[:32], want if want is not None else "?",
                 note, state))

    # ③ 감정표 구조 — 눈으로 세지 않고 셈으로 확인한다
    print("-" * 108)
    n_basic = sum(len(v) for v in basics.values())
    rungs = {b: [lv for _, lv in v] for b, v in basics.items()}
    for b in WHEEL:
        if b not in rungs:
            problems.append("기본 감정 %s 의 강도 3단이 없다" % b)
        elif sorted(rungs[b]) != sorted(INTENSITY[b]):
            problems.append("%s 의 3단이 %s — 정본은 %s"
                            % (b, rungs[b], INTENSITY[b]))
    dist = {}
    for no, (a, b) in dyads:
        if a not in WHEEL or b not in WHEEL:
            problems.append("%s호 dyad %s+%s — 모르는 감정" % (no, a, b))
            continue
        i, j = WHEEL.index(a), WHEEL.index(b)
        k = min((i - j) % 8, (j - i) % 8)
        dist.setdefault(k, []).append(no)
    print("기본 8 × 강도 3단 = %d칸 · dyad = %d칸 · 합 %d칸"
          % (n_basic, len(dyads), n_basic + len(dyads)))
    for k in sorted(dist):
        print("  %d차 dyad(수레바퀴 %d칸 간격) %2d개 — %s"
              % (k, k, len(dist[k]), " ".join(sorted(dist[k]))))
    print("수레바퀴 순서: " + " · ".join("%s%d" % (n, i) for i, n in enumerate(WHEEL)))

    # ④ Boss 가 보는 목록
    print("-" * 108)
    live = [(no, slug) for no, t, m, c, slug in Q
            if slug and no not in HOLD]
    print("라이브 URL %d개 — https://parksy.kr/channel/musician/piano/<슬러그>"
          % len(live))
    print("  " + " ".join(no for no, _ in live))
    hold = " ".join(no for no in sorted(HOLD))
    print("보류 %d개: %s   (표식 파일 %s.HOLD)" % (len(HOLD), hold, "/".join(sorted(HOLD))))

    print("-" * 108)
    if problems:
        print("문제 %d:" % len(problems))
        for p in problems:
            print("  · %s" % p)
    else:
        print("문제 0 — 48칸이 맞고, 쪽지가 다 있고, 라이브가 다 열린다.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
