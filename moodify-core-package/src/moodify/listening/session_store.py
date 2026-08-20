"""Session recording (MFY_MOBILE_LISTENING_VALIDATION_001).

Every human judgment must record reviewer, scope, time, device route and
evidence reference. DeepSeek never fabricates judgments; this store only
persists what a human (or the authorised runner) actually submitted.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    trial_id: str
    sample_id: str
    reviewer: str
    scope: str  # e.g. "blind_ab_speaker_quiet_room"
    device_route: str  # SPEAKER / WIRED_USB / BLUETOOTH_A2DP
    listening_env: str
    time_utc: str
    evidence_ref: str  # path to session JSON (audio hashes, order, labels)
    judgments: dict[str, bool]  # {"prefer_moodify": true, "identity_kept": true, "difference_audible": true}


def record_session(
    session_id: str,
    trial_id: str,
    sample_id: str,
    reviewer: str,
    scope: str,
    device_route: str,
    listening_env: str,
    evidence_ref: str,
    judgments: dict[str, bool],
) -> SessionRecord:
    """Persist one human judgment record (never auto-fill judgments)."""
    rec = SessionRecord(
        session_id=session_id,
        trial_id=trial_id,
        sample_id=sample_id,
        reviewer=reviewer,
        scope=scope,
        device_route=device_route,
        listening_env=listening_env,
        time_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        evidence_ref=evidence_ref,
        judgments=judgments,
    )
    return rec


def session_to_json(rec: SessionRecord) -> dict[str, object]:
    return asdict(rec)


def load_sessions_json(path: str) -> list[SessionRecord]:
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)
    return [SessionRecord(**r) for r in rows]


def save_sessions_json(path: str, records: list[SessionRecord]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([session_to_json(r) for r in records], fh, ensure_ascii=False, indent=2)
        fh.write("\n")
