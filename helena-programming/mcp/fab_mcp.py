#!/usr/bin/env python3
"""
fab_mcp.py — Content Manufacturing OS MCP Server (IMR = MCP = 주문)

반도체 FAB 미러링 3층(IMR: 정체 + BOM + 런시트)을 MCP 도구로 노출.
레시피 하나 = 주문 하나 = MCP 도구 호출. 읽는 원천: configs/content-fab.json.

Usage:
  python3 fab_mcp.py           # STDIO mode (MCP JSON-RPC 2.0 — Claude Code direct)
  python3 fab_mcp.py --http    # HTTP mode (curl-able, port 8766)

Register:
  claude mcp add content-fab -- python3 /root/work/helena-programming/mcp/fab_mcp.py

Tools:
  fab_list      — Division + Product 목록
  fab_bom       — 제품 BOM (부품 × Division)
  fab_recipe    — 제품 런시트(공정 순서)
  fab_order     — 레시피 실행(주문). run=true 면 실제 실행, 아니면 dry-run
  fab_register  — 새 제품 IMR 등록 (정체 + BOM + 런시트)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path("/root/work")
MANIFEST = ROOT / "configs" / "content-fab.json"


# ─── 마스터 데이터 (IMR) 로드/저장 ────────────────────────────────────────
def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save(m: dict) -> None:
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ─── 도구 ────────────────────────────────────────────────────────────────
def fab_list() -> dict:
    m = load()
    return {
        "divisions": {k: {"label": v["label"], "role": v["role"]} for k, v in m["divisions"].items()},
        "products": {k: {"label": v.get("label", k), "status": v.get("status", "?"), "outputs": v.get("outputs", [])} for k, v in m["products"].items()},
    }


def fab_bom(product: str) -> dict:
    m = load()
    p = m["products"].get(product)
    if not p:
        return {"ok": False, "error": f"없는 product: {product}. 가능: {list(m['products'])}"}
    return {"ok": True, "product": product, "label": p.get("label", product), "bom": p.get("bom", [])}


def fab_recipe(product: str) -> dict:
    m = load()
    p = m["products"].get(product)
    if not p:
        return {"ok": False, "error": f"없는 product: {product}. 가능: {list(m['products'])}"}
    r = p.get("recipe", {})
    return {"ok": True, "product": product, "recipe_id": r.get("id", ""), "steps": sorted(r.get("steps", []), key=lambda x: x["order"])}


def fab_order(product: str, run: bool = False) -> dict:
    """레시피 실행(주문). run=false → dry-run(계획만). run=true → 실제 실행(needs_env 스텝 스킵, 실패 중단)."""
    m = load()
    p = m["products"].get(product)
    if not p:
        return {"ok": False, "error": f"없는 product: {product}. 가능: {list(m['products'])}"}
    r = p.get("recipe", {})
    steps = sorted(r.get("steps", []), key=lambda x: x["order"])
    out = []
    for s in steps:
        if run and s.get("needs_env"):
            out.append({"order": s["order"], "fab": s["fab"], "step": s["step"], "status": "skip_env", "command": s["command"]})
            continue
        if not run:
            out.append({"order": s["order"], "fab": s["fab"], "step": s["step"], "status": "dry_run", "command": s["command"]})
            continue
        rc = subprocess.call(s["command"], shell=True, cwd=ROOT)
        out.append({"order": s["order"], "fab": s["fab"], "step": s["step"], "status": "ok" if rc == 0 else "fail", "exit": rc, "command": s["command"]})
        if rc != 0:
            return {"ok": False, "product": product, "recipe_id": r.get("id", ""), "result": out, "error": f"{s['step']} 실패(exit {rc}) — 중단"}
    return {"ok": True, "product": product, "recipe_id": r.get("id", ""), "mode": "run" if run else "dry_run", "result": out}


def fab_register(product: str, label: str, outputs: list[str], bom: list[dict], steps: list[dict], recipe_id: str = "") -> dict:
    """새 제품 IMR 등록. bom: [{part, division}], steps: [{order, fab, step, command, needs_env?}]."""
    m = load()
    if product in m["products"]:
        return {"ok": False, "error": f"이미 존재하는 product: {product}"}
    m["products"][product] = {
        "label": label,
        "outputs": outputs,
        "status": "registered",
        "bom": bom,
        "recipe": {"id": recipe_id or f"RECIPE-{len(m['products'])+1:03d}", "steps": steps},
    }
    save(m)
    return {"ok": True, "product": product, "label": label, "recipe_id": m["products"][product]["recipe"]["id"]}


# ─── MCP 도구 정의 (tools/list) ──────────────────────────────────────────
TOOLS = [
    {"name": "fab_list", "description": "Content FAB 제품군(Division)과 제품(Product) 목록 조회", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "fab_bom", "description": "제품의 BOM(부품 × Division) 조회", "inputSchema": {"type": "object", "properties": {"product": {"type": "string", "description": "제품 키 (publishing/video/audio/education)"}}, "required": ["product"]}},
    {"name": "fab_recipe", "description": "제품의 런시트(공정 순서) 조회", "inputSchema": {"type": "object", "properties": {"product": {"type": "string"}}, "required": ["product"]}},
    {"name": "fab_order", "description": "레시피 실행(주문). run=true면 실제 실행, 아니면 dry-run", "inputSchema": {"type": "object", "properties": {"product": {"type": "string"}, "run": {"type": "boolean", "default": False}}, "required": ["product"]}},
    {"name": "fab_register", "description": "새 제품 IMR 등록 (정체+BOM+런시트)", "inputSchema": {"type": "object", "properties": {"product": {"type": "string"}, "label": {"type": "string"}, "outputs": {"type": "array", "items": {"type": "string"}}, "bom": {"type": "array"}, "steps": {"type": "array"}, "recipe_id": {"type": "string"}}, "required": ["product", "label"]}},
]


def handle_request(method: str, params: dict | None = None) -> dict:
    """내부 디스패처 — MCP tools/call → 도구 함수."""
    params = params or {}
    try:
        if method == "fab_list":
            return fab_list()
        if method == "fab_bom":
            return fab_bom(params.get("product", ""))
        if method == "fab_recipe":
            return fab_recipe(params.get("product", ""))
        if method == "fab_order":
            return fab_order(params.get("product", ""), run=bool(params.get("run", False)))
        if method == "fab_register":
            return fab_register(
                params.get("product", ""),
                params.get("label", ""),
                params.get("outputs", []),
                params.get("bom", []),
                params.get("steps", []),
                params.get("recipe_id", ""),
            )
        return {"ok": False, "error": f"알 수 없는 method: {method}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


# ─── MCP JSON-RPC 2.0 ────────────────────────────────────────────────────
def _rpc(id_, result=None, error=None):
    r = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        r["error"] = error
    else:
        r["result"] = result
    return r


def handle_jsonrpc(req: dict):
    """MCP JSON-RPC 2.0 요청 처리. notification(id 없음) → None(응답 안 함)."""
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {}) or {}

    if req_id is None:
        return None  # notification (e.g. notifications/initialized)

    if method == "initialize":
        return _rpc(req_id, {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "content-fab", "version": "0.1.0"},
        })
    if method == "ping":
        return _rpc(req_id, {})
    if method == "tools/list":
        return _rpc(req_id, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        result = handle_request(name, args)
        return _rpc(req_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]})
    return _rpc(req_id, error={"code": -32601, "message": f"Method not found: {method}"})


# ─── STDIO 모드 (MCP JSON-RPC 2.0) ──────────────────────────────────────
def run_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_jsonrpc(req)
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)


# ─── HTTP 모드 (curl-able, 커스텀 프로토콜) ─────────────────────────────
def run_http(port: int = 8766) -> None:
    import http.server

    class Handler(http.server.BaseHTTPRequestHandler):
        def _respond(self, code: int, data: dict):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                return self._respond(200, {"ok": True, "service": "content-fab"})
            return self._respond(404, {"ok": False, "error": "POST / 만 지원"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            try:
                req = json.loads(raw)
            except json.JSONDecodeError:
                return self._respond(400, {"ok": False, "error": "bad json"})
            result = handle_request(req.get("method", ""), req.get("params"))
            self._respond(200, result)

        def log_message(self, *a):
            pass

    http.server.HTTPServer(("0.0.0.0", port), Handler).serve_forever()


def main() -> None:
    if "--http" in sys.argv:
        port = 8766
        if "--port" in sys.argv:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        run_http(port)
    else:
        run_stdio()


if __name__ == "__main__":
    main()
