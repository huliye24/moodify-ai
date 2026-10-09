"""Probe orchestration: declared provider → runtime truth, plus the policy join.

Two public answers, deliberately separate:

* :func:`probe_providers` — runtime truth only, policy-free. It never asks
  "may I use this?"; it answers "would this run here?".
* :func:`runtime_report` — the join of that truth with the pure router's
  eligibility. The join is what makes the four legitimate states readable:
  eligible-but-unavailable, eligible-and-available, ineligible-but-installed,
  and unknown-because-unprobeable.

The router is not modified, wrapped or re-implemented here. This module
*calls* it; the decision semantics stay in ``capabilities.router``.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..capabilities.models import Provider
from ..capabilities.policy import ProviderPolicy
from ..capabilities.registry import CapabilityRegistry
from ..capabilities.router import eligible_providers
from . import adapters
from .models import (
    ProviderProbe,
    ProviderRuntimeReport,
    RequirementCheck,
    RequirementStatus,
    RuntimeReport,
    probe_status_for,
)
from .specs import (
    SPECS_BY_PROVIDER,
    ExecutableCheck,
    ImportCheck,
    ProbeSpec,
    PythonVersionCheck,
    UnsupportedCheck,
    VenvCheck,
)

#: Remedy text shared by every missing-executable check. The runtime contract
#: is PATH-based; the probe reports the requirement, it never installs.
_FFMPEG_REMEDY = ("install ffmpeg (which provides both ffmpeg and ffprobe) and "
                  "ensure it is on PATH; see docs/development/THINKPAD_RUNTIME_ARCHITECTURE.md")


def _resolvers() -> dict[str, Any]:
    """Canonical executable resolvers — the processing runtime's own.

    Imported lazily so this module stays cheap to import and so the runtime
    package never becomes an import-time dependency of the auditory package.
    """
    from ..auditory.decode import _which_ffmpeg, _which_ffprobe

    return {"ffmpeg": _which_ffmpeg, "ffprobe": _which_ffprobe}


# ── individual checks ─────────────────────────────────────────────────────────

def _check_python_version(check: PythonVersionCheck) -> RequirementCheck:
    version = adapters.platform_version()
    interpreter = sys.executable
    if adapters.version_at_least(version, check.minimum):
        return RequirementCheck(
            requirement=check.requirement,
            kind="python_version",
            status=RequirementStatus.SATISFIED,
            detail=f"interpreter runs python {version}",
        )
    return RequirementCheck(
        requirement=check.requirement,
        kind="python_version",
        status=RequirementStatus.MISSING,
        detail=f"interpreter runs python {version}, below the declared >={check.minimum}",
        remedy=f"run Moodify on a python>={check.minimum} interpreter "
               f"(this one: {interpreter})",
    )


def _package_check_result(fact: dict[str, Any], package: ImportCheck) -> RequirementCheck:
    """Map one import fact onto the requirement's check record."""
    what = package.distribution or package.module
    if not fact.get("ok"):
        detail = f"import {package.module} failed: {fact.get('error') or 'unknown error'}"
        return RequirementCheck(
            requirement=package.requirement, kind="python_import",
            status=RequirementStatus.MISSING, detail=detail,
            remedy=f"install {what} into the interpreter shown in evidence",
        )
    version = fact.get("version")
    shown = f"{what} {version}" if version else f"{what} (version not published)"
    if package.pin is not None:
        if version is None:
            return RequirementCheck(
                requirement=package.requirement, kind="python_import",
                status=RequirementStatus.UNKNOWN,
                detail=f"{package.module} imports, but no distribution metadata "
                       f"exists to verify the declared pin =={package.pin}",
            )
        if fact.get("pin_ok") is False:
            return RequirementCheck(
                requirement=package.requirement, kind="python_import",
                status=RequirementStatus.MISMATCH,
                detail=f"{shown} does not match the declared pin =={package.pin}",
                remedy=f"install {what}=={package.pin}, or update the declaration",
            )
    return RequirementCheck(
        requirement=package.requirement, kind="python_import",
        status=RequirementStatus.SATISFIED,
        detail=f"imported {shown}",
    )


def _check_import(check: ImportCheck) -> RequirementCheck:
    fact = adapters.import_fact(check.module, check.distribution, check.pin)
    return _package_check_result(fact, check)


def _check_executable(
    check: ExecutableCheck, resolvers: dict[str, Any]
) -> tuple[RequirementCheck, adapters.ExecutableFact, list[str]]:
    fact = adapters.executable_fact(resolvers[check.resolver])
    warnings: list[str] = []
    if not fact.found:
        result = RequirementCheck(
            requirement=check.requirement, kind="executable",
            status=RequirementStatus.MISSING,
            detail=f"{check.requirement} not found via the runtime resolver: "
                   f"{fact.error or 'not found'}",
            remedy=_FFMPEG_REMEDY,
        )
    elif fact.timed_out:
        result = RequirementCheck(
            requirement=check.requirement, kind="executable",
            status=RequirementStatus.UNKNOWN,
            detail=f"{check.requirement} did not answer -version within "
                   f"{adapters.EXECUTABLE_TIMEOUT_S:.0f}s",
        )
    elif not fact.ran:
        result = RequirementCheck(
            requirement=check.requirement, kind="executable",
            status=RequirementStatus.MISSING,
            detail=f"{check.requirement} exists at {fact.path} but -version failed: "
                   f"{fact.error or 'nonzero exit'}",
        )
    else:
        detail = (f"resolved {fact.path}; {fact.version}" if fact.version
                  else f"resolved {fact.path}; version output not parseable")
        if not fact.version:
            warnings.append(f"{check.requirement} -version produced no parseable output")
        result = RequirementCheck(
            requirement=check.requirement, kind="executable",
            status=RequirementStatus.SATISFIED, detail=detail,
        )
    return result, fact, warnings


def _venv_missing_checks(
    check: VenvCheck, candidates: tuple[Any, ...]
) -> list[RequirementCheck]:
    """Every requirement a venv backs is MISSING when the venv is absent.

    This is a definitive negative: the declared location was looked for and a
    typed absence is the result — not "cannot verify".
    """
    where = ", ".join(str(candidate) for candidate in candidates) or "(no candidate location)"
    remedy = (
        f"create the venv and install its requirements, or point {check.env_var} "
        f"at an existing one (see moodify-desktop/scripts/requirements-*.txt); "
        f"looked at: {where}"
    )
    checks = [RequirementCheck(
        requirement=check.python_requirement, kind="python_version",
        status=RequirementStatus.MISSING,
        detail=f"{check.venv_name} not found; no interpreter to check ({where})",
        remedy=remedy,
    )]
    for package in check.packages:
        checks.append(RequirementCheck(
            requirement=package.requirement, kind="external_venv",
            status=RequirementStatus.MISSING,
            detail=f"{check.venv_name} not found; cannot verify {package.requirement}",
            remedy=remedy,
        ))
    checks.append(RequirementCheck(
        requirement=check.requirement, kind="external_venv",
        status=RequirementStatus.MISSING,
        detail=f"no runnable interpreter at {where}",
        remedy=remedy,
    ))
    return checks


def _venv_unverified_checks(check: VenvCheck, environment: str,
                            detail: str) -> list[RequirementCheck]:
    """All-UNKNOWN when the venv exists but could not be verified."""
    checks = [RequirementCheck(
        requirement=check.python_requirement, kind="python_version",
        status=RequirementStatus.UNKNOWN, detail=detail,
    )]
    for package in check.packages:
        checks.append(RequirementCheck(
            requirement=package.requirement, kind="external_venv",
            status=RequirementStatus.UNKNOWN, detail=detail,
        ))
    checks.append(RequirementCheck(
        requirement=check.requirement, kind="external_venv",
        status=RequirementStatus.UNKNOWN,
        detail=f"interpreter present at {environment} but unusable to the probe: {detail}",
    ))
    return checks


def _venv_answered_checks(check: VenvCheck, venv_dir: Path,
                          fact: adapters.VenvFact) -> list[RequirementCheck]:
    """The checks for a venv whose child ran and answered."""
    checks: list[RequirementCheck] = []
    if adapters.version_at_least(fact.python_version, check.minimum_python):
        checks.append(RequirementCheck(
            requirement=check.python_requirement, kind="python_version",
            status=RequirementStatus.SATISFIED,
            detail=f"venv interpreter runs python {fact.python_version}",
        ))
    else:
        checks.append(RequirementCheck(
            requirement=check.python_requirement, kind="python_version",
            status=RequirementStatus.MISSING,
            detail=f"venv interpreter runs python {fact.python_version}, below "
                   f"the declared >={check.minimum_python}",
            remedy=f"rebuild {check.venv_name} on python>={check.minimum_python}",
        ))
    for package in check.packages:
        entry = fact.packages.get(package.module)
        if entry is None:
            checks.append(RequirementCheck(
                requirement=package.requirement, kind="external_venv",
                status=RequirementStatus.UNKNOWN,
                detail=f"the venv probe returned no result for {package.module}",
            ))
            continue
        checks.append(_package_check_result(
            {**entry, "pin_ok": entry.get("version") == package.pin
             if package.pin and entry.get("version") else None},
            package,
        ))
    checks.append(RequirementCheck(
        requirement=check.requirement, kind="external_venv",
        status=RequirementStatus.SATISFIED,
        detail=f"interpreter ran at {venv_dir}",
    ))
    return checks


def _check_venv(check: VenvCheck) -> tuple[list[RequirementCheck], str | None, dict[str, Any]]:
    """Probe one external venv once; map the single child's answer to checks."""
    candidates = adapters.venv_candidates(check.venv_name, check.env_var)
    venv_dir = next((candidate for candidate in candidates
                     if adapters.venv_python(candidate) is not None), None)
    if venv_dir is None:
        return (_venv_missing_checks(check, candidates), None,
                {"candidates": [str(c) for c in candidates]})

    packages = tuple((package.module, package.distribution) for package in check.packages)
    fact = adapters.venv_fact(venv_dir, packages)

    if fact.timed_out:
        detail = (f"venv probe timed out after {adapters.VENV_TIMEOUT_S:.0f}s "
                  f"(importing {', '.join(p.module for p in check.packages)})")
        return (_venv_unverified_checks(check, str(venv_dir), detail), str(venv_dir),
                {"venv": str(venv_dir), "output_ok": False})
    if fact.error or fact.python_version is None:
        detail = f"venv probe failed: {fact.error or 'no interpreter version reported'}"
        return (_venv_unverified_checks(check, str(venv_dir), detail), str(venv_dir),
                {"venv": str(venv_dir), "output_ok": False})

    evidence = {
        "venv": str(venv_dir),
        "python": fact.python_version,
        "packages": fact.packages,
        "output_ok": True,
    }
    return _venv_answered_checks(check, venv_dir, fact), str(venv_dir), evidence


def _check_unsupported(check: UnsupportedCheck) -> RequirementCheck:
    return RequirementCheck(
        requirement=check.requirement, kind="unsupported",
        status=RequirementStatus.UNKNOWN, detail=check.reason,
    )


# ── one provider ──────────────────────────────────────────────────────────────

def probe_provider(
    provider: Provider,
    spec: ProbeSpec | None,
    *,
    checked_at: datetime,
    resolvers: dict[str, Any] | None = None,
) -> ProviderProbe:
    """Probe one provider against its spec (or report the missing spec)."""
    if spec is None:
        checks = tuple(
            RequirementCheck(
                requirement=requirement, kind="unsupported",
                status=RequirementStatus.UNKNOWN,
                detail="no probe spec is registered for this provider",
            )
            for requirement in provider.runtime_requirements
        )
        return ProviderProbe(
            provider_id=provider.provider_id,
            capability_ids=provider.capability_ids,
            probe_status=probe_status_for(checks),
            checked_at=checked_at,
            runtime_kind="unregistered",
            requirements_checked=checks,
            warnings=("no probe spec registered; runtime status is not known",),
            evidence={"reason": "no_probe_spec"},
        )

    acc = _ProbeAcc(resolvers if resolvers is not None else _resolvers())
    started = time.perf_counter()
    for check in spec.checks:
        _apply_check(check, acc)

    checks_tuple = tuple(acc.checks)
    missing = tuple(c.requirement for c in checks_tuple
                    if c.status is RequirementStatus.MISSING)
    acc.evidence["probe_duration_s"] = round(time.perf_counter() - started, 3)
    return ProviderProbe(
        provider_id=provider.provider_id,
        capability_ids=provider.capability_ids,
        probe_status=probe_status_for(checks_tuple),
        checked_at=checked_at,
        runtime_kind=spec.runtime_kind,
        executable_or_environment=acc.environment,
        version=acc.version,
        requirements_checked=checks_tuple,
        missing_requirements=missing,
        warnings=tuple(acc.warnings),
        evidence=acc.evidence,
    )


@dataclass
class _ProbeAcc:
    """Collects everything one provider's probe learns, in check order."""

    resolvers: dict[str, Any]
    checks: list[RequirementCheck] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    environment: str | None = None
    version: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


def _apply_python_version(check: PythonVersionCheck, acc: _ProbeAcc) -> None:
    acc.checks.append(_check_python_version(check))
    acc.environment = acc.environment or sys.executable
    acc.version = acc.version or adapters.platform_version()


def _apply_import(check: ImportCheck, acc: _ProbeAcc) -> None:
    result = _check_import(check)
    acc.checks.append(result)
    acc.evidence.setdefault("packages", {})[check.module] = result.status.value


def _apply_executable(check: ExecutableCheck, acc: _ProbeAcc) -> None:
    result, fact, extra_warnings = _check_executable(check, acc.resolvers)
    acc.checks.append(result)
    acc.warnings.extend(extra_warnings)
    if fact.path:
        acc.environment = acc.environment or fact.path
        acc.evidence.setdefault("executables", {})[check.resolver] = fact.path
    acc.version = acc.version or fact.version


def _apply_venv(check: VenvCheck, acc: _ProbeAcc) -> None:
    results, venv_path, venv_evidence = _check_venv(check)
    acc.checks.extend(results)
    acc.environment = acc.environment or venv_path
    acc.evidence.update(venv_evidence)
    venv_python_version = venv_evidence.get("python")
    if isinstance(venv_python_version, str):
        acc.version = acc.version or venv_python_version


def _apply_check(check, acc: _ProbeAcc) -> None:
    """Dispatch one spec check to its adapter. The union is closed."""
    if isinstance(check, PythonVersionCheck):
        _apply_python_version(check, acc)
    elif isinstance(check, ImportCheck):
        _apply_import(check, acc)
    elif isinstance(check, ExecutableCheck):
        _apply_executable(check, acc)
    elif isinstance(check, VenvCheck):
        _apply_venv(check, acc)
    else:
        acc.checks.append(_check_unsupported(check))


# ── whole registry ────────────────────────────────────────────────────────────

def probe_providers(
    registry: CapabilityRegistry | None = None,
    *,
    checked_at: datetime | None = None,
    specs: Mapping[str, ProbeSpec] | None = None,
) -> tuple[ProviderProbe, ...]:
    """Probe every declared provider; runtime truth only, no policy.

    Providers are probed in declared-ID order (the registry's own sort), so
    two reports over the same machine are comparable line by line. *specs*
    defaults to the built-in table; a caller probing a different registry
    supplies the matching table — a provider without a spec is reported
    ``UNKNOWN``, never guessed.
    """
    from ..capabilities.builtin import builtin_registry

    registry = registry or builtin_registry()
    specs = specs if specs is not None else SPECS_BY_PROVIDER
    stamp = checked_at or datetime.now(timezone.utc)
    resolvers = _resolvers()
    return tuple(
        probe_provider(provider, specs.get(provider.provider_id),
                       checked_at=stamp, resolvers=resolvers)
        for provider in registry.list_providers()
    )


def runtime_report(
    policy: ProviderPolicy | None = None,
    registry: CapabilityRegistry | None = None,
    *,
    checked_at: datetime | None = None,
    specs: Mapping[str, ProbeSpec] | None = None,
) -> RuntimeReport:
    """Probe, then join with router eligibility under *policy*.

    The join reads both layers without merging them: ``probe`` stays pure
    runtime truth, ``eligible_capabilities`` stays pure routing.
    """
    from ..capabilities.builtin import builtin_registry

    registry = registry or builtin_registry()
    policy = policy or ProviderPolicy()
    stamp = checked_at or datetime.now(timezone.utc)
    started = time.perf_counter()

    # Routing first (pure, cheap): which capabilities each provider is
    # eligible for under the policy.
    eligibility: dict[str, set[str]] = {}
    for capability in registry.list_capabilities():
        for provider in eligible_providers(capability.capability_id, policy, registry=registry):
            eligibility.setdefault(provider.provider_id, set()).add(capability.capability_id)

    entries: list[ProviderRuntimeReport] = []
    for probe in probe_providers(registry, checked_at=stamp, specs=specs):
        entries.append(ProviderRuntimeReport(
            probe=probe,
            eligible_capabilities=tuple(sorted(eligibility.get(probe.provider_id, ()))),
        ))

    summary = _summarize(entries)
    return RuntimeReport(
        generated_at=stamp,
        duration_s=round(time.perf_counter() - started, 3),
        policy=policy,
        providers=tuple(entries),
        summary=summary,
    )


def _summarize(entries: list[ProviderRuntimeReport]) -> dict[str, Any]:
    """The four legitimate states, counted without collapsing them."""
    counts = {status: 0 for status in ("AVAILABLE", "UNAVAILABLE", "DEGRADED", "UNKNOWN")}
    runnable_now: list[str] = []
    eligible_not_available: list[str] = []
    installed_not_eligible: list[str] = []
    for entry in entries:
        status = entry.probe.probe_status.value
        counts[status] = counts.get(status, 0) + 1
        eligible = bool(entry.eligible_capabilities)
        if eligible and status == "AVAILABLE":
            runnable_now.append(entry.probe.provider_id)
        elif eligible:
            eligible_not_available.append(entry.probe.provider_id)
        elif status == "AVAILABLE":
            installed_not_eligible.append(entry.probe.provider_id)
    return {
        "probe_status_counts": counts,
        "runnable_now": runnable_now,
        "eligible_not_available": eligible_not_available,
        "installed_not_eligible": installed_not_eligible,
    }
