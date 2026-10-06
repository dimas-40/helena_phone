#!/usr/bin/env python3
"""MIDI → [(start, dur, pitch)] 로 뽑는다. pd_build_data.py 가 쓴다.

mido 는 note_off 없이 같은 음이 다시 켜지거나, 짝 없는 note_off 를 주기도 한다
(채보기가 그렇게 만든다). 그래서 pop 에 기본값을 준다 — KeyError 로 죽으면 안 된다.
"""
import sys
import mido


def notes_from_midi(path):
    mid = mido.MidiFile(path)
    t = 0.0
    on = {}
    out = []
    for msg in mid:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            on.setdefault(msg.note, []).append(t)      # 같은 음 중복 대비 큐
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            q = on.get(msg.note)
            if q:
                s = q.pop(0)
                out.append((s, max(0.02, t - s), msg.note))
    for pitch, q in on.items():                        # 끝까지 안 꺼진 음
        for s in q:
            out.append((s, max(0.02, t - s), pitch))
    out.sort()
    return out, t


if __name__ == "__main__":
    n, t = notes_from_midi(sys.argv[1])
    print("음 %d개 · 길이 %.3fs · 음역 %d~%d" % (len(n), t, min(x[2] for x in n), max(x[2] for x in n)))
