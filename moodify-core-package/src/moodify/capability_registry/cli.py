"""CLI handlers for the capability registry."""

from __future__ import annotations

import json

from moodify.capability_registry.bootstrap import build_registry, load_registry, write_registry
from moodify.capability_registry.detect import detect_all, python_version
from moodify.capability_registry.model import registry_dumps


def cmd_capabilities_probe(args) -> int:
    print(f"Python: {python_version()}")
    for name, result in detect_all().items():
        state = "found" if result.found else "MISSING"
        ver = result.version or "-"
        print(f"  {name:12s} {state:8s} {ver[:60]}")
        if result.known_failure_modes:
            for mode in result.known_failure_modes:
                print(f"               ! {mode}")
    if args.json:
        print(json.dumps({k: v.to_dict() for k, v in detect_all().items()}, ensure_ascii=False, indent=2))
    return 0


def cmd_capabilities_regenerate(args) -> int:
    registry = build_registry()
    path = write_registry(registry)
    print(f"Registry written: {path}")
    print(f"  capabilities: {len(registry.capabilities)}")
    print(f"  providers:    {len(registry.providers)}")
    print(f"  active:       {len(registry.active_providers())}")
    return 0


def cmd_capabilities_list(args) -> int:
    registry = load_registry()
    print(f"\nMoodify Capability Registry ({registry.schema_version})")
    for cap in registry.capabilities:
        providers = registry.providers_for(cap.capability_id)
        active = [p for p in providers if p.status == "active"]
        state = ", ".join(p.provider_id for p in active) or "NO ACTIVE PROVIDER"
        print(f"\n  {cap.capability_id}")
        print(f"    purpose:   {cap.purpose}")
        print(f"    providers: {state}")
        for p in providers:
            if p.status != "active":
                print(f"      {p.provider_id}: {p.status}")
    if args.json:
        print(registry_dumps(registry))
    return 0


def cmd_capabilities(args) -> int:
    from moodify.capability_registry.adapters.cli import (
        cmd_capability_adapters,
        cmd_capability_invoke,
    )
    from moodify.capability_registry.execution.cli import (
        cmd_capability_approve,
        cmd_capability_execute,
        cmd_capability_plan,
    )
    from moodify.capability_registry.validation.cli import (
        cmd_capability_candidates,
        cmd_capability_validate,
    )
    from moodify.capability_registry.knowledge.cli import (
        cmd_capability_history,
        cmd_capability_policy,
        cmd_capability_propose,
    )

    dispatch = {
        "probe": cmd_capabilities_probe,
        "regenerate": cmd_capabilities_regenerate,
        "list": cmd_capabilities_list,
        "adapters": cmd_capability_adapters,
        "invoke": cmd_capability_invoke,
        "plan": cmd_capability_plan,
        "approve": cmd_capability_approve,
        "execute": cmd_capability_execute,
        "validate": cmd_capability_validate,
        "candidates": cmd_capability_candidates,
        "history": cmd_capability_history,
        "propose": cmd_capability_propose,
        "policy": cmd_capability_policy,
    }
    handler = dispatch.get(getattr(args, "capabilities_command", None))
    if handler is None:
        print("ERROR: capabilities command required: probe | regenerate | list | adapters | invoke | plan | approve | execute | validate | candidates | history | propose | policy")
        return 2
    return handler(args)
