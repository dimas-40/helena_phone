#!/usr/bin/env python3
"""parksy-midi. YouTube 음원을 MIDI로 뽑아 편곡하고 다시 렌더하는 레인.

미디 파일을 구하는 서버가 아니다. 이미 YouTube에 올라간 음원에서 음을 뽑는다.
그 채널들이 MIDI로 렌더링해 올린 음원이면 전사가 거의 무손실이다 —
사람이 연주한 음원은 템포·성부가 흔들려 뽑기가 어렵다.

흐름: 음원 → 추출(MIDI) → 편곡 → 렌더(내 악기).
전사는 느리다(실시간 대비 약 4배). 그래서 추출은 작업(job)으로 돌리고
midi_job 으로 상태를 본다. 편곡·렌더는 즉시 끝난다.

값을 지어내지 않는다. 못 하면 못 한다고 말한다.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
SCRIPTS = WORK / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.mcpserver import MCPServer  # noqa: E402

import midi_extract as mx  # noqa: E402

LANE = WORK / "midi_lane"
JOBS = LANE / "jobs"
OUT = LANE / "out"
WORKDIR = LANE / "work"
EXTRACTOR = SCRIPTS / "midi_extract.py"

SF2_DEFAULT = "/usr/share/sounds/sf2/default-GM.sf2"
SF2_CANDIDATES = [
    "/usr/share/sounds/sf2/default-GM.sf2",
    "/usr/share/sounds/sf2/TimGM6mb.sf2",
    "/usr/share/sounds/sf3/default-GM.sf3",
]

server = MCPServer(
    "parksy-midi",
    version="1.0.0",
    instructions=(
        "parksy-midi. YouTube 음원에서 음을 뽑아 MIDI로 만들고, 편곡하고, 다시 렌더한다. "
        "미디 파일을 검색해 받는 서버가 아니다 — 음원에서 뽑는다. "
        "전사는 실시간 대비 약 4배 걸린다. midi_extract 는 작업을 시작만 하고 job_id 를 주며, "
        "midi_job 으로 상태를 확인한다. 끝나면 midi_report 로 내용을 보고, "
        "midi_arrange 로 편곡하고, midi_render 로 소리를 낸다. "
        "사람이 연주한 음원은 템포와 성부가 흔들려 추출이 부정확하다. "
        "MIDI로 렌더링해 올린 음원을 쓰는 것이 이 서버의 전제다."
    ),
)


def _safe(name, fallback="out"):
    name = re.sub(r'[\\/:*?"<>|]', "", name or "").strip()[:80]
    return name or fallback


def _job_path(job_id):
    return JOBS / ("%s.json" % job_id)


def _read_job(job_id):
    path = _job_path(job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_job(job):
    JOBS.mkdir(parents=True, exist_ok=True)
    _job_path(job["job_id"]).write_text(
        json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")


def _alive(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


def _sf2(preferred=""):
    for cand in ([preferred] if preferred else []) + SF2_CANDIDATES:
        if cand and Path(cand).is_file():
            return cand
    return ""


def _fluidsynth():
    return shutil.which("fluidsynth") or ""


@server.tool()
def midi_extract(
    url: str,
    name: str = "",
    strategy: str = "melody",
    grid: int = 4,
    key: str = "auto",
    bpm: float = 0.0,
    program: int = 0,
    keep_raw: bool = False,
) -> str:
    """YouTube 음원에서 음을 뽑아 MIDI로 만든다. 작업을 시작하고 job_id를 돌려준다.

    전사는 느리다(200초 음원에 약 13분). 돌려준 job_id 로 midi_job 을 불러 확인한다.

    Args:
        url: YouTube 주소 또는 로컬 오디오 파일 경로.
        name: 출력 이름. 비우면 URL에서 딴다.
        strategy: 단선율화 규칙. melody=skyline+연속성(권장), strong=가장 센 음,
            top=가장 높은 음, low=가장 낮은 음. 넷 다 휴리스틱이고 멜로디를 보장하지 않는다.
        grid: 양자화 격자. 4=16분음표, 0=끄기.
        key: auto 또는 C, D#m 처럼 강제 지정.
        bpm: 0이면 자동 추정. 자동 추정은 인간 연주에서 크게 틀린다.
        program: GM 악기 번호. 0=Acoustic Grand.
        keep_raw: 전사 원본(단선율화 전)도 남긴다.
    """
    if not url.strip():
        return "실패: url 이 비었다"
    if not EXTRACTOR.is_file():
        return "실패: 추출기 없음 %s" % EXTRACTOR

    JOBS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    WORKDIR.mkdir(parents=True, exist_ok=True)

    job_id = "midi-%s" % uuid.uuid4().hex[:10]
    stem = _safe(name or Path(url.split("?")[0]).stem, "out")
    log = JOBS / ("%s.log" % job_id)

    cmd = [
        sys.executable, str(EXTRACTOR), url,
        "-o", str(OUT), "--name", stem,
        "--strategy", strategy, "--grid", str(grid),
        "--key", key, "--program", str(program),
    ]
    if bpm and bpm > 0:
        cmd += ["--bpm", str(bpm)]
    if keep_raw:
        cmd += ["--keep-raw"]

    with open(log, "wb") as fh:
        proc = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT,
                                cwd=str(WORK), start_new_session=True)

    job = {
        "job_id": job_id, "kind": "extract", "pid": proc.pid,
        "name": stem, "url": url, "started": time.time(),
        "started_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
        "log": str(log), "outdir": str(OUT),
        "midi": str(OUT / ("%s.mid" % stem)),
        "csv": str(OUT / ("%s.csv" % stem)),
        "cmd": cmd,
    }
    _write_job(job)

    return "\n".join([
        "parksy-midi · 추출 시작",
        "job_id %s" % job_id,
        "이름 %s" % stem,
        "pid %s" % proc.pid,
        "출력 %s" % job["midi"],
        "전사는 실시간 대비 약 4배 걸린다. midi_job(job_id=\"%s\") 로 확인한다." % job_id,
    ])


@server.tool()
def midi_job(job_id: str) -> str:
    """추출 작업의 상태와 결과를 본다.

    Args:
        job_id: midi_extract 가 돌려준 값.
    """
    job = _read_job(job_id)
    if not job:
        known = sorted(p.stem for p in JOBS.glob("*.json"))[-5:] if JOBS.is_dir() else []
        return "실패: 모르는 job_id %s\n최근: %s" % (job_id, ", ".join(known) or "(없음)")

    log_path = Path(job.get("log", ""))
    tail = ""
    if log_path.is_file():
        try:
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-1200:]
        except OSError:
            tail = ""

    alive = _alive(job.get("pid"))
    midi = Path(job.get("midi", ""))
    done = midi.is_file()
    elapsed = int(time.time() - job.get("started", time.time()))

    if done:
        state = "완료"
    elif alive:
        state = "진행 중"
    else:
        state = "중단됨 (pid 죽음)"

    lines = [
        "parksy-midi · %s" % job_id,
        "상태 %s · 경과 %d초" % (state, elapsed),
        "이름 %s" % job.get("name", "?"),
    ]
    if done:
        lines.append("MIDI %s (%d bytes)" % (midi, midi.stat().st_size))
        lines.append("노트표 %s" % job.get("csv", "?"))
    if tail.strip():
        lines.append("--- 로그 끝 ---")
        lines.append(tail.strip())
    return "\n".join(lines)


@server.tool()
def midi_report(path: str) -> str:
    """MIDI 파일 안을 본다. 음 수, 음역, 조, BPM, 동시발음 여부.

    Args:
        path: MIDI 파일 경로.
    """
    p = Path(path)
    if not p.is_file():
        return "실패: 파일 없음 %s" % p
    try:
        notes, ppq, tempo = mx.read_notes(p)
    except Exception as exc:  # noqa: BLE001
        return "실패: 읽기 오류 %s" % str(exc)[:300]
    if not notes:
        return "실패: 음이 0개다 %s" % p

    # 동시발음 검사 (진짜 단선율인가)
    ordered = sorted(notes, key=lambda n: n[0])
    overlap = sum(1 for a, b in zip(ordered, ordered[1:]) if b[0] < a[1] - 1e-6)

    bpm = mx.estimate_bpm(notes)
    tonic, mode = mx.detect_key(notes)
    pitches = [n[2] for n in notes]
    span = notes[-1][1] - notes[0][0]

    lines = [
        "parksy-midi · %s" % p.name,
        "음 %d개 · ppq %s · 길이 %.1f초" % (len(notes), ppq, span),
        "음역 %s ~ %s" % (mx.note_name(min(pitches)), mx.note_name(max(pitches))),
        "조 %s %s · BPM 추정 %.1f" % (mx.note_name(60 + tonic), mode, bpm),
        "동시발음 %d곳 %s" % (overlap, "(단선율)" if overlap == 0 else "(화음 있음)"),
    ]

    # 소재 판정 — 추출 때 옆에 남긴 것이 있으면 읽는다.
    # 단선율화 뒤에는 격자 정보가 사라져 여기서 다시 계산할 수 없다.
    # <name>_raw.mid 로 물어봐도 <name>.verdict.json 을 찾는다
    cands = [p.with_suffix(".verdict.json")]
    if p.stem.endswith("_raw"):
        cands.append(p.with_name(p.stem[:-4] + ".verdict.json"))
    side = next((c for c in cands if c.is_file()), cands[0])
    if side.is_file():
        try:
            v = json.loads(side.read_text(encoding="utf-8"))
            lines.append("소재 %s — 격자정렬 %s%% · 어긋남 %s%%" % (
                v.get("verdict", "?"), v.get("grid_pct", "?"), v.get("smear_pct", "?")))
        except (OSError, ValueError):
            pass
    else:
        lines.append("소재 판정 없음 — 단선율화 뒤라 격자 정보가 없다. "
                     "원본으로 보려면 추출 때 --keep-raw 를 켠다.")

    lines.append("앞 16음 " + " ".join(mx.note_name(n[2]) for n in ordered[:16]))
    return "\n".join(lines)


@server.tool()
def midi_arrange(
    path: str,
    transpose: int = 0,
    program: int = -1,
    bpm: float = 0.0,
    time_scale: float = 1.0,
    fit_octave: bool = False,
    out_name: str = "",
) -> str:
    """MIDI를 편곡한다 — 조옮김·악기 교체·템포. 새 파일로 쓴다. 원본은 건드리지 않는다.

    Args:
        path: 원본 MIDI 경로.
        transpose: 반음 단위 조옮김. 0이면 그대로.
        program: GM 악기 번호. -1이면 원본 유지.
        bpm: 0이면 원본 유지.
        time_scale: 길이 배율. 0.5=두 배 빠르게, 2.0=두 배 느리게. 1.0이면 그대로.
        fit_octave: True 면 음역을 C3~C6 안으로 옥타브 단위로 당긴다.
        out_name: 출력 이름. 비우면 <원본>-arr.
    """
    src = Path(path)
    if not src.is_file():
        return "실패: 파일 없음 %s" % src
    if time_scale <= 0:
        return "실패: time_scale 은 0보다 커야 한다 (받은 값 %s)" % time_scale

    try:
        notes, ppq, tempo = mx.read_notes(src)
    except Exception as exc:  # noqa: BLE001
        return "실패: 읽기 오류 %s" % str(exc)[:300]
    if not notes:
        return "실패: 음이 0개다"

    before = len(notes)
    if transpose:
        notes = [[n[0], n[1], n[2] + transpose, n[3]] for n in notes]

    if fit_octave:
        pitches = [n[2] for n in notes]
        shift = 0
        while min(pitches) + shift < 48 and shift < 48:
            shift += 12
        while max(pitches) + shift > 84 and shift > -48:
            shift -= 12
        if shift:
            notes = [[n[0], n[1], n[2] + shift, n[3]] for n in notes]
            transpose += shift

    if time_scale != 1.0:
        notes = [[n[0] * time_scale, n[1] * time_scale, n[2], n[3]] for n in notes]

    # 원본 program 을 모르면 0 으로 본다 (midi_extract 는 0으로 쓴다)
    out_program = program if program >= 0 else 0
    out_bpm = bpm if bpm and bpm > 0 else (mx.estimate_bpm(notes) or 120.0)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = _safe(out_name or (src.stem + "-arr"), "arr")
    dest = OUT / ("%s.mid" % stem)
    mx.write_midi(notes, dest, bpm=out_bpm, ppq=ppq, program=out_program)
    mx.write_csv(notes, OUT / ("%s.csv" % stem))

    gm = mx.NOTES
    return "\n".join([
        "parksy-midi · 편곡",
        "원본 %s (%d음)" % (src.name, before),
        "결과 %s" % dest,
        "조옮김 %+d반음 · 악기 GM%s · BPM %.1f · 길이배율 %.2f" % (
            transpose, out_program, out_bpm, time_scale),
        "원본은 건드리지 않았다. 이 파일을 midi_render 에 넘긴다.",
    ])


@server.tool()
def midi_render(
    path: str,
    sf2: str = "",
    fmt: str = "mp3",
    gain: float = 0.7,
    reverb: float = 0.7,
    normalize: bool = True,
    out_name: str = "",
) -> str:
    """MIDI를 소리로 렌더한다 (FluidSynth + GM 사운드폰트).

    내 가상악기 렌더가 아니라 GM 렌더다. 초안 확인용으로만 쓴다.

    Args:
        path: MIDI 파일 경로.
        sf2: 사운드폰트 경로. 비우면 있는 것 중에 고른다.
        fmt: wav 또는 mp3.
        gain: 0.0~1.0 볼륨.
        reverb: 0.0~1.2 잔향. 0이면 끈다.
        normalize: True 면 ffmpeg loudnorm 으로 음량을 고른다.
        out_name: 출력 이름. 비우면 MIDI 이름을 따른다.
    """
    src = Path(path)
    if not src.is_file():
        return "실패: 파일 없음 %s" % src

    fs = _fluidsynth()
    if not fs:
        return "실패: fluidsynth 가 없다. 렌더할 수 없다."
    font = _sf2(sf2)
    if not font:
        return "실패: 사운드폰트가 없다. 찾은 자리: %s" % ", ".join(SF2_CANDIDATES)
    if fmt not in ("wav", "mp3"):
        return "실패: fmt 는 wav 또는 mp3 다 (받은 값 %s)" % fmt
    if not 0.0 < gain <= 1.0:
        return "실패: gain 은 0 초과 1 이하다 (받은 값 %s)" % gain
    if not 0.0 <= reverb <= 1.2:
        return "실패: reverb 는 0~1.2 다 (받은 값 %s)" % reverb

    OUT.mkdir(parents=True, exist_ok=True)
    stem = _safe(out_name or src.stem, "render")
    wav = OUT / ("%s.wav" % stem)
    dest = OUT / ("%s.%s" % (stem, fmt))

    cmd = [fs, "-ni", "-g", "%.2f" % gain,
           "-o", "synth.reverb.active=%d" % (1 if reverb > 0 else 0),
           "-o", "synth.reverb.room-size=%.2f" % min(reverb, 1.2),
           "-o", "synth.reverb.level=0.85",
           "-o", "synth.chorus.active=0",
           "-F", str(wav), font, str(src)]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900)
    except subprocess.TimeoutExpired:
        return "실패: 렌더가 900초를 넘었다"
    if r.returncode != 0 or not wav.is_file():
        err = (r.stderr or b"").decode("utf-8", "replace")[-400:]
        return "실패: fluidsynth 종료코드 %s\n%s" % (r.returncode, err)

    ff = shutil.which("ffmpeg")
    notes = []
    if fmt == "mp3":
        if not ff:
            return ("부분 성공: wav 는 나왔다 %s\n"
                    "mp3 는 실패 — ffmpeg 가 없다. wav 를 쓴다." % wav)
        codec = [ff, "-y", "-i", str(wav)]
        if normalize:
            codec += ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"]
        codec += ["-codec:a", "libmp3lame", "-qscale:a", "2", str(dest)]
        r2 = subprocess.run(codec, capture_output=True, timeout=600)
        if r2.returncode != 0 or not dest.is_file():
            return ("부분 성공: wav 는 나왔다 %s\nmp3 변환이 실패했다 — wav 를 쓴다." % wav)
        if normalize:
            notes.append("loudnorm -16 LUFS")
        try:
            wav.unlink()
        except OSError:
            pass
    else:
        dest = wav

    size = dest.stat().st_size
    return "\n".join([
        "parksy-midi · 렌더",
        "결과 %s (%d bytes)" % (dest, size),
        "사운드폰트 %s" % font,
        "gain %.2f · 잔향 %.2f · %s" % (gain, reverb, fmt),
    ] + notes + [
        "GM 렌더다. 내 가상악기 렌더가 아니다.",
    ])


@server.tool()
def midi_list(limit: int = 20) -> str:
    """이 레인에 있는 MIDI와 렌더 결과를 본다.

    Args:
        limit: 최근 몇 개까지 볼지.
    """
    if not OUT.is_dir():
        return "아직 아무것도 없다. %s 가 비어 있다." % OUT
    midis = sorted(OUT.glob("*.mid"), key=lambda p: -p.stat().st_mtime)[:limit]
    audios = sorted([p for p in OUT.glob("*.*") if p.suffix in (".wav", ".mp3")],
                    key=lambda p: -p.stat().st_mtime)[:limit]
    if not midis and not audios:
        return "아직 아무것도 없다. %s 가 비어 있다." % OUT
    lines = ["parksy-midi · 레인 %s" % OUT]
    if midis:
        lines.append("MIDI %d개" % len(list(OUT.glob('*.mid'))))
        for p in midis:
            lines.append("  %s (%d bytes)" % (p.name, p.stat().st_size))
    if audios:
        lines.append("렌더 %d개" % len(list(OUT.glob('*.wav')) + list(OUT.glob('*.mp3'))))
        for p in audios:
            lines.append("  %s (%d bytes)" % (p.name, p.stat().st_size))
    return "\n".join(lines)


if __name__ == "__main__":
    server.run(transport="stdio")
