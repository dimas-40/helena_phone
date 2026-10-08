#!/usr/bin/env python3
"""채보가 그 녹음을 제대로 받아 적었는지 **소리와 대조해서** 판정한다.

    python3 scripts/pd_verify_transcription.py <raw.mid> <원곡오디오> [--out 판정.json]

왜 필요한가 (2026-10-08 30호 사건):
    채보 도구는 **실패해도 숫자를 뱉는다.** 699음 · 148블록 · BPM 까지 다 나왔다.
    숫자만 보면 성공처럼 보인다. 30호는 그렇게 낼 뻔했다.
    사람이 귀가 없으면 못 가리는 이 실패를 **기계가 가리게** 하려고 이 검사를 만들었다.

무엇을 재나:
    MIDI 를 100ms 창으로 잘라 **음이 시작된 개수**(밀도)를 센다.
    같은 창으로 원곡 오디오에서 **소리 에너지**를 잰다 — 두 가지로 잰다.
      flux : 스펙트럼 온셋 강도 (새 소리가 '생기는' 정도)
      rms  : 그 창의 실효 세기
    음악이면 **음이 많이 시작되는 곳에서 소리도 세다.** 그래서 상관이 양수여야 한다.
    부호가 뒤집히면(−) 도구가 소리와 무관한 것을 받아 적은 것이다.

판정선 — **이 구현으로** 통제군 네 곡을 다시 재서 잡았다 (2026-10-08):

    곡                    flux      rms     사람의 판정
    19호 슈만            +0.524   +0.235   맞음 (납품 완료)
    22호 멘델스존        +0.495   +0.328   맞음 (납품 완료)
    30호 무소르그스키    +0.104   +0.008   **실패** (사람이 귀로 확인)
    23호 캐논(현악 소재) +0.068   −0.032   알려진 불량

    → 통과: flux ≥ 0.30 **그리고** rms ≥ 0.15
      실패: flux < 0.20 **또는** rms < 0.05
      그 사이는 보류.   위 네 곡을 이 선으로 다시 재면 넷 다 제자리에 들어간다.

⚠️⚠️ **옛 숫자와 섞지 말 것.** 30호를 처음 실패로 판정할 때 쓴 임시 스크립트는
    코드가 안 남아 있다. 그때 적은 값(19호 +0.712/+0.643 · 30호 −0.423/−0.418)은
    **다른 구현으로 잰 것이라 이 스크립트의 값과 자가 다르다.** 부호 경향만 같고
    크기는 비교할 수 없다. 쪽지에 인용할 때는 **이 스크립트로 다시 잰 값**을 쓴다.

⚠️ 이 선은 통제군 **네 곡**에서 나온 것이다. 네 곡을 넘지 않는다.
   통과했다고 "좋은 채보"라는 뜻이 아니다 — "소리와 어긋나지 않는다"까지다.
   사람 연주를 받아 적는 한 이 검사는 **실패를 거르는 그물**이지 합격증이 아니다.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from pd_midi_notes import notes_from_midi  # noqa: E402

WIN = 0.100          # 창 길이(초)
GOOD_FLUX = 0.30     # 통과선
GOOD_RMS = 0.15
BAD_FLUX = 0.20      # 실패선
BAD_RMS = 0.05


def decodar(path, sr=22050):
    """오디오를 모노 float32 로. ffmpeg 한 갈래만 쓴다(디코더 차이를 만들지 않는다)."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le",
         "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32), sr


def midi_density(mid, n_win, t0=0.0):
    """창마다 '음이 시작된 개수'. 시작 시각만 센다 — 길이가 아니라 타격이다."""
    notes, _ = notes_from_midi(str(mid))       # ([(start, dur, pitch), ...], 길이)
    d = np.zeros(n_win, dtype=np.float64)
    for n in notes:
        i = int((n[0] - t0) / WIN)
        if 0 <= i < n_win:
            d[i] += 1.0
    return d


def audio_windows(x, sr, n_win):
    """창마다 RMS(dB) 와 온셋 플럭스. 둘 다 로그로 눌러 큰 소리가 지배하지 않게 한다."""
    n = min(len(x), n_win * int(sr * WIN))
    x = x[:n]
    frame = int(sr * WIN)
    m = n // frame
    blocks = x[:m * frame].reshape(m, frame)
    rms = np.sqrt((blocks ** 2).mean(axis=1) + 1e-20)
    # 스펙트럼 플럭스: 창 안을 반으로 갈라 앞뒤 스펙트럼의 양의 차이 합
    w = np.hanning(frame)
    half = frame // 2
    A = np.abs(np.fft.rfft(blocks[:, :half] * w[:half], axis=1))
    B = np.abs(np.fft.rfft(blocks[:, half:] * w[half:], axis=1))
    flux = np.maximum(B - A, 0).sum(axis=1)
    rms = np.pad(rms, (0, max(0, n_win - m)))[:n_win]
    flux = np.pad(flux, (0, max(0, n_win - m)))[:n_win]
    return rms, flux


def corr(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("midi")
    ap.add_argument("audio")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true", help="사람용 문장 대신 JSON 만")
    a = ap.parse_args()

    x, sr = decodar(a.audio)
    dur = len(x) / sr
    n_win = int(dur / WIN) + 1

    dens = midi_density(a.midi, n_win)
    rms, flux = audio_windows(x, sr, n_win)

    r_flux = corr(dens, flux)
    r_rms = corr(dens, rms)

    if r_flux >= GOOD_FLUX and r_rms >= GOOD_RMS:
        verdict = "통과"
    elif r_flux < BAD_FLUX or r_rms < BAD_RMS:
        verdict = "실패"
    else:
        verdict = "보류"

    res = {
        "midi": str(a.midi), "audio": str(a.audio),
        "audio_sec": round(dur, 3), "win_s": WIN,
        "n_notes": int(dens.sum()),
        "corr_flux": round(r_flux, 3), "corr_rms": round(r_rms, 3),
        "verdict": verdict,
        "line": {"통과": [GOOD_FLUX, GOOD_RMS], "실패": [BAD_FLUX, BAD_RMS]},
        "controls": {"19": [0.524, 0.235, "맞음"], "22": [0.495, 0.328, "맞음"],
                     "30": [0.104, 0.008, "실패"], "23": [0.068, -0.032, "불량"]},
        "note": "통제군은 19·22(맞음)·30·23(실패) 네 곡뿐이다. 통과는 '소리와 어긋나지 않음'까지.",
        "warning": "이 값은 옛 진단(19 +0.712 / 30 −0.423)과 자가 다르다. 섞어 쓰지 말 것.",
    }

    if a.out:
        Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"  음 시작 {res['n_notes']}개 · 창 {WIN*1000:.0f}ms · 길이 {dur:.2f}s")
        print(f"  소리와의 상관 — 온셋플럭스 {r_flux:+.3f} · RMS {r_rms:+.3f}")
        print(f"  판정: {verdict}  (통과 flux≥{GOOD_FLUX}·rms≥{GOOD_RMS} · 실패 flux<{BAD_FLUX}·rms<{BAD_RMS})")
        print("  통제군(이 구현으로 다시 잰 값) 19 +0.524/+0.235 ✓ · 22 +0.495/+0.328 ✓"
              " · 30 +0.104/+0.008 ✗ · 23 +0.068/−0.032 ✗")
    return 0 if verdict == "통과" else 1


if __name__ == "__main__":
    sys.exit(main())
