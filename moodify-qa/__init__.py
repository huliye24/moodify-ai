"""Moodify QA - AI Audio Quality Assurance System

Moodify QA is a standalone B2B audio quality infrastructure module,
extraction from Moodify Engine's detection capabilities.

Target Users:
- Music Companies
- AI Music Platforms
- Recording Studios
- Copyright Owners

NOT a consumer app - pure quality assurance infrastructure.
"""

__version__ = "0.1.0"
__author__ = "Moodify AI"
__license__ = "GPL-3.0-only"

from moodify_qa.core.analyzer import AudioAnalyzer
from moodify_qa.core.scoring import QAScorer
from moodify_qa.core.report import QAReport

__all__ = ["AudioAnalyzer", "QAScorer", "QAReport"]
