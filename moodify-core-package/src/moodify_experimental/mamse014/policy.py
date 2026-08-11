"""MAMSE-014 conditional invocation policy.

Off by default. Returns a policy suggestion, never an automatic decision;
v0.1 never forces masking inference into the canonical scan path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicySuggestion:
    invoke: bool
    reason: str
    triggers: tuple[str, ...]


def need_masking_inference(
    case_context: dict[str, Any] | None = None,
    prior_metrics: dict[str, Any] | None = None,
) -> PolicySuggestion:
    """Suggest whether this case needs masking inference.

    Candidate triggers (v0.1 policy suggestions only):
    - vocal-mask or masking-competition research case
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
    if context.get("vocal_mask_research"):
        triggers.append("vocal_mask_research")
    if metrics.get("masking_suspected"):
        triggers.append("masking_suspected")

    invoke = len(triggers) > 0
    return PolicySuggestion(
        invoke=invoke,
        reason="no masking-inference need indicated" if not invoke
        else f"masking inference suggested by: {', '.join(triggers)}",
        triggers=tuple(triggers),
    )
