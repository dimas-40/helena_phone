#!/usr/bin/env python3
"""저음 칸 — 이 시리즈에서 '저음이 한 음을 떠나지 않은 구간'을 세는 유일한 구현.

왜 모듈로 뺐나:
  같은 규칙이 세 군데에 따로 구현돼 있었다 (pd_facts · pd_measure · pd_build_data).
  그래서 페이지에 적힌 숫자와 페이지의 띠 그림이 서로 다른 것을 세고 있었고,
  급기야 **없는 멈춤을 있다고 적는 일**까지 났다 (아래).

한 칸의 뜻:
  저음(= 그 순간 가장 낮은 음, MIDI 50 이하)이 **음높이를 바꾸지 않고 이어지는** 구간.
  바뀌면 새 칸.

규칙 둘:
  1. 붙어 들어온 저음은 한 덩어리로 접는다 (cluster=0.15s).
     왼손이 옥타브·5도를 같이 치면 최저음 하나로 본다. 안 접으면 화음마다
     저음이 '바뀐 것'으로 세어져 진짜 정지가 안 보인다.
  2. 사이가 BASS_GAP_MAX 넘게 비면 **끊긴 것으로 본다.** 이게 핵심이다.

2번이 왜 필요한가 — 실제로 데었다:
  채보(transcription)는 저음을 통째로 놓치는 자리가 있다. 그 자리를 '안 바뀐 칸'으로
  세면 채보의 구멍이 연주의 멈춤으로 둔갑한다.
    · 05번 트로이메라이: 121.020초에 0.02초짜리 사2(G2) 하나가 찍히고 그 뒤
      137.272초까지 저음이 하나도 안 잡혔다 → "16.25초 동안 사2를 떠나지 않는다" 로 적었다.
      **없는 멈춤이었다.**
    · 02번 바흐: 40.039초부터 74.875초까지 저음이 안 잡혀 34.8초짜리 칸이 생겼다.
  그래서 칸마다 실제 최대 공백(max_gap_s)을 같이 돌려준다 — 읽는 사람이 확인할 수 있게.
  8초는 이 시리즈 저음 재타격 간격(보통 1~6초)보다 넉넉히 크고,
  채보 누락(수십 초)보다는 확실히 작다.
"""
BASS_MAX = 50
CLUSTER = 0.15
GAP_MAX = 8.0

KO = {0: "다", 1: "올림다", 2: "라", 3: "올림라", 4: "마", 5: "바",
      6: "올림바", 7: "사", 8: "올림사", 9: "가", 10: "올림가", 11: "나"}


def ko(p):
    return KO[p % 12] + str(p // 12 - 1)


def clusters(notes, bass_max=BASS_MAX, cluster=CLUSTER):
    """붙어 들어온 저음들을 한 덩어리로 접고, 덩어리마다 (시작, 끝, 최저음) 을 낸다."""
    lo = sorted((n for n in notes if n[2] <= bass_max), key=lambda n: n[0])
    out, cur, t0 = [], [], None
    for s, d, p in lo:
        if t0 is not None and s - t0 > cluster:
            out.append(cur)
            cur = []
        cur.append((s, d, p))
        t0 = s
    if cur:
        out.append(cur)
    return [(g[0][0], max(x[0] + x[1] for x in g), min(x[2] for x in g)) for g in out]


def bass_blocks(notes, bass_max=BASS_MAX, cluster=CLUSTER, gap_max=GAP_MAX):
    """칸 목록. 각 칸 = {start, end, dur, pitch, name, max_gap_s, first, strikes}."""
    out, hs = [], None
    for s, e, p in clusters(notes, bass_max, cluster):
        if hs is None:
            hs = dict(pitch=p, start=s, end=e, last=s, max_gap_s=0.0, strikes=1)
        elif p == hs["pitch"] and s - hs["last"] <= gap_max:
            hs["max_gap_s"] = max(hs["max_gap_s"], s - hs["last"])
            hs["last"] = s
            hs["end"] = max(hs["end"], e)
            hs["strikes"] += 1
        else:
            out.append(hs)
            hs = dict(pitch=p, start=s, end=e, last=s, max_gap_s=0.0, strikes=1)
    if hs is not None:
        out.append(hs)
    for b in out:
        b["dur"] = round(b["end"] - b["start"], 3)
        b["start"] = round(b["start"], 3)
        b["end"] = round(b["end"], 3)
        b["max_gap_s"] = round(b["max_gap_s"], 3)
        b["name"] = ko(b["pitch"])
    return out


QUOTE_GAP = 5.0     # 페이지에 인용하려면 칸 안의 최대 공백이 이보다 짧아야 한다
QUOTE_STRIKES = 2   # 그리고 저음이 이만큼은 다시 쳐져 있어야 한다


def quotable(blocks, gap_max=QUOTE_GAP, strikes=QUOTE_STRIKES):
    """페이지에 쓸 수 있는 칸만 고른다.

    '가장 긴 칸'을 그냥 인용하면, 채보가 놓친 자리가 이긴다.
    한 번만 찍히고 그 뒤로 안 잡힌 칸은 **연주가 멈춘 게 아니라 채보가 멈춘 것**이다.
    그래서 재타격 횟수와 칸 안 최대 공백을 함께 보고, 버틸 만한 것만 남긴다.
    """
    return sorted((b for b in blocks
                   if b["max_gap_s"] <= gap_max and b["strikes"] >= strikes),
                  key=lambda b: -b["dur"])


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from pd_midi_notes import notes_from_midi
    n, _ = notes_from_midi(sys.argv[1])
    n.sort(key=lambda x: x[0])
    bl = bass_blocks(n)
    print("칸 %d개 · 중앙 %.3fs" % (len(bl), sorted(b["dur"] for b in bl)[len(bl) // 2]))
    for b in sorted(bl, key=lambda b: -b["dur"])[:6]:
        print("  %7.2fs  %-7s %8.3f~%8.3f  최대공백 %.2fs  재타격 %d회"
              % (b["dur"], b["name"], b["start"], b["end"], b["max_gap_s"], b["strikes"]))
