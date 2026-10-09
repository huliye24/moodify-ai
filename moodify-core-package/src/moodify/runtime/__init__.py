"""Runtime capability probe — "can this machine run the declared provider now?"

This package is the third layer, between the pure router and actual execution::

    DECLARATION  what the project says a provider requires   (moodify.capabilities)
    ROUTING      which declared provider is eligible         (moodify.capabilities.router)
    PROBING      whether the provider can run here right now (this package)
    EXECUTION    actually running it                         (not built)

The router is deliberately a pure decision layer and stays one: nothing here
modifies it. This layer *calls* the router (never the other way around) and
answers the question the router refuses to ask — whether the python
environment, executables, model runtimes and external venvs are really usable
on this computer.

What a probe proves, and what it does not::

    basic_pitch imports in its venv  ≠  transcription quality is good
    ffmpeg answers -version          ≠  a render will succeed

Runtime availability is not artistic or scientific validation. ``AVAILABLE``
means the declared requirements were verified present and usable on this
machine at ``checked_at`` — nothing more, and the report says so.

Two answers are exported:

* :func:`probe_providers` — runtime truth only, policy-free;
* :func:`runtime_report` — that truth joined with router eligibility, which
  makes the four legitimate states (eligible/installed × available/not)
  readable without collapsing the layers that produced them.
"""

from .models import (
    RUNTIME_PROBE_SCHEMA,
    ProbeStatus,
    ProviderProbe,
    ProviderRuntimeReport,
    RequirementCheck,
    RequirementStatus,
    RuntimeReport,
    probe_status_for,
)
from .service import probe_provider, probe_providers, runtime_report
from .specs import SPECS_BY_PROVIDER, ProbeSpec, spec_for

__all__ = [
    "RUNTIME_PROBE_SCHEMA",
    "SPECS_BY_PROVIDER",
    "ProbeSpec",
    "ProbeStatus",
    "ProviderProbe",
    "ProviderRuntimeReport",
    "RequirementCheck",
    "RequirementStatus",
    "RuntimeReport",
    "probe_provider",
    "probe_providers",
    "probe_status_for",
    "runtime_report",
    "spec_for",
]
