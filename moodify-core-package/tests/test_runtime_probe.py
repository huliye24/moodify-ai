"""Runtime Capability Probe 0.1 — bounded probes and honest states.

The properties these tests protect:

* the router stays pure — the probe layer calls it, never the reverse;
* no check may claim more than it verified (a file that exists is not a
  runtime; an unverified requirement is never SATISFIED);
* every subprocess is bounded (timeout, captured output, closed stdin);
* nothing here touches the network or downloads a model;
* two probe runs are two runs — there is no hidden cache to go stale.

Tests that need a definitive negative or a timeout use monkeypatched
adapters; tests marked as machine verification run the real probe and skip
when the underlying runtime is absent (CI has no external venvs).
"""

from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from moodify.capabilities import (
    Capability,
    CapabilityRegistry,
    CapabilityStatus,
    Determinism,
    ExecutionMode,
    FailureCode,
    IOType,
    Locality,
    Provider,
    ProviderStatus,
    ProviderType,
    StrategicPosture,
    builtin_registry,
    get_provider,
)
from moodify.runtime import service as probe_service
from moodify.runtime import (
    ProbeStatus,
    RequirementStatus,
    probe_provider,
    probe_providers,
    runtime_report,
)
from moodify.runtime import adapters
from moodify.runtime.specs import (
    SPECS_BY_PROVIDER,
    ExecutableCheck,
    ProbeSpec,
    PythonVersionCheck,
    UnsupportedCheck,
    VenvCheck,
    import_check,
    requirement_strings,
    spec_for,
)

STAMP = datetime(2026, 10, 9, 12, 0, 0, tzinfo=timezone.utc)
STAMP_LATER = STAMP + timedelta(hours=1)

CAP = "audio.analyze"


# ── synthetic registry helpers (mirrors test_provider_router's style) ─────────

def _cap(capability_id: str, provider_ids=()):
    return Capability(
        capability_id=capability_id, title="T", description="D",
        domain=capability_id.split(".", 1)[0],
        status=CapabilityStatus.CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO,), output_types=(IOType.REPORT,),
        failure_codes=(FailureCode.EXECUTION_FAILED,),
        provider_ids=tuple(provider_ids),
        locality=Locality.LOCAL, determinism=Determinism.DETERMINISTIC,
    )


def _prov(provider_id: str, capability_ids, *, runtime_requirements=(),
          status=ProviderStatus.ACTIVE, **over):
    payload = dict(
        provider_id=provider_id, name=provider_id,
        provider_type=ProviderType.LIBRARY,
        capability_ids=tuple(capability_ids),
        execution_mode=ExecutionMode.LOCAL, status=status,
        code_license="MIT",
        runtime_requirements=tuple(runtime_requirements),
    )
    payload.update(over)
    return Provider(**payload)


def _registry(provider: Provider, capability_id: str = CAP) -> CapabilityRegistry:
    return CapabilityRegistry(
        [_cap(capability_id, provider_ids=(provider.provider_id,))], [provider])


def _in_process_spec(provider_id: str, *requirements: str) -> ProbeSpec:
    checks: list = []
    for requirement in requirements:
        if requirement.startswith("python>="):
            checks.append(PythonVersionCheck(requirement, minimum="3.10"))
        else:
            checks.append(import_check(requirement))
    return ProbeSpec(provider_id, "python_in_process", tuple(checks))


def _check(probe, requirement: str):
    return next(c for c in probe.requirements_checked if c.requirement == requirement)


def _venv_requirements(check: VenvCheck) -> tuple[str, ...]:
    """The venv's requirements in probe order (what a spec must declare)."""
    return ((check.python_requirement,)
            + tuple(package.requirement for package in check.packages)
            + (check.requirement,))


# ── A. executable probes ──────────────────────────────────────────────────────

def test_real_ffmpeg_and_ffprobe_are_available_on_this_machine():
    """Machine verification: the real resolvers, the real binaries."""
    from moodify.auditory.decode import FfmpegNotFound, _which_ffmpeg

    try:
        _which_ffmpeg()
    except FfmpegNotFound:
        pytest.skip("ffmpeg is not installed on this machine")

    probe = probe_provider(get_provider("ffmpeg.system"),
                           spec_for("ffmpeg.system"), checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.AVAILABLE
    assert probe.version and "ffmpeg" in probe.version.lower()
    assert _check(probe, "ffprobe").status is RequirementStatus.SATISFIED


def test_missing_executable_is_unavailable_and_names_the_fix(monkeypatch):
    from moodify.auditory.decode import FfmpegNotFound

    def missing():
        raise FfmpegNotFound("ffmpeg not found on PATH")

    monkeypatch.setattr("moodify.auditory.decode._which_ffmpeg", missing)
    monkeypatch.setattr("moodify.auditory.decode._which_ffprobe", missing)

    probe = probe_provider(get_provider("ffmpeg.system"),
                           spec_for("ffmpeg.system"), checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNAVAILABLE
    assert probe.missing_requirements == ("ffmpeg", "ffprobe")
    assert "install ffmpeg" in _check(probe, "ffmpeg").remedy


def test_executable_timeout_is_unknown_not_missing(monkeypatch):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(adapters.subprocess, "run", timed_out)
    result, fact, _warnings = probe_service._check_executable(
        ExecutableCheck("ffmpeg", resolver="ffmpeg"),
        {"ffmpeg": lambda: "fake-ffmpeg"})
    assert fact.timed_out and result.status is RequirementStatus.UNKNOWN
    assert "did not answer" in result.detail


def test_unparseable_version_output_is_satisfied_with_a_warning(monkeypatch):
    monkeypatch.setattr(
        adapters.subprocess, "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""))

    result, fact, warnings = probe_service._check_executable(
        ExecutableCheck("ffmpeg", resolver="ffmpeg"),
        {"ffmpeg": lambda: "fake-ffmpeg"})
    assert fact.ran and result.status is RequirementStatus.SATISFIED
    assert warnings and "no parseable output" in warnings[0]


# ── B. in-process import probes ───────────────────────────────────────────────

def test_importable_package_is_available():
    provider = _prov("probe.numpy", (CAP,), runtime_requirements=("python>=3.10", "numpy"))
    probe = probe_provider(provider, _in_process_spec("probe.numpy", "python>=3.10", "numpy"),
                           checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.AVAILABLE
    assert _check(probe, "numpy").status is RequirementStatus.SATISFIED


def test_missing_module_is_unavailable_with_a_remedy():
    provider = _prov("probe.missing", (CAP,),
                     runtime_requirements=("moodify.definitely_not_a_module",))
    probe = probe_provider(
        provider, _in_process_spec("probe.missing", "moodify.definitely_not_a_module"),
        checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNAVAILABLE
    assert probe.missing_requirements == ("moodify.definitely_not_a_module",)
    assert "install" in _check(probe, "moodify.definitely_not_a_module").remedy


def test_version_mismatch_degrades_rather_than_denies():
    """A present-but-different version is not absence — it is DEGRADED."""
    requirement = "numpy==0.0.1"
    provider = _prov("probe.pin", (CAP,), runtime_requirements=(requirement,))
    probe = probe_provider(provider, _in_process_spec("probe.pin", requirement),
                           checked_at=STAMP)
    check = _check(probe, requirement)
    assert check.status is RequirementStatus.MISMATCH
    assert probe.probe_status is ProbeStatus.DEGRADED
    assert "0.0.1" in check.detail


def test_matching_pin_is_satisfied():
    import importlib.metadata

    installed = importlib.metadata.version("numpy")
    requirement = f"numpy=={installed}"
    provider = _prov("probe.pin_ok", (CAP,), runtime_requirements=(requirement,))
    probe = probe_provider(provider, _in_process_spec("probe.pin_ok", requirement),
                           checked_at=STAMP)
    assert _check(probe, requirement).status is RequirementStatus.SATISFIED
    assert probe.probe_status is ProbeStatus.AVAILABLE


def test_python_version_is_compared_numerically_not_lexically():
    assert adapters.version_at_least("3.10.10", "3.10")
    assert not adapters.version_at_least("3.9.19", "3.10")
    assert adapters.version_at_least("3.10", "3.9")  # lexical order would say the opposite

    satisfied = probe_service._check_python_version(
        PythonVersionCheck("python>=3.10", minimum="3.10"))
    assert satisfied.status in (RequirementStatus.SATISFIED, RequirementStatus.MISSING)
    # whatever this interpreter is, the check must mirror its own version
    if satisfied.status is RequirementStatus.SATISFIED:
        assert sys.version_info[:2] >= (3, 10)
    unmet = probe_service._check_python_version(
        PythonVersionCheck("python>=3.99", minimum="3.99"))
    assert unmet.status is RequirementStatus.MISSING
    assert "3.99" in unmet.detail and unmet.remedy


# ── C. external venv probes ───────────────────────────────────────────────────

def test_venv_timeout_is_unknown_not_unavailable(monkeypatch):
    monkeypatch.setattr(adapters, "venv_python", lambda venv: Path("fake-python"))
    monkeypatch.setattr(
        adapters, "venv_fact",
        lambda venv, packages, **kw: adapters.VenvFact(
            environment=str(venv), timed_out=True))

    check = VenvCheck("external venv .venv-x", ".venv-x", "MOODIFY_VENV_X",
                      "python>=3.10", "3.10", (import_check("music21"),))
    provider = _prov("probe.venv_timeout", (CAP,),
                     runtime_requirements=_venv_requirements(check))
    probe = probe_provider(provider, ProbeSpec("probe.venv_timeout", "external_venv", (check,)),
                           checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNKNOWN
    assert all(c.status is RequirementStatus.UNKNOWN for c in probe.requirements_checked)
    assert "timed out" in _check(probe, "python>=3.10").detail


def test_venv_present_but_import_broken_is_unavailable(monkeypatch):
    monkeypatch.setattr(adapters, "venv_python", lambda venv: Path("fake-python"))
    monkeypatch.setattr(
        adapters, "venv_fact",
        lambda venv, packages, **kw: adapters.VenvFact(
            environment=str(venv), python_version="3.10.10",
            packages={"music21": {"ok": False, "version": None,
                                  "error": "ValueError: numpy.dtype size changed"}}))

    check = VenvCheck("external venv .venv-x", ".venv-x", "MOODIFY_VENV_X",
                      "python>=3.10", "3.10", (import_check("music21"),))
    provider = _prov("probe.venv_broken", (CAP,),
                     runtime_requirements=_venv_requirements(check))
    probe = probe_provider(provider, ProbeSpec("probe.venv_broken", "external_venv", (check,)),
                           checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNAVAILABLE
    assert _check(probe, "music21").status is RequirementStatus.MISSING
    assert "numpy.dtype size changed" in _check(probe, "music21").detail
    # the venv itself ran — only the import inside it failed
    assert _check(probe, "external venv .venv-x").status is RequirementStatus.SATISFIED


def test_absent_venv_is_missing_for_every_requirement_it_backs(monkeypatch):
    monkeypatch.delenv("MOODIFY_VENV_PROBE_ABSENT", raising=False)
    check = VenvCheck("external venv .venv-probe-absent-xyz", ".venv-probe-absent-xyz",
                      "MOODIFY_VENV_PROBE_ABSENT", "python>=3.10", "3.10",
                      (import_check("music21"),))
    provider = _prov("probe.venv_absent", (CAP,),
                     runtime_requirements=_venv_requirements(check))
    probe = probe_provider(provider, ProbeSpec("probe.venv_absent", "external_venv", (check,)),
                           checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNAVAILABLE
    assert len(probe.missing_requirements) == 3
    assert "MOODIFY_VENV_PROBE_ABSENT" in _check(probe, "python>=3.10").remedy


def test_real_basic_pitch_venv_is_available_when_present():
    """Machine verification: the real external venv, the real import."""
    candidates = adapters.venv_candidates(".venv-basic-pitch", "MOODIFY_VENV_BASIC_PITCH")
    if not any(adapters.venv_python(candidate) for candidate in candidates):
        pytest.skip("basic-pitch venv is not present on this machine")

    probe = probe_provider(get_provider("basic_pitch.local"),
                           spec_for("basic_pitch.local"), checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.AVAILABLE
    check = _check(probe, "basic-pitch==0.4.0")
    assert check.status is RequirementStatus.SATISFIED
    assert "0.4.0" in check.detail


# ── D. unsupported and unregistered ───────────────────────────────────────────

def test_unsupported_requirement_is_unknown_with_the_reason():
    provider = _prov("probe.remote", (CAP,), runtime_requirements=("network",),
                     execution_mode=ExecutionMode.CLOUD)
    spec = ProbeSpec("probe.remote", "remote_service",
                     (UnsupportedCheck("network", "never touches the network"),))
    probe = probe_provider(provider, spec, checked_at=STAMP)
    assert probe.probe_status is ProbeStatus.UNKNOWN
    check = _check(probe, "network")
    assert check.status is RequirementStatus.UNKNOWN
    assert "never touches the network" in check.detail


def test_provider_without_a_spec_is_unknown_not_guessed():
    provider = _prov("probe.specless", (CAP,), runtime_requirements=("something",))
    registry = _registry(provider)
    probes = probe_providers(registry, checked_at=STAMP, specs={})
    assert probes[0].probe_status is ProbeStatus.UNKNOWN
    assert probes[0].runtime_kind == "unregistered"
    assert probes[0].warnings
    assert _check(probes[0], "something").status is RequirementStatus.UNKNOWN


# ── E. the policy join — the four legitimate states ───────────────────────────

def test_eligible_but_unavailable_is_reported_as_such():
    provider = _prov("probe.eligible_missing", (CAP,),
                     runtime_requirements=("moodify.definitely_not_a_module",))
    registry = _registry(provider)
    report = runtime_report(registry=registry, checked_at=STAMP,
                            specs={"probe.eligible_missing": _in_process_spec(
                                "probe.eligible_missing", "moodify.definitely_not_a_module")})
    entry = report.providers[0]
    assert entry.eligible_capabilities == (CAP,)  # router says eligible
    assert entry.probe.probe_status is ProbeStatus.UNAVAILABLE
    assert report.summary["eligible_not_available"] == ("probe.eligible_missing",)


def test_installed_but_policy_ineligible_is_reported_as_such():
    provider = _prov("probe.installed_ineligible", (CAP,),
                     runtime_requirements=("numpy",),
                     status=ProviderStatus.EXPERIMENTAL)  # no opt-in by default
    registry = _registry(provider)
    report = runtime_report(registry=registry, checked_at=STAMP,
                            specs={"probe.installed_ineligible": _in_process_spec(
                                "probe.installed_ineligible", "numpy")})
    entry = report.providers[0]
    assert entry.eligible_capabilities == ()
    assert entry.probe.probe_status is ProbeStatus.AVAILABLE
    assert report.summary["installed_not_eligible"] == ("probe.installed_ineligible",)


def test_eligible_and_available_is_runnable_now():
    provider = _prov("probe.ready", (CAP,), runtime_requirements=("numpy",))
    registry = _registry(provider)
    report = runtime_report(registry=registry, checked_at=STAMP,
                            specs={"probe.ready": _in_process_spec("probe.ready", "numpy")})
    assert report.summary["runnable_now"] == ("probe.ready",)


# ── F. fresh runs, determinism, and the registry's purity ────────────────────

def test_two_probe_runs_are_two_runs_no_hidden_cache(monkeypatch):
    real_import_fact = adapters.import_fact
    calls: list[str] = []

    def counting(module, distribution, pin):
        calls.append(module)
        return real_import_fact(module, distribution, pin)

    monkeypatch.setattr(adapters, "import_fact", counting)
    first = probe_providers(checked_at=STAMP)
    after_first = len(calls)
    second = probe_providers(checked_at=STAMP_LATER)

    assert after_first > 0
    assert len(calls) == 2 * after_first  # every adapter ran again
    assert {probe.checked_at for probe in first} == {STAMP}
    assert {probe.checked_at for probe in second} == {STAMP_LATER}


def test_normalized_output_is_deterministic():
    provider = _prov("probe.det", (CAP,), runtime_requirements=("numpy",))
    registry = _registry(provider)
    specs = {"probe.det": _in_process_spec("probe.det", "numpy")}

    def normalized(stamp):
        report = runtime_report(registry=registry, checked_at=stamp, specs=specs)
        payload = report.model_dump(mode="json")
        payload.pop("generated_at")
        payload.pop("duration_s")
        for entry in payload["providers"]:
            entry["probe"].pop("checked_at")
            entry["probe"]["evidence"].pop("probe_duration_s", None)
        return json.dumps(payload, sort_keys=True, ensure_ascii=False)

    assert normalized(STAMP) == normalized(STAMP_LATER)


def test_probing_does_not_mutate_the_registry():
    provider = _prov("probe.snapshot", (CAP,), runtime_requirements=("numpy",))
    registry = _registry(provider)
    before = registry.snapshot_json()
    probe_providers(registry, checked_at=STAMP,
                    specs={"probe.snapshot": _in_process_spec("probe.snapshot", "numpy")})
    assert registry.snapshot_json() == before


def test_the_capability_layer_never_references_the_probe():
    """The dependency direction is one-way: runtime → capabilities."""
    import moodify.capabilities.builtin as builtin
    import moodify.capabilities.models as models
    import moodify.capabilities.policy as policy
    import moodify.capabilities.registry as registry_mod
    import moodify.capabilities.router as router

    for module in (builtin, models, policy, registry_mod, router):
        source = inspect.getsource(module)
        assert "moodify.runtime" not in source, module.__name__
        assert "from ..runtime" not in source, module.__name__


def test_importing_capabilities_does_not_import_the_probe():
    src = Path(__file__).resolve().parents[1] / "src"
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": str(src)}
    code = ("import moodify.capabilities, sys; "
            "assert 'moodify.runtime' not in sys.modules, sorted(sys.modules); "
            "print('clean')")
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, env=env, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "clean" in proc.stdout


# ── G. specs vs declarations, and process hygiene ─────────────────────────────

def test_every_builtin_provider_has_a_spec_matching_its_declaration():
    """The probe table covers the registry exactly — verbatim, in order.

    Adding a provider without a spec (or editing a declaration without its
    spec) fails here, so "probed" and "declared" cannot drift apart silently.
    """
    registry = builtin_registry()
    declared = {provider.provider_id for provider in registry.list_providers()}
    assert set(SPECS_BY_PROVIDER) == declared
    for provider in registry.list_providers():
        spec = SPECS_BY_PROVIDER[provider.provider_id]
        assert requirement_strings(spec) == provider.runtime_requirements, provider.provider_id


def test_every_subprocess_call_is_bounded_and_captured(monkeypatch):
    calls: list[tuple] = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0,
                               stdout=json.dumps({"python": "3.10.10", "packages": []}),
                               stderr="")

    monkeypatch.setattr(adapters.subprocess, "run", fake_run)
    monkeypatch.setattr(adapters, "venv_python", lambda venv: Path("fake-python"))

    adapters.executable_fact(lambda: "fake-executable")
    adapters.venv_fact(Path("fake-venv"), (("music21", "music21"),))

    assert len(calls) == 2
    for args, kwargs in calls:
        assert isinstance(args, list)  # argument arrays only, never shell strings
        assert kwargs.get("timeout"), "every subprocess needs an explicit timeout"
        assert kwargs.get("capture_output") is True
        assert kwargs.get("stdin") is subprocess.DEVNULL
        assert "shell" not in kwargs or kwargs["shell"] is False


def test_probe_subprocesses_receive_the_utf8_environment(monkeypatch):
    captured: dict = {}

    def fake_run(args, **kwargs):
        captured.update(kwargs.get("env") or {})
        return SimpleNamespace(returncode=0,
                               stdout=json.dumps({"python": "3.10.10", "packages": []}),
                               stderr="")

    monkeypatch.setattr(adapters.subprocess, "run", fake_run)
    monkeypatch.setattr(adapters, "venv_python", lambda venv: Path("fake-python"))
    adapters.venv_fact(Path("fake-venv"), (("music21", "music21"),))

    assert captured.get("PYTHONUTF8") == "1"  # the GBK console trap
    assert captured.get("PYTHONIOENCODING") == "utf-8"


def test_local_probes_never_touch_the_network_or_download(monkeypatch):
    """No socket may be opened by in-process probing, and the venv child is a
    fixed import-only script with no network modules in it."""
    def no_sockets(*args, **kwargs):
        raise AssertionError("the runtime probe must not open a socket")

    monkeypatch.setattr("socket.socket", no_sockets)
    for token in ("socket", "urllib", "http", "requests", "subprocess"):
        assert token not in adapters._VENV_PROBE_SCRIPT, token
    probes = probe_providers(checked_at=STAMP)  # real probe, real machine
    assert probes  # completed without touching the network
