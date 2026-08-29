"""Current-capability inventory generator (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Scans the moodify package and classifies each module into the auditory
intelligence bounded contexts. Uncertain classifications are marked
explicitly — nothing is guessed silently.
"""

from __future__ import annotations

import json
from pathlib import Path

# Explicit classification map. `confidence` marks certainty;
# "low" entries are explicitly uncertain and must not be silently trusted.
CLASSIFICATION: dict[str, dict] = {
    # ---- OBSERVATION (what happened in the sound) ----
    "v01_analyzer": {"category": "OBSERVATION", "confidence": "high"},
    "features": {"category": "OBSERVATION", "confidence": "high"},
    "perception": {"category": "OBSERVATION", "confidence": "high"},
    "auditory.metrics": {"category": "OBSERVATION", "confidence": "high"},
    "auditory.decode": {"category": "OBSERVATION", "confidence": "high"},
    "auditory.spectrogram": {"category": "OBSERVATION", "confidence": "high"},
    "auditory.timeline": {"category": "OBSERVATION", "confidence": "high"},
    "auditory.stereo": {"category": "OBSERVATION", "confidence": "high"},

    # ---- REPRESENTATION (how the machine describes what it heard) ----
    "auditory.models": {"category": "REPRESENTATION", "confidence": "high"},
    "auditory.profiles": {"category": "REPRESENTATION", "confidence": "high"},
    "domain": {"category": "REPRESENTATION", "confidence": "medium"},
    "data_types": {"category": "REPRESENTATION", "confidence": "medium"},

    # ---- JUDGMENT (defect / risk / intentional / ambiguity) ----
    "auditory.judgment": {"category": "JUDGMENT", "confidence": "high"},
    "auditory.comparison": {"category": "JUDGMENT", "confidence": "high"},
    "diagnosis": {"category": "JUDGMENT", "confidence": "high"},
    "evaluation": {"category": "JUDGMENT", "confidence": "medium"},
    "uncertainty": {"category": "JUDGMENT", "confidence": "medium"},
    "reality_metrics": {"category": "JUDGMENT", "confidence": "medium"},
    "mrs_adapter": {"category": "JUDGMENT", "confidence": "medium"},
    "mrs_robust": {"category": "JUDGMENT", "confidence": "medium"},
    "v01_diagnostics": {"category": "JUDGMENT", "confidence": "high"},

    # ---- INTERVENTION (controlled change applied to test/improve) ----
    "processing": {"category": "INTERVENTION", "confidence": "high"},
    "v01_pipeline": {"category": "INTERVENTION", "confidence": "high"},
    "v01_presets": {"category": "INTERVENTION", "confidence": "high"},
    "v01_exporter": {"category": "INTERVENTION", "confidence": "high"},
    "v01_types": {"category": "INTERVENTION", "confidence": "medium"},
    "craft_slider": {"category": "INTERVENTION", "confidence": "medium"},
    "calibration": {"category": "INTERVENTION", "confidence": "medium"},
    "optimizer": {"category": "INTERVENTION", "confidence": "medium"},
    "physics": {"category": "INTERVENTION", "confidence": "medium"},
    "conservation": {"category": "INTERVENTION", "confidence": "medium"},
    "transcription": {"category": "INTERVENTION", "confidence": "medium"},
    "transcription_pipeline": {"category": "INTERVENTION", "confidence": "medium"},
    "score_engine": {"category": "INTERVENTION", "confidence": "medium"},
    "orchestration": {"category": "INTERVENTION", "confidence": "medium"},
    "adapters": {"category": "INTERVENTION", "confidence": "medium"},
    "services": {"category": "INTERVENTION", "confidence": "medium"},

    # ---- VERIFICATION (what changed and did it satisfy the goal) ----
    "auditory.service": {"category": "VERIFICATION", "confidence": "high"},
    "auditory.manifests": {"category": "VERIFICATION", "confidence": "high"},
    "auditory.reports": {"category": "VERIFICATION", "confidence": "high"},
    "auditory.errors": {"category": "VERIFICATION", "confidence": "high"},
    "v01_delivery": {"category": "VERIFICATION", "confidence": "medium"},

    # ---- LEARNING (what can the system learn from this case) ----
    "learning": {"category": "LEARNING", "confidence": "high"},

    # ---- SHARED_INFRASTRUCTURE ----
    "auditory": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "app": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "storage": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "ports": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "capability_registry": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "api": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "safety": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "protocol": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "config": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "cli": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "cli_v2": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "cli_daw": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "audio_io": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "bands": {"category": "SHARED_INFRASTRUCTURE", "confidence": "high"},
    "fingerprint": {"category": "SHARED_INFRASTRUCTURE", "confidence": "medium"},

    # ---- LEGACY_UNKNOWN (explicitly uncertain) ----
    "knowledge": {"category": "LEGACY_UNKNOWN", "confidence": "low"},
    "memory": {"category": "LEGACY_UNKNOWN", "confidence": "low"},
    "llm": {"category": "LEGACY_UNKNOWN", "confidence": "low"},
    "icc": {"category": "LEGACY_UNKNOWN", "confidence": "low"},
    "system_depth": {"category": "LEGACY_UNKNOWN", "confidence": "low"},
}

CATEGORY_LABEL = {
    "OBSERVATION": "OBSERVATION",
    "REPRESENTATION": "REPRESENTATION",
    "JUDGMENT": "JUDGMENT",
    "INTERVENTION": "INTERVENTION",
    "VERIFICATION": "VERIFICATION",
    "LEARNING": "LEARNING",
    "SHARED_INFRASTRUCTURE": "SHARED_INFRASTRUCTURE",
    "LEGACY_UNKNOWN": "LEGACY_UNKNOWN",
}


def scan_package(package_dir: Path) -> list[dict]:
    """List top-level modules and classify each; unknown ones are flagged."""
    entries = []
    for child in sorted(package_dir.iterdir()):
        if child.name.startswith("__") or child.name.startswith("."):
            continue
        is_pkg = child.is_dir() and (child / "__init__.py").is_file()
        is_mod = child.is_file() and child.suffix == ".py"
        if not (is_pkg or is_mod):
            continue
        name = child.name[:-3] if is_mod else child.name
        cls = CLASSIFICATION.get(name) or CLASSIFICATION.get(f"auditory.{name}")
        if cls is None:
            cls = {"category": "LEGACY_UNKNOWN", "confidence": "low"}
        entries.append({
            "name": name,
            "kind": "package" if is_pkg else "module",
            "category": cls["category"],
            "confidence": cls["confidence"],
            "path": f"moodify/{name}",
        })
    return entries


def build_inventory(package_dir: Path) -> dict:
    entries = scan_package(package_dir)
    counts: dict[str, int] = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "counts": counts,
        "capabilities": entries,
    }


def render_markdown(inventory: dict) -> str:
    lines = [
        "# Moodify 当前能力清点（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）",
        "",
        "机器可读版本：`current_capability_inventory.json`",
        "",
        "## 分类计数",
        "",
        "| 分类 | 数量 |",
        "|---|---:|",
    ]
    for cat in CATEGORY_LABEL:
        lines.append(f"| {CATEGORY_LABEL[cat]} | {inventory['counts'].get(cat, 0)} |")
    lines += ["", "## 能力清单", ""]
    for e in inventory["capabilities"]:
        flag = "" if e["confidence"] == "high" else "（显式不确定）"
        lines.append(f"- `{e['path']}` — {e['category']}{flag}")
    lines += ["", "> 说明：LEGACY_UNKNOWN 为显式未分类项，需人工复核后迁移。", ""]
    return "\n".join(lines)


def main() -> int:
    package_dir = Path(__file__).resolve().parent.parent
    out_dir = Path("docs/auditory_intelligence")
    out_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(package_dir)
    (out_dir / "current_capability_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "current_capability_inventory.md").write_text(
        render_markdown(inventory), encoding="utf-8"
    )
    print(f"inventory written to {out_dir} ({len(inventory['capabilities'])} capabilities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
