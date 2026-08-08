"""CLI handlers for approved execution (moodify capability plan/approve/execute)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from moodify.capability_registry.adapters import all_adapters
from moodify.capability_registry.execution.envelope import (
    ApprovedExecutionEnvelope,
    EnvelopeInput,
    envelope_dumps,
    envelope_loads,
    sign_envelope,
    verify_envelope,
)
from moodify.capability_registry.execution.gateway import ExecutionGateway, FileRecordStore

ENVELOPE_SCHEMA = "approved-execution-envelope/0.1"


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_capability_plan(args) -> int:
    """Build an unsigned envelope draft from capability + inputs + parameters."""
    adapter = next((a for a in all_adapters() if a.provider_id == args.provider), None)
    if adapter is None:
        print(f"ERROR: unknown provider: {args.provider}")
        return 2

    inputs: list[EnvelopeInput] = []
    for pair in args.input:
        if "=" not in pair:
            print(f"ERROR: input must be role=path: {pair}")
            return 2
        role, path_str = pair.split("=", 1)
        path = Path(path_str.strip())
        if not path.exists():
            print(f"ERROR: input missing: {path}")
            return 2
        inputs.append(EnvelopeInput(role=role.strip(), path=str(path.resolve()), sha256=_sha256_file(path)))

    parameters: dict = {}
    for pair in args.parameter or []:
        if "=" not in pair:
            print(f"ERROR: parameter must be key=value: {pair}")
            return 2
        key, value = pair.split("=", 1)
        parameters[key.strip()] = value.strip()

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = out_dir.resolve()

    envelope = ApprovedExecutionEnvelope(
        schema_version=ENVELOPE_SCHEMA,
        envelope_id=f"env-{uuid.uuid4().hex[:12]}",
        case_id=args.case_id,
        capability_id=adapter.capability_id,
        provider_id=adapter.provider_id,
        inputs=tuple(inputs),
        parameters=parameters,
        output_dir=str(out_dir),
        timeout_s=args.timeout,
        allow_network=False,
        created_by="cli",
    )
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(envelope_dumps(envelope), encoding="utf-8")
    print(f"Envelope draft: {target}")
    print(f"  case_id: {envelope.case_id}  capability: {envelope.capability_id}  provider: {envelope.provider_id}")
    print(f"  inputs: {len(inputs)}  status: envelope_created (unsigned)")
    print(f"  Approve with: capability approve --envelope {target}")
    return 0


def cmd_capability_approve(args) -> int:
    path = Path(args.envelope)
    if not path.exists():
        print(f"ERROR: envelope not found: {path}")
        return 1
    envelope = envelope_loads(path.read_text(encoding="utf-8"))
    if envelope.is_approved():
        print(f"ERROR: envelope already approved (issuer={envelope.approval.issuer})")
        return 2
    signed = sign_envelope(envelope, issuer=args.issuer, policy_version=args.policy_version)
    ok, reason = verify_envelope(signed)
    if not ok:
        print(f"ERROR: signature verification failed: {reason}")
        return 2
    path.write_text(envelope_dumps(signed), encoding="utf-8")
    print(f"Envelope approved: {path}")
    print(f"  issuer: {args.issuer}  policy_version: {args.policy_version}")
    print(f"  signature: {signed.approval.signature[:16]}...")
    return 0


def cmd_capability_execute(args) -> int:
    path = Path(args.envelope)
    if not path.exists():
        print(f"ERROR: envelope not found: {path}")
        return 1
    envelope = envelope_loads(path.read_text(encoding="utf-8"))
    ok, reason = verify_envelope(envelope)
    if not ok:
        print(f"ERROR: {reason}")
        print("  Approve first: capability approve --envelope <path>")
        return 2

    store = FileRecordStore(Path(args.records_dir))
    gateway = ExecutionGateway(store=store)
    record = gateway.execute(envelope)
    print(f"Execute: envelope={envelope.envelope_id} provider={envelope.provider_id} "
          f"status={record.status} class={record.error_class or '-'}")
    print(f"  record: {store.root / f'{record.record_id}.json'}")
    print(f"  elapsed: {record.elapsed_s:.2f}s  exit: {record.exit_code}")
    for artifact in record.artifacts:
        print(f"  artifact: {artifact}")
    for error in record.errors:
        print(f"  ERROR: {error}")
    if args.json:
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    return 0 if record.status == "completed" else 1


def register_execution_subparsers(subparsers) -> None:
    p_plan = subparsers.add_parser("plan", help="Build unsigned envelope draft")
    p_plan.add_argument("--provider", required=True)
    p_plan.add_argument("--case-id", required=True)
    p_plan.add_argument("--input", action="append", default=[], help="role=path (repeatable)")
    p_plan.add_argument("--parameter", action="append", default=[], help="key=value (repeatable)")
    p_plan.add_argument("--output-dir", required=True, help="execution output directory (new/empty)")
    p_plan.add_argument("--timeout", type=float, default=120.0)
    p_plan.add_argument("--out", required=True, help="envelope JSON path")

    p_approve = subparsers.add_parser("approve", help="Sign an envelope (local approval)")
    p_approve.add_argument("--envelope", required=True)
    p_approve.add_argument("--issuer", required=True)
    p_approve.add_argument("--policy-version", default="policy/0.1")

    p_execute = subparsers.add_parser("execute", help="Execute an approved envelope via the gateway")
    p_execute.add_argument("--envelope", required=True)
    p_execute.add_argument("--records-dir", default="execution_records")
    p_execute.add_argument("--json", action="store_true")
