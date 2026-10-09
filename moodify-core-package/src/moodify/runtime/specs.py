"""How each declared provider is probed — explicit, static, reviewable.

This is the only place that maps a provider declaration to probe steps. It is
deliberately a hand-written table rather than something derived by parsing
``runtime_requirements`` strings at runtime: the declarations are prose for
humans, and a parser that guessed their meaning would be exactly the kind of
invented semantics this repository refuses. What is mechanically checked is
the *coverage*: a test asserts that every built-in provider has a spec, and
that each spec's requirement strings are exactly the provider's declared
requirements, verbatim and in order.

Two known declaration-vs-implementation drifts are **not** repaired here —
they are recorded in ``docs/development/THINKPAD_RUNTIME_CAPABILITY_PROBE.md``
and raised as cross-lane requests, because aligning them is a mainline
decision:

* ``moodify.preview_separation`` declares ``.venv-basic-pitch`` but the
  desktop shell now launches ``dsp_separate.py`` on its ``audio`` runtime
  (``.venv-audio``, which this machine does not have);
* ``music21.local`` declares ``.venv-score`` but the desktop shell resolves
  its ``score`` runtime to ``.venv-basic-pitch``.

The probe verifies what is declared. When the declaration and the
implementation disagree, the disagreement is the finding.
"""

from __future__ import annotations

from dataclasses import dataclass

# ── check kinds ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PythonVersionCheck:
    """``python>=X.Y`` against an interpreter (in-process by default)."""

    requirement: str
    minimum: str


@dataclass(frozen=True)
class ImportCheck:
    """A python package: existence is not enough — it must import."""

    requirement: str
    module: str
    distribution: str | None
    pin: str | None


def import_check(requirement: str, *, module: str | None = None) -> ImportCheck:
    """Build an :class:`ImportCheck` from the declared requirement string.

    ``"numpy"`` → module ``numpy``; ``"basic-pitch==0.4.0"`` → module
    ``basic_pitch`` with pin ``0.4.0``. ``module`` may override the derived
    module name when the import name is not the hyphen-to-underscore form.
    """
    distribution, _, pinned = requirement.partition("==")
    distribution = distribution.strip()
    derived = module or distribution.replace("-", "_")
    return ImportCheck(
        requirement=requirement,
        module=derived,
        distribution=distribution or None,
        pin=pinned.strip() or None,
    )


@dataclass(frozen=True)
class ExecutableCheck:
    """A system binary resolved through the runtime's own resolver."""

    requirement: str
    resolver: str
    """``"ffmpeg"`` or ``"ffprobe"`` — key into the canonical resolver table in
    the service (which reuses ``moodify.auditory.decode``'s memoized
    resolution, the same code the processing runtime uses)."""


@dataclass(frozen=True)
class VenvCheck:
    """An external venv, verified through its own interpreter.

    The venv requirement is satisfied only when the interpreter runs AND the
    listed packages import inside it. A directory that exists is not a
    runtime.
    """

    requirement: str
    venv_name: str
    env_var: str
    python_requirement: str
    minimum_python: str
    packages: tuple[ImportCheck, ...]


@dataclass(frozen=True)
class UnsupportedCheck:
    """A requirement this probe deliberately refuses to verify.

    Produces ``UNKNOWN`` with the reason attached — never ``SATISFIED``.
    """

    requirement: str
    reason: str


ProbeCheck = PythonVersionCheck | ImportCheck | ExecutableCheck | VenvCheck | UnsupportedCheck


@dataclass(frozen=True)
class ProbeSpec:
    provider_id: str
    runtime_kind: str
    checks: tuple[ProbeCheck, ...]


# ── the table ─────────────────────────────────────────────────────────────────
#
# One entry per provider declared in ``moodify.capabilities.builtin``. The
# requirement strings below are the declaration's strings, verbatim.

_PROVIDER_SPECS: tuple[ProbeSpec, ...] = (
    ProbeSpec(
        "moodify.auditory",
        "python_in_process",
        (
            PythonVersionCheck("python>=3.10", minimum="3.10"),
            import_check("numpy"),
            import_check("scipy"),
            import_check("librosa"),
            import_check("soundfile"),
        ),
    ),
    ProbeSpec(
        "moodify.intervention",
        "python_in_process",
        (
            PythonVersionCheck("python>=3.10", minimum="3.10"),
            import_check("numpy"),
        ),
    ),
    ProbeSpec(
        "moodify.mix_graph",
        "python_in_process",
        (
            PythonVersionCheck("python>=3.10", minimum="3.10"),
            import_check("pedalboard"),
            import_check("numpy"),
            import_check("scipy"),
        ),
    ),
    ProbeSpec(
        "moodify.release",
        "python_in_process",
        (
            PythonVersionCheck("python>=3.10", minimum="3.10"),
            import_check("soundfile"),
        ),
    ),
    ProbeSpec(
        "moodify.preview_separation",
        "external_venv",
        (
            VenvCheck(
                requirement="external venv .venv-basic-pitch",
                venv_name=".venv-basic-pitch",
                env_var="MOODIFY_VENV_BASIC_PITCH",
                python_requirement="python>=3.10",
                minimum_python="3.10",
                packages=(import_check("librosa"), import_check("soundfile")),
            ),
        ),
    ),
    ProbeSpec(
        "ffmpeg.system",
        "system_binary",
        (
            ExecutableCheck("ffmpeg", resolver="ffmpeg"),
            ExecutableCheck("ffprobe", resolver="ffprobe"),
        ),
    ),
    ProbeSpec(
        "lalal.cloud",
        "remote_service",
        (
            UnsupportedCheck(
                "network",
                "the local runtime probe never touches the network; whether "
                "LALAL.AI is reachable from this machine is not verified here",
            ),
            UnsupportedCheck(
                "LALAL.AI API key",
                "credential probing is out of scope: a present key would still "
                "not be verified without a network call",
            ),
        ),
    ),
    ProbeSpec(
        "basic_pitch.local",
        "external_venv",
        (
            VenvCheck(
                requirement="external venv .venv-basic-pitch",
                venv_name=".venv-basic-pitch",
                env_var="MOODIFY_VENV_BASIC_PITCH",
                python_requirement="python>=3.10",
                minimum_python="3.10",
                packages=(import_check("basic-pitch==0.4.0"),),
            ),
        ),
    ),
    ProbeSpec(
        "music21.local",
        "external_venv",
        (
            VenvCheck(
                requirement="external venv .venv-score",
                venv_name=".venv-score",
                env_var="MOODIFY_VENV_SCORE",
                python_requirement="python>=3.10",
                minimum_python="3.10",
                packages=(import_check("music21"),),
            ),
        ),
    ),
)

#: provider_id → spec. Sorted-by-provider construction; lookup is exact.
SPECS_BY_PROVIDER: dict[str, ProbeSpec] = {spec.provider_id: spec for spec in _PROVIDER_SPECS}


def spec_for(provider_id: str) -> ProbeSpec | None:
    return SPECS_BY_PROVIDER.get(provider_id)


def requirement_strings(spec: ProbeSpec) -> tuple[str, ...]:
    """The spec's requirement strings in probe order (used by the coverage test)."""
    out: list[str] = []
    for check in spec.checks:
        if isinstance(check, VenvCheck):
            out.append(check.python_requirement)
            out.extend(package.requirement for package in check.packages)
            out.append(check.requirement)
        else:
            out.append(check.requirement)
    return tuple(out)


__all__ = [
    "ExecutableCheck",
    "ImportCheck",
    "ProbeCheck",
    "ProbeSpec",
    "PythonVersionCheck",
    "SPECS_BY_PROVIDER",
    "UnsupportedCheck",
    "VenvCheck",
    "import_check",
    "requirement_strings",
    "spec_for",
]
