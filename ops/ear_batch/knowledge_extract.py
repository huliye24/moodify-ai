"""Source-grounded extraction for Moodify Ear v1 knowledge task packs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def chapter_sources(source: Path) -> list[tuple[int, Path]]:
    result = [(1, source / "Moodify_Ear_v1_Chapter_01.pdf")]
    for number in range(2, 21):
        result.append((number, source / f"Moodify_Ear_v1_Chapter_{number:02d}_Package" /
                       f"Moodify_Ear_v1_Chapter_{number:02d}" / f"Moodify_Ear_v1_Chapter_{number:02d}.md"))
    return result


def extract_pdf_text(path: Path) -> str:
    import pdfplumber
    pages = []
    with pdfplumber.open(path) as document:
        for number, page in enumerate(document.pages, 1):
            pages.append(f"\n## PDF page {number}\n\n{page.extract_text() or ''}")
    return "\n".join(pages)


def sections(text: str, pdf: bool = False) -> list[tuple[str, str]]:
    if pdf:
        heading = re.compile(r"(?m)^(?:\d+\.?\s+)?([A-Z][^\n]{2,90})$")
    else:
        heading = re.compile(r"(?m)^#{1,4}\s+(.+?)\s*$")
    matches = list(heading.finditer(text))
    result = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            result.append((match.group(1).strip(), body))
    return result or [("Document", text)]


def sentences(body: str) -> Iterable[str]:
    cleaned = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned)
    for value in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", cleaned):
        value = value.strip(" -\t")
        if 45 <= len(value) <= 700 and not value.startswith(("http://", "https://")):
            yield value


def claim_type(sentence: str) -> str:
    lower = sentence.casefold()
    if any(word in lower for word in ("hypothesis", "propose", "could", "should", "would", "must", "needs to")):
        return "proposal_or_requirement"
    if any(word in lower for word in ("is defined as", "means that", "refers to", "is therefore", "is a ")):
        return "definition_or_theory"
    if re.search(r"\b(19|20)\d{2}\b", lower) and any(word in lower for word in ("reported", "showed", "demonstrated", "found")):
        return "reported_external_evidence"
    return "theory_statement"


def extract_claims(source: Path, run_dir: Path) -> None:
    records = []
    chapter_counts: dict[int, int] = {}
    for chapter, path in chapter_sources(source):
        text = extract_pdf_text(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8")
        relative = str(path.relative_to(source)).replace("\\", "/")
        count = 0
        for section, body in sections(text, pdf=path.suffix.lower() == ".pdf"):
            for sentence in sentences(body):
                count += 1
                records.append({"id": f"EAR1-C{chapter:02d}-{count:04d}", "chapter": chapter,
                                "section": section, "source_path": relative, "claim": sentence,
                                "claim_type": claim_type(sentence),
                                "truth_status": "UNVERIFIED_MATERIAL_CLAIM",
                                "extraction_confidence": 0.85 if path.suffix.lower() == ".md" else 0.72})
        chapter_counts[chapter] = count
    output = run_dir / "knowledge" / "claims.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8", newline="\n")
    lines = ["# Moodify Ear v1 Claim Extraction", "",
             "These are source-grounded material claims, not verified product truths. "
             "`extraction_confidence` describes extraction reliability, not factual confidence.", "",
             f"- Total claims: **{len(records)}**", "- Chapters represented: **20/20**", "",
             "| Chapter | Claims | Source format |", "|---:|---:|---|"]
    for chapter in range(1, 21):
        lines.append(f"| {chapter:02d} | {chapter_counts.get(chapter, 0)} | {'PDF' if chapter == 1 else 'Markdown'} |")
    (run_dir / "knowledge" / "claims_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def extract_disciplines(source: Path, run_dir: Path) -> None:
    disciplines = {
        "WSE": {"name": "Wave-Spectral Evolution", "question": "What happened in the sound?", "evidence": []},
        "MSE": {"name": "Musical-Structural Engineering", "question": "What is the musical structure?", "evidence": []},
        "PPE": {"name": "Production Process Engineering", "question": "How is the result produced, verified and recovered reliably?", "evidence": []},
    }
    for chapter, path in chapter_sources(source):
        text = extract_pdf_text(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8")
        relative = str(path.relative_to(source)).replace("\\", "/")
        for heading, body in sections(text, pdf=path.suffix.lower() == ".pdf"):
            compact = re.sub(r"\s+", " ", body)
            for key in disciplines:
                if re.search(rf"\b{key}\b", heading + " " + compact):
                    snippets = [sentence for sentence in sentences(compact) if re.search(rf"\b{key}\b", sentence)]
                    for snippet in snippets[:3]:
                        disciplines[key]["evidence"].append({"chapter": chapter, "section": heading,
                                                            "source_path": relative, "excerpt": snippet})
    write_json(run_dir / "knowledge" / "disciplines.json", {"schema_version": 1, "disciplines": disciplines})
    lines = ["# WSE, MSE, and PPE", "", "The definitions below are indexed to Ear v1 source passages.", ""]
    for key, value in disciplines.items():
        lines.extend([f"## {key} - {value['name']}", "", f"Canonical question: *{value['question']}*", "",
                      f"Indexed source passages: **{len(value['evidence'])}**", ""])
        for evidence in value["evidence"][:8]:
            lines.append(f"- Chapter {evidence['chapter']:02d}, `{evidence['source_path']}`, {evidence['section']}")
        lines.append("")
    (run_dir / "knowledge" / "disciplines.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["TP-101", "TP-102"])
    parser.add_argument("--source", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    run_dir = Path(args.run_dir).resolve()
    {"TP-101": extract_claims, "TP-102": extract_disciplines}[args.task](source, run_dir)


if __name__ == "__main__":
    main()
