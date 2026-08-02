"""Learning-domain error taxonomy (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001)."""

from __future__ import annotations


class LearningError(Exception):
    code = "LEARNING_ERROR"

    def __init__(
        self,
        message: str,
        *,
        case_id: str | None = None,
        operation: str | None = None,
        recoverable: bool = False,
        cause: Exception | None = None,
    ) -> None:
        self.message = message
        self.case_id = case_id
        self.operation = operation
        self.recoverable = recoverable
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "case_id": self.case_id,
            "operation": self.operation,
            "recoverable": self.recoverable,
        }


class AuditoryObservationInvalid(LearningError):
    code = "AUDITORY_OBSERVATION_INVALID"


class InterventionRecordInvalid(LearningError):
    code = "INTERVENTION_RECORD_INVALID"


class HumanEvaluationInvalid(LearningError):
    code = "HUMAN_EVALUATION_INVALID"


class LearningRecordIncomplete(LearningError):
    code = "LEARNING_RECORD_INCOMPLETE"


class LearningRecordHashMismatch(LearningError):
    code = "LEARNING_RECORD_HASH_MISMATCH"


class LearningRecordNotReviewed(LearningError):
    code = "LEARNING_RECORD_NOT_REVIEWED"


class TrainingEligibilityUnknown(LearningError):
    code = "TRAINING_ELIGIBILITY_UNKNOWN"


class TrainingRightsNotAuthorized(LearningError):
    code = "TRAINING_RIGHTS_NOT_AUTHORIZED"


class DatasetExportIneligibleRecord(LearningError):
    code = "DATASET_EXPORT_INELIGIBLE_RECORD"


class PairwisePreferenceInvalid(LearningError):
    code = "PAIRWISE_PREFERENCE_INVALID"


class CandidateLineageInvalid(LearningError):
    code = "CANDIDATE_LINEAGE_INVALID"


class EvidenceReferenceMissing(LearningError):
    code = "EVIDENCE_REFERENCE_MISSING"


class LegacyCapabilityUnclassified(LearningError):
    code = "LEGACY_CAPABILITY_UNCLASSIFIED"


class ArchitectureMigrationConflict(LearningError):
    code = "ARCHITECTURE_MIGRATION_CONFLICT"
