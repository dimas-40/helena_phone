#!/usr/bin/env python3
"""저음이 한 음을 떠나지 않은 구간을 **오디오에서 직접** 잰다.

    python3 scripts/pd_bass_audio.py <원곡오디오> [--json]

왜 MIDI 로는 안 되나:
  MIDI 는 채보기(transcription)가 만든 추정이다. 추정이 틀리면 그 틀림이 그대로
  페이지의 주장이 된다. 실제로 그렇게 됐다 — 05번 트로이메라이에서 채보가 저음을
  통째로 놓친 16초를 "사2를 16.25초 동안 떠나지 않았다"고 적었다. 연주는 멀쩡했다.
  이 채널의 주장이 '실측'이라면, 주장의 근거도 채보가 아니라 소리여야 한다.

재는 법:
  1. 50ms 창마다 스펙트럼을 본다.
  2. 55~210Hz 구간에서 가장 센 봉우리를 찾고, 포물선 보간으로 주파수를 좀 더 정확히 잡는다.
  3. 주파수 → 가장 가까운 반음(MIDI 번호).
  4. 저음 봉우리가 그 창 전체 최대값의 -25dB 안에 있으면 '저음이 들린다'로 본다.
  5. '들리는' 창들이 이어지면서 반음이 안 바뀌는 최장 구간을 낸다.
     한 창(50ms)이 비면 끊긴 것으로 본다 — 다른 음이 잠깐 스쳐도 끊긴다.

  그래서 여기서 나오는 값은 MIDI 쪽 값보다 **짧게** 나오는 게 정상이다.
  MIDI 는 '저음 음높이가 바뀌지 않았다'를 세고, 이건 '저음이 실제로 계속 울렸다'를 센다.
  페이지에는 이 값을 쓴다. 짧은 쪽이 참이다.
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

R = 22050
FRAME = 2048          # 93ms
HOP = 1102            # 50ms
F_LO, F_HI = 55.0, 210.0
REL_DB = -25.0

KO = {0: "다", 1: "올림다", 2: "라", 3: "올림라", 4: "마", 5: "바",
      6: "올림바", 7: "사", 8: "올림사", 9: "가", 10: "올림가", 11: "나"}


def ko(p):
    return KO[int(p) % 12] + str(int(p) // 12 - 1)


def track(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
         "-ar", str(R), "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    win = np.hanning(FRAME).astype(np.float32)
    freqs = np.fft.rfftfreq(FRAME, 1.0 / R)
    band = (freqs >= F_LO) & (freqs <= F_HI)
    idx = np.flatnonzero(band)
    out = []
    for k in range(0, len(x) - FRAME, HOP):
        seg = x[k:k + FRAME] * win
        sp = np.abs(np.fft.rfft(seg))
        if sp.max() <= 0:
            out.append((k / R, None, -999.0))
            continue
        j = idx[int(np.argmax(sp[idx]))]
        # 포물선 보간 — 봉우리 좌우 빈으로 진짜 봉우리 위치를 좁힌다
        if 0 < j < len(sp) - 1:
            a, b, c = sp[j - 1], sp[j], sp[j + 1]
            d = a - 2 * b + c
            off = 0.5 * (a - c) / d if d != 0 else 0.0
        else:
            off = 0.0
        f = (j + off) * R / FRAME
        rel = 20 * math.log10(sp[j] / sp.max() + 1e-12)
        midi = 69 + 12 * math.log2(f / 440.0) if f > 0 else 0
        out.append((k / R, midi, rel))
    return out


def longest_hold(tracks):
    """반음이 안 바뀌면서 '들리는' 창이 이어지는 최장 구간."""
    runs, st, cur = [], None, None
    for i, (t, midi, rel) in enumerate(tracks):
        ok = midi is not None and rel >= REL_DB
        n = round(midi) if ok else None
        if cur is None:
            if ok:
                st, cur = i, n
        elif ok and n == cur:
            pass
        else:
            runs.append((st, i))
            st, cur = (i, n) if ok else (None, None)
    if cur is not None:
        runs.append((st, len(tracks)))
    out = []
    for a, b in runs:
        if b - a < 4:
            continue
        out.append(dict(start=round(tracks[a][0], 3),
                        end=round(tracks[b - 1][0] + HOP / R, 3),
                        dur=round(tracks[b - 1][0] + HOP / R - tracks[a][0], 3),
                        pitch=round(tracks[a][1]),
                        name=ko(round(tracks[a][1]))))
    out.sort(key=lambda d: -d["dur"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    holds = longest_hold(track(a.audio))
    if a.json:
        print(json.dumps(holds[:a.top], ensure_ascii=False))
        return
    print("%s — 저음이 한 음을 떠나지 않은 구간 (오디오 실측)" % Path(a.audio).name)
    for h in holds[:a.top]:
        print("   %7.2fs  %-8s %8.3f~%8.3f" % (h["dur"], h["name"], h["start"], h["end"]))
    if not holds:
        print("   없음")


if __name__ == "__main__":
    main()
