#!/usr/bin/env python3
"""곡 하나의 실측 사실을 JSON 으로 뽑는다 — 페이지에 쓰는 모든 숫자의 정본.

    python3 scripts/pd_measure.py <raw.mid> <원곡오디오> --name 05 --out 05.facts.json

왜 pd_facts.py 와 따로 있나:
  pd_facts.py 는 사람이 읽는 출력이고, 이건 기계가 읽는 출력이다.
  페이지 생성기·비교표·검사기가 전부 이 JSON 하나를 본다.
  숫자가 페이지마다 다르게 나오는 사고를 막으려고 정의를 여기 한 곳에 못 박았다.

정의 — 여기가 유일한 정의다. 다른 데서 다시 재지 말 것:

  앞머리s / 꼬리s
      -50dB(20ms RMS) 를 처음 넘는 시각 / 마지막으로 넘긴 뒤 끝까지의 길이.
      "완전한 0" 이 아니라 -50dB 기준이다 — 대부분의 녹음 바닥에 히스가 깔려 있다.

  peak_1s_db  ("1초 최고")
      1초 비중첩 창의 RMS 최댓값, dBFS.  순간 피크가 아니라 그 1초 동안의 실효 세기다.

  spread_40s_db  ("구간 세기 폭")
      40초 비중첩 창의 RMS(dB) 중 최댓값 − 최솟값.  곡이 얼마나 평평한지의 척도다.

  LUFS / LRA / TP
      ffmpeg ebur128.  원본 녹음에서 잰 값이다 (배포 트랙은 -16 LUFS 로 정규화돼 있다).

  rate  ("초당 몇 음")
      음 수 ÷ 마지막 음이 시작된 시각.  파일 길이나 orig_end 로 나누지 않는다 —
      뒤에 붙은 무음이 분모에 들어가면 같은 연주가 편집에 따라 다른 값이 된다.

  칸(blocks) — 정의는 pd_bass.py 한 곳에 있다.  여기서 다시 구현하지 않는다.
      block_max / block_top5 는 quotable() 을 통과한 칸만 담는다:
      채보가 놓친 자리가 '가장 긴 멈춤'으로 둔갑하지 않게 재타격·최대공백을 본다.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from pd_midi_notes import notes_from_midi  # noqa: E402

R = 22050            # 세기 측정용 샘플레이트 (RMS 창에는 충분하다)
from pd_bass import bass_blocks, quotable, ko  # noqa: E402  (칸 정의는 거기 한 곳에만)


def decode(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1",
         "-ar", str(R), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def level(x):
    """앞머리/꼬리 무음, 1초 최고, 40초 폭."""
    win = int(0.02 * R)
    n = (x.size // win) * win
    rms = np.sqrt((x[:n].reshape(-1, win) ** 2).mean(axis=1))
    db = 20 * np.log10(np.maximum(rms, 1e-12))
    loud = np.flatnonzero(db > -50.0)
    lead = float(loud[0] * win / R) if loud.size else float(x.size / R)
    tail = float(x.size / R - (loud[-1] + 1) * win / R) if loud.size else 0.0

    def winmax(w):
        k = int(w * R)
        m = (x.size // k) * k
        if m < k:
            return None
        a = x[:m].reshape(-1, k)
        r = np.sqrt((a ** 2).mean(axis=1))
        return 20 * np.log10(np.maximum(r, 1e-12))

    d1 = winmax(1.0)
    d40 = winmax(40.0)
    return dict(
        lead_s=round(lead, 3), tail_s=round(tail, 3),
        peak_1s_db=round(float(d1.max()), 2) if d1 is not None else None,
        spread_40s_db=round(float(d40.max() - d40.min()), 2) if d40 is not None else None,
    )


def ebur128(path):
    s = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True).stderr.splitlines()
    out = {}
    for k, ln in enumerate(s):
        if "Integrated loudness" in ln and k + 1 < len(s):
            out["lufs"] = float(s[k + 1].split("I:")[1].split("LUFS")[0])
        if "Loudness range" in ln and k + 1 < len(s):
            out["lra"] = float(s[k + 1].split("LRA:")[1].split("LU")[0])
        if "True peak" in ln and k + 1 < len(s):
            out["tp"] = float(s[k + 1].split("Peak:")[1].split("dBFS")[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("midi")
    ap.add_argument("audio")
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--orig-end", type=float, default=None,
                    help="원곡 트랙을 자른 지점(초). 없으면 오디오 전체 길이")
    a = ap.parse_args()

    notes, _ = notes_from_midi(a.midi)
    notes.sort(key=lambda n: n[0])
    pitches = [n[2] for n in notes]
    end = max(n[0] + n[1] for n in notes)
    x = decode(a.audio)
    dur = round(x.size / R, 3)

    lv = level(x)
    eb = ebur128(a.audio)

    pc = {}
    for p in pitches:
        pc[p] = pc.get(p, 0) + 1
    top = [dict(pitch=p, name=ko(p), count=c)
           for p, c in sorted(pc.items(), key=lambda kv: -kv[1])[:6]]

    top_p = top[0]["pitch"]
    ts = sorted(n[0] for n in notes if n[2] == top_p)
    iv = np.diff(ts) if len(ts) > 1 else np.array([0.0])
    med = float(np.median(iv)) if iv.size else 0.0
    gaps = sorted(((float(iv[k]), float(ts[k])) for k in range(iv.size)
                   if iv[k] > 3 * med), reverse=True) if med else []
    repeat = dict(
        pitch=top_p, name=ko(top_p), count=len(ts),
        first=round(ts[0], 3), last=round(ts[-1], 3),
        median_gap=round(med, 3),
        max_gap=round(gaps[0][0], 2) if gaps else 0.0,
        max_gap_at=round(gaps[0][1], 2) if gaps else 0.0,
        gaps=[dict(gap=round(g, 2), at=round(t, 2)) for g, t in gaps[:6]],
    )

    blocks = bass_blocks(notes)
    hold = quotable(blocks)[:5]

    W = 4.0
    nw = int(end / W) + 1
    cnt = np.zeros(nw)
    for s, d, p in notes:
        cnt[int(s / W)] += 1
    k_hi, k_lo = int(np.argmax(cnt)), int(np.argmin(cnt[1:-1])) + 1

    orig_end = round(a.orig_end, 3) if a.orig_end else dur
    facts = dict(
        name=a.name,
        n_notes=len(notes),
        rate=round(len(notes) / notes[-1][0], 2),
        pitch_lo=min(pitches), pitch_hi=max(pitches),
        pitch_lo_name=ko(min(pitches)), pitch_hi_name=ko(max(pitches)),
        first_note=round(notes[0][0], 3),
        last_note=round(notes[-1][0], 3),
        last_end=round(end, 3),
        orig_dur=dur, orig_end=orig_end,
        top_pitches=top, repeat=repeat,
        n_blocks=len(blocks),
        block_median=round(float(np.median([b["dur"] for b in blocks])), 3) if blocks else 0.0,
        block_max=hold[0] if hold else None,
        block_top5=hold,
        density_peak=dict(count=int(cnt[k_hi]), at=round(k_hi * W, 1)),
        density_trough=dict(count=int(cnt[k_lo]), at=round(k_lo * W, 1)),
        density_win_s=W,
        **lv, **eb,
    )
    Path(a.out).write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(facts, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
