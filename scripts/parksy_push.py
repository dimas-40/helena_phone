#!/usr/bin/env python3
"""parksy.kr 에 파일 묶음을 한 커밋으로 올린다. Git Data API — 중간 상태 없이 원자적.

HTTP 는 curl 로 한다. urllib 은 11MB 짜리 blob 에서 400 malformed 를 뱉었다 (실측).
토큰은 환경에서 읽고 절대 출력하지 않는다.
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
ROOT = Path(sys.argv[1])
DEST = sys.argv[2].strip("/")
MSG = sys.argv[3]
TOKEN = os.environ["GITHUB_TOKEN"]


def call(method, path, payload=None, tries=4):
    last = ""
    for k in range(tries):
        cmd = ["curl", "-s", "-m", "300", "-X", method,
               "-H", "Authorization: Bearer " + TOKEN,
               "-H", "Accept: application/vnd.github+json",
               "-H", "User-Agent: parksy-phone",
               "-H", "Content-Type: application/json",
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
