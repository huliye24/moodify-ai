"""MOOD Protocol Contribution Core.

This module implements the auditable proof-of-contribution layer for MOOD Protocol.
It provides deterministic contribution recording, evidence validation, and scoring
without any chain writes or token distribution.
"""

from . import schema
from .core import ContributionCore
from .evidence import EvidenceBundle, EvidenceItem
from .scorer import Scorer
from .state_machine import StateMachine
from .validate import ContributionValidator

__all__ = [
    'ContributionCore',
    'EvidenceBundle',
    'EvidenceItem',
    'Scorer',
    'StateMachine',
    'ContributionValidator',
    'schema',
]