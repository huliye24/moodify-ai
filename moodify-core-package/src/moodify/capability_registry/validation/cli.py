"""CLI handlers for validation and candidates (moodify capability validate/candidates)."""

from __future__ import annotations

import json
from pathlib import Path

from moodify.capability_registry.adapters import all_adapters
from moodify.capability_registry.validation.rules import validate_capability


def _load_evidence(record_path: Path) -> dict:
    data = json.loads(record_path.read_text(encoding="utf-8"))
    return {
        "artifacts": data.get("artifacts", []),
        "input_hashes": data.get("evidence", {}).get("input_hashes", {}),
        "primary_artifact": data.get("artifacts", [None])[0],
        "roundtrip_report": data.get("evidence", {}).get("roundtrip_report"),
    }


def cmd_capability_validate(args) -> int:
    """Replay validation against an existing ExecutionRecord."""
    record_path = Path(args.record)
    if not record_path.exists():
        print(f"ERROR: record not found: {record_path}")
        return 1
    data = json.loads(record_path.read_text(encoding="utf-8"))
    capability_id = data.get("capability_id", "")
    context = _load_evidence(record_path)
    report = validate_capability(capability_id, context)
    print(f"Validate: capability={capability_id} passed={report.passed()}")
    for result in report.results:
        mark = "PASS" if result.passed else f"FAIL[{result.level}]"
        detail = "" if result.passed else f" {result.message}"
        print(f"  {mark:10s} {result.rule_id:24s}{detail}")
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.passed() else 1


def cmd_capability_candidates(args) -> int:
    """Generate candidate variants for a capability from a base envelope."""
    from moodify.capability_registry.execution.envelope import envelope_loads

    env_path = Path(args.envelope)
    if not env_path.exists():
        print(f"ERROR: envelope not found: {env_path}")
        return 1
    envelope = envelope_loads(env_path.read_text(encoding="utf-8"))

    adapter = next((a for a in all_adapters() if a.provider_id == envelope.provider_id), None)
    if adapter is None:
        print(f"ERROR: unknown provider: {envelope.provider_id}")
        return 2

    # parameter variants: each is a candidate spec (same provider, different params)
    variants = args.variant or []
    specs = []
    base_label = f"{envelope.provider_id}-base"
    specs.append({"label": base_label, "parameters": dict(envelope.parameters)})
    for i, variant in enumerate(variants):
        if "=" not in variant:
            print(f"ERROR: variant must be key=value: {variant}")
            return 2
        key, value = variant.split("=", 1)
        params = dict(envelope.parameters)
        params[key.strip()] = value.strip()
        specs.append({"label": f"{envelope.provider_id}-v{i + 1}", "parameters": params})

    print(f"Candidates for capability={envelope.capability_id} provider={envelope.provider_id}")
    for spec in specs:
        print(f"  {spec['label']:24s} params={spec['parameters']}")
    print(f"\n  Note: {len(specs)} candidate specs; execution requires an approved envelope "
          f"per variant (019 immutability).")
    if args.json:
        print(json.dumps(specs, ensure_ascii=False, indent=2))
    return 0


def register_validation_subparsers(subparsers) -> None:
    p_validate = subparsers.add_parser("validate", help="Replay validation against an ExecutionRecord")
    p_validate.add_argument("--record", required=True, help="ExecutionRecord JSON path")
    p_validate.add_argument("--json", action="store_true")

    p_candidates = subparsers.add_parser("candidates", help="Generate candidate variants from a base envelope")
    p_candidates.add_argument("--envelope", required=True)
    p_candidates.add_argument("--variant", action="append", default=[], help="key=value parameter variant (repeatable)")
    p_candidates.add_argument("--json", action="store_true")
