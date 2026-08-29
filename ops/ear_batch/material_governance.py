"""Deterministic material-governance processors for Ear v1 task packs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def authoritative_chapters(source: Path) -> list[dict[str, Any]]:
    chapters = []
    for number in range(2, 21):
        outer = source / f"Moodify_Ear_v1_Chapter_{number:02d}_Package"
        inner = outer / f"Moodify_Ear_v1_Chapter_{number:02d}"
        chapters.append({"number": number, "outer": outer, "inner": inner,
                         "zip": source / f"Moodify_Ear_v1_Chapter_{number:02d}_Package.zip"})
    return chapters


def package_consistency(source: Path, run_dir: Path) -> None:
    results = []
    issue_count = 0
    for chapter in authoritative_chapters(source):
        inner: Path = chapter["inner"]
        manifest_path = inner / "manifest.json"
        issues = []
        manifest: dict[str, Any] = {}
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"manifest unreadable: {exc}")
        expected = set(manifest.get("files", [])) | {"manifest.json"}
        actual = {path.name for path in inner.iterdir() if path.is_file()} if inner.is_dir() else set()
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            issues.append(f"missing files: {missing}")
        if extra:
            issues.append(f"unlisted files: {extra}")
        if manifest.get("chapter") != chapter["number"]:
            issues.append(f"manifest chapter is {manifest.get('chapter')!r}")
        zip_members: list[str] = []
        if chapter["zip"].is_file():
            try:
                with zipfile.ZipFile(chapter["zip"]) as archive:
                    zip_members = [name.replace("\\", "/") for name in archive.namelist() if not name.endswith("/")]
                zip_basenames = {Path(name).name for name in zip_members}
                if zip_basenames != actual:
                    issues.append(f"ZIP membership differs: zip={sorted(zip_basenames)}, extracted={sorted(actual)}")
            except zipfile.BadZipFile:
                issues.append("invalid ZIP archive")
        else:
            issues.append("package ZIP missing")
        issue_count += len(issues)
        results.append({"chapter": chapter["number"], "manifest": str(manifest_path),
                        "expected_files": sorted(expected), "actual_files": sorted(actual),
                        "zip_file_count": len(zip_members), "issues": issues, "passed": not issues})
    report = {"schema_version": 1, "scope": "authoritative v1 package trees, chapters 02-20",
              "chapter_01_note": "Only standalone PDF material was supplied; no Chapter 01 package exists.",
              "chapters_checked": len(results), "issue_count": issue_count, "results": results}
    write_json(run_dir / "quality" / "package_consistency.json", report)
    lines = ["# Package Consistency", "", "Checked authoritative extracted packages and ZIP membership for Chapters 02–20.",
             "Chapter 01 is a standalone PDF in the supplied corpus and has no package manifest.", "",
             f"- Chapters checked: **{len(results)}**", f"- Issues: **{issue_count}**", "",
             "| Chapter | Result | Issues |", "|---:|---|---|"]
    for item in results:
        issues = "; ".join(item["issues"]) or "None"
        lines.append(f"| {item['chapter']:02d} | {'PASS' if item['passed'] else 'REVIEW'} | {issues} |")
    (run_dir / "quality" / "package_consistency.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def text_integrity(source: Path, run_dir: Path) -> None:
    authority = authoritative_chapters(source)
    paths: list[Path] = []
    for chapter in authority:
        paths.extend(sorted(chapter["inner"].glob("*.md")))
        paths.append(chapter["inner"] / "manifest.json")
    findings: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    suspicious_sequences = ("�", "Ã", "Â", "â€", "鈥", "枚", "眉")
    cjk = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
    for path in paths:
        relative = str(path.relative_to(source)).replace("\\", "/")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            findings.append({"severity": "error", "path": relative, "line": None,
                             "kind": "utf8_decode", "detail": str(exc)})
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            markers = sorted({marker for marker in suspicious_sequences if marker in line})
            cjk_chars = sorted(set(cjk.findall(line)))
            if markers or cjk_chars:
                findings.append({"severity": "warning", "path": relative, "line": line_number,
                                 "kind": "suspected_mojibake", "markers": markers,
                                 "cjk_characters": cjk_chars, "excerpt": line[:240]})
        if path.name.startswith("Moodify_Ear_v1_Chapter_") and path.suffix == ".md":
            refs_path = path.with_name("references.md")
            used = {int(value) for value in re.findall(r"\[(\d+)\]", text)}
            available = set()
            if refs_path.is_file():
                refs_text = refs_path.read_text(encoding="utf-8")
                available = {int(value) for value in re.findall(r"^\[(\d+)\]", refs_text, re.MULTILINE)}
            missing = sorted(used - available)
            unused = sorted(available - used)
            citations.append({"chapter_file": relative, "used": sorted(used), "available": sorted(available),
                              "missing": missing, "unused": unused})
            for number in missing:
                findings.append({"severity": "error", "path": relative, "line": None,
                                 "kind": "missing_reference", "detail": f"citation [{number}] has no reference entry"})
    counts = Counter(item["severity"] for item in findings)
    result = {"schema_version": 1, "policy": "report only; source text was not rewritten",
              "files_checked": len(paths), "finding_counts": dict(counts),
              "findings": findings, "citation_checks": citations}
    write_json(run_dir / "quality" / "text_integrity.json", result)
    lines = ["# Text and Reference Integrity", "", "The scan is evidence-only; no source text was rewritten.", "",
             f"- Files checked: **{len(paths)}**", f"- Errors: **{counts['error']}**",
             f"- Warnings: **{counts['warning']}**", "", "## Findings", ""]
    if findings:
        for item in findings:
            location = item["path"] + (f":{item['line']}" if item.get("line") else "")
            detail = item.get("detail") or item.get("excerpt") or item["kind"]
            lines.append(f"- **{item['severity'].upper()}** `{location}` — {item['kind']}: {detail}")
    else:
        lines.append("No encoding or citation-integrity findings.")
    (run_dir / "quality" / "text_integrity.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def normalized_manifest(source: Path, run_dir: Path) -> None:
    snapshot = json.loads((run_dir / "SOURCE_SNAPSHOT.json").read_text(encoding="utf-8"))
    hashes = {item["path"]: item for item in snapshot["files"]}
    chapters = []
    for chapter in authoritative_chapters(source):
        inner: Path = chapter["inner"]
        manifest = json.loads((inner / "manifest.json").read_text(encoding="utf-8"))
        files = []
        for path in sorted(inner.iterdir()):
            if not path.is_file():
                continue
            relative = str(path.relative_to(source)).replace("\\", "/")
            item = hashes[relative]
            files.append({"role": "manifest" if path.name == "manifest.json" else path.suffix.lstrip("."),
                          "path": relative, "bytes": item["bytes"], "sha256": item["sha256"]})
        chapters.append({"chapter": chapter["number"], "title": manifest.get("chapter_title"), "files": files})
    chapter_one = source / "Moodify_Ear_v1_Chapter_01.pdf"
    one_rel = str(chapter_one.relative_to(source)).replace("\\", "/")
    chapters.insert(0, {"chapter": 1, "title": None, "package_status": "standalone_pdf_only",
                        "files": [{"role": "pdf", "path": one_rel, "bytes": hashes[one_rel]["bytes"],
                                   "sha256": hashes[one_rel]["sha256"]}]})
    output = {"schema_version": 1, "corpus": "Moodify Ear v1", "source": str(source),
              "source_policy": "read-only", "v2_excluded": True,
              "authority": "package extracted trees for chapters 02-20; standalone PDF for chapter 01",
              "chapters": chapters}
    write_json(run_dir / "corpus" / "normalized_manifest.json", output)
    (run_dir / "corpus" / "README.md").write_text(
        "# Normalized Moodify Ear v1 Corpus\n\n"
        "This directory indexes immutable source material; it does not duplicate or rewrite it. "
        "`normalized_manifest.json` binds each authoritative file to its size and SHA-256 digest. "
        "Chapter 01 is represented by the supplied standalone PDF. Chapters 02–20 use extracted "
        "package trees. Moodify Ear v2 and duplicate top-level Chapter 02–04 trees are excluded.\n",
        encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["TP-004", "TP-005", "TP-006"])
    parser.add_argument("--source", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    run_dir = Path(args.run_dir).resolve()
    {"TP-004": package_consistency, "TP-005": text_integrity,
     "TP-006": normalized_manifest}[args.task](source, run_dir)


if __name__ == "__main__":
    main()
