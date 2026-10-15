"""Research-provider catalog for HEAR/Judge baselines.

Entries describe evaluation intent and known licensing gates.  They do not
install, download, approve, or execute third-party code or weights.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


UseClass = Literal["RESEARCH_ONLY", "EVALUATION_ONLY", "CANDIDATE", "REFERENCE"]


@dataclass(frozen=True)
class ProviderCandidate:
    provider_id: str
    capability: str
    use_class: UseClass
    code_license: str
    weights_or_data_license: str
    production_gate: str
    source_uri: str


CATALOG: tuple[ProviderCandidate, ...] = (
    ProviderCandidate("essentia", "ACOUSTIC", "RESEARCH_ONLY", "AGPL-3.0-or-later", "MODEL_DEPENDENT", "LEGAL_AND_ARCHITECTURE_REVIEW", "https://github.com/MTG/essentia"),
    ProviderCandidate("muq", "MUSIC_REPRESENTATION", "RESEARCH_ONLY", "MIT", "CC-BY-NC-4.0", "REPLACE_OR_LICENSE_WEIGHTS", "https://github.com/tencent-ailab/MuQ"),
    ProviderCandidate("mert", "MUSIC_REPRESENTATION", "RESEARCH_ONLY", "PROJECT_DEPENDENT", "CC-BY-NC-4.0", "REPLACE_OR_LICENSE_WEIGHTS", "https://github.com/yizhilll/MERT"),
    ProviderCandidate("laion-clap", "SEMANTIC", "CANDIDATE", "CC0-1.0", "CHECKPOINT_AND_TRAINING_DATA_REVIEW", "LICENSE_AND_PROVENANCE_REVIEW", "https://github.com/LAION-AI/CLAP"),
    ProviderCandidate("music-flamingo", "AUDIO_REASONING", "RESEARCH_ONLY", "PROJECT_DEPENDENT", "NVIDIA_MODEL_LICENSE", "REPLACE_OR_OBTAIN_LICENSE", "https://github.com/NVIDIA/audio-flamingo"),
    ProviderCandidate("qwen2.5-omni", "AUDIO_REASONING", "REFERENCE", "Apache-2.0", "MODEL_SPECIFIC", "MODEL_CARD_AND_USE_REVIEW", "https://github.com/QwenLM/Qwen2.5-Omni"),
    ProviderCandidate("marble", "BENCHMARK", "REFERENCE", "PROJECT_DEPENDENT", "DATASET_DEPENDENT", "DATASET_BY_DATASET_REVIEW", "https://github.com/a43992899/MARBLE"),
    ProviderCandidate("muse", "BENCHMARK", "EVALUATION_ONLY", "MIT", "NONCOMMERCIAL_TEST_ONLY", "NEVER_USE_STIMULI_FOR_TRAINING", "https://github.com/brandoncarone/MUSE_music_benchmark"),
    ProviderCandidate("visqol", "QUALITY_METRIC", "CANDIDATE", "Apache-2.0", "N/A", "DOMAIN_CALIBRATION_REQUIRED", "https://github.com/google/visqol"),
    ProviderCandidate("bs-roformer", "STEM", "CANDIDATE", "PROJECT_DEPENDENT", "CHECKPOINT_DEPENDENT", "MODEL_BY_MODEL_REVIEW", "https://github.com/lucidrains/BS-RoFormer"),
    ProviderCandidate("audio-separator", "STEM", "CANDIDATE", "MIT", "MODEL_DEPENDENT", "MODEL_BY_MODEL_REVIEW", "https://github.com/nomadkaraoke/python-audio-separator"),
)


def get_candidate(provider_id: str) -> ProviderCandidate:
    for candidate in CATALOG:
        if candidate.provider_id == provider_id:
            return candidate
    raise KeyError(provider_id)


def production_eligible(provider_id: str) -> bool:
    """Fail closed: catalog inclusion never constitutes production approval."""
    get_candidate(provider_id)
    return False

