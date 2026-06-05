# MHP-836: Release Candidate Learning Gate

**Status**: done
**Implementation**: `moodify_runtime/product_integration.py::check_release_learning_gate()`

Four-check gate that blocks release if: (1) fatal errors exist, (2) task success rate < 95%, (3) scoring agreement < 70%, or (4) operator decision is not PASS. Returns a LearningGateResult with pass/fail, detailed checks, blocking issues, and actionable recommendations.
