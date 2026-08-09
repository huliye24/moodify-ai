#!/usr/bin/env python3
"""Build asset registry indexes and reports (DSK-RJWC-ASSET-REGISTRY-001).

Reads asset records from asset-registry/assets/*.json and writes:
  - indexes/: six Moodify core families + RJWC class index + non-asset index
  - reports/: ASSET_REGISTRY_SUMMARY, ASSET_GAPS, THIRD_PARTY_DEPENDENCIES,
    OWNERSHIP_UNCERTAINTIES
Usage: python scripts/build_asset_registry.py [repo_root]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

FAMILIES = {
    "auditory_case_corpus": {
        "name": "Auditory Case Corpus",
        "match": ("name", "notes", "asset_subclass"),
        "terms": ("case", "corpus", "案例", "golden", "语料"),
    },
    "preference_ranking_corpus": {
        "name": "Preference & Ranking Corpus",
        "match": ("name", "notes"),
        "terms": ("preference", "ranking", "偏好", "排序"),
    },
    "auditory_knowledge_system": {
        "name": "Auditory Knowledge System",
        "match": ("name", "notes", "asset_subclass"),
        "terms": ("wse", "mse", "ppe", "knowledge", "标准", "规则"),
    },
    "auditory_representation": {
        "name": "Auditory Representation",
        "match": ("name", "notes", "asset_subclass"),
        "terms": ("representation", "contract", "表示", "契约"),
    },
    "models_decision_systems": {
        "name": "Models & Decision Systems",
        "match": ("name", "notes"),
        "terms": ("judge", "ranker", "model", "决策", "排名", "判断"),
    },
    "production_system": {
        "name": "Production System",
        "match": ("name", "notes"),
        "terms": ("control spine", "production", "evidence", "queue", "cwc", "计量"),
    },
}


def _load_records(assets_dir: Path) -> list[dict]:
    records = []
    for path in sorted(assets_dir.glob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _match(record: dict, terms: tuple[str, ...]) -> bool:
    text = " ".join(str(record.get(field, "")) for field in ("name", "notes", "asset_subclass", "asset_class"))
    return any(term.lower() in text.lower() for term in terms)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    registry = root / "asset-registry"
    indexes_dir = registry / "indexes"
    reports_dir = registry / "reports"
    indexes_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    records = _load_records(registry / "assets")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # -- six Moodify core family indexes -------------------------------------
    for key, family in FAMILIES.items():
        members = [r for r in records if _match(r, family["terms"])]
        payload = {
            "index_id": f"index-{key}",
            "family": family["name"],
            "generated_at": now,
            "member_count": len(members),
            "members": [{"asset_id": r["asset_id"], "name": r["name"]} for r in members],
        }
        (indexes_dir / f"{key}.index.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # -- RJWC class index -----------------------------------------------------
    by_class: dict[str, list[dict]] = {}
    for record in records:
        by_class.setdefault(record["asset_class"], []).append(
            {"asset_id": record["asset_id"], "name": record["name"]}
        )
    (indexes_dir / "rjwc_asset_classes.index.json").write_text(
        json.dumps({
            "index_id": "index-rjwc-asset-classes",
            "generated_at": now,
            "classes": by_class,
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # -- non-asset index (operational capabilities / services / experiments) -
    non_assets = {
        "operational_capabilities": [
            "deployment & demo operations (scripts/deploy/, cloud_status.py)",
            "audit & scan tooling (scripts/audit_focus/, scan scripts)",
            "CI/test execution environment (local JBR/venv setup)",
        ],
        "third_party_services": [
            "阿里云 ECS demo host (120.55.191.146)",
            "腾讯云 CVM hosts (139.199.186.106 / 43.134.12.248 / 43.156.175.4)",
        ],
        "temporary_experiments": [
            "docs/experiments/ 与 artifacts/ 下未定稿实验",
            "phase1 相关探索产物（docs/architecture/phase1_*）",
        ],
        "dependencies": [
            "ffmpeg/ffprobe (external decode)",
            "numpy/scipy/librosa/pyloudnorm/pydantic/PyYAML/fastapi (pypi)",
            "MuseScore / whisperX / basic-pitch (optional backends)",
        ],
        "deprecated_items": [
            "CWC 经济功能（补丁 08 已删除，git 历史可恢复）",
            "legacy WorkflowOrchestrator（归档兼容路径）",
            "night/moodify_daily_run_system* 打包重复",
        ],
    }
    (indexes_dir / "non_assets.index.json").write_text(
        json.dumps({"index_id": "index-non-assets", "generated_at": now, **non_assets},
                   ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # -- reports ----------------------------------------------------------------
    (reports_dir / "ASSET_REGISTRY_SUMMARY.md").write_text(
        _summary(records, now), encoding="utf-8"
    )
    (reports_dir / "ASSET_GAPS.md").write_text(_gaps(records), encoding="utf-8")
    (reports_dir / "THIRD_PARTY_DEPENDENCIES.md").write_text(
        _third_party(records), encoding="utf-8"
    )
    (reports_dir / "OWNERSHIP_UNCERTAINTIES.md").write_text(
        _ownership(records), encoding="utf-8"
    )
    print(json.dumps({"ok": True, "record_count": len(records), "reports": 4,
                      "indexes": 8, "generated_at": now}, ensure_ascii=False, indent=2))
    return 0


def _summary(records: list[dict], now: str) -> str:
    by_class: dict[str, int] = {}
    for record in records:
        by_class[record["asset_class"]] = by_class.get(record["asset_class"], 0) + 1
    lines = [
        "# ASSET_REGISTRY_SUMMARY",
        "",
        f"生成：{now}",
        f"资产记录数：{len(records)}",
        "",
        "## 按资产类别",
        "",
    ]
    for asset_class in sorted(by_class):
        lines.append(f"- {asset_class}: {by_class[asset_class]}")
    lines += ["", "## 按所有权", ""]
    by_owner: dict[str, int] = {}
    for record in records:
        by_owner[record["ownership_status"]] = by_owner.get(record["ownership_status"], 0) + 1
    for status in sorted(by_owner):
        lines.append(f"- {status}: {by_owner[status]}")
    return "\n".join(lines) + "\n"


def _gaps(records: list[dict]) -> str:
    lines = ["# ASSET_GAPS", "", "## 缺失项（按资产）", ""]
    for record in records:
        gaps = []
        if not record.get("evidence_refs") and record["ownership_status"] in {"OWNED", "CONTROLLED_RESOURCE"}:
            gaps.append("missing evidence_refs")
        if not record.get("current_version") and record["production_status"] == "PRODUCTION":
            gaps.append("missing current_version")
        if record.get("ownership_status") == "UNKNOWN":
            gaps.append("unknown ownership")
        if record.get("production_status") == "LEGACY_UNVERIFIED":
            gaps.append("legacy unverified provenance")
        if not record.get("license_status"):
            gaps.append("missing license status")
        if gaps:
            lines.append(f"- {record['asset_id']} ({record['name']}): {', '.join(gaps)}")
    return "\n".join(lines) + "\n"


def _third_party(records: list[dict]) -> str:
    lines = ["# THIRD_PARTY_DEPENDENCIES", ""]
    seen: set[str] = set()
    for record in records:
        for dep in record.get("third_party_dependencies", []):
            key = f"{dep.get('name')} ({dep.get('license', '?')})"
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"- {key} — {dep.get('role', '')} (used by {record['asset_id']})")
    return "\n".join(lines) + "\n"


def _ownership(records: list[dict]) -> str:
    lines = ["# OWNERSHIP_UNCERTAINTIES", ""]
    for record in records:
        if record.get("ownership_status") in {"UNKNOWN", "DISPUTED"} or record.get("owner_entity", "").startswith("UNKNOWN"):
            lines.append(f"- {record['asset_id']} ({record['name']}): ownership_status={record['ownership_status']}, owner={record['owner_entity']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
