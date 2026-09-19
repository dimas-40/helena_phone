#!/usr/bin/env python3
"""
Content FAB — 개인용 콘텐츠 제조 공장 오케스트레이터 (v0.1 스캐폴드)

반도체 공정을 콘텐츠로 미러링한 3층 관리체계를 코드로:
  Division(제품군) · BOM(부품 명세) · Recipe(공정 = MCP = "주문")

읽는 원천: configs/content-fab.json (단일 진실)

서브커맨드:
  fab.py list                   # Division + Product 목록
  fab.py bom <product>          # 해당 제품의 BOM (부품 × Division)
  fab.py recipe <product>       # 해당 제품의 FAB 공정 시퀀스
  fab.py order <product>        # dry-run: 공정 커맨드 시퀀스 출력
  fab.py order <product> --run  # 실제 실행 (needs_env 스텝은 스킵)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs" / "content-fab.json"


def load() -> dict:
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def _div_label(m: dict, key: str) -> str:
    return m["divisions"].get(key, {}).get("label", key)


def cmd_list(m: dict) -> int:
    print("## Divisions (제품군 — WHAT)")
    for key, v in m["divisions"].items():
        print(f"  {v['label']:<10} {v['role']}")
    print("\n## Products (제품 — 각자 FAB Recipe)")
    for key, v in m["products"].items():
        print(f"  {key:<14} [{v.get('status','?')}]  {v.get('label', key)}  → {', '.join(v.get('outputs', []))}")
    return 0


def _get_product(m: dict, product: str):
    p = m["products"].get(product)
    if not p:
        print(f"❌ 없는 product: {product}. 가능: {list(m['products'])}")
    return p


def cmd_bom(m: dict, product: str) -> int:
    p = _get_product(m, product)
    if not p:
        return 1
    print(f"## BOM — {p.get('label', product)}")
    for b in p.get("bom", []):
        print(f"  {b['part']:<30} → {_div_label(m, b['division'])}")
    return 0


def cmd_recipe(m: dict, product: str) -> int:
    p = _get_product(m, product)
    if not p:
        return 1
    r = p.get("recipe", {})
    print(f"## RECIPE — {r.get('id','')} ({p.get('label', product)})")
    for s in sorted(r.get("steps", []), key=lambda x: x["order"]):
        env = "  [env]" if s.get("needs_env") else ""
        print(f"  {s['order']}. [{s['fab']:<9}] {s['step']}{env}")
        print(f"       {s['command']}")
    return 0


def cmd_order(m: dict, product: str, run: bool = False) -> int:
    p = _get_product(m, product)
    if not p:
        return 1
    r = p.get("recipe", {})
    steps = sorted(r.get("steps", []), key=lambda x: x["order"])
    mode = "▶ RUN" if run else "◀ DRY-RUN (실행은 --run)"
    print(f"## ORDER — {r.get('id','')} ({product})  {mode}")
    for s in steps:
        if run and s.get("needs_env"):
            print(f"  ⏭ skip [env] {s['step']} — {s['command']}")
            continue
        print(f"  {s['order']}. [{s['fab']}] {s['step']}")
        if run:
            rc = subprocess.call(s["command"], shell=True, cwd=ROOT)
            if rc != 0:
                print(f"    ❌ exit {rc} — 중단")
                return rc
    return 0


def main() -> int:
    args = sys.argv[1:]
    m = load()
    if not args or args[0] == "list":
        return cmd_list(m)
    sub = args[0]
    if sub == "bom" and len(args) > 1:
        return cmd_bom(m, args[1])
    if sub == "recipe" and len(args) > 1:
        return cmd_recipe(m, args[1])
    if sub == "order" and len(args) > 1:
        return cmd_order(m, args[1], run=("--run" in args))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
