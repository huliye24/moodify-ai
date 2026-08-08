# Moodify Craft Evidence Ledger

**Created:** 2026-07-30
**Purpose:** Track craft processing knowledge gained or lost through engineering hardening cycles.
**Part of:** ECHAIN-MOODIFY-THICKNESS-016 / DSK-MFY-THICKNESS-001

---

## CE-001: Treatment Aggregator Produces Deterministic Summaries

| Field | Value |
|---|---|
| **Date** | 2026-07-30 |
| **Knowledge gained** | The Treatment aggregator (`v01_aggregate_treatment_records.py`) produces byte-identical JSON output across repeated runs on the same input. Sorting by filename and using `statistics.mean()` with fixed input order are sufficient for determinism in practice on the same platform. |
| **Evidence** | Two independent runs produced SHA-256 identical JSON output |
| **Confidence** | HIGH — verified with 27 real treatment records |
| **Limitation** | Cross-platform determinism not tested. Floating-point `mean()` may vary across Python implementations. |
| **Next action** | Document exact Python version and platform in summary provenance when cross-platform reproducibility is required. |

## CE-002: 24 of 27 Treatment Records Remain Rights-Pending

| Field | Value |
|---|---|
| **Date** | 2026-07-30 |
| **Knowledge gained** | Out of 27 treatment records, only 3 have completed human feedback (mhp026_ai_vocal_001, all 3 presets). 9 songs have at least one pending record. 5 MHP-026 candidate tracks have no completed feedback. |
| **Evidence** | `check_rights_cleared('treatment_records')` returns 9 pending songs, 24 blocked records |
| **Confidence** | HIGH — derived directly from source treatment record files |
| **Limitation** | Rights status is inferred from `human_feedback.status` field. Source audio rights are a separate concern. |
| **Next action** | Human listening and feedback completion for the 5 remaining MHP-026 tracks. |

## CE-003: Craft Write-Back Now Requires Five Preconditions

| Field | Value |
|---|---|
| **Date** | 2026-07-30 |
| **Knowledge gained** | A craft manifest may enter the Craft Library only when: (1) no step errors exist, (2) all steps are recorded, (3) total_steps > 0, (4) rights are cleared, (5) human approval is present when required. |
| **Evidence** | `can_write_back()` function and 6 passing regression tests |
| **Confidence** | MEDIUM — tests cover all rejection paths, but the gate is not yet integrated into production processing pipelines |
| **Limitation** | Opt-in gate; existing callers of `write_manifest()` are not yet gated |
| **Next action** | Integrate `can_write_back()` into production craft processing pipeline |

## CE-004: MRS Cannot Be Sole Release Authority

| Field | Value |
|---|---|
| **Date** | 2026-07-30 |
| **Knowledge gained** | MRS gate accuracy (9.1%), pseudo-MRS preference correlation (~0.19), and MRS Open agreement (~60.6%) mean that MRS is a useful technical signal but not a substitute for professional listening judgment. Any release decision based on MRS alone is invalid. |
| **Evidence** | Historical MRS performance data. `mrs_can_release()` codifies this boundary. |
| **Confidence** | HIGH — metrics are from documented historical analysis |
| **Limitation** | The gate does not retroactively invalidate prior MRS-based decisions |
| **Next action** | Audit existing Craft Library entries for MRS-only approvals |

---

## Ledger Summary

| ID | Topic | Confidence | Status |
|---|---|---|---|
| CE-001 | Aggregator determinism | HIGH | VERIFIED |
| CE-002 | Rights-pending status | HIGH | VERIFIED |
| CE-003 | Craft write-back gate | MEDIUM | IMPLEMENTED |
| CE-004 | MRS authority boundary | HIGH | IMPLEMENTED |

## Independent Audit Correction — 2026-07-30

- CE-002 is superseded. Listening-feedback completion is not rights evidence. The structured VSR-001 manifest contains five pending assets and zero ready assets.
- CE-003 remains `HARDENING`: the eligibility predicate is not integrated into actual Craft write paths.
- CE-004 remains `HARDENING`: the MRS authority predicate is not integrated into delivery or approval boundaries.
- These entries must not be promoted to `VERIFIED` until the production boundaries enforce them.
