"""Preregistered protocol (MFY_MOBILE_LISTENING_VALIDATION_001).

The protocol, samples and endpoints are frozen and hashed BEFORE any
listening session runs. Candidate algorithms/thresholds from 71 are frozen —
this package never changes them. Missing the threshold means returning to 71,
never lowering the threshold.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace

PROTOCOL_VERSION = "mfy-listening-protocol-v1"

LEVEL_MATCH_DB_MAX = 0.5      # A/B loudness difference must stay within this
SWITCH_LATENCY_MS_MAX = 100.0  # A/B switching latency threshold
ALPHA = 0.05                  # significance threshold for the main endpoint
MIN_SESSIONS_PER_STRATUM = 3  # floor for a stratum to be reported

# Frozen 71 candidates (never changed by this package)
CANDIDATE_PRIMITIVES = ("dc_offset_fix", "clip_peak_repair")
CANDIDATE_VERSION = "mfy-intervention-v1"


@dataclass(frozen=True)
class Stratum:
    era: str          # old_record / modern_master
    source_quality: str  # degraded / clean
    music_type: str   # e.g. "synthetic_fixture" (device audio sources later)
    device_route: str  # SPEAKER / WIRED_USB / BLUETOOTH_A2DP (device evidence)
    listening_env: str  # e.g. "quiet_room" / "uncontrolled"


@dataclass(frozen=True)
class Sample:
    sample_id: str
    kind: str  # legitimate / negative_control / placebo_bypass
    input_wav: str
    processed_wav: str | None  # None for placebo (bypassed path replayed)
    expected_decision: str  # SELECTED / BYPASSED


@dataclass(frozen=True)
class ListeningProtocol:
    version: str = PROTOCOL_VERSION
    candidates_frozen: str = CANDIDATE_VERSION
    primitives: tuple[str, ...] = CANDIDATE_PRIMITIVES
    level_match_db_max: float = LEVEL_MATCH_DB_MAX
    switch_latency_ms_max: float = SWITCH_LATENCY_MS_MAX
    alpha: float = ALPHA
    min_sessions_per_stratum: int = MIN_SESSIONS_PER_STRATUM
    # Endpoints are reported SEPARATELY, never merged into a mystery score.
    endpoints: tuple[str, ...] = ("preference", "identity_kept", "difference_audible")
    strata: tuple[Stratum, ...] = ()
    samples: tuple[Sample, ...] = ()
    frozen_sha256: str = ""  # filled by freeze_protocol


def build_default_protocol() -> ListeningProtocol:
    """Pre-registered default: negative control + placebo + legitimate cases."""
    strata = (
        Stratum("old_record", "degraded", "synthetic_fixture", "SPEAKER", "quiet_room"),
        Stratum("modern_master", "clean", "synthetic_fixture", "SPEAKER", "quiet_room"),
    )
    samples = (
        # legitimate: DC + clip case (71) -> both primitives selected
        Sample("legit_dc_clip_01", "legitimate", "legit_dc_clip_01.wav", "legit_dc_clip_01_processed.wav", "SELECTED"),
        # negative control: modern clean mix -> nothing selected (bypass)
        Sample("negative_control_01", "negative_control", "negative_control_01.wav", "negative_control_01_processed.wav", "BYPASSED"),
        # placebo: legitimate input replayed with NO processing (bypass placebo)
        Sample("placebo_bypass_01", "placebo_bypass", "legit_dc_clip_01.wav", None, "BYPASSED"),
    )
    return ListeningProtocol(strata=strata, samples=samples)


def freeze_protocol(protocol: ListeningProtocol) -> ListeningProtocol:
    """Freeze and hash the protocol (deterministic; same protocol -> same hash)."""
    return replace(protocol, frozen_sha256=hash_protocol(protocol))


def hash_protocol(protocol: ListeningProtocol) -> str:
    """Deterministic SHA-256 of the protocol payload (samples + strata + thresholds)."""
    payload = {
        "version": protocol.version,
        "candidates_frozen": protocol.candidates_frozen,
        "primitives": list(protocol.primitives),
        "level_match_db_max": protocol.level_match_db_max,
        "switch_latency_ms_max": protocol.switch_latency_ms_max,
        "alpha": protocol.alpha,
        "endpoints": list(protocol.endpoints),
        "strata": [asdict(s) for s in protocol.strata],
        "samples": [asdict(s) for s in protocol.samples],
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def protocol_to_json(protocol: ListeningProtocol) -> dict[str, object]:
    return asdict(protocol)
