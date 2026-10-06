#!/usr/bin/env python3
"""박씨 렌더링 페이지용 data.js 생성기 — 48곡 공용.

곡 페이지는 index.html + data.js 두 개로 굴러간다. index.html 은 문학이고,
data.js 는 실측이다. 이 스크립트가 실측 쪽을 만든다.

    python3 scripts/pd_build_data.py \\
        --midi <RAW.mid> --audio <combined.mp3> \\
        --orig-end 183.5886 --gap-end 185.5886 \\
        --grid auto|N  --bar-unit "마디" \\
        --out <site>/<slug>/data.js

--grid auto 는 저음(≤50) 음높이가 바뀌는 시각을 칸 경계로 쓴다. 마디 수를
모르는 곡에서 "몇 마디"라고 우기지 않기 위한 것이다. 마디 수가 확실한 곡만
숫자를 준다 — 우기는 것보다 단위를 밝히는 게 낫다.
"""
import argparse
import base64
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from pd_midi_notes import notes_from_midi  # noqa: E402

PEAK_BUCKETS = 2400


def peaks_b64(path, buckets=PEAK_BUCKETS):
    """파형을 buckets 개의 최대진폭(0~255)으로 접어 base64 로. 모노로 섞는다.

    ⚠️ 길이는 프레임이 아니라 초로 돌려준다 — len(d) 는 프레임 수다.
    """
    d, sr = sf.read(path, always_2d=True, dtype="float32")
    d = d.mean(axis=1)
    n = len(d) // buckets
    if n == 0:
        raise SystemExit("오디오가 너무 짧다")
    core = d[:n * buckets].reshape(buckets, n)
    v = np.abs(core).max(axis=1)
    m = v.max() or 1.0
    q = np.clip(v / m * 255, 0, 255).astype(np.uint8)
    return base64.b64encode(q.tobytes()).decode(), len(d) / float(sr)


def bass_blocks(notes, cluster=0.15):
    """저음 음높이가 바뀌는 시각들. 칸 경계로 쓴다.

    한 화음은 저음이 여럿 동시에 울린다(D2·D3·F4…). 그걸 다 경계로 세면
    간격 0.001초짜리 칸이 생긴다. 그래서 먼저 onset 을 묶고(cluster),
    묶음마다 **가장 낮은 음** 하나만 본다.
    """
    lo = sorted((n for n in notes if n[2] <= 50), key=lambda n: n[0])
    if not lo:
        return None
    groups, cur, t0 = [], [], None
    for s, _d, p in lo:
        if t0 is None or s - t0 <= cluster:
            cur.append((s, p))
        else:
            groups.append(cur)
            cur, t0 = [(s, p)], s
        if t0 is None:
            t0 = s
    if cur:
        groups.append(cur)
    b, last = [], None
    for g in groups:
        p = min(x[1] for x in g)
        if p != last:
            b.append(round(g[0][0], 3))
            last = p
    return b


def grid_blocks(notes, count):
    """첫 음부터 마지막 음 시작까지 count 칸으로 균등 분할."""
    t0 = notes[0][0]
    t1 = notes[-1][0]
    step = (t1 - t0) / (count - 1)
    return [round(t0 + i * step, 3) for i in range(count)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--midi", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--orig-end", type=float, required=True)
    ap.add_argument("--gap-end", type=float, required=True)
    ap.add_argument("--grid", default="auto", help="auto(저음 변화) 또는 정수")
    ap.add_argument("--bar-unit", default="칸")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    notes, _mid_len = notes_from_midi(a.midi)
    if not notes:
        raise SystemExit("음이 하나도 없다: " + a.midi)

    if a.grid == "auto":
        blocks = bass_blocks(notes)
        if not blocks:
            raise SystemExit("저음이 없어 auto 불가 — --grid N 을 주라")
    else:
        blocks = grid_blocks(notes, int(a.grid))

    peaks, dur = peaks_b64(a.audio)
    if abs(dur - a.gap_end) < 0.05:
        raise SystemExit("gap_end 가 총 길이와 같다 — orig_end 를 확인하라")

    payload = {
        "duration": round(dur, 3),
        "origEnd": round(a.orig_end, 3),
        "gapEnd": round(a.gap_end, 3),
        "renderEnd": round(dur, 3),
        "barUnit": a.bar_unit,
        "blocks": blocks,
        "notes": [[round(s, 3), round(d, 3), p] for s, d, p in notes],
        "peaks": peaks,
    }
    js = "window.PIECE=" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n"
    Path(a.out).write_text(js, encoding="utf-8")

    lo = min(n[2] for n in notes)
    hi = max(n[2] for n in notes)
    print("→ %s" % a.out)
    print("   음 %d개 · 음역 %d~%d · 길이 %.3fs" % (len(notes), lo, hi, dur))
    print("   원곡 %.3f / 침묵 %.3f / 재현 %.3f" % (a.orig_end, a.gap_end - a.orig_end, dur - a.gap_end))
    print("   %s %d칸 · 파형 %d점" % (a.bar_unit, len(blocks), PEAK_BUCKETS))
    if len(blocks) > 1:
        iv = np.diff(blocks)
        print("   칸 간격 중앙값 %.3fs (최소 %.3f 최대 %.3f)" % (np.median(iv), iv.min(), iv.max()))


if __name__ == "__main__":
    main()
