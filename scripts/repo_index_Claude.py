#!/usr/bin/env python3
"""28레포 전수 인덱서 (_Claude 2026-09-23)

목적: dtslib1979 계정의 28레포를 **클론 없이** GitHub API로 파싱한다.
      (디스크 140GB · proot 전체스캔 금지 규칙 → clone 대신 tree API)

산출:
  - _notebook/data/repo-index-2026-09-23.json   (기계용 SSOT)
  - _notebook/113-repo-index-28_Claude.md       (사람용 리포트)

사용: python3 scripts/repo_index_Claude.py [--owner dtslib1979]
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "dtslib1979"
DOC_EXT = {".md", ".markdown", ".txt", ".rst"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "venv", ".venv", "__pycache__"}


def token():
    if os.environ.get("GH_TOKEN"):
        return os.environ["GH_TOKEN"]
    for line in open(os.path.join(ROOT, ".secrets.env"), encoding="utf-8"):
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no GITHUB_TOKEN")


TOK = token()


def api(path):
    url = "https://api.github.com" + path
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOK,
        "Accept": "application/vnd.github+json",
        "User-Agent": "parksy-repo-index/1.0",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8")), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            if e.code == 409:  # empty repo
                return None, {}
            raise
    return None, {}


def fetch(path):
    for attempt in range(3):
        try:
            return api(path)[0]
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            if e.code == 404:
                return None
            raise
    return None


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def parse_repo(repo):
    name = repo["name"]
    meta = {
        "repo": name,
        "visibility": repo["visibility"],
        "archived": repo["archived"],
        "size_kb": repo["size"],
        "size_human": human(repo["size"] * 1024),
        "language": repo.get("language"),
        "pushed_at": (repo.get("pushedAt") or "")[:10],
        "created_at": (repo.get("createdAt") or "")[:10],
        "default_branch": repo.get("defaultBranchRef", {}).get("name") or "main",
        "has_pages": repo.get("hasPages", False),
        "homepage": repo.get("homepageUrl") or "",
        "description": repo.get("description") or "",
        "topics": repo.get("repositoryTopics", []),
    }
    br = meta["default_branch"]
    tree = fetch(f"/repos/{OWNER}/{name}/git/trees/{br}?recursive=1")
    files, dirs = [], {}
    if tree:
        meta["truncated"] = bool(tree.get("truncated"))
        for e in tree.get("tree", []):
            if e["type"] == "blob":
                files.append(e["path"])
    else:
        meta["truncated"] = None

    if not files and tree is None:
        # 빈 레포 or tree 실패 → 1단계 목록으로 폴백
        contents = fetch(f"/repos/{OWNER}/{name}/contents/") or []
        for c in contents:
            if c["type"] == "file":
                files.append(c["path"])

    top = {}
    for p in files:
        if "/" not in p:
            continue
        head = p.split("/")[0]
        top[head] = top.get(head, 0) + 1
    dirs = top

    docs = [p for p in files if os.path.splitext(p)[1].lower() in DOC_EXT]
    exts = {}
    for p in files:
        e = os.path.splitext(p)[1].lower() or "(none)"
        exts[e] = exts.get(e, 0) + 1

    # 루트 문서 = 사람이 제일 먼저 읽는 것
    root_docs = [p for p in docs if "/" not in p]
    key = [p for p in root_docs if os.path.basename(p).lower().startswith(
        ("readme", "claude", "index", "constitution", "handbook", "guide"))]

    meta.update({
        "file_count": len(files),
        "doc_count": len(docs),
        "top_dirs": dict(sorted(dirs.items(), key=lambda x: -x[1])[:12]),
        "exts": dict(sorted(exts.items(), key=lambda x: -x[1])[:10]),
        "root_docs": sorted(root_docs)[:25],
        "key_docs": sorted(key),
    })
    return meta


GH_FIELDS = ("name,visibility,isArchived,pushedAt,createdAt,description,primaryLanguage,"
             "diskUsage,defaultBranchRef,homepageUrl,repositoryTopics,isEmpty,isFork")


def list_repos(owner):
    """gh CLI = private 포함 전수. REST /users 는 공개만 주므로 쓰지 않는다."""
    cmd = f'gh repo list {owner} --limit 300 --json {GH_FIELDS}'
    raw = os.popen(cmd).read()
    out = json.loads(raw or "[]")
    repos = []
    for r in out:
        repos.append({
            "name": r["name"],
            "visibility": r["visibility"],
            "archived": r["isArchived"],
            "size": r.get("diskUsage") or 0,
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "pushedAt": r.get("pushedAt"),
            "createdAt": r.get("createdAt"),
            "defaultBranchRef": r.get("defaultBranchRef") or {},
            "homepageUrl": r.get("homepageUrl") or "",
            "description": r.get("description") or "",
            "repositoryTopics": r.get("repositoryTopics") or [],
            "hasPages": None,
            "isEmpty": r.get("isEmpty", False),
            "isFork": r.get("isFork", False),
        })
    return repos


def main():
    owner = sys.argv[sys.argv.index("--owner") + 1] if "--owner" in sys.argv else OWNER
    repos = list_repos(owner)
    if not repos:
        print("[!] gh repo list 반환 0 — GH_TOKEN 확인", file=sys.stderr)
    print(f"[*] {owner}: {len(repos)} repos", file=sys.stderr)
    results = []
    for i, r in enumerate(repos, 1):
        try:
            m = parse_repo(r)
        except Exception as e:
            m = {"repo": r["name"], "error": f"{type(e).__name__}: {e}"}
        results.append(m)
        print(f"  [{i:>2}/{len(repos)}] {m['repo']:<24} files={m.get('file_count','-'):>6} "
              f"docs={m.get('doc_count','-'):>5} {m.get('size_human','')}", file=sys.stderr)

    results.sort(key=lambda x: -x.get("file_count", 0))
    out = {
        "generated": "2026-09-23",
        "by": "_Claude",
        "owner": owner,
        "method": "GitHub REST git/trees?recursive=1 (clone 없음)",
        "repo_count": len(results),
        "totals": {
            "files": sum(r.get("file_count", 0) for r in results),
            "docs": sum(r.get("doc_count", 0) for r in results),
            "size_kb": sum(r.get("size_kb", 0) for r in results),
        },
        "repos": results,
    }
    os.makedirs(os.path.join(ROOT, "_notebook", "data"), exist_ok=True)
    dst = os.path.join(ROOT, "_notebook", "data", "repo-index-28.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[+] {dst}")
    print(json.dumps(out["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
