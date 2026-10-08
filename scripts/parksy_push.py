#!/usr/bin/env python3
"""parksy.kr 에 파일 묶음을 한 커밋으로 올린다. Git Data API — 중간 상태 없이 원자적.

    python3 scripts/parksy_push.py <올릴폴더> <원격경로> "<커밋메시지>"
    python3 scripts/parksy_push.py --rm <원격경로> "<커밋메시지>" <지울상대경로>...

HTTP 는 curl 로 한다. urllib 은 11MB 짜리 blob 에서 400 malformed 를 뱉었다 (실측).
토큰은 환경에서 읽고 절대 출력하지 않는다.

⚠️ 올릴 폴더를 **곡 폴더(site/<slug>) 그대로 주면 안 된다** — 그 안에는 page.py 와
   __pycache__ 가 같이 있어서 **우리 소스가 공개 사이트로 새어 나간다.** 2026-10-08 에
   실제로 그렇게 올려 page.py 와 .pyc 가 200 으로 서빙됐다(다른 곡들은 404 였다 —
   곧 이건 그때 처음 생긴 일이다). 자산을 올릴 때는 /tmp 에 **img·audio 만 복사한
   임시 폴더**를 만들어 그걸 넘길 것. 그리고 --rm 으로 지울 수 있다.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "dtslib1979/parksy.kr"
BRANCH = "main"
API = "https://api.github.com"

# --rm 모드: 지울 경로를 트리에 sha:null 로 얹으면 그 경로가 사라진다.
# base_tree 병합이라 "없는 파일"을 표현할 방법이 이것뿐이다.
RM = sys.argv[1] == "--rm"
if RM:
    DEST = sys.argv[2].strip("/")
    MSG = sys.argv[3]
    RM_PATHS = sys.argv[4:]
    ROOT = Path(".")
else:
    ROOT = Path(sys.argv[1])
    DEST = sys.argv[2].strip("/")
    MSG = sys.argv[3]
TOKEN = os.environ["GITHUB_TOKEN"]


def _header_file():
    """토큰을 argv 에 싣지 않기 위한 curl 설정 파일을 만든다 (0600).

    왜: 예전에는 `curl -H "Authorization: Bearer <TOKEN>"` 처럼 **명령줄에** 실었다.
    그러면 `ps` 를 하는 누구에게나 토큰이 그대로 보인다 — 2026-10-09 에 실제로
    그렇게 새는 것을 확인했다(ps 출력에 ghp_… 가 그대로 찍혔다).
    curl 의 -K 설정 파일은 argv 에 안 남으므로 그 경로를 없앤다.
    """
    fh = tempfile.NamedTemporaryFile("w", suffix=".curlrc", delete=False)
    os.chmod(fh.name, 0o600)
    fh.write('header = "Authorization: Bearer %s"\n' % TOKEN)
    fh.write('header = "Accept: application/vnd.github+json"\n')
    fh.write('header = "User-Agent: parksy-phone"\n')
    fh.write('header = "Content-Type: application/json"\n')
    fh.close()
    return fh.name


CFG = _header_file()
import atexit as _atexit   # noqa: E402


def _drop_cfg():
    try:
        os.unlink(CFG)
    except OSError:
        pass


_atexit.register(_drop_cfg)


def call(method, path, payload=None, tries=4):
    last = ""
    for k in range(tries):
        cmd = ["curl", "-s", "-m", "300", "-K", CFG, "-X", method,
               "-w", "\n%{http_code}"]
        tmp = None
        if payload is not None:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                json.dump(payload, fh)
                tmp = fh.name
            cmd += ["--data-binary", "@" + tmp]
        cmd.append(API + path)
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        body, _, code = out.stdout.rpartition("\n")
        code = code.strip()
        if code.startswith("2"):
            return json.loads(body or "{}")
        last = "%s %s → %s %s" % (method, path, code, body[:300])
        if code in ("502", "503", "504") and k < tries - 1:
            continue
        raise SystemExit("실패 " + last)
    raise SystemExit("실패 " + last)


base_commit = call("GET", "/repos/%s/git/ref/heads/%s" % (REPO, BRANCH))["object"]["sha"]
base_tree = call("GET", "/repos/%s/git/commits/%s" % (REPO, base_commit))["tree"]["sha"]
print("기준 커밋 %s" % base_commit[:10])

entries = []
if RM:
    if not RM_PATHS:
        raise SystemExit("--rm 에는 지울 경로가 하나 이상 필요하다")
    for i, p in enumerate(RM_PATHS, 1):
        # 절대경로나 원격경로로 줘도 되게 정규화한다 — 손으로 칠 때 틀리기 쉬운 자리다.
        rel = p.strip("/")
        if rel.startswith(DEST + "/"):
            rel = rel[len(DEST) + 1:]
        entries.append({"path": "%s/%s" % (DEST, rel), "mode": "100644",
                        "type": "blob", "sha": None})
        print("  [%d/%d] 삭제 %s" % (i, len(RM_PATHS), "%s/%s" % (DEST, rel)))
else:
    files = sorted(f for f in ROOT.rglob("*") if f.is_file())
    for i, f in enumerate(files, 1):
        rel = "%s/%s" % (DEST, f.relative_to(ROOT).as_posix())
        blob = call("POST", "/repos/%s/git/blobs" % REPO, {
            "content": base64.b64encode(f.read_bytes()).decode(),
            "encoding": "base64",
        })
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print("  [%d/%d] %-56s %9d B" % (i, len(files), rel, f.stat().st_size))

tree = call("POST", "/repos/%s/git/trees" % REPO,
            {"base_tree": base_tree, "tree": entries})["sha"]
commit = call("POST", "/repos/%s/git/commits" % REPO,
              {"message": MSG, "tree": tree, "parents": [base_commit]})["sha"]
call("PATCH", "/repos/%s/git/refs/heads/%s" % (REPO, BRANCH), {"sha": commit})
print("커밋 %s → %s" % (commit[:10], BRANCH))
print("https://parksy.kr/%s/" % DEST)
