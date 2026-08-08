"""CLI handlers for provider adapters (moodify capability adapters/invoke)."""

from __future__ import annotations

import json

from moodify.capability_registry.adapters import all_adapters
from moodify.capability_registry.adapters.base import InvokeRequest


def cmd_capability_adapters(args) -> int:
    print("\nMoodify provider adapters:")
    for adapter in all_adapters():
        available = adapter.detect()
        state = "available" if available else "UNAVAILABLE"
        version = adapter.version() or "-"
        print(f"  {adapter.provider_id:20s} {state:12s} {version[:50]}  -> {adapter.capability_id}")
    if args.json:
        print(json.dumps(
            [{
                "provider_id": a.provider_id,
                "capability_id": a.capability_id,
                "available": a.detect(),
                "version": a.version(),
                "license_label": getattr(a, "license_label", ""),
            } for a in all_adapters()],
            ensure_ascii=False, indent=2,
        ))
    return 0


def cmd_capability_invoke(args) -> int:
    provider_id = args.provider
    adapter = next((a for a in all_adapters() if a.provider_id == provider_id), None)
    if adapter is None:
        print(f"ERROR: unknown provider: {provider_id}")
        print(f"  known: {', '.join(a.provider_id for a in all_adapters())}")
        return 2

    inputs: dict[str, str] = {}
    for pair in args.input:
        if "=" not in pair:
            print(f"ERROR: input must be role=path: {pair}")
            return 2
        role, path = pair.split("=", 1)
        inputs[role.strip()] = path.strip()

    parameters: dict = {}
    for pair in args.parameter or []:
        if "=" not in pair:
            print(f"ERROR: parameter must be key=value: {pair}")
            return 2
        key, value = pair.split("=", 1)
        parameters[key.strip()] = value.strip()

    request = InvokeRequest(
        capability_id=adapter.capability_id,
        inputs=inputs,
        parameters=parameters,
        output_dir=args.output_dir,
        timeout_s=args.timeout,
    )
    result = adapter.invoke(request)
    print(f"Invoke: provider={provider_id} capability={adapter.capability_id} "
          f"status={result.status} class={result.error_class or '-'}")
    print(f"  elapsed: {result.elapsed_s:.2f}s  exit: {result.exit_code}")
    for artifact in result.artifacts:
        print(f"  artifact: {artifact}")
    for error in result.errors:
        print(f"  ERROR: {error}")
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status == "success" else 1


def register_adapter_subparsers(subparsers) -> None:
    p_adapters = subparsers.add_parser("adapters", help="List provider adapters and availability")
    p_adapters.add_argument("--json", action="store_true")
    p_invoke = subparsers.add_parser("invoke", help="Invoke a provider adapter (explicit controlled call)")
    p_invoke.add_argument("--provider", required=True, help="provider_id (e.g. ffmpeg.cli)")
    p_invoke.add_argument("--input", action="append", default=[], help="role=path (repeatable)")
    p_invoke.add_argument("--parameter", action="append", default=[], help="key=value (repeatable)")
    p_invoke.add_argument("--output-dir", required=True, help="new/empty output directory")
    p_invoke.add_argument("--timeout", type=float, default=120.0)
    p_invoke.add_argument("--json", action="store_true")
