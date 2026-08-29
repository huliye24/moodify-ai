"""MAMSE-002 conditional invocation policy (T7).

Off by default. Returns a policy suggestion, not an automatic decision;
v0.1 never forces MAMSE-002 into the canonical scan path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicySuggestion:
    invoke: bool
    reason: str
    triggers: tuple[str, ...]


def need_log_frequency(
    case_context: dict[str, Any] | None = None,
    prior_metrics: dict[str, Any] | None = None,
) -> PolicySuggestion:
    """Suggest whether this case needs log-frequency geometry.

    Candidate triggers (v0.1 policy suggestions only):
    - low-frequency ambiguous structure (low band energy spread / sub-band activity)
    - persistent narrowband cluster (low flatness with stable dominant)
    - harmonic/pitch-ratio research case
    - explicit MSE bridge request
    - manual research flag
    """
    triggers: list[str] = []
    context = case_context or {}
    metrics = prior_metrics or {}

    if context.get("research_flag") or context.get("mse_bridge_request"):
        triggers.append("explicit_research_flag_or_mse_bridge")

    if context.get("manual_research"):
        triggers.append("manual_research_flag")

    if metrics.get("persistent_narrowband_cluster"):
        triggers.append("persistent_narrowband_cluster")

    low_band = _low_band_activity(metrics)
    if low_band is not None and low_band > 0.25:
        triggers.append("low_frequency_ambiguous_structure")

    invoke = len(triggers) > 0
    return PolicySuggestion(
        invoke=invoke,
        reason="no log-frequency need indicated" if not invoke
        else f"log-frequency geometry suggested by: {', '.join(triggers)}",
        triggers=tuple(triggers),
    )


def _low_band_activity(metrics: dict[str, Any]) -> float | None:
    """Fraction of frame energy in the low band from prior metrics, if present."""
    band_key = None
    for candidate in ("band_energy_ratios", "band_ratios", "bands"):
        if candidate in metrics:
            band_key = candidate
            break
    if band_key is None:
        return None
    bands = metrics[band_key]
    if isinstance(bands, dict):
        low = bands.get("sub", 0.0) + bands.get("bass", 0.0)
        return float(low)
    return None
