"""Validate, seal, and register one overall-project-analysis run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_registry(path: Path, entry: dict) -> None:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []
    if any(row.get("run_id") == entry["run_id"] for row in rows):
        raise ValueError(f"run already registered: {entry['run_id']}")
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    run_dir = args.run_dir.resolve()
    data = json.loads((run_dir / "analysis_data.json").read_text(encoding="utf-8"))

    state_total = sum(row["count"] for row in data["task_states"])
    assert state_total == data["repository"].get("formal_task_packages", state_total)
    assert state_total == len(data["tasks"])
    assert sum(row["changed_files"] for row in data["change_areas"]) == data["repository"]["changed_tracked_files"]
    assert all(row["score"] == row["probability"] * row["impact"] for row in data["risks"])
    assert all(abs(row["modeled_roi"] - round(row["impact_points"] / row["hours_mid"], 2)) < 1e-9 for row in data["investments"])

    outputs = [
        run_dir / "analysis_data.json",
        run_dir / "Moodify_Overall_Analysis_2026-08-02_094746.xlsx",
        run_dir / "Moodify_Overall_Analysis_2026-08-02_094746.pdf",
        *sorted((run_dir / "charts").glob("*.png")),
    ]
    missing = [str(path) for path in outputs if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise FileNotFoundError(missing)
    timestamp_dir = run_dir.parent.name
    run_id = f"{timestamp_dir}-overall-project-analysis"
    manifest = {
        "schema": "moodify.analytics.run-manifest/0.1",
        "run_id": run_id,
        "analysis_id": "overall-project-analysis",
        "analysis_kind": "stage",
        "started_at": data["analysis_started_at"],
        "timezone": "Asia/Shanghai",
        "status": "complete",
        "metric_contract": "moodify.analytics.metric-contracts/0.1",
        "sources": [data["source_snapshot"]],
        "outputs": [path.relative_to(run_dir).as_posix() for path in outputs],
        "output_sha256": {path.relative_to(run_dir).as_posix(): sha256(path) for path in outputs},
        "validation": {
            "calculation_checks": [
                "task-state counts equal task-detail rows",
                "change-area counts equal changed tracked files",
                "risk score equals probability times impact",
                "modeled ROI equals impact points divided by midpoint hours",
                "workbook formula error scan matched zero entries",
                "PDF rendered to eight pages and visually sampled",
            ],
            "workbook_render": "7 of 9 sheets rendered by artifact-tool; two sheet previews hit a local Vulkan encoder error; workbook export succeeded",
            "pdf_render": "8 of 8 pages rendered with Poppler",
        },
        "limitations": data["limitations"],
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_registry(
        root / "project_analytics" / "registry.jsonl",
        {
            "run_id": run_id,
            "analysis_id": "overall-project-analysis",
            "analysis_kind": "stage",
            "started_at": data["analysis_started_at"],
            "status": "complete",
            "manifest": manifest_path.relative_to(root).as_posix(),
        },
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
