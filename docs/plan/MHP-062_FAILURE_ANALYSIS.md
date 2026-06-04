# MHP-062: Failure Analysis — Classify, Root-Cause, Recommend

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / V (Validation)
**Depends on**: MHP-061 (6h run complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

MHP-061 produces a failure_log.jsonl with error messages, stack traces, and contextual data. Without systematic analysis, these failures are just noise. This task classifies every failure, identifies root causes, and produces a prioritized fix list for Harden-6.

## Goal

Read the MHP-061 outputs and produce:

1. **Failure taxonomy**: classify each failure by type (see below)
2. **Frequency ranking**: which failures happen most often
3. **Root cause analysis**: why each failure class occurs
4. **Impact assessment**: which failures block production adoption
5. **Fix priority list**: ordered list for MHP-065

### Failure taxonomy

| Class | Example | Severity |
|-------|---------|----------|
| DSP_CRASH | Audio processing segfault | CRITICAL |
| TIMEOUT | Task exceeds 900s limit | HIGH |
| DISK_FULL | Output disk exhausted | HIGH |
| AUDIO_FORMAT | Unsupported codec | MEDIUM |
| MRS_ERROR | MRS scoring failed | MEDIUM |
| GATE_FALSE_POS | approve on bad audio | MEDIUM |
| GATE_FALSE_NEG | reject on good audio | MEDIUM |
| TRANSIENT | One-off, unreproducible | LOW |

## Non-Goals

- Don't fix the bugs (MHP-065 does that)
- Don't re-run the validation dataset
- Don't add new tests (MHP-067 does that)

## Acceptance Criteria
- Every failure in the 6h run is classified
- At least 3 distinct failure classes identified (or documented "no failures found")
- Root cause hypothesized for each class
- Fix priority list with severity ratings
- Failure analysis report written to `reports/nem_validate_001/failure_analysis.md`

## Done Means

We know exactly what broke, why it broke, and what to fix first. The Harden-6 phase has a clear work list.
