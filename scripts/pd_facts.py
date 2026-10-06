#!/usr/bin/env python3
"""곡 하나의 '실측 사실'을 뽑는다. 페이지에 쓰는 숫자는 전부 여기서 나온다.

    python3 scripts/pd_facts.py <raw.mid> <원곡오디오> [--pitch 56]

페이지는 문학이고 숫자는 실측이다. 이 스크립트가 실측 쪽이다.
기억으로 쓴 숫자는 하나도 없어야 한다 — 이 채널의 주장이 그거다.

뽑는 것:
  · 음 수 / 음역 / 첫 음·마지막 음 시각 / 길이
  · 원곡 오디오의 앞뒤 무음, 통합 라우드니스(LUFS), 라우드니스 레인지(LRA)
  · 반복음(pitch) 통계 — 몇 번, 가장 긴 공백, 언제 멈추는가
  · 저음(≤bass_max)이 바뀌는 시각 = 칸 경계 후보
  · 저음이 가장 오래 붙어 있는 구간 (곡의 '어둠')
  · 4초 창 다이내믹 곡선에서 최고점·최저점
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from pd_midi_notes import notes_from_midi  # noqa: E402


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def audio_facts(path):
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())
    loud = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path,
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    i = lra = peak = None
    lines = loud.splitlines()
    for k, ln in enumerate(lines):
        if "Integrated loudness" in ln and k + 1 < len(lines):
            i = float(lines[k + 1].split("I:")[1].split("LUFS")[0])
        if "Loudness range" in ln and k + 1 < len(lines):
            lra = float(lines[k + 1].split("LRA:")[1].split("LU")[0])
        if "True peak" in ln and k + 1 < len(lines):
            peak = float(lines[k + 1].split("Peak:")[1].split("dBFS")[0])
    sil = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
              "-af", "silencedetect=n=-50dB:d=0.30", "-f", "null", "-"])
    runs = []
    cur = None
    for ln in sil.splitlines():
        if "silence_start" in ln:
            cur = float(ln.split("silence_start:")[1].split()[0])
        elif "silence_end" in ln and cur is not None:
            e = float(ln.split("silence_end:")[1].split()[0])
            runs.append((round(cur, 3), round(e, 3)))
            cur = None
    if cur is not None:
        runs.append((round(cur, 3), round(dur, 3)))
    return dur, i, lra, peak, runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("midi")
    ap.add_argument("audio")
    ap.add_argument("--pitch", type=int, default=None,
                    help="반복음 통계를 낼 음높이 (예: 빗방울 = 56)")
    ap.add_argument("--bass-max", type=int, default=50)
    ap.add_argument("--win", type=float, default=4.0)
    a = ap.parse_args()

    notes, _ = notes_from_midi(a.midi)
    notes.sort(key=lambda n: n[0])
    pitches = [n[2] for n in notes]
    lo, hi = min(pitches), max(pitches)
    end = max(n[0] + n[1] for n in notes)
    print("음 %d개 · 음역 %d~%d · 첫 음 %.3fs · 마지막 음 시작 %.3fs · 끝 %.3fs"
          % (len(notes), lo, hi, notes[0][0], notes[-1][0], end))

    pc = {}
    for p in pitches:
        pc[p] = pc.get(p, 0) + 1
    top = sorted(pc.items(), key=lambda kv: -kv[1])[:6]
    print("많이 나온 음: " + " · ".join("%d(%s)×%d" % (p, N[p % 12] + str(p // 12 - 1), c)
                                        for p, c in top))

    if a.pitch is not None:
        ts = sorted(n[0] for n in notes if n[2] == a.pitch)
        if len(ts) > 1:
            iv = np.diff(ts)
            print("반복음 %d: %d회 · 처음 %.3fs · 마지막 %.3fs · 간격 중앙값 %.3fs "
                  "(최소 %.3f 최대 %.3f) · 최대 공백 %.2fs"
                  % (a.pitch, len(ts), ts[0], ts[-1], np.median(iv), iv.min(), iv.max(), iv.max()))
            gaps = [(round(iv[k], 2), round(ts[k], 2)) for k in range(len(iv))
                    if iv[k] > 3 * np.median(iv)]
            print("   긴 공백: " + (", ".join("%.1fs @%.1fs" % g for g in gaps[:12]) or "없음"))

    lo_notes = sorted((n for n in notes if n[2] <= a.bass_max), key=lambda n: n[0])
    if lo_notes:
        groups, cur, t0 = [], [], None
        for s, d, p in lo_notes:
            if t0 is None or s - t0 <= 0.15:
                cur.append((s, p))
            else:
                groups.append(cur); cur = [(s, p)]
            t0 = s
        if cur:
            groups.append(cur)
        seq = [(g[0][0], min(x[1] for x in g)) for g in groups]
        hold, hs = [], None
        for k in range(1, len(seq)):
            if hs is None:
                hs = seq[k - 1]
            if seq[k][1] != seq[k - 1][1]:
                hold.append((seq[k][0] - hs[0], hs[1], hs[0], seq[k][0]))
                hs = seq[k]
        hold.append((seg_end := end - hs[0], hs[1], hs[0], end))
        hold.sort(reverse=True)
        print("저음이 바뀐 횟수 %d" % (len(seq) - 1))
        print("저음이 가장 오래 붙어 있던 구간 (상위 5):")
        for dur, p, s, e in hold[:5]:
            print("   %6.2fs  %s(%d)  %.1fs~%.1fs" % (dur, N[p % 12] + str(p // 12 - 1), p, s, e))

    # 다이내믹 곡선: 창마다 음의 개수로 대략의 세기를 본다
    n_win = int(end / a.win) + 1
    cnt = np.zeros(n_win)
    for s, d, p in notes:
        k = int(s / a.win)
        if k < n_win:
            cnt[k] += 1
    k_hi = int(np.argmax(cnt)); k_lo = int(np.argmin(cnt[1:-1])) + 1
    print("4초 창 음밀도 최고 %d음 @%.1fs · 최저 %d음 @%.1fs"
          % (cnt[k_hi], k_hi * a.win, cnt[k_lo], k_lo * a.win))

    dur, i, lra, peak, runs = audio_facts(a.audio)
    print("원곡 오디오 %.3fs · 통합 %.1f LUFS · LRA %.1f LU · 트루피크 %.1f dBFS"
          % (dur, i, lra, peak))
    for s, e in runs:
        print("   무음 %.3f~%.3f (%.2fs)" % (s, e, e - s))
    print("※ 원곡 끝 = 마지막 무음 시작 권장 (%.3fs)" % (runs[-1][0] if runs else dur))


N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

if __name__ == "__main__":
    main()
