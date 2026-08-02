"""Case-level learning store (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Reads/writes learning artifacts under the authoritative case directory:
02_observations / 04_interventions / 08_listening / 09_learning.
All writes are atomic (temp + rename) and hashable.
"""

from __future__ import annotations

import json
from pathlib import Path

from moodify.learning.models import (
    AuditoryObservation,
    CandidateOutcome,
    HumanListeningEvaluation,
    InterventionRecord,
    LearningRecord,
    PairwisePreference,
    RightsMetadata,
)


def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _atomic_append(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import os
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


class CaseLearningStore:
    """Persists learning-domain artifacts under one case directory."""

    def __init__(self, case_root: Path) -> None:
        self.case_root = Path(case_root)

    # -- paths ---------------------------------------------------------------

    def _observations_dir(self) -> Path:
        return self.case_root / "02_observations"

    def _interventions_dir(self) -> Path:
        return self.case_root / "04_interventions"

    def _listening_dir(self) -> Path:
        return self.case_root / "08_listening"

    def _learning_dir(self) -> Path:
        return self.case_root / "09_learning"

    # -- observations --------------------------------------------------------

    def save_observation(self, obs: AuditoryObservation) -> Path:
        p = self._observations_dir() / f"{obs.observation_id}.json"
        _atomic_write(p, obs.to_dict())
        return p

    def list_observations(self) -> list[AuditoryObservation]:
        out = []
        for p in sorted(self._observations_dir().glob("*.json")):
            out.append(AuditoryObservation.from_dict(json.loads(p.read_text(encoding="utf-8"))))
        return out

    # -- interventions -------------------------------------------------------

    def save_intervention(self, rec: InterventionRecord) -> Path:
        p = self._interventions_dir() / f"{rec.intervention_id}.json"
        _atomic_write(p, rec.to_dict())
        return p

    def list_interventions(self) -> list[InterventionRecord]:
        out = []
        for p in sorted(self._interventions_dir().glob("*.json")):
            out.append(InterventionRecord.from_dict(json.loads(p.read_text(encoding="utf-8"))))
        return out

    # -- human listening -----------------------------------------------------

    def save_evaluation(self, ev: HumanListeningEvaluation) -> Path:
        p = self._listening_dir() / f"{ev.evaluation_id}.json"
        _atomic_write(p, ev.to_dict())
        return p

    def list_evaluations(self) -> list[HumanListeningEvaluation]:
        out = []
        for p in sorted(self._listening_dir().glob("*.json")):
            out.append(HumanListeningEvaluation.from_dict(json.loads(p.read_text(encoding="utf-8"))))
        return out

    # -- learning ------------------------------------------------------------

    def save_learning_record(self, rec: LearningRecord) -> Path:
        p = self._learning_dir() / "learning_record.json"
        _atomic_write(p, rec.to_dict())
        return p

    def load_learning_record(self) -> LearningRecord | None:
        p = self._learning_dir() / "learning_record.json"
        if not p.is_file():
            return None
        return LearningRecord.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def save_rights_review(self, rights: RightsMetadata) -> Path:
        p = self._learning_dir() / "rights_review.json"
        _atomic_write(p, rights.to_dict())
        return p

    def load_rights_review(self) -> RightsMetadata | None:
        p = self._learning_dir() / "rights_review.json"
        if not p.is_file():
            return None
        return RightsMetadata.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def save_eligibility(self, eligibility: str, reasons: list[str] | None = None) -> Path:
        p = self._learning_dir() / "training_eligibility.json"
        _atomic_write(p, {
            "training_eligibility": eligibility,
            "exclusion_reasons": reasons or [],
            "schema_version": "1.0",
        })
        return p

    def append_preference(self, pref: PairwisePreference) -> None:
        _atomic_append(self._learning_dir() / "pairwise_preferences.jsonl", pref.to_dict())

    def list_preferences(self) -> list[PairwisePreference]:
        p = self._learning_dir() / "pairwise_preferences.jsonl"
        out = []
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    out.append(PairwisePreference.from_dict(json.loads(line)))
        return out

    def append_outcome(self, outcome: CandidateOutcome) -> None:
        _atomic_append(self._learning_dir() / "candidate_outcomes.jsonl", outcome.to_dict())

    def list_outcomes(self) -> list[CandidateOutcome]:
        p = self._learning_dir() / "candidate_outcomes.jsonl"
        out = []
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    out.append(CandidateOutcome.from_dict(json.loads(line)))
        return out
