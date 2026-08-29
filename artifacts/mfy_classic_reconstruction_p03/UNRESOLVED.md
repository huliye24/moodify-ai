# MFY-CR-P03 — Unresolved (affects P04+)

1. **Evidence integration**: `evidence_refs` is empty in v0.1; wiring
   `EraDiagnosticFinding` into the ProductionCase evidence flow is a P04
   decision (no second case hierarchy was created).
2. **ED-01 cutoff estimator coarseness**: on tonal content the 99.5 %
   cumulative estimator quantizes (~14 kHz read for both 18k and 15k LPs).
   P04 may consider a smoother rolloff-based estimator — inside the estimator
   promotion gate, not by editing thresholds to fit.
3. **ED-06 transfer/encoding**: no validated detector; remains
   NOT_SUPPORTED_IN_V0_1 until a block/codec artifact detector is built and
   validated.
4. **ED-04 mono-vs-collapse**: intentionally undecidable in v0.1
   (NARROW_BY_CHARACTER vs POSSIBLE_TECHNICAL_COLLAPSE); needs more evidence
   sources (e.g. transfer history) or human context.
5. **Human review workflow**: LOW-confidence findings set
   `requires_human_review=True`; the operational review loop (who/when/tooling)
   is a P04/P05 decision and must reuse existing MFY-HUMAN-REVIEW machinery.
6. **Concurrent work**: the working tree contains uncommitted `intervention/`
   files from a parallel session (补丁包71 line); P03 does not touch them.
