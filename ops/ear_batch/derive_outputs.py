"""Derive traceable knowledge, alignment, and planning artifacts from batch evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def claims(run_dir: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (run_dir / "knowledge" / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line]


COMPONENT_PATTERNS = {
    "Auditory Representation": r"auditory representation",
    "Judgment Engine": r"judg(?:e|ment) engine|judgment layer",
    "Evidence Artifact": r"evidence artifact|evidence layer",
    "Production Case": r"production case",
    "Measurement Record": r"measurement record",
    "Auditory Report": r"auditory report",
    "Uncertainty Model": r"uncertainty (?:model|representation|estimate)",
    "WSE Sensor Layer": r"\bWSE\b|wave-spectral evolution",
    "MSE Structural Layer": r"\bMSE\b|musical-structural engineering",
    "PPE Reliability Layer": r"\bPPE\b|production process engineering",
    "Intervention Laboratory": r"intervention (?:lab|laboratory)",
    "Learning Loop": r"learning loop|case learning|learn from",
}


def tp103(run_dir: Path) -> None:
    source_claims = claims(run_dir)
    components = []
    for index, (name, pattern) in enumerate(COMPONENT_PATTERNS.items(), 1):
        matches = [item for item in source_claims if re.search(pattern, item["claim"], re.IGNORECASE)]
        components.append({"id": f"COMP-{index:03d}", "name": name, "status": "MATERIAL_PROPOSAL",
                           "source_claim_ids": [item["id"] for item in matches[:30]],
                           "chapters": sorted({item["chapter"] for item in matches}),
                           "note": "Candidate only; repository authority is evaluated separately."})
    write_json(run_dir / "knowledge" / "component_candidates.json",
               {"schema_version": 1, "components": components})
    lines = ["# Component and Interface Candidates", "",
             "Every entry is a material proposal, not implemented architecture.", "",
             "| ID | Candidate | Chapters | Source claims |", "|---|---|---|---:|"]
    for item in components:
        lines.append(f"| {item['id']} | {item['name']} | {', '.join(map(str, item['chapters']))} | {len(item['source_claim_ids'])} |")
    (run_dir / "knowledge" / "component_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


EVIDENCE_CATEGORIES = {
    "measurement": r"measur|metric|loudness|spectr|temporal|confidence|uncertainty",
    "evidence": r"evidence|artifact|record|provenance|traceab|explain",
    "verification": r"verif|validat|test|benchmark|compare|reproduc",
    "failure_recovery": r"fail|recover|retry|rollback|degrad|missing|corrupt",
    "human_authority": r"human|listen(?:er|ing)|subjective|expert|review",
}


def tp104(run_dir: Path) -> None:
    records = []
    for item in claims(run_dir):
        categories = [name for name, pattern in EVIDENCE_CATEGORIES.items()
                      if re.search(pattern, item["claim"], re.IGNORECASE)]
        if not categories:
            continue
        records.append({"id": f"REQ-{len(records)+1:05d}", "claim_id": item["id"],
                        "chapter": item["chapter"], "section": item["section"],
                        "source_path": item["source_path"], "categories": categories,
                        "requirement_text": item["claim"], "status": "MATERIAL_REQUIREMENT_CANDIDATE"})
    write_json(run_dir / "knowledge" / "evidence_requirements.json",
               {"schema_version": 1, "requirements": records})
    counts = {name: sum(name in item["categories"] for item in records) for name in EVIDENCE_CATEGORIES}
    lines = ["# Measurement, Evidence, Verification, and Failure Requirements", "",
             "Candidates are source-linked and remain unverified until mapped to implementation evidence.", "",
             f"- Requirement candidates: **{len(records)}**", ""]
    lines.extend(f"- {name.replace('_', ' ').title()}: **{count}**" for name, count in counts.items())
    (run_dir / "knowledge" / "evidence_requirements.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def tp105(run_dir: Path) -> None:
    records = []
    review = []
    for item in claims(run_dir):
        source_type = item["claim_type"]
        if source_type == "reported_external_evidence":
            label = "EXTERNAL_REPORTED_EVIDENCE"
        elif source_type == "proposal_or_requirement":
            label = "THEORY_OR_PROPOSAL"
        else:
            label = "THEORY_STATEMENT"
        record = {"claim_id": item["id"], "chapter": item["chapter"], "label": label,
                  "repository_status": "NOT_ESTABLISHED_BY_MATERIAL",
                  "source_path": item["source_path"], "claim": item["claim"]}
        records.append(record)
        if re.search(r"\b(?:Moodify|Ear v1) (?:has|uses|produces|records|provides)\b", item["claim"], re.IGNORECASE):
            review.append({"claim_id": item["id"], "reason": "Wording may imply implemented capability; repository evidence required."})
    path = run_dir / "knowledge" / "truth_labels.jsonl"
    path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8", newline="\n")
    lines = ["# Truth-Label Review", "",
             "No material claim was promoted to current verified product capability. External citations remain reported evidence, not locally reproduced truth.", "",
             f"- Claims labeled: **{len(records)}**", f"- Claims requiring later repository cross-check: **{len(review)}**", ""]
    lines.extend(f"- `{item['claim_id']}` — {item['reason']}" for item in review[:200])
    (run_dir / "knowledge" / "truth_label_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def tp106(run_dir: Path) -> None:
    requirements = load_json(run_dir / "knowledge" / "evidence_requirements.json")["requirements"]
    components = load_json(run_dir / "knowledge" / "component_candidates.json")["components"]
    component_by_claim = {}
    for component in components:
        for claim_id in component["source_claim_ids"]:
            component_by_claim.setdefault(claim_id, []).append(component["id"])
    path = run_dir / "knowledge" / "traceability.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["requirement_id", "claim_id", "chapter", "categories", "component_candidates",
                         "source_path", "implementation_status", "verification_status"])
        for item in requirements:
            writer.writerow([item["id"], item["claim_id"], item["chapter"], ";".join(item["categories"]),
                             ";".join(component_by_claim.get(item["claim_id"], [])), item["source_path"],
                             "UNMAPPED", "UNVERIFIED"])
    lines = ["# Chapter–Requirement–Evidence Traceability", "",
             f"- Rows: **{len(requirements)}**", "- Initial implementation status: `UNMAPPED`",
             "- Initial verification status: `UNVERIFIED`", "",
             "The CSV is the machine-readable handoff to repository alignment. Empty component mappings are explicit gaps, not extraction failures.", ""]
    (run_dir / "knowledge" / "traceability.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def tp203(run_dir: Path) -> None:
    capabilities = load_json(run_dir / "alignment" / "repository_capabilities.json")["capabilities"]
    unresolved = [item for item in capabilities if item["status"] == "UNRESOLVED"]
    write_json(run_dir / "alignment" / "authority_map.json",
               {"schema_version": 1, "authority_source": "AGENTS.md and docs/REPOSITORY_STATUS.md",
                "allowed_statuses": ["CANONICAL", "EXPERIMENTAL", "LEGACY", "HISTORICAL", "ABSENT", "UNRESOLVED"],
                "capabilities": capabilities, "human_decisions": [item["capability"] for item in unresolved]})
    lines = ["# Authority Review", "", "No authority status was promoted by this task.", "",
             "## Human decisions", ""]
    lines.extend(f"- `{item['capability']}` remains UNRESOLVED." for item in unresolved)
    lines.extend(["", "Legacy production-case orchestration remains preserved and non-authoritative.", ""])
    (run_dir / "alignment" / "authority_review.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def tp204(run_dir: Path) -> None:
    text = """# Orchestration Authority Risks

The supported mainline is `Import -> Analyze -> Diagnose -> Process -> Export`.
The wider `moodify-core-package/src/moodify/orchestration/workflow_engine.py`
production-case state machine is classified LEGACY. Branch-era trackers and
experimental workflow descriptions are evidence of design exploration, not a
second authority.

Risks:

- Promoting the legacy workflow engine would conflict with repository status.
- Treating this batch ledger as a product runtime would create a second state machine.
- Treating branch-only cloud/app systems as merged capability would overstate truth.
- Bulk-merging historical orchestration would bypass current tests and authority review.

Controls:

- `ops/ear_batch` manages only this offline knowledge-engineering run.
- It never imports or mutates the product orchestration layer.
- Product authority changes are emitted as human decisions, never auto-applied.
- Future implementation work should prefer narrow adapters and current contracts.
"""
    path = run_dir / "alignment" / "orchestration_risks.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def tp202(run_dir: Path) -> None:
    reqs = load_json(run_dir / "knowledge" / "evidence_requirements.json")["requirements"]
    capabilities = load_json(run_dir / "alignment" / "repository_capabilities.json")["capabilities"]
    status = {item["capability"]: item["status"] for item in capabilities}
    gap_areas = [
        {"id":"GAP-001","area":"WSE physical analysis baseline","status":status["Wave/spectral analysis"],
         "coverage":"Partial canonical metrics exist; Ear v1 time-indexed representation and invariance suite are not established.","patterns":r"WSE|spectr|loudness|phase|transient"},
        {"id":"GAP-002","area":"MSE musical-structural analysis","status":status["MSE structural analysis"],
         "coverage":"No canonical MSE subsystem.","patterns":r"MSE|musical structure|section|phrase|harmony|rhythm"},
        {"id":"GAP-003","area":"Evidence-linked judgment","status":"ABSENT",
         "coverage":"Diagnosis exists, but no verified canonical judgment/evidence/uncertainty contract.","patterns":r"judg|evidence|uncertainty|confidence|explain"},
        {"id":"GAP-004","area":"Production Case and learning loop","status":"EXPERIMENTAL",
         "coverage":"Treatment records exist experimentally; validated case learning is not canonical.","patterns":r"production case|learn|feedback|rule update"},
        {"id":"GAP-005","area":"Before/after verification","status":status["Before/after verification"],
         "coverage":"Experimental utilities exist without a single canonical comparison contract.","patterns":r"before|after|compare|verify|validation"},
        {"id":"GAP-006","area":"Reliable production process","status":"PARTIAL",
         "coverage":"A 24/7 data-node path exists, but wider Ear PPE contracts and authority remain incomplete.","patterns":r"PPE|recover|retry|queue|provenance|reproduc"},
        {"id":"GAP-007","area":"Human listening authority","status":"EXPERIMENTAL",
         "coverage":"Feedback fields exist; calibrated listening-review authority is not a canonical workflow.","patterns":r"human|listen|review|subjective"},
    ]
    for gap in gap_areas:
        pattern = gap.pop("patterns")
        matched = [item["id"] for item in reqs if re.search(pattern, item["requirement_text"], re.IGNORECASE)]
        gap["requirement_ids"] = matched[:500]
        gap["matched_requirement_count"] = len(matched)
    write_json(run_dir / "alignment" / "gap_analysis.json",
               {"schema_version": 1, "rule":"Material requirements are proposals until repository evidence verifies them.",
                "gaps": gap_areas})
    lines = ["# Ear v1 Material-to-Repository Gap Analysis", "",
             "The current canonical baseline is useful but substantially narrower than the monograph architecture.", "",
             "| Gap | Area | Current status | Matched requirements |", "|---|---|---|---:|"]
    for gap in gap_areas:
        lines.append(f"| {gap['id']} | {gap['area']} | {gap['status']} | {gap['matched_requirement_count']} |")
    lines.extend(["", "The largest authority-sensitive gaps are MSE, evidence-linked judgment, Production Case learning, and a canonical before/after verification contract.", ""])
    (run_dir / "alignment" / "gap_analysis.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def tp205(run_dir: Path) -> None:
    text = """# Moodify Ear v1 Engineering Scope

## Outcome

Build the first reproducible, evidence-linked auditory-intelligence baseline
around the verified `Import -> Analyze -> Diagnose -> Process -> Export` path,
without treating the full monograph architecture as already implemented.

## In scope

1. Versioned source identity and immutable Measurement Records.
2. A narrow Auditory Representation v1 contract using verified WSE metrics.
3. Separate measurement, judgment, evidence, and uncertainty records.
4. Reproducible Evidence Artifacts with provenance and parameter manifests.
5. Controlled before/after verification for the Intervention Laboratory.
6. Production Case records that preserve human listening decisions.
7. Controlled WSE sensitivity/invariance benchmarks and failure evidence.
8. Small adapters around the current mainline rather than replacement orchestration.

## Explicit non-goals

- Claiming full machine hearing or validated learning from the monograph alone.
- Promoting legacy orchestration, cloud runtime, or app integration.
- Automatic mastering as the product identity.
- Removing listening judgment or auto-accepting artistic conclusions.
- Implementing broad MSE before its contract and evidence gates are approved.
- Deleting historical/legacy systems as part of this batch.

## Human authority gates

- Approve the first judgment vocabulary and reference populations.
- Approve MSE scope and representation contract.
- Approve what counts as a validated Production Case.
- Listen to and accept/reject intervention outcomes.
- Decide cloud/app authority and any legacy migration.

## Failure and reuse

Every production case must retain source identity, measurements, evidence,
versions, verification result, failure state, and human decision. Failed cases
remain reusable negative evidence; retries never overwrite prior attempts.
"""
    path = run_dir / "planning" / "ear_v1_engineering_scope.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def epic_catalog() -> list[dict[str, Any]]:
    return [
        {"id":"EPIC-01","title":"Evidence contracts","outcome":"Versioned, separately addressable source, measurement, judgment, uncertainty, and evidence records.","gaps":["GAP-003","GAP-004"]},
        {"id":"EPIC-02","title":"WSE representation baseline","outcome":"A narrow Auditory Representation v1 assembled from verified physical metrics.","gaps":["GAP-001"]},
        {"id":"EPIC-03","title":"Controlled verification","outcome":"Sensitivity, invariance, and before/after checks produce reproducible evidence.","gaps":["GAP-005"]},
        {"id":"EPIC-04","title":"Production Case evidence loop","outcome":"Cases preserve attempts, decisions, evidence, and reusable failure history.","gaps":["GAP-004","GAP-006"]},
        {"id":"EPIC-05","title":"Human listening authority","outcome":"Listening decisions remain explicit, versioned, and non-overwritable.","gaps":["GAP-007"]},
        {"id":"EPIC-06","title":"PPE reliability","outcome":"Validation, recovery, and traceability are machine-checkable.","gaps":["GAP-006"]},
    ]


def work_item_catalog() -> list[dict[str, Any]]:
    return [
        {"id":"WI-001","epic":"EPIC-01","title":"Define SourceIdentity JSON Schema","deps":[],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/source_identity.schema.json","tests/ear_v1_contracts/test_source_identity_schema.py"],"acceptance":"Valid and invalid fixtures prove immutable identity, path-independent digest, media metadata, and schema version fields."},
        {"id":"WI-002","epic":"EPIC-01","title":"Define MeasurementRecord JSON Schema","deps":["WI-001"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/measurement_record.schema.json","tests/ear_v1_contracts/test_measurement_record_schema.py"],"acceptance":"Schema separates measured value, unit, time support, parameters, implementation version, source identity, and tolerance policy."},
        {"id":"WI-003","epic":"EPIC-01","title":"Define EvidenceArtifact JSON Schema","deps":["WI-001","WI-002"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/evidence_artifact.schema.json","tests/ear_v1_contracts/test_evidence_artifact_schema.py"],"acceptance":"Evidence links immutable inputs and measurement records, carries provenance, and cannot masquerade as a judgment."},
        {"id":"WI-004","epic":"EPIC-01","title":"Define Judgment and Uncertainty schemas","deps":["WI-002","WI-003"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/judgment_record.schema.json","schemas/ear_v1/uncertainty.schema.json","tests/ear_v1_contracts/test_judgment_schema.py"],"acceptance":"Judgment references but never overwrites measurements; UNCERTAIN and INSUFFICIENT_EVIDENCE are valid outputs; severity and confidence are separate."},
        {"id":"WI-005","epic":"EPIC-06","title":"Create Ear v1 contract validator CLI","deps":["WI-001","WI-002","WI-003","WI-004"],"risk":"safe","allowed_paths":["tools/ear_v1_contracts","tests/ear_v1_contracts"],"outputs":["tools/ear_v1_contracts/validate.py","tests/ear_v1_contracts/test_validator_cli.py"],"acceptance":"CLI validates one artifact or a directory, returns nonzero on invalid input, and emits deterministic JSON evidence."},
        {"id":"WI-006","epic":"EPIC-06","title":"Build provenance manifest utility","deps":["WI-001"],"risk":"safe","allowed_paths":["tools/ear_v1_contracts","tests/ear_v1_contracts"],"outputs":["tools/ear_v1_contracts/provenance.py","tests/ear_v1_contracts/test_provenance.py"],"acceptance":"Utility hashes immutable inputs, records versions and parameters, writes atomically, and detects later source drift."},
        {"id":"WI-007","epic":"EPIC-03","title":"Define controlled WSE experiment manifest","deps":["WI-002","WI-003"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/wse_experiment.schema.json","tests/ear_v1_contracts/test_wse_experiment_schema.py"],"acceptance":"Manifest distinguishes transform, expected sensitivity/invariance, tolerances, negative controls, and evidence outputs."},
        {"id":"WI-008","epic":"EPIC-03","title":"Add deterministic synthetic fixture definitions","deps":["WI-007"],"risk":"safe","allowed_paths":["configs/ear_v1","tests/ear_v1_contracts"],"outputs":["configs/ear_v1/synthetic_fixtures.json","tests/ear_v1_contracts/test_fixture_definitions.py"],"acceptance":"Definitions are parameter-only, reproducible, contain no private audio, and cover silence, tone, impulse, clipping, phase inversion, and lossless rewrap controls."},
        {"id":"WI-009","epic":"EPIC-03","title":"Define experimental before-after comparison contract","deps":["WI-002","WI-003","WI-007"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/before_after_comparison.schema.json","tests/ear_v1_contracts/test_before_after_schema.py"],"acceptance":"Contract is explicitly EXPERIMENTAL and records pairing, alignment, changed parameters, metrics, tolerance, and verification outcome."},
        {"id":"WI-010","epic":"EPIC-04","title":"Define experimental ProductionCase record","deps":["WI-003","WI-004"],"risk":"safe","allowed_paths":["schemas/ear_v1","tests/ear_v1_contracts"],"outputs":["schemas/ear_v1/production_case.schema.json","tests/ear_v1_contracts/test_production_case_schema.py"],"acceptance":"Case preserves attempts, failures, evidence, rule/model versions, and human decision without claiming autonomous learning."},
        {"id":"WI-011","epic":"EPIC-05","title":"Design listening-review authority vocabulary","deps":["WI-004","WI-010"],"risk":"human-review","allowed_paths":["docs/ear_v1"],"outputs":["docs/ear_v1/listening_authority_review.md"],"acceptance":"Human approves vocabulary, override semantics, and validation population before implementation."},
        {"id":"WI-012","epic":"EPIC-06","title":"Create traceability integrity checker","deps":["WI-005"],"risk":"safe","allowed_paths":["tools/ear_v1_contracts","tests/ear_v1_contracts"],"outputs":["tools/ear_v1_contracts/check_traceability.py","tests/ear_v1_contracts/test_traceability_checker.py"],"acceptance":"Checker rejects missing source, measurement, evidence, schema-version, or verification links and produces a reusable evidence report."},
    ]


def tp301(run_dir: Path) -> None:
    epics = epic_catalog()
    write_json(run_dir / "planning" / "epics.json", {"schema_version":1,"epics":epics})
    lines=["# Moodify Ear v1 Engineering Epics","", "| Epic | Outcome | Gaps |","|---|---|---|"]
    lines.extend(f"| {e['id']} {e['title']} | {e['outcome']} | {', '.join(e['gaps'])} |" for e in epics)
    (run_dir / "planning" / "epics.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")


def tp302(run_dir: Path) -> None:
    items=work_item_catalog()
    path=run_dir / "planning" / "work_items.jsonl"
    path.write_text("".join(json.dumps(i,ensure_ascii=False)+"\n" for i in items),encoding="utf-8",newline="\n")
    lines=["# Verifiable Work Items","", "| Work item | Epic | Risk | Dependencies |","|---|---|---|---|"]
    lines.extend(f"| {i['id']} {i['title']} | {i['epic']} | {i['risk']} | {', '.join(i['deps']) or 'none'} |" for i in items)
    (run_dir / "planning" / "work_items.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")


def tp303(run_dir: Path) -> None:
    items=work_item_catalog()
    path=run_dir / "planning" / "verification_matrix.csv"
    with path.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle);writer.writerow(["work_item","automated_gate","evidence","failure_action","human_gate"])
        for item in items:
            human=item["risk"]=="human-review"
            writer.writerow([item["id"],item["acceptance"],"task evidence JSON plus test output","retry twice then isolate","required" if human else "none"])
    (run_dir / "planning" / "verification_matrix.md").write_text(
        "# Verification Matrix\n\nEvery automated item requires declared outputs, focused tests, full contract-suite regression, and task evidence. Human-review items cannot be auto-promoted.\n",
        encoding="utf-8",newline="\n")


def tp304(run_dir: Path) -> None:
    items=work_item_catalog()
    graph={"schema_version":1,"nodes":[{"id":i["id"],"deps":i["deps"],"priority":index+1} for index,i in enumerate(items)]}
    write_json(run_dir / "planning" / "execution_dag.json",graph)
    lines=["# Execution DAG","", "The graph is acyclic and ordered by contract dependency.",""]
    lines.extend(f"- `{i['id']}` <- {', '.join(i['deps']) or 'root'}" for i in items)
    (run_dir / "planning" / "execution_dag.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")


def tp305(run_dir: Path) -> None:
    items=work_item_catalog()
    selected=[i for i in items if i["risk"]=="safe"]
    rejected=[{"id":i["id"],"reason":"Requires explicit human vocabulary/authority approval."} for i in items if i["risk"]!="safe"]
    write_json(run_dir / "planning" / "unattended_batch.json",
               {"schema_version":1,"selection_policy":"reversible, bounded, testable, no secrets/publishing/deletion/listening judgment/authority change",
                "selected":selected,"rejected":rejected})
    lines=["# Unattended Implementation Batch","",f"- Selected: **{len(selected)}**",f"- Human-gated: **{len(rejected)}**","",
           "Selected work creates versioned contracts, validators, provenance, synthetic definitions, and tests. It does not process private audio or promote experimental capability.",""]
    lines.extend(f"- `{i['id']}` {i['title']}" for i in selected)
    lines.extend(["","## Held for human authority",""]+[f"- `{i['id']}` — {i['reason']}" for i in rejected])
    (run_dir / "planning" / "unattended_batch.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")


TASKS = {"TP-103": tp103, "TP-104": tp104, "TP-105": tp105,
         "TP-106": tp106, "TP-202": tp202, "TP-203": tp203,
         "TP-204": tp204, "TP-205": tp205, "TP-301": tp301,
         "TP-302": tp302, "TP-303": tp303, "TP-304": tp304,
         "TP-305": tp305}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=sorted(TASKS))
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    TASKS[args.task](Path(args.run_dir).resolve())


if __name__ == "__main__":
    main()
