#!/usr/bin/env python3
"""4초 창 밀도 — 발행된 쪽지들이 쓰는 정의.

★ 두 벌의 정의가 있다 (2026-10-07 24호에서 확인):
  · pd_measure.py  = **고정 4초 칸**(겹치지 않음). facts.json 의 값.
  · 쪽지 발행값    = **4초 창을 0.5초씩 밀어 가며** 센 값.

이 스크립트는 후자다. 음 개수는 **온셋(onset)** 기준이다.

★ 2026-10-08 25호에서 가장자리 규칙을 확정했다:
  창이 **마지막 음까지 안에 들어와야** 한다(`t + W <= span`).
  이 규칙을 빼면 최소값이 발행값과 안 맞는다 —
    20호 5(발행 36) · 16호 7(35) · 29호 1(2) · 36호 6(7).
  규칙을 넣으면 **여섯 편 전부 정확히 맞는다**(최대값은 규칙과 무관하게 같다).

검증 (발행된 쪽지와 대조):
  20호 36↔79=2.19 · 16호 35↔132=3.77 · 27호 4↔86=21.50
  29호 2↔88=44.00 · 33호 max 208 · 36호 7↔164=23.43 · 24호 5↔26=5.20
  (24호 최소 5 @92.5초 · 최대 26 @23.5초 — 2026-10-08 발행 쪽지 정정분과 일치)
  안 맞는 둘: 13호 · 37호 (쪽지에 인용하지 않는다)

사용:
    python3 scripts/pd_density.py <raw.mid> [--orig-end SEC]
"""
import argparse
import sys
from pathlib import Path

import mido

W = 4.0
STEP = 0.5


def onsets(path: Path, orig_end: float | None = None) -> list[float]:
    mf = mido.MidiFile(str(path))
    tpb = mf.ticks_per_beat
    tempo = 500000
    out = []
    for track in mf.tracks:
        t = 0.0
        for msg in track:
            t += mido.tick2second(msg.time, tpb, tempo)
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "note_on" and msg.velocity > 0:
                out.append(t)
    out.sort()
    if orig_end:
        out = [x for x in out if x <= orig_end]
    return out


def density(ons: list[float]):
    if not ons:
        return None
    end = ons[-1]
    best = (0.0, 0)
    worst = (0.0, 10 ** 9)
    t = 0.0
    while t <= end:
        if t + W > end:          # 창이 마지막 음을 넘어가면 세지 않는다
            break
        n = sum(1 for x in ons if t <= x < t + W)
        if n > best[1]:
            best = (t, n)
        if n < worst[1]:
            worst = (t, n)
        t += STEP
    return {"n": len(ons), "span": end, "max": best, "min": worst,
            "ratio": (best[1] / worst[1]) if worst[1] else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("midi")
    ap.add_argument("--orig-end", type=float, default=None)
    a = ap.parse_args()
    ons = onsets(Path(a.midi), a.orig_end)
    d = density(ons)
    if not d:
        print("음이 없다")
        return 1
    print("음 %d · 구간 %.3fs" % (d["n"], d["span"]))
    print("최대 %d음 @%.1fs · 최소 %d음 @%.1fs · 비 %s"
          % (d["max"][1], d["max"][0], d["min"][1], d["min"][0],
             ("%.2f" % d["ratio"]) if d["ratio"] else "—(0)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
