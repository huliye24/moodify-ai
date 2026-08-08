"""Lyric temporal alignment engine (DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001, MSE boundary).

Alignment is a measurement of "when each lyric line/word occurs in the final audio".
The audio is the timing authority; the lyric text is the wording authority.
"""

from moodify.lyric_align.exporters import write_outputs
from moodify.lyric_align.models import AlignmentResult, LineTiming, WordTiming
from moodify.lyric_align.pipeline import run_alignment
from moodify.lyric_align.quality import QualityReport, evaluate

__all__ = [
    "AlignmentResult",
    "LineTiming",
    "WordTiming",
    "QualityReport",
    "evaluate",
    "run_alignment",
    "write_outputs",
]

__version__ = "0.1.0"
