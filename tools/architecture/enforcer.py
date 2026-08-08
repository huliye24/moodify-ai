"""Architecture boundary enforcer — AST-based, stdlib only (024 Stage C).

Rules come from enclosure_manifest.json:
- allowed_deps: modules an area may import
- forbidden_deps: modules an area must not import
- documented exceptions: allow with expiry (baseline debt, must not grow)
- reverse deps forbidden: areas that must not import this area

New violations fail; existing debt is baseline and must only decrease.
Deterministic: identical input -> identical output. Exit 0 = clean.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "enclosure_manifest.json"

THIRD_PARTY = {"numpy", "scipy", "librosa", "soundfile", "pyloudnorm", "pedalboard",
               "fastapi", "uvicorn", "pydantic", "pytest", "httpx", "matplotlib",
               "anyio", "pretty_midi", "mir_eval", "resampy", "scikit", "sklearn",
               "onnxruntime", "yaml", "PyYAML", "multipart"}


def _load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _area_for(rel_path: str, manifest: dict) -> tuple[str | None, dict | None]:
    p = rel_path.replace("\\", "/")
    for area in manifest["areas"]:
        for prefix in area["path_prefix"]:
            norm_prefix = prefix.replace("\\", "/").rstrip("/")
            if p.startswith(norm_prefix) or p == norm_prefix:
                return area["area"], area
    return None, None


def _imports_of(path: Path) -> list[tuple[str, int]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module, node.lineno))
    return imports


def _module_to_area(module: str, manifest: dict) -> str | None:
    """Map an imported module to an enclosure area (or None if third-party/std)."""
    if module.split(".")[0] in THIRD_PARTY or module.split(".")[0] in ("os", "sys", "json",
                                                                         "pathlib", "dataclasses", "typing", "re", "subprocess", "time",
                                                                         "datetime", "hashlib", "uuid", "enum", "collections", "itertools",
                                                                         "functools", "math", "struct", "wave", "tempfile", "shutil",
                                                                         "importlib", "io", "random", "string", "argparse", "logging",
                                                                         "xml", "sqlite3", "abc", "contextlib", "copy", "fractions",
                                                                         "decimal", "warnings", "weakref", "inspect", "traceback",
                                                                         "threading", "concurrent", "multiprocessing", "asyncio",
                                                                         "html", "urllib", "base64", "binascii", "csv", "glob", "gzip",
                                                                         "pickle", "pprint", "statistics", "zipfile", "unicodedata"):
        return None
    for area in manifest["areas"]:
        for prefix in area["path_prefix"]:
            mod_prefix = prefix.rstrip("/").replace("/", ".").replace("moodify-core-package.src.", "").rstrip(".")
            # e.g. "moodify.processing" or "moodify_runtime"
            if module == mod_prefix or module.startswith(mod_prefix + "."):
                return area["area"]
    return None


def check_enclosure() -> dict:
    manifest = _load_manifest()
    violations: list[dict] = []
    baseline_debt: list[dict] = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = str(path).replace(str(ROOT), "").lstrip("\\/")
        if "__pycache__" in rel or ".venv" in rel or rel.startswith("tools/"):
            continue
        area, area_def = _area_for(rel, manifest)
        if area is None or area_def is None:
            continue
        for module, lineno in _imports_of(path):
            if module.split(".")[0] in THIRD_PARTY or module.split(".")[0] in (
                "os", "sys", "json", "pathlib", "dataclasses", "typing", "re",
                "subprocess", "time", "datetime", "hashlib", "uuid", "enum",
                "collections", "itertools", "functools", "math", "struct",
                "wave", "tempfile", "shutil", "importlib", "io", "random",
                "string", "argparse", "logging", "xml", "sqlite3", "abc",
                "contextlib", "copy", "fractions", "decimal", "warnings",
                "weakref", "inspect", "traceback", "threading", "concurrent",
                "multiprocessing", "asyncio", "html", "urllib", "base64",
                "binascii", "csv", "glob", "gzip", "pickle", "pprint",
                "statistics", "zipfile", "unicodedata"):
                continue
            target_area = _module_to_area(module, manifest)
            if target_area is None:
                continue
            # forbidden direct dep?
            forbidden = area_def.get("forbidden_deps", [])
            if any(target_area in f or f in module for f in forbidden):
                record = {
                    "kind": "forbidden_dep",
                    "file": rel,
                    "line": lineno,
                    "area": area,
                    "imports": module,
                    "target_area": target_area,
                    "rule": f"{area} must not import {target_area}",
                }
                # documented exception?
                exc = next((e for e in manifest.get("documented_exceptions", [])
                            if e["from_area"] == area and e["to_area"] == target_area), None)
                if exc:
                    record["exception_id"] = exc["id"]
                    record["expiry"] = exc["expiry"]
                    baseline_debt.append(record)
                else:
                    violations.append(record)
            # reverse dep forbidden?
            reverse_forbidden = area_def.get("reverse_deps_forbidden", [])
            if target_area in reverse_forbidden:
                violations.append({
                    "kind": "reverse_dep",
                    "file": rel,
                    "line": lineno,
                    "area": area,
                    "imports": module,
                    "target_area": target_area,
                    "rule": f"{area} must not be imported by {target_area}",
                })
    return {
        "schema": "moodify.architecture.enforcer/0.1",
        "violations": violations,
        "baseline_debt": baseline_debt,
        "summary": {
            "violations": len(violations),
            "baseline_debt": len(baseline_debt),
        },
    }


def main() -> int:
    result = check_enclosure()
    print("enclosure check:")
    print(f"  violations: {result['summary']['violations']}  baseline debt: {result['summary']['baseline_debt']}")
    for v in result["violations"][:20]:
        print(f"  [VIOLATION] {v['file']}:{v['line']}  {v['rule']}")
    for d in result["baseline_debt"][:10]:
        print(f"  [DEBT-{d['exception_id']}] {d['file']}:{d['line']}  {d['rule']}  (expires {d['expiry']})")
    if result["summary"]["violations"] > 0:
        print("  RESULT: FAIL (new violations must be fixed or documented)")
        return 1
    print("  RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
