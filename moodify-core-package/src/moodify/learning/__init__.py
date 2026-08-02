"""Learning domain (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Moodify learns from success, failure, rejection and uncertainty. This
package owns learning records, rights governance, eligibility and
controlled dataset exports — never model training itself.
"""

from moodify.learning import eligibility, errors, exports, models, service, store

__all__ = ["eligibility", "errors", "exports", "models", "service", "store"]
