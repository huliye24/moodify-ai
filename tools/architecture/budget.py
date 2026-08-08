"""Complexity budget collector — AST-based, no third-party deps (024 Stage B).

Collects:
- public export symbols per area and their deltas vs previous snapshot
- cross-area import edges, reverse deps, cycles
- core/runtime change concentration (from git diff --numstat)
- oversized modules (top by lines) and high fan-in modules
- compatibility layers (documented exceptions) age

Deterministic for identical input. No composite score — raw indicators only.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIT = r"C:\Program Files\Git\cmd\git.exe"

MANIFEST = Path(__file__).resolve().parent / "enclosure_manifest.json"


def _load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _py_files(area_prefixes: list[str]) -> list[Path]:
    files = []
    for prefix in area_prefixes:
        base = ROOT / prefix
        if base.is_file():
            files.append(base)
        elif base.is_dir():
            files.extend(p for p in base.rglob("*.py") if "__pycache__" not in str(p))
    return files


def _public_symbols(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    symbols = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                symbols.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    symbols.append(target.id)
    return symbols


def _imports(path: Path) -> list[tuple[str, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((str(path), alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((str(path), node.module))
    return imports


def _area_of(path: str, manifest: dict) -> str | None:
    rel = str(path).replace("\\", "/")
    for area in manifest["areas"]:
        for prefix in area["path_prefix"]:
            if rel.endswith(prefix.rstrip("/")) or (prefix in rel):
                return area["area"]
    return None


def collect_budget(previous: dict | None = None) -> dict:
    manifest = _load_manifest()
    areas = {a["area"]: a for a in manifest["areas"]}

    # 1. public symbols per area
    symbols: dict[str, list[str]] = {}
    symbol_deltas: dict[str, int] = {}
    for area_name, area in areas.items():
        area_symbols: list[str] = []
        for path in _py_files(area["path_prefix"]):
            area_symbols.extend(_public_symbols(path))
        symbols[area_name] = sorted(set(area_symbols))
        prev_count = len((previous or {}).get("public_symbols", {}).get(area_name, []))
        symbol_deltas[area_name] = len(symbols[area_name]) - prev_count

    # 2. cross-area import edges (file -> module)
    edges: list[dict] = []
    reverse_deps: dict[str, int] = {a: 0 for a in areas}
    for area_name, area in areas.items():
        for path in _py_files(area["path_prefix"]):
            for _, module in _imports(path):
                target_area = None
                for other_name, other in areas.items():
                    if other_name == area_name:
                        continue
                    for prefix in other["path_prefix"]:
                        mod = prefix.rstrip("/").replace("/", ".").replace("moodify-core-package.src.", "")
                        if module.startswith(mod) or module == mod:
                            target_area = other_name
                            break
                    if target_area:
                        break
                if target_area:
                    edges.append({
                        "from": area_name,
                        "to": target_area,
                        "file": str(path).replace(str(ROOT), "").lstrip("\\/"),
                        "module": module,
                    })
                    reverse_deps[target_area] += 1

    # 3. cycles among areas (simplified: mutual edges)
    edge_pairs = {(e["from"], e["to"]) for e in edges}
    cycles = []
    for a, b in edge_pairs:
        if (b, a) in edge_pairs and a < b:
            cycles.append({"area_a": a, "area_b": b})

    # 4. oversized modules and high fan-in
    module_sizes: list[dict] = []
    for area_name, area in areas.items():
        for path in _py_files(area["path_prefix"]):
            try:
                lines = len(path.read_text(encoding="utf-8").splitlines())
            except (UnicodeDecodeError, OSError):
                continue
            module_sizes.append({
                "module": str(path).replace(str(ROOT), "").lstrip("\\/"),
                "area": area_name,
                "lines": lines,
            })
    oversized = sorted(module_sizes, key=lambda m: -m["lines"])[:10]

    # 5. git change concentration (core/runtime share of tracked changes)
    proc = subprocess.run(
        [GIT, "-C", str(ROOT), "diff", "--numstat", "HEAD"],
        capture_output=True, text=True,
    )
    core_prefixes = ("moodify-core-package/src/", "moodify_runtime/", "workers/")
    total_changes = 0
    core_changes = 0
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            add = int(parts[0]) if parts[0] != "-" else 0
            remove = int(parts[1]) if parts[1] != "-" else 0
        except ValueError:
            continue
        total_changes += add + remove
        if parts[2].startswith(core_prefixes):
            core_changes += add + remove

    return {
        "schema": "moodify.architecture.budget/0.1",
        "public_symbols": symbols,
        "symbol_deltas": symbol_deltas,
        "import_edges": edges,
        "cross_area_edges": len(edges),
        "reverse_deps": reverse_deps,
        "cycles": cycles,
        "oversized_modules": oversized,
        "git": {
            "core_share_pct": round(100 * core_changes / total_changes, 1) if total_changes else 0,
            "total_changes": total_changes,
            "core_changes": core_changes,
        },
        "documented_exceptions": manifest.get("documented_exceptions", []),
    }


def main() -> int:
    target = ROOT / "project_analytics" / "architecture_budget.json"
    budget = collect_budget()
    target.write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"budget: {target}")
    print(f"  cross-area edges: {budget['cross_area_edges']}  cycles: {len(budget['cycles'])}")
    print(f"  reverse deps: {budget['reverse_deps']}")
    print(f"  git core share: {budget['git']['core_share_pct']}%  ({budget['git']['core_changes']}/{budget['git']['total_changes']})")
    print(f"  symbol deltas: {budget['symbol_deltas']}")
    print("  oversized top5: " + ", ".join(m['module'] for m in budget['oversized_modules'][:5]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
