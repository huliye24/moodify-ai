"""Classic Reconstruction Learning Factory (MFY-CR-P07).

Turns each reconstruction run into a durable learning record:
Track -> Diagnostic -> Objective -> Candidates -> Identity Guard ->
Technical Ranking -> Human Review -> Hardware Observation -> Learning Record.

Reuses the existing Data Factory / ProductionCase / Evidence authority —
this package does NOT create a second factory. Key disciplines:
- rights/consent required, training permission defaults NO
- outcome taxonomy (GOLDEN .. FAILED), SOURCE_WINS preserved
- failures preserved with codes, never just failed += 1
- no automatic threshold updates (only PROPOSED_RULE_UPDATE records)
- serial batch, idempotent, deterministic IDs
"""

from moodify.reconstruction_factory.agreement import (
    AgreementAnalysis,
    analyze_agreement,
)
from moodify.reconstruction_factory.factory import (
    BATCH_VERSION,
    ReconstructionBatchResult,
    run_reconstruction_batch,
)
from moodify.reconstruction_factory.learning_record import (
    RECORD_VERSION,
    ReconstructionLearningRecord,
    build_learning_record,
)
from moodify.reconstruction_factory.outcome import (
    OUTCOME_TAXONOMY,
    classify_outcome,
)
from moodify.reconstruction_factory.rights import (
    RightsRecord,
    default_rights,
    validate_rights,
)

__all__ = [
    "AgreementAnalysis",
    "BATCH_VERSION",
    "OUTCOME_TAXONOMY",
    "RECORD_VERSION",
    "ReconstructionBatchResult",
    "ReconstructionLearningRecord",
    "RightsRecord",
    "analyze_agreement",
    "build_learning_record",
    "classify_outcome",
    "default_rights",
    "run_reconstruction_batch",
    "validate_rights",
]
