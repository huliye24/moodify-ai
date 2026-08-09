#!/usr/bin/env python3
"""Moodify temporal-texture static audit.

Standard-library-only scanner intended to create a stable baseline before a
behavior-preserving refactor. It is deliberately conservative: findings are
signals for review, not proof that code is incorrect.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - Python < 3.11
    raise SystemExit("Python 3.11+ is required (tomllib is used).") from exc

DEFAULTS: dict[str, Any] = {
    "scan": {
        "extensions": [".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".rs", ".go"],
        "exclude_dirs": [
            ".git", ".idea", ".vscode", ".venv", "venv", "node_modules",
            "dist", "build", "coverage", ".next", ".turbo", "vendor",
            "artifacts", "generated", "fixtures", "snapshots",
        ],
        "exclude_globs": ["**/*.min.js", "**/*.bundle.js"],
    },
    "thresholds": {
        "max_line_length": 120,
        "function_warning_lines": 60,
        "function_error_lines": 120,
        "complexity_warning": 12,
        "complexity_error": 20,
        "nesting_warning": 4,
        "nesting_error": 6,
        "parameter_warning": 6,
        "parameter_error": 9,
    },
    "policy": {
        "forbid_empty_exception_handlers": True,
        "review_broad_exception_handlers": True,
        "track_debt_markers": True,
        "debt_markers": ["TODO", "FIXME", "HACK", "TEMP", "WORKAROUND"],
        "fail_on_new_errors": True,
        "fail_on_new_warnings": False,
    },
    "weights": {"error": 5, "warning": 2, "info": 1},
}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    column: int
    symbol: str
    message: str
    evidence: dict[str, Any]
    fingerprint: str


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            result[key] = deep_merge(value, override.get(key, {}) if isinstance(override.get(key), dict) else {})
        else:
            result[key] = override.get(key, value)
    for key, value in override.items():
        if key not in result:
            result[key] = value
    return result


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return DEFAULTS
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    return deep_merge(DEFAULTS, raw)


def fingerprint(rule: str, path: str, symbol: str, message_key: str) -> str:
    payload = f"{rule}\0{path}\0{symbol}\0{message_key}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:20]


def make_finding(
    *,
    rule: str,
    severity: str,
    path: str,
    line: int,
    column: int = 0,
    symbol: str = "",
    message: str,
    message_key: str,
    evidence: dict[str, Any] | None = None,
) -> Finding:
    return Finding(
        rule=rule,
        severity=severity,
        path=path,
        line=max(1, line),
        column=max(0, column),
        symbol=symbol,
        message=message,
        evidence=evidence or {},
        fingerprint=fingerprint(rule, path, symbol, message_key),
    )


def should_exclude(relative: Path, config: dict[str, Any]) -> bool:
    exclude_dirs = set(config["scan"]["exclude_dirs"])
    if any(part in exclude_dirs for part in relative.parts[:-1]):
        return True
    posix = relative.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in config["scan"]["exclude_globs"])


def iter_source_files(repo: Path, config: dict[str, Any]) -> Iterable[Path]:
    extensions = {ext.lower() for ext in config["scan"]["extensions"]}
    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        relative_root = root_path.relative_to(repo)
        exclude_dirs = set(config["scan"]["exclude_dirs"])
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            path = root_path / name
            relative = relative_root / name
            if path.suffix.lower() not in extensions:
                continue
            if should_exclude(relative, config):
                continue
            yield path


class PythonFunctionVisitor(ast.NodeVisitor):
    BRANCH_NODES = (
        ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith,
        ast.BoolOp, ast.IfExp, ast.Match, ast.comprehension,
    )
    NESTING_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)

    def __init__(self) -> None:
        self.complexity = 1
        self.max_nesting = 0
        self._nesting = 0
        self.broad_handlers: list[ast.ExceptHandler] = []
        self.empty_handlers: list[ast.ExceptHandler] = []

    def generic_visit(self, node: ast.AST) -> None:
        is_branch = isinstance(node, self.BRANCH_NODES)
        is_nesting = isinstance(node, self.NESTING_NODES)
        if is_branch:
            if isinstance(node, ast.BoolOp):
                self.complexity += max(1, len(node.values) - 1)
            elif isinstance(node, ast.Try):
                self.complexity += max(1, len(node.handlers))
            elif isinstance(node, ast.Match):
                self.complexity += max(1, len(node.cases))
            else:
                self.complexity += 1
        if is_nesting:
            self._nesting += 1
            self.max_nesting = max(self.max_nesting, self._nesting)
        super().generic_visit(node)
        if is_nesting:
            self._nesting -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        broad = node.type is None or (
            isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
        )
        if broad:
            self.broad_handlers.append(node)
        if not node.body or all(isinstance(item, (ast.Pass, ast.Expr)) and (
            isinstance(item, ast.Pass)
            or (isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant) and item.value.value in {None, ""})
        ) for item in node.body):
            self.empty_handlers.append(node)
        self.generic_visit(node)


def function_args_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    args = node.args
    return len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs)


def severity_for(value: int, warning: int, error: int) -> str | None:
    if value > error:
        return "error"
    if value > warning:
        return "warning"
    return None


def scan_python(path: Path, relative: str, text: str, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        findings.append(make_finding(
            rule="PY-SYNTAX",
            severity="error",
            path=relative,
            line=exc.lineno or 1,
            column=exc.offset or 0,
            message=f"Python syntax could not be parsed: {exc.msg}",
            message_key="syntax-error",
            evidence={"text": exc.text.strip() if exc.text else ""},
        ))
        return findings

    thresholds = config["thresholds"]
    policy = config["policy"]

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end_line = getattr(node, "end_lineno", node.lineno)
        lines = max(1, end_line - node.lineno + 1)
        visitor = PythonFunctionVisitor()
        for statement in node.body:
            visitor.visit(statement)
        symbol = node.name

        sev = severity_for(lines, thresholds["function_warning_lines"], thresholds["function_error_lines"])
        if sev:
            findings.append(make_finding(
                rule="TT-FUNCTION-LENGTH",
                severity=sev,
                path=relative,
                line=node.lineno,
                column=node.col_offset,
                symbol=symbol,
                message=f"Function spans {lines} lines; review responsibility boundaries.",
                message_key="function-length",
                evidence={"lines": lines},
            ))

        sev = severity_for(visitor.complexity, thresholds["complexity_warning"], thresholds["complexity_error"])
        if sev:
            findings.append(make_finding(
                rule="TT-COMPLEXITY",
                severity=sev,
                path=relative,
                line=node.lineno,
                column=node.col_offset,
                symbol=symbol,
                message=f"Function complexity proxy is {visitor.complexity}; branch pressure may hide decisions.",
                message_key="complexity",
                evidence={"complexity": visitor.complexity},
            ))

        sev = severity_for(visitor.max_nesting, thresholds["nesting_warning"], thresholds["nesting_error"])
        if sev:
            findings.append(make_finding(
                rule="TT-NESTING",
                severity=sev,
                path=relative,
                line=node.lineno,
                column=node.col_offset,
                symbol=symbol,
                message=f"Maximum nesting depth is {visitor.max_nesting}; failure and decision paths are compressed.",
                message_key="nesting",
                evidence={"nesting": visitor.max_nesting},
            ))

        arg_count = function_args_count(node)
        sev = severity_for(arg_count, thresholds["parameter_warning"], thresholds["parameter_error"])
        if sev:
            findings.append(make_finding(
                rule="TT-PARAMETERS",
                severity=sev,
                path=relative,
                line=node.lineno,
                column=node.col_offset,
                symbol=symbol,
                message=f"Function has {arg_count} declared parameters; implicit context may need a named structure.",
                message_key="parameters",
                evidence={"parameters": arg_count},
            ))

        if policy["review_broad_exception_handlers"]:
            for handler in visitor.broad_handlers:
                findings.append(make_finding(
                    rule="TT-BROAD-EXCEPTION",
                    severity="warning",
                    path=relative,
                    line=handler.lineno,
                    column=handler.col_offset,
                    symbol=symbol,
                    message="Broad exception handler requires contextual logging, rethrowing, or a documented boundary.",
                    message_key=f"broad-exception:{handler.lineno}",
                ))

        if policy["forbid_empty_exception_handlers"]:
            for handler in visitor.empty_handlers:
                findings.append(make_finding(
                    rule="TT-EMPTY-EXCEPTION",
                    severity="error",
                    path=relative,
                    line=handler.lineno,
                    column=handler.col_offset,
                    symbol=symbol,
                    message="Empty exception handler hides failure evidence.",
                    message_key=f"empty-exception:{handler.lineno}",
                ))

    return findings


def scan_textual(path: Path, relative: str, text: str, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    threshold = config["thresholds"]["max_line_length"]
    policy = config["policy"]
    markers = [marker.upper() for marker in policy["debt_markers"]]

    for number, line in enumerate(text.splitlines(), start=1):
        if len(line) > threshold:
            findings.append(make_finding(
                rule="TT-LINE-LENGTH",
                severity="warning",
                path=relative,
                line=number,
                message=f"Line length is {len(line)} characters; expression may be compressed.",
                message_key=f"line-length:{number}",
                evidence={"length": len(line)},
            ))
        if policy["track_debt_markers"]:
            upper = line.upper()
            for marker in markers:
                if marker in upper:
                    findings.append(make_finding(
                        rule="TT-DEBT-MARKER",
                        severity="info",
                        path=relative,
                        line=number,
                        message=f"Debt marker {marker} requires a reason and exit condition.",
                        message_key=f"debt:{marker}:{number}",
                        evidence={"marker": marker, "excerpt": line.strip()[:240]},
                    ))
                    break

        stripped = line.strip()
        if path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            if stripped.startswith("catch") or ") catch" in stripped or "catch (" in stripped:
                # A line-level hint. Detailed JS parsing is intentionally out of scope for a stdlib-only tool.
                if "{}" in stripped or stripped.endswith("{ }"):
                    findings.append(make_finding(
                        rule="TT-EMPTY-CATCH",
                        severity="error",
                        path=relative,
                        line=number,
                        message="Empty catch block hides failure evidence.",
                        message_key=f"empty-catch:{number}",
                    ))
    return findings


def scan_file(repo: Path, path: Path, config: dict[str, Any]) -> tuple[list[Finding], str | None]:
    relative = path.relative_to(repo).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as exc:
            return [], f"Skipped non-UTF source: {relative}: {exc}"
    except OSError as exc:
        return [], f"Could not read {relative}: {exc}"

    findings = scan_textual(path, relative, text, config)
    if path.suffix.lower() == ".py":
        findings.extend(scan_python(path, relative, text, config))
    return findings, None


def summarize(findings: list[Finding], files_scanned: int, skipped: list[str], config: dict[str, Any]) -> dict[str, Any]:
    counts = {"error": 0, "warning": 0, "info": 0}
    by_rule: dict[str, int] = {}
    by_path: dict[str, int] = {}
    score = 0
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1
        by_rule[item.rule] = by_rule.get(item.rule, 0) + 1
        by_path[item.path] = by_path.get(item.path, 0) + 1
        score += int(config["weights"].get(item.severity, 1))
    return {
        "files_scanned": files_scanned,
        "findings": len(findings),
        "counts": counts,
        "weighted_pressure_score": score,
        "by_rule": dict(sorted(by_rule.items(), key=lambda pair: (-pair[1], pair[0]))),
        "top_paths": sorted(
            ({"path": path, "findings": count} for path, count in by_path.items()),
            key=lambda item: (-item["findings"], item["path"]),
        )[:25],
        "skipped": skipped,
    }


def report_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    counts = summary["counts"]
    lines = [
        "# Moodify Temporal Texture Audit",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Repository: `{report['repository']}`",
        f"- Files scanned: **{summary['files_scanned']}**",
        f"- Findings: **{summary['findings']}**",
        f"- Errors: **{counts.get('error', 0)}**",
        f"- Warnings: **{counts.get('warning', 0)}**",
        f"- Information: **{counts.get('info', 0)}**",
        f"- Weighted pressure score: **{summary['weighted_pressure_score']}**",
        "",
        "> Findings are review signals. Business risk and behavioral authority must determine refactor priority.",
        "",
        "## Top paths",
        "",
        "| Path | Findings |",
        "|---|---:|",
    ]
    for item in summary["top_paths"]:
        lines.append(f"| `{item['path']}` | {item['findings']} |")
    lines.extend(["", "## Findings", "", "| Severity | Rule | Location | Symbol | Message |", "|---|---|---|---|---|"])
    order = {"error": 0, "warning": 1, "info": 2}
    for item in sorted(report["findings"], key=lambda f: (order.get(f["severity"], 9), f["path"], f["line"], f["rule"])):
        message = item["message"].replace("|", "\\|")
        symbol = item["symbol"].replace("|", "\\|") if item["symbol"] else ""
        lines.append(
            f"| {item['severity'].upper()} | `{item['rule']}` | `{item['path']}:{item['line']}` | `{symbol}` | {message} |"
        )
    if summary["skipped"]:
        lines.extend(["", "## Skipped", ""])
        lines.extend(f"- {entry}" for entry in summary["skipped"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--config", type=Path, help="TOML configuration")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--fail-on",
        choices=["none", "error", "warning"],
        default="none",
        help="Return non-zero when findings reach the selected severity",
    )
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not repo.is_dir():
        parser.error(f"Repository is not a directory: {repo}")
    config_path = args.config.resolve() if args.config else None
    try:
        config = load_config(config_path)
    except (OSError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    skipped: list[str] = []
    files = list(iter_source_files(repo, config))
    for path in files:
        items, skip_reason = scan_file(repo, path, config)
        findings.extend(items)
        if skip_reason:
            skipped.append(skip_reason)

    findings = sorted(findings, key=lambda item: (item.path, item.line, item.column, item.rule))
    summary = summarize(findings, len(files), skipped, config)
    report = {
        "schema_version": "1.0",
        "tool": "moodify-temporal-texture-audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": str(repo),
        "config": str(config_path) if config_path else "built-in defaults",
        "summary": summary,
        "findings": [asdict(item) for item in findings],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out / "report.md").write_text(report_markdown(report), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False))
    errors = summary["counts"].get("error", 0)
    warnings = summary["counts"].get("warning", 0)
    if args.fail_on == "error" and errors:
        return 1
    if args.fail_on == "warning" and (errors or warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
