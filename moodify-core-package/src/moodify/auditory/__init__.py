"""Auditory observation and verification infrastructure (DSK-MFY-AUDITORY-SCAN-001).

Moodify is an auditory intelligence system: this package is its sensory
capture layer. It scans, measures, compares, verifies and judges — it does
not modify sound. External applications (e.g. Audacity) own the act of
processing; Moodify owns observation, measurement, comparison, evidence
and technical judgment.
"""

from moodify.auditory import errors, judgment, metrics, profiles, service

__all__ = ["errors", "judgment", "metrics", "profiles", "service"]
