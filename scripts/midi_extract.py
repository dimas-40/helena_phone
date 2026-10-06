#!/usr/bin/env python3
"""음원 → 단선율 피아노 MIDI 추출 (S25 Ultra proot 상주)

Boss 2026-10-06:
  "유튜브에 업로드돼 있는 음원을 추출해서 미디 파일을 추출하는 방법,
   이게 미디 파일 구하는 것보다 훨씬 좋은 방법이야."
  "어차피 단선율 피아노만 나온다고 하면 다른 악기로 갈아끼우면 되는 거고,
   오케스트레이션은 나중에. 지금은 단선율이 중요한 거야."

정본 근거:
  parksy-audio/pre-season/xtract/README.md      — yt-dlp → MIDI 파이프라인
  parksy-audio/pre-season/pipeline/transcriber.py — 악기 라우팅(피아노 → piano_transcription)
  docs/pre-season/MUSIC-PIPELINE-DECISION-2026-03-15.md — 모델 비교(Melodyne 98% / Basic Pitch 70%)

이 폰에서의 실측 (2026-10-06):
  basic-pitch          ❌ numpy<1.24 강제 + tensorflow 필요 → py3.14에 둘 다 없음
  librosa.pyin/piptrack ❌ numba JIT가 aarch64 LLVM 버그로 크래시
                          (UNREACHABLE at TargetSchedule.cpp)
  piano_transcription  ✅ 순수 torch. torch 2.14.0+cpu 가 이미 깔려 있음

그래서 파이프라인은 torch 경로만 쓴다. numba 경로는 절대 건드리지 않는다.
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(pitch: int) -> str:
    return f"{NOTES[pitch % 12]}{pitch // 12 - 1}"


# ─────────────────────────────────────────────────────────────
# 1. 소스 얻기
# ─────────────────────────────────────────────────────────────

def fetch_audio(src: str, out_wav: Path, sr: int) -> Path:
    """URL이면 yt-dlp로, 아니면 로컬 파일로. 최종적으로 wav 하나를 만든다."""
    if src.startswith(("http://", "https://")):
        tmp = out_wav.with_suffix(".dl.wav")
        cmd = [
            "yt-dlp", "--no-playlist", "-x", "--audio-format", "wav",
            "--postprocessor-args", f"-ar {sr} -ac 1",
            "-o", str(tmp.with_suffix(".%(ext)s")), src,
        ]
        print(f"[1/6] 유튜브에서 음원 추출: {src}")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"yt-dlp 실패:\n{r.stderr[-800:]}")
        # -x 는 <stem>.wav 로 떨어뜨린다
        produced = tmp.with_suffix(".wav")
        if produced.exists():
            produced.rename(out_wav)
        else:
            cands = list(out_wav.parent.glob("*.wav"))
            if not cands:
                raise SystemExit("yt-dlp가 wav를 만들지 못했다")
            cands[0].rename(out_wav)
        print(f"      → {out_wav} ({out_wav.stat().st_size/1e6:.1f}MB)")
        return out_wav

    src_path = Path(src)
    if not src_path.exists():
        raise SystemExit(f"파일 없음: {src}")
    print(f"[1/6] 로컬 파일 사용: {src_path}")
    return src_path


# ─────────────────────────────────────────────────────────────
# 2. 전사 (torch 경로만)
# ─────────────────────────────────────────────────────────────

def transcribe(audio_path: Path, out_mid: Path) -> None:
    """piano_transcription_inference 로 전사.

    ⚠️ 이 패키지의 load_audio() 는 librosa<1.0 내부 경로를 쓴다.
       librosa 1.0 에서는 사라져서 AttributeError 가 난다 → 직접 로드해 우회한다.
    """
    import librosa
    from piano_transcription_inference import PianoTranscription, sample_rate

    print(f"[2/6] 전사 시작 (sample_rate={sample_rate})")
    y, _ = librosa.load(str(audio_path), sr=sample_rate, mono=True)
    dur = len(y) / sample_rate
    print(f"      오디오 {dur:.1f}s → CPU 추론 (대략 실시간 1배)")

    tr = PianoTranscription(device="cpu", checkpoint_path=None)
    tr.transcribe(y, str(out_mid))
    print(f"      → {out_mid}")


# ─────────────────────────────────────────────────────────────
# 3. MIDI 읽기
# ─────────────────────────────────────────────────────────────

def read_notes(mid_path: Path):
    """MIDI → (notes, ticks_per_beat, tempo_us).

    notes = [[start_sec, end_sec, pitch, velocity], ...]
    """
    import mido

    mf = mido.MidiFile(str(mid_path))
    ppq = mf.ticks_per_beat
    tempo = 500000  # 기본 120 BPM
    notes = []

    for track in mf.tracks:
        abs_tick = 0
        pending = {}
        for msg in track:
            abs_tick += msg.time
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "note_on" and msg.velocity > 0:
                pending.setdefault(msg.note, []).append((abs_tick, msg.velocity))
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if pending.get(msg.note):
                    start_tick, vel = pending[msg.note].pop(0)
                    notes.append([
                        mido.tick2second(start_tick, ppq, tempo),
                        mido.tick2second(abs_tick, ppq, tempo),
                        msg.note,
                        vel,
                    ])
    notes.sort(key=lambda n: (n[0], -n[3]))
    return notes, ppq, tempo


# ─────────────────────────────────────────────────────────────
# 4. 단선율화 — 이 파이프라인의 핵심
# ─────────────────────────────────────────────────────────────

def melody_skyline(c, prev_pitch, max_leap=12, min_dur=0.04):
    """한 화음 묶음에서 멜로디 음 하나를 고른다 — skyline + 연속성.

    순수 skyline(무조건 최고음)은 반주 상성부·꾸밈음을 멜로디로 착각한다.
    그래서 앞 멜로디 음에서 한 옥타브(max_leap) 안에 있는 후보를 먼저 본다.
    그 안에 있으면 그중 최고음, 없으면 앞 음에 가장 가까운 음.

    실측 근거(2026-10-06): 트뢰메라이(쉬만)에서 strong·top 전략 모두
    음역이 F2~A#5(3.4옥타브)로 벌어졌다. 단선율 멜로디는 1옥타브 안이어야 한다.
    """
    if not c:
        return None
    # 꾸밈음 후보를 뒤로 미룬다 — 긴 음이 있으면 그쪽을 먼저 본다
    long_notes = [n for n in c if (n[1] - n[0]) >= min_dur] or c
    if prev_pitch is None:
        return max(long_notes, key=lambda n: n[2])

    near = [n for n in long_notes if abs(n[2] - prev_pitch) <= max_leap]
    if near:
        return max(near, key=lambda n: n[2])
    # 옥타브 안에 후보가 없다 = 앞 음이 틀렸거나 새 악구다.
    # 여기서 '앞 음에 가장 가까운 것'을 고르면 아래로 드리프트한다.
    # 실측(2026-10-06): 그 규칙 때문에 트뢰메라이 멜로디가 A#1·F1까지 내려가
    # 음역이 4.4옥타브로 벌어졌다. 멜로디는 위성부이므로 최고음을 잡는다.
    return max(long_notes, key=lambda n: n[2])


def smooth_melody(notes, window=7, max_dev=14):
    """멜로디 선의 튀는 음을 중앙값으로 눌러준다.

    멜로디는 매끄럽게 움직인다. 갑자기 30반음 아래로 떨어진 음은 멜로디가 아니라
    베이스가 잘못 딸려온 것이다. 실측(2026-10-06): melody 전략이 트뢰메라이에서
    84%를 5~6옥타브에 몰았는데 A#1 한 음이 튀어 음역이 4옥타브로 벌어졌다.

    지우지 않고 **고친다** — 리듬이 사라지면 곡이 끊긴다.
    같은 음이름에서 중앙값에 가장 가까운 옥타브로 옮긴다.

    Returns: (고친 음 목록, 고친 개수)
    """
    if len(notes) < window:
        return notes, 0
    ordered = sorted(notes, key=lambda n: n[0])
    pitches = [n[2] for n in ordered]
    half = window // 2
    fixed = 0
    out = []
    for i, n in enumerate(ordered):
        lo, hi = max(0, i - half), min(len(pitches), i + half + 1)
        med = int(statistics.median(pitches[lo:hi]))
        if abs(n[2] - med) > max_dev:
            # 같은 음이름 유지한 채 중앙값에 가장 가까운 옥타브로
            cands = [med + 12 * k for k in range(-5, 6)]
            new = min(cands, key=lambda p: (abs(p - n[2]), abs(p - med)))
            out.append([n[0], n[1], new, n[3]])
            fixed += 1
        else:
            out.append(list(n))
    if fixed:
        print(f"      멜로디 다듬기: 튄 음 {fixed}개를 중앙값으로 (창 {window}, 허용 {max_dev}반음)")
    return out, fixed


def monophonize(notes, strategy="strong", octave_dedup=True, onset_window=0.06):
    """동시발음을 하나의 선율로 접는다.

    실측 근거(2026-10-06): 43음 중 절반이 동시발음이었고, 대부분 D#4+D#5 같은
    옥타브 중복이었다. 모델이 배음을 옥타브 위로 같이 잡는 습성이다.

    ⚠️ 겹침(overlap)으로 묶으면 안 된다. 음이 꼬리를 물고 이어지면
       0.02초 음과 15초 음이 한 덩어리로 사슬처럼 뭉쳐 앞부분이 통째로 사라진다.
       (실측: 43음이 19음으로 과다 축약, 첫 음 소실)
       → **온셋이 가까운 것끼리** 묶는다. 실제 화음·옥타브 중복은 같은 시각에 뜬다.

    strategy:
      melody — skyline + 연속성 (권장). 멜로디를 노린다
      strong — velocity 최대. 사람이 실제로 눌렀을 가능성이 큰 음
      top    — 최고음. 순수 skyline 이라 반주 상성부를 멜로디로 착각한다
      low    — 최저음. 베이스 모티프를 뽑을 때
    """
    if not notes:
        return []

    ordered = sorted(notes, key=lambda n: n[0])
    clusters = []
    for n in ordered:
        if clusters and (n[0] - clusters[-1][0][0]) <= onset_window:
            clusters[-1].append(n)
        else:
            clusters.append([n])

    picked = []
    prev_pitch = None
    for c in clusters:
        if len(c) == 1:
            win = c[0]
        else:
            # 옥타브 중복 제거: 정확히 12반음 차이가 나는 짝이 있으면 하나만 남긴다
            if octave_dedup:
                by_pitch = {n[2]: n for n in c}
                for p in list(by_pitch):
                    if p + 12 in by_pitch:
                        hi, lo = by_pitch[p + 12], by_pitch[p]
                        if strategy == "top":
                            drop = lo
                        elif strategy == "melody" and prev_pitch is not None:
                            # 앞 멜로디 음에 가까운 쪽을 남긴다
                            drop = hi if abs(lo[2] - prev_pitch) <= abs(hi[2] - prev_pitch) else lo
                        else:
                            drop = hi
                        c = [x for x in c if x is not drop]
            if not c:
                continue
            if strategy == "top":
                win = max(c, key=lambda n: n[2])
            elif strategy == "low":
                win = min(c, key=lambda n: n[2])
            elif strategy == "melody":
                win = melody_skyline(c, prev_pitch)
                if win is None:
                    continue
            else:  # strong
                win = max(c, key=lambda n: (n[3], n[2]))
        picked.append(list(win))
        prev_pitch = win[2]

    # 레가토 정리: 다음 음이 시작하면 앞 음을 끊는다 (진짜 단선율)
    picked.sort(key=lambda n: n[0])
    for i in range(len(picked) - 1):
        if picked[i][1] > picked[i + 1][0]:
            picked[i][1] = picked[i + 1][0]
    out = [n for n in picked if n[1] - n[0] > 1e-4]
    print(f"[3/6] 단선율화: {len(notes)}음 → {len(out)}음 "
          f"(동시발음 {len(notes)-len(out)}개 접음, 전략={strategy})")
    return out


# ─────────────────────────────────────────────────────────────
# 5. 양자화 · 조 정렬
# ─────────────────────────────────────────────────────────────

def estimate_bpm(notes):
    """온셋 간격 중앙값으로 BPM 추정. 못 하면 None."""
    if len(notes) < 4:
        return None
    starts = sorted(n[0] for n in notes)
    iois = [b - a for a, b in zip(starts, starts[1:]) if b - a > 0.05]
    if len(iois) < 3:
        return None
    iois.sort()
    med = iois[len(iois) // 2]
    # 60/med 가 60~200 BPM에 오도록 배수 조정
    bpm = 60.0 / med
    while bpm < 60:
        bpm *= 2
    while bpm > 200:
        bpm /= 2
    return bpm


def quantize(notes, bpm, grid=4, strength=1.0):
    """grid = 한 박을 몇 등분할지 (4 = 16분음표). strength 1.0 = 완전 스냅."""
    if not bpm:
        return notes, None
    beat = 60.0 / bpm
    step = beat / grid
    for n in notes:
        for i in (0, 1):
            snapped = round(n[i] / step) * step
            n[i] = n[i] + (snapped - n[i]) * strength
    print(f"[4/6] 양자화: {bpm:.1f} BPM · 1/{grid*4}음표 격자 (strength={strength})")
    return notes, (bpm, grid)


# Krumhansl-Schmuckler 단순화 — 장음계/단음계 프로파일 상관
_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def detect_key(notes):
    """길이 가중 pitch-class 히스토그램 → 최적 조."""
    import numpy as np

    if len(notes) < 5:
        return None, None
    hist = np.zeros(12)
    for s, e, p, v in notes:
        hist[p % 12] += (e - s)
    if hist.sum() == 0:
        return None, None
    hist = hist / hist.sum()

    best = (None, None, -2)
    for tonic in range(12):
        for name, prof in (("major", _MAJOR), ("minor", _MINOR)):
            p = np.roll(np.array(prof), tonic)
            p = p / p.sum()
            r = float(np.corrcoef(hist, p)[0, 1])
            if r > best[2]:
                best = (tonic, name, r)
    return best[0], best[1]


def scale_pitches(tonic, mode):
    steps = [0, 2, 4, 5, 7, 9, 11] if mode == "major" else [0, 2, 3, 5, 7, 8, 10]
    return {(tonic + s) % 12 for s in steps}


def snap_to_scale(notes, tonic, mode, max_shift=1):
    """스케일 밖 음을 가장 가까운 스케일 음으로 당긴다.

    실측 근거: 전사 결과 D4 와 D#4 가 함께 나왔다(반음 충돌).
    조가 확정되면 그중 하나는 배음 오검출일 가능성이 높다.
    """
    if tonic is None:
        return notes, 0
    ok = scale_pitches(tonic, mode)
    moved = 0
    for n in notes:
        pc = n[2] % 12
        if pc in ok:
            continue
        for d in range(1, max_shift + 1):
            if (pc - d) % 12 in ok:
                n[2] -= d
                moved += 1
                break
            if (pc + d) % 12 in ok:
                n[2] += d
                moved += 1
                break
    print(f"[5/6] 조 정렬: {note_name(60+tonic) if tonic is not None else '?'} {mode} "
          f"— 스케일 밖 {moved}음 이동")
    return notes, moved


def denoise(notes, min_dur=0.05, min_vel=20):
    before = len(notes)
    out = [n for n in notes if (n[1] - n[0]) >= min_dur and n[3] >= min_vel]
    if before != len(out):
        print(f"      잡음 제거: {before-len(out)}음 (min_dur={min_dur}s, min_vel={min_vel})")
    return out


def source_verdict(notes, grid_sec=0.125, tol=0.06, min_notes=40):
    """이 채보가 기계(MIDI 렌더)에서 나온 것인지 사람 연주인지 판정한다.

    사람은 화음을 동시에 누르지 못한다. 온셋이 수 ms 어긋나 흩어진다.
    MIDI 렌더는 격자에 딱 맞아 온셋 간격이 정확한 배수로 떨어진다.

    실측(2026-10-06):
      Clair de Lune (인간)  — 10ms 미만 어긋남 25.9% · 격자 정렬 26.0%
      Träumerei   (MIDI 렌더) — 10ms 미만 어긋남  0.0% · 격자 정렬 96.9%

    Returns: (판정, 격자정렬률, 어긋남률, 근거문자열)
    """
    ons = sorted(n[0] for n in notes)
    iv = [b - a for a, b in zip(ons, ons[1:])]
    if len(iv) < min_notes:
        return "판정불가", 0.0, 0.0, f"음이 너무 적다 ({len(notes)}개, 최소 {min_notes}개)"
    smear = sum(1 for d in iv if 0 < d < 0.01)
    grid = sum(1 for d in iv if d > 0 and abs(d / grid_sec - round(d / grid_sec)) < tol)
    n = len(iv)
    grid_pct, smear_pct = 100.0 * grid / n, 100.0 * smear / n

    if grid_pct >= 80.0:
        verdict = "기계(MIDI 렌더)"
        note = "격자에 딱 맞는다. 이 소재는 뽑기에 좋다."
    elif grid_pct >= 50.0:
        verdict = "애매"
        note = "격자에 반쯤 맞는다. 양자화된 연주이거나 전사가 흔들린 것이다."
    else:
        verdict = "사람 연주"
        note = "온셋이 흩어져 있다. 템포·성부 추출이 부정확해진다."
    return (verdict, grid_pct, smear_pct,
            f"{note} (음 {len(notes)}개, 간격 {n}개 기준)")


# ─────────────────────────────────────────────────────────────
# 6. 쓰기 — 표준화된 단일 트랙 MIDI
# ─────────────────────────────────────────────────────────────

def write_midi(notes, out_path: Path, bpm=120.0, ppq=480, program=0):
    """GM program: 0=Acoustic Grand. Boss가 나중에 악기를 갈아끼우는 기준점."""
    import mido

    mf = mido.MidiFile(type=0, ticks_per_beat=ppq)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    tr.append(mido.MetaMessage("track_name", name="Parksy Melody", time=0))
    tr.append(mido.Message("program_change", program=program, time=0))

    events = []
    for s, e, p, v in notes:
        events.append((s, "on", p, v))
        events.append((e, "off", p, 0))
    events.sort(key=lambda x: (x[0], x[1] == "on"))

    last = 0            # int 여야 한다 — float 이면 mido가 저장을 거부한다
    for t, kind, p, v in events:
        tick = int(round(mido.second2tick(float(t), ppq, mido.bpm2tempo(bpm))))
        delta = int(max(0, tick - last))
        last = tick
        tr.append(mido.Message("note_on" if kind == "on" else "note_off",
                               note=p, velocity=v, time=delta))
    mf.save(str(out_path))
    return out_path


def write_csv(notes, out_path: Path):
    import csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["start_s", "end_s", "dur_s", "midi", "note", "velocity"])
        for s, e, p, v in notes:
            w.writerow([f"{s:.3f}", f"{e:.3f}", f"{e-s:.3f}", p, note_name(p), v])
    return out_path


# ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="음원 → 단선율 피아노 MIDI")
    ap.add_argument("src", help="유튜브 URL 또는 로컬 오디오 파일")
    ap.add_argument("-o", "--outdir", default="midi_out", help="출력 폴더")
    ap.add_argument("--name", default=None, help="출력 이름 (기본: 입력 파일명)")
    ap.add_argument("--strategy", default="melody",
                    choices=["melody", "strong", "top", "low"],
                    help="단선율화 전략 (기본 melody=skyline+연속성)")
    ap.add_argument("--no-mono", action="store_true", help="단선율화 끄기(화음 유지)")
    ap.add_argument("--grid", type=int, default=4, help="양자화 격자 (4=16분음표, 0=끄기)")
    ap.add_argument("--quant-strength", type=float, default=1.0)
    ap.add_argument("--key", default="auto", help="auto 또는 C/D#m 등 강제 지정")
    ap.add_argument("--no-scale-snap", action="store_true")
    ap.add_argument("--bpm", type=float, default=None, help="BPM 강제 (기본: 자동 추정)")
    ap.add_argument("--program", type=int, default=0, help="GM 악기 번호 (0=Acoustic Grand)")
    ap.add_argument("--keep-raw", action="store_true", help="전사 원본 .mid 도 남긴다")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    name = args.name or Path(args.src.split("?")[0]).stem or "out"
    name = "".join(c for c in name if c not in '\\/:*?"<>|').strip()[:80] or "out"

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        audio = fetch_audio(args.src, td / "audio.wav", 16000)
        raw_mid = td / "raw.mid"
        transcribe(audio, raw_mid)
        if args.keep_raw:
            import shutil
            shutil.copy(raw_mid, outdir / f"{name}_raw.mid")
        notes, ppq, tempo = read_notes(raw_mid)

    # 소재 판정 — 단선율화 전 원본으로 본다 (동시발음 정보가 살아 있어야 한다)
    verdict, grid_pct, smear_pct, why = source_verdict(notes)
    print(f"[2.5/6] 소재 판정: {verdict} — 격자정렬 {grid_pct:.1f}% · 어긋남 {smear_pct:.1f}%")
    print(f"        {why}")

    print(f"[3/6] 원본 전사: {len(notes)}음 · ppq={ppq}")

    if not args.no_mono:
        notes = monophonize(notes, strategy=args.strategy)
        if args.strategy == "melody":
            notes, _ = smooth_melody(notes)
    notes = denoise(notes)

    bpm = args.bpm or estimate_bpm(notes) or 120.0
    if args.grid:
        notes, _ = quantize(notes, bpm, grid=args.grid, strength=args.quant_strength)

    if args.key == "auto":
        tonic, mode = detect_key(notes)
    else:
        import re
        mm = re.match(r"([A-G]#?)(m?)", args.key)
        tonic = NOTES.index(mm.group(1)) if mm else None
        mode = "minor" if mm and mm.group(2) else "major"
    if not args.no_scale_snap:
        notes, _ = snap_to_scale(notes, tonic, mode)

    mid = write_midi(notes, outdir / f"{name}.mid", bpm=bpm, program=args.program)
    csv = write_csv(notes, outdir / f"{name}.csv")

    # 소재 판정을 옆에 남긴다 — 단선율화 뒤에는 격자 정보가 사라지기 때문이다
    import json as _json
    (outdir / f"{name}.verdict.json").write_text(_json.dumps({
        "source": args.src, "verdict": verdict,
        "grid_pct": round(grid_pct, 1), "smear_pct": round(smear_pct, 1),
        "raw_notes": len(notes) if args.keep_raw else None,
        "why": why, "name": name,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[6/6] 완료")
    print(f"      MIDI : {mid}")
    print(f"      노트표: {csv}")
    print(f"      {len(notes)}음 · {bpm:.1f} BPM · "
          f"{note_name(60+tonic)+' '+mode if tonic is not None else '조 미상'}")
    if notes:
        span = notes[-1][1] - notes[0][0]
        print(f"      길이 {span:.1f}s · 음역 {note_name(min(n[2] for n in notes))}"
              f"~{note_name(max(n[2] for n in notes))}")


if __name__ == "__main__":
    main()
